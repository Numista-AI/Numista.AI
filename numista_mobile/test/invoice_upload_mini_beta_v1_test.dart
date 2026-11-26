import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/add_coins_hub.dart';
import 'package:numista_ai/screens/review_hub_screen.dart';

void main() {
  group('AddCoinsHub Invoice Upload Fix (Defect 1)', () {
    testWidgets('renders exactly ONE Upload an invoice card and bottom tabs switch cleanly', (tester) async {
      tester.view.physicalSize = const Size(1280, 1400);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      // 1. Default AddCoinsHub renders exactly one 'Upload an invoice' card (zero dead duplicate)
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: AddCoinsHub()),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Upload an invoice'), findsOneWidget);
      expect(find.byKey(const Key('add_coins_upload_invoice_card')), findsOneWidget);
      expect(find.text('More ways to add'), findsOneWidget);
      expect(tester.takeException(), isNull);

      // 2. Expanded hub with bottom TabBar: tapping a tab invokes TabBar.onTap + scroll cleanly
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: AddCoinsHub(
              key: Key('expanded_add_coins_hub'),
              initialTabName: 'manual',
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Upload an invoice'), findsOneWidget);
      expect(find.text('Upload Files'), findsOneWidget);
      expect(find.text('Manual Entry'), findsOneWidget);
      expect(find.text('Open Manual Entry'), findsOneWidget);

      await tester.ensureVisible(find.text('Manual Entry'));
      await tester.tap(find.text('Manual Entry'));
      await tester.pumpAndSettle();
      expect(find.text('Open Manual Entry'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  });

  group('ReviewHubScreen Arithmetic Guard & Needs Review Badge (Defects 2 & 3)', () {
    test('isHighConfidenceItem & passesMathSanityCheck enforce unit * qty == line_total', () {
      final order1Verified = <String, dynamic>{
        'status': 'pending',
        'confidence_score': 1.0,
        'math_check_passed': true,
        'review_needed': false,
        'unit_cost_cents': 10700,
        'line_total_cents': 21400,
        'Quantity': 2,
        'allocated_fees': 0.0,
        'purchase_date': '2026-11-19',
      };
      final order2Verified = <String, dynamic>{
        'status': 'pending',
        'confidence_score': 1.0,
        'math_check_passed': true,
        'review_needed': false,
        'unit_cost_cents': 10700,
        'line_total_cents': 21400,
        'Quantity': 2,
        'allocated_fees': 9.95,
        'purchase_date': '2026-11-18',
      };
      final backendFlaggedMismatch = <String, dynamic>{
        'status': 'pending',
        'confidence_score': 1.0,
        'math_check_passed': false,
        'review_needed': true,
        'needs_review_reason': '2 x \$54.75 = \$109.50 != line total \$214.00',
        'unit_cost_cents': 5475,
        'line_total_cents': 21400,
        'Quantity': 2,
      };
      final clientDetectedMismatch = <String, dynamic>{
        'status': 'pending',
        'confidence_score': 1.0,
        'unit_cost_cents': 5475,
        'line_total_cents': 21400,
        'Quantity': 2,
      };

      expect(ReviewHubScreen.passesMathSanityCheck(order1Verified), isTrue);
      expect(ReviewHubScreen.isHighConfidenceItem(order1Verified), isTrue);
      expect(ReviewHubScreen.isHighConfidenceItem(order2Verified), isTrue);

      expect(ReviewHubScreen.passesMathSanityCheck(backendFlaggedMismatch), isFalse);
      expect(ReviewHubScreen.isHighConfidenceItem(backendFlaggedMismatch), isFalse);

      expect(ReviewHubScreen.passesMathSanityCheck(clientDetectedMismatch), isFalse);
      expect(ReviewHubScreen.isHighConfidenceItem(clientDetectedMismatch), isFalse);

      final items = [order1Verified, order2Verified, backendFlaggedMismatch, clientDetectedMismatch];
      final highConfCount = items.where(ReviewHubScreen.isHighConfidenceItem).length;
      expect(highConfCount, 2);
    });

    testWidgets('renders amber Needs review badge instead of green Conf 100% on mismatch', (tester) async {
      final mismatchRow = <String, dynamic>{
        'status': 'pending',
        'confidence_score': 1.0,
        'math_check_passed': false,
        'review_needed': true,
        'unit_cost_cents': 5475,
        'line_total_cents': 21400,
        'Quantity': 2,
      };
      final verifiedRow = <String, dynamic>{
        'status': 'pending',
        'confidence_score': 1.0,
        'math_check_passed': true,
        'review_needed': false,
        'unit_cost_cents': 10700,
        'line_total_cents': 21400,
        'Quantity': 2,
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Column(
              children: [
                KeyedSubtree(
                  key: const Key('mismatch_badge'),
                  child: ReviewHubScreen.buildConfidenceOrNeedsReviewBadge(mismatchRow, confidence: 1.0),
                ),
                KeyedSubtree(
                  key: const Key('verified_badge'),
                  child: ReviewHubScreen.buildConfidenceOrNeedsReviewBadge(verifiedRow, confidence: 1.0),
                ),
              ],
            ),
          ),
        ),
      );

      expect(
        find.descendant(of: find.byKey(const Key('mismatch_badge')), matching: find.text('Needs review')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: find.byKey(const Key('mismatch_badge')), matching: find.text('Conf: 100%')),
        findsNothing,
      );
      expect(
        find.descendant(of: find.byKey(const Key('verified_badge')), matching: find.text('Conf: 100%')),
        findsOneWidget,
      );
    });
  });
}
