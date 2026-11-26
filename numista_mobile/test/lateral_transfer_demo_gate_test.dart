import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/lateral_transfer_screen.dart';
import 'package:numista_ai/services/guest_seed_service.dart';
import 'package:numista_ai/utils/sell_transfer_access.dart';

class _CountingHttpOverrides extends HttpOverrides {
  int clients = 0;
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    clients++;
    return super.createHttpClient(context);
  }
}

void main() {
  tearDown(() {
    GuestSeedService.setDemoActiveForTest(false);
    HttpOverrides.global = null;
  });

  testWidgets('N1: Browse Demo sees only the sign-up message and makes no Firestore or HTTP call', (tester) async {
    final http = _CountingHttpOverrides();
    HttpOverrides.global = http;
    GuestSeedService.setDemoActiveForTest(true);
    expect(GuestSeedService.isBrowseDemoMode, isTrue);

    // If any code path touched FirebaseAuth / Firestore, pumping would throw (Firebase is not initialised).
    await tester.pumpWidget(const MaterialApp(
      home: LateralTransferScreen(userId: '', itemsToTransfer: [], initialTab: 'send'),
    ));
    await tester.pump();

    expect(find.byKey(const Key('sell_transfer_demo_cta')), findsOneWidget);
    expect(find.text('Create a free account to sell or transfer items.'), findsOneWidget);
    expect(find.text(kSellTransferDemoCta), findsOneWidget);
    // Blocked entry points: no tabs, no forms, no claim field.
    expect(find.text('Claim this item'), findsNothing);
    expect(find.byKey(const Key('claim_code_field')), findsNothing);
    expect(find.byKey(const Key('transfer_type_dropdown')), findsNothing);
    expect(http.clients, 0, reason: 'zero HTTP clients created');
  });

  testWidgets('Browse Demo is also blocked when the screen opens on the Claim tab', (tester) async {
    GuestSeedService.setDemoActiveForTest(true);
    await tester.pumpWidget(const MaterialApp(
      home: LateralTransferScreen(userId: '', itemsToTransfer: [], initialTab: 'claim'),
    ));
    await tester.pump();
    expect(find.text('Create a free account to sell or transfer items.'), findsOneWidget);
    expect(find.byKey(const Key('claim_code_field')), findsNothing);
  });
}