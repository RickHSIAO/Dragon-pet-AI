# TTS Character Voice Provider Selection

**Task:** TASK-TTS-004E / TASK-TTS-004E2
**Status:** TASK-TTS-004E2 BLOCKED - CONDA NOT AVAILABLE / NO INSTALL PERFORMED
**Date:** 2026-06-19
**Scope:** Docs-only provider-selection and first-probe approval plan for the
future isolated character voice lab. This task does not create the lab, clone
external repos, install packages, download models, train, infer, synthesize
audio, or wire runtime TTS.

---

## 1. Provider Selection

First provider to probe later:

- GPT-SoVITS.

Second provider / fallback research path:

- Style-Bert-VITS2.

Deferred or non-primary paths:

- RVC-like conversion remains deferred until a source TTS provider exists.
- edge-tts remains temporary Chinese/debug/fallback only.
- VOICEVOX remains a Japanese-style/Japanese utterance experiment only.

No final runtime provider is selected by TASK-TTS-004E. GPT-SoVITS is only the
first isolated lab candidate.

TASK-TTS-004E2 attempted the approved GPT-SoVITS Phase 1 bootstrap, but Conda
was not available in the current PowerShell PATH. The first probe remains
blocked.

---

## 2. Why GPT-SoVITS First

GPT-SoVITS is the first lab candidate because it is the better first fit for:

- few-shot / reference-voice style experiments;
- limited-data character voice exploration;
- Chinese and cross-lingual feasibility checks;
- a smaller first probe than immediately adopting a full style-control stack.

This is not runtime approval. GPT-SoVITS must still pass environment,
licensing, voice-data, quality, latency, stability, and manual listening gates
before any Dragon Pet AI runtime integration is considered.

Style-Bert-VITS2 remains important because it may fit anime/style-control
research well, but it should be second until Chinese quality, licensing, and
setup complexity are better understood.

---

## 3. Proposed First Lab Path

Recommended isolated lab path:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\
```

Future provider repo paths, if explicitly approved later:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS\
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\Style-Bert-VITS2\
```

TASK-TTS-004E does not create these folders.

---

## 4. Proposed Environment

Preferred first environment:

- isolated Conda environment;
- Python `3.10` or `3.11`, with the exact version selected from the chosen
  upstream release notes before setup;
- lab-only PyTorch/CUDA install if explicitly approved later;
- no reuse of `backend\.venv`;
- no app dependency, lockfile, runtime default, or provider setting change.

Current hardware evidence from prior local checks:

- RTX 3070 visible;
- 8 GB VRAM;
- PyTorch/CUDA is not available in the current backend venv.

The backend app venv is not a GPT-SoVITS / Style-Bert-VITS2 environment.

---

## 5. Required Approval Before TASK-TTS-004E2 Setup

Before any real setup, clone, install, model download, training, inference, or
test audio generation, the user must explicitly approve:

1. Exact lab path.
2. Exact provider.
3. Exact Python version.
4. Conda vs venv.
5. Whether cloning an external repo is allowed.
6. Whether package install is allowed.
7. Whether PyTorch/CUDA install is allowed.
8. Whether model download is allowed.
9. Whether test audio generation is allowed.
10. Artifact storage and cleanup policy.

Without this approval, stay docs-only.

---

## 6. First Probe Success Criteria

A future approved first probe succeeds only if:

- repo setup completes inside the isolated lab only;
- CUDA/PyTorch is verified inside the lab if GPU path is chosen;
- Dragon Pet AI runtime files remain unchanged;
- a short standalone Chinese sample can be generated;
- generated audio remains uncommitted;
- manual listening judges the sample for:
  - Chinese intelligibility;
  - Christina fit;
  - anime/character feel;
  - latency;
  - stability.

Passing a first probe still does not authorize runtime TTS. It only authorizes a
separate provider-readiness review.

---

## 7. First Probe Rejection Criteria

Reject the first probe path if:

- setup requires unsafe or unbounded installs;
- license terms are unclear;
- the path requires voice data without rights;
- it cannot run acceptably on RTX 3070 8 GB;
- Chinese output is poor;
- sample quality does not beat edge-tts / VOICEVOX enough to justify the added
  complexity.

If GPT-SoVITS is rejected for these reasons, Style-Bert-VITS2 becomes the next
research path, not an automatic runtime provider.

---

## 8. Runtime Boundary

Runtime TTS remains disabled/mock-only.

TASK-TTS-004E does not add:

- `/chat` integration;
- `/chat` schema or mood schema changes;
- runtime TTS playback;
- Pet Window playback;
- auto-speaking;
- STT default or STT selector changes;
- Conversation Mode queue/backpressure changes;
- Owner Voice hard-gate changes;
- ElevenLabs integration;
- paid/cloud default provider behavior.

Generated audio, models, reports, voice samples, temp WAV files, embeddings,
local settings, logs, and pytest temp folders must remain uncommitted.

---

## 9. TASK-TTS-004E Closeout

- First provider candidate: GPT-SoVITS.
- Second provider / fallback research candidate: Style-Bert-VITS2.
- Final runtime provider: not selected.
- First probe: not approved yet.
- Lab setup: not performed.
- Package/model install: not performed.
- External repo clone: not performed.
- Model download/training/inference/audio generation: not performed.
- Runtime wiring/playback/auto-speaking: not added.

---

## 10. TASK-TTS-004E2 Blocked Phase 1 Attempt

See:

- `docs/TTS_GPT_SOVITS_LAB_PHASE1.md`

Result:

- Final status: BLOCKED - CONDA NOT AVAILABLE / NO INSTALL PERFORMED.
- Conda was not available, so setup stopped before lab creation.
- External lab directory: not created.
- Official GPT-SoVITS clone: not attempted.
- Conda Python 3.10 env: not created.
- External Phase 1 manifest: not written.
- GPT-SoVITS branch, commit, and local license detection: unavailable because
  the repository was not cloned.
- PyTorch presence result in the target env: unavailable because the env does
  not exist; no PyTorch/CUDA package was installed.
- Runtime TTS remains disabled/mock-only.
