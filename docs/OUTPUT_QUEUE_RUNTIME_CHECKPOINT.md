# Output Queue Runtime Checkpoint

**TASK-233 — docs-only architecture checkpoint**

---

## 1. Purpose

This document is the TASK-233 checkpoint for the Output Queue work completed
across TASK-226 through TASK-232. It records what the output queue runtime
currently is, what it is not, and what must happen before queue dispatch or
enforcement can be considered.

No runtime changes are made in this document or in TASK-233. The queue remains
a local diagnostics ledger. It observes and records output intent; it does not
control, dispatch, or execute output.

The primary goal of this checkpoint is to confirm:

- The queue is a **diagnostics ledger**, not a dispatcher.
- Every current enqueue is a passive record of what the existing runtime already
  decided to do — not a new decision or new execution.
- All execution still happens through the pre-existing paths (TASK-218/219 for
  expression mirror, TASK-220 for reaction bubble, the original chat flow for
  chat reply).

---

## 2. Completed Output Queue Task Chain

| Task | Description | Status |
|------|-------------|--------|
| TASK-226 | Interaction Output Queue / Priority Design | DONE — DOCS ONLY |
| TASK-228 | Output Queue Runtime Skeleton, Disabled by Default | DONE — WINDOWS VISUAL SMOKE PASS |
| TASK-229 | Output Queue Debug Preview / Snapshot Polish | DONE — WINDOWS VISUAL SMOKE PASS |
| TASK-230 | Enqueue Reaction Bubble Diagnostics Only | DONE — WINDOWS VISUAL SMOKE PASS |
| TASK-231 | Enqueue Expression Mirror Diagnostics Only | DONE — WINDOWS VISUAL SMOKE PASS |
| TASK-232 | Enqueue Chat Reply Diagnostics Only | DONE — WINDOWS VISUAL SMOKE PASS |

**TASK-226** defined the priority model (P0–P6), channel taxonomy, forbidden
payload rules, preemption rules, and recommended future tasks. No runtime was
added.

**TASK-228** added the disabled runtime skeleton in `renderer.js`:
`OUTPUT_QUEUE_ENABLED = false`, `outputQueueItems`, `recentOutputQueueItems`,
`currentOutputQueueSnapshot`, `enqueueOutputQueueItem`, `getOutputQueueSnapshot`,
`sanitizeOutputQueueItem`, `sanitizeOutputQueuePayload`, priority ordering
helpers, and preemption helper. Queue disabled — no dispatch.

**TASK-229** added `formatOutputQueueSnapshotPreview()` and polished the
diagnostics preview line inside the existing character-status preview element.
Format: `Queue: disabled · Items: <n> · Recent: <n> · Next: <priority>/<channel>/<source>`.

**TASK-230** added `enqueueReactionBubbleOutputDiagnostics(bubble)`, called from
`recordInteractionReactionBubble` before `mirrorInteractionReactionBubble`. This
records reaction bubble intent as a diagnostics item. Does not control the bubble.

**TASK-231** added `enqueueExpressionMirrorOutputDiagnostics(expression)`, called
from `recordInteractionExpressionSuggestion` before `mirrorInteractionExpressionSuggestion`.
This records expression mirror intent. Does not control the mirror.

**TASK-232** added `enqueueChatReplyOutputDiagnostics({ reply, mood, source })`,
called from both `/chat` success paths after the reply is rendered. This records
chat reply intent. Does not control the reply or history.

---

## 3. Current Runtime State

All queue state lives in `apps/desktop/src/renderer/renderer.js`.

| Symbol | Type | Value / Description |
|--------|------|---------------------|
| `OUTPUT_QUEUE_ENABLED` | `const boolean` | `false` — queue disabled |
| `OUTPUT_QUEUE_MAX` | `const number` | `50` — max items in queue |
| `OUTPUT_QUEUE_RECENT_MAX` | `const number` | `20` — max recent items |
| `outputQueueItems` | `var array` | Live queue — items accumulate, never dispatched |
| `recentOutputQueueItems` | `var array` | Rolling history of enqueued item summaries |
| `currentOutputQueueSnapshot` | `var object` | Latest snapshot (enabled, length, recentLength, nextItem) |
| `outputQueueIdCounter` | `var number` | Monotonic ID counter |
| `getOutputQueueSnapshot()` | `function` | Returns current snapshot with sanitized nextItem |
| `formatOutputQueueSnapshotPreview()` | `function` | Returns preview string for the diagnostics element |
| `enqueueOutputQueueItem(item)` | `function` | Validates, sanitizes, appends to queue, updates snapshot |
| `sanitizeOutputQueueItem(item)` | `function` | Strips forbidden fields, validates source/priority/channel |
| `sanitizeOutputQueuePayload(payload)` | `function` | Strips forbidden payload keys, validates each allowed key |
| `clearOutputQueue(reason)` | `function` | Empties queue, updates snapshot |

The diagnostics preview is rendered via `renderInteractionReactionPreview()` into
`#interaction-reaction-preview` using `textContent` (never `innerHTML`).

---

## 4. Current Diagnostics Item Sources

Three sources currently enqueue diagnostics items:

### A. expression_mirror

| Field | Value |
|-------|-------|
| `source` | `"expression_mirror"` |
| `priority` | `"P4_NORMAL_REACTION"` |
| `channel` | `"visual_expression"` |
| `payload` | `{ expression: "<safe expression>" }` |
| `ttlMs` | `0` |
| `interruptible` | `true` |
| `ttsEligible` | `false` |
| `historyEligible` | `false` |
| `copyExportEligible` | `false` |
| `reason` | `"interaction_expression_suggestion"` |

Safe expressions (allowlisted): `neutral`, `focused`, `happy`, `proud`,
`annoyed`, `sleepy`. Invalid expression → null (no-op). Record path sanitizes
unknown → `"neutral"` so record path always enqueues.

Does **not** store user text, bubble text, or raw event payload.
Does **not** control the expression mirror — TASK-218/219 IPC still runs unchanged.

### B. reaction_bubble

| Field | Value |
|-------|-------|
| `source` | `"reaction_bubble"` |
| `priority` | `"P4_NORMAL_REACTION"` |
| `channel` | `"pet_bubble"` |
| `payload` | `{ bubbleId: "<safe bubble id>" }` |
| `ttlMs` | `3000` |
| `interruptible` | `true` |
| `ttsEligible` | `false` |
| `historyEligible` | `false` |
| `copyExportEligible` | `false` |
| `reason` | `"interaction_reaction_bubble"` |

`none`, empty, or invalid bubble ids do not enqueue (no-op).

Does **not** store bubble text, user text, or raw event payload.
Does **not** control the Pet Bubble — TASK-220 IPC still runs unchanged.

### C. chat_reply

| Field | Value |
|-------|-------|
| `source` | `"chat_reply"` |
| `priority` | `"P2_LLM_REPLY"` |
| `channel` | `"full_app_chat"` |
| `payload` | `{ source: "<safe source>", mood: "<safe mood>", replyLength: <number> }` |
| `ttlMs` | `0` |
| `interruptible` | `false` |
| `ttsEligible` | `false` |
| `historyEligible` | `true` |
| `copyExportEligible` | `true` |
| `reason` | `"chat_reply_rendered"` |

`payload.source` validated against `CHAT_REPLY_SAFE_SOURCE_ALLOWLIST`
(`llm_local`, `llm_real`, `llm_local_error`, `llm_real_error`, `unknown`);
fallback `"unknown"`. `payload.mood` validated against `CHARACTER_MOOD_STATE_ALLOWLIST`;
fallback `"neutral"`. `payload.replyLength` clamped 0–10000. Non-string `reply`
returns null (no-op).

Does **not** store reply text, user text, raw response, prompt, or memory raw content.
Does **not** control the chat reply — the original render path runs unchanged.

Note: `historyEligible: true` and `copyExportEligible: true` are intent flags only.
The queue is disabled and does not execute history writes or copy/export operations.
These flags represent what would be appropriate if the queue were ever dispatched,
not a current behavior.

---

## 5. Current Queue Preview Behavior

The preview string is produced by `formatOutputQueueSnapshotPreview()` and
embedded in the full diagnostics preview via `formatInteractionDiagnosticsPreview()`.
It is rendered into `#interaction-reaction-preview` with `textContent`.

Possible preview states:

```
Queue: disabled · Items: 0 · Recent: 0 · Next: none
Queue: disabled · Items: 1 · Recent: 1 · Next: P4_NORMAL_REACTION/visual_expression/expression_mirror
Queue: disabled · Items: 2 · Recent: 2 · Next: P4_NORMAL_REACTION/visual_expression/expression_mirror
Queue: disabled · Items: 3 · Recent: 3 · Next: P4_NORMAL_REACTION/visual_expression/expression_mirror
```

**Important:** `Next` displays `outputQueueItems[0]` — the first item inserted,
not the highest-priority item. It is a queue-order summary, not a priority winner.

After a full `chat_message_sent` + `/chat` response cycle, the typical insertion
order is:

1. `expression_mirror` (enqueued when `recordInteractionEvent` is called, before fetch)
2. `reaction_bubble` (enqueued in the same synchronous reaction hint path)
3. `chat_reply` (enqueued after fetch response is rendered)

Because `expression_mirror` arrives first, `Next` shows
`P4_NORMAL_REACTION/visual_expression/expression_mirror` even though
`chat_reply` has higher priority `P2_LLM_REPLY`. Priority winner selection is
not yet implemented.

---

## 6. Safety Boundary

The following properties are **permanently true** while `OUTPUT_QUEUE_ENABLED = false`,
and must remain true under explicit verification before any dispatch is enabled:

| Property | Status |
|----------|--------|
| Queue does not dispatch | ✓ |
| Queue does not control execution | ✓ |
| Queue does not send to Pet Window | ✓ |
| Queue does not add IPC channels | ✓ |
| Queue does not call `/chat` | ✓ |
| Queue does not trigger TTS/STT/audio | ✓ |
| Queue does not write history | ✓ |
| Queue does not write copy/export transcript | ✓ |
| Queue does not store raw user message | ✓ |
| Queue does not store reply text | ✓ |
| Queue does not store bubble text | ✓ |
| Queue does not store raw response | ✓ |
| Queue does not store prompt | ✓ |
| Queue does not store memory raw content | ✓ |
| Queue does not store debug / metadata / thinking | ✓ |
| Queue does not do background monitoring | ✓ |
| Queue does not do screenshot / OCR | ✓ |
| Queue does not do always-listening | ✓ |

---

## 7. Sanitization Summary

All items pass through `sanitizeOutputQueueItem` before entering the queue.
All payload values pass through `sanitizeOutputQueuePayload`.

**`OUTPUT_SAFE_PAYLOAD_KEYS`** (allowlist — only these keys survive):
`expression`, `bubbleId`, `state`, `action`, `reason`, `source`, `mood`,
`replyLength`.

**`OUTPUT_FORBIDDEN_KEYS`** (always stripped regardless of source):
`message`, `text`, `body`, `rawText`, `content`, `reply`, `transcript`,
`audio`, `html`, `innerHTML`, `metadata`, `debug`, `thinking`.

Each surviving payload key is validated against its own allowlist:

| Key | Validation |
|-----|-----------|
| `expression` | `INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST` |
| `bubbleId` | `INTERACTION_REACTION_BUBBLE_ALLOWLIST` |
| `action` | `COMPANION_BEHAVIOR_ACTION_ALLOWLIST` |
| `state` | per-field: mood / attention / energy / recentInteractionLevel allowlists |
| `reason` | `sanitizeOutputQueueReason` (alphanumeric + `_:/.-`, max 80 chars) |
| `source` | `CHAT_REPLY_SAFE_SOURCE_ALLOWLIST` |
| `mood` | `CHARACTER_MOOD_STATE_ALLOWLIST` |
| `replyLength` | `Math.max(0, Math.min(10000, Math.floor(value)))` |

**Default eligibility flags** (unless explicitly set):
- `ttsEligible` defaults `false`
- `historyEligible` defaults `false` (except `chat_reply` sets `true` as intent flag)
- `copyExportEligible` defaults `false` (except `chat_reply` sets `true` as intent flag)

These flags are intent annotations only. The queue is disabled; no TTS is
triggered, no history is written, and no copy/export is performed.

The preview renders only a sanitized summary line (enabled/disabled, item counts,
next item priority/channel/source). It does not render payload values, item ids,
raw JSON, or any user-generated text.

---

## 8. Relationship to Existing Runtime

The output queue runs **in parallel** with the existing execution paths and does
not replace or alter them:

| Execution path | Current owner | Queue role |
|----------------|---------------|------------|
| Expression mirror IPC | TASK-218/219 (`scheduleInteractionExpressionMirror`, `dragonPet.sendPetExpressionSuggestion`) | Records intent only via `enqueueExpressionMirrorOutputDiagnostics` |
| Reaction bubble IPC | TASK-220 (`mirrorInteractionReactionBubble`, `dragonPet.sendPetReactionBubble`) | Records intent only via `enqueueReactionBubbleOutputDiagnostics` |
| Chat reply render | Original `sendMessage` / `submitEditedUserMessage` flows | Records intent only via `enqueueChatReplyOutputDiagnostics` |
| Chat history write | `chatHistoryAppend` IPC | Not touched by queue |
| Pet Window speech | `dragonPet.updatePetSpeech` IPC | Not touched by queue |
| TTS/STT/audio | Not yet implemented | Queue has no role |

The queue enqueue calls are inserted immediately **before** or **after** the
existing execution calls, as passive observers. They do not gate or modify the
existing behavior.

---

## 9. What Is Not Implemented Yet

The following capabilities are **explicitly absent** from the current queue
runtime and must not be inferred from the disabled skeleton:

- Output dispatch (queue drain loop, item consumption)
- Priority winner selection algorithm
- Preemption runtime enforcement (active item replacement)
- Active item state (`currentOutputItem` or equivalent)
- TTL expiration / cleanup runtime
- Stop / cancel / skip output controls
- Queue-enabled flag with user or developer control surface
- Pet Window handler for receiving dispatched queue items
- IPC channel for queue items
- Queue item persistence
- TTS-safe speech segment runtime
- Idle reaction dispatch
- Notification dispatch
- Settings UI for output verbosity / frequency
- Background monitoring integration
- Screen context integration with queue

---

## 10. Dispatch Readiness Checklist

Before `OUTPUT_QUEUE_ENABLED` is set to `true` in any code path or feature flag,
all of the following must be explicitly reviewed and confirmed:

- [ ] `OUTPUT_QUEUE_ENABLED` control surface defined (dev flag, user setting, or
      guarded by feature flag)
- [ ] Active output item model defined (`currentOutputItem` or equivalent)
- [ ] Priority winner selector implemented and smoke-tested
- [ ] Preemption enforcement logic implemented and smoke-tested
- [ ] TTL expiration / cleanup loop implemented
- [ ] Stop / cancel / skip controls defined and tested
- [ ] Strict IPC boundary review: any new channel must be narrow and named
- [ ] Pet Window handler design: what does a dispatched item do in the Pet Window?
- [ ] History / copy / export boundary tests: `historyEligible`/`copyExportEligible`
      flags do not silently promote content into transcripts
- [ ] TTS integration: must remain `false` by default; TTS path must be separate
      feature gate
- [ ] Windows visual smoke checklist updated to include queue dispatch behavior
- [ ] No raw user text, reply text, bubble text, prompt, or memory content leaks
      through any new dispatch path

---

## 11. Recommended Next Tasks

| Task | Description | Type |
|------|-------------|------|
| TASK-234 | Output Queue Priority Winner Preview, diagnostics only | runtime (renderer-only, disabled) — **DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-06-01)**. Winner preview is diagnostics-only: does not dispatch, does not change queue order or Next, does not control any output channel. |
| TASK-235 | Active Output Item Model, disabled | runtime (renderer-only, disabled) |
| TASK-236 | Bubble Priority Enforcement, guarded and disabled by default | runtime (renderer-only, guarded) |
| TASK-237 | TTS-safe Segment Design, docs-only or helper-only | docs or helper-only |
| TASK-238 | User Controls for Companion Verbosity | runtime (settings UI) |
| TASK-239 | Idle Reaction Policy, fixed only, no LLM | runtime (renderer-only, guarded) |

Each task should remain narrow and testable with explicit side-effect boundaries
and Windows visual smoke before any dispatch-related change is considered
production-ready.

---

## 12. Relationship to Existing Docs

| Document | Relationship |
|----------|-------------|
| [docs/INTERACTION_OUTPUT_QUEUE_DESIGN.md](INTERACTION_OUTPUT_QUEUE_DESIGN.md) | Original TASK-226 priority design and TASK-228 through TASK-232 implementation notes. This checkpoint doc summarizes the current runtime state that the design doc describes. |
| [docs/INTERACTIVE_COMPANION_ARCHITECTURE.md](INTERACTIVE_COMPANION_ARCHITECTURE.md) | TASK-222/224 architecture checkpoint. The output queue is the parallel diagnostics ledger referenced in Section 12 ("What Is Not Implemented Yet") of that doc. |
| [docs/VOICE_TTS_RESEARCH.md](VOICE_TTS_RESEARCH.md) | TTS/STT research note. TTS integration is listed as not yet implemented above (Section 9). The queue will need a `ttsEligible` dispatch path before TTS can be considered. |
| [docs/CHRISTINA_PERSONA_CONTEXT_PACK.md](CHRISTINA_PERSONA_CONTEXT_PACK.md) | Persona context for Dragon Pet AI. Future idle reaction dispatch (TASK-239) must respect persona reaction rules and frequency guidelines defined there. |
