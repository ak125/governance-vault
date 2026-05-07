# 05 — Bucket samples (W2) + smoke URLs (W4)

## Bucket A_long — observation cohort (n=6)

Slots avec `LENGTH(r1s_micro_seo_block) >= 700`. **Pas d'intervention** sur ces slots dans la fenêtre T0→T+30 — observation passive uniquement.

| pg_id | pg_alias | len | URL |
|-------|----------|-----|-----|
| 7    | filtre-a-huile      | 804  | https://www.automecanik.com/pieces/filtre-a-huile-7 |
| 82   | disque-de-frein     | 1250 | https://www.automecanik.com/pieces/disque-de-frein-82 |
| 128  | joint-chemise-de-cylindre        | 700  | https://www.automecanik.com/pieces/joint-chemise-de-cylindre-128 |
| 792  | moteur-electrique-de-ventilateur | 756  | https://www.automecanik.com/pieces/moteur-electrique-de-ventilateur-792 |
| 854  | amortisseur         | 939  | https://www.automecanik.com/pieces/amortisseur-854 |
| 3902 | injecteur           | 754  | https://www.automecanik.com/pieces/injecteur-3902 |

**Note** : 4/6 ont des impressions à T0. Slots `128` et `792` sans data GSC — éligibles pour exclusion T+30 si toujours zéro.

## Bucket B_short — observation cohort stratifié (n=10)

Slots avec `LENGTH(r1s_micro_seo_block) < 300`. Sélection top 10 par impressions T0 pour comparable de pouvoir statistique avec A_long.

| pg_id | pg_alias | len | impressions T0 | URL |
|-------|----------|-----|----|-----|
| 1145 | vanne-egr                                | 147 | 2000 | https://www.automecanik.com/pieces/vanne-egr-1145 |
| 10   | courroie-d-accessoire                    | 145 | 791  | https://www.automecanik.com/pieces/courroie-d-accessoire-10 |
| 8    | filtre-a-air                             | 283 | 684  | https://www.automecanik.com/pieces/filtre-a-air-8 |
| 310  | galet-tendeur-de-courroie-d-accessoire   | 148 | 645  | https://www.automecanik.com/pieces/galet-tendeur-de-courroie-d-accessoire-310 |
| 316  | thermostat                               | 146 | 470  | https://www.automecanik.com/pieces/thermostat-316 |
| 577  | volant-moteur                            | 163 | 298  | https://www.automecanik.com/pieces/volant-moteur-577 |
| 2234 | turbo                                    | 159 | 264  | https://www.automecanik.com/pieces/turbo-2234 |
| 307  | kit-de-distribution                      | 154 | 248  | https://www.automecanik.com/pieces/kit-de-distribution-307 |
| 4    | alternateur                              | 170 | 241  | https://www.automecanik.com/pieces/alternateur-4 |
| 1260 | pompe-a-eau                              | 156 | 235  | https://www.automecanik.com/pieces/pompe-a-eau-1260 |

## Smoke test prod — W4 (rendering visuel)

Échantillon mixte pour vérifier `SafeCompatTable.tsx` rendering avec `r1s_safe_table_rows` populé. Suite au backfill 2.B (PR #332), 169/169 slots ont `r1s_safe_table_rows` non-vide → le test "fallback render" sur slots NULL n'est plus possible (hors scope ce snapshot).

| Cible | pg_id | URL | Vérifier |
|-------|-------|-----|----------|
| A_long high-traffic | 7 (filtre-a-huile, 140 imp) | https://www.automecanik.com/pieces/filtre-a-huile-7 | Render `SafeCompatTable` non-vide, longueur micro_seo_block apparente ≥700c |
| A_long high-CTR | 854 (amortisseur, 56 imp, 3.57% CTR) | https://www.automecanik.com/pieces/amortisseur-854 | Idem + cross-link motorisations actif |
| B_short top-traffic | 1145 (vanne-egr, 2000 imp) | https://www.automecanik.com/pieces/vanne-egr-1145 | Render OK avec micro_seo_block court (~147c) — pas de "trou" visuel |
| B_short ranked-1st | 277 (cylindre-de-roue, position 1.0) | https://www.automecanik.com/pieces/cylindre-de-roue-277 | Vérifier qu'aucune erreur console pendant render |

**Méthode** : visite navigateur (mobile + desktop), DevTools console, inspect `<table data-component="SafeCompatTable">`. Pas de DB write durant le smoke. À effectuer une fois post-deploy preprod confirmé (tag `v2026.04.28` already in PROD per memory).

## SQL canonique pour re-générer ces samples

```sql
-- A_long sample (intervalle ouvert pour réassocier si seuil change à T+30)
SELECT s.r1s_pg_id, g.pg_alias, LENGTH(s.r1s_micro_seo_block) AS len
FROM __seo_r1_gamme_slots s
LEFT JOIN pieces_gamme g ON g.pg_id::text = s.r1s_pg_id::text
WHERE LENGTH(s.r1s_micro_seo_block) >= 700
ORDER BY len DESC;

-- B_short top 10 by impressions (re-run after each snapshot to refresh)
WITH gsc_28d AS (
  SELECT (regexp_match(d.page, '/pieces/[^/]+-(\d+)(?:\.html)?(?:/|$)'))[1] AS pg_id,
         SUM(d.impressions) AS impressions
  FROM __seo_gsc_daily d
  WHERE d.date >= DATE '2026-05-04' - INTERVAL '28 days'
    AND d.date <= DATE '2026-05-04'
    AND d.page LIKE 'https://www.automecanik.com/pieces/%'
    AND d.page NOT LIKE '%/auto-%' AND d.page NOT LIKE '%/voiture-%'
  GROUP BY 1
)
SELECT s.r1s_pg_id, g.pg_alias, LENGTH(s.r1s_micro_seo_block) AS len, gsc.impressions
FROM __seo_r1_gamme_slots s
LEFT JOIN pieces_gamme g ON g.pg_id::text = s.r1s_pg_id::text
LEFT JOIN gsc_28d gsc ON gsc.pg_id = s.r1s_pg_id::text
WHERE LENGTH(s.r1s_micro_seo_block) < 300
ORDER BY gsc.impressions DESC NULLS LAST
LIMIT 10;
```
