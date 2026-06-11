# ============================================================
#  Numista.AI - Dev Launcher
#  Starts the hardware server + Flutter WEB server together.
#  Usage: Open PowerShell and run:  .\launch_numista.ps1
#
#  Once running:
#    App      -> http://localhost:8080
#    Hardware -> http://localhost:5000
# ============================================================

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$MobileDir   = Join-Path $ProjectRoot "numista_mobile"

Write-Host ""
Write-Host "  Numista.AI Dev Launcher" -ForegroundColor Cyan
Write-Host "  =====================================" -ForegroundColor Cyan
Write-Host ""

# ── PRE-LAUNCH CLEANUP ─────────────────────────────────────────────────────────
Write-Host "  [0/2] Cleaning up stale processes and locked build cache..." -ForegroundColor Yellow

# Kill any lingering Dart / Flutter processes that lock build\flutter_assets
Get-Process -Name "dart","flutter" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 800

# ⚠️  Only wipe the WINDOWS native build artifacts that cause file locks.
#    build\web is intentionally EXCLUDED so the production web build is preserved.
#    Deleting build\web here would break https://numista.ai after every dev session!
$pathsToClean = @(
    (Join-Path $MobileDir "build\windows"),
    (Join-Path $MobileDir "build\native_assets"),
    (Join-Path $MobileDir "build\native_hooks"),
    (Join-Path $MobileDir ".dart_tool"),
    (Join-Path $MobileDir "windows\flutter\ephemeral")
)
foreach ($p in $pathsToClean) {
    if (Test-Path $p) {
        Remove-Item -Path $p -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "    Removed: $p" -ForegroundColor DarkGray
    }
}

# Run pub get (NOT flutter clean — that would delete build\web)
Push-Location $MobileDir
    & flutter pub get | Out-Null
Pop-Location

# Remind user if no web build exists yet
$webBuildExists = Test-Path (Join-Path $MobileDir "build\web\index.html")
if (-not $webBuildExists) {
    Write-Host ""
    Write-Host "  ⚠️  No production build found." -ForegroundColor Yellow
    Write-Host "     Run this before deploying to numista.ai:" -ForegroundColor Yellow
    Write-Host "       flutter build web --release --base-href \"/\"" -ForegroundColor Cyan
    Write-Host "       firebase deploy --only hosting" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "  ✅ Web build present (build\web) — ready to deploy." -ForegroundColor Green
}

Write-Host "  Pre-launch cleanup complete." -ForegroundColor Green
Write-Host ""

# ── DEPENDENCY CHECKS ──────────────────────────────────────────────────────────
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "  [ERROR] Python not found. Please install Python 3." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
    Write-Host "  [ERROR] Flutter not found in PATH." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# ── START HARDWARE SERVER ──────────────────────────────────────────────────────
Write-Host "  [1/2] Starting Hardware Server (microscope)..." -ForegroundColor Yellow
$HardwareDir = Join-Path $ProjectRoot "numista_hardware"
$VenvPython  = Join-Path $ProjectRoot "numista_backend\.venv\Scripts\python.exe"

$hwCmd = "cd '$HardwareDir'; & '$VenvPython' auto_capture.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $hwCmd -WindowStyle Normal

Write-Host "  Waiting 3 seconds for hardware server to start..." -ForegroundColor DarkGray
Start-Sleep -Seconds 3

# ── START FLUTTER (Chrome device) ─────────────────────────────────────────────
Write-Host "  [2/2] Starting Flutter (Chrome)..." -ForegroundColor Yellow
Write-Host "  Chrome will open automatically in ~30 seconds." -ForegroundColor DarkGray

$flutterCmd = "cd '$MobileDir'; flutter run -d chrome --web-port 8080"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $flutterCmd -WindowStyle Normal

Write-Host ""
Write-Host "  Both processes launched!" -ForegroundColor Green
Write-Host ""
Write-Host "  Hardware Server -> http://localhost:5000" -ForegroundColor Gray
Write-Host "  Flutter App     -> Chrome opens automatically" -ForegroundColor Gray
Write-Host ""
Write-Host "  Wait about 30 seconds for Chrome to open with the app." -ForegroundColor DarkGray
Write-Host "  Hot reload: press 'r' in the Flutter PowerShell window." -ForegroundColor DarkGray
Write-Host "  The microscope only works while the Hardware Server window is open." -ForegroundColor DarkGray
Write-Host ""
Read-Host "  Press Enter to close this window (the app keeps running)"
