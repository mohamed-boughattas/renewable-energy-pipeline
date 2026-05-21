{{ config(materialized='view') }}

SELECT
    md5(rmc.country_code || rmc.source_series || rmc.period::text)::uuid AS id,
    rmc.country_code,
    c.name AS country_name,
    c.region,
    rmc.source_series,
    es.name AS source_name,
    es.category,
    rmc.period,
    rmc.capacity_gw,
    rmc.capacity_w_per_capita,
    rmc.is_aggregate_entity,
    rmc.is_aggregate_series,
    rmc.fetched_at
FROM {{ source('raw', 'raw_monthly_capacity') }} rmc
INNER JOIN {{ ref('countries') }} c ON rmc.country_code = c.code
INNER JOIN {{ ref('energy_sources') }} es ON rmc.source_series = es.code