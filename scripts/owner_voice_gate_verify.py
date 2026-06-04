"""TASK-264 owner voice verification probe against stored centroid.

This script runs in .venv-funasr Python 3.10. It reads the backend-owned
Owner Voice Gate settings JSON, loads the stored centroid, scores existing WAV
file paths against it, and prints a clean JSON report.

Safety boundaries:
- no microphone access
- no recording
- no raw audio persistence
- no transcript or waveform output
- no candidate embedding persistence
- no runtime integration
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import logging
import math
import platform
import sys
import time
import wave
from pathlib import Path
from typing import Any


PROVIDER_FUNASR_CAMPP = "funasr-campp"
DEFAULT_FUNASR_CAMPP_MODEL_ID = "iic/speech_campplus_sv_zh-cn_16k-common"
FALLBACK_FUNASR_CAMPP_MODEL_ID = "damo/speech_campplus_sv_zh-cn_16k-common"
DEFAULT_THRESHOLD = 0.65
THRESHOLD_MIN = 0.40
THRESHOLD_MAX = 0.95
REQUIRED_SAMPLE_RATE = 16000
REQUIRED_EMBEDDING_DIM = 192
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS_JSON = REPO_ROOT / "backend" / "data" / "owner_voice_gate_settings.json"


@contextlib.contextmanager
def _suppress_external_output() -> Any:
    previous_disable_level = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            yield
    finally:
        logging.disable(previous_disable_level)


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _clean_error(exc: BaseException) -> str:
    text = str(exc).replace("\r", " ").replace("\n", " ").strip()
    return (text or exc.__class__.__name__)[:240]


def _clamp_threshold(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = DEFAULT_THRESHOLD
    return round(max(THRESHOLD_MIN, min(THRESHOLD_MAX, parsed)), 4)


def _base_report() -> dict[str, Any]:
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
        "provider": PROVIDER_FUNASR_CAMPP,
        "modelId": None,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "torchAvailable": torch_available,
        "torchVersion": torch_version,
        "cudaAvailable": cuda_available,
        "funasrAvailable": _module_available("funasr"),
        "modelscopeAvailable": _module_available("modelscope"),
        "numpyAvailable": _module_available("numpy"),
        "modelLoaded": False,
        "modelLoadAttempted": False,
        "modelLoadSeconds": None,
        "enrolled": False,
        "score": None,
        "scores": [],
        "threshold": DEFAULT_THRESHOLD,
        "accepted": False,
        "embeddingDim": None,
        "sampleCount": 0,
        "settingsPath": None,
        "checkedAudioFiles": [],
        "rawAudioPersisted": False,
        "transcriptPersisted": False,
        "waveformPersisted": False,
        "base64AudioPersisted": False,
        "candidateEmbeddingPersisted": False,
        "storedCentroidExposed": False,
        "micAccessed": False,
        "runtimeIntegrated": False,
        "message": "",
    }


def _path_arg(value: str) -> Path:
    return Path(value).expanduser()


def _float_list(value: Any) -> list[float]:
    if hasattr(value, "detach"):
        value = value.detach().cpu().numpy()
    if hasattr(value, "reshape") and hasattr(value, "tolist"):
        value = value.reshape(-1).tolist()
    if not isinstance(value, (list, tuple)):
        raise ValueError("invalid_vector")
    return [float(item) for item in value]


def _l2_normalize(values: list[float]) -> list[float]:
    norm = math.sqrt(sum(item * item for item in values))
    if norm <= 0:
        raise ValueError("zero_norm_vector")
    return [item / norm for item in values]


def _validate_centroid(value: Any) -> list[float] | None:
    try:
        values = _float_list(value)
    except (TypeError, ValueError):
        return None
    if len(values) != REQUIRED_EMBEDDING_DIM:
        return None
    try:
        return _l2_normalize(values)
    except ValueError:
        return None


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("vector_dim_mismatch")
    return round(sum(x * y for x, y in zip(a, b, strict=True)), 4)


def _compute_centroid(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        raise ValueError("no_candidate_embeddings")
    dim = len(vectors[0])
    if dim != REQUIRED_EMBEDDING_DIM or any(len(vector) != dim for vector in vectors):
        raise ValueError("unexpected_embedding_dim")
    averaged = [sum(vector[idx] for vector in vectors) / len(vectors) for idx in range(dim)]
    return _l2_normalize(averaged)


def build_verification_decision(
    *,
    stored_centroid: list[float],
    candidate_embeddings: list[Any],
    threshold: float,
) -> dict[str, Any]:
    owner_centroid = _validate_centroid(stored_centroid)
    if owner_centroid is None:
        raise ValueError("invalid_stored_centroid")
    normalized_candidates = [_l2_normalize(_float_list(vector)) for vector in candidate_embeddings]
    candidate_centroid = _compute_centroid(normalized_candidates)
    score = _cosine(owner_centroid, candidate_centroid)
    scores = [_cosine(owner_centroid, vector) for vector in normalized_candidates]
    clamped_threshold = _clamp_threshold(threshold)
    return {
        "score": score,
        "scores": scores,
        "threshold": clamped_threshold,
        "accepted": bool(score >= clamped_threshold),
        "embeddingDim": REQUIRED_EMBEDDING_DIM,
        "sampleCount": len(normalized_candidates),
    }


def _load_settings(settings_path: Path) -> tuple[dict[str, Any] | None, str]:
    if not settings_path.is_file():
        return None, "not_enrolled"
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "invalid_settings_json"
    except OSError:
        return None, "settings_read_error"
    if not isinstance(data, dict):
        return None, "invalid_settings_json"
    if not data.get("enrolled") or _validate_centroid(data.get("embeddingAggregate")) is None:
        return None, "not_enrolled"
    return data, "ok"


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


def _collect_candidate_paths(candidate_samples: list[str] | None, candidate_dir: str | None) -> list[Path]:
    seen: set[str] = set()
    result: list[Path] = []
    for raw in candidate_samples or []:
        text = str(raw).strip()
        if not text:
            continue
        path = _path_arg(text)
        key = str(path)
        if key not in seen:
            seen.add(key)
            result.append(path)
    if candidate_dir:
        directory = _path_arg(candidate_dir)
        if directory.is_dir():
            for path in sorted(directory.glob("*.wav")):
                key = str(path)
                if key not in seen:
                    seen.add(key)
                    result.append(path)
    return result


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


def _extract_embedding(model: Any, path: Path) -> list[float]:
    with _suppress_external_output():
        result = model.generate(input=str(path))
    embedding = _find_embedding(result)
    if embedding is None:
        raise RuntimeError("model_output_missing_embedding")
    values = _float_list(embedding)
    if len(values) != REQUIRED_EMBEDDING_DIM:
        raise ValueError("unexpected_embedding_dim")
    return _l2_normalize(values)


def _load_funasr_model(model_id: str, allow_download: bool, device: str) -> Any:
    with _suppress_external_output():
        from funasr import AutoModel  # type: ignore

        return AutoModel(model=model_id, device=device, disable_update=not allow_download)


def run_verification(args: argparse.Namespace) -> dict[str, Any]:
    report = _base_report()
    settings_path = _path_arg(args.settings_json)
    report["settingsPath"] = str(settings_path)

    settings, settings_reason = _load_settings(settings_path)
    if settings is None:
        report.update(
            {
                "status": "not_enrolled" if settings_reason == "not_enrolled" else "unavailable",
                "reason": settings_reason,
                "message": "Owner Voice Gate is not enrolled." if settings_reason == "not_enrolled" else "Owner Voice Gate settings could not be read.",
            }
        )
        return report

    stored_centroid = _validate_centroid(settings.get("embeddingAggregate"))
    if stored_centroid is None:
        report.update(
            {
                "status": "not_enrolled",
                "reason": "not_enrolled",
                "message": "Owner Voice Gate is not enrolled.",
            }
        )
        return report

    threshold = _clamp_threshold(args.threshold if args.threshold is not None else settings.get("threshold"))
    report.update(
        {
            "enrolled": True,
            "provider": str(settings.get("provider") or PROVIDER_FUNASR_CAMPP),
            "modelId": str(settings.get("modelId") or DEFAULT_FUNASR_CAMPP_MODEL_ID),
            "threshold": threshold,
        }
    )

    candidate_paths = _collect_candidate_paths(args.candidate_samples, args.candidate_dir)
    report["sampleCount"] = len(candidate_paths)
    if not candidate_paths:
        report.update(
            {
                "status": "unavailable",
                "reason": "no_candidate_samples",
                "message": "At least one candidate WAV file path is required.",
            }
        )
        return report

    valid, inspected, reason = _validate_audio(candidate_paths)
    report["checkedAudioFiles"] = inspected
    if not valid:
        report.update(
            {
                "status": "unavailable",
                "reason": reason,
                "message": "Verification requires existing mono 16 kHz PCM WAV files.",
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

    model_ids = [args.model_id or str(settings.get("modelId") or DEFAULT_FUNASR_CAMPP_MODEL_ID)]
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

    try:
        candidate_embeddings = [_extract_embedding(model, path) for path in candidate_paths]
        decision = build_verification_decision(
            stored_centroid=stored_centroid,
            candidate_embeddings=candidate_embeddings,
            threshold=threshold,
        )
        report.update(
            {
                "status": "ok",
                "reason": "verification_complete",
                "score": decision["score"],
                "scores": decision["scores"],
                "threshold": decision["threshold"],
                "accepted": decision["accepted"],
                "embeddingDim": decision["embeddingDim"],
                "sampleCount": decision["sampleCount"],
                "message": "Verification completed against stored centroid. Candidate embeddings were not persisted.",
            }
        )
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
            "Owner Voice Gate verification probe from existing 16 kHz mono PCM WAV files. "
            "Reads a stored centroid and scores candidate files; never records audio."
        )
    )
    parser.add_argument(
        "--settings-json",
        default=str(DEFAULT_SETTINGS_JSON),
        help="Path to backend owner_voice_gate_settings.json.",
    )
    parser.add_argument(
        "--candidate-sample",
        action="append",
        dest="candidate_samples",
        metavar="PATH",
        help="Candidate WAV sample path. Repeat to score an aggregate candidate centroid.",
    )
    parser.add_argument(
        "--candidate-dir",
        metavar="DIR",
        help="Directory of candidate WAV samples (all *.wav files in the directory).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Optional override threshold. Defaults to the threshold in stored settings.",
    )
    parser.add_argument(
        "--model-id",
        help="Optional FunASR/ModelScope model id. Defaults to stored settings model id.",
    )
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Allow model download/update during model load. Default is local-cache only.",
    )
    parser.add_argument("--device", default="cpu", help="Model device, default: cpu.")
    parser.add_argument(
        "--output-json",
        metavar="PATH",
        help="Optional path to write the verification JSON report. The report contains scores only, not embeddings.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    report = run_verification(args)
    output = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    print(output)
    output_path = getattr(args, "output_json", None)
    if output_path:
        Path(output_path).expanduser().write_text(output, encoding="utf-8")
    return 0 if report.get("status") in ("ok", "unavailable", "not_enrolled") else 1


if __name__ == "__main__":
    raise SystemExit(main())
