# Architecture Document

> dragon-pet-ai — Architecture
> Status: LIVING DOCUMENT
> Last Updated: 2026-05-19
> Owner: TASK-001
> LLM Adapter Design: TASK-031 (see docs/LLM_ADAPTER_DESIGN.md)
> Real Provider Config Review: TASK-034R — PASS WITH CHANGES (applied in TASK-034F)

---

## 1. High-Level Architecture

The system is composed of two main processes: a **Desktop UI** (Electron) and a **Backend** (Python FastAPI), communicating over local HTTP. All persistent data is stored in a local SQLite database.

```
┌─────────────────────────────────────────────────────────┐
│                   Desktop App (Electron)                  │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────┐  │
│  │  Character   │   │   Chat UI    │   │ Memory / Audit│ │
│  │   Window     │   │              │   │     UI      │  │
│  └──────┬───────┘   └──────┬───────┘   └──────┬──────┘  │
│         └──────────────────┴──────────────────┘          │
│                             │                             │
│              Local HTTP (localhost only)                  │
└─────────────────────────────┬─────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────┐
│                  Backend API (FastAPI)                      │
│                                                            │
│  routes.py  (thin — validates, gates, delegates)           │
│      │                                                     │
│  chat_service  (orchestrates one chat turn)                │
│      │                                                     │
│  ┌───┴──────────┐   ┌────────────────────────────────┐   │
│  │  LLM Adapter │   │     Other Services              │   │
│  │  (Phase 4)   │   │  memory_service                 │   │
│  │              │   │  prompt_service                 │   │
│  │ MockProvider │   │  memory_audit_service           │   │
│  │  (default)   │   │  character_service              │   │
│  │ RealProvider │   │  relationship_service           │   │
│  │ (future,     │   └────────────────┬────────────────┘   │
│  │  flag-gated) │                    │                     │
│  └──────────────┘   ┌───────────────▼────────────────┐   │
│                      │      Database Layer (SQLite)    │   │
│                      │  messages, memory_entries,      │   │
│                      │  character_state, audit_log...  │   │
│                      └────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Choices

| Layer | Technology | Status |
|---|---|---|
| Desktop UI | Electron | Decided |
| Backend Framework | Python FastAPI | Decided |
| Database | SQLite via SQLModel | Decided |
| LLM Provider | Abstract interface + MockProvider + HTTPRealLLMProvider | Real provider adapter behind flags in TASK-035; mock remains default |
| Character Animation | Static image (PNG/GIF) | MVP; Live2D deferred to Phase 5 |
| Voice Output (TTS) | Not implemented | Deferred to Phase 5 |
| Voice Input (STT) | Not implemented | Deferred to Phase 5 |
| IPC / Transport | Local HTTP (localhost) | Decided |

---

## 3. Module Boundaries

### 3.1 Desktop App (`apps/desktop/`)

**Responsibility:** Render the UI, manage the character window, handle user input, call backend API.

- Character window (static image display)
- Chat input and message list UI
- Memory Management UI (create, list, deactivate, preview)
- Audit Logs UI (safe metadata cards only)
- Memory-aware chat toggle (sends `use_memory` in POST body)
- Communicates with backend via HTTP fetch only — no direct database access
- **Never receives or stores API keys, provider credentials, or raw provider responses.**

### 3.2 Backend API (`backend/`)

**Responsibility:** Route incoming requests, coordinate services, return responses.

- FastAPI entry point (`main.py`)
- Route definitions: `/health`, `/chat`, `/memory`, `/memory/audit`, `/memory/context-preview`
- Request validation (Pydantic / SQLModel models)
- No business logic at this layer — delegates to services

### 3.3 Chat Service

**Responsibility:** Orchestrate a single chat turn.

Steps per turn:
1. Receive user message
2. Load recent conversation history from DB
3. Load long-term memory entries from Memory Service (if memory gate active)
4. Load current character state from Character Service
5. Construct `LLMRequest` (system prompt + memory context + history + user message)
6. Call `get_llm_provider().generate(request)` — returns `LLMResponse`
7. Normalize `LLMResponse` → `ChatResponse` (`reply / mood / source`)
8. Store user message + pet response in DB
9. Update character state (via Character Service)
10. Return response to API

### 3.4 Memory Service

**Responsibility:** Manage long-term memory records.

- CRUD for memory entries
- Approved context builder: type allowlist, confidence filter, sensitive-content regex filter, 5-mem / 1500-char cap
- Returns formatted memory block (via `prompt_service`) for `chat_service` to pass to `LLMRequest`
- No automatic writes — memory is written only on explicit user intent

### 3.5 Character Service

**Responsibility:** Manage character state and relationship state.

- Read/write mood, energy level per turn
- Read/write affinity level, interaction count
- Provide state summary for `LLMRequest.state_context`

### 3.6 Memory Audit Service

**Responsibility:** Record and expose memory injection audit events.

- Creates one `MemoryInjectionAudit` row per injection event
- Stores: selected IDs (JSON), count, total context chars, flag state — never raw content
- `GET /memory/audit`: read-only, paginated, newest-first, safe metadata only

---

## 4. LLM Adapter Layer (Phase 4 — TASK-031 design, TASK-032 skeleton)

> Full design: `docs/LLM_ADAPTER_DESIGN.md`
> Interface skeleton: `backend/app/llm/` (implemented TASK-032)
> Real provider config design: TASK-034 DONE, TASK-034R reviewed, TASK-034F fixes applied
> Real provider adapter implementation: TASK-035 (in progress). `/chat` remains on the existing mock runtime path until runtime smoke validation.

### 4.1 Service Boundaries

```
routes.py       thin — never knows which provider is active
    │
    ▼
chat_service    orchestrates: builds LLMRequest, calls adapter, normalizes response
    │
    ▼
get_llm_provider()
    ├── MockProvider   ← DEFAULT — always available, no key, no network call
    └── RealProvider   ← DISABLED BY DEFAULT — requires LLM_PROVIDER_ENABLED=true
                          + valid LLM_PROVIDER_NAME + non-empty LLM_API_KEY
```

### 4.2 Provider Factory Safety Rules

The factory (`get_llm_provider()`) follows this evaluation order:

1. If `LLM_PROVIDER_ENABLED` is not `true` → return `MockProvider`
2. If `LLM_PROVIDER_NAME` is `mock`, empty, or unset → return `MockProvider`
3. If `LLM_PROVIDER_NAME` is unknown → return `MockProvider` + emit non-sensitive warning (never crash)
4. If `LLM_API_KEY` is missing or empty → return `MockProvider` + emit non-sensitive warning
5. Otherwise → return `RealProvider` for the named provider

### 4.3 Real Provider Config — Backend Only

| Constraint | Rule |
|---|---|
| API key source | Backend environment variable only (`LLM_API_KEY` or provider alias) |
| Frontend access | **Never** — API key must not appear in renderer.js, index.html, or any client-side code |
| Log output | **Never** — API key must not appear in any log line, including warnings and crash traces |
| Database | **Never** — API key must not be written to SQLite or any persistent store |
| HTTP responses | **Never** — API key must not appear in any response body, error body, or header |
| Provider repr / str | Must not expose API key (Python `__repr__` and `__str__` must redact key) |
| Non-2xx response bodies | Treated as **opaque** — do not parse, log, store, or return raw bodies |
| Retries | **No automatic retries in Phase 4** — at most one real provider call per `/chat` turn |

### 4.4 Canonical Safe Fallback Text

When a real provider is unavailable and a user-facing message is required:

```
"I cannot reach the real language model right now, so I will continue in safe mock mode."
```

This string is used in: fallback-to-mock responses, real provider error responses (when fallback disabled), and as the `reply` field in `ChatResponse`. It must not contain provider names, error codes, stack traces, or API key fragments.

### 4.5 Provider Visibility (Observability without Secrets)

TASK-035 exposes resolved provider state through a non-sensitive factory helper without exposing secrets. Acceptable MVP options:

- Startup `INFO` log: `provider=mock reason=flag_disabled` (no key value)
- OR `/health` response non-sensitive field: `"llm_provider": "mock"`

This requirement exists so that fallback-to-mock does not silently hide misconfiguration.

### 4.6 Logging Forbidden Fields

The following must **never** appear in any log output:

- API key value
- Full prompt text
- Approved memory context text
- System / developer prompt text
- Raw provider request body
- Raw provider response body
- Non-2xx provider response body (any part)
- `user_message` content
- `conversation_history` content
- `state_context` content
- `LLMResponse.text` (may contain sensitive user information)
- Sensitive user input of any kind

Only safe diagnostic fields are permitted in logs: provider name (not key), error category, HTTP status class (2xx / 4xx / 5xx), elapsed time.

### 4.7 Relationship to Memory Gate

The LLM provider flag is completely independent of the memory injection gate.

| `LLM_PROVIDER_ENABLED` | `MEMORY_INJECTION_ENABLED` | `use_memory` | Result |
|---|---|---|---|
| `false` | `false` | `false` | MockProvider, no memory injection |
| `false` | `true` | `true` | MockProvider, memory context built/audited but passed to mock (unused) |
| `true` | `false` | `false` | RealProvider, no memory injection |
| `true` | `true` | `true` | RealProvider, memory context built, audited, and passed to provider |

In all cases, `/chat` response schema remains `reply / mood / source`.

### 4.8 Provider Observability vs Memory Audit

`MemoryInjectionAudit` is memory-scoped. It must not store:
- Raw prompts
- Raw provider responses
- `llm_provider_used` field

Provider observability (which provider ran, whether fallback occurred) belongs in a separate non-sensitive diagnostics or health/status mechanism — not in the memory audit table.

---

## 5. Data Flow

### 5.1 Memory-Aware Chat Flow (Implemented — Phase 3)

```
User message + use_memory=true
  -> POST /chat
  -> check MEMORY_INJECTION_ENABLED AND use_memory          [two-layer gate]
  -> if both true:
       get_or_create_default_conversation()
       build_approved_memory_context_records()              [type allowlist, confidence filter,
                                                             sensitive-content filter, 5-mem / 1500-char cap]
       format_approved_memory_context()                     [delimited reference block]
       create_memory_injection_audit()                      [stores IDs, count, chars — no raw content]
  -> get_llm_provider().generate(LLMRequest)                [provider selection in TASK-035; /chat wiring deferred]
  -> normalize LLMResponse -> ChatResponse
  -> store_chat_turn()
  -> update_state_after_chat_turn()
  -> return { reply, mood, source }                         [memory content never returned]
```

### 5.2 Audit Inspection Flow (Implemented — Phase 3)

```
Desktop Audit Logs UI
  -> GET /memory/audit?limit=N&offset=M
  -> memory_audit_service.list_memory_injection_audits_paginated()
  -> DB query -> MemoryInjectionAudit rows (safe metadata only)
  -> return { items, count, limit, offset }
     items contain: id, created_at, conversation_id, selected_memory_ids,
                    selected_count, total_context_chars, feature_flag_enabled, exclusion_summary
     [raw memory content never returned]
```

---

## 6. Memory-Aware Chat Toggle Design (Implemented — TASK-023)

### 6.1 Two-Layer Safety Model

Memory-aware chat requires **both** conditions to be true:

1. **Backend global gate** — `MEMORY_INJECTION_ENABLED=true` (set before backend startup)
2. **Frontend per-request toggle** — `use_memory=true` in the POST `/chat` request body

| `MEMORY_INJECTION_ENABLED` | `use_memory` | Behavior |
|---|---|---|
| `false` | any | No memory injection |
| `true` | `false` | No memory injection |
| `true` | `true` | Approved memory context may be used |

### 6.2 Current `/chat` Request Schema

```json
{
  "message": "hello",
  "mode": "casual",
  "use_memory": true
}
```

- `use_memory` defaults to `false` if absent
- `/chat` response schema remains `reply / mood / source` regardless of flag or toggle state
- Memory content is never returned in the response body

---

## 7. Safety Boundaries

These boundaries apply to all current and future work and must not be weakened without explicit safety design review:

| Boundary | Rule |
|---|---|
| Shell commands | System cannot execute any shell or terminal commands |
| File modification | System cannot modify any user files |
| File reading | System cannot read user files (deferred to Phase 5 with safety layer) |
| External messaging | System cannot send emails, Slack messages, or any external messages |
| Financial actions | System cannot perform any trading, purchasing, or financial operations |
| Memory writes | Memory entries written only on explicit user intent or after user confirmation |
| Sensitive data | Passwords, credentials must not be stored automatically |
| LLM API calls | The ONLY external network call allowed is to the configured LLM API endpoint (Phase 4+) |
| External sync | No cloud sync, no remote database, no telemetry |
| API key exposure | Key never in frontend, logs, DB, responses, repr/str, access logs, audit rows |
| Tool execution | No tool execution from LLM output in Phase 4 |
| Autonomous action | LLM output displayed to user only — no side effects |
| Automatic memory | LLM responses must not trigger automatic memory writes |

---

## 8. Future Extension Points

| Feature | Extension Point | Phase |
|---|---|---|
| Real LLM provider | LLM Adapter → RealProvider | Phase 4 TASK-035 |
| TTS (voice output) | Character Service → audio output hook | Phase 5 |
| STT (voice input) | Desktop App → audio capture → `/chat` | Phase 5 |
| Live2D animation | Character window → animation controller | Phase 5 |
| Project file reading | Tool Layer → read-only file context | Phase 5; safety layer required |
| Calendar integration | Tool Layer → calendar API adapter | Phase 5 |
| Scheduled reminders | Task Service → scheduler | Phase 5 |
| Embedding-based memory | Memory Service → vector store | Phase 4+ after LLM stable |
| WebSocket transport | Replace HTTP polling | Phase 2 if needed |
