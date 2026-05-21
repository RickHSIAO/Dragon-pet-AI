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

---

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
TASK-072D - (TBD — OS Keychain implementation or Phase 5 planning)

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
