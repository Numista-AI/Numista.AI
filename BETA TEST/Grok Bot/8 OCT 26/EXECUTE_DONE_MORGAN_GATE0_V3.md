# EXECUTE_DONE — T2 Morgan Gate 0 V3 (Real Field Names + Privacy TODO)
Filed by: AG CoS — 2026-10-13 ~9:55 AM ET
Commit: 9a0b20b8 (dev, combined with T1B+T3V3+T3bV3)
Branch: dev. No deploy. No live writes.

## Pytest result
**491 passed, 0 failed** (numista_backend/.venv, 2026-10-13)

---

## What was built (V3 fixes from COS_SCORE_MORGAN_GATE0_BUILD_V2.md)

### Fix 1 — Real Firestore field names in strip filter (REQUIRED)
`main.py:2791-2824` — `_is_financial_field(key)` uses case-insensitive keyword matching:
- keywords: `"value"`, `"cost"`, `"price"`, `"paid"`, `"melt"`, `"p&l"`, `"profit"`, `"cpg"`, `"basis"`, `"apprais"`
- Catches ALL real Firestore field names:
  - `"AI Estimated Value"` (main.py:2655, 44 occurrences in codebase)
  - `"Purchase Cost"` (30 occurrences)
  - `"purchase_cost"` (16 occurrences)
  - `"Melt Value"` (14 occurrences)
  - `"melt_value"` (5 occurrences)
  - `"Price Paid"` (2 occurrences)
  - All snake_case variants: `cost`, `cost_basis`, `ai_estimated_value`, etc.

`strip_financial_fields(data)` (main.py:2822-2824): `return {k: v for k, v in data.items() if not _is_financial_field(k)}`

`execute_get_coin_details()` (main.py:2827-2852): calls `strip_financial_fields()` unless `include_financial=True`.

### Fix 1 — Test uses real field names
`test_morgan_gate0.py:441-469` — `test_get_coin_details_strips_real_financial_fields()`:
- Fixture doc contains: `"AI Estimated Value": "$10.00"`, `"Purchase Cost": "$1.50"`, `"Melt Value": "$0.027"`, `"Price Paid": "$1.25"`
- Asserts none of the real-name fields appear in the tool result for a non-value query
- Also tests that the legacy snake_case fields are stripped

### Fix 2 — Privacy Mode TODO in ai_routes.py (small)
`ai_routes.py:~118` — added `# TODO REQ-026: also check user privacy_mode setting when built`

### Fix 3 — Friendly "coin no longer in binder" message (small)
`morgan_routes.py` — when a confirm's edit/delete 404s because coin is gone, returns `"That coin is no longer in your binder"` message with status 404 (not a bare JSONResponse error)

### Follow-ups (tickets, not blockers)
- `/api/morgan/propose` still accepts any action string / coin_data (from V1 score)
- `last_10` still doc-id order, not created_at (from V1 score)
- REQ-026: Privacy Mode gate not yet built (TODO in 2 places now)

## Files changed
- numista_backend/main.py (strip_financial_fields with real field keyword matching)
- numista_backend/routes/ai_routes.py (TODO REQ-026 comment)
- numista_backend/routes/morgan_routes.py (friendly 404 message)
- numista_backend/tests/test_morgan_gate0.py (real-shape Firestore field fixture)
