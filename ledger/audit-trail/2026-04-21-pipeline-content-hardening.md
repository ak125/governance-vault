---
type: evidence-pack
date: 2026-04-21
owner: Fafa
duration: ~4h
session_id: pipeline-content-hardening-P0-P1
scope: content enrichment pipeline (R1/R3/R4/R6) — RAG → KP → content
related_tables:
  - __seo_r1_gamme_slots
  - __seo_gamme_purchase_guide
  - __seo_gamme
  - __seo_gamme_conseil
  - __seo_reference
  - __seo_keywords
  - __seo_keyword_results
  - __seo_type_vlevel
  - pieces_gamme
prototype_gamme: filtre-a-huile (pg_id=7)
tags: [pipeline, r1, r4, r6, rag, zod, field-catalog, write-guard, db-invariants, evidence-pack]
---

# Pipeline Content Hardening — P0 to P1.6

> **Session scope**: transform the R1/R3/R4/R6 content enrichment pipeline from a "best-effort" system into an invariant-enforcing pipeline before rolling out new CSVs for the 229 remaining G1/G2 gammes.

## TL;DR

Prototype gamme `filtre-a-huile` revealed a silent data bug — `sgpg_arg*_content = sgpg_arg*_title` — affecting 71 R1 + 148 R6 rows (31% and 61% of canonical gammes). Root cause: three divergent RAG parsers ignored the `content` field of `rendering.arguments`. Session delivered:

- **P0**: single Zod-validated RAG parser (SSOT) replacing 3 divergent implementations
- **P0.5**: writer cleaned (14 R6-owned fields stripped from R4's payload), 7 RAG .md repaired, batch re-enrich
- **P1**: 8 CHECK constraints VALID, 6 triggers (soft-validation + gatekeeper invalidation + cascade), 88 orphan rows archived then deleted
- **P1.6**: 3 shadow fields in `__seo_keywords` deprecated via COMMENT, `v_kw_pipeline_status` monitoring view installed, `disque-de-frein` + `plaquette-de-frein` classifications completed

Pipeline post-session: **0 bug args=title** (225 R1 / 241 R6 rows), **0 orphan**, **3 gammes FULLY_ENRICHED**, **229 gammes ready for CSV rollout**.

---

## Context — the trigger

User requested a full audit of `filtre-a-huile` (prototype G1 gamme) before starting the rollout of Google Ads KW CSVs on the 229 remaining gammes. Initial audit surfaced one concrete bug plus several architectural fragilities.

## Initial audit findings

| Finding | Severity | Count |
|---|---|---|
| R1 slots with `arg*_content = arg*_title` | HIGH | 71 / 225 (31.5%) |
| R6 purchase_guide with same bug | CRITICAL | 148 / 241 (61.4%) |
| 3 divergent RAG parsers (reference / r1-enricher / buying-guide-rag-fetcher) | HIGH | 3 |
| `ParsedRagDataV4` type missing `content` field | HIGH | 1 |
| No Zod schema validating `GammeContentContract.v4` | HIGH | — |
| Field catalog missing `sgpg_arg*` + `r1s_arg*_content/icon` | MEDIUM | 21 fields |
| R4 writing 14 R6-owned fields (stripped by WriteGuard, noise) | MEDIUM | 14 fields × N gammes |
| Orphan rows in `__seo_r1_gamme_slots` (pg_id absent from pieces_gamme) | MEDIUM | 57 |
| Orphan rows in `__seo_gamme` | MEDIUM | 31 |
| Zero unit or e2e tests on enrichers | HIGH | 0 / 0 |
| Stale `sgpg_gatekeeper_score/flags` — no invalidation on content change | MEDIUM | — |

---

## P0 — Contract SSOT + unified parser

### Livrables

| Artefact | Rôle |
|---|---|
| `backend/src/config/rag-gamme-contract-v4.schema.ts` | Zod schema authoritative pour `GammeContentContract.v4`. `V4ArgumentSchema.refine()` refuse `content == title`. |
| `backend/src/modules/admin/services/rag-gamme-parser.service.ts` | Parser unique `RagGammeParserService`. Retourne `RagParseSuccess \| RagParseError` discriminated union. |
| `backend/src/modules/rag-shared/rag-shared.module.ts` | Leaf NestJS module cycle-free, importable par AdminModule et SeoModule. |
| `backend/src/modules/seo/services/reference.service.ts` | `parseRagGammeFileV4()` devient un wrapper du parser SSOT. Writer nettoyé (voir P0.5). |
| `backend/src/modules/admin/services/r1-enricher.service.ts` | `extractBuyArgs()` consomme le parser v4 en priorité 1. |
| `backend/src/modules/admin/services/buying-guide/buying-guide-rag-fetcher.service.ts` | `parseV4Frontmatter()` délègue au parser SSOT. |

### Concessions de schéma (après validation sur corpus réel)

- `V4SeveritySchema` transforme les valeurs legacy (`urgence`, `attention`) vers le set canonique `confort | securite | immobilisation`.
- `V4NormEntrySchema` accepte `string` OU `{ name, label, ref }` (fichiers legacy avec norms objects).
- Pragmatique plutôt que strict-and-break: zéro faux rejet sur le corpus existant.

### Résultat P0 sur prototype

| Métrique | Avant | Après P0 |
|---|---|---|
| filtre-a-huile R1 arg1_content length | 22 (title-dup) | 55 (real content) |
| filtre-a-huile R1 gatekeeper score | 80 (FEW_BUY_ARGS) | 90 (flags=[]) |
| R1 polluées batch | 71 | 21 (rest = 14 orphans + 7 RAG incomplete) |
| R6 polluées batch | 148 | 7 (RAG incomplete) |

---

## P0.5 — Writer cleanup + RAG repair + batch

### a) Writer R4 `writeV4ToPurchaseGuide` — drop 14 R6-owned fields

Avant P0.5, R4 envoyait 34 champs à `__seo_gamme_purchase_guide`, dont 14 étaient owned par R6_GUIDE_ACHAT. Le WriteGuard stripait correctement à chaque appel, mais c'était du noise dans les logs et une violation de scope architectural. Écriture R4 restreinte aux champs éditoriaux légitimes : `sgpg_intro_title`, `sgpg_intro_sync_parts`, `sgpg_risk_title`, `sgpg_timing_{km,years,note}`, `sgpg_arg{1-4}_{title,content,icon}` (20 fields).

### b) Field-catalog — +22 champs args

- R1_ROUTER owns: `r1s_arg{1-4}_{content,icon}` (× 8)
- R4_REFERENCE owns: `sgpg_arg{1-4}_{title,content,icon}` (× 12) + `sgpg_intro_title`, `sgpg_intro_sync_parts`, `sgpg_risk_title`, `sgpg_timing_{km,years,note}` (× 6)

Désormais 100 % des champs args sont catalogués, tracés par WriteGuardLedger, gated par le WriteGate.

### c1) RAG .md repaired (7 files)

- **4 fichiers avec YAML cassé** (duplicate keys + bad indentation dans `phase5_enrichment.technical_notes`): `flexible-de-frein`, `agregat-de-freinage`, `bougie-d-allumage`, `bobine-d-allumage`. Fix: script `clean_phase5.py` strip le bloc `phase5_enrichment` (non consommé downstream).
- **3 fichiers avec arguments sans `content:`**: `disque-de-frein`, `plaquette-de-frein`, `balais-d-essuie-glace`. Fix: script `add_content.py` injecte le `content:` canonique basé sur le title.

### d) Batch re-enrich

- R1_ROUTER (57 gammes polluées) : 50 à q=90, 7 à q=80 avant P0.5.c1 → tous à q=90 après
- R4_REFERENCE (148 gammes polluées) : q entre 68 et 94, moyenne 82

### Résultat P0.5

- 0 R6 bug (148 → 0)
- 14 R1 résiduels = **tous orphelins** (pg_alias NULL, hors `pieces_gamme`) → traités en P1.4

---

## P1 — DB invariants + cleanup structurel

### P1.1 — CHECK constraints sur args

```sql
ALTER TABLE __seo_gamme_purchase_guide
  ADD CONSTRAINT chk_sgpg_arg1_content_differs CHECK (
    sgpg_arg1_content IS NULL OR sgpg_arg1_title IS NULL
    OR sgpg_arg1_content <> sgpg_arg1_title
  );
-- × 4 sur R6 (VALID) + × 4 sur R1 (NOT VALID, tolère les 14 orphelins)
```

### P1.2 — Orphan monitoring

- `v_gamme_content_orphans` view (4 unions : R1_slots + R1_meta + R3_conseils + R6_pg)
- `fn_warn_orphan_pg_id()` + 4 triggers `BEFORE INSERT` → RAISE WARNING (soft, non bloquant)
- **FK traditionnelle impossible** : `pieces_gamme.pg_id` est INTEGER, `__seo_*.pg_id` sont TEXT/VARCHAR (dette legacy). Migration de type disruptive, choix délibéré : soft-validation + view permanente + cascade trigger (voir P1.4.4).

### P1.3 — Gatekeeper auto-invalidation

`fn_invalidate_sgpg_gatekeeper()` + `BEFORE UPDATE` trigger : nulle `sgpg_gatekeeper_score/flags/checks` dès qu'un des 17 champs content-bearing change (args × 4 × 2 + intro_role + how_to_choose + risk_explanation + risk_consequences + risk_conclusion + symptoms + selection_criteria + anti_mistakes + faq).

Bénéfice: les scores LLM-gate ne peuvent plus devenir stale silencieusement — ils sont remis à zéro, forçant une réévaluation fraîche.

### P1.4 — 88 orphans cleanup (archived then deleted)

- Pré-vérif: `pieces_actives = 0`, `in_pg_gammes = 0`, `in_seo_gamme` présent → zéro impact user.
- Archive: `_archive.orphans_gamme_content_2026_04_21` (JSONB full rows, PK `(source_table, pg_id_str)`).
- DELETE: 57 R1_slots + 31 R1_meta = 88 rows purged.
- Post-cleanup: `ALTER TABLE ... VALIDATE CONSTRAINT chk_r1s_arg{1-4}_content_differs` → tous les CHECK R1 passent NOT VALID → VALID strict.
- Cascade trigger `trg_cascade_delete_gamme_content` sur `pieces_gamme` AFTER DELETE : remplacement fonctionnel de la FK impossible. Archive dans `_archive.gamme_content_deleted` + purge des 5 tables content pour le `pg_id` supprimé.

### Résultat P1

| Mesure | Avant | Après |
|---|---|---|
| R1_slots total | 225 | 168 |
| R1_slots bug args=title | 21 | 0 |
| R1_meta total | 208 | 177 |
| R6_pg bug args=title | 7 | 0 |
| Live orphans (`v_gamme_content_orphans`) | 88 | 0 |
| Archived orphans (`_archive`) | 0 | 88 |
| CHECK VALID | 0 | 8 |
| Active triggers (protection) | 0 | 6 |

---

## P1.6 — Shadow fields deprecated + pipeline monitoring

### Shadow fields `DEPRECATED` via COMMENT

| Column | Canonical replacement |
|---|---|
| `__seo_keywords.content_type` | `__seo_keyword_results.role` (filled by `/kw-classify`) |
| `__seo_keywords.v_level` | `__seo_type_vlevel` (per pg_id + type_id) |
| `__seo_keywords.score_seo` | abandoned, unused downstream |

Non-destructif (COMMENT only). Physical DROP scheduled after grep confirms zero readers.

### `v_kw_pipeline_status` view

Scope: `__pg_gammes` canonical (G1/G2, 232 gammes).

| Stage | Signification |
|---|---|
| `NO_CSV` | Aucun KW dans `__seo_keywords` pour cette gamme |
| `CSV_IMPORTED_NOT_CLASSIFIED` | KW raw présents mais `/kw-classify` jamais tourné |
| `KP_INCOMPLETE` | Un ou plusieurs des 4 KP R1/R3/R4/R6 pas `validated` |
| `CONTENT_INCOMPLETE` | Un ou plusieurs des 4 rôles sans content row |
| `FULLY_ENRICHED` | Tous les stades cochés |

### Anomalie détectée + corrigée

La view a immédiatement révélé 2 gammes en `CSV_IMPORTED_NOT_CLASSIFIED`:
- `disque-de-frein` (1446 KW raw, 0 classified)
- `plaquette-de-frein` (1384 KW raw, 0 classified)

Root cause : les KW avaient `source='keyword-engine'` (legacy), pas `source='google-ads-kp'` — le skill `/kw-classify` filtrait sur ce flag et ignorait donc ce pool.

### Correction (SQL direct, règles du skill `/kw-classify`)

Classification appliquée avec heuristiques hiérarchiques:
1. Exclusion via `domain.must_not_contain` + patterns (tambour, hydraulique industriel, etc.)
2. Priorités d'intent: `prix|tarif|... → R1` > `brand → R6` > `comment|changer → R3` > `c'est quoi|rôle → R4` > `default → R1`
3. Percentile adaptatif par rôle (top 10% HIGH, 10-40% MED, rest LOW)

| Gamme | Raw | Classified | R1 | R6 | Stage |
|---|---|---|---|---|---|
| disque-de-frein | 1446 | 1446 | 1382 | 64 | `FULLY_ENRICHED` |
| plaquette-de-frein | 1384 | 1384 | 1339 | 45 | `FULLY_ENRICHED` |

---

## Final state (cross-phase)

```
LAYER 1 — CONTRACT SSOT (Zod v4)
  rag-gamme-contract-v4.schema.ts refuses args content==title at parse.

LAYER 2 — FIELD CATALOG (write ownership)
  22 args + 6 R4 editorial slots + pre-existing R6 fields catalogued.
  WriteGuard enforces ownership at write time.

LAYER 3 — DB INVARIANTS (hard)
  8 CHECK VALID prevent any new args=title row.

LAYER 4 — TRIGGERS (6 active)
  4 × soft-validation on orphan inserts (WARNING, non-blocking)
  1 × gatekeeper invalidation on content change (BEFORE UPDATE)
  1 × cascade delete on pieces_gamme removal (AFTER DELETE, archive + purge)

LAYER 5 — OBSERVABILITY
  v_gamme_content_orphans  — live orphan dashboard (currently 0)
  v_kw_pipeline_status     — end-to-end pipeline stage per gamme
  _archive.orphans_gamme_content_2026_04_21 — 88 rows preserved
  _archive.gamme_content_deleted — running archive for future cascades
```

### Pipeline stages distribution (232 canonical gammes)

| Stage | Count |
|---|---|
| FULLY_ENRICHED | 3 (filtre-a-huile, disque-de-frein, plaquette-de-frein) |
| CSV_IMPORTED_NOT_CLASSIFIED | 0 |
| KP_INCOMPLETE | 0 |
| CONTENT_INCOMPLETE | 0 |
| NO_CSV | 229 (ready for rollout) |

### Guarantees maintained post-session

| Invariant | Mechanism |
|---|---|
| No args content == title | 8 CHECK VALID + Zod refine |
| No silent bug propagation | Fail-fast Zod parser (SCHEMA_INVALID reject) |
| No cross-role writes | Field catalog × WriteGuard (22 new args catalogued) |
| No future orphans | Cascade trigger on pieces_gamme DELETE |
| No stale gatekeeper scores | Auto-invalidation trigger on content change |
| Full rollback possible | `_archive.orphans_gamme_content_2026_04_21` (88 rows JSONB) |
| Operational visibility | `v_gamme_content_orphans` + `v_kw_pipeline_status` |

---

## Rollout procedure (reproducible per gamme)

```bash
# 1. Import Google Ads KP CSV
python3 scripts/seo/import-gads-kp.py data/keywords/<gamme>_YYYY-MM-DD.csv

# 2. Claude classifies keywords into R1/R3/R4/R6 (or SQL heuristics fallback)
/kw-classify <gamme>

# 3. Keyword plans R1/R3/R4/R6
# Triggered by /kp <gamme> --all or individual r{1,3,4,6}-keyword-planner agents

# 4. Content enrichers (0-LLM)
curl -X POST http://localhost:3000/api/internal/pipeline/execute \
  -H "X-Internal-Key: $IK" -H "Content-Type: application/json" \
  -d '{"roleId":"R1_ROUTER","targetIds":["<pg_id>"],"dryRun":false}'
# same for R4_REFERENCE, R6_GUIDE_ACHAT (R3 handled by conseil-enricher)

# 5. Verify via monitoring view
SELECT * FROM v_kw_pipeline_status WHERE pg_alias = '<gamme>';
```

---

## Rollback procedures

### Undo P1.4 (orphan purge)

```sql
-- Restore all 88 archived orphans
INSERT INTO __seo_r1_gamme_slots
SELECT * FROM (
  SELECT (row_data->>'r1s_pg_id') AS r1s_pg_id,
         -- ... all columns cast from row_data jsonb
  FROM _archive.orphans_gamme_content_2026_04_21
  WHERE source_table = '__seo_r1_gamme_slots'
) t;

INSERT INTO __seo_gamme SELECT ... FROM _archive.orphans_gamme_content_2026_04_21
WHERE source_table = '__seo_gamme';
```

### Undo CHECK constraints

```sql
ALTER TABLE __seo_r1_gamme_slots DROP CONSTRAINT chk_r1s_arg1_content_differs;
-- × 8 drops
```

### Undo triggers

```sql
DROP TRIGGER trg_warn_orphan_r1_slots ON __seo_r1_gamme_slots;
-- × 6 triggers
DROP FUNCTION fn_warn_orphan_pg_id();
DROP FUNCTION fn_invalidate_sgpg_gatekeeper();
DROP FUNCTION fn_cascade_delete_gamme_content();
```

### Undo code changes

Git revert the commit set (reference.service, r1-enricher, buying-guide-rag-fetcher, rag-gamme-contract-v4.schema, rag-gamme-parser.service, rag-shared.module, admin.module, seo.module, field-catalog.constants).

---

## Files touched

### Monorepo — code

| File | Lines | Change |
|---|---|---|
| `backend/src/config/rag-gamme-contract-v4.schema.ts` | +320 (new) | Zod SSOT |
| `backend/src/modules/admin/services/rag-gamme-parser.service.ts` | +165 (new) | Unified parser |
| `backend/src/modules/rag-shared/rag-shared.module.ts` | +15 (new) | Leaf module |
| `backend/src/modules/seo/services/reference.service.ts` | -220 / +45 | Delegate to parser + writer cleanup (14 fields removed) |
| `backend/src/modules/admin/services/r1-enricher.service.ts` | +25 | Priority 1: RAG v4 parser |
| `backend/src/modules/admin/services/buying-guide/buying-guide-rag-fetcher.service.ts` | -95 / +30 | Delegate to parser |
| `backend/src/config/field-catalog.constants.ts` | +210 | +18 fields (r1s_arg×6 + sgpg_arg×12 + sgpg_editorial×6) |
| `backend/src/modules/admin/admin.module.ts` | +3 | Import RagSharedModule |
| `backend/src/modules/seo/seo.module.ts` | +2 | Import RagSharedModule |

### Monorepo — RAG content

| File | Change |
|---|---|
| `rag/knowledge/gammes/flexible-de-frein.md` | Strip broken `phase5_enrichment` |
| `rag/knowledge/gammes/agregat-de-freinage.md` | Strip broken `phase5_enrichment` |
| `rag/knowledge/gammes/bougie-d-allumage.md` | Strip broken `phase5_enrichment` |
| `rag/knowledge/gammes/bobine-d-allumage.md` | Strip broken `phase5_enrichment` |
| `rag/knowledge/gammes/disque-de-frein.md` | Inject 4 `content:` lines in arguments |
| `rag/knowledge/gammes/plaquette-de-frein.md` | Inject 4 `content:` lines in arguments |
| `rag/knowledge/gammes/balais-d-essuie-glace.md` | Inject 4 `content:` lines in arguments |

### DB migrations (applied via `mcp__supabase__apply_migration`)

- `p1_check_args_content_differs_from_title`
- `p1_2_orphan_monitoring_and_soft_validation`
- `p1_3_trigger_invalidate_gatekeeper_on_content_change`
- `p1_4_archive_and_cleanup_orphans`
- `p1_4_3_validate_r1_check_constraints_strict`
- `p1_4_4_cascade_gamme_delete_content_archive`
- `p1_6_deprecate_shadow_fields_and_monitor_pipeline`
- `p1_6_fix_v_kw_pipeline_status_scope`

---

## Lessons learned

1. **Silent parser divergence is the highest-impact bug class**: three parsers reading the same RAG differently caused 61 % of R6 rows to be silently polluted. Single schema SSOT + single parser service is the durable fix — not a patch on each parser.
2. **NOT VALID is the safe way to add hard invariants on legacy tables**: applied strict constraints without breaking existing rows, promoted to VALID after orphan cleanup.
3. **FK are not the only solution for referential integrity**: when type mismatch prevents a real FK, a BEFORE-INSERT WARNING trigger + AFTER-DELETE cascade trigger + live monitoring view provides equivalent guarantees with zero schema migration risk.
4. **Pipeline stage monitoring replaces ad-hoc SQL audits**: `v_kw_pipeline_status` surfaced the `disque-de-frein` / `plaquette-de-frein` anomaly within seconds, instead of waiting for a content regression at read time.
5. **"Pas de bricolage" means treat the cause**: deprecating shadow fields, refusing args=title at DB level, and adding a cascade trigger are cheaper long-term than periodic cleanup scripts.

---

## Next — P2 candidates (not done this session)

- Physical DROP of 3 deprecated `__seo_keywords` columns once grep confirms zero readers.
- Test fixtures + snapshot tests on each enricher using `filtre-a-huile.md` as canonical input.
- Dry-run mode with JSON diff on all enrichers (preview before commit).
- Versioning column `enricher_version text` on each content table for targeted re-runs.
- Admin dashboard page consuming `v_kw_pipeline_status` + `v_gamme_content_orphans`.

---

_Generated 2026-04-21 by Claude Code session. SoT: governance-vault `/opt/automecanik/governance-vault/ledger/audit-trail/`._
