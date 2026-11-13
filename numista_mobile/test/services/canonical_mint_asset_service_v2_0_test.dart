import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/canonical_mint_asset_service.dart';

void main() {
  group('CanonicalMintAssetService v2.3 Enhancements (MF-C5\', MF-C7)', () {
    test('canonicalYear resolves explicit year fields and dual dates correctly', () {
      expect(CanonicalMintAssetService.canonicalYear({'year': '1958'}), '1958');
      expect(CanonicalMintAssetService.canonicalYear({'Year': '2026.0'}), '2026');
      expect(CanonicalMintAssetService.canonicalYear({'year': '', 'Year': '1964'}), '1964');
      expect(CanonicalMintAssetService.canonicalYear({'Year': '1776-2026'}), '2026');
      expect(CanonicalMintAssetService.canonicalYear({'title': '1921 Morgan Silver Dollar'}), '1921');
    });

    test('canonicalYear strictly ignores Personal Notes', () {
      final withNotes = {
        'title': 'Lincoln Cent',
        'personalNotes': 'Bought in 1999 from dealer',
        'notes': 'Inherited in 1985',
        'Personal Notes': '1999 estate lot',
      };
      expect(CanonicalMintAssetService.canonicalYear(withNotes), '');
    });

    test('MF-C5\': Denomination regex matches "1 cent", "1¢", "cent", "5¢", "5 cents", "five cents" with neutral title', () {
      for (final denom in const ['1 cent', '1¢', '1c', 'cent', 'one cent', 'penny']) {
        final coin = {
          'Year': '2026',
          'mint_mark': 'P',
          'denomination': denom,
          'title': '2026 Coin', // Neutral title so cleanTitle cannot rescue cleanDenom
        };
        final res = CanonicalMintAssetService.resolveFromMap(coin);
        expect(res, isNotNull, reason: 'Denomination "$denom" must resolve 2026 cent SKU');
        expect(res!.sku, '2026-CENT-P');
      }

      for (final denom in const ['5¢', '5c', '5 cents', '5 cent', 'five cents', 'five cent', 'nickel']) {
        final coin = {
          'Year': '2026',
          'mint_mark': 'P',
          'denomination': denom,
          'title': '2026 Coin', // Neutral title so cleanTitle cannot rescue cleanDenom
        };
        final res = CanonicalMintAssetService.resolveFromMap(coin);
        expect(res, isNotNull, reason: 'Denomination "$denom" must resolve 2026 nickel SKU');
        expect(res!.sku, '2026-NICKEL-P');
      }
    });

    test('MF-C5\': Denomination regex constructs without FormatException and rejects tokens reaching the new regex', () {
      // Explicit RegExp constructor check matching §3.C production patterns byte-for-byte
      final centRe = RegExp(
        r'(?<![\d.])(?:1c|1¢|1 cents?|one cent|penny)(?!\w)|(?:^|(?<![\d.])\s+)\bcent\b',
        caseSensitive: false,
      );
      final nickelRe = RegExp(
        r'(?<![\d.])(?:5c|5¢|5 cents?|five cents?|nickel)(?!\w)',
        caseSensitive: false,
      );
      expect(centRe.hasMatch('1 cent'), isTrue);
      expect(centRe.hasMatch('1¢'), isTrue);
      expect(centRe.hasMatch('cent'), isTrue);
      expect(nickelRe.hasMatch('5 cents'), isTrue);
      expect(nickelRe.hasMatch('5¢'), isTrue);
      expect(centRe.hasMatch('15¢'), isFalse);
      expect(centRe.hasMatch('15 cent'), isFalse);
      expect(centRe.hasMatch('2.5 cent'), isFalse);
      expect(nickelRe.hasMatch('15¢'), isFalse);
      expect(nickelRe.hasMatch('25 cents'), isFalse);

      // Note: '25c' and '50c' are caught by earlier isQuarter/isHalf branches; '15¢', '15 cent', '35 cent', '100 cent' reach the new regex.
      for (final nonCentOrNickel in const ['15¢', '15 cent', '35 cent', '100 cent', '25 cent', '25c', '50 cent', '50c']) {
        final coin = {
          'Year': '2026',
          'mint_mark': 'P',
          'denomination': nonCentOrNickel,
          'title': '2026 Coin', // Neutral title
        };
        final res = CanonicalMintAssetService.resolveFromMap(coin);
        expect(
          res?.sku,
          isNot(anyOf('2026-CENT-P', '2026-NICKEL-P')),
          reason: 'Denomination "$nonCentOrNickel" must never match cent or nickel SKU',
        );
      }
    });
  });
}
