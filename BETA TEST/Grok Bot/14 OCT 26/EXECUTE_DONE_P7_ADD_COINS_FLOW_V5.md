# EXECUTE_DONE P7 ADD-COINS FLOW V5
Date: 2026-10-14 ~17:49 ET
Agent: AG CoS (Antigravity / Gemini 3.8)
Commit: caa3c93f on dev

## V5 Blockers — All 4 CLEARED

### BLOCKER 1 — "+ Add another copy" 48px labeled button
- File: program_manager_screen.dart:1322–1348
- OutlinedButton minimumSize: Size(0, 48), label '+ Add another copy'
- Opens AddCoinsHub(showCertFullScreen: true, initialCoinPreset: {name, year, mint})
- Coin name pre-fills via || normalization

### BLOCKER 2 — Slab photo: 56px labeled button, camera-first, persistent inline result
- File: add_coins_hub.dart:2518–2528 (button), 2765–2788 (_scanSlabPhoto), 2531–2572 (result card)
- OutlinedButton.icon minimumSize: Size(double.infinity, 56)
- Label: '📷 Take a photo of the label' (16px bold)
- Bottom sheet: camera first, gallery second
- Persistent inline result card with 'Yes, look it up' (48px) button — no SnackBar

### BLOCKER 3 — 18px text, 56px fields, numeric keypad, jargon removed, banner deleted
- File: add_coins_hub.dart:2424–2426, 2430–2445, 2513, 2581
- 'Who graded it?' at 18px Color(0xFF334155)
- 'Not sure' replaces 'Auto'; chips: Not sure / PCGS / NGC / CAC
- keyboardType: TextInputType.numberWithOptions(decimal: false, signed: false)
- Tour banner ('Explore 7 Ways to Add Coins') removed entirely

### BLOCKER 4 — Cert entry full-screen (no 8-tab strip)
- File: add_coins_hub.dart:30–39 (constructor), 340–348 (build branch), 355–368 (quick-add card)
- showCertFullScreen = false default (backward compatible)
- When true: bare Scaffold with AppBar('Add by Cert #', BackButton())
- Quick-add cert card opens via Navigator.push to full-screen mode

### NGC NICE-TO-HAVES
- File: add_coins_hub.dart:2982–3031
- ListenableBuilder on _certManualGrade (reactive)
- Label: 'Check this slab on ngccoin.com'
- minimumSize: Size(double.infinity, 48); fontSize 16
- Tap without grade → SnackBar 'Enter your grade first' (amber)
- NGC URL pattern: replaceAll(RegExp(r'[^0-9]'), '') retained from V4

## Tests
- flutter analyze lib/: 0 issues
- flutter test p7_v5_ux_fixes_test.dart: 5/5 PASS
- flutter test cert_flow_test.dart: 6/6 PASS
- flutter test --reporter compact: 505/505 PASS

## Gemini BUILD Review
Filed: BETA TEST\Grok Bot\14 OCT 26\GEMINI38_REVIEW_P7_ADD_COINS_FLOW_V5_BUILD.md
All verbatim code lines included per Rule 6b. One note on 14px chip labels (see review).

## Next
Test URL (Firebase preview channel) filed in NET-108.
Passing to Grok CoS for UX gate re-review via NET-111.
