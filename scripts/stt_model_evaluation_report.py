"""
TASK-STT-006A backend STT model evaluation report.

Compares runtime STT request models against local user-provided audio samples
and writes structured JSON. This is data collection only: it does not choose or
recommend a model.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import json
import mimetypes
import os
from pathlib import Path
import platform
import sys
import time
from typing import Any, Callable
import wave


REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


DEFAULT_MODELS = ("tiny", "base", "small")
ALLOWED_MODELS = frozenset(DEFAULT_MODELS)
DEFAULT_LANGUAGE = "zh"


Transcriber = Callable[[bytes, str, str | None, str | None], dict[str, Any]]


def parse_models(value: str | None) -> list[str]:
    if value is None or not value.strip():
        return list(DEFAULT_MODELS)
    models: list[str] = []
    for raw in value.split(","):
        model = raw.strip()
        if not model:
            continue
        if model not in ALLOWED_MODELS:
            allowed = ", ".join(DEFAULT_MODELS)
            raise ValueError(f"Unsupported model {model!r}; allowed: {allowed}.")
        if model not in models:
            models.append(model)
    if not models:
        raise ValueError("At least one model must be provided.")
    return models


def _audio_duration_ms(path: Path) -> int | None:
    try:
        with wave.open(str(path), "rb") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            if rate <= 0:
                return None
            return int(round((frames / rate) * 1000))
    except Exception:
        return None


def _mime_type_for(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    if guessed:
        return guessed
    if path.suffix.lower() == ".wav":
        return "audio/wav"
    if path.suffix.lower() == ".webm":
        return "audio/webm"
    return "application/octet-stream"


def build_samples(audio_paths: list[str], labels: list[str] | None = None) -> list[dict[str, Any]]:
    labels = labels or []
    if labels and len(labels) != len(audio_paths):
        raise ValueError("Repeated --label count must match repeated --audio count.")

    samples: list[dict[str, Any]] = []
    for idx, raw_path in enumerate(audio_paths):
        path = Path(raw_path).expanduser()
        if not path.is_file():
            raise ValueError(f"Audio file does not exist: {path}")
        stat = path.stat()
        label = labels[idx].strip() if idx < len(labels) else ""
        samples.append(
            {
                "id": f"sample-{idx + 1}",
                "label": label or path.stem,
                "path": str(path),
                "samplePath": path.name,
                "pathRedacted": True,
                "mimeType": _mime_type_for(path),
                "durationMs": _audio_duration_ms(path),
                "fileSizeBytes": stat.st_size,
            }
        )
    if not samples:
        raise ValueError("Provide at least one --audio file.")
    return samples


def _status_from_runtime(result: dict[str, Any], error: str | None = None) -> str:
    if error:
        return "error"
    runtime_status = str(result.get("status") or "")
    if runtime_status == "ok":
        return "success"
    if runtime_status in {"no_speech", "empty"}:
        return "no_speech"
    return "error"


def _fallback_from_runtime(result: dict[str, Any]) -> str:
    model_fallback = str(result.get("modelFallbackReason") or "none")
    provider_fallback = str(result.get("sttProviderFallbackReason") or "none")
    if model_fallback != "none":
        return model_fallback
    if provider_fallback != "none":
        return provider_fallback
    return "none"


def _result_from_runtime(
    model: str,
    runtime_result: dict[str, Any],
    latency_ms: int,
    duration_ms: int | None,
    error: str | None = None,
) -> dict[str, Any]:
    final = str(
        runtime_result.get("finalTranscript")
        or runtime_result.get("transcript")
        or ""
    )
    raw = str(runtime_result.get("rawTranscript") or "")
    status = _status_from_runtime(runtime_result, error)
    return {
        "model": model,
        "status": status,
        "runtimeStatus": runtime_result.get("status") or ("error" if error else ""),
        "latencyMs": latency_ms,
        "rtf": (latency_ms / duration_ms) if duration_ms else None,
        "transcriptRaw": raw,
        "transcriptFinal": final,
        "transcriptLength": len(final),
        "detectedLanguage": runtime_result.get("detectedLanguage"),
        "noSpeechProbability": runtime_result.get("sttNoSpeechProbability"),
        "noSpeechGuardApplied": bool(runtime_result.get("noSpeechGuardApplied", False)),
        "noSpeechGuardReason": runtime_result.get("noSpeechGuardReason") or "none",
        "noSpeechGuardDecisionTrace": runtime_result.get("noSpeechGuardDecisionTrace"),
        "audioRms": runtime_result.get("audioRms"),
        "audioPeak": runtime_result.get("audioPeak"),
        "speechDetected": runtime_result.get("audioSpeechDetected"),
        "voicedRatio": runtime_result.get("audioSignalRatio"),
        "provider": runtime_result.get("sttProviderResolved") or runtime_result.get("provider"),
        "providerLoadStatus": runtime_result.get("sttProviderLoadStatus"),
        "modelLoadStatus": runtime_result.get("modelLoadStatus"),
        "requestedModel": runtime_result.get("requestedModel"),
        "resolvedModel": runtime_result.get("resolvedModel"),
        "modelSource": runtime_result.get("modelSource"),
        "fallback": _fallback_from_runtime(runtime_result),
        "error": error,
        "score": None,
    }


def _error_result(model: str, latency_ms: int, duration_ms: int | None, error: str) -> dict[str, Any]:
    return _result_from_runtime(
        model,
        {
            "status": "error",
            "requestedModel": model,
            "resolvedModel": model,
            "modelSource": "request",
            "modelFallbackReason": "none",
            "sttProviderFallbackReason": "none",
        },
        latency_ms,
        duration_ms,
        error=error[:500],
    )


def _default_transcriber(
    audio_bytes: bytes,
    mime_type: str,
    language: str | None,
    request_model: str | None,
) -> dict[str, Any]:
    from app.stt import stt_service  # noqa: PLC0415

    return stt_service.transcribe_audio_bytes(
        audio_bytes,
        mime_type=mime_type,
        language=language,
        request_model=request_model,
    )


def environment_info() -> dict[str, Any]:
    from app.stt import stt_service  # noqa: PLC0415

    provider_resolution = getattr(stt_service, "_STT_PROVIDER_RESOLUTION", {})
    return {
        "providerName": provider_resolution.get("resolved_provider", "unknown"),
        "providerRequested": provider_resolution.get("requested_provider", "unknown"),
        "providerSource": provider_resolution.get("provider_source", "unknown"),
        "providerFallbackReason": provider_resolution.get("provider_fallback_reason", "unknown"),
        "pythonVersion": platform.python_version(),
        "platform": platform.platform(),
    }


def evaluate_samples(
    samples: list[dict[str, Any]],
    models: list[str],
    language: str,
    transcriber: Transcriber = _default_transcriber,
) -> list[dict[str, Any]]:
    evaluated: list[dict[str, Any]] = []
    for sample in samples:
        path = Path(sample["path"])
        audio_bytes = path.read_bytes()
        model_results: list[dict[str, Any]] = []
        for model in models:
            start = time.perf_counter()
            try:
                runtime_result = transcriber(audio_bytes, sample["mimeType"], language, model)
                latency_ms = int(round((time.perf_counter() - start) * 1000))
                result = _result_from_runtime(model, runtime_result, latency_ms, sample["durationMs"])
            except Exception as exc:  # noqa: BLE001
                latency_ms = int(round((time.perf_counter() - start) * 1000))
                result = _error_result(model, latency_ms, sample["durationMs"], str(exc))
            model_results.append(result)

        evaluated.append(
            {
                "id": sample["id"],
                "label": sample["label"],
                "samplePath": sample["samplePath"],
                "pathRedacted": sample["pathRedacted"],
                "mimeType": sample["mimeType"],
                "durationMs": sample["durationMs"],
                "fileSizeBytes": sample["fileSizeBytes"],
                "results": model_results,
            }
        )
    return evaluated


def build_summary(samples: list[dict[str, Any]], models: list[str]) -> dict[str, Any]:
    by_model: dict[str, Any] = {}
    for model in models:
        results = [
            result
            for sample in samples
            for result in sample["results"]
            if result["model"] == model
        ]
        counts = Counter(result["status"] for result in results)
        latencies = [
            result["latencyMs"]
            for result in results
            if isinstance(result.get("latencyMs"), (int, float))
        ]
        by_model[model] = {
            "successCount": counts.get("success", 0),
            "noSpeechCount": counts.get("no_speech", 0),
            "errorCount": counts.get("error", 0),
            "avgLatencyMs": (sum(latencies) / len(latencies)) if latencies else None,
            "score": None,
        }
    return {
        "byModel": by_model,
        "notes": "Data collection only; no model recommendation or AI explanation is produced.",
    }


def build_report(
    samples: list[dict[str, Any]],
    models: list[str],
    language: str,
    generated_at: datetime | None = None,
    transcriber: Transcriber = _default_transcriber,
) -> dict[str, Any]:
    generated_at = generated_at or datetime.now().astimezone()
    evaluated_samples = evaluate_samples(samples, models, language, transcriber=transcriber)
    return {
        "task": "TASK-STT-006A",
        "generatedAt": generated_at.isoformat(timespec="seconds"),
        "language": language,
        "modelsEvaluated": models,
        "environment": environment_info(),
        "samples": evaluated_samples,
        "summary": build_summary(evaluated_samples, models),
    }


def write_report(
    report: dict[str, Any],
    output_dir: Path | None = None,
    generated_at: datetime | None = None,
) -> Path:
    generated_at = generated_at or datetime.now().astimezone()
    day = generated_at.strftime("%Y%m%d")
    stamp = generated_at.strftime("%Y%m%d_%H%M%S")
    base_dir = output_dir or (REPO_ROOT / "outputs" / "stt_model_evaluation")
    target_dir = base_dir / day
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"stt_model_evaluation_report_{stamp}.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + os.linesep, encoding="utf-8")
    return output_path


def print_summary(report: dict[str, Any], output_path: Path) -> None:
    print("TASK-STT-006A STT model evaluation report")
    print(f"  output: {output_path}")
    print(f"  language: {report['language']}")
    print(f"  samples: {len(report['samples'])}")
    print(f"  models: {', '.join(report['modelsEvaluated'])}")
    by_model = report.get("summary", {}).get("byModel", {})
    for model in report["modelsEvaluated"]:
        summary = by_model.get(model, {})
        print(
            "  "
            f"{model}: success={summary.get('successCount', 0)} "
            f"no_speech={summary.get('noSpeechCount', 0)} "
            f"error={summary.get('errorCount', 0)} "
            f"avgLatencyMs={summary.get('avgLatencyMs')}"
        )
    print("  recommendation: not generated (data collection only)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a backend STT model evaluation JSON report for local audio samples.",
    )
    parser.add_argument("--audio", action="append", required=True, help="Audio sample path. Repeat for multiple files.")
    parser.add_argument("--label", action="append", help="Optional label for the matching --audio. Repeat per sample.")
    parser.add_argument(
        "--output-dir",
        help="Base output directory. Default: outputs/stt_model_evaluation/YYYYMMDD/.",
    )
    parser.add_argument("--language", default=DEFAULT_LANGUAGE, help="Language hint passed to STT. Default: zh.")
    parser.add_argument(
        "--models",
        default=",".join(DEFAULT_MODELS),
        help="Comma-separated models to evaluate. Default: tiny,base,small.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        models = parse_models(args.models)
        samples = build_samples(args.audio, args.label)
        generated_at = datetime.now().astimezone()
        report = build_report(samples, models, args.language, generated_at=generated_at)
        output_path = write_report(
            report,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            generated_at=generated_at,
        )
        print_summary(report, output_path)
        return 0
    except Exception as exc:  # noqa: BLE001
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
