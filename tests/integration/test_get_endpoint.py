"""Integration tests for GET /v1 endpoint."""

from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi.testclient import TestClient

from app.respository.models import WeatherSensor


class TestGetSensorData:
    """Tests for GET /v1 sensor data retrieval."""

    def test_get_with_valid_sensor_id_and_metric_returns_200(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensors: list[WeatherSensor],
    ):
        """Test valid sensor_id and metric params return 200."""
        create_reading(test_sensors[0].id, temperature="23.50")
        response = client.get(
            "/v1",
            params={"sensor_id": test_sensors[0].id, "metric": "temperature"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sensors"] == [test_sensors[0].id]

    def test_get_filters_results_by_sensor_id(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensors: list[WeatherSensor],
    ):
        """Test that results are filtered by requested sensor_id values."""
        create_reading(test_sensors[0].id, temperature="20.00")
        create_reading(test_sensors[1].id, temperature="25.00")
        create_reading(test_sensors[2].id, temperature="30.00")

        response = client.get(
            "/v1",
            params={
                "sensor_id": [test_sensors[0].id, test_sensors[2].id],
                "metric": "temperature",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert set(data["sensors"]) == {test_sensors[0].id, test_sensors[2].id}

    def test_get_returns_only_requested_metric_columns(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test that only requested metric columns are returned."""
        create_reading(
            test_sensor.id,
            temperature="23.50",
            humidity=65,
            wind_speed="12.30",
        )

        # Request only temperature
        response = client.get(
            "/v1",
            params={"sensor_id": test_sensor.id, "metric": "temperature"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] is not None
        assert data["humidity"] is None
        assert data["wind_speed"] is None

    def test_get_accepts_multiple_sensor_ids(
        self, client, create_reading, test_sensors
    ):
        """Test that multiple sensor_id values are accepted."""
        for sensor in test_sensors:
            create_reading(sensor.id, temperature="20.00")

        response = client.get(
            "/v1",
            params={
                "sensor_id": [
                    test_sensors[0].id,
                    test_sensors[1].id,
                    test_sensors[2].id,
                ],
                "metric": "temperature",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert set(data["sensors"]) == {
            test_sensors[0].id,
            test_sensors[1].id,
            test_sensors[2].id,
        }

    def test_get_accepts_multiple_metric_values(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test that multiple metric values are accepted."""
        create_reading(
            test_sensor.id,
            temperature="23.50",
            humidity=65,
            wind_speed="12.30",
        )

        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": ["temperature", "humidity", "wind_speed"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] is not None
        assert data["humidity"] is not None
        assert data["wind_speed"] is not None

    def test_get_defaults_statistic_to_average(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test that statistic defaults to 'average' when not provided."""
        create_reading(test_sensor.id, temperature="20.00")
        create_reading(test_sensor.id, temperature="30.00")

        response = client.get(
            "/v1",
            params={"sensor_id": test_sensor.id, "metric": "temperature"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["statistic"] == "average"
        # Average of 20 and 30 is 25
        assert data["temperature"] is not None

    def test_get_missing_sensor_id_returns_422(self, client: TestClient):
        """Test that missing sensor_id returns 422."""
        response = client.get("/v1", params={"metric": "temperature"})
        assert response.status_code == 422

    def test_get_missing_metric_returns_422(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that missing metric returns 422."""
        response = client.get("/v1", params={"sensor_id": test_sensor.id})
        assert response.status_code == 422

    def test_get_invalid_metric_value_returns_422(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that invalid metric value returns 422."""
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "invalid_metric",
            },
        )
        assert response.status_code == 422

    def test_get_invalid_statistic_value_returns_422(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that invalid statistic value returns 422."""
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "statistic": "invalid_statistic",
            },
        )
        assert response.status_code == 422

    def test_get_unknown_query_params_ignored(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test that unknown query params are ignored (no error)."""
        create_reading(test_sensor.id, temperature="23.50")
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "unknown_param": "value",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] is not None


class TestGetDateFiltering:
    """Tests for GET /v1 date range filtering logic."""

    def test_get_end_date_without_start_date_returns_400(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that end_date without start_date returns 400."""
        end_date = datetime.now(timezone.utc)
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "end_date": end_date.isoformat(),
            },
        )
        assert response.status_code == 400

    def test_get_start_date_equal_to_end_date_returns_400(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that start_date equal to end_date returns 400."""
        now = datetime.now(timezone.utc)
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "start_date": now.isoformat(),
                "end_date": now.isoformat(),
            },
        )
        assert response.status_code == 400

    def test_get_start_date_after_end_date_returns_400(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that start_date after end_date returns 400."""
        now = datetime.now(timezone.utc)
        start = now + timedelta(days=1)
        end = now
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
        )
        assert response.status_code == 400

    def test_get_date_range_less_than_1_day_returns_400(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that date range < 1 day returns 400."""
        start = datetime.now(timezone.utc)
        end = start + timedelta(hours=12)
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
        )
        assert response.status_code == 400

    def test_get_date_range_more_than_30_days_returns_400(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that date range > 30 days returns 400."""
        start = datetime.now(timezone.utc)
        end = start + timedelta(days=31)
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
        )
        assert response.status_code == 400

    def test_get_valid_date_range_filters_results(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test that valid date range filters results correctly."""
        now = datetime.now(timezone.utc)
        old_time = now - timedelta(days=5)
        recent_time = now - timedelta(hours=1)

        create_reading(test_sensor.id, temperature="20.00", timestamp=old_time)
        create_reading(
            test_sensor.id, temperature="25.00", timestamp=recent_time
        )

        # Query for recent reading only
        start = now - timedelta(days=2)
        end = now
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Should only include recent reading
        assert data["temperature"] is not None

    def test_get_no_start_date_defaults_to_last_24_hours(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test that no start_date defaults to last 24 hours."""
        now = datetime.now(timezone.utc)
        old_time = now - timedelta(days=2)
        recent_time = now - timedelta(hours=1)

        create_reading(test_sensor.id, temperature="20.00", timestamp=old_time)
        create_reading(
            test_sensor.id, temperature="25.00", timestamp=recent_time
        )

        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Should only include recent reading (within last 24 hours)
        assert data["temperature"] is not None


class TestGetEdgeCases:
    """Tests for GET /v1 edge cases."""

    def test_get_non_existent_sensor_returns_empty_results(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensors: list[WeatherSensor],
    ):
        """Test that non-existent sensor_id returns empty results (not error)."""
        create_reading(test_sensors[0].id, temperature="23.50")

        # Query for non-existent sensor
        response = client.get(
            "/v1",
            params={
                "sensor_id": 99999,
                "metric": "temperature",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Should be empty or None
        assert data.get("temperature") is None

    def test_get_no_matching_readings_returns_empty_results(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test that no matching readings return empty results (not error)."""
        create_reading(test_sensor.id, humidity=65)

        # Query for temperature when only humidity exists
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] is None
