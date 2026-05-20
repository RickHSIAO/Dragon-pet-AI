import httpx
import pytest

from app.llm.real_provider import (
    CANONICAL_SAFE_FALLBACK_TEXT,
    HTTPRealLLMProvider,
    ProviderHTTPResponse,
)
from app.llm.types import LLMRequest, LLMResponse


class FakeHTTPClient:
    def __init__(self, response=None, exc=None):
        self.response = response
        self.exc = exc
        self.calls = []

    def request_json(self, method, url, headers, payload, timeout_seconds):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "payload": payload,
                "timeout_seconds": timeout_seconds,
            }
        )
        if self.exc is not None:
            raise self.exc
        return self.response


class Non2xxResponse:
    status_code = 500

    def json(self):
        raise AssertionError("non-2xx body must remain opaque")


def make_request() -> LLMRequest:
    return LLMRequest(
        system_prompt="system",
        user_message="hello",
        mode="casual",
        memory_context="memory",
        state_context={"mood": "focused"},
        conversation_history=[{"role": "user", "content": "hello"}],
    )


def make_provider(api_key="sk-test-secret-value", client=None) -> HTTPRealLLMProvider:
    return HTTPRealLLMProvider(
        provider_name="anthropic",
        api_key=api_key,
        model="test-model",
        timeout_seconds=7,
        http_client=client or FakeHTTPClient(ProviderHTTPResponse(200, {"text": "ok"})),
    )


def test_real_provider_generate_success_returns_llm_response():
    client = FakeHTTPClient(
        ProviderHTTPResponse(
            200,
            {
                "content": [{"type": "text", "text": "provider reply"}],
                "model": "claude-test",
            },
        )
    )
    provider = make_provider(client=client)

    response = provider.generate(make_request())

    assert isinstance(response, LLMResponse)
    assert response.text == "provider reply"
    assert response.provider == "anthropic"
    assert response.model == "claude-test"
    assert response.usage is None
    assert response.error is None
    assert len(client.calls) == 1
    assert client.calls[0]["method"] == "POST"
    assert client.calls[0]["timeout_seconds"] == 7


def test_real_provider_accepts_anthropic_multiple_text_blocks():
    client = FakeHTTPClient(
        ProviderHTTPResponse(
            200,
            {
                "content": [
                    {"type": "text", "text": "first"},
                    {"type": "tool_use", "id": "ignored"},
                    {"type": "text", "text": "second"},
                ],
            },
        )
    )
    provider = make_provider(client=client)

    response = provider.generate(make_request())

    assert response.text == "first\nsecond"
    assert response.error is None


def test_real_provider_non_2xx_body_is_opaque():
    provider = make_provider(client=FakeHTTPClient(Non2xxResponse()))

    response = provider.generate(make_request())

    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "provider_error"


def test_real_provider_timeout_returns_safe_response():
    client = FakeHTTPClient(exc=httpx.TimeoutException("timeout with no secret"))
    provider = make_provider(client=client)

    response = provider.generate(make_request())

    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "provider_timeout"
    assert len(client.calls) == 1


@pytest.mark.parametrize(
    "json_data",
    [
        None,
        {},
        {"content": []},
        {"content": [{"type": "text", "text": ""}]},
        {"content": [{"type": "tool_use", "id": "ignored"}]},
    ],
)
def test_real_provider_invalid_response_returns_safe_response(json_data):
    client = FakeHTTPClient(ProviderHTTPResponse(200, json_data))
    provider = make_provider(client=client)

    response = provider.generate(make_request())

    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "invalid_response"
    assert "SECRET" not in response.text


def test_real_provider_unexpected_exception_returns_safe_response():
    client = FakeHTTPClient(exc=RuntimeError("raw provider error should not leak"))
    provider = make_provider(client=client)

    response = provider.generate(make_request())

    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "provider_unavailable"
    assert len(client.calls) == 1


def test_real_provider_does_not_retry_non_2xx():
    client = FakeHTTPClient(Non2xxResponse())
    provider = make_provider(client=client)

    provider.generate(make_request())

    assert len(client.calls) == 1


def test_real_provider_repr_and_str_redact_api_key():
    key = "sk-test-secret-value"
    provider = make_provider(api_key=key)

    assert key not in repr(provider)
    assert key not in str(provider)
    assert "[REDACTED]" in repr(provider)


def test_real_provider_caplog_does_not_contain_api_key(caplog):
    key = "sk-test-secret-value"
    provider = make_provider(api_key=key, client=FakeHTTPClient(Non2xxResponse()))

    provider.generate(make_request())

    assert key not in caplog.text


def test_real_provider_stdout_stderr_do_not_contain_api_key(capsys):
    key = "sk-test-secret-value"
    provider = make_provider(api_key=key, client=FakeHTTPClient(Non2xxResponse()))

    provider.generate(make_request())
    captured = capsys.readouterr()

    assert key not in captured.out
    assert key not in captured.err
