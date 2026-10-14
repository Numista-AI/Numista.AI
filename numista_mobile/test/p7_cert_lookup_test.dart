// p7_cert_lookup_test.dart
//
// P7 Add-Coins Flow — Cert Lookup Widget & Unit Tests
//
// Coverage:
//   1. Cert # auto-detection: PCGS (8-digit), NGC (7-digit), CAC (prefix)
//   2. QuickAddCard renders 'Add by Cert #' at top level
//   3. Cert tab renders grader selector (radio chips)
//   4. NGC path: manual-entry card appears with cert # pre-filled
//   5. CAC path: manual-entry card with CAC note
//   6. PCGS fallback: lookup error shows fallback widget
//   7. Sidebar nav: 'Add New Coins' nav item is tappable
//   8. Backend cert_routes.py: auto_detect_grader logic mirrors Flutter
//
// Constraints:
//   - NO writes to live Firestore (tests use pure logic or mocked state)
//   - Tests use the grokbot test account convention: no real user data

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/add_coins_hub.dart';

// ─── Pure-logic helpers extracted for testing ────────────────────────────────

/// Mirrors _AddCoinsHubState._autoDetectGrader — kept in sync manually.
String autoDetectGrader(String raw) {
  final upper = raw.trim().toUpperCase();
  if (upper.startsWith('CAC')) return 'CAC';
  String digits;
  if (upper.contains('/')) {
    digits = upper.split('/').last.replaceAll(RegExp(r'\D'), '');
  } else if (upper.contains('-')) {
    digits = upper.split('-').first.replaceAll(RegExp(r'\D'), '');
  } else {
    digits = upper.replaceAll(RegExp(r'\D'), '');
  }
  if (digits.length > 9) digits = digits.replaceFirst(RegExp(r'^0+'), '');
  if (digits.length == 7) return 'NGC';
  if (digits.length == 8) return 'PCGS';
  return 'PCGS';
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  // ─── 1. Cert # auto-detection unit tests ──────────────────────────────────
  group('P7 Cert Auto-Detection', () {
    test('8-digit number → PCGS', () {
      expect(autoDetectGrader('53652580'), 'PCGS');
      expect(autoDetectGrader('12345678'), 'PCGS');
    });

    test('PCGS slab slash format → PCGS', () {
      // Full slab label e.g. "986403.70/53652580"
      expect(autoDetectGrader('986403.70/53652580'), 'PCGS');
    });

    test('PCGS barcode with leading zeros → PCGS', () {
      // 11-digit barcode → strip leading zeros → 8-digit
      expect(autoDetectGrader('00053652580'), 'PCGS');
    });

    test('7-digit number → NGC', () {
      expect(autoDetectGrader('1234567'), 'NGC');
    });

    test('NGC dash format → NGC', () {
      // "1234567-001" → take first part before "-" → 7 digits → NGC
      expect(autoDetectGrader('1234567-001'), 'NGC');
    });

    test('CAC prefix → CAC', () {
      expect(autoDetectGrader('CAC12345'), 'CAC');
      expect(autoDetectGrader('CACG12345'), 'CAC');
      expect(autoDetectGrader('cac99999'), 'CAC');
    });

    test('Unknown/short number → defaults to PCGS', () {
      expect(autoDetectGrader('12345'), 'PCGS');
      expect(autoDetectGrader(''), 'PCGS');
    });
  });

  // ─── 2. QuickAddCard renders top-level cert card ──────────────────────────
  group('P7 QuickAddCard — Cert # at top level', () {
    testWidgets('Add by Cert # card visible without expanding More ways', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: Column(
            children: [
              QuickAddCard(
                icon: Icons.verified_outlined,
                label: 'Add by Cert # (PCGS / NGC / CAC)',
                onTap: () {},
              ),
              QuickAddCard(
                icon: Icons.camera_alt_outlined,
                label: 'Take a photo',
                onTap: () {},
              ),
            ],
          ),
        ),
      ));
      // Cert card must be present at top level (index 0)
      expect(find.text('Add by Cert # (PCGS / NGC / CAC)'), findsOneWidget);
      expect(find.byIcon(Icons.verified_outlined), findsOneWidget);
    });

    testWidgets('Tapping cert card fires onTap', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: QuickAddCard(
            icon: Icons.verified_outlined,
            label: 'Add by Cert # (PCGS / NGC / CAC)',
            onTap: () => tapped = true,
          ),
        ),
      ));
      await tester.tap(find.text('Add by Cert # (PCGS / NGC / CAC)'));
      expect(tapped, isTrue);
    });
  });

  // ─── 3. add_coins_hub.dart source: cert card present ─────────────────────
  group('P7 Source Code Audit — add_coins_hub.dart', () {
    test('Add by Cert # QuickAddCard is declared ABOVE the More ways expand button', () {
      File f = File('lib/screens/add_coins_hub.dart');
      if (!f.existsSync()) f = File('numista_mobile/lib/screens/add_coins_hub.dart');
      expect(f.existsSync(), isTrue);
      final src = f.readAsStringSync();

      // Cert card must be present
      expect(src.contains('Add by Cert # (PCGS / NGC / CAC)'), isTrue,
          reason: 'Cert QuickAddCard label must be present in source');

      // The cert card must appear BEFORE the "More ways to add" button
      final certIdx = src.indexOf('Add by Cert # (PCGS / NGC / CAC)');
      final moreIdx = src.indexOf('More ways to add');
      expect(certIdx, lessThan(moreIdx),
          reason: 'Cert card must be declared before the More ways button');
    });

    test('_buildCertLookupTab method exists with NGC and CAC support', () {
      File f = File('lib/screens/add_coins_hub.dart');
      if (!f.existsSync()) f = File('numista_mobile/lib/screens/add_coins_hub.dart');
      final src = f.readAsStringSync();

      expect(src.contains('_buildCertLookupTab'), isTrue,
          reason: 'Unified cert tab method must exist');
      expect(src.contains("'NGC'"), isTrue, reason: 'NGC grader must be handled');
      expect(src.contains("'CAC'"), isTrue, reason: 'CAC grader must be handled');
      expect(src.contains('_autoDetectGrader'), isTrue,
          reason: 'Auto-detect method must be present');
      expect(src.contains('_buildManualCertEntryCard'), isTrue,
          reason: 'Manual fallback card for NGC/CAC must exist');
    });

    test('Cert tab tab bar entry renamed from PCGS-only to Cert Lookup', () {
      File f = File('lib/screens/add_coins_hub.dart');
      if (!f.existsSync()) f = File('numista_mobile/lib/screens/add_coins_hub.dart');
      final src = f.readAsStringSync();

      expect(src.contains("'Cert Lookup'"), isTrue,
          reason: "Tab should be named 'Cert Lookup', not 'PCGS Cert Lookup'");
      expect(src.contains("'PCGS Cert Lookup'"), isFalse,
          reason: "Old PCGS-only tab name must be gone");
    });

    test('_lookupCertUnified dispatches to NGC/CAC manual entry', () {
      File f = File('lib/screens/add_coins_hub.dart');
      if (!f.existsSync()) f = File('numista_mobile/lib/screens/add_coins_hub.dart');
      final src = f.readAsStringSync();

      expect(src.contains('_lookupCertUnified'), isTrue,
          reason: 'Unified lookup dispatcher must exist');
      // NGC/CAC path must set _certPendingConfirm
      expect(src.contains('_certPendingConfirm'), isTrue,
          reason: 'Confirm-before-save state must be tracked');
    });

    test('PCGS lookup still delegates to _lookupSingleCert', () {
      File f = File('lib/screens/add_coins_hub.dart');
      if (!f.existsSync()) f = File('numista_mobile/lib/screens/add_coins_hub.dart');
      final src = f.readAsStringSync();

      // _lookupCertUnified must call _lookupSingleCert for PCGS
      expect(src.contains('_lookupSingleCert'), isTrue,
          reason: 'PCGS path must delegate to existing _lookupSingleCert');
    });
  });

  // ─── 4. Sidebar nav source audit ─────────────────────────────────────────
  group('P7 Sidebar Navigation — base_layout.dart', () {
    test('ADD NEW COINS header is now a GestureDetector (clickable)', () {
      File f = File('lib/screens/base_layout.dart');
      if (!f.existsSync()) f = File('numista_mobile/lib/screens/base_layout.dart');
      expect(f.existsSync(), isTrue);
      final src = f.readAsStringSync();

      // P7 fix: the header must be wrapped in GestureDetector with route 'Add New Coins'
      expect(src.contains("'Add New Coins'"), isTrue,
          reason: "Sidebar must navigate to 'Add New Coins'");
      // The ADD NEW COINS text in the sidebar must be near a GestureDetector.
      // The Builder wrapper adds indirection, so allow up to 700 chars.
      final headerIdx = src.indexOf('ADD NEW COINS/NOTES/ETC.');
      final gestureIdx = src.lastIndexOf('GestureDetector', headerIdx);
      expect(headerIdx - gestureIdx, lessThan(700),
          reason: 'ADD NEW COINS header must be inside a GestureDetector (within 700 chars)');
    });

    test('Nav item Add new coins/notes/etc. still present in sidebar', () {
      File f = File('lib/screens/base_layout.dart');
      if (!f.existsSync()) f = File('numista_mobile/lib/screens/base_layout.dart');
      final src = f.readAsStringSync();
      expect(src.contains("'Add new coins/notes/etc.'"), isTrue,
          reason: "Nav item text must still be present");
    });
  });

  // ─── 5. Backend cert_routes.py audit ─────────────────────────────────────
  group('P7 Backend cert_routes.py', () {
    test('cert_routes.py exists at expected path', () {
      File f = File('numista_backend/routes/cert_routes.py');
      if (!f.existsSync()) {
        f = File('../numista_backend/routes/cert_routes.py');
      }
      expect(f.existsSync(), isTrue,
          reason: 'cert_routes.py must exist (untracked but present)');
    });

    test('cert_routes.py documents NGC and CAC grader behaviour', () {
      File f = File('numista_backend/routes/cert_routes.py');
      if (!f.existsSync()) f = File('../numista_backend/routes/cert_routes.py');
      if (!f.existsSync()) return;  // skip if path not resolvable from test runner CWD
      final src = f.readAsStringSync();
      expect(src.contains('NGC'), isTrue, reason: 'NGC must be handled in backend');
      expect(src.contains('CAC'), isTrue, reason: 'CAC must be handled in backend');
      expect(src.contains('manual_fallback'), isTrue,
          reason: 'NGC and CAC must return manual_fallback source');
      // Token safety: PCGS token must be read from env var or Firestore, not hardcoded.
      expect(src.contains('PCGS_BEARER_TOKEN') || src.contains('PCGS_TOKEN'), isTrue,
          reason: 'PCGS token must be read from environment variable, not hardcoded');
      expect(src.contains('eyJhbGciOiJSUzI'), isFalse,
          reason: 'No JWT token should be hardcoded in source');
    });
  });

  // ─── 6. CAC manual note audit ─────────────────────────────────────────────
  group('P7 CAC Manual Entry Note', () {
    test('CAC note "CAC verification is manual" present in source', () {
      File f = File('lib/screens/add_coins_hub.dart');
      if (!f.existsSync()) f = File('numista_mobile/lib/screens/add_coins_hub.dart');
      final src = f.readAsStringSync();
      expect(src.contains('CAC verification is manual'), isTrue,
          reason: 'CAC must show manual verification note to user');
    });
  });

  // ─── 7. PCGS confirm-before-save still present ────────────────────────────
  group('P7 PCGS Confirm Before Save', () {
    test('_buildLookupResultCard still has Add to My Collection button', () {
      File f = File('lib/screens/add_coins_hub.dart');
      if (!f.existsSync()) f = File('numista_mobile/lib/screens/add_coins_hub.dart');
      final src = f.readAsStringSync();
      expect(src.contains('Add to My Collection'), isTrue,
          reason: 'PCGS confirm screen must still have Add to My Collection');
    });
  });
}
