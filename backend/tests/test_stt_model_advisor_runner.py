import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "stt_model_advisor_runner.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("stt_model_advisor_runner", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_stage_result(module, tmp_path, name, report):
    path = tmp_path / f"{name}.json"
    path.write_text("{}", encoding="utf-8")
    return module.StageResult(report=report, path=path)


def _evaluation_report():
    return {
        "task": "TASK-STT-006A",
        "language": "zh",
        "modelsEvaluated": ["tiny", "base", "small"],
        "samples": [{"samplePath": "owner1.wav"}, {"samplePath": "owner2.wav"}],
    }


def _scoring_report():
    return {
        "schemaVersion": "1.0",
        "task": "TASK-STT-006B",
        "profile": "balanced",
        "models": ["tiny", "base", "small"],
        "sampleCount": 2,
        "deterministicRecommendation": {
            "recommendedModel": "base",
            "confidence": "medium",
            "marginToRunnerUp": 4.12,
            "reasonCodes": ["top_overall_score", "profile_balanced", "no_reference_transcripts"],
        },
    }


def _explanation_report():
    return {
        "schemaVersion": "1.0",
        "task": "TASK-STT-006C",
        "profile": "balanced",
        "style": "christina",
        "explanation": {
            "shortRecommendation": "建議先檢視 base。",
            "detailedExplanation": "base 是 grounded runtime suitability scoring 的最高分候選。",
            "caveats": ["no reference transcript", "default remains tiny"],
            "nextActionSuggestion": "Keep the default unchanged and collect more samples.",
        },
        "grounding": {"llmUsed": False},
        "defaultChange": {"changed": False, "currentDefault": "tiny"},
        "runtimeAutoSwitch": {"changed": False},
    }


def test_task_stt_007_parser_builds_and_validates_audio_args():
    module = _load_module()
    parser = module.build_parser()

    args = parser.parse_args(
        [
            "--audio",
            "owner1.wav",
            "--audio",
            "owner2.wav",
            "--models",
            "tiny,base,small",
            "--language",
            "zh",
            "--profile",
            "balanced",
            "--style",
            "christina",
        ]
    )

    assert args.audio == ["owner1.wav", "owner2.wav"]
    assert args.models == "tiny,base,small"
    assert args.language == "zh"
    assert args.profile == "balanced"
    assert args.style == "christina"

    with pytest.raises(SystemExit):
        parser.parse_args(["--models", "tiny"])


def test_task_stt_007_calls_006a_006b_006c_in_order_and_writes_manifest(tmp_path, monkeypatch):
    module = _load_module()
    calls = []

    def _eval_builder(audio_paths, models, language, output_root, generated_at):
        assert audio_paths == ["owner1.wav", "owner2.wav"]
        assert models == ["tiny", "base", "small"]
        assert language == "zh"
        assert output_root == tmp_path / "out"
        assert generated_at == datetime(2026, 6, 12, 10, 0, 0, tzinfo=timezone.utc)

        def _stage():
            calls.append("evaluation")
            return _write_stage_result(module, tmp_path, "evaluation", _evaluation_report())

        return _stage

    def _scoring_builder(evaluation_result, profile, output_root, generated_at):
        assert evaluation_result.report["task"] == "TASK-STT-006A"
        assert profile == "balanced"

        def _stage():
            calls.append("scoring")
            return _write_stage_result(module, tmp_path, "scoring", _scoring_report())

        return _stage

    def _explanation_builder(scoring_result, profile, style, output_root, generated_at, use_llm):
        assert scoring_result.report["task"] == "TASK-STT-006B"
        assert profile == "balanced"
        assert style == "christina"
        assert use_llm is False

        def _stage():
            calls.append("explanation")
            return _write_stage_result(module, tmp_path, "explanation", _explanation_report())

        return _stage

    monkeypatch.setattr(module, "_build_evaluation_stage", _eval_builder)
    monkeypatch.setattr(module, "_build_scoring_stage", _scoring_builder)
    monkeypatch.setattr(module, "_build_explanation_stage", _explanation_builder)

    result = module.run_advisor(
        audio_paths=["owner1.wav", "owner2.wav"],
        models=["tiny", "base", "small"],
        language="zh",
        profile="balanced",
        style="christina",
        output_root=tmp_path / "out",
        generated_at=datetime(2026, 6, 12, 10, 0, 0, tzinfo=timezone.utc),
    )

    assert calls == ["evaluation", "scoring", "explanation"]
    assert result.manifest_path == tmp_path / "out" / "stt_model_advisor" / "20260612" / "stt_model_advisor_manifest_20260612_100000.json"
    assert result.manifest_path.is_file()


def test_task_stt_007_manifest_includes_stage_basenames_and_safety_flags(tmp_path):
    module = _load_module()
    generated_at = datetime(2026, 6, 12, 10, 0, 0, tzinfo=timezone.utc)
    eval_result = _write_stage_result(module, tmp_path, "evaluation", _evaluation_report())
    scoring_result = _write_stage_result(module, tmp_path, "scoring", _scoring_report())
    explanation_result = _write_stage_result(module, tmp_path, "explanation", _explanation_report())

    manifest = module.build_advisor_manifest(
        eval_result,
        scoring_result,
        explanation_result,
        language="zh",
        profile="balanced",
        style="christina",
        generated_at=generated_at,
    )

    assert manifest["schemaVersion"] == "1.0"
    assert manifest["task"] == "TASK-STT-007"
    assert manifest["stageReports"]["evaluationReportBasename"] == "evaluation.json"
    assert manifest["stageReports"]["scoringReportBasename"] == "scoring.json"
    assert manifest["stageReports"]["explanationReportBasename"] == "explanation.json"
    assert manifest["stageReports"]["pathsAreLocalArtifacts"] is True
    assert manifest["deterministicRecommendation"]["recommendedModel"] == "base"
    assert manifest["deterministicRecommendation"]["marginToRunnerUp"] == 4.12
    assert manifest["explanation"]["shortRecommendation"] == "建議先檢視 base。"
    assert manifest["safety"] == {
        "defaultChanged": False,
        "runtimeAutoSwitchChanged": False,
        "llmUsed": False,
        "noReferenceTranscriptCaveat": True,
    }
    assert "no reference transcript / no WER" in manifest["caveats"]


def test_task_stt_007_no_llm_used_by_default(tmp_path, monkeypatch):
    module = _load_module()
    seen = {}

    monkeypatch.setattr(
        module,
        "_build_evaluation_stage",
        lambda *_args: lambda: _write_stage_result(module, tmp_path, "evaluation", _evaluation_report()),
    )
    monkeypatch.setattr(
        module,
        "_build_scoring_stage",
        lambda *_args: lambda: _write_stage_result(module, tmp_path, "scoring", _scoring_report()),
    )

    def _explanation_builder(_scoring_result, _profile, _style, _output_root, _generated_at, use_llm):
        seen["use_llm"] = use_llm
        return lambda: _write_stage_result(module, tmp_path, "explanation", _explanation_report())

    monkeypatch.setattr(module, "_build_explanation_stage", _explanation_builder)

    result = module.run_advisor(audio_paths=["owner.wav"], models=["tiny"], output_root=tmp_path)

    assert seen["use_llm"] is False
    assert result.manifest["safety"]["llmUsed"] is False


def test_task_stt_007_stage_failure_reports_correct_stage(tmp_path, monkeypatch):
    module = _load_module()

    def _eval_builder(*_args):
        def _stage():
            raise RuntimeError("simulated failure")

        return _stage

    monkeypatch.setattr(module, "_build_evaluation_stage", _eval_builder)

    with pytest.raises(module.AdvisorStageError, match="evaluation stage failed: simulated failure") as exc:
        module.run_advisor(audio_paths=["owner.wav"], models=["tiny"], output_root=tmp_path)

    assert exc.value.stage == "evaluation"


def test_task_stt_007_write_manifest_creates_output_path(tmp_path):
    module = _load_module()
    generated_at = datetime(2026, 6, 12, 10, 0, 0, tzinfo=timezone.utc)
    manifest = {
        "schemaVersion": "1.0",
        "task": "TASK-STT-007",
    }

    output_path = module.write_manifest(manifest, output_root=tmp_path, generated_at=generated_at)

    assert output_path == tmp_path / "stt_model_advisor" / "20260612" / "stt_model_advisor_manifest_20260612_100000.json"
    assert output_path.is_file()
    assert "TASK-STT-007" in output_path.read_text(encoding="utf-8")


def test_task_stt_007_has_no_audio_or_generated_report_dependency():
    source = SCRIPT_PATH.read_text(encoding="utf-8")

    assert ".local-stt-samples" not in source
    assert "getUserMedia" not in source
    assert "soundfile" not in source
    assert "runtimeAutoSwitchChanged" in source
    assert "defaultChanged" in source
