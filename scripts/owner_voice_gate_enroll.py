"""TASK-263 owner voice enrollment from existing WAV files.

This script runs in .venv-funasr Python 3.10. It accepts file paths only,
validates 16 kHz mono PCM WAV input, creates a normalized CAM++ speaker
embedding centroid, and prints a JSON report for the backend to consume.

Safety boundaries:
- no microphone access
- no recording
- no raw audio persistence
- no transcript or waveform output
- no per-sample embedding output
- no runtime integration
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
DEFAULT_FUNASR_CAMPP_MODEL_ID = "iic/speech_campplus_sv_zh-cn_16k-common"
FALLBACK_FUNASR_CAMPP_MODEL_ID = "damo/speech_campplus_sv_zh-cn_16k-common"
DEFAULT_THRESHOLD = 0.65
REQUIRED_SAMPLE_RATE = 16000
REQUIRED_EMBEDDING_DIM = 192
MIN_OWNER_SAMPLES = 2
THRESHOLD_MIN = 0.40
THRESHOLD_MAX = 0.95


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _clean_error(exc: BaseException) -> str:
    text = str(exc).replace("\r", " ").replace("\n", " ").strip()
    return (text or exc.__class__.__name__)[:240]


def _clamp_threshold(value: float) -> float:
    return round(max(THRESHOLD_MIN, min(THRESHOLD_MAX, float(value))), 4)


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
        "soundfileAvailable": _module_available("soundfile"),
        "modelLoaded": False,
        "modelLoadAttempted": False,
        "modelLoadSeconds": None,
        "embeddingDim": None,
        "sampleCount": 0,
        "threshold": DEFAULT_THRESHOLD,
        "calibrationStats": {
            "meanSelfScore": None,
            "minSelfScore": None,
            "maxSelfScore": None,
        },
        "embeddingAggregate": None,
        "rawAudioPersisted": False,
        "embeddingPersisted": False,
        "micAccessed": False,
        "runtimeIntegrated": False,
        "checkedAudioFiles": [],
        "message": "",
    }


def _path_arg(value: str) -> Path:
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


def _collect_owner_paths(owner_samples: list[str] | None, owner_dir: str | None) -> list[Path]:
    seen: set[Path] = set()
    result: list[Path] = []
    for raw in owner_samples or []:
        path = _path_arg(raw)
        if path not in seen:
            seen.add(path)
            result.append(path)
    if owner_dir:
        directory = _path_arg(owner_dir)
        if directory.is_dir():
            for path in sorted(directory.glob("*.wav")):
                if path not in seen:
                    seen.add(path)
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


def _to_vector(value: Any) -> Any:
    import numpy as np  # type: ignore

    try:
        import torch  # type: ignore

        if isinstance(value, torch.Tensor):
            value = value.detach().cpu().numpy()
    except Exception:
        pass

    arr = np.asarray(value, dtype="float32").reshape(-1)
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


def _load_funasr_model(model_id: str, allow_download: bool, device: str) -> Any:
    from funasr import AutoModel  # type: ignore

    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return AutoModel(model=model_id, device=device, disable_update=not allow_download)


def _cosine(a: Any, b: Any) -> float:
    import numpy as np  # type: ignore

    return round(float(np.dot(a, b)), 4)


def _compute_centroid(embeddings: list[Any]) -> Any:
    import numpy as np  # type: ignore

    centroid = np.mean(np.stack(embeddings), axis=0).astype("float32")
    norm = float(np.linalg.norm(centroid))
    if norm <= 0:
        raise ValueError("centroid_zero_norm")
    return centroid / norm


def _float_list(vector: Any) -> list[float]:
    values = [round(float(x), 8) for x in vector.tolist()]
    if len(values) != REQUIRED_EMBEDDING_DIM:
        raise ValueError("unexpected_embedding_dim")
    return values


def _self_score_stats(scores: list[float]) -> dict[str, float | None]:
    if not scores:
        return {"meanSelfScore": None, "minSelfScore": None, "maxSelfScore": None}
    return {
        "meanSelfScore": round(sum(scores) / len(scores), 4),
        "minSelfScore": round(min(scores), 4),
        "maxSelfScore": round(max(scores), 4),
    }


def run_enrollment(args: argparse.Namespace) -> dict[str, Any]:
    report = _base_report()
    report["threshold"] = _clamp_threshold(args.threshold)

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

    owner_paths = _collect_owner_paths(args.owner_samples, args.owner_dir)
    report["sampleCount"] = len(owner_paths)
    if len(owner_paths) < MIN_OWNER_SAMPLES:
        report.update(
            {
                "status": "unavailable",
                "reason": "not_enough_owner_samples",
                "message": "At least 2 owner WAV samples are required.",
            }
        )
        return report

    valid, inspected, reason = _validate_audio(owner_paths)
    report["checkedAudioFiles"] = inspected
    if not valid:
        report.update(
            {
                "status": "unavailable",
                "reason": reason,
                "message": "Enrollment requires existing mono 16 kHz PCM WAV files.",
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

    try:
        embeddings = [_extract_embedding(model, path) for path in owner_paths]
        centroid = _compute_centroid(embeddings)
        self_scores = [_cosine(centroid, emb) for emb in embeddings]
        report.update(
            {
                "status": "ok",
                "reason": "owner_enrollment_complete",
                "embeddingDim": int(centroid.shape[0]),
                "embeddingAggregate": _float_list(centroid),
                "calibrationStats": _self_score_stats(self_scores),
                "message": (
                    "Owner voice enrollment completed from existing WAV files. "
                    "No raw audio or per-sample embeddings were persisted."
                ),
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
            "Owner Voice Gate enrollment from existing 16 kHz mono PCM WAV files. "
            "Creates a centroid embedding for backend storage; never records audio."
        )
    )
    parser.add_argument(
        "--owner-sample",
        action="append",
        dest="owner_samples",
        metavar="PATH",
        help="Owner WAV sample path. Repeat at least twice for enrollment.",
    )
    parser.add_argument(
        "--owner-dir",
        metavar="DIR",
        help="Directory of owner WAV samples (all *.wav files in the directory).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="Enrollment threshold to store with the owner voice settings.",
    )
    parser.add_argument(
        "--model-id",
        help=(
            "Optional FunASR/ModelScope model id. Defaults to "
            f"{DEFAULT_FUNASR_CAMPP_MODEL_ID}."
        ),
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
        help=(
            "Optional path to write the enrollment JSON report. "
            "The report includes the centroid embedding and should be treated as sensitive."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    report = run_enrollment(args)
    output_path = getattr(args, "output_json", None)
    if output_path:
        report["embeddingPersisted"] = True
    output = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    print(output)
    if output_path:
        Path(output_path).expanduser().resolve().write_text(output, encoding="utf-8")
    return 0 if report.get("status") in ("ok", "unavailable") else 1


if __name__ == "__main__":
    raise SystemExit(main())
