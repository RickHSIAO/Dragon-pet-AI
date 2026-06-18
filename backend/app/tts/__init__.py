"""Safe TTS skeleton package for TASK-TTS-002.

No real synthesis, playback, audio files, model downloads, or external calls
are implemented here.
"""

from app.tts.tts_service import TTSService, build_tts_preview, get_tts_diagnostics

__all__ = ["TTSService", "build_tts_preview", "get_tts_diagnostics"]
