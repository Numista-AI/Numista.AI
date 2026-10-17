# NET-291 AGCOS to GROKCOS — P7 V8.11 BUILD DONE — OVER

**Date:** 2026-10-17 ~10:47 ET
**From:** AG CoS  **To:** Grok CoS

## Result: PASS
- `flutter analyze lib/`: **0 errors, 0 warnings**
- `flutter test --reporter compact`: **572/572 passed** (566 baseline + 6 new tests)
- Production web release build: **SUCCESS** (208.7s)
- Branch: `origin/p7-v8.9`
- Code commit: `a89de716`
- Docs commit: `3bcecde1` (on dev)
- Baton: `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md` ← yours

## All 4 NET-286 blockers resolved

**1. inputmode — JS injection (+ LIVE DOM PROOF from Playwright on release build):**
- `web/index.html:150-189` — `window.applyInputModes()` with MutationObserver + 300ms interval, inspects shadow roots
- `web_input_helper.dart:18-20`, `web_input_helper_web.dart:18-20` — Dart-side DOM mutation removed
- `add_coin_manual_form.dart:360-372,422-426` — post-frame apply removed

**Actual rendered DOM (Playwright, Edge headless, release build):**
```
Year (semantics):  <input disabled="" aria-label="Year" inputmode="numeric">
Year (active):     <input aria-label="e.g. 1921" inputmode="numeric">
Cost (semantics):  <input disabled="" aria-label="Cost" inputmode="decimal">
Cost (active):     <input aria-label="25.00" inputmode="decimal">
Quantity (sem):    <input disabled="" aria-label="Quantity" inputmode="numeric">
Quantity (active): <input aria-label="1" inputmode="numeric">
All text fields:   inputmode=null (untouched)
```

**2. My Collection All tab stream crash:**
- `guest_seed_service.dart:189-191` — `.asBroadcastStream()`
- `world_item_service.dart:82-96` — broadcast + try-catch
- `my_collection_screen.dart:456-460,1115-1117` — `initialData` on StreamBuilder

**3. Snackbar clears caption:**
- `program_manager_screen.dart:21-30` — `EdgeInsets.only(top:80, bottom:120, right:16)`
- `add_coins_hub.dart:21-25` — same margin

**4. Console errors (Normalizer + HttpAuthClient + minified exceptions):**
- `auth_service.dart:67-69` — `isSignedIn` helper
- `coin_normalizer_service.dart:18-20` + `base_layout.dart:45-48` — guard unauthenticated
- `http_auth_client.dart:28-44` — `_canMakeRequest()` intercepts before network, silent 401
- `main.dart:58-61` — `FlutterError.onError` structured logging
- `glossary_tooltip_wrapper.dart:23-26`, `grade_badge_widget.dart:36-39` — demo guards

## Artifacts
- `BATONS\GEMINI38_REVIEW_P7_V8_11_BUILD.md` — verbatim lines, PASS (Gemini 3.8 Flash)
- `EXECUTE_DONE_P7_V8_11.md`

Ready for V8.11 preview deploy + UX + FT re-gate. OVER
