"""
Owner Voice Gate local storage stub.

TASK-261 adds a backend-owned settings stub only. It does not enroll, record,
load speaker models, call STT, call chat, or store real voiceprints.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
import json
import logging
import os
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


@dataclass
class OwnerVoiceGateSettings:
    schemaVersion: int = 1
    enabled: bool = False
    enrolled: bool = False
    provider: str = OWNER_VOICE_PROVIDER
    modelId: str = OWNER_VOICE_MODEL_ID
    embeddingDim: int = OWNER_VOICE_EMBEDDING_DIM
    embeddingAggregate: None = None
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
) -> dict[str, Any]:
    data = asdict(settings)
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

    # TASK-261 is a storage stub only: real enrollment data is not accepted.
    settings.enabled = False
    settings.enrolled = False
    settings.sampleCount = 0
    settings.embeddingAggregate = None
    settings.provider = OWNER_VOICE_PROVIDER
    settings.modelId = OWNER_VOICE_MODEL_ID
    settings.embeddingDim = OWNER_VOICE_EMBEDDING_DIM
    settings.calibrationStats = OwnerVoiceCalibrationStats()
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
    # Stub safety: never persist real owner voice vectors in TASK-261.
    data["enabled"] = bool(settings.enabled and settings.enrolled)
    data["enrolled"] = False
    data["embeddingAggregate"] = None
    data["sampleCount"] = 0
    data["calibrationStats"] = asdict(OwnerVoiceCalibrationStats())
    data["provider"] = OWNER_VOICE_PROVIDER
    data["modelId"] = OWNER_VOICE_MODEL_ID
    data["embeddingDim"] = OWNER_VOICE_EMBEDDING_DIM

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)


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

            # TASK-261 never promotes the placeholder into a real voiceprint.
            self._settings.enrolled = False
            self._settings.embeddingAggregate = None
            self._settings.sampleCount = 0
            self._settings.updatedAt = now

            settings = deepcopy(self._settings)
        _save_settings_to_file(self._file_path, settings)
        return _serialize_settings(settings, reason=reason)

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
