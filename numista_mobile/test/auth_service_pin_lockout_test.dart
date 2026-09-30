import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/auth_service.dart';
import 'package:numista_ai/screens/login_screen.dart';

void main() {
  group('AuthService PIN & Lockout Security (REQ-025)', () {
    test('4a: user-not-found returns generic error without revealing account existence', () {
      final msg = AuthService.friendlyError('user-not-found');
      expect(msg, 'Incorrect email or PIN.');
      expect(msg.contains('No account'), isFalse, reason: 'Must not reveal account existence');
      expect(msg.toLowerCase().contains('password'), isFalse, reason: 'Must use PIN wording');
    });

    test('4a: wrong-password and invalid-credential return identical generic error', () {
      final wrongPwd = AuthService.friendlyError('wrong-password');
      final invalidCred = AuthService.friendlyError('invalid-credential');
      final invalidLoginCred = AuthService.friendlyError('invalid-login-credentials');

      expect(wrongPwd, 'Incorrect email or PIN.');
      expect(invalidCred, 'Incorrect email or PIN.');
      expect(invalidLoginCred, 'Incorrect email or PIN.');
      expect(wrongPwd, equals(AuthService.friendlyError('user-not-found')));
    });

    test('4c: too-many-requests returns 15-minute friendly lockout message', () {
      final msg = AuthService.friendlyError('too-many-requests');
      expect(msg, 'Too many tries. Please wait 15 minutes or use Forgot your PIN.');
    });

    testWidgets('Item 2 & 5: LoginScreen UI verifies PIN-first layout, removed badge, and prominent Google', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1200, 1800);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: LoginScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // 1. PIN is the main path
      expect(find.text('6-Digit PIN'), findsOneWidget);

      // 2. "Instead of a password" badge is REMOVED
      expect(find.text('Instead of a password'), findsNothing);

      // 3. "Older account? Sign in with password" is present as bottom toggle
      expect(find.text('Older account? Sign in with password'), findsOneWidget);

      // 4. "Forgot your PIN?" is present; old "Forgot your PIN or password?" is NOT present
      expect(find.text('Forgot your PIN?'), findsOneWidget);
      expect(find.text('Forgot your PIN or password?'), findsNothing);

      // 5. "Continue with Google" remains prominent
      expect(find.text('Continue with Google'), findsOneWidget);
    });
  });
}
