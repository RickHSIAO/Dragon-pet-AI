# Desktop Smoke & Regression Runbook — dragon-pet-ai

Windows-first, copy-pasteable PowerShell.
All commands run from the **repo root** unless noted.

> **Related docs**
> - Stack startup (Ollama + backend + Electron): `docs/LOCAL_DEV_RUNBOOK.md`
> - Pet Mode manual smoke: `docs/PET_MODE_MANUAL_SMOKE_RUNBOOK.md`
> - Screen Context 43-item manual checklist: `docs/SCREEN_CONTEXT_RELEASE_SMOKE_CHECKLIST.md`

---

## Quick Reference — All Automated Suites

Paste this block after any non-trivial change to run everything:

```powershell
# From repo root
cd F:\RickHSIAO\Python\dragon-pet-ai

# 1. Full backend suite (667 tests — includes persistence, provider, chat, OCR, LLM adapter)
Push-Location backend
.\.venv\Scripts\python.exe -m pytest tests/ -q
Pop-Location

# 2. Desktop smoke suites (all three)
node apps/desktop/scripts/renderer-chat-smoke.js
node apps/desktop/scripts/pet-renderer-smoke.js
node apps/desktop/scripts/pet-window-smoke.js

# 3. Git housekeeping
git diff --check
git status --short
```

**Expected output when everything is healthy:**

```
667 passed, 1 warning in ~6s      ← full backend suite
renderer chat smoke: PASS          ← renderer-chat-smoke
pet renderer smoke complete (226 checks)  ← pet-renderer-smoke
pet window smoke complete (45 checks)     ← pet-window-smoke
(no output from git diff --check)  ← no whitespace errors
```

> **OCR-only fast run** (for changes isolated to `backend/app/ocr/` or `routes.py`):
> `Push-Location backend; .\.venv\Scripts\python.exe -m pytest tests/test_ocr_routes.py -q; Pop-Location`
> Expected: `34 passed, 1 warning in ~2s`

---

## Suite Details

### 1. Full Backend Suite

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai\backend
.\.venv\Scripts\python.exe -m pytest tests/ -q
```

| Property | Value |
|---|---|
| Location | `backend/tests/` (all test files) |
| Count | 667 tests |
| Runtime | ~6 s |
| What it covers | Provider settings (persistence, service, routes), chat service, LLM adapters (Ollama + mock + Anthropic), OCR service + endpoints, memory service, database models, environment config |
| Expected | `667 passed, 1 warning` |

Run when: any change to any `backend/` Python file. This is the standard pre-commit gate.

> **Note:** Uses `--basetemp=.pytest-tmp` (set in `backend/pytest.ini`) to keep temp files local.
> The `.pytest-tmp/` directory is git-ignored and safe to delete at any time.

---

### 1a. Backend OCR Tests (fast subset)

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai\backend
.\.venv\Scripts\python.exe -m pytest tests/test_ocr_routes.py -q
```

| Property | Value |
|---|---|
| Location | `backend/tests/test_ocr_routes.py` |
| Count | 34 tests |
| Runtime | ~2 s (no Tesseract binary required — probes are mocked) |
| What it covers | `/ocr/extract` endpoint, preprocessing pipeline, `_probe_ocr_status`, `get_ocr_status`, `_ocr_status_cache`, all fallback reason codes, `lang is None` guard, `/ocr/status` endpoint |
| Expected | `34 passed, 1 warning` |

Run when: change is isolated to `backend/app/ocr/`, `backend/app/api/routes.py`, or OCR-related env config and you want fast feedback. Run full suite before committing.

---

### 2. renderer-chat-smoke.js

```powershell
node apps/desktop/scripts/renderer-chat-smoke.js
```

| Property | Value |
|---|---|
| Location | `apps/desktop/scripts/renderer-chat-smoke.js` |
| Runtime | ~2–3 s (Node.js + JSDOM-like FakeDocument, no Electron) |
| What it covers | Full App chat send/receive, provider settings, pet expression, pet thinking state, TTS/quiet mode, memory toggle, OCR analyze flow, ask-screen handoff, OCR ask hint, screen capture error codes, capture isolation |
| Expected | `renderer chat smoke: PASS` |

Run when: any change to `apps/desktop/src/renderer/renderer.js`, `index.html`, or `apps/desktop/scripts/renderer-chat-smoke.js`.

---

### 3. pet-renderer-smoke.js

```powershell
node apps/desktop/scripts/pet-renderer-smoke.js
```

| Property | Value |
|---|---|
| Location | `apps/desktop/scripts/pet-renderer-smoke.js` |
| Count | 226 checks |
| Runtime | ~1–2 s |
| What it covers | Pet bubble reply rendering, speech payload sanitization, expression mapping, thinking/typing state, TTS/quiet mode, voice settings panel, Pet direct input, provider-usage badge, TASK-083 through TASK-169 scope checks |
| Expected | `pet renderer smoke complete (226 checks)` |

Run when: any change to `apps/desktop/src/pet/pet-renderer.js`, `pet.html`, `pet-preload.js`, or voice/TTS settings.

---

### 4. pet-window-smoke.js

```powershell
node apps/desktop/scripts/pet-window-smoke.js
```

| Property | Value |
|---|---|
| Location | `apps/desktop/scripts/pet-window-smoke.js` |
| Count | 45 checks |
| Runtime | ~1 s |
| What it covers | Pet window show/hide IPC, position persistence, scale presets, click-through, `ipcMain.handle` channel correctness, speech payload sanitizers in main/preload, STT IPC bridge, no Pet-IPC using `ipcMain.on` |
| Expected | `pet window smoke complete (45 checks)` |

Run when: any change to `apps/desktop/src/main.js`, `apps/desktop/src/renderer/preload.js`, or `apps/desktop/src/pet/pet-preload.js`.

---

### 5. Git Housekeeping

```powershell
# Check for trailing whitespace / mixed line endings
git diff --check

# Confirm no unintended staged or unstaged changes
git status --short
```

Run before every commit.

---

## When to Run Which Suite

### After any change — minimum bar

```powershell
git diff --check
git status --short
```

### After any backend Python change

```powershell
Push-Location backend
.\.venv\Scripts\python.exe -m pytest tests/ -q
Pop-Location
git diff --check
```

### After OCR-specific change only (faster)

```powershell
Push-Location backend
.\.venv\Scripts\python.exe -m pytest tests/test_ocr_routes.py -q
Pop-Location
git diff --check
```

### After renderer.js / index.html / styles.css change

```powershell
node apps/desktop/scripts/renderer-chat-smoke.js
git diff --check
```

### After pet-renderer.js / pet.html / pet-preload.js change

```powershell
node apps/desktop/scripts/pet-renderer-smoke.js
git diff --check
```

### After main.js / preload.js / any IPC change

```powershell
node apps/desktop/scripts/pet-window-smoke.js
git diff --check
```

### Full regression (before commit on any cross-cutting change)

```powershell
Push-Location backend
.\.venv\Scripts\python.exe -m pytest tests/ -q
Pop-Location
node apps/desktop/scripts/renderer-chat-smoke.js
node apps/desktop/scripts/pet-renderer-smoke.js
node apps/desktop/scripts/pet-window-smoke.js
git diff --check
git status --short
```

### Full manual release verification (Screen Context v0.4)

Run the 43-item checklist at `docs/SCREEN_CONTEXT_RELEASE_SMOKE_CHECKLIST.md`.
Requires the full stack running (Ollama + backend + Electron) — see `docs/LOCAL_DEV_RUNBOOK.md`.

---

## One-Shot Full Regression Block (copy-paste)

```powershell
# ── Full regression — run from repo root ──────────────────────────────────────
Set-Location F:\RickHSIAO\Python\dragon-pet-ai

# Full backend suite (667 tests — persistence, provider, OCR, chat, LLM adapter)
Push-Location backend
.\.venv\Scripts\python.exe -m pytest tests/ -q
Pop-Location

# Desktop smokes
node apps/desktop/scripts/renderer-chat-smoke.js
node apps/desktop/scripts/pet-renderer-smoke.js
node apps/desktop/scripts/pet-window-smoke.js

# Git hygiene
git diff --check
git status --short
# ─────────────────────────────────────────────────────────────────────────────
```

---

## Expected Healthy Baseline

| Suite | Expected output | Checks |
|---|---|---|
| Full backend pytest | `667 passed, 1 warning in ~6s` | 667 |
| OCR pytest (subset) | `34 passed, 1 warning in ~2s` | 34 |
| renderer-chat-smoke | `renderer chat smoke: PASS` | — |
| pet-renderer-smoke | `pet renderer smoke complete (226 checks)` | 226 |
| pet-window-smoke | `pet window smoke complete (45 checks)` | 45 |
| `git diff --check` | _(no output)_ | — |

If any suite fails, fix before committing. The only acceptable "warning" in the test suites is the pytest `.pytest_cache` write warning on Windows (a known PowerShell permissions quirk — does not affect test results).

---

## Smoke Suite File Map

```
apps/desktop/scripts/
  renderer-chat-smoke.js       ← renderer + Full App + OCR + ask-screen
  pet-renderer-smoke.js        ← Pet bubble + speech + expression + TTS
  pet-window-smoke.js          ← main.js IPC + position + scale + preload
  task171a-capture-smoke.js    ← Screen Context static + dynamic (called by renderer-chat-smoke)

backend/tests/                 ← 667 tests total (run with: python -m pytest tests/ -q)
  test_ocr_routes.py           ← OCR service + endpoints (34 tests — fast subset)
  test_provider_settings*.py   ← Provider settings persistence + service (23 + more)
  test_chat_service.py         ← Chat service + LLM routing
  test_llm_adapter*.py         ← Ollama + mock + Anthropic adapters
  (+ others)                   ← Memory service, DB models, env config, routes

backend/pytest.ini             ← addopts = --basetemp=.pytest-tmp (local temp dir, git-ignored)

docs/
  SCREEN_CONTEXT_RELEASE_SMOKE_CHECKLIST.md  ← 43-item manual checklist (Screen Context v0.4)
  LOCAL_DEV_RUNBOOK.md                       ← Stack startup
  PET_MODE_MANUAL_SMOKE_RUNBOOK.md           ← Pet Mode manual smoke
  DESKTOP_SMOKE_RUNBOOK.md                   ← This file
```

---

## Common Failures & Fixes

### `Cannot find module` on any smoke script

Node.js can't find the renderer source. Verify you're running from the repo root:

```powershell
Set-Location F:\RickHSIAO\Python\dragon-pet-ai
node apps/desktop/scripts/renderer-chat-smoke.js
```

### pytest `667 passed` (or `34 passed`) but `.pytest_cache` write warning

Expected on Windows — PowerShell permission quirk with the `.pytest_cache` directory. Not a test failure. Safe to ignore.

### `.pytest-tmp/` directory appears under `backend/`

Expected — `backend/pytest.ini` sets `--basetemp=.pytest-tmp` to keep temp files in the repo directory and avoid a Windows system-temp ACL issue (`PermissionError` on `C:\Users\...\AppData\Local\Temp\pytest-of-...`). The directory is git-ignored. Safe to delete at any time.

### `AssertionError` in pet-window-smoke

Usually means a new `ipcMain.on(PET_...)` was added to `main.js` without using `ipcMain.handle`. Check that:
1. Pet IPC channels use `ipcMain.handle()`.
2. Any new `ipcMain.on()` (e.g. for picker events) is paired with `ipcMain.removeListener()`.

### renderer-chat-smoke fails on a new element

A new `getElementById` call in `renderer.js` references an ID that the `FakeDocument` harness doesn't pre-populate. The `FakeDocument` creates elements lazily with `textContent = ""` and no `hidden` attribute preset. Tests check the `.hidden` property after the renderer runs (which sets it explicitly).

### `git diff --check` shows whitespace errors

Edit the file to remove trailing whitespace. On Windows, line-ending `LF will be replaced by CRLF` warnings are **not** errors — they are expected and safe to ignore.
