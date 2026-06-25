# User Guide

## Full App

The Full App is the main desktop interface. It supports chat, local memory
management, provider settings, microphone controls, Conversation Mode,
diagnostics, search, export, and Pet Window controls.

## Chat

Type a message and send it from the chat composer. The backend returns:

```json
{
  "reply": "...",
  "mood": "focused",
  "source": "mock"
}
```

The response schema stays `reply / mood / source`.

## Provider Settings

Provider settings control whether the app uses mock mode or a local provider
such as Ollama. Test Connection is a lightweight backend check; it does not
prove character voice, persona quality, or full `/chat` behavior. Use an actual
chat turn to validate generated replies.

## Memory

Memory records are explicit and local. The app can create, list, deactivate, and
preview local memory records. Runtime memory injection has a two-layer gate:
the backend feature flag must be enabled, and a request must explicitly ask to
use memory.

## Manual Microphone

Manual microphone flow records local audio in the renderer, sends it through
the `stt:transcribe` bridge, and receives a transcript plus diagnostics from
the backend. The transcript can be filled into the composer or sent depending on
the current UI setting.

## Conversation Mode

Conversation Mode is experimental continuous listening. It uses VAD, pre-roll,
sequential STT, and a bounded chat queue. It includes backpressure diagnostics
and can pause recording when the queue is high.

Do not treat Conversation Mode as fully reliable yet.

## Owner Voice Gate

Owner Voice Gate is a dry-run/convenience filter. It can enroll from existing
local WAV paths and verify temporary candidates, but it is not security-grade
authentication and should not hard-block normal app safety assumptions.

## Pet Window

The Pet Window is a compact companion overlay. It can show expressions, speech
bubble state, quiet mode, scale presets, direct input, and Full App handoff. It
uses fixed narrow IPC channels and should not expose generic renderer IPC.

## Search, Export, And History

The Full App supports searching chat history, copying/exporting transcripts,
deleting or undoing recent management actions, and date separators. Exported
files are user-selected local files.

## TTS

Runtime TTS is not enabled. The backend has a mock/disabled TTS skeleton and the
Pet Window has local browser speech controls from earlier prototypes, but no
real character voice provider is active in the app.
