-- =============================================================================
-- ADR-041 — Baseline T0 GSC snapshot 2026-05-06
-- =============================================================================
-- Read-only. Joins __seo_gsc_daily × __seo_r1_gamme_slots × pieces_gamme.
-- 28-day rolling window ending 2026-05-04 (GSC T-2 lag).
--
-- Run:
--   psql "$DATABASE_URL" -f 03-baseline-snapshot.sql > snapshots/2026-05-06.tsv
--   # or via Supabase MCP execute_sql, query block at a time.
--
-- Convert to JSON for archival:
--   psql "$DATABASE_URL" -At -F$'\t' -f 03-baseline-snapshot.sql \
--     | jq -Rs 'split("\n")|map(split("\t"))' > snapshots/2026-05-06.json
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Q1 — Aggregate baseline 28d rolling per pg_id
--
-- Output : 169 rows (one per R1 slot), with GSC metrics or NULL if no GSC data.
-- Columns: pg_id, pg_alias, micro_seo_len, has_safe_table, gatekeeper_score,
--          clicks, impressions, ctr, position, gsc_url_count
-- -----------------------------------------------------------------------------

WITH r1_slots AS (
  SELECT
    s.r1s_pg_id            AS pg_id,
    g.pg_alias             AS pg_alias,
    LENGTH(s.r1s_micro_seo_block) AS micro_seo_len,
    (s.r1s_safe_table_rows IS NOT NULL
       AND jsonb_array_length(s.r1s_safe_table_rows::jsonb) > 0) AS has_safe_table,
    s.r1s_gatekeeper_score AS gatekeeper_score,
    -- Bucket attribution for 2.A A/B test
    CASE
      WHEN LENGTH(s.r1s_micro_seo_block) >= 700 THEN 'A_long'
      WHEN LENGTH(s.r1s_micro_seo_block) <  300 THEN 'B_short'
      ELSE 'mid'
    END AS bucket_2a
  FROM __seo_r1_gamme_slots s
  LEFT JOIN pieces_gamme g ON g.pg_id = s.r1s_pg_id
),
gsc_28d AS (
  SELECT
    -- Extract pg_id from URL pattern: https://www.automecanik.com/pieces/{slug}-{pg_id}[.html|/...]
    -- Match the trailing `-NNNN` segment that is followed by `.html` or `/` or end-of-string.
    NULLIF(
      (regexp_match(d.page, '/pieces/[^/]+-(\d+)(?:\.html)?(?:/|$)'))[1],
      ''
    )::int AS pg_id,
    SUM(d.clicks)        AS clicks,
    SUM(d.impressions)   AS impressions,
    -- CTR weighted = clicks / impressions (not avg of ctrs)
    CASE WHEN SUM(d.impressions) > 0
      THEN SUM(d.clicks)::numeric / SUM(d.impressions)::numeric
      ELSE 0
    END AS ctr,
    -- Position weighted by impressions
    CASE WHEN SUM(d.impressions) > 0
      THEN SUM(d.position * d.impressions)::numeric / SUM(d.impressions)::numeric
      ELSE NULL
    END AS position,
    COUNT(DISTINCT d.page) AS gsc_url_count
  FROM __seo_gsc_daily d
  WHERE d.date >= DATE '2026-05-04' - INTERVAL '28 days'
    AND d.date <= DATE '2026-05-04'
    AND d.page LIKE 'https://www.automecanik.com/pieces/%'
    -- Exclude vehicle-scoped URLs (R8) — keep pure R1 only
    AND d.page NOT LIKE '%/auto-%'
    AND d.page NOT LIKE '%/voiture-%'
  GROUP BY 1
)
SELECT
  r.pg_id,
  r.pg_alias,
  r.micro_seo_len,
  r.has_safe_table,
  r.gatekeeper_score,
  r.bucket_2a,
  COALESCE(gsc.clicks,        0)         AS clicks_28d,
  COALESCE(gsc.impressions,   0)         AS impressions_28d,
  ROUND(COALESCE(gsc.ctr,     0)::numeric, 5) AS ctr_28d,
  ROUND(gsc.position::numeric,   2)      AS position_28d,
  COALESCE(gsc.gsc_url_count, 0)         AS gsc_url_count
FROM r1_slots r
LEFT JOIN gsc_28d gsc ON gsc.pg_id = r.pg_id
ORDER BY COALESCE(gsc.impressions, 0) DESC, r.pg_id;

-- -----------------------------------------------------------------------------
-- Q2 — Bucket A vs B aggregate (one row per bucket)
--
-- Output : 3 rows (A_long, B_short, mid) with totals, used to track Δ on T+30
-- -----------------------------------------------------------------------------

WITH r1_slots AS (
  SELECT
    s.r1s_pg_id AS pg_id,
    CASE
      WHEN LENGTH(s.r1s_micro_seo_block) >= 700 THEN 'A_long'
      WHEN LENGTH(s.r1s_micro_seo_block) <  300 THEN 'B_short'
      ELSE 'mid'
    END AS bucket_2a
  FROM __seo_r1_gamme_slots s
),
gsc_28d AS (
  SELECT
    NULLIF(
      (regexp_match(d.page, '/pieces/[^/]+-(\d+)(?:\.html)?(?:/|$)'))[1],
      ''
    )::int AS pg_id,
    SUM(d.clicks) AS clicks,
    SUM(d.impressions) AS impressions
  FROM __seo_gsc_daily d
  WHERE d.date >= DATE '2026-05-04' - INTERVAL '28 days'
    AND d.date <= DATE '2026-05-04'
    AND d.page LIKE 'https://www.automecanik.com/pieces/%'
    AND d.page NOT LIKE '%/auto-%'
    AND d.page NOT LIKE '%/voiture-%'
  GROUP BY 1
)
SELECT
  r.bucket_2a,
  COUNT(*)                                            AS n_slots,
  COUNT(gsc.pg_id)                                    AS n_with_gsc_data,
  SUM(COALESCE(gsc.clicks, 0))                        AS clicks_28d,
  SUM(COALESCE(gsc.impressions, 0))                   AS impressions_28d,
  CASE WHEN SUM(COALESCE(gsc.impressions, 0)) > 0
    THEN ROUND(
      SUM(COALESCE(gsc.clicks, 0))::numeric
        / SUM(COALESCE(gsc.impressions, 0))::numeric,
      5)
    ELSE 0
  END                                                 AS ctr_28d
FROM r1_slots r
LEFT JOIN gsc_28d gsc ON gsc.pg_id = r.pg_id
GROUP BY r.bucket_2a
ORDER BY r.bucket_2a;
