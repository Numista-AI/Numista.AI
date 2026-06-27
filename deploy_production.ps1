# ============================================================
#  Numista.AI — Emergency Manual Deploy Script
#
#  !! PRIMARY DEPLOYMENT METHOD: Push code to the `main` branch.
#  !! GitHub Actions (.github/workflows/deploy-production.yml)
#  !! will automatically build and deploy both the Flutter frontend
#  !! and the Python backend to Cloud Run.
#
#  USE THIS SCRIPT ONLY AS AN EMERGENCY FALLBACK when the
#  GitHub Actions pipeline is unavailable or broken.
#
#  Usage:  .\deploy_production.ps1
#
#  What it does:
#    1. Removes the dev service-worker kill-switch from index.html
#    2. Builds Flutter for web (release mode) from numista_mobile/
#    3. Deploys frontend to Firebase Hosting
#    4. Restores the dev service-worker kill-switch
#    5. Verifies the live site is reachable
#
#  NOTE: This script covers the FRONTEND only.
#  For an emergency BACKEND deploy, see the block at the bottom.
# ============================================================

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$MobileDir   = Join-Path $ProjectRoot "numista_mobile"
$IndexFile   = Join-Path $MobileDir "web\index.html"
$BackupFile  = Join-Path $MobileDir "web\index.html.bak"

Write-Host ""
Write-Host "  Numista.AI - Production Deploy" -ForegroundColor Magenta
Write-Host "  ================================" -ForegroundColor Magenta
Write-Host ""

# ── SAFETY CHECK ──────────────────────────────────────────────────────────────
if (-not (Test-Path $IndexFile)) {
    Write-Host "  [ERROR] index.html not found at: $IndexFile" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
    Write-Host "  [ERROR] Flutter not found in PATH." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command firebase -ErrorAction SilentlyContinue)) {
    Write-Host "  [ERROR] Firebase CLI not found. Install with: npm install -g firebase-tools" -ForegroundColor Red
    exit 1
}

# ── STEP 1: Back up index.html and strip the dev service-worker kill-switch ───
Write-Host "  [1/5] Removing dev service-worker kill-switch from index.html..." -ForegroundColor Yellow

Copy-Item $IndexFile $BackupFile -Force

$content = Get-Content $IndexFile -Raw

# Strip the dev-only block (between the STOP banner comment and closing </script>)
$devBlockPattern = '(?s)<!--\s*[╔].*?STOP.*?-->\s*<script>.*?navigator\.serviceWorker.*?</script>'
$stripped = $content -replace $devBlockPattern, ''

if ($stripped -eq $content) {
    Write-Host "  Info: No dev block found in index.html (may already be stripped)." -ForegroundColor DarkGray
    Write-Host "        Proceeding with build anyway..." -ForegroundColor DarkGray
} else {
    Set-Content $IndexFile $stripped -NoNewline
    Write-Host "  Dev block removed." -ForegroundColor Green
}

# ── STEP 2: Flutter build ──────────────────────────────────────────────────────
Write-Host ""
Write-Host "  [2/5] Running flutter build web --release..." -ForegroundColor Yellow
Write-Host "        (This takes 2-4 minutes)" -ForegroundColor DarkGray
Write-Host ""

# Explicitly enter numista_mobile/ for all Flutter operations
Push-Location $MobileDir
Write-Host "  Working directory: $(Get-Location)" -ForegroundColor DarkGray

# Clear stale build output to prevent PathExistsException on repeated deploys
Write-Host "  Clearing stale build output..." -ForegroundColor DarkGray
Remove-Item -Recurse -Force "build\web" -ErrorAction SilentlyContinue
Write-Host "  Build output cleared." -ForegroundColor DarkGray

# (flutter analyze skipped to bypass warnings)

# Build (must run from numista_mobile/)
& flutter build web --release --base-href "/"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  [ERROR] flutter build web failed." -ForegroundColor Red
    Copy-Item $BackupFile $IndexFile -Force
    Pop-Location
    exit 1
}

Pop-Location
Write-Host ""
Write-Host "  Flutter web build complete." -ForegroundColor Green

# ── STEP 3: Firebase deploy ────────────────────────────────────────────────────
Write-Host ""
Write-Host "  [3/5] Deploying to Firebase Hosting (numista.ai)..." -ForegroundColor Yellow

# Explicitly enter numista_mobile/ — firebase.json and .firebaserc live here
Push-Location $MobileDir
Write-Host "  Working directory: $(Get-Location)" -ForegroundColor DarkGray
& firebase deploy --only hosting --project studio-9101802118-8c9a8

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  [ERROR] Firebase deploy failed." -ForegroundColor Red
    Copy-Item $BackupFile $IndexFile -Force
    Pop-Location
    exit 1
}

Pop-Location
Write-Host ""
Write-Host "  Firebase deploy complete." -ForegroundColor Green

# ── STEP 4: Restore the dev service-worker kill-switch ────────────────────────
Write-Host ""
Write-Host "  [4/5] Restoring dev service-worker kill-switch in index.html..." -ForegroundColor Yellow
Copy-Item $BackupFile $IndexFile -Force
Remove-Item $BackupFile -ErrorAction SilentlyContinue
Write-Host "  index.html restored for local dev." -ForegroundColor Green

# ── STEP 5: Verify live site ───────────────────────────────────────────────────
Write-Host ""
Write-Host "  [5/5] Verifying live site..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $response = Invoke-WebRequest -Uri "https://numista.ai" -UseBasicParsing -TimeoutSec 15
    if ($response.StatusCode -eq 200) {
        Write-Host "  https://numista.ai is UP (HTTP $($response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "  https://numista.ai returned HTTP $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Could not reach https://numista.ai - check manually." -ForegroundColor Yellow
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor DarkGray
}

# ── DONE (Frontend) ────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host "  FRONTEND DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "  =================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Live site:  https://numista.ai" -ForegroundColor Cyan
Write-Host "  Local dev:  http://localhost:8080 (run launch_numista.ps1)" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ACTION REQUIRED: Open https://numista.ai in your browser and" -ForegroundColor Yellow
Write-Host "  verify the change is live before marking this task complete." -ForegroundColor Yellow
Write-Host ""

# ── EMERGENCY BACKEND DEPLOY (OPTIONAL — only if backend also changed) ──────────
Write-Host "  -------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  EMERGENCY BACKEND DEPLOY" -ForegroundColor DarkGray
Write-Host "  -------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  Normally handled automatically by GitHub Actions." -ForegroundColor DarkGray
Write-Host "  Run the block below ONLY if the CI/CD pipeline is unavailable." -ForegroundColor DarkGray
Write-Host ""
Write-Host "  # ---- Emergency backend commands (run manually if needed) ----" -ForegroundColor DarkGray
Write-Host "  # cd numista_backend
  # gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
  # docker build -t us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest .
  # docker push us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest
  # gcloud run deploy numista-backend --image us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest --region us-central1 --project studio-9101802118-8c9a8 --quiet
  #
  # ---- Emergency scan service commands (run manually if needed) ----
  # gcloud run deploy numista-scan-service --source ./numista_backend/scan_service --project studio-9101802118-8c9a8 --region us-central1
  # ---------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""
Read-Host "  Press Enter to close"
