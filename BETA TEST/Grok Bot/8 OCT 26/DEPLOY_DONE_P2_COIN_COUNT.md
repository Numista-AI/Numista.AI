# DEPLOY_DONE — P2 Coin Count Single Source of Truth
**Filed by:** AG CoS  
**Date:** 2026-10-14  
**Ref:** NET-079 / Eric YES 11:26 AM ET  
**Status:** DEPLOYED TO MAIN ✅

## PR and Merge
- **PR:** #263 — https://github.com/Numista-AI/Numista.AI/pull/263  
- **Merge commit:** `6d54f940ad5604ab0102334f796cb0189f13f8a8`  
- **Branch:** `deploy/p2-coin-count` → `main` (squash+admin merge)

## Files Deployed (P2 only — zero P4 auth hunks)
1. `numista_mobile/lib/screens/home_dashboard.dart` — split totalCoins/totalItems, wire coin metrics correctly
2. `numista_mobile/lib/widgets/header_stats_bar.dart` — show totalCoinsCount unfiltered; filteredCount via expandCollection
3. `numista_mobile/lib/screens/my_collection_screen.dart` — liveCoinsCount via expandCollection
4. `numista_backend/main.py` — snapshot/daily hunk only: expand_collection_inventory + count_coins_and_lots for authoritative total_coins; ZERO auth/ownership route changes
5. `numista_backend/tests/test_p2_coin_count_single_source.py` — 2 pytest tests
6. `numista_mobile/test/p2_coin_count_single_source_test.dart` — 3 Flutter tests

## Verification
- pytest test_p2_coin_count_single_source.py: **2 passed**
- pytest (27 tests): **27 passed**  
- flutter test p2_coin_count_single_source_test.dart: **3 passed**
- flutter analyze lib/: **No issues found**

## Live Smoke
- home (numista-vault.web.app): **200** ✅
- spot_prices API: **200** ✅
- collection/count (no auth): **401** ✅

## Note on main.py P2 hunk
The `collection_count` cleanup in dev uses `get_current_user` (P4 infrastructure not yet on main). Only the `portfolio/snapshot/daily` hunk (pure counting logic, no auth dependency) was applied to the deploy branch. `collection/count` on main already uses `expand_collection_inventory` correctly.
