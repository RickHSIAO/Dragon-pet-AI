"""
Safe Provider Settings Test Connection service.

TASK-059 implements the backend flow with an injectable provider runner so
automated tests remain mocked-only. The runtime default runner does not call
external providers.

TASK-076: Added local provider (Ollama) test connection path. Local providers
bypass the API key check and call OllamaLocalProvider directly. No external
network call; no API key involved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx

from app.core.config import (
    get_llm_timeout_seconds,
    get_local_test_timeout_seconds,
    get_ollama_base_url,
    get_ollama_keep_alive,
    get_ollama_timeout_seconds,
)
from app.llm.ollama_provider import OllamaLocalProvider
from app.llm.types import LLMRequest, LLMResponse
from app.services.key_storage_service import (
    KeyStorageUnavailableError,
    require_api_key,
)
from app.services.provider_settings_service import (
    LOCAL_PROVIDERS,
    REAL_PROVIDERS,
    get_provider_settings,
)
from app.services.usage_meter_service import (
    UsageRecord,
    estimate_text_tokens,
    record_usage,
)


TEST_SYSTEM_PROMPT = "You are a provider connection test. Reply only with OK."
TEST_USER_MESSAGE = "Reply with OK."
TEST_MAX_TOKENS = 16

SAFE_ERROR_MESSAGES = {
    "missing_key": "No API key is configured for this provider.",
    "storage_unavailable": "Secure key storage is unavailable.",
    "provider_disabled": "Real provider is not enabled.",
    "invalid_provider": "Select a supported real provider before testing.",
    "invalid_model": "Select a model before testing the provider.",
    "provider_auth_error": "Provider authentication failed.",
    "rate_limit": "Provider returned a rate limit response.",
    "provider_timeout": "Provider did not respond in time.",
    "provider_unavailable": "Provider is not reachable right now.",
    "invalid_response": "Provider returned an unexpected response.",
    "provider_error": "Provider test failed.",
    # TASK-076: Ollama-specific safe messages
    # TASK-078: clarified messages — Test Connection now verifies server+model
    # via /api/tags only, so timeout/offline failures point to ``ollama serve``
    # rather than blaming the model load.
    "ollama_unavailable": (
        "Local Ollama server is not reachable. "
        "Make sure 'ollama serve' is running on localhost."
    ),
    "model_not_found": (
        "Local model is not installed. "
        "Run 'ollama pull <model>' to download it first."
    ),
}

# TASK-078: timeout message overrides per provider class.  Cloud providers and
# local providers fail differently and the user-facing hint should reflect that.
_LOCAL_TIMEOUT_MESSAGE = (
    "Local Ollama server did not respond in time. "
    "Make sure 'ollama serve' is running and try again."
)

SAFE_PROVIDER_ERRORS = {
    "provider_auth_error",
    "rate_limit",
    "provider_timeout",
    "provider_unavailable",
    "invalid_response",
    "provider_error",
}

# TASK-076: error categories returned by OllamaLocalProvider
SAFE_LOCAL_PROVIDER_ERRORS = {
    "ollama_unavailable",
    "model_not_found",
    "provider_timeout",
    "invalid_response",
    "provider_error",
}


class ProviderTestConnectionRequestError(ValueError):
    """Safe request/precondition failure."""

    def __init__(self, category: str, status_code: int = 400) -> None:
        super().__init__(category)
        self.category = category
        self.status_code = status_code


class ProviderTestRunner(Protocol):
    """Runner interface for one minimal provider test request."""

    def run(
        self,
        *,
        provider: str,
        api_key: str,
        model: str,
        request: LLMRequest,
        timeout_seconds: int,
        max_tokens: int,
    ) -> LLMResponse:
        ...


@dataclass(repr=False)
class UnavailableProviderTestRunner:
    """
    Safe runtime default.

    This runner never calls external providers. It exists so TASK-059 can wire
    endpoint safety and mocked tests before enabling real live provider tests.
    """

    def __repr__(self) -> str:
        return "UnavailableProviderTestRunner(secrets=<redacted>)"

    __str__ = __repr__

    def run(
        self,
        *,
        provider: str,
        api_key: str,  # noqa: ARG002
        model: str,
        request: LLMRequest,  # noqa: ARG002
        timeout_seconds: int,  # noqa: ARG002
        max_tokens: int,  # noqa: ARG002
    ) -> LLMResponse:
        return LLMResponse(
            text="",
            provider=provider,
            model=model,
            usage=None,
            error="provider_unavailable",
        )


_runner: ProviderTestRunner = UnavailableProviderTestRunner()


def set_provider_test_runner_for_tests(runner: ProviderTestRunner) -> None:
    """Replace the provider test runner for mocked tests."""
    global _runner
    _runner = runner


def reset_provider_test_runner_for_tests() -> None:
    """Restore the safe runtime default runner after tests."""
    global _runner
    _runner = UnavailableProviderTestRunner()


def run_provider_test_connection(
    *,
    provider: str,
    model: str | None,
    explicit_cost_ack: bool,
) -> dict[str, object]:
    if explicit_cost_ack is not True:
        raise ProviderTestConnectionRequestError("cost_ack_required")

    normalized_provider = _normalize_provider(provider)
    settings = get_provider_settings()
    is_local_provider = normalized_provider in LOCAL_PROVIDERS
    if settings.get("real_provider_enabled") is not True:
        # TASK-076: local providers use their own model resolver to avoid invalid_model
        if is_local_provider:
            selected_model = _resolve_model_for_local(model)
        else:
            selected_model = _resolve_model(model, normalized_provider)
        return _failed_response(
            provider=normalized_provider,
            model=selected_model,
            source=_source_for_provider(normalized_provider, is_error=True),
            error_category="provider_disabled",
            usage_estimate=None,
            is_local=is_local_provider,
        )

    # TASK-076: local providers (ollama) — skip key check, call directly
    if is_local_provider:
        selected_model = _resolve_model_for_local(model)
        return _run_local_provider_test(
            provider=normalized_provider,
            model=selected_model,
        )

    # Cloud provider path — requires API key
    selected_model = _resolve_model(model, normalized_provider)

    try:
        api_key = require_api_key(normalized_provider)
    except KeyStorageUnavailableError:
        return _failed_response(
            provider=normalized_provider,
            model=selected_model,
            source=_source_for_provider(normalized_provider, is_error=True),
            error_category="storage_unavailable",
            usage_estimate=None,
        )
    except ValueError as exc:
        if str(exc) == "missing_key":
            return _failed_response(
                provider=normalized_provider,
                model=selected_model,
                source=_source_for_provider(normalized_provider, is_error=True),
                error_category="missing_key",
                usage_estimate=None,
            )
        raise ProviderTestConnectionRequestError("invalid_provider") from exc

    request = LLMRequest(
        system_prompt=TEST_SYSTEM_PROMPT,
        user_message=TEST_USER_MESSAGE,
        mode="provider_test",
        memory_context=None,
        state_context=None,
        conversation_history=None,
    )

    try:
        llm_response = _runner.run(
            provider=normalized_provider,
            api_key=api_key,
            model=selected_model,
            request=request,
            timeout_seconds=get_llm_timeout_seconds(),
            max_tokens=TEST_MAX_TOKENS,
        )
    except (TimeoutError, httpx.TimeoutException):
        return _record_and_fail(
            provider=normalized_provider,
            model=selected_model,
            error_category="provider_timeout",
        )
    except Exception:
        return _record_and_fail(
            provider=normalized_provider,
            model=selected_model,
            error_category="provider_unavailable",
        )

    if llm_response.error:
        return _record_and_fail(
            provider=normalized_provider,
            model=selected_model,
            error_category=_safe_error_category(llm_response.error),
        )

    if not llm_response.text.strip():
        return _record_and_fail(
            provider=normalized_provider,
            model=selected_model,
            error_category="invalid_response",
        )

    usage_estimate = _usage_estimate(llm_response, is_success=True)
    _record_usage(
        provider=normalized_provider,
        model=llm_response.model or selected_model,
        source="llm_real",
        usage_estimate=usage_estimate,
        error_category=None,
    )
    return {
        "status": "success",
        "provider": normalized_provider,
        "model": llm_response.model or selected_model,
        "source": "llm_real",
        "safe_message": "Provider test connection succeeded.",
        "error_category": None,
        "usage_estimate": usage_estimate,
    }


# ---------------------------------------------------------------------------
# TASK-076: Local provider (Ollama) test connection
# ---------------------------------------------------------------------------

def _run_local_provider_test(
    *,
    provider: str,
    model: str,
) -> dict[str, object]:
    """
    Run a minimal test against the local Ollama provider.

    TASK-078: Test Connection uses a two-layer fast check that does NOT load
    the model:

    1. ``GET /api/tags`` confirms the Ollama server is alive on localhost.
    2. The returned ``models`` list confirms the requested model is installed.

    A successful Test Connection means "the local runtime is reachable and the
    selected model is available."  Generation behaviour and persona are
    validated separately by ``/chat`` smoke tests, not here.

    Safety invariants:
    - No API key involved.
    - No external network call — Ollama is localhost only.
    - Exactly one HTTP call — no retries.
    - Raw Ollama response body is never forwarded to the caller.
    - The model is NOT loaded into memory by this call; there is no cold-start
      generation latency, so the short local-test timeout is appropriate.
    """
    local_provider = OllamaLocalProvider(
        model=model,
        base_url=get_ollama_base_url(),
        keep_alive=get_ollama_keep_alive(),
        timeout_seconds=get_ollama_timeout_seconds(),
        test_timeout_seconds=get_local_test_timeout_seconds(),
    )

    try:
        llm_response = local_provider.test_connection(model=model)
    except Exception:
        return _local_record_and_fail(
            provider=provider,
            model=model,
            error_category="provider_error",
        )

    if llm_response.error:
        return _local_record_and_fail(
            provider=provider,
            model=llm_response.model or model,
            error_category=_safe_local_error_category(llm_response.error),
        )

    if not llm_response.text.strip():
        return _local_record_and_fail(
            provider=provider,
            model=llm_response.model or model,
            error_category="invalid_response",
        )

    usage_estimate = _usage_estimate(llm_response, is_success=True)
    _record_usage(
        provider=provider,
        model=llm_response.model or model,
        source="llm_local",
        usage_estimate=usage_estimate,
        error_category=None,
    )
    return {
        "status": "success",
        "provider": provider,
        "model": llm_response.model or model,
        "source": "llm_local",
        "safe_message": "Local Ollama connection successful.",
        "error_category": None,
        "usage_estimate": usage_estimate,
    }


def _local_record_and_fail(
    *,
    provider: str,
    model: str,
    error_category: str,
) -> dict[str, object]:
    usage_estimate = _usage_estimate(None, is_success=False)
    _record_usage(
        provider=provider,
        model=model,
        source="llm_local_error",
        usage_estimate=usage_estimate,
        error_category=error_category,
    )
    return _failed_response(
        provider=provider,
        model=model,
        source="llm_local_error",
        error_category=error_category,
        usage_estimate=usage_estimate,
        is_local=True,
    )


def _safe_local_error_category(error: str) -> str:
    return error if error in SAFE_LOCAL_PROVIDER_ERRORS else "provider_error"


def _resolve_model_for_local(model: str | None) -> str:
    """Resolve model for local providers; fall back to Ollama default."""
    if model is not None and model.strip():
        return model.strip()
    settings_model = get_provider_settings().get("model")
    if isinstance(settings_model, str) and settings_model.strip():
        return settings_model.strip()
    # Ollama default — avoids invalid_model error for local providers
    return "qwen3:8b"


def _source_for_provider(provider: str, *, is_error: bool) -> str:
    """Return the safe source string for usage records and responses."""
    if provider in LOCAL_PROVIDERS:
        return "llm_local_error" if is_error else "llm_local"
    return "llm_real_error" if is_error else "llm_real"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _normalize_provider(provider: str) -> str:
    normalized = (provider or "").strip().lower()
    if normalized == "mock":
        raise ProviderTestConnectionRequestError("invalid_provider")
    # TASK-076: allow local providers (ollama) in addition to cloud providers
    if normalized not in REAL_PROVIDERS and normalized not in LOCAL_PROVIDERS:
        raise ProviderTestConnectionRequestError("invalid_provider")
    return normalized


def _resolve_model(model: str | None, provider: str) -> str:  # noqa: ARG001
    if model is not None and model.strip():
        return model.strip()
    settings_model = get_provider_settings().get("model")
    if isinstance(settings_model, str) and settings_model.strip():
        return settings_model.strip()
    raise ProviderTestConnectionRequestError("invalid_model")


def _record_and_fail(
    *,
    provider: str,
    model: str,
    error_category: str,
) -> dict[str, object]:
    usage_estimate = _usage_estimate(None, is_success=False)
    _record_usage(
        provider=provider,
        model=model,
        source="llm_real_error",
        usage_estimate=usage_estimate,
        error_category=error_category,
    )
    return _failed_response(
        provider=provider,
        model=model,
        source="llm_real_error",
        error_category=error_category,
        usage_estimate=usage_estimate,
    )


def _failed_response(
    *,
    provider: str,
    model: str,
    source: str,
    error_category: str,
    usage_estimate: dict[str, int] | None,
    is_local: bool = False,
) -> dict[str, object]:
    # TASK-078: provider_timeout has a distinct local-runtime message so users
    # are pointed at ``ollama serve`` rather than at a paid provider outage.
    if is_local and error_category == "provider_timeout":
        safe_message = _LOCAL_TIMEOUT_MESSAGE
    else:
        safe_message = SAFE_ERROR_MESSAGES.get(error_category, "Provider test failed.")
    return {
        "status": "failed",
        "provider": provider,
        "model": model,
        "source": source,
        "safe_message": safe_message,
        "error_category": error_category,
        "usage_estimate": usage_estimate,
    }


def _safe_error_category(error: str) -> str:
    return error if error in SAFE_PROVIDER_ERRORS else "provider_error"


# ---------------------------------------------------------------------------
# TASK-197: Lightweight Ollama server liveness check (startup warmup probe)
# ---------------------------------------------------------------------------

def check_ollama_server_liveness() -> bool:
    """
    Return True if the local Ollama server responds to GET /api/tags.

    This is a narrow liveness probe used by the /provider/health endpoint on
    Full App startup.  It does NOT load a model, does NOT call /api/chat, and
    does NOT write any data.  Uses a 5-second timeout (hardcoded in
    OllamaLocalProvider._ollama_server_reachable).
    """
    local_provider = OllamaLocalProvider(
        model="",
        base_url=get_ollama_base_url(),
        keep_alive=get_ollama_keep_alive(),
        timeout_seconds=get_ollama_timeout_seconds(),
        test_timeout_seconds=get_local_test_timeout_seconds(),
    )
    return local_provider._ollama_server_reachable()


def _usage_estimate(
    response: LLMResponse | None,
    *,
    is_success: bool,
) -> dict[str, int]:
    usage = response.usage if response else None
    input_tokens = _usage_int(usage, "input_tokens")
    output_tokens = _usage_int(usage, "output_tokens") if is_success else None
    if input_tokens is None:
        input_tokens = estimate_text_tokens(TEST_USER_MESSAGE)
    if output_tokens is None:
        output_tokens = estimate_text_tokens(response.text) if response and is_success else 0
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
    }


def _usage_int(usage: dict[str, object] | None, key: str) -> int | None:
    if not usage:
        return None
    value = usage.get(key)
    if isinstance(value, int) and value >= 0:
        return value
    return None


def _record_usage(
    *,
    provider: str,
    model: str,
    source: str,
    usage_estimate: dict[str, int],
    error_category: str | None,
) -> None:
    record_usage(UsageRecord(
        source=source,
        provider=provider,
        model=model,
        estimated_input_tokens=usage_estimate["input_tokens"],
        estimated_output_tokens=usage_estimate["output_tokens"],
        fallback_used=False,
        memory_used=False,
        error_category=error_category,
    ))
