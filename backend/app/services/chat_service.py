from dataclasses import asdict, dataclass, is_dataclass
from typing import Any

from app.core.config import get_llm_chat_enabled, get_llm_fallback_to_mock
from app.llm.factory import get_llm_provider
from app.llm.mock_provider import MockLLMProvider
from app.llm.real_provider import CANONICAL_SAFE_FALLBACK_TEXT
from app.llm.types import LLMRequest, LLMResponse
from app.services.character_service import format_mock_reply, select_mock_mood
from app.services.prompt_service import build_character_prompt, normalize_chat_mode


@dataclass(frozen=True)
class ChatStateContext:
    current_mood: str
    interaction_count: int
    familiarity: int
    affection: int
    trust: int


def _context_value(
    state_context: ChatStateContext | dict[str, Any],
    key: str,
    default: Any,
) -> Any:
    if isinstance(state_context, dict):
        return state_context.get(key, default)
    return getattr(state_context, key, default)


def _apply_state_context(
    reply: str,
    mode: str,
    state_context: ChatStateContext | dict[str, Any] | None,
) -> str:
    if state_context is None:
        return reply

    interaction_count = _context_value(state_context, "interaction_count", 0)
    familiarity = _context_value(state_context, "familiarity", 0)
    affection = _context_value(state_context, "affection", 0)
    trust = _context_value(state_context, "trust", 0)

    if mode == "support" and affection >= 3:
        return f"I'll keep this steady with you. {reply}"
    if mode in ("project", "debug") and trust >= 3:
        return f"We can move straight to the useful check. {reply}"
    if familiarity >= 5:
        return f"This is familiar ground now. {reply}"
    if interaction_count >= 5:
        return f"We have been working on this for a bit. {reply}"
    return reply


def generate_mock_chat_reply(
    message: str,
    mode: str | None = None,
    state_context: ChatStateContext | dict[str, Any] | None = None,
) -> dict[str, str]:
    """
    Generate a mock chat response without external AI, database, or memory.
    """
    chat_mode = normalize_chat_mode(mode)
    _prompt = build_character_prompt(chat_mode)

    mood = select_mock_mood(message)
    reply = format_mock_reply(message, mood, chat_mode)
    if message.strip():
        reply = _apply_state_context(reply, chat_mode, state_context)

    return {
        "reply": reply,
        "mood": mood,
        "source": "mock",
    }


def _state_context_for_llm(
    state_context: ChatStateContext | dict[str, Any] | None,
) -> dict[str, Any] | None:
    if state_context is None:
        return None
    if isinstance(state_context, dict):
        return state_context
    if is_dataclass(state_context):
        return asdict(state_context)
    return {
        "current_mood": _context_value(state_context, "current_mood", ""),
        "interaction_count": _context_value(state_context, "interaction_count", 0),
        "familiarity": _context_value(state_context, "familiarity", 0),
        "affection": _context_value(state_context, "affection", 0),
        "trust": _context_value(state_context, "trust", 0),
    }


def _source_for_llm_response(provider: Any, response: LLMResponse) -> str:
    provider_name = getattr(provider, "provider_name", response.provider)
    if isinstance(provider, MockLLMProvider) or provider_name == "mock":
        return "llm_mock"
    return "llm_real"


def _safe_llm_fallback_response(
    message: str,
    mode: str,
    state_context: ChatStateContext | dict[str, Any] | None,
    provider: Any,
) -> dict[str, str]:
    if get_llm_fallback_to_mock():
        return generate_mock_chat_reply(message, mode, state_context)

    provider_name = getattr(provider, "provider_name", "")
    source = "llm_mock" if provider_name == "mock" else "llm_real_error"
    return {
        "reply": CANONICAL_SAFE_FALLBACK_TEXT,
        "mood": select_mock_mood(message),
        "source": source,
    }


def generate_chat_reply(
    message: str,
    mode: str | None = None,
    state_context: ChatStateContext | dict[str, Any] | None = None,
    memory_context: str | None = None,
) -> dict[str, str]:
    """
    Generate a chat reply through the existing mock flow by default.

    TASK-040: LLM adapter use is gated by LLM_CHAT_ENABLED. When disabled,
    behavior remains identical to generate_mock_chat_reply. When enabled, the
    request is normalized through LLMRequest and provider output is mapped back
    to the stable reply/mood/source response shape.
    """
    chat_mode = normalize_chat_mode(mode)
    if not get_llm_chat_enabled():
        return generate_mock_chat_reply(message, chat_mode, state_context)

    provider = get_llm_provider()
    llm_request = LLMRequest(
        system_prompt=build_character_prompt(chat_mode),
        user_message=message,
        mode=chat_mode,
        memory_context=memory_context,
        state_context=_state_context_for_llm(state_context),
        conversation_history=None,
    )

    try:
        llm_response = provider.generate(llm_request)
    except Exception:
        return _safe_llm_fallback_response(message, chat_mode, state_context, provider)

    if llm_response.error or not llm_response.text.strip():
        return _safe_llm_fallback_response(message, chat_mode, state_context, provider)

    return {
        "reply": llm_response.text,
        "mood": select_mock_mood(message),
        "source": _source_for_llm_response(provider, llm_response),
    }
