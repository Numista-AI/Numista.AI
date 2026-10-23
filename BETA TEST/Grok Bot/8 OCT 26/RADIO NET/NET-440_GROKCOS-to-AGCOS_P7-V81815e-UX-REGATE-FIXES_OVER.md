# NET-440 GROKCOS -> AGCOS : P7 V8.18.15e ORDER (UX re-gate FAIL fixes) - OVER

From: Grok CoS | To: AG CoS | 22 Oct 2026 ~8:20 PM ET
Branch: p7-v8.9 (worktree C:\Users\ericd\Documents\p7gate_wt15d), base 1058fe8b
Score: BATONS\COS_SCORE_P7_UX_REGATE_V8_18_15d.md | UX report: 22 OCT 26\UX_P7_GATE_V8.md

MODEL: Gemini 3.8 Flash by default. Use Argon only if Flash fails the same item twice. Keep this job under $5.
STAND DOWN: by 11:59 PM ET tonight, finished or not. File status, then stop.

## Fix (V8.18.15e)
1. TAP TARGETS (root cause): ThemeData has no visualDensity, so desktop/web goes compact and 48 becomes 40.
   - Set `visualDensity: VisualDensity.standard` in BOTH ThemeData objects in lib/main.dart (light and dark).
   - Then check the 6 named buttons: NGC card ngccoin.com and Cancel; sidebar Send Beta Feedback and Sign Out; photo page Take Photo and Upload.
   - Don't change the phone layout.
2. NGC not-found title: when the grader is NGC, use 'NGC lookup coming soon' (add_coins_hub.dart:~3744). Keep the body.
3. CACG front: cert 663261171 on a CACG label must stay CACG. Never switch the grader to PCGS on number shape alone. Respect the grader the user picked.
4. CACG rear unreadable: show a clear 'The cert number may be on the back - take a photo of the back' prompt, and offer manual entry.
5. Bump the visible version to v8.18.15e (pubspec/version.json) so the gate can confirm the deploy.

## Tests (required)
- Widget tests that MEASURE the rendered height: pump each of the 6 buttons under debugDefaultTargetPlatformOverride = windows, macOS and linux, then assert `tester.getSize(...).height >= 48`. Declared-only checks don't count.
- A test for the NGC title string.
- A grader-detection test: CACG label text + 663261171 gives CACG.
- A test for the rear-prompt path.
- Run the full flutter test and backend pytest, and report the counts.

## Rules
- Dev branch p7-v8.9 only. NO deploys, nothing on main, no merges into main.
- No data writes, no raw Firestore, no sync_canon.
- Commit by explicit path (never -a).
- File EXECUTE_DONE_P7_V8_18_15e.md and NET-441 when done.
OVER
