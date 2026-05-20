"""
Memory injection audit service for dragon-pet-ai.

Handles creation, serialization, parsing, and read-only listing of
MemoryInjectionAudit records.

Safety rules:
- Audit rows store only safe metadata (IDs, counts, chars, flag state).
- Raw memory content must never be stored in or returned from audit rows.
- list_memory_injection_audits_paginated is read-only; it must not create rows
  or modify any Memory row's last_used_at.
"""

import json

from sqlmodel import Session, select

from app.db.models import MemoryInjectionAudit

# ---------------------------------------------------------------------------
# Serialisation helpers (write path)
# ---------------------------------------------------------------------------

def serialize_memory_ids(memory_ids: list[int]) -> str:
    return json.dumps(memory_ids, separators=(",", ":"))


def serialize_exclusion_summary(summary: dict[str, int] | None) -> str | None:
    if summary is None:
        return None
    return json.dumps(summary, sort_keys=True, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Parsing helpers (read path)
# ---------------------------------------------------------------------------

def parse_memory_ids_json(value: str) -> list[int]:
    """
    Parse a JSON string into a list of ints.

    Returns [] on invalid JSON, non-list input, or empty string.
    Non-int values within the list are silently dropped.
    """
    if not value:
        return []
    try:
        data = json.loads(value)
    except (json.JSONDecodeError, TypeError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, int)]


def parse_exclusion_summary_json(value: str | None) -> dict[str, int] | None:
    """
    Parse a JSON string into a dict[str, int].

    Returns None on None input, invalid JSON, or non-dict input.
    Non-int values within the dict are silently dropped.
    """
    if value is None:
        return None
    try:
        data = json.loads(value)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return {k: v for k, v in data.items() if isinstance(v, int)}


# ---------------------------------------------------------------------------
# Pagination helper
# ---------------------------------------------------------------------------

def normalize_audit_pagination(
    limit: int | None, offset: int | None
) -> tuple[int, int]:
    """
    Normalise limit and offset for audit listing.

    Rules:
    - limit None or <= 0 → default 20
    - limit > 100 → clamp to 100
    - offset None or < 0 → default 0
    """
    if limit is None or limit <= 0:
        limit = 20
    elif limit > 100:
        limit = 100
    if offset is None or offset < 0:
        offset = 0
    return limit, offset


# ---------------------------------------------------------------------------
# Write path
# ---------------------------------------------------------------------------

def create_memory_injection_audit(
    session: Session,
    conversation_id: int | None,
    selected_memory_ids: list[int],
    total_context_chars: int,
    feature_flag_enabled: bool,
    exclusion_summary: dict[str, int] | None = None,
) -> MemoryInjectionAudit:
    audit = MemoryInjectionAudit(
        conversation_id=conversation_id,
        selected_memory_ids_json=serialize_memory_ids(selected_memory_ids),
        selected_count=len(selected_memory_ids),
        total_context_chars=max(0, total_context_chars),
        feature_flag_enabled=feature_flag_enabled,
        exclusion_summary_json=serialize_exclusion_summary(exclusion_summary),
    )
    session.add(audit)
    session.commit()
    session.refresh(audit)
    return audit


# ---------------------------------------------------------------------------
# Read path
# ---------------------------------------------------------------------------

def list_memory_injection_audits(session: Session) -> list[MemoryInjectionAudit]:
    """Original listing helper — ascending by id, retained for backward compat."""
    return session.exec(
        select(MemoryInjectionAudit).order_by(MemoryInjectionAudit.id)
    ).all()


def list_memory_injection_audits_paginated(
    session: Session,
    limit: int = 20,
    offset: int = 0,
) -> list[MemoryInjectionAudit]:
    """
    Return audit rows newest first, with pagination.

    This function is read-only: it does not create rows or modify any table.
    limit and offset are normalised internally via normalize_audit_pagination.
    """
    norm_limit, norm_offset = normalize_audit_pagination(limit, offset)
    return session.exec(
        select(MemoryInjectionAudit)
        .order_by(MemoryInjectionAudit.id.desc())
        .limit(norm_limit)
        .offset(norm_offset)
    ).all()
