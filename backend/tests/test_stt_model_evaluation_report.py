import importlib.util
import io
from datetime import datetime, timezone
from pathlib import Path
import wave

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "stt_model_evaluation_report.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("stt_model_evaluation_report", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_wav(path: Path, sample_value: int = 0) -> None:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(
            b"".join(
                int(sample_value).to_bytes(2, "little", signed=True)
                for _ in range(1600)
            )
        )
    path.write_bytes(buf.getvalue())


def test_task_stt_006a_parse_models():
    module = _load_module()

    assert module.parse_models(None) == ["tiny", "base", "small"]
    assert module.parse_models("tiny, base,small,base") == ["tiny", "base", "small"]

    with pytest.raises(ValueError, match="Unsupported model"):
        module.parse_models("tiny,medium")


def test_task_stt_006a_report_schema_with_mock_transcriber(tmp_path, monkeypatch):
    module = _load_module()
    audio = tmp_path / "sample.wav"
    _write_wav(audio, sample_value=1000)
    samples = module.build_samples([str(audio)], ["manual mic sample"])
    monkeypatch.setattr(
        module,
        "environment_info",
        lambda: {
            "providerName": "faster-whisper-local",
            "pythonVersion": "test",
            "platform": "test",
        },
    )

    def _mock_transcriber(_audio_bytes, _mime_type, language, request_model):
        return {
            "status": "ok",
            "transcript": f"{request_model} final",
            "rawTranscript": f"{request_model} raw",
            "finalTranscript": f"{request_model} final",
            "detectedLanguage": language,
            "sttNoSpeechProbability": 0.01,
            "noSpeechGuardApplied": False,
            "noSpeechGuardReason": "none",
            "audioRms": 0.1,
            "audioPeak": 0.2,
            "audioSpeechDetected": True,
            "audioSignalRatio": 0.8,
            "sttProviderResolved": "faster-whisper-local",
            "sttProviderLoadStatus": "loaded",
            "sttProviderFallbackReason": "none",
            "modelLoadStatus": "loaded",
            "requestedModel": request_model,
            "resolvedModel": request_model,
            "modelSource": "request",
            "modelFallbackReason": "none",
        }

    report = module.build_report(
        samples,
        ["tiny", "base"],
        "zh",
        generated_at=datetime(2026, 6, 12, tzinfo=timezone.utc),
        transcriber=_mock_transcriber,
    )

    assert report["task"] == "TASK-STT-006A"
    assert report["language"] == "zh"
    assert report["modelsEvaluated"] == ["tiny", "base"]
    assert "recommendation" not in report["summary"]
    assert "recommendedModel" not in report["summary"]["byModel"]["tiny"]
    sample = report["samples"][0]
    assert sample["samplePath"] == "sample.wav"
    assert sample["pathRedacted"] is True
    assert sample["durationMs"] == 100
    assert sample["fileSizeBytes"] > 0
    assert sample["results"][0]["status"] == "success"
    assert sample["results"][0]["transcriptRaw"] == "tiny raw"
    assert sample["results"][0]["transcriptFinal"] == "tiny final"
    assert sample["results"][0]["score"] is None


def test_task_stt_006a_failed_model_does_not_abort_report(tmp_path, monkeypatch):
    module = _load_module()
    audio = tmp_path / "sample.wav"
    _write_wav(audio)
    samples = module.build_samples([str(audio)])
    monkeypatch.setattr(module, "environment_info", lambda: {})

    def _mock_transcriber(_audio_bytes, _mime_type, _language, request_model):
        if request_model == "base":
            raise RuntimeError("simulated model load failure")
        return {
            "status": "ok",
            "transcript": "ok",
            "finalTranscript": "ok",
            "sttProviderFallbackReason": "none",
            "modelFallbackReason": "none",
            "requestedModel": request_model,
            "resolvedModel": request_model,
            "modelSource": "request",
        }

    report = module.build_report(
        samples,
        ["tiny", "base", "small"],
        "zh",
        transcriber=_mock_transcriber,
    )
    results = {result["model"]: result for result in report["samples"][0]["results"]}

    assert results["tiny"]["status"] == "success"
    assert results["base"]["status"] == "error"
    assert "simulated model load failure" in results["base"]["error"]
    assert results["small"]["status"] == "success"
    assert report["summary"]["byModel"]["base"]["errorCount"] == 1


def test_task_stt_006a_write_report_creates_dated_output_path(tmp_path):
    module = _load_module()
    generated_at = datetime(2026, 6, 12, 9, 8, 7, tzinfo=timezone.utc)
    report = {
        "task": "TASK-STT-006A",
        "language": "zh",
        "modelsEvaluated": ["tiny"],
        "samples": [],
        "summary": {},
    }

    output_path = module.write_report(report, output_dir=tmp_path, generated_at=generated_at)

    assert output_path == tmp_path / "20260612" / "stt_model_evaluation_report_20260612_090807.json"
    assert output_path.is_file()
    assert "TASK-STT-006A" in output_path.read_text(encoding="utf-8")


def test_task_stt_006a_has_no_committed_audio_dependency():
    source = SCRIPT_PATH.read_text(encoding="utf-8")

    assert ".local-stt-samples" not in source
    assert "stt_model_evaluation" in source
    assert "--audio" in source
