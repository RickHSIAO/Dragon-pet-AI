# GPT-SoVITS Isolated Lab Phase 1

**Task:** TASK-TTS-004E2
**Status:** TASK-TTS-004E6 DONE - GPT-SOVITS CHINESE TEXT DEPENDENCY REVIEW COMPLETE / INSTALL NOT APPROVED
**Date:** 2026-06-19
**Scope:** Approved Phase 1 bootstrap for the external GPT-SoVITS lab, limited
to creating the external lab folder, cloning the official GPT-SoVITS repository,
and creating an isolated Conda Python 3.10 environment. This attempt stopped
before setup because Conda was not available in the current shell. It was later
resumed by TASK-TTS-004E2B through the existing machine-wide Anaconda. The
TASK-TTS-004E3 follow-up reviewed PyTorch/CUDA compatibility only; it
recommended a future lab-only pinned `torch==2.7.0` + `torchaudio==2.7.0`
CUDA `12.8` install, with CUDA `12.6` fallback, but did not install anything.
TASK-TTS-004E3A later installed only that approved PyTorch CUDA package family
and verified CUDA on the RTX 3070. GPT-SoVITS dependencies, WebUI, inference,
synthesis, audio generation, and runtime integration remain unapproved.
TASK-TTS-004E4 later reviewed dependency compatibility only and recommended a
future Group A foundation install. No dependency was installed by E4.

---

## 1. Approval Scope

Approved for TASK-TTS-004E2:

- Create `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\`.
- Clone the official GPT-SoVITS repository:
  `https://github.com/RVC-Boss/GPT-SoVITS.git`.
- Create an isolated Conda Python 3.10 environment at:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310`.

Not approved:

- GPT-SoVITS dependency installation.
- `install.ps1`.
- `pip install`.
- PyTorch installation.
- CUDA package installation.
- Model or pretrained weight downloads.
- Dataset downloads.
- Training.
- Inference.
- WebUI startup.
- Test audio synthesis or audio generation.
- Dragon Pet AI runtime integration.

---

## 2. Main Repo Pre-flight

Main repo path:

```text
F:\RickHSIAO\Python\dragon-pet-ai
```

Pre-flight evidence:

- `git log -1 --oneline`: `79513c2 docs: select first character voice lab candidate`
- `git remote -v`: `origin https://github.com/RickHSIAO/Dragon-pet-AI.git`
- `git status --short`: expected unrelated dirty file only:
  `docs\???孵?.txt`

No generated audio, reports, models, samples, embeddings, logs, or local settings
were staged.

---

## 3. Conda Check

Commands attempted:

```powershell
conda --version
conda info --base
conda env list
```

Result:

- `conda` was not recognized in the current PowerShell PATH.
- No Miniconda, Anaconda, Micromamba, or other Conda replacement was installed.
- No fallback to the main Python installation was used.
- No fallback to `backend\.venv` was used.

Verdict:

```text
BLOCKED - CONDA NOT AVAILABLE / NO INSTALL PERFORMED
```

Because Conda was unavailable, this task did not proceed to lab creation,
repository clone, or Python environment creation.

---

## 4. External Lab State

Checked paths:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS\
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2_PHASE1.md
```

Result:

- Lab root exists: no.
- GPT-SoVITS repo exists: no.
- External Phase 1 manifest exists: no.

No external lab directory was created by this task.

---

## 5. Official Repo Verification

Official target:

```text
https://github.com/RVC-Boss/GPT-SoVITS.git
```

Target path:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS
```

Result:

- Clone was not attempted because Conda was unavailable and the task entered the
  blocked path.
- Official remote was not verified locally.
- Branch and commit are unavailable.
- `README.md`, `LICENSE`, and `install.ps1` were not inspected locally.
- Detected license is unavailable from local clone evidence.

---

## 6. Conda Environment Result

Requested prefix:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310
```

Result:

- Environment was not created.
- Python executable is unavailable.
- Python version is unavailable.
- PyTorch presence check was not run in the target environment because the
  environment does not exist.

No PyTorch, CUDA package, GPT-SoVITS dependency, model, or dataset was installed.

---

## 7. Hardware Evidence

`nvidia-smi` evidence from 2026-06-19:

- GPU: NVIDIA GeForce RTX 3070.
- VRAM: 8192 MiB.
- NVIDIA-SMI / driver evidence: `610.47`.
- Reported CUDA compatibility from `nvidia-smi`: `13.3`.

This only proves the NVIDIA driver reports CUDA compatibility. It does not prove
PyTorch CUDA is installed in any environment, and no PyTorch/CUDA package was
installed by this task.

---

## 8. Artifact Scan Result

No external lab root exists, so there were no TASK-TTS-004E2-created lab files
to scan for:

- `*.ckpt`
- `*.pth`
- `*.pt`
- `*.safetensors`
- `*.onnx`
- `*.wav`
- `*.mp3`
- `*.flac`

No model weights, generated audio, datasets, reports, samples, embeddings, logs,
or local settings were created by this task.

---

## 9. Runtime Boundary

TASK-TTS-004E2 did not change:

- Dragon Pet AI application source/runtime code.
- `/chat` wiring.
- Runtime TTS behavior.
- Playback, Pet playback, or auto-speaking.
- STT defaults or selector.
- Conversation Mode.
- Owner Voice Gate.
- `/chat` schema.
- Mood schema.
- Application dependencies.

Runtime TTS remains disabled/mock-only.

---

## 10. Next Step

TASK-TTS-004E2 remains blocked until Conda is available in the shell or the user
explicitly approves a different isolated environment tool.

TASK-TTS-004E2A approved an isolated Miniconda bootstrap. That attempt downloaded
and verified the official installer, but the silent install failed with exit
code `2`; see `docs/TTS_MINICONDA_LAB_BOOTSTRAP.md`.

TASK-TTS-004E2A2 then performed diagnostics only. It did not retry the installer
or clean the partial install. Direct log evidence narrows the failure to
rollback after a `cp950` `UnicodeDecodeError` while reading existing
Conda-related paths, but exact upstream root cause remains unproven; see
`docs/TTS_MINICONDA_INSTALL_DIAGNOSTICS.md`.

TASK-TTS-004E2A3 then deleted only the approved failed partial install root and
retried the same verified installer once to the same path with process-local
UTF-8 settings. The retry still failed with exit code `2`; see
`docs/TTS_MINICONDA_UTF8_RETRY.md`.

TASK-TTS-004E2B resumed Phase 1 through the existing machine-wide Anaconda,
created the isolated Python 3.10 env, and cloned the official GPT-SoVITS repo;
see `docs/TTS_EXISTING_ANACONDA_GPT_SOVITS_PHASE1.md`.

TASK-TTS-004E3 completed the GPT-SoVITS PyTorch/CUDA compatibility review
without installing anything. TASK-TTS-004E3A later installed only the approved
PyTorch CUDA package family and verified CUDA. TASK-TTS-004E4 dependency
compatibility review then completed without installing anything. TASK-TTS-004E4A
later installed only the approved foundation dependency group and verified
imports, NumPy/Torch interop, `pip check`, CUDA, and the protected cu128 torch
stack. TASK-TTS-004E5 then completed the audio/text dependency compatibility
review without installing anything. TASK-TTS-004E5A later installed and
verified only the approved B1 WAV/audio dependency group. The next recommended
task is TASK-TTS-004E6 GPT-SoVITS Chinese Text Dependency Review. It is not
approved yet.

---

## TASK-TTS-004E6 Chinese Text Dependency Review

**Status:** TASK-TTS-004E6 DONE - GPT-SOVITS CHINESE TEXT DEPENDENCY REVIEW COMPLETE / INSTALL NOT APPROVED
**Date:** 2026-06-20
**Evidence:** `docs/TTS_GPT_SOVITS_CHINESE_TEXT_DEPENDENCY_REVIEW.md`; external manifest `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E6_CHINESE_TEXT_DEPENDENCY_REVIEW.md`.

TASK-TTS-004E6 inspected GPT-SoVITS commit `b2cff0cd0abd0ac134a16ae7a9695f88e8826104` Chinese normalization, segmentation, pinyin/G2P, phoneme mapping, vendored G2PW, OpenCC, LangSegmenter, requirements, and model/dictionary asset boundaries read-only. No install was approved or performed.

Key conclusion: no safe useful Chinese text install group is ready yet. `jieba_fast` is imported unconditionally and PyPI `jieba-fast==0.53` is source-only; the current v2 Chinese path initializes G2PW at import time and can download model assets if missing; OpenCC needs a separate API/build-risk probe. `cn2an` and `pypinyin` are low-risk wheel candidates, but installing only them would not make the current Chinese path pass.

Selected next task, not approved yet: `TASK-TTS-004E6A - Chinese Text Import Graph Probe`. Do not mark Chinese inference ready.
