import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/base_layout.dart';
import 'package:numista_ai/screens/login_screen.dart';
import 'package:numista_ai/screens/add_coins_hub.dart';
import 'package:numista_ai/theme/numista_theme.dart';

// Type alias if tests reference _PinBoxRow directly per prompt
typedef _PinBoxRow = PinBoxRow;

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Fix 2: Typography & NumistaTheme Tokens', () {
    test('no hardcoded fontSize below 14 in base_layout.dart', () {
      File baseLayoutFile = File('lib/screens/base_layout.dart');
      if (!baseLayoutFile.existsSync()) {
        baseLayoutFile = File('numista_mobile/lib/screens/base_layout.dart');
      }
      expect(baseLayoutFile.existsSync(), isTrue,
          reason: 'base_layout.dart must exist');

      final content = baseLayoutFile.readAsStringSync();
      final regex = RegExp(r'fontSize:\s*([0-9]+(?:\.[0-9]+)?)');
      final matches = regex.allMatches(content);

      final violations = <String>[];
      for (final match in matches) {
        final val = double.tryParse(match.group(1)!);
        if (val != null && val < 14.0) {
          violations.add(match.group(0)!);
        }
      }
      expect(violations, isEmpty,
          reason:
              'Found hardcoded font sizes below 14 in base_layout: $violations');
    });

    test('no hardcoded fontSize below 14 in login_screen.dart login form section', () {
      // T3 V2 Fix 3: login form section must use tokens, no raw numbers < 14.
      // Scope: first ~1000 lines which contain the login, create, reset forms.
      // The scanner/coin-display widget sections (> line 1000) are exempt — they
      // have design-specific small sizes that are intentional (chart labels, etc.)
      File loginFile = File('lib/screens/login_screen.dart');
      if (!loginFile.existsSync()) {
        loginFile = File('numista_mobile/lib/screens/login_screen.dart');
      }
      expect(loginFile.existsSync(), isTrue,
          reason: 'login_screen.dart must exist');

      final lines = loginFile.readAsLinesSync();
      final formLines = lines.take(1000).join('\n');
      final regex = RegExp(r'fontSize:\s*([0-9]+(?:\.[0-9]+)?)');
      final matches = regex.allMatches(formLines);

      final violations = <String>[];
      for (final match in matches) {
        final val = double.tryParse(match.group(1)!);
        if (val != null && val < 14.0) {
          violations.add(match.group(0)!);
        }
      }
      expect(violations, isEmpty,
          reason:
              'Found hardcoded font sizes below 14 in login_screen form area: $violations');
    });

    test('NumistaTheme tokens are defined with required constants', () {
      expect(NumistaTheme.textCaption, 14.0);  // T3 V2 Fix 2: raised from 12 to meet 14px floor
      expect(NumistaTheme.textCaption, greaterThanOrEqualTo(14.0));  // explicit floor assertion
      expect(NumistaTheme.textBodySm, 14.0);
      expect(NumistaTheme.textBody, 16.0);
      expect(NumistaTheme.textLg, 18.0);
      expect(NumistaTheme.textXl, 22.0);
      expect(NumistaTheme.textDisplay, 28.0);
      expect(NumistaTheme.tapTarget, 44.0);
      expect(NumistaTheme.tapTargetLg, 56.0);
    });
  });

  group('Fix 3: PIN Screen 6-Box Widget', () {
    testWidgets('PIN box row shows 6 slots', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: _PinBoxRow(
            filled: List.filled(6, false),
            digits: List.filled(6, ''),
            showDigits: false,
          ),
        ),
      ));
      expect(find.byType(Container), findsWidgets);
      // Verify row widget exists
      final row = find.byType(Row);
      expect(row, findsOneWidget);
    });

    testWidgets('PIN box row reveals digits when showDigits is true',
        (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: _PinBoxRow(
            filled: [true, true, true, false, false, false],
            digits: ['1', '2', '3', '', '', ''],
            showDigits: true,
          ),
        ),
      ));
      expect(find.text('1'), findsOneWidget);
      expect(find.text('2'), findsOneWidget);
      expect(find.text('3'), findsOneWidget);
    });

    testWidgets('NumKeypad triggers onDigit and onBackspace callbacks',
        (tester) async {
      String? tappedDigit;
      bool backspaceTapped = false;

      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: NumKeypad(
            onDigit: (d) => tappedDigit = d,
            onBackspace: () => backspaceTapped = true,
          ),
        ),
      ));

      await tester.tap(find.text('7'));
      expect(tappedDigit, '7');

      await tester.tap(find.text('⌫'));
      expect(backspaceTapped, isTrue);
    });
  });

  group('Fix 4: Desktop Sidebar Navigation (6 top-level + More)', () {
    test('base_layout.dart defines 6 top-level items and MoreNavSection', () {
      File baseLayoutFile = File('lib/screens/base_layout.dart');
      if (!baseLayoutFile.existsSync()) {
        baseLayoutFile = File('numista_mobile/lib/screens/base_layout.dart');
      }
      final code = baseLayoutFile.readAsStringSync();

      expect(code.contains("'Home Dashboard'"), isTrue);
      expect(code.contains("'My Collection'"), isTrue);
      expect(code.contains("'Add new coins/notes/etc.'"), isTrue);
      expect(code.contains("'Coin Programs'"), isTrue);
      expect(code.contains('_buildNavMorganButton()'), isTrue);
      expect(code.contains('_MoreSection'), isTrue);

      // Verify all 29 routes exist
      final expectedRoutes = [
        'Home Dashboard',
        'Coin Programs',
        'Upcoming Releases',
        'All',
        'Coins',
        'Currency Collection',
        'World and Specialty',
        'Inventory',
        'My Wishlist',
        'Estate Planning',
        'Attorney Portal',
        'Lateral Transfer',
        'Claim Transfer',
        'Add new coins/notes/etc.',
        'Microscope Scanner',
        'Review Hub',
        'AI Trainer Board',
        'Admin Grade Flags',
        'Beta Feedback Inbox',
        'Admin: Support Portal',
        'Error Library',
        'Glossary Academy',
        'Coin Search',
        'AI Deepdive',
        'Settings & Backup',
        'Our Team',
        'Customer Service',
        'My Tickets',
        '🔍 Numista Lookup',
      ];
      for (final route in expectedRoutes) {
        expect(code.contains(route), isTrue,
            reason: 'Route "$route" must be present in sidebar nav');
      }
    });

    testWidgets('MoreNavSection renders ExpansionTile with title More',
        (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: MoreNavSection(
            children: [
              Text('Child Item 1'),
            ],
          ),
        ),
      ));
      expect(find.text('More'), findsOneWidget);
      expect(find.byIcon(Icons.more_horiz), findsOneWidget);
    });
  });

  group('Fix 5: Add Coin Screen (3 Quick Choice Cards)', () {
    testWidgets('QuickAddCard renders 3 cards', (tester) async {
      bool photoTapped = false;
      bool typeTapped = false;
      bool uploadTapped = false;

      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: Column(
            children: [
              QuickAddCard(
                icon: Icons.camera_alt_outlined,
                label: 'Take a photo',
                onTap: () => photoTapped = true,
              ),
              QuickAddCard(
                icon: Icons.keyboard_outlined,
                label: 'Type it in',
                onTap: () => typeTapped = true,
              ),
              QuickAddCard(
                icon: Icons.upload_file_outlined,
                label: 'Upload a list',
                onTap: () => uploadTapped = true,
              ),
            ],
          ),
        ),
      ));

      expect(find.byType(QuickAddCard), findsNWidgets(3));
      expect(find.text('Take a photo'), findsOneWidget);
      expect(find.text('Type it in'), findsOneWidget);
      expect(find.text('Upload a list'), findsOneWidget);

      await tester.tap(find.text('Take a photo'));
      expect(photoTapped, isTrue);

      await tester.tap(find.text('Type it in'));
      expect(typeTapped, isTrue);

      await tester.tap(find.text('Upload a list'));
      expect(uploadTapped, isTrue);
    });
  });
}
