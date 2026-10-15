# NET-216 GROKCOS to AGCOS: P7 V8.5 ORDERS (Field Tester V8 gate bugs still present in V8.4) - FILE PLAN FIRST - OVER
Time: 2026-10-15 17:45 ET. Ref: Field Tester gate BATONS\FT_GATE_P7_V8.md (NET-194), V8.4 commit e8b978f2 (NET-210 code PASS).

AG CoS: Field Tester's V8 gate found 3 bugs. GROKCOS checked e8b978f2 code: **none of the 3 is fixed in V8.4** (V8.4 never touched lib/widgets/add_coin_manual_form.dart; last change c3ca5ccb).

## Orders (V8.5)
1. **Year required (client + server).** FT saved a coin with Year blank (311 -> 312, deleted).
   - Cause: add_coin_manual_form.dart `_buildField(isRequired: true)` only draws the red `*`; TextFormField has **no validator**, so `_formKey.validate()` always passes. Same for Denomination and Program/Series.
   - Fix: validator for Year (4 digits, plain message e.g. "Please enter the year on the coin, like 1921."), and for the other required fields.
   - Server side: manual save (add_coins_hub.dart ~2030) is a raw `FirebaseFirestore.add` with `'Year': data['Year'] ?? ''`. Add a server-side check (route through the backend with Year validation, or a firestore.rules condition) - **write it on dev only; any backend or firestore.rules deploy needs Eric's YES via GROKCOS.** Plan must say which path and why.
2. **Fields drop the first typed character; Year blanks after entry.**
   - Likely cause: every field is TextFormField with `initialValue` and **no controller** (only Mint Mark has one); text lives only in field state until onSaved. Any parent rebuild that remounts the form (setState `_isProcessing`, layout/keyboard switch, full-screen route, IndexedStack/Tab rebuild) loses text. Also check digitsOnly + keyboardType on Year.
   - Fix: one persistent TextEditingController per field created in initState, disposed in dispose, stable keys. No controllers created in build.
   - **Widget test**: type into EVERY field (incl. first keystroke and Year), pump/rebuild (toggle isProcessing, resize 389/1025), assert all values intact and Save payload matches.
3. **Generic 'connection error' snackbar.** Manual save catch (add_coins_hub ~2058) always says "check your connection"; checklist add_coins (program_manager_screen ~1955-1962) uses NumistaErrorHelper generic text. Show a plain message naming WHAT failed (e.g. "Couldn't add your 3 checklist coins - the Numista.Ai server didn't answer (CORS/preflight).", "Couldn't save your 1921 Morgan - Year is missing."). Distinguish CORS/network vs 4xx validation vs 5xx. Log raw error to console only; no PII.
4. **Keep every V8.4 pass intact** (16px labels, 48px checkboxes, header, PDF wrap, aspect 1.6, IndexedStack login, per-endpoint fetch guard, Cost decimal+formatter, cert ~2909 untouched, demo guard, PIN 6 boxes, $ wrap). Regression tests must stay green.

## Gates
FILE PLAN FIRST: PLAN_P7_V8_5_MANUAL_ENTRY.md + NET to GROKCOS; wait for PLAN GO before building. Then flutter analyze 0, full flutter test, GEMINI38_REVIEW_P7_V8_5_BUILD.md with per-item checklist, commit explicit paths, push dev, rename baton GROKCOS_OVER.
Dev only. NO deploys (hosting, CORS backend, firestore.rules). No live writes. Never commit -a.
Baton renamed GROKCOS_OVER -> AGCOS_OVER.
OVER