{{ config(materialized='table') }}

WITH country_stats AS (
    SELECT
        country_code,
        country_name,
        region,
        ROUND(AVG(renewable_share_pct::double precision)::numeric, 2) AS avg_renewable_share_pct,
        ROUND(AVG(total_production_gwh::double precision)::numeric, 2) AS avg_monthly_production_gwh,
        SUM(total_production_gwh) AS total_production_gwh,
        SUM(total_renewable_gwh) AS total_renewable_gwh
    FROM {{ ref('mart_monthly_production_summary') }}
    GROUP BY country_code, country_name, region
)

SELECT
    country_code,
    country_name,
    region,
    avg_renewable_share_pct,
    avg_monthly_production_gwh,
    total_production_gwh,
    total_renewable_gwh,
    RANK() OVER (ORDER BY avg_renewable_share_pct DESC) AS rank_renewable_share,
    RANK() OVER (ORDER BY total_renewable_gwh DESC) AS rank_total_renewable
FROM country_stats
ORDER BY avg_renewable_share_pct DESC