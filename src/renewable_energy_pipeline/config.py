from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ember_api_key: str
    duckdb_path: str = "data/renewable_energy.duckdb"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


EMBER_BASE_URL = "https://api.ember-energy.org/v1"

EMBER_ENDPOINTS: dict[str, str] = {
    "generation": "/electricity-generation/monthly",
    "capacity": "/installed-capacity/monthly",
    "demand": "/electricity-demand/monthly",
    "emissions": "/power-sector-emissions/monthly",
    "carbon_intensity": "/carbon-intensity/monthly",
}

SERIES_CATEGORIES: dict[str, list[str]] = {
    "generation": [
        "Bioenergy", "Coal", "Gas", "Hydro", "Nuclear",
        "Other Fossil", "Other Renewables", "Solar", "Wind",
    ],
    "capacity": [
        "Bioenergy", "Coal", "Gas", "Hydro", "Nuclear",
        "Other Fossil", "Other Renewables", "Solar", "Wind",
    ],
    "demand": ["Demand"],
    "emissions": [
        "Bioenergy", "Coal", "Gas", "Other Fossil",
    ],
    "carbon_intensity": ["Carbon Intensity"],
}

EMISSION_FACTORS: dict[str, float] = {
    "Coal": 0.91,
    "Gas": 0.41,
    "Oil": 0.75,
    "Bioenergy": 0.23,
    "Other Fossil": 0.65,
}


def get_settings() -> Settings:
    return Settings()  # ty: ignore[missing-argument]
