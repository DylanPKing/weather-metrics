"""Tests for statistics aggregation in GET /v1 endpoint."""

from typing import Callable

from fastapi.testclient import TestClient

from app.respository.models import WeatherSensor


class TestStatisticsAggregation:
    """Tests for various statistic calculations."""

    def test_average_calculation(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test AVERAGE statistic calculation."""
        create_reading(test_sensor.id, temperature="20.00")
        create_reading(test_sensor.id, temperature="30.00")

        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "statistic": "average",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Average of 20 and 30 is 25
        assert float(data["temperature"]) == 25.0

    def test_min_calculation(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test MIN statistic calculation."""
        create_reading(test_sensor.id, temperature="20.00")
        create_reading(test_sensor.id, temperature="30.00")
        create_reading(test_sensor.id, temperature="15.00")

        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "statistic": "min",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["temperature"]) == 15.0

    def test_max_calculation(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test MAX statistic calculation."""
        create_reading(test_sensor.id, temperature="20.00")
        create_reading(test_sensor.id, temperature="30.00")
        create_reading(test_sensor.id, temperature="25.00")

        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "statistic": "max",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["temperature"]) == 30.0

    def test_sum_calculation(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test SUM statistic calculation."""
        create_reading(test_sensor.id, temperature="20.00")
        create_reading(test_sensor.id, temperature="30.00")
        create_reading(test_sensor.id, temperature="10.00")

        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "statistic": "sum",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["temperature"]) == 60.0

    def test_aggregation_across_multiple_sensors(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensors: list[WeatherSensor],
    ):
        """Test aggregation works across multiple sensor readings."""
        create_reading(test_sensors[0].id, humidity=40)
        create_reading(test_sensors[0].id, humidity=60)
        create_reading(test_sensors[1].id, humidity=50)
        create_reading(test_sensors[1].id, humidity=70)

        # Query both sensors
        response = client.get(
            "/v1",
            params={
                "sensor_id": [test_sensors[0].id, test_sensors[1].id],
                "metric": "humidity",
                "statistic": "average",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Average of 40, 60, 50, 70 is 55
        assert float(data["humidity"]) == 55.0

    def test_aggregation_with_multiple_metrics(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test aggregation with multiple metrics simultaneously."""
        create_reading(
            test_sensor.id,
            temperature="20.00",
            humidity=30,
            wind_speed="5.00",
        )
        create_reading(
            test_sensor.id,
            temperature="30.00",
            humidity=70,
            wind_speed="15.00",
        )

        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": ["temperature", "humidity", "wind_speed"],
                "statistic": "average",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["temperature"]) == 25.0
        assert float(data["humidity"]) == 50.0
        assert float(data["wind_speed"]) == 10.0

    def test_statistic_with_null_values(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test statistic calculation handles null values."""
        create_reading(test_sensor.id, temperature="20.00")
        create_reading(test_sensor.id, temperature=None)
        create_reading(test_sensor.id, temperature="30.00")

        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "statistic": "average",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Average ignores nulls: (20 + 30) / 2 = 25
        assert float(data["temperature"]) == 25.0
