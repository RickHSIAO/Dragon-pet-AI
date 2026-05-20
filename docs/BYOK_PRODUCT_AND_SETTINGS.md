# BYOK Product and Settings Design

Status: TASK-045 DONE. TASK-046 DONE. TASK-047 DONE. TASK-048 DONE. TASK-049 Secure Key Storage Design in progress. This document does not implement provider settings UI, settings API, or key storage and does not read API keys.

## Secure Key Storage Design (TASK-049)

The secure key storage design is documented separately in `docs/SECURE_KEY_STORAGE_DESIGN.md`. That document covers:

- Comparison of 4 storage options: environment variable, OS keychain, encrypted file, plain SQLite
- MVP recommendation: environment variable only for dev phase; OS keychain for future production desktop
- Explicitly forbidden: plain SQLite or plain config file for real API keys
- Key lifecycle: add, replace, clear, test, rotate, uninstall behavior, debug export behavior
- API integration rules: how each Provider Settings API endpoint interacts with the storage layer
- Redaction rules across logs, exceptions, repr/str, stdout/stderr, exports
- Threat model: accidental git commit, log exposure, frontend exposure, local DB leakage, debug export, malware
- Testing requirements for TASK-053 implementation
- Adjusted implementation sequence: TASK-053 must precede TASK-051

Key constraints confirmed:

- Dev phase remains environment variable only. No persistent user key storage until TASK-053 is complete.
- Future production desktop should prefer OS keychain / Credential Manager (Python `keyring` library).
- `POST /provider/settings/key` must not be implemented until TASK-053 (Secure Key Storage Implementation) is complete.
- Plain SQLite storage is explicitly forbidden for real API keys.

## Backend Provider Settings API Design (TASK-048)

The backend API design for provider settings is documented separately in `docs/PROVIDER_SETTINGS_API_DESIGN.md`. That document covers:

- Proposed endpoints: `GET /provider/settings`, `PATCH /provider/settings`, `POST /provider/settings/key`, `DELETE /provider/settings/key`, `POST /provider/settings/test`
- Request and response schemas (all key-free)
- API key write-only behavior and storage rules
- Safe status model (`not_configured`, `configured`, `invalid`, `not_tested`, `test_success`, `test_failed`)
- Test connection safety rules (`explicit_cost_ack` enforcement, no retries, no automatic calls)
- Usage meter integration points
- Security boundaries (11 rules)
- Error handling (11 safe error categories)
- Future implementation sequence (TASK-049 through TASK-053)

Key rules confirmed in the API design:

- Backend API must be designed (TASK-048) before implementing settings UI or settings API.
- Secure key storage must be designed (TASK-049) before any endpoint that stores a real key is implemented.
- API key is write-only: accepted at `POST /provider/settings/key`, never returned from any endpoint.
- All endpoints are backend-mediated — frontend never calls provider directly.

## Provider Settings UI Design (TASK-047)

The concrete UI design for provider settings is documented separately in `docs/PROVIDER_SETTINGS_UI_DESIGN.md`. That document covers:

- UI sections: provider selector, API key input, model selection, safety toggles, cost warning, usage meter placement, test connection
- Step-by-step settings flow (9 steps)
- Security boundaries for settings UI
- Error UX (7 error types, safe text only)
- Memory interaction notes
- Non-goals
- Future implementation sequence (TASK-048 through TASK-052)

Key rules confirmed in the UI design:

- Settings UI must never directly call a provider from the frontend — all operations are backend-mediated.
- API key must never be returned to the frontend. UI shows only `Key configured` or `No key saved`.
- Test Connection requires explicit user action and confirmation dialog — never automatic.
- Usage meter summary must be visible in the Provider Settings panel (implemented in TASK-050).
- Cost warning must appear whenever a real provider is selected — non-dismissable.

## Usage Meter Requirement (TASK-046)

Usage meter must be designed before provider settings implementation begins. BYOK users are responsible for their own provider billing, but the app must still warn them and provide approximate usage visibility before and during real provider use.

Rules:
- Usage meter design (TASK-046) must complete before BYOK settings UI is implemented (TASK-051).
- Provider settings implementation (TASK-050 / TASK-051) must not ship to users without usage visibility.
- The provider dashboard remains the authoritative billing source of truth. App estimates are informational only.
- See `docs/USAGE_METER_DESIGN.md` for full usage meter design.

## Implementation Dependency

```
TASK-046 (Usage Meter Design)
  → TASK-047 (Provider Settings UI Design)
  → TASK-048 (Backend Provider Settings API Design)
  → TASK-049 (Secure Key Storage Design)
  → TASK-050 (Usage Meter Implementation)   ← must be ready before TASK-051
  → TASK-051 (BYOK Settings Implementation)
  → TASK-052 (BYOK Runtime Smoke Check)
```

## Purpose

BYOK lets users provide their own provider API key.

It shifts token cost responsibility to the user's own provider account. This avoids the app owner paying unlimited cloud LLM cost and makes the model suitable for early MVP use, technical users, and personal desktop deployments.

BYOK is not a shortcut around safety. The app still needs clear cost warnings, backend-only key handling, redaction, mock defaults, and explicit user action before live provider tests.

## Product Positioning

| Option | Fit | Cost responsibility | Recommendation |
|---|---|---|---|
| Portfolio/demo mode | Strong short-term fit | App owner cost is zero if mock/local only | Keep as default public demo direction. |
| Personal local companion | Strong MVP fit | User-controlled if cloud is enabled | Good for early adopters and local experimentation. |
| BYOK desktop app | Best first product direction | User's provider account | Recommended MVP product path. |
| Hosted subscription SaaS | Premature | App owner pays provider bill | Wait until usage data, pricing, and quotas exist. |
| Credit-based cloud model | Possible later | User prepays bounded usage | Requires accurate metering and payment system. |
| Hybrid local/cloud model | Strong long-term direction | Mixed | Local/mock for casual use, cloud for explicit high-value turns. |

Recommendation:

- MVP should start as BYOK desktop app or personal companion.
- Hosted subscription should wait until usage data exists.
- Unlimited free cloud LLM should not be offered.

## API Key Ownership Model

- User owns their API key.
- User is responsible for provider billing.
- App should clearly warn that usage may cost money.
- App should not hide usage/cost implications.
- App should provide a way to remove/clear key.
- App should make it clear that provider accounts, billing limits, and invoices are managed outside dragon-pet-ai.

## Key Handling Rules

- API key must never be bundled with the app.
- API key must never be committed to git.
- API key must never be sent to frontend logs.
- API key must never be shown after save.
- API key must never be stored in chat history, memory records, audit logs, or crash reports.
- API key must only be used by backend/provider adapter.
- API key must be redacted in all logs and diagnostics.
- API key must not appear in provider repr/str output.
- API key must not be included in screenshots, debug exports, or support bundles.

## Storage Options

### Option A - Environment Variable Only

Pros:

- safest for current dev
- no app storage
- easy to keep out of frontend

Cons:

- not user-friendly
- requires restart / shell setup

### Option B - Local Encrypted Store

Pros:

- better UX
- desktop app can remember key

Cons:

- more implementation complexity
- OS keychain integration needed
- must handle deletion and migration

### Option C - Plain Local Config File

Pros:

- easy to implement

Cons:

- not recommended for secrets
- higher leak risk

Recommendation:

- MVP dev phase: Environment Variable Only.
- Future desktop product: OS keychain / encrypted local store.
- Avoid plain local config for real keys.

## Settings UI Requirements

Future Provider Settings UI should include:

- Provider selector: mock / anthropic / openai future
- Key input field with password masking
- Save key action
- Clear key action
- Test connection button, manual only
- Cost warning text
- Current provider resolved status, no key value
- Fallback mode toggle or info
- No key display after save

Rules:

- Settings UI must not directly call provider from frontend.
- Settings UI must call backend only.
- Backend must perform provider tests.
- No API key should be exposed in renderer logs.
- Settings UI should show whether a key exists without showing the key value.
- Settings UI should require explicit user action before any provider test.

## Cost Warning UX

Suggested warning text:

```text
Using a real provider may incur charges from your API provider.
```

```text
You are responsible for costs associated with your own API key.
```

```text
Start with a small test request.
```

```text
Do not enable always-on mode unless you understand the cost.
```

The warning should appear before saving a key, before testing a provider connection, and before enabling any future always-on or memory-aware real-provider mode.

## Provider Selection Rules

- mock remains default
- real providers disabled by default
- provider selected only when explicitly enabled
- unknown provider falls back to mock
- missing key falls back to mock or safe fallback depending config
- no dynamic provider loading
- provider status must be non-sensitive
- frontend must not infer or display key fragments

## BYOK + Memory Interaction

- BYOK does not automatically enable memory.
- Real provider does not automatically enable memory.
- Memory still requires `MEMORY_INJECTION_ENABLED` + `request.use_memory`.
- Memory content may increase provider cost.
- UI should warn that memory-aware chat may increase token usage.
- Memory audit remains memory-scoped and must not store provider raw response or key information.

## Usage Visibility

Future usage visibility should include:

- per-session request count
- estimated token count if available
- provider used
- model used
- daily estimated cost if possible
- warning when usage grows

This should be designed before broad real-provider use. It does not need to block one manual minimal smoke test, but it should block any always-on or productized cloud usage.

## Security Boundaries

- no frontend key exposure
- no raw key in logs
- no key in SQLite unless encrypted/keychain-backed
- no key in memory/audit records
- no key in screenshots or debug exports
- no live provider test without explicit user action
- no automatic repeated provider tests
- no hidden live calls
- no provider test during app startup
- no provider test during settings page render

## Recommended Implementation Sequence

- TASK-046 - Usage Meter Design
- TASK-047 - Provider Settings UI Design
- TASK-048 - Backend Provider Settings API Design
- TASK-049 - Secure Key Storage Design
- TASK-050 - BYOK Settings Implementation
- TASK-051 - BYOK Runtime Smoke Check

## Non-Goals

- no payment system yet
- no hosted subscription yet
- no credit wallet yet
- no cloud account management
- no automatic billing
- no enterprise admin
- no live API call in this task
