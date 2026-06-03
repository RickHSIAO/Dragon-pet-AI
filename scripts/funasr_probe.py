"""
TASK-250: FunASR / Paraformer probe — verifies the full dependency + model chain.

Exit codes:
  0  usable    — import OK, model loaded, transcription returned a result
  1  missing   — funasr or modelscope package not installed
  2  load_fail — import OK but AutoModel("paraformer-zh") failed to load
  3  infer_fail — model loaded but model.generate() raised an exception

Run from repo root (backend venv activated):
    python scripts/funasr_probe.py

Or specify the venv python explicitly:
    backend\\.venv\\Scripts\\python.exe scripts\\funasr_probe.py
"""

import struct
import sys
import wave
import io

PROBE_LABEL = "[funasr_probe]"


def _make_silence_wav(duration_secs: float = 0.5, sample_rate: int = 16000) -> bytes:
    """Return a minimal PCM WAV of silence — enough for model.generate() to accept."""
    n_frames = int(sample_rate * duration_secs)
    pcm_data = b"\x00\x00" * n_frames  # 16-bit silence
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    return buf.getvalue()


def step_check_import() -> object:
    print(f"{PROBE_LABEL} step 1/3 — checking funasr + modelscope imports ...", flush=True)
    try:
        import funasr  # noqa: F401
        import modelscope  # noqa: F401
        print(f"{PROBE_LABEL}   funasr OK, modelscope OK", flush=True)
        return funasr
    except ImportError as exc:
        print(f"{PROBE_LABEL}   FAIL: {exc}", flush=True)
        print(f"{PROBE_LABEL}   Install: pip install funasr modelscope", flush=True)
        sys.exit(1)


def step_load_model():
    print(f"{PROBE_LABEL} step 2/3 — loading AutoModel(paraformer-zh) ...", flush=True)
    print(f"{PROBE_LABEL}   (first run downloads ~500 MB to ModelScope cache)", flush=True)
    try:
        from funasr import AutoModel  # type: ignore
        model = AutoModel(
            model="paraformer-zh",
            device="cpu",
            disable_update=True,
        )
        print(f"{PROBE_LABEL}   model loaded OK: {type(model).__name__}", flush=True)
        return model
    except Exception as exc:
        print(f"{PROBE_LABEL}   FAIL: {exc}", flush=True)
        sys.exit(2)


def step_transcribe(model) -> None:
    print(f"{PROBE_LABEL} step 3/3 — running model.generate() with silence WAV ...", flush=True)
    wav_bytes = _make_silence_wav()
    audio_buf = io.BytesIO(wav_bytes)
    try:
        result = model.generate(input=audio_buf, batch_size_s=300)
        print(f"{PROBE_LABEL}   generate() returned: {result!r}", flush=True)
        print(f"{PROBE_LABEL}   result type: {type(result).__name__}", flush=True)
        print(f"{PROBE_LABEL}   OK — FunASR is usable", flush=True)
    except Exception as exc:
        print(f"{PROBE_LABEL}   FAIL: {exc}", flush=True)
        sys.exit(3)


if __name__ == "__main__":
    print(f"{PROBE_LABEL} FunASR probe starting (TASK-250)", flush=True)
    step_check_import()
    model = step_load_model()
    step_transcribe(model)
    print(f"{PROBE_LABEL} all steps passed — exit 0 (usable)", flush=True)
    sys.exit(0)
