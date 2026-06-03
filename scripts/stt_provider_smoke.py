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
original_run_funasr = stt._run_funasr
stt._run_funasr = lambda b, m="audio/wav": {
    "transcript": "克里斯蒂娜你好世界", "status": "ok", "error": None,
    "funasrSidecarMode": "oneshot", "funasrSidecarWarm": False, "funasrSidecarRestarted": False,
}

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
    stt._run_funasr = original_run_funasr
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
# TASK-253: FunASR transcript normalisation smoke
# ---------------------------------------------------------------------------
print("\n[7/7] TASK-253 — FunASR transcript normalisation")
stt = reload_stt("funasr-local")

print("  [7a] _remove_cjk_spaces")
check(stt._remove_cjk_spaces("語 音 辨 識") == "語音辨識",
      "inter-CJK spaces removed")
check(stt._remove_cjk_spaces("Dragon Pet AI") == "Dragon Pet AI",
      "latin-only string unchanged")
check(stt._remove_cjk_spaces("語 音 Dragon Pet AI 辨 識") == "語音 Dragon Pet AI 辨識",
      "CJK spaces removed, Latin boundary spaces preserved")

print("  [7b] _simp_to_trad — returns (text, method) tuple")
simp_in  = "语音识别"  # 语音识别
trad_out = "語音識別"  # 語音識別
trad_text, trad_method = stt._simp_to_trad(simp_in)
check(trad_text == trad_out,
      f"simplified yuyin shibie -> traditional (method={trad_method!r})")
check(trad_method in ("opencc", "static"),
      f"method is 'opencc' or 'static' (got {trad_method!r})")
if stt._OPENCC_AVAILABLE:
    check(trad_method == "opencc",
          f"opencc installed -> method=opencc (got {trad_method!r})")
    print(f"      OpenCC available: method={trad_method!r}")
else:
    print(f"      OpenCC not installed: using static fallback")

latin_text, latin_method = stt._simp_to_trad("Dragon Pet AI")
check(latin_text == "Dragon Pet AI", "latin passthrough unchanged")

print("  [7c] _normalize_funasr_transcript")
norm_in  = "语 音 识 别"   # 语 音 识 别
norm_out = "語音識別"       # 語音識別
result = stt._normalize_funasr_transcript(norm_in)
check(result["normalizedTranscript"] == norm_out,
      f"full norm: simp+spaces -> trad+joined (got {result['normalizedTranscript']!r})")
check(result["normalizationApplied"] is True,
      "normalizationApplied=True for modified text")
check(result["cjkSpacingRemoved"] is True,
      "cjkSpacingRemoved=True")
check(result["traditionalApplied"] is True,
      "traditionalApplied=True")
check("tradMethod" in result,
      "tradMethod field present in normalize result")
steps = result["normalizationSteps"]
check(steps[0] == "cjk_space_removal" and steps[1].startswith("simp_to_trad_"),
      f"normalizationSteps order correct (got {steps!r})")

result_clean = stt._normalize_funasr_transcript("語音辨識測試")
check(result_clean["normalizationApplied"] is False,
      "normalizationApplied=False for already-normalised text")

print("  [7d] Paraformer-specific correction map entries")
aliases = [alias for alias, _ in stt._STT_CORRECTION_MAP]
check("jdden pet ai" in aliases,    "jdden pet ai in _STT_CORRECTION_MAP")
check("jden pet ai"  in aliases,    "jden pet ai in _STT_CORRECTION_MAP")
check("cloud code"   in aliases,    "cloud code in _STT_CORRECTION_MAP")
check("claud code"   in aliases,    "claud code in _STT_CORRECTION_MAP")
check("克莉莉"       in aliases,    "克莉莉 in _STT_CORRECTION_MAP")
check("t a s k"      in aliases,    "t a s k in _STT_CORRECTION_MAP")
check("task"         in aliases,    "task in _STT_CORRECTION_MAP")

print("  [7e] normalise + correct pipeline via mock _transcribe_funasr")
stt._FUNASR_AVAILABLE = True
stt._reset_model_for_tests()
original_run_funasr2 = stt._run_funasr
stt._run_funasr = lambda b, m="audio/wav": {
    "transcript": "dragon pet a i",
    "status": "ok",
    "error": None,
    "funasrSidecarMode": "oneshot", "funasrSidecarWarm": False, "funasrSidecarRestarted": False,
}
try:
    resp = stt._transcribe_funasr(WAV)
    check(resp.get("status") == "ok",
          f"mock pipeline status=ok (got {resp.get('status')!r})")
    check(resp.get("correctedTranscript") == "Dragon Pet AI",
          f"dragon pet a i → Dragon Pet AI (got {resp.get('correctedTranscript')!r})")
    check("normalizedTranscript" in resp,
          "normalizedTranscript present in response")
    check("normalizationApplied" in resp,
          "normalizationApplied present in response")
    check("cjkSpacingRemoved"    in resp,
          "cjkSpacingRemoved present in response")
    check("traditionalApplied"   in resp,
          "traditionalApplied present in response")
    check(resp.get("rawTranscript") == "dragon pet a i",
          f"rawTranscript preserved as original (got {resp.get('rawTranscript')!r})")
    check("tradMethod" in resp,
          "tradMethod present in _transcribe_funasr response")
    check(resp.get("tradMethod") in ("opencc", "static"),
          f"tradMethod in (opencc, static) (got {resp.get('tradMethod')!r})")
finally:
    stt._run_funasr = original_run_funasr2
    stt._reset_model_for_tests()

# ---------------------------------------------------------------------------
# TASK-254: Persistent FunASR sidecar manager smoke
# ---------------------------------------------------------------------------
print("\n[8/8] TASK-254 — Persistent FunASR sidecar manager")
stt = reload_stt("funasr-local")

print("  [8a] constants and script")
check(hasattr(stt, "_FUNASR_PERSISTENT_ENV"),
      "_FUNASR_PERSISTENT_ENV constant exists")
check(stt._FUNASR_PERSISTENT_ENV == "DRAGON_PET_FUNASR_PERSISTENT",
      f"_FUNASR_PERSISTENT_ENV == 'DRAGON_PET_FUNASR_PERSISTENT' (got {stt._FUNASR_PERSISTENT_ENV!r})")
check(hasattr(stt, "_FUNASR_SIDECAR_LOOP_SCRIPT"),
      "_FUNASR_SIDECAR_LOOP_SCRIPT constant exists")
check("funasr_sidecar_loop.py" in stt._FUNASR_SIDECAR_LOOP_SCRIPT,
      "_FUNASR_SIDECAR_LOOP_SCRIPT contains funasr_sidecar_loop.py")
check(_os.path.isfile(stt._FUNASR_SIDECAR_LOOP_SCRIPT),
      f"funasr_sidecar_loop.py exists on disk: {stt._FUNASR_SIDECAR_LOOP_SCRIPT}")

print("  [8b] persistent mode toggle")
_prev_env = _os.environ.get("DRAGON_PET_FUNASR_PERSISTENT")
_os.environ.pop("DRAGON_PET_FUNASR_PERSISTENT", None)
check(stt._persistent_mode_enabled() is True,
      "persistent mode enabled by default (no env var)")
_os.environ["DRAGON_PET_FUNASR_PERSISTENT"] = "false"
check(stt._persistent_mode_enabled() is False,
      "persistent mode disabled by DRAGON_PET_FUNASR_PERSISTENT=false")
_os.environ["DRAGON_PET_FUNASR_PERSISTENT"] = "true"
check(stt._persistent_mode_enabled() is True,
      "persistent mode enabled by DRAGON_PET_FUNASR_PERSISTENT=true")
if _prev_env is None:
    _os.environ.pop("DRAGON_PET_FUNASR_PERSISTENT", None)
else:
    _os.environ["DRAGON_PET_FUNASR_PERSISTENT"] = _prev_env

print("  [8c] state variables and helpers")
check(hasattr(stt, "_funasr_process"),
      "_funasr_process module-level var exists")
check(hasattr(stt, "_funasr_stdout_queue"),
      "_funasr_stdout_queue module-level var exists")
check(hasattr(stt, "_funasr_lock"),
      "_funasr_lock module-level var exists")
check(hasattr(stt, "_shutdown_funasr_process_for_tests"),
      "_shutdown_funasr_process_for_tests helper exists")
# Shutdown when no process is running must not raise
try:
    stt._shutdown_funasr_process_for_tests()
    check(True, "_shutdown_funasr_process_for_tests does not crash when no process")
except Exception as e:
    check(False, f"_shutdown_funasr_process_for_tests raised: {e}")
check(stt._funasr_process is None,
      "_funasr_process is None after shutdown")

print("  [8d] _run_funasr mock — persistent path")
_os.environ["DRAGON_PET_FUNASR_PERSISTENT"] = "true"
stt._FUNASR_AVAILABLE = True
stt._reset_model_for_tests()
original_ensure = stt._ensure_funasr_process
original_call   = stt._call_funasr_persistent
stt._ensure_funasr_process = lambda: (True, True)
stt._call_funasr_persistent = lambda b, m: {"transcript": "語音測試", "status": "ok", "error": None}
try:
    r = stt._run_funasr(WAV, "audio/wav")
    check(r.get("funasrSidecarMode") == "persistent",
          f"mock persistent: funasrSidecarMode=persistent (got {r.get('funasrSidecarMode')!r})")
    check(r.get("funasrSidecarWarm") is True,
          f"mock persistent: funasrSidecarWarm=True (got {r.get('funasrSidecarWarm')!r})")
    check(r.get("funasrSidecarRestarted") is False,
          f"mock persistent: funasrSidecarRestarted=False")
    check(r.get("status") == "ok",
          f"mock persistent: status=ok (got {r.get('status')!r})")
finally:
    stt._ensure_funasr_process = original_ensure
    stt._call_funasr_persistent = original_call
    stt._reset_model_for_tests()

print("  [8e] _run_funasr mock — oneshot fallback path")
_os.environ["DRAGON_PET_FUNASR_PERSISTENT"] = "false"
stt._FUNASR_AVAILABLE = True
stt._reset_model_for_tests()
original_sidecar2 = stt._run_funasr_sidecar
stt._run_funasr_sidecar = lambda b: {"transcript": "語音測試", "status": "ok", "error": None}
try:
    r = stt._run_funasr(WAV, "audio/wav")
    check(r.get("funasrSidecarMode") == "oneshot",
          f"disabled persistent: funasrSidecarMode=oneshot (got {r.get('funasrSidecarMode')!r})")
    check(r.get("funasrSidecarWarm") is False,
          f"disabled persistent: funasrSidecarWarm=False")
finally:
    stt._run_funasr_sidecar = original_sidecar2
    stt._reset_model_for_tests()

print("  [8f] one-shot sidecar still exists (backward-compat)")
check(hasattr(stt, "_run_funasr_sidecar"),
      "_run_funasr_sidecar one-shot function still present")
check(hasattr(stt, "_FUNASR_SIDECAR_SCRIPT"),
      "_FUNASR_SIDECAR_SCRIPT still present")
check(_os.path.isfile(stt._FUNASR_SIDECAR_SCRIPT),
      "funasr_sidecar_transcribe.py still exists")

# Restore env
_os.environ.pop("DRAGON_PET_FUNASR_PERSISTENT", None)

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
    print("  TASK-249/250/253/253rev/254 STT Provider Smoke: PASS")
else:
    print("  TASK-249/250/253/253rev/254 STT Provider Smoke: FAIL")
print("=" * 65)
sys.exit(0 if _fail_count == 0 else 1)
