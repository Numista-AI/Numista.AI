import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:http/http.dart' as http;
import 'http_auth_client.dart';

class StripeService {
  static const String _baseUrl = 'https://numista-backend-568985927038.us-central1.run.app';

  /// Launches Stripe Checkout for Pro ($4.99/mo) or Estate ($29/yr) subscription tiers.
  /// Sends the Firebase Bearer token — the server reads user identity from the token.
  static Future<bool> launchCheckoutSession({
    required String userEmail,
    required String tier,
    http.Client? client,
  }) async {
    try {
      final response = await HttpAuthClient.post(
        Uri.parse('$_baseUrl/api/stripe/create-checkout-session'),
        client: client,
        body: jsonEncode({
          'tier': tier,
          // user_email kept for backwards compat — server should prefer token
          'user_email': userEmail,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final urlString = data['checkout_url'] as String?;
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
      debugPrint('[StripeService] Checkout session failed: $e');
      return false;
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
}
