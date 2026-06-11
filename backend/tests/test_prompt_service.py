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
    assert "project" in prompt


def test_all_modes_include_character_name():
    for mode in ("casual", "project", "debug", "support", "reminder"):
        prompt = build_character_prompt(mode)
        assert "\u514b\u8389\u7d72\u8482\u5a1c" in prompt, f"mode={mode!r}: character name not in prompt"


def test_all_modes_include_first_person_pronoun():
    for mode in ("casual", "project", "debug", "support", "reminder"):
        prompt = build_character_prompt(mode)
        assert "\u543e" in prompt, f"mode={mode!r}: pronoun not in prompt"


def test_all_modes_include_second_person_pronoun():
    for mode in ("casual", "project", "debug", "support", "reminder"):
        prompt = build_character_prompt(mode)
        assert "\u6c5d" in prompt, f"mode={mode!r}: pronoun not in prompt"


def test_all_modes_specify_traditional_chinese():
    for mode in ("casual", "project", "debug", "support", "reminder"):
        prompt = build_character_prompt(mode)
        assert "\u7e41\u9ad4\u4e2d\u6587" in prompt, f"mode={mode!r}: language not in prompt"


def test_casual_prompt_includes_tsundere_cue():
    prompt = build_character_prompt("casual")
    assert "\u50b2\u5b0c" in prompt


def test_debug_prompt_is_accuracy_focused():
    prompt = build_character_prompt("debug")
    assert "debug" in prompt.lower()


def test_task_persona_001_prompt_keeps_proud_tsundere_but_sets_tone_boundaries():
    prompt = build_character_prompt("casual")

    assert "TASK-PERSONA-001" in prompt
    assert "可愛地驕傲" in prompt
    assert "傲嬌" in prompt
    assert "嘴硬心軟" in prompt
    assert "普通客服" in prompt
    assert "辱罵型角色" in prompt


def test_task_persona_001_prompt_discourages_harsh_direct_insults():
    prompt = build_character_prompt("casual")

    assert "反覆直接羞辱" in prompt
    assert "hostile name-calling" in prompt
    assert "貶低使用者的能力或人格" in prompt
    assert "下賤的人類" not in prompt


def test_task_persona_001_debug_prompt_requires_cooperation():
    prompt = build_character_prompt("debug")

    assert "技術 / debugging / 測試情境" in prompt
    assert "合作且有效" in prompt
    assert "重現步驟" in prompt
    assert "錯誤訊息" in prompt
    assert "不要把測試訊息或驗證要求貶成沒意義" in prompt


def test_task_persona_001_prompt_has_bad_good_examples_without_brittle_output():
    prompt = build_character_prompt("support")

    assert "Bad -> Good examples" in prompt
    assert "無能之人" in prompt
    assert "把錯誤訊息、操作步驟、期望結果交給吾" in prompt
    assert "毫無價值" in prompt
    assert "先確認輸入，再看第一個偏離預期的位置" in prompt


def test_task_persona_001_second_pass_discourages_repeated_address_phrase():
    prompt = build_character_prompt("casual")

    assert "「汝這傢伙」只能少量" in prompt
    assert "非連續使用" in prompt
    assert "連續回覆使用同一個稱呼模板" in prompt
    assert "優先使用「汝」" in prompt
    assert "完全不加稱呼" in prompt


def test_task_persona_001_second_pass_debug_requires_direct_answer_evidence_next_check():
    prompt = build_character_prompt("debug")

    assert "先直接回答眼前問題" in prompt
    assert "需要的證據" in prompt
    assert "下一個檢查點" in prompt
    assert "PASS / FAIL / NEEDS EVIDENCE" in prompt
    assert "不要只反問" in prompt
    assert "turn history" in prompt
    assert "diagnostics" in prompt


def test_task_persona_001_second_pass_debug_examples_are_cooperative_not_dismissive():
    prompt = build_character_prompt("debug")

    assert "模型是否照設定跑" in prompt
    assert "Transcript 是否合理" in prompt
    assert "no-speech guard 有沒有誤判" in prompt
    assert "history 裡的 #1/#2/#3 turn 是否連續" in prompt
    assert "validation、runtime smoke、git status" in prompt
    assert "錄音、STT、queue，還是 chat" in prompt


def test_task_persona_001_second_pass_emotional_context_is_protective():
    prompt = build_character_prompt("support")

    assert "使用者說累" in prompt
    assert "不要叫對方懶、弱、沒用" in prompt
    assert "責備式開場" in prompt
    assert "吾會在這裡陪汝一會兒" in prompt
    assert "今天不用一次解決全部" in prompt


def test_ollama_payload_system_message_contains_persona(monkeypatch):
    from app.llm.ollama_provider import OllamaLocalProvider
    from app.llm.real_provider import ProviderHTTPResponse
    from app.services.chat_service import generate_chat_reply

    captured = []

    class CapturingHTTPClient:
        def request_json(self, method, url, headers, payload, timeout_seconds):
            captured.append(payload)
            return ProviderHTTPResponse(
                status_code=200,
                json_data={
                    "model": "qwen3:8b",
                    "message": {"role": "assistant", "content": "\u543e\u77e5\u9053\u4e86\u3002"},
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

    generate_chat_reply("\u7a31\u8b9a\u6211\u4e00\u4e0b", mode="casual")

    assert len(captured) == 1
    payload = captured[0]
    messages = payload.get("messages", [])
    assert len(messages) >= 2

    system_msg = messages[0]
    assert system_msg["role"] == "system"
    system_content = system_msg["content"]

    assert "\u514b\u8389\u7d72\u8482\u5a1c" in system_content
    assert "\u543e" in system_content
    assert "\u6c5d" in system_content
    assert "\u7e41\u9ad4\u4e2d\u6587" in system_content

    user_msg = messages[1]
    assert user_msg["role"] == "user"
    assert "\u7a31\u8b9a" in user_msg["content"]


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
