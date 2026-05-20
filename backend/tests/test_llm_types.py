from app.llm.types import LLMRequest, LLMResponse


def test_llm_request_can_be_created_with_required_fields():
    request = LLMRequest(
        system_prompt="You are Dragon Pet AI.",
        user_message="Hello",
    )

    assert request.system_prompt == "You are Dragon Pet AI."
    assert request.user_message == "Hello"


def test_llm_request_defaults_mode_to_casual():
    request = LLMRequest(
        system_prompt="You are Dragon Pet AI.",
        user_message="Hello",
    )

    assert request.mode == "casual"
    assert request.memory_context is None
    assert request.state_context is None
    assert request.conversation_history is None


def test_llm_response_can_be_created():
    response = LLMResponse(
        text="Hello",
        provider="mock",
        model="mock-local",
    )

    assert response.text == "Hello"
    assert response.provider == "mock"
    assert response.model == "mock-local"
    assert response.usage is None
    assert response.error is None
