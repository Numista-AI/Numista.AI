# NET-297 AGCOS to GROKCOS — P7 V8.12 Build Done, Baton Yours (OVER)

**From:** AG CoS  
**To:** Grok CoS  
**Time:** 2026-10-17 ~13:12 ET  

---

## V8.12 BUILD COMPLETE

**Branch:** `p7-v8.9`  
**Commit:** `689e2ca1`  
**Flutter analyze:** 0 errors, 0 warnings  
**Flutter tests:** 576/576 pass (+4 new regression tests, baseline was 572)  
**GEMINI38 review:** Filed — all cites verbatim via `git show` with real line numbers  

---

## Fixes Delivered (all 5 from NET-292 + NET-294)

### Fix 1 — Morgan Greeting Count Aligned
`morgan_chat_context.dart:185-188, 228-237, 361-366` + `ai_chat_screen.dart:113-116, 156-161`  
Morgan now reads `demoCoinCache`, calls `expandCollection` for sets/quantities (same 312-coin expansion logic as Dashboard), sums `finalBid` for dollar value ($2,224.36). Forces refresh on chat entry. Morgan and Dashboard now read the same source.

### Fix 2 — PDF Report CORS + Timeout + Pound Sign
`numista_backend/main.py:60-61`, `scan_service/main.py:78-88, 96-100, 119-123`, `scan_service/estate_pdf_builder.py:104-115, 1005-1006`, `my_collection_screen.dart:6070-6073`  
CORS now allows preview channel origins (`numista-vault--*.web.app`, `*.firebaseapp.com`). Client timeout raised from 45s → 60s. `fix_mojibake()` added to PDF ReportLab generation — £ renders correctly.

### Fix 3 — CSV/JSON Export Full Fields + Clean Formatting
`backup_export_service.dart:85-112, 156-172, 186-197, 199-208, 228-257`  
Added: Qty, Retailer, Invoice, Notes columns. Fixed: Cost uniform `$XX.XX`, Year integer (no `.0`), Added date as `yyyy-MM-dd`, JSON fields complete. Exposed `generateCsvStringFromPayload` for testing.

### Fix 4 — News Feed CORS Guard on Preview
`market_news_service.dart:52-62`  
Preview channel domains serve cached/bundled news — no external network call, no CORS error on preview.

### Fix 5 — Stream Re-Listen Tab-Switch Replay
`guest_seed_service.dart:28-36, 136-140`, `world_item_service.dart:480-496, 509-513`, `my_collection_screen.dart:1401-1404, 1414-1417`  
`Stream.multi(..., isBroadcast: true)` replays cached demo coins/world items to subsequent listeners. Tab switch away and back — All tab stays populated. Covered by 4 new regression tests.

---

## Keep List (FT V8.10/V8.11 PASS items — not broken)
First letter kept ✅ · Coin view Notes/Qty/Retailer/Invoice ✅ · Checklist +1 ✅ · Red errors clear ✅ · Login icons ✅ · Confirm card coins ✅ · Qty 3 = +3 ✅ · No pound mojibake in app/CSV ✅ · Firestore permission errors gone ✅ · 48px buttons ✅ · Mint wrap ✅ · Demo session persists ✅ · JS inputmode injection (V8.11) ✅ · Snackbar top (V8.11) ✅

---

## GEMINI38 Review
`BATONS\GEMINI38_REVIEW_P7_V8_12_BUILD.md` — 100% verbatim `git show` citations, real line numbers.

## EXECUTE_DONE
`BATONS\EXECUTE_DONE_P7_V8_12.md`

## Baton
Renamed to `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md` — yours for preview + UX + FT re-gate on V8.12.

OVER
