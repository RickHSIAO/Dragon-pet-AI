# TTS Provider Research

**Task:** TASK-TTS-001 / TASK-TTS-004C2
**Status:** TASK-TTS-004C2 DONE - EDGE-TTS MANUAL AUDIO OUTPUT SUCCESS / LISTENING PENDING
**Date:** 2026-06-18
**Scope:** Provider research, implemented mock-provider skeleton boundary,
TASK-TTS-004A install-free provider review, TASK-TTS-004B manual VOICEVOX
localhost probe, TASK-TTS-004B2 timeout/retry hardening, TASK-TTS-004C
edge-tts optional network candidate probe, and TASK-TTS-004C2 manual
edge-tts dependency/audio output validation. No real
voice-quality provider is selected as final, no model is downloaded, the
`edge-tts` install is optional/manual inside `backend\.venv` only, and no
runtime synthesis/playback path is implemented by TASK-TTS-004C2.

This document records candidate directions for Christina voice output. It should
guide later experiments, not lock Dragon Pet AI to a single TTS engine.

---

## 1. User Preference Summary

- Prefer local/offline or low-cost TTS.
- Prefer Japanese/anime-style voice direction when practical.
- Chinese speech is required.
- Taiwan accent is not required.
- Future singing support is interesting, but not part of TASK-TTS-001.
- ElevenLabs was not satisfying enough and should not be the first architecture
  path.
- The architecture should allow later experimentation.

---

## 2. Evaluation Criteria

Every provider experiment should record:

- Chinese speech quality.
- Christina fit: youthful/anime-style, expressive, concise delivery.
- Latency for short replies and longer chunks.
- CPU/GPU requirement.
- Windows setup complexity.
- Offline behavior.
- License and voice-data requirements.
- Whether custom voice/style data is required.
- Whether generated audio stays local.
- Whether streaming playback is possible.
- Failure behavior and diagnostics.

Do not compare providers by vibe alone. Each provider spike should produce a
small local report with consistent prompts, latency numbers, and a clear caveat
about sample limits.

---

## 3. Candidate Provider Categories

### Mock Provider

Purpose:

- Test queue behavior, disabled-by-default behavior, diagnostics, and text
  normalization without audio generation.

Use first because:

- Deterministic.
- No dependency.
- No generated audio.
- No model download.
- Safe for smoke tests.

Limit:

- Does not prove voice quality.
- TASK-TTS-002 implements this provider as metadata-only backend code under
  `backend/app/tts/`. It returns chunks, estimated duration,
  `synthesisStatus=mock_success`, `audioAvailable=false`, and `audioPath=null`.
  It is a test/diagnostics provider, not a Christina voice-quality candidate.

### Existing Platform / Web Speech

Purpose:

- Lightweight playback reference.
- Can be useful as an emergency fallback or manual smoke helper.

Strengths:

- No bundled model.
- Usually low setup cost.
- Works well for queue, stop, and speaking-state testing.

Limits:

- Voice availability depends on OS/browser.
- Anime-style voice direction is unlikely to be consistent.
- Chinese voice quality depends on installed system voices.
- Should not be treated as the final Christina voice path.

### Local Sidecar Model Provider

Purpose:

- Run heavier local TTS engines outside Electron and behind a stable adapter.

Strengths:

- Best fit for local-first provider experiments.
- Can isolate model loading and crashes.
- Can support future GPU acceleration without freezing UI.

Limits:

- Packaging and setup can be heavy.
- Model downloads must be explicit future/manual steps.
- License and voice-data constraints vary by engine.

### Local HTTP Lab Provider

Purpose:

- Let a separately launched local TTS lab server synthesize audio while Dragon
  Pet AI talks to `localhost` through a narrow adapter.

Strengths:

- Good for experiments before bundling anything.
- Keeps Dragon Pet AI dependency surface small.
- Allows quick comparison across local labs.

Limits:

- Requires explicit server startup.
- Needs health checks and clean timeout handling.
- Must never silently fall back to cloud.

### Optional Cloud Provider

Purpose:

- Future comparison only, not the first implementation path.

Constraints:

- Requires explicit cost/privacy/BYOK design.
- Must be opt-in.
- Must never be default.
- Must never receive text without visible user configuration and consent.

TASK-TTS-001 does not add cloud provider architecture beyond this boundary.

---

## 4. TASK-TTS-003 Provider Candidate Probe

TASK-TTS-003 adds `scripts/tts_provider_probe.py` as a local-only metadata probe.
It writes JSON/Markdown reports under ignored `outputs/tts_provider_probe/YYYYMMDD/`.
Generated reports are local artifacts and must not be committed.

Probe rules:

- No runtime TTS wiring.
- No `/chat` integration.
- No playback or auto-speaking.
- No dependency install.
- No generated audio by default.
- No provider is selected as final.
- Optional providers may be unavailable and should report `available=false` with
  a reason instead of failing the probe.

| Provider | Offline/local? | Chinese support | Anime/Japanese-style suitability | Setup difficulty | Runtime integration risk | Current probe status |
|---|---|---|---|---|---|---|
| `mock` | Local metadata only | Not a real voice | Not a real voice | None | Very low | Always available; metadata-only smoke provider |
| `windows_sapi` | Local OS capability if bridge exists | Depends on installed Windows voices | Usually weak/inconsistent | Low if OS voices and bridge exist | Medium; voice list and language vary by system | Availability check only; no synthesis/playback |
| `voicevox_server` | Localhost server if user runs it | Primarily Japanese; Chinese not native | Strong for Japanese/anime style | Medium; separate server install/start | Medium; local HTTP lifecycle and licensing must be reviewed | Checks `http://127.0.0.1:50021/version`; skipped if absent |
| `edge_tts` | Network/cloud-ish | Usually has Chinese voices | Depends on service voices | Low package setup, but network required | High for privacy/default policy | Optional TASK-TTS-004C probe implemented; metadata-only by default; not default |
| `piper_onnx` | Local/offline | Voice availability varies | Usually weak for anime style | Medium; model selection needed | Medium; packaging/model management | Future/manual candidate, not probed |
| `gpt_sovits` | Local/offline after setup | Possible with correct data/model | Potentially strong | High; data/model workflow | High; licensing, voice data, GPU/runtime complexity | Future research only |
| `style_bert_vits2` | Local/offline after setup | Primarily Japanese-oriented | Potentially strong | High; model/runtime setup | High; packaging and licensing complexity | Future research only |
| `rvc_like` | Local/offline after setup | Voice conversion, not TTS by itself | Potentially useful after TTS source | High; separate source voice and conversion | High; licensing/consent and pipeline complexity | Future research only |

Current recommendation:

- Keep `mock` as the only implemented runtime-safe provider.
- Use TASK-TTS-003 reports to decide which local provider deserves a later
  TASK-TTS-004/TASK-TTS-005 implementation spike.
- Do not make `edge_tts` or any paid/cloud path default.

---

## TASK-TTS-004A Install-Free Probe Review

TASK-TTS-004A reviews the Windows install-free probe result and does not select
a real provider. Runtime playback should not start yet because only `mock` is
available, and `mock` is metadata-only test infrastructure rather than a
Christina voice-quality provider.

Safety flags stayed false:

- `audioOutputAllowed=false`
- `audioGenerated=false`
- `runtimeTtsWired=false`
- `playbackAdded=false`
- `autoSpeakEnabled=false`
- `externalDependencyAdded=false`

| Provider | Availability | Probe reason | Local/offline status | Chinese support expectation | Christina/anime suitability | Setup difficulty | Recommended next action |
|---|---|---|---|---|---|---|---|
| `mock` | Available | `mock_metadata_only` | Local metadata only | Not a real voice | Not a real voice | None | Keep as the only safe skeleton provider |
| `windows_sapi` | Unavailable | `missing_optional_python_bridge` | Local OS capability if bridge exists | Depends on installed Windows voices | Usually weak/inconsistent | Low if bridge and voices exist | Do not prioritize unless a low-setup baseline is needed |
| `voicevox_server` | Unavailable | `server_unavailable:URLError` at `http://127.0.0.1:50021/version` | Localhost server if user runs it | Chinese likely weak or workaround-only | Promising for Japanese/anime style | Medium; separate server install/start | Recommended next local-first manual probe: TASK-TTS-004B |
| `edge_tts` | Unavailable | `missing_optional_dependency` | Network/cloud-ish optional candidate | Likely strong Chinese voice coverage | Variable; not character-specific | Low package setup, but network/privacy caveats | Optional TASK-TTS-004C if fast Chinese validation is priority |
| `piper_onnx` | Unavailable | `future_manual_candidate_not_probed` | Local/offline after model setup | Voice availability varies | Usually weak for anime style | Medium; model selection and packaging | Keep future/manual |
| `gpt_sovits` | Unavailable | `future_manual_candidate_not_probed` | Local/offline after setup | Possible with correct data/model | Potentially strong | High; data/model/GPU/licensing workflow | TASK-TTS-004D feasibility research |
| `style_bert_vits2` | Unavailable | `future_manual_candidate_not_probed` | Local/offline after setup | Primarily Japanese-oriented | Potentially strong | High; model/runtime/licensing complexity | TASK-TTS-004D feasibility research |
| `rvc_like` | Unavailable | `future_manual_candidate_not_probed` | Local/offline conversion after source TTS | Voice conversion, not TTS by itself | Potentially useful after TTS source | High; consent and pipeline complexity | Keep future/manual |

Recommended next provider path:

1. TASK-TTS-004B: VOICEVOX local server manual probe / optional audio output.
2. TASK-TTS-004C: edge-tts optional network candidate probe if fast Chinese
   validation is more important than local-only behavior.
3. TASK-TTS-004D: Style-Bert-VITS2 / GPT-SoVITS feasibility research for
   longer-term Christina/anime voice quality.

TASK-TTS-004A does not add runtime TTS wiring, playback, auto-speaking,
dependencies, generated reports/audio, `/chat` schema changes, mood schema
changes, STT behavior changes, Conversation Mode queue/backpressure changes, or
Owner Voice hard-gate changes.

---

## TASK-TTS-004B VOICEVOX Manual Localhost Probe

TASK-TTS-004B extends `scripts/tts_provider_probe.py` for a manually started
VOICEVOX Engine-compatible local server at `http://127.0.0.1:50021`. The probe
does not install VOICEVOX, does not download models, and does not select
VOICEVOX as the runtime provider.

Default metadata-only command:

```powershell
.\backend\.venv\Scripts\python.exe scripts\tts_provider_probe.py --providers voicevox_server --text "哼，汝總算想起要依靠吾了。這是 VOICEVOX metadata-only probe。" --pretty
```

Optional local WAV output command:

```powershell
.\backend\.venv\Scripts\python.exe scripts\tts_provider_probe.py --providers voicevox_server --text "哼，汝總算想起要依靠吾了。這是 VOICEVOX optional audio probe。" --voicevox-speaker 0 --allow-audio-output --pretty
```

Longer timeout/retry command after TASK-TTS-004B2:

```powershell
.\backend\.venv\Scripts\python.exe scripts\tts_provider_probe.py --providers voicevox_server --text "哼，汝總算想起要依靠吾了。這是 VOICEVOX optional audio retry probe。" --voicevox-speaker 0 --voicevox-timeout-sec 30 --voicevox-retries 1 --allow-audio-output --pretty
```

VOICEVOX probe behavior:

- Only localhost URLs are allowed by `--voicevox-url`; non-localhost URLs are
  rejected before network access.
- Without `--allow-audio-output`, the probe checks `/version` and optionally
  `/speakers` only. It does not call `audio_query`, does not call `synthesis`,
  does not write audio, and never plays audio.
- With `--allow-audio-output`, the probe calls `audio_query` and `synthesis`,
  then writes a WAV under ignored `outputs/tts_provider_probe/YYYYMMDD/audio/`.
- `/speakers` is best effort. Reports include speaker count in notes and the
  selected speaker name when it can be resolved.
- Reports include `voicevoxUrl`, `version`, `speakerId`, `speakerName`,
  `normalizedChunks`, `measuredLatencyMs`, `audioGenerated`, `outputPath`,
  `audioBytes`, and `synthesisStatus`.
- TASK-TTS-004B2 adds `voicevoxStage`, `versionLatencyMs`,
  `speakersLatencyMs`, `audioQueryLatencyMs`, `synthesisLatencyMs`,
  `timeoutSec`, `retryCount`, `lastExceptionClass`, and
  `lastExceptionMessage`.

Manual Windows result before TASK-TTS-004B2 hardening:

- `Invoke-RestMethod http://127.0.0.1:50021/version` returned `0.25.2`.
- Metadata-only probe passed: `available=true`,
  `reason=local_server_metadata_ok`, `version="0.25.2"`, `speakerId=0`,
  `speakerName=ずんだもん / ノーマル`, speaker count `43`,
  `synthesisStatus=audio_output_disabled`, and `audioGenerated=false`.
- Optional audio probe with `--allow-audio-output` reached the local server but
  failed before quality evaluation: `reason=voicevox_error:TimeoutError`,
  `synthesisStatus=voicevox_error`, `measuredLatencyMs=890`,
  `audioGenerated=false`, and `outputPath=null`.
- Interpretation: VOICEVOX Engine was running and metadata/speaker discovery
  worked, but first synthesis/model-load latency exceeded the previous short
  timeout.

Manual Windows retry after TASK-TTS-004B2 hardening:

- Optional audio probe with `--voicevox-timeout-sec 30 --voicevox-retries 1`
  reached `reason=voicevox_success`.
- `audioGenerated=true`, `audioBytes=291372`, `voicevoxStage=complete`,
  `audioQueryLatencyMs=30`, `synthesisLatencyMs=1568`, and `retryCount=0`.
- The generated WAV stayed under ignored
  `outputs/tts_provider_probe/YYYYMMDD/audio/`.
- Pronunciation/character quality is still not judged by the probe and requires
  manual listening.

Manual listening verdict:

| Field | Result |
|---|---|
| Provider | VOICEVOX |
| Voice | 四国めたん / あまあま |
| Version | `0.25.2` |
| Synthesis latency | `1568ms` |
| Audio output | Success |
| Japanese/anime style | Good |
| Chinese pronunciation | Failed; Chinese text was spoken as Japanese / Japanese-like pronunciation |
| Speed | Okay |
| Tone | Good |
| Strange pauses | None |
| Overall acceptability | `7/10` |
| Runtime recommendation | Not selected for Chinese main path |
| Retained use | Japanese-style experimental/fallback candidate |

Provider decision:

- VOICEVOX is technically usable as a local server provider.
- VOICEVOX can produce WAV with acceptable latency after timeout hardening.
- VOICEVOX has good Japanese/anime-style character.
- VOICEVOX is not selected as the main Chinese TTS runtime provider because
  Chinese text is not pronounced as understandable Chinese.
- Keep VOICEVOX as an optional Japanese-style or Japanese-utterance experiment
  path.
- Next provider path should be TASK-TTS-004C edge-tts optional network
  candidate for Chinese voice validation, or TASK-TTS-004D Style-Bert-VITS2 /
  GPT-SoVITS feasibility for long-term character voice.

Evaluation notes:

- Chinese pronunciation and mixed Chinese/Japanese delivery must be judged by
  listening to the locally generated WAV; the probe cannot score quality.
- VOICEVOX remains promising for Japanese/anime-style speech but risky for
  native Chinese support.
- A successful WAV generation proves only local server connectivity and file
  output. It does not approve runtime app playback.
- Audio quality has now been manually judged for this VOICEVOX sample: style and
  tone are good, but Chinese pronunciation fails the main runtime requirement.
- No runtime TTS wiring, `/chat` integration, Pet Window playback,
  auto-speaking, dependency install, ElevenLabs integration, STT behavior
  change, Conversation Mode queue change, Owner Voice gate change, or schema
  change is part of TASK-TTS-004B2.

---

## TASK-TTS-004C Edge-TTS Optional Network Candidate Probe

TASK-TTS-004C extends `scripts/tts_provider_probe.py` for `edge_tts` as an
optional network/cloud-ish Chinese voice validation candidate. It does not
install `edge-tts`, does not make it default, does not select it as runtime, and
does not add app playback.

New CLI options:

- `--edge-tts-voice`, default `zh-TW-HsiaoChenNeural`.
- `--edge-tts-rate`, default `+0%`.
- `--edge-tts-pitch`, default `+0Hz`.
- `--edge-tts-timeout-sec`, default `30`.

Metadata-only command:

```powershell
.\backend\.venv\Scripts\python.exe scripts\tts_provider_probe.py --providers edge_tts --text "哼，汝總算想起要依靠吾了。這是 Edge TTS 中文驗證 metadata-only probe。" --pretty
```

Optional MP3 output command, only after explicitly choosing to install/use
`edge-tts`:

```powershell
.\backend\.venv\Scripts\python.exe scripts\tts_provider_probe.py --providers edge_tts --text "哼，汝總算想起要依靠吾了。這是 Edge TTS 中文語音輸出驗證。" --edge-tts-voice zh-TW-HsiaoChenNeural --allow-audio-output --pretty
```

Probe behavior:

- If the package is missing, `edge_tts` reports `available=false`,
  `reason=missing_optional_dependency`, and `synthesisStatus=missing_optional_dependency`.
- If the package is installed, metadata-only mode reports availability without
  synthesis with `synthesisStatus=metadata_only`. It does not send text to
  Microsoft Edge TTS service, write audio, or play audio.
- If `--allow-audio-output` is explicitly passed, the probe may send text to
  Microsoft Edge TTS service and writes an MP3 under ignored
  `outputs/tts_provider_probe/YYYYMMDD/audio/`.
- Timeout and provider failures are classified as `edge_tts_timeout` and
  `edge_tts_error`.

Manual metadata-only result on this machine:

- `available=false`
- `reason=missing_optional_dependency`
- `synthesisStatus=missing_optional_dependency`
- `audioGenerated=false`
- No dependency was installed.
- No optional audio output was run.

Listening verdict placeholder:

| Field | Result |
|---|---|
| Provider | edge-tts |
| Voice | `zh-TW-HsiaoChenNeural` by default |
| Audio output | Pending explicit install/use and `--allow-audio-output` |
| Chinese pronunciation | Pending manual listening |
| Christina fit | Pending manual listening |
| Runtime recommendation | Not selected; probe-only candidate |

Provider decision:

- `edge_tts` remains a fast Chinese validation candidate only.
- It is not local/offline and must not become the default provider.
- It is not selected as runtime by TASK-TTS-004C.
- Runtime playback should still wait for explicit provider validation and a
  separate runtime task.

No runtime TTS wiring, `/chat` integration, Pet Window playback,
auto-speaking, dependency install, ElevenLabs integration, generated
audio/report commit, STT behavior change, Conversation Mode queue change, Owner
Voice gate change, or schema change is part of TASK-TTS-004C.

---

## TASK-TTS-004C2 Edge-TTS Manual Dependency / Audio Probe

TASK-TTS-004C2 records the explicitly approved manual dependency and audio probe
for `edge_tts`. This does not make `edge_tts` default, does not add it to app
runtime wiring, and does not add playback.

Manual dependency install:

```powershell
.\backend\.venv\Scripts\python.exe -m pip install edge-tts
```

Result:

- `edge-tts==7.2.8` installed into `backend\.venv` only.
- No locked/default runtime dependency was changed.
- No generated audio or reports are committed.

Manual probe result:

| Field | Metadata-only | Optional audio |
|---|---|---|
| Provider | `edge_tts` | `edge_tts` |
| Voice | `zh-TW-HsiaoChenNeural` | `zh-TW-HsiaoChenNeural` |
| Available | `true` | `true` |
| Reason | `optional_dependency_present` | `edge_tts_success` |
| Synthesis status | `metadata_only` | `edge_tts_success` |
| Audio generated | `false` | `true` |
| Audio bytes | `null` | `30240` |
| Synthesis latency | `null` | `1613ms` |
| Output | `null` | `outputs/tts_provider_probe/20260618/audio/edge_tts_20260618-193335.mp3` |

Listening verdict:

| Field | Result |
|---|---|
| 中文是否能聽懂 | Pending manual listening |
| 是否像日系角色 | Pending manual listening |
| 是否適合克莉絲蒂娜 | Pending manual listening |
| 語速 | Pending manual listening |
| 音色 | Pending manual listening |
| 有沒有奇怪斷句 | Pending manual listening |
| 整體可接受度 1-10 | Pending manual listening |
| 是否可作為臨時中文 provider | Pending manual listening |
| 是否可作為長期 provider | Pending manual listening |

Provider decision:

- `edge_tts` is technically usable by the standalone probe after optional
  dependency installation.
- `edge_tts` remains network/cloud-ish and is not local/offline.
- `edge_tts` is not selected as the default runtime provider.
- Chinese voice suitability and Christina fit remain unresolved until manual
  listening is recorded.

---

## 5. Local Candidate Notes

The following are candidate directions for future manual experiments. TASK-TTS-001
does not install, download, benchmark, or endorse any of them as final.

| Candidate | Why it is interesting | Main risks |
|---|---|---|
| ChatTTS-style local lab | Quick local experimentation and expressive speech tests. | Voice consistency, Chinese quality, packaging, and licensing need validation. |
| GPT-SoVITS-style workflow | Strong custom voice/style research direction. | Requires careful data preparation, consent, training/inference complexity. |
| F5-TTS-style workflow | Useful zero-shot/style research candidate. | Quality, latency, Windows setup, and license need a spike. |
| CosyVoice-style workflow | Multilingual/style-control research candidate. | Runtime footprint, packaging, and voice fit need validation. |
| Piper/Sherpa/OS TTS category | Lightweight offline fallback direction. | Anime-style Christina fit may be weak; Chinese voice availability varies. |

Japanese/anime-style and Chinese speech may be in tension. Provider experiments
should explicitly test both:

1. Chinese lines in Christina style.
2. Short Japanese/anime-flavored interjections if a provider supports them.
3. Mixed Chinese terms with project names such as Dragon Pet AI, CodeX, TASK,
   STT, and Conversation Mode.

---

## 6. Provider Experiment Boundary

Future provider spikes should be local-first and isolated:

- Use a small fixed text corpus.
- Keep generated audio under ignored local output folders only.
- Never commit generated audio.
- Never commit voice samples.
- Never commit model checkpoints.
- Never commit embeddings or voiceprints.
- Never use raw user recordings without explicit task scope.
- Never change `/chat`, mood schema, STT default, STT selector, Conversation
  Mode queue/backpressure, or Owner Voice hard-gate behavior.
- Keep provider install/model download steps manual and clearly marked.
- Record latency and errors with redacted paths.

Recommended experiment corpus:

- Short proud Christina line in Traditional Chinese.
- Supportive/debug line in Traditional Chinese.
- Long technical reply excerpt that should be chunked.
- Markdown/code-heavy reply that should be normalized before speech.
- Mixed project terms: `Dragon Pet AI`, `CodeX`, `TASK-TTS-001`,
  `Conversation Mode`, `STT`.

---

## 7. Voice Data and Licensing

Any custom or cloned voice work requires a separate consent/licensing task before
implementation.

Rules:

- Do not use copyrighted character voice samples without rights.
- Do not use private voice samples without explicit consent.
- Do not commit source voice samples.
- Do not commit trained checkpoints.
- Do not commit embeddings or voiceprints.
- Generated comparison clips remain local artifacts unless a future task
  explicitly defines safe export rules.

Christina voice direction should be treated as an original project voice style,
not an imitation of a specific real actor.

---

## 8. Singing Research Boundary

Singing is future research only.

Do not include singing in TASK-TTS-002 through TASK-TTS-006 unless the task is
explicitly widened. Singing likely needs a separate pipeline, licensing review,
timing/melody controls, and different evaluation criteria from spoken replies.

Future candidate:

- TASK-TTS-FUTURE-SINGING-001: singing feasibility and safety research.

---

## 9. Recommended Next Provider Path

Recommended sequencing:

1. TASK-TTS-002: mock provider skeleton and provider contract. DONE -
   metadata-only backend skeleton; not a voice-quality provider.
2. TASK-TTS-003: local provider candidate probe. DONE - metadata-only script;
   no runtime wiring and no provider selected.
3. TASK-TTS-004A: install-free provider review. DONE - no real provider ready;
   `mock` remains the only safe skeleton provider.
4. TASK-TTS-004B: VOICEVOX local server manual probe / optional audio output.
   DONE - manual localhost metadata probe ready; optional WAV generation is
   guarded by `--allow-audio-output` and remains local-only.
5. TASK-TTS-004B2: VOICEVOX synthesis timeout / retry hardening and listening
   verdict. DONE - audio output works, but not selected for Chinese runtime.
6. TASK-TTS-004C: edge-tts optional network candidate probe. IMPLEMENTED -
   metadata-only safe probe ready; Chinese audio validation pending explicit
   install/use and manual listening.
7. TASK-TTS-004C2: edge-tts manual dependency/audio output probe. DONE - MP3
   output works; manual listening pending.
8. TASK-TTS-004D: Style-Bert-VITS2 / GPT-SoVITS feasibility research.
9. TASK-TTS-004: renderer playback queue diagnostics after a real provider
   candidate is validated.
10. TASK-TTS-005: Pet speaking state and bubble sync.
11. TASK-TTS-006: Conversation Mode feedback prevention.
12. Future: provider comparison report and singing research.

Do not start by wiring ElevenLabs. Do not hard-code ChatTTS, GPT-SoVITS, F5-TTS,
or CosyVoice into the product path before a provider abstraction and mock tests
exist.

---

## 10. Research Acceptance

TASK-TTS-001 provider research is complete when:

- Provider categories are documented.
- Candidate local directions are listed with risks.
- Evaluation criteria are documented.
- Voice-data and generated-audio boundaries are documented.
- Future phased tasks are clear.
- No provider is selected as final.
- No runtime provider integration, package dependency, generated audio, voice
  sample, model, embedding, local setting, log, or report is committed.
