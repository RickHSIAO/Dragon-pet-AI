import os

from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, select

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

from app.db.database import create_db_engine, engine, init_db  # noqa: E402
from app.db.models import Memory  # noqa: E402
from app.main import app  # noqa: E402
from app.services.memory_service import (  # noqa: E402
    MAX_APPROVED_MEMORIES,
    MAX_MEMORY_CONTEXT_CHARS,
    build_approved_memory_context_entries,
    build_approved_memory_context_records,
    build_approved_memory_context_text,
    build_memory_context_preview,
    contains_obvious_sensitive_content,
    create_memory,
    deactivate_memory,
    is_memory_eligible_for_injection,
    list_active_memories,
)


def make_test_engine():
    test_engine = create_db_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)
    return test_engine


def test_create_memory_creates_active_memory():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="user_preference",
            content="Likes concise answers",
            source="manual",
        )

        assert memory.id is not None
        assert memory.is_active is True
        assert memory.memory_type == "user_preference"
        assert memory.content == "Likes concise answers"
        assert memory.importance == 50
        assert memory.confidence == "explicit"
        assert memory.source == "manual"
        assert memory.created_at is not None
        assert memory.updated_at is not None


def test_create_memory_strips_content():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="project_context",
            content="  Keep backend mock-only  ",
        )

        assert memory.content == "Keep backend mock-only"


def test_create_memory_rejects_blank_content():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        try:
            create_memory(
                session=session,
                memory_type="task_memory",
                content="   ",
            )
        except ValueError as exc:
            assert "content" in str(exc)
        else:
            raise AssertionError("Expected blank memory content to raise ValueError")


def test_create_memory_clamps_importance_below_zero_to_zero():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="task_memory",
            content="Low bound",
            importance=-10,
        )

        assert memory.importance == 0


def test_create_memory_clamps_importance_above_one_hundred_to_one_hundred():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="task_memory",
            content="High bound",
            importance=150,
        )

        assert memory.importance == 100


def test_list_active_memories_returns_only_active_memories():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        active = create_memory(
            session=session,
            memory_type="character_note",
            content="Active note",
        )
        inactive = create_memory(
            session=session,
            memory_type="character_note",
            content="Inactive note",
        )
        deactivate_memory(session, inactive.id)

        memories = list_active_memories(session)

        assert [memory.id for memory in memories] == [active.id]


def test_deactivate_memory_marks_memory_inactive():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="system_event",
            content="Created skeleton",
        )

        deactivated = deactivate_memory(session, memory.id)

        assert deactivated is not None
        assert deactivated.id == memory.id
        assert deactivated.is_active is False


def test_deactivate_memory_returns_none_for_missing_id():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        assert deactivate_memory(session, 9999) is None


def test_build_memory_context_preview_returns_empty_context():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        preview = build_memory_context_preview(session)

        assert preview["memories"] == []
        assert preview["count"] == 0
        assert preview["source"] == "manual_memory_preview"
        assert "No active memories." in preview["context_text"]


def test_build_memory_context_preview_orders_by_importance_then_id():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        first_equal = create_memory(
            session=session,
            memory_type="project_context",
            content="First equal priority",
            importance=70,
        )
        high = create_memory(
            session=session,
            memory_type="user_preference",
            content="Highest priority",
            importance=90,
        )
        second_equal = create_memory(
            session=session,
            memory_type="task_memory",
            content="Second equal priority",
            importance=70,
        )

        preview = build_memory_context_preview(session)

        assert [memory.id for memory in preview["memories"]] == [
            high.id,
            first_equal.id,
            second_equal.id,
        ]


def test_build_memory_context_preview_does_not_update_last_used_at():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="user_preference",
            content="Do not mark preview as use",
        )

        preview = build_memory_context_preview(session)
        refreshed_memory = session.get(Memory, memory.id)

        assert preview["count"] == 1
        assert refreshed_memory.last_used_at is None


def test_inactive_memory_is_excluded_from_approved_context():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="user_preference",
            content="Inactive preference",
        )
        deactivate_memory(session, memory.id)

        assert build_approved_memory_context_entries(session) == []


def test_system_event_memory_is_excluded_from_approved_context():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="system_event",
            content="System event should not inject",
        )

        assert is_memory_eligible_for_injection(memory) is False


def test_user_preference_explicit_memory_is_eligible():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="user_preference",
            content="Use Traditional Chinese",
        )

        assert is_memory_eligible_for_injection(memory) is True


def test_project_context_explicit_memory_is_eligible():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="project_context",
            content="Project is TASK-018",
        )

        assert is_memory_eligible_for_injection(memory) is True


def test_task_memory_explicit_memory_is_eligible():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="task_memory",
            content="Next task is audit log",
        )

        assert is_memory_eligible_for_injection(memory) is True


def test_character_note_explicit_memory_is_eligible():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="character_note",
            content="Be concise in technical mode",
        )

        assert is_memory_eligible_for_injection(memory) is True


def test_inferred_memory_is_excluded_from_approved_context():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        create_memory(
            session=session,
            memory_type="user_preference",
            content="Inferred preference",
            confidence="inferred",
        )

        assert build_approved_memory_context_entries(session) == []


def test_temporary_memory_is_excluded_from_approved_context():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        create_memory(
            session=session,
            memory_type="project_context",
            content="Temporary context",
            confidence="temporary",
        )

        assert build_approved_memory_context_entries(session) == []


def test_stale_memory_is_excluded_from_approved_context():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        create_memory(
            session=session,
            memory_type="task_memory",
            content="Stale context",
            confidence="stale",
        )

        assert build_approved_memory_context_entries(session) == []


def test_unknown_confidence_memory_is_excluded_from_approved_context():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        create_memory(
            session=session,
            memory_type="character_note",
            content="Unknown confidence",
            confidence="unknown",
        )

        assert build_approved_memory_context_entries(session) == []


def test_user_corrected_sorts_before_explicit():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        create_memory(
            session=session,
            memory_type="user_preference",
            content="Explicit memory",
            importance=100,
            confidence="explicit",
        )
        create_memory(
            session=session,
            memory_type="user_preference",
            content="Corrected memory",
            importance=1,
            confidence="user_corrected",
        )

        assert build_approved_memory_context_entries(session) == [
            "Corrected memory",
            "Explicit memory",
        ]


def test_higher_importance_sorts_before_lower_importance_within_confidence():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        create_memory(
            session=session,
            memory_type="user_preference",
            content="Low importance",
            importance=10,
        )
        create_memory(
            session=session,
            memory_type="user_preference",
            content="High importance",
            importance=90,
        )

        assert build_approved_memory_context_entries(session) == [
            "High importance",
            "Low importance",
        ]


def test_memory_type_priority_is_deterministic():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        create_memory(session, "character_note", "Character note", importance=50)
        create_memory(session, "task_memory", "Task memory", importance=50)
        create_memory(session, "project_context", "Project context", importance=50)
        create_memory(session, "user_preference", "User preference", importance=50)

        assert build_approved_memory_context_entries(session) == [
            "User preference",
            "Project context",
            "Task memory",
            "Character note",
        ]


def test_id_ascending_tie_breaker_works():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        first = create_memory(session, "user_preference", "First tied", importance=50)
        second = create_memory(session, "user_preference", "Second tied", importance=50)

        assert first.id < second.id
        assert build_approved_memory_context_entries(session) == [
            "First tied",
            "Second tied",
        ]


def test_max_included_memories_is_five():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        for index in range(7):
            create_memory(
                session=session,
                memory_type="user_preference",
                content=f"Memory {index}",
                importance=50,
            )

        entries = build_approved_memory_context_entries(session)

        assert len(entries) == MAX_APPROVED_MEMORIES
        assert entries == ["Memory 0", "Memory 1", "Memory 2", "Memory 3", "Memory 4"]


def test_sensitive_keyword_password_is_excluded():
    assert contains_obvious_sensitive_content("my password is secret") is True


def test_api_key_and_sk_pattern_are_excluded():
    assert contains_obvious_sensitive_content("api key sk-test123456") is True


def test_private_key_and_ssh_rsa_pattern_are_excluded():
    assert contains_obvious_sensitive_content("private key starts ssh-rsa AAA") is True


def test_credit_card_like_number_is_excluded():
    assert contains_obvious_sensitive_content("card 4111-1111-1111-1111") is True


def test_identity_document_keywords_are_excluded():
    assert contains_obvious_sensitive_content("passport number was shared") is True
    assert contains_obvious_sensitive_content("身分證資料") is True


def test_sensitive_memory_is_excluded_from_approved_context():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        create_memory(
            session=session,
            memory_type="user_preference",
            content="My password is secret",
        )

        assert build_approved_memory_context_entries(session) == []


def test_build_approved_memory_context_text_does_not_exceed_limit():
    test_engine = make_test_engine()
    long_entry = "A" * MAX_MEMORY_CONTEXT_CHARS

    with Session(test_engine) as session:
        create_memory(session, "user_preference", long_entry, importance=100)
        create_memory(session, "user_preference", "extra entry", importance=90)

        context_text = build_approved_memory_context_text(session)

        assert len(context_text) <= MAX_MEMORY_CONTEXT_CHARS
        assert context_text == long_entry
        assert "extra entry" not in context_text


def test_build_approved_memory_context_text_does_not_update_last_used_at():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="user_preference",
            content="Do not update usage",
        )

        context_text = build_approved_memory_context_text(session)
        refreshed_memory = session.get(Memory, memory.id)

        assert context_text == "Do not update usage"
        assert refreshed_memory.last_used_at is None


def test_approved_context_entries_do_not_contain_raw_metadata_labels():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="user_preference",
            content="Plain approved content",
            importance=80,
            confidence="user_corrected",
        )

        entries = build_approved_memory_context_entries(session)

        assert entries == ["Plain approved content"]
        assert f"id={memory.id}" not in entries[0]
        assert "importance" not in entries[0]
        assert "confidence" not in entries[0]


def test_init_db_can_create_memory_table():
    test_engine = create_db_engine("sqlite:///:memory:")

    init_db(test_engine)

    table_names = inspect(test_engine).get_table_names()
    assert "memory" in table_names


# ---------------------------------------------------------------------------
# TASK-020: build_approved_memory_context_records
# ---------------------------------------------------------------------------

def test_build_approved_memory_context_records_returns_memory_objects():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        memory = create_memory(
            session=session,
            memory_type="user_preference",
            content="Returns Memory objects not strings",
        )

        records = build_approved_memory_context_records(session)

        assert len(records) == 1
        assert records[0].id == memory.id
        assert records[0].content == "Returns Memory objects not strings"


def test_build_approved_memory_context_records_returns_empty_list_when_no_eligible():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        create_memory(
            session=session,
            memory_type="system_event",
            content="Should not appear",
        )

        records = build_approved_memory_context_records(session)

        assert records == []


def test_build_approved_memory_context_records_ids_match_entries_content():
    """IDs from records must correspond to the same content returned by entries."""
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        m1 = create_memory(session, "user_preference", "Alpha", importance=90)
        m2 = create_memory(session, "project_context", "Beta", importance=80)

        records = build_approved_memory_context_records(session)
        entries = build_approved_memory_context_entries(session)

        assert [r.id for r in records] == [m1.id, m2.id]
        assert entries == ["Alpha", "Beta"]


def test_build_approved_memory_context_records_cap_is_five():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        for i in range(7):
            create_memory(session, "user_preference", f"Record {i}", importance=50)

        records = build_approved_memory_context_records(session)

        assert len(records) == MAX_APPROVED_MEMORIES


def test_build_approved_memory_context_records_excludes_inactive():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        m = create_memory(session, "user_preference", "Will be deactivated", importance=100)
        deactivate_memory(session, m.id)

        records = build_approved_memory_context_records(session)

        assert all(r.id != m.id for r in records)


def test_build_approved_memory_context_records_excludes_sensitive():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        create_memory(session, "user_preference", "password is abc123", importance=100)

        records = build_approved_memory_context_records(session)

        assert records == []


def test_build_approved_memory_context_records_have_valid_ids():
    """All returned records must have non-None IDs for safe audit serialization."""
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        create_memory(session, "user_preference", "Valid id check", importance=50)

        records = build_approved_memory_context_records(session)

        for record in records:
            assert record.id is not None


def test_chat_still_returns_200_for_old_format():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}


def test_chat_response_does_not_include_memory_fields():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    data = response.json()
    assert response.status_code == 200
    assert set(data.keys()) == {"reply", "mood", "source"}
    assert "memory" not in data
    assert "memories" not in data
    assert "memory_context" not in data


def test_chat_does_not_create_memory_records():
    with TestClient(app) as client:
        with Session(engine) as session:
            before_count = len(session.exec(select(Memory)).all())

        response = client.post("/chat", json={"message": "Hello!"})

        with Session(engine) as session:
            after_count = len(session.exec(select(Memory)).all())

    assert response.status_code == 200
    assert after_count == before_count
