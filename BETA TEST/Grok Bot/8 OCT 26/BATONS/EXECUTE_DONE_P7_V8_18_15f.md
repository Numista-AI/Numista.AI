# EXECUTE DONE: P7 BUILD V8.18.15f (Tests & Hygiene)

**Date:** 2026-10-22 ~22:45 ET  
**Author:** AG CoS  
**Order Reference:** NET-442 (`NET-442_GROKCOS-to-AGCOS_P7-V81815f-TESTS-HYGIENE_OVER.md`)  
**Branch:** `p7-v8.9`  
**Commit SHA:** `ba37c03e66feeb6fd4e56bb5f87fbee27375d0db` (Short: `ba37c03e`)  
**Base Commit:** `b3d63b781c1aab71937c6e188c7f25c1941a11a6`  
**Diff Base:** `1058fe8b554e5d8059cecf8ba6db0d9ef6c895a4`  
**Status:** COMPLETE & VERIFIED  

---

## 1. Deliverables Summary

Per NET-442 directives, this build contains **tests and hygiene only** (zero new product features, zero modifications to the duplicate key, zero duplicate prompt dialogs).

### A. Real Backend Regression Tests (`test_v8_18_15e_regression.py`)
- Completely replaced simulated inline mocks with a zero-copy production harness: `InMemoryFirestore`, `MockGCSClient`, and `MockGenAI`.
- All 5 tests drive real production routines directly:
  1. `test_invoice_092052_gemini_list_response_drives_real_worker`: Calls `_execute_import_process_worker` with Gemini returning a top-level JSON list for US Mint invoice 092052. Asserts receipt doc written with retailer, invoice number, and date; coin doc written to `review_queue`; session status `done`; `coins_identified == 1`.
  2. `test_ase_invoice_usm23339673_gemini_dict_with_existing_ase_worker_real`: Calls `_execute_import_process_worker` with Gemini returning a dict for USM23339673 where a 2026-W ASE already exists in Firestore. Asserts coin is not dropped, receipt doc written, and `possible_duplicate: True` is stamped.
  3. `test_worker_status_done_with_errors_when_one_file_raises`: Calls `_execute_import_process_worker` with 2 files where 1 raises during download. Asserts session doc status is `done_with_errors`.
  4. `test_all_4_add_paths_through_real_routes_flag_duplicates`: Directly invokes the real route/function handlers:
     - Path 1: `commit_reviews` (queue reviews)
     - Path 2: `identify_coin_photo` (scan-save)
     - Path 3: `cert_save` (cert lookup save)
     - Path 4: `commit_batch` (bulk spreadsheet import staging)
     Asserts `possible_duplicate: True` across all 4 and confirms zero records are deleted or dropped without being committed.
  5. `test_commit_reviews_argon_a4_invoice_empty_item_no_real`: Invokes real `commit_reviews` with 3 queue documents sharing an invoice number and having empty item numbers. Asserts all 3 commit and 0 are skipped.
- **Pytest Result:** 5/5 regression tests pass; full backend test suite: **617 passed, 258 warnings in 46.34s**.

### B. Flutter Measured-Height Widget Tests (`p7_v81815f_measured_height_test.dart`)
- Created 25 comprehensive widget and source-level tests running under `debugDefaultTargetPlatformOverride` for `TargetPlatform.windows`, `TargetPlatform.macOS`, and `TargetPlatform.linux`.
- **Root Cause Identified**: Flutter applies desktop visual density (`VisualDensity.compact`) on desktop platforms, which subtracts 8px from button minimum heights (`48 - 8 = 40.0px`).
- **Fixes Applied**:
  - `add_coins_hub.dart:3882`: NGC card 'Check this slab on ngccoin.com' wrapped in `SizedBox(height: 48)`, added `visualDensity: VisualDensity.standard`.
  - `add_coins_hub.dart:3956`: NGC card 'Cancel' wrapped in `SizedBox(height: 48)`, added `visualDensity: VisualDensity.standard`.
  - `add_coins_hub.dart:5521, 5533`: Photo page 'Take Photo' & 'Upload' wrapped in `SizedBox(height: 48)`, added `visualDensity: VisualDensity.standard`.
  - `base_layout.dart:958`: Sidebar 'Send Beta Feedback' added `visualDensity: VisualDensity.standard`.
  - `base_layout.dart:1033`: Sidebar 'Sign Out' added `visualDensity: VisualDensity.standard`.
- **Flutter Test Result:** 25/25 measured-height tests pass. Full suite: **645 passed, 0 failed in 1m 01s** (baseline 620). Flutter analyze: **0 issues found**.

### C. Hygiene & Line Endings
- Converted all 5 files (`main.dart`, `constants.dart`, `add_coins_hub.dart`, `my_collection_screen.dart`, `review_hub_screen.dart`) plus `base_layout.dart` from CRLF back to pure LF.
- Reverted uncommitted post-commit hook files (`RELEASE_NOTES.md`, `home_dashboard.dart`).
- `git diff 1058fe8b HEAD --stat` shows strictly real line counts only (CRLF noise eliminated).
- Bumped `pubspec.yaml` to `8.18.15+81816` and `constants.dart` `kAppVersion` to `v8.18.15f`.

---

## 2. Baseline Comparison with `origin/main`

Running the regression scenarios against `origin/main` confirms the bugs were live in production and are resolved on `p7-v8.9`:

| Scenario | `origin/main` Baseline Behavior | `p7-v8.9` Fixed Behavior (`ba37c03e`) |
|---|---|---|
| **1. Invoice Top-Level List (092052)** | Crashed with `AttributeError: 'list' object has no attribute 'get'` at `main.py:7938` (`hdr = data`). Session left stuck in `processing`. | `hdr` extracted safely from dict or first list item. Receipt doc written, coin doc written to `review_queue`, status `done`. |
| **2. Receipt Document Write** | Receipt document write was separate from coin writes and subject to unhandled local variable errors if totals extraction failed. | Atomically written in the same Firestore batch write as coin documents with retailer, invoice number, and date. |
| **3. Partial File Errors** | Session status unconditionally updated to `"done"` at end of loop even when individual files failed. | `any_errors` logic detects failed files and marks session `done_with_errors`. Red banner shown in UI. |
| **4. Duplicate Detection (Path 1: Reviews)** | Review queue deleted duplicate coins without committing (`skipped_count += 1`), causing coins to vanish. | Duplicate coins are committed with `possible_duplicate: True` and never deleted. SnackBar alerts user. |
| **5. Duplicate Detection (Paths 2, 3, 4)** | `identify_coin_photo`, `cert_save`, and `commit_batch` had NO duplicate checking logic whatsoever. | All 3 paths call shared `check_and_flag_duplicate` and stamp `possible_duplicate: True`. |

---

## 3. Test Counts & Verification

- **Full Pytest Suite**: `617 passed, 258 warnings in 46.34s`
- **Full Flutter Test Suite**: `645 passed, 0 failed in 1m 01s` (Required: >620)
- **Flutter Analyze**: `No issues found! (ran in 27.6s)`
- **GEMINI38 Review**: `PASS` (filed in `BATONS\GEMINI38_REVIEW_P7_V8_18_15f_BUILD.md`)
- **Git Push**: Confirmed pushed to `origin/p7-v8.9` under commit `ba37c03e`.

---

## 4. Git Diff Summary (`1058fe8b` to `HEAD`)

```
 numista_backend/main.py                            |  85 ++-
 numista_backend/routes/cert_routes.py              |  15 +
 numista_backend/routes/import_routes.py            |   3 +
 numista_backend/services/duplicate_check.py        |  87 +++
 numista_backend/tests/test_v8_18_15e_regression.py | 680 +++++++++++++++++++++
 numista_mobile/lib/constants.dart                  |   2 +-
 numista_mobile/lib/main.dart                       |   2 +
 numista_mobile/lib/screens/add_coins_hub.dart      | 121 +++-
 numista_mobile/lib/screens/base_layout.dart        |   2 +
 numista_mobile/lib/screens/my_collection_screen.dart|   2 +-
 numista_mobile/lib/screens/review_hub_screen.dart  | 129 ++--
 numista_mobile/pubspec.yaml                        |   2 +-
 numista_mobile/test/p7_v81815f_measured_height_test.dart | 401 ++++++++++++
 numista_mobile/web/add_coins.html                  |  31 +-
 14 files changed, 1442 insertions(+), 120 deletions(-)
```
All mobile files show real line counts only (zero line-ending inflation).
