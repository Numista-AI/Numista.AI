# FAILFIX PLAN v1.7: Images & CSP Resolution (NET-780c)
**To:** Antigravity Desk, Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work / Catalog Day Team (`ba2bfdb2`)  
**Date:** 7 November 2026, 3:30 PM ET  
**Reference Batons:**  
- `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`  
- `BATON_NET-817_REVISE_780b-780c_v1.7_PER-COS-76_20261107-1305.md`  
- `RADIO_NET-825_TASKMASTER-to-AGCOS_BETA-RETEST-FIX-ORDER_20261107.md`  
- `RADIO_NET-828_GROKCOS-to-AGCOS_REVISE-817-v1.7_20261107.md`  
**Directives & Audit Scores:**  
- `GB CoS SCORE v1.6`: **Images 68 / 100 FAIL** (`COS_SCORE_NET-817_CARDS_IMAGES_v1.6_20261107.md`)  
- `PROTOCOL UPDATE: ARGON DROPPED`: Founder Eric typed YES. Review sequence is AG CoS Plan $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES.  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes/seeding).  
**Explicit Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all code and configurations.  
3. Execution strictly scoped to branch `p7-v8.9` (branch `dev` @ `b0b05808` lacks `canonical_mint_asset_service.dart`).  
4. Founder Eric's typed YES to this plan is strictly for code execution on `p7-v8.9` and preview channel deployment — it is NOT an approval for Firestore database writes, seeding, or security rules changes. Separate scoped Eric typed YES is required for any database writes.  
5. Zero deployments to live production `numista-vault.web.app` or `numista.ai` without prior Firebase Preview Channel sign-off and Eric's separate, explicit typed approval. Target is **p7-gate preview** (`preview-catalog`) only.  
6. **Alerts only, NEVER budget caps:** all spending caps (including $25 limit and hard $0.00 spend cap) are permanently eliminated per Eric's standing rule; alerts set at $20/mo.  
7. Zero AJ PII across all plans, logs, mocks, and code.  

---

## 1. Executive Summary & Itemized Must-Fix Closeout Table

Plan v1.7 systematically resolves all numbered blocking must-fixes from `COS_SCORE_NET-817_CARDS_IMAGES_v1.6_20261107.md` (Images 68/100 FAIL) and Beta Retest Fix Order `RADIO_NET-825` (Bundle B: B05N-7, B05N-10, B05N-12, B05N-15):

| Must-Fix # | CoS-76 / Images Must-Fix Description | Plan v1.7 Resolution & Grounding | Plan Section |
| :--- | :--- | :--- | :--- |
| **MF-1** | **Align Replacement Widget to Real `CoinImageService` & `CoinImageResult` API:** Plan v1.6 called non-existent `mintMark:`, `CoinImageResult.empty()`, and `.images.first.gcsUrl`. Align to real p7 signatures. | Grounded on p7 (@ `4d17ca5e`): calls real static method `CoinImageService.fetchReferenceImages(year:, mint:, denomination:, series:, subject:)` (passing `mint:`, not `mintMark:`). Consumes real `CoinImageResult` fields: `obverseUrl` and `reverseUrl` (no `images`, no `empty()`). Handles timeout with `.timeout(const Duration(seconds: 5), onTimeout: () => const CoinImageResult())`. Applies subject steal-guard policy. | §2.A, §3.1 |
| **MF-2** | **Ground Image Ownership Helper & Support Relative Same-Origin:** Plan v1.6 began with `if (!url.startsWith('https://')) return false;`, blocking relative `/` paths. Admit `*.firebasestorage.app` object hosts and preview hosts. Test identical shipped helper. | Shipped helper `isOwnedStorageUrl` checks `trimmed.startsWith('/') && !trimmed.startsWith('//')` FIRST, allowing relative same-origin paths. Enforces HTTPS on absolute URLs and admits verified bucket paths under `storage.googleapis.com` (`/numista-vault.firebasestorage.app/`, `/numista-ai-images/`, `/numista-reference-library/`, `/numista-catalog-assets/`, `/numista-uploads-studio-`, `/studio-9101802118-8c9a8-uploads/`), direct `*.firebasestorage.app` hosts, and preview channel hosts (`numista-vault.web.app`, `numista-vault.firebaseapp.com`, `numista.ai`, `*.web.app`). Both accepted and rejected URLs are tested against the exact shipped helper. | §2.B, §3.2, §6.2 |
| **MF-3** | **Substantive Offline Tests with Injectable Harness:** Plan v1.6 pumped naked `Image.network` and recomputed local bools without constructing `_CollectionCardImage`. Pump component with injectable boundaries, count calls, capture URLs, and assert negative fail-closed behavior. | Comprehensive offline test suite in `numista_mobile/test/widgets/collection_card_image_test.dart`. Constructs `CollectionCardImageHarness` (injectable testing seam for `_CollectionCardImage`): (1) counts `imageFetcher` invocations; (2) proves user-photo precedence (fetcher count = 0); (3) proves fail-closed placeholder on invalid/unowned user photo without network fetch (fetcher count = 0); (4) verifies bounded timeout fallback; (5) tests semantic `_RequestKey` refresh. | §3.1, §6.1 |
| **MF-4** | **Structural Anchors & RequestKey Cleanup:** Existing widget is `StatelessWidget` at 6356–6479 (not `StatefulWidget`). `_fetchInspectorSimilar` starts at 5252 (not 5250). `_RequestKey.fromData` must include full alias set and canonicalYear helper. | Anchored class replacement replaces `StatelessWidget` lines 6356–6479. Inspector loader span on p7 confirmed at lines 5252–5278. `_RequestKey.fromData` iterates camelCase, snake_case, and stored aliases matching `_extractUserPhoto` exactly, and extracts year via `CanonicalMintAssetService.canonicalYear(data)` so that empty direct `year` + populated `Year` triggers refresh. | §2.C, §3.1, §3.3 |
| **MF-5** | **Removal of Hard $0.00 Spend Cap:** Eliminate all spending caps per Eric's standing rule ("budget alerts only, never caps"). | **Hard $0.00 spend cap and $25 cap completely deleted.** Standing policy is budget alerts only, never automated shutoffs. Configured alert threshold: $20/month. Offline mocks used for all test validation. | §4 |
| **MF-6** | **Structural Deletions, Gates & Backups:** Coordinate single owner with NET-816; separate Eric YES for writes/rules; US-only scope; AI-image laptop+GCS backup gate; 3:00 AM AG stand-down; main locked; Stripe OFF. | Single deletion owner for Google/Kaggle is NET-816. Line 4410 `_onSearchEbay` is strictly PRESERVED with affiliate tags per B05N-18 and `RADIO_NET-825`. NET-817 cleanly removes inspector loader (`_fetchInspectorSimilar`, lines 5252–5278) and fields (lines 149–152). Explicit separate Eric typed YES required for Firestore writes and rules. US-only scope. Standing 3:00 AM ET stand-down. Main locked at `9f04550a`. Stripe OFF. Verified laptop + GCS backup gate for AI images before any migrations. | §4, §5 |
| **MF-7** | **Handoff & Mailbox Integrity:** Ensure exact copies of plans are mirrored across all 5 directories. | Verified physical mirroring of `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.7.md` across `docs/`, `BATONS/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`, and `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`. | §7 |

---

## 2. Verbatim Code Citations & CSP Perimeter

### A. Real API Signatures on Pinned `p7` (@ `4d17ca5e`)
In `numista_mobile/lib/services/coin_image_service.dart`:
```dart
490:  static Future<CoinImageResult> fetchReferenceImages({
491:    required String year,
492:    String? mint,
493:    String? denomination,
494:    String? series,
495:    String? subject,
496:  }) async {
```
And `CoinImageResult` class definition (lines 637–655):
```dart
637: class CoinImageResult {
638:   final String? obverseUrl;
639:   final String? reverseUrl;
640:   final String? attribution;
641:   final String? sourceLabel;
642:   final String? matchedKey;
643: 
644:   const CoinImageResult({
645:     this.obverseUrl,
646:     this.reverseUrl,
647:     this.attribution,
648:     this.sourceLabel,
649:     this.matchedKey,
650:   });
651: 
652:   bool get hasObverse => obverseUrl != null && obverseUrl!.isNotEmpty;
653:   bool get hasReverse => reverseUrl != null && reverseUrl!.isNotEmpty;
654:   bool get hasAny     => hasObverse || hasReverse;
655: }
```
`CoinImageResult` provides `const CoinImageResult()` and does NOT have `images` list or `.empty()`.
`fetchReferenceImages` expects `mint:`, not `mintMark:`.

### B. CSP Configuration in `numista_mobile/firebase.json` Line 276
```json
"img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com;"
```
Transport permission in CSP does not grant image ownership. Unapproved third-party hotlinks (e.g. `wikimedia.org`) trigger browser CSP violations and must be rejected before fetch.

### C. Anchored Existing `_CollectionCardImage` in `my_collection_screen.dart` Lines 6356–6479
```dart
6356: class _CollectionCardImage extends StatelessWidget {
6357:   final Map<String, dynamic> data;
6358:   const _CollectionCardImage({required this.data});
6359: 
6360:   static String _cleanUrl(dynamic val) {
...
6479: }
```

---

## 3. Targeted Class Implementation

### 3.1 Anchored Whole-Class Replacement
In `numista_mobile/lib/screens/my_collection_screen.dart` replacing lines 6356–6479:
```dart
/// Type signature for injectable reference image fetcher
typedef ReferenceImageFetcher = Future<CoinImageResult> Function({
  required String year,
  String? mint,
  String? denomination,
  String? series,
  String? subject,
});

/// Robust image component for collection card grid.
/// Displays personal scan if available, otherwise queries CoinImageService for reference image.
class _CollectionCardImage extends StatefulWidget {
  final Map<String, dynamic> data;
  final ReferenceImageFetcher? imageFetcher;

  const _CollectionCardImage({
    Key? key,
    required this.data,
    this.imageFetcher,
  }) : super(key: key);

  @override
  State<_CollectionCardImage> createState() => _CollectionCardImageState();
}

class _CollectionCardImageState extends State<_CollectionCardImage> {
  Future<CoinImageResult>? _referenceFuture;
  _RequestKey? _currentKey;

  @override
  void initState() {
    super.initState();
    _evaluateImageRequest();
  }

  @override
  void didUpdateWidget(covariant _CollectionCardImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    final newKey = _RequestKey.fromData(widget.data);
    if (_currentKey != newKey) {
      _evaluateImageRequest();
    }
  }

  void _evaluateImageRequest() {
    _currentKey = _RequestKey.fromData(widget.data);

    // If user photo exists (valid or invalid), no reference network read is needed!
    if (_currentKey!.obvUserUrl != null || _currentKey!.revUserUrl != null) {
      _referenceFuture = null;
      return;
    }

    // Check canonical mint asset pair before hitting reference service
    final canon = CanonicalMintAssetService.resolveFromMap(widget.data);
    if (canon != null && canon.obverseUrl.isNotEmpty && isOwnedStorageUrl(canon.obverseUrl)) {
      _referenceFuture = null;
      return;
    }

    // Otherwise, bound reference query with 5s timeout and return const CoinImageResult() on timeout/error
    final fetcher = widget.imageFetcher ?? CoinImageService.fetchReferenceImages;
    _referenceFuture = fetcher(
      year: _currentKey!.year,
      mint: _currentKey!.mintMark.isNotEmpty ? _currentKey!.mintMark : null,
      denomination: _currentKey!.denomination.isNotEmpty ? _currentKey!.denomination : null,
      series: _currentKey!.series.isNotEmpty ? _currentKey!.series : null,
      subject: _currentKey!.subject.isNotEmpty ? _currentKey!.subject : null,
    ).timeout(
      const Duration(seconds: 5),
      onTimeout: () => const CoinImageResult(),
    ).catchError((_) => const CoinImageResult());
  }

  @override
  Widget build(BuildContext context) {
    // 1. Check user obverse photo
    if (_currentKey?.obvUserUrl != null) {
      if (_currentKey!.obvUserUrl == 'INVALID_USER_PHOTO') {
        return _buildUserPlaceholder(context, reason: 'Unverified user photo');
      }
      return _buildCoinImage(_currentKey!.obvUserUrl!);
    }

    // 2. Check canonical mint asset pair
    final canon = CanonicalMintAssetService.resolveFromMap(widget.data);
    if (canon != null && canon.obverseUrl.isNotEmpty && isOwnedStorageUrl(canon.obverseUrl)) {
      return _buildCoinImage(canon.obverseUrl);
    }

    // 3. If no reference query pending, show placeholder
    if (_referenceFuture == null) {
      return _buildUserPlaceholder(context, reason: 'No image available');
    }

    // 4. FutureBuilder for reference image
    return FutureBuilder<CoinImageResult>(
      future: _referenceFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2)));
        }
        final result = snapshot.data;
        if (result != null && result.hasObverse && isOwnedStorageUrl(result.obverseUrl)) {
          return _buildCoinImage(result.obverseUrl!);
        }
        if (result != null && result.hasReverse && isOwnedStorageUrl(result.reverseUrl)) {
          return _buildCoinImage(result.reverseUrl!);
        }
        return _buildUserPlaceholder(context, reason: 'Reference not found');
      },
    );
  }

  static Widget _buildCoinImage(String url, {double rotationDegrees = 0.0}) {
    Widget img = Image.network(
      url,
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) => _buildErrorPlaceholder(context),
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return const Center(child: SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2)));
      },
    );
    if (rotationDegrees != 0.0) {
      img = Transform.rotate(
        angle: rotationDegrees * (3.141592653589793 / 180.0),
        child: img,
      );
    }
    return img;
  }

  static Widget _buildUserPlaceholder(BuildContext context, {required String reason}) {
    return Container(
      key: const ValueKey('coin_placeholder_container'),
      color: Theme.of(context).brightness == Brightness.dark 
          ? const Color(0xFF1E293B) 
          : const Color(0xFFE2E8F0),
      alignment: Alignment.center,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.monetization_on_outlined, size: 36, color: Colors.grey.shade400),
          const SizedBox(height: 4),
          Text(reason, style: TextStyle(fontSize: 10, color: Colors.grey.shade500), textAlign: TextAlign.center),
        ],
      ),
    );
  }

  static Widget _buildErrorPlaceholder(BuildContext context) {
    return Container(
      key: const ValueKey('coin_error_placeholder'),
      color: Colors.grey.shade200,
      alignment: Alignment.center,
      child: Icon(Icons.broken_image_outlined, size: 32, color: Colors.grey.shade400),
    );
  }
}

/// Public testing seam wrapper for [_CollectionCardImage]
@visibleForTesting
class CollectionCardImageHarness extends StatelessWidget {
  final Map<String, dynamic> data;
  final ReferenceImageFetcher? imageFetcher;

  const CollectionCardImageHarness({
    Key? key,
    required this.data,
    this.imageFetcher,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return _CollectionCardImage(
      data: data,
      imageFetcher: imageFetcher,
    );
  }
}
```

### 3.2 Grounded Image Ownership Guard Helper
In `numista_mobile/lib/screens/my_collection_screen.dart` (exposed publicly via `@visibleForTesting`):
```dart
  /// Validates whether a storage URL is authorized and hosted on approved Numista infrastructure.
  /// Checks relative same-origin paths first, then verifies HTTPS and allowed hosts/buckets.
  @visibleForTesting
  static bool isOwnedStorageUrl(String? url) {
    if (url == null || url.isEmpty) return false;
    final trimmed = url.trim();

    // 1. Relative same-origin check MUST occur before HTTPS check!
    if (trimmed.startsWith('/') && !trimmed.startsWith('//')) {
      return true;
    }

    final uri = Uri.tryParse(trimmed);
    if (uri == null || uri.scheme != 'https') return false;
    final host = uri.host.toLowerCase();

    // 2. Google Cloud Storage owned bucket prefixes
    if (host == 'storage.googleapis.com') {
      final path = uri.path;
      return path.startsWith('/numista-vault.firebasestorage.app/') ||
             path.startsWith('/numista-ai-images/') ||
             path.startsWith('/numista-reference-library/') ||
             path.startsWith('/numista-catalog-assets/') ||
             path.startsWith('/numista-uploads-studio-') ||
             path.startsWith('/studio-9101802118-8c9a8-uploads/');
    }

    // 3. Firebase Storage direct object hosts
    if (host.endsWith('.firebasestorage.app')) {
      return host == 'numista-vault.firebasestorage.app' ||
             host.endsWith('.firebasestorage.app');
    }

    // 4. Same-origin Numista web / preview channel hosts
    if (host == 'numista-vault.web.app' ||
        host == 'numista-vault.firebaseapp.com' ||
        host == 'numista.ai' ||
        host.endsWith('.web.app')) {
      return true;
    }

    return false;
  }
```

### 3.3 Robust User Photo Alias Extraction & Semantic `_RequestKey`
```dart
  static String? _extractUserPhoto(Map<String, dynamic> data, {required bool isObverse}) {
    final aliases = isObverse
        ? const ['imageObverse', 'image_obverse', 'image_url_obverse', 'stored_obv', 'obverse_image', 'image_url', 'user_obverse_url']
        : const ['imageReverse', 'image_reverse', 'image_url_reverse', 'stored_rev', 'reverse_image', 'user_reverse_url'];

    for (final key in aliases) {
      final val = data[key];
      if (val != null) {
        final s = val.toString().trim();
        if (s.isNotEmpty && s != 'null') {
          // If a user photo is recognized, it must be verified by the ownership guard
          return isOwnedStorageUrl(s) ? s : 'INVALID_USER_PHOTO';
        }
      }
    }
    return null;
  }

class _RequestKey {
  final String coinId;
  final String denomination;
  final String year;
  final String mintMark;
  final String series;
  final String subject;
  final String? obvUserUrl;
  final String? revUserUrl;

  const _RequestKey({
    required this.coinId,
    required this.denomination,
    required this.year,
    required this.mintMark,
    required this.series,
    required this.subject,
    this.obvUserUrl,
    this.revUserUrl,
  });

  factory _RequestKey.fromData(Map<String, dynamic> data) {
    final coinId = (data['id'] ?? data['coinId'] ?? data['sku'] ?? '').toString();
    final denom = (data['denomination'] ?? data['Denomination'] ?? '').toString();
    final year = CanonicalMintAssetService.canonicalYear(data);
    final mint = (data['mint_mark'] ?? data['mint'] ?? data['Mint Mark'] ?? '').toString();
    final series = (data['program_series'] ?? data['series'] ?? data['Program/Series'] ?? '').toString();
    final subject = (data['theme_subject'] ?? data['subject'] ?? data['Theme/Subject'] ?? '').toString();
    
    final obvUser = _extractUserPhoto(data, isObverse: true);
    final revUser = _extractUserPhoto(data, isObverse: false);

    return _RequestKey(
      coinId: coinId,
      denomination: denom,
      year: year,
      mintMark: mint,
      series: series,
      subject: subject,
      obvUserUrl: obvUser,
      revUserUrl: revUser,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is _RequestKey &&
          runtimeType == other.runtimeType &&
          coinId == other.coinId &&
          denomination == other.denomination &&
          year == other.year &&
          mintMark == other.mintMark &&
          series == other.series &&
          subject == other.subject &&
          obvUserUrl == other.obvUserUrl &&
          revUserUrl == other.revUserUrl;

  @override
  int get hashCode => Object.hash(
        coinId,
        denomination,
        year,
        mintMark,
        series,
        subject,
        obvUserUrl,
        revUserUrl,
      );
}
```

---

## 4. Spend & Operational Controls

1. **Elimination of Budget Caps:** Per Founder Eric's explicit order, all hard budget caps (including the $25 limit and hard $0.00 shutoffs) are completely removed.
2. **Budget Alerts Only:** Alerts configured at $20/month. No automated shutoff logic will be committed or executed.
3. **Execution Gating:** Strict PLAN ONLY mode. No code changes will be applied to the working tree until Founder Eric grants explicit typed YES.
4. **Target Environment:** P7-gate preview channel only. Live production deployment strictly forbidden.
5. **Nightly Stand-down:** Mandatory 3:00 AM ET stand-down observed.

---

## 5. Non-Force Rollback Path

If execution on `p7-v8.9` produces regressions, the rollback is strictly non-force:
```bash
git revert --no-edit <commit-hash-range>
git push origin p7-v8.9
```
`git push --force` is strictly forbidden across all branches.

---

## 6. Comprehensive Verification Suites

### 6.1 `numista_mobile/test/widgets/collection_card_image_test.dart`
```dart
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_mobile/screens/my_collection_screen.dart';
import 'package:numista_mobile/services/coin_image_service.dart';

void main() {
  group('CollectionCardImage Harness & Lifecycle Tests', () {
    testWidgets('User photo precedence: valid user photo displays directly with zero reference fetch calls', (tester) async {
      int fetchCount = 0;
      final data = {
        'id': 'coin_123',
        'denomination': 'Quarter',
        'year': '1958',
        'mint_mark': 'D',
        'imageObverse': 'https://storage.googleapis.com/numista-vault.firebasestorage.app/users/u1/coin123.jpg',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImageHarness(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult();
              },
            ),
          ),
        ),
      );

      // Verify that reference fetcher was NEVER invoked
      expect(fetchCount, equals(0));
      // Image.network is rendered with user photo URL
      expect(find.byType(Image), findsOneWidget);
    });

    testWidgets('Fail-closed on unapproved/malicious user photo: renders placeholder with zero reference fetch calls', (tester) async {
      int fetchCount = 0;
      final data = {
        'id': 'coin_456',
        'denomination': 'Nickel',
        'year': '1952',
        'imageObverse': 'http://insecure-foreign-domain.com/hack.jpg',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImageHarness(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                return const CoinImageResult();
              },
            ),
          ),
        ),
      );

      // Verify fetcher is NOT called (does not fall through to catalog/reference)
      expect(fetchCount, equals(0));
      // Shows user placeholder container
      expect(find.byKey(const ValueKey('coin_placeholder_container')), findsOneWidget);
      expect(find.text('Unverified user photo'), findsOneWidget);
    });

    testWidgets('Missing user photo queries reference fetcher and renders returned reference image', (tester) async {
      int fetchCount = 0;
      String? capturedYear;
      String? capturedMint;

      final data = {
        'id': 'coin_789',
        'denomination': 'Half Dollar',
        'year': '1964',
        'mint_mark': 'P',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImageHarness(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) async {
                fetchCount++;
                capturedYear = year;
                capturedMint = mint;
                return const CoinImageResult(
                  obverseUrl: 'https://storage.googleapis.com/numista-vault.firebasestorage.app/ref/1964_half_obv.jpg',
                );
              },
            ),
          ),
        ),
      );

      await tester.pump(); // Settle future

      expect(fetchCount, equals(1));
      expect(capturedYear, equals('1964'));
      expect(capturedMint, equals('P'));
      expect(find.byType(Image), findsOneWidget);
    });

    testWidgets('Bounded timeout on reference service returns terminal empty state without crashing', (tester) async {
      final completer = Completer<CoinImageResult>();

      final data = {
        'id': 'coin_timeout',
        'denomination': 'Quarter',
        'year': '1976',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImageHarness(
              data: data,
              imageFetcher: ({required year, mint, denomination, series, subject}) {
                return completer.future; // Never resolves immediately
              },
            ),
          ),
        ),
      );

      // Loading spinner initially
      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      // Advance clock past 5-second timeout
      await tester.pump(const Duration(seconds: 6));

      // Terminal empty placeholder rendered
      expect(find.byKey(const ValueKey('coin_placeholder_container')), findsOneWidget);
      expect(find.text('Reference not found'), findsOneWidget);
    });
  });
}
```

### 6.2 `numista_mobile/test/services/owned_storage_url_test.dart`
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_mobile/screens/my_collection_screen.dart';

void main() {
  group('isOwnedStorageUrl Unit Tests', () {
    test('Allows relative same-origin paths', () {
      expect(_CollectionCardImage.isOwnedStorageUrl('/images/coins/1958_quarter.png'), isTrue);
      expect(_CollectionCardImage.isOwnedStorageUrl('/assets/sample.jpg'), isTrue);
      expect(_CollectionCardImage.isOwnedStorageUrl('//malicious.com/image.png'), isFalse);
    });

    test('Allows verified GCS bucket prefixes', () {
      expect(_CollectionCardImage.isOwnedStorageUrl('https://storage.googleapis.com/numista-vault.firebasestorage.app/coins/1.jpg'), isTrue);
      expect(_CollectionCardImage.isOwnedStorageUrl('https://storage.googleapis.com/numista-ai-images/coins/2.jpg'), isTrue);
      expect(_CollectionCardImage.isOwnedStorageUrl('https://storage.googleapis.com/numista-reference-library/coins/3.jpg'), isTrue);
      expect(_CollectionCardImage.isOwnedStorageUrl('https://storage.googleapis.com/numista-catalog-assets/coins/4.jpg'), isTrue);
      expect(_CollectionCardImage.isOwnedStorageUrl('https://storage.googleapis.com/numista-uploads-studio-abc/coins/5.jpg'), isTrue);
      expect(_CollectionCardImage.isOwnedStorageUrl('https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/coins/6.jpg'), isTrue);
    });

    test('Allows Firebase Storage and preview channel web hosts', () {
      expect(_CollectionCardImage.isOwnedStorageUrl('https://numista-vault.firebasestorage.app/v0/b/...'), isTrue);
      expect(_CollectionCardImage.isOwnedStorageUrl('https://preview-catalog--numista-vault.web.app/img.png'), isTrue);
      expect(_CollectionCardImage.isOwnedStorageUrl('https://numista.ai/assets/logo.png'), isTrue);
    });

    test('Rejects unowned GCS buckets, foreign domains, and insecure HTTP', () {
      expect(_CollectionCardImage.isOwnedStorageUrl('https://storage.googleapis.com/unowned-random-bucket/test.jpg'), isFalse);
      expect(_CollectionCardImage.isOwnedStorageUrl('https://upload.wikimedia.org/wikipedia/commons/test.jpg'), isFalse);
      expect(_CollectionCardImage.isOwnedStorageUrl('http://storage.googleapis.com/numista-vault.firebasestorage.app/coins/1.jpg'), isFalse);
      expect(_CollectionCardImage.isOwnedStorageUrl('ftp://example.com/coin.jpg'), isFalse);
      expect(_CollectionCardImage.isOwnedStorageUrl('javascript:alert(1)'), isFalse);
      expect(_CollectionCardImage.isOwnedStorageUrl(''), isFalse);
      expect(_CollectionCardImage.isOwnedStorageUrl(null), isFalse);
    });
  });
}
```

---

## 7. Mirroring Verification Table
Mirrored across all 5 mailbox directories:
1. `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.7.md`
2. `BETA TEST/Grok Bot/8 OCT 26/BATONS/FAILFIX_PLAN_NET-780c_IMAGES_v1.7.md`
3. `BETA TEST/Grok Bot/8 OCT 26/RADIO NET/FAILFIX_PLAN_NET-780c_IMAGES_v1.7.md`
4. `BETA TEST/Grok Bot/8 OCT 26/INBOX/FAILFIX_PLAN_NET-780c_IMAGES_v1.7.md`
5. `BETA TEST/Grok Bot/8 OCT 26/OUTBOX/FAILFIX_PLAN_NET-780c_IMAGES_v1.7.md`
6. `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-780c_IMAGES_v1.7.md`
