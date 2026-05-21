from datetime import datetime

from pydantic import BaseModel, Field


class EmberRecord(BaseModel):
    country_code: str = Field(min_length=2, max_length=3)
    country_name: str = Field(min_length=1)
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)
    series_name: str = Field(min_length=1)
    variable: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    value: float | None = None
    is_aggregate_series: bool = False
    fetched_at: datetime = Field(default_factory=datetime.now)


class EmberPayload(BaseModel):
    records: list[EmberRecord]
    category: str
    fetched_at: datetime = Field(default_factory=datetime.now)
