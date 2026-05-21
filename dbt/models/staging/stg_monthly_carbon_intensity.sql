{{ config(materialized='view') }}

SELECT
    md5(rmci.country_code || rmci.year::text || rmci.month::text)::uuid AS id,
    rmci.country_code,
    c.name AS country_name,
    c.region,
    MAKE_DATE(rmci.year, rmci.month, 1) AS period,
    rmci.value::double AS emissions_intensity_gco2_per_kwh,
    rmci.fetched_at
FROM {{ source('raw', 'raw_monthly_carbon_intensity') }} rmci
INNER JOIN {{ ref('countries') }} c ON rmci.country_code = c.code
WHERE rmci.country_code IS NOT NULL
  AND rmci.value IS NOT NULL