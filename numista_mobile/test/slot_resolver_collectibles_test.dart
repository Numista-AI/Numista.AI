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

  // ── Annual Uncirculated Set — D-UNC blank-mint guard ─────────────────────────
  // Regression for the 26RJ annual set (eric.seaman@yahoo.com/coins/71e2d4ae…).
  // The set has no Mint Mark field. P-UNC must tick; D-UNC must tick.
  // Individual non-set coins with blank mint must NOT tick D-UNC.

  final Map<String, dynamic> annualSet2026 = {
    'Denomination': 'Set',
    'Program/Series': 'Uncirculated Sets',
    'Year': '2026',
    'Condition': 'Uncirculated',
    'Theme/Subject': '250th Anniversary Uncirculated Coin Set',
    'name': '2026 United States Mint Uncirculated Coin Set',
    'Country': 'United States',
    'is_set': true,
    // No 'Mint Mark' field — verbatim from Firestore doc 71e2d4ae
  };

  final Map<String, dynamic> coinBlankMintNotASet = {
    'Denomination': 'Quarter Dollar (25C)',
    'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
    'Year': '2026',
    'Condition': 'UNC',
    'Theme/Subject': 'Mayflower Compact & Pilgrim Couple',
    'Country': 'United States',
    // No Mint Mark, NOT a set
  };

  final ChecklistVariety vPUnc = ChecklistVariety(id: 'P-UNC', label: 'P (Uncirculated)');
  final ChecklistVariety vDUnc = ChecklistVariety(id: 'D-UNC', label: 'D (Uncirculated)');
  final ChecklistVariety vSProof = ChecklistVariety(id: 'S-PROOF', label: 'S (Proof - Clad)');

  group('Annual Uncirculated Set — D-UNC blank-mint guard', () {

    test('Annual set ticks P-UNC (existing blank-mint-P guard)', () {
      expect(SlotResolver.matchesVariety(annualSet2026, vPUnc), isTrue);
    });

    test('Annual set ticks D-UNC (new blank-mint-D set guard)', () {
      expect(SlotResolver.matchesVariety(annualSet2026, vDUnc), isTrue);
    });

    test('Annual set does NOT tick S-PROOF (no S mint mark in set)', () {
      expect(SlotResolver.matchesVariety(annualSet2026, vSProof), isFalse);
    });

    test('Non-set coin with blank mint does NOT tick D-UNC (set guard scope check)', () {
      // A coin without is_set=true and not denomination 'set' must not use the D blank-mint guard.
      // This coin would have an implicit P mint (Philadelphia pre-1980 style).
      expect(SlotResolver.matchesVariety(coinBlankMintNotASet, vDUnc), isFalse);
    });

    test('Non-set coin with blank mint still ticks P-UNC (P blank-mint guard unaffected)', () {
      expect(SlotResolver.matchesVariety(coinBlankMintNotASet, vPUnc), isTrue);
    });

  });

  // ── Full 15-coin / 19-slot regression suite (v2.1 §10.1, §10.2, §10.5) ─────

  ChecklistVariety cv(String id) => ChecklistVariety(id: id, label: id);

  final fullCollectibles19Program = CoinProgram(
    id: '2026_semiquincentennial_collectibles',
    url: '',
    name: '2026 America250 - Numismatic Collectibles',
    years: '2026',
    category: 'America250',
    mintMarkLocations: 'Obverse or edge',
    coins: [
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_morgan_silver_dollar_reverse_proof_2026',
        name: '2026 Morgan Silver Dollar Reverse Proof',
        year: '2026',
        productFamily: 'morgan',
        varieties: [cv('P-REVERSE-PROOF')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_peace_silver_dollar_reverse_proof_2026',
        name: '2026 Peace Silver Dollar Reverse Proof',
        year: '2026',
        productFamily: 'peace',
        varieties: [cv('P-REVERSE-PROOF')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_morgan_silver_dollar_enhanced_uncirculated_2026',
        name: '2026 Morgan Silver Dollar Enhanced Uncirculated',
        year: '2026',
        productFamily: 'morgan',
        varieties: [cv('EU')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_peace_silver_dollar_enhanced_uncirculated_2026',
        name: '2026 Peace Silver Dollar Enhanced Uncirculated',
        year: '2026',
        productFamily: 'peace',
        varieties: [cv('EU')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_american_eagle_one_ounce_silver_proof_coin_2026',
        name: '2026 American Eagle One Ounce Silver Proof Coin',
        year: '2026',
        productFamily: 'ase',
        varieties: [cv('W-PROOF')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_american_eagle_one_ounce_silver_enhanced_uncirculated_coin_2026',
        name: '2026 American Eagle One Ounce Silver Enhanced Uncirculated Coin',
        year: '2026',
        productFamily: 'ase',
        varieties: [cv('W-EU')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_american_eagle_one_ounce_silver_proof_coin_congratulations_set_2026',
        name: '2026 American Eagle One Ounce Silver Proof Coin (Congratulations Set)',
        year: '2026',
        productFamily: 'ase',
        varieties: [cv('P-PROOF-CONG')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_american_eagle_one_ounce_gold_proof_coin_2026',
        name: '2026 American Eagle One Ounce Gold Proof Coin',
        year: '2026',
        productFamily: 'age',
        varieties: [cv('W-PROOF')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_american_eagle_one_ounce_gold_enhanced_uncirculated_coin_2026',
        name: '2026 American Eagle One Ounce Gold Enhanced Uncirculated Coin',
        year: '2026',
        productFamily: 'age',
        varieties: [cv('W-EU')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_american_buffalo_one_ounce_gold_proof_coin_2026',
        name: '2026 American Buffalo One Ounce Gold Proof Coin',
        year: '2026',
        productFamily: 'buffalo',
        varieties: [cv('W-PROOF')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_american_innovation_1_iowa_2026',
        name: r'2026 American Innovation $1 — Iowa',
        year: '2026',
        productFamily: 'innovation:iowa',
        varieties: [cv('P'), cv('D')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_american_innovation_1_wisconsin_2026',
        name: r'2026 American Innovation $1 — Wisconsin',
        year: '2026',
        productFamily: 'innovation:wisconsin',
        varieties: [cv('P'), cv('D')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_american_innovation_1_california_2026',
        name: r'2026 American Innovation $1 — California',
        year: '2026',
        productFamily: 'innovation:california',
        varieties: [cv('P'), cv('D')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_american_innovation_1_minnesota_2026',
        name: r'2026 American Innovation $1 — Minnesota',
        year: '2026',
        productFamily: 'innovation:minnesota',
        varieties: [cv('P'), cv('D')],
      ),
      ProgramCoin(
        id: '2026_semiquincentennial_collectibles_2026_semiquincentennial_president_donald_j_trump_1_coin_2026',
        name: r'2026 Semiquincentennial President Donald J. Trump $1 Coin',
        year: '2026',
        productFamily: 'trump',
        varieties: [cv('P')],
      ),
    ],
  );

  final fullCurrency39Program = CoinProgram(
    id: '2026_semiquincentennial_currency',
    url: '',
    name: '2026 America250 - Circulating Currency',
    years: '2026',
    category: 'America250',
    mintMarkLocations: 'Obverse',
    coins: [
      ProgramCoin(id: '2026_cent', name: '1776 ~ 2026 Collectible Cent', year: '2026', varieties: [cv('P-UNC'), cv('D-UNC'), cv('S-PROOF')]),
      ProgramCoin(id: '2026_nickel', name: '1776 ~ 2026 Jefferson Nickel', year: '2026', varieties: [cv('P-UNC'), cv('D-UNC'), cv('S-PROOF')]),
      ProgramCoin(id: '2026_dime', name: 'Emerging Liberty Dime', year: '2026', varieties: [cv('P-UNC'), cv('D-UNC'), cv('S-PROOF'), cv('S-SILVER')]),
      ProgramCoin(id: '2026_quarter_mayflower', name: 'America250 Quarter #1: Mayflower Compact', year: '2026', varieties: [cv('P-UNC'), cv('D-UNC'), cv('S-PROOF'), cv('S-SILVER')]),
      ProgramCoin(id: '2026_quarter_valleyforge', name: 'America250 Quarter #2: Revolutionary War', year: '2026', varieties: [cv('P-UNC'), cv('D-UNC'), cv('S-PROOF'), cv('S-SILVER')]),
      ProgramCoin(id: '2026_quarter_declaration', name: 'America250 Quarter #3: Declaration of Independence', year: '2026', varieties: [cv('P-UNC'), cv('D-UNC'), cv('S-PROOF'), cv('S-SILVER'), cv('P-PRIVY-JULY4'), cv('D-PRIVY-JULY4')]),
      ProgramCoin(id: '2026_quarter_constitution', name: 'America250 Quarter #4: U.S. Constitution', year: '2026', varieties: [cv('P-UNC'), cv('D-UNC'), cv('S-PROOF'), cv('S-SILVER')]),
      ProgramCoin(id: '2026_quarter_gettysburg', name: 'America250 Quarter #5: Gettysburg Address', year: '2026', varieties: [cv('P-UNC'), cv('D-UNC'), cv('S-PROOF'), cv('S-SILVER')]),
      ProgramCoin(id: '2026_half_dollar', name: 'Enduring Liberty Half Dollar', year: '2026', varieties: [cv('P-UNC'), cv('D-UNC'), cv('S-PROOF'), cv('S-SILVER')]),
      ProgramCoin(id: '2026_native_american_dollar', name: r'Native American \ Coin - Polly Cooper (Oneida Allies at Valley Forge)', year: '2026', varieties: [cv('P-UNC'), cv('D-UNC'), cv('S-PROOF')]),
    ],
  );

  // Verbatim payloads from eric.seaman@yahoo.com Firestore docs
  final eric26XL = <String, dynamic>{
    'id': 'a59853c1-b72b-414d-8b8e-de6813c29996',
    'Program/Series': 'Peace Dollar',
    'Theme/Subject': 'America250',
    'Year': '2026',
    'Mint Mark': 'P',
    'mint_mark': 'P',
    'mint': 'Philadelphia',
    'Condition': 'Reverse Proof',
    'Variety': 'Reverse Proof',
    'Denomination': 'Dollar',
    'Country': 'United States',
  };

  final eric26XE = <String, dynamic>{
    'id': 'be10e44ce5b4ff4b46c92426cc7f59a254ed675c',
    'Program/Series': 'Morgan Dollar',
    'Theme/Subject': 'Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026)',
    'Year': '2026',
    'mint': 'West Point',
    'Strike Type': 'Enhanced Uncirculated',
    'Condition': 'Enhanced Uncirculated',
    'Variety': 'Liberty Bell 250 Privy, 1776~2026 Dual Date',
    'Denomination': 'Dollar',
    'Country': 'United States',
    'Quantity': 2,
  };

  final eric26EaRaw = <String, dynamic>{
    'id': 'e91efa62-4e8d-4920-a928-c0c97659bcdc',
    'Program/Series': 'American Silver Eagle',
    'Theme/Subject': 'America250',
    'Year': '2026',
    'Mint Mark': 'W',
    'mint_mark': 'W',
    'mint': 'West Point',
    'Condition': 'Proof',
    'Strike Type': '',
    'Variety': '250 Privy / W-Reverse PROOF',
    'Denomination': 'Dollar',
    'Country': 'United States',
  };

  final eric26EaFixed = <String, dynamic>{
    ...eric26EaRaw,
    'Strike Type': 'Proof',
    'Variety': '250 Privy / W-Proof',
  };

  final eric26SqrpRaw = <String, dynamic>{
    'id': '7a32932ebc4e94a586534e7180cd1c4372c4f17d',
    'Program/Series': 'Semiquincentennial President',
    'Theme/Subject': 'Donald J. Trump Semiquincentennial 250th Anniversary Roll (July 4th Privy eligible)',
    'Year': '2026',
    'Mint Mark': 'D',
    'mint_mark': 'D',
    'mint': 'Denver',
    'Strike Type': 'Circulating',
    'Condition': 'Uncirculated',
    'Denomination': 'Dollar',
    'Country': 'United States',
    'Quantity': 25,
  };

  final eric26SqrpFixed = <String, dynamic>{
    ...eric26SqrpRaw,
    'Mint Mark': '',
    'mint_mark': '',
    'mint': 'Philadelphia',
  };

  // Deferred & excluded 2026 items from eric.seaman@yahoo.com
  final eric26GcPending = <String, dynamic>{
    'id': '0e68ecba760df66bf824ec1ba2c86b32318d002d',
    'Program/Series': 'American Innovation',
    'Year': '2026',
    'Denomination': 'Dollar',
    'Condition': 'Unspecified / Raw',
    'Country': 'United States',
  };

  final ericMayflowerQuarter = <String, dynamic>{
    'id': '0172d0ee64284a12a8aa269ce805ec07',
    'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
    'Theme/Subject': 'Mayflower Compact & Pilgrim Couple',
    'Year': '2026',
    'Mint Mark': 'P',
    'mint_mark': 'P',
    'mint': 'Philadelphia',
    'Denomination': 'Quarter Dollar',
    'Condition': 'UNC',
    'Country': 'United States',
  };

  final ericEnduringHalf = <String, dynamic>{
    'id': '8f2197d5d03a428db24486b4ee375a5e',
    'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
    'Theme/Subject': '250th Anniversary of American Independence',
    'Year': '2026',
    'Mint Mark': 'D',
    'mint_mark': 'D',
    'mint': 'Denver',
    'Denomination': 'Half Dollar',
    'Condition': 'MS-66',
    'Country': 'United States',
  };

  final eric26RJ_1 = <String, dynamic>{
    ...annualSet2026,
    'id': '71e2d4ae92bc4312a4198a3a0cc21fcb',
  };

  final eric26RJ_2 = <String, dynamic>{
    'id': '91f8821265bfe8a33fbd97e21f102c67fdf849fd',
    'Program/Series': 'Uncirculated Coin Set',
    'Year': '2026',
    'Denomination': 'Set',
    'Condition': 'Uncirculated',
    'Country': 'United States',
  };

  final ericRooseveltP = <String, dynamic>{
    'id': 'nAnGLwGvhfIOibf6kIft',
    'Program/Series': 'Roosevelt Dimes',
    'Theme/Subject': 'Franklin D. Roosevelt',
    'Year': '2026',
    'Mint Mark': 'P',
    'mint_mark': 'P',
    'Denomination': 'Dime',
    'Condition': 'UNC',
    'Country': 'United States',
  };

  final ericRooseveltD = <String, dynamic>{
    'id': 'rv9SCUTahBuqJkkiJyga',
    'Program/Series': 'Roosevelt Dimes',
    'Theme/Subject': 'Franklin D. Roosevelt',
    'Year': '2026',
    'Mint Mark': 'D',
    'mint_mark': 'D',
    'Denomination': 'Dime',
    'Condition': 'UNC',
    'Country': 'United States',
  };

  List<String> ownedKeys(CoinProgram prog, List<Map<String, dynamic>> coins) {
    final inv = SlotResolver.resolveProgramInventory(program: prog, coins: coins);
    return inv.entries.where((e) => e.value.isOwned).map((e) => e.key).toList()..sort();
  }

  group('Full 19-slot Collectibles integration & regression (v2.1 §10)', () {
    test('Full 15-coin program triggers _isProgramMultiDesign (19 total slots)', () {
      expect(fullCollectibles19Program.coins.length, equals(15));
      final inv = SlotResolver.resolveProgramInventory(
        program: fullCollectibles19Program,
        coins: const [],
      );
      expect(inv.length, equals(19));
    });

    test('Eric 4 remediated coins + 7 excluded/deferred yield exactly 4 / 19 on legacy path', () {
      final owned = ownedKeys(fullCollectibles19Program, [
        eric26XL,
        eric26XE,
        eric26EaFixed,
        eric26SqrpFixed,
        eric26GcPending,
        ericMayflowerQuarter,
        ericEnduringHalf,
        eric26RJ_1,
        eric26RJ_2,
        ericRooseveltP,
        ericRooseveltD,
      ]);
      expect(owned, equals([
        '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_american_eagle_one_ounce_silver_proof_coin_2026_W-PROOF',
        '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_morgan_silver_dollar_enhanced_uncirculated_2026_EU',
        '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_peace_silver_dollar_reverse_proof_2026_P-REVERSE-PROOF',
        '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_semiquincentennial_president_donald_j_trump_1_coin_2026_P',
      ]));
    });

    test('Code-only intermediate state: Eric raw un-remediated payloads yield 2 / 19 (26XL + 26XE)', () {
      final owned = ownedKeys(fullCollectibles19Program, [
        eric26XL,
        eric26XE,
        eric26EaRaw,
        eric26SqrpRaw,
      ]);
      expect(owned, equals([
        '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_morgan_silver_dollar_enhanced_uncirculated_2026_EU',
        '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_peace_silver_dollar_reverse_proof_2026_P-REVERSE-PROOF',
      ]));
    });

    test('program_id fast path matches all 4 Eric coins + grokbot Gold Eagle EU shape', () {
      final pidCoins = [
        {...eric26XL, 'program_id': '2026_semiquincentennial_collectibles'},
        {...eric26XE, 'program_id': '2026_semiquincentennial_collectibles'},
        {...eric26EaFixed, 'program_id': '2026_semiquincentennial_collectibles'},
        {...eric26SqrpFixed, 'program_id': '2026_semiquincentennial_collectibles'},
        {
          'id': 'b71de3f2-2809-4186-a718-f3f723218f57',
          'program_id': '2026_semiquincentennial_collectibles',
          'Program/Series': '2026 America250 - Numismatic Collectibles',
          'Theme/Subject': '2026 American Eagle One Ounce Gold Enhanced Uncirculated Coin',
          'Year': '2026',
          'Mint Mark': 'W',
          'mint': 'West Point',
          'Strike Type': 'Enhanced Uncirculated',
          'Variety': 'Enhanced Uncirculated',
          'Denomination': 'Dollar',
          'Country': 'United States',
        },
      ];
      final owned = ownedKeys(fullCollectibles19Program, pidCoins);
      expect(owned.length, equals(5));
      expect(
        owned.contains(
          '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_american_eagle_one_ounce_gold_enhanced_uncirculated_coin_2026_W-EU',
        ),
        isTrue,
      );
    });

    test('Per-state Innovation payloads (8 positives) each tick exactly 1 / 19 slot', () {
      final stateCases = <List<String>>[
        ['Iowa', 'iowa', 'P'],
        ['Iowa', 'iowa', 'D'],
        ['Wisconsin', 'wisconsin', 'P'],
        ['Wisconsin', 'wisconsin', 'D'],
        ['California', 'california', 'P'],
        ['California', 'california', 'D'],
        ['Minnesota', 'minnesota', 'P'],
        ['Minnesota', 'minnesota', 'D'],
      ];
      for (final sc in stateCases) {
        final stateLabel = sc[0];
        final stateKey = sc[1];
        final mint = sc[2];
        final coin = <String, dynamic>{
          'Program/Series': 'American Innovation',
          'Theme/Subject': stateLabel,
          'Year': '2026',
          'Mint Mark': mint,
          'Denomination': 'Dollar',
          'Country': 'United States',
        };
        final owned = ownedKeys(fullCollectibles19Program, [coin]);
        expect(
          owned,
          equals([
            '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_american_innovation_1_${stateKey}_2026_$mint',
          ]),
          reason: 'Expected $stateLabel $mint to match only its own slot',
        );
      }

      // Blank-theme Innovation and S-mint Reverse Proof 26GC must yield 0 / 19
      expect(ownedKeys(fullCollectibles19Program, [eric26GcPending]), isEmpty);
      expect(
        ownedKeys(fullCollectibles19Program, [
          {
            'Program/Series': r'American Innovation $1',
            'Theme/Subject': 'Iowa',
            'Year': '2026',
            'Mint Mark': 'S',
            'Strike Type': 'Reverse Proof',
            'Condition': 'Reverse Proof',
            'Denomination': 'Dollar',
            'Country': 'United States',
          },
        ]),
        isEmpty,
      );
    });

    test('Morgan and Peace Silver Dollars combined series & Gold Eagle / Buffalo / Congrats', () {
      final morganPeacePeaceRP = <String, dynamic>{
        'Program/Series': 'Morgan and Peace Silver Dollars',
        'Theme/Subject': 'Peace Dollar Reverse Proof',
        'Year': '2026',
        'Mint Mark': '',
        'mint': 'Philadelphia',
        'Strike Type': 'Reverse Proof',
        'Denomination': 'Dollar',
        'Country': 'United States',
      };
      expect(
        ownedKeys(fullCollectibles19Program, [morganPeacePeaceRP]),
        equals([
          '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_peace_silver_dollar_reverse_proof_2026_P-REVERSE-PROOF',
        ]),
      );

      final morganPeaceMorganEU = <String, dynamic>{
        'Program/Series': 'Morgan and Peace Silver Dollars',
        'Theme/Subject': 'Morgan Dollar Enhanced Uncirculated',
        'Year': '2026',
        'Mint Mark': '',
        'mint': 'West Point',
        'Strike Type': 'Enhanced Uncirculated',
        'Denomination': 'Dollar',
        'Country': 'United States',
      };
      expect(
        ownedKeys(fullCollectibles19Program, [morganPeaceMorganEU]),
        equals([
          '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_morgan_silver_dollar_enhanced_uncirculated_2026_EU',
        ]),
      );

      // Ambiguous combined series+theme referencing both Morgan & Peace (Hmq76a3zTbPlMMTZwHr2) -> 0 / 19
      final ambiguousMorganPeace = <String, dynamic>{
        'Program/Series': 'Morgan and Peace Silver Dollars',
        'Theme/Subject': '2026 Morgan and Peace Silver Dollars Dollar',
        'Year': '2026',
        'Mint Mark': '',
        'Strike Type': 'Reverse Proof',
        'Denomination': 'Dollar',
        'Country': 'United States',
      };
      expect(ownedKeys(fullCollectibles19Program, [ambiguousMorganPeace]), isEmpty);

      // Gold Eagle Proof (26EB), Gold Eagle EU (26EH), Buffalo Proof (26EL), ASE Congrats (26RF)
      final coin26EB = <String, dynamic>{
        'Program/Series': 'American Gold Eagle',
        'Theme/Subject': 'America250',
        'Year': '2026',
        'Mint Mark': 'W',
        'Strike Type': 'Proof',
        'Denomination': 'Dollar',
        'Country': 'United States',
      };
      final coin26EH = <String, dynamic>{
        'Program/Series': 'American Gold Eagle',
        'Theme/Subject': 'America250',
        'Year': '2026',
        'Mint Mark': 'W',
        'Strike Type': 'Enhanced Uncirculated',
        'Denomination': 'Dollar',
        'Country': 'United States',
      };
      final coin26EL = <String, dynamic>{
        'Program/Series': 'American Buffalo',
        'Theme/Subject': 'America250',
        'Year': '2026',
        'Mint Mark': 'W',
        'Strike Type': 'Proof',
        'Denomination': 'Dollar',
        'Country': 'United States',
      };
      final coin26RF = <String, dynamic>{
        'Program/Series': 'American Silver Eagle',
        'Theme/Subject': 'Congratulations Set',
        'Year': '2026',
        'Mint Mark': '',
        'mint': 'Philadelphia',
        'Strike Type': 'Proof',
        'Variety': 'Congratulations Set',
        'Denomination': 'Dollar',
        'Country': 'United States',
      };
      expect(
        ownedKeys(fullCollectibles19Program, [coin26EB, coin26EH, coin26EL, coin26RF]),
        equals([
          '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_american_buffalo_one_ounce_gold_proof_coin_2026_W-PROOF',
          '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_american_eagle_one_ounce_gold_enhanced_uncirculated_coin_2026_W-EU',
          '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_american_eagle_one_ounce_gold_proof_coin_2026_W-PROOF',
          '2026_semiquincentennial_collectibles_2026_semiquincentennial_collectibles_2026_american_eagle_one_ounce_silver_proof_coin_congratulations_set_2026_P-PROOF-CONG',
        ]),
      );
    });

    test('All 6 excluded 2026 coins yield 0 / 19 in Collectibles', () {
      final owned = ownedKeys(fullCollectibles19Program, [
        ericMayflowerQuarter,
        ericEnduringHalf,
        eric26RJ_1,
        eric26RJ_2,
        ericRooseveltP,
        ericRooseveltD,
      ]);
      expect(owned, isEmpty);
    });

    test('Sibling Circulating Currency baseline remains pinned at 20 / 39 (v2.1 §10.5 R3)', () {
      final allEric2026Coins = [
        eric26XL,
        eric26XE,
        eric26EaFixed,
        eric26SqrpFixed,
        eric26GcPending,
        ericMayflowerQuarter,
        ericEnduringHalf,
        eric26RJ_1,
        eric26RJ_2,
        ericRooseveltP,
        ericRooseveltD,
      ];
      final inv = SlotResolver.resolveProgramInventory(
        program: fullCurrency39Program,
        coins: allEric2026Coins,
      );
      expect(inv.length, equals(39));
      expect(inv.values.where((r) => r.isOwned).length, equals(20));
    });
  });
}
