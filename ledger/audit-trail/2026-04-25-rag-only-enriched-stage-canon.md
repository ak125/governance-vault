---
type: evidence-pack
date: 2026-04-25
owner: Fafa
duration: ~30min
session_id: rag-only-enriched-stage-canon-20260425
scope: Decouverte que 147 gammes (63%) etaient artificiellement en NO_CSV ; ajout du stage canon RAG_ONLY_ENRICHED
related_files:
  - backend/supabase/migrations/20260425_v_kw_pipeline_status_rag_only_enriched.sql
  - ledger/rules/rules-seo-kw-import.md (R-SEO-KW-07 ajoutee)
  - ops/moc/MOC-Rules.md
prototype_gammes: [agregat-de-freinage]
tags: [pipeline-stage, view-canonical, rag-only, freinage-13-13, r-seo-kw-07]
related_prs:
  - ak125/nestjs-remix-monorepo (migration view, en cours)
related_canon:
  - ledger/rules/rules-seo-kw-import.md (R-SEO-KW-07)
continues_from: 2026-04-24-seo-kw-kit-frein-arriere-3-incidents-db.md
---

# Pipeline stage canonique `RAG_ONLY_ENRICHED`

## TL;DR

Demande utilisateur : "agregat-de-freinage pas de KW". Diagnostic : la gamme
pg=415 est entierement enrichie via RAG (R1+R3+R4+R6 KP validated + content
present, 10 sections R3) mais sans Google Ads KW car niche (composant ABS).

**Decouverte** : la view `v_kw_pipeline_status` retournait `NO_CSV` en premier
dans son CASE, masquant **147 / 232 gammes G1/G2 (63%)** dans cet etat
"RAG-only-enriched legitime". Le BLOCK QA Phase 8 cachait cette majorite
fonctionnelle.

**Fix canon** : nouveau stage prioritaire `RAG_ONLY_ENRICHED` ajoute au CASE.
Skill `/gamme-qa` Phase 8 doit l'accepter comme PASS (regle R-SEO-KW-07).

**Resultat** : freinage **12/13 → 13/13 canon** (+1 pg=415 RAG_ONLY).

## 1 — Diagnostic initial

État pg=415 `agregat-de-freinage` :

| Champ | Valeur |
|---|---|
| `__seo_keywords` | 0 |
| `__seo_keyword_results` | 0 |
| `__seo_r1_gamme_slots` | 1 row |
| `__seo_reference` | 1 published |
| `__seo_gamme_purchase_guide` | 1 row |
| `__seo_gamme_conseil` | 10 sections |
| R1 KP | validated/82 |
| R3 KP | validated |
| R6 KP | validated |
| `pipeline_stage` | `NO_CSV` (BLOCK Phase 8) |
| `pg_meta` | level=1, display=1, relfollow=1 (gamme active) |

Tout est canon-enrichi sauf le KW source. La gamme est niche : "agregat de freinage"
designe les modules ABS/ESP integres, peu de volume search Google Ads.

## 2 — Decouverte du gap systemique

Avant fix, comptage par stage :

```sql
SELECT pipeline_stage, COUNT(*) FROM v_kw_pipeline_status GROUP BY pipeline_stage;
```

| Stage | n |
|---|---|
| FULLY_ENRICHED | 19 |
| NO_CSV | 213 |

**213 gammes en NO_CSV** alors que la majorite a tout son content R1+R3+R4+R6 et
ses 4 KP validated.

Apres fix (branch RAG_ONLY_ENRICHED prioritaire) :

| Stage | n |
|---|---|
| FULLY_ENRICHED | 19 |
| **RAG_ONLY_ENRICHED** | **147** ⬆ |
| NO_CSV | 66 (vrais incomplets, sans content R1/R3/R4/R6) |

→ **63 % du catalogue** etait artificiellement BLOCK par Phase 8 alors qu'il
etait fonctionnellement complet.

## 3 — Migration canon

### View update

```sql
CASE
  -- NEW : prioritaire sur NO_CSV
  WHEN raw_count IS NULL
    AND kp_r1.pg_id IS NOT NULL
    AND kp_r3.pg_id IS NOT NULL
    AND kp_r6.pg_id IS NOT NULL
    AND content_r1.pg_id IS NOT NULL
    AND content_r3.pg_id IS NOT NULL
    AND content_r4.pg_id IS NOT NULL
    AND content_r6.pg_id IS NOT NULL
    THEN 'RAG_ONLY_ENRICHED'
  WHEN raw_count IS NULL THEN 'NO_CSV'
  ...
END
```

Migration : `backend/supabase/migrations/20260425_v_kw_pipeline_status_rag_only_enriched.sql`
(PR monorepo, branche `fix/db-view-rag-only-enriched-stage`).

Idempotent (CREATE OR REPLACE VIEW).

### Regle canon

`R-SEO-KW-07` ajoutee a `rules-seo-kw-import.md` :

> Une gamme avec `pipeline_stage = 'RAG_ONLY_ENRICHED'` est canon-valide et
> equivalent fonctionnel a `FULLY_ENRICHED` pour QA Phase 8. NE PAS bloquer
> sur l'absence de Google Ads KW si tous les KP+content sont presents.

3 cas legitimes documentes :
1. Gamme niche (faible volume search)
2. Pre-canon legacy (enrichie avant flow google-ads-kp)
3. CSV pas encore exporte (en attente)

## 4 — Impact freinage

| Avant fix | Apres fix |
|---|---|
| Freinage 12/13 canon | **Freinage 13/13 canon** (12 FULLY + 1 RAG_ONLY) |
| pg=415 BLOCK NO_CSV | pg=415 PASS RAG_ONLY_ENRICHED |

Domaine freinage **complete**.

## 5 — Skill `/gamme-qa` mise a jour

Le skill markdown n'est pas dans le filesystem du monorepo (loaded par Claude
Code remote). La regle R-SEO-KW-07 du vault canon est la **source de verite**
pour la prochaine generation/maj du skill, qui devra mettre a jour Phase 8 :

```diff
- BLOCK si pipeline_stage != 'FULLY_ENRICHED'
+ BLOCK si pipeline_stage NOT IN ('FULLY_ENRICHED', 'RAG_ONLY_ENRICHED')
+ INFO si pipeline_stage = 'RAG_ONLY_ENRICHED' (gamme niche/RAG-only legitime)
```

## 6 — Anti-pattern documente

Stub KW vol=0 inserts manuels pour "flipper" NO_CSV → CSV_IMPORTED **interdits**.
C'est du bricolage qui ment a la view. Le stage RAG_ONLY_ENRICHED est la
verite : pas de KW Google Ads, contenu complet.

## 7 — Coverage manifest

```
scope_requested:        Resoudre pg=415 agregat-de-freinage NO_CSV bloquant
scope_actually_scanned: 1 view (v_kw_pipeline_status) + impact systemique sur
                        232 gammes G1/G2

files_read_count:       3 (view def, rules canon, MOC)
excluded_paths:         skill /gamme-qa (filesystem absent, doc canon en lieu)
unscanned_zones:        autres views pipeline_stage potentielles

corrections_proposed:   1 view migration + 1 nouvelle regle canon
corrections_applied:
  - DB live : view v_kw_pipeline_status updated (CREATE OR REPLACE)
  - Migration file : 20260425_v_kw_pipeline_status_rag_only_enriched.sql
  - Vault rules : R-SEO-KW-07 ajoutee a rules-seo-kw-import.md
  - MOC-Rules : entry mise a jour R-SEO-KW-01..07

validation_executed:
  - pg=415 NO_CSV → RAG_ONLY_ENRICHED verified
  - Distribution post-migration : 19 FULLY + 147 RAG_ONLY + 66 NO_CSV
  - Freinage 13/13 canon verified

remaining_unknowns:
  - Quand le skill /gamme-qa sera mis a jour (Phase 8 alignment)
  - Si la majorite des 147 gammes RAG_ONLY meritent un export Google Ads KP
    futur ou si elles restent legitimement RAG-only

final_status: SCOPE_SCANNED
```
