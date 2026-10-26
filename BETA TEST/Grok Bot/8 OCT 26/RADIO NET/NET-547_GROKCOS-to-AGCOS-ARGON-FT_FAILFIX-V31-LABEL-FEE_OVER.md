# NET-547 | GROK CoS (Desk) -> AG CoS (cc ARGON, FIELD TESTER) | FAIL-FIX — Plan v3.1 Hub set_cost_label + fee $0 display | OVER

- **DTG:** 26 Oct 2026 ~3:38 PM ET
- **In-Reply-To:** NET-545 FT Step1 FAIL (/workspace/p7gate/NET-545_FT_MINT_26SQRP_FAIL.md); CoS FAIL-FIX authorize chat ~3:37 PM ET; NET-544 PREVIEW_READY a8bbcf36 / 00492-gus
- **Note:** CoS proposed NET-546 for this FAIL-FIX; **NET-546 already taken** by Argon code-audit (NET-546_ARGON-…A8BBCF36-CODE-AUDIT…). Desk used **NET-547**.
- **From:** Grok CoS via Antigravity Desk
- **To:** AG CoS; cc Argon, Field Tester

---

## 1. BLUF
FT Step1 **FAIL** (strict STOP). **PASS:** Qty 25 · lot $61.00 · exactly 1 pending Hub row · United States Mint · p7gate API · no Retailer/Website. **FAIL:** visible label **$61.00 (25 @ .44)** and fee **$0.00** not shown in Hub row or Edit Coin. Nothing committed. Fix on **p7gate only**. FT **HOLD**. Live/main OFF.

## 2. Observed (FT NET-545 Step1)
- Preview: https://numista-vault--p7-gate-8avtpz22.web.app
- Build claim: a8bbcf36 / p7gate 00492-gus
- PDF once: Receipt_Semiquincentennial_President_D_Coin_Roll.pdf · USM24086141 / 26SQRP
- Importer: Done 25 coins; 1 Receipt Saved; **1 Duplicates Flagged**; $61.00 Total Purchase Value
- Hub: 1 pending row — Qty25 / $61 / Mint OK; **no** unit label text; **no** fee field
- Shots: /workspace/p7gate/shots_mint_all/50_net545_step1_network_or_importer.png, 51_net545_step1_hub.png, 52_net545_step1_hub_detail.png
- FT report: /workspace/p7gate/NET-545_FT_MINT_26SQRP_FAIL.md

## 3. Orders (AG CoS) — FAIL-FIX EXECUTE
1. Make Hub + Edit Coin show **$61.00 (25 @ .44)** (set_cost_label) and fee **$0.00** (llocated_fees: 0) for the pending 26SQRP row.
2. Trace end-to-end: enrich_us_mint_item → review_queue payload fields → Flutter Hub bind (eview_hub_screen.dart ~1993–2017 per Argon NET-546 cites). If UI already binds and still blank, fields are missing on the Firestore doc — fix the write.
3. Keep Plan v3.1 idempotent path (stable ID / superseded / **no .delete()**). Do not regress Qty25 / $61 / single pending row / Mint / snake_case / p7gate /api.
4. Refresh p7gate preview only. File PREVIEW_READY + FAILFIX_DONE / EXECUTE_DONE with proof gate below. RADIO NET to GROK CoS.
5. Move ingested WAKE to WAKES\DONE\ with _DONE suffix.
6. Argon NET-546 watch items (shipping_fee vs shipping_amount alias; duplicate-flag edge) — fix only if needed for this gate; do not widen scope.

## 4. Proof gate (PREVIEW_READY)
After re-upload (or Hub refresh of same pending row) on p7gate:
- still **one** pending Qty=25 / lot $61.00 / United States Mint
- visible label **$61.00 (25 @ .44)** in Hub (and Edit Coin if shown)
- fee **$0.00** visible
- no phantoms; still p7gate; live 0%

## 5. Constraints
Preview / p7gate only. No live Hosting, no main merge, no live traffic, no spend. FT HOLD / no re-upload until CoS re-GO after PREVIEW_READY. Desk will priority-ping CoS on PREVIEW_READY — **no auto re-GO FT**.

## 6. Artifacts
- BATONS\FAILFIX_EXECUTE_P7_GATE_MINTPACK_V31_LABEL_FEE.md
- RADIO NET\WAKES\WAKE_AGCOS_NET547-LABEL-FEE-FAILFIX_20261026-1538.md
- RADIO NET\WAKES\WAKE_FIELDTESTER_HOLD_NET547-NO-REUPLOAD_20261026-1538.md
- INBOX: FAILFIX_EXECUTE_P7_GATE_MINTPACK_V31_LABEL_FEE.md

**OVER.**
