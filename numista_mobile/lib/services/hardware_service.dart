import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:shared_preferences/shared_preferences.dart';
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
    'http://127.0.0.1:5000',
    'http://localhost:5000',
  ];
  static String _activeBaseUrl = _baseUrls[0];

  static bool _mockEnabled = false;
  static bool _mockServerOnline = false;
  static bool? _mockAgentInstalled;
  static List<Map<String, dynamic>> _mockCameraDetails = const [];
  static int _mockActiveCameraIdx = -1;
  static double _mockSharpness = 0.0;
  static String? _mockScanStep;
  static String? _mockLastError;

  static void setMockHardwareState({
    bool enabled = true,
    bool serverOnline = false,
    bool? agentInstalled,
    List<Map<String, dynamic>>? cameraDetails,
    int activeCameraIdx = -1,
    double sharpness = 0.0,
    String? scanStep,
    String? lastError,
  }) {
    _mockEnabled = enabled;
    _mockServerOnline = serverOnline;
    _mockAgentInstalled = agentInstalled;
    _mockCameraDetails = cameraDetails ?? const [];
    _mockActiveCameraIdx = activeCameraIdx;
    _mockSharpness = sharpness;
    _mockScanStep = scanStep;
    _mockLastError = lastError;
  }

  static void clearMockHardwareState() {
    _mockEnabled = false;
    _mockServerOnline = false;
    _mockAgentInstalled = null;
    _mockCameraDetails = const [];
    _mockActiveCameraIdx = -1;
    _mockSharpness = 0.0;
    _mockScanStep = null;
    _mockLastError = null;
  }

  static bool get isMockEnabled => _mockEnabled;
  static bool get mockServerOnline => _mockServerOnline;
  static double get mockSharpness => _mockSharpness;
  static String? get mockScanStep => _mockScanStep;
  static String? get mockLastError => _mockLastError;

  static const String prefAgentInstalled = 'hardware_agent_installed';
  static const String prefAgentLastCamera = 'hardware_agent_last_camera';

  static Future<bool> Function()? firestoreAgentInstalledLoader;
  static Future<void> Function(Map<String, dynamic> data)?
      firestoreAgentInstalledWriter;
  static Future<bool> Function()? agentUriLauncher;
  static Uri? lastLaunchedAgentUri;

  /// Broadcasts live Microscope state & action hooks to Morgan Co-Pilot
  /// (`MorganScreenStateRegistry` & `MorganProactiveRescueObserver`) without
  /// introducing circular UI imports.
  static final ValueNotifier<Map<String, dynamic>> liveMicroscopeState =
      ValueNotifier<Map<String, dynamic>>({
    'isHydrated': false,
    'microscopeConfigured': false,
    'serverOnline': false,
    'agentInstalledBefore': false,
    'availableCameras': <Map<String, dynamic>>[],
    'activeCameraIdx': -1,
    'activeCameraName': '',
    'scanStep': 'IDLE',
    'sharpness': 0.0,
    'waitingForFlip': false,
    'lastError': null,
  });

  static final Map<String, Object?> registeredUiKeys = <String, Object?>{};
  static final Map<String, Future<void> Function([Map<String, dynamic>?])>
      registeredUiInvokers =
      <String, Future<void> Function([Map<String, dynamic>?])>{};

  static void publishMicroscopeState(Map<String, dynamic> patch) {
    final next = Map<String, dynamic>.from(liveMicroscopeState.value)
      ..addAll(patch);
    liveMicroscopeState.value = next;
  }

  /// Invokes `numista-agent://launch` synchronously within a user tap gesture.
  static Future<bool> launchDesktopAgent() async {
    final uri = Uri.parse('numista-agent://launch');
    lastLaunchedAgentUri = uri;
    final launcher = agentUriLauncher;
    if (launcher != null) {
      try {
        return await launcher();
      } catch (_) {
        return false;
      }
    }
    return false;
  }

  static Future<bool> isAgentInstalledLocal() async {
    if (_mockEnabled && _mockAgentInstalled != null) {
      return _mockAgentInstalled!;
    }
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(prefAgentInstalled) ?? false;
  }

  static Future<bool> wasAgentEverInstalled() async {
    if (_mockEnabled && _mockAgentInstalled != null) {
      return _mockAgentInstalled!;
    }
    final prefs = await SharedPreferences.getInstance();
    if (prefs.getBool(prefAgentInstalled) ?? false) {
      return true;
    }
    try {
      final remote = await firestoreAgentInstalledLoader?.call() ?? false;
      if (remote) {
        await prefs.setBool(prefAgentInstalled, true);
        return true;
      }
    } catch (_) {}
    return false;
  }

  static Future<void> markAgentInstalled({String? lastCameraName}) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(prefAgentInstalled, true);
    await prefs.setBool(prefMicroscopeEnabled, true);
    if (lastCameraName != null && lastCameraName.isNotEmpty) {
      await prefs.setString(prefAgentLastCamera, lastCameraName);
    }
    try {
      await firestoreAgentInstalledWriter?.call({
        'installed': true,
        'version': '2.1',
        if (lastCameraName != null && lastCameraName.isNotEmpty)
          'last_camera_name': lastCameraName,
      });
    } catch (_) {}
  }

  static String get _baseUrl => _activeBaseUrl;

  static final HardwareService _instance = HardwareService._internal();
  factory HardwareService() => _instance;
  HardwareService._internal();

  static const String prefMicroscopeEnabled = 'microscope_enabled';

  static Future<bool> isMicroscopeConfigured() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(prefMicroscopeEnabled) ?? false;
  }

  static Future<void> setMicroscopeConfigured(bool enabled) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(prefMicroscopeEnabled, enabled);
  }

  // ─── Pair Agent ───────────────────────────────────────────────────────────
  /// Posts to /pair on the local hardware server to auto-pair the agent.
  Future<bool> pairAgent(String userEmail) async {
    if (!(await isMicroscopeConfigured())) {
      return false;
    }
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
    if (!(await isMicroscopeConfigured())) {
      return null;
    }
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
  Future<bool> isServerRunning({bool bypassConfigCheck = false}) async {
    if (_mockEnabled) {
      return _mockServerOnline;
    }
    if (!bypassConfigCheck && !(await isMicroscopeConfigured())) {
      return false;
    }
    for (final base in _baseUrls) {
      try {
        final resp = await http
            .get(Uri.parse('$base/get-status'))
            .timeout(const Duration(seconds: 2));
        if (resp.statusCode == 200) {
          _activeBaseUrl = base;
          await markAgentInstalled();
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
    if (!(await isMicroscopeConfigured())) {
      return null;
    }
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
  Future<Map<String, dynamic>> listCameras({bool bypassConfigCheck = false}) async {
    if (_mockEnabled) {
      final filteredDetails = _mockCameraDetails
          .where((d) => d['blocked'] != true)
          .toList(growable: false);
      final camIndices = filteredDetails
          .map((d) => d['index'])
          .whereType<int>()
          .toList(growable: false);
      int active = _mockActiveCameraIdx;
      if (active < 0 || !camIndices.contains(active)) {
        final rec = filteredDetails.where((d) => d['is_recommended'] == true);
        if (rec.isNotEmpty) {
          active = rec.first['index'] as int? ?? -1;
        } else if (camIndices.isNotEmpty) {
          active = camIndices.first;
        } else {
          active = -1;
        }
      }
      String activeName = '';
      for (final d in filteredDetails) {
        if (d['index'] == active) {
          activeName = d['name']?.toString() ?? '';
          break;
        }
      }
      return {
        'cameras': camIndices,
        'camera_details': _mockCameraDetails,
        'active': active,
        'active_name': activeName,
      };
    }
    if (!bypassConfigCheck && !(await isMicroscopeConfigured())) {
      return {
        'cameras': <int>[],
        'camera_details': <Map<String, dynamic>>[],
        'active': -1,
        'active_name': '',
      };
    }
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl/list-cameras'))
          .timeout(const Duration(seconds: 3));
      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body) as Map<String, dynamic>;
        final activeName = decoded['active_name']?.toString();
        await markAgentInstalled(lastCameraName: activeName);
        return decoded;
      }
    } catch (e) {
      debugPrint('[HW] /list-cameras failed: $e');
    }
    return {
      'cameras': <int>[],
      'camera_details': <Map<String, dynamic>>[],
      'active': -1,
      'active_name': '',
    };
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
