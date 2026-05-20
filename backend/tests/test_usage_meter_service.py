"""
Tests for in-memory usage meter service.

TASK-050: Verifies safe aggregate tracking and privacy boundaries.

Privacy boundary tests verify that UsageRecord dataclass fields
contain NO forbidden attributes — specifically:
- No api_key / key / token field
- No user_message / message / raw content field
- No prompt / system_prompt field
- No memory_context / approved_context field
- No provider_response / response_body field
"""

import os

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

import dataclasses

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.usage_meter_service import (
    UsageRecord,
    UsageSummary,
    estimate_text_tokens,
    get_usage_summary,
    record_usage,
    reset_usage_meter,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_meter():
    """Reset the usage meter before and after each test."""
    reset_usage_meter()
    yield
    reset_usage_meter()


# ---------------------------------------------------------------------------
# estimate_text_tokens
# ---------------------------------------------------------------------------

class TestEstimateTextTokens:
    def test_none_returns_zero(self):
        assert estimate_text_tokens(None) == 0

    def test_empty_string_returns_zero(self):
        assert estimate_text_tokens("") == 0

    def test_short_text_returns_at_least_one(self):
        assert estimate_text_tokens("hi") >= 1

    def test_longer_text_returns_more_tokens(self):
        short = estimate_text_tokens("hello")
        long = estimate_text_tokens("hello " * 100)
        assert long > short

    def test_returns_integer(self):
        result = estimate_text_tokens("test message")
        assert isinstance(result, int)


# ---------------------------------------------------------------------------
# UsageRecord privacy boundary — forbidden fields must not exist
# ---------------------------------------------------------------------------

class TestUsageRecordPrivacyBoundary:
    """
    Verify that UsageRecord has NO fields that could store forbidden content.
    This is a structural safety check — if someone adds a forbidden field
    to the dataclass, these tests will catch it.
    """

    FORBIDDEN_FIELD_NAMES = {
        # API key variants
        "api_key", "llm_api_key", "key", "token", "secret", "bearer",
        # Raw user content
        "user_message", "message", "raw_message", "input_text",
        # Raw prompt content
        "prompt", "system_prompt", "raw_prompt", "formatted_prompt",
        # Raw memory content
        "memory_context", "approved_context", "memory_text", "raw_memory",
        # Raw provider output
        "provider_response", "response_body", "raw_response", "raw_body",
        # Conversation history
        "conversation_history", "history", "messages",
    }

    def test_usage_record_has_no_api_key_field(self):
        record_fields = {f.name for f in dataclasses.fields(UsageRecord)}
        forbidden_present = record_fields & {"api_key", "llm_api_key", "key", "token", "secret", "bearer"}
        assert not forbidden_present, f"Forbidden key field(s) found in UsageRecord: {forbidden_present}"

    def test_usage_record_has_no_raw_user_message_field(self):
        record_fields = {f.name for f in dataclasses.fields(UsageRecord)}
        forbidden_present = record_fields & {"user_message", "message", "raw_message", "input_text"}
        assert not forbidden_present, f"Forbidden message field(s) found in UsageRecord: {forbidden_present}"

    def test_usage_record_has_no_raw_prompt_field(self):
        record_fields = {f.name for f in dataclasses.fields(UsageRecord)}
        forbidden_present = record_fields & {"prompt", "system_prompt", "raw_prompt", "formatted_prompt"}
        assert not forbidden_present, f"Forbidden prompt field(s) found in UsageRecord: {forbidden_present}"

    def test_usage_record_has_no_raw_memory_context_field(self):
        record_fields = {f.name for f in dataclasses.fields(UsageRecord)}
        forbidden_present = record_fields & {"memory_context", "approved_context", "memory_text", "raw_memory"}
        assert not forbidden_present, f"Forbidden memory field(s) found in UsageRecord: {forbidden_present}"

    def test_usage_record_has_no_raw_provider_body_field(self):
        record_fields = {f.name for f in dataclasses.fields(UsageRecord)}
        forbidden_present = record_fields & {"provider_response", "response_body", "raw_response", "raw_body"}
        assert not forbidden_present, f"Forbidden provider body field(s) found in UsageRecord: {forbidden_present}"

    def test_usage_record_all_forbidden_absent(self):
        record_fields = {f.name for f in dataclasses.fields(UsageRecord)}
        forbidden_present = record_fields & self.FORBIDDEN_FIELD_NAMES
        assert not forbidden_present, f"Forbidden field(s) found in UsageRecord: {forbidden_present}"


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

class TestInitialSummaryIsZero:
    def test_request_count_is_zero(self):
        summary = get_usage_summary()
        assert summary.request_count == 0

    def test_source_counts_is_empty(self):
        summary = get_usage_summary()
        assert summary.source_counts == {}

    def test_provider_counts_is_empty(self):
        summary = get_usage_summary()
        assert summary.provider_counts == {}

    def test_model_counts_is_empty(self):
        summary = get_usage_summary()
        assert summary.model_counts == {}

    def test_token_counts_are_zero(self):
        summary = get_usage_summary()
        assert summary.estimated_input_tokens == 0
        assert summary.estimated_output_tokens == 0
        assert summary.estimated_total_tokens == 0

    def test_fallback_count_is_zero(self):
        assert get_usage_summary().fallback_count == 0

    def test_memory_used_count_is_zero(self):
        assert get_usage_summary().memory_used_count == 0

    def test_error_counts_is_empty(self):
        assert get_usage_summary().error_counts == {}


# ---------------------------------------------------------------------------
# Recording increments counters
# ---------------------------------------------------------------------------

class TestRecordingIncrements:
    def test_one_request_increments_request_count(self):
        record_usage(UsageRecord(source="mock"))
        assert get_usage_summary().request_count == 1

    def test_two_requests_increment_request_count_to_two(self):
        record_usage(UsageRecord(source="mock"))
        record_usage(UsageRecord(source="mock"))
        assert get_usage_summary().request_count == 2

    def test_source_counts_increments(self):
        record_usage(UsageRecord(source="mock"))
        assert get_usage_summary().source_counts.get("mock", 0) == 1

    def test_different_sources_tracked_separately(self):
        record_usage(UsageRecord(source="mock"))
        record_usage(UsageRecord(source="llm_real"))
        summary = get_usage_summary()
        assert summary.source_counts["mock"] == 1
        assert summary.source_counts["llm_real"] == 1

    def test_provider_counts_increment_when_provided(self):
        record_usage(UsageRecord(source="llm_real", provider="anthropic"))
        assert get_usage_summary().provider_counts.get("anthropic", 0) == 1

    def test_model_counts_increment_when_provided(self):
        record_usage(UsageRecord(source="llm_real", model="claude-opus-4-6"))
        assert get_usage_summary().model_counts.get("claude-opus-4-6", 0) == 1

    def test_provider_not_counted_when_none(self):
        record_usage(UsageRecord(source="mock", provider=None))
        assert get_usage_summary().provider_counts == {}

    def test_model_not_counted_when_none(self):
        record_usage(UsageRecord(source="mock", model=None))
        assert get_usage_summary().model_counts == {}

    def test_estimated_input_tokens_accumulate(self):
        record_usage(UsageRecord(source="mock", estimated_input_tokens=10))
        record_usage(UsageRecord(source="mock", estimated_input_tokens=5))
        assert get_usage_summary().estimated_input_tokens == 15

    def test_estimated_output_tokens_accumulate(self):
        record_usage(UsageRecord(source="mock", estimated_output_tokens=20))
        assert get_usage_summary().estimated_output_tokens == 20

    def test_estimated_total_tokens_is_sum_of_input_and_output(self):
        record_usage(UsageRecord(source="mock", estimated_input_tokens=10, estimated_output_tokens=20))
        assert get_usage_summary().estimated_total_tokens == 30

    def test_fallback_count_increments_when_fallback_used(self):
        record_usage(UsageRecord(source="llm_real_error", fallback_used=True))
        assert get_usage_summary().fallback_count == 1

    def test_fallback_count_does_not_increment_when_not_fallback(self):
        record_usage(UsageRecord(source="mock", fallback_used=False))
        assert get_usage_summary().fallback_count == 0

    def test_memory_used_count_increments_when_memory_used(self):
        record_usage(UsageRecord(source="mock", memory_used=True))
        assert get_usage_summary().memory_used_count == 1

    def test_memory_used_count_does_not_increment_when_memory_not_used(self):
        record_usage(UsageRecord(source="mock", memory_used=False))
        assert get_usage_summary().memory_used_count == 0

    def test_error_counts_increment(self):
        record_usage(UsageRecord(source="llm_real_error", error_category="timeout"))
        assert get_usage_summary().error_counts.get("timeout", 0) == 1

    def test_error_counts_not_incremented_when_no_error(self):
        record_usage(UsageRecord(source="mock", error_category=None))
        assert get_usage_summary().error_counts == {}


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------

class TestReset:
    def test_reset_clears_request_count(self):
        record_usage(UsageRecord(source="mock"))
        reset_usage_meter()
        assert get_usage_summary().request_count == 0

    def test_reset_clears_all_counters(self):
        record_usage(UsageRecord(
            source="llm_real",
            provider="anthropic",
            model="claude-opus-4-6",
            estimated_input_tokens=10,
            estimated_output_tokens=20,
            fallback_used=False,
            memory_used=True,
            error_category=None,
        ))
        reset_usage_meter()
        s = get_usage_summary()
        assert s.request_count == 0
        assert s.source_counts == {}
        assert s.provider_counts == {}
        assert s.model_counts == {}
        assert s.estimated_input_tokens == 0
        assert s.estimated_output_tokens == 0
        assert s.estimated_total_tokens == 0
        assert s.fallback_count == 0
        assert s.memory_used_count == 0
        assert s.error_counts == {}


# ---------------------------------------------------------------------------
# get_summary returns a copy (not a mutable reference)
# ---------------------------------------------------------------------------

class TestSummaryIsCopy:
    def test_modifying_returned_summary_does_not_affect_meter(self):
        record_usage(UsageRecord(source="mock"))
        summary = get_usage_summary()
        summary.request_count = 9999
        assert get_usage_summary().request_count == 1


# ---------------------------------------------------------------------------
# No SQLite usage table
# ---------------------------------------------------------------------------

class TestNoSQLiteUsageTable:
    def test_usage_record_is_not_a_sqlmodel(self):
        """UsageRecord must be a plain dataclass, not a SQLModel table."""
        try:
            from sqlmodel import SQLModel
            assert not issubclass(UsageRecord, SQLModel), \
                "UsageRecord must not be a SQLModel table"
        except ImportError:
            pass  # SQLModel not imported in this scope — also fine

    def test_usage_summary_is_not_a_sqlmodel(self):
        """UsageSummary must be a plain dataclass, not a SQLModel table."""
        try:
            from sqlmodel import SQLModel
            assert not issubclass(UsageSummary, SQLModel), \
                "UsageSummary must not be a SQLModel table"
        except ImportError:
            pass

    def test_no_usage_table_in_models(self):
        """models.py must not define a UsageRecord or UsageLog SQLModel table."""
        import app.db.models as models_module
        model_names = dir(models_module)
        assert "UsageLog" not in model_names
        assert "UsageTable" not in model_names
        # UsageRecord as a plain dataclass may exist in service, but not as a table model
        for name in model_names:
            cls = getattr(models_module, name)
            if isinstance(cls, type) and "Usage" in name:
                try:
                    from sqlmodel import SQLModel
                    assert not issubclass(cls, SQLModel), \
                        f"{name} in models.py must not be a SQLModel table"
                except ImportError:
                    pass


# ---------------------------------------------------------------------------
# /chat integration tests
# ---------------------------------------------------------------------------

class TestChatUsageMeterIntegration:
    """
    Verify that /chat records usage and that the response schema is unchanged.
    """

    def test_chat_response_schema_remains_reply_mood_source(self):
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello"})
        assert response.status_code == 200
        assert set(response.json().keys()) == {"reply", "mood", "source"}

    def test_chat_does_not_add_usage_to_response(self):
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello"})
        data = response.json()
        assert "usage" not in data
        assert "request_count" not in data
        assert "estimated_tokens" not in data
        assert "token_count" not in data

    def test_chat_increments_request_count(self):
        reset_usage_meter()
        with TestClient(app) as client:
            client.post("/chat", json={"message": "hello"})
        assert get_usage_summary().request_count == 1

    def test_chat_records_source(self):
        reset_usage_meter()
        with TestClient(app) as client:
            client.post("/chat", json={"message": "hello"})
        summary = get_usage_summary()
        assert "mock" in summary.source_counts

    def test_chat_usage_record_does_not_store_raw_message(self):
        """
        After a /chat call, the usage summary must not contain the raw message text.
        Verify by checking that the unique phrase does not appear in any field of the summary.
        """
        unique_phrase = "UNIQUE_SAFETY_PHRASE_DO_NOT_STORE_IN_USAGE_9x7z"
        reset_usage_meter()
        with TestClient(app) as client:
            client.post("/chat", json={"message": unique_phrase})
        summary = get_usage_summary()
        # Serialize summary to string and check phrase is absent
        summary_repr = repr(summary)
        assert unique_phrase not in summary_repr

    def test_chat_multiple_turns_accumulate_request_count(self):
        reset_usage_meter()
        with TestClient(app) as client:
            client.post("/chat", json={"message": "one"})
            client.post("/chat", json={"message": "two"})
            client.post("/chat", json={"message": "three"})
        assert get_usage_summary().request_count == 3

    def test_chat_old_format_still_returns_200(self):
        """Backward compatibility: requests without use_memory still work."""
        with TestClient(app) as client:
            response = client.post("/chat", json={"message": "hello"})
        assert response.status_code == 200
