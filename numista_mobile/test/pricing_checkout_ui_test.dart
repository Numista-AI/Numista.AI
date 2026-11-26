import 'dart:async';
import 'dart:convert';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:numista_ai/constants.dart';
import 'package:numista_ai/screens/estate_planning_screen.dart';
import 'package:numista_ai/screens/public_info_screens.dart';
import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/services/stripe_service.dart';
import 'package:numista_ai/widgets/auth_gate.dart';

class _FakeUser extends Fake implements User {
  @override
  final String uid;
  @override
  final String? email;
  @override
  final bool isAnonymous;

  _FakeUser({
    required this.uid,
    required this.email,
    required this.isAnonymous,
  });
}

void main() {
  tearDown(() {
    HttpAuthClient.tokenProviderOverride = null;
    HttpAuthClient.httpClientOverride = null;
  });

  group('NET-827 v2.0.7 /pricing CHECKOUT-UI (T-UI-1..10)', () {
    testWidgets('T-UI-1: Early Access Included — Plans TBA and \$0 / month are absent', (tester) async {
      tester.view.physicalSize = const Size(1280, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(
        const MaterialApp(
          home: PublicInfoShell(targetRoute: '/pricing', isSignedInOverride: false),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('Early Access Included'), findsNothing);
      expect(find.textContaining('Plans TBA'), findsNothing);
      expect(find.textContaining(r'$0 / month'), findsNothing);
    });

    testWidgets('T-UI-2: Regular Monthly and Yearly toggle renders exact locked prices', (tester) async {
      tester.view.physicalSize = const Size(1280, 2000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: false,
            nowUtcOverride: DateTime.utc(2026, 12, 1, 12),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('10 items in your vault'), findsOneWidget);
      expect(find.textContaining(r'$3.99/mo'), findsOneWidget);
      expect(find.textContaining(r'$7.99/mo'), findsOneWidget);
      expect(find.textContaining(r'$9.99/mo'), findsOneWidget);
      expect(find.textContaining(r'$15.99/mo'), findsOneWidget);
      expect(find.textContaining(r'$500.00 one-time'), findsOneWidget);

      await tester.tap(find.byKey(const Key('billing_toggle_yearly')));
      await tester.pumpAndSettle();

      expect(find.textContaining(r'$39.99/yr'), findsOneWidget);
      expect(find.textContaining(r'$79.99/yr'), findsOneWidget);
      expect(find.textContaining(r'$99.00/yr'), findsOneWidget);
      expect(find.textContaining(r'$150.00/yr'), findsOneWidget);
      expect(find.textContaining(r'$500.00 one-time'), findsOneWidget);
      expect(find.textContaining('Why is Gold our top tier?'), findsOneWidget);
    });

    testWidgets('T-UI-3: Inside CHRISTMAS2026 window shows exact sale prices, Jan 15 end date, renewal, & Lifetime excluded', (tester) async {
      tester.view.physicalSize = const Size(1280, 2000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: false,
            nowUtcOverride: DateTime.utc(2026, 12, 20, 12),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('CHRISTMAS2026 Holiday Sale'), findsOneWidget);
      expect(find.textContaining(r'$1.99/mo'), findsWidgets);
      expect(find.textContaining(r'$19.99/yr'), findsWidgets);
      expect(find.textContaining(r'$3.99/mo'), findsWidgets);
      expect(find.textContaining(r'$39.99/yr'), findsWidgets);
      expect(find.textContaining(r'$4.99/mo'), findsWidgets);
      expect(find.textContaining(r'$49.50/yr'), findsWidgets);
      expect(find.textContaining(r'$7.99/mo'), findsWidgets);
      expect(find.textContaining(r'$75.00/yr'), findsWidgets);
      expect(find.textContaining('Offer ends January 15, 2027'), findsOneWidget);
      expect(find.textContaining('renews at full regular price'), findsWidgets);
      expect(find.textContaining(r'Lifetime Family Estate ($500) is excluded'), findsOneWidget);
    });

    testWidgets('T-UI-4: Before Dec 15 (1 Dec test day), CHRISTMAS2026 banner does not auto-show while promo input remains available', (tester) async {
      tester.view.physicalSize = const Size(1280, 2000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: false,
            nowUtcOverride: DateTime.utc(2026, 12, 1, 15),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('CHRISTMAS2026 Holiday Sale'), findsNothing);
      await tester.tap(find.text('Have a promo code?'));
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('pricing_promo_field')), findsOneWidget);
    });

    testWidgets('T-UI-5: Guest/unauthenticated sees Sign in to Subscribe and makes 0 HTTP calls to /api/stripe/*', (tester) async {
      tester.view.physicalSize = const Size(1280, 2000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      var httpCalls = 0;
      HttpAuthClient.httpClientOverride = MockClient((_) async {
        httpCalls++;
        return http.Response('{}', 200);
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: PublicInfoShell(targetRoute: '/pricing', isSignedInOverride: false),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Sign in to Subscribe'), findsWidgets);
      expect(find.text('Sign in to Buy'), findsOneWidget);
      expect(httpCalls, 0);
    });

    testWidgets('T-UI-6 (P5 exact-request): Signed-in excluded test account clicking Copper Monthly POSTs exact checkout request', (tester) async {
      tester.view.physicalSize = const Size(1280, 2000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final captured = <http.Request>[];
      HttpAuthClient.tokenProviderOverride = () async => 'fake-token';
      final mockClient = MockClient((req) async {
        captured.add(req);
        if (req.url.path == '/api/stripe/subscription-status') {
          return http.Response(
            jsonEncode({
              'stripe_tier': 'free',
              'subscription_status': 'active',
              'coin_limit': 10,
              'unlimited': false,
              'estate_access': false,
              'lifetime_family_estate': false,
            }),
            200,
          );
        }
        return http.Response(jsonEncode({'checkout_url': ''}), 200);
      });
      HttpAuthClient.httpClientOverride = mockClient;

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: true,
            uidOverride: 'uid_excluded_buyer',
            nowUtcOverride: DateTime.utc(2026, 12, 1, 15),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final copperBtn = find.byKey(const Key('plan_cta_pro'));
      await tester.ensureVisible(copperBtn);
      await tester.tap(copperBtn);
      await tester.pumpAndSettle();

      final posts = captured.where((r) => r.method == 'POST').toList();
      expect(posts, hasLength(1));
      final req = posts.single;
      expect(req.url.toString(), '$kApiBaseUrl/api/stripe/create-checkout-session');
      expect(req.headers['Authorization'], 'Bearer fake-token');
      final body = jsonDecode(req.body) as Map<String, dynamic>;
      expect(body, {'tier': 'pro', 'interval': 'month'});
      expect(body.containsKey('user_email'), isFalse);
    });

    testWidgets('T-UI-7: Signed-in founding_beta user sees Founding Beta banner and no Subscribe prompt', (tester) async {
      tester.view.physicalSize = const Size(1280, 2000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: true,
            uidOverride: 'uid_founder',
            statusFetcherOverride: (_) async => const SubscriptionStatusSnapshot(
              stripeTier: 'founding_beta',
              unlimited: true,
              estateAccess: true,
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(
        find.text('Founding Beta Member — Lifetime Access (including Estate) Included'),
        findsOneWidget,
      );
      expect(find.text('Included with Founding Beta'), findsWidgets);
      expect(find.text('Subscribe'), findsNothing);
    });

    testWidgets('T-UI-8: 409 already_subscribed and 502 show inline message without throwing', (tester) async {
      tester.view.physicalSize = const Size(1280, 2000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      CheckoutLaunchResult nextResult = const CheckoutLaunchResult(
        ok: false,
        statusCode: 409,
        errorCode: 'already_subscribed',
        message: 'You already have a plan.',
      );

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: true,
            uidOverride: 'uid_sub_existing',
            statusFetcherOverride: (_) async => const SubscriptionStatusSnapshot(stripeTier: 'free'),
            checkoutStarterOverride: ({required String tier, String interval = 'month', String? promoCode}) async => nextResult,
          ),
        ),
      );
      await tester.pumpAndSettle();

      await tester.ensureVisible(find.byKey(const Key('plan_cta_pro')));
      await tester.tap(find.byKey(const Key('plan_cta_pro')));
      await tester.pumpAndSettle();
      expect(find.text('You already have a plan.'), findsOneWidget);

      nextResult = const CheckoutLaunchResult(
        ok: false,
        statusCode: 502,
        message: 'Checkout is not active yet.',
      );
      await tester.tap(find.byKey(const Key('plan_cta_pro')));
      await tester.pumpAndSettle();
      expect(find.text('Checkout is not active yet.'), findsOneWidget);
    });

    testWidgets('T-UI-9: AuthGate(publicRoute: /pricing) with signed-in user renders PublicInfoShell', (tester) async {
      tester.view.physicalSize = const Size(1280, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final fakeUser = _FakeUser(uid: 'uid_signed_in', email: 'signed@example.com', isAnonymous: false);
      await tester.pumpWidget(
        MaterialApp(
          home: AuthGate(
            publicRoute: '/pricing',
            authStream: Stream.value(fakeUser),
          ),
        ),
      );
      await tester.pump();
      await tester.pump();

      expect(find.byType(PublicInfoShell), findsOneWidget);
      expect(find.textContaining('Simple Plans for Every Collection Size'), findsOneWidget);
    });

    testWidgets('T-UI-10 (P10 display scan): Zero raw internal keys, booleans, or bad badges in rendered /pricing text', (tester) async {
      tester.view.physicalSize = const Size(1280, 2000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: false,
            nowUtcOverride: DateTime.utc(2026, 12, 20, 12),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final renderedTexts = tester
          .widgetList<Text>(find.byType(Text))
          .map((w) => w.data ?? '')
          .where((s) => s.isNotEmpty)
          .toList();
      final joined = renderedTexts.join('\n');

      for (final forbidden in <String>[
        'numismatist',
        'dealer',
        'family_estate',
        'founding_beta',
        'stripe_tier',
      ]) {
        expect(joined.contains(forbidden), isFalse, reason: 'Found forbidden raw key "$forbidden" in /pricing UI');
      }
      final rawTokenRe = RegExp(r'\b(true|false|null)\b', caseSensitive: true);
      for (final line in renderedTexts) {
        if (line == 'As a true numismatics site, we rank our plans the way the metals actually trade.' ||
            line.contains('true numismatics site')) {
          continue;
        }
        expect(rawTokenRe.hasMatch(line), isFalse, reason: 'Raw boolean/null literal in rendered text: "$line"');
      }
    });

    testWidgets('Estate upgrade sheet removes \$9.99 placeholder and links to Lifetime \$500 & /pricing', (tester) async {
      final controller = StreamController<Map<String, dynamic>>.broadcast();
      addTearDown(controller.close);
      await tester.pumpWidget(
        MaterialApp(
          home: EstatePlanningScreen(
            tierStreamOverride: controller.stream,
            userEmailOverride: 'user@example.com',
            userUidOverride: 'uid_free',
            estateAccessFetcherOverride: (_) async => false,
          ),
        ),
      );
      controller.add({'stripe_tier': 'free'});
      await tester.pump();
      await tester.pump();

      expect(find.text('Premium Feature'), findsOneWidget);
      await tester.tap(find.byType(ElevatedButton).first);
      await tester.pumpAndSettle();

      expect(find.text('Lifetime Family Estate'), findsWidgets);
      expect(find.text(r'$500'), findsOneWidget);
      expect(find.text('View Plans & Upgrade'), findsOneWidget);
      expect(find.textContaining('coming soon'), findsNothing);
      expect(find.text(r'$9.99'), findsNothing);
    });

    testWidgets('T-UI-11 (Subscribe-gap 4a): Signed-in pending status shows loading state and disables all paid/lifetime CTAs', (tester) async {
      tester.view.physicalSize = const Size(1280, 2200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final completer = Completer<SubscriptionStatusSnapshot?>();
      var checkoutCalls = 0;

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: true,
            uidOverride: 'uid_pending',
            statusFetcherOverride: (_) => completer.future,
            checkoutStarterOverride: ({required String tier, String interval = 'month', String? promoCode}) async {
              checkoutCalls++;
              return const CheckoutLaunchResult(ok: true, statusCode: 200);
            },
          ),
        ),
      );
      await tester.pump();

      expect(find.byKey(const Key('pricing_status_loading_banner')), findsOneWidget);
      expect(find.text('Checking your account...'), findsOneWidget);
      expect(find.text('Subscribe'), findsNothing);
      expect(find.text(r'Buy Lifetime ($500)'), findsNothing);

      for (final keyName in <String>[
        'plan_cta_pro',
        'plan_cta_numismatist',
        'plan_cta_dealer',
        'plan_cta_estate',
        'plan_cta_family_estate',
      ]) {
        final btn = tester.widget<ElevatedButton>(find.byKey(Key(keyName)));
        expect(btn.onPressed, isNull, reason: '$keyName must be disabled while status is pending');
      }

      await tester.tap(find.byKey(const Key('plan_cta_pro')));
      await tester.pump();
      expect(checkoutCalls, 0);

      // Unmount widget cleanly so dispose cancels the 15s timeout timer.
      await tester.pumpWidget(const SizedBox.shrink());
    });

    testWidgets('T-UI-12 (Subscribe-gap 4b): Founding Beta transitions from disabled loading state to disabled Included with Founding Beta after 200', (tester) async {
      tester.view.physicalSize = const Size(1280, 2200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final completer = Completer<SubscriptionStatusSnapshot?>();

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: true,
            uidOverride: 'uid_beta_delayed',
            statusFetcherOverride: (_) => completer.future,
          ),
        ),
      );
      await tester.pump();

      expect(find.byKey(const Key('pricing_status_loading_banner')), findsOneWidget);
      for (final keyName in <String>[
        'plan_cta_pro',
        'plan_cta_numismatist',
        'plan_cta_dealer',
        'plan_cta_estate',
        'plan_cta_family_estate',
      ]) {
        expect(tester.widget<ElevatedButton>(find.byKey(Key(keyName))).onPressed, isNull);
      }

      completer.complete(const SubscriptionStatusSnapshot(
        stripeTier: 'founding_beta',
        unlimited: true,
        estateAccess: true,
      ));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('pricing_status_loading_banner')), findsNothing);
      expect(
        find.text('Founding Beta Member — Lifetime Access (including Estate) Included'),
        findsOneWidget,
      );
      expect(find.text('Included with Founding Beta'), findsNWidgets(5));
      for (final keyName in <String>[
        'plan_cta_pro',
        'plan_cta_numismatist',
        'plan_cta_dealer',
        'plan_cta_estate',
        'plan_cta_family_estate',
      ]) {
        expect(tester.widget<ElevatedButton>(find.byKey(Key(keyName))).onPressed, isNull);
      }
    });

    testWidgets('T-UI-13 (Subscribe-gap 4c): Paid-eligible non-beta account gets enabled Subscribe/Buy buttons only after 200', (tester) async {
      tester.view.physicalSize = const Size(1280, 2200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final completer = Completer<SubscriptionStatusSnapshot?>();
      final launchedTiers = <String>[];

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: true,
            uidOverride: 'uid_paid_eligible',
            nowUtcOverride: DateTime.utc(2026, 12, 1, 12),
            statusFetcherOverride: (_) => completer.future,
            checkoutStarterOverride: ({required String tier, String interval = 'month', String? promoCode}) async {
              launchedTiers.add(tier);
              return const CheckoutLaunchResult(ok: true, statusCode: 200);
            },
          ),
        ),
      );
      await tester.pump();

      for (final keyName in <String>[
        'plan_cta_pro',
        'plan_cta_numismatist',
        'plan_cta_dealer',
        'plan_cta_estate',
        'plan_cta_family_estate',
      ]) {
        expect(tester.widget<ElevatedButton>(find.byKey(Key(keyName))).onPressed, isNull);
      }

      completer.complete(const SubscriptionStatusSnapshot(
        stripeTier: 'free',
        unlimited: false,
        estateAccess: false,
        coinLimit: 10,
      ));
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('pricing_status_loading_banner')), findsNothing);
      for (final keyName in <String>[
        'plan_cta_pro',
        'plan_cta_numismatist',
        'plan_cta_dealer',
        'plan_cta_estate',
        'plan_cta_family_estate',
      ]) {
        expect(tester.widget<ElevatedButton>(find.byKey(Key(keyName))).onPressed, isNotNull);
      }

      await tester.ensureVisible(find.byKey(const Key('plan_cta_pro')));
      await tester.tap(find.byKey(const Key('plan_cta_pro')));
      await tester.pumpAndSettle();
      expect(launchedTiers, ['pro']);
    });

    testWidgets('T-UI-14 (Subscribe-gap 4d): Error and timeout keep all buttons disabled with Retry until status succeeds', (tester) async {
      tester.view.physicalSize = const Size(1280, 2200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      var attempt = 0;
      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: true,
            uidOverride: 'uid_error_retry',
            statusFetcherOverride: (_) {
              attempt++;
              if (attempt == 1) {
                return Future<SubscriptionStatusSnapshot?>.value(null);
              }
              if (attempt == 2) {
                return Completer<SubscriptionStatusSnapshot?>().future;
              }
              return Future<SubscriptionStatusSnapshot?>.value(
                const SubscriptionStatusSnapshot(stripeTier: 'free', coinLimit: 10),
              );
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      // 1st attempt returned null -> error banner + Retry shown, all CTAs disabled
      expect(find.byKey(const Key('pricing_status_error_banner')), findsOneWidget);
      expect(find.byKey(const Key('pricing_status_retry_btn')), findsOneWidget);
      for (final keyName in <String>[
        'plan_cta_pro',
        'plan_cta_numismatist',
        'plan_cta_dealer',
        'plan_cta_estate',
        'plan_cta_family_estate',
      ]) {
        expect(tester.widget<ElevatedButton>(find.byKey(Key(keyName))).onPressed, isNull);
      }

      // Tap Retry -> 2nd attempt hangs -> advance past 15s timeout -> still error + disabled
      await tester.tap(find.byKey(const Key('pricing_status_retry_btn')));
      await tester.pump();
      expect(find.byKey(const Key('pricing_status_loading_banner')), findsOneWidget);

      await tester.pump(const Duration(seconds: 15));
      await tester.pump();
      expect(find.byKey(const Key('pricing_status_error_banner')), findsOneWidget);
      expect(find.byKey(const Key('pricing_status_retry_btn')), findsOneWidget);
      for (final keyName in <String>[
        'plan_cta_pro',
        'plan_cta_numismatist',
        'plan_cta_dealer',
        'plan_cta_estate',
        'plan_cta_family_estate',
      ]) {
        expect(tester.widget<ElevatedButton>(find.byKey(Key(keyName))).onPressed, isNull);
      }

      // Tap Retry -> 3rd attempt resolves free -> buttons enable cleanly
      await tester.tap(find.byKey(const Key('pricing_status_retry_btn')));
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('pricing_status_error_banner')), findsNothing);
      for (final keyName in <String>[
        'plan_cta_pro',
        'plan_cta_numismatist',
        'plan_cta_dealer',
        'plan_cta_estate',
        'plan_cta_family_estate',
      ]) {
        expect(tester.widget<ElevatedButton>(find.byKey(Key(keyName))).onPressed, isNotNull);
      }
    });

    testWidgets('T-UI-15 (Founding Beta + sovereign): banner shown, Included with Founding Beta, Buy Lifetime disabled, Free card omits sign-in bullet', (tester) async {
      tester.view.physicalSize = const Size(1280, 2200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      HttpAuthClient.tokenProviderOverride = () async => 'test_jwt';
      HttpAuthClient.httpClientOverride = MockClient((req) async {
        if (req.url.path == '/api/stripe/subscription-status') {
          return http.Response(
            jsonEncode({
              'stripe_tier': 'sovereign',
              'founding_beta': true,
              'unlimited': true,
              'lifetime_family_estate': false,
              'estate_access': true,
            }),
            200,
          );
        }
        return http.Response('{}', 200);
      });

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: true,
            uidOverride: 'eIGZgYb49eeCR4Bsa5ABtHr94L63',
            nowUtcOverride: DateTime.utc(2026, 12, 1, 12),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(
        find.text('Founding Beta Member — Lifetime Access (including Estate) Included'),
        findsOneWidget,
      );
      expect(find.text('Included with Founding Beta'), findsNWidgets(5));
      for (final keyName in <String>[
        'plan_cta_pro',
        'plan_cta_numismatist',
        'plan_cta_dealer',
        'plan_cta_estate',
        'plan_cta_family_estate',
      ]) {
        expect(tester.widget<ElevatedButton>(find.byKey(Key(keyName))).onPressed, isNull);
      }
      expect(find.textContaining('10 items in your vault'), findsOneWidget);
      expect(
        find.textContaining('AI coin identification (3 deep dives / day, 1 invoice scan / day)'),
        findsOneWidget,
      );
      expect(find.textContaining('Sign in required to subscribe or buy Lifetime'), findsNothing);
    });

    testWidgets('T-UI-16 (Non-beta Lifetime): no beta banner, Included with Lifetime, Subscribe & Buy Lifetime disabled, Free card omits sign-in bullet', (tester) async {
      tester.view.physicalSize = const Size(1280, 2200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      HttpAuthClient.tokenProviderOverride = () async => 'test_jwt';
      HttpAuthClient.httpClientOverride = MockClient((req) async {
        if (req.url.path == '/api/stripe/subscription-status') {
          return http.Response(
            jsonEncode({
              'stripe_tier': 'family_estate',
              'founding_beta': false,
              'unlimited': true,
              'lifetime_family_estate': true,
              'estate_access': true,
            }),
            200,
          );
        }
        return http.Response('{}', 200);
      });

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: true,
            uidOverride: 'uid_nonbeta_lifetime',
            nowUtcOverride: DateTime.utc(2026, 12, 1, 12),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(
        find.text('Founding Beta Member — Lifetime Access (including Estate) Included'),
        findsNothing,
      );
      expect(find.text('Included with Founding Beta'), findsNothing);
      expect(find.text('Included with Lifetime'), findsNWidgets(5));
      for (final keyName in <String>[
        'plan_cta_pro',
        'plan_cta_numismatist',
        'plan_cta_dealer',
        'plan_cta_estate',
        'plan_cta_family_estate',
      ]) {
        expect(tester.widget<ElevatedButton>(find.byKey(Key(keyName))).onPressed, isNull);
      }
      expect(find.textContaining('Sign in required to subscribe or buy Lifetime'), findsNothing);
    });

    testWidgets('T-UI-17 (Negative non-beta sovereign): no beta banner, Buy Lifetime ENABLED, Subscribe enabled, Free card omits sign-in bullet', (tester) async {
      tester.view.physicalSize = const Size(1280, 2200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      HttpAuthClient.tokenProviderOverride = () async => 'test_jwt';
      HttpAuthClient.httpClientOverride = MockClient((req) async {
        if (req.url.path == '/api/stripe/subscription-status') {
          return http.Response(
            jsonEncode({
              'stripe_tier': 'sovereign',
              'founding_beta': false,
              'unlimited': true,
              'lifetime_family_estate': false,
              'estate_access': true,
            }),
            200,
          );
        }
        return http.Response('{}', 200);
      });

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: true,
            uidOverride: 'uid_nonbeta_sovereign',
            nowUtcOverride: DateTime.utc(2026, 12, 1, 12),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(
        find.text('Founding Beta Member — Lifetime Access (including Estate) Included'),
        findsNothing,
      );
      expect(find.text('Included with Founding Beta'), findsNothing);
      expect(find.text('Included with Lifetime'), findsNothing);
      for (final keyName in <String>[
        'plan_cta_pro',
        'plan_cta_numismatist',
        'plan_cta_dealer',
        'plan_cta_estate',
        'plan_cta_family_estate',
      ]) {
        expect(tester.widget<ElevatedButton>(find.byKey(Key(keyName))).onPressed, isNotNull);
      }
      expect(find.text(r'Buy Lifetime ($500)'), findsOneWidget);
      expect(find.textContaining('Sign in required to subscribe or buy Lifetime'), findsNothing);
    });

    testWidgets('T-UI-18 (Signed-out regression): Free card keeps Sign in required bullet', (tester) async {
      tester.view.physicalSize = const Size(1280, 2200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(
        MaterialApp(
          home: PublicInfoShell(
            targetRoute: '/pricing',
            isSignedInOverride: false,
            nowUtcOverride: DateTime.utc(2026, 12, 1, 12),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.textContaining('10 items in your vault'), findsOneWidget);
      expect(
        find.textContaining('AI coin identification (3 deep dives / day, 1 invoice scan / day)'),
        findsOneWidget,
      );
      expect(find.textContaining('Sign in required to subscribe or buy Lifetime'), findsOneWidget);
    });
  });
}
