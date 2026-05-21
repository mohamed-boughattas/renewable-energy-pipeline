import logging
from collections.abc import Iterator
from datetime import datetime
from typing import Any

import dlt
from dlt.sources.helpers import requests

from renewable_energy_pipeline.config import EMBER_BASE_URL, EMBER_ENDPOINTS


@dlt.source
def ember_source(api_key: str = dlt.secrets.value) -> Any:
    @dlt.resource(
        name="raw_monthly_generation",
        write_disposition={"disposition": "merge", "strategy": "upsert"},
        primary_key=("country_code", "series_name", "year", "month"),
    )
    def fetch_generation() -> Iterator[dict]:
        yield from _fetch_category("generation", api_key)

    @dlt.resource(
        name="raw_monthly_capacity",
        write_disposition={"disposition": "merge", "strategy": "upsert"},
        primary_key=("country_code", "series_name", "year", "month"),
    )
    def fetch_capacity() -> Iterator[dict]:
        yield from _fetch_category("capacity", api_key)

    @dlt.resource(
        name="raw_monthly_demand",
        write_disposition={"disposition": "merge", "strategy": "upsert"},
        primary_key=("country_code", "series_name", "year", "month"),
    )
    def fetch_demand() -> Iterator[dict]:
        yield from _fetch_category("demand", api_key)

    @dlt.resource(
        name="raw_monthly_emissions",
        write_disposition={"disposition": "merge", "strategy": "upsert"},
        primary_key=("country_code", "series_name", "year", "month"),
    )
    def fetch_emissions() -> Iterator[dict]:
        yield from _fetch_category("emissions", api_key)

    @dlt.resource(
        name="raw_monthly_carbon_intensity",
        write_disposition={"disposition": "merge", "strategy": "upsert"},
        primary_key=("country_code", "series_name", "year", "month"),
    )
    def fetch_carbon_intensity() -> Iterator[dict]:
        yield from _fetch_category("carbon_intensity", api_key)

    return [
        fetch_generation,
        fetch_capacity,
        fetch_demand,
        fetch_emissions,
        fetch_carbon_intensity,
    ]


def _fetch_category(category: str, api_key: str) -> Iterator[dict]:
    endpoint = EMBER_ENDPOINTS[category]
    url = f"{EMBER_BASE_URL}{endpoint}"
    params = {"api_key": api_key}
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()

    for rec in data.get("data", []):
        yield {
            "country_code": rec.get("country_code", ""),
            "country_name": rec.get("country_name", ""),
            "year": rec.get("year", 0),
            "month": rec.get("month", 0),
            "series_name": rec.get("series_name", ""),
            "variable": rec.get("variable", ""),
            "unit": rec.get("unit", ""),
            "value": rec.get("value"),
            "is_aggregate_series": rec.get("is_aggregate_series", False),
            "fetched_at": datetime.now().isoformat(),
        }


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