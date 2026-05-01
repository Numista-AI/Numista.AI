import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

/// Result returned from the Cloud Run scan_service endpoint.
class ScanResult {
  final String programId;
  final String userId;
  final double? pageConfidence;
  final Map<String, dynamic> coins; // coin_id → true|false|null (or Map for varieties)
  final bool firestoreWritten;
  final int wishlistAdded;
  final String? errorMessage;

  const ScanResult({
    required this.programId,
    required this.userId,
    required this.coins,
    this.pageConfidence,
    this.firestoreWritten = false,
    this.wishlistAdded = 0,
    this.errorMessage,
  });

  bool get success => errorMessage == null;

  /// How many coins were detected as owned (checked).
  int get ownedCount {
    int count = 0;
    for (final v in coins.values) {
      if (v == true) count++;
      if (v is Map) {
        count += v.values.where((mv) => mv == true).length;
      }
    }
    return count;
  }

  /// How many coins were detected as NOT owned (unchecked).
  int get notOwnedCount {
    int count = 0;
    for (final v in coins.values) {
      if (v == false) count++;
      if (v is Map) {
        count += v.values.where((mv) => mv == false).length;
      }
    }
    return count;
  }

  /// How many coins were unreadable (null).
  int get unreadableCount {
    int count = 0;
    for (final v in coins.values) {
      if (v == null) count++;
      if (v is Map) {
        count += v.values.where((mv) => mv == null).length;
      }
    }
    return count;
  }

  factory ScanResult.fromJson(Map<String, dynamic> json) {
    return ScanResult(
      programId: json['program_id'] ?? '',
      userId: json['user_id'] ?? '',
      coins: Map<String, dynamic>.from(json['coins'] ?? {}),
      pageConfidence: (json['page_confidence'] as num?)?.toDouble(),
      firestoreWritten: json['firestore_written'] ?? false,
      wishlistAdded: (json['wishlist_added'] as num?)?.toInt() ?? 0,
    );
  }

  factory ScanResult.error(String message) {
    return ScanResult(
      programId: '',
      userId: '',
      coins: {},
      errorMessage: message,
    );
  }
}

/// Sends a checklist image to the Numista.AI Cloud Run scan endpoint.
class ChecklistScanService {
  static const String _baseUrl =
      'https://numista-backend-568985927038.us-central1.run.app';

  /// Posts [imageFile] to /api/analyze_checklist with the given [programId] and [userId].
  /// [pageNumber] and [totalPages] enable server-side coin chunking to reduce token usage.
  /// Returns a [ScanResult] — check [ScanResult.success] before using the data.
  static Future<ScanResult> scanChecklist({
    required File imageFile,
    required String programId,
    required String userId,
    int pageNumber = 1,
    int totalPages = 1,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/analyze_checklist');
      final request = http.MultipartRequest('POST', uri);

      request.fields['program_id'] = programId;
      request.fields['user_id'] = userId;
      request.fields['page_number'] = pageNumber.toString();
      request.fields['total_pages'] = totalPages.toString();

      final mimeType = _mimeTypeFromPath(imageFile.path);
      final parts = mimeType.split('/');
      request.files.add(await http.MultipartFile.fromPath(
        'image',
        imageFile.path,
        contentType: MediaType(parts[0], parts.length > 1 ? parts[1] : 'jpeg'),
      ));

      final streamed = await request.send().timeout(
        const Duration(seconds: 120),
        onTimeout: () => throw Exception('Request timed out after 120s'),
      );

      final body = await streamed.stream.bytesToString();

      if (streamed.statusCode == 200) {
        final json = jsonDecode(body) as Map<String, dynamic>;
        return ScanResult.fromJson(json);
      } else {
        final errorDetail = _extractError(body);
        return ScanResult.error('Server error ${streamed.statusCode}: $errorDetail');
      }
    } on SocketException {
      return ScanResult.error('No internet connection. Please check your network.');
    } catch (e) {
      return ScanResult.error('Scan failed: ${e.toString()}');
    }
  }

  /// Quick health check — returns true if the service is reachable.
  static Future<bool> isHealthy() async {
    try {
      final resp = await http
          .get(Uri.parse('$_baseUrl/'))
          .timeout(const Duration(seconds: 10));
      return resp.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static String _mimeTypeFromPath(String path) {
    final lower = path.toLowerCase();
    if (lower.endsWith('.png')) return 'image/png';
    if (lower.endsWith('.jpg') || lower.endsWith('.jpeg')) return 'image/jpeg';
    if (lower.endsWith('.webp')) return 'image/webp';
    return 'image/jpeg'; // safe default
  }

  static String _extractError(String body) {
    try {
      final json = jsonDecode(body);
      return json['error'] ?? json['description'] ?? body;
    } catch (_) {
      return body.length > 200 ? '${body.substring(0, 200)}...' : body;
    }
  }
}
