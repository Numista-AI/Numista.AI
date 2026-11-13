# COS SCORE - P7 BUILD V8.18.15e (b3d63b78) - FAIL-FIX (tests + hygiene)
Grok CoS | 22 Oct 2026 ~9:35 PM ET | Branch p7-v8.9, parent 1058fe8b | Orders: NET-440, NET-440A, NET-440B

## Re-verified by Grok CoS
- Backend pytest (worktree Temp\p7v89_build at b3d63b78): 613 passed (matches AG claim; +6 over 15d's 607).
- Real Flutter change, ignoring line endings: 6 files, +169 / -78. visualDensity: VisualDensity.standard is in both ThemeData objects (main.dart). kAppVersion = 'v8.18.15e'.
- P1 code is present: hdr list-normalization, receipt_ref batch.set before commit, any_errors -> "done_with_errors", coins_identified += added_this_file, and the shared check_and_flag_duplicate helper (flag only, no delete).
- Flutter test count NOT re-run this pass (AG reports 620, the same as 15d).
- GEMINI38 quotes NOT re-verified this pass (the verdict doesn't depend on them).

## Why FAIL-FIX
1. The P2 regression suite mostly doesn't test the real code (NET-440B P2). Tests 1, 4 and 6 copy the logic into the test itself (the hdr expression, the any_errors expression, the inv_no/item_no loop) instead of calling the main.py invoice worker or commit_reviews. Test 5 only calls the helper and never touches the 4 add paths (manual add, scan-save, cert save, spreadsheet import). Nothing checks that the receipt doc is written to (mocked) Firestore, that coins_identified equals the rows written, or that the session ends as done_with_errors. There's no origin/main baseline. The "all 4 paths" claim isn't proven.
2. No new Flutter tests (620 = 15d). NET-440 required widget tests that measure rendered height (>= 48) under windows, macOS and linux for the 6 named buttons (NGC card ngccoin.com and Cancel, sidebar Send Beta Feedback and Sign Out, photo page Take Photo and Upload), plus a test for the NGC title string. None of these exist. There are also no tests for the amber "flagged as possible duplicate" snackbar or the new Review/Collection 48x48 wrappers. NGC Look Up "Enter a cert # before saving" (NET-440B P3) isn't addressed.
3. Hygiene: CRLF flipped on main.dart, constants.dart, add_coins_hub.dart, my_collection_screen.dart and review_hub_screen.dart, which turns ~170 real lines into a ~31,000-line diff. Restore the original line endings, as 15a did. RELEASE_NOTES.md and home_dashboard.dart are left uncommitted in Temp\p7v89_build: either commit them by explicit path or revert them. pubspec version wasn't bumped (NET-440 item 5).

## Design note (for Eric / next phase, not a blocker for 15f)
The Year + Mint + normalized-Denom key (ordered in NET-440B) will flag as a "possible duplicate" every different coin that shares a year, mint and denomination: American Women Quarters, State/ATB quarters, Presidential $1, and Morgan vs Peace in 1921. It flags only and never drops, so no data is lost, but AJ's ~4,500-coin account could get a lot of false flags. It also doesn't treat "Dollar" and "$1" as the same denomination. Consider adding Program/Series (or design/honoree) to the key in a later build. Do NOT change it in 15f.

## Verdict
FAIL-FIX (small): tests and hygiene only, no new product code. NET-442 orders V8.18.15f. Baton to AGCOS OVER.
No deploys, nothing on main, no data writes.
