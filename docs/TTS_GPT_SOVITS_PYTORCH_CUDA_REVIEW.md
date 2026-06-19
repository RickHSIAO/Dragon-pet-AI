# GPT-SoVITS PyTorch CUDA Compatibility Review

**Task:** TASK-TTS-004E3
**Status:** DONE - GPT-SOVITS PYTORCH/CUDA COMPATIBILITY REVIEW COMPLETE / INSTALL NOT APPROVED
**Date:** 2026-06-19
**Scope:** Read-only compatibility review for the isolated GPT-SoVITS lab
environment. No package install, dependency install, CUDA Toolkit install,
model download, training, inference, WebUI startup, synthesis, audio generation,
Dragon Pet AI runtime change, `/chat` change, STT change, Conversation Mode
change, Owner Voice change, schema change, playback change, or auto-speaking
change was performed.

**Follow-up:** TASK-TTS-004E3A later installed only `torch==2.7.0` and
`torchaudio==2.7.0` from PyTorch CUDA `12.8` wheels in the isolated lab env and
verified CUDA on the RTX 3070. That follow-up did not install GPT-SoVITS
dependencies, `install.ps1`, TorchCodec, ffmpeg, models, WebUI, inference,
synthesis, audio generation, or runtime wiring. See
`docs/TTS_GPT_SOVITS_PYTORCH_CUDA_INSTALL.md`.

**Dependency follow-up:** TASK-TTS-004E4 later reviewed GPT-SoVITS dependency
compatibility without installing anything. TASK-TTS-004E4A then installed only
the approved Group A Safe Foundation packages and verified that torch,
torchaudio, CUDA, and NumPy/Torch interop still work. See
`docs/TTS_GPT_SOVITS_DEPENDENCY_REVIEW.md` and
`docs/TTS_GPT_SOVITS_FOUNDATION_DEPENDENCY_INSTALL.md`.

---

## 1. Reviewed State

Dragon Pet AI project:

```text
F:\RickHSIAO\Python\dragon-pet-ai
```

External lab:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab
```

Existing Anaconda:

```text
C:\ProgramData\anaconda3
C:\ProgramData\anaconda3\Scripts\conda.exe
conda 25.11.1
```

Target environment:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310
Python 3.10.20
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe
torch probe: None
```

GPT-SoVITS repository:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS
origin: https://github.com/RVC-Boss/GPT-SoVITS.git
branch: main
commit: b2cff0cd0abd0ac134a16ae7a9695f88e8826104
license: MIT
```

NVIDIA evidence from `nvidia-smi`:

```text
GPU: NVIDIA GeForce RTX 3070
VRAM: 8192 MiB
NVIDIA-SMI: 610.47
KMD Version: 610.47
CUDA UMD Version: 13.3
```

Important interpretation:

- `nvidia-smi` proves the NVIDIA driver stack reports CUDA compatibility.
- It does not prove CUDA Toolkit is installed.
- It does not prove PyTorch CUDA is installed.
- PyTorch remains absent in the target env.

---

## 2. Inspected GPT-SoVITS Files

Read-only inspected:

| Path | Evidence |
|---|---|
| `README.md` | Python badge `3.10--3.12`; install examples create `python=3.10`; Windows install uses `install.ps1 --Device <CU126|CU128|CPU>`; Docker examples use CUDA `12.6` / `12.8`; README lists tested `Python 3.11 / PyTorch 2.7.0 / CUDA 12.8`; CPU path exists. |
| `requirements.txt` | Includes `pytorch-lightning>=2.4`, `torchaudio`, `onnxruntime-gpu` on x86_64/AMD64, `torchmetrics<=1.5`; no pinned `torch`; no `torchvision`; no `xformers`, `triton`, `deepspeed`, or `faiss`. |
| `extra-req.txt` | Includes `faster-whisper`. |
| `install.ps1` | Windows device choices are `CU126`, `CU128`, `CPU`; installs `ffmpeg cmake` through Conda; installs `torch torchcodec` from PyTorch `cu128`, `cu126`, or `cpu` index; then installs `extra-req.txt` and `requirements.txt`; downloads pretrained/G2PW/NLTK/OpenJTalk assets. Not executed. |
| `install.sh` | Linux/macOS path mirrors `CU126`, `CU128`, `ROCM`, `MPS`, `CPU`; CUDA path installs `torch torchcodec` from `cu128` or `cu126`; has CPU fallback when NVIDIA driver is not found. Not executed. |
| `Dockerfile` | Default `ARG CUDA_VERSION=12.6`; base image is `xxxxrt666/torch-base:cu${CUDA_VERSION}-${TORCH_BASE}`. Not built. |
| `docker-compose.yaml` | Defines `GPT-SoVITS-CU126`, `GPT-SoVITS-CU128`, and lite variants with `runtime: nvidia` and `shm_size: "16g"`. Not run. |
| `docker_build.sh` | Accepts CUDA `12.6|12.8`. Not executed. |
| `Docker\miniforge_install.sh` | Docker path installs `torch torchcodec`, `cuda-nvcc=12.6/12.8`, and `flash-attn`. This is Docker-only evidence and should not be applied to the Windows prefix env without separate review. |
| `GPT_SoVITS\BigVGAN\requirements.txt` | Includes unpinned `torch`; BigVGAN README references a separate `pytorch-cuda=12.1` Conda example, but the main GPT-SoVITS install scripts now prefer `CU126` or `CU128`. |
| `config.py` | Uses `torch.cuda.is_available()`, GPU compute capability, and total memory; falls back to CPU when VRAM is below roughly 4 GiB or SM is too old; RTX 3070 class hardware should select CUDA and `float16` if PyTorch CUDA is working. |

No `pyproject.toml`, `environment.yml`, Conda lock file, pip lock file, or
dependency lock file was found in the repo root.

---

## 3. External Source Checks

Official PyTorch local install guidance was checked on 2026-06-19:

- PyTorch Windows supports Python `3.10-3.14`.
- PyTorch Windows pip installs are the supported binary path.
- PyTorch CUDA verification uses `torch.cuda.is_available()`.
- PyTorch previous-version commands list matching torch/torchaudio/torchvision
  wheel families for CUDA `12.6`, `12.8`, and CPU.
- Current previous-version records include `torch==2.7.0` with `cu126` and
  `cu128`, and newer versions with `cu126`/`cu128` as well.

Official TorchCodec source was checked on 2026-06-19:

- TorchCodec should be version-matched to `torch`.
- `torchcodec` `0.3` through `0.5` map to `torch 2.7` and Python `>=3.9`,
  `<=3.13`.
- Newer TorchCodec releases map to newer torch versions.
- TorchCodec CUDA support on Windows requires using the PyTorch wheel index and
  may involve FFmpeg/libnvrtc concerns, so it should not be silently bundled
  into the first PyTorch CUDA verification step.

Sources:

- https://pytorch.org/get-started/locally/
- https://pytorch.org/get-started/previous-versions/
- https://github.com/meta-pytorch/torchcodec

---

## 4. Compatibility Findings

Python:

- Target env Python `3.10.20` is compatible with GPT-SoVITS README setup
  examples and PyTorch Windows support.
- It is safer than the app backend Python for this lab because GPT-SoVITS docs
  create a Python 3.10 Conda environment.

PyTorch:

- GPT-SoVITS does not pin `torch` in `requirements.txt`.
- GPT-SoVITS install scripts install unpinned `torch torchcodec` from the
  selected PyTorch CUDA index.
- Unpinned install is not recommended for this lab because it can drift with
  upstream PyTorch/TorchCodec releases and make the review non-reproducible.
- The safest future install plan should pin the torch family first.

CUDA build:

- Repository evidence favors `CU126` or `CU128`, not `CU118`, `CU121`, or
  `CU124`.
- Current NVIDIA driver evidence reports CUDA UMD `13.3`, which is newer than
  `12.8`; this is compatible with selecting a CUDA `12.8` PyTorch wheel family.
- A system CUDA Toolkit should not be required for standard PyTorch pip wheels.
- CUDA Toolkit, `cuda-nvcc`, `flash-attn`, and Docker build dependencies should
  stay out of the first Windows prefix-env install task.

TorchAudio / TorchVision:

- `torchaudio` is required by GPT-SoVITS `requirements.txt` and multiple repo
  code paths.
- `torchvision` is not required by the main GPT-SoVITS `requirements.txt`.
- PyTorch official commands include `torchvision` as a paired domain package,
  but installing it is unnecessary for the first GPT-SoVITS inference-oriented
  PyTorch CUDA verification step unless later dependency review proves it is
  required.

TorchCodec:

- GPT-SoVITS `install.ps1` installs `torchcodec`.
- TorchCodec version must be paired with torch.
- Because TorchCodec has FFmpeg/libnvrtc/GPU codec considerations, install it
  only in the later GPT-SoVITS dependency phase or explicitly pin it with the
  torch family if that phase is approved.

GPU-sensitive packages:

- Main `requirements.txt` uses `onnxruntime-gpu` on x86_64/AMD64 and
  `torchaudio`.
- No main dependency pin was found for `xformers`, `triton`, `flash-attn`,
  `deepspeed`, or `faiss`.
- Docker-only helper installs `flash-attn` and `cuda-nvcc`; do not apply that
  to the Windows prefix env in this task.

Windows:

- GPT-SoVITS README has a Windows section and `install.ps1`.
- PyTorch Windows pip supports Python 3.10 and CUDA wheels.
- Windows-specific risk remains high because GPT-SoVITS dependency install
  includes many audio/NLP packages, but that is outside this PyTorch/CUDA-only
  review.

RTX 3070 8GB:

- GPT-SoVITS `config.py` treats VRAM below roughly 4 GiB as CPU fallback and
  uses CUDA/float16 on capable GPUs.
- RTX 3070 has 8 GiB VRAM and Ampere capability, so inference-only use is
  likely feasible after PyTorch CUDA is verified.
- Training/fine-tuning, UVR5, long batches, Docker `shm_size=16g`, and large
  models may still exceed practical memory; this review does not approve
  training or inference.

---

## 5. Compatibility Matrix

| Candidate | Python 3.10 | Windows | Driver / CUDA evidence | GPT-SoVITS evidence | Risks | Size / storage | VRAM implication | System CUDA Toolkit | Installer | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| PyTorch CUDA 11.8 | Compatible by PyTorch docs | Supported by PyTorch | Driver can likely run it, but repo no longer points here | Not current repo script path | Older CUDA family, less aligned with repo; may miss newer package expectations | Large GPU wheels | Same model VRAM need | Not required for PyTorch wheels | pip | Not recommended |
| PyTorch CUDA 12.1 | Compatible by older examples | Supported by older PyTorch examples | Driver can likely run it | Only BigVGAN README has a separate `pytorch-cuda=12.1` example; main repo scripts do not | Contradicts main `CU126/CU128` install path | Large GPU wheels | Same model VRAM need | Not required for PyTorch wheels | conda in BigVGAN example, but not main path | Not recommended for main lab |
| PyTorch CUDA 12.4 | Compatible by older PyTorch versions | Supported by older PyTorch versions | Driver can likely run it | No current GPT-SoVITS main evidence | Older than current repo script path | Large GPU wheels | Same model VRAM need | Not required for PyTorch wheels | pip | Not recommended |
| PyTorch CUDA 12.6 | Compatible | Supported | Driver CUDA UMD 13.3 is above 12.6 | Official GPT-SoVITS scripts support `CU126`; Docker services include CU126 | Slightly less aligned with README tested CUDA 12.8 row; still first-class in repo scripts | Large GPU wheels | RTX 3070 8GB likely enough for inference-only probes | Not required for PyTorch wheels | pip | Fallback |
| PyTorch CUDA 12.8 | Compatible | Supported | Driver CUDA UMD 13.3 is above 12.8 | README tested row mentions CUDA 12.8; scripts support `CU128`; Docker services include CU128 | Must pin torch family; unpinned torch/torchcodec can drift | Large GPU wheels | RTX 3070 8GB likely enough for inference-only probes; training not approved | Not required for PyTorch wheels | pip | Primary recommendation |
| CPU-only PyTorch | Compatible | Supported | GPU not used | GPT-SoVITS scripts support CPU; README points to CPU-optimized inference fork | Slow; does not validate GPU path; may be unsuitable for character-voice iteration | Smaller than CUDA wheels | No VRAM needed | Not required | pip | Fallback only if CUDA install fails |
| Repository `install.ps1` path | Compatible in principle | Windows script exists | Would choose `CU126`, `CU128`, or `CPU` | Official script path | Installs FFmpeg/CMake, dependencies, TorchCodec, downloads models/assets; too broad for this task | Very large and uncontrolled for this phase | May load many later GPU packages | May introduce broader toolchain needs | conda + pip + downloads | Not recommended until separate approved dependency task |

---

## 6. Primary Recommendation

Primary future install path:

- Target only:
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310`.
- Use direct Conda invocation to run the target env's Python/pip.
- Use pip wheels from PyTorch `cu128`.
- Pin `torch` and `torchaudio` to the same tested PyTorch family first.
- Do not install `torchvision` unless a later dependency review proves it is
  required.
- Do not install `torchcodec` in the first CUDA verification step unless that
  future task explicitly widens scope to TorchCodec; if widened, pin TorchCodec
  to the torch family instead of leaving it floating.
- Do not install CUDA Toolkit or modify system CUDA.
- Do not run GPT-SoVITS `install.ps1`.

Recommended primary family:

```text
torch==2.7.0
torchaudio==2.7.0
CUDA wheel index: https://download.pytorch.org/whl/cu128
```

Why:

- GPT-SoVITS README records a tested CUDA `12.8` / PyTorch `2.7.0` environment.
- PyTorch official previous-version commands include CUDA `12.8` wheels for
  `torch==2.7.0` and matching `torchaudio==2.7.0`.
- Python 3.10 is supported.
- This avoids unpinned upstream drift.

Fallback path:

```text
torch==2.7.0
torchaudio==2.7.0
CUDA wheel index: https://download.pytorch.org/whl/cu126
```

CPU fallback only if CUDA wheels cannot be installed or `torch.cuda.is_available()`
does not pass after a clean CUDA attempt:

```text
torch==2.7.0
torchaudio==2.7.0
CPU wheel index: https://download.pytorch.org/whl/cpu
```

CPU fallback does not satisfy the GPU install goal.

---

## 7. Proposed Future Commands

These commands are a proposal only.

```text
NOT APPROVED / DO NOT RUN YET
```

Primary PyTorch/CUDA 12.8 install proposal:

```powershell
$CondaExe = "C:\ProgramData\anaconda3\Scripts\conda.exe"
$TargetEnv = "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310"

& $CondaExe run --prefix $TargetEnv python -m pip install `
  torch==2.7.0 torchaudio==2.7.0 `
  --index-url https://download.pytorch.org/whl/cu128
```

Optional TorchCodec command only if a future task explicitly includes it:

```powershell
NOT APPROVED / DO NOT RUN YET

& $CondaExe run --prefix $TargetEnv python -m pip install `
  torchcodec==0.5 `
  --index-url https://download.pytorch.org/whl/cu128
```

CUDA 12.6 fallback:

```powershell
NOT APPROVED / DO NOT RUN YET

& $CondaExe run --prefix $TargetEnv python -m pip install `
  torch==2.7.0 torchaudio==2.7.0 `
  --index-url https://download.pytorch.org/whl/cu126
```

CPU fallback:

```powershell
NOT APPROVED / DO NOT RUN YET

& $CondaExe run --prefix $TargetEnv python -m pip install `
  torch==2.7.0 torchaudio==2.7.0 `
  --index-url https://download.pytorch.org/whl/cpu
```

Post-install verification commands for a future approved install:

```powershell
NOT APPROVED / DO NOT RUN YET

& $CondaExe run --prefix $TargetEnv python -c "import torch; print(torch.__version__); print(torch.version.cuda); print(torch.cuda.is_available()); print(torch.cuda.device_count()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NO CUDA')"

& $CondaExe list --prefix $TargetEnv

& $CondaExe run --prefix $TargetEnv python -m pip freeze
```

Rollback strategy if installation fails:

1. Do not modify Anaconda base.
2. Do not run repo install scripts.
3. Record the failed command and output in an external lab report.
4. Prefer removing only the target prefix environment after explicit approval:
   `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310`.
5. Recreate the prefix env from Anaconda only after a separate approval.
6. Do not clean global package caches unless separately approved.

---

## 8. Safe Future Dependency Order

Recommended future order:

1. Verify Dragon Pet AI repo status and keep unrelated local files unstaged.
2. Verify existing Anaconda and target prefix env.
3. Install PyTorch/Torchaudio CUDA only.
4. Verify `torch` imports.
5. Verify expected torch version.
6. Verify `torch.cuda.is_available() == True`.
7. Verify device count and device name.
8. Record `conda list` and `pip freeze` snapshots.
9. Stop.
10. Review GPT-SoVITS dependencies separately.
11. Only in a later approved task, install remaining GPT-SoVITS dependencies.
12. Keep model downloads, WebUI, inference, synthesis, and audio generation as
    separate approvals.

Do not combine PyTorch/CUDA installation with `install.ps1`,
`requirements.txt`, model downloads, or inference.

---

## 9. Future Install Success Criteria

A future TASK-TTS-004E3A PyTorch/CUDA install task should pass only if:

- `torch` imports in the target env.
- Torch version is the approved version.
- `torchaudio` imports in the target env.
- `torch.cuda.is_available() == True` for the CUDA path.
- CUDA device count is at least `1`.
- Device name includes `NVIDIA GeForce RTX 3070`.
- `torch.version.cuda` matches the approved wheel family expectation.
- No Anaconda base package install/update occurred.
- No Dragon Pet AI backend venv changed.
- No GPT-SoVITS dependency install occurred beyond the approved PyTorch family.
- No model download occurred.
- No WebUI/inference/synthesis/audio generation occurred.
- Package snapshot was recorded.

---

## 10. Rejection Criteria

Reject the proposed path if:

- It requires unsupported Python.
- It requires modifying Anaconda base.
- It requires replacing or globally installing system CUDA.
- It requires uncontrolled package upgrades.
- It requires running GPT-SoVITS `install.ps1`.
- It requires installing all GPT-SoVITS dependencies in the PyTorch-only task.
- It requires Docker, `cuda-nvcc`, `flash-attn`, or compiler setup in the first
  PyTorch/CUDA task.
- It is incompatible with Windows.
- It cannot keep packages isolated to the target prefix env.
- It fails to expose RTX 3070 through `torch.cuda`.
- It exceeds practical RTX 3070 8GB limits for inference-only use.
- Repository evidence becomes unclear or contradictory after refresh.

---

## 11. No-Install Confirmation

Confirmed for TASK-TTS-004E3:

- No PyTorch was installed.
- No CUDA Toolkit or CUDA runtime package was installed.
- No `torchvision`, `torchaudio`, or `torchcodec` was installed.
- No GPT-SoVITS dependency was installed.
- No `install.ps1`, `install.sh`, Docker build, WebUI, training, inference, or
  synthesis command was run.
- No model, dataset, or generated audio was downloaded or created.
- No Anaconda base change was made.
- No PATH, PowerShell profile, or registry change was made.
- No Dragon Pet AI runtime code changed.
- `/chat`, STT, Conversation Mode, Owner Voice Gate, schemas, playback, and
  auto-speaking behavior remain unchanged.

---

## 12. External Manifest

External manifest path:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E3_PYTORCH_CUDA_REVIEW.md
```

The external manifest is a lab report only. It must not be staged or committed
to Dragon Pet AI.

---

## 13. Recommended Next Task

```text
TASK-TTS-004E3A - GPT-SoVITS Lab PyTorch/CUDA Install
```

That task is not approved yet.
