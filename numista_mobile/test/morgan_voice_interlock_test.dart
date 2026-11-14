import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/morgan_test_harness.dart';
import 'package:numista_ai/services/morgan_voice_confirmation_parser.dart';
import 'package:numista_ai/services/stt_voice_service.dart';
import 'package:numista_ai/services/tts_voice_service.dart';

void main() {
  setUp(() {
    MorganTestHarness.debugEnabledOverride = true;
    TtsVoiceService.isSpeakingNotifier.value = false;
    SttVoiceService.instance.resetForTesting();
  });

  tearDown(() {
    TtsVoiceService.isSpeakingNotifier.value = false;
    SttVoiceService.instance.resetForTesting();
    MorganTestHarness.reset();
    MorganTestHarness.debugEnabledOverride = null;
  });

  group('MorganVoiceConfirmationParser Numismatic Normalization & Gate 0 Safety', () {
    test('normalizes spoken numismatic jargon via phonetic alias dictionary', () {
      final normalized =
          MorganVoiceConfirmationParser.normalizeNumismaticTranscript(
        'check my saint gaudens v d b in ms 65 graded by p c g s',
      );
      expect(normalized, contains('Saint-Gaudens'));
      expect(normalized, contains('VDB'));
      expect(normalized, contains('MS65'));
      expect(normalized, contains('PCGS'));
    });

    test('rejects hard negation veto, bare yes, TTS echo, expired window, and low confidence', () {
      // 1. Hard veto
      final veto = MorganVoiceConfirmationParser.evaluate(
        "no don't save",
        isConfirmationCardVisible: true,
        expectedGateAction: 'add_coin',
      );
      expect(veto.confirmed, isFalse);
      expect(veto.kind, MorganConfirmationDecisionKind.rejectedVeto);

      // 2. TTS playback lock & <450ms tail guard
      final duringTts = MorganVoiceConfirmationParser.evaluate(
        'yes save',
        isConfirmationCardVisible: true,
        duringTtsPlayback: true,
      );
      expect(duringTts.confirmed, isFalse);
      expect(duringTts.kind, MorganConfirmationDecisionKind.rejectedTtsInterlock);

      final tailBlocked = MorganVoiceConfirmationParser.evaluate(
        'yes save',
        isConfirmationCardVisible: true,
        delayAfterTtsMs: 449,
      );
      expect(tailBlocked.confirmed, isFalse);
      expect(tailBlocked.kind, MorganConfirmationDecisionKind.rejectedTtsInterlock);

      // 3. Bare "yes" rejected
      final bareYes = MorganVoiceConfirmationParser.evaluate(
        'yes',
        isConfirmationCardVisible: true,
        delayAfterTtsMs: 600,
      );
      expect(bareYes.confirmed, isFalse);
      expect(bareYes.kind, MorganConfirmationDecisionKind.rejectedBareAffirmative);

      // 4. Tier A two-word confirmation
      final tierASave = MorganVoiceConfirmationParser.evaluate(
        'yes save',
        isConfirmationCardVisible: true,
        expectedGateAction: 'add_coin',
        delayAfterTtsMs: 5000,
      );
      expect(tierASave.confirmed, isTrue);
      expect(tierASave.kind, MorganConfirmationDecisionKind.acceptedTierA);

      final tierADelete = MorganVoiceConfirmationParser.evaluate(
        'yes delete',
        isConfirmationCardVisible: true,
        expectedGateAction: 'delete_coin',
      );
      expect(tierADelete.confirmed, isTrue);
      expect(tierADelete.kind, MorganConfirmationDecisionKind.acceptedTierA);

      // "yes delete" is NOT valid for add_coin card
      final wrongVerb = MorganVoiceConfirmationParser.evaluate(
        'yes delete',
        isConfirmationCardVisible: true,
        expectedGateAction: 'add_coin',
      );
      expect(wrongVerb.confirmed, isFalse);

      // 5. Tier B natural phrasing inside 2.5s post-(450ms) window at >=0.75 confidence
      final tierBOk = MorganVoiceConfirmationParser.evaluate(
        'yes, please save that',
        isConfirmationCardVisible: true,
        expectedGateAction: 'add_coin',
        delayAfterTtsMs: 1200,
        confidence: 0.75,
      );
      expect(tierBOk.confirmed, isTrue);
      expect(tierBOk.kind, MorganConfirmationDecisionKind.acceptedTierB);

      final tierBExpired = MorganVoiceConfirmationParser.evaluate(
        'yes, please save that',
        isConfirmationCardVisible: true,
        expectedGateAction: 'add_coin',
        delayAfterTtsMs: 3200,
        confidence: 0.95,
      );
      expect(tierBExpired.confirmed, isFalse);
      expect(tierBExpired.kind, MorganConfirmationDecisionKind.rejectedWindowExpired);

      final tierBLowConf = MorganVoiceConfirmationParser.evaluate(
        'yes, please save that',
        isConfirmationCardVisible: true,
        expectedGateAction: 'add_coin',
        delayAfterTtsMs: 900,
        confidence: 0.60,
      );
      expect(tierBLowConf.confirmed, isFalse);
      expect(tierBLowConf.kind, MorganConfirmationDecisionKind.rejectedLowConfidence);
    });
  });

  group('SttVoiceService half-duplex interlock & MorganTestHarness injection', () {
    test('increments ignoredEchoCount during TTS/tail and delivers clean utterance after 450ms',
        () async {
      final stt = SttVoiceService.instance;
      SttUtteranceEvent? captured;
      stt.onUtterance = (e) => captured = e;

      TtsVoiceService.isSpeakingNotifier.value = true;
      expect(stt.isSpeakingLocked, isTrue);

      await MorganTestHarness.injectVoiceUtterance(
        'yes save',
        duringTtsPlayback: true,
        delayAfterTtsMs: 100,
      );
      expect(stt.ignoredEchoCount, 1);
      expect(captured, isNull);

      TtsVoiceService.isSpeakingNotifier.value = false;
      // Injecting at 300ms (<450ms tail) still counts as ignored echo.
      await MorganTestHarness.injectVoiceUtterance(
        'yes save',
        duringTtsPlayback: false,
        delayAfterTtsMs: 300,
      );
      expect(stt.ignoredEchoCount, 2);
      expect(captured, isNull);

      // Clear post-TTS timer via resetForTesting and send clean post-tail speech.
      stt.resetForTesting();
      stt.onUtterance = (e) => captured = e;
      await MorganTestHarness.injectVoiceUtterance(
        'yes, please save that',
        duringTtsPlayback: false,
        delayAfterTtsMs: 600,
        confidence: 0.92,
      );
      expect(captured, isNotNull);
      expect(captured!.rawTranscript, 'yes, please save that');

      final decision = stt.evaluateConfirmationUtterance(
        captured!,
        isConfirmationCardVisible: true,
        expectedGateAction: 'add_coin',
      );
      expect(decision.confirmed, isTrue);
      expect(decision.kind, MorganConfirmationDecisionKind.acceptedTierB);
    });
  });
}
