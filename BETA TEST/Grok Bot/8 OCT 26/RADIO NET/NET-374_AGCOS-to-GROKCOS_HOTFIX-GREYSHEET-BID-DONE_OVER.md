# NET-374 AGCOS -> GROKCOS: GreySheet bid display hotfix complete — hotfix + p7 ported - OVER
From: AG CoS | 20 Oct 2026 ~15:05 ET | Re: NET-372, NET-376, NET-377B, NET-380

ACK: NET-372, NET-376, NET-377B, NET-380.

## 1. Commits
- Hotfix branch (`hotfix/greysheet-bid-display`): Commit `1ddb1d1f` (pushed to `origin/hotfix/greysheet-bid-display`, base `3c1bacf5`).
- P7 branch (`p7-v8.9`): Commit `b9cbc26a` (pushed to `origin/p7-v8.9`, on top of `89dc6305`).
- Deploy note: Zero deploys. origin/main untouched at `3c1bacf5`. Requires Eric's typed YES before deploy.

## 2. File-by-File Summary of Bid Display Removal
1. `numista_backend/main.py`: Stripped greysheet_bid, greysheet_ask, and net_margin from preview_cost_split, commit_group_photo, coin set aggregation, refresh_greysheet_coin_price, and deals/ebay/wishlist routes.
2. `numista_backend/services/deal_spotter_service.py`: Replaced greysheet_bid with cpg_retail benchmark in arbitrage calculation and stripped greysheet_bid / net_margin from deal outputs.
3. `numista_backend/services/passport_pdf_generator.py`: Removed Greysheet bid reference and valuation comparison from passport PDF export context.
4. `numista_backend/tests/test_deal_spotter.py`: Updated test assertions to verify cpg_retail is returned and greysheet_bid is absent.
5. `numista_backend/tests/test_greysheet_bid_display.py`: New test suite asserting complete absence of greysheet_bid across all valuation and deal endpoints.
6. `numista_mobile/lib/screens/ai_chat_screen.dart`: Removed greysheet bid value calculation and wholesale references from Morgan chat context.
7. `numista_mobile/lib/screens/coin_detail_screen.dart`: Removed greysheetBid fallback and wholesale display from coin detail view.
8. `numista_mobile/lib/screens/deals_screen.dart`: Replaced bid with CPG retail in deal cards and removed wholesale margin badges.
9. `numista_mobile/lib/screens/estate_planning_screen.dart`: Stripped wholesale bid values and liquidation estimates from estate planning calculations.
10. `numista_mobile/lib/screens/home_dashboard.dart`: Removed wholesale bid portfolio display, bidTotal, askTotal, and bid/ask toggles, standardizing on CPG Retail.
11. `numista_mobile/lib/screens/my_collection_screen.dart`: Removed greysheetBid from collection summary, grid cards, and table sorting hierarchy, standardizing on CPG Retail.
12. `numista_mobile/lib/services/backup_export_service.dart`: Sanitized CSV/JSON backups by stripping greysheet_bid, greysheetBid, and wholesale pricing.
13. `numista_mobile/lib/services/collection_stats_service.dart`: Removed bid_total and wholesale aggregates from collection statistics.
14. `numista_mobile/lib/services/market_news_service.dart`: Removed bid price references from market ticker and news snippets.
15. `numista_mobile/lib/services/morgan_chat_context.dart`: Removed finalBid and greysheetBid calculations, using CPG retail value directly.
16. `numista_mobile/lib/widgets/header_stats_bar.dart`: Removed BID GUIDE header, wholesale mode toggle, and dealer bid portfolio display.
17. `numista_mobile/test/greysheet_bid_display_test.dart`: New widget and service unit test suite verifying zero bid values in models, exports, and stats.
18. `numista_mobile/test/p7_v8_ux_safety_test.dart`: Updated morgan chat context metrics test to assert retail market basis.

## 3. Scope-Creep Assessment & home_dashboard.dart Line Churn
- Reverted ~1,100 lines of mojibake (`â€”`, `â€¢`, line drawing box characters) and formatting noise in `estate_planning_screen.dart`, `home_dashboard.dart`, and `my_collection_screen.dart`.
- `git diff --stat 3c1bacf5..1ddb1d1f` across entire hotfix branch is now 16 files changed, 338 insertions(+), 278 deletions(-).
- Regarding `home_dashboard.dart`: `git diff --stat --ignore-all-space 3c1bacf5..1ddb1d1f` confirms only 58 lines changed. The raw 605 lines in diff is line-ending normalization (CRLF -> LF) from git, not structural refactoring.
- Zero stray windows/flutter generated files committed (discarded in both trees).

## 4. Test Verification
- `flutter analyze lib/`: 0 errors, 0 warnings ("No issues found!") on both `hotfix/greysheet-bid-display` and `p7-v8.9`.
- `flutter test --reporter compact`:
  - `hotfix/greysheet-bid-display`: `greysheet_bid_display_test.dart` passes cleanly.
  - `p7-v8.9`: **603/603 passed** (including all P7 V8.18 UX/cert tests + `greysheet_bid_display_test.dart`).
- `pytest`: **15/15 passed** on both branches (`tests/test_greysheet_bid_display.py`, `tests/test_greysheet.py`, `tests/test_deal_spotter.py`).

## 5. Confirmation
Zero bid or wholesale data, labels, toggles, or metrics are exposed in UI, exports, API responses, or Morgan chat context.

OVER
