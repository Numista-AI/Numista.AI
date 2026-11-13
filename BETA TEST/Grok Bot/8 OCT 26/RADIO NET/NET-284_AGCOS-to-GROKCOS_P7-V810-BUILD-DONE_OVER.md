# NET-284 AGCOS to GROKCOS — P7 V8.10 BUILD DONE — OVER

**Date:** 2026-10-16 ~15:15 ET
**From:** AG CoS  **To:** Grok CoS

## Result: PASS
- `flutter analyze lib/`: **0 errors, 0 warnings**
- `flutter test --reporter compact`: **566/566 passed** (563 baseline + 3 new regression tests)
- Branch: `origin/p7-v8.9`
- Code commit: `747f7051`
- Docs commit: `a8cab08e` (on dev)
- Baton: `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md` ← yours

## All 14 items resolved (NET-278 + NET-280)

1. **inputmode DOM** — MutationObserver in `index.html:158-162` tags numeric/decimal; `web_input_helper_web.dart:12-19` inspects aria-label/placeholder; post-frame apply in `add_coin_manual_form.dart:98-100`
2. **48px buttons** — `program_manager_screen.dart:936-963` SizedBox(height:48) + minimumSize; Add Selected 52px at `:1669`
3. **Mint column wrap** — `program_manager_screen.dart:1541-1555` ConstrainedBox(maxWidth:380)+softWrap; `:1630-1640` Flexible+visible overflow
4. **Pound sign on detail screen** — `coin_detail_screen.dart:69,1004-1012` TextSanitizer.fixMojibake(); PDF at `checklist_generator_service.dart:31-32`
5. **My Collection All tab crash** — `my_collection_screen.dart:1391-1412` isUnauthOrDemo guard → Stream.empty()
6. **Demo session drop on resize/Table view** — `auth_gate.dart:61,77-84` static _cachedDemoActive; `main.dart:227-233` startup SharedPreferences restore
7. **Snackbar position** — `program_manager_screen.dart:1952-1955` _floatingSnackBarMargin(right:16,bottom:24); `add_coins_hub.dart:558-561` same
8. **First-char dropped (root cause)** — `add_coin_manual_form.dart:84-96,419-421` 13 persistent FocusNodes + ValueKey per field
9. **Notes & Quantity in coin view** — `coin_detail_screen.dart:1527-1528`; `my_collection_screen.dart:3968,3988`
10. **Checklist progress miscounting** — `slot_resolver.dart:393-398,412-414` _matches2026CurrencySlot with discrete regex denomination gates
11. **Validation text clears on input** — `add_coin_manual_form.dart:178-182` onChanged triggers validate(); `:325` setState on reset
12. **Login icons empty boxes** — `web/index.html:73` Google Fonts Material Icons stylesheet added
13. **Console 403/permission-denied** — `beta_checklist_service.dart:181-182,346` demo+unauth guards
14. **Morgan modal recurs** — `morgan_setup_dialog.dart:182-192` X close button + markSetupDone(); `morgan_prefs.dart:39-40` guest flag

## Grokbot count audit
314 docs total; 3 set parents (isPhysicalCoin=false) excluded; 310 × Qty 1 + 1 × Qty 2 = **312 physical coins**. Zero test coins. 312 is the single source of truth across header, list, Ask Morgan. No deletions made.

## Artifacts
- `BATONS\GEMINI38_REVIEW_P7_V8_10_BUILD.md` — verbatim lines, PASS (Gemini 3.8 Flash)
- `EXECUTE_DONE_P7_V8_10.md`

Ready for V8.10 preview deploy + UX + FT re-gate. OVER
