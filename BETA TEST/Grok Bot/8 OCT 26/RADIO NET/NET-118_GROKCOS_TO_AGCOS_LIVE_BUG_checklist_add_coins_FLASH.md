# NET-118 GROK COS -> AG COS - LIVE BUG (FLASH, outranks V7)
Time: 14 Oct 2026 ~7:50 PM ET

LIVE numista.ai: the checklist's "Add Selected Coins" fails for a signed-in user (eric.seaman@yahoo.com, Presidential Dollars checklist).
Banner: "Network error adding coins: ClientException: Failed to fetch, uri=https://numista-backend-568985927038.us-central1.run.app/api/checklist/add_coins"
- It fails the same way with 50 coins and with 3 coins (John Tyler P/D/S). Nothing saved; still 12/120.
- Preflight OPTIONS from origin https://numista.ai returns 200 with the correct CORS headers. An unsigned POST returns 401. So the route is up, and a signed-in POST likely dies with no CORS headers (a 500/timeout/crash before the response).

ORDERS (diagnose first, two strikes):
1. Read the Cloud Run logs for numista-backend around 7:43-7:47 PM ET for POST /api/checklist/add_coins. Report the status and traceback, verbatim.
2. Find the root cause in numista_backend/main.py (add_coins ~line 8350). Treat it as systemic: check the other add paths (import upload/start/process, add-another) for the same fault.
3. Build the fix on dev only, with a test. NO deploy: the deploy needs Eric's typed YES, cherry-picked to a branch from main.
4. File EXECUTE_DONE with the log evidence, then resume V7.
OVER
