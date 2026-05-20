# Streamer Companion Mode

> dragon-pet-ai — Future Product Track
> Status: SIDE TRACK — design exploration only; not scheduled for implementation
> Last Updated: 2026-05-19
> Owner: (unassigned — future planning)

---

## 1. Overview

Streamer Companion Mode is a future product direction that adapts the dragon-pet AI for live streaming contexts (Twitch, YouTube Live, etc.). The pet becomes a visible on-stream character that reacts to stream events, engages with chat, and gives the streamer a consistent on-screen companion — without requiring the streamer to manually interact.

This is a **side track** relative to the current MVP (personal desktop companion). It is documented here to capture the idea without committing implementation resources. No code changes are planned as part of this document.

---

## 2. User Scenarios

### 2.1 Streamer with Overlay

The pet lives in a transparent OBS/Streamlabs overlay on top of the game or scene. It reacts to stream events (new follower, raid, subscription) with short visible animations or emotes, and optionally reads select chat messages aloud or displays them as speech bubbles.

### 2.2 Co-Host Character

The streamer uses the pet as a "co-host" — viewers can direct messages at the pet via a chat command (e.g. `!ask <question>`). The pet replies in character via TTS or a text overlay, adding personality without requiring the streamer to break focus.

### 2.3 Ambient Companion

The pet runs in a corner of the stream silently reacting to energy levels in the stream (e.g. gets excited when donations happen, falls asleep during slow moments). No viewer interaction, just ambient personality.

---

## 3. Unique Requirements vs. Personal Mode

| Requirement | Personal Mode | Streamer Mode |
|---|---|---|
| Visibility | Desktop window (private) | OBS overlay (public broadcast) |
| Audience | User only | Potentially thousands of concurrent viewers |
| Input sources | Keyboard + chat (optional) | Twitch/YouTube Event Sub + chat firehose |
| Response latency | Flexible | Must respond within 2–5 seconds to feel live |
| Content safety | User-controlled | Streamer-moderated public audience; higher bar |
| Cost per session | Low (personal use) | Potentially very high (many events, long sessions) |
| API key exposure risk | Backend env only | Same rule; streamer must not expose key on stream |
| Memory system | Personal facts about user | May need chat-scoped or session-scoped ephemeral memory |
| TTS | Optional future | High value — voice is part of stream personality |

---

## 4. Key Technical Requirements

### 4.1 OBS / Streaming Software Integration

- The pet overlay needs to run as a transparent browser source in OBS, Streamlabs, or similar.
- Options: Electron window with transparent frame, or a local HTTP server serving a browser source page.
- No direct OBS plugin API call is required for MVP — browser source approach is sufficient.

### 4.2 Streaming Platform Event Integration

- Twitch: EventSub API (WebSocket) for follows, subscriptions, raids, bits, channel point redemptions.
- YouTube: YouTube Data API / Live Chat API for chat polling and membership events.
- Both require OAuth app credentials (not user API key) — this is a separate credential surface from LLM API key.
- Rate limit risk: chat firehose can be very high-volume; the pet must not send every chat message to the LLM.

### 4.3 Chat Sampling and Filtering

The pet cannot respond to every chat message in real time at LLM cost. A sampling strategy is required:

- Respond only to `!ask` command prefix (explicit invocation).
- OR random selection from chat (e.g. 1 message per 30 seconds).
- OR keyword-triggered responses (streamer configures trigger words).
- Block or ignore messages that contain blocked terms before sending to LLM.

### 4.4 Content Safety for Public Audience

- Streamer mode operates in a public broadcast context. The pet must not produce content that could embarrass the streamer on stream.
- LLM output must be moderated (filtered for inappropriate content) before display or TTS.
- Chat-injected prompts are a much higher prompt injection risk than personal mode — strict input sanitization required.
- A content safety layer (beyond what Phase 4 implements for personal mode) is a prerequisite for Streamer Mode.

### 4.5 TTS Requirements

- Streamer mode relies heavily on TTS for personality. Text display alone is insufficient for most streaming contexts.
- TTS voice must be unique and recognizable across sessions.
- Latency: TTS must complete within ~2 seconds to feel live.
- Options: local TTS (pyttsx3, edge-tts), cloud TTS (ElevenLabs, Azure), or model-embedded voice.
- TTS is a separate Phase (Phase 5 or later) and is a hard prerequisite for full Streamer Mode.

### 4.6 Cost and Rate Limit Risk

- A single 4-hour stream with moderate chat and events could generate hundreds of LLM requests.
- Cost controls for Streamer Mode are much stricter than personal mode.
- A per-session token budget (hard cap) is required.
- When token budget is exhausted, the pet falls back to event-only reactions (no LLM, no TTS) for the rest of the session.

---

## 5. Safety Boundaries (Additional, Beyond Personal Mode)

| Boundary | Rule |
|---|---|
| Chat prompt injection | All chat-sourced text must be sanitized before being sent to LLM as input |
| Public content moderation | LLM output must be screened before public display or TTS |
| Streamer credential exposure | OAuth tokens for platform EventSub must be stored backend-only, same rules as LLM API key |
| Session token budget | Hard cap on LLM tokens per session; fallback to event-only mode when exceeded |
| No automatic moderation bypass | The pet cannot be instructed by chat messages to bypass content rules |
| Raid / subscription amount display | Financial amounts (bits, subs) should not be displayed as exact currency without streamer opt-in |

---

## 6. What This Track Is Not

- Not an in-stream game or interactive experience (beyond basic reaction + command response)
- Not a chatbot that maintains persistent relationships with individual viewers
- Not a moderation tool or chat filter
- Not a Twitch or YouTube replacement
- Not connected to any payment or subscription flow
- Not a real-time multiplayer feature

---

## 7. Relationship to Current Roadmap

Streamer Companion Mode depends on several capabilities not yet implemented:

| Prerequisite | Current Status |
|---|---|
| Real LLM provider (`LLM_CHAT_ENABLED`) | Phase 4 in progress |
| TTS voice output | Deferred to Phase 5 |
| OBS browser source / transparent overlay | Not designed |
| Streaming platform EventSub integration | Not designed |
| Chat sampling and filtering | Not designed |
| Public content safety layer | Not designed |
| Per-session token budget | Designed conceptually (TASK-044); not implemented |
| BYOK key handling | Phase 4 in progress (TASK-046+) |

**Minimum prerequisites before Streamer Mode can begin implementation:**
1. Phase 4 LLM adapter complete and stable (TASK-037 safety review passed)
2. TTS integrated (Phase 5+)
3. A separate Streamer Mode safety design task (not yet created)

---

## 8. Proposed Future Task Structure

These tasks are **not scheduled** and are listed only for planning reference. No task IDs are assigned.

| Future Task | Name | Type |
|---|---|---|
| STREAM-001 | Streamer Companion Mode Safety Design | Design-only |
| STREAM-002 | OBS Browser Source Overlay Architecture | Design-only |
| STREAM-003 | Twitch EventSub Integration Design | Design-only |
| STREAM-004 | Chat Sampling and Filtering Design | Design-only |
| STREAM-005 | Public Content Safety Layer Design | Design-only |
| STREAM-006 | Per-Session Token Budget Design | Design-only |
| STREAM-007 | Streamer Mode MVP Implementation | Implementation |
| STREAM-008 | Streamer Mode Smoke Check | Validation |

Each design task must complete its safety review before the implementation task begins.

---

## 9. Open Questions

- Should Streamer Mode be a separate product / app, or a mode within the existing personal companion?
- Should it support both Twitch and YouTube at launch, or Twitch-only first?
- What is the right pricing model for Streamer Mode? (BYOK applies cost to the streamer; subscribers may not want to pay per-request costs.)
- How does the pet's memory system interact with transient stream chat context?
- Who owns the content safety responsibility — the streamer, the platform, or this app?
