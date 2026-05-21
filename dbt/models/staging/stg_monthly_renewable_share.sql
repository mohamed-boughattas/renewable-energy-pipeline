{{ config(materialized='view') }}

WITH monthly_totals AS (
    SELECT
        country_code,
        country_name,
        region,
        period,
        SUM(generation_twh) FILTER (WHERE category = 'renewable') AS renewable_twh,
        SUM(generation_twh) FILTER (WHERE category = 'fossil') AS fossil_twh,
        SUM(generation_twh) FILTER (WHERE category = 'nuclear') AS nuclear_twh,
        SUM(generation_twh) AS total_twh
    FROM {{ ref('stg_monthly_generation') }}
    GROUP BY country_code, country_name, region, period
)

SELECT
    country_code,
    country_name,
    region,
    period,
    renewable_twh,
    fossil_twh,
    nuclear_twh,
    total_twh,
    CASE
        WHEN total_twh > 0
        THEN ROUND(((renewable_twh::numeric / total_twh::numeric) * 100), 2)
        ELSE 0
    END AS renewable_share_pct
FROM monthly_totals