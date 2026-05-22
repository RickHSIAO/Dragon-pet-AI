import os

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient

from app.llm.real_provider import CANONICAL_SAFE_FALLBACK_TEXT
from app.llm.types import LLMResponse
from app.main import app
from app.services.provider_settings_service import reset_provider_settings
from app.services.chat_service import LOCAL_PROVIDER_TIMEOUT_FALLBACK_TEXT
from app.services.usage_meter_service import reset_usage_meter


@pytest.fixture(autouse=True)
def reset_runtime_state():
    reset_provider_settings()
    reset_usage_meter()
    yield
    reset_provider_settings()
    reset_usage_meter()


class FakeOllamaSuccessProvider:
    provider_name = "ollama"

    def __init__(self):
        self.calls = []

    def generate(self, request):
        self.calls.append(request)
        return LLMResponse(
            text="local ollama route reply",
            provider="ollama",
            model="qwen3:8b",
            usage={"output_tokens_actual": 4},
            error=None,
        )


class FakeOllamaErrorProvider:
    provider_name = "ollama"

    def __init__(self, error="provider_timeout"):
        self.error = error
        self.calls = []

    def generate(self, request):
        self.calls.append(request)
        return LLMResponse(
            text="raw provider fallback text should not be exposed",
            provider="ollama",
            model="qwen3:8b",
            usage=None,
            error=self.error,
        )


def patch_provider_settings(client, **overrides):
    payload = {
        "provider": "ollama",
        "model": "qwen3:8b",
        "real_provider_enabled": True,
        "llm_chat_enabled": True,
        "fallback_to_mock": False,
    }
    payload.update(overrides)
    response = client.patch("/provider/settings", json=payload)
    assert response.status_code == 200
    return response.json()


def post_chat(client, message="Hello!"):
    response = client.post("/chat", json={"message": message})
    assert response.status_code == 200
    return response.json()


def test_runtime_ollama_success_returns_llm_local(monkeypatch):
    fake = FakeOllamaSuccessProvider()
    captured_settings = {}

    def fake_factory(settings):
        captured_settings.update(settings)
        return fake

    monkeypatch.delenv("LLM_CHAT_ENABLED", raising=False)
    monkeypatch.delenv("LLM_PROVIDER_NAME", raising=False)
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider_from_runtime_settings",
        fake_factory,
    )

    with TestClient(app) as client:
        settings = patch_provider_settings(client)
        data = post_chat(client)
        usage = client.get("/provider/settings").json()["usage_summary"]

    assert settings["resolved_provider"] == "ollama"
    assert captured_settings["resolved_provider"] == "ollama"
    assert len(fake.calls) == 1
    assert data["reply"] == "local ollama route reply"
    assert data["source"] == "llm_local"
    assert set(data.keys()) == {"reply", "mood", "source"}
    assert usage["source_counts"]["llm_local"] == 1
    assert usage["provider_counts"]["ollama"] == 1
    assert usage["model_counts"]["qwen3:8b"] == 1


def test_runtime_ollama_failure_without_mock_fallback_does_not_return_mock(monkeypatch):
    fake = FakeOllamaErrorProvider(error="provider_timeout")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider_from_runtime_settings",
        lambda settings: fake,
    )

    with TestClient(app) as client:
        patch_provider_settings(client, fallback_to_mock=False)
        data = post_chat(client)
        usage = client.get("/provider/settings").json()["usage_summary"]

    assert len(fake.calls) == 1
    assert data["source"] == "llm_local_error"
    assert data["source"] != "mock"
    assert data["reply"] == LOCAL_PROVIDER_TIMEOUT_FALLBACK_TEXT
    assert "loading" in data["reply"].lower()
    assert "raw provider fallback text" not in data["reply"]
    assert usage["source_counts"]["llm_local_error"] == 1
    assert usage["fallback_count"] == 0
    assert usage["error_counts"]["provider_timeout"] == 1


def test_runtime_ollama_failure_with_mock_fallback_returns_mock_and_counts(monkeypatch):
    fake = FakeOllamaErrorProvider(error="provider_timeout")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider_from_runtime_settings",
        lambda settings: fake,
    )

    with TestClient(app) as client:
        patch_provider_settings(client, fallback_to_mock=True)
        data = post_chat(client)
        usage = client.get("/provider/settings").json()["usage_summary"]

    assert len(fake.calls) == 1
    assert data["source"] == "mock"
    assert usage["source_counts"]["mock"] == 1
    assert usage["provider_counts"]["ollama"] == 1
    assert usage["model_counts"]["qwen3:8b"] == 1
    assert usage["fallback_count"] == 1
    assert usage["error_counts"]["provider_timeout"] == 1


def test_runtime_llm_chat_disabled_returns_mock_without_provider_call(monkeypatch):
    def raise_if_called(settings):  # noqa: ARG001
        raise AssertionError("runtime provider factory should not be called")

    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider_from_runtime_settings",
        raise_if_called,
    )

    with TestClient(app) as client:
        patch_provider_settings(client, llm_chat_enabled=False)
        data = post_chat(client)

    assert data["source"] == "mock"
    assert set(data.keys()) == {"reply", "mood", "source"}


def test_runtime_provider_mock_returns_mock_without_provider_call(monkeypatch):
    def raise_if_called(settings):  # noqa: ARG001
        raise AssertionError("runtime provider factory should not be called")

    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider_from_runtime_settings",
        raise_if_called,
    )

    with TestClient(app) as client:
        patch_provider_settings(
            client,
            provider="mock",
            model=None,
            real_provider_enabled=True,
            llm_chat_enabled=True,
        )
        data = post_chat(client)

    assert data["source"] == "mock"
    assert set(data.keys()) == {"reply", "mood", "source"}


def test_runtime_resolved_provider_ollama_routes_to_ollama_provider(monkeypatch):
    fake = FakeOllamaSuccessProvider()
    seen_settings = {}

    def fake_factory(settings):
        seen_settings.update(settings)
        return fake

    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider_from_runtime_settings",
        fake_factory,
    )

    with TestClient(app) as client:
        patch_provider_settings(client)
        data = post_chat(client)

    assert seen_settings["provider"] == "ollama"
    assert seen_settings["resolved_provider"] == "ollama"
    assert data["source"] == "llm_local"
    assert len(fake.calls) == 1


def test_runtime_ollama_chat_schema_stays_reply_mood_source(monkeypatch):
    fake = FakeOllamaSuccessProvider()
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider_from_runtime_settings",
        lambda settings: fake,
    )

    with TestClient(app) as client:
        patch_provider_settings(client)
        data = post_chat(client)

    assert set(data.keys()) == {"reply", "mood", "source"}
