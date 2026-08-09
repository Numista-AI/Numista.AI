// http_auth_client.dart
//
// Authenticated HTTP client helper for Numista.AI Flutter frontend.
// Automatically retrieves and attaches the Firebase ID Token (getIdToken())
// as a 'Authorization: Bearer <idToken>' header to all backend REST requests.

import 'package:flutter/foundation.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;

class HttpAuthClient {
  HttpAuthClient._();

  /// Retrieve the current Firebase Auth ID Token.
  /// Force refresh if forceRefresh is true.
  static Future<String?> getIdToken({bool forceRefresh = false}) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) {
        debugPrint('[HttpAuthClient] No signed-in Firebase user.');
        return null;
      }
      final token = await user.getIdToken(forceRefresh);
      return token;
    } catch (e) {
      debugPrint('[HttpAuthClient] Failed to retrieve ID token: $e');
      return null;
    }
  }

  /// Construct headers with attached Authorization Bearer token.
  static Future<Map<String, String>> _buildHeaders(Map<String, String>? customHeaders) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      if (customHeaders != null) ...customHeaders,
    };

    final token = await getIdToken();
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }

    return headers;
  }

  /// Send an authenticated GET request.
  static Future<http.Response> get(
    Uri url, {
    Map<String, String>? headers,
    Duration timeout = const Duration(seconds: 30),
  }) async {
    final reqHeaders = await _buildHeaders(headers);
    return http.get(url, headers: reqHeaders).timeout(timeout);
  }

  /// Send an authenticated POST request.
  static Future<http.Response> post(
    Uri url, {
    Map<String, String>? headers,
    Object? body,
    Duration timeout = const Duration(seconds: 30),
  }) async {
    final reqHeaders = await _buildHeaders(headers);
    return http.post(url, headers: reqHeaders, body: body).timeout(timeout);
  }

  /// Send an authenticated PUT request.
  static Future<http.Response> put(
    Uri url, {
    Map<String, String>? headers,
    Object? body,
    Duration timeout = const Duration(seconds: 30),
  }) async {
    final reqHeaders = await _buildHeaders(headers);
    return http.put(url, headers: reqHeaders, body: body).timeout(timeout);
  }

  /// Send an authenticated DELETE request.
  static Future<http.Response> delete(
    Uri url, {
    Map<String, String>? headers,
    Object? body,
    Duration timeout = const Duration(seconds: 30),
  }) async {
    final reqHeaders = await _buildHeaders(headers);
    return http.delete(url, headers: reqHeaders, body: body).timeout(timeout);
  }
}
