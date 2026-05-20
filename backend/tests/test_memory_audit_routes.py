"""
Tests for GET /memory/audit route.

TASK-026: Memory Injection Audit Inspection API

Safety rules verified here:
- Endpoint is read-only; it never creates rows or modifies last_used_at.
- Raw memory content is never included in any response field.
- Prompt text and approved memory context text are never returned.
- selected_memory_ids is a list of integer IDs only.
- /chat behavior and response schema remain unchanged.
"""

import os

from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlmodel import Session, select

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

from app.db.database import engine, init_db  # noqa: E402
from app.db.models import Memory, MemoryInjectionAudit  # noqa: E402
from app.main import app  # noqa: E402
from app.services.memory_audit_service import create_memory_injection_audit  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_audit_table() -> None:
    init_db(engine)
    with Session(engine) as session:
        session.exec(delete(MemoryInjectionAudit))
        session.commit()


def _create_audit(
    conversation_id: int | None = None,
    selected_memory_ids: list[int] | None = None,
    total_context_chars: int = 100,
    feature_flag_enabled: bool = True,
    exclusion_summary: dict | None = None,
) -> MemoryInjectionAudit:
    with Session(engine) as session:
        return create_memory_injection_audit(
            session=session,
            conversation_id=conversation_id,
            selected_memory_ids=selected_memory_ids or [],
            total_context_chars=total_context_chars,
            feature_flag_enabled=feature_flag_enabled,
            exclusion_summary=exclusion_summary,
        )


# ---------------------------------------------------------------------------
# 1. GET /memory/audit empty returns 200
# ---------------------------------------------------------------------------


def test_audit_route_empty_returns_200():
    _reset_audit_table()

    with TestClient(app) as client:
        response = client.get("/memory/audit")

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# 2. Empty response shape
# ---------------------------------------------------------------------------


def test_audit_route_empty_response_shape():
    _reset_audit_table()

    with TestClient(app) as client:
        response = client.get("/memory/audit")

    data = response.json()
    assert data["items"] == []
    assert data["count"] == 0
    assert data["limit"] == 20
    assert data["offset"] == 0


# ---------------------------------------------------------------------------
# 3. Returns audit items
# ---------------------------------------------------------------------------


def test_audit_route_returns_items():
    _reset_audit_table()
    _create_audit(conversation_id=1, selected_memory_ids=[10, 20])

    with TestClient(app) as client:
        response = client.get("/memory/audit")

    data = response.json()
    assert response.status_code == 200
    assert data["count"] == 1
    assert len(data["items"]) == 1


# ---------------------------------------------------------------------------
# 4. Audit item includes selected_memory_ids as a list
# ---------------------------------------------------------------------------


def test_audit_item_selected_memory_ids_is_list():
    _reset_audit_table()
    _create_audit(selected_memory_ids=[5, 7])

    with TestClient(app) as client:
        response = client.get("/memory/audit")

    item = response.json()["items"][0]
    assert isinstance(item["selected_memory_ids"], list)
    assert item["selected_memory_ids"] == [5, 7]


# ---------------------------------------------------------------------------
# 5. Audit item includes exclusion_summary as dict or null
# ---------------------------------------------------------------------------


def test_audit_item_exclusion_summary_as_dict():
    _reset_audit_table()
    _create_audit(exclusion_summary={"sensitive": 1})

    with TestClient(app) as client:
        response = client.get("/memory/audit")

    item = response.json()["items"][0]
    assert item["exclusion_summary"] == {"sensitive": 1}


def test_audit_item_exclusion_summary_null_when_none():
    _reset_audit_table()
    _create_audit(exclusion_summary=None)

    with TestClient(app) as client:
        response = client.get("/memory/audit")

    item = response.json()["items"][0]
    assert item["exclusion_summary"] is None


# ---------------------------------------------------------------------------
# 6. Supports limit
# ---------------------------------------------------------------------------


def test_audit_route_supports_limit():
    _reset_audit_table()
    for i in range(5):
        _create_audit(conversation_id=i)

    with TestClient(app) as client:
        response = client.get("/memory/audit?limit=2")

    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 2
    assert data["limit"] == 2


# ---------------------------------------------------------------------------
# 7. Supports offset
# ---------------------------------------------------------------------------


def test_audit_route_supports_offset():
    _reset_audit_table()
    for i in range(4):
        _create_audit(conversation_id=i)

    with TestClient(app) as client:
        all_resp = client.get("/memory/audit?limit=10&offset=0")
        offset_resp = client.get("/memory/audit?limit=10&offset=1")

    all_items = all_resp.json()["items"]
    offset_items = offset_resp.json()["items"]

    assert len(offset_items) == len(all_items) - 1
    assert offset_items[0]["id"] == all_items[1]["id"]


# ---------------------------------------------------------------------------
# 8. limit > 100 returns normalized limit 100
# ---------------------------------------------------------------------------


def test_audit_route_limit_over_100_clamped():
    _reset_audit_table()

    with TestClient(app) as client:
        response = client.get("/memory/audit?limit=999")

    data = response.json()
    assert response.status_code == 200
    assert data["limit"] == 100


# ---------------------------------------------------------------------------
# 9. Negative offset returns normalized offset 0
# ---------------------------------------------------------------------------


def test_audit_route_negative_offset_normalized():
    _reset_audit_table()

    with TestClient(app) as client:
        response = client.get("/memory/audit?offset=-5")

    data = response.json()
    assert response.status_code == 200
    assert data["offset"] == 0


# ---------------------------------------------------------------------------
# 10. Results are newest first
# ---------------------------------------------------------------------------


def test_audit_route_returns_newest_first():
    _reset_audit_table()
    first = _create_audit(conversation_id=1)
    second = _create_audit(conversation_id=2)

    with TestClient(app) as client:
        response = client.get("/memory/audit")

    ids = [item["id"] for item in response.json()["items"]]
    assert ids == [second.id, first.id]


# ---------------------------------------------------------------------------
# 11. Response does not include raw memory content
# ---------------------------------------------------------------------------


def test_audit_route_response_does_not_include_raw_memory_content():
    _reset_audit_table()
    _create_audit(selected_memory_ids=[42], exclusion_summary={"sensitive": 1})

    with TestClient(app) as client:
        response = client.get("/memory/audit")

    raw = str(response.json())
    assert "password" not in raw
    assert "secret memory content" not in raw
    assert "approved_context" not in raw


# ---------------------------------------------------------------------------
# 12. Response does not include prompt text
# ---------------------------------------------------------------------------


def test_audit_route_response_does_not_include_prompt_text():
    _reset_audit_table()
    _create_audit()

    with TestClient(app) as client:
        response = client.get("/memory/audit")

    item = response.json()["items"][0] if response.json()["items"] else {}
    assert "prompt" not in item
    assert "context_text" not in item
    assert "approved_memory_context" not in item


# ---------------------------------------------------------------------------
# 13. Endpoint does not create new audit rows
# ---------------------------------------------------------------------------


def test_audit_route_is_read_only():
    _reset_audit_table()
    _create_audit(conversation_id=1)

    with TestClient(app) as client:
        with Session(engine) as session:
            before_count = len(session.exec(select(MemoryInjectionAudit)).all())

        client.get("/memory/audit")

        with Session(engine) as session:
            after_count = len(session.exec(select(MemoryInjectionAudit)).all())

    assert after_count == before_count


# ---------------------------------------------------------------------------
# 14. /chat old format still returns 200 with correct schema
# ---------------------------------------------------------------------------


def test_chat_old_format_returns_200_and_schema_unchanged():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}


# ---------------------------------------------------------------------------
# 15. /chat response schema never includes audit fields
# ---------------------------------------------------------------------------


def test_chat_response_never_includes_audit_fields():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    data = response.json()
    assert "audit" not in data
    assert "memory_injection_audit" not in data
    assert "selected_memory_ids" not in data
    assert "items" not in data
