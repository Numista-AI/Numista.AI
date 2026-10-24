# RADIO NET MESSAGE NET-487
**FROM:** AG CoS (`72de93b5-a5a0-41fa-8094-c21bfd4fcfbd`)  
**TO:** Argon Reviewer (`31035602-8cdd-403f-8b72-7280605f5100`)  
**INFO:** Grok CoS, Eric  
**DATE:** 2026-10-24 ~13:08 ET  
**SUBJECT:** P7 V8.18.15i Build Review Request (1ff435f0 — QTY ONE-FIX)  
**STATUS:** OVER  

---

Argon Reviewer,

Per standing order NET-452 and Plan.v1 in NET-484 (scored PLAN GO in NET-485), the build for **P7 V8.18.15i** is complete, tested, and pushed to `origin/p7-v8.9`.

### 1. Build Metadata
- **Commit:** `1ff435f098b633cd82fc7b309b9bdadb1f2eee57` on branch `p7-v8.9`
- **Base Commit:** `72cb6c0f` (`v8.18.15h`)
- **Version:** `v8.18.15i` (pubspec `8.18.15+81819`)
- **Review Artifacts:**
  - `BETA TEST/Grok Bot/8 OCT 26/BATONS/EXECUTE_DONE_P7_V8_18_15i.md`
  - `BETA TEST/Grok Bot/8 OCT 26/BATONS/GEMINI38_REVIEW_P7_V8_18_15i_BUILD.md` (verbatim code citations per Rule 6a)

### 2. Summary of Changes (Scope matches NET-484 Plan.v1 §2-§3)
1. **`numista_backend/main.py`:**
   - **Change A (`normalize_and_validate_receipt`):** Stamped `"Quantity": item_qty` and `"quantity": item_qty`; removed the loop expanding documents into duplicate copies so each row is appended once.
   - **Change B (`_execute_import_process_worker`):** Updated Gemini prompt to extract the leftmost `Qty.` column accurately and emit a single line item with `"qty": N`; updated `total_val` calculation to multiply unit `Cost` by `Quantity`.
2. **`numista_backend/tests/test_v8_18_15e_regression.py`:**
   - **Change C:** Updated `test_invoice_092052_multipage_per_page_metadata_qty_and_linking` to assert 14 line items (9 Page 1 + 5 Page 2), 17 total physical coins, single rows with `Quantity == 2` for 1964-D, 1982-S, and 2001-P, and clean linking (`linked == 14`, `unlinked == 0`).
3. **`numista_backend/tests/test_invoice_fixtures.py`:**
   - **Change D:** Updated 4 legacy tests expecting expanded lists to assert single row with `Quantity == N`.
4. **Version Bump:** `constants.dart` (`v8.18.15i`) & `pubspec.yaml` (`8.18.15+81819`).

### 3. Verification Evidence
- `pytest` across regression, fixtures, and container import path: **15/15 passed** in 1.15s.
- `flutter test`: **645/645 passed** in 37s.
- Line Endings: **0 CRLF bytes** on all 5 files.

Please review `git show 1ff435f0` and reply with your pre-handoff score and PASS / FAIL-FIX verdict in RADIO NET.

OVER.
