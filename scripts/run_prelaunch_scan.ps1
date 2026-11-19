# scripts/run_prelaunch_scan.ps1 — Numista.AI Unified 10-Gate Pre-Launch Scan Orchestrator (v1.1)
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('Quick', 'Full')]
    [string]$Mode = 'Quick',

    [Parameter(Mandatory = $false)]
    [switch]$SkipCloudProbes
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $RepoRoot

$PythonExe = Join-Path $RepoRoot 'numista_backend\.venv\Scripts\python.exe'
$DateStamp = Get-Date -Format 'yyyy-MM-dd'
$TimeStampEt = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$ReportsDir = Join-Path $RepoRoot 'numista_tests\reports'
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null

$PortableReportPath = Join-Path $ReportsDir "PRELAUNCH_SCAN_REPORT_$DateStamp.md"
$RootScanReportPath = Join-Path $RepoRoot 'SCAN_REPORT.md'
$ReviewMirrorDir = Join-Path $RepoRoot '1 NUMISTA.AI\BETA TEST\MY TESTING\14 NOV 2026\Checks and Tests'

function Assert-NativeZero([string]$Label) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Label exited with code $LASTEXITCODE"
    }
}

function Get-ObjProp($Obj, [string]$Name) {
    if ($null -eq $Obj) { return $null }
    $prop = $Obj.PSObject.Properties[$Name]
    if ($null -eq $prop) { return $null }
    return $prop.Value
}

function Invoke-ScanGate {
    param(
        [Parameter(Mandatory = $true)][string]$GateId,
        [Parameter(Mandatory = $true)][string]$Title,
        [Parameter(Mandatory = $true)][int]$Points,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host "[$GateId] $Title ($Points pts)" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    $global:LASTEXITCODE = 0
    try {
        & $Action | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "Native command exited with code $LASTEXITCODE"
        }
        $sw.Stop()
        return [PSCustomObject]@{
            GateId       = $GateId
            Title        = $Title
            MaxPoints    = $Points
            EarnedPoints = $Points
            Status       = '🟢 PASS'
            DurationSec  = [math]::Round($sw.Elapsed.TotalSeconds, 1)
            Detail       = 'All assertions passed'
        }
    } catch {
        $sw.Stop()
        Write-Host "[$GateId] FAILED: $($_.Exception.Message)" -ForegroundColor Red
        return [PSCustomObject]@{
            GateId       = $GateId
            Title        = $Title
            MaxPoints    = $Points
            EarnedPoints = 0
            Status       = '🔴 FAIL'
            DurationSec  = [math]::Round($sw.Elapsed.TotalSeconds, 1)
            Detail       = $_.Exception.Message
        }
    }
}

$Results = [System.Collections.Generic.List[object]]::new()
$HoldNotes = [System.Collections.Generic.List[string]]::new()

# ── GATE 0: Git Hygiene, Clean origin/dev Sync & Environment Integrity (5 pts) ──
$Results.Add((Invoke-ScanGate -GateId 'Gate 0' -Title 'Git Hygiene, origin/dev Sync & .env/.venv' -Points 5 -Action {
    git fetch origin
    Assert-NativeZero 'git fetch origin'
    $branch = (git rev-parse --abbrev-ref HEAD).Trim()
    if ($branch -eq 'main') {
        throw "Never run pre-launch scan directly on 'main'; use 'dev' or an origin/dev-synced branch"
    }
    $behindCount = [int](git rev-list --count HEAD..origin/dev).Trim()
    if ($behindCount -gt 0) {
        throw "HEAD ($branch) is $behindCount commit(s) behind origin/dev. Run git rebase origin/dev"
    }
    if (Test-Path 'main.py') { throw 'Root main.py shadows numista_backend/main.py' }
    $dirtyArtifacts = git status --porcelain -- '*.db' '*.cache' 'scratch/' 'output/'
    if ($dirtyArtifacts) { throw "Dirty artifacts in git status:`n$dirtyArtifacts" }

    @'
from pathlib import Path
for p in ['numista_backend/.env', 'numista_tests/.env']:
    fp = Path(p)
    if fp.exists():
        fp.read_bytes().decode('utf-8')
for mod in ['fastapi', 'pydantic', 'google.genai', 'firebase_admin', 'stripe', 'reportlab', 'httpx', 'json_repair']:
    __import__(mod)
print('Gate 0 Python UTF-8 + 8/8 imports OK')
'@ | & $PythonExe -
    Assert-NativeZero 'Gate 0 Python check'
}))

# ── GATE 1: Gemini 4 Model Governance & Parity (10 pts) ─────────────────────────
$Results.Add((Invoke-ScanGate -GateId 'Gate 1' -Title 'Gemini 4 Model Governance & Config Parity' -Points 10 -Action {
    & $PythonExe -m pytest `
        numista_backend/tests/test_gemini_config_parity_03.py `
        numista_backend/tests/test_gemini4_review_05.py `
        numista_backend/tests/test_image_model_router.py -v
    Assert-NativeZero 'Gate 1 pytest'

    @'
import re, subprocess, sys
from pathlib import Path

banned = re.compile(r'gemini-(?:1\.5|2\.0|2\.5|3\.0|3\.1-pro|3\.6|3\.7|3\.8)[\w-]*|gemini-3\.5-flash(?!-lite)', re.I)
tracked = subprocess.run(['git', 'ls-files', 'numista_backend', 'numista_mobile/lib', 'numista_hardware', 'numista_ai'],
                         capture_output=True, text=True, check=True).stdout.splitlines()
skip_parts = {'tests', '_archive', 'scratch', 'database', '.venv', 'node_modules', '_scripts'}
allow = [('numista_mobile/lib/screens/home_dashboard.dart', re.compile(r"^\s*'(?:Ai|Model)[^']*gemini-3\.[78]-flash"))]
hits = []
for rel in tracked:
    p = Path(rel)
    if not p.is_file() or p.suffix not in {'.py', '.dart'} or any(part in skip_parts for part in p.parts):
        continue
    for i, line in enumerate(p.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
        if banned.search(line) and not any(rel == ap and pat.search(line) for ap, pat in allow):
            hits.append(f'{rel}:{i}: {line.strip()}')
if hits:
    print('\n'.join(hits))
    sys.exit(1)
print('Gate 1 active-code model scan clean (0 banned hits)')
'@ | & $PythonExe -
    Assert-NativeZero 'Gate 1 model regex scan'
}))

# ── GATE 2: Security, Route Parity, Auth Guards & Firebase Rules/Indexes (20 pts)
$Results.Add((Invoke-ScanGate -GateId 'Gate 2' -Title 'Security, Route Parity, Auth & Firestore/Storage' -Points 20 -Action {
    Push-Location (Join-Path $RepoRoot 'numista_backend')
    try {
        $env:ASSERT_ROUTE_PARITY_OFFLINE = '1'
        & $PythonExe -B scripts/assert_route_parity.py --diff
        Assert-NativeZero 'assert_route_parity.py'
    } finally {
        Pop-Location
    }

    & $PythonExe -m pytest `
        numista_backend/tests/test_default_deny_auth.py `
        numista_backend/tests/test_security_review_01.py `
        numista_backend/tests/test_security_review_02.py `
        numista_backend/tests/test_idor_fixes.py `
        numista_backend/tests/test_auth_security.py `
        numista_backend/tests/test_req031_auth.py `
        numista_backend/tests/test_cors_auth.py `
        numista_backend/tests/test_cors_public_paths.py `
        numista_backend/tests/test_stripe_auth.py `
        numista_backend/tests/test_expiring_photo_links.py `
        numista_backend/tests/test_coin_image_privacy.py `
        numista_backend/tests/test_hardware_installer_url.py `
        numista_backend/tests/test_hardware_secret_free_build.py -v
    Assert-NativeZero 'Gate 2 backend security pytest'

    Push-Location (Join-Path $RepoRoot 'numista_mobile')
    try {
        flutter test --no-pub --concurrency=2 `
            test/auth_guard_test.dart `
            test/auth_gate_navigation_test.dart `
            test/auth_service_pin_lockout_test.dart `
            test/services/bearer_header_integration_test.dart `
            test/services/signed_photo_url_service_test.dart `
            test/widgets/signed_storage_image_test.dart `
            test/utils/owned_storage_url_test.dart `
            test/desktop_agent_download_screen_test.dart
        Assert-NativeZero 'Gate 2 Flutter security tests'
    } finally {
        Pop-Location
    }

    @'
import json, re
from pathlib import Path
rule_re = re.compile(r"^rules_version\s*=\s*['\"]2['\"];", re.M)
m = Path('numista_mobile/firestore.rules').read_text(encoding='utf-8')
b = Path('numista_backend/firestore.rules').read_text(encoding='utf-8')
m_match, b_match = rule_re.search(m), rule_re.search(b)
assert m_match and b_match, 'Missing rules_version = 2 header'
m_body = m[m_match.start():].replace('\r\n', '\n').strip()
b_body = b[b_match.start():].replace('\r\n', '\n').strip()
assert m_body == b_body, f'Firestore rules drift: mobile={len(m_body)} vs backend={len(b_body)}'
assert 'wishlist_email_logs' in m_body, 'Missing wishlist_email_logs in firestore.rules'
idx_p = Path('numista_mobile/firestore.indexes.json')
assert idx_p.exists(), 'Missing numista_mobile/firestore.indexes.json'
idx_data = json.loads(idx_p.read_text(encoding='utf-8'))
assert isinstance(idx_data.get('indexes'), list) and len(idx_data['indexes']) > 0, 'Empty firestore.indexes.json'
sr_p = Path('numista_backend/storage.rules')
assert sr_p.exists(), 'Missing numista_backend/storage.rules'
sr_text = sr_p.read_text(encoding='utf-8')
assert 'allow read: if true' not in sr_text and 'allow read, write: if false' in sr_text, 'Invalid storage.rules'
print(f'Gate 2.4 OK (rules={len(m_body)}c, indexes={len(idx_data["indexes"])}, storage=32L default-deny)')
'@ | & $PythonExe -
    Assert-NativeZero 'Gate 2.4 Firebase rules/indexes/storage check'
}))

# ── GATE 3: Full Backend Pytest, Hardware & Container Parity (15 pts) ───────────
$Results.Add((Invoke-ScanGate -GateId 'Gate 3' -Title 'Backend Pytest, Hardware Filter & Container Parity' -Points 15 -Action {
    $pytestLog = Join-Path $ReportsDir 'pytest-output.txt'
    & $PythonExe -m pytest numista_backend/tests/ -q --tb=short 2>&1 | Tee-Object -FilePath $pytestLog
    Assert-NativeZero 'numista_backend/tests/'

    & $PythonExe -m pytest `
        numista_backend/tests/test_container_import_path.py `
        numista_backend/tests/test_working_tree_hazards_04.py -v
    Assert-NativeZero 'Container & working-tree tests'

    if (-not (Test-Path 'numista_hardware/test_camera_filter.py')) {
        throw 'Missing numista_hardware/test_camera_filter.py'
    }
    & $PythonExe -m pytest numista_hardware/test_camera_filter.py -v
    Assert-NativeZero 'Hardware camera filter tests'

    & $PythonExe -m pytest numista_tests/ -q --tb=short
    Assert-NativeZero 'numista_tests/ pytest suite'
}))

# ── GATE 4: Flutter Analyze, Widget Suites & Release Web Build (15 pts) ─────────
$Results.Add((Invoke-ScanGate -GateId 'Gate 4' -Title 'Flutter Analyze, Track Suites & Release Web Build' -Points 15 -Action {
    Push-Location (Join-Path $RepoRoot 'numista_mobile')
    try {
        flutter analyze --no-fatal-infos
        Assert-NativeZero 'flutter analyze'
        flutter test --no-pub --concurrency=2
        Assert-NativeZero 'flutter test (all)'
        flutter test --no-pub --concurrency=2 `
            test/home_sidebar_v21_test.dart `
            test/wishlist_auto_fill_test.dart `
            test/morgan_copilot_test.dart `
            test/morgan_voice_interlock_test.dart `
            test/morgan_a11y_keyboard_test.dart `
            test/microscope_scan_screen_test.dart `
            test/screens/unified_coin_detail_screen_test.dart `
            test/screens/catalog_soft404_routing_test.dart `
            test/catalog_browse_test.dart `
            test/catalog_chunk1_face_value_and_card_test.dart
        Assert-NativeZero 'flutter test (Nov 13-14 explicit tracks)'
        flutter build web --release --base-href '/'
        Assert-NativeZero 'flutter build web --release'
    } finally {
        Pop-Location
    }
    & $PythonExe -m pytest numista_mobile/test/web/static_route_html_test.py -v
    Assert-NativeZero 'static_route_html_test.py'
}))

# ── GATE 5: Numismatic Domain, 2-Field Mint, Valuation & Estate/Transfer (10 pts)
$Results.Add((Invoke-ScanGate -GateId 'Gate 5' -Title 'Domain Invariants (35 Programs, 2-Field Mint, CPG, Estate)' -Points 10 -Action {
    & $PythonExe -m pytest `
        numista_backend/tests/test_series_manifest_sync.py `
        numista_backend/tests/test_catalog_slot_counts.py `
        numista_backend/tests/test_us_mint_catalog.py `
        numista_backend/tests/test_usmint_releases_scraper.py `
        numista_backend/tests/test_mint_helpers.py `
        numista_backend/tests/test_migrate_two_field_mint.py `
        numista_backend/tests/test_mint_review_04.py `
        numista_backend/tests/test_greysheet.py `
        numista_backend/tests/test_greysheet_bid_display.py `
        numista_backend/tests/test_valuations.py `
        numista_backend/tests/test_valuation_cap.py `
        numista_backend/tests/test_valuation_integrity.py `
        numista_backend/tests/test_wishlist_email_and_share.py `
        numista_backend/tests/test_beta_estate_pipeline.py `
        numista_backend/tests/test_scan_service_estate_report.py `
        numista_backend/tests/test_transfer.py `
        numista_backend/tests/test_transfer_service_privacy.py -v
    Assert-NativeZero 'Gate 5 backend domain tests'

    Push-Location (Join-Path $RepoRoot 'numista_mobile')
    try {
        flutter test --no-pub --concurrency=2 `
            test/slot_resolver_50sq_test.dart test/slot_resolver_awq_test.dart `
            test/slot_resolver_collectibles_test.dart test/slot_resolver_eisenhower_test.dart `
            test/slot_resolver_kennedy_test.dart test/slot_resolver_phase4a_test.dart `
            test/slot_resolver_washington_test.dart test/set_expansion_helper_test.dart `
            test/mint_helpers_test.dart test/utils/mint_two_field_consistency_test.dart `
            test/mint_product_fields_test.dart test/greysheet_bid_display_test.dart `
            test/valuation_mode_test.dart test/widgets/my_collection_card_pricing_test.dart `
            test/estate_models_test.dart test/lateral_transfer_test.dart
        Assert-NativeZero 'Gate 5 Flutter domain tests'
    } finally {
        Pop-Location
    }
}))

# ── GATE 6: Cloud Infrastructure, Secret Bindings & Live Endpoint Probes (10 pts)
$Results.Add((Invoke-ScanGate -GateId 'Gate 6' -Title 'Cloud Run Secret Bindings & Live Endpoint Probes' -Points 10 -Action {
    if ($Mode -eq 'Full' -and $SkipCloudProbes) {
        throw '-SkipCloudProbes is forbidden in -Mode Full'
    }
    if (-not $SkipCloudProbes) {
        $null = gcloud auth print-access-token 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw 'gcloud is not authenticated. Run gcloud auth login (or pass -Mode Quick -SkipCloudProbes with manual receipt).'
        }
        foreach ($svc in @('numista-backend', 'numista-scan-service')) {
            $raw = gcloud run services describe $svc --region=us-central1 --project=studio-9101802118-8c9a8 --format=json 2>$null
            if ($LASTEXITCODE -ne 0 -or -not $raw) { throw "Failed to describe Cloud Run service $svc" }
            $parsed = $raw | ConvertFrom-Json
            $tplSpec = Get-ObjProp (Get-ObjProp (Get-ObjProp $parsed 'spec') 'template') 'spec'
            $containers = @(Get-ObjProp $tplSpec 'containers')
            $c = if ($containers.Count -gt 0) { $containers[0] } else { $null }
            $bound = @()
            foreach ($e in @(Get-ObjProp $c 'env')) {
                if ($null -eq $e) { continue }
                $eVal = Get-ObjProp $e 'value'
                $hasLit = ($null -ne $eVal) -and ($eVal.ToString().Trim().Length -gt 0)
                $vFrom = Get-ObjProp $e 'valueFrom'
                $skRef = Get-ObjProp $vFrom 'secretKeyRef'
                $sRef = Get-ObjProp $skRef 'name'
                $hasRef = ($null -ne $sRef) -and ($sRef.ToString().Trim().Length -gt 0)
                $eName = Get-ObjProp $e 'name'
                if (($hasLit -or $hasRef) -and $eName) { $bound += $eName }
            }
            $volMap = @{}
            foreach ($v in @(Get-ObjProp $tplSpec 'volumes')) {
                if ($null -eq $v) { continue }
                $vSec = Get-ObjProp $v 'secret'
                $secName = Get-ObjProp $vSec 'secretName'
                $vName = Get-ObjProp $v 'name'
                if ($vName -and $secName) { $volMap[$vName] = $secName }
            }
            foreach ($vm in @(Get-ObjProp $c 'volumeMounts')) {
                if ($null -eq $vm) { continue }
                $vmName = Get-ObjProp $vm 'name'
                if ($vmName -and $volMap.ContainsKey($vmName)) { $bound += $volMap[$vmName] }
            }
            if ($svc -eq 'numista-backend') {
                $baselineReq = @('GREYSHEET_API_KEY', 'GREYSHEET_API_TOKEN', 'PCGS_BEARER_TOKEN', 'EBAY_CERT_ID', 'STRIPE_WEBHOOK_SECRET', 'STRIPE_PUBLISHABLE_KEY')
                $missBase = $baselineReq | Where-Object { $_ -notin $bound }
                if ($missBase) { throw "Missing baseline Cloud Run bindings on numista-backend: $($missBase -join ', ')" }
                $hasEmail = ('SENDGRID_API_KEY' -in $bound) -or (('SMTP_HOST' -in $bound) -and ('SMTP_USER' -in $bound) -and ('SMTP_PASSWORD' -in $bound))
                if (-not $hasEmail) { throw 'Missing SENDGRID_API_KEY or SMTP_* triplet on numista-backend' }

                $launchReq = @('STRIPE_SECRET_KEY', 'CRON_SECRET')
                $missingLaunch = @($launchReq | Where-Object { $_ -notin $bound })
                if ($missingLaunch.Count -gt 0) {
                    if ($Mode -eq 'Full') {
                        throw "Missing required launch Cloud Run bindings on numista-backend: $($missingLaunch -join ', ')"
                    } else {
                        $HoldNotes.Add("Cloud Run numista-backend missing pre-launch bindings: $($missingLaunch -join ', ') (must be bound in GCP before -Mode Full Launch Gate)")
                    }
                }
            } elseif ($bound.Count -eq 0) {
                if ($svc -eq 'numista-scan-service') {
                    # Intentionally ADC-only: scan_service/main.py uses Application Default Credentials
                    # and reads no Secret Manager bindings at runtime (verified against scan_service/Dockerfile).
                    Write-Host "    [OK] $svc is intentionally ADC-only (0 secret/env bindings expected)." -ForegroundColor DarkGray
                } else {
                    throw "$svc has 0 valid env/secret bindings"
                }
            }
        }
    } else {
        $HoldNotes.Add('Gate 6.1 Cloud Run gcloud describe skipped under -SkipCloudProbes (Quick mode ONLY — attach manual Cloud Console secret receipt)')
    }

    @'
import urllib.request, urllib.error, json
for url in [
    'https://numista.ai/',
    'https://numista.ai/catalog',
    'https://numista.ai/pricing',
    'https://numista-backend-568985927038.us-central1.run.app/api/spot_prices',
    'https://numista-scan-service-568985927038.us-central1.run.app/health',
]:
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Numista-PreLaunch/1.1'}), timeout=15) as r:
        assert r.status == 200, f'{url} HTTP {r.status}'
        body = r.read(4096).decode('utf-8', 'ignore')
        if url == 'https://numista.ai/':
            assert 'navigator.serviceWorker.getRegistrations' not in body, 'Dev SW leaked in prod!'
        if url.endswith('/api/spot_prices'):
            d = json.loads(body)
            assert all(k in d for k in ('Gold', 'Silver', 'Platinum', 'Palladium')), 'Bad spot_prices JSON'
for priv in [
    'https://numista-backend-568985927038.us-central1.run.app/api/morgan/copilot',
    'https://numista-backend-568985927038.us-central1.run.app/api/wishlist/send-email',
]:
    try:
        urllib.request.urlopen(urllib.request.Request(priv, data=b'{}', method='POST', headers={'Content-Type': 'application/json'}), timeout=15)
        raise AssertionError(f'{priv} allowed anonymous POST')
    except urllib.error.HTTPError as e:
        assert e.code in (401, 403), f'{priv} returned {e.code}'
print('Gate 6.2 live HTTP 200 + auth-deny 401/403 probes OK')
'@ | & $PythonExe -
    Assert-NativeZero 'Gate 6.2 HTTP probes'
}))

# ── FULL MODE ONLY: GATES 7 & 8 (10 pts auto + Gate 9 manual 5 pts) ───────────
if ($Mode -eq 'Full') {
    $Results.Add((Invoke-ScanGate -GateId 'Gate 7' -Title 'Senior UX & WCAG AA/AAA Accessibility Guards' -Points 5 -Action {
        Push-Location (Join-Path $RepoRoot 'numista_mobile')
        try {
            flutter test --no-pub --concurrency=2 `
                test/home_sidebar_v21_test.dart `
                test/wishlist_auto_fill_test.dart `
                test/morgan_a11y_keyboard_test.dart
            Assert-NativeZero 'Gate 7 Flutter a11y tests'
        } finally {
            Pop-Location
        }
    }))

    $Results.Add((Invoke-ScanGate -GateId 'Gate 8' -Title 'Full Playwright E2E + numista_qc Stack B + Track B' -Points 5 -Action {
        foreach ($reqSpec in @(
            'numista_tests/tests/27-ux-home-sidebar-v21.spec.js',
            'numista_tests/tests/28-wishlist-autofill-email.spec.js',
            'numista_tests/tests/29-morgan-copilot-harness.spec.js'
        )) {
            if (-not (Test-Path $reqSpec)) { throw "Missing Full-mode prerequisite spec: $reqSpec (see Fix 7)" }
        }
        $navContent = Get-Content 'numista_tests/tests/05-navigation.spec.js' -Raw
        if ($navContent -match 'mouse\.click\(80,\s*231\)') {
            throw '05-navigation.spec.js still contains stale pre-v2.1 pixel coordinates (80, 231)'
        }

        Push-Location (Join-Path $RepoRoot 'numista_tests')
        try {
            npx playwright test
            Assert-NativeZero 'npx playwright test'
            node generate_report.js
            Assert-NativeZero 'node generate_report.js'
        } finally {
            Pop-Location
        }

        @'
import json, sys
from pathlib import Path
rp = Path('numista_tests/reports/test-results.json')
assert rp.exists(), 'Missing numista_tests/reports/test-results.json'
data = json.loads(rp.read_text(encoding='utf-8'))
stats = data.get('stats', {})
expected = int(stats.get('expected', 0))
unexpected = int(stats.get('unexpected', 0))
print(f'Playwright test-results.json: expected={expected}, unexpected={unexpected}, skipped={stats.get("skipped", 0)}')
if expected <= 10:
    print('BLOCKER: Smoke-only Playwright run (expected <= 10) cannot satisfy Full Launch Gate!')
    sys.exit(1)
if unexpected > 0:
    print('BLOCKER: Playwright failures detected!')
    sys.exit(1)
'@ | & $PythonExe -
        Assert-NativeZero 'Playwright full-suite validation'

        & (Join-Path $RepoRoot 'numista_qc\run_qc.ps1') -Layer all -SkipFlutterChecks
        Assert-NativeZero 'numista_qc Stack B'
    }))
}

# ── Compute Final Status & Write Dual Reports (Portable + Review Mirror) ────────
$Earned = ($Results | Measure-Object -Property EarnedPoints -Sum).Sum
$MaxAuto = ($Results | Measure-Object -Property MaxPoints -Sum).Sum
$FailedCount = @($Results | Where-Object { $_.Status -match 'FAIL' }).Count

$OverallStatus = if ($FailedCount -gt 0) {
    '🔴 FAIL'
} elseif ($HoldNotes.Count -gt 0 -or $Mode -eq 'Quick') {
    if ($Mode -eq 'Quick') { '🟡 PASS WITH HOLDS (Quick Mode Only — Run -Mode Full + Gate 9 Before Launch)' } else { '🟡 PASS WITH HOLDS' }
} else {
    '🟡 PASS WITH HOLDS (Awaiting Gate 9 Eric Sign-Off for 100/100)'
}

$Rows = ($Results | ForEach-Object {
    "| **$($_.GateId)** | $($_.Title) | $($_.Status) | $($_.EarnedPoints) / $($_.MaxPoints) | $($_.DurationSec)s | $($_.Detail) |"
}) -join "`n"

$HoldBlock = if ($HoldNotes.Count -gt 0) {
    "`n## Holds & Caveats`n" + (($HoldNotes | ForEach-Object { "- $_" }) -join "`n") + "`n"
} else { '' }

$ReportBody = @"
# PRE-LAUNCH SCAN REPORT (`$Mode` Mode)

- **Status:** **$OverallStatus**
- **Scan Timestamp:** $TimeStampEt
- **Git Branch / SHA:** ``$((git rev-parse --abbrev-ref HEAD).Trim())`` @ ``$((git rev-parse HEAD).Trim())``
- **Automated Score:** **$Earned / $MaxAuto** (Full Gate 9 adds `5 pts` manual Eric Sign-Off = `100 pts`)

| Gate | Domain | Status | Score | Duration | Detail |
|---|---|---|---|---:|---|
$Rows
$HoldBlock
"@

Set-Content -Path $PortableReportPath -Value $ReportBody -Encoding utf8
Set-Content -Path $RootScanReportPath -Value $ReportBody -Encoding utf8
if (Test-Path $ReviewMirrorDir) {
    $MirrorPath = Join-Path $ReviewMirrorDir "PRELAUNCH_SCAN_REPORT_$DateStamp.md"
    Copy-Item -Path $PortableReportPath -Destination $MirrorPath -Force
}

Write-Host "`nScan complete: $OverallStatus ($Earned / $MaxAuto) -> $PortableReportPath"
if ($FailedCount -gt 0) { exit 1 }
exit 0
