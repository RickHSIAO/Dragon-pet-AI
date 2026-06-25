# Architecture

Dragon Pet AI is split into a local backend, an Electron Full App, and a Pet
Window. The design goal is a desktop companion with narrow local boundaries,
safe defaults, and explicit opt-in for real model behavior.

## System Shape

```text
Full App renderer       Pet renderer
        |                   |
        +---- preload APIs --+
                 |
          Electron main
                 |
          localhost HTTP
                 |
          FastAPI backend
                 |
    SQLite, providers, STT, TTS, OCR, memory
```

## Backend

The backend owns all non-renderer behavior:

- `/health` liveness.
- `/chat` with stable `reply / mood / source` response schema.
- Provider settings and safe key-storage abstraction.
- Local Ollama provider adapter when explicitly enabled.
- Mock provider fallback and deterministic mock behavior.
- Local SQLite conversation history, state, memory, and memory audit data.
- STT route and startup warmup.
- OCR route with in-memory image handling.
- Owner Voice Gate storage and file-based sidecar verification.
- TTS service skeleton and text normalization.

Backend services are grouped by responsibility under `backend/app/services`,
provider adapters under `backend/app/llm`, STT under `backend/app/stt`, and TTS
under `backend/app/tts`.

## Desktop App

The Electron app has two user-facing surfaces:

- Full App: chat, memory, provider settings, voice controls, diagnostics,
  search, export, and Conversation Mode.
- Pet Window: compact overlay companion, expression state, speech bubble,
  quiet mode, scale controls, direct input, and Full App handoff.

Renderer code uses preload-exposed APIs. It does not receive a generic
`ipcRenderer`, filesystem access, raw provider access, or direct Ollama access.

## Data Flow

Normal chat:

```text
Renderer input -> Electron main -> FastAPI /chat -> chat service
  -> mock or configured provider -> response -> renderer and optional Pet mirror
```

Manual STT:

```text
Renderer microphone blob -> stt:transcribe IPC -> FastAPI /stt/transcribe
  -> STT service -> final transcript and diagnostics -> renderer
```

Conversation Mode:

```text
Renderer VAD loop -> sequential STT turns -> bounded chat queue
  -> /chat one turn at a time -> diagnostics and queue state
```

Pet expression and bubble updates:

```text
Full App event -> narrow IPC payload -> Pet renderer handler
```

## Persistence

- SQLite stores conversation history, local state, explicit memory, and memory
  injection audit metadata.
- Provider non-secret settings are persisted in ignored local JSON.
- Provider keys use the backend key-storage abstraction.
- Chat exports are user-selected local files.
- Generated reports and lab artifacts are ignored.

## Runtime Boundaries

- `/chat` schema is stable and must not be widened casually.
- Pet Mode is display/companion UI, not a generic automation surface.
- Owner Voice Gate is not authentication.
- TTS runtime remains disabled/mock-only.
- GPT-SoVITS research is isolated outside the application runtime.
- Scripts may inspect and report, but generated evidence should stay local.

## Tests And Smokes

The main lightweight desktop validation entry points are:

```powershell
node apps/desktop/scripts/renderer-chat-smoke.js
node apps/desktop/scripts/pet-window-smoke.js
node apps/desktop/scripts/pet-renderer-smoke.js
```

Backend tests live under `backend/tests`.
