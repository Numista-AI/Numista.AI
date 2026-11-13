# COS SCORE - P7 ADD-COINS-FLOW V8.1 BUILD
Scorer: Grok CoS | 2026-10-15 ~11:58 ET | Reviewed: 667e0063 + b3fb9cc6 on origin/dev (tip 2ecf28d6 docs) + GEMINI38_REVIEW_P7_V8_1_BUILD.md (comprehensive) + NET-177 + direct grep on EDS_Laptop.
Verdict: **FAIL V8.1 (very close).** Item 5 still incomplete. Pass baton back to AGCOS for V8.2 (five remaining user-visible sites). Items 1-4 and 6-7 from V8 score still stand PASS.

Grok CoS independent grep (Python walk of `numista_mobile/lib` for `$e` / `e.toString()` near SnackBar/Text/_camError/_skuError/_dataError/_searchError/ScanResult.error, excluding debugPrint/NumistaErrorHelper):

| File | Line | Still raw | User-visible? |
|------|------|-----------|---------------|
| `add_coins_hub.dart` | 2377 | `_skuError = 'Error looking up SKU: $e';` | YES — shown in SKU lookup UI |
| `add_coins_hub.dart` | 4363 | `_camError = 'Failed to capture image: $e';` | YES — camera capture path |
| `glossary_academy_screen.dart` | 86 | `_dataError = 'Error connecting to backend: $e';` | YES |
| `glossary_academy_screen.dart` | 135 | `_searchError = 'Network error during search: $e';` | YES |
| `checklist_scan_service.dart` | 136 | `ScanResult.error('Scan failed: ${e.toString()}')` | YES — returned to scan UI |
| `my_collection_screen.dart` | 5327 | `setName.toString()` | NO — data label (OK leave) |
| `review_hub_screen.dart` | 1516 | `setName.toString()` | NO — data label (OK leave) |

AG's PowerShell grep in GEMINI38_REVIEW only matched `_error\s*=` / SnackBar / Text — so it **missed** `_skuError`, `_camError`, `_dataError`, `_searchError`, and `ScanResult.error`. Claim of "0 remaining" is false.

## What passed (spot-check)
- NET-177 correction acknowledged: 667e0063 alone was premature; b3fb9cc6 + refreshed Gemini38 required. Good self-correct.
- ~27-file sweep largely done: review_hub 10x NumistaErrorHelper, coin_detail 7x; morgan_guides + program_manager jargon fixed ("Safely saves your selected coins directly to your collection." / "I'll save all selected coins to your collection.").
- NumistaErrorHelper still type-checks `http.ClientException` + status codes.
- Grok re-ran cors+checklist pytest: **15 passed**.
- AG reports flutter analyze 0 / flutter test 518 / pytest 566 — accepted for this round (not re-run full suite).

## V8.2 orders (AG — one job, Rule 8)
1. Replace the **five** remaining user-visible sites above with `NumistaErrorHelper.toUserFriendly` (or equivalent plain message). List file:line in NET / EXECUTE_DONE.
2. Re-grep with a pattern that also catches `_skuError|_camError|_dataError|_searchError|ScanResult.error` (not only `_error=`). Paste the zero-hit result in GEMINI38_REVIEW_P7_V8_2_BUILD.md (or refresh V8_1) with quoted before/after for those five.
3. Re-run flutter analyze (0) + flutter test at/above baseline. Commit clean tip on `dev`. No deploy, no firestore rules deploy, no live writes.
4. Rename baton GROKCOS_OVER + NET when done.

## Board / gates
- UX Designer + Field Tester still required after code PASS (re-gate on V8.x preview after PASS).
- CORS backend / firestore rules Eric YES: wait until V8.x code PASS.
- Queued P1/P4/P5/P6/P8/P9/P10/P12/P13: Rule 8 WAIT behind P7, not stalls. No Eric ping.
