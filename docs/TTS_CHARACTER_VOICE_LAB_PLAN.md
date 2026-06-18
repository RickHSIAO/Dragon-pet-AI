# TTS Character Voice Lab Plan

**Task:** TASK-TTS-004D3
**Status:** DONE - CHARACTER VOICE LAB PLAN READY / NO LAB INSTALL PERFORMED
**Date:** 2026-06-19
**Scope:** Planning-only boundary for future GPT-SoVITS / Style-Bert-VITS2
experiments in an isolated lab environment. No lab folder was created, no
external repo was cloned, no package was installed, no model was downloaded, and
no training or inference was run.

---

## 1. Decision Summary

Character voice experiments must not use Dragon Pet AI's main app environment.
Do not install GPT-SoVITS, Style-Bert-VITS2, CUDA PyTorch, model weights, lab
requirements, or voice-processing tools into `backend\.venv`.

Recommended lab location:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\
```

Acceptable alternate location:

```text
F:\RickHSIAO\Python\dragon-pet-ai-lab\
```

Both are outside committed app code. The preferred `AI-Labs` path makes it
clear that external repos, model files, generated clips, and voice samples are
lab artifacts, not Dragon Pet AI runtime files.

---

## 2. Source Basis

The plan uses official project guidance as planning evidence only:

- GPT-SoVITS official README describes a Windows path through an integrated
  package or a Conda environment named `GPTSoVits` with `python=3.10`, plus
  device-specific install choices. It also lists tested environments around
  Python 3.9-3.11 and PyTorch/CUDA combinations.
- GPT-SoVITS official README lists zero-shot, few-shot, and cross-lingual TTS
  support including Chinese, and separate pretrained model/data placement.
- Style-Bert-VITS2 official README describes inference-only pip usage, Windows
  support, CPU synthesis possibility, NVIDIA GPU requirement for training, an
  API server, and AGPL/LGPL license files.

No install or download command from those projects is executed by this task.

---

## 3. Lab Folder Layout

Recommended structure:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\
  README.local.md
  repos\
    GPT-SoVITS\
    Style-Bert-VITS2\
  envs\
    gpt-sovits-conda\
    style-bert-vits2-conda\
  models\
    gpt-sovits\
    style-bert-vits2\
  datasets\
    source_voice\
    transcriptions\
  outputs\
    gpt-sovits\
    style-bert-vits2\
    comparison\
  logs\
```

Rules:

- External repos live under the lab `repos\` folder only.
- Model weights live under the lab `models\` folder only.
- Voice samples and transcripts live under the lab `datasets\` folder only.
- Generated WAV/MP3 files live under the lab `outputs\` folder only.
- Lab logs stay under the lab `logs\` folder only.
- Nothing under the lab is committed to Dragon Pet AI.
- Dragon Pet AI can later document paths or results, but not store private data,
  model files, generated audio, or lab logs.

---

## 4. Environment Strategy

Use a dedicated Conda environment for each candidate first.

Recommended baseline:

- GPT-SoVITS: Conda environment with Python `3.10`.
- Style-Bert-VITS2: dedicated Conda environment, Python `3.10` or the version
  required by the selected upstream release.
- Do not reuse `backend\.venv`.
- Do not add lab dependencies to `backend\requirements*`, project lock files, or
  app runtime dependency documentation.
- Prefer environment-local scripts inside the lab folder, not project scripts
  that mutate app settings.

Why Conda first:

- GPT-SoVITS official setup is Conda-first for manual installation.
- CUDA/PyTorch/FFmpeg-style dependencies are easier to isolate.
- The app backend currently uses Python `3.14.4`, while official GPT-SoVITS
  tested/setup paths are older Python versions. Reusing `backend\.venv` would
  create avoidable runtime risk.

Dedicated venv is acceptable only if a specific upstream release documents a
clean Windows venv path and the environment still lives outside Dragon Pet AI.

---

## 5. GPU / CUDA / PyTorch Plan

TASK-TTS-004D2 found:

- RTX 3070 visible through `nvidia-smi`.
- VRAM total: `8192 MB`.
- Disk free: about `766 GB`.
- Current `backend\.venv`: PyTorch missing, CUDA unavailable through PyTorch.
- Verdict: `not_ready_missing_gpu_or_cuda`.

Plan:

- Keep CUDA PyTorch lab-only.
- Install candidate-specific PyTorch only inside the future lab Conda
  environment after explicit approval.
- Do not install PyTorch into `backend\.venv` for character voice experiments.
- Verify CUDA inside the lab before any model download:
  - Python version.
  - `torch.__version__`.
  - `torch.cuda.is_available()`.
  - `torch.cuda.get_device_name(0)`.
  - VRAM visible to the framework.
- Treat RTX 3070 8 GB as feasible for minimal local experiments and short
  synthesis checks, not automatically sufficient for large training runs.
- Prefer inference/minimal fine-tune checks before any long training.

If the lab cannot prove CUDA through PyTorch, stay at docs-only or CPU-only probe
planning. Do not compensate by modifying the main app environment.

---

## 6. Model, Data, and Output Storage

Store only in the lab:

- Pretrained model weights.
- ASR/VAD/punctuation helper models.
- UVR/vocal-separation models.
- Fine-tuned checkpoints.
- Embeddings, feature files, indexes, caches, and intermediate tensors.
- Source voice samples.
- Transcripts and annotation lists.
- Generated WAV/MP3 comparison clips.
- Lab logs.

Never commit:

- `.wav`, `.mp3`, `.flac`, `.m4a`, `.ogg`
- model weights/checkpoints
- embeddings/features/indexes
- raw or processed voice samples
- generated sample audio
- generated lab reports
- local lab settings
- runtime logs

Dragon Pet AI may commit only sanitized docs that summarize verdicts, commands,
latency numbers, and manual listening decisions.

---

## 7. Privacy and Licensing

Before any real voice data is used:

- Confirm source voice rights.
- Confirm consent for any private or third-party voice sample.
- Record pretrained model licenses.
- Record default voice/model usage terms.
- Record generated output restrictions.
- Do not imitate a real actor, streamer, VTuber, or private person without clear
  rights.
- Treat Christina voice as an original project voice style, not a clone of an
  existing protected performer or character voice.
- Keep private voice data out of Git and out of app runtime folders.

If licensing cannot be documented, stop at docs-only research.

---

## 8. Integration Boundary

The lab is not runtime.

Allowed first lab output:

- Standalone WAV or MP3 files generated manually in the isolated lab.
- Local-only notes about environment, command, source text, latency, and errors.
- Manual listening verdict table.

Not allowed before a separate runtime task:

- No `/chat` wiring.
- No backend TTS provider selection.
- No app playback.
- No Pet Window playback.
- No auto-speaking.
- No dependency/default-runtime change.
- No Conversation Mode coupling.
- No Owner Voice hard-gate change.
- No generated audio committed.

Runtime consideration starts only after standalone synthesis and manual listening
prove a candidate voice is worth integrating.

---

## 9. Exit Criteria Before Real Model Probe

Before TASK-TTS-004E or any real model probe can start, collect:

1. Lab folder chosen outside Dragon Pet AI.
2. Candidate repo and release selected.
3. License and voice-data review recorded.
4. Conda/venv plan selected, with Python version pinned.
5. CUDA/PyTorch verified inside the lab, or CPU-only limitation explicitly
   accepted.
6. Model and dataset storage paths confirmed outside Git.
7. Fixed Traditional Chinese Christina sample corpus prepared.
8. Cleanup plan for generated WAV/MP3 files.
9. Manual listening table template prepared.
10. Explicit user approval for install/download/probe scope.

Minimum evidence before runtime provider selection:

- Environment ready.
- CUDA/PyTorch verified in the lab if GPU path is chosen.
- Provider repo runs standalone.
- Short Chinese Christina sample can be synthesized.
- Generated audio passes manual listening for Chinese intelligibility and
  Christina/anime fit.
- Licensing and voice-data constraints are acceptable.
- Latency and failure behavior are documented.

---

## 10. TASK-TTS-004D3 Closeout

- Final status: DONE - CHARACTER VOICE LAB PLAN READY / NO LAB INSTALL PERFORMED.
- No lab folder created.
- No external repo cloned.
- No package installed.
- No model downloaded.
- No training or inference run.
- No generated audio/report/model/sample committed.
- No runtime TTS wiring, playback, Pet playback, auto-speaking, `/chat`, mood
  schema, STT, Conversation Mode, or Owner Voice behavior changed.
