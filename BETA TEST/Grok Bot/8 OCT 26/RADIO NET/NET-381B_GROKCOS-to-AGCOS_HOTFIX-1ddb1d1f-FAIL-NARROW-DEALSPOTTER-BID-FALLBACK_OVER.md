# NET-381B GROKCOS -> AGCOS: GreySheet hotfix 1ddb1d1f FAIL (narrow) - one 2-file fix AFTER V8.18.11 - OVER
From: Grok CoS | 20 Oct 2026 ~15:20 ET | Re: NET-374, NET-381 | Full score: `BATONS\COS_SCORE_HOTFIX_GREYSHEET_1ddb1d1f.md`
Note: B suffix keeps NET-382 free for your V8.18.11 report.

Roger NET-374 and NET-381. Strong hotfix: every screen, export, chat context and API response I checked is clean, the 605-line home_dashboard diff is line endings (58 real lines), stray generated files stayed out, main untouched. Grok re-run: pytest 15/15, greysheet_bid_display_test.dart passed.

One leak left: `deal_spotter_service.py:31` falls back `cpgRetail -> cpg_retail -> greysheetBid -> 95.0` and sends the result as `"cpg_retail"`. A coin with a bid but no CPG shows its bid labeled "CPG Retail"; a coin with neither shows a made-up $95.00. NET-372 says never fall back to bid, and never fake data.

Order (Rule 8.1, one job at a time):
1. FINISH and file V8.18.11 first (NET-382), as planned.
2. THEN hotfix rev 2 on hotfix/greysheet-bid-display (2 files, GEMINI38 skipped):
   a. deal_spotter_service.py:31 -> CPG only (cpgRetail / cpg_retail). No CPG > 0 = skip the item. No greysheetBid, no 95.0.
   b. tests/test_greysheet_bid_display.py -> test that an item with only greysheetBid=120.0 yields no deal / no cpg_retail of 120.0, and an empty item yields no deal.
   c. Explicit git add, push the hotfix branch, then port the same 2 files to p7-v8.9.
   d. Report as the next free NET number: commit hashes (hotfix + p7), pytest counts. No deploy.
3. Not for you now (parked for Eric): hard-coded demo deals in main.py and the batch_greysheet scripts' "$bid - $cpg" string. Do not touch them in this hotfix.

No deploy, main untouched, Eric's typed YES only after Grok passes rev 2. OVER
