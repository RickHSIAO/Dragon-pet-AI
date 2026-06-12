"""
TASK-STT-006B deterministic STT model scoring report.

Reads a TASK-STT-006A evaluation report and produces runtime-suitability
scores. This script is deterministic and does not call an LLM, change runtime
configuration, or auto-switch the STT model.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
import math
import os
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = "1.0"
DEFAULT_PROFILE = "balanced"
PROFILE_ORDER = ("manual_mic", "conversation", "balanced")

PROFILE_WEIGHTS: dict[str, dict[str, float]] = {
    "manual_mic": {
        "reliability": 0.36,
        "speed": 0.10,
        "speechEvidence": 0.16,
        "transcriptSignal": 0.24,
        "hallucinationRisk": 0.14,
        "fallbackPenalty": 1.0,
        "speedExponent": 0.75,
    },
    "conversation": {
        "reliability": 0.30,
        "speed": 0.30,
        "speechEvidence": 0.10,
        "transcriptSignal": 0.14,
        "hallucinationRisk": 0.16,
        "fallbackPenalty": 1.0,
        "speedExponent": 1.45,
    },
    "balanced": {
        "reliability": 0.32,
        "speed": 0.20,
        "speechEvidence": 0.14,
        "transcriptSignal": 0.18,
        "hallucinationRisk": 0.16,
        "fallbackPenalty": 1.0,
        "speedExponent": 1.0,
    },
}


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _round(value: float | None, digits: int = 4) -> float | None:
    if value is None or not math.isfinite(value):
        return None
    return round(value, digits)


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def _average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _safe_status(result: dict[str, Any]) -> str:
    status = str(result.get("status") or "").strip().lower()
    if status in {"success", "ok"}:
        return "success"
    if status in {"no_speech", "empty"}:
        return "no_speech"
    return "error"


def _safe_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _is_fallback(value: Any) -> bool:
    text = str(value or "none").strip().lower()
    return bool(text and text != "none")


def _has_provider_load_error(result: dict[str, Any]) -> bool:
    status = str(result.get("providerLoadStatus") or "").strip().lower()
    if status == "error":
        return True
    if result.get("providerLoadError"):
        return True
    return False


def _has_model_load_error(result: dict[str, Any]) -> bool:
    status = str(result.get("modelLoadStatus") or "").strip().lower()
    if status == "error":
        return True
    if result.get("modelLoadError"):
        return True
    return False


def _garbled_ratio(text: str) -> float:
    if not text:
        return 0.0
    suspicious = 0
    for char in text:
        code = ord(char)
        if char == "\ufffd" or 0xE000 <= code <= 0xF8FF:
            suspicious += 1
        elif char == "?" or char == "\uFFFD":
            suspicious += 1
    return suspicious / max(1, len(text))


def load_report(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Input report must be a JSON object.")
    if not isinstance(data.get("samples"), list):
        raise ValueError("Input report is missing a samples list.")
    return data


def _models_from_report(report: dict[str, Any]) -> list[str]:
    models: list[str] = []
    source_models = report.get("modelsEvaluated") or report.get("models") or []
    if isinstance(source_models, list):
        for model in source_models:
            name = str(model or "").strip()
            if name and name not in models:
                models.append(name)
    for sample in report.get("samples", []):
        if not isinstance(sample, dict):
            continue
        for result in sample.get("results", []):
            if not isinstance(result, dict):
                continue
            name = str(result.get("model") or "").strip()
            if name and name not in models:
                models.append(name)
    return models


def _results_by_model(report: dict[str, Any], models: list[str]) -> dict[str, list[dict[str, Any]]]:
    by_model: dict[str, list[dict[str, Any]]] = {model: [] for model in models}
    for sample in report.get("samples", []):
        if not isinstance(sample, dict):
            continue
        for result in sample.get("results", []):
            if not isinstance(result, dict):
                continue
            model = str(result.get("model") or "").strip()
            if model in by_model:
                by_model[model].append(result)
    return by_model


def compute_model_aggregates(report: dict[str, Any], models: list[str] | None = None) -> dict[str, dict[str, Any]]:
    models = models or _models_from_report(report)
    sample_count = len(report.get("samples", []))
    by_model = _results_by_model(report, models)
    aggregates: dict[str, dict[str, Any]] = {}

    for model in models:
        results = by_model.get(model, [])
        counts = Counter(_safe_status(result) for result in results)
        latencies = [_number(result.get("latencyMs")) for result in results]
        rtfs = [_number(result.get("rtf")) for result in results]
        lengths = [_number(result.get("transcriptLength")) for result in results]
        no_speech_probs = [_number(result.get("noSpeechProbability")) for result in results]
        rms_values = [_number(result.get("audioRms")) for result in results]
        peak_values = [_number(result.get("audioPeak")) for result in results]
        voiced_ratios = [_number(result.get("voicedRatio")) for result in results]
        speech_values = [_safe_bool(result.get("speechDetected")) for result in results]

        latencies_f = [value for value in latencies if value is not None]
        rtfs_f = [value for value in rtfs if value is not None]
        lengths_f = [value for value in lengths if value is not None]
        no_speech_probs_f = [value for value in no_speech_probs if value is not None]
        rms_values_f = [value for value in rms_values if value is not None]
        peak_values_f = [value for value in peak_values if value is not None]
        voiced_ratios_f = [value for value in voiced_ratios if value is not None]
        speech_values_b = [value for value in speech_values if value is not None]

        result_count = len(results)
        denom = result_count or sample_count or 1
        success_count = counts.get("success", 0)
        no_speech_count = counts.get("no_speech", 0)
        error_count = counts.get("error", 0)
        guard_applied_count = sum(1 for result in results if result.get("noSpeechGuardApplied") is True)
        fallback_count = sum(1 for result in results if _is_fallback(result.get("fallback")))
        provider_load_error_count = sum(1 for result in results if _has_provider_load_error(result))
        model_load_error_count = sum(1 for result in results if _has_model_load_error(result))
        garbled_ratios = [
            _garbled_ratio(str(result.get("transcriptFinal") or result.get("transcriptRaw") or ""))
            for result in results
        ]

        aggregates[model] = {
            "successCount": success_count,
            "noSpeechCount": no_speech_count,
            "errorCount": error_count,
            "sampleCount": result_count,
            "expectedSampleCount": sample_count,
            "missingResultCount": max(0, sample_count - result_count),
            "successRate": _round(success_count / denom),
            "errorRate": _round(error_count / denom),
            "noSpeechRate": _round(no_speech_count / denom),
            "avgLatencyMs": _round(_average(latencies_f), 2),
            "avgRtf": _round(_average(rtfs_f), 4),
            "avgTranscriptLength": _round(_average(lengths_f), 2),
            "avgNoSpeechProbability": _round(_average(no_speech_probs_f), 4),
            "avgAudioRms": _round(_average(rms_values_f), 6),
            "avgAudioPeak": _round(_average(peak_values_f), 6),
            "avgVoicedRatio": _round(_average(voiced_ratios_f), 6),
            "speechDetectedRate": _round(
                sum(1 for value in speech_values_b if value) / len(speech_values_b)
                if speech_values_b else None
            ),
            "guardAppliedCount": guard_applied_count,
            "fallbackCount": fallback_count,
            "providerLoadErrorCount": provider_load_error_count,
            "modelLoadErrorCount": model_load_error_count,
            "avgGarbledRatio": _round(_average(garbled_ratios), 4),
            "hasMetricGaps": any(
                not values
                for values in (
                    latencies_f,
                    lengths_f,
                    rms_values_f,
                    peak_values_f,
                    voiced_ratios_f,
                )
            ),
        }
    return aggregates


def _speech_like_sample_set(aggregates: dict[str, dict[str, Any]]) -> bool:
    for aggregate in aggregates.values():
        if (aggregate.get("speechDetectedRate") or 0) > 0:
            return True
        if (aggregate.get("avgTranscriptLength") or 0) >= 4:
            return True
        if (aggregate.get("avgAudioRms") or 0) >= 0.008:
            return True
        if (aggregate.get("avgVoicedRatio") or 0) >= 0.005:
            return True
    return False


def parse_weights(profile: str, raw_weights: str | None = None) -> dict[str, float]:
    if profile not in PROFILE_WEIGHTS:
        allowed = ", ".join(PROFILE_ORDER)
        raise ValueError(f"Unsupported profile {profile!r}; allowed: {allowed}.")
    weights = dict(PROFILE_WEIGHTS[profile])
    if not raw_weights:
        return weights

    named = raw_weights.strip()
    if named in PROFILE_WEIGHTS:
        return dict(PROFILE_WEIGHTS[named])

    try:
        override = json.loads(raw_weights)
    except json.JSONDecodeError as exc:
        raise ValueError("--weights must be a known profile name or a JSON object.") from exc
    if not isinstance(override, dict):
        raise ValueError("--weights JSON must be an object.")
    for key, value in override.items():
        if key not in weights:
            raise ValueError(f"Unsupported weight key {key!r}.")
        number = _number(value)
        if number is None or number < 0:
            raise ValueError(f"Weight {key!r} must be a non-negative number.")
        weights[key] = number
    return weights


def _speed_score(
    aggregate: dict[str, Any],
    fastest_latency: float | None,
    fastest_rtf: float | None,
    speed_exponent: float,
) -> float:
    latency = aggregate.get("avgLatencyMs")
    rtf = aggregate.get("avgRtf")
    parts: list[tuple[float, float]] = []
    if isinstance(latency, (int, float)) and latency > 0 and fastest_latency:
        parts.append((0.7, _clamp(100.0 * ((fastest_latency / latency) ** speed_exponent))))
    if isinstance(rtf, (int, float)) and rtf > 0 and fastest_rtf:
        parts.append((0.3, _clamp(100.0 * ((fastest_rtf / rtf) ** speed_exponent))))
    if not parts:
        return 50.0
    weight_sum = sum(weight for weight, _ in parts)
    return sum(weight * score for weight, score in parts) / weight_sum


def score_models(
    aggregates: dict[str, dict[str, Any]],
    profile: str = DEFAULT_PROFILE,
    weights: dict[str, float] | None = None,
) -> dict[str, dict[str, Any]]:
    weights = weights or parse_weights(profile)
    speech_like = _speech_like_sample_set(aggregates)
    latencies = [
        aggregate.get("avgLatencyMs")
        for aggregate in aggregates.values()
        if isinstance(aggregate.get("avgLatencyMs"), (int, float))
        and aggregate.get("avgLatencyMs") > 0
    ]
    rtfs = [
        aggregate.get("avgRtf")
        for aggregate in aggregates.values()
        if isinstance(aggregate.get("avgRtf"), (int, float))
        and aggregate.get("avgRtf") > 0
    ]
    fastest_latency = min(latencies) if latencies else None
    fastest_rtf = min(rtfs) if rtfs else None
    scores: dict[str, dict[str, Any]] = {}

    for model, aggregate in aggregates.items():
        success_rate = float(aggregate.get("successRate") or 0)
        error_rate = float(aggregate.get("errorRate") or 0)
        no_speech_rate = float(aggregate.get("noSpeechRate") or 0)
        guard_rate = (
            aggregate.get("guardAppliedCount", 0) / max(1, aggregate.get("sampleCount") or aggregate.get("expectedSampleCount") or 1)
        )
        fallback_rate = (
            aggregate.get("fallbackCount", 0) / max(1, aggregate.get("sampleCount") or aggregate.get("expectedSampleCount") or 1)
        )
        provider_error_rate = (
            aggregate.get("providerLoadErrorCount", 0) / max(1, aggregate.get("sampleCount") or aggregate.get("expectedSampleCount") or 1)
        )
        model_error_rate = (
            aggregate.get("modelLoadErrorCount", 0) / max(1, aggregate.get("sampleCount") or aggregate.get("expectedSampleCount") or 1)
        )

        no_speech_penalty = 35.0 if speech_like else 10.0
        reliability_score = _clamp(
            100.0 * success_rate
            - 70.0 * error_rate
            - no_speech_penalty * no_speech_rate
            - 20.0 * (aggregate.get("missingResultCount") or 0)
        )
        speed_score = _speed_score(
            aggregate,
            fastest_latency=fastest_latency,
            fastest_rtf=fastest_rtf,
            speed_exponent=float(weights.get("speedExponent", 1.0)),
        )

        speech_detected_rate = aggregate.get("speechDetectedRate")
        speech_detected_component = 0.5 if speech_detected_rate is None else float(speech_detected_rate)
        voiced_ratio = aggregate.get("avgVoicedRatio")
        rms = aggregate.get("avgAudioRms")
        peak = aggregate.get("avgAudioPeak")
        voiced_score = _clamp(100.0 * min(1.0, float(voiced_ratio or 0) / 0.05)) if voiced_ratio is not None else 50.0
        rms_score = _clamp(100.0 * min(1.0, float(rms or 0) / 0.012)) if rms is not None else 50.0
        peak_score = _clamp(100.0 * min(1.0, float(peak or 0) / 0.08)) if peak is not None else 50.0
        speech_evidence_score = _clamp(
            45.0 * speech_detected_component
            + 25.0 * (voiced_score / 100.0)
            + 20.0 * (rms_score / 100.0)
            + 10.0 * (peak_score / 100.0)
        )

        transcript_length = aggregate.get("avgTranscriptLength")
        non_empty_rate = success_rate if speech_like else max(success_rate, 1.0 - no_speech_rate)
        length_bonus = 0.0
        if isinstance(transcript_length, (int, float)):
            length_bonus = min(15.0, max(0.0, transcript_length) * 1.5)
        garbled_penalty = 40.0 * float(aggregate.get("avgGarbledRatio") or 0)
        transcript_signal_score = _clamp(25.0 + 60.0 * non_empty_rate + length_bonus - garbled_penalty)

        no_speech_probability = aggregate.get("avgNoSpeechProbability")
        if isinstance(no_speech_probability, (int, float)):
            probability_penalty = (55.0 if speech_like else 20.0) * float(no_speech_probability)
        else:
            probability_penalty = 10.0
        guard_penalty = (45.0 if speech_like else 15.0) * guard_rate
        hallucination_risk_score = _clamp(100.0 - probability_penalty - guard_penalty)

        fallback_penalty = _clamp(
            40.0 * fallback_rate
            + 55.0 * provider_error_rate
            + 45.0 * model_error_rate
            + 20.0 * error_rate
        )
        component_total = (
            float(weights["reliability"]) * reliability_score
            + float(weights["speed"]) * speed_score
            + float(weights["speechEvidence"]) * speech_evidence_score
            + float(weights["transcriptSignal"]) * transcript_signal_score
            + float(weights["hallucinationRisk"]) * hallucination_risk_score
        )
        overall_score = _clamp(component_total - float(weights.get("fallbackPenalty", 1.0)) * fallback_penalty)

        scores[model] = {
            "reliabilityScore": _round(reliability_score, 2),
            "speedScore": _round(speed_score, 2),
            "speechEvidenceScore": _round(speech_evidence_score, 2),
            "transcriptSignalScore": _round(transcript_signal_score, 2),
            "hallucinationRiskScore": _round(hallucination_risk_score, 2),
            "fallbackPenalty": _round(fallback_penalty, 2),
            "overallScore": _round(overall_score, 2),
            "reasonCodes": _reason_codes_for_model(model, aggregate, overall_score, speech_like),
        }
    return scores


def _reason_codes_for_model(
    model: str,
    aggregate: dict[str, Any],
    overall_score: float,
    speech_like: bool,
) -> list[str]:
    codes = ["runtime_suitability_score_only"]
    if speech_like:
        codes.append("speech_like_samples_detected")
    if aggregate.get("successRate") == 1:
        codes.append("all_samples_success")
    if aggregate.get("errorCount"):
        codes.append("has_error_results")
    if aggregate.get("noSpeechCount"):
        codes.append("has_no_speech_results")
    if aggregate.get("fallbackCount"):
        codes.append("has_fallback_results")
    if aggregate.get("hasMetricGaps"):
        codes.append("missing_optional_metrics")
    if overall_score >= 80:
        codes.append("high_runtime_suitability")
    elif overall_score < 50:
        codes.append("low_runtime_suitability")
    return codes


def build_recommendation(
    model_scores: dict[str, dict[str, Any]],
    aggregates: dict[str, dict[str, Any]],
    profile: str,
) -> dict[str, Any]:
    ranked = sorted(
        (
            (model, score.get("overallScore"))
            for model, score in model_scores.items()
            if isinstance(score.get("overallScore"), (int, float))
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    decision_limits = [
        "No reference transcript was provided; this is runtime-suitability scoring, not true accuracy or WER.",
        "This recommendation does not change the committed STT default.",
        "This recommendation does not auto-switch the runtime STT model.",
        "Future AI explanation is a separate stage and is not generated here.",
    ]
    if not ranked:
        return {
            "recommendedModel": None,
            "confidence": "low",
            "marginToRunnerUp": None,
            "reasonCodes": ["no_scored_models"],
            "humanReadableSummary": "No deterministic recommendation was produced because no model had scorable data.",
            "decisionLimits": decision_limits,
        }

    top_model, top_score = ranked[0]
    if top_score is None or top_score < 40:
        return {
            "recommendedModel": None,
            "confidence": "low",
            "marginToRunnerUp": None,
            "reasonCodes": ["insufficient_runtime_suitability"],
            "humanReadableSummary": "No deterministic recommendation was produced because the top score was too low.",
            "decisionLimits": decision_limits,
        }

    runner_up_score = ranked[1][1] if len(ranked) > 1 else None
    margin = float(top_score) - float(runner_up_score) if runner_up_score is not None else None
    if margin is None:
        confidence = "low"
    elif margin < 3:
        confidence = "low"
    elif margin < 10 or float(top_score) < 75:
        confidence = "medium"
    else:
        confidence = "high"

    reason_codes = ["top_overall_score", f"profile_{profile}", "no_reference_transcripts"]
    if margin is not None and margin < 3:
        reason_codes.append("close_margin_to_runner_up")
    aggregate = aggregates.get(top_model, {})
    if aggregate.get("successRate") == 1:
        reason_codes.append("all_samples_success")
    if aggregate.get("errorCount") == 0:
        reason_codes.append("no_error_results")
    if aggregate.get("noSpeechCount") == 0:
        reason_codes.append("no_no_speech_results")
    if ranked and len(ranked) > 1:
        runner_up = ranked[1][0]
        top_latency = aggregate.get("avgLatencyMs")
        runner_latency = aggregates.get(runner_up, {}).get("avgLatencyMs")
        if isinstance(top_latency, (int, float)) and isinstance(runner_latency, (int, float)):
            if top_latency < runner_latency:
                reason_codes.append("lower_latency_than_runner_up")

    runner_text = f"{margin:.2f}" if margin is not None else "n/a"
    summary = (
        f"{top_model} ranked highest for {profile} profile with overallScore={top_score:.2f}; "
        f"marginToRunnerUp={runner_text}. This is runtime-suitability scoring only."
    )
    return {
        "recommendedModel": top_model,
        "confidence": confidence,
        "marginToRunnerUp": _round(margin, 2),
        "reasonCodes": reason_codes,
        "humanReadableSummary": summary,
        "decisionLimits": decision_limits,
    }


def build_caveats(report: dict[str, Any], aggregates: dict[str, dict[str, Any]]) -> list[str]:
    caveats = [
        "no_reference_transcripts_runtime_suitability_only",
        "does_not_change_default_model",
        "does_not_auto_switch_runtime_model",
        "no_llm_or_ai_explanation_generated",
    ]
    for model, aggregate in aggregates.items():
        if aggregate.get("missingResultCount"):
            caveats.append(f"{model}_missing_results")
        if aggregate.get("hasMetricGaps"):
            caveats.append(f"{model}_missing_optional_metrics")
        if aggregate.get("errorCount"):
            caveats.append(f"{model}_has_error_results")
    if not report.get("samples"):
        caveats.append("source_report_has_no_samples")
    return sorted(set(caveats))


def build_scoring_report(
    evaluation_report: dict[str, Any],
    input_path: Path,
    profile: str = DEFAULT_PROFILE,
    weights: dict[str, float] | None = None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or datetime.now().astimezone()
    models = _models_from_report(evaluation_report)
    if not models:
        raise ValueError("Input report has no evaluated models.")
    weights = weights or parse_weights(profile)
    aggregates = compute_model_aggregates(evaluation_report, models)
    scores = score_models(aggregates, profile=profile, weights=weights)
    recommendation = build_recommendation(scores, aggregates, profile)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "task": "TASK-STT-006B",
        "generatedAt": generated_at.isoformat(timespec="seconds"),
        "inputReportBasename": input_path.name,
        "inputReportPathRedacted": True,
        "sourceReportGeneratedAt": evaluation_report.get("generatedAt"),
        "profile": profile,
        "models": models,
        "sampleCount": len(evaluation_report.get("samples", [])),
        "weights": weights,
        "modelAggregates": aggregates,
        "modelScores": scores,
        "deterministicRecommendation": recommendation,
        "caveats": build_caveats(evaluation_report, aggregates),
    }


def write_report(
    report: dict[str, Any],
    output_dir: Path | None = None,
    generated_at: datetime | None = None,
) -> Path:
    generated_at = generated_at or datetime.now().astimezone()
    day = generated_at.strftime("%Y%m%d")
    stamp = generated_at.strftime("%Y%m%d_%H%M%S")
    base_dir = output_dir or (REPO_ROOT / "outputs" / "stt_model_scoring")
    target_dir = base_dir / day
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"stt_model_scoring_report_{stamp}.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + os.linesep, encoding="utf-8")
    return output_path


def print_summary(report: dict[str, Any], output_path: Path) -> None:
    print("TASK-STT-006B deterministic STT model scoring report")
    print(f"  output: {output_path}")
    print(f"  input: {report['inputReportBasename']}")
    print(f"  profile: {report['profile']}")
    print(f"  samples: {report['sampleCount']}")
    for model in report["models"]:
        score = report["modelScores"].get(model, {})
        print(
            "  "
            f"{model}: overall={score.get('overallScore')} "
            f"reliability={score.get('reliabilityScore')} "
            f"speed={score.get('speedScore')} "
            f"fallbackPenalty={score.get('fallbackPenalty')}"
        )
    rec = report["deterministicRecommendation"]
    print(f"  recommendedModel: {rec.get('recommendedModel')}")
    print(f"  confidence: {rec.get('confidence')}")
    print("  note: deterministic runtime-suitability scoring only; no default change")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Score a TASK-STT-006A STT model evaluation report deterministically.",
    )
    parser.add_argument("--input", required=True, help="TASK-STT-006A evaluation report JSON.")
    parser.add_argument("--output-dir", help="Base output directory. Default: outputs/stt_model_scoring/YYYYMMDD/.")
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE,
        choices=PROFILE_ORDER,
        help="Scoring profile. Default: balanced.",
    )
    parser.add_argument(
        "--weights",
        help="Optional profile name or JSON object overriding scoring weights.",
    )
    parser.add_argument("--pretty", action="store_true", help="Print the scored JSON report after writing it.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        input_path = Path(args.input).expanduser()
        if not input_path.is_file():
            raise ValueError(f"Input report does not exist: {input_path}")
        generated_at = datetime.now().astimezone()
        evaluation_report = load_report(input_path)
        weights = parse_weights(args.profile, args.weights)
        report = build_scoring_report(
            evaluation_report,
            input_path=input_path,
            profile=args.profile,
            weights=weights,
            generated_at=generated_at,
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
