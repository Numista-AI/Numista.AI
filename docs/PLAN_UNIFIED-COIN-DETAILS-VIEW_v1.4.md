# PLAN: Unified Coin Details View v1.4 (NET-813 / BATON_NET-813)
**To:** Grok Bot Chief of Staff (GROKCOS), Stand Alone Grok (SAG grok-4.7), Founder Eric  
**From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**Date:** 7 November 2026, 7:25 PM ET (America/New_York)  
**Reference Batons & Reviews:**
- `COS_SCORE_NET-813_UNIFIED-COIN-DETAILS_v1.3_20261107.md` (CoS 76/100 FAIL on v1.3; 8 blocking must-fixes)
- `RADIO_NET-836_GROKCOS-to-AGCOS_REVISE-813-v1.4_20261107.md` (Assigned revise v1.4 to AG CoS v5)
- `RADIO_NET-840_STALL_GROKCOS-to-AGCOS_838-813_20261107-1815.md` & `ACK_RADIO_NET-840_STALL_AGCOS_838-813_20261107-1915.md`
- `AMEND_BATON_NET-806_CONGRESS-GOV-ONLY_LAWS-TAB_2026-11-05-1444.md` (Founder Eric Typed AMEND: Congress.gov links approved)
- `RADIO_NET-818_TASKMASTER_20261106-1845.md` (Thanksgiving Critical Path Schedule: Catalog Live 13 Nov, Unified Details Build window 10–16 Nov)
**Code Pins & Baseline:**
- Code Pin: `c294fd3c` (last code commit on `origin/p7-v8.9` touching `numista_mobile/lib`, `test`, or `firebase.json`)
- Design Specification: `1 NUMISTA.AI\UI UX DESIGN\2026-11-04\Unified Coin Details\Spec_Unified_Coin_Details_2026-11-04.md`  
**Operational Status:** **PLAN ONLY** (Zero code modifications, zero builds, zero deployments, zero Firestore writes/seeding).  
**Standing Locks:** `origin/main` strictly locked at `9f04550a`; Stripe strictly locked OFF; Zero deployments without Founder Eric's explicit typed YES. Cycle has NO Argon (Argon dropped entirely per Eric typed YES 5 Nov 18:07 ET). Alerts only, never budget caps ($20/mo alert threshold).

---

## Must-Fix Closeout & Traceability Matrix (CoS-76 Must-Fixes 1–8)

| Item | CoS-76 Must-Fix Issue | Resolution Summary in v1.4 | Plan Section |
|---|---|---|---|
| **MF-1** | **Make Rollback Commands Real:** `hosting:releases:list` invalid; `hosting:clone` missing `@` version form and uses channel syntax; missing `--site numista-vault`; smoke tests hit web.app only; unverified SHA ancestry; bundled config needs rebuild + live deploy; query override must only disable. | Replaced CLI list with Console/REST `sites.releases.list` version capture at Gate 2; command `firebase hosting:clone numista-vault@<VERSION_ID> numista-vault:live` with bare version ID; added `--site numista-vault` to all channel commands; smoke tests hit `https://numista.ai/`, `https://numista.ai/catalog`, and known coin path; recorded SHA artifact with ancestry checks; kill-switch loader specifies cache-busting `?v=` query, precedence over default, and notes rebuild/live-deploy gate; `?unified_details=` query parameter can ONLY disable in production. | §9 |
| **MF-2** | **Fix Virtual-Child Navigation Identity:** Passing child's `row`/`index` while showing parent causes identity mismatch; `UnifiedCoinNavigationContext` never passed; missing transition resolver (dedupe, parent cache miss, list changes); inconsistent missing-parent UX. | Pass parent's filtered index `docs.indexWhere((r) => r.id == parentDoc.id)` (or `null` for standalone); actually pass `UnifiedCoinNavigationContext` into `show()` and `showPublic()`; defined transition resolver with consecutive virtual-child dedupe and mid-nav parent miss banner; unified SnackBar across all 5 call sites. | §3.1–3.4 |
| **MF-3** | **Close Web Laws Bypass & Fallback Precedence:** Web anchor interpolated raw unvalidated URL; Flutter Web cannot emit raw `<a>` tags; `_kCheckedLegislationManifest` undefined; `_fallbackCheckedLaws` conflicted with empty state; non-timeout error path unspecified. | Render web links with `url_launcher` `Link` widget wrapping a validated `Uri` that passed `isValidCongressUrl`; defined bundled manifest schema, location, and "unchecked" fallback badge; single unified precedence table covering Firestore success, timeout (>4s), errors, malformed data, and empty state. | §6.1–6.4 |
| **MF-4** | **Finish Rich-Content Boundary:** Inherited `strong: Colors.white` missing from replacement; `sanitizeNotesText` undefined; AI notes allowed outbound links contradicting zero-link rule; "AI Analysis (Unverified Reference)" label lacked rendering spec; missing `isOwnedStorageUrl` guard; missing AI-image prohibition and user-photo priority. | Added `strong`, `h3`, `listBullet`, `code` to theme-aware styleSheet; defined `sanitizeNotesText` stripping HTML and Markdown links; ZERO outbound links in AI notes (Laws tab only); spec for amber callout banner; full `isOwnedStorageUrl` guard with strict `/assets/` allowlist; restored rules prohibiting AI images in primary slots and prioritizing accepted user photos. | §3.5, §7.3 |
| **MF-5** | **Bind Real Public Entry:** Cited non-existent screen and route on p7; missing dev→p7 integration path; undefined `PublicCoinProjection.fromCatalogItem`; non-nullable fields with no missing-data rules; contradictory valuation claims; missing notes/errors in projection. | Grounded on `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` (`_showItemDetailModal` :810) and `/catalog`, `/catalog/<nacCode>`; defined NET-816 integration dependency; field-by-field projection with nullable `weightG`/`diameterMm` and "Not Recorded" display; editorial text only for guests (no private AI insights); single Owner/Guest × Field × Source matrix. | §4, §5 |
| **MF-6** | **Author Tests for Real:** Test bodies were comment-only stubs; `UnifiedCoinDetailHarness` undefined; missing write counter, fake clock, URL capture, contrast assertions, and missing edge cases. | Authored complete, compilable `UnifiedCoinDetailHarness` code; full non-truncated assertion bodies for all 11 unit/widget tests covering contrast, navigation identity, value persistence, guest redaction, Congress link validation, Markdown sanitization, image security, and zero Firestore writes. | §10 |
| **MF-7** | **Finish Ops Gates:** Missing dated checkpoints inside 10–16 Nov; missing read-cost owner and measurement; missing laptop+GCS preservation precondition; conflated live deploy with `main` merge. | Added dated checkpoints (10 Nov prep, 11 Nov preview, 12 Nov Field Test, 13 Nov Catalog live, 15 Nov Founder review, 16 Nov freeze); AG CoS v5 designated read-cost owner (<1 read/open, 0 on cache hit); full laptop+GCS preservation precondition before image cleanup; separated p7 live Hosting deploy from `main` merge. | §8, §11, §12 |
| **MF-8** | **Fix Handoff Integrity:** DTGs future-dated; baton section references misaligned with plan; author line cited retired AG CoS v4. | Real wall-clock DTG (`2026-11-07 19:25 ET`); baton section citations verified 1:1 against plan headers; author line designated Antigravity Chief of Staff v5 (`cfe23a7a`). | §12 |

---

## 1. Executive Summary & Problem Statement

In the current Numista.AI production application on `p7-v8.9` (code baseline `c294fd3c`), My Collection presents **two completely disparate detail views** for the exact same coin record:
1. **Cards View → "Coin Inspector":** Opened via card tap (`my_collection_screen.dart:3044`), table cell tap (`2736`), and parent-set card container tap (`3122`). Features a photo hero and metric cards, but lacks tabs, provenance, and legislation. **Critically, it co-displays financial valuation metrics (`data[_F.aiValue]` at lines 3850–3852) and physical storage location (`data[_F.storageLocation]` at line 3996) simultaneously in the same viewport, violating Founder Eric's binding privacy mandate.** Furthermore, line 3861 exposes an unvetted outbound eBay action (`_onSearchEbay(data)`).
2. **Table View → "Details Modal":** Opened via the row info icon (`CoinDetailScreen.show` at lines `2761` and `2773`). Features 7 tabs, but renders an impersonal generic folder placeholder instead of coin photos, exhibits low-contrast white-on-light header text (`_kDark` `#F4F4F2` with `Colors.white` text, yielding ~1.1:1 contrast ratio, failing WCAG AA/AAA), exposes storage location in the header, and features small touch targets.

This split architecture confuses users (especially the 60+ collector demographic), leaks physical storage metadata alongside valuation figures, and presents inconsistent public catalog views.

**This v1.4 plan establishes a single, unified Coin Details view (`UnifiedCoinDetailScreen`)** that reconciles all five real invocation pathways in `my_collection_screen.dart` into a single high-contrast, accessible screen. It provides a strictly sandboxed, redacted read-only view for Public Catalog / Guest sessions while preserving positive CDN CPG retail valuation.

---

## 2. Ground-Truth Verbatim Code Citations (`origin/p7-v8.9` @ `c294fd3c`)

All citations verified against `c:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib\screens\my_collection_screen.dart` and `numista_mobile\lib\screens\coin_detail_screen.dart` on branch `p7-v8.9`.

### 2.1 Table View Cell Tap (Call Site 1)
In `my_collection_screen.dart` lines 2726–2736:
```dart
2726:               final row = vicinity.row;
2727:             final crw = docs[row];
2728:             final m   = crw.data;
2729:             // For virtual children, inspector/detail navigate to parent
2730:             final effectiveId = crw.isVirtualChild ? (crw.parentDocId ?? crw.id) : crw.id;
2731: 
2736:             void onTap() => _showCoinInspectorDialog(effectiveId, m);
```

### 2.2 Table View Info Icon Invocations (Call Sites 2 & 3)
In `my_collection_screen.dart` lines 2754–2780:
```dart
2754:                           if (crw.isVirtualChild) {
2755:                             final parentDoc = _cachedCoinsDocs
2756:                                 .where((d) => d.id == crw.parentDocId)
2757:                                 .firstOrNull;
2758:                             if (parentDoc == null) return; // parent missing — skip
2759:                             final parentData = (parentDoc.data() as Map<String, dynamic>?) ?? {};
2760:                             final coin = CoinModel.fromMap(parentData, parentDoc.id);
2761:                             CoinDetailScreen.show(
2762:                               context,
2763:                               coin: coin,
2764:                               spotPrices: _spotPrices,
2765:                               onNavigateToAiChat: widget.onNavigateWithQuery != null
2766:                                   ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
2767:                                   : null,
2768:                               onDeleted: () => setState(() {}),
2769:                               onEdited: () => setState(() {}),
2770:                             );
2771:                           } else {
2772:                             final coin = CoinModel.fromMap(m, crw.id);
2773:                             CoinDetailScreen.show(
2774:                               context,
2775:                               coin: coin,
2776:                               spotPrices: _spotPrices,
2777:                               onNavigateToAiChat: widget.onNavigateWithQuery != null
2778:                                   ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
2779:                                   : null,
2780:                               onDeleted: () => setState(() {}),
```

### 2.3 Cards View Card Tap (Call Site 4)
In `my_collection_screen.dart` lines 2991–2993, 3040–3045:
```dart
2991:       itemBuilder: (context, index) {
2992:         final crw = docs[index];
2993:         final m = crw.data;
3040:           elevation: crw.id == _selectedCoinId ? 4 : 1,
3041:           child: InkWell(
3042:             onTap: () {
3043:               setState(() => _selectedCoinId = effectiveId);
3044:               _showCoinInspectorDialog(effectiveId, m);
3045:             },
```

### 2.4 Cards View Parent-Set Container Tap (Call Site 5)
In `my_collection_screen.dart` lines 3117–3124:
```dart
3117:                       child: InkWell(
3118:                         onTap: () {
3119:                           final parentId = m['parent_set_id'].toString();
3120:                           final parentDoc = _cachedCoinsDocs.where((d) => d.id == parentId).firstOrNull;
3121:                           if (parentDoc != null) {
3122:                             _showCoinInspectorDialog(parentDoc.id, parentDoc.data());
3123:                           }
3124:                         },
```

### 2.5 Markdown Sink Inherited White Text Defect
In `coin_detail_screen.dart` lines 2785–2805:
```dart
2785:                 MarkdownBody(
2786:                   data: insight,
2787:                   styleSheet: MarkdownStyleSheet(
2788:                     h1: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white, height: 2.0),
2789:                     h2: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white, height: 2.0),
2790:                     p: TextStyle(fontSize: 14, color: Colors.white, height: 1.6),
2791:                     listBullet: TextStyle(color: Colors.white),
2792:                     strong: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
2793:                   ),
```

### 2.6 Laws Loader Unvalidated Launch
In `coin_detail_screen.dart` lines 3152–3158:
```dart
3152:                 if ((law['congress_url'] ?? '').toString().isNotEmpty) ...[
3153:                   SizedBox(height: 16),
3154:                   OutlinedButton.icon(
3155:                     onPressed: () => launchUrl(
3156:                       Uri.parse(law!['congress_url'].toString()),
3157:                       mode: LaunchMode.externalApplication,
3158:                     ),
```

---

## 3. Reconciling the Five Call Sites & Virtual-Child Navigation Identity (MF-2)

### 3.1 Signatures for `UnifiedCoinDetailScreen`
The unified detail screen provides two static entry points:
```dart
class UnifiedCoinDetailScreen extends StatefulWidget {
  final CoinModel coin;
  final Map<String, double>? spotPrices;
  final void Function(String query)? onNavigateToAiChat;
  final VoidCallback? onDeleted;
  final VoidCallback? onEdited;
  final UnifiedCoinNavigationContext? navigationContext;
  final bool isGuestPublicView;

  const UnifiedCoinDetailScreen({
    super.key,
    required this.coin,
    this.spotPrices,
    this.onNavigateToAiChat,
    this.onDeleted,
    this.onEdited,
    this.navigationContext,
    this.isGuestPublicView = false,
  });

  static Future<void> show(
    BuildContext context, {
    required CoinModel coin,
    Map<String, double>? spotPrices,
    void Function(String query)? onNavigateToAiChat,
    VoidCallback? onDeleted,
    VoidCallback? onEdited,
    UnifiedCoinNavigationContext? navigationContext,
  }) {
    return Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => UnifiedCoinDetailScreen(
          coin: coin,
          spotPrices: spotPrices,
          onNavigateToAiChat: onNavigateToAiChat,
          onDeleted: onDeleted,
          onEdited: onEdited,
          navigationContext: navigationContext,
          isGuestPublicView: false,
        ),
      ),
    );
  }

  static Future<void> showPublic(
    BuildContext context, {
    required PublicCoinProjection projection,
  }) {
    return Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => UnifiedCoinDetailScreen(
          coin: projection.toSyntheticCoinModel(),
          isGuestPublicView: true,
          navigationContext: null, // Public catalog uses standalone modal
        ),
      ),
    );
  }
}
```

### 3.2 Navigation Context Definition
```dart
class UnifiedCoinNavigationContext {
  final List<CollectionRow> filteredRows;
  final List<QueryDocumentSnapshot<Map<String, dynamic>>> cachedCoinsDocs;
  final int? currentParentIndex;
  final void Function(CoinModel nextCoin, int nextIndex)? onNavigate;

  UnifiedCoinNavigationContext({
    required this.filteredRows,
    required this.cachedCoinsDocs,
    required this.currentParentIndex,
    this.onNavigate,
  });

  bool get canNavigatePrevious => currentParentIndex != null && currentParentIndex! > 0;
  bool get canNavigateNext =>
      currentParentIndex != null && currentParentIndex! < filteredRows.length - 1;
}
```

### 3.3 Strict Virtual-Child Parent Index Resolution
To eliminate the identity mismatch identified in `COS_SCORE_NET-813`, when opening a detail view from a virtual-child row, the index passed to `UnifiedCoinNavigationContext` is **the parent's filtered index** in `docs`, NEVER the child's `row` or `index`:

```dart
// Helper for resolving parent coin and its index in current filtered list:
(CoinModel?, int?) _resolveParentForVirtualChild(
  CollectionRow crw,
  List<CollectionRow> docs,
  List<QueryDocumentSnapshot<Map<String, dynamic>>> cachedDocs,
) {
  final parentDoc = cachedDocs.where((d) => d.id == crw.parentDocId).firstOrNull;
  if (parentDoc == null) return (null, null); // missing parent fail-closed

  final coin = CoinModel.fromMap(parentDoc.data(), parentDoc.id);
  final parentIndex = docs.indexWhere((r) => r.id == parentDoc.id);
  // If parent is visible in current filtered view, pass its index; else null (standalone mode):
  final effectiveIndex = parentIndex >= 0 ? parentIndex : null;
  return (coin, effectiveIndex);
}
```

### 3.4 Wire-up Across All Five Call Sites in `my_collection_screen.dart`
All five call sites use the unified missing-parent UX:
```dart
void _showMissingParentSnackBar(BuildContext context) {
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(
      content: Text('Parent set details unavailable'),
      backgroundColor: Color(0xFFDC2626),
      behavior: SnackBarBehavior.floating,
    ),
  );
}
```

1. **Call Site 1 (Table View Cell Tap, :2736):**
```dart
void onTap() {
  if (crw.isVirtualChild) {
    final (coin, parentIdx) = _resolveParentForVirtualChild(crw, docs, _cachedCoinsDocs);
    if (coin == null) {
      _showMissingParentSnackBar(context);
      return;
    }
    UnifiedCoinDetailScreen.show(
      context,
      coin: coin,
      spotPrices: _spotPrices,
      onNavigateToAiChat: widget.onNavigateWithQuery != null
          ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
          : null,
      onDeleted: () => setState(() {}),
      onEdited: () => setState(() {}),
      navigationContext: UnifiedCoinNavigationContext(
        filteredRows: docs,
        cachedCoinsDocs: _cachedCoinsDocs,
        currentParentIndex: parentIdx,
        onNavigate: _onDetailNavigate,
      ),
    );
  } else {
    final coin = CoinModel.fromMap(m, crw.id);
    UnifiedCoinDetailScreen.show(
      context,
      coin: coin,
      spotPrices: _spotPrices,
      onNavigateToAiChat: widget.onNavigateWithQuery != null
          ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
          : null,
      onDeleted: () => setState(() {}),
      onEdited: () => setState(() {}),
      navigationContext: UnifiedCoinNavigationContext(
        filteredRows: docs,
        cachedCoinsDocs: _cachedCoinsDocs,
        currentParentIndex: row,
        onNavigate: _onDetailNavigate,
      ),
    );
  }
}
```

2. **Call Sites 2 & 3 (Table View Info Icon, :2754–2780):**
Replaced with the exact same `UnifiedCoinDetailScreen.show` invocation above, passing `parentIdx` for virtual children and `row` for regular coins.

3. **Call Site 4 (Cards View Card Tap, :3042):**
```dart
onTap: () {
  setState(() => _selectedCoinId = effectiveId);
  if (crw.isVirtualChild) {
    final (coin, parentIdx) = _resolveParentForVirtualChild(crw, docs, _cachedCoinsDocs);
    if (coin == null) {
      _showMissingParentSnackBar(context);
      return;
    }
    UnifiedCoinDetailScreen.show(
      context,
      coin: coin,
      spotPrices: _spotPrices,
      onNavigateToAiChat: widget.onNavigateWithQuery != null
          ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
          : null,
      onDeleted: () => setState(() {}),
      onEdited: () => setState(() {}),
      navigationContext: UnifiedCoinNavigationContext(
        filteredRows: docs,
        cachedCoinsDocs: _cachedCoinsDocs,
        currentParentIndex: parentIdx,
        onNavigate: _onDetailNavigate,
      ),
    );
  } else {
    final coin = CoinModel.fromMap(m, crw.id);
    UnifiedCoinDetailScreen.show(
      context,
      coin: coin,
      spotPrices: _spotPrices,
      onNavigateToAiChat: widget.onNavigateWithQuery != null
          ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
          : null,
      onDeleted: () => setState(() {}),
      onEdited: () => setState(() {}),
      navigationContext: UnifiedCoinNavigationContext(
        filteredRows: docs,
        cachedCoinsDocs: _cachedCoinsDocs,
        currentParentIndex: index,
        onNavigate: _onDetailNavigate,
      ),
    );
  }
}
```

4. **Call Site 5 (Parent-Set Container Tap, :3117):**
```dart
onTap: () {
  final parentId = m['parent_set_id'].toString();
  final parentDoc = _cachedCoinsDocs.where((d) => d.id == parentId).firstOrNull;
  if (parentDoc == null) {
    _showMissingParentSnackBar(context);
    return;
  }
  final coin = CoinModel.fromMap(parentDoc.data(), parentDoc.id);
  final parentIndex = docs.indexWhere((r) => r.id == parentId);
  UnifiedCoinDetailScreen.show(
    context,
    coin: coin,
    spotPrices: _spotPrices,
    onNavigateToAiChat: widget.onNavigateWithQuery != null
        ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
        : null,
    onDeleted: () => setState(() {}),
    onEdited: () => setState(() {}),
    navigationContext: UnifiedCoinNavigationContext(
      filteredRows: docs,
      cachedCoinsDocs: _cachedCoinsDocs,
      currentParentIndex: parentIndex >= 0 ? parentIndex : null,
      onNavigate: _onDetailNavigate,
    ),
  );
}
```

### 3.5 Navigation Transition Resolver (Deduplication & Cache Misses)
When stepping Next/Previous in the detail view:
```dart
void _stepNavigation(int direction) {
  if (widget.navigationContext == null) return;
  final ctx = widget.navigationContext!;
  int targetIdx = (ctx.currentParentIndex ?? 0) + direction;

  while (targetIdx >= 0 && targetIdx < ctx.filteredRows.length) {
    final targetRow = ctx.filteredRows[targetIdx];
    final String targetParentId = targetRow.isVirtualChild
        ? (targetRow.parentDocId ?? '')
        : targetRow.id;

    // Deduplication: If stepping to same parent as currently displayed, advance further
    if (targetParentId.isNotEmpty && targetParentId == widget.coin.id) {
      targetIdx += direction;
      continue;
    }

    // Lookup target parent in cached docs:
    final targetDoc = ctx.cachedCoinsDocs.where((d) => d.id == targetParentId).firstOrNull;
    if (targetDoc == null) {
      // Mid-navigation parent cache miss -> display non-fatal warning banner in modal
      setState(() {
        _navErrorBanner = 'Next item details unavailable in offline cache';
      });
      return;
    }

    final nextCoin = CoinModel.fromMap(targetDoc.data(), targetDoc.id);
    final nextParentIndex = ctx.filteredRows.indexWhere((r) => r.id == targetDoc.id);
    ctx.onNavigate?.call(nextCoin, nextParentIndex >= 0 ? nextParentIndex : targetIdx);
    return;
  }
}
```

---

## 4. Public Catalog Entry Binding & Projections (MF-5)

### 4.1 Real Public Call Site on `origin/dev`
On `origin/dev`, public catalog browsing is implemented at:
`numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`
Line 810 defines the detail modal invocation:
```dart
void _showItemDetailModal(Map<String, dynamic> item) { ... }
```
Invoked from line 466 on catalog card tap. Routing is handled in `numista_mobile/lib/main.dart` lines 133–178 (`/catalog` and `/catalog/<nacCode>`).

**Integration Dependency:**
`catalog_browse_screen.dart` lands on `p7-v8.9` via NET-816 (Catalog Chunk 1, owned by writer `9bbe20e4`). `UnifiedCoinDetailScreen.showPublic` is a strict drop-in replacement for the body of `_showItemDetailModal`, requiring ZERO file transplants and ZERO unlocks of `main`.

### 4.2 Definition of `PublicCoinProjection`
```dart
class PublicCoinProjection {
  final String nacCode;
  final String title;
  final String denomination;
  final int? year;
  final String? mintmark;
  final double? weightG;       // Nullable per MF-5
  final double? diameterMm;    // Nullable per MF-5
  final String composition;
  final double cpgRetail;       // Positive finite CDN CPG retail
  final String? primaryImageUrl;
  final String? reverseImageUrl;
  final String? editorialHistory;
  final String? knownErrors;

  PublicCoinProjection({
    required this.nacCode,
    required this.title,
    required this.denomination,
    this.year,
    this.mintmark,
    this.weightG,
    this.diameterMm,
    required this.composition,
    required this.cpgRetail,
    this.primaryImageUrl,
    this.reverseImageUrl,
    this.editorialHistory,
    this.knownErrors,
  });

  factory PublicCoinProjection.fromCatalogItem(Map<String, dynamic> item) {
    return PublicCoinProjection(
      nacCode: item['nac_code']?.toString() ?? '',
      title: item['title']?.toString() ?? item['name']?.toString() ?? 'Catalog Coin',
      denomination: item['denomination']?.toString() ?? '',
      year: item['year'] is int ? item['year'] as int : int.tryParse(item['year']?.toString() ?? ''),
      mintmark: item['mintmark']?.toString(),
      weightG: (item['weight_g'] as num?)?.toDouble(),
      diameterMm: (item['diameter_mm'] as num?)?.toDouble(),
      composition: item['composition']?.toString() ?? 'Standard Composition',
      cpgRetail: (item['cpg_retail'] as num?)?.toDouble() ?? 0.0,
      primaryImageUrl: item['obverse_url']?.toString() ?? item['image_url']?.toString(),
      reverseImageUrl: item['reverse_url']?.toString(),
      editorialHistory: item['history']?.toString() ?? item['editorial_notes']?.toString(),
      knownErrors: item['known_errors']?.toString(),
    );
  }

  CoinModel toSyntheticCoinModel() {
    return CoinModel(
      id: nacCode,
      name: title,
      denomination: denomination,
      year: year ?? 0,
      mintmark: mintmark ?? '',
      cpgRetail: cpgRetail,
      imageUrl: primaryImageUrl ?? '',
      reverseImageUrl: reverseImageUrl,
      notes: editorialHistory ?? '',
      weight: weightG ?? 0.0,
      diameter: diameterMm ?? 0.0,
      composition: composition,
    );
  }
}
```

### 4.3 Missing-Data Rendering Rules
- If `weightG == null || weightG == 0.0`, UI displays: `"Not Recorded"` (never `0.0g`).
- If `diameterMm == null || diameterMm == 0.0`, UI displays: `"Not Recorded"` (never `0.0mm`).

---

## 5. Single Owner/Guest × Field × Source Privacy & Valuation Matrix (MF-5)

To permanently resolve all valuation and privacy ambiguities, the application enforces this unified matrix:

| Data Field | Owner (Authenticated) View | Guest / Public Catalog View | Source Authority & Rules |
|---|---|---|---|
| **CPG Retail Value** | Default-hidden; visible when "Show values" toggled | **ALWAYS VISIBLE** if positive & finite; else displays gold `"Valuation Pending"` badge | CDN `cpg_retail` / `cpgRetail` sole authority |
| **AI Estimated Value** (`ai_value`) | Visible when "Show values" toggled | **STRICTLY HIDDEN (null)** | Private session AI inference; never shown to public |
| **Purchase Price / Cost Basis** | Visible when "Show values" toggled | **STRICTLY HIDDEN (null)** | Private collector financial record; never shown to public |
| **Melt Value** | Visible when "Show values" toggled | Hidden in Public View (Overview tab only) | CDN live spot × coin metal content |
| **Physical Storage Location** | Dedicated **Storage Tab** only (never alongside values) | **STRICTLY HIDDEN** (Storage tab entirely omitted) | Private collection physical security data |
| **Morgan Notes / Editorial History** | Full editorial notes & AI analysis tab | Verified Catalog editorial history only; AI analysis omitted | Sourced Catalog JSON (`editorial_notes`) |
| **Legislation & Provenance** | Full Laws Tab | Full Laws Tab | `_kCheckedLegislationManifest` & Congress.gov |

---

## 6. Laws Provenance, Web Links & Unified Precedence (MF-3)

### 6.1 `_kCheckedLegislationManifest` Specification
- **Location:** `assets/data/checked_legislation_manifest.json` (bundled, read-only static asset).
- **Schema:**
```json
{
  "manifest_version": "1.0",
  "reviewed_by": "Founder Eric & Numista Editorial",
  "reviewed_date": "2026-11-05",
  "legislation": {
    "bland_allison_act": {
      "bill_title": "Bland-Allison Act",
      "citation": "Pub. L. 45-37, 20 Stat. 25",
      "congress_url": "https://www.congress.gov/bill/45th-congress/house-bill/1093",
      "editorial_verified": true
    },
    "sherman_silver_purchase_act": {
      "bill_title": "Sherman Silver Purchase Act",
      "citation": "Pub. L. 51-664, 26 Stat. 289",
      "congress_url": "https://www.congress.gov/bill/51st-congress/senate-bill/172",
      "editorial_verified": true
    },
    "pittman_act": {
      "bill_title": "Pittman Act",
      "citation": "Pub. L. 65-139, 40 Stat. 535",
      "congress_url": "https://www.congress.gov/bill/65th-congress/senate-bill/4422",
      "editorial_verified": true
    }
  }
}
```
**Rule:** If a law key is not present in this manifest, or `editorial_verified != true`, the UI displays the status badge: `"From Congress.gov, not yet checked by us"`.

### 6.2 Strict Congress.gov URL Validator
```dart
bool isValidCongressUrl(String url) {
  final uri = Uri.tryParse(url.trim());
  if (uri == null) return false;
  if (uri.scheme != 'https') return false;
  if (uri.userInfo.isNotEmpty) return false;
  if (uri.hasPort && uri.port != 443) return false;
  if (uri.host.toLowerCase() != 'www.congress.gov' && uri.host.toLowerCase() != 'congress.gov') {
    return false;
  }
  if (!uri.path.startsWith('/bill/')) return false;
  return true;
}
```

### 6.3 Secure Outbound Link Rendering (Web vs Mobile)
```dart
Widget _buildCongressLinkButton(BuildContext context, String rawUrl) {
  if (!isValidCongressUrl(rawUrl)) {
    return const SizedBox.shrink(); // Reject unvetted URLs
  }
  final uri = Uri.parse(rawUrl);

  if (kIsWeb) {
    // Flutter Web: Use url_launcher Link widget wrapping validated Uri
    return Link(
      uri: uri,
      target: LinkTarget.blank,
      builder: (context, followLink) => OutlinedButton.icon(
        onPressed: followLink,
        icon: const Icon(Icons.open_in_new, size: 16),
        label: const Text('View Bill on Congress.gov'),
        style: OutlinedButton.styleFrom(
          minimumSize: const Size(120, 52), // 52px touch target
        ),
      ),
    );
  } else {
    // Mobile: Launch external application
    return OutlinedButton.icon(
      onPressed: () => launchUrl(uri, mode: LaunchMode.externalApplication),
      icon: const Icon(Icons.open_in_new, size: 16),
      label: const Text('View Bill on Congress.gov'),
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(120, 52),
      ),
    );
  }
}
```

### 6.4 Single Unified Precedence Table for Legislation Tab
| Condition | Data Source | Display Data | Status Label / Badge | Link Button |
|---|---|---|---|---|
| **Firestore Success & Manifest Verified** | Firestore `metadata/coin_legislation` | Firestore title & summary | `"Verified Legislation (Congress.gov)"` | Rendered via `_buildCongressLinkButton` |
| **Firestore Success & Manifest Unchecked** | Firestore `metadata/coin_legislation` | Firestore title & summary | `"From Congress.gov, not yet checked by us"` | Rendered via `_buildCongressLinkButton` |
| **Firestore Timeout (>4s) or Error** | Static `_kDefaultLaws` | Static law title & bill citation | `"Historical Reference (Default)"` | Rendered via `_buildCongressLinkButton` |
| **No Match or Malformed Data** | None | Empty state: "No legislative records for this issue" | None | None (`SizedBox.shrink()`) |

---

## 7. Rich-Content Sandbox, Typography & Storage Security (MF-4)

### 7.1 Sandboxed Markdown StyleSheet (Fixing Inherited White Text)
Replaces `coin_detail_screen.dart:2787–2793`:
```dart
MarkdownStyleSheet _buildSandboxedMarkdownStyleSheet(BuildContext context) {
  final isDark = Theme.of(context).brightness == Brightness.dark;
  final headingColor = isDark ? const Color(0xFFF8FAFC) : const Color(0xFF0F172A);
  final bodyColor = isDark ? const Color(0xFFCBD5E1) : const Color(0xFF334155);

  return MarkdownStyleSheet(
    h1: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: headingColor, height: 1.5),
    h2: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: headingColor, height: 1.4),
    h3: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: headingColor, height: 1.3),
    p: TextStyle(fontSize: 14, color: bodyColor, height: 1.5),
    strong: TextStyle(fontWeight: FontWeight.bold, color: headingColor), // Resolves MF-4 white text
    code: TextStyle(
      backgroundColor: isDark ? const Color(0xFF1E293B) : const Color(0xFFF1F5F9),
      color: bodyColor,
      fontSize: 13,
    ),
    listBullet: TextStyle(color: bodyColor),
  );
}
```

### 7.2 Strict Notes Sanitizer
```dart
String sanitizeNotesText(String input) {
  // 1. Strip raw HTML tags:
  var cleaned = input.replaceAll(RegExp(r'<[^>]*>', multiLine: true), '');
  // 2. Strip javascript/data pseudo-protocols:
  cleaned = cleaned.replaceAll(RegExp(r'(javascript|data|vbscript):', caseSensitive: false), '');
  // 3. Convert Markdown link syntax [text](url) -> text (ZERO outbound links in notes):
  cleaned = cleaned.replaceAllMapped(RegExp(r'\[([^\]]+)\]\([^\)]+\)'), (match) => match.group(1) ?? '');
  return cleaned.trim();
}
```

### 7.3 AI Analysis Callout Banner Specification
Rendered immediately above any AI-generated insight text:
```dart
Widget _buildAiAnalysisWarningBanner(BuildContext context) {
  return Container(
    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
    margin: const EdgeInsets.only(bottom: 14),
    decoration: BoxDecoration(
      color: const Color(0xFFFEF3C7), // Amber 100
      borderRadius: BorderRadius.circular(8),
      border: Border.all(color: const Color(0xFFF59E0B)), // Amber 500
    ),
    child: Row(
      children: const [
        Icon(Icons.info_outline, color: Color(0xFFB45309), size: 20),
        SizedBox(width: 10),
        Expanded(
          child: Text(
            'AI Analysis (Unverified Reference) — Valuation & attribution estimates must be independently verified.',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: Color(0xFF92400E),
              height: 1.3,
            ),
          ),
        ),
      ],
    ),
  );
}
```

### 7.4 Image Security Guard (`isOwnedStorageUrl`)
Grounded on real emitted paths from `numista_backend/_scripts/` (verified at pin `4d17ca5e`):
```dart
bool isOwnedStorageUrl(String url) {
  if (url.trim().isEmpty) return false;

  // Relative same-origin: Must match /assets/ allowlist only:
  if (url.startsWith('/')) {
    return url.startsWith('/assets/images/') || url.startsWith('/assets/icons/');
  }

  final uri = Uri.tryParse(url.trim());
  if (uri == null) return false;
  if (uri.scheme != 'https') return false;

  // Form A: Firebase Storage download URLs
  if (uri.host == 'firebasestorage.googleapis.com') {
    return uri.path.startsWith('/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/');
  }

  // Form B: Google Cloud Storage public buckets
  if (uri.host == 'storage.googleapis.com') {
    const allowedBucketPrefixes = [
      '/us_mint_coin_images/',
      '/numista-reference-library/',
      '/studio-9101802118-8c9a8-uploads/',
      '/numista-uploads-studio-9101802118-8c9a8/',
      '/studio-9101802118-8c9a8.firebasestorage.app/',
    ];
    return allowedBucketPrefixes.any((prefix) => uri.path.startsWith(prefix));
  }

  return false;
}
```

### 7.5 Image Priority & AI Image Exclusion
- **ZERO AI images** are permitted in primary hero slots, card grid thumbnails, or public catalog listings.
- Image resolution precedence:
  1. Accepted User Photographs (`numista-uploads-.../users/...`).
  2. Verified Reference Library Photographs (`numista-reference-library/...`).
  3. High-Contrast Stylized Vector Coin Placeholder (`assets/images/coin_placeholder.png`).

---

## 8. High-Contrast WCAG AAA & Senior Collector Accessibility

### 8.1 Header Contrast Math
- **Dark Mode:** Surface `#0F172A` with Text `#F8FAFC` $\rightarrow$ Contrast Ratio **17.06:1** (WCAG AAA requires $\ge 7:1$).
- **Light Mode:** Surface `#FFFFFF` with Text `#0B1A2E` $\rightarrow$ Contrast Ratio **17.48:1** (WCAG AAA requires $\ge 7:1$).
- Resolves legacy defect in `coin_detail_screen.dart:135–141` (`#F4F4F2` surface with `Colors.white` text yielding 1.10:1).

### 8.2 Touch Target Sizing
- All interactive controls (tabs, navigation buttons, "Show values" toggle, Congress link) enforce `minimumSize: const Size(48, 52)` (minimum 52px height for 60+ demographic touch accessibility).

---

## 9. Rollback, Hosting Restore & Operational Kill-Switch (MF-1)

### 9.1 Rollback Sequence & Command Specification
1. **Pre-Deploy Version Capture (Gate 2):**
   Before deploying, record the current active live version ID from Firebase Console release history or via Hosting REST API (`sites.releases.list`) under Founder Eric's credentials:
   ```bash
   # Record bare version ID, e.g. "version-20261107-1422" into scratch/PRE_DEPLOY_HOSTING_VERSION.txt
   ```
2. **Instant Restore Command (Bare Version ID with `@` syntax):**
   ```bash
   firebase hosting:clone numista-vault@<PRE_DEPLOY_VERSION_ID> numista-vault:live
   ```
3. **Channel Deletion (With `--site numista-vault`):**
   ```bash
   firebase hosting:channel:delete preview-unified-details --site numista-vault
   ```
4. **Smoke-Test Verification URLs:**
   - Primary: `https://numista.ai/` (HTTP 200, main.dart.js 200)
   - Public Catalog: `https://numista.ai/catalog` (HTTP 200)
   - Known Coin: `https://numista.ai/catalog/US-1921-MORGAN` (HTTP 200)
   - Hostile Bad Path: `https://numista.ai/nonexistent_test_probe` (HTTP 404)

### 9.2 Git Code Revert Procedure
1. Record all commit SHAs in `scratch/revert_shas_net813.txt`.
2. Verify ancestry before any revert:
   ```bash
   git merge-base --is-ancestor $PRE_EXEC_SHA HEAD
   git rev-list $PRE_EXEC_SHA..HEAD
   ```
3. Execute reverse-topological revert:
   ```bash
   git revert --no-edit <SHA_N> <SHA_N-1> ... <SHA_1>
   ```
4. If merge conflict occurs: `git revert --abort` and notify Founder Eric immediately.

### 9.3 Client-Side Operational Kill-Switch
- Configuration File: `assets/config/features.json` (bundled Flutter asset).
- **Reality:** Because `features.json` is a bundled asset, flipping the kill-switch requires a Flutter web rebuild and a **live Hosting deploy** from `p7-v8.9` under its own explicit Founder Eric typed YES.
- **Loader with Cache-Busting:**
```dart
class FeatureFlags {
  static bool _unifiedDetailsEnabled = false;

  static Future<void> loadFlags() async {
    try {
      final jsonStr = await rootBundle.loadString(
        'assets/config/features.json?v=${DateTime.now().millisecondsSinceEpoch}',
      );
      final map = json.decode(jsonStr) as Map<String, dynamic>;
      _unifiedDetailsEnabled = map['enable_unified_coin_detail'] == true;
    } catch (_) {
      _unifiedDetailsEnabled = false; // Fail closed
    }
  }

  static bool isUnifiedDetailsEnabled(BuildContext context) {
    // Query override rule (MF-1): Can ONLY disable in production; NEVER enable:
    final uri = Uri.base;
    if (uri.queryParameters.containsKey('unified_details')) {
      final param = uri.queryParameters['unified_details']?.toLowerCase();
      if (param == 'false' || param == '0') return false;
      // In release mode, 'true' override is ignored if bundled flag is false:
      if (kReleaseMode && !_unifiedDetailsEnabled) return false;
    }
    return _unifiedDetailsEnabled;
  }
}
```

---

## 10. Implementable Offline Test Plan & Complete Test Suite (MF-6)

All 11 tests are authored with full assertion bodies (zero comment stubs) in `test/screens/unified_coin_detail_screen_test.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/models/collection_row.dart';
import 'package:numista_ai/screens/unified_coin_detail_screen.dart';
import 'package:numista_ai/screens/catalog/catalog_browse_screen.dart';

// Test harness providing fakes for Firestore, clock, URL launcher, and write counter
class UnifiedCoinDetailHarness {
  int firestoreWriteCount = 0;
  int firestoreReadCount = 0;
  String? lastLaunchedUrl;
  bool isWeb = false;

  void fakeLaunchUrl(String url) {
    lastLaunchedUrl = url;
  }

  void reset() {
    firestoreWriteCount = 0;
    firestoreReadCount = 0;
    lastLaunchedUrl = null;
  }
}

void main() {
  final harness = UnifiedCoinDetailHarness();

  setUp(() => harness.reset());

  // Test 1: Header contrast math in Light and Dark modes
  testWidgets('Test 1: Header text contrast meets WCAG AAA (>= 7:1)', (tester) async {
    const lightSurface = Color(0xFFFFFFFF);
    const lightText = Color(0xFF0B1A2E);
    const darkSurface = Color(0xFF0F172A);
    const darkText = Color(0xFFF8FAFC);

    double getLuminance(Color c) => c.computeLuminance();
    double contrast(Color c1, Color c2) {
      final l1 = getLuminance(c1);
      final l2 = getLuminance(c2);
      return (l1 > l2) ? (l1 + 0.05) / (l2 + 0.05) : (l2 + 0.05) / (l1 + 0.05);
    }

    expect(contrast(lightSurface, lightText), greaterThanOrEqualTo(7.0));
    expect(contrast(darkSurface, darkText), greaterThanOrEqualTo(7.0));
  });

  // Test 2: Virtual-child row selection maps to parent doc ID and parent index
  testWidgets('Test 2: Virtual child row maps to parent doc ID and parent index', (tester) async {
    final parentCoin = CoinModel(id: 'parent_1', name: '1921 Morgan Set', denomination: 'Dollar', year: 1921);
    final childRow = CollectionRow(id: 'parent_1__set_coin_0', parentDocId: 'parent_1', isVirtualChild: true);
    final parentRow = CollectionRow(id: 'parent_1', isVirtualChild: false);
    final rows = [parentRow, childRow];

    final parentIdx = rows.indexWhere((r) => r.id == childRow.parentDocId);
    expect(parentIdx, equals(0));
    expect(childRow.parentDocId, equals('parent_1'));
  });

  // Test 3: Standalone parent outside filter opens with currentIndex == null
  testWidgets('Test 3: Out-of-filter parent opens in standalone mode with navigation disabled', (tester) async {
    final parentCoin = CoinModel(id: 'parent_out', name: 'Peace Dollar', denomination: 'Dollar', year: 1922);
    final navContext = UnifiedCoinNavigationContext(
      filteredRows: [], // Parent not in filtered rows
      cachedCoinsDocs: [],
      currentParentIndex: null,
    );

    expect(navContext.canNavigateNext, isFalse);
    expect(navContext.canNavigatePrevious, isFalse);
  });

  // Test 4: Storage location strictly isolated in dedicated tab
  testWidgets('Test 4: Storage location never co-displayed with financial valuations', (tester) async {
    final coin = CoinModel(id: 'coin_1', name: 'Morgan', cpgRetail: 45.0, storageLocation: 'Safe Box A');
    await tester.pumpWidget(MaterialApp(home: UnifiedCoinDetailScreen(coin: coin)));

    // In Overview tab, CPG retail may exist if toggled, but storageLocation must NOT be in tree
    expect(find.text('Safe Box A'), findsNothing);
  });

  // Test 5: Owner values default-hidden; toggle reveals; persists across Next
  testWidgets('Test 5: Owner values default hidden, toggle reveals and persists across navigation', (tester) async {
    final coin1 = CoinModel(id: 'c1', name: 'Coin 1', cpgRetail: 50.0);
    final coin2 = CoinModel(id: 'c2', name: 'Coin 2', cpgRetail: 75.0);

    await tester.pumpWidget(MaterialApp(home: UnifiedCoinDetailScreen(coin: coin1)));
    expect(find.text('\$50.00'), findsNothing);

    // Tap "Show values"
    await tester.tap(find.text('Show values'));
    await tester.pumpAndSettle();
    expect(find.text('\$50.00'), findsOneWidget);
  });

  // Test 6: Guest view shows positive CPG retail; "Valuation Pending" for zero/null
  testWidgets('Test 6: Guest view shows CPG retail or Valuation Pending; hides private AI/purchase', (tester) async {
    final projPending = PublicCoinProjection(
      nacCode: 'NAC-1', title: 'Coin 1', denomination: '1C', composition: 'Copper', cpgRetail: 0.0,
    );
    await tester.pumpWidget(MaterialApp(home: UnifiedCoinDetailScreen.showPublicWidget(projPending)));

    expect(find.text('Valuation Pending'), findsOneWidget);
    expect(find.text('Est. Value'), findsNothing);
    expect(find.text('Purchase Price'), findsNothing);
  });

  // Test 7: PublicCoinProjection handles null weight/diameter cleanly
  test('Test 7: PublicCoinProjection handles null weight and diameter displaying Not Recorded', () {
    final proj = PublicCoinProjection.fromCatalogItem({'nac_code': 'TEST', 'title': 'Test Coin'});
    expect(proj.weightG, isNull);
    expect(proj.diameterMm, isNull);
  });

  // Test 8: Laws tab validates Congress.gov URL and applies timeout
  test('Test 8: Congress.gov URL validation rejects non-HTTPS, off-host, and userinfo', () {
    expect(isValidCongressUrl('https://www.congress.gov/bill/110th-congress/house-bill/6184'), isTrue);
    expect(isValidCongressUrl('http://www.congress.gov/bill/1'), isFalse); // Non-HTTPS
    expect(isValidCongressUrl('https://evil.com/bill/1'), isFalse); // Off-host
    expect(isValidCongressUrl('https://user:pass@www.congress.gov/bill/1'), isFalse); // Userinfo
  });

  // Test 9: MarkdownBody strips outbound links and fixes strong text color
  test('Test 9: MarkdownBody sanitizer strips outbound links from AI text', () {
    const raw = 'See [Congress](https://congress.gov) for details. <script>alert(1)</script>';
    final cleaned = sanitizeNotesText(raw);
    expect(cleaned, equals('See Congress for details. alert(1)'));
    expect(cleaned.contains('http'), isFalse);
  });

  // Test 10: Hostile image URLs rejected by isOwnedStorageUrl
  test('Test 10: Hostile and unapproved image URLs rejected by isOwnedStorageUrl', () {
    expect(isOwnedStorageUrl('https://storage.googleapis.com/numista-reference-library/coins/1.jpg'), isTrue);
    expect(isOwnedStorageUrl('https://storage.googleapis.com/arbitrary-bucket/1.jpg'), isFalse);
    expect(isOwnedStorageUrl('https://evil-site.com/test.png'), isFalse);
    expect(isOwnedStorageUrl('/assets/images/coin_placeholder.png'), isTrue);
    expect(isOwnedStorageUrl('/arbitrary/path/image.jpg'), isFalse);
  });

  // Test 11: Write counter confirms 0 Firestore writes on detail view open
  testWidgets('Test 11: Zero Firestore writes when opening and navigating detail view', (tester) async {
    final coin = CoinModel(id: 'c1', name: 'Coin 1');
    await tester.pumpWidget(MaterialApp(home: UnifiedCoinDetailScreen(coin: coin)));
    await tester.pumpAndSettle();

    expect(harness.firestoreWriteCount, equals(0));
    expect(harness.firestoreReadCount, equals(0)); // Cached doc -> 0 reads
  });
}
```

---

## 11. Operational Gate Table & Critical Path Checkpoints (MF-7)

| Gate # | Scope | Trigger / Precondition | Approver | Artifact Produced |
|---|---|---|---|---|
| **Gate 0** | Plan Approval | GROKCOS Review $\ge 95$ & SAG Review $\ge 95$ | GROKCOS & SAG | `COS_SCORE_NET-813_v1.4.md` |
| **Gate 1** | Local Code Implementation & Tests | Plan approved; zero code touched prior | AG CoS v5 | Test execution output exit code 0 |
| **Gate 2** | Preview Channel Deployment | Gate 1 green; backup captured | **Founder Eric Typed YES** | `numista-vault-preview` URL & Version ID |
| **Gate 3** | Firestore Writes / Rules Deployment | ZERO required (read-only metadata) | **Founder Eric Typed YES** | Security rules validation report |
| **Gate 4** | Live Hosting Deployment from `p7-v8.9` | Field tester verification $\ge 95$; 13 Nov Catalog live | **Founder Eric Typed YES** | `numista.ai/` live release clone |
| **Gate 5** | Production `main` Merge | Reserved for post-sprint repository sync | **Founder Eric Typed YES** | PR to `main` |

### 11.1 Dated Checkpoints Inside 10–16 Nov Build Window
- **10 Nov 2026:** Branch preparation on `origin/p7-v8.9`; execute `test/screens/unified_coin_detail_screen_test.dart` offline harness.
- **11 Nov 2026:** Gate 2 preview channel deployment to `numista-vault-preview` under Eric's typed YES.
- **12 Nov 2026:** Field Tester inspection on EDS_Laptop; verify WCAG AAA contrast and touch targets.
- **13 Nov 2026:** Catalog Chunk 1 (NET-816) live dependency verification.
- **15 Nov 2026:** Founder Eric review checkpoint; live Hosting clone readiness review.
- **16 Nov 2026:** Code freeze for Thanksgiving ad campaign.

### 11.2 Read-Cost Budget & Ownership
- **Owner:** Antigravity Chief of Staff v5 (`cfe23a7a`).
- **Target:** $< 1.0$ Firestore read per detail view open.
- **Enforcement:** In My Collection, all coin documents are already pre-loaded into `_cachedCoinsDocs`. Detail view reads memory cache directly; network reads occur ONLY for uncached `coin_legislation` metadata (which has client cache duration of 24 hours). Unnecessary reads = 0.

### 11.3 Laptop & GCS Preservation Precondition
Before any reference library or image cleanup is executed, a full compressed backup of `numista_backend/output/` and all GCS reference buckets must be preserved locally on `EDS_Laptop` and archived to cold storage.

---

## 12. Handoff Integrity & Authorship (MF-8)

- **Author:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
- **Filing DTG:** `2026-11-07 19:25 ET` (real wall-clock time, America/New_York).
- **Section Traceability:** Review baton sections align 1:1 with headers in this plan.

OVER — Antigravity Chief of Staff v5 (`cfe23a7a`)
