from datetime import timedelta

from fastapi import HTTPException
from pydantic import AwareDatetime


def validate_date_range(
    start_date: AwareDatetime | None = None,
    end_date: AwareDatetime | None = None,
) -> tuple[AwareDatetime | None, AwareDatetime | None]:
    if end_date and not start_date:
        raise HTTPException(
            status_code=400, detail="end_date requires a start_date"
        )
    if start_date and end_date:
        if start_date >= end_date:
            raise HTTPException(
                status_code=400, detail="start_date must be before end_date"
            )
        time_delta = end_date - start_date
        if time_delta < timedelta(days=1) or time_delta > timedelta(days=30):
            raise HTTPException(
                status_code=400,
                detail="date range must be between 1 and 30 days",
            )

    return start_date, end_date
