import pytest
from pydantic import ValidationError

from renewable_energy_pipeline.models.energy import EmberRecord


def test_ember_record_valid() -> None:
    record = EmberRecord(
        country_code="DE",
        country_name="Germany",
        year=2024,
        month=6,
        series_name="Solar",
        variable="Generation",
        unit="GWh",
        value=15000.0,
    )
    assert record.country_code == "DE"
    assert record.value == 15000.0


def test_ember_record_invalid_country() -> None:
    with pytest.raises(ValidationError):
        EmberRecord(
            country_code="",
            country_name="Germany",
            year=2024,
            month=6,
            series_name="Solar",
            variable="Generation",
            unit="GWh",
            value=15000.0,
        )


def test_ember_record_invalid_month() -> None:
    with pytest.raises(ValidationError):
        EmberRecord(
            country_code="DE",
            country_name="Germany",
            year=2024,
            month=13,
            series_name="Solar",
            variable="Generation",
            unit="GWh",
            value=15000.0,
        )


def test_ember_record_null_value_ok() -> None:
    record = EmberRecord(
        country_code="DE",
        country_name="Germany",
        year=2024,
        month=6,
        series_name="Solar",
        variable="Generation",
        unit="GWh",
        value=None,
    )
    assert record.value is None