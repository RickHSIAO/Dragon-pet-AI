"""
In-memory usage meter service for dragon-pet-ai.

TASK-050: Tracks safe aggregate usage metadata per session.

Safety rules enforced by design:
- UsageRecord contains only aggregate metadata and safe identifiers.
- Raw user message text is NEVER stored — only token-length estimates.
- Raw prompt text is NEVER stored.
- Raw memory context text is NEVER stored.
- Raw provider response body is NEVER stored.
- API key is NEVER stored.
- Full conversation history is NEVER stored.
- Storage is in-memory only. Data resets on backend restart (acceptable MVP).
- No SQLite usage table is created or referenced.

Allowed fields (aggregate metadata only):
- source: controlled enum-like string (mock / llm_mock / llm_real / llm_real_error)
- provider: provider name string (mock / anthropic / openai) — not a key
- model: model name string — not a key
- estimated_input_tokens: integer count derived from message length
- estimated_output_tokens: integer count derived from reply length
- fallback_used: boolean
- memory_used: boolean
- error_category: safe error category string or None
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from threading import Lock


# ---------------------------------------------------------------------------
# Token estimation helper
# ---------------------------------------------------------------------------

def estimate_text_tokens(text: str | None) -> int:
    """
    Rough local token estimate from text length.

    Rules:
    - None or empty string returns 0.
    - Approximation only: 1 token ≈ 4 characters (English heuristic).
    - CJK and other scripts tokenize differently; this is a lower-bound estimate.
    - Never presented as exact billing. Label results as approximate in UI.
    - The original text is NOT stored anywhere — only the integer estimate is returned.
    """
    if not text:
        return 0
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# UsageRecord — one /chat turn
# ---------------------------------------------------------------------------

@dataclass
class UsageRecord:
    """
    Safe aggregate metadata for one /chat turn.

    ONLY the following fields are permitted. Adding any forbidden field is a
    safety violation that must be caught in code review.

    Permitted fields:
    - source: controlled string — never raw content
    - provider: provider name — never a key value
    - model: model identifier — never a key value
    - estimated_input_tokens: integer — derived from length only, text not stored
    - estimated_output_tokens: integer — derived from length only, text not stored
    - fallback_used: boolean
    - memory_used: boolean
    - error_category: safe error category string or None

    Forbidden fields (must NEVER be added):
    - api_key / LLM_API_KEY / any key value
    - user_message / raw message text
    - prompt / system_prompt / raw prompt text
    - memory_context / approved_context / raw memory text
    - provider_response / response_body / raw provider output
    - conversation_history / full history
    """

    source: str
    provider: str | None = None
    model: str | None = None
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    fallback_used: bool = False
    memory_used: bool = False
    error_category: str | None = None


# ---------------------------------------------------------------------------
# UsageSummary — session aggregate
# ---------------------------------------------------------------------------

@dataclass
class UsageSummary:
    """
    Safe aggregate session-level usage summary.

    All fields are integer counts or safe identifier maps.
    No raw content of any kind is stored here.
    """

    request_count: int = 0
    source_counts: dict[str, int] = field(default_factory=dict)
    provider_counts: dict[str, int] = field(default_factory=dict)
    model_counts: dict[str, int] = field(default_factory=dict)
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    estimated_total_tokens: int = 0
    fallback_count: int = 0
    memory_used_count: int = 0
    error_counts: dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# UsageMeter — thread-safe in-memory accumulator
# ---------------------------------------------------------------------------

class UsageMeter:
    """
    Thread-safe in-memory session usage meter.

    Resets on backend restart. No SQLite persistence in Phase 4 MVP.
    One singleton instance is created at module load time.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._summary = UsageSummary()

    def record(self, record: UsageRecord) -> None:
        """
        Record one safe usage event.

        Only aggregate fields from UsageRecord are accumulated. Raw content
        is never accepted by this method — callers must pass only pre-computed
        counts and safe identifiers.
        """
        with self._lock:
            s = self._summary
            s.request_count += 1

            # Source counts
            s.source_counts[record.source] = s.source_counts.get(record.source, 0) + 1

            # Provider counts (safe name string only — not key value)
            if record.provider:
                s.provider_counts[record.provider] = (
                    s.provider_counts.get(record.provider, 0) + 1
                )

            # Model counts (safe identifier string only)
            if record.model:
                s.model_counts[record.model] = (
                    s.model_counts.get(record.model, 0) + 1
                )

            # Token estimates (integers only — original text is never stored)
            s.estimated_input_tokens += record.estimated_input_tokens
            s.estimated_output_tokens += record.estimated_output_tokens
            s.estimated_total_tokens += (
                record.estimated_input_tokens + record.estimated_output_tokens
            )

            # Fallback and memory flags
            if record.fallback_used:
                s.fallback_count += 1

            if record.memory_used:
                s.memory_used_count += 1

            # Error category (safe string or None — never raw error body)
            if record.error_category:
                s.error_counts[record.error_category] = (
                    s.error_counts.get(record.error_category, 0) + 1
                )

    def get_summary(self) -> UsageSummary:
        """Return a deep-copy snapshot of the current session summary."""
        with self._lock:
            return deepcopy(self._summary)

    def reset(self) -> None:
        """
        Reset all counters to zero.

        Intended for testing and session management only. Not called
        automatically during normal backend operation.
        """
        with self._lock:
            self._summary = UsageSummary()


# ---------------------------------------------------------------------------
# Module-level singleton and public API
# ---------------------------------------------------------------------------

_meter = UsageMeter()


def record_usage(record: UsageRecord) -> None:
    """Record one safe usage event to the session meter."""
    _meter.record(record)


def get_usage_summary() -> UsageSummary:
    """Return a snapshot of the current session usage summary."""
    return _meter.get_summary()


def reset_usage_meter() -> None:
    """
    Reset the session usage meter.

    Intended for testing only. Not called during normal backend operation.
    """
    _meter.reset()
