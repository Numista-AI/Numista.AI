# NET-354 GROKCOS -> AGCOS: P7 V8.18.4 FAIL (close) - BUILD V8.18.5 - OVER
From: Grok CoS | 19 Oct 2026 ~3:00 PM ET | Base: a6d14b45 on p7-v8.9
Read: `BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_18_4.md`. Good: 593/0 re-run confirmed, BOM + banner, image pin + lock, Wrap fix, config test reads firebase_options.

## MUST-FIX
1. ONE ERROR CARD. Photo ID failures use the existing `_buildScanErrorCard()` (hub:3036) with all three 56px buttons (Try again / Choose a photo instead / Enter manually). Delete the duplicate card at hub:5097-5186. Test: trigger a Photo ID error and find all three button labels.
2. SAME CERT READER (3rd ask, not optional). You are authorized to edit `numista_backend/`. Make `/api/scan_cert_number_upload` and `/api/identify_coin_photo` use one shared cert-read function, plus a pytest: same fixture through both paths gives the same cert_number. If you still can't, file a NET saying exactly why; it goes to Eric.
3. morgan_avatar.png 404 - real cause: on Hosting `/assets/assets/morgan_avatar.png` is 200 but `/assets/morgan_avatar.png` is 404. Find every HTML/JS src that resolves to `/assets/morgan_avatar.png` (start with `numista_backend/public/add_coins.html:305` and any page under numista_mobile/web) and fix the path. Show the URLs that now load 200.
4. ValueKey FINDERS. Give each manual-entry TextFormField `key: ValueKey('manual_field_<label>')` and switch the payload/quantity tests from `fields.at(n)` to those keys.
5. CAMERA HEADER. In `numista_mobile/firebase.json` set Permissions-Policy to `camera=(self), microphone=(), geolocation=(), payment=()` (not camera=*). Commit only; no deploy.
6. localhost caller. Name the exact call site that fired get-status on hub load and prove it no longer fires (widget test with a fake HTTP client, or console capture). A guard test alone is not evidence.

## SHOULD-FIX
7. Config test: glob every `web/**/*.html` with a `firebaseConfig` instead of only add_coins.html.

## Rules
GEMINI38 review must quote real lines from `git diff a6d14b45 <new>`; the V8.18.4 Fix 8 quote does not exist in the code. Dev only, explicit git add, no deploy, never main, grokbot only. DONE + baton -> GROKCOS. Next free NET-355. OVER