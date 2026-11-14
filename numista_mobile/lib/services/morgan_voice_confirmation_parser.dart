/// Decision classification returned by [MorganVoiceConfirmationParser].
enum MorganConfirmationDecisionKind {
  acceptedTierA,
  acceptedTierB,
  rejectedVeto,
  rejectedBareAffirmative,
  rejectedTtsInterlock,
  rejectedWindowExpired,
  rejectedLowConfidence,
  rejectedNoCard,
  rejectedOtherSpeechInWindow,
  rejectedNoActionMatch,
}

class MorganVoiceConfirmationResult {
  final bool confirmed;
  final MorganConfirmationDecisionKind kind;
  final String parseTier;
  final String? matchedVerb;
  final String normalizedTranscript;
  final String reason;

  const MorganVoiceConfirmationResult({
    required this.confirmed,
    required this.kind,
    required this.parseTier,
    this.matchedVerb,
    required this.normalizedTranscript,
    required this.reason,
  });
}

/// Evaluates voice transcripts for Gate 0 safety confirmations (§7.4 & Grok §4.1)
/// and normalizes numismatic spoken jargon via a phonetic alias dictionary.
class MorganVoiceConfirmationParser {
  MorganVoiceConfirmationParser._();

  static const int ttsTailGuardMs = 450;
  static const int tierBNaturalWindowMs = 2500;
  static const double minTierBConfidence = 0.75;

  static final RegExp _vetoPattern = RegExp(
    r"\b(no|not|don'?t|do\s+not|wait|stop|cancel|hold\s+on|wrong|never\s*mind)\b",
    caseSensitive: false,
  );

  static const Set<String> _bareAffirmatives = <String>{
    'yes',
    'yeah',
    'yep',
    'yup',
    'sure',
    'okay',
    'ok',
    'alright',
    'fine',
    'uh huh',
  };

  static const Set<String> _affirmativeTokens = <String>{
    'yes',
    'yeah',
    'yep',
    'sure',
    'okay',
    'ok',
    'go ahead',
    'please',
  };

  static const Map<String, Set<String>> _tierAPhrasesByVerb =
      <String, Set<String>>{
    'save': {'yes save', 'yes confirm', 'confirm that', 'yes keep', 'yes add'},
    'add': {'yes add', 'yes save', 'yes confirm', 'confirm that'},
    'keep': {'yes keep', 'yes save', 'yes confirm', 'confirm that'},
    'confirm': {'yes confirm', 'confirm that', 'yes save'},
    'delete': {'yes delete', 'yes remove', 'yes confirm', 'confirm that'},
    'remove': {'yes remove', 'yes delete', 'yes confirm', 'confirm that'},
    'send': {'yes send', 'yes confirm', 'confirm that'},
  };

  static const Map<String, Set<String>> _allowedVerbsByGateAction =
      <String, Set<String>>{
    'add_coin': {'save', 'confirm', 'keep', 'add'},
    'edit_coin': {'save', 'confirm', 'keep'},
    'bulk_edit': {'save', 'confirm', 'keep'},
    'delete_coin': {'delete', 'remove', 'confirm'},
    'restore_coin': {'restore', 'save', 'confirm', 'keep'},
    'add_wishlist': {'save', 'confirm', 'add', 'keep'},
    'email_wishlist': {'send', 'confirm'},
    'support_ticket': {'send', 'confirm', 'save'},
  };

  static const Set<String> _allActionVerbs = <String>{
    'save',
    'confirm',
    'keep',
    'add',
    'delete',
    'remove',
    'send',
    'restore',
  };

  /// Normalizes common Web Speech API mishearings of numismatic terms & grades.
  static String normalizeNumismaticTranscript(String raw) {
    var out = raw.trim().replaceAll(RegExp(r'\s+'), ' ');

    // Spoken letter/number grade patterns -> canonical coin grade tokens.
    final gradeReplacements = <RegExp, String Function(Match)>{
      RegExp(r'\b(?:m\s*s|em\s*ess)\s*(?:sixty\s*zero|60)\b', caseSensitive: false):
          (_) => 'MS60',
      RegExp(r'\b(?:m\s*s|em\s*ess)\s*(?:sixty\s*one|61)\b', caseSensitive: false):
          (_) => 'MS61',
      RegExp(r'\b(?:m\s*s|em\s*ess)\s*(?:sixty\s*two|62)\b', caseSensitive: false):
          (_) => 'MS62',
      RegExp(r'\b(?:m\s*s|em\s*ess)\s*(?:sixty\s*three|63)\b', caseSensitive: false):
          (_) => 'MS63',
      RegExp(r'\b(?:m\s*s|em\s*ess)\s*(?:sixty\s*four|64)\b', caseSensitive: false):
          (_) => 'MS64',
      RegExp(r'\b(?:m\s*s|em\s*ess)\s*(?:sixty\s*five|65)\b', caseSensitive: false):
          (_) => 'MS65',
      RegExp(r'\b(?:m\s*s|em\s*ess)\s*(?:sixty\s*six|66)\b', caseSensitive: false):
          (_) => 'MS66',
      RegExp(r'\b(?:m\s*s|em\s*ess)\s*(?:sixty\s*seven|67)\b', caseSensitive: false):
          (_) => 'MS67',
      RegExp(r'\b(?:m\s*s|em\s*ess)\s*(?:sixty\s*eight|68)\b', caseSensitive: false):
          (_) => 'MS68',
      RegExp(r'\b(?:m\s*s|em\s*ess)\s*(?:sixty\s*nine|69)\b', caseSensitive: false):
          (_) => 'MS69',
      RegExp(r'\b(?:m\s*s|em\s*ess)\s*(?:seventy|70)\b', caseSensitive: false):
          (_) => 'MS70',
      RegExp(r'\b(?:x\s*f|ex\s*ef)\s*(?:forty\s*five|45)\b', caseSensitive: false):
          (_) => 'XF45',
      RegExp(r'\b(?:x\s*f|ex\s*ef)\s*(?:forty|40)\b', caseSensitive: false):
          (_) => 'XF40',
      RegExp(r'\b(?:a\s*u|ay\s*you)\s*(?:fifty\s*eight|58)\b', caseSensitive: false):
          (_) => 'AU58',
      RegExp(r'\b(?:a\s*u|ay\s*you)\s*(?:fifty\s*five|55)\b', caseSensitive: false):
          (_) => 'AU55',
      RegExp(r'\b(?:p\s*r|p\s*f)\s*(?:sixty\s*nine|69)\b', caseSensitive: false):
          (_) => 'PF69',
      RegExp(r'\b(?:p\s*r|p\s*f)\s*(?:seventy|70)\b', caseSensitive: false):
          (_) => 'PF70',
    };

    gradeReplacements.forEach((pattern, fn) {
      out = out.replaceAllMapped(pattern, fn);
    });

    final phraseReplacements = <RegExp, String>{
      RegExp(r'\bv\s*d\s*b\b', caseSensitive: false): 'VDB',
      RegExp(r'\bp\s*c\s*g\s*s\b', caseSensitive: false): 'PCGS',
      RegExp(r'\bn\s*g\s*c\b', caseSensitive: false): 'NGC',
      RegExp(r'\ba\s*n\s*a\s*c\s*s\b', caseSensitive: false): 'ANACS',
      RegExp(r'\bc\s*a\s*c\b', caseSensitive: false): 'CAC',
      RegExp(r'\bsaint[\s-]+gaudens\b', caseSensitive: false): 'Saint-Gaudens',
      RegExp(r'\bdeep\s+cameo\b', caseSensitive: false): 'DCAM',
      RegExp(r'\bfull\s+bell\s+lines\b', caseSensitive: false): 'FBL',
      RegExp(r'\bfull\s+steps\b', caseSensitive: false): 'FS',
    };

    phraseReplacements.forEach((pattern, replacement) {
      out = out.replaceAll(pattern, replacement);
    });

    return out;
  }

  /// Evaluates whether a spoken [transcript] confirms a currently displayed gate.
  static MorganVoiceConfirmationResult evaluate(
    String transcript, {
    required bool isConfirmationCardVisible,
    String expectedGateAction = 'add_coin',
    bool duringTtsPlayback = false,
    int? delayAfterTtsMs,
    double confidence = 1.0,
    bool otherSpeechOccurredInWindow = false,
  }) {
    final normalizedDisplay = normalizeNumismaticTranscript(transcript);
    final cleanLower = transcript
        .toLowerCase()
        .replaceAll(RegExp(r"[^\w\s']"), ' ')
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim();

    // 1. Half-duplex TTS interlock & +450ms tail guard.
    if (duringTtsPlayback ||
        (delayAfterTtsMs != null && delayAfterTtsMs < ttsTailGuardMs)) {
      return MorganVoiceConfirmationResult(
        confirmed: false,
        kind: MorganConfirmationDecisionKind.rejectedTtsInterlock,
        parseTier: 'NONE',
        normalizedTranscript: normalizedDisplay,
        reason: 'Ignored during TTS playback or <450ms post-TTS tail guard.',
      );
    }

    // 2. Hard Negation & Hesitation Veto (checked BEFORE any positive match).
    if (cleanLower.isEmpty || _vetoPattern.hasMatch(cleanLower)) {
      return MorganVoiceConfirmationResult(
        confirmed: false,
        kind: MorganConfirmationDecisionKind.rejectedVeto,
        parseTier: 'NONE',
        normalizedTranscript: normalizedDisplay,
        reason: 'Rejected due to negation or hesitation veto keyword.',
      );
    }

    // 3. Confirmation card must already be visible.
    if (!isConfirmationCardVisible) {
      return MorganVoiceConfirmationResult(
        confirmed: false,
        kind: MorganConfirmationDecisionKind.rejectedNoCard,
        parseTier: 'NONE',
        normalizedTranscript: normalizedDisplay,
        reason: 'No confirmation card is currently displayed.',
      );
    }

    // 4. Reject bare single-word affirmatives ("yes", "yeah", "sure", "okay").
    if (_bareAffirmatives.contains(cleanLower)) {
      return MorganVoiceConfirmationResult(
        confirmed: false,
        kind: MorganConfirmationDecisionKind.rejectedBareAffirmative,
        parseTier: 'NONE',
        normalizedTranscript: normalizedDisplay,
        reason: 'Bare single-word affirmative rejected for Gate 0 safety.',
      );
    }

    final allowedVerbs =
        _allowedVerbsByGateAction[expectedGateAction] ?? _allActionVerbs;

    // 5. Tier A: Exact Two-Word Confirmation Phrases.
    for (final verb in allowedVerbs) {
      final phrases = _tierAPhrasesByVerb[verb] ?? const <String>{};
      for (final phrase in phrases) {
        if (cleanLower == phrase) {
          return MorganVoiceConfirmationResult(
            confirmed: true,
            kind: MorganConfirmationDecisionKind.acceptedTierA,
            parseTier: 'TIER_A',
            matchedVerb: verb,
            normalizedTranscript: normalizedDisplay,
            reason: 'Matched exact Tier A confirmation phrase "$phrase".',
          );
        }
      }
    }

    // 6. Tier B: Natural Senior Phrasing within 2.5s window post (+450ms) TTS end.
    if (otherSpeechOccurredInWindow) {
      return MorganVoiceConfirmationResult(
        confirmed: false,
        kind: MorganConfirmationDecisionKind.rejectedOtherSpeechInWindow,
        parseTier: 'NONE',
        normalizedTranscript: normalizedDisplay,
        reason: 'Intervening speech detected inside confirmation window.',
      );
    }

    if (delayAfterTtsMs != null &&
        delayAfterTtsMs > (ttsTailGuardMs + tierBNaturalWindowMs)) {
      return MorganVoiceConfirmationResult(
        confirmed: false,
        kind: MorganConfirmationDecisionKind.rejectedWindowExpired,
        parseTier: 'NONE',
        normalizedTranscript: normalizedDisplay,
        reason:
            'Tier B natural phrasing exceeded 2.5s post-TTS confirmation window.',
      );
    }

    if (confidence < minTierBConfidence) {
      return MorganVoiceConfirmationResult(
        confirmed: false,
        kind: MorganConfirmationDecisionKind.rejectedLowConfidence,
        parseTier: 'NONE',
        normalizedTranscript: normalizedDisplay,
        reason: 'Speech confidence $confidence below 0.75 threshold.',
      );
    }

    final words = cleanLower.split(' ').where((w) => w.isNotEmpty).toList();
    final hasAffirmative = _affirmativeTokens.any((tok) {
      if (tok.contains(' ')) return cleanLower.contains(tok);
      return words.contains(tok);
    });

    String? matchedVerb;
    for (final verb in allowedVerbs) {
      if (words.contains(verb)) {
        matchedVerb = verb;
        break;
      }
      // Phonetic near-match (Levenshtein <= 1) for clear natural speech.
      if (words.any((w) => w.length >= 4 && _levenshtein(w, verb) <= 1)) {
        matchedVerb = verb;
        break;
      }
    }

    if (hasAffirmative && matchedVerb != null) {
      return MorganVoiceConfirmationResult(
        confirmed: true,
        kind: MorganConfirmationDecisionKind.acceptedTierB,
        parseTier: 'TIER_B',
        matchedVerb: matchedVerb,
        normalizedTranscript: normalizedDisplay,
        reason:
            'Matched Tier B natural confirmation (affirmative + "$matchedVerb").',
      );
    }

    return MorganVoiceConfirmationResult(
      confirmed: false,
      kind: MorganConfirmationDecisionKind.rejectedNoActionMatch,
      parseTier: 'NONE',
      normalizedTranscript: normalizedDisplay,
      reason: 'Missing both affirmative token and matching action verb.',
    );
  }

  static int _levenshtein(String a, String b) {
    if (a == b) return 0;
    if (a.isEmpty) return b.length;
    if (b.isEmpty) return a.length;
    final dp = List<int>.generate(b.length + 1, (j) => j);
    for (int i = 1; i <= a.length; i++) {
      int prevDiag = dp[0];
      dp[0] = i;
      for (int j = 1; j <= b.length; j++) {
        final temp = dp[j];
        final cost = a.codeUnitAt(i - 1) == b.codeUnitAt(j - 1) ? 0 : 1;
        final sub = prevDiag + cost;
        final ins = dp[j - 1] + 1;
        final del = dp[j] + 1;
        dp[j] = sub < ins ? (sub < del ? sub : del) : (ins < del ? ins : del);
        prevDiag = temp;
      }
    }
    return dp[b.length];
  }
}
