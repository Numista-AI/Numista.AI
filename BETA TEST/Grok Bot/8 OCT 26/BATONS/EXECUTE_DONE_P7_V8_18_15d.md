# EXECUTE DONE — P7 BUILD V8.18.15d

**Date:** 2026-10-22  
**Builder:** AG CoS P7 V8.9 Builder  
**Branch:** `p7-v8.9`  
**Commit SHA:** `1058fe8b554e5d8059cecf8ba6db0d9ef6c895a4` (Short SHA: `1058fe8b`)  
**Base Commit:** `46530318ea9969a1d174e75fff174e516c105a1c` (`46530318`)  
**Push Destination:** `origin/p7-v8.9` (Verified pushed)  

---

## 1. Summary of Changes

| Component | File | Lines | Description |
|-----------|------|-------|-------------|
| **Singular Skipped Copy** | `numista_mobile/lib/screens/review_hub_screen.dart` | 27-31 | When `skipped == 1`, copy explicitly states `"1 was already in your collection from the same invoice, so we didn't add it twice."` (replacing `"them"` with `"it"`). When `skipped > 1`, states `"$skipped were already in your collection from the same invoice, so we didn't add them twice."`. |
| **Response Parsing Helper** | `numista_mobile/lib/screens/review_hub_screen.dart` | 44-71 | Added static helper `ReviewHubScreen.snackbarFromCommitResponse(String responseBody, int fallbackCommitted)` parsing `committed`, `skipped`, and `flagged` with graceful fallbacks for malformed JSON, missing fields, or empty strings. |
| **Wired Commit Call Sites** | `numista_mobile/lib/screens/review_hub_screen.dart` | 113-116, 179-182 | Replaced duplicate JSON decoding logic in `_commitSelected` and `_commitHighConfidence` with single source of truth `snackbarFromCommitResponse`. |
| **Singular Copy Assertions** | `numista_mobile/test/p7_v8_ux_safety_test.dart` | 3104, 3116, 3120 | Updated test assertions to enforce singular copy `"didn't add it twice."` for `skipped == 1`. |
| **Response Parsing Tests** | `numista_mobile/test/p7_v8_ux_safety_test.dart` | 3124-3160 | Added comprehensive unit tests covering: (1) normal response with committed, skipped, and flagged, (2) missing flagged parameter (defaulting to 0), (3) malformed JSON body falling back to `fallbackCommitted`, (4) empty string body falling back cleanly. |
| **Split-Qty Mock Reference Fix** | `numista_backend/tests/test_req031_auth.py` | 284-290 | In `test_review_commit_split_invoice_qty_both_committed`, created explicit mock doc references `mock_ref1` and `mock_ref2` whose `.get.return_value` returns `mock_doc1` and `mock_doc2`, ensuring `mock_queue_col.document.side_effect` returns a reference whose `.get()` yields the expected document fixture. |

---

## 2. Verification & Test Results

- **Backend Pytest**: `607 passed, 258 warnings` in 37.00s (`python -m pytest numista_backend/tests -q` executed from worktree root `C:\Users\ericd\AppData\Local\Temp\p7v89_build`).
- **Frontend Flutter Test**: `620 passed, 0 failed` in 57s (`flutter test --reporter compact` executed from `numista_mobile/`, baseline 619 + 1 new test).
- **Frontend Analysis**: `0 errors, 0 warnings` (`flutter analyze lib/` executed from `numista_mobile/`: "No issues found!").

---

## 3. Systemic Dupe Audit (Drop vs Flag Confirmation)

| Code Site / Entry Point | File & Lines | Detection Trigger / Mechanism | Drop or Flag? | Rationale / Behavior |
|-------------------------|--------------|-------------------------------|---------------|----------------------|
| **Manual Add / Morgan Greeter** | `numista_backend/main.py:2700-2715` | Matches existing coin by `(year, mint_mark, denomination)` in user's collection. | **FLAG** (Never drops) | Sets `is_duplicate = True` in response JSON, but **writes document anyway** (`new_doc_ref.set(coin_data)`). User may legitimately own multiple specimens of the same year/mint/denomination. |
| **Review Queue Commit** | `numista_backend/main.py:3545-3575` | 1. **Definite Re-import:** Same `(invoice_id, invoice_item_index)` already exists in collection and existing doc ID is NOT in the current commit batch.<br>2. **Possible Specimen:** Matches `(year, mint_mark, denomination)` of an existing collection item. | **DROP (1)** / **FLAG (2)** | 1. **DROPPED from queue without committing (`skipped`)**: A re-import of the exact same receipt item should not duplicate coins already imported.<br>2. **COMMITTED with Flag (`possible_duplicate = True`, `flagged`)**: Preserves user's coins while surfacing the yellow badge. |
| **Dedup Sweep & Auto-Clean** | `numista_backend/main.py:3885-4015` | 1. `invoice_groups`: exact match on `(invoice_id, invoice_item_index)`.<br>2. `attribute_groups`: exact match on `(year, mint_mark, denom, grade, cert, created_at)`.<br>3. `cross_date_groups`: match on attributes across different dates. | **DROP (1 & 2)** / **FLAG ONLY (3)** | `dedup_auto_clean` only deletes secondary records in definite duplicate groups (1 & 2). It **never deletes** cross-date groups (3), leaving them for manual user review. |
| **PCGS Bulk / Cert Import** | `numista_mobile/lib/screens/add_coins_hub.dart:4724`<br>`pcgs_import_service.dart:185-195` | Matches existing coin in collection where `Certification Number == cert`. | **DROP (Skipped)** | Slab certification numbers are globally unique. If a slab cert is already in the collection, importing it again is rejected and reported as `"Duplicates Skipped: N"`. |
| **Invoice / Receipt Extraction** | `numista_backend/main.py:2431-2550` | Receipt OCR parsing into individual items or proof sets. | **NO DROP** (Stages all) | OCR parses all invoice items into `review_queue` as uncommitted items. No deduplication or dropping occurs at OCR ingest time; dedup is deferred to user review and commit. |
| **Spreadsheet / CSV Import** | `numista_backend/import_routes.py:330-410` | Matches existing row by cert number or `(year, mint, denom)`. Flags: `exact_duplicate`, `intra_batch_duplicate`, `potential_duplicate`. | **CONDITIONAL DROP** | Rows are staged with flags. On `commit_batch`, rows are only skipped if `dedup == 'exact_duplicate'` AND `conflict_policy == 'keep_existing'`. If policy is overwrite or append, coin is processed accordingly. |

---

## 4. Git Commit Details

```
commit 1058fe8b554e5d8059cecf8ba6db0d9ef6c895a4
Author: Numista Deployer <deploy@numista.ai>
Date:   Thu Oct 22 17:10:20 2026 -0400

    fix(p7-v8.18.15d): singular skipped copy, snackbarFromCommitResponse helper and tests, split-qty doc mock

 numista_backend/tests/test_req031_auth.py         |  7 +++-
 numista_mobile/lib/screens/review_hub_screen.dart | 66 +++++++++++++-------------------
 numista_mobile/test/p7_v8_ux_safety_test.dart     | 52 +++++++++++++++++++++++---
 3 files changed, 87 insertions(+), 38 deletions(-)
```
