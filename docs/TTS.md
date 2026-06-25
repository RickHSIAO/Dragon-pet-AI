# TTS

## Purpose

TTS exists to eventually let Christina speak with a local, character-appropriate
voice. The current application does not yet have a usable character voice.

## Runtime State

- Backend TTS service skeleton exists.
- Runtime TTS is disabled/mock-only by default.
- No real app playback path is enabled.
- No `/chat` schema or mood schema change is part of TTS.
- Pet Window browser speech controls are not the final character voice path.

## Provider Architecture

The intended architecture is:

```text
chat reply -> text normalization -> TTS queue -> provider adapter -> playback
```

The provider adapter boundary exists in backend code, but real provider runtime
integration remains unapproved.

## Provider Research Summary

- Mock provider: current safe skeleton.
- VOICEVOX: useful as a local Japanese-style/manual experiment, not selected as
  final Christina voice.
- edge-tts: acceptable as a temporary Chinese/debug candidate only; not final
  character voice and not local-only.
- GPT-SoVITS: selected as the first isolated character voice lab candidate.
- Style-Bert-VITS2: fallback/second research candidate.
- RVC-like conversion: deferred.

## External GPT-SoVITS Lab

The external lab is outside this repository:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab
```

Current lab facts:

- Isolated Python target: `3.10.20`.
- GPT-SoVITS checkout is official and external.
- Expected analyzed GPT-SoVITS commit:
  `b2cff0cd0abd0ac134a16ae7a9695f88e8826104`.
- Protected packages include `torch==2.7.0+cu128`,
  `torchaudio==2.7.0+cu128`, `numpy==1.26.4`, and `scipy==1.11.4`.

Installed dependency layers in the external lab:

- Foundation layer: NumPy/SciPy/support packages needed by later work.
- WAV/audio B1 layer: low-risk audio packages for WAV/audio preparation.

These installs do not make Chinese text inference ready.

## Chinese Text Import Graph Findings

The E6A static import-graph probe exists and is preserved:

- `scripts/tts_gpt_sovits_chinese_import_graph_probe.py`
- `backend/tests/test_tts_gpt_sovits_chinese_import_graph_probe.py`

Current Chinese path findings:

- `chinese2.py` sets `is_g2pw = True` at module level.
- `chinese2.py` imports local G2PW code and constructs `G2PWPinyin(...)` at
  module import time.
- This creates package, model/config, tokenizer, ONNX/runtime, and asset
  boundary risk before a Chinese-processing function is called.
- The `jieba_fast` Windows blocker has an external-lab-only compatibility
  bootstrap: official `jieba-0.42.1.tar.gz` was downloaded from PyPI, verified
  with SHA256
  `055ca12f62674fafed09427f176506079bc135638a14e23e25be909131928db2`, and
  extracted under the external lab vendor directory.
- A lab-local explicit `jieba_fast` adapter delegates the current required API
  surface to vendored plain `jieba`: `setLogLevel`, `cut_for_search`, and
  `posseg.lcut` with `.word` / `.flag` pair behavior.
- The repo probe verified process-local import precedence, segmentation/POS
  parity against vendored plain `jieba`, deterministic output, unchanged package
  snapshots, unchanged persistent environment variables, and no GPT-SoVITS
  Chinese module import.
- No package install, upstream GPT-SoVITS patch, import hook, `sitecustomize`,
  runtime alias, source patch, inference, WebUI, training, playback, or audio
  generation was performed.
- GPT-SoVITS currently requires `from opencc import OpenCC`,
  `OpenCC("s2tw")`, and `.convert(text)` before G2PW; converted text must
  preserve input length for the downstream assertion.
- Preferred OpenCC direction is an isolated official upstream OpenCC wheel probe
  on Windows/Python 3.10, not the GPT-SoVITS `--no-binary=opencc` source-build
  path.
- `opencc-python-reimplemented` is API/config-name compatible on static review,
  but dictionary/output parity is unproven and it is not selected as a direct
  drop-in.
- OpenCC-dependent Chinese inference remains blocked until the no-model
  compatibility probe proves import origin, asset origin, offline behavior,
  deterministic conversion, and acceptable `s2tw` output.
- Multilingual eager imports may pull non-Chinese dependencies before a
  Chinese-only path is isolated.

## Not Approved

- Chinese dependency install.
- Repository or runtime `jieba_fast` workaround implementation.
- G2PW package/model/tokenizer download.
- GPT-SoVITS WebUI.
- Training.
- Inference.
- Synthesis or generated audio.
- Runtime TTS provider integration.
- Playback or auto-speaking.

## Current Next Action

```text
TASK-TTS-004E6E - Isolated OpenCC Compatibility Probe
```
