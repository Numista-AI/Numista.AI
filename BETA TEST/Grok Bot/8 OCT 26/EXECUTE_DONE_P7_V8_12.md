# EXECUTE_DONE: P7 V8.12 Build

**Date:** 2026-10-17 13:05 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `689e2ca1d65e598df4c01df0e3d436a2b8a1338a` (short: `689e2ca1`)  
**Git Push Target:** `origin/p7-v8.9` (pushed `3bcecde1..689e2ca1`)  
**Flutter Analyze:** 0 errors, 0 warnings (`No issues found! (ran in 3.9s)`)  
**Flutter Test:** 576/576 passed (+4 new tests over baseline 572)  

---

## 1. Summary of Changes & Fixes

| Item (NET-292 / NET-294) | Description | Verbatim File & Line Cites (`git show 689e2ca1`) | Verification |
|---|---|---|---|
| **Fix 1: Morgan Greeting Alignment** | Ask Morgan greeting uses same count and valuation source as Dashboard (312 coins / $2,224.36 estate mode default). Loads demo coins cache in demo mode, applies `expandCollection` for sets/quantities, calculates `finalBid` sum, forces fresh context on chat open, and updates opening message. | `numista_mobile/lib/services/morgan_chat_context.dart:185-188, 228-237, 361-366`<br>`numista_mobile/lib/screens/ai_chat_screen.dart:113-116, 156-161` | **PASS (code + unit test)**<br>Tested in `p7_v812_morgan_context_metrics_aligned_with_dashboard`: 6 expanded coins, $110 valuation, greeting matches |
| **Fix 2: PDF Report CORS & Mojibake** | Fixed preview origin CORS failure on scan service ('The Numista.AI server didn't answer'). Extended client timeout from 45s to 60s. Sanitized `£` (Pound sign) mojibake in PDF ReportLab generation tables. | `numista_backend/main.py:60-61`<br>`numista_backend/scan_service/main.py:78-88, 96-100, 119-123`<br>`numista_backend/scan_service/estate_pdf_builder.py:104-115, 1005-1006`<br>`numista_mobile/lib/screens/my_collection_screen.dart:6070-6073` | **PASS (code)**<br>`ALLOWED_ORIGIN_REGEX` matches `numista-vault--*.(web.app\|firebaseapp.com)`. `fix_mojibake()` handles double-UTF8 & Latin-1 encoding for `£` in PDF canvas |
| **Fix 3: CSV/JSON Export Full Fields & Clean Format** | Added missing `Qty`, `Retailer`, `Invoice`, and `Notes` columns. Sanitized `Year` to int (no `.0`), `Cost` to uniform `$XX.XX`, `Qty` to int (>= 1), and `Added` to readable `yyyy-MM-dd` date. | `numista_mobile/lib/services/backup_export_service.dart:85-112, 156-172, 186-197, 199-208, 228-257` | **PASS (code + unit test)**<br>Tested in `p7_v812_csv_export_formatting_and_missing_columns`: Year `2017`, Qty `3`, Cost `$15.50`, Added `2024-10-17`, all 16 columns present |
| **Fix 4: News Feed CORS Guard on Preview** | In demo mode or on non-production web origins (`!isAllowed`), `MarketNewsService.fetchNewsFeed()` avoids external HTTP calls and returns cached/bundled news safely. | `numista_mobile/lib/services/market_news_service.dart:52-62` | **PASS (code + unit test)**<br>Tested in `p7_v812_market_news_service_preview_origin_guard` |
| **Fix 5: Stream Re-Listen Tab-Switch Replay** | Converted `GuestSeedService.getDemoCoinsStream()` and `WorldItemService.worldItemsStream()` to `Stream.multi(..., isBroadcast: true)` to replay latest cached value to all new/subsequent subscribers. Added `cachedDemoSnapshot` & `cachedDemoWorldItems` initialData in `my_collection_screen.dart`. | `numista_mobile/lib/services/guest_seed_service.dart:28-36, 136-140`<br>`numista_mobile/lib/services/world_item_service.dart:480-496, 509-513`<br>`numista_mobile/lib/screens/my_collection_screen.dart:1401-1404, 1414-1417` | **PASS (code + unit test)**<br>Tested in `p7_v812_guest_demo_stream_multi_listener_replay`: multiple listeners replay data without hanging |

---

## 2. Verification Commands & Outputs

1. **`flutter analyze lib/`**
   ```
   Analyzing lib...
   No issues found! (ran in 3.9s)
   ```
   0 errors, 0 warnings.

2. **`flutter test --reporter compact`**
   ```
   00:22 +576: All tests passed!
   ```
   Baseline: 572 -> 576 (+4 new automated tests). 100% passed.

3. **`git push origin p7-v8.9`**
   ```
   To https://github.com/Numista-AI/Numista.AI.git
      3bcecde1..689e2ca1  p7-v8.9 -> p7-v8.9
   ```

---

## 3. Review File
- Full code review with verbatim citations: `BETA TEST/Grok Bot/8 OCT 26/BATONS/GEMINI38_REVIEW_P7_V8_12_BUILD.md`
