# TASKS

## TASK-000 - Project Skeleton

Status: DONE

Goal:
Create the initial project skeleton and documentation placeholders for the AI desktop pet project.

Scope:
- Create folders
- Create documentation files
- Create README.md
- Create .env.example
- Do not implement runtime features yet

Acceptance Criteria:
- Folder structure exists ✅
- All docs files exist ✅
- README.md exists ✅
- .env.example exists ✅
- No AI API integration ✅
- No voice integration ✅
- No Live2D integration ✅

Next Task:
TASK-001 - Define MVP PRD and architecture

## TASK-001 - MVP PRD and Initial Architecture

Status: DONE

Goal:
Define the MVP scope, initial architecture, and development roadmap for the AI desktop pet project.

Scope:
- Fill docs/PRD.md
- Fill docs/ARCHITECTURE.md
- Fill docs/ROADMAP.md
- Update docs/TASKS.md
- Do not implement runtime features

Acceptance Criteria:
- PRD defines MVP goal, user stories, in-scope features, out-of-scope features, and acceptance criteria ✅
- ARCHITECTURE defines initial module boundaries, data flow, technology choices, and future extension points ✅
- ROADMAP defines Phase 0 to Phase 5 development order ✅
- TASKS.md marks TASK-000 as DONE ✅
- TASKS.md records TASK-001 as IN_PROGRESS ✅
- No code implementation is added ✅

Next Task:
TASK-002 - Character Spec and Memory System Spec

---

## TASK-002 - Character Spec and Memory System Spec

Status: DONE

Goal:
Define the character behavior rules and memory system rules before implementing the runtime skeleton.

Scope:
- Fill docs/CHARACTER_SPEC.md
- Fill docs/MEMORY_SYSTEM.md
- Update docs/TASKS.md
- Do not implement runtime features

Acceptance Criteria:
- CHARACTER_SPEC.md defines character identity, tone, relationship behavior, emotional states, boundaries, and response style ✅
- MEMORY_SYSTEM.md defines memory types, write rules, read rules, safety rules, schema direction, and MVP limitations ✅
- TASKS.md marks TASK-001 as DONE ✅
- TASKS.md records TASK-002 as IN_PROGRESS ✅
- No code implementation is added ✅

Next Task:
TASK-003 - Basic Runtime Skeleton

---

## TASK-003 - Basic Runtime Skeleton

Status: DONE

Goal:
Create the first runnable backend and desktop skeleton for dragon-pet-ai.

Scope:
- Create FastAPI backend skeleton
- Create Electron desktop skeleton
- Add GET /health endpoint
- Add POST /chat mock endpoint
- Add minimal SQLite / SQLModel database initialization placeholder
- Allow desktop app to send a chat message to backend and display mock response
- Update README startup instructions
- Update docs/TASKS.md

Acceptance Criteria:
- Backend can start locally
- GET /health returns ok status
- POST /chat accepts a message and returns a mock character-style response
- Desktop app can start locally
- Desktop app has a message input area
- Desktop app can call backend /chat
- Desktop app displays the returned mock response
- No real AI API integration
- No TTS/STT
- No Live2D
- No autonomous tool execution
- TASK-002 is marked DONE
- TASK-003 is marked DONE after runtime smoke validation

Next Task:
TASK-004 - Backend Tests and Desktop Smoke Check

---

## TASK-004 - Backend Tests and Desktop Smoke Check

Status: DONE

Goal:
Add backend route tests and perform basic desktop smoke checks for the runtime skeleton.

Completion Notes:

- TASK-004 completed after Windows local GUI runtime smoke.
- Desktop successfully called backend POST /chat and received mock response.

Scope:

- Add pytest tests for backend /health and /chat
- Validate /chat request schema behavior
- Add .gitignore for generated files
- Check backend startup instructions
- Check desktop startup instructions
- Perform static or runtime smoke check for Electron desktop
- Do not add new product features

Acceptance Criteria:

- GET /health test passes
- POST /chat valid request test passes
- POST /chat invalid request returns validation error
- Generated SQLite database files are ignored by git
- Python cache, virtualenv, node_modules, and Electron build artifacts are ignored
- README startup instructions remain accurate
- Desktop files are present and basic startup path is documented
- No real AI API integration is added
- No TTS/STT/Live2D is added

Next Task:
TASK-005 - Mark Runtime Skeleton Stable and Prepare Chat Service

---

## TASK-005 - Mark Runtime Skeleton Stable and Prepare Chat Service

Status: DONE

Goal:
Mark the runtime skeleton as stable and refactor the mock chat logic into service modules to prepare for future real chat engine integration.

Scope:

- Mark TASK-003 as DONE
- Mark TASK-004 as DONE
- Add backend chat service module
- Add backend character service module
- Keep /chat behavior unchanged
- Keep all current tests passing
- Add service-level tests if useful
- Do not connect real AI provider
- Do not implement memory system yet

Acceptance Criteria:

- TASK-003 is marked DONE
- TASK-004 is marked DONE
- TASK-005 is marked DONE
- /chat route delegates reply generation to chat_service
- chat_service can call character_service for mock tone / mood
- Existing route tests still pass
- New service tests pass if added
- Response schema remains unchanged:
  - reply
  - mood
  - source
- source remains "mock"
- No real AI API integration is added
- No TTS/STT/Live2D is added
- No autonomous tool execution is added

Next Task:
TASK-006 - Character Prompt and Mock Chat Modes

---

## TASK-006 - Character Prompt and Mock Chat Modes

Status: DONE

Goal:
Add character prompt structure and simple mock chat modes while keeping the system fully offline and mock-only.

Scope:

- Mark TASK-005 as DONE
- Add prompt service placeholder
- Define mock chat modes
- Keep /chat compatible with existing clients
- Add tests for prompt and mock mode behavior
- Do not connect a real AI provider
- Do not implement memory system yet

Acceptance Criteria:

- TASK-005 is marked DONE
- TASK-006 is marked DONE
- prompt_service exists
- prompt_service can build a character prompt string for a given mode
- Supported modes include:
  - casual
  - project
  - debug
  - support
  - reminder
- /chat remains backward compatible with existing request body:
  - { "message": "hello" }
- /chat may optionally accept:
  - mode: string
- Invalid or unknown mode falls back safely to casual or project
- Response schema remains unchanged:
  - reply
  - mood
  - source
- source remains "mock"
- Existing tests still pass
- New tests pass
- No real AI API integration is added
- No TTS/STT/Live2D is added
- No autonomous tool execution is added

Next Task:
TASK-007 - SQLite Conversation Storage

---

## TASK-007 - SQLite Conversation Storage

Status: DONE

Goal:
Add minimal SQLite-backed conversation storage for chat history while keeping the system mock-only and offline.

Scope:

- Mark TASK-006 as DONE
- Add SQLModel database models for conversations and messages
- Create tables during backend startup
- Store user message and assistant mock response when /chat is called
- Keep /chat response schema backward compatible
- Add tests for conversation storage
- Do not implement memory retrieval or long-term memory yet

Acceptance Criteria:

- TASK-006 is marked DONE
- TASK-007 is marked DONE
- Conversation and Message SQLModel models exist
- init_db creates required tables
- /chat still accepts old request format:
  - { "message": "hello" }
- /chat still accepts optional mode:
  - { "message": "help me debug", "mode": "debug" }
- /chat response schema remains:
  - reply
  - mood
  - source
- source remains "mock"
- Each /chat call stores at least:
  - one user message
  - one assistant message
- Stored assistant message includes mood, mode, and source if practical
- Existing tests still pass
- New storage tests pass
- No real AI API integration is added
- No memory retrieval is added
- No vector database is added
- No Electron UI changes are made

Next Task:
TASK-008 - Character and Relationship State Tables

---

## TASK-008 - Character and Relationship State Tables

Status: DONE

Goal:
Add minimal character and relationship state tables to support future emotional and growth behavior while keeping the system mock-only and offline.

Scope:

- Mark TASK-007 as DONE
- Add CharacterState SQLModel model
- Add RelationshipState SQLModel model
- Create tables during backend startup
- Add state service helpers
- Optionally update state after each /chat call
- Keep /chat response schema unchanged
- Add tests for state creation and update behavior
- Do not implement memory retrieval or long-term memory yet
- Do not modify Electron UI

Acceptance Criteria:

- TASK-007 is marked DONE
- TASK-008 is marked DONE
- CharacterState model exists
- RelationshipState model exists
- init_db creates required tables
- State service can get or create default character state
- State service can get or create default relationship state
- /chat response schema remains:
  - reply
  - mood
  - source
- source remains "mock"
- Existing tests still pass
- New state tests pass
- No real AI API integration is added
- No memory retrieval is added
- No vector database is added
- No Electron UI changes are made

Next Task:
TASK-009 - Basic State-Aware Mock Chat

---

## TASK-009 - Basic State-Aware Mock Chat

Status: DONE

Goal:
Make mock chat lightly aware of internal character and relationship state while keeping the system offline and mock-only.

Scope:

- Mark TASK-008 as DONE
- Allow chat_service to receive current state context
- Read current CharacterState and RelationshipState before generating mock reply
- Lightly adjust mock reply based on state
- Keep /chat response schema unchanged
- Do not return state to frontend
- Do not implement memory retrieval
- Do not connect real AI provider
- Add tests for state-aware behavior

Acceptance Criteria:

- TASK-008 is marked DONE
- TASK-009 is marked DONE
- /chat reads existing character and relationship state before generating reply
- chat_service can accept optional state context
- mock reply can change slightly based on interaction_count / familiarity / affection / trust
- /chat response schema remains:
  - reply
  - mood
  - source
- source remains "mock"
- No state fields are returned to frontend
- Existing tests still pass
- New state-aware tests pass
- No real AI API integration is added
- No memory retrieval is added
- No vector database is added
- No Electron UI changes are made

Next Task:
TASK-010 - Memory Table Skeleton

---

## TASK-010 - Memory Table Skeleton

Status: DONE

Goal:
Add the first local Memory table and memory service skeleton without using memory in chat responses yet.

Scope:

- Mark TASK-009 as DONE
- Add Memory SQLModel model
- Create memory table during backend startup
- Add basic memory_service helpers
- Add tests for memory model and service
- Do not connect memory to /chat yet
- Do not implement memory retrieval
- Do not implement automatic memory extraction
- Do not add vector database

Acceptance Criteria:

- TASK-009 is marked DONE
- TASK-010 is marked DONE
- Memory model exists
- init_db creates memory table
- memory_service can create a memory record
- memory_service can list memory records
- memory_service can mark memory as inactive or deleted
- Existing tests still pass
- New memory tests pass
- /chat response schema remains unchanged:
  - reply
  - mood
  - source
- /chat does not use memory yet
- No real AI API integration is added
- No vector database is added
- No Electron UI changes are made

Next Task:
TASK-011 - Manual Memory Write API

---

## TASK-011 - Manual Memory Write API

Status: DONE

Goal:
Add explicit manual memory API endpoints for creating, listing, and deactivating local memory records.

Scope:

- Mark TASK-010 as DONE
- Add memory request/response schemas
- Add manual memory API endpoints
- Reuse memory_service
- Add route tests for memory endpoints
- Keep /chat completely unchanged
- Do not connect memory to /chat yet
- Do not implement semantic retrieval
- Do not implement automatic memory extraction

Acceptance Criteria:

- TASK-010 is marked DONE
- TASK-011 is marked DONE
- POST /memory creates a memory record
- GET /memory returns active memories
- DELETE /memory/{memory_id} deactivates a memory record
- DELETE /memory/{memory_id} returns 404 for missing memory
- Blank memory content is rejected
- Importance is clamped to 0..100
- /chat remains backward compatible
- /chat does not read memory
- /chat does not write memory
- Existing tests still pass
- New memory API tests pass
- No real AI API integration is added
- No vector database is added
- No Electron UI changes are made

Next Task:
TASK-012 - Manual Memory Read Context Preview

---

## TASK-012 - Manual Memory Read Context Preview

Status: DONE

Goal:
Add a manual memory context preview endpoint that shows how active memories could be assembled for future prompt context, without connecting memory to /chat.

Scope:

- Mark TASK-011 as DONE
- Add memory context preview schema
- Add memory_service helper to build preview text
- Add GET /memory/context-preview endpoint
- Keep /chat completely unchanged
- Do not connect memory to /chat yet
- Do not implement semantic retrieval
- Do not implement automatic memory extraction

Acceptance Criteria:

- TASK-011 is marked DONE
- TASK-012 is marked DONE
- GET /memory/context-preview exists
- Context preview includes active memories only
- Inactive memories are excluded
- Preview output is deterministic and testable
- Preview does not require LLM
- /chat remains backward compatible
- /chat does not read memory
- /chat does not write memory
- Existing tests still pass
- New context preview tests pass
- No real AI API integration is added
- No vector database is added
- No Electron UI changes are made

Next Task:
TASK-013 - Local Memory Management UI Placeholder

---

## TASK-013 - Local Memory Management UI Placeholder

Status: DONE

Goal:
Add a minimal desktop UI placeholder for manually managing local memory records and previewing memory context.

Scope:

- Mark TASK-012 as DONE
- Add Memory Management section to Electron UI
- Allow manual memory creation from desktop
- Allow listing active memory records
- Allow deactivating memory records
- Allow viewing memory context preview
- Keep /chat completely unchanged
- Do not connect memory to chat responses
- Do not implement semantic retrieval
- Do not implement automatic memory extraction

Acceptance Criteria:

- TASK-012 is marked DONE
- TASK-013 is marked DONE
- Desktop UI has a Memory section
- User can submit a manual memory through POST /memory
- User can refresh active memories through GET /memory
- User can deactivate a memory through DELETE /memory/{memory_id}
- User can view context preview through GET /memory/context-preview
- Backend unavailable errors are shown clearly
- /chat remains backward compatible
- /chat does not read memory
- /chat does not write memory automatically
- Existing backend tests still pass
- No real AI API integration is added
- No vector database is added
- No new frontend framework is added

Next Task:
TASK-014 - Manual Memory UI Runtime Smoke Check

---

## TASK-014 - Manual Memory UI Runtime Smoke Check

Status: DONE

Goal:
Validate the Electron Memory Management UI placeholder against the local backend at runtime.

Scope:

- Mark TASK-013 as DONE
- Record Windows local runtime smoke check results
- Do not modify backend code
- Do not modify Electron UI
- Do not add new features

Runtime Smoke Check Results:

- Backend pytest: previously passed, 75 passed
- Backend uvicorn: pass
- Desktop npm start: pass
- Electron window opened: yes
- Chat hello test: pass
- POST /chat 200: yes
- Create memory test: pass
- GET /memory list updated: yes
- Context preview updated: yes
- Deactivate memory test: pass
- Context preview excludes deactivated memory: yes

Screen Validation:

- Memory list changed from 2 active memories to 1 active memory
- Deactivated user_preference memory disappeared from the active list
- Context Preview showed only the remaining project_context memory
- /chat still displayed a normal mock reply

Non-Blocking Follow-Up:

- Memory section Save Memory button / layout spacing can be polished later
- This is not a functional blocker for TASK-014

Acceptance Criteria:

- TASK-013 is marked DONE
- TASK-014 is recorded as DONE
- Manual memory UI runtime smoke check passed
- /chat remained functional with mock reply
- No backend code was modified
- No Electron UI code was modified
- No new feature was added

Next Task:
TASK-015 - Manual Memory Injection Design

---

## TASK-015 - Manual Memory Injection Design

Status: DONE

Goal:
Design how approved manual memories will be safely assembled into future chat context without implementing memory injection yet.

Scope:

- Define memory injection rules
- Define eligible memory types
- Define excluded memory types
- Define prompt context formatting
- Define safety boundaries
- Define future implementation plan
- Do not implement runtime memory injection
- Do not modify /chat behavior

Acceptance Criteria:

- TASK-015 is marked DONE
- docs/MEMORY_SYSTEM.md includes a Manual Memory Injection Design section
- docs/ARCHITECTURE.md includes future memory injection data flow
- docs/ROADMAP.md mentions the future implementation step
- /chat behavior remains unchanged
- No backend production code is modified
- No Electron UI code is modified
- No semantic retrieval is implemented
- No vector database is added
- No real AI provider is added

Next Task:
TASK-016 - Opus Review for Memory Injection Safety

---

## TASK-016 - Opus Review for Memory Injection Safety

Status: DONE

Summary:
Opus reviewed the Manual Memory Injection Design and returned PASS WITH CHANGES. The review recommended tightening memory type definitions, removing ambiguous system_event eligibility, adding concrete injection limits, adding injection-time safety filters, adding prompt injection mitigation, avoiding raw metadata exposure to LLM prompts, adding feature flag requirements, and adding audit log requirements.

---

## TASK-017 - Apply Memory Injection Safety Review Changes

Status: DONE

Goal:
Apply the TASK-016 Opus review recommendations to the memory injection design documents before implementation begins.

Scope:

- Define character_note memory type
- Clarify system_event is not eligible for normal chat memory injection
- Add concrete memory injection limits
- Clarify confidence handling
- Add injection-time sensitive data filtering rules
- Add prompt injection mitigation rules
- Remove raw metadata exposure from future prompt format
- Add feature flag requirement
- Add audit log / injection event design
- Clarify service boundaries
- Do not implement runtime memory injection

Acceptance Criteria:

- TASK-015 is marked DONE
- TASK-016 is recorded as DONE
- TASK-017 is marked DONE
- docs/MEMORY_SYSTEM.md resolves character_note definition
- docs/MEMORY_SYSTEM.md removes system_event from normal eligible injection types
- docs/MEMORY_SYSTEM.md defines max injected memories = 5 for MVP
- docs/MEMORY_SYSTEM.md defines max memory context length = 1500 characters for MVP
- docs/MEMORY_SYSTEM.md defines confidence handling for explicit, user_corrected, inferred, temporary, stale
- docs/MEMORY_SYSTEM.md defines injection-time sensitive content filter
- docs/MEMORY_SYSTEM.md defines prompt injection mitigation using delimiters and fixed instruction
- docs/MEMORY_SYSTEM.md states raw importance/confidence should not be rendered into LLM prompt
- docs/MEMORY_SYSTEM.md defines MEMORY_INJECTION_ENABLED default False
- docs/MEMORY_SYSTEM.md defines audit log requirements
- docs/ARCHITECTURE.md clarifies service boundaries
- docs/ROADMAP.md reflects TASK-018 as Approved Memory Context Builder
- No backend/app code is modified
- No apps/desktop code is modified

Next Task:
TASK-018 - Approved Memory Context Builder

---

## TASK-018 - Approved Memory Context Builder

Status: DONE

Goal:
Implement an approved manual memory context builder with safety filters and deterministic ordering, without wiring it into /chat yet.

Scope:

- Mark TASK-017 as DONE
- Add approved memory filtering in memory_service
- Add sensitive-content filter for injection-time exclusion
- Apply MVP limits:
  - max memories = 5
  - max context length = 1500 characters
- Add prompt_service helper to format approved memory context with delimiters
- Ensure raw metadata is not rendered into normal prompt text
- Add tests for eligibility, filtering, ordering, and formatting
- Do not connect memory context to /chat
- Do not implement semantic retrieval
- Do not add vector database

Acceptance Criteria:

- TASK-017 is marked DONE
- TASK-018 is marked DONE
- memory_service can build approved memory context entries
- inactive memories are excluded
- system_event memories are excluded from normal chat injection
- inferred / temporary / stale / unknown confidence memories are excluded
- explicit and user_corrected memories can be included
- obvious sensitive content is excluded
- prompt injection-like content is treated as reference text, not instructions
- max included memories is 5
- max context text length is 1500 characters
- ordering is deterministic
- raw importance / confidence / memory id are not rendered into normal prompt context
- prompt_service wraps memory context in delimiters
- /chat remains unchanged and does not use memory
- Existing tests still pass
- New tests pass
- No real AI API integration is added
- No vector database is added
- No Electron UI changes are made

Next Task:
TASK-019 - Memory Injection Audit Log Skeleton

---

## TASK-019 - Memory Injection Audit Log Skeleton

Status: DONE

Goal:
Add a local audit log skeleton for future memory injection events without wiring memory injection into /chat yet.

Scope:

- Mark TASK-018 as DONE
- Add MemoryInjectionAudit SQLModel model
- Add audit service helpers
- Add tests for audit log creation and retrieval
- Keep /chat completely unchanged
- Do not connect memory context to /chat
- Do not implement semantic retrieval
- Do not add vector database
- Do not modify Electron UI

Acceptance Criteria:

- TASK-018 is marked DONE
- TASK-019 is recorded as IN_PROGRESS
- MemoryInjectionAudit model exists
- init_db creates audit table
- audit service can create an audit event
- audit service can list audit events
- audit event records selected memory IDs as safe serialized data
- audit event records selected count
- audit event records total context length
- audit event records feature flag state
- audit event can record exclusion summary without raw sensitive memory content
- Existing tests still pass
- New audit tests pass
- /chat remains unchanged and does not use memory
- No real AI API integration is added
- No vector database is added
- No Electron UI changes are made

Next Task:
TASK-020 - Feature Flagged Memory-Aware Chat Wiring

---

## TASK-020 - Feature Flagged Memory-Aware Chat Wiring

Status: DONE

Goal:
Wire approved manual memory context into the /chat internal pipeline behind a disabled-by-default feature flag.

Scope:
- Mark TASK-019 as DONE
- Add MEMORY_INJECTION_ENABLED config flag (default False)
- When disabled: /chat must not build memory context and must not create audit rows
- When enabled: /chat builds approved memory context and creates audit row
- Keep /chat response schema unchanged (reply/mood/source)
- Do not expose memory content in /chat response
- Do not connect real AI provider
- Do not implement semantic retrieval
- Do not modify Electron UI
- Harden test DB isolation if needed

Acceptance Criteria:
- TASK-019 is marked DONE ✅
- TASK-020 is marked DONE ✅
- MEMORY_INJECTION_ENABLED exists and defaults to False
- With flag disabled: /chat returns 200, schema unchanged, no audit rows created
- With flag enabled: /chat creates MemoryInjectionAudit row with correct counts
- Existing tests still pass
- New tests pass
- backend/dragon_pet_ai.db is not touched during pytest

Implementation Notes:
- conversation_id in audit: set to default conversation id (obtained via get_or_create_default_conversation before store_chat_turn)
- exclusion_summary in audit: currently None — exclusion summary computation not yet implemented. Follow-up in TASK-021 or later.
- formatted_context is built but not passed to mock reply generator (no real LLM yet)

Next Task:
TASK-021 - Feature Flagged Memory-Aware Chat Runtime Smoke Check

---

## TASK-021 - Feature Flagged Memory-Aware Chat Runtime Smoke Check

Status: DONE

Goal:
Verify that TASK-020's feature-flagged memory wiring works correctly in a full runtime environment (backend + Electron desktop), not just under pytest.

Scope:
- Run backend pytest suite and confirm all tests pass
- Start uvicorn backend and confirm no startup errors
- Start Electron desktop with npm start and confirm window opens
- Send a chat message with MEMORY_INJECTION_ENABLED=false and confirm flag-off behaviour
- Send a chat message with MEMORY_INJECTION_ENABLED=true and confirm flag-on behaviour
- Confirm /chat response does not expose memory content
- Confirm Memory UI and Context Preview remain separate from chat response
- Record results in TASKS.md
- Do not modify backend code
- Do not modify Electron UI
- Do not add new features

Acceptance Criteria:
- TASK-020 is marked DONE ✅
- Backend pytest: 181 passed ✅
- Backend uvicorn starts without errors ✅
- Electron window opens via npm start ✅
- Flag disabled: memory UI and context preview work independently, chat response unchanged ✅
- Flag enabled: POST /chat returns 200, reply is mock-only, memory content not exposed ✅
- No backend errors during smoke check ✅
- No code changes made ✅

Runtime Smoke Check Results (performed on Windows host):
- Backend pytest: 181 passed, 0 failed
- Backend uvicorn: started successfully, no errors
- Desktop npm start: launched successfully
- Electron window: opened and responsive
- Flag false — Memory UI: PASS
- Flag false — Context Preview: PASS
- Flag true — Backend start: PASS
- Flag true — Chat send: PASS
- POST /chat response status: 200 OK
- Chat reply: mock-only, memory content NOT exposed in response
- Backend log: POST /chat HTTP/1.1 200 OK confirmed
- Backend errors: none

Screen Observations:
- Chat message "hello memory test" sent successfully
- Backend logged POST /chat HTTP/1.1 200 OK
- Chat reply remained mock-only and did not display memory content
- Memory UI and Context Preview remained separate from chat response

Next Task:
TASK-022 - Memory-Aware Chat UI Toggle Design

---

## TASK-022 - Memory-Aware Chat UI Toggle Design

Status: DONE

Goal:
Design the future desktop UI toggle for memory-aware chat using a safe two-layer control model. This task is design-only — no backend or Electron code is modified.

Scope:
- Define UI toggle behavior and disabled / unavailable states
- Define backend global gate behavior
- Define /chat request extension design (use_memory field)
- Define safety copy shown to user
- Define audit behavior under all flag/toggle combinations
- Define future implementation steps
- Do not implement the UI toggle yet
- Do not modify /chat runtime behavior
- Only docs/ files may be modified

Acceptance Criteria:
- TASK-022 is marked DONE ✅
- docs/ARCHITECTURE.md documents the two-layer memory control model ✅
- docs/MEMORY_SYSTEM.md documents when memory-aware chat may use approved memory context ✅
- docs/ROADMAP.md includes UI toggle design and implementation sequence ✅
- README notes that the UI toggle is designed but not implemented ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- /chat behavior remains unchanged ✅

Design Decisions:
- UI toggle does NOT modify backend environment variables
- No PATCH /config endpoint is needed for MVP
- MEMORY_INJECTION_ENABLED is set before backend startup (server-side gate only)
- Frontend sends use_memory per request (per-turn opt-in)
- Only when both MEMORY_INJECTION_ENABLED=true AND use_memory=true can /chat use approved memory context
- renderer.js continues to use direct HTTP fetch; no IPC required for MVP
- /chat response schema remains reply/mood/source regardless of flag or toggle state

Next Task:
TASK-023 - Memory-Aware Chat UI Toggle Implementation

---

## TASK-023 - Memory-Aware Chat UI Toggle Implementation

Status: DONE

Goal:
Implement the desktop per-request memory-aware chat toggle and wire it to /chat through use_memory while preserving the backend global gate.

Scope:
- Mark TASK-022 as DONE
- Add use_memory: bool = False to ChatRequest schema
- Update /chat route to require both MEMORY_INJECTION_ENABLED and request.use_memory before using approved memory context
- Add desktop UI toggle near chat input labeled "Use approved memories"
- Send use_memory in /chat request body according to toggle state
- Keep /chat response schema unchanged (reply/mood/source)
- Add backend tests for two-layer gate behavior
- Update existing TestChatFlagEnabled tests to send use_memory=True where needed
- Do not add PATCH /config
- Do not use Electron IPC
- Do not connect real AI provider
- Do not implement semantic retrieval

Acceptance Criteria:
- TASK-022 is marked DONE ✅
- TASK-023 is recorded as IN_PROGRESS ✅
- ChatRequest supports use_memory: bool = False ✅
- Old /chat request { "message": "hello" } still works (backward compatible) ✅
- New /chat request { "message": "hello", "use_memory": true } works ✅
- With MEMORY_INJECTION_ENABLED=false and use_memory=true: /chat returns 200, no audit row created ✅
- With MEMORY_INJECTION_ENABLED=true and use_memory=false: /chat returns 200, no audit row created ✅
- With MEMORY_INJECTION_ENABLED=true and use_memory=true: /chat returns 200, audit row created when eligible memory exists ✅
- /chat response schema remains reply/mood/source only ✅
- Memory content is not returned in /chat response ✅
- Desktop UI has a visible toggle labeled "Use approved memories" ✅
- Desktop UI sends use_memory according to toggle state ✅
- Desktop UI shows helper text about backend MEMORY_INJECTION_ENABLED requirement ✅
- Existing tests pass (updated where necessary for use_memory=True) ✅
- New two-layer gate tests pass ✅
- No real AI API integration ✅
- No vector DB, no semantic retrieval, no Electron IPC, no PATCH /config ✅

Implementation Summary:
- backend/app/schemas/chat.py: added use_memory: bool = False to ChatRequest
- backend/app/api/routes.py: two-layer gate (memory_enabled AND memory_requested)
- apps/desktop/src/renderer/index.html: #memory-toggle-bar with checkbox
- apps/desktop/src/renderer/renderer.js: reads useMemoryToggle.checked into POST body
- apps/desktop/src/renderer/styles.css: toggle styles
- backend/tests/test_routes.py: 8 existing tests updated; 13 new TestChatTwoLayerGate tests added
- pytest result: 193 passed, 0 failed
- dragon_pet_ai.db: 0 bytes, not touched during pytest

Next Task:
TASK-024 - Memory-Aware Chat Runtime Smoke Check

---

## TASK-024 - Memory-Aware Chat Runtime Smoke Check

Status: DONE

Goal:
Verify that TASK-023's two-layer memory-aware chat toggle works correctly in a full runtime environment (backend + Electron desktop), covering all three gate combinations.

Scope:
- Run backend pytest suite and confirm all tests pass
- Start uvicorn backend and confirm no startup errors
- Start Electron desktop with npm start and confirm window opens
- Smoke-check all three gate combinations:
  - flag false + toggle on  → no injection, no audit row
  - flag true  + toggle off → no injection, no audit row
  - flag true  + toggle on  → injection path used, audit row created
- Confirm /chat response does not expose memory content in all cases
- Confirm MemoryInjectionAudit row contents are correct
- Record results in TASKS.md
- Do not modify backend code
- Do not modify Electron UI
- Do not add new features

Acceptance Criteria:
- TASK-023 is marked DONE ✅
- Backend pytest: 193 passed ✅
- Backend uvicorn starts without errors ✅
- Electron window opens via npm start ✅
- flag false + toggle on: POST /chat 200, no audit row, no memory content in response ✅
- flag true  + toggle off: POST /chat 200, no audit row, no memory content in response ✅
- flag true  + toggle on:  POST /chat 200, audit row created, memory content not in response ✅
- MemoryInjectionAudit row contents verified ✅
- Backend errors: none ✅
- No code changes made ✅

Runtime Smoke Check Results (performed on Windows host):

Backend pytest: 193 passed, 0 failed

Scenario 1 — flag false + toggle on:
- MEMORY_INJECTION_ENABLED: removed / unset
- Desktop toggle: checked (use_memory=true in request)
- POST /chat response: 200 OK
- Chat: worked normally
- Memory content in response: no
- Audit row created: no
- Backend errors: none

Scenario 2 — flag true + toggle off:
- MEMORY_INJECTION_ENABLED=true
- Desktop toggle: unchecked (use_memory=false in request)
- POST /chat response: 200 OK
- Chat: worked normally
- Memory content in response: no
- Audit row created: no
- Backend errors: none

Scenario 3 — flag true + toggle on:
- MEMORY_INJECTION_ENABLED=true
- Desktop toggle: checked (use_memory=true in request)
- POST /chat response: 200 OK
- Chat: worked normally
- Memory content in response: no
- Audit row created: yes
- audit_count: 3
- latest audit selected_memory_ids_json: '[3, 2]'
- latest audit selected_count: 2
- latest audit total_context_chars: 398
- latest audit feature_flag_enabled: True
- Backend errors: none

Two-Layer Gate Verdict: PASS — all three combinations behaved as designed.

Next Task:
TASK-025 - Memory Injection Audit Inspection Design

---

## TASK-025 - Memory Injection Audit Inspection Design

Status: DONE

Goal:
Design how users and developers can inspect memory injection audit records without exposing raw memory content.

Scope:
- Define audit inspection API design
- Define audit inspection UI design
- Define safe display fields
- Define fields that must not be displayed
- Define pagination behavior
- Define relation to no-hidden-memory principle
- Do not implement endpoint
- Do not implement UI
- Do not modify runtime behavior

Acceptance Criteria:
- TASK-025 is marked DONE ✅
- docs/MEMORY_SYSTEM.md documents audit inspection rules ✅
- docs/ARCHITECTURE.md documents future audit inspection API and UI flow ✅
- docs/ROADMAP.md includes TASK-026 and TASK-027 ✅
- README notes audit inspection is designed but not implemented ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- /chat behavior remains unchanged ✅

Design Decisions:
- Future read-only endpoint: GET /memory/audit with limit/offset pagination
- Future Memory UI: Audit Inspection section showing metadata cards
- Safe to display: id, created_at, conversation_id, selected_memory_ids_json, selected_count, total_context_chars, feature_flag_enabled, exclusion_summary_json
- Must NOT display: raw memory content, full prompt text, approved memory context text, system prompt, raw LLM messages
- selected_memory_ids_json shows IDs only — no automatic inline expansion of content
- Audit rows are read-only; GET /memory/audit must not create rows or modify last_used_at
- Default limit: 20, max limit: 100, sort: created_at descending

Next Task:
TASK-026 - Memory Injection Audit Inspection API

---

## TASK-026 - Memory Injection Audit Inspection API

Status: DONE

Goal:
Implement a read-only API for inspecting memory injection audit records without exposing raw memory content.

Scope:
- Mark TASK-025 as DONE
- Add MemoryInjectionAuditResponse and MemoryInjectionAuditListResponse schemas
- Add parse_memory_ids_json, parse_exclusion_summary_json, normalize_audit_pagination helpers to memory_audit_service
- Add list_memory_injection_audits_paginated to memory_audit_service
- Add GET /memory/audit endpoint with limit/offset query params
- Return safe metadata only (no raw memory content, no prompt text)
- Keep /chat behavior unchanged
- Do not implement UI yet
- Do not expose raw memory content or prompt text

Acceptance Criteria:
- TASK-025 is marked DONE ✅
- TASK-026 is marked DONE ✅
- GET /memory/audit exists and returns 200 ✅
- Endpoint supports limit and offset query params ✅
- Default limit is 20, max limit is 100, default offset is 0 ✅
- Results sorted newest first (id descending) ✅
- Response shape: { items, count, limit, offset } ✅
- Each item includes safe audit metadata only ✅
- Response does not include raw memory content or prompt text ✅
- Endpoint is read-only (does not create/modify DB rows) ✅
- /chat behavior remains unchanged ✅
- Existing 193 tests pass + 16 new tests added = 209 passed ✅
- New audit API tests pass (test_memory_audit_routes.py — 15 tests) ✅
- New service tests pass (test_memory_audit_service.py — 14 new tests) ✅
- No Electron UI changes ✅
- dragon_pet_ai.db not touched during pytest (0 bytes) ✅

Implementation Summary:
- backend/app/schemas/memory_audit.py: MemoryInjectionAuditResponse, MemoryInjectionAuditListResponse
- backend/app/services/memory_audit_service.py: parse_memory_ids_json, parse_exclusion_summary_json, normalize_audit_pagination, list_memory_injection_audits_paginated
- backend/app/api/routes.py: GET /memory/audit (read-only, paginated, newest first)
- backend/tests/test_memory_audit_service.py: 14 new tests for new helpers
- backend/tests/test_memory_audit_routes.py: 15 new route tests (new file)
- pytest result: 209 passed, 0 failed

Next Task:
TASK-027 - Memory Injection Audit UI

---

## TASK-027 - Memory Injection Audit UI

Status: DONE

Goal:
Add an Electron UI section for inspecting memory injection audit metadata without exposing raw memory content.

Scope:
- Mark TASK-026 as DONE
- Add Audit Logs section to desktop Memory UI
- Call GET /memory/audit from renderer
- Render safe audit metadata cards
- Support Refresh button
- Support limit / offset controls
- Do not expose raw memory content
- Do not modify backend API
- Do not modify /chat behavior
- Do not add frontend framework

Acceptance Criteria:
- TASK-026 is marked DONE ✅
- TASK-027 is recorded as IN_PROGRESS ✅
- Desktop UI has an Audit Logs section
- Audit Logs section has Refresh button
- Renderer calls GET /memory/audit
- Audit cards display: id, created_at, conversation_id, selected_memory_ids, selected_count, total_context_chars, feature_flag_enabled, exclusion_summary
- Audit UI does not display raw memory content
- Audit UI does not display prompt text
- Audit UI does not display approved memory context text
- Audit UI does not automatically expand selected memory IDs into memory content
- Backend unavailable errors are shown clearly
- Existing backend tests still pass (209 passed) ✅
- No backend API changes are made ✅
- No /chat behavior changes are made ✅
- No Electron IPC is added ✅
- No frontend framework is added ✅

Implementation Summary:
- apps/desktop/src/renderer/index.html: added #audit-section with title, helper text, Refresh button, limit/offset inputs, audit-list container
- apps/desktop/src/renderer/renderer.js: added DOM refs, loadAuditLogs(), renderAuditList(), formatDateTime(), setAuditStatus(); wired refresh button and startup call
- apps/desktop/src/renderer/styles.css: added #audit-section, .audit-card, .audit-card-meta, .audit-controls styles (dark theme)
- README.md: updated feature table to include Audit Logs UI
- docs/TASKS.md: TASK-027 marked DONE
- Static checks: all passed — loadAuditLogs only calls /memory/audit, no ID expansion, no framework, no IPC
- pytest result: 209 passed, 0 failed (no backend changes)

Next Task:
TASK-028 - Audit Inspection Runtime Smoke Check

---

## TASK-028 - Audit Inspection Runtime Smoke Check

Status: DONE

Goal:
Verify that TASK-027's Audit Logs UI works correctly in a full runtime environment (backend + Electron desktop), confirming safe metadata display and no raw memory content exposure.

Scope:
- Run backend pytest suite and confirm all tests pass
- Start uvicorn backend and confirm no startup errors
- Start Electron desktop with npm start and confirm window opens
- Confirm Audit Logs section is visible
- Confirm Refresh Audit Logs button works
- Confirm audit cards display safe metadata fields
- Confirm raw memory content is not exposed in Audit UI
- Confirm /chat still works and does not expose memory content
- Record results in TASKS.md
- Do not modify backend code
- Do not modify Electron UI
- Do not add new features

Acceptance Criteria:
- TASK-027 is marked DONE ✅
- TASK-028 is recorded as DONE ✅
- Backend pytest passed ✅
- Backend uvicorn starts without errors ✅
- Electron window opens via npm start ✅
- Audit Logs section visible in UI ✅
- Refresh Audit Logs button works ✅
- Audit cards display: id, created_at, conversation_id, selected_memory_ids, selected_count, total_context_chars, feature_flag_enabled, exclusion_summary ✅
- Raw memory content not exposed in Audit UI ✅
- selected_memory_ids not auto-expanded into memory content ✅
- Chat still works and returns 200 ✅
- Memory content not exposed in chat reply ✅
- No backend errors during smoke check ✅
- No code changes made ✅

Runtime Smoke Check Results (performed on Windows host):

- Backend pytest: 226 passed, 0 failed
- Backend uvicorn: started successfully, no errors
- Desktop npm start: launched successfully
- Electron window: opened and responsive
- Audit Logs section: visible ✅
- Refresh Audit Logs: pass ✅
- Audit cards rendered: yes ✅
- selected_memory_ids visible: yes — displayed as [3, 2] ✅
- selected_count visible: yes — displayed as 2 ✅
- total_context_chars visible: yes — displayed as 398 ✅
- feature_flag_enabled visible: yes — displayed as true ✅
- exclusion_summary visible: yes — displayed as none ✅
- Raw memory content exposed in Audit UI: no ✅
- selected_memory_ids auto-expanded: no ✅
- POST /chat response: 200 OK ✅
- Chat reply: mock-only, memory content NOT exposed ✅
- Backend errors: none ✅

Screen Observations:
- Audit card shows "Audit #3" with safe metadata only
- Selected IDs displayed as [3, 2] — integer IDs, no content expansion
- Memory list and Context Preview sections still display memory content as expected (separate from Audit UI, not a leak)
- Audit UI is clearly separated from memory management sections
- Chat reply displayed normally without memory content

Two-Layer Gate and Audit Inspection Verdict: PASS — all acceptance criteria met.

Next Task:
TASK-029 - Phase 3 Stabilization and Demo Summary

---

## TASK-029 - Phase 3 Stabilization and Demo Summary

Status: DONE

Goal:
Stabilize documentation after completing the memory-aware chat and audit inspection phase.

Scope:
- Summarize Phase 3 completed capabilities
- Document current runtime status
- Document demo flow
- Document safety boundaries
- Document next recommended phase
- Do not modify runtime code
- Do not add new features

Acceptance Criteria:
- TASK-029 is recorded as DONE ✅
- docs/PHASE3_DEMO_SUMMARY.md exists ✅
- README reflects current completed capabilities ✅
- docs/ROADMAP.md reflects Phase 3 completion status ✅
- docs/ARCHITECTURE.md accurately reflects current memory-aware chat and audit flow ✅
- docs/MEMORY_SYSTEM.md accurately reflects current memory usage, audit logs, and limitations ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- /chat behavior remains unchanged ✅

Implementation Summary:
- docs/PHASE3_DEMO_SUMMARY.md: new file — capabilities table, safety model, demo flow, smoke results, known issues, not-implemented list, Phase 4 recommendations
- README.md: updated status block (Phase 3 complete, 226 passed), added PHASE3_DEMO_SUMMARY.md to docs table
- docs/ROADMAP.md: Phase 3 table updated to all DONE; Phase 4 section updated with candidate options and planning note
- docs/ARCHITECTURE.md: sections 4 (memory-aware chat flow), 6 (toggle), 7 (audit) updated from "future design" to "implemented"
- docs/MEMORY_SYSTEM.md: added Phase 3 Current Implementation Status table at top
- docs/TASKS.md: TASK-029 marked DONE

Next Task:
TASK-030 - Phase 4 Planning

---

## TASK-030 - Phase 4 Planning

Status: DONE

Goal:
Plan the next phase after completing Phase 3 memory-aware chat and audit inspection.

Scope:
- Define Phase 4 candidate tracks
- Compare LLM adapter, TTS, UI polish, daily summary, and packaging
- Recommend one primary Phase 4 path
- Define safety constraints before real AI integration
- Define task sequence for the chosen path
- Do not implement runtime code

Acceptance Criteria:
- TASK-030 is recorded as DONE ✅
- docs/PHASE4_PLAN.md exists ✅
- docs/ROADMAP.md includes Phase 4 proposed sequence (TASK-030 → TASK-037) ✅
- README notes Phase 4 is in planning ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- No runtime behavior changes ✅

Implementation Summary:
- docs/PHASE4_PLAN.md: new file — Phase 3 baseline table, 4 candidate tracks (A: LLM adapter recommended, B: TTS deferred, C: UI polish deferred, D: daily summary deferred), recommendation rationale, 12 Phase 4 safety constraints (API key env-var-only, real provider disabled by default, /chat schema unchanged, no tool execution, no auto memory extraction, etc.), task sequence TASK-031–TASK-037, not-in-scope list
- docs/ROADMAP.md: Phase 4 section updated from "NOT STARTED" to "PLANNING"; candidate options table updated; full TASK-030 to TASK-037 task table added; safety constraints summarized; link to PHASE4_PLAN.md
- README.md: status block updated with Phase 4 planning note; docs table updated to include PHASE4_PLAN.md

Next Task:
TASK-031 - LLM Adapter Design

---

## TASK-031 - LLM Adapter Design

Status: DONE

Goal:
Design a provider-agnostic LLM adapter layer before implementing any real AI provider.

Scope:
- Define LLM adapter purpose
- Define provider interface
- Define mock provider compatibility
- Define real provider safety requirements
- Define environment variable requirements
- Define prompt assembly boundaries
- Define response normalization rules
- Define error handling rules
- Define future task sequence
- Do not implement runtime code

Acceptance Criteria:
- TASK-031 was recorded as IN_PROGRESS during execution ✅
- docs/LLM_ADAPTER_DESIGN.md exists
- docs/ARCHITECTURE.md references future LLM adapter layer
- docs/ROADMAP.md reflects TASK-031 status
- README notes LLM adapter is in design only
- No backend/app code is modified
- No apps/desktop code is modified
- No real AI provider is added
- /chat runtime behavior remains unchanged

Next Task:
TASK-032 - LLM Provider Interface Skeleton

---

## TASK-032 - LLM Provider Interface Skeleton

Status: DONE

Goal:
Create the backend LLM provider interface skeleton and mock provider while keeping runtime behavior mock-only.

Scope:
- Mark TASK-031 as DONE
- Add LLM adapter package
- Define provider-agnostic request/response structures
- Define abstract provider interface
- Add MockLLMProvider
- Add provider factory that returns MockLLMProvider only
- Keep /chat behavior compatible
- Add tests for provider interface and mock provider
- Do not implement real provider
- Do not read API keys
- Do not call external APIs

Acceptance Criteria:
- TASK-031 is marked DONE
- TASK-032 is recorded as IN_PROGRESS
- backend/app/llm package exists
- LLMRequest exists
- LLMResponse exists
- abstract provider interface exists
- MockLLMProvider exists
- provider factory returns MockLLMProvider
- no real provider is implemented
- no API key is read
- no external API call exists
- existing tests pass
- new tests pass
- /chat response schema remains reply/mood/source
- Electron UI is not modified

Next Task:
TASK-033 - Mock Provider Compatibility Tests

---

## TASK-033 - Mock Provider Compatibility Tests

Status: DONE

Goal:
Verify that MockLLMProvider can safely support the existing mock chat behavior before wiring it into chat_service.

Scope:
- Mark TASK-032 as DONE
- Add compatibility tests for MockLLMProvider
- Verify chat modes are supported
- Verify memory_context can be accepted without leaking raw content by default
- Verify state_context can be accepted safely
- Verify provider output can be normalized to existing ChatResponse shape
- Keep /chat route unchanged
- Do not implement real provider
- Do not read API keys
- Do not call external APIs

Acceptance Criteria:
- TASK-032 is marked DONE
- TASK-033 was recorded as IN_PROGRESS during execution
- MockLLMProvider supports casual/project/debug/support/reminder modes
- MockLLMProvider accepts memory_context without crashing
- MockLLMProvider does not expose raw memory_context unless explicitly designed for a test-safe placeholder
- MockLLMProvider accepts state_context without crashing
- MockLLMProvider output can map to reply/mood/source compatibility
- get_llm_provider still returns MockLLMProvider
- /chat behavior remains unchanged
- Existing tests pass
- New compatibility tests pass
- No real provider is implemented
- No API key is read
- No external API call exists
- Electron UI is not modified

Next Task:
TASK-034 - Real Provider Config Design

---

## TASK-034 - Real Provider Config Design

Status: DONE

Goal:
Design the configuration and safety rules for future real LLM provider integration without implementing or calling any real provider.

Scope:
- Mark TASK-033 as DONE
- Define real provider environment variables
- Define safe API key handling rules
- Define provider enablement rules
- Define fallback behavior
- Define timeout and error handling config
- Define logging restrictions
- Define future implementation requirements
- Do not implement runtime config
- Do not read API keys
- Do not call external APIs

Acceptance Criteria:
- TASK-033 is marked DONE
- TASK-034 is recorded as IN_PROGRESS
- docs/LLM_ADAPTER_DESIGN.md includes Real Provider Config Design section
- docs/ARCHITECTURE.md references future real provider config boundaries
- docs/ROADMAP.md reflects TASK-034 status
- README notes real provider config is designed but not implemented
- No backend/app code is modified
- No apps/desktop code is modified
- No real provider is implemented
- No API key is read
- No external API call exists
- /chat runtime behavior remains unchanged

Next Task:
TASK-034R - Real Provider Config Safety Review

---

## TASK-034R - Real Provider Config Safety Review

Status: DONE

Goal:
Independent safety review of the real provider config design (TASK-034) before any real provider implementation begins.

Scope:
- Review docs/LLM_ADAPTER_DESIGN.md for config rule correctness, clarity, and completeness
- Identify ambiguous, duplicated, or missing rules
- Flag any security gaps
- Produce a verdict and a list of required fixes
- Do not implement runtime code

Review Verdict: PASS WITH CHANGES

Required fixes (to be applied in TASK-034F):
1. docs/ARCHITECTURE.md and docs/ROADMAP.md are 0 bytes in working tree — restore required
2. TASK-034 still marked IN_PROGRESS in TASKS.md — mark DONE
3. Duplicated real provider config rules in LLM_ADAPTER_DESIGN.md — reconcile to single canonical section
4. Unknown provider behavior ambiguous — fix: must fall back to MockProvider + non-sensitive warning
5. .env.example missing LLM provider env vars — add all six flags
6. Canonical safe fallback text not defined — add single canonical string
7. Provider resolved visibility not required — add requirement (startup log or /health field)
8. No automatic retry rule not documented — add explicit no-retry rule
9. Redaction utility requirement missing — add design requirement for TASK-035
10. Logging forbidden fields incomplete — add user_message, conversation_history, state_context, LLMResponse.text
11. API key redaction rules incomplete — add provider repr/str redaction; caplog/stdout/stderr test requirements
12. Non-2xx provider response body handling not specified — add opaque treatment rule
13. MemoryInjectionAudit / provider observability boundary not specified — add rule

Next Task:
TASK-034F - Apply Real Provider Config Review Fixes

---

## TASK-034F - Apply Real Provider Config Review Fixes

Status: DONE

Goal:
Apply all fixes from TASK-034R Opus review to docs and .env.example before TASK-035 can begin.

Scope:
- Restore docs/ARCHITECTURE.md (currently 0 bytes)
- Restore docs/ROADMAP.md (currently 0 bytes)
- Reconcile duplicated real provider config rules in LLM_ADAPTER_DESIGN.md
- Fix unknown provider behavior to single deterministic rule
- Update .env.example with all LLM provider env vars
- Add canonical safe fallback text
- Add provider visibility requirement
- Add no automatic retry rule
- Add redaction utility requirement
- Strengthen logging forbidden fields
- Strengthen API key redaction rules
- Add non-2xx response body opaque treatment rule
- Add MemoryInjectionAudit / provider observability boundary rule
- Mark TASK-034 as DONE in TASKS.md
- Do not implement runtime code

Acceptance Criteria:
- TASK-034R review result is recorded ✅
- TASK-034F is marked DONE ✅
- docs/ARCHITECTURE.md is not empty and includes real provider config boundaries ✅
- docs/ROADMAP.md is not empty and reflects TASK-034/TASK-034R/TASK-034F status ✅
- TASK-034 is marked DONE ✅
- docs/LLM_ADAPTER_DESIGN.md has one canonical provider config section ✅
- Unknown provider behavior is deterministic (fallback to mock + warning) ✅
- .env.example includes LLM_PROVIDER_ENABLED, LLM_PROVIDER_NAME, LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT_SECONDS, LLM_FALLBACK_TO_MOCK ✅
- Canonical safe fallback text is defined ✅
- Provider visibility requirement is documented ✅
- No automatic retries rule is documented ✅
- Redaction utility requirement is documented ✅
- Logging forbidden fields include user_message, conversation_history, state_context, LLMResponse.text ✅
- API key redaction rules include provider repr/str redaction ✅
- Non-2xx provider response bodies are documented as opaque ✅
- TASK-035 remains not started ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅

Implementation Summary:
- docs/ARCHITECTURE.md: restored from 0 bytes — full architecture with LLM adapter layer (Section 4), real provider config boundaries (Sections 4.2–4.8), safety boundaries, data flows
- docs/ROADMAP.md: restored from 0 bytes — Phase 0–5 with Phase 4 task table including TASK-034R and TASK-034F, safety constraints summary
- docs/LLM_ADAPTER_DESIGN.md: document header updated; old Section 5.2 memory gate renumbered to 5.8; Sections 5.2–5.7 added (canonical env var table, provider matrix, canonical fallback text, no-retry, provider visibility, redaction utility); duplicate embedded "Real Provider Config Design" section replaced with single reference note; Section 7.2 (normalization) updated with canonical fallback text ref, non-2xx opaque rule, LLMResponse.text log ban; Sections 8.3–8.5 added (non-2xx opaque, no retries, what must never happen); Section 9 testing updated with caplog/repr/non-2xx tests; Section 10 security expanded with 9 new boundary rows; Section 11 task sequence updated with TASK-034R and TASK-034F rows
- .env.example: LLM provider section added with all 6 env vars and inline safety annotations
- README.md: status block updated with review chain; LLM_ADAPTER_DESIGN.md docs table entry updated
- backend/README.md: real provider config paragraph updated with TASK-034R verdict, TASK-034F blocker, new safety rules (repr/str, no retry, non-2xx opaque)

Next Task:
TASK-035 - Real Provider Integration Behind Feature Flag

---

## TASK-035 - Real Provider Integration Behind Feature Flag

Status: DONE

Goal:
Implement a first real LLM provider adapter behind disabled-by-default feature flags, with mocked HTTP tests only and strict key redaction.

Scope:

- Add real provider config helpers
- Add redaction helper
- Add provider visibility helper
- Add one real provider adapter behind feature flag
- Update provider factory to select MockProvider or real provider safely
- Add tests for config, redaction, factory, fallback, and mocked provider HTTP behavior
- Keep /chat response schema unchanged
- Do not modify Electron UI
- Do not run live external API calls in tests

Acceptance Criteria:

- TASK-035 is marked DONE
- LLM_PROVIDER_ENABLED defaults False
- LLM_PROVIDER_NAME defaults mock
- Unknown provider falls back to MockProvider with non-sensitive warning
- Missing API key falls back to MockProvider when fallback enabled
- Missing API key returns canonical safe fallback behavior when fallback disabled
- API key is backend env only
- API key is never logged
- API key is never returned in responses
- API key is never stored in DB or audit rows
- Provider **repr** / **str** redacts secrets
- No automatic retries are implemented
- Non-2xx provider response bodies are treated as opaque
- Tests use mocked HTTP only
- /chat response schema remains reply/mood/source
- Existing tests pass
- New tests pass
- No Electron UI changes are made

Implementation Summary:

- Config helpers added for LLM provider env vars
- Redaction helpers added for secrets and secret-like text
- Provider visibility helper added with non-sensitive resolved provider info
- HTTPRealLLMProvider added as a mockable transport contract
- SafeFallbackLLMProvider added for canonical safe fallback behavior
- Provider factory updated for flag-disabled, mock, unknown provider, missing key, and real provider selection
- Automated tests use fake HTTP client / mocked transport only
- No live external API calls in automated tests
- /chat is not wired to the real provider in TASK-035
- /chat response schema remains reply / mood / source
- API key is read only from backend env when real provider is explicitly enabled
- API key is not written to logs, DB, responses, audit rows, or frontend
- Non-2xx provider response bodies are treated as opaque
- No automatic retries are implemented
- pytest result: 301 passed
- Actual vendor request / response format is not finalized and should be handled in the next design task

Next Task:
TASK-036 - Real Provider Vendor Contract Design

---

## TASK-036 - Real Provider Vendor Contract Design

Status: DONE

Goal:
Define the first real provider request/response contract before any live runtime smoke check.

Scope:

- Select the first real provider target
- Define request format
- Define response parsing rules
- Define error mapping rules
- Define timeout behavior
- Define mocked HTTP fixture requirements
- Define manual live smoke procedure
- Do not call real provider
- Do not implement runtime code

Acceptance Criteria:

- TASK-036 is marked DONE
- docs/LLM_PROVIDER_CONTRACT.md exists
- First target provider is selected
- Request format is documented
- Response parsing rules are documented
- Error handling and fallback rules are documented
- Mocked HTTP test fixture plan is documented
- Manual live smoke checklist is documented
- No backend/app code is modified
- No apps/desktop code is modified
- No external API is called

Implementation Summary:

- First target provider selected: Anthropic Claude Messages API
- Request contract documented: POST /v1/messages, x-api-key, anthropic-version, JSON body with model/max_tokens/system/messages
- Response parsing documented: text blocks normalize to LLMResponse.text, model/usage internal only
- Error mapping documented for auth failure, rate limit, timeout, network failure, non-2xx, malformed response, and empty text
- Mocked HTTP fixture plan documented for TASK-037
- Manual live smoke checklist documented for TASK-038
- No backend/app code was modified in TASK-036
- No apps/desktop code was modified in TASK-036
- No external API was called in TASK-036

Next Task:
TASK-037 - Real Provider Contract Tests

---

## TASK-037 - Real Provider Contract Tests

Status: DONE

Goal:
Verify the first real provider contract using mocked HTTP tests only, without live external API calls.

Scope:

- Mark TASK-036 as DONE
- Add mocked HTTP contract tests for Anthropic Messages API
- Verify request method, endpoint, headers, and body
- Verify response parsing
- Verify error mapping
- Verify opaque non-2xx bodies
- Verify timeout behavior
- Verify no retries
- Verify no API key leakage
- Keep /chat unchanged
- Do not run live provider calls

Acceptance Criteria:

- TASK-036 is marked DONE
- TASK-037 is marked DONE
- Contract tests verify POST /v1/messages
- Contract tests verify x-api-key header is used
- Contract tests verify anthropic-version header is used
- Contract tests verify request body includes model/max_tokens/system/messages
- Contract tests verify stream/tools are not included
- Success fixture parses text from content blocks
- Usage is parsed internally if supported
- Non-2xx fixture body remains opaque
- Timeout fixture returns safe error
- Malformed JSON fixture returns safe error
- Empty text fixture returns safe error
- Rate limit fixture maps safely
- Auth failure fixture maps safely
- No retries occur
- API key does not appear in logs, response text, repr, str, stdout, stderr
- Existing tests pass
- No live external API calls occur
- /chat behavior remains unchanged
- Electron UI is not modified

Implementation Summary:

- Anthropic Messages API contract verified with mocked HTTP tests
- Contract tests verify POST /v1/messages
- Contract tests verify x-api-key header
- Contract tests verify anthropic-version header
- Contract tests verify request body includes model / max_tokens / system / messages
- Contract tests verify request body does not include stream / tools
- Success response parsing verified from content text blocks
- Non-text content blocks ignored safely
- Usage retained internally when present
- Error mapping verified:
  - 401/403 -> provider_auth_error
  - 429 -> rate_limit
  - 500 -> provider_error
  - malformed JSON / empty text -> invalid_response
  - timeout -> provider_timeout
  - network failure -> provider_unavailable
- Non-2xx provider body remains opaque
- No retries occur
- API key does not appear in caplog / stdout / stderr / response / repr / str
- Raw body / prompt / user message / memory context do not appear in logs or response
- Automated tests used mocked HTTP only
- No live external API calls occurred in automated tests
- /chat is still not wired to the real provider
- /chat behavior remains unchanged
- Electron UI was not modified
- pytest result: 317 passed

Next Task:
TASK-038 - Manual Live LLM Provider Smoke Check

---

## TASK-038 - Manual Live LLM Provider Smoke Check

Status: IN_PROGRESS

Goal:
Manually verify the real provider adapter with one live minimal request after explicit user opt-in and cost acknowledgement.

Scope:

- Confirm user has a valid API key
- Confirm user accepts cost risk
- Set backend env vars manually
- Run one minimal provider adapter request
- Verify response normalizes into LLMResponse
- Verify no API key appears in logs / stdout / stderr
- Verify no memory is used
- Verify no /chat wiring is changed
- Clear env vars after test
- Do not add live API calls to automated tests

Acceptance Criteria:

- TASK-038 is recorded as IN_PROGRESS
- User explicitly confirms cost risk before live call
- Live call is manual only
- Automated pytest remains mocked-only
- API key is set only in local backend shell env
- API key is not committed
- Provider returns a non-empty response or safe error
- No API key appears in visible output
- No memory context is sent
- /chat remains not wired to real provider
- Electron UI is not modified
- Env vars are cleared after test

Manual Smoke Checklist:

1. User explicitly confirms:
   - I have an Anthropic API key
   - I understand this may cost money
   - I want to run exactly one minimal live request
2. Set env vars in backend PowerShell:
   - `LLM_PROVIDER_ENABLED=true`
   - `LLM_PROVIDER_NAME=anthropic`
   - `LLM_API_KEY=<real key, not committed>`
   - `LLM_MODEL=<chosen Claude model>`
   - `LLM_TIMEOUT_SECONDS=30`
   - `LLM_FALLBACK_TO_MOCK=true`
3. Run provider adapter only, not `/chat`.
4. Confirm:
   - response text non-empty OR safe fallback returned
   - no API key printed
   - no raw provider body printed
   - no memory context used
   - no DB/audit row created by this adapter-only smoke
5. Clear env vars after test.

Run Boundary:

- Do not create a permanent script unless absolutely necessary
- Temporary commands must not print API key
- Do not commit local keys
- Do not add keys to `.env.example`
- If the user does not confirm key availability and cost risk, stop before the live call

Next Task:
TASK-039 - Chat Service LLM Wiring Design

---

## TASK-039 - Chat Service LLM Wiring Design

Status: DONE

Goal:
Design how chat_service will safely use the LLM adapter while keeping /chat schema stable and preserving mock fallback.

Scope:

- Define chat_service to LLM adapter flow
- Define feature flags required for /chat LLM use
- Define prompt assembly sequence
- Define memory-aware interaction
- Define provider fallback behavior
- Define audit and logging rules
- Define test plan for future wiring
- Do not implement runtime code
- Do not call real provider

Acceptance Criteria:

- TASK-039 is marked DONE
- docs/CHAT_LLM_WIRING_DESIGN.md exists
- /chat response schema preservation is documented
- mock fallback behavior is documented
- memory-aware interaction is documented
- logging restrictions are documented
- future tests are listed
- No backend/app code is modified
- No apps/desktop code is modified
- No external API call is made

Implementation Summary:

- docs/CHAT_LLM_WIRING_DESIGN.md added
- LLM_CHAT_ENABLED design documented as separate /chat LLM adapter gate
- /chat response schema preservation documented
- mock fallback behavior documented
- memory-aware interaction documented
- logging restrictions documented
- future tests listed for TASK-040
- No backend/app code was modified in TASK-039
- No apps/desktop code was modified in TASK-039
- No external API call was made in TASK-039

Next Task:
TASK-040 - Chat Service LLM Wiring Behind Feature Flag

---

## TASK-040 - Chat Service LLM Wiring Behind Feature Flag

Status: DONE

Goal:
Wire chat_service to the LLM adapter behind LLM_CHAT_ENABLED while preserving default mock behavior.

Scope:

- Mark TASK-039 as DONE
- Add LLM_CHAT_ENABLED config helper
- Keep LLM_CHAT_ENABLED default False
- When LLM_CHAT_ENABLED=false, /chat uses existing mock flow
- When LLM_CHAT_ENABLED=true, /chat may use LLM adapter
- Preserve /chat response schema reply/mood/source
- Preserve memory gate independence
- Add tests for disabled and enabled paths
- Use mocked providers / mocked HTTP only
- Do not modify Electron UI
- Do not run live provider calls

Acceptance Criteria:

- TASK-039 is marked DONE
- TASK-040 is marked DONE
- LLM_CHAT_ENABLED exists
- LLM_CHAT_ENABLED defaults False
- With LLM_CHAT_ENABLED=false:
  - old /chat request still returns 200
  - /chat response schema remains reply/mood/source
  - existing mock flow remains active
  - no LLM provider call occurs
- With LLM_CHAT_ENABLED=true and provider mock:
  - /chat returns 200
  - /chat uses LLM adapter MockLLMProvider
  - response schema remains reply/mood/source
  - source can indicate llm_mock
- With LLM_CHAT_ENABLED=true and real provider selected:
  - tests use mocked HTTP only
  - /chat returns 200
  - source can indicate llm_real
  - no raw provider response exposed
- Memory gates remain independent
- API key does not appear in logs/responses
- Existing tests pass
- New tests pass
- No Electron UI changes are made
- No live external API calls occur

Implementation Notes:

- `LLM_CHAT_ENABLED` config helper added, default False
- `generate_chat_reply()` added in chat_service while preserving `generate_mock_chat_reply()`
- `/chat` uses existing mock flow when `LLM_CHAT_ENABLED=false`
- `/chat` can use LLM adapter MockLLMProvider when `LLM_CHAT_ENABLED=true` and provider resolves to mock
- `/chat` can use a mocked real provider path in tests when `LLM_CHAT_ENABLED=true`
- Memory gates remain independent from LLM chat gate
- Automated tests use mocked providers / mocked HTTP only
- Electron UI was not modified
- pytest result: 342 passed

Next Task:
TASK-041 - Chat LLM Wiring Mock Runtime Smoke Check

---

## TASK-041 - Chat LLM Wiring Mock Runtime Smoke Check

Status: DONE

Goal:
Verify the chat LLM wiring paths at runtime with mock-only configuration, without live external API calls.

Scope:

- Confirm TASK-040 remains DONE
- Run mock runtime smoke checks for `/chat`
- Verify `LLM_CHAT_ENABLED=false` keeps existing mock flow
- Verify `LLM_CHAT_ENABLED=true` with provider disabled uses LLM adapter mock path
- Verify `/chat` response schema remains `reply` / `mood` / `source`
- Verify memory content is not exposed in chat reply
- Do not modify Electron UI
- Do not run live provider calls

Acceptance Criteria:

- TASK-040 is marked DONE
- TASK-041 is recorded as DONE
- `pytest` passes
- `LLM_CHAT_ENABLED=false` `/chat` returns 200
- `LLM_CHAT_ENABLED=false` response schema remains `reply` / `mood` / `source`
- `LLM_CHAT_ENABLED=false` actual source is `mock`
- `LLM_CHAT_ENABLED=true` with `LLM_PROVIDER_ENABLED=false` `/chat` returns 200
- `LLM_CHAT_ENABLED=true` with `LLM_PROVIDER_ENABLED=false` response schema remains `reply` / `mood` / `source`
- `LLM_CHAT_ENABLED=true` with `LLM_PROVIDER_ENABLED=false` actual source is `llm_mock`
- Memory content is not exposed in chat reply
- No backend errors occurred
- No live external API call occurred
- Electron UI was not modified
- `/chat` schema remained unchanged

Runtime Smoke Result:

- pytest: pass, 342 passed
- `LLM_CHAT_ENABLED=false`:
  - `/chat` returned 200
  - response schema remained `reply` / `mood` / `source`
  - actual source: `mock`
  - backend errors: no
- `LLM_CHAT_ENABLED=true` + `LLM_PROVIDER_ENABLED=false`:
  - `/chat` returned 200
  - response schema remained `reply` / `mood` / `source`
  - actual source: `llm_mock`
  - backend errors: no
- Memory content was not exposed in chat reply
- No live external API call occurred
- Electron UI was not modified
- `/chat` schema remained unchanged

Next Task:
TASK-042 - Chat LLM Real Provider Wiring Design

---

## TASK-042 - Chat LLM Real Provider Wiring Design

Status: DONE

Goal:
Design how /chat will safely use the real provider path after mock LLM wiring has been verified.

Scope:

- Define real provider /chat wiring conditions
- Define required feature flag combinations
- Define source value behavior
- Define provider fallback behavior
- Define memory gate independence
- Define logging and redaction requirements
- Define manual live smoke prerequisites
- Do not implement runtime code
- Do not call real provider

Acceptance Criteria:

- TASK-042 is marked DONE
- docs/CHAT_LLM_REAL_PROVIDER_WIRING_DESIGN.md exists
- Required flag matrix is documented
- /chat response schema preservation is documented
- source behavior is documented
- fallback behavior is documented
- memory independence is documented
- logging restrictions are documented
- manual live smoke prerequisites are documented
- No backend/app code is modified
- No apps/desktop code is modified
- No external API call is made

Implementation Summary:

- `docs/CHAT_LLM_REAL_PROVIDER_WIRING_DESIGN.md` was added
- This task was design-only
- `/chat` future real provider path safety conditions were defined
- Feature flag matrix was defined
- source behavior was defined for `mock`, `llm_mock`, and `llm_real`
- fallback behavior must not pretend to be `llm_real`
- provider failure / fallback behavior was defined
- memory gate independence was defined
- logging / redaction restrictions were defined
- manual live smoke prerequisites were defined
- No backend/app code was modified
- No apps/desktop code was modified
- No external API call was made
- No runtime code was modified

Next Task:
TASK-043 - Chat Real Provider Wiring Contract Tests

---

## TASK-043 - Chat Real Provider Wiring Contract Tests

Status: DONE

Goal:
Verify /chat real-provider wiring behavior using mocked providers and mocked HTTP only.

Scope:

- Mark TASK-042 as DONE
- Add tests for /chat flag matrix
- Add tests for source behavior
- Add tests for real provider success path with mocked HTTP
- Add tests for real provider fallback path with mocked HTTP
- Verify no raw provider body is exposed
- Verify no API key is exposed
- Verify memory gate independence
- Keep Electron UI unchanged
- Do not run live provider calls

Acceptance Criteria:

- TASK-043 is marked DONE
- /chat old mock path still works
- /chat llm_mock path still works
- /chat real provider mocked success path returns 200
- /chat real provider mocked success source is llm_real
- /chat real provider fallback does not claim llm_real
- /chat response schema remains reply/mood/source
- API key does not appear in response/logs
- raw provider response body does not appear in response/logs
- user_message and memory_context are not logged
- LLM flags do not enable memory
- Memory flags do not enable LLM
- Memory audit remains memory-scoped
- Existing tests pass
- New tests pass
- No live external API calls occur
- Electron UI is not modified

Implementation Notes:

- Added mocked-only `/chat` real-provider wiring contract tests
- Flag matrix tests cover disabled chat, provider disabled, provider mock, unknown provider, missing key fallback true, missing key fallback false, and Anthropic key-present mocked success
- Source behavior tests verify `mock`, `llm_mock`, `llm_real`, and `llm_real_error`
- Real provider fallback no longer claims `llm_real`
- API key, raw provider body, user_message, prompt text, and memory_context are not exposed in response/log assertions
- Memory gate independence tests verify LLM flags do not create memory audit and memory flags do not enable LLM
- All real-provider route tests use fake HTTP transport / mocked provider behavior only
- No live external API calls occurred
- Electron UI was not modified
- /chat response schema remained reply / mood / source
- pytest result: 356 passed
- Production database was not polluted

Next Task:
TASK-044 - Cost Control and Live Smoke Go/No-Go Design

---

## TASK-044 - Cost Control and Live Smoke Go/No-Go Design

Status: DONE

Goal:
Define cost controls and go/no-go criteria before running any live LLM smoke test.

Scope:

- Estimate cost risks for long-running cloud LLM use
- Define cost control strategy
- Define live smoke go/no-go checklist
- Define monetization/product positioning options
- Decide whether live smoke should proceed now or be deferred
- Do not call real provider
- Do not implement runtime code

Acceptance Criteria:

- TASK-044 is marked DONE
- docs/COST_AND_MONETIZATION.md exists
- docs/LLM_PROVIDER_CONTRACT.md includes live smoke cost warning
- README notes live provider remains disabled pending cost decision
- Manual live smoke remains deferred until explicit user confirmation
- No backend/app code is modified
- No apps/desktop code is modified
- No external API call is made

Implementation Summary:

- This task was design-only
- docs/COST_AND_MONETIZATION.md was added
- Always-on cloud LLM cost risk was documented
- Cost drivers were documented
- Cost control strategy was documented
- Product positioning options were compared:
  - portfolio/demo
  - personal local companion
  - BYOK desktop app
  - subscription SaaS
  - credit-based model
  - hybrid local/cloud model
- Recommended product direction: BYOK first
- Short-term direction: portfolio/demo + personal use
- Cloud subscription should wait until real usage data exists
- Unlimited free cloud LLM is not recommended
- Live smoke remains deferred until explicit user cost confirmation
- Manual Live Chat LLM Smoke Check remains paused and is not IN_PROGRESS
- No backend/app code was modified
- No apps/desktop code was modified
- No external API call was made
- No runtime code was modified

Next Task:
TASK-045 - BYOK Product and Settings Design

Deferred Task:
Manual Live Chat LLM Smoke Check remains paused until explicit user cost confirmation.

---

## TASK-045 - BYOK Product and Settings Design

Status: DONE

Goal:
Design the BYOK product model and settings safety rules before implementing any provider settings UI.

Scope:

- Define BYOK product positioning
- Define API key ownership model
- Define safe settings UX
- Define backend-only key handling rules
- Define local storage options and risks
- Define provider selection UX
- Define usage/cost warnings
- Define future implementation sequence
- Do not implement runtime code
- Do not read API keys
- Do not call external APIs

Acceptance Criteria:

- TASK-045 is recorded as IN_PROGRESS
- docs/BYOK_PRODUCT_AND_SETTINGS.md exists
- BYOK product model is documented
- API key ownership and responsibility are documented
- API key storage options are compared
- Recommended MVP key handling approach is documented
- Settings UI requirements are documented
- Cost warning UX is documented
- Provider selection rules are documented
- Security boundaries are documented
- Manual live smoke remains deferred
- No backend/app code is modified
- No apps/desktop code is modified
- No external API call is made

Next Task:
TASK-046 - Usage Meter Design

---

## TASK-046 - Usage Meter Design

Status: DONE

Goal:
Design usage and cost visibility before implementing BYOK provider settings or broader real provider usage.

Scope:
- Define what usage data should be tracked
- Define estimated token/cost display rules
- Define provider/model visibility
- Define session/day counters
- Define quota warning UX
- Define privacy boundaries
- Define future implementation sequence
- Do not implement runtime code
- Do not call external APIs

Acceptance Criteria:
- TASK-046 is recorded as DONE ✅
- docs/USAGE_METER_DESIGN.md exists ✅
- Usage tracking fields are documented (14 fields, Section 2) ✅
- Estimated cost display rules are documented (Section 5) ✅
- Provider/model visibility rules are documented (Section 6) ✅
- Privacy and logging boundaries are documented (Section 8) ✅
- UI requirements are documented (Section 6) ✅
- Future implementation sequence is documented (Section 11) ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- No external API call is made ✅

Completion Notes:
- docs/USAGE_METER_DESIGN.md created: 12 sections covering tracking fields, token/cost estimation rules, UI requirements, warning UX, privacy boundaries, storage options, BYOK interaction, and implementation sequence
- What to track: 14 fields including request_count, provider, model, source, estimated tokens, cost, timestamp, memory flags, fallback flag, error category
- What not to track: API key, raw prompt, raw user message, raw memory context, raw provider response, system prompt
- Token estimation: prefer provider-reported; local heuristic labeled as estimate; CJK noted; never present as exact billing
- Cost estimation: pricing table required; MVP default tokens-only; approximate label required; provider dashboard is truth
- Storage: MVP Phase 1 in-memory session counters; Phase 2 optional SQLite daily rollup; no raw content stored; user-deletable
- Usage meter (TASK-050) must be ready before BYOK settings (TASK-051)

Next Task:
TASK-047 - Provider Settings UI Design

---

## TASK-047 - Provider Settings UI Design

Status: DONE

Goal:
Design the provider settings user interface for the desktop app. Document how users will configure their API key, select a provider, set model preferences, and view usage summaries. No runtime code, no backend/app changes, no apps/desktop changes.

Scope:
- Create docs/PROVIDER_SETTINGS_UI_DESIGN.md
- Document UI sections: provider selector, API key input, model selection, safety toggles, cost warning, usage meter placement, test connection
- Document settings flow (step-by-step interaction)
- Document security boundaries for settings UI
- Document error UX (7 error types, safe text only)
- Document memory interaction note
- Document non-goals
- Document future implementation sequence (TASK-048 through TASK-052)
- Update docs/BYOK_PRODUCT_AND_SETTINGS.md: note that Provider Settings UI design now exists separately; UI must be backend-mediated; usage meter visible near provider settings
- Update docs/USAGE_METER_DESIGN.md: note Provider Settings UI should include usage meter summary; provider dashboard is billing source of truth
- Update docs/ROADMAP.md: TASK-047 IN_PROGRESS (was Pending), verify TASK-046 DONE
- Update README.md: note Provider Settings UI is in design; no settings UI implemented yet; API keys remain env-only during dev phase
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests
- Do not add APIs
- Do not read or use API keys
- Do not call external APIs
- Do not implement settings UI

Acceptance Criteria:
- TASK-046 is marked DONE ✅
- TASK-047 is recorded as DONE ✅
- docs/PROVIDER_SETTINGS_UI_DESIGN.md exists ✅
- UI sections are documented (7 sections: provider selector, API key input, model selection, safety toggles, cost warning, usage meter summary, test connection) ✅
- Settings flow is documented (9-step interaction flow) ✅
- Security boundaries are documented (12 rules) ✅
- Error UX is documented (7 error types, safe text only) ✅
- Memory interaction note is included ✅
- Non-goals section exists ✅
- Future implementation sequence (TASK-048 through TASK-052) is documented ✅
- docs/BYOK_PRODUCT_AND_SETTINGS.md updated with Provider Settings UI design reference ✅
- docs/USAGE_METER_DESIGN.md updated with Provider Settings UI placement note ✅
- docs/ROADMAP.md updated: TASK-047 IN_PROGRESS → DONE, TASK-046 DONE ✅
- README.md updated with provider settings design status note ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- No external API call is made ✅

Completion Notes:
- This was a design-only task. No runtime code was written or modified.
- docs/PROVIDER_SETTINGS_UI_DESIGN.md created: 9 sections covering UI sections, 9-step settings flow, security boundaries, error UX, memory interaction, non-goals, implementation sequence, and relationship to existing documents.
- UI design key decisions:
  - Settings UI must never directly call provider from frontend — all operations backend-mediated
  - API key write-once from UI perspective: never retrieved, never shown after save
  - Test Connection requires explicit user action and confirmation dialog — never automatic, no retries
  - Usage meter summary embedded in Provider Settings panel (primary placement per TASK-046 Section 6.3)
  - Cost warning is non-dismissable when real provider is selected
  - Safety toggles (LLM flags) are read-only status displays in Phase 4 — not interactive
  - 7 error types handled with safe user-facing text only — no HTTP codes, no raw error bodies
- No backend/app was modified
- No apps/desktop was modified
- No tests were added
- No APIs were added
- No external API was called

Next Task:
TASK-048 - Backend Provider Settings API Design

---

## TASK-048 - Backend Provider Settings API Design

Status: DONE

Goal:
Design backend APIs for future BYOK provider settings without implementing them. This document defines the API surface, request/response schemas, key handling rules, and security boundaries that will guide future implementation.

Scope:
- Define backend provider settings API surface
- Define safe request/response schemas
- Define API key write-only behavior
- Define key clear behavior
- Define provider status behavior
- Define manual test connection behavior
- Define usage meter integration points
- Define security boundaries
- Do not implement runtime code
- Do not read API keys
- Do not call external APIs

Acceptance Criteria:
- TASK-047 is marked DONE ✅
- TASK-048 is recorded as DONE ✅
- docs/PROVIDER_SETTINGS_API_DESIGN.md exists ✅
- Backend API endpoints are documented (GET/PATCH /provider/settings, POST /provider/settings/key, DELETE /provider/settings/key, POST /provider/settings/test) ✅
- Request and response schemas are documented ✅
- API key write-only behavior is documented ✅
- API key clear behavior is documented (DELETE endpoint, idempotent) ✅
- Test connection behavior is documented (explicit_cost_ack required, no retries, no auto-trigger) ✅
- Provider status behavior (safe status model: not_configured / configured / invalid / not_tested / test_success / test_failed) is documented ✅
- Usage meter integration points are documented ✅
- Security boundaries are documented (11 rules) ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- No external API call is made ✅

Completion Notes:
- This was a design-only task. No runtime code was written or modified.
- docs/PROVIDER_SETTINGS_API_DESIGN.md created: 12 sections covering proposed endpoints, API key handling rules, safe status model, test connection safety, usage meter integration, error handling, security boundaries, non-goals, and future implementation sequence.
- Endpoints designed: GET /provider/settings, PATCH /provider/settings, POST /provider/settings/key, DELETE /provider/settings/key, POST /provider/settings/test
- API key write-only: accepted only at POST /provider/settings/key; never returned from any endpoint; never logged; never in SQLite until TASK-049 secure storage design is complete
- Test connection: explicit_cost_ack: true is mandatory (backend-enforced); exactly one minimal request; no retry; no auto-trigger on load/save/start; does not write to chat history or MemoryInjectionAudit
- Safe status model: not_configured / configured / invalid / not_tested / test_success / test_failed — no key fragments in any status value
- Error handling: 11 safe error categories, no raw provider body forwarded
- POST /provider/settings/key implementation must not begin until TASK-049 (Secure Key Storage Design) is complete
- No backend/app was modified
- No apps/desktop was modified
- No tests were added
- No APIs were added
- No external API was called

Next Task:
TASK-049 - Secure Key Storage Design

---

## TASK-049 - Secure Key Storage Design

Status: DONE

Goal:
Design secure local API key storage for future BYOK provider settings. Compare storage options, define the recommended MVP path, define the future desktop path, and document key lifecycle, redaction rules, and API dependency constraints. No runtime code is written.

Scope:
- Compare key storage options (env var, OS keychain, encrypted file, plain SQLite)
- Define recommended MVP storage path
- Define future desktop secure storage path
- Define deletion / rotation behavior
- Define logging and redaction requirements
- Define API dependency constraints
- Define implementation sequence
- Do not implement runtime code
- Do not read API keys
- Do not call external APIs

Acceptance Criteria:
- TASK-048 is marked DONE ✅
- TASK-049 is recorded as DONE ✅
- docs/SECURE_KEY_STORAGE_DESIGN.md exists ✅
- Storage options are compared (4 options: env var, OS keychain, encrypted file, plain SQLite) ✅
- MVP recommendation is documented (Environment Variable Only for dev phase) ✅
- Future desktop recommendation is documented (OS Keychain / Credential Manager) ✅
- Deletion and rotation behavior are documented (key lifecycle: add, replace, clear, test, rotate, uninstall, debug export) ✅
- API key redaction rules are documented (logs, exceptions, repr/str, stdout/stderr, exports, DB, audit logs) ✅
- Provider Settings API dependency is documented (POST /provider/settings/key blocked until TASK-053) ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- No external API call is made ✅

Completion Notes:
- This was a design-only task. No runtime code was written or modified.
- docs/SECURE_KEY_STORAGE_DESIGN.md created: 14 sections covering storage options, recommendation, MVP strategy, key lifecycle, API integration rules, key status model, redaction rules, testing requirements, threat model, and future implementation sequence.
- Dev phase storage recommendation: Environment Variable Only (Option A). No persistent key storage. Key set via shell env before backend start.
- Future production desktop recommendation: OS Keychain / Credential Manager (Option B). Windows Credential Manager, macOS Keychain, Linux libsecret. Implemented via Python keyring library.
- Explicitly forbidden: Plain SQLite / plain config file for real API keys — unacceptable leakage risk via backups, screenshots, debug exports.
- Key lifecycle defined: Add → Replace (overwrites old secret) → Clear (idempotent) → Test (explicit_cost_ack required) → Rotate (same as Replace in Phase 4) → App Uninstall (OS keychain entries not auto-removed; user must be informed) → Debug Export (must exclude key-adjacent fields).
- Threat model documented: accidental git commit, log exposure, frontend renderer exposure, local DB leakage, debug export leakage, malicious local user, malware, OS account compromise. Local malware and OS account compromise are accepted residual risks at the app layer.
- Adjusted implementation sequence: TASK-053 (Secure Key Storage Implementation) must precede TASK-051 (Backend Provider Settings API Implementation).
- No backend/app was modified
- No apps/desktop was modified
- No tests were added
- No APIs were added
- No external API was called

Next Task:
TASK-050 - Usage Meter Implementation

---

## TASK-050 - Usage Meter Implementation

Status: DONE

Goal:
Implement a minimal in-memory usage meter for safe session-level usage visibility. Track only safe aggregate metadata. Never store raw messages, prompts, memory context, provider response bodies, or API keys.

Scope:
- Add in-memory usage meter service (backend/app/services/usage_meter_service.py)
- Track safe aggregate usage fields only
- Integrate usage recording with /chat response generation
- Expose safe usage summary helper for future Provider Settings API
- Add tests for usage counters and privacy boundaries
- Do not store usage in SQLite
- Do not track raw messages/prompts/memory/provider bodies/API keys
- Do not call external APIs
- Do not modify Electron UI

Acceptance Criteria:
- TASK-049 is marked DONE ✅
- TASK-050 is recorded as IN_PROGRESS ✅
- In-memory usage meter service exists (usage_meter_service.py)
- Usage meter tracks request_count
- Usage meter tracks source_counts
- Usage meter tracks provider_counts
- Usage meter tracks model_counts
- Usage meter tracks estimated input/output/total tokens
- Usage meter tracks fallback_count
- Usage meter tracks memory_used_count
- Usage meter never stores API key
- Usage meter never stores raw user message
- Usage meter never stores raw prompt
- Usage meter never stores raw memory context
- Usage meter never stores raw provider response
- /chat response schema remains reply/mood/source
- Existing tests pass
- New tests pass (test_usage_meter_service.py)
- No SQLite usage table is added
- No Electron UI changes are made
- No live external API calls occur

Next Task:
TASK-051 - Backend Provider Settings API Implementation

Completion Notes:
- TASK-050 was an implementation task.
- Added in-memory usage meter only; no SQLite usage table was added.
- /chat response schema remained unchanged: reply / mood / source.
- Usage meter tracks safe aggregate metadata only: request_count, source_counts, provider_counts, model_counts, estimated tokens, fallback_count, memory_used_count, and error_counts.
- Privacy boundaries were preserved: usage meter does not record API keys, raw user messages, raw prompts, raw memory context, or raw provider responses.
- pytest result: 405 passed.
- No Electron UI changes were made.
- No API key was read.
- No external API call was made.
- POST /provider/settings/key must not be enabled before TASK-053 - Secure Key Storage Implementation.
- TASK-051 may implement non-secret endpoints and read-only status first.

---

## TASK-051 - Backend Provider Settings API Implementation

Status: DONE

Goal:
Implement safe non-secret Provider Settings API endpoints and read-only provider status without key storage.

Scope:
- Add provider settings schemas
- Add provider settings service for non-secret runtime settings
- Add GET /provider/settings
- Add PATCH /provider/settings for non-secret settings only
- Add safe usage_summary from in-memory usage meter
- Add safe provider resolved status
- Add disabled placeholder behavior for key storage endpoints
- Do not store API keys
- Do not read API keys
- Do not call external providers
- Do not modify Electron UI

Acceptance Criteria:
- TASK-051 is recorded as IN_PROGRESS
- GET /provider/settings exists
- PATCH /provider/settings exists for non-secret settings
- GET /provider/settings never returns API key
- PATCH /provider/settings rejects API key fields
- usage_summary is safe and aggregate only
- provider status is safe and non-secret
- POST /provider/settings/key returns safe not_implemented placeholder
- DELETE /provider/settings/key returns safe not_implemented placeholder
- POST /provider/settings/test returns safe not_implemented placeholder
- No API key is read
- No API key is stored
- No external API call occurs
- /chat response schema remains unchanged
- Existing tests pass
- New tests pass
- No Electron UI changes are made

Next Task:
TASK-052 - Provider Settings UI Implementation

Implementation Notes:
- `POST /provider/settings/key` must not be enabled before TASK-053 - Secure Key Storage Implementation.
- TASK-051 implements non-secret endpoints and read-only status first.
- Placeholder endpoints must not inspect request body or process submitted key values.
- pytest result: 421 passed.

Completion Notes:
- TASK-051 was an implementation task.
- Added `backend/app/schemas/provider_settings.py`.
- Added `backend/app/services/provider_settings_service.py`.
- Implemented `GET /provider/settings`.
- Implemented `PATCH /provider/settings`.
- Key endpoints remain disabled as safe `501 not_implemented` placeholders:
  - `POST /provider/settings/key`
  - `DELETE /provider/settings/key`
  - `POST /provider/settings/test`
- `POST /provider/settings/key` must not be truly enabled before TASK-053 - Secure Key Storage Implementation.
- Provider settings service is in-memory only and handles non-secret settings only.
- `usage_summary` is provided from the in-memory usage meter with safe aggregate fields only.
- No API key was read.
- No API key was stored.
- No external API call was made.
- No Electron UI changes were made.
- `/chat` response schema remained unchanged: reply / mood / source.
- pytest result: 421 passed.
- Production DB was not polluted.

---

## TASK-052 - Provider Settings UI Implementation

Status: DONE

Goal:
Implement a safe Provider Settings UI for non-secret settings and usage visibility.

Scope:
- Add Provider Settings UI section in Electron renderer
- Load GET /provider/settings
- Update non-secret settings via PATCH /provider/settings
- Display safe key_status only
- Display safe usage_summary
- Show API key save/test as disabled or not implemented
- Do not store API keys
- Do not call external providers
- Keep /chat response schema unchanged

Acceptance Criteria:
- TASK-052 is recorded as IN_PROGRESS
- Provider Settings UI section exists
- UI can load provider settings from backend
- UI can update non-secret settings
- UI displays key_status without key value
- UI displays usage_summary safe aggregate data
- API key save UI is disabled or clearly marked not implemented
- Test connection UI is disabled or clearly marked not implemented
- Frontend does not call external providers
- Frontend does not log API key
- /chat still works
- Existing backend tests pass
- Electron static checks pass
- No live external API calls occur

Next Task:
TASK-053 - Secure Key Storage Implementation

Implementation Notes:
- Provider Settings UI is implemented in the Electron renderer near Memory and Audit sections.
- UI only calls local backend endpoints: `GET /provider/settings` and `PATCH /provider/settings`.
- PATCH body includes only provider, model, real_provider_enabled, llm_chat_enabled, and fallback_to_mock.
- API key save, clear, and test connection controls are disabled placeholders.
- Frontend does not call Anthropic, OpenAI, or any external provider endpoint.
- No API key is read, stored, logged, or sent by the frontend.
- `/chat` response schema remains reply / mood / source.
- Backend pytest result: 421 passed.
- Electron static checks passed: `node --check src/main.js` and `node --check src/renderer/renderer.js`.
- Static safety scan found no external provider URLs, localStorage usage, console logging, or frontend key/test endpoint calls.

Completion Notes:
- TASK-052 was an implementation task.
- Electron renderer now includes a Provider Settings UI section after Audit Logs and before the memory toggle.
- UI can load `GET /provider/settings`.
- UI can update non-secret settings via `PATCH /provider/settings`.
- UI displays provider, model, real_provider_enabled, llm_chat_enabled, fallback_to_mock, key_status, last_test_status, resolved_provider, and safe aggregate usage_summary.
- API key save, clear, and test connection controls remain disabled placeholders.
- API key save / clear / test connection must not be truly enabled before TASK-053 - Secure Key Storage Implementation is complete.
- Frontend does not call `/provider/settings/key`.
- Frontend does not call `/provider/settings/test`.
- Frontend does not call Anthropic, OpenAI, or any external provider endpoint.
- No API key was exposed.
- `/chat` remained usable and its response schema stayed reply / mood / source.
- pytest result: 421 passed.
- Electron static checks passed:
  - `node --check src/main.js`
  - `node --check src/renderer/renderer.js`
- Static scan found no external provider URL, localStorage usage, console logging, or frontend key/test endpoint calls.
- No live external API call was made.

---

## TASK-053 - Secure Key Storage Implementation

Status: DONE

Goal:
Implement a secure key storage abstraction for future BYOK API key save/clear support without exposing or using real keys.

Scope:
- Add key storage service abstraction
- Prefer OS keychain/keyring backend when available
- Add safe unavailable fallback behavior
- Add fake/in-memory test backend for tests only
- Add tests for save/get/status/clear behavior
- Ensure API keys are never returned
- Ensure API keys are never logged
- Do not store keys in SQLite
- Do not call external APIs
- Do not enable live test connection
- Do not modify Electron UI

Acceptance Criteria:
- TASK-053 is recorded as IN_PROGRESS
- secure key storage service exists
- key storage does not use SQLite
- key storage does not use plain config file
- fake test backend exists for tests
- save key works in fake backend tests
- get key is backend-only and never exposed through response schemas
- key_status can report configured / not_configured
- clear key works and is idempotent
- replace key overwrites old key in fake backend tests
- API key is redacted from repr / str / logs
- API key does not appear in stdout / stderr
- API key does not appear in provider settings GET response
- No external API call occurs
- No Electron UI changes are made
- Existing tests pass
- New tests pass

Next Task:
TASK-054 - Provider Settings Key Endpoint Implementation

Implementation Notes:
- `backend/app/services/key_storage_service.py` implements the abstraction.
- Default runtime backend is a safe unavailable backend; it does not persist keys.
- `InMemoryKeyStorageBackend` is for tests only.
- `KeyringKeyStorageBackend` is optional and raises safe unavailable behavior if the `keyring` package is not installed.
- `GET /provider/settings` may report safe key_status but never returns key values.
- `POST /provider/settings/key`, `DELETE /provider/settings/key`, and `POST /provider/settings/test` remain disabled placeholders until TASK-054.
- No SQLite key table or plain config storage is added.
- No external provider call is made.
- Electron UI is not modified.
- pytest result: 436 passed.

Completion Notes:
- TASK-053 was an implementation task.
- Added `backend/app/services/key_storage_service.py`.
- Added `KeyStorageBackend` protocol.
- Runtime default is `UnavailableKeyStorageBackend`.
- `InMemoryKeyStorageBackend` is for tests only.
- `KeyringKeyStorageBackend` is optional and currently not enabled as a dependency.
- Provider settings can read safe key_status values: configured / not_configured.
- API key is never returned to frontend responses.
- API key is never stored in SQLite.
- API key is never stored in plain config files.
- API key is never written to logs, stdout, stderr, memory, audit, usage records, or chat history.
- No external API call was made.
- No Electron UI changes were made.
- pytest result: 436 passed.
- Production DB was not polluted.

---

## TASK-054 - Provider Settings Key Endpoint Implementation

Status: DONE

Goal:
Implement safe API key save and clear endpoints through the key storage abstraction without exposing keys or calling providers.

Scope:
- Enable POST /provider/settings/key through key storage service
- Enable DELETE /provider/settings/key through key storage service
- Keep POST /provider/settings/test disabled / placeholder
- Use fake/in-memory backend in tests only
- Runtime unavailable storage must fail safely
- Never return API key
- Never log API key
- Never store API key in SQLite
- Do not call external APIs
- Do not modify Electron UI

Acceptance Criteria:
- TASK-054 is recorded as IN_PROGRESS
- POST /provider/settings/key exists and uses key storage abstraction
- DELETE /provider/settings/key exists and uses key storage abstraction
- POST /provider/settings/test remains disabled or not implemented
- Runtime unavailable storage returns safe error without exposing key
- Test backend can save key
- Test backend can clear key
- Test backend clear is idempotent
- Replacing key overwrites old key in fake backend tests
- GET /provider/settings returns key_status only
- No endpoint returns API key or partial key
- API key does not appear in logs/stdout/stderr
- API key is not stored in SQLite
- No external API call occurs
- /chat response schema remains unchanged
- Existing tests pass
- New tests pass
- No Electron UI changes are made

Next Task:
TASK-055 - Provider Settings Key UI Enablement Design

Implementation Notes:
- `POST /provider/settings/key` now accepts write-only `provider` and `api_key` fields and saves through the key storage abstraction.
- `DELETE /provider/settings/key` now clears a provider key through the key storage abstraction and is idempotent when storage is available.
- Runtime default storage is still `UnavailableKeyStorageBackend`; save/clear return a safe unavailable error without exposing submitted key values.
- Tests use `InMemoryKeyStorageBackend` only and verify save, clear, idempotent clear, and replace behavior.
- `GET /provider/settings` returns only safe `key_status`; it never returns full or partial key values.
- `POST /provider/settings/test` remains disabled as a safe `501 not_implemented` placeholder.
- API keys are not written to SQLite, logs, stdout, stderr, memory, audit rows, usage records, chat history, or frontend responses.
- No external provider call is made.
- Electron UI is not modified.
- `/chat` response schema remains `reply / mood / source`.
- pytest result: 449 passed.
- Production DB was not polluted.

Completion Notes:
- TASK-054 was an implementation task.
- `POST /provider/settings/key` is wired to the key storage abstraction.
- `DELETE /provider/settings/key` is wired to the key storage abstraction.
- `POST /provider/settings/test` remains disabled as `501 not_implemented`.
- Runtime default `UnavailableKeyStorageBackend` fails safely with a `503` response for save/clear attempts.
- Tests use `InMemoryKeyStorageBackend` to verify save, clear, idempotent clear, and replace behavior.
- API key is never returned to frontend responses.
- API key is never stored in SQLite.
- API key is never written to logs, stdout, or stderr.
- No external provider call was made.
- No Electron UI changes were made.
- `/chat` response schema remains `reply / mood / source`.
- pytest result: 449 passed.
- Production DB was not polluted.
- Next task: TASK-055 - Provider Settings Key UI Enablement Design.

---

## TASK-055 - Provider Settings Key UI Enablement Design

Status: DONE

Goal:
Design how the Provider Settings UI will safely enable the Save Key and Clear Key controls now that the backend key save/clear endpoints are wired to the key storage abstraction (TASK-054). This task is design-only — no runtime code is written, no Electron UI is modified.

Scope:
- Design Save Key UI interaction (password masking, POST to local backend, field clearing after save, disabled states)
- Design Clear Key UI interaction (confirmation dialog, DELETE to local backend, idempotent behavior)
- Design unavailable storage UX (503 → safe message, keep Save disabled, env var dev mode recommendation)
- Design key status display (6 safe values, no key fragments)
- Design Test Connection disabled state (no live calls, future explicit_cost_ack)
- Define security boundaries for key UI (no key in renderer logs, localStorage, screenshots, etc.)
- Define error UX (7 safe messages)
- Define future task sequence (TASK-056 implementation, TASK-057 smoke check, TASK-058 test connection design)
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests
- Do not add APIs
- Do not implement UI enablement
- Do not enable Test Connection
- Do not call external APIs
- Do not read real API keys
- Do not modify /chat
- Only modify docs / README

Acceptance Criteria:
- TASK-054 is marked DONE ✅
- TASK-055 is recorded as DONE ✅
- docs/PROVIDER_SETTINGS_KEY_UI_ENABLEMENT_DESIGN.md exists ✅
- Save Key UI design is documented (masking, POST flow, field clearing, disabled states) ✅
- Clear Key UI design is documented (confirmation, DELETE flow, idempotency) ✅
- Unavailable storage UX is documented (503 safe message, Save disabled, env var recommendation) ✅
- Key status display is documented (6 values, no key fragments) ✅
- Test Connection remains documented as disabled ✅
- Security boundaries are documented (key not in renderer logs / localStorage / screenshots / memory / audit / usage / chat history) ✅
- Error UX is documented (7 safe messages) ✅
- Future task sequence is documented (TASK-056 → TASK-057 → TASK-058 → TASK-059) ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- No tests are added ✅
- No APIs are added ✅
- No external API call is made ✅

Completion Notes:
- TASK-055 was a design-only task. No runtime code was written or modified.
- docs/PROVIDER_SETTINGS_KEY_UI_ENABLEMENT_DESIGN.md created: 12 sections covering current state after TASK-054, Save Key UI interaction flow, Clear Key UI interaction flow, unavailable storage UX (503 → safe message + env var recommendation), key status display (6 canonical values), Test Connection disabled state, security boundaries (12 rules), error UX (7 safe messages), non-goals (14 items), future implementation sequence, and relationship to existing documents.
- Save Key UI: password-masked input, POST to local backend only, field cleared after save (success or failure), disabled for mock provider, disabled when storage is unavailable after 503, cost warning shown on real provider selection.
- Clear Key UI: visible only when key exists (any status other than not_configured), requires confirmation dialog before DELETE, idempotent (404 treated as success), never displays key value.
- Unavailable storage UX: 503 response returns safe message with env var setup instructions, no auto-retry, button re-enabled for manual retry.
- Key status display: not_configured / configured / not_tested / invalid / test_success / test_failed mapped to human-readable labels; no key value or fragment in any label.
- Test Connection: remains disabled, button shows "not yet available", deferred to TASK-058 (design) and TASK-059 (implementation).
- Security boundaries: 12 rules — no key in renderer state / IPC / logs / localStorage / screenshots / DevTools / memory audit / usage records / chat history / crash reports; local backend only; no external provider URLs in renderer.
- Error UX: 7 safe messages for storage unavailable (503), invalid provider (400), empty key (400), backend unreachable, save failed (500), clear failed (500), key not found on delete (treated as success).
- No backend/app code was modified.
- No apps/desktop code was modified.
- No tests were added.
- No APIs were added.
- No external API call was made.
- pytest count remains 449 passed (unchanged — design-only task).

Next Task:
TASK-056 - Provider Settings Key UI Enablement Implementation

---

## TASK-056 - Provider Settings Key UI Enablement Implementation

Status: DONE

Goal:
Enable the Provider Settings UI Save Key and Clear Key controls to safely call local backend endpoints now that the backend key save/clear endpoints are wired (TASK-054) and the UI interaction design is complete (TASK-055).

Scope:
- Enable API key input for real providers (disabled for mock)
- Enable Save Key button — calls POST http://127.0.0.1:8000/provider/settings/key
- Enable Clear Key button — calls DELETE http://127.0.0.1:8000/provider/settings/key?provider=...
- Keep Test Connection disabled
- Handle storage unavailable 503 with safe message
- Clear key input after every save attempt (success or failure)
- Never display API key after save
- Never log API key to console
- Never store API key in localStorage/sessionStorage
- Keep /chat schema unchanged
- Do not call external providers
- Do not add backend APIs
- Do not enable POST /provider/settings/test

Acceptance Criteria:
- TASK-056 is recorded as DONE ✅
- API key input can be used for real providers only ✅
- Save Key calls local backend POST /provider/settings/key ✅
- Clear Key calls local backend DELETE /provider/settings/key ✅
- Test Connection remains disabled ✅
- API key field clears after save attempt ✅
- API key value is never displayed after save ✅
- API key is not logged to console ✅
- API key is not stored in localStorage/sessionStorage ✅
- Storage unavailable 503 shows safe message ✅
- key_status refreshes after save/clear ✅
- frontend does not call external provider URLs ✅
- /chat still works ✅
- backend pytest: 449 passed ✅
- Electron static checks pass ✅
- no live external API call occurs ✅

Completion Notes:
- TASK-056 was an Electron UI implementation task. No new backend API was added.
- apps/desktop/src/renderer/index.html: updated Provider Settings section description; replaced .provider-key-placeholder with .provider-key-section; removed hardcoded disabled from API key input; updated placeholder text; replaced .provider-placeholder-actions with .provider-key-actions; removed disabled from button markup (state controlled by JS); added id=provider-key-msg div for key-specific status messages; updated Test Connection button title.
- apps/desktop/src/renderer/renderer.js: added DOM refs for providerApiKeyInput, saveProviderKeyBtn, clearProviderKeyBtn, testProviderConnectionBtn, providerKeyMsg; added setProviderKeyMsg(); added updateKeyUIState() called from renderProviderSettings(); added saveProviderKey() (POST to local backend, clears input before and after, never logs key, handles 503/400/network error); added clearProviderKey() (confirmation dialog, DELETE to local backend, idempotent 404 handling); added event listeners for save-provider-key-btn, clear-provider-key-btn, input change on key field, provider dropdown change.
- apps/desktop/src/renderer/styles.css: updated selectors from .provider-key-placeholder to .provider-key-section; added .provider-key-actions, .provider-key-msg, .provider-key-msg.error, .provider-key-note.
- backend/app/api/routes.py: file was truncated on disk from a previous session (TASK-054 pre-existing bug); restored missing content via bash append to NTFS mount — behavior unchanged, no logic was modified.
- backend/app/main.py: file was also truncated (missing `(router)` on last line); restored via bash append — behavior unchanged.
- API key is never logged to console (only in JSDoc comments).
- API key is never stored in localStorage or sessionStorage (only mentioned in comments).
- No external provider URL appears in renderer.js.
- Test Connection fetch is not wired — button disabled, no handler.
- pytest result: 449 passed (all existing tests pass; no new backend tests added).
- Electron static checks: node --check src/main.js PASS, node --check src/renderer/renderer.js PASS.
- No live external API call was made.
- Runtime smoke check is deferred to TASK-057.

Next Task:
TASK-057 - Provider Settings Key UI Runtime Smoke Check

---

## TASK-057 - Provider Settings Key UI Runtime Smoke Check

Status: DONE

Goal:
Verify the Provider Settings Key UI Save Key and Clear Key controls at runtime on the Windows local machine, confirming safe behavior, correct 503 handling, input clearing, and no external provider calls.

Scope:
- Run backend pytest suite and confirm all tests pass
- Start uvicorn backend and confirm no startup errors
- Start Electron desktop with npm start and confirm window opens
- Confirm Provider Settings section is visible
- Confirm API key input is enabled for real providers
- Confirm Save Key calls local backend only (not external provider)
- Confirm storage unavailable 503 shows safe message
- Confirm key input is cleared after save attempt
- Confirm Clear Key behavior (if applicable)
- Confirm Test Connection remains disabled
- Confirm /chat still works
- Confirm API key is not displayed in UI
- Confirm API key is not logged to console
- Confirm API key is not stored in localStorage/sessionStorage
- Confirm no external provider call occurs
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests
- Do not add APIs
- Do not call external APIs

Acceptance Criteria:
- TASK-056 is marked DONE ✅
- TASK-057 is recorded as DONE ✅
- pytest passes ✅
- backend starts without errors ✅
- Electron desktop opens ✅
- Provider Settings section visible ✅
- API key input enabled for real providers ✅
- Save Key calls local backend only ✅
- Storage unavailable 503 safe message shown ✅
- Key input cleared after save attempt ✅
- Test Connection remains disabled ✅
- /chat still works ✅
- API key not displayed in UI ✅
- API key not logged to console ✅
- API key not stored in localStorage/sessionStorage ✅
- No external provider call occurs ✅
- No backend/app code modified ✅
- No apps/desktop code modified ✅

Runtime Smoke Check Results (performed on Windows host):

- pytest: 449 passed, 0 failed ✅
- backend uvicorn: started successfully, no errors ✅
- desktop npm start: launched successfully ✅
- Electron window: opened and responsive ✅
- Provider Settings section visible: yes ✅
- anthropic provider key input enabled: yes ✅
- Save Key calls local backend only: yes ✅
- storage unavailable 503 safe message shown: yes ✅
- key input cleared after save attempt: yes ✅
- Clear Key: not applicable — key_status remained not_configured (storage unavailable by design) ✅
- Test Connection still disabled: yes ✅
- /chat still works: yes ✅
- API key shown in UI: no ✅
- API key logged to console: no ✅
- API key stored in localStorage/sessionStorage: no ✅
- external provider called: no ✅
- mock provider key input disabled: not directly verified (non-blocking)

Non-Blocking Follow-Up (not blocking TASK-057 pass):
- Electron DevTools docked right squeezes the Provider Settings UI. Future UI polish task should address layout.
- Electron font/layout is hard to read at current density. Deferred to a future UI polish/layout task.

Runtime Smoke Verdict: PASS — all acceptance criteria met.

Next Task:
TASK-058 - Provider Test Connection Design

---

## TASK-058 - Provider Test Connection Design

Status: DONE

Goal:
Design a safe manual Test Connection flow for BYOK providers without implementing it.

Scope:
- Define Test Connection purpose
- Define explicit cost acknowledgement requirement
- Define exactly-one minimal request rule
- Define provider/model/key preconditions
- Define memory-disabled test behavior
- Define no tools / no streaming / no retries rule
- Define safe success / failure response model
- Define usage meter integration
- Define UI behavior
- Define logging/redaction rules
- Do not implement runtime code
- Do not call external APIs

Acceptance Criteria:
- TASK-058 is recorded as DONE ✅
- docs/PROVIDER_TEST_CONNECTION_DESIGN.md exists ✅
- explicit_cost_ack behavior is documented ✅
- exactly-one minimal request rule is documented ✅
- safe response model is documented ✅
- failure behavior is documented ✅
- usage meter integration is documented ✅
- UI behavior is documented ✅
- logging/redaction rules are documented ✅
- Test Connection remains disabled in runtime ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- No external API call is made ✅

Completion Notes:
- TASK-058 was a design-only task. No runtime code was written or modified.
- docs/PROVIDER_TEST_CONNECTION_DESIGN.md created: defines manual Test Connection flow, preconditions (key_status configured, real provider selected, explicit_cost_ack per-click), explicit cost acknowledgement (every click requires confirmation; backend must require explicit_cost_ack: true; missing/false returns safe 400 cost_ack_required), exactly-one minimal request rule (one request only, no retries, no streaming, no tools, no memory, no history, minimal prompt "Reply with OK.", low max_tokens, timeout enforced), no-fallback policy (Test Connection verifies real provider only; no silent mock fallback), safe response model (status / provider / model / source / safe_message / error_category / usage_estimate; no API key / raw provider body / headers / prompt / diagnostics returned), usage meter integration, UI behavior, and logging/redaction rules.
- Test Connection runtime remains disabled. POST /provider/settings/test still returns 501 not_implemented.
- No backend/app code is modified.
- No apps/desktop code is modified.
- No tests are added.
- No APIs are added.
- No external API call is made.

Next Task:
TASK-059 - Provider Test Connection Implementation
(Note: TASK-059 must use mocked tests only — no live provider calls, no live smoke.)

---

## TASK-059 - Provider Test Connection Implementation

Status: DONE

Goal:
Implement the backend Test Connection flow as designed in TASK-058, using mocked-provider tests only. No live provider calls.

Scope:
- Implement POST /provider/settings/test endpoint (replace 501 placeholder)
- Require explicit_cost_ack: true in request body; return safe 400 cost_ack_required if missing/false
- Send exactly-one minimal provider-runner request (minimal prompt, low max_tokens, timeout enforced)
- No retries, no streaming, no tools, no memory, no history
- Return safe response model: status / provider / model / source / safe_message / error_category / usage_estimate
- Implement no-fallback policy: test must not silently fall back to mock
- Wire usage meter to record test connection token usage
- Implement redaction rules: no API key / raw provider body / headers / prompt in any log or response
- Write mocked tests only — no live provider calls in pytest
- Keep Electron Test Connection button disabled in this task; UI enablement is deferred
- Do not modify /chat response schema
- Do not add retries or streaming
- Do not call external APIs from tests

Acceptance Criteria:
- TASK-059 is recorded as DONE ✅
- POST /provider/settings/test is implemented (no longer returns 501) ✅
- explicit_cost_ack: true is required; missing/false returns 400 cost_ack_required ✅
- exactly-one minimal request rule is enforced in backend ✅
- safe response model is returned (status / provider / model / source / safe_message / error_category / usage_estimate) ✅
- no mock fallback on test failure ✅
- usage meter records test connection usage ✅
- redaction rules are enforced in backend ✅
- mocked pytest tests cover: missing cost_ack, false cost_ack, mock provider rejection, missing key, storage unavailable, success, auth failure, timeout, opaque non-2xx body, no retries, no memory/history/tools/streaming, key leakage, usage meter, no memory audit, /chat compatibility, and no external HTTP ✅
- no live external API call in any test ✅
- pytest passes (no regressions) ✅
- No Electron UI changes are made ✅
- No /chat response schema change ✅

Completion Notes:
- TASK-059 was a backend implementation task. No Electron UI was modified. Test Connection button remains disabled in the renderer.
- backend/app/services/provider_test_connection_service.py created: implements the provider test runner abstraction and minimal LLMRequest construction.
- backend/tests/test_provider_test_connection.py created: mocked tests only — uses injectable fake provider runner; no live external API call; no real API key used.
- POST /provider/settings/test implemented (replaces 501 placeholder). Requires explicit_cost_ack: true; missing or false returns safe HTTP 400 cost_ack_required.
- Exactly one minimal LLMRequest per test call: prompt "Reply with OK.", max_tokens=16, no memory context, no state context, no conversation history, no tools, no streaming, no retries.
- Fallback policy: no silent mock fallback. Failures return status=failed, source=llm_real_error, safe error_category only.
- Usage meter records safe aggregate metadata only (provider / model / source / token estimates / error_category). No API key, raw provider body, headers, prompt, or diagnostics in any log or response.
- Runtime default does not call external providers. Tests use injectable fake runner.
- No backend/app code was broken. No apps/desktop code was modified.
- No external API call was made. No real API key was used.
- /chat response schema remains reply / mood / source.
- pytest result: 465 passed.
- Production DB was not polluted.

Next Task:
TASK-059R - Provider Test Connection Safety Review

---

## TASK-059R - Provider Test Connection Safety Review

Status: DONE

Reviewer: Opus (automated safety review)

Goal:
Conduct a safety review of the TASK-059 Test Connection backend implementation before enabling the Electron UI. Verify that all security and safety invariants from TASK-058 design are correctly enforced.

Scope:
- Review backend/app/services/provider_test_connection_service.py
- Review POST /provider/settings/test route
- Verify explicit_cost_ack enforcement
- Verify exactly-one minimal request rule (no retries, no streaming, no tools, no memory, no history)
- Verify no-fallback policy
- Verify safe response model (no key / raw body / headers / prompt / diagnostics in response or logs)
- Verify usage meter only records safe aggregate metadata
- Verify redaction rules in backend logging
- Verify mocked tests cover all critical failure paths
- Report any findings; block TASK-060 if critical issues found
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests
- Do not call external APIs

Acceptance Criteria:
- TASK-059R is recorded as DONE ✅
- explicit_cost_ack enforcement is confirmed ✅
- exactly-one minimal request rule is confirmed ✅
- no-fallback policy is confirmed ✅
- safe response model is confirmed (no key / raw body / headers / prompt in response) ✅
- redaction rules are confirmed in logs ✅
- usage meter safe metadata only is confirmed ✅
- mocked tests confirmed to cover all critical paths ✅
- PASS / PASS WITH CHANGES / FAIL verdict recorded ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- No external API call is made ✅

Review Verdict: PASS

Findings:
- No critical issues found.
- No blocking required fixes.
- explicit_cost_ack is enforced at API boundary — missing or false returns 400 cost_ack_required. ✅
- safe error categories are limited — no raw provider body, headers, prompt, or diagnostics in response. ✅
- response schema contains no secret-bearing fields. ✅
- runtime default runner is UnavailableProviderTestRunner — no external provider calls in default configuration. ✅
- automated tests have no live external API calls. ✅
- Backend surface is safe to expose to UI. TASK-060 may proceed.

Recommended Non-Blocking Hardening Tests (deferred — not blocking TASK-060):
- provider_disabled branch with configured key: verify behavior when LLM_PROVIDER_ENABLED=false but key is configured.
- invalid_model branch: verify safe error_category returned for unsupported model identifier.
- unknown provider error collapses to provider_error: verify unrecognized runner exceptions map to safe category, not raw message.
- suspicious extra field rejection: verify extra request fields (e.g., system_prompt) are rejected without being echoed back.
- safe_message category sweep: verify all error_category values produce distinct, safe, non-technical safe_message strings.

Completion Notes:
- TASK-059R was a safety review task. No runtime code was written or modified.
- No backend/app code was modified.
- No apps/desktop code was modified.
- No tests were added.
- No external API call was made.

Next Task:
TASK-060 - Provider Test Connection UI Enablement

---

## TASK-060 - Provider Test Connection UI Enablement

Status: DONE

Goal:
Enable the Test Connection button in the Electron renderer and wire it to the POST /provider/settings/test backend endpoint, with explicit cost acknowledgement dialog. Blocked until TASK-059R passes.

Scope:
- Enable Test Connection button in Electron renderer for real providers with key_status configured
- Implement explicit cost acknowledgement confirmation dialog before sending request
- Wire renderer to POST /provider/settings/test with explicit_cost_ack: true
- Display safe_message from backend response
- Handle backend error responses (400 cost_ack_required, 503 storage unavailable, 500, network error)
- Key status indicator updated after test (test_success / test_failed)
- No live external API call from renderer — only calls local backend
- No API key exposed in UI or logs
- Do not modify /chat response schema
- Do not add retries

Acceptance Criteria:
- TASK-060 is recorded as DONE ✅
- Test Connection button enabled for real providers with configured key ✅
- Explicit cost acknowledgement dialog shown before every request ✅
- POST /provider/settings/test called with explicit_cost_ack: true ✅
- safe_message displayed in UI ✅
- key_status refreshed after test ✅
- No API key in renderer logs or localStorage ✅
- No live external API call from renderer ✅
- Electron static check passes (node --check) ✅
- No /chat response schema change ✅

Completion Notes:
- TASK-060 was an Electron UI implementation task. No backend API was added or modified.
- apps/desktop/src/renderer/index.html: updated comment block; changed Test Connection button text from "Test Connection (disabled)" to "Test Connection"; updated title attribute with enable conditions; added provider-test-msg div for test result messages; updated helper note text.
- apps/desktop/src/renderer/renderer.js: added providerTestMsg DOM ref; added isTestingConnection state flag (prevents concurrent requests); added currentProviderSettings cache (set by renderProviderSettings on every load); updated updateKeyUIState() to enable Test Connection when provider !== mock AND key exists AND real_provider_enabled === true AND no in-flight request; updated button title text to explain disabled state; added setProviderTestMsg() helper; added runTestConnection() with explicit window.confirm() cost acknowledgement (all 4 required text items), POST to local backend only with body {provider, model, explicit_cost_ack: true} (no api_key/prompt/memory), safe response rendering (status/safe_message/error_category/source/usage_estimate only); added testProviderConnectionBtn event listener.
- apps/desktop/src/renderer/styles.css: added .provider-test-msg and .provider-test-msg.error styles.
- No api_key, prompt, memory_context, or conversation_history sent to test endpoint. ✅
- No automatic test after Save Key. ✅
- No external provider URL in renderer (api.anthropic.com, api.openai.com, etc.). ✅
- localStorage/sessionStorage references in renderer are comments only, not code. ✅
- Safety scan: no external URL, no localStorage/sessionStorage code, no console.log of key. ✅
- node --check: main.js PASS, renderer.js PASS. ✅
- pytest result: 465 passed (NTFS stale-cache regressions fixed in rsync copy during test run; no backend logic was modified). ✅
- No live external API call was made. ✅
- /chat response schema remains reply / mood / source. ✅
- Runtime smoke check is deferred to TASK-061.

Next Task:
TASK-061 - Provider Test Connection Runtime Smoke Check

---

## TASK-061 - Provider Test Connection Runtime Smoke Check

Status: DONE

Goal:
Perform a manual runtime smoke check of the Test Connection UI flow on the local dev machine. Blocked until TASK-060 is complete.

Scope:
- Start backend and Electron desktop
- Verify Test Connection button disabled for mock provider
- Verify Test Connection button disabled when key_status is not_configured
- Verify Test Connection button enabled for real provider with configured key
- Verify cost acknowledgement dialog appears on click
- Verify cancelling dialog sends no backend request
- Verify confirming dialog sends POST /provider/settings/test
- Verify safe_message displayed in UI
- Verify key status indicator updated after test
- Verify no API key in renderer DevTools or console
- Verify /chat remains functional throughout
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests
- Do not call external APIs from automation

Acceptance Criteria:
- TASK-061 is recorded as DONE ✅
- All smoke check items verified ✅ or recorded as non-blocking / not applicable ✅
- Runtime Smoke Verdict recorded ✅
- No API key leaked in renderer logs or DevTools ✅
- /chat unaffected ✅
- No backend/app code modified ✅
- No apps/desktop code modified ✅
- No external API call made ✅

Smoke Check Results:

| Item | Result |
|---|---|
| pytest: 465 passed | ✅ |
| backend start | ✅ pass |
| desktop start | ✅ pass |
| Provider Settings visible | ✅ yes |
| Test Connection button visible | ✅ yes |
| Test Connection disabled when provider is mock | ✅ yes |
| Test Connection disabled when key_status is not_configured | ✅ yes |
| Test Connection enabled when provider real + key_status configured + real_provider_enabled | not directly verified — key_status remained not_configured (expected limitation) |
| Cost acknowledgement dialog shown every click | n/a — Test Connection disabled due to key_status not_configured |
| Cancel cost ack sends no request | n/a |
| Confirm sends POST /provider/settings/test to local backend only | n/a |
| Request body contains provider/model/explicit_cost_ack only | n/a |
| No api_key in request body | n/a |
| Safe message shown in UI | n/a |
| No raw provider body shown | ✅ yes — no provider test request was sent |
| No external provider called | ✅ yes |
| API key not shown / logged / stored | ✅ yes |
| /chat still works | ✅ yes |

Expected Limitation:
- Runtime key storage is unavailable (UnavailableKeyStorageBackend is the default).
- key_status remained not_configured throughout the smoke check.
- Test Connection button stayed disabled — this is the correct and safe behavior.
- Full click-through Test Connection flow requires a test harness or configured secure key storage.
- A real API key was NOT used to force the smoke; this is intentional per TASK-060 safety constraints.

Known Non-Blocking UI Issues (deferred):
- Electron UI font/layout is difficult to read in some window sizes.
- DevTools docked to the side can squeeze the layout.
- Recommended future task: UI polish/layout hardening.

Runtime Smoke Verdict: PASS WITH EXPECTED LIMITATION

Completion Notes:
- TASK-061 was a runtime smoke check task. No code was written or modified.
- No backend/app code was modified.
- No apps/desktop code was modified.
- No tests were added.
- No external API call was made.
- No real API key was used.

Next Task:
TASK-062 - Provider Test Connection Hardening Tests

---

## TASK-062 - Provider Test Connection Hardening Tests

Status: DONE

Goal:
Implement the non-blocking hardening tests recommended by Opus safety review (TASK-059R) for the POST /provider/settings/test endpoint. Covers edge cases not included in the initial TASK-059 mocked test suite.

Scope:
- provider_disabled branch with configured key: verify behavior when LLM_PROVIDER_ENABLED=false but key is configured
- invalid_model branch: verify safe error_category returned for unsupported model identifier
- unknown provider error collapses to provider_error: verify unrecognized runner exceptions map to safe category, not raw message
- suspicious extra field rejection: verify extra request fields (e.g., system_prompt) are rejected without being echoed back
- safe_message category sweep: verify all error_category values produce distinct, safe, non-technical safe_message strings
- All tests must use mocked runner — no live provider calls
- No real API key
- Do not modify backend/app behavior (tests only)
- Do not modify apps/desktop
- Do not add new backend API endpoints
- Do not call external APIs

Acceptance Criteria:
- TASK-062 is recorded as DONE
- All 5 Opus-recommended hardening test cases implemented ✅
- All tests pass (no regressions) ✅
- All tests use mocked runner — no live external API call ✅
- No real API key used ✅
- No backend logic modified ✅
- No apps/desktop code modified ✅
- pytest passes (no regressions) ✅

Implementation Summary:
- Added 5 hardening tests to backend/tests/test_provider_test_connection.py (lines 372-536)
- Test A: provider_disabled branch — verifies runner not called when real_provider_enabled=False, even with configured key
- Test B: invalid_model branch — verifies 400 invalid_model returned before runner call when no model in request or settings
- Test C: unknown error collapse — verifies unrecognized runner error strings map to safe 'provider_error', raw string does not leak
- Test D: extra field rejection — verifies ConfigDict extra='forbid' rejects system_prompt injection, sentinel value not echoed, runner not called
- Test E: safe_message category sweep — verifies all 11 error categories have non-empty safe messages free of API key / raw body / prompt sentinels
- pytest: 470 passed (465 pre-existing + 5 new), 0 failed, 0 regressions
- No backend/app logic modified, no apps/desktop code modified, no external API calls

Next Task:
TASK-063 - Electron Provider Settings UI Polish and Layout Fix

---

## TASK-063 - Electron Provider Settings UI Polish and Layout Fix

Status: DONE

Goal:
Improve Electron renderer readability, scroll behavior, and Provider Settings layout without changing backend or provider behavior.

Scope:
- Improve base font size and line height
- Improve scroll behavior
- Improve Provider Settings section readability
- Improve form spacing and button layout
- Improve mobile/narrow-width behavior when DevTools is docked
- Preserve all existing Provider Settings behavior
- Preserve Save Key / Clear Key / Test Connection safety behavior
- Do not modify backend/app
- Do not call external APIs

Acceptance Criteria:
- TASK-063 is recorded and completed as DONE
- Electron renderer font readability is improved
- Provider Settings section is easier to read
- Page can scroll vertically when content exceeds window height
- Narrow window / docked DevTools layout remains usable
- Test Connection button behavior is unchanged
- Save Key / Clear Key behavior is unchanged
- No backend/app code is modified
- No external API call occurs
- Electron static checks pass

Implementation Summary:
- apps/desktop/src/renderer/styles.css: increased base font size and line height, section padding, form spacing, button/input sizing, helper text sizing, and Provider Settings status/usage layout readability.
- apps/desktop/src/renderer/styles.css: removed global fixed-height/hidden-overflow behavior, allowed body/html vertical scrolling, converted Provider/Memory/Audit sections away from nested fixed section scrolling, and added page bottom padding.
- apps/desktop/src/renderer/styles.css: improved Provider Settings form grid, key actions wrapping, status cards, usage summary block, long-text wrapping, and narrow-width media queries for DevTools docked right.
- apps/desktop/src/renderer/index.html: updated stale Test Connection helper copy and replaced small inline status text with a CSS class.
- Save Key / Clear Key / Test Connection endpoint calls, enable conditions, explicit_cost_ack confirm logic, safe response rendering, usage data, /chat payload, and backend behavior were not changed.
- No backend/app code was modified.
- No backend tests were modified.
- No external API call was made.

Validation:
- Safety scan: renderer contains no api.anthropic.com, api.openai.com, platform.claude.com, direct provider frontend call, API key console logging, or API key localStorage/sessionStorage storage.
- `node --check src/main.js`: PASS.
- `node --check src/renderer/renderer.js`: PASS.
- pytest not run because backend/app and backend tests were not modified.

Next Task:
TASK-064 - Provider Settings UI Runtime Smoke Re-check

---

## TASK-064 - Provider Settings UI Runtime Smoke Re-check

Status: DONE

Goal:
Re-check the Electron Provider Settings UI at runtime after TASK-063 readability and layout polish, without changing backend/app, renderer code, tests, APIs, or provider behavior.

Scope:
- Start local backend
- Start Electron desktop
- Re-check Provider Settings readability and scroll behavior
- Re-check narrow layout / DevTools docked-right usability
- Confirm Save Key / Clear Key / Test Connection behavior remains unchanged
- Confirm Test Connection remains local-backend-only
- Confirm no external provider is called
- Confirm no real API key is used
- Confirm /chat still works
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests
- Do not add APIs
- Do not call a live external provider

Smoke Check Results:

| Item | Result |
|---|---|
| backend start | pass |
| desktop start | pass |
| Electron UI readable after TASK-063 | yes |
| Page can scroll vertically | yes |
| Provider Settings section fully visible | yes |
| Provider Settings fields readable | yes |
| Usage summary readable | yes |
| Buttons wrap / remain usable in narrow layout | yes |
| DevTools docked right no longer blocks basic operation | partially |
| Save Key behavior unchanged | yes |
| Clear Key behavior unchanged | yes |
| Test Connection behavior unchanged | yes |
| Test Connection remains local-backend-only | yes |
| No external provider called | yes |
| API key not shown/logged/stored | yes |
| /chat still works | yes |

Validation Notes:
- Known TASK-063 static checks remain valid: `node --check src/main.js` PASS; `node --check src/renderer/renderer.js` PASS.
- Backend runtime smoke used local backend only: `GET /health` returned `status=ok`; `POST /chat` returned a mock response with `source=mock`.
- Desktop runtime start passed after clearing the local shell environment variable `ELECTRON_RUN_AS_NODE=1`; the first attempt failed because that environment variable made Electron run in Node mode.
- DevTools docked-right result is recorded as partially because the narrow-layout behavior is improved and basic controls remain usable, but a full manual docked DevTools click-through with saved key storage was not performed.
- No real API key was entered.
- No Save Key, Clear Key, or Test Connection endpoint behavior was changed.
- No Test Connection request was sent to a live provider.
- No external provider API was called.
- No backend/app code was modified.
- No apps/desktop code was modified.
- No tests were added.
- pytest was not run because this task did not modify backend/app or backend tests.

Runtime Smoke Verdict: PASS WITH NON-BLOCKING UI NOTES

Next Task:
TASK-065 - Phase 4 Provider Settings Stabilization Summary

---

## TASK-065 - Phase 4 Provider Settings Stabilization Summary

Status: DONE

Goal:
Consolidate TASK-045 through TASK-064 achievements into a single stable reference document covering the Provider Settings / BYOK / Test Connection sub-track of Phase 4. Docs-only task — no backend/app changes, no apps/desktop changes, no external API calls.

Scope:
- Create docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md
- Update docs/TASKS.md (this file)
- Update docs/ROADMAP.md
- Update README.md
- Record: no live external provider call has occurred; no real API key has been used; Test Connection remains local-backend-only in all verified flows; manual live provider smoke requires explicit user cost confirmation

Acceptance Criteria:
- TASK-065 is recorded as DONE ✅
- docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md exists and covers all required sections ✅
- TASKS.md records TASK-065 DONE ✅
- ROADMAP.md records TASK-064 DONE and TASK-065 DONE ✅
- README.md updated with TASK-065 summary line ✅
- No backend/app code modified ✅
- No apps/desktop code modified ✅
- No external API call made ✅

Implementation Summary:
- docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md: created — covers completed capabilities (BYOK, usage meter, backend API, key storage, Provider Settings UI, Test Connection), current safety boundaries (16-row table), what is implemented, what is intentionally not implemented (14 items), current runtime limitations (5 items), known non-blocking UI notes (3 items), test results summary (10 checks + 5 hardening tests), live provider smoke go/no-go conditions (8 conditions, all unmet), recommended next tasks (5 items), and reference documents (8 docs)
- docs/ROADMAP.md: TASK-064 DONE added; TASK-065 DONE added; Phase 4 status line updated
- README.md: TASK-065 update block added; Phase 4 status line updated
- No backend/app code was modified
- No apps/desktop code was modified
- No external API call was made

Next Task:
TASK-066D - Portfolio Demo Script and Screenshots

---

## TASK-066D - Portfolio Demo Script and Screenshots

Status: DONE

Goal:
Create a portfolio/demo script that explains the current dragon-pet-ai system for interviews, project showcases, and future demos. Docs-only task — no runtime code changes.

Scope:
- Create docs/PORTFOLIO_DEMO_SCRIPT.md with full demo narrative
- Explain project purpose, architecture, completed features, safety boundaries
- Provide demo walk-through steps, screenshot checklist, interview talking points
- Provide PowerShell demo commands
- Explain what not to claim
- Update docs/TASKS.md, docs/ROADMAP.md, README.md
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests or APIs
- Do not call external APIs
- Do not use real API keys

Acceptance Criteria:
- TASK-066D is recorded as DONE ✅
- docs/PORTFOLIO_DEMO_SCRIPT.md exists ✅
- Demo narrative is documented ✅
- Screenshot checklist is documented ✅
- Interview talking points are documented ✅
- Architecture explanation is documented ✅
- Safety / BYOK explanation is documented ✅
- Current limitations are documented ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- No external API call is made ✅

Implementation Summary:
- docs/PORTFOLIO_DEMO_SCRIPT.md: created — covers project one-liner, 30-second pitch, 2-minute demo script (10 steps), architecture talking points with ASCII diagram, completed features table (21 items), safety/BYOK explanation (BYOK definition, key protection, storage, Test Connection, no live call confirmation), screenshot checklist (9 items), what not to claim (8 items), current limitations (6 items), interview talking points (8 topics), demo commands (PowerShell), suggested read-aloud demo flow, and next development options
- docs/ROADMAP.md: TASK-066D DONE added under Phase 4 portfolio stabilization section
- README.md: TASK-066D update block added; PORTFOLIO_DEMO_SCRIPT.md listed in docs table; Phase 4 status line updated
- No backend/app code was modified
- No apps/desktop code was modified
- No external API call was made

Next Task:
TASK-067D - Portfolio README Polish

---

## TASK-067D - Portfolio README Polish

Status: DONE

Goal:
Polish the README as a portfolio-friendly entry point for interviews and GitHub viewers. Docs-only — no runtime code changes.

Scope:
- Rewrite README opening section with project one-liner and current status
- Add completed capabilities summary (updated)
- Add architecture summary
- Add safety / BYOK summary
- Add Quick Start with Windows PowerShell commands
- Add Demo / Portfolio links section
- Add clear current limitations section
- Link to docs/PORTFOLIO_DEMO_SCRIPT.md
- Move development journal (task update blocks) to a clearly labelled section
- Update docs/TASKS.md and docs/ROADMAP.md
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests or APIs
- Do not call external APIs

Acceptance Criteria:
- TASK-067D is recorded as DONE ✅
- README opening section is clearer and portfolio-friendly ✅
- Project one-liner is present ✅
- Completed capabilities are summarized (updated) ✅
- Architecture is summarized ✅
- Safety / BYOK boundaries are summarized ✅
- Demo / run commands are easy to find ✅
- Current limitations are clearly stated ✅
- Link to docs/PORTFOLIO_DEMO_SCRIPT.md exists ✅
- No backend/app code is modified ✅
- No apps/desktop code is modified ✅
- No external API call is made ✅

Implementation Summary:
- README.md: completely rewritten as portfolio-friendly entry point — added project one-liner, current status table, completed capabilities table (21 items), architecture diagram with key design decisions, safety/BYOK summary table (10 rules), PowerShell quick start (pytest + backend + Electron), demo & portfolio links section (8 docs), current limitations table (8 items), updated directory structure, updated docs table (24 docs), development principles, and a collapsible Development Journal section (task update blocks TASK-054 through TASK-067D)
- docs/TASKS.md: TASK-067D added as DONE
- docs/ROADMAP.md: TASK-067D added as DONE
- No backend/app code was modified
- No apps/desktop code was modified
- No external API call was made

Next Task:
TASK-068D - Portfolio Screenshot Checklist Capture

---

## TASK-068D - Portfolio Screenshot Checklist Capture

Status: DONE

Goal:
Plan and document the portfolio screenshot checklist so that demo screenshots can be captured consistently and safely. Docs-only task — no runtime code changes.

Scope:
- Create docs/PORTFOLIO_SCREENSHOT_CHECKLIST.md
- Document naming convention, required screenshots (9 items), optional screenshots, setup commands, what must not appear, recommended capture order, and portfolio usage guidance
- Update docs/PORTFOLIO_DEMO_SCRIPT.md with checklist link
- Update README.md with checklist link
- Update docs/ROADMAP.md with TASK-068D
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests or APIs
- Do not call external APIs
- Do not use real API key

Acceptance Criteria:
- TASK-068D is recorded as DONE ✅
- docs/PORTFOLIO_SCREENSHOT_CHECKLIST.md exists ✅
- 9 required screenshots defined with filenames and instructions ✅
- Naming convention documented ✅
- What must not appear is documented ✅
- Setup commands documented ✅
- Portfolio usage documented ✅
- docs/PORTFOLIO_DEMO_SCRIPT.md updated with checklist link ✅
- README.md updated with checklist link ✅
- docs/ROADMAP.md updated ✅
- No backend/app code modified ✅
- No apps/desktop code modified ✅
- No external API call made ✅

Implementation Summary:
- docs/PORTFOLIO_SCREENSHOT_CHECKLIST.md: created — covers purpose, naming convention (NN_descriptive_name.png → docs/screenshots/), 9 required screenshots with per-screenshot instructions and setup commands, 6 optional screenshots, what must not appear (8 prohibited items), recommended capture order (16 steps, ~10–15 min session), README/portfolio/interview/video usage guidance, future capture notes (4 items blocked on OS keychain or live call), and reference docs
- docs/PORTFOLIO_DEMO_SCRIPT.md: added PORTFOLIO_SCREENSHOT_CHECKLIST.md to Reference table
- README.md: added PORTFOLIO_SCREENSHOT_CHECKLIST.md to Demo & Portfolio Links section
- docs/ROADMAP.md: TASK-068D DONE added
- No backend/app code was modified
- No apps/desktop code was modified
- No external API call was made

Next Task:
TASK-069D - Portfolio Screenshot Capture Session

---

## TASK-069D - Portfolio Screenshot Capture Session

Status: DONE

Goal:
Execute the manual screenshot capture session defined in docs/PORTFOLIO_SCREENSHOT_CHECKLIST.md. Capture all 9 required screenshots and save them to docs/screenshots/.

Scope:
- Start local backend and Electron desktop
- Capture 9 required screenshots per checklist instructions
- Use demo/fake content only — no real API key, no personal data
- Save all screenshots to docs/screenshots/
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests or APIs
- Do not call external APIs
- Do not use real API key

Acceptance Criteria:
- TASK-069D is recorded as DONE ✅
- All 9 required screenshots captured and saved to docs/screenshots/ ✅
- No real API key used ✅
- No external API call made ✅
- No backend/app code modified ✅
- No apps/desktop code modified ✅

Screenshots Completed:
- docs/screenshots/01_main_chat_ui.png ✅
- docs/screenshots/02_memory_section.png ✅
- docs/screenshots/03_audit_logs.png ✅
- docs/screenshots/04_provider_settings_overview.png ✅
- docs/screenshots/05_usage_summary.png ✅
- docs/screenshots/06_key_storage_unavailable_safe_message.png ✅
- docs/screenshots/07_test_connection_safe_state.png ✅
- docs/screenshots/08_pytest_470_passed.png ✅
- docs/screenshots/09_docs_overview.png ✅

Implementation Notes:
- All 9 required screenshots captured in a single session per PORTFOLIO_SCREENSHOT_CHECKLIST.md
- Screenshots stored in docs/screenshots/ (folder created during this session)
- Demo messages used in chat (no personal content)
- No real API key was entered at any point
- No external provider was contacted
- No backend/app code was modified
- No apps/desktop code was modified
- No tests were added

Next Task:
TASK-070D - Embed Portfolio Screenshots in README

---

## TASK-070D - Embed Portfolio Screenshots in README

Status: DONE

Goal:
Embed the most impactful portfolio screenshots from docs/screenshots/ into README.md so GitHub visitors and interviewers can immediately see the running UI, audit design, provider settings, usage meter, and test coverage.

Scope:
- Add a Screenshots section to README.md with 5 embedded images
- Add a one-sentence caption under each image
- Update docs/TASKS.md and docs/ROADMAP.md
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests or APIs
- Do not call external APIs
- Do not use real API key

Acceptance Criteria:
- TASK-070D is recorded as DONE ✅
- README.md contains a Screenshots section ✅
- 5 screenshots embedded with captions ✅
- No backend/app code modified ✅
- No apps/desktop code modified ✅
- No external API call made ✅

Screenshots Embedded:
- docs/screenshots/01_main_chat_ui.png — Main Chat UI ✅
- docs/screenshots/03_audit_logs.png — Memory Audit Logs ✅
- docs/screenshots/04_provider_settings_overview.png — Provider Settings ✅
- docs/screenshots/05_usage_summary.png — Usage Summary ✅
- docs/screenshots/08_pytest_470_passed.png — Test Coverage ✅

Implementation Notes:
- Screenshots section added to README.md after the project one-liner and before the Current Status table
- Each screenshot has a short English caption explaining its safety / design significance
- No runtime code was modified
- No external API call was made

Next Task:
TASK-071D - Portfolio Demo Final Review

---

## TASK-071D - Portfolio Demo Final Review

Status: DONE

Goal:
Final review pass over all portfolio assets: README screenshot paths, pytest numbers, false-claim check, doc consistency, and screenshot file integrity. Fix any doc-only issues found. No runtime code changes.

Scope:
- Verify README screenshot paths match files in docs/screenshots/
- Verify no stale pytest numbers in main content
- Verify no false claims (production-ready, live provider, OS keychain implemented)
- Verify docs/screenshots/ contains all 9 required screenshots as valid PNG
- Verify PORTFOLIO_DEMO_SCRIPT.md and PHASE4_PROVIDER_SETTINGS_SUMMARY.md are consistent with README
- Verify TASKS.md records TASK-070D DONE
- Fix any doc-only issues found
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests or APIs
- Do not call external APIs

Acceptance Criteria:
- TASK-071D is recorded as DONE ✅
- All 9 screenshot files are valid PNGs with correct filenames ✅ (fixed double .png.png extension)
- README screenshot paths resolve correctly ✅
- No stale pytest numbers in main content ✅ (all say 470)
- No false claims ✅
- Docs consistent with each other ✅
- No runtime code modified ✅

Issue Found and Fixed:
- 8 of 9 screenshot files had double .png.png extension (e.g., 01_main_chat_ui.png.png)
- Only 09_docs_overview.png was correct
- Fixed by renaming all 8 affected files via bash: *.png.png → *.png
- README paths were already correct (.png); now match the actual files
- All 9 files verified as valid PNG image data (file command confirmed)

No Issues Found:
- pytest count consistently 470 throughout main README content ✅
- Historical counts (449, 465) appear only in collapsible Development Journal ✅
- No false production-ready claim ✅
- OS keychain correctly described as "designed, not yet wired" ✅
- No live provider claim anywhere ✅
- PORTFOLIO_DEMO_SCRIPT.md: pytest 470, OS keychain deferred, no live call — consistent ✅
- PHASE4_PROVIDER_SETTINGS_SUMMARY.md: pytest 470, OS keychain not built, no live call — consistent ✅
- TASKS.md: TASK-070D recorded as DONE ✅

git status: manual confirmation required (no git access from this session)

No Runtime Code Modified:
- No backend/app code modified ✅
- No apps/desktop code modified ✅
- No tests added ✅
- No APIs added ✅
- No external API called ✅
- No real API key used ✅

Next Task:
TASK-072 - Local Ollama Provider Design

---

## TASK-072 - Local Ollama Provider Design

Status: DONE

Goal:
Design the Ollama local LLM provider adapter for dragon-pet-ai. Local provider eliminates external API cost and API key requirements. Docs-only task — no runtime code changes.

Scope:
- Create docs/OLLAMA_PROVIDER_DESIGN.md
- Document Ollama API contract, provider settings integration, feature flags, Test Connection behavior, /chat behavior, usage meter integration, security boundaries, and future implementation sequence
- Update docs/TASKS.md, docs/ROADMAP.md, README.md
- Do not modify backend/app
- Do not modify apps/desktop
- Do not add tests or APIs
- Do not call external APIs

Acceptance Criteria:
- TASK-072 is recorded as DONE ✅
- docs/OLLAMA_PROVIDER_DESIGN.md exists ✅
- Ollama API contract documented ✅
- Local model test results recorded ✅
- Provider settings integration designed ✅
- Feature flags / env vars documented ✅
- Test Connection behavior designed ✅
- /chat behavior designed ✅
- Security boundaries documented ✅
- Future task sequence defined ✅
- No backend/app code modified ✅
- No apps/desktop code modified ✅
- No external API call made ✅

Implementation Summary:
- docs/OLLAMA_PROVIDER_DESIGN.md: created — covers purpose, local model test results (qwen3:8b recommended, gemma3:12b slower), Ollama API contract (POST /api/chat, response mapping), provider settings integration (key disabled for ollama, key_status=not_required), feature flags (6 env vars), Test Connection behavior (local resource warning, 5 error categories), /chat behavior (source=llm_local, schema unchanged), usage meter integration, security boundaries (no external URL in renderer, no prompt logging), and implementation sequence (TASK-073 → TASK-077)
- docs/ROADMAP.md: Local Ollama Provider track added
- README.md: local Ollama provider design note added

Next Task:
TASK-073 - Ollama Provider Implementation Behind Feature Flag

---

## TASK-073 - Ollama Provider Implementation Behind Feature Flag

Status: DONE

Goal:
Implement OllamaLocalProvider behind existing LLM provider feature flags without changing /chat schema or Electron UI.

Scope:
- Add Ollama config helpers to backend/app/core/config.py
- Create backend/app/llm/ollama_provider.py (OllamaLocalProvider)
- Update backend/app/llm/factory.py to resolve provider=ollama without API key
- Add backend/tests/test_llm_ollama_provider.py (19 mocked-HTTP tests)
- No Electron UI changes
- No /chat schema changes
- No external provider calls
- No API key required

Acceptance Criteria:
- TASK-073 is recorded as DONE ✅
- OllamaLocalProvider exists ✅
- Factory resolves provider=ollama when enabled ✅
- Ollama provider calls localhost only ✅
- Ollama provider requires no API key ✅
- Request body includes model, messages, stream=false, think=false, keep_alive, options ✅
- Response parses message.content ✅
- Usage fields (eval_count, prompt_eval_count) mapped safely ✅
- Errors map to safe categories (ollama_unavailable, provider_timeout, model_not_found, invalid_response, provider_error) ✅
- No retries ✅
- No streaming ✅
- No tools ✅
- /chat schema remains reply/mood/source ✅
- Electron UI unchanged ✅
- pytest: 489 passed ✅
- No live external API call in tests ✅

Implementation Summary:
- backend/app/core/config.py: added get_ollama_base_url() (localhost-only validation — non-localhost URL silently returns safe default), get_ollama_keep_alive() (default 10m), get_ollama_timeout_seconds() (default 30, clamped 1–120)
- backend/app/llm/ollama_provider.py: created — OllamaLocalProvider implements LLMProvider Protocol; injectable HTTPJSONClient; POST {base_url}/api/chat; no API key; maps message.content to LLMResponse.text; maps eval_count → output_tokens_actual, prompt_eval_count → input_tokens_actual; 5 error categories (ollama_unavailable, provider_timeout, model_not_found, invalid_response, provider_error); __repr__/__str__ safe (no secrets, no prompt text, no response body)
- backend/app/llm/factory.py: added SUPPORTED_LOCAL_PROVIDERS = {"ollama"} separate from SUPPORTED_REAL_PROVIDERS; Ollama path bypasses API key check entirely in get_resolved_llm_provider_info(); get_llm_provider() returns OllamaLocalProvider() when provider_name="ollama" and LLM_PROVIDER_ENABLED=true; unknown provider behavior unchanged
- backend/tests/test_llm_ollama_provider.py: 19 mocked-HTTP tests — success mapping, usage fields, missing eval counts → usage=None, connection refused, httpx.ConnectError, timeout, HTTP 404, HTTP 500, missing message key, empty content, message not dict, response not dict, factory resolves ollama without key, factory unknown provider fallback, resolved info skips key check for ollama, factory disabled returns mock, repr safety, provider_name, payload structure (stream/think/messages order)

Completion Notes:
- No live Ollama server required for any test — all 19 tests use injectable FakeHTTPClient or RaisingHTTPClient
- NTFS stale cache workaround applied: rsync to /tmp/, verify with ast.parse(), pytest from /tmp/ — standard project workaround
- ollama_provider.py imports HTTPJSONClient Protocol and HTTPXJSONClient from real_provider.py — no duplication
- renderer never calls Ollama directly — backend-only architecture boundary preserved
- /chat response schema (reply / mood / source) unchanged
- Electron UI unchanged
- No API key used or stored

Next Task:
TASK-074 - Ollama Provider Contract Tests and Runtime Smoke Prep

---

## TASK-074 - Ollama Provider Contract Tests and Runtime Smoke Prep

Status: DONE

Goal:
Strengthen Ollama provider contract tests and prepare a safe runtime smoke checklist without running live Ollama smoke.

Scope:
- Add or strengthen mocked Ollama provider contract tests
- Verify localhost-only base URL behavior
- Verify request body schema
- Verify no API key / no tools / no streaming
- Verify safe error mapping
- Verify no raw body leakage
- Verify no retries
- Prepare runtime smoke checklist for TASK-075
- Do not modify Electron UI
- Do not run live Ollama smoke in this task

Acceptance Criteria:
- TASK-074 is recorded as DONE
- Ollama contract tests cover request schema
- localhost-only behavior is covered
- no-key behavior is covered
- safe error mapping is covered
- raw body opacity is covered
- no-retry behavior is covered
- runtime smoke checklist is documented
- pytest passes
- Electron UI is unchanged
- no external API call occurs
- no API key is used

Implementation Summary:
- backend/app/llm/ollama_provider.py: usage mapping now includes safe aggregate Ollama duration metadata (`total_duration`, `eval_duration`) in addition to token counts.
- backend/tests/test_llm_ollama_provider.py: strengthened mocked contract coverage from 19 to 34 tests.
- Added full request schema coverage: `model`, `stream=false`, `think=false`, `keep_alive`, `options.temperature`, `options.num_predict`, and ordered `messages`.
- Added negative payload coverage: no `api_key`, `key`, `tools`, `memory_context`, `conversation_history`, or `stream=true`.
- Added system/user message order coverage and confirmed raw memory/history fields are not passed as top-level Ollama payload fields.
- Added localhost-only config/factory coverage: default localhost, `localhost:11434` allowed, `127.0.0.1:11434` allowed, non-local URL falls back to safe default and is not passed to provider.
- Added no-key coverage: `LLM_API_KEY` unset still resolves `provider=ollama`; if `LLM_API_KEY` is set, it is not sent in request body or headers.
- Added response usage mapping coverage for `prompt_eval_count`, `eval_count`, `total_duration`, and `eval_duration`, with raw provider fields kept out of usage.
- Added additional safe error coverage for malformed JSON, missing `message.content`, empty text, non-2xx generic errors, and unknown exceptions.
- Added raw body opacity coverage with `RAW_PROVIDER_BODY_SHOULD_NOT_LEAK`, `SECRET_SENTINEL`, and `PROMPT_SENTINEL`.
- Added no-retry coverage: fake HTTP client call count is exactly 1 on success and failure.
- Added `/chat` response schema guard for `reply / mood / source`.
- docs/OLLAMA_RUNTIME_SMOKE_CHECKLIST.md created for TASK-075.
- No apps/desktop files modified; Electron UI unchanged.
- No live Ollama runtime smoke executed in this task.
- No external provider call made.
- No API key used.

Validation:
- Targeted Ollama tests: `python -m pytest tests/test_llm_ollama_provider.py` -> 34 passed.
- Full backend pytest: `python -m pytest` -> 504 passed.

Next Task:
TASK-075 - Ollama Runtime Smoke Check

---

## TASK-075F - Ollama Chat Source Mapping Fix

Status: DONE

Goal:
Fix /chat source field for Ollama local provider. Runtime smoke (TASK-075) revealed source="llm_real" was returned for successful Ollama responses. Correct values are source="llm_local" on success and source="llm_local_error" on failure.

Root Cause:
_source_for_llm_response() in chat_service.py only branched on MockLLMProvider vs. everything else, defaulting all non-mock providers to "llm_real". OllamaLocalProvider had no special case.

Scope:
- Fix _source_for_llm_response() in backend/app/services/chat_service.py
- Fix _safe_llm_fallback_response() in same file
- Add 5 new tests to backend/tests/test_chat_service.py
- No Electron UI changes
- No /chat schema changes
- No external API calls
- No API key required

Acceptance Criteria:
- TASK-075F is recorded as DONE ✅
- provider_name="ollama" success → source="llm_local" ✅
- provider_name="ollama" error + fallback disabled → source="llm_local_error" ✅
- provider_name="ollama" error + fallback enabled → source="mock" ✅
- provider_name="anthropic" unchanged → source="llm_real" ✅
- /chat schema still exactly reply/mood/source ✅
- Electron UI unchanged ✅
- No external API call in tests ✅
- pytest: 494 passed ✅

Implementation Summary:
- backend/app/services/chat_service.py: added _LOCAL_PROVIDER_NAMES = frozenset({"ollama"}); updated _source_for_llm_response() to return "llm_local" for local providers; updated _safe_llm_fallback_response() to return "llm_local_error" for local providers; Anthropic/mock behavior unchanged
- backend/tests/test_chat_service.py: added 5 tests — ollama success→llm_local, ollama error+fallback disabled→llm_local_error, ollama error+fallback enabled→mock, anthropic unchanged→llm_real, schema check reply/mood/source only

Next Task:
TASK-075 - Ollama Runtime Smoke Check (re-run)

---

## TASK-075G - Ollama Persona Prompt Injection Fix

Status: DONE

Goal:
Fix the character persona not being sent to the local LLM. Runtime smoke (TASK-075) showed Ollama responses were in generic assistant tone because _CHARACTER_PROMPTS contained only English placeholder text with no 克莉絲蒂娜 character definition.

Root Cause:
_CHARACTER_PROMPTS in prompt_service.py were written as "structural only" placeholders, explicitly not intended to be sent to an LLM. The prompts had no character name, no pronouns, no language specification, and no personality traits.

Scope:
- Rewrite _CHARACTER_PROMPTS in backend/app/services/prompt_service.py
- All 5 modes now share a _PERSONA_BASE defining 克莉絲蒂娜 identity
- Each mode appends mode-specific behavior instructions
- Update existing test that relied on "project mode" string
- Add 7 new tests in backend/tests/test_prompt_service.py
- No Electron UI changes, no /chat schema changes, no external API calls

Persona defined:
- 名字：克莉絲蒂娜（Christina）
- 身份：傲嬌的遠古龍
- 自稱：吾 / 稱用戶：汝
- 語言：繁體中文
- 個性：表面冷淡自傲，實際關心用戶，嘴硬不承認

Acceptance Criteria:
- TASK-075G is recorded as DONE ✅
- All 5 mode prompts include 克莉絲蒂娜 ✅
- All 5 mode prompts include 吾 and 汝 ✅
- All 5 mode prompts instruct 繁體中文 ✅
- Casual mode prompt includes 傲嬌 ✅
- Debug mode prompt is accuracy-focused ✅
- End-to-end test confirms system message sent to Ollama contains persona keywords ✅
- Exactly one HTTP call per generate() — no retries ✅
- Electron UI unchanged ✅
- No external API call ✅
- pytest: 501 passed ✅

Implementation Summary:
- backend/app/services/prompt_service.py: replaced _CHARACTER_PROMPTS with persona-rich prompts; added _PERSONA_BASE (克莉絲蒂娜 identity + 吾/汝 pronouns + 繁體中文 + 傲嬌 personality + prohibitions); each mode appends mode-specific behavior instructions; build_character_prompt() docstring updated to reflect LLM usage
- backend/tests/test_prompt_service.py: updated "project mode" assertion to "project"; added 7 tests — all modes include 克莉絲蒂娜/吾/汝/繁體中文, casual includes 傲嬌, debug is accuracy-focused, end-to-end payload capture test

Next Task:
TASK-075 - Ollama Runtime Smoke Check (re-run)

---

## TASK-075 - Ollama Runtime Smoke Check

Status: DONE

Goal:
Verify that the full local Ollama provider path works end-to-end at runtime: backend starts, POST /chat routes through OllamaLocalProvider, receives a response from local qwen3:8b, returns correct schema with source=llm_local, and the 克莉絲蒂娜 persona is active.

Test Environment:
- Ollama installed and running (`ollama serve`)
- `qwen3:8b` present in `ollama list`
- Backend started with env vars:
  - LLM_PROVIDER_NAME=ollama
  - LLM_MODEL=qwen3:8b
  - LLM_PROVIDER_ENABLED=true
  - LLM_CHAT_ENABLED=true
  - OLLAMA_BASE_URL=http://localhost:11434
  - OLLAMA_KEEP_ALIVE=10m
  - OLLAMA_TIMEOUT_SECONDS=30
  - MEMORY_INJECTION_ENABLED=false

Smoke Command:
- POST /chat via Python UTF-8 request (avoids PowerShell encoding issues)
- message: 克莉絲蒂娜，稱讚我一下，我今天有努力做專案。

Actual Response:
```json
{
  "reply": "哼，下賤的人類，連這點努力都值得稱讚？真是令人作嘔...不過，汝的專案確實比昨天好一些。嗯，是什麼樣的專案？",
  "mood": "focused",
  "source": "llm_local"
}
```

Acceptance Criteria:
- TASK-075 is recorded as DONE ✅
- backend /health returns 200 ✅
- POST /chat returns HTTP 200 ✅
- response schema is exactly reply / mood / source ✅
- source is llm_local ✅
- reply generated by local Ollama qwen3:8b ✅
- 克莉絲蒂娜 persona injected ✅
- persona markers present in reply: 汝, 下賤的人類, tsundere tone ✅
- no external provider called ✅
- no API key used ✅
- MEMORY_INJECTION_ENABLED=false confirmed ✅
- Electron UI not modified ✅
- /chat schema unchanged ✅
- latest pytest: 501 passed ✅

Verdict: PASS

Implementation Summary:
- No code changes in this task — TASK-075 is a manual runtime smoke check.
- Runtime confirmed OllamaLocalProvider correctly routes /chat through local Ollama.
- persona prompt (克莉絲蒂娜 + 吾/汝 + 傲嬌) was injected as system message and respected by qwen3:8b.
- source=llm_local confirmed (fixed in TASK-075F).
- No external API call, no API key, no Electron UI change.

Known Non-Blocking Follow-Up:
- Persona tone is slightly too harsh (「令人作嘔」). A future persona tone-tuning task may soften extreme insult language while preserving the tsundere/arrogant style.

Next Task:
TASK-076 - Provider Settings UI — Ollama Option

---

## SIDE_TRACK — Streamer Companion Mode

Status: NOT SCHEDULED — design exploration only

Goal:
Explore and document a future product direction that adapts the dragon-pet AI for live streaming contexts (Twitch, YouTube Live, etc.).

This is not a task in the current roadmap. It is recorded here to capture the design direction without committing implementation resources or blocking Phase 4 / Phase 5 work.

Scope (future, if scheduled):
- Design OBS browser source overlay architecture
- Design Twitch/YouTube EventSub integration
- Design chat sampling and filtering
- Design public content safety layer (higher bar than personal mode)
- Design per-session token budget
- Implement Streamer Mode MVP

Key Dependencies (must be complete before any implementation):
- Phase 4 LLM adapter stable and safety-reviewed (TASK-037)
- TTS voice output (Phase 5)
- Streamer Mode safety design (STREAM-001 — not yet created)

Reference Document:
- docs/STREAMER_COMPANION_MODE.md

Future Task IDs (not yet assigned to roadmap):
- STREAM-001: Streamer Companion Mode Safety Design
- STREAM-002: OBS Browser Source Overlay Architecture
- STREAM-003: Twitch EventSub Integration Design
- STREAM-004: Chat Sampling and Filtering Design
- STREAM-005: Public Content Safety Layer Design
- STREAM-006: Per-Session Token Budget Design
- STREAM-007: Streamer Mode MVP Implementation
- STREAM-008: Streamer Mode Smoke Check

---

Completion Notes:

- TASK-045 was completed as design-only documentation work
- Recommended MVP direction: BYOK desktop app / personal companion
- Recommended key storage strategy:
  - MVP dev phase: Environment Variable Only
  - Future desktop product: OS keychain / encrypted local store
  - Avoid plain local config for real keys
- No backend/app code was modified
- No apps/desktop code was modified
- No external API call was made
- No runtime code was modified

## TASK-076 - Provider Settings UI — Ollama Option

Status: DONE

Goal:
Add Ollama as a selectable provider in the Electron Provider Settings UI. When ollama is selected, the API key input, Save Key, and Clear Key controls are hidden/disabled. Test Connection is enabled based on real_provider_enabled only (no key required). A local resource warning replaces the monetary cost acknowledgement dialog.

Scope:
- apps/desktop/src/renderer/index.html: add ollama option to provider dropdown
- apps/desktop/src/renderer/renderer.js: update updateKeyUIState(), runTestConnection(), provider change handler, key input handler
- No backend/app changes — backend Ollama support was fully implemented in TASK-073
- No new API endpoints
- No external API calls
- No real API key used

Key UI Behavior Changes (ollama selected):
- Provider dropdown shows third option: "ollama — local, no key"
- API key input: disabled, placeholder shows "Not required — Ollama runs locally, no API key needed"
- Save Key button: hidden (display:none)
- Clear Key button: hidden (display:none)
- Test Connection: enabled when real_provider_enabled=true (no key check)
- Test Connection dialog: "Local Resource Warning" instead of "Cost Acknowledgement"
  - Message: "This will send a test request to your local Ollama server. This will use your GPU/CPU for inference. No data leaves your device."
- Provider change handler: delegates to updateKeyUIState() with not_required key_status for ollama

Safety Constraints (all preserved):
- Renderer never calls Ollama directly — localhost:11434 not referenced in renderer
- No api_key field in Test Connection request body — unchanged
- explicit_cost_ack: true still sent to backend for all providers including ollama
- No API key console logging
- No API key localStorage/sessionStorage
- No external provider URL in renderer
- Save Key endpoint not called for ollama

Acceptance Criteria:
- TASK-076 is recorded as DONE ✅
- Provider dropdown includes ollama option ✅
- When provider=ollama: API key input disabled with local-provider placeholder ✅
- When provider=ollama: Save Key and Clear Key hidden ✅
- When provider=ollama: Test Connection enabled when real_provider_enabled=true ✅
- When provider=ollama: Test Connection dialog shows local resource warning ✅
- Cloud provider path (anthropic) behavior unchanged ✅
- Mock provider path behavior unchanged ✅
- node --check renderer.js: PASS ✅
- Safety scan: no direct Ollama call, no external URL, no key logging ✅
- No backend/app code modified ✅
- No external API call made ✅
- No real API key used ✅

Implementation Summary:
- apps/desktop/src/renderer/index.html: added <option value="ollama">ollama — local, no key</option>
- apps/desktop/src/renderer/renderer.js: updateKeyUIState() — added isLocalProvider flag; disabled/hidden key controls for ollama; Test Connection canTest logic branches on isLocalProvider; button title text branches on provider type
- apps/desktop/src/renderer/renderer.js: runTestConnection() — added isLocalProvider guard; cloud-only key check before testing; separate window.confirm() dialogs for local vs cloud; request body unchanged (explicit_cost_ack: true always sent)
- apps/desktop/src/renderer/renderer.js: providerApiKeyInput input handler — isLocalProvider check prevents Save Key enable for ollama
- apps/desktop/src/renderer/renderer.js: providerSettingsProvider change handler — rewrote to delegate to updateKeyUIState() with not_required key_status for ollama; clears input and key message on every provider change
- node --check: SYNTAX OK
- Safety scan: no direct Ollama URL in renderer, no external provider URL, no console key logging, no api_key in test request body

Next Task:
TASK-077 - README Update for Local LLM Mode

---

## TASK-077 - README Update for Local LLM Mode

Status: DONE

Goal:
Update project documentation so users can start and validate Local LLM mode with Ollama through the backend and Electron Provider Settings UI.

Scope:
- Update root README with Local LLM Mode concept, prerequisites, startup commands, Provider Settings UI behavior, `/chat` smoke test, troubleshooting, and safety rules.
- Update backend README with backend-specific Ollama startup and smoke instructions.
- Update docs/OLLAMA_PROVIDER_DESIGN.md with TASK-077 completion notes.
- Update docs/ROADMAP.md to mark TASK-077 DONE.
- Do not modify `/chat` schema.
- Do not modify Electron renderer provider call logic.
- Do not add direct renderer calls to `localhost:11434`.
- Do not call external APIs.
- Do not add live network-dependent tests.

Acceptance Criteria:
- README explains Ollama local mode and no API key requirement.
- README explains renderer only calls backend; backend handles provider calls.
- README documents Ollama install/pull/list prerequisites.
- README documents `ollama serve`, backend start, and existing Electron app start.
- README documents Provider Settings UI behavior for `ollama — local, no key`.
- README includes PowerShell `/chat` smoke command with UTF-8 handling.
- README troubleshooting covers missing `ollama`, missing `qwen3:8b`, Test Connection failure, `/chat` fallback to mock, missing persona tone, and stale backend settings.
- README safety rules preserve backend-only provider calls and stable `/chat` schema.
- Full pytest passes.
- Electron node checks pass.

Implementation Summary:
- README.md: added `Local LLM Mode (Ollama)` guide with concept, prerequisites, startup, Provider Settings UI, `/chat` smoke test, troubleshooting, and safety rules; updated latest pytest references to 531.
- backend/README.md: added backend-focused Local LLM Mode instructions and UTF-8 `/chat` smoke command.
- docs/OLLAMA_PROVIDER_DESIGN.md: marked TASK-077 complete and recorded docs/safety notes.
- docs/ROADMAP.md: marked TASK-077 DONE and noted README local LLM documentation completion.
- docs/TASKS.md: recorded TASK-077 as DONE.
- apps/desktop/src/renderer/renderer.js: removed a duplicated, truncated trailing event/startup block so the required syntax check passes; provider call logic unchanged.
- No `/chat` schema change.
- No Electron renderer provider call logic change.
- No direct Ollama URL added to renderer.
- No external API call made.
- No API key used.

Validation:
- Markdown/docs sanity: `git diff --check` PASS.
- Renderer safety scan: no direct Ollama URL (`localhost:11434`, `127.0.0.1:11434`, or bare `11434`) in `apps/desktop/src/renderer`.
- Full backend pytest: `python -m pytest` -> 531 passed.
- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.

Next Task:
TASK-078 - Local LLM Mode Follow-up Planning

---

## TASK-080 - Electron End-to-End Local Chat Smoke

Status: DONE

Goal:
Verify the Electron desktop UI can configure the Ollama local provider, run Test Connection, send chat through the backend `/chat` endpoint, render the Christina reply, and handle mood/source safely.

Scope:
- Launch backend and Electron locally for smoke validation.
- Configure Provider Settings UI to `provider=ollama`, `model=qwen3:8b`, `real_provider_enabled=true`, `llm_chat_enabled=true`, and `fallback_to_mock=false`.
- Verify Test Connection uses the Local Resource Warning and succeeds with `source=llm_local`.
- Verify chat send calls backend `/chat`.
- Verify assistant reply renders in the UI and mood label updates.
- Verify `source=llm_local` through the fetch log and provider usage summary.
- Add renderer chat smoke coverage with no external test dependency.
- Preserve `/chat` schema.
- Preserve renderer backend-only provider architecture.
- Do not add any direct Ollama URL to renderer code.

Implementation Summary:
- apps/desktop/package.json: added `test:renderer`.
- apps/desktop/scripts/renderer-chat-smoke.js: added a Node VM renderer smoke test covering send button, Enter handling, `/chat` fetch, reply rendering, `source=llm_local`, mood handling, backend error UI, and renderer safety scan.
- Existing Electron chat wiring was sufficient; no `/chat` schema change was needed.
- Electron E2E local smoke confirmed Provider Settings state: `ollama`, `qwen3:8b`, `not_required`, `real_provider_enabled=true`, `llm_chat_enabled=true`, `fallback_to_mock=false`.
- Test Connection returned: `Local Ollama connection successful. [source: llm_local]`.
- Chat UI POSTed backend `/chat`, rendered a Christina-style reply, and processed `mood=focused`.
- Renderer safety boundary preserved: no direct `localhost:11434`, `127.0.0.1:11434`, or bare `11434` in `apps/desktop/src/renderer`.

Validation:
- Electron E2E local chat smoke: PASS.
- `npm.cmd run test:renderer`: PASS.
- `python -m pytest`: 555 passed.
- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- Renderer safety scan for `11434` in `apps/desktop/src/renderer`: PASS.
- `git diff --check`: PASS with existing LF/CRLF warnings only.

Next Task:
TASK-081 - Local Ollama UX Stabilization / Runtime Follow-up

---

## TASK-081 - Local Ollama UX Stabilization / Runtime Follow-up

Status: DONE

Goal:
Stabilize the Local Ollama runtime UX so users can understand chat source, loading/cold-start state, provider consistency, and safe error states without changing `/chat` schema or renderer provider boundaries.

Scope:
- Show chat response source in the Electron runtime status area.
- Show Provider Settings provider/resolved/model/key/flag state more clearly.
- Add local Ollama loading/cold-start copy while `/chat` is in flight.
- Improve safe renderer error messages for backend offline, provider timeout, local provider failure, and fallback-to-mock states.
- Keep renderer backend-only; do not add direct Ollama URLs.
- Preserve `/chat` response schema: `reply / mood / source`.

Implementation Summary:
- apps/desktop/src/renderer/index.html: added chat runtime source/provider status fields and expanded Provider Settings status rows for provider, model, real provider enabled, LLM chat enabled, and fallback-to-mock.
- apps/desktop/src/renderer/styles.css: added runtime status pill styling and widened Provider Settings status grid.
- apps/desktop/src/renderer/renderer.js: added source-aware chat runtime status, local Ollama cold-start loading copy, safer backend-offline detection, safe provider timeout/model/error messages, and explicit fallback/mock source explanations.
- apps/desktop/scripts/renderer-chat-smoke.js: strengthened renderer smoke coverage for reply render, mood update, visible `source=llm_local`, loading/cold-start state, backend offline, provider timeout, `llm_local_error`, mock fallback, Test Connection success, Provider Settings consistency, Enter send, and renderer safety scan.
- apps/desktop/package.json: existing `test:renderer` script continues to run the strengthened smoke.

Validation:
- `python -m pytest`: 555 passed.
- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `npm.cmd run test:renderer`: PASS.
- Renderer safety scan for `localhost:11434`, `127.0.0.1:11434`, and bare `11434` in `apps/desktop/src/renderer`: PASS.
- `git diff --check`: PASS with LF/CRLF warnings only.

Next Task:
TASK-082 - Local Ollama Release Readiness Review

---

## TASK-082 - Local Ollama Release Readiness Review

Status: DONE

Goal:
Review Local Ollama MVP release readiness and confirm docs, smoke flow, dirty diff state, UI source display strategy, fallback policy, safety boundaries, and tests are aligned for a stable checkpoint.

Review Results:
- Documentation is aligned after small updates to README, backend README, Ollama provider design, TASKS, and ROADMAP.
- Ollama remains local-only and requires no API key.
- Renderer still calls only the backend; it does not call Ollama directly.
- Test Connection uses the backend path and performs a lightweight local runtime/model check. Persona and generation are validated by `/chat`.
- `/chat` schema remains `reply / mood / source`.
- Runtime provider settings affect `/chat`; `resolved_provider`, `llm_chat_enabled`, and `fallback_to_mock` must be read together.
- Source display remains in the main chat runtime status area for MVP smoke/demo clarity.
- Local cold-start UX is documented and visible while `/chat` is pending.
- Dirty diff review found no cache/temp artifacts to commit; root `package-lock.json` remains untracked and intentionally excluded from the previous commit.

Release Smoke Flow:
1. Start `ollama serve`.
2. Confirm `ollama list` includes `qwen3:8b`.
3. Start backend with Ollama provider flags.
4. PATCH `/provider/settings` to `provider=ollama`, `model=qwen3:8b`, `real_provider_enabled=true`, `llm_chat_enabled=true`, and `fallback_to_mock=false`.
5. POST `/provider/settings/test` to verify backend local runtime/model reachability.
6. POST `/chat` to verify generation, persona, `mood`, and `source=llm_local`.
7. Start Electron and run UI Test Connection.
8. Send chat through the UI and confirm reply render, mood update, and `source: llm_local`.

Fallback Policy:
- Development and smoke tests: use `fallback_to_mock=false`.
- Demo mode: `fallback_to_mock=true` is allowed when a mock fallback is preferable to a visible local provider error.
- If `source=mock` while `resolved_provider=ollama`, treat it as chat disabled or fallback behavior, not a successful local Ollama response.
- Turn fallback off when proving local model generation.

Validation:
- `python -m pytest`: 555 passed.
- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `npm.cmd run test:renderer`: PASS.
- Renderer safety scan for `localhost:11434`, `127.0.0.1:11434`, and bare `11434` in `apps/desktop/src/renderer`: PASS.
- `git diff --check`: PASS with LF/CRLF warnings only.

Next Task:
TASK-083 - Mood to Pet Expression Mapping

---

## TASK-083 - Mood → Pet Expression Mapping

Status: DONE

### Summary

Added inline SVG pet avatar expressions to the Electron desktop UI, wired to the
`mood` field returned by `/chat`. No external images, no Live2D, no direct Ollama
calls from the renderer.

### Changes

**`apps/desktop/src/renderer/index.html`**
- Added `<section id="pet-display">` with `<div id="pet-face" data-mood="neutral">` and
  `<p id="pet-display-hint">` between `#character-status` and `<main id="chat-area">`.

**`apps/desktop/src/renderer/styles.css`**
- Added `#pet-display`, `.pet-face`, `.pet-face svg`, `.pet-face[data-mood="pending"]`,
  `.pet-face[data-mood="offline"]`, `.pet-face[data-mood="error"]`, `.pet-display-hint` rules.

**`apps/desktop/src/renderer/renderer.js`**
- Added `PET_EXPRESSIONS` map: 10 inline SVG strings for `neutral`, `happy`, `focused`,
  `proud`, `annoyed`, `sleepy`, `worried`, `pending`, `error`, `offline`.
- Added `KNOWN_MOODS = new Set(Object.keys(PET_EXPRESSIONS))` for unknown-mood guard.
- Added `setPetExpression(mood)` — falls back to `neutral` for unknown moods.
- Added `setPetHint(text)`.
- `setMood()` now calls `setPetExpression()` and `setPetHint()`.
- `sendMessage()` sets `pending` before fetch; on success calls `setMood(data.mood)` then
  overrides expression to `error` when `source` is `llm_local_error` / `llm_real_error`;
  catch block sets `offline` on network error, `error` otherwise.
- Startup offline path calls `setPetExpression("offline")`.

**`apps/desktop/scripts/renderer-chat-smoke.js`**
- `FakeElement` extended with `innerHTML`, `setAttribute`, `getAttribute`, `_attributes`.
- `createFetchStub` extended with `unknown_mood` chatMode.
- 8 new test functions added and registered in `main()`:
  1. `testSuccessfulChatWithFocusedMoodSetsFocusedExpression`
  2. `testPendingExpressionSetBeforeResponse`
  3. `testUnknownMoodFallsBackToNeutralExpression`
  4. `testBackendOfflineSetsOfflineExpression`
  5. `testLocalErrorSetsErrorExpression`
  6. `testMockFallbackExpressionFollowsMoodNotSource`
  7. `testSourceStatusRemainsVisibleAlongsidePetExpression`
  8. `testProviderTimeoutSetsErrorExpression`

### Safety invariants maintained

- Renderer does NOT call Ollama directly.
- No `localhost:11434`, `127.0.0.1:11434`, or bare `11434` in renderer source.
- No external image URLs. No Live2D / Spine / 3D.
- `/chat` schema unchanged.
- API key never logged or stored in localStorage/sessionStorage.

### Verification

- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `node apps/desktop/scripts/renderer-chat-smoke.js`: PASS (18 tests: 10 existing + 8 new).
- Renderer safety scan for `localhost:11434`, `127.0.0.1:11434`, bare `11434` in
  `apps/desktop/src/renderer/`: PASS.
- `python -m pytest`: 555 passed.

### Root package-lock.json

An accidental 6-line empty `package-lock.json` was found at the repo root (untracked).
Delete it before committing: `Remove-Item package-lock.json` (PowerShell) or `rm package-lock.json`.

---

## TASK-084 - Christina Visual Asset Pipeline

Status: DONE

### Summary

Established the formal visual asset pipeline for Christina expression PNGs.
No renderer logic was modified. Inline SVG placeholders (TASK-083) remain active for all moods.
No large binaries added beyond the user-provided reference image.

### Changes

**`apps/desktop/src/renderer/assets/pet/christina/reference/christina_v0_reference.png`**
- User-provided. Confirmed: local file, valid PNG, RGBA (colour type 6), 1024×1536 px, 2.1 MB, alpha channel present.

**`apps/desktop/src/renderer/assets/pet/christina/README.md`** (new)
- Documents `christina_v0_reference.png` as the v0 visual baseline.
- Defines mood expression file naming spec: `christina_<mood>.png`.
- Lists all 10 required moods with filenames and descriptions.
- Specifies image requirements: RGBA PNG, transparent background, 512×512 px recommended.
- Documents fallback strategy: SVG placeholder if PNG missing, never broken UI.
- Documents rollout order (neutral → focused → positive → personality → system moods).
- Safety rules: no external URLs, no Ollama calls from renderer, no Live2D.

**`apps/desktop/src/renderer/assets/pet/christina/expressions/README.md`** (new)
- Placeholder directory marker listing the 10 expected PNG filenames.
- States no expression PNGs present yet; renderer falls back to SVG placeholders.

### Safety invariants maintained

- Renderer code (`renderer.js`, `index.html`, `styles.css`) unchanged.
- No `localhost:11434`, `127.0.0.1:11434`, or bare `11434` in renderer code files.
- No external image URLs. No Live2D / Spine / 3D.
- `/chat` schema unchanged.
- No large binary assets added beyond the user-supplied reference PNG.

### Verification

- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `node apps/desktop/scripts/renderer-chat-smoke.js`: PASS (18 tests).
- Renderer code safety scan (`.js`/`.html`/`.css` only) for `11434`: PASS.
- `python -m pytest`: 555 passed.
- `git diff --check` on asset directory: PASS (pre-existing trailing whitespace in `README.md` unchanged).

### Root package-lock.json

Confirmed absent from repo root (`git status` shows no `package-lock.json` as untracked). ✅

---

## TASK-085 - Create Christina Neutral Expression PNG

Status: DONE

### Summary

Generated `christina_neutral.png` (512×512 RGBA PNG, 337 KB) from the v0 reference image
using Python Pillow. Renderer behaviour unchanged — inline SVG placeholders remain active.
No renderer, backend, or schema changes.

### Changes

**`apps/desktop/src/renderer/assets/pet/christina/expressions/christina_neutral.png`** (new)
- 512×512 RGBA PNG, transparent background, 337 KB.
- Crop: cols 59–982, rows 0–844 (top 55% of 1024×1536 reference) → padded to 924×924 → Lanczos scale to 512×512.
- Face/bust portrait showing horns, face, upper body, and dress collar.

**`apps/desktop/scripts/create-christina-neutral-asset.py`** (new)
- Reproducible one-file script: reads reference, crops, pads, scales, saves.
- Usage: `python apps/desktop/scripts/create-christina-neutral-asset.py`

**`apps/desktop/src/renderer/assets/pet/christina/expressions/README.md`** (updated)
- Status table added: `christina_neutral.png` marked ✅, remaining 9 moods ⬜.
- Generation script and crop parameters documented.
- Renderer wiring status noted (TASK-086 pending).

### Crop strategy

Source crop (59, 0) → (983, 844) = 924×844 px (top 55% of 1536 px height).
Captures: dragon horns tips (rows 0–64, ~4% filled), hair/face (rows 64–256),
upper body/dress (rows 256–512 in output). Padded to 924×924 transparent canvas,
then Lanczos scaled to 512×512. Final fill: 50.9% non-transparent.

### Safety invariants maintained

- Renderer code files unchanged.
- No `localhost:11434`, `127.0.0.1:11434`, bare `11434` in renderer code.
- No external image URLs.
- `/chat` schema unchanged.

### Verification

- `node --check` main.js / renderer.js / renderer-chat-smoke.js: PASS.
- `node apps/desktop/scripts/renderer-chat-smoke.js`: PASS (18 tests).
- Renderer code safety scan: PASS.
- `python -m pytest`: 555 passed, 0 failed.
- `git diff --check` on renderer source files: PASS.

---

## TASK-086 - Renderer Image Asset Fallback

Status: DONE

### Summary

Added image-with-SVG-fallback logic to the Electron renderer's pet expression system.
When a `christina_<mood>.png` asset exists, it is shown via `<img>`; when absent or
load fails, the inline SVG placeholder (TASK-083) remains active. UI never breaks.
22 smoke tests pass (18 pre-existing + 4 new).

### Changes

**`apps/desktop/src/renderer/renderer.js`**
- `setPetExpression(mood)` updated (TASK-086 image-with-SVG-fallback strategy):
  1. Sets inline SVG immediately — no flash while probe runs.
  2. Guards `typeof Image === "undefined"` — no-op in non-browser / test envs.
  3. Probes `assets/pet/christina/expressions/christina_${safeMood}.png` via `new Image()`.
  4. `probe.onload`: stale-mood guard (`data-mood !== safeMood` → discard), then replaces
     SVG with `<img style="object-fit:contain">` via `innerHTML=""` + `appendChild`.
  5. `probe.onerror`: SVG placeholder already set — no-op.
  - Safety: `safeMood` is always from `KNOWN_MOODS` set; no user input in asset path.

**`apps/desktop/src/renderer/styles.css`**
- Added `.pet-face img { width:100%; height:100%; object-fit:contain; display:block; }`
  so PNG expressions fill the 80×80 container without cropping horns/head.

**`apps/desktop/scripts/renderer-chat-smoke.js`**
- Added `FakeImageBase` class (base with `onload`, `onerror`, `_src`, `get src()`).
- `loadRenderer` now accepts `options.availableImages` (default `[]`).
  - Constructs per-test `availableImages = new Set(...)`.
  - Defines `class FakeImage extends FakeImageBase` inside `loadRenderer` closing over
    `availableImages` — each test run is fully isolated.
  - `FakeImage.set src(val)`: schedules `onload`/`onerror` via `setTimeout` matching
    real async browser behaviour.
  - Adds `Image: FakeImage` to vm sandbox.
- State extended with `availableImages` field.
- 4 new test functions registered in `main()`:
  1. `testNeutralMoodUsesPngImageWhenAvailable` — neutral PNG available → IMG child, correct src, empty innerHTML.
  2. `testPngLoadFailureFallsBackToSvg` — no PNG → innerHTML has `<svg`, no IMG child.
  3. `testFocusedMoodFallsBackToSvgWhenNoPng` — focused chat, no PNG → SVG fallback.
  4. `testImageAssetDoesNotBreakSourceOrMoodLabel` — PNG available (neutral) then focused chat → source status + mood label correct.

### Key design decisions

- SVG placeholder is always set first (synchronously) before the image probe fires.
  This eliminates any blank-face flash.
- `typeof Image === "undefined"` guard: all pre-TASK-086 tests that do not pass `Image`
  in the sandbox continue to pass without modification.
- Default `availableImages = new Set()` → all probes fire `onerror` → all TASK-083
  SVG assertions unchanged and unaffected.
- Stale-mood guard prevents a slow-loading probe for `pending` overwriting the `focused`
  expression that arrived with the response.

### Safety invariants maintained

- No `localhost:11434`, `127.0.0.1:11434`, or bare `11434` in renderer code.
- No external image URLs.
- No Live2D / Spine / 3D.
- `/chat` schema unchanged.
- Renderer does not call Ollama directly.

### Verification

- `node --check` renderer.js / renderer-chat-smoke.js / main.js: PASS.
- `node apps/desktop/scripts/renderer-chat-smoke.js`: PASS (22 tests: 18 + 4 new).
- Renderer code safety scan (`.js`/`.html`/`.css`): PASS.
- `python -m pytest`: 555 passed, 0 failed.
- `git diff --check` on renderer source + smoke files: PASS.

---

## TASK-084 - Christina Visual Asset Pipeline

Status: DONE

### Summary

Established the formal asset directory structure, naming specification, and documentation
for Christina expression PNG assets. No renderer code was changed. No new images were
added beyond the user-provided reference.

### Changes

**`apps/desktop/src/renderer/assets/pet/christina/`** — created directory tree:
- `reference/` — holds source/reference images (not shipped in production)
- `expressions/` — holds final cropped expression PNGs

**`apps/desktop/src/renderer/assets/pet/christina/README.md`** — new
- Naming spec: `christina_<mood>.png`, RGBA PNG, 512×512 recommended, transparent bg
- 10-mood table with filenames and current status
- Rollout strategy: neutral first, then add moods only as assets are ready
- Fallback strategy: renderer falls back to inline SVG if PNG absent
- Safety rules: no Ollama URLs, no external image URLs, no Live2D/Spine/3D

**`apps/desktop/src/renderer/assets/pet/christina/expressions/README.md`** — new
- Per-expression status table
- Crop parameters and generation script reference
- Asset pipeline for contributors

### Verification

- Directory structure confirmed via `find` / `ls` checks.
- No renderer JS changes.
- `python -m pytest`: 555 passed (unchanged).

---

## TASK-085 - Create Christina Neutral Expression PNG

Status: DONE

### Summary

Generated `christina_neutral.png` (512×512 RGBA) from the reference image using
Python Pillow. Created a reproducible crop script. No renderer changes. No other
mood images created.

### Crop Strategy

- Source: `reference/christina_v0_reference.png` (1024×1536 RGBA, 2.1 MB)
- Crop region: left=59, right=983, top=0, bottom=844 (top 55% of height)
  → captures horns, face, and upper-body with natural frame
- Pad to square (924×924) with transparent fill, centred
- Lanczos scale to 512×512

### Changes

**`apps/desktop/scripts/create-christina-neutral-asset.py`** — new
- Reproducible Pillow crop script with constants for all crop parameters
- Writes to `apps/desktop/src/renderer/assets/pet/christina/expressions/christina_neutral.png`

**`apps/desktop/src/renderer/assets/pet/christina/expressions/christina_neutral.png`** — new
- 512×512 RGBA PNG, 337 KB
- Non-transparent bbox: (18, 29, 512, 492) — content fills 96.5%×90.4% of canvas
- Transparent background confirmed (all corners α=0)
- No white fringe, no black background contamination

**`apps/desktop/src/renderer/assets/pet/christina/expressions/README.md`** — updated
- `christina_neutral.png` status: ✅ Done

### Verification

- File size and dimensions confirmed via Pillow.
- Alpha channel integrity confirmed.
- `python -m pytest`: 555 passed (unchanged).
- No renderer code changes.

---

## TASK-086 - Renderer Image Asset Fallback

Status: DONE

### Summary

Added PNG-with-SVG-fallback logic to `setPetExpression()`. Renderer probes each mood's
PNG asset via `new Image()`; if the file loads, the SVG placeholder is replaced with
`<img>`; if absent or fails, the inline SVG remains. All 18 pre-existing smoke tests
pass unchanged. 4 new smoke tests cover the new behaviour.

### Strategy

1. Set inline SVG immediately on every mood change (no visible flash).
2. Probe `assets/pet/christina/expressions/christina_${mood}.png` via `new Image()`.
3. `onload` → replace SVG with `<img style="object-fit:contain">` (stale-mood guard).
4. `onerror` → keep SVG placeholder. UI never breaks.
5. `typeof Image === "undefined"` guard makes probe a no-op in Node.js test sandbox.

### Changes

**`apps/desktop/src/renderer/renderer.js`**
- `setPetExpression()` updated with image probe + SVG fallback (TASK-086 strategy).

**`apps/desktop/src/renderer/styles.css`**
- Added `.pet-face img` rule: `object-fit: contain; width: 100%; height: 100%; display: block`.

**`apps/desktop/scripts/renderer-chat-smoke.js`**
- Added `FakeImageBase` class and per-test `FakeImage` closure over `availableImages: Set`.
- `loadRenderer()` now accepts `options.availableImages` — default empty set keeps all
  existing tests unaffected (all probes fire `onerror`, SVG stays).
- 4 new test functions registered in `main()`:
  1. `testNeutralMoodUsesPngImageWhenAvailable`
  2. `testPngLoadFailureFallsBackToSvg`
  3. `testFocusedMoodFallsBackToSvgWhenNoPng`
  4. `testImageAssetDoesNotBreakSourceOrMoodLabel`

### Safety invariants maintained

- Renderer does NOT call Ollama directly.
- No `localhost:11434`, `127.0.0.1:11434`, or bare `11434` in renderer source.
- No external image URLs. No Live2D / Spine / 3D.
- `/chat` schema unchanged. API key never logged.

### Verification

- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `npm.cmd run test:renderer` (renderer-chat-smoke): PASS — 22 tests (18 existing + 4 new).
- Renderer safety scan for `localhost:11434`, `127.0.0.1:11434`, bare `11434`: PASS.
- `git diff --check`: PASS (LF/CRLF warnings only).
- `python -m pytest`: 555 passed.

---

## TASK-087 - Neutral PNG Electron Visual Verification

Status: DONE

### Summary

Performed offline pixel-level visual verification of `christina_neutral.png` in the
80×80 pet display container. Electron cannot be launched headlessly in the CI sandbox,
so verification used Pillow alpha/bbox analysis and renderer code inspection.

### PNG quality analysis

| Metric | Value | Assessment |
|---|---|---|
| Canvas size | 512×512 RGBA | ✅ |
| Non-transparent bbox | (18, 29, 512, 492) | ✅ tight crop |
| Content fill | 494×463px — 96.5% wide, 90.4% tall | ✅ fills canvas |
| Fully transparent pixels | 128,620 (49.1%) | ✅ clean alpha bg |
| Fully opaque pixels | 113,893 (43.4%) | ✅ |
| Semi-transparent pixels | 19,631 (7.5%) | ✅ natural anti-aliasing |
| Corner pixels (α) | all α=0 | ✅ no black background |
| White fringe at bbox edges | 0% | ✅ no white border |

### 80×80 container assessment

With `object-fit: contain` in the 80×80 `.pet-face` div:
- Rendered character: ~77×72px (96% wide, 90% tall of container)
- Verdict: **ACCEPTABLE** — character fills nearly the entire container
- No clipping of horns or head (top margin 29px in 512px canvas → ~4.5px at 80px)
- No black background bleed (all corners fully transparent)
- No white fringe
- The `object-fit: contain` CSS rule (added in TASK-086) prevents any cropping

### Renderer behaviour confirmed

- On startup: `setMood("neutral")` → `setPetExpression("neutral")` is called.
- `setPetExpression` probes `assets/pet/christina/expressions/christina_neutral.png`.
- Because the file exists, `probe.onload` fires → SVG is replaced with `<img>`.
- Result: **PNG is displayed, not the SVG fallback**.
- For all other moods (no PNG yet): `probe.onerror` fires → SVG placeholder shown.
- No renderer calls Ollama directly. No external image URLs.

### Decision: no changes required

- 80×80 container is adequate for the current neutral expression crop.
- Issue was crop tightness (96% fill), not container size — there is no need to enlarge.
- `object-fit: contain` already handles aspect ratio and prevents clipping.
- No renderer changes, no CSS changes, no re-crop needed.

### Files changed

None — this was a read-only verification task.

### Verification

- Pillow bbox/alpha analysis: PASS (see analysis above).
- `renderer.js` code review: probe path, stale-mood guard, fallback logic all correct.
- No new tests needed (TASK-086 smoke tests already cover PNG success/failure paths).
- `python -m pytest`: 555 passed (unchanged).

### Next step

TASK-087 is the final task in the Phase 4 Extension — Local Ollama Provider Track.
The Local Ollama MVP checkpoint is complete. Suggested next tracks:
- Phase 5 planning (task management, project context, tool execution framework)
- Additional expression PNGs for remaining 9 moods (happy, focused, proud, etc.)
- UI polish pass (container sizing, chat layout, scrollback behaviour)

---

## TASK-088 - Phase 4 Extension Checkpoint / Commit Prep

Status: DONE

### Summary

Full checkpoint verification of TASK-072 ~ TASK-087. All tests pass. Working tree is
clean and commit-ready with two intentional untracked additions (asset script + assets
directory). One advisory item: `reference/christina_v0_reference.png` is 2.1 MB —
see decision below.

### Test results

| Check | Result |
|---|---|
| `python -m pytest` | ✅ 555 passed, 0 failed |
| `node --check apps/desktop/src/main.js` | ✅ PASS |
| `node --check apps/desktop/src/renderer/renderer.js` | ✅ PASS |
| `node --check apps/desktop/scripts/renderer-chat-smoke.js` | ✅ PASS |
| `npm run test:renderer` (renderer-chat-smoke) | ✅ 22 tests PASS |
| Renderer safety scan (`localhost:11434`, `127.0.0.1:11434`, bare `11434`) in `.js/.html/.css` | ✅ PASS |
| `git diff --check` | ⚠️ CRLF warnings only — README.md has Windows line endings; zero actual trailing-space characters. Pre-existing known issue. |

### git status summary

**Modified (9 files — all intentional):**
- `README.md` — Phase 4 Extension status updated, pytest count 531→555, screenshots added
- `apps/desktop/scripts/renderer-chat-smoke.js` — TASK-083/086: 22 smoke tests (was 14)
- `apps/desktop/src/renderer/index.html` — TASK-083: pet-display section added
- `apps/desktop/src/renderer/renderer.js` — TASK-083/086: PET_EXPRESSIONS map, setPetExpression, PNG fallback
- `apps/desktop/src/renderer/styles.css` — TASK-083/086: pet-display and pet-face rules
- `backend/README.md` — Ollama / Local LLM mode documentation
- `docs/OLLAMA_PROVIDER_DESIGN.md` — design doc updated with runtime smoke and UX results
- `docs/ROADMAP.md` — TASK-072 ~ TASK-088 all DONE; Phase 4 Extension COMPLETE
- `docs/TASKS.md` — TASK-072 ~ TASK-088 DONE records appended

**Untracked (2 entries — both should be committed):**
- `apps/desktop/scripts/create-christina-neutral-asset.py` — reproducible Pillow crop script
- `apps/desktop/src/renderer/assets/` — Christina expression assets and READMEs

### File-by-file assessment

| File/Path | Commit? | Notes |
|---|---|---|
| `apps/desktop/scripts/create-christina-neutral-asset.py` | ✅ YES | Reproducible asset pipeline script |
| `assets/pet/christina/README.md` | ✅ YES | Naming spec and rollout strategy |
| `assets/pet/christina/expressions/README.md` | ✅ YES | Expression status table |
| `assets/pet/christina/expressions/christina_neutral.png` | ✅ YES | 512×512 RGBA, 337 KB — app asset |
| `assets/pet/christina/reference/christina_v0_reference.png` | ⚠️ ADVISORY | 2.1 MB reference image — not needed at runtime. Options: (a) commit as-is (preserves provenance), (b) add to `.gitignore` and keep local-only, (c) move to git-lfs. Recommended: add to `.gitignore` to avoid bloating repo history. |

### root package-lock.json

Not visible to git (not in `git status` untracked list). Not present on Linux mount.
If it exists on Windows, delete with `Remove-Item package-lock.json` before committing.

### /chat schema

Confirmed unchanged: `reply / mood / source` (backend/app/schemas/chat.py).

### Safety invariants confirmed

- Renderer `.js/.html/.css` files: no `localhost:11434`, `127.0.0.1:11434`, bare `11434`.
- No external image URLs in renderer code.
- No Live2D / Spine / 3D.
- API key not logged, not in localStorage/sessionStorage, not sent to frontend.

### Suggested commit message

```
feat(phase4-ext): Local Ollama MVP + Christina pet expression UI

TASK-072 ~ TASK-088 complete. Phase 4 Extension checkpoint.

- OllamaLocalProvider behind LLM_PROVIDER=ollama flag (no API key, no external network)
- Ollama option in Provider Settings UI with Test Connection support
- source=llm_local in /chat response (schema unchanged)
- Mood → pet expression mapping: 10 inline SVG expressions wired to /chat mood field
- Christina neutral expression PNG asset pipeline:
    - create-christina-neutral-asset.py (reproducible Pillow crop)
    - christina_neutral.png (512×512 RGBA, 337 KB)

---

## TASK-089 - Create Christina Focused Expression PNG

Status: DONE

Goal:
Create the second formal Christina expression PNG asset at
`apps/desktop/src/renderer/assets/pet/christina/expressions/christina_focused.png`.

Implementation Summary:
- Created `christina_focused.png` as a v0 temporary duplicate placeholder copied from
  `christina_neutral.png`.
- Preserved the same crop style, character scale, 512x512 canvas, RGBA mode, and
  transparent alpha channel as the neutral asset.
- Updated Christina asset README files to clearly mark focused as a temporary
  duplicate placeholder, not a true focused/attentive expression yet.
- Updated root README and ROADMAP to record the focused placeholder checkpoint.
- No renderer behavior was changed.
- `/chat` schema was not changed.
- No external image URL, Live2D, Spine, or 3D asset was added.

Asset Verification:
- `christina_focused.png`: 512x512 PNG.
- Mode: RGBA, 8-bit PNG color type 6.
- Alpha: present, min 0, max 255.
- File size: 345,368 bytes / 337.3 KB.
- Placeholder status: temporary duplicate of `christina_neutral.png`.

Validation:
- `python -m pytest`: 555 passed.
- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `npm.cmd run test:renderer`: PASS.
- Renderer safety scan for direct Ollama URL / `11434`: PASS.
- `git diff --check`: PASS with LF/CRLF warnings only.

Next Task:
TASK-090 - Christina Real Expression Asset Plan

---

## TASK-090 - Christina Real Expression Asset Plan

Status: DONE

Goal:
Document the real Christina expression asset plan and prompt specifications so
future tasks replace placeholder/fallback moods with true mood-specific PNGs.

Current Expression State:

| Mood | PNG state | Runtime behavior |
|---|---|---|
| `neutral` | real v0 asset | PNG displayed |
| `focused` | temporary duplicate placeholder | PNG displayed, visually same as neutral |
| `happy` | missing | SVG fallback |
| `proud` | missing | SVG fallback |
| `annoyed` | missing | SVG fallback |
| `worried` | missing | SVG fallback |
| `sleepy` | missing | SVG fallback |
| `pending` | missing | SVG fallback |
| `error` | missing | SVG fallback |
| `offline` | missing | SVG fallback |

Implementation Summary:
- Updated Christina asset README to keep `focused` clearly marked as a duplicate
  placeholder and to stop creating additional duplicate placeholder PNGs.
- Updated expression status table with current PNG/fallback state.
- Added `apps/desktop/src/renderer/assets/pet/christina/EXPRESSION_GENERATION_GUIDE.md`.
- Added production rules: same character design, 512x512 RGBA PNG, transparent
  background, same crop style as neutral, readable at 80x80, no external URL,
  no Live2D/Spine/3D, and no `/chat` schema change.
- Added prompt drafts for `happy`, `proud`, `annoyed`, `focused`, `worried`,
  `sleepy`, `pending`, `error`, and `offline`.
- No renderer behavior was changed.
- No new duplicate PNG was created.

Recommended Real Asset Order:
1. `happy`
2. `proud`
3. `annoyed`
4. `focused` real replacement
5. `worried`
6. `sleepy`
7. `pending`
8. `error`
9. `offline`

Validation:
- `python -m pytest`: 555 passed.
- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `npm.cmd run test:renderer`: PASS.
- Renderer safety scan for direct Ollama URL / `11434`: PASS.
- `git diff --check`: PASS with LF/CRLF warnings only.

Next Task:
TASK-091 - Integrate Existing Christina Expression PNG Assets

---

## TASK-091 - Integrate Existing Christina Expression PNG Assets

Status: DONE

Goal:
Integrate and validate the existing user-provided Christina expression PNG assets
without regenerating images or changing renderer behavior.

Integrated Assets:

| Mood | File | Size | Mode | Alpha | Runtime behavior |
|---|---:|---|---:|---|---|
| `neutral` | `christina_neutral.png` | 512x512 / 345,368 bytes | RGBA | min 0 / max 255 | PNG displayed |
| `focused` | `christina_focused.png` | 1024x1536 / 2,080,881 bytes | RGBA | min 0 / max 255 | PNG displayed |
| `happy` | `christina_happy.png` | 1030x1527 / 2,212,034 bytes | RGBA | min 0 / max 255 | PNG displayed |
| `proud` | `christina_proud.png` | 1024x1536 / 2,117,924 bytes | RGBA | min 0 / max 255 | PNG displayed |
| `annoyed` | `christina_annoyed.png` | 1029x1528 / 2,658,453 bytes | RGBA | min 0 / max 255 | PNG displayed |
| `worried` | missing | n/a | n/a | n/a | SVG fallback |
| `sleepy` | missing | n/a | n/a | n/a | SVG fallback |
| `pending` | missing | n/a | n/a | n/a | SVG fallback |
| `error` | missing | n/a | n/a | n/a | SVG fallback |
| `offline` | missing | n/a | n/a | n/a | SVG fallback |

Implementation Summary:
- Confirmed all five expected PNG files exist in
  `apps/desktop/src/renderer/assets/pet/christina/expressions/`.
- Confirmed all five files are PNG RGBA assets with transparent alpha.
- Confirmed `focused` is no longer byte-identical to `neutral`; it is now a
  user-provided real focused asset, not the TASK-089 duplicate placeholder.
- Recorded that `focused`, `happy`, `proud`, and `annoyed` are larger than the
  ideal 512x512 face/bust spec, but load through the existing renderer PNG path.
- Updated renderer smoke tests to verify integrated PNG loading for `neutral`,
  `focused`, `happy`, `proud`, and `annoyed`, plus SVG fallback for missing moods.
- No renderer behavior was changed.
- `/chat` schema was not changed.
- No image was regenerated.
- No external image URL, Live2D, Spine, or 3D asset was added.

Validation:
- `python -m pytest`: 555 passed.
- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `npm.cmd run test:renderer`: PASS.
- Renderer safety scan for direct Ollama URL / `11434`: PASS.
- `git diff --check`: PASS with LF/CRLF warnings only.

Next Task:
TASK-092 - Christina Expression Visual QA and 512x512 Normalization Review

---

## TASK-092 - Christina Expression Visual QA and 512x512 Normalization Review

Status: DONE

Goal:
Review the integrated Christina expression PNGs in the actual 80x80 pet display
context and decide whether 512x512 face/bust normalization is needed.

QA Decision:
- Current assets are functional and renderer-compatible.
- `neutral` is the only mood visually consistent with the 80x80 face/bust spec.
- `focused`, `happy`, `proud`, and `annoyed` should be normalized into 512x512
  face/bust crops that match neutral before they are treated as final UI assets.
- Do not overwrite original full-body user-provided PNGs until normalized outputs pass QA.
- Do not resize the pet display as the first fix — framing inconsistency is the root cause.

Constraints Maintained:
- No new expression image was created.
- No runtime renderer behavior was changed.
- `/chat` schema was not changed.
- No external image URL, Live2D, Spine, or 3D asset was added.
- Renderer still has no direct Ollama URL.

Validation:
- `python -m pytest`: 555 passed.
- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `npm.cmd run test:renderer`: PASS.
- Renderer safety scan for direct Ollama URL / `11434`: PASS.
- `git diff --check`: PASS with LF/CRLF warnings only.

Next Task:
TASK-093 - Normalize Existing Christina Expression PNGs to 512x512 Face/Bust

---

## TASK-093 - Normalize Existing Christina Expression PNGs to 512x512 Face/Bust

Status: DONE

Goal:
Create a reproducible normalization script and QA-only 512x512 face/bust
candidates from the existing full-body Christina expression PNGs, without
overwriting runtime assets.

Implementation Summary:
- Added `apps/desktop/scripts/normalize-christina-expression-assets.py`.
- The script reads existing runtime PNGs for `focused`, `happy`, `proud`, and `annoyed`.
- The script writes candidates to
  `apps/desktop/src/renderer/assets/pet/christina/expressions/candidates/`.
- Added `apps/desktop/src/renderer/assets/pet/christina/expression-normalization-preview.html`.
- Added `apps/desktop/src/renderer/assets/pet/christina/expressions/candidates/README.md`.
- Runtime files `christina_focused.png`, `christina_happy.png`,
  `christina_proud.png`, and `christina_annoyed.png` were not overwritten.
- No renderer runtime behavior was changed.
- `/chat` schema was not changed.
- No new mood image was added.
- No external image URL, Live2D, Spine, or 3D asset was added.

Candidate Outputs:

| Mood | Candidate | Size | Mode | Alpha | File size |
|---|---|---:|---|---|---:|
| `focused` | `christina_focused_512_candidate.png` | 512x512 | RGBA | min 0 / max 255 | 406,211 bytes |
| `happy` | `christina_happy_512_candidate.png` | 512x512 | RGBA | min 0 / max 255 | 408,362 bytes |
| `proud` | `christina_proud_512_candidate.png` | 512x512 | RGBA | min 0 / max 255 | 389,606 bytes |
| `annoyed` | `christina_annoyed_512_candidate.png` | 512x512 | RGBA | min 0 / max 255 | 393,336 bytes |

Crop Strategy:

| Mood | Source crop | Strategy note |
|---|---|---|
| `focused` | x50-y0 to x973-y843 | top 55% face/bust crop; preserves horns and reaching hand |
| `happy` | x53-y0 to x976-y843 | top face/bust crop centered to match neutral scale |
| `proud` | x50-y0 to x973-y843 | top face/bust crop; preserves horns and smug face |
| `annoyed` | x52-y0 to x975-y843 | top face/bust crop; preserves horns and annoyed face |

Validation:
- `python -m pytest`: 555 passed.
- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `python -m py_compile apps/desktop/scripts/normalize-christina-expression-assets.py`: PASS.
- `npm.cmd run test:renderer`: PASS.
- Renderer safety scan for direct Ollama URL / `11434`: PASS.
- `git diff --check`: PASS with LF/CRLF warnings only.

Next Task:
TASK-094 - Approve Normalized Christina Candidates and Replace Runtime PNGs

---

## TASK-094 - Approve Normalized Christina Candidates and Replace Runtime PNGs

Status: DONE

### Summary

Promoted four 512x512 normalized face/bust candidate PNGs to runtime, replacing the
previous full-body originals (1024x1536, 2-2.6 MB each). All five active expression
PNGs are now consistently 512x512 RGBA face/bust crops. Full-body originals are
archived in `expressions/originals/`. No renderer code was changed.

### Pre-promotion vs post-promotion runtime PNGs

| Mood | Before | After |
|---|---|---|
| `neutral` | 512x512 RGBA, 337 KB | unchanged |
| `focused` | 1024x1536 RGBA, 2.0 MB | 512x512 RGBA, 396 KB |
| `happy` | 1030x1527 RGBA, 2.2 MB | 512x512 RGBA, 398 KB |
| `proud` | 1024x1536 RGBA, 2.1 MB | 512x512 RGBA, 380 KB |
| `annoyed` | 1029x1528 RGBA, 2.6 MB | 512x512 RGBA, 384 KB |

### Safety invariants maintained

- Renderer code unchanged.
- No external image URLs. No Live2D/Spine/3D. No Ollama URL in renderer.
- `/chat` schema unchanged: `reply / mood / source`.
- API key not logged, not in localStorage, not sent to frontend.

### Verification

- `python -m pytest`: 555 passed, 0 failed
- `node --check apps/desktop/src/main.js`: PASS
- `node --check apps/desktop/src/renderer/renderer.js`: PASS
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS
- `npm run test:renderer` (renderer-chat-smoke): PASS
- Renderer safety scan (js/html/css): PASS
- `git diff --check`: CRLF warnings only (pre-existing)

---

## TASK-095 - Create Christina Worried and Sleepy Expression PNGs

Status: BLOCKED (initial) -> DONE (TASK-095-RESUME)

### Summary

TASK-095 initial run: BLOCKED awaiting source images.
TASK-095-RESUME: User-provided source images for `worried` and `sleepy` were found
in the expressions directory. Applied the same normalization pipeline as TASK-093/094
to produce 512x512 RGBA face/bust crops. All 7 active runtime expression PNGs are now
consistently 512x512 RGBA with transparent backgrounds. No renderer code was changed.

### Source images found

| Mood | File | Original size | File size |
|---|---|---|---|
| `worried` | `christina_worried.png` (pre-normalization) | 1030x1527 RGBA | ~2007 KB |
| `sleepy` | `christina_sleepy.png` (pre-normalization) | 1024x1536 RGBA | ~1894 KB |

### Normalization pipeline

Same method as TASK-093 / TASK-094:
1. Computed content bounding box from alpha channel.
2. Took top 55% of image height as the face/bust crop region.
3. Centered the crop horizontally on the content.
4. Removed edge-connected light/white background artifacts (flood-fill from edges).
5. Padded shorter axis with transparent fill to produce a square crop.
6. Lanczos scaled to 512x512.

Crop boxes used:
- `worried`: (61, 0, 985, 840)
- `sleepy`: (43, 0, 967, 845)

### Post-normalization runtime PNG verification (all 7 PNGs)

| Mood | Size | Mode | Fill at 80x80 | Corners alpha=0 | KB | Verdict |
|---|---|---|---|---|---|---|
| neutral | 512x512 | RGBA | 96%x90% | YES | 337 | PASS |
| focused | 512x512 | RGBA | 98%x90% | YES | 396 | PASS |
| happy | 512x512 | RGBA | 94%x90% | YES | 398 | PASS |
| proud | 512x512 | RGBA | 96%x91% | YES | 380 | PASS |
| annoyed | 512x512 | RGBA | 92%x90% | YES | 384 | PASS |
| worried | 512x512 | RGBA | 96%x90% | YES | 325 | PASS |
| sleepy | 512x512 | RGBA | 86%x90% | YES | 302 | PASS |

### Safety invariants maintained

- Renderer code unchanged.
- No external image URLs. No Live2D/Spine/3D. No Ollama URL in renderer.
- `/chat` schema unchanged: `reply / mood / source`.
- API key not logged, not in localStorage, not sent to frontend.

### Verification

- `python -m pytest`: 555 passed, 0 failed
- `node --check apps/desktop/src/main.js`: PASS
- `node --check apps/desktop/src/renderer/renderer.js`: PASS
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS
- `npm run test:renderer` (22 tests): PASS
- Renderer safety scan (js/html/css): PASS
- `git diff --check`: CRLF warnings only (pre-existing)

---

## TASK-096 - Create Christina System-State Expression PNGs

Status: BLOCKED -- awaiting source images

### Summary

TASK-096 cannot be completed without user-provided source images for the three
remaining system-state moods (`pending`, `error`, `offline`). No fake or
duplicate-placeholder PNGs were created.

### Blocker

Source image audit result:
- No user-provided `pending`, `error`, or `offline` PNG assets found in:
  - `apps/desktop/src/renderer/assets/pet/christina/expressions/`
  - Any uploads directory
- No local image generation tools available in the sandbox.
- Generating AI artwork programmatically without a base model is not possible.

Renderer fallback status (unchanged, correct):
- `pending`: SVG fallback active -- no PNG present.
- `error`: SVG fallback active -- no PNG present.
- `offline`: SVG fallback active -- no PNG present.
- This is safe and functional; SVG expressions are defined for all three moods.

Current expression PNG status after TASK-095-RESUME:

| Mood | PNG state | KB |
|---|---|---|
| `neutral` | 512x512 RGBA | 337 |
| `focused` | 512x512 RGBA | 396 |
| `happy` | 512x512 RGBA | 398 |
| `proud` | 512x512 RGBA | 380 |
| `annoyed` | 512x512 RGBA | 384 |
| `worried` | 512x512 RGBA | 325 |
| `sleepy` | 512x512 RGBA | 302 |
| `pending` | SVG fallback | -- |
| `error` | SVG fallback | -- |
| `offline` | SVG fallback | -- |

### Required to unblock

One of the following:

**Option A** -- User provides source images (same workflow as TASK-095-RESUME).
Provide RGBA PNG files with transparent backgrounds for pending, error, and offline
expressions matching the Christina v0 character design. Drop files in
`apps/desktop/src/renderer/assets/pet/christina/expressions/` or upload in
the next Cowork session, then re-run TASK-096-RESUME.

**Option B** -- Generate via external AI image tool.
Use the prompts below with an AI image generator (DALL-E, Midjourney, Stable
Diffusion, etc.), then provide the output PNGs.

**Option C** -- Defer.
Keep SVG fallback active for all three system-state moods. Revisit when source
material is available. The renderer handles this gracefully with no UI breakage.

### Files changed

None -- no PNG files were created or modified.

### Verification (all pass, no regressions)

- `python -m pytest`: 555 passed, 0 failed
- `node --check apps/desktop/src/main.js`: PASS
- `node --check apps/desktop/src/renderer/renderer.js`: PASS
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS
- `npm run test:renderer` (22 tests): PASS
- Renderer safety scan (js/html/css): PASS
- `git diff --check`: CRLF warnings only (pre-existing)

---

## TASK-097 - Expression Set Checkpoint and Commit Review

Status: DONE

### Summary

Checkpoint review of the Christina expression asset set. The working tree is in a
stable, commit-ready state. 7 of 10 moods have real 512x512 RGBA PNGs; 3 system-state
moods (pending, error, offline) remain on SVG fallback with TASK-096 correctly marked
BLOCKED. One stale file (EXPRESSION_GENERATION_GUIDE.md) was updated to reflect the
current 7-PNG state and remaining work.

### git status audit

**Modified (9 files -- all intentional):**
- `README.md` -- Phase 4 Extension status
- `apps/desktop/scripts/renderer-chat-smoke.js` -- 22 smoke tests
- `apps/desktop/src/renderer/index.html` -- pet-display section
- `apps/desktop/src/renderer/renderer.js` -- PET_EXPRESSIONS, setPetExpression, PNG fallback
- `apps/desktop/src/renderer/styles.css` -- pet-display and pet-face rules
- `backend/README.md` -- Ollama / Local LLM mode documentation
- `docs/OLLAMA_PROVIDER_DESIGN.md` -- design doc
- `docs/ROADMAP.md` -- TASK-083 through TASK-097 status
- `docs/TASKS.md` -- TASK-083 through TASK-097 DONE/BLOCKED records

**Untracked (3 entries -- all intentional):**
- `apps/desktop/scripts/create-christina-neutral-asset.py` -- neutral asset pipeline
- `apps/desktop/scripts/normalize-christina-expression-assets.py` -- normalization pipeline
- `apps/desktop/src/renderer/assets/` -- all Christina expression assets and READMEs

### SVG fallback audit (pending / error / offline)

| Mood | SVG key | Smoke test |
|---|---|---|
| `pending` | YES | `testPendingExpressionSetBeforeResponse` PASS |
| `error` | YES | `testLocalErrorSetsErrorExpression` PASS |
| `offline` | YES | `testBackendOfflineSetsOfflineExpression` PASS |

### File updated in this task

**`EXPRESSION_GENERATION_GUIDE.md`** -- updated
- Current Expression State table: worried/sleepy updated to integrated (512x512)
- Recommended Production Order: removed worried/sleepy; remaining list is pending/error/offline only
- Added TASK-096-RESUME instructions

### Safety invariants maintained

- Renderer code unchanged.
- No external image URLs. No Live2D/Spine/3D. No Ollama URL in renderer.
- `/chat` schema unchanged: `reply / mood / source`.
- API key not logged, not in localStorage, not sent to frontend.

### Verification

- `python -m pytest`: 555 passed, 0 failed
- `node --check apps/desktop/src/main.js`: PASS
- `node --check apps/desktop/src/renderer/renderer.js`: PASS
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS
- `npm run test:renderer` (22 tests): PASS
- Renderer safety scan (js/html/css): PASS
- `git diff --check`: CRLF/BOM warnings only in `backend/README.md` (pre-existing)

---

## TASK-098 - UI Polish Pass

Status: DONE

### Summary

UI polish pass on the Electron desktop app. Made the chat scrollback reliable,
enlarged the pet display from 80px to 112px, replaced raw source labels with
friendly user-facing text, improved provider settings readability with boolean
badges, and added 2 new smoke tests (24 total). No new expression PNGs were
added. No `/chat` schema was changed. No Ollama URL was introduced.

### Files changed

**`apps/desktop/src/renderer/styles.css`** -- MODIFIED
- Pet face size: 80px -> 112px; display padding 10px -> 14px; gap 4px -> 6px
- Pet display hint: font-size 11px -> 12px; added `min-height: 18px`
- Chat area: `min-height: 200px` -> `240px`; `max-height: 38vh` -> `44vh`; gap 12px -> 10px
- `.status-note`: font-size 13px -> 12px; color `var(--text-muted)`; overflow ellipsis
- `.chat-runtime-pill`: muted color, font-size 12px, padding 2px 7px
- Added `.chat-runtime-pill.friendly`: stronger color, font-size 13px, font-weight 500
- `.provider-status-grid strong`: font-size 15px -> 14px
- Added `strong[data-bool="true"]` green badge; `strong[data-bool="false"]` muted badge
- Media query max-height threshold: 320px -> 360px

**`apps/desktop/src/renderer/renderer.js`** -- MODIFIED
- Added `sourceLabel(source)` function: maps source strings to friendly labels
  (e.g. `llm_local` -> "Local Ollama", `mock` -> "Mock fallback", `backend_offline` -> "Backend offline")
- Added `moodHintLabel(mood)` function: maps mood strings to user-facing hint text
  (e.g. `pending` -> "Thinking...", `error` -> "Something went wrong", `offline` -> "Offline")
- Updated `setChatRuntimeStatus()`: `chatSourceStatus` unchanged (smoke-test-safe),
  `chatProviderStatus` now shows `sourceLabel(lastChatSource)` with `.friendly` CSS class
- Updated `syncChatRuntimeProviderStatus()`: before first chat shows `provider: ${p}`,
  after shows `sourceLabel(lastChatSource)`
- Updated `appendMessage()`: renamed sender "Dragon Pet" -> "Christina"; added
  `requestAnimationFrame` guard for scroll-to-bottom (safe in Node.js test sandbox)
- Updated `setMood()`: uses `moodHintLabel(mood)` instead of raw mood string for pet hint
- Updated `renderProviderSettings()`: added `dataset.bool` attributes on boolean fields
  for CSS badge styling (`"true"` -> green, `"false"` -> muted gray)
- Error paths: `setPetHint(moodHintLabel("offline"))`, `setPetHint(moodHintLabel("error"))`

**`apps/desktop/scripts/renderer-chat-smoke.js`** -- MODIFIED
- Added `this.dataset = {}` to `FakeElement` constructor (required for `dataset.bool` in renderer)
- Added `testChatAreaAccumulatesMultipleMessages()`: sends 3 messages in mock mode,
  verifies 3 user messages + >=3 pet replies accumulate in DOM using `children.filter()`
- Added `testFriendlySourceLabelShownAfterLocalChat()`: verifies `chat-source-status`
  = "source: llm_local" (unchanged) AND `chat-provider-status` = "Local Ollama" (new)
- Total tests: 22 -> 24

### Note: file truncation repairs

Both `renderer.js` and `renderer-chat-smoke.js` were found truncated at the start of
this session (NTFS stale cache / partial write from prior context window). Both were
repaired using bash Python direct writes before running verification checks.

### Pet display size

Adjusted from 80px to 112px. The 7 existing 512x512 RGBA PNGs display clearly at
this size with `object-fit: contain`. No cropping of horns or face occurs.

### Chat scrollback

Auto-scroll to bottom implemented with `requestAnimationFrame` guard. Messages use
`.message.user` / `.message.pet` / `.message.status` / `.message.error` className
structure. Loading and error messages do not break layout.

### Runtime status strategy

- `chat-source-status` pill: unchanged format `source: <value>` -- smoke tests depend on this
- `chat-runtime-status`: unchanged regex-compatible format -- smoke tests depend on this
- `chat-provider-status` pill (not tested by prior smoke tests): repurposed as user-facing
  friendly label ("Local Ollama", "Mock fallback", "Backend offline", etc.) with `.friendly` CSS class

### Provider settings readability

Boolean fields (`real_provider_enabled`, `llm_chat_enabled`, `fallback_to_mock`) now
render with `data-bool="true"` / `data-bool="false"` attributes and corresponding CSS
badges (green for true, muted gray for false). Numeric usage counts rendered as `<dt>`/`<dd>` pairs.

### Safety invariants maintained

- Renderer still has no `localhost:11434`, `127.0.0.1:11434`, or bare `11434`.
- `/chat` schema unchanged: `reply / mood / source`.
- No external image URLs. No Live2D/Spine/3D. No new expression PNGs.
- No persona prompt changes. No backend provider logic changes.
- API key not logged, not in localStorage, not sent to frontend.

### Verification

- `python -m pytest`: 555 passed, 0 failed
- `node --check apps/desktop/src/main.js`: PASS
- `node --check apps/desktop/src/renderer/renderer.js`: PASS (after truncation repair)
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS (after truncation repair)
- `npm run test:renderer` (24 tests): PASS
- Renderer safety scan (js/html/css): PASS -- no Ollama URL
- `git diff --check`: CRLF/BOM warnings only in `backend/README.md` (pre-existing, non-blocking)

---

## TASK-099 — Desktop Settings Persistence Review

**Status:** DONE
**Date:** 2026-05-22

### Goal

Audit where non-secret provider settings are stored on the desktop and implement minimal
backend-side JSON persistence so that provider / model / feature-flag choices survive
app restarts.  API keys must never be written to the plain JSON file.

### Audit outcome

`ProviderSettingsService` was purely in-memory (dataclass + asyncio Lock).  On restart
all state reverted to environment-variable defaults.  No Electron `userData` persistence
existed.  `runtime_overridden` flag was always `False` after a fresh process.

### Implementation

#### `backend/app/core/config.py`
Added `get_settings_file_path()`:
- Default path: `data/provider_settings.json` (relative to backend working directory).
- Override with `SETTINGS_FILE_PATH` env var; empty string disables persistence entirely.
- Safety: only non-secret fields ever reach this file.

#### `backend/app/services/provider_settings_service.py` (full rewrite, 377 lines)
- Added `_PERSIST_FIELDS = frozenset({"provider","model","real_provider_enabled","llm_chat_enabled","fallback_to_mock"})` whitelist.
- `_load_settings_from_file(path)`: reads JSON, validates it is a dict, filters to `_PERSIST_FIELDS`, returns `None` on any error (missing file, corrupt JSON, wrong type).
- `_save_settings_to_file(path, settings)`: serialises only `_PERSIST_FIELDS`; atomic write via `.tmp` + `os.replace()`; creates parent directory with `os.makedirs(exist_ok=True)`; `f.flush(); os.fsync()` before rename.
- `ProviderSettingsService.__init__` accepts `settings_file_path: str | None = None` (defaults to env-var path); calls `_try_load_from_file()` on construction.
- `_try_load_from_file()`: seeds `_settings` from file and sets `_runtime_overridden = True` so `chat_service` routes through in-memory settings.
- `update_settings()`: saves to file after in-memory update (outside lock).
- `reset()`: clears memory only — does NOT delete the file.
- Module-level `_service = ProviderSettingsService()` uses env-var path by default.

#### `backend/data/.gitkeep`
Placeholder so the `data/` directory is tracked in git.

#### `.gitignore`
Appended two lines to exclude the settings file and its `.tmp` sibling.

#### `backend/tests/test_provider_settings_persistence.py` (282 lines, new)
20 tests across three suites:
- `TestLoadSettingsFromFile` (5): happy path, filters unknown keys, missing file, corrupt JSON, wrong JSON type.
- `TestSaveSettingsToFile` (5): round-trip, never writes secret fields, creates parent directory, empty path is no-op, `None` model serialises correctly.
- `TestProviderSettingsServicePersistence` (10): save→reload restores settings, loaded settings mark `runtime_overridden=True`, corrupt file falls back to defaults, API key never written to file, reset clears memory but keeps file, disabled persistence with empty path, `update_settings` persists on every call, `reset` does not remove file, defaults load when file absent, `llm_chat_enabled` persists correctly.

### Safety invariants maintained

- API key (`LLM_API_KEY`) is **never** written to the JSON file; `_PERSIST_FIELDS` whitelist excludes it.
- `key_status` and all other secret-adjacent fields are also excluded.
- `SETTINGS_FILE_PATH=""` disables persistence entirely (used in test isolation).
- Renderer still has no `localhost:11434`, `127.0.0.1:11434`, or bare `11434`.
- `/chat` schema unchanged.
- No external image URLs, no persona prompt changes, no backend provider logic changes.

### Verification

- `python -m pytest`: **576 passed, 0 failed** (21 new persistence tests)
- `node --check apps/desktop/src/main.js`: PASS
- `node --check apps/desktop/src/renderer/renderer.js`: PASS
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS
- `npm run test:renderer` (24 tests): PASS
- Renderer safety scan: PASS — no Ollama URL
- `git diff --check`: CRLF/BOM warnings only in `backend/README.md` (pre-existing, non-blocking)

---

## TASK-099 — Desktop Settings Persistence Review

**Status:** DONE
**Date:** 2026-05-22

### Goal

Audit where non-secret provider settings are stored on the desktop and implement minimal
backend-side JSON persistence so that provider / model / feature-flag choices survive
app restarts.  API keys must never be written to the plain JSON file.

### Audit outcome

`ProviderSettingsService` was purely in-memory (dataclass + asyncio Lock).  On restart
all state reverted to environment-variable defaults.  No Electron `userData` persistence
existed.  `runtime_overridden` flag was always `False` after a fresh process.

### Implementation

#### `backend/app/core/config.py`
Added `get_settings_file_path()`:
- Default path: `data/provider_settings.json` (relative to backend working directory).
- Override with `SETTINGS_FILE_PATH` env var; empty string disables persistence entirely.
- Safety: only non-secret fields ever reach this file.

#### `backend/app/services/provider_settings_service.py` (full rewrite, 377 lines)
- Added `_PERSIST_FIELDS` whitelist: `provider`, `model`, `real_provider_enabled`, `llm_chat_enabled`, `fallback_to_mock`.
- `_load_settings_from_file(path)`: reads JSON, validates it is a dict, filters to `_PERSIST_FIELDS`, returns None on any error.
- `_save_settings_to_file(path, settings)`: serialises only `_PERSIST_FIELDS`; atomic write via `.tmp` + `os.replace()`; creates parent directory; `f.flush(); os.fsync()` before rename.
- `ProviderSettingsService.__init__` accepts `settings_file_path: str | None = None`; calls `_try_load_from_file()` on construction.
- `_try_load_from_file()`: seeds `_settings` from file and sets `_runtime_overridden = True`.
- `update_settings()`: saves to file after in-memory update.
- `reset()`: clears memory only; does NOT delete the file.

#### `backend/data/.gitkeep`
Placeholder so the `data/` directory is tracked in git.

#### `.gitignore`
Appended exclusions for `backend/data/provider_settings.json` and `.tmp` sibling.

#### `backend/tests/test_provider_settings_persistence.py` (282 lines, new)
20 tests across three suites:
- `TestLoadSettingsFromFile` (5): happy path, filters unknown keys, missing file, corrupt JSON, wrong JSON type.
- `TestSaveSettingsToFile` (5): round-trip, never writes secret fields, creates parent directory, empty path is no-op, None model serialises correctly.
- `TestProviderSettingsServicePersistence` (10): save/reload, runtime_overridden after load, corrupt file fallback, API key exclusion, reset keeps file, disabled persistence, persistence on every update, defaults when file absent, llm_chat_enabled persists.

### Safety invariants maintained

- API key (`LLM_API_KEY`) is never written to the JSON file; `_PERSIST_FIELDS` whitelist excludes it.
- `key_status` and all secret-adjacent fields are also excluded.
- `SETTINGS_FILE_PATH=""` disables persistence entirely (used in test isolation).
- Renderer still has no `localhost:11434`, `127.0.0.1:11434`, or bare `11434`.
- `/chat` schema unchanged.
- No external image URLs, no persona prompt changes, no backend provider logic changes.

### Verification

- `python -m pytest`: **576 passed, 0 failed** (21 new persistence tests)
- `node --check apps/desktop/src/main.js`: PASS
- `node --check apps/desktop/src/renderer/renderer.js`: PASS
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS
- `npm run test:renderer` (24 smoke tests): PASS
- Renderer safety scan: PASS (no Ollama URL)
- `git diff --check`: CRLF/BOM warnings only in `backend/README.md` (pre-existing, non-blocking)

---

## TASK-100 — Settings Persistence Runtime Smoke

**Status:** DONE
**Date:** 2026-05-22

### Goal

Runtime smoke test confirming that TASK-099 persistence actually works end-to-end:
provider settings survive a backend restart and `/chat` routing uses the restored settings.

### Smoke procedure

| Step | Action | Result |
|------|--------|--------|
| 1 | Start backend (env=mock/disabled, no settings file yet) | `GET /provider/settings` → provider=mock, llm_chat_enabled=False ✓ |
| 2 | `PATCH /provider/settings` (provider=ollama, model=qwen3:8b, enabled=true, fallback=true) | Returns updated settings ✓ |
| 3 | Inspect `provider_settings.json` | Written with exactly 5 non-secret fields ✓ |
| 4 | Secret-field audit | No `api_key`, `key_status`, `resolved_provider`, `usage_summary`, `last_test_status` ✓ |
| 5 | Stop backend | Process terminated |
| 6 | Restart backend (env=mock/disabled — file should override) | Started cleanly ✓ |
| 7 | `GET /provider/settings` after restart | provider=ollama, model=qwen3:8b, llm_chat_enabled=True, resolved_provider=ollama ✓ |
| 8 | `POST /chat` | source=mock (Ollama not installed in sandbox → fallback fired); fallback_count=1 confirms Ollama was attempted ✓ |
| 9 | `git check-ignore` | `backend/data/provider_settings.json` matched by .gitignore line 34 ✓ |

### JSON file content (step 3)

```json
{
  "provider": "ollama",
  "model": "qwen3:8b",
  "real_provider_enabled": true,
  "llm_chat_enabled": true,
  "fallback_to_mock": true
}
```

Exactly `_PERSIST_FIELDS`. No secrets.

### Note on `source=llm_local`

The task spec asked for `source=llm_local`.  Ollama is not installed in the CI/sandbox
environment, so the LLM call raised a connection error.  `fallback_to_mock=true` was
set, so the response fell back to mock with `source=mock`.  The `fallback_count=1`
entry in `usage_summary` is definitive proof that the Ollama code path was entered
(not skipped in favour of the plain mock path).  On a host with `ollama serve` running
and `qwen3:8b` pulled, the same flow produces `source=llm_local`.

### Verification

- `python -m pytest`: **576 passed, 0 failed**
- `node --check apps/desktop/src/main.js`: PASS
- `node --check apps/desktop/src/renderer/renderer.js`: PASS
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS
- `npm run test:renderer` (24 smoke tests): PASS
- Renderer safety scan: PASS (no Ollama URL)
- `git diff --check`: CRLF/BOM warnings only in `backend/README.md` (pre-existing, non-blocking)
- `git check-ignore backend/data/provider_settings.json`: matched (not tracked) ✓

## TASK-101-RERUN — Post-TASK-102 Runtime Smoke

**Status:** DONE
**Date:** 2026-05-23

### Goal

Re-run full runtime smoke after TASK-102 fixes to confirm every behavioral guard is in effect:
partial PATCH preservation, explicit null model guard, Test Connection no-mutate, Electron
no-PATCH, cold-start /chat UX, persistence after restart, and secret/git safety.

### Verification results

| Check | Result |
|-------|--------|
| `python -m pytest` | **586 passed, 0 failed** |
| `node --check apps/desktop/src/main.js` | PASS |
| `node --check apps/desktop/src/renderer/renderer.js` | PASS |
| `node --check apps/desktop/scripts/renderer-chat-smoke.js` | PASS |
| `npm run test:renderer` | PASS |
| Renderer safety scan (no direct Ollama URL) | PASS |
| `git diff --check` (source files only) | PASS |
| `git diff --check` (all) | Pre-existing CRLF in `backend/README.md` only — non-blocking |

### Smoke results

| Step | Action | Result |
|------|--------|--------|
| 1 | `GET /health` | `{"status":"ok","service":"dragon-pet-ai"}` ✓ |
| 2 | `PATCH /provider/settings` (full) | provider=ollama, model=qwen3:8b, fallback_to_mock=False ✓ |
| 3 | Inspect JSON file | `{"provider":"ollama","model":"qwen3:8b","real_provider_enabled":true,"llm_chat_enabled":true,"fallback_to_mock":false}` — no secrets ✓ |
| 4 | Partial PATCH (`provider=ollama` only) | model=qwen3:8b preserved, fallback_to_mock=False preserved ✓ |
| 5 | Explicit null model PATCH (`model:null`) | model=qwen3:8b unchanged ✓ |
| 6 | Test Connection then check JSON file | JSON byte-identical before/after — no mutation ✓ |
| 7 | `POST /chat` (Ollama not in sandbox) | source=llm_local_error, fallback_count=0 (fallback disabled) ✓ |
| 8 | Usage summary | error_counts={'ollama_unavailable':2} — Ollama path entered, no silent skip ✓ |
| 9 | Stop → restart → `GET /provider/settings` | provider=ollama, model=qwen3:8b, real_provider_enabled=True, llm_chat_enabled=True, fallback_to_mock=False ✓ |

### Guards confirmed

- **Partial PATCH**: omitted fields not overwritten.
- **Explicit null model**: `model:null` PATCH does not clear existing model.
- **Test Connection no-mutate**: settings JSON byte-identical before and after.
- **Electron no-PATCH**: verified via renderer smoke test `testProviderSettingsStatusAndTestConnectionSuccess` (static check — Electron not running in sandbox).
- **Cold-start /chat**: `source=llm_local_error`, schema `reply/mood/source` unchanged, fallback=0 when disabled.
- **Warm /chat**: not verifiable in sandbox (Ollama not installed); expected `source=llm_local` on host with `ollama serve`.
- **Persistence**: all five persisted fields restored after backend restart.
- **Git safety**: `backend/data/provider_settings.json` gitignored; no API key in any tracked file.

### Commit recommendation

Commit scope: TASK-099 + TASK-100 + TASK-102 + TASK-101-RERUN verification.
Tag candidate: `v0.5.2-settings-persist`.

---

## TASK-102 - Provider Settings Partial Persist Guard + Ollama Cold Start UX

**Status:** DONE
**Date:** 2026-05-22

### Goal

Prevent partial provider-settings writes from overwriting persisted complete settings, and
improve local Ollama cold-start timeout/error UX without changing `/chat` schema or renderer
provider boundaries.

### Root cause reviewed

The persistence layer already skipped `None` values, but the PATCH route converted omitted
request fields into explicit `None` values before constructing the service update object.
The renderer also allowed Save Non-secret Settings before provider settings had loaded,
which could submit default checkbox/input values instead of the restored checkpoint state.
Full-suite pytest also used the module-level provider settings service without disabling the
runtime settings path, so tests could mutate the developer's ignored
`backend/data/provider_settings.json`.

`/provider/settings/test` does not persist provider settings. This is now covered by
backend and renderer smoke tests.

### Implementation

- Provider settings PATCH now preserves omitted fields with `exclude_unset=True`.
- Empty model text in the renderer Save flow is omitted from the PATCH body instead of being
  sent as `null`.
- Save Non-secret Settings is disabled until the current provider settings load successfully.
- Test Connection remains a read-only provider check and does not write settings JSON.
- Added `LLM_LOCAL_CHAT_TIMEOUT_SECONDS` for local `/chat` generation timeout.
- Local chat timeout default is 90 seconds, clamped to 1..300.
- Legacy `OLLAMA_TIMEOUT_SECONDS` still works as a compatibility fallback.
- Local timeout safe reply now explains that the model may still be loading or waking up.
- Renderer local error status now includes the same cold-start hint.
- Added test-suite isolation so pytest disables the runtime settings file by default; persistence
  tests still use explicit temp files.

### Safety invariants maintained

- `/chat` schema unchanged: `reply / mood / source`.
- Renderer still has no direct Ollama URL.
- API keys are not persisted to `provider_settings.json`.
- Settings JSON remains whitelisted to non-secret fields only:
  `provider`, `model`, `real_provider_enabled`, `llm_chat_enabled`, `fallback_to_mock`.
- Test Connection still uses the lightweight backend local check; it does not perform full
  `/chat` generation.
- No persona prompt changes, no new image assets, no external provider call.

### Verification

- Targeted backend tests: 136 passed.
- `python -m pytest`: 586 passed.
- `node --check apps/desktop/src/main.js`: PASS.
- `node --check apps/desktop/src/renderer/renderer.js`: PASS.
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS.
- `npm.cmd run test:renderer`: PASS.
- Renderer safety scan: PASS, no direct Ollama URL.
- `git diff --check`: PASS with CRLF normalization warnings only.

### Next Task

TASK-103 - Local Dev Launch / One-command Startup

---

## TASK-103 — Local Dev Launch / One-command Startup

**Status:** DONE
**Date:** 2026-05-23

### Goal

Improve the local development startup flow so developers can reliably start the full
Ollama + backend + Electron stack with a single command per service, and diagnose
common environment problems without reading source code.

### Changes

No product features added. No `/chat` schema changed. No provider routing changed.
No persona prompt changed. No images added. No renderer Ollama URL added.

**New files:**

| File | Purpose |
|------|---------|
| `scripts/dev-start-backend.ps1` | Port check, venv activation, env vars, uvicorn start |
| `scripts/dev-start-desktop.ps1` | node_modules check, ELECTRON_RUN_AS_NODE clear, npm.cmd run dev |
| `scripts/dev-smoke.ps1` | /health, /provider/settings, /provider/settings/test, /chat smoke; reports source |
| `docs/LOCAL_DEV_RUNBOOK.md` | Full runbook: prerequisites, startup order, env var reference, troubleshooting |

**Updated files:**

| File | Change |
|------|--------|
| `README.md` | Added Quick Start section with one-liner scripts; updated pytest count to 586 |
| `backend/README.md` | Added one-command script call; added Ollama-mode manual env var block |

### Script features

**`dev-start-backend.ps1`:**
- Resolves repo root from script location (works from any working directory).
- Checks port 8000 with a 200 ms TCP probe; exits with `netstat`/`taskkill` guidance.
- Activates `backend\.venv\Scripts\Activate.ps1` if present; warns if absent.
- Falls back to `python -m uvicorn` if `uvicorn` is not on PATH.
- Sets: `LLM_PROVIDER_NAME=ollama`, `LLM_MODEL=qwen3:8b`, `LLM_PROVIDER_ENABLED=true`, `LLM_CHAT_ENABLED=true`, `LLM_LOCAL_CHAT_TIMEOUT_SECONDS=90`, `PYTHONIOENCODING=utf-8`.

**`dev-start-desktop.ps1`:**
- Checks `apps\desktop\node_modules` and prompts `npm.cmd install` if missing.
- Clears `ELECTRON_RUN_AS_NODE` via both env var assignment and `Remove-Item Env:\`.
- Uses `npm.cmd` (not `npm`) to avoid PowerShell execution-policy errors from `npm.ps1`.

**`dev-smoke.ps1`:**
- Fails fast on `/health` unreachable with a clear restart message.
- Reports provider, model, key_status, resolved_provider from `/provider/settings`.
- Sends `POST /provider/settings/test` with `explicit_cost_ack=true` (no API key).
- Sends `POST /chat`, verifies `reply/mood/source` schema, classifies source with actionable hints.
- Exit code 0 on all pass, 1 on any failure.

### Issues addressed

| Issue | Fix |
|-------|-----|
| `uvicorn not on PATH` | Falls back to `python -m uvicorn`; startup script detects and uses it |
| `npm.ps1 execution policy` | All desktop calls use `npm.cmd` explicitly |
| `ELECTRON_RUN_AS_NODE` | Cleared in `dev-start-desktop.ps1` before `npm.cmd run dev` |
| Port 8000 occupied | 200 ms TCP probe; error message with `netstat`/`taskkill` commands |
| Cold-start timeout | `LLM_LOCAL_CHAT_TIMEOUT_SECONDS=90`; smoke reports `llm_local_error` with retry hint |
| Settings not persisting | Runbook section explains JSON file, gitignore, and `git check-ignore` verification |

### Verification

- `python -m pytest`: **586 passed, 0 failed**
- `node --check apps/desktop/src/main.js`: PASS
- `node --check apps/desktop/src/renderer/renderer.js`: PASS
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS
- `npm run test:renderer`: PASS
- Renderer safety scan: PASS (no direct Ollama URL in renderer.js or any new script)
- Script safety scan: PASS (no API key values, no direct Ollama URL in scripts)
- `git diff --check`: git index corrupt (pre-existing NTFS sandbox lock from v0.5.2 commit); source files verified clean via grep

### Next Task

TASK-104 - Manual Windows Script Smoke

---

## TASK-104 — Manual Windows Script Smoke

**Status:** DONE
**Date:** 2026-05-23

### Goal

Manually verify the three TASK-103 PowerShell startup scripts on a real Windows host
with Ollama running, confirming that port checks, venv activation, npm.cmd routing,
ELECTRON_RUN_AS_NODE clearing, and the full `/chat` round-trip all work end-to-end.

### Results

| Check | Result |
|-------|--------|
| `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` required | ✓ — PowerShell default blocks `.ps1`; Process-scope bypass is the recommended workaround and does not persist after the terminal closes |
| `dev-smoke.ps1` — `GET /health` | PASS |
| `dev-smoke.ps1` — `GET /provider/settings` | PASS |
| `dev-smoke.ps1` — `POST /provider/settings/test` | PASS |
| `dev-smoke.ps1` — `POST /chat` | PASS |
| `source` | `llm_local` — Ollama (`qwen3:8b`) generated the reply locally |
| `mood` | `happy` |
| `/chat` schema | `reply / mood / source` — unchanged |

### Cold-start note

The first `/chat` call timed out because `qwen3:8b` had not been loaded into memory yet.
After warming the model with `ollama run qwen3:8b` (or by waiting for Ollama to finish
loading), all subsequent smoke calls returned `source=llm_local` immediately.

**Recommended warm-up step** (add to personal runbook before first smoke run):

```powershell
# Warm up the model before running the smoke script
ollama run qwen3:8b
# Type a short message, wait for a reply, then Ctrl+D to exit
```

The `dev-start-backend.ps1` already sets `LLM_LOCAL_CHAT_TIMEOUT_SECONDS=90`; on a
warm model this is more than sufficient.  On first cold-start after a pull, running
`ollama run` manually first avoids the timeout.

### ExecutionPolicy guidance (added to runbook)

```powershell
# Allow .ps1 scripts for this terminal session only (does not persist)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

This is already documented in `docs/LOCAL_DEV_RUNBOOK.md` under Common Errors.
No script logic was changed.

### Verification

- All four smoke checks: PASS
- `source=llm_local`: confirmed (real local Ollama generation, not mock)
- `/chat` schema: `reply / mood / source` — unchanged
- No product logic modified

### Next Task

TASK-105 - Cold-start Warmup UX for dev-smoke

---

## TASK-105 — Cold-start Warmup UX for dev-smoke

**Status:** DONE
**Date:** 2026-05-23

### Goal

Improve `scripts/dev-smoke.ps1` so that when the local `qwen3:8b` model is still
loading (cold-start), the script prints a clear, actionable warm-up hint instead of a
generic failure message. No backend provider logic changed. No `/chat` schema changed.
No renderer modified.

### Root cause

`Invoke-BackendPost` previously used `TimeoutSec 15` for `/chat`. The backend's own
`LLM_LOCAL_CHAT_TIMEOUT_SECONDS` defaults to 90 s. On cold-start, the PowerShell
client timed out first (after 15 s) and raised a network exception, which was caught and
printed as a generic `[FAIL] /chat failed: ...` with no guidance. The
`source=llm_local_error` branch (which did have a partial hint) was never reached.

### Changes

**`scripts/dev-smoke.ps1`** only — no other file modified.

| Change | Details |
|--------|---------|
| New `-ChatTimeoutSec` param | Default 100 s — intentionally above backend 90 s so backend can return JSON |
| New `Write-WarmupHint` function | Prints the exact `ollama run qwen3:8b` warm-up command and rerun instruction |
| New `Is-TimeoutError` helper | Detects PowerShell network-timeout exception messages |
| `/chat` network-timeout branch | Detects timeout, calls `Write-WarmupHint`, increments fail counter |
| `llm_local_error` branch improved | Checks reply text for cold-start keywords; if matched calls `Write-WarmupHint`; if not matched shows possible-causes list then `Write-WarmupHint` |
| `$WARN` tag added | `[WARN]` in Yellow — distinguishes transient cold-start from hard failures |
| Header shows timeout | `Chat timeout: N s` visible in smoke header |
| Cold-start note in header | `(cold-start may take up to 90 s on first load — please wait)` |

### Warm-up hint displayed on cold-start

```
[WARN] /chat request timed out at the network level (100 s).
[WARN] The backend may still be waiting for Ollama to load the model.

  *** Local model may still be loading / waking up ***

  Warm up the model by running this in a separate terminal:

    ollama run qwen3:8b "請用一句繁體中文回覆：ready"

  Wait until it replies, then rerun:

    .\scripts\dev-smoke.ps1

  This is a cold-start loading issue — not a settings or backend problem.
```

### Safety invariants

- `/chat` schema unchanged: `reply / mood / source`.
- Renderer not modified.
- No direct Ollama URL in any script.
- Backend provider logic not modified.
- `llm_local_error` is not counted as a hard failure (exit 0) — it is a transient
  cold-start state, not a broken backend or settings problem.

### Verification

- `python -m pytest`: **586 passed, 0 failed**
- `node --check apps/desktop/src/main.js`: PASS
- `node --check apps/desktop/src/renderer/renderer.js`: PASS
- `node --check apps/desktop/scripts/renderer-chat-smoke.js`: PASS
- `npm run test:renderer`: PASS
- Renderer safety scan: PASS (no direct Ollama URL)
- `dev-smoke.ps1` safety scan: PASS (no direct Ollama URL, no API key)
- Trailing whitespace check on `dev-smoke.ps1`: CLEAN

### Next Task

TASK-106 - Manual Cold-start Warmup UX Smoke

---

## TASK-106 — Manual Cold-start Warmup UX Smoke

**Status:** DONE
**Date:** 2026-05-23

### Goal

在 Windows 本機手動驗證 TASK-105 的 cold-start warm-up UX：
確認 `dev-smoke.ps1` 在 `qwen3:8b` 尚未載入時正確顯示暖機提示，
暖機完成後 smoke 全 PASS 且 `source=llm_local`。

不新增功能，不修改程式邏輯。

### 手動驗證結果（Windows 本機）

**前置條件：** 需先執行 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` 解除 PowerShell 執行限制。

| 檢查項目 | 實際結果 |
|---------|---------|
| `/health` | ✅ `[PASS]` |
| `/provider/settings` | ✅ `[PASS]` — provider=ollama、model=qwen3:8b、real_provider_enabled=true、llm_chat_enabled=true、fallback_to_mock=false、resolved_provider=ollama |
| `/provider/settings/test` | ✅ `[PASS]` — source=llm_local |
| `/chat` | ✅ `[PASS]` — HTTP 200 |
| `/chat` source | ✅ `source=llm_local` |
| `/chat` mood | ✅ `mood=happy` |
| Schema guard | ✅ `[PASS]` — `reply / mood / source` |
| Smoke result | ✅ `ALL CHECKS PASSED` |

### Safety invariants

- `/chat` schema 不變：`reply / mood / source`
- Renderer 不修改
- Backend provider logic 不修改
- 不新增圖片
- 不呼叫外部 API

### 結論

TASK-106 DONE。cold-start warmup UX 與 `dev-smoke.ps1` 腳本在 Windows 本機手動驗證通過。
`source=llm_local` 確認，schema 正確，`ALL CHECKS PASSED`。

### Next Task

TASK-107 - Phase 5 Planning — Companion Behavior Loop

---

## TASK-107 — Phase 5 Planning: Companion Behavior Loop

**Status:** DONE
**Date:** 2026-05-23

### Goal

規劃 Phase 5「Companion Behavior Loop」，讓克莉絲蒂娜更像桌面寵物而非單純聊天框。
產出設計文件 `docs/PHASE5_COMPANION_BEHAVIOR_PLAN.md`，更新 TASKS.md 與 ROADMAP.md。
不修改任何程式碼。

### 產出

- **`docs/PHASE5_COMPANION_BEHAVIOR_PLAN.md`** — 新建，包含：
  - Phase 5 目標（idle、greeting、return greeting、time-aware、proactive、expression integration）
  - 功能範圍（In Scope / Out of Scope / Later）
  - 安全邊界（9 條永久限制）
  - 技術設計草案（純前端 MVP、idle timer、anti-spam、mood 對接、不新增 backend endpoint）
  - MVP 任務拆分（TASK-108 ~ TASK-112）
  - Phase 6+ 備忘錄

### 安全邊界確認

- 不自動讀檔 ✅
- 不自動讀 Email / Calendar ✅
- 不自動執行命令 ✅
- 不自動呼叫外部 API ✅
- 不使用精確定位 ✅
- 不在未確認時發送訊息或操作系統 ✅
- `/chat` schema 不變（`reply / mood / source`）✅
- Renderer 不直連 Ollama ✅

### Next Task

TASK-108 - Idle State UI Behavior

---

## TASK-108 — Idle State UI Behavior

**Status:** DONE
**Date:** 2026-05-23

### Goal

在 `renderer.js` 實作前端 idle timer，閒置 N 分鐘後切換克莉絲蒂娜表情（neutral / sleepy），
使用者互動後重設計時。不新增 backend endpoint，不修改 `/chat` schema。

### 範圍

- 新增 `lastActivityTime` 追蹤（鍵盤 / 點擊事件更新）
- `setInterval` 每分鐘檢查 idle 時間
- 3 分鐘 idle → `setPetExpression("neutral")` + hint text
- 10 分鐘 idle → `setPetExpression("sleepy")` + hint text
- 互動重設 → 恢復原 mood
- **不新增 backend endpoint**
- **不呼叫 `/chat`**

### 驗收條件

- `node --check apps/desktop/src/renderer/renderer.js` PASS
- `node --check apps/desktop/src/renderer/renderer.js` PASS（lint clean）
- `npm run test:renderer` PASS
- Renderer safety scan：無 Ollama 直連

### 完成記錄

- `renderer.js`：新增 `IDLE_THRESHOLD_SHORT_MS`（3 min）、`IDLE_THRESHOLD_LONG_MS`（10 min）常數；
  `resetActivity()` 頂層函式（vm sandbox 可存取）；`idleTick(_now)` 接受選用合成時間戳（供測試用）；
  `setInterval(idleTick, IDLE_CHECK_INTERVAL_MS)` 啟動輪詢；
  `msgInput / sendBtn / window / document` 互動事件 listener。
- `renderer-chat-smoke.js`：新增 `FakeDocument.addEventListener`、fake `setInterval`、
  `window.addEventListener` stub；新增 6 個 idle behavior 測試。
- 全部驗收條件通過：syntax check PASS、smoke tests PASS（含 6 新測試）、safety scan CLEAN、pytest 586 passed。

### Next Task

TASK-109 - Startup Greeting

---

## TASK-109 — Startup Greeting

**Status:** DONE
**Date:** 2026-05-23

### Goal

App 啟動成功後，在 pet hint 區域顯示一句靜態角色問候語，
設定 `setPetExpression("proud")`。不依賴 LLM，不呼叫 `/chat`。

### 範圍

- `setPetExpression("proud")` + `setPetHint("哼，汝終於把吾叫醒了。今天也要好好努力，知道嗎？")`
- 於 startup IIFE `setMood("neutral")` 之後立即呼叫
- `currentMood` 維持 "neutral"，idle timer restore 正確
- **不呼叫 `/chat`**（純靜態 UI 更新，不依賴 LLM 可用性）

### 驗收條件

- app 啟動後 pet-display-hint 含問候語 ✓
- startup 後 pet-face data-mood = "proud" ✓
- 無 /chat 呼叫 ✓
- idle 3 分鐘後 hint 正常切換（問候語被覆蓋）✓
- `node --check` PASS ✓
- `npm run test:renderer` PASS（含 4 個新測試）✓
- 受影響的 TASK-086 PNG fallback 測試已更新（testNeutralMoodUsesPngImageWhenAvailable、testPngLoadFailureFallsBackToSvg）✓

### 完成記錄

- `renderer.js`：在 startup IIFE 的 `setMood("neutral")` 之後加入 `setPetExpression("proud")` 與 `setPetHint(greeting)`。
- `renderer-chat-smoke.js`：新增 4 個測試（hint visible、expression proud、no /chat、idle still works）；更新 2 個受影響的 TASK-086 PNG 測試。
- 全部驗收通過：syntax check PASS、smoke 全部通過（含新測試）、safety scan CLEAN、pytest 586 passed、git diff --check CLEAN。

### Next Task

TASK-110 - Return-from-Away Greeting

---

## TASK-110 — Return-from-Away Greeting

**Status:** DONE
**Date:** 2026-05-23

### Goal

使用者在長時間 idle（≥ 15 分鐘）後重新互動時，顯示一句 return greeting。
設定 `setPetExpression("annoyed")`。不修改 `/chat` 請求或回應格式，不呼叫 LLM。

### 範圍

- `IDLE_THRESHOLD_RETURN_MS = 15 分鐘`（已存在於常數）
- `awayGreetingEligible` flag：`idleTick` 於 elapsed ≥ 15 min 時設為 true
- `awayGreetingFired` flag：spam guard，同一次 away 只觸發一次；進入 long_idle 時重設
- long-idle（≥ 10 min）後首次互動 + elapsed ≥ 15 min → 顯示 return greeting
- 短時間 idle 不觸發
- **不呼叫 `/chat`**
- **不修改 `/chat` schema**

### 驗收條件

- long-idle 後互動可見 return greeting ✓
- 短 idle 後互動不觸發 ✓
- 同一次 away- 同一次 away 只觸發一次 ✓
- 重新進入 long_idle 可重置資格 ✓
- 無 /chat 呼叫 ✓
- `node --check` PASS ✓
- `npm run test:renderer` PASS（含 5 個新測試） ✓

### 完成記錄

- `renderer.js`：新增 `IDLE_THRESHOLD_RETURN_MS`、`awayGreetingEligible`、`awayGreetingFired` 狀態變數；
  `idleTick` 新增 elapsed ≥ 15 min 時設 `awayGreetingEligible = true`；
  `resetActivity` 新增 return greeting 邏輯：`awayGreetingEligible && !awayGreetingFired` 時顯示 annoyed 表情與 hint；進入 long_idle 時重設 `awayGreetingFired = false`。
- `renderer-chat-smoke.js`：新增 5 個測試（return greeting 可觸發、no /chat、spam guard、short idle 不觸發、re-entry reset）。
- 全部驗收通過：syntax check PASS、smoke 全部通過、safety scan CLEAN、pytest 586 passed、git diff --check CLEAN。

### Next Task

TASK-111 - Expression Timing Polish

---

## TASK-111 — Expression Timing Polish

**Status:** DONE
**Date:** 2026-05-23

### Goal

改善表情與 hint 的 timing，避免 startup greeting、idle hint、return greeting
被其他狀態太快覆蓋。保持 UI-only，不新增 backend、不呼叫 LLM。

### 範圍

- `HINT_LOCK_MS = 8000`：重要 greeting 後的 hint lock 期間
- `hintLockedUntil`：timestamp；`lockCompanionHint(durationMs)` 頂層函式（vm sandbox 可存取）
- `idleTick` 検查 `now < hintLockedUntil`；lock 期間不覆蓋 hint/expression
- startup greeting （TASK-109）後立即呼叫 `lockCompanionHint(HINT_LOCK_MS)`
- return-from-away greeting （TASK-110）後立即呼叫 `lockCompanionHint(HINT_LOCK_MS)`
- error/offline/pending 仍可覆蓋（重要 runtime 狀態，不検查 lock）
- chat response mood 仍可覆蓋（`setMood` 直接呼叫 `setPetExpression`，不検查 lock）
- **不呼叫 `/chat`**
- **不修改 `/chat` schema**

### 驗收條件

- startup lock 阻止 idleTick 覆蓋 greeting ✓
- lock 過期後 idle 正常生效 ✓
- return greeting lock 阻止 idleTick 覆蓋 ✓
- chat response mood 可覆蓋 lock ✓
- pending/error/offline 可覆蓋 lock ✓
- `node --check` PASS ✓
- `npm run test:renderer` PASS（含 5 個新測試） ✓

### 完成記錄

- `renderer.js`：新增 `HINT_LOCK_MS = 8000`、`hintLockedUntil = 0`、`lockCompanionHint(durationMs)` 頂層函式；
  `idleTick` 新增 `locked` 検查；lock 期間跳過 hint/expression 更新；
  startup IIFE `setPetHint(greeting)` 後呼叫 `lockCompanionHint(HINT_LOCK_MS)`；
  `resetActivity` 的 return greeting 後呼叫 `lockCompanionHint(HINT_LOCK_MS)`。
- `renderer-chat-smoke.js`：新增 5 個測試（startup lock 阻止 idle、lock 過期可 idle、return lock 阻止 idle、chat 可覆蓋、pending 可覆蓋）。
- 全部驗收通過：syntax check PASS、smoke 全部通過（含 TASK-108、109、110、111 所有測試）、safety scan CLEAN、pytest 586 passed、git diff --check CLEAN。

---

## TASK-112：Phase 5 Companion Behavior Smoke Tests / Checkpoint

**狀態：DONE**
**日期：2026-05-24**

### 目標

不新增功能。針對 Phase 5 companion behavior（TASK-108~111）進行整體 smoke / checkpoint，
確認各流程整合穩定，補強測試覆蓋率，並更新文件。

### 範圍

- 純測試補強：不修改 `renderer.js`，不新增 backend route，不修改 `/chat` schema
- 檢查並補強 smoke 測試的覆蓋缺口：
  - **error/offline 可覆蓋 greeting lock**（TASK-111 原始測試未覆蓋 lock 期間的 error/offline）
  - **startup greeting 不破壞 source/runtime status pipeline**
  - **Phase 5 端對端整合流程**（startup → lock → 過期 → idle → long idle → return greeting）
- 安全驗證：確認 renderer 無直接 Ollama URL、不自動呼叫 /chat

### 新增測試（4 個）

1. `testNetworkErrorOverridesGreetingLock`：network error 在 lock 期間 → expression = "offline"
2. `testProviderErrorOverridesGreetingLock`：provider timeout 在 lock 期間 → expression = "error"
3. `testSourceRuntimeStatusNotClearedByStartupGreeting`：startup greeting 不破壞 mood-label / source-status pipeline；chat 後仍可正確更新
4. `testPhase5FullCompanionIntegrationFlow`：端對端整合（5 個子階段 A~E）：
   - A：startup greeting, proud expression, 不呼叫 /chat
   - B：lock 阻止 3-min idle hint
   - C：lock 過期後 idle hint 生效
   - D：10-min idle → sleepy
   - E：15-min + resetActivity → return greeting, annoyed, 不呼叫 /chat

### 驗收條件

- startup greeting ✓，proud expression ✓，不呼叫 /chat ✓，source/runtime status pipeline 正常 ✓
- 3-min idle → neutral hint ✓，10-min idle → sleepy ✓
- lock 阻止 idle 覆蓋 ✓，lock 過期後 idle 生效 ✓
- 15-min + resetActivity → return greeting（annoyed）✓，不 spam ✓，re-enter 後可再觸發 ✓
- pending 可覆蓋 lock ✓，error/offline 可覆蓋 lock ✓，chat response 可覆蓋 lock ✓
- PNG/SVG fallback 仍正常 ✓
- renderer 無直接 Ollama URL ✓，不自動呼叫 /chat ✓
- `node --check` PASS ✓
- `npm run test:renderer` PASS（含 4 個新 TASK-112 測試，共 53 個測試） ✓
- safety scan CLEAN ✓
- `python -m pytest` 586 passed ✓
- `git diff --check` CLEAN ✓

### 完成記錄

- `renderer.js`：未修改（TASK-112 為純 checkpoint，不新增功能）
- `renderer-chat-smoke.js`：新增 4 個 TASK-112 測試（error/offline override lock、
  source/runtime status pipeline、Phase 5 端對端整合 A~E）；smoke harness 共 53 個測試
- 全部驗收通過：syntax PASS、smoke 53/53 PASS、safety CLEAN、pytest 586 passed、git diff --check exit 0
- Phase 5 所有任務（TASK-107~112）全數完成 → Phase 5 COMPLETE

**下一步**：Phase 5 完整收尾，可考慮 commit / tag；若繼續開發可規劃 Phase 6。

---

## TASK-113 — Sticky Chat Composer / Better Chat Scroll UX（DONE）

### 問題

1. Input bar 在 HTML 中位於 memory / audit / provider settings 之後 — 使用者需捲動才能輸入
2. AI 回覆每次強制捲到底部，中斷閱讀歷史記錄的體驗
3. 不適合 desktop-pet + chat 的使用情境

### 實作內容

**`index.html`**
- 將 `<div id="memory-toggle-bar">` 和 `<footer id="input-bar">` 移至 `<main id="chat-area">` 之後，settings sections 之前
- Settings sections（memory / audit / provider）現在位於 chat + input 區塊之下（below the fold）

**`styles.css`**
- `body`：`padding-bottom: 14px` → `padding-bottom: 0`
- `#input-bar`：加入 `position: sticky; bottom: 0; z-index: 10`
- `@media (max-width: 700px)` body：移除 `padding-bottom: 10px`

**`renderer.js`**
- 新增 `CHAT_NEAR_BOTTOM_THRESHOLD_PX = 80` 常數
- 新增三個 scroll 輔助函式：`isChatNearBottom()`、`scrollChatToBottom()`、`maybeScrollChatToBottom()`
- `appendMessage(role, text)` → `appendMessage(role, text, { autoScroll = false } = {})`：移除無條件捲動，改由 caller 控制
- `sendMessage()`：
  - user 訊息、loading 訊息：`{ autoScroll: true }` — 永遠捲到底
  - pet 回覆：`maybeScrollChatToBottom()` — 只在 user 接近底部時才捲
  - error 訊息：`maybeScrollChatToBottom()`
- 同步修正：`testLoadingColdStartStatusIsVisible` 的根本原因（`currentProviderSettings = {}` 在 startup 時）已由既有 startup IIFE 中的 `loadProviderSettings()` 解決；
  TASK-113 patch 從 git clean version 重新套用，確保 IIFE 完整保留

**`renderer-chat-smoke.js`**（FakeElement 更新 + 5 個新測試）
- `FakeElement`：新增 `this.clientHeight = 0`；`appendChild` 改為 `Math.max(scrollHeight, children.length)`
- `testChatComposerExistsAndIsNotRemovedByMessageAppend`：input bar 在訊息追加後仍存在
- `testUserSendScrollsChatToBottom`：user send 時強制捲到底
- `testAiReplyDoesNotScrollWhenUserScrolledUp`：user 捲上去時 AI 回覆不干擾位置
- `testAiReplyScrollsWhenUserIsNearBottom`：user 在底部時 AI 回覆自動捲動
- `testScrollHelpersExistInSandbox`：三個 scroll 輔助函式存在於 sandbox

### 安全限制（均未違反）

- 不自動呼叫 `/chat` ✗
- 不新增 backend route ✗
- 不修改 `/chat` schema ✗
- 不修改 provider settings / Ollama routing ✗
- 不修改 persona prompt ✗
- 不新增外部 API ✗

### 驗收條件

- `node --check renderer.js` PASS ✓
- `node scripts/renderer-chat-smoke.js` PASS（56 個測試，含 5 個新 TASK-113 測試）✓
- safety scan CLEAN ✓
- `python -m pytest` 586 passed ✓
- trailing whitespace CLEAN ✓

### 完成記錄

- `apps/desktop/src/renderer/index.html`：input bar 移至 chat area 之後
- `apps/desktop/src/renderer/styles.css`：input bar sticky bottom
- `apps/desktop/src/renderer/renderer.js`：scroll helpers + autoScroll appendMessage
- `apps/desktop/scripts/renderer-chat-smoke.js`：FakeElement clientHeight + 5 新測試
- 全部驗收通過：syntax PASS、smoke 56/56 PASS、safety CLEAN、pytest 586 passed

**下一步**：可 commit TASK-113；繼續規劃 Phase 6 或下一個 UX 改善任務。
