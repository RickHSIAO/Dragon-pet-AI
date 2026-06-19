# GPT-SoVITS Audio/Text Dependency Compatibility Review

**Task:** TASK-TTS-004E5
**Status:** DONE - GPT-SOVITS AUDIO/TEXT DEPENDENCY REVIEW COMPLETE / INSTALL NOT APPROVED
**Date:** 2026-06-19
**Scope:** Read-only review for the next GPT-SoVITS audio and text-processing
dependency layer. No package install, uninstall, dependency resolver run,
`pip install`, `conda install`, `install.ps1`, `install.sh`, full requirements
install, model download, training, inference, WebUI, synthesis, audio
generation, Dragon Pet AI runtime change, `/chat` change, STT change,
Conversation Mode change, Owner Voice change, schema change, playback change,
auto-speaking change, Anaconda base change, PATH/profile/registry change,
backend venv change, GPT-SoVITS source change, or existing constraints-file
change was performed.

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

Protected installed packages, verified read-only during this task:

```text
torch==2.7.0+cu128
torchaudio==2.7.0+cu128
torch.version.cuda=12.8
torch.cuda.is_available()=True
device=NVIDIA GeForce RTX 3070
numpy==1.26.4
scipy==1.11.4
tqdm==4.68.3
PyYAML==6.0.3
chardet==7.4.3
psutil==7.2.2
colorama==0.4.6
```

`pip check` still reports:

```text
No broken requirements found.
```

GPT-SoVITS repository:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS
origin: https://github.com/RVC-Boss/GPT-SoVITS.git
commit: b2cff0cd0abd0ac134a16ae7a9695f88e8826104
```

`git status --short` in the GPT-SoVITS repo reported no changed files. Git also
emitted user-home ignore permission warnings; those warnings do not indicate
repository changes.

---

## 2. Files Inspected

Dependency and install files:

- `requirements.txt`
- `extra-req.txt`
- `install.ps1`
- `install.sh`
- `Dockerfile`
- `docker-compose.yaml`
- `docker_build.sh`
- `Docker/install_wrapper.sh`
- `Docker/miniforge_install.sh`
- `GPT_SoVITS/BigVGAN/requirements.txt`
- `README.md`
- `go-webui.ps1`
- `go-webui.bat`

Audio and inference files:

- `api.py`
- `api_v2.py`
- `webui.py`
- `GPT_SoVITS/TTS_infer_pack/TTS.py`
- `GPT_SoVITS/module/mel_processing.py`
- `GPT_SoVITS/utils.py`
- `GPT_SoVITS/export_torch_script_v3v4.py`
- `GPT_SoVITS/BigVGAN/inference.py`
- `GPT_SoVITS/BigVGAN/inference_e2e.py`
- `GPT_SoVITS/BigVGAN/train.py`
- `GPT_SoVITS/BigVGAN/meldataset.py`
- `tools/audio_sr.py`
- `tools/slice_audio.py`
- `tools/slicer2.py`
- `tools/AP_BWE_main/datasets1/dataset.py`

Text and preprocessing files:

- `GPT_SoVITS/TTS_infer_pack/TextPreprocessor.py`
- `GPT_SoVITS/TTS_infer_pack/text_segmentation_method.py`
- `GPT_SoVITS/prepare_datasets/1-get-text.py`
- `GPT_SoVITS/text/cleaner.py`
- `GPT_SoVITS/text/chinese.py`
- `GPT_SoVITS/text/chinese2.py`
- `GPT_SoVITS/text/tone_sandhi.py`
- `GPT_SoVITS/text/zh_normalization/*`
- `GPT_SoVITS/text/LangSegmenter/langsegmenter.py`
- `GPT_SoVITS/text/g2pw/onnx_api.py`
- `GPT_SoVITS/text/japanese.py`
- `GPT_SoVITS/text/english.py`
- `GPT_SoVITS/text/cantonese.py`
- `GPT_SoVITS/text/korean.py`

---

## 3. Repository Dependency Evidence

Main `requirements.txt` relevant entries:

```text
--no-binary=opencc
numpy<2.0
scipy
librosa==0.10.2
numba
ffmpeg-python
cn2an
pypinyin
pyopenjtalk>=0.4.1
g2p_en
torchaudio
jieba_fast
jieba
split-lang
fast_langdetect>=0.3.1
wordsegment
opencc
av>=11
```

`extra-req.txt`:

```text
faster-whisper
```

BigVGAN requirements relevant entries:

```text
torch
numpy
librosa>=0.8.1
scipy
soundfile
matplotlib
pesq
auraloss
tqdm
nnAudio
ninja
huggingface_hub>=0.23.4
```

Install scripts remain rejected for this layer because they can install Conda
system packages, unpinned `torch torchcodec`, full requirements, and model or
dictionary assets.

---

## 4. Audio Dependency Inventory

| Package / layer | Repo evidence | Required or optional | First probe relevance | Windows wheel/build evidence | Interaction / risk | Recommendation |
|---|---|---|---|---|---|---|
| `torchaudio` | `requirements.txt`; `api.py`; `TTS.py`; `tools/audio_sr.py` | Required for reference WAV load/resample in current code | Already installed and protected | Existing `2.7.0+cu128` verified | Must not be replaced by bare requirement | Pin in constraints, never request in B1 |
| `librosa==0.10.2` | `requirements.txt`; `TTS.py`; `api.py`; `mel_processing.py`; `utils.py` | Required by import and mel/filter/reference-load paths | Yes, needed before importing main TTS path | PyPI metadata: pure `py3-none-any` wheel | Brings `numba`, `soundfile`, `soxr`, `scikit-learn`, `joblib`, `pooch`, `lazy-loader`, `msgpack` | Include in B1 |
| `soundfile` | `api.py`, `api_v2.py`, BigVGAN reqs, export script | Required for WAV/OGG/raw output helpers; useful for WAV IO | Useful for future WAV-only checks, but no audio generation in install task | `0.13.1` has pure wheel and Windows wheels in metadata; depends on libsndfile packaging behavior | Should not require system ffmpeg | Include in B1 |
| `numba` | Main req; `librosa` dependency | Required by `librosa` | Yes as transitive for librosa | `0.59.1` has cp310 win_amd64 wheel | Must match NumPy; `0.59.1` supports NumPy 1.26 range | Pin in B1 |
| `llvmlite` | `numba` dependency | Required by `numba` | Yes as transitive for numba | `0.42.0` has cp310 win_amd64 wheel | Must match numba | Pin in B1 |
| `soxr` | `librosa` dependency | Required by `librosa` | Yes as transitive for librosa | `0.5.0.post1` and latest have cp310 win_amd64 wheels | Low risk if wheel-only | Pin in B1 |
| `audioread` | `librosa` dependency | Required by librosa dependency metadata | Low, but pulled by librosa | Pure wheel | Can use external decoders for non-WAV; first probe should stay WAV-only | Allow as B1 transitive/pin |
| `scikit-learn`, `joblib`, `threadpoolctl` | `librosa` dependency chain | Required by librosa metadata | Incidental to librosa import | `scikit-learn==1.4.2` has cp310 win_amd64 wheel; `joblib`/`threadpoolctl` pure wheels | Larger dependency set than ideal but source-build avoidable | Pin in B1 constraints if installing librosa |
| `ffmpeg-python` | `requirements.txt`; `TTS.py` imports `ffmpeg`; `speed_change()` uses subprocess ffmpeg through wrapper | Optional for default speed; required when speed change path is used and for importing `TTS.py` as written | Not needed for minimal WAV dependency install unless testing `TTS.py` import | Pure wheel | Wrapper does not provide `ffmpeg.exe`; can fail at runtime if speed path uses it | Defer to B4 unless import-only proof becomes the next task |
| system `ffmpeg.exe` / `ffprobe.exe` | `install.ps1` / `install.sh` install `ffmpeg`; `speed_change()` assumes ffmpeg process | Optional for WAV-only no-speed first probe; required for wrapper runtime and broader codecs | Not needed for B1 | Not a Python wheel | PATH/system pollution risk | Exclude from first group |
| `av>=11` / PyAV | `requirements.txt`; codec-oriented dependency | Optional codec/media layer | Not needed for WAV-only | `av==11.0.0` has only sdist; latest `17.1.0` has cp310 win_amd64 wheel | Source-build risk if resolver picks 11.x without wheel | Defer to B4; if approved later, pin wheel-bearing version |
| TorchCodec | `install.ps1`, `install.sh`, Docker scripts only | Optional/script-installed codec layer | Not needed for WAV-only | Not in requirements.txt | May couple to torch versions | Exclude |
| `pydub`, `pyloudnorm`, `webrtcvad`, `resampy` | Not required by main inspected runtime files; `resampy` only test extra through librosa metadata | Optional/non-evidence for first group | Not needed | `pydub`/`pyloudnorm` pure; `webrtcvad` sdist only | Unnecessary scope | Exclude |

---

## 5. Ffmpeg And Codec Layer Separation

1. Python wrapper:
   - `ffmpeg-python==0.2.0`.
   - Pure Python wrapper.
   - Does not install `ffmpeg.exe` or `ffprobe.exe`.
   - `TTS.py` imports `ffmpeg` at module import time and uses it in
     `speed_change()`.

2. System binary:
   - `ffmpeg.exe` / `ffprobe.exe`.
   - Installed by upstream scripts through Conda/system setup.
   - Required when the wrapper actually runs a filter/subprocess path.
   - Not required for a WAV-only dependency install review.

3. Python codec libraries:
   - PyAV (`av>=11`) is a Python binding codec layer.
   - TorchCodec is installed only by upstream scripts, not by `requirements.txt`.
   - Both are excluded from the first WAV-only group.

Layer requirements:

| Scenario | Wrapper | System ffmpeg | PyAV | TorchCodec |
|---|---:|---:|---:|---:|
| Import low-level audio helpers not importing `TTS.py` | no | no | no | no |
| Import `TTS.py` as written | yes | no, unless speed path runs | no | no |
| Load simple WAV reference through `torchaudio.load` / `librosa.load` | no | no | no | no |
| Load MP3/M4A/FLAC broadly | maybe | likely | maybe | maybe |
| Standalone inference with non-default speed | yes | yes | no | no |
| WebUI/full upstream workflow | yes | likely | possible | possible |
| Dataset preprocessing/training | likely | likely | possible | no unless script path |

Primary minimal recommendation for WAV-only first probe:

```text
Do not install system ffmpeg, PyAV, or TorchCodec in the next task.
Keep future input strictly WAV and keep speed change disabled/default.
```

---

## 6. Text Dependency Inventory

| Package | Repo evidence | Language path | Windows risk | First Chinese probe necessity | Recommendation |
|---|---|---|---|---:|---|
| `cn2an` | `chinese.py`, `chinese2.py`, `cantonese.py`, requirements | Chinese/Yue number normalization | Pure wheel | yes | Candidate for B2 |
| `pypinyin` | `chinese.py`, `chinese2.py`, `tone_sandhi.py`, G2PW code | Chinese pinyin/G2P fallback | Pure wheel | yes | Candidate for B2 |
| `jieba_fast` | `chinese.py`, `chinese2.py`, `tone_sandhi.py`, requirements | Chinese segmentation/POS | PyPI metadata for `0.53`: sdist only | yes, direct import | High-risk blocker; exclude from automatic first group |
| `jieba` | `LangSegmenter`, requirements | Language segmentation helper | `0.42.1` sdist only but pure-Python package historically | useful | Defer or allow only after confirming wheel/source policy |
| `split-lang` | `LangSegmenter` | Multilingual segmentation | Pure wheel | yes if using `LangSegmenter` | Candidate for B2 |
| `fast_langdetect` | `LangSegmenter` | Language detection | Pure wheel | yes if using `LangSegmenter` | Candidate for B2 |
| `opencc` | `requirements.txt` with `--no-binary=opencc`; `g2pw/onnx_api.py` imports `OpenCC` | Traditional/Simplified conversion in G2PW | `1.3.1` has cp310 win_amd64 wheel, but upstream requirement forces no-binary | needed if G2PW enabled | Defer; never use upstream `--no-binary` for Windows |
| `pyopenjtalk>=0.4.1` | `japanese.py`, requirements, install scripts download dictionary | Japanese | `0.4.1` sdist only | no for Chinese-only | Defer to B3/high-risk |
| `g2p_en`, `wordsegment`, `nltk` | `english.py`, requirements | English | Pure wheels; NLTK data may be external asset issue | no for Chinese-only | Defer unless mixed English accepted |
| `ToJyutping` | `cantonese.py` | Cantonese/Yue | Pure wheel | no for Mandarin-only | Defer |
| `g2pk2`, `ko_pron` | `korean.py` | Korean | Pure wheels | no | Defer |
| `fugashi`, `unidic-lite`, `python_mecab_ko` | adjacent tokenizer candidates; `python_mecab_ko` not Windows | Japanese/Korean extras | `unidic-lite` source/data-heavy; not first probe | no | Exclude from B2 |

Chinese-only conclusion:

- Current `version="v2"` Chinese path uses `chinese2.py`.
- `chinese2.py` sets `is_g2pw=True` at import time, which constructs
  `G2PWPinyin` with `model_dir="GPT_SoVITS/text/G2PWModel"` and can trigger
  G2PW/ONNX/OpenCC/model concerns.
- Even before model readiness, `jieba_fast` is a hard direct import and PyPI
  metadata shows source-only for `0.53`.
- Therefore a no-source-build, no-model-download Chinese text install is not
  yet safe enough to select as the next first group.

---

## 7. Windows Native-Build Risks

| Package | Candidate version | Wheel evidence | Source-build risk | First group decision | Safer alternative |
|---|---|---|---|---|---|
| `jieba_fast` | `0.53` | No cp310 Windows wheel in PyPI metadata; sdist only | high | exclude | investigate pure `jieba` substitution only if code patch is later approved; not in this review |
| `pyopenjtalk` | `0.4.1` | No cp310 Windows wheel in PyPI metadata; sdist only | high; dictionary handling too | exclude | defer Japanese path |
| `opencc` | `1.3.1` | cp310 win_amd64 wheel exists | high if using upstream `--no-binary=opencc` | defer | later install explicit wheel-bearing `opencc==1.3.1` without upstream no-binary |
| `av` | `11.0.0` vs `17.1.0` | `11.0.0` sdist only; `17.1.0` cp310 wheel exists | high if resolver picks old version | exclude | later pin `av==17.1.0` only if codec task approved |
| `numba` / `llvmlite` | `0.59.1` / `0.42.0` | both have cp310 win_amd64 wheels | medium; strict version coupling | include only with explicit pins | protect NumPy 1.26.4 and use wheel-only |
| `webrtcvad` | `2.0.10` | sdist only | high | exclude | not repo-required for first probe |
| `unidic-lite` | `1.0.8` | sdist/data package only in metadata | medium/high | exclude | not repo-required for Chinese-only |

---

## 8. Protected Package Conflict Analysis

Protected versions:

```text
torch==2.7.0+cu128
torchaudio==2.7.0+cu128
numpy==1.26.4
scipy==1.11.4
```

Potential resolver risks:

- Bare `torchaudio` in upstream `requirements.txt` could become resolver-owned
  if full requirements are installed.
- BigVGAN requirements contain bare `torch`.
- `numba` must be pinned to a version compatible with `numpy==1.26.4`.
- `librosa==0.10.2` accepts current NumPy/SciPy, but its dependency chain must
  be pinned to avoid NumPy 2.x pressure.
- PyAV/TorchCodec are codec layers and must not enter B1.
- Full requirements could introduce `onnxruntime-gpu`, `transformers`,
  `pydantic`, `fastapi[standard]`, and other broad resolver pressure.

Updated lab-local constraints strategy for a future install:

```text
torch==2.7.0+cu128
torchaudio==2.7.0+cu128
numpy==1.26.4
scipy==1.11.4
librosa==0.10.2
soundfile==0.13.1
numba==0.59.1
llvmlite==0.42.0
soxr==0.5.0.post1
scikit-learn==1.4.2
msgpack==1.0.8
```

This task did not create or modify that constraints file.

---

## 9. Staged Audio/Text Groups

### Group B1 - Low-risk WAV/audio foundation

Status: NOT APPROVED / DO NOT RUN YET.

Purpose:

- Satisfy the core audio helper layer for future WAV-only preparation.
- Support `librosa.load`, `librosa.filters.mel`, `soundfile` WAV IO, and
  NumPy/SciPy/Torch audio interop without entering codec/model/text risk.

Proposed direct pins:

```text
librosa==0.10.2
soundfile==0.13.1
numba==0.59.1
llvmlite==0.42.0
soxr==0.5.0.post1
audioread==3.0.1
scikit-learn==1.4.2
joblib==1.4.2
threadpoolctl==3.5.0
decorator==5.1.1
pooch==1.8.2
platformdirs==4.2.2
requests==2.32.3
lazy-loader==0.4
msgpack==1.0.8
```

Risk level: low to medium. Compiled packages have cp310 Windows wheel evidence;
scope is still larger than Group A because of librosa's dependency chain.

Verification commands:

- Import `librosa`, `soundfile`, `numba`, `llvmlite`, `soxr`.
- Generate a synthetic NumPy array in memory and run `librosa.resample`.
- Create a mel filter via `librosa.filters.mel`.
- Write/read a short in-memory WAV with `soundfile`.
- Re-verify torch/torchaudio/numpy/scipy/CUDA and `pip check`.

Rollback strategy:

- Do not run automatic rollback.
- If install fails before package changes, stop and report.
- If packages are partially installed, capture `pip freeze`, `pip check`, and
  ask for explicit cleanup approval.

### Group B2 - Chinese text processing

Status: NOT APPROVED / DO NOT RUN YET.

Candidate packages:

```text
cn2an==0.5.24
pypinyin==0.55.0
split-lang==2.1.1
fast-langdetect==1.0.1
opencc==1.3.1
jieba_fast==0.53
jieba==0.42.1
```

Risk level: high because `jieba_fast==0.53` is source-only in PyPI metadata and
is directly imported by `chinese.py`, `chinese2.py`, and `tone_sandhi.py`.
`opencc` has a wheel, but upstream `--no-binary=opencc` must not be used.

Recommendation:

- Defer B2.
- Before installing B2, decide whether source build for `jieba_fast` is
  acceptable or whether a code-level fallback to pure `jieba` is approved.
- Do not download G2PW assets in a dependency-install task.

### Group B3 - Japanese / multilingual text processing

Status: NOT APPROVED / DO NOT RUN YET.

Candidate packages:

```text
pyopenjtalk>=0.4.1
g2p_en==2.1.0
wordsegment==1.3.1
nltk==3.9.4
ToJyutping==3.2.0
g2pk2==0.0.3
ko-pron==1.3
```

Risk level: medium to high. `pyopenjtalk==0.4.1` is source-only and install
scripts separately handle OpenJTalk dictionary assets. NLTK can require data
assets depending on usage.

Recommendation:

- Defer until Chinese WAV-only path is proven.

### Group B4 - Optional codecs and ffmpeg wrappers

Status: NOT APPROVED / DO NOT RUN YET.

Candidate packages/layers:

```text
ffmpeg-python==0.2.0
av==17.1.0
system ffmpeg.exe / ffprobe.exe
TorchCodec
```

Risk level: medium/high. `ffmpeg-python` is only a wrapper; system binaries are
separate. PyAV must be pinned to a wheel-bearing version if approved. TorchCodec
may couple to torch and is not in `requirements.txt`.

Recommendation:

- Defer.
- B1 must not include this group.

### Group B5 - Native-build / high-risk

Status: NOT APPROVED / DO NOT RUN YET.

Packages:

```text
jieba_fast==0.53
pyopenjtalk==0.4.1
av==11.0.0
webrtcvad==2.0.10
pesq
flash-attn
BigVGAN CUDA extension / ninja path
```

Recommendation:

- Exclude from first install group.
- Treat each as a separate approval or code-design task.

---

## 10. Selected Next First Install Group

Selected primary next install group:

```text
TASK-TTS-004E5A - GPT-SoVITS WAV/Chinese Runtime Dependency Install
Primary install subset: Group B1 - Low-risk WAV/audio foundation.
```

Reasoning:

- B1 is the smallest useful layer that moves toward a future WAV-only probe
  while preserving torch/cu128, NumPy, and SciPy.
- It avoids source builds according to current PyPI metadata.
- It avoids system ffmpeg, PyAV, TorchCodec, model downloads, and WebUI.
- It avoids the current Chinese text blocker, `jieba_fast`, until the user
  explicitly accepts source-build risk or approves a fallback design.

Important limitation:

- B1 alone does not make GPT-SoVITS Chinese inference ready. It prepares the
  audio layer only. A later text-layer task must address `jieba_fast`, G2PW,
  OpenCC, and Chinese model assets before real Chinese inference.

Fallback plan, not automatic:

```text
If B1 metadata or install planning shows numba/llvmlite conflict, keep B1 on
hold and split a smaller import-only audio helper check around soundfile/soxr
without installing librosa. Do not execute fallback automatically.
```

---

## 11. Future Commands

All commands in this section are:

```text
NOT APPROVED / DO NOT RUN YET
```

Create future constraints file:

```powershell
$LabRoot = "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab"
$ConstraintsFile = Join-Path $LabRoot "constraints\TASK-TTS-004E5A_AUDIO_B1_PROTECTED.txt"
@"
torch==2.7.0+cu128
torchaudio==2.7.0+cu128
numpy==1.26.4
scipy==1.11.4
librosa==0.10.2
soundfile==0.13.1
numba==0.59.1
llvmlite==0.42.0
soxr==0.5.0.post1
scikit-learn==1.4.2
msgpack==1.0.8
"@ | Set-Content -Encoding UTF8 -Path $ConstraintsFile
```

Snapshot before:

```powershell
$TargetEnv = "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310"
$EnvPython = Join-Path $TargetEnv "python.exe"
$LabRoot = "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab"
& $EnvPython -m pip freeze |
  Set-Content -Encoding UTF8 (Join-Path $LabRoot "reports\TASK-TTS-004E5A_PIP_BEFORE.txt")
& "C:\ProgramData\anaconda3\Scripts\conda.exe" list --prefix $TargetEnv |
  Set-Content -Encoding UTF8 (Join-Path $LabRoot "reports\TASK-TTS-004E5A_CONDA_BEFORE.txt")
```

Install B1:

```powershell
$TargetEnv = "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310"
$EnvPython = Join-Path $TargetEnv "python.exe"
$LabRoot = "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab"
$PipCache = Join-Path $LabRoot "pip-cache"
$ConstraintsFile = Join-Path $LabRoot "constraints\TASK-TTS-004E5A_AUDIO_B1_PROTECTED.txt"
$InstallLog = Join-Path $LabRoot "reports\TASK-TTS-004E5A_AUDIO_B1_INSTALL.log"
$env:PIP_CACHE_DIR = $PipCache
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
& $EnvPython -m pip install `
  --index-url "https://pypi.org/simple" `
  --constraint $ConstraintsFile `
  --only-binary=:all: `
  --disable-pip-version-check `
  --no-input `
  "librosa==0.10.2" `
  "soundfile==0.13.1" `
  "numba==0.59.1" `
  "llvmlite==0.42.0" `
  "soxr==0.5.0.post1" `
  "audioread==3.0.1" `
  "scikit-learn==1.4.2" `
  "joblib==1.4.2" `
  "threadpoolctl==3.5.0" `
  "decorator==5.1.1" `
  "pooch==1.8.2" `
  "platformdirs==4.2.2" `
  "requests==2.32.3" `
  "lazy-loader==0.4" `
  "msgpack==1.0.8" `
  2>&1 | Tee-Object -FilePath $InstallLog
```

Verify after:

```powershell
& $EnvPython -c "import librosa, soundfile, numba, llvmlite, soxr; print(librosa.__version__, soundfile.__version__, numba.__version__, llvmlite.__version__, soxr.__version__)"
& $EnvPython -c "import torch, torchaudio, numpy, scipy; print(torch.__version__, torchaudio.__version__, torch.version.cuda, torch.cuda.is_available(), numpy.__version__, scipy.__version__)"
& $EnvPython -c "import torch; x=torch.tensor([1.0], device='cuda'); y=x+1; torch.cuda.synchronize(); print(y.device, y.item())"
& $EnvPython -m pip check
```

Snapshot after:

```powershell
& $EnvPython -m pip freeze |
  Set-Content -Encoding UTF8 (Join-Path $LabRoot "reports\TASK-TTS-004E5A_PIP_AFTER.txt")
& "C:\ProgramData\anaconda3\Scripts\conda.exe" list --prefix $TargetEnv |
  Set-Content -Encoding UTF8 (Join-Path $LabRoot "reports\TASK-TTS-004E5A_CONDA_AFTER.txt")
```

---

## 12. Success Criteria For Future Install

A future TASK-TTS-004E5A install may pass only if:

- Only explicitly approved packages are installed.
- `librosa`, `soundfile`, `numba`, `llvmlite`, and `soxr` imports pass.
- Torch remains `2.7.0+cu128`.
- Torchaudio remains `2.7.0+cu128`.
- NumPy remains `1.26.4`.
- SciPy remains `1.11.4`.
- CUDA remains available.
- RTX 3070 remains detected.
- Minimal CUDA tensor still works.
- `pip check` passes.
- Before/after package snapshots are recorded.
- No model/dataset is downloaded.
- No inference/WebUI/audio generation is performed.
- Anaconda base and Dragon Pet AI runtime remain unchanged.

---

## 13. Rejection Criteria

Stop if any of these occur:

- Resolver attempts to replace `torch`, `torchaudio`, `numpy`, or `scipy`.
- Resolver requires NumPy 2.x.
- Resolver attempts source compilation.
- Windows cp310 wheels are unavailable for the selected compiled packages.
- System ffmpeg installation becomes required for the selected first group.
- PyAV or TorchCodec is pulled unexpectedly.
- Package scripts download assets/models.
- Scope expands beyond Group B1.
- Repository evidence contradicts the selected package set.

---

## 14. External Manifest

External manifest:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E5_AUDIO_TEXT_DEPENDENCY_REVIEW.md
```

---

## 15. Confirmation

Confirmed for TASK-TTS-004E5:

- No package was installed or uninstalled.
- No `pip install` or `conda install` was run.
- No `requirements.txt`, `install.ps1`, `install.sh`, Docker script, or WebUI
  launcher was executed.
- No model, dataset, checkpoint, voice sample, or generated audio was created.
- No training, inference, WebUI, synthesis, playback, Pet playback, or
  auto-speaking occurred.
- Protected torch/torchaudio/numpy/scipy versions were unchanged.
- No ffmpeg, PyAV, or TorchCodec was installed.
- No Anaconda base, PATH, PowerShell profile, registry, failed Miniconda,
  backend venv, GPT-SoVITS source, Dragon Pet AI runtime, `/chat`, STT,
  Conversation Mode, Owner Voice, schema, or dependency-file change was made.

---

## 16. Final Verdict

```text
DONE - GPT-SOVITS AUDIO/TEXT DEPENDENCY REVIEW COMPLETE / INSTALL NOT APPROVED
```

Recommended next task, not approved yet:

```text
TASK-TTS-004E6 - GPT-SoVITS Chinese Text Dependency Review
```

Primary selected first install subset for that future task:

```text
Group B1 - Low-risk WAV/audio foundation
```

TASK-TTS-004E5A later installed and verified this Group B1 subset only. It did
not install Chinese text dependencies, model dependencies, ffmpeg, PyAV,
TorchCodec, models, WebUI, inference, synthesis, persistent audio generation,
or runtime wiring. See `docs/TTS_GPT_SOVITS_AUDIO_B1_INSTALL.md`.
