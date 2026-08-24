# run_qc_morning.ps1 — Numista QC Suite Morning Smoke Check
# 5-minute fast check: Layer 1 visual guard + Layer 3 health probe only.
# Run from the numista_qc/ directory.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$SCRIPT_DIR   = $PSScriptRoot
$MANIFEST     = "$SCRIPT_DIR\SUITE_MANIFEST.json"
$LOG_FILE     = "$SCRIPT_DIR\SESSION_LOG.md"
$PROD_PROJECT = "studio-9101802118-8c9a8"

function Write-Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $LOG_FILE -Value $line
}

function Abort($code, $msg) {
    Write-Log "PREFLIGHT_FAIL [$code]: $msg"
    # Morning report delivery failure fallback: always write to SESSION_LOG.md + stdout
    Write-Log "MORNING_REPORT: ABORTED ($code) — see SESSION_LOG.md"
    exit 1
}

Write-Log "=== MORNING SMOKE CHECK ==="

# Load manifest
if (-not (Test-Path $MANIFEST)) { Abort "NO_MANIFEST" "SUITE_MANIFEST.json not found." }
$manifest = Get-Content $MANIFEST -Raw | ConvertFrom-Json

# Quick pre-flight
$qaProject = $manifest.qa_project_id
if ($qaProject -eq $PROD_PROJECT) { Abort "PRODUCTION_PROJECT" "QA project ID matches production." }

# Isolation status notice
$isolationMode = $manifest.qa_isolation_mode
if ($isolationMode -eq "interim_sealed_account") {
    $sunsetDate = $manifest.isolation_sunset_date
    if ($sunsetDate) {
        $daysLeft = ([datetime]$sunsetDate - (Get-Date)).Days
        $isolationMsg = "[ISOLATION STATUS] Interim sealed account active. Expires: $sunsetDate. Days remaining: $daysLeft."
        if ($daysLeft -le 7) { Write-Log "WARNING: $isolationMsg" }
        else { Write-Log $isolationMsg }
    }
}

$env:GOOGLE_CLOUD_PROJECT = $qaProject
$morningPass = $true

# Layer 3: API health only (fast)
Write-Log "--- Health probes ---"
$out = & python "$SCRIPT_DIR\layer_3_data\api_health_check.py" 2>&1
$out | ForEach-Object { Write-Log $_ }
if ($LASTEXITCODE -ne 0) { $morningPass = $false; Write-Log "Health probes: FAIL" }
else { Write-Log "Health probes: PASS" }

# Layer 1: contrast + title guards (fast visual check)
Write-Log "--- Layer 1 visual guards ---"
$configPath = "$SCRIPT_DIR\playwright.config.js"
$l1out = & npx playwright test layer_1_ux_visual/ --config $configPath 2>&1
$l1out | ForEach-Object { Write-Log $_ }
if ($LASTEXITCODE -ne 0) { $morningPass = $false; Write-Log "Layer 1: FAIL" }
else { Write-Log "Layer 1: PASS" }

# Final morning report — always written even on failure (fallback guarantee)
if ($morningPass) {
    Write-Log "MORNING_REPORT: PASS — no regressions detected"
} else {
    Write-Log "MORNING_REPORT: FAIL — regressions detected. Check SESSION_LOG.md for details."
    exit 1
}
