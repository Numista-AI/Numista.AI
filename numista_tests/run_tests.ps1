# ================================================================
# run_tests.ps1 — Numista.AI Multi-Layer Automated Audit & Test Runner
# Called by Windows Task Scheduler daily at 7:00 AM
# Performs:
#   1. Pre-test HTTP cold-start site & API warming
#   2. Python backend Pytest unit suite execution
#   3. Playwright E2E test suite execution against https://numista.ai
#   4. Multi-layer morning report generation & SCAN_REPORT.md auto-sync
#   5. Screenshot & log artifact cleanup (> 14 days)
#
# Manual run: cd numista_tests && .\run_tests.ps1
# ================================================================

$TestDir    = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectDir = Split-Path -Parent $TestDir
$LogFile    = Join-Path $TestDir "reports\runner.log"
$PytestLog  = Join-Path $TestDir "reports\pytest-output.txt"
$Date       = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Ensure directories exist
$null = New-Item -ItemType Directory -Force -Path (Join-Path $TestDir "reports")
$null = New-Item -ItemType Directory -Force -Path (Join-Path $TestDir "screenshots")

function Log($msg) {
  $ts = Get-Date -Format "HH:mm:ss"
  $line = "[$ts] $msg"
  Write-Host $line
  Add-Content -Path $LogFile -Value $line -ErrorAction SilentlyContinue
}

Log "========================================"
Log "Numista.AI Multi-Layer Audit Starting: $Date"
Log "========================================"

Push-Location $TestDir

# 0. Pre-test Cold-Start Site Warming & Overnight Master Suite
Log "Warming up site & backend endpoints (cold-start mitigation)..."
try {
  $null = Invoke-WebRequest -Uri "https://numista.ai" -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue
  $null = Invoke-WebRequest -Uri "https://numista-backend-568985927038.us-central1.run.app/api/greysheet/config" -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue
  Log "Site warm-up complete."
} catch {
  Log "Site warm-up completed with fallback."
}

Log "Executing Master Overnight Domain Completeness Engine (run_overnight_tests.py)..."
$pythonExe = Join-Path $ProjectDir "numista_backend\.venv\Scripts\python.exe"
$overnightScript = Join-Path $ProjectDir "run_overnight_tests.py"
if (Test-Path $pythonExe) {
  $overnightOutput = & $pythonExe $overnightScript 2>&1
  Add-Content -Path $LogFile -Value $overnightOutput
  Log "Master Overnight Engine completed."
} else {
  Log "WARNING: Python venv executable not found at $pythonExe"
}

# 1. Install/update npm dependencies
Log "Installing dependencies..."
$npmResult = & npm install 2>&1
if ($LASTEXITCODE -ne 0) {
  Log "ERROR: npm install failed"
  Pop-Location
  exit 1
}
Log "Dependencies ready."

# 2. Ensure Playwright chromium browser is installed
Log "Ensuring Playwright browsers are installed..."
& npx playwright install chromium 2>&1 | Out-Null
Log "Browsers ready."

# 3. Clean up old screenshots (> 14 days old)
$screenshotDir = Join-Path $TestDir "screenshots"
Get-ChildItem -Path $screenshotDir -Filter "*.png" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-14) } | Remove-Item -Force -ErrorAction SilentlyContinue
Log "Screenshots storage verified & cleaned."

# 4. Run Backend Pytest Unit Suite
Log "Running Python backend Pytest unit suite..."
$pytestExe = Join-Path $ProjectDir "numista_backend\.venv\Scripts\pytest.exe"
$pytestExit = 0
if (Test-Path $pytestExe) {
  Push-Location (Join-Path $ProjectDir "numista_backend")
  $pytestOutput = & $pytestExe "tests" --capture=no 2>&1
  $pytestExit = $LASTEXITCODE
  Pop-Location
  Set-Content -Path $PytestLog -Value $pytestOutput
  if ($pytestExit -eq 0) {
    Log "Backend Pytest unit suite PASSED."
  } else {
    Log "WARNING: Pytest unit suite reported failures."
  }
} else {
  Log "WARNING: Backend venv pytest executable not found at $pytestExe"
}

# 5. Run Playwright E2E UI Tests (hard 40-minute timeout so report always runs)
Log "Running Playwright E2E tests against https://numista.ai (40-min hard timeout)..."
$playwrightLog = Join-Path $TestDir "reports\playwright-run.log"

# Use cmd.exe so npx resolves correctly regardless of whether it is a .ps1 or .cmd wrapper.
# The job prints the exit code as the last line so we can extract it reliably.
$playwrightJob = Start-Job -ScriptBlock {
  param($dir)
  Set-Location $dir
  $out = & cmd.exe /c "npx playwright test" 2>&1
  $ec  = $LASTEXITCODE
  $out
  "##EXITCODE=$ec##"
} -ArgumentList $TestDir

$jobDone = Wait-Job -Job $playwrightJob -Timeout 2400   # 2400 sec = 40 min
if ($null -eq $jobDone) {
  Log "WARNING: Playwright E2E timed out after 40 minutes -- killing and continuing to report."
  Stop-Job  -Job $playwrightJob
  Remove-Job -Job $playwrightJob -Force
  $exitCode = 124
} else {
  $rawOutput = Receive-Job -Job $playwrightJob
  Remove-Job -Job $playwrightJob -Force

  # Extract exit code embedded as last line "##EXITCODE=N##"
  $ecLine = ($rawOutput | Select-String "##EXITCODE=(\d+)##" | Select-Object -Last 1)
  if ($ecLine) {
    $exitCode = [int]$ecLine.Matches[0].Groups[1].Value
    $testOutput = ($rawOutput | Where-Object { $_ -notmatch "##EXITCODE=" }) -join "`n"
  } else {
    $exitCode = 0
    $testOutput = $rawOutput -join "`n"
  }
  Add-Content -Path $LogFile    -Value $testOutput
  Add-Content -Path $playwrightLog -Value $testOutput
}

if ($exitCode -eq 0) {
  Log "Playwright E2E suite PASSED."
} elseif ($exitCode -eq 124) {
  Log "WARNING: Playwright E2E suite TIMED OUT after 40 minutes."
} else {
  Log "WARNING: Playwright E2E suite reported failures (exit code $exitCode)."
}

# Stack B — numista_qc suite (runs after Stack A; -SkipFlutterChecks avoids double flutter run)
Log "=== numista_qc Suite (Stack B) starting ==="
$qcScript = Join-Path $ProjectDir "numista_qc\run_qc.ps1"
if (Test-Path $qcScript) {
    & $qcScript -Layer all -SkipFlutterChecks
    if ($LASTEXITCODE -ne 0) {
        Log "WARNING: numista_qc suite reported failures. See numista_qc\SESSION_LOG.md."
    } else {
        Log "numista_qc suite: PASS"
    }
} else {
    Log "WARNING: numista_qc\run_qc.ps1 not found — Stack B skipped."
}
Log "=== numista_qc Suite (Stack B) complete ==="

# 6. Generate 360-Degree Morning Report & Auto-Sync SCAN_REPORT.md (always runs)
Log "Generating 360-degree morning report..."
$reportOutput = & node generate_report.js 2>&1
Add-Content -Path $LogFile -Value $reportOutput
Log $reportOutput

# 7. Non-blocking alert logging if failures occur
if ($exitCode -ne 0 -or $pytestExit -ne 0) {
  Log "ALERT: Failures detected in automated audit! Check reports folder."
}

# 8. Artifact Cleanup (old logs older than 30 days)
Get-ChildItem -Path (Join-Path $TestDir "reports") -Filter "*.log" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force -ErrorAction SilentlyContinue

Pop-Location
Log "Multi-layer audit run complete."
Log "========================================"

exit $exitCode
