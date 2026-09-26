import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'auth_service.dart';

/// Shared service for grouping/ungrouping coins as sets.
/// Used by the My Collection UI and (later) Morgan AI assistant.
class SetGroupingService {
  /// Groups loose coins into a new Pattern A set.
  ///
  /// Creates a parent set doc with `is_set: true` and links each child
  /// coin via `parent_set_id` and `set_id`. Optionally sets Storage Location
  /// on all docs. Returns the new parent set doc ID.
  ///
  /// Throws if any coin_id contains `__set_coin_` (virtual) or already
  /// has a non-null `parent_set_id`.
  static Future<String> linkCoinsAsSet({
    required List<String> coinIds,
    required String setTitle,
    String? storageLocation,
    String? year,
    String? mintMark,
  }) async {
    // Validate: at least 2 coins
    if (coinIds.length < 2) {
      throw ArgumentError('A set requires at least 2 coins.');
    }
    
    // Validate: no virtual set coin IDs
    for (final id in coinIds) {
      if (id.contains('__set_coin_')) {
        throw ArgumentError('Cannot group virtual set coins. ID: $id');
      }
    }
    
    final userEmail = AuthService.userEmail;
    
    final coinsRef = FirebaseFirestore.instance
        .collection('users').doc(userEmail).collection('coins');
    
    // Read all target coins and validate none are already in a set
    final batch = FirebaseFirestore.instance.batch();
    
    for (final coinId in coinIds) {
      final doc = await coinsRef.doc(coinId).get();
      if (!doc.exists) {
        throw ArgumentError('Coin not found: $coinId');
      }
      final data = doc.data()!;
      final existingParent = data['parent_set_id'];
      if (existingParent != null && existingParent.toString().isNotEmpty) {
        throw ArgumentError(
          'Coin $coinId is already in a set ($existingParent). '
          'Ungroup it first.'
        );
      }
    }
    
    // Create parent set doc
    final parentRef = coinsRef.doc(); // auto-generate ID
    final parentData = <String, dynamic>{
      'is_set': true,
      'item_type': 'set',
      'Denomination': 'Set',
      'Program/Series': setTitle,
      'set_contents': coinIds,
      'owner_photos': [],
      'created_at': DateTime.now().toUtc().toIso8601String(),
    };
    if (year != null) parentData['Year'] = year;
    if (mintMark != null) parentData['Mint Mark'] = mintMark;
    if (storageLocation != null && storageLocation.isNotEmpty) {
      parentData['Storage Location'] = storageLocation;
    }
    
    batch.set(parentRef, parentData);
    
    // Link each child coin to the parent
    for (final coinId in coinIds) {
      final childUpdate = <String, dynamic>{
        'parent_set_id': parentRef.id,
        'set_id': parentRef.id,
      };
      if (storageLocation != null && storageLocation.isNotEmpty) {
        childUpdate['Storage Location'] = storageLocation;
      }
      batch.update(coinsRef.doc(coinId), childUpdate);
    }
    
    await batch.commit();
    return parentRef.id;
  }

  /// Ungroups a set: clears parent links on all children,
  /// optionally deletes owner photos from Storage, and deletes
  /// the parent set doc.
  ///
  /// If [deleteOwnerPhotos] is true, deletes all owner photo files
  /// from Firebase Storage before removing the parent doc.
  static Future<void> ungroupSet({
    required String parentSetDocId,
    required bool deleteOwnerPhotos,
  }) async {
    final userEmail = AuthService.userEmail;
    
    final coinsRef = FirebaseFirestore.instance
        .collection('users').doc(userEmail).collection('coins');
    
    // Read the parent doc
    final parentDoc = await coinsRef.doc(parentSetDocId).get();
    if (!parentDoc.exists) {
      throw ArgumentError('Set not found: $parentSetDocId');
    }
    final parentData = parentDoc.data()!;
    
    // Delete owner photos from Storage if requested
    if (deleteOwnerPhotos) {
      final ownerPhotos = parentData['owner_photos'] as List<dynamic>? ?? [];
      for (final photo in ownerPhotos) {
        final photoMap = Map<String, dynamic>.from(photo as Map);
        // Delete compressed copy
        final storagePath = photoMap['storage_path'] as String?;
        if (storagePath != null && storagePath.isNotEmpty) {
          try {
            await FirebaseStorage.instance.ref(storagePath).delete();
          } catch (_) { /* file may already be gone */ }
        }
        // Delete original copy
        final originalPath = photoMap['original_storage_path'] as String?;
        if (originalPath != null && originalPath.isNotEmpty) {
          try {
            await FirebaseStorage.instance.ref(originalPath).delete();
          } catch (_) { /* file may already be gone */ }
        }
      }
    }
    
    // Clear parent links on all child coins
    final childIds = (parentData['set_contents'] as List<dynamic>? ?? [])
        .map((e) => e.toString())
        .toList();
    
    final batch = FirebaseFirestore.instance.batch();
    for (final childId in childIds) {
      batch.update(coinsRef.doc(childId), {
        'parent_set_id': FieldValue.delete(),
        'set_id': FieldValue.delete(),
      });
    }
    
    // Delete the parent set doc
    batch.delete(coinsRef.doc(parentSetDocId));
    
    await batch.commit();
  }
  
  /// Syncs the Storage Location from a set parent doc to all its children.
  static Future<void> syncStorageLocationToChildren({
    required String parentSetDocId,
    required String storageLocation,
  }) async {
    final userEmail = AuthService.userEmail;
    
    final coinsRef = FirebaseFirestore.instance
        .collection('users').doc(userEmail).collection('coins');
    
    final parentDoc = await coinsRef.doc(parentSetDocId).get();
    if (!parentDoc.exists) return;
    
    final childIds = (parentDoc.data()!['set_contents'] as List<dynamic>? ?? [])
        .map((e) => e.toString())
        .toList();
    
    final batch = FirebaseFirestore.instance.batch();
    // Update parent
    batch.update(coinsRef.doc(parentSetDocId), {
      'Storage Location': storageLocation,
    });
    // Update all children
    for (final childId in childIds) {
      batch.update(coinsRef.doc(childId), {
        'Storage Location': storageLocation,
      });
    }
    await batch.commit();
  }
}
