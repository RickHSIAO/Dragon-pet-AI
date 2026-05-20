# dragon-pet-ai — Backend

FastAPI backend for the dragon-pet-ai desktop companion.

## Quick Start

```bash
cd backend

# Create and activate virtual environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
uvicorn app.main:app --reload --port 8000
```

On macOS / Linux, activate with:
```bash
source .venv/bin/activate
```

## Endpoints (TASK-003 — skeleton only)

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check — returns `{"status": "ok"}` |
| POST | `/chat` | Mock chat via service layer — returns a character-style reply |

| POST | `/memory` | Create an explicit local memory record |
| GET | `/memory` | List active local memory records |
| GET | `/memory/context-preview` | Preview active memory records as context text |
| DELETE | `/memory/{id}` | Deactivate a local memory record |
| GET | `/provider/settings` | Read safe non-secret provider settings and aggregate usage summary |
| PATCH | `/provider/settings` | Update non-secret provider settings only |
| POST | `/provider/settings/key` | Save provider key through secure key storage abstraction; never returns key |
| DELETE | `/provider/settings/key` | Clear provider key through secure key storage abstraction |
| POST | `/provider/settings/test` | Disabled placeholder; no live provider call |
| GET | `/memory/audit` | Read-only audit inspection — safe metadata only, no raw content |

### POST /chat

Request body:
```json
{ "message": "Hello!" }
```

Optional mock mode:
```json
{ "message": "Help me debug this", "mode": "debug" }
```

Memory-aware chat toggle (two-layer gate, TASK-023):
```json
{ "message": "hello", "use_memory": true }
```

- `use_memory` defaults to `false`. Old callers that omit it continue to work unchanged.
- Both `use_memory=true` AND `MEMORY_INJECTION_ENABLED=true` (env var, set before startup) must be true for `/chat` to use approved memory context.
- `/chat` response schema is always `reply / mood / source` — memory content is never returned.
- No `PATCH /config` endpoint. No Electron IPC required.

Supported mock modes: `casual`, `project`, `debug`, `support`, `reminder`.

Response:
```json
{
  "reply": "Got it. I'm listening — what else is on your mind?",
  "mood": "focused",
  "source": "mock"
}
```

`source: "mock"` indicates no real LLM is connected yet. `/chat` currently delegates to the backend service layer, supports optional mock modes, stores local conversation history and internal state in SQLite, and remains mock-only. Mock chat can read internal local state for lightweight phrasing, but state is not returned to the frontend.

## Memory Skeleton

The backend now includes a local SQLite `Memory` table skeleton and basic memory service helpers for future long-term memory work. Memory is not used by `/chat` yet, there is no automatic memory extraction, and no vector database is connected.

### Manual Memory API

The backend now includes manual memory API endpoints. `POST /memory` creates an explicit local memory record, `GET /memory` lists active memory records, `GET /memory/context-preview` previews active manual memories as context text, and `DELETE /memory/{id}` deactivates a memory record without deleting the row. Memory remains local SQLite only, `/chat` still does not use memory, there is no automatic memory extraction, and no vector database is connected.

Example:
```json
{
  "memory_type": "user_preference",
  "content": "Likes concise answers",
  "importance": 50
}
```

`GET /memory/context-preview` returns deterministic preview text ordered by importance descending, then id ascending. It does not use semantic retrieval and does not update `last_used_at`.

The Electron desktop app has a minimal Memory Management placeholder that can create, list, deactivate, and preview local memories through these manual endpoints. `/chat` still does not use memory, and there is no semantic retrieval or automatic memory extraction.

Manual memory injection is documented as a future design only. It is not implemented in runtime yet; `/chat` still does not use memory, and manual memory must remain inspectable and controllable before any future chat integration.

The memory injection design was safety-reviewed. Future runtime wiring must use `MEMORY_INJECTION_ENABLED` with default `False`; memory-aware chat is not enabled yet.

The backend now has an approved memory context builder and prompt formatter for future chat integration. It applies a memory type allowlist, confidence filtering, sensitive-content filtering, and 5-memory / 1500-character caps. The formatter uses delimiters and a reference-only safety instruction. This is not connected to `/chat` yet, and there is still no semantic retrieval, vector database, or real AI provider.

The LLM adapter exists under `app/llm` with provider-agnostic request/response types, an abstract provider interface, `MockLLMProvider`, and `HTTPRealLLMProvider` behind disabled-by-default flags. API keys are read only from backend environment variables when a real provider is explicitly enabled. `/chat` is gated separately by `LLM_CHAT_ENABLED=false` by default and keeps the `reply / mood / source` response schema.

Mock provider compatibility tests cover supported chat modes, optional memory/state/history context handling, response normalization to the existing `reply / mood / source` shape, and factory behavior. Real provider tests use mocked HTTP only and verify the Anthropic Messages request contract, text-block parsing, internal usage handling, redaction, no retries, timeout handling, safe error mapping, and opaque non-2xx response bodies.

Real provider config design (TASK-034), safety review (TASK-034R), and review fixes (TASK-034F) are complete. TASK-035 adds real provider selection behind `LLM_PROVIDER_ENABLED=false` by default. Unknown providers and missing keys fall back safely without exposing secrets. API keys must never appear in logs, SQLite, audit rows, API responses, provider repr/str, or the Electron frontend. No automatic retries are permitted in Phase 4. Non-2xx provider response bodies are opaque. Fallback responses must not claim `llm_real`.

TASK-040 adds `/chat` internal LLM adapter wiring behind `LLM_CHAT_ENABLED=false` by default. With the flag disabled, `/chat` keeps the existing mock flow and does not call the provider factory. With the flag enabled, `/chat` can use the LLM adapter path. TASK-043 adds mocked-only `/chat` real-provider contract tests for the flag matrix, source behavior, fallback behavior, leakage checks, memory independence, and no-retry behavior. Live provider calls are still not part of automated tests.

TASK-051 adds the safe non-secret Provider Settings API subset. `GET /provider/settings` returns provider/model flags, safe key status, resolved provider status, and aggregate in-memory `usage_summary`. `PATCH /provider/settings` updates only non-secret settings and rejects API key fields with a fixed safe error. TASK-054 wires `POST /provider/settings/key` and `DELETE /provider/settings/key` to secure key storage abstraction; they never return key values. `POST /provider/settings/test` remains a `501 not_implemented` placeholder and does not call external providers.

TASK-052 adds an Electron Provider Settings UI for that safe subset. The UI calls only local backend settings endpoints, displays safe key status and usage counters, and keeps key save/clear/test connection controls disabled.

TASK-053 adds a backend key storage abstraction in `app/services/key_storage_service.py`. TASK-054 wires `POST /provider/settings/key` and `DELETE /provider/settings/key` to that abstraction. The runtime default is a safe unavailable backend; tests use an in-memory fake backend for save/clear/idempotent-clear/replace behavior. No API key is stored in SQLite or a plain config file, no key is returned to frontend responses, and `POST /provider/settings/test` remains disabled. Latest backend validation: 449 passed.

`MemoryInjectionAudit` records injection events when memory-aware chat runs with both `MEMORY_INJECTION_ENABLED=true` and `use_memory=true`. Each audit row stores: selected memory IDs (as a JSON array), selected count, total context chars, feature flag state, and timestamp. Raw memory content is never stored in audit rows.

`GET /memory/audit` (TASK-026) is now implemented. It returns a read-only paginated list of memory injection audit records — safe metadata only (IDs, counts, chars, flag state). Supports `limit` (default 20, max 100) and `offset` (default 0) query params. Results are sorted newest first. Raw memory content, prompt text, and system instructions are never returned. The endpoint does not create rows or modify any data. UI for this endpoint is planned for TASK-027.

## Tests

```bash
cd backend
python -m pytest
```

## Current Limitations (TASK-003)

- `/chat` returns a service-generated mock reply — no real AI model is connected.
- Backend creates a local SQLite database and stores conversation history.
- Backend also has local `character_state` and `relationship_state` tables for internal MVP state.
- Backend has a local SQLite `memory` table skeleton for future memory records.
- Manual memory API endpoints can create, list, and deactivate explicit memory records.
- `/memory/context-preview` previews active memories as context text without connecting them to `/chat`.
- SQLite database files are ignored by git.
- Conversation history and state are local SQLite only.
- Memory records are local SQLite only and are not read by `/chat` yet.
- State can lightly affect mock phrasing, but this is not long-term memory retrieval or summary.
- No vector database and no automatic memory extraction.
- Character and relationship state are local counters/fields only; they do not mean the character is conscious and do not trigger autonomous actions.
- No voice (TTS/STT), no Live2D, no shell execution, no file access.

## Project Structure

```
backend/
  app/
    __init__.py
    main.py           # FastAPI app entry point
    api/
      __init__.py
      routes.py       # GET /health, POST /chat
    services/
      __init__.py
      chat_service.py
      character_service.py
      conversation_service.py
      prompt_service.py
      state_service.py
      memory_service.py
    db/
      __init__.py
      database.py     # SQLModel engine + init_db
      models.py       # Conversation, Message, CharacterState, RelationshipState, Memory
    schemas/
      __init__.py
      chat.py         # ChatRequest / ChatResponse Pydantic models
  requirements.txt
  README.md
```
