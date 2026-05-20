# Provider Test Connection Design

> dragon-pet-ai
> Phase: 4 - LLM Adapter Integration
> Status: DESIGN COMPLETE (TASK-058 DONE); BACKEND IMPLEMENTATION IN_PROGRESS (TASK-059)
> Last Updated: 2026-05-20
> Owner: TASK-058

---

## Purpose

Test Connection lets the user manually verify a configured BYOK provider.

It may incur provider cost, so it must never run automatically. It must be one
minimal request only, initiated by an explicit user action after a cost
acknowledgement. This document is design-only; no runtime code is implemented
and no live provider call is made in TASK-058.

---

## Current Baseline

- Save Key and Clear Key UI exists.
- Key storage abstraction exists.
- `POST /provider/settings/key` and `DELETE /provider/settings/key` are wired to key storage.
- Test Connection button remains disabled in the Electron renderer.
- `POST /provider/settings/test` is implemented backend-side in TASK-059 with mocked-provider tests only.
- Runtime default provider test runner does not call external providers.
- Real provider remains disabled by default.
- Manual live smoke remains deferred until explicit user cost confirmation.

---

## Preconditions

Test Connection can only be enabled when all of these are true:

- Provider is a real provider, not `mock`.
- `key_status` is `configured`.
- `real_provider_enabled` is `true`.
- User checks explicit cost acknowledgement for this click.
- Backend key storage is available.
- Provider and model are selected.
- App/backend can reach the provider network.

Do not enable Test Connection when:

- Provider is `mock`.
- `key_status` is `not_configured`.
- Key storage is unavailable.
- Real provider is disabled.
- User has not acknowledged cost.
- Model is missing when the selected provider requires one.

---

## explicit_cost_ack

The UI must show a cost warning before every Test Connection attempt.

The user must explicitly check a checkbox or confirm a dialog for each click.
The backend must require `explicit_cost_ack: true`; missing or false values
return a safe HTTP 400 error with category `cost_ack_required`.

Acknowledgement is per-click, not permanent. Saving a key, loading the settings
page, or selecting a provider must not count as cost acknowledgement.

---

## Exactly One Minimal Request

Rules for the future implementation:

- Send one provider request only.
- No retries.
- No streaming.
- No tools.
- No memory context.
- No conversation history.
- Use a fixed minimal prompt such as `Reply with OK.`
- Use a low `max_tokens` cap, for example 8 to 20.
- Enforce timeout.
- No background polling.
- No automatic test after Save Key.
- No automatic test on app startup or settings refresh.

---

## Request Contract

Future endpoint:

```http
POST /provider/settings/test
```

Request fields:

| Field | Type | Required | Notes |
|---|---:|---:|---|
| `provider` | str | yes | Real provider only, such as `anthropic` |
| `model` | str or null | no | Optional override; backend may use configured model |
| `explicit_cost_ack` | bool | yes | Must be `true` |

The request body must not include:

- `api_key`
- `key`
- `memory_context`
- raw prompt override
- user chat history
- system prompt
- tool definitions

Backend uses the stored key internally only. The frontend must never submit the
key to the test endpoint.

---

## Safe Response Model

Response fields:

| Field | Type | Notes |
|---|---:|---|
| `status` | str | `success` or `failed` |
| `provider` | str | Safe provider name |
| `model` | str or null | Safe model name |
| `source` | str | `llm_real` on success; `llm_real_error` on provider failure |
| `safe_message` | str | User-safe status text |
| `error_category` | str or null | Safe category on failure |
| `usage_estimate` | dict or null | Safe aggregate estimate only |

Must not return:

- API key or any key fragment
- raw provider response body
- raw provider error body
- request headers
- prompt text
- system prompt
- token-by-token content
- provider diagnostics
- stack traces

---

## Failure Behavior

Safe error categories:

| Category | Meaning |
|---|---|
| `cost_ack_required` | User did not explicitly accept cost for this click |
| `missing_key` | No configured key exists for the provider |
| `storage_unavailable` | Backend key storage cannot retrieve the key |
| `provider_disabled` | Real provider use is disabled |
| `invalid_provider` | Provider is mock or unsupported |
| `invalid_model` | Model is missing or unsupported |
| `provider_auth_error` | Provider rejected authentication |
| `rate_limit` | Provider returned rate limit |
| `provider_timeout` | Provider request timed out |
| `provider_unavailable` | Network/provider unavailable |
| `invalid_response` | Provider response was malformed or empty |
| `provider_error` | Generic provider failure |

No raw provider body, raw exception, API key, prompt, or internal traceback may
be returned to the frontend or written to logs.

---

## Fallback Policy

Recommended policy: no fallback for Test Connection.

Test Connection is meant to verify the real provider. If the real provider
fails, return `status: failed` with a safe `error_category`. Do not silently
fallback to mock because that would mislead the user into believing the real
provider works.

`llm_mock` should not be used for a real provider Test Connection result unless
a future task explicitly designs a separate mock-only test mode.

---

## Usage Meter Integration

If a real provider request is made, record safe aggregate usage metadata:

- increment `request_count`
- record provider
- record model
- record source
- record estimated input tokens
- record estimated output tokens
- record `error_category` if failed
- record `fallback_used=false`
- record `memory_used=false`

Do not record:

- API key
- raw prompt
- raw provider body
- raw response content
- user message
- memory context
- conversation history

---

## UI Behavior

Test Connection UI should:

- remain disabled until TASK-059 implementation.
- show a provider cost warning.
- require an explicit checkbox or confirmation dialog.
- show loading state during the single request.
- disable the button during the request.
- show safe success/failure message.
- not display raw provider body.
- not display API key.
- not auto-repeat.
- not run on app startup.
- not run after Save Key automatically.
- not run when provider/model fields change.

Recommended warning text:

> This will send one minimal request to your provider and may incur charges on
> your API account.

---

## Logging / Redaction Rules

Forbidden in logs, stdout, stderr, diagnostics, and error responses:

- API key
- request headers
- raw provider body
- prompt text
- system prompt
- raw test response
- stack trace with secrets
- memory context
- conversation history

Allowed safe fields:

- provider name
- model name
- safe error category
- status `success` or `failed`
- timing bucket if added later

---

## Security Tests Required Later

TASK-059 tests should cover:

- `explicit_cost_ack` is required.
- missing/false ack returns safe HTTP 400.
- mock provider is rejected.
- missing key is rejected.
- fake provider success path.
- fake provider auth failure.
- timeout maps safely.
- non-2xx body remains opaque.
- no retries.
- no memory context.
- no API key in response/logs/stdout/stderr.
- usage meter records safe aggregate metadata.
- Test Connection does not write chat history.
- Test Connection does not create memory audit.
- `/chat` schema remains unchanged.
- no external API call in automated tests.

---

## Runtime Smoke Checklist Later

For a future manual smoke task:

- Use fake provider first, or minimal real provider only after explicit user cost confirmation.
- Exactly one click.
- Exactly one provider request.
- Verify no repeated external calls.
- Verify no key leak in UI, logs, stdout, stderr, or network traces.
- Verify safe UI result.
- Confirm memory is disabled.
- Clear env/test key after the smoke.

---

## Non-Goals

- No implementation in TASK-058.
- No live provider call.
- No payment or billing integration.
- No automatic provider testing.
- No chat completion UX.
- No memory retrieval.
- No streaming.
- No tools.
- No retries.
- No background polling.
- No provider model list fetching.
- No frontend direct provider calls.

---

## Future Sequence

| Task | Name | Type |
|---|---|---|
| TASK-058 | Provider Test Connection Design | Design-only |
| TASK-059 | Provider Test Connection Backend Implementation | Implementation |
| TASK-060 | Provider Test Connection UI Enablement | Implementation |
| TASK-061 | Provider Test Connection Runtime Smoke Check | Manual smoke |
