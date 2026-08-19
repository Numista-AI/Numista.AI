// lib/widgets/feedback_fallback_form.dart
//
// Minimum-payload fallback form shown when:
//   - Gemini 15s first-token timeout
//   - Rate limit reached (3 interviews/hr)
//   - Dismissed kDismissalThreshold times
//   - Accessibility mode
//
// Submitted via callable SUBMIT with intake_method: 'fallback_form'.
// client_suggested_issue_type is stored; callable sets final issue_type.
// DATA_INTEGRITY suggestion sets needs_admin_triage: true; issue_type stays 'OTHER'.

import 'package:flutter/material.dart';
import '../constants/feedback_constants.dart';
import '../services/beta_feedback_service.dart';
import '../services/morgan_feedback_session.dart';

class FeedbackFallbackForm extends StatefulWidget {
  final String? message;           // optional rate-limit or context message
  final MorganFeedbackSession? session; // present if we were mid-interview
  final VoidCallback onClose;

  const FeedbackFallbackForm({
    super.key,
    this.message,
    this.session,
    required this.onClose,
  });

  @override
  State<FeedbackFallbackForm> createState() => _FeedbackFallbackFormState();
}

class _FeedbackFallbackFormState extends State<FeedbackFallbackForm> {
  String _selectedType = 'BUG';
  final TextEditingController _commentCtrl = TextEditingController();
  bool _submitting = false;
  bool _submitted = false;
  String? _error;

  @override
  void dispose() {
    _commentCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_commentCtrl.text.trim().isEmpty) {
      setState(() => _error = 'Please add a brief comment.');
      return;
    }
    setState(() {
      _submitting = true;
      _error = null;
    });

    try {
      // If there's an ongoing session with a lock, use it; otherwise CHECK first.
      final session = widget.session;
      final lockId = session?.checkResult.lockId;

      String? effectiveLockId = lockId;
      if (effectiveLockId == null) {
        // No existing lock — call CHECK to reserve a slot
        final checkResult = await BetaFeedbackService.checkThrottle(
          FeedbackTriggerReason.manualFAB,
        );
        if (checkResult.lockId != null) {
          effectiveLockId = checkResult.lockId!;
        }
      }

      if (effectiveLockId == null) {
        setState(() {
          _error = 'Unable to submit at this time. Please try again.';
          _submitting = false;
        });
        return;
      }

      final triggerReason = session?.triggerEvent.reason ?? FeedbackTriggerReason.manualFAB;

      // Build minimal transcript from comment
      final transcript = [
        TranscriptMessage(
          role: 'user',
          message: _commentCtrl.text.trim(),
          ts: DateTime.now(),
        ),
      ];

      final payload = MorganSubmitPayload(
        transcript: transcript,
        triggerReason: triggerReason,
        pageTitle: session?.triggerEvent.pageTitle ?? 'Unknown',
        route: session?.triggerEvent.route ?? '/',
        appVersion: '4.1.0-beta',
        screenshotConsented: false,
        userConfirmedSummary: false,
        clientSuggestedIssueType: _selectedType,
        intakeMethod: 'fallback_form',
        lockId: effectiveLockId,
      );

      await BetaFeedbackService.submitMorganFeedback(payload);
      setState(() {
        _submitted = true;
        _submitting = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Submission failed. Please try again.';
        _submitting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_submitted) {
      return Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.check_circle_outline,
                color: Colors.greenAccent, size: 40),
            const SizedBox(height: 12),
            const Text('Note filed. Thank you!',
                style: TextStyle(color: Colors.white, fontSize: 14)),
            const SizedBox(height: 24),
            TextButton(
                onPressed: widget.onClose,
                child: const Text('Close',
                    style: TextStyle(color: Colors.grey))),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Optional context message (rate-limit, timeout, etc.)
          if (widget.message != null) ...[
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.amber.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.amber.withValues(alpha: 0.3)),
              ),
              child: Text(
                widget.message!,
                style: const TextStyle(color: Colors.amber, fontSize: 12),
              ),
            ),
            const SizedBox(height: 16),
          ],

          const Text('What type of feedback is this?',
              style: TextStyle(
                  color: Colors.white70,
                  fontSize: 13,
                  fontWeight: FontWeight.w500)),
          const SizedBox(height: 8),

          // Issue type dropdown — safe types only; DATA_INTEGRITY omitted
          DropdownButtonFormField<String>(
            value: _selectedType,
            dropdownColor: const Color(0xFF1E2937),
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              filled: true,
              fillColor: const Color(0xFF0F172A),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide.none,
              ),
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            ),
            items: FeedbackConstants.kSafeClientIssueTypes
                .map((t) => DropdownMenuItem(
                      value: t,
                      child: Text(_labelFor(t),
                          style: const TextStyle(fontSize: 13)),
                    ))
                .toList(),
            onChanged: (v) {
              if (v != null) setState(() => _selectedType = v);
            },
          ),
          const SizedBox(height: 4),
          const Text(
            'Data accuracy issues will be routed for admin triage.',
            style: TextStyle(color: Colors.grey, fontSize: 10),
          ),

          const SizedBox(height: 16),
          const Text('Brief description',
              style: TextStyle(
                  color: Colors.white70,
                  fontSize: 13,
                  fontWeight: FontWeight.w500)),
          const SizedBox(height: 8),
          TextField(
            controller: _commentCtrl,
            maxLines: 4,
            style: const TextStyle(color: Colors.white, fontSize: 13),
            decoration: InputDecoration(
              hintText:
                  'Describe the issue or suggestion in a few words...',
              hintStyle:
                  const TextStyle(color: Colors.grey, fontSize: 12),
              filled: true,
              fillColor: const Color(0xFF0F172A),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide.none,
              ),
              contentPadding: const EdgeInsets.all(12),
              errorText: _error,
              errorStyle: const TextStyle(color: Colors.redAccent),
            ),
          ),

          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF1E4ED8),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8)),
              ),
              onPressed: _submitting ? null : _submit,
              child: _submitting
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white))
                  : const Text('File note',
                      style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                          fontSize: 14)),
            ),
          ),
          const SizedBox(height: 8),
          Center(
            child: TextButton(
              onPressed: widget.onClose,
              child: const Text('Cancel',
                  style: TextStyle(color: Colors.grey, fontSize: 12)),
            ),
          ),
        ],
      ),
    );
  }

  String _labelFor(String type) {
    switch (type) {
      case 'BUG':
        return '🐛  Bug Report';
      case 'FEATURE':
        return '✨  Feature Request';
      case 'UX':
        return '🎨  UX / Design';
      case 'PRAISE':
        return '⭐  Praise / What Works';
      case 'CONFUSION':
        return '❓  Confusing / Hard to Use';
      case 'OTHER':
        return '📝  Other';
      default:
        return type;
    }
  }
}
