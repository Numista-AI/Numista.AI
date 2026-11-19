// SILVER-EAGLE-MELT regression tests. The metal is decided by composition, never by the word 'eagle'.
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/melt_value_service.dart';

const spot = {'Gold': 4000.0, 'Silver': 50.0, 'Platinum': 1600.0, 'Palladium': 1000.0};

double? melt(String mc, String denom, {String series = '', String theme = '', Map<String, dynamic>? data, Map<String, double> prices = spot}) =>
    MeltValueService.compute(metalContent: mc, denomination: denom, spotPrices: prices, programSeries: series, themeSubject: theme, coinData: data);

void main() {
  group('American Silver Eagle uses silver, 1 oz', () {
    test('denomination "American Silver Eagle Dollar", .999 Fine Silver', () {
      expect(melt('.999 Fine Silver', 'American Silver Eagle Dollar'), closeTo(50.0, 1e-9));
    });
    test('denomination "\$1 Silver Eagle", composition "Silver"', () {
      expect(melt('Silver', r'$1 Silver Eagle'), closeTo(50.0, 1e-9));
    });
    test('header path: denomination "Dollar", series "American Eagle"', () {
      expect(melt('1 oz .999 Fine Silver', 'Dollar', series: 'American Eagle'), closeTo(50.0, 1e-9));
    });
    test('composition "Silver", series "American Eagle Silver Dollar"', () {
      expect(melt('Silver', 'Dollar', series: 'American Eagle Silver Dollar'), closeTo(50.0, 1e-9));
    });
    test('no composition, denomination "American Silver Eagle"', () {
      expect(melt('', 'American Silver Eagle'), closeTo(50.0, 1e-9));
    });
    test('gold-plated (gilded) Silver Eagle stays silver', () {
      expect(melt('.999 Fine Silver, gold-plated', 'American Silver Eagle'), closeTo(50.0, 1e-9));
    });
    test('never the gold price (old bug: 0.24188 x gold = 967.52)', () {
      expect(melt('.999 Fine Silver', 'American Silver Eagle Dollar'), isNot(closeTo(967.52, 0.01)));
    });
  });

  group('American Gold Eagle, all sizes (0.10 / 0.25 / 0.50 / 1.00 oz)', () {
    for (final c in [[r'$5', 400.0], [r'$10', 1000.0], [r'$25', 2000.0], [r'$50', 4000.0]]) {
      test('91.67% Gold ${c[0]}', () {
        expect(melt('91.67% Gold', c[0] as String, series: 'American Gold Eagle'), closeTo(c[1] as double, 1e-9));
      });
    }
    test('composition "Gold", denomination "Gold Eagle", \$25', () {
      expect(melt('Gold', r'$25 Gold Eagle'), closeTo(2000.0, 1e-9));
    });
    test('no composition, series "American Eagle Gold Coin", \$5', () {
      expect(melt('', r'$5', series: 'American Eagle Gold Coin'), closeTo(400.0, 1e-9));
    });
  });

  group('American Platinum Eagle uses platinum', () {
    for (final c in [[r'$100', 1600.0], [r'$50', 800.0], [r'$25', 400.0], [r'$10', 160.0]]) {
      test('99.95% Platinum ${c[0]}', () {
        expect(melt('99.95% Platinum', c[0] as String, series: 'American Platinum Eagle'), closeTo(c[1] as double, 1e-9));
      });
    }
    test('no composition, series "American Platinum Eagle", \$100', () {
      expect(melt('', r'$100', series: 'American Platinum Eagle'), closeTo(1600.0, 1e-9));
    });
    test('platinum spot missing -> null (never gold)', () {
      expect(melt('Platinum', r'$100', prices: const {'Gold': 4000.0, 'Silver': 50.0}), isNull);
    });
    test('unknown platinum size -> null', () {
      expect(melt('Platinum', 'Platinum bar'), isNull);
    });
  });

  group('Classic \$10 Eagle (gold, 1795-1933): 0.48375 oz', () {
    test('90% Gold, 10% Copper, \$10, Indian Head Gold Eagle', () {
      expect(melt('90% Gold, 10% Copper', r'$10', series: 'Indian Head Gold Eagle'), closeTo(1935.0, 1e-9));
    });
    test('composition "Gold", denomination "Eagle"', () {
      expect(melt('Gold', 'Eagle'), closeTo(1935.0, 1e-9));
    });
    test('no composition, "\$10 Eagle", Year 1907 -> gold', () {
      expect(melt('', r'$10 Eagle', data: {'Year': '1907'}), closeTo(1935.0, 1e-9));
    });
    test('composition "Gold", series "Indian Head Gold Eagle", \$10 -> classic, not American Gold Eagle', () {
      expect(melt('Gold', r'$10', series: 'Indian Head Gold Eagle'), closeTo(1935.0, 1e-9));
    });
    test('Double Eagle with composition "Gold" -> 0.9675 oz', () {
      expect(melt('Gold', 'Double Eagle'), closeTo(3870.0, 1e-9));
    });
    // Boundary and variety tests per Gemini non-blocking review notes
    test('no composition, "\$10 Eagle", Year 1795 (lower bound) -> gold', () {
      expect(melt('', r'$10 Eagle', data: {'Year': '1795'}), closeTo(1935.0, 1e-9));
    });
    test('no composition, "\$10 Eagle", Year 1933 (upper bound) -> gold', () {
      expect(melt('', r'$10 Eagle', data: {'Year': '1933'}), closeTo(1935.0, 1e-9));
    });
    test('no composition, "\$10 Eagle", Year 1794 (below bound) -> null', () {
      expect(melt('', r'$10 Eagle', data: {'Year': '1794'}), isNull);
    });
    test('no composition, "\$10 Eagle", Year 1934 (above bound) -> null', () {
      expect(melt('', r'$10 Eagle', data: {'Year': '1934'}), isNull);
    });
    test('no composition, "\$10 Eagle", Year "1907-D" with mint mark -> gold', () {
      expect(melt('', r'$10 Eagle', data: {'Year': '1907-D'}), closeTo(1935.0, 1e-9));
    });
    test('no composition, "\$10 Eagle", Year "1795 (Small Eagle)" with note -> gold', () {
      expect(melt('', r'$10 Eagle', data: {'Year': '1795 (Small Eagle)'}), closeTo(1935.0, 1e-9));
    });
  });

  group('Missing composition: never a gold guess', () {
    test('"\$10 Eagle", no year -> null', () {
      expect(melt('', r'$10 Eagle'), isNull);
    });
    test('"\$10 Eagle", Year 1986 (modern) -> null', () {
      expect(melt('', r'$10 Eagle', data: {'Year': 1986}), isNull);
    });
    test('"Pending" composition, series "American Eagle" -> null', () {
      expect(melt('Pending', 'Dollar', series: 'American Eagle'), isNull);
    });
    test('format shows N/A', () {
      expect(MeltValueService.format(metalContent: '', denomination: 'Eagle', spotPrices: spot), 'N/A');
    });
    test('names two metals ("Gold and Silver Set") -> null', () {
      expect(melt('', 'Set', series: 'Gold and Silver Set'), isNull);
    });
    test('metalOf: bare eagle with no data -> null', () {
      expect(MeltValueService.metalOf(metalContent: '', denomination: 'Eagle'), isNull);
    });
  });

  group('Base-metal coins with eagle/gold words are not precious', () {
    test('Flying Eagle cent, Cupro-Nickel -> null', () {
      expect(melt('Cupro-Nickel', 'Flying Eagle cent', series: 'Flying Eagle Cent'), isNull);
    });
    test('Washington quarter (eagle reverse), clad -> null', () {
      expect(melt('Copper-Nickel Clad Copper', 'Quarter', theme: 'Eagle reverse'), isNull);
    });
    test('Sacagawea "Golden Dollar", no composition -> null', () {
      expect(melt('', 'Dollar', series: 'Sacagawea Golden Dollar'), isNull);
    });
  });

  group('Unchanged behaviour', () {
    test('Morgan 90% silver dollar', () {
      expect(melt('90% Silver', 'Dollar', series: 'Morgan Silver Dollar'), closeTo(50.0 * 0.77344, 1e-9));
    });
    test('Liberty Head Half Eagle 90% gold \$5', () {
      expect(melt('90% Gold, 10% Copper', r'$5', series: 'Liberty Head Gold Half Eagle'), closeTo(4000.0 * 0.24188, 1e-9));
    });
    test('Gold Buffalo 99.99%', () {
      expect(melt('99.99% Gold', r'$50', series: 'American Buffalo'), closeTo(4000.0, 1e-9));
    });
    test('backend numeric field wins (is_gold, 0.25 oz)', () {
      expect(melt('', r'$10', data: {'troy_oz_pure_metal': 0.25, 'is_gold': true}), closeTo(1000.0, 1e-9));
    });
    test('40% silver half', () {
      expect(melt('40% Silver', 'Half Dollar'), closeTo(50.0 * 0.14792, 1e-9));
    });
    test('no spot prices -> null', () {
      expect(melt('Silver', 'Dollar', prices: const {}), isNull);
    });
  });
}
