# COS_SCORE HOTFIX GreySheet bid display - 1ddb1d1f (hotfix/greysheet-bid-display) + p7 port b9cbc26a
Scorer: Grok CoS | 20 Oct 2026 ~15:20 ET | Re: NET-372 (order), NET-374 (report) | Base: origin/main 3c1bacf5

## Verdict: FAIL (narrow). One leak path left; everything else is good.

## Grok re-run on hotfix worktree (Temp\hotfix_greysheet @ 1ddb1d1f)
- pytest tests/test_greysheet_bid_display.py tests/test_deal_spotter.py tests/test_greysheet.py: 15 passed
- flutter test test/greysheet_bid_display_test.dart: all passed
- git diff --stat --ignore-all-space 3c1bacf5..1ddb1d1f: 16 files, 328+/268-. home_dashboard.dart 58 real lines; 605 raw is CRLF->LF churn. Accepted.
- Stray windows/flutter generated_plugin* files are modified in the worktree but NOT committed. Good. Do not commit them.

## PASS
1. Client display: coin_detail EST. VALUE no longer falls back to bid; my_collection grid, totals, sort use CPG only; header_stats_bar BID GUIDE + Wholesale toggle gone; home_dashboard bid mode gone; estate screen bid gone; deals_screen shows CPG Retail and the fake 40.0 default is removed (skips coins with no CPG). PASS.
2. Exports: backup_export_service strips greysheetBid/greysheet_bid/greysheetAsk/greysheet_ask/bid_total. Passport PDF Wholesale (Bid) line, bid total row, and "Greysheet Wholesale Bid" disclaimer removed. (passport est_val at :167 is assigned but never printed, so the AI-string-first order there is harmless.) PASS.
3. Chat context: ai_chat_screen cost-split card + summary no longer show bid; p7 port also covers morgan_chat_context.dart. PASS.
4. API responses: preview_cost_split, commit_group_photo, refresh_greysheet_coin_price (single + aggregate), deals/refresh/ebay routes no longer return greysheet_bid/greysheetBid/ask/net_margin; execute_add_coin dry-run snapshot strips bid. Aggregate "AI Estimated Value" now CPG only. Firestore storage of bid kept (back-end use allowed, no data deleted). PASS.
5. collection_stats est_value now = cpg_total (was bid_total). PASS.
6. Branch hygiene: code-only commits on hotfix branch, main untouched at 3c1bacf5, port on p7-v8.9 as b9cbc26a (19 files incl. morgan_chat_context + p7 test). PASS.

## FAIL - one leak path (NET-372 rule: "Do NOT fall back to bid")
- numista_backend/services/deal_spotter_service.py:31
  `benchmark_val = float(item.get("cpgRetail") or item.get("cpg_retail") or item.get("greysheetBid") or 95.0)`
  then the output dict sends `"cpg_retail": benchmark_val` to the client. For any wishlist/collection item with a bid but no CPG, the bid is shown to the user relabeled as "CPG Retail". When neither exists it shows a made-up $95.00. That is both a bid leak and fake data.

## Required fix (hotfix rev 2, 2 files, GEMINI38 skipped per Rule 3)
1. deal_spotter_service.py:31 -> use cpgRetail / cpg_retail only. If no CPG > 0, skip the item (no 95.0 default, no greysheetBid fallback).
2. tests/test_greysheet_bid_display.py -> add a test: match_wishlist_items([{year,mint,series,"greysheetBid": 120.0}]) returns no deal (or no cpg_retail == 120.0), and an item with no values returns no deal.
3. Commit on hotfix/greysheet-bid-display (explicit paths), then port the same 2 files to p7-v8.9. No deploy.

## Not blocking (parked, report to Eric; needs his OK - out of NET-376 scope)
- main.py DEALS_DB (~10582-10605), refresh_arbitrage_deals (~10615-10650) and search_ebay_deals (~11184) still ship hard-coded demo deals (95.00 / 52.00 / 1250.00, gsid 429, random eBay ids). This hotfix relabeled those demo numbers from greysheet_bid to cpg_retail, so users could see invented "CPG Retail" prices. Pre-existing fake data; needs a decision (remove/hide Deals until real data, or label as demo).
- _scripts/batch_greysheet_direct.py:187 and batch_greysheet_v2.py:273 still write "AI Estimated Value" = "$bid - $cpg" if run. Dev scripts, not deployed; fix with the next scripts pass (write CPG only). Client prefers cpgRetail, so stored legacy strings only show when cpgRetail is 0.

## Deploy
Not ready for Eric's YES. After rev 2 passes Grok score, Grok asks Eric for a typed YES; deploy = cherry-pick the approved hotfix commits onto a branch from main only.
