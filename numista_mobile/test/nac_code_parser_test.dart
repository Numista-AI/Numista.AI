import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/catalog/catalog_service.dart';
import 'package:numista_ai/services/catalog/nac_code_parser.dart';

void main() {
  group('NAC1 Grammar & Crockford-32 Checksum Gate (Plan.v2.1 §2.2)', () {
    const canonicalVectors = <(String, String)>[
      ('NAC1.CN.CO.1C.FUGIO.1787.XX.BASE', 'K'),
      ('NAC1.CN.US.G5.LIBCAP.1838.DD.BASE', '3'),
      ('NAC1.CN.US.1D.MORGAN.1881.S.BASE', 'E'),
      ('NAC1.CN.US.1D.MORGAN.1921.P.BASE', '4'),
      ('NAC1.CN.US.5C.BUFFALO.1937.D.3LEG', '3'),
      ('NAC1.CN.US.25C.AWQ.2022.P.MAYA', 'Z'),
      ('NAC1.CN.US.1D.ASE.2024.W.PRF', 'S'),
      ('NAC1.BN.US.FRN1.FED.2017A.BEP.BASE', '6'),
      ('NAC1.BN.US.TN1000.TREAS.1890.BEP.WM', 'C'),
      ('NAC1.MD.US.PRES.PRES.1923.P.COOL', 'W'),
      ('NAC1.CN.PF.1P.PHL1P.1903.S.BASE', '3'),
      ('NAC1.CN.FS.1D.SPAN8R.1798.MO.BASE', 'P'),
      ('NAC1.MD.US.PRV.CWT.1863.XX.BASE', 'H'),
      ('NAC1.TK.US.PRV.CWT.1863.XX.BASE', 'T'),
      ('NAC1.CN.CO.1C.CT.1787.XX.DRAPED', 'V'),
      ('NAC1.BN.US.SC5.SILV.1899.BEP.BASE', 'A'),
    ];

    test('computes and validates all 13+ canonical NAC1 vectors 100%', () {
      for (final (payload, expectedChk) in canonicalVectors) {
        final fullCode = '$payload.$expectedChk';
        expect(NacCodeParser.computeNac1Chk(payload), equals(expectedChk));
        expect(NacCodeParser.validateNac1(fullCode), isTrue);
        expect(NacCodeParser.buildNac1(payload), equals(fullCode));
      }
    });

    test('rejects invalid check digits and malformed NAC1 strings', () {
      expect(
        NacCodeParser.validateNac1('NAC1.CN.US.1D.MORGAN.1881.S.BASE.F'),
        isFalse,
      );
      expect(
        NacCodeParser.validateNac1('NAC1.CN.GB.1D.MORGAN.1881.S.BASE.E'),
        isFalse,
      );
      expect(
        NacCodeParser.validateNac1('NAC1.CN.US.1D.MORGAN.1881.S.BASE.U'),
        isFalse,
      );
      expect(
        NacCodeParser.validateNac1('NAC1.CN.US.1D.MORGAN.1881.S.BASE.L'),
        isFalse,
      );
      expect(
        NacCodeParser.validateNac1('NAC1.CN.US.1D.MORGAN.1881.S.BASE.I'),
        isFalse,
      );
      expect(
        NacCodeParser.validateNac1('NAC1.CN.US.1D.MORGAN.1881.S.BASE.O'),
        isFalse,
      );
      expect(NacCodeParser.validateNac1(''), isFalse);
      expect(NacCodeParser.validateNac1(null), isFalse);
    });

    test('kindToCollection routes CN to coins, BN to currency, MD to world_items', () {
      expect(NacCodeParser.kindToCollection('CN'), equals('coins'));
      expect(NacCodeParser.kindToCollection('BN'), equals('currency'));
      expect(NacCodeParser.kindToCollection('MD'), equals('world_items'));
      expect(NacCodeParser.kindToCollection('TK'), equals('world_items'));
      expect(NacCodeParser.kindToCollection('ST'), equals('world_items'));
    });

    test('every seed catalog item has a valid NAC1 checksum', () {
      expect(UsNumismaticsCatalogService.seedItems.length, equals(15));
      for (final item in UsNumismaticsCatalogService.seedItems) {
        expect(
          NacCodeParser.validateNac1(item.nacCode),
          isTrue,
          reason: 'Seed item ${item.nacCode} failed checksum validation',
        );
      }
    });
  });
}
