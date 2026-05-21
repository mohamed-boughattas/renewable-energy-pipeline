{{ config(materialized='table') }}

WITH fossil_baseline AS (
    SELECT
        country_code,
        country_name,
        region,
        year_month,
        total_renewable_gwh,
        {{ co2_avoided('total_renewable_gwh') }} AS co2_avoided_tons
    FROM {{ ref('mart_monthly_production_summary') }}
)

SELECT
    country_code,
    country_name,
    region,
    year_month,
    total_renewable_gwh,
    co2_avoided_tons,
    ROUND((co2_avoided_tons / 4.6)::numeric, 0) AS equivalent_cars_removed,
    ROUND((co2_avoided_tons / 0.021)::numeric, 0) AS equivalent_trees_planted
FROM fossil_baseline
ORDER BY country_code, year_month