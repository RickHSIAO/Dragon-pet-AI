import pytest

from app.llm.mock_provider import MockLLMProvider
from app.llm.types import LLMResponse
from app.services.chat_service import (
    ChatStateContext,
    generate_chat_reply,
    generate_mock_chat_reply,
)
from app.services.character_service import format_mock_reply, select_mock_mood


def test_empty_message_returns_fallback():
    response = generate_mock_chat_reply("   ")

    assert response == {
        "reply": "You sent an empty message. Try saying something!",
        "mood": "neutral",
        "source": "mock",
    }


def test_valid_message_returns_mock_source():
    response = generate_mock_chat_reply("Can you help me plan this?")

    assert response["reply"]
    assert response["mood"] == "focused"
    assert response["source"] == "mock"


def test_generate_mock_chat_reply_without_state_context_still_works():
    response = generate_mock_chat_reply("hello", mode="casual", state_context=None)

    assert response["reply"]
    assert response["source"] == "mock"


def test_hello_returns_valid_mood_and_reply():
    response = generate_mock_chat_reply("hello")

    assert response["reply"]
    assert response["mood"] == "happy"
    assert response["source"] == "mock"


@pytest.mark.parametrize(
    ("message", "expected_mood"),
    [
        ("I am proud and victorious; praise me.", "proud"),
        ("I am worried this failed and may be unsafe.", "worried"),
        ("Stop it. Scold me like an annoyed tsundere.", "annoyed"),
        ("Can you help me plan this task?", "focused"),
        ("Neutral factual status summary only.", "neutral"),
        ("hello, thank you for the good work", "happy"),
        ("I am tired and need to sleep after this.", "sleepy"),
    ],
)
def test_select_mock_mood_deterministically_covers_supported_targets(
    message,
    expected_mood,
):
    assert select_mock_mood(message) == expected_mood


@pytest.mark.parametrize("mood", ["proud", "worried", "annoyed", "sleepy"])
def test_format_mock_reply_has_clean_replies_for_richer_moods(mood):
    reply = format_mock_reply("test message", mood, mode="debug")

    assert reply
    assert "mood:" not in reply.lower()
    assert "source:" not in reply.lower()
    assert "thinking" not in reply.lower()


def test_debug_mode_returns_mock_source():
    response = generate_mock_chat_reply("help me debug", mode="debug")

    assert response["reply"]
    assert response["mood"] == "focused"
    assert response["source"] == "mock"


def test_unknown_mode_falls_back_without_error():
    response = generate_mock_chat_reply("hello", mode="unknown")

    assert response["reply"]
    assert response["mood"] == "happy"
    assert response["source"] == "mock"


def test_high_familiarity_context_returns_mock_source():
    context = ChatStateContext(
        current_mood="focused",
        interaction_count=7,
        familiarity=8,
        affection=0,
        trust=0,
    )

    response = generate_mock_chat_reply(
        "Can you help me plan this?",
        mode="casual",
        state_context=context,
    )

    assert response["reply"]
    assert response["source"] == "mock"


def test_support_mode_with_higher_affection_returns_valid_reply():
    context = ChatStateContext(
        current_mood="focused",
        interaction_count=3,
        familiarity=3,
        affection=5,
        trust=0,
    )

    response = generate_mock_chat_reply(
        "I need support",
        mode="support",
        state_context=context,
    )

    assert response["reply"]
    assert response["source"] == "mock"


def test_debug_mode_with_higher_trust_returns_valid_reply():
    context = ChatStateContext(
        current_mood="focused",
        interaction_count=3,
        familiarity=3,
        affection=0,
        trust=5,
    )

    response = generate_mock_chat_reply(
        "help me debug",
        mode="debug",
        state_context=context,
    )

    assert response["reply"]
    assert response["source"] == "mock"


def test_project_mode_with_higher_trust_returns_valid_reply():
    context = ChatStateContext(
        current_mood="focused",
        interaction_count=3,
        familiarity=3,
        affection=0,
        trust=5,
    )

    response = generate_mock_chat_reply(
        "help me plan the task",
        mode="project",
        state_context=context,
    )

    assert response["reply"]
    assert response["source"] == "mock"


def test_generate_chat_reply_disabled_uses_existing_mock_behavior(monkeypatch):
    monkeypatch.delenv("LLM_CHAT_ENABLED", raising=False)

    response = generate_chat_reply("hello", mode="casual")

    assert set(response.keys()) == {"reply", "mood", "source"}
    assert response["source"] == "mock"
    assert response["mood"] == "happy"
    assert response["reply"]


def test_generate_chat_reply_disabled_does_not_call_llm_provider(monkeypatch):
    monkeypatch.setenv("LLM_CHAT_ENABLED", "false")

    def raise_if_called():
        raise AssertionError("LLM provider factory should not be called")

    monkeypatch.setattr("app.services.chat_service.get_llm_provider", raise_if_called)

    response = generate_chat_reply("hello", mode="casual")

    assert response["source"] == "mock"


def test_generate_chat_reply_enabled_uses_mock_llm_provider(monkeypatch):
    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: MockLLMProvider(),
    )

    response = generate_chat_reply("hello", mode="casual")

    assert set(response.keys()) == {"reply", "mood", "source"}
    assert response["source"] == "llm_mock"
    assert response["reply"]


def test_generate_chat_reply_enabled_accepts_memory_context_without_exposing_it(monkeypatch):
    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: MockLLMProvider(),
    )
    raw_memory = "UNIQUE_MEMORY_CONTEXT_SHOULD_NOT_APPEAR"

    response = generate_chat_reply(
        "hello",
        mode="casual",
        memory_context=raw_memory,
    )

    assert response["source"] == "llm_mock"
    assert raw_memory not in response["reply"]


def test_generate_chat_reply_enabled_real_provider_success(monkeypatch):
    class FakeRealProvider:
        provider_name = "anthropic"

        def generate(self, request):
            assert request.memory_context is None
            return LLMResponse(
                text="real provider reply",
                provider="anthropic",
                model="claude-test",
                usage={"input_tokens": 1},
                error=None,
            )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: FakeRealProvider(),
    )

    response = generate_chat_reply("hello", mode="project")

    assert response == {
        "reply": "real provider reply",
        "mood": "happy",
        "source": "llm_real",
    }


def test_generate_chat_reply_enabled_provider_error_falls_back_to_mock(monkeypatch):
    class ErrorProvider:
        provider_name = "anthropic"

        def generate(self, request):  # noqa: ARG002
            return LLMResponse(
                text="safe fallback text from provider",
                provider="anthropic",
                error="provider_error",
            )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setenv("LLM_FALLBACK_TO_MOCK", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: ErrorProvider(),
    )

    response = generate_chat_reply("hello", mode="casual")

    assert response["source"] == "mock"
    assert response["mood"] == "happy"
    assert response["reply"]


def test_generate_chat_reply_enabled_provider_error_safe_text_when_fallback_disabled(monkeypatch):
    class ErrorProvider:
        provider_name = "anthropic"

        def generate(self, request):  # noqa: ARG002
            return LLMResponse(
                text="raw provider text should not be used",
                provider="anthropic",
                error="provider_error",
            )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setenv("LLM_FALLBACK_TO_MOCK", "false")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: ErrorProvider(),
    )

    response = generate_chat_reply("hello", mode="casual")

    assert response["source"] == "llm_real_error"
    assert "raw provider text" not in response["reply"]


# ---------------------------------------------------------------------------
# TASK-075F — Ollama source mapping tests
# ---------------------------------------------------------------------------

def test_ollama_provider_success_returns_llm_local(monkeypatch):
    """provider_name='ollama' + successful LLM response → source='llm_local'."""

    class FakeOllamaProvider:
        provider_name = "ollama"

        def generate(self, request):  # noqa: ARG002
            return LLMResponse(
                text="local ollama reply",
                provider="ollama",
                model="qwen3:8b",
                usage={"output_tokens_actual": 5},
                error=None,
            )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: FakeOllamaProvider(),
    )

    response = generate_chat_reply("hello", mode="casual")

    assert response["source"] == "llm_local"
    assert response["reply"] == "local ollama reply"
    assert set(response.keys()) == {"reply", "mood", "source"}


def test_ollama_provider_success_uses_rich_message_mood_without_reply_pollution(
    monkeypatch,
):
    class FakeOllamaProvider:
        provider_name = "ollama"

        def generate(self, request):  # noqa: ARG002
            return LLMResponse(
                text="local provider character reply",
                provider="ollama",
                model="qwen3:8b",
                error=None,
            )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: FakeOllamaProvider(),
    )

    response = generate_chat_reply(
        "I am worried this safety check failed.",
        mode="support",
    )

    assert response == {
        "reply": "local provider character reply",
        "mood": "worried",
        "source": "llm_local",
    }


def test_ollama_provider_error_returns_llm_local_error_when_fallback_disabled(monkeypatch):
    """provider_name='ollama' + LLM error + fallback disabled → source='llm_local_error'."""

    class ErrorOllamaProvider:
        provider_name = "ollama"

        def generate(self, request):  # noqa: ARG002
            return LLMResponse(
                text="I cannot reach the real language model right now, "
                     "so I will continue in safe mock mode.",
                provider="ollama",
                error="ollama_unavailable",
            )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setenv("LLM_FALLBACK_TO_MOCK", "false")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: ErrorOllamaProvider(),
    )

    response = generate_chat_reply("hello", mode="casual")

    assert response["source"] == "llm_local_error"
    assert set(response.keys()) == {"reply", "mood", "source"}


def test_ollama_provider_error_falls_back_to_mock_when_fallback_enabled(monkeypatch):
    """provider_name='ollama' + LLM error + fallback enabled → source='mock'."""

    class ErrorOllamaProvider:
        provider_name = "ollama"

        def generate(self, request):  # noqa: ARG002
            return LLMResponse(
                text="I cannot reach the real language model right now, "
                     "so I will continue in safe mock mode.",
                provider="ollama",
                error="provider_timeout",
            )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setenv("LLM_FALLBACK_TO_MOCK", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: ErrorOllamaProvider(),
    )

    response = generate_chat_reply("hello", mode="casual")

    assert response["source"] == "mock"
    assert set(response.keys()) == {"reply", "mood", "source"}


def test_anthropic_provider_source_unchanged_by_ollama_fix(monkeypatch):
    """Existing cloud real provider behavior: source='llm_real' — unchanged."""

    class FakeAnthropicProvider:
        provider_name = "anthropic"

        def generate(self, request):  # noqa: ARG002
            return LLMResponse(
                text="cloud reply",
                provider="anthropic",
                model="claude-test",
                error=None,
            )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: FakeAnthropicProvider(),
    )

    response = generate_chat_reply("hello", mode="casual")

    assert response["source"] == "llm_real"
    assert set(response.keys()) == {"reply", "mood", "source"}


def test_chat_schema_has_only_reply_mood_source_with_ollama(monkeypatch):
    """/chat response schema must be exactly reply/mood/source — no extra fields."""

    class FakeOllamaProvider:
        provider_name = "ollama"

        def generate(self, request):  # noqa: ARG002
            return LLMResponse(
                text="schema check reply",
                provider="ollama",
                error=None,
            )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: FakeOllamaProvider(),
    )

    response = generate_chat_reply("test", mode="casual")

    assert set(response.keys()) == {"reply", "mood", "source"}
    assert response["source"] == "llm_local"
