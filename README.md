# Dragon Pet AI

Dragon Pet AI is a local-first desktop companion prototype. It combines a
FastAPI backend, an Electron desktop app, a Pet Window, local chat/provider
controls, offline speech experiments, and a strict privacy boundary.

The project is not a cloud assistant product. It is a local desktop companion
research app with mocked-safe defaults and explicit gates before any real model,
speech, or provider behavior is enabled.

## Current Core Features

- Full App chat UI backed by FastAPI `/chat`.
- Mock chat provider enabled by default.
- Optional local Ollama provider path through the backend only.
- Provider settings UI with safe key-storage abstraction and test connection.
- Local SQLite conversation, memory, state, audit, and settings support.
- Pet Window overlay with expression, bubble, quiet mode, scale, and direct input.
- Manual microphone and Conversation Mode STT flows.
- Offline STT candidate plumbing with no-speech and hallucination guards.
- Owner Voice Gate research UI and dry-run verification boundary.
- TTS backend skeleton and disabled/mock-only runtime state.
- GPT-SoVITS character voice research kept in an external isolated lab.

## Main Components

- `backend/app/` - FastAPI routes, services, schemas, provider adapters, STT,
  TTS skeleton, OCR, memory, and local state.
- `apps/desktop/src/main.js` - Electron main process, windows, IPC, local file
  boundaries, and backend bridge handlers.
- `apps/desktop/src/renderer/` - Full App chat, provider settings, memory,
  microphone controls, Conversation Mode, diagnostics, and output queue UI.
- `apps/desktop/src/pet/` - Pet Window renderer, local chat handoff, expression,
  bubble, quiet mode, direct input, and optional browser speech controls.
- `scripts/` - local probes, smoke helpers, STT/TTS research scripts, and dev
  startup scripts.
- `docs/` - canonical project documentation.

## Technology Stack

- Backend: Python, FastAPI, SQLModel, SQLite, pytest.
- Desktop: Electron, Node.js, browser renderer JavaScript, local IPC bridges.
- Local LLM candidate: Ollama through backend-owned HTTP only.
- STT candidates: faster-whisper local path by default, with FunASR and
  sherpa-onnx as research/runtime candidates.
- OCR: Pillow and pytesseract.
- TTS: disabled/mock backend skeleton plus external voice-lab research.

## High-Level Architecture

```text
Electron Full App / Pet Window
        |
        | narrow IPC bridges
        v
Electron main process
        |
        | localhost HTTP
        v
FastAPI backend
        |
        +-- SQLite local state
        +-- mock or local LLM provider
        +-- STT/OCR/TTS service boundaries
        +-- provider settings and safe key storage
```

The Electron renderer does not call Ollama, external providers, or local files
directly. Renderer code uses narrow preload APIs. The backend owns provider
selection, request safety, local persistence, and model/provider boundaries.

## Quick Start

Prerequisites:

- Windows PowerShell.
- Python venv for the backend.
- Node.js and npm for the Electron app.
- Optional: Ollama if testing local LLM mode.

Install backend dependencies:

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai
python -m venv backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Install desktop dependencies:

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai\apps\desktop
npm install
```

Start backend:

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai
.\scripts\dev-start-backend.ps1
```

Start desktop:

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai
.\scripts\dev-start-desktop.ps1
```

Manual backend fallback:

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Manual desktop fallback:

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai\apps\desktop
npm start
```

## Basic Usage

- Use the Full App chat box for normal messages.
- Use Provider Settings to keep mock mode or configure the local Ollama path.
- Use the Memory section for explicit local memory records.
- Use the microphone controls for manual STT trials.
- Use Conversation Mode only as an experimental continuous speech workflow.
- Use the Pet Window for display, expression, handoff, and local pet input.
- Use export/search/clear features from the Full App when reviewing chat history.

## Directory Overview

```text
apps/desktop/      Electron app
backend/           FastAPI backend
docs/              canonical docs
scripts/           local dev, smoke, STT, TTS, and research helpers
outputs/           ignored generated reports
backend/data/      local backend data, mostly ignored
```

## Privacy And Safety Boundary

- Defaults are fail-closed: mock chat, TTS disabled, no cloud provider.
- `/chat` response schema remains `reply / mood / source`.
- API keys are handled by backend services and are never returned to clients.
- STT audio is processed in memory for the route; raw audio is not committed.
- Owner Voice Gate is a convenience/dry-run filter, not security-grade auth.
- External voice-lab reports, model weights, generated audio, and package
  snapshots stay outside Git.
- Generated command logs, smoke output, package snapshots, and daily task notes
  are local-only.

## Current Limitations

- Runtime TTS is disabled/mock-only.
- GPT-SoVITS Chinese inference is not ready.
- No character voice model is selected or usable in-app.
- Owner Voice Gate is not production authentication.
- Conversation Mode is still experimental and can require more reliability work.
- Real provider mode requires explicit local setup and careful fallback settings.

## Canonical Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Setup](docs/SETUP.md)
- [User Guide](docs/USER_GUIDE.md)
- [Current State](docs/CURRENT_STATE.md)
- [Roadmap](docs/ROADMAP.md)
- [Security](docs/SECURITY.md)
- [TTS](docs/TTS.md)
- [STT](docs/STT.md)
- [Character Spec](docs/CHARACTER_SPEC.md)
- [Contributing](CONTRIBUTING.md)
