# ================================================================
# run_tests.ps1 — Numista.AI Automated Test Runner
# Called by Windows Task Scheduler every 2 days at 2:00 AM
# Runs Playwright tests against https://numista.ai
# Generates a markdown morning report in ./reports/
#
# Manual run: cd numista_tests && .\run_tests.ps1
# ================================================================

$TestDir    = Split-Path -Parent $MyInvocation.MyCommand.Definition
$LogFile    = Join-Path $TestDir "reports\runner.log"
$Date       = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Ensure reports dir exists
$null = New-Item -ItemType Directory -Force -Path (Join-Path $TestDir "reports")
$null = New-Item -ItemType Directory -Force -Path (Join-Path $TestDir "screenshots")

function Log($msg) {
  $ts = Get-Date -Format "HH:mm:ss"
  $line = "[$ts] $msg"
  Write-Host $line
  Add-Content -Path $LogFile -Value $line
}

Log "========================================"
Log "Numista.AI Test Run Starting: $Date"
Log "========================================"

# Navigate to test directory
Push-Location $TestDir

# 1. Install/update dependencies
Log "Installing dependencies..."
$npmResult = & npm install 2>&1
if ($LASTEXITCODE -ne 0) {
  Log "ERROR: npm install failed"
  Pop-Location
  exit 1
}
Log "Dependencies ready."

# 2. Install Playwright browsers (chromium only)
Log "Ensuring Playwright browsers are installed..."
& npx playwright install chromium 2>&1 | Out-Null
Log "Browsers ready."

# 3. Clear old screenshots
$screenshotDir = Join-Path $TestDir "screenshots"
Get-ChildItem -Path $screenshotDir -Filter "*.png" | Remove-Item -Force -ErrorAction SilentlyContinue
Log "Old screenshots cleared."

# 4. Run Playwright tests
Log "Running Playwright tests against https://numista.ai ..."
$testOutput = & npx playwright test --reporter=json,list 2>&1
$exitCode = $LASTEXITCODE

# Write raw output to log
Add-Content -Path $LogFile -Value $testOutput

if ($exitCode -eq 0) {
  Log "All tests PASSED."
} else {
  Log "WARNING: Some tests FAILED (exit code $exitCode)."
}

# 5. Generate morning report
Log "Generating morning report..."
$reportOutput = & node generate_report.js 2>&1
Add-Content -Path $LogFile -Value $reportOutput
Log $reportOutput

# 6. Find the report file and print path
$reportDate = Get-Date -Format "yyyy-MM-dd"
$reportFile = Join-Path $TestDir "reports\${reportDate}_morning_report.md"
if (Test-Path $reportFile) {
  Log "Morning report: $reportFile"
} else {
  Log "WARNING: Report file not found at expected path."
}

Pop-Location

Log "Test run complete."
Log "========================================"

# Return exit code so Task Scheduler can track failures
exit $exitCode
