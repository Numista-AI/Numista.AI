# COS SCORE - P7 ADD-COINS-FLOW V8.2 BUILD
Scorer: Grok CoS | 2026-10-15 ~12:28 ET | Reviewed: 6c68dd57 on origin/dev + GEMINI38_REVIEW_P7_V8_2_BUILD.md (verbatim before/after for all 5) + NET-179 + independent grep on EDS_Laptop.
Verdict: **PASS V8.2 (code).** All five V8.1 leftover user-visible raw-exception sites are fixed. Systemic `$e` / `e.toString()` user-visible candidates are clear. Items 1-4 and 6-7 from V8 score still stand PASS. Gates still pending before Eric deploy YES.

## V8.2 five sites (Grok spot-check on working tree tip)

| # | File | Line | After (verified) |
|---|------|------|------------------|
| 1 | `add_coins_hub.dart` | 2377 | `_skuError = NumistaErrorHelper.toUserFriendly(e);` |
| 2 | `add_coins_hub.dart` | 4363 | `_camError = NumistaErrorHelper.toUserFriendly(e)` |
| 3 | `glossary_academy_screen.dart` | 87 | `_dataError = NumistaErrorHelper.toUserFriendly(e);` (+ import) |
| 4 | `glossary_academy_screen.dart` | 136 | `_searchError = NumistaErrorHelper.toUserFriendly(e);` |
| 5 | `checklist_scan_service.dart` | 137 | `ScanResult.error(NumistaErrorHelper.toUserFriendly(e))` (+ import) |

Raw patterns from NET-178 (`Error looking up SKU:`, `Failed to capture image: $e`, `Error connecting to backend: $e`, `Network error during search: $e`, `Scan failed: ${e.toString()}`) — **zero hits**.

## Systemic grep (Grok, Python walk of `numista_mobile/lib`)
Candidates with `$e` / `e.toString()` near UI/error fields, excluding debugPrint/NumistaErrorHelper: **7**, all non-user-visible dumps:
- `add_coins_hub` / `login_screen` `isCorsLike` guards (boolean, not rendered)
- `my_collection` / `review_hub` `setName.toString()` data labels (OK)
- `batch_valuation_service` `ai_value_error` JSON field (service layer)

## Soft polish (NOT a fail; optional before/after preview)
Status-code strings still exist (not raw `$e`): e.g. `AI scan failed: Server returned ${statusCode}`, glossary `Status ${statusCode}`, `ScanResult.error('Server error ${statusCode}: $errorDetail')`. Prefer mapping through NumistaErrorHelper with `statusCode:` when convenient. Do not block PASS.

## Tests / review
- AG: flutter analyze 0; p7_v8_ux_safety_test 8/8; GEMINI38_REVIEW_P7_V8_2_BUILD.md with quoted before/after.
- Commit `6c68dd57` on `dev` (docs tips `2607f101` / `a75464cc` after). Clean tip vs origin/dev at score time.

## Next (Rule 8 — still one job: finish P7 gates)
1. GROKCOS: deploy **V8 preview** channel (hosting preview only, like p7-v7-gate). Do **not** deploy live, CORS backend, or firestore rules without Eric typed YES.
2. UX Designer + Field Tester re-gate on that V8 preview (test accounts only; no Eric collection writes).
3. After gates PASS: ask Eric for deploy YES (cherry-pick onto branch from main). Also then ask for CORS backend + firestore.rules YES if still needed for preview/live.
4. Queued P1/P4/P5/P6/P8/P9/P10/P12/P13: Rule 8 WAIT behind P7 gates. Not stalls. No Eric "check radio" ping.

## Board
- Baton stays **GROKCOS_OVER** (AWAITING V8 PREVIEW + UX/FT gates). No rename of holder.
- No ERIC baton yet (deploy YES after gates).
