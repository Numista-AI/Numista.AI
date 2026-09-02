import 'package:cloud_firestore/cloud_firestore.dart';

/// Lightweight wrapper for table/card rendering in My Collection.
///
/// Wraps both real Firestore snapshots and virtual set children from
/// [expandCollection]. Virtual children have [isVirtualChild] == true
/// and [snapshot] == null. Their [id] is a synthetic string
/// (`{parentId}__set_coin_{idx}`) that must NEVER be used as a
/// Firestore document path.
class CollectionRow {
  /// Document ID (real) or synthetic ID (virtual child).
  final String id;

  /// Document data map — from `doc.data()` (real) or helper output (virtual).
  final Map<String, dynamic> data;

  /// True for virtual children expanded from `set_contents`.
  final bool isVirtualChild;

  /// Parent set document ID. Non-null only for virtual children.
  final String? parentDocId;

  /// The original Firestore snapshot. Null for virtual children.
  /// Mutation actions (edit, delete) require this to be non-null.
  final QueryDocumentSnapshot? snapshot;

  const CollectionRow({
    required this.id,
    required this.data,
    this.isVirtualChild = false,
    this.parentDocId,
    this.snapshot,
  });

  /// True if this row represents a real Firestore document.
  bool get isRealDoc => snapshot != null;
}
