{{ config(materialized='view') }}

SELECT
    md5(rmci.country_code || rmci.period::text)::uuid AS id,
    rmci.country_code,
    c.name AS country_name,
    c.region,
    rmci.period,
    rmci.emissions_intensity_gco2_per_kwh,
    rmci.is_aggregate_entity,
    rmci.fetched_at
FROM {{ source('raw', 'raw_monthly_carbon_intensity') }} rmci
INNER JOIN {{ ref('countries') }} c ON rmci.country_code = c.code