# GPT-SoVITS Foundation Dependency Install

**Task:** TASK-TTS-004E4A
**Status:** DONE - GPT-SOVITS FOUNDATION DEPENDENCIES VERIFIED / AUDIO AND MODEL DEPENDENCIES NOT INSTALLED
**Date:** 2026-06-19
**Scope:** Install only the approved foundation package group into the isolated
external GPT-SoVITS lab environment. No GPT-SoVITS full requirements,
`install.ps1`, ffmpeg, PyAV, TorchCodec, librosa, soundfile, transformers,
WebUI/API packages, training packages, models, datasets, inference, synthesis,
audio generation, Dragon Pet AI runtime change, `/chat` change, STT change,
Conversation Mode change, Owner Voice change, schema change, playback change,
auto-speaking change, Anaconda base change, PATH/profile/registry change,
backend venv change, or GPT-SoVITS source change was performed.

---

## 1. Target

Dragon Pet AI project:

```text
F:\RickHSIAO\Python\dragon-pet-ai
```

Target environment:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe
Python 3.10.20
pip 26.1.1
```

GPT-SoVITS repository:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS
origin: https://github.com/RVC-Boss/GPT-SoVITS.git
commit: b2cff0cd0abd0ac134a16ae7a9695f88e8826104
status: no changed files; git emitted user-home ignore permission warnings only
```

---

## 2. Pre-install State

Approved foundation package pre-state:

```text
numpy: absent
scipy: absent
tqdm: absent
yaml/PyYAML: absent
chardet: absent
psutil: absent
```

Protected torch stack before install:

```text
torch=2.7.0+cu128
torchaudio=2.7.0+cu128
torch.version.cuda=12.8
cuda_available=True
device_count=1
device_name=NVIDIA GeForce RTX 3070
```

Before snapshots:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E4A_PIP_BEFORE.txt
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E4A_CONDA_BEFORE.txt
```

Pre-install `pip check`:

```text
No broken requirements found.
```

---

## 3. Constraints And Install

Constraints file:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\constraints\TASK-TTS-004E4A_PROTECTED_TORCH_CU128.txt
```

Contents:

```text
torch==2.7.0+cu128
torchaudio==2.7.0+cu128
numpy==1.26.4
scipy==1.11.4
```

Package index:

```text
https://pypi.org/simple
```

Exact install command:

```powershell
& "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe" -m pip install `
  --index-url "https://pypi.org/simple" `
  --constraint "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\constraints\TASK-TTS-004E4A_PROTECTED_TORCH_CU128.txt" `
  --only-binary=:all: `
  --disable-pip-version-check `
  --no-input `
  "numpy==1.26.4" `
  "scipy==1.11.4" `
  "tqdm" `
  "PyYAML" `
  "chardet" `
  "psutil"
```

Install log:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E4A_FOUNDATION_INSTALL.log
```

Install result:

```text
INSTALL_EXIT_CODE=0
```

The first attempt was interrupted by the command timeout while downloading
SciPy and did not produce a pip success/failure result. The same approved
command was rerun with a longer timeout. No SciPy fallback was attempted.

Pip warning:

- `f2py.exe`, `chardetect.exe`, and `tqdm.exe` were installed under the target
  env `Scripts` directory, which is not on PATH. PATH was not modified.

---

## 4. Installed Package Verification

Installed approved packages:

```text
numpy=1.26.4
scipy=1.11.4
tqdm=4.68.3
PyYAML/yaml=6.0.3
chardet=7.4.3
psutil=7.2.2
```

Added required transitive dependency:

```text
colorama=0.4.6
```

Import verification passed:

```text
import numpy, scipy, tqdm, yaml, chardet, psutil
```

NumPy/Torch interop:

```text
numpy_torch_shape=(2,)
numpy_torch_sum=3.0
```

Protected torch stack after install:

```text
torch=2.7.0+cu128
torchaudio=2.7.0+cu128
torch.version.cuda=12.8
cuda_available=True
device_count=1
device_name=NVIDIA GeForce RTX 3070
```

CUDA tensor verification:

```text
cuda_tensor_device=cuda:0
cuda_tensor_value=2.0
```

After snapshots:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E4A_PIP_AFTER.txt
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E4A_CONDA_AFTER.txt
```

Post-install `pip check`:

```text
No broken requirements found.
```

---

## 5. Forbidden Package Check

All checked forbidden/deferred packages were absent:

```text
torchvision=False
xformers=False
triton=False
flash_attn=False
deepspeed=False
faiss=False
torchcodec=False
av=False
librosa=False
soundfile=False
transformers=False
tokenizers=False
gradio=False
fastapi=False
uvicorn=False
onnxruntime=False
onnxruntime_gpu=False
```

---

## 6. Base / PATH / Registry Assessment

Conda base:

```text
C:\ProgramData\anaconda3
```

`conda env list` succeeded with process-local UTF-8 and showed only the known
environments:

```text
base                     C:\ProgramData\anaconda3
my_study                 C:\Users\雪狼丸\.conda\envs\my_study
                         F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310
```

Persistent PATH assessment:

- User PATH remained `C:\Users\雪狼丸\AppData\Local\Microsoft\WindowsApps;`.
- Machine PATH remained the existing system/toolchain PATH and did not include
  the target GPT-SoVITS env.
- `Get-Command conda` returned no shell command.
- `Get-Command python -All` returned user-local Python entries, not the target
  GPT-SoVITS env.
- `$PROFILE` path:
  `C:\Users\雪狼丸\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`;
  it does not exist.

Registry read-only assessment:

- HKLM still shows the existing
  `Anaconda3 2025.12-2 (Python 3.13.9 64-bit)` uninstall entry.
- HKCU had no matching Anaconda/Miniconda/GPT-SoVITS uninstall entries.
- No registry write was performed.

---

## 7. Artifact Scan

External lab scan patterns:

```text
*.ckpt, *.pth, *.pt, *.safetensors, *.onnx, *.wav, *.mp3, *.flac
```

Findings:

- Existing `distutils-precedence.pth` files are Python package metadata, not
  model weights.
- The SciPy wheel includes packaged `scipy\io\tests\data\*.wav` test fixtures.
  These are dependency test data from the wheel, not generated audio and not
  project voice samples.
- No `.ckpt`, `.pt`, `.safetensors`, `.onnx`, generated `.wav`, `.mp3`, or
  `.flac` model/audio artifacts were created.

---

## 8. External Manifest

External manifest:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E4A_FOUNDATION_INSTALL.md
```

---

## 9. Boundaries Confirmed

Confirmed not performed:

- No `scipy==1.12.0` fallback.
- No torch or torchaudio replacement.
- No cu126 fallback and no CPU fallback.
- No full GPT-SoVITS requirements install.
- No GPT-SoVITS `install.ps1`, `install.sh`, Docker script, WebUI launcher, or
  BigVGAN requirements install.
- No ffmpeg, PyAV, TorchCodec, librosa, soundfile, transformers, WebUI/API, or
  training package group install.
- No model, dataset, pretrained weight, voice sample, or generated audio.
- No training, inference, WebUI, synthesis, playback, Pet playback, or
  auto-speaking.
- No Anaconda base install/update/remove.
- No PATH, PowerShell profile, registry, or `conda init` change.
- No backend venv change.
- No Dragon Pet AI runtime TTS/STT/Conversation/Owner Voice/schema change.
- Unrelated `docs/開啟方式.txt` was not edited, staged, or committed.

---

## 10. Final Verdict

```text
DONE - GPT-SOVITS FOUNDATION DEPENDENCIES VERIFIED / AUDIO AND MODEL DEPENDENCIES NOT INSTALLED
```

Recommended next task, not approved yet:

```text
TASK-TTS-004E5 - GPT-SoVITS Audio/Text Dependency Compatibility Review
```
