# GEMINI38_REVIEW — P7 ADD-COINS-FLOW V7 BUILD
Reviewer: Antigravity / Gemini 3.8
Commit: ec34ab69 (dev)
Date: 2026-10-14 ~19:44 ET
Diff base: ae2b87bd (V6)

## Fix 1 — Empty-cert guard in `_saveManualCertEntry`

**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:3278-3286`

**Verbatim code added:**
```dart
    // Empty-cert guard — must not write a coin with no cert number
    if (certNo.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Enter a cert # before saving'),
        backgroundColor: Color(0xFFD97706),
      ));
      return; // _certManualSaving was never set true — no reset needed
    }
    setState(() => _certManualSaving = true);
```

**Verdict:** PASS. Guard fires before `setState(() => _certManualSaving = true)` — no saving flag left dangling. No Firestore write can be reached with empty certNo.

---

## Fix 1b — Refuse empty `certClean` (slash-only input like "123/")

**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:3024-3031`

**Verbatim code added:**
```dart
    // Refuse slash-only input like "123/" that yields an empty cert number
    if (certClean.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Enter a cert # before saving'),
        backgroundColor: Color(0xFFD97706),
      ));
      return;
    }
```

**Verdict:** PASS. Placed after `final certClean = raw.contains('/') ? raw.split('/').last.trim() : raw;` (line 3016). A string like `"123/"` → `certClean = ""` → SnackBar fires, no NGC manual card opens.

---

## Fix 2 — Empty-cert guard no longer sets `_pcgsLookupError`

**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:2998`

**Verbatim code removed:**
```dart
      setState(() => _pcgsLookupError = 'Please enter a cert number.');
```

**Verbatim code in place:**
```dart
      // Do NOT set _pcgsLookupError — that triggers the wrong PCGS fallback card.
      return;
```

**Verdict:** PASS. The `_buildCertLookupFallback` card (which showed "Automatic lookup unavailable / PCGS blocks automated lookups / Upload PCGS CSV below") is no longer triggered by an empty cert # input. Only the SnackBar fires.

---

## Fix 3a — `_buildCertLookupFallback` — 18px+ dark text, no CSV tip

**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:3719-3723` (header)

**Verbatim code (before → after):**
```dart
// BEFORE:
'Automatic lookup unavailable right now',
style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF92400E)),
// AFTER:
'Lookup not available right now',
style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFF92400E)),
```

**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:3728-3731` (body)

**Verbatim code (before → after):**
```dart
// BEFORE:
'PCGS blocks automated lookups from our servers. '
'You can verify the cert directly on PCGS.com instead:',
style: TextStyle(fontSize: 12, color: Color(0xFF78350F), height: 1.4),
// AFTER:
'You can check the cert directly on PCGS.com instead:',
style: TextStyle(fontSize: 18, color: Color(0xFF78350F), height: 1.4),
```

**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:3752` (button)

**Verbatim code (before → after):**
```dart
// BEFORE:
textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
// AFTER:
textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
```

CSV tip block (`SizedBox(height: 10)` + Container with lightbulb icon + "Tip: Use 'Upload PCGS CSV' below...") — **deleted entirely.**

**Verdict:** PASS. All text on the PCGS fallback card is now 18px (header, body) / 16px (button). No CSV tip. Plain language ("Lookup not available right now" / "You can check the cert directly on PCGS.com instead:").

---

## Fix 3b — Grader badge font 14px → 16px

**File:line:** `numista_mobile/lib/screens/add_coins_hub.dart:3065`

**Verbatim code (before → after):**
```dart
// BEFORE:
style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
// AFTER:
style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
```

**Verdict:** PASS. Grader badge (NGC/CAC/PCGS pill on manual entry card) now 16px.

---

## Fix 4 — Tests

**File:line:** `numista_mobile/test/p7_v5_ux_fixes_test.dart:176-178`

**Verbatim code added to `blocker1AddAnotherPlainConfirm`:**
```dart
    // No grader text — user should not see 'NGC' on the plain confirm card
    expect(find.text('NGC'), findsNothing);
```

**File:line:** `numista_mobile/test/p7_v5_ux_fixes_test.dart:215-228` (`blocker1SaveManualCertEmptyRefused`)

**Verbatim test added:**
```dart
    // Leave cert empty, tap Look Up — guard must fire at the lookup level, no NGC card opened
    final lookUpBtn = find.widgetWithText(ElevatedButton, 'Look Up');
    await tester.tap(lookUpBtn);
    await tester.pumpAndSettle();
    // Guard fires: SnackBar shown, no NGC manual card (cert was empty → no write path reached)
    expect(find.text('Enter a cert # before saving'), findsOneWidget);
    expect(find.text('Enter NGC slab details below'), findsNothing);
    expect(find.text('Enter CAC slab details below'), findsNothing);
```

**File:line:** `numista_mobile/test/p7_v5_ux_fixes_test.dart:231-244` (`blocker1EmptyLookupNoFallbackCard`)

**Verbatim test added:**
```dart
    // Must NOT show the old PCGS fallback header texts
    expect(find.text('Automatic lookup unavailable right now'), findsNothing);
    expect(find.text('Lookup not available right now'), findsNothing);
    // Only the SnackBar guard message should appear
    expect(find.text('Enter a cert # before saving'), findsOneWidget);
```

**Verdict:** PASS. 9/9 P7 tests pass. Full suite 509/509 pass. flutter analyze: 0 issues.

---

## Summary

| Fix | File:Line | Verdict |
|-----|-----------|---------|
| Empty-cert guard in `_saveManualCertEntry` | add_coins_hub.dart:3278-3285 | PASS |
| Refuse empty certClean (slash input) | add_coins_hub.dart:3024-3031 | PASS |
| Remove `_pcgsLookupError` from empty-cert path | add_coins_hub.dart:2998 | PASS |
| Fallback header 18px dark, plain text | add_coins_hub.dart:3719-3723 | PASS |
| Fallback body 18px, drop PCGS jargon + CSV tip | add_coins_hub.dart:3728-3732 | PASS |
| Fallback button 16px | add_coins_hub.dart:3752 | PASS |
| Grader badge 16px | add_coins_hub.dart:3065 | PASS |
| `find.text('NGC') findsNothing` in add-another | p7_v5_ux_fixes_test.dart:176-178 | PASS |
| `blocker1SaveManualCertEmptyRefused` | p7_v5_ux_fixes_test.dart:215-228 | PASS |
| `blocker1EmptyLookupNoFallbackCard` | p7_v5_ux_fixes_test.dart:231-244 | PASS |

flutter test: **509/509 pass** (was 507 in V6, +2 new tests).
flutter analyze: **No issues found** (ran in 131.5s).
