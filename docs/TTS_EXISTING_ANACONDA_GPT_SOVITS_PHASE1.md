# TTS Existing Anaconda GPT-SoVITS Phase 1 Resume

**Task:** TASK-TTS-004E2B / TASK-TTS-004E3
**Status:** TASK-TTS-004E3 DONE - GPT-SOVITS PYTORCH/CUDA COMPATIBILITY REVIEW COMPLETE / INSTALL NOT APPROVED
**Date:** 2026-06-19
**Scope:** Validate existing machine-wide Anaconda, create one isolated Python
3.10 prefix environment, and clone the official GPT-SoVITS repository only
after environment verification. No Anaconda base modification, PATH/profile/
registry modification, `conda init`, Miniconda retry, dependency install,
PyTorch/CUDA install, model download, training, inference, WebUI, synthesis,
audio generation, runtime TTS wiring, or backend venv change was performed.

TASK-TTS-004E3 follow-up:

- Reviewed GPT-SoVITS PyTorch/CUDA compatibility without installing anything.
- Primary future recommendation is pinned `torch==2.7.0` +
  `torchaudio==2.7.0` from PyTorch CUDA `12.8` wheels in the isolated env.
- CUDA `12.6` is fallback; CPU-only is last resort.
- GPT-SoVITS `install.ps1`, TorchCodec, full dependencies, models, WebUI,
  inference, synthesis, and audio generation remain unapproved.

---

## 1. Result

Final status:

```text
DONE - EXISTING ANACONDA VERIFIED / GPT-SOVITS LAB PHASE 1 READY
```

TASK-TTS-004E2B resumed Phase 1 by using the existing machine-wide Anaconda
installation instead of retrying Miniconda. The selected Anaconda installation
was verified with process-local UTF-8 settings, the isolated Python 3.10 env was
created under the external lab, and the official GPT-SoVITS repository was
cloned and verified.

---

## 2. Existing Anaconda Selection

Selected registry entry:

```text
HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\Anaconda3 2025.12-2 (Python 3.13.9 64-bit)
```

Selected Anaconda root:

```text
C:\ProgramData\anaconda3
```

Why selected:

- It was the only authoritative machine-wide Anaconda registry entry found.
- `Scripts\conda.exe`, `condabin\conda.bat`, `python.exe`, `conda-meta`, and
  `pkgs` all exist.
- The failed lab Miniconda path was rejected and not used.

Direct validation:

- Conda executable: `C:\ProgramData\anaconda3\Scripts\conda.exe`.
- Conda version: `conda 25.11.1`.
- `conda info --base`: `C:\ProgramData\anaconda3`.
- Base Python: `C:\ProgramData\anaconda3\python.exe`.
- Base Python version: `Python 3.13.9`.

Validation note:

- Default code-page `conda env list` fails with the known `cp950`
  `UnicodeDecodeError`.
- Direct validation succeeds when using process-local `PYTHONUTF8=1` and
  `PYTHONIOENCODING=utf-8`.
- No global environment variable, PATH, or profile was modified.

---

## 3. Isolated Environment

Lab package cache:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\pkgs-cache
```

Target prefix:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310
```

Creation command:

```text
C:\ProgramData\anaconda3\Scripts\conda.exe create --prefix F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310 --override-channels --channel defaults python=3.10 -y
```

Creation result:

```text
CreateExit: 0
```

Target Python:

```text
Python 3.10.20
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe
```

PyTorch probe:

```text
None
```

Installed env packages are normal Python 3.10 base-environment packages from
`defaults`, such as Python, pip, setuptools, wheel, openssl, sqlite, VC runtime,
UCRT, tk, xz, zlib, and related base packages. No PyTorch/CUDA/GPT-SoVITS
dependencies were installed.

---

## 4. GPT-SoVITS Repository

Official repository:

```text
https://github.com/RVC-Boss/GPT-SoVITS.git
```

Clone path:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS
```

Verification used per-command `git -c safe.directory=...` because the external
lab repo triggered Git dubious-ownership protection under the sandbox user. No
global Git config was modified.

Verified origin:

```text
origin https://github.com/RVC-Boss/GPT-SoVITS.git (fetch)
origin https://github.com/RVC-Boss/GPT-SoVITS.git (push)
```

Branch:

```text
main
```

Commit:

```text
b2cff0cd0abd0ac134a16ae7a9695f88e8826104
```

Detected license:

```text
MIT License
```

Required files found:

- `README.md`
- `LICENSE`
- `install.ps1`

`install.ps1` was not run.

---

## 5. Artifact Scan

Scanned the external lab for:

```text
*.ckpt, *.pth, *.pt, *.safetensors, *.onnx, *.wav, *.mp3, *.flac
```

Findings:

- `envs\gpt-sovits-py310\Lib\site-packages\distutils-precedence.pth` - package
  metadata, not model weight/audio.
- `pkgs-cache\setuptools-82.0.1-py310haa95532_0\Lib\site-packages\distutils-precedence.pth`
  - package metadata, not model weight/audio.
- `tools\miniconda3\pkgs\setuptools-82.0.1-py313haa95532_0\Lib\site-packages\distutils-precedence.pth`
  - prior failed Miniconda package metadata, not model weight/audio.

No `.ckpt`, `.pt`, `.safetensors`, `.onnx`, `.wav`, `.mp3`, or `.flac`
artifacts were found. This task did not create model weights or audio.

---

## 6. External Manifest

External manifest:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2B_EXISTING_ANACONDA_RESUME.md
```

Do not commit external lab reports, Conda environments, package caches,
installer files, cloned provider repositories, model files, generated audio,
or lab logs into Dragon Pet AI.

---

## 7. Forbidden Actions Confirmation

Not performed:

- Anaconda base package install or update.
- `conda update`.
- `conda install` against base.
- PATH/profile/registry modification.
- `conda init`.
- Miniconda installer retry.
- Failed partial Miniconda deletion or modification.
- Miniforge/Micromamba/alternate manager install.
- GPT-SoVITS `install.ps1`.
- GPT-SoVITS dependency install.
- `pip install`.
- PyTorch/CUDA install.
- Model or dataset download.
- Training, inference, WebUI, synthesis, or audio generation.
- Runtime TTS wiring, playback, Pet playback, or auto-speaking.
- STT, Conversation Mode, Owner Voice, `/chat` schema, or mood schema behavior
  change.
- Backend venv or application dependency file change.

---

## 8. Next Step

Recommended next task, not approved yet:

```text
TASK-TTS-004E3A - GPT-SoVITS Lab PyTorch/CUDA Install
```
