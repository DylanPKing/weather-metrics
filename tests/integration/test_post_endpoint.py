"""Integration tests for POST /v1 endpoint."""

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.respository.models import WeatherSensor


class TestPostSensorData:
    """Tests for POST /v1 sensor data creation."""

    def test_post_with_all_fields_returns_200(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test creating a reading with all fields returns 200 with complete response."""
        response = client.post(
            "/v1",
            json={
                "sensor": test_sensor.id,
                "temperature": "23.50",
                "humidity": 65,
                "wind_speed": "12.30",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sensor"] == test_sensor.id
        assert data["temperature"] == "23.50"
        assert data["humidity"] == 65
        assert data["wind_speed"] == "12.30"

    def test_post_with_only_required_field_returns_200(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test creating a reading with only sensor field returns 200 with nulls."""
        response = client.post("/v1", json={"sensor": test_sensor.id})
        assert response.status_code == 200
        data = response.json()
        assert data["sensor"] == test_sensor.id
        assert data["temperature"] is None
        assert data["humidity"] is None
        assert data["wind_speed"] is None

    def test_post_returns_auto_generated_id(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that POST response includes auto-generated id."""
        response = client.post("/v1", json={"sensor": test_sensor.id})
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], int)
        assert data["id"] > 0

    def test_post_returns_timestamp(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that POST response includes timestamp."""
        response = client.post("/v1", json={"sensor": test_sensor.id})
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert data["timestamp"] is not None

    def test_post_defaults_timestamp_to_utc(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that timestamp defaults to current UTC when not provided."""
        before = datetime.now(timezone.utc)
        response = client.post("/v1", json={"sensor": test_sensor.id})
        after = datetime.now(timezone.utc)

        assert response.status_code == 200
        data = response.json()
        timestamp_str = data["timestamp"]
        timestamp = datetime.fromisoformat(timestamp_str)

        # Ensure timestamp is timezone-aware for comparison
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        # Timestamp should be between before and after
        assert before <= timestamp <= after

    def test_post_with_custom_timestamp(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that custom timestamp is preserved."""
        custom_time = datetime(2024, 5, 10, 12, 30, 0, tzinfo=timezone.utc)
        response = client.post(
            "/v1",
            json={
                "sensor": test_sensor.id,
                "timestamp": custom_time.isoformat(),
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Timestamp in response may be without timezone info
        assert "2024-05-10T12:30:00" in data["timestamp"]

    def test_post_missing_sensor_returns_422(self, client: TestClient):
        """Test that missing sensor field returns 422."""
        response = client.post("/v1", json={})
        assert response.status_code == 422

    def test_post_invalid_sensor_type_returns_422(self, client: TestClient):
        """Test that invalid sensor type (string) returns 422."""
        response = client.post("/v1", json={"sensor": "not_an_int"})
        assert response.status_code == 422

    def test_post_invalid_json_returns_422(self, client: TestClient):
        """Test that invalid JSON body returns 422."""
        response = client.post(
            "/v1",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_post_with_partial_optional_fields(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test creating a reading with some optional fields."""
        response = client.post(
            "/v1",
            json={
                "sensor": test_sensor.id,
                "temperature": "23.50",
                "humidity": 65,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] == "23.50"
        assert data["humidity"] == 65
        assert data["wind_speed"] is None

    def test_post_with_decimal_precision(
        self, client: TestClient, test_sensor: WeatherSensor
    ):
        """Test that decimal values maintain precision."""
        response = client.post(
            "/v1",
            json={
                "sensor": test_sensor.id,
                "temperature": "23.45",
                "wind_speed": "12.89",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] == "23.45"
        assert data["wind_speed"] == "12.89"
