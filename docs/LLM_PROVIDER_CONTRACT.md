# LLM Provider Contract

Status: TASK-036 design complete; TASK-037 mocked contract tests in progress. This document defines the first vendor-specific request and response contract for future implementation and smoke checks. It does not enable live provider calls.

Sources used for this contract:

- Anthropic API overview: https://platform.claude.com/docs/en/api/overview
- Anthropic Messages API guide: https://platform.claude.com/docs/en/build-with-claude/working-with-messages
- Anthropic API errors: https://platform.claude.com/docs/en/api/errors

## Provider Selection

First target provider: Anthropic Claude Messages API.

Reason:

- The project workflow already uses Claude / Sonnet / Opus-style review and implementation language.
- Anthropic's Messages API has a simple non-streaming request contract suitable for the current `LLMRequest` / `LLMResponse` adapter.
- Anthropic supports a top-level `system` field, a `messages` list, `max_tokens`, and response `content` blocks that can be normalized into `LLMResponse.text`.

This does not mean live API is enabled yet. This is only a contract design. TASK-036 must not read API keys, call Anthropic, or modify runtime code.

## Request Contract

Future target endpoint:

| Field | Contract |
|---|---|
| Endpoint | `https://api.anthropic.com/v1/messages` |
| Method | `POST` |
| Content type | JSON only |
| Authentication | Backend-only secret header. Use `x-api-key` with the backend env key for direct Anthropic API. Do not expose, log, store, or render the key. |
| API version header | `anthropic-version`, expected value to be configured or fixed during implementation. MVP candidate: `2023-06-01`. |
| Model | From `LLM_MODEL`; required before live smoke. No hardcoded real model should be assumed in tests. |
| System prompt | Map `LLMRequest.system_prompt` to top-level `system`. Do not log it. |
| User message | Map `LLMRequest.user_message` to one `messages` item: `{ "role": "user", "content": <text> }`. Do not log it. |
| Max tokens | Required numeric field. MVP default should be conservative and documented in config before live smoke. |
| Timeout | Use `LLM_TIMEOUT_SECONDS`, clamped by existing config helper. |
| Streaming | Disabled. Do not send streaming flags. |
| Tools | Disabled. Do not include `tools`, `tool_choice`, MCP, computer-use, or tool-call fields. |

Conceptual payload:

```json
{
  "model": "<LLM_MODEL>",
  "max_tokens": 512,
  "system": "<system prompt>",
  "messages": [
    {
      "role": "user",
      "content": "<user message>"
    }
  ]
}
```

The real implementation must avoid logging the payload because it contains user text, prompt text, and possibly memory context after future wiring.

## Response Contract

Successful Anthropic Messages responses are normalized to `LLMResponse`.

Parse only:

| Provider field | Normalized field | Rule |
|---|---|---|
| `content[].text` where block `type` is `text` | `LLMResponse.text` | Join text blocks in order with a newline, then trim. Empty result is invalid. |
| `model` | `LLMResponse.model` | Internal only. |
| Provider id/name | `LLMResponse.provider` | Use configured provider name, e.g. `anthropic`. |
| `usage` | `LLMResponse.usage` | Internal only, never returned to frontend in MVP. |
| Failure category | `LLMResponse.error` | Safe category string only. |

Rules:

- Raw provider response is not returned to frontend.
- Raw provider response is not stored in DB or audit rows.
- Token usage is not returned to frontend in MVP.
- Response is normalized to `LLMResponse`.
- `LLMResponse.text` must not be logged.
- If parsed text is missing or empty, return safe fallback behavior.

## Error Mapping

All failures must preserve existing safe behavior:

- If `LLM_FALLBACK_TO_MOCK=true`, the runtime should fall back to `MockLLMProvider`.
- If `LLM_FALLBACK_TO_MOCK=false`, return the canonical safe fallback text:

```text
I cannot reach the real language model right now, so I will continue in safe mock mode.
```

No raw error body, raw provider message, stack trace, API key, prompt, user message, memory context, or conversation history may be exposed.

| Condition | Example source | `LLMResponse.error` category | Body handling |
|---|---|---|---|
| Auth failure | HTTP 401 `authentication_error`, HTTP 403 `permission_error` | `provider_auth_error` | Opaque. Do not parse beyond status/category mapping. |
| Rate limit | HTTP 429 `rate_limit_error` | `rate_limit` | Opaque. Do not retry automatically. |
| Timeout | Client timeout or HTTP 504 `timeout_error` | `provider_timeout` | Opaque. |
| Network failure | DNS/connect/read error | `provider_unavailable` | No raw exception text in frontend. |
| Non-2xx generic | HTTP 400, 402, 404, 413, 500, 529, or unknown non-2xx | `provider_error` unless a more specific safe category above applies | Opaque. |
| Malformed response | Invalid JSON or unexpected shape on 2xx | `invalid_response` | Do not log raw body. |
| Empty text | No non-empty text blocks | `invalid_response` | Do not log raw body. |

There are no automatic retries in Phase 4.

## Mocked HTTP Fixtures

TASK-037 adds mocked HTTP cases only. No fixture may call `api.anthropic.com`.

Required fixtures:

| Case | Fixture shape | Expected behavior |
|---|---|---|
| Success response | 200 with `content: [{ "type": "text", "text": "..." }]`, `model`, optional `usage` | Normalize to `LLMResponse.text`, provider `anthropic`, model, internal usage. |
| Non-2xx opaque body | 500 or 529 with realistic error JSON containing unique body text | Return safe category; assert body text is not parsed, logged, stored, or returned. |
| Timeout | Fake client raises timeout | Return `provider_timeout`; one call only. |
| Malformed JSON | 200 with invalid JSON / fake response raising JSON decode error | Return `invalid_response`; no raw body leak. |
| Empty text | 200 with empty `content`, no text blocks, or blank text | Return `invalid_response`. |
| Rate limit | 429 with error body and optional `retry-after` header | Return `rate_limit`; no automatic retry. |
| Auth failure | 401 or 403 with error body | Return `provider_auth_error`; no API key leak. |

Fixture assertions:

- HTTP call count is exactly one.
- No test performs live DNS or external HTTP.
- `caplog`, stdout, stderr, response text, DB, and audit rows do not contain the fake API key.
- Non-2xx body sentinel strings do not appear outside the fake response object.

TASK-037 implementation notes:

- `backend/tests/test_llm_provider_contract.py` verifies request method, `/v1/messages` endpoint, `x-api-key`, `anthropic-version`, `Content-Type`, `model`, `max_tokens`, `system`, and `messages`.
- It verifies no `stream` or `tools` fields are sent.
- It verifies text content blocks are parsed deterministically, non-text blocks are ignored, and usage is retained internally only.
- It verifies auth, rate limit, generic non-2xx, malformed JSON, empty text, timeout, and network failure mappings.
- It verifies no retries and no key/body/prompt/user-message/memory-context leakage.
- It verifies `/chat` remains compatible and is not wired to the real provider yet.

## Manual Live Smoke Checklist

TASK-038 is manual-only and opt-in. It is not a `/chat` smoke check because `/chat` is still not wired to the real provider.

Cost warning:

- Manual live smoke requires explicit cost confirmation.
- Live smoke must be exactly one minimal request.
- Do not proceed if the user has not accepted cost risk.
- Cost control and go/no-go criteria are tracked in `docs/COST_AND_MONETIZATION.md`.

Checklist:

- User explicitly confirms all of the following before any live call:
  - I have an Anthropic API key
  - I understand this may cost money
  - I want to run exactly one minimal live request
- User explicitly sets backend env vars for one run only:
  - `LLM_PROVIDER_ENABLED=true`
  - `LLM_PROVIDER_NAME=anthropic`
  - `LLM_API_KEY=<set outside git and outside docs>`
  - `LLM_MODEL=<confirmed Anthropic model id>`
  - `LLM_TIMEOUT_SECONDS=30`
  - `LLM_FALLBACK_TO_MOCK=true`
- User confirms cost risk before starting.
- Run provider adapter only, not `/chat`.
- Use one minimal prompt only.
- Keep memory disabled: do not send `memory_context`.
- Confirm response text is non-empty OR canonical safe fallback is returned.
- Confirm no API key appears in logs, stdout, stderr, responses, DB, or audit rows.
- Confirm no raw provider body is printed.
- Confirm no DB row or audit row is created by this adapter-only smoke.
- Confirm fallback behavior by temporarily using an invalid model or disabled key only if the user accepts possible provider-side cost/risk; otherwise test fallback with mocked runtime only.
- Clear provider env vars after test.
- Do not commit `.env`, logs, DB files, screenshots containing secrets, or shell history containing keys.

## Safety Boundaries

- No live calls in automated tests.
- No streaming.
- No tools.
- No retries.
- No frontend API key.
- No raw prompt logging.
- No raw user message logging.
- No raw memory context logging.
- No raw provider response body in frontend, logs, DB, or audit rows.
- No memory auto-write.
- No semantic retrieval.
- No vector DB.
- No autonomous agent actions.
- No Electron UI changes required for this contract.
