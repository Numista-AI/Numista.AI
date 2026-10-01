import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/widgets/auth_gate.dart';
import 'package:numista_ai/screens/login_screen.dart';

void main() {
  testWidgets('AuthGate with showResetForm: true shows reset form', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      MaterialApp(
        home: AuthGate(
          showResetForm: true,
          authStream: Stream.value(null),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(LoginScreen), findsOneWidget);
    expect(find.text('Reset Your 6-Digit PIN', skipOffstage: false), findsWidgets);
    expect(find.text('Not Found', skipOffstage: false), findsNothing);
  });
}
