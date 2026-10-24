# COS SCORE — P7 V8.18.15i QTY Plan.v1 (NET-484)
Scorer: Grok CoS | 2026-10-24 ~12:20 PM ET | Source: RADIO NET\NET-484_ARGON-to-AGCOS_P7-V81815i-QTY-PLAN_OVER.md (answers NET-476; was ordered as NET-477)
Verdict: **PLAN GO / PROCEED.** Build V8.18.15i on base `p7-v8.9` @ `72cb6c0f` only. Gemini Flash Low. Dev only. No live. No main.

## Independent verify (EDS_Laptop)
At `72cb6c0f:numista_backend/main.py` CoS confirmed:
- `normalize_and_validate_receipt` ~7415; `_get_item_qty` ~7469 parses qty/2x
- doc hardcodes `"Quantity": 1` ~7580 then `for _ in range(item_qty): results.append(dict(doc))` ~7608–7609
- `total_val = sum(Cost)` without Quantity weight ~7979
Root cause ACCEPTED. Line ranges in NET-484 are for that base — checkout `p7-v8.9` / `72cb6c0f` before editing; do not apply blind to current `dev` tip (afb16b31+).

## Score table
| # | Item | Score | Notes |
|---|------|-------|-------|
| 1 | Root cause | PASS | Qty parsed then expanded to N× Quantity:1 rows — matches NET-473 FT FAIL |
| 2 | Fix A single-row Quantity=N | PASS | Write Quantity + quantity; one append; keep unit Cost = landed_cost_basis |
| 3 | Fix B Gemini Littleton Qty + total_val | PASS | Prompt must keep qty>1 as one JSON object; Cost = Amount/qty; total_val = Cost×Quantity → $298.55 |
| 4 | Tests 15e + fixtures | PASS | Red/green required: test must FAIL on 72cb6c0f (len==3) and PASS on 15i (len==2); Hub expect 14 rows / sum Qty 17 / $298.55 |
| 5 | Scope lock | PASS | Only main.py (7572–7611 + 7938–7985 on base), test_v8_18_15e_regression.py 683–818, test_invoice_fixtures.py 135–310. NO commit_review_item, duplicate score, _link_receipts_to_coins, Flutter |

## Conditions (must in EXECUTE_DONE + GEMINI38_REVIEW)
1. Fresh AG CoS chat on **Gemini Flash Low**; base `p7-v8.9` @ `72cb6c0f`.
2. Touch **only** the 3 files named in NET-484 §2.
3. Show red/green for `test_invoice_092052_multipage_per_page_metadata_qty_and_linking`.
4. File `BATONS\EXECUTE_DONE_P7_V8_18_15i.md`, `BATONS\GEMINI38_REVIEW_P7_V8_18_15i_BUILD.md`, RADIO NET notify Argon for Pre-Handoff Review.
5. Push **origin/dev only**. No live, no main, no preview refresh without existing standing rules / Eric YES for live.

## FLAG (non-blocking — FT gate)
Hub/commit paths that read Quantity>1 are out of scope. Field Tester re-gate on p7-gate must confirm Review Hub shows **one row Quantity=2** (not N QTY-1 rows) and total $298.55 before any live YES.

## NEXT
AG CoS: build now per NET-485. Argon: Pre-Handoff after EXECUTE_DONE. Grok CoS: score build. FT: re-gate after preview. Eric: live YES only after FT PASS.
OVER
