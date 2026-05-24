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

- `220 x 280` px

Rationale:

- Large enough for the existing Christina expression assets to remain readable.
- Small enough to sit near a screen edge.
- Gives room for a short hint below the pet.

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

- Use CSS `-webkit-app-region: drag` on a dedicated drag surface around the pet body.
- Use `-webkit-app-region: no-drag` on buttons, inputs, right-click targets, and bubble controls.
- Avoid implementing manual drag math first unless CSS drag is insufficient.

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
- Pet Window uses `220 x 280`, `frame: false`, `transparent: true`, `alwaysOnTop: true`, `resizable: false`, `show: false`, and `ready-to-show` display.
- Pet Window uses `nodeIntegration: false`, `contextIsolation: true`, and `sandbox: true`.
- No preload API, backend call, `/chat` call, drag behavior, context menu behavior, bubble chat behavior, or mode switch behavior was added.

### TASK-117 - Pet Mode Drag Behavior

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

### TASK-118 - Pet Bubble Chat Design

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

### TASK-119 - Mode Switch Full App <-> Pet Mode

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

### TASK-120 - Pet Mode Smoke Tests

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
- Add right-click menu and position persistence after the first Pet Window prototype.
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
- Should position persistence live in Electron user data or through an existing backend settings endpoint?
