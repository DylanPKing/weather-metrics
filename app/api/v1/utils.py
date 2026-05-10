from pydantic import AwareDatetime
from fastapi import HTTPException


def validate_date_range(
    start_date: AwareDatetime | None = None,
    end_date: AwareDatetime | None = None,
) -> tuple[AwareDatetime | None, AwareDatetime | None]:
    if end_date and not start_date:
        raise HTTPException(
            status_code=422, detail="end_date requires a start_date"
        )
    return start_date, end_date
