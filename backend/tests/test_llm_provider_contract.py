import httpx
from fastapi.testclient import TestClient

from app.llm.mock_provider import MockLLMProvider
from app.llm.real_provider import (
    ANTHROPIC_MESSAGES_ENDPOINT,
    ANTHROPIC_VERSION,
    CANONICAL_SAFE_FALLBACK_TEXT,
    DEFAULT_MAX_TOKENS,
    HTTPRealLLMProvider,
    ProviderHTTPResponse,
)
from app.llm.types import LLMRequest
from app.main import app


FAKE_API_KEY = "sk-test-contract-secret-1234567890"
RAW_BODY_SENTINEL = "RAW_PROVIDER_BODY_SHOULD_STAY_OPAQUE"
USER_MESSAGE_SENTINEL = "USER_MESSAGE_SHOULD_NOT_BE_LOGGED"
SYSTEM_PROMPT_SENTINEL = "SYSTEM_PROMPT_SHOULD_NOT_BE_LOGGED"
MEMORY_SENTINEL = "MEMORY_CONTEXT_SHOULD_NOT_BE_LOGGED"


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


class OpaqueNon2xxResponse:
    def __init__(self, status_code):
        self.status_code = status_code

    def json(self):
        raise AssertionError("non-2xx body must not be parsed")

    def __repr__(self):
        return f"OpaqueNon2xxResponse({RAW_BODY_SENTINEL})"


class MalformedJSONResponse:
    status_code = 200

    def json(self):
        raise ValueError(f"malformed {RAW_BODY_SENTINEL}")


def make_request() -> LLMRequest:
    return LLMRequest(
        system_prompt=SYSTEM_PROMPT_SENTINEL,
        user_message=USER_MESSAGE_SENTINEL,
        mode="casual",
        memory_context=MEMORY_SENTINEL,
        state_context={"mood": "focused"},
        conversation_history=[{"role": "user", "content": "previous"}],
    )


def make_provider(client) -> HTTPRealLLMProvider:
    return HTTPRealLLMProvider(
        provider_name="anthropic",
        api_key=FAKE_API_KEY,
        model="claude-contract-test",
        timeout_seconds=9,
        http_client=client,
    )


def test_anthropic_request_contract_method_endpoint_headers_and_body():
    client = FakeHTTPClient(
        ProviderHTTPResponse(
            200,
            {"content": [{"type": "text", "text": "ok"}], "model": "claude-contract-test"},
        )
    )
    provider = make_provider(client)

    provider.generate(make_request())

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["method"] == "POST"
    assert call["url"] == ANTHROPIC_MESSAGES_ENDPOINT
    assert call["url"].endswith("/v1/messages")
    assert call["headers"]["x-api-key"] == FAKE_API_KEY
    assert call["headers"]["anthropic-version"] == ANTHROPIC_VERSION
    assert call["headers"]["Content-Type"] == "application/json"

    payload = call["payload"]
    assert payload["model"] == "claude-contract-test"
    assert payload["max_tokens"] == DEFAULT_MAX_TOKENS
    assert payload["system"] == SYSTEM_PROMPT_SENTINEL
    assert isinstance(payload["messages"], list)
    assert payload["messages"][0]["role"] == "user"
    assert payload["messages"][0]["content"] == USER_MESSAGE_SENTINEL
    assert "stream" not in payload
    assert "tools" not in payload


def test_anthropic_success_parses_text_usage_provider_and_model():
    usage = {"input_tokens": 10, "output_tokens": 4}
    client = FakeHTTPClient(
        ProviderHTTPResponse(
            200,
            {
                "content": [
                    {"type": "text", "text": "first"},
                    {"type": "tool_use", "id": "ignored"},
                    {"type": "text", "text": "second"},
                ],
                "model": "claude-3-5-sonnet-test",
                "usage": usage,
            },
        )
    )
    provider = make_provider(client)

    response = provider.generate(make_request())

    assert response.text == "first\nsecond"
    assert response.provider == "anthropic"
    assert response.model == "claude-3-5-sonnet-test"
    assert response.usage == usage
    assert response.error is None


def test_anthropic_non_text_blocks_are_ignored_safely():
    client = FakeHTTPClient(
        ProviderHTTPResponse(
            200,
            {
                "content": [
                    {"type": "tool_use", "name": "ignored"},
                    {"type": "text", "text": "visible text"},
                ],
            },
        )
    )
    provider = make_provider(client)

    response = provider.generate(make_request())

    assert response.text == "visible text"
    assert response.error is None


def test_auth_failure_maps_safely_and_body_stays_opaque():
    client = FakeHTTPClient(OpaqueNon2xxResponse(401))
    provider = make_provider(client)

    response = provider.generate(make_request())

    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "provider_auth_error"
    assert RAW_BODY_SENTINEL not in response.text
    assert RAW_BODY_SENTINEL not in response.error


def test_permission_failure_maps_safely():
    response = make_provider(FakeHTTPClient(OpaqueNon2xxResponse(403))).generate(make_request())

    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "provider_auth_error"


def test_rate_limit_maps_safely():
    response = make_provider(FakeHTTPClient(OpaqueNon2xxResponse(429))).generate(make_request())

    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "rate_limit"


def test_provider_error_maps_safely_and_body_stays_opaque():
    client = FakeHTTPClient(OpaqueNon2xxResponse(500))
    provider = make_provider(client)

    response = provider.generate(make_request())

    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "provider_error"
    assert RAW_BODY_SENTINEL not in response.text
    assert RAW_BODY_SENTINEL not in response.error


def test_malformed_json_maps_invalid_response_safely():
    response = make_provider(FakeHTTPClient(MalformedJSONResponse())).generate(make_request())

    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "invalid_response"
    assert RAW_BODY_SENTINEL not in response.text
    assert RAW_BODY_SENTINEL not in response.error


def test_empty_text_maps_invalid_response_safely():
    client = FakeHTTPClient(ProviderHTTPResponse(200, {"content": [{"type": "text", "text": "  "}]}))
    provider = make_provider(client)

    response = provider.generate(make_request())

    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "invalid_response"


def test_timeout_maps_provider_timeout_safely_and_no_retry():
    client = FakeHTTPClient(exc=httpx.TimeoutException("timeout"))
    provider = make_provider(client)

    response = provider.generate(make_request())

    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "provider_timeout"
    assert len(client.calls) == 1


def test_network_failure_maps_provider_unavailable_safely_and_no_retry():
    client = FakeHTTPClient(exc=httpx.ConnectError("network down"))
    provider = make_provider(client)

    response = provider.generate(make_request())

    assert response.text == CANONICAL_SAFE_FALLBACK_TEXT
    assert response.error == "provider_unavailable"
    assert len(client.calls) == 1


def test_api_key_absent_from_caplog_stdout_stderr_repr_str_and_response(caplog, capsys):
    client = FakeHTTPClient(OpaqueNon2xxResponse(500))
    provider = make_provider(client)

    response = provider.generate(make_request())
    captured = capsys.readouterr()

    assert FAKE_API_KEY not in caplog.text
    assert FAKE_API_KEY not in captured.out
    assert FAKE_API_KEY not in captured.err
    assert FAKE_API_KEY not in repr(provider)
    assert FAKE_API_KEY not in str(provider)
    assert FAKE_API_KEY not in response.text
    assert FAKE_API_KEY not in response.error


def test_raw_body_prompt_user_message_and_memory_context_absent_from_logs_and_response(caplog, capsys):
    client = FakeHTTPClient(OpaqueNon2xxResponse(500))
    provider = make_provider(client)

    response = provider.generate(make_request())
    captured = capsys.readouterr()
    observed = "\n".join(
        [
            caplog.text,
            captured.out,
            captured.err,
            response.text,
            response.error or "",
        ]
    )

    assert RAW_BODY_SENTINEL not in observed
    assert USER_MESSAGE_SENTINEL not in observed
    assert SYSTEM_PROMPT_SENTINEL not in observed
    assert MEMORY_SENTINEL not in observed


def test_chat_old_format_still_returns_200():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200


def test_chat_response_schema_remains_reply_mood_source():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}


def test_chat_is_not_wired_to_real_provider_yet(monkeypatch):
    def raise_if_used(self, request):  # noqa: ARG001
        raise AssertionError("/chat should not call MockLLMProvider yet")

    monkeypatch.setattr(MockLLMProvider, "generate", raise_if_used)

    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}
