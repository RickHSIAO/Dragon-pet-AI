import os

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, func, select

from app.db.database import engine
from app.db.models import MemoryInjectionAudit, Message
from app.llm.types import LLMResponse
from app.main import app
from app.services.key_storage_service import (
    InMemoryKeyStorageBackend,
    reset_key_storage_backend_for_tests,
    save_api_key,
    set_key_storage_backend_for_tests,
)
from app.services.provider_settings_service import (
    ProviderSettingsUpdate,
    reset_provider_settings,
    update_provider_settings,
)
from app.services.provider_test_connection_service import (
    TEST_MAX_TOKENS,
    TEST_USER_MESSAGE,
    reset_provider_test_runner_for_tests,
    set_provider_test_runner_for_tests,
)
from app.services.usage_meter_service import get_usage_summary, reset_usage_meter


SECRET = "sk-test-connection-secret-should-not-appear"
RAW_BODY = "RAW_PROVIDER_BODY_SHOULD_NOT_APPEAR"


class FakeProviderTestRunner:
    def __init__(self, response=None, exc=None):
        self.response = response or LLMResponse(
            text="OK",
            provider="anthropic",
            model="claude-test",
            usage={"input_tokens": 4, "output_tokens": 1},
            error=None,
        )
        self.exc = exc
        self.calls = []

    def run(
        self,
        *,
        provider,
        api_key,
        model,
        request,
        timeout_seconds,
        max_tokens,
    ):
        self.calls.append({
            "provider": provider,
            "api_key_present": bool(api_key),
            "model": model,
            "request": request,
            "timeout_seconds": timeout_seconds,
            "max_tokens": max_tokens,
        })
        if self.exc:
            raise self.exc
        return self.response


@pytest.fixture(autouse=True)
def reset_state():
    reset_key_storage_backend_for_tests()
    reset_provider_test_runner_for_tests()
    reset_provider_settings()
    reset_usage_meter()
    yield
    reset_usage_meter()
    reset_provider_settings()
    reset_provider_test_runner_for_tests()
    reset_key_storage_backend_for_tests()


def configure_real_provider_with_key(runner=None, secret=SECRET):
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())
    save_api_key("anthropic", secret)
    update_provider_settings(ProviderSettingsUpdate(
        provider="anthropic",
        model="claude-test",
        real_provider_enabled=True,
    ))
    if runner is not None:
        set_provider_test_runner_for_tests(runner)


def post_test_connection(client, **overrides):
    payload = {
        "provider": "anthropic",
        "model": "claude-test",
        "explicit_cost_ack": True,
    }
    payload.update(overrides)
    return client.post("/provider/settings/test", json=payload)


def count_rows(model) -> int:
    with Session(engine) as session:
        return session.exec(select(func.count()).select_from(model)).one()


def test_missing_explicit_cost_ack_returns_cost_ack_required():
    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/test",
            json={"provider": "anthropic", "model": "claude-test"},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "cost_ack_required"}


def test_false_explicit_cost_ack_returns_cost_ack_required():
    with TestClient(app) as client:
        response = post_test_connection(client, explicit_cost_ack=False)

    assert response.status_code == 400
    assert response.json() == {"detail": "cost_ack_required"}


def test_mock_provider_is_rejected():
    with TestClient(app) as client:
        response = post_test_connection(client, provider="mock")

    assert response.status_code == 400
    assert response.json() == {"detail": "invalid_provider"}


def test_missing_key_returns_safe_failure_without_provider_call():
    runner = FakeProviderTestRunner()
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())
    set_provider_test_runner_for_tests(runner)
    update_provider_settings(ProviderSettingsUpdate(
        provider="anthropic",
        model="claude-test",
        real_provider_enabled=True,
    ))

    with TestClient(app) as client:
        response = post_test_connection(client)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error_category"] == "missing_key"
    assert data["source"] == "llm_real_error"
    assert runner.calls == []


def test_storage_unavailable_returns_safe_failure():
    update_provider_settings(ProviderSettingsUpdate(
        provider="anthropic",
        model="claude-test",
        real_provider_enabled=True,
    ))

    with TestClient(app) as client:
        response = post_test_connection(client)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error_category"] == "storage_unavailable"
    assert SECRET not in response.text


def test_fake_provider_success_returns_safe_response():
    runner = FakeProviderTestRunner()
    configure_real_provider_with_key(runner)

    with TestClient(app) as client:
        response = post_test_connection(client)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["provider"] == "anthropic"
    assert data["model"] == "claude-test"
    assert data["source"] == "llm_real"
    assert data["safe_message"] == "Provider test connection succeeded."
    assert data["error_category"] is None
    assert data["usage_estimate"] == {
        "input_tokens": 4,
        "output_tokens": 1,
        "total_tokens": 5,
    }
    assert SECRET not in response.text
    assert "api_key" not in response.text
    assert TEST_USER_MESSAGE not in response.text
    assert len(runner.calls) == 1


def test_fake_provider_auth_failure_maps_safely():
    runner = FakeProviderTestRunner(LLMResponse(
        text=RAW_BODY,
        provider="anthropic",
        model="claude-test",
        usage=None,
        error="provider_auth_error",
    ))
    configure_real_provider_with_key(runner)

    with TestClient(app) as client:
        response = post_test_connection(client)

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "failed"
    assert data["error_category"] == "provider_auth_error"
    assert RAW_BODY not in response.text
    assert SECRET not in response.text


def test_fake_provider_timeout_maps_safely():
    runner = FakeProviderTestRunner(exc=TimeoutError("timeout with secret"))
    configure_real_provider_with_key(runner)

    with TestClient(app) as client:
        response = post_test_connection(client)

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "failed"
    assert data["error_category"] == "provider_timeout"
    assert len(runner.calls) == 1
    assert SECRET not in response.text


def test_non_2xx_body_remains_opaque(caplog):
    runner = FakeProviderTestRunner(LLMResponse(
        text=RAW_BODY,
        provider="anthropic",
        model="claude-test",
        usage=None,
        error="provider_error",
    ))
    configure_real_provider_with_key(runner)

    with TestClient(app) as client:
        response = post_test_connection(client)

    assert response.status_code == 200
    assert response.json()["error_category"] == "provider_error"
    assert RAW_BODY not in response.text
    assert RAW_BODY not in caplog.text
    assert SECRET not in response.text


def test_no_retries_exactly_one_call_on_provider_error():
    runner = FakeProviderTestRunner(LLMResponse(
        text=RAW_BODY,
        provider="anthropic",
        model="claude-test",
        usage=None,
        error="rate_limit",
    ))
    configure_real_provider_with_key(runner)

    with TestClient(app) as client:
        response = post_test_connection(client)

    assert response.status_code == 200
    assert response.json()["error_category"] == "rate_limit"
    assert len(runner.calls) == 1


def test_minimal_request_uses_no_memory_history_tools_or_streaming():
    runner = FakeProviderTestRunner()
    configure_real_provider_with_key(runner)

    with TestClient(app) as client:
        response = post_test_connection(client)

    assert response.status_code == 200
    call = runner.calls[0]
    request = call["request"]
    assert request.user_message == TEST_USER_MESSAGE
    assert request.memory_context is None
    assert request.conversation_history is None
    assert request.state_context is None
    assert not hasattr(request, "tools")
    assert not hasattr(request, "stream")
    assert call["max_tokens"] == TEST_MAX_TOKENS


def test_api_key_absent_from_caplog_stdout_stderr(caplog, capsys):
    runner = FakeProviderTestRunner()
    configure_real_provider_with_key(runner)

    with TestClient(app) as client:
        response = post_test_connection(client)

    captured = capsys.readouterr()
    assert response.status_code == 200
    assert SECRET not in response.text
    assert SECRET not in caplog.text
    assert SECRET not in captured.out
    assert SECRET not in captured.err


def test_usage_meter_records_safe_aggregate():
    runner = FakeProviderTestRunner()
    configure_real_provider_with_key(runner)

    with TestClient(app) as client:
        response = post_test_connection(client)

    summary = get_usage_summary()
    assert response.status_code == 200
    assert summary.request_count == 1
    assert summary.source_counts == {"llm_real": 1}
    assert summary.provider_counts == {"anthropic": 1}
    assert summary.model_counts == {"claude-test": 1}
    assert summary.estimated_input_tokens == 4
    assert summary.estimated_output_tokens == 1
    assert summary.fallback_count == 0
    assert summary.memory_used_count == 0
    assert SECRET not in repr(summary)
    assert RAW_BODY not in repr(summary)


def test_test_connection_does_not_write_chat_history_or_memory_audit():
    runner = FakeProviderTestRunner()
    configure_real_provider_with_key(runner)

    with TestClient(app) as client:
        before_messages = count_rows(Message)
        before_audits = count_rows(MemoryInjectionAudit)
        response = post_test_connection(client)
        after_messages = count_rows(Message)
        after_audits = count_rows(MemoryInjectionAudit)

    assert response.status_code == 200
    assert after_messages == before_messages
    assert after_audits == before_audits


def test_test_connection_does_not_call_external_http(monkeypatch):
    runner = FakeProviderTestRunner()
    configure_real_provider_with_key(runner)

    def raise_if_http_called(*args, **kwargs):
        raise AssertionError("external HTTP must not be called")

    monkeypatch.setattr("httpx.request", raise_if_http_called)

    with TestClient(app) as client:
        response = post_test_connection(client)

    assert response.status_code == 200
    assert len(runner.calls) == 1


def test_chat_old_format_still_returns_200_and_schema_unchanged():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}
