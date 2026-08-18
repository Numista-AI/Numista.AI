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
  /// Writes exclusively to canonical 4-segment path: users/{uid}/metadata/collection_stats.
  static Future<Map<String, dynamic>> rebuildAndUpsertStats() async {
    if (AuthService.coinsPath.contains('unknown')) {
      throw StateError('Cannot rebuild collection_stats for unauthenticated user path.');
    }

    final db = FirebaseFirestore.instance;
    final snap = await db.collection(AuthService.coinsPath).limit(500).get();

    int totalItems = snap.docs.length;
    int coinCount = 0;
    int supplyCount = 0;
    double faceValue = 0.0;
    double meltValue = 0.0;
    double acquisitionCost = 0.0;
    double bidTotal = 0.0;
    double cpgTotal = 0.0;

    for (final doc in snap.docs) {
      final d = doc.data();
      final itemType = (d['item_type'] ?? '').toString().toLowerCase().trim();
      final isSupply = d['is_supply'] == true || itemType == 'supply';

      if (isSupply) {
        supplyCount++;
      } else {
        coinCount++;
        faceValue += _parseNumber(d['Face Value'] ?? d['face_value'] ?? d['Denomination']);
        meltValue += _parseNumber(d['Melt Value'] ?? d['melt_value']);
        acquisitionCost += _parseNumber(d['Cost'] ?? d['purchase_price']);

        final cpg = _parseNumber(d['cpgRetail']);
        final bid = _parseNumber(d['greysheetBid']);
        final aiVal = _parseAiValue((d['AI Estimated Value'] ?? d['ai_value'] ?? '').toString());
        final baseVal = cpg > 0 ? cpg : (bid > 0 ? bid : aiVal);

        final finalCpg = cpg > 0 ? cpg : baseVal;
        final finalBid = bid > 0 ? bid : (baseVal * 0.80);

        cpgTotal += finalCpg;
        bidTotal += finalBid;
      }
    }

    final stats = {
      'item_count': totalItems,
      'coin_count': coinCount,
      'supply_count': supplyCount,
      'face_value': double.parse(faceValue.toStringAsFixed(2)),
      'melt_value': double.parse(meltValue.toStringAsFixed(2)),
      'acquisition_cost': double.parse(acquisitionCost.toStringAsFixed(2)),
      'bid_total': double.parse(bidTotal.toStringAsFixed(2)),
      'cpg_total': double.parse(cpgTotal.toStringAsFixed(2)),
      'est_value': double.parse(bidTotal.toStringAsFixed(2)), // Estate mode is canonical default
      'last_updated': DateTime.now().toUtc().toIso8601String(),
    };

    try {
      await db.doc(AuthService.statsDocPath).set(stats, SetOptions(merge: true));
    } catch (_) {}

    return stats;
  }
}
