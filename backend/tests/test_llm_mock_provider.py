from app.llm.mock_provider import MockLLMProvider
from app.llm.types import LLMRequest, LLMResponse


def generate_for_mode(mode: str) -> LLMResponse:
    provider = MockLLMProvider()
    request = LLMRequest(system_prompt="system", user_message="hello", mode=mode)

    return provider.generate(request)


def test_mock_llm_provider_name_is_mock():
    provider = MockLLMProvider()

    assert provider.provider_name == "mock"


def test_mock_llm_provider_generate_returns_llm_response():
    provider = MockLLMProvider()
    request = LLMRequest(system_prompt="system", user_message="hello")

    response = provider.generate(request)

    assert isinstance(response, LLMResponse)


def test_mock_llm_provider_generate_does_not_return_empty_text():
    provider = MockLLMProvider()
    request = LLMRequest(system_prompt="system", user_message="hello")

    response = provider.generate(request)

    assert response.text


def test_mock_llm_provider_generate_provider_is_mock():
    provider = MockLLMProvider()
    request = LLMRequest(system_prompt="system", user_message="hello")

    response = provider.generate(request)

    assert response.provider == "mock"
    assert response.model == "mock-local"
    assert response.usage is None
    assert response.error is None


def test_mock_llm_provider_health_check_returns_true():
    provider = MockLLMProvider()

    assert provider.health_check() is True


def test_mock_llm_provider_handles_casual_mode():
    response = generate_for_mode("casual")

    assert response.text


def test_mock_llm_provider_handles_project_mode():
    response = generate_for_mode("project")

    assert response.text


def test_mock_llm_provider_handles_debug_mode():
    response = generate_for_mode("debug")

    assert response.text


def test_mock_llm_provider_handles_support_mode():
    response = generate_for_mode("support")

    assert response.text


def test_mock_llm_provider_handles_reminder_mode():
    response = generate_for_mode("reminder")

    assert response.text


def test_mock_llm_provider_unknown_mode_falls_back_safely():
    response = generate_for_mode("unknown")

    assert response.text
    assert response.provider == "mock"
    assert response.error is None


def test_mock_llm_provider_accepts_memory_context_none():
    provider = MockLLMProvider()
    request = LLMRequest(
        system_prompt="system",
        user_message="hello",
        memory_context=None,
    )

    response = provider.generate(request)

    assert response.text


def test_mock_llm_provider_accepts_memory_context_string():
    provider = MockLLMProvider()
    request = LLMRequest(
        system_prompt="system",
        user_message="hello",
        memory_context="User prefers Traditional Chinese.",
    )

    response = provider.generate(request)

    assert response.text


def test_mock_llm_provider_does_not_dump_raw_memory_context_by_default():
    provider = MockLLMProvider()
    raw_memory = "UNIQUE_RAW_MEMORY_CONTEXT_SHOULD_NOT_APPEAR"
    request = LLMRequest(
        system_prompt="system",
        user_message="hello",
        memory_context=raw_memory,
    )

    response = provider.generate(request)

    assert raw_memory not in response.text


def test_mock_llm_provider_accepts_state_context_none():
    provider = MockLLMProvider()
    request = LLMRequest(
        system_prompt="system",
        user_message="hello",
        state_context=None,
    )

    response = provider.generate(request)

    assert response.text


def test_mock_llm_provider_accepts_state_context_dict():
    provider = MockLLMProvider()
    request = LLMRequest(
        system_prompt="system",
        user_message="hello",
        state_context={"mood": "focused", "affection": 3},
    )

    response = provider.generate(request)

    assert response.text


def test_mock_llm_provider_accepts_conversation_history_none():
    provider = MockLLMProvider()
    request = LLMRequest(
        system_prompt="system",
        user_message="hello",
        conversation_history=None,
    )

    response = provider.generate(request)

    assert response.text


def test_mock_llm_provider_accepts_conversation_history_list():
    provider = MockLLMProvider()
    request = LLMRequest(
        system_prompt="system",
        user_message="hello",
        conversation_history=[
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ],
    )

    response = provider.generate(request)

    assert response.text


def test_mock_llm_response_can_map_to_chat_response_like_dict():
    response = generate_for_mode("project")

    chat_like = {
        "reply": response.text,
        "mood": "focused",
        "source": response.provider or "mock",
    }

    assert set(chat_like.keys()) == {"reply", "mood", "source"}
    assert chat_like["reply"]
    assert chat_like["mood"] == "focused"
    assert chat_like["source"] == "mock"
