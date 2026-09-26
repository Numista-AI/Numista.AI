import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/upcoming_releases_screen.dart';

void main() {
  testWidgets('UpcomingReleasesScreen loads and displays releases', (WidgetTester tester) async {
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
  });
}
