# Development Roadmap

> dragon-pet-ai
> Status: LIVING DOCUMENT
> Last Updated: 2026-05-31
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

**Status:** LOCAL OLLAMA MVP CHECKPOINT COMPLETE - OllamaLocalProvider implemented (TASK-073), mocked contract tests pass (TASK-074), runtime smoke PASS (TASK-075), Provider Settings UI Ollama option complete (TASK-076), README local LLM instructions complete (TASK-077), Electron end-to-end local chat smoke PASS (TASK-080), source/loading/error UX stabilized (TASK-081), release readiness review PASS (TASK-082), mood to pet expression mapping (TASK-083), Christina visual asset pipeline through normalized candidates complete (TASK-084 to TASK-093), persisted settings runtime smoke PASS WITH NOTES (TASK-101), partial persist guard and local cold-start UX fix complete (TASK-102), TASK-150 local Ollama idle wake timeout/retry polish complete and Windows manual smoke PASS, TASK-151 local model thinking/reasoning output sanitization complete and Windows manual smoke PASS

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
| TASK-150 | Local Ollama Idle Wake Timeout / Retry Polish Design | DONE - PASS |
| TASK-151 | Local Model Thinking / Reasoning Output Sanitization Design | DONE - PASS |
| TASK-089 | Create Christina Focused Expression PNG | DONE |
| TASK-090 | Christina Real Expression Asset Plan | DONE |
| TASK-091 | Integrate Existing Christina Expression PNG Assets | DONE |
| TASK-092 | Christina Expression Visual QA and 512x512 Normalization Review | DONE |
| TASK-093 | Normalize Existing Christina Expression PNGs to 512x512 Face/Bust | DONE |

**Key design decisions:**
- `OllamaLocalProvider` implements the same `ProviderInterface` as `AnthropicProvider` ??no service layer changes required
- `source=llm_local` in `/chat` response ??schema unchanged
- No API key; no `explicit_cost_ack` required ??local resource warning instead
- `keep_alive=30m` by default to reduce idle-unload/cold-start churn on repeated calls
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
- TASK-150 implements the local Ollama idle/unloaded-model polish. Default `OLLAMA_KEEP_ALIVE` is now `30m`, local chat still uses the longer local timeout path, and `/api/chat` gets one safe timeout retry only when `/api/tags` confirms the local server is reachable. Non-timeout failures remain single-shot and safe. Windows manual smoke passed: empty-`ollama ps` cold-start behavior is clean, second request after wake works, the configured model appears loaded after request, and raw diagnostics do not leak to Pet Bubble.
- TASK-151 implements local model thinking/reasoning output sanitization. Local provider normal replies prefer `/api/chat` `message.content` and support `/api/generate` `response`, ignore explicit `thinking`/`message.thinking` fields, send `think: false`, defensively strip visible reasoning wrappers, keep Full App normal replies clean by default, and prevent Pet Bubble from showing thinking/reasoning/debug traces as normal speech. Windows manual smoke passed with `qwen3:8b`, including UTF-8 Chinese prompt handling.

**Next local provider reliability task:**

- TASK-150 and TASK-151 are fully closed. Define the next local provider reliability task in docs before implementation.

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

**Status:** RELEASE CHECKPOINT COMPLETE - TASK-114 design complete; TASK-115 static renderer skeleton complete; TASK-116 env-gated BrowserWindow prototype complete; TASK-117 CSS drag behavior complete; TASK-118 local-only bubble UI state complete; TASK-119 narrow Pet-to-Full mode switch complete; TASK-120 smoke checkpoint passed; TASK-121 manual Windows visual smoke passed with menu placeholder note; TASK-122 Pet Window position persistence complete; TASK-123 Pet menu/right-click menu complete; TASK-124 manual menu smoke passed with right-click drag-region note; TASK-125 right-click menu hotspot fix complete; TASK-126 menu UX regression fixed; TASK-127 explicit drag handle complete; TASK-128 Full App -> Show Pet bridge complete; TASK-129 drag regression fix complete; TASK-130 manual Windows drag/menu smoke passed; TASK-131 Pet Mode release checkpoint complete; TASK-132 Bubble Chat wiring design complete; TASK-133 static bubble state refinement complete; TASK-134 Pet Bubble `/chat` client wiring complete; TASK-135 Pet Bubble loading/error UX complete; TASK-136 Pet Bubble mood/expression integration complete; TASK-137 Pet Bubble long reply handling complete; TASK-138 Pet Bubble chat smoke checkpoint complete; TASK-140 Pet Bubble input visibility regression fixed; TASK-141 display-only speech bubble redesign complete; TASK-143 Full App reply mirror bridge complete; TASK-144 manual Windows speech mirror smoke PASS WITH NOTE; TASK-145 clean reply/details disclosure complete and Windows manual smoke PASS; TASK-146 controls consolidation complete and Windows manual smoke PASS; TASK-147 idle/presence polish complete and Windows manual smoke PASS; TASK-148 position persistence/reset polish complete and Windows manual smoke PASS; TASK-149 reply/details separation polish complete and Windows manual smoke PASS; TASK-152 details disclosure UX polish complete and Windows manual smoke PASS; TASK-153 mood expression mapping polish complete and Windows manual smoke PASS; TASK-154 chat mood selector richness polish DONE - WINDOWS MANUAL SMOKE PASS; TASK-155 Pet runtime manual smoke / launch runbook polish implemented — needs Windows manual smoke.

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
| TASK-146 | Pet Mode Menu / Controls Consolidation Design | DONE - PASS |
| TASK-147 | Pet Idle / Presence State Polish Design | DONE - PASS |
| TASK-148 | Pet Position Persistence / Reset Polish Design | DONE - PASS |
| TASK-149 | Pet Bubble Reply / Details Separation Polish Design | DONE - PASS |
| TASK-152 | Pet Bubble Details Disclosure UX Polish Design | DONE - PASS |
| TASK-153 | Pet Mood Expression Mapping Polish Design | DONE - PASS |
| TASK-154 | Chat Mood Selector Richness Polish Design | DONE - PASS |
| TASK-155 | Pet Runtime Manual Smoke / Launch Runbook Polish Design | IMPLEMENTED - NEEDS WINDOWS MANUAL SMOKE |

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
- TASK-146 is a docs-first design task for consolidating Pet controls. It defines Chat as a Full App chat handoff or lightweight hint, Full App as the explicit focus/open action, Menu as the place for secondary controls, `x` as Hide Pet rather than app quit, and details/info as metadata-only UI that can move into Menu if implementation preserves discoverability and compact layout.
- TASK-146 implementation keeps Pet display-only: Chat now hands off to Full App, Full App keeps the existing focus/open path, Menu owns Show/Hide Details, Reset Pet Position, and Hide Pet Window, floating `i` was removed, `x` hides Pet Window through existing Hide Pet behavior, and no backend, `/chat`, IPC/preload, provider, asset, external API, image, or voice change was made.
- TASK-146 Windows visual checks found the `220 x 280` and `260 x 340` windows cramped, with Christina and reply text too small at the latter size. The UX fix now uses `300 x 400`, keeps Menu outside-click/Escape behavior, keeps Open Full App/Close Menu removed from Menu, keeps the floating `i` removed, keeps the visible `speech bubble` label removed, enlarges Christina in speaking mode, and increases reply text readability.
- TASK-146 Windows manual smoke passed after the `300 x 400` readability/size UX fix: Pet Window is comfortable and still pet-like, Christina is larger and centered, reply text is readable, short/medium/long replies remain constrained appropriately, Menu/Details/Chat/Full App/Hide behaviors work, no Pet input box appears, and the main reply bubble remains clean with no source/status/helper/mood/local/llm_local or visible `speech bubble` label.
- TASK-147 implements frontend-only Pet idle/presence polish. Pet starts in `idle_default` with the static local hint `吾在。要找吾就去 Full App 說話。`, mirrored Full App replies remain visible for `90` seconds, Chat/Full App clicks show the local handoff hint `去 Full App 說，吾會聽。` for about `6` seconds, show/focus restores a still-recent reply or idle, and details metadata remains Menu-only. Windows manual smoke passed: idle does not trigger backend/LLM/Ollama/chat requests, clean mirrored replies render correctly, recent replies return to idle, handoff/menu/details/hide behavior works, and the `300 x 400` layout remains stable. No backend, `/chat`, IPC/preload, provider, external API, image, voice, proactive LLM, Full App renderer, or Pet input change was made.
- TASK-148 implements Pet Window position persistence/reset polish in the Electron shell. It reuses `userData/pet-window-state.json`, keeps the Pet Window fixed at `300 x 400`, requires the full window to fit inside a current display work area before restoring saved bounds, falls back to the primary-display lower-right safe default when invalid, validates bounds on Show Pet and Electron display changes, and persists Reset Pet Position immediately. Windows manual smoke passed: move/restart/reset/hide/show/off-screen fallback behavior works, TASK-146 controls remain intact, TASK-147 idle/recent/handoff behavior remains intact, and no backend, `/chat`, IPC/preload, provider, external API, image, voice, proactive LLM, Full App renderer, Pet input, speech state, or Pet size change was made.
- TASK-149 implements Pet Bubble reply/details separation polish. Pet renderer visible speech now explicitly derives from `payload.reply` only, smoke coverage confirms diagnostic/details/helper/status/provider-like fields do not render in the main bubble, and main/preload speech payload sanitizers remain limited to `reply / mood / source`. Windows manual smoke passed: Pet Bubble shows only clean character-facing reply text, diagnostics are not rendered as normal bubble text, and long replies/error states keep the main bubble clean. Full App remains the richer diagnostic surface. No backend, `/chat`, IPC/preload API, provider, external API, image, voice, proactive LLM, Pet input, mini Full App, Full App renderer, TASK-148 position behavior, or Pet size change was made.
- TASK-152 implements small Pet Bubble details disclosure UX polish. Details remain collapsed by default and Menu/details based, normal Pet Bubble speech remains character-facing, payloads with no meaningful metadata hide/disable the disclosure, safe short source/helper/status/debug-style metadata remains available only after explicit disclosure, and raw JSON-like text, stack traces, local Ollama endpoint/port text, API-key wording, and thinking/reasoning markers are filtered out of details. Windows manual smoke passed: normal replies stayed clean, no empty/noisy disclosure appeared without metadata, details opened/closed from Menu when meaningful metadata existed, long/error states remained clean and constrained, and TASK-149/TASK-150/TASK-151 behavior did not regress. No backend, `/chat`, IPC/preload API, provider settings, external API, image, voice, Pet input, Full App layout, or broad diagnostics architecture change was made.
- TASK-153 implements small frontend-only Pet mood expression mapping polish. It centralizes mood aliases in the Pet renderer, maps only to existing Christina PNG expression assets, normalizes string moods, safely falls back unknown/null/empty/inherited-key-like values to neutral/default, and restores neutral if a non-neutral expression asset fails to load. Investigation found current mock/local `/chat` prompt wording naturally returns only `neutral`, `happy`, or `focused`, so a deterministic Pet Window DevTools smoke hook `window.__dragonPetMoodExpressionSmoke.apply(mood)` verifies focused/proud/worried/neutral mapping without relying on LLM mood variability. Windows manual smoke passed: the Pet Window DevTools hook was available from `apps/desktop/src/pet/pet.html`; `neutral`, `focused`, `proud`, and `worried` returned matching expressions and `christina_<mood>.png` files; unknown/missing mood fell back to neutral; avatar `src` changed for supported moods; unknown mood did not crash; Pet Bubble visible text stayed clean; mood/source/debug/details/thinking were not exposed as normal speech; TASK-148, TASK-149, TASK-150, TASK-151, and TASK-152 behavior did not regress. Manual smoke verified expression/src/file behavior and does not claim `data-expression` manual verification. Clean Pet Bubble text and TASK-152 details disclosure remain separate from mood mapping. No backend, `/chat`, IPC/preload API, provider settings, external API, image asset, voice, animation, Pet input, Full App layout, Pet Window size, or position behavior change was made.
- TASK-154 implements a narrow backend mood selector richness polish. Mock/local `/chat` mood selection now deterministically covers `neutral`, `focused`, `happy`, `proud`, `annoyed`, `worried`, and `sleepy` while preserving the stable `reply / mood / source` schema and clean Pet Bubble behavior. The implementation did not add images, animation, voice, Pet Window layout changes, a broad emotion system, IPC/preload changes, or provider architecture rewrites.

- TASK-155 DONE - PASS (after TASK-156 fix): Windows manual smoke initially found two bugs — Pet Bubble showing raw JSON from qwen3 JSON-formatted output, and expression switching not visually verifiable. Both fixed in TASK-156. Re-smoke passed: backend health PASS, Pet Window PASS, Pet Bubble shows clean reply-only text, all 7 expression moods verified via `dataset.expression` and avatar src, missing mood falls back to neutral.
- TASK-156 DONE - PASS: `_try_unwrap_json_reply()` in `ollama_provider.py` unwraps JSON-formatted qwen3 model output; `data-expression` propagated to `#pet-mode-root` for DevTools verification; runbook section 7 extended with three verification methods. 619 pytest pass, all 3 smoke scripts pass. Windows manual smoke: Pet Bubble clean, all expression moods PASS, `dataset.expression` correct, avatar src changes per mood.

- TASK-157 DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS: Pet Bubble Thinking / Typing State. `renderer.js` calls `updatePetThinkingState()` (sends `{ reply: PET_THINKING_REPLY_TEXT, mood: "focused", source: "pet_thinking" }` via existing narrow `updatePetSpeech` IPC bridge) immediately when `sendMessage()` starts the `/chat` fetch. `pet-renderer.js` routes `source === "pet_thinking"` to the `"thinking"` bubble state and skips `rememberRecentPetReply` so the thinking state is never restored on window show/focus. On error, `updatePetSpeechFromChatResponse` replaces the thinking bubble with a clean `llm_local_error` state. Smoke counts: pet-renderer-smoke.js 50 PASS (4 new), renderer-chat-smoke.js PASS (3 new + 1 updated), pet-window-smoke.js 15 PASS. Windows manual smoke PASS: thinking bubble shows immediately on send, clean character text only, focused expression during thinking, thinking replaced by final reply on success and clean error on failure, thinking not restored after hide/show, TASK-149–TASK-154 no regression.

**Screen Context v0.4 COMPLETE** — see `docs/SCREEN_CONTEXT_V04_RELEASE_SUMMARY.md`

**Next planned task:** TASK-203 — (Suggested: message timestamps visible on hover tooltip, or Pet Window unread dot badge)

- TASK-202 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-05-31): Smooth Auto-scroll / New Message Jump Badge. New `#chat-area-wrap` (`position: relative`) wraps `<main id="chat-area">` to anchor the absolutely-positioned jump button. `#chat-area` retains all scroll/padding properties but yields flex-sizing to the wrapper. `#chat-new-message-btn` (`.chat-new-message-btn`, `position: absolute; bottom: 10px; right: 14px; z-index: 10`) is hidden by default. `maybeScrollChatToBottom()` updated: near-bottom → `scrollChatToBottom()` (unchanged); not near-bottom → `showNewMessageBtn()` unless search is active. chatArea scroll listener: hides button when user reaches bottom. Button click: `scrollChatToBottom()` + `hideNewMessageBtn()`. `clearChatHistory()` hides button on clear. `FakeElement.hidden = false` init; FakeDocument special-cases `chat-new-message-btn` (`hidden = true`); +12 TASK-202 tests. Suites: 233/55/renderer-chat PASS. git diff --check CLEAN. Windows visual smoke PASS (7 scenarios, 2026-05-31): near-bottom auto-scroll ✓, scrolled-up shows button ✓, click scrolls+dismisses ✓, manual scroll dismisses ✓, search active no button ✓, clear chat dismisses ✓, TASK-198/199/200/201/copy/Pet/Voice/STT/TTS regression PASS ✓.

- TASK-201 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-05-31): Chat Search Highlight / Result Navigation. Upgraded TASK-198 search with: (1) `body.className="msg-body"` in `appendMessage` for body lookup; (2) `escapeHtml()` + `highlightText()` — wraps case-insensitive matches in `<span class="search-highlight">` after HTML-escaping raw text; (3) `navigateToSearchResult(delta)` — advances/wraps `searchActiveIndex`, sets `search-active` class, calls `scrollIntoView`, updates count chip to "找到 N 筆，第 M 筆"; (4) Enter / Shift+Enter in chatSearchInput keydown handler → next/prev result; (5) `filterChatMessages` rewritten to populate `searchResults`, apply highlight on match, restore `escapeHtml(rawText)` on non-match/clear. CSS: `.search-highlight` (amber background); `.message.search-active` (accent outline). `dataset.msgText` and copy paths (raw text closure / `el.dataset.msgText`) untouched. **Root cause fix:** initial smoke FAIL because `child.children.find()` crashes in real DOM — `HTMLCollection` has no `.find()`; fix: `Array.from(child.children || []).find(...)`. +3 defensive tests (ArrayFrom static, MsgBodyAbsent, NavigateNoop). FakeElement gains `scrollIntoView()`; +13 TASK-201 tests total. Suites: 233/55/renderer-chat PASS. git diff --check CLEAN. Windows visual smoke PASS (7 scenarios, 2026-05-31): filter ✓, amber highlight ✓, Enter next result + outline + count chip ✓, Shift+Enter prev result ✓, clear removes highlight+outline ✓, copy/export plain text only ✓, TASK-198/199/200/Pet/Voice/STT/TTS regression PASS ✓.

- TASK-200 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-05-31): Full App Unread / Attention Badge for Pet Replies. `document.title` badge updates to `(N) Dragon Pet AI` when `appendMessage("pet", ...)` is called while `document.hidden === true` and `noHistory` is false. `markUnread()` increments `unreadChatCount` and updates title; `clearUnread()` resets count + restores `UNREAD_BASE_TITLE`. Cleared on `visibilitychange` (document becomes visible) and `window.focus`. Excluded: startup greeting (`noHistory:true`), history restore (`noHistory:true`), status/user/error messages. Scope: `document.title` only — no new DOM, no CSS, no OS notification, no tray badge, no IPC, no backend. FakeDocument gains `hidden=false` + `title="Dragon Pet AI"` stubs; +10 TASK-200 renderer-chat tests. Suites: 233/55/renderer-chat PASS. git diff --check CLEAN. Windows visual smoke PASS (6 scenarios, 2026-05-31): Full App focused — title stays "Dragon Pet AI", no badge ✓; minimized + Pet reply + cut back — title shows "(1) Dragon Pet AI" then restores on focus ✓; Full App background AI reply badges title ✓; multiple hidden replies accumulate count ✓; startup/history restore no badge ✓; chat search / Ctrl+F / copy-export / Pet Window / Voice / STT / TTS regression PASS ✓.

- TASK-199 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-05-31): Chat Search Keyboard Shortcuts. `Ctrl+F` / `Cmd+F` document-level `keydown` listener: `preventDefault()` blocks Electron native find dialog; focuses `#chat-search-input`; calls `.select()` so existing query is pre-selected for immediate replacement. `Esc` listener scoped to `#chat-search-input`: non-empty → clears value + calls `filterChatMessages("")` + empties count; empty → blurs field. No HTML/CSS change. No backend, IPC, history write, Pet Window impact, or keyword persistence. FakeDocument gains `dispatchEvent()`; FakeElement gains `blur()` + `select()`; `fireDocumentKeydown()` test helper added; +9 TASK-199 tests. Suites: 233/55/renderer-chat PASS. git diff --check CLEAN. Windows visual smoke PASS (7 scenarios, 2026-05-31): Ctrl+F focuses search ✓; Ctrl+F with existing text selects and allows overwrite ✓; Esc clears search and restores all messages ✓; Esc on empty input blurs field ✓; Ctrl+F from textarea does not send chat ✓; Esc in textarea does not clear input or send chat ✓; Pet Bubble / Voice / STT / TTS / history restore / copy-export / search-filter regression PASS ✓.

- TASK-198 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-05-31): Chat Message Search / Filter UX. Always-visible search bar between `#character-status` and `#chat-area`. Pure DOM visibility filter (`filterChatMessages(query)`) — no backend, no IPC, no data mutation, no history write. Matching user/pet messages stay visible; non-matching hidden via `style.display = "none"`; status/error separators hidden during search. Result count: "找到 N 筆" / "沒有找到符合的對話" / empty on no query. Clear button (✕) restores all messages and clears count. `clearChatHistory()` resets search state. `copyAllChat()` uses `querySelectorAll` which ignores `display:none` — copies full conversation regardless of filter state (intentional). Search corpus: `dataset.msgText` set on every bubble by TASK-196 `appendMessage()`. FakeElement-compatible: uses `chatArea.children` + `className.includes()` instead of `querySelectorAll`. HTML: `#chat-search-bar` div with `#chat-search-input`, `#chat-search-count`, `#chat-search-clear-btn` in `index.html`. CSS: `#chat-search-bar`, `.chat-search-input`, `.chat-search-count`, `.chat-search-clear-btn` in `styles.css`. Smoke: `searchChat()` + `clearSearch()` test helpers + 11 TASK-198 tests. Suites: 233/55/renderer-chat PASS. git diff --check CLEAN. Windows visual smoke PASS (7 scenarios, 2026-05-31): search bar visible on startup ✓; keyword match shows "找到 N 筆" with correct filtering ✓; no-match shows "沒有找到符合的對話" ✓; clear (✕) restores all messages ✓; copy-all during search copies full conversation ✓; clear-chat resets search state with no stale filter ✓; Pet Bubble / Voice / STT / TTS / history restore / Provider Settings / 記憶管理 / 診斷紀錄 regression PASS ✓.

- TASK-197 DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-31): Ollama Wake-up / First Chat Reliability. Four targeted fixes: (1) Startup `/health` fetch now has 8-second `AbortController` timeout — no more indefinite hang on slow/offline backend. (2) `sourceStatusMessage()` fully Chinese — all 8 source branches translated. (3) `sendMessage()` loading text Chinese — Ollama path: "本地 AI 喚醒中，第一次回覆可能需要較久..."; non-Ollama: "等待後端回覆中...". (4) Non-blocking `checkLocalProviderLiveness()` runs after startup settings load: fetches new `GET /provider/health` backend endpoint, updates `#provider-status-summary` chip only (no chat, no history, no Pet/TTS). Backend: `check_ollama_server_liveness()` in service layer (GET `/api/tags` reachability check, no model load); `/provider/health` route returns `{provider, ollama_reachable, status}`. Liveness chip: reachable → "Ollama 本地 AI 已就緒。"; reachable + fallback → preserves fallback warning; unreachable → "Ollama 尚未回應。第一次聊天可能需要較久，請確認 Ollama 已啟動。"; error → restores previous text. Smoke tests: `AbortController` added to renderer sandbox; `/provider/health` handler added to fetch stub; `ollamaReachable` option added; +9 TASK-197 renderer-chat tests; English test patterns updated to Chinese. Suites: 233/55/renderer-chat PASS. Backend pytest: 54 PASS. git diff --check CLEAN.

- TASK-196 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-05-31): Chat Message Copy / Export. Per-bubble "複製" button (hover-only, opacity 0 → 1) on every user/pet message; "複製對話" ghost header button copies full conversation as plain text. Two rounds of fix before smoke PASS: (1) `navigator.clipboard` failed — Electron `file://` not a secure context; (2) preload-direct `clipboard.writeText` also failed — renderer-process clipboard restricted; (3) final fix: IPC chain renderer.js → `window.dragonPet.writeClipboardText` → preload `ipcRenderer.invoke("clipboard:write-text", text)` → main.js `ipcMain.handle` → `clipboard.writeText(safe)`. `writeToClipboard(text)` helper wraps bridge in `Promise.resolve` to handle async IPC + sync test mocks. `copyAllChat()` collects `.message.user` and `.message.pet` only, formats "你/克莉絲蒂娜 HH:mm:\ntext\n". No backend/schema/history change. +9 renderer-chat-smoke tests, +2 pet-window-smoke tests. Suites: 233/55/renderer-chat PASS. git diff --check CLEAN. Windows visual smoke: all 8 scenarios PASS (2026-05-31).

- TASK-195 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-05-31): Chat History UX Polish / Source & Timestamp Display + Full App Layout Polish. Phase A (complete, smoke PASS): `HH:mm` timestamp + "Pet"/"Voice" source labels on chat bubbles; "已還原 N 筆對話紀錄。" restore separator; `inputMethod` through mirror pipeline. Phase B: Full App layout polish — header two-row layout; Show Pet primary (accent fill); 清除對話記錄 ghost (far right); screen capture buttons grouped; dev tag unobtrusive; mood indicator calm blue; pet display gradient + avatar drop-shadow; hint text as speech-bubble card; empty chat placeholder; responsive at 434px. Phase B follow-up 2: Electron native menu bar hidden (`Menu.setApplicationMenu(null)`); provider chip human-readable (`friendlyProviderName()`); status pills non-interactive; `#character-status` below avatar; startup greeting Chinese character voice. Phase B follow-up 3: Memory toggle → Chinese; `MEMORY_INJECTION_ENABLED` → tooltip; SYSTEM status → separator line; status clears after history restore; input+Send `nowrap`. Phase B follow-up 4: Memory section `<details>/<summary>` collapsed "記憶管理"; all form labels → Chinese (values unchanged). Phase B follow-up 5: Audit section `<details>/<summary>` collapsed "診斷紀錄"; all labels → Chinese; renderer status/card strings → Chinese; user bubble `margin-right: 4px`. Phase B follow-up 6: Provider Settings `<details>/<summary>` collapsed "AI 設定"; all visible labels → Chinese; `calcProviderStatusSummary` strings → Chinese; TASK-189/190 test patterns updated. Tests: cumulative renderer-chat/pet-window/pet-renderer PASS throughout. Final suites: 233/53/renderer-chat PASS. git diff --check CLEAN. Phase A Windows manual smoke PASS (7 scenarios). Phase B + follow-up 2–6 Windows visual smoke PASS (8 scenarios, 2026-05-31).

- TASK-194 DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-31): Full App Chat History / Session Persistence. Persists user/pet messages to `userData/chat-history.json` (max 200 entries, 2000 chars/entry). Restores history on startup before greeting — no auto-/chat, no TTS. New narrow IPC: `chat-history:append/load/clear` via contextBridge. `appendMessage()` accepts `{noHistory, source}` options; startup greeting uses `{noHistory:true}`; Pet mirror entries use `source:"pet_text"`; Full App entries use `source:"full_app"`. `clearChatHistory()` clears DOM + file. Clear button `清除對話記錄` added to header. Never saves: audio, base64, API key, screenshot, OCR image, diagnostics. Tests: +6 renderer-chat-smoke, +2 pet-window-smoke. Suites: 232/51 PASS. git diff --check CLEAN. Windows manual smoke PASS (6 scenarios: Full App persistence, Pet direct input persistence, Pet voice/STT persistence, restore safety — no auto-/chat/TTS, clear chat, safety/privacy).

- TASK-193 DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-31): Mirror Pet Text / Voice Messages into Full App Chat. New narrow IPC channel `pet:chat-mirror` (Pet Window → main → Full App). Pet direct text input and Pet voice/STT transcript + AI reply now appear in Full App Chat as a unified conversation record. Changes: `mirrorPetChatToFullApp()` helper in pet-renderer.js called from `handlePetVoiceChatSend` and `handlePetDirectSend` on success only; `mirrorChatToFullApp` exposed in pet-preload.js (text-only payload, max lengths, no audio blob); `ipcMain.handle("pet:chat-mirror")` in main.js sanitizes and forwards to fullAppWindow if available (no-op if window closed); `onChatMirrorFromPet` exposed in renderer/preload.js; `setupPetChatMirrorListener()` in renderer.js appends user message + pet reply + setMood. Safety: payload is text-only; STT failure/empty never mirrors; empty payload or missing Full App window returns ok:false; contextIsolation maintained; no nodeIntegration change; no chat API schema change; no backend change. Tests: +6 pet-renderer-smoke, +4 pet-window-smoke, +5 renderer-chat-smoke. Suites: 232/49 PASS. git diff --check CLEAN. Windows manual smoke PENDING.

- TASK-192 IMPLEMENTED - NEEDS WINDOWS MANUAL SMOKE (2026-05-31): Voice / TTS Manual Smoke Closeout. Docs-only task. Expanded TASK-191 Voice/TTS regression baseline into an executable 14-item manual smoke checklist in `docs/VOICE_TTS_REGRESSION_NOTES.md`. Each item has preconditions, step-by-step checks, and explicit pass criteria. Areas: mic button visibility (3 scales), recording indicator + CSS mutual exclusion, transcribing guard (`isTranscribingActive()`), STT→/chat handoff + transcript cleared, thinking→reply bubble, TTS ON/OFF audible, Quiet Mode (idle suppressed / recording unaffected / TTS unchanged), voice settings panel (voice selector / rate / pitch / volume / localStorage / reset), recording↔text input bidirectional mutual exclusion, transcribing blocks recording, error message cleanliness (5 sub-scenarios: no mic / denied / STT unavailable / backend offline / empty audio — all clean Chinese), direct text input regression, Full App→Pet mirror. pet-renderer-smoke 226 PASS, pet-window-smoke 45 PASS, renderer-chat-smoke PASS, git diff --check CLEAN. Windows manual smoke PENDING.

- TASK-191 DONE (2026-05-31): Voice / TTS regression baseline. Code survey of all Pet Window voice/STT/TTS files. Confirmed: no regressions from TASK-188–190. Automated baseline: 80 voice tests in pet-renderer-smoke (PASS), 7 STT/voice tests in pet-window-smoke (PASS), 14 backend STT tests (PASS). Documented: recording/transcribing/speaking state machine, 12-entry mutual exclusion matrix, 9-entry error taxonomy (all clean Chinese, no raw exceptions), TTS settings reference (voice/rate/pitch/volume, localStorage persistence). Manual smoke checklist (8 scenarios). Known gaps: getUserMedia, speechSynthesis, faster-whisper quality, 30-sec timeout, Windows CT — all manual-only. No bugs found. Docs-only task: created `docs/VOICE_TTS_REGRESSION_NOTES.md`. 667 backend PASS. git diff --check CLEAN.

- TASK-190 DONE (2026-05-31): Provider Settings UI manual smoke closeout. Static inspection of all TASK-189 changes. Bug found: `calcProviderStatusSummary` misclassified `key_status = "invalid"/"test_failed"` as "not configured" — fixed (now shows "API key invalid or connection test failed." in error state). Manual smoke checklist written (14 scenarios covering mock, Ollama active/fallback/error, cloud provider, Test Connection, API key regression). Pre-existing issue noted: `lastChatSource = "not_checked"` (truthy) prevents "before first chat" branch in `syncChatRuntimeProviderStatus` from running. renderer-chat-smoke PASS (2 new edge-case tests), pet-renderer 226 PASS, pet-window 45 PASS, git diff --check CLEAN.

- TASK-189 DONE (2026-05-30): Provider Settings UI Polish Pass. Full App Provider Settings UX review and text cleanup. Changes: (1) `save-provider-settings-btn` "Save Non-secret Settings" → "Save Provider Settings" + note about API key stored separately; (2) added `#provider-status-summary` plain-English bar showing current AI state (Mock / Ollama active / Ollama with fallback / cloud AI / API key not configured) with colour coding; (3) `sourceStatusMessage()` messages stripped of `source=xxx -` technical prefix — now user-readable ("Ollama response received.", "Local AI failed — model may still be loading.", "Using mock fallback — …", etc.); (4) checkbox labels: "Real provider enabled" → "Use real AI", "LLM chat enabled" → "Enable AI chat", "Fallback to mock" → "Fall back to mock if AI fails"; (5) status grid labels: "Resolved provider" → "Active provider", "Real provider enabled" → "Real AI", "LLM chat enabled" → "AI chat", "Key status" → "API key", "Fallback to mock" → "Mock fallback"; (6) `chat-source-status` initial HTML text changed from "source: not_checked" to "—"; (7) `updateKeyUIState` tooltips replace raw `real_provider_enabled` field name with "Use real AI". Runtime: no backend, no schema, no provider, no Screen Context change. 5 new renderer-chat-smoke tests + 3 updated assertions; renderer-chat-smoke PASS, pet-renderer 226 PASS, pet-window 45 PASS, git diff --check CLEAN.

- TASK-188 DONE (2026-05-30): Pet / Full App UX polish pass. Reviewed Full App header buttons, OCR flow, Pet Window bubble/menu/idle text, Provider Settings, Pet↔Full App navigation. Two fixes: (1) `clearScreenshot()` bug — after window capture, `capture-window-status` was not cleared on "清除截圖", leaving stale "視窗截圖完成。尚未儲存" message; added `setCaptureWindowStatus("", false)` to fix; added smoke test `test188ClearWindowStatusAfterClear`; (2) `version-tag` "v0.1 skeleton" → "dev" (stale since TASK-003). Created `docs/DESKTOP_UX_POLISH_NOTES.md` with full findings (8 issues: 2 fixed, 6 noted/deferred). Runtime: only minimal bug fix (no schema/API/provider/Screen Context change). renderer-chat-smoke PASS, pet-renderer 226 PASS, pet-window 45 PASS.

- TASK-187 DONE (2026-05-30): Full project test baseline / CI readiness check. All 5 automated suites verified clean: `python -m pytest tests/ -q` → `667 passed, 1 warning`; `test_ocr_routes.py` → `34 passed`; `renderer-chat-smoke` PASS; `pet-renderer-smoke` 226 checks; `pet-window-smoke` 45 checks; `git diff --check` CLEAN. Updated `docs/DESKTOP_SMOKE_RUNBOOK.md`: promoted full backend suite (667) to primary gate in Quick Reference, added Suite 1 (full) + Suite 1a (OCR subset), updated When-to-Run and One-Shot block, updated baseline table, added `.pytest-tmp/` note, updated file map. CI readiness: backend suite is hermetic (no Ollama needed); desktop smokes need only Node.js; `--basetemp` resolves Windows CI tmp-path issues. No runtime files modified.

- TASK-186 DONE (2026-05-30): Provider settings persistence tests cleanup. Root cause: `tmp_path` fixture failed with `PermissionError [WinError 5]` on `C:\Users\雪狼丸\AppData\Local\Temp\pytest-of-RickHSIAO` — system temp ACL issue on this machine. Fix: added `addopts = --basetemp=.pytest-tmp` to `backend/pytest.ini`; added `.pytest-tmp/` and `.pytest-tmp*/` to `.gitignore`. Result: `23 passed, 1 warning` (persistence file alone); `667 passed, 1 warning` (full suite). No runtime files modified, no test logic changed.

- TASK-185 DONE (2026-05-30): Provider / Ollama stability pass. Runtime: no bugs found — `keep_alive="30m"`, 1-retry on timeout, 90 s chat timeout, separate 10 s test-connection timeout, all error categories safe. Docs gap: `LOCAL_DEV_RUNBOOK.md` env var table was missing `OLLAMA_BASE_URL`, `OLLAMA_KEEP_ALIVE`, and `LLM_LOCAL_TEST_TIMEOUT_SECONDS`; added all three with description and defaults. Also added `source=llm_local_error` diagnosis section (Ollama not running, cold-start, fallback_to_mock masking errors, keep_alive expiry). Test results: 644 backend PASS, renderer-chat-smoke PASS.

- TASK-184 DONE - DOCS-ONLY (2026-05-30): Smoke command runbook / one-command verification docs. Created `docs/DESKTOP_SMOKE_RUNBOOK.md`: quick-reference block (all four suites + git hygiene), per-suite details (command, count, runtime, coverage, when to run), change-scoped guidance (renderer → renderer-chat-smoke; main.js/IPC → pet-window-smoke; OCR → pytest; etc.), one-shot full regression PowerShell block with Push/Pop-Location, expected healthy baseline table, smoke suite file map, and common failures & fixes. No runtime files modified.

- TASK-183 DONE (2026-05-30): General app regression / startup smoke cleanup. Found and fixed a pre-existing test regression in `pet-window-smoke.js` caused by Screen Context v0.4 picker IPC: `testPetOpenFullAppIpcIsFixedAndNarrow` asserted `assertNotIncludes(main, "ipcMain.on(")` which was correct before v0.4 but TASK-174/175/176 legitimately added `ipcMain.on()` for picker event channels (all scoped, all paired with `ipcMain.removeListener()`). Replaced overly-broad assertion with two precise guards: (1) `assertNotIncludes(main, "ipcMain.on(PET_")` — pet IPC still uses handle-only; (2) `assertIncludes(main, "ipcMain.removeListener(")` — cleanup pattern exists. All four suites now pass: renderer-chat-smoke PASS, pet-renderer-smoke 226 PASS, pet-window-smoke 45 PASS, OCR pytest 34 PASS.

- TASK-182 DONE - DOCS-ONLY (2026-05-30): Screen Context stability cleanup / post-release regression pass. Automated test re-verification: 34 OCR pytest PASS, renderer-chat-smoke PASS, git diff --check CLEAN. Docs inconsistencies found and fixed: (1) `SCREEN_CONTEXT_V04_RELEASE_SUMMARY.md` header/TASK-179 smoke row/sign-off omitted TASK-181; (2) `SCREEN_CONTEXT_RELEASE_SMOKE_CHECKLIST.md` Purpose scope outdated (TASK-177→TASK-179), D2 missing hint-hide check, new C0 item for OCR ask hint, Related Docs updated to TASK-181; (3) `TASKS.md` TASK-181 §2 said "9" safety boundaries (table has 10). No runtime files modified.

- TASK-181 DONE - DOCS-ONLY (2026-05-30): Screen Context v0.4 Final Checkpoint / Release Summary. All 9 runtime tasks (TASK-171A through TASK-179) and 4 docs tasks (TASK-173/178/180/181) recorded. Created `docs/SCREEN_CONTEXT_V04_RELEASE_SUMMARY.md` (7 sections: completed capabilities, safety boundaries, known limitations, test status, file inventory, v0.5 recommendations, sign-off). All safety boundaries confirmed: no auto-capture, no background monitoring, no auto-OCR, no auto-/chat, no image to AI, no disk write, OCR text-only default, no Pet autonomous commentary, contextIsolation/nodeIntegration enforced. Test status: 34 OCR pytest PASS, renderer-chat-smoke PASS, task171a-capture-smoke exit 0, Windows manual smoke PASS all tasks. No runtime files modified.

- TASK-179 DONE (2026-05-30): Optional Pet UI hint after OCR summary exists. Added `#ocr-ask-hint` div to `index.html` (starts hidden), `.ocr-ask-hint` CSS class (11px, `var(--text-muted)`), `ocrAskHintEl` DOM ref in `renderer.js`, and `ocrAskHintEl.hidden = !hasSummary` toggle wired into `updateAskButtonState()`. Hint appears only after successful OCR produces non-empty text; hidden on no-text, OCR failure, and after clear. Hint is display-only — no auto-chat, no auto-OCR, no auto-capture, no Pet commentary, no image sent. 1 static + 5 dynamic TASK-179 smoke tests added; `renderer-chat-smoke.js` PASS.

- TASK-178 DONE - DOCS-ONLY (2026-05-30): Screen Context v0.4 release smoke checklist. 43-item checklist at `docs/SCREEN_CONTEXT_RELEASE_SMOKE_CHECKLIST.md` covering: Pre-flight (P1–P6, backend + GET /ocr/status), Section A capture modes (A1–A3, TASK-174/175/176), Section B OCR analysis (B1–B9, TASK-172A/177 including chi_tra/eng fallback), Section C chat handoff (C1–C7, TASK-172B, OCR text only), Section D clear screenshot (D1–D4), Section E privacy & safety prohibitions (E1–E8: no auto-capture, no background monitoring, no auto-OCR, no auto-/chat, no image to AI, no disk write, no cloud OCR, no Pet autonomous commentary), Section F full-app regression (F1–F8). No runtime files modified.

- TASK-177 DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-30): OCR language/data installer checks for `chi_tra` (v0.4+ screen context OCR diagnostics). Replaced `_ocr_lang_cache` + `_get_ocr_lang()` with `_probe_ocr_status()` + `get_ocr_status()` returning `{ tesseract_available, chi_tra_available, eng_available, selected_lang, fallback_reason }`. Added `GET /ocr/status` diagnostic endpoint. Four fallback reason codes: `pytesseract-not-installed`, `tesseract-binary-not-found`, `chi_tra-language-data-missing`, `no-language-data`. `lang is None` guard in `extract_text_from_dataurl()` — no crash when language data absent. 7 new backend tests (34 OCR tests total PASS). `test177StaticChecks` desktop smoke PASS. Windows manual smoke PASS: `GET /ocr/status` → `{ tesseract_available: true, chi_tra_available: true, eng_available: true, selected_lang: "eng+chi_tra", fallback_reason: null }`, no traceback; display+region capture + OCR PASS; window capture + OCR PASS; "問克莉絲蒂娜這個畫面" sends only OCR text; "清除截圖" and Full App regression all PASS.

- TASK-180 BACKLOG - DOCS-ONLY NOTE (2026-05-30): Optional Visual Model / Multimodal Screenshot Understanding (v0.5+ future improvement). Default remains OCR text-only; visual analysis is a separate opt-in layer. All 10 safety constraints recorded: not in TASK-176 scope, not auto-enabled, no background monitoring, no auto-send image to AI, user-confirmed every time, OCR-only default preserved, local vision model (e.g. LLaVA/Ollama) preferred, cloud vision requires explicit opt-in plus cost/privacy warning, sensitive data warning required on every analysis, visual and OCR paths remain independently testable. No runtime changes. See TASK-180 in docs/TASKS.md.

- TASK-176 DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-30): Window Picker Capture (v0.4+ screen context). Active-window auto-detection rejected (clicking button changes OS focus to this app; Electron has no safe active-window API). Instead: `desktopCapturer.getSources({ types: ["window"] })` + explicit window picker. Main process pushes `[{ index, name }]` to picker window via `window-picker:list` IPC (source IDs never leave main process). User selects by index; `screen:capture-window` handler returns single-window dataUrl. New button "擷取視窗" feeds same analyze/OCR/chat pipeline. Error codes: `window-pick-cancelled`, `window-picker-failed`, `no-window-source`, `window-capture-failed`. `renderer-chat-smoke.js` PASS; 7 new TASK-176 smoke tests PASS. Windows manual smoke PASS: picker opens dark opaque window with name list; Notepad capture → only `WINDOW_PICKER_TASK176_TEST` in OCR; browser capture → only `BROWSER_WINDOW_TASK176_TEST` in OCR; capture isolation confirmed; Esc → "已取消選取視窗。"; "擷取螢幕" display+region flow unaffected; "分析這張", "問克莉絲蒂娜這個畫面", "清除截圖", Full App chat/Pet/voice/TTS: no regression.

- TASK-175 DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-30): Region Drag-to-Select Screenshot Capture (v0.4+ screen context capture improvement). Extends TASK-174: after the display picker, a canvas overlay opens on the selected display; user drags a rectangle; only the selected region is captured. New files: `src/picker/region-picker.html` (canvas-only overlay) and `src/picker/region-picker-preload.js` (drag logic, sends `screen-region:selected`/`screen-region:cancel`). Main process converts CSS logical px → physical px via `display.scaleFactor`, captures full display at physical resolution, crops with `thumbnail.crop()`. Error codes: `region-pick-cancelled`, `region-too-small` (< 16 logical px), `region-crop-failed` — all mapped to clean zh-TW messages. `renderer-chat-smoke.js` PASS; 4 new TASK-175 smoke tests PASS. Windows manual smoke PASS: display picker on both monitors; primary-only region capture confirmed (`PRIMARY_REGION_TASK175_TEST`); secondary-only region capture confirmed (`SECONDARY_REGION_TASK175_TEST`); too-small region → clean error message; Esc region cancel → "已取消選取區域。"; Esc display cancel → "已取消擷取螢幕。"; "分析這張", "問克莉絲蒂娜這個畫面", "清除截圖", and full app regression all PASS.

- TASK-174 DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-30): Click-to-Select Display Capture (v0.4+ screen context capture improvement). Cursor-based approach (TASK-174 v1) rejected after UX review: clicking "擷取螢幕" moves cursor to app-window monitor, defeating mouse-position detection. Redesigned as click-to-select picker: main process opens one semi-transparent `BrowserWindow` per display; user clicks desired monitor; main process destroys all pickers and captures the selected display. New files: `src/picker/picker.html` (CSS-only overlay) and `src/picker/picker-preload.js` (sends `screen-picker:selected`/`screen-picker:cancel` IPC). `screen:capture-once` handler replaced with `showDisplayPicker` + `desktopCapturer` capture by selected display ID. `contextIsolation: true`, `nodeIntegration: false` for all windows. Normal renderer never receives raw display IDs or source list. Error codes: `screen-pick-cancelled`, `selected-display-ambiguous`, `screen-picker-failed` — all mapped to clean zh-TW messages. `renderer-chat-smoke.js` PASS; 4 new TASK-174 smoke tests PASS. Windows manual smoke PASS: picker overlays appeared on both monitors; primary-only capture confirmed (`PRIMARY_MONITOR_TASK174_TEST`); secondary-only capture confirmed (`SECONDARY_MONITOR_TASK174_TEST`); Esc cancel → clean "已取消擷取螢幕。" message; "分析這張", "問克莉絲蒂娜這個畫面", "清除截圖", and full app regression all PASS.

- TASK-173 DONE - DOCS-ONLY CHECKPOINT (2026-05-30): v0.4 Screen Context Checkpoint / Release Summary. Full milestone documented: (1) completed capabilities — explicit capture, primary-display-safe, in-memory only, user-confirmed OCR via POST /ocr/extract, "螢幕摘要" display, user-confirmed /chat handoff with bounded summary text only; (2) privacy/safety boundaries — no auto-capture, no background monitoring, no screenshot/image persistence, no cloud OCR/vision, no dataUrl to /chat, no Pet autonomous commentary, no nodeIntegration change, explicit confirmation before OCR and before chat; (3) known limitations — OCR UI noise, Tesseract language data dependency, primary display only, no region/window/visual-reasoning; (4) manual smoke summary for TASK-171A through TASK-172B all PASS; (5) recommended next tasks TASK-174–TASK-180; (6) TASK-174 (current mouse display capture) recommended first. No runtime files modified.

- TASK-172B DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-30): User-Confirmed Screenshot Summary to Chat Handoff (v0.4 screen context slice 2B). "問克莉絲蒂娜這個畫面" button in Full App header; hidden until OCR summary exists. Privacy confirmation required before every `/chat` call. Only bounded OCR summary text sent to `/chat` via existing `sendMessage()`; no dataUrl, no image bytes, no cloud vision. Cancel prevents `/chat`. Clear hides button and discards summary. Christina replies through normal Full App chat flow; Pet mirror/TTS follow existing final-reply rules. No Pet autonomous commentary, no screenshot persistence, no background monitoring. `renderer-chat-smoke.js` PASS; 9 new TASK-172B smoke tests in `task171a-capture-smoke.js` PASS. Windows manual smoke PASS: all handoff, cancel, privacy, and regression paths confirmed.

- TASK-171A-MULTIMONITOR-SCOPE-FIX DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-30): Multi-monitor capture scope bug found during TASK-172A-OCR-POLISH manual smoke — OCR summary included text from both monitors simultaneously. Root cause: `screen:capture-once` handler fell through to `sources[0]` (virtual desktop spanning all screens) when `display_id` matching failed. Fix: fail safely with `primary-display-ambiguous` when multiple sources exist and `display_id` matching fails; `sources[0]` only for single-source systems. `renderer.js` maps `primary-display-ambiguous` to clean zh-TW message. Windows manual smoke PASS (dual-monitor): primary screen "PRIMARY SCREEN ONLY 111" captured correctly; secondary screen "SECONDARY SCREEN 222" was NOT included in OCR summary — capture scope confirmed to primary display only. Full App chat, Pet direct input, voice/STT, TTS, Quiet Mode, click-through: no regression.

- TASK-172A-OCR-POLISH DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-30): OCR Image Preprocessing / Quality Improvement (v0.4 screen context slice 2A-OCR-POLISH). Preprocessing pipeline: grayscale → 2× upscale (LANCZOS, capped at 6000px/36MP) → contrast enhance (1.5×) → sharpen. Tesseract config: --psm 11 --oem 3 --dpi 150. Language: chi_tra probed at startup, falls back to eng if missing. Output cleanup: drops symbol-only garbage lines, collapses 5+ repeated chars to 3, preserves code/URL/path-like lines, safety fallback at 60% removal threshold, bounded to 800 chars. All preprocessing in memory; no disk write; no external upload; no /chat call. Windows manual smoke PASS: preprocessing pipeline ran in memory with no temp files; visible "螢幕摘要" produced; primary-screen text extracted correctly; no raw base64, JSON, Python traceback, provider internals, or file paths in UI; /chat not called; Pet Bubble did not receive screenshot or summary; "清除截圖" reset state; Full App chat, Pet direct input, voice/STT/TTS, Quiet Mode, click-through: no regression. NOTE: OCR output can still contain UI noise from window chrome and icons — expected Tesseract limitation on full-desktop screenshots. Quality is improved and sufficient for this slice; further refinement deferred to future tasks.

- TASK-172A-OCR-BACKEND DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-30): NOTE: backend OCR path confirmed working; OCR quality on full UI screenshots is rough (Tesseract limitation — future polish work). Real text extraction works end-to-end. Backend Local OCR Endpoint Design (v0.4 screen context slice 2A-OCR-B). Designs Option B backend OCR to replace the renderer-side tesseract.js Option A that was rejected (nodeIntegration:false + contextIsolation:true). Architecture: renderer → window.dragonPet.analyzeScreen(dataUrl) → preload IPC screen:analyze-once → main.js → POST /ocr/extract → ocr_service.py. Provider: pytesseract (preferred, requires Tesseract binary) or easyocr (Python-only, heavier). Input: base64 dataUrl, 20 MB limit, in-memory decode, no disk persistence by default; temp file (if unavoidable) deleted immediately in finally block. Output: cleaned/bounded 800-char text; "螢幕摘要:\n{text}" or "未偵測到可用文字。". Error codes: 9 reason codes → clean zh-TW UI messages, no raw tracebacks. Privacy: localhost only, no cloud, no history, no /chat, no Pet Bubble. Performance: 30 s IPC timeout; analyze button disabled during OCR. Testing plan: 8 backend pytest tests + 9 desktop smoke tests documented. No runtime files modified in this docs-only step.

- TASK-172A-OCR DONE — OPTION A REJECTED / SAFE FALLBACK PASS / DONE - PASS (2026-05-30): NOTE: real OCR text extraction NOT complete. Option A (renderer-side tesseract.js) formally rejected (nodeIntegration:false + contextIsolation:true prevent require() in renderer). Clean ocr-init-failed fallback + DevTools diagnostic wired. Option B (backend POST /ocr/extract) is next. Wire Actual OCR Provider for Screenshot Analysis (v0.4 screen context slice 2A-OCR). Replaces the `runOcrAnalysis()` stub from TASK-172A with a real local OCR provider. Strategy: Option A (renderer-side tesseract.js, lazy worker init, eng+chi_tra) preferred if bundle ≤10 MB and cold-start ≤5 s; fall back to Option B (backend FastAPI POST /ocr/extract via screen:analyze-once IPC, pytesseract or easyocr) if feasibility gate fails. Decision record template provided. Input: in-memory dataUrl only, size-guarded (20 MB string limit). Output: cleaned, collapsed, truncated to 800 chars; "螢幕摘要：\n{text}" or "未偵測到可用文字。". Performance: async, button disabled during OCR, no overlapping analyses. Privacy: memory-only, no upload, no disk save, explicit confirmation every time. Error table covers 9 failure cases with clean zh-TW messages. /chat boundary: hard — no call, no injection, no Pet Bubble commentary. No new UI elements; all display logic already wired by TASK-172A. New test cases documented (§9). No runtime files modified in this docs-only step.

- TASK-172A DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-29): Screenshot OCR Summary Implementation (v0.4 screen context slice 2A). Added "分析這張" button (disabled until screenshot exists), sensitive-content confirmation via window.confirm (mentions passwords, API keys, private messages), "正在分析…" status, OCR unavailable fallback ("分析功能目前不可用。"), "清除截圖" button to reset screenshot + summary, `#analyze-screen-summary` panel. OCR stub `runOcrAnalysis()` returns unavailable fallback — no cloud vision, no /chat call, no external upload, no disk save. New capture clears prior summary. 10 new TASK-172A smoke tests added to task171a-capture-smoke.js (static checks, button state, confirmation dialog, cancel, confirm+fallback, no /chat, clear resets state, no raw base64). `confirmOverride` option added to loadRenderer sandbox. TASK-171A scope regex tightened to allow "tesseract" in comments. All automated checks PASS: renderer-chat-smoke PASS, pet-renderer-smoke 226 PASS, pet-window-smoke 45 PASS, pytest 633 PASS, git diff --check CLEAN.

- TASK-172A DEFINED (docs-only) (2026-05-29): Screenshot OCR Summary Implementation Design (v0.4 screen context slice 2A). Next implementation slice after TASK-171A. After a screenshot exists in memory, user clicks "分析這張" → confirms sensitive-content warning → app runs local OCR → displays a clean screen summary in Full App UI. No /chat handoff (deferred to TASK-172B). OCR strategy: Option A (renderer-side tesseract.js, no IPC, no backend change) preferred; fall back to Option B (backend FastAPI POST /ocr/extract via narrow screen:analyze-once IPC) if bundle size or cold-start regression is unacceptable. If neither available: clean fallback "分析功能目前不可用。". Summary output: strip/truncate raw OCR text (max 800 chars), display as "螢幕摘要：\n{text}"; no useful text → "未偵測到可用文字。". Storage: summary in renderer memory only; no disk save; no screenshot history; "清除截圖" clears both screenshot and summary. Privacy: no cloud OCR, no external upload, explicit confirmation every time. /chat boundary: no /chat call, no summary injection, no Pet Bubble commentary. Error table covers 7 failure cases with clean zh-TW messages. Preserved: TASK-171A capture, Full App chat, Pet direct input, voice/STT/TTS, Quiet Mode, CT recovery strip. No runtime files modified in this docs-only step.

- TASK-172 DEFINED (docs-only) (2026-05-29): Screenshot Analysis / User-Confirmed Vision Design (v0.4 screen context slice 2). Designs user-confirmed screenshot analysis flow: two explicit actions required (capture, then confirm). Analysis only after "分析這張" confirmation + sensitive-content warning acknowledgement. Provider strategy: local-first (OCR or local vision), no silent cloud fallback. Summary output only (not raw dataUrl to /chat). Task split: TASK-172A (analysis → summary text only), TASK-172B (summary → /chat context handoff, deferred). No runtime files modified in this docs-only step.

- TASK-171A DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-29): User-Triggered Screenshot Capture Implementation Design (v0.4 screen context slice 1A). Concrete implementation spec for the first working screenshot slice. Entry point: Full App "擷取螢幕" button only (Pet Menu and voice trigger deferred). Capture target: primary display full screenshot via Electron desktopCapturer; multi-monitor, active window, and region selection deferred. Storage: in-memory only (one data URL at a time); never written to disk, never uploaded, never sent to /chat, not persisted across restart. IPC: single narrow channel screen:capture-once (renderer → main); main returns { ok, dataUrl } or { ok:false, error:"reason-code" }; preload exposes only captureScreen() function; no broad filesystem/desktop APIs exposed. UI: button disables during capture; success shows "螢幕截圖完成。尚未儲存，可供後續分析使用。"; failure shows clean Chinese message per reason code; no stack traces, Electron internals, file paths, or JSON in UI or Pet Bubble. Privacy: user-triggered only; no automatic analysis; no external upload; no disk save. Pet: not involved in slice 1A (Full App button only); Quiet Mode does not block explicit capture. Scope out: OCR, computer vision, screenshot-to-chat, cloud vision, background monitoring, screenshot persistence, multi-monitor picker, Pet Menu capture, voice trigger, global hotkeys, backend schema change. No runtime files modified in this docs-only step.

- TASK-171 DEFINED (docs-only) (2026-05-29): Screen Context / User-Triggered Screenshot Design (v0.4 screen context slice 1). Designs privacy-safe explicit user-triggered screenshot capture. User-triggered only (no background monitoring, no periodic screenshot, no hidden capture, no always-on vision). Recommended first entry point: Full App button; Pet Menu shortcut deferred. Capture target: full primary display screenshot only (active-window and area selection deferred). Privacy: screenshot kept in memory only, not saved to disk by default, not uploaded, not sent to /chat automatically. Analysis deferred to TASK-172 with explicit user confirmation. UX: clear "正在截圖…" capturing status + clean "截圖完成，尚未儲存" confirmation; no raw paths or debug in Pet Bubble. Error handling: clean Chinese fallback for permission denied, API unavailable, no display, and capture failure. Click-through forced OFF when Pet Menu capture used; Quiet Mode does not block explicit capture. Voice trigger deferred (requires confirmation before any capture). Redaction boundary documented for future: passwords, API keys, browser content must be confirmed before analysis. Implementation direction: Electron desktopCapturer + narrow screen:capture-once IPC bridge; no global hotkeys, no broad filesystem/system APIs. Scope out: OCR, computer vision, screen analysis, background monitoring, cloud vision, screenshot persistence, Live2D, backend schema change. No runtime files modified in this docs-only step.

- TASK-170 DONE (docs-only checkpoint) (2026-05-29): Voice Interaction v0.3 Release Checkpoint. Records the completion of the full v0.3 voice loop: push-to-talk microphone capture → STT transcription → /chat → Christina text reply → system TTS playback with voice selection and speech controls (rate 0.7–1.3, pitch 0.8–1.3, volume 0.0–1.0). Completed capabilities: explicit push-to-talk recording, recording indicator, mic permission handling, in-memory audio Blob only, STT via backend POST /stt/transcribe, clean STT fallback, voice transcript auto-send to /chat, thinking bubble → final Christina reply, system TTS playback (window.speechSynthesis, fully local), TTS toggle (OFF by default), stop speech button, speaking indicator, voice selection (getVoices + onvoiceschanged), rate/pitch/volume sliders, reset-to-default, settings persistence via narrow localStorage keys. Safety boundaries preserved: no wake word, no always-listening, no hidden capture, no raw audio persistence, no cloud TTS, no voice cloning, no Live2D, no screen capture/OCR/vision, no backend schema change, no global hotkeys. All manual smoke passes confirmed (TASK-167A through TASK-169). Automated: pet-renderer-smoke 226 PASS, pet-window-smoke 45 PASS, renderer-chat-smoke PASS, pytest 633 PASS, git diff --check clean. Known limitations: generic system voices, no Christina character voice, no TTS emotion control, no Live2D sync, no screen context, no proactive voice, no background listening by design. Recommended next: Option A (Screen Context / Screenshot Design), Option B (Character Voice Provider Strategy), Option C (Voice UX Polish / Latency Cleanup).

- TASK-169 DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-29): TTS Voice Selection / Speech Controls (v0.3 voice polish slice). Added voice selector (speechSynthesis.getVoices(), onvoiceschanged, user-readable name+lang labels, safe empty-list fallback), rate (0.7–1.3, default 1.0), pitch (0.8–1.3, default 1.0), and volume (0.0–1.0, default 1.0) sliders with value display, plus reset-to-default button. All values clamped before application to SpeechSynthesisUtterance. Persistence via narrow renderer localStorage keys (pet_tts_voice, pet_tts_rate, pet_tts_pitch, pet_tts_volume); corrupt/missing values fall back to safe defaults; localStorage unavailable → in-memory only, no crash. UI placed in Pet Menu as collapsible "語音設定 ▶/▼" panel (hidden by default); pet-menu max-height extended 144→260px with scale-aware overrides (small: 210px, large: 340px). Settings apply to final reply states only; thinking/recording/transcribing/debug text unchanged. TASK-168B stop button, interrupt model, speaking indicator, TTS toggle all preserved. Quiet Mode does not alter voice settings. Recording still cancels TTS. Scope clean: no cloud TTS, ElevenLabs, Azure, OpenAI, voice cloning, Live2D, wake word, always-listening, backend schema change, new IPC channel, or broad settings architecture. 15 new smoke tests (211→226 total). Automated: pet-renderer-smoke 226 PASS, pet-window-smoke 45 PASS, renderer-chat-smoke PASS, pytest 633 PASS, git diff --check clean.

- TASK-169 DEFINED (2026-05-29): TTS Voice Selection / Speech Controls Design (v0.3 voice polish slice). Designs voice selection from available system SpeechSynthesis voices and adjustable speech controls (rate 0.7–1.3, pitch 0.8–1.3, volume 0.0–1.0). Voice labels user-readable (name + lang); no internal debug URIs exposed. Fallback: empty voice list / unavailable selected voice → browser default, no crash. Controls placed in Pet Menu TTS submenu (preferred) or compact inline expand. Controls apply to final reply states only; thinking/recording/transcribing/debug text not spoken. Persistence via narrow renderer localStorage (namespaced keys: pet_tts_voice, pet_tts_rate, pet_tts_pitch, pet_tts_volume); corrupt/missing values clamp to safe defaults. TASK-168B stop button, interrupt model, speaking indicator, TTS ON/OFF toggle all preserved. Quiet Mode does not alter voice settings. Recording still cancels TTS. No cloud TTS, no voice cloning, no Live2D, no backend schema change, no new IPC channel, no broad settings architecture.

- TASK-168B DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-29): Pet TTS Playback (v0.3 voice slice 2B). Adds `window.speechSynthesis` TTS playback for final Christina replies. TTS is OFF by default; user enables via Pet Menu toggle ("語音播放: 關/開"). Trigger: final reply states only (speaking/long_reply) — not thinking, error, recording, transcribing. Length limit: 300 chars to SpeechSynthesis (full text still in bubble). Interrupt model: new reply cancels previous speech. Stop button visible during data-speaking="true". openPetVoiceRecording calls stopPetSpeech first to prevent mic feedback loop. Speaking state: teal CSS indicator (data-speaking on #pet-mode-root), distinct from recording (red) / transcribing (indigo) / thinking. CSS mutual exclusion hides speaking indicator during recording/transcribing. Quiet Mode does not suppress TTS (separate toggle). No cloud TTS, no Live2D, no wake word, no backend schema changes. 18 new smoke tests (193 → 211 total). Automated: pet-renderer-smoke 211 PASS, pet-window-smoke 45 PASS, renderer-chat-smoke PASS, pytest 633 PASS, git diff --check clean.
- TASK-168B-FIX IMPLEMENTED (2026-05-29): Speaking indicator not visible — root cause: setSpeakingState only toggled root.dataset.speaking but never removed the HTML `hidden` attribute from #pet-speaking-indicator. The CSS rule `.pet-speaking-indicator[hidden] { display: none !important; }` overrode the show rule at all times. Fix: added `indicator.hidden = !active` to setSpeakingState, matching the identical pattern in setRecordingState and setTranscribingState. Smoke test updated with 2 new assertions. All 211 + 45 checks pass, pytest 633 PASS, git diff --check clean. DONE - included in TASK-168B WINDOWS MANUAL SMOKE PASS.
- TASK-168B WINDOWS MANUAL SMOKE CLOSEOUT (2026-05-29): Manual smoke passed. TTS toggle visible in Pet Menu (default OFF). Final Christina replies spoken aloud when TTS enabled. Thinking / recording / transcribing / debug text not spoken. Teal speaking indicator and stop button (■) appear during speech; stop button cancels audio and clears indicator. New reply interrupts previous speech safely. Voice recording cancels TTS (no feedback loop). Quiet Mode ON does not suppress user-initiated TTS. Speaking indicator works at S/M/L scales. TASK-166E direct input, TASK-167A recording, TASK-167B STT, TASK-167C voice-to-chat: no regression. Smoke bug fixed during run: TASK-168B-FIX (setSpeakingState hidden-attribute guard). Scope confirmed clean: no cloud TTS, Live2D, wake word, always-listening, screen capture, OCR, backend schema change, or global hotkeys.

- TASK-168A DEFINED (2026-05-29): Pet TTS Playback Design (v0.3 voice slice 2A). Designs TTS playback so Christina speaks her final text replies aloud. TTS is OFF by default; user enables via Pet Menu toggle. Provider: Web Speech API SpeechSynthesis (Chromium/Electron renderer, fully local, zero cost) with OS TTS IPC fallback (say / espeak / PowerShell Speak). No external cloud TTS; no user text leaves the local machine. Trigger: final assistant reply text only — not thinking text, not errors, not user messages, not debug/JSON. Interrupt model: new reply cancels previous speech. Length limit: 300 chars for TTS (full text still shown in bubble). Speaking state: teal CSS indicator (data-speaking attribute), distinct from recording (red) / transcribing (indigo) / thinking. Recording cancels active TTS immediately to prevent mic feedback. Quiet Mode does not suppress TTS (separate toggle). CT: playback needs no CT change; opening TTS controls forces CT OFF. Pet direct text input and Full App mirrored replies also eligible for TTS. Scope out: Live2D lip sync, wake word, always-listening, cloud TTS, settings persistence, broad provider architecture, backend schema changes, global hotkeys.
- TASK-167C DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-29): Voice Transcript → /chat Handoff (v0.3 slice 1C). Added `handlePetVoiceChatSend` in pet-renderer.js: guards double-send via petChatPending, calls forceClickThroughOff + closePetDirectInput, sets thinking bubble, awaits sendPetChatMessage(transcript), routes reply/error through existing stateForChatSource / setBubbleState / rememberRecentPetReply path. Updated _petSttTranscribeChunks success path: trims transcript, rejects > 2000 chars with clean Chinese message (PET_VOICE_TRANSCRIPT_TOO_LONG_MSG), auto-sends valid transcripts — no confirmation step. voiceTranscript cleared after use. Reuses /chat pipeline exactly as Pet direct text input (TASK-166E) — no new endpoint, no schema change. Exported: PET_VOICE_CHAT_MAX_CHARS, PET_VOICE_TRANSCRIPT_TOO_LONG_MSG, handlePetVoiceChatSend. 13 new smoke tests added (193 total). Automated: pet-renderer-smoke 193 PASS, pet-window-smoke 45 PASS, renderer-chat-smoke PASS, pytest 633 PASS, git diff --check clean. Scope preserved: no TTS, wake word, always-listening, screen capture, Live2D, voice-specific endpoint, backend schema change, or raw diagnostics.

- TASK-167C DEFINED (2026-05-28): Voice Transcript to Chat Handoff Design (v0.3 slice 1C). Wires valid non-empty transcript from TASK-167B into the existing /chat pipeline reusing TASK-157 thinking/reply/error state sequence. Source identifier: "pet_voice". Auto-send model: valid transcript sent immediately after STT, no confirmation step. Transcript validation: trim before send; empty/silent/unavailable/error → no send (TASK-167B fallbacks); > 2000 chars → clean length-error, no send. Chat pipeline: reuse Pet direct text input /chat path; no new endpoint, no schema change. Mutual exclusion: voice chat and text input cannot both be active; CT forced OFF for full recording→transcribing→chat cycle; CT recovery strip preserved. Quiet Mode: suppresses idle only — voice chat, thinking, reply, and error all appear; after reply expiry under Quiet Mode ON, Pet returns to collapsed/no-hint. Error table: STT unavailable/timeout/empty → no send + TASK-167B fallback msg; transcript too long → clean Chinese msg; /chat offline after transcript → existing chat offline fallback; LLM error → existing chat error fallback. Privacy: no raw audio persistence, no always-listening, no wake word, no hidden capture, voiceTranscript cleared after use. Scope out: TTS, wake word, always-listening, screen capture, OCR, Live2D, /chat schema change, global hotkeys, confirmation/edit step, multi-turn history. Preserved: TASK-167A recording lifecycle, TASK-167B STT, TASK-166A–E Pet window behaviors, TASK-160/162 Quiet Mode, TASK-157 thinking bubble, TASK-149/156 clean bubble.

- TASK-167B DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-28): Voice STT Transcription Design (v0.3 slice 1B). Implements `transcribeAudioBlob(blob) -> Promise<string|null>` replacing TASK-167A stub. Backend: `POST /stt/transcribe` FastAPI endpoint (multipart UploadFile, 10 MB cap); `app/stt/stt_service.py` with lazy-loading faster-whisper "tiny" model; safe "unavailable" fallback when faster-whisper not installed; empty-bytes checked before Whisper; no disk I/O. IPC: `stt:transcribe` channel in main.js using built-in Node.js `http`; no new npm dependencies. Pet UI: `data-transcribing="true"` state with indigo spinner distinct from recording dot; 30 s timeout; error taxonomy (stt_unavailable, stt_timeout, stt_offline, stt_error) maps to clean Chinese Pet Bubble messages; non-empty transcript stored in presenceState.voiceTranscript for TASK-167C. Mutual exclusion: transcribing hides text input and recording indicator. No /chat call (deferred to TASK-167C). Privacy: no disk audio, no always-listening, no external STT API. New tests: 14 backend pytest tests + 15 renderer smoke tests + 4 window smoke tests. Automated: pet-renderer-smoke 180 PASS, pet-window-smoke 45 PASS, renderer-chat-smoke PASS, pytest 633 PASS, git diff --check clean.
- TASK-167B BUG FIX (2026-05-28): Two bugs fixed in stop-recording → STT flow. (1) Toggle bug: second mic click called cancelPetVoiceRecording (discard) instead of stopPetVoiceRecording (transcribe) — no message appeared on stop. (2) MediaRecorder async timing: Blob was built synchronously after recorder.stop() before dataavailable fired, producing empty audio. Fix: moved Blob construction into recorder stop event handler using voiceStopAndTranscribe flag; extracted _petSttTranscribeChunks helper. Smoke test testStopVoiceRecordingEntersTranscribingState updated. Automated validation: 180/45 smoke + 633 pytest PASS.

- TASK-167A DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (2026-05-28): Pet Voice Push-to-talk UI / Mic Capture Design. Mic/Voice button (🎤) added to Pet nav bar at all S/M/L scales. Toggle-to-record lifecycle: click once to start, click again or press Esc or click ✕ to cancel. `data-recording="true"` on `#pet-mode-root` drives CSS state. Recording indicator with pulsing red dot shown during capture. `navigator.mediaDevices.getUserMedia({audio:true})` + `MediaRecorder` (prefer `audio/webm;codecs=opus`). 30 s hard timeout. Audio kept in-memory Blob only — no disk write, no `/chat` send. `transcribeAudioBlob(blob) → Promise<null>` stubbed as TASK-167B boundary. Click-through forced OFF before recording starts. Voice/text mutual exclusion (voice start closes text panel; text start cancels recording; CT-ON cancels recording). Quiet Mode does not suppress user-initiated recording. Clean Pet Bubble error messages for permission denied, no mic, unsupported, timeout. Narrow `session.setPermissionRequestHandler` for `media` only in main.js. 19 new pet-renderer-smoke tests + 3 new pet-window-smoke tests. All existing TASK-149–TASK-166E behaviors preserved. Automated: pet-renderer-smoke 165 PASS, pet-window-smoke 41 PASS, renderer-chat-smoke PASS, pytest 619 PASS, git diff --check clean.

- TASK-167A DEFINED: Pet Voice Push-to-talk UI / Mic Capture Design (v0.3 slice 1A). First implementation slice of TASK-167 voice interaction — designs the Pet-side push-to-talk UI control and microphone capture lifecycle only. Preferred mode: toggle-to-record (click once to start, click again to stop). Covers: compact Mic/Voice button in Pet nav bar (no new image assets); `data-recording` attribute on `#pet-mode-root` for CSS state; recording indicator distinct from thinking bubble; permission request only on explicit user action; clean fallbacks for permission denied / no mic / capture failure; in-memory audio Blob (no disk write, no send to `/chat`); STT handoff boundary `transcribeAudioBlob(blob) → Promise<string>` stubbed for TASK-167B; Click-through forced OFF before recording and blocked while recording; voice/text mutual exclusion (starting voice closes text input and vice versa); Quiet Mode suppresses idle only; 4-condition error table. No STT, TTS, wake word, always-listening, screen capture, OCR, Live2D, or backend/schema changes in this slice. Preserved-behavior table covers TASK-148–TASK-166E.

- TASK-167 DEFINED: Voice Interaction v0.3 Push-to-talk Design (v0.3 slice 1 of N). Designs user-initiated push-to-talk voice input from the Pet Window. No wake word, no always-listening. Covers: voice/mic entry point in Pet Window (hold or click to record); recording lifecycle (start, stop, timeout, cancel); STT/transcription (prefer local Whisper, provider-neutral interface, transcript validation before send); chat pipeline reuse (transcript → same thinking/reply/error sequence as TASK-166E/TASK-157); TTS deferred to TASK-168+; privacy/safety boundaries (no background listening, explicit mic permission, visible indicator, no raw audio persistence); Click-through forced OFF before recording; Quiet Mode suppresses idle only, not voice input; S/M/L scale layout; 6-condition error table (permission denied, no mic, STT failure, silent audio, backend offline, LLM error). Implementation split recommendation: 167A (mic capture + UI), 167B (STT integration), 167C (chat wiring), 167D (error handling). Preserved-behavior table covers TASK-148–TASK-166E. No backend/schema/wake-word/always-listening/screen-capture/OCR/Live2D changes in this docs-only step.
- TASK-166E DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS: Pet Direct Text Input Design (v0.2 slice 5/5). Designs a compact Pet-side text input that lets the user send a message from the Pet Window into the existing `/chat` pipeline without switching to the Full App. Reuses TASK-157 thinking-bubble → reply → error state sequence. Opening input forces click-through OFF (TASK-166D pattern). Quiet Mode suppresses idle presence only — Pet input and replies are unaffected. Covers S/M/L scale layout, safety/sanitization, error/offline fallback, and preserved-behavior table (TASK-148–TASK-166D). No voice, screen capture, Live2D, backend/schema changes, or full history panel.
- TASK-166E click-fix (2026-05-28): Windows manual smoke found that with Click-through ON, opening Pet direct input showed the panel but input was unreachable. Root cause: `forceClickThroughOff` did not await the IPC roundtrip, so `setIgnoreMouseEvents(false)` + `petWindow.focus()` hadn't completed before `field.focus()` was called. Fix: `forceClickThroughOff` now returns the IPC Promise; `openPetDirectInput` is `async` and awaits it; `petWindow.focus()` added to main.js CT-off handler; defensive `pointerdown`/`focus` listeners guard the panel. 6 new pet-renderer-smoke + 1 pet-window-smoke tests added. Smoke: 135 + 38 PASS, 619 pytest PASS, git diff --check CLEAN.
- TASK-166E click-fix2 — CT recovery strip (2026-05-28): Second manual smoke failure found the recovery model was still broken: with CT ON, all normal Pet controls (Chat button, Menu, input panel) are unreachable because clicks pass through the window — so recovery cannot depend on clicking any Pet UI. Fix: added `#pet-ct-recovery-strip` — a full-width (100%), 32 px high, transparent, `pointer-events: auto`, `-webkit-app-region: no-drag` div at the top of the Pet window; shown only while CT is ON (z-index 11, above drag handle and controls); wires both `pointerenter` and `mousemove` to `forceClickThroughOff` so the user exits CT mode by hovering the top edge of the Pet window — reliable because `{ forward: true }` still delivers these events to the renderer. `setClickThrough` also closes the direct input panel when CT turns ON (visible-but-unreachable panel avoided). 11 new click-fix2 renderer tests + 1 CSS check added. Smoke: 146 renderer + 38 window checks PASS. 619 pytest PASS. git diff --check CLEAN. No backend/schema/voice/Live2D changes.
- TASK-166D DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS: Pet Click-through Toggle Design (v0.2 slice 4/5). Designs a safe click-through mode that lets mouse clicks pass through the Pet Window to apps behind it while keeping the Pet visible. Specifies a recovery path (hover/recovery strip and/or Full App control) so the user is never trapped. Documents safety forced-OFF cases: Pet Menu open, details open, controls in use, drag in progress, reset triggered. Default OFF, session-local only (persistence deferred). IPC channel `pet:set-click-through` with `BrowserWindow.setIgnoreMouseEvents` and `{ forward: true }` for hover recovery. UI toggle in Pet Menu with `aria-pressed` indicator. Recovery strip must ship with the toggle. Preserved-behavior table covers TASK-148–TASK-166C. No voice, no screen capture, no Live2D, no backend/schema changes.
- TASK-166C DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS (incl. Quiet Mode regression fix 2): Pet Bubble Placement / Tail Polish Design (v0.2 slice 3/5). Designs a CSS speech-bubble tail and intentional bubble placement so the Pet bubble feels visually connected to the character rather than a floating app card. Specifies tail as a CSS `::before`/`::after` pseudo-element — no new image assets. Documents bubble placement rules: stays in readable area, avoids covering character face, does not overlap controls. Covers all existing bubble states (idle, thinking, reply, error, collapsed, details disclosure). Defines per-scale layout expectations for Small (225×300), Medium (300×400), and Large (375×500) with preference for scalable CSS values over pixel patches. Documents Quiet Mode interaction: collapsed state hides tail cleanly. Risks and fallbacks table included. Preserved-behavior table covers TASK-148 through TASK-166B. Initial smoke found tail clipped by `.pet-bubble { overflow: hidden }`; fix changed bubble to `overflow: visible` and improved tail contrast (16×16, border 0.28, box-shadow). Re-smoke PASS. Windows manual smoke PASS (2026-05-27). Quiet Mode regression fix (2026-05-27): `isIdleRotationEligible` and `fireIdleRotation` now check `quietMode` — idle timer callbacks can no longer show the idle bubble when Quiet Mode is ON. 4 new regression smoke tests added. Quiet Mode regression fix 2 (2026-05-27): Root cause was that `#pet-hint` paragraph is shown by CSS when `data-bubble-state='collapsed'`, entirely outside the bubble state machine. Fix: `setQuietMode` now writes `root.dataset.quietMode='true'`; CSS rule `.pet-shell[data-quiet-mode='true'] .pet-hint { display:none }` suppresses hint. Also guarded `toggleDetailsFromMenu` against showing `idle_default` while quiet. 5 new smoke tests added. Final smoke counts: pet-renderer-smoke.js 104 PASS, pet-window-smoke.js 30 PASS, 619 pytest PASS, `git diff --check` CLEAN. Windows manual re-smoke PASS (2026-05-27): hint hidden immediately on Quiet Mode ON, idle/default/presence text fully suppressed, thinking/reply/error bubbles unaffected, details menu guard confirmed, scale presets and transparent shell unaffected.

- TASK-166B DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS: Pet Overlay Scale Presets (v0.2 slice 2/5). Adds Small (225×300) / Medium (300×400, default) / Large (375×500) scale presets to the Pet Window. Scale persisted via `userData/pet-window-state.json` merge-write (`scale` key); delivered to renderer as `?scale=` URL param on launch. One new IPC channel (`pet:set-scale`) resizes the window, clamps position to work area, and saves state. S/M/L buttons in Pet menu with `aria-pressed` active indicator. Fluid CSS layout (`width: 100%; height: 100%`) replaces hardcoded 300×400. `data-scale` attribute on `#pet-mode-root` drives avatar size overrides at Small and Large. Smoke counts: pet-renderer-smoke.js 89 PASS (+6), pet-window-smoke.js 30 PASS (+8), 619 pytest PASS, `git diff --check` CLEAN. Windows manual smoke PASS (2026-05-27).

- TASK-166A DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS: Pet Overlay Transparent Shell Polish (v0.2 slice 1/5). Adds `backgroundColor: "#00000000"` and `skipTaskbar: true` to `createPetWindow()` in `main.js` — companion overlay no longer appears in the Windows taskbar. Adds `filter: drop-shadow(0 2px 8px rgba(0,0,0,0.18))` to `.pet-avatar` in `pet.css` for character readability on varied wallpapers. Changes `.pet-avatar-container` background from `rgba(255,255,255,0.36)` to `transparent` so the character sits naturally against the frosted shell. Refines `pet-renderer-smoke.js` filter guard: replaces broad `filter:` prohibition with targeted destructive-filter prohibitions + positive `drop-shadow` assertion. Smoke counts: pet-renderer-smoke.js 83 PASS (unchanged), pet-window-smoke.js 22 PASS (2 new), renderer chat smoke PASS, 619 pytest PASS, `git diff --check` CLEAN. Windows manual smoke PASS (2026-05-27).

- TASK-166 DONE - WINDOWS MANUAL SMOKE PASS / DONE - PASS: Pet Overlay Shell Polish Design (v0.2). All 5 slices DONE: TASK-166A (transparent shell), TASK-166B (scale presets), TASK-166C (bubble tail + Quiet Mode regression fix), TASK-166D (click-through toggle + recovery strip), TASK-166E (Pet direct text input, click-fix, click-fix2 CT recovery strip). Windows manual smoke PASS (2026-05-28): click-through recovery reliable, Pet direct input usable at all scales, clean Pet Bubble speech, Quiet Mode unaffected, no regressions across 166A–166D. Originally designs 7 areas of overlay shell improvement: (1) transparent/frameless overlay presentation with character-readable contrast and fallback; (2) always-on-top edge case audit + re-assertion strategy without focus stealing; (3) drag/position behavior — no change, audit only; (4) scale presets (Small 225×300 / Medium 300×400 / Large 375×500) with URL-param delivery, merge-write persistence, and silent
