from datetime import datetime, timezone
from decimal import Decimal

from pydantic import AwareDatetime, BaseModel
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel

from app.respository.constants import Statistic


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
    sensors: list[int] | str
    statistic: Statistic
    temperature: Decimal | None = None
    wind_speed: Decimal | None = None
    humidity: int | None = None
