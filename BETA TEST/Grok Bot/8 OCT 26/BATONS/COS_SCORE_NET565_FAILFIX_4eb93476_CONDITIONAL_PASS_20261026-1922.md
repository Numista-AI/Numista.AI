# NET-572 GROKCOS to FT/AGCOS/ARGON - NET-565 FAILFIX SCORE: CONDITIONAL PASS, RE-GO FT CANARY (23RH ONLY)
Filed 2026-10-26 7:22 PM ET by Grok CoS (evening watch). Ref NET-566 (AGCOS 7:09 PM), commit 4eb93476 (fix rode in 19:00 auto-backup; tip 90518701).

Code check: review_hub_screen.dart maps dotted keys to snake_case (purchase_date, retailer_item_num, ...), adds editable 'Fee / Shipping & Handling' -> allocated_fees + shipping_fee, Hub Date reads purchase_date first. main.py: only pack_expanded zero fee. Preview https://numista-vault--p7-gate-8avtpz22.web.app 200; live numista.ai 200; main untouched.

FT canary on p7gate, Eric 23RH only. Pre-locked acceptance (functional PASS only, no cosmetic FAIL-FIX):
1. Edit Coin -> Save and Save & Commit complete with NO error toast.
2. In Edit set Fee 9.95 -> Save -> Fee 9.95 shows on Hub card AND on reopened Edit.
3. Hub card Date shows the purchase date that Edit has.
Report PASS/FAIL per item with screenshot. Any item FAIL -> per Eric rule, Stand Alone Grok + Gemini plan loop, no blind re-fix.
Known/not in scope tonight: re-import giving 9.95 untested; 26SQRP same-order fee zeroing (~L7526) unchanged; no unit tests. Live/main OFF. Catalog NET-568 still paused, no credit burn on 565 path beyond this. OVER.
