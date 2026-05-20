import re

from sqlmodel import Session, select

from app.db.models import Memory, utc_now

APPROVED_MEMORY_TYPES = {
    "user_preference",
    "project_context",
    "task_memory",
    "character_note",
}
APPROVED_CONFIDENCE_TYPES = {"explicit", "user_corrected"}
MAX_APPROVED_MEMORIES = 5
MAX_MEMORY_CONTEXT_CHARS = 1500

_CONFIDENCE_PRIORITY = {
    "user_corrected": 0,
    "explicit": 1,
}
_MEMORY_TYPE_PRIORITY = {
    "user_preference": 0,
    "project_context": 1,
    "task_memory": 2,
    "character_note": 3,
}
_SENSITIVE_KEYWORD_PATTERNS = (
    re.compile(r"\bpassword\b", re.IGNORECASE),
    re.compile(r"\bapi[ _-]?key\b", re.IGNORECASE),
    re.compile(r"\bbearer\s+token\b", re.IGNORECASE),
    re.compile(r"\bprivate\s+key\b", re.IGNORECASE),
    re.compile(r"\bssh-rsa\b", re.IGNORECASE),
    re.compile(r"\bsk-[A-Za-z0-9_-]*", re.IGNORECASE),
    re.compile(r"\bseed\s+phrase\b", re.IGNORECASE),
    re.compile(r"\brecovery\s+phrase\b", re.IGNORECASE),
    re.compile(r"\bpassport\b", re.IGNORECASE),
    re.compile(r"\bnational\s+id\b", re.IGNORECASE),
    re.compile(r"身分證"),
    re.compile(r"護照"),
)
_CREDIT_CARD_LIKE_PATTERN = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")


def clamp_importance(value: int, min_value: int = 0, max_value: int = 100) -> int:
    return max(min_value, min(max_value, value))


def create_memory(
    session: Session,
    memory_type: str,
    content: str,
    importance: int = 50,
    confidence: str = "explicit",
    source: str | None = None,
    source_message_id: int | None = None,
) -> Memory:
    stripped_content = content.strip()
    if not stripped_content:
        raise ValueError("memory content cannot be blank")

    now = utc_now()
    memory = Memory(
        memory_type=memory_type,
        content=stripped_content,
        importance=clamp_importance(importance),
        confidence=confidence,
        source=source,
        source_message_id=source_message_id,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    session.add(memory)
    session.commit()
    session.refresh(memory)
    return memory


def list_active_memories(session: Session) -> list[Memory]:
    return session.exec(
        select(Memory).where(Memory.is_active == True).order_by(Memory.id)  # noqa: E712
    ).all()


def contains_obvious_sensitive_content(content: str) -> bool:
    """
    Conservative injection-time second-pass filter.

    This is not complete data-loss prevention. It catches obvious secrets and
    sensitive identifiers before memory can be assembled into prompt context.
    """
    for pattern in _SENSITIVE_KEYWORD_PATTERNS:
        if pattern.search(content):
            return True

    for match in _CREDIT_CARD_LIKE_PATTERN.finditer(content):
        digit_count = len(re.sub(r"\D", "", match.group(0)))
        if 13 <= digit_count <= 19:
            return True

    return False


def is_memory_eligible_for_injection(memory: Memory) -> bool:
    content = memory.content.strip()
    return (
        memory.is_active is True
        and bool(content)
        and memory.memory_type in APPROVED_MEMORY_TYPES
        and memory.confidence in APPROVED_CONFIDENCE_TYPES
        and not contains_obvious_sensitive_content(content)
    )


def build_approved_memory_context_records(session: Session) -> list[Memory]:
    """
    Return the ordered list of Memory ORM objects eligible for injection.

    Returns Memory objects (not just content strings) so callers can access
    record IDs for audit logging without putting IDs into the prompt text.

    TASK-020: Added to support audit ID tracking in the /chat wiring layer.
    """
    memories = session.exec(
        select(Memory).where(Memory.is_active == True)  # noqa: E712
    ).all()
    eligible_memories = [
        memory for memory in memories if is_memory_eligible_for_injection(memory)
    ]
    ordered_memories = sorted(
        eligible_memories,
        key=lambda memory: (
            _CONFIDENCE_PRIORITY[memory.confidence],
            -memory.importance,
            _MEMORY_TYPE_PRIORITY[memory.memory_type],
            memory.id or 0,
        ),
    )
    return ordered_memories[:MAX_APPROVED_MEMORIES]


def build_approved_memory_context_entries(session: Session) -> list[str]:
    """
    Return approved memory content strings for prompt assembly.

    Delegates to build_approved_memory_context_records so ordering and
    filtering logic stays in one place. Content strings only — no IDs,
    no metadata labels — to keep prompt text clean.
    """
    return [
        memory.content.strip()
        for memory in build_approved_memory_context_records(session)
    ]


def build_approved_memory_context_text(session: Session) -> str:
    entries = build_approved_memory_context_entries(session)
    included_entries: list[str] = []
    current_length = 0

    for entry in entries:
        separator_length = 1 if included_entries else 0
        next_length = current_length + separator_length + len(entry)
        if next_length > MAX_MEMORY_CONTEXT_CHARS:
            continue
        included_entries.append(entry)
        current_length = next_length

    return "\n".join(included_entries)


def build_memory_context_preview(session: Session) -> dict:
    memories = session.exec(
        select(Memory)
        .where(Memory.is_active == True)  # noqa: E712
        .order_by(Memory.importance.desc(), Memory.id)
    ).all()

    if not memories:
        context_text = "Memory Context Preview:\n\nNo active memories."
    else:
        lines = ["Memory Context Preview:", ""]
        for memory in memories:
            lines.append(
                "* "
                f"[{memory.memory_type}]"
                f"[importance={memory.importance}]"
                f"[confidence={memory.confidence}] "
                f"{memory.content}"
            )
        context_text = "\n".join(lines)

    return {
        "memories": memories,
        "context_text": context_text,
        "count": len(memories),
        "source": "manual_memory_preview",
    }


def deactivate_memory(session: Session, memory_id: int) -> Memory | None:
    memory = session.get(Memory, memory_id)
    if memory is None:
        return None

    memory.is_active = False
    memory.updated_at = utc_now()
    session.add(memory)
    session.commit()
    session.refresh(memory)
    return memory
