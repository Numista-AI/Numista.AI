import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/widgets/morgan_guides.dart';
import 'package:numista_ai/widgets/morgan_guide_flow.dart';

void main() {
  group('Morgan Guides Proactive Audit', () {
    test('No step contains redundant tab navigation instructions', () {
      final allGuides = [
        MorganGuides.invoice,
        MorganGuides.microscope,
        MorganGuides.photo,
        MorganGuides.collection,
        MorganGuides.programs,
      ];

      final redundantPhrases = [
        "Pick the 'Upload Files' tab",
        "Select the 'Upload Files' tab",
        "Pick the 'Single Invoice Scan' tab",
        "Select the 'Single Invoice Scan' tab",
        "Pick the 'Manual Entry' tab",
      ];

      for (final guide in allGuides) {
        for (int i = 0; i < guide.steps.length; i++) {
          final step = guide.steps[i];
          for (final phrase in redundantPhrases) {
            expect(
              step.narration.contains(phrase),
              isFalse,
              reason:
                  'Guide ${guide.id} step $i contains redundant navigation phrase: "$phrase"',
            );
          }
        }
      }
    });

    test('No step contains outdated color button references', () {
      final allGuides = [
        MorganGuides.invoice,
        MorganGuides.microscope,
        MorganGuides.photo,
        MorganGuides.collection,
        MorganGuides.programs,
      ];

      final outdatedColorPhrases = [
        "red Browse PDF button",
        "blue Browse PDF button",
      ];

      for (final guide in allGuides) {
        for (int i = 0; i < guide.steps.length; i++) {
          final step = guide.steps[i];
          for (final phrase in outdatedColorPhrases) {
            expect(
              step.narration.contains(phrase),
              isFalse,
              reason:
                  'Guide ${guide.id} step $i contains outdated color phrase: "$phrase"',
            );
          }
        }
      }
    });

    test('MorganGuideService supports context-aware initialStep', () {
      final guide = MorganGuides.invoice;

      // Start at default step 0
      MorganGuideService.start(guide);
      expect(MorganGuideService.current.value?.step, 0);

      // Start at action step 1 (skipping redundant intro step)
      MorganGuideService.start(guide, 1);
      expect(MorganGuideService.current.value?.step, 1);

      // Clean up
      MorganGuideService.exit();
      expect(MorganGuideService.current.value, isNull);
    });
  });
}
