from datetime import datetime, timezone
from typing import ClassVar

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    role: str = Field(index=True)
    content: str
    mode: str | None = None
    mood: str | None = None
    source: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class CharacterState(SQLModel, table=True):
    __tablename__: ClassVar[str] = "character_state"

    id: int | None = Field(default=None, primary_key=True)
    current_mood: str = "neutral"
    energy: int = 70
    focus: int = 50
    last_interaction_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class RelationshipState(SQLModel, table=True):
    __tablename__: ClassVar[str] = "relationship_state"

    id: int | None = Field(default=None, primary_key=True)
    affection: int = 0
    trust: int = 0
    familiarity: int = 0
    interaction_count: int = 0
    last_interaction_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Memory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    memory_type: str = Field(index=True)
    content: str
    importance: int = 50
    confidence: str = "explicit"
    source: str | None = None
    source_message_id: int | None = None
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    last_used_at: datetime | None = None


class MemoryInjectionAudit(SQLModel, table=True):
    __tablename__: ClassVar[str] = "memory_injection_audit"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int | None = Field(default=None, index=True)
    selected_memory_ids_json: str
    selected_count: int = 0
    total_context_chars: int = 0
    feature_flag_enabled: bool = False
    exclusion_summary_json: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
