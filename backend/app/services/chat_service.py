from dataclasses import asdict, dataclass, is_dataclass
from typing import Any

from app.core.config import get_llm_chat_enabled, get_llm_fallback_to_mock
from app.llm.factory import get_llm_provider, get_llm_provider_from_runtime_settings
from app.llm.mock_provider import MockLLMProvider
from app.llm.real_provider import CANONICAL_SAFE_FALLBACK_TEXT
from app.llm.types import LLMRequest, LLMResponse
from app.services.character_service import format_mock_reply, select_mock_mood
from app.services.prompt_service import build_character_prompt, normalize_chat_mode
from app.services.provider_settings_service import get_runtime_provider_settings


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


_LOCAL_PROVIDER_NAMES = frozenset({"ollama"})
LOCAL_PROVIDER_TIMEOUT_FALLBACK_TEXT = (
    "Local Ollama timed out. The model may still be loading or waking up; "
    "wait a moment and try again."
)
_HARSH_DEBUG_REPLY_PATTERNS = (
    "又想試吾的耐心",
    "先說清楚是哪段語音",
    "唾岫",
    "曄??",
)
_REPEATED_ADDRESS_PHRASES = ("汝這傢伙", "瘙")
_STT_DEBUG_TERMS = (
    "stt",
    "speech",
    "transcript",
    "finaltranscript",
    "no-speech",
    "語音辨識",
    "隤颲刻",
)
_CONVERSATION_DEBUG_TERMS = (
    "conversation mode",
    "conversation",
    "history",
    "turn",
    "pending",
    "activeturnid",
    "queue",
    "漏掉",
    "瞍",
)
_GENERIC_DEBUG_TERMS = (
    "diagnostics",
    "log",
    "git status",
    "validation",
    "runtime smoke",
    "有沒有問題",
    "收尾",
    "測試",
    "失敗",
    "嗅偏",
)


def _source_for_llm_response(provider: Any, response: LLMResponse) -> str:
    provider_name = getattr(provider, "provider_name", response.provider)
    if isinstance(provider, MockLLMProvider) or provider_name == "mock":
        return "llm_mock"
    if provider_name in _LOCAL_PROVIDER_NAMES:
        return "llm_local"
    return "llm_real"


def _provider_name(provider: Any, response: LLMResponse | None = None) -> str:
    if response is not None and response.provider:
        return response.provider
    return str(getattr(provider, "provider_name", "") or "")


def _provider_model(provider: Any, response: LLMResponse | None = None) -> str | None:
    if response is not None and response.model:
        return response.model
    model = getattr(provider, "model", None)
    if isinstance(model, str) and model.strip():
        return model.strip()
    private_model = getattr(provider, "_model", None)
    if isinstance(private_model, str) and private_model.strip():
        return private_model.strip()
    return None


def _has_known_harsh_debug_reply(reply: str) -> bool:
    normalized_reply = reply.lower()
    if any(pattern.lower() in normalized_reply for pattern in _HARSH_DEBUG_REPLY_PATTERNS):
        return True
    return any(reply.count(phrase) >= 2 for phrase in _REPEATED_ADDRESS_PHRASES)


def _message_matches_any(message: str, terms: tuple[str, ...]) -> bool:
    normalized_message = message.lower()
    return any(term.lower() in normalized_message for term in terms)


def _safe_debug_fallback_reply(message: str) -> str:
    if _message_matches_any(message, _STT_DEBUG_TERMS):
        return (
            "哼，吾先判斷為 NEEDS EVIDENCE。貼出 STT 模型、finalTranscript、"
            "no-speech guard、audio voice evidence，吾才能確認語音辨識是否正常。"
        )
    if _message_matches_any(message, _CONVERSATION_DEBUG_TERMS):
        return (
            "這句有進來。若要確認沒有漏句，要看 conversation history 的 turn "
            "是否連續，並確認 pending、activeTurnId、queue action。"
        )
    if _message_matches_any(message, _GENERIC_DEBUG_TERMS):
        return (
            "目前只能說 NEEDS EVIDENCE。把 diagnostics、log、git status 貼出來，"
            "吾會從 STT、queue、chat 三層拆。"
        )
    return (
        "哼，目前只能說 NEEDS EVIDENCE。把最近的 diagnostics 或 log 貼出來，"
        "吾再替汝判斷下一步。"
    )


def repair_persona_debug_reply(reply: str, message: str) -> str:
    """
    Narrow TASK-PERSONA-001 repair for known harsh/evasive debug templates.

    This intentionally does not sanitize normal tsundere flavor. It only replaces
    replies that match known bad patterns or excessive repeated address phrases.
    """
    if not _has_known_harsh_debug_reply(reply):
        return reply
    return _safe_debug_fallback_reply(message)


def _with_usage_metadata(
    response: dict[str, str],
    *,
    include_usage_metadata: bool,
    provider: str | None = None,
    model: str | None = None,
    fallback_used: bool = False,
    error_category: str | None = None,
) -> dict[str, Any]:
    if not include_usage_metadata:
        return response
    enriched: dict[str, Any] = dict(response)
    enriched["_usage"] = {
        "provider": provider,
        "model": model,
        "fallback_used": fallback_used,
        "error_category": error_category,
    }
    return enriched


def _safe_llm_fallback_response(
    message: str,
    mode: str,
    state_context: ChatStateContext | dict[str, Any] | None,
    provider: Any,
    *,
    llm_response: LLMResponse | None = None,
    fallback_to_mock: bool | None = None,
    error_category: str | None = None,
    include_usage_metadata: bool = False,
) -> dict[str, Any]:
    should_fallback_to_mock = (
        get_llm_fallback_to_mock()
        if fallback_to_mock is None
        else fallback_to_mock
    )
    provider_name = _provider_name(provider, llm_response) or None
    provider_model = _provider_model(provider, llm_response)

    if should_fallback_to_mock:
        response = generate_mock_chat_reply(message, mode, state_context)
        return _with_usage_metadata(
            response,
            include_usage_metadata=include_usage_metadata,
            provider=provider_name,
            model=provider_model,
            fallback_used=True,
            error_category=error_category,
        )

    provider_name = getattr(provider, "provider_name", "")
    if provider_name == "mock":
        source = "llm_mock"
    elif provider_name in _LOCAL_PROVIDER_NAMES:
        source = "llm_local_error"
    else:
        source = "llm_real_error"
    reply = CANONICAL_SAFE_FALLBACK_TEXT
    if provider_name in _LOCAL_PROVIDER_NAMES and error_category == "provider_timeout":
        reply = LOCAL_PROVIDER_TIMEOUT_FALLBACK_TEXT
    response = {
        "reply": reply,
        "mood": select_mock_mood(message),
        "source": source,
    }
    return _with_usage_metadata(
        response,
        include_usage_metadata=include_usage_metadata,
        provider=provider_name or None,
        model=provider_model,
        fallback_used=False,
        error_category=error_category,
    )


def generate_chat_reply(
    message: str,
    mode: str | None = None,
    state_context: ChatStateContext | dict[str, Any] | None = None,
    memory_context: str | None = None,
    *,
    include_usage_metadata: bool = False,
) -> dict[str, Any]:
    """
    Generate a chat reply through the existing mock flow by default.

    TASK-040: LLM adapter use is gated by LLM_CHAT_ENABLED. When disabled,
    behavior remains identical to generate_mock_chat_reply. When enabled, the
    request is normalized through LLMRequest and provider output is mapped back
    to the stable reply/mood/source response shape.
    """
    chat_mode = normalize_chat_mode(mode)
    runtime_settings = get_runtime_provider_settings()
    use_runtime_settings = bool(runtime_settings.get("runtime_overridden"))
    fallback_to_mock: bool | None = None

    if use_runtime_settings:
        if not runtime_settings.get("llm_chat_enabled"):
            response = generate_mock_chat_reply(message, chat_mode, state_context)
            return _with_usage_metadata(
                response,
                include_usage_metadata=include_usage_metadata,
                provider="mock",
                model=None,
            )

        resolved_provider = str(runtime_settings.get("resolved_provider") or "mock")
        if resolved_provider == "mock":
            response = generate_mock_chat_reply(message, chat_mode, state_context)
            return _with_usage_metadata(
                response,
                include_usage_metadata=include_usage_metadata,
                provider="mock",
                model=None,
            )

        provider = get_llm_provider_from_runtime_settings(runtime_settings)
        fallback_to_mock = bool(runtime_settings.get("fallback_to_mock"))
    else:
        if not get_llm_chat_enabled():
            response = generate_mock_chat_reply(message, chat_mode, state_context)
            return _with_usage_metadata(
                response,
                include_usage_metadata=include_usage_metadata,
                provider="mock",
                model=None,
            )

        provider = get_llm_provider()
    llm_request = LLMRequest(
        system_prompt=build_character_prompt(chat_mode, user_message=message),
        user_message=message,
        mode=chat_mode,
        memory_context=memory_context,
        state_context=_state_context_for_llm(state_context),
        conversation_history=None,
    )

    try:
        llm_response = provider.generate(llm_request)
    except Exception:
        return _safe_llm_fallback_response(
            message,
            chat_mode,
            state_context,
            provider,
            fallback_to_mock=fallback_to_mock,
            error_category="provider_error",
            include_usage_metadata=include_usage_metadata,
        )

    if llm_response.error or not llm_response.text.strip():
        return _safe_llm_fallback_response(
            message,
            chat_mode,
            state_context,
            provider,
            llm_response=llm_response,
            fallback_to_mock=fallback_to_mock,
            error_category=llm_response.error or "invalid_response",
            include_usage_metadata=include_usage_metadata,
        )

    repaired_reply = repair_persona_debug_reply(llm_response.text, message)
    response = {
        "reply": repaired_reply,
        "mood": select_mock_mood(message),
        "source": _source_for_llm_response(provider, llm_response),
    }
    return _with_usage_metadata(
        response,
        include_usage_metadata=include_usage_metadata,
        provider=_provider_name(provider, llm_response) or None,
        model=_provider_model(provider, llm_response),
        fallback_used=False,
        error_category=None,
    )
