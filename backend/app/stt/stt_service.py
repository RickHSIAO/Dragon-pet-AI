"""
TASK-167B: STT transcription service -- local Whisper, no external API.

Design boundaries:
- Uses faster-whisper (local) when installed; safe no-op fallback if absent.
- No raw audio is persisted to disk.
- No always-listening, wake-word, TTS, screen capture, or vision.
- No external network calls.
- Returns {"transcript": str, "status": "ok" | "unavailable" | "empty" | "error"}.
"""

import io
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_WHISPER_AVAILABLE: bool = False
_whisper_model: Any = None
# TASK-245: STT provider name surfaced in diagnostics
_STT_PROVIDER = "faster-whisper-local"

# TASK-246: configurable model via DRAGON_PET_STT_MODEL env var — safe fallback to "tiny"
_STT_ALLOWED_MODELS = frozenset({"tiny", "base", "small"})
_STT_DEFAULT_MODEL = "tiny"
_STT_MODEL_ENV = "DRAGON_PET_STT_MODEL"


def _resolve_stt_model_name() -> dict:
    """
    Resolve the STT model name from DRAGON_PET_STT_MODEL env var.

    Resolved once at process start — restart the app/backend to pick up env changes.
    Falls back to 'tiny' on invalid or missing value; never crashes.

    Returns dict with keys:
        requested_model  -- raw env value (or default when env is unset)
        resolved_model   -- the model name that will actually be loaded
        model_source     -- "env" | "default" | "fallback"
        fallback_reason  -- "invalid_model" | "none"
    """
    requested = os.environ.get(_STT_MODEL_ENV, "").strip()
    if not requested:
        return {
            "requested_model": _STT_DEFAULT_MODEL,
            "resolved_model": _STT_DEFAULT_MODEL,
            "model_source": "default",
            "fallback_reason": "none",
        }
    if requested in _STT_ALLOWED_MODELS:
        return {
            "requested_model": requested,
            "resolved_model": requested,
            "model_source": "env",
            "fallback_reason": "none",
        }
    logger.warning(
        "TASK-246: invalid %s=%r, falling back to %r. Allowed: %s",
        _STT_MODEL_ENV, requested, _STT_DEFAULT_MODEL,
        ", ".join(sorted(_STT_ALLOWED_MODELS)),
    )
    return {
        "requested_model": requested,
        "resolved_model": _STT_DEFAULT_MODEL,
        "model_source": "fallback",
        "fallback_reason": "invalid_model",
    }


# Resolved at process start — restart required to pick up env changes
_STT_MODEL_RESOLUTION: dict = _resolve_stt_model_name()
_STT_MODEL_NAME: str = _STT_MODEL_RESOLUTION["resolved_model"]


def _detect_whisper() -> bool:
    """Check whether faster-whisper is importable without loading the model."""
    try:
        import faster_whisper  # noqa: F401  # type: ignore
        return True
    except ImportError:
        return False


_WHISPER_AVAILABLE = _detect_whisper()

# Load status — updated by _load_model(); initialized based on availability
_STT_MODEL_LOAD_STATUS: str = "not_loaded" if _WHISPER_AVAILABLE else "unavailable"
_STT_MODEL_LOAD_ERROR: str | None = None


def _load_model() -> Any:
    """
    Lazily load the resolved faster-whisper model on first use.
    Updates _STT_MODEL_LOAD_STATUS and _STT_MODEL_LOAD_ERROR as side-effects.
    Returns None if unavailable or if loading fails.
    """
    global _whisper_model, _STT_MODEL_LOAD_STATUS, _STT_MODEL_LOAD_ERROR
    if _whisper_model is not None:
        return _whisper_model
    if not _WHISPER_AVAILABLE:
        _STT_MODEL_LOAD_STATUS = "unavailable"
        return None
    try:
        from faster_whisper import WhisperModel  # type: ignore
        _whisper_model = WhisperModel(_STT_MODEL_NAME, device="cpu", compute_type="int8")
        _STT_MODEL_LOAD_STATUS = "loaded"
        _STT_MODEL_LOAD_ERROR = None
        logger.info("TASK-246: faster-whisper %r model loaded.", _STT_MODEL_NAME)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "TASK-246: Failed to load faster-whisper model %r: %s", _STT_MODEL_NAME, exc
        )
        _STT_MODEL_LOAD_STATUS = "error"
        _STT_MODEL_LOAD_ERROR = str(exc)[:100]  # truncated — no raw stack trace
        _whisper_model = None
    return _whisper_model


def _get_model_metadata() -> dict:
    """Return current model resolution and load status metadata for diagnostics."""
    return {
        "provider": _STT_PROVIDER,
        "model": _STT_MODEL_NAME,
        "requestedModel": _STT_MODEL_RESOLUTION["requested_model"],
        "resolvedModel": _STT_MODEL_RESOLUTION["resolved_model"],
        "modelSource": _STT_MODEL_RESOLUTION["model_source"],
        "modelLoadStatus": _STT_MODEL_LOAD_STATUS,
        "modelLoadError": _STT_MODEL_LOAD_ERROR,
    }


# TASK-247: STT transcript correction — deterministic phrase/hotword correction map.
# Order matters: longer / more specific phrases first to prevent partial-match shadowing.
# All entries are conservative: only correct well-known acoustic confusions in this project.
_STT_CORRECTION_MAP: list[tuple[str, str]] = [
    # Phrase-level corrections — Whisper acoustic confusions for project vocabulary
    ("中位與英編輯", "中文語音辨識"),
    ("中文語音編輯", "中文語音辨識"),
    ("中文語音邊記", "中文語音辨識"),
    ("語音編輯測試", "語音辨識測試"),
    ("語音邊記測試", "語音辨識測試"),
    # Character name normalization
    ("克里斯蒂娜", "克莉絲蒂娜"),
    ("克莉斯蒂娜", "克莉絲蒂娜"),
    ("克麗絲蒂娜", "克莉絲蒂娜"),
]


def correct_transcript_text(raw_text: str) -> dict:
    """
    Apply deterministic phrase/hotword correction to a raw STT transcript.

    TASK-247 design boundaries:
    - No LLM rewrite.  No cloud API.  No new IPC.
    - Safe, conservative corrections only — known acoustic confusions and project vocabulary.
    - Returns rawTranscript unchanged so callers can surface both original and corrected text
      in diagnostics without losing the raw evidence.
    - Empty input passes through as-is (correctionApplied=False).

    Returns
    -------
    dict with keys:
        rawTranscript        -- original input, unmodified
        correctedTranscript  -- text after applying phrase map (equals rawTranscript if no match)
        correctionApplied    -- True when at least one substitution was made
        correctionMode       -- always "safe_dictionary" for this layer
        correctionReason     -- pipe-separated reason tags ("phrase_map" | "none")
        correctionCandidates -- reserved for future use; always empty list in this task
    """
    if not raw_text:
        return {
            "rawTranscript": "",
            "correctedTranscript": "",
            "correctionApplied": False,
            "correctionMode": "safe_dictionary",
            "correctionReason": "none",
            "correctionCandidates": [],
        }
    corrected = raw_text
    applied_reasons: list[str] = []
    for src, dst in _STT_CORRECTION_MAP:
        if src in corrected:
            corrected = corrected.replace(src, dst)
            if "phrase_map" not in applied_reasons:
                applied_reasons.append("phrase_map")
    applied = corrected != raw_text
    reason_str = "|".join(applied_reasons) if applied_reasons else "none"
    return {
        "rawTranscript": raw_text,
        "correctedTranscript": corrected,
        "correctionApplied": applied,
        "correctionMode": "safe_dictionary",
        "correctionReason": reason_str,
        "correctionCandidates": [],
    }


def _reset_model_for_tests() -> None:
    """Reset the cached model and load status -- only for test isolation. Not for production use."""
    global _whisper_model, _STT_MODEL_LOAD_STATUS, _STT_MODEL_LOAD_ERROR
    _whisper_model = None
    _STT_MODEL_LOAD_STATUS = "not_loaded" if _WHISPER_AVAILABLE else "unavailable"
    _STT_MODEL_LOAD_ERROR = None


def transcribe_audio_bytes(
    audio_bytes: bytes,
    mime_type: str = "audio/webm",
    language: str | None = None,
) -> dict:
    """
    Transcribe raw audio bytes using a local Whisper model.

    Parameters
    ----------
    audio_bytes : bytes
        Raw audio content (any format Whisper supports: webm, wav, ogg, mp4 ...).
    mime_type : str
        MIME type hint -- not used for routing, only for logging.
    language : str | None
        Language hint passed to Whisper (e.g. "zh"). None = auto-detect.

    Returns
    -------
    dict with keys:
        "transcript"    : str   -- transcribed text (empty string on failure/empty audio)
        "status"        : str   -- one of "ok", "unavailable", "empty", "error"

    TASK-246 model metadata (present for ok / unavailable / error, absent for empty-bytes early exit):
        "provider"        : str
        "model"           : str   -- resolved model name
        "requestedModel"  : str
        "resolvedModel"   : str
        "modelSource"     : str   -- "env" | "default" | "fallback"
        "modelLoadStatus" : str   -- "loaded" | "unavailable" | "error" | "not_loaded"
        "modelLoadError"  : str | None  -- short error string, no raw stack

    TASK-247 transcript correction (present for ok only):
        "rawTranscript"      : str  -- original Whisper output, unmodified
        "correctedTranscript": str  -- after deterministic phrase/hotword correction
        "correctionApplied"  : bool -- True when at least one substitution was made
        "correctionMode"     : str  -- "safe_dictionary"
        "correctionReason"   : str  -- "phrase_map" | "none"
    """
    # Empty-bytes check comes first so it is independent of Whisper availability.
    if not audio_bytes:
        return {"transcript": "", "status": "empty"}

    if not _WHISPER_AVAILABLE:
        return {
            "transcript": "",
            "status": "unavailable",
            **_get_model_metadata(),
        }

    model = _load_model()
    if model is None:
        return {
            "transcript": "",
            "status": "unavailable",
            **_get_model_metadata(),
        }

    try:
        audio_buf = io.BytesIO(audio_bytes)
        transcribe_kwargs: dict = {}
        if language:
            transcribe_kwargs["language"] = language
        segments, _info = model.transcribe(audio_buf, **transcribe_kwargs)
        transcript = "".join(seg.text for seg in segments).strip()
        # TASK-245: extract detected language from TranscriptionInfo (None-safe).
        detected_language: str | None = getattr(_info, "language", None)
        if not transcript:
            return {"transcript": "", "status": "empty"}
        # TASK-247: apply deterministic correction layer before returning.
        # text/transcript use correctedTranscript; rawTranscript preserved for diagnostics.
        correction = correct_transcript_text(transcript)
        return {
            "transcript": correction["correctedTranscript"],
            "status": "ok",
            **_get_model_metadata(),
            "detectedLanguage": detected_language,
            "rawTranscript": correction["rawTranscript"],
            "correctedTranscript": correction["correctedTranscript"],
            "correctionApplied": correction["correctionApplied"],
            "correctionMode": correction["correctionMode"],
            "correctionReason": correction["correctionReason"],
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("TASK-167B: STT error mime=%s exc=%s", mime_type, exc)
        return {
            "transcript": "",
            "status": "error",
            **_get_model_metadata(),
        }
