# COS SCORE - P7 ADD-COINS-FLOW V5
Scorer: Grok CoS | 2026-10-14 ~18:00 ET | Reviewed: caa3c93f on dev (vs V4 65711b71) + GEMINI38_REVIEW_P7_ADD_COINS_FLOW_V5_BUILD.md
Verdict: **FAIL V5 (close) - ITERATE to V6.** UX gate not re-run (no rendered build; V5 has a data-integrity bug, so no preview deploy of V5).

Tests re-run by Grok CoS: `flutter test test/p7_v5_ux_fixes_test.dart test/cert_flow_test.dart` -> **11/11 passed**.

| # | Item | Score | Evidence |
|---|------|-------|----------|
| B1 | Add another copy | **FAIL** | Button is 48px and labeled (good), but it opens the NGC manual cert card for every slot, including raw coins. See quote A. Saving writes grader NGC with an empty cert # and an NGC verify link. That is fake grading data on a raw coin. `mint` preset is passed but never used. Label text 13px. |
| B2 | Slab photo button + camera + inline result | **PASS** | 56px labeled button, camera first, gallery second, persistent result card (add_coins_hub.dart:2517-2572, 2765-2788). Result card text 14px -> raise (see B3). |
| B3 | 18px dark text, numeric keypad, plain words | **FAIL (partial)** | Keypad and cert field 18px PASS. Still small/grey or jargon on the same full-screen cert view: quote B. |
| B4 | Full-screen cert, no TabBar | **PASS** | `if (widget.showCertFullScreen) return Scaffold(appBar: ... 'Add by Cert #' ...)` (add_coins_hub.dart:340-348). |
| NGC nice-to-haves | ngccoin.com label, 48px/16px, grade gate | **PASS** | add_coins_hub.dart:2985-3031. CAC/PCGS labels still say "Verify Cert on CAC.com" (CAC's site is cacgrading.com). |

## Quote A - preset forces NGC (add_coins_hub.dart:150-154)
```dart
      final grader = preset['grader']?.toString() ?? 'NGC';
      _certPendingConfirm = {
        '_grader': grader,
        'certNo': preset['certNo']?.toString() ?? '',
      };
```
And the save (add_coins_hub.dart:3141-3145, 3157-3164) has no empty-cert guard:
```dart
        case 'NGC':
          final numericGrade = grade.replaceAll(RegExp(r'[^0-9]'), '');
          final gradeSegment = numericGrade.isNotEmpty ? numericGrade : grade;
          verifyLink = 'https://www.ngccoin.com/certlookup/$certNo/$gradeSegment/';
...
        'certNo':            certNo,
        'grader':            grader,
...
        'source':            'cert_manual_${grader.toLowerCase()}',
```
Program_manager_screen.dart:1330-1334 sends name/year/mint only, so a 2nd raw Washington dollar becomes "NGC, cert blank".

## Quote B - small text / jargon still on the full-screen cert view
```dart
2407:  Text('Auto-detects grader from cert number format. Always confirms before saving.',
2408:      style: TextStyle(color: Color(0xFF64748B), fontSize: 13)),
2436:  fontSize: 14,   // grader chips
2555:  style: TextStyle(fontSize: 14, color: Color(0xFF047857))),   // "Detected Cert #" result
2567:  child: const Text('Yes, look it up', style: TextStyle(fontSize: 14, ...
2958:  style: const TextStyle(fontSize: 14, color: Color(0xFF1E3A8A), height: 1.4),
2676:  title: const Text('Advanced Options (PCGS Token & Bulk Import)',
2677:      style: TextStyle(fontSize: 13, ... color: Color(0xFF64748B))),
2709:  labelText: 'PCGS Bearer Token',
3068:  style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
```

## V6 fix list (P7 only, Rule 8)
1. **B1 (data integrity, top):** "+ Add another copy" opens a plain confirm card for that slot's coin (name, year, mint shown, no grader, no cert #), saved through the normal single writer. "Has a slab? Enter cert #" is a secondary choice that goes to the cert screen. Only set `_grader` when the user picks a grader or enters a cert. `_saveManualCertEntry` must refuse an empty cert # (no record with a grader and no cert, no blank verify link). Show the mint. Label text 16px+ and check it wraps cleanly at 390px.
2. **B3:** every word on the full-screen cert view 18px+ (chips 16px+ is OK) and dark (#334155 or darker). Drop "Auto-detects grader..." (say "Type the number on the slab label" or similar). Move "Advanced Options / PCGS Bearer Token / API" off this screen (settings or a hidden admin area). Result card text and "Yes, look it up" 18px.
3. Verify-button labels: "Check this slab on cacgrading.com" and "Check this slab on pcgs.com".
4. Tests: widget test that add-another on a raw slot shows no NGC badge and no cert field is required; unit/widget test that save refuses an empty cert # for the cert path. Full flutter test + analyze stay green.
5. Gemini38 BUILD review with the new code quoted, then NET to Grok CoS.

## Test URL (NET-108)
Don't ask Eric to run commands (Baton Rule 6). No preview of V5 is needed. When V6 passes code score, Grok CoS will get the Firebase re-login done with Eric and deploy the preview itself. Before that, AG: state in the V6 NET which backend and Firestore the preview build talks to (NET-108 uses `FLUTTER_ENV=prod`). Test adds must be grokbot-only and must not touch live user data.

## Next
Baton -> AGCOS OVER for V6. No deploy, no Eric YES until code PASS + UX gate (rendered) + Field Tester.
