import os

from fastapi.testclient import TestClient

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

from app.main import app  # noqa: E402


def test_health_returns_ok_status_and_service():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "dragon-pet-ai",
    }


def test_chat_valid_message_returns_mock_response():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "mood" in data
    assert data["source"] == "mock"


def test_chat_missing_message_returns_validation_error():
    with TestClient(app) as client:
        response = client.post("/chat", json={"text": "Hello!"})

    assert response.status_code == 422


def test_chat_empty_json_returns_validation_error():
    with TestClient(app) as client:
        response = client.post("/chat", json={})

    assert response.status_code == 422
