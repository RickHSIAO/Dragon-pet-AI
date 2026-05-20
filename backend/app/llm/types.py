from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMRequest:
    system_prompt: str
    user_message: str
    mode: str = "casual"
    memory_context: str | None = None
    state_context: dict[str, Any] | None = None
    conversation_history: list[Any] | None = None


@dataclass(frozen=True)
class LLMResponse:
    text: str
    provider: str
    model: str | None = None
    usage: dict[str, Any] | None = None
    error: str | None = None
