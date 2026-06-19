# GPT-SoVITS Dependency Compatibility Review

**Task:** TASK-TTS-004E4
**Status:** TASK-TTS-004E6 DONE - GPT-SOVITS CHINESE TEXT DEPENDENCY REVIEW COMPLETE / INSTALL NOT APPROVED
**Date:** 2026-06-19
**Scope:** Read-only dependency compatibility review for the isolated
GPT-SoVITS lab. No package install, uninstall, dependency resolver run,
`install.ps1`, `install.sh`, requirements install, model download, WebUI,
training, inference, synthesis, audio generation, Dragon Pet AI runtime change,
`/chat` change, STT change, Conversation Mode change, Owner Voice change,
schema change, playback change, auto-speaking change, Anaconda base change,
PATH/profile/registry change, failed Miniconda change, backend venv change, or
GPT-SoVITS source change was performed.

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

Target environment:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310
Python 3.10.20
```

Protected installed packages:

```text
torch==2.7.0+cu128
torchaudio==2.7.0+cu128
torch.version.cuda=12.8
torch.cuda.is_available()=True
device=NVIDIA GeForce RTX 3070
```

Current `pip freeze` in the target env:

```text
filelock==3.29.0
fsspec==2026.4.0
Jinja2==3.1.6
MarkupSafe==3.0.3
mpmath==1.3.0
networkx==3.4.2
packaging==26.0
sympy==1.14.0
torch==2.7.0+cu128
torchaudio==2.7.0+cu128
typing_extensions==4.15.0
```

`numpy` remains absent. Importing torch still emits a non-blocking warning:

```text
UserWarning: Failed to initialize NumPy: No module named 'numpy'
```

GPT-SoVITS repository:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS
commit b2cff0cd0abd0ac134a16ae7a9695f88e8826104
```

`git status --short` in the GPT-SoVITS repo reported no changed files. Git also
emitted user-home ignore permission warnings; those warnings do not indicate
repository changes.

---

## 2. Files Inspected

Read-only dependency sources inspected:

| Path | Evidence |
|---|---|
| `requirements.txt` | Main Python requirements. Contains `numpy<2.0`, `librosa==0.10.2`, unpinned `torchaudio`, `onnxruntime-gpu` on x86_64/AMD64, `funasr==1.0.27`, `transformers>=4.43,<=4.50`, `peft<0.18.0`, `torchmetrics<=1.5`, `pydantic<=2.10.6`, `ctranslate2>=4.0,<5`, `av>=11`, `fastapi[standard]>=0.115.2`, `gradio<5`, and `--no-binary=opencc`. |
| `extra-req.txt` | Contains only `faster-whisper`. Official install scripts install it with `--no-deps`. |
| `install.ps1` | Windows install script. Installs `ffmpeg cmake` through Conda, downloads pretrained/G2PW/NLTK/OpenJTalk assets, installs unpinned `torch torchcodec` from `cu128`, `cu126`, or `cpu`, then installs `extra-req.txt --no-deps` and full `requirements.txt`. Not safe for a staged dependency task. |
| `install.sh` | Linux/macOS install script. Adds build tools, `ffmpeg cmake make unzip`, may fall back from CUDA to CPU, installs unpinned `torch torchcodec`, installs requirements, downloads model/dictionary assets, and has ROCm runtime mutation. Not safe for Windows staged review. |
| `Dockerfile` | Uses `xxxxrt666/torch-base:cu${CUDA_VERSION}-${TORCH_BASE}`, copies requirements and runs `Docker/install_wrapper.sh`. Not applicable to the Windows Conda prefix. |
| `docker-compose.yaml` | Defines `CU126`, `CU128`, and Lite services with `runtime: nvidia` and `shm_size: "16g"`. Docker-only path. |
| `docker_build.sh` | Accepts only CUDA `12.6` or `12.8`; builds images with Docker. |
| `Docker/install_wrapper.sh` | Calls `install.sh --device CU<CUDA_VERSION> --source HF`, then purges caches and shows torch. |
| `Docker/miniforge_install.sh` | Installs Miniforge, Python `3.12`, build tools, `torch torchcodec`, `cuda-nvcc`, `flash-attn` from a custom index, and purges caches. Linux/Docker-only and too broad. |
| `GPT_SoVITS/BigVGAN/requirements.txt` | BigVGAN-specific requirements include bare `torch`, unpinned `numpy`, `librosa>=0.8.1`, `soundfile`, `matplotlib`, `pesq`, `auraloss`, `nnAudio`, `ninja`, and `huggingface_hub>=0.23.4`. Training/optional path, not foundation install. |
| `README.md` | Documents Python `3.10-3.12`, tested PyTorch/CUDA combinations including PyTorch `2.7.0` with CUDA `12.8`, Windows command `install.ps1 --Device <CU126|CU128|CPU>`, manual `pip install -r` path, and separate ffmpeg guidance. |
| `go-webui.ps1` / `go-webui.bat` | Integrated-package launchers that prepend `runtime` to PATH and run bundled `runtime\python.exe`. Not applicable to the isolated Conda env and should not be used. |

Absent at repo root:

- `pyproject.toml`
- `setup.py`
- `environment.yml`
- `environment.yaml`
- constraints file

---

## 3. Dependency Inventory

### Core Runtime / Foundation

| Package | Source | Proposed handling |
|---|---|---|
| `numpy<2.0` | `requirements.txt` | Pin to `numpy==1.26.4` first. This satisfies `<2.0`, has Windows cp310 metadata evidence, and fixes the current torch warning without entering NumPy 2.x compatibility risk. |
| `scipy` | `requirements.txt`, BigVGAN | Pin to `scipy==1.11.4` first. Windows cp310 wheel metadata was verified. Fallback `1.12.0` also has Windows cp310 metadata. |
| `tqdm`, `chardet`, `PyYAML`, `psutil` | `requirements.txt` | Low-risk foundation utilities. Install after protected constraints and verify import. |
| `cn2an`, `pypinyin`, `jieba`, `wordsegment`, `split-lang`, `fast_langdetect` | `requirements.txt` | Text/language utilities. Keep out of the first numeric-only foundation group unless the next task explicitly widens Group A. |
| `jieba_fast` | `requirements.txt` | Native risk. PyPI latest metadata showed source distribution only, no Windows cp310 wheel. Defer. |
| `opencc` with `--no-binary=opencc` | `requirements.txt` | High Windows risk if using official file because it forces source build. PyPI metadata showed Windows cp310 wheels exist for OpenCC/opencc releases, but official `--no-binary` disables them. Use a lab-local copied requirement without `--no-binary` only after approval. |

### Audio / Codec

| Package / tool | Source | Proposed handling |
|---|---|---|
| `librosa==0.10.2` | `requirements.txt` | Install in Group B after NumPy/SciPy. PyPI metadata showed a pure Python wheel. |
| `soundfile` | BigVGAN requirements and code imports | Install in Group B. PyPI metadata showed pure Python wheel metadata, but it still needs runtime audio backend validation after install. |
| `ffmpeg-python` | `requirements.txt` | Python wrapper only; does not provide `ffmpeg.exe`. Install in Group B or D depending on media-output scope. |
| `av>=11` | `requirements.txt` | Defer until audio/codec group. PyPI metadata for exact `av==11.0.0` showed source-only for Windows cp310, while latest `17.1.0` showed a Windows cp310 wheel. Do not allow source build; choose a wheel-bearing version only after approval. |
| system `ffmpeg.exe` | README and install scripts | Required for non-WAV media paths and ffmpeg subprocess output. Do not install during foundation. The official scripts use Conda or manual `ffmpeg.exe` placement; both are out of scope. |
| TorchCodec | `install.ps1`, `install.sh`, Docker scripts | Not in `requirements.txt`; official install scripts install it with torch. Defer. Installing it now would widen scope and could introduce torch/codec version coupling. |
| torchaudio codec behavior | Existing env | `torchaudio==2.7.0+cu128` is already protected. Basic WAV loading may work after NumPy/audio packages, but codec behavior must be verified without replacing torchaudio. |

### ML / GPU-Sensitive

| Package | Source | Risk |
|---|---|---|
| `torch` | Installed already; BigVGAN bare requirement; install scripts | Protected. Do not let resolver replace it. |
| `torchaudio` | Installed already; `requirements.txt` bare requirement | Protected. Bare requirement should be satisfied by installed `2.7.0+cu128`; validate after each future group. |
| `torchvision` | Not required by inspected files | Do not install unless a later evidence-backed task requires it. |
| `torchcodec` | Install scripts only | Defer. |
| `onnxruntime-gpu` | `requirements.txt` on x86_64/AMD64 | Defer and pin. PyPI metadata showed `1.18.1` has Windows cp310 wheel evidence; latest `1.27.0` did not show Windows cp310 wheel evidence in this review. |
| `ctranslate2>=4.0,<5` | `requirements.txt` | Defer to model/runtime. PyPI metadata showed Windows cp310 wheels for `4.6.0` and `4.8.0`. |
| `transformers>=4.43,<=4.50` | `requirements.txt` | Pin to `transformers==4.50.0` in model/runtime group. Pure Python wheel metadata was verified. |
| `peft<0.18.0` | `requirements.txt` | Pin to `peft==0.17.1` in model/runtime group. |
| `pytorch-lightning>=2.4`, `torchmetrics<=1.5` | `requirements.txt` | Training/model infra risk. Defer; pin `torchmetrics==1.5.0` if installed. |
| `x_transformers`, `rotary_embedding_torch` | `requirements.txt` | Model architecture deps. Defer to model/runtime. |
| `funasr==1.0.27`, `modelscope`, `faster-whisper` | `requirements.txt`, `extra-req.txt` | ASR/model download adjacent. Defer; extra-req should continue to use `--no-deps` only if a later task proves its transitive dependencies are already controlled. |
| `flash-attn` | Docker Miniforge script only | Do not install on Windows. PyPI metadata showed source distribution only in this review. |
| `xformers`, `triton`, `deepspeed`, `faiss`, `bitsandbytes` | Not in inspected main requirements | Do not install. |

### Native-Build / Windows-Risk

Highest-risk items for Windows Python 3.10:

- `opencc` because the official `requirements.txt` uses `--no-binary=opencc`.
- `pyopenjtalk>=0.4.1` because PyPI metadata for `0.4.1` showed source-only.
- `jieba_fast` because PyPI metadata showed source-only.
- `pesq` from BigVGAN because PyPI metadata showed source-only.
- `flash-attn` from Docker Miniforge because PyPI metadata showed source-only.
- `av==11.0.0` if resolver chooses it, because exact metadata showed
  source-only for Windows cp310; a newer wheel-bearing version must be selected
  explicitly if this dependency is approved.

### WebUI / Optional

WebUI/API packages:

- `gradio<5`
- `fastapi[standard]>=0.115.2`
- `uvicorn` as part of the API server stack
- `pydantic<=2.10.6`

These are not required for the first foundation install. Keep them in Group D
because they bring many web/server dependencies and do not prove model inference
readiness by themselves.

Training/optional packages:

- `tensorboard`
- `pytorch-lightning`
- `torchmetrics`
- BigVGAN `matplotlib`, `pesq`, `auraloss`, `nnAudio`, `ninja`
- Docker-only `flash-attn`

Keep these out of foundation and out of first standalone inference work unless
training or BigVGAN-specific validation is explicitly approved.

---

## 4. Torch / Torchaudio Conflict Analysis

The current torch stack is protected:

```text
torch==2.7.0+cu128
torchaudio==2.7.0+cu128
```

Conflict evidence:

- `requirements.txt` has bare `torchaudio`, which can be satisfied by the
  installed package but could become resolver-controlled if run broadly.
- `GPT_SoVITS/BigVGAN/requirements.txt` has bare `torch`.
- `install.ps1` and `install.sh` install unpinned `torch torchcodec` from
  `cu128`, `cu126`, `rocm6.2`, or `cpu` indexes depending on script branch.
- `install.sh` can fall back from CUDA to CPU when it does not detect
  `nvidia-smi`.
- Docker/Miniforge scripts install unpinned `torch torchcodec` and, in one
  path, `flash-attn`.

Rejected approaches:

- Do not run `pip install -r requirements.txt` directly.
- Do not run `install.ps1`, `install.sh`, Docker scripts, or BigVGAN
  requirements directly.
- Do not install TorchCodec in the foundation task.
- Do not allow CPU fallback or cu126 fallback in a cu128-protected task.

Protected strategy:

1. Create a lab-local constraints file outside the GPT-SoVITS repo, for
   example:

   ```text
   F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\constraints\TASK-TTS-004E4A_protected_torch_cu128_constraints.txt
   ```

2. Put only approved pins in that file:

   ```text
   torch==2.7.0+cu128
   torchaudio==2.7.0+cu128
   numpy==1.26.4
   scipy==1.11.4
   ```

3. Use explicit package lists, not official full requirements.
4. Use `--upgrade-strategy only-if-needed`.
5. After each group, verify torch/torchaudio/CUDA before continuing.
6. If pip proposes replacing torch or torchaudio, stop.

---

## 5. NumPy Recommendation

Repository evidence:

- `requirements.txt` pins `numpy<2.0`.
- BigVGAN requirements use bare `numpy`.
- Current torch import warns because NumPy is missing.

PyPI metadata evidence checked on 2026-06-19:

- `numpy==1.26.4` has Windows cp310 win_amd64 wheel metadata.
- `numpy` latest metadata in this review was `2.4.6`, but this violates
  GPT-SoVITS `numpy<2.0`.
- `scipy==1.11.4` and `scipy==1.12.0` have Windows cp310 win_amd64 wheel
  metadata.
- `librosa==0.10.2` has pure Python wheel metadata.

Primary recommendation:

```text
numpy==1.26.4
scipy==1.11.4
```

Reason:

- Satisfies GPT-SoVITS `numpy<2.0`.
- Avoids NumPy 2.x compatibility churn.
- Has Windows cp310 metadata evidence.
- Should resolve the current torch missing-NumPy warning.

Fallback:

```text
numpy==1.26.4
scipy==1.12.0
```

Use fallback only if `scipy==1.11.4` conflicts with a later explicitly approved
dependency group.

Do not install NumPy in TASK-TTS-004E4.

---

## 6. Ffmpeg / Codec Requirements

Separate concerns:

- `ffmpeg-python` is only a Python wrapper and does not install `ffmpeg.exe`.
- system `ffmpeg.exe` is separately required by code paths that spawn `ffmpeg`
  for encoded media, especially non-WAV media output.
- `av` is a Python audio/video binding with native wheels or source-build risk.
- TorchCodec is not in `requirements.txt`; it appears only in official install
  scripts.
- torchaudio is already installed and protected, but codec coverage must be
  validated after audio dependencies, without replacing torchaudio.

Requirement by stage:

| Use case | Need |
|---|---|
| Basic dependency imports | No system ffmpeg. Need NumPy/SciPy utilities first. |
| Standalone text-to-speech inference with WAV-only reference/output | Likely needs NumPy, librosa, soundfile, torchaudio, model/runtime packages, and model files. System ffmpeg may be avoidable only for strict WAV-only paths. |
| Loading reference audio | Needs torchaudio/librosa/soundfile path validation. Non-WAV formats may need ffmpeg-backed codecs. |
| WebUI | Needs Gradio/FastAPI plus more complete audio stack. |
| Training / preprocessing | More likely to need ffmpeg, dataset slicing, ASR, UVR5, and BigVGAN/training dependencies. |

Recommendation:

- Do not install system ffmpeg in foundation.
- Do not install TorchCodec in foundation.
- Defer `av` until Group B and require wheel-only install behavior.
- Treat non-WAV media as out of scope until a separate audio/codec task.

---

## 7. Windows Wheel / Build Risk Notes

Read-only PyPI JSON metadata checks were performed for high-risk packages. No
wheels were downloaded and no packages were installed.

Evidence summary:

| Package / version | Metadata result | Review decision |
|---|---|---|
| `numpy==1.26.4` | Windows cp310 wheel present | Safe foundation candidate. |
| `scipy==1.11.4` | Windows cp310 wheel present | Safe foundation candidate. |
| `scipy==1.12.0` | Windows cp310 wheel present | Fallback candidate. |
| `librosa==0.10.2` | Pure Python wheel present | Group B after NumPy/SciPy. |
| `funasr==1.0.27` | Pure Python wheel present | Defer because model/ASR adjacent. |
| `pydantic==2.10.6` | Pure Python wheel present | Web/API group with FastAPI. |
| `transformers==4.50.0` | Pure Python wheel present | Group C model/runtime. |
| `peft==0.17.1` | Pure Python wheel present | Group C model/runtime. |
| `torchmetrics==1.5.0` | Pure Python wheel present | Defer; training/model infra. |
| `av==11.0.0` | Source-only metadata for Windows cp310 | Avoid exact 11.0.0; choose wheel-bearing version only after approval. |
| latest `av==17.1.0` | Windows cp310 wheel present | Candidate for later audio group, but verify compatibility separately. |
| `pyopenjtalk==0.4.1` | Source-only metadata | Native-build risk; defer. |
| `opencc==1.1.9` / `1.3.1` | Windows cp310 wheels present | Wheel exists, but official `--no-binary=opencc` forces source build; use lab-local override only after approval. |
| `ctranslate2==4.6.0` / `4.8.0` | Windows cp310 wheels present | Model/runtime candidate; pin before install. |
| `onnxruntime-gpu==1.18.1` | Windows cp310 wheel present | Candidate if GPU ONNX path is required. |
| latest `onnxruntime-gpu==1.27.0` | No Windows cp310 wheel found in this metadata check | Do not allow latest resolver choice. Pin or defer. |
| `torchcodec==0.14.0` | Windows cp310 wheel present | Defer because it widens codec/torch coupling. |
| `flash-attn==2.8.3.post1` | Source-only metadata | Do not install on Windows. |
| `jieba-fast==0.53` | Source-only metadata | Native-build risk; defer. |
| `pesq==0.0.4` | Source-only metadata | BigVGAN/training-only native risk; defer. |
| `faster-whisper==1.2.1` | Pure Python wheel present | Defer; official script installs `--no-deps`, so transitive dependency control must be reviewed first. |

---

## 8. Staged Install Groups

Do not combine these groups into one command.

### Group A - Safe Foundation

Purpose:

- Resolve missing NumPy warning.
- Establish numeric/util foundation.
- Keep torch/torchaudio protected.
- Avoid model, audio codec, WebUI, and native-build packages.

Proposed packages:

```text
numpy==1.26.4
scipy==1.11.4
tqdm
PyYAML
chardet
psutil
```

Risk: low/medium.

Verification after install:

- `pip freeze`
- import `numpy`, `scipy`, `yaml`, `tqdm`, `chardet`, `psutil`
- verify `torch==2.7.0+cu128`
- verify `torchaudio==2.7.0+cu128`
- verify CUDA available and RTX 3070 detected
- verify minimal CUDA tensor still works

Rollback strategy:

- Stop immediately if torch/torchaudio replacement is proposed or detected.
- Restore env from the pre-install package snapshot only after explicit approval.
- If only Group A failed before changes, keep logs and do not continue.

### Group B - Audio / Text Runtime

Purpose:

- Add basic text and audio utilities required before standalone TTS import
  probes.

Proposed packages:

```text
librosa==0.10.2
soundfile
ffmpeg-python
cn2an
pypinyin
jieba
wordsegment
split-lang
fast_langdetect==1.0.1
opencc==1.3.1
```

Defer from Group B unless separately approved:

```text
av
pyopenjtalk
jieba_fast
system ffmpeg.exe
TorchCodec
```

Risk: medium, because language/audio packages expand transitive dependencies.

Verification:

- import all installed Group B packages
- verify WAV-only audio library import paths
- re-verify torch/torchaudio/CUDA
- no audio generation

Rollback:

- Stop on native-build attempt.
- Stop on torch/torchaudio resolver changes.
- Keep logs and package snapshots.

### Group C - Model / Runtime

Purpose:

- Add model/runtime libraries for later import-only probes.

Proposed packages:

```text
transformers==4.50.0
peft==0.17.1
sentencepiece
huggingface-hub
modelscope
rotary_embedding_torch
x_transformers
ctranslate2==4.8.0
```

Conditional/deferred:

```text
onnxruntime-gpu==1.18.1
funasr==1.0.27
faster-whisper==1.2.1
```

Risk: medium/high because model packages can pull large transitive dependency
sets and may attempt model-cache behavior later.

Verification:

- import installed packages only
- no model download
- no model load
- no inference
- re-verify torch/torchaudio/CUDA

Rollback:

- Stop on dependency resolver attempting torch/torchaudio changes.
- Stop on package set becoming broader than approved.

### Group D - WebUI / API

Purpose:

- Add server/UI stack only after dependency import layers pass.

Proposed packages:

```text
gradio==4.44.1
fastapi[standard]==0.115.14
pydantic==2.10.6
uvicorn==0.35.0
```

Risk: medium/high due many transitive web dependencies.

Verification:

- import `gradio`, `fastapi`, `pydantic`, `uvicorn`
- no server start
- no WebUI
- re-verify torch/torchaudio/CUDA

Rollback:

- Stop on pydantic/FastAPI resolver conflicts.
- Stop on unapproved server startup or asset download.

### Group E - Training / Optional Acceleration

Purpose:

- Training, BigVGAN, optional speedups, ASR/UVR5-heavy workflows.

Packages to defer:

```text
tensorboard
pytorch-lightning
torchmetrics==1.5.0
matplotlib
pesq
auraloss
nnAudio
ninja
av
pyopenjtalk
jieba_fast
torchcodec
flash-attn
onnxruntime-gpu
funasr
faster-whisper
```

Risk: high.

Verification:

- separate task only
- import-only first
- no training
- no ASR model download
- no UVR5 model download
- no WebUI

Rollback:

- Do not start Group E without a stronger environment rollback strategy.

---

## 9. Proposed Future Commands

These commands are documentation only.

```text
NOT APPROVED / DO NOT RUN YET
```

Create lab-local folders:

```powershell
New-Item -ItemType Directory -Force -Path "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\constraints"
New-Item -ItemType Directory -Force -Path "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports"
New-Item -ItemType Directory -Force -Path "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\pip-cache"
```

Create constraints file:

```powershell
@"
torch==2.7.0+cu128
torchaudio==2.7.0+cu128
numpy==1.26.4
scipy==1.11.4
"@ | Set-Content -Encoding UTF8 -Path "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\constraints\TASK-TTS-004E4A_protected_torch_cu128_constraints.txt"
```

Capture before snapshot:

```powershell
& "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe" -m pip freeze |
  Set-Content -Encoding UTF8 "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E4A_PIP_BEFORE.txt"
```

Dry-run Group A first if pip supports it in the target pip:

```powershell
& "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe" -m pip install --dry-run `
  --extra-index-url "https://download.pytorch.org/whl/cu128" `
  --constraint "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\constraints\TASK-TTS-004E4A_protected_torch_cu128_constraints.txt" `
  --cache-dir "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\pip-cache" `
  --upgrade-strategy only-if-needed `
  "numpy==1.26.4" "scipy==1.11.4" "tqdm" "PyYAML" "chardet" "psutil"
```

Install Group A only after explicit approval:

```powershell
& "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe" -m pip install `
  --extra-index-url "https://download.pytorch.org/whl/cu128" `
  --constraint "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\constraints\TASK-TTS-004E4A_protected_torch_cu128_constraints.txt" `
  --cache-dir "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\pip-cache" `
  --upgrade-strategy only-if-needed `
  --log "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E4A_FOUNDATION_INSTALL.log" `
  "numpy==1.26.4" "scipy==1.11.4" "tqdm" "PyYAML" "chardet" "psutil"
```

Post-install verification:

```powershell
& "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe" -c "import numpy, scipy, yaml, tqdm, chardet, psutil, torch, torchaudio; print('numpy', numpy.__version__); print('scipy', scipy.__version__); print('torch', torch.__version__, torch.version.cuda, torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NO CUDA'); print('torchaudio', torchaudio.__version__)"
```

Capture after snapshot:

```powershell
& "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe" -m pip freeze |
  Set-Content -Encoding UTF8 "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E4A_PIP_AFTER.txt"
```

Do not include model downloads, WebUI startup, inference, synthesis, audio
generation, `install.ps1`, `install.sh`, or full requirements install.

---

## 10. First Dependency Install Success Criteria

TASK-TTS-004E4A should pass only if all are true:

- Approved packages install only into
  `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310`.
- `torch` remains `2.7.0+cu128`.
- `torchaudio` remains `2.7.0+cu128`.
- `torch.version.cuda` remains `12.8`.
- `torch.cuda.is_available()` remains true.
- RTX 3070 remains detected.
- Minimal CUDA tensor still works.
- Installed Group A imports pass.
- Before/after package snapshots are recorded.
- Install log is recorded.
- No models, datasets, or audio artifacts are downloaded or generated.
- No WebUI, API server, inference, training, or synthesis starts.
- Anaconda base, PATH, PowerShell profile, registry, failed Miniconda,
  Dragon Pet AI runtime, backend venv, and GPT-SoVITS source remain unchanged.

---

## 11. Rejection Criteria

Reject or stop if any of these occur:

- Pip proposes or performs torch replacement.
- Pip proposes or performs torchaudio replacement.
- Resolver selects CPU-only torch or a non-cu128 build.
- Resolver pulls TorchCodec without explicit approval.
- Resolver selects `onnxruntime-gpu` latest without Windows cp310 wheel
  evidence.
- Resolver attempts source build for `opencc`, `pyopenjtalk`, `jieba_fast`,
  `pesq`, `flash-attn`, or `av`.
- NumPy constraints contradict `numpy<2.0`.
- Dependency scripts try to download models, NLTK data, OpenJTalk dictionaries,
  G2PW, UVR5, or pretrained weights.
- System-wide CUDA, PATH, registry, PowerShell profile, Anaconda base, or failed
  Miniconda modifications are required.
- The package set becomes broader than the approved staged group.
- Requirements are unclear for commit
  `b2cff0cd0abd0ac134a16ae7a9695f88e8826104`.

---

## 12. Final Verdict

```text
DONE - GPT-SOVITS DEPENDENCY COMPATIBILITY REVIEW COMPLETE / DEPENDENCY INSTALL NOT APPROVED
```

Foundation dependency follow-up:

```text
TASK-TTS-004E4A - DONE - GPT-SOVITS FOUNDATION DEPENDENCIES VERIFIED / AUDIO AND MODEL DEPENDENCIES NOT INSTALLED
```

Primary first install group:

```text
Group A - Safe Foundation
numpy==1.26.4
scipy==1.11.4
tqdm
PyYAML
chardet
psutil
```

Fallback:

```text
Group A fallback keeps numpy==1.26.4 and uses scipy==1.12.0 only if scipy==1.11.4 conflicts.
```

Confirmed not performed:

- No package install or uninstall.
- No requirements install.
- No `install.ps1` / `install.sh`.
- No model, dataset, pretrained weight, G2PW, NLTK, OpenJTalk, or UVR5 download.
- No WebUI, API server, training, inference, synthesis, or audio generation.
- No torch/torchaudio modification.
- No NumPy install.
- No Anaconda base, PATH, profile, registry, failed Miniconda, backend venv,
  Dragon Pet AI runtime, `/chat`, STT, Conversation Mode, Owner Voice, schema,
  playback, or auto-speaking change.

TASK-TTS-004E4A later installed only this Group A foundation set with
`scipy==1.11.4`, no SciPy fallback, no torch/torchaudio replacement, and no
audio/model dependency group. See
`docs/TTS_GPT_SOVITS_FOUNDATION_DEPENDENCY_INSTALL.md`.

TASK-TTS-004E5 later completed the audio/text dependency compatibility review
without installing anything. TASK-TTS-004E5A later installed and verified only
the approved B1 WAV/audio dependency group.

Recommended next task, not approved yet:

```text
TASK-TTS-004E6 - GPT-SoVITS Chinese Text Dependency Review
```

---

## TASK-TTS-004E6 Chinese Text Dependency Review

**Status:** TASK-TTS-004E6 DONE - GPT-SOVITS CHINESE TEXT DEPENDENCY REVIEW COMPLETE / INSTALL NOT APPROVED
**Date:** 2026-06-20
**Evidence:** `docs/TTS_GPT_SOVITS_CHINESE_TEXT_DEPENDENCY_REVIEW.md`; external manifest `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E6_CHINESE_TEXT_DEPENDENCY_REVIEW.md`.

TASK-TTS-004E6 inspected GPT-SoVITS commit `b2cff0cd0abd0ac134a16ae7a9695f88e8826104` Chinese normalization, segmentation, pinyin/G2P, phoneme mapping, vendored G2PW, OpenCC, LangSegmenter, requirements, and model/dictionary asset boundaries read-only. No install was approved or performed.

Key conclusion: no safe useful Chinese text install group is ready yet. `jieba_fast` is imported unconditionally and PyPI `jieba-fast==0.53` is source-only; the current v2 Chinese path initializes G2PW at import time and can download model assets if missing; OpenCC needs a separate API/build-risk probe. `cn2an` and `pypinyin` are low-risk wheel candidates, but installing only them would not make the current Chinese path pass.

Selected next task, not approved yet: `TASK-TTS-004E6A - Chinese Text Import Graph Probe`. Do not mark Chinese inference ready.
