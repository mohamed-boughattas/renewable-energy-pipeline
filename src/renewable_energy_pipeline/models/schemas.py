import pandera.pandas as pa
import polars as pl
from pandera.polars import DataFrameSchema

ember_record_schema = DataFrameSchema(
    {
        "country_code": pa.Column(pl.Utf8, nullable=False),
        "country_name": pa.Column(pl.Utf8, nullable=False),
        "year": pa.Column(pl.Int32, nullable=False),
        "month": pa.Column(pl.Int32, nullable=False),
        "series_name": pa.Column(pl.Utf8, nullable=False),
        "variable": pa.Column(pl.Utf8, nullable=False),
        "unit": pa.Column(pl.Utf8, nullable=False),
        "value": pa.Column(pl.Float64, nullable=True),
    },
    strict=False,
)
