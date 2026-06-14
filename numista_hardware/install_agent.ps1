# ==============================================================================
#  Numista.AI Agent Installer v2
#  1. Trusts localhost.crt in Windows Root CA store (certutil)
#  2. Copies NumistaAgent.exe to %LOCALAPPDATA%\NumistaAI\
#  3. Sets HKCU registry autostart key
#  4. Launches the agent now
#
#  Run: .\install_agent.ps1
# ==============================================================================

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ExeSrc      = "$ScriptDir\dist\NumistaAgent.exe"
$CertSrc     = "$ScriptDir\localhost.crt"
$InstallDir  = "$env:LOCALAPPDATA\NumistaAI"
$ExeDest     = "$InstallDir\NumistaAgent.exe"
$RegPath     = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$RegName     = "NumistaAgent"

Write-Host ""
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host "    Numista.AI Desktop Agent Installer           " -ForegroundColor Cyan
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host ""

# Check exe exists
if (-not (Test-Path $ExeSrc)) {
    Write-Host "  [ERROR] NumistaAgent.exe not found at:" -ForegroundColor Red
    Write-Host "  $ExeSrc" -ForegroundColor Red
    Write-Host "  Run .\build_agent.ps1 first." -ForegroundColor Yellow
    exit 1
}

# Check cert exists
if (-not (Test-Path $CertSrc)) {
    Write-Host "  [ERROR] localhost.crt not found at:" -ForegroundColor Red
    Write-Host "  $CertSrc" -ForegroundColor Red
    Write-Host "  Run: python gen_cert.py" -ForegroundColor Yellow
    exit 1
}

# ---- [1/4] Trust the SSL certificate ----------------------------------------
Write-Host "  [1/4] Trusting localhost.crt in Windows Root CA store..." -ForegroundColor Yellow
certutil -user -addstore Root "$CertSrc" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK - Certificate trusted (CurrentUser store)" -ForegroundColor Green
} else {
    Write-Host "  Retrying with LocalMachine store..." -ForegroundColor DarkYellow
    certutil -addstore Root "$CertSrc" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK - Certificate trusted (LocalMachine store)" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: certutil failed. Chrome may show SSL warnings." -ForegroundColor DarkYellow
        Write-Host "  Workaround: enable chrome://flags/#allow-insecure-localhost" -ForegroundColor DarkGray
    }
}
Write-Host ""

# ---- [2/4] Install to %LOCALAPPDATA%\NumistaAI\ ------------------------------
Write-Host "  [2/4] Installing to $InstallDir ..." -ForegroundColor Yellow
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
Copy-Item $ExeSrc $ExeDest -Force
Write-Host "  OK - Copied NumistaAgent.exe to $ExeDest" -ForegroundColor Green
Write-Host ""

# ---- [3/4] Set registry autostart key ----------------------------------------
Write-Host "  [3/4] Setting Windows autostart registry key..." -ForegroundColor Yellow
Set-ItemProperty -Path $RegPath -Name $RegName -Value "`"$ExeDest`"" -Type String
$regVal = Get-ItemProperty -Path $RegPath -Name $RegName -ErrorAction SilentlyContinue
if ($regVal) {
    Write-Host "  OK - Registry key: HKCU\...\Run\$RegName" -ForegroundColor Green
    Write-Host "       -> $ExeDest" -ForegroundColor DarkGray
} else {
    Write-Host "  WARNING: Could not verify registry key." -ForegroundColor DarkYellow
}
Write-Host ""

# ---- [4/4] Launch agent now --------------------------------------------------
Write-Host "  [4/4] Starting Numista.AI Desktop Agent..." -ForegroundColor Yellow

$existing = Get-Process -Name "NumistaAgent" -ErrorAction SilentlyContinue
if ($existing) {
    $existing | Stop-Process -Force
    Start-Sleep -Milliseconds 1000
    Write-Host "  (Stopped previous instance)" -ForegroundColor DarkGray
}

Start-Process $ExeDest
Write-Host "  OK - Agent started. Look for the gold coin icon in your system tray!" -ForegroundColor Green
Write-Host ""

# ---- Summary -----------------------------------------------------------------
Write-Host "  ================================================" -ForegroundColor Green
Write-Host "    Installation Complete!                       " -ForegroundColor Green
Write-Host "  ================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  The agent will now:" -ForegroundColor White
Write-Host "    - Start automatically every time Windows starts" -ForegroundColor White
Write-Host "    - Appear as a gold coin icon in your system tray" -ForegroundColor White
Write-Host "    - Serve HTTPS on localhost:5000 (trusted by Chrome)" -ForegroundColor White
Write-Host "    - Listen for scan commands from numista.ai" -ForegroundColor White
Write-Host ""
Write-Host "  Open numista.ai -> Microscope Scanner -> should show Online" -ForegroundColor Cyan
Write-Host ""
Write-Host "  To uninstall:" -ForegroundColor DarkGray
Write-Host "    Remove-Item '$ExeDest'" -ForegroundColor DarkGray
Write-Host "    Remove-ItemProperty -Path '$RegPath' -Name '$RegName'" -ForegroundColor DarkGray
Write-Host "    certutil -user -delstore Root localhost" -ForegroundColor DarkGray
Write-Host ""
