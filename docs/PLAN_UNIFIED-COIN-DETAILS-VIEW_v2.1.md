# PLAN: Unified Coin Details View v2.1 (NET-813 / BATON_NET-813)

- **Track ID:** NET-813 (Architecture Plan / Feature Specification / Thanksgiving Critical Path)
- **Author (v2.1):** AG CoS (closing SAG 54 FAIL verified fix list from 8 Nov ~11:52 ET). Prior: v1.8–v2.0 by GB CoS fresh writer; v1.2–v1.7 by AG CoS v5.
- **Pins (full SHAs):** code pin `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235`; catalog source `b0b05808` (identical to `origin/dev` `cc815522` for `assets/catalog/catalog_public_v1.json` and `catalog_browse_screen.dart`; absent at pin `4d17ca5e`); main LOCKED `9f04550a45fa4da082ba8948c2d89a521a90fa45`.
- **Review Target:** Grok Bot Chief of Staff (`GROKCOS`) (Score target $\ge 95 / 100$)
- **Date / DTG:** Thursday, 12 November 2026 (`2026-11-12 -05:00`)
- **Mode:** **STRICT PLAN ONLY — PREVIEW GATE ONLY** (Zero code modifications, zero builds, zero test execution, zero Firestore writes/seeding, zero live deploys without Founder Eric's explicit typed YES)
- **Branch Context:** Code pinned against `origin/p7-v8.9` @ `4d17ca5e`; public catalog entry bound against `b0b05808` (= `origin/dev` `cc815522` for catalog JSON/screens)

---

## v2.1 Close-Out of SAG-54 Must-Fixes (MF-1..MF-7b)

| # | SAG-54 must-fix | v2.1 change | Evidence |
|---|---|---|---|
| **MF-1** | Harness API undeclared (`loadedImageUrls`, `lastLaunchedUrl`, `recordLaunchUrl`) | Added `UrlLauncherHook? onLaunchUrl` and `ImageLoadRecorder? onImageLoad` to `UnifiedCoinDetailDeps` (no-op in production; wired to `t.lastLaunchedUrl` and `t.loadedImageUrls` in `TestDeps`). | §9.4 (`unified_coin_detail_deps.dart`), §10 (Tests 4 & 7). |
| **MF-2** | Call-site snippets omitted `legacyOpen`, called deleted `_resolveParentIndexForVirtualChild` / `docs.indexWhere` | Deleted `_resolveParentIndexForVirtualChild`; all 5 snippets in §3.4 now use top-level `resolveParentIndex(...)` and pass `legacyOpen: () => <pin call>` verbatim. | §3.3, §3.4. |
| **MF-3** | Legislation path omitted `_matchLawKey()` and invented `_congressGovFetch` | Ported `_matchLawKey()` verbatim from `4d17ca5e:coin_detail_screen.dart:3030–3068`; dropped `_congressGovFetch`, reading `_kDefaultLaws`/manifest + `deps.lawsFetcher` (Firestore `metadata/coin_legislation` or test stub). Added `uri.userInfo.isNotEmpty` check to `isValidCongressGovUrl`. | §6.1–6.5. |
| **MF-4a/4c** | Stale `6af2afb1`/`bde8b402` SHAs; `assets/catalog/` missing in pin `pubspec.yaml` | Bound catalog evidence to `b0b05808` (= `origin/dev` `cc815522` for catalog paths); removed `6af2afb1`/`bde8b402`. Added `- assets/catalog/` to §9.3 `pubspec.yaml` (already at `b0b05808:pubspec.yaml:97`, absent at `4d17ca5e:92-96`). | Header, §9.3. |
| **MF-4d / 4b** | `isOwnedStorageUrl` vs Met catalog URLs; FALSE MF-4b/row claims | Added explicit catalog-image host allowlist (`images.metmuseum.org`, `numismatics.org`, `thumb.wikimedia.org`, `upload.wikimedia.org` verified on `b0b05808`) + `https` + non-empty `license` & `source_url` (`primary_image` has no `source` key). Owner photos keep `isOwnedStorageUrl`. Dropped unverified 248-row Met count; cited `LIBAM 1782` & `1921-P Morgan` on `b0b05808`. | §4.2, G1. |
| **MF-5** | Missing `build` widget contract & inconsistent currency format (`$50.00` vs `45.00`) | Added `build(BuildContext)` spec in §3.2 with `udv_header_surface`, `udv_header_title`, `hero_coin_image`, `'Show values'`, `Icons.arrow_forward_ios`, `'Legislation'` tab, and `Key('ebay_search_button')` (owner-only). Standardized currency format to `$XX.XX` across Tests 5 & 12 (`$45.00`). | §3.2, §10 (Tests 5 & 12). |
| **MF-6** | §9.1 `firebase hosting:clone ... :live` is a live deploy; §9.2 used `tac` | Replaced live clone with deleting preview channel `pr-net813` only; §9.2 uses portable `awk` + local `git revert` only (push behind separate Founder YES). | §9.1, §9.2. |
| **MF-7a/7b** | `fromCoinModel` set `cpgRetail: null` instead of mapping `CoinModel.cpgRetail`; kill-switch `features.json` state unstated | Mapped `cpgRetail: coin.cpgRetail > 0 ? coin.cpgRetail : null` (`4d17ca5e:coin_model.dart:54` defaults to `0.0`). Specified shipping `assets/config/features.json` = `{"unified_details_view_v1": false}` (flipping requires restart). | §4.2, §9.3. |

---

## v2.0 Close-Out of CoS-90 Must-Fixes (round 3, 08:12 ET; ONLY these items changed)

| # | CoS-90 must-fix | v2.0 change | Evidence |
|---|---|---|---|
| **H1** | `UnifiedCoinDetailDeps get harness => t.deps;` declared inside `void main()` (Dart has no local getters) | `final t = TestDeps();` and `UnifiedCoinDetailDeps get harness => t.deps;` moved to **library top level** above `main()`. A top-level getter is legal Dart and re-evaluates `t.deps` on every use, so a per-test `t.lawsFetcher` assignment is still picked up (not frozen). Test bodies unchanged. | Dart language: getters are allowed as top-level/class members, not as local declarations. Not analyzed (PLAN ONLY). |
| **H2** | Test 15 calls `jsonDecode` but the test file had no `dart:convert` import | Added `import 'dart:convert';` to the test file import block. | §10 import block. |
| **H3** | Test 16 "missing" case passed `raw: null`, which the constructor turned into ENABLED JSON | `_GateBundle` rewritten with three explicit named constructors: `.enabled()`, `.raw(String)` (disabled JSON) and `.missing()` (throws `FlutterError` for `assets/config/features.json`, never returns config). Test 16 iterates `[_GateBundle.raw(disabled), _GateBundle.missing()]`; setUp uses `_GateBundle.enabled()`. No null-coalescing default remains. | §10 Test 16 + `_GateBundle`. |

## v1.9 Close-Out of CoS-86 Must-Fixes (fresh writer round 2; ONLY these six items changed)

| # | CoS-86 must-fix | v1.9 change | Evidence |
|---|---|---|---|
| **G1 (MF-1)** | `fromCatalogMap` read nonexistent `primary_image_url` | Reads `m['primary_image']` as a Map and takes `['url']` only if it is a non-empty https URL from the verified catalog host allowlist **and** the object carries non-empty `license` and `source_url` (provenance). `type_image` is not used as a hero fallback (policy unchanged: placeholder when primary is null). Asset-backed Test 15 uses the real row `NAC1.MD.US.PRV.LIBAM.1782.XX.BASE.S` (non-null `primary_image.url`) and the null-image `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` as the negative. | `git show b0b05808:numista_mobile/assets/catalog/catalog_public_v1.json` (= `cc815522`): `NAC1.MD.US.PRV.LIBAM.1782.XX.BASE.S` has `primary_image` = `{url, full_url, side, unique_side, license, credit, source_url, resolution}`, `url` = `https://images.metmuseum.org/CRDImages/es/web-large/DP-43714-001.jpg`, `license` = `CC0 (Met Open Access)`. `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3`: all image fields null. |
| **G2 (MF-2)** | Harness types lived only in the test file but production referenced them | New **production** contract library `numista_mobile/lib/screens/unified_coin_detail_deps.dart` (New) defines `CoinDocStore`, `DetailClock`, `LawsFetcher`, and `UnifiedCoinDetailDeps` (+ production impls `CachedCoinDocStore`, `SystemDetailClock`). Production code imports it. The test file imports it and declares only fakes with **distinct names** (`CountingCoinDocStore`, `ManualClock`) that `implements` the contracts — no redeclared production names. Constructor param renamed `deps` → `deps`; class `UnifiedCoinDetailDeps` → `UnifiedCoinDetailDeps` throughout. Added to manifest. | Plan-internal; no analyzer run (PLAN ONLY). |
| **G3 (MF-3)** | `_loadCurrentDoc` read only in a test-only branch | No test-only branch: the widget **always** uses `deps ?? UnifiedCoinDetailDeps.production(cachedCoinsDocs)`. Production `CachedCoinDocStore.getDoc` reads from `cachedCoinsDocs` in memory (**0 Firestore reads, 0 writes**, matching A11.2); its `setDoc` throws `UnsupportedError` (view is read-only). Tests instrument the **same** `CoinDocStore` boundary. Deliberate regression the test rejects: adding any `deps.store.setDoc(...)` to the widget makes `writeCount > 0` → Test 11 fails; adding a direct `FirebaseFirestore.instance` call throws `[core/no-app]` (no Firebase init in the test file) → Test 11 fails. No production Firestore read is added to satisfy `readCount`. | Plan-internal. |
| **G4 (MF-4)** | Tests 1/2/3 didn't exercise real UI/resolver; Test 12 contradicted values masking | Test 1 mounts the screen and reads the rendered header `Text` style color and its `Container` `BoxDecoration.color` by key (`udv_header_title`, `udv_header_surface`). Tests 2/3 call the shipped top-level resolver `resolveParentIndex(rows, tappedRow)` that **all five** A3.4 call sites now use (§3.3). Test 12 taps **Show values** before asserting `45.00`, then asserts guest redaction on the same fixture. | A5 matrix row: Purchase Cost "Masked by default behind 'Show values' toggle". |
| **G5 (MF-5)** | Kill-switch defined but not wired | Single gate `UnifiedDetailsGate.isEnabled()` (memoized Future over `assets/config/features.json`, fail-closed false) is consulted inside `show()` and `showPublic()` — the only two entry points used by all six paths (five collection call sites + catalog `_showItemDetailModal`). Each caller passes `legacyOpen:` (its existing pre-NET-813 invocation, unchanged). Disabled/missing config → `legacyOpen()` and the unified screen is never built. Test 16 covers disabled and missing config. | Plan-internal; `assets/config/` registration already in Checkpoint 3. |
| **G6 (MF-6)** | Checkpoint 7 proposed a merge to main | Removed. Checkpoint 7 is now "Preview sign-off; **no main merge** — main stays locked at `9f04550a`; any change to that lock is a separate explicit Eric decision, not implied by this plan's YES." Deploys and Firestore writes keep separate YES gates. | Standing rule. |

## v1.8 Close-Out of CoS-92 Remaining Defects (fresh writer; ONLY these five items changed)

| # | CoS-92 defect | v1.8 change | Verified evidence |
|---|---|---|---|
| **D1** | §4.1 quote labels off by two | Card block relabeled **464–467**; initial-NAC block relabeled **77–82**; `:810` unchanged. Prose cites `onTap` `:466` and call `:80` as exact. | `git show b0b05808:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` (= `cc815522`): `:464 return _CatalogCard(`, `:465 item: item,`, `:466 onTap: () => _showItemDetailModal(item),`, `:467 );`; `:77 if (match.isNotEmpty) {`, `:78 WidgetsBinding.instance.addPostFrameCallback((_) {`, `:79 if (mounted) {`, `:80 _showItemDetailModal(match);`, `:81 }`, `:82 });`; `:810 void _showItemDetailModal(Map<String, dynamic> item) {`. |
| **D2** | Test 11 used nonexistent `seedDocument`/`getDocument`; test body (not widget) did the read | Test seeds with harness `setDoc`, calls `harness.reset()` to zero counters, mounts the widget, then asserts `firestoreReadCount >= 1` (proves the **widget** read through `harness.firestoreService`) and `firestoreWriteCount == 0`. Widget spec in §3.2 now shows `_loadCurrentDoc()` reading via `getDoc` when `deps` is set. No test-body read. | Harness interface in §10 declares only `setDoc(String collection, String id, Map)` and `getDoc(String collection, String id)` (plus `writeCount`/`readCount`). |
| **D3** | `fromCoinModel` / Test 12 invented `nacCode`/`composition`/`weight`/`diameter`; `storageLocation: 'Public Catalog'` on guest coin; redaction could not fail | `fromCoinModel` uses only real fields: `personalRef` (accepted as `nacCode` **only** if it matches `^NAC1?\.`, otherwise empty — a free-form personal reference is never copied), `themeSubject`, `denomination`, `metalContent`; `weightG`/`diameterMm` are `null` (CoinModel has no weight/diameter → render "Not Recorded"). Image is `referenceImageUrl` only (invented default URL removed). `toSyntheticCoinModel()` sets no private fields (`storageLocation`, `personalNotes`, `purchaseCost` keep constructor defaults `''`, `''`, `'\$0.00'`); `personalNotes: null`/`cpgRetail: double?` removed because the pin fields are non-nullable. Test 12 fixture uses `personalRef` and gains assertions on the synthetic model that **fail** if any owner private value is copied through. | `git show 4d17ca5e:numista_mobile/lib/models/coin_model.dart`: fields `:8 denomination`, `:10 themeSubject`, `:17 metalContent`, `:19 purchaseCost`, `:24 storageLocation`, `:25 personalNotes`, `:26 personalRef`, `:46 imageUrlObverse`, `:54 final double cpgRetail;`; no `nacCode`, `composition`, `weight`, `diameter` field in `:5-79`. Constructor `:81 CoinModel({`, `:82 required this.id,`, defaults `:85 denomination = ''`, `:87 themeSubject = ''`, `:94 metalContent = ''`, `:96 purchaseCost = '\$0.00'`, `:101 storageLocation = ''`, `:102 personalNotes = ''`, `:103 personalRef = ''`, `:107 imageUrlObverse = ''`. |
| **D4** | Test 13: widget never read `harness.clock`; asserted text contradicted §6.4 | §6.5 (new) specifies the laws loader: deadline = `clock.now + 4.0s`, a 250 ms `Timer.periodic` compares `clock.now` to the deadline, fetch goes through `harness.lawsFetcher` when set. Test 13 uses a coin whose key is **not** in the manifest, a fetcher that never completes, advances `harness.clock` 5 s, pumps 300 ms, and asserts the §6.4 step-3 text `"Founding legislation details pending verification."` (manifest hits never reach the network, so the old manifest-title assertion could not test a timeout). | Plan-internal consistency with §6.4 steps 1–3. Production clock = `DateTime.now()`. Not executed (PLAN ONLY). |
| **D5** | Test 14 read nonexistent public `currentParentIndex`; `_UnifiedCoinDetailScreenState` is library-private so `tester.state<_...>` cannot compile in a test file | §3.2 adds public `abstract class UnifiedCoinDetailNavState { int? get currentParentIndex; }` implemented by the private state with `@visibleForTesting int? get currentParentIndex => _currentParentIndex;`. Test 14 casts `tester.state(find.byType(UnifiedCoinDetailScreen)) as UnifiedCoinDetailNavState`. | Dart library privacy; plan-internal. |

## Must-Fix Closeout & Traceability Matrix (CoS-89 Must-Fixes 1–7) — carried forward from v1.7

| Item | CoS-89 Must-Fix Issue | Resolution Summary in v1.7 | Plan Section |
|---|---|---|---|
| **MF-1** | **Re-quote §2.6 header subtitle `:925` verbatim:** Pin is `style: const TextStyle(color: Colors.white60, fontSize: 12)`. v1.6 regressed to `Colors.white.withAlpha(180)`. | Restored exact verbatim code line from `git show 4d17ca5e:numista_mobile/lib/screens/coin_detail_screen.dart:925`: `style: const TextStyle(color: Colors.white60, fontSize: 12)),`. Verified `:59`, `:892–893`, `:918–921` remain 100% verbatim. | §2.6 |
| **MF-2** | **§4.1 public call site grounding:** `:315` is `child: Column(` under Morgan owl header. Real open path is card `onTap: () => _showItemDetailModal(item)` at `:466`, plus `_showItemDetailModal` at `:810` and initial-NAC at `:80`. | Quoted lines 466, 810, and 80 verbatim from `git show origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`. Explicitly noted `:315` is non-interactive header layout. Wired `UnifiedCoinDetailScreen.showPublic` replacement directly inside `_showItemDetailModal` (`:810`), cleanly routing card taps and initial-NAC direct links. | §4.1 |
| **MF-3** | **Test 14 two consecutive Next steps:** Fixture starting on parent set only has one Next (`c2`). Must perform two consecutive Next steps that both succeed and assert `_currentParentIndex` after each step. | Added `c0` (`1881-S Morgan Dollar`) before parent set `set_1` (which contains two virtual children). First Next steps `c0` -> `set_1` (asserting `currentParentIndex == 1`); second Next steps `set_1` -> `c2` skipping virtual children (asserting `currentParentIndex == 4`). Both steps succeed and indices are checked. | §10 (Test 14) |
| **MF-4** | **Test 13 advance FakeClock during in-flight request:** Advancing 5s before `pumpWidget` does not simulate a mid-request 4.0s timeout. Widget must read clock during fetch; advance after pump while request is outstanding. | Mounted widget and tapped Legislation tab. Pumped single frame (`await tester.pump()`) so async request is outstanding. Advanced `harness.clock` 5s while fetch is in flight, then called `pumpAndSettle()`. Asserted clean fallback to checked offline legislation manifest. | §10 (Test 13) |
| **MF-5** | **Test 11 must be able to fail:** Widget implementation must perform reads/writes through `harness.firestoreService`. | Wired widget to execute document queries through `harness.firestoreService`. (v1.7 text used a nonexistent `seedDocument`; **superseded by v1.8 D2**: seed via `setDoc`, widget reads via `getDoc`.) Asserted `t.store.writeCount == 0`, proving test can fail if writes occur. | §10 (Test 11) |
| **MF-6** | **Test 12 same owner fixture for guest redaction:** Guest view must use identical fixture as owner view to prove private fields (`storageLocation`, notes, purchase cost) are absent due to redaction, not absent from projection. | Built single owner coin fixture with accepted user photo, reference image, and private fields (`storageLocation`, `personalNotes`, `purchaseCost`). Verified owner view renders user photo and private fields. Derived guest view via `PublicCoinProjection.fromCoinModel(ownerCoin, referenceImageUrl: refPhoto)`. Verified guest view renders reference photo and redacts all private fields. | §4.2, §10 (Test 12) |
| **MF-7** | **Record delivery commit `2dbb525e` in §12:** v1.6 left 'Delivery Commit: To be recorded' after commit already existed on `origin/dev`. | Recorded delivery commit `2dbb525e` in §12 as the v1.6 delivery commit; recorded current v1.7 delivery on branch `dev`. | §11.1, §12 |

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
925:                     style: const TextStyle(color: Colors.white60, fontSize: 12)),
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
  final UnifiedCoinDetailDeps? deps;

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
    this.deps,
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
    this.deps,
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
    UnifiedCoinDetailDeps? deps,
    required Future<void> Function() legacyOpen, // v1.9 G5: existing pre-NET-813 invocation
  }) async {
    if (!await UnifiedDetailsGate.isEnabled()) return legacyOpen(); // kill-switch, fail-closed
    if (!context.mounted) return;
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
      deps: deps,
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
    UnifiedCoinDetailDeps? deps,
    required Future<void> Function() legacyOpen, // v1.9 G5
  }) async {
    if (!await UnifiedDetailsGate.isEnabled()) return legacyOpen();
    if (!context.mounted) return;
    final width = MediaQuery.of(context).size.width;
    final widget = UnifiedCoinDetailScreen.public(
      projection: projection,
      deps: deps,
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
/// v1.8 (D5): public, test-visible view of navigation state.
abstract class UnifiedCoinDetailNavState {
  int? get currentParentIndex;
}

class _UnifiedCoinDetailScreenState extends State<UnifiedCoinDetailScreen>
    implements UnifiedCoinDetailNavState {
  late CoinModel? _currentCoin;
  late DocumentSnapshot? _currentSnapshot;
  late int? _currentParentIndex;

  @override
  @visibleForTesting
  int? get currentParentIndex => _currentParentIndex;

  @override
  void initState() {
    super.initState();
    _currentCoin = widget.initialCoin;
    _currentSnapshot = widget.initialSnapshot;
    _currentParentIndex = widget.initialParentIndex;
    _loadCurrentDoc(); // v1.8 (D2)
  }

  /// v1.9 (G3): ONE data-access boundary for tests and production. No test-only branch.
  late final UnifiedCoinDetailDeps _deps =
      widget.deps ?? UnifiedCoinDetailDeps.production(widget.cachedCoinsDocs);

  /// Read-only refresh of the displayed doc through _deps.store (production: in-memory
  /// cachedCoinsDocs, 0 Firestore reads/writes). Never calls setDoc.
  Future<void> _loadCurrentDoc() async {
    final id = _currentCoin?.id;
    if (id == null || id.isEmpty) return;
    final data = await _deps.store.getDoc('coins', id);
    if (!mounted || data == null) return;
    setState(() => _currentCoin = CoinModel.fromMap(data, id));
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

  /// v2.1 MF-5: Explicit widget contract for build(BuildContext) (required keys, controls, currency format).
  /// Currency format: single standard `\$${val.toStringAsFixed(2)}` everywhere (e.g. `\$50.00`, `\$45.00`).
  @override
  Widget build(BuildContext context) {
    final isPublic = widget.publicProjection != null;
    final coin = _currentCoin ?? widget.publicProjection?.toSyntheticCoinModel();
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final headerBg = isDark ? const Color(0xFF0F172A) : const Color(0xFF0B1A2E);
    final headerFg = isDark ? const Color(0xFFF8FAFC) : Colors.white;
    final heroUrl = _selectHeroImageUrl(coin); // owner: isOwnedStorageUrl; public: _approvedCatalogHosts

    return Column(
      children: [
        Container(
          key: const Key('udv_header_surface'),
          decoration: BoxDecoration(color: headerBg),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  coin?.themeSubject ?? '',
                  key: const Key('udv_header_title'),
                  style: TextStyle(color: headerFg, fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
              if (canNavigateNext)
                IconButton(
                  icon: const Icon(Icons.arrow_forward_ios, color: Colors.white),
                  onPressed: () => _stepNavigation(1),
                ),
            ],
          ),
        ),
        if (heroUrl != null)
          Builder(builder: (_) {
            _deps.onImageLoad?.call(heroUrl);
            return Image.network(heroUrl, key: const Key('hero_coin_image'));
          }),
        TextButton(
          onPressed: () => setState(() => _showValues = !_showValues),
          child: const Text('Show values'),
        ),
        if (_showValues && coin != null) ...[
          if (coin.cpgRetail > 0) Text('\$${coin.cpgRetail.toStringAsFixed(2)}'),
          if (!isPublic && coin.purchaseCost.isNotEmpty)
            Text('\$${(double.tryParse(coin.purchaseCost.replaceAll(r'$', '')) ?? 0.0).toStringAsFixed(2)}'),
        ],
        if (!isPublic) ...[
          if (coin?.storageLocation.isNotEmpty ?? false) Text(coin!.storageLocation),
          if (coin?.personalNotes.isNotEmpty ?? false)
            MarkdownBody(
              data: sanitizeNotesText(coin!.personalNotes),
              styleSheet: getSandboxedMarkdownStyleSheet(context),
              imageBuilder: (_, __, ___) => const SizedBox.shrink(),
              onTapLink: (_, __, ___) {},
            ),
          ElevatedButton(
            key: const Key('ebay_search_button'),
            onPressed: () => _launchEbaySearch(coin!),
            child: const Text('Search eBay'),
          ),
        ],
        // TabBar includes Tab(text: 'Overview'), Tab(text: 'Financials'), Tab(text: 'Legislation')
        // Tapping 'Legislation' runs _matchLawKey() + _kDefaultLaws/manifest + _deps.lawsFetcher.
      ],
    );
  }
}
```

### 3.3 Strict Virtual-Child Parent Index Resolution
**v2.1 (MF-2):** the rule below is implemented once, in production, and every A3.4 call site calls it (no duplicate `_resolveParentIndexForVirtualChild` helper):
```dart
/// numista_mobile/lib/screens/unified_coin_detail_screen.dart (top-level)
@visibleForTesting
int? resolveParentIndex(List<CollectionRow> rows, CollectionRow tapped) {
  final targetId = tapped.isVirtualChild ? (tapped.parentDocId ?? '') : tapped.id;
  if (targetId.isEmpty) return null;
  final i = rows.indexWhere((r) => r.id == targetId);
  return i >= 0 ? i : null;
}
```
*Rule:* If the parent set row is absent from `collectionRows` (for example, if a search filter matches the child quarter but not the parent set), `currentParentIndex` resolves to `null` (standalone mode). It NEVER falls back to the child's index.

### 3.4 Wire-up Across All Five Call Sites in `my_collection_screen.dart` (MF-2)
Every snippet below is paste-ready, uses top-level `resolveParentIndex(docs, ...)`, and passes `legacyOpen: () async => ...` wrapping the exact pin `4d17ca5e` call:

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
    final parentIdx = resolveParentIndex(docs, crw);
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
      legacyOpen: () async => _showCoinInspectorDialog(effectiveId, m),
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
      legacyOpen: () async => _showCoinInspectorDialog(effectiveId, m),
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
  final parentIdx = resolveParentIndex(docs, crw);
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
    legacyOpen: () => CoinDetailScreen.show(
      context,
      coin: coin,
      spotPrices: _spotPrices,
      onNavigateToAiChat: widget.onNavigateWithQuery != null
          ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
          : null,
      onDeleted: () => setState(() {}),
      onEdited: () => setState(() {}),
    ),
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
    legacyOpen: () => CoinDetailScreen.show(
      context,
      coin: coin,
      spotPrices: _spotPrices,
      onNavigateToAiChat: widget.onNavigateWithQuery != null
          ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
          : null,
      onDeleted: () => setState(() {}),
      onEdited: () => setState(() {}),
    ),
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
    final parentIdx = resolveParentIndex(docs, crw);
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
      legacyOpen: () async => _showCoinInspectorDialog(effectiveId, m),
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
      legacyOpen: () async => _showCoinInspectorDialog(effectiveId, m),
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
    final parentIdx = resolveParentIndex(docs, CollectionRow(id: parentId, data: parentData));
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
      legacyOpen: () async => _showCoinInspectorDialog(parentDoc.id, parentData),
    );
  }
},
```

### 3.5 Navigation Transition Resolver & List Stability
- **List Changes While Open:** If background Firestore updates modify `_cachedCoinsDocs` or collection rows while the modal is open, the modal retains its captured `collectionRows` and `cachedCoinsDocs` instance for the lifetime of that modal session. This guarantees index stability during stepping.
- **Deduplication:** When moving through a list containing multiple virtual children of the same parent set, `_stepNavigation` skips forward or backward past all rows sharing the same resolved parent ID, landing on the next distinct coin or set.

---

## 4. Public Catalog Entry Binding & Projections (MF-1)

### 4.1 Real Public Call Sites on `origin/dev` (MF-2)
On `git show origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`, public catalog items are opened from three call sites:
1. **Catalog Card Tap (`catalog_browse_screen.dart:464-467`; `onTap` at `:466`):**
```dart
464:                                   return _CatalogCard(
465:                                     item: item,
466:                                     onTap: () => _showItemDetailModal(item),
467:                                   );
```
2. **Modal Invocation Function (`catalog_browse_screen.dart:810`):**
```dart
810:   void _showItemDetailModal(Map<String, dynamic> item) {
811:     showDialog(
812:       context: context,
813:       builder: (context) {
```
3. **Initial NAC Direct Link Entry (`catalog_browse_screen.dart:77-82`; call at `:80`):**
```dart
77:           if (match.isNotEmpty) {
78:             WidgetsBinding.instance.addPostFrameCallback((_) {
79:               if (mounted) {
80:                 _showItemDetailModal(match);
81:               }
82:             });
```

*(Note: Line 315 on `origin/dev` is non-interactive layout `child: Column(` under the Morgan owl banner and is never an open site).*

#### Replacement Wire-Up:
In `catalog_browse_screen.dart`, `_showItemDetailModal(Map<String, dynamic> item)` at line 810 is replaced directly with `UnifiedCoinDetailScreen.showPublic`:
```dart
  void _showItemDetailModal(Map<String, dynamic> item) {
    UnifiedCoinDetailScreen.showPublic(
      context,
      projection: PublicCoinProjection.fromCatalogMap(item),
      legacyOpen: () async => _showLegacyItemDetailModal(item), // existing :810 body, renamed unchanged
    );
  }
```
This single point of replacement seamlessly routes card taps (`:466`) and initial-NAC direct loads (`:80`) into `UnifiedCoinDetailScreen` without altering card rendering logic.

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
      primaryImageUrl: _approvedPrimaryImageUrl(m['primary_image']), // v1.9 G1: real nested schema
      legislationKey: m['legislation_key']?.toString(),
      weightG: m['weight_g']?.toString() ?? 'Not Recorded',
      diameterMm: m['diameter_mm']?.toString() ?? 'Not Recorded',
    );
  }

  /// v2.1 (MF-4d / FALSE MF-4b): catalog `primary_image` on `b0b05808` is an object
  /// `{url, full_url, side, unique_side, license, credit, source_url, resolution}` (no `source` key).
  /// Owner photos use `isOwnedStorageUrl` (§7.4); catalog heroes use this separate host allowlist
  /// verified from `b0b05808:numista_mobile/assets/catalog/catalog_public_v1.json`.
  static const Set<String> _approvedCatalogHosts = {
    'images.metmuseum.org',
    'numismatics.org',
    'thumb.wikimedia.org',
    'upload.wikimedia.org',
  };

  static String? _approvedPrimaryImageUrl(dynamic img) {
    if (img is! Map) return null;
    final url = img['url']?.toString() ?? '';
    final license = img['license']?.toString() ?? '';
    final source = img['source_url']?.toString() ?? '';
    final uri = Uri.tryParse(url);
    if (uri == null || uri.scheme != 'https' || uri.userInfo.isNotEmpty) return null;
    if (!_approvedCatalogHosts.contains(uri.host.toLowerCase())) return null;
    if (license.isEmpty || source.isEmpty) return null;
    return url;
  }

  factory PublicCoinProjection.fromCoinModel(CoinModel coin, {String? referenceImageUrl}) {
    // Redacts all private owner fields (storageLocation, personalNotes, purchaseCost, unapproved user photos)
    return PublicCoinProjection(
      // v1.8 (D3): real CoinModel fields only (pin coin_model.dart :8, :10, :17, :26, :54).
      // personalRef is accepted ONLY when it is a catalog NAC code; free-form personal refs are dropped.
      nacCode: RegExp(r'^NAC1?\.').hasMatch(coin.personalRef.trim().toUpperCase())
          ? coin.personalRef.trim().toUpperCase()
          : '',
      title: coin.themeSubject.isNotEmpty ? coin.themeSubject : 'Catalog Coin',
      denomination: coin.denomination,
      composition: coin.metalContent.isNotEmpty ? coin.metalContent : 'Not Recorded',
      // v2.1 (MF-7a): pin CoinModel.cpgRetail is `final double` defaulting to 0.0; map > 0, else null (unavailable)
      cpgRetail: coin.cpgRetail > 0 ? coin.cpgRetail : null,
      primaryImageUrl: referenceImageUrl, // never the owner's imageUrlObverse
      legislationKey: null,
      weightG: null,   // CoinModel has no weight field at pin -> "Not Recorded"
      diameterMm: null, // CoinModel has no diameter field at pin -> "Not Recorded"
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
      cpgRetail: cpgRetail ?? 0.0,
      imageUrlObverse: primaryImageUrl ?? '',
      // v1.8 (D3): no private field is set. storageLocation / personalNotes /
      // purchaseCost keep pin constructor defaults ('' / '' / '\$0.00').
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

### 6.1 `_kDefaultLaws` & `checked_legislation_manifest.json` Specification (MF-3)
Core law entries below match `_kDefaultLaws` in `4d17ca5e:numista_mobile/lib/screens/coin_detail_screen.dart:2973–3027`. Note: `"editorial_verified": false` is a plan manifest annotation stored in `assets/data/checked_legislation_manifest.json` (the pin's `_kDefaultLaws` map itself does not carry an `editorial_verified` key).

To resolve a coin's legislation key (since pin `CoinModel` has no `legislationKey` field), `_UnifiedCoinDetailScreenState` ports `_matchLawKey()` **verbatim** from `4d17ca5e:numista_mobile/lib/screens/coin_detail_screen.dart:3030–3068`:
```dart
// Verbatim from 4d17ca5e:numista_mobile/lib/screens/coin_detail_screen.dart:3030-3068
String? _matchLawKey(CoinModel coin) {
  final series = coin.programSeries.toLowerCase();
  final denom  = coin.denomination.toLowerCase();
  final theme  = coin.themeSubject.toLowerCase();

  if (series.contains('state quarter') || series.contains('50 state') ||
      series.contains('statehood quarter')) {
    return '105-124';
  }
  if ((series.contains('america') && series.contains('beautiful')) || series.contains('atb') || series.contains('national park')) {
    return '110-456';
  }
  if (series.contains('territor') || series.contains('district of columbia') || series.contains('dc &') || series.contains('dc and')) {
    return '110-161';
  }
  if (series.contains('women quarter') || series.contains('american women')) {
    return '116-330';
  }
  if (series.contains('presidential dollar') || series.contains('president dollar')) {
    return '109-145';
  }
  if (series.contains('silver eagle') || series.contains('american silver eagle') ||
      series.contains('gold eagle')) {
    return '99-61';
  }
  if (series.contains('susan b') || series.contains('anthony'))      return '95-447';
  if (series.contains('eisenhower'))                                 return '91-607';
  if (series.contains('march of dimes') || theme.contains('march of dimes')) {
    return '112-209';
  }
  if (series.contains('sacagawea') || series.contains('native american dollar')) {
    return '106-445';
  }
  // Coinage Act 1965: affected all silver coins — halves, quarters, dimes
  if (denom.contains('half dollar') || denom.contains('quarter') ||
      denom.contains('dime')) {
    return '89-81';
  }
  return null;
}
```

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
Only URLs matching the exact Congress.gov pattern (with no `userInfo`) are allowed to launch outbound:
```dart
bool isValidCongressGovUrl(String? rawUrl) {
  if (rawUrl == null || rawUrl.trim().isEmpty) return false;
  final uri = Uri.tryParse(rawUrl.trim());
  if (uri == null) return false;
  if (uri.scheme != 'https' || uri.userInfo.isNotEmpty || uri.hasPort) return false;
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
Future<void> launchOutboundCongressUrl(BuildContext context, String url, {UnifiedCoinDetailDeps? harness}) async {
  if (!isValidCongressGovUrl(url)) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Invalid or untrusted legislative link'),
        backgroundColor: Colors.redAccent,
      ),
    );
    return;
  }
  if (harness?.onLaunchUrl != null) {
    harness!.onLaunchUrl!(url);
    return;
  }
  await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
}
```

### 6.4 Single Unified Precedence Table for Legislation Tab (MF-3)
1. Derive `key = widget.publicProjection?.legislationKey ?? _matchLawKey(coin)`.
2. Match `key` against `_kDefaultLaws` / `assets/data/checked_legislation_manifest.json`.
3. If not in local manifest, fall back to `deps.lawsFetcher?.call(key)` (which in production reads Firestore `metadata/coin_legislation` doc per pin `4d17ca5e:coin_detail_screen.dart` — no invented Congress.gov HTTP client), guarded by a strict 4.0-second timeout.
4. If timeout occurs or key is not recognized, display standard fallback: `"Founding legislation details pending verification."`

### 6.5 Laws Loader Clock Wiring (v2.1 MF-3)
```dart
// inside _UnifiedCoinDetailScreenState
Timer? _lawsWatchdog;
bool _lawsTimedOut = false;

DateTime _now() => _deps.clock.now; // v1.9 G3: SystemDetailClock in production

Future<void> _fetchLawsOnline(String key) async {
  final deadline = _now().add(const Duration(milliseconds: 4000));
  _lawsWatchdog?.cancel();
  _lawsWatchdog = Timer.periodic(const Duration(milliseconds: 250), (t) {
    if (_now().isAfter(deadline)) {
      t.cancel();
      if (mounted) setState(() => _lawsTimedOut = true); // renders §6.4 step-4 text
    }
  });
  final fetch = _deps.lawsFetcher; // null in production if Firestore metadata/coin_legislation unavailable
  if (fetch == null) {
    _lawsWatchdog?.cancel();
    return;
  }
  final result = await fetch(key);
  if (!mounted || _lawsTimedOut) return; // late results after timeout are ignored
  _lawsWatchdog?.cancel();
  setState(() => _laws = result);
}

@override
void dispose() {
  _lawsWatchdog?.cancel();
  super.dispose();
}
```
Only reached when the §6.4 step-1 manifest lookup misses.

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

### 7.4 Image Security Guard (`isOwnedStorageUrl` for Owner Photos vs Catalog Allowlist)
`isOwnedStorageUrl` validates **owner-uploaded** and first-party Numista Cloud Storage buckets. Public **catalog** hero images (`primary_image.url`) are validated separately by `PublicCoinProjection._approvedPrimaryImageUrl` (§4.2) against `_approvedCatalogHosts` (`images.metmuseum.org`, `numismatics.org`, `thumb.wikimedia.org`, `upload.wikimedia.org`) + non-empty `license` & `source_url`:
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

### 9.1 Preview-Only Rollback Sequence & Command Specification (MF-6)
Live production Hosting (`numista-vault:live`) is **never** modified or cloned by this plan without a separate explicit Founder YES. Preview rollback deletes only the isolated preview channel:
1. **Delete Preview Channel:**
   ```bash
   firebase hosting:channel:delete pr-net813 --site numista-vault --force
   ```

### 9.2 Git Code Revert Procedure (Portable, Local Revert Only)
1. Record all commit SHAs in `scratch/revert_shas_net813.txt`.
2. Verify ancestry before any revert using an explicit loop:
   ```bash
   while IFS= read -r commit_sha; do
     [ -z "$commit_sha" ] && continue
     git merge-base --is-ancestor "$commit_sha" HEAD || { echo "SHA $commit_sha not in HEAD ancestry"; exit 1; }
   done < scratch/revert_shas_net813.txt
   ```
3. Execute clean local revert in reverse chronological order using portable `awk` (no `tac`, no `reset --hard`; push requires a separate Founder YES):
   ```bash
   REV_LIST=$(awk '{lines[NR]=$0} END {for (i=NR; i>=1; i--) if (lines[i] != "") print lines[i]}' scratch/revert_shas_net813.txt)
   for sha in $REV_LIST; do
     git revert --no-edit "$sha" || { git revert --abort || true; exit 1; }
   done
   ```

### 9.3 Client-Side Operational Kill-Switch & Pubspec Manifest (MF-4c, MF-7b)
- **Ship Default Disabled Config:** Ship `numista_mobile/assets/config/features.json` containing `{"unified_details_view_v1": false}` (fail-closed by default). Flipping the flag to `true` (or back to `false`) requires an **app restart** because `UnifiedDetailsGate.isEnabled()` memoizes `_cached` once per session.
- **Asset Declaration in `pubspec.yaml`:**
  Pin `4d17ca5e` lines 92–96 do not include `assets/catalog/` or `assets/config/` (`assets/` is not recursive in Flutter; `b0b05808:pubspec.yaml:97` already adds `- assets/catalog/`). Both must be declared in `numista_mobile/pubspec.yaml`:
  ```yaml
  flutter:
    uses-material-design: true
    assets:
      - assets/
      - assets/data/
      - assets/fonts/
      - assets/mint_mark_diagrams/
      - assets/catalog/
      - assets/config/
  ```
- **Direct Asset Loader:**
  Loaded directly from bundle without cache-busting query strings:
  ```dart
  /// v1.9 (G5): the ONE gate consulted by show() and showPublic() (all six entry paths).
  class UnifiedDetailsGate {
    static Future<bool>? _cached;           // loaded once per app session
    @visibleForTesting
    static AssetBundle? debugBundle;        // tests inject a bundle; null = rootBundle
    @visibleForTesting
    static void debugReset() => _cached = null;

    static Future<bool> isEnabled() => _cached ??= _load();

    static Future<bool> _load() async {
      try {
        final jsonStr = await (debugBundle ?? rootBundle).loadString('assets/config/features.json');
        final Map<String, dynamic> config = jsonDecode(jsonStr);
        return config['unified_details_view_v1'] == true;
      } catch (_) {
        return false; // fail closed to legacy views if config missing/malformed
      }
    }
  }
  ```
  Every A3.4 call site keeps its current legacy call verbatim inside `legacyOpen: () => <existing call>`; the catalog site's current `_showItemDetailModal` body (dev `:810`) is renamed `_showLegacyItemDetailModal` unchanged.
  ```dart
  // (end of gate spec)
  ```

---

## 9.4 Shared Dependency Contracts (v1.9 G2/G3) — `numista_mobile/lib/screens/unified_coin_detail_deps.dart` (New)
```dart
import 'package:cloud_firestore/cloud_firestore.dart' show QueryDocumentSnapshot;

abstract class CoinDocStore {
  int get writeCount;
  int get readCount;
  Future<Map<String, dynamic>?> getDoc(String collection, String id);
  Future<void> setDoc(String collection, String id, Map<String, dynamic> data);
}

abstract class DetailClock { DateTime get now; }

typedef LawsFetcher = Future<Map<String, dynamic>?> Function(String legislationKey);
typedef UrlLauncherHook = void Function(String url);
typedef ImageLoadRecorder = void Function(String url);

class UnifiedCoinDetailDeps {
  final CoinDocStore store;
  final DetailClock clock;
  final LawsFetcher? lawsFetcher; // null -> no online fallback
  final UrlLauncherHook? onLaunchUrl; // v2.1 MF-1: injected in tests, null in production
  final ImageLoadRecorder? onImageLoad; // v2.1 MF-1: injected in tests, null in production
  const UnifiedCoinDetailDeps({
    required this.store,
    required this.clock,
    this.lawsFetcher,
    this.onLaunchUrl,
    this.onImageLoad,
  });

  factory UnifiedCoinDetailDeps.production(List<QueryDocumentSnapshot<Map<String, dynamic>>> cached) =>
      UnifiedCoinDetailDeps(store: CachedCoinDocStore(cached), clock: const SystemDetailClock());
}

/// Production store: in-memory over cachedCoinsDocs. 0 Firestore reads, 0 writes.
class CachedCoinDocStore implements CoinDocStore {
  final List<QueryDocumentSnapshot<Map<String, dynamic>>> _docs;
  CachedCoinDocStore(this._docs);
  @override
  int get writeCount => 0;
  @override
  int readCount = 0;
  @override
  Future<Map<String, dynamic>?> getDoc(String collection, String id) async {
    readCount++;
    for (final d in _docs) { if (d.id == id) return d.data(); }
    return null;
  }
  @override
  Future<void> setDoc(String c, String id, Map<String, dynamic> data) =>
      throw UnsupportedError('Unified Coin Details is read-only');
}

class SystemDetailClock implements DetailClock {
  const SystemDetailClock();
  @override
  DateTime get now => DateTime.now();
}
```
Manifest addition: `numista_mobile/lib/screens/unified_coin_detail_deps.dart` — **New**, to be authored on Eric YES.

## 10. Implementable Offline Test Plan & Complete Test Suite (MF-1, MF-2, MF-4, MF-5)

The entire offline test suite is authored below in `test/screens/unified_coin_detail_screen_test.dart`. It includes real implementations for `FakeFirestoreService`, `FakeClock`, `FakeQueryDocumentSnapshot`, and `UnifiedCoinDetailDeps`:

```dart
import 'dart:async';
import 'dart:convert'; // v2.0 H2: jsonDecode in Test 15
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/models/collection_row.dart';
import 'package:numista_ai/screens/unified_coin_detail_screen.dart';
import 'package:numista_ai/screens/unified_coin_detail_deps.dart'; // v1.9 G2 shared contracts
import 'package:flutter/services.dart';

// -----------------------------------------------------------------------------
// v1.9 (G2): test fakes IMPLEMENT the production contracts imported from
// package:numista_ai/screens/unified_coin_detail_deps.dart. No production names redeclared.
// -----------------------------------------------------------------------------

class CountingCoinDocStore implements CoinDocStore {
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

class ManualClock implements DetailClock {
  DateTime _now = DateTime(2026, 11, 7, 20, 30);
  @override
  DateTime get now => _now;
  void advance(Duration d) => _now = _now.add(d);
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

/// Test-side bundle of fakes; passes a real UnifiedCoinDetailDeps to the widget.
class TestDeps {
  final store = CountingCoinDocStore();
  final clock = ManualClock();
  final List<String> loadedImageUrls = [];
  String? lastLaunchedUrl;
  Future<Map<String, dynamic>?> Function(String key)? lawsFetcher;
  UnifiedCoinDetailDeps get deps => UnifiedCoinDetailDeps(
        store: store,
        clock: clock,
        lawsFetcher: lawsFetcher,
        onLaunchUrl: (u) => lastLaunchedUrl = u,
        onImageLoad: loadedImageUrls.add,
      );
  int get firestoreWriteCount => store.writeCount;
  int get firestoreReadCount => store.readCount;
  void reset() {
    store.writeCount = 0;
    store.readCount = 0;
    lawsFetcher = null;
    loadedImageUrls.clear();
    lastLaunchedUrl = null;
  }
}

// -----------------------------------------------------------------------------
// Test Suite
// -----------------------------------------------------------------------------

// v2.0 H1: top-level (legal Dart). Re-reads t.deps on each access, so lawsFetcher set inside a test is honored.
final t = TestDeps();
UnifiedCoinDetailDeps get harness => t.deps;

void main() {

  setUp(() { t.reset(); UnifiedDetailsGate.debugReset(); UnifiedDetailsGate.debugBundle = _GateBundle.enabled(); });

  double contrast(Color a, Color b) {
    final l1 = a.computeLuminance(), l2 = b.computeLuminance();
    return (l1 > l2) ? (l1 + 0.05) / (l2 + 0.05) : (l2 + 0.05) / (l1 + 0.05);
  }

  // Test 1 (v1.9 G4): contrast measured on the MOUNTED header, light and dark
  for (final mode in [ThemeMode.light, ThemeMode.dark]) {
    testWidgets('Test 1: rendered header contrast >= 7:1 ($mode)', (tester) async {
      await tester.pumpWidget(MaterialApp(
        theme: ThemeData.light(), darkTheme: ThemeData.dark(), themeMode: mode,
        home: Scaffold(body: UnifiedCoinDetailScreen(coin: CoinModel(id: 'h1', themeSubject: 'Header Test'), deps: harness)),
      ));
      await tester.pumpAndSettle();
      final text = tester.widget<Text>(find.byKey(const Key('udv_header_title')));
      final surface = tester.widget<Container>(find.byKey(const Key('udv_header_surface')));
      final fg = text.style!.color!;
      final bg = (surface.decoration as BoxDecoration).color!;
      expect(contrast(fg, bg), greaterThanOrEqualTo(7.0));
    });
  }

  // Test 2 (v1.9 G4): the SHIPPED resolver used by all five call sites
  test('Test 2: resolveParentIndex maps virtual child to parent index', () {
    final parentRow = CollectionRow(id: 'parent_1', data: const {'id': 'parent_1'});
    final childRow = CollectionRow(id: 'parent_1__set_coin_0', data: const {'id': 'parent_1__set_coin_0'},
        parentDocId: 'parent_1', isVirtualChild: true);
    expect(resolveParentIndex([parentRow, childRow], childRow), equals(0));
    expect(resolveParentIndex([parentRow, childRow], parentRow), equals(0));
  });

  // Test 3 (v1.9 G4): parent excluded -> null (standalone)
  test('Test 3: resolveParentIndex returns null when parent row is absent', () {
    final childRow = CollectionRow(id: 'parent_1__set_coin_0', data: const {'id': 'parent_1__set_coin_0'},
        parentDocId: 'parent_1', isVirtualChild: true);
    expect(resolveParentIndex([CollectionRow(id: 'other_coin', data: const {'id': 'other_coin'})], childRow), isNull);
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
        body: UnifiedCoinDetailScreen(coin: coin, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.byType(Image), findsNothing);
    expect(t.loadedImageUrls.contains('https://evil.com/exploit.png'), isFalse);
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
          deps: harness,
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

    expect(t.lastLaunchedUrl, equals('https://www.congress.gov/bill/110th-congress/house-bill/6184'));
    expect(t.lastLaunchedUrl!.contains('auth'), isFalse);
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
        body: UnifiedCoinDetailScreen(coin: coin, deps: harness),
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
        body: UnifiedCoinDetailScreen.public(projection: proj, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.text('Not Recorded'), findsAtLeastNWidgets(1));
  });

  // Test 11: Read-only detail view wires deps.store and performs 0 writes (MF-5)
  testWidgets('Test 11: Read-only detail view wires deps.store and performs 0 writes', (tester) async {
    final doc = FakeQueryDocumentSnapshot('c1', {
      'id': 'c1',
      'themeSubject': 'Morgan Dollar',
    });
    final coin = CoinModel.fromMap(doc.data(), 'c1');

    // Seed fixture through the real harness API, then zero the counters so only
    // the widget's own calls are counted.
    await t.store.setDoc('coins', 'c1', doc.data());
    t.reset();

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(
          coin: coin,
          cachedCoinsDocs: [doc],
          deps: harness,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    // The WIDGET (not the test body) must have read through the harness (D2).
    expect(t.firestoreReadCount, greaterThanOrEqualTo(1));

    // Interact with UI
    await tester.tap(find.byType(UnifiedCoinDetailScreen));
    await tester.pumpAndSettle();

    // Assert that the injected Firestore service recorded zero writes
    expect(t.store.writeCount, equals(0));
    expect(t.firestoreWriteCount, equals(0));
  });

  // Test 12: Photo priority: Owner user photo outranks reference image; Guest view on same fixture redacts private fields (MF-6)
  testWidgets('Test 12: Photo priority (user photo > reference image) and guest redactions on same fixture', (tester) async {
    const userPhoto = 'https://firebasestorage.googleapis.com/v0/b/numista-vault.appspot.com/o/users%2Fuser1%2Fphoto.jpg?alt=media';
    const refPhoto = 'https://storage.googleapis.com/numista-reference-library/morgan.jpg';

    // 1. Single owner coin fixture containing both accepted user photo and reference image, plus private fields
    final ownerCoin = CoinModel(
      id: 'fixture_1',
      personalRef: 'NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3',
      themeSubject: '1921 Morgan Dollar',
      imageUrlObverse: userPhoto,
      purchaseCost: '45.00',
      storageLocation: 'Safe Box 3',
      personalNotes: 'Private note: bought at ANA convention',
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: ownerCoin, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    // Owner view must prioritize accepted user photo in hero section and display private fields
    final heroImage = tester.widget<Image>(find.byKey(const Key('hero_coin_image')));
    expect((heroImage.image as NetworkImage).url, equals(userPhoto));
    expect(find.text('Safe Box 3'), findsOneWidget);
    expect(find.text('Private note: bought at ANA convention'), findsOneWidget);
    // Purchase cost is masked by default (A5); reveal it first (v1.9 G4, v2.1 MF-5 unified \$XX.XX format)
    expect(find.text(r'$45.00'), findsNothing);
    await tester.tap(find.text('Show values'));
    await tester.pumpAndSettle();
    expect(find.text(r'$45.00'), findsOneWidget);

    // 2. Guest view derived directly from the exact same underlying ownerCoin fixture
    final guestProjection = PublicCoinProjection.fromCoinModel(ownerCoin, referenceImageUrl: refPhoto);

    // D3: redaction must be able to FAIL if owner private values are copied through.
    final synthetic = guestProjection.toSyntheticCoinModel();
    expect(synthetic.storageLocation, isNot(equals(ownerCoin.storageLocation)));
    expect(synthetic.personalNotes, isNot(equals(ownerCoin.personalNotes)));
    expect(synthetic.purchaseCost, isNot(equals(ownerCoin.purchaseCost)));
    expect(synthetic.imageUrlObverse, isNot(equals(userPhoto)));
    expect(guestProjection.primaryImageUrl, equals(refPhoto));

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen.public(projection: guestProjection, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    // Verify that guest projection explicitly redacted private fields and used the reference photo
    final guestHeroImage = tester.widget<Image>(find.byKey(const Key('hero_coin_image')));
    expect((guestHeroImage.image as NetworkImage).url, equals(refPhoto));
    expect(find.text('Safe Box 3'), findsNothing);
    expect(find.text('Private note: bought at ANA convention'), findsNothing);
    expect(find.text(r'$45.00'), findsNothing);
    expect(find.byKey(const Key('ebay_search_button')), findsNothing);
  });

  // Test 13: Laws fetch exceeding 4.0s on harness.clock falls back to §6.4 step-3 text (D4)
  testWidgets('Test 13: Laws fetch > 4.0s on harness.clock shows pending-verification fallback', (tester) async {
    // Key deliberately NOT in _kCheckedLegislationManifest, so §6.4 step 2 (network) runs.
    final coin = CoinModel(
      id: 'unlisted_comm',
      themeSubject: 'Unlisted Test Commemorative',
      programSeries: 'Test Series Not In Manifest',
      denomination: 'Dollar',
    );
    final never = Completer<Map<String, dynamic>?>(); // never completes
    t.lawsFetcher = (_) => never.future;

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Legislation'));
    await tester.pump(); // fetch now in flight; widget recorded deadline = harness.clock.now + 4s

    t.clock.advance(const Duration(seconds: 5));
    await tester.pump(const Duration(milliseconds: 300)); // one watchdog tick reads harness.clock.now

    expect(find.text('Founding legislation details pending verification.'), findsOneWidget);
    await tester.pumpAndSettle(); // watchdog timer cancelled after resolution -> no pending timers
  });

  // Test 14: Two consecutive Next steps across a virtual-child group resolves parent index correctly (MF-3)
  testWidgets('Test 14: Two consecutive Next steps across virtual-child group maintains correct parent index', (tester) async {
    // Fixture: coin0 -> set_1 (with 2 virtual children) -> coin2
    final coin0Doc = FakeQueryDocumentSnapshot('c0', {
      'id': 'c0',
      'themeSubject': '1881-S Morgan Dollar',
    });
    final parentDoc = FakeQueryDocumentSnapshot('set_1', {
      'id': 'set_1',
      'themeSubject': '1999 Silver Proof Set',
    });
    final coin2Doc = FakeQueryDocumentSnapshot('c2', {
      'id': 'c2',
      'themeSubject': '1921 Morgan Dollar',
    });

    final row0 = CollectionRow(id: 'c0', data: coin0Doc.data());
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

    final initialCoin = CoinModel.fromMap(coin0Doc.data(), 'c0');

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(
          coin: initialCoin,
          currentParentIndex: 0,
          collectionRows: [row0, setRow, childRow1, childRow2, regularRow],
          cachedCoinsDocs: [coin0Doc, parentDoc, coin2Doc],
          deps: harness,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.text('1881-S Morgan Dollar'), findsOneWidget);

    final state = tester.state(find.byType(UnifiedCoinDetailScreen)) as UnifiedCoinDetailNavState;
    expect(state.currentParentIndex, equals(0));

    // Step 1: First Next steps from c0 to set_1
    await tester.tap(find.byIcon(Icons.arrow_forward_ios));
    await tester.pumpAndSettle();

    expect(find.text('1999 Silver Proof Set'), findsOneWidget);
    expect(state.currentParentIndex, equals(1));

    // Step 2: Second Next skips childRow1 and childRow2 (sharing parent set_1) and steps to regularRow (c2)
    await tester.tap(find.byIcon(Icons.arrow_forward_ios));
    await tester.pumpAndSettle();

    expect(find.text('1921 Morgan Dollar'), findsOneWidget);
    expect(state.currentParentIndex, equals(4));
  });

  // Test 15 (v1.9 G1): real catalog rows from the bundled asset
  testWidgets('Test 15: fromCatalogMap uses primary_image.url with provenance; null-image row -> null', (tester) async {
    final raw = await tester.runAsync(() => rootBundle.loadString('assets/catalog/catalog_public_v1.json'));
    final rows = (jsonDecode(raw!) as List).cast<Map<String, dynamic>>();
    final withImg = rows.firstWhere((r) => r['nac_code'] == 'NAC1.MD.US.PRV.LIBAM.1782.XX.BASE.S');
    final noImg = rows.firstWhere((r) => r['nac_code'] == 'NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3');
    expect(PublicCoinProjection.fromCatalogMap(withImg).primaryImageUrl,
        equals('https://images.metmuseum.org/CRDImages/es/web-large/DP-43714-001.jpg'));
    expect(PublicCoinProjection.fromCatalogMap(noImg).primaryImageUrl, isNull);
  });

  // Test 16 (v1.9 G5): disabled or missing config routes to legacy; unified screen never built
  final gateCases = <String, _GateBundle Function()>{
    'disabled': () => _GateBundle.raw('{"unified_details_view_v1": false}'),
    'missing': () => _GateBundle.missing(), // v2.0 H3: asset genuinely absent (throws)
  };
  for (final entry in gateCases.entries) {
    testWidgets('Test 16: kill-switch ${entry.key} -> legacy', (tester) async {
      UnifiedDetailsGate.debugReset();
      UnifiedDetailsGate.debugBundle = entry.value();
      var legacyCalled = false;
      await tester.pumpWidget(MaterialApp(home: Builder(builder: (ctx) => TextButton(
        onPressed: () => UnifiedCoinDetailScreen.show(ctx, coin: CoinModel(id: 'k1'),
            legacyOpen: () async { legacyCalled = true; }),
        child: const Text('open'),
      ))));
      await tester.tap(find.text('open'));
      await tester.pumpAndSettle();
      expect(legacyCalled, isTrue);
      expect(find.byType(UnifiedCoinDetailScreen), findsNothing);
    });
  }
}

/// Test-only bundle for the kill-switch config (v2.0 H3: three explicit modes, no null default).
class _GateBundle extends CachingAssetBundle {
  final String? _config; // null ONLY for .missing()
  _GateBundle.enabled() : _config = '{"unified_details_view_v1": true}';
  _GateBundle.raw(String json) : _config = json;
  _GateBundle.missing() : _config = null;
  @override
  Future<ByteData> load(String key) async => throw FlutterError('Unable to load asset: $key');
  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    final cfg = _config;
    if (key == 'assets/config/features.json' && cfg != null) return cfg;
    throw FlutterError('Unable to load asset: $key'); // .missing(): config key always throws
  }
}
```

---

## 11. Operational Gate Table & Critical Path Checkpoints (MF-6)

### 11.1 Dated Checkpoints Inside 10–16 Nov Build Window
- **Checkpoint 1 (10 Nov 2026):** Review and sign-off by Grok CoS ($\ge 95 / 100$) and SAG ($\ge 95 / 100$).
- **Checkpoint 2 (11 Nov 2026):** Founder Eric typed YES for code branch creation (`origin/dev`).
- **Checkpoint 3 (12 Nov 2026):** Add `assets/catalog/` and `assets/config/` to `numista_mobile/pubspec.yaml`; ship `assets/config/features.json` = `{"unified_details_view_v1": false}` and `checked_legislation_manifest.json`.
- **Checkpoint 4 (13 Nov 2026):** Wire call sites 1–5 in `my_collection_screen.dart` and catalog card in `catalog_browse_screen.dart`.
- **Checkpoint 5 (14 Nov 2026):** Execute test suite in `unified_coin_detail_screen_test.dart` (assert exit code 0).
- **Checkpoint 6 (15 Nov 2026):** Deploy preview channel `pr-net813` on Firebase Hosting; complete smoke verification.
- **Checkpoint 7 (16 Nov 2026):** Preview sign-off only. **No merge to `main`** — main stays locked at `9f04550a`; changing that lock is a separate explicit Eric decision, not implied by this plan's YES. Deploys and Firestore writes keep their own YES gates.

### 11.2 Read-Cost Budget & Ownership
- Detail modal fetches strictly from local in-memory cache `_cachedCoinsDocs`. Zero Firestore reads or writes occur during standard inspection or navigation transitions.
- Total Firestore write cost per modal interaction: **0 reads, 0 writes ($0.00)**.
- Google Cloud Billing Alert threshold remains at **$20.00/month** (Alerts only; never budget caps or automated shutdowns).

### 11.3 Laptop & GCS Preservation Precondition
All work is executed strictly within git worktree on branch `dev`. Production branch `origin/main` is pinned and locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`. Stripe is locked OFF across all client and server endpoints.

---

## 12. Handoff Integrity & Authorship (MF-7)

- **v2.0 Author:** GB CoS fresh writer round 3 (8 Nov 08:12 ET). Changes limited to H1–H3. v1.9 scored 90 FAIL.
- **v1.9 Author:** GB CoS fresh writer round 2 (8 Nov ~07:55 ET). Changes limited to G1–G6. v1.8 scored 86 FAIL.
- **v1.8 Author:** GB CoS fresh writer (writer-cap handoff; Eric GO 8 Nov 07:27 ET). Changes limited to D1–D5. v1.7 delivered on origin/dev as `334b8221`; scored 92 FAIL (`RADIO_NET-853`).
- **v1.7 Author / Agent:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Revision Attempt (v1.7):** Attempt **4/4** (final attempt per `COS_SCORE_NET-813_UNIFIED-COIN-DETAILS_v1.6_20261107.md` 89 FAIL and `RADIO_NET-849`)
- **Previous Delivery Commit:** `2dbb525e` (`docs(net-813): deliver Unified Coin Details View plan v1.6, review baton, and ACK RSI-CONTROLS`)
- **Review Target:** Grok Bot Chief of Staff (`GROKCOS`) per `RADIO_NET-849`
- **Delivery Commit:** `2dbb525e` (v1.6 delivery commit; prior attempts: v1.3 `5fbff9af`, v1.4 `ab2a02b3`, v1.5 `00957e85`; v1.7 delivered on branch `dev`)
- **Filing DTG:** Saturday, 7 November 2026, 21:30 ET (`2026-11-07 21:30:00 -05:00`)
