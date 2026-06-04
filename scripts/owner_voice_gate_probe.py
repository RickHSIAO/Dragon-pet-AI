"""TASK-259/262 owner voice gate offline speaker embedding probe.

TASK-259: Single-pair embedding probe (--enroll-a, --verify-a, --verify-b).
TASK-262: Multi-sample calibration probe with centroid, self-scores, other-scores,
          score gap, and threshold suggestions (--owner-sample, --other-sample,
          --owner-dir, --other-dir, --output-json).

This script is intentionally not connected to Dragon Pet AI runtime. It accepts
existing WAV file paths only, writes a clean JSON report to stdout, and never
opens a microphone or persists raw audio / embeddings.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import platform
import sys
import time
import wave
from pathlib import Path
from typing import Any


PROVIDER_FUNASR_CAMPP = "funasr-campp"
DEFAULT_THRESHOLD = 0.65
DEFAULT_FUNASR_CAMPP_MODEL_ID = "iic/speech_campplus_sv_zh-cn_16k-common"
FALLBACK_FUNASR_CAMPP_MODEL_ID = "damo/speech_campplus_sv_zh-cn_16k-common"
REQUIRED_SAMPLE_RATE = 16000
THRESHOLD_MIN = 0.40
THRESHOLD_MAX = 0.95


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _clean_error(exc: BaseException) -> str:
    text = str(exc).replace("\r", " ").replace("\n", " ").strip()
    if not text:
        text = exc.__class__.__name__
    return text[:240]


def _base_report(provider: str) -> dict[str, Any]:
    torch_available = _module_available("torch")
    torch_version = None
    cuda_available = False
    if torch_available:
        try:
            import torch  # type: ignore

            torch_version = getattr(torch, "__version__", None)
            cuda_available = bool(torch.cuda.is_available())
        except Exception:
            torch_available = False

    return {
        "status": "unavailable",
        "reason": "not_run",
        "provider": provider,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "torchAvailable": torch_available,
        "torchVersion": torch_version,
        "cudaAvailable": cuda_available,
        "funasrAvailable": _module_available("funasr"),
        "modelscopeAvailable": _module_available("modelscope"),
        "numpyAvailable": _module_available("numpy"),
        "soundfileAvailable": _module_available("soundfile"),
        "modelLoaded": False,
        "modelLoadAttempted": False,
        "modelId": None,
        "embeddingDim": None,
        # Legacy single-pair fields (TASK-259, kept for backwards compat)
        "ownerScore": None,
        "otherScore": None,
        # Multi-sample calibration fields (TASK-262)
        "ownerSampleCount": 0,
        "otherSampleCount": 0,
        "ownerSelfScores": None,
        "otherScores": None,
        "ownerStats": None,
        "otherStats": None,
        "scoreGap": None,
        "thresholdSuggestion": DEFAULT_THRESHOLD,
        "balancedThreshold": None,
        "conservativeThreshold": None,
        "permissiveThreshold": None,
        "separationQuality": None,
        # Safety fields
        "rawAudioPersisted": False,
        "embeddingPersisted": False,
        "micAccessed": False,
        "runtimeIntegrated": False,
        "audioPathsProvided": False,
        "checkedAudioFiles": [],
        "message": "",
    }


def _path_arg(value: str | None) -> Path | None:
    if value is None:
        return None
    return Path(value).expanduser().resolve()


def _inspect_wav(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "path": str(path),
        "exists": path.is_file(),
        "format": "unknown",
        "sampleRate": None,
        "channels": None,
        "sampleWidthBytes": None,
        "frames": None,
        "durationSeconds": None,
        "valid16kPcmWav": False,
    }
    if not path.is_file():
        info["error"] = "file_not_found"
        return info
    try:
        with wave.open(str(path), "rb") as wav:
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            frame_rate = wav.getframerate()
            frames = wav.getnframes()
        info.update(
            {
                "format": "wav",
                "sampleRate": frame_rate,
                "channels": channels,
                "sampleWidthBytes": sample_width,
                "frames": frames,
                "durationSeconds": round(frames / frame_rate, 3) if frame_rate else None,
                "valid16kPcmWav": (
                    frame_rate == REQUIRED_SAMPLE_RATE
                    and channels == 1
                    and sample_width in (2, 4)
                ),
            }
        )
    except wave.Error as exc:
        info["error"] = f"invalid_wav:{_clean_error(exc)}"
    except OSError as exc:
        info["error"] = f"read_error:{_clean_error(exc)}"
    return info


def _validate_audio(paths: list[Path]) -> tuple[bool, list[dict[str, Any]], str | None]:
    inspected = [_inspect_wav(path) for path in paths]
    for item in inspected:
        if not item["exists"]:
            return False, inspected, "audio_file_not_found"
        if item.get("format") != "wav":
            return False, inspected, "audio_not_wav"
        if not item.get("valid16kPcmWav"):
            return False, inspected, "audio_not_16k_pcm_wav"
    return True, inspected, None


def _to_vector(value: Any) -> Any:
    import numpy as np  # type: ignore

    try:
        import torch  # type: ignore

        if isinstance(value, torch.Tensor):
            value = value.detach().cpu().numpy()
    except Exception:
        pass

    arr = np.asarray(value, dtype="float32")
    if arr.ndim == 0:
        raise ValueError("embedding_is_scalar")
    arr = arr.reshape(-1)
    if arr.size == 0:
        raise ValueError("embedding_is_empty")
    norm = float(np.linalg.norm(arr))
    if norm <= 0:
        raise ValueError("embedding_zero_norm")
    return arr / norm


def _find_embedding(value: Any) -> Any | None:
    keys = {
        "spk_embedding",
        "speaker_embedding",
        "embedding",
        "emb",
        "embs",
        "xvector",
        "vector",
    }
    if value is None:
        return None
    if hasattr(value, "shape"):
        return value
    if isinstance(value, dict):
        for key in keys:
            if key in value:
                candidate = value[key]
                if key == "embs" and isinstance(candidate, (list, tuple)) and candidate:
                    return candidate[0]
                return candidate
        for child in value.values():
            found = _find_embedding(child)
            if found is not None:
                return found
    if isinstance(value, (list, tuple)):
        for child in value:
            found = _find_embedding(child)
            if found is not None:
                return found
    return None


def _extract_embedding(model: Any, path: Path) -> Any:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        result = model.generate(input=str(path))
    embedding = _find_embedding(result)
    if embedding is None:
        raise RuntimeError("model_output_missing_embedding")
    return _to_vector(embedding)


def _cosine(a: Any, b: Any) -> float:
    import numpy as np  # type: ignore

    return round(float(np.dot(a, b)), 4)


def _load_funasr_model(model_id: str, allow_download: bool, device: str) -> Any:
    from funasr import AutoModel  # type: ignore

    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return AutoModel(model=model_id, device=device, disable_update=not allow_download)


def _clamp_threshold(value: float) -> float:
    return round(max(THRESHOLD_MIN, min(THRESHOLD_MAX, value)), 4)


def _percentile(scores: list[float], pct: float) -> float:
    if not scores:
        return 0.0
    sorted_s = sorted(scores)
    idx = (pct / 100.0) * (len(sorted_s) - 1)
    lo = int(idx)
    hi = lo + 1
    if hi >= len(sorted_s):
        return round(sorted_s[-1], 4)
    frac = idx - lo
    return round(sorted_s[lo] + frac * (sorted_s[hi] - sorted_s[lo]), 4)


def _compute_centroid(embeddings: list) -> Any:
    import numpy as np  # type: ignore

    centroid = np.mean(np.stack(embeddings), axis=0).astype("float32")
    norm = float(np.linalg.norm(centroid))
    if norm <= 0:
        raise ValueError("centroid_zero_norm")
    return centroid / norm


def _owner_stats(scores: list[float]) -> dict[str, float]:
    if not scores:
        return {}
    return {
        "mean": round(sum(scores) / len(scores), 4),
        "min": round(min(scores), 4),
        "max": round(max(scores), 4),
        "p10": _percentile(scores, 10),
        "p90": _percentile(scores, 90),
    }


def _other_stats(scores: list[float]) -> dict[str, float]:
    if not scores:
        return {}
    return {
        "mean": round(sum(scores) / len(scores), 4),
        "max": round(max(scores), 4),
        "p90": _percentile(scores, 90),
    }


def _compute_calibration_thresholds(
    owner_scores: list[float],
    other_scores: list[float],
    default_threshold: float,
) -> dict[str, Any]:
    """Return threshold suggestions clamped to [THRESHOLD_MIN, THRESHOLD_MAX].

    If other_scores are provided, midpoint-based calibration is used.
    If only owner_scores are available, a conservative fallback from ownerMin is used.
    Thresholds are local calibration hints only — not universal truths.
    """
    if not owner_scores:
        return {
            "scoreGap": None,
            "thresholdSuggestion": default_threshold,
            "balancedThreshold": None,
            "conservativeThreshold": None,
            "permissiveThreshold": None,
            "separationQuality": None,
        }

    owner_min = min(owner_scores)

    if other_scores:
        other_max = max(other_scores)
        gap = round(owner_min - other_max, 4)
        midpoint = (owner_min + other_max) / 2.0
        # Conservative: 60% of the way from midpoint toward ownerMin
        conservative = _clamp_threshold(midpoint + (owner_min - midpoint) * 0.6)
        balanced = _clamp_threshold(midpoint)
        # Permissive: 60% of the way from midpoint toward otherMax
        permissive = _clamp_threshold(midpoint - (midpoint - other_max) * 0.6)

        if gap <= 0:
            quality = "overlap"
        elif gap < 0.15:
            quality = "weak"
        elif gap < 0.35:
            quality = "moderate"
        else:
            quality = "strong"
    else:
        # No other samples: owner-only conservative fallback
        gap = None
        # Conservative anchor: 85% of ownerMin; clamped to [THRESHOLD_MIN, THRESHOLD_MAX]
        conservative = _clamp_threshold(owner_min * 0.85)
        balanced = _clamp_threshold(owner_min * 0.90)
        permissive = _clamp_threshold(owner_min * 0.95)
        quality = "owner_only"

    return {
        "scoreGap": gap,
        "thresholdSuggestion": balanced,
        "balancedThreshold": balanced,
        "conservativeThreshold": conservative,
        "permissiveThreshold": permissive,
        "separationQuality": quality,
    }


def _collect_wav_paths(
    single_paths: list[Path | None],
    multi_args: list[str] | None,
    dir_arg: str | None,
) -> list[Path]:
    """Collect unique WAV paths from single args, repeated args, and a directory."""
    seen: set[Path] = set()
    result: list[Path] = []
    for p in single_paths:
        if p is not None and p not in seen:
            seen.add(p)
            result.append(p)
    for raw in multi_args or []:
        p = _path_arg(raw)
        if p is not None and p not in seen:
            seen.add(p)
            result.append(p)
    if dir_arg:
        d = Path(dir_arg).expanduser().resolve()
        if d.is_dir():
            for f in sorted(d.glob("*.wav")):
                if f not in seen:
                    seen.add(f)
                    result.append(f)
    return result


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    report = _base_report(args.model)
    report["thresholdSuggestion"] = args.threshold

    if args.model != PROVIDER_FUNASR_CAMPP:
        report.update(
            {
                "status": "unavailable",
                "reason": "unsupported_provider",
                "message": f"Unsupported provider: {args.model}",
            }
        )
        return report

    missing = [
        name
        for name, present in (
            ("torch", report["torchAvailable"]),
            ("funasr", report["funasrAvailable"]),
            ("modelscope", report["modelscopeAvailable"]),
            ("numpy", report["numpyAvailable"]),
        )
        if not present
    ]
    if missing:
        report.update(
            {
                "status": "unavailable",
                "reason": "missing_dependency",
                "message": "Missing dependency: " + ", ".join(missing),
            }
        )
        return report

    if args.check_only and not args.load_model:
        report.update(
            {
                "status": "ok",
                "reason": "dependency_check_only",
                "message": "Dependency check only; no model load or audio embedding attempted.",
            }
        )
        return report

    # --- Collect audio paths ---
    owner_paths = _collect_wav_paths(
        [_path_arg(args.enroll_a), _path_arg(args.verify_a)],
        getattr(args, "owner_samples", None),
        getattr(args, "owner_dir", None),
    )
    other_paths = _collect_wav_paths(
        [_path_arg(args.verify_b)],
        getattr(args, "other_samples", None),
        getattr(args, "other_dir", None),
    )
    all_audio_paths = owner_paths + other_paths

    report["audioPathsProvided"] = bool(all_audio_paths)
    report["ownerSampleCount"] = len(owner_paths)
    report["otherSampleCount"] = len(other_paths)

    if all_audio_paths:
        valid, inspected, reason = _validate_audio(all_audio_paths)
        report["checkedAudioFiles"] = inspected
        if not valid:
            report.update(
                {
                    "status": "unavailable",
                    "reason": reason,
                    "message": "Audio probe requires existing mono 16 kHz PCM WAV files.",
                }
            )
            return report

    should_load_model = args.load_model or bool(all_audio_paths)
    if not should_load_model:
        report.update(
            {
                "status": "ok",
                "reason": "dependency_check_only",
                "message": "Dependency check only; no model load or audio embedding attempted.",
            }
        )
        return report

    model_ids = [args.model_id or DEFAULT_FUNASR_CAMPP_MODEL_ID]
    if not args.model_id and FALLBACK_FUNASR_CAMPP_MODEL_ID not in model_ids:
        model_ids.append(FALLBACK_FUNASR_CAMPP_MODEL_ID)

    model = None
    load_errors: list[str] = []
    start = time.perf_counter()
    report["modelLoadAttempted"] = True
    for model_id in model_ids:
        try:
            model = _load_funasr_model(model_id, args.allow_download, args.device)
            report["modelLoaded"] = True
            report["modelId"] = model_id
            report["modelLoadSeconds"] = round(time.perf_counter() - start, 3)
            break
        except Exception as exc:
            load_errors.append(f"{model_id}: {_clean_error(exc)}")

    if model is None:
        report.update(
            {
                "status": "unavailable",
                "reason": "missing_model",
                "message": (
                    "Could not load FunASR CAM++ locally. "
                    "Use --allow-download only for an explicit model download probe. "
                    + " | ".join(load_errors)[:360]
                ),
            }
        )
        return report

    if not all_audio_paths:
        report.update(
            {
                "status": "ok",
                "reason": "model_load_only",
                "message": "Model loaded; no audio paths supplied, so embeddings were not extracted.",
            }
        )
        return report

    if not owner_paths:
        report.update(
            {
                "status": "unavailable",
                "reason": "missing_owner_audio",
                "message": (
                    "At least one owner sample is required "
                    "(--owner-sample PATH or --enroll-a + --verify-a)."
                ),
            }
        )
        return report

    try:
        # Extract all embeddings — kept in memory only, never written to disk
        owner_embeddings = [_extract_embedding(model, p) for p in owner_paths]
        other_embeddings = [_extract_embedding(model, p) for p in other_paths]

        report["embeddingDim"] = int(owner_embeddings[0].shape[0])

        # Compute owner centroid (normalized mean of all owner embeddings)
        centroid = _compute_centroid(owner_embeddings)

        # ownerSelfScores: centroid vs each owner sample (represents runtime acceptance scores)
        owner_self_scores = [_cosine(centroid, e) for e in owner_embeddings]
        # otherScores: centroid vs each other-speaker sample
        other_scores_list = [_cosine(centroid, e) for e in other_embeddings]

        # Legacy backwards-compat: set ownerScore for single-pair mode (TASK-259 format)
        is_legacy_enroll_verify = (
            _path_arg(args.enroll_a) is not None
            and _path_arg(args.verify_a) is not None
            and not getattr(args, "owner_samples", None)
            and not getattr(args, "owner_dir", None)
        )
        if is_legacy_enroll_verify and len(owner_embeddings) == 2:
            report["ownerScore"] = _cosine(owner_embeddings[0], owner_embeddings[1])

        is_legacy_verify_b = (
            _path_arg(args.verify_b) is not None
            and not getattr(args, "other_samples", None)
            and not getattr(args, "other_dir", None)
        )
        if is_legacy_verify_b and other_scores_list:
            report["otherScore"] = other_scores_list[0]

        # Compute stats and threshold suggestions
        o_stats = _owner_stats(owner_self_scores)
        n_stats = _other_stats(other_scores_list)
        thresh_info = _compute_calibration_thresholds(
            owner_self_scores, other_scores_list, args.threshold
        )

        report.update(
            {
                "ownerSelfScores": owner_self_scores if owner_self_scores else None,
                "otherScores": other_scores_list if other_scores_list else None,
                "ownerStats": o_stats if o_stats else None,
                "otherStats": n_stats if n_stats else None,
                **thresh_info,
                "status": "ok",
                "reason": "calibration_probe_complete",
                "message": (
                    "Calibration probe completed without persisting raw audio or embeddings. "
                    "Thresholds are local calibration hints only."
                ),
            }
        )
        return report
    except Exception as exc:
        report.update(
            {
                "status": "unavailable",
                "reason": "embedding_failed",
                "message": _clean_error(exc),
            }
        )
        return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Offline owner voice gate speaker embedding probe. "
            "Accepts existing WAV paths only; never records or stores raw audio. "
            "TASK-262: multi-sample calibration via --owner-sample, --other-sample, "
            "--owner-dir, --other-dir, --output-json."
        )
    )
    # --- Legacy single-pair args (TASK-259, kept for backwards compat) ---
    parser.add_argument("--enroll-a", help="Path to owner enrollment/reference WAV.")
    parser.add_argument("--verify-a", help="Path to same-owner verification WAV.")
    parser.add_argument("--verify-b", help="Optional path to other-speaker verification WAV.")
    # --- Multi-sample calibration args (TASK-262) ---
    parser.add_argument(
        "--owner-sample",
        action="append",
        dest="owner_samples",
        metavar="PATH",
        help="Owner WAV sample path. May be repeated for multi-sample calibration.",
    )
    parser.add_argument(
        "--other-sample",
        action="append",
        dest="other_samples",
        metavar="PATH",
        help="Other-speaker WAV sample path. May be repeated.",
    )
    parser.add_argument(
        "--owner-dir",
        metavar="DIR",
        help="Directory of owner WAV samples (all *.wav files in the directory).",
    )
    parser.add_argument(
        "--other-dir",
        metavar="DIR",
        help="Directory of other-speaker WAV samples (all *.wav files).",
    )
    parser.add_argument(
        "--output-json",
        metavar="PATH",
        help=(
            "Optional path to write the calibration report JSON. "
            "Never includes raw audio or full embedding vectors."
        ),
    )
    # --- Model / mode args ---
    parser.add_argument(
        "--model",
        default=PROVIDER_FUNASR_CAMPP,
        choices=[PROVIDER_FUNASR_CAMPP],
        help="Speaker embedding provider to probe.",
    )
    parser.add_argument(
        "--model-id",
        help=(
            "Optional FunASR/ModelScope model id. Defaults to "
            f"{DEFAULT_FUNASR_CAMPP_MODEL_ID}."
        ),
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run dependency checks only unless --load-model is also supplied.",
    )
    parser.add_argument(
        "--load-model",
        action="store_true",
        help="Attempt local model load even when no audio paths are supplied.",
    )
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Allow model download/update during model load. Default is local-cache only.",
    )
    parser.add_argument("--device", default="cpu", help="Model device, default: cpu.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=(
            "Reference threshold hint reported in JSON when no audio is provided. "
            "Multi-sample calibration computes its own balanced/conservative/permissive "
            "suggestions and overrides this value in the thresholdSuggestion field."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # With no audio arguments, default behavior is the same as --check-only.
    if args.check_only:
        args.load_model = bool(args.load_model)
    report = run_probe(args)
    output = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    print(output)
    output_json_path = getattr(args, "output_json", None)
    if output_json_path:
        out_path = Path(output_json_path).expanduser().resolve()
        out_path.write_text(output, encoding="utf-8")
    return 0 if report.get("status") in ("ok", "unavailable") else 1


if __name__ == "__main__":
    raise SystemExit(main())
