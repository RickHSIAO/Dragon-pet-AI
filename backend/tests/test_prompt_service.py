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
    assert "project mode" in prompt


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
