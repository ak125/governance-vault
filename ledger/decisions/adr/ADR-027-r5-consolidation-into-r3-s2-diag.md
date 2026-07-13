---
id: ADR-027
title: "R5 Diagnostic Consolidation into R3 S2_DIAG — Canonical SEO Architecture"
status: accepted
date: 2026-04-25
decision_date: 2026-04-25
decision_makers: ["@fafa"]
supersedes: []
superseded_by: []
related_rules: ["G1", "G2", "AP-10"]
related_incidents: []
related_adr: ["ADR-015", "ADR-022", "ADR-025"]
reviewed_by: "@fafa"
---

# ADR-026: R5 Diagnostic Consolidation into R3 S2_DIAG — Canonical SEO Architecture

## Contexte

Le rôle SEO `R5_DIAGNOSTIC` (route `/diagnostic-auto/{slug}`, défini dans
`rules-seo-pagerole.md` R-SEO-02) a été instancié en deux temps avec des
résultats divergents :

1. **Phase initiale (jan-mar 2026)** — 1176 pages R5 sub-detail générées
   massivement par script anonyme (`__seo_observable.created_by IS NULL`,
   first 2026-01-26, last 2026-03-19). Sur ces 1176 pages :
   - 24 publiées avec contenu éditorial (200-921 chars symptom)
   - 1152 stubs squelettiques (~80-105 chars symptom, produit cartésien
     `voyant-X / odeur-X / fuite-X × {démarreur, alternateur, ...}`)
   - **0 ont `schema_org` peuplé**, **0 `differentiation_checklist`**

2. **Performance SEO mesurée (mars 2026)** — `~15 clics totaux, positions
   30-60` sur les 1176 URLs (source : message commit `a57cefc7`, 2026-03-22).
   Échec catégorique attribuable au thin content massif des 1152 stubs.

3. **Décision corrective (commit `a57cefc7`, 2026-03-22)** — implémentation
   en code de la consolidation R5 → R3 S2_DIAG :
   - Sitemap `/sitemap-diagnostic.xml` ne référence que le hub
     `/diagnostic-auto` (sub-pages exclues)
   - Endpoint `redirect/:slug` dans `diagnostic.controller.ts` + 301 dans
     `diagnostic-auto.$slug.tsx` loader
   - Fallback `buildS2DiagFromObservable` ajouté dans
     `conseil-enricher.service.ts` (RPC `get_observable_symptoms_for_gamme`,
     filtre `is_published = true`)
   - 4 RPCs SQL + 1 monitoring view + 8 gammes batch-enriched (3 → 11 S2_DIAG)

4. **Dette G1** — cette décision architecturale **n'a jamais été formalisée
   en ADR vault**. Elle vit dans le code et l'historique git, pas dans le
   canon. Toute évolution ultérieure sur R5/R3 manque d'ancrage.

5. **État au 2026-04-25 (audit DB live)** :
   - 259 gammes ont au moins une section conseil R3
   - **133/259 = 51%** ont une section S2_DIAG
   - **126 gammes** sont éligibles enrichissement (S2_DIAG manquant)
   - Sur ces 126 : **110 ont des observables liés** (`related_gammes`)
     mais **0 ont des observables publiés** (les 24 published couvrent
     11 gammes seulement)
   - **0/133 S2_DIAG existants n'ont été enrichis via observable_fallback**
     (toutes les S2_DIAG actuelles viennent de la voie RAG primaire :
     `≥2 symptoms AND ≥2 quick_checks` dans la gamme `.md`)
   - Le moteur déterministe `__diag_*` (62 symptômes × 58 causes × 162
     liens, 13 systèmes) est **isolé du graphe gammes** : aucune table de
     mapping `pg_id ↔ system_id`

Cette ADR formalise la décision de mars 2026 et trace le plan d'extension
pour combler le gap S2_DIAG (51% → ≥95% couverture).

## Décision

Adopter la **consolidation R5 → R3 S2_DIAG comme architecture canonique**
avec quatre piliers et un plan de mise en œuvre en deux phases.

### 4 piliers canoniques

1. **R5 sub-pages = sunsetted permanent**
   - URLs `/diagnostic-auto/{slug}` (≠ hub) → 301 redirect perpétuel vers
     `/blog-pieces-auto/conseils/{gamme-slug}#diagnostic-rapide`
   - Aucune nouvelle URL sub-page R5 ne sera créée. Le sitemap
     `/sitemap-diagnostic.xml` reste **figé à 1 URL** (le hub).
   - Les 1176 lignes `__seo_observable` restent en DB pour traçabilité
     historique mais ne sont plus la source canonique.

2. **R5 hub `/diagnostic-auto` = produit, pas SEO**
   - Le hub reste l'interface du moteur diagnostic (wizard pour l'utilisateur)
   - Indexable au sitemap, pageRole `R5_DIAGNOSTIC` conservé pour cette URL
   - Optimisé pour conversion outil → catalogue, pas pour ranking symptômes

3. **S2_DIAG = section canonique "diagnostic rapide"** dans R3 conseil gamme
   - Présente dans la page `/blog-pieces-auto/conseils/{gamme-slug}` avec
     ancre `#diagnostic-rapide` (cible des 301 ci-dessus)
   - Format canonique : table 3 colonnes (Symptôme | Cause probable | Action)
     + footer DTC codes
   - Cible : ≥95% des gammes R3 publiées (245+/259 actuelles), avec
     `sgc_quality_score ≥ 70`

> **⚠ SUPERSEDED 2026-07-07** — voir `## Correction 2026-07-07` ci-dessous. L'ordre de priorité
> P1 RAG primary / P2 `__diag_*` / P3 observable **n'est plus canonique**. RAG sort **entièrement** de
> la liste des sources autorisées de S2_DIAG.

4. **Trois sources d'enrichissement S2_DIAG, par ordre de priorité**
   - **P1 (canon)** — RAG primary : déclenché si la gamme `.md` a
     `≥2 symptoms AND ≥2 quick_checks` dans son frontmatter `diagnostic.*`
     (voie qui a produit les 133 S2_DIAG existants, qualité avg 85.4)
   - **P2 (futur, post-ADR)** — Moteur déterministe `__diag_*` : RPC
     `build_s2_diag_from_diag_engine(p_pg_id)` qui joint
     `__diag_symptom × __diag_symptom_cause_link × __diag_cause × __diag_safety_rule`
     via une table de mapping `__diag_gamme_system_map(pg_id, system_id, weight)`
     (~400 lignes seed, à constituer)
   - **P3 (legacy, déprécié)** — Observable fallback existant
     (`buildS2DiagFromObservable`, RPC `get_observable_symptoms_for_gamme`)
     conservé tant que P2 n'est pas livré, puis archivé

## Correction 2026-07-07 — Autorité de source S2_DIAG (supersede §Décision pilier 4)

Le pilier #4 « Trois sources d'enrichissement S2_DIAG, par ordre de priorité » (P1 RAG primary /
P2 `__diag_*` / P3 observable) est **superseded en totalité**. Motif : contradiction directe avec
**ADR-080** (accepted — « RAG = chatbot uniquement ; RagEnrichmentEngine legacy à neutraliser ») et
**ADR-086** (accepted — 4 intrants RAW/WIKI/DB/KW ; RAG **absent** des sources de contenu).

**Contrat d'autorité S2_DIAG (remplace le modèle de priorité P1/P2/P3 du pilier 4) :**

- **SURFACE** — S2_DIAG reste une section de **R3** *(inchangé — pilier #3 préservé)*.
- **AUTHORITATIVE INPUT A** — `__diag_*` : vérité **symptôme / système / cause**.
- **AUTHORITATIVE INPUT B** — WIKI `diagnostic_relations[]` (ADR-033) : relation typée **pièce ↔ symptôme**.
- **S2_DIAG = composition déterministe de A + B** (projection servie). **A et B sont des entrées
  COMPLÉMENTAIRES, pas des alternatives** : on ne « choisit » pas l'une ou l'autre, on ne concatène pas
  ad hoc — la composition est déterministe.
- **AUCUNE hiérarchie de fallback.** Entrée autoritaire manquante ⇒ pas de nouvelle S2_DIAG canonique
  (voir « Autorité ≠ readiness »).

**Tombstone (audit trail) :**
> Le modèle de priorité de sources **P1/P2/P3** (pilier #4) est **superseded**. **RAG est retiré
> ENTIÈREMENT de l'autorité de contenu** (ni source, ni repli, ni rang). `__seo_observable` reste
> **historique / legacy uniquement** (déjà non-canonique, pilier #1). Entrée autoritaire manquante ⇒
> **aucune nouvelle S2_DIAG canonique** ⇒ **jamais** de fallback RAG **ni** observable.

**Éléments du « Plan de mise en œuvre » également superseded par cette Correction** (marqués superseded,
non supprimés) : **Phase C — Batch RAG enrichissement** (runner `batch-enrich-s2-diag.ts` →
`ConseilEnricherService.enrichGamme`, cible 51 %→≥85 % couverture) ; la clause **Phase D** « *Pour le résidu
(gammes sans RAG suffisant) après Phase C* » (le moteur `__diag_*` est l'**INPUT A autoritaire** pour
**toutes** les gammes, pas un simple traitement du résidu post-RAG) ; le **Rollback Phase C**
(`sgc_enriched_by = 'batch-rag-runner'`) ; et le **Rollback Phase D** (flag
`S2_DIAG_SOURCE=observable|diag_engine` — `observable` n'est plus une source active/switchable).
**Préservés** (non superseded) : le **mécanisme Phase D** (`__diag_gamme_system_map` +
`buildS2DiagFromDiagEngine` = désormais le chemin **canonique, INPUT A**), **Phase E** (archivage legacy
observable), **Phase B** (instrumentation `__diag_session`), et les piliers #1/#2/#3.

**Autorité canonique ≠ readiness technique.** Tant que le mapping `__diag_* → gamme`
(`__diag_gamme_system_map`) est incomplet : **input autoritaire absent ⇒ aucune nouvelle S2_DIAG canonique
produite ; JAMAIS de fallback RAG.** Le contenu S2_DIAG existant peut **rester servi statiquement** pendant
le cutover, mais **aucune nouvelle vérité ne naît du RAG.** La migration curée des symptômes legacy vers
`diagnostic_relations[]` (ADR-033 Phase 4, différée) reste un re-source gouverné — jamais une écriture RAG.

### Plan de mise en œuvre

**Phase A — Foundation (cette ADR)**

Formaliser le canon. Pas de code dans cette PR.

**Phase B — Instrumentation neutre (parallèle, monorepo)**

Indépendante de R5/R3. Prérequis structurel pour mesurer le funnel
diagnostic → achat à terme.

- Migration : `ALTER TABLE __diag_session ADD COLUMN customer_id UUID
  REFERENCES ___xtr_customer(cst_id) NULL` (FK simple, NULL accepté pour
  sessions anonymes)
- Frontend : event GA4 `diagnostic_completed` (suit le pattern existant
  `selector_complete`)
- View SQL `v_diag_funnel` : sessions × orders agrégées par jour/semaine

> ⚠ SUPERSEDED 2026-07-07 — voir § Correction (RAG retiré des sources S2_DIAG).

**Phase C — Batch RAG enrichissement (B3 dans plan exécution)**

- Audit `scripts/audit/audit-rag-coverage-s2diag.py` sur les 126 gammes
  manquantes — identifier celles avec RAG `.md` éligible
  (`≥2 symptoms AND ≥2 quick_checks`)
- Runner `scripts/seo/batch-enrich-s2-diag.ts` qui invoque
  `ConseilEnricherService.enrichGamme(pgId)` sur les éligibles
- Quality gate : `sgc_quality_score ≥ 70` obligatoire pour upsert
- Cible : passer de 51% → ≥85% couverture S2_DIAG

**Phase D — Refonte RPC moteur __diag_* (B2 dans plan exécution)**

> ⚠ SUPERSEDED 2026-07-07 — voir § Correction (RAG retiré des sources S2_DIAG).

Pour le résidu (gammes sans RAG suffisant) après Phase C.

- Migration : table `__diag_gamme_system_map(pg_id INT REFERENCES pieces_gamme,
  system_id INT REFERENCES __diag_system, weight SMALLINT, primary_match BOOL)`
- Seed : ~400 mappings `(pg_id, system_id)` validés humainement
- RPC `build_s2_diag_from_diag_engine(p_pg_id)` en SQL STABLE
- Refactor `buildS2DiagFromObservable` → `buildS2DiagFromDiagEngine` avec
  source RPC switchée
- Cible : passer de ≥85% → ≥95% couverture

**Phase E — Archivage legacy**

- Marquer les 1152 observable drafts squelettiques en `is_archived = true`
  (ou suppression conditionnelle après PR review)
- Déprécier la RPC `get_observable_symptoms_for_gamme` au profit de la
  nouvelle RPC moteur

## Évidence

| Source | Référence |
|--------|-----------|
| Commit consolidation initiale | `a57cefc7` (monorepo, 2026-03-22) |
| Performance SEO échouée | message commit `a57cefc7` : 15 clics, positions 30-60 |
| Audit DB 2026-04-25 (live MCP) | 259 gammes R3, 133 S2_DIAG, 126 manquantes |
| Filtre RPC bloquant | `__seo_observable.is_published = true` dans `get_observable_symptoms_for_gamme` |
| Volume observable drafts squelettiques | 1152 lignes, longueur 79-105 chars symptom |
| Code conseil-enricher fallback | `backend/src/modules/admin/services/conseil-enricher.service.ts:1178-1266` |
| Moteur diag isolé | aucune jointure DB `__diag_*` ↔ `pieces_gamme` |

## Conséquences

### Positives

- **Dette G1 résolue** : décision SEO majeure (mars 2026) désormais ancrée
  au canon vault, traçable et opposable
- **Architecture propre** : un rôle, une responsabilité — R5 hub = produit,
  S2_DIAG = SEO contenu
- **Cible mesurable** : 51% → ≥95% couverture S2_DIAG, avec scoring qualité
- **Sortie progressive du legacy** : le pipeline observable (1176 lignes)
  s'éteint sans rupture, remplacé par moteur déterministe `__diag_*`

### Coûts

- **Mapping pg_id ↔ system_id** : ~400 lignes à seed humainement (Phase D)
- **Test 301 perpétuels** : vérifier que `/diagnostic-auto/{slug}` redirige
  bien vers `/blog-pieces-auto/conseils/{gamme}#diagnostic-rapide` pour
  toutes les anciennes URLs (audit GSC à J+30 post-Phase C)

### Impact règles canon

- `R-SEO-02` (Pattern URL Cohérent) : **inchangée** — `/diagnostic-auto/{slug}`
  reste mappé `R5_DIAGNOSTIC`. La consolidation se fait par 301, pas par
  changement de pattern.
- `R-SEO-04` (Longueur de Contenu, R5 min 200 words) : **à actualiser** dans
  une PR séparée → R5 = hub uniquement, contrainte longueur ne s'applique
  qu'au hub `/diagnostic-auto` (pas aux sub-pages, qui n'existent plus en
  page indexable).
- `R-SEO-05` (Maillage Interne) : **inchangée** — l'interdiction `R1 → R5`
  reste valide. Les liens diagnostic-rapide depuis R3 utilisent l'ancre
  intra-page, pas un lien cross-rôle.

### Anti-patterns explicitement interdits

- ❌ Réécrire les 1152 observable drafts squelettiques pour les rendre
  publiables (gaspillage, archi sunsettée)
- ❌ Retirer le filtre `is_published = true` dans
  `get_observable_symptoms_for_gamme` pour faire passer les drafts
  (polluerait S2_DIAG avec ~80-chars stubs)
- ❌ Re-créer des pages `/diagnostic-auto/{slug}` indexables (revient sur
  la décision data-driven de mars 2026)
- ❌ Traiter A (`__diag_*`) et B (`diagnostic_relations[]`) comme des **alternatives** (choisir l'une, ou
  concaténer ad hoc). Ce sont des **entrées complémentaires** d'une composition déterministe (§ Correction
  2026-07-07). *(supersede l'ancien « choisir P1 ou P2 par gamme, pas concaténer ».)*

## Métriques de succès

| Phase | Métrique | Cible | Mesure |
|-------|----------|-------|--------|
| B | Sessions liées customer_id | ≥80% nouvelles | `SELECT COUNT(*) FROM __diag_session WHERE customer_id IS NOT NULL` |
| B | Event GA4 `diagnostic_completed` | visible DebugView J+1 | GA4 console |
| C | S2_DIAG nouvelles produites | +80 sur 126 | `__seo_gamme_conseil` count S2_DIAG ≥ 213 |
| C | Quality score nouvelles S2_DIAG | avg ≥70 | `AVG(sgc_quality_score)` |
| D | Couverture finale S2_DIAG | ≥95% (245+/259) | idem |
| GSC J+30 post-C | Impressions pages conseil avec S2_DIAG | +20% vs baseline | GSC API |

> **SUPERSEDED HISTORICAL METRICS 2026-07-07** — les cibles Phase C RAG-batch ci-dessus (S2_DIAG nouvelles
> **+80/126**, quality **avg ≥70**, **GSC J+30 post-C +20 %**) sont **conservées pour audit trail
> uniquement** ; ce ne sont **plus des cibles d'exécution** (Phase C superseded, § Correction). La couverture
> « finale ≥95 % » (Phase D) et toute cible de couverture canonique S2_DIAG ne se **mesurent qu'une fois la
> projection déterministe DB (`__diag_*`) + WIKI (`diagnostic_relations[]`) en place** — **aucun nouveau seuil
> chiffré n'est fixé ici**. Les métriques **B** (instrumentation `customer_id`, GA4) restent actives.

## Rollback

- **Phase B (instrumentation)** : `ALTER TABLE __diag_session DROP COLUMN
  customer_id` ; suppression event GA4 (no-op côté backend)
> ⚠ SUPERSEDED 2026-07-07 — voir § Correction (RAG retiré des sources S2_DIAG).

- **Phase C (batch RAG)** : si quality < 70 ou pollution détectée →
  `DELETE FROM __seo_gamme_conseil WHERE sgc_section_type = 'S2_DIAG' AND
  sgc_enriched_at > 'YYYY-MM-DD' AND sgc_enriched_by = 'batch-rag-runner'`
> ⚠ SUPERSEDED 2026-07-07 — voir § Correction (RAG retiré des sources S2_DIAG).

- **Phase D (RPC moteur)** : conserver l'ancien `buildS2DiagFromObservable`
  jusqu'à validation Phase D ; switch via flag env
  `S2_DIAG_SOURCE=observable|diag_engine`

## Open questions

1. **Mapping pg_id ↔ system_id** — gouvernance du seed : quel humain valide
   les ~400 mappings ? Outil d'aide à la décision (LLM-suggéré + review) ?
2. **Pages historiques R5** — les 1176 URLs sub-pages ont-elles toutes des
   redirects 301 fonctionnels ? Audit GSC à J+30 obligatoire pour vérifier
   l'absence de 404.
3. **R5 hub évolutions** — le hub `/diagnostic-auto` doit-il rester un
   wizard pur ou ajouter du contenu SEO (long copy expliquant le diagnostic
   auto) ? Décision business hors scope ADR.
4. **Multi-gammes par symptôme** — un symptôme peut concerner plusieurs
   gammes (ex: "voyant moteur" → bougies, sondes, injecteurs). La RPC
   `build_s2_diag_from_diag_engine` doit-elle prioriser la primary_match ou
   ranger par poids ? Sortie Phase D.

## Références

- ADR-015 — Vault Single Source of Truth (G1)
- ADR-022 — R8 RAG Control Plane (pattern propose-before-write similaire)
- ADR-025 — SEO Department Architecture (Module 2 On-page intelligence)
- Commit `a57cefc7` (monorepo) — consolidation initiale R5 → R3 S2_DIAG
- `rules-seo-pagerole.md` — règles R-SEO-02, R-SEO-04, R-SEO-05
- Plan d'exécution : `/home/deploy/.claude/plans/verifier-ce-que-mutable-cake.md`
  (audit Phase 0 du 2026-04-25)
