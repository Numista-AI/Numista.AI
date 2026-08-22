// Washington Classic Quarters — Slot Resolver Regression Tests
// Covers the fixes in implementation_planv6.md
// Run: flutter test test/slot_resolver_washington_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/program_model.dart';
import 'package:numista_ai/utils/slot_resolver.dart';

// Minimal Washington Classic program for offline test use.
// Uses explicit id 'washington_quarters_classic' (added to JSON by Fix F).
CoinProgram _makeWashingtonClassic() {
  return CoinProgram(
    id: 'washington_quarters_classic',
    name: 'Washington Quarters (Classic)',
    url: '',
    years: '1932-1998',
    coins: [
      ProgramCoin(
        id: 'washington_quarter_1932',
        name: 'Washington Quarter',
        year: '1932',
        varieties: [
          ChecklistVariety(id: 'P', label: 'No Mint Mark'),
          ChecklistVariety(id: 'D', label: 'D'),
          ChecklistVariety(id: 'S', label: 'S'),
        ],
      ),
      ProgramCoin(
        id: 'washington_quarter_1950',
        name: 'Washington Quarter',
        year: '1950',
        varieties: [
          ChecklistVariety(id: 'P', label: 'No Mint Mark'),
          ChecklistVariety(id: 'D', label: 'D'),
          ChecklistVariety(id: 'S', label: 'S'),
          ChecklistVariety(id: 'PROOF', label: 'Proof'),
        ],
      ),
      ProgramCoin(
        id: 'washington_quarter_1965',
        name: 'Washington Quarter',
        year: '1965',
        varieties: [
          ChecklistVariety(id: 'P', label: 'No Mint Mark'),
          ChecklistVariety(id: 'SMS', label: 'SMS'),
        ],
      ),
      ProgramCoin(
        id: 'washington_quarter_1967',
        name: 'Washington Quarter',
        year: '1967',
        varieties: [
          ChecklistVariety(id: 'P', label: 'No Mint Mark'),
          ChecklistVariety(id: 'SMS', label: 'SMS'),
        ],
      ),
      ProgramCoin(
        id: 'washington_quarter_1976',
        name: 'Washington Quarter',
        year: '1976',
        varieties: [
          ChecklistVariety(id: 'P', label: 'No Mint Mark'),
          ChecklistVariety(id: 'D', label: 'D'),
          ChecklistVariety(id: 'S-PROOF', label: 'S Clad Proof'),
          ChecklistVariety(id: 'S-SILVER', label: 'S Silver BU'),
          ChecklistVariety(id: 'S-SILVER-PROOF', label: 'S Silver Proof'),
        ],
      ),
      ProgramCoin(
        id: 'washington_quarter_1992',
        name: 'Washington Quarter',
        year: '1992',
        varieties: [
          ChecklistVariety(id: 'P', label: 'P'),
          ChecklistVariety(id: 'D', label: 'D'),
          ChecklistVariety(id: 'S-PROOF', label: 'S Clad Proof'),
          ChecklistVariety(id: 'S-SILVER-PROOF', label: 'S Silver Proof'),
        ],
      ),
      ProgramCoin(
        id: 'washington_quarter_1938',
        name: 'Washington Quarter',
        year: '1938',
        varieties: [
          ChecklistVariety(id: 'P', label: 'No Mint Mark'),
          ChecklistVariety(id: 'S', label: 'S'),
          ChecklistVariety(id: 'PROOF', label: 'Proof'),
        ],
      ),
    ],
  );
}

void main() {
  final program = _makeWashingtonClassic();

  int ownedCount(Map<String, dynamic> coin) {
    final result = SlotResolver.resolveProgramInventory(
      program: program,
      coins: [coin],
    );
    return result.values.where((r) => r.isOwned).length;
  }

  bool mv(Map<String, dynamic> coin, String varietyId) {
    return SlotResolver.matchesVariety(
      coin,
      ChecklistVariety(id: varietyId, label: varietyId),
    );
  }

  group('Test 1 — SNAP four-coin fixture → 0 owned', () {
    test('1a. 2021-P Washington Quarter series MS-63', () {
      expect(ownedCount({'Year': '2021', 'Mint Mark': 'P',
        'Program/Series': 'Washington Quarter',
        'Denomination': 'Quarter Dollar', 'Condition': 'MS-63',
        'country': 'United States'}), equals(0));
    });
    test('1b. 2021-D no Program/Series', () {
      expect(ownedCount({'Year': '2021', 'Mint Mark': 'D',
        'Program/Series': '', 'Denomination': 'Quarter Dollar',
        'Condition': 'Raw'}), equals(0));
    });
    test('1c. 2021 ATB series', () {
      expect(ownedCount({'Year': '2021', 'Mint Mark': 'P',
        'Program/Series': 'America the Beautiful',
        'Denomination': 'Quarter Dollar', 'Condition': 'MS-65'}), equals(0));
    });
    test('1d. Undated Washington Quarter coin (empty Year)', () {
      expect(ownedCount({'Year': '', 'Mint Mark': 'P',
        'Program/Series': 'Washington Quarter',
        'Denomination': 'Quarter Dollar', 'Condition': 'VF-20'}), equals(0));
    });
  });

  group('Test 2 — 1965 raw unmarked → NMM not SMS', () {
    final coin = {'Year': '1965', 'Mint Mark': '', 'Strike Type': '',
      'Denomination': 'Quarter Dollar', 'Condition': 'F-12'};
    test('P/NMM = true',  () => expect(mv(coin, 'P'),   isTrue));
    test('SMS = false',    () => expect(mv(coin, 'SMS'), isFalse));
  });

  group('Test 3 — 1965 SP67 → SMS only NOT NMM (double-stamp fix)', () {
    final coin = {'Year': '1965', 'Mint Mark': '', 'Strike Type': '',
      'Denomination': 'Quarter Dollar', 'Condition': 'SP67'};
    test('SMS = true',                  () => expect(mv(coin, 'SMS'), isTrue));
    test('P/NMM = false (!isSMS gate)', () => expect(mv(coin, 'P'),   isFalse));
  });

  group('Test 3b — 1967 SP-67 hyphen → SMS only (widened regex)', () {
    final coin = {'Year': '1967', 'Mint Mark': '', 'Strike Type': '',
      'Denomination': 'Quarter Dollar', 'Condition': 'SP-67'};
    test('SMS = true',    () => expect(mv(coin, 'SMS'), isTrue));
    test('P/NMM = false', () => expect(mv(coin, 'P'),   isFalse));
  });

  group('Test 4 — 1950 PR65 unmarked → PROOF not NMM', () {
    final coin = {'Year': '1950', 'Mint Mark': '', 'Strike Type': '',
      'Denomination': 'Quarter Dollar', 'Condition': 'PR65'};
    test('PROOF = true',              () => expect(mv(coin, 'PROOF'), isTrue));
    test('P/NMM = false (!isProof)',  () => expect(mv(coin, 'P'),     isFalse));
  });

  group('Test 5 — 1976-S silver proof → S-SILVER-PROOF only', () {
    final coin = {'Year': '1976', 'Mint Mark': 'S', 'Strike Type': 'PROOF',
      'Metal Content': 'SILVER', 'Denomination': 'Quarter Dollar'};
    test('S-SILVER-PROOF = true',       () => expect(mv(coin, 'S-SILVER-PROOF'), isTrue));
    test('S-PROOF = false (!isSilver)', () => expect(mv(coin, 'S-PROOF'),        isFalse));
    test('S-SILVER = false (!isProof)', () => expect(mv(coin, 'S-SILVER'),       isFalse));
  });

  group('Test 6 — 1992-S silver proof → S-SILVER-PROOF only', () {
    final coin = {'Year': '1992', 'Mint Mark': 'S', 'Strike Type': 'PROOF',
      'Metal Content': 'SILVER', 'Denomination': 'Quarter Dollar'};
    test('S-SILVER-PROOF = true', () => expect(mv(coin, 'S-SILVER-PROOF'), isTrue));
    test('S-PROOF = false',       () => expect(mv(coin, 'S-PROOF'),        isFalse));
  });

  group('Test 6b — 1992-S PR69 silver (empty strike_type) → S-SILVER-PROOF', () {
    final coin = {'Year': '1992', 'Mint Mark': 'S', 'Strike Type': '',
      'Metal Content': 'SILVER', 'Denomination': 'Quarter Dollar',
      'Condition': 'PR69'};
    test('S-SILVER-PROOF = true (PR69 triggers isProof)', () {
      expect(mv(coin, 'S-SILVER-PROOF'), isTrue);
    });
    test('S-SILVER = false',  () => expect(mv(coin, 'S-SILVER'), isFalse));
    test('S-PROOF = false',   () => expect(mv(coin, 'S-PROOF'),  isFalse));
  });

  group('Test 7 — 1938-D → no Classic slot', () {
    test('1938-D owns nothing', () {
      expect(ownedCount({'Year': '1938', 'Mint Mark': 'D',
        'Program/Series': 'Washington Quarter',
        'Denomination': 'Quarter Dollar'}), equals(0));
    });
  });

  group('Test 8 — Integer year handled by toString()', () {
    test('year int 2021 → 0 owned Classic slots', () {
      expect(ownedCount({'Year': 2021, 'Mint Mark': 'P',
        'Program/Series': 'Washington Quarter',
        'Denomination': 'Quarter Dollar'}), equals(0));
    });
  });
}
