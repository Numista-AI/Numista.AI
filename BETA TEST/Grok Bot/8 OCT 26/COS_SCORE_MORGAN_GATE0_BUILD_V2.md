# COS SCORE - T2 Morgan Gate 0 BUILD V2 (commit 9769dac5 on dev)
Scored by: Grok CoS, 12 Oct 2026 ~8:05 PM ET. Read: git show 9769dac5 (main.py, routes/morgan_routes.py, firestore.rules, tests), dev HEAD main.py, morgan_routes.py, scan_service/collection_inventory.py, routes/ai_routes.py. Ran pytest myself.
PASS = code accepted on dev. DEPLOY needs Eric's typed YES. Nothing deployed. No live writes.

## Verdict: ITERATE (1 required fix, plus 2 small ones). Morgan still sends coin values to the AI on a normal question.

## Pytest (run by Grok CoS, numista_backend\.venv, `pytest tests -q`)
474 passed, 0 failed (9.7s). Matches EXECUTE_DONE.

## Fixed and checked in code
- Fix 1a edit needs Confirm: main.py:3262 `action_payload = propose_update_coin(owner_key, caller_uid, **c_args)`; main.py:2793 `action="update_coin"` stores `{"before": before, "changes": changes}`; confirm handles it at morgan_routes.py:266 `elif action in ("update_coin", "edit"):` and applies only `changes` (:276-277). Good.
- Fix 1b/2 tool undo: main.py:2829 `log_ref.where("coin_id", "==", coin_id).where("action", "==", "add")` (matches the log's `"action": final_action` = "add", morgan_routes.py:314), then main.py:2849 `action="delete_coin"` proposal. Missing coin returns "Coin not found in collection." with no trash write. Good.
- Fix 4 delimiter above the >50 branch: main.py:3041-3045 wraps every note/ocr/description/provenance/utterance key before `last_10 = inventory_items[-10:]` (:3052). Good.
- Fix 6 double-tap: morgan_routes.py:225 `@firestore.transactional` ... :232 `if fresh_data.get("used") is True:` ... :236 `transaction.update(prop_ref_inner, {"used": True})`. Second tap returns `idempotent: True` (:248-255). Good.

## Required fixes
1. **Values still reach the AI with no value question (G0-6, Eric's rule).** get_coin_details strips only these names, main.py:2705-2707: `("ai_estimated_value", "estimated_value", "cost", "Cost", "cost_basis", "Cost Basis", "purchase_price", "Purchase Price", "market_value", "P&L", "profit_loss")`. The real Firestore field names are different: main.py:2558 writes `"AI Estimated Value": formatted_ai_val` (44 uses in backend), and the backend also uses `"Purchase Cost"` (30), `"purchase_cost"` (16), `"Melt Value"` (14), `"melt_value"` (5), `"Price Paid"` (2). None of those are stripped, so "what year is my Vera Rubin quarter?" -> get_coin_details -> the AI sees the coin's AI Estimated Value and Purchase Cost. The test passes only because its fixture uses snake_case names (test_morgan_gate0.py:437 `"Cost": "$0.01", "ai_estimated_value": "$0.10"`). Fix: ONE shared financial-field filter (case-insensitive; drop any key containing value, cost, price, paid, melt, p&l, profit, cpg, basis) used by collection_inventory.py, get_coin_details and ai_routes.py, so a new field name can't slip past. Test with a real-shape coin doc (`"AI Estimated Value"`, `"Purchase Cost"`, `"Melt Value"`, `"Price Paid"`) and a non-value question -> none in the tool result or the built prompt. Systemic check: grep every other place a coin doc is json-dumped into a Gemini prompt (scanner, deep_dive tool results, review hub) and route them through the same filter.
2. **Privacy Mode TODO only in one place.** main.py:3025 `# TODO REQ-026: ...` is fine as a TODO, but ai_routes.py:118 `has_val_keyword = any(kw in (req.query or "").lower() ...)` has no TODO, and test_morgan_gate0.py:479 `test_privacy_mode_todo_placeholder` asserts nothing. Add the same TODO at ai_routes.py:118, and open a REQ-026 ticket line in EXECUTE_DONE saying users can't turn values off yet. Until REQ-026 ships, the keyword gate is the only gate, so fix 1 must be airtight.
3. **Claimed-but-failed proposal.** morgan_routes.py:236 marks `used` before the write; if the edit/delete then 404s (:273, :288) the proposal is burned with no action. Fine to fail closed, but return a clear message ("That coin is no longer in your binder") rather than a bare 404, and log it.

## Follow-ups (ticket, not blockers)
- `/api/morgan/propose` still accepts any action string / coin_data (from V1 score).
- `last_10` still doc-id order, not created_at (from V1 score).

Ball: AG CoS - fix 1 (with the real-field test) and 2-3 on dev, re-run pytest, file EXECUTE_DONE_MORGAN_GATE0_V3.md, pass baton back to GROKCOS. No deploy, no live writes.
