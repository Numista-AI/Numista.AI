// numista_mobile/test/services/canonical_mint_asset_service_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/canonical_mint_asset_service.dart';
import 'package:numista_ai/screens/add_coins_hub.dart';
import 'package:numista_ai/services/coin_image_service.dart';

void main() {
  group('CanonicalMintAssetService - 28 Live Firestore Document Tests + 14 Synthetic Tracker Tests', () {
    test('Row 01 (e91efa62-4e8d-4920-a928-c0c97659bcdc | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'W', 'Denomination': 'Dollar', 'Program/Series': 'American Silver Eagle', 'Theme/Subject': 'America250', 'Personal Notes': '26EA American Eagle 2026 One Ounce Silver Proof (250 privy)', 'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/American%20Eagle%202023%20One%20Ounce%20Silver%20Proof%20Coin%20Obverse.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/American%20Eagle%202023%20One%20Ounce%20Silver%20Proof%20Coin%20Reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26EA_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26EA_image_2.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_a.webp'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_b.webp'));
    });

    test('Row 02 (be10e44ce5b4ff4b46c92426cc7f59a254ed675c | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': 'Dollar', 'Program/Series': 'Morgan Dollar', 'Theme/Subject': 'Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026)', 'Personal Notes': '2026 Morgan Silver Enhanced Un | Mint Facility: West Point (no mint mark)' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_2.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_3.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_a.webp'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_b.webp'));
    });

    test('Row 03 (a59853c1-b72b-414d-8b8e-de6813c29996 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{
        'Year': '2026',
        'Mint Mark': 'P',
        'Denomination': 'Dollar',
        'Program/Series': 'Peace Dollar',
        'Theme/Subject': 'America250',
        'Variety': 'Reverse Proof',
        'Condition': 'Reverse Proof',
        'Retailer Item No.': '26XL',
        'Personal Notes': 'Peace Silver Dollar 2026 Rever',
        'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/Peace-Dollar-Reverse-Proof-Obverse.jpg',
        'image_url_reverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/Peace-Dollar-Reverse-Proof-Reverse.jpg',
      };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XL_image_3.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XL_image_2.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xl___a.webp'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XL_image_1.jpg'));
    });

    test('Row 04 (71e2d4ae92bc4312a4198a3a0cc21fcb | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': 'Set', 'Program/Series': 'Uncirculated Sets', 'Theme/Subject': '250th Anniversary Uncirculated Coin Set', 'name': '2026 United States Mint Uncirculated Coin Set', 'product_code': '26RJ', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_a.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RJ_image_1.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RJ_image_2.jpg'));
    });

    test('Row 05 (91f8821265bfe8a33fbd97e21f102c67fdf849fd | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': 'Set', 'Program/Series': 'Uncirculated Coin Set', 'Personal Notes': 'Uncirculated Coin Set 2026' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RJ_image_1.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RJ_image_2.jpg'));
    });

    test('Row 06 (0e68ecba760df66bf824ec1ba2c86b32318d002d | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': '\$1', 'Program/Series': 'American Innovation', 'Personal Notes': 'American Innovation 2026 \$1 Co' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26GC_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26gc_b.webp'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_american_innovation_obverse.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26GC_image_2.jpg'));
    });

    test('Row 07 (7a32932ebc4e94a586534e7180cd1c4372c4f17d | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'D', 'Denomination': 'Dollar', 'Program/Series': 'Semiquincentennial President', 'Theme/Subject': 'Donald J. Trump Semiquincentennial 250th Anniversary Roll (July 4th Privy eligible)', 'Personal Notes': '26SQRP Semiquincentennial President D | Mint Facility: Philadelphia (P)' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 08 (nAnGLwGvhfIOibf6kIft | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'P', 'Denomination': 'Dime', 'Program/Series': 'Roosevelt Dimes', 'Theme/Subject': 'Franklin D. Roosevelt' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-P.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg'));
      expect(pair.fallbackObverseUrl, isNull);
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 09 (rv9SCUTahBuqJkkiJyga | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'D', 'Denomination': 'Dime', 'Program/Series': 'Roosevelt Dimes', 'Theme/Subject': 'Franklin D. Roosevelt' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Obverse-Unc-D.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg'));
      expect(pair.fallbackObverseUrl, isNull);
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 10 (0172d0ee64284a12a8aa269ce805ec07 | eric.seaman@yahoo.com): MF-B user-upload guard protects Eric\'s microscope photos (returns null)', () {
      final doc = <String, dynamic>{
        'id': '0172d0ee64284a12a8aa269ce805ec07',
        'Year': '2026',
        'Mint Mark': 'P',
        'Denomination': 'Quarter Dollar (25C)',
        'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
        'Theme/Subject': 'Mayflower Compact & Pilgrim Couple',
        'scan_source': 'microscope',
        'source': 'Hardware Agent',
        'image_url_obverse': 'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/microscope/eric@numista.ai/2026_semiquincentennial_mayflower_compact_quarter_p_Obverse_20260701_1731.jpg',
        'image_url_reverse': 'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/microscope/eric@numista.ai/2026_semiquincentennial_mayflower_compact_quarter_p_Reverse_20260701_1731.jpg',
      };
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(doc), isTrue);
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      // Non-destructive: must return null so user\'s microscope photos are never overwritten!
      expect(pair, isNull);
    });

    test('Row 10 Reference Resolution: resolves Mayflower catalog pair when no user photos are present', () {
      final doc = <String, dynamic>{
        'Year': '2026',
        'Mint Mark': 'P',
        'Denomination': 'Quarter Dollar (25C)',
        'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
        'Theme/Subject': 'Mayflower Compact & Pilgrim Couple',
      };
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(doc), isFalse);
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg'));
      expect(pair.fallbackObverseUrl, isNull);
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 10 D-mint Path (R2.8.19, SAG 93 must-fix): 2026-MAYFLOWER-D fallbackObverseUrl is fully qualified with \$_base', () {
      final doc = <String, dynamic>{
        'Year': '2026',
        'Mint Mark': 'D',
        'Denomination': 'Quarter Dollar (25C)',
        'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
        'Theme/Subject': 'Mayflower Compact & Pilgrim Couple',
      };
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(doc), isFalse);
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.sku, equals('2026-MAYFLOWER-D'));
      expect(pair.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg'));
      // Cross-mint fallback to the P catalog obverse is kept as written in R2.8.18; this test documents it.
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg'));
      expect(pair.fallbackObverseUrl!.startsWith('https://'), isTrue);
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 11 (8f2197d5d03a428db24486b4ee375a5e | eric.seaman@yahoo.com): MF-B user-upload guard protects Eric\'s microscope photos (returns null)', () {
      final doc = <String, dynamic>{
        'id': '8f2197d5d03a428db24486b4ee375a5e',
        'Year': '2026',
        'Mint Mark': 'D',
        'Denomination': 'Half Dollar',
        'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
        'Theme/Subject': '250th Anniversary of American Independence',
        'scan_source': 'microscope',
        'source': 'Hardware Agent',
        'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/eric@numista.ai/coins/b22f8905-4eca-45e9-ba57-920fb5427b22/obverse.jpg?t=1782428155',
        'image_url_reverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/eric@numista.ai/coins/b22f8905-4eca-45e9-ba57-920fb5427b22/reverse.jpg?t=1782428156',
      };
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(doc), isTrue);
      expect(CanonicalMintAssetService.resolveFromMap(doc), isNull);
    });

    test('Row 11 Reference Resolution: 2026-HALF-D Catalog Lookup (Without User Photos)', () {
      final doc = <String, dynamic>{
        'Year': '2026',
        'Mint Mark': 'D',
        'Denomination': 'Half Dollar (50C)',
        'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
        'Theme/Subject': 'Semiquincentennial Half Dollar Enduring Liberty',
      };
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(doc), isFalse);
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 12 (5b424047-77e0-496e-a513-6ef180b515a6 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2005', 'Mint Mark': 'D', 'Denomination': 'Quarter', 'Program/Series': '50 State Quarters', 'program_series': '50 State Quarters', 'Theme/Subject': 'Kansas', 'theme_subject': 'Kansas', 'Personal Notes': 'Oregon', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/50_state_quarters/2003-50-state-quarters-coin-arkansas-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/2005_United_States_quarters/50_State_quarter__Kansas_/Kansas_quarter_2C_reverse_side_2C_2005.jpg'));
    });

    test('Row 13 (3346cda5-5935-4303-bf62-de43041f3175 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2019', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'American Memorial Park (Northern Mariana Islands)', 'theme_subject': 'American Memorial Park (Northern Mariana Islands)', 'Personal Notes': 'War in the Pacific National Historical Park (Guam) - ATB-P tube', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2015-america-the-beautiful-quarters-coin-blue-ridge-parkway-north-carolina-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 14 (b243621c-5a35-45f0-84bf-8786eb1547f9 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2020', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Salt River Bay National Historical Park and Ecological Preserve (U.S. Virgin Islands)', 'theme_subject': 'Salt River Bay National Historical Park and Ecological Preserve (U.S. Virgin Islands)', 'Personal Notes': 'Marsh-Billings-Rockefeller National Historical Park (Vermont) - ATB-P', 'personal_notes': 'ATB- P TUBE', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 15 (c336e53e-4105-44bd-8c08-f30ae0328467 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2013', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Mount Rushmore National Memorial (South Dakota)', 'theme_subject': 'Mount Rushmore National Memorial (South Dakota)', 'Personal Notes': 'Mount Rushmore National Memorial (South Dakota) - ATB-P', 'personal_notes': 'ATB-P', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-mount-hood-oregon-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 16 (cba5e585-758f-4b10-be7a-1a59a1f4b2e6 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2018', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Cumberland Island National Seashore (Georgia)', 'theme_subject': 'Cumberland Island National Seashore (Georgia)', 'Personal Notes': 'Apostle Islands National Lakeshore (Wisconsin) - ATB-P tube', 'personal_notes': 'ATB-P tube', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2016-america-the-beautiful-quarters-coin-cumberland-gap-kentucky-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 17 (d7fec246-983f-40de-8b58-854f59460bce | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2018', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Block Island National Wildlife Refuge (Rhode Island)', 'theme_subject': 'Block Island National Wildlife Refuge (Rhode Island)', 'Personal Notes': 'Voyageurs National Park (Minnesota) - ATB-P tube', 'personal_notes': 'ATB-P tube', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ellis-island-new-jersey-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 18 (Wq2UhSQNs67u34VFJDaI | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '1962', 'Denomination': 'Cent', 'Program/Series': 'Lincoln Cent (Memorial Reverse)', 'program_series': 'Lincoln Cent (Memorial Reverse)', 'Theme/Subject': 'Abraham Lincoln', 'theme_subject': 'Abraham Lincoln', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/penny/2008-lincoln-one-cent-reverse-2000x2000.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_cents/Obverses_of_United_States_cents/2002_Penny_Proof_Obv.png'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 19 (UOBfFO2mqgLg86NSsyss | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2019', 'Mint Mark': 'W', 'mint_mark': 'W', 'Denomination': 'Quarter Dollar', 'Program/Series': 'America the Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'San Antonio Missions', 'theme_subject': 'San Antonio Missions', 'Personal Notes': 'HV Coin Club', 'image_url_obverse': 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/1932-george-washington-quarter-obverse.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/america_the_beautiful/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 20 (3f437576-fa20-4ef1-95c0-01e10eaf43a8 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2017', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Effigy Mounds National Monument (Iowa)', 'theme_subject': 'Effigy Mounds National Monument (Iowa)', 'Personal Notes': 'Ozark National Scenic Riverways (Missouri) - ATB-TUBE', 'personal_notes': 'ATB-P tube', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 21 (6ff959a0-26f8-451f-aa4c-064b5ef68939 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2017', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Frederick Douglass National Historic Site (District of Columbia)', 'theme_subject': 'Frederick Douglass National Historic Site (District of Columbia)', 'Personal Notes': 'Frederick Douglass National Historic Site (District of Columbia)', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 22 (96eeb7b6-6c4e-4a62-bb8e-80b69706d915 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2010', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Yellowstone National Park (Wyoming)', 'theme_subject': 'Yellowstone National Park (Wyoming)', 'Personal Notes': 'Yellowstone National Park (Wyoming) - ATB-P TUBE - to Poor Condition', 'personal_notes': 'ATB-P TUBE - Poor Condition', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 23 (ab35ab5d-d51f-4b9c-bc94-ff87def52bc6 | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2017', 'Mint Mark': 'D', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'George Rogers Clark National Historical Park (Indiana)', 'theme_subject': 'George Rogers Clark National Historical Park (Indiana)', 'Personal Notes': 'George Rogers Clark National Historical Park (Indiana)', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 24 (b785236f-ca64-4461-9ee4-01cad3a7d60e | eric.seaman@yahoo.com): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2017', 'Mint Mark': 'P', 'Denomination': 'Quarter', 'Program/Series': 'America The Beautiful Quarters', 'program_series': 'America the Beautiful Quarters', 'Theme/Subject': 'Ozark National Scenic Riverways (Missouri)', 'theme_subject': 'Ozark National Scenic Riverways (Missouri)', 'Personal Notes': 'Effigy Mounds National Monument (Iowa) - ATB-P tube', 'personal_notes': 'ATB-P TUBE', 'image_url_obverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg', 'image_url_reverse': 'https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 25 (0a2bc793-8d62-47c3-88cd-7a5b9be434ba | eric@numista.ai): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': 'Set', 'Program/Series': 'Uncirculated Coin Set', 'Personal Notes': 'Item # 26RJ - Uncirculated Coin Set 2026' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RJ_image_1.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RJ_image_2.jpg'));
    });

    test('Row 26 (be10e44ce5b4ff4b46c92426cc7f59a254ed675c | eric@numista.ai): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Denomination': 'Dollar', 'Program/Series': 'Morgan Dollar', 'Theme/Subject': 'Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026)', 'Personal Notes': '2026 Morgan Silver Enhanced Un | Mint Facility: West Point (no mint mark)' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_2.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_3.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_a.webp'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_b.webp'));
    });

    test('Row 27 (faa5b1cf-7fd1-4fe6-90e8-51c2eaa7122c | eric@numista.ai): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2026', 'Mint Mark': 'D', 'Program/Series': 'Semiquincentennial President', 'Personal Notes': 'Item # 26SQRP Semiquincentennial President D' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Row 28 (2fa325166682b70aa0d64da45786c94aa4742d21 | eric@numista.ai): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'Year': '2023', 'Denomination': 'Set', 'Program/Series': 'Silver Proof Set', 'Personal Notes': 'Silver Proof Set 2023' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_five_honorees_composite.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_innovation_four_states_composite.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2023_products/23rh_b.webp'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2023_products/23rh_c.webp'));
    });

    test('Synthetic Tracker Case 01 (26XH): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'sku': '26XH' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XH_image_2.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XH_image_3.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XH_image_1.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xh_image_3.jpg'));
    });

    test('Synthetic Tracker Case 02 (26XF): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'sku': '26XF' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XF_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XF_image_2.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_2.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_3.jpg'));
    });

    test('Synthetic Tracker Case 03 (26RG): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'sku': '26RG' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RG_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rg_b.webp'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RG_image_2.jpg'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RG_image_3.jpg'));
    });

    test('Synthetic Tracker Case 04 (26RH): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'sku': '26RH' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RH_image_1.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RH_image_2.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26RH_image_3.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Synthetic Tracker Case 05 (2023-AWQ-BESSIE): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2023', 'title': 'Bessie Coleman' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_bessie_coleman_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.png'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_bessie_coleman_reverse.png'));
    });

    test('Synthetic Tracker Case 06 (2023-AWQ-EDITH): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2023', 'title': 'Edith Kanakaole' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_edith_kanakaole_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.png'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_edith_kanakaole_reverse.png'));
    });

    test('Synthetic Tracker Case 07 (2023-AWQ-ELEANOR): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2023', 'title': 'Eleanor Roosevelt' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_eleanor_roosevelt_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.png'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_eleanor_roosevelt_reverse.png'));
    });

    test('Synthetic Tracker Case 08 (2023-AWQ-JOVITA): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2023', 'title': 'Jovita Idar' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_jovita_idar_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.png'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_jovita_idar_reverse.png'));
    });

    test('Synthetic Tracker Case 09 (2023-AWQ-MARIA): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2023', 'title': 'Maria Tallchief' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_maria_tallchief_reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_shared_obverse.png'));
      expect(pair.fallbackReverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/2023_series/2023_american_women_quarters_maria_tallchief_reverse.png'));
    });

    test('Synthetic Tracker Case 10 (ATB-2013-D): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2013', 'mint': 'D', 'title': 'White Mountain' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-d.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-white-mountain-new-hampshire-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Synthetic Tracker Case 11 (ATB-2010-P): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2010', 'mint': 'P', 'title': 'Mount Hood' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-mount-hood-oregon-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Synthetic Tracker Case 12 (ATB-2020-S): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2020', 'mint': 'S', 'title': 'Marsh-Billings-Rockefeller' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-marsh-billings-rockefeller-vermont-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Synthetic Tracker Case 13 (ATB-2020-S): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2020', 'mint': 'S', 'title': 'Tallgrass Prairie' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-tallgrass-prairie-kansas-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });

    test('Synthetic Tracker Case 14 (ATB-2020-S): resolves exact verified primary & fallback URLs', () {
      final doc = <String, dynamic>{ 'year': '2020', 'mint': 'S', 'title': 'Weir Farm' };
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg'));
      expect(pair.reverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-weir-farm-connecticut-uncirculated-reverse.jpg'));
      expect(pair.fallbackObverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg'));
      expect(pair.fallbackReverseUrl, isNull);
    });
  });

  group('NET-748 v5 Tests (1 through 21)', () {
    test('1. _normYear: 2026.0 and 2026 normalize to 2026 through resolveFromMap and extractSku', () {
      final doc1 = {'year': '2026.0', 'retailer_item_num': '26SQRP'};
      final doc2 = {'year': '2026', 'retailer_item_num': '26SQRP'};
      expect(CanonicalMintAssetService.extractSku(doc1), equals('26SQRP'));
      expect(CanonicalMintAssetService.extractSku(doc2), equals('26SQRP'));
      final pair1 = CanonicalMintAssetService.resolveFromMap(doc1);
      final pair2 = CanonicalMintAssetService.resolveFromMap(doc2);
      expect(pair1, isNotNull);
      expect(pair2, isNotNull);
      expect(pair1!.sku, equals('26SQRP'));
      expect(pair2!.sku, equals('26SQRP'));
    });

    test('2. ASE proof, 2026: extractSku returns 26EA', () {
      final doc = {'title': 'American Silver Eagle', 'Condition': 'Proof', 'year': '2026.0'};
      expect(CanonicalMintAssetService.extractSku(doc), equals('26EA'));
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.sku, equals('26EA'));
    });

    test('3. MF-v3-3: ASE ungraded 2026 W returns 26EA', () {
      final doc = {
        'year': '2026',
        'mint': 'W',
        'Program/Series': 'American Silver Eagle',
        'Condition': 'Ungraded',
      };
      expect(CanonicalMintAssetService.extractSku(doc), equals('26EA'));
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.sku, equals('26EA'));
    });

    test('4. Gold Eagle proof does not resolve to 26EA', () {
      final doc = {'title': 'American Gold Eagle', 'Condition': 'Proof', 'year': '2026'};
      expect(CanonicalMintAssetService.extractSku(doc), isNot(equals('26EA')));
    });

    test('5. retailer_item_num 26SQRP extracts 26SQRP and resolves to MASTER_SEMIQDJT_image_1.jpg', () {
      final doc = {'retailer_item_num': '26SQRP', 'year': '2026'};
      expect(CanonicalMintAssetService.extractSku(doc), equals('26SQRP'));
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, contains('MASTER_SEMIQDJT_image_1.jpg'));
    });

    test('6. Declaration quarter resolves to 2026-QTR-DECLARATION and not 2026-HALF', () {
      final pair = CanonicalMintAssetService.resolve(
        title: 'Declaration of Independence Quarter',
        denomination: '25c',
        year: '2026',
      );
      expect(pair, isNotNull);
      expect(pair!.sku, startsWith('2026-QTR-DECLARATION'));
      expect(pair.sku, isNot(startsWith('2026-HALF')));
    });

    test('7. Half with independence and denom 50c resolves to 2026-HALF', () {
      final pair = CanonicalMintAssetService.resolve(
        title: 'Declaration of Independence Half Dollar',
        denomination: '50c',
        year: '2026',
      );
      expect(pair, isNotNull);
      expect(pair!.sku, startsWith('2026-HALF'));
    });

    test('8. Semiquincentennial Quarter does not resolve to 2026-CENT', () {
      final pair = CanonicalMintAssetService.resolve(
        title: 'Semiquincentennial Quarter',
        denomination: '25c',
        year: '2026',
      );
      if (pair != null) {
        expect(pair.sku, isNot(startsWith('2026-CENT')));
      }
    });

    test('9. Semiquincentennial Dime resolves to 2026-DIME', () {
      final pair = CanonicalMintAssetService.resolve(
        title: 'Semiquincentennial Dime',
        denomination: '10c',
        year: '2026',
      );
      expect(pair, isNotNull);
      expect(pair!.sku, startsWith('2026-DIME'));
    });

    test('10. Gettysburg quarter resolves to 2026-QTR-GETTYSBURG_ADDRESS and not cent', () {
      final pair = CanonicalMintAssetService.resolve(
        title: 'Lincoln Gettysburg Address Quarter',
        denomination: '25c',
        year: '2026',
      );
      expect(pair, isNotNull);
      expect(pair!.sku, startsWith('2026-QTR-GETTYSBURG_ADDRESS'));
      expect(pair.sku, isNot(startsWith('2026-CENT')));
    });

    test('11. Cent P / D resolves to exact Penny Obverse Unc paths', () {
      final pairD = CanonicalMintAssetService.resolve(
        title: 'Semiquincentennial Cent',
        denomination: '1c',
        year: '2026',
        mintMark: 'D',
      );
      expect(pairD, isNotNull);
      expect(pairD!.obverseUrl, contains('highres_scrape/SemiQ-Penny-Obverse-Unc-D.jpg'));

      final pairP = CanonicalMintAssetService.resolve(
        title: 'Semiquincentennial Cent',
        denomination: '1c',
        year: '2026',
        mintMark: 'P',
      );
      expect(pairP, isNotNull);
      expect(pairP!.obverseUrl, contains('penny/SemiQ-Penny-Obverse-Unc-P.jpg'));
    });

    test('12. Nickel P/D resolves to bulk_programs/nickel paths', () {
      final pairD = CanonicalMintAssetService.resolve(
        title: 'Semiquincentennial Nickel',
        denomination: '5c',
        year: '2026',
        mintMark: 'D',
      );
      expect(pairD, isNotNull);
      expect(pairD!.obverseUrl, contains('bulk_programs/nickel/'));

      final pairP = CanonicalMintAssetService.resolve(
        title: 'Semiquincentennial Nickel',
        denomination: '5c',
        year: '2026',
        mintMark: 'P',
      );
      expect(pairP, isNotNull);
      expect(pairP!.obverseUrl, contains('bulk_programs/nickel/'));
    });

    test('13. Polly Cooper dollar resolves to polly cooper obverse path', () {
      final pair = CanonicalMintAssetService.resolve(
        title: 'Polly Cooper Native American Dollar',
        year: '2026',
      );
      expect(pair, isNotNull);
      expect(pair!.obverseUrl, contains('2026_native_american_dollar_polly_cooper_obverse.jpg'));
    });

    test('14. Revolutionary War and Constitution quarters resolve to their 2026_series paths', () {
      final pairRev = CanonicalMintAssetService.resolve(
        title: 'Revolutionary War Quarter',
        denomination: '25c',
        year: '2026',
      );
      expect(pairRev, isNotNull);
      expect(pairRev!.obverseUrl, contains('2026_series/'));
      expect(pairRev.sku, startsWith('2026-QTR-REVOLUTIONARY_WAR'));

      final pairConst = CanonicalMintAssetService.resolve(
        title: 'US Constitution Quarter',
        denomination: '25c',
        year: '2026',
      );
      expect(pairConst, isNotNull);
      expect(pairConst!.obverseUrl, contains('2026_series/'));
      expect(pairConst.sku, contains('CONSTITUTION'));
    });

    test('15. Mayflower D regression guard (F2-3) matches existing line 146', () {
      final doc = <String, dynamic>{
        'Year': '2026',
        'Mint Mark': 'D',
        'Denomination': 'Quarter Dollar (25C)',
        'Program/Series': 'United States Semiquincentennial (250th Anniversary)',
        'Theme/Subject': 'Mayflower Compact & Pilgrim Couple',
      };
      expect(CanonicalMintAssetService.hasUserUploadedPhotos(doc), isFalse);
      final pair = CanonicalMintAssetService.resolveFromMap(doc);
      expect(pair, isNotNull);
      expect(pair!.sku, equals('2026-MAYFLOWER-D'));
      expect(pair.obverseUrl, equals('https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg'));
    });

    test('16. User-photo doc (MF-B) with a 2026 cent title resolves to null', () {
      final doc = <String, dynamic>{
        'year': '2026',
        'title': 'Semiquincentennial Cent',
        'Personal Notes': 'User photo taken via microscope',
      };
      expect(CanonicalMintAssetService.resolveFromMap(doc), isNull);
    });

    test('17. kFallbackUsMintSkus has exactly the 11 SKUs in 4.1 with sku and name', () {
      const expectedSkus = {
        '26EA', '26XE', '26XL', '26XH', '26XF', '26GC', '26SQRP', '26RG', '23RG', '26RH', '23RH',
      };
      expect(kFallbackUsMintSkus.length, equals(11));
      expect(kFallbackUsMintSkus.keys.toSet(), equals(expectedSkus));
      for (final sku in expectedSkus) {
        final entry = kFallbackUsMintSkus[sku];
        expect(entry, isNotNull);
        expect(entry!['sku'], equals(sku));
        expect(entry['name'], isNotEmpty);
      }
    });

    test('18. AddCoinsHub.buildSkuCoinDoc includes sku and mint_product_id', () {
      final doc = AddCoinsHub.buildSkuCoinDoc({'year': '2026', 'denomination': '25c'}, '26SQRP');
      expect(doc['sku'], equals('26SQRP'));
      expect(doc['mint_product_id'], equals('26SQRP'));
      expect(doc['source'], equals('manual_sku'));
    });

    test('19. CoinImageService.fetchReferenceImages resolves canonical for 2026 and bypasses for 1962', () async {
      // 2026 Mayflower
      final res2026 = await CoinImageService.fetchReferenceImages(
        year: '2026',
        series: 'Mayflower',
        mint: 'D',
      );
      expect(res2026.sourceLabel, equals('Canonical Mint Asset'));

      // 1962 cent bypasses canonical hook
      final res1962 = await CoinImageService.fetchReferenceImages(
        year: '1962',
        denomination: '1c',
        mint: 'D',
      );
      expect(res1962.sourceLabel, isNot(equals('Canonical Mint Asset')));
    });

    test('20. MF-v3-2: resolve infers SKU from title/year alone when no SKU is passed', () {
      final morgan = CanonicalMintAssetService.resolve(
        title: 'Morgan Dollar Enhanced Uncirculated',
        year: '2026',
      );
      expect(morgan, isNotNull);
      expect(morgan!.sku, equals('26XE'));

      final peace = CanonicalMintAssetService.resolve(
        title: 'Peace Dollar Uncirculated',
        year: '2026',
      );
      expect(peace, isNotNull);
      expect(peace!.sku, equals('26XH'));

      final ase = CanonicalMintAssetService.resolve(
        title: 'American Silver Eagle',
        year: '2026',
      );
      expect(ase, isNotNull);
      expect(ase!.sku, equals('26EA'));

      final sqrp = CanonicalMintAssetService.resolve(
        title: 'Trump Semiquincentennial President Quarter',
        year: '2026',
      );
      expect(sqrp, isNotNull);
      expect(sqrp!.sku, equals('26SQRP'));

      final setItem = CanonicalMintAssetService.resolve(
        title: 'Silver Proof Set',
        year: '2026',
      );
      expect(setItem, isNotNull);
      expect(setItem!.sku, equals('26RH'));
    });

    test('21. v5 case guard (SAG MF-1): case-insensitive folding matches identical assets', () {
      // Repeat Test 2 (ALL-CAPS ASE)
      final doc2 = {'title': 'AMERICAN SILVER EAGLE', 'Condition': 'PROOF', 'year': '2026.0'};
      expect(CanonicalMintAssetService.extractSku(doc2), equals('26EA'));
      final pair2 = CanonicalMintAssetService.resolveFromMap(doc2);
      expect(pair2, isNotNull);
      expect(pair2!.sku, equals('26EA'));

      // Repeat Test 6 (Mixed case Declaration Quarter)
      final pair6 = CanonicalMintAssetService.resolve(
        title: 'Declaration Of Independence QUARTER',
        denomination: '25c',
        year: '2026',
      );
      expect(pair6, isNotNull);
      expect(pair6!.sku, startsWith('2026-QTR-DECLARATION'));

      // Repeat Test 10 (ALL-CAPS Gettysburg Quarter)
      final pair10 = CanonicalMintAssetService.resolve(
        title: 'LINCOLN GETTYSBURG ADDRESS QUARTER',
        denomination: '25C',
        year: '2026',
      );
      expect(pair10, isNotNull);
      expect(pair10!.sku, startsWith('2026-QTR-GETTYSBURG_ADDRESS'));

      // Repeat Test 13 (lowercase polly cooper)
      final pair13 = CanonicalMintAssetService.resolve(
        title: 'polly cooper native american dollar',
        year: '2026',
      );
      expect(pair13, isNotNull);
      expect(pair13!.obverseUrl, contains('2026_native_american_dollar_polly_cooper_obverse.jpg'));

      // Repeat Test 11 with lowercase mint 'd'
      final pair11 = CanonicalMintAssetService.resolve(
        title: 'SEMIQUINCENTENNIAL CENT',
        denomination: '1c',
        year: '2026',
        mintMark: 'd',
      );
      expect(pair11, isNotNull);
      expect(pair11!.obverseUrl, contains('highres_scrape/SemiQ-Penny-Obverse-Unc-D.jpg'));
    });
  });
}
