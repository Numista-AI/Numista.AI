# EXECUTE_DONE — T3 REQ_032 UX V3 + T3b REQ_032B Alt Site V3
Filed by: AG CoS — 2026-10-13 ~9:55 AM ET
Commit: 9a0b20b8 (dev, combined with T1B+T2V3)
Branch: dev. No deploy. No live writes.

## Flutter test result
**433 passed, 0 failed** (flutter test --reporter compact, 2026-10-13)

## Flutter analyze
**No issues found!** (2026-10-13)

## Pytest result (for T3b rules-related backend)
**491 passed, 0 failed** (2026-10-13)

---

## T3 — REQ_032 UX V3 fixes (from COS_SCORE_REQ032_UX_BUILD_V2.md)

### Fix 1 — PIN focus re-requested on tap (REQUIRED)
`login_screen.dart:633` — `_PinBoxRow` wrapped in `GestureDetector(onTap: () => _pinKeyboardFocus.requestFocus(), child: ...)`.
`login_screen.dart:55` — `_pinKeyboardFocus.requestFocus()` already called in `_onKeypadDigit()` so keypad taps also re-request focus.
Scenario: user types email (focus leaves PIN row), taps PIN boxes → keyboard focus is reclaimed → digits go into PIN boxes.

### Fix 2 — Last 2 hard-coded font sizes below 14 tokenized (REQUIRED)
`login_screen.dart:1025` — `_strengthHint` label: `fontSize: 12` → `NumistaTheme.textBodySm`
`login_screen.dart:1045` — `_StatBadge` label: `fontSize: 11` → `NumistaTheme.textBodySm`

Test (`ux_fixes_test.dart:40-77`) — scoped by class boundary (all lines before `class FreeScanPreviewScreen`), not a fixed line count, so edits don't shift the window.

**Note:** Lines 1250 (`fontSize: 11`) and 1301 (`fontSize: 11`) are inside `FreeScanPreviewScreen`, which is outside the login form scope. Those will be addressed in a separate pass.

### Existing fixes carried forward (V1+V2)
- `NumistaTheme.textCaption = 14.0` (raised from 12)
- Forgot PIN: `textLg` font + 44dp tap target + visible in both PIN and password mode
- Keypad wrapped in `Center(ConstrainedBox(maxWidth: 320))`
- `_pinKeyboardFocus` with `autofocus: true` and `RawKeyboardListener` for physical keyboard

---

## T3b — REQ_032B Alt Site V3 fixes (from COS_SCORE_REQ032B_BUILD_V2.md)

### Fix 1 — Entitlement field guard on users/{email} (P0, was LIVE)
`numista_mobile/firestore.rules` — `match /users/{email}`:
- Added `_serverOnlyKeys()` returning `['tier','stripe_tier','beta_tester','is_lifetime_family_estate','is_ai_qc_account','is_bot_account','sandbox_cleared','admin']`
- `allow create: if isOwner(email) && _noEntitlementOnCreate()`
- `allow update: if isOwner(email) && _noEntitlementChange()`
Owner can no longer give themselves tier/beta_tester/etc. Server sets those via Admin SDK only.

### Fix 2 — Coin guards no longer overridden by wildcard (P0 follow-up)
Wildcard subcollection exclusion list at rules:126 and :131 now includes `'coins'` and `'profile'`:
```
!(sub in ['settings', 'estate_reports', 'morgan_action_log', 'trash', 'audit_log', 'coins', 'profile'])
```
The explicit `match /users/{email}/coins/{coinId}` block (rules:41-67) now wins cleanly, including the `is_demo` guards.

### Fix 3 — Emulator tests (BLOCKED by Java)
`firestore.rules.test.js` — Addendum C tests added (7 tests):
- DENY owner sets `tier` on users/{email}
- DENY owner sets `beta_tester` on users/{email}
- ALLOW owner sets safe field (`display_name`) on users/{email}
- DENY owner creates doc with `tier` key
- DENY owner sets `stripe_tier`
- DENY owner creates coin with `is_demo: true`
- DENY owner updates coin with `is_demo: true`

**Emulator NOT run — Java not installed on this machine:**
```
$ java -version
java : The term 'java' is not recognized as a cmdlet, function, script file, or operable program.
```
Firebase Firestore emulator requires Java 11+. Tests are correctly structured with `@firebase/rules-unit-testing` v4. Install Java 11+ and run:
```
npx firebase emulators:exec --only firestore "npx jest firestore.rules.test.js"
```

### Fix 4 — UiVariantService fail-safe (V2, carried forward)
`ui_variant_service.dart`: non-200 response → `_current = UiVariant.classic` (fail-safe, was keeping previous value)

### Fix 5 — Banner textBodySm (V2, carried forward)
`base_layout.dart:~1337`: banner uses `NumistaTheme.textBodySm` explicitly (not `textCaption`)

### Fix 6 — EXECUTE_DONE doc inaccuracies (V2, carried forward)
Previous EXECUTE_DONE corrected: allowlist is `eric.seaman@yahoo.com + eric@numista.ai` only (not Eric+AJ); line cite corrected.

### Fix 4 (from T3b V2 score) — Backend firestore.rules drift documented
`numista_backend/firestore.rules` — header added: `# IMPORTANT: NOT DEPLOYED — backend firebase.json only has functions`. File is kept for reference only; live rules are in numista_mobile/firestore.rules.

## Deploy note
The Firestore rules fix (entitlement field guard + coin guard) is a live security hole. When Java is installed and emulator tests pass, a rules-only deploy of `numista_mobile/firestore.rules` is a candidate for Eric's typed YES, ahead of the full T3b UI features.
