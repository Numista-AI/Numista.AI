# READY-TO-DEPLOY BATON — NET-816 FAIL-FIX R2 (v3.1)
Date: 11 Nov 2026 ~09:45 AM ET (America/New_York)  
From: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
To: Grok Bot CoS / Eric  
Status: **STOPPED AT READY-TO-DEPLOY** (Awaiting Eric's explicit typed deploy authorization)

---

## 1. Executive Summary
AG CoS v5 has executed the complete implementation and test matrix for **NET-816 Catalog Chunk 1 Fail-Fix Round 2 Plan v3.1** (`PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md`, SHA-256 `785b04e55cd3bc2ccefcf40b970e2139ad84aba679053dde7a59bb0c9ec13d04`) with deviations (a) and (b).

- **Full Built Commit SHA:** `eb8bb7ce95fa7164617eef0d0ff804465829e8c9` (short: `eb8bb7ce`)
- **Base Commit:** `a3d7dca20fbbaf06a522205b22d0740b600de52b` on local branch `p7-v8.9`
- **Verification:** All tests passed (738/738 unit/widget tests in `numista_mobile`), `flutter analyze` exit 0 (0 issues).
- **Deploy Script:** `deploy_preview.ps1` prepared and verified outside git tree (SHA-256 `884D610301277DE6FE416C33046FD846D12AFF336DF67A6DFEA7B2114BAFE81F`).
- **Deploy Status:** **STOPPED at READY-TO-DEPLOY**. Per `BATON_NET-816_AGCOS-V5_FAILFIX-R2_v3.1_IMPLEMENT-PREVIEW_20261110-2148.md` §4 step 4 and `NOTE_AGCOS-V5_NET-816_v3.1_STOP-AT-READY-TO-DEPLOY_AUTH-8de8365e_20261111-0913.md`, **NO DEPLOYMENT** will occur until Eric types his separate line:
  `YES DEPLOY p7-gate eb8bb7ce95fa7164617eef0d0ff804465829e8c9 ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b`
  AG CoS must NEVER generate, compose, or execute this string itself.

---

## 2. Git & Commit Details
- **Branch:** `p7-v8.9` (local only; zero pushes to origin)
- **Base:** `a3d7dca20fbbaf06a522205b22d0740b600de52b`
- **Built Commit SHA:** `eb8bb7ce95fa7164617eef0d0ff804465829e8c9`
- **Commit Message:** `fix(catalog): implement NET-816 chunk 1 fail-fix r2 plan v3.1`

### `git show --stat HEAD`
```text
commit eb8bb7ce95fa7164617eef0d0ff804465829e8c9
Author: Numista Deployer <deploy@numista.ai>
Date:   Wed Nov 11 09:37:53 2026 -0500

    fix(catalog): implement NET-816 chunk 1 fail-fix r2 plan v3.1

 numista_mobile/firebase.json                       |  2 +-
 numista_mobile/lib/main.dart                       | 62 ++++++++++++----
 .../lib/screens/catalog/catalog_browse_screen.dart | 36 +++++++---
 .../lib/services/melt_value_service.dart           | 37 +++++++++-
 .../catalog_chunk1_face_value_and_card_test.dart   | 84 +++++++++++++++++++++-
 numista_mobile/test/catalog_routing_test.dart      | 41 +++++++++++
 6 files changed, 238 insertions(+), 24 deletions(-)
```

---

## 3. Implementation Summary
1. **F1 (Routing):** `numista_mobile/lib/main.dart`
   - Added `CatalogRouteInfo` data class and pure helper `resolveCatalogRoute(Uri uri)`.
   - Pure parser handles path `/catalog`, `/catalog/<id>`, hash `/#/catalog`, `/#/catalog/<id>`, and hash query `/#/catalog?item=<id>`, while ignoring non-catalog routes (`/#/claim`).
   - Wired `resolveCatalogRoute(Uri.base)` in `main()` to direct app startup into catalog browse / detail.
2. **F2 (CSP Domains):** `numista_mobile/firebase.json`
   - Added `upload.wikimedia.org commons.wikimedia.org *.wikimedia.org images.metmuseum.org numismatics.org` to `img-src` and `connect-src`.
3. **F3 (Face Value Multiplier):** `numista_mobile/lib/services/melt_value_service.dart`
   - Parsed `(\d+|two|three|four|five)[- ]coin set` to extract multiplier before parenthetical stripping.
   - Added indeterminate `\bset\b` boundary guard returning `0.0`.
   - Multiplied final parsed face value by multiplier.
4. **Note 1 / D3′ (Two-Pass Search):** `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`
   - Implemented list-level two-pass filtering inside `_applyFilters()` across filtered entries.
   - Pass 1: Direct field substring match across title, subtitle, catalog ID, denomination, year, and tags.
   - Pass 2: Fallback multi-token whitespace split matching only if Pass 1 yields 0 items.
5. **F1 Tests:** `numista_mobile/test/catalog_routing_test.dart`
   - 6 test cases verifying all route resolution variants (pure parsing + non-catalog isolation).
6. **F3, F5/D2 & D3′ Widget Tests:** `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`
   - Line 139 updated to `'Dollar (two-coin set)': 2.00`.
   - Set multiplier unit tests (`Dollar (two-coin set)` = 2.00, qty 2 = 4.00, `Half Dollar (two-coin set)` = 1.00, indeterminate sets = 0.0).
   - Half dime melt math assertion tests at `$51.51` ($1.86) and reference `$30.00` ($1.09).
   - Real screen widget test for `Morgan dollar 1881` via `CatalogBrowseScreen(initialQuery: ...)`: verifies `5 items` found and all 5 cards render in `GridView`.
   - Real screen widget test for `1816`: verifies `0 items` found, `No matching catalog items found.` empty placeholder renders, and `GridView` is empty.

---

## 4. Test Verification Matrix
All verification commands were executed from `numista_mobile` and passed 100%:

### 1. `flutter analyze`
```text
Analyzing numista_mobile...
No issues found! (ran in 10.9s)
Exit code: 0
```

### 2. `flutter test test/catalog_routing_test.dart`
```text
00:00 +6: All tests passed!
Exit code: 0
```

### 3. `flutter test test/catalog_chunk1_face_value_and_card_test.dart`
```text
00:09 +9: All tests passed!
Exit code: 0
```

### 4. Full `flutter test`
```text
02:03 +738: All tests passed!
Exit code: 0
```
(Zero regressions across entire test suite of 738 tests).

---

## 5. Deploy Script Details & Deviation (b)
- **Script Location:** `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\deploy_preview.ps1`
- **File Size:** 7,390 bytes (outside git repository)
- **SHA-256:** `884D610301277DE6FE416C33046FD846D12AFF336DF67A6DFEA7B2114BAFE81F`
- **Deviation (b) Diff vs Plan v3.1 §2.2:**
```powershell
    $preLiveReleaseTime = $preLiveChannel.release.releaseTime
    if ([string]::IsNullOrWhiteSpace($preLiveReleaseTime)) {
        Pop-Location
        throw "FATAL: Live channel releaseTime is null or empty in pre-deploy listing"
    }
```
All other lines of `deploy_preview.ps1` match Plan v3.1 §2.2 byte-for-byte.

---

## 6. Current Deployment Gate Status
- **STOPPED AT READY-TO-DEPLOY:**
  `deploy_preview.ps1` has **NOT** been run.
- **Awaiting Eric's Typed Deploy String:**
  Plan §2.1, BATON §4 step 4, and `NOTE_AGCOS-V5_NET-816_v3.1_STOP-AT-READY-TO-DEPLOY_AUTH-8de8365e_20261111-0913.md` require:
  `YES DEPLOY p7-gate eb8bb7ce95fa7164617eef0d0ff804465829e8c9 ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b`
  typed explicitly by Eric.
- **RSI Engineer Note Awareness:**
  Noted RSI proposal (`NOTE_RSI_AWARENESS_AGCOS-V5_NOV11-AM_20261111-0935.md`) regarding optional Code Reviewer PASS on `BUILT_SHA` prior to deploy YES. Eric decides.

---

## 7. Invariants & Safety Holds
- **HOLD `74611e05` stands:** Never deploy `c547b7a0`.
- **HOLD `41b8bd5f` stands:** Stripe live remains OFF; zero Stripe, Firestore, or GCS mutations.
- **`origin/main` untouched:** Stays locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`.
- **Zero remote branch pushes:** Code commit `eb8bb7ce` remains strictly local on branch `p7-v8.9`.
