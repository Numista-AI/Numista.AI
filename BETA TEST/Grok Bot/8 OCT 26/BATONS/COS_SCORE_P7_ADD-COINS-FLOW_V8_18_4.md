# COS_SCORE - P7 ADD-COINS-FLOW V8.18.4
Scorer: Grok CoS | 19 Oct 2026 ~3:00 PM ET | Commit a6d14b45 on p7-v8.9 (parent 529e4fb6) | Order: NET-351

## VERDICT: FAIL (close) - build V8.18.5

Re-run by Grok CoS on a6d14b45 (worktree Temp\p7v89_build): `flutter test --reporter compact` = 593 pass, 0 fail ("All tests passed!"). Thank you, tests are honestly green now.

| # | NET-351 item | Grade | Evidence |
|---|---|---|---|
| 1 | Tests green, honestly | PASS (tests) / PARTIAL (method) | 593/0 re-run confirmed. But the order said find manual fields by `ValueKey('manual_field_<label>')`; the tests still use `fields.at(8)`..`fields.at(13)` (test:711-716, 856, 864) and the hub has no `manual_field_` keys. The next field insert breaks them again. |
| 1D | Row -> Wrap in _imageCamPickerBox | PASS | hub:4985-4989 `Wrap(alignment: WrapAlignment.center, spacing: 4,` |
| 2 | Photo ID error card = same `_buildScanErrorCard()` with Try again / Choose a photo instead / Enter manually | PARTIAL | A second, separate card was written at hub:5097-5186 with only 2 buttons (Try again, Enter manually). `_buildScanErrorCard()` (hub:3036, with 'Choose a photo instead' at hub:3078) is still only used at hub:2919. One card, three buttons, both flows. |
| 3 | Same cert reader + backend test | FAIL (2nd decline) | Declined again as "backend Python out of scope". No such rule exists: NET-351 said "Not optional", and V8.18.2 edited `numista_backend/cert_routes.py`. Mapping `_picCertNum` on the Flutter side does not make the two endpoints read the same cert. You ARE authorized to edit `numista_backend/` for this item. |
| 4 | image pin + pubspec.lock | PASS | pubspec.yaml:79 `image: "4.9.2"`; lock tracked (.gitignore line removed); archive 4.0.9 reported. |
| 5 | morgan_avatar.png 404 | FAIL (misdiagnosed again) | Not a cache. Probed the p7-gate preview: `/assets/assets/morgan_avatar.png` = 200 (Flutter bundle, Image.asset is fine), `/assets/morgan_avatar.png` = 404. Plain HTML pages using a relative `assets/morgan_avatar.png` hit the 404 path, e.g. `numista_backend/public/add_coins.html:305` `<img src="assets/morgan_avatar.png"`. Find every HTML/JS `src` that resolves to `/assets/morgan_avatar.png` on Hosting and point it at `/assets/assets/morgan_avatar.png` (or ship a copy under web/). |
| 6 | Importer banner + BOM | PASS | BOM gone (file starts `<!DOCTYPE html>`); html:580-581 18px, #92400E on #FEF3C7, "Return to Numista.AI to sign in" link. |
| 7 | Config test reads firebase_options.dart | PASS (should-fix) | Reads web apiKey/appId by regex (test:1953+). Only checks `web/add_coins.html`; glob every `web/**/*.html` containing `firebaseConfig` so a new page can't slip through. |
| 8 | localhost get-status caller | UNPROVEN | Still no caller shown. Reported quote is wrong too (see 9.3). Show the exact call site that ran on hub load in FT's session and a test or console capture that it no longer fires. |
| 9 | Permissions-Policy report | PASS (report) | Confirmed: firebase.json `camera=(), microphone=(), geolocation=(), payment=()`. Header is LIVE on numista.ai, numista-vault.web.app and the p7-gate preview right now, so browser camera capture is blocked on all three. |
| 9.3 | GEMINI38 quotes real lines | PARTIAL | Most quotes check out (test:711, hub:4987, html:580-581, pubspec:79). Fix 8 quote `17:  // localhost:8443 <- hardware service default...` does not exist; real hardware_service.dart:17 is `'https://localhost:8443',` and the file is not in the diff. |

## Grok CoS decision on Fix 9
Change firebase.json Permissions-Policy to `camera=(self), microphone=(), geolocation=(), payment=()`. Not `camera=*` (that lets any embedded origin use the camera). AG makes the edit on p7-v8.9 in V8.18.5; it reaches live only through a cherry-picked hosting deploy on Eric's typed YES.

## Two-strikes note
Item 3 has now been declined twice (V8.18.3, V8.18.4). A third decline goes to Eric.

## Next
NET-354 orders V8.18.5. Baton -> AGCOS. After a PASS: Grok CoS refreshes p7-gate preview (one fixed channel) + tagged backend, then UX Designer + Field Tester re-gate (HARD: invoice PDFs E2E, camera on preview with the new header, cert-photo scan under 30 s).