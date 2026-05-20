from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, select

from app.db.database import create_db_engine, init_db
from app.db.models import Conversation, Message
from app.services.conversation_service import (
    get_or_create_default_conversation,
    store_chat_turn,
)


def make_test_engine():
    engine = create_db_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


def test_init_db_creates_conversation_and_message_tables():
    engine = create_db_engine("sqlite:///:memory:")

    init_db(engine)

    table_names = inspect(engine).get_table_names()
    assert "conversation" in table_names
    assert "message" in table_names


def test_get_or_create_default_conversation_creates_one():
    engine = make_test_engine()

    with Session(engine) as session:
        conversation = get_or_create_default_conversation(session)

        assert conversation.id is not None
        assert conversation.title == "Default Conversation"


def test_get_or_create_default_conversation_reuses_existing_default():
    engine = make_test_engine()

    with Session(engine) as session:
        first = get_or_create_default_conversation(session)
        second = get_or_create_default_conversation(session)
        conversations = session.exec(select(Conversation)).all()

        assert first.id == second.id
        assert len(conversations) == 1


def test_store_chat_turn_stores_two_messages():
    engine = make_test_engine()

    with Session(engine) as session:
        store_chat_turn(
            session=session,
            user_message="hello",
            assistant_reply="Hi. I'm here.",
            mode="casual",
            mood="happy",
            source="mock",
        )
        messages = session.exec(select(Message).order_by(Message.id)).all()

        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[0].content == "hello"
        assert messages[1].role == "assistant"
        assert messages[1].content == "Hi. I'm here."


def test_store_chat_turn_assistant_message_stores_mood_mode_source():
    engine = make_test_engine()

    with Session(engine) as session:
        store_chat_turn(
            session=session,
            user_message="help me debug",
            assistant_reply="Start with the exact error.",
            mode="debug",
            mood="focused",
            source="mock",
        )
        assistant_message = session.exec(
            select(Message).where(Message.role == "assistant")
        ).one()

        assert assistant_message.mode == "debug"
        assert assistant_message.mood == "focused"
        assert assistant_message.source == "mock"
