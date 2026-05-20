import os

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.key_storage_service import (
    InMemoryKeyStorageBackend,
    clear_api_key,
    get_api_key,
    get_key_status,
    reset_key_storage_backend_for_tests,
    save_api_key,
    set_key_storage_backend_for_tests,
)
from app.services.provider_settings_service import (
    ProviderSettingsUpdate,
    reset_provider_settings,
    update_provider_settings,
)
from app.services.usage_meter_service import reset_usage_meter


@pytest.fixture(autouse=True)
def reset_storage_and_settings():
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())
    reset_provider_settings()
    reset_usage_meter()
    yield
    reset_provider_settings()
    reset_usage_meter()
    reset_key_storage_backend_for_tests()


def test_initial_key_status_is_not_configured():
    assert get_key_status("anthropic") == "not_configured"


def test_save_key_sets_status_configured():
    save_api_key("anthropic", "sk-test-storage-secret")
    assert get_key_status("anthropic") == "configured"


def test_get_key_returns_key_only_through_backend_service():
    secret = "sk-backend-only-secret"
    save_api_key("anthropic", secret)
    assert get_api_key("anthropic") == secret


def test_clear_key_removes_key():
    save_api_key("anthropic", "sk-clear-secret")
    clear_api_key("anthropic")
    assert get_api_key("anthropic") is None
    assert get_key_status("anthropic") == "not_configured"


def test_clear_key_is_idempotent():
    clear_api_key("anthropic")
    clear_api_key("anthropic")
    assert get_key_status("anthropic") == "not_configured"


def test_replace_key_overwrites_old_key():
    old_secret = "sk-old-secret"
    new_secret = "sk-new-secret"
    backend = InMemoryKeyStorageBackend()
    set_key_storage_backend_for_tests(backend)
    save_api_key("anthropic", old_secret)
    save_api_key("anthropic", new_secret)

    assert get_api_key("anthropic") == new_secret
    assert old_secret not in repr(backend)
    assert new_secret not in repr(backend)


def test_empty_key_is_rejected():
    with pytest.raises(ValueError, match="api key is required"):
        save_api_key("anthropic", "   ")


def test_unknown_provider_is_rejected():
    with pytest.raises(ValueError, match="unsupported provider"):
        save_api_key("unknown", "sk-test-secret")


def test_repr_and_str_do_not_expose_key():
    secret = "sk-repr-secret-should-not-appear"
    backend = InMemoryKeyStorageBackend()
    backend.save_api_key("anthropic", secret)

    assert secret not in repr(backend)
    assert secret not in str(backend)
    assert "<redacted>" in repr(backend)


def test_caplog_does_not_contain_key(caplog):
    secret = "sk-caplog-secret-should-not-appear"
    save_api_key("anthropic", secret)
    clear_api_key("anthropic")

    assert secret not in caplog.text


def test_stdout_stderr_do_not_contain_key(capsys):
    secret = "sk-stdio-secret-should-not-appear"
    save_api_key("anthropic", secret)
    clear_api_key("anthropic")

    captured = capsys.readouterr()
    assert secret not in captured.out
    assert secret not in captured.err


def test_no_sqlite_model_or_table_added_for_key_storage():
    import app.db.models as models_module

    forbidden_fragments = ("Key", "Secret", "Credential", "Token")
    for name in dir(models_module):
        if name.startswith("__"):
            continue
        assert not any(fragment in name for fragment in forbidden_fragments), (
            f"key storage must not add SQLite model/table: {name}"
        )


def test_provider_settings_get_response_does_not_include_key():
    secret = "sk-route-storage-secret-should-not-appear"
    save_api_key("anthropic", secret)
    update_provider_settings(ProviderSettingsUpdate(
        provider="anthropic",
        real_provider_enabled=True,
        llm_chat_enabled=True,
    ))

    with TestClient(app) as client:
        response = client.get("/provider/settings")

    assert response.status_code == 200
    assert response.json()["key_status"] == "configured"
    assert response.json()["resolved_provider"] == "anthropic"
    assert secret not in response.text
    assert "api_key" not in response.text


def test_placeholder_key_endpoint_remains_safe():
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


def test_placeholder_test_endpoint_remains_safe_and_no_external_call(monkeypatch):
    secret = "sk-test-placeholder-secret-should-not-appear"

    def raise_if_llm_provider_called():
        raise AssertionError("provider factory must not be called")

    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        raise_if_llm_provider_called,
    )

    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/test",
            json={"provider": "anthropic", "api_key": secret},
        )

    assert response.status_code == 501
    assert response.json()["status"] == "not_implemented"
    assert secret not in response.text
    assert "api_key" not in response.text
