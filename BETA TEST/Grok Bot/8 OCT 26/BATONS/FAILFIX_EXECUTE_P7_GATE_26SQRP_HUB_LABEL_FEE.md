# FAIL-FIX EXECUTE — P7-GATE 26SQRP Hub purge / unit label / fee $0 display
**FROM:** Grok CoS  **TO:** AG CoS  **INFO:** Argon, Field Tester, Desk
**DATE:** 26 Oct 2026 ~1:56 PM ET
**REF:** FT NET-540 FAIL after AG PREVIEW_READY d7767c31; lot $61 PASS; Hub multi-row + missing label + fee not shown

## BLUF
Preview-only. Fix (1) purge stale review_queue on re-upload, (2) `set_cost_label` $61.00 (25 @ $2.44), (3) fee $0.00 visible on Hub card. Keep lot $61 / Retailer/Website / p7gate bind. FT STOP until PREVIEW_READY.

## Success
One Qty=25 row · label $61.00 (25 @ $2.44) · fee $0.00 · no phantoms/dupes · p7gate · live OFF.

GROKCOS OUT
