"""
Secure API key storage abstraction.

TASK-053 adds the backend-only storage layer. TASK-054 wires provider settings
key save/clear endpoints to it. The production backend is intentionally disabled
unless an explicit secure backend is configured; tests use the in-memory fake.

Safety rules:
- API keys are never logged, printed, stored in SQLite, or returned in schemas.
- Only backend service code can retrieve a key value.
- Plain local files and plain config storage are not implemented.
- External provider APIs are never called from this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Protocol


ALLOWED_PROVIDERS = {"anthropic", "openai"}
KEYRING_SERVICE_NAME = "dragon-pet-ai"


class KeyStorageUnavailableError(RuntimeError):
    """Raised when no secure production key storage backend is available."""


class KeyStorageBackend(Protocol):
    """Backend interface for storing provider API keys."""

    def save_api_key(self, provider: str, api_key: str) -> None:
        """Save or replace a provider key."""

    def get_api_key(self, provider: str) -> str | None:
        """Return a provider key to backend-only callers."""

    def clear_api_key(self, provider: str) -> None:
        """Clear a provider key. This operation must be idempotent."""


def normalize_provider(provider: str) -> str:
    normalized = (provider or "").strip().lower()
    if normalized not in ALLOWED_PROVIDERS:
        raise ValueError("unsupported provider")
    return normalized


def normalize_api_key(api_key: str) -> str:
    normalized = (api_key or "").strip()
    if not normalized:
        raise ValueError("api key is required")
    return normalized


@dataclass(repr=False)
class InMemoryKeyStorageBackend:
    """
    In-memory fake backend for tests only.

    This backend is not persistent and must not be used as secure production
    storage. It is intentionally safe for unit tests because it avoids the OS
    keychain and never writes SQLite or files.
    """

    def __post_init__(self) -> None:
        self._keys: dict[str, str] = {}
        self._lock = Lock()

    def __repr__(self) -> str:
        with self._lock:
            providers = sorted(self._keys)
        return (
            f"InMemoryKeyStorageBackend(providers={providers!r}, "
            "secrets=<redacted>)"
        )

    __str__ = __repr__

    def save_api_key(self, provider: str, api_key: str) -> None:
        normalized_provider = normalize_provider(provider)
        normalized_key = normalize_api_key(api_key)
        with self._lock:
            self._keys[normalized_provider] = normalized_key

    def get_api_key(self, provider: str) -> str | None:
        normalized_provider = normalize_provider(provider)
        with self._lock:
            return self._keys.get(normalized_provider)

    def clear_api_key(self, provider: str) -> None:
        normalized_provider = normalize_provider(provider)
        with self._lock:
            self._keys.pop(normalized_provider, None)


class UnavailableKeyStorageBackend:
    """
    Safe production default until OS keychain/keyring is configured.

    Saving and retrieving keys are disabled. Status checks treat this as
    not_configured so provider settings can remain safe and non-secret.
    """

    def __repr__(self) -> str:
        return "UnavailableKeyStorageBackend(secrets=<redacted>)"

    __str__ = __repr__

    def save_api_key(self, provider: str, api_key: str) -> None:
        normalize_provider(provider)
        normalize_api_key(api_key)
        raise KeyStorageUnavailableError("secure key storage is unavailable")

    def get_api_key(self, provider: str) -> str | None:
        normalize_provider(provider)
        raise KeyStorageUnavailableError("secure key storage is unavailable")

    def clear_api_key(self, provider: str) -> None:
        normalize_provider(provider)
        raise KeyStorageUnavailableError("secure key storage is unavailable")


class KeyringKeyStorageBackend:
    """
    Optional OS keychain backend using the keyring package when available.

    The project does not depend on keyring yet. Instantiating this backend
    raises KeyStorageUnavailableError if the package cannot be imported.
    """

    def __init__(self, service_name: str = KEYRING_SERVICE_NAME) -> None:
        try:
            import keyring  # type: ignore[import-not-found]
        except ImportError as exc:
            raise KeyStorageUnavailableError(
                "keyring package is not installed"
            ) from exc
        self._keyring = keyring
        self._service_name = service_name

    def __repr__(self) -> str:
        return (
            f"KeyringKeyStorageBackend(service_name={self._service_name!r}, "
            "secrets=<redacted>)"
        )

    __str__ = __repr__

    def _account(self, provider: str) -> str:
        return f"llm:{normalize_provider(provider)}"

    def save_api_key(self, provider: str, api_key: str) -> None:
        self._keyring.set_password(
            self._service_name,
            self._account(provider),
            normalize_api_key(api_key),
        )

    def get_api_key(self, provider: str) -> str | None:
        return self._keyring.get_password(self._service_name, self._account(provider))

    def clear_api_key(self, provider: str) -> None:
        account = self._account(provider)
        try:
            self._keyring.delete_password(self._service_name, account)
        except Exception:
            # keyring backends vary when deleting a missing key. Missing-key
            # clear must remain idempotent and must not expose provider details.
            return


_backend: KeyStorageBackend = UnavailableKeyStorageBackend()


def set_key_storage_backend_for_tests(backend: KeyStorageBackend) -> None:
    """
    Replace the module backend for tests.

    Runtime code should not call this. It exists so tests can use the fake
    backend without touching OS keychains.
    """
    global _backend
    _backend = backend


def reset_key_storage_backend_for_tests() -> None:
    """Restore the safe unavailable backend after tests."""
    global _backend
    _backend = UnavailableKeyStorageBackend()


def save_api_key(provider: str, api_key: str) -> None:
    _backend.save_api_key(provider, api_key)


def get_api_key(provider: str) -> str | None:
    try:
        return _backend.get_api_key(provider)
    except KeyStorageUnavailableError:
        return None


def require_api_key(provider: str) -> str:
    """
    Return a backend-only API key or raise a safe typed error.

    This is for backend operations that must distinguish a missing key from
    unavailable secure storage. The key must never be returned through schemas.
    """
    normalized_provider = normalize_provider(provider)
    api_key = _backend.get_api_key(normalized_provider)
    if not api_key:
        raise ValueError("missing_key")
    return api_key


def clear_api_key(provider: str) -> None:
    _backend.clear_api_key(provider)


def get_key_status(provider: str) -> str:
    try:
        return "configured" if _backend.get_api_key(provider) else "not_configured"
    except KeyStorageUnavailableError:
        normalize_provider(provider)
        return "not_configured"
