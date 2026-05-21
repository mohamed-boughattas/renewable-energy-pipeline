{{ config(materialized='view') }}

SELECT
    md5(rme.country_code || rme.source_series || rme.period::text)::uuid AS id,
    rme.country_code,
    c.name AS country_name,
    c.region,
    rme.source_series,
    es.name AS source_name,
    es.category,
    rme.period,
    rme.emissions_mtco2,
    rme.share_of_emissions_pct,
    rme.is_aggregate_entity,
    rme.is_aggregate_series,
    rme.fetched_at
FROM {{ source('raw', 'raw_monthly_emissions') }} rme
INNER JOIN {{ ref('countries') }} c ON rme.country_code = c.code
INNER JOIN {{ ref('energy_sources') }} es ON rme.source_series = es.code