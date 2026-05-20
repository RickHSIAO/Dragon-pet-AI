from typing import Protocol

from app.llm.types import LLMRequest, LLMResponse


class LLMProvider(Protocol):
    @property
    def provider_name(self) -> str:
        ...

    def generate(self, request: LLMRequest) -> LLMResponse:
        ...

    def health_check(self) -> bool:
        return True
