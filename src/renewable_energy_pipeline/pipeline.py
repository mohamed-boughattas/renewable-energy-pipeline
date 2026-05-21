import logging
from collections.abc import Iterator
from datetime import datetime
from typing import Any

import dlt
from dlt.sources.helpers import requests

from renewable_energy_pipeline.config import EMBER_BASE_URL, EMBER_ENDPOINTS


def _parse_date(date_str: str) -> tuple[int, int]:
    parts = date_str.split("-")
    return int(parts[0]), int(parts[1])


def _fetch_generation(api_key: str) -> Iterator[dict]:
    url = f"{EMBER_BASE_URL}{EMBER_ENDPOINTS['generation']}"
    params = {"api_key": api_key}
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    for rec in data.get("data", []):
        entity_code = rec.get("entity_code")
        if not entity_code:
            continue
        year, month = _parse_date(rec["date"])
        yield {
            "country_code": entity_code,
            "country_name": rec.get("entity", ""),
            "year": year,
            "month": month,
            "series_name": rec.get("series") or "",
            "value": rec.get("generation_twh"),
            "is_aggregate_series": rec.get("is_aggregate_series", False),
            "fetched_at": datetime.now().isoformat(),
        }


def _fetch_capacity(api_key: str) -> Iterator[dict]:
    url = f"{EMBER_BASE_URL}{EMBER_ENDPOINTS['capacity']}"
    params = {"api_key": api_key}
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    for rec in data.get("data", []):
        entity_code = rec.get("entity_code")
        if not entity_code:
            continue
        year, month = _parse_date(rec["date"])
        yield {
            "country_code": entity_code,
            "country_name": rec.get("entity", ""),
            "year": year,
            "month": month,
            "series_name": rec.get("series") or "",
            "value": rec.get("capacity_gw"),
            "is_aggregate_series": rec.get("is_aggregate_series", False),
            "fetched_at": datetime.now().isoformat(),
        }


def _fetch_demand(api_key: str) -> Iterator[dict]:
    url = f"{EMBER_BASE_URL}{EMBER_ENDPOINTS['demand']}"
    params = {"api_key": api_key}
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    for rec in data.get("data", []):
        entity_code = rec.get("entity_code")
        if not entity_code:
            continue
        year, month = _parse_date(rec["date"])
        yield {
            "country_code": entity_code,
            "country_name": rec.get("entity", ""),
            "year": year,
            "month": month,
            "series_name": "Demand",
            "value": rec.get("demand_twh"),
            "is_aggregate_series": rec.get("is_aggregate_series", False),
            "fetched_at": datetime.now().isoformat(),
        }


def _fetch_emissions(api_key: str) -> Iterator[dict]:
    url = f"{EMBER_BASE_URL}{EMBER_ENDPOINTS['emissions']}"
    params = {"api_key": api_key}
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    for rec in data.get("data", []):
        entity_code = rec.get("entity_code")
        if not entity_code:
            continue
        year, month = _parse_date(rec["date"])
        yield {
            "country_code": entity_code,
            "country_name": rec.get("entity", ""),
            "year": year,
            "month": month,
            "series_name": rec.get("series") or "",
            "value": rec.get("emissions_mtco2"),
            "is_aggregate_series": rec.get("is_aggregate_series", False),
            "fetched_at": datetime.now().isoformat(),
        }


def _fetch_carbon_intensity(api_key: str) -> Iterator[dict]:
    url = f"{EMBER_BASE_URL}{EMBER_ENDPOINTS['carbon_intensity']}"
    params = {"api_key": api_key}
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    for rec in data.get("data", []):
        entity_code = rec.get("entity_code")
        if not entity_code:
            continue
        year, month = _parse_date(rec["date"])
        yield {
            "country_code": entity_code,
            "country_name": rec.get("entity", ""),
            "year": year,
            "month": month,
            "series_name": "Carbon Intensity",
            "value": rec.get("emissions_intensity_gco2_per_kwh"),
            "is_aggregate_series": rec.get("is_aggregate_series", False),
            "fetched_at": datetime.now().isoformat(),
        }


@dlt.source
def ember_source(api_key: str = dlt.secrets.value) -> Any:
    @dlt.resource(
        name="raw_monthly_generation",
        write_disposition={"disposition": "merge", "strategy": "upsert"},
        primary_key=("country_code", "series_name", "year", "month"),
    )
    def fetch_generation() -> Iterator[dict]:
        yield from _fetch_generation(api_key)

    @dlt.resource(
        name="raw_monthly_capacity",
        write_disposition={"disposition": "merge", "strategy": "upsert"},
        primary_key=("country_code", "series_name", "year", "month"),
    )
    def fetch_capacity() -> Iterator[dict]:
        yield from _fetch_capacity(api_key)

    @dlt.resource(
        name="raw_monthly_demand",
        write_disposition={"disposition": "merge", "strategy": "upsert"},
        primary_key=("country_code", "year", "month"),
    )
    def fetch_demand() -> Iterator[dict]:
        yield from _fetch_demand(api_key)

    @dlt.resource(
        name="raw_monthly_emissions",
        write_disposition={"disposition": "merge", "strategy": "upsert"},
        primary_key=("country_code", "series_name", "year", "month"),
    )
    def fetch_emissions() -> Iterator[dict]:
        yield from _fetch_emissions(api_key)

    @dlt.resource(
        name="raw_monthly_carbon_intensity",
        write_disposition={"disposition": "merge", "strategy": "upsert"},
        primary_key=("country_code", "year", "month"),
    )
    def fetch_carbon_intensity() -> Iterator[dict]:
        yield from _fetch_carbon_intensity(api_key)

    return [
        fetch_generation,
        fetch_capacity,
        fetch_demand,
        fetch_emissions,
        fetch_carbon_intensity,
    ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    pipeline = dlt.pipeline(
        pipeline_name="ember_energy",
        destination="duckdb",
        dataset_name="main",
        pipelines_dir=".dlt/pipelines",
    )

    load_info = pipeline.run(ember_source())
    print(load_info)