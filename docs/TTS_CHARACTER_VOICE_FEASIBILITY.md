# TTS Character Voice Feasibility

**Task:** TASK-TTS-004D / TASK-TTS-004D2 / TASK-TTS-004D3
**Status:** TASK-TTS-004D3 DONE - CHARACTER VOICE LAB PLAN READY / NO LAB INSTALL PERFORMED
**Date:** 2026-06-19
**Scope:** Documentation-only feasibility research for long-term Christina
character voice candidates, environment-check-only readiness inspection, and
isolated lab planning. No model was installed, downloaded, trained, or run.

---

## 1. Decision Summary

TASK-TTS-004D does not select a final provider.

The practical conclusion is:

1. GPT-SoVITS and Style-Bert-VITS2 are the strongest long-term research
   candidates if the project needs both Chinese usability and a more
   Christina-like character voice.
2. edge-tts remains the temporary Chinese provider / debug preview / fallback
   candidate only.
3. VOICEVOX remains useful for Japanese/anime-style experiments, but it is not
   suitable for the main Chinese runtime path.
4. RVC-like conversion may be useful later as a post-processing layer, but it is
   not a first TTS runtime because it needs a source TTS voice first.
5. Runtime TTS remains disabled/mock-only. No playback queue, `/chat` wiring,
   Pet playback, or auto-speaking should start until a real provider passes a
   standalone probe and manual listening review.

Recommended next path:

1. TASK-TTS-004D2 - Character Voice Feasibility Manual Environment Check.
2. TASK-TTS-004E - GPT-SoVITS / Style-Bert-VITS2 Minimal Local Probe Plan.
3. TASK-TTS-005 - TTS Runtime Playback Queue, only after provider decision.

---

## 2. Research Sources

Sources checked for this docs-only feasibility pass:

| Source | What was used |
|---|---|
| https://github.com/RVC-Boss/GPT-SoVITS | Official project README for feature scope, Windows setup shape, license, language support, and model/data workflow. |
| https://github.com/litagin02/Style-Bert-VITS2 | Official project README for style-control focus, Windows setup, CPU synthesis vs GPU training boundary, API server note, and license files. |
| https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI | Official project README for RVC-like voice conversion scope, data requirement, Windows/GPU setup, and pretrained-model requirement. |
| Existing Dragon Pet AI docs | TASK-TTS-004B2 VOICEVOX listening verdict and TASK-TTS-004C2/004C3 edge-tts listening verdicts. |

No installer, model download, training run, inference run, or audio generation was
performed for TASK-TTS-004D.

---

## 3. Feasibility Comparison

| Option | Chinese support | Anime/character suitability | Windows setup | GPU/VRAM | Training/data requirement | License risk | Runtime integration risk | Recommended next action |
|---|---|---|---|---|---|---|---|---|
| GPT-SoVITS | Promising; official README lists Chinese and cross-lingual support. Must verify Traditional Chinese pronunciation and mixed project terms locally. | Strong candidate for custom Christina-like voice because it supports zero/few-shot TTS and fine-tuning workflows. | High. Official Windows path exists through integrated package or Conda/PowerShell install, but it is a separate lab environment. | Medium to high for quality/training; CPU path exists but must be tested for latency. | Requires legally usable voice/style data and careful text labeling. Few-shot is possible but quality still needs listening review. | Medium. Project license is MIT, but source voice data and pretrained model terms still require review. | High. Heavy local service, model lifecycle, queue timeouts, generated files, and privacy boundaries need an isolated adapter. | Prioritize for TASK-TTS-004D2/004E if Chinese + character voice is the main goal. |
| Style-Bert-VITS2 | Unresolved for Chinese main runtime. It is based on Bert-VITS2/Japanese-Extra and appears stronger for Japanese-style expression than Chinese output. | Strong for anime-style and controllable speaking styles; likely valuable for Christina style exploration. | High but Windows-friendly. Official docs describe Windows scripts, pip/library usage for synthesis, and an API server. | Training needs NVIDIA GPU; synthesis can run on CPU according to official docs, but latency must be measured. | Needs legally usable style/voice data for a Christina-like voice; default Japanese-oriented models are not enough for Chinese runtime selection. | High. Repository includes AGPL/LGPL license files and model/voice terms must be checked before app integration. | High. Separate service/process, model downloads, style controls, and license boundaries must be kept outside runtime until proven. | Evaluate as long-term anime-style research candidate, likely after or alongside GPT-SoVITS environment check. |
| edge-tts | Proven understandable Chinese on `zh-TW-HsiaoChenNeural`; baseline `6/10`. | Weak Christina/anime fit. Tuning did not find a suitable Christina voice. | Low after optional package install, but it is network/cloud-ish. | None local. | No project training. | Medium to high privacy/default risk because optional audio sends text to Microsoft Edge TTS service. | Medium to high for policy reasons; should never become silent default. | Keep as temporary Chinese provider / debug preview / fallback candidate only. Stop tuning unless explicitly revisited. |
| VOICEVOX | Not suitable for main Chinese runtime; manual listening found Chinese text was spoken with Japanese/Japanese-like pronunciation. | Good Japanese/anime-style tone. | Medium. Requires manually started localhost engine. | Depends on VOICEVOX engine/runtime. | Uses existing VOICEVOX voices; no Christina-specific training in current path. | Medium. Voice/style terms must be checked per speaker before any runtime use. | Medium. Local HTTP lifecycle is manageable, but Chinese failure blocks main runtime use. | Keep only for Japanese-style / Japanese utterance experiments. |
| RVC-like conversion | Not a TTS provider by itself; Chinese support depends on source TTS and conversion quality. | Potentially useful as a later voice-color layer after a source TTS exists. | High. Official RVC WebUI has Windows paths but also PyTorch, ffmpeg, and pretrained model requirements. | Medium to high; training quality depends on hardware and data. | Requires target voice data, source TTS, and conversion training. Consent/licensing must be explicit. | High for voice data, conversion target identity, and generated voice misuse risk. | Very high as a first runtime because it adds a second model stage and failure surface. | Defer. Do not use as first TTS runtime; reconsider only after a source provider is chosen. |

---

## 4. Why Current Candidates Are Insufficient

VOICEVOX:

- Technically usable as a local server and good for Japanese/anime-style speech.
- Not acceptable for main Chinese conversation because the manual sample did not
  pronounce Chinese as understandable Chinese.
- Retained only for Japanese-style or Japanese utterance experiments.

edge-tts:

- Technically usable for Chinese output and acceptable as a temporary candidate.
- Baseline was understandable but slightly fast and too general/Taiwanese for
  Christina; overall `6/10`.
- Tuning did not solve the character fit problem:
  `zh-TW-HsiaoChenNeural -10%` improved speed but not character fit,
  `zh-TW-HsiaoYuNeural -10%` sounded too old, and
  `zh-CN-XiaoxiaoNeural -10%` sounded too mainland-China-like.
- Retained only as temporary/debug/fallback.

---

## 5. Long-Term Direction

The next long-term voice work should focus on a local lab environment, not app
runtime wiring.

The provider should be considered for runtime only after it passes:

- Manual environment check: Python/Conda/PowerShell/GPU/VRAM/disk constraints.
- License and voice-data review: source voice rights, generated output terms,
  pretrained model terms, and app distribution constraints.
- Standalone probe plan: fixed Traditional Chinese corpus, latency capture,
  generated output under ignored folders, and manual listening verdict.
- Integration readiness review: local sidecar/API behavior, cancellation,
  timeout, error classification, output file cleanup, and no silent fallback.

Until then:

- Runtime provider remains `mock`.
- `TTS_ENABLED` remains false by default.
- `/chat` remains text-only and unchanged.
- No playback, Pet playback, or auto-speaking is added.
- No generated audio, voice samples, models, embeddings, reports, temp WAVs,
  local settings, logs, or pytest temp folders are committed.

---

## 6. Proposed Follow-up Tasks

### TASK-TTS-004D2 - Character Voice Feasibility Manual Environment Check

Goal:

- Record local machine constraints for GPT-SoVITS and Style-Bert-VITS2 without
  installing or downloading models unless a later task explicitly allows it.
- Provide local evidence before any GPT-SoVITS or Style-Bert-VITS2 install,
  model download, training, inference, or runtime integration is considered.

Checks:

- Windows version and shell path constraints.
- Python executable, version, and venv state.
- Git, Node, and npm availability.
- Repo drive disk budget.
- GPU model, driver, CUDA compatibility, VRAM, and disk budget.
- PyTorch availability only if already installed; no install is attempted.
- Optional localhost-only VOICEVOX metadata reachability.
- Optional `edge_tts` package availability in the current environment.

Implementation:

- `scripts/tts_character_voice_env_check.py`
- `backend/tests/test_tts_character_voice_env_check.py`
- Reports write to ignored `outputs/tts_character_voice_env_check/YYYYMMDD/`.

Verdict values:

- `ready_for_docs_only`
- `ready_for_cpu_probe`
- `ready_for_gpu_probe`
- `not_ready_missing_gpu_or_cuda`

Boundary:

- No package install.
- No model download.
- No external repo clone.
- No model training.
- No model inference.
- No runtime TTS wiring.
- No playback, Pet playback, or auto-speaking.
- No generated reports committed.

### TASK-TTS-004E - GPT-SoVITS / Style-Bert-VITS2 Minimal Local Probe Plan

Goal:

- Design the smallest allowed local probe before any runtime integration.

Rules:

- No app runtime wiring.
- No `/chat` integration.
- No playback.
- No auto-speaking.
- Generated audio/reports stay under ignored local outputs.
- A manual listening table must decide Chinese intelligibility, Christina fit,
  latency, stability, and whether runtime research can continue.

### TASK-TTS-004D3 - Character Voice Lab Environment Plan

See:

- `docs/TTS_CHARACTER_VOICE_LAB_PLAN.md`

Summary:

- Future GPT-SoVITS / Style-Bert-VITS2 work should use an isolated lab outside
  Dragon Pet AI app code.
- Recommended path: `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\`.
- External repos, model weights, checkpoints, voice samples, generated audio,
  and lab logs belong in the lab only.
- GPT-SoVITS should start from a dedicated Conda environment with Python `3.10`;
  Style-Bert-VITS2 should use a separate dedicated Conda environment matching
  the selected upstream release.
- CUDA/PyTorch is lab-only and must not be installed into `backend\.venv`.
- Standalone WAV/MP3 plus manual listening verdict must come before runtime
  provider selection.
- No `/chat` wiring, playback, Pet playback, or auto-speaking starts from the
  lab plan.

### TASK-TTS-005 - TTS Runtime Playback Queue

Start only after:

- A provider candidate passes standalone synthesis and listening review.
- Licensing/voice data constraints are acceptable.
- Runtime adapter boundaries are documented.
- The user explicitly approves moving from research/probe to runtime playback.

---

## 7. TASK-TTS-004D Closeout

- Final status: DONE - CHARACTER VOICE FEASIBILITY RESEARCH COMPLETE / NO MODEL INSTALLED.
- No model installed.
- No model downloaded.
- No training or inference run.
- No generated audio or report artifact created by this task.
- No runtime TTS wiring added.
- No `/chat`, mood schema, STT, Conversation Mode, Owner Voice, playback, Pet
  playback, auto-speaking, dependency, or default-runtime behavior changed.
