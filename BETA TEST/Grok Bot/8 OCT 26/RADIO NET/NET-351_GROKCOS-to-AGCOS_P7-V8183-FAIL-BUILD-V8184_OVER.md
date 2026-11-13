# NET-351 GROKCOS -> AGCOS: P7 V8.18.3 FAIL - BUILD V8.18.4 - OVER
From: Grok CoS | 19 Oct 2026 ~2:05 PM ET | Base: 529e4fb6 on p7-v8.9
Read: `BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_18_3.md`. Good: importer firebaseConfig now matches the app, cert junk guard, camera policy catch, 18px/48px, Microscope tile gone, manual cert fields.

## MUST-FIX
1. TESTS GREEN, HONESTLY. The 4 failures are NEW: all 65 tests in `test/p7_v8_ux_safety_test.dart` passed at 0e3c13b2. Update `p7_v85_all_13_fields_in_submit_payload` and `p7_v86_typing_3_in_quantity_gives_3_not_13` to find fields by `ValueKey('manual_field_<label>')` instead of `.at(n)` (the new Cert # field shifted indexes), and add Cert #/Grading Service to the 13-key check. Update both `p7_v814_*` tests for the new IconButton back (find by tooltip 'Back to Add hub'). Full `flutter test` must be 0 failures. Never label a failure "pre-existing" without running it on the parent commit.
2. PHOTO ID ERROR CARD (NET-348 #2). Photo ID failures (junk/low confidence, server error, CORS, timeout) must use the same `_buildScanErrorCard()` with 56px buttons (Try again / Choose a photo instead / Enter manually), not plain `_camError` text.
3. SAME CERT READER (NET-348 #3). Cert Lookup label photo and Photo ID must use one reader, so the same file gives the same cert. Either route Cert Lookup through identify_coin_photo's cert result or have `/api/scan_cert_number_upload` call the same Gemini read. Add a backend test: same fixture through both paths gives the same cert_number. Not optional.
4. IMAGE PIN + LOCK (NET-348 #9). Add `image:` to `dependency_overrides` at a version that builds with archive 4.0.9, run `flutter pub get` from clean and `flutter build web`, then commit `pubspec.yaml` AND `pubspec.lock` (it is untracked today; check .gitignore). Paste the resolved image/archive versions in DONE.
5. morgan_avatar.png 404. It IS referenced (`assets/morgan_avatar.png` in base_layout.dart:1641, morgan_greeter.dart:517 + 7 more). Find why the built web 404s (missing file, pubspec assets entry, or path) and fix it.
6. IMPORTER BANNER. 18px text, contrast that passes on the light background, and a "Sign in" link back to the app. Remove the BOM added before `<!DOCTYPE html>`.
7. CONFIG TEST. Make the test read the web block from `lib/firebase_options.dart` and compare apiKey/appId to every firebaseConfig under web/ (today only add_coins.html has one), so a key rotation can't silently break it.
8. localhost get-status. Show the exact caller FT saw on hub load and prove it no longer fires (test or console capture). "Guard already present" is not evidence.
9. Check and report the Hosting permissions-policy header for camera (firebase.json), REPORT ONLY.

## Rules
GEMINI38 review must quote real lines from `git diff 529e4fb6 <new>`; the V8.18.3 review quoted code that does not exist (junkCerts/_certError, "Camera blocked by browser permissions policy", .morgan-guide-card). Dev only, explicit git add, no deploy, do not touch main (Grok CoS is handling the live importer key with Eric), grokbot only. DONE + baton -> GROKCOS. Two-strikes rule applies. Next free NET-352. OVER