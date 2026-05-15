---
id: ADR-066
title: "R2 Content Composition v2 — Per-Motorisation Variation with Eligibility Gate, Catalog-First Diversity, SUPPRESSED Canonical"
status: accepted
date: 2026-05-15
decision_date: 2026-05-15
decision_makers: [Fafa]
supersedes: []
superseded_by: []
related_rules: [G1, T1, AI1]
related_incidents: []
reviewed_by: "@fafa"
---

# ADR-066 : R2 Content Composition v2 — Pipeline 4-gates, Eligibility-First, SUPPRESSED Canonical

## Contexte

Le rôle SEO `R2_PRODUCT` (URL `/pieces/:gamme/:marque/:modele/:type.html`) génère aujourd'hui **un seul contenu par couple (gamme, type_id)** sans variation per-motorisation ET sans gate d'éligibilité business.

Volumétrie cible :
- **232 gammes G1/G2** × **53 959 types** (auto_type, 30 502 legacy + 23 457 remap TecDoc) × **~1.5 motorisations variant** ≈ **6,9M URLs théoriques**
- Indexables après filtre `product_count<2 → noindex` : **~200K-500K URLs**

Le contrat Zod `backend/src/config/r2-content-contract.schema.ts` (version 1.0.0) **prévoit déjà** les champs `fuelType, engineCode, phase, powerHp, productionStart/End` + 6 fingerprints + métriques (`productSetUniquenessScore, compatibilityDeltaScore, catalogStructureDeltaScore, semanticSimilarityScore`). La structure est prête. L'enricher actuel `backend/src/modules/admin/services/r2-enricher.service.ts:165` est minimaliste (formule `sectionsGenerated*25 + 20`, regex sur RAG markdown).

R8 (rôle véhicule) dispose déjà d'un pipeline anti-duplicate mature : 8 métriques + 6 fingerprints + governance gate INDEX/REVIEW/REGEN/REJECT + tables `__seo_r8_pages`, `__seo_r8_fingerprints`, `__seo_r8_similarity_index`, `__seo_r8_regeneration_queue`, `__seo_r8_qa_reviews`.

### Risque dominant — sur-indexation pseudo-différenciée

Le vrai risque n'est PAS technique. C'est l'**explosion de cardinalité SEO inutile** : pages "pseudo différenciées" mais économiquement faibles. Cas pathologique typique : 1.6 TDI 105ch vs 1.6 TDI 110ch — même OEM set, même catalogue produits, même structure. Générer du contenu artificiellement distinct produirait :

- embeddings différents artificiellement (LSH/cosine satisfait) ;
- valeur SEO réelle quasi nulle (Google clusterise / ignore) ;
- dilution crawl budget (~7M URLs si on génère naïvement) ;
- cannibalisation interne ;
- index bloat (impossible à QA long terme).

Une discrimination structurelle (catalogue, OEM, équipementiers, prix médian) est plus puissante qu'une discrimination textuelle (LSH MinHash, embeddings cosine) pour ce type de contenu transactionnel. La discipline industrielle exige : filtrer AVANT générer.

### Verdict empirique qui motive la décision

Revue critique expert (2026-05-15) sur plan initial v1 : 10 points correctifs majeurs identifiés (eligibility gate manquant, catalog signature absent, SUPPRESSED decision manquante, SoT au mauvais endroit, mega JSONB non viable à scale, cluster_key trop faible, ordre diversity inversé, GSC observability manquante, Rego over-scope, IntentGraph V3+). Plan v2 (`/home/deploy/.claude/plans/le-contenu-de-r2-scalable-tower.md`) intègre les 10 refinements + 7 améliorations self-review (anti-canonical-chain, cluster serialization, deterministic input_hash, feature flag kill-switch, calibration script, stratified pilot, embedding staleness).

## Décision

Adopter **R2 Content Composition v2** comme pipeline canonique pour la génération de contenu R2_PRODUCT, structuré en **4 gates** avec hard exit progressif :

### Pipeline 4-gates

```
GATE 1 : R2EligibilityService.shouldGenerate(typeId, pgId)
  eligibilityScore ∈ [0..100]
    = 0.35×motor + 0.35×compat + 0.20×commercial + 0.10×crawl
  Si < THRESHOLD_V1 (=45/100) → STOP. Pas de compose, pas de LLM.

GATE 2 : R2CompositionService.compose(R1, R8, motor, cluster)
  Pure fn → R2PageContract. Persiste snapshot SoT input
  dans __seo_r2_composition_inputs (replay-safe, hash déterministe).

GATE 3 : R2DiversityService — STRUCTURAL-FIRST
  3.a  catalog_signature : sha256(sorted_oem + sorted_subgroups + product_family_counts)
       overlap > 0.92 + sibling INDEX fiable → SUPPRESSED canonical
       overlap > 0.92 + aucun canonical fiable → REJECT contrôlé
  3.b  Structural delta (motor + commercial distinctiveness)
  3.c  LSH MinHash bands (Jaccard sur shingles)
  3.d  pgvector cosine embeddings (only si 3.a-c ambigu)

GATE 4 : R2GovernanceGate (Rego invariants + decision matrix)
  Décisions : INDEX | SUPPRESSED | REVIEW | REGENERATE | REJECT
  Rego = invariants only (forbidden signals, cluster health, collisions).
  Scoring/logique métier reste en TS.
```

### Refinements canoniques (10)

1. **R2EligibilityService AVANT compose** — hard exit avant LLM/embeddings (économie + qualité)
2. **commercialDistinctivenessScore** — Δfamilles + Δ OEM + Δ équipementiers + Δ prix médian + Δ compat (le vrai discriminant transactionnel, pas Δhp)
3. **SUPPRESSED decision (NEW)** — canonical vers sibling INDEX au lieu de reject ou index aveugle (évite index bloat)
4. **catalog_signature structural early-gate** — overlap > 0.92 → SUPPRESSED si sibling INDEX fiable, sinon REJECT contrôlé (jamais reject direct)
5. **Tables splittées** — `__seo_r2_{pages, page_content, metrics, signatures, embeddings, composition_inputs, page_versions, qa_reviews, regeneration_queue, eligibility_log, gsc_observations}` (pas mega JSONB)
6. **cluster_key v2** — `vehicle_family_id = sha256(brand + model_group + phase + platform + generation)` matérialisé si colonnes présentes, fallback v1 documenté
7. **Inversion diversity structural-first** — catalogue > texte pour transactionnel
8. **SoT = R2CompositionInput** (snapshot), pas R2PageContract (replay-safe 18 mois)
9. **r2-search-console-observer.service.ts** V1.5 — pilotage SEO réel via GSC URL Inspection (borné ~110 URLs/jour, JAMAIS 500K)
10. **OPA/Rego discipline stricte** — invariants/conformité uniquement, scoring/logique métier reste en TS

### Improvements correctness + ops (7, self-review)

| Improvement | Garde-fou |
|-------------|-----------|
| A | Anti-canonical-chain : invariant Rego (canonical_target.decision=INDEX, same pg_id) + cascade BullMQ `r2-canonical-revalidate` |
| B | Cluster serialization : Redis lock per `cluster_key` + leader-first order (`eligibilityScore DESC, type_id ASC`) |
| C | input_hash déterministe : `fast-json-stable-stringify` AVANT sha256 (jamais JSON.stringify natif) |
| D | Feature flag `R2_V2_ENABLED` (env + Redis runtime) default false — kill-switch sans redeploy |
| E | Calibration script `scripts/audit/r2-eligibility-calibration.ts` (N=200 stratified) — THRESHOLD_V1=45 confirmé empiriquement, jamais arbitraire |
| F | Pilote V1 stratified : 5 URLs même cluster_key (test SUPPRESSED) + 5 URLs distincts (test INDEX) |
| G | Embedding staleness : `__seo_r2_embeddings(page_id, content_hash, embedding)` + UNIQUE(page_id, content_hash) — recompute auto si content_hash change |

### Division responsabilités (TS vs Rego)

**TS (scoring + logique métier, testable + property-based fast-check)** :
- Calcul des 4 sous-scores eligibility (motor, compat, commercial, crawl) avec weights 0.35/0.35/0.20/0.10
- THRESHOLD_V1=45 constant exporté depuis `r2-eligibility.constants.ts`
- Algorithmes : `catalog_overlap_score`, LSH MinHash bands, cosine pgvector
- Décisions composites (INDEX vs REVIEW vs REGENERATE selon scores)
- Cascade revalidation handler

**Rego (invariants/conformité, WASM sync <1ms)** :
- `r2-content-write.rego` :
  - source_kind enum strict
  - forbidden signals (prix, promo, stock, panier, livraison, ajouter au panier) hors `S_REASSURANCE` → deny
  - `decision=SUPPRESSED → canonical_target_type_id non-null AND canonical_target.decision=INDEX AND canonical_target.pg_id=self.pg_id` (anti-chain, no cross-gamme)
  - `eligibility_score ∈ [0, 100]`
  - `retry_count ≤ 2`
  - `decision=INDEX → content_hash non-null`
  - `pipeline_generated requires feature_flag_r2_v2_enabled=true AND no lock_active`
- `r2-cluster-health.rego` :
  - `cluster_healthy` ssi ≥ 85% pages cluster `semanticSim ≤ 0.80`
  - `deny_page` si `sameContentFingerprintCount > 0` (collision exacte)

## Conséquences

### Positives

- **Filtrage agressif AVANT LLM** : eligibility gate filtre ~30-40% URLs avant génération → économie massive ($10K+ en LLM calls à V2 scale)
- **Anti index bloat** : SUPPRESSED canonical conserve le SEO long-tail légitime sans publier duplicate content
- **Replay-safe** : SoT = CompositionInput permet régénération dans 18 mois avec nouveau modèle Claude/scoring sans re-collecter R1+R8
- **Maintenabilité long terme** : tables splittées (VACUUM/TOAST/WAL isolés), Rego limité aux invariants
- **Observabilité réelle** : GSC observer V1.5 mesure `chosenCanonical`, `crawledNotIndexed`, position, CTR — pilotage SEO non aveugle

### Négatives

- **Complexité opérationnelle** : 4 gates au lieu d'1 pipeline, 11 tables, 2 queues BullMQ (`r2-content-gen` + `r2-canonical-revalidate`) — courbe d'apprentissage
- **Coût stockage** : +16GB sur base 221GB (toujours sous Supabase Pro 500GB, pas d'upgrade tier)
- **Risque calibration** : THRESHOLD_V1=45 + weights commercialDistinctiveness (0.30/0.25/0.20/0.15/0.10) sont initiaux, à ajuster par calibration script avant V1 merge

### Risques + mitigations

| Risque | Mitigation |
|--------|------------|
| Sur-indexation pseudo-différenciée | Gate 1 eligibility + commercialDistinctivenessScore + catalog_signature early-canonical |
| Index bloat (siblings) | Décision SUPPRESSED + canonical_target_type_id + canonical link tag frontend |
| Race condition cluster | Concurrency=1 par cluster_key via Redis lock + leader-first deterministic order |
| Canonical chain orphelin | Invariant Rego anti-chain + queue BullMQ cascade revalidation |
| Replay impossible 18 mois | SoT = `__seo_r2_composition_inputs` + hash déterministe via `fast-json-stable-stringify` |
| Mega JSONB TOAST/WAL | Tables splittées (11 tables par cycle d'accès hot/cold/froid) |
| OPA over-scope | Discipline stricte : Rego = invariants, scoring TS testable |
| Pilotage SEO aveugle | GSC observer V1.5 (borné ~110 URLs/jour pour respect quota URL Inspection) |
| Pilote 10× INDEX (gate ne discrimine pas) | Stratified sampling (5 même cluster + 5 distincts) + KPI mix INDEX+SUPPRESSED+REJECT obligatoire avant PR 2 |

## Rollout — Sequence

- **PR 0 (cet ADR + 2 Rego policies)** — vault, prérequis bloquant
- **PR 1** — monorepo, V1 Foundation (eligibility gate + split tables + SUPPRESSED + auto_modele_family audit-only fallback-safe). Branche `feat/seo-r2-composition-v2-foundation` depuis main.
- **Gate V1 → PR 2 (HARD)** : pilote 10 URLs stratified retourne mix sain (4-7 INDEX + 2-4 SUPPRESSED + 0-2 REJECT). PAS 10× INDEX. Sinon retour planche à dessin scoring/threshold.
- **PR 2** — monorepo, V1.5 Pipeline (BullMQ + diversity service + GSC observer borné). Gated également par KPI métier (+20% clics OR -5pts position 14j vs control).
- **PR 3** — monorepo, V2 Scale (HNSW, circuit breaker, LLM tiered routing, sitemap 10 shards). Gated par V1.5 stable ≥5 gammes G1, 30j obs.

Plan complet (architecture, file paths, tests, verifications) : `/home/deploy/.claude/plans/le-contenu-de-r2-scalable-tower.md` (workstation Fafa).

## Hors scope

- V3 `R2IntentGraph` (transactional_intent → 6 sub-intents → composition dynamique blocs) — direction notée, non implémentée
- Fix `gamme-data-transformer.service.ts:15` (price signals "à prix bas" leak en R1 meta) — dette séparée, PR autonome plus tard
- Migration de `__seo_r2_keyword_plan` (legacy) vers `__seo_r2_pages` — bridge conservé V1/V1.5, deprecation V2
- Sitemap real per-URL `lastmod` — bloqué par dette audit columns (cf MEMORY `feedback_no_real_lastmod_per_url_until_audit_columns`), proxy `generation_timestamp` suffit

## Références

- Plan : `/home/deploy/.claude/plans/le-contenu-de-r2-scalable-tower.md`
- Monorepo cible : `ak125/nestjs-remix-monorepo`
- Pattern miroir : `workspaces/seo-batch/.claude/agents/r8-keyword-planner.md` (R8 mature)
- Contrat Zod existant : `backend/src/config/r2-content-contract.schema.ts`
- Enricher actuel : `backend/src/modules/admin/services/r2-enricher.service.ts`
- Policy mirror : `governance-vault/policies/seo-content/h1-write.rego` (ADR-PR-V)
- Memories canon liées (monorepo memory, hors vault wikilink graph) : `feedback_seo_eligibility_gate_before_generation`, `feedback_seo_catalog_signature_before_text_diversity`, `feedback_seo_suppressed_canonical_decision`, `feedback_seo_sot_is_composition_input_not_content`, `feedback_table_split_vs_mega_jsonb`, `feedback_opa_rego_invariants_only`, `feedback_canonical_chain_prevention`, `feedback_seo_cluster_serialization_concurrency`, `feedback_deterministic_input_hash_canonical_json`
