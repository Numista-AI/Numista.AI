# COS SCORE - P7 ADD-COINS-FLOW V8.4 PLAN.V1
Scorer: Grok CoS | 2026-10-15 ~15:58 ET | Reviewed: PLAN_P7_V8_4_UX_FIXES.md + COS_SCORE_P7_ADD-COINS-FLOW_V8_3.md + NET-204/205 + independent spot-check on EDS_Laptop (program_manager_screen.dart, add_coins_hub.dart, login_screen.dart, upcoming_releases_service.dart at HEAD of working tree / last V8.3 commit lineage).
Verdict: **PLAN GO with the conditions below.** Build on dev only. Tier 1/2 UX + network retry so GEMINI38_REVIEW with code quoted is required before the baton comes back.

| # | Item | Score | Notes / conditions |
|---|------|-------|-------|
| 1 | Phone checklist labels / checkbox / header / PDF wrap | **PASS** | Spot-check confirms: years 12 (748), pct/Collected 12 (755-756), Advances 10 (772), subtitle 12 (957); checkbox SizedBox 24x24 (1435-1437); header title no maxLines/ellipsis (863-867); Print+Download PDF bare siblings in Row (870-904). Plan's 16px floor, 48x48 checkbox, maxLines:2+ellipsis, Wrap on Print/PDF matches V8.3 FAIL. |
| 2 | View Checklist + Advances overflow | **PASS w/ conditions** | childAspectRatio still `isNarrow ? 2.6 : 1.4` (477/609); View Checklist OutlinedButton has no minimumSize (781-796). Plan's 1.4→1.6 + 48px min + overflow tests at 389 and 1025 is the right next step. **CONDITION:** if 1.6 still overflows at 1025 in the widget test, fall back to the plan's alternate (`MainAxisSize.min` / drop Spacer) — do not ship a green analyze with a failing overflow test. |
| 3 | Cost decimal + Qty digitsOnly | **PASS w/ conditions (line-number correction)** | **ACCURACY FLAG:** PLAN and prior NET-204 cite `add_coins_hub.dart:2906` as Cost Paid with `decimal: false`. Spot-check: **2906 is the cert-number TextField** (`_pcgsSingleCtrl`) — `decimal: false` is correct there; do **not** change it to decimal. Real Cost Paid / purchase-cost gaps: (a) `_camInputField('Cost Paid', _picCost)` at ~4991 passes **no** keyboardType; (b) purchase-cost dialog `costCtrl` at ~2576 is `TextInputType.number` (no decimal); (c) mint-set `Purchase Price` at ~1690-1691 is `TextInputType.number` (no decimal). Year already has number+digitsOnly at ~3189 and ~4967. **CONDITION: (1)** leave 2906 cert keyboard alone; **(2)** set Cost Paid / Purchase Price / purchase-cost paths to `numberWithOptions(decimal: true)` + a decimal allow-formatter; **(3)** sweep Qty fields for `number` + `digitsOnly` where a Qty TextField exists; **(4)** report DOM `inputmode` for AddCoinManualForm Cost (already decimal:true there per V8.3) in GEMINI38_REVIEW. |
| 4 | Manual Entry CTA polish | **PASS** | Spot-check: subtitle fontSize 14 (718); button label default (732). Plan's 16px subtitle + 16px button label matches V8.3 polish. |
| 6 | Login fixed-height TabBarView | **PASS w/ conditions** | Spot-check: `SizedBox(height: ... 280/560/360)` still wraps TabBarView (487-494). IndexedStack at natural height is the right fix. **CONDITION:** wire `_tabCtrl` listener / `setState` so IndexedStack index updates on tab change; keep **one** outer scroll; 389px (or 360x680) widget test must show Sign In and Create buttons fully visible with no RenderFlex overflow. |
| 7 | mint-releases per-endpoint guard | **PASS** | Spot-check confirms shared `static bool _fetchAttempted` (82) and single `_cacheKey` (78) used by both `fetchUpcoming` and `fetchAll`. Plan's `Set<String> _attempted` + `_cacheKeyFor(endpoint)` + unit test (2 distinct calls then 0 on repeat) matches V8.3 FAIL exactly. |

## Gates after V8.4 (required before return)
1. `flutter analyze` → 0 issues
2. `flutter test test/p7_v8_ux_safety_test.dart` → all pass (include new overflow + login + fetch-guard tests)
3. Prefer full `flutter test` if time allows; at minimum the p7_v8 suite must be green
4. **GEMINI38_REVIEW_P7_V8_4_BUILD.md** with verbatim before/after **and a per-condition checklist** (especially item 3 corrected sites — do not quote 2906 as Cost Paid)
5. Commit + push **dev only** → rename baton to GROKCOS_OVER → NET for score
6. **NO deploys** (no live hosting, no backend CORS, no firestore.rules) without Eric typed YES

## Housekeeping
- Baton stays **AGCOS_OVER** (build now). AG renames to GROKCOS_OVER when build + GEMINI38_REVIEW are filed.
- Rule 8: P1/P4/P5/P6/P8/P9/P10 stay WAIT behind P7 — not stalls. No ERIC baton. No deploy YES.
- Commit only explicit baton/score/NET/plan paths. Do not commit numista_mobile/.firebase caches.
