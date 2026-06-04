"""TASK-259 owner voice gate offline speaker embedding probe.

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
        "ownerScore": None,
        "otherScore": None,
        "thresholdSuggestion": DEFAULT_THRESHOLD,
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

    audio_paths = [
        path
        for path in (
            _path_arg(args.enroll_a),
            _path_arg(args.verify_a),
            _path_arg(args.verify_b),
        )
        if path is not None
    ]
    report["audioPathsProvided"] = bool(audio_paths)

    if audio_paths:
        valid, inspected, reason = _validate_audio(audio_paths)
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

    should_load_model = args.load_model or bool(audio_paths)
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
                "message": "Could not load FunASR CAM++ locally. "
                "Use --allow-download only for an explicit model download probe. "
                + " | ".join(load_errors)[:360],
            }
        )
        return report

    if not audio_paths:
        report.update(
            {
                "status": "ok",
                "reason": "model_load_only",
                "message": "Model loaded; no audio paths supplied, so embeddings were not extracted.",
            }
        )
        return report

    enroll_path = _path_arg(args.enroll_a)
    verify_a_path = _path_arg(args.verify_a)
    verify_b_path = _path_arg(args.verify_b)
    if enroll_path is None or verify_a_path is None:
        report.update(
            {
                "status": "unavailable",
                "reason": "missing_audio_pair",
                "message": "--enroll-a and --verify-a are required for similarity scoring.",
            }
        )
        return report

    try:
        enroll_embedding = _extract_embedding(model, enroll_path)
        verify_a_embedding = _extract_embedding(model, verify_a_path)
        report["embeddingDim"] = int(enroll_embedding.shape[0])
        report["ownerScore"] = _cosine(enroll_embedding, verify_a_embedding)

        if verify_b_path is not None:
            verify_b_embedding = _extract_embedding(model, verify_b_path)
            report["otherScore"] = _cosine(enroll_embedding, verify_b_embedding)

        report.update(
            {
                "status": "ok",
                "reason": "embedding_probe_complete",
                "message": "Embedding probe completed without persisting raw audio or embeddings.",
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
            "Accepts existing WAV paths only; never records or stores raw audio."
        )
    )
    parser.add_argument("--enroll-a", help="Path to owner enrollment/reference WAV.")
    parser.add_argument("--verify-a", help="Path to same-owner verification WAV.")
    parser.add_argument("--verify-b", help="Optional path to other-speaker verification WAV.")
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
        help="Similarity threshold suggestion reported in JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # With no audio arguments, default behavior is the same as --check-only.
    if args.check_only:
        args.load_model = bool(args.load_model)
    report = run_probe(args)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("status") in ("ok", "unavailable") else 1


if __name__ == "__main__":
    raise SystemExit(main())
