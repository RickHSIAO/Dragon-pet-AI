from fastapi.testclient import TestClient

from app.llm.mock_provider import MockLLMProvider
from app.main import app


def test_chat_old_format_still_returns_200():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200


def test_chat_response_schema_remains_reply_mood_source():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}


def test_chat_is_not_wired_to_llm_adapter_yet(monkeypatch):
    def raise_if_used(self, request):  # noqa: ARG001
        raise AssertionError("/chat should not call MockLLMProvider yet")

    monkeypatch.setattr(MockLLMProvider, "generate", raise_if_used)

    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}
