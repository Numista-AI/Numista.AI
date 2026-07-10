# ============================================================
#  Numista.AI - Brain Control Teardown
#  Safely stops the Next.js frontend, Python backend, and watcher
# ============================================================

Write-Host "Shutting down Brain Control processes..." -ForegroundColor Yellow

# Function to safely kill a process by its active port
function Kill-ProcessByPort($port) {
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($conn) {
        $pidToKill = $conn.OwningProcess
        Write-Host "Killing process $pidToKill on port $port..."
        Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "Nothing running on port $port." -ForegroundColor DarkGray
    }
}

# 1. Kill the Admin Dashboard Backend API (Port 8081)
Kill-ProcessByPort 8081

# 2. Kill the Admin Dashboard Frontend (Port 3000)
Kill-ProcessByPort 3000

# 3. Kill the Brain Watcher (Search by script name)
$watcher = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "brain_watcher.py" }
if ($watcher) {
    Write-Host "Killing Brain Watcher (PID: $($watcher.ProcessId))..."
    Stop-Process -Id $watcher.ProcessId -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "No Brain Watcher process found." -ForegroundColor DarkGray
}

Write-Host "Brain Control shutdown complete!" -ForegroundColor Green
