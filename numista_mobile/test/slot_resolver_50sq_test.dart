// Numista.AI — Slot Resolver Unit Tests (G3b: 50SQ subject guard)
// Verifies that the program_id fast path requires a subject match for
// multi-design programs (50 State Quarters) so that:
//   - A Tennessee coin does NOT inflate Ohio's Notes count (and vice versa)
//   - Virginia does NOT match a West Virginia coin (theme OR title path)
//   - Blank/generic Theme+Title → both Notes and checkbox dark
//   - resolveProgramInventory quantity is 1 per owned state, not N
//
// All tests are pure Dart — no Firebase, no network, no platform channels.

import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/program_model.dart';
import 'package:numista_ai/utils/slot_resolver.dart';

// ── Test program: minimal 50SQ with two states ───────────────────────────────
final _tnSlot = ProgramCoin(
  id: 'tennessee',
  name: 'Tennessee',
  varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')],
);
final _ohSlot = ProgramCoin(
  id: 'ohio',
  name: 'Ohio',
  varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')],
);
final _50sqProgram = CoinProgram(
  id: '50state',
  name: '50 State Quarters Program',
  url: '',
  years: '1999-2008',
  coins: [_tnSlot, _ohSlot],
);

// ── Coin items ───────────────────────────────────────────────────────────────
final _tnCoin = {
  'program_id': '50state',
  'Theme/Subject': 'Tennessee',
  'Year': '2002',
  'Mint Mark': 'P',
  'Denomination': 'quarter',
};
final _ohCoin = {
  'program_id': '50state',
  'Theme/Subject': 'Ohio',
  'Year': '2002',
  'Mint Mark': 'P',
  'Denomination': 'quarter',
};

void main() {
  // ── Cross-state isolation ─────────────────────────────────────────────────
  group('G3b — 50SQ cross-state isolation (Theme path)', () {
    test('TN coin matches TN slot', () =>
        expect(SlotResolver.isMatch(_tnCoin, _50sqProgram, _tnSlot), isTrue));

    test('TN coin does NOT match OH slot', () =>
        expect(SlotResolver.isMatch(_tnCoin, _50sqProgram, _ohSlot), isFalse));

    test('OH coin does NOT match TN slot', () =>
        expect(SlotResolver.isMatch(_ohCoin, _50sqProgram, _tnSlot), isFalse));

    test('OH coin matches OH slot', () =>
        expect(SlotResolver.isMatch(_ohCoin, _50sqProgram, _ohSlot), isTrue));
  });

  // ── Virginia / West Virginia — theme path ─────────────────────────────────
  group('G3b — Virginia / West Virginia (Theme path)', () {
    final vaSlot = ProgramCoin(
        id: 'virginia', name: 'Virginia',
        varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')]);
    final wvSlot = ProgramCoin(
        id: 'west_virginia', name: 'West Virginia',
        varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')]);
    final program = CoinProgram(
        id: '50state', name: '50 State Quarters Program',
        url: '', years: '1999-2008', coins: [vaSlot, wvSlot]);

    final wvCoin = {
      'program_id': '50state',
      'Theme/Subject': 'West Virginia',
      'Year': '2005',
      'Mint Mark': 'P',
    };

    test('WV theme coin does NOT match Virginia slot', () =>
        expect(SlotResolver.isMatch(wvCoin, program, vaSlot), isFalse));

    test('WV theme coin DOES match West Virginia slot', () =>
        expect(SlotResolver.isMatch(wvCoin, program, wvSlot), isTrue));
  });

  // ── Virginia / West Virginia — title path ─────────────────────────────────
  group('G3b — Virginia / West Virginia (Title path)', () {
    final vaSlot = ProgramCoin(
        id: 'virginia', name: 'Virginia',
        varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')]);
    final wvSlot = ProgramCoin(
        id: 'west_virginia', name: 'West Virginia',
        varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')]);
    final program = CoinProgram(
        id: '50state', name: '50 State Quarters Program',
        url: '', years: '1999-2008', coins: [vaSlot, wvSlot]);

    final wvTitleCoin = {
      'program_id': '50state',
      'Theme/Subject': '',
      'Title': '2000 West Virginia State Quarter',
      'Year': '2000',
      'Mint Mark': 'P',
    };

    test('WV title coin does NOT match Virginia slot', () =>
        expect(SlotResolver.isMatch(wvTitleCoin, program, vaSlot), isFalse));

    test('WV title coin DOES match West Virginia slot', () =>
        expect(SlotResolver.isMatch(wvTitleCoin, program, wvSlot), isTrue));
  });

  // ── Blank Theme/Subject ───────────────────────────────────────────────────
  group('G3b — Blank Theme/Subject -> dark (Notes and checkbox)', () {
    final blankCoin = {
      'program_id': '50state',
      'Theme/Subject': '',
      'Year': '2002',
      'Mint Mark': 'P',
    };

    test('Blank-theme coin does NOT match TN slot', () =>
        expect(SlotResolver.isMatch(blankCoin, _50sqProgram, _tnSlot), isFalse));

    test('Blank-theme coin does NOT match OH slot', () =>
        expect(SlotResolver.isMatch(blankCoin, _50sqProgram, _ohSlot), isFalse));
  });

  // ── resolveProgramInventory integration ──────────────────────────────────
  group('G3b — resolveProgramInventory: no cross-count', () {
    test('TN and OH each count 1, not 2', () {
      final inventory = SlotResolver.resolveProgramInventory(
          program: _50sqProgram, coins: [_tnCoin, _ohCoin]);

      // Key pattern: '${program.id}_${coinSlot.id}_${variety.id}'
      final tnMatch = inventory['50state_tennessee_P-UNC'];
      final ohMatch = inventory['50state_ohio_P-UNC'];

      expect(tnMatch?.isOwned, isTrue);
      expect(tnMatch?.quantity, 1);

      expect(ohMatch?.isOwned, isTrue);
      expect(ohMatch?.quantity, 1);
    });
  });

  // ── Same-length slot names must not cross-match via Title ─────────────────
  group('G3b — same-length slot names: Title path (v4 fix)', () {
    test('NM title coin does NOT match New Jersey slot (both 10 chars)', () {
      final nmSlot = ProgramCoin(
          id: 'new_mexico', name: 'New Mexico',
          varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')]);
      final njSlot = ProgramCoin(
          id: 'new_jersey', name: 'New Jersey',
          varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')]);
      final program = CoinProgram(
          id: '50state', name: '50 State Quarters Program',
          url: '', years: '1999-2008', coins: [nmSlot, njSlot]);
      final nmTitleCoin = {
        'program_id': '50state',
        'Theme/Subject': '',
        'Title': '2000 New Mexico State Quarter',
        'Year': '2000',
        'Mint Mark': 'P',
      };
      expect(SlotResolver.isMatch(nmTitleCoin, program, nmSlot), isTrue);
      expect(SlotResolver.isMatch(nmTitleCoin, program, njSlot), isFalse);
    });

    test('ND title coin does NOT match South Dakota slot (both 12 chars)', () {
      final ndSlot = ProgramCoin(
          id: 'north_dakota', name: 'North Dakota',
          varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')]);
      final sdSlot = ProgramCoin(
          id: 'south_dakota', name: 'South Dakota',
          varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')]);
      final program = CoinProgram(
          id: '50state', name: '50 State Quarters Program',
          url: '', years: '1999-2008', coins: [ndSlot, sdSlot]);
      final ndTitleCoin = {
        'program_id': '50state',
        'Theme/Subject': '',
        'Title': '2006 North Dakota State Quarter',
        'Year': '2006',
        'Mint Mark': 'P',
      };
      expect(SlotResolver.isMatch(ndTitleCoin, program, ndSlot), isTrue);
      expect(SlotResolver.isMatch(ndTitleCoin, program, sdSlot), isFalse);
    });
  });

  // ── G3b v5.1 — heuristic path (no program_id, year-injected slots) ─────────
  // Slots have year set — matching what the checklist injects at render time.
  // Without year on the slot, slotYear="" and L550 never fires in the test,
  // giving a false green even if §5c were deleted. These tests are the real gate.
  group('G3b v5.1 — heuristic path (no program_id, year-injected slots)', () {
    // Slots with year — production-equivalent
    final tnSlotYr = ProgramCoin(
        id: 'tennessee', name: 'Tennessee', year: '2002',
        varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')]);
    final ohSlotYr = ProgramCoin(
        id: 'ohio', name: 'Ohio', year: '2002',
        varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')]);
    final vaSlotYr = ProgramCoin(
        id: 'virginia', name: 'Virginia', year: '2000',
        varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')]);
    final wvSlotYr = ProgramCoin(
        id: 'west_virginia', name: 'West Virginia', year: '2005',
        varieties: [ChecklistVariety(id: 'P-UNC', label: 'P Unc')]);
    final programYr = CoinProgram(
        id: '50state', name: '50 State Quarters Program',
        url: '', years: '1999-2008',
        coins: [tnSlotYr, ohSlotYr, vaSlotYr, wvSlotYr]);

    // Coin data matching live Firestore probe: no program_id, Theme/Subject filled
    final tnHeuristic = {
      // No 'program_id' key — import path
      'Theme/Subject': 'Tennessee',
      'theme_subject': 'Tennessee',
      'Year': '2002',
      'Mint Mark': 'P',
      'Denomination': 'Quarter',
      'Program/Series': '50 State Quarters',
    };
    final wvHeuristic = {
      'Theme/Subject': 'West Virginia',
      'theme_subject': 'West Virginia',
      'Year': '2005',
      'Mint Mark': 'P',
      'Denomination': 'Quarter',
      'Program/Series': '50 State Quarters',
    };
    final blankHeuristic = {
      'Theme/Subject': '',
      'Year': '2002',
      'Mint Mark': 'P',
      'Denomination': 'Quarter',
      'Program/Series': '50 State Quarters',
    };

    test('no-program_id TN coin matches TN slot (slot year = 2002)', () =>
        expect(SlotResolver.isMatch(tnHeuristic, programYr, tnSlotYr), isTrue));

    test('no-program_id TN coin does NOT match OH slot (L550 live — slotYear=2002)', () =>
        expect(SlotResolver.isMatch(tnHeuristic, programYr, ohSlotYr), isFalse));

    test('no-program_id WV Theme coin does NOT match Virginia slot (§5 contains trap closed)', () =>
        expect(SlotResolver.isMatch(wvHeuristic, programYr, vaSlotYr), isFalse));

    test('no-program_id blank-theme coin does NOT match TN slot (dark on all rows)', () =>
        expect(SlotResolver.isMatch(blankHeuristic, programYr, tnSlotYr), isFalse));
  });
}
