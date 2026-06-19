# GPT-SoVITS WAV/Chinese Runtime Dependency Install

**Task:** TASK-TTS-004E5A
**Status:** DONE - GPT-SOVITS WAV/AUDIO B1 DEPENDENCIES VERIFIED / TEXT MODEL RUNTIME NOT INSTALLED
**Date:** 2026-06-19
**Scope:** Approved install of Group B1 low-risk WAV/audio foundation packages
only into the isolated GPT-SoVITS lab environment. No GPT-SoVITS Chinese text
dependencies, `jieba_fast`, G2PW, OpenCC, `pyopenjtalk`, ffmpeg, PyAV,
TorchCodec, model/dataset download, training, inference, WebUI, persistent
audio generation, runtime TTS, playback, auto-speaking, Anaconda base,
PATH/profile/registry, `conda init`, backend venv, `/chat`, STT, Conversation
Mode, Owner Voice, schema, or Dragon Pet AI runtime change was performed.

---

## 1. Target Environment

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310
Python 3.10.20
```

Protected package constraints:

```text
torch==2.7.0+cu128
torchaudio==2.7.0+cu128
numpy==1.26.4
scipy==1.11.4
```

Constraints file:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\constraints\TASK-TTS-004E5A_AUDIO_B1_PROTECTED.txt
```

Requested package file:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\constraints\TASK-TTS-004E5A_AUDIO_B1_REQUESTED.txt
```

---

## 2. Install Method

The install used `pip install` in the isolated lab environment with:

- `--only-binary=:all:`
- `--upgrade-strategy only-if-needed`
- lab-local protected constraints
- `--no-cache-dir`
- install report and install log under the external lab reports directory

The binary-only dry-run succeeded before install. Dry-run and install reports
both contained 21 candidates and no forbidden/protected package candidates.

Installed requested B1 packages:

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

Installed transitive dependencies:

```text
cffi==2.0.0
pycparser==3.0
certifi==2026.6.17
charset-normalizer==3.4.7
idna==3.18
urllib3==2.7.0
```

The only pip warnings were that `idna.exe` and `normalizer.exe` were installed
inside the isolated environment's `Scripts` directory, which is not on PATH.
PATH was not modified.

---

## 3. Validation Results

Validation command output is recorded at:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E5A_VALIDATION.txt
```

Validation passed:

- All requested B1 package imports and versions.
- Approved transitive package versions.
- Forbidden package absence check.
- `librosa.resample` on an in-memory synthetic NumPy waveform:
  `librosa_resample_shape=(4000,)`.
- `librosa.filters.mel`:
  `librosa_mel_shape=(80, 201)`.
- `soundfile` in-memory WAV write/read round trip:
  `soundfile_roundtrip_shape=(1000,)`, `soundfile_roundtrip_sr=22050`.
- SciPy resample interop:
  `scipy_resample_poly_shape=(4009,)`.
- NumPy/Torch interop:
  `numpy_torch_sum=3.0`.
- Protected torch:
  `torch=2.7.0+cu128`.
- Protected torchaudio:
  `torchaudio=2.7.0+cu128`.
- Protected CUDA build:
  `torch_cuda=12.8`.
- Protected NumPy:
  `numpy=1.26.4`.
- Protected SciPy:
  `scipy=1.11.4`.
- CUDA available:
  `cuda_available=True`.
- RTX 3070 device:
  `device_name=NVIDIA GeForce RTX 3070`.
- Minimal CUDA tensor:
  `cuda_tensor_device=cuda:0`, `cuda_tensor_sum=6.0`.
- `pip check`:
  `No broken requirements found.`

---

## 4. External Evidence

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E5A_AUDIO_B1_INSTALL.md
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E5A_PIP_BEFORE.txt
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E5A_CONDA_BEFORE.txt
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E5A_DRY_RUN_REPORT.json
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E5A_INSTALL_REPORT.json
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E5A_AUDIO_B1_INSTALL.log
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E5A_VALIDATION.txt
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E5A_PIP_AFTER.txt
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E5A_CONDA_AFTER.txt
```

---

## 5. Boundary Confirmation

Confirmed for TASK-TTS-004E5A:

- No source build occurred.
- No fallback install path was used.
- No protected package was replaced.
- NumPy remained `1.26.4`; NumPy 2.x was not installed.
- SciPy remained `1.11.4`.
- Torch remained `2.7.0+cu128`.
- Torchaudio remained `2.7.0+cu128`.
- No PyAV, TorchCodec, ffmpeg wrapper/system binary, model package, Chinese
  text dependency, `jieba_fast`, G2PW, OpenCC, or `pyopenjtalk` was installed.
- No model, dataset, checkpoint, voice sample, or persistent generated audio
  was created.
- No training, inference, WebUI, synthesis, playback, Pet playback, or
  auto-speaking occurred.
- No Anaconda base, PATH, PowerShell profile, registry, failed Miniconda,
  backend venv, GPT-SoVITS source, Dragon Pet AI runtime, `/chat`, STT,
  Conversation Mode, Owner Voice, schema, or dependency-file change was made.

---

## 6. Final Verdict

```text
DONE - GPT-SOVITS WAV/AUDIO B1 DEPENDENCIES VERIFIED / TEXT MODEL RUNTIME NOT INSTALLED
```

Recommended next task, not approved yet:

```text
TASK-TTS-004E6 - GPT-SoVITS Chinese Text Dependency Review
```
