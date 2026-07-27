import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:web/web.dart' as web;
import 'auth_service.dart';

/// Handles exporting the user's Firestore collection into a schemaVersion: 1 JSON bundle
/// or a companion CSV spreadsheet for legal estate planning and offline backup.
class BackupExportService {
  BackupExportService._();

  /// Generates schemaVersion: 1 JSON export string.
  static Future<Map<String, dynamic>> generateExportPayload() async {
    final user = FirebaseAuth.instance.currentUser;
    final email = user?.email ?? 'guest@numista.ai';

    List<Map<String, dynamic>> coins = [];

    if (!AuthService.isGuest && user?.email != null) {
      try {
        final snap = await FirebaseFirestore.instance
            .collection(AuthService.coinsPath)
            .get();
        for (final doc in snap.docs) {
          final data = doc.data();
          coins.add({'_id': doc.id, ...data});
        }
      } catch (e) {
        debugPrint('[BackupExportService] Error fetching coins: $e');
      }
    }

    final payload = {
      'schemaVersion': 1,
      'exported_at': DateTime.now().toUtc().toIso8601String(),
      'user_email': email,
      'item_count': coins.length,
      'spot_price_baseline': {
        'timestamp': DateTime.now().toUtc().toIso8601String(),
        'silver_per_oz': 31.50,
        'gold_per_oz': 2450.00,
        'platinum_per_oz': 980.00,
        'currency': 'USD',
      },
      'coins': coins,
    };

    return payload;
  }

  /// Triggers JSON file download in browser or web target.
  static Future<void> exportJsonDownload() async {
    final payload = await generateExportPayload();
    final jsonStr = const JsonEncoder.withIndent('  ').convert(payload);
    final filename = 'numista_collection_backup_${DateTime.now().millisecondsSinceEpoch}.json';

    if (kIsWeb) {
      _triggerWebDownload(jsonStr, filename, 'application/json');
    } else {
      debugPrint('[BackupExportService] Non-web export triggered. Length: ${jsonStr.length}');
    }
  }

  /// Triggers CSV file download in browser or web target.
  static Future<void> exportCsvDownload() async {
    final payload = await generateExportPayload();
    final List coins = payload['coins'] as List;

    final StringBuffer csv = StringBuffer();
    csv.writeln('Year,Mint Mark,Denomination,Program/Series,Condition,Cost,AI Estimated Value,Certification Number,Added');

    for (final c in coins) {
      final map = c as Map<String, dynamic>;
      csv.writeln([
        _cleanCsvCell(map['Year']),
        _cleanCsvCell(map['Mint Mark']),
        _cleanCsvCell(map['Denomination']),
        _cleanCsvCell(map['Program/Series']),
        _cleanCsvCell(map['Condition']),
        _cleanCsvCell(map['Cost']),
        _cleanCsvCell(map['AI Estimated Value']),
        _cleanCsvCell(map['Certification Number']),
        _cleanCsvCell(map['Added']),
      ].join(','));
    }

    final filename = 'numista_collection_${DateTime.now().millisecondsSinceEpoch}.csv';

    if (kIsWeb) {
      _triggerWebDownload(csv.toString(), filename, 'text/csv');
    } else {
      debugPrint('[BackupExportService] CSV non-web export length: ${csv.length}');
    }
  }

  static String _cleanCsvCell(dynamic val) {
    if (val == null) return '""';
    final str = val.toString().replaceAll('"', '""');
    return '"$str"';
  }

  static void _triggerWebDownload(String content, String filename, String mimeType) {
    try {
      final bytes = utf8.encode(content);
      final blob = web.Blob([bytes.toJS].toJS, web.BlobPropertyBag(type: mimeType));
      final url = web.URL.createObjectURL(blob);
      final anchor = web.HTMLAnchorElement()
        ..href = url
        ..download = filename;
      anchor.click();
      web.URL.revokeObjectURL(url);
    } catch (e) {
      debugPrint('[BackupExportService] Web download error: $e');
    }
  }
}
