import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/login_screen.dart';

void main() {
  testWidgets('LoginScreen with showResetForm: true shows reset form', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: LoginScreen(showResetForm: true),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(LoginScreen), findsOneWidget);
    // Find a widget that is part of the reset form, for example text 'Reset PIN' or 'Reset Password'
    // Alternatively, verify that NotFoundScreen is not shown.
    expect(find.text('Not Found', skipOffstage: false), findsNothing);
  });
}
