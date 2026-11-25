import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_ai/utils/catalog_image_guard.dart';

// 1x1 transparent PNG bytes so Image.network succeeds offline in tests.
const List<int> _kTransparentPng = <int>[
  0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
  0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
  0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
  0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
  0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49,
  0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82,
];

class _OfflinePngHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return _OfflinePngHttpClient();
  }
}

class _OfflinePngHttpClient implements HttpClient {
  @override
  bool autoUncompress = true;

  @override
  Duration? connectionTimeout;

  @override
  Duration idleTimeout = const Duration(seconds: 15);

  @override
  int? maxConnectionsPerHost;

  @override
  String? userAgent;

  @override
  void addCredentials(
    Uri url,
    String realm,
    HttpClientCredentials credentials,
  ) {}

  @override
  void addProxyCredentials(
    String host,
    int port,
    String realm,
    HttpClientCredentials credentials,
  ) {}

  @override
  set authenticate(
    Future<bool> Function(Uri url, String scheme, String? realm)? f,
  ) {}

  @override
  set authenticateProxy(
    Future<bool> Function(
      String host,
      int port,
      String scheme,
      String? realm,
    )? f,
  ) {}

  @override
  set badCertificateCallback(
    bool Function(X509Certificate cert, String host, int port)? callback,
  ) {}

  @override
  set connectionFactory(
    Future<ConnectionTask<Socket>> Function(
      Uri url,
      String? proxyHost,
      int? proxyPort,
    )? f,
  ) {}

  @override
  set findProxy(String Function(Uri url)? f) {}

  @override
  set keyLog(Function(String line)? callback) {}

  @override
  void close({bool force = false}) {}

  @override
  Future<HttpClientRequest> getUrl(Uri url) async =>
      _OfflinePngHttpRequest(url);

  @override
  Future<HttpClientRequest> openUrl(String method, Uri url) async =>
      _OfflinePngHttpRequest(url);

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _OfflinePngHttpRequest implements HttpClientRequest {
  @override
  final Uri uri;

  @override
  final HttpHeaders headers = _OfflineHeaders();

  @override
  Encoding encoding = utf8;

  _OfflinePngHttpRequest(this.uri);

  @override
  Future<HttpClientResponse> close() async => _OfflinePngHttpResponse();

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _OfflineHeaders implements HttpHeaders {
  @override
  dynamic noSuchMethod(Invocation invocation) => null;
}

class _OfflinePngHttpResponse extends Stream<List<int>>
    implements HttpClientResponse {
  @override
  int get statusCode => HttpStatus.ok;

  @override
  int get contentLength => _kTransparentPng.length;

  @override
  HttpClientResponseCompressionState get compressionState =>
      HttpClientResponseCompressionState.notCompressed;

  @override
  final HttpHeaders headers = _OfflineHeaders();

  @override
  StreamSubscription<List<int>> listen(
    void Function(List<int> event)? onData, {
    Function? onError,
    void Function()? onDone,
    bool? cancelOnError,
  }) {
    return Stream<List<int>>.fromIterable(<List<int>>[_kTransparentPng]).listen(
      onData,
      onError: onError,
      onDone: onDone,
      cancelOnError: cancelOnError,
    );
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// Minimal RFC-4180 CSV parser handling quoted commas, doubled quotes, and newlines.
List<Map<String, String>> _parseCsvRows(String content) {
  final rows = <List<String>>[];
  var currentRow = <String>[];
  final field = StringBuffer();
  var inQuotes = false;

  for (int i = 0; i < content.length; i++) {
    final ch = content[i];
    if (inQuotes) {
      if (ch == '"') {
        if (i + 1 < content.length && content[i + 1] == '"') {
          field.write('"');
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        field.write(ch);
      }
    } else {
      if (ch == '"') {
        inQuotes = true;
      } else if (ch == ',') {
        currentRow.add(field.toString());
        field.clear();
      } else if (ch == '\r') {
        continue;
      } else if (ch == '\n') {
        currentRow.add(field.toString());
        field.clear();
        if (currentRow.any((v) => v.isNotEmpty)) {
          rows.add(currentRow);
        }
        currentRow = <String>[];
      } else {
        field.write(ch);
      }
    }
  }
  if (field.isNotEmpty || currentRow.isNotEmpty) {
    currentRow.add(field.toString());
    if (currentRow.any((v) => v.isNotEmpty)) {
      rows.add(currentRow);
    }
  }
  if (rows.isEmpty) return <Map<String, String>>[];
  final headers = rows.first;
  return rows.skip(1).map((vals) {
    final map = <String, String>{};
    for (int i = 0; i < headers.length; i++) {
      map[headers[i]] = i < vals.length ? vals[i] : '';
    }
    return map;
  }).toList();
}

// m2: "copy" and "path" are broad words; a real future credit that trips them
// needs a reviewed exception, never a silent removal from this list.
final Map<String, RegExp> _p10ForbiddenPatterns = <String, RegExp>{
  'this pass': RegExp(r'this pass', caseSensitive: false),
  'path': RegExp(r'path', caseSensitive: false),
  're-pointed': RegExp(r're-pointed', caseSensitive: false),
  'copy': RegExp(r'copy', caseSensitive: false),
  'CanonicalMintAssetService': RegExp(
    r'CanonicalMintAssetService',
    caseSensitive: false,
  ),
  'coin_image_index': RegExp(r'coin_image_index', caseSensitive: false),
  '/workspace': RegExp(r'/workspace', caseSensitive: false),
  'gs://': RegExp(r'gs://', caseSensitive: false),
  'numista-reference-library': RegExp(
    r'numista-reference-library',
    caseSensitive: false,
  ),
  'us_mint_coin_images': RegExp(r'us_mint_coin_images', caseSensitive: false),
  'No copy': RegExp(r'No copy', caseSensitive: false),
  'service_class': RegExp(r'\b[A-Z][A-Za-z0-9]+Service\b'),
  'storage.googleapis.com': RegExp(
    r'storage\.googleapis\.com',
    caseSensitive: false,
  ),
  'raw_bool': RegExp(r'\b(?:true|false)\b', caseSensitive: false),
  'nac_or_id': RegExp(r'(?:NAC1\.|\bgsid\b)', caseSensitive: false),
  'null_or_None': RegExp(r'\b(?:null|None)\b'),
};

List<String> _findP10Matches(String text) {
  final hits = <String>[];
  _p10ForbiddenPatterns.forEach((name, pattern) {
    if (pattern.hasMatch(text)) {
      hits.add(name);
    }
  });
  return hits;
}

Map<String, dynamic> _attachManifestRowToCatalogItem(
  Map<String, dynamic> baseItem,
  Map<String, String> row,
) {
  final copy = Map<String, dynamic>.from(baseItem);
  final obvObj = <String, dynamic>{
    'url': row['obverse_public_url'] ?? '',
    'side': 'obverse',
    'unique_side': row['obverse_unique_side'] == 'Y',
    'license': row['obverse_license'] ?? '',
    'credit': row['obverse_credit'] ?? '',
    'source': row['obverse_credit'] ?? '',
    'source_url': row['obverse_source_url'] ?? '',
  };
  final revObj = <String, dynamic>{
    'url': row['reverse_public_url'] ?? '',
    'side': 'reverse',
    'unique_side': row['reverse_unique_side'] == 'Y',
    'license': row['reverse_license'] ?? '',
    'credit': row['reverse_credit'] ?? '',
    'source': row['reverse_credit'] ?? '',
    'source_url': row['reverse_source_url'] ?? '',
  };
  if (row['obverse_target_field'] == 'primary_image') {
    copy['primary_image'] = obvObj;
  } else {
    copy['type_image'] = obvObj;
    copy['primary_image'] = null;
  }
  copy['extra_images'] = <Map<String, dynamic>>[revObj];
  return copy;
}

void main() {
  final HttpOverrides? originalOverrides = HttpOverrides.current;

  setUpAll(() {
    HttpOverrides.global = _OfflinePngHttpOverrides();
  });

  tearDownAll(() {
    HttpOverrides.global = originalOverrides;
  });

  group('CR3 P5 URL & Source URL Negatives (Dart)', () {
    test('isApprovedCatalogImageUrl rejects all P5 negatives including signed/query/fragment/%3F', () {
      const approved = <String>[
        'https://storage.googleapis.com/us_mint_coin_images/2026_quarter_obv.jpg',
        'https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/1999_nj_reverse.jpg',
        'assets/catalog/images/morgan_1921.jpg',
      ];
      for (final u in approved) {
        expect(isApprovedCatalogImageUrl(u), isTrue, reason: 'Should accept $u');
      }

      const rejected = <String>[
        // Lookalike buckets
        'https://storage.googleapis.com/numista-reference-library-evil/coin.jpg',
        'https://storage.googleapis.com/us_mint_coin_images-x/coin.jpg',
        // Userinfo @ in both forms + bare @
        'https://user@storage.googleapis.com/us_mint_coin_images/coin.jpg',
        'https://user:pass@storage.googleapis.com/us_mint_coin_images/coin.jpg',
        'https://@storage.googleapis.com/us_mint_coin_images/coin.jpg',
        // Host prefix/suffix and firebasestorage
        'https://evil.storage.googleapis.com/us_mint_coin_images/coin.jpg',
        'https://storage.googleapis.com.evil.com/us_mint_coin_images/coin.jpg',
        'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fu1%2Fphoto.jpg?alt=media',
        // Ports including :443
        'https://storage.googleapis.com:443/us_mint_coin_images/coin.jpg',
        'https://storage.googleapis.com:8443/us_mint_coin_images/coin.jpg',
        // http://
        'http://storage.googleapis.com/us_mint_coin_images/coin.jpg',
        // Raw/encoded traversal & backslashes
        'https://storage.googleapis.com/us_mint_coin_images/a/../b.jpg',
        'https://storage.googleapis.com/us_mint_coin_images/./b.jpg',
        'https://storage.googleapis.com/us_mint_coin_images/%2e%2e/b.jpg',
        'https://storage.googleapis.com/us_mint_coin_images/a%2fb.jpg',
        'https://storage.googleapis.com/us_mint_coin_images/a%5cb.jpg',
        r'https://storage.googleapis.com/us_mint_coin_images\b.jpg',
        // numista-public & unpromoted uploads-studio
        'https://storage.googleapis.com/numista-public/coin.jpg',
        'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/u1/orig.jpg',
        'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/coin.jpg',
        'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference',
        // Wikimedia, Met, ANS, Greysheet, gsid
        'https://upload.wikimedia.org/wikipedia/commons/6/69/Coin.jpg',
        'https://images.metmuseum.org/CRDImages/an/web-large/coin.jpg',
        'https://numismatics.org/collectionimages/1950/coin.jpg',
        'https://www.greysheet.com/images/gsid/12345.jpg',
        'https://cdn.greysheet.com/gsid/12345.jpg',
        // Signed, query, trailing ?, fragment, encoded %3F and %23 (D2, N2)
        'https://storage.googleapis.com/us_mint_coin_images/coin.jpg?X-Goog-Signature=deadbeef',
        'https://storage.googleapis.com/numista-reference-library/coin.jpg?GoogleAccessId=svc&Expires=99999',
        'https://storage.googleapis.com/us_mint_coin_images/coin.jpg?alt=media',
        'https://storage.googleapis.com/us_mint_coin_images/coin.jpg?',
        'https://storage.googleapis.com/us_mint_coin_images/coin.jpg#section',
        'https://storage.googleapis.com/us_mint_coin_images/coin.jpg#',
        'https://storage.googleapis.com/us_mint_coin_images/coin.jpg%3Falt=media',
        'https://storage.googleapis.com/us_mint_coin_images/coin.jpg%3falt=media',
        'https://storage.googleapis.com/us_mint_coin_images/coin.jpg%23fragment',
      ];
      for (final u in rejected) {
        expect(isApprovedCatalogImageUrl(u), isFalse, reason: 'Should reject $u');
      }
    });

    test('isApprovedSourceUrl accepts exact 3 hosts (https, no userinfo/port) and rejects P5 negatives', () {
      expect(isApprovedSourceUrl('https://usmint.gov/news/image-library'), isTrue);
      expect(isApprovedSourceUrl('https://www.usmint.gov/news/image-library/circulating'), isTrue);
      expect(isApprovedSourceUrl('https://commons.wikimedia.org/wiki/File:Fugio_cent.jpg'), isTrue);

      const badSources = <String?>[
        null,
        '',
        'http://www.usmint.gov/news/image-library',
        'http://usmint.gov/news/image-library',
        'http://commons.wikimedia.org/wiki/File:Test.jpg',
        'https://user@www.usmint.gov/news/image-library',
        'https://user:pass@commons.wikimedia.org/wiki/File:Test.jpg',
        'https://@usmint.gov/news/image-library',
        'https://www.usmint.gov:443/news/image-library',
        'https://commons.wikimedia.org:8443/wiki/File:Test.jpg',
        'https://evil.usmint.gov/news/image-library',
        'https://usmint.gov.evil.com/news/image-library',
        'https://commons.wikimedia.org.evil.com/wiki/File:Test.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/test.jpg',
        'https://si.edu/collections/test',
        'https://www.greysheet.com/gsid/123',
      ];
      for (final s in badSources) {
        expect(isApprovedSourceUrl(s), isFalse, reason: 'Should reject source_url $s');
      }
    });
  });

  group('CR3 Part 3 & Part 5 Widget Tests', () {
    testWidgets('1. Credit caption shows on card and on each detail side (credit ?? source fallback)', (WidgetTester tester) async {
      final item = <String, dynamic>{
        'nac_code': 'NAC1.CN.US.25C.QUARTER.2026.P.TEST.1',
        'name': '2026-P Test Quarter',
        'year': 2026,
        'denomination': 'Quarter',
        'type': 'coin',
        'primary_image': <String, dynamic>{
          'url': 'https://storage.googleapis.com/numista-reference-library/test/obv.jpg',
          'side': 'obverse',
          'unique_side': true,
          'credit': 'Image: United States Mint',
          'source': 'Ignored Source When Credit Present',
          'source_url': 'https://www.usmint.gov/news/image-library/circulating',
        },
        'extra_images': <Map<String, dynamic>>[
          <String, dynamic>{
            'url': 'https://storage.googleapis.com/us_mint_coin_images/test/rev.jpg',
            'side': 'reverse',
            'unique_side': true,
            'source': 'Photograph by Bobby131313, via Wikimedia Commons. Not a United States Mint photograph.',
            'source_url': 'https://commons.wikimedia.org/wiki/File:Test.jpg',
          },
        ],
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: Column(
                children: [
                  SizedBox(
                    width: 340,
                    height: 540,
                    child: CatalogItemCard(item: item, onTap: () {}),
                  ),
                  CatalogDetailImagesView(item: item),
                ],
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Credit shows on card AND on detail obverse; source fallback shows on detail reverse
      expect(find.text('Image: United States Mint'), findsNWidgets(2));
      expect(find.text('Ignored Source When Credit Present'), findsNothing);
      expect(
        find.text('Photograph by Bobby131313, via Wikimedia Commons. Not a United States Mint photograph.'),
        findsOneWidget,
      );

      // Default caption stays only when both credit and source are missing
      final defaultFallbackItem = <String, dynamic>{
        'name': 'Fallback Coin',
        'primary_image': <String, dynamic>{
          'url': 'https://storage.googleapis.com/us_mint_coin_images/fallback.jpg',
          'unique_side': true,
        },
      };
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: CatalogDetailImagesView(item: defaultFallbackItem)),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Numista.Ai reference photo'), findsOneWidget);

      // CM-1: Planted internal provenance caption fails P10
      expect(
        _findP10Matches('re-pointed in this pass from /workspace/coin_image_index'),
        containsAll(<String>['re-pointed', 'this pass', '/workspace', 'coin_image_index']),
      );
    });

    testWidgets('2. Representative label shows together with the credit (not replacing it)', (WidgetTester tester) async {
      final item = <String, dynamic>{
        'name': '1793-P Flowing Hair Cent',
        'year': 1793,
        'denomination': '1 Cent',
        'type': 'coin',
        'primary_image': null,
        'type_image': <String, dynamic>{
          'url': 'https://storage.googleapis.com/numista-reference-library/nnc/1793_obv.jpg',
          'side': 'obverse',
          'unique_side': false,
          'credit': 'National Numismatic Collection, National Museum of American History (photograph by Jaclyn Nash)',
          'source': 'National Numismatic Collection, National Museum of American History (photograph by Jaclyn Nash)',
          'source_url': 'https://commons.wikimedia.org/wiki/File:NNC.jpg',
        },
        'extra_images': <Map<String, dynamic>>[
          <String, dynamic>{
            'url': 'https://storage.googleapis.com/numista-reference-library/nnc/1793_rev.jpg',
            'side': 'reverse',
            'unique_side': false,
            'credit': 'National Numismatic Collection, National Museum of American History',
            'source': 'National Numismatic Collection, National Museum of American History',
            'source_url': 'https://commons.wikimedia.org/wiki/File:NNC_rev.jpg',
          },
        ],
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: Column(
                children: [
                  SizedBox(
                    width: 340,
                    height: 540,
                    child: CatalogItemCard(item: item, onTap: () {}),
                  ),
                  CatalogDetailImagesView(item: item),
                ],
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Credit appears on both card and detail alongside Representative label
      expect(
        find.text('National Numismatic Collection, National Museum of American History (photograph by Jaclyn Nash)'),
        findsNWidgets(2),
      );
      expect(
        find.text('National Numismatic Collection, National Museum of American History'),
        findsOneWidget,
      );
      // 1 on card + 2 on detail sides (both obverse & reverse have unique_side=false)
      expect(find.text(kRepresentativePhotoLabel), findsNWidgets(3));
    });

    testWidgets('3. Rejected host shows "No photo yet"', (WidgetTester tester) async {
      final item = <String, dynamic>{
        'name': 'Rejected Host Coin',
        'year': 2020,
        'denomination': 'Quarter',
        'type': 'coin',
        'primary_image': <String, dynamic>{
          'url': 'https://upload.wikimedia.org/wikipedia/commons/6/69/BadHost.jpg',
          'credit': 'Wikimedia',
        },
        'type_image': <String, dynamic>{
          'url': 'https://www.greysheet.com/gsid/123.jpg',
          'credit': 'Greysheet',
        },
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Column(
              children: [
                Expanded(child: CatalogItemCard(item: item, onTap: () {})),
                CatalogDetailImagesView(item: item),
              ],
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('No photo yet'), findsNWidgets(2));
      expect(find.byType(Image), findsNothing);
    });

    testWidgets('4. Bad or local-only primary with good type_image shows the type_image', (WidgetTester tester) async {
      final typeUrl = 'https://storage.googleapis.com/numista-reference-library/type_good.jpg';
      final itemWithLocalOnlyPrimary = <String, dynamic>{
        'name': 'Local Primary Coin',
        'year': 1999,
        'denomination': 'Quarter',
        'type': 'coin',
        'primary_image': <String, dynamic>{
          'file': 'reference_images/local_only.jpg',
          'source': 'Numista.Ai reference photo',
        },
        'type_image': <String, dynamic>{
          'url': typeUrl,
          'unique_side': false,
          'credit': 'Image: United States Mint',
          'source_url': 'https://www.usmint.gov/news/image-library',
        },
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Column(
              children: [
                Expanded(child: CatalogItemCard(item: itemWithLocalOnlyPrimary, onTap: () {})),
                CatalogDetailImagesView(item: itemWithLocalOnlyPrimary),
              ],
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final cardImage = tester.widget<Image>(find.byKey(const Key('catalog_card_image')));
      final detailImage = tester.widget<Image>(find.byKey(const Key('catalog_detail_image_0')));
      expect((cardImage.image as NetworkImage).url, typeUrl);
      expect((detailImage.image as NetworkImage).url, typeUrl);
      expect(find.text(kRepresentativePhotoLabel), findsNWidgets(2));
      expect(find.text('Image: United States Mint'), findsNWidgets(2));
    });

    testWidgets('5. thumb_url is used on the card and full_url in the detail view', (WidgetTester tester) async {
      const thumbUrl = 'https://storage.googleapis.com/numista-reference-library/thumbs/coin_thumb.jpg';
      const fullUrl = 'https://storage.googleapis.com/numista-reference-library/full/coin_full.jpg';
      const fallbackUrl = 'https://storage.googleapis.com/numista-reference-library/std/coin.jpg';

      final item = <String, dynamic>{
        'name': '2026 Thumb Full Coin',
        'year': 2026,
        'denomination': 'Quarter',
        'type': 'coin',
        'primary_image': <String, dynamic>{
          'url': fallbackUrl,
          'thumb_url': thumbUrl,
          'full_url': fullUrl,
          'unique_side': true,
          'credit': 'Image: United States Mint',
          'source_url': 'https://usmint.gov/news/image-library',
        },
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Column(
              children: [
                Expanded(child: CatalogItemCard(item: item, onTap: () {})),
                CatalogDetailImagesView(item: item),
              ],
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final cardImage = tester.widget<Image>(find.byKey(const Key('catalog_card_image')));
      final detailImage = tester.widget<Image>(find.byKey(const Key('catalog_detail_image_0')));
      expect((cardImage.image as NetworkImage).url, thumbUrl);
      expect((detailImage.image as NetworkImage).url, fullUrl);
    });

    testWidgets('6. Reverse comes after obverse and source_url is clickable only when allow-listed', (WidgetTester tester) async {
      const obvUrl = 'https://storage.googleapis.com/us_mint_coin_images/obv_full.jpg';
      const revUrl = 'https://storage.googleapis.com/us_mint_coin_images/rev_full.jpg';

      final item = <String, dynamic>{
        'name': 'Obverse & Reverse Detail Order Coin',
        'primary_image': <String, dynamic>{
          'url': obvUrl,
          'side': 'obverse',
          'unique_side': true,
          'credit': 'Image: United States Mint',
          'source_url': 'https://www.usmint.gov/news/image-library/50-state-quarters-program',
        },
        'extra_images': <Map<String, dynamic>>[
          <String, dynamic>{
            'url': 'https://storage.googleapis.com/us_mint_coin_images/ignored_obv_extra.jpg',
            'side': 'obverse',
            'credit': 'Should Not Show As Reverse',
          },
          <String, dynamic>{
            'url': revUrl,
            'side': 'reverse',
            'unique_side': true,
            'credit': 'Non-Allowlisted Plain Caption',
            'source_url': 'http://www.usmint.gov/insecure-not-clickable',
          },
        ],
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(child: CatalogDetailImagesView(item: item)),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final img0 = tester.widget<Image>(find.byKey(const Key('catalog_detail_image_0')));
      final img1 = tester.widget<Image>(find.byKey(const Key('catalog_detail_image_1')));
      expect((img0.image as NetworkImage).url, obvUrl);
      expect((img1.image as NetworkImage).url, revUrl);
      expect(find.text('Should Not Show As Reverse'), findsNothing);

      // Vertical order check: image_0 is strictly above image_1
      final dy0 = tester.getTopLeft(find.byKey(const Key('catalog_detail_image_0'))).dy;
      final dy1 = tester.getTopLeft(find.byKey(const Key('catalog_detail_image_1'))).dy;
      expect(dy0, lessThan(dy1));

      // Approved https www.usmint.gov link renders as clickable InkWell; http:// renders as plain Text
      expect(find.byKey(const Key('catalog_detail_source_link_0')), findsOneWidget);
      expect(find.byKey(const Key('catalog_detail_source_link_1')), findsNothing);
      expect(find.byKey(const Key('catalog_detail_source_plain_1')), findsOneWidget);
    });
  });

  group('CR3 Offline Rendered P10 Scan (All Live Rows + attach_manifest_v4)', () {
    testWidgets('scans all 3,202 live rows plus attach_manifest_v4 rows offline with zero forbidden hits', (WidgetTester tester) async {
      final jsonStr = await tester.runAsync<String>(() async {
        return rootBundle.loadString('assets/catalog/catalog_public_v1.json');
      });
      expect(jsonStr, isNotNull);
      final List<dynamic> rawList = json.decode(jsonStr!) as List<dynamic>;
      expect(rawList.length, 3202);

      final allItems = rawList
          .map((e) => Map<String, dynamic>.from(e as Map))
          .toList();

      // Check all 3,202 live rows (rendered card/detail fallback or approved captions + representative labels + raw captions)
      int liveCaptionChecks = 0;
      final liveHits = <String>[];
      for (final item in allItems) {
        final primaryImg = item['primary_image'] as Map?;
        final typeImg = item['type_image'] as Map?;
        final cardImg = resolveCatalogCardImage(item);
        if (cardImg != null) {
          final cap = resolveCatalogImageCaption(cardImg.imageMap);
          liveCaptionChecks++;
          final m = _findP10Matches(cap);
          if (m.isNotEmpty) liveHits.add('${item['nac_code']}:card:$m');
          if (isRepresentativeCatalogImage(cardImg)) {
            liveCaptionChecks++;
            final rm = _findP10Matches(kRepresentativePhotoLabel);
            if (rm.isNotEmpty) liveHits.add('${item['nac_code']}:cardRep:$rm');
          }
        } else {
          // Live rows without approved GCS URLs render "No photo yet" (and legacy local type label when applicable)
          liveCaptionChecks++;
          final nm = _findP10Matches('No photo yet');
          if (nm.isNotEmpty) liveHits.add('${item['nac_code']}:cardNoPhoto:$nm');
          if (primaryImg == null &&
              typeImg != null &&
              typeImg['url'] == null &&
              typeImg['thumb_url'] == null &&
              typeImg['file'] is String) {
            liveCaptionChecks++;
            final lm = _findP10Matches('type photo (date may differ)');
            if (lm.isNotEmpty) liveHits.add('${item['nac_code']}:legacyType:$lm');
          }
        }
        final detImgs = resolveCatalogDetailImages(item);
        if (detImgs.isEmpty) {
          liveCaptionChecks++;
          final dm = _findP10Matches('No photo yet');
          if (dm.isNotEmpty) liveHits.add('${item['nac_code']}:detailNoPhoto:$dm');
        } else {
          for (final detImg in detImgs) {
            final cap = resolveCatalogImageCaption(detImg.imageMap);
            liveCaptionChecks++;
            final m = _findP10Matches(cap);
            if (m.isNotEmpty) liveHits.add('${item['nac_code']}:detail(${detImg.side}):$m');
            if (isRepresentativeCatalogImage(detImg)) {
              liveCaptionChecks++;
              final rm = _findP10Matches(kRepresentativePhotoLabel);
              if (rm.isNotEmpty) liveHits.add('${item['nac_code']}:detailRep:$rm');
            }
          }
        }
        // Also scan any raw credit/source strings stored on live image dicts
        for (final rawField in <dynamic>[primaryImg, typeImg, ...(item['extra_images'] as List? ?? const <dynamic>[])]) {
          if (rawField is Map) {
            final cap = resolveCatalogImageCaption(rawField);
            liveCaptionChecks++;
            final rm = _findP10Matches(cap);
            if (rm.isNotEmpty) liveHits.add('${item['nac_code']}:rawCaption:$rm');
          }
        }
      }
      expect(liveCaptionChecks, greaterThan(0));
      expect(liveHits, isEmpty, reason: 'Live rows tripped P10: $liveHits');

      // Attach attach_manifest_v4 if CR3_MANIFEST_V4_PATH is set, else CI synthetic 4-class fixture
      final envManifestPath = Platform.environment['CR3_MANIFEST_V4_PATH'];
      final List<Map<String, String>> manifestRows;
      final bool usedRealManifest;
      if (envManifestPath != null && envManifestPath.isNotEmpty && File(envManifestPath).existsSync()) {
        usedRealManifest = true;
        manifestRows = _parseCsvRows(File(envManifestPath).readAsStringSync());
        expect(manifestRows.length, 487);
      } else {
        usedRealManifest = false;
        manifestRows = <Map<String, String>>[
          <String, String>{
            'nac1': allItems.first['nac_code'] as String,
            'obverse_public_url': 'https://storage.googleapis.com/numista-reference-library/ci_mint_obv.jpg',
            'obverse_unique_side': 'Y',
            'obverse_license': 'Public domain (US government work, 17 U.S.C. \u00a7 105)',
            'obverse_credit': 'Image: United States Mint',
            'obverse_source_url': 'https://www.usmint.gov/news/image-library',
            'obverse_target_field': 'primary_image',
            'reverse_public_url': 'https://storage.googleapis.com/numista-reference-library/ci_nnc_rev.jpg',
            'reverse_unique_side': 'N',
            'reverse_license': 'Public domain (PD-US-SI; U.S. government / Smithsonian employee work, not Smithsonian Open Access CC0)',
            'reverse_credit': 'National Numismatic Collection, National Museum of American History (photograph by Jaclyn Nash)',
            'reverse_source_url': 'https://commons.wikimedia.org/wiki/File:Test.jpg',
            'obverse_license_class': 'US_MINT_PD',
            'reverse_license_class': 'PD-US-SI',
          },
          <String, String>{
            'nac1': allItems[1]['nac_code'] as String,
            'obverse_public_url': 'https://storage.googleapis.com/numista-reference-library/ci_fugio_obv.jpg',
            'obverse_unique_side': 'Y',
            'obverse_license': 'Public domain (Wikimedia Commons)',
            'obverse_credit': 'Unknown engraver (purportedly Benjamin Franklin); photograph via Wikimedia Commons, File:Fugio cent.jpg (original image coins.nd.edu).',
            'obverse_source_url': 'https://commons.wikimedia.org/wiki/File:Fugio_cent.jpg',
            'obverse_target_field': 'type_image',
            'reverse_public_url': 'https://storage.googleapis.com/numista-reference-library/ci_merc_rev.jpg',
            'reverse_unique_side': 'N',
            'reverse_license': "Public domain (Wikimedia Commons; photographer's own work). Credit the photographer.",
            'reverse_credit': 'Photograph by Bobby131313, via Wikimedia Commons. Not a United States Mint photograph.',
            'reverse_source_url': 'https://commons.wikimedia.org/wiki/File:TestOwn.jpg',
            'obverse_license_class': 'WIKIMEDIA_PD_CONFIRMED',
            'reverse_license_class': 'WIKIMEDIA_PD_OWN_WORK',
          },
        ];
      }

      final byNac = <String, Map<String, dynamic>>{
        for (final item in allItems)
          if (item['nac_code'] is String) item['nac_code'] as String: item,
      };

      int attachedCaptionChecks = 0;
      final attachedHits = <String>[];
      final sampleByClass = <String, Map<String, dynamic>>{};

      for (final r in manifestRows) {
        final nac = r['nac1'] ?? '';
        final baseItem = byNac[nac];
        expect(baseItem, isNotNull, reason: 'Missing NAC in live catalog: $nac');
        final attached = _attachManifestRowToCatalogItem(baseItem!, r);

        final cls = r['obverse_license_class'] ?? 'UNKNOWN';
        sampleByClass.putIfAbsent(cls, () => attached);
        final revCls = r['reverse_license_class'] ?? 'UNKNOWN';
        sampleByClass.putIfAbsent('REV:$revCls', () => attached);

        final cardImg = resolveCatalogCardImage(attached);
        expect(cardImg, isNotNull, reason: 'Attached card image failed guard for $nac');
        final cardCap = resolveCatalogImageCaption(cardImg!.imageMap);
        attachedCaptionChecks++;
        final cardM = _findP10Matches(cardCap);
        if (cardM.isNotEmpty) attachedHits.add('$nac:card:$cardM');
        if (isRepresentativeCatalogImage(cardImg)) {
          attachedCaptionChecks++;
          final repM = _findP10Matches(kRepresentativePhotoLabel);
          if (repM.isNotEmpty) attachedHits.add('$nac:cardRep:$repM');
        }

        final detailImgs = resolveCatalogDetailImages(attached);
        expect(detailImgs.length, greaterThanOrEqualTo(2), reason: 'Missing obverse/reverse detail image for $nac');
        for (final d in detailImgs) {
          final cap = resolveCatalogImageCaption(d.imageMap);
          attachedCaptionChecks++;
          final dm = _findP10Matches(cap);
          if (dm.isNotEmpty) attachedHits.add('$nac:detail(${d.side}):$dm');
          if (isRepresentativeCatalogImage(d)) {
            attachedCaptionChecks++;
            final drm = _findP10Matches(kRepresentativePhotoLabel);
            if (drm.isNotEmpty) attachedHits.add('$nac:detailRep(${d.side}):$drm');
          }
        }
      }
      expect(attachedHits, isEmpty, reason: 'Attached rows tripped P10: $attachedHits');

      // Pump representative cards & details into widget tree and scan ALL rendered Text widgets
      int widgetTextNodesScanned = 0;
      final widgetTextHits = <String>[];
      final sampleItems = sampleByClass.values.toList();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: Column(
                children: [
                  for (final sample in sampleItems) ...[
                    SizedBox(
                      width: 340,
                      height: 540,
                      child: CatalogItemCard(item: sample, onTap: () {}),
                    ),
                    CatalogDetailImagesView(item: sample),
                  ],
                ],
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      for (final w in find.byType(Text).evaluate()) {
        final textWidget = w.widget as Text;
        final s = textWidget.data ?? textWidget.textSpan?.toPlainText() ?? '';
        if (s.isEmpty) continue;
        widgetTextNodesScanned++;
        final m = _findP10Matches(s);
        if (m.isNotEmpty) {
          widgetTextHits.add('$s -> $m');
        }
      }
      expect(widgetTextHits, isEmpty, reason: 'Rendered Text widgets tripped P10: $widgetTextHits');

      final outReportPath = Platform.environment['CR3_P10_OUT_PATH'];
      if (outReportPath != null && outReportPath.isNotEmpty) {
        File(outReportPath).writeAsStringSync(
          const JsonEncoder.withIndent('  ').convert(<String, dynamic>{
            'used_real_manifest': usedRealManifest,
            'live_rows_checked': allItems.length,
            'live_caption_and_label_checks': liveCaptionChecks,
            'manifest_rows_checked': manifestRows.length,
            'attached_caption_and_label_checks': attachedCaptionChecks,
            'widget_text_nodes_scanned': widgetTextNodesScanned,
            'total_hits': 0,
          }),
        );
      }
    });
  });
}
