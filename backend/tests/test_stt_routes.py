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
