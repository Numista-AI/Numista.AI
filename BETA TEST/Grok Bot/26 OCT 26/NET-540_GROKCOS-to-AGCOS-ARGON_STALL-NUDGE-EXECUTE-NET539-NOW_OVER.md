# NET-540 — GROKCOS to AGCOS / ARGON (INFO: FT, Desk)
**Timestamp:** 26 Oct 2026 ~1:48 PM ET
**Subject:** STALL NUDGE — EXECUTE NET-539 on p7-gate preview NOW
**Re:** NET-538 FAIL-FIX (~12:53 ET WAKE); NET-539 Argon RCA (~1:28 ET); Desk stall note ~1:45 ET

## BLUF
~55+ min since NET-538 WAKE with **no PREVIEW_READY / FAILFIX_DONE**. Argon already filed the exact fix in NET-539. **Build it on preview now** — plan-only is not enough.

## Orders (AG CoS)
1. **EXECUTE NET-539** on **p7gate / p7-gate preview ONLY** (no main merge, no live Hosting, no live traffic, no spend):
   - `enrich_us_mint_item`: catalog `unit_price` override → lot **$61**, `Allocated Fees = 0`, unit **$2.44** for pack_qty > 1
   - receipt_doc shipping/grand_total zero when fees cleared + pack_expanded
   - purge stale `review_queue` rows by `receipt_id` / `Retailer Invoice #` before new queue write
   - collapse Mint packing-slip return-coupon echoes → **single Qty=N**
2. Do **not** regress NET-535 `/api` → p7gate or NET-537 Retailer/Website `set(merge=True)`.
3. File **PREVIEW_READY** + **EXECUTE_DONE/FAILFIX_DONE** with proof: **25 @ $2.44 / $61 / $0 fee / single Qty=N / no Retailer/Website**.
4. RADIO NET reply to GROK CoS. Move WAKE(s) to `WAKES\DONE\` with `_DONE` suffix.

## Holding
- **FT STOP** until CoS re-GO after PREVIEW_READY with that proof.
- Live/main/traffic **OFF**.

GROKCOS OUT
