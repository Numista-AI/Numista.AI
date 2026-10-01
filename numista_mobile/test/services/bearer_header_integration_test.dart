import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/services/stripe_service.dart';
import 'package:numista_ai/services/grade_flag_service.dart';
import 'package:numista_ai/services/news_service.dart';
import 'package:numista_ai/services/transfer_service.dart';

void main() {
  group('Bearer Header Integration Tests', () {
    const fakeToken = 'mock_jwt_token_123';
    late MockClient mockClient;
    List<http.Request> capturedRequests = [];

    setUp(() {
      capturedRequests.clear();
      
      HttpAuthClient.tokenProviderOverride = () async => fakeToken;
      
      mockClient = MockClient((request) async {
        capturedRequests.add(request as http.Request);
        return http.Response(jsonEncode({'success': true, 'checkout_url': 'http://checkout', 'portal_url': 'http://portal', 'status': 'ok'}), 200);
      });
      HttpAuthClient.httpClientOverride = mockClient;
    });

    tearDown(() {
      HttpAuthClient.tokenProviderOverride = null;
      HttpAuthClient.httpClientOverride = null;
    });

    test('StripeService checkout sends Bearer header', () async {
      await StripeService.launchCheckoutSession(userEmail: 'test@example.com', tier: 'pro');
      
      expect(capturedRequests, isNotEmpty);
      final req = capturedRequests.first;
      expect(req.url.path, contains('create-checkout-session'));
      expect(req.headers['authorization'], equals('Bearer $fakeToken'));
    });

    test('StripeService portal sends Bearer header and no user_email', () async {
      await StripeService.launchCustomerPortal();
      
      expect(capturedRequests, isNotEmpty);
      final req = capturedRequests.first;
      expect(req.url.path, contains('create-customer-portal'));
      expect(req.headers['authorization'], equals('Bearer $fakeToken'));
      
      // Ensure user_email is not in body or query params
      if (req.body.isNotEmpty) {
        final body = jsonDecode(req.body);
        expect(body.containsKey('user_email'), isFalse);
      }
      expect(req.url.queryParameters.containsKey('user_email'), isFalse);
    });

    test('admin flag resolve sends Bearer header', () async {
      await GradeFlagService.resolveFlag('flag123', 'accept_ai', 'ok');
      
      expect(capturedRequests, isNotEmpty);
      final req = capturedRequests.first;
      expect(req.url.path, contains('/api/admin/grade-flags/flag123/resolve'));
      expect(req.headers['authorization'], equals('Bearer $fakeToken'));
    });

    test('lateral transfer init sends Bearer header', () async {
      await TransferService.initiateTransfer('123', 'coin', 'r@m.com');
      
      expect(capturedRequests, isNotEmpty);
      final req = capturedRequests.first;
      expect(req.url.path, contains('/api/transfers/init'));
      expect(req.headers['authorization'], equals('Bearer $fakeToken'));
    });

    test('dismiss news sends Bearer header', () async {
      await NewsService.dismissNewsItem('news123');
      
      expect(capturedRequests, isNotEmpty);
      final req = capturedRequests.first;
      expect(req.url.path, contains('/api/news/dismiss'));
      expect(req.headers['authorization'], equals('Bearer $fakeToken'));
    });
  });
}
