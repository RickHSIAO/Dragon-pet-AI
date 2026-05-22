# dev-smoke.ps1
# Quick local smoke test for the dragon-pet-ai backend.
#
# Usage:
#   .\scripts\dev-smoke.ps1
#   .\scripts\dev-smoke.ps1 -BaseUrl "http://127.0.0.1:8000"
#
# What this script checks:
#   1. GET  /health                    — backend is reachable
#   2. GET  /provider/settings         — current provider config + key status
#   3. POST /provider/settings/test    — lightweight local model/runtime check
#   4. POST /chat                      — full chat round-trip; reports source
#
# All requests use the local backend only.
# No API key is sent or read.  No external provider is called.

param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

Set-StrictMode -Version Latest

$PASS  = "[PASS]"
$FAIL  = "[FAIL]"
$INFO  = "[INFO]"
$failed = 0

function Write-Pass($msg) { Write-Host "$PASS $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "$FAIL $msg" -ForegroundColor Red; $script:failed++ }
function Write-Info($msg) { Write-Host "$INFO $msg" -ForegroundColor Cyan }

function Invoke-BackendGet($path) {
    try {
        $resp = Invoke-WebRequest -Uri "$BaseUrl$path" -Method GET -UseBasicParsing -TimeoutSec 10
        return @{ OK=$true; Status=$resp.StatusCode; Body=($resp.Content | ConvertFrom-Json) }
    } catch {
        return @{ OK=$false; Error=$_.Exception.Message }
    }
}

function Invoke-BackendPost($path, $body) {
    try {
        $json = $body | ConvertTo-Json
        $resp = Invoke-WebRequest -Uri "$BaseUrl$path" -Method POST `
            -ContentType "application/json" -Body $json -UseBasicParsing -TimeoutSec 15
        return @{ OK=$true; Status=$resp.StatusCode; Body=($resp.Content | ConvertFrom-Json) }
    } catch {
        return @{ OK=$false; Error=$_.Exception.Message }
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "  dragon-pet-ai — local dev smoke test"      -ForegroundColor Yellow
Write-Host "  Backend: $BaseUrl"                          -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""

# ---------------------------------------------------------------------------
# 1. GET /health
# ---------------------------------------------------------------------------
Write-Host "--- 1. GET /health ---"
$r = Invoke-BackendGet "/health"
if ($r.OK -and $r.Body.status -eq "ok") {
    Write-Pass "Backend is reachable (status=ok, service=$($r.Body.service))"
} else {
    Write-Fail "Backend not reachable at $BaseUrl — start dev-start-backend.ps1 first."
    if ($r.Error) { Write-Host "    Error: $($r.Error)" -ForegroundColor DarkGray }
    Write-Host ""
    Write-Host "Aborting smoke — no point testing further without a live backend." -ForegroundColor Red
    exit 1
}
Write-Host ""

# ---------------------------------------------------------------------------
# 2. GET /provider/settings
# ---------------------------------------------------------------------------
Write-Host "--- 2. GET /provider/settings ---"
$r = Invoke-BackendGet "/provider/settings"
if ($r.OK) {
    $s = $r.Body
    Write-Pass "Settings returned (HTTP $($r.Status))"
    Write-Info "  provider          = $($s.provider)"
    Write-Info "  model             = $($s.model)"
    Write-Info "  real_provider_enabled = $($s.real_provider_enabled)"
    Write-Info "  llm_chat_enabled  = $($s.llm_chat_enabled)"
    Write-Info "  fallback_to_mock  = $($s.fallback_to_mock)"
    Write-Info "  resolved_provider = $($s.resolved_provider)"
    Write-Info "  key_status        = $($s.key_status)"

    if ($s.provider -ne "ollama") {
        Write-Host "  HINT: provider is '$($s.provider)' — for local Ollama mode PATCH provider to 'ollama'" -ForegroundColor Yellow
    }
} else {
    Write-Fail "/provider/settings failed: $($r.Error)"
}
Write-Host ""

# ---------------------------------------------------------------------------
# 3. POST /provider/settings/test  (lightweight local check)
# ---------------------------------------------------------------------------
Write-Host "--- 3. POST /provider/settings/test ---"
$testBody = @{ provider = "ollama"; explicit_cost_ack = $true }
$r = Invoke-BackendPost "/provider/settings/test" $testBody
if ($r.OK) {
    $t = $r.Body
    Write-Pass "Test Connection returned (HTTP $($r.Status))"
    Write-Info "  status  = $($t.status)"
    Write-Info "  source  = $($t.source)"
    Write-Info "  message = $($t.safe_message)"
    if ($t.status -eq "success") {
        Write-Pass "Local Ollama runtime/model check passed"
    } else {
        Write-Host "  NOTE: Test Connection status='$($t.status)' — Ollama may not be running or model not pulled." -ForegroundColor Yellow
        Write-Host "        Run: ollama serve   (in another terminal)" -ForegroundColor Yellow
        Write-Host "        Run: ollama pull qwen3:8b" -ForegroundColor Yellow
    }
} else {
    Write-Fail "/provider/settings/test failed: $($r.Error)"
}
Write-Host ""

# ---------------------------------------------------------------------------
# 4. POST /chat
# ---------------------------------------------------------------------------
Write-Host "--- 4. POST /chat ---"
$chatBody = @{ message = "hello" }
$r = Invoke-BackendPost "/chat" $chatBody
if ($r.OK) {
    $c = $r.Body
    $keys = ($c | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name) -join ", "
    Write-Pass "/chat returned (HTTP $($r.Status))"
    Write-Info "  source = $($c.source)"
    Write-Info "  mood   = $($c.mood)"
    Write-Info "  schema = { $keys }"

    # Schema guard — must always be exactly reply / mood / source
    $expectedKeys = @("reply","mood","source") | Sort-Object
    $actualKeys   = ($c | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name) | Sort-Object
    if (($expectedKeys -join ",") -eq ($actualKeys -join ",")) {
        Write-Pass "Schema guard OK (reply / mood / source)"
    } else {
        Write-Fail "Schema mismatch! Expected {reply,mood,source} got {$($actualKeys -join ',')}"
    }

    switch ($c.source) {
        "llm_local"       { Write-Pass "source=llm_local — Ollama generated the reply locally!" }
        "llm_local_error" { Write-Host "  NOTE: source=llm_local_error — Ollama path entered but generation failed." -ForegroundColor Yellow
                            Write-Host "        Make sure 'ollama serve' is running and 'qwen3:8b' is pulled." -ForegroundColor Yellow
                            Write-Host "        First cold-start can take up to 90 s — try again in a moment." -ForegroundColor Yellow }
        "mock"            { Write-Host "  NOTE: source=mock — chat used the mock path." -ForegroundColor Yellow
                            Write-Host "        Ensure llm_chat_enabled=true and provider=ollama in /provider/settings." -ForegroundColor Yellow }
        default           { Write-Info "source=$($c.source)" }
    }
} else {
    Write-Fail "/chat failed: $($r.Error)"
}
Write-Host ""

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Host "============================================" -ForegroundColor Yellow
if ($failed -eq 0) {
    Write-Host "  Smoke result: ALL CHECKS PASSED" -ForegroundColor Green
} else {
    Write-Host "  Smoke result: $failed CHECK(S) FAILED — see above" -ForegroundColor Red
}
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""

if ($failed -gt 0) { exit 1 }
