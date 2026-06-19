# TTS Provider Research

**Task:** TASK-TTS-001 / TASK-TTS-004E4
**Status:** TASK-TTS-004E4 DONE - GPT-SOVITS DEPENDENCY COMPATIBILITY REVIEW COMPLETE / DEPENDENCY INSTALL NOT APPROVED
**Date:** 2026-06-19
**Scope:** Provider research, implemented mock-provider skeleton boundary,
TASK-TTS-004A install-free provider review, TASK-TTS-004B manual VOICEVOX
localhost probe, TASK-TTS-004B2 timeout/retry hardening, TASK-TTS-004C
edge-tts optional network candidate probe, and TASK-TTS-004C2 manual
edge-tts dependency/audio output validation, TASK-TTS-004C3 docs-first
edge-tts tuning workflow, TASK-TTS-004D character voice feasibility research,
TASK-TTS-004D2 environment check workflow, TASK-TTS-004D3 isolated lab
plan, TASK-TTS-004D4 manual bootstrap checklist, TASK-TTS-004E provider
selection checkpoint, TASK-TTS-004E2 blocked Phase 1 bootstrap attempt, and
TASK-TTS-004E2A blocked isolated Miniconda bootstrap attempt, and
TASK-TTS-004E2A2 Miniconda failure diagnostics, and TASK-TTS-004E2A3 UTF-8
retry, TASK-TTS-004E2B existing-Anaconda Phase 1 resume, TASK-TTS-004E3
PyTorch/CUDA compatibility review, TASK-TTS-004E3A lab-only PyTorch/CUDA
install verification, and TASK-TTS-004E4 dependency compatibility review.
GPT-SoVITS is selected as the first isolated lab candidate; TASK-TTS-004E4
reviewed a staged dependency plan and did not install GPT-SoVITS dependencies.
Style-Bert-VITS2 is the second
provider / fallback research path, no real voice-quality provider is selected
as final, no model is
downloaded, the `edge-tts` install is optional/manual inside `backend\.venv`
only, and no runtime synthesis/playback path is implemented by TASK-TTS-004C2,
TASK-TTS-004C3, TASK-TTS-004D, TASK-TTS-004D2, TASK-TTS-004D3,
TASK-TTS-004E2A, TASK-TTS-004E2A2, TASK-TTS-004E2A3, TASK-TTS-004E2B,
TASK-TTS-004E3, TASK-TTS-004E3A, or TASK-TTS-004E4.

This document records candidate directions for Christina voice output. It should
guide later experiments, not lock Dragon Pet AI to a single TTS engine.

---

## 1. User Preference Summary

TASK-TTS-004E4 dependency review summary:

- Reviewed `requirements.txt`, `extra-req.txt`, install scripts, Docker files,
  README install notes, launchers, and BigVGAN requirements without installing
  anything.
- Direct full requirements and official install scripts remain rejected for the
  next step because they can replace torch/torchaudio, force native builds,
  install system tools, or download models.
- Recommended first future group is Group A Safe Foundation:
  `numpy==1.26.4`, `scipy==1.11.4`, `tqdm`, `PyYAML`, `chardet`, and `psutil`.
- Future install must protect `torch==2.7.0+cu128` and
  `torchaudio==2.7.0+cu128` with lab-local constraints and verify CUDA after
  each group.
- TorchCodec, full GPT-SoVITS dependencies, ffmpeg/system codec setup, model
  downloads, inference, WebUI, audio generation, runtime playback, and
  auto-speaking remain unapproved.

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

Historical listening placeholder from the audio-probe commit:

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

Listening verdict:

| Field | Result |
|---|---|
| Provider | edge-tts |
| Voice | `zh-TW-HsiaoChenNeural` |
| Synthesis latency | `1613ms` |
| Audio output | Success |
| Chinese intelligibility | Good |
| Anime/Christina suitability | Weak |
| Speed | Slightly fast |
| Tone | Okay |
| Strange pauses | None |
| Overall acceptability | `6/10` |
| Runtime recommendation | Temporary Chinese provider only; not final |
| Retained use | Optional preview/debug/fallback candidate |

Provider decision:

- `edge_tts` is technically usable by the standalone probe after optional
  dependency installation.
- `edge_tts` remains network/cloud-ish and is not local/offline.
- `edge_tts` is technically usable for Chinese output and acceptable as a
  temporary Chinese provider candidate.
- `edge_tts` is not selected as the final Christina long-term voice because
  character/anime fit is weak and the voice feels more general/Taiwanese than
  Christina-like.
- `edge_tts` remains optional for network/cloud-ish preview, debug, or fallback
  experiments.
- `edge_tts` is not selected as the default runtime provider, and no runtime
  wiring should start from TASK-TTS-004C2.
- Next provider path: TASK-TTS-004C3 edge-tts voice/rate tuning probe if slower
  rate or alternate Mandarin voices should be checked; otherwise TASK-TTS-004D
  Style-Bert-VITS2 / GPT-SoVITS feasibility research for long-term Christina
  character voice.

---

## TASK-TTS-004C3 Edge-TTS Voice / Rate Tuning Probe

TASK-TTS-004C3 defines and closes a docs-first edge-tts tuning workflow. No
script change is required because the existing standalone probe already
supports `--edge-tts-voice`, `--edge-tts-rate`, and `--edge-tts-pitch`. Each
candidate is run as a separate explicit command, and manual listening decides
whether it is better than the TASK-TTS-004C2 baseline.

Baseline from TASK-TTS-004C2:

| Voice | Rate | Pitch | Result |
|---|---:|---:|---|
| `zh-TW-HsiaoChenNeural` | `+0%` | `+0Hz` | Understandable Chinese, slightly fast, weak Christina/anime fit, more general/Taiwanese than Christina-like, `6/10` |

Tuning matrix:

| Candidate | Voice | Rate | Pitch | Generated file path | Chinese intelligibility | Christina fit | Speed | Tone | Overall score |
|---|---|---:|---:|---|---|---|---|---|---|
| Baseline | `zh-TW-HsiaoChenNeural` | `+0%` | `+0Hz` | `outputs/tts_provider_probe/20260618/audio/edge_tts_20260618-193335.mp3` | Good | Weak | Slightly fast | Okay | `6/10` |
| Slow Chen 10 | `zh-TW-HsiaoChenNeural` | `-10%` | `+0Hz` | Local ignored probe output | Good | Improved but still not enough; lacks Christina/character feel | Better than baseline | Okay | Not selected |
| Slow Chen 15 | `zh-TW-HsiaoChenNeural` | `-15%` | `+0Hz` | Pending manual run | Pending | Pending | Pending | Pending | Pending |
| HsiaoYu baseline | `zh-TW-HsiaoYuNeural` | `+0%` | `+0Hz` | Pending manual run | Pending | Pending | Pending | Pending | Pending |
| HsiaoYu slow 10 | `zh-TW-HsiaoYuNeural` | `-10%` | `+0Hz` | Local ignored probe output | Not selected | Not suitable; too old | Not selected | Too old | Not suitable |
| HsiaoYu slow 15 | `zh-TW-HsiaoYuNeural` | `-15%` | `+0Hz` | Pending manual run | Pending | Pending | Pending | Pending | Pending |
| Xiaoxiao baseline | `zh-CN-XiaoxiaoNeural` | `+0%` | `+0Hz` | Pending manual run | Pending | Pending | Pending | Pending | Pending |
| Xiaoxiao slow 10 | `zh-CN-XiaoxiaoNeural` | `-10%` | `+0Hz` | Local ignored probe output | Not selected | Not suitable; too mainland-China-like for preference | Not selected | Not selected | Not suitable |
| Optional pitch check | Best candidate voice after rate check | Best candidate rate | `+2Hz` or `+5Hz` | Pending only if cleanly supported | Pending | Pending | Pending | Pending | Pending |

Manual command pattern:

```powershell
.\backend\.venv\Scripts\python.exe scripts\tts_provider_probe.py --providers edge_tts --text "克莉絲蒂娜，這是 Edge TTS 中文語音調音測試。" --edge-tts-voice zh-TW-HsiaoChenNeural --edge-tts-rate -10% --edge-tts-pitch +0Hz --allow-audio-output --pretty
```

Manual tuning verdict:

- `zh-TW-HsiaoChenNeural -10%`: somewhat better than baseline, but still lacks
  the right Christina/character feel and is not enough to select as provider.
- `zh-TW-HsiaoYuNeural -10%`: not suitable; sounds too old.
- `zh-CN-XiaoxiaoNeural -10%`: not suitable; sounds too mainland-China-like for
  the user's preference.
- No edge-tts voice reached desired Christina fit.

Provider decision:

- edge-tts remains usable only as a temporary Chinese provider, debug preview,
  or fallback candidate.
- edge-tts is not selected as final Christina voice or runtime provider.
- Do not wire edge-tts into runtime yet.
- Stop further edge-tts tuning for now unless explicitly revisited.
- Recommended next path: TASK-TTS-004D Style-Bert-VITS2 / GPT-SoVITS
  feasibility research for long-term character voice paths with better
  anime-style Christina fit while preserving Chinese usability.
- Runtime TTS remains disabled/mock-only; no `/chat` integration, playback,
  Pet Window playback, or auto-speaking is added by TASK-TTS-004C3.

---

## TASK-TTS-004D Character Voice Feasibility Research

TASK-TTS-004D closes the docs-only feasibility pass for longer-term Christina
character voice candidates. It does not install models, download model weights,
run training/inference, generate audio, add runtime dependencies, or select a
final provider.

Detailed report:

- `docs/TTS_CHARACTER_VOICE_FEASIBILITY.md`

Feasibility comparison:

| Option | Chinese support | Anime/character suitability | Windows setup | GPU/VRAM | Training/data requirement | License risk | Runtime integration risk | Recommended next action |
|---|---|---|---|---|---|---|---|---|
| GPT-SoVITS | Promising; official docs list Chinese and cross-lingual support, but Traditional Chinese pronunciation and mixed project terms need a local probe. | Strong long-term Christina candidate because it supports zero/few-shot and fine-tuned TTS workflows. | High; Windows package and PowerShell/Conda paths exist but should live in a separate lab environment. | Medium/high for quality and training; CPU path exists but latency must be measured. | Requires legally usable source voice/style data and careful text labeling. | Medium; code license is MIT, but voice data and pretrained model terms still need review. | High; heavy model lifecycle, sidecar/API, cancellation, timeout, and output cleanup need explicit design. | First long-term research candidate for TASK-TTS-004D2/004E. |
| Style-Bert-VITS2 | Unresolved for Chinese main runtime; appears more Japanese-oriented and must prove Chinese quality. | Strong anime/style-control candidate. | High but Windows-friendly; official docs describe Windows scripts, library use, and an API server. | Training requires NVIDIA GPU; synthesis can run on CPU according to official docs, but latency is unknown. | Needs legally usable voice/style data for a Christina-like voice. | High; AGPL/LGPL project licensing and model/voice terms need review before app integration. | High; separate service/process, style controls, model downloads, and license boundaries must be isolated. | Evaluate after or alongside GPT-SoVITS environment check. |
| edge-tts | Proven understandable Chinese; baseline `zh-TW-HsiaoChenNeural` was `6/10`. | Weak Christina/anime fit; tuning found no suitable voice. | Low package setup, but network/cloud-ish. | None local. | No training. | Medium/high privacy/default risk because optional audio sends text to Microsoft Edge TTS service. | Medium/high; should not become silent default. | Keep temporary/debug/fallback only. |
| VOICEVOX | Not suitable for main Chinese runtime; Chinese text was spoken with Japanese/Japanese-like pronunciation. | Good Japanese/anime-style tone. | Medium; manually started localhost engine. | Depends on VOICEVOX runtime. | Existing voices only in current path. | Medium; speaker terms require review. | Medium; local HTTP path is manageable, but Chinese failure blocks runtime selection. | Keep Japanese-style/Japanese utterance experiment only. |
| RVC-like conversion | Depends on source TTS; not a TTS provider by itself. | Possible future voice-color layer. | High; separate WebUI, PyTorch, ffmpeg, and pretrained model setup. | Medium/high for training quality. | Requires target voice data, source TTS, and conversion training. | High; consent/licensing and identity misuse risk. | Very high as a first runtime due to two-stage pipeline. | Defer until a source provider is selected. |

TASK-TTS-004D recommendation:

1. Do not automatically pick a final provider.
2. Put GPT-SoVITS first for the next manual environment/probe check.
3. Keep Style-Bert-VITS2 as a parallel long-term anime/style-control research
   candidate.
4. Keep edge-tts temporary/debug/fallback only.
5. Keep VOICEVOX Japanese-style experiment only.
6. Defer RVC-like conversion until a source TTS provider exists.
7. Do not start TASK-TTS-005 runtime playback until a standalone provider probe
   passes manual listening and license/data review.

Recommended next tasks:

1. TASK-TTS-004E - Character Voice Lab Provider Selection / First Probe Approval.
2. TASK-TTS-004E2 - GPT-SoVITS isolated lab Phase 1 retry, only after Conda is
   available or a different isolated environment tool is explicitly approved.
3. TASK-TTS-005 - TTS Runtime Playback Queue, only after provider decision.

No runtime TTS wiring, `/chat` integration, playback, Pet Window playback,
auto-speaking, dependency/default-runtime change, generated audio/report/model
commit, STT behavior change, Conversation Mode queue change, Owner Voice gate
change, or schema change is part of TASK-TTS-004D.

TASK-TTS-004E provider-selection update:

| Provider | TASK-TTS-004E role | Runtime status |
|---|---|---|
| GPT-SoVITS | First isolated lab candidate for later approved first probe. | Lab candidate only; not selected as runtime. |
| Style-Bert-VITS2 | Second provider / fallback research path. | Lab research path only; not selected as runtime. |
| edge-tts | Temporary Chinese/debug/fallback only. | Not default and not selected as runtime. |
| VOICEVOX | Japanese-style/Japanese utterance experiment only. | Not selected for Chinese runtime. |
| RVC-like | Deferred until a source TTS provider exists. | Not a first TTS runtime. |

The first real GPT-SoVITS setup remains unapproved until lab path, provider,
Python version, Conda vs venv, external clone, package install, PyTorch/CUDA
install, model download, test audio generation, and artifact storage policy are
explicitly approved.

---

## TASK-TTS-004D2 Character Voice Environment Check

TASK-TTS-004D2 adds `scripts/tts_character_voice_env_check.py` as an
environment-check-only workflow before any GPT-SoVITS or Style-Bert-VITS2
install/probe attempt.

The checker collects existing local evidence only:

- OS/platform and architecture.
- Python executable, version, and venv detection.
- Git availability/version.
- Repo drive disk space.
- `nvidia-smi` GPU, VRAM, driver, and CUDA evidence when available.
- PyTorch version, CUDA availability, and GPU device evidence only if already
  installed.
- Node/npm versions.
- Optional localhost-only VOICEVOX metadata reachability.
- Optional `edge_tts` package availability.
- Deterministic feasibility verdict.

Reports are JSON/Markdown local artifacts under ignored
`outputs/tts_character_voice_env_check/YYYYMMDD/` and must not be committed.

TASK-TTS-004D2 does not install packages, download models, clone repos, train or
run models, synthesize audio, wire TTS into runtime, add playback, or select a
provider. Its output only informs whether TASK-TTS-004E should plan a CPU probe,
GPU probe, or docs-only follow-up.

---

## TASK-TTS-004D3 Isolated Character Voice Lab Plan

TASK-TTS-004D3 adds `docs/TTS_CHARACTER_VOICE_LAB_PLAN.md` as the boundary for
future GPT-SoVITS / Style-Bert-VITS2 experiments.

Provider research rule:

- Do not install GPT-SoVITS, Style-Bert-VITS2, CUDA PyTorch, model weights, or
  lab helper tools into `backend\.venv`.
- External provider repos should live outside Dragon Pet AI app code, preferably
  under `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\`.
- Models, voice samples, generated audio, checkpoints, embeddings, logs, and
  local settings stay in the lab only.
- The first acceptable provider evidence is standalone WAV/MP3 plus a manual
  listening verdict, not runtime integration.
- Runtime provider selection remains blocked until licensing/data review,
  Chinese intelligibility, Christina fit, latency, and failure behavior are
  documented.

TASK-TTS-004D3 does not create the lab, clone repos, install packages, download
models, train, infer, synthesize audio, or wire runtime TTS.

---

## TASK-TTS-004D4 Character Voice Lab Bootstrap Checklist

TASK-TTS-004D4 adds `docs/TTS_CHARACTER_VOICE_LAB_BOOTSTRAP_CHECKLIST.md`.

Provider research rule:

- GPT-SoVITS and Style-Bert-VITS2 work must pass the bootstrap gate before any
  real setup.
- The gate requires explicit approval for lab path, provider, Python version,
  environment tool, GPU/CUDA install, model downloads, inference, generated
  audio, and artifact cleanup policy.
- Manual commands for future folder creation, Conda env creation, `nvidia-smi`,
  Python version checks, and PyTorch CUDA checks are documented but not run.
- Clone targets remain lab-only:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS\` and
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\Style-Bert-VITS2\`.
- Generated audio, model weights, source samples, reports, embeddings, logs,
  and local settings remain lab artifacts and must not be committed.

TASK-TTS-004D4 does not create the lab, clone repos, install packages, download
models, train, infer, synthesize audio, or wire runtime TTS.

---

## TASK-TTS-004E Character Voice Provider Selection

TASK-TTS-004E adds `docs/TTS_CHARACTER_VOICE_PROVIDER_SELECTION.md`.

Provider decision:

- First isolated lab candidate: GPT-SoVITS.
- Second provider / fallback research path: Style-Bert-VITS2.
- Final runtime provider: not selected.
- RVC-like conversion: deferred.
- edge-tts: temporary Chinese/debug/fallback only.
- VOICEVOX: Japanese-style experiment only.

First probe approval gate:

- Exact lab path.
- Exact provider.
- Exact Python version.
- Conda vs venv.
- External repo clone permission.
- Package install permission.
- PyTorch/CUDA install permission.
- Model download permission.
- Test audio generation permission.
- Artifact storage and cleanup policy.

First probe success requires lab-only setup, CUDA/PyTorch verification if GPU
path is chosen, no main app runtime changes, a short standalone Chinese sample,
uncommitted generated audio, and manual listening for Chinese intelligibility,
Christina fit, anime/character feel, latency, and stability.

TASK-TTS-004E does not create the lab, clone repos, install packages, download
models, train, infer, synthesize audio, or wire runtime TTS.

---

## TASK-TTS-004E2 GPT-SoVITS Isolated Lab Bootstrap Phase 1

TASK-TTS-004E2 adds `docs/TTS_GPT_SOVITS_LAB_PHASE1.md`.

Phase 1 approved scope:

- Create the external lab root.
- Clone official `https://github.com/RVC-Boss/GPT-SoVITS.git`.
- Create isolated Conda Python 3.10 environment.

Actual result:

- BLOCKED - CONDA NOT AVAILABLE / NO INSTALL PERFORMED.
- `conda --version`, `conda info --base`, and `conda env list` failed because
  `conda` is not recognized in PowerShell.
- No lab root was created.
- No GPT-SoVITS repository was cloned.
- No Conda env was created.
- No external Phase 1 manifest was written.
- No dependency, PyTorch/CUDA package, model, dataset, training, inference,
  WebUI, synthesis, generated audio, app runtime wiring, playback, or
  auto-speaking was added.
- Hardware evidence only: NVIDIA GeForce RTX 3070, 8192 MiB VRAM,
  NVIDIA-SMI/driver evidence `610.47`, CUDA compatibility `13.3`.

---

## TASK-TTS-004E2A Isolated Miniconda Bootstrap

TASK-TTS-004E2A adds `docs/TTS_MINICONDA_LAB_BOOTSTRAP.md`.

Actual result:

- BLOCKED - ISOLATED MINICONDA INSTALL FAILED.
- Official installer download succeeded.
- Downloaded SHA-256 matched the official SHA-256.
- Silent install returned exit code `2` and rolled back.
- Required direct Conda/Python files are missing.
- PATH inspection found no user, machine, or process PATH pollution.
- `conda init` was not run and the PowerShell profile was not modified.
- No GPT-SoVITS/Style-Bert repo, Conda env, dependency, PyTorch/CUDA package,
  model, dataset, training, inference, WebUI, synthesis, generated audio,
  runtime wiring, playback, or auto-speaking was added.
- External manifest:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2A_MINICONDA_BOOTSTRAP.md`.

---

## TASK-TTS-004E2A2 Miniconda Install Failure Diagnostics

TASK-TTS-004E2A2 adds `docs/TTS_MINICONDA_INSTALL_DIAGNOSTICS.md`.

Actual result:

- BLOCKED - MINICONDA INSTALL ROOT CAUSE NOT IDENTIFIED / NO RETRY PERFORMED.
- No installer retry, GUI install, cleanup, uninstall, alternate Conda tool,
  Conda env, `conda init`, PATH/profile modification, provider clone, package
  install, model download, inference, synthesis, generated audio, runtime
  wiring, playback, or backend venv change was performed.
- Installer metadata: `Miniconda3 py313_26.3.2-2 (64-bit)`.
- Installer SHA-256 remained
  `fe980247dfd30af229a55d9505b57e7c8dfbdb9d24c5bc66fb6078b6a2d53414`.
- Authenticode signature was valid and signed by `Anaconda, Inc.`.
- Partial install still lacks `condabin\conda.bat`, `Scripts\conda.exe`,
  `python.exe`, and `Uninstall-Miniconda3.exe`.
- Direct failure evidence is `.step.log` rollback after a `cp950`
  `UnicodeDecodeError` while reading existing Conda-related paths.
- Read-only registry inspection found existing machine-wide Anaconda state, but
  exact upstream root cause remains unproven.
- Application and Defender event log checks found no relevant Error/Warning
  over the install window.
- External diagnostics manifest:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2A2_MINICONDA_INSTALL_DIAGNOSTICS.md`.

---

## TASK-TTS-004E2A3 Miniconda UTF-8 Retry

TASK-TTS-004E2A3 adds `docs/TTS_MINICONDA_UTF8_RETRY.md`.

Actual result:

- BLOCKED - UTF-8 MINICONDA RETRY FAILED / NO FURTHER RETRY PERFORMED.
- Deleted only the approved failed partial install root after exact path
  verification.
- Preserved the official installer, SHA-256 evidence, and reports.
- Retried the same verified installer once to the same path with process-local
  `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`, and UTF-8 output encodings.
- Retry still exited `2` and recreated a partial install.
- Required `condabin\conda.bat`, `Scripts\conda.exe`, `python.exe`, and
  `Uninstall-Miniconda3.exe` remain missing.
- `.step.log` still reports rollback after a `cp950` `UnicodeDecodeError`
  while reading existing Conda-related paths.
- No further retry or post-retry cleanup was performed.
- No user/system PATH, `conda init`, PowerShell profile, registry, existing
  Anaconda removal, provider repo, GPT-SoVITS env, dependency/PyTorch/CUDA
  install, model/dataset download, training, inference, WebUI, synthesis,
  generated audio, runtime wiring, playback, or backend venv change was added.
- External retry manifest:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2A3_MINICONDA_UTF8_RETRY.md`.

---

## TASK-TTS-004E2B Existing Anaconda GPT-SoVITS Phase 1 Resume

TASK-TTS-004E2B adds `docs/TTS_EXISTING_ANACONDA_GPT_SOVITS_PHASE1.md`.

Actual result:

- DONE - EXISTING ANACONDA VERIFIED / GPT-SOVITS LAB PHASE 1 READY.
- Existing machine-wide Anaconda root: `C:\ProgramData\anaconda3`.
- Conda version: `25.11.1`.
- Process-local UTF-8 was required for direct env-list validation because the
  default code page still hit the known `cp950` issue.
- Isolated env:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310`.
- Target Python: `3.10.20`.
- PyTorch probe: `None`.
- Official GPT-SoVITS clone:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS`.
- Origin: `https://github.com/RVC-Boss/GPT-SoVITS.git`.
- Branch: `main`.
- Commit: `b2cff0cd0abd0ac134a16ae7a9695f88e8826104`.
- License: `MIT License`.
- No base Anaconda package install/update, PATH/profile/registry change,
  `conda init`, failed Miniconda modification, dependency/PyTorch/CUDA
  install, model/dataset download, training, inference, WebUI, synthesis,
  generated audio, runtime wiring, playback, or backend venv change was added.
- External manifest:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2B_EXISTING_ANACONDA_RESUME.md`.

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
   output works; manual listening accepts it only as a temporary Chinese
   provider candidate, not final Christina voice.
8. TASK-TTS-004C3: edge-tts voice/rate tuning probe if slower rate or alternate
   Mandarin voices should be checked. DONE - no suitable Christina voice found;
   keep edge-tts temporary/debug/fallback only and stop tuning for now.
9. TASK-TTS-004D: Style-Bert-VITS2 / GPT-SoVITS feasibility research. DONE -
   no model installed, no final provider selected; GPT-SoVITS and
   Style-Bert-VITS2 are the leading long-term research candidates.
10. TASK-TTS-004D2: character voice feasibility manual environment check.
   IMPLEMENTED - env checker ready, no install performed.
11. TASK-TTS-004D3: character voice lab environment plan. DONE - isolated lab
   boundary ready, no lab install performed.
12. TASK-TTS-004D4: character voice lab bootstrap checklist. DONE - manual
   commands and human approval gates ready, no setup performed.
13. TASK-TTS-004E: character voice lab provider selection. DONE - GPT-SoVITS
   first, Style-Bert-VITS2 second, first probe not approved yet.
14. TASK-TTS-004E2: GPT-SoVITS isolated lab bootstrap Phase 1. BLOCKED -
   Conda not available, no install performed.
15. TASK-TTS-004E2B: existing Anaconda GPT-SoVITS Phase 1 resume. DONE -
   isolated Python 3.10 env and official repo clone ready.
16. TASK-TTS-004E3: GPT-SoVITS PyTorch/CUDA compatibility review. DONE -
   install plan documented before installation.
17. TASK-TTS-004E3A: GPT-SoVITS lab PyTorch/CUDA install. DONE -
   `torch==2.7.0` and `torchaudio==2.7.0` CUDA `12.8` verified; GPT-SoVITS
   dependencies not installed.
18. TASK-TTS-004E4: GPT-SoVITS dependency compatibility review. DONE -
   staged dependency plan ready; dependency install not approved.
19. TASK-TTS-004E4A: GPT-SoVITS foundation dependency install. NOT APPROVED.
20. TASK-TTS-004: renderer playback queue diagnostics after a real provider
   candidate is validated.
21. TASK-TTS-005: Pet speaking state and bubble sync.
22. TASK-TTS-006: Conversation Mode feedback prevention.
23. Future: provider comparison report and singing research.

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
