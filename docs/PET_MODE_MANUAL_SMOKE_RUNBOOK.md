# Pet Mode Manual Smoke Runbook — dragon-pet-ai

Windows-first, copy-pasteable PowerShell.
For the general stack (Ollama + backend + Electron without Pet Mode) see
`docs/LOCAL_DEV_RUNBOOK.md`.

---

## Prerequisites

| Requirement | Check |
|---|---|
| Python 3.10+ | `python --version` |
| Node.js 18+ | `node --version` |
| Ollama installed | `ollama --version` |
| `qwen3:8b` model pulled | `ollama list` |
| backend venv created | `backend\.venv\Scripts\python.exe --version` |
| backend deps installed | `backend\.venv\Scripts\pip show fastapi` |
| desktop node_modules present | `Test-Path apps\desktop\node_modules` |

First-time one-shot setup:

```powershell
# Pull model (~5 GB, one-time)
ollama pull qwen3:8b

# Backend venv
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
cd ..

# Desktop deps
cd apps\desktop
npm.cmd install
cd ..\..
```

---

## 1. Start Ollama

Open a dedicated terminal and keep it running:

```powershell
ollama serve
```

If Ollama says it is already running, that is fine — ignore the message and move on.

Confirm the server is up and the model is available:

```powershell
curl.exe http://127.0.0.1:11434/api/tags
# Expected: JSON with "models" list containing "qwen3:8b"
```

Check whether the model is currently loaded in GPU/CPU memory:

```powershell
ollama ps
# If empty: model is not yet loaded — the first /chat request will cold-start it.
# If qwen3:8b appears: model is warm and ready.
```

### Warm up before first smoke

On a cold start the first `/chat` request may take 30–90 s while the model loads.
Run a warm-up request first so Pet Bubble responses come back quickly:

```powershell
ollama run qwen3:8b "reply in one word: ready"
# Wait until qwen3:8b replies, then the model is in memory.
```

After this completes, `ollama ps` will show `qwen3:8b` as loaded.

---

## 2. Start the backend

```powershell
# From the repo root — activates venv, sets Ollama env vars, starts uvicorn
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\dev-start-backend.ps1
```

Confirm it is up:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
# Expected: @{status=ok; service=dragon-pet-ai}
```

---

## 3. Start the desktop app with Pet Mode

Open a second terminal (backend stays in its own window):

```powershell
cd apps\desktop
$env:PET_MODE_ENABLED = "true"
npm.cmd start
```

Two windows will open:

- **Full App window** — the main management UI (chat, memory, audit, provider settings).
- **Pet Window** — a small frameless `220 x 280` companion window showing Christina.

---

## 4. Show / open the Pet Window

If the Pet Window is hidden:

- Click **Show Pet** in the Full App header bar.

If the Pet Window was never opened (e.g. `PET_MODE_ENABLED` was not set):

- Quit the app and relaunch with `$env:PET_MODE_ENABLED = "true"`.

---

## 5. Full App DevTools vs Pet Window DevTools

The two windows are **separate Electron renderer processes** with separate JavaScript
contexts. DevTools opened in one window cannot inspect the other.

| Window | DevTools shortcut | Context |
|---|---|---|
| Full App | `Ctrl+Shift+I` while Full App is focused | Full App renderer (`renderer.js`) |
| Pet Window | `Ctrl+Shift+I` while Pet Window is focused | Pet renderer (`pet-renderer.js`) |

**Always open DevTools in the Pet Window** for Pet-specific smoke hooks.
Opening Full App DevTools will not expose `window.__dragonPetMoodExpressionSmoke`.

---

## 6. Open Pet Window DevTools

1. Click on the Pet Window to give it focus.
2. Press `Ctrl+Shift+I`.
3. The DevTools panel opens for the Pet renderer process.

Confirm you are in the right context by running in the Console tab:

```javascript
document.title
// Expected: something like "Dragon Pet - Pet Mode" or similar pet-specific title
window.__dragonPetMoodExpressionSmoke
// Expected: a function object — not undefined
```

If `window.__dragonPetMoodExpressionSmoke` is `undefined`, you are in Full App DevTools,
not Pet Window DevTools. Close and reopen DevTools with Pet Window focused.

---

## 7. Pet mood expression smoke hook

`window.__dragonPetMoodExpressionSmoke.apply(mood)` is a deterministic manual smoke
hook exposed by the Pet renderer. It drives the Christina expression mapping directly
without making a `/chat` call and without changing any visible speech bubble text.

Run the following in **Pet Window DevTools** console:

```javascript
// Test each supported mood and the unknown-fallback case
const moods = ["neutral", "focused", "proud", "worried", "missing_mood"];
const results = moods.map(m => ({
  mood: m,
  result: window.__dragonPetMoodExpressionSmoke.apply(m)
}));
console.table(results);
```

Expected visual outcome for each call:

| Mood | Christina expression |
|---|---|
| `neutral` | `christina_neutral.png` |
| `focused` | `christina_focused.png` |
| `proud` | `christina_proud.png` |
| `worried` | `christina_worried.png` |
| `missing_mood` | neutral fallback (`christina_neutral.png`) |

The Pet Bubble visible reply text must not change when this hook is called.
If the reply text changes, the smoke hook is incorrectly wired to the speech path.

Also confirm the other supported moods:

```javascript
["happy", "annoyed", "sleepy"].forEach(m =>
  window.__dragonPetMoodExpressionSmoke.apply(m)
);
// Check visually: happy → christina_happy.png, annoyed → christina_annoyed.png,
// sleepy → christina_sleepy.png
```

### Verifying expression switching via DevTools (TASK-156)

Expression changes at 142 × 142 px may be visually subtle. Use DevTools to
confirm the expression state is being set correctly rather than relying on
visual inspection alone.

**Method 1 — Check the smoke hook return value:**

The `apply()` return object includes the new `src`. Verify it changes per mood:

```javascript
// In Pet Window DevTools console
const a = window.__dragonPetMoodExpressionSmoke.apply("focused");
console.log(a.src);   // should end with "christina_focused.png"
const b = window.__dragonPetMoodExpressionSmoke.apply("annoyed");
console.log(b.src);   // should end with "christina_annoyed.png"
```

**Method 2 — Check the root element data attribute (TASK-156):**

`setPetExpression()` now also writes `data-expression` on `#pet-mode-root`:

```javascript
// In Pet Window DevTools console — run after each apply() call
document.getElementById("pet-mode-root").dataset.expression;
// Should match the mood you passed: "focused", "annoyed", etc.
```

You can also check the container directly:

```javascript
document.getElementById("pet-avatar-container").dataset.expression;
// Same value
```

**Method 3 — Check the img src in the Elements panel:**

In Pet Window DevTools → Elements tab → find `#pet-avatar` → look at the
`src` attribute. It should end with `christina_<mood>.png` matching the last
`apply()` call.

Expression assets that exist and must load without the `onerror` fallback:

| File | Expected |
|---|---|
| `christina_neutral.png` | 345 KB |
| `christina_focused.png` | 406 KB |
| `christina_happy.png` | 408 KB |
| `christina_proud.png` | 390 KB |
| `christina_annoyed.png` | 393 KB |
| `christina_worried.png` | 333 KB |
| `christina_sleepy.png` | 309 KB |

---

## 8. Pet Bubble cleanliness verification

After a successful `/chat` round-trip via Full App:

1. Check the Full App **Pet speech mirror** area — it should show only the `reply` text.
2. Check the Pet Window bubble — it should show only the character reply.
3. None of the following should appear as normal speech text:
   - `mood:` or a raw mood value like `focused`
   - `source:` or `llm_local`
   - `<think>` blocks or thinking content
   - JSON fields or debug output
   - `details:` or `detail:` disclosure lines mixed into the reply

Run a quick check in Full App DevTools:

```javascript
// Inspect the visible pet speech mirror text
document.querySelector("#pet-speech-mirror")?.innerText
// Expected: character reply text only, no schema fields
```

---

## 8b. Pet Bubble thinking state verification (TASK-157)

When Full App sends a `/chat` request, the Pet Window should immediately show a
thinking bubble before the backend reply arrives.

**Steps:**

1. Open Pet Window (Show Pet Window button in Full App, or tray icon).
2. Open **Pet Window DevTools** (Section 6 above).
3. In Full App, type a message and click **Send**.
4. Observe the Pet Window bubble **before** the reply arrives:
   - Bubble should be visible and show thinking text such as
     `吾、吾才不是在認真思考呢……等一下！`
   - Bubble state must be `thinking`:

```javascript
document.getElementById("pet-mode-root").dataset.bubbleState  // → "thinking"
document.getElementById("pet-bubble").dataset.state            // → "thinking"
document.getElementById("pet-avatar-container").dataset.expression  // → "focused"
```

5. Once the backend reply arrives, verify the thinking bubble is **replaced**:
   - `pet-bubble-response` innerText should be the character reply only.
   - No `source:`, `mood:`, `{`, `}`, `pet_thinking`, or JSON tokens.

```javascript
document.getElementById("pet-bubble-response").innerText
// Expected: clean character reply, no schema or debug tokens
document.getElementById("pet-mode-root").dataset.bubbleState
// Expected: "speaking" (or "long_reply" for long replies)
```

6. Verify the thinking state was **not persisted** — hide the Pet Window and show
   it again; it should restore the last real reply (or idle), not the thinking text.

**Error path:**

If the backend request fails, the Pet Bubble should show a clean error message:

```javascript
document.getElementById("pet-bubble-response").innerText
// Expected: "吾的魔力暫時卡住了。" (or similar clean message)
document.getElementById("pet-mode-root").dataset.bubbleState
// Expected: "llm_local_error" or "backend_offline"
```

No raw error details, stack traces, or JSON should appear in the bubble.

---

## 9. Ollama idle wake behavior (TASK-150)

Ollama unloads the model from memory after the `keep_alive` window (default: 30 minutes
of inactivity). If the model is unloaded, the next request cold-starts it again.

Verify the behavior:

```powershell
# Step 1: Confirm model is currently unloaded
ollama ps
# Expected: empty output (no models listed)

# Step 2: Send a chat via Full App — first request triggers cold start
# The Pet Window and Full App should show a "Local model is waking up..." status
# while the model loads (~20–60 s on first cold start)

# Step 3: After the first response arrives, confirm model is now loaded
ollama ps
# Expected: qwen3:8b listed with size and processor

# Step 4: Send a second chat — should return much faster (model is warm)
```

Expected behavior summary:

| State | `ollama ps` | First response time |
|---|---|---|
| Model unloaded | empty | 20–90 s cold start |
| Model loaded | shows qwen3:8b | < 5 s |
| After 30 min idle | empty | cold start again |

The backend sends `"keep_alive": "30m"` with each Ollama request, which resets the
30-minute idle timer on every successful generation.

---

## 10. Windows `.pytest-tmp` permission workaround

On Windows, NTFS mount points can deny pytest's attempt to create `.pytest_cache`
or a shared basetemp directory inside the repo. Use a fresh per-run basetemp name
outside any mount-point issue:

```powershell
# From the repo root
python -m pytest --basetemp .\.pytest-tmp-run155 -p no:cacheprovider
```

Rules:

- Use a unique name per run (e.g. `run155`, `run156`) to avoid locked-folder conflicts.
- Do **not** `git add` any `.pytest-tmp-*` folder.
- Add to `.gitignore` if not already covered:

  ```
  .pytest-tmp-*/
  ```

- If a temp folder is locked (Windows file lock after a failed run):

  ```powershell
  # Try removing first
  Remove-Item -Recurse -Force .\.pytest-tmp-run155

  # If still locked: close all terminal windows, reboot, then delete
  ```

---

## 11. Backend pytest command

```powershell
# From the repo root
python -m pytest --basetemp .\.pytest-tmp-run155 -p no:cacheprovider
# Expected: all tests pass (611 passed as of TASK-154)
```

Run only the chat service tests (faster):

```powershell
python -m pytest backend\tests\test_chat_service.py --basetemp .\.pytest-tmp-run155-chat -p no:cacheprovider
```

---

## 12. Desktop smoke commands

Run from the repo root:

```powershell
cd apps\desktop

# Full App renderer smoke (56 tests as of TASK-113)
npm.cmd run test:renderer

# Pet renderer smoke (46 checks as of TASK-154)
node scripts/pet-renderer-smoke.js

# Pet window smoke (15 checks as of TASK-154)
node scripts/pet-window-smoke.js

cd ..\..
```

All three should end with `PASS` or a pass count. Any `FAIL` or unhandled exception
is a blocker.

---

## 13. Git hygiene

```powershell
# Do NOT use:
git add .

# Use explicit paths instead:
git add docs/PET_MODE_MANUAL_SMOKE_RUNBOOK.md
git add docs/TASKS.md docs/ROADMAP.md

# Confirm nothing unexpected is staged:
git status
git diff --cached --name-only
```

Temp folders that must not be committed:

```
.pytest-tmp-*/
backend/data/provider_settings.json   # git-ignored, personal settings
backend/data/dragon_pet.db            # git-ignored, local DB
```

LF-to-CRLF warnings during `git add` or `git commit` on Windows are usually
non-blocking. Run `git diff --check` to confirm there are no real whitespace errors:

```powershell
git diff --check
# No output = PASS
```

---

## 14. Common troubleshooting

### Ollama server reachable but model unloaded

```powershell
curl.exe http://127.0.0.1:11434/api/tags
# Shows models list — server is up

ollama ps
# Empty — model not in memory

# Fix: warm-up request
ollama run qwen3:8b "reply in one word: ready"
```

---

### Pet DevTools hook is `undefined`

You opened Full App DevTools instead of Pet Window DevTools.

```
window.__dragonPetMoodExpressionSmoke
// undefined  ← wrong window
```

Fix:

1. Close DevTools.
2. Click on the Pet Window (small 220 x 280 window) to focus it.
3. Press `Ctrl+Shift+I` again.
4. Re-run the check — it should now return a function.

---

### `.pytest-tmp` permission denied

```
PermissionError: [Errno 13] Permission denied: '.pytest-tmp-run155'
```

Fix:

```powershell
# Force-remove the locked folder
Remove-Item -Recurse -Force .\.pytest-tmp-run155

# Use a different name for the next run
python -m pytest --basetemp .\.pytest-tmp-run156 -p no:cacheprovider
```

If the folder cannot be removed, close all terminals and reboot Windows.

---

### `git diff --check` warns about CRLF

LF/CRLF warnings in the diff output (lines showing `^M` or `carriage-return`) are
usually caused by Windows line ending conversion and are non-blocking **unless** they
appear as `trailing whitespace` errors.

```powershell
git diff --check
# No output = PASS (CRLF warnings from git config are shown separately, not here)
```

If real trailing-whitespace errors appear, strip them before committing:

```powershell
# Check which files have trailing whitespace
git diff HEAD | grep '^\+.*\s+$'
```

---

## Reference: docs map

| Doc | Purpose |
|---|---|
| `docs/LOCAL_DEV_RUNBOOK.md` | General stack (Ollama + backend + Electron, no Pet Mode) |
| `docs/PET_MODE_MANUAL_SMOKE_RUNBOOK.md` | This file — Pet Mode launch, DevTools, smoke hooks |
| `docs/開啟方式.txt` | Quick three-terminal startup note (Chinese) |
| `docs/PET_MODE_UI_DESIGN.md` | Pet Window design spec and expression mapping design |
| `docs/PET_BUBBLE_CHAT_WIRING_DESIGN.md` | Pet Bubble `/chat` wiring and smoke coverage design |
| `docs/OLLAMA_PROVIDER_DESIGN.md` | Ollama backend wiring and `keep_alive` design |
| `docs/OLLAMA_RUNTIME_SMOKE_CHECKLIST.md` | Ollama-specific runtime smoke checklist |
