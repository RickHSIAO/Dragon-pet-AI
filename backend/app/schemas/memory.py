from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MemoryCreateRequest(BaseModel):
    memory_type: str
    content: str
    importance: int = 50
    confidence: str = "explicit"
    source: str | None = "manual"
    source_message_id: int | None = None


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    memory_type: str
    content: str
    importance: int
    confidence: str
    source: str | None
    source_message_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_used_at: datetime | None


class MemoryContextPreviewResponse(BaseModel):
    memories: list[MemoryResponse]
    context_text: str
    count: int
    source: str = "manual_memory_preview"
