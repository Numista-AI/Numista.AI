# Calibration Review — Invoice/Receipt Import Duplicate Fix

### 1. Attribute fallback unconditionally deletes distinct coins sharing Year, Mint, and Denomination
- **File**: `numista_backend/main.py` (lines 3534, 3540–3545, 3549–3550)
- **Exact Quote**:
  ```python
  if not is_dupe:
  ```
  ```python
  q2 = coins_ref \
      .where('Year',      '==', data.get('Year', '')) \
      .where('Mint Mark', '==', data.get('Mint Mark', '')) \
      .where('Denomination', 'in', denom_variants[:10]) \
      .limit(1).get()
  is_dupe = len(q2) > 0
  ```
  ```python
  if is_dupe:
      batch.delete(queue_ref.document(doc_id))
  ```
- **What goes wrong**: Despite line 3476 stating *"A coin is only a true duplicate if Year, Mint, Denom, Invoice#, and Item# ALL match,"* `if not is_dupe:` runs a fallback check on **only** `Year`, `Mint Mark`, and `Denomination` (even when `Retailer Invoice #` differs) and permanently deletes (`batch.delete`) the staged coin if the user already owns any coin with those three attributes (e.g., a second 1921 Morgan Dollar in a different grade, or two different 2022-P quarters).
- **One-sentence fix**: Remove the attribute-only fallback from auto-deletion, or require `Program/Series`, `Theme/Subject`, `Condition`, `Certification Number`, and `Retailer Invoice #` to match before skipping.
- **For a 70-year-old collector**: If you already own one 1921 Morgan Dollar or one 2022-P quarter, the app assumes any new coin with the same year, mint mark, and denomination is an accidental duplicate and throws the new coin in the trash without asking you.

---

### 2. Missing `Retailer Item No.` deletes every coin after the first on the same invoice
- **File**: `numista_backend/main.py` (lines 3524–3530)
- **Exact Quote**:
  ```python
  if inv_no:
      try:
          q = coins_ref \
              .where('Retailer Invoice #', '==', inv_no) \
              .where('Retailer Item No.',  '==', item_no) \
              .limit(1).get()
          is_dupe = len(q) > 0
  ```
- **What goes wrong**: Because line 3524 checks `if inv_no:` instead of `if inv_no and item_no:`, any invoice without item numbers sets `item_no = ''`; once one coin from that invoice is in `coins` with an empty item number, every subsequent coin from the same invoice matches `(inv_no, '')` and is silently deleted.
- **One-sentence fix**: Change `if inv_no:` to `if inv_no and item_no:` so the invoice duplicate query only runs when both invoice number and item number are present.
- **For a 70-year-old collector**: When a receipt has an invoice number but no item SKU numbers, saving your first coin from that receipt causes the system to mistake all the other coins on that receipt for the first one and delete them.

---

### 3. UI ignores backend `committed`/`skipped` counts and shows a false success message
- **File**: `numista_mobile/lib/screens/review_hub_screen.dart` (lines 57, 119, 1066)
- **Exact Quote**:
  ```dart
  SnackBar(content: Text('Successfully committed ${_selectedIds.length} items!')),
  ```
  ```dart
  content: Text('✅ Successfully committed ${highConfIds.length} items with 100% AI Confidence!'),
  ```
  ```dart
  const SnackBar(content: Text('Coin saved and committed to collection!')),
  ```
- **What goes wrong**: All three commit flows ignore the backend response payload (`committed` and `skipped` counts) and report that all selected coins were added, even when the backend skipped and deleted them as duplicates.
- **One-sentence fix**: Decode `response.body` in all three commit handlers and display the actual `committed` and `skipped` counts returned by `/api/review/commit`.
- **For a 70-year-old collector**: Even when the system quietly skips and deletes your coins as duplicates, the green message at the bottom still tells you that every single coin was safely added to your collection.

---

### 4. "100% AI Confidence" button count mismatches its commit filter
- **File**: `numista_mobile/lib/screens/review_hub_screen.dart` (lines 1250 and 89)
- **Exact Quote**:
  ```dart
  return conf >= 0.999;
  ```
  ```dart
  return conf >= 0.95;
  ```
- **What goes wrong**: The AppBar button badge counts items with `conf >= 0.999` (including quarantined items), while pressing it runs `_commitHighConfidence` which commits non-quarantined items with `conf >= 0.95`, mis-counting eligible items and sweeping in 95%–99% confidence coins.
- **One-sentence fix**: Use a single shared filter predicate (`conf >= 0.999` and not quarantined/`review_needed`) for both the AppBar badge count and `_commitHighConfidence`.
- **For a 70-year-old collector**: The "100% AI Confidence" button counts only 100%-certain coins on its label, but pressing it secretly sweeps in 95%-certain coins you haven't checked yet (or skips quarantined coins it counted).

---

### 5. Clearing a field in "Edit Coin" leaves the old value in Firestore
- **File**: `numista_mobile/lib/screens/review_hub_screen.dart` (lines 960–962 and 1022–1024)
- **Exact Quote**:
  ```dart
  controllers.forEach((key, ctrl) {
    if (ctrl.text.isNotEmpty) updates[key] = ctrl.text;
  });
  ```
- **What goes wrong**: If a user clears a misread `Mint Mark`, `Retailer Invoice #`, or `Retailer Item No.` in the edit dialog, `if (ctrl.text.isNotEmpty)` skips the empty field so the stale value remains in Firestore and can trigger a false duplicate deletion on commit.
- **One-sentence fix**: Assign `updates[key] = ctrl.text.trim();` unconditionally in both `Save` and `Save & Commit` so cleared fields overwrite stale Firestore values with an empty string.
- **For a 70-year-old collector**: If the scanner misreads a mint mark or invoice number and you erase that box in the Edit window, the app ignores your erasure and keeps the wrong old text, which can cause your coin to be deleted as a duplicate.
