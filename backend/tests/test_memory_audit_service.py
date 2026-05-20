import os

from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, select

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

from app.db.database import create_db_engine, engine, init_db  # noqa: E402
from app.db.models import MemoryInjectionAudit  # noqa: E402
from app.main import app  # noqa: E402
from app.services.memory_audit_service import (  # noqa: E402
    create_memory_injection_audit,
    list_memory_injection_audits,
    list_memory_injection_audits_paginated,
    normalize_audit_pagination,
    parse_exclusion_summary_json,
    parse_memory_ids_json,
    serialize_exclusion_summary,
    serialize_memory_ids,
)


def make_test_engine():
    test_engine = create_db_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)
    return test_engine


def test_serialize_memory_ids_returns_deterministic_json():
    assert serialize_memory_ids([3, 1, 2]) == "[3,1,2]"


def test_serialize_exclusion_summary_returns_deterministic_json():
    summary = {"sensitive": 2, "inactive": 1}

    assert serialize_exclusion_summary(summary) == '{"inactive":1,"sensitive":2}'


def test_serialize_exclusion_summary_none_returns_none():
    assert serialize_exclusion_summary(None) is None


def test_create_memory_injection_audit_creates_audit_row():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        audit = create_memory_injection_audit(
            session=session,
            conversation_id=7,
            selected_memory_ids=[1, 2],
            total_context_chars=120,
            feature_flag_enabled=True,
            exclusion_summary={"sensitive": 1},
        )

        assert audit.id is not None
        assert audit.conversation_id == 7
        assert audit.selected_memory_ids_json == "[1,2]"
        assert audit.selected_count == 2
        assert audit.total_context_chars == 120


def test_selected_count_equals_len_selected_memory_ids():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        audit = create_memory_injection_audit(
            session=session,
            conversation_id=None,
            selected_memory_ids=[10, 11, 12],
            total_context_chars=20,
            feature_flag_enabled=False,
        )

        assert audit.selected_count == 3


def test_total_context_chars_below_zero_clamps_to_zero():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        audit = create_memory_injection_audit(
            session=session,
            conversation_id=None,
            selected_memory_ids=[],
            total_context_chars=-5,
            feature_flag_enabled=False,
        )

        assert audit.total_context_chars == 0


def test_audit_row_stores_feature_flag_enabled():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        audit = create_memory_injection_audit(
            session=session,
            conversation_id=None,
            selected_memory_ids=[],
            total_context_chars=0,
            feature_flag_enabled=True,
        )

        assert audit.feature_flag_enabled is True


def test_audit_row_stores_exclusion_summary_json():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        audit = create_memory_injection_audit(
            session=session,
            conversation_id=None,
            selected_memory_ids=[],
            total_context_chars=0,
            feature_flag_enabled=False,
            exclusion_summary={"inactive": 1, "sensitive": 2},
        )

        assert audit.exclusion_summary_json == '{"inactive":1,"sensitive":2}'


def test_audit_row_does_not_store_raw_memory_content():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        audit = create_memory_injection_audit(
            session=session,
            conversation_id=None,
            selected_memory_ids=[42],
            total_context_chars=33,
            feature_flag_enabled=False,
            exclusion_summary={"sensitive": 1},
        )

        row_text = (
            audit.selected_memory_ids_json
            + str(audit.exclusion_summary_json)
            + str(audit.conversation_id)
        )
        assert "password" not in row_text
        assert "secret memory content" not in row_text


def test_list_memory_injection_audits_returns_events_deterministically():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        first = create_memory_injection_audit(
            session=session,
            conversation_id=1,
            selected_memory_ids=[1],
            total_context_chars=10,
            feature_flag_enabled=False,
        )
        second = create_memory_injection_audit(
            session=session,
            conversation_id=2,
            selected_memory_ids=[2],
            total_context_chars=20,
            feature_flag_enabled=True,
        )

        audits = list_memory_injection_audits(session)

        assert [audit.id for audit in audits] == [first.id, second.id]


# ---------------------------------------------------------------------------
# parse_memory_ids_json
# ---------------------------------------------------------------------------


def test_parse_memory_ids_json_valid_list():
    assert parse_memory_ids_json("[1,2,3]") == [1, 2, 3]


def test_parse_memory_ids_json_empty_string_returns_empty():
    assert parse_memory_ids_json("") == []


def test_parse_memory_ids_json_invalid_json_returns_empty():
    assert parse_memory_ids_json("not-json") == []


def test_parse_memory_ids_json_non_list_returns_empty():
    assert parse_memory_ids_json('{"a": 1}') == []


def test_parse_memory_ids_json_filters_non_int_values():
    assert parse_memory_ids_json('[1, "two", 3, null, 4.5]') == [1, 3]


# ---------------------------------------------------------------------------
# parse_exclusion_summary_json
# ---------------------------------------------------------------------------


def test_parse_exclusion_summary_json_valid_dict():
    assert parse_exclusion_summary_json('{"sensitive":2,"inactive":1}') == {
        "sensitive": 2,
        "inactive": 1,
    }


def test_parse_exclusion_summary_json_none_returns_none():
    assert parse_exclusion_summary_json(None) is None


def test_parse_exclusion_summary_json_invalid_json_returns_none():
    assert parse_exclusion_summary_json("not-json") is None


def test_parse_exclusion_summary_json_non_dict_returns_none():
    assert parse_exclusion_summary_json("[1,2,3]") is None


# ---------------------------------------------------------------------------
# normalize_audit_pagination
# ---------------------------------------------------------------------------


def test_normalize_audit_pagination_defaults():
    assert normalize_audit_pagination(None, None) == (20, 0)


def test_normalize_audit_pagination_clamps_limit_max_100():
    assert normalize_audit_pagination(200, 0) == (100, 0)


def test_normalize_audit_pagination_limit_zero_falls_back():
    assert normalize_audit_pagination(0, 0) == (20, 0)


def test_normalize_audit_pagination_limit_negative_falls_back():
    assert normalize_audit_pagination(-5, 0) == (20, 0)


def test_normalize_audit_pagination_negative_offset_falls_back():
    assert normalize_audit_pagination(10, -1) == (10, 0)


# ---------------------------------------------------------------------------
# list_memory_injection_audits_paginated
# ---------------------------------------------------------------------------


def test_paginated_list_returns_newest_first():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        first = create_memory_injection_audit(
            session=session,
            conversation_id=1,
            selected_memory_ids=[1],
            total_context_chars=10,
            feature_flag_enabled=False,
        )
        second = create_memory_injection_audit(
            session=session,
            conversation_id=2,
            selected_memory_ids=[2],
            total_context_chars=20,
            feature_flag_enabled=True,
        )

        audits = list_memory_injection_audits_paginated(session)

        assert [a.id for a in audits] == [second.id, first.id]


def test_paginated_list_respects_limit():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        for i in range(5):
            create_memory_injection_audit(
                session=session,
                conversation_id=i,
                selected_memory_ids=[i],
                total_context_chars=10,
                feature_flag_enabled=False,
            )

        audits = list_memory_injection_audits_paginated(session, limit=3)

        assert len(audits) == 3


def test_paginated_list_respects_offset():
    test_engine = make_test_engine()

    with Session(test_engine) as session:
        for i in range(4):
            create_memory_injection_audit(
                session=session,
                conversation_id=i,
                selected_memory_ids=[i],
                total_context_chars=10,
                feature_flag_enabled=False,
            )

        all_audits = list_memory_injection_audits_paginated(session, limit=10, offset=0)
        offset_audits = list_memory_injection_audits_paginated(session, limit=10, offset=1)

        assert len(offset_audits) == len(all_audits) - 1
        assert offset_audits[0].id == all_audits[1].id


def test_init_db_can_create_audit_table():
    test_engine = create_db_engine("sqlite:///:memory:")

    init_db(test_engine)

    table_names = inspect(test_engine).get_table_names()
    assert "memory_injection_audit" in table_names


def test_chat_old_format_still_returns_200():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    assert set(response.json().keys()) == {"reply", "mood", "source"}


def test_chat_response_does_not_include_audit_fields():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "Hello!"})

    data = response.json()
    assert response.status_code == 200
    assert set(data.keys()) == {"reply", "mood", "source"}
    assert "audit" not in data
    assert "memory_injection_audit" not in data
    assert "selected_memory_ids" not in data


def test_chat_does_not_create_audit_rows_automatically():
    init_db(engine)
    with TestClient(app) as client:
        with Session(engine) as session:
            before_count = len(session.exec(select(MemoryInjectionAudit)).all())

        response = client.post("/chat", json={"message": "Hello!"})

        with Session(engine) as session:
            after_count = len(session.exec(select(MemoryInjectionAudit)).all())

    assert response.status_code == 200
    assert after_count == before_count
