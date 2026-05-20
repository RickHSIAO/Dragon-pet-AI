import os

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

import pytest

from app.services.provider_settings_service import (
    ProviderSettingsUpdate,
    get_provider_settings,
    reset_provider_settings,
    update_provider_settings,
)
from app.services.usage_meter_service import (
    UsageRecord,
    record_usage,
    reset_usage_meter,
)


@pytest.fixture(autouse=True)
def reset_settings_and_usage():
    reset_provider_settings()
    reset_usage_meter()
    yield
    reset_provider_settings()
    reset_usage_meter()


def test_defaults_are_safe_and_non_secret(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-service-secret-should-not-be-read")

    settings = get_provider_settings()
    observed = repr(settings)

    assert settings["provider"] == "mock"
    assert settings["model"] is None
    assert settings["real_provider_enabled"] is False
    assert settings["llm_chat_enabled"] is False
    assert settings["fallback_to_mock"] is True
    assert settings["key_status"] == "not_configured"
    assert settings["resolved_provider"] == "mock"
    assert settings["last_test_status"] == "not_tested"
    assert "sk-service-secret-should-not-be-read" not in observed


def test_update_non_secret_provider_settings():
    settings = update_provider_settings(ProviderSettingsUpdate(
        provider="anthropic",
        model="claude-test",
        real_provider_enabled=True,
        llm_chat_enabled=True,
        fallback_to_mock=False,
    ))

    assert settings["provider"] == "anthropic"
    assert settings["model"] == "claude-test"
    assert settings["real_provider_enabled"] is True
    assert settings["llm_chat_enabled"] is True
    assert settings["fallback_to_mock"] is False
    assert settings["resolved_provider"] == "safe_fallback"


def test_update_rejects_unsupported_provider():
    with pytest.raises(ValueError, match="unsupported provider"):
        update_provider_settings(ProviderSettingsUpdate(provider="surprise"))


def test_usage_summary_is_safe_aggregate_only():
    raw_message = "UNIQUE_RAW_MESSAGE_NOT_IN_USAGE_SETTINGS"
    record_usage(UsageRecord(
        source="llm_real",
        provider="anthropic",
        model="claude-test",
        estimated_input_tokens=len(raw_message),
        estimated_output_tokens=3,
        fallback_used=True,
        memory_used=True,
        error_category="timeout",
    ))

    usage_summary = get_provider_settings()["usage_summary"]
    observed = repr(usage_summary)

    assert usage_summary["request_count"] == 1
    assert usage_summary["source_counts"] == {"llm_real": 1}
    assert usage_summary["provider_counts"] == {"anthropic": 1}
    assert usage_summary["model_counts"] == {"claude-test": 1}
    assert usage_summary["estimated_input_tokens"] == len(raw_message)
    assert usage_summary["estimated_output_tokens"] == 3
    assert usage_summary["estimated_total_tokens"] == len(raw_message) + 3
    assert usage_summary["fallback_count"] == 1
    assert usage_summary["memory_used_count"] == 1
    assert usage_summary["error_counts"] == {"timeout": 1}
    assert raw_message not in observed
    assert "api_key" not in observed
