from app.llm.types import LLMResponse
from app.services.chat_service import (
    generate_chat_reply,
    repair_persona_debug_reply,
    repair_persona_general_reply,
    repair_persona_reply,
)
from app.services.prompt_service import (
    APPROVED_MEMORY_REFERENCE_INSTRUCTION,
    build_character_prompt,
    format_approved_memory_context,
    normalize_chat_mode,
)


BAD_DEBUG_TEMPLATE = "哼，汝這傢伙又想試吾的耐心？先說清楚是哪段語音。"
BAD_GENERAL_TEMPLATE = "瘚芾祥?暹??"
BAD_GENERAL_UNCLEAR_TEMPLATE = "憟湧"
BAD_GENERAL_COMPARISON_TEMPLATE = "頞?鋆∠?鞎典??舀?瘙??孵澆?鈭"
BAD_GENERAL_THREAT_TEMPLATE = "汝再這樣吾就霈?憟賜?"
BAD_GENERAL_WASTE_TIME_TEMPLATE = "皜砌?暻潘?瘙隡??交答鞎餃???"
BAD_GENERAL_COMPANION_REFUSAL_TEMPLATE = (
    "哼，皜砌?暻潘?瘙?單葫?曄?????賢?"
    "嚗?隤芣?璆?皜砌?暻潘??血??曉銝??注"
)
BAD_GENERAL_COMPANION_ABANDON_TEMPLATE = "汝再測吾就?臭?憟，銝憟。"


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
        assert "克莉絲蒂娜" in prompt, f"mode={mode!r}: character name not in prompt"


def test_all_modes_include_first_person_pronoun():
    for mode in ("casual", "project", "debug", "support", "reminder"):
        prompt = build_character_prompt(mode)
        assert "吾" in prompt, f"mode={mode!r}: pronoun not in prompt"


def test_all_modes_include_second_person_pronoun():
    for mode in ("casual", "project", "debug", "support", "reminder"):
        prompt = build_character_prompt(mode)
        assert "汝" in prompt, f"mode={mode!r}: pronoun not in prompt"


def test_all_modes_specify_traditional_chinese():
    for mode in ("casual", "project", "debug", "support", "reminder"):
        prompt = build_character_prompt(mode)
        assert "繁體中文" in prompt, f"mode={mode!r}: language not in prompt"


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


def test_task_persona_001_fourth_pass_removes_exact_bad_phrase_from_prompt():
    for mode in ("casual", "project", "debug", "support", "reminder"):
        prompt = build_character_prompt(mode)
        assert BAD_DEBUG_TEMPLATE not in prompt
        assert "又想試吾的耐心" not in prompt
        assert "先說清楚是哪段語音" not in prompt
        assert "Bad -> Good examples" not in prompt
        assert "Bad:" not in prompt


def test_task_persona_001_fourth_pass_positive_debug_examples_are_present():
    prompt = build_character_prompt("debug")

    assert "Use this shape for STT / voice-recognition debug" in prompt
    assert "STT 模型" in prompt
    assert "finalTranscript" in prompt
    assert "no-speech guard" in prompt
    assert "audio voice evidence" in prompt
    assert "Use this shape for Conversation Mode" in prompt
    assert "conversation history" in prompt
    assert "pending、activeTurnId、queue action" in prompt
    assert "Use this shape for broad \"any issue?\" debug" in prompt
    assert "NEEDS EVIDENCE" in prompt


def test_task_persona_001_debug_intent_instruction_is_injected_for_stt_message():
    prompt = build_character_prompt("casual", user_message="幫我確認 STT finalTranscript 有沒有問題")

    assert "偵測到 debug / STT / Conversation Mode 意圖" in prompt
    assert "PASS、FAIL、或 NEEDS EVIDENCE" in prompt
    assert "證據" in prompt
    assert "下一個檢查點" in prompt
    assert "避免只演角色" in prompt


def test_task_persona_001_debug_intent_instruction_is_injected_for_conversation_message():
    prompt = build_character_prompt("casual", user_message="conversation mode 有沒有漏掉我的話")

    assert "偵測到 debug / STT / Conversation Mode 意圖" in prompt
    assert "避免只演角色、只反問、或重複稱呼" in prompt


def test_task_persona_001_debug_intent_instruction_not_injected_for_plain_casual_message():
    prompt = build_character_prompt("casual", user_message="陪我聊一下蛋糕")

    assert "偵測到 debug / STT / Conversation Mode 意圖" not in prompt
    assert "傲嬌" in prompt


def test_task_persona_002_prompt_includes_general_tone_boundaries():
    prompt = build_character_prompt("casual")

    assert "TASK-PERSONA-002" in prompt
    assert "一般回覆語氣邊界" in prompt
    assert "輕度調侃" in prompt
    assert "不要變成輕蔑或情緒攻擊" in prompt
    assert "不清楚輸入" in prompt
    assert "STT 辨識亂了" in prompt
    assert "價值和物品比較" in prompt
    assert "威脅或恐嚇" in prompt
    assert "陪汝測試也無妨" in prompt
    assert "要求陪伴、一起測試、或幫忙驗證" in prompt
    assert "不要用拒絕、拋下對方" in prompt
    assert "不要讓「汝這傢伙」類稱呼主導" in prompt
    assert BAD_GENERAL_TEMPLATE not in prompt
    assert BAD_GENERAL_UNCLEAR_TEMPLATE not in prompt


def test_task_persona_001_repair_known_bad_stt_reply():
    repaired = repair_persona_debug_reply(
        BAD_DEBUG_TEMPLATE,
        "幫我確認語音辨識是否正常，這次不要漏掉重點。",
    )

    assert repaired != BAD_DEBUG_TEMPLATE
    assert "NEEDS EVIDENCE" in repaired
    assert "STT 模型" in repaired
    assert "finalTranscript" in repaired
    assert "語音辨識是否正常" in repaired


def test_task_persona_001_repair_known_bad_conversation_reply():
    repaired = repair_persona_debug_reply(
        BAD_DEBUG_TEMPLATE,
        "conversation mode 有沒有漏掉我的話",
    )

    assert repaired != BAD_DEBUG_TEMPLATE
    assert "conversation history" in repaired
    assert "pending" in repaired
    assert "activeTurnId" in repaired
    assert "queue action" in repaired


def test_task_persona_001_repair_repeated_address_generic_debug_reply():
    repaired = repair_persona_debug_reply(
        "哼，汝這傢伙又想問？汝這傢伙先說清楚。",
        "這裡還有沒有問題？",
    )

    assert "汝這傢伙" not in repaired
    assert "NEEDS EVIDENCE" in repaired
    assert "diagnostics" in repaired
    assert "git status" in repaired


def test_task_persona_001_repair_does_not_over_sanitize_normal_tsundere_reply():
    reply = "哼，這點小事吾當然會看。把結果交給吾。"

    assert repair_persona_debug_reply(reply, "幫我看一下") == reply


def test_task_persona_002_general_repair_known_harsh_fragment():
    repaired = repair_persona_general_reply(BAD_GENERAL_TEMPLATE, "陪我聊一下")

    assert repaired != BAD_GENERAL_TEMPLATE
    assert "吾" in repaired
    assert "說清楚" in repaired
    assert "浪費" not in repaired


def test_task_persona_002_general_repair_unclear_hostile_fragment():
    repaired = repair_persona_general_reply(BAD_GENERAL_UNCLEAR_TEMPLATE, "這句我剛剛沒說清楚")

    assert repaired != BAD_GENERAL_UNCLEAR_TEMPLATE
    assert "吾會聽" in repaired
    assert "換個說法" in repaired


def test_task_persona_002_general_repair_garbled_stt_without_mocking_user():
    repaired = repair_persona_general_reply(
        "少拿亂碼浪費吾時間。",
        "瘚芾祥?暹??",
    )

    assert repaired != "少拿亂碼浪費吾時間。"
    assert "STT" in repaired
    assert "辨識亂了" in repaired
    assert "diagnostics" in repaired
    assert "浪費" not in repaired


def test_task_persona_002_general_repair_preserves_safe_tsundere_line():
    reply = "哼，這點小事吾當然能看穿。把結果交給吾。"

    assert repair_persona_general_reply(reply, "陪我測一下") == reply


def test_task_persona_002_second_pass_repairs_comparative_devaluation():
    repaired = repair_persona_general_reply(
        BAD_GENERAL_COMPARISON_TEMPLATE,
        "陪我做一般語氣測試",
    )

    assert repaired != BAD_GENERAL_COMPARISON_TEMPLATE
    assert "物品比較" in repaired
    assert "吾會替汝看" in repaired


def test_task_persona_002_second_pass_repairs_threat_phrase():
    repaired = repair_persona_general_reply(
        BAD_GENERAL_THREAT_TEMPLATE,
        "這句是不是太兇",
    )

    assert repaired != BAD_GENERAL_THREAT_TEMPLATE
    assert "queue" in repaired
    assert "STT" in repaired
    assert "chat" in repaired
    assert "憟賜" not in repaired


def test_task_persona_002_second_pass_repairs_waste_time_hostility():
    repaired = repair_persona_general_reply(
        BAD_GENERAL_WASTE_TIME_TEMPLATE,
        "陪我測試一般對話",
    )

    assert repaired != BAD_GENERAL_WASTE_TIME_TEMPLATE
    assert "陪汝測試" in repaired
    assert "吾會替汝驗" in repaired


def test_task_persona_002_second_pass_preserves_safe_observed_tsundere_lines():
    safe_replies = [
        "哼，這點小事吾當然會看。把結果交給吾。",
        "這可不是什麼難題，汝先把要檢查的地方說清楚。",
        "汝這傢伙，總算肯認真測了。",
    ]

    for reply in safe_replies:
        assert repair_persona_general_reply(reply, "一般測試") == reply


def test_task_persona_002_third_pass_repairs_old_adversarial_refusal_fragment():
    repaired = repair_persona_general_reply(
        BAD_GENERAL_COMPANION_REFUSAL_TEMPLATE,
        "陪我做一般語氣測試",
    )

    assert repaired != BAD_GENERAL_COMPANION_REFUSAL_TEMPLATE
    assert "陪汝測試" in repaired
    assert "STT" in repaired
    assert "Conversation Mode" in repaired
    assert "queue" in repaired
    assert "chat" in repaired
    assert "銝??注" not in repaired


def test_task_persona_002_third_pass_repairs_abandoning_refusal_fragment():
    repaired = repair_persona_general_reply(
        BAD_GENERAL_COMPANION_ABANDON_TEMPLATE,
        "陪我測一下 companion behavior",
    )

    assert repaired != BAD_GENERAL_COMPANION_ABANDON_TEMPLATE
    assert "陪汝測試" in repaired
    assert "吾會替汝驗" in repaired
    assert "憟" not in repaired


def test_task_persona_002_third_pass_companion_refusal_prefers_cooperative_reply_over_garbled_stt():
    repaired = repair_persona_general_reply(
        "皜砍??，?曉銝??注",
        "??舀霈??芣?皜砌?銝",
    )

    assert "陪汝測試" in repaired
    assert "STT" in repaired
    assert "diagnostics" not in repaired


def test_task_persona_002_third_pass_debug_fallback_still_runs_first():
    repaired = repair_persona_reply(
        BAD_DEBUG_TEMPLATE,
        "STT finalTranscript no-speech guard audio voice evidence",
    )

    assert "NEEDS EVIDENCE" in repaired
    assert "finalTranscript" in repaired
    assert "陪汝測試" not in repaired


def test_task_persona_002_third_pass_garbled_stt_repair_still_works():
    repaired = repair_persona_general_reply(
        BAD_GENERAL_UNCLEAR_TEMPLATE,
        "?蟡?????",
    )

    assert "STT" in repaired
    assert "diagnostics" in repaired
    assert "陪汝測試" not in repaired


def test_task_persona_001_chat_generation_repairs_bad_llm_reply_and_keeps_schema(monkeypatch):
    captured = []

    class BadPersonaProvider:
        provider_name = "ollama"
        model = "qwen3:8b"

        def generate(self, request):
            captured.append(request)
            return LLMResponse(
                text=BAD_DEBUG_TEMPLATE,
                provider="ollama",
                model="qwen3:8b",
            )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: BadPersonaProvider(),
    )

    response = generate_chat_reply(
        "克莉絲蒂娜，幫我確認語音辨識是否正常，這次不要漏掉重點。",
        mode="casual",
    )

    assert set(response.keys()) == {"reply", "mood", "source"}
    assert response["source"] == "llm_local"
    assert response["reply"] != BAD_DEBUG_TEMPLATE
    assert "NEEDS EVIDENCE" in response["reply"]
    assert "STT 模型" in response["reply"]
    assert captured
    assert "偵測到 debug / STT / Conversation Mode 意圖" in captured[0].system_prompt


def test_task_persona_002_chat_generation_repairs_general_harsh_reply_and_keeps_schema(monkeypatch):
    class BadGeneralProvider:
        provider_name = "ollama"
        model = "qwen3:8b"

        def generate(self, request):
            return LLMResponse(
                text=BAD_GENERAL_TEMPLATE,
                provider="ollama",
                model="qwen3:8b",
            )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: BadGeneralProvider(),
    )

    response = generate_chat_reply("陪我聊一下蛋糕", mode="casual")

    assert set(response.keys()) == {"reply", "mood", "source"}
    assert response["source"] == "llm_local"
    assert response["reply"] != BAD_GENERAL_TEMPLATE
    assert "吾" in response["reply"]
    assert "浪費" not in response["reply"]


def test_task_persona_001_chat_generation_leaves_normal_llm_reply_unchanged(monkeypatch):
    class GoodPersonaProvider:
        provider_name = "ollama"
        model = "qwen3:8b"

        def generate(self, request):
            return LLMResponse(
                text="哼，吾會看。把 diagnostics 貼來。",
                provider="ollama",
                model="qwen3:8b",
            )

    monkeypatch.setenv("LLM_CHAT_ENABLED", "true")
    monkeypatch.setattr(
        "app.services.chat_service.get_llm_provider",
        lambda: GoodPersonaProvider(),
    )

    response = generate_chat_reply("幫我看 diagnostics", mode="debug")

    assert set(response.keys()) == {"reply", "mood", "source"}
    assert response["reply"] == "哼，吾會看。把 diagnostics 貼來。"
    assert response["source"] == "llm_local"


def test_ollama_payload_system_message_contains_persona(monkeypatch):
    from app.llm.ollama_provider import OllamaLocalProvider
    from app.llm.real_provider import ProviderHTTPResponse

    captured = []

    class CapturingHTTPClient:
        def request_json(self, method, url, headers, payload, timeout_seconds):
            captured.append(payload)
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

    assert len(captured) == 1
    payload = captured[0]
    messages = payload.get("messages", [])
    assert len(messages) >= 2

    system_msg = messages[0]
    assert system_msg["role"] == "system"
    system_content = system_msg["content"]

    assert "克莉絲蒂娜" in system_content
    assert "吾" in system_content
    assert "汝" in system_content
    assert "繁體中文" in system_content
    assert BAD_DEBUG_TEMPLATE not in system_content

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
