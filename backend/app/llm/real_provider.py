from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from app.llm.types import LLMRequest, LLMResponse


ANTHROPIC_MESSAGES_ENDPOINT = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MAX_TOKENS = 512
CANONICAL_SAFE_FALLBACK_TEXT = (
    "I cannot reach the real language model right now, "
    "so I will continue in safe mock mode."
)


class HTTPJSONClient(Protocol):
    def request_json(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
        timeout_seconds: int,
    ) -> "ProviderHTTPResponse":
        ...


@dataclass(frozen=True)
class ProviderHTTPResponse:
    status_code: int
    json_data: Any = None

    def json(self) -> Any:
        return self.json_data


class HTTPXJSONClient:
    def request_json(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
        timeout_seconds: int,
    ) -> ProviderHTTPResponse:
        response = httpx.request(
            method,
            url,
            headers=headers,
            json=payload,
            timeout=timeout_seconds,
        )
        json_data: Any = None
        if 200 <= response.status_code < 300 and response.content:
            json_data = response.json()
        return ProviderHTTPResponse(status_code=response.status_code, json_data=json_data)


class SafeFallbackLLMProvider:
    @property
    def provider_name(self) -> str:
        return "safe_fallback"

    def generate(self, request: LLMRequest) -> LLMResponse:  # noqa: ARG002
        return LLMResponse(
            text=CANONICAL_SAFE_FALLBACK_TEXT,
            provider=self.provider_name,
            model=None,
            usage=None,
            error="provider_unavailable",
        )

    def health_check(self) -> bool:
        return False


class HTTPRealLLMProvider:
    def __init__(
        self,
        *,
        provider_name: str,
        api_key: str,
        model: str = "",
        timeout_seconds: int = 30,
        http_client: HTTPJSONClient | None = None,
        endpoint_url: str | None = None,
    ) -> None:
        self._provider_name = provider_name.strip().lower()
        self._api_key = api_key
        self._model = model.strip()
        self._timeout_seconds = timeout_seconds
        self._http_client = http_client or HTTPXJSONClient()
        self._endpoint_url = endpoint_url or ANTHROPIC_MESSAGES_ENDPOINT

    @property
    def provider_name(self) -> str:
        return self._provider_name

    def __repr__(self) -> str:
        return (
            "HTTPRealLLMProvider("
            f"provider_name={self._provider_name!r}, "
            f"model={self._model!r}, "
            "api_key='[REDACTED]', "
            f"timeout_seconds={self._timeout_seconds!r})"
        )

    def __str__(self) -> str:
        return repr(self)

    def health_check(self) -> bool:
        return bool(self._api_key)

    def generate(self, request: LLMRequest) -> LLMResponse:
        try:
            response = self._http_client.request_json(
                "POST",
                self._endpoint_url,
                headers={
                    "x-api-key": self._api_key,
                    "anthropic-version": ANTHROPIC_VERSION,
                    "Content-Type": "application/json",
                },
                payload=self._build_payload(request),
                timeout_seconds=self._timeout_seconds,
            )
        except (TimeoutError, httpx.TimeoutException):
            return self._safe_response("provider_timeout")
        except Exception:
            return self._safe_response("provider_unavailable")

        if response.status_code < 200 or response.status_code >= 300:
            return self._safe_response(self._error_for_status(response.status_code))

        try:
            data = response.json()
        except Exception:
            return self._safe_response("invalid_response")

        text = self._extract_text(data)
        if not text:
            return self._safe_response("invalid_response")

        return LLMResponse(
            text=text,
            provider=self.provider_name,
            model=self._extract_model(data),
            usage=self._extract_usage(data),
            error=None,
        )

    def _build_payload(self, request: LLMRequest) -> dict[str, Any]:
        return {
            "model": self._model,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "system": request.system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": request.user_message,
                }
            ],
        }

    def _extract_text(self, data: Any) -> str:
        if isinstance(data, dict):
            content_blocks = data.get("content")
            if isinstance(content_blocks, list):
                text_blocks = []
                for block in content_blocks:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") != "text":
                        continue
                    text = block.get("text")
                    if isinstance(text, str) and text.strip():
                        text_blocks.append(text.strip())
                if text_blocks:
                    return "\n".join(text_blocks)
        return ""

    def _extract_model(self, data: Any) -> str | None:
        if isinstance(data, dict):
            model = data.get("model")
            if isinstance(model, str) and model.strip():
                return model.strip()
        return self._model or None

    def _extract_usage(self, data: Any) -> dict[str, Any] | None:
        if isinstance(data, dict):
            usage = data.get("usage")
            if isinstance(usage, dict):
                return usage
        return None

    def _safe_response(self, error: str) -> LLMResponse:
        return LLMResponse(
            text=CANONICAL_SAFE_FALLBACK_TEXT,
            provider=self.provider_name,
            model=self._model or None,
            usage=None,
            error=error,
        )

    def _error_for_status(self, status_code: int) -> str:
        if status_code in (401, 403):
            return "provider_auth_error"
        if status_code == 429:
            return "rate_limit"
        return "provider_error"
