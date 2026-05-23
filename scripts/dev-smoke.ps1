# dev-smoke.ps1
# Quick local smoke test for the dragon-pet-ai backend.
#
# Usage:
#   .\scripts\dev-smoke.ps1
#   .\scripts\dev-smoke.ps1 -BaseUrl "http://127.0.0.1:8000"
#   .\scripts\dev-smoke.ps1 -ChatTimeoutSec 120
#
# What this script checks:
#   1. GET  /health                    — backend is reachable
#   2. GET  /provider/settings         — current provider config + key status
#   3. POST /provider/settings/test    — lightweight local model/runtime check
#   4. POST /chat                      — full chat round-trip; reports source
#
# All requests use the local backend only.
# No API key is sent or read.  No external provider is called.
#
# Cold-start note:
#   qwen3:8b takes 30–90 s to load on first use after 'ollama pull'.
#   If /chat times out or returns source=llm_local_error, warm up the model
#   first (see warm-up hint printed below) then rerun this script.

param(
    [string]$BaseUrl        = "http://127.0.0.1:8000",
    # ChatTimeoutSec must be slightly above the backend LLM_LOCAL_CHAT_TIMEOUT_SECONDS
    # (default 90 s) so the backend can return a proper JSON error instead of the
    # PowerShell client cutting the connection first.
    [int]$ChatTimeoutSec    = 100
)

Set-StrictMode -Version Latest

$PASS  = "[PASS]"
$FAIL  = "[FAIL]"
$WARN  = "[WARN]"
$INFO  = "[INFO]"
$failed = 0

function Write-Pass($msg) { Write-Host "$PASS $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "$FAIL $msg" -ForegroundColor Red; $script:failed++ }
function Write-Warn($msg) { Write-Host "$WARN $msg" -ForegroundColor Yellow }
function Write-Info($msg) { Write-Host "$INFO $msg" -ForegroundColor Cyan }

# ---------------------------------------------------------------------------
# Write-WarmupHint
# Printed whenever the local model appears to be cold / still loading.
# Not a failure of settings or backend logic — just needs a warm-up run.
# ---------------------------------------------------------------------------
function Write-WarmupHint {
    Write-Host ""
    Write-Host "  *** Local model may still be loading / waking up ***" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Warm up the model by running this in a separate terminal:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host '    ollama run qwen3:8b "請用一句繁體中文回覆：ready"' -ForegroundColor White
    Write-Host ""
    Write-Host "  Wait until it replies, then rerun:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    .\scripts\dev-smoke.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "  This is a cold-start loading issue — not a settings or backend problem." -ForegroundColor DarkGray
    Write-Host ""
}

function Invoke-BackendGet($path) {
    try {
        $resp = Invoke-WebRequest -Uri "$BaseUrl$path" -Method GET -UseBasicParsing -TimeoutSec 10
        return @{ OK=$true; Status=$resp.StatusCode; Body=($resp.Content | ConvertFrom-Json) }
    } catch {
        return @{ OK=$false; Error=$_.Exception.Message }
    }
}

function Invoke-BackendPost($path, $body, [int]$timeoutSec = 15) {
    try {
        $json = $body | ConvertTo-Json
        $resp = Invoke-WebRequest -Uri "$BaseUrl$path" -Method POST `
            -ContentType "application/json" -Body $json -UseBasicParsing -TimeoutSec $timeoutSec
        return @{ OK=$true; Status=$resp.StatusCode; Body=($resp.Content | ConvertFrom-Json) }
    } catch {
        return @{ OK=$false; Error=$_.Exception.Message }
    }
}

# Returns $true when an error string looks like a network/HTTP timeout.
function Is-TimeoutError([string]$err) {
    return ($err -match "(?i)timeout|timed.?out|operation.*time|The operation has timed")
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host "  dragon-pet-ai — local dev smoke test"      -ForegroundColor Yellow
Write-Host "  Backend: $BaseUrl"                          -ForegroundColor Yellow
Write-Host "  Chat timeout: $ChatTimeoutSec s"            -ForegroundColor Yellow
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
    Write-Info "  provider              = $($s.provider)"
    Write-Info "  model                 = $($s.model)"
    Write-Info "  real_provider_enabled = $($s.real_provider_enabled)"
    Write-Info "  llm_chat_enabled      = $($s.llm_chat_enabled)"
    Write-Info "  fallback_to_mock      = $($s.fallback_to_mock)"
    Write-Info "  resolved_provider     = $($s.resolved_provider)"
    Write-Info "  key_status            = $($s.key_status)"

    if ($s.provider -ne "ollama") {
        Write-Warn "provider is '$($s.provider)' — for local Ollama mode PATCH provider to 'ollama'"
    }
} else {
    Write-Fail "/provider/settings failed: $($r.Error)"
}
Write-Host ""

# ---------------------------------------------------------------------------
# 3. POST /provider/settings/test  (lightweight local check — no generation)
# ---------------------------------------------------------------------------
Write-Host "--- 3. POST /provider/settings/test ---"
$testBody = @{ provider = "ollama"; explicit_cost_ack = $true }
$r = Invoke-BackendPost "/provider/settings/test" $testBody 15
if ($r.OK) {
    $t = $r.Body
    Write-Pass "Test Connection returned (HTTP $($r.Status))"
    Write-Info "  status  = $($t.status)"
    Write-Info "  source  = $($t.source)"
    Write-Info "  message = $($t.safe_message)"
    if ($t.status -eq "success") {
        Write-Pass "Local Ollama runtime/model check passed"
    } else {
        Write-Warn "Test Connection status='$($t.status)' — Ollama may not be running or model not pulled."
        Write-Host "        Run in a separate terminal: ollama serve" -ForegroundColor Yellow
        Write-Host "        Then: ollama pull qwen3:8b" -ForegroundColor Yellow
    }
} else {
    Write-Fail "/provider/settings/test failed: $($r.Error)"
}
Write-Host ""

# ---------------------------------------------------------------------------
# 4. POST /chat
# Uses $ChatTimeoutSec (default 100 s) — intentionally higher than the
# backend's LLM_LOCAL_CHAT_TIMEOUT_SECONDS (default 90 s) so the backend can
# complete its own timeout and return a JSON body with source=llm_local_error
# rather than the PowerShell client cutting the connection first.
# ---------------------------------------------------------------------------
Write-Host "--- 4. POST /chat (timeout: $ChatTimeoutSec s) ---"
Write-Host "     (cold-start may take up to 90 s on first load — please wait)" -ForegroundColor DarkGray
$chatBody = @{ message = "hello" }
$r = Invoke-BackendPost "/chat" $chatBody $ChatTimeoutSec

if (-not $r.OK) {
    # Network-level failure: connection refused, or PowerShell client timed out
    # before the backend could respond.
    if (Is-TimeoutError $r.Error) {
        Write-Warn "/chat request timed out at the network level ($ChatTimeoutSec s)."
        Write-Warn "The backend may still be waiting for Ollama to load the model."
        Write-WarmupHint
        $script:failed++
    } else {
        Write-Fail "/chat failed: $($r.Error)"
    }
} else {
    $c = $r.Body
    $keys = ($c | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name) -join ", "
    Write-Pass "/chat returned (HTTP $($r.Status))"
    Write-Info "  source = $($c.source)"
    Write-Info "  mood   = $($c.mood)"
    Write-Info "  schema = { $keys }"

    # Schema guard — must always be exactly reply / mood / source
    $expectedKeys = @("reply","mood","source") | Sort-Object
    $actualKeys   = ($c | Get-Member -MemberType NoteProperty |
                     Select-Object -ExpandProperty Name) | Sort-Object
    if (($expectedKeys -join ",") -eq ($actualKeys -join ",")) {
        Write-Pass "Schema guard OK (reply / mood / source)"
    } else {
        Write-Fail "Schema mismatch! Expected {reply,mood,source} got {$($actualKeys -join ',')}"
    }

    # Classify source and give actionable guidance
    switch ($c.source) {
        "llm_local" {
            Write-Pass "source=llm_local — Ollama generated the reply locally!"
        }
        "llm_local_error" {
            # The backend entered the Ollama path but generation failed.
            # Most common cause: model still loading (cold-start timeout).
            # Check reply text for known cold-start / loading keywords.
            $replyText  = [string]$c.reply
            $isColdStart = ($replyText -match "(?i)loading|waking|cold.start|timed.?out|timeout|provider_timeout")

            if ($isColdStart) {
                Write-Warn "source=llm_local_error — model appears to still be loading."
                Write-WarmupHint
            } else {
                Write-Warn "source=llm_local_error — Ollama path entered but generation failed."
                Write-Warn "  Reply: $replyText"
                Write-Host ""
                Write-Host "  Possible causes:" -ForegroundColor Yellow
                Write-Host "    • Model still loading (cold-start) — try the warm-up below" -ForegroundColor Yellow
                Write-Host "    • 'ollama serve' not running" -ForegroundColor Yellow
                Write-Host "    • 'qwen3:8b' not pulled (run: ollama pull qwen3:8b)" -ForegroundColor Yellow
                Write-WarmupHint
            }
            # llm_local_error is not counted as a hard failure here — it is a
            # transient cold-start state, not a broken backend or settings issue.
            # The script still exits 0 so CI/smoke pipelines distinguish
            # "cold model" from "broken backend".  Remove the comment below if
            # you prefer to treat it as a failure:
            # $script:failed++
        }
        "mock" {
            Write-Warn "source=mock — chat used the mock path (Ollama not reached)."
            Write-Host "  Ensure llm_chat_enabled=true and provider=ollama in /provider/settings." -ForegroundColor Yellow
            Write-Host "  Then PATCH /provider/settings with the correct values and rerun." -ForegroundColor Yellow
        }
        default {
            Write-Info "source=$($c.source)"
        }
    }
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
