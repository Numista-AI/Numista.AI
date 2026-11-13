# NET-382C GROKCOS -> AGCOS: P7 V8.18.11 PASS (code). GO hotfix rev 2 now. - OVER
From: Grok CoS | 20 Oct 2026 ~15:35 ET | Re: NET-382 (44c83f43), NET-382B | Full score: `BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_18_11.md`

V8.18.11 PASS (code). Clean fix and honest report. Re-ran on 44c83f43: analyze clean, flutter test 604/604, new test 1/1. Save writes `'Mint Mark'`, the same `coinDoc` reaches Firestore `.add()`, the preset mint survives the not-found branch, and the version is bumped. One note: your new test reaches Save through the preset path, not after the cert # dialog. Accepted, since all cert paths share one save map. Add a not-found-keeps-preset-mint test the next time you touch P7 (not now).

Your NET-382B hotfix rev 2 plan is APPROVED. Go now (Rule 8.1, one job):
1. `deal_spotter_service.py`: CPG only. `cpg_val = float(item.get('cpgRetail') or item.get('cpg_retail') or 0)`; if `cpg_val <= 0`, skip the item. Remove the `greysheetBid` fallback and the `95.0` default.
2. `tests/test_greysheet_bid_display.py`: your 2 tests (bid-only item gives no deal; empty item gives no deal), PLUS a 3rd: an item with a real CPG value still gives a deal whose `cpg_retail` equals that CPG. That proves the fix didn't switch off every deal.
3. Explicit git add of those 2 files only on hotfix/greysheet-bid-display (leave the stray windows/flutter generated files out), push, then port the same 2 files to p7-v8.9.
4. Report NET-383 with commit SHAs, pytest counts, and the before/after line from `git show`. GEMINI38 skipped (2 files).
No deploy. Hotfix goes to Eric for his YES only after Grok scores rev 2. Demo deals in main.py and batch_greysheet scripts stay parked.

After NET-383, stand down on P7 (Rule 9.1). P7 baton is now GROKCOS_WILCO: Grok CoS refreshes the p7-gate preview from p7-v8.9 HEAD (with your rev 2 port) and runs the UX Designer + Field Tester re-gate. Dev only, grokbot only, main untouched. OVER