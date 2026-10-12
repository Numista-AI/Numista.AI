import 'dart:convert';
import 'package:numista_ai/constants.dart';
import 'package:numista_ai/services/http_auth_client.dart';

enum UiVariant { classic, alt }

class UiVariantService {
  static UiVariant _current = UiVariant.classic;
  static UiVariant get current => _current;

  /// Fetch the variant from the server. Call once after sign-in.
  static Future<void> refresh() async {
    try {
      final response = await HttpAuthClient.get(
        Uri.parse('$kApiBaseUrl/api/user/ui_variant'),
      );
      if (response.statusCode == 200) {
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        final raw = body['variant'] as String? ?? 'classic';
        _current = raw == 'alt' ? UiVariant.alt : UiVariant.classic;
      }
    } catch (_) {
      _current = UiVariant.classic; // fail safe
    }
  }

  /// Reset on sign-out.
  static void reset() => _current = UiVariant.classic;
}
