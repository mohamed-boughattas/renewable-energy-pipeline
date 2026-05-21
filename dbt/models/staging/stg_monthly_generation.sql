{{ config(materialized='view') }}

SELECT
    md5(rmg.country_code || rmg.series_name || rmg.year::text || rmg.month::text)::uuid AS id,
    rmg.country_code,
    c.name AS country_name,
    c.region,
    rmg.series_name AS source_series,
    es.name AS source_name,
    es.category,
    MAKE_DATE(rmg.year, rmg.month, 1) AS period,
    rmg.value::double AS generation_twh,
    CASE
        WHEN SUM(rmg.value::double) OVER (PARTITION BY rmg.country_code, rmg.year, rmg.month) > 0
        THEN ROUND((rmg.value::double / SUM(rmg.value::double) OVER (PARTITION BY rmg.country_code, rmg.year, rmg.month)) * 100, 2)
        ELSE 0
    END AS share_of_generation_pct,
    rmg.is_aggregate_series,
    rmg.fetched_at
FROM {{ source('raw', 'raw_monthly_generation') }} rmg
INNER JOIN {{ ref('countries') }} c ON rmg.country_code = c.code
INNER JOIN {{ ref('energy_sources') }} es ON rmg.series_name = es.code
WHERE rmg.is_aggregate_series = false
  AND rmg.country_code IS NOT NULL
  AND rmg.value IS NOT NULL