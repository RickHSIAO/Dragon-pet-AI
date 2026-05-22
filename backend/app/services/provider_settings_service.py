"""
Safe provider settings service.

Non-secret settings remain in memory and are persisted to a JSON file
(TASK-099). TASK-054 key save/clear helpers delegate to the key storage
abstraction and never return, log, or persist keys in SQLite or the
settings file.

Persistence:
- Path: controlled by get_settings_file_path() / SETTINGS_FILE_PATH env var.
- On startup: service reads the JSON file and seeds in-memory state.
- On update (PATCH /provider/settings): service writes non-secret fields only.
- On error: file I/O errors are logged and never propagate to callers.
- Never written: key_status, resolved_provider, usage_summary, api_key.
"""

from __future__ import annotations

import json
import logging
import os
from copy import deepcopy
from dataclasses import asdict, dataclass
from threading import Lock
from typing import Any

from app.core.config import get_settings_file_path
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

# TASK-099: only these fields are written to the settings file.
# Never persist key_status, resolved_provider, usage_summary, or any secret.
_PERSIST_FIELDS = frozenset(
    {"provider", "model", "real_provider_enabled", "llm_chat_enabled", "fallback_to_mock"}
)


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


# ---------------------------------------------------------------------------
# File-based persistence helpers (TASK-099)
# ---------------------------------------------------------------------------

def _load_settings_from_file(path: str) -> dict[str, Any] | None:
    """
    Load non-secret settings from the JSON file.

    Returns a dict with only _PERSIST_FIELDS keys, or None on any error.
    Missing file is treated as a normal first-run condition (returns None).
    Corrupt or unreadable files emit a warning and return None.
    """
    if not path:
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            logging.warning(
                "provider_settings_persistence: settings file is not a JSON object; "
                "using defaults"
            )
            return None
        # Strip any keys not in the safe whitelist before returning
        return {k: v for k, v in data.items() if k in _PERSIST_FIELDS}
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        logging.warning(
            "provider_settings_persistence: could not load settings file %r: %s; "
            "using defaults",
            path,
            exc,
        )
        return None


def _save_settings_to_file(path: str, settings: ProviderSettings) -> None:
    """
    Write non-secret settings to the JSON file.

    Errors are logged but never raised. The caller continues normally even
    if the write fails (e.g. read-only filesystem, missing parent directory).

    Safety: only fields in _PERSIST_FIELDS are written. key_status,
    resolved_provider, usage_summary, and any secret are never included.
    """
    if not path:
        return
    data = {k: v for k, v in asdict(settings).items() if k in _PERSIST_FIELDS}
    try:
        parent = os.path.dirname(os.path.abspath(path))
        os.makedirs(parent, exist_ok=True)
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except OSError as exc:
        logging.warning(
            "provider_settings_persistence: could not save settings to %r: %s",
            path,
            exc,
        )


class ProviderSettingsService:
    """
    Thread-safe non-secret settings store with optional JSON persistence.

    The service is deliberately independent from LLM_API_KEY and secure key
    storage. It exposes safe status metadata only.

    On startup the service loads persisted settings from the JSON file
    (if it exists and is valid). Any subsequent PATCH call re-writes the file.
    The API key is never part of the persisted data.
    """

    def __init__(self, settings_file_path: str | None = None) -> None:
        self._lock = Lock()
        self._settings = ProviderSettings()
        self._runtime_overridden = False
        # Allow override for tests; fall back to env-var-configured path.
        self._settings_file_path: str = (
            settings_file_path
            if settings_file_path is not None
            else get_settings_file_path()
        )
        self._try_load_from_file()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

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

        # Persist outside the lock so file I/O does not block readers.
        _save_settings_to_file(self._settings_file_path, settings)
        return self._serialize(settings)

    def reset(self) -> None:
        """Reset in-memory state to defaults. Does NOT delete the settings file."""
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

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _try_load_from_file(self) -> None:
        """
        Seed in-memory state from the persisted settings file on startup.

        If the file is absent, corrupt, or contains invalid values, the service
        silently starts with safe defaults. Loaded settings mark
        ``_runtime_overridden = True`` so the chat service uses them instead of
        falling back to env vars.
        """
        loaded = _load_settings_from_file(self._settings_file_path)
        if loaded is None:
            return
        try:
            with self._lock:
                if "provider" in loaded:
                    p = str(loaded["provider"]).strip().lower()
                    if p in SUPPORTED_PROVIDERS:
                        self._settings.provider = p
                    # unknown provider → keep default "mock"
                if "model" in loaded:
                    raw_model = loaded["model"]
                    self._settings.model = (
                        str(raw_model).strip() or None
                        if raw_model is not None
                        else None
                    )
                if "real_provider_enabled" in loaded:
                    self._settings.real_provider_enabled = bool(
                        loaded["real_provider_enabled"]
                    )
                if "llm_chat_enabled" in loaded:
                    self._settings.llm_chat_enabled = bool(loaded["llm_chat_enabled"])
                if "fallback_to_mock" in loaded:
                    self._settings.fallback_to_mock = bool(loaded["fallback_to_mock"])
                self._runtime_overridden = True
            logging.info(
                "provider_settings_persistence: loaded settings from %r",
                self._settings_file_path,
            )
        except (TypeError, ValueError, KeyError) as exc:
            logging.warning(
                "provider_settings_persistence: ignoring invalid settings file: %s; "
                "using defaults",
                exc,
            )
            with self._lock:
                self._settings = ProviderSettings()
                self._runtime_overridden = False

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
