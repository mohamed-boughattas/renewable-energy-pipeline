{{ config(materialized='table') }}

SELECT
    country_code,
    country_name,
    region,
    DATE_TRUNC('month', period)::DATE AS year_month,
    SUM(capacity_gw) FILTER (WHERE category = 'renewable') AS renewable_capacity_gw,
    SUM(capacity_gw) FILTER (WHERE category = 'fossil') AS fossil_capacity_gw,
    SUM(capacity_gw) AS total_capacity_gw,
    ROUND(AVG(CASE WHEN category = 'renewable' THEN capacity_gw::double precision END)::numeric, 4) AS avg_renewable_capacity_gw,
    ROUND(AVG(capacity_gw::double precision)::numeric, 4) AS avg_total_capacity_gw
FROM {{ ref('stg_monthly_capacity') }}
GROUP BY country_code, country_name, region, DATE_TRUNC('month', period)
ORDER BY country_code, year_month