from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_root_endpoint_returns_success() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "message" in response.json()


def test_health_endpoint_returns_expected_payload() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "inventory-api",
        "version": "0.1.0",
    }
