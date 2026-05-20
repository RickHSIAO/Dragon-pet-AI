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
