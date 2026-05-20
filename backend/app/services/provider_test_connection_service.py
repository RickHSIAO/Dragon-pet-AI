"""
Safe Provider Settings Test Connection service.

TASK-059 implements the backend flow with an injectable provider runner so
automated tests remain mocked-only. The runtime default runner does not call
external providers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx

from app.core.config import get_llm_timeout_seconds
from app.llm.types import LLMRequest, LLMResponse
from app.services.key_storage_service import (
    KeyStorageUnavailableError,
    require_api_key,
)
from app.services.provider_settings_service import (
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
}

SAFE_PROVIDER_ERRORS = {
    "provider_auth_error",
    "rate_limit",
    "provider_timeout",
    "provider_unavailable",
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
    selected_model = _resolve_model(model)
    settings = get_provider_settings()
    if settings.get("real_provider_enabled") is not True:
        return _failed_response(
            provider=normalized_provider,
            model=selected_model,
            error_category="provider_disabled",
            usage_estimate=None,
        )

    try:
        api_key = require_api_key(normalized_provider)
    except KeyStorageUnavailableError:
        return _failed_response(
            provider=normalized_provider,
            model=selected_model,
            error_category="storage_unavailable",
            usage_estimate=None,
        )
    except ValueError as exc:
        if str(exc) == "missing_key":
            return _failed_response(
                provider=normalized_provider,
                model=selected_model,
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


def _normalize_provider(provider: str) -> str:
    normalized = (provider or "").strip().lower()
    if normalized == "mock" or normalized not in REAL_PROVIDERS:
        raise ProviderTestConnectionRequestError("invalid_provider")
    return normalized


def _resolve_model(model: str | None) -> str:
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
        error_category=error_category,
        usage_estimate=usage_estimate,
    )


def _failed_response(
    *,
    provider: str,
    model: str,
    error_category: str,
    usage_estimate: dict[str, int] | None,
) -> dict[str, object]:
    return {
        "status": "failed",
        "provider": provider,
        "model": model,
        "source": "llm_real_error",
        "safe_message": SAFE_ERROR_MESSAGES.get(error_category, "Provider test failed."),
        "error_category": error_category,
        "usage_estimate": usage_estimate,
    }


def _safe_error_category(error: str) -> str:
    return error if error in SAFE_PROVIDER_ERRORS else "provider_error"


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

