# Numista.AI Agent Builder
# Packages tray_agent.py into NumistaAgent.exe using PyInstaller
# Run: .\build_agent.ps1
# Output: .\dist\NumistaAgent.exe

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host ""
Write-Host "  Numista.AI Agent Builder" -ForegroundColor Cyan
Write-Host "  --------------------------------" -ForegroundColor Cyan
Write-Host ""

# [1/3] Install build dependencies
Write-Host "  [1/3] Installing build dependencies..." -ForegroundColor Yellow
pip install pyinstaller pystray pillow --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] pip install failed." -ForegroundColor Red
    exit 1
}
Write-Host "  OK - Dependencies ready" -ForegroundColor Green

# Clean previous build artifacts
if (Test-Path "$ScriptDir\dist\NumistaAgent.exe") {
    Remove-Item "$ScriptDir\dist\NumistaAgent.exe" -Force
}
if (Test-Path "$ScriptDir\build") {
    Remove-Item "$ScriptDir\build" -Recurse -Force
}

# [2/3] Build
Write-Host "  [2/3] Building NumistaAgent.exe (this takes about 1-2 minutes)..." -ForegroundColor Yellow

$TrayScript = "$ScriptDir\tray_agent.py"
$AddData    = "identify_coin.py;."

$PyInstallerArgs = @(
    "--onefile",
    "--noconsole",
    "--name", "NumistaAgent",
    "--add-data", $AddData,
    "--hidden-import", "pystray._win32",
    "--hidden-import", "PIL._tkinter_finder",
    $TrayScript
)

# Add icon if one exists
if (Test-Path "$ScriptDir\coin.ico") {
    $PyInstallerArgs = @("--icon", "$ScriptDir\coin.ico") + $PyInstallerArgs
}

pyinstaller @PyInstallerArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] PyInstaller build failed. See above for details." -ForegroundColor Red
    exit 1
}

# [3/3] Report
$ExePath = "$ScriptDir\dist\NumistaAgent.exe"
if (Test-Path $ExePath) {
    $SizeMB = [math]::Round((Get-Item $ExePath).Length / 1MB, 1)
    Write-Host ""
    Write-Host "  [3/3] Build complete!" -ForegroundColor Green
    Write-Host "  Output: $ExePath ($SizeMB MB)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Next step: Run install_agent.ps1 to set up auto-start" -ForegroundColor Cyan
} else {
    Write-Host "  [ERROR] Build appeared to succeed but exe not found." -ForegroundColor Red
    exit 1
}
Write-Host ""
