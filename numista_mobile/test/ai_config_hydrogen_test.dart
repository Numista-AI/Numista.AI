import 'package:firebase_ai/firebase_ai.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/config/ai_config.dart';

void main() {
  group('AiConfig Hydrogen P5 Contract', () {
    test('defaultFlashModel is gemini-4-hydrogen', () {
      expect(AiConfig.defaultFlashModel, equals('gemini-4-hydrogen'));
    });

    test('buildFlashGenerationConfig sets thinkingLevel on gemini-4-hydrogen with no temperature/topP/topK', () {
      final lowCfg = AiConfig.buildFlashGenerationConfig(
        'gemini-4-hydrogen',
        level: ThinkingLevel.low,
        responseMimeType: 'application/json',
      );
      final lowJson = lowCfg.toJson();
      expect(lowJson['responseMimeType'], equals('application/json'));
      expect(lowJson['temperature'], isNull);
      expect(lowJson['topP'], isNull);
      expect(lowJson['topK'], isNull);
      expect(lowJson['thinkingConfig'], isNotNull);
      expect((lowJson['thinkingConfig'] as Map<String, dynamic>)['thinkingLevel'], isNotNull);

      final medCfg = AiConfig.buildFlashGenerationConfig(
        'gemini-4-hydrogen',
        level: ThinkingLevel.medium,
      );
      final medJson = medCfg.toJson();
      expect(medJson['temperature'], isNull);
      expect(medJson['topP'], isNull);
      expect(medJson['topK'], isNull);
      expect(medJson['thinkingConfig'], isNotNull);
      expect((medJson['thinkingConfig'] as Map<String, dynamic>)['thinkingLevel'], isNotNull);
    });

    test('buildFlashGenerationConfig omits thinkingConfig on rollback gemini-3.8-flash', () {
      final rollbackCfg = AiConfig.buildFlashGenerationConfig(
        'gemini-3.8-flash',
        level: ThinkingLevel.low,
        responseMimeType: 'application/json',
      );
      final rollbackJson = rollbackCfg.toJson();
      expect(rollbackJson['thinkingConfig'], isNull);
      expect(rollbackJson['temperature'], isNull);
      expect(rollbackJson['topP'], isNull);
      expect(rollbackJson['topK'], isNull);
    });
  });
}
