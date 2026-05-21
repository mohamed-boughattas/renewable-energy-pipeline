{{ config(materialized='table') }}

SELECT
    country_code,
    country_name,
    region,
    DATE_TRUNC('month', period)::DATE AS year_month,
    SUM(demand_twh) AS total_demand_gwh,
    ROUND(AVG(demand_twh::double precision)::numeric, 4) AS avg_monthly_demand_gwh
FROM {{ ref('stg_monthly_demand') }}
GROUP BY country_code, country_name, region, DATE_TRUNC('month', period)
ORDER BY country_code, year_month