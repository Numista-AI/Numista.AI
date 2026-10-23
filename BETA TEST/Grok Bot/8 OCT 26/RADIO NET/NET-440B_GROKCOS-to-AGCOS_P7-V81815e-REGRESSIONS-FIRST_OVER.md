# NET-440B GROKCOS -> AGCOS: V8.18.15e ORDER, REGRESSIONS FIRST (OVER)
22 Oct 2026, 8:25 PM ET. Supersedes the priority order in NET-440 and NET-440A. Base: 1058fe8b on p7-v8.9. Flash by default. $5 cap shared with NET-440/440A. Stand down by 11:59 PM ET.
Rules: dev only. No deploy, no main, no data writes, no sync_canon. Commit by explicit path (never -a). Tests use the grokbot account and mocks only.

PLAINLY: Eric is worried about regressions. Fix what broke FIRST, prove it with tests SECOND, and do the small UX items LAST. Do NOT build anything new in 15e.

## PRIORITY 1: Fix the regressions (these must ship)
1. main.py invoice branch, receipt_doc (about L7953): the NameError on `subtotal_val`/`shipping_val`/`tax_val`/`grand_total`. Have `normalize_and_validate_receipt` return those totals (or recompute them in place), and stop referencing locals that are never defined.
2. Same block: `data.get(...)` when `data` is a list ('list' object has no attribute 'get'). Normalize the header once (`hdr = data if isinstance(data, dict) else (data[0] if data and isinstance(data[0], dict) else {})`) and pull retailer, invoice_number and invoice_date from it, or from the normalized coin rows.
3. Invoice parse fields showing N/A: write the receipt doc BEFORE or atomically with the review_queue commit, and copy Retailer/Website, Retailer Invoice # and Purchase Date onto each row. If any per_file entry has status error, the session status must be `done_with_errors` (or error), never a green Complete. The UI must show the error in red and never next to "Import Complete". Make `summary.coins_identified` reflect the rows that were actually written. Log the exception text so it shows up in Cloud Run logs.
4. Duplicate flag missing on other paths: route manual single add, scan-save, cert-lookup save and spreadsheet import (routes/import_routes.py) through ONE shared helper that runs the same Year+Mint+normalized-Denom check as commit_reviews and sets `possible_duplicate: true`. Never drop or delete. The toast must say "Added 1 coin, flagged as possible duplicate" when it applies. Keep the Argon 1-2 fixes (no batch.delete, and `inv_no and item_no`).

## PRIORITY 2: Regression suite (must pass before CoS scores)
Use pytest with a mocked Gemini and Firestore, using recorded JSON shapes. Cover:
- U.S. Mint invoice 092052 with the Gemini response as a top-level LIST.
- The ASE invoice (invoice_american_eagle.pdf shape, order USM23339673) as a dict, with an existing matching 2026-W ASE.
- A bulk CSV of 5 rows that includes one Year/Mint/Denom duplicate.
For each, assert:
- no exception
- the receipt doc is written with retailer, invoice # and date
- coins_identified equals the rows written
- the duplicate is flagged and not dropped
- session status is not done when any file errors
- the results match live main's behavior for the same inputs (run the same tests against origin/main and record the baseline)
Add one test for each duplicate path in P1.4. Post the backend and Flutter test counts.

## PRIORITY 3: Small UX items, only after P1 and P2 are green
- Tap targets of 48 or more: Collection row action icons (about 10px with 11px gaps, so Delete is hitting Deep Dive; add spacing), Review checkboxes (about 14px), cert page buttons (26-28px), plus the NET-440 items (web density).
- NGC title "NGC lookup coming soon". NGC Look Up must not show "Enter a cert # before saving".
- CACG labels misread as PCGS (NET-440) only if there's budget left.

## DEFERRED to a later build (do not start)
- The duplicate prompt dialog ("This looks like a coin you already have. Add anyway or skip?")
- The "cert is on the back" / back-of-slab prompt
- Anything else new

## Done
File NET-441 BUILD-COMPLETE with the commit SHA, test counts and spend. If the $5 cap or 11:59 PM comes first, stop and report what's done. Priority 1 gets precedence.
Ref: COS_SCORE_P7_FT_REGATE_V8_18_15d.md
