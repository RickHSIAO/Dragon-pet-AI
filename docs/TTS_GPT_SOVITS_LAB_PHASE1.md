# GPT-SoVITS Isolated Lab Phase 1

**Task:** TASK-TTS-004E2
**Status:** BLOCKED - CONDA NOT AVAILABLE / NO INSTALL PERFORMED
**Date:** 2026-06-19
**Scope:** Approved Phase 1 bootstrap for the external GPT-SoVITS lab, limited
to creating the external lab folder, cloning the official GPT-SoVITS repository,
and creating an isolated Conda Python 3.10 environment. This attempt stopped
before setup because Conda was not available in the current shell.

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
  `docs\開啟方式.txt`

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

The previously suggested next task, TASK-TTS-004E3 GPT-SoVITS Lab
PyTorch/CUDA Compatibility Review, is not approved and cannot start from this
blocked state.
