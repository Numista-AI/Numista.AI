import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:numista_ai/constants.dart';
import 'package:numista_ai/screens/estate_planning_screen.dart';
import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/services/stripe_service.dart';

void main() {
  tearDown(() {
    HttpAuthClient.tokenProviderOverride = null;
    HttpAuthClient.httpClientOverride = null;
  });

  group('fetchEstateAccess request (RSI P5)', () {
    test('T-EST-D1: exact URL, method, Bearer token, query; true only on estate_access == true', () async {
      final captured = <http.Request>[];
      HttpAuthClient.tokenProviderOverride = () async => 'fake-token';
      final client = MockClient((req) async {
        captured.add(req);
        return http.Response(jsonEncode({'estate_access': true, 'stripe_tier': 'founding_beta'}), 200);
      });
      final ok = await StripeService.fetchEstateAccess(uid: ' uid_F ', client: client);
      expect(ok, isTrue);
      expect(captured, hasLength(1));
      final r = captured.single;
      expect(r.method, 'GET');
      expect(r.url.toString(), '$kApiBaseUrl/api/stripe/subscription-status?uid=uid_F');
      expect(r.url.path, '/api/stripe/subscription-status');
      expect(r.url.queryParameters, {'uid': 'uid_F'});
      expect(r.headers['Authorization'], 'Bearer fake-token');
      expect(r.body, isEmpty);
    });

    test('T-EST-D2: empty or blank uid sends no request and returns false', () async {
      var calls = 0;
      HttpAuthClient.tokenProviderOverride = () async => 'fake-token';
      final client = MockClient((req) async {
        calls++;
        return http.Response(jsonEncode({'estate_access': true}), 200);
      });
      expect(await StripeService.fetchEstateAccess(uid: '', client: client), isFalse);
      expect(await StripeService.fetchEstateAccess(uid: '   ', client: client), isFalse);
      expect(calls, 0);
    });

    test('T-EST-D3: no token -> no Authorization header; 401 -> false', () async {
      http.Request? seen;
      HttpAuthClient.tokenProviderOverride = () async => null;
      final client = MockClient((req) async {
        seen = req;
        return http.Response('{"detail":"Authentication token missing or invalid"}', 401);
      });
      expect(await StripeService.fetchEstateAccess(uid: 'uid_F', client: client), isFalse);
      expect(seen, isNotNull);
      expect(seen!.headers.containsKey('Authorization'), isFalse);
    });

    test('T-EST-D4: fail closed on 503, 500, non-bool, missing key, bad JSON, thrown error', () async {
      HttpAuthClient.tokenProviderOverride = () async => 'fake-token';
      final replies = <http.Response>[
        http.Response('{"detail":"Account check unavailable, try again"}', 503),
        http.Response('{"detail":"x"}', 500),
        http.Response(jsonEncode({'estate_access': 'true'}), 200),
        http.Response(jsonEncode({'estate_access': 1}), 200),
        http.Response(jsonEncode({'stripe_tier': 'founding_beta'}), 200),
        http.Response('not json', 200),
        http.Response(jsonEncode([true]), 200),
      ];
      for (final reply in replies) {
        final client = MockClient((_) async => reply);
        expect(await StripeService.fetchEstateAccess(uid: 'uid_F', client: client), isFalse,
            reason: 'status ${reply.statusCode} body ${reply.body}');
      }
      final throwing = MockClient((_) async => throw http.ClientException('offline'));
      expect(await StripeService.fetchEstateAccess(uid: 'uid_F', client: throwing), isFalse);
    });
  });

  group('estateGateView (pure)', () {
    test('T-EST-D5: Founding Beta (server true) opens Estate even on a Free doc', () {
      expect(estateGateView(tierLoaded: true, serverChecked: true, serverAccess: true, localAccess: false),
          EstateGateView.open);
    });
    test('T-EST-D6: post-cutoff Free / Gold non-beta (server false, no local) is locked', () {
      expect(estateGateView(tierLoaded: true, serverChecked: true, serverAccess: false, localAccess: false),
          EstateGateView.locked);
    });
    test('T-EST-D7: Lifetime / staff (local true) still open when the server says false', () {
      expect(estateGateView(tierLoaded: true, serverChecked: true, serverAccess: false, localAccess: true),
          EstateGateView.open);
    });
    test('T-EST-D8: waiting states never open', () {
      expect(estateGateView(tierLoaded: false, serverChecked: true, serverAccess: true, localAccess: false),
          EstateGateView.loading);
      expect(estateGateView(tierLoaded: true, serverChecked: false, serverAccess: false, localAccess: false),
          EstateGateView.loading);
    });
  });

  group('EstatePlanningScreen wiring', () {
    Future<void> pumpScreen(WidgetTester tester, Map<String, dynamic> doc,
        Future<bool> Function(String) fetcher,
        {String email = 'user@example.com', String uid = 'uid_user'}) async {
      final controller = StreamController<Map<String, dynamic>>.broadcast();
      addTearDown(controller.close);
      await tester.pumpWidget(MaterialApp(
        home: EstatePlanningScreen(
          tierStreamOverride: controller.stream,
          userEmailOverride: email,
          userUidOverride: uid,
          estateAccessFetcherOverride: fetcher,
        ),
      ));
      controller.add(doc);
      await tester.pump();
      await tester.pump();
    }

    testWidgets('T-EST-D9: asks the server once with the Firebase uid; server false -> Premium gate',
        (tester) async {
      final asked = <String>[];
      await pumpScreen(tester, {'stripe_tier': 'free'}, (u) async { asked.add(u); return false; });
      expect(asked, ['uid_user']);
      expect(find.text('Premium Feature'), findsOneWidget);
      expect(find.byType(TabBarView), findsNothing);
    });

    testWidgets('T-EST-D10: Gold non-beta doc + server false -> Premium gate', (tester) async {
      await pumpScreen(tester, {'stripe_tier': 'estate'}, (_) async => false);
      expect(find.text('Premium Feature'), findsOneWidget);
    });

    testWidgets('T-EST-D11: client-set beta fields in Firestore are ignored', (tester) async {
      await pumpScreen(tester, {
        'stripe_tier': 'free', 'founding_beta': true, 'is_beta': true,
        'estate_access': true, 'creation_timestamp': 0, 'power_user': true,
      }, (_) async => false);
      expect(find.text('Premium Feature'), findsOneWidget);
      expect(find.byType(TabBarView), findsNothing);
    });

    testWidgets('T-EST-D12: server error fails closed', (tester) async {
      await pumpScreen(tester, {'stripe_tier': 'free'}, (_) async => throw Exception('503'));
      expect(find.text('Premium Feature'), findsOneWidget);
    });

    testWidgets('T-EST-D13: server never answers -> spinner, never the Estate tabs', (tester) async {
      final never = Completer<bool>();
      await pumpScreen(tester, {'stripe_tier': 'free'}, (_) => never.future);
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.byType(TabBarView), findsNothing);
      expect(find.text('Premium Feature'), findsNothing);
    });

    testWidgets('T-EST-D14: empty uid -> server not asked, Premium gate', (tester) async {
      var asked = 0;
      await pumpScreen(tester, {'stripe_tier': 'free'}, (_) async { asked++; return true; }, uid: '');
      expect(asked, 0);
      expect(find.text('Premium Feature'), findsOneWidget);
    });
  });

  group('C5 local rule D-1a (beta_tester / is_ai_qc_account)', () {
    test('T-EST-D15: server-only beta_tester == true opens Estate locally', () {
      expect(
        hasEstateAccess(subscriptionTier: 'free', isLifetime: false, isBetaTester: true),
        isTrue,
      );
      expect(
        estateGateView(tierLoaded: true, serverChecked: true, serverAccess: false, localAccess: true),
        EstateGateView.open,
      );
    });

    test('T-EST-D16: server-only is_ai_qc_account == true opens Estate locally', () {
      expect(
        hasEstateAccess(subscriptionTier: 'free', isLifetime: false, isAiQcAccount: true),
        isTrue,
      );
      expect(
        estateGateView(tierLoaded: true, serverChecked: true, serverAccess: false, localAccess: true),
        EstateGateView.open,
      );
    });

    testWidgets('T-EST-D17: negative — non-flag / non-bool doc stays locked when server says false',
        (tester) async {
      expect(
        hasEstateAccess(
          subscriptionTier: 'free',
          isLifetime: false,
          isBetaTester: false,
          isAiQcAccount: false,
        ),
        isFalse,
      );
      final controller = StreamController<Map<String, dynamic>>.broadcast();
      addTearDown(controller.close);
      await tester.pumpWidget(MaterialApp(
        home: EstatePlanningScreen(
          tierStreamOverride: controller.stream,
          userEmailOverride: 'user@example.com',
          userUidOverride: 'uid_user',
          estateAccessFetcherOverride: (_) async => false,
        ),
      ));
      controller.add({
        'stripe_tier': 'free',
        'beta_tester': 'true',
        'is_ai_qc_account': 1,
      });
      await tester.pump();
      await tester.pump();
      expect(find.text('Premium Feature'), findsOneWidget);
      expect(find.byType(TabBarView), findsNothing);
    });
  });
}
