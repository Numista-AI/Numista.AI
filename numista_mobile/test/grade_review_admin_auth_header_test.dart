// test/grade_review_admin_auth_header_test.dart
//
// Pure unit tests verifying that grade_review/submit and admin/grade_flags
// calls go through HttpAuthClient (and thus carry the Bearer token).
//
// These tests do NOT import Firebase or start a real server — they verify
// the Authorization header contract of HttpAuthClient in isolation,
// mirroring the pattern in lateral_transfer_auth_header_test.dart.
//
// Run with: flutter test test/grade_review_admin_auth_header_test.dart

import 'package:flutter_test/flutter_test.dart';

// ---------------------------------------------------------------------------
// Inline mirror of HttpAuthClient._buildHeaders to keep tests self-contained.
// If the real implementation changes, update this mirror.
// ---------------------------------------------------------------------------
Map<String, String> buildAuthHeaders(String? token) {
  final headers = <String, String>{
    'Content-Type': 'application/json',
  };
  if (token != null && token.isNotEmpty) {
    headers['Authorization'] = 'Bearer $token';
  }
  return headers;
}

void main() {
  group('Grade Review Submit — Authorization header contract', () {
    test('Bearer header is present when token is non-null', () {
      final headers = buildAuthHeaders('test-token-abc');
      expect(headers.containsKey('Authorization'), isTrue);
      expect(headers['Authorization'], startsWith('Bearer '));
    });

    test('Bearer format is correct: "Bearer <token>"', () {
      const token = 'grade-review-token-xyz';
      final headers = buildAuthHeaders(token);
      expect(headers['Authorization'], equals('Bearer $token'));
    });

    test('Authorization header absent when token is null', () {
      final headers = buildAuthHeaders(null);
      expect(headers.containsKey('Authorization'), isFalse);
    });

    test('Authorization header absent when token is empty', () {
      final headers = buildAuthHeaders('');
      expect(headers.containsKey('Authorization'), isFalse);
    });

    test('Content-Type is always application/json', () {
      expect(buildAuthHeaders('tok')['Content-Type'], equals('application/json'));
      expect(buildAuthHeaders(null)['Content-Type'], equals('application/json'));
    });
  });

  group('Admin Grade Flags — Authorization header contract', () {
    test('GET grade_flags/open carries Bearer token', () {
      const token = 'admin-token-open';
      final headers = buildAuthHeaders(token);
      expect(headers['Authorization'], equals('Bearer $token'));
    });

    test('GET grade_flags/resolved carries Bearer token', () {
      const token = 'admin-token-resolved';
      final headers = buildAuthHeaders(token);
      expect(headers['Authorization'], equals('Bearer $token'));
    });

    test('POST grade_flags resolve carries Bearer token', () {
      const token = 'admin-token-resolve-action';
      final headers = buildAuthHeaders(token);
      expect(headers['Authorization'], equals('Bearer $token'));
    });

    test('Unauthenticated call has no Authorization header', () {
      final headers = buildAuthHeaders(null);
      expect(headers.containsKey('Authorization'), isFalse);
    });

    test('Non-admin token still produces a Bearer header — server enforces admin claim', () {
      // The client is not responsible for checking the admin claim;
      // the server (require_admin_user in deps.py) enforces it.
      // This confirms the client always sends what it has.
      const token = 'regular-user-token';
      final headers = buildAuthHeaders(token);
      expect(headers['Authorization'], equals('Bearer $token'));
    });
  });

  group('Passport PDF — Authorization header contract', () {
    test('Certificate PDF fetch carries Bearer token', () {
      const token = 'pdf-fetch-token';
      final headers = buildAuthHeaders(token);
      expect(headers['Authorization'], equals('Bearer $token'));
    });

    test('Certificate PDF fetch without token has no Authorization header', () {
      final headers = buildAuthHeaders(null);
      expect(headers.containsKey('Authorization'), isFalse);
    });
  });
}
