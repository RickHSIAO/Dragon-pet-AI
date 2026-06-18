# TTS Architecture

**Task:** TASK-TTS-001 / TASK-TTS-004C3
**Status:** TASK-TTS-004C3 DONE - EDGE-TTS TUNING REVIEW COMPLETE / NO SUITABLE CHRISTINA VOICE FOUND
**Date:** 2026-06-18
**Scope:** Provider-neutral architecture plus TASK-TTS-002 backend mock skeleton,
TASK-TTS-004A install-free provider review, TASK-TTS-004B VOICEVOX manual
localhost probe, TASK-TTS-004B2 timeout/retry diagnostics, TASK-TTS-004C
edge-tts optional network probe, TASK-TTS-004C2 manual edge-tts dependency /
audio output validation, and TASK-TTS-004C3 docs-first edge-tts tuning
workflow. No runtime
wiring, app playback, runtime/default dependency, schema change, STT behavior
change, Conversation Mode behavior change, or Owner Voice behavior change is
added by TASK-TTS-004C2 or TASK-TTS-004C3.

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

TASK-TTS-004A review checkpoint:

- Windows install-free probe found no real provider ready except `mock`.
- `mock` remains the only safe runtime skeleton provider and is not a
  voice-quality provider.
- `windows_sapi` lacked the optional Python bridge.
- `voicevox_server` was unavailable at `http://127.0.0.1:50021/version`.
- `edge_tts` lacked the optional dependency.
- Piper, GPT-SoVITS, Style-Bert-VITS2, and RVC-like paths remain future/manual
  candidates.
- Runtime playback, renderer queue wiring, Pet speaking state, and
  Conversation Mode feedback prevention should wait for a provider-specific
  manual probe.

TASK-TTS-004B implementation checkpoint:

- `voicevox_server` supports a manually started VOICEVOX Engine-compatible
  localhost server through `scripts/tts_provider_probe.py`.
- Default behavior remains metadata-only: `/version` plus best-effort
  `/speakers`, with no synthesis call, no audio write, and no playback.
- Optional WAV generation requires `--allow-audio-output`; generated files go
  under ignored `outputs/tts_provider_probe/YYYYMMDD/audio/`.
- `--voicevox-url` accepts localhost only; non-localhost URLs are rejected before
  network access.
- `--voicevox-speaker` selects the VOICEVOX speaker/style id for metadata and
  optional synthesis.
- VOICEVOX remains probe-only. No runtime provider has been selected yet, and
  the app runtime remains disabled/mock-only for the new TTS architecture.

TASK-TTS-004B2 implementation checkpoint:

- `voicevox_server` now supports `--voicevox-timeout-sec` with default `30`
  seconds for `/version`, `/speakers`, `/audio_query`, and `/synthesis`.
- `voicevox_server` supports finite `--voicevox-retries` with default `1` for
  local audio stages only.
- Reports include stage diagnostics: `voicevoxStage`, version/speakers/audio
  query/synthesis latency, `timeoutSec`, `retryCount`, `lastExceptionClass`,
  and `lastExceptionMessage`.
- Stage-specific timeout statuses distinguish `audio_query_timeout` from
  `synthesis_timeout`.
- Manual listening found VOICEVOX is technically usable and strong for
  Japanese/anime style, but Chinese text is pronounced as Japanese and is not
  acceptable for Chinese conversation.
- Runtime TTS remains disabled/mock-only; VOICEVOX is still a manual probe path
  and optional Japanese-style experiment candidate, not an app playback provider
  or selected Chinese runtime.
- Provider selection remains unresolved for the main Chinese runtime path.

TASK-TTS-004C implementation checkpoint:

- `edge_tts` supports a deeper optional probe through
  `scripts/tts_provider_probe.py`.
- Default `edge_tts` behavior is metadata-only: it checks whether the optional
  package is installed and does not synthesize, send text to the network, write
  audio, or play audio.
- Optional MP3 generation requires `--allow-audio-output`; generated files go
  under ignored `outputs/tts_provider_probe/YYYYMMDD/audio/`.
- Reports include `voice`, `rate`, `pitch`, `normalizedChunks`,
  `measuredLatencyMs`, `synthesisLatencyMs`, `timeoutSec`, `audioGenerated`,
  `outputPath`, `audioBytes`, `synthesisStatus`, and network safety notes.
- `edge_tts` is network/cloud-ish, not default, not local/offline, and not
  selected as runtime.
- Current machine metadata-only result is safe unavailable:
  `missing_optional_dependency`, `audioGenerated=false`.
- Provider selection remains unresolved for the main Chinese runtime path.

TASK-TTS-004C2 manual probe checkpoint:

- With explicit approval, `edge-tts` was installed into `backend\.venv` only for
  manual provider probing.
- Metadata-only `edge_tts` probe now reports `available=true`,
  `reason=optional_dependency_present`, `synthesisStatus=metadata_only`, and
  `audioGenerated=false`.
- Optional audio probe with `--allow-audio-output` generated an MP3 under
  ignored `outputs/tts_provider_probe/20260618/audio/`.
- The probe and app did not play the MP3.
- Manual listening found Chinese is understandable and the output is acceptable
  as a temporary Chinese provider candidate, but character/anime fit is weak:
  the voice feels more general/Taiwanese than Christina-like, slightly fast,
  and overall `6/10`.
- `edge_tts` remains optional/network/cloud-ish, not default, not wired to
  runtime, and not selected as the final Christina long-term voice.
- Chinese runtime provider selection remains unresolved; the app runtime remains
  disabled/mock-only.

TASK-TTS-004C3 tuning checkpoint:

- No script/runtime change is required because `scripts/tts_provider_probe.py`
  already supports edge-tts voice, rate, and pitch options.
- The tuning workflow compares HsiaoChen, HsiaoYu, and Xiaoxiao Mandarin
  candidates with slower rates and optional pitch checks.
- Generated MP3 files and probe reports remain ignored local artifacts under
  `outputs/tts_provider_probe/YYYYMMDD/`.
- Manual listening found HsiaoChen `-10%` somewhat better but still not enough,
  HsiaoYu `-10%` too old, and Xiaoxiao `-10%` too mainland-China-like for the
  user's preference.
- No edge-tts tuning candidate reached the desired Christina fit. Stop further
  edge-tts tuning for now unless explicitly revisited.
- Chinese runtime provider selection remains unresolved. Recommended next path
  is TASK-TTS-004D Style-Bert-VITS2 / GPT-SoVITS feasibility research for
  long-term character voice.
- Runtime TTS remains disabled/mock-only; edge-tts is not default, not wired to
  `/chat`, not wired to app/Pet Window playback, and not selected as runtime.

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
| Provider candidate probe | `scripts/tts_provider_probe.py` | TASK-TTS-004C checks optional provider availability and can manually probe VOICEVOX localhost WAV or edge-tts MP3 only behind `--allow-audio-output`, with timeout/error diagnostics. No runtime wiring or playback. |
| Provider review | Docs/status only | TASK-TTS-004A records that no real provider is ready except metadata-only `mock`; playback remains blocked pending provider-specific probe. |
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

TASK-TTS-004B automated tests cover:

- VOICEVOX unavailable server skip behavior.
- Default metadata-only behavior does not call synthesis or generate audio.
- `--allow-audio-output` is required for WAV generation.
- Localhost URLs are accepted and non-localhost URLs are rejected before network
  access.
- Mocked `audio_query` and `synthesis` write a WAV under a caller-supplied
  output root.
- VOICEVOX report schema includes safety and audio fields.
- No playback helper is introduced by the probe script.

TASK-TTS-004B2 automated tests cover:

- Default VOICEVOX timeout and retry values in reports.
- CLI timeout/retry option parsing and report override.
- `audio_query_timeout` classification and finite retry count.
- `synthesis_timeout` classification and finite retry count.
- Metadata-only behavior still avoids `audio_query` and `synthesis`.
- Non-localhost rejection still occurs before network access.
- Successful mocked synthesis still writes WAV under a caller-supplied output
  root.
- No playback helper is introduced.

TASK-TTS-004C automated tests cover:

- `edge_tts` missing optional dependency skip behavior.
- Metadata-only behavior does not synthesize, write audio, or send text to the
  service.
- Explicit `--allow-audio-output` success writes MP3 under a caller-supplied
  output root.
- Timeout and error classification.
- Report schema fields for voice, rate, pitch, timeout, synthesis status, audio
  output, and safety notes.
- No playback helper is introduced.
- `edge_tts` does not become a default provider.

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
- TASK-TTS-004A: Local TTS provider selection review. DONE - install-free probe
  reviewed; no real provider selected and `mock` remains the only safe skeleton.
- TASK-TTS-004B: VOICEVOX local server manual probe / optional audio output.
  IMPLEMENTED - probe-only; optional local WAV output requires explicit flag.
- TASK-TTS-004B2: VOICEVOX synthesis timeout / retry hardening and listening
  verdict. DONE - audio output succeeds, but VOICEVOX is not selected for
  Chinese runtime.
- TASK-TTS-004C: edge-tts optional network candidate probe. IMPLEMENTED -
  metadata-only safe probe ready; Chinese audio validation pending.
- TASK-TTS-004C2: edge-tts manual dependency/audio output probe. DONE - MP3
  output succeeds; manual listening accepts it only as a temporary Chinese
  provider candidate, not final Christina voice.
- TASK-TTS-004C3: edge-tts voice/rate tuning probe if slower rate or alternate
  Mandarin voices should be checked. DONE - no suitable Christina voice found;
  keep edge-tts temporary/debug/fallback only and stop tuning for now.
- TASK-TTS-004D: Style-Bert-VITS2 / GPT-SoVITS feasibility research.
- TASK-TTS-004: Playback queue and renderer diagnostics after a real provider
  candidate is validated.
- TASK-TTS-005: Pet speaking state / bubble sync after playback queue validation.
- TASK-TTS-006: Conversation Mode feedback prevention after playback behavior is
  explicit.
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

TASK-TTS-004A is complete when:

- The install-free Windows probe result is recorded in README, roadmap, tasks,
  architecture, and provider research docs.
- `mock` remains documented as the only available safe skeleton provider, not a
  real voice provider.
- No real provider is selected and runtime playback remains not started.
- Recommended next paths are documented as TASK-TTS-004B, TASK-TTS-004C, and
  TASK-TTS-004D.
- No runtime TTS wiring, `/chat` integration, playback, auto-speaking,
  dependency/install, generated audio/report commit, schema change, STT behavior
  change, Conversation Mode behavior change, or Owner Voice behavior change is
  committed.

TASK-TTS-004B is complete when:

- `scripts/tts_provider_probe.py` supports `voicevox_server` localhost metadata
  checks with `--voicevox-url` and `--voicevox-speaker`.
- Default VOICEVOX behavior does not call synthesis, write audio, or play audio.
- `--allow-audio-output` is required before calling `audio_query` and
  `synthesis`.
- Optional WAV files are written only under ignored
  `outputs/tts_provider_probe/YYYYMMDD/audio/`.
- Non-localhost VOICEVOX URLs are rejected.
- Reports include VOICEVOX URL/version/speaker/audio/synthesis safety fields.
- No runtime TTS wiring, `/chat` integration, playback, auto-speaking,
  dependency/install, generated audio/report commit, schema change, STT behavior
  change, Conversation Mode behavior change, or Owner Voice behavior change is
  committed.

TASK-TTS-004B2 is complete when:

- `--voicevox-timeout-sec` and `--voicevox-retries` are documented and wired to
  the VOICEVOX probe.
- Reports include stage latency, timeout, retry, and last exception diagnostics.
- Audio query and synthesis timeout failures are classified separately.
- Default metadata-only behavior still does not call synthesis or write audio.
- Optional WAV files remain gated by `--allow-audio-output` and ignored output
  paths.
- Runtime TTS remains disabled/mock-only with no playback, `/chat`, STT,
  Conversation Mode, Owner Voice, dependency, or schema changes.
- Manual listening verdict and provider decision are recorded: VOICEVOX remains
  probe-only / optional Japanese-style experiment path and is not selected for
  the Chinese runtime provider.

TASK-TTS-004C is complete when:

- `edge_tts` supports safe missing-dependency reporting without failing the
  probe.
- Metadata-only behavior does not synthesize, send text to the network, write
  audio, or play audio.
- Optional MP3 output is gated by `--allow-audio-output` and ignored output
  paths.
- Reports include edge-tts voice/rate/pitch/audio/timeout/synthesis status
  fields and network/cloud-ish safety notes.
- Runtime TTS remains disabled/mock-only with no playback, `/chat`, STT,
  Conversation Mode, Owner Voice, dependency, or schema changes.

TASK-TTS-004C2 is complete when:

- Optional `edge-tts` dependency installation is explicitly approved and scoped
  to `backend\.venv`.
- Metadata-only probe confirms dependency availability without synthesis,
  network text submission, audio write, or playback.
- Optional audio probe with `--allow-audio-output` generates MP3 under ignored
  output paths.
- Manual listening verdict and provider decision are recorded: understandable
  Chinese, temporary provider candidate only, not final Christina voice.
- Runtime TTS remains disabled/mock-only with no playback, `/chat`, STT,
  Conversation Mode, Owner Voice, default provider, or schema changes.
