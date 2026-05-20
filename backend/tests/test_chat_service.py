from app.llm.mock_provider import MockLLMProvider
from app.llm.types import LLMResponse
from app.services.chat_service import (
    ChatStateContext,
    generate_chat_reply,
    generate_mock_chat_reply,
)


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
