# PLAN: Unified Coin Details View v1.2 (NET-813 / BATON_NET-813)
**To:** Antigravity Desk, Grok Bot CoS, Stand Alone Grok (SAG grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 / Catalog Night Team (`ba2bfdb2`)  
**Date:** 6 November 2026, 10:00 PM ET  
**Reference Batons & Reviews:**
- `BATON_NET-813_REVISE_UNIFIED-COIN-DETAILS-VIEW_v1.2_PER-COS-86-SAG-58_2026-11-05-1705.md`
- `COS_SCORE_NET-806_UNIFIED-COIN-DETAILS-v1.1_20261105.md` (CoS 86 FAIL on v1.1)
- `SAG_SCORE_NET-806_20261105.md` (SAG 58 FAIL on v1.1)
- `AMEND_BATON_NET-806_CONGRESS-GOV-ONLY_LAWS-TAB_2026-11-05-1444.md` (Founder Eric Typed AMEND: Congress.gov links approved)
- `RADIO_NET-818_TASKMASTER_20261106-1845.md` (Thanksgiving Critical Path Schedule: Catalog Live 13 Nov, Unified Details Build window 10–16 Nov)
**Design Specification:** `1 NUMISTA.AI\UI UX DESIGN\2026-11-04\Unified Coin Details\Spec_Unified_Coin_Details_2026-11-04.md`  
**Status:** **PLAN ONLY** (Zero code modifications, zero deployments, zero Firestore writes/seeding).  
**Target Build Window:** 10–16 November 2026 Sprint Build on `origin/p7-v8.9` (Founder Locked Decision #1; code freeze before Thanksgiving ad launch).  
**Standing Locks:** `origin/main` strictly locked at `9f04550a`; Stripe strictly locked OFF; Zero deployments without Founder Eric's explicit typed YES. Cycle has NO Argon (Argon dropped entirely per Eric typed YES 5 Nov 18:07 ET).

---

## 1. Executive Summary & Problem Statement

In the current Numista.AI production application on `p7-v8.9`, My Collection presents **two completely disparate detail views** for the exact same coin record:
1. **Cards View → "Coin Inspector":** Opened via card tap (`my_collection_screen.dart:3044`), table cell tap (`2736`), and parent-set card container tap (`3122`). Features a photo hero and metric cards, but lacks tabs, provenance, and legislation. **Critically, it co-displays financial valuation metrics (`data[_F.aiValue]` at lines 3850–3852) and physical storage location (`data[_F.storageLocation]` at line 3996) simultaneously in the same viewport, violating Founder Eric's binding privacy mandate.** Furthermore, line 3861 exposes an unvetted outbound eBay action (`_onSearchEbay(data)`).
2. **Table View → "Details Modal":** Opened via the row info icon (`CoinDetailScreen.show` at lines `2761` and `2773`). Features 7 tabs, but renders an impersonal generic folder placeholder instead of coin photos, exhibits low-contrast white-on-light header text (`_kDark` `#F4F4F2` with `Colors.white` text, yielding ~1.1:1 contrast ratio, failing WCAG AA/AAA), exposes storage location in the header, and features small touch targets.

This split architecture confuses users (especially the 60+ collector demographic), creates maintenance overhead, leaks physical storage metadata alongside valuation figures, and presents inconsistent public catalog views.

**This v1.2 plan establishes a single, unified Coin Details view (`UnifiedCoinDetailScreen`)** that reconciles all five real invocation pathways in `my_collection_screen.dart` into a single high-contrast, accessible screen. It provides a strictly sandboxed, redacted read-only view for Public Catalog / Guest sessions while preserving positive CDN CPG retail valuation.

### Key Architectural Resolutions in v1.2:
1. **Dynamic Pre-Execute Ancestor Rollback (Resolving CoS #1 & SAG #1):**
   - Strike the invalid and forbidden `HEAD...9f04550a` revert. `9f04550a` is locked `origin/main` and is **not an ancestor** of `p7-v8.9` (2112 files span, +282,979 / -11,590 lines).
   - Require dynamic capture of pre-execute HEAD (`PRE_EXEC_SHA=$(git rev-parse HEAD)`) prior to building on `p7-v8.9`. Revert command explicitly targets execute commit(s): `git revert --no-edit <EXECUTE_COMMITS>`.
   - Specify named Firebase Hosting release rollback / preview channel cleanup (`firebase hosting:channel:delete <preview-channel> --force` or cloning live).
2. **Verbatim Code Ground Truth & eBay Removal (Resolving SAG #2):**
   - Rewrite §2.5 verbatim quoting lines 3849–3864 (`_metricCard` for Est. Value, Melt Value, Grade, and Live eBay `_onSearchEbay(data)`) and lines 3989–3999 (`PURCHASE & STORAGE` section).
   - Completely remove the outbound eBay action (`_onSearchEbay`). Zero outbound links permitted anywhere in the modal except verified Congress.gov links in the Laws tab.
3. **Non-Const Default-Off Feature Flag & Per-Site Legacy Fallbacks (Resolving SAG #3):**
   - Replace compile-time `const bool` with mutable runtime gate: `bool kUnifiedCoinDetailsEnabled = false;` (defaults to `false`, non-const, assignable in tests).
   - Specify per-site legacy fallback for all five sites: Sites 1, 4, 5 fall back to `_showCoinInspectorDialog`, while Sites 2 & 3 fall back to `CoinDetailScreen.show`.
4. **Real Laws Tab Architecture & Congress.gov Boundaries (Resolving CoS #3 & SAG #4):**
   - Ground §6 in real app code: reads checked Firestore `metadata/coin_legislation` (doc read) or static fallback `_kDefaultLaws`.
   - Backend writer `coin_legislation_map.py` is NOT executed; NO client-side live API writer; NO client Firestore writes.
   - Outbound link is strictly a plain text link (`target=_blank`, `rel=noopener`), NO icon button, NO Congress images.
   - Checked catalog data takes precedence (`Source: Numista.AI catalog (checked)`). Unchecked text is prominently labeled: `"From Congress.gov, not yet checked by us"`.
   - Fail-closed: arbitrary API errors/timeouts yield clean labeled empty state (`"Morgan hasn't found the law for this coin yet"`), NEVER inventing unverified legal claims.
5. **Initial Release Strictly Read-Only (Resolving CoS #2 & SAG #5):**
   - Initial release of `UnifiedCoinDetailScreen` is 100% read-only.
   - All mutation actions (Edit, Wishlist, Delete) and Ask Morgan research request logging are visually inert or disabled (`onTap: null`). No callbacks fire.
   - Zero Firestore rules modifications, zero database schema migrations, zero Firestore writes or seeding under this plan. All mutations remain gated behind a separate typed YES from Founder Eric.
   - Unit tests explicitly assert that zero write callbacks or Firestore mutations are triggered.
6. **Public Guest CPG Retail Visibility & AI Image Hygiene (Resolving CoS #3 & SAG #6):**
   - In Guest Mode (`isPublicGuestMode == true`), while the private "Purchase & value" tab is redacted/hidden, positive CDN CPG retail (`cpgRetail > 0`) is displayed prominently on the **Overview** tab / hero slot. Guests always see verified retail market value.
   - Gold `'Valuation Pending'` chip is displayed ONLY when retail value is missing (`null`), empty, or `<= 0` — NEVER in place of a positive value.
   - Wholesale prices are strictly excluded (zero dealer ask/bid).
   - AI Estimate (`aiValue`) is strictly secondary and never displaces positive CDN retail in the primary value slot.
   - AI replica images: permitted strictly in labeled `ai_replica_images` collection, and NEVER displayed as primary, card, or index image.
7. **Real Call-Site Resolvers & List Sources (Resolving SAG #7):**
   - Completely drop uncited "Global Search" pathway.
   - Explicitly cite real list sources: `docs` (`List<CollectionRow>`) sourced from `rows = _sortedRows(_filteredRows(_expandedRows()))`.
   - Provide exact data extraction, parent-doc resolution from `_cachedCoinsDocs`, index resolution (`row` for Table View, `index` for Cards View), and `CoinModel` instantiation for all five call sites.

---

## 2. Ground-Truth Verbatim Code Citations (`origin/p7-v8.9`)

All citations verified against `c:\Users\ericd\Documents\MyVertexProject\numista_mobile\lib\screens\my_collection_screen.dart` and `numista_mobile\lib\screens\coin_detail_screen.dart` on branch `p7-v8.9`.

### 2.1 Table View Cell Tap (Call Site 1)
In `my_collection_screen.dart` lines 2733–2736:
```dart
2733:             // For virtual children, inspector/detail navigate to parent
2734:             final effectiveId = crw.isVirtualChild ? (crw.parentDocId ?? crw.id) : crw.id;
2735: 
2736:             void onTap() => _showCoinInspectorDialog(effectiveId, m);
```
- **Context:** Pinned table cell tap in `_buildDataTable(List<CollectionRow> docs, {bool advanced = false})`. `crw` is `docs[row]`, `m` is `crw.data`.

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
- **Context:** Actions column (col 0) info icon `Icons.info_outline`. For virtual children (Site 2, line 2761), resolves `parentDoc` from `_cachedCoinsDocs`. For normal coins (Site 3, line 2773), builds `CoinModel` from `m` and `crw.id`.

### 2.3 Cards View Card Tap (Call Site 4)
In `my_collection_screen.dart` lines 3040–3045:
```dart
3040:           elevation: crw.id == _selectedCoinId ? 4 : 1,
3041:           child: InkWell(
3042:             onTap: () {
3043:               setState(() => _selectedCoinId = effectiveId);
3044:               _showCoinInspectorDialog(effectiveId, m);
3045:             },
```
- **Context:** In `_buildCardGrid(List<CollectionRow> docs, {bool advanced = false})`, `crw` is `docs[index]`, `m` is `crw.data`. Tapping the card invokes `_showCoinInspectorDialog(effectiveId, m)`.

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
- **Context:** In `_buildCardGrid`, inside the parent set indicator chip for child coins. Tapping retrieves `parentDoc` from `_cachedCoinsDocs` and opens `_showCoinInspectorDialog(parentDoc.id, parentDoc.data())`.

### 2.5 Verbatim Ground Truth: Values, eBay Action & Storage Privacy Defect in Legacy Inspector
In `my_collection_screen.dart` lines 3849–3864:
```dart
3849:     return Row(children: [
3850:       Expanded(child: _metricCard('Est. Value', data[_F.aiValue]?.toString() ?? '--', Color(0xFF1A73E8), Icons.attach_money)),
3851:       SizedBox(width: 10),
3852:       Expanded(child: _metricCard('Melt Value', meltStr, Color(0xFF34A853), Icons.blur_circular_outlined)),
3853:       SizedBox(width: 10),
3854:       Expanded(child: _metricCard('Grade', data[_F.condition]?.toString() ?? '--', Color(0xFFF9AB00), Icons.grade_outlined)),
3855:       SizedBox(width: 10),
3856:       Expanded(child: _metricCard(
3857:           'Live eBay',
3858:           _ebayPrices[_selectedCoinId] ?? 'Check >',
3859:           Color(0xFFE53935),
3860:           Icons.shopping_cart_outlined,
3861:           onTap: () => _onSearchEbay(data),
3862:       )),
3863:     ]);
```
And in `my_collection_screen.dart` lines 3989–3999:
```dart
3989:       section('PURCHASE & STORAGE', [
3990:         // Format cost as currency ($XX.XX)
3991:         ['Cost',        _formatCost(data[_F.cost]?.toString())],
3992:         ['Date',        data[_F.purchaseDate]?.toString()],
3993:         ['Retailer',    data[_F.retailer]?.toString()],
3994:         ['Item #',      data[_F.retailerItemNo]?.toString()],
3995:         ['Invoice #',   data[_F.retailerInvoice]?.toString()],
3996:         ['Storage',     data[_F.storageLocation]?.toString()],
3997:         ['Ref #',       data[_F.personalRef]?.toString()],
3998:         ['Notes',       (data['Notes'] ?? data['notes'] ?? data[_F.personalNotes] ?? data['personalNotes'])?.toString()],
3999:       ]),
```
- **Defects:**
  1. Financial valuations (`Est. Value` at 3850, `Melt Value` at 3852, `Cost` at 3991) and physical storage location (`Storage` at 3996) are co-displayed in the same dialog body.
  2. Line 3861 executes `_onSearchEbay(data)` launching an unvetted third-party marketplace query.
  3. `Est. Value` at line 3850 displays ungrounded `data[_F.aiValue]` directly instead of verified CDN CPG retail.

### 2.6 Contrast Defect in Legacy Modal Header
In `coin_detail_screen.dart`:
```dart
59: Color _kDark(BuildContext c) => _isDarkCtx(c) ? const Color(0xFF0B1120) : const Color(0xFFF4F4F2);
...
892:     return Container(
893:       color: _kDark(context),
894:       padding: const EdgeInsets.fromLTRB(20, 14, 12, 16),
...
918:                   Text(title,
919:                     style: const TextStyle(
920:                       color: Colors.white, fontSize: 18,
921:                       fontWeight: FontWeight.bold, height: 1.3),
922:                   ),
```
- **Defect:** In light mode, `_kDark(context)` returns `#F4F4F2`. Text color is hardcoded `Colors.white`, resulting in white text on cream background (~1.1:1 contrast ratio, failing WCAG AA 4.5:1).

---

## 3. Real Call-Site Bindings & Unified Component Architecture

### 3.1 Real List Source & Index Resolution
- **List Source:** In `my_collection_screen.dart`, both Table and Cards views operate on the filtered, sorted collection rows:
  ```dart
  final allRows = _expandedRows();
  final rows    = _sortedRows(_filteredRows(allRows)); // List<CollectionRow>
  ```
- **Index Resolution:**
  - In Table View: `vicinity.row` directly indexes `rows[row]`.
  - In Cards View: Grid item `index` directly indexes `rows[index]`.
  - Both views pass `rows` as `List<CollectionRow> coinList` and the item index as `currentIndex` to enable `Previous coin` / `Next coin` navigation across all filtered items.

### 3.2 Exact Per-Site Dispatch & Legacy Fallback
All five call sites in `my_collection_screen.dart` are wrapped with the non-const feature flag `kUnifiedCoinDetailsEnabled`:

```dart
// ── Call Site 1: Table cell tap (line 2736) ──────────────────────────────────
void onTap() {
  if (!kUnifiedCoinDetailsEnabled) {
    _showCoinInspectorDialog(effectiveId, m);
    return;
  }
  final CoinModel targetCoin;
  if (crw.isVirtualChild) {
    final parentDoc = _cachedCoinsDocs.where((d) => d.id == crw.parentDocId).firstOrNull;
    final parentData = (parentDoc?.data() as Map<String, dynamic>?) ?? m;
    targetCoin = CoinModel.fromMap(parentData, effectiveId);
  } else {
    targetCoin = CoinModel.fromMap(m, crw.id);
  }
  UnifiedCoinDetailScreen.show(
    context,
    coin: targetCoin,
    coinList: docs,
    currentIndex: row,
    spotPrices: _spotPrices,
    isPublicGuestMode: false,
  );
}

// ── Call Site 2: Table info icon on virtual child (lines 2754–2770) ──────────
if (crw.isVirtualChild) {
  final parentDoc = _cachedCoinsDocs.where((d) => d.id == crw.parentDocId).firstOrNull;
  if (parentDoc == null) return;
  final parentData = (parentDoc.data() as Map<String, dynamic>?) ?? {};
  final coin = CoinModel.fromMap(parentData, parentDoc.id);
  if (!kUnifiedCoinDetailsEnabled) {
    CoinDetailScreen.show(context, coin: coin, spotPrices: _spotPrices, ...);
    return;
  }
  UnifiedCoinDetailScreen.show(
    context,
    coin: coin,
    coinList: docs,
    currentIndex: row,
    spotPrices: _spotPrices,
    isPublicGuestMode: false,
  );
}

// ── Call Site 3: Table info icon on normal coin (lines 2771–2780) ────────────
else {
  final coin = CoinModel.fromMap(m, crw.id);
  if (!kUnifiedCoinDetailsEnabled) {
    CoinDetailScreen.show(context, coin: coin, spotPrices: _spotPrices, ...);
    return;
  }
  UnifiedCoinDetailScreen.show(
    context,
    coin: coin,
    coinList: docs,
    currentIndex: row,
    spotPrices: _spotPrices,
    isPublicGuestMode: false,
  );
}

// ── Call Site 4: Cards grid card tap (line 3044) ─────────────────────────────
onTap: () {
  setState(() => _selectedCoinId = effectiveId);
  if (!kUnifiedCoinDetailsEnabled) {
    _showCoinInspectorDialog(effectiveId, m);
    return;
  }
  final CoinModel targetCoin;
  if (crw.isVirtualChild) {
    final parentDoc = _cachedCoinsDocs.where((d) => d.id == crw.parentDocId).firstOrNull;
    final parentData = (parentDoc?.data() as Map<String, dynamic>?) ?? m;
    targetCoin = CoinModel.fromMap(parentData, effectiveId);
  } else {
    targetCoin = CoinModel.fromMap(m, crw.id);
  }
  UnifiedCoinDetailScreen.show(
    context,
    coin: targetCoin,
    coinList: docs,
    currentIndex: index,
    spotPrices: _spotPrices,
    isPublicGuestMode: false,
  );
}

// ── Call Site 5: Cards grid parent-set chip tap (line 3122) ──────────────────
onTap: () {
  final parentId = m['parent_set_id'].toString();
  final parentDoc = _cachedCoinsDocs.where((d) => d.id == parentId).firstOrNull;
  if (parentDoc != null) {
    final parentData = (parentDoc.data() as Map<String, dynamic>?) ?? {};
    if (!kUnifiedCoinDetailsEnabled) {
      _showCoinInspectorDialog(parentDoc.id, parentData);
      return;
    }
    final parentCoin = CoinModel.fromMap(parentData, parentDoc.id);
    final parentIndex = docs.indexWhere((r) => r.id == parentDoc.id);
    UnifiedCoinDetailScreen.show(
      context,
      coin: parentCoin,
      coinList: docs,
      currentIndex: parentIndex >= 0 ? parentIndex : 0,
      spotPrices: _spotPrices,
      isPublicGuestMode: false,
    );
  }
}
```

### 3.3 Header Component (`_UnifiedHeader`)
- **Background:** Crisp pure white (`#ffffff`) in light mode; Deep charcoal (`#0f172a`) in dark mode.
- **Coin Title:** 32px bold typography in `#0b1a2e` (Deep Navy) in light mode and `#f8fafc` in dark mode (**17.5:1 contrast ratio, WCAG AAA compliant**).
- **Subtitle:** 20px regular font in `#334155` (e.g., `San Francisco · 90% Silver · United States`).
- **Touch Targets & Controls:**
  - `◀ Previous coin`: Outlined button, minimum height ≥52px, text + icon. Disabled when `currentIndex == 0`.
  - `Next coin ▶`: Outlined button, minimum height ≥52px, text + icon. Disabled when `currentIndex >= coinList.length - 1`.
  - `✕ Close`: Text button with clear label "Close", minimum height ≥52px.

### 3.4 Media & Imagery Rules
- **Side-by-Side Dual Photos:** Obverse (Front) and Reverse (Back) displayed in equal-width aspect-ratio containers with label chips ("Front", "Back").
- **Asset Grounding:**
  - User-uploaded photos take absolute first priority.
  - Reference photos from verified CDN take secondary priority.
  - AI replicas: Allowed **strictly** within the labeled `ai_replica_images` collection and labeled `"AI Simulation (Reference Only)"`. **AI replica images are NEVER displayed as the primary photo, card thumbnail, or catalog index image.**
- **Empty State Fallback:** When no photo is available, displays a friendly gold-outlined coin silhouette icon (`Icons.monetization_on_outlined`) with an `"Add a photo"` action prompt. **Folder icons (`Icons.folder_open`) are permanently eliminated.**

### 3.5 Values & Physical Storage Mutual Privacy Gate
In compliance with Founder Eric's binding privacy rules:
1. **Default State:**
   - Financial valuation metrics (Purchase Price, Cost Basis, Melt Value, CPG Retail Estimated Market Value) are **hidden** behind a prominent `"Show values"` button.
   - Physical storage location is **strictly hidden**.
2. **Values Revealed:**
   - Tapping `"Show values"` displays verified Purchase Price, Melt Value, and CDN CPG Retail value.
   - Physical storage location remains **strictly suppressed**. Under no circumstances do financial figures and physical storage location ever share a viewport.
3. **Session Persistence (Founder Locked Decision #2):**
   - Once `"Show values"` is tapped, values remain visible as the user steps through `Previous coin` / `Next coin`.
   - Values revert to hidden immediately upon modal `Close`.
4. **Permanent Removal of Fictional Pin Service:** Fictional `StorageLocationPinService` is deleted. Physical storage location remains blanked across all views until a formal crypto/PIN security model receives a dedicated typed YES from Founder Eric.

---

## 4. Strict Public / Guest Mode Specification

When `UnifiedCoinDetailScreen` is opened from the Public Catalog or an unauthenticated session:
```dart
UnifiedCoinDetailScreen.show(
  context,
  coin: publicCatalogCoin,
  isPublicGuestMode: true, // STRICT GUEST SANDBOX
);
```

### 4.1 Strict Guest Hide-List
In Public / Guest mode (`isPublicGuestMode == true`), the following elements are **hard-suppressed and completely omitted from the widget tree**:
1. **Private Financial Metrics:** Purchase Price, Cost Basis, Purchase Date, and Invoice Number.
2. **Sourcing Data:** Retailer / Seller Name, Item Number, and Personal Reference Code.
3. **Physical Storage:** Physical Storage Location.
4. **Values Toggle:** The private `"Show values"` toggle button is omitted.
5. **Private Notes:** Private user notes and collection annotations.
6. **Mutation Actions:** Edit, Delete, Verify, and Wishlist buttons are omitted.
7. **Redacted Private Tab:** The entire private "Purchase & value" tab is completely hidden/suppressed.

### 4.2 Public Pricing Visibility (Resolving SAG #6)
- **Positive CPG Retail Shown Outside Redacted Area:** Guests **must** see verified CDN CPG retail (`cpgRetail`) prominently displayed in the public **Overview** tab / hero valuation slot.
- **Valuation Pending Rule:** A gold styled `'Valuation Pending'` chip is rendered **only** when `cpgRetail` is missing (`null`), empty, or `<= 0`. A positive retail figure is **never** displaced by `'Valuation Pending'`.
- **Wholesale Strictly Excluded:** Zero dealer ask, wholesale sheets, or raw trade bids.
- **AI Estimate Demoted:** AI estimates (`aiValue`) are strictly secondary and displayed only as a labeled sub-caption (`"AI Estimate (Experimental)"`). AI estimates **never** displace positive CDN CPG retail in the primary slot.

---

## 5. Pricing & Marketplace Action Rules

1. **Primary Retail Source:** All valuation figures are sourced strictly and exclusively from **CDN CPG retail** (`cpgRetail`).
2. **Complete Removal of Outbound eBay Action:** The live eBay card and `_onSearchEbay(data)` action (legacy line 3861) are completely removed from the unified view. No marketplace search queries are launched.
3. **Strict Outbound Link Boundary:** No third-party outbound links are permitted anywhere in the unified view, with the sole exception of verified plain text links to Congress.gov in the Laws tab.

---

## 6. Laws Tab Architecture & Congress.gov Boundaries

Founder Eric's binding mandate (AMEND 5 Nov 2:44 PM ET) permits outbound links **strictly** to Congress.gov via plain text links (`target=_blank`, `rel=noopener`).

### 6.1 Real Architecture vs App Code
- **Firestore Read:** Grounded in `numista_mobile/lib/screens/coin_detail_screen.dart` line 2960: reads Firestore document `metadata/coin_legislation`.
- **Static Fallback:** Falls back to verified catalog constants `_kDefaultLaws[lawKey]`.
- **Zero Client Writer / Zero Live API Execution:**
  - `coin_legislation_map.py` is a backend tool and is **NOT executed** during build or runtime.
  - The mobile app contains **zero client-side Congress.gov API writers** and performs **zero Firestore writes** from the client.
- **Outbound Link Formatting:**
  - Formatted strictly as plain text links using `launchUrl(Uri.parse(law['congress_url']), mode: LaunchMode.externalApplication)` on mobile and `<a href="..." target="_blank" rel="noopener noreferrer">` on web.
  - **Zero icon buttons (`Icons.open_in_new` omitted per review).**
  - **Zero Congress.gov imagery fetched or rendered.**
- **Attribution & Editorial Labels:**
  - When verified catalog legislation is present: `Source: Numista.AI catalog (checked)`.
  - When unverified external statutory summary is rendered: Prominently labeled `"From Congress.gov, not yet checked by us"`.
- **Fail-Closed State:** If Congress.gov data is missing, rate-limited, or throws an error:
  - Renders clean labeled empty state: `"Morgan hasn't found the law for this coin yet"`.
  - **NEVER invents laws or generates hallucinated statutory claims.**

---

## 7. Consolidated 6-Tab Specification

| Tab Name | Content & Purpose | Sourced from Legacy Inspector | Sourced from Legacy Details Modal | Guest Mode Visibility |
|---|---|---|---|---|
| **1. Overview** | Specifications, metal, grade, mintage, and **public CDN CPG retail price**. | Identity (Year, Mint, Denomination, Series, Metal); Grade tile. | Details tab; Proof badge; Subtitle. | **Full (Always shows positive CPG retail)** |
| **2. Purchase & value** | Private cost, purchase date, invoice, retailer, and private owner notes. Gated by "Show values". | Cost, Date, Retailer, Invoice #. | Financials tab; Provenance tab. | **REDACTED (Hidden in Guest Mode)** |
| **3. Morgan's notes** | AI analysis, series insights, diagnostic attribution notes. | — | AI Insights tab; "Morgan is fairly sure" confidence indicator. | **Full (Educational)** |
| **4. History** | Historical background, designer credits, mintage statistics. | — | History tab; Mintage figures; Obverse/Reverse designers. | **Full (Educational)** |
| **5. Laws** | Authorizing legislation (Catalog checked or labeled Congress.gov). | — | Legislation tab (`metadata/coin_legislation`). | **Full (Statutory Reference)** |
| **6. Known errors** | Documented varieties, repunched mintmarks (RPMs), strike errors. | — | Known Errors tab; variety cross-references. | **Full (Reference)** |

---

## 8. Bottom Action Bar: Strictly Read-Only Initial Release

In resolution of CoS Must-Fix #2 and SAG Must-Fix #5:
1. **Initial Release is 100% Read-Only:**
   - The initial release of `UnifiedCoinDetailScreen` introduces **zero Firestore database writes, zero rules modifications, zero schema changes, and zero database seeding**.
2. **Mutation Controls Inert/Disabled:**
   - In authenticated user mode, `Edit`, `Wishlist`, and `Delete` action controls are either completely omitted from the layout or rendered visually inert/disabled with `onTap: null`.
   - Legacy mutation callbacks (`onEdited`, `onDeleted`) are **not wired to active database writers** in this build.
   - Ask Morgan research request logging is **disabled** (does not write to any Firestore request collection).
3. **Subsequent Founder YES Required:**
   - All Firestore mutation capabilities, edit dialogs, delete confirmations, and wishlist toggles remain strictly parked until Founder Eric explicitly reviews the mutation architecture and issues a dedicated typed YES.

---

## 9. Rollback Strategy & Feature Flag Configuration

### 9.1 Non-Const Feature Flag
In `numista_mobile/lib/config/feature_flags.dart`:
```dart
/// Feature flag governing the Unified Coin Details View rollout.
/// Defaults to false; non-const to allow instant runtime rollback and test mutability.
bool kUnifiedCoinDetailsEnabled = false;
```
- By defaulting to `false`, new code is dormant upon landing.
- Enabling requires an explicit runtime assignment (`kUnifiedCoinDetailsEnabled = true;`).
- In automated test suites, tests can freely assign `kUnifiedCoinDetailsEnabled = true` or `false` without requiring rebuilds.

### 9.2 Real Ancestor Git Rollback Procedure (Resolving CoS #1 & SAG #1)
- **Forbidden:** `git revert HEAD...9f04550a` is strictly struck and banned. `9f04550a` is locked `origin/main` and is **not an ancestor** of `origin/p7-v8.9`.
- **Pre-Execute Anchor Capture:**
  Before executing any commit for the Unified Details build on `origin/p7-v8.9`, the engineer must capture and record the exact pre-execute commit hash:
  ```bash
  PRE_EXEC_SHA=$(git rev-parse HEAD)
  echo "Pre-execute baseline SHA: $PRE_EXEC_SHA"
  ```
- **Clean Git Revert Procedure:**
  If code rollback is necessary on `p7-v8.9`:
  ```bash
  # Revert all commits introduced during the execution session cleanly
  git revert --no-edit $PRE_EXEC_SHA..HEAD
  git push origin p7-v8.9
  ```
- **Firebase Hosting Release Restore:**
  Because preview channels are used for testing prior to merge:
  ```bash
  # If deployed to a Firebase Hosting preview channel:
  firebase hosting:channel:delete preview-unified-details --force
  # If deployed to live channel by mistake, immediately restore live from previous release:
  firebase hosting:clone <site-id>:live <site-id>:rollback-temp
  firebase hosting:releases:list
  ```

---

## 10. Automated Machine-Checkable Verification Plan

All tests authored in `numista_mobile/test/screens/unified_coin_detail_screen_test.dart`:

### 10.1 Call-Site Routing & Legacy Fallback Test
- Instantiate each of the 5 call sites with `kUnifiedCoinDetailsEnabled = false`:
  - Assert that Sites 1, 4, 5 invoke `_showCoinInspectorDialog`.
  - Assert that Sites 2 & 3 invoke `CoinDetailScreen.show`.
- Set `kUnifiedCoinDetailsEnabled = true`:
  - Assert that all 5 sites launch `UnifiedCoinDetailScreen`.

### 10.2 Strict Read-Only & Zero Write Callback Test
- In `UnifiedCoinDetailScreen`, tap all visible buttons (navigation, tabs, header, close, action bar):
  - Assert that **zero Firestore write methods** (`add`, `set`, `update`, `delete`) are called.
  - Assert that no legacy mutation callbacks are executed.

### 10.3 Public Guest Mode & CPG Retail Visibility Test
- Launch with `isPublicGuestMode: true` and a coin with `cpgRetail: 1250.00`:
  - Assert that `"$1,250.00"` is rendered prominently on the Overview surface.
  - Assert that `'Valuation Pending'` is NOT present.
  - Assert that private tab `"Purchase & value"` is NOT in the widget tree.
  - Assert that `"Show values"` button is NOT in the widget tree.
  - Assert that cost, purchase date, retailer, invoice, and storage location widgets are NOT in the widget tree.
- Launch with `isPublicGuestMode: true` and a coin with `cpgRetail: 0` or `null`:
  - Assert that styled gold `'Valuation Pending'` chip IS rendered.

### 10.4 Mutual Privacy Gate Test
- Launch in authenticated user mode (`isPublicGuestMode: false`):
  - Assert that financial valuation metrics are hidden by default.
  - Assert that physical storage location is hidden by default.
  - Tap `"Show values"`: Assert valuation figures are displayed; assert physical storage location remains STRICTLY hidden.
  - Tap `Next coin ▶`: Assert valuation figures remain displayed (session persistence).
  - Tap `✕ Close`: Assert valuation state resets to hidden on next open.

### 10.5 Laws Tab Fail-Closed & Outbound Link Test
- Render Laws tab with checked catalog law:
  - Assert text `Source: Numista.AI catalog (checked)` is displayed.
  - Assert Congress.gov link contains `target=_blank` and `rel=noopener`.
  - Assert zero Congress.gov images are requested.
  - Assert zero eBay, PCGS, or NGC links are rendered.
- Simulate Congress.gov error/timeout:
  - Assert empty state text `"Morgan hasn't found the law for this coin yet"` is displayed without unverified legal claims.

---

## 11. Multi-Agent Review Chain & Approvals

In compliance with Founder Eric's binding review sequence (Argon dropped entirely per typed YES 5 Nov 18:07 ET):
1. **Author:** Antigravity CoS v4 / Catalog Night Team (`ba2bfdb2`)
2. **Reviewer 1:** Grok Bot Chief of Staff (Target: `>= 95 / 100`)
3. **Reviewer 2:** Stand Alone Grok (SAG grok-4.7, Target: `>= 95 / 100`)
4. **Final Gate:** Founder Eric typed **YES** prior to any code modification, build execution, or deployment.

**Locks Remaining Enforced:** `origin/main` locked at `9f04550a`; Stripe strictly OFF; strict PLAN ONLY mode.
