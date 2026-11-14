import 'package:cloud_firestore/cloud_firestore.dart';
import 'auth_service.dart';
import 'beta_checklist_service.dart';
import 'epn_service.dart';
import '../models/coin_model.dart';
import '../models/program_model.dart';
import '../utils/mint_helpers.dart';
import '../utils/program_goal_helper.dart';
import '../utils/slot_resolver.dart';

class WishlistAutoFillPrefs {
  final Set<String> dismissedSlots;
  final Set<String> dismissedPrograms;
  final Set<String> pinnedPrograms;
  final Map<String, String> goalOverrides;
  final String lastRecipientEmail;
  final List<String> savedRecipientEmails;

  const WishlistAutoFillPrefs({
    this.dismissedSlots = const {},
    this.dismissedPrograms = const {},
    this.pinnedPrograms = const {},
    this.goalOverrides = const {},
    this.lastRecipientEmail = '',
    this.savedRecipientEmails = const [],
  });

  factory WishlistAutoFillPrefs.fromMap(Map<String, dynamic>? data) {
    if (data == null) return const WishlistAutoFillPrefs();
    return WishlistAutoFillPrefs(
      dismissedSlots: Set<String>.from(data['dismissed_slots'] ?? const []),
      dismissedPrograms:
          Set<String>.from(data['dismissed_programs'] ?? const []),
      pinnedPrograms: Set<String>.from(data['pinned_programs'] ?? const []),
      goalOverrides:
          Map<String, String>.from(data['goal_overrides'] ?? const {}),
      lastRecipientEmail:
          (data['last_recipient_email'] ?? '').toString().trim(),
      savedRecipientEmails:
          List<String>.from(data['saved_recipient_emails'] ?? const []),
    );
  }
}

class MissingProgramSlot {
  final String slotKey;
  final CoinProgram program;
  final ProgramCoin coinSlot;
  final ChecklistVariety variety;
  final String mintMark;
  final String varietyLabel;
  final String ebayQuery;
  final String ebayUrl;

  const MissingProgramSlot({
    required this.slotKey,
    required this.program,
    required this.coinSlot,
    required this.variety,
    required this.mintMark,
    required this.varietyLabel,
    required this.ebayQuery,
    required this.ebayUrl,
  });
}

class AutoFilledProgramGroup {
  final CoinProgram program;
  final String effectiveGoal;
  final int ownedCount;
  final int targetCount;
  final int hiddenSlotCount;
  final List<MissingProgramSlot> missingSlots;

  const AutoFilledProgramGroup({
    required this.program,
    required this.effectiveGoal,
    required this.ownedCount,
    required this.targetCount,
    required this.hiddenSlotCount,
    required this.missingSlots,
  });
}

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
      timestamp: (data['timestamp'] is Timestamp)
          ? (data['timestamp'] as Timestamp).toDate()
          : DateTime.now(),
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

  static DocumentReference get _userDoc => _db.doc(AuthService.userDocPath);

  static CollectionReference get _wishlistRef =>
      _userDoc.collection('wishlist');

  static DocumentReference get _prefsDocRef =>
      _userDoc.collection('wishlist_preferences').doc('config');

  static Stream<List<WishlistItem>> getWishlistStream() {
    return _wishlistRef.snapshots().map((snapshot) {
      return snapshot.docs.map((doc) => WishlistItem.fromFirestore(doc)).toList();
    });
  }

  static Stream<WishlistAutoFillPrefs> getWishlistPrefsStream() {
    return _prefsDocRef.snapshots().map((doc) {
      if (!doc.exists) return const WishlistAutoFillPrefs();
      return WishlistAutoFillPrefs.fromMap(doc.data() as Map<String, dynamic>?);
    });
  }

  static Future<WishlistAutoFillPrefs> getWishlistPrefs() async {
    final doc = await _prefsDocRef.get();
    if (!doc.exists) return const WishlistAutoFillPrefs();
    return WishlistAutoFillPrefs.fromMap(doc.data() as Map<String, dynamic>?);
  }

  static Future<void> dismissAutoSlot(String slotKey) async {
    await _prefsDocRef.set({
      'dismissed_slots': FieldValue.arrayUnion([slotKey]),
      'updated_at': FieldValue.serverTimestamp(),
    }, SetOptions(merge: true));
  }

  static Future<void> restoreAutoSlot(String slotKey) async {
    await _prefsDocRef.set({
      'dismissed_slots': FieldValue.arrayRemove([slotKey]),
      'updated_at': FieldValue.serverTimestamp(),
    }, SetOptions(merge: true));
  }

  static Future<void> dismissAutoProgram(String programId) async {
    await _prefsDocRef.set({
      'dismissed_programs': FieldValue.arrayUnion([programId]),
      'updated_at': FieldValue.serverTimestamp(),
    }, SetOptions(merge: true));
  }

  static Future<void> restoreAllHidden() async {
    await _prefsDocRef.set({
      'dismissed_slots': <String>[],
      'dismissed_programs': <String>[],
      'updated_at': FieldValue.serverTimestamp(),
    }, SetOptions(merge: true));
  }

  static Future<void> setProgramGoalOverride(
      String programId, String goal) async {
    await _prefsDocRef.set({
      'goal_overrides': {programId: goal},
      'updated_at': FieldValue.serverTimestamp(),
    }, SetOptions(merge: true));
  }

  static Future<void> pinProgramToWishlist(String programId) async {
    await _prefsDocRef.set({
      'pinned_programs': FieldValue.arrayUnion([programId]),
      'dismissed_programs': FieldValue.arrayRemove([programId]),
      'updated_at': FieldValue.serverTimestamp(),
    }, SetOptions(merge: true));
  }

  static Future<void> saveRecipientEmail(String email) async {
    final normalized = email.trim().toLowerCase();
    if (normalized.isEmpty) return;
    await _prefsDocRef.set({
      'last_recipient_email': normalized,
      'saved_recipient_emails': FieldValue.arrayUnion([normalized]),
      'updated_at': FieldValue.serverTimestamp(),
    }, SetOptions(merge: true));
  }

  static List<AutoFilledProgramGroup> computeAutoMissingPrograms({
    required Map<String, List<CoinProgram>> allProgramsMap,
    required List<Map<String, dynamic>> expandedCoins,
    required Map<String, Map<String, dynamic>> programPreferences,
    required WishlistAutoFillPrefs wishlistPrefs,
    required String userHash,
  }) {
    final allPrograms = allProgramsMap.values.expand((list) => list).toList();
    final groups = <AutoFilledProgramGroup>[];

    for (final program in allPrograms) {
      if (programPreferences[program.id]?['is_manually_completed'] == true) {
        continue;
      }
      if (wishlistPrefs.dismissedPrograms.contains(program.id)) {
        continue;
      }

      final inventory = SlotResolver.resolveProgramInventory(
        program: program,
        coins: expandedCoins,
      );
      final hasOwned = inventory.values.any((r) => r.isOwned);
      final isPinned = wishlistPrefs.pinnedPrograms.contains(program.id);
      if (!hasOwned && !isPinned) continue;

      final effectiveGoal = wishlistPrefs.goalOverrides[program.id] ??
          programPreferences[program.id]?['goal']?.toString() ??
          ProgramGoalHelper.defaultAutoFillGoal;

      int targetCount = 0;
      int ownedCount = 0;
      int hiddenSlotCount = 0;
      final missingSlots = <MissingProgramSlot>[];

      for (final coinSlot in program.coins) {
        if (coinSlot.name.contains('Pending')) continue;
        for (final variety in coinSlot.varieties) {
          if (variety.label.contains('Pending')) continue;
          if (!ProgramGoalHelper.goalAllowsVariety(variety, effectiveGoal)) {
            continue;
          }

          final slotKey = '${program.id}_${coinSlot.id}_${variety.id}';
          targetCount++;

          if (inventory[slotKey]?.isOwned == true) {
            ownedCount++;
            continue;
          }
          if (wishlistPrefs.dismissedSlots.contains(slotKey)) {
            hiddenSlotCount++;
            continue;
          }

          final ebayQuery = ProgramGoalHelper.buildEbayQuery(
            program: program,
            coinSlot: coinSlot,
            variety: variety,
          );
          final ebayUrl = EpnService.buildSearchUrlFromQuery(
            ebayQuery,
            customId: '${userHash}_${program.id}',
          );

          missingSlots.add(
            MissingProgramSlot(
              slotKey: slotKey,
              program: program,
              coinSlot: coinSlot,
              variety: variety,
              mintMark: ProgramGoalHelper.extractRawMintMark(variety),
              varietyLabel: ProgramGoalHelper.describeVarietyForSenior(variety),
              ebayQuery: ebayQuery,
              ebayUrl: ebayUrl,
            ),
          );
        }
      }

      if (missingSlots.isNotEmpty || hiddenSlotCount > 0) {
        groups.add(
          AutoFilledProgramGroup(
            program: program,
            effectiveGoal: effectiveGoal,
            ownedCount: ownedCount,
            targetCount: targetCount,
            hiddenSlotCount: hiddenSlotCount,
            missingSlots: missingSlots,
          ),
        );
      }
    }
    return groups;
  }

  static Future<void> addToWishlist(CoinModel coin) async {
    await _wishlistRef.add({
      'type': 'individual',
      'coin': coin.toFirestore(),
      'timestamp': FieldValue.serverTimestamp(),
    });
    BetaChecklistService.autoCompleteTask('task_14_wishlist');
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
      BetaChecklistService.autoCompleteTask('task_14_wishlist');
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

  /// Checks if a newly added/found coin matches anything in the wishlist.
  static Future<WishlistItem?> checkMatchAndMarkAsFound(CoinModel foundCoin) async {
    final snapshot = await _wishlistRef.get();
    final foundYear = foundCoin.year.trim();
    final foundDenom = foundCoin.denomination.trim().toLowerCase();
    final foundMm = MintHelpers.readMintMark({'mint_mark': foundCoin.mintMark});
    final foundTheme = foundCoin.themeSubject.trim().toLowerCase();

    for (var doc in snapshot.docs) {
      final item = WishlistItem.fromFirestore(doc);

      if (item.type == 'individual' && item.coin != null) {
        final wish = item.coin!;
        final wishYear = wish.year.trim();
        final wishDenom = wish.denomination.trim().toLowerCase();
        final wishMm = MintHelpers.readMintMark({'mint_mark': wish.mintMark});
        final wishTheme = wish.themeSubject.trim().toLowerCase();

        final yearMatch = wishYear.isEmpty || wishYear == foundYear;
        final denomMatch = wishDenom.isEmpty || wishDenom == foundDenom;
        final mintMatch = wishMm.isEmpty || wishMm == foundMm;
        final themeMatch = wishTheme.isEmpty ||
            foundTheme.contains(wishTheme) ||
            wishTheme.contains(foundTheme);

        if (yearMatch && denomMatch && mintMatch && themeMatch) {
          return item;
        }
      }
    }
    return null;
  }

  /// Seeds the initial wishlist for testing as requested by the user.
  static Future<void> seedInitialWishlist() async {
    await pinProgramToWishlist('50state');
  }
}
