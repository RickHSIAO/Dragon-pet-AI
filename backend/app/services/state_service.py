from sqlmodel import Session, select

from app.db.models import CharacterState, RelationshipState, utc_now
from app.services.chat_service import ChatStateContext
from app.services.prompt_service import normalize_chat_mode


def clamp_state_value(value: int, min_value: int = 0, max_value: int = 100) -> int:
    return max(min_value, min(max_value, value))


def get_or_create_default_character_state(session: Session) -> CharacterState:
    state = session.exec(select(CharacterState).order_by(CharacterState.id)).first()
    if state is not None:
        return state

    state = CharacterState()
    session.add(state)
    session.commit()
    session.refresh(state)
    return state


def get_or_create_default_relationship_state(session: Session) -> RelationshipState:
    state = session.exec(select(RelationshipState).order_by(RelationshipState.id)).first()
    if state is not None:
        return state

    state = RelationshipState()
    session.add(state)
    session.commit()
    session.refresh(state)
    return state


def get_chat_state_context(session: Session) -> ChatStateContext:
    """
    Return the minimal local state needed by mock chat generation.

    This creates defaults if needed and does not retrieve memories.
    """
    character_state = get_or_create_default_character_state(session)
    relationship_state = get_or_create_default_relationship_state(session)
    return ChatStateContext(
        current_mood=character_state.current_mood,
        interaction_count=relationship_state.interaction_count,
        familiarity=relationship_state.familiarity,
        affection=relationship_state.affection,
        trust=relationship_state.trust,
    )


def update_state_after_chat_turn(
    session: Session,
    mood: str,
    mode: str | None = None,
) -> tuple[CharacterState, RelationshipState]:
    """
    Update local MVP state after a chat turn.

    This does not perform memory retrieval, summaries, or autonomous actions.
    """
    chat_mode = normalize_chat_mode(mode)
    now = utc_now()

    character_state = get_or_create_default_character_state(session)
    relationship_state = get_or_create_default_relationship_state(session)

    character_state.current_mood = mood
    character_state.last_interaction_at = now
    character_state.updated_at = now

    relationship_state.interaction_count += 1
    relationship_state.familiarity = clamp_state_value(
        relationship_state.familiarity + 1
    )
    if chat_mode == "support":
        relationship_state.affection = clamp_state_value(
            relationship_state.affection + 1
        )
    if chat_mode in ("project", "debug"):
        relationship_state.trust = clamp_state_value(relationship_state.trust + 1)
    relationship_state.last_interaction_at = now
    relationship_state.updated_at = now

    session.add(character_state)
    session.add(relationship_state)
    session.commit()
    session.refresh(character_state)
    session.refresh(relationship_state)
    return character_state, relationship_state
