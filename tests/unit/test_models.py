"""Tests for data models and validation."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.respository.models import WeatherReadingCreate


class TestWeatherReadingCreateModel:
    """Tests for WeatherReadingCreate model validation."""

    def test_all_fields_valid(self):
        """Test creating a reading with all fields."""
        data = {
            "sensor": 1,
            "temperature": Decimal("23.50"),
            "humidity": 65,
            "wind_speed": Decimal("12.30"),
            "timestamp": datetime.now(timezone.utc),
        }
        reading = WeatherReadingCreate(**data)
        assert reading.sensor == 1
        assert reading.temperature == Decimal("23.50")
        assert reading.humidity == 65
        assert reading.wind_speed == Decimal("12.30")

    def test_only_required_field(self):
        """Test creating a reading with only required sensor field."""
        reading = WeatherReadingCreate(sensor=1)
        assert reading.sensor == 1
        assert reading.temperature is None
        assert reading.humidity is None
        assert reading.wind_speed is None
        assert reading.timestamp is None

    def test_missing_sensor_raises_validation_error(self):
        """Test that missing sensor field raises ValidationError."""
        with pytest.raises(ValidationError):
            WeatherReadingCreate()

    def test_invalid_sensor_type_raises_validation_error(self):
        """Test that non-integer sensor type raises ValidationError."""
        with pytest.raises(ValidationError):
            WeatherReadingCreate(sensor="not_an_int")

    def test_valid_temperature_values(self):
        """Test various valid temperature values."""
        valid_temps = [
            Decimal("0.00"),
            Decimal("23.50"),
            Decimal("-10.25"),
            Decimal("999.99"),
            Decimal("-99.99"),
        ]
        for temp in valid_temps:
            reading = WeatherReadingCreate(sensor=1, temperature=temp)
            assert reading.temperature == temp

    def test_large_temperature_accepted(self):
        """Test that large temperature values are accepted (no upper limit enforced)."""
        reading = WeatherReadingCreate(sensor=1, temperature=Decimal("1000.00"))
        assert reading.temperature == Decimal("1000.00")

    def test_valid_wind_speed_values(self):
        """Test various valid wind_speed values."""
        valid_speeds = [
            Decimal("0.00"),
            Decimal("12.30"),
            Decimal("999.99"),
        ]
        for speed in valid_speeds:
            reading = WeatherReadingCreate(sensor=1, wind_speed=speed)
            assert reading.wind_speed == speed

    def test_large_wind_speed_accepted(self):
        """Test that large wind_speed values are accepted (no upper limit enforced)."""
        reading = WeatherReadingCreate(sensor=1, wind_speed=Decimal("1000.00"))
        assert reading.wind_speed == Decimal("1000.00")

    def test_valid_humidity_values(self):
        """Test various valid humidity values."""
        valid_humidities = [0, 50, 100]
        for humidity in valid_humidities:
            reading = WeatherReadingCreate(sensor=1, humidity=humidity)
            assert reading.humidity == humidity

    def test_timezone_aware_timestamp(self):
        """Test that timezone-aware timestamp is accepted."""
        timestamp = datetime(2024, 5, 10, 12, 30, 0, tzinfo=timezone.utc)
        reading = WeatherReadingCreate(sensor=1, timestamp=timestamp)
        assert reading.timestamp == timestamp

    def test_naive_timestamp_rejected(self):
        """Test that naive timestamp (without timezone) is rejected."""
        with pytest.raises(ValidationError):
            timestamp = datetime(2024, 5, 10, 12, 30, 0)
            WeatherReadingCreate(sensor=1, timestamp=timestamp)

    def test_invalid_timestamp_format_raises_validation_error(self):
        """Test that invalid timestamp format raises ValidationError."""
        with pytest.raises(ValidationError):
            WeatherReadingCreate(sensor=1, timestamp="not_a_timestamp")
