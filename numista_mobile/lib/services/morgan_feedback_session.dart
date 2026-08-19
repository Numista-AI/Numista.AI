// lib/services/morgan_feedback_session.dart
//
// Interview engine for MORGAN Feedback Mode.
// Uses the existing Cloud Run chat proxy (same endpoint as AiChatScreen).
// Does NOT write to Firestore. Does NOT read users/{uid}/coins.

import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import 'beta_feedback_service.dart';
import 'feedback_trigger_observer.dart';
import '../constants/feedback_constants.dart';
import '../constants.dart' show kApiBaseUrl;

// ---------------------------------------------------------------------------
// Session state
// ---------------------------------------------------------------------------

enum SessionPhase {
  idle,
  interviewing,
  extracting,
  awaitingConfirmation,
  extractFailed,
  submitted,
  fallbackRequired,
}

class ChatBubble {
  final String role; // 'assistant' | 'user'
  final String text;
  final DateTime ts;
  final bool isStreaming;

  const ChatBubble({
    required this.role,
    required this.text,
    required this.ts,
    this.isStreaming = false,
  });

  ChatBubble copyWith({String? text, bool? isStreaming}) => ChatBubble(
        role: role,
        text: text ?? this.text,
        ts: ts,
        isStreaming: isStreaming ?? this.isStreaming,
      );

  TranscriptMessage toTranscriptMessage() =>
      TranscriptMessage(role: role, message: text, ts: ts);
}

// ---------------------------------------------------------------------------
// Session
// ---------------------------------------------------------------------------

class MorganFeedbackSession extends ChangeNotifier {
  final FeedbackTriggerEvent triggerEvent;
  final CheckResult checkResult; // holds lockId + draftDocId from server

  MorganFeedbackSession({
    required this.triggerEvent,
    required this.checkResult,
  });

  // ── State ─────────────────────────────────────────────────────────────────
  SessionPhase _phase = SessionPhase.idle;
  SessionPhase get phase => _phase;

  final List<ChatBubble> _bubbles = [];
  List<ChatBubble> get bubbles => List.unmodifiable(_bubbles);

  int _turnCount = 0;
  int get turnCount => _turnCount;

  ExtractionResult? _lastExtraction;
  ExtractionResult? get lastExtraction => _lastExtraction;

  String? _submittedDocId;
  String? get submittedDocId => _submittedDocId;

  bool _correctionWindowOpen = false;
  bool get correctionWindowOpen => _correctionWindowOpen;

  String? _screenshotObjectPath;

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  Future<void> start() async {
    _phase = SessionPhase.interviewing;
    notifyListeners();
    await _sendAssistantMessage(_openingMessage());
  }

  // ── User sends a message ──────────────────────────────────────────────────

  Future<void> sendUserMessage(String text) async {
    if (_phase != SessionPhase.interviewing) return;
    if (text.trim().isEmpty) return;

    _addBubble(ChatBubble(role: 'user', text: text, ts: DateTime.now()));
    _turnCount++;
    notifyListeners();

    if (_turnCount >= FeedbackConstants.kMaxInterviewTurns) {
      await _triggerSummarize();
      return;
    }

    await _streamAssistantTurn(text);
  }

  // ── Summarize ─────────────────────────────────────────────────────────────

  Future<void> _triggerSummarize() async {
    _phase = SessionPhase.extracting;
    notifyListeners();

    final transcript = _bubbles.map((b) => b.toTranscriptMessage()).toList();

    final result = await BetaFeedbackService.extractFeedback(
      transcript: transcript,
      pageTitle: triggerEvent.pageTitle,
      route: triggerEvent.route,
      triggerReason: triggerEvent.reason,
    );

    _lastExtraction = result;

    if (result.isComplete && result.morganSummary != null) {
      _phase = SessionPhase.awaitingConfirmation;
      _addBubble(ChatBubble(
        role: 'assistant',
        text:
            "Based on what you've shared, here is what I'm going to file for you — does this sound right?\n\n${result.morganSummary}",
        ts: DateTime.now(),
      ));
    } else {
      // EXTRACT FAILED — show best-effort summary, require explicit user action
      _phase = SessionPhase.extractFailed;
      _addBubble(ChatBubble(
        role: 'assistant',
        text: result.morganSummary ??
            "I wasn't able to fully structure your feedback, but I've captured our conversation. "
                "You can still file it as-is for the team to review.",
        ts: DateTime.now(),
      ));
    }
    notifyListeners();
  }

  // ── Confirmation flow ─────────────────────────────────────────────────────

  /// Called when user taps "Yes" on the summary confirmation.
  Future<SubmitResult?> confirmAndSubmit({
    String? screenshotUrl,
    bool screenshotConsented = false,
    String appVersion = '4.1.0-beta',
  }) async {
    if (_phase != SessionPhase.awaitingConfirmation) return null;

    final transcript = _bubbles.map((b) => b.toTranscriptMessage()).toList();
    final confirmedText = _lastExtraction?.morganSummary;

    final payload = MorganSubmitPayload(
      transcript: transcript,
      extractionResult: _lastExtraction,
      triggerReason: triggerEvent.reason,
      pageTitle: triggerEvent.pageTitle,
      route: triggerEvent.route,
      appVersion: appVersion,
      screenshotUrl: screenshotUrl ?? _screenshotObjectPath,
      screenshotConsented: screenshotConsented,
      userConfirmedSummary: true,
      morganSummaryConfirmedText: confirmedText,
      intakeMethod: 'morgan_interview',
      lockId: checkResult.lockId!,
    );

    final result = await BetaFeedbackService.submitMorganFeedback(payload);
    _submittedDocId = result.docId;
    _phase = SessionPhase.submitted;

    // Open correction window for kCorrectionWindowMs
    _correctionWindowOpen = true;
    Future.delayed(
      Duration(milliseconds: FeedbackConstants.kCorrectionWindowMs),
      () {
        _correctionWindowOpen = false;
        notifyListeners();
      },
    );

    notifyListeners();
    return result;
  }

  /// Called when user taps "No" — sends a correction turn (max 1).
  Future<void> requestCorrection(String correctionNote) async {
    if (_phase != SessionPhase.awaitingConfirmation) return;
    _phase = SessionPhase.interviewing;
    _addBubble(ChatBubble(
      role: 'user',
      text: correctionNote,
      ts: DateTime.now(),
    ));
    notifyListeners();

    await _sendAssistantMessage(
        "Thanks for clarifying! Let me update that. $correctionNote");
    await _triggerSummarize();
  }

  /// Called when user taps "File this as unconfirmed" after EXTRACT FAIL.
  Future<SubmitResult?> fileUnconfirmed({
    String? clientSuggestedIssueType,
    String appVersion = '4.1.0-beta',
  }) async {
    final transcript = _bubbles.map((b) => b.toTranscriptMessage()).toList();

    final payload = MorganSubmitPayload(
      transcript: transcript,
      extractionResult: _lastExtraction,
      triggerReason: triggerEvent.reason,
      pageTitle: triggerEvent.pageTitle,
      route: triggerEvent.route,
      appVersion: appVersion,
      screenshotUrl: _screenshotObjectPath,
      screenshotConsented: _screenshotObjectPath != null,
      userConfirmedSummary: false,
      clientSuggestedIssueType: clientSuggestedIssueType,
      intakeMethod: 'morgan_interview',
      lockId: checkResult.lockId!,
    );

    final result = await BetaFeedbackService.submitMorganFeedback(payload);
    _submittedDocId = result.docId;
    _phase = SessionPhase.submitted;
    notifyListeners();
    return result;
  }

  /// Screenshot: gets signed URL from callable, stores object path.
  Future<UploadUrlResult?> requestUploadUrl() async {
    final lockId = checkResult.lockId;
    if (lockId == null) return null;
    return BetaFeedbackService.getUploadUrl(lockId: lockId);
  }

  void setScreenshotObjectPath(String path) {
    _screenshotObjectPath = path;
  }

  // ── Streaming assistant turn ──────────────────────────────────────────────

  Future<void> _streamAssistantTurn(String userMessage) async {
    // Check for summarize signals in the conversation
    if (_turnCount >= FeedbackConstants.kMaxInterviewTurns - 1) {
      await _triggerSummarize();
      return;
    }

    await _sendAssistantMessage(null, userTurn: userMessage);
  }

  Future<void> _sendAssistantMessage(String? staticMessage,
      {String? userTurn}) async {
    if (staticMessage != null) {
      _addBubble(ChatBubble(
          role: 'assistant', text: staticMessage, ts: DateTime.now()));
      notifyListeners();
      return;
    }

    // Streaming from Cloud Run chat proxy
    final streamingBubble = ChatBubble(
      role: 'assistant',
      text: '',
      ts: DateTime.now(),
      isStreaming: true,
    );
    _addBubble(streamingBubble);
    final streamingIndex = _bubbles.length - 1;
    notifyListeners();

    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) throw Exception('Not authenticated');
      final token = await user.getIdToken();

      final prompt = _buildSystemPrompt();
      final history = _bubbles
          .where((b) => !b.isStreaming)
          .map((b) => {'role': b.role, 'text': b.text})
          .toList();

      final url = Uri.parse(
          '$kApiBaseUrl/api/ai/chat/stream');

      final request = http.Request('POST', url)
        ..headers['Authorization'] = 'Bearer $token'
        ..headers['Content-Type'] = 'application/json'
        ..body = jsonEncode({
          'system_prompt': prompt,
          'history': history,
          'query': userTurn ?? '',
          'feedback_mode': true,
        });

      final client = http.Client();
      bool firstChunkReceived = false;

      final streamResponse = await client.send(request).timeout(
        Duration(milliseconds: FeedbackConstants.kGeminiFirstTokenTimeoutMs),
        onTimeout: () {
          client.close();
          throw TimeoutException('No first token within 15s');
        },
      );

      if (streamResponse.statusCode != 200) {
        throw Exception('Stream error ${streamResponse.statusCode}');
      }

      final buffer = StringBuffer();
      await streamResponse.stream
          .transform(utf8.decoder)
          .transform(const LineSplitter())
          .forEach((line) {
        if (!firstChunkReceived) firstChunkReceived = true;
        if (line.startsWith('data: ')) {
          final chunk = line.substring(6);
          if (chunk != '[DONE]') {
            buffer.write(chunk);
            _bubbles[streamingIndex] = _bubbles[streamingIndex]
                .copyWith(text: buffer.toString(), isStreaming: true);
            notifyListeners();
          }
        }
      });

      client.close();
      _bubbles[streamingIndex] = _bubbles[streamingIndex]
          .copyWith(text: buffer.toString(), isStreaming: false);

      // Check if MORGAN wants to summarize
      final responseText = buffer.toString().toLowerCase();
      if (responseText.contains('does this sound right') ||
          responseText.contains("i'm going to file") ||
          _turnCount >= FeedbackConstants.kMaxInterviewTurns) {
        await _triggerSummarize();
      }
    } on TimeoutException {
      _bubbles[streamingIndex] = _bubbles[streamingIndex]
          .copyWith(text: '', isStreaming: false);
      _phase = SessionPhase.fallbackRequired;
    } catch (e) {
      debugPrint('[MorganFeedbackSession] Stream error: $e');
      _bubbles[streamingIndex] = _bubbles[streamingIndex]
          .copyWith(text: '', isStreaming: false);
      _phase = SessionPhase.fallbackRequired;
    }
    notifyListeners();
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  void _addBubble(ChatBubble bubble) {
    _bubbles.add(bubble);
  }

  String _openingMessage() {
    final name = triggerEvent.userName.isNotEmpty
        ? triggerEvent.userName.split(' ').first
        : 'there';
    // Switch expression: Dart recognizes enum exhaustiveness here.
    return switch (triggerEvent.reason) {
      FeedbackTriggerReason.manualFAB =>
        "Thanks for reaching out! What's on your mind — did something not work as expected, "
        "or is there a feature you'd like to see?",
      FeedbackTriggerReason.scanTimeout =>
        "Hey $name, it looks like a scan ran into trouble just now. "
        "Want to walk me through what happened?",
      FeedbackTriggerReason.pcgsImportError =>
        "Hey $name — the PCGS import hit an issue. "
        "Can you tell me what you were trying to bring in?",
      FeedbackTriggerReason.addCoinAbandoned =>
        "Hey $name, it looks like adding an item didn't quite complete. "
        "Did something give you trouble, or did you just step away?",
      FeedbackTriggerReason.milestoneAchieved =>
        "Congratulations on your milestone, $name! Before we move on — "
        "is there anything we could have made smoother along the way?",
    };
  }

  String _buildSystemPrompt() {
    return '''
You are Morgan, the AI assistant for Numista.AI.

You are in FEEDBACK INTERVIEW MODE. You are warm, patient, and professional.
You do NOT have access to the user's collection data in this mode.
You know only the user's first name and the page they were on.

CONTEXT:
  Trigger: ${triggerEvent.reason.name}
  Page: ${triggerEvent.pageTitle} (${triggerEvent.route})
  Turn limit: ${FeedbackConstants.kMaxInterviewTurns}

INTERVIEW OBJECTIVES:
  1. Ask exactly ONE question per turn.
  2. Probe for: what the user was doing, what they expected, what happened.
  3. Mirror and paraphrase to confirm understanding.
  4. Summarize after 3-4 turns (or when you have enough context).
  5. At turn ${FeedbackConstants.kMaxInterviewTurns}: say "Based on what you've shared, here is what I'm going to file for you — does this sound right?" followed by a 2-3 sentence summary.

RULES:
  - 1-3 sentences per response. Never lecture.
  - Ask exactly ONE question per turn.
  - Never dismiss or minimize.
  - Never promise a fix or timeline. Say "I will make sure this gets to the team."
  - Never repeat cert numbers, dollar amounts, or email addresses.

DATA_INTEGRITY ROUTING:
  If user describes wrong PCGS/NGC data, missing items after import, incorrect estate valuations,
  or failed cert lookups — say "This sounds like a data accuracy issue. I am flagging this as
  high priority for the team." Then proceed to summarize.
''';
  }
}
