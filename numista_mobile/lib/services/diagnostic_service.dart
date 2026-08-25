// diagnostic_service.dart
//
// Collects safe device/session metadata for help ticket diagnostic packages.
// Deliberately minimal: collects only non-identifying technical data.
// Never reads or transmits coin financial data (cost, value, notes, etc.).
// User must explicitly opt-in and select which coins to share.

import 'package:flutter/foundation.dart';
import '../constants.dart';

class DiagnosticService {
  DiagnosticService._();

  /// Builds a diagnostic package for inclusion in a help ticket.
  ///
  /// [selectedCoinIds] — coin document IDs the user explicitly chose to share.
  /// [redactedFields] — additional fields the user wants withheld beyond ALWAYS_REDACTED.
  /// [errorLogs] — optional app-captured error strings (already sanitized by caller).
  /// [collectionStats] — non-financial aggregate stats (total coin count, etc.).
  ///
  /// Returns a map safe to send to POST /tickets as diagnostic_package.
  /// The server strips any coin values — this package carries only IDs and metadata.
  static Map<String, dynamic> buildPackage({
    required List<String> selectedCoinIds,
    List<String> redactedFields = const [],
    List<String> errorLogs = const [],
    Map<String, dynamic> collectionStats = const {},
  }) {
    final deviceInfo = _getDeviceInfo();

    // Sanitize error logs: strip anything that looks like an email or path containing @
    final sanitizedLogs = errorLogs
        .map((log) => _sanitizeLog(log))
        .where((log) => log.isNotEmpty)
        .take(50) // cap at 50 entries
        .toList();

    return {
      'app_version': kAppVersion,
      'platform': 'web',
      'device_info': deviceInfo,
      'error_logs': sanitizedLogs,
      'collection_stats': collectionStats,
      'redacted_fields': redactedFields,
      'selected_coin_ids': selectedCoinIds,
      // NOTE: no coin field values are included here.
      // The server re-fetches live coin data from users/{identifier}/coins/{id}
      // and applies its own redaction logic on every support view.
    };
  }

  static Map<String, String> _getDeviceInfo() {
    return {
      'platform': kIsWeb ? 'web' : defaultTargetPlatform.name,
      'flutter_target': kIsWeb ? 'web' : 'native',
    };
  }

  /// Strips email addresses and absolute Firestore paths from a log string.
  static String _sanitizeLog(String log) {
    // Remove anything that looks like an email (contains @ followed by domain)
    var sanitized = log.replaceAllMapped(
      RegExp(r'[\w.+-]+@[\w.-]+\.\w+'),
      (_) => '[email_redacted]',
    );
    // Remove Firestore paths that contain email/uid segments
    sanitized = sanitized.replaceAllMapped(
      RegExp(r'users/[^/\s]+/'),
      (_) => 'users/[uid_redacted]/',
    );
    return sanitized.trim();
  }
}
