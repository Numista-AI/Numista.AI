import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../services/auth_service.dart';

/// Manages the two non-authenticated entry tiers:
///
/// [browseDemoMode]  – Read-only. Coins loaded from JSON asset into memory,
///                    no Firestore reads or writes. Zero Firebase auth.
///
/// [guestMode]       – Firebase Anonymous Auth. On first login the 100 demo
///                    coins are seeded into the user's own Firestore collection.
///                    Full features except CSV download and wishlist share.
class GuestSeedService {

  // ─── Demo mode flag ───────────────────────────────────────────────────────
  static bool _browseDemoActive = false;
  static List<Map<String, dynamic>> _demoCoinCache = [];

  static bool get isBrowseDemoMode => _browseDemoActive;

  /// Activate Browse Demo: load JSON into memory, no Firestore.
  static Future<void> activateBrowseDemo() async {
    final jsonStr = await rootBundle.loadString('assets/guest_demo_coins.json');
    _demoCoinCache = List<Map<String, dynamic>>.from(jsonDecode(jsonStr));
    _browseDemoActive = true;
  }

  static void deactivateBrowseDemo() {
    _browseDemoActive = false;
    _demoCoinCache = [];
  }

  /// Returns the in-memory demo coin list (Browse Demo mode only).
  static List<Map<String, dynamic>> get demoCoinCache => _demoCoinCache;

  // ─── Guest (Anonymous) seeding ────────────────────────────────────────────

  static const _prefSeedKey = 'guest_seeded_';

  /// Call after Firebase Anonymous Sign-In. Seeds 100 demo coins into the
  /// user's Firestore collection if they haven't been seeded yet this session.
  static Future<void> seedIfNeeded(String uid) async {
    final prefs = await SharedPreferences.getInstance();
    final alreadySeeded = prefs.getBool('$_prefSeedKey$uid') ?? false;
    if (alreadySeeded) return;

    try {
      final jsonStr = await rootBundle.loadString('assets/guest_demo_coins.json');
      final List<dynamic> coins = jsonDecode(jsonStr);
      final coinsPath = AuthService.coinsPath;
      final batch = FirebaseFirestore.instance.batch();

      for (final coin in coins) {
        final ref = FirebaseFirestore.instance.collection(coinsPath).doc();
        final data = Map<String, dynamic>.from(coin as Map);
        data['_demo'] = true;                           // mark as demo data
        data['_seededAt'] = FieldValue.serverTimestamp();
        batch.set(ref, data);
      }

      await batch.commit();
      await prefs.setBool('$_prefSeedKey$uid', true);
    } catch (e) {
      // Non-fatal — user can still use the app, just without pre-seeded coins
      debugPrint('GuestSeedService: seed failed — $e');
    }
  }

  // ─── Permission helpers ───────────────────────────────────────────────────

  /// True when the current user should be blocked from downloading data.
  static bool get canDownload =>
      !_browseDemoActive && !(AuthService.isGuest);

  /// True when the current user can share their wishlist externally.
  static bool get canShareWishlist =>
      !_browseDemoActive && !(AuthService.isGuest);

  // ─── Demo spreadsheet ─────────────────────────────────────────────────────

  /// Loads the bundled demo CSV bytes for use in the wizard upload step.
  static Future<Uint8List> loadDemoSpreadsheetBytes() async {
    final byteData = await rootBundle.load('assets/demo_spreadsheet.csv');
    return byteData.buffer.asUint8List();
  }

  /// Returns a stream that emits a single `DemoQuerySnapshot` containing the
  /// in-memory cached demo coins.
  static Stream<QuerySnapshot<Map<String, dynamic>>> getDemoCoinsStream() {
    final snapshots = _demoCoinCache.asMap().entries.map((e) {
      return DemoDocumentSnapshot('demo_${e.key}', Map<String, dynamic>.from(e.value));
    }).toList();
    return Stream.value(DemoQuerySnapshot(snapshots));
  }

  /// Returns a future that resolves to a `DemoQuerySnapshot` containing the
  /// in-memory cached demo coins.
  static Future<QuerySnapshot<Map<String, dynamic>>> getDemoCoinsFuture() async {
    final snapshots = _demoCoinCache.asMap().entries.map((e) {
      return DemoDocumentSnapshot('demo_${e.key}', Map<String, dynamic>.from(e.value));
    }).toList();
    return Future.value(DemoQuerySnapshot(snapshots));
  }
}

// ignore: subtype_of_sealed_class
class DemoDocumentSnapshot implements QueryDocumentSnapshot<Map<String, dynamic>> {
  @override
  final String id;
  final Map<String, dynamic> _data;

  DemoDocumentSnapshot(this.id, this._data);

  @override
  Map<String, dynamic> data([SnapshotOptions? options]) => _data;

  @override
  dynamic operator [](Object field) => _data[field];

  @override
  dynamic get(Object field) => _data[field];

  @override
  bool get exists => true;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

// ignore: subtype_of_sealed_class
class DemoQuerySnapshot implements QuerySnapshot<Map<String, dynamic>> {
  @override
  final List<QueryDocumentSnapshot<Map<String, dynamic>>> docs;

  DemoQuerySnapshot(this.docs);

  bool get isEmpty => docs.isEmpty;

  @override
  int get size => docs.length;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
