from datetime import date, datetime

from pydantic import BaseModel, Field


class ProductionRecord(BaseModel):
    country_code: str = Field(min_length=2, max_length=2)
    source_code: str = Field(min_length=2, max_length=5)
    production_date: date
    production_mwh: float = Field(ge=0)
    fetched_at: datetime = Field(default_factory=datetime.now)


class DailyProductionPayload(BaseModel):
    records: list[ProductionRecord]
    country_code: str
    fetched_at: datetime = Field(default_factory=datetime.now)
