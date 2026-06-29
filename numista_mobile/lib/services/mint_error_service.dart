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
  // NOTE: To avoid requiring a composite index on every filter combination,
  // we apply orderBy only when no extra filters are active, and sort client-side
  // otherwise. Firestore requires composite indexes for (filter + orderBy) combos.
  static Stream<List<MintError>> streamErrors({
    String? dataset,   // 'collectible' | 'common' | 'recent' | 'photographed'
    String? category,  // 'Doubled Die' | 'Planchet' | etc.
  }) {
    final hasFilter = (dataset != null && dataset.isNotEmpty) ||
        (category != null && category.isNotEmpty);

    Query<Map<String, dynamic>> q = _db
        .collection(_collection)
        .where('isPublished', isEqualTo: true);

    // Only add orderBy when no extra filters — avoids composite index requirement
    if (!hasFilter) {
      q = q.orderBy('name');
    }

    if (dataset != null && dataset.isNotEmpty) {
      q = q.where('datasets', arrayContains: dataset);
    }
    if (category != null && category.isNotEmpty) {
      q = q.where('category', isEqualTo: category);
    }

    return q.snapshots().map((snap) {
      final list = snap.docs.map(MintError.fromFirestore).toList();
      // Client-side sort when orderBy was skipped due to filters
      if (hasFilter) list.sort((a, b) => a.name.compareTo(b.name));
      return list;
    });
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
    // Normalize denomination — coins may store 'Quarter Dollar', '25C', 'Quarter', etc.
    final normalized = _normalizeDenomination(denomination);

    final snap = await _db
        .collection(_collection)
        .where('isPublished', isEqualTo: true)
        .where('denominations', arrayContains: normalized)
        .get();

    final all = snap.docs.map(MintError.fromFirestore).toList();
    // Filter by year (years list contains the coin's year OR is empty = "any year")
    return all.where((e) => e.years.isEmpty || e.years.contains(year)).toList();
  }

  // ─── Denomination normalizer ──────────────────────────────────────────────
  // Maps any denomination string variant to the lowercase key used in Firestore.
  static String _normalizeDenomination(String raw) {
    final s = raw.toLowerCase().trim();
    if (s.contains('cent') || s.contains('penny') || s == '1c' || s == '1¢') return 'cent';
    if (s.contains('nickel') || s == '5c' || s == '5¢') return 'nickel';
    if (s.contains('dime') || s == '10c' || s == '10¢') return 'dime';
    if (s.contains('quarter') || s == '25c' || s == '25¢') return 'quarter';
    if (s.contains('half') || s == '50c' || s == '50¢') return 'half dollar';
    if (s.contains('dollar') && !s.contains('half')) return 'dollar';
    if (s.contains('eagle') && s.contains('silver')) return 'silver eagle';
    if (s.contains('eagle') && s.contains('gold')) return 'gold eagle';
    if (s.contains('currency') || s.contains('note') || s.contains('bill')) return 'currency';
    return s; // fallback: pass through as-is
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
