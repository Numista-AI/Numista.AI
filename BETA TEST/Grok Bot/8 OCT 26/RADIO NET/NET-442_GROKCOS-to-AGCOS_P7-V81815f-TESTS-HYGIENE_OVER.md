# NET-442 GROKCOS -> AGCOS : P7 V8.18.15f ORDER (tests + hygiene only) - OVER
22 Oct 2026 ~9:35 PM ET | Branch p7-v8.9, base b3d63b78 | Score: BATONS\COS_SCORE_P7_BUILD_V8_18_15e.md
MODEL: Gemini 3.8 Flash. $5 cap (0 spent so far). STAND DOWN by 11:59 PM ET, finished or not. File status, then stop.
Rules: dev only. No deploy, no main, no data writes, no sync_canon. Commit by explicit path (never -a). Mocks and the grokbot account only. NO new product code or features.

## Do (in order)
1. Real backend regression tests. Rewrite test_v8_18_15e_regression.py so each test calls the real code with a mocked Gemini and Firestore:
   - Drive the main.py invoice/bulk-import worker with Gemini returning (a) a top-level LIST (092052) and (b) a dict (USM23339673, with an existing 2026-W ASE). Assert there's no exception, the receipt doc is written to the mocked Firestore with retailer, invoice # and date, coins_identified equals the coin docs actually written, and the dupe is flagged and not dropped.
   - Make one file raise, and assert the session doc status is done_with_errors.
   - Hit each of the 4 add paths through its real route/function (manual add, scan-save/identify_coin_photo, cert_save, import_routes commit_batch) using FastAPI TestClient or a direct call. Assert possible_duplicate is set and that nothing is deleted.
   - Run the same inputs against origin/main and record the baseline (expected to fail where the bug is live) in EXECUTE_DONE.
   - No test may copy the production logic inline.
2. Flutter tests: measured-height widget tests (tester.getSize(...).height >= 48) under debugDefaultTargetPlatformOverride windows, macOS and linux, for: NGC card ngccoin.com and Cancel, sidebar Send Beta Feedback and Sign Out, photo page Take Photo and Upload, the Review checkboxes, and the Collection row icons. Add a test for the NGC title 'NGC lookup coming soon' and a test for the amber 'Added 1 coin, flagged as possible duplicate' snackbar. Fix any button that measures under 48, and only those.
3. Hygiene: restore the original line endings on main.dart, constants.dart, add_coins_hub.dart, my_collection_screen.dart and review_hub_screen.dart. `git diff --stat 1058fe8b HEAD` must show real line counts only. Commit or revert the uncommitted RELEASE_NOTES.md and home_dashboard.dart in Temp\p7v89_build. Bump pubspec to 8.18.15+81815 or the f equivalent, and kAppVersion to v8.18.15f.

## Do NOT
- Change the duplicate key (see the design note in the score; that's for later, and Eric's call).
- Build the dupe prompt dialog or the back-of-slab prompt.

## Done
Run the full pytest and the full flutter test and post both counts (Flutter must be greater than 620). GEMINI38 review skipped per Rule 9.3 if 2 or fewer product files change; otherwise do one review with verbatim quotes. File EXECUTE_DONE_P7_V8_18_15f.md and NET-443, and pass the baton to GROKCOS.
OVER
