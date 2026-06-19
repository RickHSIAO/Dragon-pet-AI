# TTS Miniconda UTF-8 Retry

**Task:** TASK-TTS-004E2A3
**Status:** BLOCKED - UTF-8 MINICONDA RETRY FAILED / NO FURTHER RETRY PERFORMED
**Date:** 2026-06-19
**Scope:** Approved cleanup of only the failed partial Miniconda install root,
then one retry of the same verified official installer to the same isolated lab
path with process-local UTF-8 settings. No PATH/profile/registry modification,
`conda init`, existing Anaconda removal, provider clone, Conda env creation,
dependency install, PyTorch/CUDA install, model download, training, inference,
WebUI, synthesis, audio generation, runtime wiring, or backend venv change was
performed.

---

## 1. Result

Final status:

```text
BLOCKED - UTF-8 MINICONDA RETRY FAILED / NO FURTHER RETRY PERFORMED
```

The approved partial install directory was deleted after exact path resolution,
then the same verified installer was retried once with process-local UTF-8
settings. The installer still exited with code `2` and left a new partial
install directory. No second retry was performed.

---

## 2. Cleanup Boundary

Deleted only:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\miniconda3
```

The resolved path matched the approved target exactly before deletion. After
deletion:

```text
ExistsAfter: false
```

Preserved:

- Official installer.
- SHA-256 evidence.
- Existing reports.

---

## 3. Retry Boundary

Installer:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\installers\Miniconda3-latest-Windows-x86_64.exe
```

Target:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\miniconda3
```

Process-local UTF-8 settings in the retry process:

```text
PYTHONUTF8=1
PYTHONIOENCODING=utf-8
Console OutputEncoding=utf-8
PowerShell OutputEncoding=utf-8
```

Installer arguments:

```text
/InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /S /D=F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\miniconda3
```

Retry result:

```text
ExitCode: 2
InstallRootExists: true
```

---

## 4. Post-Retry Partial Install

Required file checks after retry:

| Path under install root | Exists |
|---|---:|
| `_conda.exe` | yes |
| `python.exe` | no |
| `Scripts\conda.exe` | no |
| `condabin\conda.bat` | no |
| `Uninstall-Miniconda3.exe` | no |
| `conda-meta` | yes |
| `pkgs` | yes |
| `.step.log` | yes |
| `install.log` | yes, empty |

Post-retry install root timestamps:

- Creation time: `2026-06-19 13:44:27`.
- Last write time: `2026-06-19 13:45:06`.

Residual `_conda.exe --version` reports `conda 26.1.1`, but `_conda.exe info
--base` points to a temporary extraction directory, not the approved install
root. The partial install is not usable.

---

## 5. Failure Log Evidence

`.step.log` after the UTF-8 retry still contains:

- transaction preparation completed;
- transaction execution completed;
- rollback completed;
- `UnicodeDecodeError('cp950', ...)` while reading existing Conda-related
  paths.

Private user paths from the traceback are intentionally omitted from this repo
doc. `install.log` exists but is empty (`0` bytes).

Interpretation: process-local UTF-8 environment variables and PowerShell output
encoding did not prevent the installer rollback. Direct evidence still points
to `cp950` decode failure while reading existing Conda-related paths. Exact
upstream root cause remains unresolved.

---

## 6. Pollution Checks

After retry:

- User PATH contains install root: false.
- Machine PATH contains install root: false.
- Current process PATH contains install root: false.
- User `PYTHONUTF8`: unset.
- Machine `PYTHONUTF8`: unset.
- Current process `PYTHONUTF8`: unset in the post-check shell.
- User `PYTHONIOENCODING`: unset.
- Machine `PYTHONIOENCODING`: unset.
- Current process `PYTHONIOENCODING`: unset in the post-check shell.
- PowerShell profile exists: false.
- `Get-Command python -All` still resolves existing user Python commands only.

Forbidden lab actions remained absent:

- GPT-SoVITS repo: absent.
- Style-Bert-VITS2 repo: absent.
- `gpt-sovits-py310` env: absent.
- Installer preserved: true.
- Reports directory preserved: true.

---

## 7. External Manifest

External retry manifest:

```text
F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2A3_MINICONDA_UTF8_RETRY.md
```

Do not commit external lab reports, installers, partial Miniconda files, or
generated lab artifacts into Dragon Pet AI.

---

## 8. Next Step

TASK-TTS-004E2A3 exhausted the approved one-time retry. The failed partial
install directory exists again because the retry failed with exit code `2`; it
was not deleted after retry because no post-retry cleanup was approved.

Next action requires new explicit approval for a different remediation path,
such as manual cleanup plus alternate installer/tooling, existing Anaconda state
repair, or a different isolated environment strategy.
