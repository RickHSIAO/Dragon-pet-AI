# Provider Settings UI Design

> dragon-pet-ai
> Phase: 4 — LLM Adapter Integration
> Status: DESIGN COMPLETE (TASK-047 DONE); NON-SECRET UI IMPLEMENTED (TASK-052 DONE); KEY UI ENABLEMENT DESIGNED (TASK-055)
> Last Updated: 2026-05-20
> Owner: TASK-047
> Backend API Design: see `docs/PROVIDER_SETTINGS_API_DESIGN.md` (TASK-048)
> Key UI Enablement Design: see `docs/PROVIDER_SETTINGS_KEY_UI_ENABLEMENT_DESIGN.md` (TASK-055)

---

## 1. Purpose

This document defines the user interface design for the Provider Settings panel in the dragon-pet-ai desktop app. The panel allows users to configure their LLM provider, enter their own API key (BYOK), select a model, and view current usage summaries.

Key principles:

- Settings UI must never directly call a provider from the frontend. All provider operations (key save, key validation, test connection) must be mediated through backend API endpoints.
- API key must never be sent to the frontend in any response. The UI may only show whether a key exists, not the key value.
- No live provider test should happen automatically. All provider tests require explicit user action.
- Cost warnings must appear before and during real provider configuration.

Backend API design is documented separately in `docs/PROVIDER_SETTINGS_API_DESIGN.md` (TASK-048). The UI calls backend endpoints only — it never stores the key in frontend state, never calls the provider directly, and never reconstructs or displays the key after submission.
- Mock mode remains the default. Provider Settings UI should make switching to real mode feel deliberate, not casual.

TASK-052 implements the safe non-secret UI subset: settings load/save and usage summary display. API key storage, key clearing, and live test connection remain disabled placeholders until secure key storage is implemented.

TASK-055 designs the key UI enablement — how Save Key and Clear Key controls are safely wired now that the backend key endpoints exist (TASK-054). Test Connection remains disabled. See `docs/PROVIDER_SETTINGS_KEY_UI_ENABLEMENT_DESIGN.md` for the full interaction design, unavailable storage UX, error messages, and security boundaries.

---

## 2. UI Sections

The Provider Settings panel consists of seven sections presented in a single scrollable panel or a dedicated settings screen.

### 2.1 Provider Selector

Allows the user to select which provider to use.

| Element | Description |
|---|---|
| Provider dropdown or radio group | Options: `Mock (no cost)`, `Anthropic`, `OpenAI` (future) |
| Current resolved provider | Read-only status field showing the currently active provider name (e.g. `mock`, `anthropic`) — never shows key |
| Mock indicator | If mock is active, show a subtle badge: `Safe Mode — No API cost` |

Rules:
- Mock must be the default selected option.
- Unknown or unconfigured provider falls back to mock — the UI should reflect this in the resolved status.
- Switching to a real provider must not automatically start any provider test.
- Switching to a real provider must show the cost warning (Section 2.5) immediately.

### 2.2 API Key Input

Allows the user to enter, save, or clear their API key for the selected provider.

| Element | Description |
|---|---|
| Key input field | Password-masked text input. Shows placeholder text only — never shows key value after save. |
| Save Key button | Sends key to backend for secure storage. Requires explicit user action. |
| Clear Key button | Deletes the stored key from backend storage. Requires confirmation dialog. |
| Key status indicator | Read-only: `Key configured` or `No key saved` — never shows key fragments |
| Key masking rule | After save, the input field is cleared. No way to retrieve or display the key through the UI. |

Rules:
- API key must never be sent back to the frontend after save.
- API key must never appear in renderer logs, DevTools, or Electron IPC messages.
- Save Key must POST to a backend endpoint (designed in TASK-048). It must not store the key in any frontend state.
- If the backend returns an error during save, show a safe generic error (Section 2.7).
- Clear Key must ask for confirmation before deleting. Clearing the key returns to mock mode.

### 2.3 Model Selection

Allows the user to select which model to use for the configured provider.

| Element | Description |
|---|---|
| Model input or dropdown | Free-text input or preset list for provider-specific models (e.g. `claude-opus-4-6`, `claude-sonnet-4-6` for Anthropic) |
| Current resolved model | Read-only: shows the model currently active on the backend. If not set, shows backend default. |
| Model token rate note | Informational text: `Model choice affects token rates and cost. Check provider pricing.` |

Rules:
- Model selection is sent to backend when saved. It does not trigger a provider test.
- Unknown model names are accepted by the UI but may be rejected by the backend — the UI should show a safe error in that case.
- Model dropdown contents may be static (hard-coded list for known providers) in MVP. Dynamic fetching from provider is deferred.

### 2.4 Safety Toggles

Shows the current state of key safety flags. These are read-only status displays in the settings UI — they are controlled via environment variables (or, in a future release, through a separate admin config API).

| Toggle / Status | Description |
|---|---|
| LLM Provider Enabled | Shows `On` / `Off` based on resolved backend flag. |
| LLM Chat Enabled | Shows `On` / `Off` based on resolved backend flag. |
| Fallback to Mock | Shows `On` / `Off` — whether real provider failure falls back to mock. |
| Memory-Aware Chat | Shows `On` / `Off` based on `MEMORY_INJECTION_ENABLED` backend flag. |

Rules:
- These must be read-only in the TASK-047 design. They are not interactive toggles in Phase 4.
- The UI should not expose raw env var names to the user — use plain-language labels.
- Showing these flags gives the user visibility without giving them direct control over backend safety settings.

### 2.5 Cost Warning

A persistent, non-dismissable warning shown whenever a real provider is selected or configured.

```
⚠ Using a real provider will incur charges from your API provider.
You are responsible for costs associated with your own API key.
Start with a small test request.
Do not enable always-on mode unless you understand the ongoing cost.
Mock mode (default) has no API cost.
```

Rules:
- This warning must appear as soon as the user selects a real provider.
- This warning must appear again before the user clicks Test Connection.
- The warning must not be dismissable or hideable in Phase 4.
- The text must be clear and non-technical. It should not reference env var names.

### 2.6 Usage Meter Summary

A compact usage summary embedded in the Provider Settings panel, showing current session and daily usage estimates.

| Display Element | Source |
|---|---|
| Session requests | In-memory session counter |
| Today's requests | Daily aggregate |
| Estimated tokens (session) | In-memory estimate — labeled as `~estimate` |
| Estimated tokens (today) | Daily aggregate — labeled as `~estimate` |
| Current provider | Resolved provider name |
| Current model | Resolved model name |
| Last response source | `mock`, `llm_mock`, `llm_real`, `llm_real_error` |
| Fallback count today | Daily aggregate |

Standing disclaimer (always visible):
```
Usage estimates are approximate. Check your provider dashboard for exact billing.
```

Rules:
- Usage meter must not show the API key or any key fragment.
- Token estimates must be labeled as approximate.
- Provider dashboard is the authoritative billing source — link or reference should be shown.
- If usage meter is not yet implemented (TASK-050), show a placeholder: `Usage tracking not yet available. Check your provider dashboard for billing.`
- Usage meter display is always read-only.

### 2.7 Test Connection

Allows the user to manually test whether the configured provider is reachable and the API key is accepted. This is the only permitted trigger for a live provider call outside of chat.

| Element | Description |
|---|---|
| Test Connection button | Sends a minimal test request to the backend, which calls the provider. Never called automatically. |
| Pre-test warning | Shows the cost warning (Section 2.5) again before the test is confirmed. |
| Confirm test dialog | Requires the user to confirm: `This will send one test request to your provider. A small charge may apply. Continue?` |
| Test result indicator | Shows `Connected` (success), `Auth failed` (401), `Provider unreachable` (timeout / 5xx), or `Unknown error` — safe text only. |
| Last test timestamp | Read-only: shows when the last successful test was run. |

Rules:
- Test Connection must not fire automatically on page load, settings save, or provider switch.
- Only one test request per user action. No retry loop.
- Backend handles the actual provider call — frontend never calls provider directly.
- Response body from provider is never sent to frontend. Only a safe status enum is returned.
- Non-2xx provider responses are opaque — the backend returns only a safe error category to the UI.
- If no key is configured, Test Connection button should be disabled with label `Save a key first`.

---

## 3. Settings Flow

The following is the intended step-by-step interaction when a user sets up a real provider for the first time.

| Step | User Action | System Response |
|---|---|---|
| 1 | User opens Provider Settings panel | Panel loads. Current provider shown as `mock`. All safety toggles shown as-is. Usage meter shows session counters (or placeholder). |
| 2 | User selects `Anthropic` from provider dropdown | Cost warning appears immediately. Key input unlocks. Model input unlocks. |
| 3 | User types API key into key input field | Input is masked. No backend call yet. |
| 4 | User clicks Save Key | UI POSTs key to backend settings endpoint (TASK-048). Key is never stored in frontend. |
| 5 | Backend saves key (env / keychain) | Backend returns `{ "key_saved": true }`. UI shows `Key configured`. Input field is cleared. |
| 6 | User optionally selects a model | Model name sent to backend when saved. |
| 7 | User clicks Test Connection | Pre-test confirmation dialog shown (with cost warning). |
| 8 | User confirms test | Backend sends minimal test request to provider. No retry. |
| 9 | Result shown | `Connected` or safe error text. Timestamp recorded. |

After step 9, the user must still manually enable `LLM_PROVIDER_ENABLED` and `LLM_CHAT_ENABLED` flags to activate real provider for chat — the settings panel does not do this automatically in Phase 4.

---

## 4. Security Boundaries

| Boundary | Rule |
|---|---|
| No frontend key storage | API key must never be stored in any Electron renderer state, localStorage, or IPC message |
| No key in response | Backend settings endpoints must never return the key value — only `key_saved: true` / `key_exists: true` |
| No key in logs | Renderer logs, DevTools console, and Electron IPC logs must never contain the key |
| No automatic provider test | Test Connection must require explicit user action and confirmation dialog every time |
| No test on page load | Settings panel must not trigger any backend call to provider on render |
| No test on save | Saving a key must not trigger a provider test — test is a separate explicit action |
| Backend-mediated only | All key save, key clear, test connection, and flag read operations go through backend API |
| Non-2xx opaque | If provider test fails with non-2xx response, backend returns only a safe status enum — never the raw error body |
| No key in screenshots | If the UI is screenshotted or exported, no key value should appear |
| No key in crash reports | Any crash or error reporting must exclude key values and key-adjacent fields |
| No automatic retries | UI must not retry a failed provider test automatically |
| Confirmation before clear | Clearing a key must prompt a confirmation dialog before calling backend |

---

## 5. Error UX

All error messages shown to the user must use safe, non-technical language. Provider error bodies are never surfaced. The following error types must be handled:

| Error Type | Safe Message to User |
|---|---|
| Auth failed (401 / invalid key) | `API key not accepted. Check that your key is correct and still active on your provider account.` |
| Provider unreachable (timeout / 5xx) | `Provider is not reachable right now. Try again later or check your provider's status page.` |
| Rate limit hit (429) | `Provider returned a rate limit response. Wait a moment and try again.` |
| Key save failed (backend error) | `Could not save key. Please try again.` |
| Key clear failed (backend error) | `Could not clear key. Please try again.` |
| Model not recognized | `Model name not recognized. Check your provider's model list.` |
| Unknown error | `Something went wrong. Check the app and provider status, then try again.` |

Rules:
- Never show HTTP status codes in user-facing error text.
- Never show raw provider error response bodies.
- Never show internal Python tracebacks or stack traces.
- Never hint at the key value in error messages.

---

## 6. Memory Interaction Note

The Provider Settings panel does not control memory-aware chat. These remain independent:

- Configuring a real provider does NOT automatically enable memory injection.
- Memory injection still requires both `MEMORY_INJECTION_ENABLED=true` (backend flag) AND `use_memory=true` (per-request field).
- The settings panel may show the current `MEMORY_INJECTION_ENABLED` status in the Safety Toggles section (read-only).
- A note should appear near the usage meter: `Memory-aware chat may increase input tokens per turn.`
- Memory audit records must not store provider name, API key, or any usage meter data. MemoryInjectionAudit remains memory-scoped only.

---

## 7. Non-Goals

The following are explicitly out of scope for the TASK-047 design and Phase 4 implementation:

| Out of Scope | Reason |
|---|---|
| Interactive enable/disable of LLM flags from UI | Flags remain env-var controlled in Phase 4 |
| API key retrieval / display | Key is write-once from UI perspective — never retrieved |
| Multiple provider key management | Single active provider in Phase 4 |
| Dynamic model list fetching from provider | Static list only in MVP |
| Payment or billing integration | No payment flow |
| Automatic provider tests on save | All tests are explicitly user-initiated |
| Usage export or download | Deferred to later phase |
| Admin / multi-user settings | Single-user desktop app only |
| TTS or voice configuration | Deferred to Phase 5 |
| Streaming response configuration | Not in Phase 4 scope |
| Automatic retries on test failure | No retries in Phase 4 |

---

## 8. Future Implementation Sequence

| Task | Name | Type | Depends On |
|---|---|---|---|
| TASK-048 | Backend Provider Settings API Design | Design-only | TASK-047 |
| TASK-049 | Secure Key Storage Design | Design-only | TASK-048 |
| TASK-050 | Usage Meter Implementation | Implementation | TASK-049 |
| TASK-051 | Backend Provider Settings API Implementation | DONE | TASK-049, TASK-050 |
| TASK-052 | Provider Settings UI Implementation | DONE | TASK-051 |
| TASK-053 | Secure Key Storage Implementation | DONE | TASK-052 |
| TASK-054 | Provider Settings Key Endpoint Implementation | DONE | TASK-053 |
| TASK-055 | Provider Settings Key UI Enablement Design | IN_PROGRESS | TASK-054 |
| TASK-056 | Provider Settings Key UI Enablement Implementation | Pending | TASK-055 |
| TASK-057 | Provider Settings Key UI Smoke Check | Pending | TASK-056 |

The safe non-secret Provider Settings UI described in this document is implemented in TASK-052. No runtime code changes are made in TASK-047.

TASK-050 (Usage Meter Implementation) must be complete before TASK-051 (BYOK Settings Implementation) ships to users. A user who enables live provider calls should be able to see what they are spending immediately.

Key UI enablement (Save Key, Clear Key) is designed in TASK-055 and implemented in TASK-056. Test Connection remains disabled until TASK-058 (design) and TASK-059 (implementation).

---

## 9. Relationship to Existing Documents

| Document | Relationship |
|---|---|
| `docs/BYOK_PRODUCT_AND_SETTINGS.md` | Defines key ownership model, storage options, and BYOK product positioning. TASK-047 adds the concrete UI flow on top of those rules. |
| `docs/USAGE_METER_DESIGN.md` | Defines what to track and how. TASK-047 specifies the placement of the usage meter summary inside the Provider Settings panel. |
| `docs/LLM_ADAPTER_DESIGN.md` | Defines the backend adapter, feature flags, and security boundaries. The settings UI must respect all flag and redaction rules defined there. |
| `docs/COST_AND_MONETIZATION.md` | Defines cost control strategy and live smoke go/no-go criteria. Cost warnings in the settings UI must align with the warning UX defined there. |
| `docs/CHAT_LLM_REAL_PROVIDER_WIRING_DESIGN.md` | Defines the real-provider `/chat` wiring. Settings UI changes do not affect `/chat` routing or memory gate. |
