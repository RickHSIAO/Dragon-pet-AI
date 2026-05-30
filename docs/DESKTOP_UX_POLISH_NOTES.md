# Desktop UX Polish Notes — dragon-pet-ai

> Created: TASK-188 (2026-05-30)
> Updated: TASK-190 (2026-05-31) — Provider Settings manual smoke closeout added.
> Scope: Pet Window + Full App UX review after Screen Context v0.4 and provider stability pass.

This document records UX findings from TASK-188. Items marked **FIXED** were addressed in
the same task. Items marked **NOTED** are known issues deferred for future work.

---

## Fixed in TASK-188

### [FIXED] `clearScreenshot()` did not clear `capture-window-status`

**File:** `apps/desktop/src/renderer/renderer.js` — `clearScreenshot()`

**Problem:** After a window capture (`擷取視窗`), the `#capture-window-status` span shows
"視窗截圖完成。尚未儲存，可供後續分析使用。" Clicking "清除截圖" cleared the
`#capture-screen-status` but left the window status stale. The user saw conflicting messages:
- `#capture-screen-status` → "截圖已清除。"
- `#capture-window-status` → "視窗截圖完成。尚未儲存，可供後續分析使用。" ← stale

**Fix:** Added `setCaptureWindowStatus("", false)` in `clearScreenshot()` before the
`setCaptureScreenStatus` call.

**Test added:** `test188ClearWindowStatusAfterClear` in `task171a-capture-smoke.js`.

---

### [FIXED] Header version tag said "v0.1 skeleton"

**File:** `apps/desktop/src/renderer/index.html`

**Problem:** The `<span class="version-tag">v0.1 skeleton</span>` has been in the header
since TASK-003 (Phase 1 skeleton). The app is now at ~TASK-188 with full OCR, pet mode,
voice, TTS, provider settings, and Screen Context v0.4.

**Fix:** Changed to `dev`. Neutral, indicates ongoing development without committing to a
specific semantic version.

---

## Noted — Not Fixed

The following issues were identified but deferred. They are intentional design decisions,
developer-facing debug UI, or require more design consideration before changing.

### [NOTED] `#chat-source-status` initial value "source: not_checked"

The character status bar shows `source: not_checked` and `provider: mock` before any chat
response. These are developer-facing diagnostic pills, intentional for the current dev-phase
UI. `not_checked` sounds like an error but is just the initial state. Future consideration:
hide the pills until the first chat response, or change initial text to "—" / "等待中".

### [NOTED] Provider Settings section uses technical/developer labels

Labels like "Resolved provider", "Real provider enabled", "LLM chat enabled",
`key_status: not_configured`, `last_test: not_tested` are accurate but technical. This
section is developer-facing in the current UX — acceptable for the dev phase.

### [NOTED] "Save Non-secret Settings" button text is confusing

The provider settings form submit button says "Save Non-secret Settings". The "Non-secret"
qualifier is meant to distinguish from the key-save button, but is confusing without context.
Future: "Save Settings" with a note that API key is stored separately.

### [NOTED] Pet idle/handoff lines reference "Full App"

Pet idle presence lines say things like "去 Full App 說話。" and "可開 Full App 查看完整內容。"
"Full App" is an internal app term. New users may not understand what it refers to. However,
this is the established project terminology used consistently across all Pet text.

Future option: "主視窗" (main window) might be friendlier for non-developer users.

### [NOTED] Pet Menu "Toggle Details" is unclear

`#pet-menu-toggle-details` says "Toggle Details" without explaining what "details" are (it's
the source/provider diagnostic panel inside the speech bubble). A label like "詳細資訊" or
"顯示/隱藏診斷" would be clearer, but requires updating aria-expanded handling and any
references in pet-renderer-smoke.js.

### [NOTED] Pet bubble placeholder text is English

`#pet-bubble-placeholder` contains: "Display-only speech bubble. Type in Full App." This is
inside the hidden speech bubble and not visible in normal use. Low priority.

### [NOTED] Memory toggle technical hint

`#memory-toggle-hint` explains: "Requires backend MEMORY_INJECTION_ENABLED=true."
A general user does not know what this means. Since memory injection is not actively used
in the main workflow, this is acceptable for the current dev phase.

### [NOTED] Mixed English/Chinese in header

"Show Pet", "Send", "Mood:" are in English; capture/analyze buttons are in Chinese. This
is consistent with the current design where developer controls remain in English and
user-facing pet interaction buttons are in Chinese. Acceptable for dev phase.

---

## Reviewed — Unchanged by Design

| Area | Verdict |
|---|---|
| OCR ask hint `#ocr-ask-hint` | Clear and accurate. Not misleading. No change needed. |
| Screen capture status messages (zh-TW) | All map cleanly to user-visible zh-TW text. No raw codes exposed. |
| Pet speech bubble states | All 16 states render cleanly (tested by pet-renderer-smoke 226 checks). |
| Pet menu items (Quiet/Click-through/TTS) | Toggle labels with current state ("Off"/"On") are clear. |
| S/M/L scale presets in Pet menu | Clear visual grouping. No change needed. |
| Provider status grid | Intentionally developer-facing. No change. |
| `分析這張` confirmation dialog | Privacy warning covers passwords/keys/messages. Clear. |
| `問克莉絲蒂娜這個畫面` confirmation dialog | Privacy warning is appropriate. |
| `清除截圖` visibility logic | Hidden until screenshot exists, shown after capture. Correct. |

---

## Test Coverage After TASK-188

| Suite | Result | Change |
|---|---|---|
| `renderer-chat-smoke.js` | PASS | 1 new test in task171a-capture-smoke.js |
| `pet-renderer-smoke.js` | 226 checks PASS | No change |
| `pet-window-smoke.js` | 45 checks PASS | No change |
| `python -m pytest tests/ -q` | 667 PASS | No backend change |

---

## TASK-189 + TASK-190 — Provider Settings UI Polish Pass & Manual Smoke Closeout

> TASK-189: Completed 2026-05-30 — text, labels, summary bar
> TASK-190: Completed 2026-05-31 — manual smoke closeout, edge-case bug fix

### Changes Made in TASK-189

| Item | Before | After |
|---|---|---|
| Save button | "Save Non-secret Settings" | "Save Provider Settings" |
| Save note | (absent) | "Provider, model, and toggle settings only. API key is stored separately using the controls below." |
| Checkbox: real_provider_enabled | "Real provider enabled" | "Use real AI" |
| Checkbox: llm_chat_enabled | "LLM chat enabled" | "Enable AI chat" |
| Checkbox: fallback_to_mock | "Fallback to mock" | "Fall back to mock if AI fails" |
| Grid: Resolved provider | "Resolved provider" | "Active provider" |
| Grid: real_provider_enabled | "Real provider enabled" | "Real AI" |
| Grid: llm_chat_enabled | "LLM chat enabled" | "AI chat" |
| Grid: key_status | "Key status" | "API key" |
| Grid: fallback_to_mock | "Fallback to mock" | "Mock fallback" |
| `#chat-source-status` initial | "source: not_checked" | "—" |
| Section description | "Configure provider, model, and API key. Test Connection is available only after the safe preconditions are met." | "Configure your AI provider, model, and API key." |
| Runtime status messages | Started with `source=xxx -` technical prefix | Plain English (e.g. "Ollama response received.", "Local AI failed — …") |
| New element | — | `#provider-status-summary`: colour-coded plain-English state bar |

### Bug Fixed in TASK-190 (Static Analysis)

**`calcProviderStatusSummary` edge case:** When `key_status = "invalid"` or `"test_failed"` (key exists but failed), the summary incorrectly showed "API key not configured." Fixed to show "API key invalid or connection test failed." (error state).

---

### Provider Settings Manual Smoke Checklist

> For use when running the Full App in development. Run after `npm start` with backend live.

#### 1. Initial State (Mock / No Settings Changed)

- [ ] Open Full App — scroll to Provider Settings section
- [ ] `#provider-status-summary` shows **"Current: Mock mode — no real AI connected."** in muted text
- [ ] Save button reads **"Save Provider Settings"** (not "Save Non-secret Settings")
- [ ] Note below save button reads **"Provider, model, and toggle settings only. API key is stored separately…"**
- [ ] Checkbox labels read **"Use real AI"**, **"Enable AI chat"**, **"Fall back to mock if AI fails"**
- [ ] Status grid labels: **"API key"**, **"Active provider"**, **"Real AI"**, **"AI chat"**, **"Mock fallback"**
- [ ] `#chat-source-status` pill shows **"—"** (not "source: not_checked") before first chat
- [ ] `#chat-provider-status` pill shows **"provider: mock"** on load

#### 2. After Sending First Chat (Mock)

- [ ] `#chat-source-status` shows **"source: mock"** (technical pill — expected)
- [ ] `#chat-runtime-status` shows **"Using mock provider."** (no `source=mock -` prefix)
- [ ] `#chat-provider-status` shows **"Mock fallback"**

#### 3. Ollama Configured, real_provider_enabled ON, fallback OFF

*Prerequisites: backend running, Ollama running, model pulled. Provider = ollama, Use real AI = ✓, Enable AI chat = ✓, Fall back to mock = ✗, saved.*

- [ ] Summary shows **"Current: Ollama active — local AI connected."** in green
- [ ] Grid: "Active provider" = `ollama`, "Real AI" = `true` (green), "AI chat" = `true` (green), "Mock fallback" = `false` (muted)
- [ ] Send a chat → `#chat-source-status` = `source: llm_local`
- [ ] `#chat-runtime-status` = **"Ollama response received. Local AI is active."** (no raw prefix)
- [ ] `#chat-provider-status` = **"Local Ollama"**

#### 4. Ollama Configured, fallback ON

*Provider = ollama, Use real AI = ✓, Enable AI chat = ✓, Fall back to mock = ✓, saved.*

- [ ] Summary shows **"Current: Ollama with fallback — real AI when available, mock on failure."** in amber
- [ ] Grid: "Mock fallback" = `true` (amber or muted)

#### 5. Ollama Error / Timeout State

*Ollama stopped or model unavailable. Send chat with provider = ollama, real AI = ✓, AI chat = ✓, fallback = ✗.*

- [ ] `#chat-source-status` = `source: llm_local_error`
- [ ] `#chat-runtime-status` = **"Local AI failed — the model may still be loading. Check that Ollama is running and the model name is correct."**
- [ ] No raw traceback, no JSON, no raw HTTP response visible anywhere
- [ ] `#chat-provider-status` = **"Ollama Error"**

#### 6. Fallback to Mock After Ollama Error

*Provider = ollama, real AI = ✓, AI chat = ✓, fallback = ✓. Ollama stopped.*

- [ ] `#chat-source-status` = `source: mock`
- [ ] `#chat-runtime-status` = **"Using mock fallback — Ollama is configured but a provider error occurred and fallback is on."** (no `source=mock` prefix)

#### 7. AI Chat Disabled

*Provider = ollama, Use real AI = ✓, Enable AI chat = ✗, saved.*

- [ ] Summary shows **"Current: Ollama selected — AI chat is disabled. Enable 'AI chat' to use it."** in amber
- [ ] Send chat → `source: mock`, runtime = **"Using mock — AI chat is disabled. Enable 'AI chat' in Provider Settings to use Ollama."**

#### 8. Cloud Provider (Anthropic) — Key Not Configured

*Provider = anthropic, Use real AI = ✓, no API key saved.*

- [ ] Summary shows **"Current: anthropic selected — API key not configured."** in red/error
- [ ] API key input enabled, placeholder reads "Enter provider API key"
- [ ] "Save API Key" button visible; "Clear API Key" button hidden

#### 9. Cloud Provider — Key Invalid / Test Failed

*Provider = anthropic, key saved but connection test failed.*

- [ ] Summary shows **"Current: anthropic selected — API key invalid or connection test failed."** in red/error

#### 10. Test Connection — Ollama Success

*Provider = ollama, Use real AI = ✓, Ollama running. Click Test Connection.*

- [ ] Confirmation dialog appears: "Test Connection — Local Resource Warning…"
- [ ] After confirmation: `#provider-test-msg` shows success message (e.g., "Local Ollama connection successful") + `[source: llm_local]`
- [ ] No raw traceback, no JSON body, no API key in message

#### 11. Test Connection — Ollama Failure

*Provider = ollama, Use real AI = ✓, Ollama stopped. Click Test Connection.*

- [ ] `#provider-test-msg` shows a clean error (e.g., safe_message from backend)
- [ ] No raw traceback visible

#### 12. Save Provider Settings Does Not Clear API Key

*Cloud provider, key saved (key input shows placeholder "Enter provider API key").*

- [ ] Change model field, click Save Provider Settings
- [ ] API key input remains showing placeholder (cleared from DOM after save attempt, not stored anyway)
- [ ] `#provider-key-msg` does NOT show any error about the key

#### 13. Full App Chat — Regression Check

- [ ] Type a message in the chat input, press Enter
- [ ] Message appears in chat area
- [ ] Pet expression updates
- [ ] Chat reply arrives (mock or real depending on settings)
- [ ] No console errors related to Provider Settings changes

#### 14. Pet Window — Quick Regression Check

- [ ] Click "Show Pet" → Pet Window appears
- [ ] Pet bubble and menu work normally (no Provider Settings-related regression)
- [ ] Pet Window requires no re-test for Screen Context, TTS, or voice (not touched)

---

### Pre-existing Issues Noted (Not Introduced by TASK-189)

| # | Location | Issue | Status |
|---|---|---|---|
| N1 | `renderer.js` `lastChatSource` | Initialised as `"not_checked"` (truthy) so `syncChatRuntimeProviderStatus` "before first chat" branch (`!lastChatSource`) never runs; `#chat-provider-status` briefly shows `"not_checked"` between settings load and first chat response | NOTED — pre-existing, low impact |
| N2 | `#chat-runtime-status` initial text | "mock mode - no AI connected" — slightly technical; after first chat it updates to the friendly source message | NOTED — acceptable for dev phase |

---

### Test Coverage After TASK-189 + TASK-190

| Suite | Result | Change |
|---|---|---|
| `renderer-chat-smoke.js` | PASS | +3 updated assertions + 5 TASK-189 tests + 2 TASK-190 tests = +10 changes |
| `pet-renderer-smoke.js` | 226 checks PASS | No change (Pet not touched) |
| `pet-window-smoke.js` | 45 checks PASS | No change (Pet not touched) |
| `python -m pytest tests/ -q` | 667 PASS (baseline) | No backend change |
