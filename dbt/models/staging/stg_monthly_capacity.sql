{{ config(materialized='view') }}

SELECT
    md5(rmc.country_code || rmc.series_name || rmc.year::text || rmc.month::text)::uuid AS id,
    rmc.country_code,
    c.name AS country_name,
    c.region,
    rmc.series_name AS source_series,
    es.name AS source_name,
    es.category,
    MAKE_DATE(rmc.year, rmc.month, 1) AS period,
    rmc.value AS capacity_gw,
    rmc.fetched_at
FROM {{ source('raw', 'raw_monthly_capacity') }} rmc
INNER JOIN {{ ref('countries') }} c ON rmc.country_code = c.code
INNER JOIN {{ ref('energy_sources') }} es ON rmc.series_name = es.code
WHERE rmc.is_aggregate_series = false
  AND rmc.country_code IS NOT NULL
  AND rmc.value IS NOT NULL