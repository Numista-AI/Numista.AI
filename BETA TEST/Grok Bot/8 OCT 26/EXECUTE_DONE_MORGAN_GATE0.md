# EXECUTE_DONE — Morgan Gate 0 (T2)
Filed by: Antigravity CoS  
Date: 2026-10-12 ~5:27 PM ET  
Commit: `0b436c97` on `dev` (rebased on T1 `a774152f`)

## Result: DONE — all G0-1 through G0-9 applied, 456 tests pass, pushed to dev

| Item | Description | File:Line |
|---|---|---|
| G0-1a | Removed "immediately" from Morgan prompt | main.py:3061-3063 |
| G0-1b | Proposal store (Firestore proposals/{uid}/pending/{id}) | morgan_routes.py:53-97 |
| G0-1c | `POST /api/morgan/confirm` — idempotent, 410 on expiry | morgan_routes.py:123-228 |
| G0-1d | `add_coin_to_collection` → `propose_add_coin` | main.py:2608-2639 |
| G0-2 | Most-recent fallback removed; disambiguation on ambiguous target | main.py:2692-2708 |
| G0-3a | Hard delete → trash move (deleted_at, deleted_by='morgan') | main.py:2738-2742 |
| G0-3b | `POST /api/coins/restore/{coin_id}` — 30-day window | morgan_routes.py:231-267 |
| G0-3c | INTERNAL_UNDO → undo-by-action-id, verified against log | main.py:2841-2895 |
| G0-4 | Action log written on confirm: who/action/coin_id/before/after | morgan_routes.py:214-225 |
| G0-5 | deep_dive cap 30/day; confirm cap 20/day; fail-closed 429 | main.py:2835-2836, morgan_routes.py:136 |
| G0-6a | `collection_inventory.py` strips ai_estimated_value/cost by default | collection_inventory.py:49,112-115,160-163,185-188 |
| G0-6b | Server-side keyword check for include_financial | main.py:2907-2911 |
| G0-6c | Financial strip in /api/ai/chat | ai_routes.py:117-130 |
| G0-7a | client collection_context ignored; server-built only | main.py:2938-2947 |
| G0-7b | Notes/OCR wrapped in data delimiter | morgan_routes.py:26-32, main.py:2933-2936 |
| G0-8a | Context capped at 50 coins; summary for larger collections | main.py:2920-2936 |
| G0-8b | `get_coin_details` function tool added | main.py:3123-3132, 2642-2657 |
| G0-9 | uid-vs-email already fixed by T1 (verified, skipped) | ai_routes.py:74-81 |

## Pytest counts
- Gate 0 suite (test_morgan_gate0.py): **9 passed**
- Full backend suite: **456 passed, 0 failed** (T1 baseline was 447)

## New file
`numista_backend/routes/morgan_routes.py` — propose, confirm, restore endpoints

## What's next
T3b Alt Site may begin once T3 UX lands on dev (T3b reuses T3 screens).
