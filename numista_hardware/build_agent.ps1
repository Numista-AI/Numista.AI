# ==============================================================================
#  Numista.AI Agent Builder v2
#  Packages tray_agent.py into NumistaAgent.exe using PyInstaller
#
#  Usage:  .\build_agent.ps1
#  Output: .\dist\NumistaAgent.exe
# ==============================================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SpecFile  = "$ScriptDir\NumistaAgent.spec"

Write-Host ""
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host "    Numista.AI Desktop Agent Builder v2           " -ForegroundColor Cyan
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host ""

# ---- [PRE-CHECK] Required source files -------------------------------------
Write-Host "  [Pre-check] Verifying required source files..." -ForegroundColor Yellow
$required = @(
    "tray_agent.py",
    "agent_config.py",
    "agent_setup.py",
    "auto_capture.py",
    "identify_coin.py",
    "pcgs_service.py",
    "coin-schema.json",
    "localhost.crt",
    "localhost.key",
    ".env",
    "NumistaAgent.spec"
)

$missing = @()
foreach ($f in $required) {
    if (-not (Test-Path "$ScriptDir\$f")) {
        $missing += $f
        Write-Host "    MISSING: $f" -ForegroundColor Red
    } else {
        Write-Host "    OK: $f" -ForegroundColor DarkGreen
    }
}

$saKey = "$ScriptDir\..\numista_backend\serviceAccountKey.json.json"
if (Test-Path $saKey) {
    Write-Host "    OK: serviceAccountKey.json.json" -ForegroundColor DarkGreen
} else {
    Write-Host "    WARNING: serviceAccountKey.json.json not found (ADC fallback)" -ForegroundColor DarkYellow
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "  [ERROR] $($missing.Count) required file(s) missing. Fix before building." -ForegroundColor Red
    exit 1
}
Write-Host "  All required files present." -ForegroundColor Green
Write-Host ""

# ---- [1/3] Install build dependencies --------------------------------------
Write-Host "  [1/3] Installing build dependencies..." -ForegroundColor Yellow
pip install pyinstaller pystray pillow --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] pip install failed." -ForegroundColor Red
    exit 1
}
Write-Host "  OK - Build dependencies ready" -ForegroundColor Green
Write-Host ""

# Clean previous build artefacts
if (Test-Path "$ScriptDir\dist\NumistaAgent.exe") {
    Remove-Item "$ScriptDir\dist\NumistaAgent.exe" -Force
    Write-Host "  Cleaned old NumistaAgent.exe" -ForegroundColor DarkGray
}
if (Test-Path "$ScriptDir\build") {
    Remove-Item "$ScriptDir\build" -Recurse -Force
    Write-Host "  Cleaned build/ directory" -ForegroundColor DarkGray
}
Write-Host ""

# ---- [2/3] Build using spec file -------------------------------------------
Write-Host "  [2/3] Building NumistaAgent.exe (takes 2-4 minutes)..." -ForegroundColor Yellow
Write-Host "        Spec: $SpecFile" -ForegroundColor DarkGray
Write-Host ""

Set-Location $ScriptDir
python -m PyInstaller $SpecFile --distpath "$ScriptDir\dist" --workpath "$ScriptDir\build" --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  [ERROR] PyInstaller build failed. See output above." -ForegroundColor Red
    exit 1
}

# ---- [3/3] Report ----------------------------------------------------------
$ExePath = "$ScriptDir\dist\NumistaAgent.exe"
if (Test-Path $ExePath) {
    $SizeMB = [math]::Round((Get-Item $ExePath).Length / 1MB, 1)
    Write-Host ""
    Write-Host "  ================================================" -ForegroundColor Green
    Write-Host "    BUILD COMPLETE!" -ForegroundColor Green
    Write-Host "  ================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Output:  $ExePath" -ForegroundColor White
    Write-Host "  Size:    $SizeMB MB" -ForegroundColor White
    Write-Host ""
    Write-Host "  Next steps:" -ForegroundColor Cyan
    Write-Host "    1. Test:    .\dist\NumistaAgent.exe" -ForegroundColor Cyan
    Write-Host "    2. Install: .\install_agent.ps1" -ForegroundColor Cyan
    Write-Host "    3. Package: makensis NumistaAgentSetup.nsi" -ForegroundColor Cyan
} else {
    Write-Host "  [ERROR] Build appeared to succeed but exe not found." -ForegroundColor Red
    Write-Host "  Expected: $ExePath" -ForegroundColor Red
    exit 1
}
Write-Host ""
