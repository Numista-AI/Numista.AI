import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/estate_models.dart';

/// Firestore CRUD for the estate profile document.
/// Document path: users/{uid}/estate_profile/data
class EstateProfileService {
  static const _profileDoc = 'data';

  static DocumentReference<Map<String, dynamic>> _ref(String uid) =>
      FirebaseFirestore.instance
          .collection('users')
          .doc(uid)
          .collection('estate_profile')
          .doc(_profileDoc);

  /// Fetches the estate profile once. Returns null if not yet created.
  static Future<EstateProfile?> getProfile(String uid) async {
    try {
      final snap = await _ref(uid).get();
      if (!snap.exists) return null;
      return EstateProfile.fromFirestore(snap);
    } catch (e) {
      return null;
    }
  }

  /// Saves (creates or overwrites) the estate profile.
  static Future<void> saveProfile(String uid, EstateProfile profile) async {
    await _ref(uid).set(profile.toFirestore(), SetOptions(merge: true));
  }

  /// Updates only the beneficiaries list.
  static Future<void> updateBeneficiaries(
      String uid, List<EstateBeneficiary> beneficiaries) async {
    await _ref(uid).update({
      'beneficiaries': beneficiaries.map((b) => b.toMap()).toList(),
    });
  }

  /// Real-time stream of profile changes.
  static Stream<EstateProfile?> watchProfile(String uid) {
    return _ref(uid).snapshots().map((snap) {
      if (!snap.exists) return null;
      return EstateProfile.fromFirestore(snap);
    });
  }
}
