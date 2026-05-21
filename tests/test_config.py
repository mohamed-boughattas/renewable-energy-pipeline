from renewable_energy_pipeline.config import (
    EMBER_BASE_URL,
    EMBER_ENDPOINTS,
    EMISSION_FACTORS,
    SERIES_CATEGORIES,
)


def test_ember_base_url() -> None:
    assert EMBER_BASE_URL == "https://api.ember-energy.org/v1"


def test_ember_endpoints() -> None:
    assert len(EMBER_ENDPOINTS) == 5
    for category in ["generation", "capacity", "demand", "emissions", "carbon_intensity"]:
        assert category in EMBER_ENDPOINTS
        assert EMBER_ENDPOINTS[category].startswith("/")


def test_series_categories() -> None:
    assert "generation" in SERIES_CATEGORIES
    assert "capacity" in SERIES_CATEGORIES
    assert "demand" in SERIES_CATEGORIES
    assert "emissions" in SERIES_CATEGORIES
    assert "carbon_intensity" in SERIES_CATEGORIES
    assert "Solar" in SERIES_CATEGORIES["generation"]
    assert "Wind" in SERIES_CATEGORIES["generation"]


def test_emission_factors() -> None:
    assert "Coal" in EMISSION_FACTORS
    assert "Gas" in EMISSION_FACTORS
    assert EMISSION_FACTORS["Coal"] > EMISSION_FACTORS["Gas"]