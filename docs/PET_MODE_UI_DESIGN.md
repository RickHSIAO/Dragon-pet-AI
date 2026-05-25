# Pet Mode UI Design

> Task: TASK-114 - Pet Mode UI Design
> Status: DESIGN ONLY
> Date: 2026-05-24
> Scope: Product and technical design for a future desktop pet mode. No runtime code is changed by this document.

---

## 1. Pet Mode Goals

Pet Mode moves Dragon Pet AI from a full management window toward a small desktop companion experience:

- Christina appears as a small floating desktop pet.
- The window can be transparent or semi-transparent.
- The window is borderless, compact, and optionally always-on-top.
- The pet can be dragged around the desktop.
- A click, double-click, menu action, or future shortcut can open a compact chat surface.
- The user can return to the full management interface when they need settings, memory, audit logs, provider controls, or debugging.

Pet Mode is not a replacement for the current app. It is a daily-use surface for fast interaction. Full App Mode remains the safe control center.

### Relationship to Full App / Dev UI

Full App Mode should keep the existing responsibilities:

- Full chat history and larger conversation view.
- Memory management and context preview.
- Audit log inspection.
- Provider Settings and key management.
- Usage summary and runtime status.
- Developer smoke/debug visibility.

Pet Mode should keep only the narrow companion surface:

- Christina visual expression.
- Short status hint.
- Compact bubble chat entry point.
- Mode switch back to Full App Mode.
- Minimal local backend chat calls through the same `/chat` contract.

### Daily User Flow

1. User starts Dragon Pet AI.
2. Full App Mode may open first during early MVP, or Pet Mode may open first after a later preference is added.
3. User switches to Pet Mode.
4. Christina floats on the desktop in a small always-on-top window.
5. Startup greeting appears as a short hint or bubble.
6. User drags Christina to a comfortable corner.
7. User clicks Christina to open a small bubble chat.
8. User sends a short message.
9. Christina replies in the bubble and updates expression using the existing mood/expression system.
10. User collapses the bubble and continues working.
11. User uses right-click menu or a mode button to reopen Full App Mode for settings or memory work.

### Why Pet Mode Is Needed

The current UI is useful for development and management, but it is too large for passive daily companionship. Pet Mode gives the project its core identity:

- It makes Christina visible without occupying the whole screen.
- It lowers friction for quick chats.
- It lets idle, startup, and return-from-away behaviors feel like a desktop companion instead of a dashboard notification.
- It separates daily interaction from advanced configuration.

---

## 2. UI Mode Split

### Full App Mode

Full App Mode is the current full Electron window.

Recommended responsibilities:

- Full chat and scrollable conversation history.
- Sticky chat composer.
- Memory CRUD.
- Memory context preview.
- Audit logs.
- Provider Settings.
- Usage summary.
- Runtime status and troubleshooting.
- Developer smoke-test target.

Window characteristics:

- Normal framed Electron window.
- Resizable.
- Not always-on-top by default.
- Uses current `index.html`, `renderer.js`, and `styles.css`.

### Pet Mode

Pet Mode is the small desktop pet window.

Recommended responsibilities:

- Show Christina expression asset.
- Show optional short hint text.
- Support drag movement.
- Support click/double-click/right-click interactions.
- Open Bubble Chat Mode.
- Offer a path back to Full App Mode.

Window characteristics:

- Transparent or semi-transparent.
- Frameless.
- Compact.
- Always-on-top by default, with an option to disable later.
- No memory/settings/audit UI.
- No direct Ollama calls.

### Bubble Chat Mode

Bubble Chat Mode is a compact chat surface opened from Pet Mode.

Recommended responsibilities:

- Show recent short exchange only.
- Provide input when expanded.
- Send user message through local backend `/chat`.
- Display reply and mood/source state in a compact way.
- Collapse without destroying Pet Mode.

Bubble Chat Mode can be implemented either inside the same Pet Window or as a second lightweight window. For MVP, same-window expansion is simpler and safer because it avoids cross-window focus, positioning, and IPC complexity.

---

## 3. Pet Mode Window Specification Draft

### Default Size

Recommended MVP default:

- `300 x 400` px after TASK-146 readability UX fix.

Rationale:

- Large enough for the existing Christina expression assets to remain readable.
- Small enough to sit near a screen edge as a desktop pet.
- Gives room for a short hint below the pet.
- Gives the current clean reply bubble, larger Christina image, and bottom controls enough space without becoming a mini chat app.

Alternative compact size:

- `180 x 240` px

Use this only if the expression assets are normalized for small display and text is mostly hidden.

### Electron Window Flags

Recommended MVP flags for the future Pet Window:

- `frame: false`
- `transparent: true`
- `alwaysOnTop: true`
- `resizable: false` for MVP
- `skipTaskbar: false` initially, then evaluate `true` only if tray support exists
- `hasShadow: false` or platform-tested shadow behavior

### Resizable

MVP recommendation: not resizable.

Reason:

- Drag and transparent hit areas are easier to test.
- Asset scaling and bubble positioning are more predictable.
- Small fixed sizes reduce layout drift.

Future option:

- Add `200-320 px` width presets instead of free resizing.

### Draggable

Required for MVP.

Recommended approach:

- Use CSS `-webkit-app-region: drag` only on a small explicit drag handle.
- Use `-webkit-app-region: no-drag` on avatar, pet body, buttons, inputs, right-click targets, bubble controls, and menus.
- Avoid large-area CSS drag regions on Windows because they can behave like native title bars and trigger the OS system menu on right-click.
- Use a future custom drag implementation if whole-character drag is required.

### Click-through

MVP recommendation: do not enable click-through globally.

Reason:

- The pet must receive click, double-click, context menu, and drag interactions.
- Global click-through would make chat opening and right-click menu fragile.

Possible future design:

- Add a "click-through idle mode" preference.
- Use `setIgnoreMouseEvents(true, { forward: true })` only when the bubble is closed and the user explicitly enables pass-through.
- Temporarily disable click-through when the pointer enters a visible control area.

### Right-click Menu

Recommended for MVP.

Menu items:

- Open Chat
- Hide Chat
- Open Full App
- Always on Top: On/Off
- Reset Position
- Quit

The right-click menu should be owned by the main process or exposed through a narrow preload API. Renderer should not gain broad Electron or Node access.

### Tray Icon

Recommended after the first Pet Window prototype, not in the first skeleton.

Tray responsibilities:

- Restore Pet Mode if hidden.
- Open Full App Mode.
- Toggle always-on-top.
- Quit.

Do not rely on tray as the only way to restore the app until tray behavior is tested on Windows.

### Remember Last Position

Recommended after drag behavior works.

Rules:

- Persist only window bounds and mode preference.
- Store locally.
- Clamp restored position to the current display work area.
- If the saved position is off-screen, reset to bottom-right.

---

## 4. Interaction Design

### Single Click on Christina

Recommended behavior:

- If Bubble Chat is closed, open it in compact mode.
- If Bubble Chat is open, focus the input field.
- If a startup/idle hint is visible, keep it unless chat opens.

### Double Click on Christina

Recommended behavior:

- Toggle Bubble Chat expanded/collapsed.

Alternative:

- Open Full App Mode. This is less discoverable for chat-first use, so reserve Full App for menu or a visible small action.

### Right-click Menu

Recommended behavior:

- Show context menu with mode and window controls.
- Right-click must not send chat messages.
- Right-click must not trigger file, email, calendar, screenshot, microphone, or external API behavior.

### Drag Movement

Recommended behavior:

- User can drag Christina from the pet body area.
- Dragging closes hover affordances but does not clear chat content.
- On drag end, future implementation saves position.

### Open / Close Chat

Recommended behavior:

- Single click opens Bubble Chat.
- Escape collapses Bubble Chat if focused.
- Close button collapses Bubble Chat.
- Sending a message keeps the bubble open until reply is shown.

### Switch Back to Full App Mode

Recommended behavior:

- Right-click menu item: Open Full App.
- Optional tiny icon button in expanded bubble: Open Full App.
- Full App should restore or create the existing full window.
- Pet Mode can either remain visible or hide based on a future user preference.

MVP recommendation:

- Open Full App and keep Pet Mode visible.
- This avoids a confusing state where the pet disappears after opening settings.

### Idle / Startup / Return-from-Away in Pet Mode

Pet Mode should reuse the existing companion behavior rules conceptually:

- Startup greeting: short hint bubble near Christina; no `/chat` call.
- Idle short threshold: neutral expression and small hint.
- Idle long threshold: sleepy expression and smaller/non-intrusive hint.
- Return-from-away: annoyed or worried short greeting; no `/chat` call.
- Chat response mood overrides idle expression after the backend reply.

Pet Mode-specific rules:

- Idle hints should be shorter than Full App hints.
- Hints should auto-hide faster when they cover desktop content.
- No proactive LLM call should happen just because the user is idle or returned.

---

## 5. Bubble Chat Design

### Position

Recommended MVP:

- Bubble appears attached to the right side of the pet when there is space.
- If near the right screen edge, bubble appears on the left.
- If near the bottom edge, bubble grows upward.

For same-window MVP, this can be approximated by expanding the Pet Window width while keeping Christina anchored on one side.

### Input Box

Recommended behavior:

- Input is not always visible in collapsed Pet Mode.
- Input appears only when Bubble Chat is expanded.
- Single-line default, with Shift+Enter for newline if textarea is used.

Reason:

- Always-visible input makes the desktop pet feel like a small app window instead of a companion.
- Hidden input reduces accidental typing and desktop obstruction.

### Collapse / Expand

Recommended states:

- Collapsed: pet only, optional short hint.
- Compact bubble: last message or greeting, no full history.
- Expanded bubble: last few messages plus input.

Transitions:

- Click pet: collapsed -> compact or expanded bubble.
- Double-click pet: compact <-> expanded.
- Escape/close button: bubble -> collapsed.

### Auto-collapse After AI Reply

MVP recommendation: do not auto-collapse immediately.

Reason:

- User needs time to read the reply.
- Auto-collapse can feel like the app ignored a long response.

Future preference:

- Auto-collapse after 15-30 seconds only for short replies and only if input is not focused.

### Long Messages

Rules:

- Clamp bubble height.
- Use internal scrolling for long replies.
- Preserve line breaks.
- Do not resize the pet image or move the window unexpectedly during a long reply.
- Offer "Open Full App" for long conversation review.

Recommended limits:

- Bubble max width: `360 px`
- Bubble max height: `420 px`
- Visible message history: last 3-5 turns

### Avoiding Desktop Obstruction

Rules:

- Prefer screen-edge aware positioning.
- Keep collapsed state small.
- Auto-hide transient hints.
- Allow drag repositioning.
- Provide a quick hide/collapse action.
- Do not open Full App automatically from a chat reply.

---

## 6. Technical Design

### Electron BrowserWindow

Future Pet Window likely needs a second `BrowserWindow`.

Draft options:

```js
new BrowserWindow({
  width: 220,
  height: 280,
  frame: false,
  transparent: true,
  alwaysOnTop: true,
  resizable: false,
  webPreferences: {
    nodeIntegration: false,
    contextIsolation: true,
    preload: path.join(__dirname, "pet-preload.js"),
  },
});
```

Design note:

- The current main window uses `nodeIntegration: false` and `contextIsolation: true`.
- Pet Mode should keep those security defaults.
- If IPC is needed, expose only narrow mode/window commands through preload.

### `transparent`

Use `transparent: true` for Pet Mode only after prototype testing.

Risks:

- Platform-specific rendering differences.
- Hit testing may be surprising with transparent regions.
- Shadows and rounded shapes may behave differently.

Mitigation:

- Prototype with a simple visible debug background toggle.
- Keep smoke tests for nonblank pet rendering.

### `alwaysOnTop`

Use `alwaysOnTop: true` by default for Pet Mode.

Add later preference:

- Always on top: enabled/disabled.

Do not apply always-on-top to Full App Mode by default.

### `setIgnoreMouseEvents`

MVP recommendation: not required.

Use only for an explicit future click-through option.

If implemented later:

- Main process controls it.
- Renderer requests pass-through through a narrow IPC command.
- Disable pass-through when bubble is open or input is focused.

### Preload / IPC

A preload file is recommended once Pet Mode needs Electron window actions.

Allowed narrow API examples:

- `openFullApp()`
- `togglePetChat()`
- `setAlwaysOnTop(enabled)`
- `resetPetPosition()`
- `closePetBubble()`
- `showPetContextMenu()`

Disallowed renderer capabilities:

- No unrestricted Node access.
- No shell execution.
- No filesystem reads.
- No direct Ollama calls.
- No arbitrary IPC channel access.

### Main Process Window Management

The main process should eventually own:

- `fullAppWindow`
- `petWindow`
- optional `tray`
- mode switch commands
- window bounds persistence
- always-on-top state
- context menu

Recommended behavior:

- Full App Mode and Pet Mode can coexist.
- Closing Full App should not necessarily quit if Pet Mode is active.
- Quitting from tray/menu should close both windows.
- Opening Full App from Pet Mode should focus existing Full App if present.

### Renderer Strategy

Recommended MVP: create a new renderer for Pet Mode.

Potential files in a future implementation:

- `apps/desktop/src/renderer/pet.html`
- `apps/desktop/src/renderer/pet-renderer.js`
- `apps/desktop/src/renderer/pet.css`
- optional `apps/desktop/src/pet-preload.js`

Reason:

- Full App Mode has memory, audit, provider settings, and large chat layout.
- Pet Mode needs a small fixed surface with very different layout constraints.
- Separate renderer keeps Pet Mode tests focused and avoids making current `renderer.js` more complex.

What should be shared:

- Christina expression assets.
- Mood-to-expression mapping rules, if extracted later.
- Backend `/chat` client shape.
- Safety constants and backend URL handling pattern.

What should not be shared by direct copy-paste long term:

- Full App settings DOM logic.
- Memory management DOM logic.
- Audit log DOM logic.
- Provider key UI logic.

### Shared Expression Assets

Pet Mode should reuse:

- `apps/desktop/src/renderer/assets/pet/christina/expressions/*.png`
- existing expression names such as `neutral`, `happy`, `proud`, `annoyed`, `focused`, `worried`, `sleepy`

Pet Mode should not add new images in TASK-114. Future visual work can evaluate whether the 512x512 normalized candidates should become the Pet Mode default.

### Backend Contract

Pet Mode should call only the local backend:

- `POST /chat`
- Existing response schema: `reply`, `mood`, `source`

Do not change `/chat` schema for Pet Mode. If Pet Mode needs UI-only metadata, keep it renderer-local or add a separate future endpoint after design review.

---

## 7. Safety Boundaries

Pet Mode must preserve the current local-first safety posture.

Hard boundaries:

- Pet Mode does not automatically read files.
- Pet Mode does not automatically read Email.
- Pet Mode does not automatically read Calendar.
- Pet Mode does not automatically execute commands.
- Pet Mode does not automatically call external APIs.
- Pet Mode does not secretly record audio.
- Pet Mode does not secretly take screenshots.
- Pet Mode does not monitor the screen.
- Pet Mode does not send messages before the user confirms or submits input.
- Pet Mode does not change the `/chat` schema.
- Pet Mode does not let renderer directly call Ollama.
- Pet Mode calls only the local backend.
- Pet Mode does not expose API keys to renderer code.
- Pet Mode does not add autonomous tool use.
- Pet Mode does not make idle/startup/return-from-away behavior call an LLM automatically.

Renderer safety requirements:

- `nodeIntegration: false`
- `contextIsolation: true`
- CSP should allow only local assets and the local backend.
- No external CDN, fonts, analytics, or tracking.
- IPC must be explicit and narrow if added.

---

## 8. MVP Task Split

### TASK-115 - Create Pet Window Design Skeleton

Status: DONE on 2026-05-24.

Goal:

- Add static design skeleton files for Pet Mode without changing Electron window behavior.

Scope:

- Draft `pet.html`, `pet.css`, and `pet-renderer.js` structure.
- Reuse Christina expression assets.
- No new BrowserWindow.
- No backend changes.

Acceptance:

- Static files exist.
- No app runtime path uses them yet.
- Existing Full App remains unchanged.

Completion notes:

- Added `apps/desktop/src/pet/pet.html`.
- Added `apps/desktop/src/pet/pet.css`.
- Added `apps/desktop/src/pet/pet-renderer.js`.
- Added `apps/desktop/scripts/pet-renderer-smoke.js`.
- The skeleton includes avatar, hint, bubble placeholder, right-click/menu hook, and Full App mode-switch hook.
- It is not connected to Electron `main.js`, backend, `/chat`, or Ollama.

### TASK-116 - Pet Mode BrowserWindow Prototype

Status: DONE on 2026-05-24.

Goal:

- Add an Electron Pet Window prototype behind a safe dev-only or explicit mode switch.

Scope:

- Add `createPetWindow()` in main process.
- Use frameless, transparent, always-on-top draft flags.
- Load Pet renderer.
- Keep Full App unchanged.

Acceptance:

- Pet Window opens only through explicit dev command or menu.
- Full App still works.
- `nodeIntegration: false`, `contextIsolation: true`.

Completion notes:

- Added `createPetWindow()` and `petWindow` in `apps/desktop/src/main.js`.
- Pet Window is gated by `PET_MODE_ENABLED=true`; default startup remains Full App only.
- Pet Window loads `apps/desktop/src/pet/pet.html`.
- Pet Window originally used `220 x 280`; TASK-146 updates the current default to `300 x 400` after `260 x 340` remained too cramped in Windows visual testing. It remains `frame: false`, `transparent: true`, `alwaysOnTop: true`, `resizable: false`, `show: false`, and `ready-to-show` display.
- Pet Window uses `nodeIntegration: false`, `contextIsolation: true`, and `sandbox: true`.
- No preload API, backend call, `/chat` call, drag behavior, context menu behavior, bubble chat behavior, or mode switch behavior was added.

### TASK-117 - Pet Mode Drag Behavior

Status: DONE on 2026-05-24.

Goal:

- Make the Pet Window draggable and position-stable.

Scope:

- Add CSS drag region.
- Mark buttons/inputs as no-drag.
- Evaluate window bounds persistence design.

Acceptance:

- User can drag the pet.
- Chat controls remain clickable.
- No click-through yet.

Completion notes:

- `#pet-drag-region` now has `.pet-drag-region` and uses CSS `-webkit-app-region: drag`.
- Bubble, chat form, input, buttons, context-menu hook, and Full App hook now have `.pet-no-drag`.
- CSS applies `-webkit-app-region: no-drag` to `.pet-no-drag`, bubble, form, action area, buttons, inputs, and textareas.
- No IPC, preload API, mousemove drag implementation, click-through behavior, backend call, or `/chat` call was added.

TASK-127 supersedes the large drag-region approach:

- `#pet-drag-region` is now a no-drag interaction region.
- `#pet-drag-handle` is the only CSS-native drag region.
- Avatar, bubble, menu, and controls are no-drag.

### TASK-118 - Pet Bubble Chat Design

Status: DONE on 2026-05-24 for local UI state only. Backend `/chat` wiring remains deferred.

Goal:

- Add compact Bubble Chat Mode inside Pet Window.

Scope:

- Collapsed, compact, and expanded states.
- Single local backend `/chat` path.
- Long-message scroll behavior.
- Source/mood display in compact form.

Acceptance:

- User can open bubble, send message, see reply.
- Reply mood updates expression.
- `/chat` schema remains unchanged.

Completion notes:

- Added collapsed and expanded bubble UI states.
- Added bubble message area, placeholder input, send button, Chat open hook, and close/collapse control.
- Clicking the pet drag region or Chat hook expands the bubble.
- Clicking the close control collapses the bubble.
- Placeholder submit prevents default behavior and updates only local UI text.
- Bubble, input, form, and buttons remain no-drag regions.
- No backend call, `/chat` call, IPC, preload API, main-process change, or schema change was added.

### TASK-119 - Mode Switch Full App <-> Pet Mode

Status: DONE on 2026-05-24 for Pet-to-Full switch. Full-to-Pet controls remain deferred.

Goal:

- Add explicit switching between Full App Mode and Pet Mode.

Scope:

- Main process manages both windows.
- Pet menu can open/focus Full App.
- Full App can open/show Pet Mode.
- Decide whether both windows coexist or one hides.

Acceptance:

- Switching does not lose chat input unexpectedly.
- Full App remains the settings/memory/audit surface.
- Pet Mode remains compact.

Completion notes:

- Added `apps/desktop/src/pet/pet-preload.js`.
- Exposed only `window.dragonPet.openFullApp()`.
- Added fixed IPC channel `pet:open-full-app`.
- Main process handler only creates/shows/restores/focuses the Full App window.
- Pet renderer calls the narrow API from `#pet-open-full-app-hook`.
- If the API is unavailable, Pet Mode shows a local fallback message instead of throwing.
- No arbitrary IPC, shell, fs, process, openExternal, backend call, `/chat` call, or schema change was added.

### TASK-120 - Pet Mode Smoke Tests

Status: DONE on 2026-05-24. Pet Mode MVP checkpoint passed.

Goal:

- Add smoke coverage for Pet Mode rendering and safety invariants.

Scope:

- Renderer smoke for bubble state.
- Main process static checks where practical.
- Safety scan: no direct Ollama URL, no Node access, no external API.
- Optional Playwright or Electron visual smoke later.

Acceptance:

- Existing renderer smoke tests still pass.
- Pet Mode tests pass.
- Safety boundaries are validated.

Completion notes:

- `pet-renderer-smoke.js` validates Pet DOM/CSS hooks, local bubble state, no backend calls, no `/chat`, no direct Ollama, no external image URL, Full App hook narrow API usage, and fallback behavior.
- `pet-window-smoke.js` validates main-process Pet Window options, Full App preservation, `PET_MODE_ENABLED=true` gating, fixed IPC channel `pet:open-full-app`, narrow preload API, and no direct Ollama access from renderer/preload surfaces.
- Existing Full App renderer smoke still passes.
- Backend pytest still passes with 586 tests.
- `/chat` schema remains unchanged.
- No runtime feature was added in TASK-120.

### TASK-121 - Manual Windows Pet Mode Visual Smoke

Status: DONE - PASS WITH NOTE on 2026-05-24.

Manual smoke summary:

- Pet small window can be dragged: PASS.
- Chat can expand/collapse the bubble: PASS.
- Full App hook can bring the main window back to foreground: PASS.
- Menu hook cannot be clicked / used yet: NOTE. This remains an expected placeholder; menu behavior is not implemented.
- After backend startup, Full App provider/backend status is normal: PASS.
- Pet small window stays always-on-top: PASS.

Checkpoint note:

- No code was changed for TASK-121.
- No backend call, `/chat` wiring, `/chat` schema change, external API, image, file access, Email access, Calendar access, screenshot, microphone, or screen-monitoring behavior was added.

### TASK-122 - Pet Window Position Persistence

Status: DONE on 2026-05-24.

Implementation summary:

- Pet Window position is saved by Electron main process only.
- State path is Electron `app.getPath("userData")` plus `pet-window-state.json`.
- Stored values are `x`, `y`, `width`, and `height`; Pet Window size now follows the fixed current default `300 x 400`.
- Position saves after Pet Window `move` with a small debounce and again on `close`.
- Pet Window loads saved `x/y` when `PET_MODE_ENABLED=true` creates the Pet Window.

Off-screen behavior:

- Saved position is accepted only if the Pet Window center point is inside a current display work area from `screen.getAllDisplays()`.
- Missing, invalid, or off-screen saved state falls back to a bottom-right default on the primary display work area.

Safety note:

- Full App Window position is not affected.
- No backend call, `/chat` call, `/chat` schema change, provider settings change, Ollama routing change, external API, image, menu implementation, or bubble backend wiring was added.
- The only file read/write is the local app-owned Pet Window state JSON under Electron `userData`.

### TASK-123 - Pet Mode Menu / Right-click Menu

Status: DONE on 2026-05-24.

Implementation summary:

- Pet Mode now has a local DOM popup menu.
- The visible Menu hook opens the menu.
- Right-click on the Pet root opens the menu.
- Close Menu collapses the popup.
- Open Full App uses the existing `window.dragonPet.openFullApp()`.
- Reset Pet Position uses `window.dragonPet.resetPetPosition()` over fixed IPC channel `pet:reset-position`.
- Hide Pet Window uses `window.dragonPet.hidePetWindow()` over fixed IPC channel `pet:hide-window`.

Menu items:

- Open Full App.
- Reset Pet Position.
- Hide Pet Window.
- Close Menu.

Safety note:

- The menu uses fixed narrow preload APIs only.
- Renderer cannot send arbitrary IPC channels or arbitrary x/y coordinates.
- No fs, shell, process, openExternal, backend call, `/chat` call, `/chat` schema change, provider settings change, Ollama routing change, external API, image, or bubble backend wiring was added.

### TASK-124 - Manual Windows Pet Menu Smoke

Status: DONE - PASS WITH NOTE on 2026-05-24.

Manual smoke summary:

| Check | Result | Notes |
|---|---|---|
| Click Menu hook | PASS | Menu opens. |
| Right-click Pet Window | PASS WITH NOTE | Lower / non-drag area opens menu; top avatar/image drag region does not respond to right-click. |
| Close Menu | PASS | Menu collapses. |
| Open Full App | PASS | Full App is brought back to foreground. |
| Reset Pet Position | PASS | Pet Window returns to safe default position. |
| Hide Pet Window | PASS | Pet Window hides; Full App remains open. |
| Relaunch with `PET_MODE_ENABLED=true` | PASS | Saved position is restored. |
| Bubble Chat | PASS | Still local placeholder; not wired to `/chat`. |

Right-click note:

- Right-click menu currently works only on non-drag / lower area.
- Top avatar/image drag region does not receive right-click.
- Likely cause: `-webkit-app-region: drag` consumes renderer `contextmenu` events in the upper drag region.
- Follow-up recommended: TASK-125 - Fix Pet right-click menu hit area.

Safety note:

- No code was changed for TASK-124.
- No backend call, `/chat` wiring, `/chat` schema change, external API, image, file access, Email access, Calendar access, screenshot, microphone, or screen-monitoring behavior was added.

### TASK-125 - Fix Pet Right-click Menu Hit Area

Status: DONE on 2026-05-24.

Root cause:

- The upper avatar/image area is intentionally part of the Electron CSS drag region.
- Electron `-webkit-app-region: drag` can prevent renderer `contextmenu` events from reaching the Pet renderer.
- Full-window right-click and full-window drag are not both reliable on the same pixels.

Implementation summary:

- Added an explicit upper-right `#pet-menu-hotspot` inside the Pet stage.
- The hotspot is `pet-no-drag`, so it can receive click and right-click events.
- Hotspot click and hotspot right-click open the existing local DOM menu.
- The main avatar stage remains draggable.
- The existing lower Menu hook and non-drag lower/root context menu behavior remain available.

Resulting hit areas:

- Dragging: main Pet drag stage and avatar surrounding area.
- Right-click/menu: explicit upper-right menu hotspot, lower non-drag area, and existing Menu hook.
- Known limitation: pixels assigned to `-webkit-app-region: drag` may still not deliver renderer right-click events; the UI now provides a clear visible no-drag target instead of relying on those pixels.

Safety note:

- No IPC, preload API, backend call, `/chat` call, `/chat` schema change, provider settings change, Ollama routing change, external API, image, file access, Email access, Calendar access, screenshot, microphone, screen-monitoring behavior, or bubble backend wiring was added.

### TASK-126 - Fix Pet Menu UX Regression

Status: DONE on 2026-05-24.

Root cause:

- The visible upper-right `#pet-menu-hotspot` added in TASK-125 created a duplicated Menu affordance.
- On Windows, right-clicking a `-webkit-app-region: drag` area can behave like right-clicking a native title bar and may show the OS system menu.
- Renderer `contextmenu` cannot be relied on for pixels assigned to the native drag region.

Implementation summary:

- Removed the visible upper-right menu hotspot.
- Kept the bottom `Chat / Full App / Menu` action row as the Pet menu entry point.
- Changed the bottom `Menu` button to toggle the DOM menu open and closed.
- Kept `Close Menu` and added Escape-to-close for the local DOM menu.
- Kept no-drag-area right-click as a local toggle where renderer events are delivered.

Current UX rule:

- The drag region is primarily for moving the Pet Window.
- The bottom `Menu` button is the primary custom menu entry.
- Right-click in the native drag region may show the Windows system menu; this is accepted for the CSS-native drag MVP.
- Full-window custom right-click is deferred unless a future task replaces CSS native drag with a custom drag implementation.

Safety note:

- No IPC, preload API, `main.js` change, backend call, `/chat` call, `/chat` schema change, provider settings change, Ollama routing change, external API, image, file access, Email access, Calendar access, screenshot, microphone, screen-monitoring behavior, or bubble backend wiring was added.

### TASK-127 - Replace Large Pet Drag Region with Explicit Drag Handle

Status: DONE on 2026-05-24.

Root cause:

- On Windows, `-webkit-app-region: drag` behaves like a native title bar region.
- Right-clicking a native drag region may show the Windows system menu instead of the Pet DOM menu.
- A large avatar/stage drag region creates too much overlap between Pet interactions and OS window behavior.

Implementation summary:

- Added a small top `#pet-drag-handle` grip as the only CSS-native drag region.
- Removed CSS-native drag behavior from the large avatar/stage region.
- Avatar container, avatar image, hint, bubble, menu, action hooks, buttons, inputs, and textareas are no-drag interaction areas.
- The bottom `Menu` button continues to toggle the Pet DOM menu.
- `Close Menu` and Escape-to-close remain available.
- Right-click in no-drag interaction areas can still toggle the Pet DOM menu when renderer events are delivered.

Current UX rule:

- Dragging uses the explicit top handle.
- Avatar / bubble / controls are interaction-first no-drag areas.
- Right-clicking the drag handle may still show the Windows OS system menu; this is accepted because the handle is small and clearly for moving the window.
- Restoring whole-character drag without OS menu interference should be handled by a future custom drag implementation, not by large-area CSS `app-region: drag`.

Safety note:

- No IPC, preload API, `main.js` change, backend call, `/chat` call, `/chat` schema change, provider settings change, Ollama routing change, external API, image, file access, Email access, Calendar access, screenshot, microphone, screen-monitoring behavior, or bubble backend wiring was added.

### TASK-128 - Full App -> Show Pet Window Bridge

Status: DONE on 2026-05-24.

Goal:

- Let the Full App show/focus Pet Window after the Pet menu `Hide Pet Window` action hides it.

Implementation summary:

- Added a `Show Pet` button in the Full App header.
- Added Full App preload `apps/desktop/src/renderer/preload.js`.
- Full App preload exposes only `window.dragonPet.showPetWindow()`.
- Main process uses fixed IPC channel `pet:show-window`.
- If Pet Window already exists, main shows/restores/focuses it.
- If Pet Window does not exist and `PET_MODE_ENABLED=true`, main creates it and shows/focuses it.
- If `PET_MODE_ENABLED` is not enabled, main returns a safe disabled status and the Full App shows a local message.

Safety note:

- This is a narrow Full App -> Pet Window bridge only.
- No arbitrary IPC, fs, shell, process, backend route, backend call, `/chat` call, `/chat` schema change, Ollama call, external API, image, Email access, Calendar access, screenshot, microphone, screen-monitoring behavior, or bubble backend wiring was added.
- Bubble Chat remains local placeholder UI only.

### TASK-129 - Fix Pet Window Drag Regression

Status: DONE on 2026-05-24.

Root cause:

- TASK-127 correctly removed the large avatar/stage drag region.
- The replacement explicit drag handle existed, was not no-drag, and used `-webkit-app-region: drag`.
- The handle was only `58 x 10 px`, which was too small and too subtle for reliable Windows manual dragging.

Implementation summary:

- Kept the explicit handle strategy and did not restore large-area avatar/body drag.
- Enlarged `#pet-drag-handle` to a `156 x 24 px` top bar.
- Added a subtle CSS grip line, higher `z-index`, `pointer-events: auto`, and `user-select: none`.
- Avatar, bubble, menu, controls, buttons, inputs, and textareas remain no-drag interaction areas.

Current UX rule:

- Dragging uses only the top explicit handle.
- Right-click on the handle may still show the Windows OS system menu because it is a native drag region.
- The rest of the Pet Window remains interaction-first and no-drag.
- Whole-character drag remains deferred to a future custom drag implementation.

Safety note:

- No IPC, preload API, `main.js` change, backend call, `/chat` call, `/chat` schema change, provider settings change, Ollama routing change, external API, image, file access, Email access, Calendar access, screenshot, microphone, screen-monitoring behavior, or bubble backend wiring was added.

### TASK-130 - Manual Windows Pet Drag/Menu Smoke

Status: DONE - PASS on 2026-05-24.

Manual smoke summary:

| Check | Result | Notes |
|---|---|---|
| Top drag handle drags Pet Window | PASS | Enlarged `156 x 24 px` handle is usable. |
| Avatar / image area avoids broad Windows system menu behavior | PASS | Large avatar/body drag region remains removed. |
| Bottom Menu opens on first click | PASS | Menu toggle open path works. |
| Bottom Menu closes on second click | PASS | Menu toggle close path works. |
| Escape closes Menu | PASS | Keyboard close path works. |
| Chat bubble expands/collapses | PASS | Still local placeholder UI. |
| Full App hook brings main window forward | PASS | Pet -> Full App bridge works. |
| Hide Pet Window hides the small window | PASS | Full App remains open. |
| Full App Show Pet brings Pet Window back | PASS | Full App -> Pet Window bridge works. |
| Reset Position returns to safe default | PASS | Position reset remains functional. |

Notes:

- No remaining manual smoke note for TASK-130.
- The Windows drag-region limitation remains accepted and documented.
- Pet Mode keeps explicit-handle drag; avatar, bubble, and controls remain no-drag interaction areas.
- Bubble Chat remains local placeholder UI and is not wired to `/chat`.

Safety note:

- No code, IPC, preload API, `main.js`, backend, `/chat`, `/chat` schema, provider settings, Ollama routing, external API, image, file access, Email access, Calendar access, screenshot, microphone, screen-monitoring behavior, or bubble backend wiring was changed for TASK-130.

### TASK-131 - Pet Mode Release Checkpoint

Status: DONE on 2026-05-24.

Checkpoint reference:

- `docs/PET_MODE_RELEASE_CHECKPOINT.md`

Release summary:

- Pet Mode first-stage MVP is checkpointed and maintainable behind `PET_MODE_ENABLED=true`.
- Full App remains the default management surface.
- Pet Window supports explicit-handle drag, no-drag interaction zones, local bubble state, position persistence, menu actions, Pet -> Full App focus, Full App -> Show Pet, Hide Pet Window, Reset Position, and manual Windows smoke PASS.
- Bubble Chat remains a local UI placeholder and is not wired to backend `/chat`.

Deferred items:

- Real Pet Bubble Chat responses.
- Bubble loading / offline / source / mood / error states.
- Mood to expression integration from bubble replies.
- Tray icon.
- Packaging and autostart.
- Full custom drag implementation for whole-character drag.

Safety note:

- No runtime code, backend route, `/chat` call, `/chat` schema change, IPC expansion, external API, file access, Email access, Calendar access, screenshot, microphone, screen-monitoring behavior, image, or bubble backend wiring was added for TASK-131.
- Renderer still does not directly call Ollama.
- Preload APIs remain fixed and narrow.

Next recommendation:

- TASK-132 - Pet Bubble Chat `/chat` Wiring Design.
- TASK-132 should be design-only first and cover loading state, backend offline, `llm_local` / `mock` / error source display, mood to expression integration, long reply handling, timeout / cold-start hints, safe send flow, and no schema change unless explicitly planned.

### TASK-132 - Pet Bubble Chat `/chat` Wiring Design

Status: DONE on 2026-05-24.

Design reference:

- `docs/PET_BUBBLE_CHAT_WIRING_DESIGN.md`

Summary:

- Pet Bubble Chat should wire to the existing local backend `/chat` in a later implementation task.
- `/chat` response schema remains `reply`, `mood`, `source`.
- Pet Mode should render compact bubble replies, source/status badges, loading/error states, and mood-to-expression updates without duplicating Full App.
- Full App remains the troubleshooting and long-reading path.
- Implementation remains deferred.

Planned bubble states:

- collapsed
- expanded
- composing
- empty input
- pending / thinking
- success
- backend offline
- timeout / local cold-start
- llm local error
- fallback mock
- long reply

Safety note:

- No runtime code, backend route, `/chat` call, `/chat` schema change, IPC expansion, external API, file access, Email access, Calendar access, screenshot, microphone, screen monitoring, image, provider settings, Ollama routing, or bubble backend wiring was added for TASK-132.
- Pet renderer must not call Ollama directly.
- Pet renderer may call only the local backend when wiring is implemented.

Follow-up tasks:

- TASK-133 - Pet Bubble Chat Static State Refinement.
- TASK-134 - Pet Bubble `/chat` Client Wiring.
- TASK-135 - Pet Bubble Loading/Error UX.
- TASK-136 - Pet Bubble Mood/Expression Integration.
- TASK-137 - Pet Bubble Long Reply Handling.
- TASK-138 - Pet Bubble Chat Smoke Tests.
- TASK-139 - Manual Windows Pet Bubble Chat Smoke.

### TASK-141 - Display-only Speech Bubble Redesign

Status: DONE on 2026-05-24.

Product direction update:

- Pet Bubble is no longer treated as a tiny full chat panel.
- The visible Pet Bubble is now a display-only comic-style speech bubble.
- Pet Mode focuses on Christina's presence, short replies, mood/expression, and companion feeling.
- Full App is the primary text input, troubleshooting, settings, and long-reading interface.
- Future voice input or push-to-talk should be designed in a separate task.

UI summary:

- Speech bubble uses a light rounded panel with a CSS tail pointing toward Christina.
- Bubble content prioritizes response text and compact source/status.
- Long replies show a short Full App reading hint rather than trying to fit the full answer into `220 x 280`.
- The Pet form/input/send hooks are hidden dev-only hooks retained for `/chat` client helper tests and future dispatch reuse.

Safety note:

- No backend route, `/chat` schema change, IPC expansion, preload API, direct Ollama call, voice feature, speech-to-text, external API, image, file access, Email access, Calendar access, screenshot, microphone, screen-monitoring behavior, tray, packaging, or autostart was added.

### TASK-143 - Full App Reply Mirror Bridge

Status: DONE on 2026-05-24.

Design update:

- Full App remains the primary text input and chat surface.
- Pet speech bubble mirrors the latest Full App AI reply.
- Pet Window does not take over input.
- Full App sends only `reply`, `mood`, and `source` to Pet Mode after successful `/chat`.
- The bridge uses fixed narrow IPC channels: `pet:speech-update` and `pet:speech-received`.
- Pet Window displays mirrored replies through the display-only speech bubble and updates Christina expression from mood.
- Hidden Pet Window is not automatically shown; the Full App `Show Pet` button remains the explicit recovery path.

Safety note:

- No backend route, `/chat` schema change, arbitrary IPC, direct Ollama call, external API, file access, Email access, Calendar access, voice feature, speech-to-text, screenshot, microphone, screen-monitoring behavior, image, tray, packaging, or autostart was added.

Validation note:

- Renderer chat smoke, Pet renderer smoke, Pet window smoke, desktop renderer smoke, backend pytest, direct Ollama `11434` safety scan, and `git diff --check` pass for the bridge checkpoint.

### TASK-144 - Manual Windows Full App -> Pet Speech Mirror Smoke

Status: DONE - PASS WITH NOTE on 2026-05-25.

Manual Windows observation:

- Full App -> Pet speech mirror works.
- Pet speech bubble receives the mirrored reply.
- UX issue: role reply, source/status badge, and helper text were displayed together in the visible bubble.
- The Pet bubble looked too much like a debug panel instead of a compact comic-style companion reply.

Follow-up:

- TASK-145 should make the normal bubble view clean reply only and move source/status/helper details behind click/expand.

### TASK-145 - Pet Speech Bubble Clean Reply + Details Disclosure

Status: DONE on 2026-05-25.

UI behavior:

- The visible Pet speech bubble now defaults to clean Christina reply text only.
- The normal reply box appears directly below Christina's image and above the `Chat / Full App / Menu` action row.
- The reply box auto-expands only up to a safe max height so the fixed `220 x 280` Pet Window and bottom actions stay usable.
- `source`, `mood`, helper text, long-reply hints, and status/debug explanations are hidden in a details area.
- Details open/close by clicking the bubble or the small `i` affordance.
- Details use an internal constrained scroll area and do not resize the `220 x 280` Pet Window.
- Normal `llm_local` replies do not show a distracting `local` badge in the main reply surface.
- Full App remains the primary text input surface.
- Pet Window remains a display/companion layer.

State behavior:

- Normal reply: main bubble shows only the reply.
- `fallback_mock`: main bubble shows mock reply; details explain the source.
- `backend_offline` / `timeout` / `llm_local_error`: main bubble shows a short character-safe error; details carry the Full App/provider status hint.
- Long reply: main bubble shows a truncated preview; details tell the user to read the full content in Full App.

Safety note:

- No backend change, `/chat` schema change, backend route, IPC/preload expansion, direct Ollama access, provider settings change, external API, image, voice, file, Email, or Calendar access was added.

Validation note:

- Pet renderer syntax check, Pet renderer smoke, Pet window smoke, desktop renderer smoke, backend pytest, direct Ollama `11434` safety scan, and `git diff --check` pass for TASK-145.

### TASK-146 - Pet Mode Menu / Controls Consolidation Design

Status: DONE - WINDOWS MANUAL SMOKE PASS on 2026-05-25.

Goal:

- Consolidate Pet Window control behavior after TASK-145 without changing the display-only product direction.
- Keep Full App as the primary text input surface.
- Keep Pet Window as the compact companion display layer.
- Keep the compact Pet Window, Christina image, visible reply bubble, and bottom controls usable. TASK-146 readability UX fix uses `300 x 400` after Windows visual testing found `260 x 340` still cramped.

Control definitions:

- `Chat`: does not open a Pet text box. It should hand off to Full App for typing or show a compact local hint that typing belongs in Full App.
- `Full App`: explicitly opens/focuses Full App through existing Pet-to-Full behavior.
- `Menu`: owns secondary actions: Show/Hide Details or Info, Reset Pet Position, and Hide Pet Window.
- Details/info: remains metadata/debug/helper only and is toggled from Menu only.
- `x`: hides Pet Window through existing Hide Pet behavior. It does not quit the app.

Non-goals:

- No backend, `/chat` schema, provider settings, external API, image, voice, speech-to-text, file, Email, Calendar, screenshot, microphone, or screen-monitoring change.
- No Pet Window text input box.
- No mini full chat app in Pet Window.
- No new IPC/preload APIs unless implementation documents why existing narrow APIs are insufficient.

Implementation note:

- `Chat` opens/focuses Full App through the existing Pet-to-Full behavior and does not add a Pet text input.
- `Full App` keeps the existing explicit Full App open/focus behavior.
- `Menu` includes Show/Hide Details, Reset Pet Position, and Hide Pet Window.
- Menu closes from Menu re-click, left outside-click, Escape, and menu actions that intentionally close it.
- Floating `i` was removed because details/info now lives in Menu.
- Floating `x` maps to Hide Pet Window.
- The visible `speech bubble` status label was removed from the UI.
- Pet Window default size is now `300 x 400`.
- Christina image is larger in speaking mode, targeting roughly 142px.
- Main reply text is 13px with a more comfortable line height.
- Reply bubble grows taller for medium replies while long replies remain constrained.
- Menu height is constrained with internal scroll.
- Existing automated validation passes.
- Windows manual smoke passed after the `300 x 400` readability/size UX fix.

### TASK-147 - Pet Idle / Presence State Polish Design

Status: DONE - WINDOWS MANUAL SMOKE PASS on 2026-05-25.

Goal:

- Define narrow frontend-only idle/presence polish for the Pet Window.
- Keep Full App as the primary text input surface.
- Keep Pet Window as display/companion-only.
- Keep Pet Window default size at `300 x 400`.
- Avoid proactive/idle LLM calls.

State definitions:

- `idle_default`: no recent mirrored reply is active. Christina remains visible and centered. The reply bubble shows the static local hint `吾在。要找吾就去 Full App 說話。` without calling `/chat` or any provider.
- `recent_reply`: latest mirrored Full App reply remains visible for `90` seconds. A newer mirrored reply resets the timer; expiry returns to `idle_default`.
- `handoff`: after Chat or Full App is clicked, Pet shows the local hint `去 Full App 說，吾會聽。` for about `6` seconds while opening/focusing Full App. It does not create Pet input. Handoff expiry restores the active recent reply if still inside its `90` second window, otherwise `idle_default`.
- `long_reply`: keep constrained preview and Full App reading hint in details/menu metadata. Do not auto-open Full App.
- `error`: visible main reply shows only a short readable character-safe message. Source/status/helper/provider/debug details stay in details.
- `hidden_restore`: Hide Pet must not be overridden by idle/presence updates. Show/focus restores the last clean reply if still inside the `90` second window, otherwise `idle_default`, without any LLM call.
- `details_metadata`: details remains Menu-only and can show source, mood, helper/status, and long-reply hint. The main reply remains clean.

Implementation notes:

- New visible bubble states: `idle_default` and `handoff`.
- Recent reply presence is timer-only and local to the Pet renderer.
- Long reply preview, clean main reply, Menu-only details, `300 x 400` layout, larger centered Christina image, readable reply text, and TASK-146 Menu/Hide behavior are preserved.
- Automated validation passed: Pet renderer syntax check, Pet renderer smoke with 42 checks, Pet window smoke with 10 checks, desktop renderer smoke, backend pytest with 586 tests, and direct Ollama `11434` runtime scan.
- Windows manual smoke passed: idle does not call backend/LLM/Ollama/chat, mirrored replies remain clean, recent replies return to idle after about `90` seconds, handoff/menu/details/hide behavior works, and the `300 x 400` layout remains stable.

Acceptance criteria:

- No backend, `/chat` schema, provider settings, external API, image asset, voice, screenshot, microphone, screen monitoring, file, Email, Calendar, or Pet input behavior.
- No new IPC/preload API unless separately justified in docs before implementation.
- No proactive LLM calls for startup, idle, return-from-away, or hide/show.
- `300 x 400` layout remains stable.
- Christina image, clean reply bubble, and `Chat / Full App / Menu` remain usable.
- Details remains Menu-only.
- Main reply never exposes source/status/helper/mood/local/llm_local/debug text.

---

### TASK-148 - Pet Position Persistence / Reset Polish Design

Status: DONE - WINDOWS MANUAL SMOKE PASS on 2026-05-25.

Goal:

- Define narrow Electron-shell position persistence/reset polish for the Pet Window.
- Keep Full App as the primary text input surface.
- Keep Pet Window as display/companion-only.
- Keep Pet Window default size at `300 x 400`.
- Avoid proactive LLM calls.

Position design to implement:

- `restart_restore`: Pet Window should restore the last valid saved position across app restarts.
- `reset_position`: Reset Pet Position should return the Pet Window to a documented safe default, expected to be primary-display bottom-right with visible margins unless implementation finds an existing safer constant.
- `safe_screen_restore`: if saved bounds or center would be off-screen, restore to the safe default instead of creating an unreachable Pet Window.
- `display_change`: monitor add/remove, work-area, resolution, and scaling changes should not leave Pet unreachable. Implementation should choose whether validation runs at launch only or also on Electron display-change events.
- `hide_show_position`: Hide Pet preserves the last valid position; Show Pet restores that position or safe default if invalid.

Acceptance criteria:

- No backend, `/chat` schema, provider settings, external API, image asset, voice, screenshot, microphone, screen monitoring, file, Email, Calendar, or Pet input behavior.
- No new IPC/preload API unless separately justified in docs before implementation.
- No proactive LLM calls for startup, idle, return-from-away, hide/show, reset, or display changes.
- Pet Window remains `300 x 400`.
- Christina image, clean reply bubble, and `Chat / Full App / Menu` remain usable.
- Full App remains the primary input surface.
- Pet Window remains display/companion-only.

Implementation boundary:

- Expected implementation should stay in Electron shell/window lifecycle code and focused smoke tests.
- Runtime implementation should inspect `apps/desktop/src/main.js` and `apps/desktop/scripts/pet-window-smoke.js`.
- Renderer files should only change if a real position/menu integration bug requires it.
- Speech bubble reply, details, idle/recent/handoff behavior, provider behavior, and backend behavior are out of scope.

Implementation notes:

- Reused the existing `userData/pet-window-state.json` position storage.
- Saved positions now restore only when the full `300 x 400` Pet Window fits inside a current display work area.
- Invalid, missing, or off-screen positions fall back to the primary display lower-right safe default with a `24px` margin.
- Show Pet validates bounds before showing/focusing the Pet Window.
- Reset Pet Position uses the existing menu/preload/IPC path, moves to the safe default, and persists immediately.
- Electron display added, removed, and metrics-changed events revalidate Pet Window bounds.
- Pet renderer, backend, `/chat`, provider settings, preload APIs, external APIs, image assets, voice features, Full App renderer behavior, speech state, and Pet Window size were not changed.
- Automated validation passed; Windows manual smoke passed. TASK-148 is closed.

---

### TASK-149 - Pet Bubble Reply / Details Separation Polish Design

Status: IMPLEMENTED - NEEDS WINDOWS MANUAL SMOKE on 2026-05-25.

Goal:

- Keep normal Pet Bubble speech character-facing and clean.
- Hide explanation, debug, details, helper text, source/status/provider diagnostics, and raw payload-style text by default.
- Preserve Full App as the richer diagnostic/debug surface.
- Preserve Pet Window as a `300 x 400` display/companion layer.

Implemented behavior:

- Visible mirrored speech uses the `reply` field only.
- The Full App -> Pet speech bridge remains sanitized to `reply / mood / source`.
- Extra diagnostic-like fields such as `diagnostics`, `details`, `debug`, `provider`, `status`, `helper`, and `explanation` are not rendered as normal Pet Bubble text.
- Existing details UI remains Menu-only; no new details payload channel was added.
- Details/debug payload UI is deferred because the runtime mirror path intentionally drops diagnostic fields before Pet receives mirrored speech.

Acceptance criteria:

- No backend, `/chat` schema, provider settings, external API, image asset, voice, screenshot, microphone, screen monitoring, file, Email, Calendar, or Pet input behavior.
- No new IPC/preload API.
- No proactive LLM calls.
- Pet Window remains `300 x 400`.
- Normal main Pet Bubble never exposes source/status/helper/mood/local/llm_local/debug/provider/raw diagnostic text.
- Full App remains the primary input and diagnostic surface.
- TASK-148 position persistence/reset behavior remains unchanged.

Manual smoke required:

- Confirm normal short/medium replies show only Christina's character-facing reply text.
- Confirm details/debug/source/status/helper content stays hidden unless details are explicitly opened.
- Confirm long reply and error states keep the main bubble clean.
- Confirm TASK-146 controls, TASK-147 idle/recent/handoff behavior, and TASK-148 position behavior still work.

---

### TASK-152 - Pet Bubble Details Disclosure UX Polish Design

Status: IMPLEMENTED - NEEDS WINDOWS MANUAL SMOKE on 2026-05-25.

Implemented UX:

- Normal Pet Bubble speech remains character-facing by default and is not a diagnostics panel.
- Details remain collapsed by default and are still reached through the existing Menu/details path.
- If a mirrored/local payload has no meaningful details metadata, the details disclosure is hidden/disabled instead of showing an empty panel.
- Safe short source/helper/status/debug-style metadata may appear only after explicit disclosure.
- Details are visually secondary and constrained so they do not compete with the main reply or push Chat / Full App / Menu out of the `300 x 400` Pet Window.
- Details sanitization filters raw JSON-like text, provider stack traces, local Ollama endpoint/port text, API-key wording, and thinking/reasoning markers.
- Thinking/reasoning remains hidden from both normal speech and normal details; a future explicit debug-mode task would be required before exposing it anywhere in Pet Window.

Manual smoke required:

- Confirm normal replies show only Christina's character-facing text.
- Confirm details are hidden by default.
- Confirm payloads without meaningful metadata do not show a noisy empty details disclosure.
- Confirm details can open/close from Menu when safe metadata exists.
- Confirm long replies and error states remain clean and constrained.
- Confirm TASK-149, TASK-150, and TASK-151 behavior does not regress.

---

## 9. Explicit Non-goals for TASK-114

This design task does not:

- Modify code.
- Add an Electron window.
- Add renderer files.
- Change backend behavior.
- Change `/chat` schema.
- Add external API calls.
- Add images.
- Change provider settings.
- Change memory behavior.
- Change the existing Full App UI.

---

## 10. Recommended Direction

Recommended product direction:

- Keep Full App Mode as the control center.
- Add Pet Mode as a separate compact renderer and separate BrowserWindow in later tasks.
- Implement Bubble Chat inside the Pet Window first, not as a separate floating window.
- Use transparent/frameless/always-on-top for Pet Mode only.
- Keep click-through out of MVP.
- Right-click menu is implemented in TASK-123; position persistence is implemented in TASK-122.
- Preserve the current local backend-only chat architecture.

Recommended technical direction:

- Main process owns Full App and Pet Window lifecycle.
- Pet renderer owns only pet presentation, bubble state, and local `/chat` calls.
- Preload exposes only narrow window/mode controls if needed.
- Shared expression assets are reused.
- `/chat` contract remains `reply`, `mood`, `source`.

---

## 11. Open Questions

- Should Pet Mode open by default after the feature stabilizes, or should Full App remain the startup default?
- Should closing Full App keep Pet Mode alive?
- Should Pet Mode be hidden from taskbar only after tray support exists?
- Should click-through be a power-user option?
- Should Bubble Chat show only current session messages or reuse recent persisted history?
- Position persistence now lives in Electron user data as of TASK-122.
