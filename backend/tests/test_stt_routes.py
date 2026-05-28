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
