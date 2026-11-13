import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/models/program_model.dart';
import 'package:numista_ai/utils/mint_helpers.dart';
import 'package:numista_ai/utils/slot_resolver.dart';

void main() {
  group('MintHelpers Canonical Fixtures (F01-F15)', () {
    test('F01-F14 deterministic resolution and display formatting', () {
      final f01 = MintHelpers.resolveTwoFieldMint(
        year: '1921',
        rawMintMark: '',
        series: 'Morgan Dollars',
        denomination: 'Dollar',
      );
      expect(f01.mint, 'Philadelphia');
      expect(f01.mintMark, '');
      expect(f01.ruleId, 10);
      expect(MintHelpers.formatMintMarkForDisplay(f01.mint, f01.mintMark, compact: true), 'NMM');
      expect(MintHelpers.formatMintMarkForDisplay(f01.mint, f01.mintMark, compact: false), 'No Mint Mark');

      final f02 = MintHelpers.resolveTwoFieldMint(
        year: '1921',
        rawMintMark: 'D',
        series: 'Morgan Dollars',
        denomination: 'Dollar',
      );
      expect((f02.mint, f02.mintMark, f02.ruleId), ('Denver', 'D', 3));

      final f04 = MintHelpers.resolveTwoFieldMint(
        year: '1943',
        rawMintMark: '',
        series: 'Jefferson Nickels',
        denomination: '5 Cents',
        variety: 'War Nickel',
        metalContent: '35% Silver',
      );
      expect((f04.mint, f04.mintMark, f04.ruleId), ('', '', 11));

      final f05 = MintHelpers.resolveTwoFieldMint(
        year: '1942',
        rawMintMark: '',
        series: 'Jefferson Nickels',
        denomination: '5 Cents',
        variety: 'Type 1',
        metalContent: 'Copper-Nickel',
      );
      expect((f05.mint, f05.mintMark, f05.ruleId), ('Philadelphia', '', 10));

      final f09 = MintHelpers.resolveTwoFieldMint(
        year: '1849',
        rawMintMark: 'D',
        series: 'Liberty Head Gold',
        denomination: '\$5 Half Eagle',
      );
      expect((f09.mint, f09.mintMark, f09.ruleId), ('Dahlonega', 'D', 2));

      final f10 = MintHelpers.resolveTwoFieldMint(
        year: '1849',
        rawMintMark: 'C',
        series: 'Liberty Head Gold',
        denomination: '\$5 Half Eagle',
      );
      expect((f10.mint, f10.mintMark, f10.ruleId), ('Charlotte', 'C', 4));

      final f11 = MintHelpers.resolveTwoFieldMint(
        year: '2026',
        rawMintMark: '',
        series: 'Morgan Dollars',
        denomination: 'Dollar',
        strikeType: 'Enhanced Uncirculated',
        variety: 'Enhanced Uncirculated',
        retailerItemNo: '26XE',
      );
      expect((f11.mint, f11.mintMark, f11.ruleId), ('West Point', '', 9));
      expect(MintHelpers.formatMintMarkForDisplay(f11.mint, f11.mintMark, compact: true), '');

      final f12 = MintHelpers.resolveTwoFieldMint(
        year: '2026',
        rawMintMark: '',
        series: 'Morgan Dollars',
        denomination: 'Dollar',
        strikeType: 'Reverse Proof',
        variety: 'Reverse Proof',
        retailerItemNo: '26XF',
      );
      expect((f12.mint, f12.mintMark, f12.ruleId), ('Philadelphia', '', 10));
      expect(MintHelpers.formatMintMarkForDisplay(f12.mint, f12.mintMark, compact: true), 'NMM');

      final f13 = MintHelpers.resolveTwoFieldMint(
        year: '1964',
        rawMintMark: 'None',
        series: 'Roosevelt Dimes',
        denomination: 'Dime',
      );
      expect((f13.mint, f13.mintMark, f13.ruleId), ('Philadelphia', '', 10));

      final f14 = MintHelpers.resolveTwoFieldMint(
        year: '2015',
        rawMintMark: '',
        series: 'Canadian Maple Leaf',
        denomination: '\$5 CAD',
        country: 'Canada',
      );
      expect((f14.mint, f14.mintMark, f14.ruleId), ('', '', 11));
    });

    test('F15 unmigrated legacy doc reads Mint Mark D via dual-key fallback', () {
      final legacyDoc = <String, dynamic>{
        'Year': '1921',
        'Mint Mark': 'D',
        'Denomination': 'Dollar',
        'Program/Series': 'Morgan Dollars',
      };
      expect(MintHelpers.readMintFacility(legacyDoc), '');
      expect(MintHelpers.readMintMark(legacyDoc), 'D');

      final coin = CoinModel.fromMap(legacyDoc, 'doc_f15');
      expect(coin.mint, '');
      expect(coin.mintMark, 'D');
    });

    test('SlotResolver isolates West Point NMM (EU) from Philadelphia NMM (P-UNC / P-REVERSE-PROOF)', () {
      final wpEuDoc = <String, dynamic>{
        'Year': '2026',
        'mint': 'West Point',
        'mint_mark': '',
        'Strike Type': 'Enhanced Uncirculated',
        'Variety': 'Enhanced Uncirculated',
      };
      final phillyRpDoc = <String, dynamic>{
        'Year': '2026',
        'mint': 'Philadelphia',
        'mint_mark': '',
        'Strike Type': 'Reverse Proof',
        'Variety': 'Reverse Proof',
      };
      final euVariety = ChecklistVariety(id: 'EU', label: 'Enhanced Uncirculated');
      final pRpVariety = ChecklistVariety(id: 'P-REVERSE-PROOF', label: 'Reverse Proof');

      expect(SlotResolver.matchesVariety(wpEuDoc, euVariety), isTrue);
      expect(SlotResolver.matchesVariety(wpEuDoc, pRpVariety), isFalse);
      expect(SlotResolver.matchesVariety(phillyRpDoc, pRpVariety), isTrue);
      expect(SlotResolver.matchesVariety(phillyRpDoc, euVariety), isFalse);
    });
  });

  group('F1 parity: Rule 11 preserves existing facility', () {
    test('probe cases', () {
      final a = MintHelpers.resolveTwoFieldMint(rawMint: 'Royal Canadian Mint', country: 'Canada', year: '2020');
      expect((a.mint, a.mintMark, a.ruleId), ('Royal Canadian Mint', '', 11));
      final b = MintHelpers.resolveTwoFieldMint(rawMintMark: 'D', rawMint: 'Denver', year: '1900');
      expect((b.mint, b.mintMark, b.ruleId), ('Denver', 'D', 11));
      final c = MintHelpers.resolveTwoFieldMint(rawMintMark: 'DENVER', year: '1990');
      expect((c.mint, c.mintMark, c.ruleId), ('Denver', '', 11));
    });
  });}
