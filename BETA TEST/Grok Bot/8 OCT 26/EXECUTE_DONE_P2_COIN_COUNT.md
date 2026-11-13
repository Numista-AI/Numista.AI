# EXECUTE_DONE — P2 Coin Count Single Source of Truth
**Filed by:** AG CoS (Gemini 3.8)  
**Date:** 2026-10-14  
**Ref:** NET-070 / Baton `BATON_P2_COIN-COUNT-MISMATCH`  
**Status:** **COMPLETE — READY FOR GROK COS BUILD REVIEW**

---

## 1. Summary of Changes
Resolved the discrepancy across surfaces (`313 / 311 / 284 / 314`) by establishing `expand_collection_inventory` / `expandCollection` and `count_coins_and_lots` as the single canonical source of truth for counting physical coins across both frontend Flutter and backend FastAPI surfaces.

- **311 (Authoritative):** 280 loose coins + 31 child coins from 4 sets = 311 physical coins. Set parents (4), paper currency (2), and supplies (1) are correctly excluded from the coin count.
- **284 (Header Stats Bar Bug):** Header stats bar was displaying raw unexpanded parent documents count (`${widget.docs.length} coins`) when unfiltered. Fixed to display `${widget.totalCoinsCount} coins` (311) when unfiltered, and `'$filteredCount of ${widget.totalCoinsCount}'` when filtered.
- **313 / 314 (Home Dashboard Conflation):** `home_dashboard.dart` had computed `totalItems = totalCoins + currency.length + worldItems.length` and passed `totalItems` into metric cards labeled `'Total Coins'`, Morgan dashboard greeting widget, and portfolio snapshot service. Fixed to pass canonical `totalCoins` (`expansion.totalCoins`) to all coin metrics and Morgan greetings.
- **Backend Daily Snapshot & Collection Count:** Synchronized backend `/api/portfolio/snapshot/daily` and `/api/collection/count` to both use `expand_collection_inventory` and `count_coins_and_lots(inventory)["total_coins"]`.

---

## 2. Modified Files
1. `numista_mobile/lib/screens/home_dashboard.dart`
   - Split `totalCoins` from `totalItems`.
   - Wired `totalCoins` to `_metricCard('Total Coins')`, `_metricCardFlex`, `PortfolioSnapshotService.maybeTakeSnapshot`, and `_MorganDashboardCard`.
2. `numista_mobile/lib/widgets/header_stats_bar.dart`
   - Imported `set_expansion_helper.dart`.
   - Fixed count chip to render `${widget.totalCoinsCount} coins` when unfiltered.
   - Calculated `filteredCount = expandCollection(...).totalCoins` for filtered views.
3. `numista_mobile/lib/screens/my_collection_screen.dart`
   - Computed `liveCoinsCount` using `expandCollection(coinsDocs...).totalCoins`.
4. `numista_backend/main.py`
   - Cleaned up syntax in `/api/collection/count`.
   - Updated `/api/portfolio/snapshot/daily` to compute `total_coins` using `expand_collection_inventory` and `count_coins_and_lots(inventory)["total_coins"]`.
5. `numista_backend/tests/test_p2_coin_count_single_source.py`
   - New unit tests verifying physical coin expansion and lot vs coin counting (2 passed).
6. `numista_mobile/test/p2_coin_count_single_source_test.dart`
   - New Flutter tests verifying `expandCollection` and `HeaderStatsBar` rendering (3 passed).
7. `BETA TEST/Grok Bot/8 OCT 26/GEMINI38_REVIEW_P2_COIN_COUNT_BUILD.md`
   - Full build review with verbatim code citations and verification logs.

---

## 3. Machine Checkable Verification Commands
- `python -m pytest numista_backend/tests/test_p2_coin_count_single_source.py` -> 2 passed in 0.17s (Exit code 0)
- `python -m pytest numista_backend/tests/test_p2_coin_count_single_source.py numista_backend/tests/test_catalog_slot_counts.py numista_backend/tests/test_checklist_parser.py` -> 27 passed in 3.33s (Exit code 0)
- `flutter test test/p2_coin_count_single_source_test.dart` -> 3 passed (Exit code 0)
- `flutter analyze lib/` -> No issues found (Exit code 0)

---

## 4. Hard Safety Rules Adherence
- Zero writes to Firestore or user collections.
- Zero data migrations or `sync_canon` runs.
- Work committed on branch `dev` only. Never pushed to `main`.
