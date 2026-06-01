# Interaction Output Queue / Priority Design

**Task:** TASK-226
**Status:** IMPLEMENTED - DOCS ONLY / NO WINDOWS SMOKE REQUIRED
**Date:** 2026-06-01
**Scope:** Architecture/design only. No runtime behavior is implemented here.

This document defines a future interaction output queue and priority model for
Dragon Pet AI. It is a design reference only. It does not change the renderer,
Pet Window, backend, `/chat`, IPC, TTS, STT, prompts, assets, or persistence.

---

## 1. Purpose

Dragon Pet AI now has multiple companion output paths:

- Full App chat replies.
- Pet Window expression mirrors.
- Fixed reaction bubbles.
- Local diagnostics preview.

Future features may add more output paths:

- Idle reactions.
- TTS playback.
- STT-confirmed transcript handoff.
- Manual Pet input.
- Notifications or reminders.
- Long reply display segments.
- TTS-safe speech segments.

Without an explicit queue and priority model, these outputs can compete for the
same UI and audio surfaces. This design defines future arbitration rules so chat
replies, reaction bubbles, idle reactions, TTS, manual input, notifications, and
diagnostics do not collide.

This is not runtime. It is the design boundary for future implementation tasks.

---

## 2. Problem Statement

Output conflicts to avoid:

- An LLM reply is visible, then a reaction bubble replaces it too aggressively.
- TTS starts speaking while an idle reaction or another reply is active.
- User-triggered Pet input competes with automatic or ambient output.
- Reaction bubbles repeat too often or appear during higher-priority work.
- Notifications or reminders interrupt active user-driven workflows.
- Debug preview or metadata leaks into bubble text or TTS.
- Long reply segmentation conflicts with short Pet bubble TTL behavior.

The system needs deterministic rules before adding idle reactions, TTS,
notifications, or richer Pet responses.

---

## 3. Output Source Inventory

Current output sources:

- `chat_reply`
- `pet_expression_mirror`
- `reaction_bubble`
- `diagnostics_preview`

Future output sources:

- `idle_reaction`
- `tts_playback`
- `stt_confirmed_transcript`
- `manual_pet_input`
- `notification_reminder`
- `long_reply_display_segment`
- `tts_safe_speech_segment`

---

## 4. Proposed Priority Levels

Priority levels are ordered from highest to lowest.

### P0 - Critical Safety / Error

Examples:

- Crash-safe fallback.
- Backend error display.
- TTS error safe fallback.
- User safety-critical warning.

### P1 - User Direct Action

Examples:

- User submitted chat message.
- Manual Pet input.
- Explicit button action.
- Explicit show/hide/menu command.

### P2 - LLM Chat Reply

Examples:

- Normal `/chat` reply.
- Long reply display segments.
- Future TTS-safe speech derived from an LLM reply.

### P3 - Important Companion Reaction

Examples:

- `attention_returned`.
- `correction`.
- `reset`.
- High-confidence behavior decision reaction.

### P4 - Normal Companion Reaction

Examples:

- `user_active`.
- `message_management`.
- Fixed short reaction bubble.

### P5 - Idle / Ambient Reaction

Examples:

- Future idle bubble.
- Future low-frequency mood line.
- Future silent expression-only reaction.

### P6 - Diagnostics Only

Examples:

- Full App preview.
- State / decision debug.
- Internal counters.

---

## 5. Preemption Rules

Proposed interruption rules:

- P0 can interrupt all.
- P1 can interrupt P2-P6.
- P2 can suppress P3-P5 while active.
- P3 can interrupt P4-P5, but not P1 or P2.
- P4 cannot interrupt P1, P2, or P3.
- P5 never interrupts anything.
- P6 never causes side effects.

Design intent:

- User actions and safety always win.
- LLM replies should remain stable while active.
- Companion reactions should feel responsive, but not noisy.
- Diagnostics should never affect runtime behavior.

---

## 6. Bubble Display Rules

Future bubble arbitration should follow these rules:

- Reaction bubbles should not replace an active LLM reply bubble unless allowed
  by priority.
- Reaction bubble TTL should be short.
- Repeated identical bubbles should be suppressed by cooldown.
- Fixed reaction bubbles should never enter chat history.
- Fixed reaction bubbles should never be exported or copied.
- Reaction bubbles should not be sent to TTS by default.
- Long reply display segments should not be truncated by reaction-bubble TTL.

---

## 7. Expression Rules

Expression output is lower risk than bubble text, but still needs boundaries:

- Expression mirror is lower risk than bubble text.
- Expression may update more freely than bubble text.
- Expression should still obey debounce or coalescing.
- Expression should not imply spoken output.
- Expression should not create history entries.
- Expression should not trigger TTS.

---

## 8. TTS Future Rules

TTS is not changed by TASK-226. Future TTS queue work should follow these rules:

- TTS is default off.
- TTS never calls `/chat` by itself.
- TTS only reads TTS-safe text.
- TTS never reads debug preview.
- TTS never reads metadata, JSON, source labels, or thinking text.
- TTS uses a queue so speech does not overlap.
- TTS allows user stop/cancel.
- Speech and singing must be separate capabilities.
- Voice cloning requires legally authorized data.

---

## 9. STT Future Rules

STT is not changed by TASK-226. Future STT queue work should follow these rules:

- Push-to-talk or explicit user action only.
- No always listening.
- Transcript confirmation before `/chat` if needed.
- Do not store raw audio by default.
- Do not send unconfirmed ambient audio to an LLM.

---

## 10. Queue Item Schema Proposal

TASK-228 implements the first disabled-by-default renderer skeleton using this
queue item shape:

```js
{
  id,
  source,
  priority,
  channel,
  payload,
  createdAt,
  ttlMs,
  interruptible,
  ttsEligible,
  historyEligible,
  copyExportEligible,
  reason
}
```

Schema guidance:

- `payload` must be sanitized per source.
- Reaction bubble payload must not contain raw user text.
- Diagnostics preview should not become a side-effect queue item.
- `ttsEligible` should default to `false`.
- `historyEligible` should default to `false` for reactions.
- `copyExportEligible` should default to `false` for reactions and diagnostics.

---

## 11. Channel Taxonomy

Potential future queue channels:

- `visual_expression`
- `pet_bubble`
- `full_app_chat`
- `tts_audio`
- `diagnostics_preview`
- `notification`

This taxonomy is conceptual. TASK-226 did not add IPC or runtime channels.
TASK-228 uses the taxonomy as local renderer allowlist values only; it still
does not add IPC or dispatch channels.

---

## 12. Safety Boundary / Forbidden List

The output queue design must not allow:

- Proactive long-form speech without explicit future design.
- Always listening.
- Hidden capture.
- Screenshot capture.
- OCR.
- Debug preview sent to TTS.
- Reaction bubble written into chat history.
- Reaction bubble included in copy/export.
- Raw user message text sent into reaction bubble payloads.
- Generic or broad IPC.
- Lower-priority output interrupting direct user action.
- LLM-generated reaction bubbles unless a future task explicitly designs safe
  generation.

---

## 13. Relationship to Existing Docs

Related current docs:

- `docs/INTERACTIVE_COMPANION_ARCHITECTURE.md`
- `docs/CHRISTINA_PERSONA_CONTEXT_PACK.md`
- `docs/VOICE_TTS_RESEARCH.md`

Voice/TTS research design docs:

- TASK-227 adds `docs/VOICE_TTS_RESEARCH.md`.
- Voice/TTS research supplies provider candidates, licensing boundaries, and
  local-first speech roadmap.
- This output queue design supplies timing, priority, and interruption rules for
  any future TTS/STT runtime.

---

## 14. Recommended Future Implementation Tasks

Suggested future tasks:

- TASK-228 Output Queue Runtime Skeleton and Diagnostics Preview, disabled by
  default. DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS.
- TASK-229 Output Queue Debug Preview / Snapshot Polish. DONE - WINDOWS VISUAL
  SMOKE PASS / DONE - PASS.
- TASK-230 Bubble Priority Enforcement.
- TASK-231 TTS-safe segment design.
- TASK-232 Idle Reaction Policy, fixed only, no LLM.
- TASK-233 User controls for companion reaction verbosity.

Each task should remain narrow, testable, and explicit about side-effect
boundaries.

---

## 15. TASK-226 Runtime Boundary

TASK-226 is docs-only. It does not:

- Change renderer behavior.
- Change Pet Window behavior.
- Change backend behavior.
- Change `/chat` API schema.
- Change chat history persistence format.
- Add IPC.
- Add generic IPC.
- Add TTS.
- Add STT.
- Call `/chat`.
- Change Ollama / Provider runtime.
- Change prompt runtime.
- Add assets.
- Commit or push changes.

---

## 16. TASK-228 Runtime Skeleton Status

TASK-228 implements a Full App renderer-only skeleton of this design. It is
disabled by default and does not dispatch output. Automated smoke and Windows
visual smoke PASS were confirmed on 2026-06-01.

Implemented local state and helpers:

- `OUTPUT_QUEUE_ENABLED = false`
- `OUTPUT_QUEUE_MAX = 50`
- `OUTPUT_QUEUE_RECENT_MAX = 20`
- Priority allowlist P0-P6.
- Channel allowlist:
  `visual_expression`, `pet_bubble`, `full_app_chat`, `tts_audio`,
  `diagnostics_preview`, `notification`.
- Source allowlist:
  `chat_reply`, `manual_pet_input`, `reaction_bubble`, `expression_mirror`,
  `idle_reaction`, `tts_playback`, `stt_transcript`, `notification`,
  `diagnostics_preview`, `safety_error`.
- `sanitizeOutputQueueItem(input)`.
- `enqueueOutputQueueItem(input)`.
- `getOutputQueueSnapshot()`.
- `clearOutputQueue(reason)`.
- `compareOutputPriority(a, b)`.
- `shouldOutputPreempt(activeItem, incomingItem)`.

Forbidden fields are dropped from payloads and queue summaries:

- `message`
- `text`
- `body`
- `rawText`
- `content`
- `reply`
- `transcript`
- `audio`
- `html`
- `innerHTML`
- `metadata`
- `debug`
- `thinking`

Diagnostics preview now displays:

```text
Queue: disabled · Items: <count>
```

Runtime boundary:

- No dispatch loop.
- No IPC.
- No generic IPC.
- No Pet Window send.
- No `/chat` call.
- No history write.
- No TTS/STT/audio runtime.
- No prompt runtime.
- No persistence.
- No Pet Bubble runtime behavior change.
- No Pet expression mirror runtime behavior change.
- No reaction bubble mirror runtime behavior change.
- No raw message text storage or forwarding.

TASK-228 automated renderer smoke covers sanitization, queue caps, invalid
token rejection, priority/preemption helpers, diagnostics preview boundaries,
history/copy/export exclusion, no side effects, and narrow IPC regression
guards.

Windows visual smoke PASS confirmed:

- Startup shows `Queue: disabled · Items: <valid number>` and Pet Window remains
  normal.
- Send message, Delete/Undo, Edit last user, Clear Chat, and Focus remain
  functional while Queue stays disabled.
- Diagnostics format has no `undefined`, `null`, `NaN`, `[object Object]`, raw
  JSON, or user text.
- No new IPC side effect, extra TTS, extra `/chat`, history/copy/export
  pollution, or Pet Window expression/reaction bubble regression.

The runtime skeleton is complete but still does not control execution. Any
future dispatch/arbitration task must explicitly opt in and preserve the same
side-effect boundaries.

---

## 17. TASK-229 Debug Preview / Snapshot Polish

TASK-229 polishes the TASK-228 disabled runtime skeleton diagnostics preview.
It remains Full App renderer-only. Automated smoke and Windows visual smoke PASS
were confirmed on 2026-06-01.

Implemented:

- `formatOutputQueueSnapshotPreview(snapshot)`.
- Safe `nextItem` summary through `getOutputQueueSnapshot()`.
- Diagnostics preview integration.
- Initial HTML fallback text update.

Preview format:

```text
Queue: disabled · Items: 0 · Recent: 0 · Next: none
```

With a safe queued item:

```text
Queue: disabled · Items: 1 · Recent: 1 · Next: P4_NORMAL_REACTION/pet_bubble/reaction_bubble
```

`Next` displays only `priority/channel/source`. It does not display payload,
id, raw JSON, raw user message text, raw event payload, debug metadata,
`undefined`, `null`, `NaN`, or `[object Object]`.

`getOutputQueueSnapshot()` now exposes `nextItem` as a sanitized summary only.
Allowed summary fields are:

- `id`
- `source`
- `priority`
- `channel`
- `reason`
- `ttlMs`

Fallback rules:

- Invalid `enabled` -> `disabled`.
- Invalid `length` -> `0`.
- Invalid `recentLength` -> `0`.
- Missing or invalid `nextItem` -> `Next: none`.
- Invalid `priority`, `source`, or `channel` -> `Next: none`.

TASK-229 does not add dispatch or execution control. It does not add IPC, send
anything to the Pet Window, call `/chat`, write history, trigger TTS/STT/audio,
change expression mirror behavior, change reaction bubble mirror behavior,
connect prompt runtime, add persistence, or store raw message text.

Automated renderer smoke PASS.

Windows visual smoke PASS confirmed:

- Startup shows `Queue: disabled · Items/Recent/Next` and Pet Window remains
  normal.
- Send message keeps chat, expression, and reaction bubble normal; Queue remains
  disabled; `Next` displays a safe summary.
- Delete/Undo, Edit last user, Clear Chat, and Focus remain functional with
  Queue disabled.
- Diagnostics format has no `undefined`, `null`, `NaN`, `[object Object]`, raw
  JSON, user text, or payload.
- No new IPC side effect, extra TTS, extra `/chat`, history/copy/export
  pollution, or Pet Window expression/reaction bubble regression.

The snapshot preview polish is complete but still does not control execution.
Any future dispatch/arbitration task must explicitly opt in.
