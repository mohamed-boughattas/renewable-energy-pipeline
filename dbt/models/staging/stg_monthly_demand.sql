{{ config(materialized='view') }}

SELECT
    md5(rmd.country_code || rmd.period::text)::uuid AS id,
    rmd.country_code,
    c.name AS country_name,
    c.region,
    rmd.period,
    rmd.demand_twh,
    rmd.is_aggregate_entity,
    rmd.fetched_at
FROM {{ source('raw', 'raw_monthly_demand') }} rmd
INNER JOIN {{ ref('countries') }} c ON rmd.country_code = c.code