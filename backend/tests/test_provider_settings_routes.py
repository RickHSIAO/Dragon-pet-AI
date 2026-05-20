import os

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.provider_settings_service import reset_provider_settings
from app.services.usage_meter_service import (
    UsageRecord,
    record_usage,
    reset_usage_meter,
)


@pytest.fixture(autouse=True)
def reset_settings_and_usage():
    reset_provider_settings()
    reset_usage_meter()
    yield
    reset_provider_settings()
    reset_usage_meter()


def test_get_provider_settings_returns_safe_defaults():
    with TestClient(app) as client:
        response = client.get("/provider/settings")

    data = response.json()
    assert response.status_code == 200
    assert data["provider"] == "mock"
    assert data["model"] is None
    assert data["real_provider_enabled"] is False
    assert data["llm_chat_enabled"] is False
    assert data["fallback_to_mock"] is True
    assert data["key_status"] == "not_configured"
    assert data["resolved_provider"] == "mock"
    assert data["last_test_status"] == "not_tested"


def test_get_provider_settings_never_returns_api_key(monkeypatch):
    secret = "sk-route-secret-should-not-appear"
    monkeypatch.setenv("LLM_API_KEY", secret)

    with TestClient(app) as client:
        response = client.get("/provider/settings")

    observed = response.text
    assert response.status_code == 200
    assert secret not in observed
    assert "api_key" not in observed
    assert '"key"' not in observed


def test_get_provider_settings_includes_safe_usage_summary_only():
    raw_message = "RAW_MESSAGE_NOT_ALLOWED_IN_PROVIDER_SETTINGS"
    record_usage(UsageRecord(
        source="mock",
        estimated_input_tokens=len(raw_message),
        estimated_output_tokens=2,
    ))

    with TestClient(app) as client:
        response = client.get("/provider/settings")

    usage = response.json()["usage_summary"]
    observed = repr(usage)
    assert response.status_code == 200
    assert set(usage.keys()) == {
        "request_count",
        "source_counts",
        "provider_counts",
        "model_counts",
        "estimated_input_tokens",
        "estimated_output_tokens",
        "estimated_total_tokens",
        "fallback_count",
        "memory_used_count",
        "error_counts",
    }
    assert usage["request_count"] == 1
    assert raw_message not in observed
    assert "api_key" not in observed
    assert "prompt" not in observed
    assert "memory_context" not in observed
    assert "raw_provider_response" not in observed


def test_patch_provider_settings_updates_non_secret_fields():
    with TestClient(app) as client:
        response = client.patch(
            "/provider/settings",
            json={
                "provider": "anthropic",
                "model": "claude-test",
                "real_provider_enabled": True,
                "llm_chat_enabled": True,
                "fallback_to_mock": False,
            },
        )

    data = response.json()
    assert response.status_code == 200
    assert data["provider"] == "anthropic"
    assert data["model"] == "claude-test"
    assert data["real_provider_enabled"] is True
    assert data["llm_chat_enabled"] is True
    assert data["fallback_to_mock"] is False
    assert data["key_status"] == "not_configured"
    assert data["resolved_provider"] == "safe_fallback"


def test_patch_provider_settings_rejects_api_key_field_without_echoing_value():
    secret = "sk-patch-secret-should-not-appear"

    with TestClient(app) as client:
        response = client.patch(
            "/provider/settings",
            json={"provider": "mock", "api_key": secret},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "unsupported setting field"}
    assert secret not in response.text


def test_patch_provider_settings_rejects_key_field_without_echoing_value():
    secret = "raw-key-value-should-not-appear"

    with TestClient(app) as client:
        response = client.patch(
            "/provider/settings",
            json={"key": secret},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "unsupported setting field"}
    assert secret not in response.text


def test_patch_provider_settings_rejects_unknown_dangerous_field():
    with TestClient(app) as client:
        response = client.patch(
            "/provider/settings",
            json={"prompt": "raw prompt should not be accepted"},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "unsupported setting field"}
    assert "raw prompt should not be accepted" not in response.text


def test_patch_provider_settings_does_not_call_external_api(monkeypatch):
    def raise_if_provider_called():
        raise AssertionError("provider factory must not be called")

    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        raise_if_provider_called,
    )

    with TestClient(app) as client:
        response = client.patch(
            "/provider/settings",
            json={"provider": "anthropic", "real_provider_enabled": True},
        )

    assert response.status_code == 200


def test_post_provider_settings_key_is_safe_placeholder():
    secret = "sk-placeholder-secret-should-not-appear"

    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/key",
            json={"provider": "anthropic", "api_key": secret},
        )

    assert response.status_code == 501
    assert response.json()["status"] == "not_implemented"
    assert secret not in response.text
    assert "api_key" not in response.text


def test_delete_provider_settings_key_is_safe_placeholder():
    with TestClient(app) as client:
        response = client.delete("/provider/settings/key")

    assert response.status_code == 501
    assert response.json()["status"] == "not_implemented"
    assert "api_key" not in response.text


def test_post_provider_settings_test_is_safe_placeholder():
    secret = "sk-test-secret-should-not-appear"

    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/test",
            json={"provider": "anthropic", "api_key": secret},
        )

    assert response.status_code == 501
    assert response.json()["status"] == "not_implemented"
    assert secret not in response.text
    assert "api_key" not in response.text


def test_chat_old_format_still_returns_200_and_schema_unchanged():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}
