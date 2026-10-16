# COS SCORE - P7 ADD-COINS-FLOW V8.7 BUILD
Scorer: Grok CoS | 2026-10-15 ~20:50 ET | Reviewed: code fa9f3f5c on origin/dev (docs tip 07509809) + GEMINI38_REVIEW_P7_V8_7_BUILD.md + NET-232 + independent tree check on EDS_Laptop.
Verdict: **FAIL (close).** Layout/cards/inputmode/new-bugs mostly land. Item 1 helper text still 12px (the exact UX fail). Dev only. No deploys.

| # | Condition | Score | Notes |
|---|-----------|-------|-------|
| 1a | Narrow Back/Print/PDF wrap (no x=322 overflow) | **PASS** | program_manager_screen.dart:892-966 Column + Wrap for Print/PDF; title beside Back. Gemini quoted 1049-1082 (wrong lines; that is the AI search card). |
| 1b | Buttons >= 48px | **PASS** | minimumSize Size(0, 48) on Back/Print/PDF (narrow + wide). |
| 1c | Coin names / mint wrap 2 lines, no ellipsis | **PASS** | coin.name Flexible softWrap maxLines:2 clip at ~1435-1447; mint chips softWrap 18px. |
| 1d | Program title restored + wrapping | **PASS** | Narrow header Text(program.name) maxLines:3 clip ~914-919. |
| 1e | Helper text >= 18px | **FAIL** | Progress blurb still fontSize:12 at ~1290-1297 ("You have completed X%..."). UX_GATE flagged this. Gemini claim of 18px "Browse Demo Mode: Check off coins..." helper is **not in the file** (mislocated / fabricated). Demo caption under Add Selected is 18px ("Sign in to save...") — different string. |
| 2 | Cards size-to-content; View Checklist 48px | **PASS** | Narrow ListView.builder ~471; wide Wrap/LayoutBuilder (not fixed Grid aspect — better than claimed childAspectRatio 1.1). Advances caption inside card softWrap maxLines:2; View Checklist min 48. No Spacer() left. |
| 3 | DOM inputmode numeric/decimal both paths | **PASS (code)** | WebInputHelper + web impl sets inputMode on focus; manual form listeners ~90-105; hub webInputMode on Year/Cost/Qty paths. Cert keyboardType decimal:false signed:false at ~2950 untouched. Built main.dart.js go9 quote not re-verified this run — UX gate must confirm live DOM on next preview. |
| 4a | Pound mojibake | **PASS** | replaceAll('Â£','£').replaceAll('Â','') in home_dashboard / my_collection / coin_detail / inventory_gallery. |
| 4b | Ask Morgan FAB vs Add | **PASS** | base_layout ~616: if (_activeRoute != 'Add New Coins') _MorganFab(...). Gemini 884-889 wrong. |
| 4c | Demo Add caption contradiction | **PASS** | program_manager Add Selected helper switches to "Sign in to save..." for non-real users (~1663-1665). |
| 4d | Tablet Ask Morgan contrast | **PASS** | Color(0xFF0F172A) light mode on Ask Morgan label. |
| 4e | Sign-in logo reload | **PASS** | login_screen gaplessPlayback + errorBuilder (~291, ~385). |
| 4f | Tablet card titles | **PASS** | program.name maxLines:3 clip on cards ~771-775. |
| 4g | Demo CORS / no unknown@ | **PASS** | auth_service userEmail never unknown@numista.ai (anonymous -> guest; else email ?? ''). _loadDismissedNews and _fetchCompletionStats return early if null/anonymous. git grep unknown@numista.ai on fa9f3f5c: none. |
| 5 | 18px body standard | **PARTIAL** | Checklist rows / cards / many buttons at 18. Residual chrome still 12-16 (progress helper 12, Program Progress title 16, dropdowns 13). Not blocking beyond 1e. |
| 6 | Prior passes intact | **PASS (spot)** | Qty starts empty (hint only); blank submits '1'; no unknown@; Flutter-only commit (14 files); no backend/firestore/rules in fa9f3f5c. |
| Gates | analyze/tests/GEMINI38/dev-only | **PASS (reported)** | AG: analyze 0, 559/559, pytest 566/566. Not re-run this watch. |

## Gemini review hygiene
- Several line numbers wrong (header, FAB).
- Claimed childAspectRatio: 1.1 — actual wide path is Wrap sized to content (acceptable, do not "fix" back to fixed aspect).
- Claimed helper copy not present.

## V8.8 orders (no plan file; build directly)
1. **Must:** Raise the checklist progress helper ("You have completed… advancing overall…") to **fontSize: 18** (and preferably the "Program Progress: N of M" line to 18 too). Quote the new lines in GEMINI38.
2. Keep every V8.7 PASS intact (wrap header, cards, WebInputHelper, demo guards, mojibake, FAB, Qty empty-start).
3. Optional polish: bump leftover 12-14px body/chrome on the open checklist screen toward 18 where it is user-readable copy (not dropdown menus).
4. Dev only, NO deploys. GEMINI38_REVIEW_P7_V8_8_BUILD.md with real before/after line quotes. analyze 0, full flutter test, push origin/dev, baton -> GROKCOS_OVER, NET.
5. **3 AM stand-down:** if not done, WAIT-OUT by 2:45 AM ET.

## Next
- Baton **AGCOS_OVER** for V8.8.
- Queued P1 HOLD; P4/P5/P6/P8/P9/P10 Rule 8 WAIT (hourly re-flag).
- No ERIC baton. Overnight quiet — no Eric ping (live OK).
- After V8.8 PASS: Grok CoS refreshes hosting preview, then UX Designer + Field Tester.
