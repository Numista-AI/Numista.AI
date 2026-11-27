import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/widgets/auth_gate.dart';
import 'package:numista_ai/screens/login_screen.dart';
import 'package:numista_ai/screens/base_layout.dart';
import 'package:numista_ai/screens/public_info_screens.dart';
import 'package:numista_ai/services/guest_seed_service.dart';

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

  testWidgets('D4: Exiting Demo Vault clears _cachedDemoActive and lands on LoginScreen cleanly', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1200, 1800);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
      AuthGate.clearDemoState();
      GuestSeedService.deactivateBrowseDemo();
    });

    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (context) => Column(
            children: [
              ElevatedButton(
                onPressed: () {
                  AuthGate.navigateTo(
                    context,
                    isDemo: true,
                    authStream: Stream.value(null),
                    testDemoHomeBuilder: (_) =>
                        const Scaffold(body: Text('DEMO_VAULT_ACTIVE')),
                  );
                },
                child: const Text('Enter Demo'),
              ),
            ],
          ),
        ),
      ),
    );
    await tester.tap(find.text('Enter Demo'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 200));
    expect(find.text('DEMO_VAULT_ACTIVE'), findsOneWidget);
    expect(GuestSeedService.isBrowseDemoMode, isTrue);

    // Exit Demo Vault using D4 fix path (navigateTo itself clears _cachedDemoActive and GuestSeedService)
    final ctx = tester.element(find.text('DEMO_VAULT_ACTIVE'));
    AuthGate.navigateTo(ctx, authStream: Stream.value(null));
    await tester.pumpAndSettle();

    expect(GuestSeedService.isBrowseDemoMode, isFalse);
    expect(find.byType(LoginScreen), findsOneWidget);
    expect(find.text('DEMO_VAULT_ACTIVE'), findsNothing);
    expect(find.byType(BaseLayout), findsNothing);
    expect(find.text("We couldn't load your home"), findsNothing);
  });
}
