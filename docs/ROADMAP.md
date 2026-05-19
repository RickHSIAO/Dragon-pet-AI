# Development Roadmap

> dragon-pet-ai
> Status: DRAFT
> Last Updated: 2026-05-19
> Owner: TASK-001

---

## Overview

The project is developed in discrete phases. Each phase has a clearly defined scope and must not implement features belonging to later phases. This prevents scope creep and keeps each task reviewable and verifiable.

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
Docs      Skeleton  Chat+Char  Memory    Voice     Assistant
```

---

## Phase 0 — Project Definition

**Goal:** Establish the project structure, specifications, and documentation before writing any runtime code.

**Status:** IN_PROGRESS

| Task | Name | Status |
|---|---|---|
| TASK-000 | Project Skeleton | DONE |
| TASK-001 | MVP PRD and Initial Architecture | IN_PROGRESS |

**Deliverables:**
- Folder structure
- README.md, .env.example
- docs/PRD.md — product requirements
- docs/ARCHITECTURE.md — system design
- docs/ROADMAP.md — this file
- docs/TASKS.md — task tracking
- docs/MEMORY_SYSTEM.md — memory design (pending)
- docs/CHARACTER_SPEC.md — character design (pending)

**Exit Criteria:**
- All docs files have meaningful content
- No runtime code exists yet

---

## Phase 1 — Basic Runtime Skeleton

**Goal:** Establish the running skeleton of both the backend and desktop app. No real AI, no real features — just the infrastructure working end-to-end.

**Status:** NOT STARTED

| Task | Name | Status |
|---|---|---|
| TASK-002 | FastAPI backend skeleton + /health | Pending |
| TASK-003 | Electron desktop shell + IPC setup | Pending |
| TASK-004 | /chat mock endpoint (returns hardcoded response) | Pending |

**Deliverables:**
- `backend/` — FastAPI app that starts and responds to `/health`
- `apps/desktop/` — Electron window that opens and displays a placeholder character image
- `/chat` endpoint that returns a hardcoded mock response (no LLM yet)
- Local HTTP communication confirmed between Desktop and Backend

**Out of Scope:**
- Real LLM calls
- Database
- Character state
- Memory

**Exit Criteria:**
- `uvicorn` starts the backend without errors
- `npm start` opens the Electron window
- Desktop can POST to `/chat` and display the mock response

---

## Phase 2 — Chat and Character

**Goal:** Wire up real LLM calls, define the character, and make the chat experience feel alive.

**Status:** NOT STARTED

| Task | Name | Status |
|---|---|---|
| TASK-005 | LLM adapter (abstract interface + first real provider) | Pending |
| TASK-006 | Character prompt definition | Pending |
| TASK-007 | Message history (in-memory, no DB yet) | Pending |
| TASK-008 | Chat UI (scrollable history, input, send) | Pending |

**Deliverables:**
- LLM adapter with pluggable provider (OpenAI or Anthropic)
- Character system prompt loaded from config
- Chat UI functional: user types, pet responds in character
- Last N messages included in prompt for context

**Out of Scope:**
- Database persistence
- Long-term memory
- Voice
- Character state

**Exit Criteria:**
- User can have a multi-turn conversation with consistent character personality
- LLM provider can be swapped via config change

---

## Phase 3 — Memory and State

**Goal:** Add persistence, long-term memory, character state, and relationship state.

**Status:** NOT STARTED

| Task | Name | Status |
|---|---|---|
| TASK-009 | SQLite schema + ORM setup | Pending |
| TASK-010 | Conversation persistence | Pending |
| TASK-011 | Long-term memory CRUD + prompt injection | Pending |
| TASK-012 | Character state (mood, energy) | Pending |
| TASK-013 | Relationship state (affinity level) | Pending |
| TASK-014 | Daily summary placeholder endpoint | Pending |

**Deliverables:**
- All messages persisted to SQLite
- Long-term memory entries stored, viewable, and injected into prompts
- Character state and relationship state persisted and updated each turn
- `/summary` endpoint returning a placeholder or basic summary

**Out of Scope:**
- Voice
- Task list
- Live2D

**Exit Criteria:**
- Conversations survive app restart
- Pet recalls long-term memories across sessions
- Character state influences response tone

---

## Phase 4 — Voice and Presence

**Goal:** Add voice output (TTS) and placeholder mouth/emotion animation.

**Status:** NOT STARTED

| Task | Name | Status |
|---|---|---|
| TASK-015 | TTS integration (basic voice output) | Pending |
| TASK-016 | Basic mouth animation placeholder | Pending |
| TASK-017 | Simple emotion expression (image swap or overlay) | Pending |

**Deliverables:**
- Pet speaks responses aloud via TTS
- Character image changes based on emotion state (happy, tired, etc.)
- Mouth animation placeholder (static swap, not Live2D)

**Out of Scope:**
- STT (voice input)
- Live2D
- Task list

**Notes:**
- STT may be added as TASK-018 in this phase if TTS is stable
- Live2D remains explicitly out of scope until a future phase

**Exit Criteria:**
- Pet speaks at least one response via TTS
- Emotion image changes visible to user

---

## Phase 5 — Assistant Capabilities

**Goal:** Add task management, project context, and carefully scoped tool execution.

**Status:** NOT STARTED

| Task | Name | Status |
|---|---|---|
| TASK-019 | Basic task list (CRUD via chat) | Pending |
| TASK-020 | Project planning support (conversational) | Pending |
| TASK-021 | Read-only project file context (with safety layer) | Pending |
| TASK-022 | Scheduled reminders | Pending |
| TASK-023 | Tool execution framework (safety-gated) | Pending |

**Deliverables:**
- User can manage tasks through conversation
- Pet can reference project file context (read-only, user-approved paths)
- Scheduled reminders fire at configured times
- Tool execution framework with explicit user approval gate

**Safety Requirements for TASK-021 and TASK-023:**
- No shell command execution without a dedicated safety review
- File access restricted to user-approved directories only
- All tool actions logged and reversible where possible
- User must explicitly enable tool execution capability

**Exit Criteria:**
- User can add, list, and complete tasks through chat
- At least one file context read confirmed working safely
- Tool execution blocked by default until explicitly enabled

---

## Principles Across All Phases

1. **Docs before code.** Each feature must be specified before it is implemented.
2. **Scope discipline.** Features belong to one phase; do not implement Phase N+1 features during Phase N.
3. **Safety first.** Any capability that touches the user's system requires a safety design step before implementation.
4. **Local first.** All user data stays on device unless the user explicitly opts into a cloud feature.
5. **Reversible steps.** Prefer designs that can be undone or corrected without data loss.
