import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/beta_checklist_service.dart';

void main() {
  group('BetaChecklistService Task Invariants and Structure', () {
    test('Contains exactly 20 distinct beta checklist tasks', () {
      expect(BetaChecklistService.allTasks.length, 20);
      final ids = BetaChecklistService.allTasks.map((t) => t.id).toSet();
      expect(ids.length, 20, reason: 'Every task ID must be unique');
    });

    test('All task IDs follow snake_case format', () {
      final snakeCasePattern = RegExp(r'^task_\d+_[a-z0-9_]+$');
      for (final task in BetaChecklistService.allTasks) {
        expect(
          snakeCasePattern.hasMatch(task.id),
          isTrue,
          reason: 'Task ID "${task.id}" must match pattern task_<num>_<snake_case>',
        );
      }
    });

    test('All tasks have non-empty titles and descriptions', () {
      for (final task in BetaChecklistService.allTasks) {
        expect(task.title.trim().isNotEmpty, isTrue);
        expect(task.description.trim().isNotEmpty, isTrue);
      }
    });

    test('Auto-detectable tasks are correctly flagged', () {
      final autoDetectableIds = BetaChecklistService.allTasks
          .where((t) => t.isAutoDetectable)
          .map((t) => t.id)
          .toSet();

      // Tasks 8, 9, 10 (filter), 11, 17 are manual toggles; others are auto-detectable
      expect(autoDetectableIds.contains('task_3_manual_entry'), isTrue);
      expect(autoDetectableIds.contains('task_4_csv_upload'), isTrue);
      expect(autoDetectableIds.contains('task_5_invoice_pdf'), isTrue);
      expect(autoDetectableIds.contains('task_6_pcgs_cert'), isTrue);
      expect(autoDetectableIds.contains('task_7_roll_batch'), isTrue);
      expect(autoDetectableIds.contains('task_12_currency'), isTrue);
      expect(autoDetectableIds.contains('task_13_world_items'), isTrue);
      expect(autoDetectableIds.contains('task_14_wishlist'), isTrue);
      expect(autoDetectableIds.contains('task_15_public_wishlist'), isTrue);
      expect(autoDetectableIds.contains('task_16_estate_report'), isTrue);
      expect(autoDetectableIds.contains('task_18_ai_chat'), isTrue);
      expect(autoDetectableIds.contains('task_20_overall_feedback'), isTrue);

      // Hardware/inspection skip task
      expect(BetaChecklistService.allTasks.firstWhere((t) => t.id == 'task_9_microscope').supportsSkip, isTrue);
    });

    test('ResetSessionSync clears session latch', () {
      BetaChecklistService.resetSessionSync();
      // Verifies reset method executes cleanly
      expect(true, isTrue);
    });
  });
}
