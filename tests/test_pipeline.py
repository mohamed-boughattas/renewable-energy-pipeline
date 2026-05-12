from datetime import date

from renewable_energy_tracker.config import ENTSOE_BASE_URL
from renewable_energy_tracker.pipeline import _build_url, _parse_xml


def test_build_url() -> None:
    """Verify _build_url constructs a correctly formatted ENTSO-E API URL."""
    api_key = "test-security-token"
    domain = "10Y1001A1001A83F"
    target_date = date(2024, 6, 1)

    url = _build_url(api_key, domain, target_date)

    assert ENTSOE_BASE_URL in url
    assert "securityToken=test-security-token" in url
    assert "documentType=A73" in url
    assert "processType=A16" in url
    assert "in_Domain=10Y1001A1001A83F" in url
    assert "periodStart=202406010000" in url
    assert "periodEnd=202406020000" in url


def test_parse_xml(sample_xml_response: str) -> None:
    """Verify _parse_xml extracts records from a valid ENTSO-E XML response.

    Args:
        sample_xml_response: XML string fixture containing two TimeSeries entries.
    """
    records = list(_parse_xml(sample_xml_response, "DE", "2024-06-01T00:00:00Z"))

    assert len(records) == 2
    assert records[0]["country_code"] == "DE"
    assert records[0]["source_code"] == "B16"
    assert records[0]["production_mwh"] == 15000.0
    assert records[0]["production_date"] == "2024-06-01"

    assert records[1]["source_code"] == "B17"
    assert records[1]["production_mwh"] == 22000.0


def test_parse_xml_empty_response() -> None:
    """Verify _parse_xml returns an empty list for an XML with no TimeSeries."""
    empty_xml = """<?xml version="1.0" encoding="UTF-8"?>
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:generationdocument:7:0">
</GL_MarketDocument>"""
    records = list(_parse_xml(empty_xml, "DE", "2024-06-01T00:00:00Z"))
    assert records == []


def test_parse_xml_invalid_xml_syntax() -> None:
    """Verify _parse_xml handles malformed XML gracefully."""
    bad_xml = "not valid xml at all <<<<"
    records = list(_parse_xml(bad_xml, "FR", "2024-06-01T00:00:00Z"))
    assert records == []


def test_parse_xml_unknown_psr_type() -> None:
    """Verify _parse_xml skips TimeSeries with unknown psrType."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:generationdocument:7:0">
    <TimeSeries>
        <MktPSRType><psrType>B99</psrType></MktPSRType>
        <Period>
            <timeInterval><start>2024-06-01T00:00Z</start></timeInterval>
            <Point><position>1</position><quantity>100</quantity></Point>
        </Period>
    </TimeSeries>
</GL_MarketDocument>"""
    records = list(_parse_xml(xml, "DE", "2024-06-01T00:00:00Z"))
    assert records == []


def test_parse_xml_missing_mkt_psr_type() -> None:
    """Verify _parse_xml skips TimeSeries without MktPSRType."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:generationdocument:7:0">
    <TimeSeries>
        <Period>
            <timeInterval><start>2024-06-01T00:00Z</start></timeInterval>
            <Point><position>1</position><quantity>100</quantity></Point>
        </Period>
    </TimeSeries>
</GL_MarketDocument>"""
    records = list(_parse_xml(xml, "DE", "2024-06-01T00:00:00Z"))
    assert records == []


def test_parse_xml_missing_start_element() -> None:
    """Verify _parse_xml skips TimeSeries without timeInterval start."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:generationdocument:7:0">
    <TimeSeries>
        <MktPSRType><psrType>B16</psrType></MktPSRType>
        <Period>
            <timeInterval></timeInterval>
            <Point><position>1</position><quantity>100</quantity></Point>
        </Period>
    </TimeSeries>
</GL_MarketDocument>"""
    records = list(_parse_xml(xml, "DE", "2024-06-01T00:00:00Z"))
    assert records == []


def test_parse_xml_missing_point_elements() -> None:
    """Verify _parse_xml skips Point elements missing position or quantity."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:generationdocument:7:0">
    <TimeSeries>
        <MktPSRType><psrType>B16</psrType></MktPSRType>
        <Period>
            <timeInterval><start>2024-06-01T00:00Z</start></timeInterval>
            <Point><quantity>100</quantity></Point>
            <Point><position>2</position></Point>
        </Period>
    </TimeSeries>
</GL_MarketDocument>"""
    records = list(_parse_xml(xml, "DE", "2024-06-01T00:00:00Z"))
    assert records == []


def test_parse_xml_multiple_points_single_timeseries() -> None:
    """Verify _parse_xml correctly yields multiple points from one TimeSeries."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:generationdocument:7:0">
    <TimeSeries>
        <MktPSRType><psrType>B16</psrType></MktPSRType>
        <Period>
            <timeInterval><start>2024-06-01T00:00Z</start></timeInterval>
            <Point><position>1</position><quantity>15000</quantity></Point>
            <Point><position>2</position><quantity>16000</quantity></Point>
            <Point><position>3</position><quantity>17000</quantity></Point>
        </Period>
    </TimeSeries>
</GL_MarketDocument>"""
    records = list(_parse_xml(xml, "FR", "2024-06-01T00:00:00Z"))
    assert len(records) == 3
    assert records[0]["production_date"] == "2024-06-01"
    assert records[0]["production_mwh"] == 15000.0
    assert records[1]["production_date"] == "2024-06-02"
    assert records[1]["production_mwh"] == 16000.0
    assert records[2]["production_date"] == "2024-06-03"
    assert records[2]["production_mwh"] == 17000.0
