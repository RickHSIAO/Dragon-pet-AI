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

Status: IN_PROGRESS

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
- TASK-005 is recorded as IN_PROGRESS
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
