"""
TASK-167B: STT transcription service -- local Whisper, no external API.

Design boundaries:
- Uses faster-whisper (local) when installed; safe no-op fallback if absent.
- No raw audio is persisted to disk.
- No always-listening, wake-word, TTS, screen capture, or vision.
- No external network calls.
- Returns {"transcript": str, "status": "ok" | "unavailable" | "empty" | "error"}.
"""

import base64
import io
import json
import logging
import os
import pathlib
import queue
import re
import subprocess
import threading
import time
import uuid
from typing import Any

try:
    import opencc as _opencc_lib
    _OPENCC_AVAILABLE: bool = True
except ImportError:
    _opencc_lib = None  # type: ignore[assignment]
    _OPENCC_AVAILABLE: bool = False

logger = logging.getLogger(__name__)

_WHISPER_AVAILABLE: bool = False
_whisper_model: Any = None
# TASK-245: STT provider name surfaced in diagnostics
_STT_PROVIDER = "faster-whisper-local"

# TASK-246: configurable model via DRAGON_PET_STT_MODEL env var — safe fallback to "tiny"
_STT_ALLOWED_MODELS = frozenset({"tiny", "base", "small"})
_STT_DEFAULT_MODEL = "tiny"
_STT_MODEL_ENV = "DRAGON_PET_STT_MODEL"

# TASK-249: configurable provider via DRAGON_PET_STT_PROVIDER env var
_STT_PROVIDER_ENV = "DRAGON_PET_STT_PROVIDER"
_STT_ALLOWED_PROVIDERS = frozenset({"faster-whisper-local", "funasr-local", "sherpa-onnx-local"})
_STT_DEFAULT_PROVIDER = "faster-whisper-local"
# Design notes for each candidate (surfaced in sttProviderCandidateNotes diagnostics field)
_STT_PROVIDER_CANDIDATE_NOTES: dict = {
    "faster-whisper-local": "production; default fallback",
    "funasr-local": (
        "TASK-251 sidecar / dedicated venv; "
        "calls .venv-funasr Python via subprocess (stdin audio bytes → stdout JSON); "
        "set DRAGON_PET_FUNASR_PYTHON to override python path; "
        "paraformer-zh served from ModelScope cache (~500 MB on first download)"
    ),
    "sherpa-onnx-local": "evaluation candidate; design-only in TASK-249/250 — not yet implemented",
}

# TASK-251: FunASR sidecar — dedicated venv Python path configuration.
# Default points to .venv-funasr at repo root (Windows Scripts path).
# Override with DRAGON_PET_FUNASR_PYTHON env var for non-standard installs.
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent
_FUNASR_PYTHON_ENV = "DRAGON_PET_FUNASR_PYTHON"
_FUNASR_PYTHON_DEFAULT = str(_REPO_ROOT / ".venv-funasr" / "Scripts" / "python.exe")
_FUNASR_SIDECAR_SCRIPT = str(_REPO_ROOT / "scripts" / "funasr_sidecar_transcribe.py")


def _resolve_funasr_python() -> str:
    """Return the Python executable for the funasr sidecar venv.

    Priority: DRAGON_PET_FUNASR_PYTHON env var → .venv-funasr/Scripts/python.exe (default).
    """
    from_env = os.environ.get(_FUNASR_PYTHON_ENV, "").strip()
    return from_env if from_env else _FUNASR_PYTHON_DEFAULT


def _resolve_stt_model_name() -> dict:
    """
    Resolve the STT model name from DRAGON_PET_STT_MODEL env var.

    Resolved once at process start — restart the app/backend to pick up env changes.
    Falls back to 'tiny' on invalid or missing value; never crashes.

    Returns dict with keys:
        requested_model  -- raw env value (or default when env is unset)
        resolved_model   -- the model name that will actually be loaded
        model_source     -- "env" | "default" | "fallback"
        fallback_reason  -- "invalid_model" | "none"
    """
    requested = os.environ.get(_STT_MODEL_ENV, "").strip()
    if not requested:
        return {
            "requested_model": _STT_DEFAULT_MODEL,
            "resolved_model": _STT_DEFAULT_MODEL,
            "model_source": "default",
            "fallback_reason": "none",
        }
    if requested in _STT_ALLOWED_MODELS:
        return {
            "requested_model": requested,
            "resolved_model": requested,
            "model_source": "env",
            "fallback_reason": "none",
        }
    logger.warning(
        "TASK-246: invalid %s=%r, falling back to %r. Allowed: %s",
        _STT_MODEL_ENV, requested, _STT_DEFAULT_MODEL,
        ", ".join(sorted(_STT_ALLOWED_MODELS)),
    )
    return {
        "requested_model": requested,
        "resolved_model": _STT_DEFAULT_MODEL,
        "model_source": "fallback",
        "fallback_reason": "invalid_model",
    }


def _resolve_stt_provider() -> dict:
    """
    Resolve the STT provider from DRAGON_PET_STT_PROVIDER env var.

    Resolved once at process start — restart required to pick up env changes.
    Falls back to 'faster-whisper-local' on invalid or missing value; never crashes.

    Returns dict with keys:
        requested_provider       -- raw env value (or default when env is unset)
        resolved_provider        -- the provider that will actually be used
        provider_source          -- "env" | "default" | "fallback"
        provider_fallback_reason -- "invalid_provider" | "none"
    """
    requested = os.environ.get(_STT_PROVIDER_ENV, "").strip()
    if not requested:
        return {
            "requested_provider": _STT_DEFAULT_PROVIDER,
            "resolved_provider": _STT_DEFAULT_PROVIDER,
            "provider_source": "default",
            "provider_fallback_reason": "none",
        }
    if requested in _STT_ALLOWED_PROVIDERS:
        return {
            "requested_provider": requested,
            "resolved_provider": requested,
            "provider_source": "env",
            "provider_fallback_reason": "none",
        }
    logger.warning(
        "TASK-249: invalid %s=%r, falling back to %r. Allowed: %s",
        _STT_PROVIDER_ENV, requested, _STT_DEFAULT_PROVIDER,
        ", ".join(sorted(_STT_ALLOWED_PROVIDERS)),
    )
    return {
        "requested_provider": requested,
        "resolved_provider": _STT_DEFAULT_PROVIDER,
        "provider_source": "fallback",
        "provider_fallback_reason": "invalid_provider",
    }


# Resolved at process start — restart required to pick up env changes
_STT_MODEL_RESOLUTION: dict = _resolve_stt_model_name()
_STT_MODEL_NAME: str = _STT_MODEL_RESOLUTION["resolved_model"]

_STT_PROVIDER_RESOLUTION: dict = _resolve_stt_provider()
_STT_RESOLVED_PROVIDER: str = _STT_PROVIDER_RESOLUTION["resolved_provider"]
logger.info(
    "[stt_service] STT provider resolved=%r  source=%r  requested=%r  fallback_reason=%r",
    _STT_RESOLVED_PROVIDER,
    _STT_PROVIDER_RESOLUTION["provider_source"],
    _STT_PROVIDER_RESOLUTION["requested_provider"],
    _STT_PROVIDER_RESOLUTION["provider_fallback_reason"],
)


def _detect_whisper() -> bool:
    """Check whether faster-whisper is importable without loading the model."""
    try:
        import faster_whisper  # noqa: F401  # type: ignore
        return True
    except ImportError:
        return False


_WHISPER_AVAILABLE = _detect_whisper()

# Load status — updated by _load_model(); initialized based on availability
_STT_MODEL_LOAD_STATUS: str = "not_loaded" if _WHISPER_AVAILABLE else "unavailable"
_STT_MODEL_LOAD_ERROR: str | None = None


def _load_model() -> Any:
    """
    Lazily load the resolved faster-whisper model on first use.
    Updates _STT_MODEL_LOAD_STATUS and _STT_MODEL_LOAD_ERROR as side-effects.
    Returns None if unavailable or if loading fails.
    """
    global _whisper_model, _STT_MODEL_LOAD_STATUS, _STT_MODEL_LOAD_ERROR
    if _whisper_model is not None:
        return _whisper_model
    if not _WHISPER_AVAILABLE:
        _STT_MODEL_LOAD_STATUS = "unavailable"
        return None
    try:
        from faster_whisper import WhisperModel  # type: ignore
        _whisper_model = WhisperModel(_STT_MODEL_NAME, device="cpu", compute_type="int8")
        _STT_MODEL_LOAD_STATUS = "loaded"
        _STT_MODEL_LOAD_ERROR = None
        logger.info("TASK-246: faster-whisper %r model loaded.", _STT_MODEL_NAME)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "TASK-246: Failed to load faster-whisper model %r: %s", _STT_MODEL_NAME, exc
        )
        _STT_MODEL_LOAD_STATUS = "error"
        _STT_MODEL_LOAD_ERROR = str(exc)[:100]  # truncated — no raw stack trace
        _whisper_model = None
    return _whisper_model


# TASK-251: FunASR sidecar — availability check: does the dedicated venv Python exist?
def _detect_funasr_sidecar() -> bool:
    """Check whether the .venv-funasr sidecar Python executable exists."""
    return os.path.isfile(_resolve_funasr_python())


_FUNASR_AVAILABLE: bool = _detect_funasr_sidecar()
# Load status — updated by _transcribe_funasr() on first call; initialized based on availability
_FUNASR_LOAD_STATUS: str = "not_loaded" if _FUNASR_AVAILABLE else "unavailable"
_FUNASR_LOAD_ERROR: str | None = None

# TASK-250: hotword list surfaced in diagnostics and passed to the sidecar.
_FUNASR_HOTWORDS: str = (
    "克莉絲蒂娜 Dragon Pet AI Claude Code CodeX Whisper faster-whisper "
    "語音辨識 語音輸入 對話模式 桌面寵物"
)


def _run_funasr_sidecar(audio_bytes: bytes) -> dict:
    """
    TASK-251: Invoke the funasr sidecar subprocess with audio bytes on stdin.

    The sidecar runs inside .venv-funasr (or DRAGON_PET_FUNASR_PYTHON) and returns
    a single-line JSON result on stdout:
      {"transcript": str, "status": "ok"|"empty"|"error", "error": str|null}

    Raises
    ------
    subprocess.TimeoutExpired   if sidecar does not complete within 300 s
    json.JSONDecodeError        if stdout is not valid JSON
    ValueError                  if stdout is empty (sidecar crashed before writing)
    """
    py_exec = _resolve_funasr_python()
    proc = subprocess.run(
        [py_exec, _FUNASR_SIDECAR_SCRIPT],
        input=audio_bytes,
        capture_output=True,
        timeout=300,
    )
    stdout_text = proc.stdout.decode("utf-8", errors="replace")
    # funasr/modelscope may write progress text to stdout before our JSON line;
    # find the last line that looks like a JSON object.
    json_line = ""
    for line in reversed(stdout_text.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            json_line = line
            break
    if not json_line:
        stderr_snippet = proc.stderr.decode("utf-8", errors="replace")[:200]
        logger.warning(
            "TASK-251: sidecar no JSON in stdout exit=%d stdout_tail=%r stderr=%r",
            proc.returncode, stdout_text[-300:], stderr_snippet,
        )
        raise ValueError(f"sidecar_no_json exit={proc.returncode}")
    return json.loads(json_line)


# ---------------------------------------------------------------------------
# TASK-254: Persistent FunASR sidecar manager
# ---------------------------------------------------------------------------

# Env var to enable/disable persistent mode.  Default: true.
# Set DRAGON_PET_FUNASR_PERSISTENT=false to fall back to one-shot for every call.
_FUNASR_PERSISTENT_ENV = "DRAGON_PET_FUNASR_PERSISTENT"

# Path to the persistent loop sidecar script (TASK-254).
_FUNASR_SIDECAR_LOOP_SCRIPT = str(_REPO_ROOT / "scripts" / "funasr_sidecar_loop.py")

# Module-level persistent-process state.
_funasr_process: "subprocess.Popen[bytes] | None" = None
_funasr_stdout_queue: queue.Queue = queue.Queue()
_funasr_stdout_thread: "threading.Thread | None" = None
_funasr_lock = threading.Lock()


def _persistent_mode_enabled() -> bool:
    """Return True unless DRAGON_PET_FUNASR_PERSISTENT is set to a falsy value."""
    val = os.environ.get(_FUNASR_PERSISTENT_ENV, "true").lower().strip()
    return val not in ("false", "0", "no", "off")


def _funasr_stdout_reader(proc: "subprocess.Popen[bytes]", q: queue.Queue) -> None:
    """Daemon thread: reads stdout lines from the sidecar and enqueues them."""
    try:
        for raw_line in proc.stdout:  # type: ignore[union-attr]
            line = raw_line.rstrip(b"\r\n").decode("utf-8", errors="replace")
            if line:
                q.put(line)
    except Exception:  # noqa: BLE001
        pass
    finally:
        q.put(None)  # sentinel: stream closed / process died


def _drain_stdout_queue() -> None:
    """Discard all pending items from the shared stdout queue."""
    while True:
        try:
            _funasr_stdout_queue.get_nowait()
        except queue.Empty:
            break


def _kill_funasr_process() -> None:
    """
    Attempt graceful shutdown then hard-kill the persistent sidecar.
    Resets _funasr_process / _funasr_stdout_thread to None.
    Must be called with _funasr_lock held.
    """
    global _funasr_process, _funasr_stdout_thread
    if _funasr_process is not None:
        try:
            if _funasr_process.poll() is None:
                try:
                    _funasr_process.stdin.write(  # type: ignore[union-attr]
                        (json.dumps({"type": "shutdown"}) + "\n").encode("utf-8")
                    )
                    _funasr_process.stdin.flush()  # type: ignore[union-attr]
                    _funasr_process.wait(timeout=3)
                except Exception:  # noqa: BLE001
                    _funasr_process.kill()
        except Exception:  # noqa: BLE001
            pass
        _funasr_process = None
    _funasr_stdout_thread = None
    _drain_stdout_queue()


def _ensure_funasr_process() -> "tuple[bool, bool]":
    """
    Ensure the persistent sidecar is running and ready.
    Returns (success, was_warm).
      was_warm=True  — process was already alive when this call arrived.
      was_warm=False — a new process was started.
    Must be called with _funasr_lock held.
    """
    global _funasr_process, _funasr_stdout_thread

    # Fast path: process is alive.
    if _funasr_process is not None and _funasr_process.poll() is None:
        return True, True

    _funasr_process = None  # clear dead reference

    py_path = _resolve_funasr_python()
    if not os.path.isfile(py_path):
        return False, False
    if not os.path.isfile(_FUNASR_SIDECAR_LOOP_SCRIPT):
        logger.warning("TASK-254: loop script not found: %s", _FUNASR_SIDECAR_LOOP_SCRIPT)
        return False, False

    _drain_stdout_queue()

    try:
        proc: "subprocess.Popen[bytes]" = subprocess.Popen(
            [py_path, _FUNASR_SIDECAR_LOOP_SCRIPT, "--hotwords", _FUNASR_HOTWORDS],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("TASK-254: Popen persistent sidecar failed: %s", exc)
        return False, False

    t = threading.Thread(
        target=_funasr_stdout_reader,
        args=(proc, _funasr_stdout_queue),
        daemon=True,
        name="funasr-stdout-reader",
    )
    t.start()

    # Wait for the ready signal (120 s — first-run model download can be slow).
    deadline = time.monotonic() + 120.0
    ready = False
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            line = _funasr_stdout_queue.get(timeout=min(remaining, 2.0))
        except queue.Empty:
            if proc.poll() is not None:
                break
            continue
        if line is None:
            break
        try:
            msg = json.loads(line)
            if msg.get("type") == "ready" and msg.get("status") == "ok":
                ready = True
                break
        except json.JSONDecodeError:
            continue

    if not ready:
        logger.warning("TASK-254: persistent sidecar did not become ready (120 s timeout)")
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:  # noqa: BLE001
            proc.kill()
        return False, False

    _funasr_process = proc
    _funasr_stdout_thread = t
    logger.info("TASK-254: persistent funasr sidecar ready (pid=%d)", proc.pid)
    return True, False


def _call_funasr_persistent(audio_bytes: bytes, mime_type: str) -> dict:
    """
    Send one transcription request to the running persistent sidecar and wait for the result.
    Must be called with _funasr_lock held and _funasr_process alive.

    Raises
    ------
    subprocess.TimeoutExpired  — no result within 60 s
    ValueError                 — sidecar process died or stdout closed mid-request
    """
    req_id = str(uuid.uuid4())
    request = (json.dumps({
        "type": "transcribe",
        "requestId": req_id,
        "audioBase64": base64.b64encode(audio_bytes).decode("ascii"),
        "mimeType": mime_type,
    }) + "\n").encode("utf-8")

    _funasr_process.stdin.write(request)  # type: ignore[union-attr]
    _funasr_process.stdin.flush()  # type: ignore[union-attr]

    deadline = time.monotonic() + 60.0
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise subprocess.TimeoutExpired("persistent_sidecar_request", 60)
        try:
            line = _funasr_stdout_queue.get(timeout=min(remaining, 1.0))
        except queue.Empty:
            if _funasr_process.poll() is not None:  # type: ignore[union-attr]
                raise ValueError("persistent_sidecar_died_during_request")
            continue
        if line is None:
            raise ValueError("persistent_sidecar_stdout_closed")
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("type") == "result" and msg.get("requestId") == req_id:
            return {
                "transcript": msg.get("transcript", ""),
                "status": msg.get("status", "error"),
                "error": msg.get("error"),
            }


def _run_funasr(audio_bytes: bytes, mime_type: str) -> dict:
    """
    TASK-254: FunASR call dispatcher.

    Uses persistent sidecar loop when enabled; falls back to one-shot sidecar on failure.
    Augments result dict with:
      funasrSidecarMode      — "persistent" | "oneshot"
      funasrSidecarWarm      — True if model was already loaded at call time
      funasrSidecarRestarted — True if the sidecar was restarted during this call

    Raises subprocess.TimeoutExpired or Exception on unrecoverable one-shot failure.
    """
    if not _persistent_mode_enabled():
        r = _run_funasr_sidecar(audio_bytes)
        r.update({"funasrSidecarMode": "oneshot",
                   "funasrSidecarWarm": False,
                   "funasrSidecarRestarted": False})
        return r

    use_oneshot = False
    result: "dict | None" = None
    was_warm = False
    restarted = False

    with _funasr_lock:
        ok, was_warm = _ensure_funasr_process()
        if not ok:
            use_oneshot = True
        else:
            try:
                result = _call_funasr_persistent(audio_bytes, mime_type)
            except Exception as exc:  # noqa: BLE001
                logger.warning("TASK-254: persistent call raised: %s", exc)
                _kill_funasr_process()
                use_oneshot = True
            else:
                if result.get("status") == "error":
                    # Attempt one restart before giving up.
                    _kill_funasr_process()
                    ok2, _ = _ensure_funasr_process()
                    if ok2:
                        restarted = True
                        try:
                            result = _call_funasr_persistent(audio_bytes, mime_type)
                        except Exception as exc2:  # noqa: BLE001
                            logger.warning("TASK-254: restart call raised: %s", exc2)
                            _kill_funasr_process()
                            use_oneshot = True
                        else:
                            if result.get("status") == "error":
                                _kill_funasr_process()
                                use_oneshot = True
                    else:
                        use_oneshot = True

    if use_oneshot:
        logger.info("TASK-254: persistent sidecar unavailable — falling back to one-shot")
        r = _run_funasr_sidecar(audio_bytes)  # may raise
        r.update({"funasrSidecarMode": "oneshot",
                   "funasrSidecarWarm": False,
                   "funasrSidecarRestarted": False})
        return r

    assert result is not None
    result.update({
        "funasrSidecarMode": "persistent",
        "funasrSidecarWarm": was_warm,
        "funasrSidecarRestarted": restarted,
    })
    return result


def _shutdown_funasr_process_for_tests() -> None:
    """Kill the persistent sidecar and reset all state. Only for test isolation."""
    with _funasr_lock:
        _kill_funasr_process()


def _get_model_metadata() -> dict:
    """Return current faster-whisper model resolution and load status metadata for diagnostics."""
    return {
        "provider": _STT_PROVIDER,
        "model": _STT_MODEL_NAME,
        "requestedModel": _STT_MODEL_RESOLUTION["requested_model"],
        "resolvedModel": _STT_MODEL_RESOLUTION["resolved_model"],
        "modelSource": _STT_MODEL_RESOLUTION["model_source"],
        "modelLoadStatus": _STT_MODEL_LOAD_STATUS,
        "modelLoadError": _STT_MODEL_LOAD_ERROR,
    }


def _get_provider_metadata() -> dict:
    """Return TASK-249 provider resolution and load status metadata for diagnostics."""
    resolved = _STT_RESOLVED_PROVIDER
    if resolved == "funasr-local":
        load_status = _FUNASR_LOAD_STATUS
        load_error = _FUNASR_LOAD_ERROR
    elif resolved == "sherpa-onnx-local":
        # Design-only in TASK-249 — always unavailable
        load_status = "unavailable"
        load_error = "sherpa-onnx-local not yet implemented (TASK-249 design-only)"
    else:
        # faster-whisper-local
        load_status = _STT_MODEL_LOAD_STATUS
        load_error = _STT_MODEL_LOAD_ERROR
    return {
        "sttProviderRequested": _STT_PROVIDER_RESOLUTION["requested_provider"],
        "sttProviderResolved": resolved,
        "sttProviderSource": _STT_PROVIDER_RESOLUTION["provider_source"],
        "sttProviderLoadStatus": load_status,
        "sttProviderLoadError": load_error,
        "sttProviderFallbackReason": _STT_PROVIDER_RESOLUTION["provider_fallback_reason"],
        "sttProviderCandidateNotes": _STT_PROVIDER_CANDIDATE_NOTES.get(resolved, ""),
    }


# TASK-247/248: STT transcript correction — deterministic phrase/hotword correction map.
# Design rules:
#   - Longer / more specific phrases come first to prevent partial-match shadowing.
#   - Compound forms (e.g. "faster whisper") come before their components (e.g. "Whisper")
#     to avoid corrupting already-corrected compound targets.
#   - More specific multi-word forms (e.g. "克勞德 code") come before standalone components
#     (e.g. "克勞德") to avoid leaving two-step corrections stranded.
#   - All entries are conservative: only well-known acoustic confusions in this project.
_STT_CORRECTION_MAP: list[tuple[str, str]] = [
    # -------------------------------------------------------------------------
    # TASK-247: Phrase-level corrections — project vocabulary acoustic confusions
    # -------------------------------------------------------------------------
    ("中位與英編輯", "中文語音辨識"),
    ("中文語音編輯", "中文語音辨識"),
    ("中文語音邊記", "中文語音辨識"),
    ("語音編輯測試", "語音辨識測試"),
    ("語音邊記測試", "語音辨識測試"),

    # -------------------------------------------------------------------------
    # TASK-247 + TASK-248: 克莉絲蒂娜 — extended alias list
    # Canonical: 克莉絲蒂娜
    # -------------------------------------------------------------------------
    ("克里斯蒂娜",  "克莉絲蒂娜"),  # TASK-247
    ("克莉斯蒂娜",  "克莉絲蒂娜"),  # TASK-247
    ("克麗絲蒂娜",  "克莉絲蒂娜"),  # TASK-247
    ("克利斯蒂娜",  "克莉絲蒂娜"),
    ("克里斯提娜",  "克莉絲蒂娜"),
    ("克莉絲提娜",  "克莉絲蒂娜"),
    ("可莉絲蒂娜",  "克莉絲蒂娜"),
    ("葛莉絲蒂娜",  "克莉絲蒂娜"),
    ("格莉絲蒂娜",  "克莉絲蒂娜"),
    ("格里斯蒂娜",  "克莉絲蒂娜"),
    ("可麗絲蒂娜",  "克莉絲蒂娜"),
    ("克麗絲提娜",  "克莉絲蒂娜"),
    ("克莉絲緹娜",  "克莉絲蒂娜"),
    ("克里斯緹娜",  "克莉絲蒂娜"),
    ("克莉斯緹娜",  "克莉絲蒂娜"),
    ("克莉絲蒂那",  "克莉絲蒂娜"),
    ("克里斯蒂那",  "克莉絲蒂娜"),
    ("克莉絲蒂納",  "克莉絲蒂娜"),
    ("克里斯蒂納",  "克莉絲蒂娜"),

    # -------------------------------------------------------------------------
    # TASK-248: faster-whisper — compound before standalone to avoid partial corruption
    # Note: "whisper" (standalone lowercase) is intentionally omitted — it is a substring
    # of the canonical "faster-whisper" target and would corrupt it post-correction.
    # -------------------------------------------------------------------------
    ("faster whisper",   "faster-whisper"),
    ("faster Whisper",   "faster-whisper"),
    ("威斯伯",           "Whisper"),

    # -------------------------------------------------------------------------
    # TASK-248: Claude Code — multi-word form before standalone to allow single-pass match
    # -------------------------------------------------------------------------
    ("克勞德 code",   "Claude Code"),
    ("克勞德 Code",   "Claude Code"),
    ("Claude code",   "Claude Code"),
    ("克勞德",        "Claude"),

    # -------------------------------------------------------------------------
    # TASK-248: CodeX
    # -------------------------------------------------------------------------
    ("扣得 X",   "CodeX"),
    ("Code X",   "CodeX"),
    ("code x",   "CodeX"),
    ("Codex",    "CodeX"),

    # -------------------------------------------------------------------------
    # TASK-248: Dragon Pet AI — more specific forms first
    # -------------------------------------------------------------------------
    ("Dragon Pet A I",   "Dragon Pet AI"),
    ("DragonPet AI",     "Dragon Pet AI"),
    ("Dragon pet AI",    "Dragon Pet AI"),
    ("dragon pet AI",    "Dragon Pet AI"),
    ("dragon pet ai",    "Dragon Pet AI"),
    ("龍寵 AI",          "Dragon Pet AI"),
    ("龍寵AI",           "Dragon Pet AI"),

    # -------------------------------------------------------------------------
    # TASK-248: Common feature terms
    # -------------------------------------------------------------------------
    ("語音輸人",    "語音輸入"),
    ("語音書入",    "語音輸入"),
    ("對話糢式",    "對話模式"),
    ("對話模式式",  "對話模式"),
    ("桌面重物",    "桌面寵物"),
    ("桌面從物",    "桌面寵物"),

    # -------------------------------------------------------------------------
    # TASK-253: Paraformer-specific acoustic variants
    # Dragon Pet AI — Paraformer romanisation variants (compound before standalone)
    # -------------------------------------------------------------------------
    ("jdden pet ai",     "Dragon Pet AI"),
    ("jden pet ai",      "Dragon Pet AI"),
    ("dragon pet a i",   "Dragon Pet AI"),

    # Claude Code — Paraformer romanisation variants
    ("cloud code",   "Claude Code"),
    ("claud code",   "Claude Code"),

    # CodeX
    ("codex",   "CodeX"),

    # TASK — Paraformer spells out letters or lowercases
    ("t a s k",   "TASK"),
    ("task",      "TASK"),

    # 克莉莉 — Paraformer short-form collapse of 克莉絲蒂娜
    ("克莉莉",   "克莉絲蒂娜"),
]


def correct_transcript_text(raw_text: str) -> dict:
    """
    Apply deterministic phrase/hotword correction to a raw STT transcript.

    TASK-247/248 design boundaries:
    - No LLM rewrite.  No cloud API.  No new IPC.
    - Safe, conservative corrections only — known acoustic confusions and project vocabulary.
    - Returns rawTranscript unchanged so callers can surface both original and corrected text
      in diagnostics without losing the raw evidence.
    - Empty input passes through as-is (correctionApplied=False).

    Returns
    -------
    dict with keys:
        rawTranscript        -- original input, unmodified
        correctedTranscript  -- text after applying phrase map (equals rawTranscript if no match)
        correctionApplied    -- True when at least one substitution was made
        correctionMode       -- always "safe_dictionary" for this layer
        correctionReason     -- pipe-separated reason tags ("phrase_map" | "none")
        matchedAlias         -- first alias that triggered a correction (empty if none)
        canonicalTerm        -- canonical target for the first matched alias (empty if none)
        correctionCandidates -- reserved for future use; always empty list in this task
    """
    if not raw_text:
        return {
            "rawTranscript": "",
            "correctedTranscript": "",
            "correctionApplied": False,
            "correctionMode": "safe_dictionary",
            "correctionReason": "none",
            "matchedAlias": "",
            "canonicalTerm": "",
            "correctionCandidates": [],
        }
    corrected = raw_text
    applied_reasons: list[str] = []
    first_matched_alias: str = ""
    first_canonical_term: str = ""
    for src, dst in _STT_CORRECTION_MAP:
        if src in corrected:
            corrected = corrected.replace(src, dst)
            if "phrase_map" not in applied_reasons:
                applied_reasons.append("phrase_map")
            if not first_matched_alias:
                first_matched_alias = src
                first_canonical_term = dst
    applied = corrected != raw_text
    reason_str = "|".join(applied_reasons) if applied_reasons else "none"
    return {
        "rawTranscript": raw_text,
        "correctedTranscript": corrected,
        "correctionApplied": applied,
        "correctionMode": "safe_dictionary",
        "correctionReason": reason_str,
        "matchedAlias": first_matched_alias if applied else "",
        "canonicalTerm": first_canonical_term if applied else "",
        "correctionCandidates": [],
    }


def _reset_model_for_tests() -> None:
    """Reset cached models and load status — only for test isolation. Not for production use."""
    global _whisper_model, _STT_MODEL_LOAD_STATUS, _STT_MODEL_LOAD_ERROR
    global _FUNASR_LOAD_STATUS, _FUNASR_LOAD_ERROR
    _whisper_model = None
    _STT_MODEL_LOAD_STATUS = "not_loaded" if _WHISPER_AVAILABLE else "unavailable"
    _STT_MODEL_LOAD_ERROR = None
    _FUNASR_LOAD_STATUS = "not_loaded" if _FUNASR_AVAILABLE else "unavailable"
    _FUNASR_LOAD_ERROR = None


def _parse_funasr_result(raw_result) -> str:
    """
    TASK-250: Robust FunASR output parser.

    FunASR generate() may return:
      list[dict{text, ...}]  — standard paraformer-zh output
      dict{text, ...}        — single-segment result
      str                    — raw transcript string (some model variants)
      empty list / None      — no speech detected

    Returns the joined transcript string (stripped), or "" if no text found.
    Does not raise; all paths are safe.
    """
    if not raw_result:
        return ""
    if isinstance(raw_result, str):
        return raw_result.strip()
    if isinstance(raw_result, dict):
        return str(raw_result.get("text", "")).strip()
    if isinstance(raw_result, list):
        parts: list[str] = []
        for item in raw_result:
            if isinstance(item, dict):
                text = item.get("text", "")
                if text:
                    parts.append(str(text))
            elif isinstance(item, str) and item:
                parts.append(item)
        return "".join(parts).strip()
    return str(raw_result).strip()


# ---------------------------------------------------------------------------
# TASK-253: FunASR transcript normalisation
# ---------------------------------------------------------------------------

# Matches a single ASCII space that sits between two CJK Unified Ideograph codepoints.
# Paraformer-zh frequently inserts spaces between characters in its output.
_CJK_SPACE_RE = re.compile(
    r"(?<=[一-鿿㐀-䶿豈-﫿])"
    r" "
    r"(?=[一-鿿㐀-䶿豈-﫿])"
)

# Fallback: static simplified→traditional character map used when OpenCC is unavailable.
# Covers only chars commonly emitted by Paraformer-zh that differ from Traditional Chinese.
_SIMP_CHAR_MAP: dict[str, str] = {
    "语": "語", "识": "識", "别": "別", "测": "測", "试": "試",
    "对": "對", "话": "話", "宠": "寵", "帮": "幫", "输": "輸",
    "这": "這", "现": "現", "简": "簡", "体": "體", "开": "開",
    "们": "們", "时": "時", "会": "會", "说": "說", "来": "來",
}
_SIMP_TRAD_TABLE = str.maketrans(_SIMP_CHAR_MAP)

# Lazy-initialised OpenCC converter (s2tw = Simplified → Traditional Taiwan).
# None until first call; avoids loading the conversion tables at import time.
_opencc_converter: Any = None


def _remove_cjk_spaces(text: str) -> str:
    return _CJK_SPACE_RE.sub("", text)


def _get_opencc_converter() -> Any:
    """Return a cached OpenCC("s2tw") instance, or None if opencc is not installed."""
    global _opencc_converter
    if not _OPENCC_AVAILABLE:
        return None
    if _opencc_converter is None:
        try:
            _opencc_converter = _opencc_lib.OpenCC("s2tw")
        except Exception:  # noqa: BLE001
            return None
    return _opencc_converter


def _simp_to_trad(text: str) -> tuple[str, str]:
    """
    Convert simplified Chinese to Traditional Chinese.

    Returns (converted_text, method) where method is one of:
      "opencc"  — OpenCC s2tw was used
      "static"  — static _SIMP_CHAR_MAP fallback was used
    """
    converter = _get_opencc_converter()
    if converter is not None:
        return converter.convert(text), "opencc"
    return text.translate(_SIMP_TRAD_TABLE), "static"


def _normalize_funasr_transcript(text: str) -> dict:
    """
    TASK-253/rev: Apply Paraformer-specific normalisation before phrase correction.

    Pipeline order:
      1. CJK inter-character space removal
      2. Simplified→Traditional conversion (OpenCC s2tw preferred; static map fallback)

    Returns a dict with the normalised text and per-step metadata.
    Does not modify the correction map; callers chain this before correct_transcript_text().
    """
    steps: list[str] = []
    after_spaces = _remove_cjk_spaces(text)
    cjk_spacing_removed = after_spaces != text
    if cjk_spacing_removed:
        steps.append("cjk_space_removal")

    after_trad, trad_method = _simp_to_trad(after_spaces)
    traditional_applied = after_trad != after_spaces
    if traditional_applied:
        steps.append(f"simp_to_trad_{trad_method}")

    normalised = after_trad
    return {
        "normalizedTranscript": normalised,
        "normalizationApplied": bool(steps),
        "normalizationSteps": steps,
        "cjkSpacingRemoved": cjk_spacing_removed,
        "traditionalApplied": traditional_applied,
        "tradMethod": trad_method,
    }


def _transcribe_funasr(
    audio_bytes: bytes,
    mime_type: str = "audio/webm",
    language: str | None = None,
) -> dict:
    """
    TASK-251: FunASR Paraformer transcription via sidecar subprocess.

    Invokes .venv-funasr Python with audio bytes on stdin; reads JSON result from stdout.
    No raw audio persistence to disk; no funasr import in the backend venv.
    TASK-247/248 correction layer applies when transcription succeeds.
    """
    global _FUNASR_LOAD_STATUS, _FUNASR_LOAD_ERROR

    if not _FUNASR_AVAILABLE:
        return {
            "transcript": "",
            "status": "unavailable",
            **_get_model_metadata(),
            **_get_provider_metadata(),
        }

    try:
        sidecar_result = _run_funasr(audio_bytes, mime_type)
    except subprocess.TimeoutExpired:
        _FUNASR_LOAD_STATUS = "error"
        _FUNASR_LOAD_ERROR = "sidecar_timeout"
        logger.warning("TASK-254: funasr sidecar timed out mime=%s", mime_type)
        return {
            "transcript": "",
            "status": "error",
            **_get_model_metadata(),
            **_get_provider_metadata(),
        }
    except Exception as exc:  # noqa: BLE001
        _FUNASR_LOAD_STATUS = "error"
        _FUNASR_LOAD_ERROR = str(exc)[:100]
        logger.warning("TASK-254: funasr sidecar error mime=%s exc=%s", mime_type, exc)
        return {
            "transcript": "",
            "status": "error",
            **_get_model_metadata(),
            **_get_provider_metadata(),
        }

    sidecar_status = sidecar_result.get("status", "error")
    transcript = sidecar_result.get("transcript", "")
    sidecar_error = sidecar_result.get("error")

    if sidecar_error:
        logger.warning("TASK-251: sidecar reported error: %s", sidecar_error)

    if sidecar_status == "error":
        _FUNASR_LOAD_STATUS = "error"
        _FUNASR_LOAD_ERROR = (sidecar_error or "sidecar_error")[:100]
        return {
            "transcript": "",
            "status": "error",
            **_get_model_metadata(),
            **_get_provider_metadata(),
        }

    if sidecar_status == "empty" or not transcript:
        _FUNASR_LOAD_STATUS = "loaded"
        _FUNASR_LOAD_ERROR = None
        return {
            "transcript": "",
            "status": "empty",
            **_get_model_metadata(),
            **_get_provider_metadata(),
        }

    _FUNASR_LOAD_STATUS = "loaded"
    _FUNASR_LOAD_ERROR = None
    norm = _normalize_funasr_transcript(transcript)
    correction = correct_transcript_text(norm["normalizedTranscript"])
    return {
        "transcript": correction["correctedTranscript"],
        "status": "ok",
        **_get_model_metadata(),
        **_get_provider_metadata(),
        "detectedLanguage": language or "zh",
        "rawTranscript": transcript,
        "normalizedTranscript": norm["normalizedTranscript"],
        "normalizationApplied": norm["normalizationApplied"],
        "normalizationSteps": norm["normalizationSteps"],
        "cjkSpacingRemoved": norm["cjkSpacingRemoved"],
        "traditionalApplied": norm["traditionalApplied"],
        "tradMethod": norm["tradMethod"],
        "correctedTranscript": correction["correctedTranscript"],
        "correctionApplied": correction["correctionApplied"],
        "correctionMode": correction["correctionMode"],
        "correctionReason": correction["correctionReason"],
        "matchedAlias": correction["matchedAlias"],
        "canonicalTerm": correction["canonicalTerm"],
        "funasrSidecarMode": sidecar_result.get("funasrSidecarMode", "oneshot"),
        "funasrSidecarWarm": sidecar_result.get("funasrSidecarWarm", False),
        "funasrSidecarRestarted": sidecar_result.get("funasrSidecarRestarted", False),
    }


def transcribe_audio_bytes(
    audio_bytes: bytes,
    mime_type: str = "audio/webm",
    language: str | None = None,
) -> dict:
    """
    Transcribe raw audio bytes using the resolved local STT provider.

    Provider is selected by DRAGON_PET_STT_PROVIDER env var (default: faster-whisper-local).
    Falls back to faster-whisper-local for invalid provider values.
    TASK-247/248 correction layer applies regardless of provider.

    Parameters
    ----------
    audio_bytes : bytes
        Raw audio content (any format the provider supports: webm, wav, ogg, mp4 ...).
    mime_type : str
        MIME type hint -- not used for routing, only for logging.
    language : str | None
        Language hint (e.g. "zh"). None = auto-detect.

    Returns
    -------
    dict with keys:
        "transcript"    : str   -- transcribed text (empty string on failure/empty audio)
        "status"        : str   -- one of "ok", "unavailable", "empty", "error"

    TASK-246 model metadata (present for ok / unavailable / error):
        "provider"        : str
        "model"           : str
        "requestedModel"  : str
        "resolvedModel"   : str
        "modelSource"     : str   -- "env" | "default" | "fallback"
        "modelLoadStatus" : str   -- "loaded" | "unavailable" | "error" | "not_loaded"
        "modelLoadError"  : str | None

    TASK-247/248 transcript correction (present for ok only):
        "rawTranscript"      : str
        "correctedTranscript": str
        "correctionApplied"  : bool
        "correctionMode"     : str  -- "safe_dictionary"
        "correctionReason"   : str  -- "phrase_map" | "none"
        "matchedAlias"       : str
        "canonicalTerm"      : str

    TASK-249 provider selection metadata (present for ok / unavailable / error):
        "sttProviderRequested"     : str
        "sttProviderResolved"      : str
        "sttProviderSource"        : str   -- "env" | "default" | "fallback"
        "sttProviderLoadStatus"    : str   -- "loaded" | "unavailable" | "error" | "not_loaded"
        "sttProviderLoadError"     : str | None
        "sttProviderFallbackReason": str   -- "invalid_provider" | "none"
        "sttProviderCandidateNotes": str
    """
    # Empty-bytes check is provider-independent.
    if not audio_bytes:
        return {"transcript": "", "status": "empty"}

    resolved = _STT_RESOLVED_PROVIDER
    if resolved == "funasr-local":
        return _transcribe_funasr(audio_bytes, mime_type=mime_type, language=language)
    if resolved == "sherpa-onnx-local":
        # TASK-249: design-only in this release — clean unavailable, no crash.
        return {
            "transcript": "",
            "status": "unavailable",
            **_get_model_metadata(),
            **_get_provider_metadata(),
        }

    # Default path: faster-whisper-local
    if not _WHISPER_AVAILABLE:
        return {
            "transcript": "",
            "status": "unavailable",
            **_get_model_metadata(),
            **_get_provider_metadata(),
        }

    model = _load_model()
    if model is None:
        return {
            "transcript": "",
            "status": "unavailable",
            **_get_model_metadata(),
            **_get_provider_metadata(),
        }

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
        # TASK-247: apply deterministic correction layer before returning.
        correction = correct_transcript_text(transcript)
        return {
            "transcript": correction["correctedTranscript"],
            "status": "ok",
            **_get_model_metadata(),
            **_get_provider_metadata(),
            "detectedLanguage": detected_language,
            "rawTranscript": correction["rawTranscript"],
            "correctedTranscript": correction["correctedTranscript"],
            "correctionApplied": correction["correctionApplied"],
            "correctionMode": correction["correctionMode"],
            "correctionReason": correction["correctionReason"],
            "matchedAlias": correction["matchedAlias"],
            "canonicalTerm": correction["canonicalTerm"],
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("TASK-167B: STT error mime=%s exc=%s", mime_type, exc)
        return {
            "transcript": "",
            "status": "error",
            **_get_model_metadata(),
            **_get_provider_metadata(),
        }
