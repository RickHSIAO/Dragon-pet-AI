# GPT-SoVITS Chinese Import Graph Probe

**Task:** TASK-TTS-004E6A
**Status:** DONE - GPT-SOVITS CHINESE IMPORT GRAPH PROBE COMPLETE / NO INSTALL OR DOWNLOAD PERFORMED
**Date:** 2026-06-25
**Scope:** Static AST import-graph probe for GPT-SoVITS Chinese text processing
in the isolated external lab. No package install, uninstall, requirements
install, model/dictionary/tokenizer download, G2PW initialization, module import,
WebUI, training, inference, synthesis, audio generation, GPT-SoVITS source edit,
Dragon Pet AI runtime edit, `/chat`, STT, Conversation Mode, Owner Voice Gate,
schemas, playback, auto-speaking, Anaconda base, PATH/profile/registry, or
backend venv change was performed.

---

## 1. Verified State

Dragon Pet AI rollback target before this task:

```text
021bfdb
docs: review GPT-SoVITS Chinese text dependencies
```

The unrelated local modification remained preserved and unstaged:

```text
docs/開啟方式.txt
```

External lab:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab
```

Target environment:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe
Python 3.10.20
```

GPT-SoVITS repository:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS
commit: b2cff0cd0abd0ac134a16ae7a9695f88e8826104
```

The probe verified the commit read-only via `.git\refs\heads\main`.

---

## 2. Probe Added

Script:

```text
scripts/tts_gpt_sovits_chinese_import_graph_probe.py
```

CLI:

```powershell
.\backend\.venv\Scripts\python.exe `
  scripts\tts_gpt_sovits_chinese_import_graph_probe.py `
  --repo "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS" `
  --env-python "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe" `
  --pretty
```

Supported options:

- `--repo`
- `--env-python`
- `--output-dir`
- `--pretty`
- `--no-write`

Default generated reports are ignored by Git:

```text
outputs/tts_gpt_sovits_chinese_import_graph/YYYYMMDD/
```

Generated local reports from this run:

```text
outputs/tts_gpt_sovits_chinese_import_graph/20260625/tts_gpt_sovits_chinese_import_graph_probe.json
outputs/tts_gpt_sovits_chinese_import_graph/20260625/tts_gpt_sovits_chinese_import_graph_probe.md
```

External manifest:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E6A_CHINESE_IMPORT_GRAPH_PROBE.md
```

---

## 3. Static Analysis Summary

The probe used Python AST parsing only. It did not import or execute target
GPT-SoVITS modules.

Run summary:

- Inspected files: `69`
- Import edges: `808`
- Top-level executable statements: `1052`
- GPT-SoVITS commit analyzed: `b2cff0cd0abd0ac134a16ae7a9695f88e8826104`
- Selected next task: `TASK-TTS-004E6B - jieba_fast Windows Resolution Design`

Availability checks used only `importlib.util.find_spec(...)` in the target
Python. No candidate package was imported.

Checked packages all reported unavailable in the target env at probe time:

```text
cn2an
pypinyin
jieba
jieba_fast
opencc
G2PW
LangSegment
split_lang
fast_langdetect
regex
num2words
wordsegment
nltk
transformers
tokenizers
onnxruntime
pyopenjtalk
```

---

## 4. Chinese Import Graph Findings

The v1 Chinese path still depends on normalization, segmentation, pinyin, tone
sandhi, and OpenCC-related conversion boundaries:

- `cn2an`
- `pypinyin`
- `jieba_fast`
- `jieba_fast.posseg`
- `opencc`
- local `text.zh_normalization`
- local `text.tone_sandhi`
- local `text.symbols`

The probe found `jieba_fast` in `5` import locations. Plain `jieba` has plausible
API equivalents for the observed module and `posseg` usage, but aliasing or
import hooks should remain design-only until Chinese text regression fixtures
prove behavior parity.

OpenCC remains an implementation-contract risk. The expected contract is
`opencc.OpenCC(config).convert(text)`. A substitution with
`opencc-python-reimplemented` is only plausibly drop-in if the import path,
config names, and `convert(text)` behavior match the GPT-SoVITS source.

---

## 5. chinese2 / G2PW Findings

`GPT_SoVITS/text/chinese2.py` has import-time G2PW risk:

- `is_g2pw = True` is set at module level.
- The `if is_g2pw:` block imports `G2PWPinyin` and
  `correct_pronunciation` from local `text.g2pw`.
- `G2PWPinyin(...)` is constructed at module level.
- The constructor receives `model_dir="GPT_SoVITS/text/G2PWModel"`.
- The constructor receives `model_source=os.environ.get("bert_path", ...)`.

Static conclusion:

```text
Importing chinese2.py would require the G2PW local package path immediately,
would require or resolve model/tokenizer assets immediately, may reach download
or asset-resolution paths depending on local asset state, and can fail before a
Chinese-processing function is called.
```

The probe therefore does not import `chinese2.py`.

---

## 6. Multilingual Eager Imports

The report separates Chinese execution requirements from eager multilingual
imports.

Summary:

- Chinese execution closure edges: `133`
- Multilingual eager import closure edges: `39`
- Eager-import-only dependency edges: `24`

Eager coupling can pull in non-Chinese language packages or model/dictionary
families through cleaner/package initialization paths. Chinese-only readiness
should not be declared until this coupling is isolated or explicitly accepted.

---

## 7. Minimum Dependency Closures

### Closure A - Pure normalization

Includes pure text normalization packages and local `zh_normalization` modules.
This is useful independently but does not unblock Chinese phones by itself.

### Closure B - Chinese segmentation and pinyin

Includes `jieba_fast`, `pypinyin`, `cn2an`, OpenCC contract behavior, tone
sandhi, and local symbol mapping. This is the current practical blocker for the
v1 Chinese path because `jieba_fast` remains the Windows resolution problem.

### Closure C - chinese2 / G2PW

Includes local `text.g2pw`, G2PW model/config assets, ONNX/runtime references,
tokenizer assets, and possible asset-resolution/download behavior. This needs a
separate asset-boundary review before any install or import attempt.

### Closure D - Eager multilingual coupling

Includes language modules that may load before Chinese-only execution. This
needs source-boundary review if Chinese-only loading must avoid non-Chinese
dependencies.

---

## 8. Selected Next Task

Selected next task:

```text
TASK-TTS-004E6B - jieba_fast Windows Resolution Design
```

Rationale:

- `jieba_fast` is directly present in the Chinese import path.
- It appears before G2PW asset work can make Chinese text runtime usable.
- Plain `jieba` fallback looks technically plausible, but needs an explicit
  design and regression-fixture decision before any source patch, shim,
  `sitecustomize`, import hook, or dependency substitution.

No install task is selected by this probe.

---

## 9. Validation

Validation commands:

```powershell
.\backend\.venv\Scripts\python.exe -m py_compile `
  scripts\tts_gpt_sovits_chinese_import_graph_probe.py

.\backend\.venv\Scripts\python.exe `
  scripts\tts_gpt_sovits_chinese_import_graph_probe.py `
  --help

.\backend\.venv\Scripts\python.exe `
  scripts\tts_gpt_sovits_chinese_import_graph_probe.py `
  --repo "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS" `
  --env-python "F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310\python.exe" `
  --pretty

.\backend\.venv\Scripts\python.exe -m pytest `
  backend\tests\test_tts_gpt_sovits_chinese_import_graph_probe.py `
  -v `
  -p no:cacheprovider `
  --basetemp=backend.pytest-tmp-tts004e6a
```

Validation result at documentation time:

```text
py_compile PASS
--help PASS
probe PASS
pytest 9 passed
```

Desktop smoke and final diff checks are recorded in the final task report.

---

## 10. Safety Confirmations

- No GPT-SoVITS target module was imported or executed.
- No package was installed or uninstalled.
- No dependency resolver was run.
- No model, dictionary, tokenizer, or audio file was downloaded.
- No G2PW model was initialized.
- No WebUI, training, inference, synthesis, or audio generation occurred.
- No external GPT-SoVITS source file was modified.
- No protected package or target Conda environment file was modified.
- No Anaconda base, PATH, PowerShell profile, or registry change occurred.
- No Dragon Pet AI runtime source, `/chat`, STT, Conversation Mode, Owner Voice
  Gate, schema, playback, or auto-speaking behavior changed.
- `docs/開啟方式.txt` remained preserved and must stay unstaged.
