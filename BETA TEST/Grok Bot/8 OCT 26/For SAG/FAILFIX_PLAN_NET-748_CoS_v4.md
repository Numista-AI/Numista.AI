# FAILFIX PLAN — NET-748 — CoS v4 (overall attempt 11; CoS try 2 of 4)

Writer: GB CoS | Written: 2026-11-04 ET | Baton: NET-759 | PLAN ONLY: no code edits, commits, deploys or rules deploys
Decision: Eric, typed, 4 Nov 2026 9:25 AM ET: "one plan with only Argon's 3 fixes" (no 3-way split). Attempt 11 is past the 10-attempt limit and is allowed by that decision.
Route: Argon (RADIO NET) → GB CoS 95+ → SAG (CoS via API) → Eric's typed YES → EXECUTE.
**The rules deploy (Step 1b) REACHES LIVE and needs its own separate LIVE YES from Eric.** The p7-gate preview YES does not cover it. Firestore seeding also needs its own YES.
Scope: branch p7-v8.9 (tip 7c0eec8d) and the p7-gate preview channel only
Locks: main 9f04550a | Stripe OFF | live untouched
Base: FAILFIX_PLAN_NET-748_CoS_v3.md (unchanged except the 3 must-fixes below) + ARGON_REVIEW_NET-748_CoS_v3.md (92, MF-v3-1..MF-v3-3)
Verification method (v3, unchanged): line numbers read from the working tree at 7c0eec8d on 2026-11-03; GCS objects listed with read-only `gcloud storage ls`. v4 line refs for the MFs are Argon's, not re-read by CoS today.

## v4 change list (fix-only; line numbers are v3 lines)

| MF | v3 lines changed | Change |
|---|---|---|
| MF-v3-1 | 28, 35, 39, 45, 50 | Rules file is `numista_mobile/firestore.rules`; both match paths prefixed `/global_metadata/`; pre-check names the real `global_metadata` doc path (add_coins_hub.dart:2589-2601) |
| MF-v3-2 | new 3.5 after 171; 255; 256; new test 20 after 315 | `resolve()` infers `cleanSku` via `extractSku` when `sku` is empty; my_collection_screen 3467/4452 and coin_detail_screen 1052 call `resolveFromMap` before `fetchReferenceImages` |
| MF-v3-3 | 83, 85, 93 (removed), 98, 299 | `cond` joins Condition/Variety/Strike Type/Denomination instead of `??`; 26EA no longer requires a `proof` token (metal exclusion kept); test 3 updated to match |

Nothing else changed. Argon's side note that `inventory_gallery.dart` (v3 line 254) does not exist is NOT applied here (outside the 3 MFs); flagged for Argon.

---

## 0. What v3 changes vs AG v2 (summary)

| ID | v2 status | v3 action |
|---|---|---|
| F2-1 rules | Narrow named-doc rule was already correct | Kept. Added a pre-deploy local-vs-live diff and a separate step labeled REACHES LIVE |
| F2-2 state vars / styling | Correct (`_skuSearching`, `_skuSearchResult`, `withAlpha(40)`, icon `0xFF8B92B4`) | Kept unchanged |
| F2-3 Mayflower | Preserved | Kept byte-for-byte. Lines 353-369 are not touched; new blocks go after line 369 |
| F2-4 26SQRP path | Fixed in seed item 1 | Kept. Provenance table **rewritten**: v2's table cited 13 paths that do not exist (see section 6) |
| NEW-1 compile | v2 used `_kFallbackUsMintSkus` but never defined it | Defined in section 4.2 |
| NEW-2 compile | v2 wiring used `label:` / `matchKey:` | Real `CoinImageResult` fields are `sourceLabel` / `matchedKey`. Fixed in section 5 |
| NEW-3 assets | v2 cent/nickel/Polly paths **do not exist in GCS** | Replaced with listed objects (section 3.4) |
| NEW-4 seed | v2 seeded 26RA-26RF with no source | Dropped. The real gap is 11 docs (section 4.1) |

---

## 1. STEP 1 (local only): firestore.rules edit — F2-1

File: `numista_mobile/firestore.rules` (339 lines). The `isAuthenticated()` helper is at lines 8-10. The deny-all `match /{document=**}` is at lines 335-337. There's no existing rule for the dictionaries.

Insert directly **above line 335** (inside the `match /databases/{database}/documents` block):

```
    // NET-748: read-only SKU dictionary lookups for Add by SKU.
    // Named docs only. {skuId} is a single-segment variable, NOT recursive.
    match /global_metadata/usmint_sku_dictionary/skus/{skuId} {
      allow get: if isAuthenticated();
      allow list, write: if false;
    }
    match /global_metadata/littleton_sku_dictionary/skus/{skuId} {
      allow get: if isAuthenticated();
      allow list, write: if false;
    }
```

Pre-check (read-only): `_lookupSku` (add_coins_hub.dart:2572-2628) must read exactly those two paths (`collection('global_metadata').doc('usmint_sku_dictionary').collection('skus').doc(docId)` and the littleton equivalent; add_coins_hub.dart:2589-2601) with a `.doc(docId).get()` and never a `.get()` on the collection. If the code uses any other path, STOP and report. Do not widen the rule.

### STEP 1b — REACHES LIVE (project-wide) — needs Eric's separate typed YES
`firebase deploy --only firestore:rules` replaces the **whole** rules file for project studio-9101802118-8c9a8, live included. Preview channels share the same database and rules. Before asking for YES:
1. Fetch the currently deployed ruleset (Firebase console > Firestore > Rules, or `firebase firestore:rules` / the Rules API, read-only) and save it to `INBOX\LIVE_RULES_SNAPSHOT_<ts>.rules`.
2. `diff` that snapshot against the local `numista_mobile/firestore.rules`. The diff must show **only** the 10 lines above. If anything else differs (for example drift committed on another branch), STOP and report. Don't deploy.
3. Ask Eric for a typed YES that names this rules diff. The YES for the p7-gate hosting preview does NOT cover this step.
4. Rollback: redeploy the saved snapshot.

Until 1b is approved, Add by SKU on p7-gate uses the local fallback dictionary (section 4.2), so the preview can be tested without touching live.

---

## 2. STEP 2: add_coins_hub.dart — F2-2 (kept from v2, names verified)

Real state variables (lines 127-129): `_skuRetailer`, `bool _skuSearching`, `Map<String, dynamic>? _skuSearchResult`. Use only these names.
- `_lookupSku` (2572-2628). `docId` = sanitized, uppercased `rawSku`.
  - In the `!snap.exists` branch (2610-2616) **and** the `catch` (2622-2627), fall back to `_kFallbackUsMintSkus[docId]` (section 4.2). When it's found, `setState(() { _skuSearchResult = {...fallback, 'sku': docId}; _skuSearching = false; })`. Otherwise keep the existing not-found behavior.
- `_addSkuToCollection` (2630). In the `coinDoc` map (2638-2647) add `'sku': (_skuSearchResult?['sku'] ?? docId)` and `'mint_product_id'` with the same value. **MF-5: Add by SKU saves the SKU**, so `extractSku` finds it at the first key.
- Result card (2440-2445) is unchanged. It reads `name`/`description`, `year`, `program`/`program_series`, `item_type`. The fallback entries carry exactly those keys.
- `_buildCoinImage` styling is preserved: circular container, `withAlpha(40)`, icon color `0xFF8B92B4`. No `withOpacity` anywhere in new code.

---

## 3. STEP 3: canonical_mint_asset_service.dart (545 lines)

### 3.1 MF-2: year normalization ("2026.0")
Add a helper and use it at **all three** sites: line 100 (`extractSku`), line 154 (`resolveFromMap`) and line 184 (`resolve` `cleanYear`).
```dart
  static String _normYear(Object? y) {
    final s = (y ?? '').toString().trim();
    final m = RegExp(r'^(\d{4})(?:\.0+)?$').firstMatch(s);
    return m != null ? m.group(1)! : s;
  }
```
Line 100: `final year = _normYear(data['year'] ?? data['Year']);`. Line 154: same. Line 184: `final cleanYear = _normYear(year);`.

### 3.2 extractSku key list (lines 73-80)
Append `'retailer_item_num'` after `'retailer_item_no'`, and keep the other keys as they are. Also read `Condition`/`condition`, `Variety`/`variety`, `Strike Type`/`strike_type` and `Denomination`/`denomination` into `combined` (line 104) for the ASE rule, JOINED, not `??` (MF-v3-3: `??` stops at a non-null 'Ungraded' Condition and drops Variety/Strike Type):
```dart
    final cond = <Object?>[
      data['Condition'], data['condition'],
      data['Variety'], data['variety'],
      data['Strike Type'], data['strike_type'],
      data['Denomination'], data['denomination'],
    ].where((v) => v != null).map((v) => v.toString().toLowerCase()).join(' ');
    final combined = '$prog $theme $title $cond';
```

### 3.3 MF-2b: ASE rule (in extractSku, after `combined`)
```dart
    if (year == '2026' &&
        RegExp(r'\b(american|silver)\s+eagle\b').hasMatch(combined) &&
        !RegExp(r'\b(gold|platinum|palladium)\b').hasMatch(combined)) {
      return '26EA';
    }
```
26EA is the "American Silver Eagle Proof" (main.py:2190). MF-v3-3: the `proof` token requirement is removed, because an ungraded 2026-W Silver Eagle doc carries no "proof" token in any field. Gold/Platinum/Palladium eagles stay excluded.

### 3.4 2026 title block (starts at 314)
- **Dime (315-331): unchanged.**
- **MF-3: half block (332-352) gets a quarter guard.** Add before line 332:
```dart
      final isQuarter = RegExp(r'\b(25c|25¢|quarter)\b').hasMatch(cleanDenom) ||
          RegExp(r'\bquarter\b').hasMatch(cleanTitle);
      final isHalf = RegExp(r'\b(50c|50¢|half)\b').hasMatch(cleanDenom) ||
          RegExp(r'\b(kennedy|half dollar)\b').hasMatch(cleanTitle);
```
  Change line 336 from `cleanTitle.contains('independence')) {` to `(cleanTitle.contains('independence') && !isQuarter)) {`. The rest of the half block is unchanged. The Declaration of Independence **quarter** no longer maps to the Kennedy half.
- **F2-3: Mayflower block (353-369) is NOT TOUCHED.** Test "Row 10 D-mint Path" (test line 146) and "Row 10 Reference Resolution" (line 129) keep passing.
- **Insert after line 369** (still inside the 2026 `if`), in this order: quarters first, then $1, then cent and nickel. Every path below is an object listed in GCS today (section 6).
```dart
      // 2026 Semiquincentennial quarters (Declaration, Gettysburg, Revolutionary War, Constitution)
      const qtrs = <String, String>{
        'declaration of independence': 'declaration_of_independence',
        'gettysburg': 'gettysburg_address',
        'revolutionary war': 'revolutionary_war',
        'constitution': 'us_constitution',
      };
      for (final e in qtrs.entries) {
        if (cleanTitle.contains(e.key) && (isQuarter || !isHalf)) {
          final effMint = (cleanMint.isEmpty || cleanMint == 'P') ? 'P' : cleanMint;
          return CanonicalMintAssetPair(
            sku: '2026-QTR-${e.value.toUpperCase()}-$effMint',
            obverseUrl: '$_base/2026_series/2026_quarter_dollar_${e.value}_obverse.jpg',
            reverseUrl: '$_base/2026_series/2026_quarter_dollar_${e.value}_reverse.jpg',
            isGenuine2026: true,
          );
        }
      }
      // 2026 Native American $1 (Polly Cooper)
      if (cleanTitle.contains('polly cooper') ||
          (RegExp(r'\bnative american\b').hasMatch(cleanTitle) &&
              (cleanDenom.contains('1') || cleanTitle.contains('dollar')))) {
        return const CanonicalMintAssetPair(
          sku: '2026-NATIVE-POLLY',
          obverseUrl: '$_base/2026_series/2026_native_american_dollar_polly_cooper_obverse.jpg',
          reverseUrl: '$_base/2026_series/2026_native_american_dollar_polly_cooper_reverse.jpg',
          isGenuine2026: true,
        );
      }
      // MF-1: cent and nickel, whole word or denomination field only. NEVER substring 'cent'.
      final isCent = RegExp(r'\b(1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) ||
          RegExp(r'\b(lincoln cent|one cent|penny)\b').hasMatch(cleanTitle);
      final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
          RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
      if (isCent && !isQuarter && !isHalf) {
        final effMint = cleanMint == 'D' ? 'D' : 'P';
        return CanonicalMintAssetPair(
          sku: '2026-CENT-$effMint',
          obverseUrl: effMint == 'D'
              ? '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Penny-Obverse-Unc-D.jpg'
              : '$_base/bulk_programs/penny/SemiQ-Penny-Obverse-Unc-P.jpg',
          reverseUrl: '$_base/bulk_programs/penny/SemiQ-Penny-Reverse-Unc.jpg',
          isGenuine2026: true,
        );
      }
      if (isNickel && !isQuarter && !isHalf) {
        final effMint = cleanMint == 'D' ? 'D' : 'P';
        return CanonicalMintAssetPair(
          sku: '2026-NICKEL-$effMint',
          obverseUrl: '$_base/bulk_programs/nickel/SemiQ-Nickel-Obverse-Unc-$effMint.jpg',
          reverseUrl: '$_base/bulk_programs/nickel/SemiQ-Nickel-Reverse-Unc.jpg',
          isGenuine2026: true,
        );
      }
```
Notes:
- Bare "lincoln" is **not** a cent trigger, because the Gettysburg quarter says "Lincoln". Bare "cent" in the **title** is not a trigger either, only in the denomination field, as a whole word. `\bcent\b` cannot match inside "semiquincentennial".
- Implementers must confirm that the `CanonicalMintAssetPair` constructor (line 11) has defaults for omitted optional fields (`isSet`, `isRepresentativePreview`, fallbacks). If any is `required`, pass the same values the dime block (315-331) passes. Don't add new fields.
- The quarter loop `sku` strings are synthetic resolver keys like the existing `2026-MAYFLOWER-P`. They aren't Mint SKUs and aren't written to Firestore.

### 3.5 MF-v3-2: `resolve()` infers the SKU when none is passed (line 182)
`resolve()` never calls `extractSku()`, so a call without `sku` skips `switch (cleanSku)` (196-311) and returns null for 2026 Morgan (26XE/26XF), Peace (26XL/26XH), ASE (26EA), 26SQRP and all sets. Replace line 182 (place it after `cleanYear`/`cleanTitle`/`cleanDenom`/`cleanMint` are computed):
```dart
    final rawSku = (sku ?? '').trim().toUpperCase();
    final cleanSku = rawSku.isNotEmpty
        ? rawSku
        : extractSku(<String, dynamic>{
            'year': cleanYear,
            'title': cleanTitle,
            'denomination': cleanDenom,
            'mint_mark': cleanMint,
          });
```
Callers that hold the full doc call `resolveFromMap(...)` first (section 5.2), so Condition, Variety, Strike Type, Retailer Item No. and sku are kept.

---

## 4. STEP 4: SKU dictionary seed data — MF-4

### 4.1 Gap (11 docs, sourced)
`_knownSkus` (lines 57-70) has 12 SKUs. 26RJ already has a dictionary doc, so 11 docs are missing. Sources: `numista_backend/main.py` 2189-2200 and 2233-2237, and the service switch at 196-311. **26RA-26RF are dropped**, because no source exists in the repo or the backend.

| SKU | Name (source) | Image used by the service (switch, verified in GCS) |
|---|---|---|
| 26EA | American Silver Eagle Proof (main.py:2190) | us_mint_official/2026_products/26EA_image_1.jpg / _image_2.jpg |
| 26XE | Morgan Dollar Enhanced Unc (main.py:2189-2200) | 26XE_image_2.jpg / 26XE_image_3.jpg |
| 26XL | Peace Dollar Reverse Proof (main.py) | 26XL_image_3.jpg / 26XL_image_2.jpg |
| 26XH | Peace Dollar (per switch comment) | 26XH_image_2.jpg / 26XH_image_3.jpg |
| 26XF | Morgan Dollar Proof (per switch) | 26XF_image_1.jpg / 26XF_image_2.jpg |
| 26GC | American Innovation $1 Proof Set (per switch) | 26GC_image_1.jpg / 26gc_b.webp |
| 26SQRP | "2026 Semiquincentennial President Donald J. Trump $1 Coin 25-Coin Roll", Presidential $1 Coins, $61.00 (main.py:2200) | MASTER_SEMIQDJT_image_1.jpg / 26sqrp_b.webp, fallback _image_2.jpg |
| 26RG | Clad Proof Set (per switch) | 26RG_image_1.jpg / 26rg_b.webp |
| 23RG | 2023 Clad Proof Set (per switch) | **reuses 26RG_image_1.jpg / 26rg_b.webp (representative preview)** |
| 26RH | Silver Proof Set (per switch) | 26RH_image_1.jpg / 26RH_image_2.jpg |
| 23RH | 2023 Silver Proof Set (per switch) | 2023_series composites (as coded) |

The implementer copies the exact `name`, `program_series`, `item_type`, `denomination` and `year` strings **from main.py and the switch comments**, and does not paraphrase. When a field has no source, leave it out of the map. Don't invent it.

### 4.2 `_kFallbackUsMintSkus` (NEW-1: must be defined; v2 referenced it without defining it)
Top-level in add_coins_hub.dart, above the State class:
```dart
// NET-748: local mirror of usmint_sku_dictionary/skus/* for preview, when the doc
// is missing or rules deny the read. Values copied verbatim from numista_backend/main.py.
const Map<String, Map<String, dynamic>> _kFallbackUsMintSkus = {
  '26SQRP': {
    'sku': '26SQRP',
    'name': '2026 Semiquincentennial President Donald J. Trump \$1 Coin 25-Coin Roll',
    'program_series': 'Presidential \$1 Coins',
    'year': '2026',
    'item_type': 'roll',
  },
  // ... one entry per SKU in 4.1, keys limited to: sku, name, description, year,
  // program, program_series, item_type, denomination, mint_mark
};
```
`item_type` values must use the same vocabulary `_addSkuToCollection` already branches on (set vs coin). The implementer greps the existing branch condition and reuses its literal. The `'roll'` above is a placeholder only if that literal is not already in use. Check this before writing the map.
Firestore seeding (writing the 11 docs) is a **live data write** and is out of scope for this plan. It needs its own YES.

---

## 5. STEP 5: image wiring on every coin-image screen — MF-6 (NEW-2 fixed)

### 5.1 `coin_image_service.dart` `fetchReferenceImages` (line 489)
Add `import 'canonical_mint_asset_service.dart';` (today the only imports are cloud_firestore and foundation, so there's no cycle, because canonical imports nothing from it). At the top of `fetchReferenceImages`:
```dart
    final y = year.toString().replaceFirst(RegExp(r'\.0+$'), '');
    if (y == '2026' || y == '2023') {
      final pair = CanonicalMintAssetService.resolve(
        title: [series, subject].whereType<String>().join(' '),
        year: y,
        mintMark: mint,
        denomination: denomination,
      );
      if (pair != null) {
        return CoinImageResult(
          obverseUrl: pair.obverseUrl,
          reverseUrl: pair.reverseUrl,
          attribution: 'U.S. Mint',
          sourceLabel: 'Canonical Mint Asset',
          matchedKey: pair.sku,
        );
      }
    }
```
- Only `sourceLabel` / `matchedKey` are used, so there's no `label:` or `matchKey:`. Confirm that the `CoinImageResult` constructor (618-631) is named-param, and match its required set.
- Hook is limited to 2026/2023 so 1962 cents and ATB pre-2023 keep today's behavior.
- Callers covered automatically: coin_detail_screen.dart:1071, my_collection_screen.dart:3471, 4460, 6381, and set_contents_panel.dart:133 and 144.

### 5.2 Screens that bypass the service (must be wired explicitly)
In each one, add `import '../services/canonical_mint_asset_service.dart';` (adjust the relative path), then before using a stored URL:
```dart
final canon = CanonicalMintAssetService.resolveFromMap(data);  // returns null if user photos exist
final obv = canon?.obverseUrl ?? storedObverse;
```
- review_hub_screen.dart:2190-2209 (reads `image_url_obverse` directly)
- coin_set_viewer.dart (stored image fields)
- inventory_gallery.dart:131 and 347
- my_collection_screen.dart `_CollectionCardImage` (6345, build 6357). Run `resolveFromMap` **before** the stored `directUrl`, so broken stored reference URLs are replaced, and the MF-B guard still protects user/microscope photos. Inspector at 3448/3467 (MF-v3-2: call `CanonicalMintAssetService.resolveFromMap(data)` before falling back to `CoinImageService.fetchReferenceImages`; same at the Vault detail, line 4452): the `hasUserPhoto` check must use `CanonicalMintAssetService.hasUserUploadedPhotos(data)` instead of "any http URL".
- coin_detail_screen.dart around line 1030-1071: when there's no personal photo, prefer `resolveFromMap(data)` over a stored reference URL. MF-v3-2: at line 1052 (`_CoinImagePairState`) call `resolveFromMap({...widget.coin.toFirestore(), 'source': widget.coin.source, 'Personal Notes': widget.coin.personalNotes})` before `fetchReferenceImages`.

---

## 6. Provenance table (F2-4): every image path, checked with `gcloud storage ls` on 2026-11-03 11:20 ET

Base: `gs://numista-reference-library/reference_library/`

| Use | Object | Listed |
|---|---|---|
| 26SQRP obv / rev / fallback | us_mint_official/2026_products/MASTER_SEMIQDJT_image_1.jpg, 26sqrp_b.webp, MASTER_SEMIQDJT_image_2.jpg | yes |
| 26EA | us_mint_official/2026_products/26EA_image_1..3.jpg | yes |
| 26XE / 26XF / 26XH / 26XL | us_mint_official/2026_products/26X{E,F,H,L}_image_1..3.jpg | yes |
| 26RG / 23RG | us_mint_official/2026_products/26RG_image_1..3.jpg, 26rg_b.webp | yes |
| 26GC | us_mint_official/2026_products/26GC_image_1..3.jpg, 26gc_b.webp | yes |
| 26RH | us_mint_official/2026_products/26RH_image_1..3.jpg | yes |
| 26RJ | user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_a..f.jpg (+ us_mint_official/2026_products/26RJ_image_1..3.jpg) | yes |
| 23RH / 2023 composites | 2023_series/2023_american_women_quarters_five_honorees_composite.jpg, 2023_series/2023_american_innovation_four_states_composite.jpg | yes |
| Quarters x5 | 2026_series/2026_quarter_dollar_{mayflower_compact,declaration_of_independence,gettysburg_address,revolutionary_war,us_constitution}_{obverse,reverse}.jpg | yes |
| Polly Cooper $1 | 2026_series/2026_native_american_dollar_polly_cooper_{obverse,reverse}.jpg | yes |
| Cent | bulk_programs/penny/SemiQ-Penny-Obverse-Unc-P.jpg, bulk_programs/us_mint_manual/highres_scrape/SemiQ-Penny-Obverse-Unc-D.jpg, bulk_programs/penny/SemiQ-Penny-Reverse-Unc.jpg | yes |
| Nickel | bulk_programs/nickel/SemiQ-Nickel-Obverse-Unc-{P,D}.jpg, SemiQ-Nickel-Reverse-Unc.jpg | yes |
| Dime / Half (existing) | bulk_programs/dime/SemiQ-Dime-*, bulk_programs/half_dollar/SemiQ-Half-*, highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg, 2026_series/2026_half_dollar_enduring_liberty_*.jpg | yes |

**v2 paths that DO NOT EXIST (each one returned "matched no objects", so don't use them):**
- 2026_series/2026_one_cent_*
- 2026_series/2026_five_cent_*
- 2026_series/*eagle*
- 2026_series/*oneida*. v2's Polly reverse `2026_american_innovation_oneida_indian_nation_reverse.jpg` is missing, and the Polly obverse was an American Innovation image, which was wrong.
- v2's table paths: 2026_series/2026_american_eagle_silver_*, 2026_morgan_dollar_*, 2026_peace_dollar_*, 26rj_a.webp, 26gc_a.webp, 26rg_a.webp, 26rh_a/b.webp and 2023_series/23rg_*/23rh_* weren't seen in the listings and **don't match the code's switch**. They were dropped.

Gate check before the preview deploy: `curl -sI <https URL>` for every row must return 200 (public read). `gcloud ls` proves an object exists, not that it's publicly readable.

---

## 7. Tests

### 7.1 Existing (must stay green): 45 tests in test/services/canonical_mint_asset_service_test.dart
Counted today: 45 `test(` calls. These include Row 10 MF-B guard (line 110), "Row 10 Reference Resolution" Mayflower (129), "**Row 10 D-mint Path**" (146, fully qualified fallbackObverseUrl) and Row 11 2026-HALF-D (183). Rows 01-28 and Synthetic 01-14 are unchanged.

### 7.2 New tests (one or more per fix)
1. `_normYear`: '2026.0' and '2026' give '2026', both through `resolveFromMap` and `extractSku`.
2. ASE proof, 2026: title "American Silver Eagle", Condition "Proof", year 2026.0 → extractSku '26EA'.
3. MF-v3-3: ASE ungraded: year 2026, mint W, Program/Series "American Silver Eagle", Condition "Ungraded", no proof token → extractSku '26EA'. Condition "Ungraded" + Variety "Reverse Proof" → `combined` contains "reverse proof" (Variety not dropped).
4. Gold Eagle proof → not 26EA.
5. `retailer_item_num: '26SQRP'` → extractSku '26SQRP' → obverse MASTER_SEMIQDJT_image_1.jpg.
6. Declaration quarter: title "Declaration of Independence Quarter", denom "25c" → sku starts '2026-QTR-DECLARATION', NOT '2026-HALF'.
7. Half with "independence" and denom "50c" → still '2026-HALF-*' (regression).
8. **Semiquincentennial negative**: title "Semiquincentennial Quarter", denom "25c", no other keyword → NOT '2026-CENT-*'.
9. Semiquincentennial Dime → still dime (dime block unchanged).
10. Gettysburg quarter ("Lincoln ... Gettysburg Address") → '2026-QTR-GETTYSBURG_ADDRESS-*', NOT cent.
11. Cent P / D: denom "1c", mint D → highres_scrape/SemiQ-Penny-Obverse-Unc-D.jpg. Mint P → penny/SemiQ-Penny-Obverse-Unc-P.jpg.
12. Nickel P/D → bulk_programs/nickel paths.
13. Polly Cooper → 2026_native_american_dollar_polly_cooper_obverse.jpg.
14. Revolutionary War and Constitution quarters → their 2026_series paths.
15. Mayflower D after the new blocks are inserted → identical to test line 146 (F2-3 guard).
16. User-photo doc (MF-B) with a 2026 cent title → resolveFromMap null.
17. Widget/unit: `_kFallbackUsMintSkus` has exactly the 11 SKUs in 4.1, and each entry has `sku` and `name`.
18. `_addSkuToCollection` coinDoc includes `sku` and `mint_product_id` (fake Firestore).
19. CoinImageService.fetchReferenceImages(year: 2026, series: 'Mayflower', mint: 'D') returns sourceLabel 'Canonical Mint Asset', and year 1962 bypasses the hook.
20. MF-v3-2: `resolve(title: 'Morgan Dollar Enhanced Uncirculated', year: '2026')` with no sku → non-null via the inferred SKU; same for a Peace, ASE, 26SQRP and a set title. Assert non-null. If `extractSku` cannot infer a SKU from title/year alone for any case, STOP and report; do not add new title rules (out of scope).

Gate: `flutter analyze` 0 errors, all tests (45 + new) pass, then the p7-gate preview deploy only (`firebase hosting:channel:deploy p7-gate`). It must not be `--only hosting` live and must not be rules.

---

## 8. Execution order and stops
1. Steps 2-5 code, locally on p7-v8.9. Analyze and run tests. Commit to p7-v8.9 only (main 9f04550a stays locked).
2. Curl gate (section 6), then the p7-gate preview deploy. Eric FT checks it at https://numista-vault--p7-gate-8avtpz22.web.app.
3. Step 1b rules: REACHES LIVE (project-wide). Needs Eric's separate typed YES plus the snapshot diff.
4. Firestore seeding of the 11 docs: live data write, needs its own YES, out of scope.
Stripe stays OFF. Nothing is promoted to live.

## 9. Unverified / flagged
- Public HTTP 200 for each object hasn't been checked. Only `gcloud storage ls` existence was (curl gate in section 6).
- `CanonicalMintAssetPair` and `CoinImageResult` constructors: the required versus optional params have to be confirmed before compiling. The plan only uses field names that were read in the source.
- Morgan Reverse Proof has no SKU in `_knownSkus` and maps nowhere new. It's left as is and flagged.
- 23RG uses 26RG imagery (representative preview), the same as today.
- The `item_type` literal for rolls has to be taken from the existing `_addSkuToCollection` branch.
- The exact names for 26XH/26XF/26GC/26RG/26RH/23RG/23RH have to be copied from main.py and switch comments, and weren't retyped here.
- The live rules snapshot hasn't been fetched yet. That happens in Step 1b.