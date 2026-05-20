from app.llm.types import LLMRequest, LLMResponse


class MockLLMProvider:
    @property
    def provider_name(self) -> str:
        return "mock"

    def generate(self, request: LLMRequest) -> LLMResponse:
        message = request.user_message.strip()
        mode = request.mode.strip().lower()

        if mode == "debug":
            text = "Mock debug reply: start with the exact error and smallest reproduction."
        elif mode == "project":
            text = "Mock project reply: define the next concrete step and verify it."
        elif mode == "support":
            text = "Mock support reply: I will stay calm and focus on the next manageable step."
        elif mode == "reminder":
            text = "Mock reminder reply: noted. I will keep the reminder concise."
        elif mode == "casual" and message:
            text = f"Mock reply received: {message}"
        elif message:
            text = "Mock reply ready."
        else:
            text = "Mock reply ready."

        return LLMResponse(
            text=text,
            provider=self.provider_name,
            model="mock-local",
            usage=None,
            error=None,
        )

    def health_check(self) -> bool:
        return True
