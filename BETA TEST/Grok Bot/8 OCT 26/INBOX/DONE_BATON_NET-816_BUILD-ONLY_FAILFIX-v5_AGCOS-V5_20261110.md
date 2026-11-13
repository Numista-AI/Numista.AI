# DONE — BATON NET-816 BUILD-ONLY FAIL-FIX v5 (NO DEPLOY) (AG CoS v5)
Filed: 2026-11-10 16:48 EST by AG CoS v5 (cfe23a7a-d721-44f9-b9d5-d2b74602b687).
In response to: BATON_NET-816_AGCOS-V5_BUILD-ONLY_FAILFIX-v5_NO-DEPLOY_20261110-1624.md
Authority: Founder Eric's typed 'OK. Go' (t2507u, 4:23 PM ET) for preview build job only; CoS 100 PASS (19a799c...), SAG 97 PASS (347743f2...).

---

## 1. Built Fix Commit & Branch Verification
* **Built Fix Commit SHA:** 3d7dca20fbbaf06a522205b22d0740b600de52b (short: 3d7dca2)
* **Branch:** p7-v8.9 (pushed cleanly to origin/p7-v8.9, git commit range 7fe4fae8..a3d7dca2).
* **Commit Message:** ix(catalog): add /catalog rewrites and correct half-dime melt value (NET-816 A1/A2)
* **File Scope (Strictly 3 Files Modified, No Other Files):**
  1. 
umista_mobile/firebase.json (lines 73–80: added /catalog and /catalog/** rewrites to /index.html)
  2. 
umista_mobile/lib/services/melt_value_service.dart (added half dime to _ag90, updated _matchDenom for .05, war nickel logic, and closed Morgan inflation fallback)
  3. 
umista_mobile/test/catalog_chunk1_face_value_and_card_test.dart (added comprehensive A2/D1-D3/N2/N4 regression suite covering tests (a)–(e))
* **Workspace Isolation:** Built, verified, and committed in an isolated temporary worktree outside the shared repo (C:\Users\ericd\AppData\Local\Temp\p7gate_build_net816). Never checked out old commits in MyVertexProject.

---

## 2. Machine-Checkable Verification Outputs

### 2.1 Firebase Rewrites Verification
`
python -c "import json; d = json.load(open('firebase.json')); rewrites = [r.get('source') for r in d['hosting']['rewrites']]; assert '/catalog' in rewrites, 'missing /catalog'; assert '/catalog/**' in rewrites, 'missing /catalog/**'; print('firebase.json rewrites VERIFIED')"
`
**Output:** irebase.json rewrites VERIFIED (Exit Code 0).

### 2.2 Dart Static Analysis
`
flutter analyze lib/services/melt_value_service.dart test/catalog_chunk1_face_value_and_card_test.dart
`
**Output:** Analyzing 2 items... No issues found! (ran in 2.6s) (Exit Code 0).

### 2.3 Full Test Suite Execution
`
flutter test test/catalog_chunk1_face_value_and_card_test.dart
`
**Output:**
* NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1 & NET-837 #2/#4/#5) parses previously mis-valued catalog denominations, canonical names, sets, and planchets [PASS]
* NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1 & NET-837 #2/#4/#5) full catalog_public_v1.json check: 0 mis-parses across all 3,202 entries, 66 non-null strings, and 71 (type, denomination) pairs [PASS]
* NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1 & NET-837 #2/#4/#5) caller blast-radius regression: header_stats_bar.dart:108 qty-weighted usdFaceSum & MeltValueService.compute [PASS]
* NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1 & NET-837 #2/#4/#5) NET-816 Fail-Fix A2 & D1-D3/N2/N4 regression: half dime, war nickel, sub-dollar silver, and Morgan dollars [PASS]
* NET-816 Chunk 1 — _CatalogCard Widget Tests (#2 & NET-837 #3/#6) shows "type photo (date may differ)" when isTypeImage is true and renders parsed face value + honest non-promissory chip [PASS]
* NET-816 Chunk 1 — _CatalogCard Widget Tests (#2 & NET-837 #3/#6) medal cards display "No face value" and omit face-value chip [PASS]
* **Result:** All tests passed! (Exit Code 0).

### 2.4 FT-4 Filtered Half Dime Test
`
flutter test test/catalog_chunk1_face_value_and_card_test.dart --plain-name "half dime"
`
**Output:**
* NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1 & NET-837 #2/#4/#5) NET-816 Fail-Fix A2 & D1-D3/N2/N4 regression: half dime, war nickel, sub-dollar silver, and Morgan dollars [PASS]
* **Result:** All tests passed! (Exit Code 0).
* **Assertions Confirmed:** Half dime variants compute to 0.03617 oz * \ = \.0851 (formatted \.09), never \.20. War nickel computes to 0.05626 oz * \ = \.6878. Generic/unlisted sub-dollar silver returns null. Morgan fallback preserved for Morgan/Peace dollar series.

### 2.5 Stated FT-4 Gaps (§5.1)
1. FT-4 is a local unit-level A2 proof on typed-in literal strings. It does not read ssets/catalog/catalog_public_v1.json or the real 1853 row (NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2).
2. The preview visual dashboard check on a half dime is **DEFERRED / NOT VERIFIED ON PREVIEW** (enforcing zero live Firestore writes; no demo half dime exists).

---

## 3. Pre-Deploy Record of Hosting Channel p7-gate (§7.2)
* **Command:** irebase hosting:channel:list --project studio-9101802118-8c9a8
* **Output:**
  `
  Channels for site studio-9101802118-8c9a8
  Channel ID: live | Last Release Time: 2026-06-24 20:10:45 | URL: https://studio-9101802118-8c9a8.web.app | Expire Time: never
  `
* **Channel Status:** Channel p7-gate does **NOT exist** currently on Firebase Hosting.
* **Rollback Target Determination (§7.2):**
  - **RT-B: No redeploy** (channel did not exist / nothing to restore).
  - c547b7a0 is **NEVER deployed**.

---

## 4. Hard Stops & Invariants Maintained
* **NO DEPLOY EXECUTED:** Zero Firebase Hosting deploy commands run (stopped after Step 4 per baton instructions).
* **NO MAIN TOUCHED:** origin/main strictly pinned at 9f04550a. Zero commits or pushes to main.
* **NO FIRESTORE / NO STRIPE:** Live database and live payment services remain completely untouched.
* **HOLDS ACTIVE:**
  - HOLD 74611e05e00a99e4dfb5f524f16a7dc92d540265986ff138c61ccf5884f11b6b in force.
  - Stop-rule HOLD 41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d in force.
  - Go-live addendum SHA c2b6ac93... stays **NOT ACTIVE**.

---

## 5. Next Steps for CoS
* **Action:** CoS may now present Founder Eric with the scoped preview deploy YES request naming built commit 3d7dca20fbbaf06a522205b22d0740b600de52b and rollback target **RT-B: No redeploy**.
