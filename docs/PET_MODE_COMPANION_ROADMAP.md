# Pet Mode Companion Roadmap — v0.1 through v0.6

> Task: TASK-165
> Date: 2026-05-27
> Status: STABLE REFERENCE

This document resets the project direction from the stable Pet Mode v0.1 foundation
toward the full desktop AI companion vision. It defines what each version stage
should deliver, why that ordering makes sense, and what the next concrete
implementation task is.

---

## Vision Statement

The end goal is a desktop AI companion that lives near the edge of the screen,
feels present rather than just reactive, can hear the user when addressed, can
optionally see what the user is working on with explicit permission, and offers
proactive — but quiet and cooldown-governed — suggestions when useful. The
companion should feel like a colleague in the room: aware, sometimes helpful,
never noisy, and always under the user's control.

This is meaningfully different from a chat window. The companion is ambient.
It does not require the user to switch focus to interact with it.

---

## v0.1 — Stable Pet Bubble / Pet Window Foundation

**Status: DONE — TASK-148 through TASK-163, TASK-163 regression checkpoint PASS**

### What is complete

| Capability | Task |
|---|---|
| Frameless always-on-top Pet Window (300 × 400) | TASK-148 |
| Position persistence and off-screen fallback | TASK-148 |
| Clean bubble reply-only display — no source / JSON / debug leakage | TASK-148 |
| Details disclosure collapsed by default | TASK-148 |
| Ollama keep_alive / retry on idle cold-start | TASK-150 |
| JSON reply unwrapping | TASK-156 |
| Thinking / reasoning sanitization (`<think>` stripped) | TASK-156 |
| Thinking bubble transition (thinking → reply / error) | TASK-157 |
| Mood selector richness | TASK-155 |
| Mood expression mapping | TASK-156 |
| Idle presence rotation (60 s rotation, 120 s launch quiet) | TASK-158 |
| Idle timing / noise-control cooldown (90 s after chat reply) | TASK-159 |
| Quiet Mode ON/OFF (collapses bubble, suppresses rotation) | TASK-160 |
| Quiet Mode persistence across restart | TASK-162 |
| Corrupt stored quietMode falls back to OFF — no crash | TASK-162 |
| Full regression checkpoint: 83 + 20 + 619 automated, 21-item Windows smoke | TASK-163 |

### What v0.1 does not yet deliver

- The Pet Window feels more like a floating widget than a desktop overlay. The
  window is correctly positioned and sized, but its visual integration with the
  desktop background is minimal.
- There is no direct text input in the Pet Window — the user must switch to the
  Full App to send a message.
- Always-on-top can fail after certain focus changes (full-screen apps, system
  dialogs). No edge-case recovery is implemented.
- Click-through mode does not exist — the window always captures mouse events.
- There is no voice interaction of any kind.
- There is no screen context reading.
- There is no proactive companion behavior beyond cooldown-governed idle rotation.
- The character uses static PNG expression assets. There is no animation.

---

## v0.2 — Desktop Companion Shell

**Status: Planned — recommend TASK-166 (design) as next task**

### Goal

Make the Pet Window feel like a proper always-visible desktop overlay. This is
the physical container that voice, screen context, and Live2D will eventually live
inside. Getting the shell right first prevents rework in every later stage.

### Planned scope

**Overlay visual polish**
- Refine the Pet Window background, shadow, and border so the character sits
  naturally on varied desktop wallpapers and dark/light system themes.
- Ensure the transparent regions are genuinely transparent, not gray or white.
- Remove any visual artifacts that appear during drag or window focus changes.

**Always-on-top reliability**
- Audit the current always-on-top behavior across common Windows focus-change
  scenarios: opening a full-screen game, a system dialog box, a UAC prompt,
  a second monitor switch.
- Add a recovery mechanism (e.g., a brief re-assert of `setAlwaysOnTop` after
  focus returns) for the cases where always-on-top silently drops.

**Drag / resize / scale controls**
- Allow the user to resize the Pet Window or change the character scale without
  restarting.
- Persist the chosen size/scale in `pet-window-state.json` alongside position.
- Drag handle should feel natural — the whole character body, not just a thin
  strip at the top.

**Click-through toggle**
- When the Pet is in ambient display mode (idle, no bubble open), allow mouse
  events to pass through the window to whatever is behind it.
- User can toggle click-through from the Pet menu or a dedicated button.
- Click-through is disabled automatically when the bubble is open.

**Pet direct text input**
- Add a minimal text field directly in the Pet Window so the user can type and
  send a message without switching to the Full App.
- This is the single most important usability gap in v0.1.
- Input goes through the same `/chat` pipeline; no new backend route needed.

**Natural bubble placement**
- The speech bubble should feel visually attached to the character (origin near
  the character's head or mouth area) rather than floating in a fixed position.
- Exact placement depends on the character asset dimensions.

**Demo-ready desktop presence**
- By the end of v0.2 the Pet Window should be polished enough to appear in
  portfolio screenshots and demo recordings without visual apology.

### Why v0.2 before voice and Live2D

Voice interaction (v0.3) requires a stable window that can display a recording
indicator while the user is speaking and remains on-screen during OS audio focus
changes. Live2D (v0.6) requires a correctly sized, correctly positioned window that
handles resize reliably. If always-on-top breaks or the window size changes
unexpectedly, both the voice UI and the Live2D canvas will look wrong. Fixing the
shell first is cheaper than fixing it after those layers are built on top.

Additionally, adding direct text input (v0.2) is the fastest path to making the
companion feel more useful day-to-day. It does not require any new backend work
and immediately removes the main friction point in v0.1.

---

## v0.3 — Voice Interaction

**Status: Planned — depends on v0.2 shell stability**

### Goal

Let the user speak to the companion rather than type. Push-to-talk first — no
always-listening mode — so the privacy surface stays small and the implementation
is tractable without OS-level background service work.

### Planned scope

**Push-to-talk**
- A dedicated button in the Pet Window (or a configurable hotkey) starts
  microphone recording when held or clicked.
- A visible recording indicator is shown while the microphone is active.
- Recording stops when the button is released or clicked again.
- No audio is captured outside of an explicit push-to-talk session.

**Microphone capture**
- Use Electron's `getUserMedia` API (browser-standard) or a Node native audio
  library depending on latency requirements.
- Request microphone permission explicitly; do not assume it.
- Display a clear permission denied message if the OS denies access.

**STT integration**
- Local Whisper (via `whisper.cpp` or a Python binding) is the preferred STT
  backend — no cloud, no ongoing cost, no data leaving the device.
- OS speech recognition (Windows Speech Recognition / macOS dictation API) is
  a simpler fallback if local Whisper proves too heavy on the target hardware.
- The STT result is a plain text transcript.

**Send transcript to `/chat`**
- The transcript is sent to the existing `/chat` endpoint exactly as if the user
  had typed it.
- No new backend route is required.
- The thinking bubble and reply flow work the same as for typed input.

**Optional TTS reply**
- OS text-to-speech reads the reply aloud after it appears in the bubble.
- TTS is opt-in — the user enables it in the Pet menu.
- No custom voice model is required at this stage; OS TTS is sufficient.

**Wake word deferred**
- Always-listening wake word detection is explicitly out of scope for v0.3.
- It requires a background audio process, OS microphone permissions that stay
  active, and a reliable hotword model. Each of those is a separate design task.
- Push-to-talk is the right starting point because it has zero ambient capture.

### Privacy constraints

- Microphone is never active without a visible recording indicator in the Pet Window.
- No audio is stored beyond the current transcription session.
- No audio is sent to any external service by default.
- Users can disable voice input entirely from the Pet menu.

---

## v0.4 — Screen Context

**Status: Planned — depends on v0.3 voice loop being stable**

### Goal

Let the companion optionally understand what the user is working on, with
every capture being explicitly user-triggered. No background surveillance.

### Planned scope

**User-triggered screenshot capture**
- A "Describe my screen" button in the Pet Window captures a screenshot of the
  primary display (or the active window, user's choice) on demand.
- No automatic or periodic capture.
- A visible flash or sound confirms that a capture happened.

**OCR or vision analysis**
- Local OCR (Tesseract via a Python binding) converts screen text to a string
  that is sent as context to `/chat`.
- A local vision model (e.g., LLaVA via Ollama) can provide richer scene
  description if the hardware supports it.
- The choice between OCR-only and vision model is a user setting.

**Screen context as optional chat input**
- The captured text or description is prepended to the user's next message as
  a `[Screen context: ...]` block.
- The user can review and discard the context before sending.
- No context is injected automatically without the user's confirmation.

**Privacy and redaction**
- Before the screen text is sent to the model, a simple pattern filter removes
  common sensitive-content shapes: API keys, passwords in visible fields,
  credit card number patterns, and similar.
- The user can configure which redaction patterns are active.
- Raw screenshot pixels are never stored and never sent to any external service.

### Privacy constraints

- No background screen recording under any circumstance.
- Every capture requires an explicit user action.
- Captured data is discarded after the `/chat` response is received.
- Users can disable screen context entirely from settings.

---

## v0.5 — Proactive Companion

**Status: Planned — depends on v0.4 context system being stable**

### Goal

The companion notices when the user might benefit from a nudge and offers one —
once, quietly, after an appropriate cooldown — without becoming annoying.

### Planned scope

**User-approved context watching**
- The companion monitors a narrow set of activity signals — idle time, app in
  focus, last chat timestamp — only after the user has explicitly enabled
  proactive mode.
- Default: proactive mode is OFF.

**Cooldown-based proactive nudges**
- A nudge is only sent after a configurable cooldown since the last interaction
  or the last nudge.
- Minimum cooldown: 30 minutes (configurable upward, not downward below 10 min).
- At most one proactive message per session by default.

**Work-state awareness**
- The companion distinguishes between active work (recent keyboard/mouse
  activity), idle (no activity for N minutes), and break (very long idle).
- Nudge content and tone adapt to the detected state.
- No OS-level keylogger or input hook; idle detection uses the existing
  `presenceState` timer pattern from pet-renderer.

**Quiet Mode and Focus Mode integration**
- Quiet Mode always suppresses proactive nudges — no exceptions.
- A separate Focus Mode toggle (to be designed) suppresses nudges without
  collapsing the bubble, for users who want the companion visible but silent.
- Proactive content goes through the same `setIdleQuietBubble` / bubble state
  machine as idle rotation, so the suppression logic is consistent.

**No noisy interruptions**
- Proactive nudges use the same visual path as idle hints (the `idle_default`
  bubble state), not a modal, alert, or notification.
- Sound is never used for proactive nudges unless the user has explicitly enabled
  TTS for all replies.

---

## v0.6 — Live2D / Rich Character Presentation

**Status: Planned — depends on v0.2–v0.5 interaction loop being stable**

### Goal

Replace the static PNG expression assets with a Live2D animated model that moves
naturally, blinks, shifts posture, and expresses mood through motion rather than
a static image swap.

### Planned scope

**Live2D Cubism SDK integration**
- Integrate the Live2D Cubism SDK for Electron (WebGL renderer in the Pet Window).
- The Live2D canvas replaces the current `<img>` expression element.
- No other UI structure changes.

**Motion clips**
- Idle motion: subtle breathing, occasional head tilt, blink.
- Thinking motion: tilted head, slightly furrowed expression.
- Happy / excited motion: upbeat posture shift.
- Worried motion: head lowered, tighter expression.
- Talking motion: synchronized with TTS output from v0.3.
- Sleepy motion: slow blink, drooping posture.

**Expression parameter mapping**
- The existing `mood → expression` mapping is extended to drive Live2D
  expression parameters (eye openness, mouth curve, eyebrow position) rather
  than swapping PNG files.
- The public API (`setPetExpression`, `renderPetSpeechUpdate`) does not change;
  only the renderer implementation changes.

**Mouth movement with TTS (v0.3 dependency)**
- If TTS is active (v0.3), mouth open/close parameters are synchronized with
  the audio output.
- If TTS is disabled, mouth movement plays a generic talking animation during
  reply display.

### Why Live2D waits until v0.2–v0.5 are stable

The character's behavioral model — what it says, when it speaks, how it responds
to Quiet Mode, voice input, screen context, and proactive nudges — should be
complete and stable before the visual layer is upgraded. If the behavior changes
after Live2D is integrated (e.g., adding proactive nudges requires new motion
clips), that means Live2D work that was already done gets revisited.

Additionally, Live2D requires the window to maintain a stable size and a reliable
always-on-top position (v0.2 dependency). Upgrading the visual layer before the
shell is solid creates rework risk.

The correct order is: stable shell → stable interaction loop → stable character
behavior → Live2D visual upgrade.

---

## Next Implementation Task

**TASK-166 | Pet Overlay Shell Polish Design**

Define the v0.2 overlay shell improvements as a focused design task before
writing any runtime code.

### What TASK-166 should cover

- Audit current always-on-top behavior across 5–8 common Windows focus-change
  scenarios and document which ones cause the Pet Window to fall behind.
- Design the click-through toggle: IPC channel, preload exposure, UI element in
  Pet menu, and automatic disable when bubble is open.
- Design the Pet direct text input: HTML element, send flow, connection to the
  existing `/chat` call in `pet-renderer.js`, keyboard shortcut.
- Design drag/scale controls: which resize handles to expose, how scale
  preference is stored in `pet-window-state.json`, IPC surface.
- Define acceptance criteria for "overlay polished": no visual artifacts,
  always-on-top survives N specified focus-change scenarios, click-through
  toggled with one action, direct send works end-to-end.

### Why design first

The overlay shell touches the IPC bridge, the preload, and window management
in `main.js`. A design document first prevents ad-hoc IPC channel proliferation,
keeps the safety review lightweight, and gives a clear acceptance gate before
implementation begins. The pattern has worked well across TASK-148–TASK-165.

---

## What Not to Do Next

Deliberately sequenced constraints to prevent common missteps:

| Do not | Reason |
|---|---|
| Jump straight to Live2D | Live2D requires a stable shell (v0.2) and a stable behavior model (v0.3–v0.5) — building it first creates rework |
| Implement background screen surveillance | Unacceptable privacy surface; all screen capture must be user-triggered (v0.4 design) |
| Build broad settings architecture now | Settings complexity should grow with features; adding settings infrastructure before the features exist is over-engineering |
| Add wake word before push-to-talk is stable | Wake word requires a background audio process with ambient microphone access — too large a privacy jump to make before push-to-talk (v0.3) is validated |
| Add proactive nudges before cooldown and context rules are reliable | Proactive messages without reliable suppression become spam; v0.5 depends on v0.4 context being trustworthy |
| Polish the Live2D model before the behavior is stable | Behavior changes drive new motion clip requirements; finish the behavioral model first |
| Add cloud sync or account system | Local-first is a core product decision; no cloud backend in scope for any of v0.2–v0.6 |

---

## Summary Table

| Version | Theme | Key deliverable | Dependency |
|---|---|---|---|
| v0.1 | Stable foundation | Clean bubble, idle rotation, Quiet Mode persistence | — |
| v0.2 | Desktop shell | Direct input, click-through, drag, overlay polish | v0.1 stable |
| v0.3 | Voice | Push-to-talk, local STT, optional TTS | v0.2 shell stable |
| v0.4 | Screen context | User-triggered capture, OCR, privacy redaction | v0.3 loop stable |
| v0.5 | Proactive | Cooldown nudges, work-state awareness, Focus Mode | v0.4 context stable |
| v0.6 | Live2D | Animated model, motion clips, TTS mouth sync | v0.2–v0.5 stable |

---

## Reference

| Document | Topic |
|---|---|
| `docs/PET_MODE_DEMO.md` | Pet Mode v0.1 demo / portfolio packaging |
| `docs/PET_MODE_RELEASE_CHECKPOINT.md` | TASK-163 regression checkpoint and 21-item Windows smoke record |
| `docs/PET_MODE_UI_DESIGN.md` | Original Pet Mode UI design (TASK-114) |
| `docs/PET_BUBBLE_CHAT_WIRING_DESIGN.md` | Bubble chat wiring design |
| `docs/PHASE5_COMPANION_BEHAVIOR_PLAN.md` | Phase 5 companion behavior loop design (Chinese) |
| `docs/PET_MODE_MANUAL_SMOKE_RUNBOOK.md` | Windows manual smoke runbook |
| `docs/TASKS.md` | Full task history |
| `docs/ROADMAP.md` | Phase-by-phase status |
