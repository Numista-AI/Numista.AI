# Numista.AI -- Windows Task Scheduler Script for Daily Noon EST Beta Audit
# Schedules Windows to run the last 2 days beta feedback audit daily at 12:00 PM EST.

$TaskName = "Numista_Daily_Beta_Feedback_Audit"
$ScriptPath = "C:\Users\ericd\Documents\MyVertexProject\numista_qa_runner\run_daily_beta_audit.py"
$PythonExe = "python.exe"

$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "$ScriptPath --days 2" -WorkingDirectory "C:\Users\ericd\Documents\MyVertexProject"
$Trigger = New-ScheduledTaskTrigger -Daily -At "12:00PM"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Daily Noon EST automated beta test audit for the last 2 days feedback." -Force

Write-Host "✅ Successfully registered Windows Scheduled Task: $TaskName to run daily at 12:00 PM EST (testing last 2 days)."
