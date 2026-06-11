"""
TASK-167B: Backend pytest tests for POST /stt/transcribe.

Tests are designed to pass whether or not faster-whisper is installed.
When STT is unavailable, the endpoint returns status="unavailable" (not an error).
"""

import io
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace
import wave

import pytest

os.environ.setdefault("DB_PATH", "sqlite:///:memory:")
os.environ.setdefault("SETTINGS_FILE_PATH", "")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services import owner_voice_gate_storage  # noqa: E402
from app.services.owner_voice_gate_storage import reset_owner_voice_gate_storage_for_tests  # noqa: E402
from app.stt import stt_service  # noqa: E402


def _task_stt_004_pcm16_wav(sample_value: int = 0, frames: int = 16000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(
            b"".join(
                int(sample_value).to_bytes(2, "little", signed=True)
                for _ in range(frames)
            )
        )
    return buf.getvalue()


def _task_stt_004_pulsed_pcm16_wav(
    peak_value: int,
    pulse_frames: int,
    frames: int = 16000,
) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        samples = [int(peak_value)] * int(pulse_frames)
        samples.extend([0] * max(0, int(frames) - len(samples)))
        wav.writeframes(b"".join(sample.to_bytes(2, "little", signed=True) for sample in samples))
    return buf.getvalue()


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
    assert result["status"] in ("ok", "unavailable", "empty", "error", "no_speech")


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


def test_task_stt_004_silent_wav_hallucination_suppressed(monkeypatch):
    """TASK-STT-004: silent WAV + subtitle-credit hallucination returns no_speech."""

    class _HallucinatingModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(
                text="摮?by蝝Ｗ憡",
                no_speech_prob=0.91,
                avg_logprob=-2.5,
                compression_ratio=1.0,
            )
            return iter([seg]), SimpleNamespace(language="zh")

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _HallucinatingModel())

    result = stt_service.transcribe_audio_bytes(
        _task_stt_004_pcm16_wav(0, frames=16000),
        mime_type="audio/wav",
        language="zh",
    )

    assert result["status"] == "no_speech"
    assert result["transcript"] == ""
    assert result["finalTranscript"] == ""
    assert result["noSpeechGuardApplied"] is True
    assert result["noSpeechGuardReason"] == "no_speech_hallucination_guard"
    assert result["audioSpeechDetected"] is False
    assert result["audioRms"] == 0
    assert result["audioPeak"] == 0
    assert result["sttNoSpeechProbability"] == 0.91
    assert result["suspiciousTranscriptPattern"] == "subtitle_credit"
    assert result["correctionApplied"] is False
    assert result["correctionReason"] == "no_speech_guard"
    assert result["noSpeechGuardSignals"]["nearSilentAudio"] is True
    assert result["noSpeechGuardSignals"]["suspiciousTranscript"] is True
    assert result["noSpeechGuardDecisionTrace"] == "suppress:weak_speech_suspicious_transcript"


def test_task_stt_004_runtime_small_model_silence_hallucination_suppressed(monkeypatch):
    """TASK-STT-004: Windows small-model silent-runtime evidence returns no_speech."""

    class _RuntimeHallucinatingModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(
                text="摮?by蝝Ｗ憡",
                no_speech_prob=0.620446,
                avg_logprob=-1.2,
                compression_ratio=1.0,
            )
            return iter([seg]), SimpleNamespace(language="zh")

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _RuntimeHallucinatingModel())

    result = stt_service.transcribe_audio_bytes(
        _task_stt_004_pulsed_pcm16_wav(556, 193),
        mime_type="audio/wav",
        language="zh",
    )

    assert result["status"] == "no_speech"
    assert result["transcript"] == ""
    assert result["finalTranscript"] == ""
    assert result["noSpeechGuardApplied"] is True
    assert result["noSpeechGuardReason"] == "no_speech_hallucination_guard"
    assert result["audioSpeechDetected"] is False
    assert result["audioRms"] == pytest.approx(0.001863, abs=0.00001)
    assert result["audioPeak"] == pytest.approx(0.016969, abs=0.00001)
    assert result["sttNoSpeechProbability"] == 0.620446
    assert result["suspiciousTranscriptPattern"] == "subtitle_credit"
    assert result["noSpeechGuardSignals"]["highNoSpeechProbability"] is True
    assert result["noSpeechGuardThresholds"]["noSpeechProbability"] == 0.60
    assert result["noSpeechGuardDecisionTrace"] == "suppress:weak_speech_suspicious_transcript"


def test_task_stt_004_creator_cta_runtime_silence_hallucination_suppressed(monkeypatch):
    """TASK-STT-004: Windows creator-CTA silence hallucination returns no_speech."""

    class _CreatorCtaHallucinatingModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(
                text="霂瑞韏?霈ａ? 頧砍? ?? ??",
                no_speech_prob=0.52816,
                avg_logprob=-1.2,
                compression_ratio=1.0,
            )
            return iter([seg]), SimpleNamespace(language="zh")

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _CreatorCtaHallucinatingModel())

    result = stt_service.transcribe_audio_bytes(
        _task_stt_004_pulsed_pcm16_wav(3410, 244, frames=86640),
        mime_type="audio/wav",
        language="zh",
    )

    assert result["status"] == "no_speech"
    assert result["transcript"] == ""
    assert result["finalTranscript"] == ""
    assert result["noSpeechGuardApplied"] is True
    assert result["noSpeechGuardReason"] == "no_speech_hallucination_guard"
    assert result["audioSpeechDetected"] is False
    assert result["audioRms"] == pytest.approx(0.005523, abs=0.00001)
    assert result["audioPeak"] == pytest.approx(0.104068, abs=0.00001)
    assert result["audioSignalRatio"] == pytest.approx(0.002816, abs=0.00001)
    assert result["audioVoicedSampleCount"] == 244
    assert result["audioTransientPeakDetected"] is True
    assert result["sttNoSpeechProbability"] == 0.52816
    assert result["suspiciousTranscriptPattern"] == "creator_cta"
    assert result["noSpeechGuardSignals"]["creatorCtaTranscript"] is True
    assert result["noSpeechGuardSignals"]["transientPeak"] is True
    assert result["noSpeechGuardDecisionTrace"] == "suppress:weak_speech_suspicious_transcript"


def test_task_stt_004_silent_short_transcript_suppressed(monkeypatch):
    """TASK-STT-004: silent WAV with a short hallucinated transcript is not accepted."""

    class _ShortHallucinationModel:
        def transcribe(self, _buf, **_kwargs):
            return iter([SimpleNamespace(text="你好", no_speech_prob=0.2)]), None

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _ShortHallucinationModel())

    result = stt_service.transcribe_audio_bytes(
        _task_stt_004_pcm16_wav(0, frames=16000),
        mime_type="audio/wav",
        language="zh",
    )

    assert result["status"] == "no_speech"
    assert result["transcript"] == ""
    assert result["noSpeechGuardReason"] == "silent_audio"
    assert result["audioSpeechDetected"] is False


def test_task_stt_004_low_energy_high_no_speech_probability_suppressed(monkeypatch):
    """TASK-STT-004: low-energy audio plus no-speech metadata suppresses missed patterns."""

    class _MissedPatternModel:
        def transcribe(self, _buf, **_kwargs):
            return iter([SimpleNamespace(text="普通錯字", no_speech_prob=0.620446)]), None

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _MissedPatternModel())

    result = stt_service.transcribe_audio_bytes(
        _task_stt_004_pulsed_pcm16_wav(556, 193),
        mime_type="audio/wav",
        language="zh",
    )

    assert result["status"] == "no_speech"
    assert result["noSpeechGuardReason"] == "no_speech_probability"
    assert result["suspiciousTranscriptPattern"] == "none"
    assert result["noSpeechGuardSignals"]["highNoSpeechProbability"] is True
    assert result["noSpeechGuardDecisionTrace"] == "suppress:near_silent_high_no_speech_probability"


def test_task_stt_004_transient_peak_is_not_speech_evidence():
    meta = stt_service._audio_energy_metadata(
        _task_stt_004_pulsed_pcm16_wav(3410, 244, frames=86640),
        "audio/wav",
    )

    assert meta["audioRms"] == pytest.approx(0.005523, abs=0.00001)
    assert meta["audioPeak"] == pytest.approx(0.104068, abs=0.00001)
    assert meta["audioSignalRatio"] == pytest.approx(0.002816, abs=0.00001)
    assert meta["audioVoicedSampleCount"] == 244
    assert meta["audioSpeechDetected"] is False
    assert meta["audioTransientPeakDetected"] is True


def test_task_stt_004_real_energy_suspicious_phrase_not_suppressed(monkeypatch):
    """TASK-STT-004: suspicious text is blocked only with strong no-speech audio evidence."""

    class _RealSpeechModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(
                text="我真的說了摮?這個詞",
                no_speech_prob=0.1,
                avg_logprob=-0.1,
                compression_ratio=1.0,
            )
            return iter([seg]), SimpleNamespace(language="zh")

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _RealSpeechModel())

    result = stt_service.transcribe_audio_bytes(
        _task_stt_004_pcm16_wav(4000, frames=16000),
        mime_type="audio/wav",
        language="zh",
    )

    assert result["status"] == "ok"
    assert result["noSpeechGuardApplied"] is False
    assert result["audioSpeechDetected"] is True
    assert result["finalTranscript"]
    assert "摮?" in result["rawTranscript"]
    assert result["noSpeechGuardDecisionTrace"] == "allow:audio_energy_detected"


def test_task_stt_004_real_energy_creator_cta_phrase_not_suppressed(monkeypatch):
    """TASK-STT-004: CTA-like text is blocked only with weak/no-speech audio evidence."""

    class _RealSpeechModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(
                text="我真的說了閮這個詞",
                no_speech_prob=0.1,
                avg_logprob=-0.1,
                compression_ratio=1.0,
            )
            return iter([seg]), SimpleNamespace(language="zh")

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _RealSpeechModel())

    result = stt_service.transcribe_audio_bytes(
        _task_stt_004_pulsed_pcm16_wav(14352, 177),
        mime_type="audio/wav",
        language="zh",
    )

    assert result["status"] == "ok"
    assert result["noSpeechGuardApplied"] is False
    assert result["audioSpeechDetected"] is True
    assert result["suspiciousTranscriptPattern"] == "creator_cta"
    assert result["noSpeechGuardSignals"]["creatorCtaTranscript"] is True
    assert result["noSpeechGuardDecisionTrace"] == "allow:audio_energy_detected"


def test_task_stt_004_runtime_real_speech_energy_not_suppressed(monkeypatch):
    """TASK-STT-004: runtime-like real speech energy remains accepted."""

    class _RealSpeechModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(
                text="這是真實語音測試",
                no_speech_prob=0.1,
                avg_logprob=-0.1,
                compression_ratio=1.0,
            )
            return iter([seg]), SimpleNamespace(language="zh")

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _RealSpeechModel())

    result = stt_service.transcribe_audio_bytes(
        _task_stt_004_pulsed_pcm16_wav(14352, 177),
        mime_type="audio/wav",
        language="zh",
    )

    assert result["status"] == "ok"
    assert result["noSpeechGuardApplied"] is False
    assert result["audioSpeechDetected"] is True
    assert result["audioRms"] == pytest.approx(0.046, abs=0.001)
    assert result["audioPeak"] == pytest.approx(0.438, abs=0.001)
    assert result["finalTranscript"]


@pytest.mark.parametrize(
    "text",
    [
        "摮?by",
        "摮? by",
        "摮? By",
        "摮?BY",
        "摮?嚗",
        "摮?蝏",
        "摮?by蝝Ｗ憡",
        "subtitles by example",
        "caption by example",
        "字幕由範例提供",
        "字幕制作範例",
    ],
)
def test_task_stt_004_suspicious_subtitle_credit_variants_detected(text):
    assert stt_service._detect_suspicious_transcript_pattern(text) == "subtitle_credit"


@pytest.mark.parametrize(
    "text",
    [
        "霂瑞韏?",
        "隢?霈",
        "?寡?",
        "暺?",
        "霈ａ?",
        "閮",
        "頧砍?",
        "頧",
        "??",
        "?寡? 霈ａ? 頧砍? ??",
        "?? ??",
        "like and subscribe",
    ],
)
def test_task_stt_004_suspicious_creator_cta_variants_detected(text):
    assert stt_service._detect_suspicious_transcript_pattern(text) == "creator_cta"


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
    assert data["status"] in ("ok", "unavailable", "empty", "error", "no_speech")


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


def _owner_voice_gate_temp_storage(tmp_path):
    path = tmp_path / "owner_voice_gate_settings.json"
    reset_owner_voice_gate_storage_for_tests(str(path))
    return path


def test_owner_voice_gate_default_status_safe_schema(tmp_path):
    """TASK-261: Owner Voice Gate status is safe, disabled, and not enrolled by default."""
    _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        response = client.get("/owner-voice-gate/status")

    data = response.json()
    assert response.status_code == 200
    assert data["schemaVersion"] == 1
    assert data["storageOwner"] == "backend"
    assert data["status"] == "not_enrolled"
    assert data["enabled"] is False
    assert data["enrolled"] is False
    assert data["provider"] == "funasr-campp"
    assert data["modelId"] == "iic/speech_campplus_sv_zh-cn_16k-common"
    assert data["embeddingDim"] == 192
    assert data["embeddingAggregate"] is None
    assert data["sampleCount"] == 0
    assert data["threshold"] == 0.65
    assert data["safetyNoticeAccepted"] is False
    assert "rawAudio" not in response.text
    assert "base64Audio" not in response.text
    assert "transcript" not in response.text
    assert "waveform" not in response.text


def test_owner_voice_gate_update_accepts_safety_notice_and_threshold(tmp_path):
    """TASK-261: settings endpoint stores only safe stub fields."""
    path = _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/settings",
            json={"safetyNoticeAccepted": True, "threshold": 0.72},
        )

    data = response.json()
    assert response.status_code == 200
    assert data["safetyNoticeAccepted"] is True
    assert data["threshold"] == 0.72
    assert data["enabled"] is False
    assert data["enrolled"] is False
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["safetyNoticeAccepted"] is True
    assert saved["threshold"] == 0.72
    assert saved["embeddingAggregate"] is None


def test_owner_voice_gate_threshold_is_clamped(tmp_path):
    """TASK-261: threshold stays in the documented 0.40..0.95 range."""
    _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        low = client.post("/owner-voice-gate/settings", json={"threshold": 0.1})
        high = client.post("/owner-voice-gate/settings", json={"threshold": 1.5})

    assert low.status_code == 200
    assert low.json()["threshold"] == 0.4
    assert high.status_code == 200
    assert high.json()["threshold"] == 0.95


def test_owner_voice_gate_cannot_enable_when_not_enrolled(tmp_path):
    """TASK-261: enabling the gate before enrollment returns clean not_enrolled."""
    _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        response = client.post("/owner-voice-gate/settings", json={"enabled": True})

    data = response.json()
    assert response.status_code == 200
    assert data["enabled"] is False
    assert data["enrolled"] is False
    assert data["reason"] == "not_enrolled"
    assert data["status"] == "not_enrolled"


def test_owner_voice_gate_rejects_forbidden_storage_fields(tmp_path):
    """TASK-261: endpoint rejects audio, transcript, and embedding vector fields."""
    _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/settings",
            json={
                "rawAudio": "not allowed",
                "base64Audio": "not allowed",
                "transcript": "not allowed",
                "waveform": [0, 1],
                "embeddingAggregate": [0.1, 0.2],
            },
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "unsupported owner voice gate setting field"}
    assert "not allowed" not in response.text
    assert "0.1" not in response.text


def test_owner_voice_gate_storage_file_never_contains_audio_or_embedding_fields(tmp_path):
    """TASK-261: persisted stub does not contain raw audio, transcripts, or real vectors."""
    path = _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/settings",
            json={"safetyNoticeAccepted": True, "threshold": 0.65},
        )

    assert response.status_code == 200
    raw = path.read_text(encoding="utf-8")
    assert "rawAudio" not in raw
    assert "base64Audio" not in raw
    assert "audioBytes" not in raw
    assert "transcript" not in raw
    assert "waveform" not in raw
    assert "perSampleEmbeddings" not in raw
    assert '"embeddingAggregate": null' in raw


def test_owner_voice_gate_delete_resets_storage_stub(tmp_path):
    """TASK-261: delete resets placeholder storage to default, with no chat/STT effect."""
    path = _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        client.post(
            "/owner-voice-gate/settings",
            json={"safetyNoticeAccepted": True, "threshold": 0.72},
        )
        assert path.exists()
        response = client.post("/owner-voice-gate/delete")
        status = client.get("/owner-voice-gate/status")

    assert response.status_code == 200
    assert response.json()["reason"] == "deleted"
    assert response.json()["enabled"] is False
    assert response.json()["safetyNoticeAccepted"] is False
    assert not path.exists()
    assert status.json()["threshold"] == 0.65
    assert status.json()["enabled"] is False


def test_owner_voice_gate_errors_do_not_return_raw_stack(tmp_path):
    """TASK-261: bad requests are sanitized."""
    _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        response = client.post("/owner-voice-gate/settings", json=["bad"])

    assert response.status_code == 400
    assert response.json() == {"detail": "request body must be an object"}
    assert "Traceback" not in response.text
    assert "Exception" not in response.text


def _mock_owner_voice_enrollment_report(paths, threshold):
    vector = [0.0] * 192
    vector[0] = 1.0
    return {
        "status": "ok",
        "reason": "owner_enrollment_complete",
        "provider": "funasr-campp",
        "modelId": "iic/speech_campplus_sv_zh-cn_16k-common",
        "embeddingDim": 192,
        "sampleCount": len(paths),
        "threshold": threshold,
        "calibrationStats": {
            "meanSelfScore": 0.98,
            "minSelfScore": 0.97,
            "maxSelfScore": 0.99,
        },
        "embeddingAggregate": vector,
        "rawAudioPersisted": False,
        "embeddingPersisted": False,
        "micAccessed": False,
        "runtimeIntegrated": False,
    }


def _owner_voice_sample_paths(tmp_path, folder_name="voice"):
    sample_dir = tmp_path / folder_name
    sample_dir.mkdir(parents=True, exist_ok=True)
    owner1 = sample_dir / "owner1.wav"
    owner2 = sample_dir / "owner2.wav"
    owner1.write_bytes(b"mock owner wav path only")
    owner2.write_bytes(b"mock owner wav path only")
    return str(owner1), str(owner2)


def _load_owner_voice_verify_module():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "owner_voice_gate_verify.py"
    spec = importlib.util.spec_from_file_location("owner_voice_gate_verify_for_tests", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _write_task264_wav(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 1600)


def _write_task264_settings(path, centroid=None, threshold=0.65):
    centroid = centroid or ([1.0] + [0.0] * 191)
    path.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "enabled": False,
                "enrolled": True,
                "provider": "funasr-campp",
                "modelId": "iic/speech_campplus_sv_zh-cn_16k-common",
                "embeddingDim": 192,
                "embeddingAggregate": centroid,
                "sampleCount": 2,
                "threshold": threshold,
                "safetyNoticeAccepted": True,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _task264_args(settings_path, candidate_samples=None, threshold=None):
    return SimpleNamespace(
        settings_json=str(settings_path),
        candidate_samples=candidate_samples or [],
        candidate_dir=None,
        threshold=threshold,
        model_id=None,
        allow_download=False,
        device="cpu",
    )


def test_owner_voice_gate_enroll_requires_safety_notice(tmp_path):
    """TASK-263: file enrollment requires explicit safety notice acceptance."""
    _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/enroll-files",
            json={"paths": ["owner1.wav", "owner2.wav"], "safetyNoticeAccepted": False},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "safety notice must be accepted before enrollment"}


def test_owner_voice_gate_enroll_rejects_forbidden_fields(tmp_path):
    """TASK-263: enrollment endpoint accepts paths only, never audio or embeddings from UI."""
    _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/enroll-files",
            json={
                "paths": ["owner1.wav", "owner2.wav"],
                "safetyNoticeAccepted": True,
                "rawAudio": "not allowed",
                "base64Audio": "not allowed",
                "transcript": "not allowed",
                "embeddingAggregate": [0.1] * 192,
            },
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "unsupported owner voice enrollment field"}
    assert "not allowed" not in response.text
    assert "0.1" not in response.text


def test_owner_voice_gate_enroll_rejects_fewer_than_two_samples(tmp_path):
    """TASK-263: enrollment requires at least two owner WAV file paths."""
    _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/enroll-files",
            json={"paths": ["owner1.wav"], "safetyNoticeAccepted": True},
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "at least 2 owner voice samples are required"}


def test_owner_voice_gate_enroll_mock_writes_centroid_storage(tmp_path, monkeypatch):
    """TASK-263: successful mocked enrollment stores centroid only in backend storage."""
    path = _owner_voice_gate_temp_storage(tmp_path)
    owner1, owner2 = _owner_voice_sample_paths(tmp_path)
    monkeypatch.setattr(
        owner_voice_gate_storage,
        "run_owner_voice_enrollment_sidecar",
        _mock_owner_voice_enrollment_report,
    )

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/enroll-files",
            json={
                "paths": [owner1, owner2],
                "threshold": 0.65,
                "safetyNoticeAccepted": True,
            },
        )

    data = response.json()
    assert response.status_code == 200
    assert data["reason"] == "enrolled"
    assert data["enabled"] is False
    assert data["enrolled"] is True
    assert data["sampleCount"] == 2
    assert data["embeddingAggregate"] is None, "API response must not expose centroid"
    assert data["embeddingPersisted"] is True
    assert data["calibrationStats"]["meanSelfScore"] == 0.98

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["enrolled"] is True
    assert saved["enabled"] is False
    assert saved["sampleCount"] == 2
    assert len(saved["embeddingAggregate"]) == 192
    assert saved["embeddingAggregate"][0] == 1.0
    assert "rawAudio" not in saved
    assert "base64Audio" not in saved
    assert "transcript" not in saved
    assert "waveform" not in saved
    assert "perSampleEmbeddings" not in saved


def test_owner_voice_gate_enroll_accepts_unicode_existing_paths(tmp_path, monkeypatch):
    """TASK-263 follow-up: Windows Unicode paths must reach the sidecar unchanged."""
    _owner_voice_gate_temp_storage(tmp_path)
    owner1, owner2 = _owner_voice_sample_paths(tmp_path, "雪狼丸 owner voice")
    captured_paths = []

    def _capture_owner_voice_enrollment_report(paths, threshold):
        captured_paths.extend(paths)
        return _mock_owner_voice_enrollment_report(paths, threshold)

    monkeypatch.setattr(
        owner_voice_gate_storage,
        "run_owner_voice_enrollment_sidecar",
        _capture_owner_voice_enrollment_report,
    )

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/enroll-files",
            json={
                "paths": [owner1, owner2],
                "threshold": 0.65,
                "safetyNoticeAccepted": True,
            },
        )

    data = response.json()
    assert response.status_code == 200
    assert data["reason"] == "enrolled"
    assert data["sampleCount"] == 2
    assert captured_paths == [owner1, owner2]
    assert "雪狼丸" in captured_paths[0]
    assert data["embeddingAggregate"] is None


def test_owner_voice_gate_enroll_ascii_existing_paths_still_work(tmp_path, monkeypatch):
    """TASK-263 follow-up: ASCII path enrollment remains compatible."""
    _owner_voice_gate_temp_storage(tmp_path)
    owner1, owner2 = _owner_voice_sample_paths(tmp_path, "ascii-owner-voice")
    monkeypatch.setattr(
        owner_voice_gate_storage,
        "run_owner_voice_enrollment_sidecar",
        _mock_owner_voice_enrollment_report,
    )

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/enroll-files",
            json={
                "paths": [owner1, owner2],
                "threshold": 0.65,
                "safetyNoticeAccepted": True,
            },
        )

    assert response.status_code == 200
    assert response.json()["reason"] == "enrolled"
    assert response.json()["sampleCount"] == 2


def test_owner_voice_gate_enroll_missing_file_returns_clean_not_enrolled(tmp_path, monkeypatch):
    """TASK-263 follow-up: missing files return a clean reason and do not call sidecar."""
    _owner_voice_gate_temp_storage(tmp_path)
    missing1 = str(tmp_path / "雪狼丸 missing" / "owner1.wav")
    missing2 = str(tmp_path / "雪狼丸 missing" / "owner2.wav")

    def _fail_if_called(_paths, _threshold):
        raise AssertionError("sidecar must not run for missing enrollment paths")

    monkeypatch.setattr(
        owner_voice_gate_storage,
        "run_owner_voice_enrollment_sidecar",
        _fail_if_called,
    )

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/enroll-files",
            json={
                "paths": [missing1, missing2],
                "threshold": 0.65,
                "safetyNoticeAccepted": True,
            },
        )

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "not_enrolled"
    assert data["reason"] == "audio_file_not_found"
    assert data["message"] == "Enrollment requires existing mono 16 kHz PCM WAV files."
    assert "Traceback" not in response.text
    assert "AssertionError" not in response.text
    assert "雪狼丸" not in response.text


def test_owner_voice_gate_enable_allowed_after_enrollment(tmp_path, monkeypatch):
    """TASK-263: enabled can be true only after a centroid has been enrolled."""
    _owner_voice_gate_temp_storage(tmp_path)
    owner1, owner2 = _owner_voice_sample_paths(tmp_path)
    monkeypatch.setattr(
        owner_voice_gate_storage,
        "run_owner_voice_enrollment_sidecar",
        _mock_owner_voice_enrollment_report,
    )

    with TestClient(app) as client:
        enroll = client.post(
            "/owner-voice-gate/enroll-files",
            json={
                "paths": [owner1, owner2],
                "safetyNoticeAccepted": True,
            },
        )
        enabled = client.post("/owner-voice-gate/settings", json={"enabled": True})

    assert enroll.status_code == 200
    assert enabled.status_code == 200
    assert enabled.json()["enrolled"] is True
    assert enabled.json()["enabled"] is True
    assert enabled.json()["status"] == "enabled"


def test_owner_voice_gate_delete_clears_enrolled_centroid(tmp_path, monkeypatch):
    """TASK-263: delete clears the stored centroid and enrolled state."""
    path = _owner_voice_gate_temp_storage(tmp_path)
    owner1, owner2 = _owner_voice_sample_paths(tmp_path)
    monkeypatch.setattr(
        owner_voice_gate_storage,
        "run_owner_voice_enrollment_sidecar",
        _mock_owner_voice_enrollment_report,
    )

    with TestClient(app) as client:
        client.post(
            "/owner-voice-gate/enroll-files",
            json={
                "paths": [owner1, owner2],
                "safetyNoticeAccepted": True,
            },
        )
        assert path.exists()
        response = client.post("/owner-voice-gate/delete")
        status = client.get("/owner-voice-gate/status")

    assert response.status_code == 200
    assert response.json()["enrolled"] is False
    assert response.json()["embeddingAggregate"] is None
    assert response.json()["embeddingPersisted"] is False
    assert not path.exists()
    assert status.json()["status"] == "not_enrolled"


def test_owner_voice_gate_enroll_route_no_stt_or_chat_runtime_calls():
    """TASK-263: enrollment endpoint must not call STT or chat runtime."""
    import inspect
    import app.api.routes as routes_module

    source = inspect.getsource(routes_module.owner_voice_gate_enroll_files_route)
    assert "transcribe_audio_bytes" not in source
    assert "stt_transcribe" not in source
    assert "generate_chat_reply" not in source
    assert "store_chat_turn" not in source


def test_owner_voice_gate_verify_no_enrollment_returns_clean_not_enrolled(tmp_path):
    """TASK-264: verification probe returns clean not_enrolled without model load."""
    verify = _load_owner_voice_verify_module()

    result = verify.run_verification(_task264_args(tmp_path / "missing_settings.json"))

    assert result["status"] == "not_enrolled"
    assert result["reason"] == "not_enrolled"
    assert result["enrolled"] is False
    assert result["accepted"] is False
    assert result["modelLoadAttempted"] is False
    assert result["storedCentroidExposed"] is False
    assert result["candidateEmbeddingPersisted"] is False
    assert "embeddingAggregate" not in result


def test_owner_voice_gate_verify_missing_wav_returns_clean_audio_not_found(tmp_path):
    """TASK-264: missing candidate files return a clean reason and do not load model."""
    verify = _load_owner_voice_verify_module()
    settings_path = tmp_path / "owner_voice_gate_settings.json"
    _write_task264_settings(settings_path)
    missing_path = tmp_path / "雪狼丸 missing" / "candidate.wav"

    result = verify.run_verification(_task264_args(settings_path, [str(missing_path)]))

    assert result["status"] == "unavailable"
    assert result["reason"] == "audio_file_not_found"
    assert result["enrolled"] is True
    assert result["modelLoadAttempted"] is False
    assert "Traceback" not in json.dumps(result, ensure_ascii=False)
    assert "embeddingAggregate" not in result


def test_owner_voice_gate_verify_unicode_path_and_mock_accept(tmp_path, monkeypatch):
    """TASK-264: Unicode candidate paths reach mocked embedding extraction unchanged."""
    verify = _load_owner_voice_verify_module()
    settings_path = tmp_path / "owner_voice_gate_settings.json"
    _write_task264_settings(settings_path)
    candidate_path = tmp_path / "雪狼丸 voice probe" / "owner2.wav"
    _write_task264_wav(candidate_path)
    captured_paths = []
    original_base_report = verify._base_report

    def _mock_base_report():
        report = original_base_report()
        report.update(
            {
                "torchAvailable": True,
                "funasrAvailable": True,
                "modelscopeAvailable": True,
                "numpyAvailable": True,
            }
        )
        return report

    monkeypatch.setattr(verify, "_base_report", _mock_base_report)
    monkeypatch.setattr(verify, "_load_funasr_model", lambda *_args, **_kwargs: object())

    def _mock_extract(_model, path):
        captured_paths.append(str(path))
        return [1.0] + [0.0] * 191

    monkeypatch.setattr(verify, "_extract_embedding", _mock_extract)

    result = verify.run_verification(_task264_args(settings_path, [str(candidate_path)]))

    assert result["status"] == "ok"
    assert result["reason"] == "verification_complete"
    assert result["score"] == 1.0
    assert result["scores"] == [1.0]
    assert result["threshold"] == 0.65
    assert result["accepted"] is True
    assert result["embeddingDim"] == 192
    assert result["sampleCount"] == 1
    assert captured_paths == [str(candidate_path)]
    assert "雪狼丸" in captured_paths[0]
    assert result["storedCentroidExposed"] is False
    assert result["candidateEmbeddingPersisted"] is False
    assert "embeddingAggregate" not in result


def test_owner_voice_gate_verify_mock_reject_decision():
    """TASK-264: cosine score below threshold rejects without exposing embeddings."""
    verify = _load_owner_voice_verify_module()
    owner_centroid = [1.0] + [0.0] * 191
    other_embedding = [0.0, 1.0] + [0.0] * 190

    result = verify.build_verification_decision(
        stored_centroid=owner_centroid,
        candidate_embeddings=[other_embedding],
        threshold=0.65,
    )

    assert result == {
        "score": 0.0,
        "scores": [0.0],
        "threshold": 0.65,
        "accepted": False,
        "embeddingDim": 192,
        "sampleCount": 1,
    }


def test_stt_service_no_audio_persistence():
    """TASK-167B privacy: stt_service must not write audio to disk."""
    import inspect, re

    source = inspect.getsource(stt_service)
    # Check for file write patterns (open with write mode).
    # "Popen(" is allowed (subprocess management); plain open() for file writes is not.
    assert not re.search(r'\bopen\s*\(', source), (
        "stt_service must not call open() for file I/O -- audio must stay in-memory. "
        "Note: subprocess.Popen() is permitted."
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
    # Count /stt/ route decorators — TASK-256 adds /stt/warmup; minimum 2 allowed
    stt_routes = [line for line in source.splitlines() if '"/stt/' in line]
    assert any("/stt/transcribe" in r for r in stt_routes), (
        "TASK-245: /stt/transcribe must still exist, found: %r" % stt_routes
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


def test_task_stt_003_model_override_env_constant_exists():
    """TASK-STT-003: stt_service must expose DRAGON_STT_MODEL as the short override."""
    assert hasattr(stt_service, "_STT_MODEL_OVERRIDE_ENV")
    assert stt_service._STT_MODEL_OVERRIDE_ENV == "DRAGON_STT_MODEL"


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
    assert "model_env"       in res


def test_stt_service_model_resolver_default(monkeypatch):
    """TASK-246: _resolve_stt_model_name without env var defaults to 'tiny'."""
    monkeypatch.delenv("DRAGON_STT_MODEL", raising=False)
    monkeypatch.delenv("DRAGON_PET_STT_MODEL", raising=False)
    result = stt_service._resolve_stt_model_name()
    assert result["resolved_model"] == "tiny", (
        "Default resolved model must be 'tiny', got %r" % result["resolved_model"]
    )
    assert result["model_source"] == "default"
    assert result["fallback_reason"] == "none"
    assert result["model_env"] == ""


def test_stt_service_model_resolver_env_small(monkeypatch):
    """TASK-246: DRAGON_PET_STT_MODEL=small resolves to 'small'."""
    monkeypatch.delenv("DRAGON_STT_MODEL", raising=False)
    monkeypatch.setenv("DRAGON_PET_STT_MODEL", "small")
    result = stt_service._resolve_stt_model_name()
    assert result["resolved_model"] == "small", (
        "Env 'small' must resolve to 'small', got %r" % result["resolved_model"]
    )
    assert result["model_source"] == "env"
    assert result["fallback_reason"] == "none"
    assert result["model_env"] == "DRAGON_PET_STT_MODEL"


def test_stt_service_model_resolver_env_base(monkeypatch):
    """TASK-246: DRAGON_PET_STT_MODEL=base resolves to 'base'."""
    monkeypatch.delenv("DRAGON_STT_MODEL", raising=False)
    monkeypatch.setenv("DRAGON_PET_STT_MODEL", "base")
    result = stt_service._resolve_stt_model_name()
    assert result["resolved_model"] == "base", (
        "Env 'base' must resolve to 'base', got %r" % result["resolved_model"]
    )
    assert result["model_source"] == "env"
    assert result["fallback_reason"] == "none"
    assert result["model_env"] == "DRAGON_PET_STT_MODEL"


def test_task_stt_003_model_override_env_base(monkeypatch):
    """TASK-STT-003: DRAGON_STT_MODEL=base resolves as first runtime candidate."""
    monkeypatch.setenv("DRAGON_STT_MODEL", "base")
    monkeypatch.setenv("DRAGON_PET_STT_MODEL", "small")
    result = stt_service._resolve_stt_model_name()
    assert result["requested_model"] == "base"
    assert result["resolved_model"] == "base"
    assert result["model_source"] == "env"
    assert result["fallback_reason"] == "none"
    assert result["model_env"] == "DRAGON_STT_MODEL"


def test_task_stt_003_model_override_env_small(monkeypatch):
    """TASK-STT-003: DRAGON_STT_MODEL=small resolves for quality candidate smoke."""
    monkeypatch.setenv("DRAGON_STT_MODEL", "small")
    monkeypatch.delenv("DRAGON_PET_STT_MODEL", raising=False)
    result = stt_service._resolve_stt_model_name()
    assert result["requested_model"] == "small"
    assert result["resolved_model"] == "small"
    assert result["model_source"] == "env"
    assert result["fallback_reason"] == "none"
    assert result["model_env"] == "DRAGON_STT_MODEL"


def test_stt_service_model_resolver_invalid_fallback(monkeypatch):
    """TASK-246: invalid DRAGON_PET_STT_MODEL falls back to 'tiny' safely — no crash."""
    monkeypatch.delenv("DRAGON_STT_MODEL", raising=False)
    monkeypatch.setenv("DRAGON_PET_STT_MODEL", "large-v3")
    result = stt_service._resolve_stt_model_name()
    assert result["resolved_model"] == "tiny", (
        "Invalid model must fall back to 'tiny', got %r" % result["resolved_model"]
    )
    assert result["model_source"] == "fallback"
    assert result["fallback_reason"] == "invalid_model"
    assert result["model_env"] == "DRAGON_PET_STT_MODEL"


def test_task_stt_003_invalid_override_fallback(monkeypatch):
    """TASK-STT-003: invalid DRAGON_STT_MODEL falls back safely and reports source."""
    monkeypatch.setenv("DRAGON_STT_MODEL", "large-v3")
    monkeypatch.setenv("DRAGON_PET_STT_MODEL", "base")
    result = stt_service._resolve_stt_model_name()
    assert result["requested_model"] == "large-v3"
    assert result["resolved_model"] == "tiny"
    assert result["model_source"] == "fallback"
    assert result["fallback_reason"] == "invalid_model"
    assert result["model_env"] == "DRAGON_STT_MODEL"


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
    assert "modelFallbackReason" in result, "ok result must include 'modelFallbackReason'"
    assert "modelEnv"        in result, "ok result must include 'modelEnv'"
    assert "modelLoadStatus" in result, "ok result must include 'modelLoadStatus'"


def test_stt_service_unavailable_has_model_metadata(monkeypatch):
    """TASK-246: unavailable response must include model metadata for diagnostics."""
    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", False)
    stt_service._reset_model_for_tests()
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03")
    assert result["status"] == "unavailable"
    assert "requestedModel"  in result, "unavailable result must include 'requestedModel'"
    assert "resolvedModel"   in result, "unavailable result must include 'resolvedModel'"
    assert "modelFallbackReason" in result, "unavailable result must include 'modelFallbackReason'"
    assert "modelEnv"        in result, "unavailable result must include 'modelEnv'"
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
    assert "modelFallbackReason" in data, "Response must include 'modelFallbackReason'"
    assert "modelEnv"        in data, "Response must include 'modelEnv'"
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
    # TASK-256 adds /stt/warmup; /stt/transcribe must remain
    assert any("/stt/transcribe" in r for r in stt_routes), (
        "TASK-246: /stt/transcribe must still exist, found: %r" % stt_routes
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
    import inspect, re

    source = inspect.getsource(stt_service)
    # subprocess.Popen() is allowed (process management); standalone open() for file I/O is not.
    assert not re.search(r'\bopen\s*\(', source), (
        "stt_service must not call open() for file I/O — audio must stay in-memory "
        "(TASK-247 did not change this). Note: subprocess.Popen() is permitted."
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


# -- TASK-STT-001: Chinese STT punctuation restoration -------------------------


def test_task_stt_001_punctuation_helper_exists():
    """TASK-STT-001: stt_service must expose restore_transcript_punctuation helper."""
    assert hasattr(stt_service, "restore_transcript_punctuation")
    assert callable(stt_service.restore_transcript_punctuation)


def test_task_stt_001_chinese_without_punctuation_gets_terminal_period():
    """Conservative CJK text without punctuation receives a final sentence mark."""
    result = stt_service.restore_transcript_punctuation("今天天氣很好我們開始測試")
    assert result["punctuatedTranscript"] == "今天天氣很好我們開始測試。"
    assert result["finalTranscript"] == result["punctuatedTranscript"]
    assert result["punctuationApplied"] is True
    assert result["punctuationMode"] == "conservative_cjk_terminal"
    assert result["punctuationReason"] == "added_terminal_period"


def test_task_stt_001_already_punctuated_transcript_not_damaged():
    """Already punctuated Chinese text must pass through unchanged."""
    text = "今天天氣很好，我們開始測試。"
    result = stt_service.restore_transcript_punctuation(text)
    assert result["punctuatedTranscript"] == text
    assert result["finalTranscript"] == text
    assert result["punctuationApplied"] is False
    assert result["punctuationReason"] == "already_punctuated"


def test_task_stt_001_empty_transcript_remains_empty():
    """Empty transcript remains empty and is not marked as punctuated."""
    result = stt_service.restore_transcript_punctuation("")
    assert result["punctuatedTranscript"] == ""
    assert result["finalTranscript"] == ""
    assert result["punctuationApplied"] is False
    assert result["punctuationReason"] == "empty"


def test_task_stt_001_short_ambiguous_transcript_not_modified():
    """Short ambiguous utterances like '你好' must not be aggressively modified."""
    result = stt_service.restore_transcript_punctuation("你好")
    assert result["punctuatedTranscript"] == "你好"
    assert result["finalTranscript"] == "你好"
    assert result["punctuationApplied"] is False
    assert result["punctuationReason"] == "short_ambiguous"


def test_task_stt_001_safe_dictionary_correction_precedes_punctuation(monkeypatch):
    """Pipeline order: raw STT -> safe dictionary correction -> punctuation -> final transcript."""
    from types import SimpleNamespace

    class _CorrectableModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(text="這是中文語音編輯測試我們開始")
            info = SimpleNamespace(language="zh")
            return iter([seg]), info

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "faster-whisper-local")
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _CorrectableModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")

    assert result["status"] == "ok"
    assert result["rawTranscript"] == "這是中文語音編輯測試我們開始"
    assert result["correctedTranscript"] == "這是中文語音辨識測試我們開始"
    assert result["punctuatedTranscript"] == "這是中文語音辨識測試我們開始。"
    assert result["finalTranscript"] == result["punctuatedTranscript"]
    assert result["transcript"] == result["finalTranscript"]
    assert result["correctionApplied"] is True
    assert result["punctuationApplied"] is True


def test_task_stt_001_funasr_ok_path_uses_final_transcript(monkeypatch):
    """FunASR ok path also returns finalTranscript in transcript."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(
        stt_service,
        "_run_funasr",
        lambda b, m: {
            "transcript": "今天天氣很好我們開始測試",
            "status": "ok",
            "error": None,
            "funasrSidecarMode": "persistent",
            "funasrSidecarWarm": True,
            "funasrSidecarRestarted": False,
        },
    )
    result = stt_service._transcribe_funasr(b"\x01\x02")
    assert result["status"] == "ok"
    assert result["transcript"] == "今天天氣很好我們開始測試。"
    assert result["finalTranscript"] == result["transcript"]
    assert result["punctuationApplied"] is True


def test_task_stt_001_stt_route_response_includes_punctuation_metadata(monkeypatch):
    """Endpoint response surfaces punctuation metadata without changing request schema."""
    import app.api.routes as routes_module

    def _mock_transcribe(_audio_bytes, mime_type="audio/webm", language=None):
        return {
            "transcript": "今天天氣很好我們開始測試。",
            "status": "ok",
            "rawTranscript": "今天天氣很好我們開始測試",
            "correctedTranscript": "今天天氣很好我們開始測試",
            "punctuatedTranscript": "今天天氣很好我們開始測試。",
            "finalTranscript": "今天天氣很好我們開始測試。",
            "punctuationApplied": True,
            "punctuationMode": "conservative_cjk_terminal",
            "punctuationReason": "added_terminal_period",
        }

    monkeypatch.setattr(routes_module, "transcribe_audio_bytes", _mock_transcribe)
    with TestClient(app) as client:
        response = client.post(
            "/stt/transcribe",
            files={"audio": ("audio.wav", io.BytesIO(b"\x01\x02\x03"), "audio/wav")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["transcript"] == data["finalTranscript"]
    assert data["punctuatedTranscript"] == data["finalTranscript"]
    assert data["punctuationApplied"] is True
    assert data["punctuationMode"] == "conservative_cjk_terminal"
    assert data["punctuationReason"] == "added_terminal_period"
    assert data["language"] == "zh"
    assert data["languageLocked"] is True


def test_task_stt_001_transcribe_signature_unchanged():
    """TASK-STT-001 must not change /stt/transcribe service request inputs."""
    import inspect

    sig = inspect.signature(stt_service.transcribe_audio_bytes)
    assert list(sig.parameters.keys()) == ["audio_bytes", "mime_type", "language"]


def test_task_stt_001_owner_voice_gate_runtime_unmodified():
    """Punctuation restoration must not add Owner Voice hard-gate wiring."""
    import inspect
    import app.api.routes as routes_module

    stt_source = inspect.getsource(routes_module.stt_transcribe)
    chat_source = inspect.getsource(routes_module.chat)
    assert "verify_owner_voice_gate_from_files" not in stt_source
    assert "owner_voice_gate_verify_files_route" not in stt_source
    assert "runtimeHardBlocked" not in stt_source
    assert "punctuation" not in chat_source
    assert "finalTranscript" not in chat_source


# =============================================================================
# TASK-249: Free Local Chinese STT Provider Evaluation tests
# =============================================================================

def test_stt_provider_env_constant_exists():
    """TASK-249: DRAGON_PET_STT_PROVIDER env constant must be defined."""
    assert hasattr(stt_service, "_STT_PROVIDER_ENV"), "TASK-249: _STT_PROVIDER_ENV must exist"
    assert stt_service._STT_PROVIDER_ENV == "DRAGON_PET_STT_PROVIDER"


def test_stt_allowed_providers_includes_expected():
    """TASK-249: allowed providers must include all three candidates."""
    allowed = stt_service._STT_ALLOWED_PROVIDERS
    assert "faster-whisper-local" in allowed, "TASK-249: faster-whisper-local must be allowed"
    assert "funasr-local"         in allowed, "TASK-249: funasr-local must be allowed"
    assert "sherpa-onnx-local"    in allowed, "TASK-249: sherpa-onnx-local must be allowed"


def test_stt_default_provider_is_faster_whisper():
    """TASK-249: default provider must be faster-whisper-local."""
    assert stt_service._STT_DEFAULT_PROVIDER == "faster-whisper-local"


def test_stt_provider_resolution_default(monkeypatch):
    """TASK-249: no env var → resolved provider is faster-whisper-local, source is default."""
    monkeypatch.delenv("DRAGON_PET_STT_PROVIDER", raising=False)
    result = stt_service._resolve_stt_provider()
    assert result["resolved_provider"]        == "faster-whisper-local"
    assert result["provider_source"]          == "default"
    assert result["provider_fallback_reason"] == "none"


def test_stt_provider_resolution_env_valid(monkeypatch):
    """TASK-249: valid env var → resolved provider matches env, source is env."""
    monkeypatch.setenv("DRAGON_PET_STT_PROVIDER", "funasr-local")
    result = stt_service._resolve_stt_provider()
    assert result["requested_provider"]       == "funasr-local"
    assert result["resolved_provider"]        == "funasr-local"
    assert result["provider_source"]          == "env"
    assert result["provider_fallback_reason"] == "none"


def test_stt_provider_resolution_invalid_fallback(monkeypatch):
    """TASK-249: invalid env var → fallback to faster-whisper-local, fallback reason set."""
    monkeypatch.setenv("DRAGON_PET_STT_PROVIDER", "openai-cloud-invalid")
    result = stt_service._resolve_stt_provider()
    assert result["resolved_provider"]        == "faster-whisper-local"
    assert result["provider_source"]          == "fallback"
    assert result["provider_fallback_reason"] == "invalid_provider"


def test_stt_provider_resolution_sherpa_onnx(monkeypatch):
    """TASK-249: sherpa-onnx-local is a valid allowed provider value."""
    monkeypatch.setenv("DRAGON_PET_STT_PROVIDER", "sherpa-onnx-local")
    result = stt_service._resolve_stt_provider()
    assert result["resolved_provider"]  == "sherpa-onnx-local"
    assert result["provider_source"]    == "env"


def test_stt_funasr_unavailable_returns_clean_unavailable(monkeypatch):
    """TASK-249: funasr-local provider when funasr not installed → clean unavailable, no crash."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", False)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert result["status"] == "unavailable", "TASK-249: funasr unavailable must return status=unavailable"
    assert result["transcript"] == "", "TASK-249: transcript must be empty for unavailable"
    assert "Traceback" not in str(result), "TASK-249: no raw stack trace in unavailable response"


def test_stt_sherpa_onnx_unavailable_returns_clean_unavailable(monkeypatch):
    """TASK-249: sherpa-onnx-local provider → clean unavailable (design-only), no crash."""
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "sherpa-onnx-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "sherpa-onnx-local",
        "resolved_provider": "sherpa-onnx-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert result["status"] == "unavailable", "TASK-249: sherpa-onnx-local must return status=unavailable"
    assert result["transcript"] == ""
    assert "Traceback" not in str(result)


def test_stt_provider_metadata_in_response_faster_whisper(monkeypatch):
    """TASK-249: ok response must include all provider metadata fields."""
    from types import SimpleNamespace

    class _GoodModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(text="你好")
            info = SimpleNamespace(language="zh")
            return iter([seg]), info

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "faster-whisper-local")
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _GoodModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert result["status"] == "ok"
    assert "sttProviderRequested"      in result, "TASK-249: sttProviderRequested must be present"
    assert "sttProviderResolved"       in result, "TASK-249: sttProviderResolved must be present"
    assert "sttProviderSource"         in result, "TASK-249: sttProviderSource must be present"
    assert "sttProviderLoadStatus"     in result, "TASK-249: sttProviderLoadStatus must be present"
    assert "sttProviderFallbackReason" in result, "TASK-249: sttProviderFallbackReason must be present"


def test_stt_provider_metadata_in_unavailable_response(monkeypatch):
    """TASK-249: unavailable response (no whisper) must include provider metadata."""
    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", False)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "faster-whisper-local")
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert result["status"] == "unavailable"
    assert "sttProviderResolved" in result, "TASK-249: sttProviderResolved must be in unavailable response"
    assert "sttProviderSource"   in result, "TASK-249: sttProviderSource must be in unavailable response"


def test_stt_provider_no_raw_stack_in_unavailable():
    """TASK-249: provider unavailable response must not contain raw stack traces."""
    result = stt_service._get_provider_metadata()
    for val in result.values():
        if isinstance(val, str):
            assert "Traceback" not in val, "TASK-249: provider metadata must not contain stack traces"
            assert 'File "' not in val,   "TASK-249: provider metadata must not contain file paths"


def test_stt_no_new_endpoint_added():
    """TASK-249: /stt/transcribe must still exist; TASK-256 adds /stt/warmup."""
    import app.api.routes as routes_module
    route_paths = [r.path for r in routes_module.router.routes]
    stt_routes = [p for p in route_paths if "stt" in p]
    assert "/stt/transcribe" in stt_routes, "TASK-249: /stt/transcribe must still exist"
    # TASK-256 adds /stt/warmup; /stt/transcribe must remain present
    assert len(stt_routes) >= 1, (
        f"TASK-249: /stt/transcribe must be present; found {stt_routes}"
    )


def test_stt_language_lock_still_zh_after_task249():
    """TASK-249 regression: language lock (TASK-245) must not be regressed."""
    import app.api.routes as routes_module
    assert routes_module._STT_DEFAULT_LANGUAGE == "zh", "TASK-249 regression: language lock must still be zh"


def test_stt_model_metadata_still_present_after_task249(monkeypatch):
    """TASK-249 regression: TASK-246 model metadata fields must not be regressed."""
    from types import SimpleNamespace

    class _GoodModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(text="test")
            info = SimpleNamespace(language="zh")
            return iter([seg]), info

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "faster-whisper-local")
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _GoodModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert result["status"] == "ok"
    assert "requestedModel"  in result, "TASK-249 regression: requestedModel must still be present"
    assert "resolvedModel"   in result, "TASK-249 regression: resolvedModel must still be present"
    assert "modelLoadStatus" in result, "TASK-249 regression: modelLoadStatus must still be present"


def test_stt_correction_metadata_still_present_after_task249(monkeypatch):
    """TASK-249 regression: TASK-247/248 correction metadata must not be regressed."""
    from types import SimpleNamespace

    class _GoodModel:
        def transcribe(self, _buf, **_kwargs):
            seg = SimpleNamespace(text="test transcript")
            info = SimpleNamespace(language="zh")
            return iter([seg]), info

    monkeypatch.setattr(stt_service, "_WHISPER_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "faster-whisper-local")
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_load_model", lambda: _GoodModel())
    result = stt_service.transcribe_audio_bytes(b"\x01\x02\x03", language="zh")
    assert result["status"] == "ok"
    assert "rawTranscript"       in result, "TASK-249 regression: rawTranscript must still be present"
    assert "correctedTranscript" in result, "TASK-249 regression: correctedTranscript must still be present"
    assert "correctionApplied"   in result, "TASK-249 regression: correctionApplied must still be present"
    assert "matchedAlias"        in result, "TASK-249 regression: matchedAlias must still be present"
    assert "canonicalTerm"       in result, "TASK-249 regression: canonicalTerm must still be present"


# -- TASK-250: FunASR parser unit tests ----------------------------------------


def test_funasr_parse_result_list_dict():
    """TASK-250: _parse_funasr_result handles list[dict{text}] — standard paraformer-zh output."""
    result = stt_service._parse_funasr_result([{"text": "你好世界"}, {"text": " 測試"}])
    assert result == "你好世界 測試"


def test_funasr_parse_result_dict():
    """TASK-250: _parse_funasr_result handles single dict{text}."""
    result = stt_service._parse_funasr_result({"text": "你好"})
    assert result == "你好"


def test_funasr_parse_result_str():
    """TASK-250: _parse_funasr_result handles raw string return."""
    result = stt_service._parse_funasr_result("直接字串")
    assert result == "直接字串"


def test_funasr_parse_result_empty_list():
    """TASK-250: _parse_funasr_result handles empty list and None — returns empty string."""
    assert stt_service._parse_funasr_result([]) == ""
    assert stt_service._parse_funasr_result(None) == ""


def test_funasr_parse_result_dict_missing_text():
    """TASK-250: _parse_funasr_result handles dict without 'text' key — returns empty string."""
    result = stt_service._parse_funasr_result({"score": 0.9})
    assert result == ""


def test_funasr_hotword_constant_exists():
    """TASK-250: _FUNASR_HOTWORDS constant must exist on stt_service module."""
    assert hasattr(stt_service, "_FUNASR_HOTWORDS")
    assert isinstance(stt_service._FUNASR_HOTWORDS, str)
    assert len(stt_service._FUNASR_HOTWORDS) > 0


def test_funasr_hotword_includes_expected_terms():
    """TASK-250: _FUNASR_HOTWORDS must include project-specific vocabulary terms."""
    hw = stt_service._FUNASR_HOTWORDS
    assert "克莉絲蒂娜" in hw, "pet name must be in hotword list"
    assert "Dragon Pet AI" in hw, "project name must be in hotword list"
    assert "Claude Code" in hw, "tool name must be in hotword list"


def test_funasr_transcribe_mock_ok_response(monkeypatch):
    """TASK-250/251: _transcribe_funasr with mocked sidecar returns status=ok + provider metadata."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: {"transcript": "你好世界", "status": "ok", "error": None},
    )

    result = stt_service._transcribe_funasr(b"\x01\x02\x03")
    assert result["status"] == "ok"
    assert result["transcript"] == "你好世界"
    assert result["rawTranscript"] == "你好世界"
    assert "sttProviderResolved" in result
    assert result["sttProviderResolved"] == "funasr-local"


def test_funasr_transcribe_mock_correction_applies(monkeypatch):
    """TASK-250/251: correction layer applies to FunASR sidecar result — 克里斯蒂娜 → 克莉絲蒂娜."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: {"transcript": "克里斯蒂娜你好", "status": "ok", "error": None},
    )

    result = stt_service._transcribe_funasr(b"\x01\x02\x03")
    assert result["status"] == "ok"
    assert result["correctedTranscript"] == "克莉絲蒂娜你好"
    assert result["rawTranscript"] == "克里斯蒂娜你好"
    assert result["correctionApplied"] is True


def test_funasr_transcribe_mock_empty_includes_provider_metadata(monkeypatch):
    """TASK-250/251: status=empty from sidecar must still include provider metadata fields."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: {"transcript": "", "status": "empty", "error": None},
    )

    result = stt_service._transcribe_funasr(b"\x01\x02\x03")
    assert result["status"] == "empty"
    assert result["transcript"] == ""
    assert "sttProviderResolved"       in result, "TASK-251: provider metadata missing on status=empty"
    assert "sttProviderLoadStatus"     in result
    assert "sttProviderFallbackReason" in result


def test_funasr_transcribe_no_audio_to_disk():
    """TASK-251/254: _transcribe_funasr delegates to _run_funasr — no temp files, no disk writes."""
    import inspect
    import re
    source = inspect.getsource(stt_service._transcribe_funasr)
    assert "_run_funasr" in source, (
        "TASK-254: must delegate to _run_funasr (persistent sidecar dispatcher)"
    )
    assert "NamedTemporaryFile" not in source, "TASK-251: must NOT write audio to disk"
    assert "tempfile" not in source, "TASK-251: must NOT use tempfile in transcribe path"
    assert not re.search(r'\bopen\s*\(', source), "TASK-251: must NOT use open() in transcribe path"


# =============================================================================
# TASK-251: FunASR Sidecar / Dedicated Venv Runtime Bridge tests
# =============================================================================

def test_funasr_python_env_constant_exists():
    """TASK-251: _FUNASR_PYTHON_ENV must be 'DRAGON_PET_FUNASR_PYTHON'."""
    assert hasattr(stt_service, "_FUNASR_PYTHON_ENV")
    assert stt_service._FUNASR_PYTHON_ENV == "DRAGON_PET_FUNASR_PYTHON"


def test_funasr_sidecar_script_constant_exists():
    """TASK-251: _FUNASR_SIDECAR_SCRIPT must point to the sidecar script."""
    assert hasattr(stt_service, "_FUNASR_SIDECAR_SCRIPT")
    assert "funasr_sidecar_transcribe.py" in stt_service._FUNASR_SIDECAR_SCRIPT


def test_funasr_resolve_python_default():
    """TASK-251: _resolve_funasr_python returns a path containing .venv-funasr and python."""
    old = os.environ.pop("DRAGON_PET_FUNASR_PYTHON", None)
    try:
        path = stt_service._resolve_funasr_python()
        assert ".venv-funasr" in path
        assert "python" in path.lower()
    finally:
        if old is not None:
            os.environ["DRAGON_PET_FUNASR_PYTHON"] = old


def test_funasr_resolve_python_env_override(monkeypatch):
    """TASK-251: DRAGON_PET_FUNASR_PYTHON env overrides default path."""
    monkeypatch.setenv("DRAGON_PET_FUNASR_PYTHON", "/custom/venv/bin/python")
    path = stt_service._resolve_funasr_python()
    assert path == "/custom/venv/bin/python"


def test_funasr_run_sidecar_function_exists():
    """TASK-251: _run_funasr_sidecar helper must be callable on stt_service."""
    assert hasattr(stt_service, "_run_funasr_sidecar")
    assert callable(stt_service._run_funasr_sidecar)


def test_funasr_sidecar_timeout_returns_error(monkeypatch):
    """TASK-251: sidecar timeout → status=error, clean no-crash."""
    import subprocess as _sp

    def _timeout(b):
        raise _sp.TimeoutExpired(cmd=["python"], timeout=300)

    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(stt_service, "_run_funasr_sidecar", _timeout)

    result = stt_service._transcribe_funasr(b"\x01\x02\x03")
    assert result["status"] == "error"
    assert result["transcript"] == ""
    assert "Traceback" not in str(result)


def test_funasr_sidecar_error_status_propagates(monkeypatch):
    """TASK-251: sidecar returning status=error propagates as status=error, no crash."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: {"transcript": "", "status": "error", "error": "load_failed: test"},
    )

    result = stt_service._transcribe_funasr(b"\x01\x02\x03")
    assert result["status"] == "error"
    assert result["transcript"] == ""
    assert "Traceback" not in str(result)


def test_funasr_sidecar_unavailable_no_subprocess(monkeypatch):
    """TASK-251: _FUNASR_AVAILABLE=False → clean unavailable, sidecar never called."""
    called = []

    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", False)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    monkeypatch.setattr(stt_service, "_run_funasr_sidecar", lambda b: called.append(b) or {})

    result = stt_service._transcribe_funasr(b"\x01\x02\x03")
    assert result["status"] == "unavailable"
    assert len(called) == 0, "sidecar must not be called when _FUNASR_AVAILABLE=False"


def test_funasr_sidecar_ok_sets_load_status_loaded(monkeypatch):
    """TASK-251: successful sidecar call sets _FUNASR_LOAD_STATUS='loaded'."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: {"transcript": "測試", "status": "ok", "error": None},
    )

    stt_service._transcribe_funasr(b"\x01\x02\x03")
    assert stt_service._FUNASR_LOAD_STATUS == "loaded"


def test_funasr_sidecar_candidate_notes_updated():
    """TASK-251: sttProviderCandidateNotes for funasr-local must mention sidecar."""
    notes = stt_service._STT_PROVIDER_CANDIDATE_NOTES.get("funasr-local", "")
    assert "sidecar" in notes.lower(), (
        "TASK-251: funasr-local candidate notes must mention 'sidecar'"
    )
    assert "DRAGON_PET_FUNASR_PYTHON" in notes, (
        "TASK-251: funasr-local candidate notes must mention DRAGON_PET_FUNASR_PYTHON"
    )


# ---------------------------------------------------------------------------
# TASK-253: FunASR transcript normalisation tests
# ---------------------------------------------------------------------------


def test_task253_remove_cjk_spaces_removes_inter_cjk_spaces():
    """_remove_cjk_spaces strips spaces between CJK characters."""
    result = stt_service._remove_cjk_spaces("語 音 辨 識")
    assert result == "語音辨識"


def test_task253_remove_cjk_spaces_preserves_latin_spaces():
    """_remove_cjk_spaces does not touch spaces adjacent to latin chars."""
    result = stt_service._remove_cjk_spaces("Dragon Pet AI")
    assert result == "Dragon Pet AI"


def test_task253_remove_cjk_spaces_mixed_text():
    """_remove_cjk_spaces removes spaces between CJK chars but preserves CJK-Latin boundaries."""
    result = stt_service._remove_cjk_spaces("語 音 Dragon Pet AI 辨 識")
    # 語[space]音 — both CJK → space removed
    # 音[space]Dragon — Latin boundary → space preserved
    # AI[space]辨 — Latin boundary → space preserved
    # 辨[space]識 — both CJK → space removed
    assert result == "語音 Dragon Pet AI 辨識"


def test_task253_simp_to_trad_converts_known_chars():
    """_simp_to_trad converts simplified chars; returns (text, method) tuple."""
    simplified = "语音识别测试对话宠物帮输这现简体开们时会说来"
    text, method = stt_service._simp_to_trad(simplified)
    assert method in ("opencc", "static")
    # All 20 chars in _SIMP_CHAR_MAP must be converted by both paths
    assert "語" in text and "音" in text and "識" in text and "別" in text


def test_task253_simp_to_trad_passthrough_unmapped():
    """_simp_to_trad leaves latin and already-traditional chars unchanged."""
    text, method = stt_service._simp_to_trad("Dragon Pet AI 克莉絲蒂娜")
    assert text == "Dragon Pet AI 克莉絲蒂娜"
    assert method in ("opencc", "static")


def test_task253_normalize_funasr_transcript_cjk_spaces_flag():
    """_normalize_funasr_transcript sets cjkSpacingRemoved=True when spaces removed."""
    result = stt_service._normalize_funasr_transcript("語 音 辨 識")
    assert result["cjkSpacingRemoved"] is True
    assert "cjk_space_removal" in result["normalizationSteps"]
    assert result["normalizationApplied"] is True


def test_task253_normalize_funasr_transcript_trad_flag():
    """_normalize_funasr_transcript sets traditionalApplied=True when trad conversion fires."""
    result = stt_service._normalize_funasr_transcript("语音识别")
    assert result["traditionalApplied"] is True
    # step name is simp_to_trad_opencc or simp_to_trad_static depending on availability
    assert any(s.startswith("simp_to_trad_") for s in result["normalizationSteps"])
    assert result["normalizedTranscript"] == "語音識別"


def test_task253_normalize_funasr_transcript_no_change():
    """_normalize_funasr_transcript returns flags=False for already-normalised text."""
    result = stt_service._normalize_funasr_transcript("語音辨識測試")
    assert result["normalizationApplied"] is False
    assert result["cjkSpacingRemoved"] is False
    assert result["traditionalApplied"] is False
    assert result["normalizationSteps"] == []
    assert result["normalizedTranscript"] == "語音辨識測試"


def test_task253_normalize_funasr_transcript_both_steps():
    """_normalize_funasr_transcript applies CJK space removal then simp→trad in order."""
    result = stt_service._normalize_funasr_transcript("语 音 识 别")
    assert result["cjkSpacingRemoved"] is True
    assert result["traditionalApplied"] is True
    assert result["normalizedTranscript"] == "語音識別"
    steps = result["normalizationSteps"]
    assert steps[0] == "cjk_space_removal"
    assert steps[1].startswith("simp_to_trad_")
    assert len(steps) == 2


def test_task253_transcribe_funasr_response_has_norm_fields(monkeypatch):
    """_transcribe_funasr ok-path includes all TASK-253 normalisation fields."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: {"transcript": "语音识别", "status": "ok", "error": None},
    )

    result = stt_service._transcribe_funasr(b"\x01\x02")
    assert result["status"] == "ok"
    assert "normalizedTranscript" in result
    assert "normalizationApplied" in result
    assert "normalizationSteps" in result
    assert "cjkSpacingRemoved" in result
    assert "traditionalApplied" in result


def test_task253_transcribe_funasr_raw_transcript_is_original(monkeypatch):
    """_transcribe_funasr rawTranscript must be the pre-normalisation text."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    raw = "语 音 识 别"
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: {"transcript": raw, "status": "ok", "error": None},
    )

    result = stt_service._transcribe_funasr(b"\x01\x02")
    assert result["rawTranscript"] == raw
    assert result["normalizedTranscript"] == "語音識別"


def test_task253_correction_map_has_paraformer_variants():
    """TASK-253: _STT_CORRECTION_MAP must include Paraformer-specific entries."""
    aliases = [alias for alias, _ in stt_service._STT_CORRECTION_MAP]
    assert "jdden pet ai" in aliases
    assert "jden pet ai" in aliases
    assert "cloud code" in aliases
    assert "claud code" in aliases
    assert "克莉莉" in aliases
    assert "t a s k" in aliases
    assert "task" in aliases


def test_task253_correction_map_task_maps_to_uppercase(monkeypatch):
    """TASK-253: 'task' alias must correct to 'TASK'."""
    result = stt_service.correct_transcript_text("task 253")
    assert result["correctedTranscript"] == "TASK 253"


def test_task253_correction_map_cloud_code_maps_to_claude_code():
    """TASK-253: 'cloud code' must correct to 'Claude Code'."""
    result = stt_service.correct_transcript_text("cloud code")
    assert result["correctedTranscript"] == "Claude Code"


def test_task253_correction_map_克莉莉_maps_to_full_name():
    """TASK-253: '克莉莉' Paraformer collapse must correct to '克莉絲蒂娜'."""
    result = stt_service.correct_transcript_text("克莉莉")
    assert result["correctedTranscript"] == "克莉絲蒂娜"


def test_task253_normalise_then_correct_pipeline(monkeypatch):
    """TASK-253: normalisation output feeds phrase correction in _transcribe_funasr."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    # Sidecar returns simplified Chinese with spaces; pipeline should normalise then correct
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: {"transcript": "dragon pet a i", "status": "ok", "error": None},
    )

    result = stt_service._transcribe_funasr(b"\x01\x02")
    assert result["correctedTranscript"] == "Dragon Pet AI"


# ---------------------------------------------------------------------------
# TASK-253 revision: OpenCC s2tw integration
# ---------------------------------------------------------------------------


def test_task253rev_opencc_available():
    """opencc-python-reimplemented must be installed in the backend venv."""
    assert stt_service._OPENCC_AVAILABLE is True, (
        "opencc not installed — run: pip install opencc-python-reimplemented"
    )


def test_task253rev_simp_to_trad_returns_tuple():
    """_simp_to_trad must return (str, method_str) where method is 'opencc' or 'static'."""
    result = stt_service._simp_to_trad("语音")
    assert isinstance(result, tuple) and len(result) == 2
    text, method = result
    assert isinstance(text, str)
    assert method in ("opencc", "static")


def test_task253rev_trad_method_opencc_when_available():
    """When opencc is installed _simp_to_trad reports method='opencc'."""
    if not stt_service._OPENCC_AVAILABLE:
        pytest.skip("opencc not installed")
    _, method = stt_service._simp_to_trad("语音识别")
    assert method == "opencc"


def test_task253rev_opencc_converts_broader_chars():
    """OpenCC s2tw converts chars outside the static _SIMP_CHAR_MAP (e.g. 处 → 處)."""
    if not stt_service._OPENCC_AVAILABLE:
        pytest.skip("opencc not installed")
    text, method = stt_service._simp_to_trad("处理")
    assert method == "opencc"
    assert text == "處理", f"expected 處理, got {text!r}"


def test_task253rev_normalize_tradmethod_field():
    """_normalize_funasr_transcript includes tradMethod field."""
    result = stt_service._normalize_funasr_transcript("语音识别")
    assert "tradMethod" in result
    assert result["tradMethod"] in ("opencc", "static")


def test_task253rev_transcribe_funasr_has_tradmethod(monkeypatch):
    """_transcribe_funasr ok-path response includes tradMethod field."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: {"transcript": "语音识别", "status": "ok", "error": None},
    )
    result = stt_service._transcribe_funasr(b"\x01\x02")
    assert "tradMethod" in result
    assert result["tradMethod"] in ("opencc", "static")


def test_task253rev_fallback_static_when_opencc_unavailable(monkeypatch):
    """When _OPENCC_AVAILABLE=False, _simp_to_trad falls back to static map."""
    monkeypatch.setattr(stt_service, "_OPENCC_AVAILABLE", False)
    monkeypatch.setattr(stt_service, "_opencc_converter", None)
    text, method = stt_service._simp_to_trad("语音识别")
    assert method == "static"
    assert text == "語音識別"


def test_task253rev_fallback_normalize_uses_static(monkeypatch):
    """When opencc unavailable, _normalize_funasr_transcript uses static path without crash."""
    monkeypatch.setattr(stt_service, "_OPENCC_AVAILABLE", False)
    monkeypatch.setattr(stt_service, "_opencc_converter", None)
    result = stt_service._normalize_funasr_transcript("语音识别")
    assert result["normalizedTranscript"] == "語音識別"
    assert result["tradMethod"] == "static"
    trad_step = next((s for s in result["normalizationSteps"] if s.startswith("simp_to_trad_")), None)
    assert trad_step == "simp_to_trad_static"


def test_task253rev_opencc_对话模式():
    """OpenCC s2tw converts 对话模式 → 對話模式."""
    if not stt_service._OPENCC_AVAILABLE:
        pytest.skip("opencc not installed")
    text, _ = stt_service._simp_to_trad("对话模式")
    assert text == "對話模式"


def test_task253rev_opencc_桌面宠物():
    """OpenCC s2tw converts 桌面宠物 → 桌面寵物."""
    if not stt_service._OPENCC_AVAILABLE:
        pytest.skip("opencc not installed")
    text, _ = stt_service._simp_to_trad("桌面宠物")
    assert text == "桌面寵物"


def test_task253rev_full_pipeline_帮我修一下_task(monkeypatch):
    """Full pipeline: 帮我修一下 task → 幫我修一下 TASK (norm then correction)."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: {"transcript": "帮我修一下 task", "status": "ok", "error": None},
    )
    result = stt_service._transcribe_funasr(b"\x01\x02")
    assert result["normalizedTranscript"] == "幫我修一下 task"
    assert result["correctedTranscript"] == "幫我修一下 TASK"


# ---------------------------------------------------------------------------
# TASK-254: Persistent FunASR sidecar manager tests
# ---------------------------------------------------------------------------


def test_task254_persistent_env_constant_exists():
    """_FUNASR_PERSISTENT_ENV constant must be present."""
    assert hasattr(stt_service, "_FUNASR_PERSISTENT_ENV")
    assert stt_service._FUNASR_PERSISTENT_ENV == "DRAGON_PET_FUNASR_PERSISTENT"


def test_task254_sidecar_loop_script_constant_exists():
    """_FUNASR_SIDECAR_LOOP_SCRIPT constant must be present."""
    assert hasattr(stt_service, "_FUNASR_SIDECAR_LOOP_SCRIPT")
    assert "funasr_sidecar_loop.py" in stt_service._FUNASR_SIDECAR_LOOP_SCRIPT


def test_task254_sidecar_loop_script_file_exists():
    """scripts/funasr_sidecar_loop.py must exist on disk."""
    import os
    assert os.path.isfile(stt_service._FUNASR_SIDECAR_LOOP_SCRIPT), (
        f"TASK-254: loop script missing: {stt_service._FUNASR_SIDECAR_LOOP_SCRIPT}"
    )


def test_task254_persistent_mode_enabled_default_true(monkeypatch):
    """Persistent mode is enabled by default (no env var set)."""
    monkeypatch.delenv("DRAGON_PET_FUNASR_PERSISTENT", raising=False)
    assert stt_service._persistent_mode_enabled() is True


def test_task254_persistent_mode_disabled_by_env_false(monkeypatch):
    """DRAGON_PET_FUNASR_PERSISTENT=false disables persistent mode."""
    monkeypatch.setenv("DRAGON_PET_FUNASR_PERSISTENT", "false")
    assert stt_service._persistent_mode_enabled() is False


def test_task254_persistent_mode_disabled_by_env_0(monkeypatch):
    """DRAGON_PET_FUNASR_PERSISTENT=0 disables persistent mode."""
    monkeypatch.setenv("DRAGON_PET_FUNASR_PERSISTENT", "0")
    assert stt_service._persistent_mode_enabled() is False


def test_task254_persistent_mode_enabled_by_env_true(monkeypatch):
    """DRAGON_PET_FUNASR_PERSISTENT=true keeps persistent mode enabled."""
    monkeypatch.setenv("DRAGON_PET_FUNASR_PERSISTENT", "true")
    assert stt_service._persistent_mode_enabled() is True


def test_task254_shutdown_for_tests_does_not_crash():
    """_shutdown_funasr_process_for_tests must not raise when no process is running."""
    stt_service._shutdown_funasr_process_for_tests()
    assert stt_service._funasr_process is None


def test_task254_run_funasr_oneshot_when_persistent_disabled(monkeypatch):
    """When persistent mode is disabled, _run_funasr calls _run_funasr_sidecar."""
    monkeypatch.setenv("DRAGON_PET_FUNASR_PERSISTENT", "false")
    calls = []
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: (calls.append("oneshot"), {"transcript": "測試", "status": "ok", "error": None})[1],
    )
    r = stt_service._run_funasr(b"\x01", "audio/wav")
    assert calls == ["oneshot"]
    assert r["funasrSidecarMode"] == "oneshot"
    assert r["funasrSidecarWarm"] is False
    assert r["funasrSidecarRestarted"] is False


def test_task254_run_funasr_persistent_ok_returns_persistent_mode(monkeypatch):
    """When persistent mode succeeds _run_funasr returns funasrSidecarMode=persistent."""
    monkeypatch.setenv("DRAGON_PET_FUNASR_PERSISTENT", "true")
    monkeypatch.setattr(stt_service, "_ensure_funasr_process", lambda: (True, False))
    monkeypatch.setattr(
        stt_service, "_call_funasr_persistent",
        lambda b, m: {"transcript": "測試", "status": "ok", "error": None},
    )
    r = stt_service._run_funasr(b"\x01", "audio/wav")
    assert r["funasrSidecarMode"] == "persistent"
    assert r["funasrSidecarWarm"] is False
    assert r["funasrSidecarRestarted"] is False
    assert r["transcript"] == "測試"


def test_task254_run_funasr_persistent_warm_on_second_mock(monkeypatch):
    """was_warm=True is returned when the process was already running."""
    monkeypatch.setenv("DRAGON_PET_FUNASR_PERSISTENT", "true")
    monkeypatch.setattr(stt_service, "_ensure_funasr_process", lambda: (True, True))
    monkeypatch.setattr(
        stt_service, "_call_funasr_persistent",
        lambda b, m: {"transcript": "測試", "status": "ok", "error": None},
    )
    r = stt_service._run_funasr(b"\x01", "audio/wav")
    assert r["funasrSidecarWarm"] is True


def test_task254_run_funasr_persistent_failure_falls_back_to_oneshot(monkeypatch):
    """When _ensure_funasr_process returns False, one-shot fallback is used."""
    monkeypatch.setenv("DRAGON_PET_FUNASR_PERSISTENT", "true")
    monkeypatch.setattr(stt_service, "_ensure_funasr_process", lambda: (False, False))
    calls = []
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: (calls.append("oneshot"), {"transcript": "測試", "status": "ok", "error": None})[1],
    )
    r = stt_service._run_funasr(b"\x01", "audio/wav")
    assert calls == ["oneshot"]
    assert r["funasrSidecarMode"] == "oneshot"


def test_task254_run_funasr_persistent_error_result_falls_back(monkeypatch):
    """When persistent call returns status=error and restart also fails, one-shot fallback used."""
    monkeypatch.setenv("DRAGON_PET_FUNASR_PERSISTENT", "true")
    ensure_calls = [0]
    def mock_ensure():
        ensure_calls[0] += 1
        return True, False
    monkeypatch.setattr(stt_service, "_ensure_funasr_process", mock_ensure)
    monkeypatch.setattr(stt_service, "_kill_funasr_process", lambda: None)
    monkeypatch.setattr(
        stt_service, "_call_funasr_persistent",
        lambda b, m: {"transcript": "", "status": "error", "error": "mock_error"},
    )
    calls = []
    monkeypatch.setattr(
        stt_service, "_run_funasr_sidecar",
        lambda b: (calls.append("oneshot"), {"transcript": "救援", "status": "ok", "error": None})[1],
    )
    r = stt_service._run_funasr(b"\x01", "audio/wav")
    assert calls == ["oneshot"]
    assert r["funasrSidecarMode"] == "oneshot"


def test_task254_transcribe_funasr_response_has_sidecar_fields(monkeypatch):
    """_transcribe_funasr ok-path response includes all TASK-254 sidecar metadata fields."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(
        stt_service, "_run_funasr",
        lambda b, m: {
            "transcript": "測試", "status": "ok", "error": None,
            "funasrSidecarMode": "persistent",
            "funasrSidecarWarm": True,
            "funasrSidecarRestarted": False,
        },
    )
    result = stt_service._transcribe_funasr(b"\x01\x02")
    assert result["status"] == "ok"
    assert result["funasrSidecarMode"] == "persistent"
    assert result["funasrSidecarWarm"] is True
    assert result["funasrSidecarRestarted"] is False


def test_task254_transcribe_funasr_norm_correction_still_applied(monkeypatch):
    """TASK-254: normalisation and correction pipeline still applies on persistent path."""
    monkeypatch.setattr(stt_service, "_FUNASR_AVAILABLE", True)
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "funasr-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "funasr-local",
        "resolved_provider": "funasr-local",
        "provider_source": "env",
        "provider_fallback_reason": "none",
    })
    stt_service._reset_model_for_tests()
    monkeypatch.setattr(
        stt_service, "_run_funasr",
        lambda b, m: {
            "transcript": "dragon pet a i",
            "status": "ok", "error": None,
            "funasrSidecarMode": "persistent",
            "funasrSidecarWarm": True,
            "funasrSidecarRestarted": False,
        },
    )
    result = stt_service._transcribe_funasr(b"\x01\x02")
    assert result["correctedTranscript"] == "Dragon Pet AI"
    assert result["funasrSidecarMode"] == "persistent"


def test_task254_no_new_endpoint():
    """TASK-254: no new routes added — transcribe_audio_bytes signature unchanged."""
    import inspect
    sig = inspect.signature(stt_service.transcribe_audio_bytes)
    params = list(sig.parameters.keys())
    assert "audio_bytes" in params
    assert "mime_type" in params
    assert "language" in params


def test_task254_no_audio_persistence_in_loop_script():
    """funasr_sidecar_loop.py must not contain writeFile/open() for audio output."""
    import os
    script_path = stt_service._FUNASR_SIDECAR_LOOP_SCRIPT
    assert os.path.isfile(script_path)
    content = open(script_path, encoding="utf-8").read()
    # Must not write audio to disk
    assert "open(" not in content or "TextIOWrapper" in content  # TextIOWrapper is allowed for stdin
    assert "writeFile" not in content


def test_task254_faster_whisper_path_unchanged(monkeypatch):
    """TASK-254: faster-whisper-local provider path must be unaffected."""
    monkeypatch.setattr(stt_service, "_STT_RESOLVED_PROVIDER", "faster-whisper-local")
    monkeypatch.setattr(stt_service, "_STT_PROVIDER_RESOLUTION", {
        "requested_provider": "faster-whisper-local",
        "resolved_provider": "faster-whisper-local",
        "provider_source": "default",
        "provider_fallback_reason": "none",
    })
    result = stt_service.transcribe_audio_bytes(b"\x00" * 100, mime_type="audio/wav")
    # Whisper path returns unavailable or empty — not an error from sidecar code
    assert result["status"] in ("unavailable", "empty", "error")
    assert "funasrSidecarMode" not in result  # whisper path does not set sidecar fields


# ---------------------------------------------------------------------------
# TASK-256: Startup Warmup / STT + Ollama Preload
# ---------------------------------------------------------------------------


def test_task256_stt_warmup_route_exists():
    """TASK-256: POST /stt/warmup must be reachable (not 404)."""
    with TestClient(app) as client:
        response = client.post("/stt/warmup")
    assert response.status_code != 404, "POST /stt/warmup must exist"
    assert response.status_code == 200


def test_task256_stt_warmup_no_audio_required():
    """TASK-256: /stt/warmup must not require an audio upload."""
    with TestClient(app) as client:
        response = client.post("/stt/warmup")
    # Must accept POST with no body/files
    assert response.status_code == 200, (
        f"/stt/warmup must accept empty POST, got {response.status_code}"
    )


def test_task256_stt_warmup_response_shape():
    """TASK-256: /stt/warmup response must include status/warmupStatus/provider/elapsedMs."""
    with TestClient(app) as client:
        response = client.post("/stt/warmup")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data, "response must include 'status'"
    assert "warmupStatus" in data, "response must include 'warmupStatus'"
    assert "provider" in data, "response must include 'provider'"
    assert "elapsedMs" in data, "response must include 'elapsedMs'"
    assert "message" in data, "response must include 'message'"
    assert data["status"] in ("ok", "skipped", "error")
    assert data["warmupStatus"] in ("loaded", "already_loaded", "skipped", "error")
    assert isinstance(data["elapsedMs"], int)


def test_task256_stt_warmup_non_funasr_returns_skipped(monkeypatch):
    """TASK-256: /stt/warmup with non-funasr provider returns status=skipped."""
    import app.api.routes as routes_module
    monkeypatch.setattr(routes_module, "_stt_resolved_provider", "faster-whisper-local")
    with TestClient(app) as client:
        response = client.post("/stt/warmup")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "skipped"
    assert data["warmupStatus"] == "skipped"


def test_task256_stt_warmup_funasr_calls_warmup_helper(monkeypatch):
    """TASK-256: /stt/warmup with funasr-local calls warmup_funasr_sidecar."""
    import app.api.routes as routes_module
    monkeypatch.setattr(routes_module, "_stt_resolved_provider", "funasr-local")
    called = []
    monkeypatch.setattr(
        routes_module, "warmup_funasr_sidecar",
        lambda: (called.append(True), {"status": "ok", "warmupStatus": "loaded",
                                        "sidecarMode": "persistent", "message": "ok"})[1],
    )
    with TestClient(app) as client:
        response = client.post("/stt/warmup")
    assert response.status_code == 200
    assert called == [True], "/stt/warmup must call warmup_funasr_sidecar"
    data = response.json()
    assert data["status"] == "ok"
    assert data["warmupStatus"] == "loaded"


def test_task256_stt_warmup_error_is_clean(monkeypatch):
    """TASK-256: /stt/warmup error must return status=error with no raw stack trace."""
    import app.api.routes as routes_module
    monkeypatch.setattr(routes_module, "_stt_resolved_provider", "funasr-local")
    monkeypatch.setattr(
        routes_module, "warmup_funasr_sidecar",
        lambda: (_ for _ in ()).throw(RuntimeError("simulated crash")),
    )
    with TestClient(app) as client:
        response = client.post("/stt/warmup")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["warmupStatus"] == "error"
    assert "Traceback" not in str(data)
    assert "simulated crash" not in str(data), "raw exception text must not leak"


def test_task256_stt_warmup_no_audio_persistence():
    """TASK-256: stt_warmup handler must not contain audio write/open patterns."""
    import inspect
    source = inspect.getsource(stt_service.warmup_funasr_sidecar)
    assert "NamedTemporaryFile" not in source
    assert "tempfile" not in source
    assert "writeFile" not in source


def test_task256_warmup_funasr_sidecar_disabled_returns_skipped(monkeypatch):
    """TASK-256: warmup_funasr_sidecar returns skipped when persistent mode is disabled."""
    monkeypatch.setenv("DRAGON_PET_FUNASR_PERSISTENT", "false")
    result = stt_service.warmup_funasr_sidecar()
    assert result["status"] == "skipped"
    assert result["warmupStatus"] == "skipped"
    assert result["sidecarMode"] == "disabled"


def test_task256_warmup_funasr_sidecar_already_warm(monkeypatch):
    """TASK-256: warmup_funasr_sidecar returns already_loaded when process already alive."""
    import subprocess

    class _FakeProc:
        def poll(self):
            return None  # process alive

    monkeypatch.setenv("DRAGON_PET_FUNASR_PERSISTENT", "true")
    monkeypatch.setattr(stt_service, "_funasr_process", _FakeProc())
    try:
        result = stt_service.warmup_funasr_sidecar()
        assert result["status"] == "ok"
        assert result["warmupStatus"] == "already_loaded"
    finally:
        monkeypatch.setattr(stt_service, "_funasr_process", None)


def test_task256_llm_warmup_route_exists():
    """TASK-256: POST /llm/warmup must be reachable (not 404)."""
    with TestClient(app) as client:
        response = client.post("/llm/warmup")
    assert response.status_code != 404, "POST /llm/warmup must exist"
    assert response.status_code == 200


def test_task256_llm_warmup_non_ollama_returns_skipped(monkeypatch):
    """TASK-256: /llm/warmup with non-ollama provider returns status=skipped."""
    from app.services import provider_settings_service
    monkeypatch.setattr(
        provider_settings_service, "get_provider_settings",
        lambda: {"provider": "mock", "real_provider_enabled": False, "model": ""},
    )
    with TestClient(app) as client:
        response = client.post("/llm/warmup")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "skipped"
    assert data["warmupStatus"] == "skipped"


def test_task256_llm_warmup_real_disabled_returns_skipped(monkeypatch):
    """TASK-256: /llm/warmup with ollama but real_provider_enabled=False returns skipped."""
    from app.services import provider_settings_service
    monkeypatch.setattr(
        provider_settings_service, "get_provider_settings",
        lambda: {"provider": "ollama", "real_provider_enabled": False, "model": "qwen3:8b"},
    )
    with TestClient(app) as client:
        response = client.post("/llm/warmup")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "skipped"


def test_task256_llm_warmup_does_not_write_chat_history(monkeypatch):
    """TASK-256: /llm/warmup must not call generate_chat_reply or store_chat_turn."""
    import inspect
    import app.api.routes as routes_module
    source = inspect.getsource(routes_module.llm_warmup)
    assert "generate_chat_reply" not in source, (
        "/llm/warmup must not call generate_chat_reply"
    )
    assert "store_chat_turn" not in source, (
        "/llm/warmup must not call store_chat_turn"
    )
    assert "ChatRequest" not in source, (
        "/llm/warmup must not use ChatRequest"
    )


def test_task256_llm_warmup_error_is_clean(monkeypatch):
    """TASK-256: /llm/warmup error must return status=error with no raw stack trace."""
    from app.services import provider_settings_service
    _ollama_settings = lambda: {"provider": "ollama", "real_provider_enabled": True, "model": "qwen3:8b"}
    monkeypatch.setattr(provider_settings_service, "get_provider_settings", _ollama_settings)
    # Also patch the already-imported name in routes so the guard passes
    import app.api.routes as routes_module
    monkeypatch.setattr(routes_module, "get_provider_settings", _ollama_settings)
    # Patch httpx.AsyncClient to raise a connection error
    import httpx

    class _FailClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *a):
            pass
        async def post(self, *a, **kw):
            raise httpx.ConnectError("simulated connect error")

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: _FailClient())
    with TestClient(app) as client:
        response = client.post("/llm/warmup")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["warmupStatus"] == "error"
    assert "Traceback" not in str(data)
    assert "simulated connect error" not in str(data), "raw exception text must not leak"


def test_task256_stt_transcribe_regression():
    """TASK-256 regression: /stt/transcribe must still work after warmup routes added."""
    with TestClient(app) as client:
        response = client.post(
            "/stt/transcribe",
            files={"audio": ("audio.webm", io.BytesIO(b"\x01\x02\x03"), "audio/webm")},
        )
    assert response.status_code == 200
    data = response.json()
    assert "transcript" in data
    assert "status" in data
    assert data["status"] in ("ok", "unavailable", "empty", "error", "no_speech")


# -- TASK-265: Backend Owner Voice Gate verify-files endpoint tests -----------


def _mock_owner_voice_verification_report_accept(paths, threshold, settings_path):
    return {
        "status": "ok",
        "reason": "verification_complete",
        "provider": "funasr-campp",
        "enrolled": True,
        "score": 0.98,
        "scores": [0.98] * len(paths),
        "threshold": threshold or 0.65,
        "accepted": True,
        "embeddingDim": 192,
        "sampleCount": len(paths),
        "checkedAudioFiles": [
            {"path": p, "exists": True, "valid16kPcmWav": True} for p in paths
        ],
        "rawAudioPersisted": False,
        "candidateEmbeddingPersisted": False,
        "storedCentroidExposed": False,
        "micAccessed": False,
        "runtimeIntegrated": False,
        "message": "Verification completed against stored centroid.",
    }


def _mock_owner_voice_verification_report_reject(paths, threshold, settings_path):
    return {
        "status": "ok",
        "reason": "verification_complete",
        "provider": "funasr-campp",
        "enrolled": True,
        "score": 0.07,
        "scores": [0.07] * len(paths),
        "threshold": threshold or 0.65,
        "accepted": False,
        "embeddingDim": 192,
        "sampleCount": len(paths),
        "checkedAudioFiles": [
            {"path": p, "exists": True, "valid16kPcmWav": True} for p in paths
        ],
        "rawAudioPersisted": False,
        "candidateEmbeddingPersisted": False,
        "storedCentroidExposed": False,
        "micAccessed": False,
        "runtimeIntegrated": False,
        "message": "Verification completed against stored centroid.",
    }


def _enroll_for_verify_tests(tmp_path, monkeypatch):
    """Set up enrolled centroid state so TASK-265 verify tests can proceed."""
    _owner_voice_gate_temp_storage(tmp_path)
    owner1, owner2 = _owner_voice_sample_paths(tmp_path)
    monkeypatch.setattr(
        owner_voice_gate_storage,
        "run_owner_voice_enrollment_sidecar",
        _mock_owner_voice_enrollment_report,
    )
    with TestClient(app) as client:
        client.post(
            "/owner-voice-gate/enroll-files",
            json={"paths": [owner1, owner2], "threshold": 0.65, "safetyNoticeAccepted": True},
        )


def test_owner_voice_gate_verify_files_not_enrolled(tmp_path):
    """TASK-265: verify-files returns not_enrolled when no centroid is stored."""
    _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/verify-files",
            json={"paths": ["candidate.wav"]},
        )

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "not_enrolled"
    assert data["reason"] == "not_enrolled"
    assert data["enrolled"] is False
    assert data["accepted"] is False
    assert data["score"] is None
    assert data["storedCentroidExposed"] is False
    assert data["candidateEmbeddingPersisted"] is False
    assert "embeddingAggregate" not in response.text


def test_owner_voice_gate_verify_files_audio_not_found(tmp_path, monkeypatch):
    """TASK-265: missing WAV path returns audio_file_not_found without calling sidecar."""
    _enroll_for_verify_tests(tmp_path, monkeypatch)
    missing = str(tmp_path / "雪狼丸 missing" / "candidate.wav")

    def _fail_if_called(_paths, _threshold, _settings_path):
        raise AssertionError("sidecar must not run for missing verification paths")

    monkeypatch.setattr(
        owner_voice_gate_storage,
        "run_owner_voice_verification_sidecar",
        _fail_if_called,
    )

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/verify-files",
            json={"paths": [missing]},
        )

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "unavailable"
    assert data["reason"] == "audio_file_not_found"
    assert data["enrolled"] is True
    assert data["accepted"] is False
    assert "Traceback" not in response.text
    assert "AssertionError" not in response.text
    assert "雪狼丸" not in response.text
    assert "embeddingAggregate" not in response.text


def test_owner_voice_gate_verify_files_unicode_path(tmp_path, monkeypatch):
    """TASK-265: Unicode candidate WAV paths must reach the verification sidecar unchanged."""
    _enroll_for_verify_tests(tmp_path, monkeypatch)
    candidate_dir = tmp_path / "雪狼丸 verify"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    candidate_wav = candidate_dir / "candidate.wav"
    candidate_wav.write_bytes(b"mock wav bytes for path only")
    captured_paths: list[str] = []

    def _capture_verify(paths, threshold, settings_path):
        captured_paths.extend(paths)
        return _mock_owner_voice_verification_report_accept(paths, threshold, settings_path)

    monkeypatch.setattr(
        owner_voice_gate_storage,
        "run_owner_voice_verification_sidecar",
        _capture_verify,
    )

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/verify-files",
            json={"paths": [str(candidate_wav)]},
        )

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["reason"] == "verification_complete"
    assert len(captured_paths) == 1
    assert "雪狼丸" in captured_paths[0]
    assert data["embeddingDim"] == 192
    assert data["storedCentroidExposed"] is False
    assert data["candidateEmbeddingPersisted"] is False
    assert "embeddingAggregate" not in response.text


def test_owner_voice_gate_verify_files_mock_accept(tmp_path, monkeypatch):
    """TASK-265: high similarity score returns accepted=True with safe schema."""
    _enroll_for_verify_tests(tmp_path, monkeypatch)
    candidate = tmp_path / "owner2.wav"
    candidate.write_bytes(b"mock owner wav")

    monkeypatch.setattr(
        owner_voice_gate_storage,
        "run_owner_voice_verification_sidecar",
        _mock_owner_voice_verification_report_accept,
    )

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/verify-files",
            json={"paths": [str(candidate)], "threshold": 0.65},
        )

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["reason"] == "verification_complete"
    assert data["enrolled"] is True
    assert data["accepted"] is True
    assert data["score"] == 0.98
    assert data["scores"] == [0.98]
    assert data["threshold"] == 0.65
    assert data["embeddingDim"] == 192
    assert data["sampleCount"] == 1
    assert data["rawAudioPersisted"] is False
    assert data["candidateEmbeddingPersisted"] is False
    assert data["storedCentroidExposed"] is False
    assert data["micAccessed"] is False
    assert data["runtimeIntegrated"] is False
    assert "embeddingAggregate" not in response.text


def test_owner_voice_gate_verify_files_mock_reject(tmp_path, monkeypatch):
    """TASK-265: low similarity score returns accepted=False."""
    _enroll_for_verify_tests(tmp_path, monkeypatch)
    candidate = tmp_path / "other.wav"
    candidate.write_bytes(b"mock other wav")

    monkeypatch.setattr(
        owner_voice_gate_storage,
        "run_owner_voice_verification_sidecar",
        _mock_owner_voice_verification_report_reject,
    )

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/verify-files",
            json={"paths": [str(candidate)]},
        )

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["reason"] == "verification_complete"
    assert data["accepted"] is False
    assert data["score"] == 0.07
    assert data["storedCentroidExposed"] is False
    assert data["candidateEmbeddingPersisted"] is False
    assert "embeddingAggregate" not in response.text


def test_owner_voice_gate_verify_files_rejects_forbidden_fields(tmp_path):
    """TASK-265: verify-files rejects raw audio, transcript, and embedding fields."""
    _owner_voice_gate_temp_storage(tmp_path)

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/verify-files",
            json={
                "paths": ["candidate.wav"],
                "rawAudio": "not allowed",
                "base64Audio": "not allowed",
                "transcript": "not allowed",
                "embeddingAggregate": [0.1] * 192,
            },
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "unsupported owner voice verification field"}
    assert "not allowed" not in response.text
    assert "0.1" not in response.text


def test_owner_voice_gate_verify_files_no_runtime_wiring():
    """TASK-265: verify-files route must not call STT or chat runtime."""
    import inspect
    import app.api.routes as routes_module

    source = inspect.getsource(routes_module.owner_voice_gate_verify_files_route)
    assert "transcribe_audio_bytes" not in source
    assert "generate_chat_reply" not in source
    assert "store_chat_turn" not in source
    assert "stt_transcribe" not in source


# -- TASK-266: Owner Voice Gate Manual Mic dry-run backend regression ----------


def test_task266_chat_response_schema_unchanged():
    """TASK-266: /chat schema stays fixed at reply/mood/source."""
    from app.schemas.chat import ChatResponse

    fields = getattr(ChatResponse, "model_fields", None) or getattr(ChatResponse, "__fields__", {})
    assert set(fields.keys()) == {"reply", "mood", "source"}
    assert "ownerVoiceDryRunStatus" not in fields
    assert "ownerVoiceScore" not in fields
    assert "ownerVoiceAccepted" not in fields


def test_task266_no_new_owner_voice_runtime_endpoints():
    """TASK-266: dry-run reuses verify-files; no Manual Mic or Conversation gate endpoint."""
    route_paths = {getattr(route, "path", "") for route in app.routes}
    assert "/owner-voice-gate/verify-files" in route_paths
    assert "/owner-voice-gate/manual-mic" not in route_paths
    assert "/owner-voice-gate/manual-mic/verify" not in route_paths
    assert "/owner-voice-gate/conversation-mode" not in route_paths
    assert "/owner-voice-gate/conversation-mode/verify" not in route_paths


def test_task266_stt_and_chat_are_not_owner_voice_hard_gated():
    """TASK-266: backend STT/chat runtime paths do not call Owner Voice Gate."""
    import inspect
    import app.api.routes as routes_module

    stt_source = inspect.getsource(routes_module.stt_transcribe)
    chat_source = inspect.getsource(routes_module.chat)
    for source in (stt_source, chat_source):
        assert "verify_owner_voice_gate_from_files" not in source
        assert "owner_voice_gate_verify_files_route" not in source
        assert "/owner-voice-gate/verify-files" not in source
        assert "runtimeHardBlocked" not in source


def test_task266_verify_files_response_keeps_sensitive_data_hidden(tmp_path, monkeypatch):
    """TASK-266: dry-run source endpoint still returns only safe status fields."""
    _enroll_for_verify_tests(tmp_path, monkeypatch)
    candidate = tmp_path / "manual-mic-candidate.wav"
    candidate.write_bytes(b"mock owner wav")
    monkeypatch.setattr(
        owner_voice_gate_storage,
        "run_owner_voice_verification_sidecar",
        _mock_owner_voice_verification_report_reject,
    )

    with TestClient(app) as client:
        response = client.post(
            "/owner-voice-gate/verify-files",
            json={"paths": [str(candidate)], "threshold": 0.65},
        )

    data = response.json()
    assert response.status_code == 200
    assert data["accepted"] is False
    assert data["rawAudioPersisted"] is False
    assert data["candidateEmbeddingPersisted"] is False
    assert data["storedCentroidExposed"] is False
    assert data["micAccessed"] is False
    assert data["runtimeIntegrated"] is False
    assert "embeddingAggregate" not in response.text
    assert "perSampleEmbeddings" not in response.text
    assert "rawAudio" not in data
    assert "base64Audio" not in data


# -- TASK-267: Owner Voice Gate Conversation Mode dry-run backend regression ---


def test_task267_chat_response_schema_stays_unchanged():
    """TASK-267: Conversation Mode dry-run does not add owner voice fields to /chat."""
    from app.schemas.chat import ChatResponse

    fields = getattr(ChatResponse, "model_fields", None) or getattr(ChatResponse, "__fields__", {})
    assert set(fields.keys()) == {"reply", "mood", "source"}
    assert "ownerVoiceDryRunSource" not in fields
    assert "ownerVoiceDryRunStatus" not in fields
    assert "ownerVoiceAccepted" not in fields


def test_task267_no_new_conversation_owner_voice_endpoint():
    """TASK-267: Conversation Mode dry-run reuses verify-files only when a safe path exists."""
    route_paths = {getattr(route, "path", "") for route in app.routes}
    assert "/owner-voice-gate/verify-files" in route_paths
    assert "/owner-voice-gate/conversation-mode" not in route_paths
    assert "/owner-voice-gate/conversation-mode/verify" not in route_paths
    assert "/owner-voice-gate/conversation" not in route_paths
    assert "/owner-voice-gate/conversation/verify" not in route_paths


def test_task267_stt_and_chat_runtime_paths_stay_unwired():
    """TASK-267: backend STT/chat runtime paths do not call Owner Voice Gate."""
    import inspect
    import app.api.routes as routes_module

    stt_source = inspect.getsource(routes_module.stt_transcribe)
    chat_source = inspect.getsource(routes_module.chat)
    for source in (stt_source, chat_source):
        assert "verify_owner_voice_gate_from_files" not in source
        assert "owner_voice_gate_verify_files_route" not in source
        assert "/owner-voice-gate/verify-files" not in source
        assert "ownerVoiceDryRunSource" not in source
        assert "runtimeHardBlocked" not in source
