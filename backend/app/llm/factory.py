import logging
from typing import Any

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

SUPPORTED_REAL_PROVIDERS = {"openai", "anthropic", "http"}
SUPPORTED_LOCAL_PROVIDERS = {"ollama"}
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

    if provider_name in SUPPORTED_LOCAL_PROVIDERS:
        return {"provider": provider_name, "enabled": True, "reason": "real_provider_enabled"}

    if provider_name not in SUPPORTED_REAL_PROVIDERS:
        return {"provider": "mock", "enabled": True, "reason": "unknown_provider_fallback"}
    if not api_key_present and fallback_to_mock:
        return {"provider": "mock", "enabled": True, "reason": "missing_key_fallback"}
    if not api_key_present:
        return {"provider": "safe_fallback", "enabled": True, "reason": "missing_key_fallback"}
    return {"provider": provider_name, "enabled": True, "reason": "real_provider_enabled"}


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

    if provider_name == "ollama":
        model = get_llm_model() or "qwen3:8b"
        return OllamaLocalProvider(
            model=model,
            base_url=get_ollama_base_url(),
            keep_alive=get_ollama_keep_alive(),
            timeout_seconds=get_ollama_timeout_seconds(),
        )

    return HTTPRealLLMProvider(
        provider_name=get_llm_provider_name(),
        api_key=get_llm_api_key(),
        model=get_llm_model(),
        timeout_seconds=get_llm_timeout_seconds(),
    )


def get_llm_provider_from_runtime_settings(settings: dict[str, Any]) -> LLMProvider:
    """
    Build a provider from runtime Provider Settings.

    This is used after the user has PATCHed /provider/settings. It deliberately
    follows the already-resolved safe provider value from that service instead
    of re-reading LLM_PROVIDER_NAME from the environment.
    """
    provider_name = str(settings.get("resolved_provider") or "mock").strip().lower()
    model = str(settings.get("model") or get_llm_model() or "").strip()

    if provider_name == "mock":
        return MockLLMProvider()
    if provider_name == "safe_fallback":
        return SafeFallbackLLMProvider()

    if provider_name == "ollama":
        return OllamaLocalProvider(
            model=model or "qwen3:8b",
            base_url=get_ollama_base_url(),
            keep_alive=get_ollama_keep_alive(),
            timeout_seconds=get_ollama_timeout_seconds(),
        )

    if provider_name in SUPPORTED_REAL_PROVIDERS:
        return HTTPRealLLMProvider(
            provider_name=provider_name,
            api_key=get_llm_api_key(),
            model=model,
            timeout_seconds=get_llm_timeout_seconds(),
        )

    _warn("unknown runtime llm provider; falling back to mock")
    return MockLLMProvider()
