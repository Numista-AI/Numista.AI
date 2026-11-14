import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/base_layout.dart';
import 'package:numista_ai/screens/home_dashboard.dart';
import 'package:numista_ai/widgets/collection_card_image.dart';

Widget _wrapTestHome({
  List<Map<String, dynamic>> coins = const [],
  bool isLoading = false,
  bool hasError = false,
  int reviewQueueCount = 0,
}) {
  late Stream<CombinedDashboardData> stream;
  if (isLoading) {
    stream = const Stream<CombinedDashboardData>.empty();
  } else if (hasError) {
    stream = Stream<CombinedDashboardData>.error(Exception('load failed'));
  } else {
    stream = Stream<CombinedDashboardData>.value(
      CombinedDashboardData(coins: coins, currency: const [], worldItems: const []),
    );
  }

  return MaterialApp(
    home: Scaffold(
      body: SizedBox(
        width: 1160,
        height: 900,
        child: HomeDashboard(
          reviewQueueCount: reviewQueueCount,
          isReviewCountLoading: isLoading,
          testStream: stream,
        ),
      ),
    ),
  );
}

void main() {
  final coinWithoutPhoto = <String, dynamic>{
    'id': 'c1',
    'Program/Series': 'Peace Dollar',
    'Year': '1922',
    'cpgRetail': '35',
  };

  final coinWithPhoto = <String, dynamic>{
    'id': 'c2',
    'Program/Series': 'Morgan Dollar',
    'Year': '1921',
    'image_url_obverse': 'https://example.com/morgan.jpg',
    'cpgRetail': '12400',
  };

  testWidgets('1. Media rule: CollectionCardImage and No photo yet fallback, zero dollar signs', (tester) async {
    await tester.pumpWidget(_wrapTestHome(coins: [coinWithoutPhoto]));
    await tester.pumpAndSettle();
    expect(find.byType(CollectionCardImage), findsOneWidget);
    expect(find.textContaining('No photo'), findsOneWidget);
    expect(find.textContaining(r'$'), findsNothing);
  });

  testWidgets('2. Value hidden by default; Show value reveals and Hide value hides', (tester) async {
    await tester.pumpWidget(_wrapTestHome(coins: [coinWithPhoto]));
    await tester.pump();
    await tester.pump();
    expect(find.text('Hidden for your safety'), findsOneWidget);
    expect(find.textContaining('12,400'), findsNothing);

    await tester.tap(find.text('Show value'));
    await tester.pump();
    expect(find.textContaining('12,400 dollars'), findsOneWidget);
    expect(find.text('Hide value'), findsOneWidget);

    await tester.tap(find.text('Hide value'));
    await tester.pump();
    expect(find.text('Hidden for your safety'), findsOneWidget);
  });

  testWidgets('3. Typography >= 18px and tap targets >= 56px', (tester) async {
    await tester.pumpWidget(_wrapTestHome(coins: [coinWithoutPhoto]));
    await tester.pumpAndSettle();
    for (final w in tester.widgetList<Text>(find.byType(Text))) {
      final size = w.style?.fontSize;
      if (size != null) {
        expect(size, greaterThanOrEqualTo(18.0), reason: 'Text "${w.data}" had fontSize $size');
      }
    }
    expect(
      tester.getSize(find.widgetWithText(OutlinedButton, 'Show value')).height,
      greaterThanOrEqualTo(56.0),
    );
  });

  testWidgets('4. Empty, Loading, and Error states', (tester) async {
    await tester.pumpWidget(_wrapTestHome(isLoading: true));
    expect(find.text('Loading your home'), findsOneWidget);

    await tester.pumpWidget(_wrapTestHome(hasError: true));
    await tester.pump();
    expect(find.text("We couldn't load your home"), findsOneWidget);
    expect(find.text('Try again'), findsOneWidget);

    await tester.pumpWidget(_wrapTestHome(coins: const []));
    await tester.pump();
    expect(find.text('Add your first coin'), findsOneWidget);
    expect(find.text('Show value'), findsNothing);
  });

  testWidgets('5. Desktop accordion: single group open at a time', (tester) async {
    String? openGroup;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: StatefulBuilder(
            builder: (context, setState) => Column(
              children: [
                SidebarAccordionGroup(
                  title: 'Research',
                  icon: Icons.search,
                  isExpanded: openGroup == 'Research',
                  onToggle: () => setState(() => openGroup = openGroup == 'Research' ? null : 'Research'),
                  children: const [Text('Coin Search', style: TextStyle(fontSize: 18))],
                ),
                SidebarAccordionGroup(
                  title: 'Estate & Transfers',
                  icon: Icons.description_outlined,
                  isExpanded: openGroup == 'Estate & Transfers',
                  onToggle: () => setState(() => openGroup = openGroup == 'Estate & Transfers' ? null : 'Estate & Transfers'),
                  children: const [Text('Estate Planning', style: TextStyle(fontSize: 18))],
                ),
              ],
            ),
          ),
        ),
      ),
    );

    await tester.tap(find.text('Research'));
    await tester.pump();
    expect(find.text('Coin Search'), findsOneWidget);
    expect(find.text('Estate Planning'), findsNothing);

    await tester.tap(find.text('Estate & Transfers'));
    await tester.pump();
    expect(find.text('Coin Search'), findsNothing);
    expect(find.text('Estate Planning'), findsOneWidget);
  });

  testWidgets('6. Phone 390px menu & drill-in Back', (tester) async {
    String? drillGroup;
    await tester.pumpWidget(
      MaterialApp(
        home: SizedBox(
          width: 390,
          height: 844,
          child: StatefulBuilder(
            builder: (context, setState) => PhoneMenuOverlay(
              displayName: 'Sample User',
              activeRoute: 'Home Dashboard',
              reviewCount: 3,
              isReviewLoading: false,
              drillGroup: drillGroup,
              isAdmin: false,
              onClose: () {},
              onBack: () => setState(() => drillGroup = null),
              onOpenGroup: (g) => setState(() => drillGroup = g),
              onSelectRoute: (_) {},
            ),
          ),
        ),
      ),
    );

    expect(find.text('Close'), findsOneWidget);
    expect(find.text('Wishlist'), findsOneWidget);
    await tester.tap(find.text('Research'));
    await tester.pump();
    expect(find.text('Back'), findsOneWidget);
    expect(find.text('Coin Search'), findsOneWidget);
    await tester.tap(find.text('Back'));
    await tester.pump();
    expect(find.text('Close'), findsOneWidget);
  });
}
