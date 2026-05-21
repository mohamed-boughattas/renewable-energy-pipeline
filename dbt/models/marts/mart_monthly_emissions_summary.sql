{{ config(materialized='table') }}

SELECT
    country_code,
    country_name,
    region,
    DATE_TRUNC('month', period)::DATE AS year_month,
    SUM(emissions_mtco2) FILTER (WHERE category = 'fossil') AS fossil_emissions_mtco2,
    SUM(emissions_mtco2) AS total_emissions_mtco2,
    ROUND(AVG(CASE WHEN category = 'fossil' THEN emissions_mtco2::double precision END)::numeric, 4) AS avg_fossil_emissions_mtco2,
    ROUND(AVG(emissions_mtco2::double precision)::numeric, 4) AS avg_total_emissions_mtco2
FROM {{ ref('stg_monthly_emissions') }}
GROUP BY country_code, country_name, region, DATE_TRUNC('month', period)
ORDER BY country_code, year_month