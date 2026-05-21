{{ config(materialized='view') }}

SELECT
    md5(rmg.country_code || rmg.source_series || rmg.period::text)::uuid AS id,
    rmg.country_code,
    c.name AS country_name,
    c.region,
    rmg.source_series,
    es.name AS source_name,
    es.category,
    rmg.period,
    rmg.generation_twh,
    rmg.share_of_generation_pct,
    rmg.is_aggregate_entity,
    rmg.is_aggregate_series,
    rmg.fetched_at
FROM {{ source('raw', 'raw_monthly_generation') }} rmg
INNER JOIN {{ ref('countries') }} c ON rmg.country_code = c.code
INNER JOIN {{ ref('energy_sources') }} es ON rmg.source_series = es.code