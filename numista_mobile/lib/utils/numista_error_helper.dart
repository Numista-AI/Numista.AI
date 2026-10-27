import 'package:firebase_core/firebase_core.dart';
import 'package:http/http.dart' as http;
import '../services/guest_seed_service.dart';

/// Centralized error translation helper for Numista.AI.
/// Transforms raw exceptions into plain-English messages without
/// technical jargon, URLs, or internal paths. Raw errors are printed
/// to the console only — no PII in user-facing strings.
class NumistaErrorHelper {
  // ── Public API ─────────────────────────────────────────────────────────────

  /// Returns a plain-English message for [error].
  /// [statusCode] takes precedence when provided (HTTP-level status).
  static String toUserFriendly(dynamic error, {int? statusCode, String? fallback}) {
    // 1. HTTP status code (explicit) takes priority.
    final statusMsg = _fromStatusCode(statusCode);
    if (statusMsg != null) return statusMsg;

    if (error == null) return fallback ?? _unknown;

    // 2. FirebaseException — direct Firestore/Auth writes produce these.
    if (error is FirebaseException) return _fromFirebase(error);

    // 3. http.ClientException typed object.
    if (error is http.ClientException) return _serverNoAnswer;

    // 4. String matching on toString().
    return _fromString(error.toString(), fallback: fallback);
  }

  /// Returns "Couldn't [action] — [base message]."
  /// Use this when you can name what the user was trying to do.
  ///
  /// Example: `toUserFriendlyWithContext(e, action: "save your 1921 coin")`
  /// → "Couldn't save your 1921 coin — no internet connection."
  static String toUserFriendlyWithContext(
    dynamic error, {
    required String action,
    int? statusCode,
  }) {
    if (GuestSeedService.isBrowseDemoMode) {
      return 'Demo mode — create a free account to save coins.';
    }
    final base = toUserFriendly(error, statusCode: statusCode);
    if (base.toLowerCase().contains('demo mode')) return base;
    return "Couldn't $action — $base";
  }

  // ── Private helpers ─────────────────────────────────────────────────────────

  static const _unknown      = 'An unexpected error occurred. Please try again.';
  static const _serverNoAnswer = 'The Numista.AI server didn\'t answer. Try again in a moment.';
  static const _offline      = 'No internet connection. Please check your network and try again.';
  static const _signIn       = 'Your session expired or sign-in is required. Please sign in to continue.';
  static const _permission   = 'Access denied. You do not have permission to perform this action.';
  static const _serverError  = 'Server is temporarily unavailable. Please try again in a few moments.';

  static String? _fromStatusCode(int? code) {
    if (code == null) return null;
    if (code == 401 || code == 403) {
      if (GuestSeedService.isBrowseDemoMode) {
        return 'Demo mode — create a free account to save coins.';
      }
      return code == 401 ? _signIn : _permission;
    }
    if (code == 404) return 'The requested resource was not found. Please try again.';
    if (code >= 500) return _serverError;
    return null;
  }

  static String _fromFirebase(FirebaseException e) {
    switch (e.code) {
      case 'unavailable':
      case 'deadline-exceeded':
        return _serverNoAnswer;
      case 'permission-denied':
      case 'unauthenticated':
        if (GuestSeedService.isBrowseDemoMode) {
          return 'Demo mode — create a free account to save coins.';
        }
        return _signIn;  // was _permission — for manual save, permission-denied means session expired
      case 'not-found':
        return 'The data wasn\'t found. It may have been deleted.';
      case 'already-exists':
        return 'This item already exists. Please refresh and try again.';
      case 'resource-exhausted':
        return 'Too many requests. Please wait a moment and try again.';
      default:
        return _unknown;
    }
  }

  static String _fromString(String str, {String? fallback}) {
    // CORS / web fetch failure — the server didn't answer (not offline).
    // On Flutter Web, a CORS block looks like XMLHttpRequest or
    // "Failed to fetch" — NOT an offline error.
    if (str.contains('XMLHttpRequest') ||
        str.contains('Failed to fetch') ||
        str.contains('NetworkError when attempting to fetch')) {
      return _serverNoAnswer;
    }

    // Genuine offline / DNS failure.
    if (str.contains('SocketException') ||
        str.contains('Failed host lookup') ||
        str.contains('Connection refused') ||
        str.contains('Connection reset') ||
        str.contains('Network is unreachable')) {
      return _offline;
    }

    // ClientException string (non-typed path).
    if (str.contains('ClientException')) return _serverNoAnswer;

    // Auth / permission strings.
    if (str.contains('401') ||
        str.contains('unauthenticated') ||
        str.contains('unauthorized') ||
        str.contains('permission-denied') ||
        str.contains('403') ||
        str.contains('Forbidden')) {
      if (GuestSeedService.isBrowseDemoMode) {
        return 'Demo mode — create a free account to save coins.';
      }
      if (str.contains('403') || str.contains('Forbidden')) {
        return _permission;
      }
      return _signIn;
    }

    // Server errors by status code string.
    if (str.contains('500') || str.contains('502') || str.contains('503') || str.contains('504')) {
      return _serverError;
    }

    // Fallback.
    if (fallback != null && fallback.isNotEmpty) return fallback;

    final cleaned = str.replaceFirst(RegExp(r'^(Exception|Error):\s*'), '').trim();
    if (cleaned.contains('http://') || cleaned.contains('https://') || cleaned.contains('uri=')) {
      return _serverNoAnswer;
    }
    return cleaned.isNotEmpty ? cleaned : _unknown;
  }
}
