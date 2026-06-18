"""Local TTS provider candidate probe for TASK-TTS-003.

This script is evaluation-only. It does not wire TTS into /chat, does not play
audio, does not auto-speak, and does not generate audio unless a future provider
explicitly implements that behind --allow-audio-output. TASK-TTS-003 keeps every
implemented probe metadata-only.
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
    outputPath: None = None
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


def probe_voicevox_server(chunks: list[str], *, timeout_seconds: float = 0.5) -> ProviderProbeResult:
    url = "http://127.0.0.1:50021/version"
    start = time.perf_counter()
    notes = [
        "Local server availability check only.",
        "No audio query, synthesis, file write, or playback is attempted.",
    ]
    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            body = response.read(200).decode("utf-8", errors="replace").strip()
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        return ProviderProbeResult(
            provider="voicevox_server",
            available=False,
            reason=f"server_unavailable:{type(exc).__name__}",
            normalizedChunks=chunks,
            measuredLatencyMs=latency_ms,
            notes=notes + [f"Checked {url}."],
        )
    latency_ms = int((time.perf_counter() - start) * 1000)
    return ProviderProbeResult(
        provider="voicevox_server",
        available=True,
        reason="local_server_version_ok",
        normalizedChunks=chunks,
        measuredLatencyMs=latency_ms,
        notes=notes + [f"Version response: {body or 'empty'}."],
    )


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


def probe_provider(provider: str, chunks: list[str]) -> ProviderProbeResult:
    if provider == "mock":
        return probe_mock(chunks)
    if provider == "windows_sapi":
        return probe_windows_sapi(chunks)
    if provider == "voicevox_server":
        return probe_voicevox_server(chunks)
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
) -> dict[str, object]:
    normalized_chunks = normalize_tts_text(text)
    provider_results = [probe_provider(provider, normalized_chunks).to_dict() for provider in providers]
    audio_generated = any(bool(result["audioGenerated"]) for result in provider_results)
    return {
        "task": "TASK-TTS-003",
        "status": "probe_only_no_runtime_wiring",
        "generatedAt": _dt.datetime.now(_dt.UTC).isoformat(),
        "audioOutputAllowed": bool(allow_audio_output),
        "audioGenerated": audio_generated,
        "inputTextLength": len(text),
        "normalizedChunks": normalized_chunks,
        "providersRequested": list(providers),
        "providers": provider_results,
        "safety": {
            "runtimeTtsWired": False,
            "playbackAdded": False,
            "autoSpeakEnabled": False,
            "chatSchemaChanged": False,
            "externalDependencyAdded": False,
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
        help="Reserved future opt-in. TASK-TTS-003 providers remain metadata-only.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    text = build_sample_text(args.text)
    providers = parse_provider_list(args.providers)
    report = build_probe_report(
        text=text,
        providers=providers,
        allow_audio_output=args.allow_audio_output,
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
