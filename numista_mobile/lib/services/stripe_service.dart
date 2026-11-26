import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:http/http.dart' as http;
import '../constants.dart';
import 'http_auth_client.dart';

class CheckoutLaunchResult {
  final bool ok;
  final int statusCode;
  final String? checkoutUrl;
  final String? errorCode;
  final String? message;

  const CheckoutLaunchResult({
    required this.ok,
    required this.statusCode,
    this.checkoutUrl,
    this.errorCode,
    this.message,
  });
}

class SubscriptionStatusSnapshot {
  final String stripeTier;
  final String subscriptionStatus;
  final bool unlimited;
  final bool estateAccess;
  final bool lifetimeFamilyEstate;
  final int? coinLimit;

  const SubscriptionStatusSnapshot({
    required this.stripeTier,
    this.subscriptionStatus = 'active',
    this.unlimited = false,
    this.estateAccess = false,
    this.lifetimeFamilyEstate = false,
    this.coinLimit,
  });

  bool get hasPaidSubscription =>
      stripeTier != 'free' &&
      stripeTier != 'founding_beta' &&
      (subscriptionStatus == 'active' ||
          subscriptionStatus == 'trialing' ||
          subscriptionStatus == 'past_due');
}

class StripeService {
  static const String _baseUrl = kApiBaseUrl;

  /// Launches Stripe Checkout for Copper ($3.99/mo, $39.99/yr), Silver ($7.99/mo, $79.99/yr),
  /// Platinum ($9.99/mo, $99/yr), Gold ($15.99/mo, $150/yr), or Lifetime Family Estate ($500 one-time).
  /// Sends the Firebase Bearer token — the server reads user identity from the token.
  static Future<CheckoutLaunchResult> startCheckout({
    required String tier,
    String interval = 'month',
    String? promoCode,
    http.Client? client,
  }) async {
    try {
      final cleanPromo = (promoCode ?? '').trim();
      final payload = <String, dynamic>{
        'tier': tier,
        'interval': interval,
        if (cleanPromo.isNotEmpty) 'promo_code': cleanPromo,
      };
      final response = await HttpAuthClient.post(
        Uri.parse('$_baseUrl/api/stripe/create-checkout-session'),
        client: client,
        body: jsonEncode(payload),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final urlString = data is Map ? data['checkout_url'] as String? : null;
        if (urlString != null && urlString.isNotEmpty) {
          final uri = Uri.parse(urlString);
          if (await canLaunchUrl(uri)) {
            await launchUrl(uri, mode: LaunchMode.externalApplication);
            return CheckoutLaunchResult(
              ok: true,
              statusCode: 200,
              checkoutUrl: urlString,
            );
          }
        }
        return CheckoutLaunchResult(
          ok: false,
          statusCode: 200,
          checkoutUrl: urlString,
          message: 'Unable to open Stripe Checkout.',
        );
      }

      String? errorCode;
      String? msg;
      try {
        final decoded = jsonDecode(response.body);
        if (decoded is Map) {
          final detail = decoded['detail'];
          if (detail is Map) {
            errorCode = detail['error']?.toString();
            msg = detail['message']?.toString();
          } else if (detail != null) {
            msg = detail.toString();
          }
        }
      } catch (_) {}

      if (response.statusCode == 502) {
        msg = 'Checkout is not active yet.';
      } else if (msg == null || msg.isEmpty) {
        switch (errorCode) {
          case 'already_subscribed':
            msg = 'You already have a plan. To change it, cancel in Manage Billing; you can choose a new plan when the current period ends.';
            break;
          case 'already_lifetime':
            msg = 'You already own Lifetime Family Estate.';
            break;
          case 'promo_not_active':
            msg = 'This promo code is not active right now.';
            break;
          case 'promo_not_applicable_to_lifetime':
            msg = 'This promo code does not apply to Lifetime Family Estate.';
            break;
          case 'promo_invalid':
            msg = 'Invalid promo code.';
            break;
          case 'sign_in_required':
            msg = 'Please sign in to subscribe.';
            break;
          default:
            msg = 'Unable to start checkout (status ${response.statusCode}).';
        }
      }

      return CheckoutLaunchResult(
        ok: false,
        statusCode: response.statusCode,
        errorCode: errorCode,
        message: msg,
      );
    } catch (e) {
      debugPrint('[StripeService] Checkout session failed: $e');
      return const CheckoutLaunchResult(
        ok: false,
        statusCode: 0,
        message: 'Network error starting checkout. Please try again.',
      );
    }
  }

  static Future<bool> launchCheckoutSession({
    String? userEmail,
    required String tier,
    String interval = 'month',
    String? promoCode,
    http.Client? client,
  }) async {
    final res = await startCheckout(
      tier: tier,
      interval: interval,
      promoCode: promoCode,
      client: client,
    );
    return res.ok;
  }

  /// Queries current tier & entitlements via authenticated backend endpoint.
  static Future<SubscriptionStatusSnapshot?> fetchSubscriptionStatus({
    required String uid,
    http.Client? client,
  }) async {
    final id = uid.trim();
    if (id.isEmpty) return null;
    try {
      final response = await HttpAuthClient.get(
        Uri.parse('$_baseUrl/api/stripe/subscription-status')
            .replace(queryParameters: {'uid': id}),
        client: client,
      );
      if (response.statusCode != 200) return null;
      final data = jsonDecode(response.body);
      if (data is! Map) return null;
      final rawLimit = data['coin_limit'];
      return SubscriptionStatusSnapshot(
        stripeTier: (data['stripe_tier'] ?? 'free').toString(),
        subscriptionStatus: (data['subscription_status'] ?? 'active').toString(),
        unlimited: data['unlimited'] == true,
        estateAccess: data['estate_access'] == true,
        lifetimeFamilyEstate: data['lifetime_family_estate'] == true,
        coinLimit: rawLimit is num ? rawLimit.toInt() : null,
      );
    } catch (e) {
      debugPrint('[StripeService] Subscription status check failed: $e');
      return null;
    }
  }

  /// Launches Stripe Customer Portal for self-serve payment method and subscription management.
  /// The server reads the user from the Bearer token — the user_email query param is NOT sent
  /// to prevent the IDOR where any signed-in user could manage another user's billing.
  static Future<bool> launchCustomerPortal({http.Client? client}) async {
    try {
      final response = await HttpAuthClient.post(
        Uri.parse('$_baseUrl/api/stripe/create-customer-portal'),
        client: client,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final urlString = data['portal_url'] as String?;
        if (urlString != null && urlString.isNotEmpty) {
          final uri = Uri.parse(urlString);
          if (await canLaunchUrl(uri)) {
            await launchUrl(uri, mode: LaunchMode.externalApplication);
            return true;
          }
        }
      }
      return false;
    } catch (e) {
      debugPrint('[StripeService] Customer Portal launch failed: $e');
      return false;
    }
  }

  /// NET-827 v2.0.6: asks the server whether this signed-in account may open Estate.
  /// The server decides (Lifetime, AI-QC, Founding Beta from the Firebase Auth sign-up date
  /// or the server-set beta flag, staff allowlist). Fails closed: an empty uid sends nothing,
  /// and any error, non-200 reply, or missing / non-boolean `estate_access` returns false.
  static Future<bool> fetchEstateAccess({
    required String uid,
    http.Client? client,
  }) async {
    final id = uid.trim();
    if (id.isEmpty) return false;
    try {
      final response = await HttpAuthClient.get(
        Uri.parse('$_baseUrl/api/stripe/subscription-status')
            .replace(queryParameters: {'uid': id}),
        client: client,
      );
      if (response.statusCode != 200) return false;
      final data = jsonDecode(response.body);
      return data is Map && data['estate_access'] == true;
    } catch (e) {
      debugPrint('[StripeService] Estate access check failed: $e');
      return false;
    }
  }
}
