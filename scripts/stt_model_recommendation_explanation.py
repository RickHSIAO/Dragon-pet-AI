"""
TASK-STT-006C grounded STT recommendation explanation.

Reads a TASK-STT-006B deterministic scoring report and writes a user-facing
explanation report. This script is deterministic by default: it does not call an
LLM, change the committed STT default, or auto-switch the runtime STT model.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
import os
from pathlib import Path
import re
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = "1.0"
TASK_ID = "TASK-STT-006C"
DEFAULT_MODEL = "tiny"
STYLE_ORDER = ("christina", "plain")
PROFILE_ORDER = ("manual_mic", "conversation", "balanced")
KNOWN_MODEL_NAMES = {"tiny", "base", "small"}

FORBIDDEN_CLAIMS = (
    "base is more accurate",
    "small is worse at transcription accuracy",
    "lowest wer",
    "wer",
    "accuracyscore",
    "default changed",
    "default switched",
    "runtime model switched",
    "auto-switched",
    "final permanent decision",
    "permanent decision",
)


def _round(value: Any, digits: int = 2) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return round(float(value), digits)
    return None


def _text(value: Any) -> str:
    return str(value) if value is not None else ""


def _score_text(value: Any) -> str:
    number = _round(value, 2)
    return f"{number:.2f}" if number is not None else "n/a"


def _clean_decision_limits(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    cleaned: list[str] = []
    for value in values:
        text = _text(value).replace("WER", "word-error-rate").replace("wer", "word-error-rate")
        if text:
            cleaned.append(text)
    return cleaned


def load_report(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Input scoring report must be a JSON object.")
    if data.get("task") and data.get("task") != "TASK-STT-006B":
        raise ValueError("Input report must be a TASK-STT-006B scoring report.")
    if not isinstance(data.get("modelScores"), dict):
        raise ValueError("Input report is missing modelScores.")
    if not isinstance(data.get("deterministicRecommendation"), dict):
        raise ValueError("Input report is missing deterministicRecommendation.")
    return data


def _models_from_report(report: dict[str, Any]) -> list[str]:
    models: list[str] = []
    raw_models = report.get("models")
    if isinstance(raw_models, list):
        for model in raw_models:
            name = _text(model).strip()
            if name and name not in models:
                models.append(name)
    for model in report.get("modelScores", {}):
        name = _text(model).strip()
        if name and name not in models:
            models.append(name)
    return models


def build_model_score_summary(report: dict[str, Any]) -> list[dict[str, Any]]:
    model_scores = report.get("modelScores", {})
    if not isinstance(model_scores, dict):
        return []
    summary: list[dict[str, Any]] = []
    for model in _models_from_report(report):
        score = model_scores.get(model, {})
        if not isinstance(score, dict):
            score = {}
        summary.append(
            {
                "model": model,
                "overallScore": _round(score.get("overallScore")),
                "reliabilityScore": _round(score.get("reliabilityScore")),
                "speedScore": _round(score.get("speedScore")),
                "transcriptSignalScore": _round(score.get("transcriptSignalScore")),
                "hallucinationRiskScore": _round(score.get("hallucinationRiskScore")),
            }
        )
    return summary


def _source_recommendation(report: dict[str, Any]) -> dict[str, Any]:
    rec = report.get("deterministicRecommendation", {})
    if not isinstance(rec, dict):
        rec = {}
    return {
        "recommendedModel": rec.get("recommendedModel"),
        "confidence": rec.get("confidence") or "low",
        "marginToRunnerUp": _round(rec.get("marginToRunnerUp")),
        "reasonCodes": list(rec.get("reasonCodes") or []),
        "decisionLimits": _clean_decision_limits(rec.get("decisionLimits")),
    }


def _score_for_model(summary: list[dict[str, Any]], model: str | None) -> dict[str, Any] | None:
    if not model:
        return None
    for item in summary:
        if item.get("model") == model:
            return item
    return None


def _ranked_summary(summary: list[dict[str, Any]], language: str = "plain") -> str:
    ranked = sorted(
        (item for item in summary if isinstance(item.get("overallScore"), (int, float))),
        key=lambda item: item["overallScore"],
        reverse=True,
    )
    if not ranked:
        return "沒有可用的模型分數。" if language == "zh" else "No scored models are available."
    if language == "zh":
        return "，".join(f"{item['model']} overallScore {_score_text(item.get('overallScore'))}" for item in ranked)
    return ", ".join(f"{item['model']} overall {_score_text(item.get('overallScore'))}" for item in ranked)


def _common_caveats(sample_count: int) -> list[str]:
    return [
        "Runtime-suitability scoring only.",
        "No reference transcript was provided, so this is not transcript accuracy or word-error-rate evidence.",
        f"Local sample count is {sample_count}; add more samples before changing operational policy.",
        f"The committed STT default remains {DEFAULT_MODEL}.",
        "This script does not auto-switch the runtime STT model.",
    ]


def _christina_caveats(sample_count: int) -> list[str]:
    return [
        "這只是 runtime suitability scoring，不是真正的逐字稿準確率證明。",
        "沒有 reference transcript，所以不能當成真正 accuracy 或字詞錯誤率結論。",
        f"這次 local sample count 是 {sample_count}，樣本可能偏少，還需要更多語音再判斷。",
        f"committed STT default 仍然是 {DEFAULT_MODEL}。",
        "這個 script 不會自動切換 runtime STT model。",
    ]


def _plain_explanation(
    source_rec: dict[str, Any],
    summary: list[dict[str, Any]],
    profile: str,
    sample_count: int,
) -> dict[str, Any]:
    model = source_rec.get("recommendedModel")
    confidence = source_rec.get("confidence") or "low"
    margin = source_rec.get("marginToRunnerUp")
    caveats = _common_caveats(sample_count)
    if not model:
        return {
            "shortRecommendation": "No model recommendation was produced from this scoring report.",
            "detailedExplanation": (
                "The scoring report does not contain enough grounded scoring evidence to recommend a model. "
                "Collect more local samples and rerun evaluation and scoring before using this report for decisions."
            ),
            "caveats": caveats,
            "nextActionSuggestion": "Collect more representative local samples and rerun the 006A and 006B reports.",
        }

    score = _score_for_model(summary, _text(model)) or {}
    tentative = ""
    if confidence == "low":
        tentative = " This is a weak recommendation because confidence is low; use more samples before acting on it."
        caveats.append("Low confidence means the recommendation is tentative.")
    return {
        "shortRecommendation": (
            f"The scoring report recommends reviewing {model} for the {profile} profile "
            f"(overall score {_score_text(score.get('overallScore'))}, confidence {confidence})."
        ),
        "detailedExplanation": (
            f"For the {profile} profile, {model} is the top deterministic runtime-suitability candidate. "
            f"The margin to runner-up is {_score_text(margin)} and the scored model order is: "
            f"{_ranked_summary(summary)}.{tentative} This is a recommendation to review, not a command to change runtime behavior."
        ),
        "caveats": caveats,
        "nextActionSuggestion": (
            "Keep the default unchanged, test the candidate manually with more representative audio, "
            "then decide whether a future task should change any runtime policy."
        ),
    }


def _christina_explanation(
    source_rec: dict[str, Any],
    summary: list[dict[str, Any]],
    profile: str,
    sample_count: int,
) -> dict[str, Any]:
    return _christina_explanation_zh(source_rec, summary, profile, sample_count)


def _christina_explanation_zh(
    source_rec: dict[str, Any],
    summary: list[dict[str, Any]],
    profile: str,
    sample_count: int,
) -> dict[str, Any]:
    model = source_rec.get("recommendedModel")
    confidence = source_rec.get("confidence") or "low"
    margin = source_rec.get("marginToRunnerUp")
    caveats = _christina_caveats(sample_count)
    if not model:
        return {
            "shortRecommendation": "哼，這份 scoring report 還不足以讓吾給出模型建議。",
            "detailedExplanation": (
                "吾已經看過 scoring report，但裡面沒有足夠的 grounded recommendation。"
                "吾不會為了裝得很果斷就亂編模型選擇；先收集更多樣本，再讓證據說話。"
            ),
            "caveats": caveats,
            "nextActionSuggestion": "先收集更多本機語音樣本，再重新跑 evaluation、scoring 與 explanation。",
        }

    score = _score_for_model(summary, _text(model)) or {}
    tentative = ""
    if confidence == "low":
        tentative = (
            " confidence 是 low，所以就算是吾也只能把這當成暫定建議；"
            "還需要更多樣本，不能只靠這份結果改 default。"
        )
        caveats.append("confidence 是 low，代表這個建議偏弱，還需要更多樣本。")
    return {
        "shortRecommendation": (
            f"哼，吾看這份 scoring report，{profile} profile 目前建議先檢視 {model}；"
            f"overallScore {_score_text(score.get('overallScore'))}，confidence {confidence}。"
        ),
        "detailedExplanation": (
            f"吾判斷 {model} 是這份 grounded runtime suitability scoring 裡，"
            f"{profile} profile 的最高分候選。runner-up margin 是 {_score_text(margin)}；"
            f"模型分數順序是：{_ranked_summary(summary, language='zh')}。{tentative}"
            "這只是建議汝優先檢視候選模型，不是命令系統切換 runtime model。"
        ),
        "caveats": caveats,
        "nextActionSuggestion": (
            "先維持目前 default，不要急著改。等收集更多代表性語音、重新確認分數後，"
            "再由後續任務決定是否調整 runtime policy。"
        ),
    }


def build_explanation(
    source_rec: dict[str, Any],
    summary: list[dict[str, Any]],
    profile: str,
    style: str,
    sample_count: int,
) -> dict[str, Any]:
    if style == "plain":
        return _plain_explanation(source_rec, summary, profile, sample_count)
    return _christina_explanation_zh(source_rec, summary, profile, sample_count)


def _explanation_text(explanation: dict[str, Any]) -> str:
    values = [
        explanation.get("shortRecommendation"),
        explanation.get("detailedExplanation"),
        explanation.get("nextActionSuggestion"),
    ]
    caveats = explanation.get("caveats")
    if isinstance(caveats, list):
        values.extend(caveats)
    return "\n".join(_text(value) for value in values if value is not None)


def validate_grounding(
    explanation: dict[str, Any],
    source_rec: dict[str, Any],
    summary: list[dict[str, Any]],
) -> tuple[bool, list[str]]:
    text = _explanation_text(explanation)
    lowered = text.lower()
    failures: list[str] = []
    for phrase in FORBIDDEN_CLAIMS:
        if phrase in lowered:
            failures.append(f"forbidden_claim:{phrase}")

    models_in_report = {str(item.get("model")) for item in summary if item.get("model")}
    allowed_models = models_in_report | {DEFAULT_MODEL}
    mentioned_models = {
        model
        for model in KNOWN_MODEL_NAMES
        if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(model)}(?![A-Za-z0-9_-])", lowered)
    }
    unsupported_models = mentioned_models - allowed_models
    if unsupported_models:
        failures.append("unsupported_model_mentions:" + ",".join(sorted(unsupported_models)))

    recommended = source_rec.get("recommendedModel")
    if recommended and recommended not in models_in_report:
        failures.append("recommendation_model_missing_from_scores")
    if recommended and _text(recommended).lower() not in lowered:
        failures.append("recommendation_not_mentioned")
    if not recommended and "recommends reviewing" in lowered:
        failures.append("invented_recommendation")

    return not failures, failures


def _fallback_explanation(
    source_rec: dict[str, Any],
    summary: list[dict[str, Any]],
    profile: str,
    style: str,
    sample_count: int,
) -> dict[str, Any]:
    model = source_rec.get("recommendedModel")
    caveats = _common_caveats(sample_count)
    if model and model in {item.get("model") for item in summary}:
        score = _score_for_model(summary, _text(model)) or {}
        return {
            "shortRecommendation": (
                f"The grounded scoring report recommends reviewing {model} for {profile} "
                f"(overall score {_score_text(score.get('overallScore'))})."
            ),
            "detailedExplanation": (
                f"{model} is the highest scored model in the supplied report. "
                "This explanation was regenerated from a safe template after validation."
            ),
            "caveats": caveats,
            "nextActionSuggestion": "Keep the default unchanged and collect more samples before any policy change.",
        }
    return {
        "shortRecommendation": "No grounded model recommendation is available.",
        "detailedExplanation": (
            "The supplied scoring report does not provide a usable deterministic recommendation. "
            "This safe template avoids inventing a model choice."
        ),
        "caveats": caveats,
        "nextActionSuggestion": "Collect more samples and rerun the evaluation and scoring reports.",
    }


def validate_or_fallback(
    explanation: dict[str, Any],
    source_rec: dict[str, Any],
    summary: list[dict[str, Any]],
    profile: str,
    style: str,
    sample_count: int,
) -> tuple[dict[str, Any], list[str]]:
    ok, failures = validate_grounding(explanation, source_rec, summary)
    if ok:
        return explanation, []
    fallback = _fallback_explanation(source_rec, summary, profile, style, sample_count)
    ok, fallback_failures = validate_grounding(fallback, source_rec, summary)
    if not ok:
        raise ValueError("Safe fallback explanation failed grounding validation: " + ", ".join(fallback_failures))
    return fallback, failures


def build_facts_used(
    source_rec: dict[str, Any],
    summary: list[dict[str, Any]],
    profile: str,
    sample_count: int,
) -> list[str]:
    facts = [
        f"profile={profile}",
        f"sampleCount={sample_count}",
        f"recommendedModel={source_rec.get('recommendedModel')}",
        f"confidence={source_rec.get('confidence')}",
        f"marginToRunnerUp={source_rec.get('marginToRunnerUp')}",
    ]
    for item in summary:
        facts.append(
            f"{item.get('model')}:overall={item.get('overallScore')},"
            f"reliability={item.get('reliabilityScore')},speed={item.get('speedScore')}"
        )
    return facts


def build_explanation_report(
    scoring_report: dict[str, Any],
    input_path: Path,
    profile: str | None = None,
    style: str = "christina",
    generated_at: datetime | None = None,
    use_llm: bool = False,
) -> dict[str, Any]:
    generated_at = generated_at or datetime.now().astimezone()
    report_profile = _text(scoring_report.get("profile") or "balanced")
    if profile and profile != report_profile:
        raise ValueError(f"Requested profile {profile!r} does not match scoring report profile {report_profile!r}.")
    profile = profile or report_profile
    if profile not in PROFILE_ORDER:
        raise ValueError(f"Unsupported profile {profile!r}.")
    if style not in STYLE_ORDER:
        raise ValueError(f"Unsupported style {style!r}.")

    summary = build_model_score_summary(scoring_report)
    source_rec = _source_recommendation(scoring_report)
    sample_count = int(scoring_report.get("sampleCount") or 0)
    explanation = build_explanation(source_rec, summary, profile, style, sample_count)
    explanation, removed_claims = validate_or_fallback(
        explanation,
        source_rec,
        summary,
        profile,
        style,
        sample_count,
    )
    unsupported_removed = list(removed_claims)
    llm_used = False
    if use_llm:
        unsupported_removed.append("llm_requested_but_deterministic_fallback_used")

    return {
        "schemaVersion": SCHEMA_VERSION,
        "task": TASK_ID,
        "generatedAt": generated_at.isoformat(timespec="seconds"),
        "inputReportBasename": input_path.name,
        "inputReportPathRedacted": True,
        "profile": profile,
        "style": style,
        "sourceRecommendation": source_rec,
        "modelScoreSummary": summary,
        "explanation": explanation,
        "grounding": {
            "factsUsed": build_facts_used(source_rec, summary, profile, sample_count),
            "forbiddenClaimsChecked": list(FORBIDDEN_CLAIMS),
            "unsupportedClaimsRemoved": unsupported_removed,
            "llmUsed": llm_used,
        },
        "defaultChange": {
            "changed": False,
            "currentDefault": DEFAULT_MODEL,
        },
        "runtimeAutoSwitch": {
            "changed": False,
        },
    }


def write_report(
    report: dict[str, Any],
    output_dir: Path | None = None,
    generated_at: datetime | None = None,
) -> Path:
    generated_at = generated_at or datetime.now().astimezone()
    day = generated_at.strftime("%Y%m%d")
    stamp = generated_at.strftime("%Y%m%d_%H%M%S")
    base_dir = output_dir or (REPO_ROOT / "outputs" / "stt_model_explanation")
    target_dir = base_dir / day
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"stt_model_explanation_report_{stamp}.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + os.linesep, encoding="utf-8")
    return output_path


def print_summary(report: dict[str, Any], output_path: Path) -> None:
    rec = report["sourceRecommendation"]
    explanation = report["explanation"]
    print("TASK-STT-006C grounded STT recommendation explanation")
    print(f"  output: {output_path}")
    print(f"  input: {report['inputReportBasename']}")
    print(f"  profile: {report['profile']}")
    print(f"  style: {report['style']}")
    print(f"  recommendedModel: {rec.get('recommendedModel')}")
    print(f"  confidence: {rec.get('confidence')}")
    print(f"  llmUsed: {report['grounding']['llmUsed']}")
    print(f"  shortRecommendation: {explanation.get('shortRecommendation')}")
    print("  note: explanation only; no default change and no runtime auto-switch")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Explain a TASK-STT-006B scoring report with grounded deterministic text.",
    )
    parser.add_argument("--input", required=True, help="TASK-STT-006B scoring report JSON.")
    parser.add_argument(
        "--profile",
        choices=PROFILE_ORDER,
        help="Expected scoring profile. If provided, it must match the input report profile.",
    )
    parser.add_argument(
        "--style",
        default="christina",
        choices=STYLE_ORDER,
        help="Explanation style. Default: christina.",
    )
    parser.add_argument("--output-dir", help="Base output directory. Default: outputs/stt_model_explanation/YYYYMMDD/.")
    parser.add_argument("--pretty", action="store_true", help="Print the explanation JSON report after writing it.")
    llm_group = parser.add_mutually_exclusive_group()
    llm_group.add_argument("--no-llm", action="store_true", help="Use deterministic templates only. This is the default.")
    llm_group.add_argument(
        "--use-llm",
        action="store_true",
        help="Accepted for future compatibility; currently falls back to deterministic grounded templates.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        input_path = Path(args.input).expanduser()
        if not input_path.is_file():
            raise ValueError(f"Input report does not exist: {input_path}")
        generated_at = datetime.now().astimezone()
        scoring_report = load_report(input_path)
        report = build_explanation_report(
            scoring_report,
            input_path=input_path,
            profile=args.profile,
            style=args.style,
            generated_at=generated_at,
            use_llm=bool(args.use_llm),
        )
        output_path = write_report(
            report,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            generated_at=generated_at,
        )
        print_summary(report, output_path)
        if args.pretty:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:  # noqa: BLE001
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
