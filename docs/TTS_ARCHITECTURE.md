# TTS Architecture

**Task:** TASK-TTS-001 / TASK-TTS-003
**Status:** TASK-TTS-003 IMPLEMENTED - LOCAL TTS PROVIDER PROBE SMOKE PASS / NO RUNTIME WIRING
**Date:** 2026-06-18
**Scope:** Provider-neutral architecture plus TASK-TTS-002 backend mock skeleton
and TASK-TTS-003 local provider candidate probe. No runtime wiring, real
synthesis, playback, dependency, generated audio, schema change, STT behavior
change, or Conversation Mode behavior change is added by TASK-TTS-003.

This document defines the target architecture for Christina voice output and the
implemented TASK-TTS-002 mock skeleton. It remains provider-neutral: Dragon Pet
AI should be able to evaluate local and low-cost voices without hard-coding one
engine as the permanent path.

TASK-TTS-002 implementation checkpoint:

- Backend package `backend/app/tts/` now exists.
- `MockTTSProvider` returns deterministic metadata only.
- `normalize_tts_text()` produces TTS-safe chunks from visible reply text.
- `TTSService` exposes metadata-only preview and disabled queue diagnostics.
- Defaults are `TTS_ENABLED=false`, provider `mock`, voice `christina_mock`.
- No `/tts` route, renderer controls, Pet Window runtime, real synthesis,
  playback, generated audio, external dependency, or auto-speaking is added.

TASK-TTS-003 implementation checkpoint:

- `scripts/tts_provider_probe.py` probes candidate provider availability without
  runtime wiring.
- The probe reuses TASK-TTS-002 text normalization.
- Reports are JSON/Markdown local artifacts under ignored
  `outputs/tts_provider_probe/YYYYMMDD/`.
- `mock` is always available; optional candidates skip with `available=false`
  and a reason when unavailable.
- Audio generation is off by default and no TASK-TTS-003 provider generates
  audio.
- No provider is selected as final.

---

## 1. Goals

- Prepare a local-first TTS architecture for Christina voice output.
- Support Chinese speech; Taiwan accent is not required.
- Prefer Japanese/anime-style voice direction where available and legally usable.
- Keep ElevenLabs and other cloud providers out of the first architecture path.
- Allow later experiments with multiple local providers.
- Keep runtime TTS disabled by default until implemented and smoke-tested.
- Keep Conversation Mode STT/backpressure independent from TTS playback.

Non-goals for TASK-TTS-001:

- No runtime TTS playback implementation.
- No new package dependency.
- No external paid API dependency.
- No ElevenLabs integration.
- No voice cloning, enrollment, or recording changes.
- No generated audio, voice samples, temp WAVs, embeddings, local settings, logs,
  or reports committed.
- No `/chat` schema or mood schema change.
- No STT default or STT model selector behavior change.
- No Conversation Mode queue/backpressure behavior change.
- No Owner Voice hard-gate behavior change.

---

## 2. Runtime Placement

Recommended split:

| Component | Location | Responsibility |
|---|---|---|
| TTS request trigger | Full App renderer and Pet renderer call sites, future task | Submit only accepted assistant replies to the TTS queue when user-enabled. Not implemented by TASK-TTS-002. |
| Text normalization | `backend/app/tts/text_normalizer.py` | TASK-TTS-002 implements conservative backend chunking helper; renderer/shared reuse is future. |
| TTS queue controller | `backend/app/tts/tts_service.py` diagnostics skeleton; renderer queue future task | TASK-TTS-002 exposes disabled queue diagnostics only. No playback queue dispatch. |
| Provider adapter | `backend/app/tts/providers.py` | TASK-TTS-002 implements `TTSProvider` protocol and metadata-only `MockTTSProvider`. Real synthesis adapters are future. |
| Provider candidate probe | `scripts/tts_provider_probe.py` | TASK-TTS-003 checks optional provider availability and writes local reports. No runtime wiring or playback. |
| Local external process | Optional provider-specific sidecar, future task | Run heavy local engines outside Electron renderer/main. |
| Playback | Renderer/Pet Window, future task | Play audio through browser audio APIs or an explicit playback bridge. |
| Electron main | Narrow IPC only if needed, future task | Bridge local process/audio file handles without exposing broad filesystem APIs. |

Default architecture decision:

1. Keep orchestration close to the renderer because TTS is a UI output, not a
   chat decision.
2. Put heavy local synthesis behind backend or sidecar adapters so model loading
   and subprocess failures do not freeze the renderer.
3. Keep Electron main as a narrow bridge only. It should not own TTS policy,
   prompt text, persona decisions, or provider selection logic.
4. Treat local external providers as replaceable adapters. Provider-specific
   setup, model download, and GPU/CPU runtime requirements belong to explicit
   future tasks.

---

## 3. Target Pipeline

```text
accepted chat reply
-> TTS eligibility gate
-> text normalization
-> sentence chunking
-> TTS queue
-> provider adapter
-> synthesized audio or stream
-> playback controller
-> Pet speaking state / diagnostics
```

Rules:

- The trigger is an accepted assistant reply only.
- TTS never calls `/chat`.
- TTS never sends user audio or generated audio to `/chat`.
- TTS does not read Full App diagnostics, hidden details, raw provider metadata,
  prompt text, chain/system/debug metadata, or Output Queue payload internals.
- TTS-safe text is derived from visible reply text, not from hidden diagnostic
  state.
- Provider failure must degrade to visual reply only, not retry `/chat`.

---

## 4. Provider Abstraction

Implemented TASK-TTS-002 shape:

```text
TTSSynthesisRequest:
  chunks
  provider
  voice
  language_hint
  style_hint
  request_id

TTSSynthesisResult:
  provider
  voice
  chunks
  estimatedDurationMs
  synthesisStatus
  audioAvailable
  audioPath
  error
```

`MockTTSProvider` returns:

- `provider=mock`
- `voice=christina_mock` by default
- normalized chunks
- deterministic estimated duration
- `synthesisStatus=mock_success` or `empty`
- `audioAvailable=false`
- `audioPath=null`

No audio file, audio bytes, stream reference, model load, subprocess, network
request, or external dependency is used.

Future real-provider interface shape:

```text
TtsProvider.synthesize(request) -> TtsResult

request:
  providerId
  voiceId
  languageHint
  styleHint
  chunkText
  rate
  pitch
  volume
  requestId

result:
  ok
  providerId
  requestedVoiceId
  resolvedVoiceId
  audioRef or audioBytes or streamRef
  mimeType
  durationMs
  synthesisLatencyMs
  errorCode
  safeMessage
```

Provider contract:

- `mock` provider is implemented first for tests and queue behavior.
- Local providers must be selectable by configuration, not hard-coded in call
  sites.
- Provider adapters must return safe error codes and safe messages, not raw
  stack traces.
- Provider-specific model paths, subprocess commands, and local cache paths must
  not be exposed to Pet Bubble speech.
- Cloud providers are not part of the first path. If ever added, they require a
  separate opt-in, cost/privacy design, and explicit user acknowledgement.

Initial provider ids:

| Provider id | Role |
|---|---|
| `mock` | Deterministic tests, disabled/default diagnostics, no audio generation. |
| `web_speech` | Existing platform/browser capability reference; useful fallback, not the architecture lock-in. |
| `local_sidecar` | Generic local process adapter for model-based experiments. |
| `local_http` | Generic localhost adapter for a separately launched TTS lab server. |

---

## 5. Text Normalization

TTS text normalization should run before queue admission.

TASK-TTS-002 implements the backend helper `normalize_tts_text()` with max chunk
length/count guards. It accepts visible assistant reply text and returns a list
of safe chunks; it does not invent replacement narration.

Inputs:

- Visible assistant reply text from `/chat` success path.
- Optional mood/expression only as a style hint, never as spoken text.
- Optional language hint, normally `zh-TW` or `zh`.

Required cleanup:

- Strip Markdown code fences and inline code markers.
- Skip or summarize long code blocks instead of reading them verbatim.
- Remove debug labels, source labels, hidden details, JSON-like diagnostics,
  stack traces, local URLs, local file paths, and provider internals.
- Remove markdown table separators and excessive bullets.
- Collapse repeated whitespace.
- Keep Traditional Chinese text readable when present.
- Keep Christina voice concise; do not read long technical diagnostics unless the
  user explicitly requests spoken diagnostics in a future task.

Chunking:

- Split on Chinese and Western sentence punctuation.
- Keep chunks short enough for provider stability.
- Preserve ordering.
- Drop empty chunks.
- Enforce a max chunk count and max characters per chunk.
- Long replies should either stop after a safe limit or require explicit user
  action to continue speaking.

Forbidden spoken sources:

- raw user message text outside the visible reply
- hidden chain/system/developer/debug metadata
- Voice Diagnostics
- Owner Voice scores, thresholds, paths, or embeddings
- Output Queue raw payloads
- provider stack traces
- JSON responses
- screenshots/OCR raw data unless a future task explicitly designs spoken screen
  summaries

---

## 6. Playback Queue

The TTS queue is separate from the Conversation Mode STT queue.

TASK-TTS-002 implements only a disabled backend queue diagnostics model:

```text
enabled=false
provider=mock
requestedVoice=christina_mock
resolvedVoice=christina_mock
queueLength=0
activeJobId=null
chunksCount=<last preview chunk count>
lastSynthesisStatus=not_started | mock_success | empty
lastError=null
playbackStatus=disabled
autoSpeakEnabled=false
```

Preview does not enqueue runtime playback. `queueLength` remains `0` and
`activeJobId` remains `null`.

Queue item shape:

```text
ttsJob:
  id
  sourceReplyId
  sourceSurface: full_app | pet_window | conversation_mode
  providerId
  voiceId
  chunks[]
  currentChunkIndex
  status: queued | synthesizing | ready | playing | stopped | failed | complete
  interruptible
  createdAt
  startedAt
  completedAt
```

Queue rules:

- TTS is disabled by default.
- Only one TTS job may play at a time.
- New accepted replies should interrupt or replace older speech according to a
  documented user setting; first implementation should prefer "new reply stops
  current speech" to avoid overlap.
- Stop must cancel queued and active chunks.
- Provider synthesis should be cancellable when the provider supports it; when
  not supported, ignore late results after stop.
- Queue diagnostics must remain local, safe, and text-only.
- The existing Output Queue can record diagnostics later, but TTS dispatch must
  not be enabled until a future task explicitly connects it.

---

## 7. Conversation Mode Integration

Conversation Mode must remain STT-first and queue-stable.

Rules:

- TTS may only be considered after a Conversation Mode `/chat` reply is accepted.
- TTS must not block STT transcription, chat queue drain, or backpressure
  pause/resume.
- Conversation Mode queue max remains `4`.
- `queue_full` remains a hard fallback diagnostics path and is not affected by
  TTS.
- TTS playback must not be recorded into the microphone. Future implementation
  must stop, duck, or gate playback before opening a mic recorder.
- TTS must not trigger a new Conversation Mode turn.
- TTS failure must not retry STT or `/chat`.
- Owner Voice dry-run remains non-blocking unless a future hard-gate task
  explicitly changes it.

Recommended future feedback prevention:

1. If Conversation Mode is listening and TTS starts, pause VAD-triggered capture
   or mark the period as playback-muted.
2. If the user starts Manual Mic or Pet mic recording, stop current TTS first.
3. Diagnostics should show whether playback was stopped due to mic capture.
4. Do not implement full duplex speech until a separate barge-in design exists.

---

## 8. Pet Window Integration

Pet Window should remain display-oriented.

Future behavior:

- Pet speaking state may show a small speaking indicator while audio plays.
- Pet expression may use the accepted reply mood/expression already selected by
  the chat flow.
- The speech bubble remains the source of visible reply text.
- TTS failure should leave the visible reply intact and optionally show a small
  non-speaking status in diagnostics or details.
- Pet Bubble must not show provider stack traces, model paths, raw JSON, or
  synthesis diagnostics as normal speech.
- Pet Window IPC remains narrow and allowlisted.

Suggested UI states:

| State | Meaning |
|---|---|
| `tts_disabled` | User has not enabled TTS. |
| `tts_queued` | Reply is accepted and waiting to synthesize. |
| `tts_synthesizing` | Provider is generating a chunk. |
| `tts_playing` | Audio is playing; speaking indicator may show. |
| `tts_stopped` | User or mic capture stopped speech. |
| `tts_failed` | Audio failed; visible reply remains available. |

---

## 9. Diagnostics

Future diagnostics should include safe scalar facts:

- TTS enabled/disabled.
- Provider id.
- Requested voice id.
- Resolved voice id.
- Language hint.
- Chunk count.
- Current chunk index.
- Synthesis latency.
- Playback latency.
- Queue length.
- Active job status.
- Stop/interrupt reason.
- Error code and safe fallback.
- Audio source type: generated fresh, cached, or mock.
- Whether audio was cached.

Diagnostics must not include:

- raw generated audio bytes
- local model paths
- voice sample paths
- user audio paths
- owner voice centroid or candidate embeddings
- stack traces
- provider secrets
- hidden prompt/debug/system metadata

---

## 10. Safety and Privacy

- No external network provider by default.
- No generated voice audio committed.
- No voice samples committed.
- No raw user audio persistence.
- No embeddings or voiceprints committed.
- No automatic voice enrollment.
- No silent microphone use.
- No always-listening or wake word in this TTS architecture.
- TTS output is not authentication and must not interact with Owner Voice Gate.
- Provider experiments that require model downloads must be future/manual and
  clearly documented before use.
- Any future cloud provider requires separate BYOK/cost/privacy design.

---

## 11. Testing Plan

TASK-TTS-002 automated tests cover:

- Mock provider returns deterministic safe results.
- TTS disabled by default.
- Normalization strips diagnostics, markdown code fences, JSON-like payloads, and
  stack traces.
- Sentence chunking preserves order and enforces max length.

TASK-TTS-003 automated tests cover:

- Probe report schema and safety flags.
- Mock provider is always available and metadata-only.
- Unavailable/unsupported providers skip without crashing.
- No audio is generated by default.
- JSON/Markdown report creation under a caller-supplied output root.
- TASK-TTS-002 text normalization is reused.

Future runtime tests should cover:

- Queue prevents overlapping playback.
- Stop clears active and pending jobs.
- Late provider result after stop is ignored.
- Conversation Mode accepted reply can enqueue TTS without changing STT queue
  state.
- Manual Mic or Pet mic start stops current speech.
- Pet speaking state toggles only during playback.
- Provider failure leaves visible reply intact.

Manual Windows playback smoke checklist for the first runtime task:

- TTS default OFF on app start.
- Enable TTS explicitly.
- Normal Christina reply speaks once.
- Long reply chunks in order and can be stopped.
- New reply interrupts old speech without overlap.
- Manual Mic start stops speech before recording.
- Conversation Mode remains drained/backpressure-stable.
- Pet speaking indicator appears only during playback.
- Provider failure is clean and does not call `/chat`.
- No generated audio files or logs are written to the repo.

---

## 12. Phased Implementation Plan

- TASK-TTS-002: Mock TTS provider skeleton / disabled-by-default queue. DONE -
  backend metadata-only skeleton; runtime playback not started.
- TASK-TTS-003: Local TTS provider candidate probe. DONE - metadata-only
  reports; no runtime wiring, playback, generated audio, or provider selection.
- TASK-TTS-004: Playback queue and renderer diagnostics.
- TASK-TTS-005: Pet speaking state / bubble sync.
- TASK-TTS-006: Conversation Mode feedback prevention.
- Future: voice quality comparison / singing research.

Implementation should stop after each phase for smoke validation before widening
the runtime surface.

---

## 13. Acceptance

TASK-TTS-001 is complete when:

- `docs/TTS_ARCHITECTURE.md` records the provider-neutral TTS architecture.
- `docs/TTS_PROVIDER_RESEARCH.md` records local provider candidates and research
  boundaries.
- Existing roadmap/task/persona/Pet Bubble/architecture docs point to the new
  design.
- README status is updated.
- Validation smoke scripts still pass.
- No runtime TTS implementation, dependency, generated audio, STT behavior,
  Conversation Mode behavior, Owner Voice behavior, or schema behavior changes
  are committed.

TASK-TTS-002 is complete when:

- `backend/app/tts/` provides a mock provider, text normalizer, service facade,
  and disabled queue diagnostics.
- `backend/tests/test_tts_service.py` covers config defaults, normalization,
  mock metadata, and disabled diagnostics.
- Runtime playback, generated audio, provider downloads, route/UI controls,
  auto-speaking, and real synthesis remain not started.
- `/chat`, mood schema, STT defaults, STT selector, Conversation Mode
  backpressure, and Owner Voice hard-gate behavior remain unchanged.

TASK-TTS-003 is complete when:

- `scripts/tts_provider_probe.py` supports mock plus optional local/future
  candidates.
- Probe reports are written under ignored `outputs/tts_provider_probe/YYYYMMDD/`.
- Unavailable providers return `available=false` with a reason.
- Audio generation is disabled by default and no generated audio/report artifact
  is committed.
- No runtime wiring, `/chat` integration, playback, auto-speaking, dependency,
  route/UI/Pet Window change, schema change, STT behavior change, Conversation
  Mode behavior change, or Owner Voice behavior change is committed.
