"""
TASK-249/250 STT Provider Smoke — direct module test.

Tests all 4 provider scenarios by reloading app.stt.stt_service with
different DRAGON_PET_STT_PROVIDER env values.  Does NOT require uvicorn
or port 8000 — the module-level resolver is the thing being tested.

TASK-250 additions: _parse_funasr_result parser tests + _FUNASR_HOTWORDS checks
+ mock transcription test.

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
check(m["sttProviderLoadStatus"] in ("unavailable", "not_loaded", "loaded"),
      f"loadStatus in (unavailable, not_loaded, loaded) — got {m['sttProviderLoadStatus']!r}")

print("      Calling transcribe_audio_bytes() with silence WAV ...")
try:
    resp = stt.transcribe_audio_bytes(WAV, mime_type="audio/wav", language="zh")
    check("sttProviderResolved" in resp,
          "transcribe response includes sttProviderResolved")
    check(resp.get("sttProviderResolved") == "funasr-local",
          f"transcribe.sttProviderResolved=funasr-local")
    check(resp.get("status") in ("unavailable", "ok", "empty"),
          f"status in (unavailable, ok, empty) — got {resp.get('status')!r}")
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
# TASK-250 parser unit smoke
# ---------------------------------------------------------------------------
print("\n[5/5] TASK-250 — FunASR parser + hotwords + mock transcription")
stt = reload_stt("funasr-local")

print("  [5a] _parse_funasr_result parser")
check(stt._parse_funasr_result([{"text": "你好"}, {"text": "世界"}]) == "你好世界",
      "list[dict{text}] joins correctly")
check(stt._parse_funasr_result({"text": "單段"}) == "單段",
      "dict{text} returns text")
check(stt._parse_funasr_result("字串直接") == "字串直接",
      "str passthrough")
check(stt._parse_funasr_result([]) == "",
      "empty list returns ''")
check(stt._parse_funasr_result(None) == "",
      "None returns ''")
check(stt._parse_funasr_result({"score": 0.9}) == "",
      "dict missing 'text' returns ''")

print("  [5b] _FUNASR_HOTWORDS constant")
check(hasattr(stt, "_FUNASR_HOTWORDS"),
      "_FUNASR_HOTWORDS constant exists")
hw = getattr(stt, "_FUNASR_HOTWORDS", "")
check(isinstance(hw, str) and len(hw) > 0,
      "_FUNASR_HOTWORDS is non-empty string")
check("克莉絲蒂娜" in hw,
      "_FUNASR_HOTWORDS includes 克莉絲蒂娜")
check("Dragon Pet AI" in hw,
      "_FUNASR_HOTWORDS includes Dragon Pet AI")
check("Claude Code" in hw,
      "_FUNASR_HOTWORDS includes Claude Code")

print("  [5c] mock transcription with correction (TASK-251 sidecar mock)")

stt._FUNASR_AVAILABLE = True
stt._reset_model_for_tests()
original_sidecar = stt._run_funasr_sidecar
stt._run_funasr_sidecar = lambda b: {"transcript": "克里斯蒂娜你好世界", "status": "ok", "error": None}

try:
    resp = stt._transcribe_funasr(WAV)
    check(resp.get("status") == "ok",
          f"mock transcribe status=ok (got {resp.get('status')!r})")
    check(resp.get("correctedTranscript") == "克莉絲蒂娜你好世界",
          f"correction applied: 克里斯蒂娜→克莉絲蒂娜 (got {resp.get('correctedTranscript')!r})")
    check(resp.get("correctionApplied") is True,
          "correctionApplied=True")
    check("sttProviderResolved" in resp,
          "provider metadata present on mock ok result")
finally:
    stt._run_funasr_sidecar = original_sidecar
    stt._reset_model_for_tests()

# ---------------------------------------------------------------------------
# TASK-251 sidecar availability check
# ---------------------------------------------------------------------------
import os as _os
print("\n[6/6] TASK-251 — FunASR sidecar availability check")
stt = reload_stt("funasr-local")

check(hasattr(stt, "_FUNASR_PYTHON_ENV"),
      "_FUNASR_PYTHON_ENV constant exists")
check(stt._FUNASR_PYTHON_ENV == "DRAGON_PET_FUNASR_PYTHON",
      "_FUNASR_PYTHON_ENV == 'DRAGON_PET_FUNASR_PYTHON'")
check(hasattr(stt, "_FUNASR_SIDECAR_SCRIPT"),
      "_FUNASR_SIDECAR_SCRIPT constant exists")
check("funasr_sidecar_transcribe.py" in stt._FUNASR_SIDECAR_SCRIPT,
      "_FUNASR_SIDECAR_SCRIPT contains funasr_sidecar_transcribe.py")

py_path = stt._resolve_funasr_python()
sidecar_script = stt._FUNASR_SIDECAR_SCRIPT
py_exists = _os.path.isfile(py_path)
script_exists = _os.path.isfile(sidecar_script)

check(script_exists,
      f"sidecar script exists: {sidecar_script}")
check(stt._FUNASR_AVAILABLE == py_exists,
      f"_FUNASR_AVAILABLE={stt._FUNASR_AVAILABLE} matches python exists={py_exists}")

if py_exists:
    print(f"      .venv-funasr python FOUND: {py_path}")
    print(f"      sidecar is USABLE — DRAGON_PET_STT_PROVIDER=funasr-local will call sidecar")
else:
    print(f"      .venv-funasr python NOT found: {py_path}")
    print(f"      Set DRAGON_PET_FUNASR_PYTHON or run scripts/create-funasr-venv.ps1")
    print(f"      funasr-local will return status=unavailable until python is found")

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
    print("  TASK-249/250 STT Provider Smoke: PASS")
else:
    print("  TASK-249/250 STT Provider Smoke: FAIL")
print("=" * 65)
sys.exit(0 if _fail_count == 0 else 1)
