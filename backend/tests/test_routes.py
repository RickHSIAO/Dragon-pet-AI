import os

from fastapi.testclient import TestClient
from sqlmodel import Session, select

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

from app.db.database import engine  # noqa: E402
from app.db.models import Memory, MemoryInjectionAudit, Message, RelationshipState  # noqa: E402
from app.main import app  # noqa: E402
from app.services.memory_service import create_memory  # noqa: E402


def test_health_returns_ok_status_and_service():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "dragon-pet-ai",
    }


# ---------------------------------------------------------------------------
# TASK-197: /provider/health endpoint
# ---------------------------------------------------------------------------

def test_provider_health_returns_not_applicable_for_mock_provider():
    # Default test environment uses mock provider (real_provider_enabled=False).
    with TestClient(app) as client:
        response = client.get("/provider/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_applicable"
    assert data["ollama_reachable"] is None
    assert "provider" in data


def test_provider_health_returns_not_applicable_when_real_provider_disabled(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.get_provider_settings",
        lambda: {"provider": "ollama", "real_provider_enabled": False},
    )
    with TestClient(app) as client:
        response = client.get("/provider/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_applicable"
    assert data["provider"] == "ollama"
    assert data["ollama_reachable"] is None


def test_provider_health_ollama_reachable_returns_ok(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.get_provider_settings",
        lambda: {"provider": "ollama", "real_provider_enabled": True},
    )
    monkeypatch.setattr(
        "app.api.routes.check_ollama_server_liveness",
        lambda: True,
    )
    with TestClient(app) as client:
        response = client.get("/provider/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["ollama_reachable"] is True
    assert data["provider"] == "ollama"


def test_provider_health_ollama_unreachable_returns_unavailable(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.get_provider_settings",
        lambda: {"provider": "ollama", "real_provider_enabled": True},
    )
    monkeypatch.setattr(
        "app.api.routes.check_ollama_server_liveness",
        lambda: False,
    )
    with TestClient(app) as client:
        response = client.get("/provider/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unavailable"
    assert data["ollama_reachable"] is False
    assert data["provider"] == "ollama"


def test_chat_valid_message_returns_mock_response():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "mood" in data
    assert data["source"] == "mock"


def test_chat_with_debug_mode_returns_mock_response():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={"message": "help me debug", "mode": "debug"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "mood" in data
    assert data["source"] == "mock"


def test_chat_stores_user_and_assistant_messages():
    with TestClient(app) as client:
        with Session(engine) as session:
            before_count = len(session.exec(select(Message)).all())

        response = client.post(
            "/chat",
            json={"message": "help me debug", "mode": "debug"},
        )

        with Session(engine) as session:
            messages = session.exec(select(Message).order_by(Message.id)).all()

    assert response.status_code == 200
    new_messages = messages[before_count:]
    assert len(new_messages) == 2
    assert new_messages[0].role == "user"
    assert new_messages[0].content == "help me debug"
    assert new_messages[1].role == "assistant"
    assert new_messages[1].mode == "debug"
    assert new_messages[1].mood
    assert new_messages[1].source == "mock"


def test_chat_updates_internal_state_without_changing_response_schema():
    with TestClient(app) as client:
        with Session(engine) as session:
            before_state = session.exec(select(RelationshipState)).first()
            before_count = before_state.interaction_count if before_state else 0

        response = client.post(
            "/chat",
            json={"message": "I need support", "mode": "support"},
        )

        with Session(engine) as session:
            relationship_state = session.exec(select(RelationshipState)).first()

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}
    assert response.json()["source"] == "mock"
    assert relationship_state is not None
    assert relationship_state.interaction_count == before_count + 1
    assert relationship_state.affection >= 1


def test_chat_response_does_not_include_state_fields():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "hello"})

    data = response.json()
    assert response.status_code == 200
    assert set(data.keys()) == {"reply", "mood", "source"}
    assert "interaction_count" not in data
    assert "familiarity" not in data
    assert "affection" not in data
    assert "trust" not in data


def test_chat_response_does_not_include_memory_fields():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "hello"})

    data = response.json()
    assert response.status_code == 200
    assert set(data.keys()) == {"reply", "mood", "source"}
    assert "memory" not in data
    assert "memories" not in data
    assert "memory_context" not in data


def test_chat_does_not_consume_approved_memory_context():
    with TestClient(app) as client:
        with Session(engine) as session:
            create_memory(
                session=session,
                memory_type="user_preference",
                content="Unique approved memory phrase",
                importance=100,
            )

        response = client.post("/chat", json={"message": "hello"})

    data = response.json()
    assert response.status_code == 200
    assert "Unique approved memory phrase" not in data["reply"]


def test_chat_does_not_create_memory_automatically():
    with TestClient(app) as client:
        with Session(engine) as session:
            before_count = len(session.exec(select(Memory)).all())

        response = client.post("/chat", json={"message": "hello"})

        with Session(engine) as session:
            after_count = len(session.exec(select(Memory)).all())

    assert response.status_code == 200
    assert after_count == before_count


def test_chat_with_support_mode_returns_mock_response():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={"message": "I need support", "mode": "support"},
        )

    assert response.status_code == 200
    assert response.json()["source"] == "mock"


def test_chat_with_unknown_mode_falls_back_safely():
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={"message": "hello", "mode": "unknown"},
        )

    assert response.status_code == 200
    assert response.json()["source"] == "mock"


def test_chat_missing_message_returns_validation_error():
    with TestClient(app) as client:
        response = client.post("/chat", json={"text": "Hello!"})

    assert response.status_code == 422


def test_chat_empty_json_returns_validation_error():
    with TestClient(app) as client:
        response = client.post("/chat", json={})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# TASK-020 — flag disabled (default)
# ---------------------------------------------------------------------------

class TestChatFlagDisabled:
    """
    When MEMORY_INJECTION_ENABLED is absent or False, /chat must behave
    identically to pre-TASK-020: no audit rows, no memory context.
    """

    def test_flag_disabled_returns_200(self, monkeypatch):
        monkeypatch.delenv("MEMORY_INJECTION_ENABLED", raising=False)
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello"})
        assert response.status_code == 200

    def test_flag_disabled_response_schema_is_unchanged(self, monkeypatch):
        monkeypatch.delenv("MEMORY_INJECTION_ENABLED", raising=False)
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello"})
        assert set(response.json().keys()) == {"reply", "mood", "source"}

    def test_flag_disabled_does_not_create_audit_rows(self, monkeypatch):
        monkeypatch.delenv("MEMORY_INJECTION_ENABLED", raising=False)
        with TestClient(app) as client:
            with Session(engine) as session:
                before = len(session.exec(select(MemoryInjectionAudit)).all())
            client.post("/chat", json={"message": "hello"})
            with Session(engine) as session:
                after = len(session.exec(select(MemoryInjectionAudit)).all())
        assert after == before

    def test_flag_disabled_response_has_no_memory_fields(self, monkeypatch):
        monkeypatch.delenv("MEMORY_INJECTION_ENABLED", raising=False)
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello"})
        data = response.json()
        assert "memory" not in data
        assert "memory_context" not in data
        assert "selected_ids" not in data
        assert "audit" not in data

    def test_flag_false_string_does_not_create_audit_rows(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "false")
        with TestClient(app) as client:
            with Session(engine) as session:
                before = len(session.exec(select(MemoryInjectionAudit)).all())
            client.post("/chat", json={"message": "hello"})
            with Session(engine) as session:
                after = len(session.exec(select(MemoryInjectionAudit)).all())
        assert after == before


# ---------------------------------------------------------------------------
# TASK-020 — flag enabled
# ---------------------------------------------------------------------------

class TestChatFlagEnabled:
    """
    When MEMORY_INJECTION_ENABLED=true, /chat must build approved memory
    context and write one MemoryInjectionAudit row per call.
    Response schema and source must remain unchanged.
    Memory content must never appear in the response.
    """

    def test_flag_enabled_returns_200(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello"})
        assert response.status_code == 200

    def test_flag_enabled_response_schema_is_unchanged(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello"})
        assert set(response.json().keys()) == {"reply", "mood", "source"}

    def test_flag_enabled_source_remains_mock(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello"})
        assert response.json()["source"] == "mock"

    def test_flag_enabled_creates_one_audit_row_per_call(self, monkeypatch):
        # Both layers must be True → audit row created.
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            with Session(engine) as session:
                before = len(session.exec(select(MemoryInjectionAudit)).all())
            client.post("/chat", json={"message": "hello", "use_memory": True})
            with Session(engine) as session:
                after = len(session.exec(select(MemoryInjectionAudit)).all())
        assert after == before + 1

    def test_flag_enabled_audit_feature_flag_enabled_is_true(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            with Session(engine) as session:
                before_ids = {
                    row.id for row in session.exec(select(MemoryInjectionAudit)).all()
                }
            client.post("/chat", json={"message": "hello", "use_memory": True})
            with Session(engine) as session:
                new_rows = [
                    row for row in session.exec(select(MemoryInjectionAudit)).all()
                    if row.id not in before_ids
                ]
        assert len(new_rows) == 1
        assert new_rows[0].feature_flag_enabled is True

    def test_flag_enabled_with_eligible_memory_selected_count_matches(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            with Session(engine) as session:
                create_memory(
                    session=session,
                    memory_type="user_preference",
                    content="Prefers concise replies for test_flag_enabled_selected_count",
                    importance=80,
                )
                before_ids = {
                    row.id for row in session.exec(select(MemoryInjectionAudit)).all()
                }

            client.post("/chat", json={"message": "hello", "use_memory": True})

            with Session(engine) as session:
                new_rows = [
                    row for row in session.exec(select(MemoryInjectionAudit)).all()
                    if row.id not in before_ids
                ]
        assert len(new_rows) == 1
        # selected_count must be ≥ 1 because we added an eligible memory
        assert new_rows[0].selected_count >= 1

    def test_flag_enabled_with_eligible_memory_total_context_chars_greater_than_zero(
        self, monkeypatch
    ):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            with Session(engine) as session:
                create_memory(
                    session=session,
                    memory_type="project_context",
                    content="Project is dragon-pet-ai for context chars test",
                    importance=90,
                )
                before_ids = {
                    row.id for row in session.exec(select(MemoryInjectionAudit)).all()
                }

            client.post("/chat", json={"message": "hello", "use_memory": True})

            with Session(engine) as session:
                new_rows = [
                    row for row in session.exec(select(MemoryInjectionAudit)).all()
                    if row.id not in before_ids
                ]
        assert new_rows[0].total_context_chars > 0

    def test_flag_enabled_audit_does_not_contain_raw_memory_content(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        unique_phrase = "UNIQUE_CONTENT_PHRASE_DO_NOT_STORE_2025"
        with TestClient(app) as client:
            with Session(engine) as session:
                create_memory(
                    session=session,
                    memory_type="user_preference",
                    content=unique_phrase,
                    importance=100,
                )
                before_ids = {
                    row.id for row in session.exec(select(MemoryInjectionAudit)).all()
                }

            client.post("/chat", json={"message": "hello", "use_memory": True})

            with Session(engine) as session:
                new_rows = [
                    row for row in session.exec(select(MemoryInjectionAudit)).all()
                    if row.id not in before_ids
                ]

        assert len(new_rows) == 1
        audit = new_rows[0]
        stored_text = (
            (audit.selected_memory_ids_json or "")
            + (audit.exclusion_summary_json or "")
        )
        assert unique_phrase not in stored_text

    def test_flag_enabled_sensitive_memory_not_selected(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            with Session(engine) as session:
                sensitive = create_memory(
                    session=session,
                    memory_type="user_preference",
                    content="My password is hunter2",
                    importance=100,
                )
                before_ids = {
                    row.id for row in session.exec(select(MemoryInjectionAudit)).all()
                }

            client.post("/chat", json={"message": "hello", "use_memory": True})

            with Session(engine) as session:
                new_rows = [
                    row for row in session.exec(select(MemoryInjectionAudit)).all()
                    if row.id not in before_ids
                ]

        import json as _json
        selected_ids = _json.loads(new_rows[0].selected_memory_ids_json)
        assert sensitive.id not in selected_ids

    def test_flag_enabled_inactive_memory_not_selected(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        from app.services.memory_service import deactivate_memory
        with TestClient(app) as client:
            with Session(engine) as session:
                inactive = create_memory(
                    session=session,
                    memory_type="user_preference",
                    content="This memory is inactive",
                    importance=100,
                )
                deactivate_memory(session, inactive.id)
                before_ids = {
                    row.id for row in session.exec(select(MemoryInjectionAudit)).all()
                }

            client.post("/chat", json={"message": "hello", "use_memory": True})

            with Session(engine) as session:
                new_rows = [
                    row for row in session.exec(select(MemoryInjectionAudit)).all()
                    if row.id not in before_ids
                ]

        import json as _json
        selected_ids = _json.loads(new_rows[0].selected_memory_ids_json)
        assert inactive.id not in selected_ids

    def test_flag_enabled_system_event_memory_not_selected(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            with Session(engine) as session:
                sys_event = create_memory(
                    session=session,
                    memory_type="system_event",
                    content="System event should be excluded",
                    importance=100,
                )
                before_ids = {
                    row.id for row in session.exec(select(MemoryInjectionAudit)).all()
                }

            client.post("/chat", json={"message": "hello", "use_memory": True})

            with Session(engine) as session:
                new_rows = [
                    row for row in session.exec(select(MemoryInjectionAudit)).all()
                    if row.id not in before_ids
                ]

        import json as _json
        selected_ids = _json.loads(new_rows[0].selected_memory_ids_json)
        assert sys_event.id not in selected_ids

    def test_flag_enabled_response_does_not_expose_memory_fields(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello"})
        data = response.json()
        assert "memory" not in data
        assert "memory_context" not in data
        assert "selected_ids" not in data
        assert "audit" not in data
        assert "formatted_context" not in data


# ---------------------------------------------------------------------------
# TASK-023 — two-layer gate
# ---------------------------------------------------------------------------

class TestChatTwoLayerGate:
    """
    Verifies the two-layer safety model:
    Layer 1 — backend global gate: MEMORY_INJECTION_ENABLED
    Layer 2 — per-request toggle:  use_memory

    Audit rows are created ONLY when both layers are True.
    """

    def test_old_request_without_use_memory_still_returns_200(self):
        """Backward compatibility: old callers that omit use_memory still get 200."""
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello"})
        assert response.status_code == 200

    def test_use_memory_defaults_false_no_audit_when_flag_enabled(self, monkeypatch):
        """use_memory absent means False — no audit even when backend gate is open."""
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            with Session(engine) as session:
                before = len(session.exec(select(MemoryInjectionAudit)).all())
            client.post("/chat", json={"message": "hello"})  # no use_memory key
            with Session(engine) as session:
                after = len(session.exec(select(MemoryInjectionAudit)).all())
        assert after == before

    def test_flag_false_use_memory_true_returns_200(self, monkeypatch):
        monkeypatch.delenv("MEMORY_INJECTION_ENABLED", raising=False)
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello", "use_memory": True})
        assert response.status_code == 200

    def test_flag_false_use_memory_true_does_not_create_audit(self, monkeypatch):
        """Backend gate closed → no audit even if frontend requests memory."""
        monkeypatch.delenv("MEMORY_INJECTION_ENABLED", raising=False)
        with TestClient(app) as client:
            with Session(engine) as session:
                before = len(session.exec(select(MemoryInjectionAudit)).all())
            client.post("/chat", json={"message": "hello", "use_memory": True})
            with Session(engine) as session:
                after = len(session.exec(select(MemoryInjectionAudit)).all())
        assert after == before

    def test_flag_false_use_memory_true_response_schema_unchanged(self, monkeypatch):
        monkeypatch.delenv("MEMORY_INJECTION_ENABLED", raising=False)
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello", "use_memory": True})
        assert set(response.json().keys()) == {"reply", "mood", "source"}

    def test_flag_true_use_memory_false_returns_200(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello", "use_memory": False})
        assert response.status_code == 200

    def test_flag_true_use_memory_false_does_not_create_audit(self, monkeypatch):
        """Frontend toggle off → no audit even though backend gate is open."""
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            with Session(engine) as session:
                before = len(session.exec(select(MemoryInjectionAudit)).all())
            client.post("/chat", json={"message": "hello", "use_memory": False})
            with Session(engine) as session:
                after = len(session.exec(select(MemoryInjectionAudit)).all())
        assert after == before

    def test_flag_true_use_memory_false_response_schema_unchanged(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello", "use_memory": False})
        assert set(response.json().keys()) == {"reply", "mood", "source"}

    def test_both_true_creates_audit_row(self, monkeypatch):
        """Both layers True → audit row created."""
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            with Session(engine) as session:
                before = len(session.exec(select(MemoryInjectionAudit)).all())
            client.post("/chat", json={"message": "hello", "use_memory": True})
            with Session(engine) as session:
                after = len(session.exec(select(MemoryInjectionAudit)).all())
        assert after == before + 1

    def test_both_true_response_schema_unchanged(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello", "use_memory": True})
        assert set(response.json().keys()) == {"reply", "mood", "source"}

    def test_both_true_no_eligible_memory_still_returns_200(self, monkeypatch):
        """Both layers True but no eligible memories → still 200, audit row with count=0."""
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        with TestClient(app) as client:
            response = client.post(
                "/chat",
                json={"message": "unique message for empty-memory gate test", "use_memory": True},
            )
        assert response.status_code == 200

    def test_both_true_memory_content_not_in_response(self, monkeypatch):
        """Memory content must never appear in /chat response."""
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        unique = "GATE_TEST_UNIQUE_PHRASE_XYZ_9999"
        with TestClient(app) as client:
            with Session(engine) as session:
                create_memory(
                    session=session,
                    memory_type="user_preference",
                    content=unique,
                    importance=100,
                )
            response = client.post("/chat", json={"message": "hello", "use_memory": True})
        data = response.json()
        assert unique not in data.get("reply", "")
        assert unique not in data.get("mood", "")
        assert unique not in data.get("source", "")


# ---------------------------------------------------------------------------
# TASK-040 - LLM chat wiring gate
# ---------------------------------------------------------------------------

class TestChatLLMWiringGate:
    def test_llm_chat_disabled_old_format_still_returns_200(self, monkeypatch):
        monkeypatch.delenv("LLM_CHAT_ENABLED", raising=False)
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "Hello!"})

        assert response.status_code == 200

    def test_llm_chat_disabled_response_schema_remains_reply_mood_source(self, monkeypatch):
        monkeypatch.delenv("LLM_CHAT_ENABLED", raising=False)
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "Hello!"})

        assert response.status_code == 200
        assert set(response.json().keys()) == {"reply", "mood", "source"}
        assert response.json()["source"] == "mock"

    def test_llm_chat_disabled_no_llm_provider_call_occurs(self, monkeypatch):
        monkeypatch.setenv("LLM_CHAT_ENABLED", "false")

        def raise_if_called():
            raise AssertionError("LLM provider factory should not be called")

        monkeypatch.setattr("app.services.chat_service.get_llm_provider", raise_if_called)

        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "Hello!"})

        assert response.status_code == 200
        assert response.json()["source"] == "mock"

    def test_llm_chat_enabled_with_mock_provider_returns_llm_mock(self, monkeypatch):
        from app.llm.mock_provider import MockLLMProvider

        monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
        monkeypatch.setattr(
            "app.services.chat_service.get_llm_provider",
            lambda: MockLLMProvider(),
        )

        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "Hello!"})

        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == {"reply", "mood", "source"}
        assert data["source"] == "llm_mock"
        assert "memory" not in data
        assert "memory_context" not in data

    def test_llm_chat_enabled_real_provider_mocked_returns_llm_real(self, monkeypatch):
        from app.llm.types import LLMResponse

        fake_key = "sk-test-route-secret"
        raw_body = "RAW_PROVIDER_BODY_SHOULD_NOT_APPEAR"

        class FakeRealProvider:
            provider_name = "anthropic"

            def generate(self, request):
                assert request.memory_context is None
                return LLMResponse(
                    text="real provider route reply",
                    provider="anthropic",
                    model="claude-test",
                    usage={"input_tokens": 1},
                    error=None,
                )

        monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
        monkeypatch.setattr(
            "app.services.chat_service.get_llm_provider",
            lambda: FakeRealProvider(),
        )

        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "Hello!"})

        data = response.json()
        observed = repr(data)
        assert response.status_code == 200
        assert set(data.keys()) == {"reply", "mood", "source"}
        assert data["source"] == "llm_real"
        assert fake_key not in observed
        assert raw_body not in observed

    def test_llm_chat_enabled_does_not_use_memory_without_memory_gates(self, monkeypatch):
        monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
        monkeypatch.delenv("MEMORY_INJECTION_ENABLED", raising=False)

        def raise_if_memory_builder_called(session):  # noqa: ARG001
            raise AssertionError("memory builder should not be called")

        monkeypatch.setattr(
            "app.api.routes.build_approved_memory_context_records",
            raise_if_memory_builder_called,
        )

        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "Hello!"})

        assert response.status_code == 200

    def test_memory_enabled_does_not_use_llm_when_llm_chat_disabled(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        monkeypatch.setenv("LLM_CHAT_ENABLED", "false")

        def raise_if_called():
            raise AssertionError("LLM provider factory should not be called")

        monkeypatch.setattr("app.services.chat_service.get_llm_provider", raise_if_called)

        with TestClient(app) as client:
            response = client.post(
                "/chat",
                json={"message": "Hello!", "use_memory": True},
            )

        assert response.status_code == 200
        assert response.json()["source"] == "mock"

    def test_memory_audit_remains_memory_scoped_with_llm_enabled(self, monkeypatch):
        from app.llm.types import LLMResponse

        class FakeRealProvider:
            provider_name = "anthropic"

            def generate(self, request):
                return LLMResponse(
                    text="real provider route reply",
                    provider="anthropic",
                    error=None,
                )

        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
        monkeypatch.setattr(
            "app.services.chat_service.get_llm_provider",
            lambda: FakeRealProvider(),
        )

        with TestClient(app) as client:
            with Session(engine) as session:
                before_ids = {
                    row.id for row in session.exec(select(MemoryInjectionAudit)).all()
                }

            response = client.post(
                "/chat",
                json={"message": "Hello!", "use_memory": True},
            )

            with Session(engine) as session:
                new_rows = [
                    row for row in session.exec(select(MemoryInjectionAudit)).all()
                    if row.id not in before_ids
                ]

        assert response.status_code == 200
        assert len(new_rows) == 1
        audit_text = (new_rows[0].selected_memory_ids_json or "") + (
            new_rows[0].exclusion_summary_json or ""
        )
        assert "anthropic" not in audit_text
        assert "real provider route reply" not in audit_text
