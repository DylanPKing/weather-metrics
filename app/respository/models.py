from decimal import Decimal
from datetime import datetime, timezone

from pydantic import BaseModel, AwareDatetime
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field

from app.respository.constants import Metric


class WeatherSensor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)


class WeatherReading(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    sensor: int = Field(foreign_key=f"{WeatherSensor.__tablename__}.id")
    temperature: Decimal | None = Field(
        default=None,
        max_digits=5,
        decimal_places=2,
    )
    wind_speed: Decimal | None = Field(
        default=None,
        max_digits=5,
        decimal_places=2,
    )
    humidity: int | None = Field(default=None)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class WeatherReadingCreate(BaseModel):
    sensor: int
    temperature: Decimal | None = None
    wind_speed: Decimal | None = None
    humidity: int | None = None
    timestamp: AwareDatetime | None = None


class SensorReadingResponse(BaseModel):
    sensors: list[int]
    metric: Metric
    temperature: Decimal | None = None
    wind_speed: Decimal | None = None
    humidity: int | None = None
