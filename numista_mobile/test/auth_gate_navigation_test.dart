import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/widgets/auth_gate.dart';
import 'package:numista_ai/screens/login_screen.dart';
import 'package:numista_ai/screens/public_info_screens.dart';

void main() {
  testWidgets('AuthGate unauthenticated renders LoginScreen with initial tab', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(
      MaterialApp(
        home: AuthGate(
          initialAuthTab: 1,
          authStream: Stream.value(null),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(LoginScreen), findsOneWidget);
  });

  testWidgets('AuthGate renders PublicInfoShell when publicRoute is supplied', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(
      MaterialApp(
        home: AuthGate(
          publicRoute: '/about',
          authStream: Stream.value(null),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(PublicInfoShell), findsOneWidget);
  });

  testWidgets('AuthGate.navigateTo resets navigation stack and renders target AuthGate', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (context) => Scaffold(
            body: ElevatedButton(
              onPressed: () {
                AuthGate.navigateTo(
                  context,
                  initialAuthTab: 1,
                  authStream: Stream.value(null),
                );
              },
              child: const Text('Go to AuthGate'),
            ),
          ),
        ),
      ),
    );

    expect(find.text('Go to AuthGate'), findsOneWidget);
    await tester.tap(find.text('Go to AuthGate'));
    await tester.pumpAndSettle();

    expect(find.byType(AuthGate), findsOneWidget);
    expect(find.byType(LoginScreen), findsOneWidget);
  });
}
