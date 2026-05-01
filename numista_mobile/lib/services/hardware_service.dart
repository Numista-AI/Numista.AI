import 'dart:async';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

/// Bridges the Flutter UI to the numista hardware agent.
///
/// Scan TRIGGERS use Firestore (HTTPS-safe, works from numista.ai).
/// Live status POLLING uses localhost:5000 Flask (available when agent is
/// running on the same machine as the browser, which is always true for
/// the microscope use case).
class HardwareService {
  static const String _statusUrl = 'http://localhost:5000/get-status';
  static const String _userEmail = 'eric@numista.ai';
  static const String _commandsPath = 'commands/$_userEmail/pending';
  static const String _resultsPath = 'commands/$_userEmail/results';

  static final HardwareService _instance = HardwareService._internal();
  factory HardwareService() => _instance;
  HardwareService._internal();

  final FirebaseFirestore _db = FirebaseFirestore.instance;

  // ─── Write a command to Firestore ─────────────────────────────────────────
  Future<bool> _writeCommand(String command, [Map<String, dynamic>? data]) async {
    try {
      final payload = <String, dynamic>{
        'command': command,
        'created_at': FieldValue.serverTimestamp(),
        ...?data != null ? {'data': data} : null,
      };
      await _db.collection(_commandsPath).add(payload);
      debugPrint('[HW] Command written → $command');
      return true;
    } catch (e) {
      debugPrint('[HW] Failed to write command: $e');
      return false;
    }
  }

  // ─── Start Scan ───────────────────────────────────────────────────────────
  /// Writes a start_scan command to Firestore.
  /// The local hardware agent picks this up and fires the microscope.
  /// Returns true if the command was written successfully.
  Future<bool> startScan() => _writeCommand('start_scan');

  // ─── Confirm & Save ───────────────────────────────────────────────────────
  /// Writes a save_coin command to Firestore with the confirmed coin data.
  /// The agent uploads images to GCS, writes the coin to Firestore,
  /// then writes a result doc to commands/{user}/results.
  /// Returns the Firestore coin ID by listening to the results collection.
  Future<String?> addToCollection(Map<String, dynamic> coinData) async {
    try {
      // Write the save command
      await _writeCommand('save_coin', coinData);

      // Wait for the agent to write back a result (up to 30 seconds)
      final completer = Completer<String?>();
      StreamSubscription? sub;

      sub = _db
          .collection(_resultsPath)
          .orderBy('saved_at', descending: true)
          .limit(1)
          .snapshots()
          .listen((snap) {
        if (snap.docs.isNotEmpty) {
          final doc = snap.docs.first;
          final firestoreId = doc['firestore_id'] as String?;
          if (!completer.isCompleted && firestoreId != null) {
            completer.complete(firestoreId);
            sub?.cancel();
          }
        }
      });

      // Timeout after 30 seconds
      Future.delayed(const Duration(seconds: 30), () {
        if (!completer.isCompleted) {
          completer.complete(null);
          sub?.cancel();
        }
      });

      return completer.future;
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
