{{ config(materialized='table') }}

SELECT
    country_code,
    country_name,
    region,
    DATE_TRUNC('month', period)::DATE AS year_month,
    SUM(demand_twh) * 1000 AS total_demand_mwh,
    ROUND(AVG(demand_twh::double precision)::numeric, 4) * 1000 AS avg_monthly_demand_mwh
FROM {{ ref('stg_monthly_demand') }}
GROUP BY country_code, country_name, region, DATE_TRUNC('month', period)
ORDER BY country_code, year_month