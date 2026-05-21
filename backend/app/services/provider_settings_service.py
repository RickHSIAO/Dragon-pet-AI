"""
Safe provider settings service.

Non-secret settings remain in memory. TASK-054 key save/clear helpers delegate
to the key storage abstraction and never return, log, or persist keys in SQLite.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from threading import Lock
from typing import Any

from app.services.key_storage_service import (
    KeyStorageUnavailableError,
    clear_api_key,
    get_key_status,
    save_api_key,
)
from app.services.usage_meter_service import get_usage_summary


# TASK-076: added "ollama" to supported providers
SUPPORTED_PROVIDERS = {"mock", "anthropic", "openai", "ollama"}
REAL_PROVIDERS = {"anthropic", "openai"}
# TASK-076: local providers — no API key, no external network
LOCAL_PROVIDERS = {"ollama"}


class ProviderKeyStorageError(RuntimeError):
    """Safe provider key storage failure without secret details."""


@dataclass
class ProviderSettings:
    provider: str = "mock"
    model: str | None = None
    real_provider_enabled: bool = False
    llm_chat_enabled: bool = False
    fallback_to_mock: bool = True
    key_status: str = "not_configured"
    last_test_status: str = "not_tested"


@dataclass
class ProviderSettingsUpdate:
    provider: str | None = None
    model: str | None = None
    real_provider_enabled: bool | None = None
    llm_chat_enabled: bool | None = None
    fallback_to_mock: bool | None = None


class ProviderSettingsService:
    """
    Thread-safe in-memory non-secret settings store.

    The service is deliberately independent from LLM_API_KEY and secure key
    storage. It exposes safe status metadata only.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._settings = ProviderSettings()
        self._runtime_overridden = False

    def get_settings(self) -> dict[str, Any]:
        with self._lock:
            settings = deepcopy(self._settings)
        return self._serialize(settings)

    def update_settings(self, update: ProviderSettingsUpdate) -> dict[str, Any]:
        with self._lock:
            if update.provider is not None:
                provider = update.provider.strip().lower()
                if provider not in SUPPORTED_PROVIDERS:
                    raise ValueError("unsupported provider")
                self._settings.provider = provider

            if update.model is not None:
                model = update.model.strip()
                self._settings.model = model or None

            if update.real_provider_enabled is not None:
                self._settings.real_provider_enabled = update.real_provider_enabled

            if update.llm_chat_enabled is not None:
                self._settings.llm_chat_enabled = update.llm_chat_enabled

            if update.fallback_to_mock is not None:
                self._settings.fallback_to_mock = update.fallback_to_mock

            self._runtime_overridden = True
            settings = deepcopy(self._settings)
        return self._serialize(settings)

    def reset(self) -> None:
        with self._lock:
            self._settings = ProviderSettings()
            self._runtime_overridden = False

    def get_runtime_settings(self) -> dict[str, Any]:
        with self._lock:
            settings = deepcopy(self._settings)
            runtime_overridden = self._runtime_overridden
        data = self._serialize(settings)
        data["runtime_overridden"] = runtime_overridden
        return data

    def _serialize(self, settings: ProviderSettings) -> dict[str, Any]:
        data = asdict(settings)
        data["key_status"] = get_provider_key_status(settings.provider)
        data["resolved_provider"] = _resolve_provider(settings)
        data["usage_summary"] = _safe_usage_summary()
        return data


def _resolve_provider(settings: ProviderSettings) -> str:
    if not settings.llm_chat_enabled:
        return "mock"
    if not settings.real_provider_enabled:
        return "mock"
    if settings.provider == "mock":
        return "mock"
    # TASK-076: local providers resolve to themselves — no key check required
    if settings.provider in LOCAL_PROVIDERS:
        return settings.provider
    if settings.provider not in REAL_PROVIDERS:
        return "mock"
    if get_provider_key_status(settings.provider) != "configured":
        return "mock" if settings.fallback_to_mock else "safe_fallback"
    return settings.provider


def _normalize_key_provider(provider: str) -> str:
    normalized = (provider or "").strip().lower()
    if normalized == "mock":
        raise ValueError("mock provider cannot store an api key")
    # TASK-076: local providers do not use API keys
    if normalized in LOCAL_PROVIDERS:
        raise ValueError("local provider does not require an api key")
    if normalized not in REAL_PROVIDERS:
        raise ValueError("unsupported provider")
    return normalized


def save_provider_api_key(provider: str, api_key: str) -> dict[str, str]:
    normalized_provider = _normalize_key_provider(provider)
    try:
        save_api_key(normalized_provider, api_key)
    except KeyStorageUnavailableError as exc:
        raise ProviderKeyStorageError("secure key storage is unavailable") from exc
    return {
        "provider": normalized_provider,
        "key_status": "configured",
        "message": "API key saved.",
    }


def clear_provider_api_key(provider: str) -> dict[str, str]:
    normalized_provider = _normalize_key_provider(provider)
    try:
        clear_api_key(normalized_provider)
    except KeyStorageUnavailableError as exc:
        raise ProviderKeyStorageError("secure key storage is unavailable") from exc
    return {
        "provider": normalized_provider,
        "key_status": "not_configured",
        "message": "API key cleared.",
    }


def get_provider_key_status(provider: str) -> str:
    normalized = (provider or "").strip().lower()
    if normalized == "mock":
        return "not_configured"
    # TASK-076: local providers never require an API key
    if normalized in LOCAL_PROVIDERS:
        return "not_required"
    if normalized not in REAL_PROVIDERS:
        raise ValueError("unsupported provider")
    return get_key_status(normalized)


def _safe_usage_summary() -> dict[str, Any]:
    summary = get_usage_summary()
    return {
        "request_count": summary.request_count,
        "source_counts": dict(summary.source_counts),
        "provider_counts": dict(summary.provider_counts),
        "model_counts": dict(summary.model_counts),
        "estimated_input_tokens": summary.estimated_input_tokens,
        "estimated_output_tokens": summary.estimated_output_tokens,
        "estimated_total_tokens": summary.estimated_total_tokens,
        "fallback_count": summary.fallback_count,
        "memory_used_count": summary.memory_used_count,
        "error_counts": dict(summary.error_counts),
    }


_service = ProviderSettingsService()


def get_provider_settings() -> dict[str, Any]:
    return _service.get_settings()


def get_runtime_provider_settings() -> dict[str, Any]:
    return _service.get_runtime_settings()


def update_provider_settings(update: ProviderSettingsUpdate) -> dict[str, Any]:
    return _service.update_settings(update)


def reset_provider_settings() -> None:
    _service.reset()
