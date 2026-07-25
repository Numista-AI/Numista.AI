# ================================================================
# setup_scheduler.ps1
# Registers a Windows Task Scheduler job to run Numista.AI tests
# daily at 7:00 AM automatically.
# ================================================================

$TaskName   = "NumistaAI-AutoTests"
$TestDir    = "c:\Users\ericd\Documents\MyVertexProject\numista_tests"
$ScriptPath = Join-Path $TestDir "run_tests.ps1"

Write-Host ""
Write-Host "  Numista.AI - Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "  ===================================" -ForegroundColor Cyan
Write-Host ""

# Remove existing task if present
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
  Write-Host "  Removed existing task: $TaskName" -ForegroundColor Yellow
}

# Define action, trigger, settings, principal
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$ScriptPath`"" -WorkingDirectory $TestDir
$startTime = (Get-Date -Hour 7 -Minute 0 -Second 0)
if ($startTime -lt (Get-Date)) {
    $startTime = $startTime.AddDays(1)
}
$trigger = New-ScheduledTaskTrigger -Daily -DaysInterval 1 -At $startTime
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew -WakeToRun
$principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Automated Playwright tests for https://numista.ai - runs daily at 7 AM" -Force | Out-Null

# Disable WakeToRun on NumistaAI_DailyBackup (runs at 7 PM) to keep display off during overnight hours
$backupTask = Get-ScheduledTask -TaskName "NumistaAI_DailyBackup" -ErrorAction SilentlyContinue
if ($backupTask) {
  $backupTask.Settings.WakeToRun = $false
  Set-ScheduledTask -InputObject $backupTask -ErrorAction SilentlyContinue | Out-Null
  Write-Host "  Updated NumistaAI_DailyBackup: WakeToRun set to False" -ForegroundColor Green
}

Write-Host "  Task registered successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "  Task Name   : $TaskName" -ForegroundColor White
Write-Host "  Schedule    : Daily at 7:00 AM" -ForegroundColor White
$firstRunStr = $startTime.ToString('yyyy-MM-dd HH:mm')
Write-Host "  First Run   : $firstRunStr" -ForegroundColor White
Write-Host "  Script      : $ScriptPath" -ForegroundColor White
Write-Host "  Reports     : $TestDir\reports\" -ForegroundColor White
Write-Host ""
