"""
dragon-pet-ai — runtime configuration helpers.

Reads feature flags from environment variables.
No heavy config framework — plain os.environ reads only.

Safety:
- These helpers do not execute shell commands.
- They do not read user files.
- They only inspect environment variables.
"""

import os


def read_str_env(name: str, default: str = "") -> str:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    return raw_value.strip()


def read_int_env(name: str, default: int, min_value: int, max_value: int) -> int:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value.strip())
    except (TypeError, ValueError):
        return default
    return max(min_value, min(max_value, value))


def read_bool_env(name: str, default: bool = False) -> bool:
    """
    Read a boolean value from an environment variable.

    Accepted true  values (case-insensitive): "1", "true", "yes", "on"
    Accepted false values (case-insensitive): "0", "false", "no", "off"
    Missing or unknown values fall back to ``default`` (which itself defaults
    to False, so the system fails closed for safety-relevant flags).
    """
    raw_value = os.environ.get(name)
    if raw_value is None:
        # Genuinely absent → use the caller-supplied default.
        return default
    raw = raw_value.strip().lower()
    if raw in ("1", "true", "yes", "on"):
        return True
    if raw in ("0", "false", "no", "off"):
        return False
    # Whitespace-only or unknown value → fail closed to False regardless of
    # default, because we never want an unrecognised value to enable a safety
    # boundary.
    return False


def is_memory_injection_enabled() -> bool:
    """
    Return True only when MEMORY_INJECTION_ENABLED is explicitly set to a
    recognised truthy value.

    Default is False — /chat does NOT build memory context unless the flag is
    explicitly enabled. This preserves the safety boundary described in
    docs/MEMORY_SYSTEM.md and the TASK-017 Opus review outcome.
    """
    return read_bool_env("MEMORY_INJECTION_ENABLED", default=False)


def get_llm_provider_enabled() -> bool:
    return read_bool_env("LLM_PROVIDER_ENABLED", default=False)


def get_llm_chat_enabled() -> bool:
    return read_bool_env("LLM_CHAT_ENABLED", default=False)


def get_llm_provider_name() -> str:
    return read_str_env("LLM_PROVIDER_NAME", default="mock").lower() or "mock"


def get_llm_api_key() -> str:
    return read_str_env("LLM_API_KEY", default="")


def get_llm_model() -> str:
    return read_str_env("LLM_MODEL", default="")


def get_llm_timeout_seconds() -> int:
    return read_int_env(
        "LLM_TIMEOUT_SECONDS",
        default=30,
        min_value=1,
        max_value=120,
    )


def get_llm_fallback_to_mock() -> bool:
    return read_bool_env("LLM_FALLBACK_TO_MOCK", default=True)


# ---------------------------------------------------------------------------
# Ollama local provider config
# ---------------------------------------------------------------------------

_OLLAMA_ALLOWED_PREFIXES = ("http://localhost", "http://127.0.0.1")


def get_ollama_base_url() -> str:
    """
    Return the Ollama server base URL.

    Default: ``http://localhost:11434``.

    Safety: Only localhost / 127.0.0.1 URLs are accepted.  If the env var
    contains any other host, the safe default is returned instead.  This
    prevents the renderer (or a misconfigured env) from routing Ollama traffic
    to an external server.
    """
    url = read_str_env("OLLAMA_BASE_URL", default="http://localhost:11434").rstrip("/")
    if not any(url.startswith(prefix) for prefix in _OLLAMA_ALLOWED_PREFIXES):
        return "http://localhost:11434"
    return url


def get_ollama_keep_alive() -> str:
    """Return the Ollama keep-alive duration string (e.g. ``10m``).

    Default: ``10m`` — keeps the model loaded in memory for 10 minutes after
    the last request, avoiding cold-start latency on repeated calls.
    """
    return read_str_env("OLLAMA_KEEP_ALIVE", default="10m")


def get_local_chat_timeout_seconds() -> int:
    """Return the local-provider chat/generation timeout in seconds.

    Default: 90. Clamped to [1, 300]. Local models can be slow on first load
    (model not yet warmed). Override with ``LLM_LOCAL_CHAT_TIMEOUT_SECONDS``.

    Backward compatibility: if the new local-chat variable is absent but the
    older ``OLLAMA_TIMEOUT_SECONDS`` is set, use the older value.
    """
    if os.environ.get("LLM_LOCAL_CHAT_TIMEOUT_SECONDS") is not None:
        return read_int_env(
            "LLM_LOCAL_CHAT_TIMEOUT_SECONDS",
            default=90,
            min_value=1,
            max_value=300,
        )
    return read_int_env(
        "OLLAMA_TIMEOUT_SECONDS",
        default=90,
        min_value=1,
        max_value=300,
    )


def get_ollama_timeout_seconds() -> int:
    """Return the Ollama chat timeout.

    Kept as a compatibility alias for older call sites and docs.
    """
    return get_local_chat_timeout_seconds()


def get_local_test_timeout_seconds() -> int:
    """Return the local provider Test Connection HTTP timeout in seconds.

    Default: 10. Clamped to [1, 60]. This timeout is intentionally separate
    from ``OLLAMA_TIMEOUT_SECONDS`` because Test Connection uses ``/api/tags``,
    which does not load any model and returns quickly.  Generation cold-start
    latency does not apply to this path, so a short timeout is appropriate.

    Override with ``LLM_LOCAL_TEST_TIMEOUT_SECONDS`` if the local runtime needs
    longer (for example a slow disk or container restart).
    """
    return read_int_env(
        "LLM_LOCAL_TEST_TIMEOUT_SECONDS",
        default=10,
        min_value=1,
        max_value=60,
    )


# ---------------------------------------------------------------------------
# Non-secret settings persistence (TASK-099)
# ---------------------------------------------------------------------------

def get_settings_file_path() -> str:
    """
    Return the path for the non-secret provider settings JSON file.

    Default: ``data/provider_settings.json`` relative to the backend working
    directory (i.e. ``backend/data/provider_settings.json``).

    Override with ``SETTINGS_FILE_PATH`` for testing or alternative layouts:
    - Set to empty string to disable persistence (in-memory only).
    - Set to ``/tmp/dragon-pet-ai-settings.json`` to isolate test runs.

    Safety: This file stores ONLY non-secret fields (provider, model, booleans).
    API keys are never written to this file.
    """
    return read_str_env("SETTINGS_FILE_PATH", default="data/provider_settings.json")
