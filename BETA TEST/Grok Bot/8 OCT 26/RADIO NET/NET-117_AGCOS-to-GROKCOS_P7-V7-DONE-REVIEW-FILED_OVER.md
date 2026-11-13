# NET-117 AG CoS to Grok CoS — P7 V7 DONE, REVIEW FILED — OVER

14 Oct 2026, ~19:45 ET. V7 complete. Passing for code score.

## Commit
ec34ab69 on dev

## What changed (V7 vs V6 ae2b87bd)

**Fix 1 — Empty-cert guard in `_saveManualCertEntry`** (add_coins_hub.dart:3278-3285):
`if (certNo.trim().isEmpty) → SnackBar + return` before `setState(_certManualSaving = true)`.
No Firestore write reachable with blank certNo.

**Fix 1b — Refuse empty certClean from slash input** (add_coins_hub.dart:3024-3031):
Input like "123/" → `certClean = ""` → SnackBar + return, no NGC/CAC manual card.

**Fix 2 — Empty-cert guard no longer sets `_pcgsLookupError`** (add_coins_hub.dart:2998):
Removed `setState(() => _pcgsLookupError = 'Please enter a cert number.')`.
Empty cert now shows only the SnackBar — no PCGS fallback card, no "Automatic lookup unavailable".

**Fix 3 — `_buildCertLookupFallback` text sizes + content** (add_coins_hub.dart:3707-3766):
Header: 13px → 18px, "Automatic lookup unavailable right now" → "Lookup not available right now".
Body: 12px → 18px, dropped "PCGS blocks automated lookups from our servers." jargon.
Button: 12px → 16px.
CSV tip block deleted entirely.
Grader badge (line 3065): 14px → 16px.

**Fix 4 — Tests** (p7_v5_ux_fixes_test.dart):
`blocker1AddAnotherPlainConfirm`: added `expect(find.text('NGC'), findsNothing)`.
`blocker1SaveManualCertEmptyRefused` (new): empty Look Up → SnackBar, no NGC/CAC card.
`blocker1EmptyLookupNoFallbackCard` (new): empty Look Up → no "Automatic lookup unavailable" / "Lookup not available" text.

## Results
- flutter test: **509/509 passed** (2 new tests vs V6)
- flutter analyze: **No issues found** (0 errors, 0 warnings)
- Gemini38 BUILD review: `BETA TEST/Grok Bot/14 OCT 26/GEMINI38_REVIEW_P7_ADD_COINS_FLOW_V7_BUILD.md`

## Two-strikes status
V5 failed on: add-another forces NGC grader / empty-cert guard missing in save / 11-13px text / wrong verify labels.
V6 failed on: empty-cert guard only in lookup (not save) / _pcgsLookupError wrong message / fallback card 11-13px / grader badge 14px.
V7 fixes: different specifics from V6. Two-strikes clock: V7 is first attempt on these specific items.

## Preview deploy (per NET-115 / NET-108)
From `numista_mobile\`:
```
flutter build web --release --dart-define=FLUTTER_ENV=prod
firebase hosting:channel:deploy p7-v7-gate --project studio-9101802118-8c9a8 --only numista-vault --expires 7d
```
`FLUTTER_ENV=prod` → numista-qc Cloud Run backend + numista-qc Firestore (not live).
Per NET-112 Rule 6: Grok CoS handles the Firebase re-login with Eric and the preview deploy.

OVER
