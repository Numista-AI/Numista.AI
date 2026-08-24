# run_qc.ps1 — Numista QC Suite Master Entry Point
# Windows PowerShell. Run from the numista_qc/ directory.
# Usage: .\run_qc.ps1 [-Layer <1|2|3|4|all>] [-Verbose]

param(
    [string]$Layer = "all",
    [switch]$Verbose
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$SCRIPT_DIR   = $PSScriptRoot
$MANIFEST     = "$SCRIPT_DIR\SUITE_MANIFEST.json"
$LOG_FILE     = "$SCRIPT_DIR\SESSION_LOG.md"
$PROD_PROJECT = "studio-9101802118-8c9a8"

# ---- Helpers ---------------------------------------------------------------
function Write-Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $LOG_FILE -Value $line
}

function Abort($code, $msg) {
    Write-Log "PREFLIGHT_FAIL [$code]: $msg"
    Add-Content -Path $LOG_FILE -Value "SUITE_RESULT: ABORTED ($code)"
    exit 1
}

# ---- Load manifest ---------------------------------------------------------
if (-not (Test-Path $MANIFEST)) {
    Abort "NO_MANIFEST" "SUITE_MANIFEST.json not found at $MANIFEST"
}
$manifest = Get-Content $MANIFEST -Raw | ConvertFrom-Json

# ---- PRE-FLIGHT CHECK 1: Production project ID ----------------------------
$qaProject = $manifest.qa_project_id
if (-not $qaProject -or $qaProject -eq "REPLACE_WITH_QA_PROJECT_ID") {
    Abort "UNCONFIGURED" "qa_project_id not set in SUITE_MANIFEST.json. Provision QA project first."
}
if ($qaProject -eq $PROD_PROJECT) {
    Abort "PRODUCTION_PROJECT" "qa_project_id matches the production project ($PROD_PROJECT). Refusing to run."
}
Write-Log "QA project: $qaProject"

# ---- PRE-FLIGHT CHECK 2: Forbidden accounts --------------------------------
$credFile = $env:GOOGLE_APPLICATION_CREDENTIALS
if ($credFile -and (Test-Path $credFile)) {
    $credJson = Get-Content $credFile -Raw | ConvertFrom-Json
    $credEmail = $credJson.client_email
    foreach ($forbidden in $manifest.forbidden_accounts) {
        if ($credEmail -like "*$forbidden*") {
            Abort "FORBIDDEN_ACCOUNT" "Credential $credEmail matches forbidden account $forbidden."
        }
    }
    Write-Log "Credential email: $credEmail (not forbidden)"
}

# ---- PRE-FLIGHT CHECK 3: Isolation sunset ----------------------------------
$isolationMode = $manifest.qa_isolation_mode
if ($isolationMode -eq "interim_sealed_account") {
    $sunsetDate = $manifest.isolation_sunset_date
    if (-not $sunsetDate) {
        # First run: set the sunset date to today + 30 days
        $sunset = (Get-Date).AddDays(30).ToString("yyyy-MM-dd")
        $manifest.isolation_sunset_date = $sunset
        $manifest | ConvertTo-Json -Depth 10 | Set-Content $MANIFEST
        Write-Log "Interim account sunset date set: $sunset (30 days from today)"
        $sunsetDate = $sunset
    }
    $today   = Get-Date -Format "yyyy-MM-dd"
    $daysLeft = ([datetime]$sunsetDate - [datetime]$today).Days
    if ($daysLeft -le 0) {
        Abort "ISOLATION_SUNSET_EXCEEDED" "Interim sealed account expired on $sunsetDate. Provision the dedicated QA project and update qa_project_id."
    }
    $isolationMsg = "[ISOLATION STATUS] Interim sealed account active. Expires: $sunsetDate. Days remaining: $daysLeft."
    if ($daysLeft -le 7) {
        Write-Log "WARNING: $isolationMsg"
    } else {
        Write-Log $isolationMsg
    }
}

# ---- PRE-FLIGHT CHECK 4: Seed fixtures ------------------------------------
Write-Log "Running seed_qc_fixtures.py --check..."
$seedScript = "$SCRIPT_DIR\layer_3_data\seed_qc_fixtures.py"
$seedResult = & python $seedScript --check 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Log "Fixtures missing. Running seed_qc_fixtures.py..."
    & python $seedScript
    if ($LASTEXITCODE -ne 0) {
        Abort "FIXTURE_SEED_FAILED" "seed_qc_fixtures.py failed. Cannot run suite without fixtures."
    }
}
Write-Log "Fixtures OK."

# ---- Set environment -------------------------------------------------------
$env:GOOGLE_CLOUD_PROJECT = $qaProject
Write-Log "GOOGLE_CLOUD_PROJECT set to $qaProject"

# ---- Run layers ------------------------------------------------------------
$suitePass = $true

function Run-Layer1 {
    Write-Log "=== LAYER 1: UX Visual Guard ==="
    $configPath = "$SCRIPT_DIR\playwright.config.js"
    $result = & npx playwright test layer_1_ux_visual/ --config $configPath 2>&1
    $result | ForEach-Object { Write-Log $_ }
    if ($LASTEXITCODE -ne 0) { $script:suitePass = $false; Write-Log "LAYER 1: FAIL" }
    else { Write-Log "LAYER 1: PASS" }
}

function Run-Layer2 {
    Write-Log "=== LAYER 2: Functional ==="
    $configPath = "$SCRIPT_DIR\playwright.config.js"
    $result = & npx playwright test layer_2_functional/ --config $configPath 2>&1
    $result | ForEach-Object { Write-Log $_ }
    if ($LASTEXITCODE -ne 0) { $script:suitePass = $false; Write-Log "LAYER 2: FAIL" }
    else { Write-Log "LAYER 2: PASS" }
}

function Run-Layer3 {
    Write-Log "=== LAYER 3: Data Audit ==="
    $scripts = @(
        "$SCRIPT_DIR\layer_3_data\api_health_check.py",
        "$SCRIPT_DIR\layer_3_data\account_integrity.py",
        "$SCRIPT_DIR\layer_3_data\coin_data_audit.py"
    )
    foreach ($s in $scripts) {
        $name = Split-Path $s -Leaf
        $args = if ($Verbose) { "--verbose" } else { "" }
        $out = & python $s $args 2>&1
        $out | ForEach-Object { Write-Log $_ }
        if ($LASTEXITCODE -ne 0) { $script:suitePass = $false; Write-Log "$name FAIL" }
        else { Write-Log "$name PASS" }
    }
}

function Run-Layer4 {
    Write-Log "=== LAYER 4: Self-Update (feedback mining only) ==="
    $miner = "$SCRIPT_DIR\layer_4_self_update\feedback_miner.py"
    if (Test-Path $miner) {
        $out = & python $miner 2>&1
        $out | ForEach-Object { Write-Log $_ }
        if ($LASTEXITCODE -ne 0) { Write-Log "feedback_miner.py WARN (non-fatal)" }
        else { Write-Log "feedback_miner.py PASS" }
    }
    Write-Log "Note: code_reader.py and test_synthesizer.py run nightly only (not in main suite run)."
}

switch ($Layer.ToLower()) {
    "1"   { Run-Layer1 }
    "2"   { Run-Layer2 }
    "3"   { Run-Layer3 }
    "4"   { Run-Layer4 }
    "all" { Run-Layer1; Run-Layer2; Run-Layer3; Run-Layer4 }
    default { Abort "INVALID_LAYER" "Layer must be 1, 2, 3, 4, or all." }
}

# ---- Final result ----------------------------------------------------------
if ($suitePass) {
    Write-Log "SUITE_RESULT: PASS"
} else {
    Write-Log "SUITE_RESULT: FAIL — check SESSION_LOG.md for details"
    exit 1
}
