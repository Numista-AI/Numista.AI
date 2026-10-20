# NET-389 GROKCOS -> AGCOS: PORT importer auth fix into p7-v8.9 (V8.18.12)
DTG: 20 OCT 26 ~5:20 PM ET. Priority: add to the V8.18.12 fix list (NET-387), item 1 alongside the invoice 'list'.get crash.

## Situation
Live Bulk Import (add_coins.html) fails "Failed to fetch". Cause: upload/process/status fetches send NO Firebase ID token -> backend 401 "Authentication token missing or invalid" with no CORS header -> browser shows CORS / Failed to fetch.
Also: GreySheet release (7e4424a0) was cut without 34d63d60, so live add_coins.html is back on the OLD Firebase appId/apiKey.

## Live hotfix (prepared, NOT deployed)
Branch hotfix/importer-auth-header (from 7e4424a0): c3e24a24 (cherry-pick of 34d63d60 key fix) + 81a21ecc (auth). PR #267, do not merge.
Preview: https://numista-vault--importer-auth-gv7jjhmu.web.app (expires 27 OCT 26).

## Order to AG: port to p7-v8.9, numista_mobile/web/add_coins.html only
p7-v8.9 already has the web appId (OK). It still lacks auth on fetches. Apply the 81a21ecc diff:
1. Add SIGN_IN_AGAIN_MSG, AuthError, requireAuthHeader() (awaits window._fbUserReady via getAuthHeader, throws if no token), checkAuthResp() (401/403).
2. /api/import/upload: headers: await requireAuthHeader(); checkAuthResp(resp).
3. /api/import/process: headers: Object.assign({'Content-Type':'application/json'}, await requireAuthHeader()); checkAuthResp.
4. /api/import/status poll: { headers: await getAuthHeader() }; on 401/403 stop polling + friendly message.
5. /api/receipts list + view_url: on 401/403 friendly message.
6. catch: AuthError -> "Please sign in again..."; TypeError -> "Could not reach Numista.AI... sign in again and retry."
Reference: git show 81a21ecc -- numista_mobile/web/add_coins.html
Also check any other non-Flutter HTML page that calls the backend with bare fetch().
Backend follow-up (separate, dev only): 401 responses lack Access-Control-Allow-Origin; add CORS headers on error responses so the browser can read them.
Explicit paths only. No git commit -a. Dev only. OVER.
