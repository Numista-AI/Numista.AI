// error_message_service.dart
// ITEM 4 - Numista.AI Beta Sprint
//
// Dual-path error handling:
//   Path 1(a) - Friendly user-facing message (plain English, no stack traces)
//   Path 1(b) - Silent background telemetry via POST /api/telemetry/silent-error
//               Backend writes to Firestore beta_feedback via Admin SDK.
//               NEVER calls FirebaseFirestore directly - rules block client create.
//
// firebase_crashlytics is NOT in pubspec.yaml (desktop-web-only project).
// Crash-level events are sent via the same telemetry endpoint with isCrash=true.

import 'dart:async';
import 'package:flutter/foundation.dart' show kDebugMode;
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import '../constants.dart';

class ErrorMessageService {
  ErrorMessageService._();

  static const Map<String, String> _friendlyMessages = {
    'network':   "We couldn't reach the server. Please check your connection and try again.",
    'timeout':   'The request took too long. Please try again in a moment.',
    'permission':"You don't have permission to do that. Try signing out and back in.",
    'unauthenticated': 'Your session may have expired. Please sign in again.',
    '401':       'Your session may have expired. Please sign in again.',
    '403':       "You don't have permission to do that.",
    '404':       "We couldn't find that item. It may have been moved or deleted.",
    '429':       'Too many requests. Please wait a moment and try again.',
    '500':       "Something went wrong on our end. We've been notified.",
    '502':       'Our server had trouble connecting to a third-party service.',
    '503':       'A service we depend on is temporarily unavailable.',
    'socket':    'Connection failed. Please check your internet connection.',
    'format':    'We received an unexpected response. Our team has been notified.',
    'json':      'We received an unexpected response. Please try again.',
    'pcgs':      'The PCGS lookup is temporarily unavailable. Try again in a moment.',
    'firestore': 'We had trouble saving your data. Please try again.',
    'storage':   'We had trouble uploading your file. Please try again.',
  };

  static String friendlyMessage(Object error, {String? fallback}) {
    final lower = error.toString().toLowerCase();
    for (final entry in _friendlyMessages.entries) {
      if (lower.contains(entry.key)) return entry.value;
    }
    return fallback ?? 'Something went wrong. Please try again. If this continues, use Report Issue.';
  }

  static Future<String> handle({
    required Object error,
    StackTrace? stackTrace,
    required String context,
    String? userMessage,
    bool isCrash = false,
  }) async {
    final friendly = userMessage ?? friendlyMessage(error);

    // Path 1(b): silent background telemetry (also handles crash-level events
    // since firebase_crashlytics is not installed in this desktop-web project).
    unawaited(_sendSilentTelemetry(
      error: error,
      stackTrace: stackTrace,
      context: context,
      isCrash: isCrash,
    ));

    if (kDebugMode) {
      // ignore: avoid_print
      print('[ErrorMessageService] $context: $error\n$stackTrace');
    }

    return friendly;
  }

  /// Path 1(b): POST /api/telemetry/silent-error
  /// Backend writes to Firestore beta_feedback/{auto_id} via Admin SDK.
  /// Firestore rules block direct client writes to beta_feedback (create = false).
  static Future<void> _sendSilentTelemetry({
    required Object error,
    StackTrace? stackTrace,
    required String context,
    bool isCrash = false,
  }) async {
    try {
      final idToken = await FirebaseAuth.instance.currentUser?.getIdToken();
      if (idToken == null) return;

      final payload = '{"context":"$context","error_type":"${error.runtimeType}","has_stack":${stackTrace != null},"is_crash":$isCrash}';

      await http.post(
        Uri.parse('$kApiBaseUrl/api/telemetry/silent-error'),
        headers: {
          'Authorization': 'Bearer $idToken',
          'Content-Type': 'application/json',
        },
        body: payload,
      ).timeout(const Duration(seconds: 5));
    } catch (_) {
      // Telemetry must never crash the app.
    }
  }
}
