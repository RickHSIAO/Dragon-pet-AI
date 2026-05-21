import logging

from app.core.config import (
    get_llm_api_key,
    get_llm_fallback_to_mock,
    get_llm_model,
    get_ollama_base_url,
    get_ollama_keep_alive,
    get_ollama_timeout_seconds,
    get_llm_provider_enabled,
    get_llm_provider_name,
    get_llm_timeout_seconds,
)
from app.llm.mock_provider import MockLLMProvider
from app.llm.ollama_provider import OllamaLocalProvider
from app.llm.provider import LLMProvider
from app.llm.real_provider import HTTPRealLLMProvider, SafeFallbackLLMProvider


logger = logging.getLogger(__name__)

# Providers that require an API key.
SUPPORTED_REAL_PROVIDERS = {"openai", "anthropic", "http"}

# Providers that are fully local — no API key required.
SUPPORTED_LOCAL_PROVIDERS = {"ollama"}

# Union used for "is this a known provider at all?" checks.
ALL_KNOWN_PROVIDERS = SUPPORTED_REAL_PROVIDERS | SUPPORTED_LOCAL_PROVIDERS


def _warn(message: str) -> None:
    logger.warning(message)


def get_resolved_llm_provider_info() -> dict[str, object]:
    enabled = get_llm_provider_enabled()
    provider_name = get_llm_provider_name()
    api_key_present = bool(get_llm_api_key())
    fallback_to_mock = get_llm_fallback_to_mock()

    if not enabled:
        return {"provider": "mock", "enabled": False, "reason": "flag_disabled"}
    if provider_name == "mock":
        return {"provider": "mock", "enabled": True, "reason": "provider_mock"}

    # Local providers (e.g. Ollama) — no key required; skip key checks entirely.
    if provider_name in SUPPORTED_LOCAL_PROVIDERS:
        return {
            "provider": provider_name,
            "enabled": True,
            "reason": "real_provider_enabled",
        }

    if provider_name not in SUPPORTED_REAL_PROVIDERS:
        return {
            "provider": "mock",
            "enabled": True,
            "reason": "unknown_provider_fallback",
        }
    if not api_key_present and fallback_to_mock:
        return {
            "provider": "mock",
            "enabled": True,
            "reason": "missing_key_fallback",
        }
    if not api_key_present:
        return {
            "provider": "safe_fallback",
            "enabled": True,
            "reason": "missing_key_fallback",
        }
    return {
        "provider": provider_name,
        "enabled": True,
        "reason": "real_provider_enabled",
    }


def get_llm_provider() -> LLMProvider:
    info = get_resolved_llm_provider_info()
    reason = str(info["reason"])
    provider_name = str(info["provider"])

    if reason == "unknown_provider_fallback":
        _warn("unknown llm provider name; falling back to mock")
        return MockLLMProvider()
    if reason == "missing_key_fallback":
        if get_llm_fallback_to_mock():
            _warn("llm provider api key missing; falling back to mock")
            return MockLLMProvider()
        _warn("llm provider api key missing; using safe fallback provider")
        return SafeFallbackLLMProvider()
    if reason != "real_provider_enabled":
        return MockLLMProvider()

    # Local provider path — Ollama.
    if provider_name == "ollama":
        model = get_llm_model() or "qwen3:8b"
        return OllamaLocalProvider(
            model=model,
            base_url=get_ollama_base_url(),
            keep_alive=get_ollama_keep_alive(),
            timeout_seconds=get_ollama_timeout_seconds(),
        )

    # Cloud / key-based provider path.
    return HTTPRealLLMProvider(
        provider_name=get_llm_provider_name(),
        api_key=get_llm_api_key(),
        model=get_llm_model(),
        timeout_seconds=get_llm_timeout_seconds(),
    )
