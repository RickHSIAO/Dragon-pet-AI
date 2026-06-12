import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "stt_model_scoring_report.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("stt_model_scoring_report", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _result(
    model,
    status="success",
    latency=1000,
    rtf=0.5,
    length=12,
    no_speech_prob=0.05,
    rms=0.02,
    peak=0.12,
    voiced=0.2,
    speech=True,
    fallback="none",
    provider_status="loaded",
):
    return {
        "model": model,
        "status": status,
        "runtimeStatus": "ok" if status == "success" else status,
        "latencyMs": latency,
        "rtf": rtf,
        "transcriptRaw": f"{model} raw",
        "transcriptFinal": f"{model} final",
        "transcriptLength": length,
        "detectedLanguage": "zh",
        "noSpeechProbability": no_speech_prob,
        "noSpeechGuardApplied": False,
        "noSpeechGuardReason": "none",
        "audioRms": rms,
        "audioPeak": peak,
        "speechDetected": speech,
        "voicedRatio": voiced,
        "provider": "faster-whisper-local",
        "providerLoadStatus": provider_status,
        "modelLoadStatus": provider_status,
        "requestedModel": model,
        "resolvedModel": model,
        "modelSource": "request",
        "fallback": fallback,
        "error": None,
        "score": None,
    }


def _minimal_report():
    return {
        "task": "TASK-STT-006A",
        "generatedAt": "2026-06-12T17:44:17+08:00",
        "language": "zh",
        "modelsEvaluated": ["tiny", "base", "small"],
        "samples": [
            {
                "samplePath": "owner1.wav",
                "durationMs": 2000,
                "fileSizeBytes": 1000,
                "results": [
                    _result("tiny", latency=2600, rtf=1.3, length=8),
                    _result("base", latency=1700, rtf=0.85, length=12),
                    _result("small", latency=4800, rtf=2.4, length=15),
                ],
            },
            {
                "samplePath": "owner2.wav",
                "durationMs": 2000,
                "fileSizeBytes": 1000,
                "results": [
                    _result("tiny", latency=2700, rtf=1.35, length=8),
                    _result("base", latency=1800, rtf=0.9, length=12),
                    _result("small", latency=4700, rtf=2.35, length=15),
                ],
            },
        ],
    }


def test_task_stt_006b_reads_minimal_report_and_writes_scoring_report(tmp_path):
    module = _load_module()
    input_path = tmp_path / "evaluation.json"
    input_path.write_text(json.dumps(_minimal_report()), encoding="utf-8")
    source = module.load_report(input_path)

    report = module.build_scoring_report(
        source,
        input_path=input_path,
        profile="balanced",
        generated_at=datetime(2026, 6, 12, 10, 0, 0, tzinfo=timezone.utc),
    )
    output_path = module.write_report(
        report,
        output_dir=tmp_path / "scoring",
        generated_at=datetime(2026, 6, 12, 10, 0, 0, tzinfo=timezone.utc),
    )

    assert report["schemaVersion"] == "1.0"
    assert report["task"] == "TASK-STT-006B"
    assert report["inputReportBasename"] == "evaluation.json"
    assert report["inputReportPathRedacted"] is True
    assert output_path == tmp_path / "scoring" / "20260612" / "stt_model_scoring_report_20260612_100000.json"
    assert output_path.is_file()


def test_task_stt_006b_computes_aggregates_for_tiny_base_small():
    module = _load_module()
    aggregates = module.compute_model_aggregates(_minimal_report())

    assert set(aggregates) == {"tiny", "base", "small"}
    assert aggregates["tiny"]["successCount"] == 2
    assert aggregates["base"]["sampleCount"] == 2
    assert aggregates["small"]["errorRate"] == 0
    assert aggregates["base"]["avgLatencyMs"] == 1750
    assert aggregates["small"]["avgTranscriptLength"] == 15


def test_task_stt_006b_no_reference_transcript_means_no_accuracy_score():
    module = _load_module()
    report = module.build_scoring_report(_minimal_report(), input_path=Path("evaluation.json"))
    encoded = json.dumps(report)

    assert "accuracyScore" not in encoded
    assert "runtime-suitability" in report["deterministicRecommendation"]["decisionLimits"][0]


def test_task_stt_006b_recommendation_exists_when_data_sufficient():
    module = _load_module()
    report = module.build_scoring_report(_minimal_report(), input_path=Path("evaluation.json"))
    rec = report["deterministicRecommendation"]

    assert rec["recommendedModel"] in {"tiny", "base", "small"}
    assert rec["confidence"] in {"low", "medium", "high"}
    assert "no_reference_transcripts" in rec["reasonCodes"]
    assert rec["decisionLimits"]


def test_task_stt_006b_confidence_low_when_scores_are_close():
    module = _load_module()
    report = _minimal_report()
    for sample in report["samples"]:
        sample["results"] = [
            _result("tiny", latency=1000, rtf=0.5, length=10),
            _result("base", latency=1005, rtf=0.5025, length=10),
        ]
    report["modelsEvaluated"] = ["tiny", "base"]

    scored = module.build_scoring_report(report, input_path=Path("evaluation.json"))

    assert scored["deterministicRecommendation"]["confidence"] == "low"
    assert scored["deterministicRecommendation"]["marginToRunnerUp"] < 3


def test_task_stt_006b_one_model_error_does_not_crash_scoring():
    module = _load_module()
    report = _minimal_report()
    report["samples"][0]["results"][1] = _result("base", status="error", latency=50, length=0, speech=True)
    report["samples"][0]["results"][1]["error"] = "simulated failure"

    scored = module.build_scoring_report(report, input_path=Path("evaluation.json"))

    assert scored["modelAggregates"]["base"]["errorCount"] == 1
    assert scored["modelScores"]["base"]["overallScore"] is not None
    assert "base_has_error_results" in scored["caveats"]


def test_task_stt_006b_missing_optional_metrics_do_not_crash_scoring():
    module = _load_module()
    report = {
        "generatedAt": "2026-06-12T00:00:00+00:00",
        "modelsEvaluated": ["tiny"],
        "samples": [{"samplePath": "x.wav", "results": [{"model": "tiny", "status": "success"}]}],
    }

    scored = module.build_scoring_report(report, input_path=Path("evaluation.json"))

    assert scored["modelAggregates"]["tiny"]["successCount"] == 1
    assert scored["modelScores"]["tiny"]["overallScore"] is not None
    assert "tiny_missing_optional_metrics" in scored["caveats"]


def test_task_stt_006b_conversation_profile_penalizes_slow_model_more():
    module = _load_module()
    report = _minimal_report()

    manual = module.build_scoring_report(report, input_path=Path("evaluation.json"), profile="manual_mic")
    conversation = module.build_scoring_report(report, input_path=Path("evaluation.json"), profile="conversation")

    assert conversation["modelScores"]["small"]["speedScore"] < manual["modelScores"]["small"]["speedScore"]
    manual_gap = manual["modelScores"]["base"]["overallScore"] - manual["modelScores"]["small"]["overallScore"]
    conversation_gap = conversation["modelScores"]["base"]["overallScore"] - conversation["modelScores"]["small"]["overallScore"]
    assert conversation_gap > manual_gap


def test_task_stt_006b_has_no_audio_or_generated_report_dependency():
    source = SCRIPT_PATH.read_text(encoding="utf-8")

    assert ".local-stt-samples" not in source
    assert "--input" in source
    assert "outputs" in source
    assert "getUserMedia" not in source
