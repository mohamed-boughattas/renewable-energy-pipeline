SELECT *
FROM {{ ref('gld_monthly_production_summary') }}
WHERE total_production_mwh < 0
