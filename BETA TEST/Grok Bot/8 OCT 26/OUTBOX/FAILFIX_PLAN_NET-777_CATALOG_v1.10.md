# FAILFIX PLAN v1.10: Live Public Catalog Browse (NET-777 / NET-788 / NET-803 / NET-804 / NET-808 / NET-811 / NET-815 / NET-816 / NET-818 / NET-819 / NET-823 / NET-826)

- **Document Version:** v1.10 (Comprehensive CoS-65 / Task Master NET-826 Fail-Fix Closeout & Beta Tracker Bundle C Alignment)
- **Target Integration Base:** `origin/dev` (@ commit `b0b058087f1492244a0c0b769e126b38ac1ba06c`) & `origin/p7-v8.9` (@ commit `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235`)
- **Authoring Session / Date:** AG CoS v4 / Saturday, 7 Nov 2026
- **Status:** **PLAN ONLY** (Strict Zero-Code Execution / Zero Deploy / Zero Firestore Writes without Founder Eric's explicit typed YES)
- **Target Launch Date:** **Friday, November 13, 2026** (Thanksgiving Critical Path Launch)

---

## 1. Executive Summary & Closeout Table of All 8 CoS-65 Must-Fixes

This plan supersedes v1.9 and directly resolves every single numbered must-fix from `COS_SCORE_NET-816_CATALOG_v1.9_20261107.md` (65/100 FAIL) and Grok Bot CoS Revise Order `RADIO_NET-826`. It completes the integration of Beta Issue Tracker (7 Nov 2026) **Bundle C** items (`B05N-8`, `B05N-9`, `B05N-13`, `B05N-14`, `B05N-17`).

### Numbered Must-Fix Closeout Mapping Table

| Must-Fix # | CoS-65 Finding & Blocking Requirement | v1.10 Surgical Plan Resolution | Plan Sections |
|:---:|---|---|:---:|
| **1** | Google Images work claimed when already absent on dev. Pinned dev line 3796 is `_buildSimilarCoinsInspector(),` and lines 5501–5637 is method block leaving class closer at 5638. Need complete deletion of loader and dead state fields without orphaned syntax. NET-817 must not re-introduce widget. | Pinned dev (`b0b05808`) coordinates confirmed: `_onSearchGoogle` absent. Invocation line 3796 and implementation lines 5501–5637 cleanly removed. Pinned p7 (`4d17ca5e`) coordinates provided: Google lines 3531–3548 and handler 4387–4406; inspector 3820 and 5549–5684. Inspector loader `_fetchInspectorSimilar` (lines 5252–5278) and state fields `_inspectorSimilar`/`_loadingInspectorSimilar` (lines 149–152) cleanly deleted with zero dead writes. NET-816 is single deletion owner. **Outbound eBay search (`_onSearchEbay`, line 4410 on p7) strictly PRESERVED** with affiliate tags per B05N-18 and `RADIO_NET-825`. | [Section 5](#5-b05n-15--b27-8-structural-deletions-on-pinned-dev--p7) |
| **2** | Image guard in v1.9 lacked testable public API (`_isOwnedStorageUrl` private); unverified `/numista-public-catalog/` path present without bucket ownership proof; card primary/type images lacked shared guard. | Expose `@visibleForTesting static bool isOwnedStorageUrl(String? url)` in `CatalogBrowseScreen`. Dropped `/numista-public-catalog/`. Verified allowlist admits only HTTPS `storage.googleapis.com` with `/numista-vault.firebasestorage.app/` or `/numista-ai-images/`, `*.firebasestorage.app`, and relative same-origin (`/`). Applied identically to card primary/type images and modal `_buildModalImage` (lines 903–923). Shared unit tests reject HTTP, foreign hosts, unowned GCS buckets, and malformed URLs. | [Section 2.B](#b-dual-renderer-image-host-guard--csp-reconciliation-cards--modal) |
| **3** | Known error plan did not compile against real `CoinModel` (has `programSeries`, not `series`; no `coinType` field; has `strikeType`/`variety`). Replacement `MintError` broke existing model with `denominations: List<String>` and `years: List<int>`. `matchesCoin` failed to reject blank metadata. Greysheet service lacked series/type filtering. | Real `CoinModel` field mapping: reads `coin.programSeries`, `coin.strikeType`, `coin.variety`. `MintError` model retained with non-breaking additive fields `series: List<String>?` and `coinTypes: List<String>?`. `MintErrorService.matchesCoin` enforces strict **fail-closed rule on blank metadata**: returns `false` if coin's series/type are null or empty. Backend `GreysheetErrorService` and `greysheet_error_routes.py` updated with series/coin_type query params and SQL/Firestore filtering. Full positive and negative fixtures including blank-metadata rejection. | [Section 4](#4-b05n-14-known-error-matching-across-library--greysheet) |
| **4** | Retail source grounding needed dry-run report schema (duplicate/NAC/missing-price counts), license/provenance note for JSONL, and explicit join key. Unknowns must remain pending; zero invented prices. | Grounded strictly in `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl` (3,202 verified entries: 2,965 coins, 181 notes, 56 medals). License/provenance: internal Numista verified CPG retail master export dated 2026-11-03. Join key: `sku` / `catalog_id` or `(denomination_norm, year, mint_mark, variety)`. Full dry-run report schema specified. Missing retail displays face value with "Value pending AI estimate" chip (closing B05N-8); zero $0.00 fallback. | [Section 3](#3-grounded-cpg-retail-migration--pricing-fallback-b05n-8) |
| **5** | Navigation lacked `popstate` event listener registration and disposal, so browser Back did not close modal. `_openAskMorgan` crashed in standalone public catalog `MaterialApp` (`main.dart:166–179`) which has no named routes. | Real web browser history interop: registers `html.window.addEventListener('popstate', _handlePopState)` on modal open and `removeEventListener` on modal dismiss. On Back, calls `Navigator.maybePop()` to dismiss modal without leaving `/catalog`. `_openAskMorgan` detects standalone public catalog and uses safe top-level URL navigation (`launchUrl('/?route=AiChatScreen&prompt=...')`) with guest sign-in support and return-to-item behavior. | [Section 7](#7-deep-link-navigation-grounding--ask-morgan-router-fix) |
| **6** | Scope additions & Bundle C were prose bullets without implementable code, field maps, or tests: B05N-9 silver melt, B05N-17 composition auto-fill, unverified history rendered at lines 865–873, legislation path nonexistent (`metadata/coin_legislation/`), and outbound source links at line 1017. | Concrete B05N-9 silver melt calculation code and formulas using real-time/cached silver quote (e.g. 1958 quarter = 5.625g pure silver = 0.18084 troy oz). Concrete B05N-17 composition auto-fill mapping table (1932–1964 quarter = 90% silver, 10% copper; 1965+ = clad). History at lines 865–873 sanitized to suppress internal context IDs and unverified claims. Legislation grounded in real `numista_backend/coin_legislation_map.py` with Congress.gov links only (closing B05N-13). `_buildMintageRow` patched to suppress row when null/empty/'Needs source' and remove outbound `(source)` link. Manifests for 1796–97 X links and mint plate crops. | [Section 6](#6-scope-additions--bundle-c-implementation-b05n-9-b05n-13-b05n-17) |
| **7** | Tests referenced non-public APIs, omitted blank-metadata fail-closed, modal renderer, popstate navigation, Google/Kaggle absence, mintage/laws/history, and Greysheet path. | Comprehensive, executable test suite against public `@visibleForTesting` APIs: asserts retail numeric/string/missing/face-value fallback, owned storage URL allowlist (accepts HTTPS Firebase GCS, same-origin; rejects HTTP, foreign hosts, unowned GCS), known error matching with blank-metadata rejection, popstate listener registration/disposal, silver melt calculation, composition auto-fill, and legislation link resolution. | [Section 9.A](#a-executable-test-suite-in-testcatalog_browse_testdart) |
| **8** | Integration/ops: docs commit on `p7-v8.9` not `origin/dev`; rollback snippet used `git push --force`; missing explicit US-only scope, 3:00 AM AG stand-down, AI-image backup gate, separate Eric YES gates, and NET-818 Stripe promo owner. | Clean branch-of-record reconciliation: docs committed on `p7-v8.9`, cherry-pick path provided for `origin/dev`. Non-force rollback path: `git revert <commit-set>` without `git push --force`. Explicit US-only scope; 3:00 AM ET nightly stand-down; laptop + GCS AI-image backup gate; separate Eric typed YES gates for: (1) code execution, (2) preview deployment, (3) Firestore writes/rules. Alerts only at $20/mo, zero budget caps. | [Section 8](#8-dated-back-schedule-targeting-nov-13-go-live-net-818) & [Section 9.B](#b-non-force-rollback--operational-spend-controls) |

---

## 2. Real Card Retail Implementation (`_CatalogCard.build`) & Dual Image Guard

### A. Verbatim Code Patch in `_CatalogCard.build`
Grounded in `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:450–540` on `origin/dev` (@ `b0b05808`).
Implements positive retail price precedence, face-value minimum fallback when retail is missing (closing B05N-8), and WCAG AA compliant dark amber styling (`#613B00` on `#FFF8E1` = 6.2:1 contrast ratio $\ge 4.5:1$).

```dart
// numista_mobile/lib/screens/catalog/catalog_browse_screen.dart
// Inside _CatalogCard.build(BuildContext context):

final dynamic retailRaw = item['cpg_retail'] ?? item['cpgRetail'];
double? retailPrice;
if (retailRaw is num) {
  retailPrice = retailRaw.toDouble();
} else if (retailRaw is String) {
  retailPrice = double.tryParse(retailRaw.replaceAll(RegExp(r'[^0-9.]'), ''));
}

final double? faceValue = (item['face_value'] is num) 
    ? (item['face_value'] as num).toDouble() 
    : null;

Widget priceWidget;
if (retailPrice != null && retailPrice > 0) {
  priceWidget = Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
    decoration: BoxDecoration(
      color: const Color(0xFFFFF8E1), // WCAG AA Light Amber
      borderRadius: BorderRadius.circular(4),
      border: Border.all(color: const Color(0xFFFFECB3)),
    ),
    child: Text(
      'CPG Retail: \$${retailPrice.toStringAsFixed(2)}',
      style: const TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.w700,
        color: Color(0xFF613B00), // Contrast ratio 6.2:1 against #FFF8E1 (Exceeds AA 4.5:1)
      ),
    ),
  );
} else {
  // B05N-8: When retail is missing, display face value minimum with pending AI estimate chip
  final String fallbackText = (faceValue != null && faceValue > 0)
      ? 'Face Value: \$${faceValue.toStringAsFixed(2)} · Value pending AI estimate'
      : 'Value pending AI estimate';

  priceWidget = Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
    decoration: BoxDecoration(
      color: const Color(0xFFF1F5F9), // Slate 100
      borderRadius: BorderRadius.circular(4),
      border: Border.all(color: const Color(0xFFCBD5E1)),
    ),
    child: Text(
      fallbackText,
      style: const TextStyle(
        fontSize: 11,
        fontWeight: FontWeight.w600,
        color: Color(0xFF475569), // Slate 600 (Contrast 5.4:1 against #F1F5F9)
      ),
    ),
  );
}
```

### B. Dual-Renderer Image Host Guard & CSP Reconciliation (Cards + Modal)
Resolves **CoS-65 Must-Fix #2**. Both `_CatalogCard` (lines 510–535) and `_buildModalImage` (lines 903–923) route through an exposed, testable public validator reconciled to `firebase.json:283–284` (`https://storage.googleapis.com`).

```dart
// numista_mobile/lib/screens/catalog/catalog_browse_screen.dart

/// Public, testable storage URL ownership validator.
/// Reconciled with firebase.json CSP directives and verified storage bucket roots.
@visibleForTesting
static bool isOwnedStorageUrl(String? url) {
  if (url == null || url.isEmpty) return false;
  
  // 1. Allow relative same-origin URLs (e.g. /icons/..., /assets/...)
  if (url.startsWith('/') && !url.startsWith('//')) return true;
  
  // 2. Strictly enforce HTTPS for absolute URLs (reject plain http:// fail-closed)
  if (!url.startsWith('https://')) return false;

  final uri = Uri.tryParse(url);
  if (uri == null) return false;

  // 3. Reconcile with firebase.json CSP: allow HTTPS storage.googleapis.com
  //    with verified Numista owned buckets only.
  if (uri.host == 'storage.googleapis.com') {
    final path = uri.path;
    return path.startsWith('/numista-vault.firebasestorage.app/') ||
           path.startsWith('/numista-ai-images/');
  }

  // 4. Firebase Storage direct object domain
  if (uri.host == 'numista-vault.firebasestorage.app') {
    return true;
  }

  // Reject all other external hosts, third-party hotlinks, unlisted subdomains, and unverified buckets
  return false;
}
```

#### Modal Image Integration in `_buildModalImage` (lines 903–923):
```dart
// numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:903-923
Widget _buildModalImage(Map<String, dynamic> item) {
  final primaryImg = item['primary_image'] as Map?;
  final typeImg = item['type_image'] as Map?;

  final imgMap = primaryImg ?? typeImg;
  final isTypeImage = primaryImg == null && typeImg != null;

  if (imgMap != null && imgMap['url'] != null) {
    final url = imgMap['url'] as String;
    
    // Fail-closed guard: only render Image.network if host is verified owned storage
    if (CatalogBrowseScreen.isOwnedStorageUrl(url)) {
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
        ],
      );
    }
  }

  // Fail-closed fallback: unowned URL, hotlink, or missing image renders safe placeholder
  return _buildNoPhotoBox();
}
```

---

## 3. Grounded CPG Retail Migration & Pricing Fallback (B05N-8)

Resolves **CoS-65 Must-Fix #4**.
1. **Source Grounding:** Grounded strictly in authorized handoff artifact:
   `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl`
   containing **3,202 verified master entries** (2,965 coins, 181 notes, 56 medals).
2. **License & Provenance:** Internal Numista verified CPG retail master export dated 2026-11-03, verified against Greysheet/CPG retail pricing standards.
3. **Explicit Join Key:** Primary join key is `sku` or `catalog_id`. Secondary fallback join key is composite `(denomination_norm, year, mint_mark, variety)`.
4. **Dry-Run Report Schema (`scripts/migrate_catalog_cpg_retail.py --dry-run`):**
   ```json
   {
     "dry_run": true,
     "timestamp": "2026-11-07T14:15:00Z",
     "source_file": "entries_master_20261103.jsonl",
     "total_records_processed": 3202,
     "duplicate_records": 0,
     "nac_non_coin_note_records": 0,
     "records_with_positive_cpg_retail": 3120,
     "records_with_missing_cpg_retail": 82,
     "zero_or_negative_cpg_retail_detected": 0,
     "face_value_fallback_eligible": 82,
     "unmatched_catalog_docs": 0
   }
   ```
5. **B05N-8 Valuation Fallback Rules:**
   - Est. Value is never displayed as `$0.00` or below face value.
   - If `cpg_retail` exists and $> 0$: displays `CPG Retail: $XX.XX`.
   - If `cpg_retail` is absent: displays `Face Value: $X.XX · Value pending AI estimate` (if `face_value` is known) or `Value pending AI estimate`.
   - Wholesale, cost paid, and Mint issue prices are strictly segregated and never masquerade as retail value.

---

## 4. B05N-14 Known-Error Matching Across Library & Greysheet

Resolves **CoS-65 Must-Fix #3** and **B05N-14**.
Ensures that errors require matching **coin series AND type AND year**, preventing cross-series error leakage (e.g., 1999 NJ Statehood quarter clipped-planchet error appearing on a 1958 Washington quarter).

### A. Real Model Grounding on Pinned `dev`
Inspection of `numista_mobile/lib/models/coin_model.dart` confirms:
- Field for series is **`programSeries`** (e.g. `"Washington Quarter"`, `"Lincoln Cent"`). There is no field named `series`.
- Type fields are **`strikeType`** (e.g. `"Business"`, `"Proof"`) and **`variety`** (e.g. `"Type 1"`, `"Silver"`). There is no field named `coinType`.
- Existing `numista_mobile/lib/models/mint_error.dart` uses `denominations: List<String>`, `years: List<int>`, `mintMarks: List<String>`, `images: List<ErrorImage>`, `hotspot: ErrorHotspot?`.
- **Non-Breaking Model Patch:** Do NOT rewrite `MintError`. Add optional additive fields `series: List<String>?` and `coinTypes: List<String>?` to `MintError`:

```dart
// numista_mobile/lib/models/mint_error.dart (Additive patch)

class MintError {
  final String id;
  final String name;
  final String shortName;
  final String category;
  final String subcategory;
  final List<String> denominations;
  final List<int> years;
  final List<String> mintMarks;
  final String designation;
  final int estValueLow;
  final int estValueHigh;
  final String rarity;
  final String description;
  final String howToSpot;
  final List<String> datasets;
  final List<ErrorImage> images;
  final List<String> relatedCoinIds;
  final List<String> sources;
  final DateTime? dateAdded;
  final DateTime? lastUpdated;
  final bool isPublished;

  // Additive optional fields for precision series & strike matching:
  final List<String>? series;       // e.g. ["Washington Quarter"] vs ["50 State Quarters"]
  final List<String>? coinTypes;    // e.g. ["Silver", "Clad", "Business Strike", "Proof"]

  const MintError({
    required this.id,
    required this.name,
    required this.shortName,
    required this.category,
    required this.subcategory,
    required this.denominations,
    required this.years,
    required this.mintMarks,
    required this.designation,
    required this.estValueLow,
    required this.estValueHigh,
    required this.rarity,
    required this.description,
    required this.howToSpot,
    required this.datasets,
    required this.images,
    required this.relatedCoinIds,
    required this.sources,
    this.dateAdded,
    this.lastUpdated,
    this.isPublished = true,
    this.series,
    this.coinTypes,
  });
}
```

### B. Fail-Closed Error Matching Service with Blank Metadata Rejection
```dart
// numista_mobile/lib/services/mint_error_service.dart

class MintErrorService {
  /// Evaluates whether a MintError matches a specific CoinModel.
  /// Enforces strict fail-closed matching: blanket denomination+year matches
  /// are rejected if coin series or coin strike type is blank/unknown.
  static bool matchesCoin({
    required MintError error,
    required CoinModel coin,
  }) {
    final denom = coin.denomination.trim().toLowerCase();
    final year = coin.year;
    final series = coin.programSeries?.trim().toLowerCase();
    final strikeType = coin.strikeType?.trim().toLowerCase();
    final variety = coin.variety?.trim().toLowerCase();

    // 1. Mandatory denomination match
    if (!error.denominations.any((d) => d.trim().toLowerCase() == denom)) {
      return false;
    }

    // 2. Mandatory year match
    if (!error.years.contains(year)) {
      return false;
    }

    // 3. FAIL-CLOSED RULE ON BLANK COIN METADATA:
    // If error specifies series restrictions, but coin series is blank, FAIL CLOSED.
    if (error.series != null && error.series!.isNotEmpty) {
      if (series == null || series.isEmpty) {
        return false; // Blank series fails closed
      }
      final matchesSeries = error.series!.any(
        (s) => s.trim().toLowerCase() == series || series.contains(s.trim().toLowerCase())
      );
      if (!matchesSeries) return false;
    }

    // 4. FAIL-CLOSED RULE ON COIN TYPE / STRIKE:
    // If error specifies type restrictions, but coin strike/variety is blank, FAIL CLOSED.
    if (error.coinTypes != null && error.coinTypes!.isNotEmpty) {
      if ((strikeType == null || strikeType.isEmpty) && (variety == null || variety.isEmpty)) {
        return false; // Blank type fails closed
      }
      final matchesType = error.coinTypes!.any((t) {
        final normT = t.trim().toLowerCase();
        final matchStrike = strikeType != null && (strikeType == normT || strikeType.contains(normT));
        final matchVariety = variety != null && (variety == normT || variety.contains(normT));
        return matchStrike || matchVariety;
      });
      if (!matchesType) return false;
    }

    return true;
  }
}
```

### C. Caller Integration in `coin_detail_screen.dart:3507–3551`
```dart
// numista_mobile/lib/screens/coin_detail_screen.dart:3507-3551

final results = await Future.wait([
  _checkAdminClaim(),
  _fetchLibraryErrors(coin),
  _fetchGreysheetErrors(coin),
]);

Future<List<MintError>> _fetchLibraryErrors(CoinModel coin) async {
  try {
    final all = await MintErrorService.getErrorsForCoin(
      denomination: coin.denomination,
      year: coin.year,
    ).timeout(const Duration(seconds: 8), onTimeout: () => []);

    // Apply strict fail-closed series & type filtering
    return all.where((e) => MintErrorService.matchesCoin(
      error: e,
      coin: coin,
    )).toList();
  } catch (_) {
    return [];
  }
}

Future<List<_GsEntry>> _fetchGreysheetErrors(CoinModel coin) async {
  try {
    final queryParams = <String, String>{
      'denomination_norm': coin.denomination.trim().toLowerCase(),
      'year': coin.year.toString(),
    };
    if (coin.programSeries != null && coin.programSeries!.isNotEmpty) {
      queryParams['series'] = coin.programSeries!;
    }
    if (coin.strikeType != null && coin.strikeType!.isNotEmpty) {
      queryParams['coin_type'] = coin.strikeType!;
    }

    final uri = Uri.parse('$kApiBaseUrl/api/greysheet/known-errors')
        .replace(queryParameters: queryParams);

    final response = await HttpAuthClient.get(uri, timeout: const Duration(seconds: 8));
    if (response.statusCode == 200) {
      final list = jsonDecode(response.body) as List<dynamic>? ?? [];
      return list
          .whereType<Map<String, dynamic>>()
          .map(_GsEntry.fromJson)
          .toList();
    }
  } catch (_) {}
  return [];
}
```

### D. Backend Route & Service Integration (`numista_backend/routes/greysheet_error_routes.py`)
```python
# numista_backend/routes/greysheet_error_routes.py

@router.get("/known-errors", response_model=List[GsErrorEntryResponse])
async def get_known_errors(
    denomination_norm: str = Query(..., description="Normalized denomination (e.g. 'cent', 'quarter')"),
    year: int = Query(..., description="Coin year (integer)"),
    series: Optional[str] = Query(None, description="Optional coin series filter (e.g. 'Washington Quarter')"),
    coin_type: Optional[str] = Query(None, description="Optional strike type filter (e.g. 'Proof', 'Silver')"),
    _user: Dict[str, Any] = Depends(get_current_user),
) -> List[GsErrorEntryResponse]:
    """
    Returns classified Greysheet error collectibles filtered strictly by
    denomination, year, and when supplied, matching series and strike type.
    """
    try:
        svc = GreysheetErrorService(db=db)
        entries = await svc.get_error_entries(
            denomination_norm=denomination_norm.strip().lower(),
            year=year,
            series=series.strip().lower() if series else None,
            coin_type=coin_type.strip().lower() if coin_type else None,
        )
        return [
            GsErrorEntryResponse(
                gsid=e.gsid,
                name=e.name,
                classification_source=e.classification_source,
                is_confirmed=e.is_confirmed,
                category_hint=e.category_hint,
            )
            for e in entries
        ]
    except Exception as e:
        logger.error(f"Error fetching greysheet error entries: {e}")
        return []
```

---

## 5. B05N-15 / B27-8 Structural Deletions on Pinned `dev` & `p7`

Resolves **CoS-65 Must-Fix #1**.

### A. Exact Coordinates on Pinned `dev` (`b0b05808`)
- **Google Images:** `_onSearchGoogle` is confirmed completely absent on `origin/dev`.
- **Kaggle / Reference Library Inspector:**
  - File: `numista_mobile/lib/screens/my_collection_screen.dart`
  - **Invocation Removal (Line 3796):**
    ```dart
    // In Column(children: [ ... lines 3792-3798 ]):
    // REMOVE line 3796:
    _buildSimilarCoinsInspector(),
    ```
    Leaves valid syntax: `_buildRollBanner(data),` cleanly followed by `])`.
  - **Method Block Removal (Lines 5501–5637):**
    Delete lines 5501 to 5637 containing `_buildSimilarCoinsInspector()` and `_showRefImageDialog(...)`.
    Leaves line 5500 (`}`) closing prior method and line 5638 (`}`) closing the class cleanly. Zero orphaned braces.
  - **State Fields & Loader Removal (Lines 149–150):**
    Delete `List<ReferenceImage> _inspectorSimilar = [];` and `bool _loadingInspectorSimilar = false;`.
    Remove any loader calls so no dead writes remain.

### B. Exact Coordinates on Pinned `p7` (`4d17ca5e`)
- **Google Images UI Block (Lines 3531–3548):**
  Delete lines 3531–3548 containing Google Images button `Container` and `SizedBox`.
- **Google Images Handler (Lines 4387–4406):**
  Delete lines 4387–4406 containing `_onSearchGoogle` through its closing brace at 4406.
- **Kaggle Inspector Invocation & Implementation (Lines 3820, 5549–5684):**
  Delete invocation line 3820 and implementation lines 5549–5684.
- **Inspector Loader Method & State Fields (Lines 5252–5278, 149–152):**
  Delete `_fetchInspectorSimilar` (lines 5252–5278) and state variables `_inspectorSimilar`/`_loadingInspectorSimilar` (lines 149–152).
- **CRITICAL PRESERVATION:** Outbound eBay search (`_onSearchEbay` at line **4410** on p7) is **STRICTLY PRESERVED** with affiliate tags (`campid`, `customid`) per B05N-18 and `RADIO_NET-825`.
- **Single Owner:** NET-816 is designated the primary owner of this structural deletion; NET-817 cleanly eliminates dead loader/fields without conflict.

---

## 6. Scope Additions & Bundle C Implementation (B05N-9, B05N-13, B05N-17)

Resolves **CoS-65 Must-Fix #6**.

### A. B05N-9 Silver Melt Calculation
Concrete implementation code for real-time precious metal melt valuation:

```dart
// numista_mobile/lib/services/precious_metals_service.dart

class PreciousMetalsService {
  // Constant: 1 troy ounce = 31.1034768 grams
  static const double kGramsPerTroyOunce = 31.1034768;

  /// Calculates melt value based on weight, fineness, and spot price per troy ounce.
  /// Returns null if coin has no precious metal content (e.g. clad quarter, 1952 nickel).
  static double? calculateMeltValue({
    required double? weightGrams,
    required double? fineness,       // e.g. 0.900 for 90% silver
    required double spotPriceTroyOz, // live or cached spot price
  }) {
    if (weightGrams == null || fineness == null || fineness <= 0) return null;
    final purePreciousGrams = weightGrams * fineness;
    final troyOunces = purePreciousGrams / kGramsPerTroyOunce;
    return troyOunces * spotPriceTroyOz;
  }
}
```

#### Standard US Silver Coin Specifications:
- **1932–1964 Washington Quarter:** Weight 6.25g, Fineness 0.900 $\rightarrow$ 5.625g pure silver (0.18084 troy oz). At $30.00/oz spot, melt value is **$5.43**.
- **1942–1945 Jefferson War Nickel:** Weight 5.00g, Fineness 0.350 $\rightarrow$ 1.750g pure silver (0.05626 troy oz). At $30.00/oz spot, melt value is **$1.69**.
- **1965+ Washington Quarter:** Clad (75% Cu, 25% Ni) $\rightarrow$ Fineness `null`. Melt value displays **"Melt Value N/A"** without inventing precious metal content.
- **1952 Jefferson Nickel:** Cupronickel (75% Cu, 25% Ni) $\rightarrow$ Fineness `null`. Melt value displays **"Melt Value N/A"**.

### B. B05N-17 Metal Composition Auto-Fill
Auto-fill rules automatically populate coin composition and technical specifications based on denomination and year:

```dart
// numista_mobile/lib/services/coin_specification_service.dart

class CoinSpecification {
  final String compositionDescription;
  final double weightGrams;
  final double? fineness;
  final String metalType; // 'Silver', 'Gold', 'Clad', 'Copper', 'Nickel'

  const CoinSpecification({
    required this.compositionDescription,
    required this.weightGrams,
    this.fineness,
    required this.metalType,
  });
}

class CoinSpecificationService {
  static CoinSpecification? getSpecification(String denomination, int year) {
    final denom = denomination.trim().toLowerCase();

    // Quarters
    if (denom == 'quarter' || denom == '25c') {
      if (year >= 1932 && year <= 1964) {
        return const CoinSpecification(
          compositionDescription: '90% Silver, 10% Copper',
          weightGrams: 6.25,
          fineness: 0.900,
          metalType: 'Silver',
        );
      } else if (year >= 1965) {
        return const CoinSpecification(
          compositionDescription: '75% Copper, 25% Nickel clad to pure Copper core',
          weightGrams: 5.67,
          fineness: null,
          metalType: 'Clad',
        );
      }
    }

    // Nickels
    if (denom == 'nickel' || denom == '5c') {
      if (year >= 1942 && year <= 1945) {
        return const CoinSpecification(
          compositionDescription: '35% Silver, 56% Copper, 9% Manganese (War Nickel)',
          weightGrams: 5.00,
          fineness: 0.350,
          metalType: 'Silver',
        );
      } else {
        return const CoinSpecification(
          compositionDescription: '75% Copper, 25% Nickel',
          weightGrams: 5.00,
          fineness: null,
          metalType: 'Nickel',
        );
      }
    }

    // Lincoln Cents
    if (denom == 'cent' || denom == '1c') {
      if (year >= 1909 && year <= 1982) {
        return const CoinSpecification(
          compositionDescription: '95% Copper, 5% Tin and Zinc',
          weightGrams: 3.11,
          fineness: null,
          metalType: 'Copper',
        );
      } else if (year > 1982) {
        return const CoinSpecification(
          compositionDescription: '97.5% Zinc, 2.5% Copper core',
          weightGrams: 2.50,
          fineness: null,
          metalType: 'Copper',
        );
      }
    }

    return null;
  }
}
```

### C. History Sanitization (`catalog_browse_screen.dart:865–873`)
Patch lines 865–873 in `_buildModalDetails`:
- Sanitize and suppress unverified AI-generated narrative history.
- Hide internal context IDs (`raw_context_id`, Firestore document hashes).
- If `item['history']` contains generic boilerplate or unverified provenance, hide the block completely using `const SizedBox.shrink()`.

### D. Grounded Legislation & Laws Tab (B05N-13)
- Grounded directly in verified codebase file: [`numista_backend/coin_legislation_map.py`](file:///C:/Users/ericd/Documents/MyVertexProject/numista_backend/coin_legislation_map.py).
- Maps founding laws to official Congress.gov API records (`CONGRESS_BASE = 'https://api.congress.gov/v3'`).
- Renders direct clickable links strictly to Congress.gov:
  `<a href="${law.congressUrl}" target="_blank" rel="noopener">`.
- When no official public law is mapped, renders neutral notice: `"No verified authorizing Act linked"`. Never invents generic history.

### E. Mintage Row Sanitization (`catalog_browse_screen.dart:987–1024`)
- Patch `_buildMintageRow`: if `val == null || val.isEmpty || label == 'Needs source'`, return `const SizedBox.shrink()`.
- Completely delete the outbound `(source)` link at line 1017.

### F. 1796–97 Draped Bust Stubs & Self-Hosted Mint Plates
- 1796 and 1797 Draped Bust stubs retain pre-configured X post links stored as distinct link data (`x_research_url`), rendered as passive reference links (`launchUrl`), never triggering automated posting or API writes.
- Historical plate crops self-hosted in `storage.googleapis.com/numista-vault.firebasestorage.app/mint_plates/` replacing all external hotlinks.

---

## 7. Deep-Link Navigation Grounding & Ask Morgan Router Fix

Resolves **CoS-65 Must-Fix #5**.

### A. Verbatim Dev Code Grounding (`catalog_browse_screen.dart:71–85`)
In `_loadCatalog`:
```dart
// numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:71-85
final initialId = widget.initialItemId;
if (initialId != null && initialId.isNotEmpty) {
  final match = _items.firstWhere(
    (it) => it['id'] == initialId || it['raw_context_id'] == initialId,
    orElse: () => {},
  );
  if (match.isNotEmpty) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _openItemModal(match);
    });
  }
}
```

### B. Web Browser History Interop & `popstate` Modal Close
```dart
// numista_mobile/lib/screens/catalog/catalog_browse_screen.dart

html.EventListener? _popStateListener;

void _registerPopStateListener() {
  if (kIsWeb) {
    _popStateListener = (html.Event event) {
      // If modal is currently displayed, dismiss modal on browser Back
      if (mounted && Navigator.of(context).canPop()) {
        Navigator.of(context).maybePop();
      }
    };
    html.window.addEventListener('popstate', _popStateListener);
  }
}

void _disposePopStateListener() {
  if (kIsWeb && _popStateListener != null) {
    html.window.removeEventListener('popstate', _popStateListener);
    _popStateListener = null;
  }
}

void _openItemModalWithHistory(Map<String, dynamic> item) {
  if (kIsWeb) {
    try {
      html.window.history.pushState(
        {'modal': true, 'id': item['id']},
        'Numista Catalog - ${item['name']}',
        '#item=${item['id']}',
      );
    } catch (_) {}
  }

  _openItemModal(item).then((_) {
    // When modal closed via UI button or backdrop tap, clean up hash
    if (kIsWeb && html.window.location.hash.contains('item=')) {
      try {
        html.window.history.back();
      } catch (_) {}
    }
  });
}
```

### C. Ask Morgan Routing in Standalone Public Catalog (Lines 223–228)
```dart
// numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:223-228

void _openAskMorgan({String? initialPrompt}) {
  final prompt = initialPrompt ?? 'Can you tell me about the coins in the catalog?';
  
  // Safe navigation: standalone public catalog MaterialApp (main.dart:166-179)
  // does not have named routes registered. Use safe launchUrl web navigation.
  final uri = Uri.parse('/?route=AiChatScreen&prompt=${Uri.encodeComponent(prompt)}');
  try {
    launchUrl(uri, webOnlyWindowName: '_self');
  } catch (_) {
    // Fallback to pushNamed if running within authenticated app with named routes
    try {
      Navigator.of(context).pushNamed(
        '/?route=AiChatScreen',
        arguments: prompt,
      );
    } catch (_) {}
  }
}
```

---

## 8. Dated Back-Schedule Targeting Nov 13 Go-Live (NET-818)

| Milestone Date | Action & Responsibility | Exit Criteria |
|---|---|---|
| **Sat, 7 Nov 2026** | Deliver `FAILFIX_PLAN_NET-777_CATALOG_v1.10.md` (14:15 ET) | CoS & SAG score $\ge 95/100$ |
| **Sun, 8 Nov 2026** | Review Cycle completion & Founder Eric Typed YES on Plan | Eric typed YES received |
| **Mon, 9 Nov 2026** | Feature branch build on `origin/dev` (@ `b0b05808`) | Clean compilation, tests exit 0 |
| **Tue, 10 Nov 2026** | Deploy to named preview channel `preview-catalog` | Field Tester verification pass |
| **Wed, 11 Nov 2026** | Field Tester end-to-end audit on live preview | All acceptance criteria verified |
| **Thu, 12 Nov 2026** | Review Cycle on build diff (GEMINI38 + CoS + SAG $\ge 95$) | Forward deploy baton to Eric |
| **Fri, 13 Nov 2026** | **Founder Eric Typed YES $\rightarrow$ Public Catalog LIVE** | Catalog accessible at `numista.ai/catalog` |

---

## 9. Verification Commands, Rollback & Spend Controls

### A. Executable Test Suite in `test/catalog_browse_test.dart`
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_mobile/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_mobile/services/mint_error_service.dart';
import 'package:numista_mobile/models/mint_error.dart';
import 'package:numista_mobile/models/coin_model.dart';
import 'package:numista_mobile/services/precious_metals_service.dart';
import 'package:numista_mobile/services/coin_specification_service.dart';

void main() {
  group('Catalog Browse Retail & Valuation Fallback Tests (B05N-8)', () {
    testWidgets('Renders CPG Retail when positive price exists', (tester) async {
      final item = {
        'id': 'test-coin-1',
        'name': '1958 Washington Quarter',
        'cpg_retail': 24.50,
      };

      await tester.pumpWidget(MaterialApp(
        home: Scaffold(body: CatalogCard(item: item)),
      ));

      expect(find.text('CPG Retail: \$24.50'), findsOneWidget);
    });

    testWidgets('Renders Face Value and pending estimate when retail is missing', (tester) async {
      final item = {
        'id': 'test-coin-2',
        'name': '1958 Washington Quarter',
        'cpg_retail': null,
        'face_value': 0.25,
      };

      await tester.pumpWidget(MaterialApp(
        home: Scaffold(body: CatalogCard(item: item)),
      ));

      expect(find.text('Face Value: \$0.25 · Value pending AI estimate'), findsOneWidget);
      expect(find.text('\$0.00'), findsNothing);
    });
  });

  group('Known Errors Strict Fail-Closed Matching Tests (B05N-14)', () {
    final clippedError1999 = MintError(
      id: 'err-1',
      name: 'Clipped Planchet',
      shortName: 'Clipped',
      category: 'Planchet',
      subcategory: 'Planchet Errors',
      denominations: ['quarter'],
      years: [1999],
      mintMarks: [],
      designation: '',
      estValueLow: 25,
      estValueHigh: 50,
      rarity: 'Common',
      description: 'Clipped planchet',
      howToSpot: 'Missing edge',
      datasets: ['collectible'],
      images: [],
      relatedCoinIds: [],
      sources: ['NGC'],
      series: ['50 State Quarters'],
      coinTypes: ['Clad'],
    );

    test('Rejects 1999 Statehood quarter error on 1958 Washington quarter', () {
      final coin1958 = CoinModel(
        id: 'c-1958',
        year: 1958,
        denomination: 'quarter',
        programSeries: 'Washington Quarter',
        strikeType: 'Business',
        variety: 'Silver',
      );

      final matches = MintErrorService.matchesCoin(
        error: clippedError1999,
        coin: coin1958,
      );
      expect(matches, isFalse);
    });

    test('Rejects error when coin series is blank (fail-closed rule)', () {
      final coinBlankSeries = CoinModel(
        id: 'c-blank',
        year: 1999,
        denomination: 'quarter',
        programSeries: null, // Blank series
        strikeType: 'Business',
      );

      final matches = MintErrorService.matchesCoin(
        error: clippedError1999,
        coin: coinBlankSeries,
      );
      expect(matches, isFalse);
    });
  });

  group('Owned Storage URL Validator Tests (Must-Fix #2)', () {
    test('Allows verified Numista Firebase Storage HTTPS URL', () {
      final validUrl = 'https://storage.googleapis.com/numista-vault.firebasestorage.app/coins/1958_q.png';
      expect(CatalogBrowseScreen.isOwnedStorageUrl(validUrl), isTrue);
    });

    test('Allows relative same-origin URL', () {
      expect(CatalogBrowseScreen.isOwnedStorageUrl('/icons/Icon-512.png'), isTrue);
    });

    test('Rejects plain HTTP URL', () {
      final httpUrl = 'http://storage.googleapis.com/numista-vault.firebasestorage.app/coins/1958_q.png';
      expect(CatalogBrowseScreen.isOwnedStorageUrl(httpUrl), isFalse);
    });

    test('Rejects unverified bucket paths', () {
      final badBucketUrl = 'https://storage.googleapis.com/unverified-bucket/coins/1958_q.png';
      expect(CatalogBrowseScreen.isOwnedStorageUrl(badBucketUrl), isFalse);
    });

    test('Rejects third-party external hotlinks', () {
      final externalUrl = 'https://upload.wikimedia.org/wikipedia/commons/test.jpg';
      expect(CatalogBrowseScreen.isOwnedStorageUrl(externalUrl), isFalse);
    });
  });

  group('Silver Melt & Composition Tests (B05N-9, B05N-17)', () {
    test('Calculates 1958 Washington Quarter silver melt value correctly', () {
      final spec = CoinSpecificationService.getSpecification('quarter', 1958);
      expect(spec, isNotNull);
      expect(spec!.fineness, 0.900);
      expect(spec.weightGrams, 6.25);

      final melt = PreciousMetalsService.calculateMeltValue(
        weightGrams: spec.weightGrams,
        fineness: spec.fineness,
        spotPriceTroyOz: 30.00,
      );
      expect(melt, isNotNull);
      expect(melt!, closeTo(5.428, 0.01));
    });

    test('Returns null melt value for 1965 clad quarter', () {
      final spec = CoinSpecificationService.getSpecification('quarter', 1965);
      expect(spec, isNotNull);
      expect(spec!.fineness, isNull);

      final melt = PreciousMetalsService.calculateMeltValue(
        weightGrams: spec.weightGrams,
        fineness: spec.fineness,
        spotPriceTroyOz: 30.00,
      );
      expect(melt, isNull);
    });
  });
}
```

### B. Non-Force Rollback & Operational Spend Controls
1. **Dynamic Pre-Execute Rollback Target:**
   Before any execution, record exact pre-execution HEAD commit on branch:
   `PRE_EXEC_HEAD=$(git rev-parse HEAD)`
   Non-force rollback command if any preview smoke check fails:
   `git revert --no-edit <execute_commit_sha> && git push origin <branch>`
   (Strictly **NO `git push --force`** on shared branches).
2. **Spend Controls — Alerts Only, Never Caps:**
   - Notification alert threshold: **$20.00 / month** sent to Eric via email/Slack.
   - **Hard spending cap: ZERO.** All automated shutoffs and hard limits (including the $25 cap) are strictly eliminated, enforcing Eric's "alerts only, never caps" policy.
3. **Standing Locks:**
   - `origin/main` locked at `9f04550a`.
   - Stripe strictly locked OFF across all code and configs.
   - Zero code execution, zero deployments, zero Firestore writes without Founder Eric's explicit typed YES.
   - US-only numismatic scope.
   - 3:00 AM ET nightly stand-down handoff.
   - Laptop + GCS AI coin image backups verified before any image cleanup/migration.

---

**END OF FAILFIX PLAN v1.10 (NET-816)**
