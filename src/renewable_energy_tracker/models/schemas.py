import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema

VALID_COUNTRY_CODES = ["DE", "FR", "ES", "DK", "NO", "NL"]
VALID_SOURCE_CODES = [
    "B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B09",
    "B10", "B11", "B12", "B13", "B14", "B15", "B16", "B17", "B18", "B19",
]

daily_production_schema = DataFrameSchema(
    {
        "country_code": Column(
            str,
            checks=pa.Check.isin(VALID_COUNTRY_CODES),
            nullable=False,
        ),
        "source_code": Column(
            str,
            checks=pa.Check.isin(VALID_SOURCE_CODES),
            nullable=False,
        ),
        "production_date": Column(
            "datetime64[ns]",
            nullable=False,
        ),
        "production_mwh": Column(
            float,
            checks=[
                pa.Check.ge(0),
                pa.Check.le(500000),
            ],
            nullable=False,
        ),
    },
    strict=True,
    coerce=True,
)
