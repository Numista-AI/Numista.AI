// test/slot_resolver_collectibles_test.dart
//
// Regression tests for the collectibles product-family guard in SlotResolver.isMatch().
// Fixtures match Eric's actual Firestore coins (26EA, 26XL) plus corrected
// Mint item identities (26XE = Morgan EU per US Mint harvest report, NOT ASE EU;
// 26EG = ASE EU).
//
// flutter test test/slot_resolver_collectibles_test.dart  must exit 0.

import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/program_model.dart';
import 'package:numista_ai/utils/slot_resolver.dart';

// ── Shared program stub ──────────────────────────────────────────────────────

CoinProgram _collectiblesProgram({required List<ProgramCoin> coins}) => CoinProgram(
  id: '2026_semiquincentennial_collectibles',
  url: '',
  name: '2026 America250 - Numismatic Collectibles',
  years: '2026',
  category: 'Collectible Programs',
  coins: coins,
  mintMarkLocations: 'MIXED',
);

// ── Coin fixtures (verbatim from Firestore via show_coin_fields.py) ──────────

/// 26EA — American Eagle 2026 One Ounce Silver Proof Coin (West Point, 250 privy)
final Map<String, dynamic> coin26EA = {
  'Program/Series': 'American Silver Eagle',
  'Year': '2026',
  'Mint Mark': 'W',
  'Condition': 'Proof',
  'Variety': '250 Privy / W-PROOF',
  'Denomination': 'Dollar',
  'Country': 'United States',
};

/// 26XL — Peace Silver Dollar 2026 Reverse Proof Coin (Philadelphia, blank mint mark)
final Map<String, dynamic> coin26XL = {
  'Program/Series': 'Peace Dollar',
  'Year': '2026',
  'Mint Mark': '',
  'Condition': 'Reverse Proof',
  'Variety': 'Reverse Proof',
  'Denomination': 'Dollar',
  'Country': 'United States',
};

/// 26XE — Morgan Silver Dollar 2026 Enhanced Uncirculated Coin (West Point)
/// Item 26XE is MORGAN EU — not ASE EU (26EG). Do not confuse.
final Map<String, dynamic> coin26XE = {
  'Program/Series': 'Morgan Dollar',
  'Year': '2026',
  'Mint Mark': 'W',
  'Condition': 'Uncirculated',
  'Variety': 'Enhanced Uncirculated',
  'Denomination': 'Dollar',
  'Country': 'United States',
};

/// 26EG — American Eagle 2026 One Ounce Silver Enhanced Uncirculated Coin (West Point)
final Map<String, dynamic> coin26EG = {
  'Program/Series': 'American Silver Eagle',
  'Year': '2026',
  'Mint Mark': 'W',
  'Condition': 'Uncirculated',
  'Variety': 'Enhanced Uncirculated',
  'Denomination': 'Dollar',
  'Country': 'United States',
};

/// Hypothetical Iowa Innovation dollar
final Map<String, dynamic> coinIowaInnovation = {
  'Program/Series': 'American Innovation',
  'Theme/Subject': 'Iowa',
  'Year': '2026',
  'Mint Mark': 'P',
  'Denomination': 'Dollar',
  'Country': 'United States',
};

// ── Slot fixtures (ProgramCoin with productFamily set) ──────────────────────

ProgramCoin _slot(String id, String name, String family, String varietyId) =>
    ProgramCoin(
      id: id,
      name: name,
      year: '2026',
      productFamily: family,
      varieties: [ChecklistVariety(id: varietyId, label: varietyId)],
    );

final slotMorganRP  = _slot('2026_morgan_reverse_proof',
    '2026 Morgan Silver Dollar Reverse Proof', 'morgan', 'P-REVERSE-PROOF');
final slotPeaceRP   = _slot('2026_peace_silver_dollar_reverse_proof',
    '2026 Peace Silver Dollar Reverse Proof', 'peace', 'P-REVERSE-PROOF');
final slotMorganEU  = _slot('2026_morgan_silver_dollar_enhanced_uncirculated',
    '2026 Morgan Silver Dollar Enhanced Uncirculated', 'morgan', 'EU');
final slotPeaceEU   = _slot('2026_peace_silver_dollar_enhanced_uncirculated',
    '2026 Peace Silver Dollar Enhanced Uncirculated', 'peace', 'EU');
final slotASEProof  = _slot('2026_american_eagle_one_ounce_silver_proof_coin',
    '2026 American Eagle One Ounce Silver Proof Coin', 'ase', 'W-PROOF');
final slotASEEU     = _slot('2026_american_eagle_one_ounce_silver_enhanced_uncirculated_coin',
    '2026 American Eagle One Ounce Silver Enhanced Uncirculated Coin', 'ase', 'W-EU');
final slotASECong   = _slot('2026_american_eagle_one_ounce_silver_proof_coin_congratulations_set',
    '2026 American Eagle One Ounce Silver Proof Coin (Congratulations Set)', 'ase', 'P-PROOF-CONG');
final slotAGEProof  = _slot('2026_american_eagle_one_ounce_gold_proof_coin',
    '2026 American Eagle One Ounce Gold Proof Coin', 'age', 'W-PROOF');
final slotAGEEU     = _slot('2026_american_eagle_one_ounce_gold_enhanced_uncirculated_coin',
    '2026 American Eagle One Ounce Gold Enhanced Uncirculated Coin', 'age', 'W-EU');
final slotBuffalo   = _slot('2026_american_buffalo_one_ounce_gold_proof_coin',
    '2026 American Buffalo One Ounce Gold Proof Coin', 'buffalo', 'W-PROOF');
final slotInnIowa   = _slot('2026_american_innovation_1_iowa',
    '2026 American Innovation \\ - Iowa', 'innovation:iowa', 'P');
final slotInnWisc   = _slot('2026_american_innovation_1_wisconsin',
    '2026 American Innovation \\ - Wisconsin', 'innovation:wisconsin', 'P');
final slotInnCalif  = _slot('2026_american_innovation_1_california',
    '2026 American Innovation \\ - California', 'innovation:california', 'P');
final slotInnMinn   = _slot('2026_american_innovation_1_minnesota',
    '2026 American Innovation \\ - Minnesota', 'innovation:minnesota', 'P');

bool _isMatch(Map<String, dynamic> coin, ProgramCoin slot) =>
    SlotResolver.isMatch(coin, _collectiblesProgram(coins: [slot]), slot);

void main() {
  group('SlotResolver collectibles guard', () {

    // Must-true: exactly 2
    test('26XL Peace Reverse Proof ticks Peace RP slot (correct 1 of 2)', () {
      expect(_isMatch(coin26XL, slotPeaceRP), isTrue);
    });

    test('26EA ASE W-Proof ticks ASE Silver Proof slot (correct 2 of 2)', () {
      expect(_isMatch(coin26EA, slotASEProof), isTrue);
    });

    // Must-false: the 5 false ticks from Try 4
    test('26XL Peace RP does NOT tick Morgan RP slot (Stage 1: wrong product family)', () {
      expect(_isMatch(coin26XL, slotMorganRP), isFalse);
    });

    test('26EA ASE does NOT tick AGE Gold Proof slot (Stage 1: ase != age)', () {
      expect(_isMatch(coin26EA, slotAGEProof), isFalse);
    });

    test('26EA ASE does NOT tick Buffalo Gold Proof slot (Stage 1: ase != buffalo)', () {
      expect(_isMatch(coin26EA, slotBuffalo), isFalse);
    });

    test('26EA ASE Proof does NOT tick ASE Congratulations slot (Stage 2: no cong in Variety)', () {
      expect(_isMatch(coin26EA, slotASECong), isFalse);
    });

    test('26XL Peace RP does NOT tick Morgan EU slot (Stage 2: RP coin cannot tick EU slot)', () {
      expect(_isMatch(coin26XL, slotMorganEU), isFalse);
    });

    test('26EA ASE Proof does NOT tick ASE EU slot (Stage 2: plain Proof cannot tick EU slot)', () {
      expect(_isMatch(coin26EA, slotASEEU), isFalse);
    });

    // 26XE fixture identity: Morgan EU, not ASE EU
    test('26XE (Morgan EU) ticks Morgan EU slot', () {
      expect(_isMatch(coin26XE, slotMorganEU), isTrue);
    });

    test('26XE (Morgan EU) does NOT tick Peace EU slot (Stage 1: morgan != peace)', () {
      expect(_isMatch(coin26XE, slotPeaceEU), isFalse);
    });

    test('26XE (Morgan EU) does NOT tick ASE EU slot (Stage 1: morgan != ase)', () {
      expect(_isMatch(coin26XE, slotASEEU), isFalse);
    });

    test('26EG (ASE EU) ticks ASE EU slot', () {
      expect(_isMatch(coin26EG, slotASEEU), isTrue);
    });

    test('26EG (ASE EU) does NOT tick AGE EU slot (Stage 1: ase != age)', () {
      expect(_isMatch(coin26EG, slotAGEEU), isFalse);
    });

    // Innovation state isolation
    test('Iowa dollar ticks Iowa slot only', () {
      expect(_isMatch(coinIowaInnovation, slotInnIowa), isTrue);
    });

    test('Iowa dollar does NOT tick Wisconsin slot (exact equality blocks)', () {
      expect(_isMatch(coinIowaInnovation, slotInnWisc), isFalse);
    });

    test('Iowa dollar does NOT tick California slot', () {
      expect(_isMatch(coinIowaInnovation, slotInnCalif), isFalse);
    });

    test('Iowa dollar does NOT tick Minnesota slot', () {
      expect(_isMatch(coinIowaInnovation, slotInnMinn), isFalse);
    });

    test('26EA ASE does NOT tick Iowa Innovation slot (wrong family entirely)', () {
      expect(_isMatch(coin26EA, slotInnIowa), isFalse);
    });

    // Empty productFamily safety
    test('Slot with empty productFamily always returns false (safe reject)', () {
      final slotNoFamily = ProgramCoin(
        id: 'unknown_slot',
        name: '2026 Unknown Coin',
        year: '2026',
        productFamily: '',
        varieties: [ChecklistVariety(id: 'W-PROOF', label: 'W-PROOF')],
      );
      expect(_isMatch(coin26EA, slotNoFamily), isFalse);
    });

  });
}
