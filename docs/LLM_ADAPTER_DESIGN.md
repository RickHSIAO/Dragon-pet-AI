# LLM Adapter Design

> dragon-pet-ai
> Phase: 4 — LLM Adapter Integration
> Status: REVIEW FIXES APPLIED (TASK-034F)
> Last Updated: 2026-05-19
> Owner: TASK-031
> TASK-034R Verdict: PASS WITH CHANGES — fixes applied in TASK-034F

---

## 1. Purpose

The LLM adapter is the abstraction layer that sits between the chat engine and the actual model provider. It decouples the rest of the system from any specific LLM implementation, following the same design principle already documented in `docs/ARCHITECTURE.md`.

Goals of this layer:

- `routes.py` and `chat_service` never need to know which provider is active or how it is configured.
- The Electron frontend never touches API keys, provider credentials, or provider-specific response formats.
- Swapping the mock provider for a real provider (or swapping between real providers) requires only a configuration change — no business logic changes.
- The mock provider remains the default at all times. A real provider is activated only when explicitly configured via backend environment variables.
- The existing `/chat` response schema (`reply / mood / source`) is preserved regardless of which provider is active.
- The existing memory-aware chat two-layer gate (`MEMORY_INJECTION_ENABLED` + `use_memory`) is unchanged.

The adapter is **not** a general-purpose tool execution layer and must not be extended to support tool calls, file access, or autonomous actions in Phase 4.

---

## 2. Current Baseline (Phase 3 Completed State)

The following services are implemented and stable. **No changes are permitted to any of these in TASK-031.**

| Component | Location | Current Role |
|---|---|---|
| `/chat` route | `backend/app/api/routes.py` | Receives POST, runs two-layer gate, delegates to chat_service, returns `reply/mood/source` |
| `chat_service` | `backend/app/services/chat_service.py` | Orchestrates chat turn: history load, memory context, prompt, mock reply, state update |
| `prompt_service` | `backend/app/services/prompt_service.py` | Formats approved memory context block with delimiters and safety instruction |
| `memory_service` | `backend/app/services/memory_service.py` | CRUD, approved context builder, injection-time filtering, 5-mem / 1500-char cap |
| `memory_audit_service` | `backend/app/services/memory_audit_service.py` | Creates audit rows, pagination helpers, parse helpers |
| Character / Relationship State | `backend/app/services/` | Read/write mood, energy, affinity per turn |
| Mock response | `backend/app/services/chat_service.py` | `generate_mock_chat_reply()` — returns deterministic mock strings |
| Memory-aware gate | `routes.py` | `MEMORY_INJECTION_ENABLED AND request.use_memory` before any memory injection |
| Audit log | `memory_audit_service.py` | One row per injection event; stores IDs + metadata only |

**Current gap:** `formatted_context` (the approved memory context block) is built and audited but not yet passed to any language model. The mock reply generator ignores it. TASK-035 adds provider selection and a mocked-HTTP real adapter. TASK-036 documents the vendor-specific contract in `docs/LLM_PROVIDER_CONTRACT.md`; it still does not enable live provider calls or wire `/chat` to the real provider.

---

## 3. Proposed Provider Interface

This section defines the conceptual interface. The Python skeleton is now implemented in TASK-032 under `backend/app/llm`.

### 3.1 Request Structure (`LLMRequest`)

The adapter receives fully assembled prompt parts from `chat_service`. It does not build prompts itself.

| Field | Type | Description |
|---|---|---|
| `system_prompt` | `str` | Character persona and behavioral rules. Assembled by `chat_service`. |
| `user_message` | `str` | The user's current message. |
| `mode` | `str` | Chat mode (casual / debug / support / project / reminder). |
| `memory_context` | `str \| None` | Pre-formatted approved memory block from `prompt_service`. `None` when memory injection is off. |
| `state_context` | `dict \| None` | Character and relationship state summary. Assembled by `chat_service`. |
| `conversation_history` | `list[dict] \| None` | Recent N turns for context. Already trimmed before passing. |

Design rules:
- The adapter receives pre-assembled parts. It does not call `memory_service` or `prompt_service` directly.
- `memory_context` is always a pre-formatted string — the adapter does not know about individual memory entries.
- The adapter never sees raw memory IDs, raw memory content before filtering, or user PII that has not already been approved for injection by the memory pipeline.

### 3.2 Response Structure (`LLMResponse`)

| Field | Type | Description |
|---|---|---|
| `text` | `str` | The generated reply text. Mandatory. |
| `provider` | `str` | Provider name string (e.g. `"mock"`, `"openai"`, `"anthropic"`). |
| `model` | `str \| None` | Model identifier if available (e.g. `"gpt-4o"`, `"claude-opus-4-6"`). `None` for mock. |
| `usage` | `dict \| None` | Token usage metadata if available. Not exposed to frontend in MVP. |
| `error` | `str \| None` | Non-null only on soft error path (e.g. fallback triggered). |

Design rules:
- `text` is always a safe, user-facing string. The provider implementation must validate this before returning.
- `raw_response` from the external API must never be returned through this interface. Internal logging of safe subfields is permitted only with key-free sanitization (see Section 7).
- `usage` is internal only — it must not be forwarded to the Electron frontend in Phase 4.

### 3.3 Provider Interface Methods

| Method / Property | Description |
|---|---|
| `generate(request: LLMRequest) -> LLMResponse` | Core method. Takes a request, returns a response. Must not raise on handled errors — returns `LLMResponse` with `error` set instead. |
| `health_check() -> bool` | Optional. Returns `True` if the provider is reachable. Used in smoke checks only. |
| `provider_name: str` | Read-only property. Returns the canonical provider identifier string. |

---

## 4. Provider Types

### 4.1 MockProvider (Default)

TASK-035 implementation status: `MockLLMProvider` remains the default. `HTTPRealLLMProvider` exists behind `LLM_PROVIDER_ENABLED`, provider selection is config-driven, and automated tests use mocked HTTP only. `/chat` is not wired to the real provider in TASK-035.

TASK-036 contract status: vendor-specific Anthropic request/response mapping is documented separately in `docs/LLM_PROVIDER_CONTRACT.md`. TASK-036 is design-only: no runtime code, no API key reads, and no live provider calls.

TASK-037 contract test status: mocked HTTP tests verify Anthropic request method, endpoint, headers, body shape, text-block parsing, internal usage parsing, safe error mapping, no retries, no key leaks, and unchanged `/chat` behavior. No live provider calls are made in automated tests.

TASK-040 chat wiring status: `/chat` wiring is implemented behind `LLM_CHAT_ENABLED` as designed in `docs/CHAT_LLM_WIRING_DESIGN.md`. The default remains `LLM_CHAT_ENABLED=false`, so normal runtime behavior stays on the existing mock flow. Automated tests use mocked providers / mocked HTTP only.

TASK-033 compatibility status: tests now verify that `MockLLMProvider` handles the current chat modes, accepts optional memory/state/history context without crashing, avoids dumping raw `memory_context` into response text, and can be mapped to the existing `reply / mood / source` response shape. `/chat` is still not wired to the LLM adapter.

The mock provider is the **always-available, always-safe default**. It wraps the existing `generate_mock_chat_reply()` logic.

| Property | Value |
|---|---|
| Default? | Yes — active unless explicitly overridden |
| Requires API key? | No |
| External network call? | No |
| Deterministic? | Semi-deterministic (mode-based reply selection) |
| Used in tests? | Yes — all pytest tests use MockProvider |
| Safe fallback? | Yes — chat_service falls back to MockProvider on real provider failure |

Rules:
- MockProvider must remain functional and testable at all times, regardless of Phase 4 progress.
- MockProvider must not require any environment variable to be active.
- MockProvider must produce a valid `LLMResponse` on every call without raising.
- When `memory_context` is provided but the provider is MockProvider, the context is received but not used (mock responses remain deterministic). This is expected and intentional — context wiring to real output is the job of the real provider.

### 4.2 RealProvider (Disabled by Default)

The real provider calls an external LLM API. It is **disabled by default** and must not activate unless all required conditions are met.

| Property | Value |
|---|---|
| Default? | No — must be explicitly enabled via env var |
| Requires API key? | Yes — from backend environment variable only |
| External network call? | Yes — to configured provider endpoint only |
| Timeout? | Required — configurable, must not block indefinitely |
| Error handling? | Required — must not surface raw errors to frontend |
| Fallback? | Yes — falls back to MockProvider on failure unless fallback disabled |

Rules:
- The real provider adapter is implemented in TASK-035 behind disabled-by-default flags.
- The API key must come from an environment variable only (`LLM_API_KEY` or provider-specific equivalent).
- The API key must never appear in: frontend code, HTTP responses, log output, database records, or error messages.
- The real provider must validate that its API key is present and non-empty before attempting any call. If missing, it must not activate — `get_llm_provider()` should fall back to mock.
- Output from the real provider must be validated for basic structure (non-empty `text` string) before being returned as `LLMResponse`.
- An async timeout must be configured. If exceeded, the provider returns an `LLMResponse` with `error` set and `text` set to a safe user-facing fallback message.

---

## 5. Feature Flags and Configuration

Phase 4 introduces two new environment variables. These join the existing `MEMORY_INJECTION_ENABLED` flag without replacing or modifying it.

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER_ENABLED` | `false` | Master switch. When `false`, the system uses MockProvider regardless of other settings. |
| `LLM_PROVIDER_NAME` | `mock` | Which real provider to use when enabled. Values: `openai`, `anthropic`. Ignored when `LLM_PROVIDER_ENABLED=false`. |
| `LLM_API_KEY` | — | API key for the active real provider. Backend env var only. Not logged. Not forwarded. Provider-specific overrides (e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) may be supported as aliases. |
| `LLM_TIMEOUT_SECONDS` | `30` | Request timeout for real provider calls. |
| `LLM_FALLBACK_TO_MOCK` | `true` | When `true`, a real provider failure falls back to MockProvider. When `false`, the error is returned directly. |

### 5.1 Flag Evaluation Logic

```
get_llm_provider():
  if LLM_PROVIDER_ENABLED is not true:
    return MockProvider
  if LLM_PROVIDER_NAME is "mock" or not set:
    return MockProvider
  if LLM_PROVIDER_NAME is not in KNOWN_PROVIDERS:
    emit non-sensitive warning: "unknown provider name, falling back to mock"
    return MockProvider                          ← MUST NOT attempt dynamic loading
  if LLM_API_KEY is missing or empty:
    emit non-sensitive warning: "API key missing, falling back to mock"  ← never log key value
    return MockProvider
  return RealProvider(name=LLM_PROVIDER_NAME, key=LLM_API_KEY)
```

This logic ensures:
- MockProvider is always the default with zero configuration.
- Unknown provider names always fall back to MockProvider — never crash, never dynamic-load.
- A misconfigured real provider (missing key) falls back to mock with a non-sensitive warning.
- The flag hierarchy is clear, deterministic, and testable.

**Unknown provider behavior is fixed:** An unknown `LLM_PROVIDER_NAME` value must always fall back to `MockProvider` plus a non-sensitive warning log line. It must never crash the backend, and must never attempt dynamic provider loading.

**Missing API key behavior is fixed:** If `LLM_FALLBACK_TO_MOCK=true` (default), fall back to MockProvider with a non-sensitive warning. If `LLM_FALLBACK_TO_MOCK=false`, return the canonical safe fallback text (see Section 5.4). Never expose the raw key or provider error.

### 5.2 Env Var Table (Canonical Reference)

> These are the canonical env var definitions. All other references in this document defer here.

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER_ENABLED` | `false` | Master switch. `false` → MockProvider always. True values: `1`, `true`, `yes`, `on`. Unknown values fail closed to `false`. |
| `LLM_PROVIDER_NAME` | `mock` | Provider to use when enabled. Allowed values: `mock`, `openai`, `anthropic`. Unknown values fall back to MockProvider + warning. |
| `LLM_API_KEY` | — | API key for the active real provider. Backend env var only. Not logged. Not forwarded. Provider-specific aliases (e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) may be supported. |
| `LLM_MODEL` | — | Optional. Provider-specific model identifier. Unknown values must not crash the backend. |
| `LLM_TIMEOUT_SECONDS` | `30` | Request timeout for real provider calls. Valid range: `1`–`120`. Invalid values fall back to `30`. |
| `LLM_FALLBACK_TO_MOCK` | `true` | `true` → real provider failure falls back to MockProvider. `false` → return canonical safe fallback text. Raw provider error bodies are never exposed in either case. |

### 5.3 Provider Enablement Matrix

| `LLM_PROVIDER_ENABLED` | `LLM_PROVIDER_NAME` | `LLM_API_KEY` | Resolved Provider |
|---|---|---|---|
| `false` | any | any | MockProvider |
| `true` | `mock` or not set | any | MockProvider |
| `true` | unknown name | any | MockProvider + non-sensitive warning |
| `true` | real provider | missing or empty | MockProvider + non-sensitive warning |
| `true` | real provider | present | RealProvider |

### 5.4 Canonical Safe Fallback Text

When a real provider is unavailable and a user-facing message is required, the following single canonical string must be used:

```
"I cannot reach the real language model right now, so I will continue in safe mock mode."
```

This string is used as the `reply` field in `ChatResponse`. It must not contain provider names, error codes, stack traces, or API key fragments. No other variant is permitted in Phase 4.

### 5.5 No Automatic Retries

**Phase 4 has no automatic retries.** Each `/chat` turn may make at most one real provider call. If that call fails, the error handling rules in Section 8 apply immediately. Automatic retries are prohibited because they risk:
- Accidental duplicate billing on per-token providers
- Rate-limit amplification under high load
- Unpredictable latency on the `/chat` endpoint

### 5.6 Provider Visibility (Observability Without Secrets)

TASK-035 exposes resolved provider state through a non-sensitive factory helper without exposing secrets. Acceptable MVP options:
- Startup `INFO` log: `provider_resolved=mock reason=flag_disabled` (no key value, no key fragment)
- OR `/health` response non-sensitive field: `"llm_provider": "mock"`

This requirement exists so that fallback-to-mock does not silently hide misconfiguration. Silent degradation is permitted for security; invisible degradation is not.

### 5.7 Redaction Utility Requirement

TASK-035 must implement or design a shared redaction helper before logging any provider diagnostics. Requirements:
- Must mask API key-like strings matching patterns: `sk-`, `Bearer `, `api_key`, `token`, `private_key`
- Must mask the configured `LLM_API_KEY` value specifically (known secret)
- Python provider class `__repr__` and `__str__` must not expose API key value
- pytest tests must assert that the configured key value does not appear in `caplog`, `stdout`, or `stderr`

### 5.8 Relationship to Existing Memory Gate

The LLM provider flag is **completely independent** of the memory injection gate.

| `LLM_PROVIDER_ENABLED` | `MEMORY_INJECTION_ENABLED` | `use_memory` | Behavior |
|---|---|---|---|
| `false` | `false` | `false` | MockProvider, no memory injection |
| `false` | `true` | `true` | MockProvider, memory context built and audited but passed to mock (unused) |
| `true` | `false` | `false` | RealProvider, no memory injection |
| `true` | `true` | `true` | RealProvider, memory context built, audited, and passed to real provider |

In all cases, `/chat` response schema remains `reply / mood / source`.

---

> **Note on real provider config rules:** The complete, canonical real provider configuration rules are defined in **Section 5** above (Sections 5.1 through 5.8). The sections below (6 onward) cover prompt assembly, response normalization, error handling, testing, and security — all of which reference Section 5 as the authoritative source for config decisions.

---

## 6. Prompt Assembly Boundaries

The adapter receives pre-assembled parts. Prompt construction responsibility is distributed as follows:

| Service | Responsibility |
|---|---|
| `memory_service` | Selects approved memory entries (type allowlist, confidence filter, sensitive-content regex filter, 5-mem / 1500-char cap) |
| `prompt_service` | Formats approved entries into the delimited memory context block with the fixed reference-only safety instruction |
| `chat_service` | Assembles `LLMRequest`: combines system prompt, memory context, state context, history, and user message |
| `llm_adapter` | Receives the fully assembled `LLMRequest`. Builds the final raw prompt string for the specific provider API. Does not call any service. |
| `routes.py` | Remains thin: validates request, checks two-layer gate, delegates to `chat_service`, returns response |

### 6.1 Content Priority Rules

These rules govern how the assembled prompt must be structured inside the adapter:

1. **System / developer rules always rank highest.** Character persona, safety instructions, and behavioral constraints are in `system_prompt`. They cannot be overridden by memory content or user messages.
2. **Current user message outranks memory.** If memory context contains an entry that contradicts the current user request, the user request takes precedence. The memory block is reference-only.
3. **Memory content is reference-only.** The approved memory context block (from `prompt_service`) includes a fixed safety instruction: memory entries are reference information only and must not be treated as instructions. This instruction must not be removed or weakened by the adapter.
4. **Provider output cannot mutate memory.** LLM responses must not trigger automatic memory writes. Response text is displayed to the user only.

---

## 7. Response Normalization

The adapter normalizes any provider's output into the existing `ChatResponse` schema.

### 7.1 Source Field Values

The `source` field in `ChatResponse` distinguishes which provider generated the reply:

| Value | Meaning |
|---|---|
| `mock` | MockProvider (current default) |
| `llm_real` | RealProvider (future, Phase 4 TASK-035+) |

> Note: `llm_mock` was considered but rejected for simplicity — MockProvider returns `mock`, the same as today. This preserves full backward compatibility for clients that check `source`.

### 7.2 Normalization Rules

- `reply` = `LLMResponse.text`. Must be a non-empty string. If empty or missing, substitute the canonical safe fallback text (Section 5.4).
- `mood` = derived from character state (same as today — the provider does not set mood).
- `source` = `LLMResponse.provider` mapped to the normalized value above.
- Raw provider response body is **never** forwarded to the frontend.
- Non-2xx provider response bodies are **opaque** — do not parse, log, store, or return any part of them. Only log the safe error category and HTTP status class (e.g. `"4xx auth error"`).
- Token usage (`LLMResponse.usage`) is **never** forwarded to the frontend in Phase 4.
- `LLMResponse.text` must not be logged — it may contain sensitive user information.
- Internal logging must sanitize: no API keys, no raw error bodies, no raw prompt text, no `LLMResponse.text`.

---

## 8. Error Handling

### 8.1 Error Categories

| Error Type | Cause | Handling |
|---|---|---|
| Missing API key | `LLM_API_KEY` not set or empty | `get_llm_provider()` returns MockProvider; no real call attempted |
| Provider unavailable | Network error, DNS failure | Return `LLMResponse(text=<safe fallback>, error="provider_unavailable")` |
| Timeout | Request exceeds `LLM_TIMEOUT_SECONDS` | Return `LLMResponse(text=<safe fallback>, error="provider_timeout")` |
| Invalid response | Provider returns empty, malformed, or structurally invalid text | Validate before returning; substitute safe fallback if invalid |
| Rate limit (429) | Provider rate limit exceeded | Return `LLMResponse(text=<safe fallback>, error="rate_limit")` |
| Auth failure (401/403) | Invalid API key | Return `LLMResponse(text=<safe fallback>, error="provider_auth_error")`; **do not log the key** |
| Unexpected exception | Unhandled provider error | Catch-all; log safe summary (no key, no raw body); return safe fallback |

### 8.2 Fallback Logic

When `LLM_FALLBACK_TO_MOCK=true` (default) and the real provider fails:

1. Real provider call fails with any error.
2. `chat_service` detects `LLMResponse.error` is non-null.
3. `chat_service` calls `MockProvider.generate(request)` to obtain a fallback reply.
4. Final response returned to user has `source: "mock"` to signal that fallback occurred.
5. No raw error details are sent to the Electron frontend.

When `LLM_FALLBACK_TO_MOCK=false`:
1. Real provider call fails.
2. `chat_service` returns an error response with a safe, generic user-facing message.
3. HTTP status remains `200` with `reply` set to the safe error message. (The frontend never receives a 5xx from an LLM provider failure in Phase 4.)

### 8.3 Non-2xx Provider Response Body Rule

Provider non-2xx response bodies are **opaque**. The implementation must:
- Not parse the body for error details
- Not log any part of the raw body
- Not store any part of the body
- Not return any part of the body to the frontend or in `LLMResponse.error`

Only safe diagnostic fields may be logged: HTTP status class (e.g. `"4xx"`), error category (e.g. `"auth_error"`), elapsed time.

### 8.4 No Automatic Retries

Each `/chat` turn may make **at most one real provider call**. If that call fails, error handling applies immediately — no retry loop. This is required to prevent duplicate billing and rate-limit amplification. See Section 5.5.

### 8.5 What Must Never Happen

- API key value must never appear in any log line, response body, error message, repr, or str.
- Raw provider HTTP response body (including non-2xx bodies) must never be forwarded to the frontend or logged.
- A provider failure must never crash the backend process.
- A provider failure must never leave the `/chat` endpoint without a response.
- Canonical safe fallback text (Section 5.4) is the only user-facing error string permitted.

---

## 9. Testing Strategy

The following test coverage is expected across TASK-032 through TASK-037. Tests are **not** implemented in TASK-031.

| Test Category | Description | When |
|---|---|---|
| Mock provider unit tests | `MockProvider.generate()` returns valid `LLMResponse`; `provider_name` returns `"mock"` | TASK-032 |
| Interface contract tests | Both providers satisfy the abstract interface | TASK-032 |
| Config flag tests | `LLM_PROVIDER_ENABLED=false` → MockProvider returned; `=true` + name set → RealProvider config attempted | TASK-033 / TASK-034 |
| Missing API key tests | Missing or empty `LLM_API_KEY` → MockProvider returned, no real call | TASK-034 |
| Fallback tests | Real provider returns error → fallback to mock; `source` becomes `"mock"` | TASK-035 |
| `/chat` schema compatibility | Response always `reply / mood / source`; no extra fields; no raw provider data | TASK-035 |
| Memory-aware + LLM disabled | Memory context built and audited; mock reply returned; source is `"mock"` | TASK-033 |
| Memory-aware + LLM enabled | Memory context passed to real provider; real reply returned; audit row created | TASK-036 |
| No API key leakage | Pytest confirms configured key does not appear in response bodies, `caplog`, `stdout`, or `stderr` | TASK-035 / TASK-037 |
| Provider repr/str | `repr(provider)` and `str(provider)` do not expose API key value | TASK-035 |
| Timeout handling | Real provider call exceeds `LLM_TIMEOUT_SECONDS` → canonical safe fallback text returned | TASK-035 |
| Rate limit handling | Real provider returns 429 → opaque body, safe fallback, no raw body logged | TASK-035 |
| Non-2xx body opaque | Non-2xx response body never parsed, logged, stored, or returned | TASK-035 |
| No retry | Only one provider call per `/chat` turn; no retry loop | TASK-035 |
| Canonical fallback text | All user-facing error paths return exactly Section 5.4 text | TASK-035 / TASK-036 |

---

## 10. Security Boundaries

These boundaries apply to all Phase 4 work. They cannot be weakened without an explicit safety design review.

| Boundary | Rule |
|---|---|
| No frontend API keys | API key must never appear in `renderer.js`, `index.html`, or any client-side file |
| No API keys in DB | API key must never be written to SQLite or any other persistent store |
| No API keys in logs | API key must never appear in any log line, including warnings, debug, crash traces |
| No API keys in responses | No HTTP response (success or error) may contain the API key value |
| No API keys in repr / str | Provider `__repr__` and `__str__` must not expose API key value |
| No API keys in access logs | API key must not appear in access logs, request IDs, correlation IDs, or audit rows |
| No raw provider response to frontend | Raw provider response body (including non-2xx bodies) must never reach the Electron renderer |
| Non-2xx bodies opaque | Non-2xx provider response bodies must not be parsed, logged, stored, or returned |
| No automatic retries | At most one real provider call per `/chat` turn — no retry loops (see Section 5.5) |
| Forbidden log fields | Must never log: API key, full prompt, approved memory context, system prompt, raw provider request/response body, non-2xx body, `user_message`, `conversation_history`, `state_context`, `LLMResponse.text`, sensitive user input |
| No tool execution | LLM output must not be parsed for tool call syntax; no tool execution in Phase 4 |
| No file access | LLM must not be given access to user files |
| No autonomous action | LLM output is displayed to the user only; no side effects are triggered |
| No automatic memory write | LLM responses must not trigger automatic memory writes |
| No semantic retrieval | No vector database, no embedding-based retrieval in Phase 4 |
| Output validation required | `LLMResponse.text` must be validated for non-empty string before being returned to `chat_service` |
| `/chat` schema unchanged | Response always `reply / mood / source`; no new fields exposed to frontend |
| Memory gate unchanged | `MEMORY_INJECTION_ENABLED` + `use_memory` two-layer gate is not modified |
| MemoryInjectionAudit boundary | Audit rows must not store: raw prompts, raw provider responses, `llm_provider_used`. Provider observability belongs in a separate non-sensitive diagnostics mechanism, not in the memory audit table. |
| Redaction utility required | TASK-035 must implement a shared redaction helper before logging provider diagnostics (see Section 5.7) |

---

## 11. Proposed Task Sequence

| Task | Name | Type | Status | Key Constraint |
|---|---|---|---|---|
| TASK-032 | LLM Provider Interface Skeleton | Implementation | DONE | Abstract `LLMProvider` class + `MockLLMProvider` + `get_llm_provider()` factory — no real API calls |
| TASK-033 | Mock Provider Compatibility Tests | Testing | DONE | Verify mock modes, optional contexts, response normalization, factory behavior, unchanged `/chat` wiring |
| TASK-034 | Real Provider Config Design | Design-only | DONE | Define env var names, config loading, API key validation, error handling — no real API calls |
| TASK-034R | Real Provider Config Safety Review | Review | DONE | Opus-level review — PASS WITH CHANGES |
| TASK-034F | Apply Real Provider Config Review Fixes | Docs + Config | DONE | Applied all 13 Opus review fixes to docs and .env.example — no runtime code |
| TASK-035 | Real Provider Integration Behind Feature Flag | Implementation | DONE | First real provider behind `LLM_PROVIDER_ENABLED` flag; mocked HTTP tests only; `/chat` schema unchanged |
| TASK-036 | Real Provider Vendor Contract Design | Design-only | DONE | Anthropic request/response/error contract; no runtime code and no live API calls |
| TASK-037 | Real Provider Contract Tests | Testing | IN_PROGRESS | Mocked HTTP contract tests for Anthropic success, errors, timeout, malformed response, no leaks |
| TASK-038 | Manual Live LLM Provider Smoke Check | Validation | IN_PROGRESS | Manual opt-in provider adapter smoke; not a `/chat` smoke because `/chat` is not wired |
| TASK-039 | Chat Service LLM Wiring Design | Design-only | DONE | Define `LLM_CHAT_ENABLED`, `/chat` adapter flow, fallback, memory interaction, logging, and tests |
| TASK-040 | Chat Service LLM Wiring Behind Feature Flag | Implementation | IN_PROGRESS | Wire `/chat` to LLM adapter only when `LLM_CHAT_ENABLED=true`; mocked tests only |
| TASK-041 | Chat LLM Wiring Mock Runtime Smoke Check | Validation | Pending | Runtime smoke using mock adapter path; no live provider required |

### Sequencing Rules

- **TASK-034F must be complete before TASK-035 starts.** All Opus review fixes must be applied and verified.
- **TASK-035 is the first task permitted to reference a real external API.** It must include mocked HTTP tests — no live API calls in pytest. It must implement the redaction utility before logging any provider diagnostics.
- **TASK-036 is contract design only.** It must not read API keys, call the provider, or change runtime code.
- **TASK-037 must use mocked HTTP only.** It should turn the TASK-036 contract into tests without live calls.
- **TASK-038 requires a manual runtime smoke check.** Automated tests alone are insufficient for this task.
- **TASK-039 is design-only.** It must not wire `/chat`, read API keys, or call external APIs.
- **TASK-040 must introduce `LLM_CHAT_ENABLED=false` by default before `/chat` calls the LLM adapter.**

---

## 12. Non-Goals for Phase 4

The following are explicitly out of scope for TASK-031 through TASK-037:

| Feature | Reason |
|---|---|
| TTS (voice output) | Deferred to after LLM adapter is stable |
| STT (voice input) | Phase 5 |
| Live2D animation | Phase 5 |
| Vector database | Phase 4+ (after LLM adapter stable) |
| Semantic / embedding-based retrieval | Requires vector DB; deferred |
| Autonomous agent actions | Phase 5; requires dedicated safety design |
| User file reading | Phase 5; requires safety layer design |
| Electron packaging / distribution | Phase 4 follow-up (Option C); deferred until LLM adapter done |
| Automatic memory extraction from chat | Requires explicit user review flow; Phase 4 follow-up at earliest |
| Daily summary generation | Requires LLM adapter first; Option D deferred |
| Multi-user support | Not in MVP scope |
| Cloud sync / remote database | Not in MVP scope |
| Tool call parsing from LLM output | Not permitted in Phase 4 |
| Streaming responses | Not in Phase 4 scope; single-shot request/response only |
