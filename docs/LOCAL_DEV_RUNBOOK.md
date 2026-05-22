# Local Dev Runbook — dragon-pet-ai

This runbook covers starting the full local stack (Ollama + backend + Electron) for
development and smoke testing. No external provider call is needed. No real API key is used.

---

## Prerequisites

| Requirement | Check |
|-------------|-------|
| Python 3.10+ | `python --version` |
| Node.js 18+ / npm | `node --version && npm.cmd --version` |
| Ollama installed | `ollama --version` |
| `qwen3:8b` model pulled | `ollama list` |
| backend venv created | `backend\.venv\Scripts\python.exe --version` |
| backend dependencies installed | `backend\.venv\Scripts\pip show fastapi` |
| desktop node_modules present | `Test-Path apps\desktop\node_modules` |

### First-time setup

```powershell
# 1. Pull the local model (one-time, ~5 GB download)
ollama pull qwen3:8b

# 2. Create and populate the backend virtual environment
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
cd ..

# 3. Install Electron dependencies
cd apps\desktop
npm.cmd install
cd ..\..
```

---

## Startup order

Always start in this order:

```
1. Ollama          (background process, provides the local LLM)
2. backend         (FastAPI on :8000, talks to Ollama)
3. Electron        (Electron app, talks to backend)
```

---

## 1. Start Ollama

Open a dedicated terminal and keep it running:

```powershell
ollama serve
```

Ollama listens on `http://localhost:11434` (backend-only — the Electron renderer never
calls it directly).

Confirm the model is available:

```powershell
ollama list
# Should include qwen3:8b
```

---

## 2. Start the backend

### Recommended (one-command script)

```powershell
# From the repo root
.\scripts\dev-start-backend.ps1
```

The script:
- Checks port 8000 is free.
- Activates `backend\.venv` if present.
- Sets all required env vars for Ollama mode.
- Starts `uvicorn` with `--reload`.

### Manual (advanced)

```powershell
cd backend
$env:PYTHONIOENCODING = "utf-8"
$env:LLM_PROVIDER_NAME = "ollama"
$env:LLM_MODEL = "qwen3:8b"
$env:LLM_PROVIDER_ENABLED = "true"
$env:LLM_CHAT_ENABLED = "true"
$env:LLM_LOCAL_CHAT_TIMEOUT_SECONDS = "90"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Confirm it is up:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
# { status: "ok", service: "dragon-pet-ai" }
```

---

## 3. Start the Electron desktop app

### Recommended (one-command script)

```powershell
# From the repo root (backend must already be running)
.\scripts\dev-start-desktop.ps1
```

The script:
- Verifies `node_modules` exists.
- Clears `ELECTRON_RUN_AS_NODE`.
- Uses `npm.cmd` (not `npm`) to avoid PowerShell execution-policy errors.
- Runs `npm.cmd run dev`.

### Manual

```powershell
cd apps\desktop
Remove-Item Env:\ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
npm.cmd run dev
```

---

## 4. Run the smoke helper

After all three services are running:

```powershell
.\scripts\dev-smoke.ps1
```

Checks `/health`, `/provider/settings`, `/provider/settings/test`, and `/chat`, and
reports whether `source=llm_local` (full local Ollama generation).

Custom backend URL:

```powershell
.\scripts\dev-smoke.ps1 -BaseUrl "http://127.0.0.1:8000"
```

---

## Provider settings persistence

Provider settings are stored in `backend/data/provider_settings.json` (git-ignored).
After a full `PATCH /provider/settings`, the backend remembers them across restarts.

Persisted fields (non-secret only):

```json
{
  "provider": "ollama",
  "model": "qwen3:8b",
  "real_provider_enabled": true,
  "llm_chat_enabled": true,
  "fallback_to_mock": false
}
```

API keys are **never** written to this file.

---

## Common errors

### `ConnectionRefusedError` in the Electron UI

The Electron app shows "Backend not reachable" when it cannot reach `http://localhost:8000`.

Fix: make sure `dev-start-backend.ps1` (or `uvicorn`) is running and healthy.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

---

### `uvicorn: command not found` / `uvicorn not on PATH`

The venv is not activated, or dependencies are not installed.

Fix:

```powershell
cd backend
.venv\Scripts\Activate.ps1   # activate venv
pip install -r requirements.txt
```

Or use `python -m uvicorn` directly — the startup script falls back to this automatically.

---

### `npm.ps1 ... running scripts is disabled on this system`

PowerShell's execution policy blocks `npm.ps1`.

Fix: always use `npm.cmd` instead of `npm`:

```powershell
npm.cmd install
npm.cmd run dev
```

The `dev-start-desktop.ps1` script uses `npm.cmd` automatically.

---

### `ELECTRON_RUN_AS_NODE` — Electron opens a terminal instead of the app window

If `ELECTRON_RUN_AS_NODE=1` is set, Electron behaves as a plain Node.js process and
shows a terminal instead of the app window.

Fix:

```powershell
Remove-Item Env:\ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
npm.cmd run dev
```

The `dev-start-desktop.ps1` script clears this automatically.

---

### First local model cold-start timeout

On first launch after `ollama pull qwen3:8b`, the model needs to load into memory.
The first `/chat` request may time out (default: 90 s via `LLM_LOCAL_CHAT_TIMEOUT_SECONDS`).

The backend returns `source=llm_local_error` with a message explaining the model may
still be loading. Wait 30–60 s and send another message — subsequent requests are fast.

You can verify the model is warm:

```powershell
ollama list   # should show qwen3:8b
# Then send one test request via dev-smoke.ps1
```

---

### `provider_settings.json` not persisting across restarts

If settings reset to `provider=mock` on restart, the settings file path may not be writable.

Check:

```powershell
Test-Path backend\data\provider_settings.json
Get-Content backend\data\provider_settings.json
```

If the file is absent, the backend will create it on the first `PATCH /provider/settings`.
The file is git-ignored — confirm with:

```powershell
git check-ignore backend\data\provider_settings.json
# Expected: backend/data/provider_settings.json
```

---

## Environment variable reference

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER_NAME` | `mock` | Provider: `ollama`, `anthropic`, or `mock` |
| `LLM_MODEL` | _(none)_ | Model name passed to the provider |
| `LLM_PROVIDER_ENABLED` | `false` | Enables real provider factory |
| `LLM_CHAT_ENABLED` | `false` | Routes `/chat` through LLM adapter |
| `LLM_LOCAL_CHAT_TIMEOUT_SECONDS` | `90` | Timeout for local Ollama generation (1–300 s) |
| `LLM_FALLBACK_TO_MOCK` | `true` | Falls back to mock on provider error |
| `DB_PATH` | `sqlite:///./data/dragon_pet.db` | SQLite path (relative to `backend/`) |
| `SETTINGS_FILE_PATH` | `data/provider_settings.json` | Persisted settings path |
| `MEMORY_INJECTION_ENABLED` | `false` | Enables memory-aware chat (TASK-023) |
| `PYTHONIOENCODING` | _(system)_ | Set to `utf-8` to avoid encoding issues on Windows |

All boolean env vars accept: `1`, `true`, `yes`, `on` (case-insensitive) as true;
anything else is false. Unknown values fail closed to false.

---

## Safety constraints (permanent)

- The Electron renderer never calls Ollama directly (`localhost:11434` is not in renderer.js).
- API keys are never persisted to `provider_settings.json` or any git-tracked file.
- `/chat` schema is always `reply / mood / source`.
- No external provider call is made in automated tests.
- `fallback_to_mock=false` is recommended when verifying that Ollama is actually generating replies.
