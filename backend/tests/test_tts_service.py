"""TASK-TTS-002 tests for the safe mock TTS skeleton."""

import os

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")

from app.core.config import get_tts_enabled, get_tts_provider_name, get_tts_voice  # noqa: E402
from app.tts.providers import MockTTSProvider, TTSSynthesisRequest  # noqa: E402
from app.tts.text_normalizer import normalize_tts_text  # noqa: E402
from app.tts.tts_service import TTSService, build_tts_preview, get_tts_diagnostics  # noqa: E402


def test_tts_config_defaults_disabled_mock(monkeypatch):
    monkeypatch.delenv("TTS_ENABLED", raising=False)
    monkeypatch.delenv("TTS_PROVIDER", raising=False)
    monkeypatch.delenv("TTS_VOICE", raising=False)

    assert get_tts_enabled() is False
    assert get_tts_provider_name() == "mock"
    assert get_tts_voice() == "christina_mock"


def test_tts_config_unknown_bool_fails_closed(monkeypatch):
    monkeypatch.setenv("TTS_ENABLED", "enabled")

    assert get_tts_enabled() is False


def test_normalize_tts_text_keeps_traditional_chinese_reply():
    chunks = normalize_tts_text("哼，汝總算知道要問吾了。這點小事，吾會幫汝處理！")

    assert chunks == ["哼，汝總算知道要問吾了。", "這點小事，吾會幫汝處理！"]


def test_normalize_tts_text_removes_markdown_code_fence():
    text = """
    這段吾會說。

    ```python
    print("不要朗讀這段程式碼")
    ```

    **完成後再提醒汝。**
    """

    chunks = normalize_tts_text(text)
    joined = " ".join(chunks)

    assert "不要朗讀這段程式碼" not in joined
    assert "print" not in joined
    assert "這段吾會說" in joined
    assert "完成後再提醒汝" in joined


def test_normalize_tts_text_removes_debug_diagnostics_and_paths():
    text = """
    吾已經收到回覆。
    Diagnostics: {"provider":"mock","audioPath":"C:\\temp\\secret.wav"}
    Source: llm_local
    Provider: stack trace hidden
    Owner Voice: score=0.12 threshold=0.8
    接下來只說安全內容。
    """

    chunks = normalize_tts_text(text)
    joined = " ".join(chunks)

    assert "Diagnostics" not in joined
    assert "C:\\temp\\secret.wav" not in joined
    assert "Owner Voice" not in joined
    assert "吾已經收到回覆" in joined
    assert "接下來只說安全內容" in joined


def test_normalize_tts_text_chunks_long_text_with_guard():
    text = "吾會先整理這件事，" * 20

    chunks = normalize_tts_text(text, max_chunk_chars=30, max_chunks=5)

    assert len(chunks) == 5
    assert all(0 < len(chunk) <= 30 for chunk in chunks)


def test_normalize_tts_text_empty_whitespace_returns_no_chunks():
    assert normalize_tts_text("   \n\t  ") == []
    assert normalize_tts_text(None) == []


def test_mock_provider_returns_metadata_only_no_audio():
    provider = MockTTSProvider()
    result = provider.synthesize(
        TTSSynthesisRequest(chunks=["哼。", "吾會處理！"], voice="christina_mock")
    )

    assert result.provider == "mock"
    assert result.voice == "christina_mock"
    assert result.chunks == ["哼。", "吾會處理！"]
    assert result.estimatedDurationMs > 0
    assert result.synthesisStatus == "mock_success"
    assert result.audioAvailable is False
    assert result.audioPath is None


def test_tts_service_diagnostics_default_disabled_queue_empty():
    diagnostics = get_tts_diagnostics()

    assert diagnostics["enabled"] is False
    assert diagnostics["provider"] == "mock"
    assert diagnostics["requestedVoice"] == "christina_mock"
    assert diagnostics["resolvedVoice"] == "christina_mock"
    assert diagnostics["queueLength"] == 0
    assert diagnostics["activeJobId"] is None
    assert diagnostics["chunksCount"] == 0
    assert diagnostics["lastSynthesisStatus"] == "not_started"
    assert diagnostics["lastError"] is None
    assert diagnostics["playbackStatus"] == "disabled"
    assert diagnostics["autoSpeakEnabled"] is False


def test_tts_service_preview_returns_mock_metadata_without_queueing():
    service = TTSService(enabled=False)
    preview = service.preview("吾會回答。不要讓聲音自己播放。")

    assert preview["enabled"] is False
    assert preview["provider"] == "mock"
    assert preview["voice"] == "christina_mock"
    assert preview["chunks"] == ["吾會回答。", "不要讓聲音自己播放。"]
    assert preview["chunksCount"] == 2
    assert preview["lastSynthesisStatus"] == "mock_success"
    assert preview["synthesisStatus"] == "mock_success"
    assert preview["queueLength"] == 0
    assert preview["activeJobId"] is None
    assert preview["playbackStatus"] == "disabled"
    assert preview["autoSpeakEnabled"] is False
    assert preview["audioAvailable"] is False
    assert preview["audioPath"] is None


def test_build_tts_preview_empty_reply_does_not_create_audio_or_queue():
    preview = build_tts_preview(" \n ")

    assert preview["chunks"] == []
    assert preview["chunksCount"] == 0
    assert preview["synthesisStatus"] == "empty"
    assert preview["queueLength"] == 0
    assert preview["audioAvailable"] is False
    assert preview["audioPath"] is None


def test_tts_service_enabled_flag_does_not_enable_auto_speak_or_playback():
    service = TTSService(enabled=True)
    preview = service.preview("就算旗標開了，TASK-TTS-002 也不播放。")

    assert preview["enabled"] is True
    assert preview["playbackStatus"] == "not_started"
    assert preview["autoSpeakEnabled"] is False
    assert preview["audioAvailable"] is False
    assert preview["queueLength"] == 0
