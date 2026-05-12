import logging
from collections.abc import Iterator
from datetime import date, datetime, timedelta
from typing import Any

import dlt
from dlt.sources.helpers import requests
from lxml import etree

from renewable_energy_tracker.config import (
    COUNTRY_CODES,
    ENTSOE_BASE_URL,
    ENTSOE_DOMAIN_MAP,
    ENTSOE_PRODUCTION_TYPES,
)

logger = logging.getLogger(__name__)

NS = {"ns": "urn:iec62325.351:tc57wg16:451-3:generationdocument:7:0"}

_production_incremental = dlt.sources.incremental(
    "production_date",
    initial_value="2024-01-01",
)


@dlt.source
def entsoe_source(api_key: str = dlt.secrets.value) -> Any:
    """Define the dlt source for ENTSO-E energy production data.

    Args:
        api_key: ENTSO-E API security token, sourced from secrets.

    Returns:
        dlt.Resource: A dlt resource that yields production records.
    """
    @dlt.resource(
        name="raw_daily_production",
        write_disposition={"disposition": "merge", "strategy": "upsert"},
        primary_key=("country_code", "source_code", "production_date"),
        columns={
            "country_code": {"data_type": "text", "nullable": False},
            "source_code": {"data_type": "text", "nullable": False},
            "production_date": {"data_type": "date", "nullable": False},
            "production_mwh": {"data_type": "double", "nullable": False},
            "fetched_at": {"data_type": "timestamp", "nullable": False},
        },
    )
    def daily_production(
        last_date: dlt.sources.incremental[date] = _production_incremental,
    ) -> Iterator[dict]:
        """Fetch daily production data for all configured countries.

        Args:
            last_date: Incremental cursor tracking the last fetched date.

        Yields:
            dict: Production record with keys country_code, source_code,
                production_date, production_mwh, and fetched_at.
        """
        for country_code in COUNTRY_CODES:
            domain = ENTSOE_DOMAIN_MAP[country_code]
            target_date = last_date.start_value

            url = _build_url(api_key, domain, target_date)
            logger.info("Fetching ENTSO-E data for %s on %s", country_code, target_date)

            response = requests.get(url, timeout=60)
            response.raise_for_status()

            fetched_at = dlt.current.load_package()["state"]["created_at"]
            records = _parse_xml(response.text, country_code, fetched_at)
            yield from records

    return daily_production


def _build_url(api_key: str, in_domain: str, target_date: date) -> str:
    """Build the ENTSO-E API URL for a given domain and date.

    Args:
        api_key: ENTSO-E API security token.
        in_domain: ENTSO-E domain code (e.g. "10Y1001A1001A83F" for Germany).
        target_date: The date to fetch data for.

    Returns:
        str: The fully constructed API URL.
    """
    params = {
        "securityToken": api_key,
        "documentType": "A73",
        "processType": "A16",
        "in_Domain": in_domain,
        "periodStart": target_date.strftime("%Y%m%d0000"),
        "periodEnd": (target_date + timedelta(days=1)).strftime("%Y%m%d0000"),
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{ENTSOE_BASE_URL}?{query}"


def _parse_xml(xml_content: str, country_code: str, fetched_at: str) -> Iterator[dict]:
    """Parse an ENTSO-E XML response into production record dictionaries.

    Args:
        xml_content: Raw XML string from the ENTSO-E API response.
        country_code: Two-letter country code (e.g. "DE").
        fetched_at: ISO-8601 timestamp of when the data was fetched.

    Yields:
        dict: A production record with keys country_code, source_code,
            production_date, production_mwh, and fetched_at.
    """
    try:
        tree = etree.fromstring(xml_content.encode())
    except etree.XMLSyntaxError:
        logger.warning("Failed to parse XML for %s", country_code)
        return

    for timeseries in tree.findall(".//ns:TimeSeries", NS):
        psr_type_elem = timeseries.find("ns:MktPSRType/ns:psrType", NS)
        if psr_type_elem is None:
            continue
        source_code = psr_type_elem.text

        if source_code not in ENTSOE_PRODUCTION_TYPES:
            continue

        start_elem = timeseries.find("ns:Period/ns:timeInterval/ns:start", NS)
        if start_elem is None:
            continue

        period_start = datetime.strptime(start_elem.text[:10], "%Y-%m-%d").date()

        for point in timeseries.findall("ns:Period/ns:Point", NS):
            position_elem = point.find("ns:position", NS)
            quantity_elem = point.find("ns:quantity", NS)
            if position_elem is None or quantity_elem is None:
                continue

            position = int(position_elem.text)
            quantity = float(quantity_elem.text)
            production_date = period_start + timedelta(days=position - 1)

            yield {
                "country_code": country_code,
                "source_code": source_code,
                "production_date": production_date.isoformat(),
                "production_mwh": quantity,
                "fetched_at": fetched_at,
            }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    pipeline = dlt.pipeline(
        pipeline_name="entsoe_energy",
        destination="postgres",
        dataset_name="raw",
    )

    load_info = pipeline.run(entsoe_source())
    print(load_info)
