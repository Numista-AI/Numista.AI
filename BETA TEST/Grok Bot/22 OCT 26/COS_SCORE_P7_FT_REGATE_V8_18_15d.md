# COS SCORE - P7 FT re-gate V8.18.15d (1058fe8b, backend numista-backend-00483-mop) - FAIL
22 Oct 2026, 8:25 PM ET. Grok CoS. Read-only triage: code at 1058fe8b plus Cloud Run logs. No data reads or writes.
Note: FT_P7_GATE_V8_18_15d.md isn't in the 22 OCT 26 folder yet, so I used FT's NET-439 summary and UX's UX_P7_GATE_V8 notes.

## (a) Invoice regressions: CONFIRMED, one root cause
- main.py about L7940-7960, `_execute_import_process_worker` invoice branch. 15b (c0965740) moved the subtotal/shipping/tax/grand_total math into `normalize_and_validate_receipt` (L7397), but `receipt_doc` still uses the old locals `subtotal_val`, `shipping_val`, `tax_val` and `grand_total`. The result is `NameError: name 'subtotal_val' is not defined` (UX, ASE invoice).
- The same block calls `data.get("retailer"/"invoice_number"/"invoice_date")`. When Gemini returns a top-level JSON list (a common shape for multi-line Mint invoices like 092052), this raises `'list' object has no attribute 'get'`. That's the old 8.18.12 bug coming back through this code path. `normalize_and_validate_receipt` accepts `Any`, but the receipt_doc code doesn't.
- Both errors happen AFTER `batch.commit()` of the review_queue rows. That explains all the symptoms:
  - The rows reach the Review Hub (17).
  - The receipt doc is never written, so Retailer, Invoice # and Date show N/A.
  - `summary.coins_identified` is never incremented, so the summary reads 0 identified / 0 saved.
  - `_run_duplicate_sweep` still runs on `new_coin_ids` and flags those rows against grokbot's coins (16 for 092052, 1 for the ASE, which matches the existing USM23339673 2026-W ASE). The flags are probably legitimate matches against coins already in grokbot, but I didn't read grokbot's data to confirm it.
  - The session is then set to `status: done` no matter what per_file errors happened, so the user sees a green "Import Complete" next to an error.
- The exception is caught and only written to per_file. `logger.exception` output didn't show up in the 00483-mop text logs (00:09:35-00:09:43Z), so the logs have no trace. That's a logging gap too.

## (b) Dime duplicate with no flag
- The 15d possible_duplicate logic only exists in `commit_reviews` (L3558-3605) and in the bulk-session `_run_duplicate_sweep`. A single manual add ("Added 1 coin" toast) writes straight to the collection and never goes through either one, so FT almost certainly used the single-add path. That path has no duplicate check, and the 15d audit missed it. Paths to audit: manual add, scan-save, cert lookup save, spreadsheet `/api/import/spreadsheet` (routes/import_routes.py) and review commit.

## (c) Tap targets: FAIL (confirmed by FT and UX)
Collection row icons are about 10px with 11px gaps (Delete hits AI Deep Dive), Review checkboxes about 14px, cert buttons 26-28px, and NET-440 already covers the 40px buttons and the web density shrink.

## (d) NGC Look Up
It says "Enter a cert # before saving" when the field has a value. The validator runs on the save path and not the NGC lookup path. Minor copy/flow fix.

## Score: FAIL. 15d doesn't meet "audit every duplicate path", and 15b caused an invoice regression that live main doesn't have.
Argon calibration findings 1-2 still stand, and the hotfix has to carry them. The hotfix must NOT carry 15b's receipt_doc refactor unless the regression fixes come with it.
