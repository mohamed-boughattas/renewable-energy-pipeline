from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_settings_env() -> Iterator[MagicMock]:
    mock_settings = MagicMock()
    mock_settings.ember_api_key = "test_api_key"
    mock_settings.duckdb_path = "data/test_renewable_energy.duckdb"
    with patch("renewable_energy_pipeline.config.get_settings", return_value=mock_settings):
        yield mock_settings
