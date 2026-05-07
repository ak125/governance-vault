-- =============================================================================
-- ADR-041 — Baseline T0 GSC snapshot 2026-05-06 (CORRECTED 2026-05-07)
-- =============================================================================
-- Read-only. Joins __seo_gsc_daily × __seo_r1_gamme_slots × pieces_gamme.
-- 28-day rolling window ending 2026-05-04 (GSC T-2 lag).
--
-- ⚠️ FILTRE URL — IMPORTANT
-- Pages R1 PURES = `/pieces/{slug}-{pg_id}.html` (un seul segment après /pieces/,
-- terminant par .html, sans hierarchy de véhicule).
-- Pages R8 (vehicle-scoped) = `/pieces/{slug}-{pg_id}/{marque}-{id}/{modele}-{id}/{type}-{id}.html`
-- Le pattern ANCRÉ `^...$` exclut R8 même si pg_id matche.
--
-- Le 1er snapshot (avant correction 2026-05-07) utilisait un filtre LIKE qui
-- agrégait par erreur les URLs R8 sous le pg_id R1 → CTR/impressions sur-estimés.
--
-- Run:
--   psql "$DATABASE_URL" -f 03-baseline-snapshot.sql
--   # ou via Supabase MCP execute_sql, query block at a time.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Q1 — Aggregate baseline 28d rolling per pg_id (R1 PURE only)
--
-- Output : 169 rows (one per R1 slot), with GSC metrics or 0 if no R1 traffic.
-- -----------------------------------------------------------------------------

WITH r1_slots AS (
  SELECT
    s.r1s_pg_id::text AS pg_id,
    g.pg_alias        AS pg_alias,
    LENGTH(s.r1s_micro_seo_block) AS micro_seo_len,
    (s.r1s_safe_table_rows IS NOT NULL
       AND jsonb_array_length(s.r1s_safe_table_rows) > 0) AS has_safe_table,
    s.r1s_gatekeeper_score AS gatekeeper_score,
    CASE
      WHEN LENGTH(s.r1s_micro_seo_block) >= 700 THEN 'A_long'
      WHEN LENGTH(s.r1s_micro_seo_block) <  300 THEN 'B_short'
      ELSE 'mid'
    END AS bucket_2a
  FROM __seo_r1_gamme_slots s
  LEFT JOIN pieces_gamme g ON g.pg_id::text = s.r1s_pg_id::text
),
gsc_28d_r1_pure AS (
  SELECT
    -- ANCRÉ `^...$` : exactement 1 segment apres /pieces/, terminant en .html
    (regexp_match(d.page, '^https://www\.automecanik\.com/pieces/[^/]+-(\d+)\.html$'))[1] AS pg_id,
    SUM(d.clicks)        AS clicks,
    SUM(d.impressions)   AS impressions,
    CASE WHEN SUM(d.impressions) > 0
      THEN SUM(d.clicks)::numeric / SUM(d.impressions)::numeric
      ELSE 0
    END AS ctr,
    CASE WHEN SUM(d.impressions) > 0
      THEN SUM(d.position * d.impressions)::numeric / SUM(d.impressions)::numeric
      ELSE NULL
    END AS position,
    COUNT(DISTINCT d.page) AS gsc_url_count
  FROM __seo_gsc_daily d
  WHERE d.date >= DATE '2026-05-04' - INTERVAL '28 days'
    AND d.date <= DATE '2026-05-04'
    AND d.page ~ '^https://www\.automecanik\.com/pieces/[^/]+\.html$'
  GROUP BY 1
)
SELECT
  r.pg_id,
  r.pg_alias,
  r.micro_seo_len,
  r.has_safe_table,
  r.gatekeeper_score,
  r.bucket_2a,
  COALESCE(gsc.clicks,        0)              AS clicks_28d,
  COALESCE(gsc.impressions,   0)              AS impressions_28d,
  ROUND(COALESCE(gsc.ctr,     0)::numeric, 5) AS ctr_28d,
  ROUND(gsc.position::numeric,   2)           AS position_28d,
  COALESCE(gsc.gsc_url_count, 0)              AS gsc_url_count
FROM r1_slots r
LEFT JOIN gsc_28d_r1_pure gsc ON gsc.pg_id = r.pg_id
ORDER BY COALESCE(gsc.impressions, 0) DESC, r.pg_id;

-- -----------------------------------------------------------------------------
-- Q2 — Bucket A vs B aggregate (R1 PURE only)
--
-- Output : 3 rows (A_long, B_short, mid).
-- -----------------------------------------------------------------------------

WITH r1_slots AS (
  SELECT
    s.r1s_pg_id::text AS pg_id,
    CASE
      WHEN LENGTH(s.r1s_micro_seo_block) >= 700 THEN 'A_long'
      WHEN LENGTH(s.r1s_micro_seo_block) <  300 THEN 'B_short'
      ELSE 'mid'
    END AS bucket_2a
  FROM __seo_r1_gamme_slots s
),
gsc_28d_r1_pure AS (
  SELECT
    (regexp_match(d.page, '^https://www\.automecanik\.com/pieces/[^/]+-(\d+)\.html$'))[1] AS pg_id,
    SUM(d.clicks) AS clicks,
    SUM(d.impressions) AS impressions
  FROM __seo_gsc_daily d
  WHERE d.date >= DATE '2026-05-04' - INTERVAL '28 days'
    AND d.date <= DATE '2026-05-04'
    AND d.page ~ '^https://www\.automecanik\.com/pieces/[^/]+\.html$'
  GROUP BY 1
)
SELECT
  r.bucket_2a,
  COUNT(*)                          AS n_slots,
  COUNT(gsc.pg_id)                  AS n_with_gsc,
  SUM(COALESCE(gsc.clicks, 0))      AS clicks_28d,
  SUM(COALESCE(gsc.impressions, 0)) AS impressions_28d,
  CASE WHEN SUM(COALESCE(gsc.impressions, 0)) > 0
    THEN ROUND(SUM(COALESCE(gsc.clicks, 0))::numeric / SUM(COALESCE(gsc.impressions, 0))::numeric, 5)
    ELSE 0
  END                               AS ctr_28d
FROM r1_slots r
LEFT JOIN gsc_28d_r1_pure gsc ON gsc.pg_id = r.pg_id
GROUP BY r.bucket_2a
ORDER BY r.bucket_2a;
