---
type: evidence-pack
date: 2026-04-25
owner: Fafa
duration: ~30min
session_id: r1-gatekeeper-symmetry-backfill-20260425
scope: Closure du follow-up #4 (symmetry audit) de 2026-04-23-r6-gatekeeper-wiring-and-vlevel-script-port.md — auditer chaque rôle R* portant des colonnes `*_gatekeeper_*`, vérifier la couverture, backfiller R1 si nécessaire
related_files:
  - scripts/seo/backfill-r1-gatekeeper.py (nouveau)
  - backend/src/modules/admin/services/r1-enricher.service.ts (writer existant ligne 192-193, non modifié)
related_prs:
  - ak125/nestjs-remix-monorepo#178 (merged — backfill-r1-gatekeeper.py)
  - ak125/nestjs-remix-monorepo#177 (closed — superseded, branche borked auto-switch)
related_canon:
  - ledger/audit-trail/2026-04-23-r6-gatekeeper-wiring-and-vlevel-script-port.md §7 #4 (follow-up symmetry audit)
continues_from: 2026-04-23-r6-gatekeeper-wiring-and-vlevel-script-port.md
tags: [r1-gatekeeper, r6-gatekeeper, symmetry-audit, backfill, canon]
---

# R1 gatekeeper symmetry audit + backfill — closure follow-up §7 #4

## TL;DR

Symmetry audit complété : 2 paires de colonnes `*_gatekeeper_*` existent en DB, **les 2 ont un writer**. Découverte : R1 avait 48/169 rows NULL (28.4 %) — non pas par absence de writer, mais parce que les rows seedées au split de table 2026-03-17 n'avaient jamais été ré-enrichies. Backfill exécuté → **R1 désormais 100 % scored (169/169)**. R6 reste à 92.5 % (cluster RAG-incomplet documenté §7 #1).

| Rôle | Avant | Après | Coverage |
|---|---|---|---|
| R1_ROUTER (`__seo_r1_gamme_slots`) | 121/169 | **169/169** | **100 %** ✅ |
| R6_GUIDE_ACHAT (`__seo_gamme_purchase_guide`) | 223/241 | 223/241 (inchangé) | 92.5 % |

---

## 1 — Symmetry audit (méthode)

### Inventaire DB

```sql
SELECT table_name, column_name
FROM information_schema.columns
WHERE column_name LIKE '%_gatekeeper_%' AND table_schema = 'public'
ORDER BY table_name, column_name;
```

Résultat : **2 tables, 6 colonnes** (3 par table) :

| Table | Colonnes | Owner |
|---|---|---|
| `__seo_r1_gamme_slots` | `r1s_gatekeeper_score/flags/checks` | R1_ROUTER |
| `__seo_gamme_purchase_guide` | `sgpg_gatekeeper_score/flags/checks` | R6_GUIDE_ACHAT |

Aucun autre rôle (R2/R3/R4/R5/R7/R8) n'a de colonnes `*_gatekeeper_*`. La symétrie binaire R1↔R6 est donc complète à inspecter.

### Inventaire writers code

```bash
grep -rn "_gatekeeper_score\b" backend/src/modules/admin/services/ | grep "= "
```

| Service | Writer location | Mode |
|---|---|---|
| `R1EnricherService` | `r1-enricher.service.ts:192-193` | direct mutation `slots.r1s_gatekeeper_*` |
| `BuyingGuideEnricherService` | `buying-guide-enricher.service.ts:265-267` | merge dans `updatePayload` |

**Conclusion intermédiaire** : les 2 writers sont en place. Asymétrie de couverture DB ≠ asymétrie de code.

### Inventaire couverture DB

R1 : **121/169 scored (71.6 %), 48 NULL**, tous live (0 orphan vs `pieces_gamme`), tous `r1s_updated_at = 2026-03-17 20:44:03` — date du split de la table.

Diagnostic : ces 48 rows ont été *seedées* au moment du split `__seo_gamme_purchase_guide` → `__seo_r1_gamme_slots` (cf. migration `20260322_create_r1_gamme_slots.sql`) mais n'ont jamais été ré-enrichies depuis. `R1EnricherService.enrichSingle()` n'a simplement jamais run sur ces pg_ids.

---

## 2 — Backfill R1 (livrable)

### `scripts/seo/backfill-r1-gatekeeper.py` (PR #178, merged `0d9f751f`)

Symétrique strict de `scripts/seo/backfill-r6-gatekeeper.py` :

| Aspect | R6 backfill | R1 backfill |
|---|---|---|
| Endpoint | `POST /api/internal/buying-guides/enrich` | `POST /api/internal/pipeline/execute` (roleId=R1_ROUTER) |
| DB connection | psycopg2 direct port 5432 | identique |
| Resume-safe | re-query NULL list par itération | identique |
| Idempotent | merge logic + `IS DISTINCT FROM OLD` trigger | direct write (pas de trigger côté R1) |
| Health check | pre-flight `/health` | identique |
| Connection-refused recovery | retry idempotent (rerun script) | identique |

### Validation live (DEV DB)

```
pre-check  : 48 rows NULL (out of 169 total)
test batch : --limit 5  → 5/5 OK, 5/5 now_scored, 0 error
full run   : 38/42 OK first pass, 4 connection-refused (nodemon mid-run)
retry      : 4/4 OK
final      : 169/169 scored (100%), 0 NULL
```

Score distribution : **avg=83.2**, toutes les rows backfillées scorent 80 avec flag unique `FEW_BUY_ARGS` — pattern attendu (RAG `.md` qui ont ≥ 1 `buy_arg` mais < 2, seuil `score -= 10` dans `r1-enricher.service.ts:184-187`).

---

## 3 — Asymétrie résiduelle R6 (hors scope)

R6 conserve 18 rows NULL (= 7.5 % de 241). Cluster identifié dans `2026-04-23-r6-gatekeeper-wiring-and-vlevel-script-port.md §3` :

```
pg_ids: 26, 76, 141, 158, 170, 249, 259, 291, 292, 293, 294,
        789, 807, 1362, 1365, 1375, 1787, 3220
```

Cause racine : `BuyingGuideEnricherService.enrichSingle()` fait `return { updated: false }` quand `okSections.length === 0` (toutes les sections sautées par anti-wiki ou anti-dup) **avant** l'écriture du gatekeeper. Ces 18 rows ont des `.md` RAG incomplets (clusters identifiés dans `2026-04-21-pipeline-content-hardening.md §P0.5.c1`).

R1 ne souffre pas du même symptôme parce que `R1EnricherService` écrit le score *même si peu de slots sont peuplés* — le score est calculé sur la base de présence/absence de chaque champ (`microSeo`, `faq`, `buyArgs`, etc.) sans early-return.

**Décision produit pendante** (suivi #1 de §7 du précédent audit) : fix RAG `.md` individuels OR patch enricher R6 pour écrire `{score: 0, flags: ['ALL_SECTIONS_SKIPPED']}` même en early-return. Hors scope de cette session.

---

## 4 — Final state matrix

| Livrable | Statut | SHA |
|---|---|---|
| Script `backfill-r1-gatekeeper.py` | merged | `0d9f751f` (PR #178) |
| PR #177 (borked branch) | closed superseded | — |
| R1 backfill live execution | DONE | 169/169 scored |
| R6 backfill live execution (rappel) | DONE 2026-04-23 | 223/241 scored |
| Symmetry audit follow-up §7 #4 | **CLOSED** | — |
| 18 R6 NULL cluster follow-up §7 #1 | OPEN (decision produit) | — |

---

## 5 — Incidents opérationnels (non bloquants)

### 5.1 Auto-switches de branche persistants

Pendant le commit du script R1, le HEAD a été déplacé d'`chore/backfill-r1-gatekeeper` vers `feat/vehicle-rag-web-enrichment-stage1` (active dans une autre session) avant l'écriture du commit. Résultat : commit atterri sur la mauvaise branche, embarquant 10 commits unrelated lors du push.

**Rescue** :
- Reset du commit orphelin sur la mauvaise branche
- Worktree fresh créé sur `origin/main` pour rebuilder un commit propre linéaire
- Force-push **refusé** par la safety policy (correct, non sollicité par utilisateur)
- Solution : push d'une nouvelle branche `chore/backfill-r1-gatekeeper-clean` + close PR #177 + open clean PR #178

Ce pattern récurrent (4 incidents observés sur 2 sessions consécutives) reste à investiguer (suivi #2 du précédent audit). Hypothèse : autre session Claude active concurrente ou hook IDE.

### 5.2 Backend connection-refused mid-backfill

4/42 calls ont retourné `Errno 111 Connection refused` — backend nodemon redémarrait pendant la session. Recovery automatique via re-run du script (resume-safe). Aucune perte de données, idempotent confirmé.

---

## 6 — Coverage manifest

```
scope_requested:       follow-up §7 #4 du précédent audit (symmetry audit gatekeeper)
scope_actually_scanned:
  - inventaire DB (information_schema.columns LIKE %_gatekeeper_%)
  - inventaire writers code (grep backend/src/modules/admin/services)
  - couverture DB R1 + R6 par pg_id
  - backfill R1 (live, 48 → 0 NULL)

files_read_count:      ~10 fichiers (r1-enricher, buying-guide-enricher, execution-router,
                       internal-pipeline.controller, backfill-r6-gatekeeper.py, audit-trail ref)
excluded_paths:        autres rôles R2/R3/R4/R5/R7/R8 (vérifié 0 colonne gatekeeper donc OOSCOPE)
unscanned_zones:       18 R6 NULL cluster (suivi #1 précédent audit, decision produit pendante)

corrections_proposed:
  - Backfill R1 via nouveau script symétrique R6
  - Closure §7 #4

corrections_applied:
  - PR #178 merged (1 nouveau script, +226 lignes)
  - 48 R1 rows backfillées (NULL → scored)

validation_executed:
  - tsc --noEmit (n/a, script Python pas de TS)
  - test batch 5 rows OK
  - full run 42 rows : 38 OK first pass + 4 retry idempotent → 100%
  - DB cross-check post-backfill : 0 NULL R1

remaining_unknowns:
  - 18 R6 NULL cluster — décision produit attendue
  - Cause exacte des auto-switches inter-sessions

final_status: SCOPE_SCANNED
```

---

_Generated 2026-04-25 by Claude Code session. SoT: governance-vault `/opt/automecanik/governance-vault/ledger/audit-trail/`._
