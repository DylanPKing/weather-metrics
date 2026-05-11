"""Integration tests for end-to-end workflows."""

from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi.testclient import TestClient

from app.respository.models import WeatherSensor


class TestEndToEndWorkflows:
    """End-to-end workflow tests covering multiple operations."""

    def test_create_and_retrieve_single_reading(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test creating a reading and retrievi§ng it."""
        # Create a reading
        post_response = client.post(
            "/v1",
            json={
                "sensor": test_sensor.id,
                "temperature": "23.50",
                "humidity": 65,
            },
        )
        assert post_response.status_code == 200
        created_reading = post_response.json()

        # Retrieve the reading
        get_response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
            },
        )
        assert get_response.status_code == 200
        data = get_response.json()
        # Values may be normalized (23.50 -> 23.5)
        assert float(data["temperature"]) == 23.5

    def test_create_multiple_readings_and_query_with_filters(
        self, client: TestClient, test_sensors: list[WeatherSensor]
    ):
        """Test creating multiple readings and querying with various filters."""
        # Create readings from multiple sensors
        for i, sensor in enumerate(test_sensors):
            client.post(
                "/v1",
                json={
                    "sensor": sensor.id,
                    "temperature": str(20 + i * 5),  # 20, 25, 30
                    "humidity": 50 + i * 10,
                },
            )

        # Query sensor 1 only
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensors[0].id,
                "metric": "temperature",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["temperature"]) == 20.0

        # Query sensors 1 and 3
        response = client.get(
            "/v1",
            params={
                "sensor_id": [test_sensors[0].id, test_sensors[2].id],
                "metric": ["temperature", "humidity"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] is not None
        assert data["humidity"] is not None

    def test_comprehensive_workflow_3_sensors_5_readings_each(
        self, client: TestClient, test_sensors: list[WeatherSensor]
    ):
        """Test full workflow: create 3 sensors × 5 readings each, query combinations."""
        # Create 5 readings per sensor
        for sensor in test_sensors:
            for j in range(5):
                client.post(
                    "/v1",
                    json={
                        "sensor": sensor.id,
                        "temperature": str(20 + j * 2),  # 20, 22, 24, 26, 28
                        "humidity": 50 + j * 5,
                        "wind_speed": str(5 + j * 1),  # 5, 6, 7, 8, 9
                    },
                )

        # Query 1: All sensors, temperature average
        response = client.get(
            "/v1",
            params={
                "sensor_id": [
                    test_sensors[0].id,
                    test_sensors[1].id,
                    test_sensors[2].id,
                ],
                "metric": "temperature",
                "statistic": "average",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # All temperatures are the same across sensors, average should be 24
        assert float(data["temperature"]) == 24.0

        # Query 2: Single sensor, multiple metrics, MIN
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensors[0].id,
                "metric": ["temperature", "humidity", "wind_speed"],
                "statistic": "min",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["temperature"]) == 20.0
        assert float(data["humidity"]) == 50.0
        assert float(data["wind_speed"]) == 5.0

        # Query 3: Single sensor, multiple metrics, MAX
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensors[1].id,
                "metric": ["temperature", "humidity", "wind_speed"],
                "statistic": "max",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert float(data["temperature"]) == 28.0
        assert float(data["humidity"]) == 70.0
        assert float(data["wind_speed"]) == 9.0

        # Query 4: Two sensors with SUM
        response = client.get(
            "/v1",
            params={
                "sensor_id": [test_sensors[0].id, test_sensors[1].id],
                "metric": "temperature",
                "statistic": "sum",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Sum of 20, 22, 24, 26, 28 twice = 240
        assert float(data["temperature"]) == 240.0

    def test_workflow_with_date_filtering(
        self,
        client: TestClient,
        create_reading: Callable,
        test_sensor: WeatherSensor,
    ):
        """Test workflow with creation and retrieval using date filtering."""
        now = datetime.now(timezone.utc)
        day1 = now - timedelta(days=3)
        day2 = now - timedelta(days=1)
        day3 = now

        # Create readings across multiple days
        create_reading(test_sensor.id, temperature="20.00", timestamp=day1)
        create_reading(
            test_sensor.id,
            temperature="22.00",
            timestamp=day1 + timedelta(hours=1),
        )
        create_reading(test_sensor.id, temperature="25.00", timestamp=day2)
        create_reading(test_sensor.id, temperature="28.00", timestamp=day3)

        # Query day 1 to day 2 (should get readings from day1)
        start1 = day1 - timedelta(minutes=1)  # Just before day1
        end1 = day1 + timedelta(days=1)
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "start_date": start1.isoformat(),
                "end_date": end1.isoformat(),
                "statistic": "average",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Average of day 1 readings: (20 + 22) / 2 = 21
        assert float(data["temperature"]) == 21.0

        # Query day 2 onwards
        start2 = day2 - timedelta(minutes=1)
        end2 = day3 + timedelta(hours=1)
        response = client.get(
            "/v1",
            params={
                "sensor_id": test_sensor.id,
                "metric": "temperature",
                "start_date": start2.isoformat(),
                "end_date": end2.isoformat(),
                "statistic": "average",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Average of days 2-3: (25 + 28) / 2 = 26.5
        assert float(data["temperature"]) == 26.5
