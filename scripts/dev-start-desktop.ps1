# dev-start-desktop.ps1
# Local development startup script for the dragon-pet-ai Electron desktop app.
#
# Usage:
#   .\scripts\dev-start-desktop.ps1
#
# What this script does:
#   1. Checks that node_modules/ exists (prompts npm install if missing).
#   2. Clears ELECTRON_RUN_AS_NODE (avoids Electron running as plain Node).
#   3. Uses npm.cmd instead of npm (avoids PowerShell execution-policy errors
#      caused by npm.ps1).
#   4. Starts Electron in dev mode via npm.cmd run dev.
#
# Prerequisites:
#   - Node.js 18+ and npm installed and on PATH.
#   - Backend already running on http://localhost:8000
#     (use .\scripts\dev-start-backend.ps1 in another terminal).

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
$RepoRoot   = Split-Path -Parent $PSScriptRoot
$DesktopDir = Join-Path $RepoRoot "apps\desktop"

if (-not (Test-Path $DesktopDir)) {
    Write-Error "ERROR: apps/desktop/ directory not found at $DesktopDir"
    exit 1
}

# ---------------------------------------------------------------------------
# Check node_modules
# ---------------------------------------------------------------------------
$NodeModules = Join-Path $DesktopDir "node_modules"
if (-not (Test-Path $NodeModules)) {
    Write-Host ""
    Write-Host "ERROR: node_modules/ not found." -ForegroundColor Red
    Write-Host "       Run this first (from the repo root or apps/desktop):" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "         cd apps\desktop"
    Write-Host "         npm.cmd install"
    Write-Host ""
    exit 1
}

# ---------------------------------------------------------------------------
# Clear ELECTRON_RUN_AS_NODE
# Electron respects this env var to run as a plain Node.js process instead of
# the desktop application.  It must not be set when launching the app UI.
# ---------------------------------------------------------------------------
if ($env:ELECTRON_RUN_AS_NODE) {
    Write-Host "Clearing ELECTRON_RUN_AS_NODE (was: $($env:ELECTRON_RUN_AS_NODE))" -ForegroundColor Yellow
    $env:ELECTRON_RUN_AS_NODE = ""
    Remove-Item Env:\ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
}

# ---------------------------------------------------------------------------
# Verify npm.cmd is available
# npm.cmd is the Windows CMD wrapper for npm — it always works from PowerShell.
# Do NOT use 'npm' directly; PowerShell may resolve it to npm.ps1 and fail
# with "running scripts is disabled on this system" (execution-policy error).
# ---------------------------------------------------------------------------
$npmCmd = $null
try { $npmCmd = Get-Command npm.cmd -ErrorAction Stop } catch {}
if (-not $npmCmd) {
    Write-Host ""
    Write-Host "ERROR: npm.cmd not found. Is Node.js installed and on PATH?" -ForegroundColor Red
    Write-Host "       Download from https://nodejs.org" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# ---------------------------------------------------------------------------
# Start Electron
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host " dragon-pet-ai — Electron desktop (dev)  " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Backend expected at : http://localhost:8000"
Write-Host "  Mode                : dev (--dev flag passed to Electron)"
Write-Host ""
Write-Host "Tip: If the chat area shows 'Backend not reachable', make sure"
Write-Host "     dev-start-backend.ps1 is running in another terminal."
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

Set-Location $DesktopDir
npm.cmd run dev
