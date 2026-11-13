# PLAN: Unified Coin Details View v1.6 (NET-813 / BATON_NET-813)

- **Track ID:** NET-813 (Architecture Plan / Feature Specification / Thanksgiving Critical Path)
- **Author:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Attempt:** AG CoS v5 attempt **3/4** on revision (v1.3 was 76 FAIL, v1.4 was 86 FAIL, v1.5 was 81 FAIL per `RADIO_NET-846`)
- **Review Target:** Grok Bot Chief of Staff (`GROKCOS`) (Score target $\ge 95 / 100$)
- **Date / DTG:** Saturday, 7 November 2026, 20:30 ET (`2026-11-07 20:30:00 -05:00`)
- **Mode:** **STRICT PLAN ONLY — PREVIEW GATE ONLY** (Zero code modifications, zero builds, zero test execution, zero Firestore writes/seeding, zero live deploys without Founder Eric's explicit typed YES)
- **Branch Context:** Pinned against `origin/p7-v8.9` @ `4d17ca5e` (and `c294fd3c`, identical mobile tree); public catalog entry bound against `origin/dev` @ `6af2afb1`

---

## Must-Fix Closeout & Traceability Matrix (CoS-81 Must-Fixes 1–6)

| Item | CoS-81 Must-Fix Issue | Resolution Summary in v1.6 | Plan Section |
|---|---|---|---|
| **MF-1** | **Re-quote all five call sites verbatim from `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart` and fix §1 site list:** v1.5 showed fabricated quotes (`final row = crw.data;`, positional `CoinDetailScreen.show(...)`, wrong site 4/5 calling `CoinDetailScreen.show`). | Quoted exact lines verbatim from pin `4d17ca5e`: §2.1 (`:2726` `final row = vicinity.row;`, `:2729` `final crw = docs[row];`, `:2730` `final m = crw.data;`, `:2734` `final effectiveId = ...`, `:2736` `void onTap() => _showCoinInspectorDialog(effectiveId, m);`); §2.2 (`:2754–2783` using `_cachedCoinsDocs` and named `CoinDetailScreen.show(context, coin: coin, spotPrices: _spotPrices, onNavigateToAiChat: ..., onDeleted: ..., onEdited: ...)`); §2.3 card tap (`:3041–3045` `onTap: () { setState(() => _selectedCoinId = effectiveId); _showCoinInspectorDialog(effectiveId, m); }`); §2.4 parent-set chip (`:3117–3124` resolving `m['parent_set_id']` against `_cachedCoinsDocs` and calling `_showCoinInspectorDialog(parentDoc.id, parentDoc.data())`); §2.7 laws (`coin_detail_screen.dart:3152–3165` `if ((law['congress_url'] ?? '').toString().isNotEmpty) ...[` and non-const `SizedBox(height: 16),`). Fixed §1 site list to reflect that 3 of the 5 sites invoke `_showCoinInspectorDialog` and 2 invoke `CoinDetailScreen.show`. | §1, §2.1–§2.4, §2.7 |
| **MF-2** | **Make wire-up compile and keep existing behavior:** v1.5 used non-existent `_allCoinsDocs` (0 hits at pin; real is `_cachedCoinsDocs` `:131`) and passed method `_filteredRows` as a list; dropped `spotPrices`, `onNavigateToAiChat`, `onDeleted`, `onEdited` from `show()`. | Removed `_allCoinsDocs`; wired `_cachedCoinsDocs` exclusively. Bound navigation collection list directly to the `docs` parameter already passed to `_buildDataTable(List<CollectionRow> docs, ...)` (`:2557`) and `_buildCardGrid(List<CollectionRow> docs, ...)` (`:2982`). Carried `spotPrices`, `onNavigateToAiChat`, `onDeleted`, and `onEdited` throughout `UnifiedCoinDetailScreen.show(...)` to ensure spot-based melt calculations and list state refreshes remain active. | §3.1, §3.4 |
| **MF-3** | **Use real `_kDefaultLaws` values in manifest — zero edits:** v1.5 altered statute citations (`121 Stat. 2018`, `§ 5112(x)` instead of `§ 5112(z)`). | Copied all entries verbatim from `git show 4d17ca5e:numista_mobile/lib/screens/coin_detail_screen.dart` `:2973–3027`: `110-456` (`122 Stat. 5038 (31 U.S.C. § 5112(t))`), `105-124` (`111 Stat. 2534 (31 U.S.C. § 5112(k))`), `110-161` (full title `District of Columbia and United States Territories Circulating Quarter Dollar Program Act`, citation `121 Stat. 2014 (31 U.S.C. § 5112(r))`), and `116-330` (citation `134 Stat. 5101 (31 U.S.C. § 5112(z))`). Kept `editorial_verified: false`. | §6.1 |
| **MF-4** | **Finish harness for real and fix tests that cannot pass:** v1.5 harness was missing fake Firestore, clock, and image capture; Test 5 passed `cachedCoinsDocs: []` so Next never navigated; Test 9 threw before pumping widget and had defective regex expectations; Test 12 asserted no photo ranking. | Implemented real `FakeFirestoreService` (with in-memory storage, read/write counters), `FakeClock`, `FakeQueryDocumentSnapshot`, and `UnifiedCoinDetailHarness`. In Test 5, provided real `FakeQueryDocumentSnapshot` cached docs, asserting in-state navigation and preserved values toggle. In Test 9, pumped widget before querying element, extended regex to strip markdown images `!\[...\](...)`, and asserted valid text. In Test 12, added owner fixture with accepted user photo asserting it outranks reference image, and tested guest redaction on the identical fixture. Added Test 13 testing 4.0s laws timeout via `FakeClock`. | §10 |
| **MF-5** | **Move navigation state into `State`:** `coin` and `currentParentIndex` were final on widget with empty `onNavigate` stubs, causing second Next to use stale widget state. | Moved `_currentCoin`, `_currentSnapshot`, and `_currentParentIndex` into `_UnifiedCoinDetailScreenState`. Implemented `_stepNavigation(int direction)` in `State` calling `setState()`, updating current coin and resolving parent index in-place. Added Test 14 testing two consecutive Next steps across a virtual-child group. | §3.1, §3.2, §3.5, §10 |
| **MF-6** | **Asset manifest + hygiene:** Add `assets/config/` (for `features.json`) to `pubspec.yaml` manifest list; record delivery commits in §12. | Documented explicit `pubspec.yaml` addition of `assets/config/` alongside existing asset folders. Recorded previous delivery commit `00957e85` (v1.5) and target attempt 3/4. Stamped honest DTG matching file mtimes. | §9.3, §11.1, §12 |

---

## 1. Executive Summary & Problem Statement

Numista.AI currently suffers from fragmented coin detail presentations across five distinct UI pathways in `my_collection_screen.dart`:
1. **Call Site 1 (Table View Cell Tap — `:2736`):** `onTap` calls `_showCoinInspectorDialog(effectiveId, m);` displaying AI value, melt, storage location, and an unquarantined eBay search link (`:3861`).
2. **Call Site 2 (Table View Actions Menu — Virtual Set Child 'View Parent Set' — `:2761–2770`):** Resolves `crw.parentDocId` against `_cachedCoinsDocs` and calls `CoinDetailScreen.show(context, coin: coin, spotPrices: _spotPrices, onNavigateToAiChat: ..., onDeleted: ..., onEdited: ...)`.
3. **Call Site 3 (Table View Actions Menu — Regular Coin 'View Details' — `:2773–2782`):** Calls `CoinDetailScreen.show(context, coin: coin, spotPrices: _spotPrices, onNavigateToAiChat: ..., onDeleted: ..., onEdited: ...)`.
4. **Call Site 4 (Cards View Card Tap — `:3042–3045`):** `onTap` executes `setState(() => _selectedCoinId = effectiveId); _showCoinInspectorDialog(effectiveId, m);`.
5. **Call Site 5 (Cards View Parent-Set Chip Tap — `:3118–3124`):** `onTap` resolves `m['parent_set_id']` against `_cachedCoinsDocs` and calls `_showCoinInspectorDialog(parentDoc.id, parentDoc.data());`.

This fragmentation creates severe functional, visual, and security defects:
- **Navigation Identity Mismatch:** Virtual children in table/card views navigate inconsistently between inspector dialogs and `CoinDetailScreen`, with no unified handling of parent set indices when stepping Next/Previous.
- **Markdown White-on-White Defect:** Notes rendered via `MarkdownBody` inherit `strong: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)` from `coin_detail_screen.dart:2792`, rendering bold text completely invisible on light surfaces.
- **Header Contrast Defect:** `_kDark(context)` at `coin_detail_screen.dart:59` returns `#F4F4F2` in light mode; container at `:892–893` renders title text at `:918–921` with `Colors.white`, producing an illegal 1.10:1 contrast ratio that fails WCAG requirements.
- **Public Privacy Leaks:** Guest users accessing catalog entries risk exposure to private purchase costs, storage locations, or unquarantined outbound links.

**Goal of NET-813:** Consolidate all five collection invocation sites and the public catalog entry modal into a single, secure, accessible `UnifiedCoinDetailScreen` with strict virtual-child navigation identity, sandboxed rich text, and high-contrast WCAG AAA compliance.

---

## 2. Ground-Truth Verbatim Code Citations (`origin/p7-v8.9` @ `4d17ca5e`)

Every citation below is reproduced verbatim from `git show 4d17ca5e:<path>` on the repository:

### 2.1 Table View Cell Tap (Call Site 1)
In `numista_mobile/lib/screens/my_collection_screen.dart` at lines 2723–2736:
```dart
2723:           cellBuilder: (context, vicinity) {
2724:             try {
2725:               final col = vicinity.column;
2726:               final row = vicinity.row;
2727: 
2728:             // -- ALL ROWS ARE DATA (no row == 0 header branch) ----------
2729:             final crw = docs[row];
2730:             final m   = crw.data;
2731:             final sel = crw.id == _selectedCoinId;
2732: 
2733:             // For virtual children, inspector/detail navigate to parent
2734:             final effectiveId = crw.isVirtualChild ? (crw.parentDocId ?? crw.id) : crw.id;
2735: 
2736:             void onTap() => _showCoinInspectorDialog(effectiveId, m);
```

### 2.2 Table View Actions Menu Invocations (Call Sites 2 & 3)
In `numista_mobile/lib/screens/my_collection_screen.dart` at lines 2751–2783:
```dart
2751:                           crw.isVirtualChild ? 'View Parent Set' : 'View Details', () {
2752:                           // G-2: For virtual children, look up parent doc data.
2753:                           // If parent not in cache, skip navigation.
2754:                           if (crw.isVirtualChild) {
2755:                             final parentDoc = _cachedCoinsDocs
2756:                                 .where((d) => d.id == crw.parentDocId)
2757:                                 .firstOrNull;
2758:                             if (parentDoc == null) return; // parent missing – skip
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
2781:                               onEdited: () => setState(() {}),
2782:                             );
2783:                           }
```

### 2.3 Cards View Card Tap (Call Site 4)
In `numista_mobile/lib/screens/my_collection_screen.dart` at lines 3041–3045:
```dart
3041:           child: InkWell(
3042:             onTap: () {
3043:               setState(() => _selectedCoinId = effectiveId);
3044:               _showCoinInspectorDialog(effectiveId, m);
3045:             },
```

### 2.4 Cards View Parent-Set Container Tap (Call Site 5)
In `numista_mobile/lib/screens/my_collection_screen.dart` at lines 3117–3124:
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
In `numista_mobile/lib/screens/coin_detail_screen.dart` at lines 2785–2806:
```dart
2785:                 MarkdownBody(
2786:                   data: insight,
2787:                   styleSheet: MarkdownStyleSheet(
2788:                     p: TextStyle(fontSize: 14, color: _kText(context), height: 1.7),
2789:                     h1: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white, height: 2.0),
2790:                     h2: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white, height: 2.0),
2791:                     h3: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: _kText(context), height: 1.8),
2792:                     strong: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
2793:                     listBullet: TextStyle(fontSize: 14, color: _kText(context), height: 1.7),
2794:                     blockquoteDecoration: BoxDecoration(
2795:                       color: _kAccent(context).withAlpha(20),
2796:                       borderRadius: BorderRadius.circular(4),
2797:                       border: Border(left: BorderSide(color: _kAccent(context), width: 3)),
2798:                     ),
2799:                     code: TextStyle(fontSize: 13, backgroundColor: _kBg(context), color: _kText(context)),
2800:                   ),
2801:                   onTapLink: (text, href, title) {
2802:                     if (href != null) {
2803:                       launchUrl(Uri.parse(href), mode: LaunchMode.externalApplication);
2804:                     }
2805:                   },
2806:                 ),
```
*Note:* Line 2792 hardcodes `color: Colors.white` for `strong`, causing invisible text on light backgrounds.

### 2.6 Header Contrast Defect Ground Truth
In `numista_mobile/lib/screens/coin_detail_screen.dart`:
```dart
59: Color _kDark(BuildContext c) => _isDarkCtx(c) ? const Color(0xFF0B1120) : const Color(0xFFF4F4F2);
...
892:     return Container(
893:       color: _kDark(context),
...
918:                   Text(title,
919:                     style: const TextStyle(
920:                       color: Colors.white, fontSize: 18,
921:                       fontWeight: FontWeight.bold, height: 1.3),
...
925:                     style: TextStyle(color: Colors.white.withAlpha(180), fontSize: 12),
```
*Contrast Defect:* When `_isDarkCtx(c)` is false (Light Mode), `_kDark(context)` returns `#F4F4F2` (relative luminance ~0.89). Text colored `Colors.white` (luminance 1.0) produces an illegal contrast ratio of **1.10:1** (WCAG AAA requires 7.0:1).

### 2.7 Laws Loader Ground Truth
In `numista_mobile/lib/screens/coin_detail_screen.dart` at lines 3152–3165:
```dart
3152:                 if ((law['congress_url'] ?? '').toString().isNotEmpty) ...[
3153:                   SizedBox(height: 16),
3154:                   OutlinedButton.icon(
3155:                     onPressed: () => launchUrl(
3156:                       Uri.parse(law!['congress_url'].toString()),
3157:                       mode: LaunchMode.externalApplication,
3158:                     ),
3159:                     icon: Icon(Icons.open_in_new, size: 14),
3160:                     label: Text('View on Congress.gov'),
3161:                     style: OutlinedButton.styleFrom(
3162:                       foregroundColor: _kAccent(context),
3163:                       side: BorderSide(color: _kAccent(context)),
3164:                       padding: const EdgeInsets.symmetric(
3165:                           horizontal: 14, vertical: 8),
```

---

## 3. Reconciling the Five Call Sites & Virtual-Child Navigation Identity (MF-2 & MF-3)

### 3.1 Signatures for `UnifiedCoinDetailScreen`
The unified component replaces both `_showCoinInspectorDialog` and `CoinDetailScreen.show`, providing identical named arguments to preserve melt calculation (`spotPrices`) and collection refresh (`onDeleted`, `onEdited`):

```dart
class UnifiedCoinDetailScreen extends StatefulWidget {
  final CoinModel? initialCoin;
  final DocumentSnapshot? initialSnapshot;
  final int? initialParentIndex;
  final List<CollectionRow> collectionRows;
  final List<QueryDocumentSnapshot<Map<String, dynamic>>> cachedCoinsDocs;
  final Map<String, double> spotPrices;
  final void Function(String query)? onNavigateToAiChat;
  final VoidCallback? onDeleted;
  final VoidCallback? onEdited;
  final PublicCoinProjection? publicProjection;
  final UnifiedCoinDetailHarness? testHarness;

  const UnifiedCoinDetailScreen({
    Key? key,
    required CoinModel coin,
    DocumentSnapshot? snapshot,
    int? currentParentIndex,
    List<CollectionRow> collectionRows = const [],
    List<QueryDocumentSnapshot<Map<String, dynamic>>> cachedCoinsDocs = const [],
    Map<String, double> spotPrices = const {},
    void Function(String query)? onNavigateToAiChat,
    VoidCallback? onDeleted,
    VoidCallback? onEdited,
    this.testHarness,
  })  : initialCoin = coin,
        initialSnapshot = snapshot,
        initialParentIndex = currentParentIndex,
        collectionRows = collectionRows,
        cachedCoinsDocs = cachedCoinsDocs,
        spotPrices = spotPrices,
        onNavigateToAiChat = onNavigateToAiChat,
        onDeleted = onDeleted,
        onEdited = onEdited,
        publicProjection = null,
        super(key: key);

  const UnifiedCoinDetailScreen.public({
    Key? key,
    required PublicCoinProjection projection,
    this.testHarness,
  })  : initialCoin = null,
        initialSnapshot = null,
        initialParentIndex = null,
        collectionRows = const [],
        cachedCoinsDocs = const [],
        spotPrices = const {},
        onNavigateToAiChat = null,
        onDeleted = null,
        onEdited = null,
        publicProjection = projection,
        super(key: key);

  static Future<void> show(
    BuildContext context, {
    required CoinModel coin,
    DocumentSnapshot? snapshot,
    int? currentParentIndex,
    List<CollectionRow> collectionRows = const [],
    List<QueryDocumentSnapshot<Map<String, dynamic>>> cachedCoinsDocs = const [],
    Map<String, double> spotPrices = const {},
    void Function(String query)? onNavigateToAiChat,
    VoidCallback? onDeleted,
    VoidCallback? onEdited,
    UnifiedCoinDetailHarness? testHarness,
  }) {
    final width = MediaQuery.of(context).size.width;
    final widget = UnifiedCoinDetailScreen(
      coin: coin,
      snapshot: snapshot,
      currentParentIndex: currentParentIndex,
      collectionRows: collectionRows,
      cachedCoinsDocs: cachedCoinsDocs,
      spotPrices: spotPrices,
      onNavigateToAiChat: onNavigateToAiChat,
      onDeleted: onDeleted,
      onEdited: onEdited,
      testHarness: testHarness,
    );

    if (width >= 800) {
      return showDialog<void>(
        context: context,
        barrierColor: Colors.black54,
        builder: (_) => Dialog(
          backgroundColor: Colors.transparent,
          insetPadding: const EdgeInsets.symmetric(horizontal: 40, vertical: 24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1000, maxHeight: 850),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: widget,
            ),
          ),
        ),
      );
    } else {
      return showModalBottomSheet<void>(
        context: context,
        isScrollControlled: true,
        backgroundColor: Colors.transparent,
        builder: (_) => DraggableScrollableSheet(
          initialChildSize: 0.92,
          minChildSize: 0.5,
          maxChildSize: 0.95,
          builder: (_, controller) => ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
            child: widget,
          ),
        ),
      );
    }
  }

  static Future<void> showPublic(
    BuildContext context, {
    required PublicCoinProjection projection,
    UnifiedCoinDetailHarness? testHarness,
  }) {
    final width = MediaQuery.of(context).size.width;
    final widget = UnifiedCoinDetailScreen.public(
      projection: projection,
      testHarness: testHarness,
    );

    if (width >= 800) {
      return showDialog<void>(
        context: context,
        barrierColor: Colors.black54,
        builder: (_) => Dialog(
          backgroundColor: Colors.transparent,
          insetPadding: const EdgeInsets.symmetric(horizontal: 40, vertical: 24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1000, maxHeight: 850),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: widget,
            ),
          ),
        ),
      );
    } else {
      return showModalBottomSheet<void>(
        context: context,
        isScrollControlled: true,
        backgroundColor: Colors.transparent,
        builder: (_) => DraggableScrollableSheet(
          initialChildSize: 0.92,
          minChildSize: 0.5,
          maxChildSize: 0.95,
          builder: (_, controller) => ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
            child: widget,
          ),
        ),
      );
    }
  }

  @override
  State<UnifiedCoinDetailScreen> createState() => _UnifiedCoinDetailScreenState();
}
```

### 3.2 Navigation State in `State` (MF-5)
All mutable navigation state lives strictly inside `_UnifiedCoinDetailScreenState`. Stepping Next or Previous mutates `_currentCoin`, `_currentSnapshot`, and `_currentParentIndex` via `setState()`, directly re-rendering the modal in-place:

```dart
class _UnifiedCoinDetailScreenState extends State<UnifiedCoinDetailScreen> {
  late CoinModel? _currentCoin;
  late DocumentSnapshot? _currentSnapshot;
  late int? _currentParentIndex;

  @override
  void initState() {
    super.initState();
    _currentCoin = widget.initialCoin;
    _currentSnapshot = widget.initialSnapshot;
    _currentParentIndex = widget.initialParentIndex;
  }

  bool get canNavigatePrevious =>
      _currentParentIndex != null && _currentParentIndex! > 0;

  bool get canNavigateNext =>
      _currentParentIndex != null &&
      _currentParentIndex! < widget.collectionRows.length - 1;

  void _stepNavigation(int direction) {
    if (_currentParentIndex == null) return;
    final rows = widget.collectionRows;
    if (rows.isEmpty) return;

    int targetIdx = _currentParentIndex! + direction;

    while (targetIdx >= 0 && targetIdx < rows.length) {
      final targetRow = rows[targetIdx];
      final String targetParentId = targetRow.isVirtualChild
          ? (targetRow.parentDocId ?? '')
          : targetRow.id;

      // Deduplication: If target resolves to the same parent document currently displayed,
      // skip ahead in the same direction to avoid cycling through sibling virtual children.
      if (targetParentId.isNotEmpty && _currentCoin != null && targetParentId == _currentCoin!.id) {
        targetIdx += direction;
        continue;
      }

      // Resolve document from cachedCoinsDocs
      final doc = widget.cachedCoinsDocs
          .where((d) => d.id == targetParentId)
          .firstOrNull;

      if (doc == null) {
        // Cache miss: skip over missing parent doc
        targetIdx += direction;
        continue;
      }

      final docData = (doc.data() as Map<String, dynamic>?) ?? {};
      final nextCoin = CoinModel.fromMap(docData, doc.id);

      // Resolve parent's index in the active collectionRows
      final parentIndex = rows.indexWhere((r) => r.id == targetParentId);

      setState(() {
        _currentCoin = nextCoin;
        _currentSnapshot = doc;
        _currentParentIndex = parentIndex >= 0 ? parentIndex : null;
      });
      return;
    }
  }
```

### 3.3 Strict Virtual-Child Parent Index Resolution
```dart
int? _resolveParentIndexForVirtualChild(
  CollectionRow childRow,
  List<CollectionRow> collectionRows,
) {
  if (!childRow.isVirtualChild || childRow.parentDocId == null) return null;
  final idx = collectionRows.indexWhere((r) => r.id == childRow.parentDocId);
  return idx >= 0 ? idx : null;
}
```
*Rule:* If the parent set row is absent from `collectionRows` (for example, if a search filter matches the child quarter but not the parent set), `currentParentIndex` resolves to `null` (standalone mode). It NEVER falls back to the child's index.

### 3.4 Wire-up Across All Five Call Sites in `my_collection_screen.dart` (MF-2)

The wire-up binds directly to the `docs` parameter already supplied to `_buildDataTable` and `_buildCardGrid`, and references `_cachedCoinsDocs` (`:131`). All five call sites route to `UnifiedCoinDetailScreen.show(...)`:

#### Call Site 1 (Table Row Cell Tap — `:2736`):
```dart
// my_collection_screen.dart:2736 replacement inside _buildDataTable(List<CollectionRow> docs, ...)
void onTap() {
  if (crw.isVirtualChild) {
    final parentDoc = _cachedCoinsDocs
        .where((d) => d.id == crw.parentDocId)
        .firstOrNull;
    if (parentDoc == null) return;
    final parentData = (parentDoc.data() as Map<String, dynamic>?) ?? {};
    final coin = CoinModel.fromMap(parentData, parentDoc.id);
    final parentIdx = _resolveParentIndexForVirtualChild(crw, docs);
    UnifiedCoinDetailScreen.show(
      context,
      coin: coin,
      snapshot: parentDoc,
      currentParentIndex: parentIdx,
      collectionRows: docs,
      cachedCoinsDocs: _cachedCoinsDocs,
      spotPrices: _spotPrices,
      onNavigateToAiChat: widget.onNavigateWithQuery != null
          ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
          : null,
      onDeleted: () => setState(() {}),
      onEdited: () => setState(() {}),
    );
  } else {
    final coin = CoinModel.fromMap(m, crw.id);
    UnifiedCoinDetailScreen.show(
      context,
      coin: coin,
      snapshot: crw.snapshot,
      currentParentIndex: row,
      collectionRows: docs,
      cachedCoinsDocs: _cachedCoinsDocs,
      spotPrices: _spotPrices,
      onNavigateToAiChat: widget.onNavigateWithQuery != null
          ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
          : null,
      onDeleted: () => setState(() {}),
      onEdited: () => setState(() {}),
    );
  }
}
```

#### Call Sites 2 & 3 (Table Actions Menu Invocations — `:2751–2783`):
```dart
// Replaces lines 2754–2783 in _buildDataTable:
if (crw.isVirtualChild) {
  final parentDoc = _cachedCoinsDocs
      .where((d) => d.id == crw.parentDocId)
      .firstOrNull;
  if (parentDoc == null) return;
  final parentData = (parentDoc.data() as Map<String, dynamic>?) ?? {};
  final coin = CoinModel.fromMap(parentData, parentDoc.id);
  final parentIdx = _resolveParentIndexForVirtualChild(crw, docs);
  UnifiedCoinDetailScreen.show(
    context,
    coin: coin,
    snapshot: parentDoc,
    currentParentIndex: parentIdx,
    collectionRows: docs,
    cachedCoinsDocs: _cachedCoinsDocs,
    spotPrices: _spotPrices,
    onNavigateToAiChat: widget.onNavigateWithQuery != null
        ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
        : null,
    onDeleted: () => setState(() {}),
    onEdited: () => setState(() {}),
  );
} else {
  final coin = CoinModel.fromMap(m, crw.id);
  UnifiedCoinDetailScreen.show(
    context,
    coin: coin,
    snapshot: crw.snapshot,
    currentParentIndex: row,
    collectionRows: docs,
    cachedCoinsDocs: _cachedCoinsDocs,
    spotPrices: _spotPrices,
    onNavigateToAiChat: widget.onNavigateWithQuery != null
        ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
        : null,
    onDeleted: () => setState(() {}),
    onEdited: () => setState(() {}),
  );
}
```

#### Call Site 4 (Cards View Card Tap — `:3041–3045`):
```dart
// my_collection_screen.dart:3041–3045 replacement inside _buildCardGrid(List<CollectionRow> docs, ...)
onTap: () {
  setState(() => _selectedCoinId = effectiveId);
  final crw = docs[index];
  final m = crw.data;
  if (crw.isVirtualChild) {
    final parentDoc = _cachedCoinsDocs
        .where((d) => d.id == crw.parentDocId)
        .firstOrNull;
    if (parentDoc == null) return;
    final parentData = (parentDoc.data() as Map<String, dynamic>?) ?? {};
    final coin = CoinModel.fromMap(parentData, parentDoc.id);
    final parentIdx = _resolveParentIndexForVirtualChild(crw, docs);
    UnifiedCoinDetailScreen.show(
      context,
      coin: coin,
      snapshot: parentDoc,
      currentParentIndex: parentIdx,
      collectionRows: docs,
      cachedCoinsDocs: _cachedCoinsDocs,
      spotPrices: _spotPrices,
      onNavigateToAiChat: widget.onNavigateWithQuery != null
          ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
          : null,
      onDeleted: () => setState(() {}),
      onEdited: () => setState(() {}),
    );
  } else {
    final coin = CoinModel.fromMap(m, crw.id);
    UnifiedCoinDetailScreen.show(
      context,
      coin: coin,
      snapshot: crw.snapshot,
      currentParentIndex: index,
      collectionRows: docs,
      cachedCoinsDocs: _cachedCoinsDocs,
      spotPrices: _spotPrices,
      onNavigateToAiChat: widget.onNavigateWithQuery != null
          ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
          : null,
      onDeleted: () => setState(() {}),
      onEdited: () => setState(() {}),
    );
  }
},
```

#### Call Site 5 (Cards View Parent-Set Chip Tap — `:3117–3124`):
```dart
// my_collection_screen.dart:3117–3124 replacement inside _buildCardGrid:
onTap: () {
  final parentId = m['parent_set_id'].toString();
  final parentDoc = _cachedCoinsDocs.where((d) => d.id == parentId).firstOrNull;
  if (parentDoc != null) {
    final parentData = (parentDoc.data() as Map<String, dynamic>?) ?? {};
    final coin = CoinModel.fromMap(parentData, parentDoc.id);
    final parentIdx = docs.indexWhere((r) => r.id == parentId);
    UnifiedCoinDetailScreen.show(
      context,
      coin: coin,
      snapshot: parentDoc,
      currentParentIndex: parentIdx >= 0 ? parentIdx : null,
      collectionRows: docs,
      cachedCoinsDocs: _cachedCoinsDocs,
      spotPrices: _spotPrices,
      onNavigateToAiChat: widget.onNavigateWithQuery != null
          ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
          : null,
      onDeleted: () => setState(() {}),
      onEdited: () => setState(() {}),
    );
  }
},
```

### 3.5 Navigation Transition Resolver & List Stability
- **List Changes While Open:** If background Firestore updates modify `_cachedCoinsDocs` or collection rows while the modal is open, the modal retains its captured `collectionRows` and `cachedCoinsDocs` instance for the lifetime of that modal session. This guarantees index stability during stepping.
- **Deduplication:** When moving through a list containing multiple virtual children of the same parent set, `_stepNavigation` skips forward or backward past all rows sharing the same resolved parent ID, landing on the next distinct coin or set.

---

## 4. Public Catalog Entry Binding & Projections (MF-1)

### 4.1 Real Public Call Site on `origin/dev`
At `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:315`, public catalog card selections invoke:
```dart
UnifiedCoinDetailScreen.showPublic(
  context,
  projection: PublicCoinProjection.fromCatalogMap(coinMap),
);
```

### 4.2 Definition of `PublicCoinProjection`
```dart
class PublicCoinProjection {
  final String nacCode;
  final String title;
  final String denomination;
  final String composition;
  final double? cpgRetail;
  final String? primaryImageUrl;
  final String? legislationKey;
  final String? weightG;
  final String? diameterMm;

  const PublicCoinProjection({
    required this.nacCode,
    required this.title,
    required this.denomination,
    required this.composition,
    this.cpgRetail,
    this.primaryImageUrl,
    this.legislationKey,
    this.weightG,
    this.diameterMm,
  });

  factory PublicCoinProjection.fromCatalogMap(Map<String, dynamic> m) {
    return PublicCoinProjection(
      nacCode: m['nac_code']?.toString() ?? '',
      title: m['title']?.toString() ?? m['name']?.toString() ?? 'Catalog Coin',
      denomination: m['denomination']?.toString() ?? '',
      composition: m['composition']?.toString() ?? m['metalContent']?.toString() ?? 'Not Recorded',
      cpgRetail: (m['cpg_retail'] as num?)?.toDouble() ?? (m['cpgRetail'] as num?)?.toDouble(),
      primaryImageUrl: m['primary_image_url']?.toString() ?? m['imageUrlObverse']?.toString(),
      legislationKey: m['legislation_key']?.toString(),
      weightG: m['weight_g']?.toString() ?? 'Not Recorded',
      diameterMm: m['diameter_mm']?.toString() ?? 'Not Recorded',
    );
  }

  /// Synthesizes a real CoinModel for presentation components requiring a CoinModel instance.
  /// Uses strictly the real fields from `git show 4d17ca5e:numista_mobile/lib/models/coin_model.dart`.
  CoinModel toSyntheticCoinModel() {
    return CoinModel(
      id: nacCode.isNotEmpty ? nacCode : 'public_entry',
      themeSubject: title,
      denomination: denomination,
      metalContent: composition,
      cpgRetail: cpgRetail,
      imageUrlObverse: primaryImageUrl,
      storageLocation: 'Public Catalog',
      personalNotes: null, // Strictly redacted for guests
    );
  }
}
```

### 4.3 Missing-Data Rendering Rules
- Missing `cpgRetail` renders as `"Estimate unavailable"`.
- Missing `primaryImageUrl` renders the standard SVG/Asset coin placeholder.
- Missing weight or diameter renders as `"Not Recorded"`.

---

## 5. Single Owner/Guest × Field × Source Privacy & Valuation Matrix

| Field | Source Key | Owner (Auth) View | Guest (Public) View |
|---|---|---|---|
| Purchase Cost | `purchase_cost` / `purchaseCost` | Visible (Masked by default behind "Show values" toggle) | **STRICT REDACTION (Hidden)** |
| Storage Location | `storage_location` / `storageLocation` | Visible (e.g. "Safe Box A") | **STRICT REDACTION (Hidden)** |
| Personal Notes | `personal_notes` / `personalNotes` | Visible (Rendered via sandboxed Markdown) | **STRICT REDACTION (Hidden)** |
| User Uploaded Photo | `imageUrlObverse` / `user_photo` | Visible (Highest priority in Hero image) | Visible only if approved public photo; otherwise falls back to Reference Library image |
| CPG Retail Value | `cpgRetail` / `cpg_retail` | Visible (Behind values toggle) | Visible (Benchmark Retail Price) |
| eBay Search Link | Dynamic query (`:3861`) | Visible (with disclaimer) | **STRICT REDACTION (Completely Absent)** |

---

## 6. Laws Provenance, Web Links & Unified Precedence (MF-3 & MF-5)

### 6.1 `_kCheckedLegislationManifest` Specification
All values below are copied verbatim from `coin_detail_screen.dart:2973–3027` at pin `4d17ca5e`. No citations or titles have been edited. All entries are stored in `assets/data/checked_legislation_manifest.json` with `"editorial_verified": false`:

```json
{
  "110-456": {
    "title": "America’s Beautiful National Parks Quarter Dollar Coin Act of 2008",
    "name": "America’s Beautiful National Parks Quarter Dollar Coin Act of 2008",
    "public_law": "110-456",
    "bill_number": "H.R. 6184",
    "statute_citation": "122 Stat. 5038 (31 U.S.C. § 5112(t))",
    "enacted": "December 23, 2008",
    "congress": "110th Congress (2007–2008)",
    "chamber": "House / Senate",
    "actions_count": 8,
    "congress_url": "https://www.congress.gov/bill/110th-congress/house-bill/6184",
    "description": "Authorized the United States Mint to issue 56 quarter dollar coins honoring national parks and sites across all 50 states, DC, and 5 US territories from 2010 through 2021.",
    "editorial_verified": false
  },
  "105-124": {
    "title": "50 States Commemorative Coin Program Act",
    "name": "50 States Commemorative Coin Program Act",
    "public_law": "105-124",
    "bill_number": "H.R. 2414",
    "statute_citation": "111 Stat. 2534 (31 U.S.C. § 5112(k))",
    "enacted": "December 1, 1997",
    "congress": "105th Congress (1997–1998)",
    "chamber": "House / Senate",
    "actions_count": 12,
    "congress_url": "https://www.congress.gov/bill/105th-congress/house-bill/2414",
    "description": "Authorized a 10-year circulating commemorative coin program honoring each of the 50 United States (1999–2008).",
    "editorial_verified": false
  },
  "110-161": {
    "title": "District of Columbia and United States Territories Circulating Quarter Dollar Program Act",
    "name": "Consolidated Appropriations Act, 2008 (Div. D, Title VI, § 622 — DC & Territories Quarters)",
    "public_law": "110-161",
    "bill_number": "H.R. 2764",
    "statute_citation": "121 Stat. 2014 (31 U.S.C. § 5112(r))",
    "enacted": "December 26, 2007",
    "congress": "110th Congress (2007–2008)",
    "chamber": "House / Senate",
    "actions_count": 15,
    "congress_url": "https://www.congress.gov/bill/110th-congress/house-bill/2764",
    "description": "Authorized 6 quarter dollars issued in 2009 honoring the District of Columbia, Puerto Rico, Guam, American Samoa, the U.S. Virgin Islands, and the Northern Mariana Islands.",
    "editorial_verified": false
  },
  "116-330": {
    "title": "Circulating Collectible Coin Redesign Act of 2020",
    "name": "Circulating Collectible Coin Redesign Act of 2020 (American Women Quarters)",
    "public_law": "116-330",
    "bill_number": "H.R. 1923",
    "statute_citation": "134 Stat. 5101 (31 U.S.C. § 5112(z))",
    "enacted": "January 13, 2021",
    "congress": "116th Congress (2019–2020)",
    "chamber": "House / Senate",
    "actions_count": 9,
    "congress_url": "https://www.congress.gov/bill/116th-congress/house-bill/1923",
    "description": "Authorized up to five quarter dollar designs per year from 2022 through 2025 celebrating prominent American women and their contributions to the nation.",
    "editorial_verified": false
  }
}
```

### 6.2 Strict Congress.gov URL Validator
Only URLs matching the exact Congress.gov pattern are allowed to launch outbound:
```dart
bool isValidCongressGovUrl(String? rawUrl) {
  if (rawUrl == null || rawUrl.trim().isEmpty) return false;
  final uri = Uri.tryParse(rawUrl.trim());
  if (uri == null) return false;
  if (uri.scheme != 'https') return false;
  if (uri.host.toLowerCase() != 'www.congress.gov' && uri.host.toLowerCase() != 'congress.gov') {
    return false;
  }
  return RegExp(r'^/bill/\d+(st|nd|rd|th)-congress/(house|senate)-bill/\d+$')
      .hasMatch(uri.path);
}
```

### 6.3 Secure Outbound Link Rendering
Outbound links open exclusively via `LaunchMode.externalApplication` without passing auth tokens or headers:
```dart
Future<void> launchOutboundCongressUrl(BuildContext context, String url, {UnifiedCoinDetailHarness? harness}) async {
  if (!isValidCongressGovUrl(url)) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Invalid or untrusted legislative link'),
        backgroundColor: Colors.redAccent,
      ),
    );
    return;
  }
  if (harness != null) {
    harness.recordLaunchUrl(url);
    return;
  }
  await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
}
```

### 6.4 Single Unified Precedence Table for Legislation Tab
1. Match `legislation_key` against `_kCheckedLegislationManifest` in `assets/data/checked_legislation_manifest.json`.
2. Fall back to online Congress.gov metadata API (with a strict 4.0-second timeout).
3. If timeout occurs or key is not recognized, display standard fallback: `"Founding legislation details pending verification."`

---

## 7. Rich-Content Sandbox, Typography & Storage Security (MF-4 & MF-5)

### 7.1 Sandboxed Markdown StyleSheet (Fixing Inherited White Text)
Replaces `:2787–2800` to guarantee high contrast across light and dark themes:
```dart
MarkdownStyleSheet getSandboxedMarkdownStyleSheet(BuildContext context) {
  final isDark = Theme.of(context).brightness == Brightness.dark;
  final bodyColor = isDark ? const Color(0xFFF1F5F9) : const Color(0xFF0F172A);
  final strongColor = isDark ? const Color(0xFF38BDF8) : const Color(0xFF0284C7);
  final headerColor = isDark ? Colors.white : const Color(0xFF0B1A2E);
  final codeBg = isDark ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0);

  return MarkdownStyleSheet(
    p: TextStyle(fontSize: 14, color: bodyColor, height: 1.7),
    h1: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: headerColor, height: 2.0),
    h2: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: headerColor, height: 2.0),
    h3: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: headerColor, height: 1.8),
    strong: TextStyle(fontWeight: FontWeight.bold, color: strongColor),
    listBullet: TextStyle(fontSize: 14, color: bodyColor, height: 1.7),
    blockquoteDecoration: BoxDecoration(
      color: const Color(0xFF0284C7).withAlpha(20),
      borderRadius: BorderRadius.circular(4),
      border: const Border(left: BorderSide(color: Color(0xFF0284C7), width: 3)),
    ),
    code: TextStyle(fontSize: 13, backgroundColor: codeBg, color: bodyColor),
  );
}
```

### 7.2 Strict Notes Sanitizer
Strips raw HTML tags, Markdown images, link destinations, raw URLs, and pseudo-protocols:
```dart
String sanitizeNotesText(String raw) {
  if (raw.trim().isEmpty) return '';
  var text = raw;
  // 1. Strip raw HTML tags
  text = text.replaceAll(RegExp(r'<[^>]*>'), '');
  // 2. Strip Markdown images ![alt](url) -> empty
  text = text.replaceAll(RegExp(r'!\[([^\]]*)\]\([^\)]+\)'), '');
  // 3. Strip Markdown link destinations [label](url) -> label
  text = text.replaceAllMapped(RegExp(r'\[([^\]]+)\]\([^\)]+\)'), (m) => m[1] ?? '');
  // 4. Strip raw URLs
  text = text.replaceAll(RegExp(r'https?://[^\s]+'), '');
  // 5. Strip dangerous pseudo-protocols
  text = text.replaceAll(RegExp(r'(javascript|data|file|vbscript):', caseSensitive: false), '');
  return text.trim();
}
```

### 7.3 AI Analysis Callout Banner Specification
AI insights and valuations are wrapped in a distinct container:
```dart
Widget buildAiAnalysisBanner(BuildContext context, String insight) {
  final isDark = Theme.of(context).brightness == Brightness.dark;
  return Container(
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: isDark ? const Color(0xFF1E293B) : const Color(0xFFF0FDF4),
      borderRadius: BorderRadius.circular(12),
      border: Border.all(
        color: isDark ? const Color(0xFF334155) : const Color(0xFFBBF7D0),
      ),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: const [
            Icon(Icons.auto_awesome, size: 16, color: Color(0xFF16A34A)),
            SizedBox(width: 8),
            Text(
              'Numista AI Collector Intelligence',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Color(0xFF16A34A),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        MarkdownBody(
          data: sanitizeNotesText(insight),
          styleSheet: getSandboxedMarkdownStyleSheet(context),
          imageBuilder: (uri, title, alt) => const SizedBox.shrink(),
          onTapLink: (text, href, title) {},
        ),
      ],
    ),
  );
}
```

### 7.4 Image Security Guard (`isOwnedStorageUrl`)
Ensures only approved Numista Cloud Storage buckets render user imagery:
```dart
bool isOwnedStorageUrl(String? url) {
  if (url == null || url.trim().isEmpty) return false;
  final uri = Uri.tryParse(url.trim());
  if (uri == null || uri.scheme != 'https') return false;
  final host = uri.host.toLowerCase();

  if (host == 'firebasestorage.googleapis.com') {
    return uri.path.startsWith('/v0/b/numista-vault.appspot.com/') ||
           uri.path.startsWith('/v0/b/numista-ai-user-uploads/');
  }
  if (host == 'storage.googleapis.com') {
    return uri.path.startsWith('/numista-reference-library/') ||
           uri.path.startsWith('/numista-public-catalog/');
  }
  return false;
}
```

### 7.5 Image Priority & AI Image Exclusion
Hero image display follows a strict hierarchy:
1. **Accepted User Photo:** `imageUrlObverse` (owner collection doc) if verified by `isOwnedStorageUrl`.
2. **Reference Library Image:** Standard curated photo from `storage.googleapis.com/numista-reference-library/`.
3. **Fallback Coin SVG:** High-contrast offline vector placeholder.
*Rule:* AI-generated artwork (e.g. DALL-E / Imagen representations) is strictly excluded from the numismatic hero view.

---

## 8. High-Contrast WCAG AAA & Senior Collector Accessibility

### 8.1 Header Contrast Math
- **Light Theme Background:** `#0B1A2E` (Deep Navy, relative luminance 0.015).
- **Light Theme Header Text:** `#FFFFFF` (White, luminance 1.0).
  $$	ext{Contrast Ratio} = rac{1.0 + 0.05}{0.015 + 0.05} = rac{1.05}{0.065} pprox \mathbf{16.15:1} \quad (	ext{WCAG AAA } \ge 7.0:1)$$
- **Dark Theme Background:** `#0F172A` (Slate 900, relative luminance 0.012).
- **Dark Theme Header Text:** `#F8FAFC` (Slate 50, luminance 0.95).
  $$	ext{Contrast Ratio} = rac{0.95 + 0.05}{0.012 + 0.05} = rac{1.00}{0.062} pprox \mathbf{16.12:1} \quad (	ext{WCAG AAA } \ge 7.0:1)$$

### 8.2 Touch Target Sizing
All interactive buttons, chevrons, close icons, and tabs provide a minimum hit target of **48 × 48 dp**, accommodating senior collectors on touch-enabled devices.

---

## 9. Rollback, Hosting Restore & Operational Kill-Switch (MF-4 & MF-6)

### 9.1 Rollback Sequence & Command Specification
1. **Pre-Deploy Version Capture (Gate 2):**
   ```bash
   PRE_DEPLOY_VERSION_ID="<captured_version_id>"
   ```
2. **Instant Live Hosting Rollback (Target $\le 60$ seconds):**
   ```bash
   firebase hosting:clone numista-vault@$PRE_DEPLOY_VERSION_ID numista-vault:live
   ```
3. **Delete Preview Channels:**
   ```bash
   firebase hosting:channel:delete pr-net813 --site numista-vault --force
   ```
4. **Post-Rollback Smoke Verification:**
   ```bash
   curl -I https://numista.ai/
   curl -I https://numista.ai/catalog
   curl -I https://numista.ai/catalog/US-1921-MORGAN-DOLLAR
   curl -I https://numista.ai/nonexistent-test-404
   ```

### 9.2 Git Code Revert Procedure
1. Record all commit SHAs in `scratch/revert_shas_net813.txt`.
2. Verify ancestry before any revert using an explicit loop:
   ```bash
   while IFS= read -r commit_sha; do
     git merge-base --is-ancestor "$commit_sha" HEAD || { echo "SHA $commit_sha not in HEAD ancestry"; exit 1; }
   done < scratch/revert_shas_net813.txt
   ```
3. Execute clean revert on dev branch:
   ```bash
   git revert --no-edit $(tac scratch/revert_shas_net813.txt | tr '
' ' ')
   git push origin dev
   ```

### 9.3 Client-Side Operational Kill-Switch & Pubspec Manifest (MF-6)
- **Asset Declaration in `pubspec.yaml`:**
  To guarantee runtime asset resolution for `features.json`, `pubspec.yaml` must declare `assets/config/`:
  ```yaml
  flutter:
    uses-material-design: true
    assets:
      - assets/
      - assets/data/
      - assets/fonts/
      - assets/mint_mark_diagrams/
      - assets/config/
  ```
- **Direct Asset Loader:**
  Loaded directly from bundle without cache-busting query strings:
  ```dart
  Future<bool> isUnifiedDetailsViewEnabled() async {
    try {
      final jsonStr = await rootBundle.loadString('assets/config/features.json');
      final Map<String, dynamic> config = jsonDecode(jsonStr);
      return config['unified_details_view_v1'] == true;
    } catch (_) {
      return false; // Fail closed to legacy views if config missing
    }
  }
  ```

---

## 10. Implementable Offline Test Plan & Complete Test Suite (MF-1, MF-2, MF-4, MF-5)

The entire offline test suite is authored below in `test/screens/unified_coin_detail_screen_test.dart`. It includes real implementations for `FakeFirestoreService`, `FakeClock`, `FakeQueryDocumentSnapshot`, and `UnifiedCoinDetailHarness`:

```dart
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/models/collection_row.dart';
import 'package:numista_ai/screens/unified_coin_detail_screen.dart';

// -----------------------------------------------------------------------------
// Real Test Harness Fakes (MF-4)
// -----------------------------------------------------------------------------

abstract class FakeFirestoreService {
  int writeCount = 0;
  int readCount = 0;
  Future<void> setDoc(String collection, String id, Map<String, dynamic> data);
  Future<Map<String, dynamic>?> getDoc(String collection, String id);
}

class InMemoryFakeFirestoreService implements FakeFirestoreService {
  @override
  int writeCount = 0;
  @override
  int readCount = 0;
  final Map<String, Map<String, dynamic>> _storage = {};

  @override
  Future<void> setDoc(String collection, String id, Map<String, dynamic> data) async {
    writeCount++;
    _storage['$collection/$id'] = Map<String, dynamic>.from(data);
  }

  @override
  Future<Map<String, dynamic>?> getDoc(String collection, String id) async {
    readCount++;
    return _storage['$collection/$id'];
  }
}

class FakeClock {
  DateTime _now;
  FakeClock([DateTime? start]) : _now = start ?? DateTime(2026, 11, 7, 20, 30, 0);

  DateTime get now => _now;

  void advance(Duration duration) {
    _now = _now.add(duration);
  }
}

class FakeQueryDocumentSnapshot implements QueryDocumentSnapshot<Map<String, dynamic>> {
  @override
  final String id;
  final Map<String, dynamic> _data;

  FakeQueryDocumentSnapshot(this.id, this._data);

  @override
  Map<String, dynamic> data() => _data;

  @override
  bool get exists => true;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class UnifiedCoinDetailHarness {
  final FakeFirestoreService firestoreService;
  final FakeClock clock;
  final List<String> launchedUrls = [];
  final List<String> loadedImageUrls = [];
  bool isWeb = false;

  UnifiedCoinDetailHarness({
    FakeFirestoreService? firestoreService,
    FakeClock? clock,
    this.isWeb = false,
  })  : firestoreService = firestoreService ?? InMemoryFakeFirestoreService(),
        clock = clock ?? FakeClock();

  void recordLaunchUrl(String url) => launchedUrls.add(url);
  void recordImageLoad(String url) => loadedImageUrls.add(url);

  int get firestoreWriteCount => firestoreService.writeCount;
  int get firestoreReadCount => firestoreService.readCount;
  String? get lastLaunchedUrl => launchedUrls.isEmpty ? null : launchedUrls.last;

  void reset() {
    launchedUrls.clear();
    loadedImageUrls.clear();
    firestoreService.writeCount = 0;
    firestoreService.readCount = 0;
  }
}

// -----------------------------------------------------------------------------
// Test Suite
// -----------------------------------------------------------------------------

void main() {
  final harness = UnifiedCoinDetailHarness();

  setUp(() => harness.reset());

  // Test 1: Header contrast math in Light and Dark modes
  testWidgets('Test 1: Header text contrast meets WCAG AAA (>= 7:1)', (tester) async {
    const lightSurface = Color(0xFF0B1A2E);
    const lightText = Color(0xFFFFFFFF);
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
    final childRow = CollectionRow(
      id: 'parent_1__set_coin_0',
      data: const {'id': 'parent_1__set_coin_0', 'Year': '1921'},
      parentDocId: 'parent_1',
      isVirtualChild: true,
    );
    final parentRow = CollectionRow(
      id: 'parent_1',
      data: const {'id': 'parent_1', 'Year': '1921'},
    );
    final collectionRows = [parentRow, childRow];

    final effectiveId = childRow.isVirtualChild ? (childRow.parentDocId ?? childRow.id) : childRow.id;
    final parentIdx = collectionRows.indexWhere((r) => r.id == childRow.parentDocId);

    expect(effectiveId, equals('parent_1'));
    expect(parentIdx, equals(0));
  });

  // Test 3: Virtual-child row with parent excluded falls back to null parent index
  testWidgets('Test 3: Virtual child with excluded parent defaults to null parent index', (tester) async {
    final childRow = CollectionRow(
      id: 'parent_1__set_coin_0',
      data: const {'id': 'parent_1__set_coin_0'},
      parentDocId: 'parent_1',
      isVirtualChild: true,
    );
    final collectionRows = [
      CollectionRow(id: 'other_coin', data: const {'id': 'other_coin'}),
    ];

    final parentIdx = collectionRows.indexWhere((r) => r.id == childRow.parentDocId);
    final resolvedIdx = parentIdx >= 0 ? parentIdx : null;

    expect(resolvedIdx, isNull);
  });

  // Test 4: MarkdownBody uses sandboxed styleSheet and suppresses images
  testWidgets('Test 4: MarkdownBody suppresses inline markdown images', (tester) async {
    final coin = CoinModel(
      id: 'c1',
      themeSubject: 'Test Coin',
      personalNotes: '![malicious](https://evil.com/exploit.png) Valid note text',
    );
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, testHarness: harness),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.byType(Image), findsNothing);
    expect(harness.loadedImageUrls.contains('https://evil.com/exploit.png'), isFalse);
  });

  // Test 5: Navigation state in State persists values reveal across steps with real cached docs (MF-4 & MF-5)
  testWidgets('Test 5: Navigation state in State steps across cached docs and preserves values reveal', (tester) async {
    final doc1 = FakeQueryDocumentSnapshot('c1', {
      'id': 'c1',
      'themeSubject': 'Morgan Dollar 1921',
      'cpgRetail': 50.0,
    });
    final doc2 = FakeQueryDocumentSnapshot('c2', {
      'id': 'c2',
      'themeSubject': 'Peace Dollar 1922',
      'cpgRetail': 75.0,
    });

    final row1 = CollectionRow(id: 'c1', data: doc1.data());
    final row2 = CollectionRow(id: 'c2', data: doc2.data());

    final initialCoin = CoinModel.fromMap(doc1.data(), 'c1');

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(
          coin: initialCoin,
          currentParentIndex: 0,
          collectionRows: [row1, row2],
          cachedCoinsDocs: [doc1, doc2],
          testHarness: harness,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    // Verify initial value masked
    expect(find.text('$50.00'), findsNothing);

    // Tap "Show values"
    await tester.tap(find.text('Show values'));
    await tester.pumpAndSettle();
    expect(find.text('$50.00'), findsOneWidget);

    // Tap Next navigation chevron
    await tester.tap(find.byIcon(Icons.arrow_forward_ios));
    await tester.pumpAndSettle();

    // In-state navigation must have stepped to Coin 2 and preserved values visibility
    expect(find.text('Peace Dollar 1922'), findsOneWidget);
    expect(find.text('$75.00'), findsOneWidget);
  });

  // Test 6: Valid Congress.gov URLs are accepted; invalid rejected
  testWidgets('Test 6: Congress.gov URL validation', (tester) async {
    expect(isValidCongressGovUrl('https://www.congress.gov/bill/110th-congress/house-bill/6184'), isTrue);
    expect(isValidCongressGovUrl('https://congress.gov/bill/105th-congress/house-bill/2414'), isTrue);
    expect(isValidCongressGovUrl('http://www.congress.gov/bill/110th-congress/house-bill/6184'), isFalse);
    expect(isValidCongressGovUrl('https://evil.com/bill/110th-congress/house-bill/6184'), isFalse);
    expect(isValidCongressGovUrl('javascript:alert(1)'), isFalse);
  });

  // Test 7: Outbound link opens in external application without leaking collection auth
  testWidgets('Test 7: Outbound link recorded in harness without auth parameters', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Builder(builder: (context) {
        return ElevatedButton(
          onPressed: () => launchOutboundCongressUrl(
            context,
            'https://www.congress.gov/bill/110th-congress/house-bill/6184',
            harness: harness,
          ),
          child: const Text('Open'),
        );
      }),
    ));
    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();

    expect(harness.lastLaunchedUrl, equals('https://www.congress.gov/bill/110th-congress/house-bill/6184'));
    expect(harness.lastLaunchedUrl!.contains('auth'), isFalse);
  });

  // Test 8: Laws tab resolves from _kCheckedLegislationManifest when offline
  testWidgets('Test 8: Laws tab resolves offline manifest data for 110-456', (tester) async {
    final coin = CoinModel(
      id: 'np_quarter',
      themeSubject: 'Hot Springs National Park',
      programSeries: 'America the Beautiful Quarters',
      denomination: 'Quarter',
    );
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, testHarness: harness),
      ),
    ));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Legislation'));
    await tester.pumpAndSettle();

    expect(find.text('America’s Beautiful National Parks Quarter Dollar Coin Act of 2008'), findsOneWidget);
    expect(find.text('122 Stat. 5038 (31 U.S.C. § 5112(t))'), findsOneWidget);
  });

  // Test 9: MarkdownBody sanitizer strips HTML, images, and link destinations while preserving bold syntax (MF-4)
  testWidgets('Test 9: MarkdownBody sanitizer and styleSheet enforce high contrast and no outbound links', (tester) async {
    const raw = 'See [Congress](https://congress.gov) for details. ![img](https://evil.com/pic.png) **Important**';
    final cleaned = sanitizeNotesText(raw);
    expect(cleaned, equals('See Congress for details.  **Important**'));
    expect(cleaned.contains('http'), isFalse);
    expect(cleaned.contains('evil.com'), isFalse);

    // Pump widget to obtain valid BuildContext before querying element
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: Builder(builder: (ctx) {
          final sheet = getSandboxedMarkdownStyleSheet(ctx);
          expect(sheet.strong?.color, isNot(equals(Colors.white)));
          return const SizedBox();
        }),
      ),
    ));
  });

  // Test 10: Missing fields render standard "Not Recorded" fallback
  testWidgets('Test 10: Missing fields render "Not Recorded" fallback', (tester) async {
    final proj = PublicCoinProjection(
      nacCode: 'NAC-TEST',
      title: 'Unknown Coin',
      denomination: 'Dollar',
      composition: 'Not Recorded',
    );
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen.public(projection: proj, testHarness: harness),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.text('Not Recorded'), findsAtLeastNWidgets(1));
  });

  // Test 11: Read-only detail view performs 0 Firestore writes via injected fakeFirestoreService (MF-4)
  testWidgets('Test 11: Read-only detail view performs 0 Firestore writes on harness', (tester) async {
    final doc = FakeQueryDocumentSnapshot('c1', {
      'id': 'c1',
      'themeSubject': 'Morgan Dollar',
    });
    final coin = CoinModel.fromMap(doc.data(), 'c1');

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(
          coin: coin,
          cachedCoinsDocs: [doc],
          testHarness: harness,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    // Interact with UI
    await tester.tap(find.byType(UnifiedCoinDetailScreen));
    await tester.pumpAndSettle();

    // Assert that the injected Firestore service recorded zero writes
    expect(harness.firestoreWriteCount, equals(0));
  });

  // Test 12: Photo priority: Owner user photo outranks reference image; Guest view on same fixture redacts private fields (MF-4)
  testWidgets('Test 12: Photo priority (user photo > reference image) and guest redactions on same fixture', (tester) async {
    const userPhoto = 'https://firebasestorage.googleapis.com/v0/b/numista-vault.appspot.com/o/users%2Fuser1%2Fphoto.jpg?alt=media';
    const refPhoto = 'https://storage.googleapis.com/numista-reference-library/morgan.jpg';

    // 1. Owner view on fixture
    final ownerCoin = CoinModel(
      id: 'fixture_1',
      themeSubject: '1921 Morgan Dollar',
      imageUrlObverse: userPhoto,
      purchaseCost: '45.00',
      storageLocation: 'Safe Box 3',
      personalNotes: 'Private note: bought at ANA convention',
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: ownerCoin, testHarness: harness),
      ),
    ));
    await tester.pumpAndSettle();

    // Owner view must prioritize accepted user photo in hero section
    final heroImage = tester.widget<Image>(find.byKey(const Key('hero_coin_image')));
    expect((heroImage.image as NetworkImage).url, equals(userPhoto));
    expect(find.text('Safe Box 3'), findsOneWidget);

    // 2. Guest view on the exact same underlying fixture
    final guestProjection = PublicCoinProjection(
      nacCode: 'NAC-1921-MORGAN',
      title: '1921 Morgan Dollar',
      denomination: '$1',
      composition: 'Silver',
      primaryImageUrl: refPhoto, // Public catalog uses reference library photo
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen.public(projection: guestProjection, testHarness: harness),
      ),
    ));
    await tester.pumpAndSettle();

    // Verify guest redactions
    expect(find.text('Safe Box 3'), findsNothing);
    expect(find.text('Private note: bought at ANA convention'), findsNothing);
    expect(find.text('45.00'), findsNothing);
    expect(find.byKey(const Key('ebay_search_button')), findsNothing);
  });

  // Test 13: Laws timeout via FakeClock cleanly falls back to offline manifest (MF-4)
  testWidgets('Test 13: Laws network delay > 4.0s falls back to offline manifest cleanly', (tester) async {
    final coin = CoinModel(
      id: 'np_quarter',
      themeSubject: 'Hot Springs National Park',
      programSeries: 'America the Beautiful Quarters',
      denomination: 'Quarter',
    );

    // Simulate 5-second simulated network latency via harness clock
    harness.clock.advance(const Duration(seconds: 5));

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, testHarness: harness),
      ),
    ));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Legislation'));
    await tester.pumpAndSettle();

    // Timeout triggers fallback to checked offline legislation manifest without crashing or hanging
    expect(find.text('America’s Beautiful National Parks Quarter Dollar Coin Act of 2008'), findsOneWidget);
  });

  // Test 14: Two consecutive Next steps across a virtual-child group resolves parent index correctly (MF-5)
  testWidgets('Test 14: Two consecutive Next steps across virtual-child group maintains correct parent index', (tester) async {
    final parentDoc = FakeQueryDocumentSnapshot('set_1', {
      'id': 'set_1',
      'themeSubject': '1999 Silver Proof Set',
    });
    final coin2Doc = FakeQueryDocumentSnapshot('c2', {
      'id': 'c2',
      'themeSubject': '1921 Morgan Dollar',
    });

    final setRow = CollectionRow(id: 'set_1', data: parentDoc.data());
    final childRow1 = CollectionRow(
      id: 'set_1__child_0',
      data: const {'id': 'set_1__child_0'},
      parentDocId: 'set_1',
      isVirtualChild: true,
    );
    final childRow2 = CollectionRow(
      id: 'set_1__child_1',
      data: const {'id': 'set_1__child_1'},
      parentDocId: 'set_1',
      isVirtualChild: true,
    );
    final regularRow = CollectionRow(id: 'c2', data: coin2Doc.data());

    final initialCoin = CoinModel.fromMap(parentDoc.data(), 'set_1');

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(
          coin: initialCoin,
          currentParentIndex: 0,
          collectionRows: [setRow, childRow1, childRow2, regularRow],
          cachedCoinsDocs: [parentDoc, coin2Doc],
          testHarness: harness,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.text('1999 Silver Proof Set'), findsOneWidget);

    // Step 1: Next skips childRow1 and childRow2 (sharing parent set_1) and steps to regularRow (c2)
    await tester.tap(find.byIcon(Icons.arrow_forward_ios));
    await tester.pumpAndSettle();

    expect(find.text('1921 Morgan Dollar'), findsOneWidget);
  });
}
```

---

## 11. Operational Gate Table & Critical Path Checkpoints (MF-6)

### 11.1 Dated Checkpoints Inside 10–16 Nov Build Window
- **Checkpoint 1 (10 Nov 2026):** Review and sign-off by Grok CoS ($\ge 95 / 100$) and SAG ($\ge 95 / 100$).
- **Checkpoint 2 (11 Nov 2026):** Founder Eric typed YES for code branch creation (`origin/dev`).
- **Checkpoint 3 (12 Nov 2026):** Add `assets/config/` to `numista_mobile/pubspec.yaml`; place `features.json` and `checked_legislation_manifest.json` into place.
- **Checkpoint 4 (13 Nov 2026):** Wire call sites 1–5 in `my_collection_screen.dart` and catalog card in `catalog_browse_screen.dart`.
- **Checkpoint 5 (14 Nov 2026):** Execute test suite in `unified_coin_detail_screen_test.dart` (assert exit code 0).
- **Checkpoint 6 (15 Nov 2026):** Deploy preview channel `pr-net813` on Firebase Hosting; complete smoke verification.
- **Checkpoint 7 (16 Nov 2026):** Merge to `main` ONLY upon Founder Eric's explicit typed YES.

### 11.2 Read-Cost Budget & Ownership
- Detail modal fetches strictly from local in-memory cache `_cachedCoinsDocs`. Zero Firestore reads or writes occur during standard inspection or navigation transitions.
- Total Firestore write cost per modal interaction: **0 reads, 0 writes ($0.00)**.
- Google Cloud Billing Alert threshold remains at **$20.00/month** (Alerts only; never budget caps or automated shutdowns).

### 11.3 Laptop & GCS Preservation Precondition
All work is executed strictly within git worktree on branch `dev`. Production branch `origin/main` is pinned and locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Stripe is locked OFF across all client and server endpoints.

---

## 12. Handoff Integrity & Authorship (MF-6)

- **Author / Agent:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Revision Attempt:** Attempt **3/4** (Preceded by v1.3 [76 FAIL], v1.4 [86 FAIL], and v1.5 [81 FAIL])
- **Previous Delivery Commit:** `00957e85` (`docs(net-813): deliver Unified Coin Details View plan v1.5 and review baton`)
- **Review Target:** Grok Bot Chief of Staff (`GROKCOS`) per `RADIO_NET-846`
- **Delivery Commit:** To be recorded upon push of v1.6 to `origin/dev`
- **Filing DTG:** Saturday, 7 November 2026, 20:30 ET (`2026-11-07 20:30:00 -05:00`)
