# DEPLOY LOG: Importer auth hotfix, LIVE, 21 Oct 2026

Authorization: Eric typed YES at 8:46 AM ET (test copy first, Field Tester check, then live). Field Tester PASS 5/5 on 00479-beg.
Live at about 9:30 AM ET.

## Backend (Cloud Run numista-backend, project studio-9101802118-8c9a8)
- LIVE: numista-backend-00479-beg, 100% traffic. Code = hotfix/importer-auth-header HEAD 79581352.
- ROLLBACK: numista-backend-00472-roc (tag greysheet kept).
  `gcloud run services update-traffic numista-backend --region us-central1 --to-revisions numista-backend-00472-roc=100`
- importerauth tag removed after live.

## Hosting (site numista-vault)
- LIVE release: 1792589392840000 (9:29 AM ET), built from stage_importer_auth2 with the backend URL swapped back to live. Checked first: 0 'importerauth' strings remain.
- ROLLBACK release: 1792529216899000 (20 Oct, 4:46 PM ET, GreySheet hotfix).

## Live smoke test: all PASS
- numista.ai / 200, numista-vault.web.app / 200, main.dart.js 200
- add_coins.html contains getIdToken
- signed-out /api/receipts: 401 with Access-Control-Allow-Origin https://numista-vault.web.app plus credentials true
- /api/spot_prices 200

## Branch / PR
- PR 267 (hotfix/importer-auth-header) NOT merged. Merging triggers a CI redeploy, so it is left for Eric. main untouched (3c1bacf5).

## REQUIRED for the next P7 release
The next P7 release MUST include these commits, or it will regress live:
- c3e24a24: web Firebase apiKey/appId in add_coins.html
- 81a21ecc: Firebase ID token on all backend fetches, friendly 401
- 0cf28dd1: Gemini list/multi-block line_items normalize; list_receipts session filter with Python sort
- 98529d5d: CORS regex for numista-vault--*.web.app preview channels
- 79581352: CORS headers on the default-deny 401
