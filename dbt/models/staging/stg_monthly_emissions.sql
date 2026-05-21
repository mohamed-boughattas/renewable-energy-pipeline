{{ config(materialized='view') }}

SELECT
    md5(rme.country_code || rme.series_name || rme.year::text || rme.month::text)::uuid AS id,
    rme.country_code,
    c.name AS country_name,
    c.region,
    rme.series_name AS source_series,
    es.name AS source_name,
    es.category,
    MAKE_DATE(rme.year, rme.month, 1) AS period,
    rme.value AS emissions_mtco2,
    rme.fetched_at
FROM {{ source('raw', 'raw_monthly_emissions') }} rme
INNER JOIN {{ ref('countries') }} c ON rme.country_code = c.code
INNER JOIN {{ ref('energy_sources') }} es ON rme.series_name = es.code
WHERE rme.is_aggregate_series = false
  AND rme.country_code IS NOT NULL
  AND rme.value IS NOT NULL