import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/utils/catalog_image_guard.dart';

void main() {
  group('isApprovedCatalogImageUrl Guard Tests (v1.8 F3, v1.9 MF-F3-RawPath, v2.0.1)', () {
    test('Rejects private Firebase Storage, unpromoted uploads, traversal, userinfo, port, and bare reference root', () {
      expect(isApprovedCatalogImageUrl('https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fu1%2Fphoto.jpg?alt=media'), isFalse);
      expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/u1/original.jpg'), isFalse);
      expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference'), isFalse);
      expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/us_mint_coin_images/../numista-uploads-studio-9101802118-8c9a8/users/u1/x.jpg'), isFalse);
      expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/us_mint_coin_images/%2E%2E/other/x.jpg'), isFalse);
      expect(isApprovedCatalogImageUrl('https://user@storage.googleapis.com/us_mint_coin_images/x.png'), isFalse);
      expect(isApprovedCatalogImageUrl('assets/catalog/images/../../secret.png'), isFalse);
      expect(isApprovedCatalogImageUrl('assets/catalog/images/'), isFalse);
      // v1.9 MF-F3-RawPath: in-allowlist normalization rejected pre-parse
      expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/us_mint_coin_images/a/../x.jpg'), isFalse);
      expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/us_mint_coin_images/./x.jpg'), isFalse);
      expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference/a/../x.jpg'), isFalse);
      expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/us_mint_coin_images/../numista-reference-library/x.jpg'), isFalse);
    });

    test('Accepts approved public reference buckets, %20 spaces, and trimmed whitespace', () {
      expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference/fixture_program/fixture_doc.jpg'), isTrue);
      expect(isApprovedCatalogImageUrl(' https://storage.googleapis.com/us_mint_coin_images/fixture.png '), isTrue);
      expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/us_mint_coin_images/Numista_Attributed_Coins%20(1)/2024_america-the-beautiful_reverse.jpg'), isTrue);
      expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/1999_nj_reverse.jpg'), isTrue);
      expect(isApprovedCatalogImageUrl('assets/catalog/images/morgan_1921.jpg'), isTrue);
    });
  });
}
