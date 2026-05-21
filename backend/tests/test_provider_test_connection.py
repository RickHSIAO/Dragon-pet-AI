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


# ── TASK-062: Opus review hardening tests ─────────────────────────────────


def test_provider_disabled_with_configured_key_returns_safe_failure():
    """Test A — provider_disabled branch with configured key.

    Runner must NOT be called when real_provider_enabled=False,
    even when a key is present in key storage.
    """
    runner = FakeProviderTestRunner()
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())
    save_api_key("anthropic", SECRET)
    update_provider_settings(ProviderSettingsUpdate(
        provider="anthropic",
        model="claude-test",
        real_provider_enabled=False,
    ))
    set_provider_test_runner_for_tests(runner)

    with TestClient(app) as client:
        response = post_test_connection(client)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error_category"] == "provider_disabled"
    assert data["source"] == "llm_real_error"
    assert runner.calls == [], "runner must not be called when provider is disabled"
    assert SECRET not in response.text
    assert "api_key" not in response.text


def test_invalid_model_returns_400_without_provider_call():
    """Test B — invalid_model branch.

    When neither the request nor settings carry a non-empty model,
    the endpoint must return 400 invalid_model before the runner is called.
    """
    runner = FakeProviderTestRunner()
    set_key_storage_backend_for_tests(InMemoryKeyStorageBackend())
    save_api_key("anthropic", SECRET)
    update_provider_settings(ProviderSettingsUpdate(
        provider="anthropic",
        real_provider_enabled=True,
        # model intentionally omitted — settings.model stays None/empty
    ))
    set_provider_test_runner_for_tests(runner)

    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/test",
            json={"provider": "anthropic", "explicit_cost_ack": True},
            # no model field in request body
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "invalid_model"}
    assert runner.calls == [], "runner must not be called when model is invalid"
    assert SECRET not in response.text


def test_unknown_runner_error_collapses_to_provider_error():
    """Test C — unknown provider error collapses to provider_error.

    Unrecognized error strings must map to the safe 'provider_error'
    category and must not leak the raw unknown string in the response.
    """
    UNKNOWN_ERROR = "weird_internal_error_xyz_should_not_leak"
    runner = FakeProviderTestRunner(
        response=LLMResponse(
            text="",
            provider="anthropic",
            model="claude-test",
            usage=None,
            error=UNKNOWN_ERROR,
        )
    )
    configure_real_provider_with_key(runner)

    with TestClient(app) as client:
        response = post_test_connection(client)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error_category"] == "provider_error", (
        "unknown error string must collapse to 'provider_error'"
    )
    assert data["source"] == "llm_real_error"
    assert UNKNOWN_ERROR not in response.text, (
        "raw unknown error string must not appear in response"
    )
    assert SECRET not in response.text


def test_extra_field_rejected_without_echoing_value():
    """Test D — suspicious extra field rejected without echoing the value.

    Extra request fields (e.g., system_prompt) must be rejected by the
    schema (ConfigDict extra='forbid'). The field value must not appear
    in the response, and the runner must not be called.
    """
    runner = FakeProviderTestRunner()
    configure_real_provider_with_key(runner)
    LEAK_SENTINEL = "EXTRA_FIELD_LEAK_SENTINEL_XYZ"

    with TestClient(app) as client:
        response = client.post(
            "/provider/settings/test",
            json={
                "provider": "anthropic",
                "model": "claude-test",
                "explicit_cost_ack": True,
                "system_prompt": LEAK_SENTINEL,
            },
        )

    # Must be rejected — not processed successfully
    assert response.status_code != 200, (
        "extra field must cause request rejection (not 200)"
    )
    # Runner must not be called
    assert runner.calls == [], "runner must not be called when extra field is present"
    # The sentinel value must not appear in the response
    assert LEAK_SENTINEL not in response.text, (
        "extra field value must not be echoed back in response"
    )
    assert SECRET not in response.text


def test_safe_message_category_sweep():
    """Test E — safe_message category sweep.

    Every error category defined in SAFE_ERROR_MESSAGES must have:
    - A non-empty safe message string
    - No API key sentinel value
    - No raw body sentinel value
    - No prompt text sentinel value
    - A reasonable length (more than 5 chars, fewer than 200 chars)
    """
    from app.services.provider_test_connection_service import (
        SAFE_ERROR_MESSAGES,
        TEST_USER_MESSAGE,
    )

    API_KEY_SENTINEL  = "sk-sentinel-key-value-must-not-appear"
    RAW_BODY_SENTINEL = "RAW_PROVIDER_BODY_MUST_NOT_APPEAR"
    PROMPT_SENTINEL   = TEST_USER_MESSAGE  # "Reply with OK."

    for category, safe_msg in SAFE_ERROR_MESSAGES.items():
        assert safe_msg, (
            f"safe_message for '{category}' must not be empty"
        )
        assert API_KEY_SENTINEL not in safe_msg, (
            f"safe_message for '{category}' must not contain API key sentinel"
        )
        assert RAW_BODY_SENTINEL not in safe_msg, (
            f"safe_message for '{category}' must not contain raw body sentinel"
        )
        assert PROMPT_SENTINEL not in safe_msg, (
            f"safe_message for '{category}' must not contain prompt text"
        )
        assert 5 < len(safe_msg) < 200, (
            f"safe_message for '{category}' has unexpected length: {len(safe_msg)}"
        )



# ---------------------------------------------------------------------------
# TASK-076 / TASK-078: Ollama local provider test connection tests
# ---------------------------------------------------------------------------
#
# TASK-078: Test Connection no longer calls ``OllamaLocalProvider.generate()``.
# Instead it calls ``OllamaLocalProvider.test_connection(model)`` which does a
# single ``GET /api/tags`` to verify server-alive + model-installed.  This
# avoids the cold-start generation timeout that caused TASK-077R flakiness.

class _FakeOllamaSuccess:
    """OllamaLocalProvider stub that returns a valid Test Connection result."""
    def __init__(self, **kwargs):
        self._model = kwargs.get("model", "qwen3:8b")

    def test_connection(self, model=None):
        return LLMResponse(
            text="ok",
            provider="ollama",
            model=(model or self._model),
            usage=None,
            error=None,
        )


class _FakeOllamaUnavailable:
    """Simulates Ollama server not running."""
    def __init__(self, **kwargs):
        pass

    def test_connection(self, model=None):
        return LLMResponse(
            text="",
            provider="ollama",
            model=(model or "qwen3:8b"),
            usage=None,
            error="ollama_unavailable",
        )


class _FakeOllamaModelNotFound:
    """Simulates server alive but model not installed."""
    def __init__(self, **kwargs):
        pass

    def test_connection(self, model=None):
        return LLMResponse(
            text="",
            provider="ollama",
            model=(model or "qwen3:8b"),
            usage=None,
            error="model_not_found",
        )


class _FakeOllamaTimeout:
    """Simulates /api/tags timing out."""
    def __init__(self, **kwargs):
        pass

    def test_connection(self, model=None):
        return LLMResponse(
            text="",
            provider="ollama",
            model=(model or "qwen3:8b"),
            usage=None,
            error="provider_timeout",
        )


def _enable_ollama_provider():
    update_provider_settings(ProviderSettingsUpdate(
        provider="ollama",
        real_provider_enabled=True,
        llm_chat_enabled=True,
        fallback_to_mock=True,
    ))


def test_ollama_success_does_not_require_api_key(monkeypatch):
    """Ollama test connection must succeed without an API key."""
    _enable_ollama_provider()
    monkeypatch.setattr(
        "app.services.provider_test_connection_service.OllamaLocalProvider",
        _FakeOllamaSuccess,
    )
    with TestClient(app) as client:
        result = client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": True},
        )
    assert result.status_code == 200
    data = result.json()
    assert data["status"] == "success"
    assert data["source"] == "llm_local"


def test_ollama_success_source_is_llm_local(monkeypatch):
    """Successful Ollama test must return source=llm_local, not llm_real."""
    _enable_ollama_provider()
    monkeypatch.setattr(
        "app.services.provider_test_connection_service.OllamaLocalProvider",
        _FakeOllamaSuccess,
    )
    with TestClient(app) as client:
        result = client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": True},
        )
    data = result.json()
    assert data["source"] == "llm_local"
    assert data["status"] == "success"


def test_ollama_provider_disabled_returns_safe_failure(monkeypatch):
    """When real_provider_enabled=False, Ollama test must return provider_disabled."""
    update_provider_settings(ProviderSettingsUpdate(
        provider="ollama",
        real_provider_enabled=False,
        llm_chat_enabled=True,
        fallback_to_mock=True,
    ))
    monkeypatch.setattr(
        "app.services.provider_test_connection_service.OllamaLocalProvider",
        _FakeOllamaSuccess,
    )
    with TestClient(app) as client:
        result = client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": True},
        )
    assert result.status_code == 200
    data = result.json()
    assert data["status"] == "failed"
    assert data["error_category"] == "provider_disabled"
    assert data["source"] == "llm_local_error"


def test_ollama_unavailable_returns_safe_failure(monkeypatch):
    """Ollama server down must return failed status, not 500."""
    _enable_ollama_provider()
    monkeypatch.setattr(
        "app.services.provider_test_connection_service.OllamaLocalProvider",
        _FakeOllamaUnavailable,
    )
    with TestClient(app) as client:
        result = client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": True},
        )
    assert result.status_code == 200
    data = result.json()
    assert data["status"] == "failed"
    assert data["error_category"] == "ollama_unavailable"
    assert data["source"] == "llm_local_error"


def test_ollama_unavailable_safe_message_points_to_ollama_serve(monkeypatch):
    """TASK-078: ollama_unavailable safe_message must point at 'ollama serve'."""
    _enable_ollama_provider()
    monkeypatch.setattr(
        "app.services.provider_test_connection_service.OllamaLocalProvider",
        _FakeOllamaUnavailable,
    )
    with TestClient(app) as client:
        result = client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": True},
        )
    data = result.json()
    assert "ollama serve" in data["safe_message"].lower()


def test_ollama_model_not_found_maps_safely(monkeypatch):
    """Model not installed must map to safe error_category, not 500."""
    _enable_ollama_provider()
    monkeypatch.setattr(
        "app.services.provider_test_connection_service.OllamaLocalProvider",
        _FakeOllamaModelNotFound,
    )
    with TestClient(app) as client:
        result = client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": True},
        )
    assert result.status_code == 200
    data = result.json()
    assert data["status"] == "failed"
    assert data["error_category"] == "model_not_found"
    assert data["source"] == "llm_local_error"
    assert "ollama pull" in data["safe_message"].lower()


def test_ollama_timeout_returns_local_timeout_safe_message(monkeypatch):
    """TASK-078: /api/tags timeout must use the local-runtime safe_message."""
    _enable_ollama_provider()
    monkeypatch.setattr(
        "app.services.provider_test_connection_service.OllamaLocalProvider",
        _FakeOllamaTimeout,
    )
    with TestClient(app) as client:
        result = client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": True},
        )
    assert result.status_code == 200
    data = result.json()
    assert data["status"] == "failed"
    assert data["error_category"] == "provider_timeout"
    assert data["source"] == "llm_local_error"
    # Local timeout message must point to Ollama, not a paid provider.
    assert "ollama" in data["safe_message"].lower()
    # Must not blame the user for a missing API key on a timeout.
    assert "api key" not in data["safe_message"].lower()


def test_ollama_model_falls_back_to_default_when_unset(monkeypatch):
    """With no model configured, Ollama test must use qwen3:8b."""
    update_provider_settings(ProviderSettingsUpdate(
        provider="ollama",
        model=None,
        real_provider_enabled=True,
        llm_chat_enabled=True,
        fallback_to_mock=True,
    ))
    captured = {}

    class _CapturingOllama:
        def __init__(self, **kwargs):
            captured["constructor_model"] = kwargs.get("model")

        def test_connection(self, model=None):
            captured["test_connection_model"] = model
            return LLMResponse(
                text="ok",
                provider="ollama",
                model=(model or captured["constructor_model"]),
                usage=None,
                error=None,
            )

    monkeypatch.setattr(
        "app.services.provider_test_connection_service.OllamaLocalProvider",
        _CapturingOllama,
    )
    with TestClient(app) as client:
        client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": True},
        )
    assert captured["constructor_model"] == "qwen3:8b"
    assert captured["test_connection_model"] == "qwen3:8b"


def test_ollama_cost_ack_still_required():
    """explicit_cost_ack must still be required for local providers."""
    _enable_ollama_provider()
    with TestClient(app) as client:
        result = client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": False},
        )
    assert result.status_code == 400
    assert result.json()["detail"] == "cost_ack_required"


def test_ollama_test_does_not_call_generate(monkeypatch):
    """TASK-078: Test Connection must NOT invoke generate() — only test_connection()."""
    _enable_ollama_provider()
    call_log = []

    class _ChatCheckingOllama:
        def __init__(self, **kwargs):
            pass

        def test_connection(self, model=None):
            call_log.append(("test_connection", model))
            return LLMResponse(
                text="ok",
                provider="ollama",
                model=(model or "qwen3:8b"),
                usage=None,
                error=None,
            )

        def generate(self, request):
            call_log.append(("generate", request))
            raise AssertionError(
                "generate() must NOT be called by Test Connection — "
                "TASK-078 uses /api/tags only."
            )

    monkeypatch.setattr(
        "app.services.provider_test_connection_service.OllamaLocalProvider",
        _ChatCheckingOllama,
    )
    with TestClient(app) as client:
        result = client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": True},
        )
    assert result.status_code == 200
    assert result.json()["status"] == "success"
    assert call_log == [("test_connection", "qwen3:8b")]


def test_ollama_no_retries_exactly_one_test_connection_call(monkeypatch):
    """Ollama test must call test_connection() exactly once on exception, no retries."""
    _enable_ollama_provider()
    call_count = [0]

    class _CrashingOllama:
        def __init__(self, **kwargs):
            pass

        def test_connection(self, model=None):
            call_count[0] += 1
            raise RuntimeError("simulated crash")

    monkeypatch.setattr(
        "app.services.provider_test_connection_service.OllamaLocalProvider",
        _CrashingOllama,
    )
    with TestClient(app) as client:
        result = client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": True},
        )
    assert result.status_code == 200
    assert call_count[0] == 1, "Expected exactly one test_connection() call — no retries"
    assert result.json()["status"] == "failed"


def test_ollama_uses_local_test_timeout_config(monkeypatch):
    """TASK-078: provider must be constructed with the local-test timeout config."""
    _enable_ollama_provider()
    monkeypatch.setenv("LLM_LOCAL_TEST_TIMEOUT_SECONDS", "7")
    captured = {}

    class _TimeoutCapturingOllama:
        def __init__(self, **kwargs):
            captured["test_timeout_seconds"] = kwargs.get("test_timeout_seconds")
            captured["timeout_seconds"] = kwargs.get("timeout_seconds")

        def test_connection(self, model=None):
            return LLMResponse(
                text="ok",
                provider="ollama",
                model="qwen3:8b",
                usage=None,
                error=None,
            )

    monkeypatch.setattr(
        "app.services.provider_test_connection_service.OllamaLocalProvider",
        _TimeoutCapturingOllama,
    )
    with TestClient(app) as client:
        client.post(
            "/provider/settings/test",
            json={"provider": "ollama", "explicit_cost_ack": True},
        )
    assert captured["test_timeout_seconds"] == 7
