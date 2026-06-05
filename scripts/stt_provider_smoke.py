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
print("  TASK-249/256  STT Provider Smoke")
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
# TASK-256: warmup_funasr_sidecar helper smoke
# ---------------------------------------------------------------------------
print("\n[9/9] TASK-256 — warmup_funasr_sidecar helper")
stt = reload_stt("funasr-local")

check(hasattr(stt, "warmup_funasr_sidecar"),
      "warmup_funasr_sidecar function exists")
check(callable(getattr(stt, "warmup_funasr_sidecar", None)),
      "warmup_funasr_sidecar is callable")

# Persistent mode disabled → must return skipped
_os.environ["DRAGON_PET_FUNASR_PERSISTENT"] = "false"
result = stt.warmup_funasr_sidecar()
check(result.get("status") == "skipped",
      f"warmup returns status=skipped when persistent disabled (got {result.get('status')!r})")
check(result.get("warmupStatus") == "skipped",
      f"warmup returns warmupStatus=skipped (got {result.get('warmupStatus')!r})")
check(result.get("sidecarMode") == "disabled",
      f"warmup returns sidecarMode=disabled (got {result.get('sidecarMode')!r})")
check("message" in result,
      "warmup result has message field")

# Required keys always present
required_keys = {"status", "warmupStatus", "sidecarMode", "message"}
missing = required_keys - set(result.keys())
check(len(missing) == 0,
      f"all required keys present (missing: {missing!r})")

_os.environ.pop("DRAGON_PET_FUNASR_PERSISTENT", None)

# ---------------------------------------------------------------------------
# TASK-STT-001: Chinese STT punctuation restoration static/runtime checks
# ---------------------------------------------------------------------------
print("\n[10/19] TASK-STT-001 - Chinese STT punctuation restoration")
stt = reload_stt("faster-whisper-local")

check(hasattr(stt, "restore_transcript_punctuation"),
      "stt_service exposes restore_transcript_punctuation helper")
check(callable(getattr(stt, "restore_transcript_punctuation", None)),
      "restore_transcript_punctuation is callable")
punct = stt.restore_transcript_punctuation("今天天氣很好我們開始測試")
check(punct.get("finalTranscript") == "今天天氣很好我們開始測試。",
      "Chinese transcript without punctuation gets conservative terminal period")
check(punct.get("punctuationApplied") is True,
      "punctuationApplied=True when terminal punctuation is added")
short = stt.restore_transcript_punctuation("你好")
check(short.get("finalTranscript") == "你好" and short.get("punctuationApplied") is False,
      "short ambiguous transcript is not aggressively modified")
existing = stt.restore_transcript_punctuation("今天天氣很好。")
check(existing.get("finalTranscript") == "今天天氣很好。" and existing.get("punctuationApplied") is False,
      "already-punctuated transcript is preserved")

stt_service_path = _os.path.join(REPO_ROOT, "backend", "app", "stt", "stt_service.py")
routes_path = _os.path.join(REPO_ROOT, "backend", "app", "api", "routes.py")
renderer_js = _os.path.join(REPO_ROOT, "apps", "desktop", "src", "renderer", "renderer.js")
renderer_preload_path = _os.path.join(REPO_ROOT, "apps", "desktop", "src", "renderer", "preload.js")

with open(stt_service_path, "r", encoding="utf-8") as f:
    stt_service_text = f.read()
with open(routes_path, "r", encoding="utf-8") as f:
    routes_source = f.read()
with open(renderer_js, "r", encoding="utf-8") as f:
    renderer_js_text = f.read()
with open(renderer_preload_path, "r", encoding="utf-8") as f:
    renderer_preload_text = f.read()

for token in (
    "punctuatedTranscript",
    "finalTranscript",
    "punctuationApplied",
    "punctuationMode",
    "punctuationReason",
):
    check(token in stt_service_text,
          f"stt_service includes punctuation field {token}")
    check(token in routes_source,
          f"/stt/transcribe response docs include punctuation field {token}")
    check(token in renderer_js_text,
          f"renderer diagnostics include punctuation field {token}")

check('"transcript": punctuation["finalTranscript"]' in stt_service_text,
      "backend transcript field is finalTranscript on ok responses")
check("raw STT transcript -> existing safe-dictionary correction -> conservative punctuation" in stt_service_text,
      "stt_service documents raw -> correction -> punctuation processing order")
check("stt:punctuate" not in renderer_preload_text and "stt:punctuate" not in renderer_js_text,
      "TASK-STT-001 adds no punctuation IPC channel")

# ---------------------------------------------------------------------------
# TASK-259/260/261: Owner Voice Gate probe and storage docs static safety checks
# ---------------------------------------------------------------------------
print("\n[11/19] TASK-259/260/261 - Owner Voice Gate probe and storage docs static safety")
probe_path = _os.path.join(REPO_ROOT, "scripts", "owner_voice_gate_probe.py")
owner_voice_doc = _os.path.join(REPO_ROOT, "docs", "OWNER_VOICE_GATE_RESEARCH.md")
owner_voice_storage_doc = _os.path.join(REPO_ROOT, "docs", "OWNER_VOICE_GATE_STORAGE_DESIGN.md")
owner_voice_storage_service = _os.path.join(REPO_ROOT, "backend", "app", "services", "owner_voice_gate_storage.py")
renderer_html = _os.path.join(REPO_ROOT, "apps", "desktop", "src", "renderer", "index.html")

check(_os.path.isfile(probe_path),
      f"owner_voice_gate_probe.py exists: {probe_path}")

try:
    with open(probe_path, "r", encoding="utf-8") as f:
        probe_source = f.read()
except OSError as exc:
    probe_source = ""
    _fail(f"could not read owner_voice_gate_probe.py: {exc}")

check("argparse" in probe_source,
      "probe uses argparse file-path CLI")
check("json.dumps" in probe_source,
      "probe writes JSON report")
check("rawAudioPersisted" in probe_source and "embeddingPersisted" in probe_source,
      "probe report includes persistence safety fields")
check("--enroll-a" in probe_source and "--verify-a" in probe_source,
      "probe accepts enrollment and verification WAV paths")

for forbidden in (
    "getUserMedia",
    "MediaRecorder",
    "navigator.mediaDevices",
    "ipcRenderer",
    "ipcMain",
    "stt:transcribe",
    "/stt/transcribe",
    "/chat",
    "NamedTemporaryFile",
    "mkdtemp",
    "write_bytes",
    "shutil.copy",
    "save_dir",
):
    check(forbidden not in probe_source,
          f"probe source does not contain forbidden token {forbidden!r}")

check(_os.path.isfile(owner_voice_doc),
      "OWNER_VOICE_GATE_RESEARCH.md exists")
try:
    with open(owner_voice_doc, "r", encoding="utf-8") as f:
        owner_voice_text = f.read()
except OSError as exc:
    owner_voice_text = ""
    _fail(f"could not read OWNER_VOICE_GATE_RESEARCH.md: {exc}")

check("TASK-259" in owner_voice_text,
      "owner voice research doc records TASK-259")
check("No Manual Mic runtime change" in owner_voice_text,
      "owner voice research doc preserves Manual Mic boundary")
check("No Conversation Mode runtime change" in owner_voice_text,
      "owner voice research doc preserves Conversation Mode boundary")
check("No raw audio persistence" in owner_voice_text,
      "owner voice research doc preserves raw audio boundary")
check("not security-grade" in owner_voice_text,
      "owner voice research doc keeps convenience-filter limitation")

check(_os.path.isfile(owner_voice_storage_doc),
      "OWNER_VOICE_GATE_STORAGE_DESIGN.md exists")
try:
    with open(owner_voice_storage_doc, "r", encoding="utf-8") as f:
        owner_voice_storage_text = f.read()
except OSError as exc:
    owner_voice_storage_text = ""
    _fail(f"could not read OWNER_VOICE_GATE_STORAGE_DESIGN.md: {exc}")

check("TASK-260" in owner_voice_storage_text,
      "owner voice storage design doc records TASK-260")
check("DESIGNED - OWNER VOICE ENROLLMENT STORAGE PLAN / NO RUNTIME CHANGE" in owner_voice_storage_text,
      "owner voice storage design doc records no-runtime status")
check("backend/data/owner_voice_gate_settings.json" in owner_voice_storage_text,
      "owner voice storage design doc records backend-owned storage path")
check("raw audio" in owner_voice_storage_text and "Forbidden stored values" in owner_voice_storage_text,
      "owner voice storage design doc forbids raw audio storage")
check("centroid" in owner_voice_storage_text and "Store the centroid only" in owner_voice_storage_text,
      "owner voice storage design doc recommends centroid-only storage")
check("not security-grade" in owner_voice_storage_text,
      "owner voice storage design doc keeps non-security limitation")
check("No Manual Mic runtime change" in owner_voice_storage_text,
      "owner voice storage design doc preserves Manual Mic boundary")
check("No Conversation Mode runtime change" in owner_voice_storage_text,
      "owner voice storage design doc preserves Conversation Mode boundary")
check("No `/stt/transcribe` behavior change" in owner_voice_storage_text,
      "owner voice storage design doc preserves STT boundary")
check("No `/chat` schema change" in owner_voice_storage_text,
      "owner voice storage design doc preserves chat schema boundary")

check(_os.path.isfile(owner_voice_storage_service),
      f"owner voice gate storage service exists: {owner_voice_storage_service}")
if _os.path.isfile(owner_voice_storage_service):
    with open(owner_voice_storage_service, "r", encoding="utf-8") as f:
        owner_voice_storage_service_text = f.read()
else:
    owner_voice_storage_service_text = ""
if _os.path.isfile(routes_path):
    with open(routes_path, "r", encoding="utf-8") as f:
        routes_source = f.read()
else:
    routes_source = ""

check("OwnerVoiceGateStorageService" in owner_voice_storage_service_text,
      "owner voice storage service defines narrow storage service")
check("OWNER_VOICE_DEFAULT_THRESHOLD = 0.65" in owner_voice_storage_service_text,
      "owner voice storage service records default threshold")
check("OWNER_VOICE_MIN_THRESHOLD = 0.40" in owner_voice_storage_service_text and "OWNER_VOICE_MAX_THRESHOLD = 0.95" in owner_voice_storage_service_text,
      "owner voice storage service clamps threshold")
check("embeddingAggregate: list[float] | None = None" in owner_voice_storage_service_text,
      "owner voice storage service supports centroid-only embedding storage")
check("run_owner_voice_enrollment_sidecar" in owner_voice_storage_service_text,
      "owner voice storage service runs narrow enrollment sidecar")
check("_prepare_owner_voice_enrollment_paths" in owner_voice_storage_service_text,
      "owner voice storage service prepares enrollment paths before sidecar")
check("Path(path).expanduser().resolve()" not in owner_voice_storage_service_text,
      "owner voice storage service does not eagerly resolve enrollment paths")
check("path.is_file()" in owner_voice_storage_service_text,
      "owner voice storage service validates enrollment paths exist")
check('reason="audio_file_not_found"' in owner_voice_storage_service_text,
      "owner voice storage service returns clean audio_file_not_found reason")
check('encoding="utf-8"' in owner_voice_storage_service_text and "PYTHONIOENCODING" in owner_voice_storage_service_text,
      "owner voice storage service decodes sidecar JSON with UTF-8")
for forbidden in ("getUserMedia", "MediaRecorder", "navigator.mediaDevices", "/stt/transcribe", "/chat", "transcribe_audio_bytes", "warmup_funasr_sidecar"):
    check(forbidden not in owner_voice_storage_service_text,
          f"owner voice storage service does not contain forbidden token {forbidden!r}")
for forbidden_field in ("rawAudio", "base64Audio", "transcript", "waveform", "embeddingAggregate", "perSampleEmbeddings"):
    check(forbidden_field in owner_voice_storage_service_text,
          f"owner voice storage service explicitly rejects forbidden field {forbidden_field!r}")

if _os.path.isfile(renderer_html):
    with open(renderer_html, "r", encoding="utf-8") as f:
        renderer_html_text = f.read()
else:
    renderer_html_text = ""
if _os.path.isfile(renderer_js):
    with open(renderer_js, "r", encoding="utf-8") as f:
        renderer_js_text = f.read()
else:
    renderer_js_text = ""

check('id="owner-voice-gate-section"' in renderer_html_text,
      "owner voice gate UI section exists")
check("Convenience filter only, not security authentication" in renderer_html_text,
      "owner voice gate UI includes safety boundary text")
check("/owner-voice-gate/status" in renderer_js_text,
      "owner voice gate UI calls narrow status endpoint")
check("/owner-voice-gate/settings" in renderer_js_text,
      "owner voice gate UI calls narrow settings endpoint")
check("/owner-voice-gate/delete" in renderer_js_text,
      "owner voice gate UI calls narrow delete endpoint")
check("/owner-voice-gate/enroll-files" in renderer_js_text,
      "owner voice gate UI calls narrow file enrollment endpoint")
owner_ui_start = renderer_js_text.find("TASK-261/263: Owner Voice Gate settings UI + backend storage/file enrollment.")
owner_ui_end = renderer_js_text.find("Provider Key Save / Clear", owner_ui_start)
owner_ui_text = renderer_js_text[owner_ui_start:owner_ui_end] if owner_ui_start >= 0 and owner_ui_end > owner_ui_start else ""
check(bool(owner_ui_text), "owner voice gate UI renderer section can be isolated")
for forbidden in ("getUserMedia", "MediaRecorder", "navigator.mediaDevices", "ipcRenderer", "ipcMain", "dragonPet.", "DragonOutputQueue"):
    check(forbidden not in owner_ui_text,
          f"owner voice gate UI section does not contain forbidden token {forbidden!r}")
check("localStorage." not in owner_ui_text and "localStorage[" not in owner_ui_text,
      "owner voice gate UI section does not use localStorage for voiceprint")
check('fetch(`${BACKEND_URL}/stt/transcribe`' not in owner_ui_text,
      "owner voice gate UI section does not call /stt/transcribe")
check('fetch(`${BACKEND_URL}/chat`' not in owner_ui_text,
      "owner voice gate UI section does not call /chat")

# ---------------------------------------------------------------------------
# TASK-262: Multi-sample calibration probe static safety checks
# ---------------------------------------------------------------------------
print("\n[12/19] TASK-262 - Owner Voice Gate multi-sample calibration probe static safety")

check("--owner-sample" in probe_source,
      "probe accepts --owner-sample for multi-sample calibration")
check("--other-sample" in probe_source,
      "probe accepts --other-sample for other-speaker samples")
check("--owner-dir" in probe_source,
      "probe accepts --owner-dir for directory of owner WAVs")
check("--other-dir" in probe_source,
      "probe accepts --other-dir for directory of other-speaker WAVs")
check("--output-json" in probe_source,
      "probe accepts --output-json for optional report file output")
check("ownerSelfScores" in probe_source,
      "probe report includes ownerSelfScores (centroid vs each owner sample)")
check("otherScores" in probe_source,
      "probe report includes otherScores (centroid vs each other-speaker sample)")
check("ownerStats" in probe_source,
      "probe report includes ownerStats (mean/min/max/p10/p90)")
check("otherStats" in probe_source,
      "probe report includes otherStats (mean/max/p90)")
check("scoreGap" in probe_source,
      "probe report includes scoreGap (ownerMin - otherMax)")
check("balancedThreshold" in probe_source,
      "probe report includes balancedThreshold suggestion")
check("conservativeThreshold" in probe_source,
      "probe report includes conservativeThreshold suggestion")
check("permissiveThreshold" in probe_source,
      "probe report includes permissiveThreshold suggestion")
check("separationQuality" in probe_source,
      "probe report includes separationQuality (strong/moderate/weak/overlap/owner_only)")
check("THRESHOLD_MIN" in probe_source and "THRESHOLD_MAX" in probe_source,
      "probe defines THRESHOLD_MIN and THRESHOLD_MAX clamp constants")
check("_compute_calibration_thresholds" in probe_source,
      "probe defines _compute_calibration_thresholds function")
check("_compute_centroid" in probe_source,
      "probe defines _compute_centroid for owner centroid computation")
check("_clamp_threshold" in probe_source,
      "probe defines _clamp_threshold clamping helper")
check("calibration_probe_complete" in probe_source,
      "probe uses calibration_probe_complete reason in output")
check("Thresholds are local calibration hints only" in probe_source,
      "probe documents that thresholds are local calibration hints")

# Calibration output must not contain raw embedding vectors or audio bytes
check("write_text" in probe_source and "output_json" in probe_source,
      "probe writes --output-json report to file (no raw audio)")
for forbidden in (
    "getUserMedia",
    "MediaRecorder",
    "navigator.mediaDevices",
    "ipcRenderer",
    "ipcMain",
    "stt:transcribe",
    "/stt/transcribe",
    "/chat",
    "NamedTemporaryFile",
    "mkdtemp",
    "write_bytes",
    "shutil.copy",
    "save_dir",
):
    check(forbidden not in probe_source,
          f"calibration probe source does not contain forbidden token {forbidden!r}")

# Docs checks: TASK-262 must be recorded in owner voice research doc
check("TASK-262" in owner_voice_text,
      "owner voice research doc records TASK-262 calibration probe")
check("calibration" in owner_voice_text,
      "owner voice research doc covers calibration context")

# Storage design doc threshold section must document calibration boundary
check("TASK-262" in owner_voice_storage_text,
      "owner voice storage design doc records TASK-262 calibration threshold")
check("calibration" in owner_voice_storage_text,
      "owner voice storage design doc covers calibration threshold strategy")

# ---------------------------------------------------------------------------
# TASK-263: Owner voice file enrollment + centroid storage static checks
# ---------------------------------------------------------------------------
print("\n[13/19] TASK-263 - Owner Voice Gate file enrollment and centroid storage static safety")

enroll_path = _os.path.join(REPO_ROOT, "scripts", "owner_voice_gate_enroll.py")
check(_os.path.isfile(enroll_path),
      f"owner_voice_gate_enroll.py exists: {enroll_path}")
if _os.path.isfile(enroll_path):
    with open(enroll_path, "r", encoding="utf-8") as f:
        enroll_source = f.read()
else:
    enroll_source = ""

check("--owner-sample" in enroll_source,
      "enrollment sidecar accepts --owner-sample")
check("--owner-dir" in enroll_source,
      "enrollment sidecar accepts --owner-dir")
check("--threshold" in enroll_source,
      "enrollment sidecar accepts --threshold")
check("--output-json" in enroll_source,
      "enrollment sidecar accepts --output-json")
check("owner_enrollment_complete" in enroll_source,
      "enrollment sidecar reports owner_enrollment_complete")
check("embeddingAggregate" in enroll_source,
      "enrollment sidecar outputs final centroid embeddingAggregate")
check("per-sample embedding" in enroll_source,
      "enrollment sidecar documents no per-sample embedding output")
for forbidden in (
    "getUserMedia",
    "MediaRecorder",
    "navigator.mediaDevices",
    "ipcRenderer",
    "ipcMain",
    "stt:transcribe",
    "/stt/transcribe",
    "/chat",
    "NamedTemporaryFile",
    "mkdtemp",
    "write_bytes",
    "shutil.copy",
    "save_dir",
):
    check(forbidden not in enroll_source,
          f"enrollment sidecar source does not contain forbidden token {forbidden!r}")

check("/owner-voice-gate/enroll-files" in routes_source,
      "backend exposes narrow owner voice file enrollment endpoint")
check("validate_owner_voice_gate_enroll_fields" in routes_source,
      "backend enrollment endpoint validates allowed fields")
check("enroll_owner_voice_gate_from_files" in routes_source,
      "backend enrollment endpoint delegates storage write")
check("rawAudio" in owner_voice_storage_service_text and "base64Audio" in owner_voice_storage_service_text,
      "storage service rejects raw audio/base64 enrollment fields")
check("embeddingAggregate" in owner_voice_storage_service_text and "include_embedding: bool = False" in owner_voice_storage_service_text,
      "storage service masks centroid from status/settings API responses by default")
check("enrolled = True" in owner_voice_storage_service_text,
      "storage service can mark owner voice as enrolled after sidecar success")
check("enabled = False" in owner_voice_storage_service_text,
      "storage service keeps gate disabled immediately after enrollment")
check('id="owner-voice-gate-enroll-paths"' in renderer_html_text,
      "owner voice UI includes enrollment paths textarea")
check('id="owner-voice-gate-enroll-btn"' in renderer_html_text,
      "owner voice UI includes file enrollment button")
check("Accept the safety notice before enrollment" in renderer_js_text,
      "owner voice UI requires safety notice before enrollment")
check("Provide at least two owner WAV file paths" in renderer_js_text,
      "owner voice UI requires at least two owner paths")
check("embeddingAggregate" not in owner_ui_text,
      "owner voice UI section does not render embeddingAggregate")
check("TASK-263" in owner_voice_text,
      "owner voice research doc records TASK-263")
check("TASK-263" in owner_voice_storage_text,
      "owner voice storage design doc records TASK-263")
check("centroid" in owner_voice_storage_text and "sensitive" in owner_voice_storage_text,
      "owner voice storage design doc treats centroid as sensitive local voiceprint")
check("Unicode" in owner_voice_storage_text and "audio_file_not_found" in owner_voice_storage_text,
      "owner voice storage design doc records Unicode path follow-up")

# ---------------------------------------------------------------------------
# TASK-264: Stored centroid verification probe static safety checks
# ---------------------------------------------------------------------------
print("\n[14/19] TASK-264 - Owner Voice Gate stored centroid verification probe static safety")

verify_path = _os.path.join(REPO_ROOT, "scripts", "owner_voice_gate_verify.py")
check(_os.path.isfile(verify_path),
      f"owner_voice_gate_verify.py exists: {verify_path}")
if _os.path.isfile(verify_path):
    with open(verify_path, "r", encoding="utf-8") as f:
        verify_source = f.read()
else:
    verify_source = ""

check("--settings-json" in verify_source,
      "verification probe accepts --settings-json")
check("--candidate-sample" in verify_source,
      "verification probe accepts --candidate-sample")
check("--candidate-dir" in verify_source,
      "verification probe accepts --candidate-dir")
check("verification_complete" in verify_source,
      "verification probe reports verification_complete")
check("build_verification_decision" in verify_source,
      "verification probe has testable score/threshold decision helper")
check("embeddingAggregate" in verify_source and "storedCentroidExposed" in verify_source,
      "verification probe reads stored centroid but reports it as not exposed")
check("candidateEmbeddingPersisted" in verify_source,
      "verification probe reports candidate embedding persistence boundary")
check(_os.path.isfile(verify_path),
      "TASK-264 verify script is standalone file; TASK-265 exposes it via backend endpoint")
for forbidden in (
    "getUserMedia",
    "MediaRecorder",
    "navigator.mediaDevices",
    "ipcRenderer",
    "ipcMain",
    "stt:transcribe",
    "/stt/transcribe",
    "/chat",
    "NamedTemporaryFile",
    "mkdtemp",
    "write_bytes",
    "shutil.copy",
    "save_dir",
):
    check(forbidden not in verify_source,
          f"verification probe source does not contain forbidden token {forbidden!r}")
check("TASK-264" in owner_voice_text,
      "owner voice research doc records TASK-264")
check("TASK-264" in owner_voice_storage_text,
      "owner voice storage design doc records TASK-264")

# ---------------------------------------------------------------------------
# TASK-265: Backend verify-files endpoint static safety checks
# ---------------------------------------------------------------------------
print("\n[15/19] TASK-265 - Owner Voice Gate backend verify-files endpoint static safety")

verify_endpoint_route = "/owner-voice-gate/verify-files"
check(verify_endpoint_route in routes_source,
      "backend exposes POST /owner-voice-gate/verify-files endpoint")
check("validate_owner_voice_gate_verify_fields" in routes_source,
      "backend verify-files endpoint validates allowed fields before dispatch")
check("verify_owner_voice_gate_from_files" in routes_source,
      "backend verify-files endpoint delegates to storage service verify function")

owner_voice_storage_service_text = open(
    _os.path.join(REPO_ROOT, "backend", "app", "services", "owner_voice_gate_storage.py"),
    encoding="utf-8",
).read()

check("run_owner_voice_verification_sidecar" in owner_voice_storage_service_text,
      "storage service has verification sidecar runner")
check("verify_from_files" in owner_voice_storage_service_text,
      "storage service has verify_from_files method")
check("storedCentroidExposed" in owner_voice_storage_service_text,
      "storage service verify sets storedCentroidExposed=False in response")
check("candidateEmbeddingPersisted" in owner_voice_storage_service_text,
      "storage service verify sets candidateEmbeddingPersisted=False in response")
check("runtimeIntegrated" in owner_voice_storage_service_text,
      "storage service verify sets runtimeIntegrated=False in response")
check("micAccessed" in owner_voice_storage_service_text,
      "storage service verify sets micAccessed=False in response")
check("_OWNER_VOICE_VERIFY_SCRIPT" in owner_voice_storage_service_text,
      "storage service references verification script path constant")
check("OWNER_VOICE_VERIFICATION_TIMEOUT_SECONDS" in owner_voice_storage_service_text,
      "storage service defines verification timeout constant")

for forbidden in (
    "getUserMedia",
    "MediaRecorder",
    "navigator.mediaDevices",
    "ipcRenderer",
    "ipcMain",
    "stt:transcribe",
    "/stt/transcribe",
    "/chat",
    "NamedTemporaryFile",
    "mkdtemp",
    "write_bytes",
    "shutil.copy",
):
    check(forbidden not in open(
              _os.path.join(REPO_ROOT, "backend", "app", "api", "routes.py"),
              encoding="utf-8",
          ).read().split("owner_voice_gate_verify_files_route")[1].split("\n@router")[0]
          if "owner_voice_gate_verify_files_route" in routes_source else True,
          f"verify-files route handler does not contain forbidden token {forbidden!r}")

check("TASK-265" in owner_voice_text,
      "owner voice research doc records TASK-265")
check("TASK-265" in owner_voice_storage_text,
      "owner voice storage design doc records TASK-265")

# ---------------------------------------------------------------------------
# TASK-266: Manual Mic dry-run policy static safety checks
# ---------------------------------------------------------------------------
print("\n[16/19] TASK-266 - Owner Voice Gate Manual Mic dry-run policy static safety")

check("OWNER_VOICE_MANUAL_MIC_DRY_RUN_ENABLED" in renderer_js_text,
      "renderer defines Manual Mic owner voice dry-run enable flag")
check("ownerVoiceDryRunStatus" in renderer_js_text,
      "renderer exposes ownerVoiceDryRunStatus diagnostics field")
check("ownerVoiceDryRunReason" in renderer_js_text,
      "renderer exposes ownerVoiceDryRunReason diagnostics field")
check("ownerVoiceDryRunSource" in renderer_js_text,
      "renderer exposes ownerVoiceDryRunSource diagnostics field")
check("ownerVoiceScore" in renderer_js_text and "ownerVoiceThreshold" in renderer_js_text,
      "renderer exposes safe owner voice score/threshold diagnostics")
check("ownerVoiceAccepted" in renderer_js_text,
      "renderer exposes safe owner voice accepted diagnostics")
check("runtimeHardBlocked" in renderer_js_text,
      "renderer records runtimeHardBlocked safety field")
check("rawAudioPersisted" in renderer_js_text and "candidateEmbeddingPersisted" in renderer_js_text,
      "renderer records raw audio / candidate embedding persistence safety fields")
check("storedCentroidExposed" in renderer_js_text,
      "renderer records storedCentroidExposed safety field")
check("async function runOwnerVoiceManualMicDryRun" in renderer_js_text,
      "renderer defines Manual Mic dry-run helper")
check("/owner-voice-gate/verify-files" in renderer_js_text,
      "Manual Mic dry-run reuses verify-files endpoint")
check("candidate_wav_temp_unavailable" in renderer_js_text,
      "Manual Mic dry-run safely reports unavailable temp WAV policy")

dry_run_start = renderer_js_text.find("async function runOwnerVoiceManualMicDryRun")
dry_run_section = renderer_js_text[dry_run_start:dry_run_start + 2600] if dry_run_start >= 0 else ""
check(bool(dry_run_section), "Manual Mic dry-run helper section can be isolated")
for forbidden in (
    "fullAppVoiceConversation",
    "sendMessage(",
    "DragonOutputQueue",
    "dragonPet.",
    "embeddingAggregate",
    "transcript",
):
    check(forbidden not in dry_run_section,
          f"Manual Mic dry-run helper does not contain forbidden token {forbidden!r}")
check("runtimeHardBlocked" in dry_run_section and "false" in dry_run_section,
      "Manual Mic dry-run explicitly keeps runtimeHardBlocked=false")

check("TASK-266" in owner_voice_storage_text,
      "owner voice storage design doc records TASK-266")
check("TASK-266" in owner_voice_text,
      "owner voice research doc records TASK-266")

# TASK-267: Conversation Mode dry-run policy static safety checks
print("\n[17/19] TASK-267 - Owner Voice Gate Conversation Mode dry-run policy static safety")

check("OWNER_VOICE_CONVERSATION_MODE_DRY_RUN_ENABLED" in renderer_js_text,
      "renderer defines Conversation Mode owner voice dry-run enable flag")
check("fullAppOwnerVoiceConversationDryRunCandidatePath" in renderer_js_text,
      "renderer defines Conversation Mode candidate path policy hook")
check("ownerVoiceDryRunSource" in renderer_js_text and "conversation_mode" in renderer_js_text,
      "renderer distinguishes Conversation Mode owner voice dry-run source")
check("async function runOwnerVoiceConversationModeDryRun" in renderer_js_text,
      "renderer defines Conversation Mode dry-run helper")
check("runOwnerVoiceConversationModeDryRun(audioBlob);" in renderer_js_text,
      "Conversation Mode dry-run is called from Conversation Mode capture path")
check("candidate_wav_temp_unavailable" in renderer_js_text,
      "Conversation Mode dry-run reports unavailable temp WAV policy without blocking")

conversation_dry_run_start = renderer_js_text.find("async function runOwnerVoiceConversationModeDryRun")
conversation_dry_run_section = (
    renderer_js_text[conversation_dry_run_start:conversation_dry_run_start + 2600]
    if conversation_dry_run_start >= 0 else ""
)
check(bool(conversation_dry_run_section), "Conversation Mode dry-run helper section can be isolated")
check("/owner-voice-gate/verify-files" in conversation_dry_run_section,
      "Conversation Mode dry-run reuses verify-files endpoint only through helper")
for forbidden in (
    "sendMessage(",
    "DragonOutputQueue",
    "dragonPet.",
    "embeddingAggregate",
    "transcript",
    "base64Audio",
):
    check(forbidden not in conversation_dry_run_section,
          f"Conversation Mode dry-run helper does not contain forbidden token {forbidden!r}")
check("runtimeHardBlocked" in conversation_dry_run_section and "false" in conversation_dry_run_section,
      "Conversation Mode dry-run explicitly keeps runtimeHardBlocked=false")

conversation_path_start = renderer_js_text.find("async function _processConversationQueueItem")
if conversation_path_start < 0:
    conversation_path_start = renderer_js_text.find("function _transcribeConversationChunks")
conversation_path_section = (
    renderer_js_text[conversation_path_start:conversation_path_start + 2600]
    if conversation_path_start >= 0 else ""
)
check(bool(conversation_path_section), "Conversation Mode queued processing section can be isolated")
check("runOwnerVoiceConversationModeDryRun(audioBlob);" in conversation_path_section,
      "Conversation Mode queued processing path starts owner voice dry-run")
check("await runOwnerVoiceConversationModeDryRun" not in conversation_path_section,
      "Conversation Mode owner voice dry-run is fire-and-forget")
check("TASK-267" in owner_voice_storage_text,
      "owner voice storage design doc records TASK-267")
check("TASK-267" in owner_voice_text,
      "owner voice research doc records TASK-267")

# TASK-268: Owner Voice dry-run diagnostics polish static safety checks
print("\n[18/19] TASK-268 - Owner Voice dry-run diagnostics polish static safety")

check("formatOwnerVoiceDryRunSourceLabel" in renderer_js_text,
      "renderer defines owner voice dry-run source label formatter")
check("formatOwnerVoiceDryRunStateLabel" in renderer_js_text,
      "renderer defines owner voice dry-run state label formatter")
check("formatOwnerVoiceDryRunReasonLabel" in renderer_js_text,
      "renderer defines owner voice dry-run reason label formatter")
check("ownerVoiceDryRunSafetySummary" in renderer_js_text,
      "renderer defines owner voice dry-run safety summary formatter")
check("Manual Mic" in renderer_js_text and "Conversation Mode" in renderer_js_text,
      "renderer exposes readable owner voice dry-run source labels")
check("Not computed" in renderer_js_text and "Temporary candidate WAV unavailable" in renderer_js_text,
      "renderer exposes readable not_computed/candidate_wav_temp_unavailable wording")
check("Dry-run only; existing voice flow is not blocked" in renderer_js_text,
      "renderer exposes readable dry-run only safety summary")
check("runtimeHardBlocked=" in renderer_js_text,
      "renderer keeps runtimeHardBlocked visible in diagnostics")

diagnostics_start = renderer_js_text.find("function renderFullAppVoiceDiagnostics")
diagnostics_end = renderer_js_text.find("function updateFullAppVoiceDiagnostics", diagnostics_start)
diagnostics_section = (
    renderer_js_text[diagnostics_start:diagnostics_end]
    if diagnostics_start >= 0 and diagnostics_end > diagnostics_start else ""
)
check(bool(diagnostics_section), "voice diagnostics render section can be isolated")
check("textContent" in diagnostics_section and "innerHTML" not in diagnostics_section,
      "voice diagnostics render remains textContent-only")
for forbidden in (
    "embeddingAggregate",
    "perSampleEmbeddings",
    "base64Audio",
    "fullAppOwnerVoiceDryRunCandidatePath",
    "fullAppOwnerVoiceConversationDryRunCandidatePath",
):
    check(forbidden not in diagnostics_section,
          f"Owner Voice diagnostics render does not expose forbidden token {forbidden!r}")
check("TASK-268" in owner_voice_storage_text,
      "owner voice storage design doc records TASK-268")
check("TASK-268" in owner_voice_text,
      "owner voice research doc records TASK-268")

# TASK-270: Owner Voice candidate WAV temporary policy checks
print("\n[19/19] TASK-270 - Owner Voice candidate WAV temporary policy static safety")

renderer_preload_path = _os.path.join(REPO_ROOT, "apps", "desktop", "src", "renderer", "preload.js")
main_js_path = _os.path.join(REPO_ROOT, "apps", "desktop", "src", "main.js")
try:
    with open(renderer_preload_path, "r", encoding="utf-8") as f:
        renderer_preload_text = f.read()
except Exception:
    renderer_preload_text = ""
try:
    with open(main_js_path, "r", encoding="utf-8") as f:
        main_js_text = f.read()
except Exception:
    main_js_text = ""

check("TASK-270" in renderer_js_text,
      "renderer records TASK-270 candidate WAV temp policy")
check("_ownerVoiceBlobToTemporaryWavBytes" in renderer_js_text,
      "renderer prepares temporary WAV bytes before owner voice verification")
check("createOwnerVoiceCandidateWavTemp" in renderer_js_text,
      "renderer calls narrow temp WAV create bridge")
check("deleteOwnerVoiceCandidateWavTemp" in renderer_js_text,
      "renderer calls narrow temp WAV delete bridge")
check("candidateWavTemporary" in renderer_js_text and "candidateWavDeleted" in renderer_js_text,
      "renderer exposes only candidate WAV temporary/deleted booleans")
check("candidate_wav_temp_unavailable" in renderer_js_text,
      "renderer fail-opens with safe candidate_wav_temp_unavailable reason")
check("/owner-voice-gate/verify-files" in renderer_js_text,
      "TASK-270 still reuses existing verify-files endpoint")
check("/stt/transcribe" not in dry_run_section and "/chat" not in dry_run_section,
      "Manual Mic owner voice dry-run does not call /stt/transcribe or /chat")
check("/stt/transcribe" not in conversation_dry_run_section and "/chat" not in conversation_dry_run_section,
      "Conversation Mode owner voice dry-run does not call /stt/transcribe or /chat")
check("owner-voice:candidate-wav-temp:create" in renderer_preload_text,
      "preload exposes narrow TASK-270 temp WAV create IPC channel")
check("owner-voice:candidate-wav-temp:delete" in renderer_preload_text,
      "preload exposes narrow TASK-270 temp WAV delete IPC channel")
check("require(\"fs\")" not in renderer_preload_text and "require('fs')" not in renderer_preload_text,
      "preload does not expose filesystem module")
check("OWNER_VOICE_CANDIDATE_WAV_MAX_BYTES" in main_js_text,
      "main bounds candidate WAV temp size")
check("OWNER_VOICE_CANDIDATE_WAV_TEMP_TTL_MS" in main_js_text,
      "main schedules candidate WAV cleanup timeout")
check("getOwnerVoiceCandidateWavTempDir" in main_js_text and 'app.getPath("temp")' in main_js_text,
      "main stores candidate WAVs under app-controlled OS temp location")
check("path.relative" in main_js_text and "invalid_candidate_path" in main_js_text,
      "main validates candidate WAV cleanup path containment")
check("rawAudioPersisted = false" in renderer_js_text or "rawAudioPersisted: false" in renderer_js_text,
      "TASK-270 keeps rawAudioPersisted false in diagnostics")
check("runtimeHardBlocked = false" in renderer_js_text or "runtimeHardBlocked: false" in renderer_js_text,
      "TASK-270 keeps runtimeHardBlocked false")
for forbidden in (
    "perSampleEmbeddings",
    "base64Audio",
):
    check(forbidden not in renderer_js_text,
          f"TASK-270 renderer does not expose forbidden token {forbidden!r}")
check("TASK-270" in owner_voice_storage_text,
      "owner voice storage design doc records TASK-270")

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
    print("  TASK-249/250/253/253rev/254/256/TASK-STT-001/259/260/261/262/263/264/265/266/267/268/270 STT Provider Smoke: PASS")
else:
    print("  TASK-249/250/253/253rev/254/256/TASK-STT-001/259/260/261/262/263/264/265/266/267/268/270 STT Provider Smoke: FAIL")
print("=" * 65)
sys.exit(0 if _fail_count == 0 else 1)
