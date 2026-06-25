# Current State

This document records the current project state only. It is not a task journal.

## What Works

- FastAPI backend starts locally and exposes health, chat, provider, memory,
  OCR, STT, Owner Voice Gate, and related routes.
- Electron Full App starts locally and talks to the backend.
- `/chat` works in mock mode by default and can use local Ollama when explicitly
  configured.
- Provider settings and safe key-storage abstraction are implemented.
- Local memory records, preview, and safe memory audit metadata exist.
- Pet Window overlay, expression mirroring, bubble state, quiet mode, scale, and
  direct input exist.
- Manual microphone and Conversation Mode STT flows exist.
- STT no-speech and suspicious-transcript guards are implemented.
- Owner Voice Gate enrollment/verification research path exists as a dry-run
  convenience filter.
- TTS backend skeleton exists but runtime speech remains disabled/mock-only.
- GPT-SoVITS voice work is isolated in an external lab.

## Experimental Areas

- Conversation Mode reliability and long-session quality.
- Owner Voice Gate thresholds, enrollment quality, and dry-run UX.
- Local STT provider selection among faster-whisper, FunASR, and sherpa-onnx.
- Local character-quality TTS provider selection.
- GPT-SoVITS Chinese text dependency resolution.

## Known Blockers

- GPT-SoVITS Chinese inference is not ready.
- The `jieba_fast` Windows blocker is resolved only inside the external lab by a
  verified, explicit adapter backed by official vendored `jieba-0.42.1`; the
  application runtime remains unchanged.
- `chinese2.py` eagerly constructs G2PW at import time.
- G2PW model/tokenizer/asset boundaries still need explicit approval.
- OpenCC implementation compatibility remains unresolved.
- Multilingual eager imports may pull non-Chinese dependencies before a
  Chinese-only path is isolated.
- Runtime TTS is disabled/mock-only.

## Current Next Actions

- TTS: `TASK-TTS-004E6D - OpenCC and G2PW Boundary Review`.
- STT: continue provider reliability work without changing the committed
  default unless explicitly approved.
- Documentation: keep current state in canonical docs and keep execution
  evidence local/ignored.
