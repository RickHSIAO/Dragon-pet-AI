# Pet Mode Release Checkpoint

> Task: TASK-131 - Pet Mode Release Checkpoint
> Date: 2026-05-24
> Status: DONE - Pet Mode first-stage MVP checkpoint

This checkpoint records the completed first-stage Pet Mode surface after TASK-114 through TASK-130.

Pet Mode is now a maintainable MVP for a small desktop pet window that can coexist with the Full App. Bubble Chat remains a local UI placeholder and is intentionally not wired to `/chat` yet.

## Completed Capabilities

- Optional Pet Window starts only when `PET_MODE_ENABLED=true`.
- Full App remains the default startup and management surface.
- Pet Window is `220 x 280`, frameless, transparent, always-on-top, and non-resizable.
- Pet Mode uses a separate static renderer under `apps/desktop/src/pet`.
- Christina avatar uses the existing expression asset path.
- Pet hint text is rendered locally.
- Bubble Chat placeholder exists with collapsed / expanded local UI state.
- Explicit top drag handle supports moving the Pet Window.
- Avatar, bubble, menu, buttons, inputs, and controls are no-drag interaction zones.
- Pet Window can ask main process to show / focus Full App.
- Full App can show / focus Pet Window after it has been hidden.
- Pet menu supports Open Full App, Reset Pet Position, Hide Pet Window, and Close Menu.
- Bottom Menu button toggles open / closed.
- Escape closes the menu.
- Pet Window position persists locally under Electron `userData`.
- Off-screen saved positions fall back to a safe default.
- Manual Windows drag/menu smoke passed.

## Deferred Items

- Bubble Chat is not wired to `/chat`.
- Pet Mode does not yet display real LLM responses.
- Pet bubble does not yet show source / mood / error / loading states from backend responses.
- Pet bubble does not yet integrate backend mood with expression updates.
- Tray icon support is not implemented.
- Package / installer / autostart behavior is not implemented.
- Full custom drag implementation is not implemented.
- Whole-character dragging is deferred.
- Windows CSS drag-region right-click can still trigger the OS system menu on the explicit handle; large avatar/body drag remains intentionally disabled.

## Safety Boundaries

- Pet Mode does not automatically read files.
- Pet Mode does not read Email.
- Pet Mode does not read Calendar.
- Pet Mode does not execute commands.
- Pet Mode does not call external APIs.
- Pet Mode does not secretly take screenshots.
- Pet Mode does not record audio.
- Pet Mode does not monitor the screen.
- Pet Mode does not modify `/chat` schema.
- Pet renderer does not directly call Ollama.
- Pet renderer currently does not call backend `/chat`.
- IPC channels are fixed and narrow.
- Preload APIs do not expose arbitrary `ipcRenderer`.
- Preload APIs do not expose fs, shell, or process.

## Smoke And Test Results

Recorded checkpoint results:

- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/src/renderer/preload.js`: PASS.
- `node --check apps/desktop/src/pet/pet-renderer.js`: PASS.
- `node --check apps/desktop/src/pet/pet-preload.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `node --check apps/desktop/scripts/pet-renderer-smoke.js`: PASS.
- `node --check apps/desktop/scripts/pet-window-smoke.js`: PASS.
- `node apps/desktop/scripts/pet-renderer-smoke.js`: PASS, 13 checks.
- `node apps/desktop/scripts/pet-window-smoke.js`: PASS, 10 checks.
- `npm.cmd run test:renderer`: PASS.
- `python -m pytest`: PASS, 586 passed.
- Direct Ollama `11434` safety scan: PASS.
- Manual Windows Pet drag/menu smoke: PASS.

Manual Windows smoke confirmed:

| Check | Result |
|---|---|
| Top drag handle drags Pet Window | PASS |
| Avatar / image area avoids broad Windows system menu behavior | PASS |
| Bottom Menu opens on first click | PASS |
| Bottom Menu closes on second click | PASS |
| Escape closes Menu | PASS |
| Chat bubble expands/collapses | PASS |
| Full App hook brings main window forward | PASS |
| Hide Pet Window hides the small window | PASS |
| Full App Show Pet brings Pet Window back | PASS |
| Reset Position returns to safe default | PASS |

## Recommended Next Stage

Recommended next task:

- TASK-132 - Pet Bubble Chat `/chat` Wiring Design

TASK-132 should be design-only before implementation. It should plan:

- Bubble loading state.
- Backend offline state.
- `llm_local`, `mock`, and error source display.
- Mood to expression integration.
- Long reply handling.
- Timeout and local cold-start hint behavior.
- Safe send flow.
- No `/chat` schema change unless explicitly planned and reviewed.

## Release Decision

Pet Mode first-stage MVP is ready to checkpoint.

It is suitable for continued manual use behind `PET_MODE_ENABLED=true`, with Bubble Chat backend wiring deferred to a separate design task.


---

# Pet Mode Release Checkpoint — TASK-163

> Task: TASK-163 - Pet Mode Release Checkpoint / Regression Smoke
> Date: 2026-05-27
> Status: DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS

This checkpoint records the completed second-stage Pet Mode surface after
TASK-148 through TASK-162. All tasks in that range are DONE - PASS and pushed.

---

## What Is Now Stable Pet Mode Behavior

The following capabilities are confirmed stable as of this checkpoint:

**Window lifecycle**
- Pet Window launches at last-saved position; falls back to a safe default on
  off-screen or missing position data.
- Pet Window hide / show cycle preserves position and in-memory state.
- Full App ↔ Pet Window IPC is fixed-channel and narrow.

**Position persistence**
- Position is saved to `userData/pet-window-state.json` on every move.
- Merge-write pattern preserves `quietMode` field when saving position.
- Reset IPC restores a safe default and saves it.

**Clean bubble speech**
- Pet Bubble shows reply text only — no source, no mood string, no provider
  prefix, no raw JSON, no stack traces, no debug markers.
- Details disclosure is collapsed by default; expands only on explicit click.

**Ollama reliability**
- Idle wake sends a keep-alive ping before the first real chat request.
- Retry logic handles Ollama cold-start latency gracefully.

**Thinking / reasoning sanitization**
- `<think>` blocks and raw reasoning tokens are stripped before display.
- No reasoning text leaks into the Pet Bubble under any circumstance.

**Thinking bubble transition (TASK-157)**
- While backend is processing: Pet Bubble enters `thinking` state.
- On success: reply replaces the thinking state cleanly.
- On error: error fallback state replaces the thinking state cleanly.

**Mood richness and expression mapping**
- Full App mood selector exposes a rich set of mood options.
- Selected mood maps to the correct Christina expression asset in Pet Window.

**Idle presence rotation (TASK-158)**
- After `PET_IDLE_LAUNCH_QUIET_MS` (120 s) on launch, idle lines begin rotating.
- Lines rotate every `PET_IDLE_ROTATION_MS` (60 s); no consecutive repeat.

**Idle timing / noise-control cooldown (TASK-159)**
- After a chat reply, idle rotation is suppressed for `PET_IDLE_COOLDOWN_MS`
  (90 s).
- Rotation delay is `max(cooldownRemaining, PET_IDLE_ROTATION_MS)`.

**Quiet Mode ON/OFF (TASK-160)**
- Toggle collapses idle bubble to `collapsed` state and stops idle rotation.
- Toggle OFF restores `idle_default` bubble and resumes rotation after cooldown.
- Chat replies, thinking bubble, error fallback, and details are not affected.

**Quiet Mode persistence (TASK-162)**
- Preference is written to `userData/pet-window-state.json` via narrow IPC
  channel `pet:set-quiet-mode`.
- On launch, persisted value is delivered as a `?quietMode=` URL param so the
  renderer applies it synchronously before first `setPetIdleDefault` — no flash.
- Missing, null, corrupt, or non-boolean stored value falls back to `false` (OFF).

**Repo hygiene (TASK-161)**
- `.gitignore` lines 38 and 41 have no trailing `\r`; Big5 bytes preserved.
- `docs/開啟方式.txt` has no CRLF line endings.
- `git diff --check` is clean from these files.

---

## Automated Validation Results (2026-05-27)

| Command | Result |
|---|---|
| `node apps/desktop/scripts/pet-renderer-smoke.js` | PASS — 83 checks |
| `node apps/desktop/scripts/pet-window-smoke.js` | PASS — 20 checks |
| `cd apps/desktop && npm.cmd run test:renderer` | PASS |
| `python -m pytest --basetemp /tmp/pytest-run163 -p no:cacheprovider` | PASS — 619 passed |
| `git diff --check` | CLEAN |

---

## Windows Manual Smoke Checklist

To be run on Windows with Ollama + backend + Electron (`PET_MODE_ENABLED=true`).

### Setup

```powershell
# Start Ollama
ollama serve

# Start backend (separate terminal)
cd backend
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# Start Electron (separate terminal)
cd apps\desktop
npm.cmd start
```

### Checklist

| # | Check | Expected | Result |
|---|---|---|---|
| 1 | Pet Window launches | Appears at last-saved position or safe default | |
| 2 | Pet Window idle bubble | Idle hint shows after launch quiet delay | |
| 3 | Pet Window idle rotation | Idle lines rotate; no two consecutive lines repeat | |
| 4 | Hide Pet Window | Window disappears | |
| 5 | Show Pet Window (Full App button) | Window reappears at same position | |
| 6 | Drag Pet Window | Position saved; survives restart | |
| 7 | Reset Pet Position | Returns to safe default | |
| 8 | Send chat message | Thinking bubble appears in Pet Window | |
| 9 | Chat reply received | Thinking state replaced by reply text only | |
| 10 | Reply text check | No source / mood / JSON / debug visible in bubble | |
| 11 | Details disclosure | Collapsed by default; expands on click | |
| 12 | Backend error scenario | Error fallback state; no raw JSON or stack trace | |
| 13 | Mood selector | Full mood option set visible in Full App | |
| 14 | Mood expression | Selected mood updates Pet expression asset | |
| 15 | Toggle Quiet Mode ON | Idle bubble collapses; idle rotation stops | |
| 16 | Chat with Quiet Mode ON | Thinking bubble and reply still appear | |
| 17 | Toggle Quiet Mode OFF | Idle bubble restores; rotation resumes after cooldown | |
| 18 | Restart with Quiet Mode ON | Quiet Mode is ON after restart; no flash | |
| 19 | Restart with Quiet Mode OFF | Quiet Mode is OFF after restart | |
| 20 | Delete `quietMode` key from JSON | Pet starts with Quiet Mode OFF; no crash | |
| 21 | Pet Bubble leakage check | Bubble never shows source, mood string, debug, thinking markers, raw JSON, provider text, stack traces, or diagnostics at any step above | |

### Known Non-Blocking Windows Notes

- **Locked `.pytest-tmp*` folders**: On Windows the NTFS mount can produce
  `PermissionError` when pytest tries to stat its own temp dirs from a prior run.
  Workaround: copy `backend/` to a non-NTFS path (e.g. `C:\tmp\backend-run163`)
  and run pytest from there, or use `--basetemp` pointing to a local temp path.
  This does not affect the backend test results — 619 tests pass.
- **`git diff --check` on `.gitignore`**: Big5-encoded lines 38/41 were cleaned
  of `\r` in TASK-161. If any tooling re-introduces CRLF, re-run the TASK-161
  byte-level patch.

---

## Checkpoint Decision

Pet Mode second-stage is ready to checkpoint.

TASK-148 through TASK-162 are all DONE - PASS. The automated gate (83 + 20 + chat
smoke + 619 pytest + `git diff --check`) passes clean. Windows manual smoke
(21-item checklist above) is the remaining gate before this checkpoint closes.

Windows manual smoke passed on 2026-05-27 — all 21 checklist items PASS.
TASK-163 is marked `DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS` in
`docs/TASKS.md` and `docs/ROADMAP.md`.

---

## Deferred Items (Out of Scope for This Checkpoint)

- Tray icon support.
- Package / installer / autostart behavior.
- Full custom character-body drag.
- Cloud / account sync for Quiet Mode preference.
- New expression assets or animation.
- Voice or audio output.
- Broad settings architecture.
- New IPC channels beyond the current narrow set.
