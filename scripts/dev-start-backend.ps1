# dev-start-backend.ps1
# Local development startup script for the dragon-pet-ai FastAPI backend.
#
# Usage:
#   .\scripts\dev-start-backend.ps1
#
# What this script does:
#   1. Checks that port 8000 is free (exits with guidance if occupied).
#   2. Activates the Python virtual environment inside backend/.venv if present.
#   3. Sets the required environment variables for local Ollama mode.
#   4. Starts uvicorn with --reload for hot-code-reloading.
#
# Prerequisites:
#   - Python 3.10+
#   - backend/.venv already created:   python -m venv .venv
#   - Dependencies installed:          .venv\Scripts\pip install -r requirements.txt
#   - Ollama installed and running:    ollama serve   (in a separate terminal)
#   - Model pulled:                    ollama pull qwen3:8b

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Resolve repo root from script location
# ---------------------------------------------------------------------------
$RepoRoot  = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RepoRoot "backend"

if (-not (Test-Path $BackendDir)) {
    Write-Error "ERROR: backend/ directory not found at $BackendDir"
    exit 1
}

# ---------------------------------------------------------------------------
# Port 8000 check
# ---------------------------------------------------------------------------
$portInUse = $false
try {
    $conn = [System.Net.Sockets.TcpClient]::new()
    $result = $conn.BeginConnect("127.0.0.1", 8000, $null, $null)
    $portInUse = $result.AsyncWaitHandle.WaitOne(200, $false)
    $conn.Close()
} catch {
    $portInUse = $false
}

if ($portInUse) {
    Write-Host ""
    Write-Host "ERROR: Port 8000 is already in use." -ForegroundColor Red
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  1. Stop the existing process using port 8000:"
    Write-Host "       netstat -ano | findstr :8000"
    Write-Host "       taskkill /PID <pid> /F"
    Write-Host "  2. Or wait a moment and retry — a previous uvicorn may still be shutting down."
    Write-Host ""
    exit 1
}

# ---------------------------------------------------------------------------
# Activate virtual environment (if present)
# ---------------------------------------------------------------------------
$VenvActivate = Join-Path $BackendDir ".venv\Scripts\Activate.ps1"
if (Test-Path $VenvActivate) {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & $VenvActivate
} else {
    Write-Host "WARNING: No .venv found at $VenvActivate" -ForegroundColor Yellow
    Write-Host "         Using system Python. Consider running:"
    Write-Host "           cd backend; python -m venv .venv; .venv\Scripts\pip install -r requirements.txt"
    Write-Host ""
}

# ---------------------------------------------------------------------------
# Verify uvicorn is available
# ---------------------------------------------------------------------------
$uvicorn = $null
try { $uvicorn = Get-Command uvicorn -ErrorAction Stop } catch {}
if (-not $uvicorn) {
    # Try via python -m uvicorn as a fallback probe
    $probe = python -m uvicorn --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: uvicorn not found." -ForegroundColor Red
        Write-Host "       Inside the backend directory, run:"
        Write-Host "         .venv\Scripts\pip install -r requirements.txt"
        Write-Host ""
        exit 1
    }
    Write-Host "uvicorn not on PATH; will use: python -m uvicorn" -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# Environment variables
# ---------------------------------------------------------------------------
$env:PYTHONIOENCODING   = "utf-8"
$env:LLM_PROVIDER_NAME  = "ollama"
$env:LLM_MODEL          = "qwen3:8b"
$env:LLM_PROVIDER_ENABLED = "true"
$env:LLM_CHAT_ENABLED   = "true"
# Timeout: allow 90 s for first cold-start generation (model may need to load).
$env:LLM_LOCAL_CHAT_TIMEOUT_SECONDS = "90"
# DB and settings files live inside backend/data/ (git-ignored).
# Leaving DB_PATH and SETTINGS_FILE_PATH unset uses the production defaults.

# STT provider (TASK-249): read from calling shell; safe default is faster-whisper-local.
# To use funasr-local or sherpa-onnx-local, set this env var BEFORE running this script
# in *this* terminal (not the Electron terminal), then restart the backend:
#   $env:DRAGON_PET_STT_PROVIDER = "funasr-local"
#   .\scripts\dev-start-backend.ps1
$sttProviderDisplay = if ($env:DRAGON_PET_STT_PROVIDER) {
    $env:DRAGON_PET_STT_PROVIDER
} else {
    "(not set — default: faster-whisper-local)"
}

# ---------------------------------------------------------------------------
# Start backend
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host " dragon-pet-ai — backend (Ollama mode)   " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  LLM Provider : ollama (qwen3:8b)"
Write-Host "  STT Provider : $sttProviderDisplay" -ForegroundColor $(if ($env:DRAGON_PET_STT_PROVIDER) { "Cyan" } else { "DarkGray" })
Write-Host "  Port         : 8000"
Write-Host "  Reload       : enabled"
Write-Host "  DB           : backend/data/dragon_pet.db (default)"
Write-Host "  Settings     : backend/data/provider_settings.json (default)"
Write-Host ""
Write-Host "Tip: Make sure 'ollama serve' is running in another terminal."
Write-Host "     If this is the first chat after a model pull, the first"
Write-Host "     request may take up to 90 s while the model loads."
Write-Host ""
Write-Host "STT Tip: DRAGON_PET_STT_PROVIDER must be set in THIS terminal before starting" -ForegroundColor DarkYellow
Write-Host "         the backend. Setting it in the Electron terminal has no effect." -ForegroundColor DarkYellow
Write-Host "         Uvicorn startup log will show: [stt_service] STT provider resolved=..." -ForegroundColor DarkYellow
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

Set-Location $BackendDir

if ($uvicorn) {
    uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} else {
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
}
