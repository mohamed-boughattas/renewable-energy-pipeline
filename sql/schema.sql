CREATE TABLE IF NOT EXISTS countries (
    code VARCHAR(2) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS energy_sources (
    code VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(20) NOT NULL
        CHECK (category IN ('renewable', 'fossil', 'nuclear', 'other'))
);

CREATE TABLE IF NOT EXISTS emission_factors (
    source_code VARCHAR(50) PRIMARY KEY REFERENCES energy_sources(code),
    co2_factor_tons_per_mwh NUMERIC(6, 4) NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_daily_production (
    id BIGSERIAL PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL REFERENCES countries(code),
    source_code VARCHAR(50) NOT NULL REFERENCES energy_sources(code),
    production_date DATE NOT NULL,
    production_mwh NUMERIC(12, 2) NOT NULL,
    fetched_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (country_code, source_code, production_date)
);

CREATE INDEX IF NOT EXISTS idx_raw_production_date ON raw_daily_production(production_date);
CREATE INDEX IF NOT EXISTS idx_raw_production_country ON raw_daily_production(country_code);
CREATE INDEX IF NOT EXISTS idx_raw_production_source ON raw_daily_production(source_code);
