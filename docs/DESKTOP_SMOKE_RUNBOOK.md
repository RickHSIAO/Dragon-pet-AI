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

# 1. Backend OCR unit tests
Set-Location backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_ocr_routes.py -q
Set-Location ..

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
34 passed, 1 warning in ~2s       ← OCR tests
renderer chat smoke: PASS          ← renderer-chat-smoke
pet renderer smoke complete (226 checks)  ← pet-renderer-smoke
pet window smoke complete (45 checks)     ← pet-window-smoke
(no output from git diff --check)  ← no whitespace errors
```

---

## Suite Details

### 1. Backend OCR Tests

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai\backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_ocr_routes.py -q
```

| Property | Value |
|---|---|
| Location | `backend/tests/test_ocr_routes.py` |
| Count | 34 tests |
| Runtime | ~2 s (no Tesseract binary required — probes are mocked) |
| What it covers | `/ocr/extract` endpoint, preprocessing pipeline, `_probe_ocr_status`, `get_ocr_status`, `_ocr_status_cache`, all fallback reason codes, `lang is None` guard, `/ocr/status` endpoint |
| Expected | `34 passed, 1 warning` |

Run when: any change to `backend/app/ocr/`, `backend/app/api/routes.py`, or OCR-related env config.

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

### After any OCR / backend change

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_ocr_routes.py -q
cd ..
git diff --check
```

### Full regression (before commit on Screen Context or cross-cutting changes)

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai\backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_ocr_routes.py -q
cd ..
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

# Backend OCR
Push-Location backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_ocr_routes.py -q
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
| OCR pytest | `34 passed, 1 warning in ~2s` | 34 |
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

backend/tests/
  test_ocr_routes.py           ← OCR service + endpoints

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

### pytest `34 passed` but `.pytest_cache` write warning

Expected on Windows — PowerShell permission quirk with the cache directory. Not a test failure. Safe to ignore.

### `AssertionError` in pet-window-smoke

Usually means a new `ipcMain.on(PET_...)` was added to `main.js` without using `ipcMain.handle`. Check that:
1. Pet IPC channels use `ipcMain.handle()`.
2. Any new `ipcMain.on()` (e.g. for picker events) is paired with `ipcMain.removeListener()`.

### renderer-chat-smoke fails on a new element

A new `getElementById` call in `renderer.js` references an ID that the `FakeDocument` harness doesn't pre-populate. The `FakeDocument` creates elements lazily with `textContent = ""` and no `hidden` attribute preset. Tests check the `.hidden` property after the renderer runs (which sets it explicitly).

### `git diff --check` shows whitespace errors

Edit the file to remove trailing whitespace. On Windows, line-ending `LF will be replaced by CRLF` warnings are **not** errors — they are expected and safe to ignore.
