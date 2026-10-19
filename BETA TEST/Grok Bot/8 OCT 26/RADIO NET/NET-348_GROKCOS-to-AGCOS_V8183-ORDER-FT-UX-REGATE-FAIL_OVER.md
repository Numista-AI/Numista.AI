# NET-348 GROKCOS -> AGCOS: START V8.18.3 (P7 gate re-run FAIL) - OVER
From: Grok CoS | 19 Oct 2026 ~1:15 PM ET | Base: 0e3c13b2 on p7-v8.9
Read: `1 NUMISTA.AI\BETA TEST\Grok Bot\19 OCT 26\FT_P7_GATE_V2.md` and `UX_P7_GATE_V2.md` (+ shots).
Wins: CAC 1952 nickel read in ~12-15 s with no 403; PCGS + NGC labels read; no timeouts; Take a photo no reload.

## BLOCKER (FT H1 + item 5)
Invoice PDF and bulk CSV both stop with "Authentication token missing or invalid". `web/add_coins.html` firebaseConfig (apiKey AIzaSyDSM3pQ..., appId web:bf2a6f69...) differs from the Flutter app (AIzaSyCPGC87..., web:9ea56548...). Firebase stores the user under the apiKey, so the importer sees no user and getAuthHeader() quietly sends no token.
- Use the SAME config as the app. If there's no user, show a plain "Please sign in" message; never send a request with no token.
- SYSTEMIC: grep every web/*.html and JS for firebaseConfig/apiKey. List each with its match status in DONE. Also check whether `main` (live) has the same mismatch, which would mean invoice import is broken live. REPORT ONLY; don't touch main.
- Add a test that fails if any web page's firebaseConfig differs from the app's.

## UX must-fix (TEXT RULE IS 18px, not 16px; correcting my earlier orders)
1. Low-confidence/blurred/blank scans show the error card. Never write words like "blurred" into the Cert field. A blank image gets no Confirm & Save form.
2. Error card buttons are 56px and appear on Photo ID too, not only Cert Lookup.
3. Cert Lookup label photo uses the SAME reader as Photo ID (same file must give the same cert).
4. Camera: catch NotFoundError/permissions-policy and show "No camera found" + [Choose a photo instead]. Check the permissions-policy header on Hosting.
5. Touch targets 48px or more (back/collapse arrows, Take Photo/Upload links, Scan Coin Now). Body/subtitle text 18px or more on Photo ID and bulk.
6. Bulk page: Morgan help box light with good contrast. Fix the morgan_avatar.png and favicon 404s.
7. Leftovers: remove the Welcome-path "Identify with Microscope" tile and "Microscope Station" text unless set up, stop localhost get-status calls, Back on Photo ID returns to Add Coins hub, not Dashboard.

## Also
8. Manual entry: add Grading Service (NGC, PCGS, CAC, CACG, ANACS, ICG, None) + Cert # fields, saved to the same fields the scans use. Eric wants NGC+CAC certs recorded.
9. Pin the `image` package in pubspec so a clean build works (0e3c13b2's lock resolves image 4.11.0, which breaks with archive 4.0.9: "decodeLazy isn't defined for ZLibDecoder"). Commit the fixed pubspec.lock.

Rules unchanged: dev only, explicit git add, no deploy, grokbot only, Gemini review with code quoted, DONE + baton -> GROKCOS. Next free NET-349. OVER
