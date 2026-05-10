from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AwareDatetime
from sqlmodel import Session, func, select

from app.api.v1.utils import validate_date_range
from app.respository.constants import Metric, Statistic
from app.respository.dal import get_session
from app.respository.models import (
    SensorReadingResponse,
    WeatherReading,
    WeatherReadingCreate,
)

router = APIRouter(prefix="/v1")


@router.post("")
async def add_sensor_data(
    reading: WeatherReadingCreate,
    session: Session = Depends(get_session),
) -> WeatherReading:
    data = reading.model_dump(exclude_none=True)
    db_reading = WeatherReading(**data)
    session.add(db_reading)
    session.commit()
    session.refresh(db_reading)
    return db_reading


@router.get("")
async def get_sensor_data(
    sensor_id: list[int] | None = Query(),
    metric: list[Metric] = Query(),
    statistic: Statistic = Statistic.AVERAGE,
    date_range: tuple[AwareDatetime | None, AwareDatetime | None] = Depends(
        validate_date_range
    ),
    session: Session = Depends(get_session),
):
    if len(metric) == 0:
        raise HTTPException(status_code=400, detail="Need at least one metric")

    start_date, end_date = date_range

    match statistic:
        case Statistic.AVERAGE:
            db_func = func.avg
        case Statistic.MIN:
            db_func = func.min  # type: ignore[assignment]
        case Statistic.MAX:
            db_func = func.max  # type: ignore[assignment]
        case Statistic.SUM:
            db_func = func.sum  # type: ignore[assignment]

    db_columns = {
        _metric: getattr(WeatherReading, _metric) for _metric in metric
    }

    select_cols = [
        db_func(column).label(label.value)
        for label, column in db_columns.items()
    ]
    statement = select(*select_cols)
    if sensor_id:
        statement = statement.where(
            WeatherReading.sensor.in_(sensor_id)  # type: ignore[attr-defined]
        )

    if start_date:
        statement = statement.where(WeatherReading.timestamp > start_date)
    else:
        # If no start date, then definitely no end date, look at last day.
        statement = statement.where(
            WeatherReading.timestamp
            > datetime.now(timezone.utc) - timedelta(days=1)
        )

    if end_date:
        statement = statement.where(WeatherReading.timestamp <= end_date)

    if results := session.execute(statement).mappings().one_or_none():
        return SensorReadingResponse(
            sensors=sensor_id or "all",
            statistic=statistic,
            temperature=results.get("temperature"),
            humidity=results.get("humidity"),
            wind_speed=results.get("wind_speed"),
        )
