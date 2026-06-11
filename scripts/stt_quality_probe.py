"""
TASK-STT-002 Chinese STT quality probe.

Runs local faster-whisper model comparisons against explicit WAV samples and
reference text. The probe is intentionally offline by default: model loading
uses local_files_only when supported, and missing models are reported as skipped
unless --allow-download is passed.
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
from pathlib import Path
import re
import sys
import time
import wave
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


DEFAULT_MODELS = ("tiny", "base", "small")
ALLOWED_MODELS = ("tiny", "base", "small", "medium")
ALLOWED_SOURCE_TYPES = {"manual_mic", "conversation_mode", "external_clean_reference"}
PUNCTUATION_RE = re.compile(r"[\s。！？!?，、；：,.\"'`~\-_\[\]{}()（）<>《》「」『』…]+")


def _load_stt_helpers():
    from app.stt import stt_service  # noqa: PLC0415

    return stt_service.correct_transcript_text, stt_service.restore_transcript_punctuation


def _read_manifest(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        samples = data.get("samples")
    else:
        samples = data
    if not isinstance(samples, list):
        raise ValueError("Manifest must be a JSON list or an object with a 'samples' list.")
    return [_normalize_sample(entry, base_dir=path.parent) for entry in samples]


def _normalize_sample(entry: dict[str, Any], base_dir: Path | None = None) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValueError("Manifest sample entries must be objects.")

    sample_path = Path(str(entry.get("path", "")).strip())
    if not sample_path:
        raise ValueError("Sample entry is missing 'path'.")
    if not sample_path.is_absolute() and base_dir is not None:
        sample_path = base_dir / sample_path

    reference = str(entry.get("reference", "")).strip()
    if not reference:
        raise ValueError(f"Sample {sample_path} is missing non-empty 'reference'.")

    source_type = str(entry.get("sourceType", "external_clean_reference")).strip()
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError(
            f"Sample {sample_path} has invalid sourceType {source_type!r}; "
            f"allowed: {', '.join(sorted(ALLOWED_SOURCE_TYPES))}."
        )

    return {
        "id": str(entry.get("id") or sample_path.stem),
        "path": str(sample_path),
        "reference": reference,
        "sourceType": source_type,
        "notes": str(entry.get("notes", "")),
    }


def _samples_from_args(args: argparse.Namespace) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    if args.manifest:
        samples.extend(_read_manifest(Path(args.manifest)))

    cli_samples = args.sample or []
    cli_refs = args.reference or []
    cli_source_types = args.source_type or []
    cli_notes = args.notes or []
    if len(cli_samples) != len(cli_refs):
        raise ValueError("Repeated --sample and --reference counts must match.")

    for idx, sample_path in enumerate(cli_samples):
        source_type = (
            cli_source_types[idx]
            if idx < len(cli_source_types)
            else "external_clean_reference"
        )
        notes = cli_notes[idx] if idx < len(cli_notes) else ""
        samples.append(
            _normalize_sample(
                {
                    "id": Path(sample_path).stem,
                    "path": sample_path,
                    "reference": cli_refs[idx],
                    "sourceType": source_type,
                    "notes": notes,
                }
            )
        )

    if not samples:
        raise ValueError("Provide at least one --sample/--reference pair or --manifest.")
    return samples


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


def _normalize_for_cer(text: str) -> str:
    return PUNCTUATION_RE.sub("", text)


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (0 if ca == cb else 1)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current
    return previous[-1]


def _cer(reference: str, transcript: str) -> tuple[int, int, float | None]:
    ref = _normalize_for_cer(reference)
    hyp = _normalize_for_cer(transcript)
    if not ref:
        return (0 if not hyp else len(hyp), 0, None)
    distance = _levenshtein(ref, hyp)
    return distance, len(ref), distance / len(ref)


def _has_repeated_token_warning(text: str) -> bool:
    if not text:
        return False
    if re.search(r"(\S)\1{3,}", text):
        return True
    tokens = [token for token in re.split(r"\s+", text.strip()) if token]
    for idx in range(len(tokens) - 2):
        if tokens[idx] == tokens[idx + 1] == tokens[idx + 2]:
            return True
    return False


def _load_whisper_model(model_name: str, allow_download: bool) -> tuple[Any | None, str, str | None, int]:
    start = time.perf_counter()
    try:
        from faster_whisper import WhisperModel  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        elapsed = int(round((time.perf_counter() - start) * 1000))
        return None, "skipped", f"faster-whisper is not importable: {exc}", elapsed

    kwargs: dict[str, Any] = {"device": "cpu", "compute_type": "int8"}
    supports_local_files_only = False
    for target in (WhisperModel, getattr(WhisperModel, "__init__", None)):
        if target is None:
            continue
        try:
            signature = inspect.signature(target)
            if "local_files_only" in signature.parameters:
                supports_local_files_only = True
                kwargs["local_files_only"] = not allow_download
                break
        except Exception:
            continue
    if not allow_download and not supports_local_files_only:
        elapsed = int(round((time.perf_counter() - start) * 1000))
        return (
            None,
            "skipped",
            "faster-whisper WhisperModel does not expose local_files_only; "
            "rerun with --allow-download only if downloads are intended.",
            elapsed,
        )

    try:
        model = WhisperModel(model_name, **kwargs)
        elapsed = int(round((time.perf_counter() - start) * 1000))
        return model, "loaded", None, elapsed
    except Exception as exc:  # noqa: BLE001
        elapsed = int(round((time.perf_counter() - start) * 1000))
        status = "failed" if allow_download else "skipped"
        return model_name, status, str(exc)[:500], elapsed


def _transcribe_sample(
    model: Any,
    model_name: str,
    sample: dict[str, Any],
    model_load_ms: int,
) -> dict[str, Any]:
    correct_transcript_text, restore_transcript_punctuation = _load_stt_helpers()
    sample_path = Path(sample["path"])
    duration_ms = _audio_duration_ms(sample_path)

    start = time.perf_counter()
    try:
        segments, info = model.transcribe(
            str(sample_path),
            language="zh",
            task="transcribe",
            vad_filter=False,
        )
        raw = "".join((getattr(segment, "text", "") or "") for segment in segments).strip()
        latency_ms = int(round((time.perf_counter() - start) * 1000))

        correction = correct_transcript_text(raw)
        punctuation = restore_transcript_punctuation(correction["correctedTranscript"])
        final = punctuation["finalTranscript"]
        char_distance, reference_chars, cer = _cer(sample["reference"], final)
        raw_distance, raw_reference_chars, raw_cer = _cer(sample["reference"], raw)

        return {
            "sampleId": sample["id"],
            "samplePath": str(sample_path),
            "sourceType": sample["sourceType"],
            "provider": "faster-whisper-local",
            "model": model_name,
            "status": "ok" if final else "empty",
            "rawTranscript": raw,
            "correctedTranscript": correction["correctedTranscript"],
            "punctuatedTranscript": punctuation["punctuatedTranscript"],
            "finalTranscript": final,
            "reference": sample["reference"],
            "charDistance": char_distance,
            "referenceChars": reference_chars,
            "charErrorRate": cer,
            "rawCharDistance": raw_distance,
            "rawReferenceChars": raw_reference_chars,
            "rawCharErrorRate": raw_cer,
            "cerNormalization": "strip whitespace and common punctuation",
            "latencyMs": latency_ms,
            "modelLoadMs": model_load_ms,
            "audioDurationMs": duration_ms,
            "realTimeFactor": (latency_ms / duration_ms) if duration_ms else None,
            "repeatedTokenWarning": _has_repeated_token_warning(raw),
            "emptyTranscriptWarning": not bool(final),
            "detectedLanguage": getattr(info, "language", None),
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        latency_ms = int(round((time.perf_counter() - start) * 1000))
        return {
            "sampleId": sample["id"],
            "samplePath": str(sample_path),
            "sourceType": sample["sourceType"],
            "provider": "faster-whisper-local",
            "model": model_name,
            "status": "failed",
            "rawTranscript": "",
            "correctedTranscript": "",
            "punctuatedTranscript": "",
            "finalTranscript": "",
            "reference": sample["reference"],
            "charDistance": None,
            "referenceChars": len(_normalize_for_cer(sample["reference"])),
            "charErrorRate": None,
            "rawCharDistance": None,
            "rawReferenceChars": len(_normalize_for_cer(sample["reference"])),
            "rawCharErrorRate": None,
            "cerNormalization": "strip whitespace and common punctuation",
            "latencyMs": latency_ms,
            "modelLoadMs": model_load_ms,
            "audioDurationMs": duration_ms,
            "realTimeFactor": None,
            "repeatedTokenWarning": False,
            "emptyTranscriptWarning": True,
            "detectedLanguage": None,
            "error": str(exc)[:500],
        }


def _skipped_result(
    model_name: str,
    sample: dict[str, Any],
    status: str,
    error: str | None,
    model_load_ms: int,
) -> dict[str, Any]:
    duration_ms = _audio_duration_ms(Path(sample["path"]))
    return {
        "sampleId": sample["id"],
        "samplePath": sample["path"],
        "sourceType": sample["sourceType"],
        "provider": "faster-whisper-local",
        "model": model_name,
        "status": status,
        "rawTranscript": "",
        "correctedTranscript": "",
        "punctuatedTranscript": "",
        "finalTranscript": "",
        "reference": sample["reference"],
        "charDistance": None,
        "referenceChars": len(_normalize_for_cer(sample["reference"])),
        "charErrorRate": None,
        "rawCharDistance": None,
        "rawReferenceChars": len(_normalize_for_cer(sample["reference"])),
        "rawCharErrorRate": None,
        "cerNormalization": "strip whitespace and common punctuation",
        "latencyMs": None,
        "modelLoadMs": model_load_ms,
        "audioDurationMs": duration_ms,
        "realTimeFactor": None,
        "repeatedTokenWarning": False,
        "emptyTranscriptWarning": True,
        "detectedLanguage": None,
        "error": error,
    }


def _average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_model: dict[str, Any] = {}
    by_source: dict[str, Any] = {}
    for result in results:
        if result["status"] != "ok" or result["charErrorRate"] is None:
            continue
        model = result["model"]
        source_type = result["sourceType"]
        by_model.setdefault(model, []).append(result["charErrorRate"])
        by_source.setdefault(model, {}).setdefault(source_type, []).append(result["charErrorRate"])

    model_summary = {
        model: {
            "avgCharErrorRate": _average(values),
            "okCount": len(values),
        }
        for model, values in sorted(by_model.items())
    }
    source_summary = {
        model: {
            source_type: {
                "avgCharErrorRate": _average(values),
                "okCount": len(values),
            }
            for source_type, values in sorted(source_map.items())
        }
        for model, source_map in sorted(by_source.items())
    }
    return {
        "byModel": model_summary,
        "byModelAndSourceType": source_summary,
        "diagnosis": _build_diagnosis(source_summary),
    }


def _build_diagnosis(source_summary: dict[str, Any]) -> list[dict[str, str]]:
    diagnosis: list[dict[str, str]] = []
    for model, source_map in source_summary.items():
        clean = source_map.get("external_clean_reference", {}).get("avgCharErrorRate")
        manual = source_map.get("manual_mic", {}).get("avgCharErrorRate")
        conversation = source_map.get("conversation_mode", {}).get("avgCharErrorRate")

        if clean is not None and clean >= 0.5:
            diagnosis.append(
                {
                    "model": model,
                    "signal": "clean_audio_bad_transcript",
                    "interpretation": "Model issue suspected for this sample set.",
                }
            )
        if manual is not None and conversation is not None:
            if manual <= 0.35 and conversation >= manual + 0.2:
                interpretation = "Conversation Mode capture/VAD issue suspected."
            elif manual >= 0.5 and conversation >= 0.5:
                interpretation = "Model/capture combination issue suspected."
            else:
                interpretation = "No strong capture-vs-model split from current samples."
            diagnosis.append(
                {
                    "model": model,
                    "signal": "manual_mic_vs_conversation_mode",
                    "interpretation": interpretation,
                }
            )
    return diagnosis


def _select_models(args: argparse.Namespace) -> list[str]:
    models = args.model or list(DEFAULT_MODELS)
    if args.include_medium and "medium" not in models:
        models.append("medium")
    unknown = [model for model in models if model not in ALLOWED_MODELS]
    if unknown:
        raise ValueError(
            f"Unsupported model(s): {', '.join(unknown)}. "
            f"Allowed: {', '.join(ALLOWED_MODELS)}."
        )
    return models


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare local faster-whisper Chinese STT quality against WAV references.",
    )
    parser.add_argument("--manifest", help="JSON list or object with samples[].")
    parser.add_argument("--sample", action="append", help="WAV sample path. Repeat with --reference.")
    parser.add_argument("--reference", action="append", help="Reference transcript for the matching --sample.")
    parser.add_argument(
        "--source-type",
        action="append",
        choices=sorted(ALLOWED_SOURCE_TYPES),
        help="Source type for the matching --sample. Default: external_clean_reference.",
    )
    parser.add_argument("--notes", action="append", help="Optional notes for the matching --sample.")
    parser.add_argument(
        "--model",
        action="append",
        choices=ALLOWED_MODELS,
        help="Model to test. Repeat to override default tiny/base/small.",
    )
    parser.add_argument("--include-medium", action="store_true", help="Also test faster-whisper medium.")
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Allow faster-whisper to download missing models. Default is local cache only.",
    )
    parser.add_argument("--output", help="Write JSON report to this path instead of stdout.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        samples = _samples_from_args(args)
        models = _select_models(args)
        for sample in samples:
            path = Path(sample["path"])
            if not path.is_file():
                raise ValueError(f"Sample file does not exist: {path}")
    except Exception as exc:  # noqa: BLE001
        parser.error(str(exc))

    results: list[dict[str, Any]] = []
    for model_name in models:
        model, status, error, model_load_ms = _load_whisper_model(model_name, args.allow_download)
        if status != "loaded":
            for sample in samples:
                results.append(_skipped_result(model_name, sample, status, error, model_load_ms))
            continue
        for sample in samples:
            results.append(_transcribe_sample(model, model_name, sample, model_load_ms))

    report = {
        "task": "TASK-STT-002",
        "provider": "faster-whisper-local",
        "models": models,
        "allowDownload": bool(args.allow_download),
        "sampleCount": len(samples),
        "samples": samples,
        "results": results,
        "summary": _build_summary(results),
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + os.linesep, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
