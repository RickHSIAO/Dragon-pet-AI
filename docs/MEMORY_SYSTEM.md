# Memory System Specification

> dragon-pet-ai — Memory System Design
> Status: DRAFT
> Last Updated: 2026-05-19
> Owner: TASK-002

---

## 1. Purpose

Memory exists to make the pet feel **personal, consistent, and useful** across sessions.

Memory in dragon-pet-ai is not model fine-tuning. The underlying LLM has no persistent state between calls. All persistence is handled externally via a local database, and relevant memory is injected into the prompt at the start of each turn.

### Design Goals

- The pet should remember what the user has explicitly shared
- The pet should not pretend to remember things it was never told
- Memory reads should feel natural, not mechanical
- Memory writes must be controlled and transparent
- The user must always be able to inspect and delete any stored memory
- Sensitive data must never be stored automatically

---

## 2. Memory Types

### 2.1 `conversation_history`
Short-to-medium term record of messages exchanged in recent sessions.

- Stored per session with timestamps
- Used for context injection in current and near-future turns
- Oldest entries age out of active context window (configurable N turns)
- Retained in DB for user review; not permanently injected after aging out
- Does not summarize automatically in MVP

### 2.2 `long_term_memory`
Explicit facts the user has asked the pet to remember, or facts confirmed as important by the user.

- Examples: name, current projects, long-term goals, key preferences
- Injected into every session start prompt
- Has confidence level (see Section 5)
- Can be tagged, viewed, and deleted by user
- Has no automatic expiry — remains until user deletes or corrects it

### 2.3 `user_preference`
Behavioral preferences that affect how the pet responds.

- Examples: response length preference, preferred language style, topics to avoid
- Applied to system prompt construction
- Stored separately from factual memories to allow targeted management
- Updated when user explicitly states a preference or corrects pet behavior

### 2.4 `project_context`
Information about the user's ongoing projects.

- Examples: project names, current phase, tech stack, open problems, team members
- Written only when user explicitly shares project information
- Injected selectively when project-related conversation is detected
- Not injected in casual/emotional conversation to avoid noise

### 2.5 `task_memory`
State of the user's task list.

- Individual tasks with status (pending, in_progress, done, cancelled)
- Linked to `tasks` table (see Section 6)
- Injected as a summary when user asks about tasks or during planning conversation
- Task completion is tracked; completed tasks move to archive, not deleted

### 2.6 `character_state`
The pet's current internal state.

- Stores: mood enum, energy level (integer), last interaction timestamp
- Updated after each completed chat turn
- Persists across sessions
- Read at session start to restore pet's current state
- User can ask about the pet's state; state is transparent

### 2.7 `relationship_state`
The evolving relationship between user and pet.

- Stores: affection (int), trust (int), familiarity (int), interaction_count (int), last_session_at (timestamp)
- Updated incrementally after each session
- Influences prompt construction (tone, formality, reference depth)
- Transparently accessible — user can ask "how do you feel about me?" and get an honest answer

### 2.8 `daily_summary`
A summarized record of each day's interactions.

- Generated at end of session or on demand (not automatic in MVP)
- Covers: topics discussed, tasks added/completed, notable events
- Stored per calendar day
- Used for context retrieval in future sessions ("what did we talk about last Tuesday?")
- In MVP: placeholder endpoint exists; generation logic deferred to Phase 3

### 2.9 `system_event`
Internal events logged for transparency and debugging.

- Examples: memory write confirmed, memory deleted by user, character state updated, session started/ended
- Not injected into LLM prompt
- Available for user inspection (audit log)
- Useful for debugging unexpected pet behavior

---

## 3. Memory Write Rules

### 3.1 Always Allowed — Write Without Confirmation

| Data Type | Example |
|---|---|
| User explicitly asks pet to remember something | "Remember that I prefer dark mode." |
| Long-term user preferences stated clearly | "I like short responses for casual chat." |
| Project-level status user shares directly | "This project is called Orion, it's a FastAPI backend." |
| User goals stated explicitly | "My goal this month is to finish the MVP." |
| Character state changes (internal) | Mood update after a positive interaction |
| Task status changes | User says "mark that task as done" |

### 3.2 Never Allowed — Must Not Store Automatically

| Sensitive Data | Reason |
|---|---|
| Passwords or passphrases | Security — must never be stored |
| API keys or tokens | Security |
| Private keys (SSH, GPG, crypto) | Security |
| Financial account numbers or credentials | Security |
| Government ID numbers | Privacy |
| Highly sensitive health information | Privacy (e.g., diagnoses, medications) |
| Emotional statements made in distress | Context-sensitive; likely not intended as fact |
| Unconfirmed inferences or guesses | Accuracy; must not treat assumption as fact |

If the user accidentally shares any of the above, the pet must:
1. Not store it
2. Gently acknowledge it was received but not retained
3. Suggest the user not share such information in chat

### 3.3 Requires User Confirmation Before Writing

| Data Type | Why Confirmation Is Needed |
|---|---|
| Health-related information | Sensitive; context-dependent |
| Financial situation or status | Sensitive |
| Interpersonal / relationship information | Sensitive; may change |
| Long-term psychological state | Not a fact; could harm if referenced incorrectly |
| Work secrets or confidential project details | User must explicitly consent to storage |

Confirmation flow (MVP):
> Pet: "You mentioned [X]. Should I remember this for future conversations?"
> User: "Yes" → write to `long_term_memory` with `confidence: explicit`
> User: "No" → discard

---

## 4. Memory Read Rules

### 4.1 Context Assembly Order (per chat turn)

1. System prompt (character identity + behavior rules)
2. User preferences (from `user_preference`)
3. Relationship state summary (from `relationship_state`)
4. Character state summary (from `character_state`)
5. Long-term memory block (from `long_term_memory`, filtered by relevance)
6. Active project context (from `project_context`, injected only if relevant)
7. Recent conversation history (last N turns from `conversation_history`)
8. User's current message

### 4.2 Read Principles

- **Recency wins:** Recent conversation context is prioritized over older long-term memory for topic resolution
- **Relevance filtering:** Long-term memory and project context are only injected when topically relevant — not on every turn
- **No over-mentioning:** The pet must not constantly reference stored facts unprompted; memory should surface naturally
- **Conflict resolution:** If current user input contradicts stored memory, the current input is treated as correct; the pet may ask if the memory should be updated
- **Confidence awareness:** Low-confidence or stale memories are phrased cautiously ("I think I remember you mentioned...", "If I'm recalling correctly...")
- **Token budget:** Total injected memory must not exceed a configurable token limit to leave room for the current conversation

### 4.3 Memory Injection Examples

Good (natural):
> User: "I'm starting on the auth module today."
> Pet (with stored project context): "Good — you mentioned Orion uses FastAPI, so JWT should integrate cleanly there."

Bad (mechanical):
> Pet: "I have stored memory: user's project is Orion (FastAPI backend). User's name is Rick. User likes dark mode. Now responding to: 'I'm starting on the auth module today.'"

---

## 5. Memory Confidence Levels

Each memory entry carries a confidence level that affects how the pet phrases references to it.

| Level | Definition | How Pet Phrases It |
|---|---|---|
| `explicit` | User directly stated this fact | States it as fact: "You mentioned X" |
| `inferred` | Pet inferred this from conversation, not stated directly | Phrases cautiously: "I think you prefer X — is that right?" |
| `temporary` | Relevant only for the current session or short term | Not carried forward to future sessions automatically |
| `stale` | Not referenced or confirmed in a long time | Prefixes with uncertainty: "I recall you mentioned X a while back — still true?" |
| `user_corrected` | User has corrected this memory | Marked; old value retained for audit; new value is active |

---

## 6. Suggested MVP Database Schema

> These are directional field definitions for planning purposes.
> Exact types, constraints, and migrations will be defined in TASK-003.

### `users`
Single-user system in MVP. Table exists for future multi-user support.
- `id` (PK)
- `created_at`
- `display_name`

### `conversations`
One row per session (a continuous interaction block).
- `id` (PK)
- `user_id` (FK)
- `started_at`
- `ended_at`
- `summary` (nullable — populated in Phase 3)

### `messages`
All messages exchanged.
- `id` (PK)
- `conversation_id` (FK)
- `role` — `user` | `assistant`
- `content`
- `created_at`

### `memories`
Long-term memory entries.
- `id` (PK)
- `user_id` (FK)
- `type` — maps to memory type (long_term, preference, project_context, etc.)
- `key` — short label (e.g., "project_name", "preferred_language")
- `value` — stored fact
- `confidence` — explicit | inferred | temporary | stale | user_corrected
- `created_at`
- `last_referenced_at`
- `is_active` — soft delete flag

### `character_state`
One active row per user.
- `id` (PK)
- `user_id` (FK)
- `mood` — enum (neutral, happy, proud, concerned, sulking, focused, excited, tired)
- `energy` — integer 0–100
- `updated_at`

### `relationship_state`
One active row per user.
- `id` (PK)
- `user_id` (FK)
- `affection` — integer 0–100
- `trust` — integer 0–100
- `familiarity` — integer 0–100
- `interaction_count` — total sessions
- `last_session_at`

### `tasks`
User's task list.
- `id` (PK)
- `user_id` (FK)
- `title`
- `status` — pending | in_progress | done | cancelled
- `created_at`
- `completed_at` (nullable)

### `daily_summaries`
One row per calendar day (when generated).
- `id` (PK)
- `user_id` (FK)
- `date` — calendar date (YYYY-MM-DD)
- `summary_text`
- `generated_at`

---

## 7. Memory Lifecycle

### 7.1 Create
- Triggered by user request, confirmation flow, or internal state update
- Writes to appropriate table with confidence level and timestamp
- System event logged

### 7.2 Retrieve
- Called at session start and per-turn context assembly
- Filtered by type, relevance, and token budget
- `last_referenced_at` updated on access

### 7.3 Update
- Triggered when user corrects or refines a memory
- Old value archived (not deleted) as `user_corrected` confidence record
- New value written as fresh entry with `explicit` confidence

### 7.4 Decay / Stale
- Memory entries not referenced for a configurable period are marked `stale`
- Stale memories are not deleted; they are injected less aggressively and phrased with uncertainty
- No automatic deletion in MVP

### 7.5 Delete
- User can request deletion of specific memory entries via chat or UI
- Deletion is a hard delete in MVP (no archive in user-facing deletion flow)
- System event logged for audit trail
- Pet confirms deletion before executing

### 7.6 User Correction
- User says something contradicting a stored memory
- Pet detects conflict and asks for clarification
- If user confirms correction, old entry marked `user_corrected`, new entry written
- Pet does not argue with corrections

---

## 8. Safety Boundaries

These rules apply at MVP and must not be weakened without explicit safety design review.

| Boundary | Rule |
|---|---|
| **Inspectable** | User must be able to list all stored memories at any time |
| **Deletable** | User must be able to delete any memory entry at any time |
| **No hidden memory** | The pet must not store information that is not visible to the user |
| **No sensitive auto-write** | Passwords, keys, credentials, and sensitive health data must never be stored automatically |
| **No autonomous action** | Memory alone cannot trigger any action — actions require user instruction |
| **No external leakage** | Memory data must not be sent to any external service except the configured LLM API (as part of the prompt) |
| **Transparent on request** | If the user asks "what do you remember about me?", the pet must respond honestly and completely |
| **Soft correction** | Stale or incorrect memories must be handled gracefully, not defensively |

---

## 9. MVP Limitations

The following capabilities are explicitly out of scope for MVP:

| Capability | Status |
|---|---|
| Vector database / semantic search | Not in MVP — simple keyword/tag filtering only |
| Automatic memory summarization | Not in MVP — daily summary is manual/on-demand |
| Fine-tuning on user data | Not in MVP — never planned unless explicitly designed with safety review |
| Cross-device memory sync | Not in MVP — local SQLite only |
| Cloud memory backup | Not in MVP — local-first always |
| Autonomous file reading for memory | Not in MVP — Phase 5 (with safety layer) |
| Autonomous terminal execution | Not in MVP — Phase 5 (with safety layer) |
| Proactive memory suggestions | Not in MVP — memory writes are always user-initiated or confirmed |
| Emotion-triggered memory writes | Not in MVP — emotional state is internal only; does not write user-facing memories |
| Multi-user memory | Not in MVP — single user only |
