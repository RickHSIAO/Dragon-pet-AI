import os

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.key_storage_service import (
    InMemoryKeyStorageBackend,
    get_api_key,
    reset_key_storage_backend_for_tests,
    set_key_storage_backend_for_tests,
)
from app.services.provider_settings_service import (
    ProviderSettingsUpdate,
    reset_provider_settings,
    update_provider_settings,
)
from app.services.usage_meter_service import (
    UsageRecord,
    record_usage,
    reset_usage_meter,
)


@pytest.fixture(autouse=True)
def reset_settings_and_usage():
    reset_key_storage_backend_for_tests()
    reset_provider_settings()
    reset_usage_meter()
    yield
    reset_provider_settings()
    reset_usage_meter()
    reset_key_storage_backend_for_tests()


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


def test_partial_patch_preserves_existing_model_and_fallback_to_mock():
    with TestClient(app) as client:
        first = client.patch(
            "/provider/settings",
            json={
                "provider": "ollama",
                "model": "qwen3:8b",
                "real_provider_enabled": True,
                "llm_chat_enabled": True,
                "fallback_to_mock": False,
            },
        )
        assert first.status_code == 200

        response = client.patch("/provider/settings", json={"provider": "ollama"})
        data = response.json()

    assert response.status_code == 200
    assert data["provider"] == "ollama"
    assert data["model"] == "qwen3:8b"
    assert data["fallback_to_mock"] is False


def test_explicit_null_model_does_not_clear_existing_model():
    with TestClient(app) as client:
        first = client.patch(
            "/provider/settings",
            json={
                "provider": "ollama",
                "model": "qwen3:8b",
                "real_provider_enabled": True,
                "llm_chat_enabled": True,
                "fallback_to_mock": False,
            },
        )
        assert first.status_code == 200

        response = client.patch("/provider/settings", json={"model": None})
        data = response.json()

    assert response.status_code == 200
    assert data["model"] == "qwen3:8b"
    assert data["fallback_to_mock"] is False


def test_provider_test_connection_does_not_mutate_provider_settings(monkeypatch):
    def fake_test_connection(provider, model=None, explicit_cost_ack=False):
        return {
            "status": "success",
            "provider": provider,
            "model": model or "qwen3:8b",
            "source": "llm_local",
            "safe_message": "Local Ollama connection successful.",
            "error_category": None,
            "usage_estimate": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
        }

    monkeypatch.setattr(
        "app.api.routes.run_provider_test_connection",
        fake_test_connection,
    )

    with TestClient(app) as client:
        first = client.patch(
            "/provider/settings",
            json={
                "provider": "ollama",
                "model": "qwen3:8b",
                "real_provider_enabled": True,
                "llm_chat_enabled": True,
                "fallback_to_mock": False,
            },
        )
        assert first.status_code == 200

        test = client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": True},
        )
        settings = client.get("/provider/settings").json()

    assert test.status_code == 200
    assert settings["provider"] == "ollama"
    assert settings["model"] == "qwen3:8b"
    assert settings["fallback_to_mock"] is False


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


def test_post_provider_settings_key_rejects_empty_key_without_echoing_value():
    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/key",
            json={"provider": "anthropic", "api_key": "   "},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "api key is required"}


def test_post_provider_settings_key_rejects_mock_provider():
    secret = "sk-mock-provider-secret-should-not-appear"

    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/key",
            json={"provider": "mock", "api_key": secret},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "mock provider cannot store an api key"}
    assert secret not in response.text


def test_post_provider_settings_key_rejects_unknown_provider():
    secret = "sk-unknown-provider-secret-should-not-appear"

    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/key",
            json={"provider": "unknown", "api_key": secret},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "unsupported provider"}
    assert secret not in response.text


def test_post_provider_settings_key_unavailable_storage_fails_safely():
    secret = "sk-placeholder-secret-should-not-appear"

    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/key",
            json={"provider": "anthropic", "api_key": secret},
        )

    assert response.status_code == 503
    assert response.json() == {"detail": "secure key storage is unavailable"}
    assert secret not in response.text
    assert "api_key" not in response.text


def test_post_provider_settings_key_with_fake_backend_succeeds():
    secret = "sk-fake-route-secret-should-not-appear"
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())

    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/key",
            json={"provider": "anthropic", "api_key": secret},
        )

    assert response.status_code == 200
    assert response.json() == {
        "provider": "anthropic",
        "key_status": "configured",
        "message": "API key saved.",
    }
    assert get_api_key("anthropic") == secret
    assert secret not in response.text
    assert "api_key" not in response.text


def test_post_provider_settings_key_does_not_expose_key_in_caplog(caplog):
    secret = "sk-caplog-route-secret-should-not-appear"
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())

    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/key",
            json={"provider": "anthropic", "api_key": secret},
        )

    assert response.status_code == 200
    assert secret not in caplog.text


def test_post_provider_settings_key_does_not_expose_key_in_stdout_stderr(capsys):
    secret = "sk-stdio-route-secret-should-not-appear"
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())

    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/key",
            json={"provider": "anthropic", "api_key": secret},
        )

    captured = capsys.readouterr()
    assert response.status_code == 200
    assert secret not in captured.out
    assert secret not in captured.err


def test_get_provider_settings_after_fake_save_returns_key_status_configured():
    secret = "sk-status-route-secret-should-not-appear"
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())
    update_provider_settings(ProviderSettingsUpdate(provider="anthropic"))

    with TestClient(app) as client:
        save_response = client.post(
            "/provider/settings/key",
            json={"provider": "anthropic", "api_key": secret},
        )
        settings_response = client.get("/provider/settings")

    assert save_response.status_code == 200
    assert settings_response.status_code == 200
    assert settings_response.json()["key_status"] == "configured"
    assert secret not in settings_response.text
    assert "api_key" not in settings_response.text


def test_delete_provider_settings_key_clears_key_with_fake_backend():
    secret = "sk-delete-route-secret-should-not-appear"
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())

    with TestClient(app) as client:
        client.post(
            "/provider/settings/key",
            json={"provider": "anthropic", "api_key": secret},
        )
        response = client.delete("/provider/settings/key?provider=anthropic")

    assert response.status_code == 200
    assert response.json() == {
        "provider": "anthropic",
        "key_status": "not_configured",
        "message": "API key cleared.",
    }
    assert get_api_key("anthropic") is None
    assert secret not in response.text
    assert "api_key" not in response.text


def test_delete_provider_settings_key_is_idempotent_with_fake_backend():
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())

    with TestClient(app) as client:
        first = client.delete("/provider/settings/key?provider=anthropic")
        second = client.delete("/provider/settings/key?provider=anthropic")

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["key_status"] == "not_configured"


def test_replacing_provider_settings_key_overwrites_old_key():
    old_secret = "sk-old-route-secret-should-not-appear"
    new_secret = "sk-new-route-secret-should-not-appear"
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())

    with TestClient(app) as client:
        first = client.post(
            "/provider/settings/key",
            json={"provider": "anthropic", "api_key": old_secret},
        )
        second = client.post(
            "/provider/settings/key",
            json={"provider": "anthropic", "api_key": new_secret},
        )

    assert first.status_code == 200
    assert second.status_code == 200
    assert get_api_key("anthropic") == new_secret
    assert old_secret not in second.text
    assert new_secret not in second.text


def test_provider_settings_key_endpoints_do_not_call_external_api(monkeypatch):
    secret = "sk-no-external-route-secret-should-not-appear"
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())

    def raise_if_llm_provider_called():
        raise AssertionError("provider factory must not be called")

    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        raise_if_llm_provider_called,
    )

    with TestClient(app) as client:
        save_response = client.post(
            "/provider/settings/key",
            json={"provider": "anthropic", "api_key": secret},
        )
        clear_response = client.delete("/provider/settings/key?provider=anthropic")

    assert save_response.status_code == 200
    assert clear_response.status_code == 200
    assert secret not in save_response.text
    assert secret not in clear_response.text


def test_delete_provider_settings_key_unavailable_storage_fails_safely():
    with TestClient(app) as client:
        response = client.delete("/provider/settings/key?provider=anthropic")

    assert response.status_code == 503
    assert response.json() == {"detail": "secure key storage is unavailable"}


def test_post_provider_settings_test_rejects_api_key_field():
    secret = "sk-test-secret-should-not-appear"

    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/test",
            json={"provider": "anthropic", "api_key": secret},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "unsupported test field"}
    assert secret not in response.text
    assert "api_key" not in response.text


def test_chat_old_format_still_returns_200_and_schema_unchanged():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}
