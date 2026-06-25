# GPT-SoVITS Chinese Text Dependency Review

**Latest TASK-TTS-004E6A status (2026-06-25):** The requested follow-up Chinese Import Graph Probe is complete. It added a static AST probe and tests, inspected commit `b2cff0cd0abd0ac134a16ae7a9695f88e8826104`, found `808` import edges and `1052` top-level executable statements, confirmed `chinese2.py` eager G2PW risk, and selected `TASK-TTS-004E6B - jieba_fast Windows Resolution Design`. No install or download occurred.

**Task:** TASK-TTS-004E6
**Status:** DONE - GPT-SOVITS CHINESE TEXT DEPENDENCY REVIEW COMPLETE / INSTALL NOT APPROVED
**Date:** 2026-06-20
**Scope:** Read-only Chinese text dependency review for the isolated GPT-SoVITS
lab. No package install, uninstall, resolver run, full requirements install,
model download, text-model download, WebUI, training, inference, synthesis,
audio generation, GPT-SoVITS source edit, Dragon Pet AI runtime edit, `/chat`,
STT, Conversation Mode, Owner Voice Gate, schemas, playback, auto-speaking,
Anaconda base, PATH/profile/registry, or backend venv change was performed.

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

Protected packages verified read-only during this task:

```text
torch==2.7.0+cu128
torchaudio==2.7.0+cu128
numpy==1.26.4
scipy==1.11.4
torch.cuda.is_available()=True
device=NVIDIA GeForce RTX 3070
```

GPT-SoVITS repository:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS
commit: b2cff0cd0abd0ac134a16ae7a9695f88e8826104
```

Git command access to that repo is blocked by Git safe.directory ownership
protection in the Codex sandbox user, so the commit was verified read-only via
`.git\HEAD` and `.git\refs\heads\main`.

---

## 2. Files Inspected

Entry points and preprocessing:

- `api.py`
- `api_v2.py`
- `GPT_SoVITS/TTS_infer_pack/TTS.py`
- `GPT_SoVITS/TTS_infer_pack/TextPreprocessor.py`
- `GPT_SoVITS/TTS_infer_pack/text_segmentation_method.py`
- `GPT_SoVITS/prepare_datasets/1-get-text.py`

Chinese text modules:

- `GPT_SoVITS/text/cleaner.py`
- `GPT_SoVITS/text/chinese.py`
- `GPT_SoVITS/text/chinese2.py`
- `GPT_SoVITS/text/tone_sandhi.py`
- `GPT_SoVITS/text/__init__.py`
- `GPT_SoVITS/text/opencpop-strict.txt`
- `GPT_SoVITS/text/symbols.py`
- `GPT_SoVITS/text/symbols2.py`
- `GPT_SoVITS/text/zh_normalization/*.py`

G2PW and segmentation:

- `GPT_SoVITS/text/g2pw/__init__.py`
- `GPT_SoVITS/text/g2pw/g2pw.py`
- `GPT_SoVITS/text/g2pw/onnx_api.py`
- `GPT_SoVITS/text/g2pw/dataset.py`
- `GPT_SoVITS/text/g2pw/utils.py`
- `GPT_SoVITS/text/g2pw/polyphonic.rep`
- `GPT_SoVITS/text/g2pw/polyphonic-fix.rep`
- `GPT_SoVITS/text/g2pw/polyphonic.pickle`
- `GPT_SoVITS/text/LangSegmenter/langsegmenter.py`

Dependency references:

- `requirements.txt`
- `extra-req.txt`
- `Dockerfile`
- `Docker/install_wrapper.sh`
- `docs/cn/README.md`
- `docs/en/Changelog_EN.md`
- `docs/cn/Changelog_CN.md`

---

## 3. Chinese Text Import Graph

Primary v1 API path:

```text
api.py
-> from text.LangSegmenter import LangSegmenter
-> from text.cleaner import clean_text
-> from text import cleaned_text_to_sequence
-> from text import chinese
   -> GPT_SoVITS/text/chinese.py
      -> cn2an
      -> pypinyin.lazy_pinyin / Style
      -> text.tone_sandhi.ToneSandhi
         -> import jieba_fast as jieba
         -> pypinyin.lazy_pinyin / Style
      -> import jieba_fast
      -> import jieba_fast.posseg as psg
```

Primary API v2 / class path:

```text
api_v2.py
-> GPT_SoVITS.TTS_infer_pack.TTS
-> GPT_SoVITS.TTS_infer_pack.TextPreprocessor
-> text.LangSegmenter.LangSegmenter
-> text.cleaner.clean_text
-> text.cleaned_text_to_sequence
-> from text import chinese
```

Chinese cleaning and model-facing sequence:

```text
Chinese input text
-> LangSegmenter.getTexts(text, "zh")
-> clean_text(text, "zh", version)
-> dynamic import:
   version "v1": text.chinese
   version "v2": text.chinese2
-> text_normalize()
   -> TextNormalizer.normalize()
   -> zh_normalization date/time/number/phone/quantifier replacements
   -> punctuation cleanup
-> g2p()
   -> sentence split by punctuation
   -> jieba_fast.posseg.lcut()
   -> ToneSandhi.pre_merge_for_modify()
   -> v1: pypinyin lazy_pinyin()
   -> v2: G2PWPinyin / G2PWOnnxConverter, with pypinyin fallback per character
   -> opencpop-strict pinyin to symbol mapping
-> phones, word2ph, normalized text
-> cleaned_text_to_sequence()
-> integer phoneme IDs consumed by GPT-SoVITS model code
```

Important eager imports:

- `text.cleaner` itself delays language-module import until `clean_text()`.
- `api.py` and `TextPreprocessor.py` also import `from text import chinese`,
  so the v1 Chinese module and `jieba_fast` are imported before any v2 Chinese
  cleaning call.
- `LangSegmenter.langsegmenter` imports `jieba`, `fast_langdetect`, and
  `split_lang` at import time.
- `chinese2.py` sets `is_g2pw = True` and constructs `G2PWPinyin(...)` at
  module import time. That initialization can download G2PW assets and initialize
  the tokenizer/ONNX session if assets are missing.

---

## 4. Dependency Inventory

| Package | Import name | Repo requirement | Role | Chinese-only status | Windows CPython 3.10 wheel/source-build risk | Model/download behavior | License concern | Recommended action |
|---|---|---|---|---|---|---|---|---|
| cn2an | `cn2an` | `cn2an` unpinned | Chinese number normalization helper in `chinese.py` and `chinese2.py` | Required by Chinese modules | Low. PyPI latest checked: `0.5.24`, `py3-none-any` wheel | No model download found | MIT per project metadata should be verified before install | Safe candidate only after import blockers are handled |
| pypinyin | `pypinyin` | `pypinyin` unpinned | Pinyin conversion and constants | Required by Chinese, tone sandhi, G2PW fallback | Low. PyPI latest checked: `0.55.0`, `py2.py3-none-any` wheel | Package data only; no external download found | MIT-style project, verify metadata before install | Safe candidate only after import blockers are handled |
| jieba_fast | `jieba_fast`, `jieba_fast.posseg` | `jieba_fast` unpinned | Chinese segmentation and POS tagging | Required by `chinese.py`, `chinese2.py`, `tone_sandhi.py` | High. PyPI `0.53` is source-only; no cp310 Windows wheel listed | Bundled dictionary in sdist; no model download, but build requires C/SWIG toolchain | MIT | Blocker for strict upstream compatibility |
| jieba | `jieba` | `jieba` unpinned | LangSegmenter segmentation/logging; possible fallback candidate | Directly imported by LangSegmenter; not used as fallback for `jieba_fast` | Medium-low. PyPI `0.42.1` is source distribution only but pure Python | Bundled dictionaries; no external download found | MIT | Keep for LangSegmenter; fallback to replace `jieba_fast` needs source patch or controlled monkey patch |
| opencc | `opencc.OpenCC` | `opencc` plus `--no-binary=opencc` | G2PW Traditional/Simplified conversion | Required when G2PW initializes with non-traditional conversion enabled | Mixed. PyPI `OpenCC 1.3.1` has cp310 win_amd64 wheel, but repo requirements force source build via `--no-binary=opencc` | Bundled OpenCC dictionaries; no runtime model download | Apache-2.0 | Do not install via full requirements; validate API before direct binary-wheel use |
| opencc-python-reimplemented | `opencc.OpenCC` | Not listed | Pure-Python OpenCC-compatible alternative | Possible API-compatible candidate because import name is `opencc` and configs like `s2tw` are documented | Low. `0.1.7` has `py2.py3-none-any` wheel | Bundled dictionaries | Apache | Do not substitute without explicit compatibility probe; it is not the upstream requirement |
| G2PW vendored code | `text.g2pw` | Vendored, not a PyPI package | Polyphone disambiguation | Mandatory for current `chinese2.py` import path | Python code is vendored; runtime dependencies include onnxruntime, transformers, requests, opencc, pypinyin, numpy | Downloads `G2PWModel_1.1.zip` from ModelScope if `model_dir` is missing; tokenizer may load from local pretrained model path or try remote if not present | Derived from g2pW, pypinyin-g2pW, PaddleSpeech code; license review needed | Split package dependencies, model assets, and tokenizer/model assets into separate approvals |
| onnxruntime-gpu | `onnxruntime` | `onnxruntime-gpu; platform_machine == "x86_64" or "AMD64"` | G2PW ONNX inference | Required by G2PW current path | Usually wheel-based but large/native; must verify CUDA provider and protected packages | No model download by package itself | MIT | Defer to G2PW package/runtime task |
| transformers | `transformers`, `AutoTokenizer` | `transformers>=4.43,<=4.50` | BERT tokenizer/model source for G2PW and TTS BERT | Required once G2PW initializes | Wheel/pure Python plus dependencies; resolver risk significant | `AutoTokenizer.from_pretrained()` can access local assets or remote hubs if not offline | Apache-2.0 plus transitive licenses | Defer; require offline/local asset boundaries |
| split-lang | `split_lang` | `split-lang` unpinned | LangSegmenter language splitting | Imported eagerly by LangSegmenter | Low-to-medium. PyPI latest checked: `2.1.1`, Python >=3.9, MIT | Uses fast-langdetect; no install-time model download found | MIT | Required for API/TextPreprocessor import path, but not enough alone |
| fast-langdetect | `fast_langdetect` | `fast_langdetect>=0.3.1` | Language detection in LangSegmenter | Imported eagerly by LangSegmenter | Low-to-medium. PyPI latest checked: `1.0.1`, supports Python 3.10 | Works offline with lite model per PyPI docs; repo sets cache under `GPT_SoVITS/pretrained_models/fast_langdetect` | MIT | Include only in a later import-graph group |
| wordsegment | `wordsegment` | `wordsegment` unpinned | English segmentation | Not required by Chinese-only cleaner unless English path is selected | Low. Pure Python, but old metadata | Package data bundled | Apache-2.0; includes derived corpus subset | Defer unless English eager import proves unavoidable |
| nltk | `nltk` | Not listed in current `requirements.txt` | Not found in current Chinese path | Not required by evidence | Not applicable | NLTK data can download if used, but no current import found | Apache-2.0 | Do not include |
| regex | `regex` | Not listed in current `requirements.txt` | Not found in current Chinese path | Not required by evidence | PyPI latest checked: `2026.5.9`, native wheels expected, Python >=3.10 | No model download | Apache-2.0 AND CNRI-Python | Do not include unless future evidence appears |
| inflect | `inflect` | Not listed in current `requirements.txt` | Not found in Chinese path | Not required by evidence | Not evaluated for install | No model download known | Verify if ever needed | Do not include |
| Unidecode/unidecode | `unidecode` | Not listed in current `requirements.txt` | Not found in Chinese path | Not required by evidence | Not evaluated for install | No model download known | GPL risk depends exact package | Do not include |
| num2words | `num2words` | Not listed in current `requirements.txt` | Not found in Chinese path | Not required by evidence | PyPI latest checked: `0.5.14`, Python 3.10 classifier | No model download | LGPL | Do not include |
| pyopenjtalk | `pyopenjtalk` | `pyopenjtalk>=0.4.1` | Japanese path | Not required by `cleaner.py` unless Japanese module is imported | Native build/wheel risk; Japanese scope | Dictionary/model behavior must be reviewed separately | Verify separately | Defer |
| g2p_en | `g2p_en` | `g2p_en` unpinned | English path | Not required by Chinese-only cleaner unless English module is imported | May pull NLTK style data risk | Potential data downloads depending usage | Verify separately | Defer |
| g2pk2 | `g2pk2` | `g2pk2` unpinned | Korean path | Not required by Chinese-only cleaner unless Korean module is imported | Unknown | Unknown | Verify separately | Defer |
| ToJyutping | `ToJyutping` | `ToJyutping` unpinned | Cantonese/Yue path | Not required for Mandarin Chinese path | Unknown | Unknown | Verify separately | Defer |

---

## 5. `jieba_fast` Blocker

Evidence:

- `GPT_SoVITS/text/chinese.py` imports `jieba_fast` and
  `jieba_fast.posseg as psg` unconditionally.
- `GPT_SoVITS/text/chinese2.py` imports the same modules unconditionally.
- `GPT_SoVITS/text/tone_sandhi.py` imports `jieba_fast as jieba`
  unconditionally.
- Used APIs are `setLogLevel`, `posseg.lcut`, and `cut_for_search`.
- No fallback logic to plain `jieba` exists in the inspected source.
- PyPI `jieba-fast 0.53` exposes only a source distribution, uploaded in 2018,
  with no Windows cp310 wheel listed.

Path A - Strict upstream compatibility:

- Install `jieba_fast` exactly as upstream imports it.
- This likely requires a local C/SWIG build on Windows CPython 3.10 and may
  require Visual Studio Build Tools.
- This violates the current no-source-build preference.
- Recommended status: not approved; treat as a blocker-resolution decision.

Path B - Minimal fallback design:

- Plain `jieba` appears API-compatible for the functions actually used:
  `jieba.setLogLevel`, `jieba.posseg.lcut`, and `jieba.cut_for_search`.
- The repository has no existing fallback, so reliable use of plain `jieba`
  would require either a future source patch or a fragile pre-import
  `sys.modules["jieba_fast"] = jieba` monkey patch before importing text modules.
- A source patch would be cleaner but modifies official repo source and is not
  approved in this task.
- Recommended status: viable design candidate only after explicit source-patch
  approval or a dedicated no-source-change shim approval.

---

## 6. OpenCC Findings

Actual repository import:

```python
from opencc import OpenCC
```

Actual repository usage:

```python
OpenCC("s2tw")
```

Findings:

- The repo requirement is `opencc`, and `requirements.txt` also contains
  `--no-binary=opencc`.
- PyPI `OpenCC 1.3.1` currently has a CPython 3.10 Windows x86-64 wheel, but
  upstream full requirements would reject that wheel and attempt source build.
- `opencc-python-reimplemented` has the same import name (`opencc`) and
  documents config names like `s2tw`, but it is not the upstream requirement.
- Substitution must not be assumed. It needs an explicit compatibility probe
  for `OpenCC("s2tw").convert(...)` and any dictionary differences.
- OpenCC conversion is mandatory for the current G2PW default because
  `G2PWPinyin` defaults `enable_non_tradional_chinese=True`.
- It may not be mandatory for a first Simplified-only text probe if G2PW is
  disabled or patched, but current upstream `chinese2.py` does not offer that
  switch.

Recommended action:

- Do not run full `requirements.txt`.
- Do not substitute OpenCC implementations without a future compatibility probe.
- Keep OpenCC as its own future group because upstream source-build policy and
  API shape are separate risks.

---

## 7. G2PW Findings

G2PW is vendored under `GPT_SoVITS/text/g2pw`; there is no direct PyPI package
requirement named `G2PWModel`.

Import chain:

```text
chinese2.py
-> from text.g2pw import G2PWPinyin, correct_pronunciation
-> text.g2pw.__init__
-> text.g2pw.g2pw
-> text.g2pw.onnx_api
```

Runtime initialization:

```text
chinese2.py import
-> is_g2pw = True
-> g2pw = G2PWPinyin(...)
-> G2PWOnnxConverter(...)
-> download_and_decompress(model_dir)
-> AutoTokenizer.from_pretrained(model_source)
-> onnxruntime.InferenceSession(...)
```

Package/runtime dependencies:

- `numpy`
- `onnxruntime` or `onnxruntime-gpu`
- `requests`
- `opencc`
- `pypinyin`
- `transformers`
- local G2PW code and dictionaries

Asset behavior:

- If `model_dir` is missing, `download_and_decompress()` downloads
  `https://www.modelscope.cn/models/kamiorinn/g2pw/resolve/master/G2PWModel_1.1.zip`.
- The default target is under the parent of the configured model dir, ultimately
  `GPT_SoVITS/text/G2PWModel` for the current `chinese2.py` call.
- `docs/cn/README.md` also instructs users to download `G2PWModel.zip` from
  Hugging Face or ModelScope and place it under `GPT_SoVITS/text`.
- `AutoTokenizer.from_pretrained(model_source)` uses
  `GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large` by default via
  `bert_path`; if local assets are absent and offline mode is not enforced,
  Transformers may attempt remote resolution.

Mandatory or avoidable:

- For current v2 Chinese inference path, G2PW is mandatory because
  `is_g2pw = True` is hardcoded and initialized at import time.
- For v1 Chinese path, G2PW is not used, but v1 still depends on `jieba_fast`,
  `cn2an`, and `pypinyin`.
- A non-G2PW fallback exists in code only inside the `if not is_g2pw` branch,
  but the switch is hardcoded to true. Using that fallback requires source patch
  or controlled runtime modification, neither approved here.

Separate future approvals required:

1. Python package install group for G2PW runtime dependencies.
2. G2PW model asset download or manual placement.
3. BERT tokenizer/model asset download or local placement.
4. Import/runtime initialization probe.

---

## 8. cn2an and pypinyin

`cn2an`:

- Repo requirement: `cn2an` unpinned.
- Actual import: `import cn2an`.
- Usage: `cn2an.transform(x, "an2cn")` and Chinese text normalization support.
- PyPI latest checked: `0.5.24`, released 2026-04-22, `py3-none-any` wheel.
- Source-build risk: low.
- External downloads: none found.
- Recommendation: low-risk package, but not useful as the next standalone
  install because upstream Chinese import still blocks on `jieba_fast` and G2PW.

`pypinyin`:

- Repo requirement: `pypinyin` unpinned.
- Actual imports include `lazy_pinyin`, `Style`, `pinyin`,
  `to_finals_tone3`, `to_initials`, pypinyin constants and converter classes.
- PyPI latest checked: `0.55.0`, released 2025-07-20,
  `py2.py3-none-any` wheel.
- Source-build risk: low.
- External downloads: none found.
- Recommendation: low-risk package, but not useful as the next standalone
  install for the same `jieba_fast`/G2PW reasons.

---

## 9. LangSegment and Multilingual Coupling

Actual module:

- The repo vendors `GPT_SoVITS/text/LangSegmenter`, not the old external
  `LangSegment` package.
- It imports `jieba`, `fast_langdetect`, and `split_lang` eagerly.
- It sets a `fast_langdetect` cache directory under
  `GPT_SoVITS/pretrained_models/fast_langdetect`.

Chinese-only behavior:

- `get_phones_and_bert(text, "zh", ...)` calls
  `LangSegmenter.getTexts(text, "zh")`.
- Because `default_lang="zh"` is passed, detected substrings are forced to
  Chinese after the splitter runs.
- This still requires the eager imports of `split_lang` and `fast_langdetect`.

Multilingual modules:

- `cleaner.py` dynamically imports language modules by selected language, so
  `japanese.py`, `korean.py`, `english.py`, and `cantonese.py` are not imported
  by `clean_text(..., "zh", ...)` itself.
- However, full entry points import `LangSegmenter` and `text.chinese`
  eagerly, so Chinese text probing cannot be reduced to only `cn2an` and
  `pypinyin`.
- `pyopenjtalk`, `g2p_en`, `g2pk2`, `ko_pron`, and `ToJyutping` can remain
  deferred unless a future import probe proves a selected entry point imports
  those modules eagerly.

Critical result:

- Do not assume unused languages are safely optional until a controlled import
  graph probe runs under the target environment with network-offline flags.

---

## 10. Model and Dictionary Asset Boundaries

| Asset | Evidence path | Local package or remote | Expected storage path | Required before import | Required before inference | Separate approval |
|---|---|---|---|---|---|---|
| `opencpop-strict.txt` | `GPT_SoVITS/text/opencpop-strict.txt` | Local repo file | Same path | Yes for `chinese.py`/`chinese2.py` import | Yes | No download; included in repo |
| zh normalization modules | `GPT_SoVITS/text/zh_normalization/*.py` | Local repo files | Same path | Yes | Yes | No download |
| G2PW polyphonic dictionaries | `GPT_SoVITS/text/g2pw/polyphonic.*` | Local repo files | Same path | Yes for `text.g2pw.g2pw` | Yes | No download for these files |
| G2PW ONNX model | `G2PWModel_1.1.zip` | Remote if missing | `GPT_SoVITS/text/G2PWModel` | Yes for current `chinese2.py` import because G2PW initializes at import time | Yes | Yes |
| BERT tokenizer/model source | `bert_path` default | Local if present, otherwise Transformers may resolve remote | `GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large` | Yes for G2PW initialization | Yes | Yes |
| OpenCC dictionaries | `opencc` package data | Package asset | Site-packages | Yes when `OpenCC("s2tw")` is constructed | Yes | Package install approval |
| fast_langdetect data/cache | LangSegmenter cache override | Package/model asset, cache under repo pretrained dir | `GPT_SoVITS/pretrained_models/fast_langdetect` | Import constructs detector | Yes for segmentation | Package/asset behavior approval |
| wordsegment corpus data | `wordsegment` package | Package data | Site-packages | No for Chinese-only unless English imported | English only | Defer |
| NLTK data | None found in current requirement/import evidence | Not applicable | Not applicable | No | No | Not approved |
| Hugging Face assets | `AutoTokenizer.from_pretrained()` | Local or remote | `GPT_SoVITS/pretrained_models/...` or hub cache | Yes for G2PW initialization | Yes | Yes |

---

## 11. Staged Chinese Text Groups

### C1 - Low-risk pure-Python normalization

Packages:

- `cn2an==0.5.24`
- `pypinyin==0.55.0`

Purpose:

- Chinese number normalization and pinyin conversion.

Risk:

- Low source-build risk; wheels are platform independent.
- Not sufficient for current repo import because `jieba_fast` is still
  unconditional.

Status:

- Not approved.
- Not selected as the next task because it would not make Chinese imports pass.

### C2 - Upstream tokenizer/segmentation blocker

Packages/design:

- Strict upstream: `jieba_fast==0.53`.
- Fallback design: plain `jieba==0.42.1` with source patch or shim.

Risk:

- `jieba_fast` is source-only on PyPI and likely requires Windows build tools.
- Plain `jieba` fallback requires changing official source or injecting a shim.

Status:

- Not approved.
- Main blocker.

### C3 - OpenCC conversion layer

Candidates:

- `opencc` as upstream requires.
- `opencc-python-reimplemented` only as a compatibility candidate.

Risk:

- Upstream `requirements.txt` forces `--no-binary=opencc`.
- Direct `opencc` cp310 Windows wheel exists, but full requirements would avoid
  it.
- API/config compatibility must be proven.

Status:

- Not approved.

### C4 - G2PW Python runtime dependencies

Packages:

- `onnxruntime-gpu` or `onnxruntime`
- `transformers>=4.43,<=4.50`
- `requests`
- `opencc`
- already-protected `numpy`
- `pypinyin`

Risk:

- Large resolver surface.
- G2PW import initializes model/tokenizer assets.

Status:

- Not approved.

### C5 - G2PW/model assets

Assets:

- `G2PWModel_1.1.zip`
- `GPT_SoVITS/text/G2PWModel`
- Chinese RoBERTa tokenizer/model assets under `GPT_SoVITS/pretrained_models`.

Risk:

- Remote downloads and licensing/storage boundaries.

Status:

- Not approved.

### C6 - Multilingual eager-import dependencies

Packages:

- `split-lang`
- `fast_langdetect`
- `jieba`
- potentially English/Japanese/Korean/Yue packages only if an import probe proves
  they are eager for the selected entry point.

Risk:

- Language detection model/cache behavior.
- Scope expansion into Japanese/Korean/English.

Status:

- Not approved.

---

## 12. Selected Next Task

Selected next task:

```text
TASK-TTS-004E6A - Chinese Text Import Graph Probe
```

Reason:

- No useful install group satisfies all constraints today.
- C1 packages are low risk but insufficient because current import graph still
  fails on `jieba_fast` and can trigger G2PW asset initialization.
- The next useful step is a no-install, network-offline import graph probe that
  confirms exactly which imports fail first in the isolated env and verifies
  whether a future source patch is required before any install group can be
  safely approved.

Do not mark Chinese inference ready.

---

## 13. Future Commands

All commands in this section are:

```text
NOT APPROVED / DO NOT RUN YET
```

### TASK-TTS-004E6A no-install import graph probe

```powershell
$LabRoot = "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab"
$Repo = Join-Path $LabRoot "repos\GPT-SoVITS"
$Py = Join-Path $LabRoot "envs\gpt-sovits-py310\python.exe"
$Report = Join-Path $LabRoot "reports\TASK-TTS-004E6A_IMPORT_GRAPH_PROBE.txt"

$env:PYTHONPATH = (Join-Path $Repo "GPT_SoVITS")
$env:TRANSFORMERS_OFFLINE = "1"
$env:HF_HUB_OFFLINE = "1"
$env:HF_HUB_DISABLE_TELEMETRY = "1"

& $Py -c "import sys, importlib.util; mods=['cn2an','pypinyin','jieba_fast','jieba','opencc','onnxruntime','transformers','split_lang','fast_langdetect','pyopenjtalk','g2p_en','g2pk2','ToJyutping']; [print(m, bool(importlib.util.find_spec(m))) for m in mods]" |
  Set-Content -Encoding UTF8 $Report
```

Expected behavior:

- No package install.
- No model download.
- No source modification.
- No inference/WebUI/audio.
- Records present/missing modules only.

### Hypothetical C1 install after blockers are resolved

This is not selected now and must remain blocked until TASK-TTS-004E6A and
blocker resolution explicitly approve it.

```powershell
$LabRoot = "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab"
$Py = Join-Path $LabRoot "envs\gpt-sovits-py310\python.exe"
$Constraints = Join-Path $LabRoot "constraints\TASK-TTS-004E6A_TEXT_C1_PROTECTED.txt"
$Log = Join-Path $LabRoot "reports\TASK-TTS-004E6A_TEXT_C1_INSTALL.log"

@"
torch==2.7.0+cu128
torchaudio==2.7.0+cu128
numpy==1.26.4
scipy==1.11.4
"@ | Set-Content -Encoding UTF8 $Constraints

& $Py -m pip install `
  --index-url https://pypi.org/simple `
  --only-binary=:all: `
  --upgrade-strategy only-if-needed `
  --constraint $Constraints `
  --report (Join-Path $LabRoot "reports\TASK-TTS-004E6A_TEXT_C1_DRY_RUN_REPORT.json") `
  --dry-run `
  "cn2an==0.5.24" `
  "pypinyin==0.55.0" `
  *>&1 | Tee-Object -FilePath $Log
```

---

## 14. Success Criteria for a Future Chinese Text Task

- Only approved packages are installed.
- Imports succeed for the approved probe target.
- No source build occurs.
- No G2PW model, BERT/tokenizer asset, OpenCC external asset, NLTK data, or
  Hugging Face asset is downloaded without separate approval.
- No Japanese/multilingual packages are installed unless explicitly approved.
- Protected `torch`, `torchaudio`, `numpy`, and `scipy` versions remain
  unchanged.
- CUDA remains available and RTX 3070 remains detected.
- `pip check` remains clean.
- No inference, WebUI, synthesis, audio generation, training, playback, or
  runtime TTS occurs.
- Before/after snapshots are recorded.
- Anaconda base and Dragon Pet AI runtime/backend venv remain unchanged.

---

## 15. Rejection Criteria

Stop if:

- `jieba_fast` requires source compilation.
- The resolver tries to replace torch, torchaudio, numpy, or scipy.
- NumPy 2.x is requested.
- G2PW models download automatically.
- `AutoTokenizer.from_pretrained()` attempts remote resolution.
- OpenCC API/config compatibility is not proven.
- Multilingual eager imports expand scope into Japanese/Korean/English packages.
- Japanese dependencies become mandatory for the selected Chinese probe.
- System PATH/compiler/profile/registry changes are required.
- Any source patch is required without explicit approval.
- Repository evidence contradicts the selected install/probe path.

---

## 16. External Manifest

External manifest path:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E6_CHINESE_TEXT_DEPENDENCY_REVIEW.md
```

This Dragon Pet AI documentation file is the committed copy. The external
manifest mirrors this review for lab-local records and is not staged in the
Dragon Pet AI git repository.

---

## 17. Confirmation

Confirmed during TASK-TTS-004E6:

- No package was installed or uninstalled.
- Protected packages remained unchanged:
  `torch==2.7.0+cu128`, `torchaudio==2.7.0+cu128`,
  `numpy==1.26.4`, `scipy==1.11.4`.
- CUDA remained available.
- RTX 3070 remained detected.
- No model, dictionary, tokenizer, or dataset asset was downloaded.
- No GPT-SoVITS inference, WebUI, training, synthesis, or audio generation ran.
- No GPT-SoVITS source file was modified.
- No Anaconda base, PATH/profile/registry, backend venv, Dragon Pet AI runtime,
  `/chat`, STT, Conversation Mode, Owner Voice, schema, playback, or
  auto-speaking change was made.
- Existing unrelated `docs/開啟方式.txt` remained unrelated and must not be
  staged for this task.

---

## 18. References Checked

Repository-local evidence is primary. Current PyPI metadata was checked only for
wheel/source-build and license-risk planning:

- `https://pypi.org/project/jieba-fast/`
- `https://pypi.org/project/jieba/`
- `https://pypi.org/project/cn2an/`
- `https://pypi.org/project/pypinyin/`
- `https://pypi.org/project/OpenCC/`
- `https://pypi.org/project/opencc-python-reimplemented/`
- `https://pypi.org/project/split-lang/`
- `https://pypi.org/project/fast-langdetect/`
- `https://pypi.org/project/wordsegment/`
- `https://pypi.org/project/regex/`
- `https://pypi.org/project/num2words/`
