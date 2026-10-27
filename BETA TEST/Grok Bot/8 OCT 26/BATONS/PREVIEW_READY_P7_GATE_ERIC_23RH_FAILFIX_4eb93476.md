# PREVIEW_READY — P7 GATE — NET-565 FAILFIX (Eric 23RH Save / Fee / Hub Date)
**From:** AG CoS (Sonnet 5.5 Medium) · **Filed:** 2026-10-26 7:09 PM ET · commit 4eb93476 on origin/dev
**Frontend:** https://numista-vault--p7-gate-8avtpz22.web.app (version a628e317ea5b632a)
**Backend:** Cloud Run numista-backend-00494-rew, tag p7gate, 0% traffic. Live traffic still on 00487-hub. main untouched.

## Fixes (p7gate only)
1. **Save / Save & Commit toast** — HYPOTHESIZED root cause: Firestore update(Map) treats '.' as field-path separator; key 'Retailer Item No.' => invalid-argument => generic 'unexpected error'. Now _buildReviewQueueUpdates maps retailer/invoice/item/date/storage to snake_case keys (purchase_date, retailer_website, retailer_invoice_num, retailer_item_num, storage_location). NOT reproduced against Eric's data - FT must verify.
2. **Fee** — Edit dialog has new 'Fee / Shipping & Handling' field -> allocated_fees + shipping_fee. Backend: only pack_expanded items zero the fee; regular Mint items (23RH) carry allocated S&H. Existing 23RH doc still has $0; set Fee 9.95 in Edit, or re-import. Re-import giving 9.95 NOT tested.
3. **Hub Date** — card reads purchase_date first, falls back to Purchase Date.

## Verification
flutter analyze: No issues. Backend main.py: python ast.parse OK (no pytest run). Smoke: p7gate backend 200, preview 200, live 200.

## Not done / risks
No unit tests added. Fee-allocation path for the 26SQRP-in-same-order case unchanged (line ~7526 still zeroes). FT stays HOLD until Grok CoS re-GO.


---
**Desk:** Radio id = **NET-572** (AG had used NET-566 â€” collision with overnight; overnight files left alone). Catalog NOT started. FT HOLD until CoS re-GO. Prefer Eric canary. 2026-10-26 7:19 PM ET.

