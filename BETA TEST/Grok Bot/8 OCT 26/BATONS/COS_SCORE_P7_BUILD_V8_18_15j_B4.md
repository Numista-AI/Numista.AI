# COS SCORE - P7 BUILD V8.18.15j B4 (shipping-credit cap) @ 2d2be994
**FROM:** Grok CoS  **DATE:** Mon 26 Oct 2026 ~9:36 AM ET
**REF:** NET-521 Argon PASS + HOLD PREVIEW, NET-520 EXECUTE_DONE, NET-518 FAIL-FIX EXECUTE, prior `COS_SCORE_P7_BUILD_V8_18_15j.md` (OC1 open at 3cdfa9d0)
**Scored tip (product):** `2d2be994` fix(p7): cap shipping fee to 0 when grand_total <= subtotal (OC1/B4)
**Repo tip at score time:** `4ea4f9ec` (docs only after B4; product score is `2d2be994`)

## VERDICT: 9/10 -- ACCEPT WITH CONDITIONS
**OC1 / Argon B4: CLOSED.** Narrow FAIL-FIX matches the EXECUTE baton, Argon PASSed (9/9), CoS re-verified on disk + re-ran the enrichment suite green. **Not live. No Eric YES. HOLD PREVIEW** until the `origin/dev` vs live `origin/p7-v8.9` branch split is reconciled (Argon NET-521 Part 2). CoS does **not** recommend asking Eric for a preview channel refresh until that reconcile lands.

## Plain-English
Sunday's Mint-pack landing left one hole: when the Mint invoice already includes (credits) shipping so total == subtotal, the worker still added the reported shipping fee and could stamp **$70.95** instead of **$61.00**. AG patched that on `dev` (`2d2be994`). Unit test now asserts Cost **61.00**, Qty **25**, unit_cost **2.44**. Argon and CoS both green on that patch.

Separately, Argon found `origin/dev` is missing **41** product commits that live only on **`origin/p7-v8.9` (`6ee3de89`)** (the branch that was actually deployed for V8.18.15i). Staging today's `dev` tip as preview would roll back multi-page invoices, `2x/Nx` Quantity rows, duplicate_check, `resolveApiBase()` preview host routing, and more. That is why preview is **HOLD**, not "ready after B4."

## What was verified (Grok CoS, EDS_Laptop, Mon 26 Oct ~9:36 AM ET)
1. **Commit scope:** `2d2be994` touches only `numista_backend/main.py` + `numista_backend/tests/test_us_mint_invoice_enrichment.py` (2 files; Rule 9.3 / skip GEMINI38 OK).
2. **B4 guard (`main.py` ~7490-7497 on tip containing `2d2be994`):**
   - `total_global_fees = 0.0`
   - `if grand_total > subtotal_val and subtotal_val > 0:` -> fees = grand - subtotal
   - `elif grand_total <= 0 and (shipping_val + tax_val) > 0:` -> fall back to explicit fees only
   - Else (credit case grand_total <= subtotal): fees stay **0** (no fallthrough to shipping_val).
3. **Regression test:** `test_b4_shipping_credit_cap_and_unit_cost` asserts `Cost == 61.00`, `Quantity == 25`, `unit_cost == 2.44` (not 70.95).
4. **CoS pytest re-run:** `python -m pytest numista_backend/tests/test_us_mint_invoice_enrichment.py -q` -> **9 passed in 0.18s**.
5. **Argon NET-521:** PASS on narrow B4/OC1; **HOLD PREVIEW** for 41-commit `origin/dev` vs `origin/p7-v8.9` (`6ee3de89`) split. CoS confirms split: `git log origin/dev..origin/p7-v8.9` = **41** commits; merge-base era ~16 Oct; tip of live branch `6ee3de89`.

## Plan / Argon scorecard (B4 re-score only)
| Item | Status |
|------|--------|
| B4 / OC1 shipping credit cap | **CLOSED** at `2d2be994` |
| C1 cost semantics (61 / 2.44 when input clean) | MET under B4 guard + enrich |
| C2 expand guard | Unchanged MET (prior 15j) |
| C5 tests | Improved: B4 Cost==61 present; still missing plan gaps 2->50 / non-pack (OC2) |
| C4 pack_quantity audit | Still PARTIAL / OC3 (26SQRP only) |
| C6 / no live | MET |
| Preview / staging readiness | **HOLD** -- branch split |

## Open conditions (updated)
- **OC1 (B4):** **CLOSED** at `2d2be994` (Argon PASS + CoS verify).
- **OC-PREVIEW (NEW, binding before any preview ask):** Reconcile `origin/p7-v8.9` (`6ee3de89`) with `origin/dev` (`2d2be994` + Mint-pack 15j commits) so preview does **not** drop the 41 live product commits. Apply B1/B2/B3/B4 onto the live-path sites Argon named (`normalize_and_validate_receipt` fee block + enrich call; worker `total_val` must not `Cost * Quantity` after pack expand; `added_this_file += Quantity`). Exact merge strategy is AG's call; CoS gates on "preview tip contains 15i live behavior + 15j B4."
- **OC2 (C5):** Still open -- 2 rolls->50, non-pack unchanged; keep Nx regression green after reconcile.
- **OC3 (C4):** Follow-up Mint roll/bag/pack SKU list with `pack_quantity`.
- **OC4:** Likely resolves when `p7-v8.9` (Quantity / Retailer Item No. in invoice path) is reconciled into the scored tip; re-check after merge.

## What HOLD PREVIEW means (house definition this turn)
1. **Do not** stage / refresh the preview channel from current `origin/dev` tip.
2. **Do not** ask Eric for a preview YES yet.
3. **Do not** start Field Tester uploads against a tip that would roll back `p7-v8.9` live commits.
4. B4/OC1 logic itself is **approved**; the hold is **branch topology / staging safety**, not a re-open of the shipping-cap bug.
5. After reconcile + CoS/Argon spot-check of the reconciled tip: CoS **will** recommend asking Eric (chat OK) for preview channel refresh YES. Until then: **no**.

## CoS recommendation on preview
- **Now:** **Do not recommend** preview. Exact blocker = **41-commit `origin/dev` missing live `origin/p7-v8.9` (`6ee3de89`) product history**.
- **After reconcile green:** Recommend Eric typed YES for preview refresh only (still no live/deploy). Then FT clears all **7** PDFs in Eric's Invoices folder. Only then discuss live YES (separate typed YES; never assumed).

## NEXT GATE (order)
1. **AG:** reconcile `origin/p7-v8.9` (`6ee3de89`) <-> `origin/dev` Mint-pack/B4 (`5a293ba3` / `3cdfa9d0` / `2d2be994`) per NET-521 Part 2; push; file EXECUTE_DONE / NET.
2. **Argon:** spot-check reconciled tip (B4 still present; no Cost*Qty explode; no live-commit rollback).
3. **CoS:** short re-score / go-no-go on preview tip.
4. **Eric typed YES** for preview channel refresh (chat OK) -- **required**; CoS will not assume.
5. Field Tester clears every PDF in Invoices folder (incl. 26SQRP -> Qty 25 / $61 / $2.44).
6. Only then: Eric typed YES for any live/deploy discussion.

**Explicit:** Not live. No deploy. No main merge. No Cloud Run. No spend. No FT uploads from CoS this turn. No preview refresh. WAKE never authorizes deploy.

GROKCOS OUT
