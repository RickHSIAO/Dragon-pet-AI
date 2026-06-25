# Setup

This guide covers local development setup for the current project state.

## Prerequisites

- Windows PowerShell.
- Python with venv support.
- Node.js and npm.
- Optional: Ollama for local LLM experiments.
- Optional: Tesseract OCR runtime if using OCR beyond tests.

## Backend

From the repository root:

```powershell
python -m venv backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Start backend with the project helper:

```powershell
.\scripts\dev-start-backend.ps1
```

Manual fallback:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Desktop

Install dependencies:

```powershell
cd apps\desktop
npm install
```

Start from the repository root:

```powershell
.\scripts\dev-start-desktop.ps1
```

Manual fallback:

```powershell
cd apps\desktop
npm start
```

## Optional Local Ollama Mode

Install Ollama and pull a local model:

```powershell
ollama pull qwen3:8b
ollama list
```

Start Ollama:

```powershell
ollama serve
```

Start the backend with local provider settings:

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai\backend
$env:LLM_PROVIDER_ENABLED = "true"
$env:LLM_CHAT_ENABLED = "true"
$env:LLM_PROVIDER_NAME = "ollama"
$env:LLM_MODEL = "qwen3:8b"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:LLM_LOCAL_CHAT_TIMEOUT_SECONDS = "90"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The renderer still talks only to the backend. It never calls Ollama directly.

## Pet Window

Pet Mode is controlled by environment/startup behavior in the Electron app. If
the Full App reports that Pet Mode is disabled, start with the documented local
Pet Mode flag for your shell session:

```powershell
$env:PET_MODE_ENABLED = "true"
```

Then start the desktop app.

## Validation

Recommended lightweight validation after documentation or UI-safe changes:

```powershell
node apps/desktop/scripts/renderer-chat-smoke.js
node apps/desktop/scripts/pet-window-smoke.js
node apps/desktop/scripts/pet-renderer-smoke.js
git diff --check
git diff --cached --check
git status --short
```

Backend-only changes should also run focused pytest targets.
