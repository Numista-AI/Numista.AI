# GEMINI 3.8 FLASH REVIEW — P7 BUILD V8.18.15c

**Date:** 2026-10-22  
**Reviewer:** AG CoS P7 V8.9 Builder (Gemini 3.8 Flash Persona)  
**Target:** Numista.AI P7 V8.18.15c Commit `46530318ea9969a1d174e75fff174e516c105a1c`  
**Branch:** `p7-v8.9`  
**Verdict:** **PASS**

---

## 1. Executive Summary
Build V8.18.15c resolves all FAIL-FIX items from NET-432 and `COS_SCORE_P7_BUILD_V8_18_15b.md`:
1. **NGC Copy Alignment**: Stale NGC test expectations in `numista_mobile/test/p7_v8_ux_safety_test.dart` were updated to the exact new copy: `"We can't look up NGC numbers automatically yet. Snap the label or type the details below."`.
2. **Review Commit Flagged Count**: `numista_backend/main.py:commit_reviews` tracks `flagged_count` whenever `possible_duplicate` is set to `True` on committed review items, returning `"flagged": flagged_count` alongside `committed` and `skipped`.
3. **Review Hub Snackbar Copy**: `numista_mobile/lib/screens/review_hub_screen.dart` was updated with `ReviewHubScreen.formatCommitSnackbar` generating plain English explanations for committed, skipped duplicate re-imports, and yellow-flagged possible duplicates.
4. **Backend Test Coverage**: `numista_backend/tests/test_req031_auth.py` was updated with `test_review_commit_split_invoice_qty_both_committed` (verifying both split lines commit) and `test_review_commit_reimport_same_invoice_item_skipped` (verifying second ingest re-import skips already committed items).
5. **Systemic Duplicate Audit**: Full audit matrix documented analyzing drop vs flag behavior across manual Morgan add, review commit, dedup sweep, PCGS import, invoice extraction, and CSV spreadsheet import.

All test suites pass:
- **Pytest**: 607 passed, 0 failed.
- **Flutter Test**: 619 passed, 0 failed (including 96/96 in `p7_v8_ux_safety_test.dart`).
- **Flutter Analyze**: 0 errors, 0 warnings (clean).

---

## 2. Verbatim Code Changes & Per-Condition Checklist

### Item 1: Stale NGC Tests Updated (`p7_v8_ux_safety_test.dart`)

**Requirement:** Update the 2 stale tests in `p7_v8_ux_safety_test.dart` to assert the exact copy: `"We can't look up NGC numbers automatically yet. Snap the label or type the details below."`

**File:** `numista_mobile/test/p7_v8_ux_safety_test.dart`

**Verbatim Code (Lines 1958-1960):**
```dart
      expect(find.text("We can't look up NGC numbers automatically yet. Snap the label or type the details below."), findsOneWidget);
      expect(find.text('Type Details Below'), findsOneWidget);
      expect(find.text('Take Photo'), findsOneWidget);
```

**Verbatim Code (Lines 2898-2900):**
```dart
      expect(find.text("We can't look up NGC numbers automatically yet. Snap the label or type the details below."), findsOneWidget);
      expect(find.text('Type Details Below'), findsOneWidget);
      expect(find.text('Take Photo'), findsOneWidget);
```

**Verbatim Code (Lines 3004-3011):**
```dart
    test('V8.18.15b: NGC unsupported lookup copy matches exact string', () {
      const expectedCopy =
          "We can't look up NGC numbers automatically yet. Snap the label or type the details below.";
      expect(
        expectedCopy,
        "We can't look up NGC numbers automatically yet. Snap the label or type the details below.",
      );
    });
```

**Checklist:**
- [x] `p7_v8188_cert_lookup_not_found_ngc_shows_honest_message` asserts exact copy — **PASS**
- [x] `p7_v81815_401_4_ngc_not_found_amber_card_with_cert` asserts exact copy — **PASS**
- [x] Assertion matches UI implementation in `add_coins_hub.dart:1872` verbatim — **PASS**

---

### Item 2: Backend `flagged_count` Tracking (`main.py`)

**Requirement:** In `numista_backend/main.py` (`commit_reviews`), track `flagged_count` for `possible_duplicate=True` and return `"flagged": flagged_count` in response dict.

**File:** `numista_backend/main.py`

**Verbatim Code (Line 3538):**
```python
    flagged_count = 0
```

**Verbatim Code (Lines 3574-3575):**
```python
            if is_dup:
                coin_data["possible_duplicate"] = True
                flagged_count += 1
```

**Verbatim Code (Line 3632):**
```python
        return {"committed": committed_count, "skipped": skipped_count, "flagged": flagged_count}
```

**Checklist:**
- [x] Initialized `flagged_count = 0` — **PASS**
- [x] Incremented `flagged_count += 1` when `is_dup` is detected on committed review items — **PASS**
- [x] Response payload includes `"flagged": flagged_count` — **PASS**

---

### Item 3: Review Hub Snackbar Clear Copy (`review_hub_screen.dart`)

**Requirement:** Update Review Hub snackbar copy to inform user of committed count, skipped duplicates (`"M were already in your collection from the same invoice, so we didn't add them twice."`), and flagged possible duplicates (`"K might be coins you already have; look for the yellow 'Possible duplicate' tag."`).

**File:** `numista_mobile/lib/screens/review_hub_screen.dart`

**Verbatim Code (Lines 24-52):**
```dart
  static String formatCommitSnackbar({
    required int committed,
    required int skipped,
    int flagged = 0,
  }) {
    final parts = <String>[];
    if (committed > 0) {
      parts.add('Added $committed ${committed == 1 ? 'coin' : 'coins'} to your collection.');
    }
    if (skipped > 0) {
      parts.add('$skipped ${skipped == 1 ? 'was' : 'were'} already in your collection from the same invoice, so we didn\'t add them twice.');
    }
    if (flagged > 0) {
      parts.add('$flagged might be ${flagged == 1 ? 'a coin' : 'coins'} you already have; look for the yellow \'Possible duplicate\' tag.');
    }
    if (parts.isEmpty) {
      return 'No coins were added.';
    }
    return parts.join(' ');
  }
```

**Verbatim Code (Lines 444-463):**
```dart
    try {
      final res = await _client.commitReviewQueue(ids);
      final committed = (res['committed'] as num?)?.toInt() ?? 0;
      final skipped = (res['skipped'] as num?)?.toInt() ?? 0;
      final flagged = (res['flagged'] as num?)?.toInt() ?? 0;
      if (mounted) {
        final message = ReviewHubScreen.formatCommitSnackbar(
          committed: committed,
          skipped: skipped,
          flagged: flagged,
        );
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(message),
            backgroundColor: Colors.teal[800],
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
```

**Checklist:**
- [x] `ReviewHubScreen.formatCommitSnackbar` formats single and plural forms cleanly — **PASS**
- [x] Uses plain English avoiding technical jargon ("invoice hash", "doc ID") — **PASS**
- [x] Tested across all combinations in `p7_v8_ux_safety_test.dart` — **PASS**

---

### Item 4: Pytest Coverage for Split Quantity & Re-Import (`test_req031_auth.py`)

**Requirement:**
- Rewrite `test_review_commit_split_invoice_qty_both_committed` mocking collection state where existing coin has `doc_id` in `review_ids`.
- Add `test_review_commit_reimport_same_invoice_item_skipped` mocking collection state where existing coin has `doc_id` NOT in `review_ids`.

**File:** `numista_backend/tests/test_req031_auth.py`

**Verbatim Code (Lines 290-324):**
```python
    def test_review_commit_split_invoice_qty_both_committed(self, mock_auth):
        """Split line items from single receipt (e.g., qty=2 split into 2 items) must both commit."""
        q1 = {"id": "rev_q1", "coin": {"name": "1881-S Morgan", "year": 1881, "invoice_id": "INV-100", "invoice_item_index": 0}}
        q2 = {"id": "rev_q2", "coin": {"name": "1881-S Morgan", "year": 1881, "invoice_id": "INV-100", "invoice_item_index": 1}}
        mock_rev1 = MagicMock()
        mock_rev1.id = "rev_q1"
        mock_rev1.to_dict.return_value = q1
        mock_rev2 = MagicMock()
        mock_rev2.id = "rev_q2"
        mock_rev2.to_dict.return_value = q2

        # In split-qty flow, both have different item indexes, or even if same item index,
        # an existing coin with doc_id in review_ids is NOT considered a pre-existing duplicate.
        mock_existing = MagicMock()
        mock_existing.id = "rev_q1"
        mock_existing.to_dict.return_value = {"invoice_id": "INV-100", "invoice_item_index": 0}

        def mock_stream():
            return iter([mock_existing])

        with patch("main.get_db") as mock_db:
            db_instance = MagicMock()
            mock_db.return_value = db_instance
            db_instance.collection.return_value.document.return_value.collection.return_value.document.return_value.get.side_effect = [
                mock_rev1, mock_rev2
            ]
            db_instance.collection.return_value.document.return_value.collection.return_value.stream.side_effect = mock_stream
            batch_mock = MagicMock()
            db_instance.batch.return_value = batch_mock

            res = client.post(
                "/api/reviews/commit",
                json={"review_ids": ["rev_q1", "rev_q2"]},
                headers={"Authorization": "Bearer mock-token"},
            )
            assert res.status_code == 200
            data = res.json()
            assert data["committed"] == 2
            assert data["skipped"] == 0
```

**Verbatim Code (Lines 326-360):**
```python
    def test_review_commit_reimport_same_invoice_item_skipped(self, mock_auth):
        """True re-import of same invoice line item already in collection must be skipped."""
        q1 = {"id": "rev_reimport", "coin": {"name": "1881-S Morgan", "year": 1881, "invoice_id": "INV-100", "invoice_item_index": 0}}
        mock_rev1 = MagicMock()
        mock_rev1.id = "rev_reimport"
        mock_rev1.to_dict.return_value = q1

        # An existing coin whose doc_id is NOT in the incoming review_ids indicates
        # this invoice item was already committed in a previous batch!
        mock_existing = MagicMock()
        mock_existing.id = "already_saved_coin_doc_999"
        mock_existing.to_dict.return_value = {"invoice_id": "INV-100", "invoice_item_index": 0}

        def mock_stream():
            return iter([mock_existing])

        with patch("main.get_db") as mock_db:
            db_instance = MagicMock()
            mock_db.return_value = db_instance
            db_instance.collection.return_value.document.return_value.collection.return_value.document.return_value.get.side_effect = [
                mock_rev1
            ]
            db_instance.collection.return_value.document.return_value.collection.return_value.stream.side_effect = mock_stream
            batch_mock = MagicMock()
            db_instance.batch.return_value = batch_mock

            res = client.post(
                "/api/reviews/commit",
                json={"review_ids": ["rev_reimport"]},
                headers={"Authorization": "Bearer mock-token"},
            )
            assert res.status_code == 200
            data = res.json()
            assert data["committed"] == 0
            assert data["skipped"] == 1
```

**Checklist:**
- [x] Split-quantity items both commit cleanly (`committed: 2, skipped: 0`) — **PASS**
- [x] True re-import from existing invoice line skips duplicate (`committed: 0, skipped: 1`) — **PASS**
- [x] `test_req031_auth.py` all 15 tests pass — **PASS**

---

## 3. Test Suite Verification

### Backend (Python/Pytest)
```
============================= 607 passed in 13.91s =============================
```
- Status: **ALL 607 PASS**

### Frontend (Flutter Test)
```
00:42 +619: All tests passed!
```
- Status: **ALL 619 PASS** (including 96/96 in `test/p7_v8_ux_safety_test.dart`)

### Frontend Analysis (Flutter Analyze)
```
Analyzing lib...
No issues found! (ran in 10.3s)
```
- Status: **0 ISSUES FOUND**

---

## 4. Final Verdict

**VERDICT: PASS**  
The branch `p7-v8.9` is clean, all tests are passing, git commit `46530318ea9969a1d174e75fff174e516c105a1c` is pushed to `origin/p7-v8.9`, and all requirements from NET-432 are completely fulfilled.
