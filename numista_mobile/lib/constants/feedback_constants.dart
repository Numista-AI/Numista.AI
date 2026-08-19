// lib/constants/feedback_constants.dart
//
// All tunable constants for the MORGAN Feedback System.
// Change values here only — never hardcode these in widgets or services.

class FeedbackConstants {
  FeedbackConstants._();

  // ── Timing ────────────────────────────────────────────────────────────────
  /// How long the "Resume or close?" soft-dismiss banner stays visible (ms).
  static const int kSoftDismissWindowMs = 5 * 60 * 1000; // 5 minutes

  /// Minimum quiet-time before a milestone trigger is delivered at next-idle (ms).
  static const int kNextIdleMinQuietMs = 3 * 1000; // 3 seconds

  /// How long after SUBMIT the user can append a correction (ms).
  static const int kCorrectionWindowMs = 10 * 60 * 1000; // 10 minutes

  /// Maximum duration of a feedback_trigger_lock written at CHECK (ms).
  /// Lock auto-expires if the user abandons the interview.
  static const int kInterviewMaxDurationMs = 30 * 60 * 1000; // 30 minutes

  /// Time-to-first-token budget for Gemini in feedback mode (ms).
  /// If no streaming chunk arrives in this window → fallback form.
  static const int kGeminiFirstTokenTimeoutMs = 15 * 1000; // 15 seconds

  // ── Interview ─────────────────────────────────────────────────────────────
  /// Hard cap on conversation turns; MORGAN force-summarises at this turn.
  static const int kMaxInterviewTurns = 6;

  /// Max interview sessions per rolling kRateLimitWindowMs per uid.
  static const int kMaxInterviewsPerWindow = 3;

  /// Rolling window for the per-uid interview rate limit (ms).
  static const int kRateLimitWindowMs = 60 * 60 * 1000; // 60 minutes

  // ── Dismissal ─────────────────────────────────────────────────────────────
  /// Number of dismissals before FAB goes straight to fallback form.
  static const int kDismissalThreshold = 3;

  /// Short lock-out after a DISMISS on a behavioral trigger (ms).
  /// Applied only if behavioral re-trigger noise is observed in production.
  /// Phase 3+ optional — default false in FeedbackTriggerObserver.
  static const int kDismissLockoutMs = 15 * 60 * 1000; // 15 minutes

  // ── Drawer UI ─────────────────────────────────────────────────────────────
  /// Fixed width of the right-hand feedback drawer in logical pixels.
  static const double kDrawerWidthPx = 420;

  /// BackdropFilter blur sigma applied to the app shell while drawer is open.
  static const double kBackdropBlurSigma = 6.0;

  // ── Backend ───────────────────────────────────────────────────────────────
  /// Path of the Cloud Run feedback callable relative to the backend base URL.
  static const String kCallablePath = '/api/feedback/callable';

  // ── GCS ───────────────────────────────────────────────────────────────────
  static const String kGcsBucket = 'studio-9101802118-8c9a8-uploads';
  static const String kGcsStandardPrefix = 'feedback_screenshots';
  static const String kGcsHoldPrefix = 'feedback_screenshots_hold';

  // ── Issue types (enum values) ─────────────────────────────────────────────
  static const List<String> kSafeClientIssueTypes = [
    'BUG',
    'FEATURE',
    'UX',
    'PRAISE',
    'CONFUSION',
    'OTHER',
  ];
  // DATA_INTEGRITY is intentionally absent — only EXTRACT or ADMIN_RESOLVE may set it.
}
