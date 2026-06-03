# TASK-250: Create a separate FunASR venv using Python 3.11.
#
# Background:
#   backend\.venv uses Python 3.14, but funasr depends on editdistance which
#   has no cp314 pre-built wheels — C extension build requires MSVC 14.0+.
#   This script creates .venv-funasr\ at repo root using py -3.11, which has
#   pre-built cp311 wheels for all funasr dependencies.
#
# Usage (from repo root):
#   .\scripts\create-funasr-venv.ps1
#
# What this does:
#   1. Finds py -3.11 (or py -3.10 as fallback).
#   2. Creates .venv-funasr\ at repo root (does NOT touch backend\.venv).
#   3. Installs funasr + modelscope into .venv-funasr.
#   4. Prints next-step probe command.
#
# After creation, run the probe:
#   .venv-funasr\Scripts\python.exe scripts\funasr_probe.py
#
# .venv-funasr\ is listed in .gitignore — model cache is NOT in the repo.

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$VenvDir  = Join-Path $RepoRoot ".venv-funasr"

Write-Host ""
Write-Host "[create-funasr-venv] TASK-250: Creating FunASR venv (Python 3.11)" -ForegroundColor Cyan
Write-Host "[create-funasr-venv] Target: $VenvDir" -ForegroundColor DarkGray
Write-Host ""

# --- Find Python 3.11 (or 3.10 fallback) ------------------------------------
$PyExe = $null
$PyVersion = $null

foreach ($ver in @("3.11", "3.10")) {
    $test = py -$ver -c "import sys; print(sys.version_info.major, sys.version_info.minor)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $PyExe = "py"
        $PyFlag = "-$ver"
        $PyVersion = $ver
        break
    }
}

if ($null -eq $PyExe) {
    Write-Host "[create-funasr-venv] ERROR: Python 3.11 or 3.10 not found via py launcher." -ForegroundColor Red
    Write-Host "  Install Python 3.11 from https://www.python.org/downloads/release/python-3119/" -ForegroundColor Yellow
    Write-Host "  Then re-run this script." -ForegroundColor Yellow
    exit 1
}

Write-Host "[create-funasr-venv] Found Python $PyVersion via py launcher." -ForegroundColor Green

# --- Create venv -------------------------------------------------------------
if (Test-Path $VenvDir) {
    Write-Host "[create-funasr-venv] .venv-funasr already exists — skipping venv creation." -ForegroundColor DarkGray
} else {
    Write-Host "[create-funasr-venv] Creating venv ..." -ForegroundColor DarkGray
    & py $PyFlag -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[create-funasr-venv] venv creation FAILED." -ForegroundColor Red
        exit 1
    }
    Write-Host "[create-funasr-venv] venv created." -ForegroundColor Green
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

# --- Install funasr + modelscope ---------------------------------------------
Write-Host ""
Write-Host "[create-funasr-venv] Installing funasr + modelscope ..." -ForegroundColor Cyan
Write-Host "[create-funasr-venv] (this may take a few minutes)" -ForegroundColor DarkGray
Write-Host ""

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install funasr modelscope

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[create-funasr-venv] pip install FAILED (exit $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "[create-funasr-venv] Installation complete." -ForegroundColor Green
Write-Host ""
Write-Host "Next step — run the FunASR probe to verify the full chain:" -ForegroundColor Yellow
Write-Host "  $VenvPython scripts\funasr_probe.py" -ForegroundColor White
Write-Host ""
Write-Host "The first probe run will auto-download paraformer-zh (~500 MB) to ModelScope cache." -ForegroundColor DarkGray
Write-Host ""
Write-Host "NOTE: The backend still runs on backend\.venv (Python 3.14)." -ForegroundColor Yellow
Write-Host "      The .venv-funasr is for probe / quality smoke only — it does NOT integrate" -ForegroundColor Yellow
Write-Host "      with the live backend until a FunASR bridge is designed for Python 3.11." -ForegroundColor Yellow
Write-Host ""
