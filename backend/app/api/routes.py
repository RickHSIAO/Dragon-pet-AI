"""
API routes for dragon-pet-ai backend.

TASK-009 keeps the system mock-only while allowing mock chat to read internal
MVP state before generating a reply.

Safety boundaries:
- /chat does not call any external AI API.
- /chat does not execute shell commands.
- /chat does not read or write user files.
- /chat only writes local conversation history and internal MVP state to SQLite.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.config import is_memory_injection_enabled
from app.db.database import get_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.memory import (
    MemoryContextPreviewResponse,
    MemoryCreateRequest,
    MemoryResponse,
)
from app.schemas.memory_audit import (
    MemoryInjectionAuditListResponse,
    MemoryInjectionAuditResponse,
)
from app.services.chat_service import generate_chat_reply
from app.services.conversation_service import get_or_create_default_conversation, store_chat_turn
from app.services.memory_audit_service import (
    create_memory_injection_audit,
    list_memory_injection_audits_paginated,
    normalize_audit_pagination,
    parse_exclusion_summary_json,
    parse_memory_ids_json,
)
from app.services.memory_service import (
    build_approved_memory_context_records,
    build_memory_context_preview,
    create_memory,
    deactivate_memory,
    list_active_memories,
)
from app.services.prompt_service import format_approved_memory_context, normalize_chat_mode
from app.services.state_service import get_chat_state_context, update_state_after_chat_turn
from app.services.usage_meter_service import UsageRecord, estimate_text_tokens, record_usage

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Liveness check endpoint.
    Returns ok status if the backend is running.
    """
    return {"status": "ok", "service": "dragon-pet-ai"}


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    """
    Mock chat endpoint.

    The route adapts the API request/response, reads internal local state for
    mock phrasing, optionally builds approved memory context (feature-flagged),
    stores the turn, and updates state afterward.

    Response schema is always: reply / mood / source
    Memory content is never returned to the caller.

    TASK-020: MEMORY_INJECTION_ENABLED (default False) gates memory context
    building and audit log creation. When disabled, behaviour is identical to
    TASK-019 and earlier. When enabled, the approved context is built and an
    audit row is written, but the formatted context is not yet passed to the
    mock reply generator (no real LLM connected yet).

    TASK-023: Two-layer safety model. Approved memory context is used only when
    BOTH the backend global gate (MEMORY_INJECTION_ENABLED=true) AND the
    per-request toggle (request.use_memory=true) are true.  Either gate being
    False means no injection and no audit row.
    """
    mode = normalize_chat_mode(request.mode)
    state_context = get_chat_state_context(session)

    # ── Two-layer memory context gate (TASK-023) ───────────────────────────
    # Layer 1 — backend global gate: MEMORY_INJECTION_ENABLED env var (default False)
    # Layer 2 — per-request toggle:  request.use_memory (default False)
    #
    # Only when BOTH are True may /chat build approved memory context and
    # write a MemoryInjectionAudit row.  Either gate being False means no
    # memory injection and no audit row — identical to pre-TASK-020 behaviour.
    #
    # Memory content is NEVER placed in the response returned to the caller.
    memory_enabled = is_memory_injection_enabled()
    memory_requested = request.use_memory is True
    should_use_memory = memory_enabled and memory_requested
    formatted_context: str | None = None

    if should_use_memory:
        # Obtain conversation_id before store_chat_turn so the audit row can
        # reference the same default conversation.
        conversation = get_or_create_default_conversation(session)
        conversation_id: int | None = conversation.id

        selected_records = build_approved_memory_context_records(session)
        selected_ids = [record.id for record in selected_records if record.id is not None]
        entries = [record.content.strip() for record in selected_records]
        formatted_context = format_approved_memory_context(entries)

        # exclusion_summary is not yet computed by the builder — tracked in
        # TASKS.md TASK-020 implementation notes for follow-up.
        create_memory_injection_audit(
            session=session,
            conversation_id=conversation_id,
            selected_memory_ids=selected_ids,
            total_context_chars=len(formatted_context),
            feature_flag_enabled=True,
            exclusion_summary=None,
        )
        # NOTE: formatted_context is safe-delimited approved memory context.
        # It is passed to chat_service only; it is never returned to clients.

    response_data = generate_chat_reply(
        request.message,
        request.mode,
        state_context,
        memory_context=formatted_context,
    )

    # ── Usage meter recording (TASK-050) ──────────────────────────────────
    # Record only safe aggregate metadata. Raw message text, prompt text,
    # memory context text, provider response body, and API key are NEVER
    # stored. Only integer token-length estimates and safe identifiers.
    _source = response_data["source"]
    record_usage(UsageRecord(
        source=_source,
        provider=None,   # provider name not exposed at this layer
        model=None,      # model name not exposed at this layer
        estimated_input_tokens=estimate_text_tokens(request.message),
        estimated_output_tokens=estimate_text_tokens(response_data["reply"]),
        fallback_used=(_source == "llm_real_error"),
        memory_used=should_use_memory,
        error_category=None,
    ))

    store_chat_turn(
        session=session,
        user_message=request.message,
        assistant_reply=response_data["reply"],
        mode=mode,
        mood=response_data["mood"],
        source=response_data["source"],
    )
    update_state_after_chat_turn(
        session=session,
        mood=response_data["mood"],
        mode=mode,
    )
    return ChatResponse(**response_data)


@router.post("/memory", response_model=MemoryResponse)
def create_memory_route(
    request: MemoryCreateRequest,
    session: Session = Depends(get_session),
) -> MemoryResponse:
    """
    Create an explicit local memory record.

    This endpoint is manual-only. It does not perform extraction, retrieval, or
    connect memory to chat responses.
    """
    try:
        memory = create_memory(
            session=session,
            memory_type=request.memory_type,
            content=request.content,
            importance=request.importance,
            confidence=request.confidence,
            source=request.source,
            source_message_id=request.source_message_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MemoryResponse.model_validate(memory)


@router.get("/memory", response_model=list[MemoryResponse])
def list_memory_route(session: Session = Depends(get_session)) -> list[MemoryResponse]:
    """
    List active local memory records.

    This is a plain list endpoint, not semantic retrieval.
    """
    return [
        MemoryResponse.model_validate(memory)
        for memory in list_active_memories(session)
    ]


@router.get("/memory/context-preview", response_model=MemoryContextPreviewResponse)
def memory_context_preview_route(
    session: Session = Depends(get_session),
) -> MemoryContextPreviewResponse:
    """
    Preview active memories as deterministic context text.

    This does not perform semantic retrieval and is not used by /chat.
    """
    preview = build_memory_context_preview(session)
    return MemoryContextPreviewResponse(
        memories=[
            MemoryResponse.model_validate(memory)
            for memory in preview["memories"]
        ],
        context_text=preview["context_text"],
        count=preview["count"],
        source=preview["source"],
    )


@router.get("/memory/audit", response_model=MemoryInjectionAuditListResponse)
def list_audit_route(
    limit: int = 20,
    offset: int = 0,
    session: Session = Depends(get_session),
) -> MemoryInjectionAuditListResponse:
    """
    Read-only audit inspection endpoint.

    Returns safe metadata about past memory injection events: which memory IDs
    were selected, how many, total context chars, and flag state.

    Safety rules:
    - This endpoint is read-only. It does not create rows or modify any table.
    - Raw memory content is never included in any response field.
    - Prompt text and approved memory context text are never returned.
    - selected_memory_ids is a list of integer IDs only.

    TASK-026: supports limit (default 20, max 100) and offset (default 0).
    Results are sorted newest first (id descending).
    """
    norm_limit, norm_offset = normalize_audit_pagination(limit, offset)
    rows = list_memory_injection_audits_paginated(
        session, limit=norm_limit, offset=norm_offset
    )
    items = [
        MemoryInjectionAuditResponse(
            id=row.id,
            created_at=row.created_at,
            conversation_id=row.conversation_id,
            selected_memory_ids=parse_memory_ids_json(row.selected_memory_ids_json),
            selected_count=row.selected_count,
            total_context_chars=row.total_context_chars,
            feature_flag_enabled=row.feature_flag_enabled,
            exclusion_summary=parse_exclusion_summary_json(row.exclusion_summary_json),
        )
        for row in rows
    ]
    return MemoryInjectionAuditListResponse(
        items=items,
        count=len(items),
        limit=norm_limit,
        offset=norm_offset,
    )


@router.delete("/memory/{memory_id}", response_model=MemoryResponse)
def deactivate_memory_route(
    memory_id: int,
    session: Session = Depends(get_session),
) -> MemoryResponse:
    """
    Deactivate a memory record without deleting the database row.
    """
    memory = deactivate_memory(session, memory_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="memory not found")
    return MemoryResponse.model_validate(memory)
