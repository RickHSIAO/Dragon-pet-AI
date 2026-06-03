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
from typing import Any

logger = logging.getLogger(__name__)

_WHISPER_AVAILABLE: bool = False
_whisper_model: Any = None
# TASK-245: static metadata surfaced in diagnostics — update if model changes.
_STT_PROVIDER = "faster-whisper-local"
_STT_MODEL_NAME = "tiny"


def _detect_whisper() -> bool:
    """Check whether faster-whisper is importable without loading the model."""
    try:
        import faster_whisper  # noqa: F401  # type: ignore
        return True
    except ImportError:
        return False


_WHISPER_AVAILABLE = _detect_whisper()


def _load_model() -> Any:
    """
    Lazily load the faster-whisper 'tiny' model on first use.
    Returns None if unavailable or if loading fails.
    """
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    if not _WHISPER_AVAILABLE:
        return None
    try:
        from faster_whisper import WhisperModel  # type: ignore
        _whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
        logger.info("TASK-167B: faster-whisper 'tiny' model loaded.")
    except Exception as exc:  # noqa: BLE001
        logger.warning("TASK-167B: Failed to load faster-whisper model: %s", exc)
        _whisper_model = None
    return _whisper_model


def _reset_model_for_tests() -> None:
    """Reset the cached model -- only for test isolation. Not for production use."""
    global _whisper_model
    _whisper_model = None


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
        "transcript" : str   -- transcribed text (empty string on failure/empty audio)
        "status"     : str   -- one of "ok", "unavailable", "empty", "error"
    """
    # Empty-bytes check comes first so it is independent of Whisper availability.
    if not audio_bytes:
        return {"transcript": "", "status": "empty"}

    if not _WHISPER_AVAILABLE:
        return {"transcript": "", "status": "unavailable"}

    model = _load_model()
    if model is None:
        return {"transcript": "", "status": "unavailable"}

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
        return {
            "transcript": transcript,
            "status": "ok",
            "provider": _STT_PROVIDER,
            "model": _STT_MODEL_NAME,
            "detectedLanguage": detected_language,
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("TASK-167B: STT error mime=%s exc=%s", mime_type, exc)
        return {"transcript": "", "status": "error"}
