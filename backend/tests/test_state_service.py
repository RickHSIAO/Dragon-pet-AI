from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, select

from app.db.database import create_db_engine, init_db
from app.db.models import CharacterState, RelationshipState
from app.services.state_service import (
    clamp_state_value,
    get_chat_state_context,
    get_or_create_default_character_state,
    get_or_create_default_relationship_state,
    update_state_after_chat_turn,
)


def make_test_engine():
    engine = create_db_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


def test_init_db_creates_state_tables():
    engine = create_db_engine("sqlite:///:memory:")

    init_db(engine)

    table_names = inspect(engine).get_table_names()
    assert "character_state" in table_names
    assert "relationship_state" in table_names


def test_get_or_create_default_character_state_creates_default_state():
    engine = make_test_engine()

    with Session(engine) as session:
        state = get_or_create_default_character_state(session)

        assert state.id is not None
        assert state.current_mood == "neutral"
        assert state.energy == 70
        assert state.focus == 50


def test_get_or_create_default_character_state_reuses_existing_state():
    engine = make_test_engine()

    with Session(engine) as session:
        first = get_or_create_default_character_state(session)
        second = get_or_create_default_character_state(session)
        states = session.exec(select(CharacterState)).all()

        assert first.id == second.id
        assert len(states) == 1


def test_get_or_create_default_relationship_state_creates_default_state():
    engine = make_test_engine()

    with Session(engine) as session:
        state = get_or_create_default_relationship_state(session)

        assert state.id is not None
        assert state.affection == 0
        assert state.trust == 0
        assert state.familiarity == 0
        assert state.interaction_count == 0


def test_get_or_create_default_relationship_state_reuses_existing_state():
    engine = make_test_engine()

    with Session(engine) as session:
        first = get_or_create_default_relationship_state(session)
        second = get_or_create_default_relationship_state(session)
        states = session.exec(select(RelationshipState)).all()

        assert first.id == second.id
        assert len(states) == 1


def test_clamp_state_value_clamps_below_zero():
    assert clamp_state_value(-5) == 0


def test_clamp_state_value_clamps_above_one_hundred():
    assert clamp_state_value(105) == 100


def test_update_state_after_chat_turn_updates_current_mood():
    engine = make_test_engine()

    with Session(engine) as session:
        character_state, relationship_state = update_state_after_chat_turn(
            session=session,
            mood="happy",
            mode="casual",
        )

        assert character_state.current_mood == "happy"
        assert character_state.last_interaction_at is not None
        assert relationship_state.last_interaction_at is not None


def test_update_state_after_chat_turn_increments_interaction_count():
    engine = make_test_engine()

    with Session(engine) as session:
        update_state_after_chat_turn(session=session, mood="focused", mode="casual")
        _, relationship_state = update_state_after_chat_turn(
            session=session,
            mood="focused",
            mode="casual",
        )

        assert relationship_state.interaction_count == 2
        assert relationship_state.familiarity == 2


def test_support_mode_can_increase_affection():
    engine = make_test_engine()

    with Session(engine) as session:
        _, relationship_state = update_state_after_chat_turn(
            session=session,
            mood="focused",
            mode="support",
        )

        assert relationship_state.affection == 1


def test_project_and_debug_modes_can_increase_trust():
    engine = make_test_engine()

    with Session(engine) as session:
        update_state_after_chat_turn(session=session, mood="focused", mode="project")
        _, relationship_state = update_state_after_chat_turn(
            session=session,
            mood="focused",
            mode="debug",
        )

        assert relationship_state.trust == 2


def test_get_chat_state_context_creates_defaults_if_missing():
    engine = make_test_engine()

    with Session(engine) as session:
        context = get_chat_state_context(session)
        character_states = session.exec(select(CharacterState)).all()
        relationship_states = session.exec(select(RelationshipState)).all()

        assert context.current_mood == "neutral"
        assert context.interaction_count == 0
        assert len(character_states) == 1
        assert len(relationship_states) == 1


def test_get_chat_state_context_returns_expected_fields():
    engine = make_test_engine()

    with Session(engine) as session:
        update_state_after_chat_turn(session=session, mood="focused", mode="debug")
        context = get_chat_state_context(session)

        assert context.current_mood == "focused"
        assert context.interaction_count == 1
        assert context.familiarity == 1
        assert context.affection == 0
        assert context.trust == 1
