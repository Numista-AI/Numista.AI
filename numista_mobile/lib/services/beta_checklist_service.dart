import 'package:cloud_firestore/cloud_firestore.dart';
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

  static DocumentReference<Map<String, dynamic>> _getDocRef() {
    final userEmail = AuthService.currentUserEmail.isNotEmpty
        ? AuthService.currentUserEmail
        : 'guest_demo_user';
    return _firestore
        .collection('users')
        .doc(userEmail)
        .collection('settings')
        .doc('beta_checklist');
  }

  /// Stream of checklist state from `users/{email}/settings/beta_checklist`.
  static Stream<DocumentSnapshot<Map<String, dynamic>>> getChecklistStream() {
    return _getDocRef().snapshots();
  }

  /// Toggle task completed state.
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
        'last_updated': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));
    } catch (e) {
      debugPrint('BetaChecklistService: toggleTaskCompleted error — $e');
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
        'last_updated': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));
    } catch (e) {
      debugPrint('BetaChecklistService: toggleTaskSkipped error — $e');
    }
  }

  /// Auto-detect helper: Marks task as completed if not already done.
  static Future<void> autoCompleteTask(String taskId) async {
    await toggleTaskCompleted(taskId, true);
  }
}
