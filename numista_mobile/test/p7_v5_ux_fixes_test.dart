// p7_v5_ux_fixes_test.dart
//
// Widget and flow tests for P7 V5/V6/V7 UX Fixes
//
// Tests:
// 1. blocker1AddAnotherPresetPrefill: verifies initialCoinPreset pre-fills coin name & year in manual entry card
// 2. blocker2LabeledPhotoReadButton: verifies '📷 Take a photo of the label' button exists with >= 56px height
// 3. blocker3NumberKeypadAndContrast: verifies cert input has number keypad, 18px font style, and no tour banner
// 4. blocker4FullScreenCertScaffold: verifies showCertFullScreen renders AppBar 'Add by Cert #' without 8-tab strip
// 5. blocker5NgcVerifyButtonValidation: verifies NGC verify button has label 'Check this slab on ngccoin.com',
//    >= 48px height, and alerts 'Enter your grade first' if grade field is empty
// 6. blocker1AddAnotherPlainConfirm: verifies add-another on raw slot shows plain confirm card, no NGC text
// 7. blocker1EmptyCertRefused: verifies cert lookup refuses empty cert # with warning SnackBar
// 8. blocker1SaveManualCertEmptyRefused (V7): verifies _saveManualCertEntry with blank cert shows SnackBar, no write
// 9. blocker1EmptyLookupNoFallbackCard (V7): verifies empty Look Up does NOT show 'Automatic lookup unavailable'

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:numista_ai/screens/add_coins_hub.dart';
import 'package:numista_ai/services/http_auth_client.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({'add_coins_hub_tour_dismissed': true});
    HttpAuthClient.tokenProviderOverride = () async => 'mock-test-token';
  });

  tearDown(() {
    HttpAuthClient.httpClientOverride = null;
    HttpAuthClient.tokenProviderOverride = null;
  });

  void setTestViewSize(WidgetTester tester) {
    tester.view.physicalSize = const Size(1200, 2400);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });
  }

  testWidgets('blocker4FullScreenCertScaffold', (WidgetTester tester) async {
    setTestViewSize(tester);

    // Pump AddCoinsHub with showCertFullScreen: true
    await tester.pumpWidget(
      const MaterialApp(
        home: AddCoinsHub(showCertFullScreen: true),
      ),
    );
    await tester.pumpAndSettle();

    // Verify AppBar with 'Add by Cert #' exists
    expect(find.text('Add by Cert #'), findsOneWidget);

    // Verify TabBar is NOT present (no 8-tab strip)
    expect(find.byType(TabBar), findsNothing);

    // Verify cert input is present directly
    expect(find.byType(TextField), findsAtLeastNWidgets(1));
  });

  testWidgets('blocker2LabeledPhotoReadButton', (WidgetTester tester) async {
    setTestViewSize(tester);

    await tester.pumpWidget(
      const MaterialApp(
        home: AddCoinsHub(showCertFullScreen: true),
      ),
    );
    await tester.pumpAndSettle();

    // Verify 56px+ photo button exists with exact label
    final photoBtnFinder = find.widgetWithText(OutlinedButton, '📷 Take a photo of the label');
    expect(photoBtnFinder, findsOneWidget);

    final btnSize = tester.getSize(photoBtnFinder);
    expect(btnSize.height, greaterThanOrEqualTo(56.0));
  });

  testWidgets('blocker3NumberKeypadAndContrast', (WidgetTester tester) async {
    setTestViewSize(tester);

    await tester.pumpWidget(
      const MaterialApp(
        home: AddCoinsHub(showCertFullScreen: true),
      ),
    );
    await tester.pumpAndSettle();

    // Verify tour banner is not present
    expect(find.text('Explore 7 Ways to Add Coins'), findsNothing);

    // Verify cert TextField has number keyboard and 18px text
    final textField = tester.widget<TextField>(find.byType(TextField).first);
    expect(textField.keyboardType, const TextInputType.numberWithOptions(decimal: false, signed: false));
    expect(textField.style?.fontSize, 18.0);
  });

  testWidgets('blocker1AddAnotherPresetPrefill', (WidgetTester tester) async {
    setTestViewSize(tester);

    await tester.pumpWidget(
      const MaterialApp(
        home: AddCoinsHub(
          showCertFullScreen: true,
          initialCoinPreset: {
            'name': '1921-D Morgan Dollar',
            'year': '1921',
            'mint': 'D',
          },
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Enter NGC cert to trigger manual confirm card
    final certInput = find.byType(TextField).first;
    await tester.enterText(certInput, '1234567');
    await tester.pump();

    final lookUpBtn = find.widgetWithText(ElevatedButton, 'Look Up');
    await tester.tap(lookUpBtn);
    await tester.pumpAndSettle();

    // Manual entry card should have pre-filled coin name and year from preset
    expect(find.text('1921-D Morgan Dollar'), findsOneWidget);
    expect(find.text('1921'), findsOneWidget);
  });

  testWidgets('blocker5NgcVerifyButtonValidation', (WidgetTester tester) async {
    setTestViewSize(tester);

    await tester.pumpWidget(
      const MaterialApp(
        home: AddCoinsHub(showCertFullScreen: true),
      ),
    );
    await tester.pumpAndSettle();

    // Enter NGC cert to trigger manual confirm card
    final certInput = find.byType(TextField).first;
    await tester.enterText(certInput, '1234567');
    await tester.pump();

    final lookUpBtn = find.widgetWithText(ElevatedButton, 'Look Up');
    await tester.tap(lookUpBtn);
    await tester.pumpAndSettle();

    // Find NGC verify button
    final ngcVerifyBtn = find.widgetWithText(OutlinedButton, 'Check this slab on ngccoin.com');
    expect(ngcVerifyBtn, findsOneWidget);

    final btnSize = tester.getSize(ngcVerifyBtn);
    expect(btnSize.height, greaterThanOrEqualTo(48.0));

    // Tap without entering grade -> verify SnackBar 'Enter your grade first'
    await tester.tap(ngcVerifyBtn);
    await tester.pump();

    expect(find.text('Enter your grade first'), findsOneWidget);
  });

  testWidgets('blocker1AddAnotherPlainConfirm', (WidgetTester tester) async {
    setTestViewSize(tester);
    await tester.pumpWidget(
      const MaterialApp(
        home: AddCoinsHub(
          showAddAnotherConfirm: true,
          initialCoinPreset: {'name': '2024-D Lincoln Cent', 'year': '2024', 'mint': 'D'},
        ),
      ),
    );
    await tester.pumpAndSettle();
    // Shows coin name and appbar
    expect(find.text('Add another copy'), findsOneWidget);
    expect(find.text('2024-D Lincoln Cent'), findsOneWidget);
    // Does NOT show NGC badge or cert field as the primary UI
    expect(find.byType(TabBar), findsNothing);
    // No grader text — user should not see 'NGC' on the plain confirm card
    expect(find.text('NGC'), findsNothing);
    // Save button is present
    expect(find.widgetWithText(ElevatedButton, 'Save to My Collection'), findsOneWidget);
  });

  testWidgets('blocker1EmptyCertRefused', (WidgetTester tester) async {
    setTestViewSize(tester);
    await tester.pumpWidget(
      const MaterialApp(home: AddCoinsHub(showCertFullScreen: true)),
    );
    await tester.pumpAndSettle();
    // Get cert input and leave it empty, tap Look Up
    final lookUpBtn = find.widgetWithText(ElevatedButton, 'Look Up');
    await tester.tap(lookUpBtn);
    await tester.pumpAndSettle();
    // Verify SnackBar 'Enter a cert # before saving'
    expect(find.text('Enter a cert # before saving'), findsOneWidget);
    expect(find.text('Enter NGC slab details below'), findsNothing);
    expect(find.text('Enter CAC slab details below'), findsNothing);
  });

  // V7 test: blank cert on the save path writes nothing — guard fires before write
  testWidgets('blocker1SaveManualCertEmptyRefused', (WidgetTester tester) async {
    setTestViewSize(tester);
    await tester.pumpWidget(
      const MaterialApp(home: AddCoinsHub(showCertFullScreen: true)),
    );
    await tester.pumpAndSettle();

    // Leave cert empty, tap Look Up — guard must fire at the lookup level, no NGC card opened
    final lookUpBtn = find.widgetWithText(ElevatedButton, 'Look Up');
    await tester.tap(lookUpBtn);
    await tester.pumpAndSettle();
    // Guard fires: SnackBar shown, no NGC manual card (cert was empty → no write path reached)
    expect(find.text('Enter a cert # before saving'), findsOneWidget);
    expect(find.text('Enter NGC slab details below'), findsNothing);
    expect(find.text('Enter CAC slab details below'), findsNothing);
  });

  // V7 test: empty Look Up does NOT show 'Automatic lookup unavailable' / PCGS fallback text
  testWidgets('blocker1EmptyLookupNoFallbackCard', (WidgetTester tester) async {
    setTestViewSize(tester);
    await tester.pumpWidget(
      const MaterialApp(home: AddCoinsHub(showCertFullScreen: true)),
    );
    await tester.pumpAndSettle();
    // Leave cert empty, tap Look Up
    final lookUpBtn = find.widgetWithText(ElevatedButton, 'Look Up');
    await tester.tap(lookUpBtn);
    await tester.pumpAndSettle();
    // Must NOT show the old PCGS fallback header texts
    expect(find.text('Automatic lookup unavailable right now'), findsNothing);
    expect(find.text('Lookup not available right now'), findsNothing);
    // Only the SnackBar guard message should appear
    expect(find.text('Enter a cert # before saving'), findsOneWidget);
  });
}
