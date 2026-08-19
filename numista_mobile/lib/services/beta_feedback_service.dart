// lib/services/beta_feedback_service.dart
//
// All feedback writes go through the Cloud Run callable endpoint.
// This service is a thin HTTP client over /api/feedback/callable.
// It NEVER writes directly to Firestore.

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import '../constants/feedback_constants.dart';
import '../constants.dart' show kApiBaseUrl;

// ---------------------------------------------------------------------------
// Data models
// ---------------------------------------------------------------------------

enum FeedbackTriggerReason {
  manualFAB,
  scanTimeout,
  pcgsImportError,
  addCoinAbandoned,
  milestoneAchieved,
}

class CheckResult {
  final bool allowed;
  final bool interviewMode;
  final String? lockId;
  final String? draftDocId;
  final String? reason; // 'throttled' | 'already_locked' | 'rate_limited'

  const CheckResult({
    required this.allowed,
    required this.interviewMode,
    this.lockId,
    this.draftDocId,
    this.reason,
  });

  factory CheckResult.fromJson(Map<String, dynamic> j) => CheckResult(
        allowed: j['allowed'] as bool? ?? false,
        interviewMode: j['interview_mode'] as bool? ?? false,
        lockId: j['lock_id'] as String?,
        draftDocId: j['draft_doc_id'] as String?,
        reason: j['reason'] as String?,
      );
}

class ExtractionResult {
  final String extractionStatus; // 'COMPLETE' | 'FAILED'
  final String? issueType;
  final String? severityEstimate;
  final String? affectedFeature;
  final String? userIntent;
  final String? reproductionSteps;
  final String? morganSummary;
  final int redactionApplied;

  const ExtractionResult({
    required this.extractionStatus,
    this.issueType,
    this.severityEstimate,
    this.affectedFeature,
    this.userIntent,
    this.reproductionSteps,
    this.morganSummary,
    this.redactionApplied = 0,
  });

  bool get isComplete => extractionStatus == 'COMPLETE';

  factory ExtractionResult.fromJson(Map<String, dynamic> j) => ExtractionResult(
        extractionStatus: j['extraction_status'] as String? ?? 'FAILED',
        issueType: j['issue_type'] as String?,
        severityEstimate: j['severity_estimate'] as String?,
        affectedFeature: j['affected_feature'] as String?,
        userIntent: j['user_intent'] as String?,
        reproductionSteps: j['reproduction_steps'] as String?,
        morganSummary: j['morgan_summary'] as String?,
        redactionApplied: j['redaction_applied'] as int? ?? 0,
      );
}

class SubmitResult {
  final String? docId;
  final String status; // 'filed' | 'duplicate' | 'error'

  const SubmitResult({this.docId, required this.status});

  factory SubmitResult.fromJson(Map<String, dynamic> j) => SubmitResult(
        docId: j['doc_id'] as String?,
        status: j['status'] as String? ?? 'error',
      );
}

class UploadUrlResult {
  final String signedUrl;
  final String objectPath;

  const UploadUrlResult({required this.signedUrl, required this.objectPath});

  factory UploadUrlResult.fromJson(Map<String, dynamic> j) => UploadUrlResult(
        signedUrl: j['signed_url'] as String,
        objectPath: j['object_path'] as String,
      );
}

// Represents a single message in the transcript
class TranscriptMessage {
  final String role; // 'user' | 'assistant'
  final String message;
  final DateTime ts;

  const TranscriptMessage({
    required this.role,
    required this.message,
    required this.ts,
  });

  Map<String, dynamic> toJson() => {
        'role': role,
        'message': message,
        'ts': ts.toIso8601String(),
      };
}

// Full payload for SUBMIT mode
class MorganSubmitPayload {
  final List<TranscriptMessage> transcript;
  final ExtractionResult? extractionResult;
  final FeedbackTriggerReason triggerReason;
  final String pageTitle;
  final String route;
  final String appVersion;
  final String? screenshotUrl;
  final bool screenshotConsented;
  final bool userConfirmedSummary;
  final String? morganSummaryConfirmedText;
  final String? clientSuggestedIssueType;
  final String intakeMethod; // 'morgan_interview' | 'fallback_form'
  final String lockId;

  const MorganSubmitPayload({
    required this.transcript,
    this.extractionResult,
    required this.triggerReason,
    required this.pageTitle,
    required this.route,
    required this.appVersion,
    this.screenshotUrl,
    required this.screenshotConsented,
    required this.userConfirmedSummary,
    this.morganSummaryConfirmedText,
    this.clientSuggestedIssueType,
    required this.intakeMethod,
    required this.lockId,
  });

  Map<String, dynamic> toJson() => {
        'transcript': transcript.map((m) => m.toJson()).toList(),
        if (extractionResult != null) ...{
          'extraction_status': extractionResult!.extractionStatus,
          'issue_type': extractionResult!.issueType,
          'severity_estimate': extractionResult!.severityEstimate,
          'affected_feature': extractionResult!.affectedFeature,
          'user_intent': extractionResult!.userIntent,
          'reproduction_steps': extractionResult!.reproductionSteps,
          'morgan_summary': extractionResult!.morganSummary,
        },
        'trigger_reason': triggerReason.name,
        'page_title': pageTitle,
        'route': route,
        'app_version': appVersion,
        if (screenshotUrl != null) 'screenshot_url': screenshotUrl,
        'screenshot_consented': screenshotConsented,
        'user_confirmed_summary': userConfirmedSummary,
        if (morganSummaryConfirmedText != null)
          'morgan_summary_confirmed_text': morganSummaryConfirmedText,
        if (clientSuggestedIssueType != null)
          'client_suggested_issue_type': clientSuggestedIssueType,
        'intake_method': intakeMethod,
        'lock_id': lockId,
      };
}

// ---------------------------------------------------------------------------
// Service
// ---------------------------------------------------------------------------

class BetaFeedbackService {
  BetaFeedbackService._();

  static String get _baseUrl => kApiBaseUrl;

  // ── Internal helper ───────────────────────────────────────────────────────

  static Future<Map<String, dynamic>> _call(
    Map<String, dynamic> body,
  ) async {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) throw Exception('Not authenticated');
    final token = await user.getIdToken();

    final url = Uri.parse('$_baseUrl${FeedbackConstants.kCallablePath}');
    final response = await http
        .post(
          url,
          headers: {
            'Authorization': 'Bearer $token',
            'Content-Type': 'application/json',
          },
          body: jsonEncode(body),
        )
        .timeout(const Duration(seconds: 30));

    if (response.statusCode != 200) {
      throw Exception(
          'Callable error ${response.statusCode}: ${response.body}');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  // ── Public API ────────────────────────────────────────────────────────────

  /// CHECK mode — verifies throttle, rate limit, writes lock + draft_doc_id.
  /// Returns whether an interview may open and the server-assigned lock + doc ID.
  static Future<CheckResult> checkThrottle(
    FeedbackTriggerReason reason,
  ) async {
    try {
      final data = await _call({'mode': 'CHECK', 'trigger_reason': reason.name});
      return CheckResult.fromJson(data);
    } catch (e) {
      debugPrint('BetaFeedbackService.checkThrottle error: $e');
      return const CheckResult(allowed: false, interviewMode: false, reason: 'error');
    }
  }

  /// EXTRACT mode — PII-redacts transcript then calls Gemini for JSON extraction.
  /// Read-only: no Firestore write.
  static Future<ExtractionResult> extractFeedback({
    required List<TranscriptMessage> transcript,
    required String pageTitle,
    required String route,
    required FeedbackTriggerReason triggerReason,
  }) async {
    try {
      final data = await _call({
        'mode': 'EXTRACT',
        'transcript': transcript.map((m) => m.toJson()).toList(),
        'page_title': pageTitle,
        'route': route,
        'trigger_reason': triggerReason.name,
      });
      return ExtractionResult.fromJson(data);
    } catch (e) {
      debugPrint('BetaFeedbackService.extractFeedback error: $e');
      return const ExtractionResult(extractionStatus: 'FAILED');
    }
  }

  /// SUBMIT mode — full write via callable. Returns server-assigned doc ID.
  static Future<SubmitResult> submitMorganFeedback(
    MorganSubmitPayload payload,
  ) async {
    try {
      final data = await _call({'mode': 'SUBMIT', ...payload.toJson()});
      return SubmitResult.fromJson(data);
    } catch (e) {
      debugPrint('BetaFeedbackService.submitMorganFeedback error: $e');
      rethrow; // caller handles offline queue
    }
  }

  /// DISMISS mode — increments dismissal_count, clears lock. No doc written.
  static Future<void> dismiss({
    required String lockId,
    required String dismissReason, // 'banner_timeout' | 'user_closed' | 'esc_key'
  }) async {
    try {
      await _call({
        'mode': 'DISMISS',
        'lock_id': lockId,
        'reason': dismissReason,
      });
    } catch (e) {
      debugPrint('BetaFeedbackService.dismiss error: $e');
    }
  }

  /// UPLOAD_URL mode — returns a signed PUT URL for screenshot upload.
  /// Input is lock_id only; server reads draft_doc_id from the lock.
  static Future<UploadUrlResult?> getUploadUrl({
    required String lockId,
  }) async {
    try {
      final data = await _call({'mode': 'UPLOAD_URL', 'lock_id': lockId});
      return UploadUrlResult.fromJson(data);
    } catch (e) {
      debugPrint('BetaFeedbackService.getUploadUrl error: $e');
      return null;
    }
  }

  /// CORRECTION mode — append-only post-submit correction (10-min window).
  static Future<void> submitCorrection({
    required String docId,
    required String correctionText,
  }) async {
    try {
      await _call({
        'mode': 'CORRECTION',
        'doc_id': docId,
        'correction_text': correctionText,
      });
    } catch (e) {
      debugPrint('BetaFeedbackService.submitCorrection error: $e');
    }
  }

  /// ADMIN_RESOLVE mode — admin-only; DATA_INTEGRITY tickets require resolution_note.
  /// Optional new_issue_type lets triage promote a needs_admin_triage doc to DATA_INTEGRITY.
  /// Optional newStatus sets the status transition (OPEN → TRIAGED → RESOLVED).
  static Future<void> adminResolve({
    required String docId,
    required String resolutionNote,
    String? newIssueType, // optional promotion (e.g. 'DATA_INTEGRITY')
    String? newStatus,   // optional status transition (e.g. 'RESOLVED')
  }) async {
    await _call({
      'mode': 'ADMIN_RESOLVE',
      'doc_id': docId,
      'resolution_note': resolutionNote,
      if (newIssueType != null) 'new_issue_type': newIssueType,
      if (newStatus != null) 'new_status': newStatus,
    });
  }

  // ── Legacy admin read methods (unchanged — no direct Firestore writes) ────

  /// Admin: stream of all feedback submissions, newest first.
  static Stream<List<Map<String, dynamic>>> getFeedbackStream() {
    // Kept as Firestore read — reads are fine, only writes go through callable.
    // ignore: avoid_dynamic_calls
    throw UnimplementedError(
        'Migrate getFeedbackStream to use admin_feedback_screen Firestore reads directly.');
  }
}
