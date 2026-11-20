import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:numista_ai/constants.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/models/program_model.dart';
import 'package:numista_ai/screens/wishlist_screen.dart';
import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/services/wishlist_service.dart';
import 'package:numista_ai/utils/program_goal_helper.dart';

void main() {
  final sampleProgram = CoinProgram(
    id: '50state',
    name: '50 State Quarters',
    url: '',
    years: '1999-2008',
    category: 'Quarter',
    mintMarkLocations: 'Reverse',
    coins: [
      ProgramCoin(
        id: 'delaware',
        name: 'Delaware',
        year: '1999',
        varieties: const [
          ChecklistVariety(id: 'D-UNC', label: 'D Unc'),
        ],
      ),
    ],
  );

  List<AutoFilledProgramGroup> sampleAutoGroups() => [
        AutoFilledProgramGroup(
          program: sampleProgram,
          effectiveGoal: ProgramGoalHelper.defaultAutoFillGoal,
          ownedCount: 0,
          targetCount: 1,
          hiddenSlotCount: 0,
          missingSlots: [
            MissingProgramSlot(
              slotKey: '50state_delaware_D-UNC',
              program: sampleProgram,
              coinSlot: sampleProgram.coins.first,
              variety: const ChecklistVariety(id: 'D-UNC', label: 'D Unc'),
              mintMark: 'D',
              varietyLabel: 'D Mint (Denver)',
              ebayQuery: '1999 D 50 State Quarters Delaware Uncirculated coin',
              ebayUrl:
                  'https://www.ebay.com/sch/i.html?_nkw=1999+D+Delaware&campid=5339148752&mkrid=711-53200-19255-0',
            ),
          ],
        ),
      ];

  List<WishlistItem> sampleManualItems() => [
        WishlistItem(
          id: 'wish_1',
          type: 'individual',
          coin: CoinModel(
            id: 'c1',
            year: '1921',
            mint: 'Philadelphia',
            mintMark: 'P',
            denomination: 'Dollar',
            themeSubject: 'Morgan Silver Dollar',
          ),
          timestamp: DateTime(2026, 11, 19),
        ),
      ];

  late List<http.Request> capturedRequests;

  setUp(() {
    capturedRequests = <http.Request>[];
    HttpAuthClient.tokenProviderOverride = () async => 'test-firebase-id-token';
    HttpAuthClient.httpClientOverride = MockClient((request) async {
      capturedRequests.add(request);
      return http.Response('{"status":"sent","item_count":1}', 200);
    });
  });

  tearDown(() {
    HttpAuthClient.tokenProviderOverride = null;
    HttpAuthClient.httpClientOverride = null;
  });

  testWidgets(
      'P5: Send Wish List Email issues exact POST /api/wishlist/send-email with Bearer token and JSON body',
      (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: WishlistScreen(
          isGuestForTest: false,
          initialAutoGroupsForTest: sampleAutoGroups(),
          initialManualItemsForTest: const [],
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.enterText(
      find.widgetWithText(TextField, 'Family Member Email'),
      'family.member@example.test',
    );
    await tester.enterText(
      find.widgetWithText(TextField, 'Personal Note (Optional)'),
      'Happy Holidays!',
    );

    await tester.ensureVisible(
      find.byKey(const Key('wishlist_send_email_button')),
    );
    await tester.tap(find.byKey(const Key('wishlist_send_email_button')));
    await tester.pumpAndSettle();

    expect(capturedRequests.length, 1);
    final req = capturedRequests.single;
    expect(req.method, 'POST');
    expect(req.url.toString(), '$kApiBaseUrl/api/wishlist/send-email');
    expect(req.headers['Authorization'], 'Bearer test-firebase-id-token');
    expect(req.headers['Content-Type'], contains('application/json'));

    final body = jsonDecode(req.body) as Map<String, dynamic>;
    expect(body['recipient_email'], 'family.member@example.test');
    expect(body['personal_note'], 'Happy Holidays!');
    expect((body['items'] as List).length, 1);
  });

  testWidgets(
      'Invalid email or empty wishlist stops before issuing POST /api/wishlist/send-email',
      (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: WishlistScreen(
          isGuestForTest: false,
          initialAutoGroupsForTest: sampleAutoGroups(),
          initialManualItemsForTest: const [],
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.enterText(
      find.widgetWithText(TextField, 'Family Member Email'),
      'invalid-email',
    );
    await tester.ensureVisible(
      find.byKey(const Key('wishlist_send_email_button')),
    );
    await tester.tap(find.byKey(const Key('wishlist_send_email_button')));
    await tester.pumpAndSettle();
    expect(capturedRequests, isEmpty);

    await tester.pumpWidget(
      const MaterialApp(
        home: WishlistScreen(
          isGuestForTest: false,
          initialAutoGroupsForTest: [],
          initialManualItemsForTest: [],
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.enterText(
      find.widgetWithText(TextField, 'Family Member Email'),
      'family.member@example.test',
    );
    await tester.ensureVisible(
      find.byKey(const Key('wishlist_send_email_button')),
    );
    await tester.tap(find.byKey(const Key('wishlist_send_email_button')));
    await tester.pumpAndSettle();
    expect(capturedRequests, isEmpty);
  });

  testWidgets('test_wishlist_email_post_fires_when_save_throws',
      (tester) async {
    var saveAttempted = false;
    await tester.pumpWidget(
      MaterialApp(
        home: WishlistScreen(
          isGuestForTest: false,
          initialManualItemsForTest: sampleManualItems(),
          saveRecipientEmailForTest: (email) async {
            saveAttempted = true;
            throw Exception('firestore permission-denied');
          },
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.enterText(
      find.widgetWithText(TextField, 'Family Member Email'),
      'family.member@example.test',
    );
    await tester.ensureVisible(
      find.byKey(const Key('wishlist_send_email_button')),
    );
    await tester.tap(find.byKey(const Key('wishlist_send_email_button')));
    await tester.pumpAndSettle();

    expect(saveAttempted, isTrue);
    expect(capturedRequests.length, 1);
    final req = capturedRequests.single;
    expect(req.method, 'POST');
    expect(req.url.toString(), '$kApiBaseUrl/api/wishlist/send-email');
    expect(req.headers['Authorization'], 'Bearer test-firebase-id-token');
    expect(req.headers['Content-Type'], contains('application/json'));

    final body = jsonDecode(req.body) as Map<String, dynamic>;
    expect(body['recipient_email'], 'family.member@example.test');
    expect((body['items'] as List).isNotEmpty, isTrue);
  });

  testWidgets('test_save_email_button', (tester) async {
    final savedEmails = <String>[];
    await tester.pumpWidget(
      MaterialApp(
        home: WishlistScreen(
          isGuestForTest: false,
          initialManualItemsForTest: sampleManualItems(),
          saveRecipientEmailForTest: (email) async {
            savedEmails.add(email);
          },
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Valid input saves without sending email.
    await tester.enterText(
      find.widgetWithText(TextField, 'Family Member Email'),
      'family.member@example.test',
    );
    await tester.ensureVisible(
      find.byKey(const Key('wishlist_save_email_button')),
    );
    await tester.tap(find.byKey(const Key('wishlist_save_email_button')));
    await tester.pumpAndSettle();

    expect(savedEmails, ['family.member@example.test']);
    expect(
      find.text('Saved family.member@example.test to Family Emails.'),
      findsOneWidget,
    );
    expect(capturedRequests, isEmpty);

    // Invalid input neither saves nor sends.
    savedEmails.clear();
    await tester.enterText(
      find.widgetWithText(TextField, 'Family Member Email'),
      'not-an-email',
    );
    await tester.ensureVisible(
      find.byKey(const Key('wishlist_save_email_button')),
    );
    await tester.tap(find.byKey(const Key('wishlist_save_email_button')));
    await tester.pumpAndSettle();

    expect(savedEmails, isEmpty);
    expect(capturedRequests, isEmpty);
  });
}
