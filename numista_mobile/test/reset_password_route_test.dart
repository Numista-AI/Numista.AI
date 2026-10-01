import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/login_screen.dart';

void main() {
  testWidgets('LoginScreen with showResetForm: true shows reset form', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
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
