# COS SCORE - P7 V8.18.15 (2aa65b50 on p7-v8.9) - CODE PASS, 1 HYGIENE FIX BEFORE PREVIEW - GROKCOS watch
Scored 2026-10-21 ~2:12 PM ET by Grok CoS (watch run). Parent cff5ab1b. Orders scored: NET-411 items 1-5, NET-404 g/h, NET-406 j-m, NET-408 n, NET-410, NET-413 p/q.

## What Grok CoS checked (real diff, not the review)
- origin/p7-v8.9 = 2aa65b50 (confirmed). 21 files; `git diff -w` = +1155/-278.
- Re-ran `pytest tests/test_invoice_fixtures.py tests/test_cert_lookup.py`: 39 passed.
- Re-ran `flutter test --plain-name p7_v81815`: 8/8 passed. Re-ran FULL `flutter test`: 617/617 passed (609 baseline + 8 new).
- Searched the real diff for 22 quoted lines from GEMINI38_REVIEW_P7_V8_18_15_BUILD.md: all 22 found. Rule 6 satisfied.

## PASS
1. NET-411.1 Rule 6: GEMINI38 quotes are real diff lines (e.g. `merged["line_items"] = [li for d in dict_entries ...`, `bool get isNativePhone => debugIsNativePhoneOverride ?? getNativePhone();`, `padding: EdgeInsets.fromLTRB(0, 0, 0, isNativePhone ? 88 : 24)`).
2. NET-411.2 tests: 8 new Flutter tests (400d, 400e, 401.3, 401.4, 410, 408n, 413p, 413q); 8 new pytest (PCGS 200 valid / 200 no-data->404 / 200 quota->503, 4 label-photo fixtures, `test_invoice_092052_acceptance`). Qty test now imports production `normalize_and_validate_receipt` (no local copy of `_get_item_qty`).
3. NET-411.3 add_coins_hub.dart restored to LF: CR count 0 (was 12,208 at cff5ab1b). vs a4a77e4c the file is +353/-241 raw, +185/-73 with -w. Accepted.
4. NET-411.4 PCGS ServerMessage for 53652580 reported: `IsValidRequest: false`, "No data found for this certification number." -> 404 not_found.
5. NET-410 gate: `_platform_gate_io.dart` `!kIsWeb && (Platform.isAndroid || Platform.isIOS)`, web stub returns false, conditional import. Phone-only changes use `isNativePhone`.
6. NET-404 g/h, NET-406 j-m, NET-408 n, NET-413 p/q built as described (greeter camera route, microscope banner hidden on phone + Flexible, DASHBOARD FittedBox, checklist count from `BetaChecklistService.allTasks.length`, landscape SingleChildScrollView 88dp, FAB clamp, CameraRecoveryService + 1600x1600 q75).

## FIX BEFORE PREVIEW (small hygiene commit, V8.18.15a)
1. NEW CRLF CHURN in 4 files (were LF at cff5ab1b, now CRLF on every line):
   - RELEASE_NOTES.md: 4,729 lines changed vs 26 real (-w).
   - numista_mobile/test/p7_v8_ux_safety_test.dart: 3,140 vs 360 real.
   - numista_mobile/pubspec.yaml: 131 vs 2 real.
   - numista_mobile/lib/constants.dart: 29 vs ~1 real.
   Convert these 4 files back to LF only, commit with explicit paths, and prove it: `git diff --numstat cff5ab1b HEAD` must be close to `git diff -w --numstat cff5ab1b HEAD` for every file. Same check on all 21 files.
2. UNREQUESTED SCOPE: new dev dependency `flutter_launcher_icons: ^0.14.1` + `flutter_launcher_icons.yaml` + pubspec.lock changes. Not in any NET order. Either justify it in one line (which order, why needed for this build) or drop it from this branch and propose it for V8.18.16.
3. Device checks still open (not blocking the code score): NET-404g camera opens directly, NET-413q 5 photos in a row on the TCL T609C.

## Next
AG: V8.18.15a hygiene commit on p7-v8.9 (items 1-2 only, no feature changes, no new review needed beyond a diff numstat table). Then Grok CoS: p7-gate preview refresh, UX Designer + Field Tester re-gate. NET-417 items stay queued for V8.18.16. Eric typed YES before any live deploy (cherry-pick onto a branch from main only). No deploy, nothing on main. See NET-418. Baton -> AGCOS.