import 'package:cloud_firestore/cloud_firestore.dart';
import 'auth_service.dart';
import '../models/coin_model.dart';

class WishlistItem {
  final String id;
  final String type; // 'individual' or 'program'
  final String? programId;
  final CoinModel? coin;
  
  // Legacy: List of coin IDs found (simple flat tracking)
  final List<String> addedCoins; 
  
  // Expert: Map of coinId -> List<varietyId>
  final Map<String, List<String>> foundVarieties; 
  
  final DateTime timestamp;

  WishlistItem({
    required this.id,
    required this.type,
    this.programId,
    this.coin,
    this.addedCoins = const [],
    this.foundVarieties = const {},
    required this.timestamp,
  });

  factory WishlistItem.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>;
    
    // Map conversion for foundVarieties
    final rawVarieties = data['foundVarieties'] as Map<String, dynamic>? ?? {};
    final convertedVarieties = rawVarieties.map((key, value) => MapEntry(key, List<String>.from(value)));

    return WishlistItem(
      id: doc.id,
      type: data['type'] ?? 'individual',
      programId: data['programId'],
      coin: data['coin'] != null ? CoinModel.fromMap(data['coin'], doc.id) : null,
      addedCoins: List<String>.from(data['addedCoins'] ?? []),
      foundVarieties: convertedVarieties,
      timestamp: (data['timestamp'] as Timestamp).toDate(),
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'type': type,
      'programId': programId,
      'coin': coin?.toFirestore(),
      'addedCoins': addedCoins,
      'foundVarieties': foundVarieties,
      'timestamp': FieldValue.serverTimestamp(),
    };
  }
}

class WishlistService {
  static final FirebaseFirestore _db = FirebaseFirestore.instance;

  static CollectionReference get _wishlistRef =>
      _db.collection('users').doc(AuthService.userEmail).collection('wishlist');

  static Stream<List<WishlistItem>> getWishlistStream() {
    return _wishlistRef.snapshots().map((snapshot) {
      return snapshot.docs.map((doc) => WishlistItem.fromFirestore(doc)).toList();
    });
  }

  static Future<void> addToWishlist(CoinModel coin) async {
    await _wishlistRef.add({
      'type': 'individual',
      'coin': coin.toFirestore(),
      'timestamp': FieldValue.serverTimestamp(),
    });
  }

  static Future<void> addProgramToWishlist(String programId, {
    List<String> initialAdded = const [],
    Map<String, List<String>> initialVarieties = const {},
  }) async {
    // Check if program already exists in wishlist
    final existing = await _wishlistRef.where('programId', isEqualTo: programId).get();
    if (existing.docs.isEmpty) {
      await _wishlistRef.add({
        'type': 'program',
        'programId': programId,
        'addedCoins': initialAdded,
        'foundVarieties': initialVarieties,
        'timestamp': FieldValue.serverTimestamp(),
      });
    }
  }

  static Future<void> removeFromWishlist(String id) async {
    await _wishlistRef.doc(id).delete();
  }

  static Future<void> updateProgramProgress(String id, {List<String>? addedCoins, Map<String, List<String>>? varieties}) async {
    final updateData = <String, dynamic>{};
    if (addedCoins != null) updateData['addedCoins'] = addedCoins;
    if (varieties != null) updateData['foundVarieties'] = varieties;
    
    await _wishlistRef.doc(id).update(updateData);
  }

  /// Logic to determine which variety a found coin belongs to
  static String? _getVarietyIdForCoin(CoinModel coin) {
    final mint = coin.mintMark.toUpperCase();
    final strike = coin.strikeType.toLowerCase();
    final metal = coin.metalContent.toLowerCase();

    if (strike.contains('satin')) return 'S-SATIN';
    if (mint == 'S' && metal.contains('silver')) return 'S-SILVER';
    if (mint == 'S' && strike.contains('proof')) return 'S-CLAD';
    if (mint == 'D') return 'D-UNC';
    if (mint == 'P') return 'P-UNC';
    
    return null;
  }

  /// Checks if a newly added/found coin matches anything in the wishlist.
  static Future<WishlistItem?> checkMatchAndMarkAsFound(CoinModel foundCoin) async {
    final snapshot = await _wishlistRef.get();
    for (var doc in snapshot.docs) {
      final item = WishlistItem.fromFirestore(doc);
      
      if (item.type == 'individual' && item.coin != null) {
        if (item.coin!.year == foundCoin.year && 
            item.coin!.denomination == foundCoin.denomination &&
            item.coin!.mintMark == foundCoin.mintMark) {
          return item;
        }
      } else if (item.type == 'program' && item.programId != null) {
        // Expertise Logic: Matching Varieties
        if (item.programId == '5state' && foundCoin.programSeries == '50 State Quarters Program') {
          final coinId = foundCoin.themeSubject.toLowerCase().replaceAll(' ', '_');
          final varietyId = _getVarietyIdForCoin(foundCoin);
          
          if (coinId.isNotEmpty && varietyId != null) {
            final currentVarieties = Map<String, List<String>>.from(item.foundVarieties);
            final coinVarieties = List<String>.from(currentVarieties[coinId] ?? []);
            
            if (!coinVarieties.contains(varietyId)) {
              coinVarieties.add(varietyId);
              currentVarieties[coinId] = coinVarieties;
              await updateProgramProgress(item.id, varieties: currentVarieties);
            }
          }
        }
      }
    }
    return null;
  }

  /// Seeds the initial wishlist for testing as requested by the user.
  static Future<void> seedInitialWishlist() async {
    await addProgramToWishlist('50state', initialAdded: [
      'New York', 
      'New Jersey', 
      'Alaska', 
      'Virginia', 
      'Colorado', 
      'Louisiana', 
      'Pennsylvania', 
      'North Carolina'
    ]);
  }
}
