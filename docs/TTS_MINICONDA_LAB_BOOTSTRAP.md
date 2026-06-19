# TTS Miniconda Lab Bootstrap

**Task:** TASK-TTS-004E2A
**Status:** BLOCKED - ISOLATED MINICONDA INSTALL FAILED
**Date:** 2026-06-19
**Scope:** Approved isolated Miniconda bootstrap for the external character
voice lab. This task was allowed to download the official Miniconda Windows
x86_64 installer, create lab tools/report directories, install Miniconda only
under the approved lab path, and verify direct isolated Conda invocation. It was
not allowed to clone provider repos, create the GPT-SoVITS Python environment,
install dependencies, install PyTorch/CUDA, download models, run inference, or
wire runtime TTS.

---

## 1. Result

Final status:

```text
BLOCKED - ISOLATED MINICONDA INSTALL FAILED
```

The official installer downloaded successfully and SHA-256 verification matched
the official Miniconda index, but the silent installer returned exit code `2`
instead of expected exit code `0`. Required files for a complete install are
missing:

| Required file | Exists |
|---|---|
| `condabin\conda.bat` | no |
| `Scripts\conda.exe` | no |
| `python.exe` | no |
| `Uninstall-Miniconda3.exe` | no |

The partial install directory contains `_conda.exe`, `pkgs`, `Lib`,
`conda-meta`, `.step.log`, and related installer files. `_conda.exe --version`
reports `conda 26.1.1`, but `_conda.exe info --base` points to a temporary
extraction path, not the approved install path. This is not a valid isolated
Miniconda installation.

---

## 2. Installer Evidence

Official source URL:

```text
https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe
```

Installer path:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\installers\Miniconda3-latest-Windows-x86_64.exe
```

File size:

```text
99155816 bytes
```

Downloaded SHA-256:

```text
fe980247dfd30af229a55d9505b57e7c8dfbdb9d24c5bc66fb6078b6a2d53414
```

Official SHA-256:

```text
fe980247dfd30af229a55d9505b57e7c8dfbdb9d24c5bc66fb6078b6a2d53414
```

Hash match:

```text
true
```

Installer exit code:

```text
2
```

Installer rollback evidence from `.step.log`:

- transaction prepared and executed;
- rollback transaction ran;
- installer reported a `cp950` `UnicodeDecodeError` while reading existing
  Conda-related paths.

Private user paths from that traceback are intentionally not copied into this
repo doc.

---

## 3. External Paths

Created by this task:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\installers\
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\
```

Attempted install path:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\miniconda3
```

External manifest:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2A_MINICONDA_BOOTSTRAP.md
```

Do not commit external lab files, installer binaries, partial Miniconda files,
or external manifests into Dragon Pet AI.

---

## 4. PATH and Registration Evidence

The installer was run with:

```text
/InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /S /D=F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\miniconda3
```

PATH inspection after the failed install:

- Persistent user PATH contains install path: false.
- Persistent machine PATH contains install path: false.
- Current process PATH contains install path: false.
- `Get-Command conda`: no command found.
- `where.exe conda`: no command found.
- `Get-Command python -All`: existing user Python commands only, not Miniconda.
- `where.exe python`: no output in this shell.

No `conda init` was run. The PowerShell profile was not created or modified by
this task.

---

## 5. Forbidden Actions Confirmation

Not performed:

- GPT-SoVITS clone.
- Style-Bert-VITS2 clone.
- Conda environment `gpt-sovits-py310`.
- `conda create`.
- `conda install`.
- `pip install`.
- `install.ps1`.
- PyTorch/CUDA package install.
- Model/pretrained-weight download.
- Dataset download.
- Training.
- Inference.
- WebUI startup.
- Synthesis or audio generation.
- Dragon Pet AI runtime integration.

Artifact scan:

- No model/audio artifact patterns were created by this task.
- One package metadata file,
  `tools\miniconda3\pkgs\setuptools-82.0.1-py313haa95532_0\Lib\site-packages\distutils-precedence.pth`,
  exists under the partial installer extraction. It is package metadata, not a
  model weight.

Runtime TTS remains disabled/mock-only.

---

## 6. Next Step

Do not continue to TASK-TTS-004E2B until the failed isolated Miniconda
installation is manually reviewed or the user explicitly approves a retry or
cleanup strategy.

The intended TASK-TTS-004E2B scope, if later approved, is limited to resuming
GPT-SoVITS Phase 1: creating the isolated Python 3.10 environment and cloning /
verifying the official GPT-SoVITS repository. It still must not install
GPT-SoVITS dependencies, PyTorch/CUDA packages, models, or run inference unless
separately approved.
