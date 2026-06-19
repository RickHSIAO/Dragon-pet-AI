# GPT-SoVITS PyTorch CUDA Install

**Task:** TASK-TTS-004E3A
**Status:** DONE - GPT-SOVITS LAB PYTORCH CUDA VERIFIED / GPT-SOVITS DEPENDENCIES NOT INSTALLED
**Date:** 2026-06-19
**Scope:** Install only the explicitly approved PyTorch CUDA package family into
the isolated GPT-SoVITS lab Conda prefix. No GPT-SoVITS dependency install,
`install.ps1`, ffmpeg, TorchCodec, model download, dataset download, training,
inference, WebUI, synthesis, audio generation, Dragon Pet AI runtime change,
`/chat` change, STT change, Conversation Mode change, Owner Voice change,
schema change, playback change, or auto-speaking change was performed.

---

## 1. Approval Scope

Approved packages:

```text
torch==2.7.0
torchaudio==2.7.0
```

Approved wheel index:

```text
https://download.pytorch.org/whl/cu128
```

Approved target prefix:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310
```

Approved package cache:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\pip-cache
```

Install log:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E3A_PYTORCH_INSTALL.log
```

Snapshots:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E3A_PIP_BEFORE.txt
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E3A_PIP_AFTER.txt
```

External manifest:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E3A_PYTORCH_CUDA_INSTALL.md
```

---

## 2. Main Repo Pre-flight

Dragon Pet AI repo:

```text
F:\RickHSIAO\Python\dragon-pet-ai
```

Pre-flight:

```text
git log -1 --oneline
337fd43 docs: review GPT-SoVITS PyTorch CUDA compatibility

git remote -v
origin  https://github.com/RickHSIAO/Dragon-pet-AI.git (fetch)
origin  https://github.com/RickHSIAO/Dragon-pet-AI.git (push)
```

`git status --short` showed only the expected unrelated local file before this
task:

```text
M docs/開啟方式.txt
```

That file was not edited, staged, or committed by this task.

---

## 3. Pre-install Environment

Target Python:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe
Python 3.10.20
3.10.20 | packaged by Anaconda, Inc. | (main, Jun 11 2026, 15:13:20) [MSC v.1942 64 bit (AMD64)]
```

Target pip:

```text
pip 26.1.1 from F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\lib\site-packages\pip (python 3.10)
```

Pre-install package state:

```text
torch= None
torchaudio= None
```

Pre-install `pip freeze`:

```text
packaging==26.0
```

Pre-install Conda package inventory contained the Python 3.10 base packages
only, including:

- `python 3.10.20`
- `pip 26.1.1`
- `setuptools 82.0.1`
- `wheel 0.47.0`
- `packaging 26.0`

---

## 4. Base Anaconda Baseline

Conda executable:

```text
C:\ProgramData\anaconda3\Scripts\conda.exe
```

Base path:

```text
C:\ProgramData\anaconda3
```

`conda env list` after installation still showed base plus the same known
environments, including the target prefix:

```text
base                     C:\ProgramData\anaconda3
my_study                 C:\Users\雪狼丸\.conda\envs\my_study
                         F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310
```

No command targeted Anaconda base for install, update, or removal.

---

## 5. GPU Evidence Before Install

`nvidia-smi` evidence:

```text
NVIDIA-SMI 610.47
KMD Version: 610.47
CUDA UMD Version: 13.3
GPU: NVIDIA GeForce RTX 3070
VRAM: 1745 MiB / 8192 MiB used at check time
Driver model: WDDM
```

Interpretation:

- `nvidia-smi` proves driver-level CUDA compatibility evidence.
- It does not prove PyTorch CUDA works; PyTorch CUDA was verified separately
  after installation.

---

## 6. Install Command

Process-local environment variables were set only for this install process:

- `PIP_CACHE_DIR=F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\pip-cache`
- `PYTHONUTF8=1`
- `PYTHONIOENCODING=utf-8`

They were restored after the command and were not persisted.

Exact install command:

```powershell
& "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe" -m pip install --index-url "https://download.pytorch.org/whl/cu128" "torch==2.7.0" "torchaudio==2.7.0"
```

Install result:

```text
INSTALL_EXIT_CODE=0
```

Installer output summary:

- Downloaded `torch-2.7.0+cu128-cp310-cp310-win_amd64.whl`.
- Downloaded `torchaudio-2.7.0+cu128-cp310-cp310-win_amd64.whl`.
- Installed approved packages and required transitive dependencies.
- Pip warned that `isympy.exe`, `torchfrtrace.exe`, and `torchrun.exe` were
  installed under the target env `Scripts` directory, which is not on PATH.
  PATH was not modified.

---

## 7. Installed Packages

`pip list` after install:

```text
filelock          3.29.0
fsspec            2026.4.0
Jinja2            3.1.6
MarkupSafe        3.0.3
mpmath            1.3.0
networkx          3.4.2
packaging         26.0
pip               26.1.1
setuptools        82.0.1
sympy             1.14.0
torch             2.7.0+cu128
torchaudio        2.7.0+cu128
typing_extensions 4.15.0
wheel             0.47.0
```

Added transitive dependencies:

- `filelock==3.29.0`
- `fsspec==2026.4.0`
- `Jinja2==3.1.6`
- `MarkupSafe==3.0.3`
- `mpmath==1.3.0`
- `networkx==3.4.2`
- `sympy==1.14.0`
- `typing_extensions==4.15.0`

Pre-existing package retained:

- `packaging==26.0`

No pip/Conda/Python/setuptools/wheel upgrade was requested.

---

## 8. Version Verification

Torch verification:

```text
torch_version= 2.7.0+cu128
torch_cuda_build= 12.8
```

Torchaudio verification:

```text
torchaudio_version= 2.7.0+cu128
```

Combined import check:

```text
2.7.0+cu128
2.7.0+cu128
```

Observed warning:

```text
UserWarning: Failed to initialize NumPy: No module named 'numpy'
```

Interpretation:

- `numpy` was not installed because it was not approved for this task.
- The warning did not block torch import, torchaudio import, CUDA detection, or
  the minimal CUDA tensor verification.
- Do not install `numpy` unless a later task explicitly approves dependency
  review/installation.

---

## 9. CUDA Verification

CUDA/device check:

```text
cuda_available= True
device_count= 1
device_name= NVIDIA GeForce RTX 3070
```

Minimal CUDA tensor test:

```text
cuda_tensor_device= cuda:0
cuda_tensor_value= 2.0
```

This was hardware verification only. No model was loaded and no inference was
performed.

---

## 10. Forbidden Package Check

Read-only import-spec check after install:

```text
{
  'torchvision': False,
  'xformers': False,
  'triton': False,
  'flash_attn': False,
  'deepspeed': False,
  'faiss': False,
  'torchcodec': False
}
```

Not installed:

- `torchvision`
- `xformers`
- `triton`
- `flash_attn`
- `deepspeed`
- `faiss`
- `torchcodec`
- GPT-SoVITS requirements
- ffmpeg
- CUDA Toolkit

---

## 11. PATH / Profile / Registry Assessment

PATH:

- User and Machine PATH were inspected read-only.
- `Get-Command conda` did not resolve `conda` from PATH.
- `Get-Command python -All` still resolved user-local Python entries.
- The target env `Scripts` directory was not added to PATH.

PowerShell profile:

```text
C:\Users\雪狼丸\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
exists: False
```

Registry:

- The existing Anaconda uninstall registry entry was inspected read-only.
- No registry modification command was run.

`conda init`:

- Not run.

Failed partial Miniconda:

- The failed partial Miniconda path was inspected read-only.
- It was not modified or cleaned.

---

## 12. GPT-SoVITS Repository Status

Repository:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS
```

Status:

```text
git status --short
<no changed files>
```

The command emitted sandbox git-ignore permission warnings for the user home
Git ignore path, but no GPT-SoVITS repo changes were reported.

Commit:

```text
b2cff0cd0abd0ac134a16ae7a9695f88e8826104
```

Remote:

```text
origin  https://github.com/RVC-Boss/GPT-SoVITS.git (fetch)
origin  https://github.com/RVC-Boss/GPT-SoVITS.git (push)
```

Not run:

- `install.ps1`
- `install.sh`
- dependency installers
- WebUI
- inference
- training
- synthesis

---

## 13. Artifact Scan

External lab scan for:

```text
*.ckpt, *.pth, *.pt, *.safetensors, *.onnx, *.wav, *.mp3, *.flac
```

Findings:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\pkgs-cache\setuptools-82.0.1-py310haa95532_0\Lib\site-packages\distutils-precedence.pth
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\miniconda3\pkgs\setuptools-82.0.1-py313haa95532_0\Lib\site-packages\distutils-precedence.pth
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\Lib\site-packages\distutils-precedence.pth
```

These `.pth` files are Python package metadata, not model weights.

No `.ckpt`, `.pt`, `.safetensors`, `.onnx`, `.wav`, `.mp3`, or `.flac`
artifacts were found.

---

## 14. Forbidden Actions Confirmation

Confirmed not performed:

- No cu126 fallback.
- No CPU fallback.
- No second PyTorch build.
- No GPT-SoVITS dependency install.
- No GPT-SoVITS `install.ps1`.
- No ffmpeg install.
- No TorchCodec install.
- No torchvision manual install.
- No xformers/triton/flash-attn/deepspeed/faiss install.
- No CUDA Toolkit or NVIDIA driver install.
- No Anaconda base install/update/remove.
- No PATH modification.
- No PowerShell profile modification.
- No registry modification.
- No `conda init`.
- No failed Miniconda modification.
- No model or pretrained weight download.
- No dataset download.
- No training.
- No inference.
- No WebUI.
- No synthesis or audio generation.
- No Dragon Pet AI runtime source change.
- No `/chat` wiring.
- No playback, Pet playback, or auto-speaking.
- No backend venv modification.

---

## 15. Final Verdict

```text
DONE - GPT-SOVITS LAB PYTORCH CUDA VERIFIED / GPT-SOVITS DEPENDENCIES NOT INSTALLED
```

Recommended next task, not approved yet:

```text
TASK-TTS-004E4 - GPT-SoVITS Dependency Compatibility Review
```
