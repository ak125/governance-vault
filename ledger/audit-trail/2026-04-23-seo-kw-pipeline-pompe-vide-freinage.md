---
type: evidence-pack
date: 2026-04-23
owner: Fafa
duration: ~40min
session_id: seo-kw-pompe-vide-freinage-20260423
scope: Pipeline SEO KW `pompe-a-vide-de-freinage` (gamme 17/232) avec arbitrage canon taxonomie inter-gammes
related_files:
  - config/rag-alias-expansions.yaml
  - scripts/seo/import-gads-kp.py
  - scripts/insert-missing-keywords.ts
  - scripts/seo/rebuild-type-vlevel.py
prototype_gammes: [pompe-a-vide-de-freinage]
tags: [pipeline, seo, kw, r1-router, vlevel, canon-taxonomy, cross-gamme-scope]
related_prs:
  - ak125/nestjs-remix-monorepo#137 (merged — YAML batch pompe-a-vide, 89% → 3.9% rejets)
related_canon:
  - ledger/rules/rules-seo-kw-import.md
  - ledger/audit-trail/2026-04-23-seo-kw-vehicle-rpc-refactor.md (RPC refactor)
continues_from: 2026-04-23-seo-kw-vehicle-rpc-refactor.md
---

# Pipeline SEO KW — `pompe-a-vide-de-freinage`

## TL;DR

Gamme 17/232 du batch R1_ROUTER. Cas d'école **cross-gamme scope** : 4 gammes `pompe-a-vide-*` coexistent en DB mais 1 seule est éditorialement active. R-SEO-KW-01 triggered à 89% (CSV scopé trop large), résolu par analyse canon de la taxonomie DB + alias YAML élargi. **QA 9 phases PASS** avec score R6=84 (PR #130 gatekeeper wiring actif) et V-Level via canon script `rebuild-type-vlevel.py` (PR #131).

## 1 — Arbitrage canon cross-gamme `pompe-a-vide-*`

Dry-run initial : **89 % vol rejeté** (5650/6350). Cause : filtre RAG core_words=`['pompe','vide','freinage']` exige "freinage" explicite, mais 95 % des KW Google Ads utilisent "frein" ou juste "pompe à vide + véhicule".

### Taxonomie DB lue

```sql
SELECT pg_id, pg_alias, pg_level, pg_parent, pg_display, pg_relfollow
FROM pieces_gamme WHERE pg_id IN (387, 2397, 1416, 1417);
```

| pg_id | pg_alias | level | parent | display | relfollow | Content |
|---|---|---|---|---|---|---|
| **387** | `pompe-a-vide-de-freinage` | **1** | self | **1** | 1 | R1+R3(11)+R4+R6 ✅ |
| 2397 | `pompe-a-vide` | 4 | self | 0 | 0 | vide |
| 1417 | `pompe-a-vide-verrouillage-central` | 5 | **387** | 0 | 0 | vide |
| 1416 | `pompe-vide climatisation-*` | **0** | self | 1 | 0 | vide |

### Décision

- `pg=387` est la **seule gamme éditoriale visible** (level=1, display=1, enrichie).
- `pg=1417` est **child de pg=387** (sous-catégorie cachée, absorbée).
- `pg=1416` est **exclu de `__pg_gammes` G1/G2** (level=0 → gamme morte, cf. mémoire `gamme_aggregates` : 232 gammes G1/G2 exclut pg_level=0).
- `pg=2397` est un rollup technique interne (display=0).

**Conclusion canon** : ajouter `pompe a vide` comme alias de pg=387 n'est **pas du bricolage** — c'est refléter la taxonomie DB où pg=387 est la seule surface éditoriale. Aucune cannibalisation réelle.

### YAML appliqué (PR [#137](https://github.com/ak125/nestjs-remix-monorepo/pull/137))

```yaml
pompe-a-vide-de-freinage:
  - pompe a vide frein
  - pompe a vide pour frein
  - pompe a depression frein
  - pompe depression frein
  - pompe a vide servo frein
  - pompe a vide          # catch vehicule/motorisation ambigus
  - pompe de frein        # forme courte FR
```

Post-YAML : 100 raw → 86 pertinents, 5 rejets (≈ 3.9 % vol < 5 % seuil R-SEO-KW-01) ✅

## 2 — Pipeline exécuté

| Étape | Outil canon | Résultat |
|---|---|---|
| Dry-run | `import-gads-kp.py --suggest-aliases --threshold-vol 50` | 89 % rejets → arbitrage taxo |
| YAML batch | PR #137 merged (`dff60aa6`) | 7 aliases, 89 % → 3.9 % |
| Live import | `import-gads-kp.py --pg-id 387` | 86 rows UPSERT |
| Classify | skill `/kw-classify` (règles priorité) | R1=77 R3=4 R4=4 R6=1 (86 UPSERT) |
| Vehicle extract | RPC `extract_vehicle_keywords(387)` + backfill SQL | 20 KW type=vehicle, 20 type_id |
| V-Level | `insert-missing-keywords.ts --recalc` (PR #132 dynamique) | 20 KW classifiés V2/V3/V4 via `match_keyword_text_to_vehicle_batch` |
| UPSERT type_vlevel | **`rebuild-type-vlevel.py 387` (PR #131 canon)** | 12 rows V2=10 V3=2 V4=0 conf=0.90 |
| R6 enrich | POST `/api/admin/buying-guides/enrich` (PR #130 wiring) | 5 sections updated, **score=84** |

## 3 — Verdict QA

```
Phase 1  : PASS  Zod OK, 86 KW imported
Phase 2  : PASS  R1=77 R3=4 R4=4 R6=1
Phase 3  : PASS  R1=78 validated, R3/R6 validated, R4=missing (WARN optionnel)
Phase 4  : PASS  R1=90, R4 pub def=531 (WARN <600), R6=84, R3=11 sections
Phase 5  : PASS  0 orphans/bugs
Phase 5B : PASS  12 V-Level rows (V2=10 V3=2) conf=0.90
Phase 7  : PASS  0 pollution
Phase 8  : PASS  FULLY_ENRICHED
Phase 9  : PASS  q2..q7=0
```

**VERDICT : PASS** (0 BLOCK, 2 WARN non-bloquants : R4 KP missing + R4 def<600).

## 4 — Améliorations notables vs sessions précédentes

Les 2 follow-ups identifiés dans evidences `cable-frein-main` et `maitre-cylindre` ont été livrés en parallèle :

- **PR #130** — R6 `BuyingGuideQualityGatesService` wire : `sgpg_gatekeeper_score/flags/checks` désormais persistés symétriquement à R1. Évidence : pg=387 R6 score=84 (vs NULL pour pg=124 avant ce fix).
- **PR #131** — Script canon `rebuild-type-vlevel.py` : remplace le manual SQL UPSERT par un CLI testé. Utilisé ici en one-shot (`python3 scripts/seo/rebuild-type-vlevel.py 387`).

Zéro dette technique résiduelle du workflow V-Level + R6 gatekeeper.

## 5 — Règle canon émergente : arbitrage cross-gamme

Quand un CSV déclenche **R-SEO-KW-01 au-delà de 50 % vol rejeté** (au lieu du seuil 5 %), c'est un signal de **scope mismatch** qui nécessite une analyse taxonomie avant tout ajout d'alias :

1. **Identifier les siblings** : `SELECT pg_id, pg_alias, pg_level, pg_parent, pg_display FROM pieces_gamme WHERE pg_alias ~ '<famille>'`
2. **Vérifier leur état** : RAG, content, pipeline_stage. Si inactifs → gamme active = catch-all légitime.
3. **Si siblings actifs** : NE PAS ajouter alias large. Demander scope plus strict au CSV source.

Proposition d'ajout au runbook `ledger/rules/rules-seo-kw-import.md` : **R-SEO-KW-06 : Cross-gamme scope check required when rejection rate ≥ 50 %.**

## 6 — Coverage manifest

```
scope_requested:        Pipeline SEO KW `pompe-a-vide-de-freinage`
scope_actually_scanned: 1 gamme, 4 siblings analysés, 9 phases QA, 7 aliases YAML

files_read_count:       ~6 (scripts seo, config/rag-alias-expansions.yaml, RAG .md, SQL rpc defs)
excluded_paths:         gammes autres que pompe-a-vide-*
unscanned_zones:        autres gammes R1_ROUTER du batch

corrections_proposed:   7 aliases YAML canon (pg=387 champion)
corrections_applied:
  - PR monorepo #137 merged (dff60aa6)
  - Live import 86 rows __seo_keywords (100 raw → 86 pertinents)
  - UPSERT 86 rows __seo_keyword_results
  - extract_vehicle_keywords(387) → 20 KW type=vehicle
  - Backfill type_id via custom SQL (20 KW)
  - insert-missing-keywords.ts --recalc → v_level V2=10 V3=3 V4=7
  - rebuild-type-vlevel.py 387 → 12 rows __seo_type_vlevel
  - R6 enricher live → score 84 (PR #130 wiring active)

validation_executed:
  - Dry-run before/after (89 % → 3.9 %)
  - QA 9 phases consolidated check
  - kw_vehicle_without_vlevel = 0 verification

remaining_unknowns:
  - R4 KP manquant (R4 optionnel, non-bloquant)
  - R4 definition=531 chars (<600 conseillé — enrichissement possible)
  - Proposition R-SEO-KW-06 pour codifier cross-gamme scope check (hors scope PR)

final_status: SCOPE_SCANNED
```
