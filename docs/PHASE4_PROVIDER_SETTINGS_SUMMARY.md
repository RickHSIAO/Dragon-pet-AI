# Phase 4 Provider Settings Stabilization Summary

> dragon-pet-ai
> Status: STABLE REFERENCE
> Covers: TASK-045 through TASK-064
> Created: TASK-065
> Last Updated: 2026-05-21

---

## Overview

This document consolidates the outcomes of the Provider Settings / BYOK / Test Connection sub-track of Phase 4. It serves as the canonical reference for what has been built, what safety boundaries hold, what remains intentionally out of scope, and what must happen before a live external provider call can be made.

**Top-line status as of TASK-064:**
- No live external provider call has occurred.
- No real API key has been used in any test or runtime session.
- Test Connection remains local-backend-only in all verified flows.
- Manual live provider smoke requires explicit user cost confirmation (per TASK-044 go/no-go criteria).
- pytest: 470 passed, 0 failed.

---

## Completed Capabilities

### BYOK Architecture (TASK-045)

The project adopts a Bring Your Own Key model: the user supplies their own provider API key and bears provider billing directly. No shared API key is baked into the app. The recommended MVP storage path is an OS keychain (future implementation); the MVP development path uses environment variables. Plain SQLite storage for keys is explicitly prohibited.

### Usage Meter (TASK-046, TASK-050)

An in-memory usage meter tracks 14 fields per provider interaction:

- `provider`, `model`, `call_type`, `timestamp_utc`
- `input_tokens_actual`, `output_tokens_actual`, `input_tokens_estimated`, `output_tokens_estimated`
- `status`, `error_category`, `source`
- `explicit_cost_ack`, `has_memory_context`, `is_test_connection`

The meter is local and ephemeral (in-memory, resets on restart). No raw prompt text or API key is stored. Token counts are actual where the provider returns them, estimated otherwise using the approved estimation rules from TASK-046.

### Backend Provider Settings API (TASK-048, TASK-051)

Five endpoints are implemented and tested:

| Endpoint | Purpose |
|---|---|
| `GET /provider/settings` | Return current non-secret settings (provider, model, real_provider_enabled) |
| `PATCH /provider/settings` | Update non-secret settings |
| `POST /provider/settings/key` | Save API key to secure storage (write-only; key not echoed back) |
| `DELETE /provider/settings/key` | Clear stored API key from secure storage |
| `GET /provider/settings/key/status` | Return key status (one of 6 safe values; no key fragment returned) |
| `POST /provider/settings/test` | Run one minimal test connection (requires `explicit_cost_ack: true`) |

All endpoints are local-backend-only (localhost:8000). No external provider URL is contacted by any endpoint unless the Test Connection runner is explicitly wired and `explicit_cost_ack` is supplied.

### Secure Key Storage (TASK-049, TASK-053)

A key storage abstraction layer is in place with two concrete backends:

- **`UnavailableProviderKeyStorageBackend`** — runtime default. Always returns 503. No key is ever written to disk or SQLite via this backend.
- **`InMemoryProviderKeyStorageBackend`** — test-only. Keys are stored in a Python dict, never written to disk.

The OS keychain backend (recommended for production desktop) is designed but not yet implemented. The abstraction is ready to receive it.

Key lifecycle rules:
- Key loaded from storage backend by the save/test endpoints only.
- Key never logged at any level.
- Key never included in any response body or response header.
- Key never stored in Electron localStorage or sessionStorage.
- Key never sent to Electron renderer.
- Provider `__repr__` and `__str__` redact secret fields.

### Provider Settings UI (TASK-047, TASK-052, TASK-055, TASK-056, TASK-063)

The Electron renderer includes a Provider Settings section with:

- Provider selector (mock / anthropic / openai)
- Model input field (enabled for real providers only)
- Enable Real Provider toggle
- API key input field (enabled for real providers only; cleared after every Save Key attempt)
- Save Key button — POSTs to `/provider/settings/key`; clears input after attempt; shows safe status message
- Clear Key button — shows confirmation dialog; DELETEs via `/provider/settings/key`; shows safe status message
- Key status display (one of 6 safe values; no key fragment)
- Test Connection button — enabled only when: real provider selected, `key_status === "configured"`, `real_provider_enabled === true`, and no in-flight test is running
- Usage summary display (safe aggregate fields only)
- Storage unavailable (503) UX: shows safe message with env var instructions

UI readability and scroll behavior were polished in TASK-063. The Provider Settings section is vertically scrollable when content exceeds window height.

### Provider Test Connection (TASK-058, TASK-059, TASK-059R, TASK-060, TASK-061, TASK-062)

The Test Connection flow is fully designed, implemented, and safety-reviewed:

**Backend (`POST /provider/settings/test`):**
- Requires `explicit_cost_ack: true` on every request (not cached, not defaulted).
- Sends exactly one minimal request: `TEST_USER_MESSAGE = "Reply with OK."`, `TEST_MAX_TOKENS = 16`, no memory, no tools, no streaming, no conversation history.
- Never falls back to mock provider on failure — failures return `source: "llm_real_error"`.
- Response schema: `status`, `safe_message`, `error_category`, `source`, `provider`, `model`, `usage_estimate`. No API key, no raw provider body, no prompt text in any response field.
- Unknown runner errors are collapsed to the safe `"provider_error"` category by `_safe_error_category()`.
- Extra request fields (e.g., `system_prompt`) are rejected by `ConfigDict(extra="forbid")` with a 422 before any runner is called.
- Runtime default runner: `UnavailableProviderTestRunner` — returns a safe failure without contacting any external provider.
- Safety review verdict: **PASS** (TASK-059R, Opus).

**Electron renderer:**
- Test Connection button calls `window.confirm()` with all 4 required cost disclosures on every click.
- POST body: `{provider, model, explicit_cost_ack: true}` only — no API key, no prompt, no memory.
- Renders only safe response fields: `status`, `safe_message`, `error_category`, `source`, `usage_estimate`.
- No automatic test after Save Key.
- No external provider URL in renderer source.

**Runtime smoke (TASK-061):**
- Test Connection button correctly remained disabled (`key_status: not_configured`) — expected safe behavior given `UnavailableProviderKeyStorageBackend` runtime default.
- No live external provider call was made.
- Verdict: **PASS WITH EXPECTED LIMITATION**.

**Hardening tests (TASK-062):**
- 5 of 5 Opus-recommended hardening tests pass (see table below).

---

## Current Safety Boundaries

These boundaries hold as of TASK-064 and must not be violated by future tasks without a dedicated safety review.

| Boundary | Rule |
|---|---|
| LLM_PROVIDER_ENABLED | Defaults `false`; real provider requires explicit env var opt-in |
| LLM_CHAT_ENABLED | Defaults `false`; gates `/chat` LLM adapter separately from provider selection |
| API key scope | Backend env var only; never logged, never returned, never in frontend, never in repr/str |
| Key storage | UnavailableBackend runtime default; OS keychain deferred; plain SQLite prohibited |
| /chat schema | Remains `reply / mood / source` — unchanged |
| Memory gate | Two-layer gate unchanged: `MEMORY_INJECTION_ENABLED` + per-request `use_memory` |
| Retries | No automatic retries; at most one real provider call per `/chat` turn or Test Connection click |
| Non-2xx responses | Opaque — not parsed, not logged, not returned |
| Test Connection | `explicit_cost_ack: true` required per click; no auto-run after Save Key; no mock fallback |
| Test Connection request | Exactly one minimal request; no memory / tools / streaming / history |
| Extra request fields | `ConfigDict(extra="forbid")` on `ProviderTestConnectionRequest` rejects unknown fields |
| Response safety | No API key, no raw provider body, no prompt text in any response field |
| Electron storage | API key never in localStorage / sessionStorage |
| External URLs | No external provider URL in Electron renderer source |
| Tool execution | Not implemented; deferred to Phase 5 with dedicated safety review |
| Live smoke gating | Blocked until explicit user cost confirmation and TASK-044 go/no-go criteria met |

---

## What Is Implemented

- Backend Provider Settings API: 6 endpoints (GET/PATCH settings, POST/DELETE/GET-status key, POST test)
- Secure key storage abstraction with `UnavailableBackend` (runtime) and `InMemoryBackend` (tests)
- In-memory usage meter: 14 tracking fields, token estimation, privacy boundaries
- Provider Settings UI in Electron: provider/model select, Save Key, Clear Key, Test Connection, status display, usage summary
- Provider Test Connection: explicit cost ack, one minimal request, safe response schema, 11-category error map, unknown error collapse, extra-field rejection
- Opus safety review of Test Connection backend (TASK-059R): verdict PASS
- Electron Test Connection UI enablement: confirm dialog with 4 disclosures, safe field rendering
- 5 hardening tests: provider_disabled branch, invalid_model branch, unknown error collapse, extra-field rejection, safe_message category sweep
- UI readability and scroll behavior polish (TASK-063)
- Runtime smoke checks: TASK-057 (key UI), TASK-061 (Test Connection), TASK-064 (UI re-check after polish)

---

## What Is Intentionally Not Implemented

These items were explicitly deferred or excluded from scope. They must not be added without a new task and, where noted, a dedicated safety review.

| Item | Reason Deferred |
|---|---|
| OS keychain backend | Requires platform-specific implementation (keytar / Credential Manager); designed, not built |
| Live `/chat` with real provider | `LLM_CHAT_ENABLED=false`; requires TASK-038 live smoke and explicit user cost acceptance |
| Test Connection auto-run after Save Key | Explicitly prohibited — user must initiate every test click with cost ack |
| Streaming in Test Connection | Out of scope for minimal-request safety design |
| Tool use in Test Connection | Out of scope; no tool execution in Phase 4 |
| Retries in Test Connection | Prohibited — at most one external call per click |
| Memory context in Test Connection | Prohibited — no memory, no history, no context |
| External provider URL in Electron renderer | API key and provider calls are backend-only |
| API key echo in any response | Write-only key handling by design |
| Real-time cost display | Usage meter is aggregate; per-call cost display deferred |
| Multi-provider simultaneous use | Single active provider at a time |
| Provider API key rotation / versioning | Out of scope for MVP |

---

## Current Runtime Limitations

| Limitation | Root Cause | Status |
|---|---|---|
| Test Connection button disabled at runtime | `UnavailableProviderKeyStorageBackend` returns 503; `key_status: not_configured` | Expected safe default — unblocked by OS keychain impl |
| No key can be saved at runtime | Same — `UnavailableBackend` is the runtime default | Unblocked by OS keychain impl or env var wiring |
| No live provider call has been verified | TASK-038 (Live LLM Provider Smoke) is `IN_PROGRESS` | Requires explicit user cost confirmation |
| DevTools docked-right layout: partial | Narrow layout improved but full docked-right click-through not verified | Non-blocking; docked DevTools is a development-only view |
| Usage meter resets on backend restart | In-memory only; no persistence | By design for MVP; persistent meter deferred |

---

## Known Non-Blocking UI Notes

These were observed during TASK-064 runtime smoke and are recorded for reference. None block current development.

- **DevTools docked right**: basic controls remain usable but a full click-through with key storage in docked mode was not completed. Normal (undocked) operation is fully verified.
- **Test Connection disabled**: the button shows the correct disabled state and tooltip. This is the expected safe behavior given the current `UnavailableBackend` default — not a bug.
- **Desktop startup environment variable**: `ELECTRON_RUN_AS_NODE=1` must not be set in the shell launching Electron; if set, Electron starts in Node mode instead of opening the window. This is an Electron platform behavior, not a code bug.

---

## Test Results Summary

| Suite / Check | Result | Task |
|---|---|---|
| pytest (pre-TASK-062 baseline) | 465 passed | TASK-057 / TASK-061 |
| pytest (post-TASK-062 hardening) | **470 passed, 0 failed** | TASK-062 |
| node --check src/main.js | PASS | TASK-060, TASK-063 |
| node --check src/renderer/renderer.js | PASS | TASK-060, TASK-063 |
| Safety scan: no external provider URL in renderer | PASS | TASK-060, TASK-063 |
| Safety scan: no API key logging / localStorage | PASS | TASK-060 |
| TASK-059R Opus safety review | **PASS** | TASK-059R |
| Key UI runtime smoke (TASK-057) | PASS | TASK-057 |
| Test Connection runtime smoke (TASK-061) | PASS WITH EXPECTED LIMITATION | TASK-061 |
| UI readability runtime smoke (TASK-064) | PASS WITH NON-BLOCKING UI NOTES | TASK-064 |

### Hardening Tests (TASK-062)

| Test | Assertion | Result |
|---|---|---|
| A — provider_disabled with configured key | Runner not called; response status=failed, error_category=provider_disabled | PASS |
| B — invalid_model | 400 returned before runner; no runner call; SECRET not in response | PASS |
| C — unknown error collapse | Unknown string maps to provider_error; raw string not in response | PASS |
| D — extra field rejection | system_prompt injection rejected (422); sentinel not echoed; runner not called | PASS |
| E — safe_message category sweep | All 11 categories: non-empty, no API key / raw body / prompt sentinel, len 5–200 | PASS |

---

## Live Provider Smoke Go/No-Go Conditions

The following conditions must all be true before a manual live external provider call is made. This is the TASK-044 go/no-go gate.

| Condition | Current State |
|---|---|
| User has explicitly accepted cost risk in writing | NOT YET |
| Real API key configured (env var or OS keychain) | NOT YET — UnavailableBackend is runtime default |
| `LLM_PROVIDER_ENABLED=true` set at startup | NOT YET |
| `LLM_CHAT_ENABLED=true` set at startup (for /chat) | NOT YET |
| `explicit_cost_ack: true` sent per-click (for Test Connection) | Implemented and enforced |
| TASK-038 Live LLM Provider Smoke prerequisites met | IN_PROGRESS |
| No automatic retries, no fallback to mock | Implemented and enforced |
| Response body does not leak raw provider content | Implemented and enforced |

Until all conditions are met, no live external provider call should be initiated.

---

## Recommended Next Tasks

| Priority | Task | Description |
|---|---|---|
| High | TASK-066 — OS Keychain Backend Implementation | Implement the OS keychain storage backend (keytar on Windows/macOS/Linux) to unblock Save Key at runtime |
| High | TASK-038 Close or Live Smoke | Either close TASK-038 as deferred-until-keychain or execute the manual live smoke once key storage is working and user accepts cost |
| Medium | TASK-067 — Phase 4 /chat Real Provider Wiring | Wire `/chat` to the real provider adapter behind `LLM_CHAT_ENABLED=true` (requires TASK-038 complete and key storage working) |
| Low | TASK-068 — Usage Meter Persistence | Persist usage meter to SQLite so token counts survive backend restart |
| Low | Phase 5 Planning | Begin Phase 5 (Assistant Capabilities) task sequence once Phase 4 LLM wiring is stable |

---

## Reference Documents

| Document | Task | Topic |
|---|---|---|
| `docs/BYOK_PRODUCT_AND_SETTINGS.md` | TASK-045 | BYOK product design, key ownership, storage options, security boundaries |
| `docs/USAGE_METER_DESIGN.md` | TASK-046 | Token/cost tracking, estimation rules, privacy boundaries |
| `docs/PROVIDER_SETTINGS_UI_DESIGN.md` | TASK-047 | UI sections, 9-step settings flow, security boundaries, error UX |
| `docs/PROVIDER_SETTINGS_API_DESIGN.md` | TASK-048 | 5 endpoints, write-only key handling, safe status model, test connection safety |
| `docs/SECURE_KEY_STORAGE_DESIGN.md` | TASK-049 | 4 storage options, MVP recommendation, key lifecycle, redaction rules, threat model |
| `docs/PROVIDER_SETTINGS_KEY_UI_ENABLEMENT_DESIGN.md` | TASK-055 | Save Key / Clear Key UI flow, unavailable storage UX, key status display |
| `docs/PROVIDER_TEST_CONNECTION_DESIGN.md` | TASK-058 | Test Connection design, explicit cost ack, safe response model, hardening test results |
| `docs/COST_AND_MONETIZATION.md` | TASK-044 | Cost control, BYOK-first direction, live smoke go/no-go criteria |
| `docs/PHASE4_PLAN.md` | TASK-030 | Full Phase 4 planning, candidate directions, safety constraints |
