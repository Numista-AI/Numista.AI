#!/usr/bin/env pwsh
# deploy_to_main.ps1
# Safe deploy helper: creates PR, waits for CI to pass, then merges.
# Usage: .\deploy_to_main.ps1 -Title "feat: ..." -Body "## Changes..."

param(
  [Parameter(Mandatory)][string]$Title,
  [Parameter(Mandatory)][string]$Body
)

$env:PATH = $env:PATH + ";C:\Program Files\GitHub CLI"

# ── Step 1: Create PR ─────────────────────────────────────────────────────────
Write-Host "Creating PR: $Title" -ForegroundColor Cyan
$prNumber = gh api repos/Numista-AI/Numista.AI/pulls --method POST `
  --field title="$Title" `
  --field head="dev" `
  --field base="main" `
  --field body="$Body" `
  --jq '.number'

if (-not $prNumber) { Write-Error "Failed to create PR"; exit 1 }
Write-Host "PR #$prNumber created. Waiting for CI..." -ForegroundColor Yellow

# ── Step 2: Poll for CI completion (max 10 minutes) ──────────────────────────
$deadline = (Get-Date).AddMinutes(10)
$passed   = $false

while ((Get-Date) -lt $deadline) {
  Start-Sleep -Seconds 30

  $checks = gh api repos/Numista-AI/Numista.AI/commits/$(
    gh api repos/Numista-AI/Numista.AI/pulls/$prNumber --jq '.head.sha'
  )/check-runs --jq '.check_runs[] | {name:.name, status:.status, conclusion:.conclusion}' 2>&1

  $flutterOk = $checks | Select-String "Flutter Web Build" | Select-String '"conclusion":"success"'
  $pythonOk  = $checks | Select-String "Python Lint"        | Select-String '"conclusion":"success"'
  $anyFail   = $checks | Select-String '"conclusion":"failure"'

  if ($anyFail) {
    Write-Host "CI FAILED on PR #$prNumber:" -ForegroundColor Red
    $anyFail | ForEach-Object { Write-Host "  $_" }
    Write-Host "Closing PR without merging." -ForegroundColor Red
    gh api repos/Numista-AI/Numista.AI/pulls/$prNumber --method PATCH --field state=closed | Out-Null
    exit 1
  }

  if ($flutterOk -and $pythonOk) {
    Write-Host "CI passed!" -ForegroundColor Green
    $passed = $true
    break
  }

  Write-Host "  Still running... ($('{0:mm\:ss}' -f ((Get-Date) - ($deadline.AddMinutes(-10)))))" -ForegroundColor DarkGray
}

if (-not $passed) {
  Write-Error "Timed out waiting for CI on PR #$prNumber. Not merging."
  exit 1
}

# ── Step 3: Merge ─────────────────────────────────────────────────────────────
Write-Host "Merging PR #$prNumber to main..." -ForegroundColor Cyan
$result = gh api repos/Numista-AI/Numista.AI/pulls/$prNumber/merge `
  --method PUT `
  --field merge_method=merge `
  --field commit_title="$Title" 2>&1

if ($result -match '"merged":true') {
  Write-Host "PR #$prNumber merged successfully!" -ForegroundColor Green
} else {
  Write-Error "Merge failed: $result"
  exit 1
}
