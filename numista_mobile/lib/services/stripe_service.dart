import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';

class StripeService {
  static const String _baseUrl = 'https://numista-backend-568985927038.us-central1.run.app';

  /// Launches Stripe Checkout for Pro ($4.99/mo) or Estate ($29/yr) subscription tiers.
  static Future<bool> launchCheckoutSession({
    required String userEmail,
    required String tier,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/stripe/create-checkout-session'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_email': userEmail,
          'tier': tier,
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
  static Future<bool> launchCustomerPortal({required String userEmail}) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/api/stripe/create-customer-portal?user_email=${Uri.encodeComponent(userEmail)}'),
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
