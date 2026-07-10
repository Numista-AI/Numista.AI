# ============================================================
#  Numista.AI - Brain Control Launcher
#  Starts the Admin Frontend, Backend API, and Brain Watcher
#  Usage: Open PowerShell and run:  .\launch_brain.ps1
# ============================================================

Write-Host "Starting Brain Control Systems..." -ForegroundColor Green

# Window 1: Spin up the backend isolated on Port 8081 for the Admin Tool
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PORT=8081; & 'numista_backend\.venv\Scripts\python.exe' numista_backend\main.py"

# Window 2: Spin up your file watcher / brain watcher
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'numista_backend\.venv\Scripts\python.exe' numista_backend\brain_watcher.py"

# Window 3: Spin up the Next.js Admin Dashboard on Port 3000
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd numista_admin; npm run dev"
