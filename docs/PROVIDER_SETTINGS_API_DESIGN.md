# Provider Settings API Design

> dragon-pet-ai
> Phase: 4 — LLM Adapter Integration
> Status: DESIGN COMPLETE (TASK-048 DONE); NON-SECRET API IMPLEMENTED (TASK-051 DONE); KEY STORAGE ABSTRACTION IN PROGRESS (TASK-053)
> Last Updated: 2026-05-20
> Owner: TASK-048
> Secure Key Storage Design: see `docs/SECURE_KEY_STORAGE_DESIGN.md` (TASK-049)

---

## 1. Purpose

The Backend Provider Settings API supports the future BYOK settings UI designed in TASK-047. It gives the frontend a safe, backend-mediated surface for configuring the LLM provider, storing the API key, querying provider status, and running a manual test connection.

Key principles:

- Frontend must never call providers directly. All provider operations are mediated by the backend.
- The API key is write-only. It must never appear in any response body, log line, or error message.
- Test connection is manual-only. No endpoint triggers a live provider call automatically.
- Provider status responses expose only safe, non-secret metadata.
- TASK-048 was design-only. TASK-051 implements the safe non-secret subset only.
- API key storage endpoints remain disabled placeholders until TASK-054.

---

## 2. Current Baseline

| Component | Status |
|---|---|
| Provider Settings UI design | DONE (TASK-047) — `docs/PROVIDER_SETTINGS_UI_DESIGN.md` |
| Backend Provider Settings API | Non-secret GET/PATCH implemented in TASK-051 |
| API key handling | Environment variable only during dev phase |
| Secure key storage | Abstraction implemented in TASK-053; key endpoints still disabled |
| Usage meter design | DONE (TASK-046) — `docs/USAGE_METER_DESIGN.md` |
| Usage meter runtime | In-memory safe aggregate implementation complete (TASK-050) |
| LLM provider factory | Exists in `backend/app` behind feature flags |
| Real provider | Disabled by default (`LLM_PROVIDER_ENABLED=false`) |
| Manual live smoke | Deferred until explicit user cost confirmation |

---

## 3. Proposed Endpoints

### 3.1 `GET /provider/settings`

**Purpose:** Return the current safe provider settings state. Used by the settings UI on load to display current configuration.

**TASK-051 runtime status:** Implemented for safe non-secret status and safe aggregate usage summary. It does not read `LLM_API_KEY`.

**Response fields:**

| Field | Type | Description |
|---|---|---|
| `provider` | str | Currently configured provider name: `mock`, `anthropic`, `openai` |
| `model` | str \| null | Currently configured model identifier, or null if not set |
| `real_provider_enabled` | bool | Whether `LLM_PROVIDER_ENABLED` is true |
| `llm_chat_enabled` | bool | Whether `LLM_CHAT_ENABLED` is true |
| `fallback_to_mock` | bool | Whether `LLM_FALLBACK_TO_MOCK` is true |
| `key_status` | str | One of: `not_configured`, `configured`, `invalid`, `not_tested` |
| `resolved_provider` | str | Effective resolved provider name: `mock`, `anthropic`, `unknown` |
| `last_test_status` | str | One of: `success`, `failed`, `not_tested` |
| `usage_summary` | dict \| null | Optional safe usage summary (see Section 7) |

**Must not return:**

- API key value
- Partial API key or key fragments
- Raw provider diagnostics or internal error messages
- Raw provider response body
- Any field whose value could be used to reconstruct the key

---

### 3.2 `PATCH /provider/settings`

**Purpose:** Update safe, non-secret provider settings. Does not accept or touch the API key.

**TASK-051 runtime status:** Implemented for non-secret in-memory settings only. Unsupported fields such as `api_key`, `key`, `prompt`, and `memory_context` are rejected with a fixed safe error that does not echo submitted values.

**Allowed request fields:**

| Field | Type | Description |
|---|---|---|
| `provider` | str | Provider selection: `mock`, `anthropic`, `openai` |
| `model` | str \| null | Model identifier to use, or null to clear |
| `real_provider_enabled` | bool | Enable or disable real provider |
| `llm_chat_enabled` | bool | Enable or disable LLM chat wiring |
| `fallback_to_mock` | bool | Whether to fall back to mock on provider failure |

**Response:** Updated settings state in the same shape as `GET /provider/settings`.

**Must not accept:**

- API key — key changes go to `POST /provider/settings/key` only
- Raw prompt text
- Memory content
- Provider raw response

**Rules:**

- Changing `provider` to a real provider does not trigger a provider test.
- Changing `real_provider_enabled` to `true` requires a key to be already configured; if no key is present, backend returns a safe error (`missing_key`).
- No live provider call happens as a side effect of `PATCH`.

---

### 3.3 `POST /provider/settings/key`

**Purpose:** Save or update the API key for the configured provider. This is the only endpoint that accepts a key value.

**TASK-051/TASK-053 runtime status:** Disabled placeholder returning `501 not_implemented`. TASK-053 adds the storage abstraction only; this endpoint remains disabled until TASK-054 Provider Settings Key Endpoint Implementation.

**Request fields:**

| Field | Type | Description |
|---|---|---|
| `provider` | str | Provider the key belongs to: `anthropic`, `openai` |
| `api_key` | str | The API key value (write-only) |

**Response fields:**

| Field | Type | Description |
|---|---|---|
| `key_status` | str | `configured` on success; `invalid` if rejected by validation |
| `provider` | str | Provider the key was saved for |
| `message` | str | Safe informational text only — no key fragments |

**API key write-only rules:**

- The `api_key` field is accepted in the request body.
- The key value must never appear in any response field.
- The key must never appear in any log line at any level (DEBUG, INFO, WARNING, ERROR).
- The key must never be stored in plain SQLite. Storage method is determined by TASK-049 Secure Key Storage Design — recommended path is OS keychain / Credential Manager. See `docs/SECURE_KEY_STORAGE_DESIGN.md` for the full comparison and recommendation.
- Plain SQLite storage is explicitly forbidden for real API keys. Any column that would store the key unencrypted violates the security boundaries defined in TASK-048 and TASK-049.
- Persistent key endpoints remain disabled until TASK-054. TASK-053 provides only the storage abstraction and tests.
- The key must never appear in any Python `repr()` or `str()` of any object that holds it.
- If validation of the key format fails (e.g. wrong prefix), return `key_status: invalid` with a safe message. Do not echo back the key or any fragment.
- Future implementation must not begin until TASK-049 is complete.

---

### 3.4 `DELETE /provider/settings/key`

**Purpose:** Clear the stored API key for the configured provider. After deletion, real provider calls cannot be made until a new key is provided.

**TASK-051/TASK-053 runtime status:** Disabled placeholder returning `501 not_implemented`. TASK-053 adds the storage abstraction only; this endpoint remains disabled until TASK-054 Provider Settings Key Endpoint Implementation.

**Request:** No body required. Provider may be specified as a query parameter or path segment.

**Response fields:**

| Field | Type | Description |
|---|---|---|
| `key_status` | str | Always `not_configured` on success |
| `provider` | str | Provider the key was cleared for |
| `message` | str | Safe informational text: e.g. `Key cleared. Provider will fall back to mock mode.` |

**Rules:**

- Clearing a key immediately returns the resolved provider to mock (or safe fallback).
- Backend must confirm deletion before returning success.
- If no key exists, return success (idempotent) with `key_status: not_configured`.

---

### 3.5 `POST /provider/settings/test`

**Purpose:** Execute a single minimal test request to the configured provider. This is the only endpoint that may trigger a live provider call outside of `/chat`. It requires explicit user action and an explicit cost acknowledgement.

**TASK-051 runtime status:** Disabled placeholder returning `501 not_implemented`. It does not call external providers and must remain disabled until key storage and live-test safety are implemented.

**Request fields:**

| Field | Type | Description |
|---|---|---|
| `provider` | str | Provider to test: `anthropic`, `openai` |
| `model` | str \| null | Optional model override. Defaults to configured model. |
| `explicit_cost_ack` | bool | Must be `true`. Backend rejects if `false` or absent. |
| `test_message` | str \| null | Optional minimal test message. Defaults to a fixed safe phrase. |

**Response fields:**

| Field | Type | Description |
|---|---|---|
| `status` | str | `success`, `failed`, or `fallback_used` |
| `provider` | str | Provider that was tested |
| `model` | str \| null | Model used for the test |
| `source` | str | `llm_real`, `llm_real_error`, `mock` |
| `safe_message` | str | Safe informational text — no raw provider content |
| `error_category` | str \| null | Safe error category if failed (see Section 8) |
| `usage_estimate` | dict \| null | Optional safe usage estimate: `{ input_tokens, output_tokens, estimated_cost_usd }` |

**Must not return:**

- Raw provider response body
- Raw provider error message or stack trace
- API key or any key fragment
- Internal Python error details

**Test connection safety rules:**

- `explicit_cost_ack: true` is mandatory. If absent or false, return HTTP 400 with safe error `cost_ack_required`.
- Exactly one minimal request is sent. No retry loop.
- No memory context is injected.
- No tools are used.
- No streaming response.
- Does not write to chat history.
- Does not create a `MemoryInjectionAudit` row.
- Does not trigger automatic re-test on failure.
- No test is triggered on app start, settings page load, or key save.
- If `LLM_PROVIDER_ENABLED=false`, the endpoint returns a safe error `provider_disabled` without attempting a call.
- If no key is configured, the endpoint returns `missing_key` without attempting a call.

---

## 4. API Key Handling Rules

The following rules apply to every endpoint in this API and to any future implementation:

| Rule | Detail |
|---|---|
| Write-only | API key is accepted as input only — never returned |
| Never logged | Key must not appear in any log line at any severity level |
| Never in responses | Key must not appear in any response body, header, or error message |
| Never in memory records | Key must not be stored in `Memory` table or `MemoryInjectionAudit` table |
| Never in chat history | Key must not appear in any `Message` or `ConversationTurn` record |
| Never in repr/str | Any object holding the key must redact it in `__repr__` and `__str__` |
| Never in plain SQLite | Key must not be stored unencrypted — storage requires TASK-049 Secure Key Storage Design |
| Redacted in errors | Any error path that touches the key must redact it before logging or returning |
| Clear available | A `DELETE /provider/settings/key` endpoint must always be available |
| Idempotent clear | Clearing a non-existent key returns success (`not_configured`) |

---

## 5. Safe Status Model

The `key_status` field uses the following canonical values:

| Value | Meaning |
|---|---|
| `not_configured` | No API key has been stored for this provider |
| `configured` | A key has been stored; it has not been tested or tested successfully |
| `invalid` | The key failed format validation on save, or the provider rejected it (401) |
| `not_tested` | A key is stored but no test has been run |
| `test_success` | Last test connection returned a 2xx response |
| `test_failed` | Last test connection returned an error (timeout, non-2xx, etc.) |

The `last_test_status` field is a simplified subset: `success`, `failed`, `not_tested`.

Rules:
- These status values must never expose the key value or key fragments.
- `configured` does not imply the key is valid — only that it has been stored.
- `invalid` may be set either at save time (format check) or after a failed test (auth error).

---

## 6. Test Connection Safety

The following rules govern all behavior related to `POST /provider/settings/test`:

- Test connection is **manual-only**. No endpoint, background task, or startup hook may trigger it automatically.
- No automatic test on app start.
- No automatic test when settings page loads.
- No automatic test when a key is saved.
- No repeated test loop. Backend enforces single-request-per-call.
- Cost warning must be shown in the UI before the user submits the test request (enforced by UI design in TASK-047).
- Backend enforces `explicit_cost_ack: true` as a hard requirement — this is a second layer of safety beyond UI-only warnings.
- Test response body is always sanitized before returning to frontend. Raw provider body is never forwarded.
- Non-2xx provider responses are opaque: backend returns only a safe `error_category` and `safe_message`.
- Test result does not mutate `/chat` behavior, memory state, or audit logs.
- Usage meter may be incremented if a real provider call was made (see Section 7).

---

## 7. Usage Meter Integration

When `POST /provider/settings/test` triggers a real provider call, the usage meter should record the following:

| Field | Value |
|---|---|
| `request_count` | +1 |
| `provider` | Tested provider name |
| `model` | Model used for test |
| `source` | `llm_real`, `llm_real_error`, or `mock` |
| `estimated_input_tokens` | From provider-reported usage if available; local heuristic otherwise |
| `estimated_output_tokens` | From provider-reported usage if available |
| `fallback_used` | True if real provider failed and mock was used |
| `error_category` | Safe error category if failed |

**Must not record:**

- API key value
- Raw prompt or test message content
- Raw provider response body
- Full user message text

Usage records from test connection are tagged identically to chat turn records. The usage meter does not distinguish test requests from chat requests in the current design — both count toward the session and daily totals.

---

## 8. Error Handling

All errors returned by provider settings endpoints must use safe, non-technical language. Raw provider error bodies are never forwarded.

| Error Category | Safe Message to Frontend |
|---|---|
| `missing_key` | `No API key is configured for this provider.` |
| `invalid_key` | `API key not accepted. Check that your key is correct and still active.` |
| `provider_disabled` | `Real provider is not enabled. Check your configuration flags.` |
| `cost_ack_required` | `Explicit cost acknowledgement is required to run a provider test.` |
| `timeout` | `Provider did not respond in time. Try again later.` |
| `rate_limit` | `Provider returned a rate limit response. Wait a moment and try again.` |
| `provider_unavailable` | `Provider is not reachable right now. Check your provider's status page.` |
| `invalid_response` | `Provider returned an unexpected response. Try again later.` |
| `fallback_used` | `Real provider failed. Mock fallback was used.` |
| `key_save_failed` | `Could not save key. Please try again.` |
| `key_clear_failed` | `Could not clear key. Please try again.` |

Rules:
- Never include HTTP status codes in error messages returned to frontend.
- Never include raw provider response body.
- Never include Python stack traces.
- Never hint at key value in error messages.
- `error_category` field uses the snake_case identifier; `safe_message` uses human-readable text.

---

## 9. Security Boundaries

| Boundary | Rule |
|---|---|
| No API key in response | No endpoint returns the key value in any field |
| No API key in logs | Backend must redact key from all log lines at all levels |
| No API key in DB unless secure | Key must not be stored unencrypted — requires TASK-049 design approval |
| No raw provider body in response | Non-2xx responses from provider are opaque; only safe status and category are returned |
| No raw provider body in logs | Provider error bodies must not be logged even at DEBUG level |
| No raw prompt in response | Test connection prompt/message is not echoed back |
| No raw prompt in logs | Test message content must not appear in log lines |
| No user_message in logs | User message content must not be logged via any settings endpoint |
| No memory context in logs | No memory content is used in test connection |
| No automatic live calls | No endpoint triggers a provider call without explicit user action |
| No background provider polling | No scheduled or periodic provider health check |
| No test on settings page load | `GET /provider/settings` must not trigger any provider call |
| No implicit key exposure | `key_status` values must not be constructable into the key value |

---

## 10. Non-Goals

The following are explicitly out of scope for TASK-048 and Phase 4:

| Out of Scope | Reason |
|---|---|
| Runtime implementation of these endpoints | Deferred to TASK-051 |
| Secure key storage implementation | Separate design task TASK-049 |
| Frontend UI implementation | Separate task TASK-052 |
| Live provider call in this task | Design-only; no API calls made |
| Payment or billing integration | Not in Phase 4 scope |
| Hosted account management | Not in Phase 4 scope |
| Multi-user or multi-tenant key management | Single-user desktop app only |
| Automatic key rotation | Not in Phase 4 scope |
| Provider health polling | No background automatic calls |
| Dynamic model list fetching from provider | Static or user-defined model name only |
| Streaming test response | Not in Phase 4 scope |

---

## 11. Future Implementation Sequence

| Task | Name | Type | Depends On |
|---|---|---|---|
| TASK-049 | Secure Key Storage Design | Design-only | TASK-048 |
| TASK-050 | Usage Meter Implementation | Implementation | TASK-049 |
| TASK-051 | Backend Provider Settings API Implementation | Implementation | TASK-049, TASK-050 |
| TASK-052 | Provider Settings UI Implementation | Implementation | TASK-051 |
| TASK-053 | Secure Key Storage Implementation | Implementation | TASK-052 |
| TASK-054 | Provider Settings Key Endpoint Implementation | Implementation | TASK-053 |
| TASK-055 | BYOK Runtime Smoke Check | Validation | TASK-054 |

`POST /provider/settings/key` implementation must not begin until TASK-049 (Secure Key Storage Design) is complete, because the storage backend for the key is not yet determined.

`TASK-051` (Backend implementation) must not begin until `TASK-050` (Usage Meter Implementation) is ready, because the test connection endpoint must be able to record usage at the moment of the first live call.

---

## 12. Relationship to Existing Documents

| Document | Relationship |
|---|---|
| `docs/PROVIDER_SETTINGS_UI_DESIGN.md` | Defines the frontend surface that this API supports. UI rules (no direct provider call, key write-only, confirmation dialogs) are enforced on the backend side here. |
| `docs/BYOK_PRODUCT_AND_SETTINGS.md` | Defines key ownership model, storage options, and BYOK product positioning. This API design implements the backend side of those rules. |
| `docs/USAGE_METER_DESIGN.md` | Defines what to track. Section 7 of this document specifies how test connection integrates with usage meter. |
| `docs/LLM_ADAPTER_DESIGN.md` | Defines the provider factory, feature flags, and redaction utility. The settings API must use the same factory and redaction rules. |
| `docs/COST_AND_MONETIZATION.md` | Defines cost control strategy. `explicit_cost_ack` enforcement on test connection aligns with the live smoke go/no-go criteria. |
