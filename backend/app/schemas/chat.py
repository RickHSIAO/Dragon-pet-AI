"""
Chat request / response schemas for dragon-pet-ai.

Response schema is fixed at reply / mood / source.
Memory content is never included in any response field.

TASK-023: ChatRequest now supports an optional use_memory field.
use_memory defaults to False.  Both use_memory=True AND the backend
MEMORY_INJECTION_ENABLED env flag must be True before /chat uses
approved memory context (two-layer safety model).
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    mode: str | None = None
    use_memory: bool = False


class ChatResponse(BaseModel):
    reply: str
    mood: str
    source: str
