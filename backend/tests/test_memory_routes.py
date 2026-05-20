import os

from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlmodel import Session, select

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

from app.db.database import engine, init_db  # noqa: E402
from app.db.models import Memory  # noqa: E402
from app.main import app  # noqa: E402


def clear_memory_records() -> None:
    init_db(engine)
    with Session(engine) as session:
        session.exec(delete(Memory))
        session.commit()


def test_post_memory_creates_memory():
    clear_memory_records()

    with TestClient(app) as client:
        response = client.post(
            "/memory",
            json={
                "memory_type": "user_preference",
                "content": "Likes concise answers",
            },
        )

    data = response.json()
    assert response.status_code == 200
    assert data["id"] is not None
    assert data["memory_type"] == "user_preference"
    assert data["content"] == "Likes concise answers"
    assert data["importance"] == 50
    assert data["confidence"] == "explicit"
    assert data["source"] == "manual"
    assert data["is_active"] is True


def test_post_memory_strips_content():
    clear_memory_records()

    with TestClient(app) as client:
        response = client.post(
            "/memory",
            json={
                "memory_type": "project_context",
                "content": "  Keep memory manual-only  ",
            },
        )

    assert response.status_code == 200
    assert response.json()["content"] == "Keep memory manual-only"


def test_post_memory_rejects_blank_content():
    clear_memory_records()

    with TestClient(app) as client:
        response = client.post(
            "/memory",
            json={
                "memory_type": "task_memory",
                "content": "   ",
            },
        )

    assert response.status_code == 400
    with Session(engine) as session:
        assert session.exec(select(Memory)).all() == []


def test_post_memory_clamps_importance_below_zero_to_zero():
    clear_memory_records()

    with TestClient(app) as client:
        response = client.post(
            "/memory",
            json={
                "memory_type": "task_memory",
                "content": "Low bound",
                "importance": -5,
            },
        )

    assert response.status_code == 200
    assert response.json()["importance"] == 0


def test_post_memory_clamps_importance_above_one_hundred_to_one_hundred():
    clear_memory_records()

    with TestClient(app) as client:
        response = client.post(
            "/memory",
            json={
                "memory_type": "task_memory",
                "content": "High bound",
                "importance": 120,
            },
        )

    assert response.status_code == 200
    assert response.json()["importance"] == 100


def test_get_memory_returns_only_active_memories():
    clear_memory_records()

    with TestClient(app) as client:
        active_response = client.post(
            "/memory",
            json={
                "memory_type": "character_note",
                "content": "Active note",
            },
        )
        inactive_response = client.post(
            "/memory",
            json={
                "memory_type": "character_note",
                "content": "Inactive note",
            },
        )
        inactive_id = inactive_response.json()["id"]
        client.delete(f"/memory/{inactive_id}")

        response = client.get("/memory")

    active_id = active_response.json()["id"]
    data = response.json()
    assert response.status_code == 200
    assert [memory["id"] for memory in data] == [active_id]
    assert all(memory["is_active"] is True for memory in data)


def test_delete_memory_deactivates_memory():
    clear_memory_records()

    with TestClient(app) as client:
        create_response = client.post(
            "/memory",
            json={
                "memory_type": "system_event",
                "content": "Manual memory API added",
            },
        )
        memory_id = create_response.json()["id"]

        response = client.delete(f"/memory/{memory_id}")

    data = response.json()
    assert response.status_code == 200
    assert data["id"] == memory_id
    assert data["is_active"] is False

    with Session(engine) as session:
        stored_memory = session.get(Memory, memory_id)
        assert stored_memory is not None
        assert stored_memory.is_active is False


def test_delete_memory_missing_id_returns_404():
    clear_memory_records()

    with TestClient(app) as client:
        response = client.delete("/memory/9999")

    assert response.status_code == 404


def test_get_memory_context_preview_returns_200():
    clear_memory_records()

    with TestClient(app) as client:
        response = client.get("/memory/context-preview")

    assert response.status_code == 200


def test_empty_memory_context_preview_returns_count_zero_and_source():
    clear_memory_records()

    with TestClient(app) as client:
        response = client.get("/memory/context-preview")

    data = response.json()
    assert response.status_code == 200
    assert data["memories"] == []
    assert data["count"] == 0
    assert data["source"] == "manual_memory_preview"
    assert "No active memories." in data["context_text"]


def test_active_memories_appear_in_context_preview_text():
    clear_memory_records()

    with TestClient(app) as client:
        client.post(
            "/memory",
            json={
                "memory_type": "user_preference",
                "content": "User prefers Traditional Chinese.",
                "importance": 80,
            },
        )

        response = client.get("/memory/context-preview")

    data = response.json()
    assert response.status_code == 200
    assert data["count"] == 1
    assert "User prefers Traditional Chinese." in data["context_text"]
    assert "[user_preference][importance=80][confidence=explicit]" in data["context_text"]


def test_inactive_memories_do_not_appear_in_context_preview_text():
    clear_memory_records()

    with TestClient(app) as client:
        active_response = client.post(
            "/memory",
            json={
                "memory_type": "project_context",
                "content": "Active project context",
                "importance": 70,
            },
        )
        inactive_response = client.post(
            "/memory",
            json={
                "memory_type": "project_context",
                "content": "Inactive project context",
                "importance": 100,
            },
        )
        client.delete(f"/memory/{inactive_response.json()['id']}")

        response = client.get("/memory/context-preview")

    data = response.json()
    assert response.status_code == 200
    assert [memory["id"] for memory in data["memories"]] == [active_response.json()["id"]]
    assert "Active project context" in data["context_text"]
    assert "Inactive project context" not in data["context_text"]


def test_memory_context_preview_ordering_is_deterministic():
    clear_memory_records()

    with TestClient(app) as client:
        first_equal = client.post(
            "/memory",
            json={
                "memory_type": "project_context",
                "content": "First equal priority",
                "importance": 70,
            },
        ).json()
        high = client.post(
            "/memory",
            json={
                "memory_type": "user_preference",
                "content": "Highest priority",
                "importance": 90,
            },
        ).json()
        second_equal = client.post(
            "/memory",
            json={
                "memory_type": "task_memory",
                "content": "Second equal priority",
                "importance": 70,
            },
        ).json()

        response = client.get("/memory/context-preview")

    data = response.json()
    assert response.status_code == 200
    assert [memory["id"] for memory in data["memories"]] == [
        high["id"],
        first_equal["id"],
        second_equal["id"],
    ]
    assert data["context_text"].index("Highest priority") < data["context_text"].index(
        "First equal priority"
    )
    assert data["context_text"].index("First equal priority") < data["context_text"].index(
        "Second equal priority"
    )


def test_memory_context_preview_does_not_update_last_used_at():
    clear_memory_records()

    with TestClient(app) as client:
        create_response = client.post(
            "/memory",
            json={
                "memory_type": "user_preference",
                "content": "Preview is not usage",
            },
        )
        memory_id = create_response.json()["id"]

        response = client.get("/memory/context-preview")

    assert response.status_code == 200
    with Session(engine) as session:
        memory = session.get(Memory, memory_id)
        assert memory is not None
        assert memory.last_used_at is None


def test_chat_old_format_still_returns_200():
    clear_memory_records()

    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}


def test_chat_response_does_not_include_memory_fields():
    clear_memory_records()

    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    data = response.json()
    assert response.status_code == 200
    assert set(data.keys()) == {"reply", "mood", "source"}
    assert "memory" not in data
    assert "memories" not in data
    assert "memory_context" not in data


def test_chat_does_not_create_memory_automatically():
    clear_memory_records()

    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    with Session(engine) as session:
        assert session.exec(select(Memory)).all() == []


def test_chat_does_not_consume_memory_context_preview():
    clear_memory_records()

    with TestClient(app) as client:
        create_response = client.post(
            "/memory",
            json={
                "memory_type": "user_preference",
                "content": "Unique preview-only memory phrase",
                "importance": 100,
            },
        )
        memory_id = create_response.json()["id"]
        preview_response = client.get("/memory/context-preview")

        chat_response = client.post("/chat", json={"message": "Hello!"})

    chat_data = chat_response.json()
    assert preview_response.status_code == 200
    assert "Unique preview-only memory phrase" in preview_response.json()["context_text"]
    assert chat_response.status_code == 200
    assert set(chat_data.keys()) == {"reply", "mood", "source"}
    assert "Unique preview-only memory phrase" not in chat_data["reply"]
    with Session(engine) as session:
        memory = session.get(Memory, memory_id)
        assert memory is not None
        assert memory.last_used_at is None
