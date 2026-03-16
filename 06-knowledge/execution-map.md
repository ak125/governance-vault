# Execution Map — massdoc DB

> **Cartographie des flux critiques : entry point → service chain → tables**
> **Version**: 1.2.0 | **Status**: BASELINE_AUDIT | **Date**: 2026-03-14
> **Complement de**: domain-map.md V1.4.2, schema-governance-matrix.md V1.2.0

---

## Legende

| Terme | Definition |
|-------|-----------|
| **Entry** | Point d'entree : HTTP route, BullMQ queue, event interne |
| **Chain** | Sequence : Controller → Service → RPC/Query |
| **Tables R** | Tables lues par le flux |
| **Tables W** | Tables ecrites par le flux |
| **Cache** | Pattern de cle Redis + TTL |
| **Feature flag** | Condition d'activation du flux |

### Criticite des flux

| Niveau | Definition |
|--------|-----------|
| **HOT_READ** | Flux de lecture sur le chemin utilisateur direct (latence visible) |
| **HOT_WRITE** | Flux d'ecriture sur des tables source_of_truth |
| **PIPELINE** | Flux asynchrone (BullMQ), impact indirect |
| **NOT_MATERIALIZED** | Schema en place, 0 consumer actif dans le code |

---

## Note sur la restructuration U3/U4

Le code search revele que :
- L'ancien **U3 (Rebuild RM CQRS)** n'existe pas comme flux independant — le RM est consomme en lecture par U1 via `rm_get_page_complete_v2`. Pas de rebuild batch observe.
- L'ancien **U4 (SEO generation)** est en realite le pipeline `content-refresh` — il fusionne avec U3.
- L'ancien **U5 (import catalogue)** est non materialise.

Restructuration adoptee :
- **U1** : Listing catalogue (read path)
- **U2** : Recherche reference (read path)
- **U3** : Content refresh pipeline (write path, BullMQ)
- **U4** : RAG ingestion → content refresh (write path, event-driven)
- **U5** : Import catalogue (non materialise)

---

## U1 — Listing catalogue

> **Criticite** : HOT_READ — page produit, impacte directement l'experience utilisateur et le SEO.

### Entry

```
GET /pieces/:gamme/:marque/:modele/:type.html
```

### Chain

```
Frontend Loader (pieces.$gamme.$marque.$modele.$type[.]html.tsx)
  ↓ fetchRmPageV2(gammeId, vehicleId, 200)
RmController (rm.controller.ts:127)
  ↓ GET /api/rm/page-v2
RmBuilderService.getPageCompleteV2() (rm-builder.service.ts:495-641)
  ↓
RPC: rm_get_page_complete_v2(p_gamme_id, p_vehicle_id, p_limit)
  ↓
Returns: JSONB {products, grouped_pieces, vehicleInfo, gamme, seo, oemRefs, crossSelling, filters}
```

### Tables

| Mode | Table | Domain | Donnee |
|------|-------|--------|--------|
| R | `pieces` | D1 | Produits et details |
| R | `pieces_marque` | D1 | Marques |
| R | `pieces_media_img` | D1 | Images produit |
| R | `pieces_price` | D1 | Prix |
| R | `pieces_gamme` | D1 | Association gamme-famille |
| R | `pieces_relation_type` | D1 | Compatibilite vehicule |
| R | `__seo_gamme_purchase_guide` | D3 | Guide d'achat SEO |
| R | `__seo_reference` | D3 | References OEM |
| R | `rm_listing` | D8 | Metadata listing cache |

> Note : `auto_type` (D4) est probablement lu via la RPC `rm_get_page_complete_v2` pour construire `vehicleInfo`. Non confirme par inspection directe de la RPC SQL. Certaines tables retournees via cette RPC sont inferees depuis le payload JSONB et non confirmees par lecture directe du SQL de la RPC.

### Cache

| Pattern | TTL | Performance |
|---------|-----|-------------|
| `rm:page-v2:{gamme_id}:{vehicle_id}` | 3600s (1h) | Hit ~50ms / Miss ~400ms (mesure ponctuelle dev, non benchmarke) |

### Feature flags

Aucun — flux toujours actif.

### Fichiers source

| Fichier | Role |
|---------|------|
| `frontend/app/routes/pieces.$gamme.$marque.$modele.$type[.]html.tsx` | Loader Remix |
| `backend/src/modules/rm/controllers/rm.controller.ts:127` | Endpoint API |
| `backend/src/modules/rm/services/rm-builder.service.ts:495-641` | Orchestration RPC |

---

## U2 — Recherche reference

> **Criticite** : HOT_READ — recherche par reference piece, impact UX direct.

### Entry

```
GET /api/search?query=KH22&limit=20
```

### Chain

```
SearchController.searchPieces(query, page, limit) (search.controller.ts:27)
  ↓
SearchSimpleService.search(query, filters, pagination) (search-simple.service.ts:223-350+)
  ↓
Generate variants: UPPERCASE, no-spaces, space-separated, hyphenated
  ↓
Query: pieces_ref_search WHERE prs_search IN [variants] LIMIT 1000
  ↓
Fallback (si vide): pieces_price WHERE pri_ref ILIKE query
  ↓
Enrichment: pieces + pieces_marque + pieces_gamme + pieces_media_img
  ↓
Return: scored + paginated results
```

### Tables

| Mode | Table | Domain | Donnee |
|------|-------|--------|--------|
| R | `pieces_ref_search` | D1 | Index de recherche principal |
| R | `pieces_price` | D1 | Fallback refs + prix |
| R | `pieces` | D1 | Details produit |
| R | `pieces_marque` | D1 | Marque |
| R | `pieces_gamme` | D1 | Gamme |
| R | `pieces_media_img` | D1 | Images |

### Cache

| Pattern | TTL | Performance |
|---------|-----|-------------|
| `oem_search:{query}:p{page}:l{limit}:f{filters}:eq{equiv}:v{variants}` | variable | Hit ~100ms / Miss ~1-2s (estimation, non benchmarke) |

### Feature flags

Aucun — flux toujours actif.

### Fichiers source

| Fichier | Role |
|---------|------|
| `backend/src/modules/search/controllers/search.controller.ts:27` | Endpoint |
| `backend/src/modules/search/services/search-simple.service.ts:223-350+` | Logique de recherche |

---

## U3 — Content refresh pipeline

> **Criticite** : PIPELINE — ecriture asynchrone sur les tables SEO source_of_truth. Impact indirect sur SEO/indexation.

### Entry

```
BullMQ queue: content-refresh
Triggered by:
  - Event RAG_INGESTION_COMPLETED → queueRefreshForGamme()
  - Event KEYWORD_PLAN_VALIDATED → queueRefreshForGamme(force=true)
  - Admin manual trigger
```

### Chain

```
ContentRefreshService (content-refresh.service.ts)
  ↓ onIngestionCompleted() / onKeywordPlanValidated()
  ↓ queueRefreshForGamme(pgAlias, jobId, source, supplementaryFiles)
ContentRefreshProcessor.@Process('content-refresh') (content-refresh.processor.ts:44-200+)
  ↓ Route by pageType:
  ├─ R3_conseils → ConseilEnricherService
  ├─ R3_buying_guide → BuyingGuideEnricherService  // alias legacy — role canonique = R6 Guide d'achat
  ├─ R1_keyword_plan → R1ContentPipelineService
  └─ R5_diagnostic → DiagnosticService
  ↓
Quality gates (validation avant ecriture):
  ├─ BriefGatesService (format)
  ├─ HardGatesService (regles semantiques)
  ├─ ImageGatesService (images)
  └─ RagFoundationGateService (eligibilite RAG)
  ↓
SectionCompilerService (compilation finale)
  ↓
INSERT/UPDATE → __seo_gamme_purchase_guide / __seo_gamme_conseil / __seo_reference
```

> Note : `R3_buying_guide` est un alias technique legacy. Le role canonique est **R6 Guide d'achat** (voir role-matrix.md v5). Le code utilise encore cet alias pour le routage interne.

### Job data

```typescript
{
  pgId: number,
  pgAlias: string,
  pageType: 'R3_conseils' | 'R1_keyword_plan' | 'R5_diagnostic',
  jobId: string,
  source: string,
  supplementaryFiles: string[],
  force: boolean
}
```

### Tables

| Mode | Table | Domain | Donnee |
|------|-------|--------|--------|
| R | `pieces_gamme` | D1 | Details gamme |
| R | `__seo_gamme` | D3 | Metadata gamme SEO |
| R | `__seo_r3_keyword_plan` | D3 | Keyword plans R3 |
| R | `__rag_content_refresh_log` | D6 | Historique refresh |
| W | `__seo_gamme_purchase_guide` | D3 | Contenu guide d'achat (R6 canon, R3 legacy) |
| W | `__seo_gamme_conseil` | D3 | Contenu conseil R3 |
| W | `__seo_reference` | D3 | Contenu reference R4 |
| W | `__rag_content_refresh_log` | D6 | Audit trail refresh |

> Note : `__seo_keywords` (D3) est tres probablement consulte par certaines gates ou enrichers pour le contexte SEO, mais cette lecture n'est pas encore confirmee flux par flux dans ce document.

### Feature flags

| Flag | Effet |
|------|-------|
| `PIPELINE_CHAIN_ENABLED` | Auto-chain keyword plan → content refresh (default: false) |
| `RAG_FOUNDATION_GATE_ENABLED` | Gate d'eligibilite RAG source |

### Fichiers source

| Fichier | Role |
|---------|------|
| `backend/src/modules/admin/services/content-refresh.service.ts` | Event listeners + job queue |
| `backend/src/workers/processors/content-refresh.processor.ts:44-200+` | Job handler principal |
| `backend/src/modules/admin/services/buying-guide-enricher.service.ts` | Enrichissement R3 guide |
| `backend/src/modules/admin/services/conseil-enricher.service.ts` | Enrichissement R3 conseil |
| `backend/src/modules/admin/services/r1-content-pipeline.service.ts` | Pipeline R1 |
| `backend/src/modules/admin/services/brief-gates.service.ts` | Gate format |
| `backend/src/modules/admin/services/hard-gates.service.ts` | Gate semantique |
| `backend/src/modules/admin/services/section-compiler.service.ts` | Compilation finale |
| `backend/src/modules/rag-proxy/services/rag-foundation-gate.service.ts` | Gate eligibilite RAG |

---

## U4 — RAG ingestion

> **Criticite** : PIPELINE — ingestion de contenu RAG, declenche U3 en aval.

### Entry

```
RagIngestionService.ingestWeb(url)
RagIngestionService.ingestPdf(filePath)
Source: /opt/automecanik/rag/knowledge/ (~318 fichiers .md)
```

### Chain

```
RagIngestionService.ingestWeb() / ingestPdf() (rag-ingestion.service.ts)
  ↓
FrontmatterValidatorService.validate() (YAML metadata)
  ↓
RagGammeDetectionService.detectGammes() (rag-gamme-detection.service.ts)
  → Extract gamme aliases from content
  → Returns: affectedGammes[], affectedGammesMap, affectedDiagnostics[]
  ↓
[Phase 1.5 — Normalisation]
RagNormalizationService.normalize() (rag-normalization.service.ts)
  → Stabilise structure et identite canonique sans muter le sens metier
  → Etat sortie : NORMALIZED
  ↓
[Phase 1.6 — Admissibilite]
RagAdmissibilityGateService.evaluate() (rag-admissibility-gate.service.ts)
  → Qualifie le role R* candidat unique
  → Etat sortie : ADMISSIBLE_R*
  ↓
RagFoundationGateService.check() (rag-foundation-gate.service.ts)
  → Verifie eligibilite RAG source
  ↓
RagRedisJobService (track progress via Redis)
  ↓
Store job in __rag_web_ingest_jobs
  ↓
Emit RagIngestionCompletedEvent
  ↓
ContentRefreshService.onIngestionCompleted() [→ triggers U3]
  → Pour chaque gamme affectee: queueRefreshForGamme()
```

### Event payload

```typescript
RagIngestionCompletedEvent {
  jobId: string,
  status: 'done' | 'failed',
  source: 'web' | 'pdf',
  affectedGammes: string[],
  affectedGammesMap: { [pgAlias]: string[] },
  affectedDiagnostics: string[],
  validationSummary: {
    validFiles: number,
    quarantinedFiles: number
  }
}
```

### Tables

| Mode | Table | Domain | Donnee |
|------|-------|--------|--------|
| R | `__rag_knowledge` | D6 | Lu par foundation-gate et admissibility-gate (Phase 1.5/1.6) |
| W | `__rag_web_ingest_jobs` | D6 | Job tracking |
| W | `__rag_knowledge` | D6 | Corpus RAG (fichiers .md stockes) |
| W | `__rag_content_refresh_log` | D6 | Audit trail (via U3) |

### Feature flags

Aucun — flux toujours actif.

### Fichiers source

| Fichier | Role |
|---------|------|
| `backend/src/modules/rag-proxy/services/rag-ingestion.service.ts` | Orchestration ingestion (Phase 1) |
| `backend/src/modules/rag-proxy/services/rag-gamme-detection.service.ts` | Detection gammes (Phase 1) |
| `backend/src/modules/rag-proxy/services/frontmatter-validator.service.ts` | Validation YAML (Phase 1) |
| `backend/src/modules/rag-proxy/services/rag-normalization.service.ts` | Normalisation canonique (Phase 1.5) |
| `backend/src/modules/rag-proxy/services/rag-admissibility-gate.service.ts` | Admissibilite role R* (Phase 1.6) |
| `backend/src/modules/rag-proxy/services/rag-foundation-gate.service.ts` | Eligibilite RAG source (Phase 1.6) |
| `backend/src/modules/rag-proxy/services/rag-redis-job.service.ts` | Progress tracking |

---

## U5 — Import catalogue

> **Criticite** : NOT_MATERIALIZED — schema en place, 0 consumer actif.

### Status

Le pipeline d'import catalogue est **concu mais non active** (voir domain-map.md V1.4.2, domaine D9) :
- 26 tables D9 en place (staging → normalisation → natural keys → decisions)
- ~35 RPC existantes (`create_import_batch`, `check_gate_*`, `merge_staging_*`)
- 0 consumer actif dans le code backend
- decision_status : `observe_activation`

### Tables prevues (non actives)

| Phase | Tables | Role |
|-------|--------|------|
| Staging | `stg_vehicle`, `stg_article`, `stg_compatibility`, `stg_brand` | Donnees brutes importees |
| Normalisation | `norm_vehicle`, `norm_brand`, `norm_article` | Donnees normalisees |
| Natural keys | `natural_key_article`, `natural_key_brand`, `natural_key_vehicle` | Cles naturelles deduites |
| Cross-reference | `xref_article`, `xref_brand`, `xref_vehicle` | Mapping vers cles internes |
| Decision | `decision_article`, `decision_brand`, `decision_compat` | Decisions de merge |
| Control | `import_batch`, `__import_batch_contract`, `__import_gate_status` | Orchestration |
| Audit | `__import_proof`, `__import_manifest`, `__catalog_import_history` | Tracabilite |

### Prochaine action

Confirmer si un premier import batch est planifie — gate : `observe_activation`.

> En l'etat, U5 est documente comme flux theorique / structurel, et non comme flux observe en execution. Aucune validation runtime n'est possible — seulement validation par design/schema/RPC.

---

## Matrice de couverture tables x usages (scope restreint aux flux U1-U5)

> Quelle table est touchee par quels usages. R = read, W = write, — = non implique.

### Tables Tier 1

| Table | U1 | U2 | U3 | U4 | U5 |
|-------|----|----|----|----|-----|
| `pieces_gamme` | R | — | R | — | — |
| `__seo_gamme_purchase_guide` | R | — | W | — | — |
| `__seo_reference` | R | — | W | — | — |
| `__rag_knowledge` | — | — | — | W | — |
| `__seo_observable` | — | — | — | — | — |
| `__seo_page_brief` | — | — | — | — | — |
| `__seo_gamme` | — | — | R | — | — |
| `__seo_keywords` | — | — | — | — | — |
| `__seo_page` | — | — | — | — | — |
| `ic_postback` | — | — | — | — | — |
| `kg_edges` | — | — | — | — | — |
| `pieces` | R | R | — | — | — |
| `auto_type` | R | — | — | — | — |

### Tables Tier 2

| Table | U1 | U2 | U3 | U4 | U5 |
|-------|----|----|----|----|-----|
| `catalog_gamme` | — | — | — | — | — |
| `catalog_family` | — | — | — | — | — |
| `__seo_gamme_conseil` | — | — | W | — | — |
| `__blog_advice` | — | — | — | — | — |
| `__blog_guide` | — | — | — | — | — |
| `___xtr_order` | — | — | — | — | — |
| `kg_nodes` | — | — | — | — | — |
| `__rag_content_refresh_log` | — | — | R/W | W | — |
| `gamme_aggregates` | — | — | — | — | — |
| `__cross_gamme_car_new` | — | — | — | — | — |
| `__cross_gamme_car` | — | — | — | — | — |
| `gamme_seo_audit` | — | — | — | — | — |
| `gamme_seo_metrics` | — | — | — | — | — |
| `__agentic_runs` | — | — | — | — | — |

### Observations

1. **U1 et U2 dominent D1** — toute modification sur `pieces`, `pieces_price`, `pieces_gamme` impacte les deux flux utilisateur critiques
2. **U3 domine D3 en ecriture** — c'est le seul flux qui ecrit dans `__seo_gamme_purchase_guide`, `__seo_gamme_conseil`, `__seo_reference`
3. **Tables hors scope U1-U5 mais critiques sur d'autres flux** : `ic_postback`, `kg_edges`, `kg_nodes`, `catalog_gamme`, `catalog_family`, `__blog_*`, `___xtr_order`, `gamme_*`, `__agentic_runs`, `__seo_keywords`, `__seo_page`, `__seo_observable`, `__seo_page_brief`
   - Ces tables sont consommees par d'autres chemins (sitemap, blog, paiements, KG, moteur agentique) non traces dans ce document
4. **U5 n'impacte aucune table active** — flow non materialise

---

## Dependances inter-flux

```
U4 (RAG ingestion)
  ↓ emit RAG_INGESTION_COMPLETED
U3 (Content refresh pipeline)
  ↓ ecrit dans __seo_gamme_purchase_guide, __seo_gamme_conseil
U1 (Listing catalogue)
  ↓ lit __seo_gamme_purchase_guide (cache Redis 1h)
```

### Cascade d'invalidation

| Declencheur | Impact | Delai |
|-------------|--------|-------|
| Nouveau fichier RAG ingere (U4) | Job content-refresh queue (U3) | Immediat (event-driven) |
| Content refresh termine (U3) | Cache U1 invalide apres TTL | ≤ 3600s (pas d'invalidation active) |
| Keyword plan valide (trigger DB) | Job content-refresh queue (U3) | Immediat (si `PIPELINE_CHAIN_ENABLED`) |

### Risque identifie

Le cache U1 (`rm:page-v2:*`, TTL 1h) n'est **pas invalide activement** apres un content refresh U3. Un utilisateur peut voir du contenu SEO obsolete pendant 1h max apres un refresh. Acceptable pour du contenu editorial, mais a documenter.

---

## Points de profiling prioritaires

> Pre-requis pour perf-findings.md — les requetes a analyser en priorite.

| # | Requete | Flux | Raison | Action |
|---|---------|------|--------|--------|
| P1 | `rm_get_page_complete_v2` | U1 | RPC critique, ~400ms miss | EXPLAIN ANALYZE avec gamme/vehicle representatifs |
| P2 | `SELECT FROM pieces_ref_search WHERE prs_search IN (...)` | U2 | Scan sur 73M lignes, variants multiples | EXPLAIN ANALYZE avec ref frequente + rare |
| P3 | `INSERT/UPDATE __seo_gamme_purchase_guide` | U3 | Ecriture sur source_of_truth SEO | EXPLAIN ANALYZE / profiling applicatif du cout d'ecriture pipeline |
| P4 | `INSERT/UPDATE __seo_keywords` | U3 | 7 triggers en cascade sur cette table | Mesurer temps total d'un write avec triggers actifs |
| P5 | `pieces_relation_type` seq scan | U1 | 463B seq_tup_read (C1) | EXPLAIN sur jointure vehicule-piece |
| P6 | `pieces_relation_criteria` | U1 | 36 GB, plus grosse table | EXPLAIN sur filtrage criteres |
| P7 | Index D1 a 0 scan (8 GB) | — | Confirmer inutilite | `pg_stat_user_indexes` + EXPLAIN des requetes U1/U2 |
| P8 | Index D2 a 0 scan (15.4 GB) | — | Confirmer inutilite | `pg_stat_user_indexes` apres code search |

---

## Limites de ce document

- Le code search couvre le backend TypeScript (`.from()`, `.rpc()`) — pas les vues SQL, fonctions PostgreSQL internes, ou acces directs
- Les flux non traces ici (sitemap generation, blog serving, paiements, KG diagnostic, moteur agentique) ne sont pas inclus — ils ont des chemins d'acces distincts
- Les `runtime_signal` (pg_stat) ne sont pas correles directement aux flux U1-U5 — une session de profiling dediee est requise
- U5 est documente sur la base du schema et des RPC, pas d'execution reelle

---

## Non-goals

Ce document ne valide pas les performances — c'est le role de perf-findings.md.
Ce document ne propose pas de modifications — c'est le role de change-control-plan.md.

---

_Derniere mise a jour: 2026-03-14_
_Genere depuis code search backend + domain-map.md V1.4.2 + schema-governance-matrix.md V1.1_
