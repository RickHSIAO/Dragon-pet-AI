import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "stt_model_recommendation_explanation.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("stt_model_recommendation_explanation", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _minimal_scoring_report(confidence="medium", recommended_model="base", margin=5.52):
    return {
        "schemaVersion": "1.0",
        "task": "TASK-STT-006B",
        "generatedAt": "2026-06-12T18:48:23+08:00",
        "inputReportBasename": "stt_model_evaluation_report.json",
        "inputReportPathRedacted": True,
        "profile": "balanced",
        "models": ["tiny", "base", "small"],
        "sampleCount": 2,
        "modelAggregates": {
            "tiny": {"successCount": 2, "errorCount": 0, "noSpeechCount": 0},
            "base": {"successCount": 2, "errorCount": 0, "noSpeechCount": 0},
            "small": {"successCount": 2, "errorCount": 0, "noSpeechCount": 0},
        },
        "modelScores": {
            "tiny": {
                "overallScore": 86.72,
                "reliabilityScore": 100.0,
                "speedScore": 73.4,
                "transcriptSignalScore": 97.0,
                "hallucinationRiskScore": 98.0,
            },
            "base": {
                "overallScore": 92.24,
                "reliabilityScore": 100.0,
                "speedScore": 100.0,
                "transcriptSignalScore": 97.0,
                "hallucinationRiskScore": 98.0,
            },
            "small": {
                "overallScore": 79.03,
                "reliabilityScore": 100.0,
                "speedScore": 37.1,
                "transcriptSignalScore": 97.0,
                "hallucinationRiskScore": 98.0,
            },
        },
        "deterministicRecommendation": {
            "recommendedModel": recommended_model,
            "confidence": confidence,
            "marginToRunnerUp": margin,
            "reasonCodes": ["top_overall_score", "profile_balanced", "no_reference_transcripts"],
            "decisionLimits": [
                "No reference transcript was provided; this is runtime-suitability scoring, not true accuracy or WER.",
                "This recommendation does not change the committed STT default.",
                "This recommendation does not auto-switch the runtime STT model.",
            ],
        },
        "caveats": [
            "no_reference_transcripts_runtime_suitability_only",
            "does_not_change_default_model",
            "does_not_auto_switch_runtime_model",
        ],
    }


def _encoded_explanation(report):
    return json.dumps(report["explanation"], ensure_ascii=False)


def test_task_stt_006c_reads_minimal_scoring_report_and_writes_explanation_json(tmp_path):
    module = _load_module()
    input_path = tmp_path / "scoring.json"
    input_path.write_text(json.dumps(_minimal_scoring_report()), encoding="utf-8")
    source = module.load_report(input_path)

    report = module.build_explanation_report(
        source,
        input_path=input_path,
        style="christina",
        generated_at=datetime(2026, 6, 12, 10, 0, 0, tzinfo=timezone.utc),
    )
    output_path = module.write_report(
        report,
        output_dir=tmp_path / "explanation",
        generated_at=datetime(2026, 6, 12, 10, 0, 0, tzinfo=timezone.utc),
    )

    assert report["schemaVersion"] == "1.0"
    assert report["task"] == "TASK-STT-006C"
    assert report["inputReportBasename"] == "scoring.json"
    assert report["sourceRecommendation"]["recommendedModel"] == "base"
    assert output_path == tmp_path / "explanation" / "20260612" / "stt_model_explanation_report_20260612_100000.json"
    assert output_path.is_file()


def test_task_stt_006c_christina_style_includes_caveats_and_no_auto_switch_claim():
    module = _load_module()
    report = module.build_explanation_report(
        _minimal_scoring_report(),
        input_path=Path("scoring.json"),
        style="christina",
    )
    encoded = _encoded_explanation(report)

    assert "Hmph" in report["explanation"]["shortRecommendation"]
    assert "runtime-suitability" in encoded
    assert "does not auto-switch" in encoded
    assert report["runtimeAutoSwitch"]["changed"] is False
    assert report["defaultChange"] == {"changed": False, "currentDefault": "tiny"}


def test_task_stt_006c_plain_style_works():
    module = _load_module()
    report = module.build_explanation_report(
        _minimal_scoring_report(),
        input_path=Path("scoring.json"),
        style="plain",
    )

    assert report["style"] == "plain"
    assert report["explanation"]["shortRecommendation"].startswith("The scoring report recommends reviewing base")
    assert report["grounding"]["llmUsed"] is False


def test_task_stt_006c_low_confidence_says_tentative_more_samples_needed():
    module = _load_module()
    source = _minimal_scoring_report(confidence="low", margin=2.19)

    report = module.build_explanation_report(source, input_path=Path("scoring.json"), style="plain")
    encoded = _encoded_explanation(report).lower()

    assert "weak recommendation" in encoded
    assert "more samples" in encoded
    assert "default remains tiny" in encoded


def test_task_stt_006c_missing_recommendation_does_not_invent_model_choice():
    module = _load_module()
    source = _minimal_scoring_report(recommended_model=None, confidence="low", margin=None)
    source["deterministicRecommendation"]["reasonCodes"] = ["no_scored_models"]

    report = module.build_explanation_report(source, input_path=Path("scoring.json"), style="christina")
    encoded = _encoded_explanation(report).lower()

    assert report["sourceRecommendation"]["recommendedModel"] is None
    assert "not strong enough" in encoded or "does not provide" in encoded
    assert "recommends reviewing base" not in encoded


def test_task_stt_006c_no_accuracy_score_or_wer_claims_in_explanation():
    module = _load_module()
    report = module.build_explanation_report(_minimal_scoring_report(), input_path=Path("scoring.json"))
    encoded = _encoded_explanation(report)

    assert "accuracyScore" not in encoded
    assert "WER" not in encoded
    assert "lowest WER" not in encoded
    assert "more accurate" not in encoded.lower()


def test_task_stt_006c_forbidden_phrase_validation_triggers_fallback():
    module = _load_module()
    source = _minimal_scoring_report()
    summary = module.build_model_score_summary(source)
    source_rec = module._source_recommendation(source)
    bad_explanation = {
        "shortRecommendation": "base is more accurate and should be used.",
        "detailedExplanation": "The runtime model switched.",
        "caveats": [],
        "nextActionSuggestion": "Change it now.",
    }

    fallback, removed = module.validate_or_fallback(
        bad_explanation,
        source_rec,
        summary,
        profile="balanced",
        style="plain",
        sample_count=2,
    )

    assert removed
    assert "base is more accurate" not in json.dumps(fallback).lower()
    assert "runtime model switched" not in json.dumps(fallback).lower()


def test_task_stt_006c_no_real_llm_required_even_when_requested():
    module = _load_module()

    report = module.build_explanation_report(
        _minimal_scoring_report(),
        input_path=Path("scoring.json"),
        use_llm=True,
    )

    assert report["grounding"]["llmUsed"] is False
    assert "llm_requested_but_deterministic_fallback_used" in report["grounding"]["unsupportedClaimsRemoved"]


def test_task_stt_006c_generated_output_path_creation_works(tmp_path):
    module = _load_module()
    report = module.build_explanation_report(
        _minimal_scoring_report(),
        input_path=Path("scoring.json"),
        generated_at=datetime(2026, 6, 12, 10, 0, 0, tzinfo=timezone.utc),
    )

    output_path = module.write_report(
        report,
        output_dir=tmp_path / "nested" / "out",
        generated_at=datetime(2026, 6, 12, 10, 0, 0, tzinfo=timezone.utc),
    )

    assert output_path.parent.is_dir()
    assert output_path.read_text(encoding="utf-8").startswith("{")


def test_task_stt_006c_has_no_audio_or_generated_report_dependency():
    source = SCRIPT_PATH.read_text(encoding="utf-8")

    assert ".local-stt-samples" not in source
    assert "getUserMedia" not in source
    assert "soundfile" not in source
    assert "--input" in source
    assert "outputs" in source
