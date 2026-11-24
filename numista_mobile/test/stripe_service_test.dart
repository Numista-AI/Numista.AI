import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/services/stripe_service.dart';

void main() {
  tearDown(() {
    HttpAuthClient.tokenProviderOverride = null;
    HttpAuthClient.httpClientOverride = null;
  });

  test('T-DART-1: launchCheckoutSession sends tier + interval and no user_email', () async {
    Map<String, dynamic>? capturedBody;
    http.Request? capturedRequest;
    HttpAuthClient.tokenProviderOverride = () async => 'fake-token';
    final mockClient = MockClient((request) async {
      capturedRequest = request;
      capturedBody = jsonDecode(request.body) as Map<String, dynamic>;
      return http.Response(jsonEncode({'checkout_url': ''}), 200);
    });

    await StripeService.launchCheckoutSession(
      userEmail: 'ignored@example.com',
      tier: 'estate',
      interval: 'year',
      client: mockClient,
    );

    expect(capturedRequest, isNotNull);
    expect(capturedRequest!.method, 'POST');
    expect(capturedRequest!.url.path, '/api/stripe/create-checkout-session');
    expect(capturedRequest!.headers['Authorization'], 'Bearer fake-token');
    expect(capturedRequest!.headers['Content-Type'], contains('application/json'));
    expect(capturedBody, {'tier': 'estate', 'interval': 'year'});
    expect(capturedBody!.containsKey('user_email'), isFalse);
  });

  test('T-DART-2: launchCheckoutSession returns false on 403 sign_in_required', () async {
    HttpAuthClient.tokenProviderOverride = () async => 'fake-token';
    final mockClient = MockClient((request) async {
      return http.Response(
        jsonEncode({'detail': {'error': 'sign_in_required'}}),
        403,
      );
    });

    final ok = await StripeService.launchCheckoutSession(
      userEmail: 'guest@example.com',
      tier: 'pro',
      client: mockClient,
    );

    expect(ok, isFalse);
  });

  test('T-DART-3: startCheckout sends promo_code and parses 409/502 error details; fetchSubscriptionStatus GETs exact URL', () async {
    http.Request? capturedCheckout;
    HttpAuthClient.tokenProviderOverride = () async => 'fake-token-3';

    final client = MockClient((request) async {
      capturedCheckout = request;
      if (request.url.path == '/api/stripe/subscription-status') {
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
      return http.Response(
        jsonEncode({
          'detail': {
            'error': 'already_subscribed',
            'message': 'You already have a plan. Cancel in Manage Billing.',
          },
        }),
        409,
      );
    });

    final snap = await StripeService.fetchSubscriptionStatus(uid: ' uid_sub_1 ', client: client);
    expect(snap, isNotNull);
    expect(snap!.stripeTier, 'free');
    expect(snap.coinLimit, 10);
    expect(snap.estateAccess, isFalse);
    expect(capturedCheckout!.method, 'GET');
    expect(capturedCheckout!.url.path, '/api/stripe/subscription-status');
    expect(capturedCheckout!.url.queryParameters, {'uid': 'uid_sub_1'});
    expect(capturedCheckout!.headers['Authorization'], 'Bearer fake-token-3');

    final res409 = await StripeService.startCheckout(
      tier: 'pro',
      interval: 'month',
      promoCode: ' CHRISTMAS2026 ',
      client: client,
    );
    expect(res409.ok, isFalse);
    expect(res409.statusCode, 409);
    expect(res409.errorCode, 'already_subscribed');
    expect(jsonDecode(capturedCheckout!.body), {
      'tier': 'pro',
      'interval': 'month',
      'promo_code': 'CHRISTMAS2026',
    });

    final client502 = MockClient((_) async => http.Response('{"detail":"Stripe is not configured"}', 502));
    final res502 = await StripeService.startCheckout(tier: 'pro', client: client502);
    expect(res502.ok, isFalse);
    expect(res502.statusCode, 502);
    expect(res502.message, 'Checkout is not active yet.');
  });

  test('T-DART-4: launchCustomerPortal POSTs exact endpoint with Bearer token and fails closed on 404', () async {
    http.Request? req;
    HttpAuthClient.tokenProviderOverride = () async => 'portal-tok';
    final mock404 = MockClient((r) async {
      req = r;
      return http.Response('{"detail":{"error":"no_billing_account"}}', 404);
    });

    final ok = await StripeService.launchCustomerPortal(client: mock404);
    expect(ok, isFalse);
    expect(req!.method, 'POST');
    expect(req!.url.path, '/api/stripe/create-customer-portal');
    expect(req!.headers['Authorization'], 'Bearer portal-tok');
  });
}
