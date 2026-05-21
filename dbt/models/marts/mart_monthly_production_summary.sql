{{ config(materialized='table') }}

SELECT
    country_code,
    country_name,
    region,
    DATE_TRUNC('month', period)::DATE AS year_month,
    SUM(renewable_twh) AS total_renewable_gwh,
    SUM(fossil_twh) AS total_fossil_gwh,
    SUM(nuclear_twh) AS total_nuclear_gwh,
    SUM(total_twh) AS total_production_gwh,
    ROUND(AVG(renewable_twh::double precision)::numeric, 4) AS avg_monthly_renewable_twh,
    ROUND(AVG(fossil_twh::double precision)::numeric, 4) AS avg_monthly_fossil_twh,
    ROUND(AVG(total_twh::double precision)::numeric, 4) AS avg_monthly_total_twh,
    ROUND(AVG(renewable_share_pct::double precision)::numeric, 2) AS renewable_share_pct
FROM {{ ref('stg_monthly_renewable_share') }}
GROUP BY country_code, country_name, region, DATE_TRUNC('month', period)
ORDER BY country_code, year_month