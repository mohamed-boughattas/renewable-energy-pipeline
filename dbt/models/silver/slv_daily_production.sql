{{ config(materialized='view') }}

SELECT
    rdp.id,
    rdp.country_code,
    c.name AS country_name,
    c.region,
    rdp.source_code,
    es.name AS source_name,
    es.category,
    rdp.production_date,
    rdp.production_mwh,
    rdp.fetched_at
FROM {{ source('raw', 'raw_daily_production') }} rdp
INNER JOIN {{ ref('countries') }} c ON rdp.country_code = c.code
INNER JOIN {{ ref('energy_sources') }} es ON rdp.source_code = es.code
