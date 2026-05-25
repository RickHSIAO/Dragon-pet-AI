"""
dragon-pet-ai — Ollama local LLM provider.

Implements the LLMProvider Protocol using the Ollama REST API running on
localhost.  No API key required.  No external network calls.

Safety boundaries (mirrors HTTPRealLLMProvider):
- Renderer never calls Ollama directly — this class is backend-only.
- Raw prompt text is never logged.
- Raw Ollama response body is never forwarded to the frontend.
- One safe timeout retry is allowed after /api/tags confirms the local server is reachable.
- stream: false enforced — streaming is out of scope for Phase 4.
- No tool execution, no file access.
"""

import re
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
OLLAMA_TAGS_PATH = "/api/tags"
DEFAULT_OLLAMA_MODEL = "qwen3:8b"
DEFAULT_OLLAMA_TEMPERATURE = 0.7
DEFAULT_OLLAMA_NUM_PREDICT = 256
DEFAULT_LOCAL_TEST_TIMEOUT_SECONDS = 10
DEFAULT_OLLAMA_KEEP_ALIVE = "30m"
MAX_TIMEOUT_RETRIES = 1

_THINK_TAG_RE = re.compile(r"<think\b[^>]*>.*?</think>", re.IGNORECASE | re.DOTALL)
_THINKING_BLOCK_RE = re.compile(
    r"^\s*Thinking(?:\.\.\.|:)?[\s\S]*?(?:\.\.\.)?\s*done thinking\.?\s*",
    re.IGNORECASE,
)
_THINKING_PREFIX_LINE_RE = re.compile(
    r"^\s*(?:Thinking(?:\.\.\.|:)?|Reasoning:|Analysis:|Debug:)[^\n]*(?:\n+|$)",
    re.IGNORECASE,
)
_DONE_THINKING_LINE_RE = re.compile(
    r"^\s*(?:\.\.\.)?\s*done thinking\.?\s*(?:\n+|$)",
    re.IGNORECASE,
)


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
        keep_alive: str = DEFAULT_OLLAMA_KEEP_ALIVE,
        timeout_seconds: int = 30,
        test_timeout_seconds: int = DEFAULT_LOCAL_TEST_TIMEOUT_SECONDS,
        http_client: HTTPJSONClient | None = None,
    ) -> None:
        self._model = model.strip() or DEFAULT_OLLAMA_MODEL
        self._base_url = base_url.rstrip("/")
        self._keep_alive = keep_alive
        self._timeout_seconds = timeout_seconds
        self._test_timeout_seconds = test_timeout_seconds
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

    def test_connection(self, model: str | None = None) -> LLMResponse:
        """
        Fast Test Connection check for the local Ollama runtime.

        This performs a single ``GET /api/tags`` request — it does NOT load the
        model and does NOT call ``/api/chat``.  The Test Connection contract is
        intentionally narrow: confirm the local runtime is reachable and the
        requested model is present in the local model list.  Generation latency
        and persona behaviour are validated by ``/chat`` smoke tests, not here.

        On success returns ``LLMResponse(text="ok", error=None)``.

        On failure returns ``LLMResponse(text="", error=<safe_category>)`` where
        the category is one of:

        - ``ollama_unavailable`` — server is not reachable
        - ``provider_timeout``  — server did not respond in time
        - ``model_not_found``   — server alive, but model is not pulled
        - ``invalid_response``  — server responded with an unexpected body
        - ``provider_error``    — any other failure (collapsed to safe category)

        Exactly one HTTP request is made — no retries.  Raw provider bodies are
        never forwarded to the caller.
        """
        target_model = (model or self._model).strip() or self._model
        endpoint = self._base_url + OLLAMA_TAGS_PATH

        try:
            http_response = self._http_client.request_json(
                "GET",
                endpoint,
                headers={},
                payload={},
                timeout_seconds=self._test_timeout_seconds,
            )
        except httpx.TimeoutException:
            return self._safe_response("provider_timeout")
        except (httpx.ConnectError, ConnectionRefusedError, OSError):
            return self._safe_response("ollama_unavailable")
        except Exception:
            return self._safe_response("ollama_unavailable")

        if http_response.status_code < 200 or http_response.status_code >= 300:
            return self._safe_response("provider_error")

        try:
            data = http_response.json()
        except Exception:
            return self._safe_response("invalid_response")

        if not isinstance(data, dict):
            return self._safe_response("invalid_response")

        models_field = data.get("models")
        if not isinstance(models_field, list):
            return self._safe_response("invalid_response")

        installed_names: list[str] = []
        for entry in models_field:
            if not isinstance(entry, dict):
                continue
            # Ollama returns either ``name`` (older) or ``model`` (newer) — accept both.
            name = entry.get("name")
            if not isinstance(name, str):
                name = entry.get("model")
            if isinstance(name, str) and name.strip():
                installed_names.append(name.strip())

        if not _model_in_installed(target_model, installed_names):
            return LLMResponse(
                text="",
                provider="ollama",
                model=target_model,
                usage=None,
                error="model_not_found",
            )

        return LLMResponse(
            text="ok",
            provider="ollama",
            model=target_model,
            usage=None,
            error=None,
        )

    def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Send a chat completion request to the local Ollama server.

        At most one chat retry is made after a timeout if /api/tags is reachable.
        On any failure, returns a safe fallback response with an error category.
        Raw Ollama response bodies are never forwarded to the caller as-is.
        """
        endpoint = self._base_url + OLLAMA_CHAT_PATH
        payload = self._build_payload(request)

        timeout_retries_remaining = MAX_TIMEOUT_RETRIES
        while True:
            try:
                http_response = self._post_chat(endpoint, payload)
            except (TimeoutError, httpx.TimeoutException):
                if timeout_retries_remaining > 0 and self._ollama_server_reachable():
                    timeout_retries_remaining -= 1
                    continue
                return self._safe_response("provider_timeout")
            except (httpx.ConnectError, ConnectionRefusedError, OSError):
                return self._safe_response("ollama_unavailable")
            except Exception:
                return self._safe_response("ollama_unavailable")

            return self._handle_http_response(http_response)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _post_chat(self, endpoint: str, payload: dict[str, Any]) -> ProviderHTTPResponse:
        return self._http_client.request_json(
            "POST",
            endpoint,
            headers={"Content-Type": "application/json; charset=utf-8"},
            payload=payload,
            timeout_seconds=self._timeout_seconds,
        )

    def _ollama_server_reachable(self) -> bool:
        endpoint = self._base_url + OLLAMA_TAGS_PATH
        try:
            http_response = self._http_client.request_json(
                "GET",
                endpoint,
                headers={},
                payload={},
                timeout_seconds=self._test_timeout_seconds,
            )
        except Exception:
            return False
        return 200 <= http_response.status_code < 300

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

        content = _final_answer_text(data)
        if not content:
            return self._safe_response("invalid_response")

        # Token counts and durations. Ollama returns these as integers when
        # available; keep them as safe aggregate metadata only.
        output_tokens = data.get("eval_count")
        input_tokens = data.get("prompt_eval_count")
        total_duration = data.get("total_duration")
        eval_duration = data.get("eval_duration")

        usage: dict[str, Any] | None = None
        usage_fields = {
            "input_tokens_actual": input_tokens if isinstance(input_tokens, int) else None,
            "output_tokens_actual": output_tokens if isinstance(output_tokens, int) else None,
            "total_duration": total_duration if isinstance(total_duration, int) else None,
            "eval_duration": eval_duration if isinstance(eval_duration, int) else None,
        }
        if any(value is not None for value in usage_fields.values()):
            usage = usage_fields

        confirmed_model: str | None = None
        raw_model = data.get("model")
        if isinstance(raw_model, str) and raw_model.strip():
            confirmed_model = raw_model.strip()

        return LLMResponse(
            text=content,
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


def _final_answer_text(data: dict[str, Any]) -> str:
    """Return only the final user-facing Ollama answer text.

    Ollama chat responses use ``message.content``.  Some model/API paths can
    also return explicit thinking fields; those are intentionally ignored.
    The ``response`` fallback keeps the extraction safe for generate-style
    mocked payloads and future adapter reuse.
    """
    message = data.get("message")
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, str):
            return _strip_visible_reasoning(content)

    response = data.get("response")
    if isinstance(response, str):
        return _strip_visible_reasoning(response)

    return ""


def _strip_visible_reasoning(text: str) -> str:
    """Remove common visible thinking wrappers from final answer text."""
    cleaned = _THINK_TAG_RE.sub("", text).strip()
    for _ in range(4):
        previous = cleaned
        cleaned = _THINKING_BLOCK_RE.sub("", cleaned).strip()
        cleaned = _THINKING_PREFIX_LINE_RE.sub("", cleaned).strip()
        cleaned = _DONE_THINKING_LINE_RE.sub("", cleaned).strip()
        if cleaned == previous:
            break
    return cleaned


def _model_in_installed(target: str, installed: list[str]) -> bool:
    """Return True if ``target`` matches any installed Ollama model name.

    Ollama tag names may include a ``:<tag>`` suffix.  A request for ``qwen3``
    matches ``qwen3:latest`` and ``qwen3:8b``; a request for ``qwen3:8b``
    requires an exact match against the tagged entry.  Comparison is
    case-insensitive and ignores leading/trailing whitespace.
    """
    if not target:
        return False
    target_norm = target.strip().lower()
    if not target_norm:
        return False
    if ":" in target_norm:
        # Fully-qualified tag — exact match required.
        return any(name.lower() == target_norm for name in installed)
    # Unqualified name — match by base before ``:``.
    for name in installed:
        base = name.split(":", 1)[0].lower()
        if base == target_norm:
            return True
    return False
