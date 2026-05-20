from sqlmodel import Session, select

from app.db.models import Conversation, Message, utc_now

DEFAULT_CONVERSATION_TITLE = "Default Conversation"


def get_or_create_default_conversation(session: Session) -> Conversation:
    conversation = session.exec(
        select(Conversation).where(Conversation.title == DEFAULT_CONVERSATION_TITLE)
    ).first()
    if conversation is not None:
        return conversation

    conversation = Conversation(title=DEFAULT_CONVERSATION_TITLE)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def store_chat_turn(
    session: Session,
    user_message: str,
    assistant_reply: str,
    mode: str,
    mood: str,
    source: str,
) -> None:
    """
    Store one user/assistant exchange in the default local conversation.

    This is conversation history only. It does not retrieve memory or summarize.
    """
    conversation = get_or_create_default_conversation(session)
    conversation.updated_at = utc_now()
    session.add(conversation)

    session.add(
        Message(
            conversation_id=conversation.id,
            role="user",
            content=user_message,
            mode=mode,
        )
    )
    session.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_reply,
            mode=mode,
            mood=mood,
            source=source,
        )
    )
    session.commit()
