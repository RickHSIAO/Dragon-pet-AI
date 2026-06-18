"""Disabled-by-default TTS queue and mock preview service.

TASK-TTS-002 creates deterministic TTS metadata only. The service never plays
audio, never creates generated audio files, and never auto-speaks chat replies.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.core.config import get_tts_enabled, get_tts_provider_name, get_tts_voice
from app.tts.providers import (
    DEFAULT_MOCK_PROVIDER,
    DEFAULT_MOCK_VOICE,
    TTSSynthesisRequest,
    create_tts_provider,
)
from app.tts.text_normalizer import normalize_tts_text


@dataclass(frozen=True)
class TTSQueueJob:
    id: str
    provider: str
    requested_voice: str
    resolved_voice: str
    chunks: list[str]
    status: str = "not_started"


@dataclass
class TTSQueueState:
    enabled: bool = False
    provider_name: str = DEFAULT_MOCK_PROVIDER
    requested_voice: str = DEFAULT_MOCK_VOICE
    resolved_voice: str = DEFAULT_MOCK_VOICE
    queue: list[TTSQueueJob] = field(default_factory=list)
    active_job_id: str | None = None
    chunks_count: int = 0
    last_synthesis_status: str = "not_started"
    last_error: str | None = None
    playback_status: str = "disabled"
    auto_speak_enabled: bool = False

    def diagnostics(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "provider": self.provider_name,
            "requestedVoice": self.requested_voice,
            "resolvedVoice": self.resolved_voice,
            "queueLength": len(self.queue),
            "activeJobId": self.active_job_id,
            "chunksCount": self.chunks_count,
            "lastSynthesisStatus": self.last_synthesis_status,
            "lastError": self.last_error,
            "playbackStatus": self.playback_status,
            "autoSpeakEnabled": self.auto_speak_enabled,
        }


class TTSService:
    """Small service facade for mock TTS provider preview and diagnostics."""

    def __init__(
        self,
        *,
        enabled: bool | None = None,
        provider_name: str | None = None,
        requested_voice: str | None = None,
    ) -> None:
        self.enabled = get_tts_enabled() if enabled is None else bool(enabled)
        self.provider_name = provider_name or get_tts_provider_name()
        self.requested_voice = requested_voice or get_tts_voice()
        self.provider = create_tts_provider(self.provider_name)
        self.queue_state = TTSQueueState(
            enabled=self.enabled,
            provider_name=getattr(self.provider, "provider_id", self.provider_name),
            requested_voice=self.requested_voice,
            resolved_voice=self.requested_voice or DEFAULT_MOCK_VOICE,
            playback_status="not_started" if self.enabled else "disabled",
            auto_speak_enabled=False,
        )

    def diagnostics(self) -> dict[str, object]:
        return self.queue_state.diagnostics()

    def preview(self, reply_text: str | None) -> dict[str, object]:
        """Return normalized chunks and mock synthesis metadata.

        This does not enqueue runtime playback. The queue length and active job
        remain empty/None in TASK-TTS-002.
        """

        chunks = normalize_tts_text(reply_text)
        request = TTSSynthesisRequest(
            chunks=chunks,
            provider=self.queue_state.provider_name,
            voice=self.queue_state.requested_voice,
        )
        result = self.provider.synthesize(request)
        self.queue_state.chunks_count = len(result.chunks)
        self.queue_state.last_synthesis_status = result.synthesisStatus
        self.queue_state.last_error = result.error
        self.queue_state.resolved_voice = result.voice
        self.queue_state.playback_status = "not_started" if self.enabled else "disabled"

        response = self.queue_state.diagnostics()
        response.update(result.to_dict())
        return response


def get_tts_diagnostics() -> dict[str, object]:
    return TTSService().diagnostics()


def build_tts_preview(reply_text: str | None) -> dict[str, object]:
    return TTSService().preview(reply_text)
