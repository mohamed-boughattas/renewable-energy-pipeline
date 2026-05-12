from datetime import date

import pandas as pd
import pandera.pandas as pa
import pytest
from pydantic import ValidationError

from renewable_energy_tracker.models.energy import ProductionRecord
from renewable_energy_tracker.models.schemas import daily_production_schema


def test_production_record_valid() -> None:
    """Verify ProductionRecord accepts valid fields."""
    record = ProductionRecord(
        country_code="DE",
        source_code="B16",
        production_date=date(2024, 6, 1),
        production_mwh=15000.0,
    )
    assert record.country_code == "DE"
    assert record.production_mwh == 15000.0


def test_production_record_invalid_country() -> None:
    """Verify ProductionRecord rejects an invalid country_code."""
    with pytest.raises(ValidationError):
        ProductionRecord(
            country_code="INVALID",
            source_code="B16",
            production_date=date(2024, 6, 1),
            production_mwh=15000.0,
        )


def test_production_record_negative_production() -> None:
    """Verify ProductionRecord rejects negative production_mwh."""
    with pytest.raises(ValidationError):
        ProductionRecord(
            country_code="DE",
            source_code="B16",
            production_date=date(2024, 6, 1),
            production_mwh=-100.0,
        )


def test_daily_production_payload(sample_production_data: pd.DataFrame) -> None:
    """Verify daily_production_schema validates a known-good DataFrame.

    Args:
        sample_production_data: Fixture with five valid production rows.
    """
    validated = daily_production_schema.validate(sample_production_data)
    assert len(validated) == 5


def test_pandera_rejects_invalid_country() -> None:
    """Verify pandera schema rejects an unknown country_code."""
    df = pd.DataFrame(
        {
            "country_code": ["XX"],
            "source_code": ["B16"],
            "production_date": pd.to_datetime(["2024-06-01"]),
            "production_mwh": [100.0],
        }
    )
    with pytest.raises(pa.errors.SchemaError):
        daily_production_schema.validate(df)


def test_pandera_rejects_negative_production() -> None:
    """Verify pandera schema rejects negative production_mwh."""
    df = pd.DataFrame(
        {
            "country_code": ["DE"],
            "source_code": ["B16"],
            "production_date": pd.to_datetime(["2024-06-01"]),
            "production_mwh": [-100.0],
        }
    )
    with pytest.raises(pa.errors.SchemaError):
        daily_production_schema.validate(df)
