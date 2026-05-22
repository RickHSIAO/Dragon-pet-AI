# Dragon Pet AI

> **Dragon Pet AI** is a local-first Electron + FastAPI desktop companion prototype with manual memory, memory audit logs, BYOK provider settings, usage metering, a safety-reviewed Test Connection endpoint, Anthropic/Ollama provider adapters behind flags, local Ollama `/chat` runtime smoke passed with `source=llm_local` and ??蝯脰?憡?persona active, Ollama option in Provider Settings UI (no API key, local GPU/CPU) - built with safety-first incremental development and a 531-test mocked backend suite.

**Not production-ready.** No live external provider call has been made. No real API key has been used. This is a portfolio / prototype project.

?? **[Full Demo Script & Interview Talking Points ?(docs/PORTFOLIO_DEMO_SCRIPT.md)**
?? **[Phase 4 Provider Settings Summary ?(docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md)**

---

## Screenshots

![Main Chat UI](docs/screenshots/01_main_chat_ui.png)

*Local-first Electron desktop companion UI with mock LLM source ??no external provider call.*

---

![Memory Audit Logs](docs/screenshots/03_audit_logs.png)

*Safe metadata-only audit trail ??raw memory content and prompt text are never stored in audit rows.*

---

![Provider Settings](docs/screenshots/04_provider_settings_overview.png)

*BYOK provider configuration with write-only key handling, key status display, and safety-gated controls.*

---

![Usage Summary](docs/screenshots/05_usage_summary.png)

*Safe aggregate usage counters only ??no raw prompt text, no API key, no provider response body.*

---

![Pytest 470 Passed](docs/screenshots/08_pytest_470_passed.png)

*Mocked backend test suite screenshot from portfolio capture; latest known backend suite: 531 passing tests, zero failures, no external HTTP, no real API key.*

---

## Quick Start (Local Ollama Mode)

> Full instructions and troubleshooting: **[docs/LOCAL_DEV_RUNBOOK.md](docs/LOCAL_DEV_RUNBOOK.md)**

Three terminals, in order:

**Terminal 1 — Ollama (local LLM server)**
```powershell
ollama serve
# First time: ollama pull qwen3:8b
```

**Terminal 2 — Backend**
```powershell
.\scripts\dev-start-backend.ps1
# Sets all env vars, activates venv, starts uvicorn on :8000
```

**Terminal 3 — Electron desktop**
```powershell
.\scripts\dev-start-desktop.ps1
# Uses npm.cmd (avoids execution-policy issues), clears ELECTRON_RUN_AS_NODE
```

**Optional smoke check**
```powershell
.\scripts\dev-smoke.ps1
# Checks /health, /provider/settings, /provider/settings/test, /chat
# Reports source=llm_local when Ollama is generating replies
```

Common issues:
- `uvicorn not found` → `cd backend; .venv\Scripts\pip install -r requirements.txt`
- `npm.ps1 is disabled` → always use `npm.cmd`, not `npm`
- `ELECTRON_RUN_AS_NODE` → cleared automatically by the startup script
- Cold-start timeout → first `/chat` can take up to 90 s while the model loads; retry after waiting

---

## Current Status

| Item | State |
|---|---|
| Architecture | Electron desktop + FastAPI backend, end-to-end working |
| Phase 3 | ??Complete ??Memory, Audit Logs, Memory-Aware Chat |
| Phase 4 | IN_PROGRESS - Provider Settings / BYOK stabilized; Local Ollama runtime smoke PASSED; Ollama Provider Settings UI complete (TASK-076); Mood -> Pet Expression Mapping complete (TASK-083); Christina neutral/focused v0 PNG assets present (focused is temporary duplicate placeholder, TASK-089) |
| pytest | 586 passed, 0 failed |
| Local Ollama /chat smoke | ??PASS ??`qwen3:8b`, `source=llm_local`, persona confirmed |
| Live external provider call | ??None ??intentionally gated |
| Real API key used | ??None ??all tests use mocked runners |
| Production-ready | ??Not yet ??prototype / portfolio stage |
| Demo-ready (local mock) | ??Yes |

---

## Completed Capabilities

| Capability | Notes |
|---|---|
| `GET /health` | Backend liveness check |
| `POST /chat` | Mock character response; LLM adapter behind feature flag |
| Electron desktop UI | Chat, Memory, Audit Logs, Provider Settings sections |
| Manual Memory CRUD | `POST/GET/DELETE /memory` ??SQLite persistence |
| Memory context preview | `GET /memory/context-preview` ??safe, no injection |
| Approved memory context builder | Type allowlist, confidence filter, 5-memory / 1500-char cap |
| Memory-aware chat (two-layer gate) | `MEMORY_INJECTION_ENABLED` env flag + per-request `use_memory` |
| Memory Injection Audit API | `GET /memory/audit` ??safe metadata only, no raw content |
| Audit Logs UI | Desktop section; shows injection events |
| In-memory usage meter | 14 tracked fields; token estimation; privacy boundaries |
| Provider Settings API | `GET/PATCH /provider/settings` ??non-secret fields only |
| Key status endpoint | `GET /provider/settings/key/status` ??6 safe values, no key fragment |
| Save Key endpoint | `POST /provider/settings/key` ??write-only; key never echoed |
| Clear Key endpoint | `DELETE /provider/settings/key` ??clears from storage abstraction |
| Provider Settings UI | Provider/model select, Save Key, Clear Key, key status, usage summary |
| Secure key storage abstraction | `UnavailableBackend` (runtime), `InMemoryBackend` (tests) |
| Test Connection backend | `POST /provider/settings/test` ??explicit cost ack required; Opus review PASS |
| Test Connection UI | Cost confirm dialog; safe field rendering; no auto-run |
| LLM adapter layer | Anthropic adapter behind `LLM_PROVIDER_ENABLED=false` |
| Hardening tests | 5 Opus-recommended tests covering edge cases and safety boundaries |
| Local Ollama provider | Implemented behind flags; no API key; localhost-only; runtime smoke PASSED ??`source=llm_local`, ??蝯脰?憡?persona active in qwen3:8b |
| Ollama Provider Settings UI | Provider selector includes `ollama`; API key input hidden/disabled for local provider; Test Connection uses Local Resource Warning; renderer never calls Ollama directly |
| 531 mocked tests | Full backend suite; no external HTTP; no real key |

---

## Architecture

```
Electron renderer (HTML / CSS / JS)
  ??? localhost HTTP ??FastAPI backend (:8000)
        ??? api/routes.py                    ??all HTTP endpoints
        ??? services/
        ??    ??? chat_service               ??/chat routing, LLM adapter wiring
        ??    ??? memory_service             ??memory CRUD, approved context builder
        ??    ??? memory_audit_service       ??audit row creation and inspection
        ??    ??? usage_meter_service        ??token/cost tracking (in-memory)
        ??    ??? provider_settings_service  ??non-secret settings persistence
        ??    ??? key_storage_service        ??secure key storage abstraction
        ??    ??? provider_test_connection_service ??Test Connection logic
        ??? providers/
        ??    ??? mock_provider              ??always-on safe default
        ??    ??? anthropic_provider         ??behind LLM_PROVIDER_ENABLED flag
        ??    ??? provider_factory           ??selects provider by config
        ??? schemas/                         ??Pydantic request/response models
        ??? db/                              ??SQLModel / SQLite engine
```

**Key design decisions:**
- **Adapter pattern** ??adding a new LLM provider requires only a new adapter; service and route layers are unchanged
- **Feature flags everywhere** ??`LLM_PROVIDER_ENABLED`, `LLM_CHAT_ENABLED`, `MEMORY_INJECTION_ENABLED` all default `false`
- **Schema stability** ??`/chat` response (`reply / mood / source`) unchanged across all of Phase 4
- **Write-only key handling** ??no endpoint returns the API key or any fragment of it
- **Test isolation** ??`InMemoryKeyStorageBackend` and `FakeProviderTestRunner` injected via dependency inversion; no test touches a real provider or a real key

---

## Safety / BYOK

**BYOK (Bring Your Own Key)** means the user supplies their own LLM provider API key. The app does not ship with a developer-owned key.

| Rule | Implementation |
|---|---|
| API key never returned to frontend | Write-only endpoints; key never in any response body |
| API key never stored in SQLite | `UnavailableBackend` runtime default; OS keychain designed (not yet wired) |
| API key never logged | Forbidden fields enforced; provider `__repr__`/`__str__` redact secrets |
| API key never in localStorage/sessionStorage | Electron renderer does not store or receive the key |
| Test Connection requires cost ack | `explicit_cost_ack: true` required per click; `window.confirm()` with 4 disclosures |
| Test Connection sends exactly one request | 16 output tokens; no memory, tools, streaming, or history |
| Unknown errors return safe messages | `_safe_error_category()` collapses unknown strings to `"provider_error"` |
| Extra request fields rejected | `ConfigDict(extra="forbid")` on all request schemas |
| No live provider call | Runtime default is `UnavailableProviderTestRunner` and `UnavailableKeyStorageBackend` |
| Independent safety review | Test Connection backend reviewed by Opus ??verdict: **PASS** |

---

## Quick Start (Windows PowerShell)

### Run tests

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest
# Expected: 531 passed
```

### Start the backend

```powershell
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### Verify backend

```powershell
# Health check
Invoke-RestMethod -Uri http://localhost:8000/health

# Mock chat
Invoke-RestMethod -Method POST `
  -Uri http://localhost:8000/chat `
  -ContentType "application/json" `
  -Body '{"message": "Hello!"}'
```

### Start the Electron desktop

> Requires backend running at localhost:8000.

```powershell
cd apps\desktop
npm install
npm start
```

---

## Local LLM Mode (Ollama)

Local LLM mode uses Ollama on your own machine. It does not require an API key and does not send renderer data directly to Ollama. The Electron renderer only calls the FastAPI backend at `localhost:8000`; the backend owns provider selection, safety checks, usage metadata, and the Ollama request to `localhost:11434`.

### Preconditions

Install Ollama, pull the recommended local model, and confirm it is available:

```powershell
ollama pull qwen3:8b
ollama list
```

### Start Local LLM Mode

Start Ollama:

```powershell
ollama serve
```

Start the backend:

```powershell
cd backend
$env:LLM_PROVIDER_ENABLED="true"
$env:LLM_CHAT_ENABLED="true"
$env:LLM_PROVIDER_NAME="ollama"
$env:LLM_MODEL="qwen3:8b"
$env:OLLAMA_BASE_URL="http://localhost:11434"
uvicorn app.main:app --reload
```

Start Electron using the existing desktop command:

```powershell
cd apps\desktop
npm start
```

### Provider Settings UI

Open Provider Settings and select `ollama ??local, no key`.

Expected UI state:
- API key input is disabled because Ollama does not use an API key.
- Key status shows `not_required`.
- Save Key and Clear Key are unavailable for Ollama.
- Test Connection is available when real provider is enabled.
- Test Connection shows a Local Resource Warning because it uses local GPU/CPU, not an API cost warning.

### /chat Smoke Test

With backend running in Ollama mode:

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai\backend

$env:PYTHONIOENCODING="utf-8"

python -c "import json, urllib.request; data=json.dumps({'message':'??蝯脰?憡?蝔梯???銝???憭拇??芸???獢?}, ensure_ascii=False).encode('utf-8'); req=urllib.request.Request('http://127.0.0.1:8000/chat', data=data, headers={'Content-Type':'application/json; charset=utf-8'}); raw=urllib.request.urlopen(req).read().decode('utf-8'); print(raw)"
```

Expected result:
- HTTP 200
- Response schema remains `reply / mood / source`
- `source` is `llm_local`
- `reply` is generated locally by `qwen3:8b`
- The reply should carry Christina's voice, such as `?霉, `瘙, `?嬋, or a tsundere / arrogant tone.

### Release Readiness Smoke Flow

Use this checkpoint flow before calling Local LLM mode ready:

1. Start Ollama: `ollama serve`.
2. Confirm the model: `ollama list` should include `qwen3:8b`.
3. Start the backend with `LLM_PROVIDER_ENABLED=true`, `LLM_CHAT_ENABLED=true`, `LLM_PROVIDER_NAME=ollama`, `LLM_MODEL=qwen3:8b`, and optionally `LLM_LOCAL_CHAT_TIMEOUT_SECONDS=90` for cold local model loads.
4. PATCH `/provider/settings` to `provider=ollama`, `model=qwen3:8b`, `real_provider_enabled=true`, `llm_chat_enabled=true`, and `fallback_to_mock=false`.
5. POST `/provider/settings/test` to confirm the backend can reach the local Ollama runtime and model. This is a lightweight local runtime/model check, not a full persona chat generation.
6. POST `/chat` to verify generation, Christina persona, `mood`, and `source=llm_local`.
7. Start Electron with the existing desktop command.
8. In Provider Settings, select `ollama - local, no key`, verify `key_status=not_required`, run Test Connection, then send a chat message.
9. Confirm the UI renders the reply, updates mood, and shows `source: llm_local` in the chat runtime status area.

### Runtime UX and Fallback Policy

- The chat runtime status area is intentionally visible in the main UI for MVP smoke and demo clarity. It shows the last `/chat` source and provider/resolved/model summary.
- Local Ollama replies should show `source: llm_local`.
- Local provider failures with fallback disabled show `source: llm_local_error` and a safe error-style status.
- For development and smoke tests, use `fallback_to_mock=false` so provider failures are visible.
- For safer demos where a mock reply is preferable to an error, `fallback_to_mock=true` is allowed, but the UI will show `source: mock` and explain that fallback may have occurred.
- If you need to prove the local model is actually responding, turn fallback off.
- First local responses may be slower while the model wakes up; the Electron UI shows a local cold-start loading message while `/chat` is pending. Local chat generation uses `LLM_LOCAL_CHAT_TIMEOUT_SECONDS` (default 90 seconds) so cold starts have more time than cloud-provider calls.

### Troubleshooting

| Symptom | Check |
|---|---|
| `ollama` not found | Install Ollama and reopen the terminal so `ollama` is on PATH. |
| `qwen3:8b` not found | Run `ollama pull qwen3:8b`, then confirm with `ollama list`. |
| Test Connection fails | Confirm `ollama serve` is running and `OLLAMA_BASE_URL` is `http://localhost:11434`. |
| `/chat` returns `source=mock` | Confirm `llm_chat_enabled=true`; if `resolved_provider=ollama`, check whether `fallback_to_mock=true` allowed a fallback after local provider failure. |
| `/chat` returns `source=llm_local_error` | Ollama was selected but local generation failed. Check `ollama serve`, the model name, and timeout/cold-start behavior; increase `LLM_LOCAL_CHAT_TIMEOUT_SECONDS` if your first local response loads slowly. |
| Provider Settings lose `model` or fallback changes unexpectedly | Refresh Provider Settings before saving. Partial PATCH preserves omitted fields, and Test Connection does not persist settings. |
| Reply lacks Christina tone | Confirm latest backend code is running and restart backend so prompt changes are loaded. |
| Backend seems to ignore new settings | Stop and restart backend; env vars and provider settings are read by the backend process. |

### Local LLM Safety Rules

- Do not add direct `localhost:11434` calls to the Electron renderer.
- Do not treat Ollama as a provider that needs an API key.
- Do not change the `/chat` response schema.
- Do not call Anthropic/OpenAI or any external provider for Ollama mode.
- Do not add live network-dependent tests; automated tests must keep using mocked transports.

---

## Demo & Portfolio Links

| Document | Purpose |
|---|---|
| [docs/PORTFOLIO_DEMO_SCRIPT.md](docs/PORTFOLIO_DEMO_SCRIPT.md) | Full demo script: one-liner, 30-sec pitch, 2-min walk-through, interview talking points, screenshot checklist |
| [docs/PORTFOLIO_SCREENSHOT_CHECKLIST.md](docs/PORTFOLIO_SCREENSHOT_CHECKLIST.md) | Screenshot capture plan: 9 required screenshots, naming convention, setup commands, what not to show |
| [docs/OLLAMA_PROVIDER_DESIGN.md](docs/OLLAMA_PROVIDER_DESIGN.md) | Local Ollama provider design and TASK-074 contract test notes: API contract, qwen3:8b recommendation, provider settings integration, feature flags, security boundaries |
| [docs/OLLAMA_RUNTIME_SMOKE_CHECKLIST.md](docs/OLLAMA_RUNTIME_SMOKE_CHECKLIST.md) | TASK-075 runtime smoke checklist ??**PASS** (2026-05-21): `source=llm_local`, ??蝯脰?憡?persona confirmed, no external API |
| [docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md](docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md) | Phase 4 stabilization summary: completed capabilities, safety boundaries, test results, live smoke go/no-go |
| [docs/PROVIDER_TEST_CONNECTION_DESIGN.md](docs/PROVIDER_TEST_CONNECTION_DESIGN.md) | Test Connection design and hardening test results |
| [docs/SECURE_KEY_STORAGE_DESIGN.md](docs/SECURE_KEY_STORAGE_DESIGN.md) | Key storage threat model, storage options, redaction rules |
| [docs/BYOK_PRODUCT_AND_SETTINGS.md](docs/BYOK_PRODUCT_AND_SETTINGS.md) | BYOK product design and security boundaries |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Full phase-by-phase development roadmap |
| [docs/TASKS.md](docs/TASKS.md) | Complete task history |
| [docs/STREAMER_COMPANION_MODE.md](docs/STREAMER_COMPANION_MODE.md) | Future side track ??OBS overlay / Twitch companion design (not scheduled) |

---

## Current Limitations

| Limitation | Detail |
|---|---|
| No live provider call | Runtime key storage unavailable; Test Connection button disabled by design |
| No real API key used | All tests use mocked runners and in-memory fake storage |
| OS keychain not wired | Storage abstraction is ready; `keytar` backend not yet implemented |
| Usage meter is in-memory | Resets on backend restart; persistent meter deferred |
| No automatic memory extraction | All memory is manually created |
| No streaming / tools / TTS / Live2D | Out of scope for current phase |
| No installer / packaging | Not packaged as distributable app |
| Not billing-accurate | Token cost estimates use rule-based approximation |

---

## Directory Structure

```
dragon-pet-ai/
  apps/
    desktop/
      package.json
      src/
        main.js               # Electron main process
        renderer/
          index.html          # Main window HTML
          renderer.js         # UI logic, backend calls
          styles.css          # Styles
  backend/
    app/
      main.py                 # FastAPI entry point
      api/routes.py           # All HTTP endpoints
      core/config.py          # Feature flags, env config
      db/database.py          # SQLModel engine
      schemas/                # Pydantic request/response models
      services/               # Business logic (one file per service)
      providers/              # LLM adapter layer
    tests/                    # pytest suite (531 tests)
    requirements.txt
  docs/                       # All design documents
  .env.example
  README.md
```

---

## All Design Documents

| Document | Topic |
|---|---|
| `docs/TASKS.md` | Task history and progress tracking |
| `docs/ROADMAP.md` | Phase-by-phase development roadmap |
| `docs/PRD.md` | MVP product requirements |
| `docs/ARCHITECTURE.md` | System architecture |
| `docs/CHARACTER_SPEC.md` | Character personality spec |
| `docs/MEMORY_SYSTEM.md` | Memory system design |
| `docs/PHASE3_DEMO_SUMMARY.md` | Phase 3 demo summary and safety model |
| `docs/PHASE4_PLAN.md` | Phase 4 planning: options, safety constraints, task sequence |
| `docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md` | Phase 4 Provider Settings stabilization summary (TASK-045?ASK-064) |
| `docs/LLM_ADAPTER_DESIGN.md` | LLM adapter architecture: provider interface, feature flags, safety rules |
| `docs/LLM_PROVIDER_CONTRACT.md` | Anthropic request/response/error mapping, mocked fixtures |
| `docs/CHAT_LLM_WIRING_DESIGN.md` | Chat LLM wiring design: `LLM_CHAT_ENABLED`, adapter flow, fallback |
| `docs/CHAT_LLM_REAL_PROVIDER_WIRING_DESIGN.md` | Real-provider /chat wiring design: flag matrix, source behavior |
| `docs/COST_AND_MONETIZATION.md` | Cost control and live smoke go/no-go criteria |
| `docs/BYOK_PRODUCT_AND_SETTINGS.md` | BYOK product design: key ownership, storage, security boundaries |
| `docs/USAGE_METER_DESIGN.md` | Usage meter: 14 tracking fields, token estimation, privacy boundaries |
| `docs/PROVIDER_SETTINGS_UI_DESIGN.md` | Provider Settings UI: 9-step settings flow, error UX, security boundaries |
| `docs/PROVIDER_SETTINGS_API_DESIGN.md` | Provider Settings API: 6 endpoints, write-only key handling, safe status model |
| `docs/SECURE_KEY_STORAGE_DESIGN.md` | Secure key storage: 4 options, threat model, redaction rules |
| `docs/PROVIDER_SETTINGS_KEY_UI_ENABLEMENT_DESIGN.md` | Save Key / Clear Key UI flow, unavailable storage UX, key status display |
| `docs/PROVIDER_TEST_CONNECTION_DESIGN.md` | Test Connection design and hardening test results (Opus review PASS) |
| `docs/PORTFOLIO_DEMO_SCRIPT.md` | Portfolio demo script: 30-sec pitch, 2-min walk-through, interview talking points |
| `docs/OLLAMA_PROVIDER_DESIGN.md` | Local Ollama provider design and contract test notes: API contract, qwen3:8b, no-key integration, security boundaries |
| `docs/OLLAMA_RUNTIME_SMOKE_CHECKLIST.md` | TASK-075 local Ollama runtime smoke checklist |
| `docs/STREAMER_COMPANION_MODE.md` | Future side track: OBS overlay / Twitch companion (not scheduled) |

---

## Development Principles

- **Docs before code** ??every feature is specified before it is implemented
- **Scope discipline** ??features belong to one phase; no Phase N+1 work during Phase N
- **Safety first** ??any capability that touches user data or incurs cost requires a safety design step
- **Local first** ??all user data stays on device unless the user explicitly opts in to a cloud feature
- **Reversible steps** ??prefer designs that can be undone without data loss

---

## Development Journal

> Internal task update log. Documents what changed in each task.

<details>
<summary>Expand task update history (TASK-054 ??TASK-067D)</summary>

> TASK-054: provider key save/clear endpoints are wired to the secure key storage abstraction. Runtime default remains a safe unavailable backend, tests use an in-memory fake backend, no key is written to SQLite or plain config files, and live test connection remains disabled. No external provider calls are made. pytest: 449 passed.

> TASK-055: Key UI enablement design complete. Save Key and Clear Key controls are now designed with full interaction flows, unavailable storage UX (503 ??safe message, env var recommendation), key status display (6 safe values, no key fragments), and security boundaries. Test Connection remains disabled.

> TASK-056: Save Key and Clear Key controls are now enabled in the Provider Settings UI. Key input is enabled for real providers only, disabled for mock. Save Key POSTs to local backend and clears the input field after every attempt. Clear Key shows a confirmation dialog and DELETEs via local backend. Storage unavailable (503) shows a safe message with env var instructions. API key is never logged, never stored in localStorage/sessionStorage, never sent to external providers. Test Connection remains disabled. pytest: 449 passed.

> TASK-058: Provider Test Connection design is documented. Test Connection remains disabled in runtime, requires future per-click `explicit_cost_ack`, sends exactly one minimal request, uses no retries/tools/streaming/memory, and does not fallback to mock. No live provider call has occurred.

> TASK-059: Backend `POST /provider/settings/test` is implemented with mocked-provider runner support. It requires per-click `explicit_cost_ack`, builds exactly one minimal no-memory/no-tools/no-streaming request, records safe aggregate usage, and never falls back to mock. Runtime default runner does not call external providers; Electron Test Connection UI remains disabled. pytest: 465 passed.

> TASK-059R: Opus safety review of TASK-059 backend: verdict PASS. No critical issues. explicit_cost_ack enforced at API boundary, response schema contains no secret-bearing fields, runtime default runner is UnavailableProviderTestRunner, no live external API calls in tests. TASK-060 unblocked.

> TASK-060: Test Connection button enabled in Electron renderer. Enable conditions: real provider selected, key_status configured, real_provider_enabled true. Explicit cost acknowledgement (window.confirm) required on every click ??covers all 4 required disclosures. POST to local backend only with body {provider, model, explicit_cost_ack: true} ??no api_key, no prompt, no memory. Safe response fields rendered: status, safe_message, error_category, source, usage_estimate. No automatic test after Save Key. No external provider URL in renderer. API key never logged, never in localStorage/sessionStorage. node --check: PASS. pytest: 465 passed.

> TASK-061: Runtime smoke check PASS WITH EXPECTED LIMITATION. Test Connection button correctly remained disabled (key_status: not_configured, no key stored ??expected safe behavior). No live external provider call was made.

> TASK-062: Provider Test Connection hardening tests complete. Added 5 Opus-recommended hardening tests: provider_disabled branch with configured key (runner not called), invalid_model 400 before runner call, unknown error collapse to provider_error (raw string does not leak), extra field rejection without echoing value (ConfigDict extra=forbid), safe_message category sweep across all 11 error categories. pytest: 470 passed, 0 failed. No backend logic modified. No Electron UI modified.

> TASK-063: Electron Provider Settings UI polish/layout fix complete. Renderer readability, vertical scrolling, Provider Settings status cards, usage summary, form spacing, button wrapping, and narrow-width DevTools-docked layout were improved. Save Key / Clear Key / Test Connection behavior is unchanged. No backend/app code was modified. No provider behavior changed. No external API call was made. Electron static checks passed.

> TASK-064: Provider Settings UI runtime smoke re-check PASS WITH NON-BLOCKING UI NOTES. All provider settings controls verified readable and functional after TASK-063 polish. Test Connection correctly disabled (key_status: not_configured ??expected safe behavior). No live external provider call. No real API key entered.

> TASK-065: Phase 4 Provider Settings Stabilization Summary complete. Created docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md covering TASK-045 through TASK-064: completed capabilities, safety boundaries (16 rules), implemented vs intentionally-not-implemented, runtime limitations, non-blocking UI notes, test results (470 passed), live smoke go/no-go conditions (all unmet ??no live call has occurred), and recommended next tasks. No backend/app code modified. No external API call made.

> TASK-066D: Portfolio Demo Script complete. Created docs/PORTFOLIO_DEMO_SCRIPT.md with project one-liner, 30-second pitch, 2-minute demo script (10 steps), architecture talking points, completed features table (21 items), safety/BYOK explanation, screenshot checklist (9 items), what not to claim (8 items), interview talking points (8 topics), and PowerShell demo commands. Project is demo-ready as a local-first prototype. No live external provider call has occurred. No real API key used. No backend/app code modified.

> TASK-067D: README polished as portfolio-friendly entry point. Added project one-liner, current status table, completed capabilities table (21 items), architecture diagram with key design decisions, safety/BYOK summary table, PowerShell quick start, demo & portfolio links, current limitations table, updated directory structure, updated docs table. Moved task update history to collapsible Development Journal section. No backend/app code modified. No external API call made.

</details>
