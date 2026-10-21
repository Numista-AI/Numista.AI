# COS SCORE - P7 GATE V8.18.12 (p7-v8.9 @ 68c03e45, parent 65072e6f) - PASS (code gate) -> UX + FT re-gate
Scored by GROKCOS, 2026-10-20 ~8:10 PM ET. AG NET-392, GEMINI38 PASS. Live untouched (backend 00472-roc 100%).

## Preview
- Web: https://numista-vault--p7-gate-8avtpz22.web.app (expires 27 OCT 26), build shows 8.18.12, API_BASE = p7gate tag.
- Backend: numista-backend-00476-hol, tag p7gate, 0% traffic: https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app
- Bulk Import page: add `?api=https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app`
- Smoke: unauthenticated /api/receipts from preview origin -> 401 WITH Access-Control-Allow-Origin (browser can now read the error).

## Tests (clean worktree at 68c03e45)
- flutter analyze: 0 errors/warnings, 2 infos (depend_on_referenced_packages in tests).
- flutter test: 604 passed.
- pytest: 587 passed, 4 failed - same 4 fail at parent 65072e6f (pre-existing env/data: test_identify_timeout project_id import, missing_images_csv x2, usmint local catalog). No regressions; +2 new invoice tests pass.

## Rules review (both firestore.rules)
- config/ebay and config/{document=**}: read = signed-in AND (doc missing OR no cert_id). Writes still false. Only effect: reading a NON-EXISTENT config doc no longer throws permission-denied (fixes EPN load). cert_id docs still unreadable. OK.
- EXTRA change, numista_mobile/firestore.rules only: beta_feedback `allow list` widened from admin-only to admin OR owner (resource.data.user_id == auth.uid). Owner-scoped; queries must filter on user_id, so no cross-user read. Not in the ask; acceptable but noted. Backend copy of rules does not have it (rules files drift).

## NET-387 / NET-389 checklist (code present; behavior to be confirmed by UX/FT)
1. Invoice 'list'.get crash: FIXED in main.py ~7704 (normalizes list/non-dict Gemini output, fallback keys, clean_valuation_value) + tests/test_invoice_fixtures.py.
2. EPN permission-denied: rules resource==null + epn_service guard.
3. Cert UX / CACG OCR prompt: cert_routes.py prompt + add_coins_hub.dart.
4-7. Camera copy, sizing, 'back of coin not photographed', input lag, settings rename: in diff.
NET-389 importer auth: add_coins.html has requireAuthHeader/checkAuthResp/SIGN_IN_AGAIN (13 refs).

## Live crash path (AG claim)
TRUE. Live 7e4424a0 numista_backend/main.py line 7350 (not ~7125): `items = data.get("line_items", [])` with no list guard; float(data.get("subtotal")) follows. hotfix/importer-auth-header (81a21ecc) does NOT touch this; it fixes auth headers only. Live invoice import will still crash on a list response after the auth hotfix. Needs the 68c03e45 main.py hunk (lines 7701-7739) cherry-picked to the hotfix - Eric YES required.

## Verdict: PASS code gate. Next: UX Designer + Field Tester (grokbot only) re-gate. No Eric YES request until FT check 1 (invoice PDF adds coins) passes.
