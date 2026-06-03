# TASK-250: Install FunASR + ModelScope into the backend venv.
#
# Usage (from repo root):
#   .\scripts\install-funasr.ps1
#
# What this does:
#   1. Locates the backend venv Python.
#   2. Checks Python version — aborts with guidance if >= 3.14 (no cp314 wheels for editdistance).
#   3. Installs funasr and modelscope via pip.
#   4. Prints next-step command to run the probe.
#
# BLOCKED on Python 3.14 (cp314):
#   funasr depends on editdistance, which requires a C extension build.
#   No pre-built cp314 wheels exist; build fails without MSVC 14.0+.
#   Use scripts\create-funasr-venv.ps1 to create a separate .venv-funasr with Python 3.11.
#
# After installation, run the probe to verify:
#   backend\.venv\Scripts\python.exe scripts\funasr_probe.py   (if on 3.11 venv)
#   .venv-funasr\Scripts\python.exe  scripts\funasr_probe.py   (if using create-funasr-venv.ps1)

$ErrorActionPreference = "Stop"

$VenvPython = Join-Path $PSScriptRoot "..\backend\.venv\Scripts\python.exe"
$VenvPython = (Resolve-Path $VenvPython).Path

Write-Host ""
Write-Host "[install-funasr] TASK-250: Installing funasr + modelscope" -ForegroundColor Cyan
Write-Host "[install-funasr] Python: $VenvPython" -ForegroundColor DarkGray
Write-Host ""

# --- Python version guard ---------------------------------------------------
$VersionOutput = & $VenvPython -c "import sys; print(sys.version_info.major, sys.version_info.minor)" 2>&1
$Parts = $VersionOutput -split " "
$PythonMajor = [int]$Parts[0]
$PythonMinor = [int]$Parts[1]

Write-Host "[install-funasr] Python version: $PythonMajor.$PythonMinor" -ForegroundColor DarkGray

if ($PythonMajor -gt 3 -or ($PythonMajor -eq 3 -and $PythonMinor -ge 14)) {
    Write-Host ""
    Write-Host "[install-funasr] BLOCKED: Python $PythonMajor.$PythonMinor (cp$PythonMajor$PythonMinor)" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Problem: funasr depends on 'editdistance' which requires a C extension build." -ForegroundColor Yellow
    Write-Host "           No pre-built cp$PythonMajor$PythonMinor wheels exist on PyPI." -ForegroundColor Yellow
    Write-Host "           Build fails without Microsoft Visual C++ 14.0+ (not required on 3.11)." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Solution A (recommended): create a separate FunASR venv with Python 3.11" -ForegroundColor Cyan
    Write-Host "    .\scripts\create-funasr-venv.ps1" -ForegroundColor White
    Write-Host "    (creates .venv-funasr\ at repo root; does NOT touch backend\.venv)" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  Solution B: install Microsoft C++ Build Tools 14.0+ then re-run this script" -ForegroundColor DarkGray
    Write-Host "    https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor DarkGray
    Write-Host ""
    exit 1
}

# --- Install -----------------------------------------------------------------
& $VenvPython -m pip install funasr modelscope

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[install-funasr] pip install FAILED (exit $LASTEXITCODE)" -ForegroundColor Red
    Write-Host "  If the error mentions a C extension build failure, see the Python version guard" -ForegroundColor Yellow
    Write-Host "  above, or use .\scripts\create-funasr-venv.ps1 for a Python 3.11 venv." -ForegroundColor Yellow
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "[install-funasr] Installation complete." -ForegroundColor Green
Write-Host ""
Write-Host "Next step — run the FunASR probe to verify the full chain:" -ForegroundColor Yellow
Write-Host "  $VenvPython scripts\funasr_probe.py" -ForegroundColor White
Write-Host ""
Write-Host "Then set the provider env var in your BACKEND terminal before starting the backend:" -ForegroundColor Yellow
Write-Host "  `$env:DRAGON_PET_STT_PROVIDER = 'funasr-local'" -ForegroundColor White
Write-Host "  .\scripts\dev-start-backend.ps1" -ForegroundColor White
Write-Host ""
