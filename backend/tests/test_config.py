"""
Tests for app.core.config — feature flag helpers.

TASK-020: MEMORY_INJECTION_ENABLED must default to False and only activate
on recognised truthy values. Unknown values must fail closed to False.
"""

import os

import pytest

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

from app.core.config import (  # noqa: E402
    get_llm_fallback_to_mock,
    get_llm_chat_enabled,
    get_local_chat_timeout_seconds,
    get_llm_provider_enabled,
    get_llm_provider_name,
    get_llm_timeout_seconds,
    is_memory_injection_enabled,
    read_bool_env,
    read_int_env,
)


# ---------------------------------------------------------------------------
# read_bool_env
# ---------------------------------------------------------------------------

class TestReadBoolEnv:
    def test_missing_env_var_returns_default_false(self, monkeypatch):
        monkeypatch.delenv("TEST_FLAG_XYZ", raising=False)
        assert read_bool_env("TEST_FLAG_XYZ") is False

    def test_missing_env_var_returns_explicit_default_true(self, monkeypatch):
        monkeypatch.delenv("TEST_FLAG_XYZ", raising=False)
        assert read_bool_env("TEST_FLAG_XYZ", default=True) is True

    @pytest.mark.parametrize("value", ["1", "true", "True", "TRUE", "yes", "Yes", "YES", "on", "On", "ON"])
    def test_truthy_values_return_true(self, monkeypatch, value):
        monkeypatch.setenv("TEST_FLAG_XYZ", value)
        assert read_bool_env("TEST_FLAG_XYZ") is True

    @pytest.mark.parametrize("value", ["0", "false", "False", "FALSE", "no", "No", "NO", "off", "Off", "OFF"])
    def test_falsy_values_return_false(self, monkeypatch, value):
        monkeypatch.setenv("TEST_FLAG_XYZ", value)
        assert read_bool_env("TEST_FLAG_XYZ") is False

    @pytest.mark.parametrize("value", ["maybe", "2", "enabled", "tru", "fals", "random", "  "])
    def test_unknown_values_fail_closed_to_false(self, monkeypatch, value):
        monkeypatch.setenv("TEST_FLAG_XYZ", value)
        # Unknown value must ALWAYS return False regardless of default —
        # we never want an unrecognised string to silently enable a safety flag.
        assert read_bool_env("TEST_FLAG_XYZ", default=True) is False

    def test_leading_trailing_whitespace_is_stripped(self, monkeypatch):
        monkeypatch.setenv("TEST_FLAG_XYZ", "  true  ")
        assert read_bool_env("TEST_FLAG_XYZ") is True


# ---------------------------------------------------------------------------
# is_memory_injection_enabled
# ---------------------------------------------------------------------------

class TestIsMemoryInjectionEnabled:
    def test_default_is_false_when_env_var_absent(self, monkeypatch):
        monkeypatch.delenv("MEMORY_INJECTION_ENABLED", raising=False)
        assert is_memory_injection_enabled() is False

    def test_explicit_false_string_returns_false(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "false")
        assert is_memory_injection_enabled() is False

    def test_explicit_zero_returns_false(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "0")
        assert is_memory_injection_enabled() is False

    def test_explicit_true_string_returns_true(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "true")
        assert is_memory_injection_enabled() is True

    def test_explicit_one_returns_true(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "1")
        assert is_memory_injection_enabled() is True

    def test_unknown_value_fails_closed_to_false(self, monkeypatch):
        monkeypatch.setenv("MEMORY_INJECTION_ENABLED", "enabled")
        assert is_memory_injection_enabled() is False


class TestLLMProviderConfig:
    def test_llm_provider_enabled_default_false(self, monkeypatch):
        monkeypatch.delenv("LLM_PROVIDER_ENABLED", raising=False)
        assert get_llm_provider_enabled() is False

    @pytest.mark.parametrize("value", ["1", "true", "yes", "on"])
    def test_llm_provider_enabled_true_like_values(self, monkeypatch, value):
        monkeypatch.setenv("LLM_PROVIDER_ENABLED", value)
        assert get_llm_provider_enabled() is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "off"])
    def test_llm_provider_enabled_false_like_values(self, monkeypatch, value):
        monkeypatch.setenv("LLM_PROVIDER_ENABLED", value)
        assert get_llm_provider_enabled() is False

    def test_llm_provider_enabled_unknown_bool_fails_closed(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER_ENABLED", "enabled")
        assert get_llm_provider_enabled() is False

    def test_llm_provider_name_default_mock(self, monkeypatch):
        monkeypatch.delenv("LLM_PROVIDER_NAME", raising=False)
        assert get_llm_provider_name() == "mock"

    def test_llm_timeout_default_30(self, monkeypatch):
        monkeypatch.delenv("LLM_TIMEOUT_SECONDS", raising=False)
        assert get_llm_timeout_seconds() == 30

    def test_llm_timeout_below_min_clamps_safely(self, monkeypatch):
        monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "0")
        assert get_llm_timeout_seconds() == 1

    def test_llm_timeout_above_max_clamps_safely(self, monkeypatch):
        monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "999")
        assert get_llm_timeout_seconds() == 120

    def test_llm_timeout_invalid_falls_back_to_default(self, monkeypatch):
        monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "not-an-int")
        assert get_llm_timeout_seconds() == 30

    def test_local_chat_timeout_default_90(self, monkeypatch):
        monkeypatch.delenv("LLM_LOCAL_CHAT_TIMEOUT_SECONDS", raising=False)
        monkeypatch.delenv("OLLAMA_TIMEOUT_SECONDS", raising=False)
        assert get_local_chat_timeout_seconds() == 90

    def test_local_chat_timeout_uses_new_env(self, monkeypatch):
        monkeypatch.setenv("LLM_LOCAL_CHAT_TIMEOUT_SECONDS", "150")
        monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "10")
        assert get_local_chat_timeout_seconds() == 150

    def test_local_chat_timeout_legacy_env_fallback(self, monkeypatch):
        monkeypatch.delenv("LLM_LOCAL_CHAT_TIMEOUT_SECONDS", raising=False)
        monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "45")
        assert get_local_chat_timeout_seconds() == 45

    def test_local_chat_timeout_clamps_safely(self, monkeypatch):
        monkeypatch.setenv("LLM_LOCAL_CHAT_TIMEOUT_SECONDS", "999")
        assert get_local_chat_timeout_seconds() == 300

    def test_llm_fallback_to_mock_default_true(self, monkeypatch):
        monkeypatch.delenv("LLM_FALLBACK_TO_MOCK", raising=False)
        assert get_llm_fallback_to_mock() is True

    def test_read_int_env_clamps_boundaries(self, monkeypatch):
        monkeypatch.setenv("TEST_INT", "-5")
        assert read_int_env("TEST_INT", default=10, min_value=1, max_value=20) == 1


class TestLLMChatConfig:
    def test_llm_chat_enabled_default_false(self, monkeypatch):
        monkeypatch.delenv("LLM_CHAT_ENABLED", raising=False)
        assert get_llm_chat_enabled() is False

    @pytest.mark.parametrize("value", ["1", "true", "yes", "on"])
    def test_llm_chat_enabled_true_like_values(self, monkeypatch, value):
        monkeypatch.setenv("LLM_CHAT_ENABLED", value)
        assert get_llm_chat_enabled() is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "off"])
    def test_llm_chat_enabled_false_like_values(self, monkeypatch, value):
        monkeypatch.setenv("LLM_CHAT_ENABLED", value)
        assert get_llm_chat_enabled() is False

    def test_llm_chat_enabled_unknown_value_fails_closed(self, monkeypatch):
        monkeypatch.setenv("LLM_CHAT_ENABLED", "enabled")
        assert get_llm_chat_enabled() is False
