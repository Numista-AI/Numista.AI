import 'package:cloud_firestore/cloud_firestore.dart';
import 'auth_service.dart';

class CollectionStatsService {
  static double _parseNumber(dynamic val) {
    if (val == null) return 0.0;
    if (val is num) return val.toDouble();
    final s = val.toString().replaceAll(RegExp(r'[^\d.]'), '');
    return double.tryParse(s) ?? 0.0;
  }

  static double _parseAiValue(String raw) {
    if (raw.isEmpty || raw == 'Pending' || raw == 'null') return 0.0;
    final norm = raw
        .replaceAll(',', '')
        .replaceAll('\u2013', '-')
        .replaceAll('\u2014', '-')
        .replaceAll('\u2012', '-');
    final rangeMatch = RegExp(r'(\d+\.?\d*)\s*-\s*[^0-9]*(\d+\.?\d*)').firstMatch(norm);
    if (rangeMatch != null) {
      final a = double.tryParse(rangeMatch.group(1)!) ?? 0.0;
      return a > 100000 ? 0.0 : a;
    }
    final v = double.tryParse(norm.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;
    return v > 100000 ? 0.0 : v;
  }

  /// One-shot aggregation rebuild of collection_stats capped at 500 docs.
  /// Upserts users/{uid}/metadata/collection_stats and merges into users/{uid}.
  static Future<Map<String, dynamic>> rebuildAndUpsertStats() async {
    final db = FirebaseFirestore.instance;
    final snap = await db.collection(AuthService.coinsPath).limit(500).get();

    int totalItems = snap.docs.length;
    int coinCount = 0;
    int supplyCount = 0;
    double faceValue = 0.0;
    double meltValue = 0.0;
    double estValue = 0.0;

    for (final doc in snap.docs) {
      final d = doc.data();
      final itemType = (d['item_type'] ?? '').toString().toLowerCase().trim();
      final isSupply = d['is_supply'] == true || itemType == 'supply';

      if (isSupply) {
        supplyCount++;
      } else {
        coinCount++;
        faceValue += _parseNumber(d['Face Value'] ?? d['face_value']);
        meltValue += _parseNumber(d['Melt Value'] ?? d['melt_value']);

        final cpg = _parseNumber(d['cpgRetail']);
        final bid = _parseNumber(d['greysheetBid']);
        final val = cpg > 0 ? cpg : (bid > 0 ? bid : _parseAiValue((d['AI Estimated Value'] ?? d['ai_value'] ?? '').toString()));
        estValue += val;
      }
    }

    final stats = {
      'item_count': totalItems,
      'coin_count': coinCount,
      'supply_count': supplyCount,
      'face_value': double.parse(faceValue.toStringAsFixed(2)),
      'melt_value': double.parse(meltValue.toStringAsFixed(2)),
      'est_value': double.parse(estValue.toStringAsFixed(2)),
      'last_updated': DateTime.now().toUtc().toIso8601String(),
    };

    try {
      await db.doc(AuthService.statsDocPath).set(stats, SetOptions(merge: true));
      await db.doc(AuthService.userDocPath).set({'collection_stats': stats}, SetOptions(merge: true));
    } catch (_) {}

    return stats;
  }
}
