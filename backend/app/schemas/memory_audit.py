"""
Audit inspection response schemas for dragon-pet-ai.

TASK-026: Read-only audit inspection API.

Safety rules:
- These schemas must never include raw memory content.
- These schemas must never include prompt text or approved memory context text.
- selected_memory_ids is a list of integer IDs only — not memory content.
- exclusion_summary is a metadata dict (reason -> count) only.
"""

from datetime import datetime

from pydantic import BaseModel


class MemoryInjectionAuditResponse(BaseModel):
    """
    Safe audit metadata for a single memory injection event.

    Fields deliberately excluded:
    - raw memory content
    - formatted memory context text
    - prompt text
    - system / developer instructions
    """

    id: int
    created_at: datetime
    conversation_id: int | None
    selected_memory_ids: list[int]
    selected_count: int
    total_context_chars: int
    feature_flag_enabled: bool
    exclusion_summary: dict[str, int] | None


class MemoryInjectionAuditListResponse(BaseModel):
    """
    Paginated list of audit inspection records.
    Sorted newest first.
    """

    items: list[MemoryInjectionAuditResponse]
    count: int
    limit: int
    offset: int
