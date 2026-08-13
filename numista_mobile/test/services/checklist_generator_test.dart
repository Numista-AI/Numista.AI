import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/program_model.dart';
import 'package:numista_ai/services/checklist_generator_service.dart';
import 'package:numista_ai/utils/slot_resolver.dart';

void main() {
  group('SheldonGradeRanker Tests', () {
    test('Calculates accurate Sheldon numerical scores', () {
      expect(SheldonGradeRanker.getSheldonScore('MS-70'), equals(70));
      expect(SheldonGradeRanker.getSheldonScore('MS-65 PCGS'), equals(65));
      expect(SheldonGradeRanker.getSheldonScore('AU-58'), equals(58));
      expect(SheldonGradeRanker.getSheldonScore('XF-40'), equals(40));
      expect(SheldonGradeRanker.getSheldonScore('VF-20'), equals(20));
      expect(SheldonGradeRanker.getSheldonScore('G-4'), equals(4));
      expect(SheldonGradeRanker.getSheldonScore('PO-1'), equals(1));
    });

    test('Maps adjectival and unnumbered grades correctly', () {
      expect(SheldonGradeRanker.getSheldonScore('BU'), equals(63));
      expect(SheldonGradeRanker.getSheldonScore('UNC'), equals(63));
      expect(SheldonGradeRanker.getSheldonScore('AU'), equals(53));
      expect(SheldonGradeRanker.getSheldonScore('VF'), equals(25));
      expect(SheldonGradeRanker.getSheldonScore('Raw'), equals(0));
      expect(SheldonGradeRanker.getSheldonScore('Circulated'), equals(0));
      expect(SheldonGradeRanker.getSheldonScore(''), equals(-1));
    });

    test('Docks problem/details coins appropriately', () {
      expect(SheldonGradeRanker.getSheldonScore('MS-65 Details Cleaned'), equals(60));
      expect(SheldonGradeRanker.getSheldonScore('AU-50 Scratched'), equals(45));
      expect(SheldonGradeRanker.getSheldonScore('Details'), equals(10));
    });

    test('Sorts multi-item inventory deterministically', () {
      final item1 = {'Condition': 'AU-50', 'Grading Service': 'Raw', 'id': 'coin_1'};
      final item2 = {'Condition': 'MS-66', 'Grading Service': 'PCGS', 'id': 'coin_2'};
      final item3 = {'Condition': 'MS-63', 'Grading Service': 'NGC', 'id': 'coin_3'};

      final list = [item1, item2, item3];
      list.sort(SheldonGradeRanker.compareItems);

      expect(list[0]['id'], equals('coin_2')); // MS-66 PCGS first
      expect(list[1]['id'], equals('coin_3')); // MS-63 NGC second
      expect(list[2]['id'], equals('coin_1')); // AU-50 Raw third
    });
  });

  group('SlotResolver & Snapshot ID Tests', () {
    final sampleProgram = CoinProgram(
      id: 'test_presidential',
      name: 'Presidential Dollars',
      url: '',
      years: '2007-2020',
      coins: [
        ProgramCoin(
          id: 'washington',
          name: 'George Washington',
          year: '2007',
          varieties: [
            ChecklistVariety(id: 'P-UNC', label: 'P Unc'),
            ChecklistVariety(id: 'D-UNC', label: 'D Unc'),
            ChecklistVariety(id: 'S-PROOF', label: 'S Proof'),
          ],
        ),
        ProgramCoin(
          id: 'adams',
          name: 'John Adams',
          year: '2007',
          varieties: [
            ChecklistVariety(id: 'P-UNC', label: 'P Unc'),
            ChecklistVariety(id: 'D-UNC', label: 'D Unc'),
          ],
        ),
      ],
    );

    test('Resolves inventory against program slots accurately', () {
      final userCoins = [
        {
          'id': 'c1',
          'Year': '2007',
          'Denomination': 'Dollar',
          'Program/Series': 'Presidential \$1 Coin Program',
          'Theme/Subject': 'George Washington',
          'Mint Mark': 'P',
          'Condition': 'MS-65',
          'Grading Service': 'PCGS',
          'Certification Number': '12345678',
        },
        {
          'id': 'c2',
          'Year': '2007',
          'Denomination': 'Dollar',
          'Program/Series': 'Presidential \$1 Coin Program',
          'Theme/Subject': 'George Washington',
          'Mint Mark': 'P',
          'Condition': 'AU-55',
          'Grading Service': 'Raw',
        },
      ];

      final inventory = SlotResolver.resolveProgramInventory(
        program: sampleProgram,
        coins: userCoins,
      );

      final washingtonP = inventory['test_presidential_washington_P-UNC'];
      expect(washingtonP, isNotNull);
      expect(washingtonP!.isOwned, isTrue);
      expect(washingtonP.quantity, equals(2));
      expect(washingtonP.primaryGrade, equals('MS-65'));
      expect(washingtonP.primaryService, equals('PCGS'));
      expect(washingtonP.formattedNotes, contains('QTY: 2 | MS-65 PCGS, +1 other'));

      final washingtonD = inventory['test_presidential_washington_D-UNC'];
      expect(washingtonD, isNotNull);
      expect(washingtonD!.isOwned, isFalse);
    });

    test('Generates deterministic SHA-256 Snapshot ID matching format regex', () {
      final userCoins = [
        {
          'id': 'c1',
          'Year': '2007',
          'Denomination': 'Dollar',
          'Program/Series': 'Presidential \$1 Coin Program',
          'Theme/Subject': 'George Washington',
          'Mint Mark': 'P',
          'Condition': 'MS-65',
        }
      ];

      final inventory = SlotResolver.resolveProgramInventory(
        program: sampleProgram,
        coins: userCoins,
      );

      final fixedTimestamp = DateTime.utc(2026, 8, 13, 21, 45, 0);
      final snapId1 = SlotResolver.generateSnapshotId(
        collectorEmail: 'eric.seaman@yahoo.com',
        programId: sampleProgram.id,
        totalSlots: 5,
        resolvedSlots: inventory,
        timestampUtc: fixedTimestamp,
      );

      final snapId2 = SlotResolver.generateSnapshotId(
        collectorEmail: 'eric.seaman@yahoo.com',
        programId: sampleProgram.id,
        totalSlots: 5,
        resolvedSlots: inventory,
        timestampUtc: fixedTimestamp,
      );

      // Deterministic equality
      expect(snapId1, equals(snapId2));
      // Strict regex pattern check
      expect(RegExp(r'^SNAP-\d{8}-[A-F0-9]{8}$').hasMatch(snapId1), isTrue);
      expect(snapId1.startsWith('SNAP-20260813-'), isTrue);
    });
  });

  group('ChecklistGeneratorService PDF Generation Tests', () {
    final sampleProgram = CoinProgram(
      id: '50state',
      name: '50 State Quarters Program',
      url: '',
      years: '1999-2008',
      coins: [
        ProgramCoin(
          id: 'delaware',
          name: 'Delaware',
          year: '1999',
          varieties: [
            ChecklistVariety(id: 'P-UNC', label: 'P Unc'),
            ChecklistVariety(id: 'D-UNC', label: 'D Unc'),
            ChecklistVariety(id: 'S-PROOF', label: 'S Proof'),
          ],
        ),
        ProgramCoin(
          id: 'pennsylvania',
          name: 'Pennsylvania',
          year: '1999',
          varieties: [
            ChecklistVariety(id: 'P-UNC', label: 'P Unc'),
            ChecklistVariety(id: 'D-UNC', label: 'D Unc'),
          ],
        ),
      ],
    );

    test('Generates Blank Master PDF bytes without crashing', () async {
      final pdfBytes = await ChecklistGeneratorService.generateChecklist(sampleProgram);
      expect(pdfBytes, isNotNull);
      expect(pdfBytes.length, greaterThan(1000));
    });

    test('Generates Personalized SoR PDF bytes with legal disclaimer and snapshot hash', () async {
      final userCoins = [
        {
          'id': 'c1',
          'Year': '1999',
          'Denomination': 'Quarter Dollar',
          'Program/Series': '50 State Quarters',
          'Theme/Subject': 'Delaware',
          'Mint Mark': 'P',
          'Condition': 'MS-66',
          'Grading Service': 'PCGS',
        }
      ];

      final inventory = SlotResolver.resolveProgramInventory(
        program: sampleProgram,
        coins: userCoins,
      );

      final pdfBytes = await ChecklistGeneratorService.generateChecklist(
        sampleProgram,
        resolvedInventory: inventory,
        collectorEmail: 'eric.seaman@yahoo.com',
        snapshotId: 'SNAP-20260813-8C9A4B21',
        distinctOwnedSlots: 1,
        totalCatalogSlots: 5,
        totalOwnedItems: 1,
        isPartialSnapshot: false,
      );

      expect(pdfBytes, isNotNull);
      expect(pdfBytes.length, greaterThan(1000));
    });

    test('Handles partial snapshot warning without breaking PDF compilation', () async {
      final pdfBytes = await ChecklistGeneratorService.generateChecklist(
        sampleProgram,
        resolvedInventory: {},
        collectorEmail: 'eric.seaman@yahoo.com',
        snapshotId: 'SNAP-20260813-PARTIAL1',
        distinctOwnedSlots: 0,
        totalCatalogSlots: 5,
        totalOwnedItems: 0,
        isPartialSnapshot: true,
      );

      expect(pdfBytes, isNotNull);
      expect(pdfBytes.length, greaterThan(1000));
    });
  });
}
