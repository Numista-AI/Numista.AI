import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/coin_image_service.dart';
import 'package:numista_ai/services/coin_picture_picker.dart';
import 'package:numista_ai/widgets/collection_card_image.dart';
import 'package:numista_ai/widgets/signed_storage_image.dart';

void main() {
  group('COIN-IMAGES-FIX v1.0 P5/P5a Tests', () {
    test('1. Ulysses S. Grant (2011 \$1 Presidential) composite keys & CoinPicturePicker', () {
      final program = CoinImageService.testResolveProgram(
        'Dollar',
        'Presidential \$1 Coin Program',
        subject: 'Ulysses S. Grant',
      );
      expect(program, equals('presidential-dollars'));

      final subject = CoinImageService.testResolveSubject('Ulysses S. Grant', program);
      expect(subject, equals('ulysses-s-grant'));

      final obvKeys = CoinImageService.testCompositeKeys(
        '2011', 'P', program, 'obverse', subject: subject,
      );
      final revKeys = CoinImageService.testCompositeKeys(
        '2011', 'P', program, 'reverse', subject: subject,
      );
      expect(obvKeys, contains('dollar|presidential-dollars|2011|ulysses-s-grant|obverse'));
      expect(revKeys, contains('dollar|presidential-dollars|*|shared|reverse'));

      final sel = CoinPicturePicker.select(
        {
          'Year': '2011',
          'denomination': 'Dollar',
          'program_series': 'Presidential \$1 Coin Program',
          'theme_subject': 'Ulysses S. Grant',
        },
        referenceResult: const CoinImageResult(
          obverseUrl: 'https://storage.googleapis.com/us_mint_coin_images/2011_grant_obv.jpg',
        ),
      );
      expect(sel.preferredSide, equals('obverse'));
      expect(sel.preferredCardUrl, contains('2011_grant_obv.jpg'));
    });

    testWidgets('2. Thomas Jefferson 2007-D saved user photo failure falls back to reference obverse', (tester) async {
      const brokenUserUrl = 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/test/jefferson_broken.jpg';
      const refObvUrl = 'https://storage.googleapis.com/us_mint_coin_images/2007_thomas_jefferson_obv.jpg';

      final data = {
        'Year': '2007',
        'mint_mark': 'D',
        'denomination': 'Dollar',
        'program_series': 'Presidential \$1 Coin Program',
        'theme_subject': 'Thomas Jefferson',
        'image_url_obverse': brokenUserUrl,
      };

      // Also verify CoinPicturePicker supports gs:// user URIs and ignoreUserPhotos fallback
      final gsData = {
        ...data,
        'image_url_obverse': 'gs://numista-uploads-studio-9101802118-8c9a8/users/test/jefferson.jpg',
      };
      final gsSel = CoinPicturePicker.select(gsData);
      expect(gsSel.hasUserObverse, isTrue);
      expect(gsSel.primaryObverseUrl, startsWith('gs://'));

      final fbSel = CoinPicturePicker.select(
        gsData,
        ignoreUserPhotos: true,
        referenceResult: const CoinImageResult(obverseUrl: refObvUrl),
      );
      expect(fbSel.hasUserObverse, isFalse);
      expect(fbSel.preferredCardUrl, equals(refObvUrl));

      int fetchCount = 0;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult(obverseUrl: refObvUrl);
              },
            ),
          ),
        ),
      );

      // Initially renders user photo
      final initialImg = tester.widget<SignedStorageImage>(find.byType(SignedStorageImage));
      expect(initialImg.url, equals(brokenUserUrl));
      expect(fetchCount, 0);

      // Simulate SignedStorageImage load error via its errorBuilder
      final errorWidget = initialImg.errorBuilder!(tester.element(find.byType(SignedStorageImage)));
      expect(errorWidget, isA<Widget>());

      await tester.pump(const Duration(milliseconds: 50)); // postFrameCallback + SignedPhotoUrlService coalesce
      await tester.pump(); // FutureBuilder resolves
      await tester.pump(); // SignedStorageImage renders fallback

      expect(fetchCount, 1);
      final fallbackImg = tester.widget<SignedStorageImage>(find.byType(SignedStorageImage));
      expect(fallbackImg.url, equals(refObvUrl));
    });

    test('3. Theodore Roosevelt \$1 (2013) vs Theodore Roosevelt NP 25c (2016) zero collision', () {
      final presProg = CoinImageService.testResolveProgram('Dollar', 'Presidential \$1 Coin Program');
      final atbProg = CoinImageService.testResolveProgram('Quarter', 'America the Beautiful Quarters');

      final presSubj = CoinImageService.testResolveSubject('Theodore Roosevelt', presProg);
      final atbSubj = CoinImageService.testResolveSubject('Theodore Roosevelt National Park', atbProg);
      final atbSubjShort = CoinImageService.testResolveSubject('Theodore Roosevelt', atbProg);

      expect(presSubj, equals('theodore-roosevelt'));
      expect(atbSubj, equals('theodore-roosevelt-np'));
      expect(atbSubjShort, equals('theodore-roosevelt-np'));

      final presKeys = CoinImageService.testCompositeKeys('2013', 'P', presProg, 'obverse', subject: presSubj);
      final atbKeys = CoinImageService.testCompositeKeys('2016', 'D', atbProg, 'reverse', subject: atbSubj);
      expect(presKeys.first, equals('dollar|presidential-dollars|2013|theodore-roosevelt|obverse'));
      expect(atbKeys.first, equals('quarter|america-the-beautiful|2016|theodore-roosevelt-np|reverse'));
    });

    test('4. FDR (2014), Harry S. Truman (2015), Dwight D. Eisenhower (2015) exact slugs', () {
      expect(
        CoinImageService.testResolveSubject('Franklin D. Roosevelt', 'presidential-dollars'),
        equals('franklin-d-roosevelt'),
      );
      expect(
        CoinImageService.testResolveSubject('Harry S. Truman', 'presidential-dollars'),
        equals('harry-s-truman'),
      );
      expect(
        CoinImageService.testResolveSubject('Dwight D. Eisenhower', 'presidential-dollars'),
        equals('dwight-d-eisenhower'),
      );
      // Must not collide with Eleanor Roosevelt
      expect(
        CoinImageService.testResolveSubject('Eleanor Roosevelt', 'american-women-quarters'),
        equals('eleanor-roosevelt'),
      );
    });

    test('5. Grover Cleveland (1st & 2nd term) and Richard Nixon (2016) exact slugs', () {
      expect(
        CoinImageService.testResolveSubject('Grover Cleveland First Term', 'presidential-dollars'),
        equals('grover-cleveland-1st'),
      );
      expect(
        CoinImageService.testResolveSubject('Grover Cleveland Second Term', 'presidential-dollars'),
        equals('grover-cleveland-2nd'),
      );
      expect(
        CoinImageService.testResolveSubject('Richard M. Nixon', 'presidential-dollars'),
        equals('richard-nixon'),
      );
    });

    test('6. 2026 Semiquincentennial Quarters resolve all 5 distinct designs', () {
      final designs = <String, String>{
        'Mayflower Compact & Pilgrim Couple': 'mayflower-compact',
        'Revolutionary War': 'revolutionary-war',
        'Declaration of Independence': 'declaration-of-independence',
        'U.S. Constitution': 'us-constitution',
        'Gettysburg Address': 'gettysburg-address',
      };
      for (final entry in designs.entries) {
        final prog = CoinImageService.testResolveProgram(
          '25 Cents',
          'United States Semiquincentennial (250th Anniversary)',
          subject: entry.key,
        );
        expect(prog, equals('quarter'));
        final subj = CoinImageService.testResolveSubject(entry.key, prog, year: '2026');
        expect(subj, equals(entry.value));
        final keys = CoinImageService.testCompositeKeys('2026', 'P', prog, 'reverse', subject: subj);
        expect(keys.first, equals('quarter|quarter|2026|${entry.value}|reverse'));
      }
    });

    test('7. ATB San Antonio Missions (2019) composite key', () {
      final subj = CoinImageService.testResolveSubject(
        'San Antonio Missions National Historical Park',
        'america-the-beautiful',
      );
      expect(subj, equals('san-antonio-missions'));
      final keys = CoinImageService.testCompositeKeys(
        '2019', 'D', 'america-the-beautiful', 'reverse', subject: subj,
      );
      expect(keys.first, equals('quarter|america-the-beautiful|2019|san-antonio-missions|reverse'));
    });

    test('8. American Women Quarters 2022 honorees & shared obverse', () {
      final honorees = <String, String>{
        'Maya Angelou': 'maya-angelou',
        'Sally Ride': 'sally-ride',
        'Wilma Mankiller': 'wilma-mankiller',
        'Nina Otero-Warren': 'nina-otero-warren',
        'Anna May Wong': 'anna-may-wong',
      };
      for (final entry in honorees.entries) {
        final subj = CoinImageService.testResolveSubject(entry.key, 'american-women-quarters');
        expect(subj, equals(entry.value));
        final revKeys = CoinImageService.testCompositeKeys(
          '2022', 'P', 'american-women-quarters', 'reverse', subject: subj,
        );
        final obvKeys = CoinImageService.testCompositeKeys(
          '2022', 'P', 'american-women-quarters', 'obverse', subject: subj,
        );
        expect(revKeys.first, equals('quarter|american-women-quarters|2022|${entry.value}|reverse'));
        expect(obvKeys, contains('quarter|american-women-quarters|*|shared|obverse'));
        expect(
          CoinPicturePicker.distinctiveSide(program: 'american-women-quarters', year: '2022'),
          equals('reverse'),
        );
      }
    });
  });
}
