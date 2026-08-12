import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:uuid/uuid.dart';
import 'auth_service.dart';

/// Bridges the Flutter UI to the numista hardware agent.
///
/// Scan TRIGGERS and saves use Firestore commands to avoid mixed-content
/// security blocks in HTTPS browsers.
/// Live status POLLING still uses localhost:5000 Flask.
class HardwareService {
  static const List<String> _baseUrls = [
    'https://localhost:8443',
    'https://localhost:5000',
  ];
  static String _activeBaseUrl = _baseUrls[0];

  static String get _baseUrl => _activeBaseUrl;

  static final HardwareService _instance = HardwareService._internal();
  factory HardwareService() => _instance;
  HardwareService._internal();

  // ─── Pair Agent ───────────────────────────────────────────────────────────
  /// Posts to /pair on the local hardware server to auto-pair the agent.
  Future<bool> pairAgent(String userEmail) async {
    for (final base in _baseUrls) {
      try {
        final response = await http
            .post(
              Uri.parse('$base/pair'),
              headers: {'Content-Type': 'application/json'},
              body: jsonEncode({'email': userEmail}),
            )
            .timeout(const Duration(seconds: 2));
        if (response.statusCode == 200) {
          _activeBaseUrl = base;
          debugPrint('[HW] ✅ Agent paired successfully on $base');
          return true;
        }
      } catch (e) {
        debugPrint('[HW] /pair failed on $base: $e');
      }
    }
    return false;
  }

  // ─── Start Scan ───────────────────────────────────────────────────────────
  /// Writes a 'start_scan' command to Firestore.
  /// The local hardware agent listens for this and triggers the capture worker.
  Future<bool> startScan() async {
    try {
      final email = AuthService.userEmail;
      await FirebaseFirestore.instance
          .collection('commands/$email/pending')
          .add({
        'command': 'start_scan',
        'timestamp': FieldValue.serverTimestamp(),
      });
      debugPrint('[HW] ✅ Scan started via Firestore command');
      return true;
    } catch (e) {
      debugPrint('[HW] ❌ Failed to write start_scan command: $e');
      return false;
    }
  }

  // ─── Confirm & Save ───────────────────────────────────────────────────────
  /// Writes a 'save_coin' command to Firestore with the coin data.
  /// The agent handles GCS upload + Firestore write via service account.
  /// Returns the pre-generated coin ID.
  Future<String?> addToCollection(Map<String, dynamic> coinData) async {
    try {
      final email = AuthService.userEmail;
      final coinId = const Uuid().v4();

      // Ensure the ID is in the data so the agent uses it
      final data = Map<String, dynamic>.from(coinData);
      data['id'] = coinId;

      await FirebaseFirestore.instance
          .collection('commands/$email/pending')
          .add({
        'command': 'save_coin',
        'data': data,
        'timestamp': FieldValue.serverTimestamp(),
      });

      debugPrint('[HW] ✅ Save command written to Firestore');
      return coinId;
    } catch (e) {
      debugPrint('[HW] ❌ Failed to write save_coin command: $e');
      return null;
    }
  }

  // ─── Poll Status (localhost — for live sharpness bar) ─────────────────────
  /// Polls the local Flask server for real-time capture progress.
  /// Returns null if the agent is not reachable (server offline).
  Future<HardwareStatus?> getStatus() async {
    for (final base in _baseUrls) {
      try {
        final response = await http
            .get(Uri.parse('$base/get-status'))
            .timeout(const Duration(seconds: 2));

        if (response.statusCode == 200) {
          _activeBaseUrl = base;
          final json = jsonDecode(response.body) as Map<String, dynamic>;
          return HardwareStatus.fromJson(json);
        }
      } catch (_) {
        // Probe next base URL
      }
    }
    return null;
  }

  // ─── Server Health Check ──────────────────────────────────────────────────
  Future<bool> isServerRunning() async {
    for (final base in _baseUrls) {
      try {
        final resp = await http
            .get(Uri.parse('$base/get-status'))
            .timeout(const Duration(seconds: 2));
        if (resp.statusCode == 200) {
          _activeBaseUrl = base;
          return true;
        }
      } catch (_) {
        // Probe next
      }
    }
    return false;
  }

  // ─── Live Frame ───────────────────────────────────────────────────────────
  /// Fetches the latest annotated camera frame as raw JPEG bytes.
  /// Returns null if the agent is not scanning (204) or unreachable.
  Future<Uint8List?> fetchFrame() async {
    try {
      final resp = await http
          .get(Uri.parse('$_baseUrl/frame'))
          .timeout(const Duration(milliseconds: 600));
      if (resp.statusCode == 200 && resp.bodyBytes.isNotEmpty) {
        return resp.bodyBytes;
      }
    } catch (_) {
      // Not scanning or unreachable — caller handles null gracefully
    }
    return null;
  }

  // ─── Confirm Flip ─────────────────────────────────────────────────────────
  /// Writes a 'confirm_flip' command to Firestore.
  Future<bool> confirmFlip() async {
    try {
      final email = AuthService.userEmail;
      await FirebaseFirestore.instance
          .collection('commands/$email/pending')
          .add({
        'command': 'confirm_flip',
        'timestamp': FieldValue.serverTimestamp(),
      });
      debugPrint('[HW] ✅ Flip confirmed via Firestore');
      return true;
    } catch (e) {
      debugPrint('[HW] ❌ Failed to write confirm_flip command: $e');
      return false;
    }
  }

  // ─── List Cameras ─────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> listCameras() async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl/list-cameras'))
          .timeout(const Duration(seconds: 3));
      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      }
    } catch (e) {
      debugPrint('[HW] /list-cameras failed: $e');
    }
    return {'cameras': <int>[], 'active': -1};
  }

  // ─── Set Camera Index ─────────────────────────────────────────────────────
  Future<bool> setCameraIndex(int index) async {
    try {
      final response = await http
          .post(
            Uri.parse('$_baseUrl/set-camera'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'index': index}),
          )
          .timeout(const Duration(seconds: 3));
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('[HW] /set-camera failed: $e');
      return false;
    }
  }
}



// ─── Data Model ───────────────────────────────────────────────────────────────
class HardwareStatus {
  final bool isActive;
  final String currentStep;
  final int sharpness;
  final int maxSharpness;
  final double motion;
  final bool waitingForFlip;
  final String statusMessage;
  final String? error;
  final Map<String, dynamic>? lastReport;
  final double? captureCountdownRemaining;
  final double? flipTimeRemaining;
  final String? pairedEmail;

  const HardwareStatus({
    required this.isActive,
    required this.currentStep,
    required this.sharpness,
    required this.maxSharpness,
    required this.motion,
    required this.waitingForFlip,
    required this.statusMessage,
    this.error,
    this.lastReport,
    this.captureCountdownRemaining,
    this.flipTimeRemaining,
    this.pairedEmail,
  });

  factory HardwareStatus.fromJson(Map<String, dynamic> j) {
    return HardwareStatus(
      isActive: j['is_active'] as bool? ?? false,
      currentStep: j['current_step'] as String? ?? 'IDLE',
      sharpness: (j['sharpness'] as num?)?.toInt() ?? 0,
      maxSharpness: (j['max_sharpness'] as num?)?.toInt() ?? 0,
      motion: (j['motion'] as num?)?.toDouble() ?? 0.0,
      waitingForFlip: j['waiting_for_flip'] as bool? ?? false,
      statusMessage: j['status_message'] as String? ?? '',
      error: j['error'] as String?,
      lastReport: j['last_report'] as Map<String, dynamic>?,
      captureCountdownRemaining:
          (j['capture_countdown_remaining'] as num?)?.toDouble(),
      flipTimeRemaining: (j['flip_time_remaining'] as num?)?.toDouble(),
      pairedEmail: j['paired_email'] as String?,
    );
  }

  bool get isScanComplete =>
      !isActive && lastReport != null && currentStep != 'IDLE';

  double get sharpnessPct =>
      maxSharpness > 0 ? (sharpness / maxSharpness).clamp(0.0, 1.0) : 0.0;

  /// True while the pre-capture countdown ring should be shown.
  bool get isCountingDown => captureCountdownRemaining != null;

  /// Progress fraction (0.0 → 1.0) of the pre-capture ring (fills as time runs out).
  double get captureCountdownPct =>
      captureCountdownRemaining != null
          ? 1.0 - (captureCountdownRemaining! / 3.0).clamp(0.0, 1.0)
          : 0.0;

  /// Progress fraction of the flip-coin ring.
  double get flipCountdownPct =>
      flipTimeRemaining != null
          ? 1.0 - (flipTimeRemaining! / 8.0).clamp(0.0, 1.0)
          : 0.0;
}
