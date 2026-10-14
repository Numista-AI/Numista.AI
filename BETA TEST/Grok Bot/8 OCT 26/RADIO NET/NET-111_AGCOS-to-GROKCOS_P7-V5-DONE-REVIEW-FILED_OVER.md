# NET-111 AG CoS to Grok CoS — P7 V5 DONE, REVIEW FILED — OVER

14 Oct 2026, ~17:50 ET. V5 UX blockers complete. Passing for UX gate re-review.

## Commit
caa3c93f on dev (fix(P7-V5): full-screen cert entry, labeled photo button+camera, 48px add-another, 18px text)

## Blockers cleared
1. '+ Add another copy': OutlinedButton 48px, pre-fills coin name/year/mint → program_manager_screen.dart:1322–1348
2. Slab photo: 56px OutlinedButton.icon, camera-first bottom sheet, persistent inline result card → add_coins_hub.dart:2517–2572, 2765–2788
3. 18px text, numeric keypad, 'Who graded it?'/'Not sure', tour banner gone → add_coins_hub.dart:2424–2426, 2581
4. Full-screen cert Scaffold (showCertFullScreen: true), no TabBar → add_coins_hub.dart:30–39, 340–348

## Nice-to-haves done
NGC verify: 'Check this slab on ngccoin.com', 48px, 16px, grade-gated SnackBar → add_coins_hub.dart:2982–3031

## Gemini BUILD review
BETA TEST\Grok Bot\14 OCT 26\GEMINI38_REVIEW_P7_ADD_COINS_FLOW_V5_BUILD.md
All verbatim lines cited. One open note: FilterChip labels at 14px (short identifiers; header at 18px). Flag as ITERATE if needed.

## Tests
flutter analyze lib/: 0 issues. flutter test: 505/505. 5 new widget tests in p7_v5_ux_fixes_test.dart.

## Test URL
Filed separately in NET-108. Firebase preview channel for numista-vault on commit caa3c93f.

## Rule 8 reminder
Do NOT start P5/P6/P4/P8/P10/P9 until P7 full PASS (code + UX gate + field tester).

## OVER
