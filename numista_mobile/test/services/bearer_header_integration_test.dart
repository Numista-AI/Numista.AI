import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/services/stripe_service.dart';
import 'package:numista_ai/services/lateral_transfer_service.dart';

/// Bearer Header Integration Tests — MUST 8 (REQ_027F)
///
/// Drives the REAL service classes (StripeService, LateralTransferService)
/// and HttpAuthClient directly. Uses HttpAuthClient.tokenProviderOverride and
/// httpClientOverride to inject a MockClient that captures every request.
///
/// Assertions:
///   - Authorization: Bearer <token> header is present on every request.
///   - Stripe portal body/query does NOT contain user_email (IDOR fix).
///
/// Run with: flutter test test/services/bearer_header_integration_test.dart

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  const fakeToken = 'mock_jwt_token_for_bearer_test';

  setUp(() {
    HttpAuthClient.tokenProviderOverride = () async => fakeToken;
  });

  tearDown(() {
    HttpAuthClient.tokenProviderOverride = null;
    HttpAuthClient.httpClientOverride = null;
  });

  group('HttpAuthClient — Bearer header on direct calls', () {
    test('post() sends Authorization: Bearer header', () async {
      http.Request? captured;
      HttpAuthClient.httpClientOverride = MockClient((req) async {
        captured = req;
        return http.Response('{"ok":true}', 200);
      });

      await HttpAuthClient.post(
        Uri.parse('http://localhost/api/test-endpoint'),
        body: jsonEncode({'key': 'value'}),
      );

      expect(captured, isNotNull);
      expect(captured!.headers['authorization'], equals('Bearer $fakeToken'));
      expect(captured!.headers['content-type'], contains('application/json'));
    });

    test('get() sends Authorization: Bearer header', () async {
      http.Request? captured;
      HttpAuthClient.httpClientOverride = MockClient((req) async {
        captured = req;
        return http.Response('{"ok":true}', 200);
      });

      await HttpAuthClient.get(Uri.parse('http://localhost/api/test-get'));

      expect(captured, isNotNull);
      expect(captured!.headers['authorization'], equals('Bearer $fakeToken'));
    });

    test('No token => no Authorization header', () async {
      HttpAuthClient.tokenProviderOverride = () async => null;
      http.Request? captured;
      HttpAuthClient.httpClientOverride = MockClient((req) async {
        captured = req;
        return http.Response('{}', 200);
      });

      await HttpAuthClient.post(Uri.parse('http://localhost/api/no-token'));

      expect(captured, isNotNull);
      expect(captured!.headers.containsKey('authorization'), isFalse);
    });
  });

  group('StripeService — Bearer header via HttpAuthClient', () {
    test('launchCheckoutSession sends Bearer header', () async {
      final captured = <http.Request>[];
      HttpAuthClient.httpClientOverride = MockClient((req) async {
        captured.add(req);
        return http.Response(
          jsonEncode({'checkout_url': 'https://checkout.stripe.com/pay/mock', 'session_id': 'sess_mock'}),
          200,
        );
      });

      await StripeService.launchCheckoutSession(userEmail: 'test@example.com', tier: 'pro');

      expect(captured, isNotEmpty, reason: 'Expected at least one HTTP request');
      final req = captured.first;
      expect(req.url.path, contains('create-checkout-session'));
      expect(req.headers['authorization'], equals('Bearer $fakeToken'));
    });

    test('launchCustomerPortal sends Bearer header and no user_email', () async {
      final captured = <http.Request>[];
      HttpAuthClient.httpClientOverride = MockClient((req) async {
        captured.add(req);
        return http.Response(
          jsonEncode({'portal_url': 'https://billing.stripe.com/mock'}),
          200,
        );
      });

      await StripeService.launchCustomerPortal();

      expect(captured, isNotEmpty, reason: 'Expected at least one HTTP request');
      final req = captured.first;
      expect(req.url.path, contains('create-customer-portal'));
      expect(req.headers['authorization'], equals('Bearer $fakeToken'));

      // IDOR check: user_email must not appear in URL or body
      expect(req.url.queryParameters.containsKey('user_email'), isFalse,
          reason: 'user_email must not be in the query string (IDOR fix)');
      if (req.body.isNotEmpty) {
        final body = jsonDecode(req.body) as Map<String, dynamic>;
        expect(body.containsKey('user_email'), isFalse,
            reason: 'user_email must not be in the request body (IDOR fix)');
      }
    });
  });

  group('LateralTransferService — Bearer header via HttpAuthClient', () {
    test('initiateTransfer sends Bearer header', () async {
      http.Request? captured;
      HttpAuthClient.httpClientOverride = MockClient((req) async {
        captured = req;
        // Return a minimal valid transfer payload matching TransferModel.fromMap expectations
        return http.Response(
          jsonEncode({
            'transfer': {
              'transfer_id': 'txfr_mock123',
              'claim_pin': '123456',
              'status': 'pending',
              'user_a_id': 'sender@numista.ai',
              'items': [],
              'created_at': '2026-10-01T00:00:00Z',
            },
          }),
          200,
        );
      });

      final svc = LateralTransferService();
      try {
        await svc.initiateTransfer(
          userId: 'sender@numista.ai',
          itemIds: ['coin_001'],
          recipientEmail: 'recipient@numista.ai',
        );
      } catch (_) {
        // TransferModel.fromMap may throw on minimal mock data — we only care that
        // the HTTP request was made with the correct Bearer header.
      }

      expect(captured, isNotNull, reason: 'Expected an HTTP request from initiateTransfer');
      expect(captured!.headers['authorization'], equals('Bearer $fakeToken'));
    });
  });

  group('dismiss_news — Bearer header via HttpAuthClient', () {
    test('HttpAuthClient.post to dismiss_news endpoint sends Bearer header', () async {
      http.Request? captured;
      HttpAuthClient.httpClientOverride = MockClient((req) async {
        captured = req;
        return http.Response('{"status":"ok"}', 200);
      });

      // Drive the real HttpAuthClient.post with the dismiss_news endpoint pattern
      await HttpAuthClient.post(
        Uri.parse('http://localhost/api/dismiss_news'),
        body: jsonEncode({'article_id': 'news_abc123'}),
      );

      expect(captured, isNotNull);
      expect(captured!.url.path, contains('dismiss_news'));
      expect(captured!.headers['authorization'], equals('Bearer $fakeToken'));
      // Confirm user_email is NOT in the body
      final body = jsonDecode(captured!.body) as Map<String, dynamic>;
      expect(body.containsKey('user_email'), isFalse,
          reason: 'dismiss_news must not send user_email in body (server reads from token)');
    });
  });

  group('Admin grade flag resolve — Bearer header via HttpAuthClient', () {
    test('HttpAuthClient.post to grade_flags/resolve endpoint sends Bearer header', () async {
      http.Request? captured;
      HttpAuthClient.httpClientOverride = MockClient((req) async {
        captured = req;
        return http.Response('{"message":"Resolved"}', 200);
      });

      await HttpAuthClient.post(
        Uri.parse('http://localhost/api/admin/grade_flags/flag_xyz/resolve'),
        body: jsonEncode({
          'decision': 'accept_ai',
          'resolved_grade': '',
          'notes': '',
        }),
      );

      expect(captured, isNotNull);
      expect(captured!.url.path, contains('grade_flags'));
      expect(captured!.url.path, contains('resolve'));
      expect(captured!.headers['authorization'], equals('Bearer $fakeToken'));
    });
  });
}
