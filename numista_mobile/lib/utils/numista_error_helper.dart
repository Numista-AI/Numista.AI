import 'package:http/http.dart' as http;

/// Centralized error translation helper for Numista.AI.
/// Transforms raw exceptions (ClientException, XMLHttpRequest, etc.) into clean,
/// plain-English messages without technical jargon, URLs, or internal paths.
class NumistaErrorHelper {
  static String toUserFriendly(dynamic error, {int? statusCode, String? fallback}) {
    if (statusCode == 401) {
      return 'Your session expired or sign-in is required. Please sign in to continue.';
    }
    if (statusCode == 403) {
      return 'Access denied. You do not have permission to perform this action.';
    }
    if (statusCode != null && statusCode >= 500) {
      return 'Server is temporarily unavailable. Please try again in a few moments.';
    }

    if (error == null) {
      return fallback ?? 'An unexpected error occurred. Please try again.';
    }

    if (error is http.ClientException) {
      return 'Unable to connect to the server. Please check your internet connection and try again.';
    }

    final str = error.toString();

    if (str.contains('ClientException') ||
        str.contains('XMLHttpRequest') ||
        str.contains('Failed host lookup') ||
        str.contains('Connection refused') ||
        str.contains('NetworkError') ||
        str.contains('SocketException')) {
      return 'Unable to connect to the server. Please check your internet connection and try again.';
    }

    if (str.contains('401') || str.contains('unauthenticated') || str.contains('unauthorized')) {
      return 'Your session expired or sign-in is required. Please sign in to continue.';
    }

    if (str.contains('403') || str.contains('permission-denied') || str.contains('Forbidden')) {
      return 'Access denied. You do not have permission to perform this action.';
    }

    if (str.contains('500') || str.contains('502') || str.contains('503')) {
      return 'Server is temporarily unavailable. Please try again in a few moments.';
    }

    if (fallback != null && fallback.isNotEmpty) {
      return fallback;
    }

    final cleaned = str.replaceFirst(RegExp(r'^(Exception|Error):\s*'), '').trim();
    if (cleaned.contains('http://') || cleaned.contains('https://') || cleaned.contains('uri=')) {
      return 'Network connection issue. Please check your internet connection and try again.';
    }

    return cleaned.isNotEmpty ? cleaned : 'An unexpected error occurred. Please try again.';
  }
}
