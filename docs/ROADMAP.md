# Development Roadmap

> dragon-pet-ai
> Status: LIVING DOCUMENT
> Last Updated: 2026-05-24
> Owner: TASK-001

---

## Overview

The project is developed in discrete phases. Each phase has a clearly defined scope and must not implement features belonging to later phases.

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
Docs      Skeleton  Chat+Char  Memory    LLM+AI    Assistant
```

---

## Phase 0 — Project Definition

**Goal:** Establish the project structure, specifications, and documentation before writing any runtime code.

**Status:** COMPLETE

| Task | Name | Status |
|---|---|---|
| TASK-000 | Project Skeleton | DONE |
| TASK-001 | MVP PRD and Initial Architecture | DONE |
| TASK-002 | Character Spec and Memory System Spec | DONE |

---

## Phase 1 — Basic Runtime Skeleton

**Goal:** Establish the running skeleton of both the backend and desktop app. No real AI, no real features ??just the infrastructure working end-to-end.

**Status:** COMPLETE

| Task | Name | Status |
|---|---|---|
| TASK-003 | FastAPI backend skeleton + /health + /chat mock | DONE |
| TASK-004 | Electron desktop shell + chat UI | DONE |

**Exit Criteria ??Met:**
- `uvicorn` starts the backend without errors ??
- `npm start` opens the Electron window ??
- Desktop can POST to `/chat` and display the mock response ??

---

## Phase 2 — Chat and Character

**Goal:** Wire up character state, conversation history, and SQLite persistence.

**Status:** COMPLETE

| Task | Name | Status |
|---|---|---|
| TASK-005 to TASK-014 | Chat modes, character state, relationship state, SQLite persistence, memory table skeleton | DONE |

---

## Phase 3 — Memory and State

**Goal:** Add long-term memory, memory-aware chat, and audit inspection.

**Status:** COMPLETE

| Task | Name | Status |
|---|---|---|
| TASK-015 | Manual memory injection design | DONE |
| TASK-016 | Memory injection safety review | DONE |
| TASK-017 | Apply memory injection safety review changes | DONE |
| TASK-018 | Approved Memory Context Builder | DONE |
| TASK-019 | Memory Injection Audit Log Skeleton | DONE |
| TASK-020 | Feature Flagged Memory-Aware Chat Wiring | DONE |
| TASK-021 | Feature Flagged Memory-Aware Chat Runtime Smoke Check | DONE |
| TASK-022 | Memory-Aware Chat UI Toggle Design | DONE |
| TASK-023 | Memory-Aware Chat UI Toggle Implementation | DONE |
| TASK-024 | Memory-Aware Chat Runtime Smoke Check | DONE |
| TASK-025 | Memory Injection Audit Inspection Design | DONE |
| TASK-026 | Memory Injection Audit Inspection API | DONE |
| TASK-027 | Memory Injection Audit UI | DONE |
| TASK-028 | Audit Inspection Runtime Smoke Check | DONE |
| TASK-029 | Phase 3 Stabilization and Demo Summary | DONE |

**Phase 3 Deliverables Completed:**
- All messages persisted to SQLite ??
- Manual memory CRUD API ??
- Memory management UI ??
- Approved memory context builder with safety filters ??
- Memory-aware chat with two-layer safety gate ??
- MemoryInjectionAudit model + audit row creation ??
- Audit inspection API (read-only, paginated, safe metadata only) ??
- Audit Logs UI ??
- pytest: 226 passed, 0 failed ??
- All runtime smoke checks passed ??

**Not implemented in Phase 3 (remains deferred):**
- Real AI / LLM provider
- Voice (TTS / STT)
- Live2D
- Semantic retrieval / vector database
- Automatic memory extraction

---

## Phase 4 — LLM Adapter Integration

**Goal:** Wire the approved memory context pipeline to a real LLM provider behind a feature flag, using an adapter pattern that keeps mock as the default.

**Status:** IN PROGRESS ??provider adapter exists behind flags; mock `/chat` LLM wiring smoke passed; real-provider `/chat` wiring contract tests passed with mocked HTTP only; in-memory usage meter, non-secret provider settings API, Provider Settings UI, secure key storage abstraction, key save/clear endpoints, key UI enablement, Provider Test Connection design, backend Test Connection implementation (TASK-059), Opus safety review PASS (TASK-059R), Test Connection UI enablement (TASK-060), hardening tests (TASK-062), and Provider Settings UI layout polish (TASK-063) are complete; explicit cost acknowledgement required per click; no automatic test after Save Key; no live external API call; live provider remains disabled by default

**Recommended primary path: Option A ??LLM Adapter Integration**

| Option | Description | Notes |
|---|---|---|
| **A ??LLM adapter integration** 漎?selected | Wire approved memory context to a real LLM behind explicit flags | TASK-031 ??TASK-051 |
| B ??TTS voice output | Add basic text-to-speech output | Deferred ??more valuable after real LLM is wired |
| C ??UI polish and packaging | Improve layouts, scrolling, package as installable app | Deferred ??better after LLM adapter done |
| D ??Daily summary / memory review | Generate end-of-day summaries and memory review UI | Deferred ??requires LLM adapter first |

**Task Sequence:**

| Task | Name | Status |
|---|---|---|
| TASK-030 | Phase 4 Planning | DONE |
| TASK-031 | LLM Adapter Design | DONE |
| TASK-032 | LLM Provider Interface Skeleton | DONE |
| TASK-033 | Mock Provider Compatibility Tests | DONE |
| TASK-034 | Real Provider Config Design | DONE |
| TASK-034R | Real Provider Config Safety Review (Opus) | DONE ??PASS WITH CHANGES |
| TASK-034F | Apply Real Provider Config Review Fixes | DONE |
| TASK-035 | Real Provider Integration Behind Feature Flag | DONE |
| TASK-036 | Real Provider Vendor Contract Design | DONE |
| TASK-037 | Real Provider Contract Tests | DONE |
| TASK-038 | Manual Live LLM Provider Smoke Check | IN_PROGRESS |
| TASK-039 | Chat Service LLM Wiring Design | DONE |
| TASK-040 | Chat Service LLM Wiring Behind Feature Flag | DONE |
| TASK-041 | Chat LLM Wiring Mock Runtime Smoke Check | DONE |
| TASK-042 | Chat LLM Real Provider Wiring Design | DONE |
| TASK-043 | Chat Real Provider Wiring Contract Tests | DONE |
| TASK-044 | Cost Control and Live Smoke Go/No-Go Design | DONE |
| TASK-045 | BYOK Product and Settings Design | DONE |
| TASK-046 | Usage Meter Design | DONE |
| TASK-047 | Provider Settings UI Design | DONE |
| TASK-048 | Backend Provider Settings API Design | DONE |
| TASK-049 | Secure Key Storage Design | DONE |
| TASK-050 | Usage Meter Implementation | DONE |
| TASK-051 | Backend Provider Settings API Implementation | DONE |
| TASK-052 | Provider Settings UI Implementation | DONE |
| TASK-053 | Secure Key Storage Implementation | DONE |
| TASK-054 | Provider Settings Key Endpoint Implementation | DONE |
| TASK-055 | Provider Settings Key UI Enablement Design | DONE |
| TASK-056 | Provider Settings Key UI Enablement Implementation | DONE |
| TASK-057 | Provider Settings Key UI Smoke Check | DONE |
| TASK-058 | Provider Test Connection Design | DONE |
| TASK-059 | Provider Test Connection Backend Implementation | DONE |
| TASK-059R | Provider Test Connection Safety Review (Opus) | DONE ??PASS |
| TASK-060 | Provider Test Connection UI Enablement | DONE |
| TASK-061 | Provider Test Connection Runtime Smoke Check | DONE ??PASS WITH EXPECTED LIMITATION |
| TASK-062 | Provider Test Connection Hardening Tests | DONE |
| TASK-063 | Electron Provider Settings UI Polish and Layout Fix | DONE |
| TASK-064 | Provider Settings UI Runtime Smoke Re-check | DONE ??PASS WITH NON-BLOCKING UI NOTES |
| TASK-065 | Phase 4 Provider Settings Stabilization Summary | DONE |
| TASK-066D | Portfolio Demo Script and Screenshots | DONE |
| TASK-067D | Portfolio README Polish | DONE |
| TASK-068D | Portfolio Screenshot Checklist Capture | DONE |
| TASK-069D | Portfolio Screenshot Capture Session | DONE |
| TASK-070D | Embed Portfolio Screenshots in README | DONE |
| TASK-071D | Portfolio Demo Final Review | DONE |
| TASK-072 | Local Ollama Provider Design | DONE |
| TASK-073 | Ollama Provider Implementation Behind Feature Flag | DONE |
| TASK-074 | Ollama Provider Contract Tests and Runtime Smoke Prep | DONE |

**Phase 4 Key Safety Constraints:**
- `LLM_PROVIDER_ENABLED=false` is the default; real provider requires explicit opt-in via env var
- `LLM_CHAT_ENABLED=false` must gate `/chat` LLM adapter use separately from provider selection
- API key loaded from environment variable only ??never hardcoded, never logged, never sent to frontend, never in repr/str
- `/chat` response schema remains `reply / mood / source` ??unchanged
- Memory-aware chat two-layer gate is unchanged
- No automatic retries in Phase 4 (at most one real provider call per `/chat` turn)
- Non-2xx provider response bodies are opaque ??not parsed, not logged, not returned
- No tool execution, no file access, no autonomous action, no automatic memory extraction
- Live smoke is blocked until explicit user cost confirmation and TASK-044 go/no-go criteria are satisfied
- BYOK is the recommended MVP path; provider settings UI design done (TASK-047); backend API design done (TASK-048); secure key storage design done (TASK-049); usage meter implementation done (TASK-050); non-secret settings API implementation done (TASK-051); Provider Settings UI implementation done (TASK-052); secure key storage abstraction done (TASK-053); provider key save/clear endpoints done (TASK-054); key UI enablement design done (TASK-055); Save Key / Clear Key UI done (TASK-056); key UI smoke passed (TASK-057); Test Connection design done (TASK-058); Test Connection backend done (TASK-059); safety review PASS (TASK-059R); Test Connection UI enabled in renderer (TASK-060); runtime smoke PASS WITH EXPECTED LIMITATION (TASK-061); hardening tests DONE ??470 passed (TASK-062); Provider Settings UI readability/layout polish DONE (TASK-063); runtime smoke re-check PASS WITH NON-BLOCKING UI NOTES (TASK-064); Phase 4 Provider Settings stabilization summary created (TASK-065); portfolio demo script created (TASK-066D); README polished as portfolio-friendly entry point (TASK-067D); no live external provider call has occurred; no real API key has been used; project is demo-ready as local-first prototype

See `docs/PHASE4_PLAN.md`, `docs/LLM_ADAPTER_DESIGN.md`, `docs/LLM_PROVIDER_CONTRACT.md`, `docs/CHAT_LLM_WIRING_DESIGN.md`, `docs/CHAT_LLM_REAL_PROVIDER_WIRING_DESIGN.md`, `docs/COST_AND_MONETIZATION.md`, `docs/BYOK_PRODUCT_AND_SETTINGS.md`, `docs/USAGE_METER_DESIGN.md`, `docs/PROVIDER_SETTINGS_UI_DESIGN.md`, `docs/PROVIDER_SETTINGS_API_DESIGN.md`, `docs/SECURE_KEY_STORAGE_DESIGN.md`, `docs/PROVIDER_TEST_CONNECTION_DESIGN.md`, and `docs/OLLAMA_PROVIDER_DESIGN.md` for full planning and design documents.

---

## Phase 4 Extension ??Local Ollama Provider Track

**Goal:** Add a local LLM provider option via Ollama. No API key, no external network, no per-token cost. Runs on user's hardware.

**Status:** LOCAL OLLAMA MVP CHECKPOINT COMPLETE - OllamaLocalProvider implemented (TASK-073), mocked contract tests pass (TASK-074), runtime smoke PASS (TASK-075), Provider Settings UI Ollama option complete (TASK-076), README local LLM instructions complete (TASK-077), Electron end-to-end local chat smoke PASS (TASK-080), source/loading/error UX stabilized (TASK-081), release readiness review PASS (TASK-082), mood to pet expression mapping (TASK-083), Christina visual asset pipeline through normalized candidates complete (TASK-084 to TASK-093), persisted settings runtime smoke PASS WITH NOTES (TASK-101), partial persist guard and local cold-start UX fix complete (TASK-102)

**Local model candidates:**

| Model | Speed (warm) | Throughput | Verdict |
|---|---|---|---|
| `qwen3:8b` | ~0.35s | ~73 tok/s | **Recommended ??MVP default** |
| `gemma3:12b` | ~3.48s | ~13 tok/s | Usable; better tone, slower |

**Task Sequence:**

| Task | Name | Status |
|---|---|---|
| TASK-072 | Local Ollama Provider Design | DONE |
| TASK-073 | Ollama Provider Implementation Behind Feature Flag | DONE |
| TASK-074 | Ollama Provider Contract Tests and Runtime Smoke Prep | DONE |
| TASK-075 | Ollama Runtime Smoke Check | DONE |
| TASK-076 | Provider Settings UI ??Ollama Option | DONE |
| TASK-077 | README Update for Local LLM Mode | DONE |
| TASK-080 | Electron End-to-End Local Chat Smoke | DONE |
| TASK-081 | Local Ollama UX Stabilization / Runtime Follow-up | DONE |
| TASK-082 | Local Ollama Release Readiness Review | DONE |
| TASK-083 | Mood ??Pet Expression Mapping (Electron UI) | DONE |
| TASK-084 | Christina Visual Asset Pipeline | DONE |
| TASK-085 | Create Christina Neutral Expression PNG | DONE |
| TASK-086 | Renderer Image Asset Fallback | DONE |
| TASK-087 | Neutral PNG Electron Visual Verification | DONE |
| TASK-088 | Phase 4 Extension Checkpoint / Commit Prep | DONE |
| TASK-094 | Approve Normalized Christina Candidates and Replace Runtime PNGs | DONE |
| TASK-095 | Create Christina Worried and Sleepy Expression PNGs | DONE (TASK-095-RESUME) |
| TASK-096 | Create Christina System-State Expression PNGs (pending/error/offline) | BLOCKED — awaiting source images |
| TASK-097 | Expression Set Checkpoint and Commit Review | DONE |
| TASK-098 | UI Polish Pass | DONE |
| TASK-099 | Desktop Settings Persistence Review | DONE |
| TASK-100 | Settings Persistence Runtime Smoke | DONE |
| TASK-101 | Post-Checkpoint Manual App Smoke | DONE |
| TASK-101-RERUN | Post-TASK-102 Runtime Smoke | DONE |
| TASK-102 | Provider Settings Partial Persist Guard + Ollama Cold Start UX | DONE |
| TASK-103 | Local Dev Launch / One-command Startup | DONE |
| TASK-104 | Manual Windows Script Smoke | DONE |
| TASK-105 | Cold-start Warmup UX for dev-smoke | DONE |
| TASK-106 | Manual Cold-start Warmup UX Smoke | DONE |
| TASK-089 | Create Christina Focused Expression PNG | DONE |
| TASK-090 | Christina Real Expression Asset Plan | DONE |
| TASK-091 | Integrate Existing Christina Expression PNG Assets | DONE |
| TASK-092 | Christina Expression Visual QA and 512x512 Normalization Review | DONE |
| TASK-093 | Normalize Existing Christina Expression PNGs to 512x512 Face/Bust | DONE |

**Key design decisions:**
- `OllamaLocalProvider` implements the same `ProviderInterface` as `AnthropicProvider` ??no service layer changes required
- `source=llm_local` in `/chat` response ??schema unchanged
- No API key; no `explicit_cost_ack` required ??local resource warning instead
- `keep_alive=10m` to avoid cold-start latency on repeated calls
- `think=false`, `stream=false` ??concise, deterministic responses
- Renderer never calls Ollama directly ??backend-only architecture boundary preserved
- New key status value: `not_required` for providers that need no key
- TASK-074 strengthened mocked contract coverage to 34 Ollama tests and added `docs/OLLAMA_RUNTIME_SMOKE_CHECKLIST.md`; pytest: 504 passed; no external provider call and no API key used
- TASK-077 documents Local LLM mode in README/backend README, including Ollama prerequisites, startup, Provider Settings UI behavior, `/chat` smoke test, troubleshooting, and safety constraints; latest pytest: 531 passed
- TASK-080 confirms Electron Provider Settings, Test Connection, and chat UI work end-to-end with local Ollama; `/chat` response stayed `reply / mood / source`, `source=llm_local` was confirmed, and renderer still has no direct Ollama URL
- TASK-081 makes source, provider state, local cold-start loading, backend offline, provider timeout, local error, and mock fallback states visible in the Electron UI; renderer smoke covers these states
- TASK-082 release readiness review confirms docs, smoke flow, fallback policy, source display strategy, dirty diff, and safety scans are aligned for a Local Ollama MVP checkpoint
- TASK-091 integrates existing user-provided Christina expression PNGs for `focused`, `happy`, `proud`, and `annoyed`; renderer smoke verifies integrated PNG loading and SVG fallback for missing moods
- TASK-092 adds an 80x80 local preview and confirms the full-body expression assets are functional but too small compared with neutral; preferred next step is 512x512 face/bust normalization, not a pet container resize
- TASK-093 adds a reproducible normalization script plus QA-only 512x512 candidates for `focused`, `happy`, `proud`, and `annoyed`; runtime PNGs are not replaced yet
- TASK-101 confirms the persisted Local Ollama checkpoint works in manual Windows runtime smoke, with notes on partial settings persistence risk and cold-start timeout.
- TASK-102 fixes partial PATCH persistence guards, prevents renderer pre-load/default saves, isolates pytest from the developer runtime settings file, adds `LLM_LOCAL_CHAT_TIMEOUT_SECONDS`, and improves local cold-start timeout messaging without changing `/chat` schema.
- TASK-101-RERUN verifies all TASK-102 behavioral guards in a sandbox runtime smoke: partial PATCH preservation ✓, explicit null model guard ✓, Test Connection no-mutate ✓, cold-start source=llm_local_error with fallback disabled ✓, persistence after restart ✓. pytest: 586 passed.
- TASK-105 improves `dev-smoke.ps1` cold-start UX: raises `/chat` client timeout to 100 s, adds `Write-WarmupHint` with exact `ollama run qwen3:8b` command, distinguishes network-timeout from hard failure, treats `llm_local_error` as non-fatal cold-start state. No backend or renderer changes.
- TASK-106 manual Windows cold-start UX smoke PASSED: `dev-smoke.ps1` executed successfully after `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`; `/health` PASS, `/provider/settings` PASS (provider=ollama, model=qwen3:8b, fallback_to_mock=false), `/provider/settings/test` PASS (source=llm_local), `/chat` PASS (HTTP 200, source=llm_local, mood=happy), schema guard PASS (reply/mood/source), `ALL CHECKS PASSED`.
- TASK-104 manual Windows smoke confirms `source=llm_local` with real `qwen3:8b` generation; documents ExecutionPolicy bypass (`-Scope Process`) and cold-start warm-up (`ollama run qwen3:8b`) as one-time steps. No code changes.
- TASK-103 adds one-command PowerShell startup scripts (`dev-start-backend.ps1`, `dev-start-desktop.ps1`, `dev-smoke.ps1`) and `docs/LOCAL_DEV_RUNBOOK.md`; addresses port-8000 check, venv activation, `npm.cmd` vs `npm.ps1` execution-policy issue, `ELECTRON_RUN_AS_NODE` clear, cold-start timeout guidance, and settings persistence troubleshooting. No product features changed.

See `docs/OLLAMA_PROVIDER_DESIGN.md` for full design.

---

## Phase 5 — Companion Behavior Loop

**Goal:** 讓克莉絲蒂娜從「聊天框」進化為真正的桌面寵物，具備 idle 狀態、greeting、time-aware 語氣、expression 整合，以及輕量 proactive 存在感。

**Status:** COMPLETE — TASK-107～112 全數 DONE（2026-05-24）

> 設計文件：`docs/PHASE5_COMPANION_BEHAVIOR_PLAN.md`

| Task | Name | Status |
|---|---|---|
| TASK-107 | Phase 5 Planning: Companion Behavior Loop | DONE |
| TASK-108 | Idle State UI Behavior | DONE |
| TASK-109 | Startup Greeting | DONE |
| TASK-110 | Return-from-Away Greeting | DONE |
| TASK-111 | Expression Timing Polish | DONE |
| TASK-112 | Companion Behavior Smoke Tests | DONE |
| TASK-113 | Sticky Chat Composer / Better Chat Scroll UX | DONE |

**Phase 5 安全邊界（永久性限制）：**
- Renderer 不自動讀取任何本機檔案
- 不整合 Email / Calendar / 任何外部系統資料
- 不執行 shell 命令或系統操作
- 不呼叫任何外部 API（僅允許 `localhost:8000`）
- 不使用精確定位（僅 `new Date().getHours()` 判斷時段）
- 所有 proactive 訊息僅顯示於 UI，不自動操作系統
- `/chat` schema 維持 `reply / mood / source` 不變
- Renderer 不直連 Ollama（`localhost:11434`）

**Key design decisions:**
- TASK-107 confirms Phase 5 MVP is pure-frontend (renderer.js only); no new backend endpoints for companion behavior.
- Idle timer uses `setInterval` + `lastActivityTime`; expression changes via existing `setPetExpression(mood)`.
- Startup and return greetings are pre-written (not LLM calls) to avoid cold-start dependency.
- Time-aware behavior uses `new Date().getHours()` client-side only; no time data sent to backend.
- Anti-spam: `hasGreetedThisSession` flag + `RETURN_THRESHOLD` guard; max one proactive per session.
- Expression priority: `/chat` backend `mood` field overrides idle state immediately on response.

---

## Future Product Track — Streamer Companion Mode

> Status: SIDE TRACK — design exploration only; not scheduled for implementation
> See: `docs/STREAMER_COMPANION_MODE.md`

---

## Phase 6 - Pet Mode UI Track

**Goal:** Move the product from a full management interface toward a small desktop pet plus compact chat bubble, while keeping Full App Mode as the control center.

**Status:** RELEASE CHECKPOINT COMPLETE - TASK-114 design complete; TASK-115 static renderer skeleton complete; TASK-116 env-gated BrowserWindow prototype complete; TASK-117 CSS drag behavior complete; TASK-118 local-only bubble UI state complete; TASK-119 narrow Pet-to-Full mode switch complete; TASK-120 smoke checkpoint passed; TASK-121 manual Windows visual smoke passed with menu placeholder note; TASK-122 Pet Window position persistence complete; TASK-123 Pet menu/right-click menu complete; TASK-124 manual menu smoke passed with right-click drag-region note; TASK-125 right-click menu hotspot fix complete; TASK-126 menu UX regression fixed; TASK-127 explicit drag handle complete; TASK-128 Full App -> Show Pet bridge complete; TASK-129 drag regression fix complete; TASK-130 manual Windows drag/menu smoke passed; TASK-131 Pet Mode release checkpoint complete; TASK-132 Bubble Chat wiring design complete; TASK-133 static bubble state refinement complete; TASK-134 Pet Bubble `/chat` client wiring complete; TASK-135 Pet Bubble loading/error UX complete; TASK-136 Pet Bubble mood/expression integration complete; TASK-137 Pet Bubble long reply handling complete; TASK-138 Pet Bubble chat smoke checkpoint complete; TASK-140 Pet Bubble input visibility regression fixed; TASK-141 display-only speech bubble redesign complete; TASK-143 Full App reply mirror bridge complete; TASK-144 manual Windows speech mirror smoke PASS WITH NOTE; TASK-145 clean reply/details disclosure complete and Windows manual smoke PASS; TASK-146 menu/controls consolidation design defined.

> Design reference: `docs/PET_MODE_UI_DESIGN.md`
> Release checkpoint: `docs/PET_MODE_RELEASE_CHECKPOINT.md`
> Bubble Chat wiring design: `docs/PET_BUBBLE_CHAT_WIRING_DESIGN.md`

| Task | Name | Status |
|---|---|---|
| TASK-114 | Pet Mode UI Design | DONE |
| TASK-115 | Create Pet Window Design Skeleton | DONE |
| TASK-116 | Pet Mode BrowserWindow Prototype | DONE |
| TASK-117 | Pet Mode Drag Behavior | DONE |
| TASK-118 | Pet Bubble Chat Design | DONE |
| TASK-119 | Mode Switch Full App <-> Pet Mode | DONE |
| TASK-120 | Pet Mode Smoke Tests | DONE |
| TASK-121 | Manual Windows Pet Mode Visual Smoke | DONE - PASS WITH NOTE |
| TASK-122 | Pet Window Position Persistence | DONE |
| TASK-123 | Pet Mode Menu / Right-click Menu | DONE |
| TASK-124 | Manual Windows Pet Menu Smoke | DONE - PASS WITH NOTE |
| TASK-125 | Fix Pet Right-click Menu Hit Area | DONE |
| TASK-126 | Fix Pet Menu UX Regression | DONE |
| TASK-127 | Replace Large Pet Drag Region with Explicit Drag Handle | DONE |
| TASK-128 | Full App -> Show Pet Window Bridge | DONE |
| TASK-129 | Fix Pet Window Drag Regression | DONE |
| TASK-130 | Manual Windows Pet Drag/Menu Smoke | DONE - PASS |
| TASK-131 | Pet Mode Release Checkpoint | DONE |
| TASK-132 | Pet Bubble Chat `/chat` Wiring Design | DONE |
| TASK-133 | Pet Bubble Chat Static State Refinement | DONE |
| TASK-134 | Pet Bubble `/chat` Client Wiring | DONE |
| TASK-135 | Pet Bubble Loading/Error UX | DONE |
| TASK-136 | Pet Bubble Mood/Expression Integration | DONE |
| TASK-137 | Pet Bubble Long Reply Handling | DONE |
| TASK-138 | Pet Bubble Chat Smoke Tests | DONE |
| TASK-139 | Manual Windows Pet Bubble Chat Smoke | DONE - SUPERSEDED / RESOLVED |
| TASK-140 | Fix Pet Bubble Input Visibility | DONE |
| TASK-141 | Redesign Pet Bubble as Display-only Speech Bubble | DONE |
| TASK-143 | Mirror Full App Chat Reply to Pet Speech Bubble | DONE |
| TASK-144 | Manual Windows Full App -> Pet Speech Mirror Smoke | DONE - PASS WITH NOTE |
| TASK-145 | Pet Speech Bubble Clean Reply + Details Disclosure | DONE - PASS |
| TASK-146 | Pet Mode Menu / Controls Consolidation Design | DEFINED - READY FOR IMPLEMENTATION |

**Recommended direction:**

- Full App Mode remains the full chat, memory, audit, provider settings, usage, and debug surface.
- Pet Mode becomes a compact transparent/frameless/always-on-top desktop companion window.
- Pet Bubble should live inside the Pet Window as a display-only speech bubble.
- Full App is the primary text input surface.
- Pet Mode should use a separate renderer instead of reusing the full management UI directly.
- Pet Mode should reuse Christina expression assets.
- Pet Mode should call only the local backend and preserve `/chat` response schema: `reply / mood / source`.

**Safety constraints:**

- No automatic file, Email, Calendar, screen, microphone, command, or external API access.
- No autonomous LLM calls for startup, idle, or return-from-away.
- No renderer direct Ollama calls.
- No API key exposure to renderer code.
- No `/chat` schema change.

**Checkpoint notes:**

- Pet Mode still opens only with `PET_MODE_ENABLED=true`.
- Full App remains the default startup surface.
- Bubble Chat is wired to the existing local backend `/chat` in Pet Mode and still preserves `/chat` response schema.
- Pet-to-Full switch uses only `window.dragonPet.openFullApp()` over fixed IPC channel `pet:open-full-app`.
- TASK-120 verification passed: pet renderer smoke, pet window/preload smoke, existing renderer smoke, backend pytest 586 passed, direct-Ollama scan clean, and `git diff --check` clean.
- TASK-121 manual Windows visual smoke passed: drag, bubble expand/collapse, Full App focus hook, backend/provider status, and always-on-top all passed. Menu hook remains a placeholder note and is not implemented yet.
- TASK-122 persists Pet Window position to Electron `userData/pet-window-state.json`, saves on move/close, restores on next `PET_MODE_ENABLED=true` startup, and falls back to a primary-display bottom-right default if the saved center point is off-screen.
- TASK-123 implements the Menu hook and right-click DOM menu with Open Full App, Reset Pet Position, Hide Pet Window, and Close Menu. Reset/Hide use fixed narrow preload APIs and fixed IPC channels only.
- TASK-124 manual Windows Pet Menu smoke passed with note: Menu hook, close, Open Full App, Reset Pet Position, Hide Pet Window, relaunch position restore, and Bubble Chat placeholder passed; right-click works only on non-drag/lower area because the top avatar/image drag region does not receive renderer `contextmenu` events. Follow-up: TASK-125 Fix Pet right-click menu hit area.
- TASK-125 fixes the practical right-click hit area by adding an explicit upper-right `pet-no-drag` menu hotspot inside the Pet stage. The main avatar/stage remains draggable; right-click on pure drag-region pixels may still be limited by Electron behavior, so the supported target is now visible and reliable.
- TASK-126 removes the visible upper-right hotspot after Windows UX testing showed it looked like a duplicate Menu button. The bottom Menu button is now the primary custom menu entry and toggles open/closed. Windows drag-region right-click may show the OS system menu; full-window custom right-click is deferred unless a future custom drag implementation replaces CSS native drag.
- TASK-127 replaces the large avatar/stage drag region with a small explicit top `#pet-drag-handle`. Avatar, bubble, menu, and controls are no-drag interaction areas. Right-click on the handle may still show the Windows OS system menu; whole-character drag without that behavior is deferred to a future custom drag implementation.
- TASK-128 adds a narrow Full App -> Pet Window bridge. The Full App header has a `Show Pet` button that calls only `window.dragonPet.showPetWindow()` through fixed IPC channel `pet:show-window`. If Pet Mode is disabled, the Full App shows a local disabled message. Bubble Chat remains local placeholder UI only.
- TASK-129 fixes the drag regression by enlarging the explicit `#pet-drag-handle` from a tiny grip into a `156 x 24 px` top bar with a visible CSS grip line, higher z-index, and pointer-events enabled. Large avatar/body drag remains intentionally disabled to avoid Windows system menu interference.
- TASK-130 manual Windows drag/menu smoke passed: drag handle, avatar no-system-menu behavior, Menu toggle, Escape close, bubble expand/collapse, Pet -> Full App, Hide Pet Window, Full App Show Pet, and Reset Position all passed. No remaining note for this checkpoint.
- TASK-131 closes the first-stage Pet Mode MVP checkpoint in `docs/PET_MODE_RELEASE_CHECKPOINT.md`. Pet Mode is maintainable behind `PET_MODE_ENABLED=true`; Bubble Chat `/chat` wiring remains deferred to TASK-132 design.
- TASK-132 designs Pet Bubble Chat `/chat` wiring in `docs/PET_BUBBLE_CHAT_WIRING_DESIGN.md`. It preserves `/chat` schema as `reply / mood / source`, plans loading/offline/source/mood/long-reply UX, and keeps implementation deferred.
- TASK-133 refines Pet Bubble static DOM/CSS/local renderer state for `collapsed`, `expanded`, `composing`, `empty_input`, `pending`, `success`, `backend_offline`, `timeout`, `llm_local_error`, `fallback_mock`, and `long_reply`. It keeps all behavior local: no backend call, no `/chat` call, no schema change, no IPC expansion.
- TASK-134 wires Pet Bubble Chat to the existing local backend `/chat` using the Full App request shape `{ message, use_memory }` and response schema `reply / mood / source`. Pet Mode fixes `use_memory=false`, maps `source` into compact bubble states, maps `mood` to existing Christina expression PNGs, handles network failure as `backend_offline`, and keeps direct Ollama access blocked.
- TASK-135 adds Pet Bubble timeout/cold-start handling with `PET_CHAT_TIMEOUT_MS = 100000`, restores input/send after completion, preserves input for retry on offline/timeout/local-error/malformed responses, prevents duplicate pending submits, and keeps raw diagnostics out of the bubble.
- TASK-136 unifies Pet Bubble mood/expression mapping through `normalizePetMood`, `setPetExpression`, and `setPetExpressionForBubbleState`. Response `success` uses backend `mood`; local states map to existing Christina PNG moods only: pending/focused, offline/worried, timeout/sleepy, local-error/worried, mock/proud, empty-input/annoyed, long-reply/focused.
- TASK-137 defines long reply threshold as `PET_REPLY_LONG_THRESHOLD = 160`, routes long backend replies through `long_reply`, shows `回覆較長，可開 Full App 查看完整內容。`, keeps response text internally scrollable, and reinforces `220 x 280` layout constraints with no new backend, IPC, API, or schema change.
- TASK-138 strengthens Pet Bubble smoke coverage to 29 checks across success, empty input, source mapping, mood expression, timeout/offline/malformed errors, long replies, pending duplicate guard, retry/next-send behavior, layout hooks, and direct-Ollama safety. Runtime code was not changed.
- TASK-139 Windows manual smoke found a Pet Bubble layout regression: the bubble expanded and displayed status/response/legacy placeholder text, but input and Send were clipped out of the visible Pet Window. That original manual smoke path is not recorded as PASS; it is closed as superseded/resolved by TASK-140's regression fix, TASK-141's display-only Pet Window direction, and TASK-145's Windows manual smoke PASS.
- TASK-140 fixes the composer visibility regression by making the bubble a fixed-height grid, hiding the legacy placeholder body from layout, keeping response text in the scrollable middle row, and pinning the input/Send composer as the bottom row. Input and Send stay visible in every non-collapsed state; pending only disables them.
- TASK-141 changes product direction: the visible Pet Bubble is now a display-only comic-style speech bubble with a CSS tail, compact status, and response text. The Pet form/input/send hooks are hidden dev-only hooks retained for the existing `/chat` client tests and future voice/dispatch reuse. Full App is now the primary text input surface.
- TASK-143 adds a narrow Full App -> Pet speech bridge. After Full App receives `/chat`, it sends only `{ reply, mood, source }` through `window.dragonPet.updatePetSpeech()` on fixed IPC channel `pet:speech-update`; main sanitizes/truncates and forwards to Pet Window on `pet:speech-received`; Pet preload exposes only `onSpeechUpdate(callback)`; hidden Pet Window is not automatically shown.
- TASK-144 Windows manual smoke confirmed Full App -> Pet speech mirror works, but recorded a UX note: the visible Pet bubble mixed role reply, source/status, and helper text inline.
- TASK-145 fixes the TASK-144 UX note by making the visible Pet Bubble a clean reply-only comic-style speech bubble. Source/status/mood/helper/long-reply details are hidden behind a click/expand details disclosure, Full App remains the primary text input surface, and no backend, IPC, API, or `/chat` schema change was made.
- TASK-145 Windows manual smoke passed in the visible Windows app: Christina image on top, clean reply bubble below image, floating `i`/`x` controls no longer crowd text, action buttons remain visible, medium/long replies stay constrained, details contains metadata/helper/status/long-reply hint only, and Hide/Show Pet still works.
- TASK-146 is a docs-first design task for consolidating Pet controls. It defines Chat as a Full App chat handoff or lightweight hint, Full App as the explicit focus/open action, Menu as the place for secondary controls, `x` as Hide Pet rather than app quit, and details/info as metadata-only UI that may stay as a floating `i` or move into Menu if implementation preserves discoverability and the `220 x 280` layout.

**Next recommended task:**

- Implement TASK-146 with the smallest frontend-only control consolidation needed. Keep Full App as the primary text input surface and Pet Window as the display/companion layer.
