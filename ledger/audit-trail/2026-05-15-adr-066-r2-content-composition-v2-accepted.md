---
date: 2026-05-15
type: audit-trail
related: [ADR-066, ADR-049, ADR-058, ADR-059, ADR-031, MOC-Decisions, MOC-AuditTrail]
---

# 2026-05-15 — ADR-066 R2 Content Composition v2 (acceptance + PR 0 vault)

## What

Création et acceptance de **[[ADR-066-r2-content-composition-v2]]** + livraison PR 0 vault :

- ADR-066 `status: accepted` (date 2026-05-15, decision_maker `@fafa`, reviewed_by `@fafa`)
- 2 nouvelles policies Rego (invariants only) : `r2-content-write.rego` + `r2-cluster-health.rego` + tests OPA correspondants
- Script générique `_scripts/build-opa-bundles.sh` (compile + reproductibilité SHA-256)
- WASM bundles pré-compilés dans `dist/policies/` (r2-content-write.wasm, r2-cluster-health.wasm)
- Workflow `opa-policy-build.yml` étendu pour itérer les 3 policies (h1-write + 2 R2) via le script
- 66/66 tests OPA passent localement (`opa 0.69.0` épinglé)

## Why

R2_PRODUCT (URL `/pieces/:gamme/:marque/:modele/:type.html`) génère aujourd'hui un seul contenu par couple (gamme, type_id), sans variation per-motorisation et sans gate d'éligibilité business. À l'échelle (232 gammes G1/G2 × ~50K types × ~1.5 variants ≈ 6,9M URLs théoriques, ~200K-500K indexables), c'est une garantie de duplicate content Google et de cardinalité SEO inutile (1.6 TDI 105 vs 110, même OEM, même catalogue → pseudo-différenciation artificielle).

ADR-066 adopte un pipeline **4 gates** miroir R8 mature : Eligibility (avant LLM) → Composition (pure fn + SoT snapshot) → Diversity (structural-first : catalog → motor → LSH → embeddings) → Governance (Rego invariants + décision INDEX/SUPPRESSED/REVIEW/REGEN/REJECT). La décision pilote a été conduite en 4 rounds itératifs avec un reviewer expert :

1. **Round 1** : plan v1 proposait eligibility implicite + diversity text-first (MinHash + embeddings) + décision binaire INDEX/REJECT. Reviewer a flagué le vrai risque opérationnel : explosion de cardinalité pseudo-différenciée (Δhp seul ne suffit pas).
2. **Round 2** : ajout de 10 refinements canon — `R2EligibilityService` avant compose, `commercialDistinctivenessScore` (Δfamilles + Δ OEM + Δ équipementiers + Δ prix médian + Δ compat), **décision `SUPPRESSED`** (canonical sibling au lieu de reject ou index aveugle), `catalog_signature` structural early-gate (overlap > 0.92 → SUPPRESSED si sibling INDEX fiable, sinon REJECT contrôlé), tables splittées (8 tables au lieu d'1 mega JSONB), `cluster_key v2` matérialisé (`vehicle_family_id` audit-only fallback-safe), inversion diversity structural-first, SoT = `R2CompositionInput` (replay-safe 18 mois), GSC observer borné, Rego invariants-only.
3. **Round 3** : self-review correctness + ops ajoute 7 improvements — anti-canonical-chain (invariant Rego + cascade BullMQ), cluster serialization (Redis lock per cluster_key, leader-first), `input_hash` déterministe (`fast-json-stable-stringify` AVANT sha256), feature flag `R2_V2_ENABLED` (kill-switch), calibration script empirique (`THRESHOLD_V1=45` validé sur N=200, pas inventé), pilote V1 stratified sampling (5 même cluster + 5 distincts), embedding staleness (UNIQUE(page_id, content_hash)).
4. **Round 4** : 6 patches surgicaux finaux (catalog_overlap > 0.92 → SUPPRESSED uniformément, UNIQUE indexes explicites, GSC observer scope borné ~110 URLs/jour vs JAMAIS 500K, SUPPRESSED rules explicites — `noindex` interdit par défaut, audit-only fallback-safe `auto_modele_family`, test catalog signature property aligné SUPPRESSED/REJECT).

Discipline canon enforced : **scoring (weights 0.35/0.35/0.20/0.10, threshold 45, algorithmes catalog_overlap/LSH/cosine) reste en TS testable + property-based fast-check, JAMAIS en Rego** (cf `feedback_opa_rego_invariants_only` persisté en mémoire monorepo).

## Architecture livrée PR 0

| Livrable | Path | Rôle |
|----------|------|------|
| ADR | `ledger/decisions/adr/ADR-066-r2-content-composition-v2.md` | Canon LIVE (status accepted) |
| Policy invariants R2 write | `policies/seo-content/r2-content-write.rego` | source_kind, decision matrix, anti-chain, anti cross-gamme, forbidden signals hors S_REASSURANCE, retry max, score range, feature flag |
| Policy invariants cluster | `policies/seo-content/r2-cluster-health.rego` | cluster_healthy ≥ 85% INDEX healthy, deny_collision exact, deny_canonical_chain, cluster_pollution_detected >70% SUPPRESSED |
| Tests OPA | `policies/seo-content/r2-content-write_test.rego` (29 tests) + `r2-cluster-health_test.rego` (15 tests) | property + table-driven |
| Script générique | `_scripts/build-opa-bundles.sh` | itère POLICIES array, build via paths relatifs (reproductibilité SHA), drift-check possible localement |
| WASM bundles | `dist/policies/r2-content-write.wasm` + `r2-cluster-health.wasm` + `.bundle.tar.gz` | pré-compilés (opa 0.69.0 pinned), embed dans monorepo PR 1 |
| Workflow CI | `.github/workflows/opa-policy-build.yml` | test + build + SHA-256 drift check pour les 3 policies (h1-write + r2-content-write + r2-cluster-health) |

**Pré-flight local validé** : `/tmp/opa test policies/seo-content/ -v` → **66/66 PASS** (22 h1-write existants + 29 r2-content-write nouveaux + 15 r2-cluster-health nouveaux). SHA-256 reproductible localement après fix paths relatifs depuis vault root (le WASM embed le source path en debug section).

## Bénéfices anticipés (à mesurer pilote V1)

- Filtrage agressif **AVANT LLM** : eligibility gate estimée à 30-40% des URLs filtrées avant génération → économie massive ($10K+ en LLM calls à V2 scale 500K URLs).
- Anti index bloat : SUPPRESSED canonical conserve le SEO long-tail légitime des siblings sans publier duplicate content (vs. REJECT qui perd les motorisations marginales).
- Replay-safe 18 mois : SoT = `__seo_r2_composition_inputs` permet régénération avec nouveau modèle Claude/scoring sans re-collecter R1+R8.
- Maintenabilité long terme : 8 tables splittées (VACUUM/TOAST/WAL isolés par hot/cold/froid), Rego limité aux invariants (pas de scoring).
- Pilotage SEO non-aveugle : GSC observer V1.5 mesure `chosenCanonical`, `crawledNotIndexed`, position, CTR (borné à ~110 URLs/jour, jamais 500K — respect quota URL Inspection ~2000/jour).

## Impacts cross-canon

- **ADR-031 (Cadre 4-layer canonical raw/wiki/exports/consumers)** : R2 v2 respecte le cadre, schemas + scoring en L2 (wiki), runtime BullMQ + Rego en L4 (consumers).
- **ADR-049 (DB Governance)** : 11 migrations PR 1 monorepo (toutes RLS enabled + GRANT explicite service_role uniquement par `feedback_supabase_grant_explicit_for_new_projects`), validation squawk obligatoire.
- **ADR-058 (Repository Control Plane)** : nouveau module `backend/src/modules/seo/r2/` à tracer dans `ownership.yaml` (domain D8 SEO, owner @fafa).
- **ADR-059 (SEO Runtime Projection)** : R2 v2 entry sera ajouté en Phase B (sous préconditions hold actuelles).
- **MOC-Decisions** : ADR-066 indexé (formule canonique grepable : « eligibility avant LLM + structural diversity-first + SUPPRESSED canonical = pipeline 4-gates anti-cardinalité SEO inutile »).

## Sequence rollout

- **PR 0 (cet ADR + 2 Rego policies, vault)** : EN COURS — prérequis bloquant pour PR 1 monorepo
- **PR 1 (monorepo)** : V1 Foundation après merge PR 0 — 11 migrations + eligibility service + composition pure + scoring TS + 4 nouveaux scores + tests property-based + calibration script + feature flag kill-switch
- **Gate V1 → PR 2 (HARD)** : pilote 10 URLs stratified (5 même cluster + 5 distincts) doit retourner mix sain (4-7 INDEX + 2-4 SUPPRESSED + 0-2 REJECT). PAS 10× INDEX. Sinon retour planche à dessin scoring/threshold.
- **PR 2 (monorepo, BLOQUÉ)** : V1.5 Pipeline BullMQ + GSC observer borné. Gated également par KPI métier 14j (+20% clics OR -5pts position vs control).
- **PR 3 (monorepo, différé)** : V2 Scale (HNSW, circuit breaker, LLM tiered routing, sitemap shards). Gated par V1.5 stable ≥5 gammes G1, 30j obs.

## Canon mémoire ajouté au monorepo

8 mémoires `feedback_*` persistées dans `/home/deploy/.claude/projects/-opt-automecanik-app/memory/` (avec entrées dans MEMORY.md index) :

- `feedback_seo_eligibility_gate_before_generation` — Gate avant LLM/embeddings/MinHash
- `feedback_seo_catalog_signature_before_text_diversity` — Catalog > texte pour transactionnel
- `feedback_seo_suppressed_canonical_decision` — SUPPRESSED ≠ REJECT, sibling canonical
- `feedback_seo_sot_is_composition_input_not_content` — SoT replay-safe
- `feedback_table_split_vs_mega_jsonb` — DB hot/cold/froid
- `feedback_opa_rego_invariants_only` — Rego = invariants, jamais scoring
- `feedback_canonical_chain_prevention` — Anti-chain + cascade revalidation
- `feedback_seo_cluster_serialization_concurrency` — Cluster lock leader-first
- `feedback_deterministic_input_hash_canonical_json` — fast-json-stable-stringify obligatoire

Ces mémoires institutionnalisent les leçons de la revue critique 4-rounds pour tout travail SEO content-gen futur.

## Follow-ups (out of scope post-acceptance)

- **R1 forbidden signals fix** : `gamme-data-transformer.service.ts:15` contient "neuf & à prix bas" + "au meilleur tarif" en meta description R1, viole la règle "transactional signals confined to R2 S_REASSURANCE". À traiter dans PR autonome monorepo, hors PR 1 R2 v2.
- **`auto_modele_family` backfill** : si `modele_phase/platform/generation` colonnes absentes, fallback `cluster_key v1` documenté en dette ADR. Backfill nécessiterait PR séparée ownership SEO+Data.
- **V3 IntentGraph aspirational** : direction notée (transactional_intent → 6 sub-intents → composition dynamique blocs) — hors V1/V1.5/V2. À ré-évaluer post-V2 stabilisé.
- **Sitemap real per-URL lastmod** : bloqué par dette audit columns (cf `feedback_no_real_lastmod_per_url_until_audit_columns`), proxy `generation_timestamp` suffit pour R2 v2.

## Self-review verdict

**APPROVE** — ADR exhaustif (2 rounds expert + self-review ops), policies Rego testées 44/44, build script reproductible, workflow CI étendu, tests locaux 66/66 PASS, mémoires canon persistées. Aucun scoring/logique métier en Rego (discipline stricte respectée). PR 0 vault prêt pour review humain et merge avant PR 1 monorepo.
