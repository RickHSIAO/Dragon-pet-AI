# Security And Privacy Boundaries

Dragon Pet AI is local-first and fail-closed by default. This document records
stable boundaries, not per-task audit evidence.

## Defaults

- Mock chat is the default.
- Real provider chat requires explicit backend settings.
- TTS runtime is disabled/mock-only.
- Owner Voice Gate is not authentication.
- External voice-lab artifacts stay outside the repository.

## Secrets

- Do not commit `.env` files, API keys, tokens, private keys, or provider
  credentials.
- Provider keys are handled by backend services and never returned to clients.
- Renderer code must not receive raw provider keys or generic filesystem access.

## Renderer And IPC

- Renderer code uses narrow preload APIs.
- Do not expose generic `ipcRenderer`.
- Do not add direct renderer calls to Ollama or external providers.
- Pet Window channels should stay fixed-purpose and payload-sanitized.

## Backend Routes

- `/chat` does not execute shell commands.
- `/chat` response schema remains `reply / mood / source`.
- Provider Test Connection is a narrow liveness/configuration check, not a full
  persona or generation validation.
- OCR image data is processed in memory.
- STT audio uploads are bounded and handled through backend routes.

## Memory

- Memory injection is gated by backend flag and request opt-in.
- Memory audit responses must not include raw memory text, prompts, or formatted
  memory context.
- Memory records are local SQLite data.

## STT And Owner Voice

- Raw audio should not be committed.
- Temporary owner-voice candidate WAV files must be local and cleaned up.
- Owner Voice Gate stores aggregate data only and is not security-grade.

## TTS And Voice Lab

- Generated audio, model weights, datasets, tokenizer assets, and external lab
  reports stay out of Git.
- GPT-SoVITS is researched in an isolated external lab.
- No model download or runtime speech integration should happen without explicit
  approval.
