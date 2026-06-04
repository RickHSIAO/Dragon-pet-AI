"""
Owner Voice Gate local storage.

TASK-261 added a backend-owned settings stub. TASK-263 adds explicit
file-import enrollment from existing WAV paths only. This module never records
audio, stores raw audio, calls STT, calls chat, or opens the microphone.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
import json
import logging
import os
from pathlib import Path
import subprocess
import threading
from typing import Any

_logger = logging.getLogger(__name__)

OWNER_VOICE_GATE_FILE_ENV = "OWNER_VOICE_GATE_FILE_PATH"
DEFAULT_OWNER_VOICE_GATE_FILE_PATH = "data/owner_voice_gate_settings.json"
OWNER_VOICE_PROVIDER = "funasr-campp"
OWNER_VOICE_MODEL_ID = "iic/speech_campplus_sv_zh-cn_16k-common"
OWNER_VOICE_EMBEDDING_DIM = 192
OWNER_VOICE_DEFAULT_THRESHOLD = 0.65
OWNER_VOICE_MIN_THRESHOLD = 0.40
OWNER_VOICE_MAX_THRESHOLD = 0.95
OWNER_VOICE_MIN_ENROLLMENT_SAMPLES = 2
OWNER_VOICE_ENROLLMENT_TIMEOUT_SECONDS = 600
_REPO_ROOT = Path(__file__).resolve().parents[3]
_FUNASR_PYTHON_ENV = "DRAGON_PET_FUNASR_PYTHON"
_FUNASR_PYTHON_DEFAULT = str(_REPO_ROOT / ".venv-funasr" / "Scripts" / "python.exe")
_OWNER_VOICE_ENROLL_SCRIPT = str(_REPO_ROOT / "scripts" / "owner_voice_gate_enroll.py")

_FORBIDDEN_STORAGE_FIELDS = {
    "rawAudio",
    "raw_audio",
    "base64Audio",
    "base64_audio",
    "audio",
    "audioBytes",
    "audio_bytes",
    "transcript",
    "waveform",
    "embeddingAggregate",
    "embedding_aggregate",
    "perSampleEmbeddings",
    "per_sample_embeddings",
}


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _get_default_file_path() -> str:
    raw_value = os.environ.get(OWNER_VOICE_GATE_FILE_ENV)
    if raw_value is None:
        return DEFAULT_OWNER_VOICE_GATE_FILE_PATH
    return raw_value.strip()


def _clamp_threshold(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        parsed = OWNER_VOICE_DEFAULT_THRESHOLD
    parsed = max(OWNER_VOICE_MIN_THRESHOLD, min(OWNER_VOICE_MAX_THRESHOLD, parsed))
    return round(parsed, 3)


@dataclass
class OwnerVoiceCalibrationStats:
    ownerScore: float | None = None
    otherScore: float | None = None
    meanSelfScore: float | None = None
    minSelfScore: float | None = None
    maxSelfScore: float | None = None


@dataclass
class OwnerVoiceGateSettings:
    schemaVersion: int = 1
    enabled: bool = False
    enrolled: bool = False
    provider: str = OWNER_VOICE_PROVIDER
    modelId: str = OWNER_VOICE_MODEL_ID
    embeddingDim: int = OWNER_VOICE_EMBEDDING_DIM
    embeddingAggregate: list[float] | None = None
    sampleCount: int = 0
    threshold: float = OWNER_VOICE_DEFAULT_THRESHOLD
    calibrationStats: OwnerVoiceCalibrationStats = field(default_factory=OwnerVoiceCalibrationStats)
    safetyNoticeAccepted: bool = False
    createdAt: str | None = None
    updatedAt: str | None = None


@dataclass
class OwnerVoiceGateSettingsUpdate:
    enabled: bool | None = None
    threshold: float | None = None
    safetyNoticeAccepted: bool | None = None


def _serialize_settings(
    settings: OwnerVoiceGateSettings,
    *,
    reason: str = "ok",
    message: str | None = None,
    include_embedding: bool = False,
) -> dict[str, Any]:
    data = asdict(settings)
    embedding_persisted = (
        isinstance(settings.embeddingAggregate, list)
        and len(settings.embeddingAggregate) == OWNER_VOICE_EMBEDDING_DIM
    )
    if not include_embedding:
        data["embeddingAggregate"] = None
    data["embeddingPersisted"] = embedding_persisted
    data["storageOwner"] = "backend"
    data["storagePath"] = DEFAULT_OWNER_VOICE_GATE_FILE_PATH
    data["status"] = "enabled" if settings.enabled else ("disabled" if settings.enrolled else "not_enrolled")
    data["reason"] = reason
    data["message"] = message or reason
    return data


def _settings_from_loaded(data: dict[str, Any]) -> OwnerVoiceGateSettings:
    settings = OwnerVoiceGateSettings()
    if "schemaVersion" in data:
        settings.schemaVersion = 1
    if "threshold" in data:
        settings.threshold = _clamp_threshold(data["threshold"])
    if "safetyNoticeAccepted" in data:
        settings.safetyNoticeAccepted = bool(data["safetyNoticeAccepted"])
    if "createdAt" in data and (isinstance(data["createdAt"], str) or data["createdAt"] is None):
        settings.createdAt = data["createdAt"]
    if "updatedAt" in data and (isinstance(data["updatedAt"], str) or data["updatedAt"] is None):
        settings.updatedAt = data["updatedAt"]

    embedding = data.get("embeddingAggregate")
    sample_count = data.get("sampleCount")
    enrolled = bool(data.get("enrolled"))
    if enrolled and _is_valid_embedding_aggregate(embedding):
        settings.enrolled = True
        settings.embeddingAggregate = _normalize_embedding_aggregate(embedding)
        settings.sampleCount = int(sample_count) if isinstance(sample_count, int) else 0
        settings.enabled = bool(data.get("enabled"))
    else:
        settings.enabled = False
        settings.enrolled = False
        settings.sampleCount = 0
        settings.embeddingAggregate = None
    settings.provider = OWNER_VOICE_PROVIDER
    settings.modelId = OWNER_VOICE_MODEL_ID
    settings.embeddingDim = OWNER_VOICE_EMBEDDING_DIM
    stats = data.get("calibrationStats") if isinstance(data.get("calibrationStats"), dict) else {}
    settings.calibrationStats = OwnerVoiceCalibrationStats(
        ownerScore=_optional_float(stats.get("ownerScore")),
        otherScore=_optional_float(stats.get("otherScore")),
        meanSelfScore=_optional_float(stats.get("meanSelfScore")),
        minSelfScore=_optional_float(stats.get("minSelfScore")),
        maxSelfScore=_optional_float(stats.get("maxSelfScore")),
    )
    return settings


def _load_settings_from_file(path: str) -> OwnerVoiceGateSettings | None:
    if not path:
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return None
    except Exception as exc:  # noqa: BLE001
        _logger.warning(
            "owner_voice_gate_storage: could not load settings file %r: %s; using defaults",
            path,
            type(exc).__name__,
        )
        return None
    if not isinstance(data, dict):
        return None
    return _settings_from_loaded(data)


def _save_settings_to_file(path: str, settings: OwnerVoiceGateSettings) -> None:
    if not path:
        return
    data = asdict(settings)
    data["enabled"] = bool(settings.enabled and settings.enrolled)
    data["enrolled"] = bool(settings.enrolled)
    data["embeddingAggregate"] = (
        _normalize_embedding_aggregate(settings.embeddingAggregate)
        if settings.enrolled and _is_valid_embedding_aggregate(settings.embeddingAggregate)
        else None
    )
    data["sampleCount"] = int(settings.sampleCount) if settings.enrolled else 0
    data["provider"] = OWNER_VOICE_PROVIDER
    data["modelId"] = OWNER_VOICE_MODEL_ID
    data["embeddingDim"] = OWNER_VOICE_EMBEDDING_DIM

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return None


def _normalize_embedding_aggregate(value: Any) -> list[float]:
    if not isinstance(value, list):
        raise ValueError("invalid embedding aggregate")
    normalized: list[float] = []
    for item in value:
        normalized.append(round(float(item), 8))
    return normalized


def _is_valid_embedding_aggregate(value: Any) -> bool:
    if not isinstance(value, list) or len(value) != OWNER_VOICE_EMBEDDING_DIM:
        return False
    try:
        _normalize_embedding_aggregate(value)
    except (TypeError, ValueError):
        return False
    return True


def _resolve_funasr_python() -> str:
    from_env = os.environ.get(_FUNASR_PYTHON_ENV, "").strip()
    return from_env if from_env else _FUNASR_PYTHON_DEFAULT


def _prepare_owner_voice_enrollment_paths(paths: list[str]) -> tuple[list[str], str | None]:
    clean_paths: list[str] = []
    for raw_path in paths:
        text = str(raw_path).strip()
        if not text:
            continue
        path = Path(text).expanduser()
        if not path.is_file():
            return [], "audio_file_not_found"
        # Preserve the caller-provided Unicode spelling. On Windows, eager
        # resolve/canonicalization can corrupt non-ASCII user profile paths
        # before the path crosses into the .venv-funasr sidecar.
        clean_paths.append(str(path))
    return clean_paths, None


def _last_json_object(stdout: str) -> dict[str, Any]:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    for idx in range(len(lines)):
        candidate = "\n".join(lines[idx:])
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise ValueError("owner voice enrollment script returned no json")


def run_owner_voice_enrollment_sidecar(paths: list[str], threshold: float) -> dict[str, Any]:
    py_exec = _resolve_funasr_python()
    if not os.path.isfile(py_exec):
        return {
            "status": "unavailable",
            "reason": "missing_funasr_python",
            "message": ".venv-funasr python not found",
        }
    if not os.path.isfile(_OWNER_VOICE_ENROLL_SCRIPT):
        return {
            "status": "unavailable",
            "reason": "missing_enrollment_script",
            "message": "owner voice enrollment script not found",
        }

    cmd = [py_exec, _OWNER_VOICE_ENROLL_SCRIPT, "--threshold", str(_clamp_threshold(threshold))]
    for path in paths:
        cmd.extend(["--owner-sample", path])
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=OWNER_VOICE_ENROLLMENT_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "unavailable",
            "reason": "enrollment_timeout",
            "message": "owner voice enrollment timed out",
        }
    except Exception as exc:  # noqa: BLE001
        _logger.warning("owner_voice_gate_storage: enrollment sidecar failed: %s", type(exc).__name__)
        return {
            "status": "unavailable",
            "reason": "enrollment_sidecar_error",
            "message": "owner voice enrollment sidecar failed",
        }

    try:
        report = _last_json_object(proc.stdout)
    except ValueError:
        return {
            "status": "unavailable",
            "reason": "invalid_enrollment_report",
            "message": "owner voice enrollment report was not valid json",
        }
    if proc.returncode not in (0, None) and report.get("status") != "ok":
        return {
            "status": "unavailable",
            "reason": str(report.get("reason") or "enrollment_failed"),
            "message": str(report.get("message") or "owner voice enrollment failed")[:240],
        }
    return report


class OwnerVoiceGateStorageService:
    def __init__(self, file_path: str | None = None) -> None:
        self._file_path = _get_default_file_path() if file_path is None else file_path
        self._lock = threading.Lock()
        self._settings = _load_settings_from_file(self._file_path) or OwnerVoiceGateSettings()

    def get_status(self, *, reason: str = "ok") -> dict[str, Any]:
        with self._lock:
            settings = deepcopy(self._settings)
        return _serialize_settings(settings, reason=reason)

    def update_settings(self, update: OwnerVoiceGateSettingsUpdate) -> dict[str, Any]:
        reason = "settings_updated"
        with self._lock:
            now = _utc_now_iso()
            if self._settings.createdAt is None:
                self._settings.createdAt = now

            if update.safetyNoticeAccepted is not None:
                self._settings.safetyNoticeAccepted = bool(update.safetyNoticeAccepted)
            if update.threshold is not None:
                self._settings.threshold = _clamp_threshold(update.threshold)
            if update.enabled is not None:
                requested_enabled = bool(update.enabled)
                if requested_enabled and not self._settings.enrolled:
                    self._settings.enabled = False
                    reason = "not_enrolled"
                else:
                    self._settings.enabled = requested_enabled

            if not self._settings.enrolled:
                self._settings.enabled = False
                self._settings.embeddingAggregate = None
                self._settings.sampleCount = 0
            self._settings.updatedAt = now

            settings = deepcopy(self._settings)
        _save_settings_to_file(self._file_path, settings)
        return _serialize_settings(settings, reason=reason)

    def enroll_from_report(
        self,
        *,
        report: dict[str, Any],
        threshold: float,
        safety_notice_accepted: bool,
    ) -> dict[str, Any]:
        embedding = report.get("embeddingAggregate")
        if not _is_valid_embedding_aggregate(embedding):
            raise ValueError("invalid enrollment embedding")
        sample_count = report.get("sampleCount")
        if not isinstance(sample_count, int) or sample_count < OWNER_VOICE_MIN_ENROLLMENT_SAMPLES:
            raise ValueError("not enough owner voice samples")
        stats = report.get("calibrationStats") if isinstance(report.get("calibrationStats"), dict) else {}
        with self._lock:
            now = _utc_now_iso()
            if self._settings.createdAt is None:
                self._settings.createdAt = now
            self._settings.enabled = False
            self._settings.enrolled = True
            self._settings.provider = OWNER_VOICE_PROVIDER
            self._settings.modelId = OWNER_VOICE_MODEL_ID
            self._settings.embeddingDim = OWNER_VOICE_EMBEDDING_DIM
            self._settings.embeddingAggregate = _normalize_embedding_aggregate(embedding)
            self._settings.sampleCount = sample_count
            self._settings.threshold = _clamp_threshold(threshold)
            self._settings.safetyNoticeAccepted = bool(safety_notice_accepted)
            self._settings.calibrationStats = OwnerVoiceCalibrationStats(
                ownerScore=_optional_float(stats.get("ownerScore")),
                otherScore=_optional_float(stats.get("otherScore")),
                meanSelfScore=_optional_float(stats.get("meanSelfScore")),
                minSelfScore=_optional_float(stats.get("minSelfScore")),
                maxSelfScore=_optional_float(stats.get("maxSelfScore")),
            )
            self._settings.updatedAt = now
            settings = deepcopy(self._settings)
        _save_settings_to_file(self._file_path, settings)
        return _serialize_settings(settings, reason="enrolled")

    def delete_voiceprint(self) -> dict[str, Any]:
        with self._lock:
            self._settings = OwnerVoiceGateSettings()
            settings = deepcopy(self._settings)
        if self._file_path:
            try:
                os.remove(self._file_path)
            except FileNotFoundError:
                pass
            except Exception as exc:  # noqa: BLE001
                _logger.warning(
                    "owner_voice_gate_storage: could not delete settings file %r: %s",
                    self._file_path,
                    type(exc).__name__,
                )
        return _serialize_settings(settings, reason="deleted")

    def reset_for_tests(self, file_path: str | None = None) -> None:
        with self._lock:
            if file_path is not None:
                self._file_path = file_path
            self._settings = OwnerVoiceGateSettings()


_service = OwnerVoiceGateStorageService()


def get_owner_voice_gate_status() -> dict[str, Any]:
    return _service.get_status()


def update_owner_voice_gate_settings(update: OwnerVoiceGateSettingsUpdate) -> dict[str, Any]:
    return _service.update_settings(update)


def delete_owner_voice_gate_voiceprint() -> dict[str, Any]:
    return _service.delete_voiceprint()


def reset_owner_voice_gate_storage_for_tests(file_path: str | None = None) -> None:
    _service.reset_for_tests(file_path)


def validate_owner_voice_gate_update_fields(body: dict[str, Any]) -> None:
    unsupported = set(body) - {"enabled", "threshold", "safetyNoticeAccepted"}
    if unsupported:
        raise ValueError("unsupported owner voice gate setting field")
    if set(body) & _FORBIDDEN_STORAGE_FIELDS:
        raise ValueError("unsupported owner voice gate setting field")


def validate_owner_voice_gate_enroll_fields(body: dict[str, Any]) -> None:
    unsupported = set(body) - {"paths", "threshold", "safetyNoticeAccepted"}
    if unsupported:
        raise ValueError("unsupported owner voice enrollment field")
    if set(body) & _FORBIDDEN_STORAGE_FIELDS:
        raise ValueError("unsupported owner voice enrollment field")


def enroll_owner_voice_gate_from_files(
    *,
    paths: list[str],
    threshold: float,
    safety_notice_accepted: bool,
) -> dict[str, Any]:
    if not safety_notice_accepted:
        raise ValueError("safety notice must be accepted before enrollment")
    if len(paths) < OWNER_VOICE_MIN_ENROLLMENT_SAMPLES:
        raise ValueError("at least 2 owner voice samples are required")
    clean_paths, path_error = _prepare_owner_voice_enrollment_paths(paths)
    if len(clean_paths) < OWNER_VOICE_MIN_ENROLLMENT_SAMPLES:
        if path_error == "audio_file_not_found":
            return _serialize_settings(
                OwnerVoiceGateSettings(),
                reason="audio_file_not_found",
                message="Enrollment requires existing mono 16 kHz PCM WAV files.",
            )
        raise ValueError("at least 2 owner voice samples are required")
    report = run_owner_voice_enrollment_sidecar(clean_paths, threshold)
    if report.get("status") != "ok":
        return _serialize_settings(
            OwnerVoiceGateSettings(),
            reason=str(report.get("reason") or "enrollment_unavailable"),
            message=str(report.get("message") or "owner voice enrollment unavailable")[:240],
        )
    return _service.enroll_from_report(
        report=report,
        threshold=threshold,
        safety_notice_accepted=safety_notice_accepted,
    )
