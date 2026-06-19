# TTS Miniconda Install Failure Diagnostics

**Task:** TASK-TTS-004E2A2
**Status:** BLOCKED - MINICONDA INSTALL ROOT CAUSE NOT IDENTIFIED / NO RETRY PERFORMED
**Date:** 2026-06-19
**Scope:** Diagnostics-only follow-up to the failed TASK-TTS-004E2A isolated
Miniconda bootstrap. No installer retry, GUI install, cleanup, uninstall,
alternate Conda tool, Conda environment creation, package install, model
download, GPT-SoVITS clone, inference, synthesis, audio generation, runtime TTS
wiring, or backend venv change was performed.

---

## 1. Result

Final status:

```text
BLOCKED - MINICONDA INSTALL ROOT CAUSE NOT IDENTIFIED / NO RETRY PERFORMED
```

The strongest direct evidence remains the failed install root `.step.log`: the
installer prepared and executed a transaction, rolled it back, then reported a
`cp950` `UnicodeDecodeError` while reading existing Conda-related paths. That
narrows the failure to installer encoding/path handling around existing Conda
state, but the exact upstream root cause is not proven by diagnostics alone.

---

## 2. Installer Evidence

Installer path:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\installers\Miniconda3-latest-Windows-x86_64.exe
```

Observed metadata:

- Product name: `Miniconda3 py313_26.3.2-2 (64-bit)`.
- Product/File version: `py313_26.3.2-2`.
- File size: `99155816` bytes.
- SHA-256:
  `fe980247dfd30af229a55d9505b57e7c8dfbdb9d24c5bc66fb6078b6a2d53414`.
- Authenticode status: valid.
- Signer: `Anaconda, Inc.`.
- Timestamp certificate: `DigiCert SHA512 RSA4096 Timestamp Responder 2025 1`.
- Alternate data streams: only `:$DATA`; no `Zone.Identifier` stream was
  present.

The installer evidence does not point to a corrupted or unsigned installer.

---

## 3. Partial Install Inventory

Attempted install root:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\miniconda3
```

Directory timestamps:

- Creation time: `2026-06-19 12:38:29`.
- Last write time: `2026-06-19 12:39:07`.

Required file checks:

| Path under install root | Exists |
|---|---:|
| `_conda.exe` | yes |
| `python.exe` | no |
| `Scripts\conda.exe` | no |
| `condabin\conda.bat` | no |
| `Uninstall-Miniconda3.exe` | no |
| `conda-meta` | yes |
| `pkgs` | yes |

Top-level leftovers include `.nonadmin`, `.step.log`, empty `install.log`,
`EULA.txt`, `pre_uninstall.bat`, `_conda.exe`, `conda-meta`, `Lib`, and `pkgs`.
Package metadata under `conda-meta` includes `conda-26.3.2` and
`python-3.13.13`, but the missing root executables mean this is not a valid
isolated Miniconda installation.

---

## 4. Direct Failure Log Evidence

`.step.log` contains these relevant facts:

- `Preparing transaction` completed.
- `Executing transaction` completed.
- `Rolling back transaction` completed.
- A `UnicodeDecodeError('cp950', ...)` was reported while reading existing
  Conda-related paths.

Private user paths from the traceback are intentionally omitted from this repo
doc. `install.log` exists but is empty (`0` bytes).

Interpretation: the immediate logged failure is a `cp950` decode error while
reading existing Conda-related paths, followed by rollback. This narrows the
diagnosis, but it does not prove whether the upstream cause is an installer bug,
existing Conda state, Windows code-page behavior, or the exact combination of
those factors.

---

## 5. Existing Conda State Evidence

Read-only registry inspection found an existing machine-wide Anaconda uninstall
entry:

- Display name: `Anaconda3 2025.12-2 (Python 3.13.9 64-bit)`.
- Uninstall string: `C:\ProgramData\anaconda3\Uninstall-Anaconda3.exe`.

This aligns with the existing Conda path visible in the sanitized `.step.log`
evidence. It is evidence of pre-existing Conda/Anaconda state, not proof that
the registry entry alone caused the installer failure.

---

## 6. Permission and Environment Evidence

- Approved install root length: `58` characters.
- Approved install root contains no non-ASCII characters.
- External lab tools directory ACL allows Modify for authenticated users and
  FullControl for the current owner, administrators, and SYSTEM.
- Partial install root ACL gives the current owner FullControl and read/execute
  access to standard user groups.
- A scoped write probe in the external lab tools directory succeeded, then the
  probe file was removed.
- `Get-Volume -DriveLetter F` was unavailable due access denial; lower
  privilege `Get-PSDrive -Name F` returned the filesystem drive root.

Permission evidence does not show the approved lab tools path as unwritable.

---

## 7. Event and Security Evidence

- Windows Application event log query over the install window found no relevant
  Error/Warning entries for Miniconda, Anaconda, Conda, Python, or installer
  keywords.
- Windows Defender Operational event query over the install window found no
  relevant Error/Warning entries for those keywords.
- Temp directory top-level scan after installer download found only unrelated
  zero-byte `.tmp` files and no named Conda/Miniconda/Anaconda/constructor/NSIS
  diagnostic log.
- Installer signature and hash evidence do not point to a corrupted or unsigned
  installer.

---

## 8. External Manifest

External diagnostics manifest:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2A2_MINICONDA_INSTALL_DIAGNOSTICS.md
```

Do not commit external lab reports, installers, partial Miniconda files, or
generated lab artifacts into Dragon Pet AI.

---

## 9. Forbidden Actions Confirmation

Not performed:

- Installer retry.
- GUI installer run.
- Delete/rename of the partial install.
- Uninstaller run.
- Temp cleanup.
- Install to another path.
- Miniforge, Anaconda, or Micromamba install.
- Conda env creation.
- `conda init`.
- PATH/profile modification.
- GPT-SoVITS or Style-Bert-VITS2 clone.
- Dependency, PyTorch, CUDA, model, or dataset install/download.
- Training, inference, WebUI, synthesis, or audio generation.
- Dragon Pet AI runtime or backend venv change.

---

## 10. Next Step

TASK-TTS-004E2B was later explicitly approved and avoided another Miniconda
retry by using the existing machine-wide Anaconda path. Do not retry Miniconda
again unless a future task explicitly approves it.

---

## 11. TASK-TTS-004E2A3 Follow-Up

TASK-TTS-004E2A3 was later approved for one narrow remediation attempt:

- delete only the failed partial install root;
- preserve installer, hash evidence, and reports;
- retry the same verified installer once to the same isolated path with
  process-local UTF-8 settings.

Result:

```text
BLOCKED - UTF-8 MINICONDA RETRY FAILED / NO FURTHER RETRY PERFORMED
```

See `docs/TTS_MINICONDA_UTF8_RETRY.md`.

---

## 12. TASK-TTS-004E2B Follow-Up

TASK-TTS-004E2B later avoided another Miniconda retry and resumed Phase 1
through the existing machine-wide Anaconda. It created the isolated Python 3.10
env and cloned the official GPT-SoVITS repo without touching the failed partial
Miniconda evidence.

See `docs/TTS_EXISTING_ANACONDA_GPT_SOVITS_PHASE1.md`.
