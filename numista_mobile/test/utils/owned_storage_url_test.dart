import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/utils/owned_storage_url.dart';

void main() {
  group('isOwnedStorageUrl Real Allowlist & Index public_url Verification (MF-I1, MF-I7\')', () {
    test('Accepts Form A: Real Firebase Storage download URL for project bucket', () {
      const realUserUrl = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon_user_1%2Fcoins%2F123.jpg?alt=media';
      expect(isOwnedStorageUrl(realUserUrl), isTrue);
    });

    test('MF-I7\': Accepts every real emitted public_url shape from _scripts/build_image_index.py, build_currency_image_index.py, and promote_user_photos.py', () {
      // 1. _scripts/build_image_index.py:55-56 (SCAN_TARGETS Tier 1: us_mint_coin_images / Numista_Attributed_Coins (1)/ with space encoded as %20 at :302)
      const scanTargetMintUrl = 'https://storage.googleapis.com/us_mint_coin_images/Numista_Attributed_Coins%20(1)/2024_america-the-beautiful_reverse.jpg';
      // 2. _scripts/build_image_index.py:62-63 (SCAN_TARGETS Tier 2: numista-reference-library / reference_library/bulk_programs/)
      const scanTargetBulkUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/1999_new-jersey_50-state-quarters_reverse.jpg';
      // 3. _scripts/build_image_index.py:69-70 (SCAN_TARGETS Tier 3: numista-reference-library / reference_library/wikimedia_uscoin/)
      const scanTargetWikiUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/1964_kennedy-half-dollar_reverse.png';
      // 4. _scripts/build_image_index.py:76-98 (SCAN_TARGETS Tier 2/5: rare_uscoin, balabaskar_coins, 2026_series, user_contributed)
      const scanTargetRareUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/rare_uscoin/1909_s_vdb_lincoln-cent_obverse.jpg';
      const scanTarget2026Url = 'https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026-CENT-P_reverse.jpg';
      const scanTargetContribUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/1921_morgan-dollar_obverse.jpg';
      // 5. _scripts/build_currency_image_index.py:40-41, 267 (REFERENCE_BUCKET = numista-reference-library, GCS_PREFIX = reference_library/us_banknotes/)
      const currencyBanknoteUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/us_banknotes/fr_1613_n_star_obv.jpg';
      // 6. _scripts/promote_user_photos.py:16-17, 35-37, 130 (BUCKET_NAME = numista-uploads-studio-9101802118-8c9a8, reference/{program_slug}/{year}_{program_slug}_{side}.jpg)
      const promotedUserRefUrl = 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference/morgan-dollar/1881_morgan-dollar_obverse.jpg';

      expect(isOwnedStorageUrl(scanTargetMintUrl), isTrue);
      expect(isOwnedStorageUrl(scanTargetBulkUrl), isTrue);
      expect(isOwnedStorageUrl(scanTargetWikiUrl), isTrue);
      expect(isOwnedStorageUrl(scanTargetRareUrl), isTrue);
      expect(isOwnedStorageUrl(scanTarget2026Url), isTrue);
      expect(isOwnedStorageUrl(scanTargetContribUrl), isTrue);
      expect(isOwnedStorageUrl(currencyBanknoteUrl), isTrue);
      expect(isOwnedStorageUrl(promotedUserRefUrl), isTrue);
      // v2.1 MF-SAG-I7: balabaskar prefix (build_image_index.py:84)
      const balabaskarUrl = 'https://storage.googleapis.com/numista-reference-library/reference_library/balabaskar_coins/fixture_coin_obverse.jpg';
      expect(isOwnedStorageUrl(balabaskarUrl), isTrue);
    });

    test('v2.1 MF-SAG-I3: rejects traversal, encoded dots, userinfo and port', () {
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/%2E%2E/other-bucket/x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/../other-bucket/x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/a%2f..%2fb/x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2F..%2Fx.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o'), isFalse);
      expect(isOwnedStorageUrl('https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2F%2Fcoin.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://user:pw@storage.googleapis.com/us_mint_coin_images/x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com:8443/us_mint_coin_images/x.jpg'), isFalse);
      expect(isOwnedStorageUrl('/assets/../secret.png'), isFalse);
    });

    test('v2.2 MF-SAG-I3: raw dot segments inside an allowed root are rejected pre-normalization', () {
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/a/../x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/./x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/../numista-reference-library/x.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/us_mint_coin_images/a%20b/x.jpg'), isTrue); // %20 still allowed
    });

    test('Accepts Form B: Real direct upload bucket roots', () {
      const upload1 = 'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/user_abc/front.jpg';
      const gcsFb = 'https://storage.googleapis.com/studio-9101802118-8c9a8.firebasestorage.app/o/photo.png';
      expect(isOwnedStorageUrl(upload1), isTrue);
      expect(isOwnedStorageUrl(gcsFb), isTrue);
    });

    test('Accepts relative same-origin path', () {
      expect(isOwnedStorageUrl('/assets/images/placeholder.png'), isTrue);
    });

    test('Rejects fabricated buckets', () {
      expect(isOwnedStorageUrl('https://storage.googleapis.com/numista-vault.firebasestorage.app/coin.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/numista-ai-images/coin.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/numista-catalog-assets/coin.jpg'), isFalse);
    });

    test('Rejects attacker-registrable wildcards and open prefixes', () {
      expect(isOwnedStorageUrl('https://evil.firebasestorage.app/coin.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://evil.web.app/coin.jpg'), isFalse);
      expect(isOwnedStorageUrl('https://storage.googleapis.com/numista-uploads-studio-evil/coin.jpg'), isFalse);
    });

    test('Rejects protocol-relative backslash and double-slash attacks', () {
      expect(isOwnedStorageUrl(r'/\evil.com/coin.jpg'), isFalse);
      expect(isOwnedStorageUrl('//evil.com/coin.jpg'), isFalse);
    });

    test('Rejects non-HTTPS schemes and empty strings', () {
      expect(isOwnedStorageUrl('http://storage.googleapis.com/us_mint_coin_images/penny.jpg'), isFalse);
      expect(isOwnedStorageUrl(''), isFalse);
      expect(isOwnedStorageUrl(null), isFalse);
    });
  });
}
