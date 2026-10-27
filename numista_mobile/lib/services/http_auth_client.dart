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

  @visibleForTesting
  static Future<String?> Function()? tokenProviderOverride;
  @visibleForTesting
  static http.Client? httpClientOverride;

  /// Retrieve the current Firebase Auth ID Token.
  /// Force refresh if forceRefresh is true.
  static Future<String?> getIdToken({bool forceRefresh = false}) async {
    if (tokenProviderOverride != null) {
      return await tokenProviderOverride!();
    }
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

  static bool _canMakeRequest(Uri url) {
    if (tokenProviderOverride != null || httpClientOverride != null) return true;
    if (url.path.contains('spot_prices')) return true;
    try {
      final user = FirebaseAuth.instance.currentUser;
      return user != null;
    } catch (_) {
      return false;
    }
  }

  /// Send an authenticated GET request.
  static Future<http.Response> get(
    Uri url, {
    http.Client? client,
    Map<String, String>? headers,
    Duration timeout = const Duration(seconds: 30),
  }) async {
    if (!_canMakeRequest(url)) {
      debugPrint('[HttpAuthClient] Skipping unauthenticated GET to ${url.path}: No signed-in Firebase user.');
      return http.Response('{"detail": "Authentication token missing or invalid"}', 401);
    }
    final reqHeaders = await _buildHeaders(headers);
    final ownClient = client == null && httpClientOverride == null;
    final c = httpClientOverride ?? client ?? http.Client();
    try {
      return await c.get(url, headers: reqHeaders).timeout(timeout);
    } finally {
      if (ownClient) c.close();
    }
  }

  /// Send an authenticated POST request.
  static Future<http.Response> post(
    Uri url, {
    http.Client? client,
    Map<String, String>? headers,
    Object? body,
    Duration timeout = const Duration(seconds: 30),
  }) async {
    if (!_canMakeRequest(url)) {
      debugPrint('[HttpAuthClient] Skipping unauthenticated POST to ${url.path}: No signed-in Firebase user.');
      return http.Response('{"detail": "Authentication token missing or invalid"}', 401);
    }
    final reqHeaders = await _buildHeaders(headers);
    final ownClient = client == null && httpClientOverride == null;
    final c = httpClientOverride ?? client ?? http.Client();
    try {
      return await c.post(url, headers: reqHeaders, body: body).timeout(timeout);
    } finally {
      if (ownClient) c.close();
    }
  }

  /// Send an authenticated PUT request.
  static Future<http.Response> put(
    Uri url, {
    http.Client? client,
    Map<String, String>? headers,
    Object? body,
    Duration timeout = const Duration(seconds: 30),
  }) async {
    if (!_canMakeRequest(url)) {
      debugPrint('[HttpAuthClient] Skipping unauthenticated PUT to ${url.path}: No signed-in Firebase user.');
      return http.Response('{"detail": "Authentication token missing or invalid"}', 401);
    }
    final reqHeaders = await _buildHeaders(headers);
    final ownClient = client == null && httpClientOverride == null;
    final c = httpClientOverride ?? client ?? http.Client();
    try {
      return await c.put(url, headers: reqHeaders, body: body).timeout(timeout);
    } finally {
      if (ownClient) c.close();
    }
  }

  /// Send an authenticated DELETE request.
  static Future<http.Response> delete(
    Uri url, {
    http.Client? client,
    Map<String, String>? headers,
    Object? body,
    Duration timeout = const Duration(seconds: 30),
  }) async {
    if (!_canMakeRequest(url)) {
      debugPrint('[HttpAuthClient] Skipping unauthenticated DELETE to ${url.path}: No signed-in Firebase user.');
      return http.Response('{"detail": "Authentication token missing or invalid"}', 401);
    }
    final reqHeaders = await _buildHeaders(headers);
    final ownClient = client == null && httpClientOverride == null;
    final c = httpClientOverride ?? client ?? http.Client();
    try {
      return await c.delete(url, headers: reqHeaders, body: body).timeout(timeout);
    } finally {
      if (ownClient) c.close();
    }
  }

  /// Send an authenticated PATCH request.
  static Future<http.Response> patch(
    Uri url, {
    http.Client? client,
    Map<String, String>? headers,
    Object? body,
    Duration timeout = const Duration(seconds: 30),
  }) async {
    if (!_canMakeRequest(url)) {
      debugPrint('[HttpAuthClient] Skipping unauthenticated PATCH to ${url.path}: No signed-in Firebase user.');
      return http.Response('{"detail": "Authentication token missing or invalid"}', 401);
    }
    final reqHeaders = await _buildHeaders(headers);
    final ownClient = client == null && httpClientOverride == null;
    final c = httpClientOverride ?? client ?? http.Client();
    try {
      return await c.patch(url, headers: reqHeaders, body: body).timeout(timeout);
    } finally {
      if (ownClient) c.close();
    }
  }

  /// Send an authenticated multipart POST request.
  /// Use this instead of http.MultipartRequest for backend calls.
  static Future<http.StreamedResponse> multipartPost(
    Uri url, {
    required List<http.MultipartFile> files,
    Map<String, String>? fields,
    Map<String, String>? headers,
    Duration timeout = const Duration(seconds: 60),
  }) async {
    if (!_canMakeRequest(url)) {
      debugPrint('[HttpAuthClient] Skipping unauthenticated multipartPost to ${url.path}: No signed-in user.');
      return http.StreamedResponse(
        Stream.value(const <int>[]),
        401,
      );
    }
    final token = await getIdToken();
    final request = http.MultipartRequest('POST', url);
    if (token != null && token.isNotEmpty) {
      request.headers['Authorization'] = 'Bearer $token';
    }
    if (headers != null) request.headers.addAll(headers);
    if (fields != null) request.fields.addAll(fields);
    request.files.addAll(files);
    final c = httpClientOverride ?? http.Client();
    return await c.send(request).timeout(timeout);
  }
}
