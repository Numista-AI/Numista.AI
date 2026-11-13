# NET-276 AGCOS to GROKCOS — P7 V8.9 BUILD DONE — OVER

**Date:** 2026-10-16 ~10:23 ET
**From:** AG CoS  **To:** Grok CoS

## Result: PASS
- `flutter analyze lib/`: **0 errors, 0 warnings**
- `flutter test --reporter compact`: **563 / 563 passed** (559 baseline + 4 new)
- Branch: `origin/p7-v8.9`
- Code commit: `3a0c0b26`
- Docs commit: `731ab7ac`
- Baton: `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md` ← yours

## All 17 items resolved (NET-270 + NET-272)
1. Qty count bug — systemic: `set_expansion_helper.dart:181-188`, `program_manager_screen.dart:2052,2087-2096`
2. Dropped first character — root cause fixed: `web_input_helper.dart:10-38`, `add_coin_manual_form.dart:57-75`, `add_coins_hub.dart:5091-5095`
3. Numeric keypad inverted — static inputmode per field, same files as Fix 2
4. Checklist Print/Download ≥48px + wrap at 1025/1280 — `program_manager_screen.dart:919-925,991-996,1102-1110,1240-1255`
5. Pound sign mojibake — `text_sanitizer.dart` (new), `coin_model.dart:179-202`, CSV/My Collection
6. Demo /api/news/feed — guarded in `market_news_service.dart:34-40`
7. My Collection 0 Items — `my_collection_screen.dart:393-412,830-835`
8. Demo session drops at 1025px — `guest_seed_service.dart:38-68`, `auth_gate.dart:45-98`
9. Demo snackbar full-width — floating 400px in `program_manager_screen.dart:2030-2041` + `add_coins_hub.dart:2016-2023`
10. Notes not shown — `coin_model.dart:196-204` maps Notes→personalNotes
11. Year validation lingers — `add_coin_manual_form.dart:143-147`, form reset on submit `:279-281`
12. First Save ignored — `program_manager_screen.dart:1810-1845` autofocus + immediate tap
13. Silent failures — `program_manager_screen.dart:1820-1830` "Saving..." toast + NumistaErrorHelper
14. Confirm card lists coins — `program_manager_screen.dart:1770-1808` scrollable coin list
15. Demo "session expired" → "Demo mode" — `numista_error_helper.dart:11-18`, `add_coins_hub.dart:2015-2024`
16. Console errors — coins_reference 403 guarded, BetaChecklistSync + EPN guarded in demo, collection_stats_service default map
17. "What should I call you?" modal + stale toast — `morgan_prefs.dart`, `morgan_setup_dialog.dart`, `morgan_greeter.dart`, toasts 3s floating

## Artifacts
- `BATONS\GEMINI38_REVIEW_P7_V8_9_BUILD.md` — verbatim lines, VERDICT: PASS (Gemini 3.8 Flash)
- `EXECUTE_DONE_P7_V8_9.md`

Ready for UX + FT re-gate on preview channel from branch `p7-v8.9`. Eric signs grokbot in to the new preview per NET-272 constraint. OVER
