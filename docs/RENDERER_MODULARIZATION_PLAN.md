# Renderer Modularization Plan / Boundary Map

**Task:** TASK-237
**Status:** IMPLEMENTED - DOCS CHECKPOINT / NO WINDOWS SMOKE REQUIRED
**Date:** 2026-06-02

This document is a docs-only architecture checkpoint. It defines a renderer
module boundary map before any runtime extraction begins.

No runtime code changed for TASK-237. No renderer extraction was performed.

## 1. Purpose

TASK-237 records the planned modularization boundary for the Full App renderer.
The current `apps/desktop/src/renderer/renderer.js` file owns many unrelated
responsibilities after TASK-214 through TASK-236, including chat flows,
interaction diagnostics, companion behavior previews, output queue diagnostics,
settings, context menu behavior, and Pet Window bridge calls.

This checkpoint does not extract modules. It gives the next implementation tasks
a stable map so extraction can proceed in narrow steps without changing runtime
behavior.

## 2. Current Renderer Responsibility Map

The current renderer file owns the following responsibilities:

| Responsibility | Current owner | Notes |
|---|---|---|
| Boot / DOM lookup / event wiring | `renderer.js` | Startup, DOM refs, button/input listeners, initial state wiring. |
| Chat submit / `/chat` request flow | `renderer.js` | Sends user text to backend `/chat` and handles response. |
| Chat rendering | `renderer.js` | Renders user and pet messages in the Full App chat area. |
| Chat history / copy / export | `renderer.js` | Keeps transcript behavior and export/copy boundaries. |
| Edit / delete / undo / clear chat | `renderer.js` | Message management and undo flows. |
| Search / Ctrl+F | `renderer.js` | Chat search UI and keyboard behavior. |
| Context menu | `renderer.js` | Right-click actions such as copy, edit, delete, and restore. |
| Pet Window bridge | `renderer.js` | Show Pet / Full App bridge calls and narrow Pet update entry points. |
| Expression mirror | `renderer.js` | Sends sanitized expression suggestions to Pet Window. |
| Reaction bubble mirror | `renderer.js` | Sends safe reaction bubble ids to Pet Window. |
| Interaction event recorder | `renderer.js` | Records local interaction events and derives hints. |
| Companion behavior decision | `renderer.js` | Local decision preview for behavior policy. |
| Character state layer | `renderer.js` | Attention / energy / mood diagnostics preview. |
| Output queue diagnostics ledger | `renderer.js` | Disabled queue item sanitize, enqueue, snapshot, Next/Winner/Active diagnostics. |
| Diagnostics drawer | `renderer.js` | Collapsed summary and expanded details UI. |
| Settings / provider UI | `renderer.js` | Provider/model/settings controls. |
| Memory UI | `renderer.js` | Memory panel behavior where present. |
| Voice / STT / TTS placeholder UI | `renderer.js` | Existing UI shell only where present; no TASK-237 runtime work. |

## 3. Proposed Module Boundary Map

| Module | Owns | Should not own | Dependencies |
|---|---|---|---|
| `renderer-core.js` | Bootstrapping, DOM ready, high-level orchestration only. | Feature logic, direct queue internals, direct Pet Window formatting. | All controllers and modules through narrow imports. |
| `dom-refs.js` | DOM lookup and safe element references. | Event behavior, rendering decisions, network calls. | Browser DOM only. |
| `chat-api-client.js` | `/chat` request wrapper only. | Rendering, history writes, Pet Window calls, diagnostics formatting. | Backend API endpoint and request schema. |
| `chat-rendering.js` | Rendering user / pet messages and formal chat entries. | `/chat` calls, history persistence, queue dispatch, Pet bridge calls. | DOM refs, message formatting helpers. |
| `chat-history.js` | History state, transcript copy/export, undo clear state. | DOM context menu logic, `/chat` calls, Pet Window calls. | Storage/history IPC as already used. |
| `chat-actions.js` | Send, edit, delete, undo, clear command orchestration. | Low-level DOM lookup, direct provider settings, direct Pet Window payload formatting. | Chat API, chat rendering, chat history, diagnostics hooks. |
| `search-controller.js` | Search and Ctrl+F UI logic. | Message rendering, history writes, queue logic. | DOM refs and chat rendering state. |
| `context-menu-controller.js` | Right-click menu, copy/delete/edit actions. | `/chat` calls except through chat actions, Pet Window calls. | DOM refs, chat actions, chat history. |
| `pet-bridge.js` | Show Pet / Full App / narrow bridge calls. | Chat rendering, history writes, queue dispatch logic. | Existing `window.dragonPet` APIs only. |
| `interaction-events.js` | Local interaction event recording and hint derivation. | Pet Window IPC, `/chat`, history writes. | Local state only. |
| `companion-behavior.js` | Behavior decision mapping. | Executing actions, dispatching queue items, Pet Window IPC. | Interaction events and character state inputs. |
| `character-state.js` | Attention / energy / mood local state preview. | Chat rendering, queue dispatch, Pet Window IPC. | Interaction event summaries. |
| `output-queue.js` | Output queue item sanitize, enqueue, snapshot, Next/Winner/Active diagnostics. | Dispatch, Pet Window sending, TTS/STT/audio, history/copy/export writes. | Local diagnostics state and allowlists. |
| `diagnostics-drawer.js` | Collapsible diagnostics summary/details UI and toggle state. | Queue logic, chat history, Pet Window messages, dispatch. | Safe snapshots from interaction, behavior, character state, and output queue. |
| `settings-panel.js` | Provider/model/settings UI. | Chat rendering, diagnostics drawer, Pet bridge internals. | Existing settings API/IPC surfaces only. |
| `memory-panel.js` | Memory UI. | `/chat` response schema, Pet Window bridge, queue dispatch. | Existing memory data surface only. |
| `voice-controls.js` | Existing voice / STT / TTS UI shell only. | New TTS/STT runtime, queue dispatch, `/chat` calls. | Existing UI state only. |

## 4. First Extraction Recommendation

Recommended next implementation task:

**TASK-238 - Extract Output Queue Module**

Reason:

- Output queue logic is already diagnostics-only.
- Runtime side effects are intentionally minimal.
- The helper set is testable as pure or near-pure state helpers.
- The current queue state is isolated from Pet Window, IPC, backend, TTS, and
  chat history behavior.
- Existing smoke tests already cover queue safety, sanitization, snapshots,
  disabled state, and no side effects.

TASK-238 should extract queue helpers without enabling dispatch and without
changing visible behavior.

## 5. Suggested Extraction Order

1. TASK-238 Extract Output Queue Module. **DONE — WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-06-02, Windows visual smoke 2026-06-01).**
2. TASK-239 Extract Diagnostics Drawer Module. **DONE — WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-06-02, Windows visual smoke 2026-06-01).**
3. TASK-240 Christina Desktop Pet Cutout Stage Foundation. **DONE — WINDOWS VISUAL SMOKE PASS / DONE - PASS (2026-06-02).** Pure Pet Window CSS polish: transparent cutout shell, avatar-bound stage pad/glow, avatar-container as primary drag zone, close X permanently hidden, compact hover dock controls, no runtime behavior change.
4. TASK-241 Extract Pet Bridge Module.
5. TASK-242 Extract Chat Rendering Module.
6. TASK-243 Extract Chat History / Copy / Export Module.
7. TASK-244 Extract Context Menu / Search Modules.
8. TASK-245 Renderer Core Cleanup.

## 6. Module Contract Rules

Every extraction should follow these rules:

- No broad global mutation unless the module explicitly owns that state.
- No direct Pet Window calls outside `pet-bridge.js`.
- No `/chat` calls outside `chat-api-client.js`.
- No history writes outside `chat-history.js`.
- No output queue dispatch until an explicit guarded task enables it.
- No TTS/STT side effects from diagnostics modules.
- No `innerHTML` for user-controlled content.
- No raw user text, reply text, bubble text, raw JSON, or payload values inside
  diagnostics queue UI.
- No new IPC unless separately reviewed.
- Every extraction must preserve existing smoke tests.
- Every runtime extraction requires Windows visual smoke before final DONE state.

## 7. Output Queue Extraction Sketch

TASK-238 should create:

`apps/desktop/src/renderer/modules/output-queue.js`

Expected shape:

- Export pure helpers and state accessors where practical.
- Keep `OUTPUT_QUEUE_ENABLED = false`.
- Keep diagnostics-only enqueue and snapshot behavior.
- Keep no dispatch.
- Keep no IPC.
- Keep no Pet Window side effects.
- Keep no history/copy/export writes.
- Keep queue payload sanitization and allowlists intact.
- Keep tests passing unchanged or with minimal import-oriented updates.
- Preserve current visible behavior.

## 8. Diagnostics Drawer Extraction Sketch

TASK-239 should create a diagnostics drawer module.

Expected ownership:

- Summary formatting.
- Details formatting.
- Toggle state.
- DOM update for the drawer.

Inputs:

- Safe reaction / behavior / character snapshots.
- Safe output queue snapshot.

Non-ownership:

- Does not own queue logic.
- Does not own chat history.
- Does not send Pet Window messages.
- Does not dispatch.
- Does not persist state by default.

## 9. Risk Register

| Risk | Mitigation |
|---|---|
| Module extraction may break globals expected by smoke tests. | Extract one module at a time and update tests only for module access, not behavior. |
| DOM timing / initialization order regressions. | Keep `renderer-core.js` as the only startup coordinator and preserve DOM-ready order. |
| Circular dependencies between chat, diagnostics, and queue modules. | Prefer one-way data flow: actions call helpers, diagnostics consumes snapshots. |
| Copy/export/history behavior changes accidentally. | Keep transcript ownership in `chat-history.js` and retain smoke coverage. |
| Pet Window mirror behavior changes accidentally. | Move bridge calls behind `pet-bridge.js` and keep narrow IPC tests. |
| ESM/CommonJS/Electron renderer compatibility. | Use the existing renderer loading pattern until a separate bundling task exists. |
| Windows path / line ending issues. | Run `git diff --check` and Windows smoke after runtime extractions. |

## 10. Smoke / Validation Strategy

For runtime extraction tasks, run:

```powershell
node apps\desktop\scripts\renderer-chat-smoke.js
node apps\desktop\scripts\pet-window-smoke.js
node apps\desktop\scripts\pet-renderer-smoke.js
git diff --check
```

Windows visual smoke is required when runtime behavior is touched.

For TASK-237 itself, no Windows visual smoke is required because it is docs-only.

## 11. Explicit Non-Goals

TASK-237 does not implement:

- Runtime extraction.
- Output queue dispatch.
- Priority enforcement.
- TTS/STT implementation.
- Pet Window refactor.
- Backend refactor.
- `/chat` schema change.
- IPC change.
- UI redesign beyond docs.
- Prompt/runtime persona changes.
- Provider/Ollama runtime changes.
- Asset changes.

TASK-237 also does not modify `renderer.js`, `index.html`, `styles.css`, smoke
tests, main/preload/Pet Window code, backend code, chat history persistence,
prompt runtime, TTS/STT/audio runtime, or any IPC channel.

## 12. Relationship to Existing Docs

| Document | Relationship |
|---|---|
| [docs/INTERACTIVE_COMPANION_ARCHITECTURE.md](INTERACTIVE_COMPANION_ARCHITECTURE.md) | Records the broader companion architecture. TASK-237 adds the renderer modularization phase as a docs-only map before extraction. |
| [docs/INTERACTION_OUTPUT_QUEUE_DESIGN.md](INTERACTION_OUTPUT_QUEUE_DESIGN.md) | Defines the output queue priority model. TASK-237 recommends extracting that diagnostics ledger first in TASK-238. |
| [docs/OUTPUT_QUEUE_RUNTIME_CHECKPOINT.md](OUTPUT_QUEUE_RUNTIME_CHECKPOINT.md) | Records current queue runtime state. TASK-237 uses it as the source for the output queue module boundary. |
| [docs/VOICE_TTS_RESEARCH.md](VOICE_TTS_RESEARCH.md) | Voice/TTS remains a future integration layer. TASK-237 does not add voice runtime. |
| [docs/CHRISTINA_PERSONA_CONTEXT_PACK.md](CHRISTINA_PERSONA_CONTEXT_PACK.md) | Persona content remains a content-layer input only. TASK-237 does not change prompt/runtime persona behavior. |
