# Development Roadmap

> dragon-pet-ai
> Status: LIVING DOCUMENT
> Last Updated: 2026-05-21
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

**Goal:** Establish the running skeleton of both the backend and desktop app. No real AI, no real features — just the infrastructure working end-to-end.

**Status:** COMPLETE

| Task | Name | Status |
|---|---|---|
| TASK-003 | FastAPI backend skeleton + /health + /chat mock | DONE |
| TASK-004 | Electron desktop shell + chat UI | DONE |

**Exit Criteria — Met:**
- `uvicorn` starts the backend without errors ✅
- `npm start` opens the Electron window ✅
- Desktop can POST to `/chat` and display the mock response ✅

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
- All messages persisted to SQLite ✅
- Manual memory CRUD API ✅
- Memory management UI ✅
- Approved memory context builder with safety filters ✅
- Memory-aware chat with two-layer safety gate ✅
- MemoryInjectionAudit model + audit row creation ✅
- Audit inspection API (read-only, paginated, safe metadata only) ✅
- Audit Logs UI ✅
- pytest: 226 passed, 0 failed ✅
- All runtime smoke checks passed ✅

**Not implemented in Phase 3 (remains deferred):**
- Real AI / LLM provider
- Voice (TTS / STT)
- Live2D
- Semantic retrieval / vector database
- Automatic memory extraction

---

## Phase 4 — LLM Adapter Integration

**Goal:** Wire the approved memory context pipeline to a real LLM provider behind a feature flag, using an adapter pattern that keeps mock as the default.

**Status:** IN PROGRESS — provider adapter exists behind flags; mock `/chat` LLM wiring smoke passed; real-provider `/chat` wiring contract tests passed with mocked HTTP only; in-memory usage meter, non-secret provider settings API, Provider Settings UI, secure key storage abstraction, key save/clear endpoints, key UI enablement, Provider Test Connection design, backend Test Connection implementation (TASK-059), Opus safety review PASS (TASK-059R), Test Connection UI enablement (TASK-060), hardening tests (TASK-062), and Provider Settings UI layout polish (TASK-063) are complete; explicit cost acknowledgement required per click; no automatic test after Save Key; no live external API call; live provider remains disabled by default

**Recommended primary path: Option A — LLM Adapter Integration**

| Option | Description | Notes |
|---|---|---|
| **A — LLM adapter integration** ⬅ selected | Wire approved memory context to a real LLM behind explicit flags | TASK-031 → TASK-051 |
| B — TTS voice output | Add basic text-to-speech output | Deferred — more valuable after real LLM is wired |
| C — UI polish and packaging | Improve layouts, scrolling, package as installable app | Deferred — better after LLM adapter done |
| D — Daily summary / memory review | Generate end-of-day summaries and memory review UI | Deferred — requires LLM adapter first |

**Task Sequence:**

| Task | Name | Status |
|---|---|---|
| TASK-030 | Phase 4 Planning | DONE |
| TASK-031 | LLM Adapter Design | DONE |
| TASK-032 | LLM Provider Interface Skeleton | DONE |
| TASK-033 | Mock Provider Compatibility Tests | DONE |
| TASK-034 | Real Provider Config Design | DONE |
| TASK-034R | Real Provider Config Safety Review (Opus) | DONE — PASS WITH CHANGES |
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
| TASK-059R | Provider Test Connection Safety Review (Opus) | DONE — PASS |
| TASK-060 | Provider Test Connection UI Enablement | DONE |
| TASK-061 | Provider Test Connection Runtime Smoke Check | DONE — PASS WITH EXPECTED LIMITATION |
| TASK-062 | Provider Test Connection Hardening Tests | DONE |
| TASK-063 | Electron Provider Settings UI Polish and Layout Fix | DONE |
| TASK-064 | Provider Settings UI Runtime Smoke Re-check | DONE — PASS WITH NON-BLOCKING UI NOTES |
| TASK-065 | Phase 4 Provider Settings Stabilization Summary | DONE |

**Phase 4 Key Safety Constraints:**
- `LLM_PROVIDER_ENABLED=false` is the default; real provider requires explicit opt-in via env var
- `LLM_CHAT_ENABLED=false` must gate `/chat` LLM adapter use separately from provider selection
- API key loaded from environment variable only — never hardcoded, never logged, never sent to frontend, never in repr/str
- `/chat` response schema remains `reply / mood / source` — unchanged
- Memory-aware chat two-layer gate is unchanged
- No automatic retries in Phase 4 (at most one real provider call per `/chat` turn)
- Non-2xx provider response bodies are opaque — not parsed, not logged, not returned
- No tool execution, no file access, no autonomous action, no automatic memory extraction
- Live smoke is blocked until explicit user cost confirmation and TASK-044 go/no-go criteria are satisfied
- BYOK is the recommended MVP path; provider settings UI design done (TASK-047); backend API design done (TASK-048); secure key storage design done (TASK-049); usage meter implementation done (TASK-050); non-secret settings API implementation done (TASK-051); Provider Settings UI implementation done (TASK-052); secure key storage abstraction done (TASK-053); provider key save/clear endpoints done (TASK-054); key UI enablement design done (TASK-055); Save Key / Clear Key UI done (TASK-056); key UI smoke passed (TASK-057); Test Connection design done (TASK-058); Test Connection backend done (TASK-059); safety review PASS (TASK-059R); Test Connection UI enabled in renderer (TASK-060); runtime smoke PASS WITH EXPECTED LIMITATION (TASK-061); hardening tests DONE — 470 passed (TASK-062); Provider Settings UI readability/layout polish DONE (TASK-063); runtime smoke re-check PASS WITH NON-BLOCKING UI NOTES (TASK-064); Phase 4 Provider Settings stabilization summary created (TASK-065); no live external provider call has occurred; no real API key has been used; recommended next: OS keychain backend implementation (TASK-066)

See `docs/PHASE4_PLAN.md`, `docs/LLM_ADAPTER_DESIGN.md`, `docs/LLM_PROVIDER_CONTRACT.md`, `docs/CHAT_LLM_WIRING_DESIGN.md`, `docs/CHAT_LLM_REAL_PROVIDER_WIRING_DESIGN.md`, `docs/COST_AND_MONETIZATION.md`, `docs/BYOK_PRODUCT_AND_SETTINGS.md`, `docs/USAGE_METER_DESIGN.md`, `docs/PROVIDER_SETTINGS_UI_DESIGN.md`, `docs/PROVIDER_SETTINGS_API_DESIGN.md`, `docs/SECURE_KEY_STORAGE_DESIGN.md`, and `docs/PROVIDER_TEST_CONNECTION_DESIGN.md` for full planning and design documents.

---

## Phase 5 — Assistant Capabilities

**Goal:** Add task management, project context, and carefully scoped tool execution.

**Status:** NOT STARTED

| Task | Name | Status |
|---|---|---|
| (TBD) | Basic task list (CRUD via chat) | Pending |
| (TBD) | Project planning support (conversational) | Pending |
| (TBD) | Read-only project file context (with safety layer) | Pending |
| (TBD) | Scheduled reminders | Pending |
| (TBD) | Tool execution framework (safety-gated) | Pending |

**Safety Requirements for Phase 5:**
- No shell command execution without a dedicated safety review
- File access restricted to user-approved directories only
- All tool actions logged and reversible where possible
- User must explicitly enable tool execution capability

---

## Future Product Track — Streamer Companion Mode

> Status: SIDE TRACK — design exploration only; not scheduled for implementation
> See: `docs/STREAMER_COMPANION_MODE.md`

A potential future direction that adapts the dragon-pet AI for live streaming contexts (Twitch, YouTube Live). The pet would run as an OBS overlay, react to stream events (follows, subs, raids), and respond to chat commands — giving streamers an on-screen AI companion with personality.

**This track is explicitly deferred** until the following are complete:
- Phase 4 LLM adapter stable and safety-reviewed (TASK-037)
- TTS voice output (Phase 5)
- A dedicated Streamer Mode safety design (STREAM-001 — not yet created)

| Future Task ID | Name | Status |
|---|---|---|
| STREAM-001 | Streamer Companion Mode Safety Design | Not scheduled |
| STREAM-002 | OBS Browser Source Overlay Architecture | Not scheduled |
| STREAM-003 | Twitch EventSub Integration Design | Not scheduled |
| STREAM-004 | Chat Sampling and Filtering Design | Not scheduled |
| STREAM-005 | Public Content Safety Layer Design | Not scheduled |
| STREAM-006 | Per-Session Token Budget Design | Not scheduled |
| STREAM-007 | Streamer Mode MVP Implementation | Not scheduled |
| STREAM-008 | Streamer Mode Smoke Check | Not scheduled |

Key differences from personal mode: public broadcast context, chat firehose input, per-session hard token budget, TTS required, higher content safety bar. See `docs/STREAMER_COMPANION_MODE.md` for full design exploration.

---

## Principles Across All Phases

1. **Docs before code.** Each feature must be specified before it is implemented.
2. **Scope discipline.** Features belong to one phase; do not implement Phase N+1 features during Phase N.
3. **Safety first.** Any capability that touches the user's system requires a safety design step before implementation.
4. **Local first.** All user data stays on device unless the user explicitly opts into a cloud feature.
5. **Reversible steps.** Prefer designs that can be undone or corrected without data loss.
