{{ config(materialized='view') }}

WITH daily_totals AS (
    SELECT
        country_code,
        country_name,
        region,
        production_date,
        SUM(production_mwh) FILTER (WHERE category = 'renewable') AS renewable_mwh,
        SUM(production_mwh) FILTER (WHERE category = 'fossil') AS fossil_mwh,
        SUM(production_mwh) FILTER (WHERE category = 'nuclear') AS nuclear_mwh,
        SUM(production_mwh) AS total_mwh
    FROM {{ ref('slv_daily_production') }}
    GROUP BY country_code, country_name, region, production_date
)

SELECT
    country_code,
    country_name,
    region,
    production_date,
    renewable_mwh,
    fossil_mwh,
    nuclear_mwh,
    total_mwh,
    CASE
        WHEN total_mwh > 0
        THEN ROUND((renewable_mwh / total_mwh) * 100, 2)
        ELSE 0
    END AS renewable_share_pct
FROM daily_totals
