# DONE BATON — NET-816 FAIL-FIX R2 — PLAN ONLY — v3.1 narrow fix (from CoS 96)
Date: 10 Nov 2026 ~9:22 PM ET
From: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
To: Grok Bot CoS

## 1. Plan Delivery Metadata
- **New File Name:** `PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md`
- **Location:** `1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\` (and byte-identical mirror in `Carbon\`)
- **On-Disk File Size:** `41,293 bytes` (LF line endings)
- **On-Disk SHA-256:** `785B04E55CD3BC2CCEFCF40B970E2139AD84ABA679053DDE7A59BB0C9EC13D04`
- **Base Plan:** `PLAN_NET-816_FAILFIX-R2_v3_AGCOS-V5_20261110.md` (35,380 B, SHA-256 `e7c54bab6a756c43a3e8aafc8ea7614b884a1d62dcda1ca6761c848e37557f75`)
- **Iteration:** NET-816 R2 track attempt 4 of 10; AG CoS v5 try 4 of 4

---

## 2. Closure Map (D3′, D4′ → Plan Lines)
| Deduction | Focus | Exact Plan Lines in v3.1 | Resolution & Verification Evidence |
|---|---|---|---|
| **D3′** | List-Level Two-Pass Search & Real Screen Widget Test | Lines 359–435 | Implements list-level two-pass filtering inside `_applyFilters()` (`catalog_browse_screen.dart:112-200`). Filters non-query criteria first; Pass 1 performs direct substring match across filtered items; Pass 2 performs multi-token fallback only if Pass 1 returns 0 items. Verified on real `assets/catalog/catalog_public_v1.json` at `a3d7dca2`: `"1842 Liberty Seated dollar"` -> Pass 1, 1 item (`['1842 Liberty Seated dollar']`); `"Morgan dollar 1881"` -> Pass 2, 5 items (`['1881-CC Morgan Silver Dollars', ...]`); `"1816"` -> Pass 2, 0 items. Verified on real screen via `test/catalog_chunk1_face_value_and_card_test.dart` using real helper `pumpLoadedCatalog` and `CatalogBrowseScreen(initialQuery: ...)`: `:348-385` passes with exactly 1 card (`findsOneWidget`) untouched; added 5-card test for 1881 Morgan and 0-card empty state test for 1816. |
| **D4′** | Preview Host Regex, Throw on Skip, Live Release Timestamp Invariance, Repo Root Assertion | Lines 480–520, Lines 560–630 | Updated preview host regex to `^https://numista-vault--p7-gate-[a-z0-9]+\.web\.app` matching Hosting site `numista-vault`. Throws unconditionally if preview URL is missing or any route check fails (never prints "verified" on skip). Implements pre-deploy live channel release time capture via `firebase hosting:channel:list --project studio-9101802118-8c9a8 --json` and post-deploy re-read with `$LASTEXITCODE` check, throwing if live `releaseTime` changes or `p7-gate` is missing. Fixes repo root assertion with fixed path `C:\Users\ericd\Documents\MyVertexProject` and asserts `git rev-parse --show-toplevel`. |

---

## 3. Surgical Line Diff against v3 (`e7c54bab...7f75`)
Changes are strictly isolated to allowed areas (header/note, §1.6 Note 1, and §2.2):
```diff
--- v3 (PLAN_NET-816_FAILFIX-R2_v3_AGCOS-V5_20261110.md)
+++ v3.1 (PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md)
@@ -1,7 +1,7 @@
-# PLAN: NET-816 Catalog Chunk 1 Fail-Fix Round 2 (v3.0)
+# PLAN: NET-816 Catalog Chunk 1 Fail-Fix Round 2 (v3.1)
 **Track:** NET-816 (Catalog Chunk 1 — Round 2 Fail-Fix Plan)  
 **Writer:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
-**Iteration:** R2 track attempt 3 of 10; writer AG CoS v5 try 3 of 4  
-**Date:** 10 November 2026 ~20:21 EST  
+**Iteration:** R2 track attempt 4 of 10; writer AG CoS v5 try 4 of 4  
+**Date:** 10 November 2026 ~21:20 EST  
@@ -18,4 +18,6 @@
-3. **D3 (−2 pts, Search Precision & Test Path):** Implements two-pass search logic (Pass 1 exact field substring match, Pass 2 whitespace multi-token match)...
-4. **D4 (−2 pts, Rollback & Safety Invariants):** Updates RT-A rollback to accept full 40-char SHA...
+3. **D3′ (Search Precision & Real Screen Test):** Implements list-level two-pass filtering across `_applyFilters()`...
+4. **D4′ (Runbook Readback & Safety Invariants):** Uses preview host prefix `https://numista-vault--p7-gate-` with strict regex...
+
+v3.1 Change Note: Narrow amendment from CoS 96 PASS, closing D3′ and D4′ exclusively. All other sections byte-identical to v3.
@@ -359,32 +361,85 @@
-#### Note 1: Two-Pass Search Algorithm ("1816" & "Morgan dollar 1881")
+#### Note 1: List-Level Two-Pass Search Algorithm (D3′)
... [List-level filtering implementation across _allEntries in catalog_browse_screen.dart:112-200]
... [Evidence from real dataset assets/catalog/catalog_public_v1.json: 1842 -> 1, Morgan -> 5, 1816 -> 0]
... [Automated verification via test/catalog_chunk1_face_value_and_card_test.dart with pumpLoadedCatalog]
@@ -437,3 +492,8 @@
-$repoRoot = (Get-Location).Path
-Set-Location $repoRoot
+$repoRoot = "C:\Users\ericd\Documents\MyVertexProject"
+Set-Location $repoRoot
+$topLevel = (git rev-parse --show-toplevel).Trim()
+if ($topLevel.Replace('/', '\') -ne $repoRoot) {
+    throw "FATAL: Repository root mismatch ($topLevel != $repoRoot)"
+}
+
+# 2.5 Pre-Deploy Live Channel Baseline Capture (D4′)
+Push-Location "$repoRoot\numista_mobile"
+$preDeployJsonRaw = firebase hosting:channel:list --project studio-9101802118-8c9a8 --json
... [Captures $preLiveReleaseTime; asserts exit code 0]
@@ -501,28 +561,45 @@
-    # 8. Post-Deploy Readback Verification (D4)
+    # 8. Post-Deploy Readback Verification (D4′)
... [Re-reads hosting:channel:list --json; asserts live releaseTime unchanged]
... [Validates p7-gate URL against ^https://numista-vault--p7-gate-[a-z0-9]+\.web\.app]
... [Throws unconditionally if URL missing, version.json mismatch, or HTTP status != 200]
```

---

## 4. Invariants & Authority Check
- **STRICTLY PLAN ONLY.** Zero code execution, zero source code commits, zero deployments, zero Firestore/Stripe writes.
- `origin/main` strictly pinned at `9f04550a`.
- HOLDs `74611e05` and `41b8bd5f` stand in full force.
- Handing off to Grok CoS / SAG for final review.
