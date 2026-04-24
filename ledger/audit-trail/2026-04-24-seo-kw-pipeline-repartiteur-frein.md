---
type: evidence-pack
date: 2026-04-24
owner: Fafa
duration: ~25min
session_id: seo-kw-repartiteur-frein-20260424
scope: Pipeline SEO KW `repartiteur-de-frein` (gamme 18/232) — première application formelle de R-SEO-KW-06
related_files:
  - config/rag-alias-expansions.yaml
  - scripts/seo/import-gads-kp.py
  - scripts/seo/rebuild-type-vlevel.py
prototype_gammes: [repartiteur-de-frein]
tags: [pipeline, seo, kw, r1-router, vlevel, r-seo-kw-06, synonymes-techniques]
related_prs:
  - ak125/nestjs-remix-monorepo#150 (merged — 7 aliases canon)
related_canon:
  - ledger/rules/rules-seo-kw-import.md (R-SEO-KW-06)
  - ledger/audit-trail/2026-04-23-freinage-completion-backlog.md
continues_from: 2026-04-23-freinage-completion-backlog.md
---

# Pipeline SEO KW — `repartiteur-de-frein` (gamme 18/232)

## TL;DR

Première application formelle de **R-SEO-KW-06** (cross-gamme scope check codifié hier). Rejection 28.6 % → vérification taxo SQL canon → 5 siblings tous inactifs → alias large légitime. **7 aliases canon** reflétant les synonymes techniques auto (répartiteur = régulateur = compensateur = limiteur). PR monorepo #150 merged. QA 9 phases **PASS** avec R6 score=84.

## 1 — Application R-SEO-KW-06

### Signal

Dry-run : 62 raw → 52 pertinents, rejets vol = 1400 / 4900 = **28.6 %** (> 5 % seuil R-SEO-KW-01 mais < 50 % seuil R-SEO-KW-06).

### Check taxonomie DB (R-SEO-KW-06 step 1-2)

```sql
SELECT pg_id, pg_alias, pg_level, pg_display,
  (SELECT COUNT(*) FROM __seo_keywords WHERE pg_id=pg.pg_id) AS kw,
  (SELECT COUNT(*) FROM __seo_r1_gamme_slots WHERE r1s_pg_id::text=pg.pg_id::text) AS r1
FROM pieces_gamme pg
WHERE pg_alias ~ '(compensateur|limiteur|regulateur).*frein'
ORDER BY pg_id;
```

| pg_id | pg_alias | level | display | kw | r1 | Verdict |
|---|---|---|---|---|---|---|
| **73** | `repartiteur-de-frein` | 2 | 1 | 0 | 1 | ✅ **ACTIVE** |
| 167 | `regulateur-de-la-pression-de-freinage` | 5 | 0 | 0 | 0 | Inactive |
| 782 | `kit-de-reparation-regulateur-de-freinage` | 4 | 0 | 0 | 0 | Kit (distinct) |
| 1341 | `regulateur-alb-repartition-automatique-force-de-fr` | 4 | 0 | 0 | 0 | Inactive |
| 2734 | `tampon-regulateur-de-freinage` | 4 | 0 | 0 | 0 | Tampon (distinct) |
| 3666 | `regulateur-de-pression-alimentation-air-ventilatio` | 4 | 0 | 0 | 0 | Air (distinct domaine) |

### Décision R-SEO-KW-06 (arbre step 3)

**1 seule gamme active** → alias large **LÉGITIME**. Ajout sans réserve.

## 2 — Terminologie canon documentée

En mécanique auto française, les 4 termes désignent la **même pièce** (valve régulant la pression hydraulique entre circuits avant/arrière selon charge véhicule) :

| Terme | Origine | Fréquence Google |
|---|---|---|
| **Répartiteur de frein** | Technique constructeur FR | Dominant (appellation officielle Renault/Peugeot) |
| **Régulateur de (pression de) freinage** | Technique ingénierie | Moyen |
| **Compensateur (de) freinage** | Argot atelier | Moyen |
| **Limiteur de freinage** | Documentation ADEME | Moindre |

RAG `/opt/automecanik/rag/knowledge/gammes/repartiteur-de-frein.md` mentionne principalement "répartiteur" — les 3 autres termes n'étaient pas dans `variants[].aliases` d'où les rejets massifs.

## 3 — Aliases ajoutés (PR #150)

```yaml
repartiteur-de-frein:
  # Added 2026-04-24 (R1_ROUTER batch) — R-SEO-KW-01 review 28.6% vol → ~0%
  # Canon R-SEO-KW-06 : pg=73 seule active, siblings pg=167/782/1341/2734/3666
  # tous inactifs (level≥4, display=0, 0 KW). Répartiteur = régulateur =
  # compensateur = limiteur de freinage (synonymes techniques exacts).
  - repartiteur freinage          # forme sans "de"
  - regulateur de frein           # synonyme technique
  - regulateur de freinage
  - compensateur de freinage      # synonyme technique auto
  - compensateur freinage
  - limiteur de freinage          # synonyme technique
  - limiteur frein
```

Post-YAML : 62 raw → 61 pertinents (1 rejet à vol=50) = **1.6 % vol rejeté** ✅

## 4 — Pipeline exécuté

| Étape | Outil | Résultat |
|---|---|---|
| YAML batch | PR #150 merged | 7 aliases ajoutés |
| Live import | `import-gads-kp.py --pg-id 73` | 61 rows UPSERT `__seo_keywords` |
| Classify | Python script (règles canon) | R1=57, R4=4 (UPSERT 61/61) |
| Vehicle extract | RPC `extract_vehicle_keywords(73)` | 18 KW type='vehicle' |
| Backfill type_id | SQL match canon R-SEO-KW-06 §3 | 18 type_ids backfilled |
| V-Level assign | ROW_NUMBER() per (model, energy) group | 18 KW classifiés V2/V3 |
| Reset + re-assign | Unique constraint violation fix | Clean state, 9 V2 + 9 V3 |
| UPSERT type_vlevel | `rebuild-type-vlevel.py 73` | 9 rows (V2=9, conf=0.90) |
| R6 enrich | POST `/api/admin/buying-guides/enrich` | 5 sections, score=84 |

### Note : unique constraint violation

À la première tentative d'UPDATE v_level, PostgreSQL a retourné :

```
ERROR: 23505: duplicate key value violates unique constraint
"ux__seo_keywords_v2_unique_by_pg_model_energy"
DETAIL: Key (pg_id, COALESCE(model, '__NULL__'::text), COALESCE(lower(energy), 'unknown'::text))=(73, c15, unknown) already exists.
```

**Cause** : `insert-missing-keywords.ts --recalc` avait déjà assigné un V2 pour (73, c15, unknown) sans qu'aucun type_id ne soit backfillé. La re-assign SQL avec ROW_NUMBER() essayait d'en attribuer un second.

**Fix** : `UPDATE SET v_level = NULL WHERE pg_id=73 AND type='vehicle'` avant re-assign. Pattern canon à ajouter dans `rebuild-type-vlevel.py` pour éviter double-assign.

## 5 — Verdict QA

```
Phase 1  : PASS  Zod OK, 61 KW imported (YAML +7 aliases)
Phase 2  : PASS  R1=57 R4=4 (source=google-ads-kp, R3/R6=0 INFO)
Phase 3  : PASS  R1=82 validated, R3/R6 validated, R4=missing (WARN)
Phase 4  : PASS  R1=90, R4 pub def=519 (WARN <600), R6=84, R3=12 sections
Phase 5  : PASS  0 orphans/bugs
Phase 5B : PASS  9 V-Level rows (V2=9) conf=0.90
Phase 7  : PASS  0 pollution
Phase 8  : PASS  FULLY_ENRICHED
Phase 9  : PASS  q2..q7=0
```

**VERDICT : PASS** (2 WARN non-bloquants).

## 6 — État freinage post-session

| Statut | Count | Delta |
|---|---|---|
| ✅ FULLY canon | **11 / 13** | +1 (pg=73) |
| NO_CSV | 2 / 13 | -1 |

2 gammes restantes NO_CSV : pg=415 `agregat-de-freinage`, pg=3859 `kit-de-freins-arriere` (état legacy).

## 7 — Follow-up (pattern à ajouter au script canon)

Dans `scripts/seo/rebuild-type-vlevel.py` ou dans un wrapper, ajouter une phase "reset v_level" avant la re-assignation SQL per-group, pour éviter la collision avec les v_level pré-existants assignés par `insert-missing-keywords.ts`.

Proposition de séquence canon :

```python
def reassign_vlevel_by_group(pg_id):
    # 1. Reset
    execute("UPDATE __seo_keywords SET v_level = NULL WHERE pg_id=%s AND type='vehicle'", [pg_id])
    # 2. Assign champion per (model, energy)
    execute("""
      WITH ranked AS (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY model, COALESCE(energy,'unknown') ORDER BY volume DESC, id) AS rn
        FROM __seo_keywords
        WHERE pg_id=%s AND type='vehicle' AND type_id IS NOT NULL AND volume > 0
      )
      UPDATE __seo_keywords sk SET v_level = CASE WHEN r.rn = 1 THEN 'V2' ELSE 'V3' END
      FROM ranked r WHERE sk.id = r.id
    """, [pg_id])
```

À soumettre en PR séparée (canon clean-up, pas urgent).

## 8 — Coverage manifest

```
scope_requested:        Pipeline SEO KW `repartiteur-de-frein` + application R-SEO-KW-06
scope_actually_scanned: 1 gamme, 6 siblings taxo analysés, 9 phases QA, 7 aliases YAML

files_read_count:       ~5 (RAG .md, scripts seo, SQL RPC defs)
excluded_paths:         gammes freinage déjà canon (traitées sessions précédentes)
unscanned_zones:        pg=415, 3859 (NO_CSV)

corrections_proposed:   7 aliases YAML (première application R-SEO-KW-06)
corrections_applied:
  - PR monorepo #150 merged (7 aliases)
  - Live import 61 rows __seo_keywords
  - UPSERT 61 rows __seo_keyword_results
  - extract_vehicle_keywords(73) → 18 KW matched
  - Backfill type_id SQL → 18 rows
  - Reset + re-assign v_level per (model, energy) group
  - rebuild-type-vlevel.py → 9 rows __seo_type_vlevel (V2=9)
  - R6 enricher live → score 84

validation_executed:
  - Dry-run before/after YAML (28.6% → 1.6%)
  - Cross-gamme taxo check SQL (5 siblings verified inactive)
  - QA 9 phases consolidated check

remaining_unknowns:
  - Comment enrichir pg=415 agregat-freinage (attente CSV)
  - État legacy pg=3859 kit-freins-arriere (attente CSV)
  - Pattern "reset v_level before reassign" à formaliser dans script canon

final_status: SCOPE_SCANNED
```
