from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

from app.main import app
from app.respository.dal import get_session
from app.respository.models import WeatherReading, WeatherSensor


@pytest.fixture(scope="function")
def test_engine():
    """Create an in-memory SQLite test database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Provide a test database session."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(test_session):
    """Provide a FastAPI test client with test database."""

    def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_sensor(test_session) -> WeatherSensor:
    """Create a test sensor in the database."""
    sensor = WeatherSensor()
    test_session.add(sensor)
    test_session.commit()
    test_session.refresh(sensor)
    return sensor


@pytest.fixture(scope="function")
def test_sensors(test_session) -> list[WeatherSensor]:
    """Create multiple test sensors in the database."""
    sensors = [WeatherSensor() for _ in range(3)]
    for sensor in sensors:
        test_session.add(sensor)
    test_session.commit()
    for sensor in sensors:
        test_session.refresh(sensor)
    return sensors


@pytest.fixture(scope="function")
def sample_reading_data():
    """Provide sample data for creating readings."""
    return {
        "sensor": 1,
        "temperature": Decimal("23.50"),
        "humidity": 65,
        "wind_speed": Decimal("12.30"),
    }


@pytest.fixture(scope="function")
def sample_reading_minimal():
    """Provide minimal required data for creating readings."""
    return {"sensor": 1}


@pytest.fixture(scope="function")
def create_reading(test_session):
    """Factory fixture to create readings."""

    def _create_reading(
        sensor: int,
        temperature: Decimal | None = None,
        humidity: int | None = None,
        wind_speed: Decimal | None = None,
        timestamp: datetime | None = None,
    ) -> WeatherReading:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        reading = WeatherReading(
            sensor=sensor,
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            timestamp=timestamp,
        )
        test_session.add(reading)
        test_session.commit()
        test_session.refresh(reading)
        return reading

    return _create_reading
