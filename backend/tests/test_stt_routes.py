"""
TASK-167B: Backend pytest tests for POST /stt/transcribe.

Tests are designed to pass whether or not faster-whisper is installed.
When STT is unavailable, the endpoint returns status="unavailable" (not an error).
"""

import io
import os

import pytest

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")
os.environ.setdefault("SETTINGS_FILE_PATH", "")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.stt import stt_service  # noqa: E402


# -- stt_service unit tests ---------------------------------------------------


def test_stt_service_empty_bytes_returns_empty_status():
    """transcribe_audio_bytes with empty bytes -> status='empty' regardless of Whisper."""
    result = stt_service.transcribe_audio_bytes(b"")
    assert result["transcript"] == ""
    assert result["status"] == "empty"


def test_stt_service_returns_dict_with_required_keys():
    """transcribe_audio_bytes always returns dict with 'transcript' and 'status'."""
    result = stt_service.transcribe_audio_bytes(b"\x00\x01\x02")
    assert "transcript" in result
    assert "status" in result
    assert isinstance(result["transcript"], str)
    assert result["status"] in ("ok", "unavailable", "empty", "error")


def test_stt_service_unavailable_when_no_whisper(monkeypatch):
    """When _WHISPER_AVAILABLE is False, service returns status='unavailable'."""
    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", False)
    stt_service._reset_model_for_tests()
    result = stt_service.transcribe_audio_bytes(b"fake audio data")
    assert result["status"] == "unavailable"
    assert result["transcript"] == ""


def test_stt_service_model_load_failure_returns_unavailable(monkeypatch):
    """If model loading raises, service returns status='unavailable'."""
    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()

    def _bad_load():
        return None

    monkeypatch.setattr(stt_service, "_load_model", _bad_load)
    result = stt_service.transcribe_audio_bytes(b"fake audio data")
    assert result["status"] == "unavailable"
    assert result["transcript"] == ""


def test_stt_service_model_transcribe_error_returns_error_status(monkeypatch):
    """If model.transcribe() raises, service returns status='error'."""

    class _BadModel:
        def transcribe(self, *_args, **_kwargs):
            raise RuntimeError("simulated whisper crash")

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _BadModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03")
    assert result["status"] == "error"
    assert result["transcript"] == ""


def test_stt_service_empty_transcript_returns_empty_status(monkeypatch):
    """If Whisper returns no speech, service returns status='empty'."""

    class _SilentModel:
        def transcribe(self, _buf, **_kwargs):
            return iter([]), None  # no segments -> empty transcript

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _SilentModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03")
    assert result["status"] == "empty"
    assert result["transcript"] == ""


def test_stt_service_ok_transcript(monkeypatch):
    """If Whisper returns text, service returns status='ok' with non-empty transcript."""
    from types import SimpleNamespace

    class _GoodModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(text="hello world")
            return iter([seg]), None

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _GoodModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03")
    assert result["status"] == "ok"
    assert result["transcript"] == "hello world"


# -- /stt/transcribe endpoint tests ------------------------------------------


def test_stt_transcribe_endpoint_exists():
    """POST /stt/transcribe must be reachable (not 404 or 405)."""
    with TestClient(app) as client:
        audio_bytes = b"fake webm data"
        response = client.post(
            "/stt/transcribe",
            files={"audio": ("audio.webm", io.BytesIO(audio_bytes), "audio/webm")},
        )
    assert response.status_code != 404, "POST /stt/transcribe must exist"
    assert response.status_code != 405, "POST /stt/transcribe must allow POST"


def test_stt_transcribe_returns_json_with_transcript_and_status():
    """Response body must contain 'transcript' (str) and 'status' (str)."""
    with TestClient(app) as client:
        audio_bytes = b"\x00\x01\x02\x03"
        response = client.post(
            "/stt/transcribe",
            files={"audio": ("audio.webm", io.BytesIO(audio_bytes), "audio/webm")},
        )
    assert response.status_code == 200
    data = response.json()
    assert "transcript" in data, "Response must contain 'transcript'"
    assert "status" in data, "Response must contain 'status'"
    assert isinstance(data["transcript"], str)
    assert data["status"] in ("ok", "unavailable", "empty", "error")


def test_stt_transcribe_empty_audio_returns_empty_or_unavailable():
    """Sending zero bytes returns status 'empty' or 'unavailable' -- never 'ok'."""
    with TestClient(app) as client:
        response = client.post(
            "/stt/transcribe",
            files={"audio": ("audio.webm", io.BytesIO(b""), "audio/webm")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("empty", "unavailable"), (
        "Empty audio must return 'empty' or 'unavailable', got %r" % data["status"]
    )


def test_stt_transcribe_no_audio_field_returns_422():
    """Missing 'audio' form field must return HTTP 422 (unprocessable)."""
    with TestClient(app) as client:
        response = client.post("/stt/transcribe")
    assert response.status_code == 422


def test_stt_transcribe_oversized_audio_returns_413(monkeypatch):
    """Audio exceeding limit must return HTTP 413."""
    import app.api.routes as routes_module

    original = routes_module._STT_MAX_BYTES
    monkeypatch.setattr(routes_module, "_STT_MAX_BYTES", 5)
    try:
        with TestClient(app) as client:
            big_audio = b"\x00" * 10  # 10 bytes > limit of 5
            response = client.post(
                "/stt/transcribe",
                files={"audio": ("audio.webm", io.BytesIO(big_audio), "audio/webm")},
            )
        assert response.status_code == 413
    finally:
        monkeypatch.setattr(routes_module, "_STT_MAX_BYTES", original)


def test_stt_transcribe_no_chat_forwarding(monkeypatch):
    """TASK-167B: /stt/transcribe must not call generate_chat_reply (TASK-167C boundary)."""
    import inspect
    import app.api.routes as routes_module

    source = inspect.getsource(routes_module.stt_transcribe)
    assert "generate_chat_reply" not in source, (
        "/stt/transcribe must not call generate_chat_reply (TASK-167C boundary)"
    )
    assert "chat_service" not in source, (
        "/stt/transcribe must not import chat_service (TASK-167C boundary)"
    )


def test_stt_service_no_audio_persistence():
    """TASK-167B privacy: stt_service must not write audio to disk."""
    import inspect

    source = inspect.getsource(stt_service)
    assert "open(" not in source, (
        "stt_service must not call open() -- audio must stay in-memory"
    )


# -- TASK-245: STT language lock tests ----------------------------------------


def test_stt_default_language_constant_exists():
    """TASK-245: routes module must expose _STT_DEFAULT_LANGUAGE constant."""
    import app.api.routes as routes_module

    assert hasattr(routes_module, "_STT_DEFAULT_LANGUAGE"), (
        "_STT_DEFAULT_LANGUAGE constant must exist in routes.py"
    )
    assert routes_module._STT_DEFAULT_LANGUAGE == "zh", (
        "_STT_DEFAULT_LANGUAGE must be 'zh'"
    )


def test_stt_default_task_constant_exists():
    """TASK-245: routes module must expose _STT_DEFAULT_TASK constant."""
    import app.api.routes as routes_module

    assert hasattr(routes_module, "_STT_DEFAULT_TASK"), (
        "_STT_DEFAULT_TASK constant must exist in routes.py"
    )
    assert routes_module._STT_DEFAULT_TASK == "transcribe", (
        "_STT_DEFAULT_TASK must be 'transcribe'"
    )


def test_stt_route_passes_language_to_transcribe(monkeypatch):
    """TASK-245: /stt/transcribe route must pass language='zh' to transcribe_audio_bytes."""
    import app.api.routes as routes_module

    captured_kwargs: dict = {}

    def _mock_transcribe(audio_bytes, mime_type="audio/webm", language=None):
        captured_kwargs["language"] = language
        return {"transcript": "test", "status": "ok"}

    monkeypatch.setattr(routes_module, "transcribe_audio_bytes", _mock_transcribe)
    with TestClient(app) as client:
        client.post(
            "/stt/transcribe",
            files={"audio": ("audio.webm", io.BytesIO(b"\x01\x02\x03"), "audio/webm")},
        )
    assert captured_kwargs.get("language") == "zh", (
        "Route must pass language='zh' to transcribe_audio_bytes, got %r" % captured_kwargs.get("language")
    )


def test_stt_route_response_includes_language_metadata():
    """TASK-245: /stt/transcribe response must include language/languageLocked/task fields."""
    with TestClient(app) as client:
        response = client.post(
            "/stt/transcribe",
            files={"audio": ("audio.webm", io.BytesIO(b"\x01\x02\x03"), "audio/webm")},
        )
    assert response.status_code == 200
    data = response.json()
    assert "language" in data, "Response must include 'language' field"
    assert data["language"] == "zh", "language must be 'zh'"
    assert "languageLocked" in data, "Response must include 'languageLocked' field"
    assert data["languageLocked"] is True, "languageLocked must be True"
    assert "task" in data, "Response must include 'task' field"
    assert data["task"] == "transcribe", "task must be 'transcribe'"


def test_stt_route_no_new_endpoint():
    """TASK-245: no new /stt/* endpoint added beyond /stt/transcribe."""
    import inspect
    import app.api.routes as routes_module

    source = inspect.getsource(routes_module)
    # Count /stt/ route decorators — must remain exactly 1
    stt_routes = [line for line in source.splitlines() if '"/stt/' in line]
    assert len(stt_routes) == 1, (
        "Only one /stt/ route allowed (TASK-245 restriction), found: %r" % stt_routes
    )


def test_stt_route_no_raw_audio_persistence():
    """TASK-245: /stt/transcribe handler must not write audio to disk."""
    import inspect
    import app.api.routes as routes_module

    source = inspect.getsource(routes_module.stt_transcribe)
    assert "open(" not in source, "stt_transcribe must not call open()"
    assert ".write(" not in source or "audio_bytes" not in source, (
        "stt_transcribe must not write audio_bytes to disk"
    )


def test_stt_service_provider_constant_exists():
    """TASK-245: stt_service must expose _STT_PROVIDER constant."""
    assert hasattr(stt_service, "_STT_PROVIDER"), (
        "_STT_PROVIDER must exist in stt_service"
    )
    assert isinstance(stt_service._STT_PROVIDER, str) and stt_service._STT_PROVIDER, (
        "_STT_PROVIDER must be a non-empty string"
    )


def test_stt_service_model_name_constant_exists():
    """TASK-245: stt_service must expose _STT_MODEL_NAME constant."""
    assert hasattr(stt_service, "_STT_MODEL_NAME"), (
        "_STT_MODEL_NAME must exist in stt_service"
    )
    assert isinstance(stt_service._STT_MODEL_NAME, str) and stt_service._STT_MODEL_NAME, (
        "_STT_MODEL_NAME must be a non-empty string"
    )


def test_stt_service_ok_includes_provider_metadata(monkeypatch):
    """TASK-245: ok response from transcribe_audio_bytes must include provider/model."""
    from types import SimpleNamespace

    class _GoodModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(text="你好")
            info = SimpleNamespace(language="zh")
            return iter([seg]), info

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _GoodModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert result["status"] == "ok"
    assert "provider" in result, "ok result must include 'provider'"
    assert "model" in result, "ok result must include 'model'"
    assert "detectedLanguage" in result, "ok result must include 'detectedLanguage'"
    assert result["detectedLanguage"] == "zh"


def test_stt_service_language_param_passed_to_whisper(monkeypatch):
    """TASK-245: language kwarg must be forwarded to model.transcribe."""
    from types import SimpleNamespace

    received_kwargs: dict = {}

    class _KwargsModel:
        def transcribe(self, _buf, **kwargs):
            received_kwargs.update(kwargs)
            seg = SimpleNamespace(text="test")
            info = SimpleNamespace(language=kwargs.get("language", "unknown"))
            return iter([seg]), info

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _KwargsModel())
    stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert received_kwargs.get("language") == "zh", (
        "language kwarg must be forwarded to model.transcribe, got: %r" % received_kwargs
    )


# -- TASK-246: STT Model Quality / Whisper Model Upgrade tests ----------------


def test_stt_service_allowed_models_constant_exists():
    """TASK-246: stt_service must expose _STT_ALLOWED_MODELS with supported model names."""
    assert hasattr(stt_service, "_STT_ALLOWED_MODELS"), (
        "_STT_ALLOWED_MODELS must exist in stt_service"
    )
    assert "tiny"  in stt_service._STT_ALLOWED_MODELS
    assert "base"  in stt_service._STT_ALLOWED_MODELS
    assert "small" in stt_service._STT_ALLOWED_MODELS


def test_stt_service_default_model_constant_exists():
    """TASK-246: stt_service must expose _STT_DEFAULT_MODEL = 'tiny'."""
    assert hasattr(stt_service, "_STT_DEFAULT_MODEL"), (
        "_STT_DEFAULT_MODEL must exist in stt_service"
    )
    assert stt_service._STT_DEFAULT_MODEL == "tiny", (
        "_STT_DEFAULT_MODEL must be 'tiny' (conservative default)"
    )


def test_stt_service_model_env_constant_exists():
    """TASK-246: stt_service must expose _STT_MODEL_ENV = 'DRAGON_PET_STT_MODEL'."""
    assert hasattr(stt_service, "_STT_MODEL_ENV"), (
        "_STT_MODEL_ENV must exist in stt_service"
    )
    assert stt_service._STT_MODEL_ENV == "DRAGON_PET_STT_MODEL", (
        "_STT_MODEL_ENV must be 'DRAGON_PET_STT_MODEL'"
    )


def test_stt_service_model_resolution_constant_exists():
    """TASK-246: stt_service must expose _STT_MODEL_RESOLUTION dict at module level."""
    assert hasattr(stt_service, "_STT_MODEL_RESOLUTION"), (
        "_STT_MODEL_RESOLUTION must exist in stt_service"
    )
    res = stt_service._STT_MODEL_RESOLUTION
    assert "requested_model" in res
    assert "resolved_model"  in res
    assert "model_source"    in res
    assert "fallback_reason" in res


def test_stt_service_model_resolver_default(monkeypatch):
    """TASK-246: _resolve_stt_model_name without env var defaults to 'tiny'."""
    monkeypatch.delenv("DRAGON_PET_STT_MODEL", raising=False)
    result = stt_service._resolve_stt_model_name()
    assert result["resolved_model"] == "tiny", (
        "Default resolved model must be 'tiny', got %r" % result["resolved_model"]
    )
    assert result["model_source"] == "default"
    assert result["fallback_reason"] == "none"


def test_stt_service_model_resolver_env_small(monkeypatch):
    """TASK-246: DRAGON_PET_STT_MODEL=small resolves to 'small'."""
    monkeypatch.setenv("DRAGON_PET_STT_MODEL", "small")
    result = stt_service._resolve_stt_model_name()
    assert result["resolved_model"] == "small", (
        "Env 'small' must resolve to 'small', got %r" % result["resolved_model"]
    )
    assert result["model_source"] == "env"
    assert result["fallback_reason"] == "none"


def test_stt_service_model_resolver_env_base(monkeypatch):
    """TASK-246: DRAGON_PET_STT_MODEL=base resolves to 'base'."""
    monkeypatch.setenv("DRAGON_PET_STT_MODEL", "base")
    result = stt_service._resolve_stt_model_name()
    assert result["resolved_model"] == "base", (
        "Env 'base' must resolve to 'base', got %r" % result["resolved_model"]
    )
    assert result["model_source"] == "env"
    assert result["fallback_reason"] == "none"


def test_stt_service_model_resolver_invalid_fallback(monkeypatch):
    """TASK-246: invalid DRAGON_PET_STT_MODEL falls back to 'tiny' safely — no crash."""
    monkeypatch.setenv("DRAGON_PET_STT_MODEL", "large-v3")
    result = stt_service._resolve_stt_model_name()
    assert result["resolved_model"] == "tiny", (
        "Invalid model must fall back to 'tiny', got %r" % result["resolved_model"]
    )
    assert result["model_source"] == "fallback"
    assert result["fallback_reason"] == "invalid_model"


def test_stt_service_ok_includes_model_quality_metadata(monkeypatch):
    """TASK-246: ok response from transcribe_audio_bytes must include model quality fields."""
    from types import SimpleNamespace

    class _GoodModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(text="你好")
            info = SimpleNamespace(language="zh")
            return iter([seg]), info

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _GoodModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert result["status"] == "ok"
    assert "requestedModel"  in result, "ok result must include 'requestedModel'"
    assert "resolvedModel"   in result, "ok result must include 'resolvedModel'"
    assert "modelSource"     in result, "ok result must include 'modelSource'"
    assert "modelLoadStatus" in result, "ok result must include 'modelLoadStatus'"


def test_stt_service_unavailable_has_model_metadata(monkeypatch):
    """TASK-246: unavailable response must include model metadata for diagnostics."""
    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", False)
    stt_service._reset_model_for_tests()
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03")
    assert result["status"] == "unavailable"
    assert "requestedModel"  in result, "unavailable result must include 'requestedModel'"
    assert "resolvedModel"   in result, "unavailable result must include 'resolvedModel'"
    assert "modelLoadStatus" in result, "unavailable result must include 'modelLoadStatus'"
    assert result["modelLoadStatus"] == "unavailable"


def test_stt_route_response_includes_model_quality_fields():
    """TASK-246: /stt/transcribe response must include model quality metadata fields."""
    with TestClient(app) as client:
        response = client.post(
            "/stt/transcribe",
            files={"audio": ("audio.webm", io.BytesIO(b"\x01\x02\x03"), "audio/webm")},
        )
    assert response.status_code == 200
    data = response.json()
    # TASK-245 language lock fields must still be present
    assert data.get("language") == "zh", "language must still be 'zh'"
    assert data.get("languageLocked") is True, "languageLocked must still be True"
    assert data.get("task") == "transcribe", "task must still be 'transcribe'"
    # TASK-246 model quality fields
    assert "requestedModel"  in data, "Response must include 'requestedModel'"
    assert "resolvedModel"   in data, "Response must include 'resolvedModel'"
    assert "modelSource"     in data, "Response must include 'modelSource'"
    assert "modelLoadStatus" in data, "Response must include 'modelLoadStatus'"


def test_stt_service_no_raw_stack_in_model_error(monkeypatch):
    """TASK-246: modelLoadError in response must be a short string, not a raw stack trace."""
    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()

    def _bad_load():
        stt_service._STT_MODEL_LOAD_STATUS = "error"
        stt_service._STT_MODEL_LOAD_ERROR = "simulated load failure"
        return None

    monkeypatch.setattr(stt_service, "_load_model", _bad_load)
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03")
    assert result["status"] == "unavailable"
    if result.get("modelLoadError"):
        assert len(result["modelLoadError"]) <= 200, (
            "modelLoadError must be truncated, not a raw stack trace"
        )
        assert "Traceback" not in result["modelLoadError"], (
            "modelLoadError must not contain Python stack traces"
        )


def test_stt_route_no_new_stt_endpoint():
    """TASK-246: no new /stt/* endpoint added beyond /stt/transcribe."""
    import inspect
    import app.api.routes as routes_module

    source = inspect.getsource(routes_module)
    stt_routes = [line for line in source.splitlines() if '"/stt/' in line]
    assert len(stt_routes) == 1, (
        "Only one /stt/ route allowed (TASK-246 restriction), found: %r" % stt_routes
    )


# -- TASK-247: STT Transcript Correction / Context-Aware Normalization tests ----


def test_stt_correction_helper_exists():
    """TASK-247: stt_service must expose correct_transcript_text helper."""
    assert hasattr(stt_service, "correct_transcript_text"), (
        "correct_transcript_text must exist in stt_service"
    )
    assert callable(stt_service.correct_transcript_text)


def test_stt_correction_empty_input_returns_empty():
    """TASK-247: empty input passes through unchanged — no correction, no crash."""
    result = stt_service.correct_transcript_text("")
    assert result["rawTranscript"] == "", "rawTranscript must be empty string"
    assert result["correctedTranscript"] == "", "correctedTranscript must be empty string"
    assert result["correctionApplied"] is False, "correctionApplied must be False for empty input"
    assert result["correctionMode"] == "safe_dictionary"
    assert result["correctionReason"] == "none"


def test_stt_correction_no_change_returns_same():
    """TASK-247: text with no matching phrase returns unchanged with correctionApplied=False."""
    text = "今天天氣很好"
    result = stt_service.correct_transcript_text(text)
    assert result["rawTranscript"] == text
    assert result["correctedTranscript"] == text
    assert result["correctionApplied"] is False
    assert result["correctionReason"] == "none"


def test_stt_correction_phrase_map_zhong_wen_bian_ji():
    """TASK-247: '中文語音編輯' → '中文語音辨識'."""
    result = stt_service.correct_transcript_text("這是中文語音編輯測試")
    assert "中文語音辨識" in result["correctedTranscript"], (
        "Expected '中文語音辨識' in corrected, got %r" % result["correctedTranscript"]
    )
    assert result["correctionApplied"] is True
    assert "phrase_map" in result["correctionReason"]


def test_stt_correction_phrase_map_zhong_wen_bian_ji2():
    """TASK-247: '中文語音邊記' → '中文語音辨識'."""
    result = stt_service.correct_transcript_text("中文語音邊記")
    assert result["correctedTranscript"] == "中文語音辨識", (
        "Expected '中文語音辨識', got %r" % result["correctedTranscript"]
    )
    assert result["correctionApplied"] is True


def test_stt_correction_phrase_map_mid_wei():
    """TASK-247: '中位與英編輯' → '中文語音辨識'."""
    result = stt_service.correct_transcript_text("這文中位與英編輯測試")
    assert "中文語音辨識" in result["correctedTranscript"], (
        "Expected '中文語音辨識' in corrected, got %r" % result["correctedTranscript"]
    )
    assert result["correctionApplied"] is True


def test_stt_correction_name_ke_li_si():
    """TASK-247: '克里斯蒂娜' → '克莉絲蒂娜'."""
    result = stt_service.correct_transcript_text("你好克里斯蒂娜")
    assert "克莉絲蒂娜" in result["correctedTranscript"], (
        "Expected '克莉絲蒂娜' in corrected, got %r" % result["correctedTranscript"]
    )
    assert result["correctionApplied"] is True


def test_stt_correction_name_ke_li_si2():
    """TASK-247: '克莉斯蒂娜' → '克莉絲蒂娜'."""
    result = stt_service.correct_transcript_text("克莉斯蒂娜你好")
    assert "克莉絲蒂娜" in result["correctedTranscript"]
    assert result["correctionApplied"] is True


def test_stt_correction_name_ke_li_si3():
    """TASK-247: '克麗絲蒂娜' → '克莉絲蒂娜'."""
    result = stt_service.correct_transcript_text("克麗絲蒂娜")
    assert result["correctedTranscript"] == "克莉絲蒂娜"
    assert result["correctionApplied"] is True


def test_stt_correction_raw_transcript_preserved():
    """TASK-247: rawTranscript must always equal the original unmodified input."""
    raw = "中文語音編輯"
    result = stt_service.correct_transcript_text(raw)
    assert result["rawTranscript"] == raw, (
        "rawTranscript must equal original input, got %r" % result["rawTranscript"]
    )
    assert result["correctedTranscript"] != raw  # correction was applied


def test_stt_correction_corrected_transcript_returned():
    """TASK-247: correctedTranscript key must be present in result."""
    result = stt_service.correct_transcript_text("test")
    assert "correctedTranscript" in result
    assert "rawTranscript" in result
    assert "correctionApplied" in result
    assert "correctionMode" in result
    assert "correctionReason" in result


def test_stt_correction_applied_true_false_correct():
    """TASK-247: correctionApplied is True only when text was actually changed."""
    changed = stt_service.correct_transcript_text("克里斯蒂娜")
    assert changed["correctionApplied"] is True
    unchanged = stt_service.correct_transcript_text("好的謝謝")
    assert unchanged["correctionApplied"] is False


def test_stt_service_ok_uses_corrected_transcript(monkeypatch):
    """TASK-247: transcript field in ok response must equal correctedTranscript."""
    from types import SimpleNamespace

    class _CorrectableModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(text="中文語音編輯")
            info = SimpleNamespace(language="zh")
            return iter([seg]), info

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _CorrectableModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert result["status"] == "ok"
    assert result["transcript"] == result["correctedTranscript"], (
        "transcript must equal correctedTranscript, got transcript=%r corrected=%r"
        % (result["transcript"], result["correctedTranscript"])
    )
    assert result["transcript"] != result["rawTranscript"], (
        "transcript (corrected) must differ from rawTranscript when correction applied"
    )
    assert result["correctionApplied"] is True


def test_stt_service_ok_includes_correction_metadata(monkeypatch):
    """TASK-247: ok response must include all correction metadata fields."""
    from types import SimpleNamespace

    class _GoodModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(text="你好")
            info = SimpleNamespace(language="zh")
            return iter([seg]), info

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _GoodModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert result["status"] == "ok"
    assert "rawTranscript"       in result, "ok result must include 'rawTranscript'"
    assert "correctedTranscript" in result, "ok result must include 'correctedTranscript'"
    assert "correctionApplied"   in result, "ok result must include 'correctionApplied'"
    assert "correctionMode"      in result, "ok result must include 'correctionMode'"
    assert "correctionReason"    in result, "ok result must include 'correctionReason'"


def test_stt_route_response_includes_correction_fields():
    """TASK-247: /stt/transcribe response must include correction metadata fields."""
    with TestClient(app) as client:
        response = client.post(
            "/stt/transcribe",
            files={"audio": ("audio.webm", io.BytesIO(b"\x01\x02\x03"), "audio/webm")},
        )
    assert response.status_code == 200
    data = response.json()
    # TASK-245 language lock fields must still be present
    assert data.get("language") == "zh", "TASK-245 language must still be 'zh'"
    assert data.get("languageLocked") is True, "TASK-245 languageLocked must still be True"
    # TASK-246 model quality fields must still be present
    assert "requestedModel"  in data, "TASK-246 requestedModel must still be present"
    assert "resolvedModel"   in data, "TASK-246 resolvedModel must still be present"
    assert "modelLoadStatus" in data, "TASK-246 modelLoadStatus must still be present"
    # TASK-247 correction fields (present when status is ok; unavailable if whisper absent)
    if data.get("status") == "ok":
        assert "rawTranscript"       in data, "TASK-247 rawTranscript must be present for ok status"
        assert "correctedTranscript" in data, "TASK-247 correctedTranscript must be present for ok status"
        assert "correctionApplied"   in data, "TASK-247 correctionApplied must be present for ok status"
        assert "correctionMode"      in data, "TASK-247 correctionMode must be present for ok status"
        assert "correctionReason"    in data, "TASK-247 correctionReason must be present for ok status"


def test_stt_correction_no_raw_stack_in_output():
    """TASK-247: correction output must not contain Python stack traces or raw payloads."""
    result = stt_service.correct_transcript_text("test input")
    for key, val in result.items():
        if isinstance(val, str):
            assert "Traceback" not in val, "correction output must not contain stack traces"
            assert "File \"" not in val, "correction output must not contain file paths"


def test_stt_service_no_raw_audio_persistence_with_correction():
    """TASK-247: adding correction must not introduce audio persistence."""
    import inspect

    source = inspect.getsource(stt_service)
    assert "open(" not in source, (
        "stt_service must not call open() — audio must stay in-memory (TASK-247 did not change this)"
    )


def test_stt_correction_language_lock_still_present(monkeypatch):
    """TASK-247: language lock (TASK-245) fields must not be regressed."""
    import app.api.routes as routes_module

    assert routes_module._STT_DEFAULT_LANGUAGE == "zh", "TASK-245 language lock must still be 'zh'"
    assert routes_module._STT_DEFAULT_TASK == "transcribe", "TASK-245 task must still be 'transcribe'"


def test_stt_correction_model_metadata_still_present(monkeypatch):
    """TASK-247: TASK-246 model metadata fields must not be regressed."""
    from types import SimpleNamespace

    class _GoodModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(text="test")
            info = SimpleNamespace(language="zh")
            return iter([seg]), info

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _GoodModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert result["status"] == "ok"
    assert "requestedModel"  in result, "TASK-246 requestedModel must not be regressed"
    assert "resolvedModel"   in result, "TASK-246 resolvedModel must not be regressed"
    assert "modelSource"     in result, "TASK-246 modelSource must not be regressed"
    assert "modelLoadStatus" in result, "TASK-246 modelLoadStatus must not be regressed"


# =============================================================================
# TASK-248: STT Hotword Coverage / Alias Expansion tests
# =============================================================================

# --- 克莉絲蒂娜 new aliases (16 added in TASK-248) ---

_CHRISTIANA_NEW_ALIASES = [
    "克利斯蒂娜",
    "克里斯提娜",
    "克莉絲提娜",
    "可莉絲蒂娜",
    "葛莉絲蒂娜",
    "格莉絲蒂娜",
    "格里斯蒂娜",
    "可麗絲蒂娜",
    "克麗絲提娜",
    "克莉絲緹娜",
    "克里斯緹娜",
    "克莉斯緹娜",
    "克莉絲蒂那",
    "克里斯蒂那",
    "克莉絲蒂納",
    "克里斯蒂納",
]


def test_stt_correction_christiana_all_new_aliases():
    """TASK-248: all 16 new aliases must correct to canonical 克莉絲蒂娜."""
    canonical = "克莉絲蒂娜"
    for alias in _CHRISTIANA_NEW_ALIASES:
        result = stt_service.correct_transcript_text(alias)
        assert result["correctedTranscript"] == canonical, (
            f"TASK-248: {alias!r} must correct to {canonical!r}, got {result['correctedTranscript']!r}"
        )
        assert result["correctionApplied"] is True, (
            f"TASK-248: correctionApplied must be True for alias {alias!r}"
        )


# --- Dragon Pet AI aliases ---

_DRAGON_PET_ALIASES = [
    ("Dragon Pet A I",  "Dragon Pet AI"),
    ("DragonPet AI",    "Dragon Pet AI"),
    ("Dragon pet AI",   "Dragon Pet AI"),
    ("dragon pet AI",   "Dragon Pet AI"),
    ("dragon pet ai",   "Dragon Pet AI"),
    ("龍寵 AI",         "Dragon Pet AI"),
    ("龍寵AI",          "Dragon Pet AI"),
]


def test_stt_correction_dragon_pet_ai_aliases():
    """TASK-248: all Dragon Pet AI alias forms must correct to canonical."""
    for alias, canonical in _DRAGON_PET_ALIASES:
        result = stt_service.correct_transcript_text(alias)
        assert result["correctedTranscript"] == canonical, (
            f"TASK-248: {alias!r} must correct to {canonical!r}, got {result['correctedTranscript']!r}"
        )
        assert result["correctionApplied"] is True


# --- Claude / Claude Code aliases ---

_CLAUDE_ALIASES = [
    ("克勞德 code",  "Claude Code"),
    ("克勞德 Code",  "Claude Code"),
    ("Claude code",  "Claude Code"),
    ("克勞德",       "Claude"),
]


def test_stt_correction_claude_code_aliases():
    """TASK-248: Claude / Claude Code aliases must correct to canonical forms."""
    for alias, canonical in _CLAUDE_ALIASES:
        result = stt_service.correct_transcript_text(alias)
        assert result["correctedTranscript"] == canonical, (
            f"TASK-248: {alias!r} must correct to {canonical!r}, got {result['correctedTranscript']!r}"
        )
        assert result["correctionApplied"] is True


# --- CodeX aliases ---

_CODEX_ALIASES_248 = [
    ("扣得 X",  "CodeX"),
    ("Code X",  "CodeX"),
    ("code x",  "CodeX"),
    ("Codex",   "CodeX"),
]


def test_stt_correction_codex_aliases():
    """TASK-248: CodeX alias forms must correct to canonical 'CodeX'."""
    for alias, canonical in _CODEX_ALIASES_248:
        result = stt_service.correct_transcript_text(alias)
        assert result["correctedTranscript"] == canonical, (
            f"TASK-248: {alias!r} must correct to {canonical!r}, got {result['correctedTranscript']!r}"
        )
        assert result["correctionApplied"] is True


# --- faster-whisper / Whisper aliases ---

def test_stt_correction_faster_whisper_aliases():
    """TASK-248: faster-whisper alias forms and 威斯伯 must correct correctly."""
    cases = [
        ("faster whisper",  "faster-whisper"),
        ("faster Whisper",  "faster-whisper"),
        ("威斯伯",          "Whisper"),
    ]
    for alias, canonical in cases:
        result = stt_service.correct_transcript_text(alias)
        assert result["correctedTranscript"] == canonical, (
            f"TASK-248: {alias!r} must correct to {canonical!r}, got {result['correctedTranscript']!r}"
        )
        assert result["correctionApplied"] is True


def test_stt_correction_whisper_not_corrupted_in_compound():
    """TASK-248: 'faster-whisper' (canonical) must not be re-corrupted after correction."""
    result = stt_service.correct_transcript_text("我在測試 faster whisper 模型")
    assert "faster-whisper" in result["correctedTranscript"], (
        "TASK-248: 'faster whisper' must become 'faster-whisper'"
    )
    assert "faster-Whisper" not in result["correctedTranscript"], (
        "TASK-248: canonical 'faster-whisper' must not be corrupted to 'faster-Whisper'"
    )


# --- Common feature term aliases ---

_FEATURE_TERM_ALIASES = [
    ("語音輸人",   "語音輸入"),
    ("語音書入",   "語音輸入"),
    ("對話糢式",   "對話模式"),
    ("對話模式式", "對話模式"),
    ("桌面重物",   "桌面寵物"),
    ("桌面從物",   "桌面寵物"),
]


def test_stt_correction_feature_terms():
    """TASK-248: common feature term aliases must correct to canonical."""
    for alias, canonical in _FEATURE_TERM_ALIASES:
        result = stt_service.correct_transcript_text(alias)
        assert result["correctedTranscript"] == canonical, (
            f"TASK-248: {alias!r} must correct to {canonical!r}, got {result['correctedTranscript']!r}"
        )
        assert result["correctionApplied"] is True


# --- matchedAlias / canonicalTerm fields ---

def test_stt_correction_matched_alias_populated():
    """TASK-248: matchedAlias must be populated when a correction fires."""
    result = stt_service.correct_transcript_text("克里斯蒂娜來了")
    assert result["correctionApplied"] is True
    assert result["matchedAlias"] == "克里斯蒂娜", (
        f"TASK-248: matchedAlias must be the first alias that fired, got {result['matchedAlias']!r}"
    )


def test_stt_correction_canonical_term_populated():
    """TASK-248: canonicalTerm must be the canonical target when a correction fires."""
    result = stt_service.correct_transcript_text("克里斯蒂娜來了")
    assert result["correctionApplied"] is True
    assert result["canonicalTerm"] == "克莉絲蒂娜", (
        f"TASK-248: canonicalTerm must be the canonical target, got {result['canonicalTerm']!r}"
    )


def test_stt_correction_no_match_matched_alias_empty():
    """TASK-248: matchedAlias and canonicalTerm must be empty when no correction fires."""
    result = stt_service.correct_transcript_text("沒有需要修正的文字")
    assert result["correctionApplied"] is False
    assert result["matchedAlias"] == "", (
        f"TASK-248: matchedAlias must be empty when no correction, got {result['matchedAlias']!r}"
    )
    assert result["canonicalTerm"] == "", (
        f"TASK-248: canonicalTerm must be empty when no correction, got {result['canonicalTerm']!r}"
    )


def test_stt_correction_empty_input_matched_alias_empty():
    """TASK-248: matchedAlias and canonicalTerm must be empty for empty input."""
    result = stt_service.correct_transcript_text("")
    assert result["matchedAlias"] == ""
    assert result["canonicalTerm"] == ""


def test_stt_service_ok_includes_matched_alias(monkeypatch):
    """TASK-248: ok response from transcribe_audio_bytes must include matchedAlias/canonicalTerm."""
    from types import SimpleNamespace

    class _GoodModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(text="你好")
            info = SimpleNamespace(language="zh")
            return iter([seg]), info

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _GoodModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert result["status"] == "ok"
    assert "matchedAlias"  in result, "TASK-248: ok result must include 'matchedAlias'"
    assert "canonicalTerm" in result, "TASK-248: ok result must include 'canonicalTerm'"


def test_stt_route_response_includes_matched_alias():
    """TASK-248: /stt/transcribe ok response must include matchedAlias/canonicalTerm."""
    with TestClient(app) as client:
        response = client.post(
            "/stt/transcribe",
            files={"audio": ("audio.webm", io.BytesIO(b"\x01\x02\x03"), "audio/webm")},
        )
    assert response.status_code == 200
    data = response.json()
    if data.get("status") == "ok":
        assert "matchedAlias"  in data, "TASK-248: ok response must include 'matchedAlias'"
        assert "canonicalTerm" in data, "TASK-248: ok response must include 'canonicalTerm'"
