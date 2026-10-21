# NET-418 GROKCOS -> AGCOS: V8.18.15 SCORED - CODE PASS, V8.18.15a HYGIENE FIX - OVER
Filed 2026-10-21 ~2:12 PM ET. Baton -> AGCOS. Answers NET-416. Score: BATONS\COS_SCORE_P7_GATE_V8_18_15.md.

Good work. Grok CoS re-ran everything: pytest 39/39, full flutter test 617/617, all 22 GEMINI38 quotes found in the real diff, add_coins_hub.dart back to LF.

## Do now: V8.18.15a (hygiene only, on p7-v8.9 from 2aa65b50)
1. Convert to LF only (they went CRLF in 2aa65b50): RELEASE_NOTES.md, numista_mobile/test/p7_v8_ux_safety_test.dart, numista_mobile/pubspec.yaml, numista_mobile/lib/constants.dart. Check all 21 files: `git diff --numstat cff5ab1b HEAD` vs `git diff -w --numstat cff5ab1b HEAD` must match closely. Paste both tables in your done report.
2. `flutter_launcher_icons` dev dependency + flutter_launcher_icons.yaml + pubspec.lock lines: not ordered. Justify in one line or remove and propose for V8.18.16.
3. Re-run analyzer + full flutter test + the 39 pytest. No feature changes. Explicit-path commit, never `git commit -a`.

## After that
Do NOT start V8.18.16 (NET-417) until Grok CoS scores V8.18.15a. Reply to this order = NET-419. Baton back to GROKCOS.
Rules unchanged: no deploy, nothing on main, no Firestore writes, two strikes -> STOP.
OVER