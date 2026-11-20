import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:numista_ai/screens/upcoming_releases_screen.dart';
import 'package:numista_ai/services/upcoming_releases_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
    UpcomingReleasesService.resetForTest();
  });

  testWidgets('UpcomingReleasesScreen loads and displays releases without broken image icon', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.runAsync(() async {
      await tester.pumpWidget(
        const MaterialApp(
          home: UpcomingReleasesScreen(),
        ),
      );
      // Allow async fetch and fallback to complete
      await Future.delayed(const Duration(milliseconds: 200));
    });

    // Rebuild after async state update
    await tester.pump();

    // Verify AppBar title is rendered
    expect(find.text('Upcoming US Mint Releases'), findsOneWidget);

    // Verify filter choice chips
    expect(find.widgetWithText(ChoiceChip, 'All'), findsOneWidget);
    expect(find.widgetWithText(ChoiceChip, 'Coming Soon'), findsOneWidget);
    expect(find.widgetWithText(ChoiceChip, 'Available'), findsOneWidget);
    expect(find.widgetWithText(ChoiceChip, 'Sold Out'), findsOneWidget);

    // Verify hero item is rendered from fallback
    expect(find.text('Morgan 2026 Silver Dollar'), findsOneWidget);
    // Verify second item in list is rendered
    expect(find.text('American Eagle 2026 One Ounce Silver Proof Coin'), findsOneWidget);
    // Verify broken image icon is never used
    expect(find.byIcon(Icons.image_not_supported), findsNothing);
  });

  testWidgets('UpcomingReleasesScreen renders coin medallion placeholder when imageUrl is null or blank', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    final mockClient = MockClient((request) async {
      return http.Response(
        jsonEncode({
          'products': [
            {
              'item_number': '26NOIMG1',
              'title': 'Hero Without Image',
              'price': '\$99.00',
              'status': 'Coming Soon',
              'release_date': 'Fall 2026',
              'image_url': null,
              'product_url': 'https://catalog.usmint.gov',
              'program': 'Test Program',
              'badge': '',
            },
            {
              'item_number': '26NOIMG2',
              'title': 'List Item With Blank Image',
              'price': '\$49.00',
              'status': 'Available',
              'release_date': 'Winter 2026',
              'image_url': '   ',
              'product_url': 'https://catalog.usmint.gov',
              'program': 'Test Program',
              'badge': '',
            },
          ],
        }),
        200,
      );
    });

    await tester.runAsync(() async {
      await http.runWithClient(
        () async {
          await tester.pumpWidget(
            const MaterialApp(
              home: UpcomingReleasesScreen(),
            ),
          );
          await Future.delayed(const Duration(milliseconds: 200));
        },
        () => mockClient,
      );
    });

    await tester.pump();

    expect(find.text('Hero Without Image'), findsOneWidget);
    expect(find.text('List Item With Blank Image'), findsOneWidget);
    expect(find.byIcon(Icons.image_not_supported), findsNothing);
    expect(find.byIcon(Icons.toll_outlined), findsNWidgets(2));
  });
}
