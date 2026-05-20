# Phase 4 Plan

> dragon-pet-ai
> Phase: 4 — LLM Adapter Integration (Proposed)
> Status: PLANNING
> Last Updated: 2026-05-19
> Owner: TASK-030

---

## Current Phase 3 Baseline

Phase 3 is complete. The following capabilities are stable and smoke-tested:

| Capability | Status |
|---|---|
| Mock chat (casual / debug / support / project / reminder modes) | ✅ Done |
| Conversation history (SQLite) | ✅ Done |
| Character state + relationship state | ✅ Done |
| Manual Memory API (POST / GET / DELETE /memory) | ✅ Done |
| Memory Management UI | ✅ Done |
| Approved memory context builder (type allowlist, safety filters, caps) | ✅ Done |
| Memory-aware chat two-layer gate (`MEMORY_INJECTION_ENABLED` + `use_memory`) | ✅ Done |
| MemoryInjectionAudit model + audit row creation | ✅ Done |
| Audit Inspection API (`GET /memory/audit`, read-only, paginated) | ✅ Done |
| Audit Logs UI (safe metadata cards) | ✅ Done |
| pytest: 226 passed | ✅ Done |
| Runtime smoke checks passed | ✅ Done |
| docs/PHASE3_DEMO_SUMMARY.md | ✅ Done |

**Current limitation:** `/chat` still returns mock-only replies. Approved memory context is built and audited but not yet passed to a real language model. The system is fully local and requires no external API calls.

---

## Candidate Tracks

### Option A — LLM Adapter Integration (Recommended)

**What it is:**
Build a provider abstraction layer that allows `/chat` to route reply generation through either the existing mock provider or a real LLM provider, controlled by a new `LLM_PROVIDER` feature flag. The mock provider remains the default. The real provider is disabled unless explicitly configured.

**How it fits:**
The memory-aware chat path already builds and audits approved memory context. Wiring that context to a real LLM is the next logical step and delivers the highest user-facing value from Phase 3 investment.

**Approach:**
- Define a `LLMProvider` abstract interface (e.g. `complete(prompt: str) -> str`)
- Implement `MockLLMProvider` (wraps existing mock reply logic)
- Implement `RealLLMProvider` (calls configured external API) — only in TASK-035+
- `chat_service` calls `get_llm_provider()` rather than `generate_mock_chat_reply()` directly
- API key comes from environment variable only (`LLM_API_KEY`); never hardcoded, never logged, never sent to frontend
- `/chat` response schema remains `reply / mood / source` — unchanged
- Memory-aware context continues to be controlled by the existing two-layer gate

**Risks and mitigations:**

| Risk | Mitigation |
|---|---|
| API key exposure | Key loaded from env var only; never returned in any response; never logged |
| Prompt injection via memory | Approved memory context already uses delimiters and a reference-only safety instruction (implemented in TASK-018) |
| Unexpected LLM output | Output validated for basic structure before returning; mock fallback available |
| Cost / rate limits | Mock provider remains default; real provider requires explicit opt-in |
| Latency | Real provider is async; timeout and fallback to error response if exceeded |
| Output correctness | Mock tests verify response schema; new integration tests added per provider |

---

### Option B — TTS Voice Output

**What it is:**
Add text-to-speech so the pet speaks each reply aloud after displaying it in the chat UI.

**Approach:**
- Integrate a TTS library (e.g. `pyttsx3` for local, `edge-tts` for higher quality) in the backend or renderer
- Desktop plays audio when a reply is received
- Toggle to mute/unmute in UI

**Risks:**

| Risk | Mitigation |
|---|---|
| Dependency complexity | Choose a well-maintained, offline-capable library |
| Latency added to reply display | Play audio asynchronously; do not block chat UI |
| Voice quality | Acceptable for MVP; can be upgraded later |
| Platform differences (Windows / macOS / Linux) | Test on all target platforms before shipping |

**Why deferred:**
TTS adds complexity and a new dependency without advancing the AI capability or memory system. It is better done after the chat engine is real, so the voice can speak meaningful LLM responses rather than mock strings.

---

### Option C — UI Polish and Packaging

**What it is:**
Improve visual layout (spacing, scrolling, memory section polish), add proper window controls, and package the app as a distributable installer (Electron Builder).

**Approach:**
- Fix known layout issues in Memory section and Audit Logs section
- Add proper overflow/scrolling behavior
- Run `electron-builder` to produce a Windows `.exe` and macOS `.dmg`
- Add auto-update placeholder (no real backend required)

**Risks:**

| Risk | Mitigation |
|---|---|
| Engineering effort diluted | Scope to a fixed list of layout issues; do not redesign from scratch |
| Packaging edge cases | Test on clean machines before declaring done |
| No AI value delivered | Accepted trade-off; this track is pure polish |

**Why deferred:**
UI polish has positive user-facing value but does not advance the core AI capabilities. Better done after the LLM adapter is wired, so the packaging captures a meaningful feature set.

---

### Option D — Daily Summary / Memory Review Workflow

**What it is:**
At end of session (or on demand), generate a plain-text summary of the day's conversation and allow the user to review and approve memory writes from it.

**Approach:**
- `GET /summary` or `POST /summary/generate` triggers summarization
- Summarization could be rule-based (MVP) or LLM-based (requires Option A first)
- User reviews proposed memory writes before they are committed
- Approved items written to Memory table with `source: daily_summary`

**Risks:**

| Risk | Mitigation |
|---|---|
| Touches automatic memory extraction boundary | Require explicit user approval before any write; no silent extraction |
| Requires LLM for quality summaries | Rule-based MVP first; LLM upgrade after Option A |
| Safety boundary more complex | Additional safety design step required before implementation |

**Why deferred:**
Daily summary requires either a rule-based or LLM-based summarizer. Option A (LLM adapter) is a prerequisite for the LLM path. Do Option A first, then revisit Option D.

---

## Recommendation

**Primary Phase 4 path: Option A — LLM Adapter Integration**

### Rationale

1. Phase 3 built a complete safety baseline: approved memory context builder, two-layer gate, audit log, and safe schema. The memory injection pipeline is ready to be wired to a real LLM.
2. The system is currently mock-only. The highest-value next step is making chat responses real. All other Phase 4 options (TTS, UI polish, daily summary) are more valuable when the AI engine is real.
3. The adapter pattern keeps the mock provider as the default and allows real providers to be added, swapped, or removed without changing the rest of the system.
4. All safety constraints from Phase 3 carry forward unchanged. No new safety surface is introduced beyond API key management.

### What Option A Does NOT Change

- `/chat` response schema remains `reply / mood / source`
- Memory-aware chat two-layer gate is unchanged
- Audit log creation is unchanged
- The mock provider remains available and is the default
- No tool execution, no file access, no autonomous action
- No TTS, no STT, no Live2D
- No vector database or semantic retrieval
- No automatic memory extraction

---

## Phase 4 Safety Constraints

These constraints apply to all Phase 4 work and must not be weakened without an explicit safety design review:

| Constraint | Rule |
|---|---|
| Real provider disabled by default | `LLM_PROVIDER=mock` is the default; real provider requires `LLM_PROVIDER=<name>` |
| Mock provider always available | MockLLMProvider must remain functional and testable at all times |
| API key from env var only | `LLM_API_KEY` (or provider-specific equivalent) must come from environment variable only |
| No API key in frontend | API key must never be sent to or stored in renderer.js, index.html, or any client-side code |
| No API key in logs | Backend must never log the API key value |
| No API key in responses | API key must never appear in any HTTP response body |
| `/chat` schema unchanged | Response remains `reply / mood / source` regardless of which provider is active |
| Memory gate unchanged | `MEMORY_INJECTION_ENABLED` + `use_memory` two-layer gate controls memory injection — no change |
| No tool execution | LLM output must not be parsed for tool call syntax in Phase 4 |
| No file access | LLM must not be given access to user files |
| No autonomous action | LLM output is displayed to user only; no side effects triggered |
| No automatic memory extraction | LLM responses must not trigger automatic memory writes |
| Output validation | LLM response must be validated for basic schema before being returned |
| Fallback on error | If real provider fails, return a clear error message; never crash silently |

---

## Proposed Task Sequence

| Task | Name | Type | Notes |
|---|---|---|---|
| TASK-030 | Phase 4 Planning | Design-only | This document |
| TASK-031 | LLM Adapter Design | Design-only | Define interface, provider pattern, API key handling design, safety constraints — no code |
| TASK-032 | LLM Provider Interface Skeleton | Implementation | Define abstract `LLMProvider` class, `MockLLMProvider`, and `get_llm_provider()` factory — no real API calls |
| TASK-033 | Mock Provider Compatibility Tests | Testing | Verify existing 226 tests still pass; add tests confirming mock provider matches current behavior |
| TASK-034 | Real Provider Config Design | Design-only | Define env var names, config loading, API key validation, error handling — no real API calls yet |
| TASK-035 | Real Provider Integration Behind Feature Flag | Implementation | Implement first real provider (OpenAI or Anthropic) behind `LLM_PROVIDER` flag; integration tests with mocked HTTP |
| TASK-036 | LLM Runtime Smoke Check | Validation | End-to-end runtime test with real provider; verify schema, memory gate, audit, no key exposure |
| TASK-037 | LLM Safety Review | Review | Review prompt construction, key handling, output validation, and memory gate before marking Phase 4 stable |

### Task Sequencing Rules

- **TASK-031 is design-only.** No provider code may be written until TASK-031 design is complete.
- **TASK-032 is interface-only.** No real LLM API calls until TASK-035.
- **TASK-034 is design-only.** Config design must be reviewed before real provider code begins.
- **TASK-035 is the first task that touches a real external API.** It requires TASK-034 design approval and must include mocked HTTP tests.
- **TASK-037 (safety review) must pass before Phase 4 is declared stable.**

---

## Not In Phase 4 Initial Scope

The following are explicitly deferred and must not be implemented during TASK-031 through TASK-037:

| Feature | Reason for deferral |
|---|---|
| TTS (voice output) | Deferred to after LLM adapter; more valuable with real responses |
| STT (voice input) | Requires TTS first; Phase 5 |
| Live2D animation | Phase 5 |
| Vector database | Phase 4+ (after LLM adapter is stable) |
| Semantic / embedding-based retrieval | Requires vector DB; deferred |
| Autonomous agent actions | Phase 5; requires dedicated safety design |
| User file reading | Phase 5; requires safety layer design |
| Full Electron packaging / distribution | Phase 4 polish track (Option C); deferred until LLM adapter done |
| Automatic memory extraction from chat | Requires explicit user review flow; Phase 4 follow-up at earliest |
| Daily summary generation | Requires LLM adapter first; Option D deferred |
| Multi-user support | Not in MVP scope |
| Cloud sync / remote database | Not in MVP scope |
