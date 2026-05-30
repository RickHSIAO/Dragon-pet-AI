# Desktop UX Polish Notes — dragon-pet-ai

> Created: TASK-188 (2026-05-30)
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
