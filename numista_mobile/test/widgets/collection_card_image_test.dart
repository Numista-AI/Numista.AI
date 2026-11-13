import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/canonical_mint_asset_service.dart';
import 'package:numista_ai/services/coin_image_service.dart';
import 'package:numista_ai/utils/collection_image_utils.dart';
import 'package:numista_ai/widgets/collection_card_image.dart';

void main() {
  group('CollectionCardImage Production Widget Tests (MF-I2, MF-I3\', MF-I5\', MF-I6)', () {
    testWidgets('Case 1 (MF-I3\'): User-uploaded Firebase Storage photo (users%2F) yields in resolveFromMap, renders user photo, and bypasses network fetch even on 2026 SKU', (tester) async {
      int fetchCount = 0;
      const userUrl = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon%2Fcoins%2Fobv.jpg';
      final data = {
        'image_url_obverse': userUrl,
        'Year': '2026',
        'mint_mark': 'P',
        'denomination': '1¢',
        'title': '2026 Lincoln Cent',
      };

      expect(CanonicalMintAssetService.hasUserUploadedPhotos(data), isTrue);
      expect(CanonicalMintAssetService.resolveFromMap(data), isNull);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult();
              },
            ),
          ),
        ),
      );

      expect(fetchCount, 0, reason: 'Valid user photo must bypass network reference fetch');
      final img = tester.widget<Image>(find.byType(Image));
      expect((img.image as NetworkImage).url, equals(userUrl));
    });

    testWidgets('Case 2: Reverse-only user photo renders reverse and bypasses network fetch', (tester) async {
      int fetchCount = 0;
      const revUrl = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon%2Fcoins%2Frev.jpg';
      final data = {
        'image_url_reverse': revUrl,
        'Year': '1964',
        'denomination': 'Half Dollar',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult();
              },
            ),
          ),
        ),
      );

      expect(fetchCount, 0, reason: 'Valid reverse-only user photo must bypass network fetch');
      final img = tester.widget<Image>(find.byType(Image));
      expect((img.image as NetworkImage).url, equals(revUrl));
    });

    // v2.1 MF-SAG-I1: Case 3 split. (3a) unowned URL with NO user-upload signal is treated as absent:
    // never rendered, precedence continues to reference (matches shipped :6369-6406 + hasUserUploadedPhotos :27).
    testWidgets('Case 3a: unowned non-user URL is never rendered; reference fetch proceeds', (tester) async {
      int fetchCount = 0;
      final data = {'image_url_obverse': 'https://evil.firebasestorage.app/malicious.jpg', 'Year': '1964', 'denomination': 'Half Dollar'};
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(data: data,
          imageFetcher: ({required year, mint, denomination, series, subject}) async { fetchCount++; return const CoinImageResult(); }))));
      await tester.pump();
      expect(fetchCount, 1);
      expect(find.byWidgetPredicate((w) => w is Image && w.image is NetworkImage &&
          (w.image as NetworkImage).url.contains('evil')), findsNothing);
    });

    // (3b) confirmed user upload (isUserUrl matches '/users/') whose selected URL is unowned -> placeholder, no fetch, no canonical.
    testWidgets('Case 3b: confirmed user upload with unowned selected URL fails closed', (tester) async {
      int fetchCount = 0;
      final data = {'image_url_obverse': 'https://evil.example/users/x.jpg', 'Year': '1964', 'denomination': 'Half Dollar'};
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(data: data,
          imageFetcher: ({required year, mint, denomination, series, subject}) async { fetchCount++; return const CoinImageResult(); }))));
      expect(fetchCount, 0);
      expect(find.byIcon(Icons.image_not_supported_outlined), findsOneWidget);
    });

    testWidgets('Case 4 (MF-I6): Non-URL sentinel strings ("N/A", "pending", "none", bare filename) return "" from extractUserPhoto and fall through to reference/canonical', (tester) async {
      for (final junk in const ['N/A', 'pending', 'none', 'null', '—', 'gs://bucket/file.jpg', 'IMG_001.jpg']) {
        final data = {
          'image_url_obverse': junk,
          'Year': '1964',
          'mint_mark': 'D',
          'denomination': 'Half Dollar',
        };

        expect(extractUserPhoto(data, isObverse: true), isEmpty, reason: 'Junk "$junk" must be ignored by extractUserPhoto');

        int fetchCount = 0;
        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: CollectionCardImage(
                key: ValueKey('junk_$junk'),
                data: data,
                imageFetcher: ({required year, mint, denomination, series, subject}) async {
                  fetchCount++;
                  return const CoinImageResult(
                    reverseUrl: 'https://storage.googleapis.com/us_mint_coin_images/Numista_Attributed_Coins%20(1)/1964_kennedy_rev.jpg',
                  );
                },
              ),
            ),
          ),
        );
        await tester.pump();

        expect(fetchCount, 1, reason: 'Card with non-URL junk "$junk" must fall through to reference fetcher');
        expect(find.byType(Image), findsOneWidget);
      }
    });

    testWidgets('Case 5: Reference fetch triggered when no user photo and no canonical asset (1964 Kennedy)', (tester) async {
      final data = {
        'Year': '1964',
        'mint_mark': 'D',
        'denomination': 'Half Dollar',
        'program_series': 'Kennedy Half Dollar',
      };

      expect(CanonicalMintAssetService.resolveFromMap(data), isNull);

      int fetchCount = 0;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult(
                  reverseUrl: 'https://storage.googleapis.com/us_mint_coin_images/Numista_Attributed_Coins%20(1)/1964_kennedy_rev.jpg',
                );
              },
            ),
          ),
        ),
      );
      await tester.pump();

      expect(fetchCount, 1, reason: 'Reference fetcher must be called exactly once');
      expect(find.byType(Image), findsOneWidget);
    });

    testWidgets('Case 6: MF-V3-3 Steal-Guard: Subject known + reverse null displays placeholder (no obverse fallback)', (tester) async {
      int fetchCount = 0;
      final data = {
        'Year': '1964',
        'denomination': 'Half Dollar',
        'theme_subject': 'Specific Commemorative Subject',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult(
                  obverseUrl: 'https://storage.googleapis.com/us_mint_coin_images/Numista_Attributed_Coins%20(1)/generic_obv.jpg',
                  reverseUrl: null,
                );
              },
            ),
          ),
        ),
      );
      await tester.pump();

      expect(fetchCount, 1);
      expect(find.byIcon(Icons.image_not_supported_outlined), findsOneWidget);
    });

    testWidgets('Case 7 (MF-I5\'): Semantic RequestKey refresh on the SAME State instance triggers second fetch when Year changes from "" to "1964"', (tester) async {
      int fetchCount = 0;
      const cardKey = ValueKey('card');
      final dataInitial = {
        'Year': '',
        'denomination': 'Half Dollar',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              key: cardKey,
              data: dataInitial,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult();
              },
            ),
          ),
        ),
      );
      await tester.pump();
      final stateBefore = tester.state(find.byKey(cardKey));
      expect(fetchCount, 1);

      final dataUpdated = {
        'Year': '1964',
        'denomination': 'Half Dollar',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
              key: cardKey,
              data: dataUpdated,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult();
              },
            ),
          ),
        ),
      );
      await tester.pump();
      final stateAfter = tester.state(find.byKey(cardKey));

      expect(identical(stateBefore, stateAfter), isTrue, reason: 'Must update the exact same State instance via didUpdateWidget');
      expect(fetchCount, 2, reason: 'Mutating Year must invalidate RequestKey and trigger second fetch');
    });

    // v2.1 MF-SAG-I1
    testWidgets('Case 8: 2026 cent with canonical match + unowned URL in photo field still shows canonical', (tester) async {
      final data = {'Year': '2026', 'denomination': 'Cent', 'mint_mark': 'P', 'title': '2026 Coin',
                    'image_url_obverse': 'https://evil.example/x.jpg'};
      final canon = CanonicalMintAssetService.resolveFromMap(data)!;
      final expected = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(data: data,
          imageFetcher: ({required year, mint, denomination, series, subject}) async => fail('no fetch')))));
      expect((tester.widget<Image>(find.byType(Image)).image as NetworkImage).url, equals(expected));
    });

    testWidgets('Case 9: owned user reverse + unowned obverse renders the reverse', (tester) async {
      const rev = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon_user_1%2Fcoins%2Frev.jpg?alt=media';
      final data = {'image_url_reverse': rev, 'image_url_obverse': 'https://evil.example/x.jpg'};
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(data: data))));
      expect((tester.widget<Image>(find.byType(Image)).image as NetworkImage).url, equals(rev));
    });

    // v2.1 MF-SAG-I5
    testWidgets('Case 10: clearing the user photo on the same State starts a reference fetch', (tester) async {
      var fetchCount = 0;
      Future<CoinImageResult> f({required year, mint, denomination, series, subject}) async { fetchCount++; return const CoinImageResult(); }
      const key = Key('c10');
      const rev = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon_user_1%2Fcoins%2Frev.jpg?alt=media';
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(key: key, imageFetcher: f,
          data: const {'Year': '1964', 'denomination': 'Half Dollar', 'image_url_reverse': rev}))));
      expect(fetchCount, 0);
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(key: key, imageFetcher: f,
          data: const {'Year': '1964', 'denomination': 'Half Dollar'}))));
      await tester.pump();
      expect(fetchCount, 1);
    });

    // v2.3 MF-2: signal-only uploads (microscope/hardware agent or stored_obv/stored_rev)
    testWidgets('Case 11 (v2.3 MF-2): scan_source microscope with empty photo fields falls through to reference fetch', (tester) async {
      var fetchCount = 0;
      const refUrl = 'https://storage.googleapis.com/us_mint_coin_images/Numista_Attributed_Coins%20(1)/1964_kennedy_rev.jpg';
      final data = {'scan_source': 'microscope', 'Year': '2026', 'denomination': 'Cent', 'mint_mark': 'P', 'title': '2026 Lincoln Cent'};
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(data), isTrue);
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(
        data: data,
        imageFetcher: ({required year, mint, denomination, series, subject}) async {
          fetchCount++;
          return const CoinImageResult(reverseUrl: refUrl);
        },
      ))));
      await tester.pump();
      expect(fetchCount, 1, reason: 'Signal-only microscope upload with no direct HTTP URL must fall through to reference fetch');
      expect((tester.widget<Image>(find.byType(Image)).image as NetworkImage).url, equals(refUrl));
    });

    testWidgets('Case 12 (v2.3 MF-2): owned stored_obv signal-only (empty direct fields) suppresses canonical and triggers reference fetch', (tester) async {
      var fetchCount = 0;
      const storedUrl = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon%2Fcoins%2Fstored_obv.jpg?alt=media';
      final data = {'stored_obv': storedUrl, 'Year': '2026', 'denomination': 'Cent', 'mint_mark': 'P', 'title': '2026 Lincoln Cent'};
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(data), isTrue);
      expect(extractUserPhoto(data, isObverse: true), isEmpty, reason: 'stored_obv is a signal only, not displayed directly');
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(
        data: data,
        imageFetcher: ({required year, mint, denomination, series, subject}) async {
          fetchCount++;
          return const CoinImageResult();
        },
      ))));
      await tester.pump();
      expect(fetchCount, 1);
    });

    testWidgets('Case 13 (v2.3 MF-2): unowned reverse + owned obverse on user upload selects reverse and fails closed to placeholder', (tester) async {
      var fetchCount = 0;
      const ownedObv = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon%2Fcoins%2Fobv.jpg?alt=media';
      final data = {
        'image_url_reverse': 'https://evil.example/users/rev.jpg',
        'image_url_obverse': ownedObv,
        'Year': '1964',
        'denomination': 'Half Dollar',
      };
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardImage(
        data: data,
        imageFetcher: ({required year, mint, denomination, series, subject}) async {
          fetchCount++;
          return const CoinImageResult();
        },
      ))));
      expect(fetchCount, 0);
      expect(find.byIcon(Icons.image_not_supported_outlined), findsOneWidget);
    });
  });
}
