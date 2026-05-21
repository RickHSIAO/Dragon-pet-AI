from app.services.prompt_service import (
    APPROVED_MEMORY_REFERENCE_INSTRUCTION,
    build_character_prompt,
    format_approved_memory_context,
    normalize_chat_mode,
)


def test_normalize_chat_mode_none_uses_safe_fallback():
    assert normalize_chat_mode(None) == "casual"


def test_normalize_chat_mode_debug_is_supported():
    assert normalize_chat_mode("debug") == "debug"


def test_normalize_chat_mode_unknown_falls_back():
    assert normalize_chat_mode("unknown") == "casual"


def test_build_character_prompt_project_returns_non_empty_string():
    prompt = build_character_prompt("project")

    assert isinstance(prompt, str)
    assert prompt
    # Prompt must reference the project mode — now encoded in Chinese.
    assert "project" in prompt


# ---------------------------------------------------------------------------
# TASK-075G — Persona injection tests
# ---------------------------------------------------------------------------

def test_all_modes_include_character_name():
    """Every prompt must include 克莉絲蒂娜 so the LLM knows the character."""
    for mode in ("casual", "project", "debug", "support", "reminder"):
        prompt = build_character_prompt(mode)
        assert "克莉絲蒂娜" in prompt, f"mode={mode!r}: '克莉絲蒂娜' not in prompt"


def test_all_modes_include_first_person_pronoun():
    """Every prompt must define the self-reference pronoun 吾."""
    for mode in ("casual", "project", "debug", "support", "reminder"):
        prompt = build_character_prompt(mode)
        assert "吾" in prompt, f"mode={mode!r}: '吾' not in prompt"


def test_all_modes_include_second_person_pronoun():
    """Every prompt must define the user-reference pronoun 汝."""
    for mode in ("casual", "project", "debug", "support", "reminder"):
        prompt = build_character_prompt(mode)
        assert "汝" in prompt, f"mode={mode!r}: '汝' not in prompt"


def test_all_modes_specify_traditional_chinese():
    """Every prompt must instruct the LLM to use Traditional Chinese."""
    for mode in ("casual", "project", "debug", "support", "reminder"):
        prompt = build_character_prompt(mode)
        assert "繁體中文" in prompt, f"mode={mode!r}: '繁體中文' not in prompt"


def test_casual_prompt_includes_tsundere_cue():
    """Casual prompt should explicitly carry the tsundere /傲嬌 style."""
    prompt = build_character_prompt("casual")
    assert "傲嬌" in prompt


def test_debug_prompt_is_accuracy_focused():
    """Debug prompt should emphasise accuracy / debug behavior."""
    prompt = build_character_prompt("debug")
    assert "debug" in prompt.lower()


def test_ollama_payload_system_message_contains_persona(monkeypatch):
    """
    End-to-end check: when generate_chat_reply is called with LLM_CHAT_ENABLED,
    the system message sent to the fake Ollama client must contain the
    克莉絲蒂娜 persona keywords.
    """
    from app.llm.ollama_provider import OllamaLocalProvider
    from app.llm.real_provider import ProviderHTTPResponse
    from app.services.chat_service import generate_chat_reply

    captured: list[dict] = []

    class CapturingHTTPClient:
        def request_json(self, method, url, headers, payload, timeout_seconds):
            captured.append(payload)
            # Return a valid Ollama response so the service doesn't error out.
            return ProviderHTTPResponse(
                status_code=200,
                json_data={
                    "model": "qwen3:8b",
                    "message": {"role": "assistant", "content": "吾知道了。"},
                    "done": True,
                    "eval_count": 5,
                    "prompt_eval_count": 30,
                },
            )

    fake_provider = OllamaLocalProvider(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        http_client=CapturingHTTPClient(),
    )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: fake_provider,
    )

    generate_chat_reply("稱讚我一下", mode="casual")

    assert len(captured) == 1, "Expected exactly one HTTP call — no retries"
    payload = captured[0]

    messages = payload.get("messages", [])
    assert len(messages) >= 2, "Expected at least system + user messages"

    system_msg = messages[0]
    assert system_msg["role"] == "system"
    system_content = system_msg["content"]

    assert "克莉絲蒂娜" in system_content, "Persona name missing from system prompt"
    assert "吾" in system_content, "Self-reference pronoun missing from system prompt"
    assert "汝" in system_content, "User-reference pronoun missing from system prompt"
    assert "繁體中文" in system_content, "Language instruction missing from system prompt"

    user_msg = messages[1]
    assert user_msg["role"] == "user"
    assert "稱讚" in user_msg["content"]


def test_format_approved_memory_context_empty_list_returns_empty_string():
    assert format_approved_memory_context([]) == ""


def test_format_approved_memory_context_includes_delimiter():
    context = format_approved_memory_context(["User prefers Traditional Chinese."])

    assert "<approved_manual_memory_context>" in context
    assert "</approved_manual_memory_context>" in context
    assert "<memory_entry>User prefers Traditional Chinese.</memory_entry>" in context


def test_format_approved_memory_context_includes_reference_only_instruction():
    context = format_approved_memory_context(["Project is TASK-018."])

    assert APPROVED_MEMORY_REFERENCE_INSTRUCTION in context
    assert "reference facts only" in context


def test_format_approved_memory_context_escapes_xml_like_characters():
    context = format_approved_memory_context(["Use A < B & C > D"])

    assert "<memory_entry>Use A &lt; B &amp; C &gt; D</memory_entry>" in context
    assert "Use A < B & C > D" not in context


def test_format_approved_memory_context_does_not_include_raw_metadata():
    context = format_approved_memory_context(["Plain memory content"])

    assert "Plain memory content" in context
    assert "id=" not in context
    assert "importance=" not in context
    assert "confidence=" not in context
