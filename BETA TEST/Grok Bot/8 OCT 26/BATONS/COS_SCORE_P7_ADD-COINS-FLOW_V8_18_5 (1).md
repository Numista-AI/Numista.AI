# COS_SCORE - P7 ADD-COINS-FLOW V8.18.5
Scorer: Grok CoS | 19 Oct 2026 ~4:05 PM ET | Commit 4531f45d on p7-v8.9 (parent a6d14b45) | Order: NET-354

## VERDICT: FAIL (small) - build V8.18.6 (one backend item)

Re-run by Grok CoS on 4531f45d (worktree Temp\p7v89_build): `flutter test --reporter compact` = 595 pass, 0 fail ("All tests passed!"); `pytest tests/test_cert_lookup.py` = 18 passed. Big step forward: 6 of 7 items are done right.

| # | NET-354 item | Grade | Evidence |
|---|---|---|---|
| 1 | ONE error card, 3 x 56px buttons | PASS | hub:3041-3046 `_buildScanErrorCard({String? errorMessage, VoidCallback? onRetry, VoidCallback? onChoosePhoto, VoidCallback? onManual})`; Try again / Choose a photo instead / Enter manually all `minimumSize: const Size(140, 56)`; Photo ID (hub:5108+) now calls `_buildScanErrorCard(errorMessage: _camError, ...)`; duplicate container deleted. Test `p7_v8185_photo_id_error_shows_all_three_buttons` finds all 3 labels at >= 56px. Nit (P7.1): the no-camera case lost its special layout; 'Try again' is now primary even when there is no camera. |
| 2 | SAME cert reader, both endpoints | FAIL | `extract_cert_from_image()` (cert_routes:383) is real and `/api/scan_cert_number_upload` uses it. But in `identify_coin_photo` (main:6361-6373) it only runs as a fallback `if not final_cert:` AFTER pass 1/pass 2. Three problems: (a) when pass 1/2 return a cert (the normal slab case) the old reader still wins, so the two endpoints can still disagree; (b) it runs on every raw (no-slab) coin photo, up to twice (image A then B), synchronously inside an async route (blocks the event loop), with no timeout and outside the 28 s `GEMINI_IDENTIFY_BUDGET` clock (main:6194, 6261) - this undoes V8.18.2's 28 s cap and adds 1-2 Gemini calls (cost) to every non-slab Photo ID; (c) the error message is now `f"Scan failed: {e}"` (raw exception text shown to users; was the friendly "please enter cert # manually"). The pytest only covers the "pass 1 found no cert" fallback. |
| 3 | morgan_avatar.png 404 | PASS | `numista_backend/public/add_coins.html:305` now `src="/assets/assets/morgan_avatar.png"`. Grok CoS probe on p7-gate preview: `/assets/assets/morgan_avatar.png` = 200, `/assets/morgan_avatar.png` = 404. `git grep morgan_avatar -- *.html *.js` shows no other site page using the 404 path (Pitch Deck only, not hosted). |
| 4 | ValueKey finders | PASS | add_coin_manual_form:435 `ValueKey('manual_field_Mint Mark')`, :497 `ValueKey('manual_field_$key')`; zero `fields.at(` left in p7_v8_ux_safety_test.dart. |
| 5 | Camera header | PASS | numista_mobile/firebase.json:237 `"camera=(self), microphone=(), geolocation=(), payment=()"`. Branch only; live still has camera=() until a cherry-picked hosting deploy on Eric's YES. |
| 6 | localhost caller | PASS (with note) | Grok CoS traced callers: only `desktop_agent_download_screen.dart:71/76` and `microscope_scan_screen.dart:86/113` call `isServerRunning()`/`getStatus()`, both guarded by `isMicroscopeConfigured()` (hardware_service:120, 143). Hub has no direct caller. HttpOverrides test proves 0 localhost requests on hub load. Note: HttpOverrides covers dart:io only, not the web build, so FT checks the preview console for `localhost:8443` during re-gate. |
| 7 | Config test glob (should) | PASS | test:1963-1986 globs `web/**/*.html` containing `firebaseConfig`, checks web apiKey/appId from firebase_options and no Android key, asserts >= 1 file checked. |
| R | GEMINI38 quotes real lines | PASS | Spot-checked hub:3041-3054, 3094-3122 against `git diff a6d14b45 4531f45d`: verbatim. Gemini did not catch the item 2 budget/blocking issue. |
| H | Hygiene | NOTE | No EXECUTE_DONE_P7_V8_18_5.md filed (NET-356 + baton log cover it this time). No main touch, no deploy. |

## V8.18.6 order (NET-357)
Item 2 only. Make the shared reader THE cert source in identify_coin_photo, inside the budget:
- Run `extract_cert_from_image` via `asyncio.to_thread(...)` wrapped in `asyncio.wait_for(..., timeout=<remaining GEMINI_IDENTIFY_BUDGET>)`, concurrently with pass 1 (`asyncio.gather` or a task started before pass 1), so it adds no wall-clock time. Image A only (one call); B only if budget remains >= 3 s.
- When the shared reader returns a cert, it wins over pass1/pass2 `cert_number`. Pass 1/2 cert is used only if the shared reader returns none.
- Restore the friendly user message on failure; log the exception server-side only.
- pytests: (a) pass 1 mock returns cert X, shared reader mock returns Y -> identify returns Y, and scan_cert_number_upload returns Y; (b) shared reader mock sleeps past the budget -> identify still returns in < 28 s with no cert and no 500.
Keep everything else from 4531f45d as is.

## Next
Baton -> AGCOS for V8.18.6. After a PASS: Grok CoS refreshes p7-gate preview (one fixed channel) + tagged backend, then UX Designer + Field Tester re-gate (HARD: invoice PDFs E2E, camera on preview with the new header, cert-photo scan under 30 s, preview console shows no localhost:8443 on hub load).
