import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../constants.dart';
import '../models/estate_models.dart';

// Platform-conditional imports for PDF opening
import 'estate_report_service_web.dart'
    if (dart.library.io) 'estate_report_service_mobile.dart' as platform;

/// Result of a report generation call.
class EstateReportResult {
  final Uint8List pdfBytes;
  final String reportId;
  const EstateReportResult({required this.pdfBytes, required this.reportId});
}

/// Service for generating estate report PDFs and retrieving report history.
class EstateReportService {
  static const String _baseUrl = kApiBaseUrl;

  /// Calls the backend to generate a PDF report.
  /// Returns [EstateReportResult] with raw PDF bytes and report ID on success.
  static Future<EstateReportResult> generateReport({
    required String uid,
    required EstateProfile profile,
    required String mode, // 'living_inventory' | 'estate_settlement'
    String? dateOfDeath,  // ISO date, estate_settlement only
    bool includePhotos = true,
  }) async {
    final body = {
      'uid': uid,
      'mode': mode,
      'include_photos': includePhotos,
      'owner_name': profile.ownerName,
      'owner_email': profile.ownerEmail,
      'jurisdiction': profile.jurisdiction,
      'marital_status': profile.maritalStatus,
      'will_or_trust_status': profile.willOrTrustStatus,
      'attorney_name': profile.attorneyName,
      'attorney_email': profile.attorneyEmail,
      'attorney_firm': profile.attorneyFirm,
      'attorney_phone': profile.attorneyPhone,
      'executor_name': profile.executorName,
      'executor_email': profile.executorEmail,
      'executor_phone': profile.executorPhone,
      'beneficiaries': profile.beneficiaries.map((b) => b.toMap()).toList(),
      'date_of_death': dateOfDeath,
    };

    final response = await http.post(
      Uri.parse('$_baseUrl/generate_estate_report'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    ).timeout(
      const Duration(seconds: 240),
      onTimeout: () => throw Exception(
          'Report generation timed out. Your collection may be very large — please try again.'),
    );

    // Server errors come back as JSON with an 'error' key
    if (response.statusCode != 200) {
      String errorMsg = 'Server error (${response.statusCode})';
      try {
        final json = jsonDecode(response.body) as Map<String, dynamic>;
        errorMsg = json['error']?.toString() ?? errorMsg;
      } catch (_) {}
      throw Exception(errorMsg);
    }

    final contentType = response.headers['content-type'] ?? '';
    if (!contentType.contains('application/pdf')) {
      // Try to parse as error JSON
      try {
        final json = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(json['error']?.toString() ?? 'Unexpected response from server');
      } catch (_) {
        throw Exception('Unexpected response from server');
      }
    }

    final reportId = response.headers['x-report-id'] ?? '';
    return EstateReportResult(pdfBytes: response.bodyBytes, reportId: reportId);
  }

  /// Builds the attorney portal URL for a given uid + report ID.
  static String attorneyPortalUrl(String uid, String reportId) =>
      'https://numista.ai/attorney?uid=${Uri.encodeComponent(uid)}&token=${Uri.encodeComponent(reportId)}';

  /// Copies the attorney portal link to clipboard.
  static Future<void> copyAttorneyLink(String uid, String reportId) async {
    await Clipboard.setData(
        ClipboardData(text: attorneyPortalUrl(uid, reportId)));
  }

  /// Fetches the list of previously generated estate reports from Firestore.
  static Future<List<EstateReportRecord>> getReportHistory(String uid) async {
    try {
      final snap = await FirebaseFirestore.instance
          .collection('users')
          .doc(uid)
          .collection('estate_reports')
          .orderBy('generated_at', descending: true)
          .limit(50)
          .get();
      return snap.docs.map((d) => EstateReportRecord.fromFirestore(d)).toList();
    } catch (_) {
      return [];
    }
  }

  /// Opens the PDF bytes using platform-appropriate method:
  /// - Web: creates a Blob URL and opens in new tab
  /// - Mobile: saves to temp dir and opens with url_launcher
  static Future<void> openPdf(Uint8List pdfBytes, String filename) async {
    await platform.openPdfPlatform(pdfBytes, filename);
  }
}
