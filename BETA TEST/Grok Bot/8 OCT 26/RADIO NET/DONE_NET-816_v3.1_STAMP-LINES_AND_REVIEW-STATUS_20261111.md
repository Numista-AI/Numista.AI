# DONE / ACK — NET-816 v3.1: version.json Stamp Lines & Code Reviewer PASS Acknowledgment
Date: 11 Nov 2026 ~10:28 AM ET (America/New_York)  
From: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
To: Grok Bot CoS / Eric / Code Reviewer  
References:
- `NOTE_AGCOS-V5_NET-816_v3.1_DEPLOY-ALSO-WAITS-CODE-REVIEWER-PASS_20261111-1000.md`
- `NOTE_AGCOS-V5_NET-816_v3.1_REVIEW-COPY-FOR-CODE-REVIEWER_eb8bb7ce_20261111-1007.md`
- `NOTE_AGCOS-V5_NET-816_v3.1_REVIEW-COPY-OPTIONAL_STAMP-LINES-STILL-REQUIRED_20261111-1010.md`
- `CODE_REVIEW_NET-816_v3.1_eb8bb7ce_20261111.md` (Code Reviewer PASS)

---

## 1. Exact File & Line Citations for `version.json git_commit = BUILT_SHA` Stamping

Per Desk requirement (Notes `d3a9097e` and `8e744dd2`), here are the exact file paths, line numbers, and verbatim quotes in `deploy_preview.ps1` that stamp and assert `git_commit = BUILT_SHA`:

**File Path:** `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\deploy_preview.ps1`  
**Size:** 7,390 bytes  
**SHA-256:** `884D610301277DE6FE416C33046FD846D12AFF336DF67A6DFEA7B2114BAFE81F`  

### A. Pre-Deploy Stamping & In-Worktree Assertion (`deploy_preview.ps1` lines 91–107):
```powershell
    # 6. F4: version.json git_commit Stamping (UTF-8 without BOM)
    $versionPath = Join-Path (Get-Location).Path "build\web\version.json"
    if (-not (Test-Path $versionPath)) {
        throw "FATAL: build\web\version.json not found after build"
    }

    $jsonContent = Get-Content -Path $versionPath -Raw | ConvertFrom-Json
    $jsonContent | Add-Member -NotePropertyName "git_commit" -NotePropertyValue $resolvedSha -Force
    $stampedJson = $jsonContent | ConvertTo-Json -Depth 4
    [System.IO.File]::WriteAllText($versionPath, $stampedJson, (New-Object System.Text.UTF8Encoding($false)))

    # Verify stamp
    $verifyJson = Get-Content -Path $versionPath -Raw | ConvertFrom-Json
    if ($verifyJson.git_commit -ne $resolvedSha) {
        throw "FATAL: Verification failed: git_commit ($($verifyJson.git_commit)) != $resolvedSha"
    }
    Write-Host "==> version.json verified stamped with git_commit: $resolvedSha" -ForegroundColor Green
```

### B. Post-Deploy Served Readback Assertion (`deploy_preview.ps1` lines 143–149):
```powershell
    # Verify version.json served by p7-gate (D4′)
    Write-Host "==> Checking $p7Url/version.json..." -ForegroundColor Cyan
    $deployedVersion = Invoke-RestMethod -Uri "$p7Url/version.json" -TimeoutSec 15
    if (-not $deployedVersion -or $deployedVersion.git_commit -ne $resolvedSha) {
        throw "FATAL: Served version.json git_commit ($($deployedVersion.git_commit)) != $resolvedSha"
    }
    Write-Host "==> Deployed version.json verified matching $resolvedSha" -ForegroundColor Green
```

### C. Cache Prevention in `firebase.json` (`numista_mobile/firebase.json` lines 190–194):
```json
      {
        "source": "version.json",
        "headers": [
          { "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" }
        ]
      },
```
*(Ensures the deployed readback at `$p7Url/version.json` is never stale).*

---

## 2. Acknowledgment of Code Reviewer PASS
AG CoS v5 formally acknowledges receipt of [`CODE_REVIEW_NET-816_v3.1_eb8bb7ce_20261111.md`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/11%20NOV%2026/CODE_REVIEW_NET-816_v3.1_eb8bb7ce_20261111.md):
- **Verdict:** **PASS** (0 Blocker, 0 Major findings).
- **Target SHA:** `eb8bb7ce95fa7164617eef0d0ff804465829e8c9`.
- **Pre-flight & Invariants Confirmed:** All 6 modified files match plan §4; working tree porcelain clean for `numista_mobile` and `numista_backend`; zero backend, user-data, auth, or Stripe changes.
- **Field Tester Procedure Note Noted:** Tester must open URL fresh or hard-reload when testing `/#/catalog` in a browser.

---

## 3. Current Gate Status
- **Code Reviewer Gate:** **PASSED** (`CODE_REVIEW_NET-816_v3.1_eb8bb7ce_20261111.md`).
- **Deploy Authorization Gate:** **AWAITING ERIC'S TYPED LINE**.
  Per Standing Orders, Baton §4 step 4, and Note `bf37ab4b`:
  AG CoS will **NOT** deploy until Eric explicitly types:
  ```text
  YES DEPLOY p7-gate eb8bb7ce95fa7164617eef0d0ff804465829e8c9 ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b
  ```
  *(AG CoS never composes or executes this approval line itself).*

---

## 4. Invariants Held
- Code remains strictly local on branch `p7-v8.9` (zero pushes to origin).
- `origin/main` untouched at `9f04550a45fa4da082ba8948c2d89a521a90fa45`.
- HOLD `74611e05` (no `c547b7a0`) and HOLD `41b8bd5f` (Stripe live OFF) stand in full effect.
