# ============================================================
#  Numista.AI - Brain Control Launcher
#  Starts the Admin Frontend, Backend API, and Brain Watcher
#  Usage: Open PowerShell and run:  .\launch_brain.ps1
# ============================================================

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BackendDir  = Join-Path $ProjectRoot "numista_backend"
$AdminDir    = Join-Path $ProjectRoot "numista_admin"
$VenvPython  = Join-Path $BackendDir ".venv\Scripts\python.exe"

Write-Host "Starting Brain Control Systems..." -ForegroundColor Green

# Window 1: Spin up the backend isolated on Port 8081 for the Admin Tool
$backendCmd = "`$env:PORT=8081; cd '$BackendDir'; & '$VenvPython' main.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# Window 2: Spin up your file watcher / brain watcher
$watcherCmd = "cd '$BackendDir'; & '$VenvPython' brain_watcher.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $watcherCmd

# Window 3: Spin up the Next.js Admin Dashboard on Port 3000
$adminCmd = "cd '$AdminDir'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $adminCmd
