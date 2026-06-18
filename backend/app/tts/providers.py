"""TTS provider contracts and the deterministic mock provider.

TASK-TTS-002 deliberately implements metadata-only mock synthesis. No WAV/MP3
files are generated, no audio bytes are returned, and no provider dependency is
loaded.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


DEFAULT_MOCK_PROVIDER = "mock"
DEFAULT_MOCK_VOICE = "christina_mock"
_ESTIMATED_MS_PER_CHINESE_CHAR = 140
_MIN_CHUNK_DURATION_MS = 320


@dataclass(frozen=True)
class TTSSynthesisRequest:
    chunks: list[str]
    provider: str = DEFAULT_MOCK_PROVIDER
    voice: str = DEFAULT_MOCK_VOICE
    language_hint: str = "zh-TW"
    style_hint: str = "christina"
    request_id: str | None = None


@dataclass(frozen=True)
class TTSSynthesisResult:
    provider: str
    voice: str
    chunks: list[str]
    estimatedDurationMs: int
    synthesisStatus: str
    audioAvailable: bool
    audioPath: None
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "voice": self.voice,
            "chunks": list(self.chunks),
            "estimatedDurationMs": self.estimatedDurationMs,
            "synthesisStatus": self.synthesisStatus,
            "audioAvailable": self.audioAvailable,
            "audioPath": self.audioPath,
            "error": self.error,
        }


class TTSProvider(Protocol):
    provider_id: str

    def synthesize(self, request: TTSSynthesisRequest) -> TTSSynthesisResult:
        """Return safe synthesis metadata for the request."""


class MockTTSProvider:
    """Deterministic metadata-only TTS provider for tests and diagnostics."""

    provider_id = DEFAULT_MOCK_PROVIDER

    def synthesize(self, request: TTSSynthesisRequest) -> TTSSynthesisResult:
        chunks = [chunk for chunk in request.chunks if chunk.strip()]
        estimated_ms = sum(
            max(_MIN_CHUNK_DURATION_MS, len(chunk) * _ESTIMATED_MS_PER_CHINESE_CHAR)
            for chunk in chunks
        )
        return TTSSynthesisResult(
            provider=self.provider_id,
            voice=request.voice or DEFAULT_MOCK_VOICE,
            chunks=chunks,
            estimatedDurationMs=estimated_ms,
            synthesisStatus="mock_success" if chunks else "empty",
            audioAvailable=False,
            audioPath=None,
            error=None,
        )


def create_tts_provider(provider_name: str | None) -> TTSProvider:
    """Return the provider implementation for TASK-TTS-002.

    Only ``mock`` is implemented. Future provider names intentionally fall back
    to the mock provider instead of loading external engines or dependencies.
    """

    provider_id = (provider_name or DEFAULT_MOCK_PROVIDER).strip().lower()
    if provider_id == DEFAULT_MOCK_PROVIDER:
        return MockTTSProvider()
    return MockTTSProvider()
