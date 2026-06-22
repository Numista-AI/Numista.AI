// mint_error_service.dart
//
// Firestore service for the Mint Error Library.
// Reads from the top-level `mint_errors` collection (public — no auth required).

import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/mint_error.dart';

class MintErrorService {
  static final FirebaseFirestore _db = FirebaseFirestore.instance;
  static const String _collection = 'mint_errors';

  // ─── Stream: all published errors, optionally filtered ───────────────────
  static Stream<List<MintError>> streamErrors({
    String? dataset,   // 'collectible' | 'common' | 'recent' | 'photographed'
    String? category,  // 'Doubled Die' | 'Planchet' | etc.
  }) {
    Query<Map<String, dynamic>> q = _db
        .collection(_collection)
        .where('isPublished', isEqualTo: true)
        .orderBy('name');

    if (dataset != null && dataset.isNotEmpty) {
      q = q.where('datasets', arrayContains: dataset);
    }
    if (category != null && category.isNotEmpty) {
      q = q.where('category', isEqualTo: category);
    }

    return q.snapshots().map(
          (snap) => snap.docs.map(MintError.fromFirestore).toList(),
        );
  }

  // ─── Future: single error by ID ──────────────────────────────────────────
  static Future<MintError?> getErrorById(String errorId) async {
    final doc = await _db.collection(_collection).doc(errorId).get();
    if (!doc.exists) return null;
    return MintError.fromFirestore(doc);
  }

  // ─── Future: search by name, year or denomination ────────────────────────
  // Note: Firestore doesn't support full-text search natively.
  // We fetch all published errors and filter client-side (dataset is <300 records).
  static Future<List<MintError>> searchErrors(String query) async {
    if (query.trim().isEmpty) return [];
    final lower = query.toLowerCase();
    final snap = await _db
        .collection(_collection)
        .where('isPublished', isEqualTo: true)
        .get();

    return snap.docs
        .map(MintError.fromFirestore)
        .where((e) =>
            e.name.toLowerCase().contains(lower) ||
            e.shortName.toLowerCase().contains(lower) ||
            e.category.toLowerCase().contains(lower) ||
            e.denominations.any((d) => d.toLowerCase().contains(lower)) ||
            e.years.any((y) => '$y'.contains(lower)) ||
            e.designation.toLowerCase().contains(lower))
        .toList();
  }

  // ─── Future: errors that match a coin's denomination and year range ───────
  // Used by coin_detail_screen to show "Known Errors for this coin".
  static Future<List<MintError>> getErrorsForCoin({
    required String denomination,
    required int year,
  }) async {
    final snap = await _db
        .collection(_collection)
        .where('isPublished', isEqualTo: true)
        .where('denominations', arrayContains: denomination.toLowerCase())
        .get();

    final all = snap.docs.map(MintError.fromFirestore).toList();
    // Filter by year (years list contains the coin's year OR is empty = "any year")
    return all.where((e) => e.years.isEmpty || e.years.contains(year)).toList();
  }

  // ─── Distinct categories list (for filter chips) ─────────────────────────
  static Future<List<String>> getCategories() async {
    final snap = await _db
        .collection(_collection)
        .where('isPublished', isEqualTo: true)
        .get();
    final cats = snap.docs
        .map(MintError.fromFirestore)
        .map((e) => e.category)
        .toSet()
        .toList()
      ..sort();
    return cats;
  }
}
