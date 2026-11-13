# NET-425 | GROKCOS to AGCOS | TOP PRIORITY: Argon RCA on vanishing grokbot coins (READ-ONLY), then add FT items to V8.18.15b Plan.v1
Filed 2026-10-22 10:20 ET. Eric's direct order. Adds to NET-424. Baton stays AGCOS (BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md).
FT report: BETA TEST\Grok Bot\22 OCT 26\FT_P7_GATE_V8_18_15a.md (OVERALL FAIL).

## 0. TOP PRIORITY, before any other V8.18.15b item: Gemini 4 Argon root-cause analysis
Symptom: on grokbot, FT committed 34 coins (2 invoice runs x 17 rows) through the p7gate backend; count went 312 -> 346, then back to 312 within minutes with nobody deleting. Totals also moved: cost 951.59 -> 946.87, melt 2197.76 -> 2187.13, so rows other than the 34 may have changed.
Argon is READ-ONLY: read code, Cloud Run logs and scheduled jobs. NO data writes, NO restores, NO deploys, NO raw Firestore writes, grokbot data only.
Deliverable: BETA TEST\Grok Bot\22 OCT 26\ARGON_VANISHING_COINS_RCA.md with evidence (file:line, log lines), the root cause, whether it can hit REAL user collections (systemic yes/no + why), and a proposed fix for the plan.

### Grok CoS findings already done (do not repeat; build on them)
Window checked 13:30-14:15 UTC (9:30-10:15 AM ET), project studio-9101802118-8c9a8.
1. Only ONE write call: POST /api/review/commit 200 at 13:55:07Z (9:55 ET) on numista-backend-00482-laj (p7gate). No other non-GET requests except /api/scan_cert_number_upload and /api/deep_dive.
2. NO HTTP DELETE, no /api/dedup_sweep, no /api/dedup_sweep/auto_clean, no delete-all-coins call on p7gate 00482-laj OR live 00479-beg in the window. Live 00479-beg only logged an instance shutdown at 14:02:37Z.
3. No text logs matching delete/dedup/cleanup/reset/rollback/purge on numista-backend after 13:30Z.
4. No other Cloud Run service, job or function logged anything 13:55-14:15Z.
5. Cloud Scheduler: none ran in the window. scraper-every-3-hours last 13:00Z (before the commit, next 16:00Z); nightly-bq-load 11:00Z; nightly-firestore-export 10:00Z; daily-scraper 01:00Z; numista-sync-monthly 1 Oct; weekly-image-index 18 Oct. Functions: onFeedbackCreated, app (ACTIVE), annotate_gcs/annotate-http (UNKNOWN). Run jobs: numista-bq-loader, numista-data-sync.
6. Firestore Data Access audit logs are NOT enabled (no firestore.googleapis.com entries), so a client-SDK delete or overwrite would leave no server log.
Conclusion so far: no backend endpoint or scheduled job deleted the coins. Remaining suspects for Argon:
  a. commit_reviews main.py:3510-3623 writes coins_ref.document(doc_id) with the review_queue doc_id (line 3610-3611, batch.set). If invoice-import queue IDs are deterministic or reused, a commit can OVERWRITE existing coins (would explain cost/melt changing on other rows). Also check the duplicate branch at line 3588 and the second batch.commit at 3617/3622.
  b. Client-side Firestore SDK writes/deletes from the web/Flutter app or another open session/tab (no server log). FT console showed Firestore Listen errors: check whether the 346 was an optimistic/local view and the listener fell back to a cached 312 snapshot (i.e. coins never persisted or were written under a different owner doc, e.g. uid fallback at main.py:3517-3518 vs users/<email>).
  c. Import staging cleanup import_routes.py:275 and scan_routes.py:74 (batch.delete), and the review/commit_session route scan_routes.py:290.
  d. Dedupe logic main.py:3882-4060 (attr key year/mint/denom/series/theme/cond/date when invoice # is blank; FT's rows had Invoice # N/A) - admin-only and not called in the window, but check every other caller of the same grouping.
  e. Test-account reset logic for grokbot/demo anywhere (backend, functions "app", numista_tests).

## Then add these Field Tester items to PLAN_P7_V8_18_15b.v1.md (with NET-424 Fix 1, Fix 2, NGC wording)
a. U.S. Mint invoice PDF: run A shows "Error" with no text; run B sticks at "Processing 0/1" and polling stops at ~17 s; every coin lands QTY 1; Retailer, Invoice # and Date are N/A. Fix: real error text, polling until done/fail with a timeout message, parse quantity and invoice header fields. Invoice/receipt PDF scanning is must-keep.
b. Cert-photo scan takes 60-100 s and fails ("Couldn't read a cert number"). Same as NET-424 Fix 2. LOG EVIDENCE: 14:10:03Z and 14:12:05Z "WARNING:numista_backend.deps:extract_cert_from_image failed: Unterminated string starting at: line 1 column 17 / column 174" right after a gemini-3.8-flash generateContent 200 that took ~34 s and ~30 s. The model reply is truncated/non-JSON and the parse fails: check max output tokens, response schema/JSON mode, AFC (logs show "AFC is enabled with max remote calls: 10"), and image size.
c. Console: CORS errors on storage.googleapis.com reference images, and Firestore Listen errors. Find the cause (bucket CORS for the preview origin, signed URLs, listener rules/auth) without changing the live site unless that change is intentionally shared and called out.
d. The vanishing-coins fix from Argon's RCA, if the cause is in code. Plan it as its own item with a regression test.

## Rules
Dev/preview only on p7-v8.9. Plan first; Grok CoS scores before execution. No deploys, main untouched, no live data writes, no restores, grokbot/demo only, no NGC scraping, don't push past the PCGS block, no git commit -a, phone-only fixes gated !kIsWeb && (Platform.isAndroid || Platform.isIOS). Eric will type "check radio".
OVER
