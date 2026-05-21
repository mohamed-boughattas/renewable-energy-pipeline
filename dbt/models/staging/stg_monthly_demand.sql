{{ config(materialized='view') }}

SELECT
    md5(rmd.country_code || rmd.year::text || rmd.month::text)::uuid AS id,
    rmd.country_code,
    c.name AS country_name,
    c.region,
    MAKE_DATE(rmd.year, rmd.month, 1) AS period,
    rmd.value AS demand_twh,
    rmd.is_aggregate_series AS is_aggregate_entity,
    rmd.fetched_at
FROM {{ source('raw', 'raw_monthly_demand') }} rmd
INNER JOIN {{ ref('countries') }} c ON rmd.country_code = c.code
WHERE rmd.is_aggregate_series = false
  AND rmd.country_code IS NOT NULL
  AND rmd.value IS NOT NULL