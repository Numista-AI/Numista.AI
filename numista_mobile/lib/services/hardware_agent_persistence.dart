import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:url_launcher/url_launcher.dart';
import 'hardware_service.dart';

/// Wires [HardwareService] `hardware_agent.installed` dual-persistence to
/// Firestore (`users/{uid}`) and custom-scheme launcher (`numista-agent://launch`)
/// cleanly outside unit test dependencies.
class HardwareAgentPersistence {
  HardwareAgentPersistence._();

  static bool _registered = false;

  /// Registers Firestore loader/writer callbacks and `url_launcher` handler
  /// on [HardwareService].
  static void ensureRegistered() {
    if (_registered) return;
    _registered = true;

    HardwareService.agentUriLauncher = () async {
      final uri = Uri.parse('numista-agent://launch');
      return launchUrl(uri, mode: LaunchMode.externalApplication);
    };

    HardwareService.firestoreAgentInstalledLoader = () async {
      try {
        final uid = FirebaseAuth.instance.currentUser?.uid;
        if (uid == null || uid.isEmpty) return false;
        final snap = await FirebaseFirestore.instance
            .collection('users')
            .doc(uid)
            .get();
        final data = snap.data();
        final hw = data?['hardware_agent'];
        if (hw is Map && hw['installed'] == true) {
          return true;
        }
      } catch (_) {}
      return false;
    };

    HardwareService.firestoreAgentInstalledWriter =
        (Map<String, dynamic> payload) async {
      try {
        final uid = FirebaseAuth.instance.currentUser?.uid;
        if (uid == null || uid.isEmpty) return;
        await FirebaseFirestore.instance.collection('users').doc(uid).set({
          'hardware_agent': {
            ...payload,
            'last_seen_at': FieldValue.serverTimestamp(),
          },
        }, SetOptions(merge: true));
      } catch (_) {}
    };
  }
}
