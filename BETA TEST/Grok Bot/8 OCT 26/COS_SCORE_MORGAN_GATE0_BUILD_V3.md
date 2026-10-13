# COS SCORE - T2 Morgan Gate 0 BUILD V3 (commit 9a0b20b8 on dev)
Scored by: Grok CoS, 13 Oct 2026 ~10:30 AM ET. Read real code at dev HEAD 0f33323b: main.py (_is_financial_field / strip_financial_fields / execute_get_coin_details / propose_update_coin / deep_dive tool loop), scan_service/collection_inventory.py, routes/ai_routes.py, routes/morgan_routes.py, tests/test_morgan_gate0.py. Ran pytest myself.
PASS = code accepted on dev. DEPLOY needs Eric's typed YES. Nothing deployed. No live writes.

## Verdict: PASS (on dev). All 3 V2 items are fixed and I checked them in the code. Deploy waits on T1B, since they ship together under one Eric YES.

## Pytest (run by Grok CoS)
491 passed, 0 failed (13.2s).

## V2 items - checked in code
1. **Real field names stripped (required).** main.py:2807-2819 `k = key.lower()` / `return any(kw in k for kw in ("value", "cost", "price", "paid", "melt", "p&l", "profit", "basis", "cpg", "apprais",))`; main.py:2824 `return {k: v for k, v in data.items() if not _is_financial_field(k)}`; used at main.py:2839-2840 `if not include_financial:` / `data = strip_financial_fields(data)`. Covers "AI Estimated Value", "Purchase Cost", "Melt Value", "Price Paid" and the snake_case forms. Called from the tool loop at main.py:3397 `action_payload = execute_get_coin_details(owner_key, include_financial=has_val_keyword, **c_args)`.
   - Systemic check: the only coin data that goes back to Gemini is `json.dumps(action_payload)` at main.py:3400. The other tool payloads return no raw coin doc: propose_update_coin returns only `"changes": changes` (main.py:2927-2933; the `before` snapshot goes only into the proposal, :2924). The inventory in collection_inventory.py is an allow-list, and money appears only under `if include_financial:` (:111-113, :164-166, :185-187). ai_routes.py:129 `if has_val_keyword:` gates portfolio value/P&L. No leak found.
   - Real-shape test: test_morgan_gate0.py:441-444 fixture `"AI Estimated Value": "$10.00", "Purchase Cost": "$1.50", "Melt Value": "$0.027", "Price Paid": "$1.25",`, asserts :467-470 `assert "AI Estimated Value" not in coin` ... `assert "Price Paid" not in coin`, and checks :481-484 that Year/Denomination/Personal Notes survive. Good.
2. **Privacy TODO in ai_routes (small).** ai_routes.py:119 `# TODO REQ-026: also check user privacy_mode setting when built - the keyword gate`, plus main.py:3155. Good.
3. **Clear message on claimed-but-missing coin (small).** morgan_routes.py edit and delete branches now `logger.warning(f"Claimed edit proposal {req.proposal_id} but coin {coin_id} no longer in collection")` and `detail="That coin is no longer in your binder - it may have been deleted. The proposal has been used and cannot be retried."` (status 404). Good.

## Notes (not blockers for T2; tracked elsewhere)
- The keyword filter is broad ("value" also strips a "Face Value" field if one exists). That fails closed, which is the safe direction. Watch for Morgan answers about face value.
- deep_dive turns its own 401 and the G0-5 429 rate cap into 500 "Morgan AI is temporarily unavailable" (main.py:3409). Fix is in T1B required fix 5.
- users/{email}/morgan_proposals is client-writable under the rules wildcard, and /api/morgan/confirm reads proposals from there (morgan_routes.py:169 `user_prop_ref = db.collection("users").document(caller_email).collection("morgan_proposals")...`). A user can forge their own proposal and have the server (Admin SDK) apply it to their own coins, which skips Confirm and the is_demo rule. This only affects the user's own account. Fix is in the T3b rules item.

## Follow-ups (ticket, not blockers - carried from V1)
- `/api/morgan/propose` still accepts any action string / coin_data.
- `last_10` still doc-id order, not created_at.
- REQ-026 Privacy Mode gate not built (TODO in 2 places).

Ball: AG CoS, WAIT-OUT (parked, no T2 work). It goes to Eric for YES in one bundle with T1B + rules once T1B passes. When T1B V2 is passed back to GROKCOS, pass this baton back with it.