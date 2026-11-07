# GB CoS score: NET-816 Catalog v1.11

**58/100: FAIL.** A pass needs 95+. The plan is not ready for SAG pass, Eric's YES or execution.
Reviewed 7 Nov 2026, about 2:11–2:20 PM EST (America/New_York).

## Scope and method
This was a read-only document review. Evidence came from targeted `git show`, `git grep` and ancestry checks, SHA256, and a read-only parse of the bundled `catalog_public_v1.json` at the dev pin on EDS_Laptop. I did not check out code, run tests, build, deploy, access Firestore, message Eric or write live data. Compile and runtime outcomes are inferred from pinned source types only; nothing was executed.

Plan: `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.11.md` (894 lines). On-disk SHA256 is **F4F5E445…8B8A** in all 6 locations (`docs/`, `BATONS/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`, `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`), which are identical. The baton's claimed **4260A171…E71C** equals the LF-normalized content (the files on disk are CRLF). Content integrity ✓. In future, state which normalization the hash covers.
Pins verified: dev **b0b058087f1492244a0c0b769e126b38ac1ba06c**, p7 **4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235**, and origin/main **9f04550a** (lock intact). Plan commit **98a70c87** (authored 2:08:50 PM EST) is on `origin/p7-v8.9` only and is **not an ancestor of origin/dev b15fdda1**.

## Headline
v1.11 is a real improvement: the retail retraction is honest, the bucket is real, the deletions are complete, `MeltValueService` is reused and the package name is right. Pin checks still disprove several "closed" claims, and four new defects would ship wrong data or break compilation:
- **Reusing `parseFaceValue` gives wrong face values on 103 of 3,202 catalog entries.** I ran the pinned parser logic (`melt_value_service.dart:53–99`) over the real `denomination` strings. Results: `'Half dime'` (35 entries) returns **$0.10** because `dime` (`:80`) is checked before `half dime` (`:81`). `'3 cents'` (9) returns **$0.01**. Every `'N Dollars'` note or coin (`'10 Dollars'`, `'20 Dollars'`, `'100 Dollars'`, `'1,000 Dollars'`, `'10,000 Dollars'`, `'2 1/2 Dollars'` and so on, 58 entries) returns **$1.00** via the `dollar` branch (`:87`), and `'$1000'` returns **$100**. That is wrong data in a "Smithsonian-level" catalog. Section 9.A tests only clean tokens.
- **The Greysheet patch adds three runtime errors and keeps the silent `[]`.** `_serve_from_cache(..., series=series)` fails because the real signature (`:347–349`) is `(denomination_norm, year)`, so it raises TypeError. `_read_errors_cache_keyed` does not exist (the real helper is `_read_errors_cache`, `:353`), so it raises AttributeError. `e.series` fails because the `GsErrorEntry` dataclass (`:79–84`) has no `series` field, so it raises AttributeError. The keyed cache is never written, since `_fetch_and_cache` (`:344`) writes the unkeyed key. `coin_type` is accepted and ignored. The route still has `except Exception … return []` (`greysheet_error_routes.py:79–82`), yet the plan says that no longer swallows errors, and the route is not patched.
- **Standalone Ask Morgan detection is inverted.** The standalone catalog is `runApp(MaterialApp(home: CatalogBrowseScreen(...)))` (`main.dart:166–178`). Flutter names the `home` route `'/'`, so `ModalRoute.of(context)?.settings.name == null` is **false**. The code then falls through to `pushNamed('/?route=AiChatScreen')` on a MaterialApp with no routes, which throws. That is the exact failure this must-fix was meant to remove.
- **Card patch regresses the card-level type-photo label.** Pinned `_CatalogCard` `1142–1149` renders `'type photo (date may differ)'` when `isTypeImage`. The v1.11 "verbatim" card build computes `isTypeImage` but never uses it, so the label disappears, and the title and metadata styling also change. Imports `1–4` gain no `melt_value_service.dart`.

## GEMINI38_REVIEW: pinned-code evidence for each critical claim
**G1 Retail (MF1): mostly closed.** I parsed `catalog_public_v1.json` (3,202): 0 `cpg_retail` / `retail` / `face_value` keys ✓, and `nac_code` is on 3,202/3,202 ✓. The 3,120/82 counts were retracted ✓, and the amber chip was added. Open: the 103 face-value mis-parses above. `'Face Value N/A'` plus "Value pending AI estimate" shows on all 56 medals, with no AI-estimate pipeline defined. The contrast of `#856404` on `#FFF3CD` is **4.96:1**, not the claimed 5.1:1 (still AA for normal text).

**G2 Images (MF2): partially closed.** Real bucket: `firebase_options.dart` `storageBucket: 'studio-9101802118-8c9a8.firebasestorage.app'` ✓. Fabricated buckets dropped ✓, and there is no `*.web.app` / `*.firebasestorage.app` wildcard ✓. Self-host runs before the guard ✓, and the laptop + GCS backup is noted ✓. Modal `931–935` label preserved verbatim ✓ (pin `931: if (isTypeImage)` … `933: 'Representative photo — date may differ'`). Open items:
- (a) The card label regression above.
- (b) **CSP is not reconciled, despite the section title.** `numista_mobile/firebase.json:284` has `img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app`. It does not include `firebasestorage.googleapis.com`, the `studio-…firebasestorage.app` host, or `storage.numista.ai` / `cdn.numista.ai`. No CSP diff is given.
- (c) There is no bucket CORS config (needed for CanvasKit fetch) and no public-read rule, token or `alt=media` handling for `catalog/v1/`, so the rewritten URLs can still fail to render.
- (d) `storage.numista.ai` / `cdn.numista.ai` are allowlisted "if provisioned", meaning hosts we don't own are admitted. That is the same class of finding as NET-817 MF-I1.
- (e) Uploading 167 objects to the production bucket has no YES gate of its own. Gate 4 covers Firestore only.
- (f) The manifest does not keep per-image license or attribution for Wikimedia CC-BY(-SA) sources.

**G3 Known errors (MF3): partially closed.** `coin_model.dart:6/9/11/13` are non-nullable `String` and `:81–90` default to `''`. The matcher uses `int.tryParse(coin.year.trim())` and `isEmpty` ✓. The `MintError` additive fields and the `fromFirestore` patch match `mint_error.dart:150–177` exactly, with additive lines added ✓. Open items:
- (a) The §4.C caller rewrite is incompatible. The real `_fetchLibraryErrors` (`coin_detail_screen.dart:3526`) returns `Future<List<MintError>>`, consumed by `Future.wait` → `results[1] as List<MintError>` (`:3507–3514`). The plan makes it `Future<void>` with `setState(_libraryErrors/_loadingErrors)`, fields that don't exist. That is a compile error, and the cast breaks. Apply `errorMatchesCoin` inside the existing return (or in `_merge`) instead.
- (b) It cites `int.tryParse` at line **3480**; the real line is **3505**.
- (c) The Greysheet runtime errors described above.

**G4 Navigation (MF4): partially closed.** The real `_showItemDetailModal` is at `810` ✓, `?item=` matches `main.dart:163–164` ✓, and the 71–82 quote now uses the real identifiers ✓. Open items:
- (a) The "verbatim" quote runs to about line 99, not 82, and changes `89: 'We don\'t have…'` to `'We don't have…'`, which is a Dart syntax error if pasted.
- (b) `web_meta_web.dart` (13 lines) exports only `injectNoIndexMeta()`. There is no pushState or popstate helper, and `_initWebHistoryListener` / `_removeWebHistoryListener` are defined nowhere in the plan.
- (c) `import 'web_meta.dart' if (dart.library.js_interop) 'web_meta_web.dart'` doubles a conditional that `web_meta.dart:2–3` already performs. Import `web_meta.dart` and add the helpers to both stub and web files.
- (d) `initState` is at **40–47**, not 50–55 (that is `dispose`).

**G5 Ask Morgan (MF5): open.**
- (a) Standalone detection is inverted, as described above.
- (b) The plan says it patches `main.dart:175–177`, but those lines are `ThemeData` inside the catalog `runApp`. The real route parse is `207–209`.
- (c) `WelcomeScreen` has only `static String? pendingRoute` (`welcome_screen.dart:17`). `pendingPrompt` must be declared, and the consumer is `BaseLayout:203–209`, not WelcomeScreen, and it is not patched.
- (d) `AiChatScreen` (`ai_chat_screen.dart:31`) has no initial-prompt parameter, so the prompt has nowhere to go.
- (e) The guest "Return to Catalog" link and return-to-**item** (`?item=`) are only asserted.

**G6 Deletions (MF6): closed ✓.** On dev, `3454: _fetchInspectorSimilar(data);`, `5205: Future<void> _fetchInspectorSimilar(…)` through `5231: }`. On p7, `3454` call site and `5548: // --- Similar Coins widget for the inspector` (span 5548–5685). eBay is preserved at `4408–4410: void _onSearchEbay(`. NET-816 is the single owner.

**G7 Bundle C (MF7): partially closed.** Extends the real `MeltValueService` (`:9`, `compute` `:103–111`) ✓. The alloy list is correct: 1943 steel, 1944–46 brass, 1962–82, post-1982 zinc core with copper plating, war nickel, 0.07234/0.18084/0.36169, 40% Kennedy, 1992–2018 90% and 2019+ .999 proofs ✓. History lines `865–873` are correctly located ✓. Legislation is grounded: `:47 'congress_url'`, `:62 NUMISMATIC_LAWS`, `:26` key literal → Secret Manager ✓ (key not reproduced). Open items:
- (a) **`SpotPriceService` does not exist**, and neither does a `system_config/spot_prices` path. The real source is backend `/api/spot_prices` (`valuation_routes.py:13`), backed by Firestore `config/spot_prices`, with fallback **Gold 3100 / Silver 35 / Pt 1000 / Pd 1000** (`:63`), not the $2,700/$32/$1,000 the plan states.
- (b) Claiming `composition` / `weight_g` are "populated on all 3,202 entries" is false. Non-empty counts are **composition 1,871/3,202** and **weight_g 5/3,202**.
- (c) **`TextSanitizer.cleanProse` does not exist** (`text_sanitizer.dart` has only `fixMojibake` and `_repairKnownSequences`). The §6.C patch also declares `final sanitizedHistory` inside a collection-`if` spread, which is invalid Dart.
- (d) The 1796–97 manifest codes `nac_coin_us_1796_quarter_draped_bust` / `…half_draped_bust` (and the test's `nac_coin_us_1909_lincoln_cent_vdb`) are fabricated. Real codes look like `NAC1.CN.US.1C.LINCOLNCEN.1909.XX.WHEAT.C`, and the bundled catalog has **no** 1796 25C/50C entry. `mint_plates_manifest.json` has no contents.
- (e) The Congress.gov key is already committed in git history, so moving it to Secret Manager is not enough. The plan needs a **rotation** step (revoke the old key, issue a new one) plus a check that it is never bundled.

**G8 Tests (MF8): partially closed.** `pubspec.yaml: name: numista_ai` ✓, a new file is used and the 91-line `catalog_browse_test.dart` is preserved ✓, and fixtures use a String year ✓. Open: `MintError(id:, name:, years:, denominations:, series:)` omits **14 required** constructor params (`mint_error.dart:100–118`: shortName, category, subcategory, mintMarks, designation, estValueLow/High, rarity, description, howToSpot, datasets, images, relatedCoinIds, sources), so this is a compile error. There are no tests for the real failing denominations, popstate/history, Ask Morgan standalone routing, Greysheet series filter, sanitizer or the card type-photo label.

**G9 Ops (MF9): partially closed.**
- (a) **DTG is still future-stamped.** The baton, RADIO_ENTRY and plan say 15:15 ET, but the commit was authored 14:08:50 EST and the files have mtime 2:08 PM. The closeout claims "DTG stamped accurately", which is false. AG's WHOSE_TURN "2:15 PM" ACK entry is also future-dated.
- (b) `git cherry-pick -n <sha> -- <paths>` is invalid, because cherry-pick takes no pathspec. Use `git checkout <sha> -- <paths>` (or `git restore --source=<sha>`) on a temp worktree from origin/dev, then commit and push without force. 98a70c87 is still not on origin/dev.
- (c) The gates contradict each other. §8 calls them Gate 1 Code Build / Gate 2 Preview Deploy / **Gate 3 Production Live (13 Nov)**, while §9.C calls them Gate 1 Plan / 2 Code / 3 Preview / 4 Firestore / **Gate 5 Production "Strictly PROHIBITED"**. Production for Eric's 13 Nov catalog go-live must be a separate Eric-YES gate, not "prohibited", and the numbering must be the same everywhere.
- (d) There is no gate for the production-bucket upload or a CSP/hosting-header change.
- (e) NET-818 is "restored" only as a one-line owner note ✓.

## Numbered must-fix closeout (v1.11 vs CoS-48)
1. Retail: **mostly closed** (face-value parser defects open)
2. Images: **partially closed** (card label, CSP, CORS/read, unowned CDN hosts, upload gate, attribution)
3. Known errors: **partially closed** (caller signature, Greysheet runtime errors, route swallow)
4. Navigation: **partially closed** (no history helpers, quote escape, lifecycle lines)
5. Ask Morgan: **open** (inverted detection, wrong lines, no prompt sink)
6. Deletions: **closed ✓**
7. Bundle C: **partially closed** (SpotPriceService invented, coverage claim false, cleanProse missing or invalid, fabricated nac codes, key rotation)
8. Tests: **partially closed** (MintError fixtures don't compile; coverage gaps)
9. Ops: **partially closed** (future DTG, invalid cherry-pick, gate contradictions)

## Rubric
|Dimension|Score|
|---|---:|
|Standing locks / production gates|9/15|
|Retail implementation / real provenance|11/15|
|Images / CSP / ownership|8/15|
|Known-error model / complete matching|7/15|
|Google/Kaggle structural removal|10/10|
|Navigation and lifecycle|4/10|
|Scope additions / dated launch / integration|7/15|
|Executable verification|2/5|
|**Total**|**58/100 FAIL**|

## Handoff integrity
Mirrors are identical ✓, and the hash is OK after LF normalization ✓. The `1 NUMISTA.AI/` mailbox is local-only (gitignored). The plan commit is **not on origin/dev**. CoS pushes this score package to origin/dev as docs only.

I found no AJ PII in the plan or the code I selected. I did not copy the Congress.gov key into this file. No authority is granted. Next steps: return Catalog **v1.12** closing every item in `RADIO_NET-831`, then independent SAG 95+, then Eric's typed YES. All gates stay separate.
