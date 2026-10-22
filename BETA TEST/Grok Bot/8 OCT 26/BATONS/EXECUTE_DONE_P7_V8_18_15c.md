# EXECUTE DONE — P7 BUILD V8.18.15c

**Date:** 2026-10-22  
**Builder:** AG CoS P7 V8.9 Builder  
**Branch:** `p7-v8.9`  
**Commit SHA:** `46530318ea9969a1d174e75fff174e516c105a1c`  
**Base:** `c0965740` -> `184cd215` -> `46530318`  
**Push Destination:** `origin/p7-v8.9` (Verified pushed)

---

## 1. Summary of Changes

| Component | File | Lines | Description |
|-----------|------|-------|-------------|
| **NGC Test Copy** | `numista_mobile/test/p7_v8_ux_safety_test.dart` | 1958, 2898 | Updated test expectations to match exact copy: `"We can't look up NGC numbers automatically yet. Snap the label or type the details below."` |
| **Review Commit Flagging** | `numista_backend/main.py` | 3538, 3574-3575, 3632 | Track `flagged_count` for `possible_duplicate=True` and return `"flagged": flagged_count` in commit response. |
| **Review Snackbar Copy** | `numista_mobile/lib/screens/review_hub_screen.dart` | 24-52, 444-463, 497-516 | Implemented `ReviewHubScreen.formatCommitSnackbar` with clear plain-English copy for committed, skipped duplicate re-imports, and yellow-flagged possible duplicates. |
| **Snackbar Unit Test** | `numista_mobile/test/p7_v8_ux_safety_test.dart` | 3013-3039 | Added test covering all combinations of committed, skipped, and flagged snackbar messages. |
| **Split-Qty & Re-Import Tests** | `numista_backend/tests/test_req031_auth.py` | 290-360, 284 | Rewrote split invoice test; added true re-import duplicate skipped test; updated attribute test for `flagged == 1`. |

---

## 2. Verification & Test Results

- **Backend Pytest**: `607 passed, 0 failed` in 13.91s (`numista_backend/tests/`).
- **Frontend Flutter Test**: `619 passed, 0 failed` in 42s (all suites passing, including 96/96 in `p7_v8_ux_safety_test.dart`).
- **Frontend Analysis**: `0 errors, 0 warnings` (`flutter analyze lib/`).

---

## 3. Systemic Dupe Audit (Drop vs Flag Analysis)

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
commit 46530318ea9969a1d174e75fff174e516c105a1c
Author: Numista Deployer <deploy@numista.ai>
Date:   Thu Oct 22 16:03:49 2026 -0400

    fix(p7-v8.18.15c): NGC stale test fix, review flagged count and clear snackbar copy, split-qty & re-import tests, dupe audit

 numista_backend/main.py                           |  7 ++-
 numista_backend/tests/test_req031_auth.py         | 65 ++++++++++++++++++++++-
 numista_mobile/lib/screens/review_hub_screen.dart | 44 ++++++++++++---
 numista_mobile/test/p7_v8_ux_safety_test.dart     | 49 +++++++++++------
 4 files changed, 139 insertions(+), 26 deletions(-)
```
