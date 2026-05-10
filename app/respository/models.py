from decimal import Decimal

from sqlmodel import SQLModel, Field


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
