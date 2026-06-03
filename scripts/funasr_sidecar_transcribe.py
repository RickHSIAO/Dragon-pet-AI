"""
TASK-251: FunASR sidecar transcription script.

Run with the dedicated .venv-funasr Python; receives raw audio bytes on stdin,
writes a single-line JSON result to stdout, then exits.

Never writes audio to disk. Uses sys.stdin.buffer for binary input.

Exit codes (match funasr_probe.py conventions):
  0  success        JSON on stdout, status "ok" or "empty"
  1  import_error   funasr/modelscope not installed in this venv
  2  load_error     AutoModel("paraformer-zh") failed to load
  3  infer_error    model.generate raised

JSON output schema:
  {"transcript": str, "status": "ok"|"empty"|"error", "error": str|null}

Usage (from repo root):
  .venv-funasr\\Scripts\\python.exe scripts\\funasr_sidecar_transcribe.py < audio.wav
Or via the backend sidecar bridge (TASK-251): audio bytes piped through stdin.
"""
from __future__ import annotations

import io
import json
import sys

_HOTWORDS = (
    "克莉絲蒂娜 Dragon Pet AI Claude Code CodeX Whisper faster-whisper "
    "語音辨識 語音輸入 對話模式 桌面寵物"
)


def _parse_result(raw_result) -> str:
    """Mirror of stt_service._parse_funasr_result — robust multi-format FunASR output parser."""
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


def _write_result(result: dict) -> None:
    sys.stdout.write(json.dumps(result, ensure_ascii=False))
    sys.stdout.write("\n")
    sys.stdout.flush()


def main() -> None:
    # Step 1: import funasr
    try:
        from funasr import AutoModel  # type: ignore  # noqa: PLC0415
    except ImportError as exc:
        _write_result({"transcript": "", "status": "error", "error": f"import_failed: {exc}"})
        sys.exit(1)

    # Step 2: load model
    try:
        model = AutoModel(model="paraformer-zh", device="cpu", disable_update=True)
    except Exception as exc:  # noqa: BLE001
        _write_result({
            "transcript": "", "status": "error",
            "error": f"load_failed: {str(exc)[:100]}",
        })
        sys.exit(2)

    # Step 3: read audio bytes from stdin and transcribe
    try:
        audio_bytes = sys.stdin.buffer.read()
        if not audio_bytes:
            _write_result({"transcript": "", "status": "empty", "error": None})
            sys.exit(0)

        audio_buf = io.BytesIO(audio_bytes)
        try:
            result = model.generate(input=audio_buf, batch_size_s=300, hotword=_HOTWORDS)
        except TypeError:
            audio_buf.seek(0)
            result = model.generate(input=audio_buf, batch_size_s=300)

        transcript = _parse_result(result)
        if not transcript:
            _write_result({"transcript": "", "status": "empty", "error": None})
        else:
            _write_result({"transcript": transcript, "status": "ok", "error": None})
        sys.exit(0)

    except Exception as exc:  # noqa: BLE001
        _write_result({"transcript": "", "status": "error", "error": str(exc)[:100]})
        sys.exit(3)


if __name__ == "__main__":
    main()
