# COS SCORE - NET-118 LIVE AUTH FIX V2 (f55a11de) - SYSTEMIC
Scored by Grok CoS, 14 Oct 2026 ~9:18 PM ET (evening watch). Ref: NET-121 orders, NET-123, 14 OCT 26\EXECUTE_DONE_NET118_V2.md.

## Result: PASS (code). Deploy needs Eric's typed YES (decision already put to Eric ~8:15 PM ET).

## Checked independently (not taken from AG's report)
1. Log evidence (order 1): PASS. Grok CoS ran gcloud logging read on studio-9101802118-8c9a8 / numista-backend for 23:43-23:47 UTC itself. Real rows: 23:45:36.912145Z OPTIONS 200, 23:45:37.032520Z POST 401, 23:45:54.629052Z POST 401, 23:46:27.29Z POST 401, 23:47:36.739Z POST 401. AG's quoted timestamps match the real ones (one is 6 ms off because it came from the stdout entry). The evidence is real this time.
2. Call-site coverage (order 2): PASS. 25 files changed (+354/-336). Grok CoS scanned all of numista_mobile/lib for bare http.get/post/put/delete/patch/head/read, http.Request, http.MultipartRequest, http.Client() and .send(. Remaining bare calls:
   - coin_detail_screen.dart:313 GET on the coin image URL (external CDN image for Gemini). OK.
   - epn_service.dart:89 api.ebay.com with its own eBay Bearer. OK.
   - numista_service.dart:14, 38 api.numista.com. OK.
   - pcgs_import_service.dart:114/153/182 api.pcgs.com/publicapi with the user's PCGS token. OK.
   - morgan_feedback_session.dart:302 http.Request POST $kApiBaseUrl/api/ai/chat/stream. Sets the Firebase Bearer itself (lines 289-303). OK (streaming).
   No bare numista-backend call is left.
3. HttpAuthClient: patch + multipartPost added. Leaving out the token when signed out is OK for public /api/spot_prices. The form-encoded calls (dedup_sweep etc.) set the urlencoded Content-Type, so http bodyFields won't throw. Spot-checked settings_screen.dart:1660.
4. Guard test (order 3): PASS with gaps (not blocking, see notes).
5. Tests (order 4): Grok CoS re-ran on dev HEAD 88bb9aaf. flutter analyze lib: No issues found. flutter test: 510/510 All tests passed. Grok CoS did not re-run pytest (no backend change in f55a11de). AG reports 62/62.
6. EXECUTE_DONE table (order 5): PASS, with file:line, route and status for each call.

## Not blocking (later, NOT tonight)
- N1 Guard test: the backend-name list is case-sensitive, so 'baseUrl' misses '_backendBaseUrl'. It also doesn't scan http.Request( / client.send(. Tighten it in the next batch that touches lib.
- N2 HttpAuthClient.multipartPost never closes the http.Client it creates (small leak). Close it in finally as the other helpers do.
- N3 Should /api/reference/* (glossary, grade badges) be public for signed-out visitors? That is a product question for Eric/Grok CoS. Don't widen _PUBLIC_PATHS without that decision.

## Deploy
Eric picks: (a) add_coins only (ab9f596a), or (b) one bundle with V2 (f55a11de). Grok CoS recommends (b): it fixes every 401 path at once. Cherry-pick to a branch from main only after Eric's typed YES. Eric was already asked ~8:15 PM ET (_ERIC_PINGED_LIVE-AUTH_DEPLOY_PICK_2026-10-14.md). No overnight re-ping: the live site is up.