import 'dart:async';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import 'auth_service.dart';

class BetaTaskItem {
  final String id;
  final String title;
  final String description;
  final bool isAutoDetectable;
  final bool supportsSkip;

  const BetaTaskItem({
    required this.id,
    required this.title,
    required this.description,
    this.isAutoDetectable = false,
    this.supportsSkip = false,
  });
}

class BetaChecklistService {
  static final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  static const List<BetaTaskItem> allTasks = [
    BetaTaskItem(
      id: 'task_1_account',
      title: '1. Sign Up / Log In',
      description: 'Create a beta account or log in.',
    ),
    BetaTaskItem(
      id: 'task_2_onboarding',
      title: '2. Onboarding Tour',
      description: 'View or complete the Onboarding Wizard.',
    ),
    BetaTaskItem(
      id: 'task_3_manual_entry',
      title: '3. Manual Coin Entry',
      description: 'Add a coin manually with Year, Mint, and Grade.',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_4_csv_upload',
      title: '4. CSV / Excel Import',
      description: 'Import a spreadsheet using Smart Column Mapper.',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_5_invoice_pdf',
      title: '5. Invoice PDF Scan',
      description: 'Upload a PDF purchase receipt for AI extraction.',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_6_pcgs_cert',
      title: '6. PCGS / NGC Cert Verification',
      description: 'Lookup a cert number and click the pop-up link.',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_7_roll_batch',
      title: '7. Roll & Batch Entry Wizard',
      description: 'Enter a roll of coins using the Roll Wizard.',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_8_checklist_ocr',
      title: '8. Checklist Photo OCR',
      description: 'Upload a photo of a physical paper checklist.',
    ),
    BetaTaskItem(
      id: 'task_9_microscope',
      title: '9. USB Microscope Scanner',
      description: 'Capture or link a coin photo via camera scanner.',
      supportsSkip: true,
    ),
    BetaTaskItem(
      id: 'task_10_search_sort',
      title: '10. Collection Search & Sort',
      description: 'Filter and sort collection table by Year, Mint, Grade.',
    ),
    BetaTaskItem(
      id: 'task_11_sticky_headers',
      title: '11. Sticky Header Freeze Pane',
      description: 'Scroll down collection table and verify header pins.',
    ),
    BetaTaskItem(
      id: 'task_12_currency',
      title: '12. Currency & Banknotes',
      description: 'Add a paper bill or banknote to your collection.',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_13_world_items',
      title: '13. World & Specialty Items',
      description: 'Add a foreign coin or specialty item.',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_14_wishlist',
      title: '14. Wish List & eBay Links',
      description: 'Add a wanted item to Wish List & click "Find on eBay".',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_15_public_wishlist',
      title: '15. Public Wish List Sharing',
      description: 'Generate and test your read-only public Wish List link.',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_16_estate_report',
      title: '16. Estate Planning Report',
      description: 'View portfolio valuation & generate Estate Report PDF.',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_17_family_subaccounts',
      title: '17. Family Sub-Accounts',
      description: 'Open Family Settings and test custodian sub-accounts.',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_18_ai_chat',
      title: '18. AI Deepdive (Ask Morgan)',
      description: 'Ask Morgan a question in AI Deepdive chat.',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_19_coa_inspector',
      title: '19. COA Inspector',
      description: 'Scan or view a Certificate of Authenticity document.',
      isAutoDetectable: true,
    ),
    BetaTaskItem(
      id: 'task_20_overall_feedback',
      title: '20. Overall Beta Review',
      description: 'Submit your ratings via the floating 💬 Feedback button.',
      isAutoDetectable: true,
    ),
  ];

  static final StreamController<BetaChecklistEvent> _eventController =
      StreamController<BetaChecklistEvent>.broadcast();

  /// Broadcast stream of task completion events for UI toasts and telemetry.
  static Stream<BetaChecklistEvent> get onTaskCompleted => _eventController.stream;

  static String get _userIdentifier {
    final user = FirebaseAuth.instance.currentUser;
    if (user != null) {
      if (user.email != null && user.email!.trim().isNotEmpty) {
        return user.email!.trim().toLowerCase();
      }
      return user.uid;
    }
    return AuthService.userEmail.isNotEmpty ? AuthService.userEmail : 'guest_demo_user';
  }

  static DocumentReference<Map<String, dynamic>> _getDocRef() {
    return _firestore
        .collection('users')
        .doc(_userIdentifier)
        .collection('settings')
        .doc('beta_checklist');
  }

  /// Stream of checklist state from `users/{identifier}/settings/beta_checklist`.
  static Stream<DocumentSnapshot<Map<String, dynamic>>> getChecklistStream() {
    return _getDocRef().snapshots();
  }

  /// Toggle task completed state manually from the modal UI.
  static Future<void> toggleTaskCompleted(String taskId, bool isCompleted) async {
    try {
      final docRef = _getDocRef();
      final doc = await docRef.get();

      List<String> completed = [];
      List<String> skipped = [];

      if (doc.exists && doc.data() != null) {
        completed = List<String>.from(doc.data()!['completed_tasks'] ?? []);
        skipped = List<String>.from(doc.data()!['skipped_tasks'] ?? []);
      }

      if (isCompleted) {
        if (!completed.contains(taskId)) completed.add(taskId);
        skipped.remove(taskId);
      } else {
        completed.remove(taskId);
      }

      final total = allTasks.length;
      final percentage =
          ((completed.length + skipped.length) / total * 100).clamp(0.0, 100.0);

      await docRef.set({
        'completed_tasks': completed,
        'skipped_tasks': skipped,
        'completed_count': completed.length,
        'skipped_count': skipped.length,
        'total_tasks': total,
        'completion_percentage': percentage,
        'is_fully_completed': (completed.length + skipped.length) >= total,
        'created_at': doc.exists ? (doc.data()!['created_at'] ?? FieldValue.serverTimestamp()) : FieldValue.serverTimestamp(),
        'last_synced_at': doc.exists ? (doc.data()!['last_synced_at'] ?? FieldValue.serverTimestamp()) : FieldValue.serverTimestamp(),
        'last_updated': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));

      if (isCompleted) {
        final task = allTasks.cast<BetaTaskItem?>().firstWhere(
          (t) => t?.id == taskId,
          orElse: () => null,
        );
        if (task != null) {
          _eventController.add(BetaChecklistEvent(taskId: taskId, taskTitle: task.title));
        }
      }
    } catch (e) {
      debugPrint('[BetaChecklistService] toggleTaskCompleted error — $e');
    }
  }

  /// Toggle task skipped state (for N/A hardware tasks).
  static Future<void> toggleTaskSkipped(String taskId, bool isSkipped) async {
    try {
      final docRef = _getDocRef();
      final doc = await docRef.get();

      List<String> completed = [];
      List<String> skipped = [];

      if (doc.exists && doc.data() != null) {
        completed = List<String>.from(doc.data()!['completed_tasks'] ?? []);
        skipped = List<String>.from(doc.data()!['skipped_tasks'] ?? []);
      }

      if (isSkipped) {
        if (!skipped.contains(taskId)) skipped.add(taskId);
        completed.remove(taskId);
      } else {
        skipped.remove(taskId);
      }

      final total = allTasks.length;
      final percentage =
          ((completed.length + skipped.length) / total * 100).clamp(0.0, 100.0);

      await docRef.set({
        'completed_tasks': completed,
        'skipped_tasks': skipped,
        'completed_count': completed.length,
        'skipped_count': skipped.length,
        'total_tasks': total,
        'completion_percentage': percentage,
        'is_fully_completed': (completed.length + skipped.length) >= total,
        'created_at': doc.exists ? (doc.data()!['created_at'] ?? FieldValue.serverTimestamp()) : FieldValue.serverTimestamp(),
        'last_synced_at': doc.exists ? (doc.data()!['last_synced_at'] ?? FieldValue.serverTimestamp()) : FieldValue.serverTimestamp(),
        'last_updated': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));
    } catch (e) {
      debugPrint('[BetaChecklistService] toggleTaskSkipped error — $e');
    }
  }

  /// Auto-detect helper: Marks task as completed if not already done.
  /// If [evidenceDocPath] is provided, verifies that document exists before dispatching write.
  static Future<void> autoCompleteTask(String taskId, {String? evidenceDocPath}) async {
    try {
      final task = allTasks.cast<BetaTaskItem?>().firstWhere(
        (t) => t?.id == taskId,
        orElse: () => null,
      );
      if (task == null) return;

      // Evidence check if required (e.g. Task 16 estate exports receipt)
      if (evidenceDocPath != null && evidenceDocPath.isNotEmpty) {
        final evidenceDoc = await _firestore.doc(evidenceDocPath).get();
        if (!evidenceDoc.exists) {
          debugPrint('[BetaChecklistService] Aborting autoCompleteTask for $taskId: evidence doc not found ($evidenceDocPath)');
          return;
        }
      }

      final docRef = _getDocRef();
      final doc = await docRef.get();

      if (!doc.exists) {
        // Schema bootstrap on missing document
        await docRef.set({
          'completed_tasks': [taskId],
          'skipped_tasks': <String>[],
          'total_tasks': allTasks.length,
          'created_at': FieldValue.serverTimestamp(),
          'last_synced_at': FieldValue.serverTimestamp(),
          'last_updated': FieldValue.serverTimestamp(),
        });
        _eventController.add(BetaChecklistEvent(taskId: taskId, taskTitle: task.title));
      } else {
        final data = doc.data() ?? {};
        final completed = List<String>.from(data['completed_tasks'] ?? []);
        if (!completed.contains(taskId)) {
          await docRef.update({
            'completed_tasks': FieldValue.arrayUnion([taskId]),
            'last_updated': FieldValue.serverTimestamp(),
          });
          _eventController.add(BetaChecklistEvent(taskId: taskId, taskTitle: task.title));
        }
      }
    } catch (e) {
      debugPrint('[BetaChecklistService] autoCompleteTask error: $e');
    }
  }

  static bool _hasSyncedThisSession = false;

  /// Visible for testing to reset session sync guard
  @visibleForTesting
  static void resetSessionSync() {
    _hasSyncedThisSession = false;
  }

  /// Retrospective Startup Sync Engine:
  /// Evaluates existing collection progress on account boot and updates the checklist
  /// document atomically without duplicate reads or polling loops.
  static Future<void> syncExistingAccountProgress() async {
    if (_hasSyncedThisSession) return;
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return;

    final uid = _userIdentifier;
    final docRef = _getDocRef();

    try {
      final doc = await docRef.get();
      final detected = <String>[];

      // 1. Manual entry check (limit 1)
      final manualCoinsSnap = await _firestore
          .collection('users').doc(uid).collection('coins')
          .where('source', isEqualTo: 'manual').limit(1).get();
      if (manualCoinsSnap.docs.isNotEmpty) detected.add('task_3_manual_entry');

      // 2. Currency check (limit 1)
      final currSnap = await _firestore
          .collection('users').doc(uid).collection('currency').limit(1).get();
      if (currSnap.docs.isNotEmpty) detected.add('task_12_currency');

      // 3. World items / foreign coins check (world_items OR is_foreign: true, limit 1 each)
      final worldSnap = await _firestore
          .collection('users').doc(uid).collection('world_items').limit(1).get();
      final foreignCoinSnap = await _firestore
          .collection('users').doc(uid).collection('coins')
          .where('is_foreign', isEqualTo: true).limit(1).get();
      if (worldSnap.docs.isNotEmpty || foreignCoinSnap.docs.isNotEmpty) {
        detected.add('task_13_world_items');
      }

      // 4. CSV upload check (source == 'csv' or review_queue, limit 1)
      final csvSnap = await _firestore
          .collection('users').doc(uid).collection('coins')
          .where('source', isEqualTo: 'csv').limit(1).get();
      final rqSnap = await _firestore
          .collection('users').doc(uid).collection('review_queue').limit(1).get();
      if (csvSnap.docs.isNotEmpty || rqSnap.docs.isNotEmpty) {
        detected.add('task_4_csv_upload');
      }

      // 5. Wishlist check (limit 1)
      final wishSnap = await _firestore
          .collection('users').doc(uid).collection('wishlist').limit(1).get();
      if (wishSnap.docs.isNotEmpty) detected.add('task_14_wishlist');

      // 6. Public Wishlists check (owner_email == uid or owner_uid == uid, limit 1)
      final pubSnap = await _firestore
          .collection('public_wishlists')
          .where('owner_email', isEqualTo: uid).limit(1).get();
      final pubUidSnap = user.uid != uid
          ? await _firestore.collection('public_wishlists').where('owner_uid', isEqualTo: user.uid).limit(1).get()
          : null;
      if (pubSnap.docs.isNotEmpty || (pubUidSnap != null && pubUidSnap.docs.isNotEmpty)) {
        detected.add('task_15_public_wishlist');
      }

      // 7. Estate export receipt check (limit 1)
      final estateSnap = await _firestore
          .collection('users').doc(uid).collection('estate_exports').limit(1).get();
      if (estateSnap.docs.isNotEmpty) detected.add('task_16_estate_report');

      // 8. Feedback check (user_id == user.uid, limit 1)
      final feedSnap = await _firestore
          .collection('beta_feedback')
          .where('user_id', isEqualTo: user.uid).limit(1).get();
      if (feedSnap.docs.isNotEmpty) detected.add('task_20_overall_feedback');

      if (!doc.exists) {
        // Combined schema bootstrap + detection write when document does not exist
        await docRef.set({
          'completed_tasks': detected,
          'skipped_tasks': <String>[],
          'total_tasks': allTasks.length,
          'created_at': FieldValue.serverTimestamp(),
          'last_synced_at': FieldValue.serverTimestamp(),
          'last_updated': FieldValue.serverTimestamp(),
        });
      } else {
        // Document exists: update timestamps and union new detections
        final Map<String, dynamic> updatePayload = {
          'last_synced_at': FieldValue.serverTimestamp(),
          'last_updated': FieldValue.serverTimestamp(),
        };
        if (detected.isNotEmpty) {
          updatePayload['completed_tasks'] = FieldValue.arrayUnion(detected);
        }
        await docRef.update(updatePayload);
      }

      _hasSyncedThisSession = true; // Mark session flag strictly on success
    } catch (e) {
      debugPrint('[BetaChecklistSync] ERROR: phase=retrospective_sync uid=$uid error=${e.toString()}');
    }
  }
}

class BetaChecklistEvent {
  final String taskId;
  final String taskTitle;

  const BetaChecklistEvent({
    required this.taskId,
    required this.taskTitle,
  });
}
