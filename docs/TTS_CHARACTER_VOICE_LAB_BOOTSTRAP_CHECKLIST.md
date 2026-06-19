# TTS Character Voice Lab Bootstrap Checklist

**Task:** TASK-TTS-004D4 / TASK-TTS-004E / TASK-TTS-004E2 / TASK-TTS-004E2A
**Status:** TASK-TTS-004E2A BLOCKED - ISOLATED MINICONDA INSTALL FAILED
**Date:** 2026-06-19
**Scope:** Manual-command checklist for a future isolated character voice lab.
This task did not create the lab folder, clone external repos, install
packages, download models, train, infer, synthesize audio, or wire runtime TTS.

TASK-TTS-004E adds the provider-selection checkpoint:

- `docs/TTS_CHARACTER_VOICE_PROVIDER_SELECTION.md`

GPT-SoVITS is the first isolated lab candidate. Style-Bert-VITS2 is the second
provider / fallback research path. The first real probe remains unapproved.

TASK-TTS-004E2 attempted approved GPT-SoVITS Phase 1 bootstrap, but Conda was
not available in the current PowerShell PATH. No lab setup was performed.

TASK-TTS-004E2A attempted isolated Miniconda bootstrap, but the official
installer failed with exit code `2` after successful SHA-256 verification.

---

## 1. Pre-flight Safety Checks

Before any future lab setup, confirm the app repo state from PowerShell:

```powershell
Set-Location F:\RickHSIAO\Python\dragon-pet-ai
git status --short
git diff --cached --name-only
git diff --cached --stat
```

Required state:

- Current repo path is `F:\RickHSIAO\Python\dragon-pet-ai`.
- Git status is clean except any explicitly unrelated local file such as
  `docs\開啟方式.txt`.
- No generated audio, model, report, voice sample, temp WAV, embedding, local
  setting, log, or pytest temp folder is staged.
- Runtime app files are not being modified for this task.
- `/chat`, mood schema, STT selector/defaults, Conversation Mode
  queue/backpressure, Owner Voice hard-gate, playback, and auto-speaking remain
  untouched.

---

## 2. Lab Folder Plan

Recommended lab path:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\
```

Manual commands for a later approved setup:

```powershell
New-Item -ItemType Directory -Force -Path F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab
New-Item -ItemType Directory -Force -Path F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos
New-Item -ItemType Directory -Force -Path F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs
New-Item -ItemType Directory -Force -Path F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\models
New-Item -ItemType Directory -Force -Path F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\datasets
New-Item -ItemType Directory -Force -Path F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\outputs
New-Item -ItemType Directory -Force -Path F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports
New-Item -ItemType Directory -Force -Path F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\scratch
```

These commands are examples only. TASK-TTS-004D4 does not execute them.

---

## 3. Environment Strategy

Preferred strategy:

- Use isolated Conda environments for heavy model work.
- Use a dedicated venv only if the selected upstream release documents a known
  working Windows/Python/CUDA combination.
- Do not reuse `backend\.venv`.
- Do not add lab packages to app dependency files.
- Prefer Python `3.10` or `3.11`, depending on the target provider release.
- Avoid Python `3.14` for GPT-SoVITS / Style-Bert-VITS2 experiments unless
  upstream explicitly supports it.

Current app environment note:

- The current Dragon Pet AI backend venv uses Python `3.14.4`.
- TASK-TTS-004D2 found PyTorch missing and CUDA unavailable through PyTorch in
  `backend\.venv`.
- That app venv is not suitable for GPT-SoVITS / Style-Bert-VITS2 setup.

Manual Conda examples for a future approved setup:

```powershell
conda create -n dragon-pet-gpt-sovits python=3.10
conda create -n dragon-pet-style-bert-vits2 python=3.10
```

Do not run these commands until the human approval gate in section 9 is passed.

---

## 4. GPU / CUDA / PyTorch Verification Checklist

Manual checks before any model download:

```powershell
nvidia-smi
python --version
python -c "import sys; print(sys.executable); print(sys.version)"
```

After a future approved PyTorch install inside the lab environment only:

```powershell
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NO CUDA')"
```

Rules:

- Do not install PyTorch during TASK-TTS-004D4.
- Do not install CUDA/PyTorch into `backend\.venv`.
- Record GPU name, VRAM, driver/CUDA evidence, Python version, PyTorch version,
  and CUDA availability in a lab report before any synthesis probe.
- If CUDA is unavailable, stop and decide whether a CPU-only probe is acceptable
  before downloading models.

---

## 5. External Repo Boundary

Future clone locations only:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS\
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\Style-Bert-VITS2\
```

Rules:

- Do not clone external repos into `F:\RickHSIAO\Python\dragon-pet-ai`.
- Do not vendor provider source into the app repo.
- Do not add provider repo paths to runtime imports.
- Do not create sidecar runtime wiring until a separate runtime task approves
  it.

---

## 6. Model and Data Storage Rules

Lab-only storage:

- Model weights: `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\models\`
- Source datasets and transcripts:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\datasets\`
- Generated samples:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\outputs\`
- Lab reports:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\`
- Temporary processing files:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\scratch\`

Never commit to Dragon Pet AI:

- Model weights/checkpoints.
- Source or processed voice samples.
- Generated WAV/MP3/FLAC/M4A/OGG files.
- Embeddings, indexes, feature files, caches, and intermediate tensors.
- Local lab settings, logs, or raw provider reports.

Voice data rules:

- Voice samples require rights and explicit permission.
- Generated voices are local artifacts unless a later task defines safe export
  rules.
- Christina voice work should target an original project voice style, not an
  imitation of a real person or protected performer.

---

## 7. Git Ignore / Repo Safety

Current repo safety coverage already includes:

```gitignore
outputs/tts_provider_probe/
outputs/tts_character_voice_env_check/
outputs/tts_character_voice_lab/
.local-voice-lab/
voice-lab/
```

Future ignore changes, if needed, must be narrow and local-artifact-only.

Allowed examples:

- `.local-voice-lab/`
- `voice-lab/`
- `outputs/tts_character_voice_lab/`
- `outputs/tts_character_voice_env_check/`
- `outputs/tts_provider_probe/`

Do not ignore:

- Source docs.
- Runtime app code.
- Test files.
- Project dependency manifests.
- Real task records.

---

## 8. Provider-specific Bootstrap Notes

### GPT-SoVITS

Before install, check and record:

- Official install documentation for the selected release.
- Required Python version.
- Required CUDA/PyTorch version.
- Whether Windows setup should use Conda, integrated package, or another
  upstream-supported path.
- Model license and pretrained weight terms.
- Voice data rights.
- Inference-only path before training.
- Minimal Traditional Chinese sample synthesis path.
- Output folder and cleanup plan.

### Style-Bert-VITS2

Before install, check and record:

- Official install documentation for the selected release.
- Required Python version.
- Required CUDA/PyTorch version.
- Supported languages and Chinese quality expectations.
- Model/license terms, including project and pretrained model terms.
- Whether CPU synthesis or GPU training is planned.
- Minimal sample synthesis path.
- Output folder and cleanup plan.

---

## 9. Human Approval Gate Before Real Install

Before any install, clone, model download, training, inference, or audio
synthesis, the user must explicitly approve:

1. Exact lab path.
2. Exact target provider.
3. Exact Python version.
4. Exact environment tool: Conda or venv.
5. Whether cloning an external repo is allowed.
6. Whether package install is allowed.
7. Whether GPU/CUDA install is allowed.
8. Whether model downloads are allowed.
9. Whether inference is allowed.
10. Whether generated audio output is allowed.
11. Artifact cleanup and non-commit policy.

Without this approval, stop at docs-only planning.

---

## 10. TASK-TTS-004E Provider Selection

TASK-TTS-004E selects the first lab candidate but does not approve setup.

- First provider candidate: GPT-SoVITS.
- Second provider / fallback research path: Style-Bert-VITS2.
- Final runtime provider: not selected.
- RVC-like conversion: deferred until a source TTS provider exists.
- edge-tts: temporary Chinese/debug/fallback only.
- VOICEVOX: Japanese-style/Japanese utterance experiment only.

Success criteria for a later approved first probe:

- Repo setup completes in the isolated lab only.
- CUDA/PyTorch is verified inside the lab if GPU path is chosen.
- Dragon Pet AI runtime stays unchanged.
- A short standalone Chinese sample can be generated.
- Generated audio remains uncommitted.
- Manual listening judges Chinese intelligibility, Christina fit,
  anime/character feel, latency, and stability.

Rejection criteria:

- Setup requires unsafe or unbounded installs.
- License terms are unclear.
- Voice data rights are missing.
- The path cannot run acceptably on RTX 3070 8 GB.
- Chinese output is poor.
- Sample quality does not beat edge-tts / VOICEVOX enough to justify added
  complexity.

## 11. Exit Criteria for Future TASK-TTS-004E2

TASK-TTS-004E2 or any real model probe may begin only after:

- Lab path is approved.
- Environment strategy is approved.
- Python version is selected.
- First provider is selected, likely GPT-SoVITS first.
- Install/download permission is explicitly given.
- Generated artifact policy is confirmed.
- CUDA/PyTorch or CPU-only limitation is documented.
- Provider license and voice-data constraints are reviewed.
- Manual listening verdict template is ready.
- Cleanup plan is agreed.

Until those criteria are met, runtime TTS remains disabled/mock-only and the
Chinese Christina provider remains unresolved.

---

## 12. TASK-TTS-004D4 Closeout

- Final status: DONE - CHARACTER VOICE LAB BOOTSTRAP CHECKLIST READY / NO SETUP PERFORMED.
- New checklist document added.
- Manual command examples documented but not executed.
- No package/model installed.
- No external repo cloned.
- No lab folder created.
- No model download, training, inference, synthesis, or generated audio.
- No runtime TTS wiring, playback, Pet playback, auto-speaking, `/chat`, mood
  schema, STT, Conversation Mode, or Owner Voice behavior changed.

---

## 13. TASK-TTS-004E Closeout

- Final status: DONE - CHARACTER VOICE PROVIDER SELECTION READY / FIRST PROBE NOT APPROVED YET.
- Provider selection doc added.
- GPT-SoVITS selected as first isolated lab candidate.
- Style-Bert-VITS2 kept as second provider / fallback research path.
- No final runtime provider selected.
- No lab setup performed.
- No external repo cloned.
- No package/model installed.
- No model download, training, inference, synthesis, or generated audio.
- No runtime TTS wiring, playback, Pet playback, auto-speaking, `/chat`, mood
  schema, STT, Conversation Mode, or Owner Voice behavior changed.

---

## 14. TASK-TTS-004E2 Blocked Bootstrap Attempt

- Final status: BLOCKED - CONDA NOT AVAILABLE / NO INSTALL PERFORMED.
- Evidence doc: `docs/TTS_GPT_SOVITS_LAB_PHASE1.md`.
- `conda --version`, `conda info --base`, and `conda env list` failed because
  `conda` is not recognized in the current PowerShell PATH.
- Lab root was not created.
- GPT-SoVITS repository was not cloned.
- Conda Python 3.10 environment was not created.
- External Phase 1 manifest was not written.
- `nvidia-smi` evidence: NVIDIA GeForce RTX 3070, 8192 MiB VRAM,
  NVIDIA-SMI/driver evidence `610.47`, CUDA compatibility `13.3`.
- The CUDA compatibility value from `nvidia-smi` does not prove PyTorch CUDA is
  installed.
- No dependency, PyTorch/CUDA package, model, dataset, training, inference,
  WebUI, synthesis, generated audio, runtime TTS wiring, playback,
  auto-speaking, `/chat`, mood schema, STT, Conversation Mode, or Owner Voice
  behavior changed.

---

## 15. TASK-TTS-004E2A Blocked Miniconda Attempt

- Final status: BLOCKED - ISOLATED MINICONDA INSTALL FAILED.
- Evidence doc: `docs/TTS_MINICONDA_LAB_BOOTSTRAP.md`.
- Official installer download and SHA-256 verification succeeded.
- Silent install returned exit code `2` and rolled back.
- Required `condabin\conda.bat`, `Scripts\conda.exe`, `python.exe`, and
  `Uninstall-Miniconda3.exe` are missing.
- PATH/Python registration inspection did not show Miniconda pollution.
- `conda init` was not run.
- PowerShell profile was not created or modified by this task.
- No GPT-SoVITS / Style-Bert clone, Conda env, dependency install,
  PyTorch/CUDA install, model/dataset download, training, inference, WebUI,
  synthesis, audio generation, runtime TTS wiring, playback, auto-speaking,
  `/chat`, mood schema, STT, Conversation Mode, or Owner Voice behavior changed.
