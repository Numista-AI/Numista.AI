import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

/// Bridges the Flutter UI to the numista hardware agent.
///
/// Scan TRIGGERS and saves use the hardware server's HTTP endpoints directly
/// (localhost:5000) to avoid Firestore client-write restrictions.
/// The hardware server itself writes to Firestore using its service account.
/// Live status POLLING also uses localhost:5000 Flask.
class HardwareService {
  static const String _statusUrl    = 'https://localhost:5000/get-status';
  static const String _startScanUrl = 'https://localhost:5000/start-scan';
  static const String _saveUrl      = 'https://localhost:5000/add-to-collection';
  static const String _pairUrl      = 'https://localhost:5000/pair';


  // Firestore fallback paths: not implemented, HTTP is used in all code paths
  // (keeping comment for future reference if offline-first support is needed)

  static final HardwareService _instance = HardwareService._internal();
  factory HardwareService() => _instance;
  HardwareService._internal();

  // ─── Pair Agent ───────────────────────────────────────────────────────────
  /// Posts to /pair on the local hardware server to auto-pair the agent.
  Future<bool> pairAgent(String userEmail) async {
    try {
      final response = await http
          .post(
            Uri.parse(_pairUrl),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'email': userEmail}),
          )
          .timeout(const Duration(seconds: 3));
      if (response.statusCode == 200) {
        debugPrint('[HW] ✅ Agent paired successfully');
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('[HW] /pair failed: $e');
      return false;
    }
  }

  // ─── Start Scan ───────────────────────────────────────────────────────────
  /// Posts to /start-scan on the local hardware server.
  /// Returns true if the command was accepted.
  Future<bool> startScan() async {
    try {
      final response = await http
          .post(Uri.parse(_startScanUrl))
          .timeout(const Duration(seconds: 5));
      if (response.statusCode == 200) {
        debugPrint('[HW] ✅ Scan started via HTTP /start-scan');
        return true;
      }
      debugPrint('[HW] /start-scan returned ${response.statusCode}');
      return false;
    } catch (e) {
      debugPrint('[HW] /start-scan failed: $e');
      return false;
    }
  }

  // ─── Confirm & Save ───────────────────────────────────────────────────────
  /// Posts coin data to /add-to-collection on the local hardware server.
  /// The server handles GCS upload + Firestore write via service account.
  /// Returns a coin ID string on success, null on failure.
  Future<String?> addToCollection(Map<String, dynamic> coinData) async {
    try {
      final response = await http
          .post(
            Uri.parse(_saveUrl),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(coinData),
          )
          .timeout(const Duration(seconds: 10));
      if (response.statusCode == 200) {
        final json = jsonDecode(response.body) as Map<String, dynamic>;
        debugPrint('[HW] ✅ addToCollection HTTP success: $json');
        return json['coin_id'] as String? ??
            'microscope_${DateTime.now().millisecondsSinceEpoch}';
      }
      debugPrint('[HW] /add-to-collection returned ${response.statusCode}');
      return null;
    } catch (e) {
      debugPrint('[HW] addToCollection error: $e');
      return null;
    }
  }

  // ─── Poll Status (localhost — for live sharpness bar) ─────────────────────
  /// Polls the local Flask server for real-time capture progress.
  /// Returns null if the agent is not reachable (server offline).
  Future<HardwareStatus?> getStatus() async {
    try {
      final response = await http
          .get(Uri.parse(_statusUrl))
          .timeout(const Duration(seconds: 3));

      if (response.statusCode == 200) {
        final json = jsonDecode(response.body) as Map<String, dynamic>;
        return HardwareStatus.fromJson(json);
      }
    } catch (_) {
      // Server not running or unreachable — caller handles null gracefully
    }
    return null;
  }

  // ─── Server Health Check ──────────────────────────────────────────────────
  Future<bool> isServerRunning() async {
    try {
      final resp = await http
          .get(Uri.parse(_statusUrl))
          .timeout(const Duration(seconds: 2));
      return resp.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // ─── Live Frame ───────────────────────────────────────────────────────────
  /// Fetches the latest annotated camera frame as raw JPEG bytes.
  /// Returns null if the agent is not scanning (204) or unreachable.
  Future<Uint8List?> fetchFrame() async {
    try {
      final resp = await http
          .get(Uri.parse('https://localhost:5000/frame'))
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
  /// Called when the user clicks "I've flipped the coin — Scan Reverse".
  /// Immediately clears the flip lockout on the hardware agent so the reverse
  /// capture begins without waiting for the 8-second auto-timer to expire.
  Future<bool> confirmFlip() async {
    try {
      final response = await http
          .post(Uri.parse('https://localhost:5000/confirm-flip'))
          .timeout(const Duration(seconds: 3));
      debugPrint('[HW] confirmFlip → ${response.statusCode}');
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('[HW] confirmFlip failed: $e');
      return false;
    }
  }

  // ─── List Cameras ─────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> listCameras() async {
    try {
      final response = await http
          .get(Uri.parse('https://localhost:5000/list-cameras'))
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
            Uri.parse('https://localhost:5000/set-camera'),
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
