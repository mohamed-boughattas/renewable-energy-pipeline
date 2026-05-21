SELECT *
FROM {{ ref('mart_monthly_production_summary') }}
WHERE total_production_gwh < 0
