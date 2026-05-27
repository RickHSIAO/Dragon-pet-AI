# Pet Mode v0.1 — Demo / Portfolio Packaging

> Task: TASK-164
> Covers: TASK-148 through TASK-163
> Date: 2026-05-27
> Status: STABLE REFERENCE

This document packages the Pet Mode v0.1 feature set for demo and portfolio use.
It complements `docs/PORTFOLIO_DEMO_SCRIPT.md` (Phase 4 backend features) with the
Pet Window surface added in the TASK-148–163 range.

---

## Project Summary

Dragon Pet AI is a local-first desktop companion application built with Electron
and FastAPI. The user talks to a small animated character that lives in a frameless
always-on-top Pet Window alongside their other apps. All processing happens on
device — responses come from a locally running Ollama model, no cloud service is
contacted, and no API key is required. Pet Mode v0.1 covers the full interactive
surface: speech display, idle presence with rotation, Quiet Mode persistence,
mood-driven expression changes, and thinking bubble transitions — all backed by
a 619-test mocked backend suite and a 103-check automated desktop smoke suite.

---

## Problem Statement

Most AI assistants live in a browser tab or a chat window that competes for screen
real estate. Dragon Pet AI tries a different model: a small character window that
sits at a corner of the screen, always visible but unobtrusive, that responds when
addressed and stays quiet when not. The goal is ambient companionship rather than
on-demand query-response — something closer to having a colleague in the room than
opening a search engine.

The engineering challenge is making that feel reliable: the character must handle
Ollama cold-start latency, sanitize reasoning tokens before they reach the display,
persist user preferences across restarts, and never leak raw JSON or debug output
into the visible bubble — all without a cloud backend or an API key.

---

## Pet Mode v0.1 Feature List

Stable as of TASK-163 release checkpoint (2026-05-27):

| Feature | Task | Notes |
|---|---|---|
| Pet Window — launch / show / hide | TASK-148 | Frameless, 300 × 400, always-on-top |
| Position persistence and reset | TASK-148 | `userData/pet-window-state.json`; off-screen fallback |
| Clean bubble reply-only display | TASK-148 | No source / mood / JSON in bubble |
| Details disclosure | TASK-148 | Collapsed by default; explicit click to expand |
| Ollama keep_alive / retry | TASK-150 | Idle wake ping before first chat request |
| JSON reply unwrapping | TASK-156 | Strips Ollama's JSON-in-text wrapper if present |
| Thinking / reasoning sanitization | TASK-156 | `<think>` blocks stripped before display |
| Thinking bubble transition | TASK-157 | Thinking → reply / error replacement |
| Mood selector richness | TASK-155 | Full mood option set in Full App |
| Mood expression mapping | TASK-156 | Selected mood drives Pet expression asset |
| Idle presence rotation | TASK-158 | Lines rotate every 60 s after 120 s launch quiet |
| Idle timing / noise-control cooldown | TASK-159 | 90 s cooldown after chat reply |
| Quiet Mode ON/OFF | TASK-160 | Collapses bubble; suppresses idle rotation |
| Quiet Mode persistence | TASK-162 | Survives app restart; corrupt value falls back to OFF |
| Repo hygiene | TASK-161 | CRLF / trailing whitespace cleaned; `git diff --check` clean |
| TASK-163 regression checkpoint | TASK-163 | Full 21-item Windows manual smoke PASS |

---

## Demo Flow Script

### Setup (Windows PowerShell)

```powershell
# Terminal 1 — Ollama
ollama serve

# Terminal 2 — Backend
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 3 — Electron (Pet Mode enabled)
cd apps\desktop
$env:PET_MODE_ENABLED = "true"
npm.cmd start
```

### Step-by-step walkthrough

**1. Launch**
> "Two windows open: the Full App and a small Pet Window. The Pet Window is
> frameless, always-on-top, and 300 × 400 pixels. It opens at the last saved
> position — or a safe default if no position has been stored."

**2. Idle presence**
> "After 120 seconds of no chat activity the Pet Window starts showing idle hints
> that rotate every 60 seconds. Two consecutive hints are never the same line.
> This is the idle presence system — the character stays visible without spamming."

**3. Send a chat message (Full App)**
> "I type a message in the Full App and press Send. The Pet Window immediately
> enters a thinking state — the bubble changes to indicate the backend is working.
> This happens before the Ollama response arrives, so there is no blank waiting period."

**4. Thinking bubble → reply**
> "When the response arrives, the thinking state is replaced by the reply text.
> The bubble shows only the reply — no source label, no mood string, no JSON,
> no provider name, no stack trace. If Ollama wrapped the response in a JSON
> object, that wrapper is stripped before display."

**5. Mood expression change**
> "If I change the mood in the Full App mood selector, the Pet expression asset
> updates to match. The mapping is handled in the renderer — no backend call needed
> for expression changes."

**6. Quiet Mode ON**
> "Right-clicking the Pet Window menu gives me a Quiet Mode toggle. Turning it ON
> collapses the bubble and stops idle rotation. Chat replies and thinking bubbles
> still appear — Quiet Mode only suppresses idle noise."

**7. Quiet Mode persistence**
> "If I close the app and reopen it, Quiet Mode is still ON. The preference is
> written to `userData/pet-window-state.json` through a narrow IPC channel and
> read back as a URL param before the first idle render — no flash."

**8. Position drag and reset**
> "The Pet Window has a drag handle. I can move it to any corner. The position
> is saved automatically. The Reset Position menu item returns it to a safe default
> near the bottom-right of the primary screen."

---

## Screenshot Capture List

Capture these for portfolio use. Store as `docs/screenshots/pet_NN_name.png`.

| # | What to capture | Setup note |
|---|---|---|
| pet_01_idle | Pet Window in idle state — hint text visible | Wait 120 s after launch |
| pet_02_thinking | Pet Window in thinking state | Send a chat message; screenshot immediately |
| pet_03_reply | Pet Window showing a reply | After response arrives |
| pet_04_quiet_on | Pet Window with Quiet Mode ON — bubble collapsed | Toggle via menu |
| pet_05_mood_expression | Pet Window expression after mood change | Change mood in Full App |
| pet_06_full_app_mood | Full App mood selector open | Click the mood selector |
| pet_07_details_expanded | Full App Details disclosure expanded | Click Details after a reply |
| pet_08_smoke_pass | Terminal: `pet renderer smoke complete (83 checks)` | Run smoke script |
| pet_09_pytest_pass | Terminal: `619 passed` | Run pytest |

---

## 30–60 Second Video Recording Checklist

Record in this order to keep the clip tight. Target: 45 seconds.

1. [ ] Both windows visible at launch — point to Pet Window and Full App.
2. [ ] Pet Window idle hint rotating (speed up or pre-wait 120 s in recording).
3. [ ] Type and send a message in Full App — show thinking state in Pet Window.
4. [ ] Reply appears in Pet Window — show clean bubble, no debug text.
5. [ ] Change mood in Full App — Pet expression updates.
6. [ ] Open Pet menu — toggle Quiet Mode ON — bubble collapses.
7. [ ] Drag Pet Window to a new position.
8. [ ] Brief terminal cut: `pet renderer smoke complete (83 checks)`.

Keep narration minimal; let the UI speak. If narrating, use the talking points below.

---

## Technical Architecture Summary

```
User
  ├── Full App (Electron BrowserWindow)
  │     ├── renderer.js         — chat input, mood selector, details disclosure
  │     └── preload.js          — narrow IPC bridge (updatePetSpeech, showPetWindow)
  │
  └── Pet Window (Electron BrowserWindow — frameless, always-on-top, 300 × 400)
        ├── pet-renderer.js     — bubble state machine, idle rotation, Quiet Mode
        └── pet-preload.js      — narrow IPC bridge (setQuietMode, hidePetWindow, …)

        Both windows ↕ main.js (Electron main process)
              ├── IPC handlers  — fixed narrow channels only; contextBridge
              ├── Pet Window state — pet-window-state.json (position + quietMode)
              └── Backend HTTP  — FastAPI at localhost:8000

FastAPI backend (Python, local only)
  └── /chat → chat_service → ollama_provider → qwen3:8b (local Ollama)
```

**Key design choices:**

- **Narrow IPC bridge** — Pet Window and Full App expose only a fixed set of
  typed channels through `contextBridge`. No arbitrary `ipcRenderer` access;
  no `fs`, `shell`, or `process` in preload.
- **Merge-write state** — `pet-window-state.json` is always read before writing
  so position saves cannot overwrite `quietMode` and vice versa.
- **URL param startup** — persisted `quietMode` is delivered as `?quietMode=true`
  in the Pet Window's `loadURL` call so the renderer applies it before the first
  idle render. No async IPC round-trip; no flash.
- **Bubble state machine** — Pet Bubble has named states (`idle_default`,
  `thinking`, `collapsed`, `reply`, `error`) managed by a single `setBubbleState`
  function. UI transitions are explicit state changes, not DOM patches scattered
  across the codebase.
- **Thinking sanitization** — `<think>` blocks are stripped by `ollama_provider.py`
  before the reply leaves the backend. The renderer adds a second guard so
  reasoning tokens never reach the bubble even if the backend path changes.

---

## Safety and Reliability Highlights

| Property | How it is enforced |
|---|---|
| Clean bubble reply-only | `setBubbleState` sets only `reply` text; all other bubble content is controlled by state; no raw data path to the bubble |
| Details hidden by default | `<details>` element is closed by default; JS does not auto-open it |
| Thinking / reasoning sanitization | `ollama_provider.py` strips `<think>` blocks; renderer guards against re-injection |
| Ollama keep_alive / retry | Full App sends a keep-alive ping before the first real chat request; retry logic handles cold-start latency |
| JSON reply unwrapping | `ollama_provider.py` detects and unwraps JSON-in-text Ollama responses before returning |
| Quiet Mode persistence | Narrow IPC `pet:set-quiet-mode`; fallback to `false` on any corrupt / missing value; no crash path |
| No debug leakage | `source`, `mood`, stack traces, raw JSON, provider names, and `<think>` content are never routed to the Pet Bubble under any circumstance |
| Position persistence safety | Off-screen saved positions fall back to a safe default; merge-write prevents field clobbering |

---

## Testing and Validation Highlights

| Suite | Command | Result |
|---|---|---|
| Backend pytest | `python -m pytest --basetemp /tmp/pytest-run163 -p no:cacheprovider` | 619 passed |
| Renderer chat smoke | `cd apps/desktop && npm.cmd run test:renderer` | PASS |
| Pet renderer smoke | `node apps/desktop/scripts/pet-renderer-smoke.js` | 83 checks PASS |
| Pet window smoke | `node apps/desktop/scripts/pet-window-smoke.js` | 20 checks PASS |
| Whitespace check | `git diff --check` | CLEAN |
| TASK-163 Windows manual smoke | 21-item checklist in `docs/PET_MODE_RELEASE_CHECKPOINT.md` | PASS |

**What the smoke suites cover:**

- `pet-renderer-smoke.js` (83 checks) — bubble state transitions, idle rotation
  timing, cooldown logic, Quiet Mode ON/OFF, Quiet Mode persistence pre-apply,
  corrupt-value fallback, thinking bubble not suppressed by Quiet Mode, chat reply
  not suppressed by Quiet Mode.
- `pet-window-smoke.js` (20 checks) — static analysis of `main.js`,
  `pet-preload.js`, and `pet-renderer.js`: narrow IPC enforcement, no broad
  `ipcRenderer` exposure, `loadPetQuietMode` / `savePetQuietMode` existence,
  merge-write pattern, URL param delivery, `setQuietMode` in contextBridge.
- Backend pytest (619 tests) — mocked; no external HTTP; no real API key used
  anywhere.

---

## Suggested README / Demo Section Updates

Add or update the following in `README.md`:

1. **Pet Mode section** — brief description of the Pet Window, how to enable it
   (`PET_MODE_ENABLED=true`), and what it shows.
2. **Updated one-liner** — include Pet Mode in the project summary sentence.
3. **Updated test count** — currently 619 pytest + 83 + 20 desktop smoke checks.
4. **Screenshot** — add `pet_03_reply.png` and `pet_01_idle.png` once captured.
5. **Demo script link** — add a link to this document alongside the existing
   `PORTFOLIO_DEMO_SCRIPT.md` link.

---

## Interview Talking Points

**Why Electron + FastAPI?**

Electron gives a native desktop window with a full web renderer — useful for a
companion UI that needs to be always-on-top, frameless, and transparent.
FastAPI gives a typed HTTP API with Pydantic validation, which makes it easy to
add features (memory, settings, usage metering) as separate endpoints without
touching existing schema. The two layers communicate over localhost; no external
network is involved.

**Why local Ollama support matters**

Ollama runs a model on the user's own GPU or CPU. No API key, no per-token cost,
no data leaving the machine. For a companion app that runs continuously in the
background, cloud costs and privacy exposure would be significant concerns. Ollama
removes both. The trade-off is cold-start latency, which the keep_alive/retry
design handles.

**How the UI state machine was handled**

The Pet Bubble is not a free-form DOM patch target. It has a fixed set of named
states managed by a single `setBubbleState` function. Every transition goes through
that function; nothing sets CSS classes or text content directly outside of it.
This made it straightforward to add Quiet Mode (a new state) and the thinking
bubble (a transition sequence) without breaking the existing idle and reply paths.
The 83-check smoke suite runs against the state machine with a fake timer so
timing-sensitive tests are deterministic.

**How testing reduced regression risk**

Each new feature came with smoke tests before it was considered done. When Quiet
Mode (TASK-160) was added, 4 existing idle tests were updated to assert the
`collapsed` state rather than idle text, and 1 new test was added for the collapse
behavior. When persistence (TASK-162) was added, 6 new tests verified URL param
pre-apply, corrupt-value fallback, and non-suppression of chat replies. The TASK-163
regression checkpoint then ran the full 21-item Windows manual smoke against the
combined feature set. This layered approach meant regressions were caught at the
unit level before the manual pass, making the manual pass faster and more reliable.

**What would you improve next?**

Three things in priority order: (1) Replace the `<details>` disclosure with a
proper modal or slide-out panel — the current `<details>` approach works but is
not the most polished UX. (2) Add a tray icon so the Pet Window can be restored
without keeping the Full App open. (3) Implement streaming replies so the bubble
updates word-by-word rather than appearing all at once — this would make the
companion feel more responsive and less like a loading spinner.

---

## What Not to Claim

| Do not claim | Correct statement |
|---|---|
| Production-ready | Prototype / portfolio project |
| Cloud-free by policy | Cloud-free by architecture — all providers are local or user-supplied |
| Live streaming replies | Reply appears after full Ollama response; streaming is not implemented |
| Voice / audio output | Not implemented |
| Tray icon | Not implemented |
| Multiple simultaneous Pet characters | Single Pet Window |
| Packaged / installable | No installer; run from source |

---

## Reference

| Document | Topic |
|---|---|
| `docs/PET_MODE_RELEASE_CHECKPOINT.md` | Full TASK-148–163 regression checkpoint and 21-item Windows smoke record |
| `docs/PET_MODE_MANUAL_SMOKE_RUNBOOK.md` | Step-by-step manual smoke instructions for Windows |
| `docs/PORTFOLIO_DEMO_SCRIPT.md` | Phase 4 backend features demo script (memory, audit, BYOK, Test Connection) |
| `docs/PORTFOLIO_SCREENSHOT_CHECKLIST.md` | Phase 4 screenshot capture plan |
| `docs/TASKS.md` | Full task history (TASK-001 onward) |
| `docs/ROADMAP.md` | Phase-by-phase status |
| `docs/LOCAL_DEV_RUNBOOK.md` | Full local dev setup and troubleshooting |
