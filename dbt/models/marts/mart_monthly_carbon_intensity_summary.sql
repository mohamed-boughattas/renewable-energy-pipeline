{{ config(materialized='table') }}

SELECT
    country_code,
    country_name,
    region,
    DATE_TRUNC('month', period)::DATE AS year_month,
    ROUND(AVG(emissions_intensity_gco2_per_kwh::double precision)::numeric, 4) AS avg_intensity_gco2_per_kwh,
    MIN(emissions_intensity_gco2_per_kwh) AS min_intensity_gco2_per_kwh,
    MAX(emissions_intensity_gco2_per_kwh) AS max_intensity_gco2_per_kwh
FROM {{ ref('stg_monthly_carbon_intensity') }}
GROUP BY country_code, country_name, region, DATE_TRUNC('month', period)
ORDER BY country_code, year_month