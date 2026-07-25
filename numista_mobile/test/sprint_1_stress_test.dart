import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/services/wizard_service.dart';

import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity', () {
    late List<Map<String, dynamic>> rawJsonList;
    late List<CoinModel> parsedCoins;

    setUpAll(() {
      SharedPreferences.setMockInitialValues({});
      final jsonFile = File('assets/guest_demo_coins.json');
      expect(jsonFile.existsSync(), isTrue, reason: 'assets/guest_demo_coins.json must exist');
      final jsonString = jsonFile.readAsStringSync();
      rawJsonList = List<Map<String, dynamic>>.from(jsonDecode(jsonString));
      parsedCoins = rawJsonList.asMap().entries.map((e) => CoinModel.fromMap(e.value, 'demo_${e.key}')).toList();
    });

    test('Dataset contains exactly 100 items', () {
      expect(rawJsonList.length, equals(100));
      expect(parsedCoins.length, equals(100));
    });

    test('Certified-to-Raw ratio meets 60/40 estate credibility requirement', () {
      final certifiedCount = parsedCoins.where((c) {
        return c.gradingService.isNotEmpty || c.holderType.isNotEmpty || c.certificationNumber.isNotEmpty;
      }).length;
      final rawCount = parsedCoins.length - certifiedCount;

      print('📊 Demo Dataset Ratio: $certifiedCount Certified / $rawCount Raw');
      expect(certifiedCount, greaterThanOrEqualTo(55), reason: 'Must have at least 55-60 certified coins for estate showcase');
      expect(rawCount, greaterThanOrEqualTo(35), reason: 'Must have at least 35-40 raw coins');
    });

    test('Multi-View dataset distribution covers Coins, Currency, and World items', () {
      final banknotes = rawJsonList.where((item) {
        final denom = (item['Denomination'] ?? '').toString();
        return item['Is Currency'] == true ||
               item['Category'] == 'Currency' ||
               denom.contains('Bill') ||
               denom.contains('Note');
      }).toList();

      final worldItems = rawJsonList.where((item) {
        final country = (item['Country'] ?? '').toString();
        return item['Category'] == 'World' || (country.isNotEmpty && country != 'USA');
      }).toList();

      final usCoins = rawJsonList.where((item) {
        final country = (item['Country'] ?? '').toString();
        final isCurr = item['Is Currency'] == true || item['Category'] == 'Currency';
        return (country == 'USA' || country.isEmpty) && !isCurr;
      }).toList();

      print('🌐 Multi-View Items: ${usCoins.length} US Coins, ${banknotes.length} Banknotes, ${worldItems.length} World Items');
      expect(banknotes.length, equals(5), reason: 'Must have exactly 5 banknote demo items');
      expect(worldItems.length, equals(5), reason: 'Must have exactly 5 world demo items');
      expect(usCoins.length, equals(90), reason: 'Must have exactly 90 US coin demo items');
    });

    test('Zero missing or null critical fields across all 100 items', () {
      for (int i = 0; i < parsedCoins.length; i++) {
        final c = parsedCoins[i];
        expect(c.year, isNotNull, reason: 'Coin #$i year is null');
        expect(c.denomination, isNotEmpty, reason: 'Coin #$i denomination is empty');
        expect(c.condition, isNotEmpty, reason: 'Coin #$i condition is empty');
      }
    });
  });

  group('Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing', () {
    test('PCGS URL formatting & whitespace trimming', () {
      final c1 = CoinModel(id: '1', gradingService: 'PCGS', certificationNumber: '21849301');
      expect(c1.getVerificationUrl(), equals('https://www.pcgs.com/cert/21849301'));

      final c2 = CoinModel(id: '2', holderType: '  pcgs  ', certificationNumber: ' 21849301 ');
      expect(c2.getVerificationUrl(), equals('https://www.pcgs.com/cert/21849301'));
    });

    test('NGC URL formatting & slash stripping', () {
      final c1 = CoinModel(id: '1', gradingService: 'NGC', certificationNumber: '48201948');
      expect(c1.getVerificationUrl(), equals('https://www.ngccoin.com/certlookup/48201948/'));

      final c2 = CoinModel(id: '2', gradingService: 'ngc', certificationNumber: '48201948/001');
      expect(c2.getVerificationUrl(), equals('https://www.ngccoin.com/certlookup/48201948001/'));
    });

    test('ANACS URL formatting', () {
      final c = CoinModel(id: '1', gradingService: 'ANACS', certificationNumber: '49201948');
      expect(c.getVerificationUrl(), equals('https://www.anacs.com/Verify/CertVerification.aspx?Cert=49201948'));
    });

    test('CAC Sticker vs CACG primary slab URL routing', () {
      // CACG primary slab
      final cacgSlab = CoinModel(id: '1', gradingService: 'CACG', certificationNumber: '59201948');
      expect(cacgSlab.getVerificationUrl(), equals('https://www.cacgrading.com/cert-verify/59201948'));

      // CAC sticker on PCGS slab
      final cacSticker = CoinModel(id: '2', gradingService: 'PCGS', certificationNumber: '71326501', hasCac: true);
      // PCGS service should take precedence for direct PCGS cert verify
      expect(cacSticker.getVerificationUrl(), equals('https://www.pcgs.com/cert/71326501'));

      // Pure CAC sticker lookup
      final pureCac = CoinModel(id: '3', gradingService: 'CAC', certificationNumber: '1029481');
      expect(pureCac.getVerificationUrl(), equals('https://www.caccoin.com/cert-lookup/'));
    });

    test('Raw / Uncertified / Malformed cert strings return null safely', () {
      final raw1 = CoinModel(id: '1', condition: 'MS-65');
      expect(raw1.getVerificationUrl(), isNull);

      final raw2 = CoinModel(id: '2', gradingService: 'Unknown', certificationNumber: '');
      expect(raw2.getVerificationUrl(), isNull);

      final raw3 = CoinModel(id: '3', gradingService: 'PCGS', certificationNumber: '  --- ');
      expect(raw3.getVerificationUrl(), isNull);
    });
  });

  group('Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark', () {
    late List<CoinModel> mock5kCollection;

    setUpAll(() {
      final services = ['', 'PCGS', 'NGC', 'ANACS', 'CACG'];
      final conditions = ['BS-1', 'AG-3', 'VG-8', 'F-12', 'VF-20', 'EF-40', 'AU-58', 'MS-63', 'MS-65', 'MS-70'];

      mock5kCollection = List.generate(5000, (i) {
        final year = (1800 + (i % 226)).toString();
        final service = services[i % services.length];
        final cert = service.isNotEmpty ? '${10000000 + i}' : '';
        final cond = conditions[i % conditions.length];
        final val = (10 + (i * 3) % 15000).toDouble();

        return CoinModel(
          id: 'coin_$i',
          year: year,
          mintMark: i % 2 == 0 ? 'S' : 'P',
          denomination: r'$1',
          condition: cond,
          gradingService: service,
          certificationNumber: cert,
          aiEstimatedValue: '\$$val',
          purchaseCost: '\$${val * 0.8}',
          metalContent: i % 3 == 0 ? 'Silver' : 'Copper',
        );
      });
    });

    test('5,000-row collection generation check', () {
      expect(mock5kCollection.length, equals(5000));
    });

    test('Benchmark: Sorting 5,000 coins by Year completes in < 30ms', () {
      final list = List<CoinModel>.from(mock5kCollection);
      final sw = Stopwatch()..start();
      list.sort((a, b) => a.year.compareTo(b.year));
      sw.stop();

      print('⏱️ 5,000-row Year sort time: ${sw.elapsedMicroseconds / 1000.0} ms');
      expect(sw.elapsedMilliseconds, lessThan(30), reason: 'Year sort must execute under 30ms');
    });

    test('Benchmark: Sorting 5,000 coins by Condition (Sheldon Scale) completes in < 30ms', () {
      final list = List<CoinModel>.from(mock5kCollection);
      final sw = Stopwatch()..start();
      list.sort((a, b) => a.condition.compareTo(b.condition));
      sw.stop();

      print('⏱️ 5,000-row Condition sort time: ${sw.elapsedMicroseconds / 1000.0} ms');
      expect(sw.elapsedMilliseconds, lessThan(30), reason: 'Condition sort must execute under 30ms');
    });

    test('Benchmark: Sorting 5,000 coins by Cert # completes in < 30ms', () {
      final list = List<CoinModel>.from(mock5kCollection);
      final sw = Stopwatch()..start();
      list.sort((a, b) => a.certificationNumber.compareTo(b.certificationNumber));
      sw.stop();

      print('⏱️ 5,000-row Cert # sort time: ${sw.elapsedMicroseconds / 1000.0} ms');
      expect(sw.elapsedMilliseconds, lessThan(30), reason: 'Cert # sort must execute under 30ms');
    });
  });

  group('Sprint 1 Stress Test Suite 4: Wizard Service State Machine & Concurrency', () {
    test('Rapid nextStep concurrency check (100 calls)', () async {
      await WizardService.start('guest');
      expect(WizardService.isActive, isTrue);

      for (int i = 0; i < 100; i++) {
        await WizardService.nextStep();
      }

      // After 100 calls, wizard should be dismissed cleanly
      expect(WizardService.isActive, isFalse);
    });

    test('Reset and re-start guest tour', () async {
      await WizardService.reset('guest');
      await WizardService.start('guest');
      expect(WizardService.isActive, isTrue);
      expect(WizardService.state.value?.stepIndex, equals(0));
      await WizardService.dismiss();
      expect(WizardService.isActive, isFalse);
    });
  });
}
