# Chat LLM Real Provider Wiring Design

Status: TASK-042 design complete; TASK-043 mocked contract tests in progress. This document is design-only and does not enable live provider calls.

## Purpose

This document defines how `/chat` may use a real LLM provider in the future.

It does not enable live provider calls. It does not modify `/chat` runtime behavior yet. It preserves the existing `ChatResponse` schema:

```text
reply / mood / source
```

## Current Baseline

- `/chat` works with the old mock flow when `LLM_CHAT_ENABLED=false`.
- `/chat` works with the `llm_mock` path when `LLM_CHAT_ENABLED=true` and `LLM_PROVIDER_ENABLED=false`.
- `HTTPRealLLMProvider` exists behind provider feature flags.
- Anthropic Messages API contract tests pass with mocked HTTP.
- Live provider smoke has not been run.
- Electron UI does not know provider details.
- `/chat` response schema remains `reply / mood / source`.
- TASK-041 mock runtime smoke passed with 342 pytest tests passing.

## Required Feature Flag Matrix

| `LLM_CHAT_ENABLED` | `LLM_PROVIDER_ENABLED` | `LLM_PROVIDER_NAME` | `LLM_API_KEY` | Expected `/chat` path |
|---|---|---|---|---|
| `false` | any | any | any | old mock flow |
| `true` | `false` | any | any | LLM adapter `MockLLMProvider` |
| `true` | `true` | `mock` | any | LLM adapter `MockLLMProvider` |
| `true` | `true` | unknown | any | `MockLLMProvider` fallback |
| `true` | `true` | `anthropic` | missing | `MockLLMProvider` fallback or safe fallback depending on `LLM_FALLBACK_TO_MOCK` |
| `true` | `true` | `anthropic` | present | real provider path may be used |

Rules:

- All automated tests must mock HTTP.
- Live calls are allowed only in a manual smoke task after explicit user opt-in and cost acknowledgement.
- `LLM_PROVIDER_ENABLED=true` must not affect `/chat` unless `LLM_CHAT_ENABLED=true`.
- `LLM_CHAT_ENABLED=true` must not imply a real provider; provider factory resolution still controls mock, fallback, or real provider.

## Response Schema

Response keys remain:

```text
reply / mood / source
```

The `/chat` response must not include:

- token usage
- raw provider JSON
- provider diagnostics
- API key
- provider request body
- raw provider response body
- prompt text
- memory context
- conversation history
- state context

## Source Values

Allowed source values:

| Source | Meaning |
|---|---|
| `mock` | Existing old mock flow was used. |
| `llm_mock` | LLM adapter path used `MockLLMProvider` or mock fallback. |
| `llm_real` | LLM adapter path used a real provider and returned a successful normalized response. |
| `llm_real_error` | Real provider path was selected but returned canonical safe fallback text without mock fallback. |

Fallback source rules:

- If a real provider is requested but the factory resolves to mock, source should be `llm_mock`.
- If a real provider fails and mock fallback is used, source should be `llm_mock` or `mock`, but not `llm_real`.
- If fallback is disabled and canonical safe fallback text is used, source is `llm_real_error`.
- A response must not claim `llm_real` unless a real provider produced a non-empty normalized `LLMResponse.text`.

## Provider Failure / Fallback

| Failure | Fallback behavior | Source behavior |
|---|---|---|
| Missing key | If `LLM_FALLBACK_TO_MOCK=true`, use mock fallback. If false, use canonical safe fallback text. | `llm_mock` for mock fallback; conservative safe value for safe fallback. |
| Unknown provider | Use `MockLLMProvider` fallback with a non-sensitive warning. | `llm_mock`. |
| Auth failure | Do not expose provider body or exception. Use mock fallback or canonical safe fallback. | Not `llm_real`. |
| Rate limit | Do not retry. Use mock fallback or canonical safe fallback. | Not `llm_real`. |
| Timeout | Do not retry. Use mock fallback or canonical safe fallback. | Not `llm_real`. |
| Network failure | Do not retry. Use mock fallback or canonical safe fallback. | Not `llm_real`. |
| Invalid response | Treat as `invalid_response`. Use mock fallback or canonical safe fallback. | Not `llm_real`. |
| Empty text | Treat as `invalid_response`. Use mock fallback or canonical safe fallback. | Not `llm_real`. |

Every failure path must preserve these boundaries:

- no raw provider body to frontend
- no raw exception to frontend
- no API key leakage
- no prompt leakage
- no memory context leakage
- no automatic retry

## Memory Gate Independence

LLM and memory controls remain independent:

- `LLM_CHAT_ENABLED` does not enable memory.
- `LLM_PROVIDER_ENABLED` does not enable memory.
- `MEMORY_INJECTION_ENABLED` does not enable LLM.
- `request.use_memory` is still required before memory can be used.
- Approved memory context may be sent to the provider only when both memory gates are true and `/chat` is already using the LLM adapter path.
- `MemoryInjectionAudit` remains memory-scoped.
- Provider observability remains separate from memory audit.
- Real provider responses must not trigger automatic memory writes.

## Logging / Redaction

Forbidden in logs:

- API key
- `user_message`
- full prompt
- memory context
- conversation history
- state context
- raw provider request
- raw provider response
- non-2xx provider response body
- `LLMResponse.text`

Allowed safe diagnostics:

- provider resolved name
- safe provider resolution reason
- safe error category
- fallback occurred true/false
- latency bucket if implemented later

Allowed diagnostics must never include key fragments, prompt text, response text, raw body snippets, or user text.

## Manual Live Smoke Prerequisites

Before TASK-038 or a future live smoke task can make a live provider call:

- user has an API key
- user explicitly accepts cost risk
- exactly one minimal request is planned
- memory is disabled first
- no tools
- no streaming
- no retries
- logs are inspected for key leakage
- env vars are cleared after the test
- no API key is committed
- the call is not added to automated tests

## Future Test Plan

TASK-043 should test:

- full flag matrix with mocked provider / mocked HTTP
- source behavior for mock, `llm_mock`, `llm_real`, and fallback paths
- fallback behavior for missing key, unknown provider, auth failure, rate limit, timeout, network failure, invalid response, and empty text
- no raw body leakage
- no API key leakage
- no memory auto-enable
- `/chat` schema remains `reply / mood / source`
- no live API calls
- no retries
- `backend/dragon_pet_ai.db` is not polluted

TASK-043 current mocked contract coverage:

- `/chat` flag matrix is tested with mocked providers / fake HTTP transport only.
- Anthropic key-present success path is tested with fake HTTP transport and returns `llm_real`.
- Missing key and provider failure fallback paths are tested and do not claim `llm_real`.
- Response schema remains `reply / mood / source`.
- API key, raw provider body, user message, prompt text, and memory context leakage checks are covered.
- Memory gate independence is covered.
- No live provider call is part of automated tests.

## Non-Goals

- No live provider call.
- No Electron UI change.
- No frontend config.
- No streaming.
- No tools.
- No retries.
- No automatic memory write.
- No semantic retrieval.
- No vector DB.
