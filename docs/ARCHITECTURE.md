# Architecture Document

> dragon-pet-ai — Initial Architecture
> Status: DRAFT
> Last Updated: 2026-05-19
> Owner: TASK-001

---

## 1. High-Level Architecture

The system is composed of two main processes: a **Desktop UI** (Electron) and a **Backend** (Python FastAPI), communicating over local HTTP. All persistent data is stored in a local SQLite database.

```
┌─────────────────────────────────────────────────────────┐
│                     Desktop App (Electron)               │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────┐ │
│  │  Character   │   │   Chat UI    │   │  Task Panel │ │
│  │   Window     │   │              │   │             │ │
│  └──────┬───────┘   └──────┬───────┘   └──────┬──────┘ │
│         └──────────────────┴──────────────────┘         │
│                             │                            │
│              IPC / Local HTTP (localhost)                │
└─────────────────────────────┬───────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────┐
│                  Backend API (FastAPI)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Chat Service│  │Memory Service│  │Character Service│  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘  │
│         │                │                   │           │
│  ┌──────▼──────┐  ┌──────▼──────────────────▼────────┐  │
│  │ LLM Adapter │  │         Database Layer             │  │
│  │(placeholder)│  │           (SQLite)                 │  │
│  └─────────────┘  └───────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │              Task Service                          │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

---

## 2. Initial Technology Choices

| Layer | Technology | Decision Status |
|---|---|---|
| Desktop UI | Electron | Decided |
| Backend Framework | Python FastAPI | Decided |
| Database | SQLite | Decided |
| ORM | SQLAlchemy or SQLModel | TBD — final choice in TASK-002 |
| LLM Provider | Abstract interface (adapter pattern) | Interface defined; real provider in TASK-002+ |
| Character Animation | Static image (PNG/GIF) | MVP only; Live2D deferred to Phase 4 |
| Voice Output (TTS) | Not implemented | Deferred to Phase 4 |
| Voice Input (STT) | Not implemented | Deferred to Phase 4 |
| IPC / Transport | Local HTTP (localhost) | Decided for MVP; may add WebSocket in Phase 2 |
| Config Format | YAML or TOML | TBD |

### Rationale

- **Electron**: Cross-platform desktop, mature ecosystem, supports always-on-top windows.
- **FastAPI**: Async Python, fast to prototype, clean OpenAPI docs, good for ML/LLM integration later.
- **SQLite**: Zero-config, local-first, single-file database — ideal for a personal desktop app.
- **Adapter pattern for LLM**: Decouples the rest of the system from any specific LLM provider, making it easy to swap OpenAI for Anthropic or a local model.

---

## 3. Module Boundaries

### 3.1 Desktop App (`apps/desktop/`)
**Responsibility:** Render the UI, manage the character window, handle user input, call backend API.

- Character window (static image display)
- Chat input and message list UI
- Task panel UI
- Local settings panel (window position, opacity, etc.)
- Communicates with backend via HTTP only — no direct database access

### 3.2 Backend API (`backend/`)
**Responsibility:** Route incoming requests, coordinate services, return responses.

- FastAPI entry point
- Route definitions: `/health`, `/chat`, `/memory`, `/tasks`, `/character`, `/summary`
- Request validation (Pydantic models)
- No business logic at this layer — delegates to services

### 3.3 Chat Service
**Responsibility:** Orchestrate a single chat turn.

Steps per turn:
1. Receive user message
2. Load recent conversation history from DB
3. Load long-term memory entries from Memory Service
4. Load current character state from Character Service
5. Construct prompt (system prompt + memory + history + user message)
6. Call LLM Adapter (returns response)
7. Store user message + pet response in DB
8. Update character state (via Character Service)
9. Return response to API

### 3.4 Memory Service
**Responsibility:** Manage long-term memory records.

- CRUD for memory entries (key facts about the user)
- Memory injection: returns formatted memory block for prompt construction
- No automatic writes — memory is written only on explicit user intent or confirmed extraction
- Future: embedding-based retrieval (Phase 3+)

### 3.5 Character Service
**Responsibility:** Manage character state and relationship state.

- Read/write character state (mood, energy level)
- Read/write relationship state (affinity level, interaction count)
- Provide state summary for prompt injection
- Apply state update rules after each interaction

### 3.6 Task Service
**Responsibility:** Manage user's task list.

- CRUD for tasks (title, status, created_at, completed_at)
- Natural language task parsing delegated to Chat Service / LLM
- Returns task list as structured data for UI and chat context

### 3.7 Database Layer
**Responsibility:** Persist all structured data.

Tables (initial schema, defined in TASK-002):
- `messages` — conversation history
- `memory_entries` — long-term memory facts
- `character_state` — mood, energy, last updated
- `relationship_state` — affinity level, interaction count
- `tasks` — task list items
- `sessions` — session metadata (start time, summary placeholder)

### 3.8 Future Tool Layer (Phase 5+)
**Responsibility:** Allow the pet to execute approved actions on behalf of the user.

- NOT implemented in MVP
- Will require explicit safety design before implementation
- Examples: read project files (read-only), trigger scheduled reminders
- Will NOT include: shell execution, file writes, external API calls without user approval

---

## 4. Data Flow

### Standard Chat Turn

```
User types message in Desktop UI
        │
        ▼
Desktop App sends POST /chat { message, session_id }
        │
        ▼
Backend API → Chat Service
        │
        ├─► Memory Service.get_memory_entries()
        │       └─► DB query → memory facts
        │
        ├─► Character Service.get_state()
        │       └─► DB query → mood, energy, affinity
        │
        ├─► DB query → recent N messages (conversation history)
        │
        ├─► Prompt Construction
        │       system_prompt + memory + character_state + history + user_message
        │
        ▼
LLM Adapter.complete(prompt)
        │   (placeholder in Phase 1; real call in Phase 2)
        │
        ▼
Chat Service receives LLM response
        │
        ├─► DB write → store user message + pet response
        │
        ├─► Character Service.update_state(response_context)
        │       └─► DB write → updated mood, energy, affinity
        │
        ▼
Backend API returns { response, character_state }
        │
        ▼
Desktop App renders response in chat UI
Updates character expression (if state changed)
```

---

## 5. Safety Boundaries

These boundaries apply to MVP and must not be removed without explicit safety design review:

| Boundary | Rule |
|---|---|
| Shell commands | MVP CANNOT execute any shell or terminal commands |
| File modification | MVP CANNOT modify any user files |
| File reading | MVP CANNOT read user files (deferred to Phase 5 with safety layer) |
| External messaging | MVP CANNOT send emails, Slack messages, or any external messages |
| Financial actions | MVP CANNOT perform any trading, purchasing, or financial operations |
| Memory writes | Memory entries are written ONLY on explicit user intent or after user confirmation |
| Sensitive data | Personal sensitive data (passwords, credentials) must NOT be stored automatically |
| LLM API calls | The ONLY external network call allowed in MVP is to the configured LLM API endpoint |
| External sync | No cloud sync, no remote database, no telemetry |

---

## 6. Future Extension Points

The following are designed as extension points but NOT implemented in MVP:

| Feature | Extension Point | Notes |
|---|---|---|
| TTS (voice output) | Character Service → audio output hook | Phase 4 |
| STT (voice input) | Desktop App → audio capture → `/chat` | Phase 4 |
| Live2D animation | Character window → animation controller | Phase 4; replaces static image |
| Project file reading | Tool Layer → read-only file context | Phase 5; requires safety layer |
| Calendar integration | Tool Layer → calendar API adapter | Phase 5 |
| Scheduled reminders | Task Service → scheduler | Phase 5 |
| Local tool execution | Tool Layer → approved tool registry | Phase 5; safety design required first |
| Embedding-based memory | Memory Service → vector store | Phase 3+; replaces exact-match lookup |
| Multi-session summary | Chat Service → summary generator | Phase 3 |
| WebSocket transport | Replace HTTP polling with WebSocket | Phase 2 if needed for real-time feel |
