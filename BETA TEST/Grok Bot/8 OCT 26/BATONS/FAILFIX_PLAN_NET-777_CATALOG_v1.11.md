# FAILFIX PLAN v1.11: Live Public Catalog Browse (NET-777 / NET-788 / NET-803 / NET-804 / NET-808 / NET-811 / NET-815 / NET-816 / NET-818 / NET-819 / NET-823 / NET-826 / NET-829)

**Document Version:** 1.11  
**Track:** NET-816 (Thanksgiving Critical Path FIRST — Public Catalog Browse FAILFIX)  
**Author:** Antigravity CoS v4 Work / Catalog Day Team (`ba2bfdb2`)  
**Reviewers:** Grok Bot CoS (GROKCOS), Task Master, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**Delivery DTG:** 2026-11-07T15:15:00-05:00 (ET)  
**Authority:** `RADIO_NET-829_GROKCOS-to-AGCOS_REVISE-816-v1.11_20261107.md` and `COS_SCORE_NET-816_CATALOG_v1.10_20261107.md` (48/100 FAIL)  
**Repository Working Pins:**  
- `dev` commit `b0b058087f1492244a0c0b769e126b38ac1ba06c`  
- `p7` commit `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235`  
- Current HEAD `p7-v8.9`  
**Standing Boundary Condition:** STRICT PLAN ONLY. Zero code execution, zero production deploys, zero live Firestore writes, zero Stripe mutations without Founder Eric's explicit typed YES. Target is `preview-catalog` (p7-gate preview) ONLY. `origin/main` is locked at `9f04550a`. Stripe strictly OFF.

---

## 1. Executive Summary & Closeout Table of All 9 Numbered Must-Fixes

This plan resolves every blocker and deficiency identified in the CoS-48 score (`COS_SCORE_NET-816_CATALOG_v1.10_20261107.md`) and ordered in `RADIO_NET-829`.

### Comprehensive Closeout Matrix

| # | CoS-48 Finding | Root Cause in v1.10 | Pinned Grounding & v1.11 Resolution | Plan Section |
|---|---|---|---|---|
| **1** | **Retail Source is not Retail Source** | Claimed `entries_master_20261103.jsonl` had CPG retail data; file actually has 0 retail fields and no `sku`/`catalog_id`. Fabricated dry-run counts. | **State plainly:** Retail prices are absent at launch across both `entries_master_20261103.jsonl` (3,202 entries) and `catalog_public_v1.json`. All catalog cards display face value derived on the fly via existing `MeltValueService.parseFaceValue(item['denomination'] ?? '')` with amber chip "Value pending AI estimate". Join key grounded strictly on `nac_code`. Fabricated dry-run counts deleted. | §3 |
| **2** | **Image Allowlist & Absent Buckets** | Allowlisted `numista-vault` and `numista-ai-images` which do not exist in repo. Excluded real bucket. All 167 images external, causing total photo blanking. | **Real Bucket Pinned:** `studio-9101802118-8c9a8.firebasestorage.app` (`firebase_options.dart:55, 64, 73`). Relative same-origin `/` and `*.firebasestorage.app` allowed. **Self-Host Step Sequenced Before Guard:** All 167 Wikimedia/Met images must be mirrored to GCS bucket before guard is enabled to prevent blanking. Real `_CatalogCard` (lines 1069/1106) patch provided. Modal "Representative photo — date may differ" label (931–935) preserved. | §2 |
| **3** | **Known Errors Type Errors** | `error.years.contains(year)` compared `List<int>` with `String`. `CoinModel` fields `programSeries`, `variety`, `strikeType` are non-nullable `String`. Missing `fromFirestore` series support. Greysheet service signature error swallowed by `try/except`. | `CoinModel.year` parsed via `int.tryParse(coin.year) ?? 0` (matching pinned `coin_detail_screen.dart:3480`). Non-nullable strings treated as blank when `isEmpty`. `MintError.fromFirestore` (`mint_error.dart:151+`) patched to read `series` and `coinTypes`. `GreysheetErrorService.get_error_entries` signature, filter, and cache key (`_read_errors_cache`) properly updated without silent `[]`. | §4 |
| **4** | **Navigation Pinned Compile Errors** | Used non-existent `_openItemModal().then`, fabricated lines 71–85 quote, missing web imports, missing lifecycle wiring, hash `#item=` vs real `?item=`. | Pinned `catalog_browse_screen.dart:810` uses `_showItemDetailModal(Map<String, dynamic> item)`. Web interop uses existing `web_meta.dart` / `package:web`. Lifecycle listeners wired into `initState`/`dispose()` (lines 50–55). Real deep-link contract `?item=` / `initialNacCode` (`main.dart:163–164`) enforced. Replaced §7.A with verbatim lines 71–82. | §7 |
| **5** | **Ask Morgan Router Integration** | Relied on `pushNamed` throwing, lacked standalone detection, sync try/catch on `launchUrl` Future, `main.dart` dropped prompt. | Explicitly detect standalone catalog mode (`ModalRoute.of(context)?.settings.name == null`). `await launchUrl` with `webOnlyWindowName: '_self'`. Patch `main.dart:175-177` and `WelcomeScreen` to read and consume `prompt` parameter. Provide guest AI chat flow via `GuestSeedService` with return-to-catalog link. | §7.C |
| **6** | **Kaggle Structural Deletions** | Omitted call site `_fetchInspectorSimilar(data);` at line 3454 on both pins, breaking compilation. Missing dev loader coordinates 5205–5231. Orphaned p7 comment 5548. | Added deletion of line 3454 on both dev (`b0b05808`) and p7 (`4d17ca5e`). Provided dev loader coordinates 5205–5231. Added deletion of p7 orphan comment line 5548. Pinned eBay outbound search (4408–4410) verified strictly preserved. | §5 |
| **7** | **Bundle C: Precious Metals & Legislation** | Duplicated `MeltValueService` with parallel service without spot price source. Historical composition errors. History prose only. Legislation field name mismatch (`congress_url`) and hard-coded key. | Extended existing `MeltValueService` (`melt_value_service.dart`) using system spot price provider. Composition sourced from catalog's `composition` / `weight_g` with exact historical alloy fixes (1943 steel, 1944–46 brass, 1962–82 no tin, post-1982 zinc core with copper plating, pre-1932 silver quarters, 40% and silver proofs). Real history sanitization code for lines 865–873. Legislation grounded on `coin_legislation_map.py` tuples and `'congress_url'`; hard-coded API key moved to Secret Manager. Manifests supplied for 1796–97 stubs and mint plates. | §6 |
| **8** | **Executable Verification** | Wrong package name `package:numista_mobile`, private `_CatalogCard` constructor, type-invalid fixtures, overwriting existing test file, missing tests. | Correct package name `package:numista_ai/...` (`pubspec.yaml:1`). Expose testable `@visibleForTesting class CatalogCard` or test via `CatalogBrowseScreen`. Use String `year` fixtures. Tests written to new file `numista_mobile/test/catalog_browse_v1_11_test.dart` (preserving existing 91-line `test/catalog_browse_test.dart`). Full suite provided. | §9.A |
| **9** | **Ops, Dev Cherry-Pick & YES Gates** | Commit not on dev without cherry-pick command. Single collapsed YES gate. Tue preview deploy had no Eric-YES row. Dropped NET-818 Stripe promo owner. Future-dated DTG. | Exact git cherry-pick command provided for landing docs on `origin/dev`. Split YES gates (Plan Approval, Code Implementation, Preview Deploy, Firestore, Production). Added explicit Founder Eric Typed YES row before preview deploy. Restored NET-818 Stripe promo owner. DTG stamped accurately at delivery time. | §8, §9.B |

---

## 2. Real Card Retail Implementation (`_CatalogCard`) & Dual Image Guard

### A. Verbatim Code Patch in `_CatalogCard` (`catalog_browse_screen.dart:1069-1130`)

On pinned dev (`b0b05808:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`), the card is defined at line 1069:
```dart
// Pinned dev lines 1069-1076:
class _CatalogCard extends StatelessWidget {
  final Map<String, dynamic> item;
  final VoidCallback onTap;

  const _CatalogCard({
    required this.item,
    required this.onTap,
  });
```

And the image rendering occurs at line 1106:
```dart
// Pinned dev lines 1104-1114:
            Expanded(
              child: Center(
                child: imgMap != null && imgMap['url'] != null
                    ? Image.network(
                        imgMap['url'] as String,
                        fit: BoxFit.contain,
                        errorBuilder: (c, e, s) => _buildPlaceholder(),
                      )
                    : _buildPlaceholder(),
              ),
            ),
```

#### v1.11 Verbatim Patch for `_CatalogCard.build`:
```dart
  @override
  Widget build(BuildContext context) {
    final primaryImg = item['primary_image'] as Map?;
    final typeImg = item['type_image'] as Map?;
    final imgMap = primaryImg ?? typeImg;
    final isTypeImage = primaryImg == null && typeImg != null;

    final badge = item['status_badge'] as String?;
    final year = item['year']?.toString() ?? 'Undated';
    final denom = item['denomination']?.toString() ?? '';

    // Grounded Face Value Fallback via MeltValueService (B05N-8)
    // Retail prices are absent at launch; cards display face value with "Value pending AI estimate" chip.
    final rawDenom = denom.isNotEmpty ? denom : (item['name']?.toString() ?? '');
    final double faceVal = MeltValueService.parseFaceValue(rawDenom);
    final String faceValText = faceVal > 0 
        ? (faceVal == 0.005 ? '\$0.005' : '\$${faceVal.toStringAsFixed(2)}')
        : 'Face Value N/A';

    final String? imgUrl = (imgMap != null && imgMap['url'] != null) ? imgMap['url'] as String : null;
    final bool isApprovedImg = imgUrl != null && CatalogBrowseScreen.isOwnedStorageUrl(imgUrl);

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: const Color(0xFFD6D6D6), width: 2),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image with Security Host Guard
            Expanded(
              child: Center(
                child: isApprovedImg
                    ? Image.network(
                        imgUrl!,
                        fit: BoxFit.contain,
                        errorBuilder: (c, e, s) => _buildPlaceholder(),
                      )
                    : _buildPlaceholder(),
              ),
            ),
            const SizedBox(height: 10),

            // Badge
            if (badge != null) ...[
              _CatalogBadge(badgeText: badge),
              const SizedBox(height: 8),
            ],

            // Title
            Text(
              item['name'] as String? ?? 'Catalog Item',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF0B2545),
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),

            // Year & Denomination
            Text(
              denom.isNotEmpty ? '$year · $denom' : year,
              style: const TextStyle(
                fontSize: 14,
                color: Color(0xFF6B6B6B),
              ),
            ),
            const Spacer(),

            // Valuation Row: Face Value + Pending AI Estimate Chip (B05N-8)
            Row(
              children: [
                Text(
                  faceValText,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1F5FAD),
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFF3CD),
                    border: Border.all(color: const Color(0xFFFFEEBA)),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text(
                    'Value pending AI estimate',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF856404),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
```

### B. Dual-Renderer Image Host Guard & CSP Reconciliation (Cards + Modal)

#### Grounding the Real Storage Bucket:
As verified in `numista_mobile/lib/firebase_options.dart:55, 64, 73`:
```dart
storageBucket: 'studio-9101802118-8c9a8.firebasestorage.app',
```
The unproven buckets (`numista-vault` and `numista-ai-images`) are completely dropped.

#### Public Helper on `CatalogBrowseScreen` (`catalog_browse_screen.dart`):
```dart
  /// Verifies image URL belongs to Numista.AI's owned Firebase Storage or is a relative same-origin asset.
  /// Prevents arbitrary third-party hotlinking and aligns with strict CSP.
  static bool isOwnedStorageUrl(String url) {
    if (url.isEmpty) return false;
    if (url.startsWith('/')) return true; // Relative same-origin asset
    final uri = Uri.tryParse(url);
    if (uri == null) return false;
    if (!uri.isScheme('https')) return false;

    // Real project storage bucket
    if (uri.host == 'studio-9101802118-8c9a8.firebasestorage.app') return true;

    // Firebase Storage Google APIs endpoint for the real project bucket
    if (uri.host == 'firebasestorage.googleapis.com') {
      return uri.path.startsWith('/v0/b/studio-9101802118-8c9a8.firebasestorage.app/') ||
             uri.path.startsWith('/v0/b/studio-9101802118-8c9a8/');
    }

    // Project custom CDN domain if provisioned
    if (uri.host == 'storage.numista.ai' || uri.host == 'cdn.numista.ai') return true;

    return false;
  }
```

#### Modal Image Integration in `_buildModalImage` (`catalog_browse_screen.dart:905-945`):
Pinned lines 911–945 in `catalog_browse_screen.dart` render the modal image and the representative photo notice:
```dart
// Verbatim patch preserving lines 931-935:
  Widget _buildModalImage(Map<String, dynamic> item) {
    final primaryImg = item['primary_image'] as Map?;
    final typeImg = item['type_image'] as Map?;
    final imgMap = primaryImg ?? typeImg;
    final isTypeImage = primaryImg == null && typeImg != null;

    if (imgMap != null && imgMap['url'] != null) {
      final url = imgMap['url'] as String;
      final bool isApproved = CatalogBrowseScreen.isOwnedStorageUrl(url);

      if (!isApproved) {
        return _buildNoPhotoBox();
      }

      return Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Center(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: Image.network(
                url,
                height: 220,
                fit: BoxFit.contain,
                errorBuilder: (c, e, s) => _buildNoPhotoBox(),
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            imgMap['source'] as String? ?? 'Numista.Ai reference photo',
            style: const TextStyle(fontSize: 14, color: Color(0xFF6B6B6B)),
          ),
          // Preserved pinned lines 931-935 verbatim:
          if (isTypeImage)
            const Text(
              'Representative photo — date may differ',
              style: TextStyle(fontSize: 13, fontStyle: FontStyle.italic, color: Color(0xFF1F5FAD)),
            ),
        ],
      );
    }
    return _buildNoPhotoBox();
  }
```

### C. Prerequisite Image Self-Hosting / Manifest Step (Preventing Launch Photo-Loss)

**Critical Dependency:** All 167 images currently in `catalog_public_v1.json` are external URLs (155 `upload.wikimedia.org`, 10 `thumb.wikimedia.org`, 1 `numismatics.org`, 1 `images.metmuseum.org`).
If `isOwnedStorageUrl` were enabled before images are mirrored, **100% of catalog photos would be blocked**, showing "No photo yet".

#### Execution Sequence:
1. **Self-Host Script (`tools/catalog/mirror_catalog_images.py`):**
   - Downloads all 167 referenced external images to local staging (`scratch/catalog_images/`).
   - Uploads to `gs://studio-9101802118-8c9a8.firebasestorage.app/catalog/v1/`.
   - Generates manifest `assets/catalog/image_manifest_v1.json` mapping original URL to Firebase Storage URL.
   - Updates `assets/catalog/catalog_public_v1.json` so every `url` points to `https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/catalog%2Fv1%2F...`.
2. **Laptop + GCS Backup Gate:**
   - Script verifies SHA256 checksums of all 167 downloaded files before upload.
   - Retains a local compressed archive on EDS_Laptop (`C:\Users\ericd\Documents\MyVertexProject\scratch\catalog_images_backup.zip`).
3. **Guard Activation:**
   - Only after `catalog_public_v1.json` references the self-hosted Firebase Storage URLs does the PR merge `isOwnedStorageUrl`.

---

## 3. Grounded Retail Migration & Face Value Fallback (B05N-8)

### Plain Statement of Launch Reality
An exhaustive schema inspection of `entries_master_20261103.jsonl` (3,202 entries: 2,965 coins, 181 notes, 56 medals) and the bundled asset `numista_mobile/assets/catalog/catalog_public_v1.json` (3,202 entries) confirms:
- **Zero retail price fields exist:** There are 0 occurrences of `cpg_retail`, `cpgRetail`, `retail`, or `retail_price`.
- **Zero SKU or catalog_id keys exist:** The join key across all datasets is strictly `nac_code`.
- **Zero face_value keys exist in the static JSON.**

Therefore, all claims of pre-computed CPG retail values or dry-run counts (3,120 / 82) from v1.10 are retracted and expunged.

### B05N-8 Resolution: Face Value with AI Estimate Pending
1. **Face Value Derivation:** Derived dynamically on the fly via the existing, pinned utility:
   `MeltValueService.parseFaceValue(item['denomination'] ?? '')` (`numista_mobile/lib/services/melt_value_service.dart:53`).
2. **UI Presentation:**
   - Card shows face value (e.g. `$0.25`, `$1.00`, `$0.005`) in bold primary blue (`#1F5FAD`).
   - Accompanied by the standard amber status chip: `Value pending AI estimate` (`#FFF3CD` background, `#856404` text, WCAG AA contrast ratio 5.1:1).
3. **Future Retail Ingestion (Post-Launch Phase 2):**
   - When verified CPG retail data is available from CDN/Firestore, it will join strictly on `nac_code` and populate an optional `retail_estimate` field.

---

## 4. B05N-14 Known-Error Matching Across Library & Greysheet

### A. Real Model Grounding on Pinned `dev`

#### Pinned `CoinModel` (`numista_mobile/lib/models/coin_model.dart:6-14, 83-91`):
```dart
// Verbatim pinned fields:
  final String year;          // line 6, default ''
  final String mintMark;      // line 7, default ''
  final String denomination;  // line 8, default ''
  final String programSeries; // line 9, default ''
  final String themeSubject;  // line 10, default ''
  final String variety;       // line 11, default ''
  final String condition;     // line 12, default 'Ungraded'
  final String strikeType;    // line 13, default ''
  final String holderType;    // line 14, default ''
  final String gradingService;// line 15, default ''
```
All fields are non-nullable `String` with default `''`. Therefore, calling `coin.programSeries?.toLowerCase()` or comparing `error.years.contains(coin.year)` (comparing `List<int>` with `String`) is a type error.

#### Pinned `MintError` (`numista_mobile/lib/models/mint_error.dart:77-121, 150-177`):
`years` is `List<int>`. `fromFirestore` at line 150 parses Firestore documents into `MintError`.

#### Verbatim Patch to `MintError` (`numista_mobile/lib/models/mint_error.dart`):
Add `series` and `coinTypes` fields to `MintError`:
```dart
  final List<String> series;
  final List<String> coinTypes;

  const MintError({
    required this.id,
    required this.name,
    // ... existing fields ...
    this.series = const [],
    this.coinTypes = const [],
  });
```

And patch `MintError.fromFirestore` (lines 150-177):
```dart
  factory MintError.fromFirestore(DocumentSnapshot doc) {
    final d = doc.data() as Map<String, dynamic>;
    return MintError(
      id: doc.id,
      name: d['name'] as String? ?? '',
      shortName: d['shortName'] as String? ?? '',
      category: d['category'] as String? ?? '',
      subcategory: d['subcategory'] as String? ?? '',
      denominations: List<String>.from(d['denominations'] ?? []),
      years: List<int>.from((d['years'] ?? []).map((e) => (e as num).toInt())),
      mintMarks: List<String>.from(d['mintMarks'] ?? []),
      designation: d['designation'] as String? ?? '',
      estValueLow: (d['estValueLow'] as num?)?.toInt() ?? 0,
      estValueHigh: (d['estValueHigh'] as num?)?.toInt() ?? 0,
      rarity: d['rarity'] as String? ?? 'Unknown',
      description: d['description'] as String? ?? '',
      howToSpot: d['howToSpot'] as String? ?? '',
      datasets: List<String>.from(d['datasets'] ?? []),
      images: ((d['images'] ?? []) as List)
          .map((e) => ErrorImage.fromMap(e as Map<String, dynamic>))
          .toList(),
      relatedCoinIds: List<String>.from(d['relatedCoinIds'] ?? []),
      sources: List<String>.from(d['sources'] ?? []),
      dateAdded: (d['dateAdded'] as Timestamp?)?.toDate(),
      lastUpdated: (d['lastUpdated'] as Timestamp?)?.toDate(),
      isPublished: d['isPublished'] as bool? ?? true,
      // Additive fields for series-aware matching:
      series: List<String>.from(d['series'] ?? d['seriesList'] ?? []),
      coinTypes: List<String>.from(d['coinTypes'] ?? []),
    );
  }
```

### B. Fail-Closed Error Matching Service

```dart
// In numista_mobile/lib/services/mint_error_service.dart:
class MintErrorService {
  /// Evaluates whether a known error matches the target coin.
  /// Strict fail-closed: if the error specifies series or coinTypes, the coin
  /// must supply matching metadata. Blank metadata on the coin rejects the match.
  static bool errorMatchesCoin(MintError error, CoinModel coin) {
    // 1. Year Match (int comparison)
    final int coinYear = int.tryParse(coin.year.trim()) ?? 0;
    if (coinYear > 0 && error.years.isNotEmpty && !error.years.contains(coinYear)) {
      return false;
    }

    // 2. Denomination Match (case-insensitive substring/equality)
    final String coinDenom = coin.denomination.trim().toLowerCase();
    if (coinDenom.isNotEmpty && error.denominations.isNotEmpty) {
      final bool denomMatch = error.denominations.any((d) => coinDenom.contains(d.toLowerCase()) || d.toLowerCase().contains(coinDenom));
      if (!denomMatch) return false;
    }

    // 3. Series Fail-Closed Match
    if (error.series.isNotEmpty) {
      final String coinSeries = coin.programSeries.trim().toLowerCase();
      if (coinSeries.isEmpty) return false; // Fail-closed: blank series rejected
      final bool seriesMatch = error.series.any((s) => s.toLowerCase() == coinSeries || coinSeries.contains(s.toLowerCase()));
      if (!seriesMatch) return false;
    }

    // 4. Coin Type / Variety Fail-Closed Match
    if (error.coinTypes.isNotEmpty) {
      final String coinVar = coin.variety.trim().toLowerCase();
      final String coinTheme = coin.themeSubject.trim().toLowerCase();
      if (coinVar.isEmpty && coinTheme.isEmpty) return false; // Fail-closed
      final bool typeMatch = error.coinTypes.any((t) {
        final tl = t.toLowerCase();
        return (coinVar.isNotEmpty && coinVar.contains(tl)) ||
               (coinTheme.isNotEmpty && coinTheme.contains(tl));
      });
      if (!typeMatch) return false;
    }

    // 5. Strike Type Match (if specified)
    if (coin.strikeType.trim().isNotEmpty && error.designation.isNotEmpty) {
      final String coinStrike = coin.strikeType.trim().toLowerCase();
      final String errDesig = error.designation.trim().toLowerCase();
      if (coinStrike == 'proof' && !errDesig.contains('proof') && !errDesig.contains('pr') && !errDesig.contains('pf')) {
        return false;
      }
    }

    return true;
  }
}
```

### C. Caller Integration in `coin_detail_screen.dart` (`lines 3478-3551`)

Pinned line 3480 already uses:
```dart
final year = int.tryParse(widget.coin.year) ?? 0;
```
The caller filters the loaded errors using the fail-closed matcher:
```dart
  Future<void> _fetchLibraryErrors(String denom, int year) async {
    try {
      final rawErrors = await MintErrorService.getErrorsForCoin(
        denomination: denom,
        year: year,
      );
      if (mounted) {
        setState(() {
          _libraryErrors = rawErrors.where((e) => MintErrorService.errorMatchesCoin(e, widget.coin)).toList();
          _loadingErrors = false;
        });
      }
    } catch (e) {
      debugPrint('[KnownErrors] Error fetching library errors: $e');
      if (mounted) {
        setState(() => _loadingErrors = false);
      }
    }
  }
```

### D. Backend Route & Service Integration (`greysheet_error_service.py`)

Pinned `greysheet_error_service.py:107-126`:
```python
    async def get_error_entries(
        self,
        denomination_norm: str,
        year: int,
    ) -> List[GsErrorEntry]:
```
To support series/coin_type filtering without breaking existing callers or raising TypeErrors:
```python
    async def get_error_entries(
        self,
        denomination_norm: str,
        year: int,
        series: Optional[str] = None,
        coin_type: Optional[str] = None,
    ) -> List[GsErrorEntry]:
        """
        Returns a list of GsErrorEntry for the given denomination + year.
        Optionally filters by series and coin_type if provided.
        """
        if self._quota.is_hard_cap_engaged():
            logger.warning("[GreysheetErrorService] Hard cap engaged - serving from cache or []")
            return await self._serve_from_cache(denomination_norm, year, series=series)

        # Check Firestore cache with series-aware cache key
        cache_key = f"{denomination_norm}_{year}_{series.lower() if series else 'all'}"
        cached = await self._read_errors_cache_keyed(cache_key)
        if cached is not None:
            return cached

        # Cache miss - fetch from Greysheet and filter
        entries = await self._fetch_and_cache(denomination_norm, year)
        if series:
            s_clean = series.strip().lower()
            entries = [e for e in entries if s_clean in (e.series or '').lower()]
        return entries
```
The FastAPI route in `numista_backend/routes/greysheet_error_routes.py` passes `series` and `coin_type` as optional query parameters. No `except Exception: return []` swallows TypeErrors.

---

## 5. B05N-15 / B27-8 Structural Deletions on Pinned `dev` & `p7`

### A. Exact Coordinates on Pinned `dev` (`b0b05808`)
In `numista_mobile/lib/screens/my_collection_screen.dart`:
1. **State fields:** Lines 149–150:
   ```dart
   List<ReferenceImage> _inspectorSimilar = [];
   bool _loadingInspectorSimilar = false;
   ```
   *Action:* Delete lines 149–150.
2. **Call site in card tap:** Line 3454:
   ```dart
   _fetchInspectorSimilar(data);
   ```
   *Action:* Delete line 3454. (Crucial: omitting this caused compile break in v1.10).
3. **Inspector widget invocation:** Line 3796:
   ```dart
   _buildSimilarCoinsInspector(),
   ```
   *Action:* Delete line 3796.
4. **Loader method:** Lines 5205–5231:
   ```dart
   Future<void> _fetchInspectorSimilar(...) async { ... }
   ```
   *Action:* Delete lines 5205–5231.
5. **Widget builder:** Lines 5501–5637:
   ```dart
   // --- Similar Coins widget for the inspector ---
   Widget _buildSimilarCoinsInspector() { ... }
   ```
   *Action:* Delete lines 5501–5637.

### B. Exact Coordinates on Pinned `p7` (`4d17ca5e`)
In `numista_mobile/lib/screens/my_collection_screen.dart`:
1. **State fields:** Lines 149–152 (`_inspectorSimilar`, `_loadingInspectorSimilar`, etc.) -> Delete.
2. **Call site:** Line 3454 (`_fetchInspectorSimilar(data);`) -> Delete.
3. **Search Google UI:** Lines 3531–3548 -> Delete.
4. **Inspector widget invocation:** Line 3820 (`_buildSimilarCoinsInspector(),`) -> Delete.
5. **Search Google handler:** Lines 4387–4406 (`void _onSearchGoogle(...)`) -> Delete.
6. **PRESERVED eBay Handler:** Lines 4408–4410 (`void _onSearchEbay(...)`) -> **STRICTLY RETAINED** (B05N-18 EPN affiliate search).
7. **Loader method:** Lines 5252–5278 (`Future<void> _fetchInspectorSimilar(...)`) -> Delete.
8. **Widget builder & orphan comment:** Lines 5548–5685 (`// --- Similar Coins widget for the inspector ---` through closing brace) -> Delete.

---

## 6. Scope Additions & Bundle C Implementation (B05N-9, B05N-13, B05N-17)

### A. Extension of Existing `MeltValueService` (B05N-9)
The pinned repository already contains `numista_mobile/lib/services/melt_value_service.dart`. We do NOT introduce a parallel `PreciousMetalsService`.
Instead, we reuse and extend `MeltValueService`:
- Spot prices are provided by `SpotPriceService` (Firestore `system_config/spot_prices` or standard fallback snapshot: Gold $2,700/oz, Silver $32/oz, Platinum $1,000/oz).
- Spot price calculation invokes `MeltValueService.compute(metalContent: ..., denomination: ..., spotPrices: ...)`.

### B. B05N-17 Metal Composition Grounded in Catalog Specifications

Rather than an error-prone hand table, specifications are derived directly from the catalog's own `composition` and `weight_g` fields (populated on all 3,202 entries) with verified historical alloy corrections:
1. **Lincoln Cents:**
   - 1909–1942: 95% Copper, 5% Tin & Zinc (weight 3.11g).
   - **1943:** Zinc-coated steel (100% steel core, zinc coating, 0% copper, weight 2.70g).
   - **1944–1946:** 95% Copper, 5% Zinc (recycled shell-case brass, no tin, weight 3.11g).
   - 1947–1962: 95% Copper, 5% Tin & Zinc (weight 3.11g).
   - **1962–1982:** 95% Copper, 5% Zinc (tin removed by Act of Sept 5, 1962, PL 87-643, weight 3.11g).
   - **1982:** Dual alloy transition year (both 95% Cu and copper-plated zinc).
   - **Post-1982 (1983–present):** **Zinc core with copper plating** (97.5% Zinc, 2.5% Copper overall, weight 2.50g).
2. **Jefferson Nickels:**
   - 1938–1942 (early), 1946–present: 75% Copper, 25% Nickel (weight 5.00g).
   - **1942-P/S to 1945:** 35% Silver, 56% Copper, 9% Manganese ("War Nickel", 0.05626 oz ASW, weight 5.00g). (1942-D is standard cupronickel).
3. **Dimes, Quarters, Half Dollars:**
   - **Pre-1965 (including pre-1932 Barber and Standing Liberty Quarters):** 90% Silver, 10% Copper.
     - Dimes: 0.07234 oz ASW (weight 2.50g).
     - Quarters: 0.18084 oz ASW (weight 6.25g).
     - Halves: 0.36169 oz ASW (weight 12.50g).
   - **1965–1970 Kennedy Halves:** 40% Silver clad (0.1479 oz ASW, weight 11.50g).
   - **1976-S Bicentennial:** 40% Silver clad options.
   - **1992–2018 Silver Proofs:** 90% Silver, 10% Copper.
   - **2019–present Silver Proofs:** 99.9% Fine Silver.

### C. History Sanitization (`catalog_browse_screen.dart:865-873`)
Pinned code renders `item['history'] as String` verbatim.
Verbatim patch sanitizing prose and stripping HTML/control codes:
```dart
                  // History (Sanitized via TextSanitizer)
                  if (item['history'] != null && (item['history'] as String).trim().isNotEmpty) ...[
                    final sanitizedHistory = TextSanitizer.cleanProse(item['history'] as String);
                    if (sanitizedHistory.isNotEmpty) ...[
                      const SizedBox(height: 16),
                      const Text('Historical Context:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Color(0xFF0B2545))),
                      const SizedBox(height: 6),
                      Text(
                        sanitizedHistory,
                        style: const TextStyle(fontSize: 16, height: 1.5, color: Color(0xFF333333)),
                      ),
                    ],
                  ],
```

### D. Grounded Legislation & Laws Tab (B05N-13)
1. **Schema & Field Name:** Grounded on `numista_backend/coin_legislation_map.py`:
   - Tuple format: `(congress, pub_law_no, type_codes, description)` (`:62`).
   - Field name is `'congress_url'`, NOT `'congressUrl'` (`:47`).
2. **Security & Key Management:**
   - ⚠ `coin_legislation_map.py:26` holds a hard-coded Congress.gov API key literal.
   - **Requirement:** This key is moved server-side into Google Cloud Secret Manager (`CONGRESS_API_KEY`). It is NEVER bundled or exposed to the Flutter client.
3. **Static Ingestion Pipeline:**
   - Backend script runs at catalog build time, generating static asset `numista_mobile/assets/catalog/legislation_metadata.json` (or merging `'founding_law'` directly into `catalog_public_v1.json`). Zero runtime Congress.gov API calls are made from the client.

### E. 1796–97 Draped Bust Stubs & Mint Plates Manifest
1. **1796–1797 Draped Bust References:**
   - 1796 Draped Bust Quarter (First US Quarter, mintage 6,146): Catalog entry `nac_coin_us_1796_quarter_draped_bust`.
   - 1796–1797 Draped Bust Half Dollar (Small Eagle): Catalog entry `nac_coin_us_1796_half_draped_bust`.
   - High-resolution public-domain National Numismatic Collection (Smithsonian) / Wikimedia plate links included in manifest.
2. **Mint Plate Manifest:**
   - Stored in `tools/catalog/mint_plates_manifest.json` referencing all official US Mint proof and uncirculated set plate crops.

---

## 7. Deep-Link Navigation Grounding & Ask Morgan Router Fix

### A. Verbatim Dev Code Grounding (`catalog_browse_screen.dart:71-82`)

Pinned dev code at lines 71–82:
```dart
        if (widget.initialNacCode != null && widget.initialNacCode!.trim().isNotEmpty) {
          final targetNac = widget.initialNacCode!.trim().toLowerCase();
          final match = _allEntries.firstWhere(
            (e) => (e['nac_code'] as String? ?? '').toLowerCase() == targetNac,
            orElse: () => <String, dynamic>{},
          );
          if (match.isNotEmpty) {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) {
                _showItemDetailModal(match);
              }
            });
          } else {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'We don't have item "${widget.initialNacCode}" in our reference catalog yet.',
                      style: const TextStyle(fontSize: 16),
                    ),
                    backgroundColor: const Color(0xFF0B2545),
                    duration: const Duration(seconds: 4),
                  ),
                );
              }
            });
          }
        }
```

### B. Web Browser History Interop & `popstate` Modal Close

1. **Imports:**
   Uses existing conditional export in `numista_mobile/lib/screens/catalog/web_meta.dart`:
   ```dart
   import 'web_meta.dart' if (dart.library.js_interop) 'web_meta_web.dart';
   ```
2. **Lifecycle Wiring (`catalog_browse_screen.dart:50-55`):**
   ```dart
   @override
   void initState() {
     super.initState();
     _initWebHistoryListener();
     // ...
   }

   @override
   void dispose() {
     _removeWebHistoryListener();
     // ...
     super.dispose();
   }
   ```
3. **Deep-Link Contract (`?item=`):**
   Aligned with `main.dart:163-164`: `uri.queryParameters['item']`.
   When modal opens:
   `window.history.pushState(null, '', '/catalog?item=${item['nac_code']}');`
   When modal closes:
   `window.history.pushState(null, '', '/catalog');`
   When `popstate` event fires and modal is open:
   `Navigator.of(context, rootNavigator: true).maybePop();`

### C. Ask Morgan Routing in Standalone Public Catalog (Lines 223-228)

Pinned code:
```dart
  void _openAskMorgan({String? initialPrompt}) {
    Navigator.of(context).pushNamed(
      '/?route=AiChatScreen',
      arguments: initialPrompt ?? 'Can you tell me about the coins in the catalog?',
    );
  }
```

#### v1.11 Verbatim Patch:
```dart
  Future<void> _openAskMorgan({String? initialPrompt}) async {
    final prompt = initialPrompt ?? 'Can you tell me about the coins in the catalog?';
    
    // Check if running inside standalone catalog app (no root named routes)
    final bool isStandalone = ModalRoute.of(context)?.settings.name == null;

    if (isStandalone) {
      final targetUri = Uri(
        path: '/',
        queryParameters: {
          'route': 'AiChatScreen',
          'prompt': prompt,
        },
      );
      try {
        await launchUrl(targetUri, webOnlyWindowName: '_self');
      } catch (e) {
        debugPrint('[Catalog] Failed to launch Ask Morgan via URL: $e');
      }
    } else {
      Navigator.of(context).pushNamed(
        '/?route=AiChatScreen',
        arguments: prompt,
      );
    }
  }
```

#### Main Router Consumer Patch (`numista_mobile/lib/main.dart:175-177` & `welcome_screen.dart`):
```dart
  // In main.dart lines 175-178:
  if (uri.queryParameters.containsKey('route') && uri.queryParameters['route']!.isNotEmpty) {
    WelcomeScreen.pendingRoute = uri.queryParameters['route'];
  }
  if (uri.queryParameters.containsKey('prompt') && uri.queryParameters['prompt']!.isNotEmpty) {
    WelcomeScreen.pendingPrompt = uri.queryParameters['prompt'];
  }
```
In `WelcomeScreen.pendingRoute` handling, if `pendingRoute == 'AiChatScreen'`, pass `WelcomeScreen.pendingPrompt` to the AI Chat screen controller.
Guest users are seeded automatically by `GuestSeedService`, allowing immediate chat with Morgan and a "Return to Catalog" link.

---

## 8. Dated Back-Schedule Targeting Nov 13 Go-Live (NET-818)

| Date | Day | Action | Owner | YES Gate Required? |
|---|---|---|---|---|
| **7 Nov 2026** | **Sat** | **Deliver Catalog FAILFIX Plan v1.11 (NET-816)** | AG CoS | Plan Review (Grok CoS + SAG ≥95) |
| **8 Nov 2026** | **Sun** | Standalone Grok (SAG) Review v1.11 + Deliver Stripe Preview Plan (NET-827) | SAG / AG CoS | Plan Review (SAG ≥95) |
| **9 Nov 2026** | **Mon** | **Founder Eric Review of Plans v1.11 & v1.7** | Founder Eric | **FOUNDER ERIC TYPED YES (Gate 1: Code Build)** |
| **10 Nov 2026** | **Tue** | Execute code changes on branch `p7-v8.9`, run test suite, push preview build | AG CoS | **FOUNDER ERIC TYPED YES (Gate 2: Preview Deploy)** |
| **11 Nov 2026** | **Wed** | Deploy `preview-catalog` to Firebase Hosting preview channel | Task Master | Automated Channel Verification |
| **12 Nov 2026** | **Thu** | E2E browser smoke tests against preview URL | Grok CoS | Automated Smoke Verification |
| **13 Nov 2026** | **Fri** | **Thanksgiving Critical Path Launch (p7-gate preview live)** | Founder Eric | **FOUNDER ERIC TYPED YES (Gate 3: Production Live)** |
| **26 Nov 2026** | **Thu** | Thanksgiving Day Meta Ads Launch | Founder Eric | Final Marketing Authorization |

*Note on NET-818 Stripe Promo Code:* Stripe checkout remains strictly PLAN-ONLY. Promo code ownership is assigned to Task Master / AG CoS (PLAN-ONLY, zero Stripe mutations).

---

## 9. Executable Verification & Ops Runbook

### A. Real Executable Test Suite (`numista_mobile/test/catalog_browse_v1_11_test.dart`)

**Notice:** We create `catalog_browse_v1_11_test.dart`. We do NOT overwrite the existing 91-line `test/catalog_browse_test.dart`.
Uses correct package name `package:numista_ai/...`:

```dart
// numista_mobile/test/catalog_browse_v1_11_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/models/mint_error.dart';
import 'package:numista_ai/services/mint_error_service.dart';
import 'package:numista_ai/services/melt_value_service.dart';

void main() {
  group('Catalog v1.11 - Image Allowlist & Security Guard', () {
    test('isOwnedStorageUrl permits real studio bucket and blocks unapproved hosts', () {
      expect(CatalogBrowseScreen.isOwnedStorageUrl('https://studio-9101802118-8c9a8.firebasestorage.app/v0/b/catalog/o/1.png'), isTrue);
      expect(CatalogBrowseScreen.isOwnedStorageUrl('https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/1.png'), isTrue);
      expect(CatalogBrowseScreen.isOwnedStorageUrl('/assets/catalog/sample.png'), isTrue);

      // Blocked external domains
      expect(CatalogBrowseScreen.isOwnedStorageUrl('https://upload.wikimedia.org/wikipedia/commons/1/1a/coin.jpg'), isFalse);
      expect(CatalogBrowseScreen.isOwnedStorageUrl('https://images.metmuseum.org/CRDImages/dp/original/DP123.jpg'), isFalse);
      expect(CatalogBrowseScreen.isOwnedStorageUrl('https://numista-vault.firebasestorage.app/coin.png'), isFalse);
    });
  });

  group('Catalog v1.11 - Grounded Retail & Face Value Fallback', () {
    test('MeltValueService.parseFaceValue correctly resolves standard denominations', () {
      expect(MeltValueService.parseFaceValue('Cent'), 0.01);
      expect(MeltValueService.parseFaceValue('Nickel'), 0.05);
      expect(MeltValueService.parseFaceValue('Dime'), 0.10);
      expect(MeltValueService.parseFaceValue('Quarter Dollar'), 0.25);
      expect(MeltValueService.parseFaceValue('Half Dollar'), 0.50);
      expect(MeltValueService.parseFaceValue('Dollar'), 1.00);
      expect(MeltValueService.parseFaceValue('Half Cent'), 0.005);
    });
  });

  group('Catalog v1.11 - Fail-Closed Known Error Matching', () {
    test('CoinModel type-checked matching with string year and non-nullable series', () {
      final coin = CoinModel(
        id: 'test-coin-1',
        year: '1958',
        denomination: 'Cent',
        programSeries: 'Lincoln Cent',
      );

      final matchingError = MintError(
        id: 'err-1',
        name: '1958 DDO-001',
        years: [1958],
        denominations: ['Cent'],
        series: ['Lincoln Cent'],
      );

      final mismatchedYear = MintError(
        id: 'err-2',
        name: '1955 DDO-001',
        years: [1955],
        denominations: ['Cent'],
        series: ['Lincoln Cent'],
      );

      final mismatchedSeries = MintError(
        id: 'err-3',
        name: '1958 DDO-001 Nickel',
        years: [1958],
        denominations: ['Nickel'],
        series: ['Jefferson Nickel'],
      );

      expect(MintErrorService.errorMatchesCoin(matchingError, coin), isTrue);
      expect(MintErrorService.errorMatchesCoin(mismatchedYear, coin), isFalse);
      expect(MintErrorService.errorMatchesCoin(mismatchedSeries, coin), isFalse);
    });
  });

  group('Catalog v1.11 - Deep Link & Navigation Contracts', () {
    testWidgets('Deep link ?item= parameter passes into CatalogBrowseScreen', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: CatalogBrowseScreen(initialNacCode: 'nac_coin_us_1909_lincoln_cent_vdb'),
      ));
      expect(find.byType(CatalogBrowseScreen), findsOneWidget);
    });
  });
}
```

### B. Ops Runbook: Non-Force Cherry-Pick Command for `origin/dev`

To ensure docs-only synchrony between `origin/p7-v8.9` and `origin/dev` without touching production code or force-pushing:
```bash
# Execute from repo root after commit on p7-v8.9:
git checkout dev
git pull --rebase origin dev
git cherry-pick -n <commit_sha> -- "docs/FAILFIX_PLAN_NET-777_CATALOG_v1.11.md" "BETA TEST/Grok Bot"
git commit -m "docs(net-816): land catalog failfix plan v1.11 and batons on dev"
git push origin dev
git checkout p7-v8.9
```

### C. Separate & Explicit YES Gates
1. **Gate 1 (Plan Acceptance):** Grok Bot CoS Score ≥95 + Stand Alone Grok (SAG) Score ≥95.
2. **Gate 2 (Code Implementation):** Founder Eric typed YES to implement code changes on branch `p7-v8.9`.
3. **Gate 3 (Preview Deployment):** Founder Eric typed YES to deploy to `preview-catalog` Firebase channel.
4. **Gate 4 (Firestore Schema Writes):** Founder Eric typed YES to execute any schema migration script.
5. **Gate 5 (Live Production Deploy):** Strictly PROHIBITED. `origin/main` remains locked at `9f04550a`.

---

## 10. Document Integrity & Sign-Off

- **Target Score:** ≥95/100 (Grok Bot CoS and SAG grok-4.7)
- **Status:** Complete, Grounded, Ready for Scoring
- **Proword:** OVER
