// cert_flow_test.dart
//
// P7 Add-Coins Flow Widget & Flow Tests
//
// Test cases:
// 1. certFlowPcgsAutoDetect — pump AddCoinsHub, tap cert tab, enter 8-digit cert, assert grader label shows 'PCGS'
// 2. certFlowNgcAutoDetect — enter 7-digit cert, assert grader label shows 'NGC'
// 3. certFlowCacPrefix — enter 'CAC12345', assert grader label shows 'CAC'
// 4. certFlowManualGraderSelect — tap grader selector, pick 'PCGS', enter cert -> assert grader='PCGS'
// 5. certFlowDupConfirmDialog — mock backend returns 409, assert dialog appears with "Add another copy anyway?"
// 6. certFlowNavFromTopLevel — from main AddCoinsHub build, tap "Add by Cert # (PCGS / NGC / CAC)" card -> assert cert tab becomes visible
//
// Constraints:
// - Dev only. No live Firestore writes.

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
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

  Widget createTestWidget({String? initialTabName}) {
    return MaterialApp(
      home: Scaffold(
        body: AddCoinsHub(initialTabName: initialTabName),
      ),
    );
  }

  void setTestViewSize(WidgetTester tester) {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });
  }

  testWidgets('certFlowPcgsAutoDetect', (WidgetTester tester) async {
    setTestViewSize(tester);
    await tester.pumpWidget(createTestWidget(initialTabName: 'cert'));
    await tester.pump();

    // Find the cert input field
    final certInput = find.byType(TextField).first;
    await tester.enterText(certInput, '53652580');
    await tester.pump();

    // Verify label shows 'PCGS Certification Number'
    expect(find.text('PCGS Certification Number'), findsOneWidget);
  });

  testWidgets('certFlowNgcAutoDetect', (WidgetTester tester) async {
    setTestViewSize(tester);
    await tester.pumpWidget(createTestWidget(initialTabName: 'cert'));
    await tester.pump();

    final certInput = find.byType(TextField).first;
    await tester.enterText(certInput, '1234567');
    await tester.pump();

    // Verify label shows 'NGC Certification Number'
    expect(find.text('NGC Certification Number'), findsOneWidget);
  });

  testWidgets('certFlowCacPrefix', (WidgetTester tester) async {
    setTestViewSize(tester);
    await tester.pumpWidget(createTestWidget(initialTabName: 'cert'));
    await tester.pump();

    final certInput = find.byType(TextField).first;
    await tester.enterText(certInput, 'CAC12345');
    await tester.pump();

    // Verify label shows 'CAC Certification Number'
    expect(find.text('CAC Certification Number'), findsOneWidget);
  });

  testWidgets('certFlowManualGraderSelect', (WidgetTester tester) async {
    setTestViewSize(tester);
    await tester.pumpWidget(createTestWidget(initialTabName: 'cert'));
    await tester.pump();

    // Tap PCGS filter chip
    final pcgsChip = find.widgetWithText(FilterChip, 'PCGS');
    expect(pcgsChip, findsOneWidget);
    await tester.tap(pcgsChip);
    await tester.pump();

    // Enter a 7-digit number that would otherwise auto-detect to NGC
    final certInput = find.byType(TextField).first;
    await tester.enterText(certInput, '1234567');
    await tester.pump();

    // Because manual grader 'PCGS' is selected, label remains 'PCGS Certification Number'
    expect(find.text('PCGS Certification Number'), findsOneWidget);
  });

  testWidgets('certFlowDupConfirmDialog', (WidgetTester tester) async {
    setTestViewSize(tester);

    // Mock backend returning 409 on cert_save
    HttpAuthClient.httpClientOverride = MockClient((request) async {
      if (request.url.path.contains('cert_save')) {
        return http.Response(
          jsonEncode({
            'error': 'cert_duplicate',
            'detail': {
              'error': 'cert_duplicate',
              'message': 'This cert # is already in your collection.',
              'existing_coin_id': 'coin_dup_123',
            }
          }),
          409,
          headers: {'content-type': 'application/json'},
        );
      }
      return http.Response('Not Found', 404);
    });

    await tester.pumpWidget(createTestWidget(initialTabName: 'cert'));
    await tester.pump();

    // Enter NGC cert number
    final certInput = find.byType(TextField).first;
    await tester.enterText(certInput, '1234567');
    await tester.pump();

    // Tap 'Look Up' button
    final lookUpBtn = find.widgetWithText(ElevatedButton, 'Look Up');
    expect(lookUpBtn, findsOneWidget);
    await tester.tap(lookUpBtn);
    await tester.pump();

    // Manual entry card appears with Confirm & Add button
    final confirmSaveBtn = find.text('Confirm & Add to My Collection');
    expect(confirmSaveBtn, findsOneWidget);
    await tester.ensureVisible(confirmSaveBtn);
    await tester.tap(confirmSaveBtn);
    await tester.pumpAndSettle();

    // Assert dialog appears with "Add another copy anyway?"
    expect(find.text('This cert # is already in your collection. Add another copy anyway?'), findsOneWidget);
    expect(find.text('Add anyway'), findsOneWidget);
    expect(find.text('Cancel'), findsOneWidget);
  });

  testWidgets('certFlowNavFromTopLevel', (WidgetTester tester) async {
    setTestViewSize(tester);

    // Pump default AddCoinsHub (top-level view, _showMoreWays == false)
    await tester.pumpWidget(createTestWidget(initialTabName: null));
    await tester.pump();

    // Verify top-level card is present
    final certCard = find.text('Add by Cert # (PCGS / NGC / CAC)');
    expect(certCard, findsOneWidget);

    // Tap card to navigate to cert tab
    await tester.tap(certCard);
    await tester.pumpAndSettle();

    // Cert tab should now be visible and active
    expect(find.text('Add by Cert # — PCGS / NGC / CAC'), findsOneWidget);
    expect(find.widgetWithText(FilterChip, 'PCGS'), findsOneWidget);
    expect(find.widgetWithText(FilterChip, 'NGC'), findsOneWidget);
    expect(find.widgetWithText(FilterChip, 'CAC'), findsOneWidget);
  });
}
