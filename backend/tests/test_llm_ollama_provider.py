"""
Tests for OllamaLocalProvider and Ollama factory integration.

All tests use mocked HTTP — no live Ollama server required.
No real network calls, no real API keys, no prompt text in logs.

Coverage:
 1. Successful response maps correctly to LLMResponse
 2. eval_count / prompt_eval_count land in usage dict
 3. Missing eval counts produce usage=None
 4. Connection refused → ollama_unavailable
 5. Generic ConnectError → ollama_unavailable
 6. Timeout → provider_timeout
 7. 404 → model_not_found
 8. Non-2xx (500) → provider_error
 9. Malformed JSON (no message key) → invalid_response
10. message.content empty string → invalid_response
11. message is not a dict → invalid_response
12. Response is not a dict → invalid_response
13. Factory: LLM_PROVIDER_NAME=ollama + LLM_PROVIDER_ENABLED=true → OllamaLocalProvider
14. Factory: unknown provider name → MockLLMProvider (unknown_provider_fallback)
15. get_resolved_llm_provider_info: ollama → real_provider_enabled, no key check
16. Factory: LLM_PROVIDER_ENABLED=false → MockLLMProvider regardless of provider name
17. OllamaLocalProvider.__repr__ contains no secrets
18. OllamaLocalProvider provider_name == 'ollama'
19. Request payload structure: stream=False, think=False, messages in correct order
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest

from app.llm.ollama_provider import (
    DEFAULT_OLLAMA_MODEL,
    OllamaLocalProvider,
)
from app.llm.real_provider import (
    CANONICAL_SAFE_FALLBACK_TEXT,
    ProviderHTTPResponse,
)
from app.llm.types import LLMRequest, LLMResponse


# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = "You are a test assistant."
USER_MESSAGE = "Hello, test."

SAMPLE_REQUEST = LLMRequest(
    system_prompt=SYSTEM_PROMPT,
    user_message=USER_MESSAGE,
)


def make_ollama_response(
    content: str = "OK.",
    model: str = "qwen3:8b",
    eval_count: int | None = 3,
    prompt_eval_count: int | None = 42,
) -> dict[str, Any]:
    """Build a minimal valid Ollama API response body."""
    resp: dict[str, Any] = {
        "model": model,
        "message": {"role": "assistant", "content": content},
        "done": True,
    }
    if eval_count is not None:
        resp["eval_count"] = eval_count
    if prompt_eval_count is not None:
        resp["prompt_eval_count"] = prompt_eval_count
    return resp


class FakeHTTPClient:
    """Injectable HTTP client that returns a pre-configured ProviderHTTPResponse."""

    def __init__(self, response: ProviderHTTPResponse) -> None:
        self._response = response
        self.last_payload: dict[str, Any] | None = None
        self.last_url: str | None = None

    def request_json(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
        timeout_seconds: int,
    ) -> ProviderHTTPResponse:
        self.last_url = url
        self.last_payload = payload
        return self._response


class RaisingHTTPClient:
    """Injectable HTTP client that raises a given exception."""

    def __init__(self, exc: Exception) -> None:
        self._exc = exc

    def request_json(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
        timeout_seconds: int,
    ) -> ProviderHTTPResponse:
        raise self._exc


def make_provider(
    http_client: Any = None,
    model: str = "qwen3:8b",
    base_url: str = "http://localhost:11434",
) -> OllamaLocalProvider:
    return OllamaLocalProvider(
        model=model,
        base_url=base_url,
        keep_alive="10m",
        timeout_seconds=30,
        http_client=http_client,
    )


# ---------------------------------------------------------------------------
# Test 1 — Successful response maps correctly to LLMResponse
# ---------------------------------------------------------------------------

def test_successful_response_maps_to_llm_response() -> None:
    body = make_ollama_response(content="Hello from Ollama!", model="qwen3:8b")
    client = FakeHTTPClient(ProviderHTTPResponse(status_code=200, json_data=body))
    provider = make_provider(http_client=client)

    result = provider.generate(SAMPLE_REQUEST)

    assert result.text == "Hello from Ollama!"
    assert result.provider == "ollama"
    assert result.model == "qwen3:8b"
    assert result.error is None


# ---------------------------------------------------------------------------
# Test 2 — eval_count / prompt_eval_count land in usage dict
# ---------------------------------------------------------------------------

def test_token_counts_land_in_usage() -> None:
    body = make_ollama_response(eval_count=7, prompt_eval_count=55)
    client = FakeHTTPClient(ProviderHTTPResponse(status_code=200, json_data=body))
    provider = make_provider(http_client=client)

    result = provider.generate(SAMPLE_REQUEST)

    assert result.usage is not None
    assert result.usage["output_tokens_actual"] == 7
    assert result.usage["input_tokens_actual"] == 55


# ---------------------------------------------------------------------------
# Test 3 — Missing eval counts → usage is None
# ---------------------------------------------------------------------------

def test_missing_eval_counts_produces_no_usage() -> None:
    body = make_ollama_response(eval_count=None, prompt_eval_count=None)
    client = FakeHTTPClient(ProviderHTTPResponse(status_code=200, json_data=body))
    provider = make_provider(http_client=client)

    result = provider.generate(SAMPLE_REQUEST)

    assert result.usage is None
    assert result.error is None


# ---------------------------------------------------------------------------
# Test 4 — Connection refused → ollama_unavailable
# ---------------------------------------------------------------------------

def test_connection_refused_returns_ollama_unavailable() -> None:
    exc = ConnectionRefusedError("Connection refused")
    client = RaisingHTTPClient(exc)
    provider = make_provider(http_client=client)

    result = provider.generate(SAMPLE_REQUEST)

    assert result.error == "ollama_unavailable"
    assert result.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert result.provider == "ollama"


# ---------------------------------------------------------------------------
# Test 5 — Generic ConnectError → ollama_unavailable
# ---------------------------------------------------------------------------

def test_httpx_connect_error_returns_ollama_unavailable() -> None:
    exc = httpx.ConnectError("connection failed")
    client = RaisingHTTPClient(exc)
    provider = make_provider(http_client=client)

    result = provider.generate(SAMPLE_REQUEST)

    assert result.error == "ollama_unavailable"
    assert result.text == CANONICAL_SAFE_FALLBACK_TEXT


# ---------------------------------------------------------------------------
# Test 6 — Timeout → provider_timeout
# ---------------------------------------------------------------------------

def test_timeout_returns_provider_timeout() -> None:
    exc = httpx.TimeoutException("timed out")
    client = RaisingHTTPClient(exc)
    provider = make_provider(http_client=client)

    result = provider.generate(SAMPLE_REQUEST)

    assert result.error == "provider_timeout"
    assert result.text == CANONICAL_SAFE_FALLBACK_TEXT


# ---------------------------------------------------------------------------
# Test 7 — HTTP 404 → model_not_found
# ---------------------------------------------------------------------------

def test_http_404_returns_model_not_found() -> None:
    client = FakeHTTPClient(ProviderHTTPResponse(status_code=404, json_data=None))
    provider = make_provider(http_client=client)

    result = provider.generate(SAMPLE_REQUEST)

    assert result.error == "model_not_found"
    assert result.text == CANONICAL_SAFE_FALLBACK_TEXT


# ---------------------------------------------------------------------------
# Test 8 — HTTP 500 → provider_error
# ---------------------------------------------------------------------------

def test_http_500_returns_provider_error() -> None:
    client = FakeHTTPClient(ProviderHTTPResponse(status_code=500, json_data=None))
    provider = make_provider(http_client=client)

    result = provider.generate(SAMPLE_REQUEST)

    assert result.error == "provider_error"
    assert result.text == CANONICAL_SAFE_FALLBACK_TEXT


# ---------------------------------------------------------------------------
# Test 9 — Missing "message" key → invalid_response
# ---------------------------------------------------------------------------

def test_missing_message_key_returns_invalid_response() -> None:
    bad_body: dict[str, Any] = {"model": "qwen3:8b", "done": True}  # no "message"
    client = FakeHTTPClient(ProviderHTTPResponse(status_code=200, json_data=bad_body))
    provider = make_provider(http_client=client)

    result = provider.generate(SAMPLE_REQUEST)

    assert result.error == "invalid_response"
    assert result.text == CANONICAL_SAFE_FALLBACK_TEXT


# ---------------------------------------------------------------------------
# Test 10 — Empty content string → invalid_response
# ---------------------------------------------------------------------------

def test_empty_content_returns_invalid_response() -> None:
    body = make_ollama_response(content="")
    client = FakeHTTPClient(ProviderHTTPResponse(status_code=200, json_data=body))
    provider = make_provider(http_client=client)

    result = provider.generate(SAMPLE_REQUEST)

    assert result.error == "invalid_response"
    assert result.text == CANONICAL_SAFE_FALLBACK_TEXT


# ---------------------------------------------------------------------------
# Test 11 — message is not a dict → invalid_response
# ---------------------------------------------------------------------------

def test_message_not_dict_returns_invalid_response() -> None:
    bad_body: dict[str, Any] = {"model": "qwen3:8b", "message": "not-a-dict", "done": True}
    client = FakeHTTPClient(ProviderHTTPResponse(status_code=200, json_data=bad_body))
    provider = make_provider(http_client=client)

    result = provider.generate(SAMPLE_REQUEST)

    assert result.error == "invalid_response"


# ---------------------------------------------------------------------------
# Test 12 — Response body is not a dict → invalid_response
# ---------------------------------------------------------------------------

def test_response_not_dict_returns_invalid_response() -> None:
    client = FakeHTTPClient(ProviderHTTPResponse(status_code=200, json_data=["not", "a", "dict"]))
    provider = make_provider(http_client=client)

    result = provider.generate(SAMPLE_REQUEST)

    assert result.error == "invalid_response"


# ---------------------------------------------------------------------------
# Test 13 — Factory: ollama + enabled=true → OllamaLocalProvider
# ---------------------------------------------------------------------------

def test_factory_ollama_provider_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER_NAME", "ollama")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_MODEL", "qwen3:8b")
    # No LLM_API_KEY set — Ollama must not require one.

    from app.llm.factory import get_llm_provider
    provider = get_llm_provider()

    assert isinstance(provider, OllamaLocalProvider)
    assert provider.provider_name == "ollama"


# ---------------------------------------------------------------------------
# Test 14 — Factory: unknown provider name → MockLLMProvider
# ---------------------------------------------------------------------------

def test_factory_unknown_provider_falls_back_to_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER_NAME", "nonexistent_provider_xyz")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")

    from app.llm.mock_provider import MockLLMProvider
    from app.llm.factory import get_llm_provider
    provider = get_llm_provider()

    assert isinstance(provider, MockLLMProvider)


# ---------------------------------------------------------------------------
# Test 15 — get_resolved_llm_provider_info: ollama → real_provider_enabled
# ---------------------------------------------------------------------------

def test_resolved_info_ollama_no_key_check(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER_NAME", "ollama")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    # Deliberately omit LLM_API_KEY — must not trigger missing_key_fallback.
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    from app.llm.factory import get_resolved_llm_provider_info
    info = get_resolved_llm_provider_info()

    assert info["provider"] == "ollama"
    assert info["reason"] == "real_provider_enabled"


# ---------------------------------------------------------------------------
# Test 16 — Factory: provider_enabled=false → MockLLMProvider regardless
# ---------------------------------------------------------------------------

def test_factory_provider_disabled_returns_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER_NAME", "ollama")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "false")

    from app.llm.mock_provider import MockLLMProvider
    from app.llm.factory import get_llm_provider
    provider = get_llm_provider()

    assert isinstance(provider, MockLLMProvider)


# ---------------------------------------------------------------------------
# Test 17 — __repr__ contains no secrets (no api key, no prompt text)
# ---------------------------------------------------------------------------

def test_repr_contains_no_secrets() -> None:
    provider = make_provider(model="qwen3:8b")
    r = repr(provider)

    assert "OllamaLocalProvider" in r
    assert "qwen3:8b" in r
    # Ensure no raw prompt/response text can appear in repr.
    assert SYSTEM_PROMPT not in r
    assert USER_MESSAGE not in r
    assert "api_key" not in r.lower()
    assert "secret" not in r.lower()


# ---------------------------------------------------------------------------
# Test 18 — provider_name == 'ollama'
# ---------------------------------------------------------------------------

def test_provider_name_is_ollama() -> None:
    provider = make_provider()
    assert provider.provider_name == "ollama"


# ---------------------------------------------------------------------------
# Test 19 — Request payload has correct structure
# ---------------------------------------------------------------------------

def test_request_payload_structure() -> None:
    body = make_ollama_response(content="pong")
    client = FakeHTTPClient(ProviderHTTPResponse(status_code=200, json_data=body))
    provider = make_provider(http_client=client)

    provider.generate(SAMPLE_REQUEST)

    payload = client.last_payload
    assert payload is not None

    # Required Ollama fields.
    assert payload["stream"] is False
    assert payload["think"] is False
    assert "keep_alive" in payload
    assert payload["model"] == "qwen3:8b"

    # Messages must be [system, user] in that order.
    messages = payload["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == SYSTEM_PROMPT
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == USER_MESSAGE
