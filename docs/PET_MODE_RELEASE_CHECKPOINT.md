# Pet Mode Release Checkpoint

> Task: TASK-131 - Pet Mode Release Checkpoint
> Date: 2026-05-24
> Status: DONE - Pet Mode first-stage MVP checkpoint

This checkpoint records the completed first-stage Pet Mode surface after TASK-114 through TASK-130.

Pet Mode is now a maintainable MVP for a small desktop pet window that can coexist with the Full App. Bubble Chat remains a local UI placeholder and is intentionally not wired to `/chat` yet.

## Completed Capabilities

- Optional Pet Window starts only when `PET_MODE_ENABLED=true`.
- Full App remains the default startup and management surface.
- Pet Window is `220 x 280`, frameless, transparent, always-on-top, and non-resizable.
- Pet Mode uses a separate static renderer under `apps/desktop/src/pet`.
- Christina avatar uses the existing expression asset path.
- Pet hint text is rendered locally.
- Bubble Chat placeholder exists with collapsed / expanded local UI state.
- Explicit top drag handle supports moving the Pet Window.
- Avatar, bubble, menu, buttons, inputs, and controls are no-drag interaction zones.
- Pet Window can ask main process to show / focus Full App.
- Full App can show / focus Pet Window after it has been hidden.
- Pet menu supports Open Full App, Reset Pet Position, Hide Pet Window, and Close Menu.
- Bottom Menu button toggles open / closed.
- Escape closes the menu.
- Pet Window position persists locally under Electron `userData`.
- Off-screen saved positions fall back to a safe default.
- Manual Windows drag/menu smoke passed.

## Deferred Items

- Bubble Chat is not wired to `/chat`.
- Pet Mode does not yet display real LLM responses.
- Pet bubble does not yet show source / mood / error / loading states from backend responses.
- Pet bubble does not yet integrate backend mood with expression updates.
- Tray icon support is not implemented.
- Package / installer / autostart behavior is not implemented.
- Full custom drag implementation is not implemented.
- Whole-character dragging is deferred.
- Windows CSS drag-region right-click can still trigger the OS system menu on the explicit handle; large avatar/body drag remains intentionally disabled.

## Safety Boundaries

- Pet Mode does not automatically read files.
- Pet Mode does not read Email.
- Pet Mode does not read Calendar.
- Pet Mode does not execute commands.
- Pet Mode does not call external APIs.
- Pet Mode does not secretly take screenshots.
- Pet Mode does not record audio.
- Pet Mode does not monitor the screen.
- Pet Mode does not modify `/chat` schema.
- Pet renderer does not directly call Ollama.
- Pet renderer currently does not call backend `/chat`.
- IPC channels are fixed and narrow.
- Preload APIs do not expose arbitrary `ipcRenderer`.
- Preload APIs do not expose fs, shell, or process.

## Smoke And Test Results

Recorded checkpoint results:

- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/src/renderer/preload.js`: PASS.
- `node --check apps/desktop/src/pet/pet-renderer.js`: PASS.
- `node --check apps/desktop/src/pet/pet-preload.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `node --check apps/desktop/scripts/pet-renderer-smoke.js`: PASS.
- `node --check apps/desktop/scripts/pet-window-smoke.js`: PASS.
- `node apps/desktop/scripts/pet-renderer-smoke.js`: PASS, 13 checks.
- `node apps/desktop/scripts/pet-window-smoke.js`: PASS, 10 checks.
- `npm.cmd run test:renderer`: PASS.
- `python -m pytest`: PASS, 586 passed.
- Direct Ollama `11434` safety scan: PASS.
- Manual Windows Pet drag/menu smoke: PASS.

Manual Windows smoke confirmed:

| Check | Result |
|---|---|
| Top drag handle drags Pet Window | PASS |
| Avatar / image area avoids broad Windows system menu behavior | PASS |
| Bottom Menu opens on first click | PASS |
| Bottom Menu closes on second click | PASS |
| Escape closes Menu | PASS |
| Chat bubble expands/collapses | PASS |
| Full App hook brings main window forward | PASS |
| Hide Pet Window hides the small window | PASS |
| Full App Show Pet brings Pet Window back | PASS |
| Reset Position returns to safe default | PASS |

## Recommended Next Stage

Recommended next task:

- TASK-132 - Pet Bubble Chat `/chat` Wiring Design

TASK-132 should be design-only before implementation. It should plan:

- Bubble loading state.
- Backend offline state.
- `llm_local`, `mock`, and error source display.
- Mood to expression integration.
- Long reply handling.
- Timeout and local cold-start hint behavior.
- Safe send flow.
- No `/chat` schema change unless explicitly planned and reviewed.

## Release Decision

Pet Mode first-stage MVP is ready to checkpoint.

It is suitable for continued manual use behind `PET_MODE_ENABLED=true`, with Bubble Chat backend wiring deferred to a separate design task.
