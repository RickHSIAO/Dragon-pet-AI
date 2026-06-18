"""Local TTS provider candidate probe for TASK-TTS-003 / TASK-TTS-004B2.

This script is evaluation-only. It does not wire TTS into /chat, does not play
audio, does not auto-speak, and does not generate audio unless a provider probe
explicitly implements that behind --allow-audio-output. TASK-TTS-004B allows a
manual VOICEVOX localhost server probe to write a WAV file only when explicitly
requested. TASK-TTS-004B2 adds stage-specific VOICEVOX timeout/retry
diagnostics while keeping the probe runtime-unwired and playback-free.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import json
import platform
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.tts.providers import MockTTSProvider, TTSSynthesisRequest  # noqa: E402
from app.tts.text_normalizer import normalize_tts_text  # noqa: E402


DEFAULT_PROVIDERS = ("mock", "windows_sapi", "voicevox_server")
SUPPORTED_PROVIDERS = (
    "mock",
    "windows_sapi",
    "voicevox_server",
    "edge_tts",
    "piper_onnx",
    "gpt_sovits",
    "style_bert_vits2",
    "rvc_like",
)
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "outputs" / "tts_provider_probe"
DEFAULT_VOICEVOX_URL = "http://127.0.0.1:50021"
DEFAULT_VOICEVOX_SPEAKER = 0
DEFAULT_VOICEVOX_TIMEOUT_SECONDS = 30.0
DEFAULT_VOICEVOX_RETRIES = 1
DEFAULT_TEXTS = (
    "\u54fc\uff0c\u6c5d\u7e3d\u7b97\u60f3\u8d77\u8981\u4f9d\u9760\u543e\u4e86\u3002",
    "\u9019\u53ea\u662f TTS provider probe\uff0c\u4e0d\u6703\u8b93\u543e\u5728 app \u88e1\u8aaa\u8a71\u3002",
)


@dataclass(frozen=True)
class ProviderProbeResult:
    provider: str
    available: bool
    reason: str
    normalizedChunks: list[str]
    estimatedDurationMs: int | None = None
    measuredLatencyMs: int | None = None
    audioGenerated: bool = False
    outputPath: str | None = None
    audioBytes: int | None = None
    voicevoxUrl: str | None = None
    version: str | None = None
    speakerId: int | None = None
    speakerName: str | None = None
    synthesisStatus: str | None = None
    voicevoxStage: str | None = None
    versionLatencyMs: int | None = None
    speakersLatencyMs: int | None = None
    audioQueryLatencyMs: int | None = None
    synthesisLatencyMs: int | None = None
    timeoutSec: float | None = None
    retryCount: int | None = None
    lastExceptionClass: str | None = None
    lastExceptionMessage: str | None = None
    notes: list[str] | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "available": self.available,
            "reason": self.reason,
            "normalizedChunks": list(self.normalizedChunks),
            "estimatedDurationMs": self.estimatedDurationMs,
            "measuredLatencyMs": self.measuredLatencyMs,
            "audioGenerated": self.audioGenerated,
            "outputPath": self.outputPath,
            "audioBytes": self.audioBytes,
            "voicevoxUrl": self.voicevoxUrl,
            "version": self.version,
            "speakerId": self.speakerId,
            "speakerName": self.speakerName,
            "synthesisStatus": self.synthesisStatus,
            "voicevoxStage": self.voicevoxStage,
            "versionLatencyMs": self.versionLatencyMs,
            "speakersLatencyMs": self.speakersLatencyMs,
            "audioQueryLatencyMs": self.audioQueryLatencyMs,
            "synthesisLatencyMs": self.synthesisLatencyMs,
            "timeoutSec": self.timeoutSec,
            "retryCount": self.retryCount,
            "lastExceptionClass": self.lastExceptionClass,
            "lastExceptionMessage": self.lastExceptionMessage,
            "notes": list(self.notes or []),
        }


def parse_provider_list(raw: str | None) -> list[str]:
    if not raw:
        return list(DEFAULT_PROVIDERS)
    providers = []
    for item in raw.split(","):
        provider = item.strip().lower()
        if provider:
            providers.append(provider)
    return providers or list(DEFAULT_PROVIDERS)


def build_sample_text(text: str | None) -> str:
    if text and text.strip():
        return text.strip()
    return "\n".join(DEFAULT_TEXTS)


def probe_mock(chunks: list[str]) -> ProviderProbeResult:
    start = time.perf_counter()
    provider = MockTTSProvider()
    result = provider.synthesize(TTSSynthesisRequest(chunks=chunks))
    latency_ms = int((time.perf_counter() - start) * 1000)
    return ProviderProbeResult(
        provider="mock",
        available=True,
        reason="mock_metadata_only",
        normalizedChunks=result.chunks,
        estimatedDurationMs=result.estimatedDurationMs,
        measuredLatencyMs=latency_ms,
        audioGenerated=False,
        outputPath=None,
        notes=[
            "Always available.",
            "Metadata only; does not prove voice quality.",
            "No audio file or playback is produced.",
        ],
    )


def probe_windows_sapi(chunks: list[str]) -> ProviderProbeResult:
    notes = [
        "Availability check only; no speech synthesis or playback.",
        "Windows SAPI quality and Chinese voices depend on installed OS voices.",
    ]
    if platform.system().lower() != "windows":
        return _unavailable("windows_sapi", chunks, "not_windows", notes)

    pyttsx3_available = importlib.util.find_spec("pyttsx3") is not None
    win32com_available = importlib.util.find_spec("win32com") is not None
    if pyttsx3_available or win32com_available:
        found = []
        if pyttsx3_available:
            found.append("pyttsx3")
        if win32com_available:
            found.append("win32com")
        return ProviderProbeResult(
            provider="windows_sapi",
            available=True,
            reason="metadata_check_available",
            normalizedChunks=chunks,
            measuredLatencyMs=0,
            notes=notes + [f"Detected optional module(s): {', '.join(found)}."],
        )
    return _unavailable(
        "windows_sapi",
        chunks,
        "missing_optional_python_bridge",
        notes + ["Install is not required for TASK-TTS-003."],
    )


def probe_voicevox_server(
    chunks: list[str],
    *,
    allow_audio_output: bool = False,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    voicevox_url: str = DEFAULT_VOICEVOX_URL,
    voicevox_speaker: int = DEFAULT_VOICEVOX_SPEAKER,
    timeout_seconds: float = DEFAULT_VOICEVOX_TIMEOUT_SECONDS,
    voicevox_retries: int = DEFAULT_VOICEVOX_RETRIES,
) -> ProviderProbeResult:
    base_url = normalize_voicevox_url(voicevox_url)
    timeout_seconds = normalize_voicevox_timeout(timeout_seconds)
    max_retries = normalize_voicevox_retries(voicevox_retries)
    start = time.perf_counter()
    notes = [
        "Local server probe only.",
        "Not runtime wiring.",
        "Chinese/Japanese pronunciation quality must be manually judged.",
        "No playback is attempted.",
        f"VOICEVOX timeout seconds: {timeout_seconds:g}.",
        f"VOICEVOX audio retry limit: {max_retries}.",
    ]
    if base_url is None:
        return ProviderProbeResult(
            provider="voicevox_server",
            available=False,
            reason="non_localhost_url_rejected",
            normalizedChunks=chunks,
            measuredLatencyMs=0,
            audioGenerated=False,
            outputPath=None,
            audioBytes=None,
            voicevoxUrl=voicevox_url,
            speakerId=voicevox_speaker,
            synthesisStatus="voicevox_error",
            voicevoxStage="url_validation",
            timeoutSec=timeout_seconds,
            retryCount=0,
            notes=notes + ["Only localhost VOICEVOX URLs are allowed for TASK-TTS-004B."],
        )

    version_url = f"{base_url}/version"
    version = None
    speaker_name = None
    speaker_count = None
    version_latency_ms = None
    speakers_latency_ms = None
    try:
        version_raw, version_latency_ms = timed_call(
            lambda: _voicevox_get_text(version_url, timeout_seconds=timeout_seconds)
        )
        version = normalize_voicevox_version(version_raw)
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return ProviderProbeResult(
            provider="voicevox_server",
            available=False,
            reason=f"server_unavailable:{type(exc).__name__}",
            normalizedChunks=chunks,
            measuredLatencyMs=latency_ms,
            audioGenerated=False,
            outputPath=None,
            audioBytes=None,
            voicevoxUrl=base_url,
            version=None,
            speakerId=voicevox_speaker,
            speakerName=None,
            synthesisStatus="server_unavailable",
            voicevoxStage="version",
            versionLatencyMs=version_latency_ms,
            timeoutSec=timeout_seconds,
            retryCount=0,
            lastExceptionClass=type(exc).__name__,
            lastExceptionMessage=safe_exception_message(exc),
            notes=notes + [f"Checked {version_url}."],
        )

    try:
        speakers, speakers_latency_ms = timed_call(
            lambda: _voicevox_get_json(f"{base_url}/speakers", timeout_seconds=timeout_seconds)
        )
        speaker_count, speaker_name = summarize_voicevox_speakers(speakers, voicevox_speaker)
    except (json.JSONDecodeError, OSError, urllib.error.URLError, TimeoutError, TypeError, ValueError):
        speaker_count = None
        speaker_name = None

    metadata_notes = notes + [
        f"Checked {version_url}.",
        f"Version response: {version or 'empty'}.",
        f"Selected speaker id: {voicevox_speaker}.",
    ]
    if speaker_count is not None:
        metadata_notes.append(f"Speaker count: {speaker_count}.")
    if speaker_name:
        metadata_notes.append(f"Selected speaker name: {speaker_name}.")
    if not allow_audio_output:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return ProviderProbeResult(
            provider="voicevox_server",
            available=True,
            reason="local_server_metadata_ok",
            normalizedChunks=chunks,
            measuredLatencyMs=latency_ms,
            audioGenerated=False,
            outputPath=None,
            audioBytes=None,
            voicevoxUrl=base_url,
            version=version,
            speakerId=voicevox_speaker,
            speakerName=speaker_name,
            synthesisStatus="audio_output_disabled",
            voicevoxStage="metadata",
            versionLatencyMs=version_latency_ms,
            speakersLatencyMs=speakers_latency_ms,
            timeoutSec=timeout_seconds,
            retryCount=0,
            notes=metadata_notes + ["Audio output disabled; no synthesis call or WAV write."],
        )

    audio_query_latency_ms = None
    synthesis_latency_ms = None
    retry_count = 0
    try:
        query, audio_query_latency_ms, query_retry_count = call_voicevox_audio_stage(
            lambda: _voicevox_audio_query(
                base_url,
                text="\n".join(chunks),
                speaker_id=voicevox_speaker,
                timeout_seconds=timeout_seconds,
            ),
            max_retries=max_retries,
        )
        retry_count += query_retry_count
    except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        audio_query_latency_ms = getattr(exc, "voicevox_latency_ms", audio_query_latency_ms)
        status = "audio_query_timeout" if is_timeout_exception(exc) else "voicevox_error"
        return ProviderProbeResult(
            provider="voicevox_server",
            available=True,
            reason=f"{status}:{type(exc).__name__}",
            normalizedChunks=chunks,
            measuredLatencyMs=latency_ms,
            audioGenerated=False,
            outputPath=None,
            audioBytes=None,
            voicevoxUrl=base_url,
            version=version,
            speakerId=voicevox_speaker,
            speakerName=speaker_name,
            synthesisStatus=status,
            voicevoxStage="audio_query",
            versionLatencyMs=version_latency_ms,
            speakersLatencyMs=speakers_latency_ms,
            audioQueryLatencyMs=audio_query_latency_ms,
            timeoutSec=timeout_seconds,
            retryCount=max_retries,
            lastExceptionClass=type(exc).__name__,
            lastExceptionMessage=safe_exception_message(exc),
            notes=metadata_notes + ["Audio query failed; no synthesis call, WAV write, or playback was attempted."],
        )

    try:
        audio, synthesis_latency_ms, synthesis_retry_count = call_voicevox_audio_stage(
            lambda: _voicevox_synthesis(
                base_url,
                query=query,
                speaker_id=voicevox_speaker,
                timeout_seconds=timeout_seconds,
            ),
            max_retries=max_retries,
        )
        retry_count += synthesis_retry_count
        output_path = write_voicevox_audio(audio, output_root=output_root)
    except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        synthesis_latency_ms = getattr(exc, "voicevox_latency_ms", synthesis_latency_ms)
        status = "synthesis_timeout" if is_timeout_exception(exc) else "voicevox_error"
        return ProviderProbeResult(
            provider="voicevox_server",
            available=True,
            reason=f"{status}:{type(exc).__name__}",
            normalizedChunks=chunks,
            measuredLatencyMs=latency_ms,
            audioGenerated=False,
            outputPath=None,
            audioBytes=None,
            voicevoxUrl=base_url,
            version=version,
            speakerId=voicevox_speaker,
            speakerName=speaker_name,
            synthesisStatus=status,
            voicevoxStage="synthesis",
            versionLatencyMs=version_latency_ms,
            speakersLatencyMs=speakers_latency_ms,
            audioQueryLatencyMs=audio_query_latency_ms,
            synthesisLatencyMs=synthesis_latency_ms,
            timeoutSec=timeout_seconds,
            retryCount=retry_count + max_retries,
            lastExceptionClass=type(exc).__name__,
            lastExceptionMessage=safe_exception_message(exc),
            notes=metadata_notes + ["Audio query succeeded, but VOICEVOX synthesis failed before WAV write."],
        )

    latency_ms = int((time.perf_counter() - start) * 1000)
    return ProviderProbeResult(
        provider="voicevox_server",
        available=True,
        reason="voicevox_success",
        normalizedChunks=chunks,
        measuredLatencyMs=latency_ms,
        audioGenerated=True,
        outputPath=str(output_path),
        audioBytes=len(audio),
        voicevoxUrl=base_url,
        version=version,
        speakerId=voicevox_speaker,
        speakerName=speaker_name,
        synthesisStatus="voicevox_success",
        voicevoxStage="complete",
        versionLatencyMs=version_latency_ms,
        speakersLatencyMs=speakers_latency_ms,
        audioQueryLatencyMs=audio_query_latency_ms,
        synthesisLatencyMs=synthesis_latency_ms,
        timeoutSec=timeout_seconds,
        retryCount=retry_count,
        notes=metadata_notes + ["WAV generated under ignored local probe outputs. No playback was attempted."],
    )


def normalize_voicevox_url(raw_url: str) -> str | None:
    parsed = urllib.parse.urlparse(raw_url.strip())
    if parsed.scheme not in {"http", "https"}:
        return None
    hostname = (parsed.hostname or "").lower()
    if hostname not in {"127.0.0.1", "localhost", "::1"}:
        return None
    path = parsed.path.rstrip("/")
    if path:
        return None
    netloc = parsed.netloc
    return urllib.parse.urlunparse((parsed.scheme, netloc, "", "", "", "")).rstrip("/")


def normalize_voicevox_timeout(timeout_seconds: float) -> float:
    try:
        timeout = float(timeout_seconds)
    except (TypeError, ValueError):
        return DEFAULT_VOICEVOX_TIMEOUT_SECONDS
    if timeout <= 0:
        return DEFAULT_VOICEVOX_TIMEOUT_SECONDS
    return min(timeout, 120.0)


def normalize_voicevox_retries(retries: int) -> int:
    try:
        value = int(retries)
    except (TypeError, ValueError):
        return DEFAULT_VOICEVOX_RETRIES
    return max(0, min(value, 3))


def normalize_voicevox_version(raw_version: str) -> str | None:
    value = (raw_version or "").strip()
    if not value:
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return value
    if isinstance(parsed, str):
        return parsed.strip() or None
    return value


def safe_exception_message(exc: BaseException) -> str:
    message = str(exc).strip()
    if not message:
        return ""
    return message[:200]


def is_timeout_exception(exc: BaseException) -> bool:
    if isinstance(exc, TimeoutError):
        return True
    reason = getattr(exc, "reason", None)
    if isinstance(reason, TimeoutError):
        return True
    name = type(exc).__name__.lower()
    return "timeout" in name or "timed out" in str(exc).lower()


def timed_call(callable_fn):
    start = time.perf_counter()
    try:
        value = callable_fn()
    finally:
        latency_ms = int((time.perf_counter() - start) * 1000)
    return value, latency_ms


def call_voicevox_audio_stage(callable_fn, *, max_retries: int):
    retry_count = 0
    for attempt_index in range(max_retries + 1):
        start = time.perf_counter()
        try:
            value = callable_fn()
            latency_ms = int((time.perf_counter() - start) * 1000)
            return value, latency_ms, retry_count
        except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            setattr(exc, "voicevox_latency_ms", int((time.perf_counter() - start) * 1000))
            if attempt_index >= max_retries:
                raise exc
            retry_count += 1
    raise RuntimeError("unreachable_voicevox_retry_state")


def summarize_voicevox_speakers(speakers: object, speaker_id: int) -> tuple[int | None, str | None]:
    if not isinstance(speakers, list):
        return None, None
    speaker_count = len(speakers)
    for speaker in speakers:
        if not isinstance(speaker, dict):
            continue
        speaker_name = str(speaker.get("name") or "").strip()
        styles = speaker.get("styles")
        if not isinstance(styles, list):
            continue
        for style in styles:
            if not isinstance(style, dict):
                continue
            if style.get("id") == speaker_id:
                style_name = str(style.get("name") or "").strip()
                selected = speaker_name
                if speaker_name and style_name:
                    selected = f"{speaker_name} / {style_name}"
                elif style_name:
                    selected = style_name
                return speaker_count, selected or None
    return speaker_count, None


def _voicevox_get_text(url: str, *, timeout_seconds: float) -> str:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return response.read(500).decode("utf-8", errors="replace").strip()


def _voicevox_get_json(url: str, *, timeout_seconds: float) -> object:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _voicevox_audio_query(
    base_url: str,
    *,
    text: str,
    speaker_id: int,
    timeout_seconds: float,
) -> dict[str, object]:
    params = urllib.parse.urlencode({"text": text, "speaker": speaker_id})
    request = urllib.request.Request(f"{base_url}/audio_query?{params}", data=b"", method="POST")
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _voicevox_synthesis(
    base_url: str,
    *,
    query: dict[str, object],
    speaker_id: int,
    timeout_seconds: float,
) -> bytes:
    params = urllib.parse.urlencode({"speaker": speaker_id})
    body = json.dumps(query, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/synthesis?{params}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        audio = response.read()
    if not audio:
        raise ValueError("empty_voicevox_audio")
    return audio


def write_voicevox_audio(audio: bytes, *, output_root: Path = DEFAULT_OUTPUT_ROOT) -> Path:
    date_key = _dt.datetime.now().strftime("%Y%m%d")
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = output_root / date_key / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"voicevox_server_{stamp}.wav"
    output_path.write_bytes(audio)
    return output_path


def probe_edge_tts(chunks: list[str]) -> ProviderProbeResult:
    notes = [
        "Network/cloud-ish candidate only; not default.",
        "TASK-TTS-003 does not synthesize or send text to this provider.",
    ]
    if importlib.util.find_spec("edge_tts") is None:
        return _unavailable("edge_tts", chunks, "missing_optional_dependency", notes)
    return ProviderProbeResult(
        provider="edge_tts",
        available=True,
        reason="optional_dependency_present",
        normalizedChunks=chunks,
        measuredLatencyMs=0,
        notes=notes,
    )


def probe_future_manual(provider: str, chunks: list[str]) -> ProviderProbeResult:
    notes_by_provider = {
        "piper_onnx": "Offline local path candidate; model/runtime setup is future manual work.",
        "gpt_sovits": "Future research path; requires explicit model/data/licensing task.",
        "style_bert_vits2": "Future research path; requires explicit model/data/licensing task.",
        "rvc_like": "Future voice-conversion research only; not a TTS runtime path here.",
    }
    return _unavailable(
        provider,
        chunks,
        "future_manual_candidate_not_probed",
        [notes_by_provider.get(provider, "Future manual candidate.")],
    )


def probe_provider(
    provider: str,
    chunks: list[str],
    *,
    allow_audio_output: bool = False,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    voicevox_url: str = DEFAULT_VOICEVOX_URL,
    voicevox_speaker: int = DEFAULT_VOICEVOX_SPEAKER,
    voicevox_timeout_seconds: float = DEFAULT_VOICEVOX_TIMEOUT_SECONDS,
    voicevox_retries: int = DEFAULT_VOICEVOX_RETRIES,
) -> ProviderProbeResult:
    if provider == "mock":
        return probe_mock(chunks)
    if provider == "windows_sapi":
        return probe_windows_sapi(chunks)
    if provider == "voicevox_server":
        return probe_voicevox_server(
            chunks,
            allow_audio_output=allow_audio_output,
            output_root=output_root,
            voicevox_url=voicevox_url,
            voicevox_speaker=voicevox_speaker,
            timeout_seconds=voicevox_timeout_seconds,
            voicevox_retries=voicevox_retries,
        )
    if provider == "edge_tts":
        return probe_edge_tts(chunks)
    if provider in {"piper_onnx", "gpt_sovits", "style_bert_vits2", "rvc_like"}:
        return probe_future_manual(provider, chunks)
    return _unavailable(
        provider,
        chunks,
        "unsupported_provider",
        [f"Supported providers: {', '.join(SUPPORTED_PROVIDERS)}."],
    )


def build_probe_report(
    *,
    text: str,
    providers: Iterable[str],
    allow_audio_output: bool = False,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    voicevox_url: str = DEFAULT_VOICEVOX_URL,
    voicevox_speaker: int = DEFAULT_VOICEVOX_SPEAKER,
    voicevox_timeout_seconds: float = DEFAULT_VOICEVOX_TIMEOUT_SECONDS,
    voicevox_retries: int = DEFAULT_VOICEVOX_RETRIES,
) -> dict[str, object]:
    normalized_chunks = normalize_tts_text(text)
    provider_results = [
        probe_provider(
            provider,
            normalized_chunks,
            allow_audio_output=allow_audio_output,
            output_root=output_root,
            voicevox_url=voicevox_url,
            voicevox_speaker=voicevox_speaker,
            voicevox_timeout_seconds=voicevox_timeout_seconds,
            voicevox_retries=voicevox_retries,
        ).to_dict()
        for provider in providers
    ]
    audio_generated = any(bool(result["audioGenerated"]) for result in provider_results)
    return {
        "task": "TASK-TTS-004B2",
        "status": "probe_only_no_runtime_wiring",
        "generatedAt": _dt.datetime.now(_dt.UTC).isoformat(),
        "audioOutputAllowed": bool(allow_audio_output),
        "audioGenerated": audio_generated,
        "inputTextLength": len(text),
        "normalizedChunks": normalized_chunks,
        "providersRequested": list(providers),
        "providers": provider_results,
        "voicevox": {
            "timeoutSec": normalize_voicevox_timeout(voicevox_timeout_seconds),
            "retries": normalize_voicevox_retries(voicevox_retries),
            "localhostOnly": True,
        },
        "safety": {
            "runtimeTtsWired": False,
            "playbackAdded": False,
            "autoSpeakEnabled": False,
            "chatSchemaChanged": False,
            "externalDependencyAdded": False,
            "runtimePlaybackAdded": False,
            "sttDefaultChanged": False,
            "conversationModeChanged": False,
            "ownerVoiceGateChanged": False,
        },
    }


def write_reports(report: dict[str, object], *, output_root: Path = DEFAULT_OUTPUT_ROOT) -> dict[str, str]:
    date_key = _dt.datetime.now().strftime("%Y%m%d")
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = output_root / date_key
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"tts_provider_probe_{stamp}.json"
    md_path = output_dir / f"tts_provider_probe_{stamp}.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown_report(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def render_markdown_report(report: dict[str, object]) -> str:
    lines = [
        "# TTS Provider Probe",
        "",
        f"- Task: {report['task']}",
        f"- Status: {report['status']}",
        f"- Generated at: {report['generatedAt']}",
        f"- Audio output allowed: {str(report['audioOutputAllowed']).lower()}",
        f"- Audio generated: {str(report['audioGenerated']).lower()}",
        "",
        "## Normalized Chunks",
        "",
    ]
    chunks = report.get("normalizedChunks") or []
    if chunks:
        lines.extend(f"- {chunk}" for chunk in chunks)
    else:
        lines.append("- none")
    lines.extend(["", "## Providers", ""])
    for result in report.get("providers", []):
        lines.extend(
            [
                f"### {result['provider']}",
                "",
                f"- Available: {str(result['available']).lower()}",
                f"- Reason: {result['reason']}",
                f"- Measured latency ms: {result['measuredLatencyMs']}",
                f"- Estimated duration ms: {result['estimatedDurationMs']}",
                f"- Audio generated: {str(result['audioGenerated']).lower()}",
                f"- Output path: {result['outputPath']}",
                f"- Audio bytes: {result['audioBytes']}",
                f"- VOICEVOX URL: {result['voicevoxUrl']}",
                f"- VOICEVOX version: {result['version']}",
                f"- Speaker id: {result['speakerId']}",
                f"- Speaker name: {result['speakerName']}",
                f"- Synthesis status: {result['synthesisStatus']}",
                f"- VOICEVOX stage: {result['voicevoxStage']}",
                f"- Version latency ms: {result['versionLatencyMs']}",
                f"- Speakers latency ms: {result['speakersLatencyMs']}",
                f"- Audio query latency ms: {result['audioQueryLatencyMs']}",
                f"- Synthesis latency ms: {result['synthesisLatencyMs']}",
                f"- Timeout sec: {result['timeoutSec']}",
                f"- Retry count: {result['retryCount']}",
                f"- Last exception class: {result['lastExceptionClass']}",
                f"- Last exception message: {result['lastExceptionMessage']}",
                "- Notes:",
            ]
        )
        notes = result.get("notes") or []
        lines.extend(f"  - {note}" for note in notes) if notes else lines.append("  - none")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _unavailable(
    provider: str,
    chunks: list[str],
    reason: str,
    notes: list[str] | None = None,
) -> ProviderProbeResult:
    return ProviderProbeResult(
        provider=provider,
        available=False,
        reason=reason,
        normalizedChunks=chunks,
        estimatedDurationMs=None,
        measuredLatencyMs=0,
        audioGenerated=False,
        outputPath=None,
        notes=notes or [],
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Probe local/offline TTS provider candidates without runtime wiring or playback.",
    )
    parser.add_argument("--text", default=None, help="Sample text to normalize and probe.")
    parser.add_argument(
        "--providers",
        default=",".join(DEFAULT_PROVIDERS),
        help=f"Comma-separated providers. Supported: {', '.join(SUPPORTED_PROVIDERS)}.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Root directory for local JSON/Markdown reports.",
    )
    parser.add_argument("--pretty", action="store_true", help="Print pretty JSON to stdout.")
    parser.add_argument(
        "--allow-audio-output",
        action="store_true",
        help="Allow provider probes that explicitly support it to write local audio files. Never plays audio.",
    )
    parser.add_argument(
        "--voicevox-url",
        default=DEFAULT_VOICEVOX_URL,
        help="VOICEVOX Engine-compatible localhost URL. Non-localhost URLs are rejected.",
    )
    parser.add_argument(
        "--voicevox-speaker",
        type=int,
        default=DEFAULT_VOICEVOX_SPEAKER,
        help="VOICEVOX speaker/style id for optional audio output and speaker metadata.",
    )
    parser.add_argument(
        "--voicevox-timeout-sec",
        type=float,
        default=DEFAULT_VOICEVOX_TIMEOUT_SECONDS,
        help="VOICEVOX HTTP timeout in seconds for version, speakers, audio_query, and synthesis.",
    )
    parser.add_argument(
        "--voicevox-retries",
        type=int,
        default=DEFAULT_VOICEVOX_RETRIES,
        help="Finite retry count for local VOICEVOX audio_query/synthesis stages.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    text = build_sample_text(args.text)
    providers = parse_provider_list(args.providers)
    report = build_probe_report(
        text=text,
        providers=providers,
        allow_audio_output=args.allow_audio_output,
        output_root=Path(args.output_root),
        voicevox_url=args.voicevox_url,
        voicevox_speaker=args.voicevox_speaker,
        voicevox_timeout_seconds=args.voicevox_timeout_sec,
        voicevox_retries=args.voicevox_retries,
    )
    report_paths = write_reports(report, output_root=Path(args.output_root))
    report["reportPaths"] = report_paths
    if args.pretty:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"status": "ok", "reportPaths": report_paths}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
