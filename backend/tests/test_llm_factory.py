import pytest
from app.llm.factory import get_llm_provider, get_resolved_llm_provider_info
from app.llm.mock_provider import MockLLMProvider
from app.llm.real_provider import (
    CANONICAL_SAFE_FALLBACK_TEXT,
    HTTPRealLLMProvider,
    SafeFallbackLLMProvider,
)
from app.llm.types import LLMRequest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def clear_llm_env(monkeypatch):
    for name in (
        "LLM_PROVIDER_ENABLED",
        "LLM_PROVIDER_NAME",
        "LLM_API_KEY",
        "LLM_MODEL",
        "LLM_TIMEOUT_SECONDS",
        "LLM_FALLBACK_TO_MOCK",
    ):
        monkeypatch.delenv(name, raising=False)


def test_get_llm_provider_returns_mock_provider():
    provider = get_llm_provider()

    assert isinstance(provider, MockLLMProvider)
    assert provider.provider_name == "mock"


def test_disabled_flag_returns_mock_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "false")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "openai")
    monkeypatch.setenv("LLM_API_KEY", "sk-test-secret-value")

    provider = get_llm_provider()

    assert isinstance(provider, MockLLMProvider)


def test_factory_does_not_require_api_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    provider = get_llm_provider()

    assert isinstance(provider, MockLLMProvider)
    assert provider.health_check() is True


def test_factory_ignores_external_provider_config(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "real-provider-should-not-load")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")

    provider = get_llm_provider()

    assert isinstance(provider, MockLLMProvider)
    assert provider.provider_name == "mock"


def test_provider_name_mock_returns_mock_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "mock")
    monkeypatch.setenv("LLM_API_KEY", "sk-test-secret-value")

    provider = get_llm_provider()

    assert isinstance(provider, MockLLMProvider)


def test_unknown_provider_returns_mock_with_safe_warning(monkeypatch, caplog):
    key = "sk-test-secret-value"
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "unknown")
    monkeypatch.setenv("LLM_API_KEY", key)

    provider = get_llm_provider()

    assert isinstance(provider, MockLLMProvider)
    assert key not in caplog.text
    assert "falling back to mock" in caplog.text


def test_real_provider_missing_key_fallback_true_returns_mock(monkeypatch, caplog):
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "openai")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("LLM_FALLBACK_TO_MOCK", "true")

    provider = get_llm_provider()

    assert isinstance(provider, MockLLMProvider)
    assert "api key missing" in caplog.text.lower()


def test_real_provider_missing_key_fallback_false_returns_safe_provider(monkeypatch, caplog):
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "openai")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("LLM_FALLBACK_TO_MOCK", "false")

    provider = get_llm_provider()

    assert isinstance(provider, SafeFallbackLLMProvider)
    assert provider.provider_name == "safe_fallback"
    assert "api key missing" in caplog.text.lower()

    response = provider.generate(LLMRequest(system_prompt="system", user_message="hello"))
    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "provider_unavailable"


def test_real_provider_with_key_returns_real_adapter(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "openai")
    monkeypatch.setenv("LLM_API_KEY", "sk-test-secret-value")

    provider = get_llm_provider()

    assert isinstance(provider, HTTPRealLLMProvider)
    assert provider.provider_name == "openai"


def test_resolved_provider_info_contains_no_key(monkeypatch):
    key = "sk-test-secret-value"
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "openai")
    monkeypatch.setenv("LLM_API_KEY", key)

    info = get_resolved_llm_provider_info()

    assert info == {
        "provider": "openai",
        "enabled": True,
        "reason": "real_provider_enabled",
    }
    assert key not in repr(info)


def test_chat_old_format_still_returns_200():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200


def test_chat_response_schema_remains_reply_mood_source():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}
