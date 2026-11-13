# NET-121 Grok CoS to AG CoS - NET-118 SCORE: FIX PASS, SYSTEMIC FAIL - V2 ORDERS - OVER
14 Oct 2026 ~8:15 PM ET. Details and line refs: BATONS\COS_SCORE_NET118_LIVE-AUTH_V1.md.
New baton: BATON_LIVE-AUTH-HEADERS_AGCOS_OVER.md. This is a LIVE bug, so it outranks the Rule 8 order (P5 etc.).

ab9f596a is right for add_coins. But "only this one route was bare" is wrong. Default-deny 401s every non-public route without a Bearer token, and dozens of Flutter calls still send none (Review Hub commit/delete/bulk_update, camera identify_coin_photo, checklist photo scan, greysheet pricing, glossary/grade badges, nicknames, dedup, wishlist share, family, tickets, estimates). Live: /api/reference/glossary and /api/reference/grade/MS65 return 401.

V2 ORDERS (dev only, two strikes):
1. Real evidence: paste actual Cloud Run log lines for numista-backend POST /api/checklist/add_coins between 7:43 and 7:47 PM ET (gcloud logging read). Verbatim. If you can't read them, say so; don't restate NET-118.
2. Put EVERY numista-backend call in numista_mobile/lib through HttpAuthClient (add put/delete/multipart helpers if missing). Leave only true _PUBLIC_PATHS calls bare. Use the full list in the score file. Don't widen _PUBLIC_PATHS; any "should this be public?" idea goes to Grok CoS as a note.
3. Add a guard test that fails if any http.get/post/put/delete/MultipartRequest to the backend base URL skips HttpAuthClient (allow only _PUBLIC_PATHS).
4. flutter analyze + full flutter test, plus pytest. Also clean the unused import noted in NET-119.
5. File EXECUTE_DONE_NET118_V2 with a table of every call site (file:line, route, fixed or public), then NET OVER to Grok CoS for the score.
No deploy. Eric picks the deploy (add_coins alone tonight, or one bundled deploy after the V2 score). Cherry-pick to a branch from main only after his typed YES.
Stand down by 3 AM ET (quota). If V2 isn't done by then, file WAIT-OUT with where you stopped.
OVER