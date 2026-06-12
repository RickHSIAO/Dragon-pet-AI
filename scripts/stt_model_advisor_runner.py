"""
TASK-STT-007 STT model advisor runner.

Runs the existing TASK-STT-006A evaluation, TASK-STT-006B deterministic
scoring, and TASK-STT-006C grounded explanation stages in one command. This
runner writes a final advisor manifest only; it does not change runtime model
selection, the committed default, or any frontend behavior.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import stt_model_evaluation_report as evaluation  # noqa: E402
import stt_model_recommendation_explanation as explanation  # noqa: E402
import stt_model_scoring_report as scoring  # noqa: E402


SCHEMA_VERSION = "1.0"
TASK_ID = "TASK-STT-007"
DEFAULT_LANGUAGE = "zh"
DEFAULT_PROFILE = "balanced"
DEFAULT_STYLE = "christina"
PROFILE_ORDER = ("balanced", "manual_mic", "conversation")
STYLE_ORDER = ("christina", "plain")


class AdvisorStageError(RuntimeError):
    def __init__(self, stage: str, message: str) -> None:
        self.stage = stage
        super().__init__(f"{stage} stage failed: {message}")


@dataclass(frozen=True)
class StageResult:
    report: dict[str, Any]
    path: Path


@dataclass(frozen=True)
class AdvisorResult:
    evaluation: StageResult
    scoring: StageResult
    explanation: StageResult
    manifest: dict[str, Any]
    manifest_path: Path


StageCallable = Callable[[], StageResult]


def _stage_output_dir(output_root: Path | None, stage_name: str) -> Path | None:
    if output_root is None:
        return None
    return output_root / stage_name


def _run_stage(stage_name: str, stage_fn: StageCallable) -> StageResult:
    try:
        result = stage_fn()
    except AdvisorStageError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise AdvisorStageError(stage_name, str(exc)) from exc
    if not isinstance(result.report, dict):
        raise AdvisorStageError(stage_name, "stage returned a non-object report")
    if not result.path.is_file():
        raise AdvisorStageError(stage_name, f"stage did not write report: {result.path}")
    return result


def _build_evaluation_stage(
    audio_paths: list[str],
    models: list[str],
    language: str,
    output_root: Path | None,
    generated_at: datetime,
) -> StageCallable:
    def _stage() -> StageResult:
        samples = evaluation.build_samples(audio_paths)
        report = evaluation.build_report(
            samples,
            models,
            language,
            generated_at=generated_at,
        )
        output_path = evaluation.write_report(
            report,
            output_dir=_stage_output_dir(output_root, "stt_model_evaluation"),
            generated_at=generated_at,
        )
        return StageResult(report=report, path=output_path)

    return _stage


def _build_scoring_stage(
    evaluation_result: StageResult,
    profile: str,
    output_root: Path | None,
    generated_at: datetime,
) -> StageCallable:
    def _stage() -> StageResult:
        report = scoring.build_scoring_report(
            evaluation_result.report,
            input_path=evaluation_result.path,
            profile=profile,
            generated_at=generated_at,
        )
        output_path = scoring.write_report(
            report,
            output_dir=_stage_output_dir(output_root, "stt_model_scoring"),
            generated_at=generated_at,
        )
        return StageResult(report=report, path=output_path)

    return _stage


def _build_explanation_stage(
    scoring_result: StageResult,
    profile: str,
    style: str,
    output_root: Path | None,
    generated_at: datetime,
    use_llm: bool,
) -> StageCallable:
    def _stage() -> StageResult:
        report = explanation.build_explanation_report(
            scoring_result.report,
            input_path=scoring_result.path,
            profile=profile,
            style=style,
            generated_at=generated_at,
            use_llm=use_llm,
        )
        output_path = explanation.write_report(
            report,
            output_dir=_stage_output_dir(output_root, "stt_model_explanation"),
            generated_at=generated_at,
        )
        return StageResult(report=report, path=output_path)

    return _stage


def build_advisor_manifest(
    evaluation_result: StageResult,
    scoring_result: StageResult,
    explanation_result: StageResult,
    language: str,
    profile: str,
    style: str,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or datetime.now().astimezone()
    scoring_report = scoring_result.report
    explanation_report = explanation_result.report
    recommendation = scoring_report.get("deterministicRecommendation") or {}
    explanation_body = explanation_report.get("explanation") or {}
    grounding = explanation_report.get("grounding") or {}
    models = list(scoring_report.get("models") or evaluation_result.report.get("modelsEvaluated") or [])
    sample_count = int(scoring_report.get("sampleCount") or len(evaluation_result.report.get("samples", [])))

    return {
        "schemaVersion": SCHEMA_VERSION,
        "task": TASK_ID,
        "generatedAt": generated_at.isoformat(timespec="seconds"),
        "language": language,
        "profile": profile,
        "style": style,
        "models": models,
        "sampleCount": sample_count,
        "stageReports": {
            "evaluationReportBasename": evaluation_result.path.name,
            "scoringReportBasename": scoring_result.path.name,
            "explanationReportBasename": explanation_result.path.name,
            "evaluationReportPathLocalArtifact": str(evaluation_result.path),
            "scoringReportPathLocalArtifact": str(scoring_result.path),
            "explanationReportPathLocalArtifact": str(explanation_result.path),
            "pathsAreLocalArtifacts": True,
        },
        "deterministicRecommendation": {
            "recommendedModel": recommendation.get("recommendedModel"),
            "confidence": recommendation.get("confidence"),
            "marginToRunnerUp": recommendation.get("marginToRunnerUp"),
            "reasonCodes": list(recommendation.get("reasonCodes") or []),
        },
        "explanation": {
            "shortRecommendation": explanation_body.get("shortRecommendation"),
            "detailedExplanation": explanation_body.get("detailedExplanation"),
            "caveats": list(explanation_body.get("caveats") or []),
            "nextActionSuggestion": explanation_body.get("nextActionSuggestion"),
        },
        "safety": {
            "defaultChanged": False,
            "runtimeAutoSwitchChanged": False,
            "llmUsed": bool(grounding.get("llmUsed", False)),
            "noReferenceTranscriptCaveat": True,
        },
        "caveats": [
            "runtime-suitability only",
            "no reference transcript / no WER",
            "no default change",
            "no auto-switch",
            "generated reports are runtime artifacts",
        ],
    }


def write_manifest(
    manifest: dict[str, Any],
    output_root: Path | None = None,
    generated_at: datetime | None = None,
) -> Path:
    generated_at = generated_at or datetime.now().astimezone()
    day = generated_at.strftime("%Y%m%d")
    stamp = generated_at.strftime("%Y%m%d_%H%M%S")
    base_dir = (output_root / "stt_model_advisor") if output_root else (REPO_ROOT / "outputs" / "stt_model_advisor")
    target_dir = base_dir / day
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"stt_model_advisor_manifest_{stamp}.json"
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + os.linesep, encoding="utf-8")
    return output_path


def run_advisor(
    audio_paths: list[str],
    models: list[str],
    language: str = DEFAULT_LANGUAGE,
    profile: str = DEFAULT_PROFILE,
    style: str = DEFAULT_STYLE,
    output_root: Path | None = None,
    generated_at: datetime | None = None,
    use_llm: bool = False,
) -> AdvisorResult:
    generated_at = generated_at or datetime.now().astimezone()
    if not audio_paths:
        raise ValueError("Provide at least one --audio file.")
    if profile not in PROFILE_ORDER:
        raise ValueError(f"Unsupported profile {profile!r}.")
    if style not in STYLE_ORDER:
        raise ValueError(f"Unsupported style {style!r}.")

    evaluation_result = _run_stage(
        "evaluation",
        _build_evaluation_stage(audio_paths, models, language, output_root, generated_at),
    )
    scoring_result = _run_stage(
        "scoring",
        _build_scoring_stage(evaluation_result, profile, output_root, generated_at),
    )
    explanation_result = _run_stage(
        "explanation",
        _build_explanation_stage(scoring_result, profile, style, output_root, generated_at, use_llm),
    )
    manifest = build_advisor_manifest(
        evaluation_result,
        scoring_result,
        explanation_result,
        language=language,
        profile=profile,
        style=style,
        generated_at=generated_at,
    )
    manifest_path = write_manifest(manifest, output_root=output_root, generated_at=generated_at)
    return AdvisorResult(
        evaluation=evaluation_result,
        scoring=scoring_result,
        explanation=explanation_result,
        manifest=manifest,
        manifest_path=manifest_path,
    )


def print_summary(result: AdvisorResult) -> None:
    rec = result.manifest["deterministicRecommendation"]
    safety = result.manifest["safety"]
    print("TASK-STT-007 STT model advisor runner")
    print(f"  manifest: {result.manifest_path}")
    print(f"  evaluation: {result.evaluation.path.name}")
    print(f"  scoring: {result.scoring.path.name}")
    print(f"  explanation: {result.explanation.path.name}")
    print(f"  language: {result.manifest['language']}")
    print(f"  profile: {result.manifest['profile']}")
    print(f"  style: {result.manifest['style']}")
    print(f"  models: {', '.join(result.manifest['models'])}")
    print(f"  samples: {result.manifest['sampleCount']}")
    print(f"  recommendedModel: {rec.get('recommendedModel')}")
    print(f"  confidence: {rec.get('confidence')}")
    print(f"  marginToRunnerUp: {rec.get('marginToRunnerUp')}")
    print(f"  llmUsed: {safety.get('llmUsed')}")
    print("  note: advisor only; no default change and no runtime auto-switch")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run STT model evaluation, deterministic scoring, and grounded explanation in one command.",
    )
    parser.add_argument("--audio", action="append", required=True, help="Audio sample path. Repeat for multiple files.")
    parser.add_argument(
        "--models",
        default=",".join(evaluation.DEFAULT_MODELS),
        help="Comma-separated models to evaluate. Default: tiny,base,small.",
    )
    parser.add_argument("--language", default=DEFAULT_LANGUAGE, help="Language hint passed to STT. Default: zh.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, choices=PROFILE_ORDER, help="Scoring profile.")
    parser.add_argument("--style", default=DEFAULT_STYLE, choices=STYLE_ORDER, help="Explanation style.")
    parser.add_argument("--output-root", help="Output root. Default: repo outputs/ stage directories.")
    parser.add_argument(
        "--keep-intermediate",
        action="store_true",
        default=True,
        help="Keep 006A/006B/006C reports. Default: true.",
    )
    parser.add_argument("--pretty", action="store_true", help="Print the final advisor manifest JSON after summary.")
    llm_group = parser.add_mutually_exclusive_group()
    llm_group.add_argument("--no-llm", action="store_true", help="Use deterministic templates only. This is the default.")
    llm_group.add_argument(
        "--use-llm",
        action="store_true",
        help="Accepted for future compatibility; current explanation remains deterministic/no-LLM.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        models = evaluation.parse_models(args.models)
        result = run_advisor(
            audio_paths=args.audio,
            models=models,
            language=args.language,
            profile=args.profile,
            style=args.style,
            output_root=Path(args.output_root) if args.output_root else None,
            use_llm=bool(args.use_llm),
        )
        print_summary(result)
        if args.pretty:
            print(json.dumps(result.manifest, ensure_ascii=False, indent=2))
        return 0
    except AdvisorStageError as exc:
        parser.exit(2, f"error: {exc}\n")
        return 2
    except Exception as exc:  # noqa: BLE001
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
