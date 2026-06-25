# STT

## Purpose

STT lets the Full App and Pet Window turn local microphone input into text for
manual chat and experimental Conversation Mode. It is local-first and guarded
against common no-speech hallucination failures.

## Backend Architecture

- Main route: `POST /stt/transcribe`.
- Warmup route: `POST /stt/warmup`.
- Default language is locked to Chinese (`zh`).
- Task is transcription, not translation.
- Audio bytes are bounded and processed in memory by the route.

## Model And Provider Selection

Current committed default:

```text
provider: faster-whisper-local
model: tiny
```

Supported model candidates include `tiny`, `base`, and `small`. Runtime
selection can use a session/UI request model or environment override, but the
committed default should not change without explicit approval.

Provider candidates include:

- `faster-whisper-local`
- `funasr-local`
- `sherpa-onnx-local`

Candidate providers remain reliability work, not default replacements.

## Guards

The STT service includes:

- no-speech probability handling,
- audio energy checks,
- weak-speech suppression,
- suspicious transcript pattern suppression,
- diagnostics for model/provider resolution,
- safe truncation of error strings.

Manual mic no-speech should not fill the composer or auto-send chat.

## Conversation Mode

Conversation Mode is experimental. It uses:

- VAD and local audio context,
- pre-roll,
- sequential STT/chat processing,
- bounded pending queue,
- backpressure pause/resume diagnostics,
- distinct no-speech, empty-artifact, queue-full, and chat-error states.

It is not yet fully reliable for all long sessions.

## Owner Voice Gate

Owner Voice Gate is a dry-run/convenience boundary. It can enroll from local WAV
paths and verify temporary candidates. It must not be treated as production
authentication and must not expose raw audio, embeddings, candidate paths, or
raw verification internals in normal UI diagnostics.

## Validation Approach

Use focused backend tests for service changes and the desktop smoke scripts for
renderer/IPC regressions:

```powershell
node apps/desktop/scripts/renderer-chat-smoke.js
node apps/desktop/scripts/pet-window-smoke.js
node apps/desktop/scripts/pet-renderer-smoke.js
```

Keep generated WAVs, reports, and local manifests out of Git.
