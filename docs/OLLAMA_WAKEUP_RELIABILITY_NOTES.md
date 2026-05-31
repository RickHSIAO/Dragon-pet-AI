# Ollama Wake-up / First Chat Reliability Notes

> Task: TASK-197
> Date: 2026-05-31

---

## Problem

After app restart, the first chat via Ollama often hangs or times out. Root causes:

1. **No startup liveness check** — the app has no way to tell the user whether Ollama is ready.
2. **Model cold-start latency** — Ollama must load the model into VRAM on first inference request. This takes 5–60 seconds depending on model size and GPU.
3. **No startup fetch timeout** — if the backend is offline, the startup `/health` fetch could hang indefinitely.
4. **English status messages** — inconsistent with the Chinese UI introduced in TASK-195.

## Fixes Applied (TASK-197)

### 1. Startup `/health` fetch — AbortController timeout

```javascript
const _healthCtrl = new AbortController();
const _healthTimer = setTimeout(() => _healthCtrl.abort(), 8000);
try {
  const res = await fetch(`${BACKEND_URL}/health`, { signal: _healthCtrl.signal });
  clearTimeout(_healthTimer);
  // ...
} catch {
  clearTimeout(_healthTimer);
  // error path
}
```

If the backend doesn't respond in 8 seconds, the fetch aborts and the offline error path runs. This prevents the app from hanging silently on startup.

### 2. `sourceStatusMessage()` — full Chinese translation

All 8 source branches translated to Chinese:

| Source | Message |
|---|---|
| `llm_local` | `"Ollama 已回覆。本地 AI 正常運作。"` |
| `llm_local_error` | `"本地 AI 失敗 — 模型可能仍在載入中。請確認 Ollama 正在執行且模型名稱正確。"` |
| `mock` (disabled) | `"使用模擬模式 — AI 聊天已停用。請在 AI 設定中啟用「啟用 AI 聊天」。"` |
| `mock` (fallback) | `"使用模擬備援 — 已設定 Ollama，但發生錯誤且已啟用備援模式。"` |
| `mock` (Ollama unresponsive) | `"使用模擬模式 — 已選擇 Ollama 但未回應。請確認 Ollama 是否已啟動。"` |
| `mock` (other) | `"使用模擬 provider。"` |
| `llm_real` | `"雲端 AI 已回覆。"` |
| `llm_real_error` | `"雲端 AI 失敗。請確認 API 金鑰與 provider 設定。"` |
| `pending` (Ollama) | `"等待本地 Ollama 回應中。第一次回覆可能需要較久，模型可能正在喚醒。"` |
| `pending` (other) | `"等待後端回覆中。"` |
| `backend_offline` | `"後端無法連線。請確認後端服務正在執行。"` |

### 3. `sendMessage()` loading text — Chinese

During the fetch-in-progress state, the loading bubble now shows:
- Ollama path: `"本地 AI 喚醒中，第一次回覆可能需要較久..."`
- Non-Ollama: `"等待後端回覆中..."`

### 4. `/provider/health` backend endpoint

```
GET /provider/health
```

Response schema:
```json
{"provider": "ollama", "ollama_reachable": true, "status": "ok"}
{"provider": "ollama", "ollama_reachable": false, "status": "unavailable"}
{"provider": "mock", "ollama_reachable": null, "status": "not_applicable"}
```

Returns `not_applicable` when the configured provider is not Ollama or when `real_provider_enabled` is false. Only performs a GET `/api/tags` reachability check — no model load, no `/api/chat`.

#### Service layer

`check_ollama_server_liveness()` in `provider_test_connection_service.py`:

```python
def check_ollama_server_liveness() -> bool:
    local_provider = OllamaLocalProvider(model="", ...)
    return local_provider._ollama_server_reachable()
```

`_ollama_server_reachable()` issues `GET /api/tags` with a 5-second hardcoded timeout. Returns `True` if the response is 200 OK.

### 5. `checkLocalProviderLiveness()` — non-blocking startup probe

```javascript
async function checkLocalProviderLiveness() {
  if (!isOllamaChatPath()) return;
  // ...
  el.textContent = "正在檢查本地 AI...";
  const res = await fetch(`${BACKEND_URL}/provider/health`);
  // ...
  if (data.ollama_reachable === true) {
    if (!currentProviderSettings.fallback_to_mock) {
      el.textContent = "Ollama 本地 AI 已就緒。";
    } else {
      // Preserve fallback warning — it's more important than the "ready" status
      el.textContent = prevText;
    }
  } else {
    el.textContent = "Ollama 尚未回應。第一次聊天可能需要較久，請確認 Ollama 已啟動。";
  }
}
```

Called **without `await`** after `loadProviderSettings()` — runs in background, does not block startup.

**Side-effect constraints:**
- Updates `#provider-status-summary` only
- No `appendMessage()` call — nothing written to chat history
- No `updatePetSpeech()` call — no Pet/TTS trigger
- No `/chat` fetch
- Errors (network, parse) silently restore the previous chip text

## Design Decisions

### Why not auto-send a warmup message?

Warmup messages would appear in chat history, confuse the user, and trigger Pet/TTS. The liveness check is purely a passive observation — it uses GET `/api/tags` which is a no-op for the model.

### Why AbortController (8s) and not a shorter timeout?

The backend's own Ollama timeout (configurable, default 30s) is the real bound on how long a chat can take. The startup `/health` fetch should be fast (sub-second if backend is up) — 8s is generous enough to avoid false timeouts on slow machines while still protecting against indefinite hangs.

### Why preserve the fallback warning over "已就緒"?

If `fallback_to_mock` is enabled, the user intentionally chose to allow mock fallbacks. The fallback warning is configuration-level information and is more actionable ("I know my setup has a risk") than a transient liveness result ("Ollama is reachable right now"). The unreachable case still shows the warning regardless of fallback.

## Limitations

- The liveness check uses `GET /api/tags` (server-level ping), not a model-level inference test. A responsive Ollama server with a missing or corrupted model would show "已就緒" but the first real chat would still fail.
- The 5-second timeout in `_ollama_server_reachable()` is hardcoded in the service. A slow Ollama startup might still time out this probe.
- No retry logic — if the probe fails on startup, the user sees "Ollama 尚未回應" and must wait for a chat reply to get updated status.
