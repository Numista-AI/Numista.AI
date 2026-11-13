# ==============================================================================
#  Numista.AI Agent Builder v2 (Secret-Free Hardened Build — Task 2 ARGON)
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

# ---- [PRE-CHECK] Required source files (NO secrets or static keys bundled) --
Write-Host "  [Pre-check] Verifying required source files..." -ForegroundColor Yellow
$required = @(
    "tray_agent.py",
    "agent_config.py",
    "agent_setup.py",
    "auto_capture.py",
    "identify_coin.py",
    "pcgs_service.py",
    "install_cert.py",
    "coin-schema.json",
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

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "  [ERROR] $($missing.Count) required file(s) missing. Fix before building." -ForegroundColor Red
    exit 1
}
Write-Host "  All required files present." -ForegroundColor Green
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

# ---- [1/2] Build using spec file -------------------------------------------
Write-Host "  [1/2] Building NumistaAgent.exe (takes 1-3 minutes)..." -ForegroundColor Yellow
Write-Host "        Spec: $SpecFile" -ForegroundColor DarkGray
Write-Host ""

Set-Location $ScriptDir
python -m PyInstaller $SpecFile --distpath "$ScriptDir\dist" --workpath "$ScriptDir\build" --noconfirm --clean

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  [ERROR] PyInstaller build failed. See output above." -ForegroundColor Red
    exit 1
}

# ---- [2/2] Post-Build Secret-Free Verification Gate ------------------------
$ExePath = "$ScriptDir\dist\NumistaAgent.exe"
if (-not (Test-Path $ExePath)) {
    Write-Host "  [ERROR] Build appeared to succeed but exe not found at $ExePath" -ForegroundColor Red
    exit 1
}

Write-Host "  [2/2] Running Post-Build Secret-Free Verification Gate..." -ForegroundColor Yellow
python -c "
import pathlib, sys
from PyInstaller.archive.readers import CArchiveReader

exe_path = pathlib.Path(r'$ExePath')
reader = CArchiveReader(str(exe_path))
toc_keys = set(reader.toc.keys())
forbidden_toc = ('.env', 'serviceaccountkey', '.key', '.crt')
bad_toc = [k for k in toc_keys if any(f in k.lower() for f in forbidden_toc)]
if bad_toc:
    exe_path.unlink(missing_ok=True)
    sys.exit(f'FATAL: Forbidden TOC entries found in {exe_path}: {bad_toc}')
raw = exe_path.read_bytes()
for pat in (b'AIzaSy', b'7af45f7e0a341f369ff1a6034175825f8b9e81af', b'f2eb11c27044ca5d178e5e5a31678f037e88940b', b'BEGIN PRIVATE KEY', b'BEGIN RSA PRIVATE KEY'):
    if pat in raw:
        exe_path.unlink(missing_ok=True)
        sys.exit(f'FATAL: Forbidden secret byte pattern found in {exe_path}')
print('  OK - Secret-free TOC & binary scan passed.')
"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Post-build secret verification failed!" -ForegroundColor Red
    exit 1
}

$SizeMB = [math]::Round((Get-Item $ExePath).Length / 1MB, 1)
Write-Host ""
Write-Host "  ================================================" -ForegroundColor Green
Write-Host "    BUILD COMPLETE (SECRET-FREE VERIFIED)!        " -ForegroundColor Green
Write-Host "  ================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Output:  $ExePath" -ForegroundColor White
Write-Host "  Size:    $SizeMB MB" -ForegroundColor White
Write-Host ""
