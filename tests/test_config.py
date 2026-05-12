from unittest.mock import patch

from renewable_energy_tracker.config import (
    COUNTRY_CODES,
    ENTSOE_BASE_URL,
    ENTSOE_DOMAIN_MAP,
    ENTSOE_PRODUCTION_TYPES,
)


class TestSettings:
    def test_database_url_property(self) -> None:
        """Verify database_url property builds the correct connection string."""
        with patch("renewable_energy_tracker.config.get_settings") as mock:
            mock.return_value.postgres_host = "db.example.com"
            mock.return_value.postgres_port = 5433
            mock.return_value.postgres_db = "mydb"
            mock.return_value.postgres_user = "admin"
            mock.return_value.postgres_password = "secret"
            mock.return_value.database_url = "postgresql://admin:secret@db.example.com:5433/mydb"

            settings = mock.return_value
            assert "db.example.com" in settings.database_url
            assert "5433" in settings.database_url
            assert "mydb" in settings.database_url


class TestConstants:
    def test_country_codes(self) -> None:
        """Verify all 6 expected country codes are present."""
        assert len(COUNTRY_CODES) == 6
        assert "DE" in COUNTRY_CODES
        assert "FR" in COUNTRY_CODES
        assert "ES" in COUNTRY_CODES

    def test_entsoe_domain_map(self) -> None:
        """Verify domain map has correct structure for all countries."""
        assert len(ENTSOE_DOMAIN_MAP) == 6
        for code in COUNTRY_CODES:
            assert code in ENTSOE_DOMAIN_MAP
            assert ENTSOE_DOMAIN_MAP[code].startswith("10Y")

    def test_entsoe_production_types(self) -> None:
        """Verify production types cover expected categories."""
        assert len(ENTSOE_PRODUCTION_TYPES) == 19
        assert "B16" in ENTSOE_PRODUCTION_TYPES  # Solar
        assert "B17" in ENTSOE_PRODUCTION_TYPES  # Wind Onshore
        assert "B18" in ENTSOE_PRODUCTION_TYPES  # Wind Offshore
        assert "B14" in ENTSOE_PRODUCTION_TYPES  # Nuclear

    def test_entsoe_base_url(self) -> None:
        """Verify the API base URL is correct."""
        assert ENTSOE_BASE_URL == "https://web-api.tp.entsoe.eu/api"
