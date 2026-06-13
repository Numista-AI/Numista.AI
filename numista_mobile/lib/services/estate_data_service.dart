import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/estate_models.dart';

/// Firestore CRUD for per-coin estate annotations.
/// Collection path: users/{uid}/estate_data/{coinId}
class EstateDataService {
  static CollectionReference<Map<String, dynamic>> _col(String uid) =>
      FirebaseFirestore.instance
          .collection('users')
          .doc(uid)
          .collection('estate_data');

  /// Returns a map of coinId → CoinEstateData for all estate annotations.
  static Future<Map<String, CoinEstateData>> getAllEstateData(
      String uid) async {
    try {
      final snap = await _col(uid).get();
      final result = <String, CoinEstateData>{};
      for (final doc in snap.docs) {
        result[doc.id] = CoinEstateData.fromFirestore(doc);
      }
      return result;
    } catch (_) {
      return {};
    }
  }

  /// Saves or overwrites estate data for a single coin.
  static Future<void> saveCoinEstateData(
      String uid, CoinEstateData data) async {
    await _col(uid)
        .doc(data.coinId)
        .set(data.toFirestore(), SetOptions(merge: true));
  }

  /// Deletes estate data for a single coin.
  static Future<void> deleteCoinEstateData(
      String uid, String coinId) async {
    await _col(uid).doc(coinId).delete();
  }

  /// Real-time stream of all coin estate data (map of coinId → data).
  static Stream<Map<String, CoinEstateData>> watchEstateData(String uid) {
    return _col(uid).snapshots().map((snap) {
      final result = <String, CoinEstateData>{};
      for (final doc in snap.docs) {
        result[doc.id] = CoinEstateData.fromFirestore(doc);
      }
      return result;
    });
  }
}
