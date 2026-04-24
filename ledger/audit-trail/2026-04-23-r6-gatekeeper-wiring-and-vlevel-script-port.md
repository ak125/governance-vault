---
type: evidence-pack
date: 2026-04-23
owner: Fafa
duration: ~2h
session_id: r6-gatekeeper-wiring-and-vlevel-script-port-20260423
scope: Clôture des 2 follow-ups ouverts dans 2026-04-23-seo-kw-pipeline-cable-frein-main.md — (1) wire BuyingGuideQualityGatesService pour persister sgpg_gatekeeper_*, (2) porter recalculate_vlevel.py (cassé) en script live + backfill des 233 rows R6 NULL
related_files:
  - backend/src/modules/admin/services/buying-guide/buying-guide-quality-gates.service.ts
  - backend/src/modules/admin/services/buying-guide/index.ts
  - backend/src/modules/admin/services/buying-guide-enricher.service.ts
  - backend/src/config/field-catalog.constants.ts
  - scripts/seo/rebuild-type-vlevel.py (nouveau)
  - scripts/seo/recalculate_vlevel.py (supprimé)
  - scripts/seo/backfill-r6-gatekeeper.py (nouveau)
related_prs:
  - ak125/nestjs-remix-monorepo#130 (merged — R6 gatekeeper wiring)
  - ak125/nestjs-remix-monorepo#131 (merged — rebuild-type-vlevel.py canon)
  - ak125/nestjs-remix-monorepo#138 (merged — backfill-r6-gatekeeper.py)
related_canon:
  - ledger/audit-trail/2026-04-23-seo-kw-pipeline-cable-frein-main.md §4 (gap identifié)
  - ledger/audit-trail/2026-04-23-seo-kw-pipeline-cable-frein-main.md §5 (UPSERT canon source)
  - ledger/audit-trail/2026-04-21-pipeline-content-hardening.md §P1.3 (trigger fn_invalidate_sgpg_gatekeeper)
continues_from: 2026-04-23-seo-kw-pipeline-cable-frein-main.md
tags: [pipeline, r6-gatekeeper, vlevel, backfill, canon, symmetry-r1-r6]
---

# R6 gatekeeper wiring + V-Level script canon + backfill 223 rows

## TL;DR

Session de clôture des 2 follow-ups de `2026-04-23-seo-kw-pipeline-cable-frein-main.md` (hors-scope de la QA gamme mais trackés comme dette).

| Follow-up | Avant | Après |
|---|---|---|
| R6 gatekeeper service wired | 0 (235/241 rows `sgpg_gatekeeper_score = NULL`) | **223/241 scored (92.5 %)** |
| Script live `__seo_type_vlevel` ← `__seo_keywords` | `recalculate_vlevel.py` cassé (réfère `__seo_keywords_clean` archivé) | **`rebuild-type-vlevel.py` canon + invalidation Redis stub** |

Les 18 rows restants (7.5 %) sont toutes le cluster "RAG incomplet" déjà identifié dans `2026-04-21-pipeline-content-hardening.md §P0.5.c1` — l'enricher fait `return { updated: false }` avant l'écriture gatekeeper quand aucune section RAG n'est OK. Follow-up séparé.

3 PRs mergées : #130 (code), #131 (script V-Level), #138 (script backfill).

---

## 1 — Task 1 : `BuyingGuideQualityGatesService.computeGatekeeperScore()`

### Contexte

`R1EnricherService` ligne 192-193 persiste `r1s_gatekeeper_score/flags` dans `__seo_r1_gamme_slots`. La colonne équivalente R6 (`sgpg_gatekeeper_score/flags/checks`) existe dans `__seo_gamme_purchase_guide` depuis au moins la migration P1.3 (`2026-04-21-pipeline-content-hardening.md`) mais **aucun service ne l'écrivait**. Le trigger `fn_invalidate_sgpg_gatekeeper` nullait la colonne sur chaque changement de contenu, donc la colonne restait NULL même après enrichissement.

### Design

Symétrie R1 ↔ R6 exacte, avec enrichissement JSON sur `sgpg_gatekeeper_checks` (absent côté R1) :

```typescript
computeGatekeeperScore(input: {
  sectionResults, qualityFlags, qualityScore, antiWikiGate
}): { score: number; flags: string[]; checks: Record<string, unknown> }
```

- `score` = `qualityScore` clamp [0, 100]
- `flags` = union(`qualityFlags`, `antiWikiGate.reasons`) dédupliqué
- `checks` = `{ quality_score, min_threshold, passed, anti_wiki, sections_ok, computed_at }`

### Intégration dans le orchestrator

Dans `BuyingGuideEnricherService.enrichSingle()`, après `buildUpdatePayload` et avant `upsertBuyingGuide`, merge dans le payload :

```typescript
updatePayload.sgpg_gatekeeper_score = gatekeeper.score;
updatePayload.sgpg_gatekeeper_flags = gatekeeper.flags;
updatePayload.sgpg_gatekeeper_checks = gatekeeper.checks;
```

**Invariant crucial** : les 3 colonnes sont écrites dans **le même UPDATE** que les colonnes de contenu. Le trigger `fn_invalidate_sgpg_gatekeeper` utilise `IS NOT DISTINCT FROM OLD` sur `score` + `flags` ; si la valeur diffère (premier write NULL→84, ou changement de score), la branche de nulling est skippée. `checks` suit par transitivité.

### Field catalog

3 entrées R6_GUIDE_ACHAT × `purchase_guide_main` ajoutées symétrie des 3 entrées R1 existantes :

```typescript
{ table: '__seo_gamme_purchase_guide', field: 'sgpg_gatekeeper_score',  ownerRole: R6_GUIDE_ACHAT, writeClass: 'metadata', writeStrategy: 'replace' }
{ table: '__seo_gamme_purchase_guide', field: 'sgpg_gatekeeper_flags',  ownerRole: R6_GUIDE_ACHAT, writeClass: 'metadata', writeStrategy: 'replace' }
{ table: '__seo_gamme_purchase_guide', field: 'sgpg_gatekeeper_checks', ownerRole: R6_GUIDE_ACHAT, writeClass: 'metadata', writeStrategy: 'replace' }
```

Sans ces entrées, `WriteGuardCasService.checkOwnership` aurait silencieusement strippé les champs en mode `enforce`.

### Validation e2e (pg_id=124 `cable-de-frein-a-main`)

```bash
POST /api/internal/buying-guides/enrich {"pgIds":["124"],"dryRun":false}
→ HTTP 201, 4 sections updated
```

Row DB après :
```
sgpg_gatekeeper_score = 84
sgpg_gatekeeper_flags = [ANTI_MISTAKES_NO_ACTION, MISSING_REQUIRED_TERMS,
                         MISSING_ANTI_MISTAKES (got 0, need 4),
                         GUIDANCE_COPIES_LABEL (6/7 criteria …),
                         USE_CASES_NOT_PROFILES]
sgpg_gatekeeper_checks = {
  "passed": false,
  "quality_score": 84,
  "min_threshold": 70,
  "anti_wiki": { "ok": false, "reasons": [...] },
  "sections_ok": { "faq": true, "use_cases": true, "anti_mistakes": false,
                   "decision_tree": true, "how_to_choose": false,
                   "selection_criteria": true },
  "computed_at": "2026-04-23T15:01:22.544Z"
}
```

**PR [ak125/nestjs-remix-monorepo#130](https://github.com/ak125/nestjs-remix-monorepo/pull/130)** — merged `8248d273`.

---

## 2 — Task 2 : `rebuild-type-vlevel.py` canon port

### Diagnostic

`scripts/seo/recalculate_vlevel.py` (existant) lisait `__seo_keywords_clean` → table archivée dans le schéma `_archive` (confirmé via `information_schema.tables.table_schema = '_archive'`). Script cassé depuis archivage, phase 5B de `/gamme-qa` en WARN.

### Design

- **psycopg2 direct port 5432** (même pattern que `scripts/db/adr017-create-index-concurrently.py`) pour éviter le pooler `statement_timeout ≈ 60s`.
- **Canon SQL inliné verbatim** depuis l'audit-trail précédent §5 (DISTINCT ON (pg_id, type_id) avec priorité V2 > V3 > V4 > V5, `confidence = 0.90` si `volume > 0`, `source` CASE dérivée de `v_level`).
- **Pre-check** : counts per v_level + distinct type_ids (dry-run prédit exactement le nombre de rows UPSERT).
- **Post-check** : distribution finale + `avg_confidence` + `newest` + `kw_vehicle_without_vlevel` (orphan count).
- **Redis invalidation** : optional. Skip gracieux si `redis-py` absent OU `REDIS_URL` non défini. Pattern `vlevel:{pg_id}:*` (préventif ; aucun consumer actuel en code).

### Validation live (pg_id=124)

```
Pre-check:  V2=10 V3=26 V4=27 V5=14 (distinct type_ids=48)
UPSERT:     affected rows = 48
Post-check: V2=10 V3=24 V4=0 V5=14 total=48 avg_conf=0.90 orphans=0
```

**Note** : V3 passe de 26 → 24 et V4 passe de 27 → 0 parce que le DISTINCT ON garde la priorité V2 > V3 > V4 > V5 — un type_id ayant à la fois des KW V3 et V4 est classifié V3. Match exact avec l'audit-trail §5 reported result (`48 rows : V2=10 V3=24 V4=0 V5=14`).

**PR [ak125/nestjs-remix-monorepo#131](https://github.com/ak125/nestjs-remix-monorepo/pull/131)** — merged `cc53e649`. Ancien `recalculate_vlevel.py` supprimé (0 live caller, vérifié par grep sur `backend/` + `frontend/` + CI).

---

## 3 — Task 3 : Backfill 223 R6 NULL rows

### Design

`scripts/seo/backfill-r6-gatekeeper.py` — tool one-shot qui :
1. Query `__seo_gamme_purchase_guide WHERE sgpg_gatekeeper_score IS NULL` via psycopg2
2. POST `/api/internal/buying-guides/enrich` par pg_id, rate-limit `--sleep` (2s default)
3. Re-lit le score post-call pour validation
4. **Resume-safe** : chaque itération ré-interroge la NULL list (interruption = reprise propre)

### Rollout tiered

| Phase | Scope | Résultat |
|---|---|---|
| Dry-run `--limit 5` | list-only | 233 NULL confirmés, 5 affichés |
| Test batch `--limit 10` | 10 pg_ids | 10/10 OK, 10/10 now_scored, 0 err |
| Full run | 223 pg_ids restants | 205 OK, 18 FAIL (all_sections_skipped) |

Duration full : 9m 18s (2.5s/iteration moyenne).

### État DB final

| Métrique | Valeur |
|---|---|
| Total rows `__seo_gamme_purchase_guide` | 241 |
| `sgpg_gatekeeper_score IS NOT NULL` | **223 (92.5 %)** |
| `sgpg_gatekeeper_score IS NULL` | 18 (7.5 %) |
| Score ≥ 70 (pass) | 222/223 (99.6 %) |
| Score = 100 | 90/223 (40.4 %) |
| Score min / avg / max | 60 / 90.1 / 100 |

### Cluster des 18 rows restants (cause racine connue)

```
pg_ids: 26, 76, 141, 158, 170, 249, 259, 291, 292, 293, 294,
        789, 807, 1362, 1365, 1375, 1787, 3220
```

Pattern uniforme : **"all sections skipped"** à cause du RAG incomplet. Dans `BuyingGuideEnricherService.enrichSingle()` :

```typescript
if (okSections.length === 0) {
  return { updated: false, sectionsUpdated: 0, skippedSections: [...] };
  // ← early return AVANT écriture gatekeeper
}
```

Ces gammes sont déjà identifiées dans `2026-04-21-pipeline-content-hardening.md §P0.5.c1` comme "RAG incomplets" et attendent soit :
- un fix RAG `.md` (injection des sections manquantes)
- soit un ajustement de l'enricher pour écrire un gatekeeper minimal `{ score: 0, flags: ['ALL_SECTIONS_SKIPPED'] }` même en early-return (signal explicite meilleur que NULL)

**PR [ak125/nestjs-remix-monorepo#138](https://github.com/ak125/nestjs-remix-monorepo/pull/138)** — merged `80e3c3d8`. Le script reste dans `scripts/seo/` comme outil canon pour future regression du trigger gate.

---

## 4 — Incidents opérationnels (contexte, non bloquants)

### 4.1 Auto-switches de branche non sollicités

**Symptôme** : pendant 2 commits consécutifs, le HEAD a été déplacé entre `git switch -c <branch>` et `git commit`. Reflog :

```
HEAD@{2}: checkout: moving from fix/rebuild-type-vlevel-script to refactor/r8-vehicle-route-split
HEAD@{1}: checkout: moving from refactor/r8-vehicle-route-split to refactor/r8-vehicle-sections-phase2
HEAD@{0}: commit: fix(seo): port recalculate_vlevel.py ...
```

Résultat : le commit a atterri sur la mauvaise branche (orphan local `refactor/r8-vehicle-sections-phase2`).

**Rescue** :
- Cherry-pick du commit vers la bonne branche
- `git branch -f <orphan> <previous-head>` pour restaurer l'orphan à son état attendu
- Aucune contamination côté remote (rien n'était pushé)

**Origine probable** : autre session Claude Code active en parallèle (l'utilisateur avait mentionné des `/loop` / background tasks), ou extension IDE qui fait des checkouts. À investiguer si récurrent.

### 4.2 GitHub 500 transient pendant push + CI

- 1 × HTTP 500 pendant `git push` (retry à +3s → OK)
- 1 × `🧪 Backend Tests` FAIL sur PR #138 cause `git clone` HTTP 500 côté runner GitHub — **pas** mon code. Merge autorisé malgré UNSTABLE.

Aucune corrélation avec le contenu des PRs. Monitoring status.github.com recommandé pour la même journée.

---

## 5 — Final state matrix

| Livrable | Statut | Commit / SHA |
|---|---|---|
| R6 gatekeeper wiring (code) | MERGED | `8248d273` PR #130 |
| `rebuild-type-vlevel.py` | MERGED | `cc53e649` PR #131 |
| `backfill-r6-gatekeeper.py` | MERGED | `80e3c3d8` PR #138 |
| Task 1 e2e validation (pg_id=124) | PASS | score=84, flags=5, checks JSON valid |
| Task 2 live validation (pg_id=124) | PASS | 48 rows, 0 orphans |
| Task 3 backfill full | PASS | 223/241 scored (92.5%) |
| DEV pré-prod deploy | Auto-triggered | `.github/workflows/ci.yml` |

---

## 6 — Rollback procedures

### Undo Task 1 (R6 gatekeeper wiring)

```bash
git revert 8248d273  # PR #130 squash
git push origin main
# Les colonnes existantes restent en DB (non destructif) ; elles ne seront simplement plus écrites par l'enricher.
# Pour purger les scores déjà écrits :
# UPDATE __seo_gamme_purchase_guide SET sgpg_gatekeeper_score = NULL,
#   sgpg_gatekeeper_flags = NULL, sgpg_gatekeeper_checks = NULL;
```

### Undo Task 2 (rebuild-type-vlevel.py)

```bash
git revert cc53e649
# Restaure recalculate_vlevel.py (cassé) et supprime rebuild-type-vlevel.py
# Les 48 rows UPSERT dans __seo_type_vlevel pour pg_id=124 restent (non destructif)
```

### Undo Task 3 (backfill script)

```bash
git revert 80e3c3d8  # supprime le script
# Pour purger les scores backfillés :
# UPDATE __seo_gamme_purchase_guide SET sgpg_gatekeeper_score = NULL,
#   sgpg_gatekeeper_flags = NULL, sgpg_gatekeeper_checks = NULL
# WHERE sgpg_source_verified_at >= '2026-04-23 16:39:00';  # ou par pg_id list
```

---

## 7 — Follow-ups

1. **18 rows "RAG incomplet"** — décider : fix RAG `.md` individuel OU patch enricher pour écrire gatekeeper minimal en early-return. Issue à créer.
2. **Investigate auto-switches** — si récurrents sur prochaines sessions, chercher processus externe (autres Claude sessions concurrentes, hooks VS Code, git-sync).
3. **Redis cache `vlevel:*` consumer** — actuellement 0 lecteur de cache ; le stub d'invalidation dans `rebuild-type-vlevel.py` est prêt le jour où un cache sera câblé.
4. **Symmetry audit** — audit systématique : pour chaque R* ayant un champ `*_gatekeeper_*`, vérifier qu'un service persiste le verdict. `grep -rn "_gatekeeper_score\b" backend/src/modules/admin/services/` (règle mentionnée dans §7 du cable-frein-main audit).

---

## 8 — Coverage manifest

```
scope_requested:       2 follow-ups ouverts dans 2026-04-23-seo-kw-pipeline-cable-frein-main.md
scope_actually_scanned:
  - R6 gatekeeper service wiring (3 fichiers TS + 1 field catalog)
  - V-Level script live (nouveau script + suppression ancien)
  - Backfill 223 R6 NULL rows (nouveau script + run live)

files_read_count:      ~20 fichiers (enricher, db-service, quality-gates, field-catalog,
                       internal-enrich controller, migrations gatekeeper, audit-trail ref,
                       old recalculate_vlevel.py, rebuild scripts)
excluded_paths:        autres rôles R1/R3/R4/R5/R7/R8 (hors scope task 1)
unscanned_zones:       autres gammes en état "RAG incomplet" non listées ici

corrections_proposed:
  - Wiring R6 gatekeeper
  - Port rebuild-type-vlevel.py
  - Backfill 223 rows
  - Field catalog 3 entries R6 gatekeeper

corrections_applied:
  - PR #130 merged (4 files, +96 / -1)
  - PR #131 merged (1 new script, 1 deleted, +263 / -242)
  - PR #138 merged (1 new script, +209)
  - UPSERT live __seo_type_vlevel pg_id=124 (48 rows)
  - Backfill enrich POST × 223 (205 ok, 18 all-skipped)

validation_executed:
  - tsc --noEmit EXIT=0 pre-PR
  - PR #130/#131 CI: all blocking gates SUCCESS (2 known infra flakes UNSTABLE non-bloquant)
  - PR #138 CI: Backend Tests FAIL = GitHub infra HTTP 500 (pas mon code)
  - Task 1 e2e: POST enrich pg_id=124 → 3 colonnes DB peuplées (vérif SQL direct)
  - Task 2 live: 48 rows UPSERT vs audit-trail expected 48 ✓
  - Task 3 backfill: 223/241 scored (92.5%), 99.6% PASS threshold

remaining_unknowns:
  - Origine exacte des auto-switches de branches (pas critique, rescue manuel efficace)
  - Sortie définitive des 18 rows "RAG incomplet" (décision produit nécessaire)

final_status: SCOPE_SCANNED
```

---

_Generated 2026-04-23 by Claude Code session. SoT: governance-vault `/opt/automecanik/governance-vault/ledger/audit-trail/`._
