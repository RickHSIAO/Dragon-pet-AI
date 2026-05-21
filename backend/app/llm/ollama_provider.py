"""
dragon-pet-ai — Ollama local LLM provider.

Implements the LLMProvider Protocol using the Ollama REST API running on
localhost.  No API key required.  No external network calls.

Safety boundaries (mirrors HTTPRealLLMProvider):
- Renderer never calls Ollama directly — this class is backend-only.
- Raw prompt text is never logged.
- Raw Ollama response body is never forwarded to the frontend.
- No automatic retries — exactly one request per generate() call.
- stream: false enforced — streaming is out of scope for Phase 4.
- No tool execution, no file access.
"""

from typing import Any

import httpx

from app.llm.real_provider import (
    CANONICAL_SAFE_FALLBACK_TEXT,
    HTTPJSONClient,
    HTTPXJSONClient,
    ProviderHTTPResponse,
)
from app.llm.types import LLMRequest, LLMResponse


OLLAMA_CHAT_PATH = "/api/chat"
DEFAULT_OLLAMA_MODEL = "qwen3:8b"
DEFAULT_OLLAMA_TEMPERATURE = 0.7
DEFAULT_OLLAMA_NUM_PREDICT = 256


class OllamaLocalProvider:
    """
    Local LLM provider backed by an Ollama server running on localhost.

    Implements the same generate() / health_check() interface as
    HTTPRealLLMProvider so it can be returned from the factory transparently.

    __repr__ and __str__ are safe to log — they contain no secrets and no
    model-generated text.
    """

    def __init__(
        self,
        *,
        model: str = DEFAULT_OLLAMA_MODEL,
        base_url: str = "http://localhost:11434",
        keep_alive: str = "10m",
        timeout_seconds: int = 30,
        http_client: HTTPJSONClient | None = None,
    ) -> None:
        self._model = model.strip() or DEFAULT_OLLAMA_MODEL
        self._base_url = base_url.rstrip("/")
        self._keep_alive = keep_alive
        self._timeout_seconds = timeout_seconds
        self._http_client: HTTPJSONClient = http_client or HTTPXJSONClient()

    @property
    def provider_name(self) -> str:
        return "ollama"

    def __repr__(self) -> str:
        return (
            "OllamaLocalProvider("
            f"model={self._model!r}, "
            f"base_url={self._base_url!r}, "
            f"keep_alive={self._keep_alive!r}, "
            f"timeout_seconds={self._timeout_seconds!r})"
        )

    def __str__(self) -> str:
        return repr(self)

    def health_check(self) -> bool:
        """
        Return True if the Ollama server appears reachable.

        Sends a HEAD request to the base URL.  A network error → False.
        This is a best-effort check — it does not pull or load any model.
        """
        try:
            response = self._http_client.request_json(
                "GET",
                self._base_url,
                headers={},
                payload={},
                timeout_seconds=5,
            )
            return response.status_code < 500
        except Exception:
            return False

    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Send a chat completion request to the local Ollama server.

        Exactly one HTTP request is made per call — no retries.
        On any failure, returns a safe fallback response with an error category.
        Raw Ollama response bodies are never forwarded to the caller as-is.
        """
        endpoint = self._base_url + OLLAMA_CHAT_PATH
        payload = self._build_payload(request)

        try:
            http_response = self._http_client.request_json(
                "POST",
                endpoint,
                headers={"Content-Type": "application/json; charset=utf-8"},
                payload=payload,
                timeout_seconds=self._timeout_seconds,
            )
        except httpx.TimeoutException:
            return self._safe_response("provider_timeout")
        except (httpx.ConnectError, ConnectionRefusedError, OSError):
            return self._safe_response("ollama_unavailable")
        except Exception:
            return self._safe_response("ollama_unavailable")

        return self._handle_http_response(http_response)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_payload(self, request: LLMRequest) -> dict[str, Any]:
        return {
            "model": self._model,
            "stream": False,
            "think": False,
            "keep_alive": self._keep_alive,
            "options": {
                "temperature": DEFAULT_OLLAMA_TEMPERATURE,
                "num_predict": DEFAULT_OLLAMA_NUM_PREDICT,
            },
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_message},
            ],
        }

    def _handle_http_response(self, response: ProviderHTTPResponse) -> LLMResponse:
        if response.status_code == 404:
            return self._safe_response("model_not_found")
        if response.status_code < 200 or response.status_code >= 300:
            return self._safe_response("provider_error")

        try:
            data = response.json()
        except Exception:
            return self._safe_response("invalid_response")

        return self._extract_llm_response(data)

    def _extract_llm_response(self, data: Any) -> LLMResponse:
        """Extract LLMResponse from a parsed Ollama JSON response body."""
        if not isinstance(data, dict):
            return self._safe_response("invalid_response")

        message = data.get("message")
        if not isinstance(message, dict):
            return self._safe_response("invalid_response")

        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            return self._safe_response("invalid_response")

        # Token counts — Ollama returns these as integers when available.
        output_tokens = data.get("eval_count")
        input_tokens = data.get("prompt_eval_count")

        usage: dict[str, Any] | None = None
        if isinstance(output_tokens, int) or isinstance(input_tokens, int):
            usage = {
                "input_tokens_actual": input_tokens if isinstance(input_tokens, int) else None,
                "output_tokens_actual": output_tokens if isinstance(output_tokens, int) else None,
            }

        confirmed_model: str | None = None
        raw_model = data.get("model")
        if isinstance(raw_model, str) and raw_model.strip():
            confirmed_model = raw_model.strip()

        return LLMResponse(
            text=content.strip(),
            provider="ollama",
            model=confirmed_model or self._model,
            usage=usage,
            error=None,
        )

    def _safe_response(self, error: str) -> LLMResponse:
        return LLMResponse(
            text=CANONICAL_SAFE_FALLBACK_TEXT,
            provider="ollama",
            model=self._model,
            usage=None,
            error=error,
        )
