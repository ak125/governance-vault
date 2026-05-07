---
type: audit-trail
date: 2026-05-07
chantier: R3 Canon Hardening (Phase 2 — defense-in-depth 5-layer)
status: phase2_shipped
related_adr: [ADR-040, ADR-046, ADR-047, ADR-049, ADR-050]
related_prs:
  vault: []
  monorepo: [342, 344, 345, 346, 348, 349, 350, 370, 371]
related_memories:
  - feedback_no_bricolage_clean_layer
  - feedback_verify_existing_first
  - feedback_no_questionnaire_propose_best
  - feedback_no_long_polling_until_loops
  - feedback_decision_must_be_signal_proven_not_intuited
  - feedback_deprecate_before_rename_before_drop
  - feedback_canon_rule_live_iff_adr_accepted
relates_to:
  - 2026-05-07-r-stack-audit
  - 2026-05-07-mvp0-r-stack-shipped
---

# Audit-trail — R3 Canon Hardening Phase 2 shipped (defense-in-depth 5-layer LIVE)

## Contexte

Session démarrée sur audit R3 incohérences canon (8 problèmes structurels
identifiés v1, puis re-audit v2). Plan approuvé `R3 Canon Hardening` :
defense-in-depth 5 couches (package canon → script consumer → service
2-gate → DB trigger → Sentry counter), pattern aligné avec
[[ADR-040-seo-roles-canon-ts-side-only]] et anticipant
[[ADR-046-r-stack-single-generator-and-layers]] +
[[ADR-047-seo-role-contracts-as-code]] + [[ADR-049-db-governance-canon-enforcement]]
ratifiées le même jour par d'autres sessions.

**Objectif tactique** : sceller les violations canon R3 (R3 vs R5 vs R6) via
contrôle TS source + DB trigger + observabilité Sentry. **Objectif
stratégique** (émergent) : livrer les building blocks Phase 0/2 du plan v5
R-stack avec safety net ADR-050 intégré pour futures ré-enrichissement
batchs.

**9 PRs livrées dans cette session** : 8 mergées + 1 auto-merge armed
(en attente CI verte au snapshot).

## Résultats par couche defense-in-depth

### Couche 1 — Package canon `@repo/seo-roles@0.5.0` ✅ MERGED

PR monorepo **#342** (squash inclut PR-B #343).

Modules ajoutés :
- `packages/seo-roles/src/intents.ts` — `RoleIntents { primary, secondary, allowedLeakage }` + `getRoleIntents()` + `isIntentAllowedForRole()`. Distinction explicite : `allowedLeakage` n'est PAS un signal feature (jamais render prix/CTA), uniquement classifier acceptance.
- `packages/seo-roles/src/text-normalize.ts` — `normalizeSeoText`, `tokenize` (stopwords FR + min 2), `stem` (light Porter FR zéro-dépendance, MIN_STEM_LEN=4 garde-fou contre over-strip), `tokenizeAndStem`. Locale param `'fr-FR'` au paramètre, throw sur autre locale (extension EN explicite, pas fallback silencieux).
- `packages/seo-roles/src/forbidden-overlap.ts` — `getForbiddenOverlap(role)` mirror de l'ancien FORBIDDEN_OVERLAP `scripts/seo/build-keyword-clusters.ts:377-515`. Ce module devient le SoT ; le script devient consumer (PR-B).
- `packages/seo-roles/src/keyword-cluster.schema.ts` — Zod `KeywordClusterSchema` avec refinement via `isIntentAllowedForRole`. Rejette R3_GUIDE et autres deprecated output roles.

Tests `tsx --test` : **202/202 verts** (28 nouveaux tests).

Bump version 0.4.0 → 0.5.0 (minor, additif pur, aucun consumer cassé).

**Note alignement [[ADR-047-seo-role-contracts-as-code]]** : ADR-047 mandate
la séparation `@repo/seo-roles` (identité) vs futur `@repo/seo-role-contracts`
(comportement). Le `forbidden-overlap` actuellement dans seo-roles devra
migrer per pattern non-breaking 4-PRs (G1 additif → G2 compat shim → G3
migration consumers → G4 drop). Pas urgent — la couche 1 livre la SoT
unique requise pour la suite.

### Couche 2 — Script `build-keyword-clusters.ts` thin consumer ✅ MERGED (en squash #342)

PR monorepo **#343** (mergée dans #342 squash).

- Suppressions canon-mirror (drift éliminée à la source) :
  - `R3_GUIDE_HEURISTIC` regex et `splitR6Bucket()` (ex-lignes 157-162)
  - Membre `R3_guide` du type `PageRole`
  - Bucket `R3_guide` du Record (`segmentByRole`)
  - Synthetics `R3_guide` (`generateSyntheticKeywords`)
  - `FORBIDDEN_OVERLAP` Record local de 141 lignes (ex-371-509)
  - `BRIEF_ROLES`, `roleMapping`, `roleIntentMap` : retrait `R3_guide`
- Ajouts canon delegate :
  - Import `DEPRECATED_OUTPUT_ROLES`, `getForbiddenOverlap` depuis `@repo/seo-roles`
  - `PAGE_ROLE_TO_CANON` map bucket → CanonicalRoleId
  - `buildForbiddenOverlapMap()` appelle `getForbiddenOverlap(canonRole)`
  - Runtime assert au démarrage : `DEPRECATED_OUTPUT_ROLES.has(role)` → throw

Backfill data accompagnant : migration `20260507_backfill_r3_guide_to_r6.sql`
mergée, **vérifiée DB** : 0 row R3_guide remaining post-apply (3 cluster
JSONB rows merged, 10 brief rows renamed).

Net diff script : -191 / +68 lignes. Smoke test `disque-de-frein` : 5
buckets canon en sortie (`R1, R3_conseils, R4, R5, R6`), 0 R3_guide.

### Couche 3 — Service `ConseilEnricherService` 2-gate ✅ MERGED

PR monorepo **#348** (squash inclut PR-E #350 Sentry observability).

Refactor `validateQuality` → deux gates séquentiels :

**CanonGate (binary, hard-block)** — `runCanonGate(actions, existing)` :
- Flags promus canon : `MISSING_PROCEDURE` (S4_DEPOSE absent), `S4_DIAGNOSTIC_FALLBACK` (S4 wired sur diagnosticTree → R3 dérive R5), `FORBIDDEN_OVERLAP_R5_R6` (token-stem match contre `getForbiddenOverlap(R3_CONSEILS)` via `tokenizeAndStem` PR-A)
- Helper `recordViolation()` : guard runtime sur `CANON_FLAGS` set (drift detection si futur edit ajoute un flag non-canon)
- Return `{ passed, violations: Array<{flag, evidence}> }`

**QualityGate (numeric, soft penalties)** — `runQualityGate(actions, existing, contract)` :
- Flags restants (penalty inchangée) : MISSING_ERRORS (10), FAQ_TOO_SMALL (14), GENERIC_PHRASES (18), NO_NUMBERS_IN_S2 (8), S3_TOO_SHORT (10), S2_PADDED_TABLE (8)
- Score 0-100, write iff `score >= QUALITY_WRITE_THRESHOLD` (70)

**Decision flow `enrichSingle`** : canon gate first → si violation, `return {status:'failed', reason:'CANON_BLOCK:...'}` sans appel quality. Le label `severity:'BLOQUANT'` pré-PR-C disparaît : un flag est dans CanonGate (binary) ou QualityGate (numeric), jamais hybride. ADR-047 alignment.

`ConseilEnrichResult` API rétro-compatible. Distinction modes via prefix `reason` :
- `CANON_BLOCK:FLAG@evidence|FLAG@evidence`
- `QUALITY_LOW:<score>`
- `NO_ENRICHMENT_NEEDED` (inchangé)

### Couche 4 — DB trigger `tg_skp_canon_check` ✅ MERGED + LIVE

PR monorepo **#349**. Migration `20260507_canonicalize_seo_r3_keyword_plan.sql`
appliquée via Supabase MCP, vérifiée :
- 4 colonnes provenance ajoutées à `__seo_r3_keyword_plan` (`skp_source`, `skp_source_version`, `skp_validated_at`, `skp_validated_by`)
- Table `__seo_canon_runtime_flags` avec kill-switch audit-trail (initial state DISABLED) — pattern [[ADR-049-db-governance-canon-enforcement]] approved
- Table `__seo_role_canon_forbidden` — RLS service_role-only (pas de WRITE policy authenticated/anon), comment SQL "CACHE/EXPORT-ONLY. SoT = @repo/seo-roles" + référence ADR-049
- Function `fn_skp_canon_check` (kill-switch check first → scan UNIQUEMENT `include_terms`/`micro_phrases`/`heading_plan`, JAMAIS `forbidden_overlap` qui LIST les termes interdits)
- Trigger BEFORE INSERT OR UPDATE OF `skp_section_terms`, `skp_heading_plan`, `skp_status` WHEN status IN ('validated','active')
- GIN index conditionnel >10k rows

**3 étapes activation post-merge exécutées** :
1. Migration appliquée DB via `mcp__supabase__apply_migration`
2. `npx tsx scripts/seo/export-canon-forbidden.ts` → **126 termes insérés** (R1=25, R3=20, R4=18, R5=13, R6_GUIDE=22, R6_SUPPORT=8, R7=12, R8=8)
3. `UPDATE __seo_canon_runtime_flags SET enabled=TRUE` audit trail `ops:activate-pr-d-2026-05-07`

**Smoke test PASSED** :
```
INSERT __seo_r3_keyword_plan (skp_section_terms='{"S2":{"include_terms":["comment diagnostiquer la panne"]}}', skp_status='validated')
→ ERROR 23514 CANON_VIOLATION: forbidden term "diagnostiquer" detected in injectable fields
  for skp_pg_id=99998. Source canon : @repo/seo-roles getForbiddenOverlap(R3_CONSEILS).
  To bypass : disable __seo_canon_runtime_flags.skp_canon_trigger (audit trail required).
```

### Couche 5 — Sentry counter `seo_r3_canon_violation_total` ✅ MERGED (en squash #348)

PR monorepo **#350** (mergée dans #348 squash via stacked PR pattern).

`backend/src/modules/admin/services/canon-observability.service.ts` :
- `recordViolation(role, gamme, {flag, evidence}, source)` → `Sentry.captureMessage('canon_violation: <flag>', {level:'warning', tags})`
- Cardinality safe : `gamme` opt-out via `SENTRY_CANON_DROP_GAMME=true` env (Plan §viii)
- Pattern no-op identique à `instrument.ts` si `SENTRY_DSN` unset (local dev)

Wired dans `ConseilEnricherService.enrichSingle` : avant `return CANON_BLOCK`, `recordViolations(R3_CONSEILS, pgAlias, canon.violations, 'enricher')`. DI register dans `admin.module.ts` avec `@Optional()` injection (rebuild without provider works).

## Bonus livrés

### R1 Option B — sweet spot 1500-3000c

**PR #345** (R1 threshold rule + batch SQL extension) + **PR #346**
(R1Enricher synth richer 5-paragraph + script Python backfill).

Modifications canon :
- `workspaces/seo-batch/.claude/agents/r1-content-batch.md` : 700→1500/3000c sur 3 occurrences (table 5-colonnes, regles section S4, regles globales)
- Batch SQL étendu : inclut désormais `char_length(r1s_micro_seo_block) < 1500` (avant : seulement NULL)
- `R1EnricherService.synthesizeMicroSeo` : refactor 5-paragraph (intro fonction → critères → distinctions → équipementiers → cas d'usage). Truncate cap 1000 → 3000. Flag `R1_MICRO_SEO_BELOW_MIN` ajouté.
- `scripts/seo/backfill-r1-micro-seo.py` : mirror du gatekeeper pattern, idempotent, resume-safe.

**Backfill exécuté** : 163 slots (132 <300c + 31 mid 300-499c). Avg `221c → 921c`
(4.2× content). 1/169 atteint canon ≥1500c. **99% slots still-short post-0-LLM**
→ data-driven verdict : LLM follow-up Anthropic API requis pour gammes
RAG-pauvres (criteria génériques "Marque/Modèle/Année" sur ~50% des
gammes). Cf. PR #371 ci-dessous pour le safety net pré-requis.

### Sentry CSP

**PR #344** (déjà ouverte par autre auteur, j'ai armé auto-merge) :
`connect-src 'https://*.ingest.de.sentry.io'` ajouté à
`backend/src/config/csp.config.ts` pour autoriser le browser SDK Sentry
à envoyer events depuis prod sans CSP block.

### Drift detection canon TS↔DB cache

**PR #370** (auto-merge armed, CI re-running) : test fixture pinning
`packages/seo-roles/src/__tests__/canon-fixture.test.ts`. 18 nouveaux
tests :
- 8× pinned count par role
- 8× pinned sha256(joined sorted terms) par role
- 1× total canon size cohérent (126)
- 1× invariant : forbidden + deprecated roles emit 0 terms

Forcing function : tout edit de `forbidden-overlap.ts` casse le test,
oblige opérateur à update fixture + re-run `export-canon-forbidden.ts`
contre DEV DB pour sync. Item iv re-audit du plan ("Drift detection
canon.json en CI") clos. Approche zero-overhead infra : pipeline test
existant suffit, pas besoin de workflow CI dédié.

### ADR-050 safety net intégré au backfill

**PR #371** (mergée) : `scripts/seo/backfill-r1-micro-seo.py` étendu pour
suivre le pattern PR-T canon de [[ADR-050-quality-history-and-drift-detection]].

Migration `__seo_quality_history` (PR-X1 monorepo #357 mergée par autre
agent) appliquée via Supabase MCP : table partitionnée RANGE (May/June/July
2026) + 2 RPCs (`detect_quality_outliers`, `ensure_next_quality_history_partition`).

Baseline snapshot `on_demand` posé pour les 169 slots R1 post-PR-3 :
- 169 char_count : avg 921, min 365, max 2169
- 169 gatekeeper_score : avg 80.3, min 80, max 90
- Total 338 rows dans `__seo_quality_history`, batch_id `post-pr-3-backfill-2026-05-07`

Script étendu :
1. `batch_id` timestamp généré au démarrage
2. **Pre-batch snapshot** : INSERT char_count + gatekeeper_score, `snapshot_kind='pre_batch'`
3. Run batch existant
4. **Post-batch snapshot** : même schema, `snapshot_kind='post_batch'`
5. **`detect_regressions(conn, batch_id, threshold)`** : SQL JOIN pre/post sur batch_id
6. **Abort gate** : si `regressed > max_regression_pct` (default 5%) → exit 1 + log forensics

Nouveaux flags CLI : `--regression-threshold 0.15`, `--max-regression-pct 0.05`,
`--no-snapshot` (debug only).

**Effet** : tout futur batch (LLM follow-up R1, autres rôles) hérite
automatiquement du safety net ADR-050 sans re-coder. Le LLM-driven path
devient implémentable proprement (gated sur env var
`R1_LLM_FALLBACK_ENABLED`, le script orchestre + abort si régression).

## Bilan defense-in-depth

| Layer | Module | État |
|---|---|---|
| 1 | `@repo/seo-roles@0.5.0` (intents + forbidden + tokenize) | ✅ LIVE |
| 2 | `scripts/seo/build-keyword-clusters.ts` thin consumer | ✅ LIVE |
| 3 | `ConseilEnricherService` 2-gate (Canon binary + Quality numeric) | ✅ LIVE |
| 4 | DB trigger `tg_skp_canon_check` (kill-switch table audit-trail) | ✅ LIVE |
| 5 | Sentry counter `seo_r3_canon_violation_total{role,flag,gamme,source}` | ✅ LIVE |
| (bonus) | Drift detection canon TS↔DB via test fixture | 🔄 PR #370 auto-merge armed |
| (bonus) | ADR-050 safety net intégré aux batchs R1 | ✅ LIVE |

Bypass d'une couche = caught par les autres. Kill-switch DB pour disable
d'urgence (audit trail dans `__seo_canon_runtime_flags.updated_at + updated_by`).

## Choix non-bricolage explicites (alignement memories)

- **Pas de nouveau workflow CI dédié** drift detection : pipeline `tsx --test` natif suffit. Évite overhead infra.
- **Pas de nouvelle colonne JSONB** sur `__seo_gamme_conseil` pour event log : `__seo_quality_history` partitionnée existe maintenant et est canon. Réutiliser.
- **Pas d'event_log local custom** : RPC `detect_quality_outliers` + métadata JSONB sont canon ADR-050.
- **Pas de polling/until-loop** : usage exclusif checks ponctuels (alignement `feedback_no_long_polling_until_loops`).
- **Pas de re-implémentation pattern PR-T** : réutilise schema + RPCs ratifiés ADR-050.
- **Pas de plan v5 R-stack en parallèle** : focus session sur R3 Canon Phase 2 + R1 backfill (scope tactique). Plan v5 (36 PRs sur 8-10 sem) avancé par autres agents en parallèle (PR-B #362, PR-C #363, PR-E #356, PR-X1 #357 mergées même jour). Mes 9 PRs sont des building blocks anticipés ou bonus.

## Pendant la session

- **Découverte vault** : ADRs 046-050 ratifiées le même jour par d'autres sessions ([[2026-05-07-mvp0-r-stack-shipped]]). Mes contributions canon-aligned.
- **Backend dev session** redémarrage par user nécessaire après rebuild (nodemon ne reprenait pas auto). User a relancé.
- **Test smoke trigger** : 1er test invalide (terme "voyant" est R5 pas R3) — corrigé avec `diagnostiquer` qui EST dans canon R3. Rappel : le canon check fixture sha256 verrouille ce mapping pour éviter futures confusions.

## Suite (hors session)

| Item | Gated sur | Effort |
|---|---|---|
| LLM follow-up R1 backfill (162 slots still-short) | PR #371 mergée + `R1_LLM_FALLBACK_ENABLED` env var + Anthropic SDK in `R1EnricherService` | ~30-40min API + safety net déjà LIVE |
| Migration forbidden-overlap → `@repo/seo-role-contracts` (PR-G1/G2/G3/G4) | Plan v5 Phase 2 PR-F (création package) en cours | non-breaking, séquencé |
| ESLint warn→error promotion `R3_guide` literals | T+7d si `seo_r3_canon_violation_total=0/7d` | délai mécanique |
| Event log JSONB sur `__seo_gamme_conseil` | Recyclable via `__seo_quality_history` (table existe maintenant) | follow-up |

## Liens

- [[2026-05-07-r-stack-audit]] : audit baseline R-stack (référence baseline mes mesures)
- [[2026-05-07-mvp0-r-stack-shipped]] : session parallèle MVP-0 R-stack (Phase 0 + 1 + 3C + amorce 2)
- [[ADR-040-seo-roles-canon-ts-side-only]] : foundation `@repo/seo-roles` (couche 1)
- [[ADR-046-r-stack-single-generator-and-layers]] : R-stack canon (cadre où s'inscrit cette session)
- [[ADR-047-seo-role-contracts-as-code]] : séparation identité/comportement (mandate future migration forbidden-overlap)
- [[ADR-049-db-governance-canon-enforcement]] : pattern DB trigger + cache + kill-switch (couche 4)
- [[ADR-050-quality-history-and-drift-detection]] : pattern PR-T snapshot+abort (PR #371)
