# NET-383 AGCOS -> GROKCOS: GreySheet hotfix rev 2 complete - 44f8604d hotfix / 86ee05e0 p7 port - OVER
From: AG CoS | 20 Oct 2026 ~19:50 ET | Re: NET-381B (hotfix FAIL narrow) + NET-382C (GO)

V8.18.11 PASS received. Hotfix rev 2 complete and ported.

## Commits
- Hotfix branch: 44f8604d on hotfix/greysheet-bid-display (on top of 1ddb1d1f)
- P7 port: 86ee05e0 on p7-v8.9 (on top of 44c83f43)

## Changes — 3 files (GEMINI38 skipped per Rule 9.3)

### deal_spotter_service.py
Line 12 (calculate_arbitrage): greysheet_bid kwarg fallback removed.
  Before: target_val = benchmark_val if benchmark_val > 0 else float(kwargs.get("greysheet_bid") or 0.0)
  After:  target_val = benchmark_val if benchmark_val > 0 else 0.0

Lines 31-33 (match_wishlist_items): bid fallback + fake  removed; skip-if-no-CPG added.
  Before: benchmark_val = float(item.get("cpgRetail") or item.get("cpg_retail") or item.get("greysheetBid") or 95.0)
  After:  benchmark_val = float(item.get("cpgRetail") or item.get("cpg_retail") or 0.0)
          if benchmark_val <= 0:
              continue

### test_deal_spotter.py — 3 existing tests updated to CPG-only inputs
- test_deal_spotter_service_arbitrage_math: now passes benchmark_val=100.0 (not greysheet_bid kwarg)
- test_deal_spotter_wishlist_matching: item now has cpgRetail=150.0 (not greysheetBid)
- test_wishlist_deals_endpoints: POST payload uses cpg_retail=120.0 (not greysheetBid)

### test_greysheet_bid_display.py — 3 new tests added
- test_deal_spotter_bid_only_item_yields_no_deal: item with only greysheetBid=120.0 -> 0 deals
- test_deal_spotter_empty_item_yields_no_deal: item with no pricing -> 0 deals
- test_deal_spotter_real_cpg_item_yields_deal: item with cpgRetail=150.0 -> 1 deal, cpg_retail==150.0, no greysheet_bid/net_margin

## Test results
- Hotfix worktree (44f8604d): pytest tests/test_greysheet_bid_display.py tests/test_deal_spotter.py: 10/10 passed
- P7 worktree (86ee05e0): pytest tests/test_greysheet_bid_display.py tests/test_deal_spotter.py: 10/10 passed

## Not touched (parked per NET-381B)
- main.py hard-coded demo deals still show cpg_retail values; labeling decision deferred to Eric
- batch_greysheet scripts still write AI Estimated Value string; dev scripts, not deployed

## Branch hygiene
- hotfix/greysheet-bid-display: code-only, pushed to origin
- p7-v8.9: port pushed to origin
- origin/main untouched at 3c1bacf5
- No deploy

AG CoS standing down on P7 per NET-382C. Baton GROKCOS_WILCO — gate phase is yours. OVER
