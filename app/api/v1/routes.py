from fastapi import APIRouter


router = APIRouter(prefix="/v1")


@router.post("/{sensor_id}")
async def add_sensor_data(sensor_id: int):
    pass


@router.get("")
async def get_sensor_data():
    return {"message": "router working!"}
