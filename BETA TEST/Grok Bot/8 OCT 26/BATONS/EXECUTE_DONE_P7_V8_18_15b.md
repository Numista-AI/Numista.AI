# EXECUTE DONE: P7 Add Coins Flow V8.18.15b

**Date:** 2026-10-22 ~15:26 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `c096574095b0c5f8856e0908833c8d346f9dba5b` (pushed cleanly to `origin/p7-v8.9`)  
**Parent Commit:** `a7c83d7d16023aada321643a4b92329118c11270`  
**Preceding Directives:** NET-425 RCA / V8.18.15 Follow-Up Items 1-5  
**Rule 6 / Rule 9.3 Review Status:** Complete (`BETA TEST\Grok Bot\8 OCT 26\BATONS\GEMINI38_REVIEW_P7_V8_18_15b_BUILD.md`)

---

## 1. Quality Gates & Test Verification

- **`flutter test test/p7_v8_ux_safety_test.dart --name "V8.18.15b"`**: **2/2 PASS** (100% green; covers Item 2 exact NGC copy and Item 5 review snackbars formatting logic).
- **`flutter analyze lib/`**: **0 issues found** (0 errors, 0 warnings; clean in 5.9s).
- **`py -m pytest numista_backend/tests/`**: **606/606 PASS** (100% green in 32.8s; includes 3 new regression tests in `test_cert_lookup.py`, `test_invoice_fixtures.py`, and `test_req031_auth.py`).
- **Line Ending Hygiene**: LF-only line endings strictly preserved across all 11 modified files.
- **No live deploy performed**: Pushed strictly to `origin/p7-v8.9`. Nothing pushed to `main` or `dev`. No direct writes to Firestore.

---

## 2. Requirement Verification Matrix

| Item | Requirement Description | Status | Exact file:line Implementation & Tests |
|---|---|---|---|
| **Item 1** | **Tap targets $\ge$ 48px on sidebar buttons:** Ensure `Send Beta Feedback` and `Sign Out` sidebar buttons have 48px minimum touch target height. | **PASS** | `numista_mobile/lib/screens/base_layout.dart:958, 1033` |
| **Item 2** | **NGC card copy update:** Update copy to exact string: `"We can't look up NGC numbers automatically yet. Snap the label or type the details below."` | **PASS** | `numista_mobile/lib/screens/add_coins_hub.dart:3753`<br>`numista_mobile/test/p7_v8_ux_safety_test.dart:3053-3085` |
| **Item 3** | **Cert photo OCR 1024 tokens + timeout + json_repair:** Increase `max_output_tokens` to 1024, wrap model call in 25s executor timeout, add `json_repair` fallback handling for truncated responses, and guide reverse-label cert numbers. | **PASS** | `numista_backend/routes/cert_routes.py:416-419, 440-466`<br>`numista_backend/requirements.txt:151`<br>`numista_backend/tests/test_cert_lookup.py:864-876` |
| **Item 4** | **U.S. Mint invoice PDF parsing & web polling:** Parse retailer (defaulting "United States Mint"), invoice number, purchase date, preserve Qty > 1. Update `add_coins.html` polling to 60s timeout with countdown and real server error text. | **PASS** | `numista_backend/main.py:7542-7545, 7865-7893`<br>`numista_mobile/web/add_coins.html:1031-1055, 1073-1087`<br>`numista_backend/tests/test_invoice_fixtures.py:276-310` |
| **Item 5** | **Deduplication rules without silent drops:** Attribute matches (Year+Mint+Denom) commit with `possible_duplicate=True` and `duplicate_flag` (never delete queue doc without committing). Invoice# + Item No matches exclude `request.review_ids` so split Qty rows in same batch both commit. Review hub snackbars state committed and skipped counts. | **PASS** | `numista_backend/main.py:3565, 3583-3595`<br>`numista_mobile/lib/screens/review_hub_screen.dart:55-72, 130-148`<br>`numista_backend/tests/test_req031_auth.py:192-308`<br>`numista_mobile/test/p7_v8_ux_safety_test.dart:3087-3105` |

---

## 3. Commit & Branch Summary

- **Branch:** `p7-v8.9`
- **Worktree:** `C:\Users\ericd\AppData\Local\Temp\p7v89_build`
- **Remote:** `origin/p7-v8.9`
- **Commit:** `c096574095b0c5f8856e0908833c8d346f9dba5b`
- **Commit Message:** `fix(p7-v8.18.15b): tap targets 48px, NGC copy, cert photo 1024 tokens, invoice pdf parsing, no silent dupe drops, review snackbars`
