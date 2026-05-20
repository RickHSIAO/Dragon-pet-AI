# Chat Service LLM Wiring Design

Status: TASK-039 design complete; TASK-040 implementation complete; TASK-041 mock runtime smoke complete. This document defines `/chat` to LLM adapter wiring behind `LLM_CHAT_ENABLED`. Real-provider `/chat` path rules are designed separately in `docs/CHAT_LLM_REAL_PROVIDER_WIRING_DESIGN.md`. It does not enable live provider calls and does not modify the Electron UI.

## Purpose

This design defines how `/chat` will eventually call the LLM adapter.

It does not enable live provider calls. It preserves the existing `ChatResponse` schema:

```text
reply / mood / source
```

The main design goal is to let the backend use `LLMProvider` safely while preserving the current mock-first behavior, deterministic fallback, memory controls, and logging boundaries.

The real provider `/chat` path is documented separately in `docs/CHAT_LLM_REAL_PROVIDER_WIRING_DESIGN.md`; live provider calls remain disabled until explicit manual opt-in.

## Current Baseline

- `/chat` uses the existing `chat_service` mock flow when `LLM_CHAT_ENABLED=false`.
- `/chat` uses the LLM adapter mock path when `LLM_CHAT_ENABLED=true` and provider resolution returns mock.
- `/chat` response schema is `reply / mood / source`.
- `LLMRequest` / `LLMResponse` exist.
- `MockLLMProvider` exists.
- `HTTPRealLLMProvider` exists behind feature flags.
- `SafeFallbackLLMProvider` exists.
- `get_llm_provider()` exists and selects mock / real / safe fallback based on config.
- Anthropic Messages API contract has mocked HTTP tests.
- TASK-040 wired `/chat` internally to the LLM adapter only when `LLM_CHAT_ENABLED=true`.
- TASK-041 mock runtime smoke passed for old mock flow and `llm_mock` path.
- Memory-aware chat gate exists:
  - backend global gate: `MEMORY_INJECTION_ENABLED`
  - per-request gate: `request.use_memory`
- `MemoryInjectionAudit` exists and records memory-injection metadata only.
- No live provider call has been executed unless the user explicitly opts in during TASK-038.

## Required Feature Flags

| Flag | Default | Purpose |
|---|---|---|
| `LLM_PROVIDER_ENABLED` | `false` | Controls provider factory resolution. When false, provider factory resolves to mock regardless of provider config. |
| `LLM_CHAT_ENABLED` | `false` | New required gate before `/chat` may call the LLM adapter. Must be introduced before runtime wiring. |
| `MEMORY_INJECTION_ENABLED` | `false` | Controls whether approved memory context may be built. Does not enable LLM calls. |
| `request.use_memory` | `false` | Per-request memory opt-in. Does not enable LLM calls. |

Rules:

- Even if a real provider adapter exists, `/chat` must not use the LLM adapter unless `LLM_CHAT_ENABLED=true`.
- `LLM_PROVIDER_ENABLED=true` alone must not change `/chat` behavior.
- `LLM_CHAT_ENABLED=true` with `LLM_PROVIDER_ENABLED=false` should call the adapter path with mock provider only, if the wiring task chooses to support mock-adapter runtime testing.
- `MEMORY_INJECTION_ENABLED=true` must not enable LLM calls.
- `request.use_memory=true` must not enable LLM calls.
- `LLM_CHAT_ENABLED` avoids provider adapter existence accidentally changing `/chat` behavior.

## Proposed Flow

```text
/chat request
  -> validate ChatRequest
  -> normalize mode
  -> load state_context
  -> evaluate memory gate:
       memory_enabled = MEMORY_INJECTION_ENABLED
       memory_requested = request.use_memory is true
       should_use_memory = memory_enabled and memory_requested
  -> if should_use_memory:
       build approved memory context records
       format approved memory context via prompt_service
       create MemoryInjectionAudit row with safe metadata only
     else:
       memory_context = None
  -> build prompt parts via prompt_service
  -> if LLM_CHAT_ENABLED is true:
       create LLMRequest
       provider = get_llm_provider()
       llm_response = provider.generate(LLMRequest)
       normalize LLMResponse to ChatResponse
     else:
       use existing mock chat flow
  -> store conversation
  -> update state
  -> return ChatResponse
```

The future implementation should keep the current storage and state update steps after response generation so mock and LLM paths share conversation persistence and state updates.

## Prompt Assembly

Prompt assembly should stay in `prompt_service`.

Rules:

- `prompt_service` assembles the system prompt.
- Approved memory context is already delimiter-wrapped before inclusion.
- System / developer safety rules outrank memory content.
- The current user message must outrank memory content.
- Memory content is reference material only; it must not become instructions.
- The final raw prompt must not be logged.
- `user_message` must not be logged.
- `memory_context` must not be logged.
- `conversation_history` must not be logged.
- `state_context` must not be logged.

Future prompt assembly order:

```text
system safety / character rules
  -> mode-specific character prompt
  -> state summary if safe and needed
  -> approved memory context if both memory gates are true
  -> current user message
```

## Response Normalization

`/chat` response schema remains:

```text
reply / mood / source
```

Mapping rules:

| ChatResponse field | Source |
|---|---|
| `reply` | `LLMResponse.text` if non-empty; otherwise canonical safe fallback text or mock fallback output. |
| `mood` | Existing mood selection / state-derived mood. The provider does not set mood. |
| `source` | `mock` for existing mock flow; `llm_mock` if the LLM adapter path used `MockLLMProvider`; `llm_real` if a real provider produced the response; `mock` if fallback used existing mock flow. |

Do not return:

- raw provider response
- provider request body
- token usage
- API key
- provider diagnostics
- latency diagnostics
- memory context
- prompt text
- conversation history
- state context

## Fallback Behavior

Fallback rules:

- If provider fails and fallback is enabled, use `MockLLMProvider` or the existing mock chat flow.
- If fallback is disabled, return the canonical safe fallback text:

```text
I cannot reach the real language model right now, so I will continue in safe mock mode.
```

- Never raise raw provider errors to frontend.
- Never expose raw provider response bodies.
- Never expose raw provider request bodies.
- Never expose stack traces.
- Never expose API key fragments.
- Provider failures must not create partial frontend response shapes.
- `/chat` should still return HTTP 200 with `reply / mood / source` for provider failures in Phase 4.

## Memory Interaction

LLM and memory gates are independent.

Rules:

- `LLM_CHAT_ENABLED` does not enable memory.
- `LLM_PROVIDER_ENABLED` does not enable memory.
- `MEMORY_INJECTION_ENABLED` does not enable LLM.
- `request.use_memory` does not enable LLM.
- Approved memory context may be built only when both memory gates are true.
- Memory context may be passed to the LLM adapter only when both memory gates are true and `LLM_CHAT_ENABLED=true`.
- `MemoryInjectionAudit` remains memory-scoped.
- Memory audit rows must not store provider name, provider raw response, prompt text, or LLM diagnostics.
- Provider observability should be separate from memory audit.
- No automatic memory write is introduced by LLM responses.

## Logging Rules

Forbidden log fields:

- API key
- `user_message`
- full prompt
- system prompt
- memory context
- conversation history
- state context
- `LLMResponse.text`
- raw provider response
- raw provider request body
- non-2xx response body
- sensitive user input

Allowed safe diagnostics:

- resolved provider name
- provider resolution reason
- safe error category
- feature flag state
- latency bucket if later implemented
- non-sensitive status class such as `4xx` or `5xx`

Allowed diagnostics must never include key fragments, prompt text, response text, or raw body snippets.

## Future Test Plan

TASK-040 should add tests before or with runtime wiring.

TASK-040 implementation status:

- `LLM_CHAT_ENABLED` helper exists and defaults false.
- With `LLM_CHAT_ENABLED=false`, `/chat` uses the existing mock flow and does not call provider factory.
- With `LLM_CHAT_ENABLED=true`, `/chat` can use the LLM adapter path.
- Tests use mocked providers / mocked transport only.
- No live external provider calls are part of automated tests.

Required tests:

- `LLM_CHAT_ENABLED` defaults false.
- `/chat` behavior is unchanged when `LLM_CHAT_ENABLED=false`.
- `/chat` uses LLM adapter mock path when `LLM_CHAT_ENABLED=true` and provider resolves to mock.
- `/chat` uses real provider only when `LLM_CHAT_ENABLED=true`, `LLM_PROVIDER_ENABLED=true`, valid provider config exists, and tests use mocked HTTP.
- `/chat` schema remains exactly `reply / mood / source`.
- `source` is correct for mock flow, LLM mock path, real provider path, and fallback path.
- Memory disabled + LLM disabled.
- Memory disabled + LLM enabled.
- Memory enabled + request.use_memory false + LLM enabled.
- Memory enabled + request.use_memory true + LLM enabled.
- Fallback enabled provider failure returns mock / safe mock output.
- Fallback disabled provider failure returns canonical safe fallback text.
- No API key leakage in response, logs, DB, audit rows, stdout, stderr, repr, or str.
- No raw prompt logging.
- No raw memory context logging.
- No `LLMResponse.text` logging.
- Non-2xx body remains opaque.
- No retries.
- Automated tests do not call live external APIs.
- `backend/dragon_pet_ai.db` is not polluted by tests.

## Non-Goals

- No live provider call.
- No Electron UI change.
- No frontend code.
- No streaming.
- No tools.
- No retries.
- No automatic memory write.
- No vector DB.
- No semantic retrieval.
- No automatic memory extraction.
- No autonomous agent behavior.
- No new API endpoint.
