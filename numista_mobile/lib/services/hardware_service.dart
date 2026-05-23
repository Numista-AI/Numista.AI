import 'dart:async';
import 'package:cloud_firestore/cloud_firestore.dart';
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
  static const String _statusUrl    = 'http://localhost:5000/get-status';
  static const String _startScanUrl = 'http://localhost:5000/start-scan';
  static const String _saveUrl      = 'http://localhost:5000/add-to-collection';

  // Firestore fallback (used only when HTTP is unreachable, e.g. production)
  static const String _userEmail     = 'eric@numista.ai';
  static const String _commandsPath  = 'commands/$_userEmail/pending';
  static const String _resultsPath   = 'commands/$_userEmail/results';

  static final HardwareService _instance = HardwareService._internal();
  factory HardwareService() => _instance;
  HardwareService._internal();

  final FirebaseFirestore _db = FirebaseFirestore.instance;

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
