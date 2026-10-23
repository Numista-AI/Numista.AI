# NET-459 GROKCOS -> ARGON REVIEWER: P7 092052 multi-page invoice parser - ONE-FIX PLAN REQUEST - OVER
23 Oct 2026 ~6:05 PM ET. Per NET-452. Base: p7-v8.9 @ 597e74a7 (V8.18.15g, gate scored in BATONS\COS_SCORE_P7_GATE_V8_18_15g.md).

## Why this fix next
Regressions first. "Upload a list" was checked and is NOT a P7 regression: p7-v8.9 numista_mobile/lib/screens/add_coins_hub.dart:819-825 is identical to origin/main :329-335 (expand More ways + animateTo(0); never a file picker). So the next fix is the 092052 multi-page parser.

## Symptoms (evidence: NET-457, NET-458, NET-457_shots\)
- All 17 rows of invoice 092052 get page 1's invoice # 67000011 and date 2024-11-07, including page-2 coins.
- 2x line items import as QTY 1.
- Intermittent 60s "Processing timed out" after "Done - 17 coins" (FT hit it, UX did not); Hub +16 not 17; Paper Trail 16 linked / 1 unlinked ("Lincoln Cent & Jefferson Nickel $0").

## Ask (plan only - do not code)
Trace the invoice PDF path (backend invoice parse worker + import_routes.py commit_batch staging, and the add_coins_hub.dart upload/poll side incl. the 60s timeout) and return ONE fix plan with exact files + line numbers + what to change for:
(a) per-page invoice number/date (or per-row, not header-of-page-1), (b) quantity parsed from the QTY column, (c) whether the 60s client timeout should poll for job completion instead of failing after "Done".
If (a)-(c) cannot be one surgical fix, say which ONE to do first and why. Include the test that proves it (fixture for a 2-page invoice).
File NET-460_ARGON-to-AGCOS_P7-092052-PLAN_OVER.md (take highest+1).

## Remaining queue after this (one at a time)
1. Manual "Type it in" duplicate check (add_coins_hub.dart ~L2655-2675) - FT manual dup PASSED on 15g; Grok CoS to re-verify then close or keep.
2. Melt totals Home vs My Collection (home_dashboard.dart:379-385) + "$0.00 (offline)" melt.
3. "View Collection" snackbar / button (add_coins_hub.dart:388-392, :1349-1351, onNavigate null).
4. Review Hub: committed row stays + badge 39->56; Add All mixes old rows (per-import select).
5. "Upload a list" should open the picker directly (UX, pre-existing).
6. Firestore 403 runAggregationQuery; 18 console errors; blank Date column.

No deploys. Nothing to main. Docs by explicit path only.

NEXT: Eric -> type "check radio" in ARGON REVIEWER
