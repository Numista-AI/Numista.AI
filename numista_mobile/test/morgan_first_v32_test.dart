import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/morgan_first_home_screen.dart';
import 'package:numista_ai/screens/home_dashboard.dart';
import 'package:numista_ai/services/morgan_first_service.dart';
import 'package:numista_ai/widgets/morgan_full_site_toggle.dart';

void main() {
  testWidgets('AT-03, AT-06, AT-07: Type -> Confirm Card -> Fix Details -> Add -> Done',
      (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    int proposeCalls = 0;
    int confirmCalls = 0;
    String? lastConfirmedId;
    bool switchedToFullSite = false;

    await tester.pumpWidget(
      MaterialApp(
        home: MorganFirstHomeScreen(
          onSwitchToFullSite: () => switchedToFullSite = true,
          proposeFn: (coinData) async {
            proposeCalls++;
            return {'proposal_id': 'prop-$proposeCalls', 'coin': coinData};
          },
          confirmFn: (proposalId) async {
            confirmCalls++;
            lastConfirmedId = proposalId;
            return {'status': 'success', 'coin_id': 'coin-1'};
          },
        ),
      ),
    );

    // 3 balanced tiles, Upload tile hidden
    expect(find.byKey(const Key('tile_photo')), findsOneWidget);
    expect(find.byKey(const Key('tile_scan')), findsOneWidget);
    expect(find.byKey(const Key('tile_type')), findsOneWidget);
    expect(find.text('Upload file'), findsNothing);

    // Go to Type
    await tester.tap(find.byKey(const Key('tile_type')));
    await tester.pumpAndSettle();

    expect(find.text('Type your question'), findsOneWidget);
    await tester.enterText(
        find.byKey(const Key('morgan_type_input')), '1921 Morgan dollar, Denver, about fine');
    await tester.tap(find.byKey(const Key('type_submit_btn')));
    await tester.pumpAndSettle();

    // AT-03: Confirm card shown, ZERO confirm calls yet
    expect(find.byKey(const Key('morgan_confirm_card')), findsOneWidget);
    expect(confirmCalls, 0);
    expect(find.textContaining('Morgan is fairly sure (85%)'), findsOneWidget);

    // AT-06: Fix details -> edit -> returns to confirm card without saving
    await tester.tap(find.byKey(const Key('confirm_fix_btn')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('morgan_fix_details')), findsOneWidget);
    await tester.enterText(find.byKey(const Key('fix_condition_input')), 'MS-63');
    await tester.tap(find.byKey(const Key('fix_done_btn')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('morgan_confirm_card')), findsOneWidget);
    expect(find.textContaining('Condition: MS-63'), findsOneWidget);
    expect(confirmCalls, 0);

    // Tap Add to collection -> writes once
    await tester.tap(find.byKey(const Key('confirm_add_btn')));
    await tester.pumpAndSettle();

    expect(confirmCalls, 1);
    expect(lastConfirmedId, 'prop-2');
    expect(find.byKey(const Key('morgan_done_heading')), findsOneWidget);

    // AT-07: See my coins switches to Full site
    await tester.tap(find.byKey(const Key('see_my_coins_btn')));
    await tester.pumpAndSettle();
    expect(switchedToFullSite, isTrue);
  });

  testWidgets('AT-04 & AT-05: Under 40% has no Add button; Skip asks and does not save',
      (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(1024, 768));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    int confirmCalls = 0;

    // Test <40% confidence words and button gating
    expect(MorganFirstService.confidenceWords(32),
        "Morgan can't tell - try another photo");
    expect(MorganFirstService.canAddForConfidence(32), isFalse);
    expect(MorganFirstService.canAddForConfidence(40), isTrue);
    expect(MorganFirstService.highlightFixFirst(55), isTrue);

    await tester.pumpWidget(
      MaterialApp(
        home: MorganFirstHomeScreen(
          onSwitchToFullSite: () {},
          proposeFn: (coinData) async => {'proposal_id': 'prop-low'},
          confirmFn: (proposalId) async {
            confirmCalls++;
            return {'status': 'success'};
          },
          identifyPhotoFn: (front, back, isScan) async => {
            'Year': '1921',
            'Denomination': 'Morgan Dollar',
            'confidence': 30,
          },
        ),
      ),
    );

    // Go to Type -> confirm card -> test Skip confirmation (AT-05)
    await tester.tap(find.byKey(const Key('tile_type')));
    await tester.pumpAndSettle();
    await tester.enterText(
        find.byKey(const Key('morgan_type_input')), '1921 Morgan dollar');
    await tester.tap(find.byKey(const Key('type_submit_btn')));
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('confirm_skip_btn')));
    await tester.pumpAndSettle();
    expect(find.text('Throw away this photo?'), findsOneWidget);

    await tester.tap(find.byKey(const Key('skip_discard_btn')));
    await tester.pumpAndSettle();
    expect(confirmCalls, 0);
    expect(find.text("Hello. I'm Morgan."), findsOneWidget);
  });

  testWidgets('AT-16: No microphone control & 390/1024/1440 layout check',
      (WidgetTester tester) async {
    for (final size in [
      const Size(1440, 900),
      const Size(1024, 768),
      const Size(390, 844),
    ]) {
      await tester.binding.setSurfaceSize(size);

      // 1. MorganFirstHomeScreen
      await tester.pumpWidget(
        MaterialApp(
          home: MorganFirstHomeScreen(
            onSwitchToFullSite: () {},
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byIcon(Icons.mic), findsNothing);
      expect(find.byIcon(Icons.mic_none), findsNothing);
      expect(find.byIcon(Icons.mic_rounded), findsNothing);
      expect(find.byIcon(Icons.mic_none_rounded), findsNothing);
      expect(find.text('Microphone'), findsNothing);

      // 2. FullSiteMorganBar + HomeDashboard Ask Morgan box
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Column(
              children: [
                FullSiteMorganBar(onBackToMorgan: () {}),
                Expanded(
                  child: HomeDashboard(
                    testStream: Stream.value(CombinedDashboardData(
                      coins: const [],
                      currency: const [],
                      worldItems: const [],
                    )),
                    onAskMorgan: () {},
                    onTakePhoto: () {},
                  ),
                ),
              ],
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byIcon(Icons.mic), findsNothing);
      expect(find.byIcon(Icons.mic_none), findsNothing);
      expect(find.byIcon(Icons.mic_rounded), findsNothing);
      expect(find.byIcon(Icons.mic_none_rounded), findsNothing);
      expect(find.text('Microphone'), findsNothing);
      expect(find.text('Type your question'), findsOneWidget);
      expect(find.text('Back to Morgan'), findsOneWidget);
    }
    await tester.binding.setSurfaceSize(null);
  });
}
