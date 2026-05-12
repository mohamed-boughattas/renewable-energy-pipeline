{% macro co2_avoided(renewable_mwh_column) %}
    {{ renewable_mwh_column }} * {{ var('grid_avg_emission_factor', 0.45) }}
{% endmacro %}
