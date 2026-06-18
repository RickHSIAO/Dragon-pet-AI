# TTS Provider Research

**Task:** TASK-TTS-001 / TASK-TTS-003
**Status:** TASK-TTS-003 IMPLEMENTED - LOCAL TTS PROVIDER PROBE SMOKE PASS / NO RUNTIME WIRING
**Date:** 2026-06-18
**Scope:** Provider research, implemented mock-provider skeleton boundary, and
TASK-TTS-003 local provider candidate probe. No real voice-quality provider is
selected as final, no model is downloaded, no dependency is added, and no real
synthesis/playback path is implemented by TASK-TTS-003.

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
| `edge_tts` | Network/cloud-ish | Usually has Chinese voices | Depends on service voices | Low package setup, but network required | High for privacy/default policy | Optional dependency check only; not default |
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
3. TASK-TTS-004: renderer playback queue diagnostics with mock/provider output.
4. TASK-TTS-005: Pet speaking state and bubble sync.
5. TASK-TTS-006: Conversation Mode feedback prevention.
6. Future: provider comparison report and singing research.

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
