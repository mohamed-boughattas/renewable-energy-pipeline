from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    entsoe_api_key: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "renewable_energy"
    postgres_user: str = "renewable"
    postgres_password: str = "renewable123"
    kestra_url: str = "http://localhost:8080"

    @property
    def database_url(self) -> str:
        """Build PostgreSQL connection URL from settings fields."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


ENTSOE_BASE_URL = "https://web-api.tp.entsoe.eu/api"

COUNTRY_CODES: list[str] = ["DE", "FR", "ES", "DK", "NO", "NL"]

ENTSOE_DOMAIN_MAP: dict[str, str] = {
    "DE": "10Y1001A1001A83F",
    "FR": "10YFR-RTE------C",
    "ES": "10YES-REE------0",
    "DK": "10Y1001A1001A65H",
    "NO": "10YNO-0--------C",
    "NL": "10YNL----------L",
}

ENTSOE_PRODUCTION_TYPES: dict[str, str] = {
    "B01": "Biomass",
    "B02": "Fossil Brown coal/Lignite",
    "B03": "Fossil Coal-derived gas",
    "B04": "Fossil Gas",
    "B05": "Fossil Hard coal",
    "B06": "Fossil Oil",
    "B07": "Fossil Oil shale",
    "B08": "Fossil Peat",
    "B09": "Geothermal",
    "B10": "Hydro Pumped Storage",
    "B11": "Hydro Run-of-river and poundage",
    "B12": "Hydro Water Reservoir",
    "B13": "Marine",
    "B14": "Nuclear",
    "B15": "Other renewable",
    "B16": "Solar",
    "B17": "Wind Onshore",
    "B18": "Wind Offshore",
    "B19": "Other",
}


def get_settings() -> Settings:
    """Return application settings loaded from environment and .env file.

    Returns:
        Settings: Configured settings instance with values from environment
            variables or .env file.

    Raises:
        pydantic.ValidationError: If ENTSOE_API_KEY is not set.
    """
    return Settings()  # ty: ignore[missing-argument]
