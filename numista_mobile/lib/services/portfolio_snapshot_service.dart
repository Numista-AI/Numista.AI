import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:intl/intl.dart';
import '../services/auth_service.dart';

// ══════════════════════════════════════════════════════════════════════════════
//  PortfolioSnapshotService
//  ────────────────────────
//  Manages daily portfolio value snapshots stored in Firestore at:
//    users/{email}/portfolio_snapshots/{YYYY-MM-DD}
//
//  Snapshots are taken client-side on the first dashboard load of each day.
//  Using the date string as the doc ID guarantees one snapshot per day and
//  makes the "does today exist?" check a single doc GET (not a query).
// ══════════════════════════════════════════════════════════════════════════════

class PortfolioSnapshot {
  final String date;        // YYYY-MM-DD
  final int totalCoins;
  final double portfolioValue;
  final double meltValue;
  final double acquisitionCost;
  final double faceValue;
  final DateTime snapshotAt;

  const PortfolioSnapshot({
    required this.date,
    required this.totalCoins,
    required this.portfolioValue,
    required this.meltValue,
    required this.acquisitionCost,
    required this.faceValue,
    required this.snapshotAt,
  });

  factory PortfolioSnapshot.fromFirestore(Map<String, dynamic> data) {
    return PortfolioSnapshot(
      date: data['date']?.toString() ?? '',
      totalCoins: (data['totalCoins'] as num?)?.toInt() ?? 0,
      portfolioValue: (data['portfolioValue'] as num?)?.toDouble() ?? 0.0,
      meltValue: (data['meltValue'] as num?)?.toDouble() ?? 0.0,
      acquisitionCost: (data['acquisitionCost'] as num?)?.toDouble() ?? 0.0,
      faceValue: (data['faceValue'] as num?)?.toDouble() ?? 0.0,
      snapshotAt: (data['snapshotAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toFirestore() => {
    'date': date,
    'totalCoins': totalCoins,
    'portfolioValue': portfolioValue,
    'meltValue': meltValue,
    'acquisitionCost': acquisitionCost,
    'faceValue': faceValue,
    'snapshotAt': FieldValue.serverTimestamp(),
  };
}

class PortfolioSnapshotService {
  static final _dateFormat = DateFormat('yyyy-MM-dd');

  /// Returns the Firestore collection path for the current user's snapshots.
  static String get _snapshotsPath {
    return 'users/${AuthService.userEmail}/portfolio_snapshots';
  }

  /// Takes a portfolio snapshot for today if one doesn't already exist.
  ///
  /// Call this fire-and-forget on each dashboard load — the first load of the
  /// day creates the snapshot, subsequent loads are a no-op (single doc GET).
  static Future<void> maybeTakeSnapshot({
    required int totalCoins,
    required double portfolioValue,
    required double meltValue,
    required double acquisitionCost,
    required double faceValue,
  }) async {
    try {
      final today = _dateFormat.format(DateTime.now());
      final docRef = FirebaseFirestore.instance
          .collection(_snapshotsPath)
          .doc(today);

      final existing = await docRef.get();
      if (existing.exists) return; // already snapped today

      final snapshot = PortfolioSnapshot(
        date: today,
        totalCoins: totalCoins,
        portfolioValue: portfolioValue,
        meltValue: meltValue,
        acquisitionCost: acquisitionCost,
        faceValue: faceValue,
        snapshotAt: DateTime.now(),
      );

      await docRef.set(snapshot.toFirestore());
    } catch (_) {
      // Non-critical — silently swallow errors so the dashboard isn't blocked.
    }
  }

  /// Returns the most recent [days] worth of snapshots, ordered by date.
  ///
  /// If fewer than [days] snapshots exist, returns whatever is available.
  static Future<List<PortfolioSnapshot>> getSnapshots({int days = 90}) async {
    try {
      final query = await FirebaseFirestore.instance
          .collection(_snapshotsPath)
          .orderBy('date', descending: true)
          .limit(days)
          .get();

      return query.docs
          .map((doc) => PortfolioSnapshot.fromFirestore(doc.data()))
          .toList()
          .reversed  // oldest first for the chart X-axis
          .toList();
    } catch (_) {
      return [];
    }
  }
}
