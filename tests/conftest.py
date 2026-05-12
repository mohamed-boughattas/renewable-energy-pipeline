from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def mock_settings_env() -> Iterator[MagicMock]:
    """Mock get_settings to avoid requiring a .env file in tests.

    Yields:
        MagicMock: The mocked settings instance.
    """
    mock_settings = MagicMock()
    mock_settings.entsoe_api_key = "test_api_key"
    mock_settings.postgres_host = "localhost"
    mock_settings.postgres_port = 5432
    mock_settings.postgres_db = "test_db"
    mock_settings.postgres_user = "test_user"
    mock_settings.postgres_password = "test_pass"
    mock_settings.database_url = "postgresql://test_user:test_pass@localhost:5432/test_db"
    with patch("renewable_energy_tracker.config.get_settings", return_value=mock_settings):
        yield mock_settings


@pytest.fixture
def sample_production_data() -> pd.DataFrame:
    """Provide a sample DataFrame representing ENTSO-E production data.

    Returns:
        pd.DataFrame: Sample production data with columns country_code,
            source_code, production_date, and production_mwh.
    """
    return pd.DataFrame(
        {
            "country_code": ["DE", "DE", "FR", "FR", "ES"],
            "source_code": ["B16", "B17", "B04", "B16", "B17"],
            "production_date": pd.to_datetime(
                ["2024-06-01", "2024-06-01", "2024-06-01", "2024-06-01", "2024-06-01"]
            ),
            "production_mwh": [15000.0, 22000.0, 30000.0, 12000.0, 18000.0],
        }
    )


@pytest.fixture
def sample_xml_response() -> str:
    """Provide a sample ENTSO-E XML response for testing.

    Returns:
        str: A minimal valid ENTSO-E XML document with two TimeSeries entries.
    """
    return """<?xml version="1.0" encoding="UTF-8"?>
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:generationdocument:7:0">
    <TimeSeries>
        <MktPSRType>
            <psrType>B16</psrType>
        </MktPSRType>
        <Period>
            <timeInterval>
                <start>2024-06-01T00:00Z</start>
                <end>2024-06-02T00:00Z</end>
            </timeInterval>
            <Point>
                <position>1</position>
                <quantity>15000</quantity>
            </Point>
        </Period>
    </TimeSeries>
    <TimeSeries>
        <MktPSRType>
            <psrType>B17</psrType>
        </MktPSRType>
        <Period>
            <timeInterval>
                <start>2024-06-01T00:00Z</start>
                <end>2024-06-02T00:00Z</end>
            </timeInterval>
            <Point>
                <position>1</position>
                <quantity>22000</quantity>
            </Point>
        </Period>
    </TimeSeries>
</GL_MarketDocument>"""
