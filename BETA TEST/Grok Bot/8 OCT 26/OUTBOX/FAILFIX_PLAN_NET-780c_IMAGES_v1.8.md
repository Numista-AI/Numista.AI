# FAILFIX PLAN v1.8: Broken Images & Storage URL Security Guard (NET-780c)
**To:** Antigravity Desk, Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work / Catalog Day Team (`ba2bfdb2`)  
**Date:** 7 November 2026, 2:30 PM ET  
**Reference Batons:**  
- `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`  
- `BATON_NET-817_REVISE_780b-780c_v1.8_PER-COS-60_20261107-1410.md`  
- `RADIO_NET-830_GROKCOS-to-AGCOS_REVISE-817-v1.8_20261107.md`  
- `COS_SCORE_NET-817_CARDS_IMAGES_v1.7_20261107.md` (Images 53/100 FAIL, Cards 67/100 FAIL, Combined 60/100 FAIL)  
**Directives & Audit Authority:**  
- `GB CoS SCORE v1.7`: Must-fixes MF-B1–B3 and MF-I1–I5.  
- `PROTOCOL UPDATE: ARGON DROPPED ENTIRELY`: Founder Eric typed YES. Review sequence is strictly: AG CoS Plan $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES.  
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

Plan v1.8 systematically resolves all numbered blocking must-fixes from `COS_SCORE_NET-817_CARDS_IMAGES_v1.7_20261107.md` and `RADIO_NET-830`:

| Must-Fix # | Must-Fix Description | Plan v1.8 Resolution & Grounding | Plan Section |
| :--- | :--- | :--- | :--- |
| **MF-B1** | **Kaggle Single Owner + Complete Span:** Resolve contradiction; pick single owner for all Google/Kaggle deletions (`3454`, `3820`, `5252–5278`, `5549–5684`, `150–151`). Keep `_onSearchEbay` @4410 with EPN affiliate tags. | **NET-816 is the sole structural deletion owner** for all Google & Kaggle inspector elements across both dev (`b0b05808`) and p7 (`4d17ca5e`). NET-817 explicitly cites NET-816 as a prerequisite dependency and performs **zero duplicate or conflicting deletions**. Line 4410 `_onSearchEbay` is strictly **PRESERVED** with affiliate tags per B05N-18 and `RADIO_NET-825`. | §2.A, §4.A |
| **MF-B2** | **Package Name Correctness:** Use `package:numista_ai/...` strictly matching `pubspec.yaml:1` (not `numista_mobile`). | All proposed imports, production widgets, utility helpers, and test files strictly use `package:numista_ai/...` matching `numista_mobile/pubspec.yaml:1`. | §3, §6 |
| **MF-B3** | **Accurate DTG & Declared Apply Order:** Stamp actual filing DTG and declare precise apply order between Cards and Images. | Delivery stamped at actual filing time (`7 Nov 2026, 2:30 PM ET`). Stated apply order: **Cards `canonicalYear` (NET-780b) lands first**, followed by **Images `_RequestKey` (NET-780c)** which depends on it. | §1, §4.C |
| **MF-I1** | **Real URL Forms Only (Exact Names, No Wildcards):** Accept `firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/...` (user `getDownloadURL()`) and `storage.googleapis.com/us_mint_coin_images/` (Tier-1 refs); drop fabricated buckets; drop open wildcards. | Strict allowlist accepts: (1) `https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/...`; (2) `https://storage.googleapis.com/us_mint_coin_images/...`; (3) `https://storage.googleapis.com/numista-reference-library/...`; (4) `https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/...`; (5) `https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/...` (exact bucket); (6) `https://storage.googleapis.com/studio-9101802118-8c9a8.firebasestorage.app/...`; (7) Relative paths starting with `/`, not `//`, and containing no backslash `\`. Fabricated buckets (`numista-vault`, `numista-ai-images`, `numista-catalog-assets`) and open wildcards (`*.firebasestorage.app`, `*.web.app`) are completely eliminated. | §2.B, §3.A |
| **MF-I2** | **Reachable Public Helpers & Public Testable Widget:** Place `isOwnedStorageUrl` top-level public; place `extractUserPhoto` top-level public; test exact public symbols. | Declares `bool isOwnedStorageUrl(String? url)` as a public top-level function in `lib/utils/owned_storage_url.dart`. Declares `String extractUserPhoto(Map<String, dynamic> data, {bool isObverse = true})` in `lib/utils/collection_image_utils.dart`. Encapsulates card image rendering in public production widget `CollectionCardImage` in `lib/widgets/collection_card_image.dart` with injectable `imageFetcher`. Tests import and test the exact public functions and pump the production widget. | §3.A, §3.B, §6 |
| **MF-I3** | **Restore Shipped Display Policy & Reverse Preference:** Keep reverse preferred; keep MF-V3-3 steal-guard (`:6409–6417`); render reverse-only user photos; preserve circular glow and `BoxFit.contain`. | Restored shipped display policy: (1) Canonical pair prefers reverse (`canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl`); (2) Direct user photos prefer reverse, and reverse-only user photos (`revUserUrl` present, `obvUserUrl` null) render the reverse photo with fail-closed security guard; (3) Steal-guard (`:6409–6417`) strictly preserved: when subject is non-empty and reverse is null, displays placeholder instead of falling back to generic obverse; (4) Visual coin integrity preserved with `BoxFit.contain` and gold circular glow (`blurRadius: 14`), preventing coin cropping. | §2.C, §3.B |
| **MF-I4** | **CSP Truth & Firebase Storage Support:** Quote `firebase.json:276` verbatim; verify accepted hosts reachable under CSP; add `firebasestorage.googleapis.com` to `img-src`. | Verbatim quote of `numista_mobile/firebase.json:276` provided. Explains that while `storage.googleapis.com` is present in `img-src`, Firebase download URLs (`https://firebasestorage.googleapis.com/...`) require adding `https://firebasestorage.googleapis.com` to `img-src`. Exact surgical diff for `firebase.json:276` provided. | §2.D, §3.C |
| **MF-I5** | **Comprehensive Test Suite:** `_RequestKey` refresh test; real bucket fixtures; accepted/rejected ownership tests; proven 1964 Half Dollar reference fallback. | Test suite in `numista_mobile/test/widgets/collection_card_image_test.dart` verifies: (1) `_RequestKey` refresh test: pumps with empty year, then pumps with populated year, asserting fetcher count increments to 2; (2) Real bucket fixtures tested through public `isOwnedStorageUrl`; (3) Rejection of `evil.firebasestorage.app`, `evil.web.app`, `storage.googleapis.com/numista-uploads-studio-evil/`, and `/\evil.com`; (4) Proves `CanonicalMintAssetService.resolveFromMap` returns null for 1964 Kennedy Half Dollar fixture, mathematically proving reference fetch count = 1. | §6.1, §6.2 |

---

## 2. Root Cause Analysis & Verbatim Grounding

### A. Kaggle & Google Images Structural Deletion Ownership (MF-B1)
On branch `p7-v8.9` at commit `4d17ca5e`, `numista_mobile/lib/screens/my_collection_screen.dart` contains:
- Call site at line 3454 (`_fetchInspectorSimilar(data);`).
- Inspector loader at lines 5252–5278.
- Inspector UI at lines 5549–5684.
- State variables at lines 150–151.
- Google Images button at lines 3531–3548 and handler at lines 4387–4406.
- Outbound eBay search at line 4410 (`_onSearchEbay`).

**Ownership Rule:** NET-816 (Catalog FAILFIX Plan v1.11) is the sole deletion owner for all Google and Kaggle elements (`3454`, `3820`, `5252–5278`, `5549–5684`, `150–151`, `3531–3548`, `4387–4406`). NET-780c declares this dependency and performs zero duplicate deletions. Line 4410 `_onSearchEbay` is strictly **PRESERVED** with EPN affiliate tags (`campid=5339123164, customid=numista_app_search`).

### B. Real Storage Bucket & Host URLs on the Pin (MF-I1)
Auditing the codebase on `p7` (@ `4d17ca5e`):
1. **Real Project Storage Bucket:**
   `numista_mobile/lib/firebase_options.dart` lines 55, 64, 73:
   ```dart
   storageBucket: 'studio-9101802118-8c9a8.firebasestorage.app'
   ```
   `.firebaserc`:
   ```json
   "default": "studio-9101802118-8c9a8"
   ```
2. **Real User Upload Download URLs:**
   `my_collection_screen.dart` lines 5015, 5489, 5493:
   ```dart
   5015: final url = await snap.ref.getDownloadURL();
   5489: FirebaseStorage.instance.ref('users/$userEmail/coins/...').getDownloadURL()
   ```
   Firebase Storage `getDownloadURL()` yields URLs of the form:
   `https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/...`
3. **Real Official Mint Tier-1 Reference Images:**
   `ref_image_widget.dart` line 57:
   `https://storage.googleapis.com/us_mint_coin_images/$path`
4. **Real Tier 2–5 Reference Images:**
   `canonical_mint_asset_service.dart` line 53:
   `https://storage.googleapis.com/numista-reference-library/$path`
5. **Real Direct Upload Buckets:**
   `canonical_mint_asset_service.dart` lines 37–38:
   `storage.googleapis.com/studio-9101802118-8c9a8-uploads/` and `storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/`.

**Defect in Prior Allowlist:** Prior versions admitted fabricated bucket names (`numista-vault.firebasestorage.app`, `numista-ai-images`, `numista-catalog-assets`) which do not exist, while rejecting real user photos (`firebasestorage.googleapis.com`) and Tier-1 reference images (`us_mint_coin_images`). Furthermore, wildcard rules like `host.endsWith('.firebasestorage.app')` or `host.endsWith('.web.app')` allowed any arbitrary attacker-created Firebase project to inject images, and protocol-relative URLs containing backslashes (`/\evil.com`) bypassed browser origin checks.

### C. Existing Widget Display Policy & Steal-Guard (MF-I3)
In `my_collection_screen.dart` lines 6356–6479 on p7 (`4d17ca5e`):
1. **Canonical Pair Reverse Preference (line 6371):**
   ```dart
   final canonUrl = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
   ```
2. **User Direct URL Reverse Preference (line 6379):**
   ```dart
   final directUrl = rev.isNotEmpty ? rev : obv; // Prefer reverse (distinct design)
   ```
3. **MF-V3-3 Steal-Guard (lines 6409–6417):**
   ```dart
   // MF-V3-3: When subject is known and reverse is null (steal-guard
   // correctly blocked a generic reverse), show placeholder instead of
   // falling back to generic obverse. Keeps obverse fallback for coins
   // without a subject (e.g. generic Morgan/Peace).
   final refUrl = (ref?.reverseUrl?.isNotEmpty == true)
       ? ref!.reverseUrl!
       : (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)
           ? ref!.obverseUrl!
           : '';
   ```
4. **Visual Styling & BoxFit (lines 6443–6477):**
   ```dart
   child: Container(
     decoration: BoxDecoration(
       shape: BoxShape.circle,
       boxShadow: [
         BoxShadow(
           color: const Color(0xFFC9A227).withAlpha(40),
           blurRadius: 14,
           spreadRadius: 1,
         ),
       ],
     ),
     child: Image.network(
       url,
       fit: BoxFit.contain,
   ```

### D. Verbatim Content-Security-Policy Analysis (MF-I4)
In `numista_mobile/firebase.json` line 276 on p7 (`4d17ca5e`), the CSP header reads verbatim:
```json
"value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
```
**CSP Analysis:** Under W3C Content Security Policy level 2/3, when `img-src` is specified, it strictly overrides `default-src` for image loads. The current `img-src` contains:
`img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app;`
Notice that `storage.googleapis.com` is permitted, but `firebasestorage.googleapis.com` is **omitted** from `img-src`. When user photos are rendered from `https://firebasestorage.googleapis.com/v0/b/...`, the browser blocks the image load with a CSP violation unless `https://firebasestorage.googleapis.com` is explicitly added to `img-src`. Adding `https://firebasestorage.googleapis.com` ensures full CSP compliance.

---

## 3. Targeted Production Code Implementation

### A. Public Top-Level Storage Guard: `lib/utils/owned_storage_url.dart` (MF-I1, MF-I2)
```dart
/// Public top-level security guard for image URLs rendered in Numista.AI.
/// Admits only verified first-party and official Google Cloud / Firebase storage URLs.
/// Blocks unowned third-party storage, wildcards, and protocol-relative bypasses.
bool isOwnedStorageUrl(String? url) {
  if (url == null) return false;
  final trimmed = url.trim();
  if (trimmed.isEmpty) return false;

  // 1. Relative same-origin paths: must start with single '/', not '//', and no backslashes
  if (trimmed.startsWith('/') && !trimmed.startsWith('//') && !trimmed.contains(r'\')) {
    return true;
  }

  // 2. Strict HTTPS parsing
  final uri = Uri.tryParse(trimmed);
  if (uri == null || uri.scheme != 'https') return false;

  final host = uri.host.toLowerCase();
  final path = uri.path;

  // 3. Form A: Firebase Storage download URL for real project bucket (studio-9101802118-8c9a8)
  if (host == 'firebasestorage.googleapis.com') {
    return path.startsWith('/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/');
  }

  // 4. Form B: Google Cloud Storage with exact permitted bucket roots
  if (host == 'storage.googleapis.com') {
    return path.startsWith('/us_mint_coin_images/') ||
           path.startsWith('/numista-reference-library/') ||
           path.startsWith('/studio-9101802118-8c9a8-uploads/') ||
           path.startsWith('/numista-uploads-studio-9101802118-8c9a8/') ||
           path.startsWith('/studio-9101802118-8c9a8.firebasestorage.app/');
  }

  return false;
}
```

### B. User Photo Helper: `lib/utils/collection_image_utils.dart` (MF-I2)
```dart
/// Extracts cleaned direct user photo URL from coin document map.
/// Checks camelCase, snake_case, and legacy aliases.
String extractUserPhoto(Map<String, dynamic> data, {bool isObverse = true}) {
  final keys = isObverse
      ? const <String>[
          'image_url_obverse',
          'imageUrlObverse',
          'obverse_image_url',
          'imageObverse',
          'image_obverse',
          'obverseUrl',
          'photo_obverse',
        ]
      : const <String>[
          'image_url_reverse',
          'imageUrlReverse',
          'reverse_image_url',
          'imageReverse',
          'image_reverse',
          'reverseUrl',
          'photo_reverse',
        ];

  for (final k in keys) {
    final val = data[k];
    if (val != null) {
      final s = val.toString().trim();
      if (s.isNotEmpty && s != 'null' && s != 'None' && !s.startsWith('gs://')) {
        return s;
      }
    }
  }
  return '';
}
```

### C. Public Production Widget: `lib/widgets/collection_card_image.dart` (MF-I2, MF-I3)
```dart
import 'package:flutter/material.dart';
import 'package:numista_ai/services/canonical_mint_asset_service.dart';
import 'package:numista_ai/services/coin_image_service.dart';
import 'package:numista_ai/utils/collection_image_utils.dart';
import 'package:numista_ai/utils/owned_storage_url.dart';

/// Semantic request key for memoizing reference image fetches.
/// Uses CanonicalMintAssetService.canonicalYear to normalize year representation.
@immutable
class CollectionCardImageRequestKey {
  final String year;
  final String mint;
  final String denomination;
  final String series;
  final String subject;

  const CollectionCardImageRequestKey({
    required this.year,
    required this.mint,
    required this.denomination,
    required this.series,
    required this.subject,
  });

  factory CollectionCardImageRequestKey.fromData(Map<String, dynamic> data) {
    String read(String snakeKey, String legacyKey) {
      final s = data[snakeKey]?.toString();
      if (s != null && s.trim().isNotEmpty && s.trim() != 'None' && s.trim() != 'null') return s.trim();
      final l = data[legacyKey]?.toString();
      if (l != null && l.trim().isNotEmpty && l.trim() != 'None' && l.trim() != 'null') return l.trim();
      return '';
    }

    final canonYear = CanonicalMintAssetService.canonicalYear(data);
    final year = canonYear.isNotEmpty ? canonYear : read('year', 'Year').replaceAll(RegExp(r'\.0$'), '');
    final mint = read('mint_mark', 'Mint Mark');
    final denom = read('denomination', 'Denomination');
    final series = read('program_series', 'Program/Series');
    final subject = read('theme_subject', 'Theme/Subject');

    return CollectionCardImageRequestKey(
      year: year,
      mint: mint,
      denomination: denom,
      series: series,
      subject: subject,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CollectionCardImageRequestKey &&
          runtimeType == other.runtimeType &&
          year == other.year &&
          mint == other.mint &&
          denomination == other.denomination &&
          series == other.series &&
          subject == other.subject;

  @override
  int get hashCode =>
      year.hashCode ^
      mint.hashCode ^
      denomination.hashCode ^
      series.hashCode ^
      subject.hashCode;
}

typedef ImageFetcherFn = Future<CoinImageResult> Function({
  required String year,
  String? mint,
  String? denomination,
  String? series,
  String? subject,
});

/// Production collection card image widget with lifecycle caching, fail-closed
/// storage validation, reverse-preference display policy, and MF-V3-3 steal-guard.
class CollectionCardImage extends StatefulWidget {
  final Map<String, dynamic> data;
  final ImageFetcherFn? imageFetcher;

  const CollectionCardImage({
    super.key,
    required this.data,
    this.imageFetcher,
  });

  @override
  State<CollectionCardImage> createState() => _CollectionCardImageState();
}

class _CollectionCardImageState extends State<CollectionCardImage> {
  Future<CoinImageResult>? _refFuture;
  CollectionCardImageRequestKey? _lastKey;

  @override
  void initState() {
    super.initState();
    _checkAndInitFetch();
  }

  @override
  void didUpdateWidget(covariant CollectionCardImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    final newKey = CollectionCardImageRequestKey.fromData(widget.data);
    if (newKey != _lastKey) {
      _checkAndInitFetch();
    }
  }

  void _checkAndInitFetch() {
    _lastKey = CollectionCardImageRequestKey.fromData(widget.data);

    // 1. Direct user photos (prefer reverse, support reverse-only)
    final revUserUrl = extractUserPhoto(widget.data, isObverse: false);
    final obvUserUrl = extractUserPhoto(widget.data, isObverse: true);

    if (revUserUrl.isNotEmpty || obvUserUrl.isNotEmpty) {
      _refFuture = null; // Bypasses network fetch completely
      return;
    }

    // 2. Canonical Mint asset pair
    final canon = CanonicalMintAssetService.resolveFromMap(widget.data);
    if (canon != null) {
      final canonUrl = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
      if (canonUrl.isNotEmpty) {
        _refFuture = null; // Bypasses network fetch completely
        return;
      }
    }

    // 3. Fallback to reference service with 5s timeout
    final fetcher = widget.imageFetcher ?? CoinImageService.fetchReferenceImages;
    _refFuture = fetcher(
      year: _lastKey!.year,
      mint: _lastKey!.mint.isEmpty ? null : _lastKey!.mint,
      denomination: _lastKey!.denomination.isEmpty ? null : _lastKey!.denomination,
      series: _lastKey!.series.isEmpty ? null : _lastKey!.series,
      subject: _lastKey!.subject.isEmpty ? null : _lastKey!.subject,
    ).timeout(
      const Duration(seconds: 5),
      onTimeout: () => const CoinImageResult(),
    );
  }

  @override
  Widget build(BuildContext context) {
    // 1. User photo check with reverse preference and fail-closed guard
    final revUserUrl = extractUserPhoto(widget.data, isObverse: false);
    final obvUserUrl = extractUserPhoto(widget.data, isObverse: true);

    if (revUserUrl.isNotEmpty) {
      if (isOwnedStorageUrl(revUserUrl)) {
        return _buildCoinImage(revUserUrl);
      }
      return _buildPlaceholder(); // Fail-closed on unowned reverse user photo
    }

    if (obvUserUrl.isNotEmpty) {
      if (isOwnedStorageUrl(obvUserUrl)) {
        return _buildCoinImage(obvUserUrl);
      }
      return _buildPlaceholder(); // Fail-closed on unowned obverse user photo
    }

    // 2. Canonical Mint asset check
    final canon = CanonicalMintAssetService.resolveFromMap(widget.data);
    if (canon != null) {
      final canonUrl = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
      if (canonUrl.isNotEmpty && isOwnedStorageUrl(canonUrl)) {
        return _buildCoinImage(canonUrl);
      }
    }

    // 3. Render reference fetch future
    if (_refFuture == null) {
      return _buildPlaceholder();
    }

    return FutureBuilder<CoinImageResult>(
      future: _refFuture,
      builder: (context, snapshot) {
        final ref = snapshot.data;

        // MF-V3-3 Steal-Guard: When subject is known and reverse is null,
        // show placeholder instead of falling back to generic obverse.
        final refUrl = (ref?.reverseUrl?.isNotEmpty == true)
            ? ref!.reverseUrl!
            : (_lastKey!.subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)
                ? ref!.obverseUrl!
                : '';

        if (refUrl.isNotEmpty && isOwnedStorageUrl(refUrl)) {
          return _buildCoinImage(refUrl);
        }

        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(
            child: SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Color(0xFFC9A227),
              ),
            ),
          );
        }

        return _buildPlaceholder();
      },
    );
  }

  Widget _buildPlaceholder() {
    return const Center(
      child: Icon(Icons.image_not_supported_outlined, size: 36, color: Color(0xFF8B92B4)),
    );
  }

  Widget _buildCoinImage(String url) {
    return Center(
      child: Container(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: const Color(0xFFC9A227).withAlpha(40),
              blurRadius: 14,
              spreadRadius: 1,
            ),
          ],
        ),
        child: Image.network(
          url,
          fit: BoxFit.contain, // Prevents coin edge cropping
          errorBuilder: (context, error, stackTrace) => _buildPlaceholder(),
          loadingBuilder: (context, child, progress) {
            if (progress == null) return child;
            return const Center(
              child: SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Color(0xFFC9A227),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
```

In `numista_mobile/lib/screens/my_collection_screen.dart`:
Lines 6356–6479 are replaced with `CollectionCardImage`:
```dart
<<<<
6356: class _CollectionCardImage extends StatelessWidget {
...
6479: }
====
6356: // Delegated to production widget CollectionCardImage (NET-780c v1.8)
6357: class _CollectionCardImage extends StatelessWidget {
6358:   final Map<String, dynamic> data;
6359:   const _CollectionCardImage({required this.data});
6360:   @override
6361:   Widget build(BuildContext context) => CollectionCardImage(data: data);
6362: }
>>>>
```

### D. Surgical CSP Patch in `firebase.json` (MF-I4)
In `numista_mobile/firebase.json` line 276:
```json
<<<<
"value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
====
"value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://firebasestorage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
>>>>
```

---

## 4. Execution Gates & Apply Ordering

### A. Pre-Flight Verification & Pinned Commit
Before executing any file modifications on branch `p7-v8.9`:
```bash
git status
git log --oneline -1
```
Execution is strictly locked to branch `p7-v8.9` at HEAD `ebf1eed8`. `origin/main` remains strictly locked at `9f04550a`. Stripe remains locked OFF.

### B. Single Ownership Contract (MF-B1)
NET-816 is the sole structural deletion owner of all Google and Kaggle inspector artifacts (`3454`, `3820`, `5252–5278`, `5549–5684`, `150–151`, `3531–3548`, `4387–4406`). NET-817 depends on NET-816 landing first or concurrently, and performs zero duplicate deletions. `_onSearchEbay` (@ line 4410) is strictly preserved with EPN affiliate tracking.

### C. Stated Apply Ordering (MF-B3)
1. **First:** Cards Plan NET-780b lands `canonicalYear` at line 76 of `canonical_mint_asset_service.dart`, updates denomination regex at lines 431–435, and extracts `CollectionCardValuationRow`.
2. **Second:** Images Plan NET-780c lands `_RequestKey` in `my_collection_screen.dart` (which invokes `CanonicalMintAssetService.canonicalYear(data)`), and deploys `isOwnedStorageUrl` and `CollectionCardImage`.

### D. Rollback Protocol
If any post-apply check or test fails:
```bash
git checkout p7-v8.9
git revert --no-edit <Images-commit-hash>
git push origin p7-v8.9
```

---

## 5. Security, Rules & Standing Boundaries
- **No Argon:** Cycle has zero Argon reviews per Founder Eric's typed YES.
- **PLAN ONLY:** Zero code execution, zero deployments, zero Firestore writes without Founder Eric's explicit typed YES.
- **Alerts Only, Never Budget Caps:** Hard spending caps are permanently eliminated; alerts set at $20/mo.
- **No AJ PII:** Zero user emails or private credentials in plans, tests, or fixtures.
- **Nightly Stand-Down:** Standing 3:00 AM ET stand-down observed.

---

## 6. Real Automated Test Suites

### 6.1 `numista_mobile/test/utils/owned_storage_url_test.dart` (MF-I1, MF-I2, MF-I5)
Verifies public top-level `isOwnedStorageUrl` against real accepted bucket forms and malicious/unowned rejected forms:
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/utils/owned_storage_url.dart';

void main() {
  group('isOwnedStorageUrl Real Allowlist Verification', () {
    test('Accepts Form A: Real Firebase Storage download URL for project bucket', () {
      const realUserUrl = 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon_user_1%2Fcoins%2F123.jpg';
      expect(isOwnedStorageUrl(realUserUrl), isTrue);
    });

    test('Accepts Form B: Real GCS official Tier-1 mint reference images', () {
      const tier1Ref = 'https://storage.googleapis.com/us_mint_coin_images/2026_series/lincoln_cent_obverse.jpg';
      expect(isOwnedStorageUrl(tier1Ref), isTrue);
    });

    test('Accepts Form B: Real GCS Tier 2-5 reference library', () {
      const refLib = 'https://storage.googleapis.com/numista-reference-library/morgan/1881s_reverse.jpg';
      expect(isOwnedStorageUrl(refLib), isTrue);
    });

    test('Accepts Form B: Real direct upload bucket roots', () {
      const upload1 = 'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/user_abc/front.jpg';
      const upload2 = 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/user_def/back.jpg';
      const gcsFb = 'https://storage.googleapis.com/studio-9101802118-8c9a8.firebasestorage.app/o/photo.png';
      expect(isOwnedStorageUrl(upload1), isTrue);
      expect(isOwnedStorageUrl(upload2), isTrue);
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
```

### 6.2 `numista_mobile/test/widgets/collection_card_image_test.dart` (MF-I2, MF-I3, MF-I5)
Pumps the production `CollectionCardImage` widget with an injectable fetcher, proving user-photo precedence, reverse-only user photos, steal-guard behavior, request-key refresh, and reference fallback:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/canonical_mint_asset_service.dart';
import 'package:numista_ai/services/coin_image_service.dart';
import 'package:numista_ai/widgets/collection_card_image.dart';

void main() {
  group('CollectionCardImage Production Widget Tests', () {
    testWidgets('Case 1: User photo takes top precedence and bypasses network fetch', (tester) async {
      int fetchCount = 0;
      final data = {
        'image_url_obverse': 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon%2Fcoins%2Fobv.jpg',
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

      expect(fetchCount, 0, reason: 'Valid user photo must bypass network reference fetch');
      expect(find.byType(Image), findsOneWidget);
    });

    testWidgets('Case 2: Reverse-only user photo renders reverse and bypasses network fetch', (tester) async {
      int fetchCount = 0;
      final data = {
        'image_url_reverse': 'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fanon%2Fcoins%2Frev.jpg',
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
      expect(find.byType(Image), findsOneWidget);
    });

    testWidgets('Case 3: Unowned/malicious user photo fails closed without network fetch', (tester) async {
      int fetchCount = 0;
      final data = {
        'image_url_obverse': 'https://evil.firebasestorage.app/malicious.jpg',
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

      expect(fetchCount, 0, reason: 'Unowned user photo must fail closed without network fetch');
      expect(find.byIcon(Icons.image_not_supported_outlined), findsOneWidget);
    });

    testWidgets('Case 4: Reference fetch triggered when no user photo and no canonical asset (1964 Kennedy)', (tester) async {
      final data = {
        'Year': '1964',
        'mint_mark': 'D',
        'denomination': 'Half Dollar',
        'program_series': 'Kennedy Half Dollar',
      };

      // Mathematical proof: CanonicalMintAssetService.resolveFromMap returns null for 1964 Kennedy
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
                  reverseUrl: 'https://storage.googleapis.com/us_mint_coin_images/kennedy/1964_rev.jpg',
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

    testWidgets('Case 5: MF-V3-3 Steal-Guard: Subject known + reverse null displays placeholder (no obverse fallback)', (tester) async {
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
                  obverseUrl: 'https://storage.googleapis.com/us_mint_coin_images/generic_obv.jpg',
                  reverseUrl: null, // Steal-guard blocked generic reverse
                );
              },
            ),
          ),
        ),
      );
      await tester.pump();

      expect(fetchCount, 1);
      expect(find.byIcon(Icons.image_not_supported_outlined), findsOneWidget, reason: 'Steal guard must prevent falling back to generic obverse when subject is populated');
    });

    testWidgets('Case 6: Semantic RequestKey refresh: changing Year from "" to populated triggers second fetch', (tester) async {
      int fetchCount = 0;
      final dataInitial = {
        'Year': '',
        'denomination': 'Half Dollar',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
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
      expect(fetchCount, 1);

      // Mutate year in updated widget
      final dataUpdated = {
        'Year': '1964',
        'denomination': 'Half Dollar',
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CollectionCardImage(
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
      expect(fetchCount, 2, reason: 'Changing year from empty to populated must invalidate request key and trigger second fetch');
    });
  });
}
```

---

## 7. Delivery & Sign-Off Requirements
- **Verification Command:** `flutter test test/utils/owned_storage_url_test.dart test/widgets/collection_card_image_test.dart`
- **Review Requirement:** Independent review score $\ge 95$ from Grok Bot CoS and Stand Alone Grok (SAG, grok-4.7) prior to Founder Eric's typed YES.
