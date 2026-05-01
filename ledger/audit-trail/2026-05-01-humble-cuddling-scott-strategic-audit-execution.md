---
type: evidence-pack
date: 2026-05-01
owner: Fafa
duration: ~6h
session_id: humble-cuddling-scott-strategic-audit-execution
scope: vérification d'un audit stratégique externe (4 blocs) + exécution Sprints 1-3 + 6 principes architecturaux
related_repos:
  - nestjs-remix-monorepo
  - automecanik-wiki
  - automecanik-raw
related_prs:
  - automecanik-wiki#11 (P-pré statuts CLAUDE.md + double verrou)
  - automecanik-raw#7 (P0 manifests dérivés + manifest_id content-addressable)
  - automecanik-raw#8 (P1 _scripts/gates.py AEC runner, stacked)
  - automecanik-wiki#12 (P5 confidence drift gate)
  - nestjs-remix-monorepo#259 (P3 diag-canon flat map + composite FK)
related_adr:
  - ADR-031 (raw/wiki/exports/consumers)
  - ADR-033 (wiki gamme diagnostic_relations contract)
  - ADR-039 (wiki frontmatter Zod canon)
plan_internal: /home/deploy/.claude/plans/humble-cuddling-scott.md
tags:
  - strategic-audit
  - schema-first
  - content-addressing
  - pre-commit-primary
  - manifest-id
  - aec-runner
  - sprint-execution
final_status: PARTIAL_COVERAGE
---

# Audit stratégique externe — vérification + exécution Sprints 1-3

> **Session scope** : un audit stratégique externe a été produit le 2026-05-01
> couvrant 4 blocs (`nestjs-remix-monorepo`, `governance-vault`,
> `automecanik-raw`, `automecanik-wiki`). Ce document consigne (1) la
> vérification claim-par-claim de l'audit contre les fichiers réels, (2) les
> 6 principes architecturaux introduits, (3) les livraisons Sprints 1-3,
> (4) ce qui reste en Sprint 4.

## TL;DR

Audit externe **majoritairement juste**, avec **1 erreur factuelle** (claim asymétrie symptom/system, à nuancer) et **1 omission grave** (manifests `automecanik-raw` quasi-vides, pas seulement non-enforced).

Plutôt que patcher chaque trou identifié, 6 principes architecturaux unifiés ont été dégagés et appliqués transversalement. **Sprints 1-3 livrés en 5 PRs**, Sprint 4 pendant.

## Vérification claim-par-claim (19 claims + 1 ajout post-revue)

### Bloc monorepo

| # | Claim auditeur | Verdict | Évidence |
|---|---|---|---|
| 1 | OperatingMatrixService existe + scan agents + boot invariant | ✅ CONFIRMÉ | `backend/src/config/operating-matrix.service.ts` (689 L) |
| 2 | EXECUTION_REGISTRY dérive `writeScope` de FIELD_CATALOG | ✅ CONFIRMÉ | `execution-registry.constants.ts:190-192` |
| 3 | FIELD_CATALOG field-by-field structure | ✅ CONFIRMÉ | `field-catalog.constants.ts` (1351 L) |
| 4 | WriteGuardModule expose 7 services + boot invariant | ✅ CONFIRMÉ | `write-guard.module.ts:44-66` |
| 5 | **Asymétrie symptom_slug FK / system_slug free** | ⚠️ PARTIELLEMENT CONFIRMÉ | 2 validateurs distincts : wiki `quality-gates.py` (symétrique présence-only) + monorepo `validate-gamme-diagnostic-relations.py` (symptom FK strict, system pas validé). Ni l'un ni l'autre ne valide la cohérence FK composite. Audit avait raison sur le validateur monorepo seulement. |

### Bloc wiki

| # | Claim | Verdict | Évidence |
|---|---|---|---|
| 6 | `frontmatter.schema.json` impose 11 fields + diagnostic_relations[] top-level | ✅ CONFIRMÉ | `_meta/schema/frontmatter.schema.json:7-18,226-307` |
| 7 | review_status enum = draft\|proposed\|in_review\|approved\|deprecated | ✅ CONFIRMÉ | `:169` exact |
| 8 | **CLAUDE.md utilise needs_human_review/human_reviewed/status:validated hors enum** | ✅ CONFIRMÉ | `CLAUDE.md:40,52-56` — incohérence réelle |
| 9 | `quality-gates.py` 16 gates implémentés | ✅ CONFIRMÉ | `_scripts/quality-gates.py:run_gates() L437-450` |
| 10 | source-catalog `to_capture` (4 sources brake_*) | ✅ CONFIRMÉ | `_meta/source-catalog.yaml:34-89` |
| 11 | plaquette-de-frein.md `confidence_score_computed: 1.0` | ✅ CONFIRMÉ structurellement, mais **anomalie SÉMANTIQUE pas arithmétique** : la formule ADR-033 §C8 donne mathématiquement 1.0 pour 2 sources `oem_workshop`+`brochure`. Lecture sur `reviewed: false / diagnostic_safe: false` reste trompeuse. |
| 12 | Pas de validateur cross-check symptom↔system | ✅ CONFIRMÉ | Schema L235 délègue explicitement à Phase 2 ADR-033 |
| 12bis | `wiki-readiness-check.py` PR-F #253 (post-revue, omis par audit) | ✅ AJOUT | Critère C3 : freshness `diag-canon-slugs.json` < 7j |

### Bloc vault

| # | Claim | Verdict | Évidence |
|---|---|---|---|
| 13 | "Vault n'est pas le canon technique" | ⚠️ NUANCÉ | Distinction de scope : `.spec/00-canon/` = canon architectural, vault = canon opérationnel (incidents, ADRs, rules). Pas une contradiction. ADR-015. |
| 14 | `check-orphans.sh` strip code, regex wikilinks, exit 1 | ✅ CONFIRMÉ | `_scripts/check-orphans.sh:88-149` |
| 15 | ADR-033 sépare système/symptôme/cause/pièce + 3 anti-patterns interdits | ✅ CONFIRMÉ | `ADR-033...md:94-99,105-123,161-169` |
| 16 | **Aucun gate ne vérifie archived_at→raw existence** | ✅ CONFIRMÉ — GAP RÉEL | `quality-gates.py` gates #3+#10 = WARN seulement |

### Bloc raw

| # | Claim | Verdict | Évidence |
|---|---|---|---|
| 17 | Structure sources/recycled/normalized/quarantine | ✅ CONFIRMÉ | sources/(6) recycled/(2816) normalized/(.gitkeep) quarantine/(empty) |
| 18 | Contrat clair (CLAUDE.md, raw-contract.md, retention 90j) | ✅ CONFIRMÉ | docs canon présents |
| 19 | **Enforcement faible** | ✅ CONFIRMÉ — PIRE QUE DIT | Manifests **quasi-vides** : `source-inventory.csv` 1 ligne header (0/2822), `checksums.json` files:{}, `lineage-map.json` empty. Workflow CI existait mais ne pouvait rien bloquer. |

## Erreurs / omissions de l'auditeur (à corriger)

### E1. Claim #5 — asymétrie symptom/system

L'auditeur affirmait "validation FK stricte porte surtout sur symptom_slug et source_slug ; je ne vois pas de vérification réelle de system_slug". Mon premier verdict (REFUTÉ) était trop catégorique — il ne regardait que le validateur wiki. Verdict corrigé : ⚠️ PARTIELLEMENT CONFIRMÉ après examen des **deux** validateurs distincts (wiki + monorepo).

### E2. Claim #13 — vault mirror vs SoT

Auditeur présente "vault = miroir" comme un point unique. Réalité : distinction de scope documentée dans ADR-015. `.spec/00-canon/` = canon architectural ; vault = canon opérationnel. Pas une contradiction.

### E3. Omission grave — manifests raw vides

Auditeur dit "raw a un bon contrat, enforcement faible". Réel : manifests **non-renseignés**, pas seulement non-enforced. C'est plus grave (régression silencieuse G2 Zero Orphelin).

## 6 Principes architecturaux unifiés (post-feedback "pas de bricolage")

L'utilisateur a refusé l'approche "patcher chaque trou" et demandé "la stratégie la plus robuste et la plus moderne". 6 principes ont été dégagés et appliqués transversalement :

| # | Principe | Conséquence concrète |
|---|---|---|
| 1 | Schema canonique = source unique | JSON Schema partout. Validateurs (Python, TS) **générés** depuis le schema, pas écrits à la main. ADR-039 fait déjà ça pour le frontmatter wiki. |
| 2 | Manifests = artefacts dérivés | Toute donnée inférable du filesystem (inventory, checksums) est une projection déterministe régénérée par hook. Jamais éditée à la main. |
| 3 | Cross-repo via content-addressing | Wiki ne référence plus raw par filesystem path mais par `manifest_id` stable + `expected_sha256`. Renames safe. |
| 4 | Pre-commit > CI | Gates locaux primaires, CI = filet. Catch fail-fast avant push. |
| 5 | Champs dérivés = readonly + drift detection | `confidence_score_computed`, `checksum`, `inventory.added_at` sont calculés. Hand-edit interdit. |
| 6 | Runner AEC unifié par repo | `_scripts/gates.py --all` orchestre tous les gates et émet sortie AEC standard. 1 source, 2 entrées (pre-commit + CI). |

## Sprints livrés

### Sprint 1 — hardening intra-repo

**Wiki PR #11** (`feat/p-pre-claude-md-statuses-double-lock`) — P-pré
- Correction CLAUDE.md + hot.md + _meta/quality-gates.md + _meta/ingestion-contract.md (3 statuts legacy → enum schema canon)
- Verrou primaire : `validate-frontmatter.py` (déjà câblé) rejette tout `review_status` hors enum à la source
- Verrou secondaire : nouveau hook `forbid-non-schema-statuses-in-docs` avec regex assignment-only (anti-régression docs)
- CI verte
- **Principes 1, 4**

**Raw PR #7** (`feat/p0-derived-manifests-content-addressing`) — P0
- `_schemas/raw-manifests.schema.json` (JSON Schema 2020-12) — contrat formel inventory + checksums + lineage
- `_scripts/regen-manifests.py` — scan déterministe sources/+recycled/, modes `--check` (idempotent) + `--fix`. _updated_at préservé tant que contenu inchangé
- 6 sidecars `.manifest.yaml` pour les sources/ — 0 `unstable_id: true` au bootstrap
- 4334 fichiers indexés (4334 checksums, 4210 manifest_ids — 124 partagent un content_hash, légitime)
- Stratégie `manifest_id` : `rec-<doc_id>` (UUIDv5 existant) | `rec-h-<sha16>` | `src-<slug>` | fallback `path-<sha16>` + `unstable_id: true` (deadline J+30)
- CI verte (a nécessité fix `lfs: true` dans 2 workflows car 1162 fichiers LFS)
- **Principes 1, 2, 4**

### Sprint 2 — gates schema-driven + drift detection

**Raw PR #8** (`feat/p1-gates-aec-runner`, stacked sur #7) — P1
- `_schemas/recycled-frontmatter.schema.json` (descriptive de l'état réel, pas aspirationnel)
- `_scripts/gates.py --all` AEC runner : Gate A (recycled frontmatter via `jsonschema` lib), Gate B (manifests drift, délégué à `regen-manifests --check`), Gate D (quarantine 90j). Gate E (gitleaks) délégué au pre-commit existant
- Sortie AEC standard JSON (verdict / blocked_reasons / coverage_manifest / final_status)
- Exemptions documentées avec deadline : `*.prompt.md` (897 image-prompt files schema différent → Gate F futur), `recycled/rag-knowledge/web/` (1725 fichiers legacy frontmatter incomplet/indenté pré-2026-05)
- État actuel : SCOPE_SCANNED, 4528 files scannés, 0 blocked_reasons (194 strict-validés en `web-catalog/`+`web-vehicles/`)
- CI verte
- **Principes 1, 6**

**Wiki PR #12** (`feat/p5-confidence-drift-gate`) — P5
- Hook `wiki-symptom-confidence` câblé : `compute-symptom-confidence.py --check` (script existait déjà avec `--check`/`--fix` idempotent)
- Champ `confidence_score_computed` marqué `readOnly: true` + description explicite hand-edit interdit
- Découverte intéressante : l'« anomalie 1.0 » audit est **mathématiquement correcte** par formule ADR-033 §C8. Sweep --check sur tout le repo : 1/1 fiches PASS
- CI verte
- **Principes 4, 5, 6**

### Sprint 3 — diag canon FK composite

**Monorepo PR #259** (`feat/p3-diag-canon-flat-map-composite-fk`) — P3
- `scripts/wiki/export-diag-canon-slugs.py` étendu : nouveau mode `--output-dir` émet 3 artefacts atomiquement (legacy array + flat map + JSON Schema)
- `scripts/wiki/validate-gamme-diagnostic-relations.py` étendu :
  - `load_canon()` préfère `diag-canon.json` (flat map P3), fallback transition `diag-canon-slugs.json`, **fail-fast** si aucun (drop FALLBACK_CANON_SYMPTOM_SLUGS hardcoded — bricolage éliminé)
  - 4 nouveaux blocked_reasons : `system_slug_unknown`, `symptom_system_mismatch`, `canon_export_missing`, etc.
  - Composite FK : émet `symptom_system_mismatch` ssi les 2 slugs sont individuellement canon (anti double-noise)
- `.github/workflows/diag-canon-slugs-export.yml` switch vers `--output-dir`, diff loop sur 3 fichiers
- **Le cron PR-D existant a été déclenché manuellement** avant cette PR pour seeder `automecanik-wiki/exports/diag-canon-slugs.json` (sans ça, fail-fast aurait cassé CI immédiatement)
- Validator sur wiki main réel : 10/10 PASS via transition fallback
- Composite FK violation testée : `symptom_system_mismatch:brake_noise_metallic:filtration:freinage` détecté correctement
- **Principes 1, 6**

## Sprint 4 — pendant

**P2 — Cross-repo content-addressing** : migration `automecanik-wiki/_meta/source-catalog.yaml` de `archived_at: <path>` vers `raw_ref: { repo, manifest_id, expected_sha256 }`. Dépend du **merge de raw PR #7** (qui définit la stratégie `manifest_id`). Règle de transition 30j codifiée dans le plan : ✅ raw_ref seul, ⚠️ archived_at seul (WARN avec deadline), ❌ les deux divergents (FAIL `dual_ref_divergence`).

## Tests / vérifications exécutés

- ✅ Verrous schema-driven testés sur cas positif + négatif (P-pré, P5)
- ✅ Idempotence `regen-manifests.py --check` × 3 consécutifs : 0 byte diff (P0)
- ✅ Format flat checksums.json compat workflow CI existant (P0)
- ✅ Gates runner sortie JSON AEC valide (P1)
- ✅ Composite FK violation réelle détectée (P3)
- ✅ Fail-fast sans canon : exit 2 + message clair (P3)
- ✅ Validator P3 sur wiki main réel : 10/10 PASS via transition fallback
- ⏸️ CI runs encore en cours sur PR #259 (Sprint 3) au moment de la consignation

## Coverage Manifest (AEC v1.0.0)

```yaml
scope_requested: vérifier audit stratégique externe + exécuter principes architecturaux
scope_actually_scanned:
  - 4 blocs scannés via Explore agents parallèles
  - 19 claims + 1 ajout post-revue verifiés statiquement
  - 5 PRs livrées (3 repos)
  - 4 sprints planifiés, 3 livrés
files_modified_count:
  monorepo: 3 (export-diag-canon-slugs.py, validate-gamme-diagnostic-relations.py, .github/workflows/diag-canon-slugs-export.yml)
  wiki: 7 (CLAUDE.md, hot.md, _meta/quality-gates.md, _meta/ingestion-contract.md, .pre-commit-config.yaml, _meta/schema/frontmatter.schema.json, _scripts/forbid-non-schema-statuses.sh)
  raw: 12 (3 manifests, _schemas/raw-manifests.schema.json, _schemas/recycled-frontmatter.schema.json, _scripts/regen-manifests.py, _scripts/gates.py, .pre-commit-config.yaml, .github/workflows/raw-checksum-verify.yml + lint.yml, 6 sidecars sources/.manifest.yaml)
files_read_count: ~30 (validators, schemas, ADRs, manifests, samples)
excluded_paths:
  - backend/dist/
  - .worktrees/
  - node_modules/
unscanned_zones:
  - PRs récentes #239-#256 individuellement (références titre uniquement, pas diffs)
  - Tests automatisés Python (pas exécutés en CI ici)
  - Logs runs CI antérieurs (non consultés)
corrections_proposed: 5 (P-pré, P0, P1, P5, P3)
corrections_applied: 5 + 1 dépendance déclenchée (cron manuel)
validation_executed:
  - Lectures statiques exhaustives (Read + git show)
  - 4 PRs CI passées (#11, #7, #8, #12) — #259 en cours
  - Aucun script d'agent IA exécuté sans validation humaine
remaining_unknowns:
  - Sprint 4 P2 cross-repo migration (pendant — dépend du merge des PRs Sprint 1-2-3)
  - Cron PR-D nightly run effectivement émettra 3 fichiers post-merge P3
  - Vault canon-hashes.json drift detection sur diag-canon.json (vault PR follow-up)
final_status: PARTIAL_COVERAGE — verdict 19/19 claims couverts statiquement + 5 PRs livrées + Sprint 4 pendant
```

## Référence

- Plan interne : `/home/deploy/.claude/plans/humble-cuddling-scott.md`
- Audit externe : message utilisateur 2026-05-01 (intégral dans plan §1)
- ADR-031 (raw/wiki/exports/consumers) — vault `ledger/decisions/adr/`
- ADR-033 (wiki gamme diagnostic_relations contract) — vault
- ADR-039 (wiki frontmatter Zod canon) — vault
- `rules-agent-exit-contract.md` v1.0.0 — vault `ledger/rules/`
- Mémoires user-side liées (hors vault, `~/.claude/projects/-opt-automecanik-app/memory/`) :
  `feedback_no_hybrid_workarounds.md`, `feedback_deprecate_before_rename_before_drop.md`,
  `feedback_branch_scope_discipline.md`
