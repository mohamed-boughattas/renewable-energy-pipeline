{{ config(materialized='table') }}

SELECT
    country_code,
    country_name,
    region,
    DATE_TRUNC('month', production_date)::DATE AS year_month,
    SUM(renewable_mwh) AS total_renewable_mwh,
    SUM(fossil_mwh) AS total_fossil_mwh,
    SUM(nuclear_mwh) AS total_nuclear_mwh,
    SUM(total_mwh) AS total_production_mwh,
    ROUND(AVG(renewable_mwh), 2) AS avg_daily_renewable_mwh,
    ROUND(AVG(fossil_mwh), 2) AS avg_daily_fossil_mwh,
    ROUND(AVG(total_mwh), 2) AS avg_daily_total_mwh,
    CASE
        WHEN SUM(total_mwh) > 0
        THEN ROUND((SUM(renewable_mwh) / SUM(total_mwh)) * 100, 2)
        ELSE 0
    END AS renewable_share_pct
FROM {{ ref('slv_daily_renewable_share') }}
GROUP BY country_code, country_name, region, DATE_TRUNC('month', production_date)
ORDER BY country_code, year_month
