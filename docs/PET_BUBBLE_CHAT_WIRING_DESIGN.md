# Pet Bubble Chat Wiring Design

> Task: TASK-132 - Pet Bubble Chat `/chat` Wiring Design
> Date: 2026-05-24
> Status: DESIGN ONLY - no runtime implementation

This document designs how Pet Bubble Chat should safely connect to the existing backend `/chat` endpoint in a later implementation task.

TASK-132 does not modify runtime code, backend routes, APIs, or `/chat` schema.

## 1. Goals

Pet Bubble Chat should become the compact chat surface for Pet Mode without copying the full management UI.

Goals:

- Let the user type a short message in the Pet bubble.
- Send that message to the existing local backend `/chat`.
- Render the AI `reply` inside the bubble.
- Use backend `mood` to update Christina's Pet Mode expression.
- Show a compact source/status signal.
- Preserve the `220 x 280` Pet Window constraints.
- Keep Full App as the troubleshooting and full-history surface.

Non-goals for the wiring MVP:

- Do not add memory management UI to Pet Mode.
- Do not copy Provider Settings into Pet Mode.
- Do not add new backend endpoints.
- Do not change `/chat` response schema.
- Do not add autonomous or proactive LLM calls.

## 2. `/chat` Schema

Pet Bubble Chat should reuse the existing `/chat` request and response contract.

Expected response fields:

- `reply`
- `mood`
- `source`

The wiring MVP should not require a schema change.

Reason:

- Full App already depends on this contract.
- Backend pytest coverage already validates `/chat` behavior.
- Pet Mode can derive all MVP UI states from transport status plus `reply`, `mood`, and `source`.
- Adding Pet-only metadata would increase backend surface area before the Pet bubble UX is proven.

If a future task proposes a schema change, it should first document why `reply / mood / source` is insufficient and include compatibility tests for Full App.

## 3. UI State Design

Pet Bubble Chat should use a small explicit state machine.

| State | Meaning | UI behavior |
|---|---|---|
| `collapsed` | Bubble hidden. | Show avatar, hint, and action row. |
| `expanded` | Bubble open but idle. | Show latest local message/reply area, input, send button. |
| `composing` | User is typing. | Input enabled, Send enabled only when trimmed input is non-empty. |
| `empty_input` | User clicks Send with empty text. | Do not call `/chat`; show local hint. |
| `pending` | Request in flight. | Disable input and Send; show pending text; keep Collapse/Menu usable. |
| `success` | `/chat` returned usable `reply`. | Render reply, update mood/expression, show source badge. |
| `backend_offline` | Local backend cannot be reached. | Show short offline hint and Open Full App path. |
| `llm_local_error` | Backend returned `source=llm_local_error` or equivalent safe local provider failure. | Show cold-start/provider hint; do not retry automatically. |
| `timeout` | HTTP timeout or provider timeout category. | Show local cold-start hint and Open Full App path. |
| `fallback_mock` | Backend returns `source=mock`. | Render reply with a compact mock badge. |
| `long_reply` | Reply exceeds compact bubble space. | Scroll inside bubble and offer Open Full App for full reading. |

State transitions:

- `collapsed -> expanded`: Chat button, avatar click, or existing bubble open hook.
- `expanded -> composing`: User types non-empty input.
- `composing -> pending`: User sends non-empty input.
- `pending -> success`: HTTP 200 with `reply`.
- `pending -> backend_offline`: fetch/network failure.
- `pending -> timeout`: request timeout or backend timeout response.
- `pending -> llm_local_error`: response `source=llm_local_error`.
- `pending -> fallback_mock`: response `source=mock`.
- Any open state -> `collapsed`: close control.

## 4. Loading, Timeout, And Cold-start UX

Send behavior:

- Trim the input before sending.
- Empty input must not call `/chat`.
- During `pending`, disable input and Send button.
- Keep Collapse, Menu, and Open Full App usable.
- Preserve typed text until a request is accepted; after success, clear input.

Pending copy:

- Primary pending hint: `吾正在想，別催。`
- Secondary neutral fallback if encoding is a concern: `Thinking...`

Timeout/cold-start behavior:

- If the request times out, show a short message that the local model may still be waking up.
- Do not show raw provider diagnostics in the bubble.
- Do not retry automatically.
- Provide Open Full App as the troubleshooting path.

Recommended timeout display:

- Badge: `local timeout`
- Message: `Local model may still be waking up. Open Full App for provider status.`

The bubble must never look stuck:

- Pending state must always show visible text.
- Send button must visibly change disabled/loading state.
- Timeout must return controls to usable state.
- Collapse/Menu must remain usable during failures.

## 5. Source Display

The bubble should show a compact source badge, not a verbose diagnostics panel.

| Source | Badge | Bubble hint |
|---|---|---|
| `llm_local` | `local` | Normal local response. |
| `mock` | `mock` | Mock fallback response; Full App can explain provider state. |
| `llm_local_error` | `local error` | Local provider failed or timed out safely. |
| backend offline | `offline` | Backend is unreachable. |
| unknown source | `source ?` | Render reply if present, but keep status conservative. |

Display rules:

- Badge should be small and secondary.
- Do not render raw backend/provider error bodies.
- Keep detailed provider troubleshooting in Full App.
- Open Full App should be visible or easy to reach when source is not `llm_local`.

## 6. Mood And Expression Integration

Pet Bubble Chat should use backend `mood` to update the Pet Mode expression after a successful response.

Suggested expression mapping:

- `happy` -> existing Christina happy PNG if available.
- `focused` -> existing focused PNG if available.
- `proud` -> existing proud PNG if available.
- `annoyed` -> existing annoyed PNG if available.
- `neutral` -> existing neutral PNG.
- unknown mood -> neutral fallback.

Request lifecycle expression hints:

- `pending` -> pending expression if available; otherwise focused or neutral fallback.
- `backend_offline` -> offline expression if available; otherwise error or neutral fallback.
- `llm_local_error` / timeout -> error expression if available; otherwise focused/neutral fallback.
- `mock` reply should still follow the returned `mood`; source should not force expression unless the response is an error.

Implementation guidance:

- Reuse the existing Pet Mode expression asset path pattern.
- Keep expression updates local to Pet renderer.
- Do not add backend expression metadata.
- Do not change `/chat` schema.

## 7. Long Reply Handling

The Pet Window is fixed at `220 x 280`, so the bubble must be constrained.

Recommended layout:

- Bubble max height: fit within the Pet Window without covering the action row.
- Reply body: `overflow-y: auto`.
- Preserve line breaks but wrap long words.
- Keep input visible unless the bubble is in a read-only error state.
- Avoid expanding the BrowserWindow for long replies.

Long reply policy:

- Do not hard-truncate by default.
- Scroll the reply area.
- If the reply is very long, show a local hint: `Open Full App for more room.`
- Open Full App should be the full-reading path.

## 8. Safety Boundaries

Pet Bubble Chat wiring must preserve these boundaries:

- Pet renderer does not directly call Ollama.
- Pet renderer calls only the local backend.
- Pet renderer does not read files.
- Pet renderer does not read Email.
- Pet renderer does not read Calendar.
- Pet renderer does not execute commands.
- Pet renderer does not call external APIs.
- Pet Mode does not secretly take screenshots.
- Pet Mode does not record audio.
- Pet Mode does not monitor the screen.
- Pet Mode does not modify provider settings.
- Pet Mode does not change `/chat` schema.
- Pet Mode does not add arbitrary IPC.
- Preload does not expose arbitrary `ipcRenderer`.
- Preload does not expose fs, shell, or process.
- Pet Bubble Chat does not send messages automatically.
- User must explicitly click Send or press the accepted send shortcut.

## 9. Implementation Task Breakdown

Recommended next tasks:

- TASK-133 - Pet Bubble Chat Static State Refinement
  - Refine DOM hooks, state attributes, disabled states, empty input hints, and CSS constraints without calling `/chat`.
- TASK-134 - Pet Bubble `/chat` Client Wiring
  - Add local backend `/chat` request from Pet renderer using existing schema.
- TASK-135 - Pet Bubble Loading/Error UX
  - Add pending, backend offline, timeout, local error, and fallback mock displays.
- TASK-136 - Pet Bubble Mood/Expression Integration
  - Map response `mood` and error states to Christina expression assets.
- TASK-137 - Pet Bubble Long Reply Handling
  - Add constrained scroll behavior and Open Full App path for long replies.
- TASK-138 - Pet Bubble Chat Smoke Tests
  - Add mocked renderer smoke tests for success, empty input, pending, offline, timeout, mock fallback, and no direct Ollama access.
- TASK-139 - Manual Windows Pet Bubble Chat Smoke
  - Validate the wired bubble on Windows with local backend and optional local Ollama.

## 10. Explicit Non-goals For TASK-132

TASK-132 does not:

- Modify runtime code.
- Modify backend code.
- Add a backend route.
- Add an API.
- Wire Pet Bubble Chat to `/chat`.
- Change `/chat` schema.
- Add images.
- Add external services.
- Change provider settings.
- Change Ollama routing.

## 11. Recommendation

Proceed with TASK-133 before wiring network behavior.

The reason is pragmatic: the Pet Window is small, and the state/layout constraints should be stable before `/chat` request handling is added.

## 12. TASK-133 Static State Checkpoint

Status: DONE on 2026-05-24.

TASK-133 implemented the static Pet Bubble state foundation without wiring backend chat.

Completed:

- Added explicit DOM hooks for bubble status, message, response, placeholder, input, and send button.
- Added local renderer state rendering through `BUBBLE_STATES` and `setBubbleState(...)`.
- Added local states for `collapsed`, `expanded`, `composing`, `empty_input`, `pending`, `success`, `backend_offline`, `timeout`, `llm_local_error`, `fallback_mock`, and `long_reply`.
- Added local placeholder handling for empty input and non-empty send preview.
- Added fixed `220 x 280` layout constraints and an internal scroll response area.
- Preserved no-drag interaction zones and explicit drag handle behavior.
- Updated Pet renderer smoke checks for state hooks, placeholders, no-drag boundaries, no `fetch(`, no `/chat` call, and no direct Ollama `11434` reference.

Still deferred:

- Real `/chat` request wiring.
- Backend offline detection from transport errors.
- Real `source` display from backend response.
- Real `mood` to expression updates from backend response.
- Long reply behavior with real backend replies.

Safety confirmation:

- No backend code changed.
- `/chat` schema remains `reply`, `mood`, `source`.
- Pet renderer still does not call backend or `/chat`.
- No IPC or preload API was added.
- No provider settings, Ollama routing, external API, file access, Email access, Calendar access, image, screenshot, microphone, or screen monitoring behavior was added.

Next recommendation:

- TASK-134 - Pet Bubble `/chat` Client Wiring.

## 13. TASK-134 `/chat` Client Wiring Checkpoint

Status: DONE on 2026-05-24.

TASK-134 implemented the first Pet Bubble Chat backend wiring without modifying backend code or `/chat` schema.

Completed:

- Pet Bubble submit now posts non-empty input to the existing local backend `/chat`.
- Request shape follows Full App chat behavior:
  - `message`
  - `use_memory`
- Pet Mode has no memory toggle, so `use_memory` is fixed to `false`.
- Response parsing uses the existing `/chat` fields:
  - `reply`
  - `mood`
  - `source`
- `reply` renders inside the constrained Pet bubble response area.
- Successful send clears the input after the response returns.
- Offline/error paths preserve input so the user can retry.
- Pet HTML CSP now allows only local backend connections to `http://localhost:8000` and `http://127.0.0.1:8000`.

Source mapping:

- `llm_local` renders as `success` or `long_reply` with compact `local` status.
- `mock` renders as `fallback_mock` with `mock fallback` status.
- `llm_local_error` renders as `llm_local_error`.
- Network fetch failure renders as `backend_offline`.
- Dedicated timeout handling remains deferred until a timeout helper is introduced.

Mood / expression mapping:

- Supported moods map to existing Christina expression PNG assets:
  - `neutral`
  - `focused`
  - `happy`
  - `proud`
  - `annoyed`
  - `worried`
  - `sleepy`
- Unknown mood falls back to `neutral`.
- Pending, backend offline, and local error currently fall back to `neutral`.
- No image asset was added.

Long reply handling:

- Replies above the compact threshold render `long_reply`.
- The existing internal scroll response area prevents the `220 x 280` Pet Window from expanding.
- The state message points users to Full App for complete reading.

Safety confirmation:

- Backend code was not changed.
- `/chat` schema remains `reply`, `mood`, `source`.
- No backend route or API was added.
- Pet renderer does not call Ollama directly.
- No direct Ollama `11434` reference was added.
- No IPC or preload API was added.
- No provider settings, Ollama routing, external API, file access, Email access, Calendar access, image, tray, packaging, autostart, screenshot, microphone, or screen monitoring behavior was added.

Validation:

- Pet renderer smoke now uses mocked fetch for success, empty input, mock source, local error source, network failure, long reply, mood expression mapping, and direct-Ollama safety.
- Pet window smoke now allows the intended local backend `/chat` client while still blocking direct Ollama access.

Next recommendation:

- TASK-135 - Pet Bubble Loading/Error UX.

## 14. TASK-135 Loading/Error UX Checkpoint

Status: DONE on 2026-05-24.

TASK-135 refined the Pet Bubble `/chat` loading, timeout, error, and retry behavior.

Completed:

- Added Pet Bubble fetch timeout helper.
- Timeout duration is `PET_CHAT_TIMEOUT_MS = 100000`.
- Timeout maps to `timeout` state.
- Timeout copy tells the user the local model may still be waking up and suggests opening Full App to check status.
- Pending state disables input and send.
- A pending guard prevents duplicate submit while a request is in flight.
- Request completion restores input and send.
- Empty input renders `empty_input` and does not fetch.
- Network fetch failure maps to `backend_offline`.
- `source=llm_local_error` maps to `llm_local_error`.
- Malformed response or missing `reply` maps to `llm_local_error` with safe generic copy.
- `source=mock` continues to map to `fallback_mock`.
- Offline, timeout, local-error, and malformed-response paths preserve the user's input for retry.
- Successful response clears the input.
- Existing Send button is the retry path; no Retry button was added.

Safety confirmation:

- Backend code was not changed.
- `/chat` schema remains `reply`, `mood`, `source`.
- No backend route or API was added.
- No direct Ollama access was added.
- No IPC or preload API was added.
- No raw stack trace or raw diagnostics are rendered in the Pet Bubble.
- No provider settings, Ollama routing, external API, file access, Email access, Calendar access, image, tray, packaging, autostart, screenshot, microphone, or screen monitoring behavior was added.

Validation:

- Pet renderer smoke covers pending disabled state, restored input/send after completion, empty input no-fetch, timeout state, timeout retry input preservation, backend offline, malformed response safe error, `llm_local_error`, `mock`, duplicate pending submit guard, and direct-Ollama safety.

Next recommendation:

- TASK-136 - Pet Bubble Mood/Expression Integration.

## 15. TASK-136 Mood/Expression Integration Checkpoint

Status: DONE on 2026-05-24.

TASK-136 unified Pet Bubble mood, source/local state, and Christina expression mapping.

Completed:

- Added explicit `PET_BUBBLE_STATE_EXPRESSIONS` mapping.
- Added `normalizePetMood(mood)`.
- Kept `setPetExpression(documentRef, mood)` as the single avatar update helper.
- Added `expressionForBubbleState(state, responseMood)`.
- Added `setPetExpressionForBubbleState(documentRef, state, options)`.
- Routed `setBubbleState(...)` through `setPetExpressionForBubbleState(...)`.
- Response `success` state uses backend response `mood`.
- Unknown response mood falls back to `neutral`.

Response mood mapping:

- `neutral` -> `christina_neutral.png`
- `focused` -> `christina_focused.png`
- `happy` -> `christina_happy.png`
- `proud` -> `christina_proud.png`
- `annoyed` -> `christina_annoyed.png`
- `worried` -> `christina_worried.png`
- `sleepy` -> `christina_sleepy.png`

Local state expression mapping:

- `collapsed` -> `neutral`
- `expanded` -> `neutral`
- `composing` -> `neutral`
- `empty_input` -> `annoyed`
- `pending` -> `focused`
- `success` -> backend response mood
- `backend_offline` -> `worried`
- `timeout` -> `sleepy`
- `llm_local_error` -> `worried`
- `fallback_mock` -> `proud`
- `long_reply` -> `focused`

Safety confirmation:

- No image asset was added.
- Backend code was not changed.
- `/chat` schema remains `reply`, `mood`, `source`.
- No backend route or API was added.
- No direct Ollama access was added.
- No IPC or preload API was added.
- No provider settings, external API, file access, Email access, Calendar access, tray, packaging, autostart, screenshot, microphone, or screen monitoring behavior was added.

Validation:

- Pet renderer smoke covers response mood `happy`, response mood `focused`, unknown mood fallback, pending expression, backend offline expression, timeout expression, local error expression, mock fallback expression, empty input expression, long reply expression, existing asset mapping, and direct-Ollama safety.

Next recommendation:

- TASK-137 - Pet Bubble Long Reply Handling.

## 16. TASK-137 Long Reply Handling Checkpoint

Status: DONE on 2026-05-24.

TASK-137 improved long reply detection and constrained reading behavior for Pet Bubble Chat.

Completed:

- Kept the long reply threshold explicit as `PET_REPLY_LONG_THRESHOLD = 160`.
- Added `isLongReply(reply)`.
- `stateForChatSource(...)` now routes long non-mock, non-error replies through `isLongReply(...)`.
- Added shared `PET_LONG_REPLY_HINT`.
- `long_reply` state message is `回覆較長，可開 Full App 查看完整內容。`
- Long reply content remains in `#pet-bubble-response`.
- No automatic Full App opening was added.
- No new window was added.

Layout behavior:

- Pet shell remains fixed to the `220 x 280` design target.
- Pet shell explicitly keeps `max-height: 280px` and `overflow: hidden`.
- Bubble response keeps `overflow-y: auto`.
- Long reply response area remains capped at `36px`.
- Response text uses `overflow-wrap: anywhere` and `white-space: pre-wrap`.
- Avatar remains visible in expanded mode.
- Input and Send remain available after long replies.
- Explicit drag handle and no-drag hooks remain intact.

Reading path:

- The existing Full App button/hook remains the path for longer reading.
- The bubble only displays a compact hint; it does not duplicate Full App.

Safety confirmation:

- Backend code was not changed.
- `/chat` schema remains `reply`, `mood`, `source`.
- No backend route or API was added.
- No IPC or preload API was added.
- No direct Ollama access was added.
- No external API, file access, Email access, Calendar access, image, provider settings, screenshot, microphone, or screen monitoring behavior was added.

Validation:

- Pet renderer smoke covers long reply state routing, threshold helper, long reply hint, internal scroll/max-height CSS, input/send restoration, Full App hook presence, drag handle presence, no-drag hooks, fixed Pet Window size assumptions, `/chat` schema field assumptions, and direct-Ollama safety.

Next recommendation:

- TASK-138 - Pet Bubble Chat Smoke Tests.

## 17. TASK-138 Smoke Checkpoint

Status: DONE on 2026-05-24.

TASK-138 strengthened Pet Bubble Chat smoke coverage before manual Windows validation.

Runtime scope:

- Runtime code was not changed.
- Smoke coverage was expanded in `apps/desktop/scripts/pet-renderer-smoke.js`.

Coverage:

- Non-empty input sends the existing backend `/chat` path.
- Request body remains `{ message, use_memory: false }`.
- Pending state appears before mocked response resolves.
- Pending disables input/send and maps expression to `focused`.
- Success renders `reply`, source status, and mood expression.
- Success clears input and restores Send.
- Empty input maps to `empty_input`, does not fetch, and maps expression to `annoyed`.
- `source=llm_local` maps to `success` / local status.
- `source=mock` maps to `fallback_mock` / `proud`.
- `source=llm_local_error` maps to `llm_local_error` / `worried`.
- Network failure maps to `backend_offline` / `worried`.
- Timeout maps to `timeout` / `sleepy`.
- Malformed response maps to safe `llm_local_error`.
- `mood=happy` maps to `christina_happy.png`.
- `mood=focused` maps to `christina_focused.png`.
- `mood=proud` maps to `christina_proud.png`.
- Unknown mood falls back to `neutral`.
- Long replies over `PET_REPLY_LONG_THRESHOLD = 160` map to `long_reply`.
- Long reply hint, response rendering, max-height, internal scroll, and `220 x 280` layout assumptions are covered.
- Full App hook, drag handle, and no-drag hooks remain present.
- Duplicate submit while pending does not create a second fetch.
- After pending completes, a next message can be sent.
- Pet renderer contains no direct Ollama `11434` access.

Safety confirmation:

- Backend code was not changed.
- `/chat` schema remains `reply`, `mood`, `source`.
- No backend route or API was added.
- No IPC or preload API was added.
- No direct Ollama access was added.
- No external API, file access, Email access, Calendar access, image, provider settings, screenshot, microphone, or screen monitoring behavior was added.

Validation:

- `node apps/desktop/scripts/pet-renderer-smoke.js` passes 29 checks.

Next recommendation:

- TASK-139 - Manual Windows Pet Bubble Chat Smoke.

## 18. TASK-140 Composer Visibility Fix Checkpoint

Status: DONE on 2026-05-24.

TASK-139 Windows manual smoke found a Pet Bubble input visibility regression during the wired bubble chat validation.

Manual finding:

- Full App chat worked.
- Pet Bubble expanded in the Pet Window.
- The bubble showed status/response text and the legacy TASK-133 placeholder body.
- The input and Send composer were not visible, so the user could not type in Pet Bubble.

Root cause:

- The form/input/send DOM remained present in `pet.html`.
- The bug was caused by layout clipping, not by missing DOM or `/chat` wiring.
- The expanded bubble had only a small visual budget inside the `220 x 280` Pet Window.
- Header, status, message, response, legacy placeholder body, and composer all participated in layout.
- Because `.pet-bubble` used `overflow: hidden`, the composer could be pushed below the visible area and clipped.

Fix:

- Pet Bubble now uses a fixed-height grid layout.
- The composer is pinned as the bottom grid row.
- The response area is the flexible scrollable row.
- The legacy `#pet-bubble-placeholder` body is hidden from layout.
- Message/status rows are compact so they cannot push the composer out.
- Long replies keep internal response scrolling and do not remove the composer.

Composer state rules:

- `expanded`, `composing`, `empty_input`, `success`, `backend_offline`, `timeout`, `llm_local_error`, `fallback_mock`, and `long_reply`: input and Send stay visible and enabled.
- `pending`: input and Send stay visible but disabled.
- `collapsed`: the whole bubble remains collapsed/hidden.

Safety confirmation:

- Backend code was not changed.
- `/chat` schema remains `reply`, `mood`, `source`.
- No backend route or API was added.
- No IPC or preload API was added.
- No direct Ollama access was added.
- No provider settings, external API, file access, Email access, Calendar access, image, tray, packaging, autostart, screenshot, microphone, or screen monitoring behavior was added.

Validation:

- Pet renderer smoke now covers composer visibility for expanded, composing, pending, success, backend_offline, timeout, llm_local_error, fallback_mock, and long_reply states.
- Pet renderer smoke also covers the Full App "Opening Full App..." status path without removing the composer.
- Pet renderer smoke passes 31 checks.
- Pet window smoke passes 10 checks.
- Existing desktop renderer smoke passes.
- Backend pytest passes with 586 tests.
- Direct Ollama `11434` safety scan passes.
- `git diff --check` passes.

Next recommendation:

- Re-run TASK-139 Manual Windows Pet Bubble Chat Smoke and verify the input and Send composer are visible and usable in the real Windows Pet Window.

## 19. TASK-141 Display-only Speech Bubble Redesign

Status: DONE on 2026-05-24.

TASK-141 changes the Pet Bubble product direction after Windows hands-on use.

Design shift:

- Previous direction: Pet Bubble behaved like a tiny chat panel with input and Send inside the `220 x 280` Pet Window.
- New direction: Pet Bubble is a display-only comic-style speech bubble for Christina's short replies and status.
- Full App is the main text input, troubleshooting, provider/settings, and long-reading surface.
- Future voice input or push-to-talk should be designed as a separate task.

UI behavior:

- Visible bubble uses `pet-speech-bubble`.
- Bubble has a light rounded panel and CSS tail pointing toward Christina.
- Visible content is compact: source/status badge, response text, and a short Full App hint.
- The bubble no longer presents input/send as primary UI.
- The hidden `pet-chat-form-hook`, `pet-chat-input-hook`, and `pet-chat-send-hook` remain as dev-only hooks for the existing client helper tests and possible future dispatch path.

State model:

- `collapsed`: bubble hidden.
- `expanded`: display-only prompt telling the user to type in Full App.
- `speaking`: shows a backend reply in the speech bubble.
- `thinking`: shows `吾正在想，別催。`.
- `backend_offline`: short Full App troubleshooting prompt.
- `timeout`: short local-model waking-up prompt.
- `llm_local_error`: short local model error prompt.
- `fallback_mock`: short mock fallback reply.
- `long_reply`: shows the Full App reading hint instead of trying to show the whole long reply in the small window.

Compatibility:

- The existing Pet `/chat` client function remains.
- Request body remains `{ message, use_memory: false }`.
- Response parsing still uses only `reply`, `mood`, and `source`.
- Normal successful replies now render through `speaking`.
- Legacy aliases such as `success` and `pending` remain for compatibility, but visible product language is `speaking` / `thinking`.

Safety confirmation:

- Backend code was not changed.
- `/chat` schema remains `reply`, `mood`, `source`.
- No backend route or API was added.
- No IPC or preload API was added.
- No direct Ollama access was added.
- No speech-to-text, voice input, provider settings change, external API, file access, Email access, Calendar access, image, tray, packaging, autostart, screenshot, microphone, or screen monitoring behavior was added.

Validation:

- Pet renderer smoke covers speech bubble DOM, CSS tail, hidden dev-only composer, speaking/thinking states, long-reply Full App hint, Full App hook, drag handle, Menu toggle, `/chat` schema assumptions, and direct-Ollama safety.
- Pet renderer smoke passes 31 checks.
- Pet window smoke passes 10 checks.
- Existing desktop renderer smoke passes.
- Backend pytest passes with 586 tests.
- Direct Ollama `11434` safety scan passes.
- `git diff --check` passes.

Next recommendation:

- Manual Windows visual smoke for the display-only speech bubble.
- Follow-up design task: Pet input source design for Full App dispatch, voice, or push-to-talk.

## 20. TASK-143 Full App Reply Mirror Bridge

Status: DONE on 2026-05-24.

TASK-143 connects the display-only Pet speech bubble to the Full App chat flow.

Behavior:

- Full App remains the primary text input interface.
- After Full App receives a successful `/chat` response, it mirrors only `reply`, `mood`, and `source` to Pet Mode.
- Pet Window does not provide visible text input.
- Pet speech bubble displays the latest AI reply and source/status.
- Pet expression updates from the mirrored `mood`.
- Long replies use the existing compact Full App reading hint.

IPC bridge:

- Full App renderer calls `window.dragonPet.updatePetSpeech({ reply, mood, source })`.
- Full App preload exposes fixed method `updatePetSpeech(payload)`.
- Fixed IPC channel from Full App to main: `pet:speech-update`.
- Main process sanitizes/truncates payload and forwards only `{ reply, mood, source }`.
- Fixed IPC channel from main to Pet Window: `pet:speech-received`.
- Pet preload exposes fixed listener `onSpeechUpdate(callback)`.
- Pet preload returns an unsubscribe function for only the fixed speech listener.

Hidden Pet Window behavior:

- If Pet Window does not exist or is hidden, main process returns a safe status and does not crash.
- Hidden Pet Window is not automatically shown, so a user-initiated Hide Pet Window remains respected.
- Full App `Show Pet` remains the explicit way to bring Pet Window back.

Safety confirmation:

- Backend code was not changed.
- `/chat` schema remains `reply`, `mood`, `source`.
- No backend route or API was added.
- No arbitrary IPC was exposed.
- Preloads do not expose arbitrary `ipcRenderer`, fs, shell, process, or arbitrary channel send.
- Pet renderer does not call backend `/chat` for mirrored speech updates.
- No direct Ollama access was added.
- No external API, file access, Email access, Calendar access, image, voice, speech-to-text, tray, packaging, autostart, screenshot, microphone, or screen monitoring behavior was added.

Validation:

- Full App renderer smoke verifies successful `/chat` response mirrors only `reply`, `mood`, and `source`.
- Full App renderer smoke verifies missing `updatePetSpeech` API does not crash.
- Pet renderer smoke verifies speech updates display bubble text, source, mood expression, and long-reply hint.
- Pet window smoke verifies fixed channels `pet:speech-update` and `pet:speech-received`, narrow preload APIs, and hidden-window safe status logic.
- Desktop renderer smoke passes.
- Backend pytest passes with 586 tests.
- Direct Ollama `11434` safety scan passes.
- `git diff --check` passes.

Next recommendation:

- Manual Windows smoke for Full App reply mirroring into Pet speech bubble.
