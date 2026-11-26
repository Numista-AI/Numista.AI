import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/estate_planning_screen.dart';

void main() {
  group('Estate access gate (NET-827 C5)', () {
    test('T-ESTATE-1: family_estate tier grants access', () {
      expect(
        hasEstateAccess(subscriptionTier: 'family_estate', isLifetime: false),
        isTrue,
      );
    });

    test('T-ESTATE-2: isLifetime flag grants access', () {
      expect(
        hasEstateAccess(subscriptionTier: 'free', isLifetime: true),
        isTrue,
      );
    });

    test('T-ESTATE-3: estate (Gold) subscription does NOT grant access', () {
      expect(
        hasEstateAccess(subscriptionTier: 'estate', isLifetime: false),
        isFalse,
      );
    });

    test('T-ESTATE-4: pro (Copper) subscription does NOT grant access', () {
      expect(
        hasEstateAccess(subscriptionTier: 'pro', isLifetime: false),
        isFalse,
      );
    });

    test('T-ESTATE-5: numismatist and dealer do NOT grant access', () {
      expect(
        hasEstateAccess(subscriptionTier: 'numismatist', isLifetime: false),
        isFalse,
      );
      expect(
        hasEstateAccess(subscriptionTier: 'dealer', isLifetime: false),
        isFalse,
      );
    });

    test('T-ESTATE-6: free and empty tier do NOT grant access', () {
      expect(
        hasEstateAccess(subscriptionTier: 'free', isLifetime: false),
        isFalse,
      );
      expect(
        hasEstateAccess(subscriptionTier: '', isLifetime: false),
        isFalse,
      );
    });

    test('T-ESTATE-7: non-allowlisted @numista.ai email does NOT grant access', () {
      expect(
        hasEstateAccess(
          subscriptionTier: 'free',
          isLifetime: false,
          email: 'beta@numista.ai',
        ),
        isFalse,
      );
    });

    test('T-ESTATE-8: kEstateStaffUidAllowlist is empty', () {
      expect(kEstateStaffUidAllowlist, isEmpty);
      expect(
        isEstateStaff(uid: 'some-random-uid', email: 'user@example.com'),
        isFalse,
      );
    });

    test('T-ESTATE-9 (Q5): exact staff allowlist match after trim + lowercase', () {
      expect(kEstateStaffAllowlist.length, 2);
      expect(isEstateStaff(email: ' Eric@Numista.AI '), isTrue);
      expect(isEstateStaff(email: 'grokbot@numista.ai'), isTrue);

      for (final bad in [
        'someone@numista.ai',
        'xeric@numista.ai',
        'eric@numista.ai.evil.com',
        'eric@numista.ai x',
        '',
      ]) {
        expect(isEstateStaff(email: bad), isFalse, reason: 'Expected false for "$bad"');
      }
    });

    testWidgets('onError fails closed (drives real _listenToTier onError)', (tester) async {
      final controller = StreamController<Map<String, dynamic>>.broadcast();
      addTearDown(controller.close);

      await tester.pumpWidget(
        MaterialApp(
          home: EstatePlanningScreen(
            tierStreamOverride: controller.stream,
            userEmailOverride: 'user@example.com',
            userUidOverride: 'uid_user',
          ),
        ),
      );

      // Before stream emits, spinner is shown (fail-closed while loading).
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.byType(TabBarView), findsNothing);

      // Trigger the real onError handler on _tierSub.
      controller.addError(Exception('firestore unavailable'));
      await tester.pump();

      expect(find.byType(CircularProgressIndicator), findsNothing);
      expect(find.byType(TabBarView), findsNothing);
      expect(find.text('Premium Feature'), findsOneWidget);
    });
  });
}
