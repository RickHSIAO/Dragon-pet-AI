"""
TASK-254: Persistent FunASR sidecar loop.

Loads paraformer-zh once at startup, then serves JSON transcription requests from stdin.
Model stays warm between calls — eliminates cold-start latency on second and subsequent requests.
Never exits until a shutdown request or stdin closes.

Protocol
--------
Startup → stdout: {"type":"ready","status":"ok"}
           stdout: {"type":"ready","status":"error","error":"..."}  (then exits)

Request ← stdin:  {"type":"transcribe","requestId":"<uuid>","audioBase64":"<b64>","mimeType":"audio/wav"}
Response → stdout: {"type":"result","requestId":"<uuid>","status":"ok|empty|error","transcript":"...","error":null|"..."}

Shutdown ← stdin: {"type":"shutdown"}

Safety rules
------------
- Never writes raw audio to disk.
- Never outputs raw stack traces on stdout (stderr only).
- All stdout lines are valid single-line JSON objects.
- sys.stdout is redirected to sys.stderr during model import/load to suppress progress noise.
  The _PROTO_BUF saves the real stdout binary buffer for protocol messages.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import sys

# ── Protocol I/O setup ────────────────────────────────────────────────────────
# Save the real stdout binary buffer before any potential redirect.
_PROTO_BUF = sys.stdout.buffer


def _write(msg: dict) -> None:
    """Write a single protocol JSON line to the real stdout."""
    _PROTO_BUF.write((json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8"))
    _PROTO_BUF.flush()


# ── Result parser (mirrors stt_service._parse_funasr_result) ──────────────────
def _parse_result(raw_result) -> str:
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


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--hotwords", default="", help="Hotword string passed to paraformer-zh")
    args, _ = parser.parse_known_args()
    hotwords: str = args.hotwords

    # Redirect Python-level stdout to stderr so that funasr/modelscope
    # progress messages do not pollute our JSON protocol stream.
    sys.stdout = sys.stderr  # type: ignore[assignment]

    # Import funasr
    try:
        from funasr import AutoModel  # type: ignore  # noqa: PLC0415
    except ImportError as exc:
        _write({"type": "ready", "status": "error", "error": f"import_failed: {str(exc)[:100]}"})
        sys.exit(1)

    # Load model
    try:
        model = AutoModel(model="paraformer-zh", device="cpu", disable_update=True)
    except Exception as exc:  # noqa: BLE001
        _write({"type": "ready", "status": "error", "error": f"load_failed: {str(exc)[:100]}"})
        sys.exit(2)

    # Signal ready — model is warm
    _write({"type": "ready", "status": "ok"})

    # ── Request loop ──────────────────────────────────────────────────────────
    # Read from the real stdin binary buffer, decoded as UTF-8 text.
    stdin_text = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

    for raw_line in stdin_text:
        raw_line = raw_line.strip()
        if not raw_line:
            continue

        try:
            req = json.loads(raw_line)
        except json.JSONDecodeError:
            continue

        req_type = req.get("type")
        request_id = req.get("requestId", "")

        if req_type == "shutdown":
            break

        if req_type != "transcribe":
            continue

        audio_b64 = req.get("audioBase64", "")
        try:
            audio_bytes = base64.b64decode(audio_b64)
            if not audio_bytes:
                _write({
                    "type": "result", "requestId": request_id,
                    "status": "empty", "transcript": "", "error": None,
                })
                continue

            audio_buf = io.BytesIO(audio_bytes)
            try:
                result = model.generate(
                    input=audio_buf,
                    batch_size_s=300,
                    hotword=hotwords if hotwords else None,
                )
            except TypeError:
                audio_buf.seek(0)
                result = model.generate(input=audio_buf, batch_size_s=300)

            transcript = _parse_result(result)
            if transcript:
                _write({
                    "type": "result", "requestId": request_id,
                    "status": "ok", "transcript": transcript, "error": None,
                })
            else:
                _write({
                    "type": "result", "requestId": request_id,
                    "status": "empty", "transcript": "", "error": None,
                })

        except Exception as exc:  # noqa: BLE001
            _write({
                "type": "result", "requestId": request_id,
                "status": "error", "transcript": "",
                "error": str(exc)[:100],
            })


if __name__ == "__main__":
    main()
