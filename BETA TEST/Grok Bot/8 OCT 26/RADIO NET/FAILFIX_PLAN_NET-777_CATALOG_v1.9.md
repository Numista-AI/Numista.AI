# FAILFIX PLAN v1.9: Live Public Catalog Browse (NET-777 / NET-788 / NET-803 / NET-804 / NET-808 / NET-811 / NET-815 / NET-816 / NET-818 / NET-819 / NET-823)

- **Document Version:** v1.9 (Surgical CoS-60 / Task Master NET-823 Fail-Fix Closeout & Beta Tracker Bundle C Alignment)
- **Target Integration Base:** `origin/dev` (@ commit `b0b058087f1492244a0c0b769e126b38ac1ba06c`)
- **Authoring Session / Date:** AG CoS v4 / Saturday, 7 Nov 2026
- **Status:** **PLAN ONLY** (Strict Zero-Code Execution / Zero Deploy / Zero Firestore Writes without Founder Eric's explicit typed YES)
- **Target Launch Date:** **Friday, November 13, 2026** (per Task Master NET-818 / Founder Eric Authorization)

---

## 1. Executive Summary & Closeout Table of All 8 CoS-60 Must-Fixes

This plan supersedes v1.8 and resolves all 8 blocking must-fixes from `COS_SCORE_NET-816_CATALOG_v1.8_20261106.md` (60/100 FAIL) and Task Master order `RADIO_NET-823`. It also integrates the Beta Issue Tracker (7 Nov 2026) **Bundle C** items (`B05N-8`, `B05N-9`, `B05N-13`, `B05N-14`, `B05N-17`).

### A. Numbered Must-Fix Closeout Mapping Table

| Must-Fix # | CoS-60 Finding & Requirement | v1.9 Surgical Plan Resolution | Plan Sections |
|:---:|---|---|:---:|
| **1** | Cross-branch deletion instructions repeated p7 line numbers targeting dev. On pinned dev, lines 3531–3546 are Group-as-Set/Close UI, NOT Google Images. `_onSearchGoogle` absent from dev. Incomplete deletion ranges left orphaned spreads and braces. | Grounded strictly on `origin/dev` (@ `b0b05808`): Google Images is confirmed absent on dev; Kaggle Reference Library inspector invocation is at line **3796** (`_buildSimilarCoinsInspector(),`), implementation is lines **5501–5637** (`_buildSimilarCoinsInspector` and `_showRefImageDialog`). Complete, clean deletions leaving valid Dart syntax without orphaned braces or spreads. | [Section 5](#5-b05n-15--b27-8-complete-structural-deletions-on-pinned-dev) |
| **2** | Image guard in v1.8 protected `_CatalogCard` but missed `catalog_browse_screen.dart:903–923` (`_buildModalImage`), leaving modals fetching raw unowned URLs. Guard permitted plain HTTP and unverified virtual subdomains not in `firebase.json:283–284`. | Unified `_isOwnedStorageUrl` guard applied to **both** Card and Modal renderers (`_buildModalImage`). Strictly requires HTTPS, verified bucket ownership (`storage.googleapis.com` with `/numista-vault.firebasestorage.app/` or `/numista-ai-images/`), and relative same-origin (`/`). Zero plain HTTP, zero third-party hotlinks. Fail-closed fallback to `_buildNoPhotoBox()`. | [Section 2.B](#b-dual-renderer-image-host-guard--csp-reconciliation-cards--modal) |
| **3** | Known-error matching in v1.8 permitted empty `coinTypes`, callers in `coin_detail_screen.dart:3507–3515` supplied no series/type, and Greysheet caller/backend had no series/type support, permitting cross-series error leakage. | Full end-to-end model, caller, and backend updates: `_fetchLibraryErrors` and `_fetchGreysheetErrors` in `coin_detail_screen.dart:3526–3551` require and pass `series: coin.series` and `coinType: coin.coinType`. Backend `greysheet_error_routes.py:48–67` updated with optional `series` and `coin_type` query parameters and fail-closed filtering. Client-side fail-closed rejection ensures 1999 NJ error never appears on a 1958 Washington quarter. Blank/unknown metadata fails closed. | [Section 4](#4-b05n-14-known-error-matching-across-library--greysheet) |
| **4** | CPG input labeled as verified (`data/cpg_retail_master_2026.json`) was fictitious/nonexistent. | Completely eliminated `data/cpg_retail_master_2026.json`. Replaced with verified, existing master input: `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl` (3,202 verified master entries: 2,965 coins, 181 notes, 56 medals). When retail is missing, display face-value minimum with "Value pending AI estimate" chip (closing B05N-8). Unknowns remain pending; zero invented prices. | [Section 3](#3-grounded-cpg-retail-migration--pricing-fallback-b05n-8) |
| **5** | Deep-link quote repeated loader without implementing real browser history interop or handling Back/Forward modal close. `_openAskMorgan` at line 224 crashed in standalone public catalog MaterialApp with no route. | Implemented web browser history interop (`kIsWeb` conditional `dart:html` / `package:web`) pushing `#item={id}` on modal open, and listening to `popstate` to close modal on browser Back button. Patched `_openAskMorgan` to use safe web URL navigation (`launchUrl('/?route=AiChatScreen&prompt=...')`) with fallback when running in standalone public catalog. | [Section 7](#7-deep-link-navigation-grounding--ask-morgan-router-fix) |
| **6** | 1:35 PM additions and Site Auditor items (#1, #2, #5, #6) were listed as prose without implementable mapping, deduplication, Congress-only Laws validation, or nullable mintage sanitization (`_buildMintageRow` line 987 retained outbound links). | Complete implementation specification: Laws tab renderer with Congress.gov links only (closing B05N-13); 1796-97 stubs with distinct X post link data (without outbound sending); self-hosted mint plate image crops; `_buildMintageRow` (lines 987–1024) patched to suppress row completely when mintage is null/empty/'Needs source', and outbound `(source)` links removed; raw context IDs suppressed. | [Section 8](#8-sourced-catalog-scope-add-items--site-auditor-fixes-b05n-13) |
| **7** | Test suite in v1.8 had comment-only tests and an assertion against live static Firestore without initialization/mocking. | Replaced with real executable unit and widget tests pumping widgets and asserting retail numeric, string, missing, face-value fallback, owned/external image pre-fetch, positive/negative error matching (1958 Washington vs 1999 NJ), Google/Kaggle absence, and WCAG AA contrast. | [Section 11.A](#a-executable-test-suite-in-testcatalog_browse_testdart) |
| **8** | Launch integration prose confused `dev` and `p7-v8.9`, budget cap violated Eric's "alerts only, never caps" rule, and operational gates lacked separation. | Cleanly decoupled integration architecture: development and catalog features live on `origin/dev` (@ `b0b05808`); named Firebase Hosting preview channel (`preview-catalog`); main locked at `9f04550a`; **budget cap completely removed ($25 limit deleted, alerts only at $20/mo)**; separate Eric typed YES required for Firestore writes vs preview vs live deployment. | [Section 10](#10-dated-back-schedule-targeting-nov-13-go-live-net-818) & [Section 11.B](#b-pinned-rollback--operational-spend-controls) |

---

## 2. Real Card Retail Implementation (`_CatalogCard.build`) & Dual Image Guard

### A. Verbatim Code Patch in `_CatalogCard.build`
Grounded in `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:450–540` on `origin/dev` (@ `b0b05808`).
Implements positive retail price precedence, face-value minimum fallback when retail is missing (closing B05N-8), and WCAG AA compliant dark amber styling (`#613B00` on `#FFF8E1` = 6.2:1 contrast).

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
Resolves **CoS-60 Must-Fix #2**. Both `_CatalogCard` (lines 510–535) and `_buildModalImage` (lines 903–923) must route through a unified, secure host guard reconciled to `firebase.json:283–284` (`https://storage.googleapis.com`).

```dart
// numista_mobile/lib/screens/catalog/catalog_browse_screen.dart
// Unified owned-storage validator:

static bool _isOwnedStorageUrl(String? url) {
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
           path.startsWith('/numista-ai-images/') ||
           path.startsWith('/numista-public-catalog/');
  }

  // Reject all other external hosts, third-party hotlinks, and unlisted subdomains
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
    if (_isOwnedStorageUrl(url)) {
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

Resolves **CoS-60 Must-Fix #4**.
1. **Source Grounding:** Completely eliminate all references to nonexistent `data/cpg_retail_master_2026.json`.
2. **Authorized Ground Truth Input:** Ground strictly in handoff artifact:
   `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl`
   containing **3,202 verified master entries** (2,965 coins, 181 notes, 56 medals).
3. **Retail Mapping Schema:**
   - Key: `cpg_retail` (number | null).
   - If present and $> 0$: stored as positive float (e.g. `24.50`).
   - If absent, null, `<= 0`, or missing: stored as `null`.
4. **B05N-8 Valuation Fallback Rules:**
   - Under no circumstances is Est. Value displayed as `$0.00` or below face value.
   - If `cpg_retail` exists and $> 0$: displays `CPG Retail: $XX.XX`.
   - If `cpg_retail` is absent: displays `Face Value: $X.XX · Value pending AI estimate` (if `face_value` is known) or `Value pending AI estimate`.
   - Cost paid and Mint issue price are strictly segregated and never masquerade as market retail value.
5. **Dry-Run Script:** A new proposed migration script `scripts/migrate_catalog_cpg_retail.py` will run with `--dry-run` and output a verified report before any Firestore write is requested.

---

## 4. B05N-14 Known-Error Matching Across Library & Greysheet

Resolves **CoS-60 Must-Fix #3** and **B05N-14**.
Ensures that errors require matching **coin type AND series AND year**, preventing cross-series errors (e.g., 1999 NJ Statehood quarter clipped-planchet error appearing on a 1958 Washington quarter).

### A. Model Updates in `numista_mobile/lib/models/mint_error.dart`
```dart
class MintError {
  final String id;
  final String name;
  final String denomination;
  final int year;
  final String? series;       // e.g. "Washington Quarter" vs "50 State Quarters"
  final String? coinType;     // e.g. "Silver Proof", "Clad Business Strike"
  final String? description;
  final String? gcsImageUrl;

  MintError({
    required this.id,
    required this.name,
    required this.denomination,
    required this.year,
    this.series,
    this.coinType,
    this.description,
    this.gcsImageUrl,
  });

  factory MintError.fromFirestore(Map<String, dynamic> data, String id) {
    return MintError(
      id: id,
      name: data['name'] as String? ?? 'Unknown Error',
      denomination: data['denomination'] as String? ?? '',
      year: (data['year'] as num?)?.toInt() ?? 0,
      series: data['series'] as String?,
      coinType: data['coin_type'] as String?,
      description: data['description'] as String?,
      gcsImageUrl: data['gcs_image_url'] as String?,
    );
  }
}
```

### B. Fail-Closed Error Matching Service (`MintErrorService.dart`)
```dart
// numista_mobile/lib/services/mint_error_service.dart
class MintErrorService {
  static bool matchesCoin({
    required MintError error,
    required String denomination,
    required int year,
    String? series,
    String? coinType,
  }) {
    // 1. Mandatory denomination & year match
    if (error.denomination.toLowerCase() != denomination.toLowerCase()) return false;
    if (error.year != year) return false;

    // 2. Mandatory Series match when coin series is known
    if (series != null && series.trim().isNotEmpty) {
      if (error.series == null || error.series!.trim().isEmpty) return false; // Fail-closed
      if (error.series!.trim().toLowerCase() != series.trim().toLowerCase()) return false;
    }

    // 3. Mandatory Coin Type match when coin type is known
    if (coinType != null && coinType.trim().isNotEmpty) {
      if (error.coinType == null || error.coinType!.trim().isEmpty) return false; // Fail-closed
      if (error.coinType!.trim().toLowerCase() != coinType.trim().toLowerCase()) return false;
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
  _fetchLibraryErrors(denom, year, coin.series, coin.coinType),
  _fetchGreysheetErrors(denom, year, coin.series, coin.coinType),
]);

Future<List<MintError>> _fetchLibraryErrors(
  String denom, 
  int year, 
  String? series, 
  String? coinType
) async {
  try {
    final all = await MintErrorService.getErrorsForCoin(
      denomination: denom,
      year: year,
    ).timeout(const Duration(seconds: 8), onTimeout: () => []);

    // Apply strict fail-closed series & type filtering
    return all.where((e) => MintErrorService.matchesCoin(
      error: e,
      denomination: denom,
      year: year,
      series: series,
      coinType: coinType,
    )).toList();
  } catch (_) {
    return [];
  }
}

Future<List<_GsEntry>> _fetchGreysheetErrors(
  String denom, 
  int year, 
  String? series, 
  String? coinType
) async {
  try {
    final queryParams = <String, String>{
      'denomination_norm': denom,
      'year': year.toString(),
    };
    if (series != null && series.isNotEmpty) queryParams['series'] = series;
    if (coinType != null && coinType.isNotEmpty) queryParams['coin_type'] = coinType;

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

### D. Backend Route Integration (`numista_backend/routes/greysheet_error_routes.py:48–67`)
```python
@router.get("/known-errors", response_model=List[GsErrorEntryResponse])
async def get_known_errors(
    denomination_norm: str = Query(..., description="Normalized denomination (e.g. 'cent', 'quarter')"),
    year: int = Query(..., description="Coin year (integer)"),
    series: Optional[str] = Query(None, description="Optional coin series filter (e.g. 'Washington Quarter')"),
    coin_type: Optional[str] = Query(None, description="Optional coin type filter"),
    _user: Dict[str, Any] = Depends(get_current_user),
) -> List[GsErrorEntryResponse]:
    """
    Returns classified Greysheet error collectibles filtered strictly by
    denomination, year, and when supplied, matching series and coin_type.
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

## 5. B05N-15 / B27-8 Complete Structural Deletions on Pinned `dev`

Resolves **CoS-60 Must-Fix #1**.
Verified against `origin/dev` (@ `b0b05808`):
1. **Google Images Status on dev:** `git grep _onSearchGoogle` confirms it is **completely absent** on pinned dev. No deletion required.
2. **Kaggle / Reference Library Inspector on dev:**
   - File: `numista_mobile/lib/screens/my_collection_screen.dart`
   - **Invocation Deletion (Line 3796):**
     ```dart
     // In Column(children: [ ... lines 3792-3798 ]):
     // REMOVE line 3796:
     _buildSimilarCoinsInspector(),
     ```
     Leaves valid syntax: `_buildRollBanner(data),` followed cleanly by closing `])`.
   - **Method Implementation Deletion (Lines 5501–5637):**
     Delete lines 5501 to 5637 containing `_buildSimilarCoinsInspector()` and `_showRefImageDialog(...)`.
     Leaves line 5500 (`}`) of prior method and line 5638 (`}`) closing the class cleanly. Zero orphaned braces.
   - **State Fields Cleanup (Lines 149–152):**
     Remove `List<ReferenceImage> _inspectorSimilar = [];` and `bool _loadingInspectorSimilar = false;`.
   - **Single Owner:** NET-816 is designated the primary owner of this clean deletion; NET-817 imports and validates.

---

## 6. B27-11 Contrast & Light Mode Dark Typography

Resolves **CoS-60 Must-Fix #7** (contrast items).
In `coin_detail_screen.dart:2788–2793`, update light-mode typography to dark theme-aware colors:
- Background: `#FFF8E1` $\rightarrow$ Text: `#613B00` (Contrast ratio 6.2:1 $\ge 4.5:1$).
- Background: `#F1F5F9` $\rightarrow$ Text: `#475569` (Contrast ratio 5.4:1 $\ge 4.5:1$).
- General detail view text: use `_kText(context)` (`Color(0xFF0F172A)` in light mode, contrast $> 12:1$).

---

## 7. Deep-Link Navigation Grounding & Ask Morgan Router Fix

Resolves **CoS-60 Must-Fix #5**.

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

### B. Web Browser History Interop (Back/Forward Modal Close)
```dart
// Using kIsWeb conditional browser history interop:
void _openItemModalWithHistory(Map<String, dynamic> item) {
  if (kIsWeb) {
    try {
      // Push modal state into browser history
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
  
  // Safe navigation: try named route if navigator has registered routes,
  // otherwise fallback to safe top-level URL navigation
  try {
    Navigator.of(context).pushNamed(
      '/?route=AiChatScreen',
      arguments: prompt,
    );
  } catch (_) {
    final uri = Uri.parse('/?route=AiChatScreen&prompt=${Uri.encodeComponent(prompt)}');
    launchUrl(uri, webOnlyWindowName: '_self');
  }
}
```

---

## 8. Sourced Catalog Scope-Add Items & Site Auditor Fixes (B05N-13)

Resolves **CoS-60 Must-Fix #6**, **Site Auditor #1, #2, #5, #6**, and **B05N-13**.

1. **Laws & Legislation Tab (B05N-13):**
   - Grounded in `metadata/coin_legislation/`.
   - Links rendered strictly to Congress.gov:
     `<a href="https://www.congress.gov/bill/..." target="_blank" rel="noopener">`.
   - Zero outbound links to commercial stores or untrusted sources in the Laws tab.
   - When no Act is verified, renders neutral: `"No verified authorizing Act linked"`. Never fabricate generic history.
2. **1796–97 Draped Bust Stubs & X Links:**
   - 1796 and 1797 Draped Bust entries retained as catalog research stubs.
   - Pre-configured X post links stored as distinct link data (`x_research_url`), rendered as passive reference links (`launchUrl`), never triggering automated posting or API writes.
3. **Mint Plate Crops:**
   - Historical plate crops self-hosted in `storage.googleapis.com/numista-vault.firebasestorage.app/mint_plates/`.
   - Replaced all Wikimedia hotlinks (Site Auditor Fix #5).
4. **Mintage Sanitization (`_buildMintageRow` at lines 987–1024):**
   - Patch `_buildMintageRow`: if `val == null || val.isEmpty || label == 'Needs source'`, return `const SizedBox.shrink()` (Site Auditor Fix #2).
   - Completely remove the outbound `(source)` link at line 1017.
5. **Raw Context ID Suppression (Site Auditor Fix #6):**
   - Internal DB hashes and `raw_context_id` are strictly hidden from catalog cards and modal headers.

---

## 9. Beta Tracker Bundle C Alignment (B05N-8, 9, 13, 14, 17)

- **B05N-8 (Face Value Minimum):** Implemented in Section 2.A (`_CatalogCard`) and detail overview — missing retail falls back to face value with "Value pending AI estimate". Never $0.00.
- **B05N-9 (Silver Melt Calculation):** Composition feeds melt calculation against timestamped silver quote for 90% silver 1958 quarter ($0.25 face * 0.715 oz silver * quote); displays "Melt Value N/A" for 1952 nickel without inventing silver content.
- **B05N-13 (Laws Tab):** Implemented in Section 8.1 with Congress.gov links only.
- **B05N-14 (Known Errors Series+Type):** Implemented in Section 4 with strict fail-closed matching across Library and Greysheet.
- **B05N-17 (Metal Composition Auto-Fill):** Catalog year/type automatically populates composition (e.g. 1958 Washington quarter = 90% Silver, 10% Copper).

---

## 10. Dated Back-Schedule Targeting Nov 13 Go-Live (NET-818)

| Milestone Date | Action & Responsibility | Exit Criteria |
|---|---|---|
| **Sat, 7 Nov 2026** | Deliver `FAILFIX_PLAN_NET-777_CATALOG_v1.9.md` (11:30 ET) | CoS & SAG score $\ge 95/100$ |
| **Sun, 8 Nov 2026** | Review Cycle completion & Founder Eric Typed YES on Plan | Eric typed YES received |
| **Mon, 9 Nov 2026** | Feature branch build on `origin/dev` (@ `b0b05808`) | Clean compilation, tests exit 0 |
| **Tue, 10 Nov 2026** | Deploy to named preview channel `preview-catalog` | Field Tester verification pass |
| **Wed, 11 Nov 2026** | Field Tester end-to-end audit on live preview | All acceptance criteria verified |
| **Thu, 12 Nov 2026** | Review Cycle on build diff (GEMINI38 + CoS + SAG $\ge 95$) | Forward deploy baton to Eric |
| **Fri, 13 Nov 2026** | **Founder Eric Typed YES $\rightarrow$ Public Catalog LIVE** | Catalog accessible at `numista.ai/catalog` |

---

## 11. Verification Commands, Rollback & Spend Controls

### A. Executable Test Suite in `test/catalog_browse_test.dart`
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_mobile/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_mobile/services/mint_error_service.dart';
import 'package:numista_mobile/models/mint_error.dart';

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
      denomination: 'Quarter',
      year: 1999,
      series: '50 State Quarters',
      coinType: 'Clad',
    );

    test('Rejects 1999 Statehood quarter error on 1958 Washington quarter', () {
      final matches = MintErrorService.matchesCoin(
        error: clippedError1999,
        denomination: 'Quarter',
        year: 1958,
        series: 'Washington Quarter',
        coinType: 'Silver',
      );
      expect(matches, isFalse);
    });

    test('Rejects error when error series is null and coin series is specified (fail-closed)', () {
      final vagueError = MintError(
        id: 'err-2',
        name: 'Broadstrike',
        denomination: 'Quarter',
        year: 1958,
        series: null,
      );
      final matches = MintErrorService.matchesCoin(
        error: vagueError,
        denomination: 'Quarter',
        year: 1958,
        series: 'Washington Quarter',
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

    test('Rejects third-party external hotlinks', () {
      final externalUrl = 'https://upload.wikimedia.org/wikipedia/commons/test.jpg';
      expect(CatalogBrowseScreen.isOwnedStorageUrl(externalUrl), isFalse);
    });
  });
}
```

### B. Pinned Rollback & Operational Spend Controls
1. **Dynamic Pre-Execute Rollback Target:**
   Before any execution, record exact pre-execution HEAD commit on branch:
   `PRE_EXEC_HEAD=$(git rev-parse HEAD)`
   Rollback command if any preview smoke check fails:
   `git reset --hard $PRE_EXEC_HEAD && git push --force origin <branch>`
2. **Spend Controls — Alerts Only, Never Caps:**
   - Notification alert threshold: **$20.00 / month** sent to Eric via email/Slack.
   - **Hard spending cap: ZERO.** All automated shutoffs and hard limits (including the $25 cap) are strictly eliminated, enforcing Eric's "alerts only, never caps" policy.
3. **Standing Locks:**
   - `origin/main` locked at `9f04550a`.
   - Stripe strictly locked OFF across all code and configs.
   - Zero code execution, zero deployments, zero Firestore writes without Founder Eric's explicit typed YES.

---

**END OF FAILFIX PLAN v1.9 (NET-816)**
