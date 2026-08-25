# run_qc.ps1 - Numista QC Suite Master Entry Point
# Windows PowerShell. Run from the numista_qc/ directory OR called by run_tests.ps1.
# Usage: .\run_qc.ps1 [-Layer <1|2|3|4|all>] [-SkipFlutterChecks] [-Verbose]

param(
    [string]$Layer = "all",
    [switch]$SkipFlutterChecks,   # Set by run_tests.ps1 to avoid double flutter run
    [switch]$Verbose
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

$SCRIPT_DIR   = $PSScriptRoot
$MANIFEST     = "$SCRIPT_DIR\SUITE_MANIFEST.json"
$LOG_FILE     = "$SCRIPT_DIR\SESSION_LOG.md"
$PROD_PROJECT = "studio-9101802118-8c9a8"
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR

# ---- Helpers ---------------------------------------------------------------
function Write-Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $LOG_FILE -Value $line -ErrorAction SilentlyContinue
}

function Abort($code, $msg) {
    Write-Log "PREFLIGHT_FAIL [$code]: $msg"
    Add-Content -Path $LOG_FILE -Value "SUITE_RESULT: ABORTED ($code)" -ErrorAction SilentlyContinue
    exit 1
}

# ---- Load manifest ---------------------------------------------------------
if (-not (Test-Path $MANIFEST)) {
    Abort "NO_MANIFEST" "SUITE_MANIFEST.json not found at $MANIFEST"
}
$manifest = Get-Content $MANIFEST -Raw | ConvertFrom-Json

# ---- PRE-FLIGHT CHECK 0: qc_uid must be set and not a placeholder ----------
$qcUid = $manifest.qc_uid
if (-not $qcUid -or $qcUid -eq '' -or $qcUid -eq 'REPLACE_WITH_QA_USER_UID') {
    Abort "QC_UID_NOT_SET" "qc_uid is missing or still a placeholder in SUITE_MANIFEST.json. Create a test user in numista-qc Firebase Authentication, copy the UID, and set it in SUITE_MANIFEST.json before running any layer."
}
Write-Log "QA UID: $qcUid"

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
    try {
        $credJson = Get-Content $credFile -Raw | ConvertFrom-Json
        $credEmail = $credJson.client_email
        foreach ($forbidden in $manifest.forbidden_accounts) {
            if ($credEmail -like "*$forbidden*") {
                Abort "FORBIDDEN_ACCOUNT" "Credential $credEmail matches forbidden account $forbidden."
            }
        }
        Write-Log "Credential email: $credEmail (not forbidden)"
    } catch {
        Write-Log "WARN: Could not parse credential file for forbidden-account check."
    }
}

# ---- PRE-FLIGHT CHECK 3: Isolation sunset ----------------------------------
$isolationMode = $manifest.qa_isolation_mode
if ($isolationMode -eq "interim_sealed_account") {
    $sunsetDate = $manifest.isolation_sunset_date
    if (-not $sunsetDate) {
        $sunset = (Get-Date).AddDays(30).ToString("yyyy-MM-dd")
        $manifest.isolation_sunset_date = $sunset
        $manifest | ConvertTo-Json -Depth 10 | Set-Content $MANIFEST
        Write-Log "Interim account sunset date set: $sunset (30 days from today)"
        $sunsetDate = $sunset
    }
    $daysLeft = ([datetime]$sunsetDate - (Get-Date)).Days
    if ($daysLeft -le 0) {
        Abort "ISOLATION_SUNSET_EXCEEDED" "Interim sealed account expired on $sunsetDate. Provision the dedicated QA project and update qa_project_id."
    }
    $isolationMsg = "[ISOLATION STATUS] Interim sealed account active. Expires: $sunsetDate. Days remaining: $daysLeft."
    if ($daysLeft -le 7) { Write-Log "WARNING: $isolationMsg" } else { Write-Log $isolationMsg }
}

$sunsetDate   = $manifest.isolation_sunset_date
$daysLeft     = if ($sunsetDate) { ([datetime]$sunsetDate - (Get-Date)).Days } else { 999 }

# ---- PRE-FLIGHT CHECK 4: Seed fixtures ------------------------------------
Write-Log "Running seed_qc_fixtures.py --check..."
$seedScript = "$SCRIPT_DIR\layer_3_data\seed_qc_fixtures.py"
$null = & python $seedScript --check 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Log "Fixtures missing. Running seed_qc_fixtures.py..."
    & python $seedScript
    if ($LASTEXITCODE -ne 0) {
        Abort "FIXTURE_SEED_FAILED" "seed_qc_fixtures.py failed. Cannot run suite without fixtures."
    }
}
Write-Log "Fixtures OK."

# ---- PRE-FLIGHT CHECK 5: Cloud Run secrets (WARNING - non-blocking) --------
Write-Log "Checking Cloud Run secrets (non-blocking)..."
try {
    $gcResult = & gcloud run services describe numista-backend-568985927038 --region=us-central1 --format=json 2>&1
    if ($LASTEXITCODE -eq 0) {
        $gcJson = $gcResult | ConvertFrom-Json
        $envVars = $gcJson.spec.template.spec.containers[0].env | ForEach-Object { $_.name }
        $missing = @('GREYSHEET_API_KEY','GREYSHEET_API_TOKEN') | Where-Object { $_ -notin $envVars }
        if ($missing) {
            Write-Log "WARN [CLOUD_RUN_SECRET_MISSING]: $($missing -join ', ') not found in Cloud Run env."
        } else {
            Write-Log "Cloud Run secrets: present."
        }
    } else {
        Write-Log "WARN [CLOUD_RUN_UNREACHABLE]: gcloud call failed (non-fatal). Check manually if persistent."
    }
} catch {
    Write-Log "WARN [CLOUD_RUN_CHECK_ERROR]: $_ (non-fatal)"
}

# ---- PRE-FLIGHT CHECK 6: Deprecated Gemini model IDs (WARNING - non-blocking) ---
Write-Log "Scanning for deprecated Gemini model IDs (non-blocking)..."
$deprecatedPattern = 'gemini-(1\.5|2\.0|2\.5)'
$searchPaths = @(
    (Join-Path $PROJECT_ROOT "numista_backend"),
    (Join-Path $PROJECT_ROOT "numista_mobile\lib")
)
$deprecatedHits = @()
foreach ($p in $searchPaths) {
    if (Test-Path $p) {
        $hits = Get-ChildItem -Path $p -Recurse -Include "*.py","*.dart" -File -ErrorAction SilentlyContinue |
                Select-String -Pattern $deprecatedPattern -ErrorAction SilentlyContinue
        if ($hits) { $deprecatedHits += $hits }
    }
}
if ($deprecatedHits.Count -gt 0) {
    Write-Log "WARN [DEPRECATED_MODEL_FOUND]: $($deprecatedHits.Count) match(es). Read Gemini Deprecation Schedules before updating."
    $deprecatedHits | ForEach-Object { Write-Log "  $($_.Filename):$($_.LineNumber) $($_.Line.Trim())" }
} else {
    Write-Log "Model ID scan: no deprecated patterns found."
}

# ---- Set environment -------------------------------------------------------
$env:GOOGLE_CLOUD_PROJECT = $qaProject
Write-Log "GOOGLE_CLOUD_PROJECT set to $qaProject"

# ---- Layer result tracking -------------------------------------------------
$suitePass = $true
$l1Status  = "NOT_RUN"
$l2Status  = "NOT_RUN"
$l3Status  = "NOT_RUN"
$l4Status  = "NOT_RUN"

# ---- FLUTTER CHECKS (Layer 0 - skipped if Stack A already ran them) --------
function Run-FlutterChecks {
    if ($SkipFlutterChecks) {
        Write-Log "Flutter checks: SKIPPED (-SkipFlutterChecks set by Stack A)"
        return
    }
    Write-Log "=== Flutter Checks (analyze + test) ==="
    $flutterDir = Join-Path $PROJECT_ROOT "numista_mobile"
    if (-not (Test-Path $flutterDir)) {
        Write-Log "WARN: numista_mobile/ not found. Skipping flutter checks."
        return
    }
    $analyzeOut = & flutter analyze $flutterDir 2>&1
    $analyzeOut | ForEach-Object { Write-Log $_ }
    if ($LASTEXITCODE -ne 0) { $script:suitePass = $false; Write-Log "flutter analyze: FAIL" }
    else { Write-Log "flutter analyze: PASS" }

    $testOut = & flutter test $flutterDir 2>&1
    $testOut | ForEach-Object { Write-Log $_ }
    if ($LASTEXITCODE -ne 0) { $script:suitePass = $false; Write-Log "flutter test: FAIL" }
    else { Write-Log "flutter test: PASS" }
}

# ---- Run layers ------------------------------------------------------------
function Run-Layer1 {
    Write-Log "=== LAYER 1: UX Visual Guard ==="
    $configPath = "$SCRIPT_DIR\playwright.config.js"
    $out = & npx playwright test layer_1_ux_visual/ --config $configPath 2>&1
    $out | ForEach-Object { Write-Log $_ }
    if ($LASTEXITCODE -ne 0) { $script:suitePass = $false; $script:l1Status = "FAIL"; Write-Log "LAYER 1: FAIL" }
    else { $script:l1Status = "PASS"; Write-Log "LAYER 1: PASS" }
}

function Run-Layer2 {
    Write-Log "=== LAYER 2: Functional (CRUD write test suspended) ==="
    $configPath = "$SCRIPT_DIR\playwright.config.js"
    # collection_crud.spec.js is suspended until a QA deployment exists (qa_base_url in SUITE_MANIFEST.json)
    $out = & npx playwright test layer_2_functional/ --config $configPath --ignore-glob "**/collection_crud.spec.js" 2>&1
    $out | ForEach-Object { Write-Log $_ }
    if ($LASTEXITCODE -ne 0) { $script:suitePass = $false; $script:l2Status = "FAIL"; Write-Log "LAYER 2: FAIL" }
    else { $script:l2Status = "PASS"; Write-Log "LAYER 2: PASS (5/6 specs; CRUD write test SUSPENDED)" }
}

function Run-Layer3 {
    Write-Log "=== LAYER 3: Data Audit ==="
    $scripts = @(
        "$SCRIPT_DIR\layer_3_data\api_health_check.py",
        "$SCRIPT_DIR\layer_3_data\account_integrity.py",
        "$SCRIPT_DIR\layer_3_data\coin_data_audit.py"
    )
    $l3All = $true
    foreach ($s in $scripts) {
        $name = Split-Path $s -Leaf
        $scriptArgs = @()
        if ($Verbose) { $scriptArgs = @("--verbose") }
        $out = & python $s @scriptArgs 2>&1
        $out | ForEach-Object { Write-Log $_ }
        if ($LASTEXITCODE -ne 0) { $l3All = $false; $script:suitePass = $false; Write-Log "$name FAIL" }
        else { Write-Log "$name PASS" }
    }
    $script:l3Status = if ($l3All) { "PASS" } else { "FAIL" }
}

function Run-Layer4 {
    Write-Log "=== LAYER 4: Self-Update (feedback mining only) ==="
    $miner = "$SCRIPT_DIR\layer_4_self_update\feedback_miner.py"
    if (Test-Path $miner) {
        $out = & python $miner 2>&1
        $out | ForEach-Object { Write-Log $_ }
        if ($LASTEXITCODE -ne 0) { $script:l4Status = "SKIPPED (non-fatal)"; Write-Log "feedback_miner.py WARN (non-fatal)" }
        else { $script:l4Status = "PASS"; Write-Log "feedback_miner.py PASS" }
    } else {
        $script:l4Status = "NOT_FOUND"
    }
    Write-Log "Note: code_reader.py and test_synthesizer.py run nightly only."
}

# ---- CRUD suspension status ------------------------------------------------
$qaBaseUrl = $manifest.qa_base_url
$crudStatus = if (-not $qaBaseUrl -or $qaBaseUrl -eq '' -or $qaBaseUrl -eq 'REPLACE_WITH_QA_DEPLOYMENT_URL') {
    "SUSPENDED (set qa_base_url in SUITE_MANIFEST.json to activate)"
} else {
    "ACTIVE (qa_base_url: $qaBaseUrl)"
}

# ---- Execute selected layers -----------------------------------------------
switch ($Layer.ToLower()) {
    "1"   { Run-FlutterChecks; Run-Layer1 }
    "2"   { Run-Layer2 }
    "3"   { Run-Layer3 }
    "4"   { Run-Layer4 }
    "all" { Run-FlutterChecks; Run-Layer1; Run-Layer2; Run-Layer3; Run-Layer4 }
    default { Abort "INVALID_LAYER" "Layer must be 1, 2, 3, 4, or all." }
}

# ---- Write SCAN_REPORT.md block --------------------------------------------
function Write-SuiteReport {
    $scanReport = Join-Path $PROJECT_ROOT "SCAN_REPORT.md"
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $isolationLine = if ($manifest.qa_isolation_mode -eq "interim_sealed_account") {
        "Interim sealed account | Expires: $sunsetDate ($daysLeft days remaining)"
    } else {
        "Dedicated QA project: $qaProject"
    }
    $uidStatus = if ($qcUid -and $qcUid -ne 'REPLACE_WITH_QA_USER_UID') { "SET" } else { "! NOT SET" }

    $block = @"

---
## numista_qc Suite (Stack B)
**Run:** $ts

| Layer | Result | Notes |
|-------|--------|-------|
| L1 UX Visual | $l1Status | CONTRAST_SAMPLING_PATH: screenshot |
| L2 Functional (5 specs) | $l2Status | auth, navigation, search, valuation, programs |
| L2 CRUD write test | $crudStatus | collection_crud.spec.js |
| L3 Data Audit | $l3Status | quad title check, estate boundary, API health |
| L4 Self-Update | $l4Status | feedback_miner (today's folder only) |

**Isolation:** $isolationLine | qc_uid: $uidStatus
**Suite result:** $(if ($suitePass) { 'PASS' } else { 'FAIL - see numista_qc/SESSION_LOG.md' })
"@

    Add-Content -Path $scanReport -Value $block -ErrorAction SilentlyContinue
    Write-Log "numista_qc block appended to SCAN_REPORT.md"
}

Write-SuiteReport

# ---- Final result ----------------------------------------------------------
if ($suitePass) {
    Write-Log "SUITE_RESULT: PASS"
} else {
    Write-Log "SUITE_RESULT: FAIL - check SESSION_LOG.md for details"
    exit 1
}


