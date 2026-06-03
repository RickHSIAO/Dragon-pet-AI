"""
TASK-249 STT Provider Smoke — direct module test.

Tests all 4 provider scenarios by reloading app.stt.stt_service with
different DRAGON_PET_STT_PROVIDER env values.  Does NOT require uvicorn
or port 8000 — the module-level resolver is the thing being tested.

Usage (from repo root):
    backend\\.venv\\Scripts\\python.exe scripts\\stt_provider_smoke.py
"""
import os
import sys
import struct
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_pass_count = 0
_fail_count = 0


def _ok(msg: str) -> None:
    global _pass_count
    _pass_count += 1
    print(f"    PASS  {msg}")


def _fail(msg: str) -> None:
    global _fail_count
    _fail_count += 1
    print(f"    FAIL  {msg}")


def check(cond: bool, msg: str) -> None:
    (_ok if cond else _fail)(msg)


def create_minimal_wav() -> bytes:
    """0.1 s of silence — mono 16kHz 16-bit PCM."""
    sr, ch, bps = 16000, 1, 16
    ns = sr // 10
    ds = ns * ch * (bps // 8)
    return (
        b"RIFF" + struct.pack("<I", 36 + ds) + b"WAVE"
        + b"fmt " + struct.pack("<IHHIIHH", 16, 1, ch, sr,
                                sr * ch * (bps // 8), ch * (bps // 8), bps)
        + b"data" + struct.pack("<I", ds) + b"\x00" * ds
    )


def reload_stt(provider_value):
    """
    Clear all cached app.* modules, set the env var, then re-import
    app.stt.stt_service so module-level resolver re-runs from scratch.
    """
    for key in list(sys.modules.keys()):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]

    if provider_value is None:
        os.environ.pop("DRAGON_PET_STT_PROVIDER", None)
    else:
        os.environ["DRAGON_PET_STT_PROVIDER"] = provider_value

    import app.stt.stt_service as stt  # noqa: PLC0415
    return stt


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------
WAV = create_minimal_wav()

print()
print("=" * 65)
print("  TASK-249  STT Provider Smoke")
print("=" * 65)

# ── 1 / default ─────────────────────────────────────────────────────────────
print("\n[1/4] Default (DRAGON_PET_STT_PROVIDER not set)")
stt = reload_stt(None)
r = stt._STT_PROVIDER_RESOLUTION
m = stt._get_provider_metadata()
check(r["resolved_provider"]    == "faster-whisper-local",
      f"resolved=faster-whisper-local (got {r['resolved_provider']!r})")
check(r["provider_source"]      == "default",
      f"source=default (got {r['provider_source']!r})")
check(r["provider_fallback_reason"] == "none",
      f"fallback_reason=none")
check(m["sttProviderResolved"]  == "faster-whisper-local",
      f"metadata.sttProviderResolved=faster-whisper-local")
check(m["sttProviderSource"]    == "default",
      f"metadata.sttProviderSource=default")
check(m["sttProviderFallbackReason"] == "none",
      f"metadata.sttProviderFallbackReason=none")
check(m["sttProviderRequested"] == "faster-whisper-local",
      f"metadata.sttProviderRequested=faster-whisper-local (default fills in resolved)")

# ── 2 / invalid fallback ─────────────────────────────────────────────────────
print("\n[2/4] Invalid provider fallback  (DRAGON_PET_STT_PROVIDER=bad-provider)")
stt = reload_stt("bad-provider")
r = stt._STT_PROVIDER_RESOLUTION
m = stt._get_provider_metadata()
check(r["requested_provider"]   == "bad-provider",
      f"requested=bad-provider (got {r['requested_provider']!r})")
check(r["resolved_provider"]    == "faster-whisper-local",
      f"resolved=faster-whisper-local")
check(r["provider_source"]      == "fallback",
      f"source=fallback")
check(r["provider_fallback_reason"] == "invalid_provider",
      f"fallback_reason=invalid_provider")
check(m["sttProviderRequested"]      == "bad-provider",
      f"metadata.sttProviderRequested=bad-provider")
check(m["sttProviderSource"]         == "fallback",
      f"metadata.sttProviderSource=fallback")
check(m["sttProviderFallbackReason"] == "invalid_provider",
      f"metadata.sttProviderFallbackReason=invalid_provider")

# ── 3 / funasr-local ─────────────────────────────────────────────────────────
print("\n[3/4] funasr-local  (DRAGON_PET_STT_PROVIDER=funasr-local)")
print("      (unavailable = PASS if funasr not installed; loaded = PASS if installed)")
stt = reload_stt("funasr-local")
r = stt._STT_PROVIDER_RESOLUTION
m = stt._get_provider_metadata()
check(r["requested_provider"]  == "funasr-local",
      f"requested=funasr-local")
check(r["resolved_provider"]   == "funasr-local",
      f"resolved=funasr-local")
check(r["provider_source"]     == "env",
      f"source=env")
check(r["provider_fallback_reason"] == "none",
      f"fallback_reason=none")
check(m["sttProviderResolved"] == "funasr-local",
      f"metadata.sttProviderResolved=funasr-local")
check(m["sttProviderSource"]   == "env",
      f"metadata.sttProviderSource=env")
check(m["sttProviderLoadStatus"] in ("unavailable", "loaded"),
      f"loadStatus in (unavailable, loaded) — got {m['sttProviderLoadStatus']!r}")

print("      Calling transcribe_audio_bytes() with silence WAV ...")
try:
    resp = stt.transcribe_audio_bytes(WAV, mime_type="audio/wav", language="zh")
    check("sttProviderResolved" in resp,
          "transcribe response includes sttProviderResolved")
    check(resp.get("sttProviderResolved") == "funasr-local",
          f"transcribe.sttProviderResolved=funasr-local")
    check(resp.get("status") in ("unavailable", "ok"),
          f"status in (unavailable, ok) — got {resp.get('status')!r}")
    check("Traceback" not in json.dumps(resp, ensure_ascii=False),
          "no raw stack trace in response")
    print(f"      transcribe status: {resp.get('status')!r}")
    print(f"      sttProviderLoadStatus: {resp.get('sttProviderLoadStatus')!r}")
except Exception as exc:
    _fail(f"transcribe_audio_bytes raised: {exc}")

# ── 4 / sherpa-onnx-local ────────────────────────────────────────────────────
print("\n[4/4] sherpa-onnx-local  (DRAGON_PET_STT_PROVIDER=sherpa-onnx-local)")
print("      (design-only in TASK-249; always unavailable)")
stt = reload_stt("sherpa-onnx-local")
r = stt._STT_PROVIDER_RESOLUTION
m = stt._get_provider_metadata()
check(r["requested_provider"]  == "sherpa-onnx-local",
      f"requested=sherpa-onnx-local")
check(r["resolved_provider"]   == "sherpa-onnx-local",
      f"resolved=sherpa-onnx-local")
check(r["provider_source"]     == "env",
      f"source=env")
check(r["provider_fallback_reason"] == "none",
      f"fallback_reason=none")
check(m["sttProviderResolved"]   == "sherpa-onnx-local",
      f"metadata.sttProviderResolved=sherpa-onnx-local")
check(m["sttProviderLoadStatus"] == "unavailable",
      f"loadStatus=unavailable (got {m['sttProviderLoadStatus']!r})")

print("      Calling transcribe_audio_bytes() with silence WAV ...")
try:
    resp = stt.transcribe_audio_bytes(WAV, mime_type="audio/wav", language="zh")
    check(resp.get("status") == "unavailable",
          f"transcribe status=unavailable (got {resp.get('status')!r})")
    check("sttProviderResolved" in resp,
          "transcribe response includes sttProviderResolved")
    check(resp.get("sttProviderResolved") == "sherpa-onnx-local",
          f"transcribe.sttProviderResolved=sherpa-onnx-local")
    check("Traceback" not in json.dumps(resp, ensure_ascii=False),
          "no raw stack trace in response")
    print(f"      transcribe status: {resp.get('status')!r}")
    print(f"      sttProviderLoadStatus: {resp.get('sttProviderLoadStatus')!r}")
except Exception as exc:
    _fail(f"transcribe_audio_bytes raised: {exc}")

# ---------------------------------------------------------------------------
# Clean up env so test leaves no side effects
# ---------------------------------------------------------------------------
os.environ.pop("DRAGON_PET_STT_PROVIDER", None)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print()
print("=" * 65)
print(f"  {_pass_count} PASS  {_fail_count} FAIL")
if _fail_count == 0:
    print("  TASK-249 STT Provider Smoke: PASS")
else:
    print("  TASK-249 STT Provider Smoke: FAIL")
print("=" * 65)
sys.exit(0 if _fail_count == 0 else 1)
