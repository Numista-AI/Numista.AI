# COS SCORE - T3b Alt Site Phase A BUILD (REQ_032B)
Scored by: Grok CoS, 12 Oct 2026 ~5:58 PM ET. Commit scored: 84a1f361 on dev (doc commit 5fa75bd6 on top).
My run: `pytest tests/test_ui_variant.py` = 12 passed. Full-suite 468 / Flutter 432 counts taken from EXECUTE_DONE, not re-run.

## Verdict: ITERATE

Good: GET /api/user/ui_variant is token-authed and server-gated (main.py:248-270); allowlist is Eric's two accounts only (main.py:225); non-allowlist 'alt' degrades to classic (main.py:267); admin-only setter (main.py:228); client reads the API, not Firestore (ui_variant_service.dart:12-24); reset on sign-out (auth_gate.dart:121, base_layout.dart). Phase B/C not built. Correct.

### Required fixes
1. **Plan fix #2 is NOT met - clients can still write settings/ui_variant.** Firestore rules are OR'd: if any matching block allows, the write is allowed. The new `match /users/{email}/settings/{doc}` with `allow write: if false` (numista_backend/firestore.rules:31-33; numista_mobile/firestore.rules:93-95) is overridden by the owner wildcard `match /users/{email}/{document=**}` with `allow read, write: if isOwner(email)` (backend :39-40; mobile :108-109). Phase A is still safe only because the server re-checks the allowlist (main.py:267) - that won't hold for Phase B/C.
2. **Systemic (Eric's rule - check every related feature):** the same wildcard overrides EVERY "stricter" block under users/{email}: estate_reports `write: if false` (mobile :24-27, backend :24-27), coins field guards (mobile :41-64), profile guards (mobile :77-81). The comment at mobile :105-107 ("more-specific match blocks above enforce field-level guards") is wrong. Fix: change the wildcard so it excludes protected subcollections (e.g. `match /users/{email}/{sub}/{document=**}` with `allow write: if isOwner(email) && !(sub in ['settings','estate_reports','coins','profile', ...Morgan action log / any server-only path])`), then audit T2's Morgan action-log / soft-delete paths for the same hole. Rules change = dev only; deploying rules needs Eric's typed YES.
3. **Plan asked for a rules test; none added.** numista_mobile/firestore.rules.test.js has no settings/ui_variant case (0 matches; file last changed 31 Aug). Add emulator tests: owner write to settings/ui_variant DENIED, owner write to estate_reports DENIED, coin field-guard violations DENIED. These tests would have caught #1.
4. ui_variant_service.dart:17-21 - non-200 keeps the previous value. Set `_current = UiVariant.classic` on any non-200 (fail-safe both paths).
5. Banner text uses textCaption = 12 (base_layout.dart:1336; numista_theme.dart:7) - under the 14 floor already flagged in T3 ITERATE. Folds in with T3 fix #2.
6. EXECUTE_DONE accuracy: says "Phase A: Eric + AJ only" but code allowlist is Eric's two accounts (main.py:225) - code is right, doc is wrong; also cites main.py:247 for the allowlist (actual :225). Correct the doc.

Ball: AG CoS - fix on dev, re-file EXECUTE_DONE. No deploy, no live writes, no rules deploy without Eric's typed YES.
