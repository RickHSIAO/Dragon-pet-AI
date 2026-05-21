# Ollama Local Provider Design

> dragon-pet-ai
> Task: TASK-072
> Status: IMPLEMENTED AND CONTRACT TESTED - TASK-073 and TASK-074 DONE; runtime smoke pending (TASK-075)
> Last Updated: 2026-05-21

---

## Purpose

This document designs the integration of Ollama as a local LLM provider option for dragon-pet-ai.

**Why Ollama?**

The existing provider architecture supports Anthropic (cloud, requires API key, incurs cost) and Mock (no-op). Adding Ollama enables a third path: a fully local model that runs on the user's hardware, requires no API key, incurs no per-token cost, and never sends data to an external server.

This aligns with the project's local-first design principle and unblocks live LLM testing without requiring the user to accept external provider cost risk.

| Attribute | Anthropic | Ollama |
|---|---|---|
| API key required | Yes | No |
| External network call | Yes | No — localhost only |
| Cost | Per-token billing | Free (local compute) |
| Privacy | Data leaves device | Data stays on device |
| Latency | Network-dependent | Hardware-dependent |
| Explicit cost ack | Required (TASK-058) | Not required — local resource warning instead |

**Provider name:** `ollama`
**Default model candidate:** `qwen3:8b`
**Endpoint:** `http://localhost:11434`

---

## Local Model Test Results

Tests conducted manually on the development machine using PowerShell with UTF-8 encoded request bodies.

### Issue Fixed: UTF-8 Encoding in PowerShell

By default, PowerShell's `Invoke-RestMethod` sends request bodies as UTF-16. The Ollama API requires UTF-8. Fix:

```powershell
$body = '{"model":"qwen3:8b","stream":false,"think":false,"messages":[{"role":"user","content":"Reply with OK."}]}'
$bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
Invoke-RestMethod -Method POST -Uri http://localhost:11434/api/chat `
  -ContentType "application/json; charset=utf-8" `
  -Body $bytes
```

### qwen3:8b

| Metric | Value |
|---|---|
| First response (cold) | Slower — model loading |
| Second response (warm) | ~0.35 seconds |
| Throughput | ~73 tokens/second |
| Quality | Good — follows instructions, concise |
| Verdict | **Recommended — first local MVP model** |

### gemma3:12b

| Metric | Value |
|---|---|
| First response (cold) | Slow |
| Second response (warm) | ~3.48 seconds |
| Throughput | ~13 tokens/second |
| Quality | Warmer, more natural tone |
| Verdict | Usable but significantly slower; better for longer companion-style responses when latency is acceptable |

### Recommendation

Use `qwen3:8b` as the default local model for MVP integration. `gemma3:12b` can be an opt-in alternative via `LLM_MODEL` env var.

---

## Ollama API Contract

### Request

```
POST http://localhost:11434/api/chat
Content-Type: application/json; charset=utf-8
```

```json
{
  "model": "qwen3:8b",
  "stream": false,
  "think": false,
  "keep_alive": "10m",
  "options": {
    "temperature": 0.7,
    "num_predict": 256
  },
  "messages": [
    {
      "role": "system",
      "content": "<system prompt>"
    },
    {
      "role": "user",
      "content": "<user message>"
    }
  ]
}
```

**Field notes:**
- `stream: false` — required; streaming is explicitly out of scope for Phase 4
- `think: false` — disables chain-of-thought reasoning tokens (qwen3 feature); keeps response compact
- `keep_alive: "10m"` — keeps model loaded in memory for 10 minutes after last request; avoids cold-start latency on subsequent messages
- `options.temperature` — controls response randomness; 0.7 is a reasonable companion default
- `options.num_predict` — max output tokens; 256 is sufficient for short companion responses

### Response

```json
{
  "model": "qwen3:8b",
  "message": {
    "role": "assistant",
    "content": "OK."
  },
  "done": true,
  "eval_count": 3,
  "prompt_eval_count": 42
}
```

### Response Mapping to LLMResponse

| Ollama field | LLMResponse field | Notes |
|---|---|---|
| `message.content` | `text` | Main reply text |
| `model` | `model` | Confirmed model name |
| `eval_count` | usage `output_tokens_actual` | Output token count from Ollama |
| `prompt_eval_count` | usage `input_tokens_actual` | Input token count from Ollama |
| — | `provider` | Set to `"ollama"` by adapter |
| — | `error` | `None` on success; category string on failure |

### Error Categories

| Category | When |
|---|---|
| `ollama_unavailable` | Connection refused to `localhost:11434`; Ollama not running |
| `model_not_found` | 404 from Ollama; model not pulled |
| `provider_timeout` | Request exceeds `OLLAMA_TIMEOUT_SECONDS` |
| `invalid_response` | Response body does not match expected schema |
| `provider_error` | Any other unexpected failure |

All error categories map to safe human-readable messages via `SAFE_ERROR_MESSAGES`. Raw Ollama response bodies are never forwarded to the frontend.

---

## Provider Settings Integration

### New Provider Option

The provider selector in the UI gains a third option:

```
mock      — always-on, no cost, no key
anthropic — cloud provider, requires API key, BYOK
ollama    — local provider, no key, no external call
```

### Behavior Differences for `provider=ollama`

| Setting | anthropic | ollama |
|---|---|---|
| API key input | Enabled | **Disabled** (no key needed) |
| key_status | configured / not_configured / unavailable | **not_required** |
| Save Key button | Enabled when key input has value | **Hidden or permanently disabled** |
| Clear Key button | Enabled when key configured | **Hidden or permanently disabled** |
| Test Connection | Enabled when key configured + real_provider_enabled | **Enabled when real_provider_enabled=true** (no key check) |
| Test Connection cost ack | Required — monetary cost disclosure | **Local resource warning only** |

### Key Status Value

A new safe key status value is required: `not_required`. This is added alongside the existing 6 values:

| Value | Meaning |
|---|---|
| `not_configured` | Storage backend available but no key saved |
| `configured` | Key saved and available |
| `unavailable` | Storage backend unavailable (503) |
| `not_supported` | Provider does not use a key |
| `storage_error` | Error reading from storage |
| `unknown` | Cannot determine status |
| **`not_required`** ← new | Provider does not require an API key (e.g., Ollama) |

---

## Feature Flags / Environment Variables

All new env vars follow the existing pattern: startup-time only, never runtime-patched, never returned to frontend.

| Variable | Default | Purpose |
|---|---|---|
| `LLM_PROVIDER_NAME` | `mock` | Set to `ollama` to activate Ollama adapter |
| `LLM_MODEL` | *(provider default)* | Set to `qwen3:8b` for Ollama MVP |
| `LLM_PROVIDER_ENABLED` | `false` | Must be `true` to use any real provider |
| `LLM_CHAT_ENABLED` | `false` | Must be `true` to route `/chat` through LLM adapter |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server endpoint |
| `OLLAMA_KEEP_ALIVE` | `10m` | Keep model loaded in memory after last request |
| `OLLAMA_TIMEOUT_SECONDS` | `30` | Request timeout; Ollama can be slow on first load |

### .env.example additions

```dotenv
# --- Ollama local provider ---
# LLM_PROVIDER_NAME=ollama
# LLM_MODEL=qwen3:8b
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_KEEP_ALIVE=10m
# OLLAMA_TIMEOUT_SECONDS=30
```

### Minimum config to enable Ollama in development

```dotenv
LLM_PROVIDER_NAME=ollama
LLM_MODEL=qwen3:8b
LLM_PROVIDER_ENABLED=true
LLM_CHAT_ENABLED=true
```

---

## Test Connection Behavior for Ollama

The existing Test Connection endpoint (`POST /provider/settings/test`) must be adapted for the Ollama case.

### Differences from Anthropic Test Connection

| Rule | Anthropic | Ollama |
|---|---|---|
| `explicit_cost_ack` required | Yes — monetary cost disclosure | **Local resource warning only** — see below |
| API key required | Yes | No |
| External network | Yes | No — localhost only |
| Cost | Per-token | Free |

### Local Resource Warning

For Ollama, `explicit_cost_ack` is not required in the monetary sense, but the UI should still show a one-click confirmation:

> "This will send a test request to your local Ollama server and use your GPU/CPU. No data leaves your device."

This preserves the intentional-click safety pattern without implying monetary cost.

### Test Request (same as existing minimal request)

```json
{
  "model": "qwen3:8b",
  "stream": false,
  "think": false,
  "messages": [
    {"role": "system", "content": "You are a provider connection test. Reply only with OK."},
    {"role": "user", "content": "Reply with OK."}
  ],
  "options": {"num_predict": 16}
}
```

- Exactly one request — no retries
- No memory, no chat history, no tools, no streaming
- 16 output tokens max
- `think: false` — no reasoning tokens

### Safe Response Fields (unchanged schema)

```json
{
  "status": "ok",
  "safe_message": "Local Ollama connection successful.",
  "error_category": null,
  "source": "llm_local",
  "provider": "ollama",
  "model": "qwen3:8b",
  "usage_estimate": {"input_tokens": 12, "output_tokens": 2}
}
```

---

## /chat Behavior for Ollama

When `LLM_PROVIDER_ENABLED=true`, `LLM_CHAT_ENABLED=true`, and `LLM_PROVIDER_NAME=ollama`:

1. `/chat` receives `POST {"message": "...", "use_memory": false}`
2. `chat_service` builds the prompt (system prompt + user message; memory context if two-layer gate allows)
3. `OllamaLocalProvider.chat()` is called — identical interface to `AnthropicProvider.chat()`
4. Ollama returns a response; adapter maps it to `LLMResponse`
5. `/chat` returns `ChatResponse`:

```json
{
  "reply": "<model response>",
  "mood": "neutral",
  "source": "llm_local"
}
```

**`source` value:** `llm_local` on success; `llm_local_error` on failure. Implemented in TASK-075F via `_LOCAL_PROVIDER_NAMES = frozenset({"ollama"})` in `chat_service.py`. This decision is now final — `llm_local` is the stable source value for all local providers.

**What does NOT change:**
- `/chat` request and response schema — unchanged (`message`, `use_memory` in; `reply`, `mood`, `source` out)
- Memory injection two-layer gate — unchanged
- Memory audit logging — unchanged
- Usage meter — extended with `provider=ollama`, `source=llm_local`
- Fallback behavior — on failure, returns `source=llm_local_error` (no fallback to mock)

---

## Usage Meter Integration

The existing usage meter records 14 fields. For Ollama requests:

| Field | Value |
|---|---|
| `provider` | `ollama` |
| `model` | `qwen3:8b` (or whatever `LLM_MODEL` is set to) |
| `source` | `llm_local` |
| `input_tokens_actual` | `prompt_eval_count` from Ollama response |
| `output_tokens_actual` | `eval_count` from Ollama response |
| `input_tokens_estimated` | Used only if Ollama does not return counts |
| `output_tokens_estimated` | Used only if Ollama does not return counts |
| `status` | `ok` or `failed` |
| `error_category` | One of the 5 Ollama error categories, or `null` |
| `is_test_connection` | `true` for Test Connection calls, `false` for /chat |

**What is never recorded:**
- Raw prompt text
- Raw user message
- Memory context content
- Raw Ollama response body
- Any field containing model-generated text

---

## Security Boundaries

These boundaries must hold exactly as they do for the Anthropic provider.

| Boundary | Rule |
|---|---|
| Renderer ↔ Ollama | Renderer never calls Ollama directly — only calls local backend (:8000) |
| Ollama URL in renderer | `http://localhost:11434` must not appear in any Electron renderer file |
| Prompt logging | Raw prompt text is never logged at any level |
| Response body forwarding | Raw Ollama response body is never forwarded to the frontend |
| Automatic background calls | No periodic polling, no auto-test, no background keep-alive pings |
| Retries | No automatic retries — exactly one request per user action |
| Streaming | Not implemented; `stream: false` enforced |
| Tool use | Not implemented in Phase 4 |
| Memory in Test Connection | Memory context never included in the test request |

**Why "renderer never calls Ollama directly" matters:** Even though Ollama is localhost and carries no API key, routing through the backend preserves the architecture boundary — all LLM interaction goes through the service layer, which enforces logging rules, usage metering, and response sanitization.

---

## Adapter Implementation Notes (for TASK-073)

These are design hints to guide the implementation task, not implementation code.

**Class name:** `OllamaLocalProvider`

**Interface:** Must implement the same `ProviderInterface` as `AnthropicProvider`:
```python
class OllamaLocalProvider:
    def chat(self, *, prompt: str, system: str, model: str, max_tokens: int) -> LLMResponse:
        ...
```

**HTTP client:** Use `httpx` (already a project dependency) with a configurable timeout from `OLLAMA_TIMEOUT_SECONDS`.

**No API key parameter:** `OllamaLocalProvider.__init__` does not accept an `api_key` argument.

**Provider factory:** `provider_factory.py` must recognize `LLM_PROVIDER_NAME=ollama` and return `OllamaLocalProvider()`. If Ollama is unavailable and `LLM_FALLBACK_TO_MOCK=true`, fall back to MockProvider with a non-sensitive warning log.

**`__repr__` / `__str__`:** No secrets to redact for Ollama (no API key), but follow the same pattern for consistency.

**Content-Type:** Must send `Content-Type: application/json; charset=utf-8`. The Ollama server requires UTF-8 encoding.

---

## Future Implementation Sequence

| Task | Name | Type |
|---|---|---|
| TASK-072 | Local Ollama Provider Design | Design — **DONE** |
| TASK-073 | Ollama Provider Implementation Behind Feature Flag | **DONE** |
| TASK-074 | Ollama Provider Contract Tests and Runtime Smoke Prep | **DONE** |
| TASK-075 | Ollama Runtime Smoke Check | Manual smoke |
| TASK-076 | Provider Settings UI — Ollama Option | Implementation |
| TASK-077 | README Update for Local LLM Mode | Docs |

### TASK-074 completion notes

- Mocked Ollama provider contract coverage strengthened to 34 tests.
- Request schema coverage includes `model`, `stream=false`, `think=false`, `keep_alive`, `options.temperature`, `options.num_predict`, and ordered system/user `messages`.
- Negative payload coverage confirms no API key, no tools, no streaming, no top-level raw memory context, and no conversation history in the Ollama request body.
- Localhost-only behavior is covered: default localhost, `localhost:11434`, `127.0.0.1:11434`, and external URL fallback to safe default.
- No-key behavior is covered: `provider=ollama` resolves without `LLM_API_KEY`, and API key env values are not sent in request body or headers.
- Usage mapping now covers `prompt_eval_count`, `eval_count`, `total_duration`, and `eval_duration` as safe aggregate metadata.
- Safe error mapping and raw body opacity are covered with sentinel values.
- No-retry behavior is covered by fake HTTP client call counts.
- `docs/OLLAMA_RUNTIME_SMOKE_CHECKLIST.md` added for TASK-075.
- Full backend pytest: 504 passed.
- No live Ollama smoke was executed in TASK-074.
- No external provider call was made and no API key was used.

### TASK-073 scope (preview)

- Add `OllamaLocalProvider` class under `backend/app/providers/`
- Add Ollama env var config helpers under `backend/app/core/config.py`
- Update `provider_factory.py` to recognize `ollama`
- Add `not_required` to key status enum
- Add Ollama error categories to `SAFE_ERROR_MESSAGES`
- No Electron UI changes in TASK-073 (UI is TASK-076)
- No live Ollama call in tests (TASK-074 uses mocked httpx)

### TASK-074 scope (preview)

- Mock `httpx.post` to return a valid Ollama response fixture
- Test: successful response maps to `LLMResponse` correctly
- Test: `eval_count` and `prompt_eval_count` land in usage meter
- Test: connection refused → `ollama_unavailable`
- Test: 404 model not found → `model_not_found`
- Test: timeout → `provider_timeout`
- Test: malformed response → `invalid_response`
- No live Ollama server required

### TASK-075 scope (preview)

- Start Ollama (`ollama serve`)
- Ensure `qwen3:8b` is pulled (`ollama pull qwen3:8b`)
- Set env vars: `LLM_PROVIDER_NAME=ollama`, `LLM_MODEL=qwen3:8b`, `LLM_PROVIDER_ENABLED=true`, `LLM_CHAT_ENABLED=true`
- Verify `POST /chat` returns `source=llm_local` and a non-empty reply
- Verify usage meter records the call
- Verify no prompt text in logs

---

## Reference Documents

| Document | Topic |
|---|---|
| `docs/LLM_ADAPTER_DESIGN.md` | LLM adapter architecture: `ProviderInterface`, feature flags, safety rules |
| `docs/LLM_PROVIDER_CONTRACT.md` | Anthropic request/response/error mapping — reference for Ollama contract design |
| `docs/PROVIDER_TEST_CONNECTION_DESIGN.md` | Test Connection design: explicit cost ack, minimal request, safe response |
| `docs/SECURE_KEY_STORAGE_DESIGN.md` | Key storage — Ollama bypasses this entirely |
| `docs/CHAT_LLM_REAL_PROVIDER_WIRING_DESIGN.md` | Real-provider /chat wiring — Ollama follows the same pattern |
| `docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md` | Full Phase 4 Provider Settings summary |
| `docs/COST_AND_MONETIZATION.md` | Live smoke go/no-go — Ollama bypasses the cost gate |
