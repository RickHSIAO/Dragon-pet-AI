from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.db.database import engine
from app.db.models import MemoryInjectionAudit
from app.llm.real_provider import CANONICAL_SAFE_FALLBACK_TEXT, ProviderHTTPResponse
from app.main import app
from app.services.memory_service import create_memory


FAKE_API_KEY = "sk-task-043-fake-key"
RAW_BODY_SENTINEL = "RAW_PROVIDER_BODY_TASK_043"
USER_MESSAGE_SENTINEL = "USER_MESSAGE_TASK_043"
MEMORY_CONTEXT_SENTINEL = "MEMORY_CONTEXT_TASK_043"


class FakeHTTPXJSONClient:
    calls: list[dict] = []
    response = ProviderHTTPResponse(
        200,
        {
            "content": [{"type": "text", "text": "mocked anthropic chat reply"}],
            "model": "claude-task-043",
            "usage": {"input_tokens": 3, "output_tokens": 4},
        },
    )
    exc: Exception | None = None

    def request_json(self, method, url, headers, payload, timeout_seconds):
        self.__class__.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "payload": payload,
                "timeout_seconds": timeout_seconds,
            }
        )
        if self.__class__.exc is not None:
            raise self.__class__.exc
        return self.__class__.response


class OpaqueNon2xxResponse:
    status_code = 500

    def json(self):
        raise AssertionError("non-2xx body must remain opaque")


def reset_fake_http_client(response=None, exc=None):
    FakeHTTPXJSONClient.calls = []
    FakeHTTPXJSONClient.response = response or ProviderHTTPResponse(
        200,
        {
            "content": [{"type": "text", "text": "mocked anthropic chat reply"}],
            "model": "claude-task-043",
            "usage": {"input_tokens": 3, "output_tokens": 4},
        },
    )
    FakeHTTPXJSONClient.exc = exc


def configure_llm_chat(monkeypatch):
    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "anthropic")
    monkeypatch.setenv("LLM_API_KEY", FAKE_API_KEY)
    monkeypatch.setenv("LLM_MODEL", "claude-task-043")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "30")


def assert_chat_schema(data):
    assert set(data.keys()) == {"reply", "mood", "source"}


def post_chat(message="Hello!", use_memory=False):
    with TestClient(app) as client:
        return client.post(
            "/chat",
            json={"message": message, "use_memory": use_memory},
        )


def test_flag_matrix_chat_disabled_uses_old_mock(monkeypatch):
    monkeypatch.setenv("LLM_CHAT_ENABLED", "false")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "anthropic")
    monkeypatch.setenv("LLM_API_KEY", FAKE_API_KEY)

    response = post_chat()

    assert response.status_code == 200
    data = response.json()
    assert_chat_schema(data)
    assert data["source"] == "mock"


def test_flag_matrix_provider_disabled_uses_llm_mock(monkeypatch):
    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "false")

    response = post_chat()

    assert response.status_code == 200
    data = response.json()
    assert_chat_schema(data)
    assert data["source"] == "llm_mock"


def test_flag_matrix_provider_name_mock_uses_llm_mock(monkeypatch):
    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "mock")
    monkeypatch.setenv("LLM_API_KEY", FAKE_API_KEY)

    response = post_chat()

    assert response.status_code == 200
    data = response.json()
    assert_chat_schema(data)
    assert data["source"] == "llm_mock"


def test_flag_matrix_unknown_provider_falls_back_to_llm_mock(monkeypatch, caplog):
    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "unknown-provider")
    monkeypatch.setenv("LLM_API_KEY", FAKE_API_KEY)

    response = post_chat()

    assert response.status_code == 200
    data = response.json()
    assert_chat_schema(data)
    assert data["source"] == "llm_mock"
    assert FAKE_API_KEY not in caplog.text


def test_flag_matrix_missing_key_fallback_true_uses_llm_mock(monkeypatch, caplog):
    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "anthropic")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("LLM_FALLBACK_TO_MOCK", "true")

    response = post_chat()

    assert response.status_code == 200
    data = response.json()
    assert_chat_schema(data)
    assert data["source"] == "llm_mock"
    assert FAKE_API_KEY not in repr(data)
    assert FAKE_API_KEY not in caplog.text


def test_flag_matrix_missing_key_fallback_false_returns_safe_non_real_source(monkeypatch, caplog):
    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_NAME", "anthropic")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("LLM_FALLBACK_TO_MOCK", "false")

    response = post_chat()

    assert response.status_code == 200
    data = response.json()
    assert_chat_schema(data)
    assert data["reply"] == CANONICAL_SAFE_FALLBACK_TEXT
    assert data["source"] == "llm_real_error"
    assert data["source"] != "llm_real"
    assert FAKE_API_KEY not in caplog.text


def test_flag_matrix_anthropic_key_present_mocked_success_returns_llm_real(monkeypatch, caplog):
    configure_llm_chat(monkeypatch)
    reset_fake_http_client()
    monkeypatch.setattr("app.llm.real_provider.HTTPXJSONClient", FakeHTTPXJSONClient)

    response = post_chat(USER_MESSAGE_SENTINEL)

    assert response.status_code == 200
    data = response.json()
    observed = repr(data)
    assert_chat_schema(data)
    assert data["source"] == "llm_real"
    assert data["reply"] == "mocked anthropic chat reply"
    assert "usage" not in data
    assert "diagnostics" not in data
    assert "provider" not in data
    assert FAKE_API_KEY not in observed
    assert RAW_BODY_SENTINEL not in observed
    assert USER_MESSAGE_SENTINEL not in caplog.text
    assert len(FakeHTTPXJSONClient.calls) == 1


def test_real_provider_non_2xx_fallback_does_not_claim_llm_real(monkeypatch, caplog):
    configure_llm_chat(monkeypatch)
    monkeypatch.setenv("LLM_FALLBACK_TO_MOCK", "false")
    reset_fake_http_client(response=OpaqueNon2xxResponse())
    monkeypatch.setattr("app.llm.real_provider.HTTPXJSONClient", FakeHTTPXJSONClient)

    response = post_chat(USER_MESSAGE_SENTINEL)

    assert response.status_code == 200
    data = response.json()
    observed = "\n".join([repr(data), caplog.text])
    assert_chat_schema(data)
    assert data["reply"] == CANONICAL_SAFE_FALLBACK_TEXT
    assert data["source"] == "llm_real_error"
    assert data["source"] != "llm_real"
    assert FAKE_API_KEY not in observed
    assert RAW_BODY_SENTINEL not in observed
    assert USER_MESSAGE_SENTINEL not in observed
    assert len(FakeHTTPXJSONClient.calls) == 1


def test_real_provider_success_response_does_not_expose_provider_metadata(monkeypatch):
    configure_llm_chat(monkeypatch)
    reset_fake_http_client()
    monkeypatch.setattr("app.llm.real_provider.HTTPXJSONClient", FakeHTTPXJSONClient)

    response = post_chat()

    data = response.json()
    assert response.status_code == 200
    assert_chat_schema(data)
    assert data["source"] == "llm_real"
    assert "usage" not in data
    assert "input_tokens" not in repr(data)
    assert "claude-task-043" not in repr(data)
    assert FAKE_API_KEY not in repr(data)


def test_logging_safety_for_raw_body_prompt_user_message_and_memory_context(monkeypatch, caplog):
    configure_llm_chat(monkeypatch)
    monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
    reset_fake_http_client()
    monkeypatch.setattr("app.llm.real_provider.HTTPXJSONClient", FakeHTTPXJSONClient)

    with TestClient(app) as client:
        with Session(engine) as session:
            create_memory(
                session=session,
                memory_type="user_preference",
                content=MEMORY_CONTEXT_SENTINEL,
                importance=100,
            )
        response = client.post(
            "/chat",
            json={"message": USER_MESSAGE_SENTINEL, "use_memory": True},
        )

    observed = "\n".join([repr(response.json()), caplog.text])
    assert response.status_code == 200
    assert FAKE_API_KEY not in observed
    assert RAW_BODY_SENTINEL not in observed
    assert USER_MESSAGE_SENTINEL not in observed
    assert MEMORY_CONTEXT_SENTINEL not in observed


def test_llm_chat_enabled_alone_does_not_create_memory_audit(monkeypatch):
    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER_ENABLED", "false")
    monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "false")

    with TestClient(app) as client:
        with Session(engine) as session:
            before = len(session.exec(select(MemoryInjectionAudit)).all())
        response = client.post("/chat", json={"message": "Hello!", "use_memory": True})
        with Session(engine) as session:
            after = len(session.exec(select(MemoryInjectionAudit)).all())

    assert response.status_code == 200
    assert response.json()["source"] == "llm_mock"
    assert after == before


def test_memory_flags_do_not_enable_llm_when_chat_flag_disabled(monkeypatch):
    monkeypatch.setenv("LLM_CHAT_ENABLED", "false")
    monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")

    def raise_if_called():
        raise AssertionError("LLM provider factory should not be called")

    monkeypatch.setattr("app.services.chat_service.get_llm_provider", raise_if_called)

    response = post_chat("Hello!", use_memory=True)

    assert response.status_code == 200
    assert response.json()["source"] == "mock"


def test_both_llm_and_memory_gates_true_do_not_leak_memory_or_provider_details(monkeypatch):
    configure_llm_chat(monkeypatch)
    monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
    reset_fake_http_client()
    monkeypatch.setattr("app.llm.real_provider.HTTPXJSONClient", FakeHTTPXJSONClient)

    with TestClient(app) as client:
        with Session(engine) as session:
            create_memory(
                session=session,
                memory_type="user_preference",
                content=MEMORY_CONTEXT_SENTINEL,
                importance=100,
            )
            before_ids = {row.id for row in session.exec(select(MemoryInjectionAudit)).all()}
        response = client.post(
            "/chat",
            json={"message": "Hello!", "use_memory": True},
        )
        with Session(engine) as session:
            new_rows = [
                row
                for row in session.exec(select(MemoryInjectionAudit)).all()
                if row.id not in before_ids
            ]

    data = response.json()
    observed_response = repr(data)
    audit_text = "\n".join(
        (row.selected_memory_ids_json or "") + (row.exclusion_summary_json or "")
        for row in new_rows
    )
    assert response.status_code == 200
    assert data["source"] == "llm_real"
    assert MEMORY_CONTEXT_SENTINEL not in observed_response
    assert FAKE_API_KEY not in observed_response
    assert "mocked anthropic chat reply" not in audit_text
    assert "anthropic" not in audit_text
    assert RAW_BODY_SENTINEL not in audit_text
    assert len(new_rows) == 1


def test_real_provider_mocked_http_called_once_no_retry(monkeypatch):
    configure_llm_chat(monkeypatch)
    reset_fake_http_client(response=OpaqueNon2xxResponse())
    monkeypatch.setattr("app.llm.real_provider.HTTPXJSONClient", FakeHTTPXJSONClient)

    response = post_chat()

    assert response.status_code == 200
    assert len(FakeHTTPXJSONClient.calls) == 1
