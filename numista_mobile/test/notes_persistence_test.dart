import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/screens/coin_detail_screen.dart';

void main() {
  group('D1 Personal Notes read priority & targeted persistence', () {
    test('Read priority checks Personal Notes I -> Personal Notes -> personalNotes -> Notes -> notes, skipping blanks', () {
      expect(
        CoinModel.fromMap({
          'Notes': '',
          'Personal Notes': '',
          'Personal Notes I': '  Mint state obverse  ',
        }, 'c1').personalNotes,
        'Mint state obverse',
      );

      expect(
        CoinModel.fromMap({
          'notes': 'oldest lowercase',
          'Notes': 'legacy notes',
          'personalNotes': 'camel notes',
          'Personal Notes': 'spaced notes',
          'Personal Notes I': 'primary notes',
        }, 'c2').personalNotes,
        'primary notes',
      );

      expect(
        CoinModel.fromMap({
          'Personal Notes I': '   ',
          'Personal Notes': 'secondary spaced',
          'Notes': 'legacy notes',
        }, 'c3').personalNotes,
        'secondary spaced',
      );

      expect(
        CoinModel.fromMap({
          'Personal Notes I': null,
          'Personal Notes': '',
          'personalNotes': 'camel fallback',
          'Notes': 'legacy notes',
        }, 'c4').personalNotes,
        'camel fallback',
      );

      expect(
        CoinModel.fromMap({
          'Notes': 'legacy fallback',
          'notes': 'lowercase fallback',
        }, 'c5').personalNotes,
        'legacy fallback',
      );

      expect(
        CoinModel.fromMap({'notes': 'lowest fallback'}, 'c6').personalNotes,
        'lowest fallback',
      );

      expect(
        CoinModel.fromMap({'Notes': '', 'Personal Notes': '  '}, 'c7').personalNotes,
        '',
      );
    });

    test('Write-path (a): Saved note updates targeted keys and survives Firestore reload', () {
      final storedDoc = <String, dynamic>{
        'Year': '1921',
        'Denomination': '1',
        'Notes': '',
        'Personal Notes': '',
      };

      final updates = <String, dynamic>{'Year': '1921'};
      CoinDetailScreen.applyTargetedNotesUpdate(
        updates,
        initialNotes: CoinModel.fromMap(storedDoc, 'c_save').personalNotes,
        editedNotes: '  PQ toning  ',
      );

      expect(updates['Personal Notes I'], 'PQ toning');
      expect(updates['Personal Notes'], 'PQ toning');
      expect(updates['Notes'], 'PQ toning');

      final afterSave = {...storedDoc, ...updates};
      final reloaded = CoinModel.fromMap(afterSave, 'c_save');
      expect(reloaded.personalNotes, 'PQ toning');
    });

    test('Write-path (b): Saving an unrelated field omits all notes keys and preserves existing Personal Notes I', () {
      final storedDoc = <String, dynamic>{
        'Year': '1889',
        'Condition': 'MS-64',
        'Personal Notes I': 'mint error',
        'Personal Notes': 'mint error',
        'Notes': 'mint error',
      };

      // Simulate user editing only Condition without changing Personal Notes.
      final loaded = CoinModel.fromMap(storedDoc, 'c_unrelated');
      final updates = <String, dynamic>{
        'Condition': 'MS-65',
      };
      CoinDetailScreen.applyTargetedNotesUpdate(
        updates,
        initialNotes: loaded.personalNotes,
        editedNotes: loaded.personalNotes,
      );

      for (final key in const [
        'Personal Notes I',
        'Personal Notes',
        'personalNotes',
        'Notes',
        'notes',
      ]) {
        expect(updates.containsKey(key), isFalse, reason: 'Unrelated edit must not write $key');
      }

      final afterSave = {...storedDoc, ...updates};
      final reloaded = CoinModel.fromMap(afterSave, 'c_unrelated');
      expect(reloaded.condition, 'MS-65');
      expect(reloaded.personalNotes, 'mint error');
    });

    test('Write-path (c): Explicit clear writes empty string to all 3 keys so old note does not resurrect on reload', () {
      final storedDoc = <String, dynamic>{
        'Personal Notes I': 'old',
        'Personal Notes': 'old',
        'Notes': 'old',
      };

      final updates = <String, dynamic>{};
      CoinDetailScreen.applyTargetedNotesUpdate(
        updates,
        initialNotes: 'old',
        editedNotes: '   ',
      );

      expect(updates['Personal Notes I'], '');
      expect(updates['Personal Notes'], '');
      expect(updates['Notes'], '');

      final afterSave = {...storedDoc, ...updates};
      final reloaded = CoinModel.fromMap(afterSave, 'c_clear');
      expect(reloaded.personalNotes, '');
    });
  });
}
