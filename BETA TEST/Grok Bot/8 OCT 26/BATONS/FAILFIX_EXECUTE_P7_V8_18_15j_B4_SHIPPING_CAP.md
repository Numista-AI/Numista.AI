# FAIL-FIX EXECUTE - P7 V8.18.15j B4 shipping-credit cap (OC1)
**FROM:** Grok CoS  **TO:** AG CoS  **INFO:** Argon, Eric
**DATE:** 26 Oct 2026 ~9:00 AM ET
**REF:** `COS_SCORE_P7_BUILD_V8_18_15j.md` (8/10 ACCEPT WITH CONDITIONS), NET-517, NET-505 B4 BINDING, `GEMINI38_REVIEW_P7_V8_15j_BUILD.md`, tip `3cdfa9d0`
**PATTERN:** Same as NET-489 after diagnosis clear (qty FAIL-FIX) — CoS orders AG exact patch; Argon re-reviews the fix commit.

## BLUF
CoS BUILD score holds **ACCEPT WITH CONDITIONS**. Binding hole **OC1 / Argon B4** is incomplete on tip `3cdfa9d0`: when the model reports `shipping_fee=.95` while `total_amount` already equals the `` subtotal (shipping credited), the worker `elif` still adds fees and lands **Cost=$70.95`** (unit_cost ~2.84) instead of Mint public **$61.00 / $2.44**.

**Owner now: AG CoS.** Patch on `dev` only. No main merge / Cloud Run / live / spend. Eric YES required for those.

Secondary (do **not** block this EXECUTE): OC2 C5 suite gaps; OC3 pack_quantity only on 26SQRP; OC4 worker JSON schema Quantity / Retailer Item No. — note in EXECUTE_DONE; defer unless trivial in same tiny diff.

## EXACT FIX (AG)

### File 1 — `numista_backend/main.py` (import worker landed-cost block ~7490-7495)
**Current (broken when grand_total == subtotal and shipping_val > 0):**
```python
                    # B4: Cap shipping offset to avoid phantom landed cost
                    total_global_fees = 0.0
                    if grand_total > subtotal_val and subtotal_val > 0:
                        total_global_fees = grand_total - subtotal_val
                    elif (shipping_val + tax_val) > 0:
                        total_global_fees = shipping_val + tax_val
```

**Required:**
```python
                    # B4: Cap shipping offset to avoid phantom landed cost
                    # When grand_total <= subtotal (shipping credited / included), fees MUST stay 0.
                    # Do NOT fall through to shipping_val+tax_val — that lands $70.95 instead of $61.00.
                    total_global_fees = 0.0
                    if grand_total > subtotal_val and subtotal_val > 0:
                        total_global_fees = grand_total - subtotal_val
                    elif grand_total <= 0 and (shipping_val + tax_val) > 0:
                        # Invoice total missing — fall back to explicit fee fields only
                        total_global_fees = shipping_val + tax_val
                    # else: grand_total <= subtotal_val (credit/offset case) → total_global_fees stays 0.0
```

If the same `elif (shipping_val + tax_val) > 0` pattern still exists in legacy `normalize_and_validate_receipt`, apply the identical guard there. Prefer one tiny worker-path fix if that is the only live Add Coins path (CoS scored worker path).

### File 2 — `numista_backend/tests/test_us_mint_invoice_enrichment.py` (or worker landed-cost unit test)
Add a regression that **fails on `3cdfa9d0`** and **passes after the patch**:
- Inputs simulating Mint 26SQRP: subtotal `61.00`, shipping_fee `9.95`, tax `0`, total_amount `61.00` (credited).
- Assert landed `Cost == 61.00` (NOT `70.95`) and after enrich `Quantity == 25`, `unit_cost == 2.44`.
- Keep existing 8 enrichment tests green.

### Scope lock
Touch **only** the worker B4 block (+ legacy twin if needed) and the test file(s). No Flutter. No catalog churn. No live/deploy scripts.

### Docs after green
1. Update / file `BATONS\EXECUTE_DONE_P7_V8_18_15j_B4.md` with commit hash, Red/Green one-liner, pytest count for the touched suite.
2. Thin `BATONS\GEMINI38_REVIEW_...` only if Rule 9 allows skip for ≤2 files — **skip GEMINI38** for this ≤2-file fix (Rule 9.3); Argon re-review substitutes.
3. Radio NET to Argon requesting re-review of the B4 fix commit (PASS / FAIL-FIX).

## SEQUENCE
AG patch + push `dev` → Argon re-review → CoS re-score OC1 → preview (Eric chat OK) → FT Invoices folder → Eric YES for live.

**Explicit:** Not live. No deploy. No main merge. No spend. WAKE never authorizes deploy.

GROKCOS OUT