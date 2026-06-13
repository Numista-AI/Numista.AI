# ================================================================
# setup_scheduler.ps1
# Registers a Windows Task Scheduler job to run Numista.AI tests
# every 2 days at 2:00 AM automatically.
#
# Run ONCE to install:  .\setup_scheduler.ps1
# To remove the task:   Unregister-ScheduledTask -TaskName "NumistaAI-Tests" -Confirm:$false
# ================================================================

$TaskName   = "NumistaAI-AutoTests"
$TestDir    = "c:\Users\ericd\Documents\MyVertexProject\numista_tests"
$ScriptPath = Join-Path $TestDir "run_tests.ps1"

Write-Host ""
Write-Host "  Numista.AI — Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "  ===================================" -ForegroundColor Cyan
Write-Host ""

# Remove existing task if present
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
  Write-Host "  Removed existing task: $TaskName" -ForegroundColor Yellow
}

# Define the action: run PowerShell with the test script
$action = New-ScheduledTaskAction `
  -Execute "powershell.exe" `
  -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$ScriptPath`"" `
  -WorkingDirectory $TestDir

# Trigger: every 2 days at 2:00 AM, starting tonight
$startTime = (Get-Date -Hour 2 -Minute 0 -Second 0).AddDays(1)
$trigger = New-ScheduledTaskTrigger `
  -Daily `
  -DaysInterval 2 `
  -At $startTime

# Settings: run even on battery, do not stop if computer becomes idle
$settings = New-ScheduledTaskSettingsSet `
  -StartWhenAvailable `
  -RunOnlyIfNetworkAvailable `
  -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
  -MultipleInstances IgnoreNew

# Principal: run as current user
$principal = New-ScheduledTaskPrincipal `
  -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
  -LogonType Interactive `
  -RunLevel Limited

# Register the task
try {
  Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Automated Playwright tests for https://numista.ai — runs every 2 days at 2 AM" `
    -Force | Out-Null

  Write-Host "  Task registered successfully!" -ForegroundColor Green
  Write-Host ""
  Write-Host "  Task Name   : $TaskName" -ForegroundColor White
  Write-Host "  Schedule    : Every 2 days at 2:00 AM" -ForegroundColor White
  Write-Host "  First Run   : $($startTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor White
  Write-Host "  Script      : $ScriptPath" -ForegroundColor White
  Write-Host "  Reports     : $TestDir\reports\" -ForegroundColor White
  Write-Host ""
  Write-Host "  To view in Task Scheduler: taskschd.msc" -ForegroundColor DarkGray
  Write-Host "  To run now manually:       Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor DarkGray
  Write-Host "  To remove:                 Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor DarkGray
  Write-Host ""
} catch {
  Write-Host "  ERROR registering task: $_" -ForegroundColor Red
  Write-Host "  Try running this script as Administrator." -ForegroundColor Yellow
  exit 1
}
