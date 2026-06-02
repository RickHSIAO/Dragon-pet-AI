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
- TASK-230 Enqueue Reaction Bubble Diagnostics Only. DONE - WINDOWS VISUAL
  SMOKE PASS / DONE - PASS.
- TASK-231 Enqueue Expression Mirror Diagnostics Only. DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS.
- TASK-232 Enqueue Chat Reply Diagnostics Only. DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS.
- TASK-233 Idle Reaction Policy, fixed only, no LLM.
- TASK-234 User controls for companion reaction verbosity.

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

---

## 18. TASK-230 Reaction Bubble Diagnostics Enqueue

TASK-230 connects the existing safe reaction bubble record path to the disabled
output queue as local diagnostics only. It remains Full App renderer-only and
does not dispatch output. Automated smoke PASS and Windows visual smoke PASS
were confirmed; the Windows visual smoke date is 2026-06-01.

Implemented helper:

- `enqueueReactionBubbleOutputDiagnostics(bubble)`

Behavior:

- Sanitizes `bubble.id` through `INTERACTION_REACTION_BUBBLE_ALLOWLIST`.
- Enqueues only safe non-`none` reaction bubble ids.
- Ignores `none`, empty, or invalid bubble ids.
- Calls `enqueueOutputQueueItem(...)`.
- Works while `OUTPUT_QUEUE_ENABLED = false`.
- Does not send anything to the Pet Window.
- Does not replace or drive `mirrorInteractionReactionBubble(...)`.
- Does not throw if the Pet bridge is absent.

TASK-230 reaction bubble diagnostics item:

```js
{
  source: "reaction_bubble",
  priority: "P4_NORMAL_REACTION",
  channel: "pet_bubble",
  payload: {
    bubbleId: "<safe bubble id>"
  },
  ttlMs: 3000,
  interruptible: true,
  ttsEligible: false,
  historyEligible: false,
  copyExportEligible: false,
  reason: "interaction_reaction_bubble"
}
```

The payload only contains `bubbleId`. It does not contain reaction bubble text,
user message text, raw event payload, hint, message/body/content/reply fields,
transcript/audio fields, HTML, metadata, debug data, or thinking text.

Preview after a safe `user_active` reaction bubble can show:

```text
Queue: disabled · Items: 1 · Recent: 1 · Next: P4_NORMAL_REACTION/pet_bubble/reaction_bubble
```

The preview still does not expose raw payload, raw JSON, user text, fixed
reaction bubble text, `undefined`, `null`, `NaN`, or `[object Object]`.

TASK-230 preserves the TASK-218 and TASK-220 narrow IPC channels:

- `pet:expression-suggestion`
- `pet:expression-suggestion-received`
- `pet:reaction-bubble`
- `pet:reaction-bubble-received`

No generic `"pet"` channel is used for those mirrors.

TASK-230 does not add IPC, dispatch, Pet Window runtime behavior, Pet Bubble
visible behavior, expression mirror changes, reaction bubble mirror payload
changes, `/chat`, history writes, TTS/STT/audio, prompt runtime, persistence,
assets, hover action buttons, or message edit scope changes.

Windows visual smoke PASS confirmed on 2026-06-01:

- Basic startup PASS: Preview shows `Queue: disabled · Items/Recent/Next`; Pet
  Window remains normal.
- Send message PASS: reaction bubble remains normal, Queue enqueues the
  diagnostics item, and `Next` shows
  `P4_NORMAL_REACTION/pet_bubble/reaction_bubble`.
- Delete / Undo PASS: feature remains normal; Queue stays disabled.
- Edit last user PASS: feature remains normal; Queue stays disabled.
- Clear Chat PASS: feature remains normal; Queue stays disabled.
- Focus PASS: feature remains normal; Queue stays disabled.
- Queue diagnostics format PASS: no `undefined`, `null`, `NaN`,
  `[object Object]`, raw JSON, user text, bubble text, or payload.
- General regression PASS: no new IPC side effect, no extra TTS, no extra
  `/chat`, no history/copy/export pollution, and Pet Window expression plus
  reaction bubble behavior remains normal.

The output queue can now record reaction bubble output intent for diagnostics,
but it still does not control execution.

---

## 19. TASK-231 Expression Mirror Diagnostics Enqueue

TASK-231 connects the existing safe expression mirror record path to the disabled
output queue as local diagnostics only. It remains Full App renderer-only and
does not dispatch output. Renderer automated smoke PASS and Windows visual smoke
PASS confirmed on 2026-06-01.

`enqueueExpressionMirrorOutputDiagnostics(expression)` is called from
`recordInteractionExpressionSuggestion` immediately before
`mirrorInteractionExpressionSuggestion(expression)`. This means every safe
expression mirror event produces one diagnostics-only queue item.

TASK-231 expression mirror diagnostics item:

```js
{
  source: "expression_mirror",
  priority: "P4_NORMAL_REACTION",
  channel: "visual_expression",
  payload: { expression: "<safe expression>" },
  ttlMs: 0,
  interruptible: true,
  ttsEligible: false,
  historyEligible: false,
  copyExportEligible: false,
  reason: "interaction_expression_suggestion",
}
```

`payload` contains only `expression`. Calling the helper directly with an invalid
expression returns `null` (no-op). The record path sanitizes unknown → `"neutral"`
before calling, so the record path always enqueues.

The preview after a full `chat_message_sent` event (expression_mirror first, then
reaction_bubble from TASK-230):

```
Queue: disabled · Items: 2 · Recent: 2 · Next: P4_NORMAL_REACTION/visual_expression/expression_mirror
```

TASK-231 preserves the TASK-218 and TASK-220 narrow IPC channels:

- `pet:expression-suggestion`
- `pet:expression-suggestion-received`
- `pet:reaction-bubble`
- `pet:reaction-bubble-received`

No generic `"pet"` channel is used for those mirrors.

TASK-231 does not add IPC, dispatch, Pet Window runtime behavior, Pet Bubble
visible behavior, expression mirror IPC payload changes, expression mirror
scheduling or TASK-219 debounce changes, reaction bubble mirror payload
changes, `/chat`, history writes, TTS/STT/audio, prompt runtime, persistence,
assets, hover action buttons, or message edit scope changes.

Windows visual smoke PASS confirmed on 2026-06-01:

- Basic startup PASS: Preview shows `Queue: disabled · Items/Recent/Next`; Pet
  Window remains normal.
- Send message PASS: expression mirror remains normal, reaction bubble remains
  normal, Queue enqueues the `expression_mirror` diagnostics item, and `Next`
  shows `P4_NORMAL_REACTION/visual_expression/expression_mirror`.
- Delete / Undo PASS: feature remains normal; Queue stays disabled.
- Edit last user PASS: feature remains normal; Queue stays disabled.
- Clear Chat PASS: feature remains normal; Queue stays disabled.
- Focus PASS: feature remains normal; Queue stays disabled.
- Queue diagnostics format PASS: no `undefined`, `null`, `NaN`,
  `[object Object]`, raw JSON, user text, bubble text, or payload.
- General regression PASS: no new IPC side effect, no extra TTS, no extra
  `/chat`, no history/copy/export pollution, and Pet Window expression plus
  reaction bubble behavior remains normal.

The output queue can now record both expression mirror intent and reaction
bubble intent as local diagnostics, but it still does not control execution.

---

## 20. TASK-232 Chat Reply Diagnostics Enqueue

TASK-232 connects both `/chat` success paths in the Full App renderer to the
disabled output queue as local diagnostics only. It remains Full App renderer-only
and does not dispatch output. Renderer automated smoke PASS confirmed on 2026-06-02.
Windows visual smoke PASS confirmed on 2026-06-01.

`enqueueChatReplyOutputDiagnostics({ reply, mood, source })` is called immediately
after the chat reply is rendered to the chat area, in both the main `sendMessage`
flow (after `appendMessage("pet", data.reply, ...)`) and the edit flow (after
`renderFormalChatEntries(finalEntries)`). This means every successful `/chat`
response that reaches the display layer produces one diagnostics-only queue item.

TASK-232 chat reply diagnostics item:

```js
{
  source: "chat_reply",
  priority: "P2_LLM_REPLY",
  channel: "full_app_chat",
  payload: { source: "<safe source>", mood: "<safe mood>", replyLength: <number> },
  ttlMs: 0,
  interruptible: false,
  ttsEligible: false,
  historyEligible: true,
  copyExportEligible: true,
  reason: "chat_reply_rendered",
}
```

`payload` contains only `source`, `mood`, and `replyLength`. Reply text is never
stored. `payload.source` is validated against `CHAT_REPLY_SAFE_SOURCE_ALLOWLIST`
(`llm_local`, `llm_real`, `llm_local_error`, `llm_real_error`, `unknown`); unknown
values fall back to `"unknown"`. `payload.mood` is validated against
`CHARACTER_MOOD_STATE_ALLOWLIST`; unknown values fall back to `"neutral"`.
`payload.replyLength` is clamped 0–10000. Non-string `reply` returns `null` (no-op).
Network errors and non-200 responses never reach the call site.

After a full successful `sendChat`, the queue holds three items:
expression_mirror (index 0, from TASK-231), reaction_bubble (index 1, from TASK-230),
and chat_reply (index 2, from TASK-232). Since `nextItem` = `outputQueueItems[0]`:

```
Queue: disabled · Items: 3 · Recent: 3 · Next: P4_NORMAL_REACTION/visual_expression/expression_mirror
```

TASK-232 preserves the TASK-218 and TASK-220 narrow IPC channels and all prior
behavior. It does not add IPC, dispatch, Pet Window runtime behavior, Pet Bubble
visible behavior, expression mirror behavior, reaction bubble mirror behavior,
TASK-219 debounce changes, extra `/chat` calls, extra history writes, TTS/STT/audio,
prompt runtime, persistence, assets, hover action buttons, or message edit scope
changes.

Windows visual smoke PASS confirmed on 2026-06-01:

- Basic startup PASS: Preview shows `Queue: disabled · Items/Recent/Next`; Pet
  Window remains normal.
- Send message PASS: formal chat reply renders normally, Queue enqueues the
  `chat_reply` diagnostics item; Queue does not display reply text, user text,
  raw response, prompt, or memory raw content.
- Edit last user PASS: edited reply renders normally, Queue enqueues the
  `chat_reply` diagnostics item; no extra `/chat` call.
- Delete / Undo PASS: feature remains normal; Queue stays disabled.
- Clear Chat PASS: feature remains normal; Queue stays disabled.
- Focus PASS: feature remains normal; Queue stays disabled.
- Queue diagnostics format PASS: no `undefined`, `null`, `NaN`,
  `[object Object]`, raw JSON, user text, reply text, bubble text, or payload.
- General regression PASS: no new IPC side effect, no extra TTS, no extra
  `/chat`, no history/copy/export pollution, and Pet Window expression plus
  reaction bubble behavior remains normal.

The output queue can now record expression mirror intent (TASK-231), reaction bubble
intent (TASK-230), and chat reply intent (TASK-232) as local diagnostics, but it
still does not control execution.

---

## 21. TASK-233 Output Queue Runtime Checkpoint

TASK-233 is a docs-only checkpoint for the TASK-226 through TASK-232 output queue
work. It adds `docs/OUTPUT_QUEUE_RUNTIME_CHECKPOINT.md`, which consolidates the
current state of the disabled diagnostics ledger into a single reference.

As of TASK-232, the queue is a **disabled diagnostics ledger**:

- Three sources enqueue items: `expression_mirror`, `reaction_bubble`, `chat_reply`.
- All existing execution paths (TASK-218/219, TASK-220, original chat flow) remain
  unchanged — the queue is a passive parallel observer.
- `OUTPUT_QUEUE_ENABLED = false`. No dispatch, no IPC, no TTS, no Pet Window send,
  no extra `/chat`, no history write, no raw text storage.

The checkpoint doc defines a dispatch readiness checklist (12 items) that must be
satisfied before `OUTPUT_QUEUE_ENABLED` can be set to `true`, and recommends
TASK-234 through TASK-239 as the next incremental steps.

See [`docs/OUTPUT_QUEUE_RUNTIME_CHECKPOINT.md`](OUTPUT_QUEUE_RUNTIME_CHECKPOINT.md)
for the full checkpoint.

## 22. TASK-234 Output Queue Priority Winner Preview

**Status: DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-06-01)**

TASK-234 builds the Output Queue Priority Winner Preview. Full App renderer-only.

`getOutputQueuePriorityWinner(items)` — a pure helper that scans `outputQueueItems`
and returns the highest-priority item summary, using `compareOutputPriority` for
ordering (ties broken by earlier queue index). The result is sanitized via
`cloneOutputQueueNextItemSummary` (no payload).

`getOutputQueueSnapshot()` and `updateOutputQueueSnapshot()` now include
`winnerItem` (sanitized summary or null).

`formatOutputQueueSnapshotPreview()` now appends `· Winner: P/C/S` (or
`· Winner: none`), completing the preview format:

```
Queue: disabled · Items: N · Recent: N · Next: P/C/S · Winner: P/C/S
```

**Key distinction:**
- `Next` = `outputQueueItems[0]` (queue-order first item).
- `Winner` = highest-priority item across all items.

After `sendChat`, the queue holds three items in enqueue order:
`expression_mirror` [0] → `reaction_bubble` [1] → `chat_reply` [2].
- Next: `P4_NORMAL_REACTION/visual_expression/expression_mirror`
- Winner: `P2_LLM_REPLY/full_app_chat/chat_reply`

**Winner is diagnostics-only.** It does not dispatch, does not change queue order,
does not change Next, does not control expression mirror / reaction bubble / chat
reply, does not send to Pet Window, does not add IPC, does not call `/chat`, does
not trigger TTS/STT/audio, does not write history, does not enter copy/export, and
does not store raw user text / reply text / bubble text / payload.

`OUTPUT_QUEUE_ENABLED` remains false. 19 new smoke tests plus 8 updated existing
tests. All 3 smoke scripts PASS. Windows visual smoke PASS: startup / send /
Winner boundary / Delete / Undo / Edit last user / Clear Chat / Focus / diagnostics
format / general regression all confirmed.

## 23. TASK-235 Active Output Item Model, Disabled

**Status: DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-06-01, manual console helper SKIP — covered by automated smoke)**

TASK-235 adds the Active Output Item Model. Full App renderer-only. Diagnostics-only
disabled model for representing the item "currently being output."

New state: `currentActiveOutputItem = null`.

New helpers:

- `cloneOutputQueueActiveItemSummary(item)` — fields: `source / priority / channel /
  reason / ttlMs` only. No payload, no id. Invalid item returns null.
- `getActiveOutputItemSnapshot()` — returns sanitized summary or null.
- `setActiveOutputItemForDiagnosticsOnly(item)` — sanitizes item, sets
  `currentActiveOutputItem`. Invalid input → null. Updates snapshot. No dispatch,
  no IPC, no TTS, no history.
- `clearActiveOutputItem()` — clears `currentActiveOutputItem`, updates snapshot.

`getOutputQueueSnapshot()` and `updateOutputQueueSnapshot()` now include
`activeItem` (sanitized summary or null).

`formatOutputQueueSnapshotPreview()` now appends `· Active: P/C/S` (or
`· Active: none`), completing the preview format:

```
Queue: disabled · Items: N · Recent: N · Next: P/C/S · Winner: P/C/S · Active: P/C/S
```

**Active is diagnostics-only.** It is never set automatically by `sendChat`.
It does not dispatch, does not change queue order/Next/Winner, does not control
expression mirror / reaction bubble / chat reply, does not send to Pet Window,
does not add IPC, does not call `/chat`, does not trigger TTS/STT/audio, does not
write history, does not enter copy/export, and does not store raw text.

`OUTPUT_QUEUE_ENABLED` remains false. 19 new smoke tests plus 9 updated existing
tests. All 3 smoke scripts PASS.

## 24. TASK-236 Collapsible Diagnostics Drawer

**Status: DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-06-01)**

TASK-236 changes the Full App diagnostics preview UI only. The queue model,
snapshot fields, item schemas, priority winner, and active item behavior remain
unchanged.

The normal UI now shows a single-line safe summary:

```
Reaction: <hint> · Suggestion: <expression> · Queue disabled · Items <n>
```

The full diagnostics are available only after the user clicks the Diagnostics
toggle:

```
Reaction: <hint> · Suggestion: <expression>
Decision: <action> · State: <mood>/<attention>/<energy> · Level: <level>
Queue: disabled · Items: <n> · Recent: <n> · Next: <P/C/S|none> · Winner: <P/C/S|none> · Active: <P/C/S|none>
```

TASK-236 behavior summary:

- Creates a Collapsible Diagnostics Drawer as Full App renderer-only UI cleanup.
- Diagnostics default to collapsed.
- The normal screen shows one safe summary line only.
- Clicking Diagnostics expands the full details.
- Details retain Reaction / Suggestion, Decision / State / Level, and Queue /
  Items / Recent / Next / Winner / Active.
- Clicking Diagnostics again collapses the details.
- No persistence, localStorage, settings page, or `innerHTML`.
- The drawer does not enter chat history or copy/export transcript.
- The drawer does not send to the Pet Window, does not add IPC, and does not
  change Pet Window runtime.
- The drawer does not change expression mirror, reaction bubble mirror, or chat
  reply flow.
- The drawer does not call extra `/chat` and does not trigger TTS/STT/audio.
- Queue remains disabled.
- The drawer does not dispatch and does not control any output.

New renderer helpers:

- `formatInteractionDiagnosticsSummary()`
- `formatInteractionDiagnosticsDetails()`
- `toggleInteractionDiagnosticsDrawer()`

New renderer state:

- `interactionDiagnosticsExpanded = false`

This is a local Full App renderer presentation change. It does not enable queue
dispatch, does not add IPC, does not call `/chat`, does not write history, does
not enter copy/export, does not send to the Pet Window, and does not control
expression mirror, reaction bubble, chat reply, TTS, STT, or audio.

The drawer uses `textContent`, `hidden`, `aria-expanded`, and `aria-controls`.
It does not use `innerHTML`, localStorage, persistence, fixed positioning, or an
overlay. Automated renderer smoke passes.

Windows visual smoke PASS (2026-06-01):

- Basic startup PASS: Diagnostics default collapsed, normal UI shows only one
  summary line, Pet Window normal.
- Expand Diagnostics PASS: clicking Diagnostics shows full Reaction / Decision /
  Queue / Next / Winner / Active.
- Collapse Diagnostics PASS: clicking again hides details and restores compact UI.
- Send message PASS: chat / expression / reaction bubble normal, summary/details
  update normally, Queue remains disabled.
- Delete / Undo PASS: context menu unaffected; drawer layout consistent with no
  observed UI abnormality.
- Edit last user PASS: function normal, Queue remains disabled, no extra `/chat`;
  drawer layout consistent with no observed UI abnormality.
- Clear Chat / Focus PASS: function normal; Pet Window expression and reaction
  bubble remain normal.
- Diagnostics format PASS: summary/details show no `undefined`, `null`, `NaN`,
  `[object Object]`, raw JSON, user text, reply text, bubble text, or payload.
- General regression PASS: no new IPC side effect, no extra TTS, no extra `/chat`,
  no history/copy/export pollution.
