# Portfolio Demo Script — Dragon Pet AI

> Task: TASK-066D
> Audience: Interviewers, portfolio reviewers, personal reference
> Last Updated: 2026-05-21
> Status: STABLE REFERENCE

---

## Purpose

This document is the single reference for:

- **Job interviews** — talking through design decisions, safety engineering, and test strategy
- **Portfolio / GitHub showcases** — explaining what the project is and what was deliberately left out
- **Demo recordings** — a step-by-step script you can follow on screen
- **Personal architecture review** — a quick refresher on what is built and why

---

## Project One-liner

> Dragon Pet AI is a local-first Electron + FastAPI desktop companion prototype with a manual memory system, memory audit logs, BYOK provider settings, secure key storage abstraction, a safety-reviewed Test Connection endpoint, in-memory usage metering, and a 470-test mocked backend suite — with no live external provider call made and no real API key used.

---

## 30-Second Pitch

Dragon Pet AI is a personal desktop companion app built with an Electron frontend and a FastAPI backend. The app is designed around a local-first, privacy-first model: all data stays on device, and the user brings their own LLM provider API key rather than sharing a developer-owned key.

On the backend I built a layered service architecture — memory management, memory audit logging, usage metering, provider settings, secure key storage abstraction, and a Test Connection endpoint that was independently safety-reviewed by an AI model acting as a second reviewer. The key storage design explicitly prohibits writing API keys to plain SQLite or log files, and the Test Connection endpoint requires a per-click explicit cost acknowledgement before sending any request.

The full test suite has 470 tests, all mocked — no live provider call has been made, and no real API key has been used anywhere in development. The system is intentionally conservative: every capability that could expose user data or incur cost has a feature flag, a safety design document, and mocked tests before the implementation is enabled.

---

## 2-Minute Demo Script

Follow these steps in order. The script assumes the backend is running at `localhost:8000` and the Electron window is open.

### Step 1 — Open the Electron desktop app

```powershell
cd apps\desktop
npm start
```

Point out: the window opens, connects to the local FastAPI backend, and shows a health status. Everything is local — no cloud service is contacted.

### Step 2 — Show chat works (mock mode)

Type a message in the chat input and press Send. The response comes back from the mock provider with `source: mock`. Explain:

> The chat is working end-to-end through the full backend service stack — request schema validation, the chat service, the LLM adapter layer, and the response schema — even though the LLM is currently mocked. Switching to a real provider only requires enabling two environment variables and providing a key.

### Step 3 — Show the Memory section

Open the Memory section. Create a memory entry (e.g., "User prefers concise responses"). Show that:

- Memory entries are stored in SQLite locally
- Entries can be listed, previewed as context, and deactivated
- The Memory Context Preview shows exactly how memory would be formatted into a prompt
- Memory injection into `/chat` is behind a two-layer safety gate: a backend feature flag (`MEMORY_INJECTION_ENABLED`) and a per-request toggle (`use_memory`)

> This design means memory can never be accidentally injected — both the operator and the user must opt in separately.

### Step 4 — Show Audit Logs

Open the Audit Logs section. Each row shows:

- `id`, `created_at`, `selected_memory_ids`, `selected_count`, `total_context_chars`, `feature_flag_enabled`

Explain what is **not** stored:

> Audit rows never contain raw memory content, prompt text, or any user message. The audit design was reviewed to ensure it surfaces enough to be useful for debugging without becoming a privacy leak.

### Step 5 — Show Provider Settings

Open the Provider Settings section. Walk through:

- Provider selector (mock / anthropic / openai)
- Model field
- Enable Real Provider toggle
- Key status display — shows one of six safe status values; no key fragment is ever shown

Explain the layout improvements from TASK-063: the section is vertically scrollable, form fields are readable, and buttons wrap correctly in narrow windows.

### Step 6 — Show Usage Summary

Point to the Usage Summary display within Provider Settings. Explain:

- 14 fields tracked per provider interaction
- Aggregate only — no raw prompt text, no raw response, no API key
- Ephemeral in-memory for the current session (resets on restart by design)

### Step 7 — Explain Save Key / Clear Key safety

Point to the Save Key button (currently disabled because key storage returns unavailable). Explain:

> When the OS keychain backend is wired in, Save Key will POST the key to the backend, which passes it to the key storage abstraction. The key is write-only — it is never echoed back, never returned in any response body, never logged, and never stored in localStorage or sessionStorage. Clear Key shows a confirmation dialog before sending the DELETE request. The input field clears after every Save Key attempt so the key is not left in the DOM.

### Step 8 — Explain Test Connection safety

Point to the Test Connection button (currently disabled because `key_status: not_configured`). Explain:

> When enabled, Test Connection requires the user to confirm a cost acknowledgement dialog on every click — not once, but every time. The dialog covers four disclosures: this sends a real request, charges may apply, no retries will be made, and the user should only proceed if they have confirmed their key and provider settings. The backend sends exactly one minimal request — sixteen tokens, no memory, no tools, no streaming, no conversation history. If the provider returns an unknown error, it collapses to a safe generic message; the raw error string is never returned. This design was reviewed by a second AI model (Opus) and passed with no critical issues.

### Step 9 — Confirm no live provider call yet

Explicitly state:

> No live external provider call has been made in this project. No real API key has been used anywhere — in tests, in dev, or in demos. The Test Connection button is correctly disabled in the current runtime because the key storage backend is `UnavailableProviderKeyStorageBackend` by default, which always returns 503. This is intentional — the safety gate is working.

### Step 10 — Show test coverage

Open a terminal and run:

```powershell
cd backend
python -m pytest
```

Point to `470 passed`. Explain:

- Tests cover the full backend: memory service, audit service, usage meter, provider settings API, key endpoints, and Test Connection
- All tests use mocked runners and in-memory key storage — no external HTTP, no real key
- Five hardening tests were added after an independent safety review specifically to cover: provider-disabled branch with a configured key, invalid-model 400, unknown error string collapse, extra field rejection, and safe-message category sweep

---

## Architecture Talking Points

```
User
  └── Electron renderer (HTML / CSS / JS)
        └── IPC / localhost HTTP → FastAPI backend (port 8000)
              ├── api/routes.py            — all HTTP endpoints
              ├── services/
              │     ├── chat_service               — /chat routing
              │     ├── memory_service             — memory CRUD, context builder
              │     ├── memory_audit_service       — audit row creation and inspection
              │     ├── usage_meter_service        — token/cost tracking (in-memory)
              │     ├── provider_settings_service  — non-secret settings persistence
              │     ├── key_storage_service        — secure key storage abstraction
              │     └── provider_test_connection_service — Test Connection logic
              ├── providers/
              │     ├── mock_provider              — always-on fallback
              │     ├── anthropic_provider         — behind LLM_PROVIDER_ENABLED
              │     └── provider_factory           — selects provider by config
              ├── schemas/                         — Pydantic request/response models
              └── db/                              — SQLModel / SQLite engine
```

**Key design choices worth discussing:**

- **Adapter pattern for LLM providers** — the `ProviderInterface` abstraction means adding a new provider (OpenAI, Gemini) requires only a new adapter, not changes to the service layer or routes.
- **Feature flags everywhere** — `LLM_PROVIDER_ENABLED`, `LLM_CHAT_ENABLED`, `MEMORY_INJECTION_ENABLED` default to `false`. No live feature activates without an explicit opt-in.
- **Write-only key handling** — `POST /provider/settings/key` accepts the key, passes it to storage, and forgets it. No endpoint returns the key or any fragment of it.
- **Schema stability** — `/chat` response schema (`reply / mood / source`) has not changed across the entire Phase 4 build. Adding memory, usage metering, and provider settings did not touch the schema.
- **Test isolation** — `InMemoryKeyStorageBackend` and `FakeProviderTestRunner` are injected via the dependency-inversion pattern for tests. The real database and real provider are never touched by the test suite.
- **Independent safety review** — the Test Connection backend implementation was reviewed by a separate, more capable model (Opus) before the UI was enabled. The review verdict was PASS, and five additional hardening tests were added based on the review recommendations.

---

## Completed Features

| Feature | Notes |
|---|---|
| `GET /health` | Liveness check |
| `POST /chat` | Mock character response; LLM adapter behind `LLM_CHAT_ENABLED=false` |
| Memory CRUD (`POST/GET/DELETE /memory`) | SQLite persistence |
| `GET /memory/context-preview` | Formats approved memories as context text without triggering injection |
| Approved memory context builder | Type allowlist, confidence filter, sensitive-content filter, 5-memory / 1500-char cap |
| Memory-aware chat toggle | Two-layer gate: `MEMORY_INJECTION_ENABLED` + per-request `use_memory` |
| `GET /memory/audit` | Read-only, paginated, safe metadata only — no raw memory content |
| Audit Logs UI | Desktop section showing injection events |
| In-memory usage meter | 14 fields, token estimation, privacy boundaries |
| `GET/PATCH /provider/settings` | Non-secret settings (provider, model, real_provider_enabled) |
| `GET /provider/settings/key/status` | Six safe status values; no key fragment |
| `POST /provider/settings/key` | Write-only key save to storage abstraction |
| `DELETE /provider/settings/key` | Key clear with confirmation |
| `POST /provider/settings/test` | Exactly-one minimal request; `explicit_cost_ack` required; Opus safety review PASS |
| Secure key storage abstraction | `UnavailableBackend` (runtime), `InMemoryBackend` (tests); OS keychain designed |
| Provider Settings UI | Provider/model select, Save Key, Clear Key, Test Connection, key status, usage summary |
| Test Connection UI | Cost ack confirm dialog; safe field rendering; no auto-run |
| Provider test connection hardening tests | 5 tests: provider_disabled, invalid_model, unknown error, extra field, safe_message sweep |
| pytest: 470 passed | Full backend suite; mocked; no external HTTP; no real key |

---

## Safety / BYOK Explanation

*Use this section to explain the key design to a non-technical interviewer.*

**What is BYOK?**
BYOK stands for Bring Your Own Key. Instead of the app shipping with a developer-owned API key — which would mean the developer pays for every user's AI usage and the key could be extracted from the app — the user provides their own key from their own provider account. The user pays provider costs directly, and the developer never has access to the user's key.

**How is the key protected?**
- The key is sent from the Electron frontend to the local backend only — never to any external service.
- The backend accepts the key, passes it to the key storage abstraction, and does not keep it in memory beyond the request.
- No endpoint returns the key or any part of it.
- The key is never written to the SQLite database, never written to log files, never included in audit rows, never stored in Electron `localStorage` or `sessionStorage`, and never included in any response field — including error responses.
- The provider's `__repr__` and `__str__` methods redact any secret fields, so even accidental logging cannot leak the key.

**How does the runtime key storage work?**
By default the runtime uses `UnavailableProviderKeyStorageBackend`, which returns a 503 on every key operation. This means no key can be stored until the OS keychain backend is implemented. This is the safe default: a missing key backend is surfaced as a UI message with instructions to use an environment variable, rather than silently failing or falling back to an insecure store.

**How does Test Connection protect the user?**
- Every click requires the user to confirm a cost acknowledgement dialog covering four disclosures.
- The backend sends exactly one request — sixteen output tokens, no memory, no tools, no streaming, no conversation history.
- There are no automatic retries.
- If the provider call fails for any reason, the response contains only a safe category string and a safe human-readable message — never the raw provider error body.
- Unknown error strings are collapsed to a generic `provider_error` category so internal provider details cannot leak through error responses.

**Has a live provider call been made?**
No. No live external provider call has been made at any point in this project. No real API key has been used in tests, in demos, or in development sessions.

---

## Screenshot Checklist

Capture these screenshots for the portfolio. Label each file clearly.

| # | What to Capture | Notes |
|---|---|---|
| 1 | Main Electron chat UI | Show a sent message and a mock response (`source: mock`) |
| 2 | Memory section | Show one or two created memories; show the context preview |
| 3 | Audit Logs section | Show at least one audit row with safe metadata columns |
| 4 | Provider Settings — full section | Show provider selector, model field, enable toggle, key status, usage summary |
| 5 | Provider Settings — key status unavailable | Show the safe storage-unavailable message with env var instructions |
| 6 | Test Connection button — disabled state | Show the disabled button with tooltip or helper text |
| 7 | pytest result | Terminal showing `470 passed` |
| 8 | Project docs listing | File explorer or `ls docs/` showing all design documents |
| 9 | Backend health check | Terminal showing `curl` or `Invoke-RestMethod` response with `status: ok` |

*Optional if available:*
- Test Connection cost acknowledgement dialog (requires `key_status: configured`)
- Provider settings after a successful mock provider test run

---

## What Not To Claim

Be explicit about what this project is not yet. Misrepresenting the state undermines credibility.

| Do not claim | Correct statement |
|---|---|
| Production-ready | This is a prototype / portfolio project |
| Live Anthropic or OpenAI integration is fully working | The LLM adapter exists and is tested with mocked HTTP; no live call has been made |
| OS keychain storage is implemented | The OS keychain backend is designed and the abstraction is ready; the implementation is deferred |
| Token cost estimates are billing-accurate | Cost estimates use rule-based estimation; they are not sourced from provider billing APIs |
| Automatic memory extraction from conversation | All memory is manual; automatic extraction is not implemented |
| Streaming, tool use, TTS, or Live2D are implemented | These are out of scope for the current phase |
| The app is installable / packaged | No installer or packaged binary exists yet |
| Multiple simultaneous providers | Single active provider at a time |

---

## Current Limitations

| Limitation | Impact | Next Step |
|---|---|---|
| No live provider call | Cannot demo real LLM responses | Implement OS keychain + explicit user cost confirmation |
| Runtime key storage unavailable | Save Key / Test Connection disabled at runtime | Implement OS keychain backend |
| Usage meter is in-memory | Resets on backend restart | Persist to SQLite (deferred) |
| UI needs further polish | DevTools docked-right layout partially improved | Phase 5 UI work |
| No production packaging | Cannot distribute as installable app | Packaging / installer (Phase 5) |
| TASK-038 (Live LLM Smoke) pending | Manual live smoke not yet executed | Requires key storage + user cost confirmation |

---

## Interview Talking Points

Use these to structure technical conversation with an interviewer.

**Safe incremental development**
Every capability that could expose user data or incur cost has three things before implementation: a design document, a safety review, and a feature flag. Nothing is enabled by default.

**Feature flags**
`LLM_PROVIDER_ENABLED`, `LLM_CHAT_ENABLED`, and `MEMORY_INJECTION_ENABLED` all default to `false`. Switching any of them on is a deliberate opt-in, not a gradual drift.

**Privacy boundaries**
The project defines explicit "forbidden fields" for logging — `user_message`, `conversation_history`, `LLMResponse.text`, and `api_key` — and the provider's `__repr__` and `__str__` are overridden to prevent accidental secret logging.

**Test-first safety gates**
For Test Connection: design (TASK-058) → backend implementation with mocked tests (TASK-059) → independent safety review (TASK-059R) → UI enablement (TASK-060) → hardening tests based on review recommendations (TASK-062). The UI was not enabled until the backend passed external review.

**Mocked provider testing**
The entire test suite runs against `FakeProviderTestRunner` and `InMemoryKeyStorageBackend`. No test touches a real provider endpoint or a real key. This makes the CI suite deterministic, cost-free, and safe to run in any environment.

**Response schema stability**
The `/chat` response schema (`reply / mood / source`) has not changed across the entire Phase 4 build. Every new feature was added as a separate endpoint or a separate response field, never by breaking an existing schema.

**No secret leakage**
Five dedicated hardening tests verify: that the runner is never called when the provider is disabled or the model is missing, that unknown provider errors don't leak raw strings, that extra request fields are rejected without being echoed, and that all error category safe messages are free of API key or raw body content.

**Service separation**
The backend has one service per responsibility: `chat_service`, `memory_service`, `memory_audit_service`, `usage_meter_service`, `provider_settings_service`, `key_storage_service`, `provider_test_connection_service`. Each is independently testable and has a clear ownership boundary.

**Clear product direction**
Local-first, BYOK, personal companion. The project makes a deliberate product choice: no shared backend, no cloud key, no automatic data upload. This is stated in design documents, not just implied by the code.

---

## Demo Commands (Windows PowerShell)

```powershell
# 1. Start the backend
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 2. Health check
Invoke-RestMethod -Uri http://localhost:8000/health

# 3. Chat (mock)
Invoke-RestMethod -Method POST `
  -Uri http://localhost:8000/chat `
  -ContentType "application/json" `
  -Body '{"message": "Hello!"}'

# 4. Start Electron (in a separate terminal)
cd apps\desktop
npm install
npm start

# 5. Run tests
cd backend
python -m pytest
# Expected: 470 passed

# 6. Check Provider Settings API
Invoke-RestMethod -Uri http://localhost:8000/provider/settings

# 7. Check key status
Invoke-RestMethod -Uri http://localhost:8000/provider/settings/key/status
```

---

## Suggested Demo Flow (Read-Aloud Script)

> "Let me show you the Dragon Pet AI project. It's a local-first desktop companion app built with Electron and FastAPI."

*Open Electron. Point to the window.*

> "The Electron frontend connects to a local FastAPI backend on port 8000. Everything runs on your machine — no cloud service, no external API call."

*Type a message and send.*

> "The chat goes through the full backend stack — request validation, the chat service, the LLM adapter layer — and comes back with a mock response. The LLM is mocked right now. When the user provides their own API key and enables the real provider, this is where the real response would appear."

*Open Memory section. Create an entry.*

> "The memory system lets the user or the app store facts about them. These live in a local SQLite database. There's an approved context builder that formats selected memories into a prompt — with a 5-memory, 1500-character cap and a sensitive-content filter. Memory injection into chat is behind two separate gates: a backend environment variable and a per-request toggle."

*Open Audit Logs.*

> "Every time the memory-aware chat runs, it creates an audit row. The row stores which memory IDs were selected, how many, and the total context length — but never the raw memory content or the user message. This makes the system inspectable without becoming a privacy leak."

*Open Provider Settings.*

> "This is the provider settings section. The user can select their provider, enter their model, and bring their own API key. The key is write-only — the backend accepts it, stores it in the key storage abstraction, and never returns it. The key status here shows 'not configured' because the key storage backend in the current runtime is an unavailable backend that returns 503 by default. That's the safe default."

*Point to Usage Summary.*

> "The usage summary tracks 14 fields per provider interaction — tokens, status, whether memory context was included, whether it was a test connection. All in-memory, never written to disk in this version."

*Point to Test Connection.*

> "Test Connection requires the user to confirm a cost acknowledgement every single click. The backend sends exactly one request — sixteen tokens, no tools, no memory, no history — and collapses any unknown error to a safe message. This endpoint was reviewed by a separate AI model acting as a second reviewer, and it passed. Then I added five more hardening tests based on the review recommendations."

*Show terminal.*

> "The test suite has 470 tests — all mocked, all deterministic, no external HTTP, no real key. This runs in a couple of seconds."

---

## Next Development Options

| Option | Description | Dependency |
|---|---|---|
| OS Keychain backend | Implement `keytar`-based storage so Save Key works at runtime | None — abstraction is ready |
| Live provider smoke | Manual live smoke with explicit user cost confirmation | OS Keychain + user confirmation |
| `/chat` real provider wiring | Enable `LLM_CHAT_ENABLED=true` with a real provider | Live smoke complete |
| Usage meter persistence | Persist meter to SQLite so counts survive restart | Design doc only (no impl) |
| UI polish and packaging | Installer, tray icon, window management | Phase 5 |
| Streamer Companion Mode | OBS overlay, Twitch EventSub, public safety layer | Phase 5 LLM stable + TTS |

---

## Reference

| Document | Topic |
|---|---|
| `docs/PORTFOLIO_SCREENSHOT_CHECKLIST.md` | Screenshot capture plan: 9 required screenshots, naming convention, what not to show, setup commands |
| `docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md` | Full Phase 4 Provider Settings summary (TASK-045–TASK-064) |
| `docs/PROVIDER_TEST_CONNECTION_DESIGN.md` | Test Connection design and hardening test results |
| `docs/SECURE_KEY_STORAGE_DESIGN.md` | Key storage options, threat model, redaction rules |
| `docs/BYOK_PRODUCT_AND_SETTINGS.md` | BYOK product design and security boundaries |
| `docs/COST_AND_MONETIZATION.md` | Live smoke go/no-go criteria |
| `docs/PHASE4_PLAN.md` | Phase 4 planning document |
| `docs/TASKS.md` | Full task history |
| `docs/ROADMAP.md` | Phase-by-phase status |
