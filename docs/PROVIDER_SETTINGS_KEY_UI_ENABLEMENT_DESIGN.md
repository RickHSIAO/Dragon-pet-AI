# Provider Settings Key UI Enablement Design

> dragon-pet-ai
> Phase: 4 — LLM Adapter Integration
> Status: DESIGN COMPLETE (TASK-055 DONE); IMPLEMENTATION DONE (TASK-056); SMOKE PASS (TASK-057); TEST CONNECTION DESIGN DONE (TASK-058); BACKEND TEST CONNECTION IN_PROGRESS (TASK-059)
> Last Updated: 2026-05-20
> Owner: TASK-055
> Depends on: TASK-054 (key save/clear backend endpoints wired to key storage abstraction)
> Parent UI Design: see `docs/PROVIDER_SETTINGS_UI_DESIGN.md` (TASK-047)
> Parent API Design: see `docs/PROVIDER_SETTINGS_API_DESIGN.md` (TASK-048)
> Key Storage Design: see `docs/SECURE_KEY_STORAGE_DESIGN.md` (TASK-049)

---

## 1. Purpose

This document defines how the Provider Settings UI will expose the API key save and clear controls now that the backend key endpoints are wired to the key storage abstraction.

TASK-052 implemented the Provider Settings UI but left API key save, key clear, and Test Connection as disabled placeholders — pending the backend key storage abstraction (TASK-053) and key endpoint wiring (TASK-054). Both are now complete. This document designs the safe enablement of the key UI controls only.

Key principles carried forward from TASK-047:

- API key must never appear in any frontend state, renderer log, Electron IPC message, or DevTools console.
- The UI sends the key to the local backend only — never to an external provider.
- After save, the input field is cleared. The key is never displayed again through the UI.
- Clear Key requires a confirmation dialog. It is idempotent.
- Test Connection remains disabled in runtime. Its explicit cost acknowledgement flow is documented separately in TASK-058.

This task is design-only. No runtime code is written and no Electron UI is modified.

---

## 2. Current State After TASK-054

| Component | Status |
|---|---|
| Provider Settings UI | Implemented (TASK-052); key controls are disabled placeholders |
| `GET /provider/settings` | Implemented — returns safe `key_status` only, never key value |
| `PATCH /provider/settings` | Implemented — non-secret settings only, rejects key fields |
| `POST /provider/settings/key` | Implemented (TASK-054) — wired to key storage abstraction; runtime storage is `UnavailableKeyStorageBackend` (safe 503 default) |
| `DELETE /provider/settings/key` | Implemented (TASK-054) — wired to key storage abstraction; idempotent |
| `POST /provider/settings/test` | Disabled placeholder returning `501 not_implemented` — unchanged |
| Key storage backend (runtime) | `UnavailableKeyStorageBackend` — fails safely with no key exposure |
| Key storage backend (tests) | `InMemoryKeyStorageBackend` — tests only |
| pytest result | 449 passed |

The UI enablement designed here must respect the current runtime behavior: saving a key through the UI will fail safely (503) in the default environment. The UI must communicate this to the user with a safe message and must not retry or bypass the backend.

---

## 3. Save Key UI Design

### 3.1 Control Layout

| Element | Behavior |
|---|---|
| API key input field | Password-masked (`type="password"`). Placeholder text: `Paste your API key here`. Never shows key value after save. |
| Save Key button | Enabled only when: provider is a real provider (not mock), key input is non-empty, and provider is selected. Disabled otherwise. |
| Key status indicator | Read-only label. Shows one of the 6 canonical values from Section 6. Never shows key value or key fragment. |

### 3.2 Save Key Interaction Flow

| Step | Action | System Response |
|---|---|---|
| 1 | User selects a real provider (e.g. `anthropic`) | Cost warning appears. API key input unlocks. Save Key button activates when non-empty. |
| 2 | User types or pastes API key | Input is masked. No backend call occurs yet. |
| 3 | User clicks Save Key | UI sends `POST /provider/settings/key` with `{ "provider": "anthropic", "api_key": "<value>" }` to local backend. |
| 4a | Backend returns success | `{ "key_status": "configured", "provider": "anthropic", "message": "Key saved." }` → UI clears input field, updates key status indicator to `Key configured`. |
| 4b | Backend returns 503 (storage unavailable) | UI shows safe message: `Secure key storage is unavailable in this environment. Use an environment variable to set your API key for now.` Input field is cleared. Save Key button is re-enabled after a short delay. |
| 4c | Backend returns 400 (invalid key format) | UI shows safe message: `API key not accepted. Check that your key is correct and still active on your provider account.` Input field is cleared. |
| 4d | Backend is unreachable | UI shows safe message: `Could not reach backend. Make sure the backend is running.` |

### 3.3 Save Key Disabled States

Save Key must be disabled when:

| Condition | Label |
|---|---|
| Provider is mock | `Not required for mock provider` |
| Key input is empty | (button disabled, no label change) |
| Save is in progress | `Saving…` (button disabled during request) |
| Key storage is known unavailable (after a prior 503) | `Storage unavailable — use env var` |

### 3.4 Save Key Security Rules

- API key is submitted in the POST body to the local backend only.
- The key value is never stored in any Electron renderer state variable.
- The key value is never assigned to any DOM attribute beyond the `value` property of the password input field.
- The key value is never sent to any Electron IPC channel.
- The key value is never written to `localStorage` or `sessionStorage`.
- After the POST response is received (success or failure), the input field's `value` property is set to an empty string immediately.
- No `console.log`, `console.warn`, or `console.error` call may include the key value.
- The key must not appear in renderer DevTools, network logs, or any exported state.

---

## 4. Clear Key UI Design

### 4.1 Control Layout

| Element | Behavior |
|---|---|
| Clear Key button | Visible only when `key_status` is `configured`, `invalid`, `not_tested`, `test_success`, or `test_failed` — i.e., any state where a key exists. Hidden (not just disabled) when `key_status` is `not_configured`. |
| Confirmation dialog | Required before calling backend. Text: `This will permanently delete your stored API key. The provider will revert to mock mode. Continue?` Two buttons: `Cancel` and `Clear Key`. |

### 4.2 Clear Key Interaction Flow

| Step | Action | System Response |
|---|---|---|
| 1 | User clicks Clear Key | Confirmation dialog appears. No backend call yet. |
| 2a | User clicks Cancel | Dialog closes. No change. |
| 2b | User clicks Confirm (Clear Key) | UI sends `DELETE /provider/settings/key?provider=<provider>` to local backend. |
| 3a | Backend returns success | `{ "key_status": "not_configured", ... }` → UI updates key status indicator to `No key saved`. Clear Key button is hidden. |
| 3b | Backend returns 503 (storage unavailable) | UI shows safe message: `Could not clear key. Secure key storage is unavailable in this environment.` |
| 3c | Backend is unreachable | UI shows safe message: `Could not reach backend. Make sure the backend is running.` |

### 4.3 Clear Key Security Rules

- Clear Key never displays the stored key at any point.
- The confirmation dialog never shows key value, key fragment, or masked key.
- Clear Key is idempotent — if the backend returns `not_configured`, the UI treats this as success.
- After clearing, the resolved provider falls back to mock mode. The UI must reflect this by updating the resolved provider display.
- No retry loop. If clearing fails, the user may try again manually.

---

## 5. Unavailable Storage UX

The default runtime storage backend is `UnavailableKeyStorageBackend`. Any attempt to save or clear a key will return HTTP 503. The UI must handle this gracefully.

### 5.1 Unavailable Storage Safe Message

When a 503 is received from `POST /provider/settings/key` or `DELETE /provider/settings/key`:

```
Secure key storage is unavailable in this environment.
To use a real provider, set your API key as an environment variable before starting the backend:

  Windows:    set ANTHROPIC_API_KEY=<your-key>
  macOS/Linux: export ANTHROPIC_API_KEY=<your-key>

Then restart the backend and enable LLM_PROVIDER_ENABLED.
```

### 5.2 Unavailable Storage Behavior Rules

- The UI must not retry the save/clear request automatically on 503.
- The Save Key button is re-enabled after 503 so the user can try again after reconfiguring their environment.
- The key status indicator remains unchanged after a failed save — it reflects the last known state from `GET /provider/settings`.
- The UI must not suggest alternative storage paths not supported by the backend (e.g., it must not ask the user to enter a path to a keychain manually).

---

## 6. Key Status Display

The `key_status` field returned by `GET /provider/settings` uses the following canonical values. The UI must translate these to human-readable labels.

| `key_status` value | UI Display Label | Interpretation |
|---|---|---|
| `not_configured` | `No key saved` | No key has been stored. Save Key is enabled (if real provider selected). |
| `configured` | `Key configured` | A key has been stored. It has not yet been tested. |
| `not_tested` | `Key saved, not tested` | A key is stored but no test has been run. (Equivalent to `configured` for UI purposes.) |
| `invalid` | `Key invalid or rejected` | Key failed format validation or was rejected by provider. |
| `test_success` | `Key tested — OK` | Last test connection succeeded. |
| `test_failed` | `Key tested — failed` | Last test connection returned an error. |

Rules:

- Key status labels must never include the key value or any fragment of it.
- Key status labels must never include provider-internal error codes or HTTP status codes.
- Key status must be refreshed after every successful save, clear, or settings load.
- The UI must not infer or guess key status from any local state — it must always read from the backend `GET /provider/settings` response.

---

## 7. Test Connection (Remains Disabled)

Test Connection (`POST /provider/settings/test`) remains disabled in runtime. The backend placeholder returns `501 not_implemented`. The future Test Connection flow is now designed separately in `docs/PROVIDER_TEST_CONNECTION_DESIGN.md`.

The UI behavior for Test Connection must remain:

- Button disabled with label: `Test Connection (not yet available)`.
- No click handler or backend call is wired.
- No live provider call occurs from this button.
- Save Key and Clear Key must not trigger Test Connection automatically.
- The pre-test cost warning from Section 2.5 of `PROVIDER_SETTINGS_UI_DESIGN.md` is not shown until the button is enabled.

Test Connection enablement is deferred to TASK-058 (design) and TASK-059 (implementation). Enablement requires:

- `explicit_cost_ack: true` support in the backend (already designed in TASK-048).
- Frontend confirmation dialog with cost warning.
- A go/no-go decision on live provider calling.

---

## 8. Security Boundaries

The following security boundaries apply to the key UI. These extend the boundaries defined in Section 4 of `PROVIDER_SETTINGS_UI_DESIGN.md`.

| Boundary | Rule |
|---|---|
| No key in renderer state | Key value must not be assigned to any JavaScript variable beyond the live password input `value` property |
| No key in Electron IPC | No `ipcRenderer.send` or `contextBridge` call may include the key value |
| No key in renderer logs | No `console.*` call may print the key value |
| No key in localStorage | Key must never be written to `localStorage`, `sessionStorage`, or any browser storage API |
| No key in screenshots | If the UI is screenshotted while the key is in the input field, the browser default password masking must obscure it |
| No key in DevTools | Inspecting renderer DOM or network tab must not reveal the key value; the key is submitted once as POST body to localhost and then cleared |
| No key in memory audit | `MemoryInjectionAudit` rows must never contain provider name paired with key status transitions |
| No key in usage records | `UsageMeter` records must never contain the key value or any field that could reconstruct it |
| No key in chat history | `Message` and `ConversationTurn` records must not contain key values |
| No key in crash reports | Any renderer crash report must not include key input field values |
| Local backend only | The renderer must only call `localhost` (or `127.0.0.1`) endpoints — never call an external provider URL |
| No external provider URLs in renderer | No Anthropic, OpenAI, or other provider base URL may appear in renderer code for key submission |

---

## 9. Error UX

All error messages shown to the user must use safe, non-technical language. The following error types must be handled by the key UI:

| Trigger | Safe Message to User |
|---|---|
| 503 from save/clear (storage unavailable) | `Secure key storage is unavailable in this environment. Use an environment variable to set your API key for now.` |
| 400 from save (invalid provider) | `Unknown provider. Select a supported provider before saving a key.` |
| 400 from save (empty key) | `API key cannot be empty.` |
| Backend unreachable (network error / CORS / offline) | `Could not reach backend. Make sure the backend is running on localhost.` |
| 500 from save | `Could not save key. Please try again.` |
| 500 from clear | `Could not clear key. Please try again.` |
| 404 from delete (key not found) | Treated as success — display `No key saved`. Delete is idempotent. |

Rules:

- Never show HTTP status codes in user-facing error text.
- Never show raw backend error response bodies.
- Never show Python tracebacks or internal error details.
- Never hint at the key value in error messages.
- Error messages must be shown in a non-blocking inline notice near the relevant control, not as a modal (except for the confirmation dialog before clear).

---

## 10. Non-Goals

The following are explicitly out of scope for TASK-055:

| Out of Scope | Reason |
|---|---|
| Runtime implementation of key UI controls | Deferred to TASK-056 |
| Live Test Connection | Deferred to TASK-058 (design) and TASK-059 (implementation) |
| Enabling `POST /provider/settings/test` | Backend placeholder remains `501 not_implemented` |
| OS keychain dependency changes | `KeyringKeyStorageBackend` remains optional; runtime default stays `UnavailableKeyStorageBackend` |
| Payment or billing integration | Out of scope for Phase 4 |
| External provider API calls | No direct provider calls from frontend — ever |
| Multi-provider key management | Single active provider in Phase 4 |
| TTS or voice configuration | Deferred to Phase 5 |
| Automatic provider tests on save | All tests are explicitly user-initiated |
| Automatic retries on failed save/clear | No retry loop in Phase 4 |
| Dynamic model list fetching | Static model list only in MVP |
| Usage export or download | Deferred to later phase |
| Admin or multi-user settings | Single-user desktop app only |

---

## 11. Future Implementation Sequence

| Task | Name | Type | Depends On |
|---|---|---|---|
| TASK-055 | Provider Settings Key UI Enablement Design | Design-only | TASK-054 |
| TASK-056 | Provider Settings Key UI Enablement Implementation | Implementation | TASK-055 |
| TASK-057 | Provider Settings Key UI Smoke Check | Smoke check | TASK-056 |
| TASK-058 | Provider Test Connection Design | Design-only | TASK-057 |
| TASK-059 | Provider Test Connection Backend Implementation | Implementation | TASK-058 |
| TASK-060 | Provider Test Connection UI Enablement | Implementation | TASK-059 |
| TASK-061 | Provider Test Connection Runtime Smoke Check | Manual smoke | TASK-060 |

TASK-056 will modify the Electron renderer to:
- Enable Save Key button for real providers.
- Wire Save Key to `POST /provider/settings/key`.
- Clear input field after save (success or failure).
- Show unavailable storage safe message on 503.
- Enable Clear Key button when key exists.
- Wire Clear Key to `DELETE /provider/settings/key` with confirmation dialog.
- Refresh key status after save and clear.

TASK-057 will perform a manual runtime smoke check on the local dev machine:
- Verify Save Key shows safe error (503) with `UnavailableKeyStorageBackend`.
- Verify Clear Key shows safe error (503) with `UnavailableKeyStorageBackend`.
- Verify input field is cleared after each attempt.
- Verify key status indicator remains unchanged after failed save.
- Verify no key value appears in renderer logs or DevTools.
- Verify `/chat` remains functional and unchanged throughout.

TASK-058 will design Test Connection enablement, including:
- Frontend confirmation dialog flow with cost warning.
- `explicit_cost_ack: true` wire-up.
- Backend response handling for test result display.
- Go/no-go criteria for enabling live provider calls.

---

## 12. Relationship to Existing Documents

Test Connection is now designed separately in `docs/PROVIDER_TEST_CONNECTION_DESIGN.md`; Save Key and Clear Key must not trigger that flow automatically.

| Document | Relationship |
|---|---|
| `docs/PROVIDER_SETTINGS_UI_DESIGN.md` (TASK-047) | Parent UI design. This document adds the key UI interaction layer on top of the Section 2.2 (API Key Input) design. |
| `docs/PROVIDER_SETTINGS_API_DESIGN.md` (TASK-048) | Defines the backend endpoints this UI calls. Section 3.3 (POST key), Section 3.4 (DELETE key), and Section 3.5 (test — disabled) are the relevant endpoints. |
| `docs/SECURE_KEY_STORAGE_DESIGN.md` (TASK-049) | Defines the key storage abstraction, safe behaviors, and redaction rules. The UX for storage unavailability in this document follows those rules. |
| `docs/BYOK_PRODUCT_AND_SETTINGS.md` (TASK-045) | Defines key ownership model and BYOK product positioning. Cost warnings and env-var dev mode recommendation in this document align with that design. |
| `docs/COST_AND_MONETIZATION.md` (TASK-044) | Defines live smoke go/no-go criteria. Test Connection remains gated behind those criteria. |
