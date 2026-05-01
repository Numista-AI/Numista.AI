# ============================================================
#  Numista.AI Agent Installer
#  Adds NumistaAgent.exe to Windows Startup so it runs on every login.
#  Run ONCE after building: .\install_agent.ps1
# ============================================================

$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ExePath    = "$ScriptDir\dist\NumistaAgent.exe"
$StartupDir = [Environment]::GetFolderPath('Startup')
$StartupExe = "$StartupDir\NumistaAgent.exe"

Write-Host ""
Write-Host "  Numista.AI Agent Installer" -ForegroundColor Cyan
Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# ─── Check exe exists ─────────────────────────────────────────
if (-not (Test-Path $ExePath)) {
    Write-Host "  [ERROR] NumistaAgent.exe not found at:" -ForegroundColor Red
    Write-Host "  $ExePath" -ForegroundColor Red
    Write-Host "  Run build_agent.ps1 first." -ForegroundColor Yellow
    exit 1
}

# ─── Copy to Startup folder ───────────────────────────────────
Write-Host "  Installing to Windows Startup..." -ForegroundColor Yellow
Copy-Item $ExePath $StartupExe -Force
Write-Host "  ✓ Copied to: $StartupExe" -ForegroundColor Green

# ─── Start it now (so user doesn't need to reboot) ───────────
Write-Host "  Starting agent now..." -ForegroundColor Yellow
Start-Process $StartupExe

Write-Host ""
Write-Host "  ✓ Numista.AI Hardware Agent installed!" -ForegroundColor Green
Write-Host ""
Write-Host "  The agent will now:" -ForegroundColor Gray
Write-Host "    • Start automatically every time Windows starts" -ForegroundColor Gray
Write-Host "    • Appear as a coin icon in your system tray" -ForegroundColor Gray
Write-Host "    • Listen for scan commands from numista.ai" -ForegroundColor Gray
Write-Host ""
Write-Host "  To uninstall: delete $StartupExe" -ForegroundColor DarkGray
Write-Host ""
