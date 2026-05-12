from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


@pytest.fixture
def sample_production_data() -> pd.DataFrame:
    """Provide a sample DataFrame for load tests.

    Returns:
        pd.DataFrame: Sample production data with known values.
    """
    return pd.DataFrame(
        {
            "country_code": ["DE", "DE", "FR", "FR", "ES"],
            "source_code": ["B16", "B17", "B04", "B16", "B17"],
            "production_date": pd.to_datetime(
                ["2024-06-01", "2024-06-01", "2024-06-01", "2024-06-01", "2024-06-01"],
            ),
            "production_mwh": [15000.0, 22000.0, 30000.0, 12000.0, 18000.0],
        }
    )


def test_load_dataframe_empty() -> None:
    """Verify DbConnection.get_connection delegates to _get_pool."""
    from renewable_energy_tracker.app.query import DbConnection

    with patch.object(DbConnection, "_get_pool") as mock_pool:
        mock_conn = MagicMock()
        mock_conn.closed = False
        mock_pool.return_value.getconn.return_value = mock_conn

        conn = DbConnection.get_connection()
        assert conn is mock_conn
