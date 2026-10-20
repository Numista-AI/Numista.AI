# GreySheet bid-display hotfix - DEPLOYED LIVE (Grok CoS)
20 Oct 2026, 4:47 PM ET. Authorized by Eric's typed YES (4:35 PM ET).

Branch: hotfix/greysheet-bid-display = origin/main 3c1bacf5 + 6370c65c, 1ddb1d1f, 44f8604d (16 files, verified) + 7e4424a0 (firebase.json SW header order).
PR: https://github.com/Numista-AI/Numista.AI/pull/266 - OPEN, DO NOT MERGE without Eric (merge triggers CI redeploy). Dev NOT merged into main.

Backend: numista-backend-00472-roc (tag greysheet) at 100%. Rollback: 00465-xx7.
  gcloud run services update-traffic numista-backend --region us-central1 --project studio-9101802118-8c9a8 --to-revisions numista-backend-00465-xx7=100
Hosting: release 1792529216899000. Rollback target: 1792502930550000 (live 13:28 UTC 20 Oct).
Scan service: not changed, not redeployed. p7gate tag/channel untouched.

Smoke (live): / 200, /privacy 200, /terms 200, /login 200, /api/spot_prices 200, /api/collection 401 unsigned.
main.dart.js: "Bid:" 0 (was 1), "Wholesale Bid" 0 (was 1). Service worker now no-cache (was immutable 1 yr).
Not smoke-tested signed-in: /api/greysheet/deals (401 unsigned); covered by unit tests.

Leftover: settings_screen.dart:1451/1471 toggle text still says "Greysheet Bid" (Estate/Liquidation View). Next small fix.
Built with Flutter 3.41.5 (engine 052f31d1) - full bundle, engine now 052f31d1 live.
