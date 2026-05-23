# dragon-pet-ai 後端

FastAPI backend for the dragon-pet-ai desktop companion.

## Quick Start

### Recommended: one-command dev script (from repo root)

```powershell
.\scripts\dev-start-backend.ps1
```

This activates `.venv`, sets all required env vars for Ollama mode, checks port 8000,
and starts `uvicorn --reload`.  See [docs/LOCAL_DEV_RUNBOOK.md](../docs/LOCAL_DEV_RUNBOOK.md)
for troubleshooting.

### Manual setup

```bash
cd backend

# Create and activate virtual environment (Windows)
python -m venv .venv
.venv\Scripts\Activate.ps1   # PowerShell
# or: .venv\Scripts\activate.bat  (CMD)

# Install dependencies
pip install -r requirements.txt

# Start the development server (mock mode)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

For Ollama mode set env vars before starting:
```powershell
$env:LLM_PROVIDER_NAME = "ollama"
$env:LLM_MODEL = "qwen3:8b"
$env:LLM_PROVIDER_ENABLED = "true"
$env:LLM_CHAT_ENABLED = "true"
$env:LLM_LOCAL_CHAT_TIMEOUT_SECONDS = "90"
$env:PYTHONIOENCODING = "utf-8"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

On macOS / Linux, activate with:
```bash
source .venv/bin/activate
```

## Local LLM Mode (Ollama)

Ollama runs on the user's local machine and does not require an API key. The Electron renderer does not send data directly to Ollama; it calls the FastAPI backend, and the backend owns provider selection, safety checks, usage metadata, and the localhost Ollama request.

### Preconditions

Install Ollama, pull the recommended local model, and confirm the model exists:

```powershell
ollama pull qwen3:8b
ollama list
```

### Start Ollama Mode

Start Ollama:

```powershell
ollama serve
```

Start the backend with Ollama selected:

```powershell
cd backend
$env:LLM_PROVIDER_ENABLED="true"
$env:LLM_CHAT_ENABLED="true"
$env:LLM_PROVIDER_NAME="ollama"
$env:LLM_MODEL="qwen3:8b"
$env:OLLAMA_BASE_URL="http://localhost:11434"
$env:LLM_LOCAL_CHAT_TIMEOUT_SECONDS="90"
uvicorn app.main:app --reload
```

### /chat Smoke Test

With the backend running in Ollama mode:

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai\backend

$env:PYTHONIOENCODING="utf-8"

python -c "import json, urllib.request; data=json.dumps({'message':'你好！克莉絲蒂娜，請用你的口吻跟我說說話。'}, ensure_ascii=False).encode('utf-8'); req=urllib.request.Request('http://127.0.0.1:8000/chat', data=data, headers={'Content-Type':'application/json; charset=utf-8'}); raw=urllib.request.urlopen(req).read().decode('utf-8'); print(raw)"
```

Expected result:
- HTTP 200.
- Response schema remains `reply / mood / source`.
- `source` is `llm_local`.
- No API key is required or sent.
- The reply is generated locally by `qwen3:8b` and should keep Christina-style wording — 傲嬌語氣例如「哼」、「才不是」、「切」 (tsundere / arrogant tone).

### Release Readiness Smoke Flow

1. Start Ollama with `ollama serve`.
2. Confirm `ollama list` includes `qwen3:8b`.
3. Start the backend with Ollama env vars enabled.
4. PATCH `/provider/settings` to `provider=ollama`, `model=qwen3:8b`, `real_provider_enabled=true`, `llm_chat_enabled=true`, and `fallback_to_mock=false`.
5. POST `/provider/settings/test` to run the lightweight backend local runtime/model check. This does not validate the Christina persona and is not a full `/chat` generation.
6. POST `/chat` to validate generation, persona, `mood`, and `source=llm_local`.
7. Start Electron, run UI Test Connection, then send a chat message.
8. Confirm the UI shows `source: llm_local`, updates mood, and renders the reply.

### Fallback Policy

- Development and smoke tests should use `fallback_to_mock=false`.
- Demo mode may use `fallback_to_mock=true` if a mock fallback is preferred over a visible local provider error.
- If `/chat` returns `source=mock` while `resolved_provider=ollama`, treat it as chat disabled or fallback behavior, not a successful local Ollama response.
- Disable fallback when proving the local model is actually generating replies.

### Troubleshooting

- `ollama` not found: install Ollama and reopen the terminal so it is on PATH.
- `qwen3:8b` not found: run `ollama pull qwen3:8b`, then confirm with `ollama list`.
- Test Connection fails: confirm `ollama serve` is running and `OLLAMA_BASE_URL` is `http://localhost:11434`.
- `/chat` returns `source=mock`: confirm `llm_chat_enabled=true`; if `resolved_provider=ollama`, check whether `fallback_to_mock=true` allowed mock fallback.
- `/chat` returns `source=llm_local_error`: Ollama was selected but local generation failed; check server, model, timeout, and cold-start behavior. Local first responses may take longer while the model loads; increase `LLM_LOCAL_CHAT_TIMEOUT_SECONDS` if your hardware needs more time.
- Reply lacks Christina tone: restart backend so the latest prompt code is loaded.
- Backend uses old settings: stop and restart the backend process after changing env vars or provider settings.
- Provider settings unexpectedly lose `model` or revert `fallback_to_mock`: refresh Provider Settings before saving. The backend preserves omitted fields on partial PATCH, and Test Connection does not persist settings.

Safety constraints:
- Do not add direct Ollama calls to the Electron renderer.
- Do not treat Ollama as an API-key provider.
- Do not change the `/chat` response schema.
- Do not call external providers for Ollama mode.
- Do not add live network-dependent automated tests.

## Endpoints (TASK-003 — 端點清單)

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check — 回傳 `{"status": "ok"}` |
| POST | `/chat` | Chat via service layer; mock by default, Ollama local when provider settings and flags enable it |

| POST | `/memory` | Create an explicit local memory record |
| GET | `/memory` | List active local memory records |
| GET | `/memory/context-preview` | Preview active memory records as context text |
| DELETE | `/memory/{id}` | Deactivate a local memory record |
| GET | `/provider/settings` | Read safe non-secret provider settings and aggregate usage summary |
| PATCH | `/provider/settings` | Update non-secret provider settings only |
| POST | `/provider/settings/key` | Save provider key through secure key storage abstraction; never returns key |
| DELETE | `/provider/settings/key` | Clear provider key through secure key storage abstraction |
| POST | `/provider/settings/test` | Backend Test Connection endpoint; Ollama path performs a lightweight local runtime/model check via backend only |
| GET | `/memory/audit` | Read-only audit inspection — 純安全元資料，不含原始內容 |

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
- `/chat` response schema is always `reply / mood / source` — 記憶內容絕不回傳。
- No `PATCH /config` endpoint. No Electron IPC required.

Supported mock modes: `casual`, `project`, `debug`, `support`, `reminder`.

Response:
```json
{
  "reply": "Got it. I'm listening — 還有什麼想說的嗎？",
  "mood": "focused",
  "source": "mock"
}
```

`source: "mock"` indicates the mock path was used. In Local LLM mode, successful Ollama generation returns `source: "llm_local"`; local provider failure without fallback returns `source: "llm_local_error"`. `/chat` delegates to the backend service layer, supports optional mock modes, stores local conversation history and internal state in SQLite, and keeps the same `reply / mood / source` schema.

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

python -c "import json, urllib.request; data=json.dumps({'message':'你好！克莉絲蒂娜，請用你的口吻跟我說說話。'}, ensure_ascii=False).encode('utf-8'); req=urllib.request.Request('http://127.0.0.1:8000/chat', data=data, headers={'Content-Type':'application/json; charset=utf-8'}); raw=urllib.request.urlopen(req).read().decode('utf-8'); print(raw)"

TASK-076 adds Ollama as a selectable option in Provider Settings. `provider_settings_service.py` introduces `LOCAL_PROVIDERS = {"ollama"}`: local providers return `key_status="not_required"`, are accepted by `PATCH /provider/settings`, resolve to `"ollama"` (not mock) when `real_provider_enabled=True`, and reject API key save/clear operations. `provider_test_connection_service.py` accepts `ollama` in the `_normalize_provider` path, uses `_resolve_model_for_local()` (falls back to `"qwen3:8b"` instead of raising `invalid_model`), and runs `OllamaLocalProvider.generate()` directly — 無 API Key，無外部呼叫, `source="llm_local"`. 15 new backend tests added (6 provider settings, 9 test connection Ollama path).

TASK-040 adds `/chat` internal LLM adapter wiring behind `LLM_CHAT_ENABLED=false` by default. With the flag disabled, `/chat` keeps the existing mock flow and does not call the provider factory. With the flag enabled, `/chat` can use the LLM adapter path. TASK-043 adds mocked-only `/chat` real-provider contract tests for the flag matrix, source behavior, fallback behavior, leakage checks, memory independence, and no-retry behavior. Live provider calls are still not part of automated tests.

TASK-051 adds the safe non-secret Provider Settings API subset. `GET /provider/settings` returns provider/model flags, safe key status, resolved provider status, and aggregate in-memory `usage_summary`. `PATCH /provider/settings` updates only non-secret settings and rejects API key fields with a fixed safe error. TASK-054 wires `POST /provider/settings/key` and `DELETE /provider/settings/key` to secure key storage abstraction; they never return key values. TASK-059 wires `POST /provider/settings/test` as a backend-only Test Connection endpoint; it requires explicit acknowledgement, uses exactly one minimal request, has no mock fallback, and keeps cloud provider tests mocked by default. For Ollama, the endpoint runs a lightweight local `/api/tags` model/runtime check through the backend only; persona and generation are validated by `/chat`.

TASK-052 adds an Electron Provider Settings UI for that safe subset. The UI calls only local backend settings endpoints, displays safe key status and usage counters, and keeps key save/clear/test connection controls disabled.

TASK-053 adds a backend key storage abstraction in `app/services/key_storage_service.py`. TASK-054 wires `POST /provider/settings/key` and `DELETE /provider/settings/key` to that abstraction. The runtime default is a safe unavailable backend; tests use an in-memory fake backend for save/clear/idempotent-clear/replace behavior. No API key is stored in SQLite or a plain config file, and no key is returned to frontend responses. TASK-059 backend validation: 465 passed.

`MemoryInjectionAudit` records injection events when memory-aware chat runs with both `MEMORY_INJECTION_ENABLED=true` and `use_memory=true`. Each audit row stores: selected memory IDs (as a JSON array), selected count, total context chars, feature flag state, and timestamp. Raw memory content is never stored in audit rows.

`GET /memory/audit` (TASK-026) is now implemented. It returns a read-only paginated list of memory injection audit records — safe metadata only (IDs, counts, chars, flag state). Supports `limit` (default 20, max 100) and `offset` (default 0) query params. Results are sorted newest first. Raw memory content, prompt text, and system instructions are never returned. The endpoint does not create rows or modify any data. UI for this endpoint is planned for TASK-027.

## Tests

```bash
cd backend
python -m pytest
```

Latest known full backend result after TASK-102/TASK-103: `586 passed`.

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
   