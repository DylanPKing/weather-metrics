from fastapi import APIRouter, Depends, Query
from pydantic import AwareDatetime
from app.api.v1.utils import validate_date_range
from app.respository.constants import Metric, Statistic
from app.respository.dal import get_session
from app.respository.models import (
    WeatherReadingCreate,
    WeatherReading,
    SensorReadingResponse,
)
from sqlmodel import Session, func, select


router = APIRouter(prefix="/v1")


@router.post("")
async def add_sensor_data(
    reading: WeatherReadingCreate,
    session: Session = Depends(get_session),
) -> WeatherReading:
    db_reading = WeatherReading.model_validate(reading)
    session.add(db_reading)
    session.commit()
    session.refresh(db_reading)
    return db_reading


@router.get("")
async def get_sensor_data(
    sensor_id: list[int] = Query(),
    metric: list[Metric] = Query(),
    statistic: Statistic = Statistic.AVERAGE,
    date_range: tuple[AwareDatetime | None, AwareDatetime | None] = Depends(
        validate_date_range
    ),
    session: Session = Depends(get_session),
):
    start_date, end_date = date_range

    match statistic:
        case Statistic.AVERAGE:
            db_func = func.avg
        case Statistic.MIN:
            db_func = func.min
        case Statistic.MAX:
            db_func = func.max
        case Statistic.SUM:
            db_func = func.sum

    db_columns = [getattr(WeatherReading, _metric) for _metric in metric]

    select_cols = [db_func(column) for column in db_columns]
    statement = select(*select_cols)
    statement = statement.where(WeatherReading.sensor.in_(sensor_id))

    if start_date:
        statement = statement.where(WeatherReading.timestamp > start_date)

    if end_date:
        statement = statement.where(WeatherReading.timestamp <= end_date)

    results = session.exec(statement).one()

    print(results)
