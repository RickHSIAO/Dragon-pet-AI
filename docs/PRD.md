# Product Requirements Document (PRD)

> dragon-pet-ai MVP
> Status: DRAFT
> Last Updated: 2026-05-19
> Owner: TASK-001

---

## 1. Project Summary

**dragon-pet-ai** is an AI-powered desktop pet companion designed to live on the user's screen as a persistent, interactive character.

The goal is to create a desktop companion that can:
- Chat with the user in a natural, character-consistent manner
- Remember selected long-term information across sessions
- Express a distinct personality through its responses
- Eventually support voice interaction and light task assistance

Unlike traditional productivity tools or chatbots, dragon-pet-ai aims to combine **emotional presence** with **practical utility** — a companion that is both a friend and a lightweight workflow assistant.

---

## 2. MVP Goal

The Minimum Viable Product (MVP) must deliver a functional, usable desktop companion experience with the following capabilities:

| Capability | Description |
|---|---|
| Desktop character window | A persistent window showing the pet character |
| Text chat | User can type messages and receive character-style responses |
| Character-style responses | Responses reflect a defined personality (tone, style, name) |
| Local conversation history | Messages are stored locally and retrievable |
| Basic long-term memory | User can store important facts the pet will recall later |
| Basic task list | User can maintain a simple task list via conversation |
| Daily summary placeholder | Structure exists for future daily recap feature |

**Explicitly NOT in MVP:**
- Autonomous computer control
- Voice (TTS/STT)
- Live2D animation
- Cloud sync

---

## 3. Target User

**Primary User:** A single personal user (no multi-user support in MVP)

**Profile:**
- Works on a computer for extended periods (developer, writer, designer, researcher, etc.)
- Wants more than a plain chatbot — values emotional connection and persistent memory
- Comfortable with a desktop app that stays on screen
- Values privacy: prefers local-first data storage over cloud

**Core Need:**
> "I want an AI companion that knows me over time, helps me stay organized, and keeps me company while I work — without being intrusive."

---

## 4. Core MVP Features

### 4.1 Desktop Pet Window
- A resizable, always-on-top (optional) desktop window
- Displays a static character image (Live2D not required for MVP)
- Window can be minimized or hidden

### 4.2 Text Chat
- Input field for user messages
- Chat history visible in scrollable view
- Keyboard shortcut to open/focus chat

### 4.3 Character Prompt
- Defined character name, personality traits, and response style
- System prompt loaded at backend startup
- Character consistency maintained across sessions

### 4.4 Conversation Storage
- All messages (user + pet) stored locally in SQLite
- Conversation session tagging (by date or session ID)
- Retrievable for context injection

### 4.5 Long-Term Memory Records
- Key facts explicitly marked for long-term retention
- Stored separately from raw conversation history
- Injected into context on each session start
- User can view and delete memory entries

### 4.6 Character State
- Internal state tracking (e.g., mood, energy)
- State influences response tone (e.g., tired pet responds differently)
- State persists across sessions

### 4.7 Relationship State
- Tracks cumulative interaction quality (e.g., affinity level)
- Simple integer or enum value
- Influences character personality expression

### 4.8 Basic Task List
- User can ask the pet to add, list, or complete tasks
- Tasks stored locally in SQLite
- No calendar integration in MVP

### 4.9 Daily Summary Placeholder
- Schema and API endpoint reserved for daily summary
- Not fully implemented in MVP; structure defined for Phase 3+

---

## 5. Out of Scope for MVP

The following are explicitly excluded from MVP to keep scope manageable:

| Feature | Reason Excluded |
|---|---|
| Live2D animation | High complexity, not core to MVP value |
| Full voice conversation (TTS/STT) | Deferred to Phase 4 |
| Autonomous terminal execution | Safety risk; requires dedicated safety layer |
| Automatic file modification | Safety risk |
| Cloud sync | Privacy concern and complexity |
| Mobile app | Different platform; deferred entirely |
| Multi-user support | Single-user only in MVP |
| Payment system | Not applicable for MVP |
| Full agent autonomy | Requires extensive safety design first |
| Calendar integration | Deferred to Phase 5 |
| Web search | Deferred to Phase 5 |

---

## 6. User Stories

### Core Chat & Companion

1. **As a user**, I want to type a message and receive a character-style response, so that I can have a natural conversation with the pet.

2. **As a user**, I want the pet to maintain a consistent personality and name across all conversations, so that it feels like a real companion rather than a generic chatbot.

3. **As a user**, I want the pet to remember important facts I tell it (e.g., my name, preferences, current projects), so that it feels personal and avoids asking me the same things repeatedly.

4. **As a user**, I want to view my past conversations with the pet, so that I can reference previous discussions and maintain continuity.

### Memory & State

5. **As a user**, I want the pet to have an internal state (mood, energy), so that interactions feel dynamic rather than static.

6. **As a user**, I want to see the relationship level grow over time, so that I feel the companionship deepens through repeated interactions.

7. **As a user**, I want to view and manage my stored long-term memories, so that I stay in control of what the pet knows about me.

8. **As a user**, I want the pet to recall long-term memories automatically at the start of each session, so that it doesn't forget important context when I reopen the app.

### Task & Workflow

9. **As a user**, I want to tell the pet to add a task to my list, so that I can capture todos without switching to another app.

10. **As a user**, I want to ask the pet what tasks I have pending, so that I can get a quick overview of my to-do list through conversation.

11. **As a user**, I want to mark a task as done by telling the pet, so that my task list stays up to date conversationally.

### Presence & UX

12. **As a user**, I want the pet window to stay visible on my desktop while I work, so that I can glance at it and feel accompanied without switching apps.

13. **As a user**, I want all my data (conversations, memory, tasks) stored locally, so that my private information never leaves my machine without my consent.

---

## 7. MVP Acceptance Criteria

The MVP is considered complete when all of the following are true:

### Functional
- [ ] User can open the desktop app and see the character window
- [ ] User can type a message and receive a response in character voice
- [ ] User can scroll through past messages in the current session
- [ ] Messages are persisted to local SQLite database
- [ ] Long-term memory entries are saved and injected into new sessions
- [ ] User can view, add, and delete memory entries via UI or chat
- [ ] Character state (mood/energy) persists across app restarts
- [ ] Relationship state increments over interactions
- [ ] User can add, list, and complete tasks via chat
- [ ] Daily summary endpoint exists (even if it returns a placeholder)

### Non-Functional
- [ ] All data is stored locally (no external network calls except to LLM API)
- [ ] App starts in under 5 seconds on a modern laptop
- [ ] No autonomous file modification capability exists
- [ ] No shell command execution capability exists
- [ ] Character prompt is configurable without code changes

### Safety
- [ ] No action can be taken on the user's file system without explicit user command
- [ ] No external messages (email, Slack, etc.) can be sent by the pet
- [ ] Memory writes require explicit user intent or confirmation
