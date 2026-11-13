# DEPLOY_DONE P7 V8.18.15i QTY one-row Qty=N — LIVE

- **When:** 24 Oct 2026 ~6:34 PM ET
- **Eric YES:** typed tonight — live of tip `6ee3de89` (QTY fix). 48h Mint-ready ceiling Mon 26 Oct ~6:32 PM ET (ceiling, not delay).
- **Gate:** NET-497 FT OVERALL PASS; COS_SCORE_P7_GATE_V8_18_15i GATE PASS; Argon NET-494 PASS.

## What shipped (backend-only traffic shift)
- **Live backend:** `numista-backend-00487-hub` at **100%** traffic (same revision FT gated via p7gate).
- **Source tip:** `6ee3de89` on `origin/p7-v8.9` (surgical QTY: `main.py` + 2 tests vs `72cb6c0f`).
- **Tags kept:** `p7gate` → 00487-hub; `greysheet` → 00472-roc.
- **Rollback:** `numista-backend-00479-beg` (still present; prior live 100%).
  `gcloud run services update-traffic numista-backend --region us-central1 --project studio-9101802118-8c9a8 --to-revisions numista-backend-00479-beg=100`
- **Hosting / Flutter:** **not** redeployed. Live `numista-vault` / `add_coins.html` already has importer auth (21 Oct) and `getIdToken`; `main.dart.js` has **0** `p7gate` refs; API host `numista-backend-568985927038.us-central1.run.app` (same Cloud Run service → now 00487).

## Aborted path (do not retry without new plan)
- Branch-from-main + `git checkout 6ee3de89 --` only 3 files: **unsafe**. Tip `main.py` imports `cert_routes` + `duplicate_check` absent from `origin/main`. Would crash or regress.
- No PR merge to main tonight (SOP: importer-auth #267 / greysheet #266 left open — merge triggers CI redeploy). `origin/main` remains `3c1bacf5`.

## Required for next main merge (still owed — from DEPLOY_LOG_IMPORTER_AUTH_HOTFIX_2026-10-21.md)
Do not lose these live hotfixes when eventually syncing main:
- `c3e24a24` web Firebase apiKey/appId in add_coins.html
- `81a21ecc` Firebase ID token on backend fetches; friendly 401
- `0cf28dd1` Gemini list/multi-block line_items normalize; list_receipts session filter
- `98529d5d` CORS regex for numista-vault--*.web.app preview channels
- `79581352` CORS headers on default-deny 401
Plus greysheet bid-display commits on `hotfix/greysheet-bid-display` / PR #266 if not already ported into the tip tree that built 00487.

## Smoke (live) — all PASS ~6:34 PM ET
| Check | Result |
|---|---|
| https://numista.ai/ | 200 |
| https://numista-vault.web.app/ | 200 |
| backend `/` (qntvrqvxma + 568985927038 hosts) | 200 |
| `/api/spot_prices` | 200 |
| `/api/collection` unsigned | 401 |
| `/api/receipts` unsigned + Origin numista-vault.web.app | 401 + `Access-Control-Allow-Origin: https://numista-vault.web.app` + credentials true |
| Traffic map | 100% 00487-hub; greysheet tag 00472; p7gate tag 00487 |
| main.dart.js p7gate refs | 0 |

## FT cleanup
Grokbot test coins from NET-497 may be cleaned when convenient (WAKE / NET-499). No collection writes by CoS.
