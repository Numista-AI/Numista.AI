# ACK NET-039 — AG CoS

**ACK'd:** 2026-10-13 ~16:44 ET

## Initial findings

### P0 — CORS on /api/spot_prices: FIXED in code
- **Root cause confirmed:** `/api/spot_prices` was not in `_PUBLIC_PATHS` (main.py:129-152).
  - `home_dashboard.dart:249` calls `http.get(Uri.parse('$kApiBaseUrl/api/spot_prices'))` — **no auth header**.
  - Default-deny middleware (main.py:171) rejects unauthenticated requests. OPTIONS pass through (line 179), but the subsequent GET returns 401 — and that 401 lacks the CORS headers because the middleware short-circuits before CORS runs.
- **Fix applied:** Added `"/api/spot_prices"` to `_PUBLIC_PATHS` at main.py:152.
  - Code verbatim: `"/api/spot_prices",  # Metal spot prices — called unauthenticated from home_dashboard.dart before sign-in`
  - Data is non-sensitive (yfinance commodity prices, no PII).
- **Tests needed:** Add pytest for OPTIONS preflight on protected route returning CORS headers, and for `/api/spot_prices` returning 200 without auth.

### P1 — Flutter web build
- PR #258 used cherry-pick of 9 SHAs onto `deploy/unified-bundle` (separate from dev). The T3/T3b UX fixes (font tokens, PIN box, nav changes) were in commits `9a0b20b8`, `e6b808f7` which were cherry-picked. Investigating whether the GitHub Actions build ran correctly from those cherry-picks.
- FT report: "v4.403, both old and new nav show, small text" — this suggests either (a) the build wasn't triggered, (b) the cherry-pick missed a UX commit, or (c) browser cache.

### P2 — Morgan Undo not shown after confirm
- The `_buildAddedCoinCard` widget (ai_chat_screen.dart:747+) shows the Undo button based on `action_payload['coin_id']`. After the proposal Confirm flow, the backend returns `{"status": "success", "coin_id": ..., "action": "add_coin"}` but the chat message may not be structured with the right `action_payload` type to trigger `_buildAddedCoinCard`.
- Root cause: the Confirm button (in `_buildConfirmationCard`) fires `INTERNAL_CONFIRM` but the response from `/api/deep_dive` after confirm may not include `action_payload.action == 'added_coin'`.

### P2 — Firestore onSnapshot failures
- Rules look correct: all subcollections allow owner read. Likely caused by CORS/401 cascade on backend calls which affects the app state, OR the app is trying to `snapshots()` on `morgan_proposals` which is server-only write (but read-allowed). Need to check console errors more carefully.

### P3 — Home page blank
- Likely caused by CORS/401 on `/api/spot_prices` + possibly `/api/reference/stats`. With P0 fixed, home page should load. Will re-smoke after deploy.

## Next actions
1. Run pytest with new spot_prices test
2. Write GEMINI_REVIEW doc with verbatim code quotes
3. Push to dev, request cherry-pick deploy with Eric's YES
4. Investigate P1 (Flutter build) and P2 (Morgan Undo) — may need additional commits

AG CoS OVER
