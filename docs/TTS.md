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
- `jieba_fast` is present in the Chinese import path and remains the immediate
  Windows resolution blocker.
- Plain `jieba` fallback is plausible only as a design option; no alias, shim,
  import hook, or source patch has been implemented.
- OpenCC compatibility remains unresolved; `opencc.OpenCC(config).convert(text)`
  behavior must be verified before substitution.
- Multilingual eager imports may pull non-Chinese dependencies before a
  Chinese-only path is isolated.

## Not Approved

- Chinese dependency install.
- `jieba_fast` workaround implementation.
- G2PW package/model/tokenizer download.
- GPT-SoVITS WebUI.
- Training.
- Inference.
- Synthesis or generated audio.
- Runtime TTS provider integration.
- Playback or auto-speaking.

## Current Next Action

```text
jieba_fast Windows Resolution Design
```
