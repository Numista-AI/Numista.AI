# GB CoS score — NET-817 Cards v1.7 + Images v1.7

**Combined: 60/100 — FAIL.** Equal-weight plan scores: **Cards 67/100 FAIL; Images 53/100 FAIL**. Each plan must reach 95+; averaging never bypasses a failed plan.
Reviewed 7 Nov 2026, approximately 2:00–2:10 PM EST (America/New_York). Baton `BATON_NET-817_GROKCOS_REVIEW_FAILFIX_PLAN_780b-780c_v1.7_20261107-1530.md` was filed ~1:59 PM ET but stamped 3:30 PM ET (future DTG — stamp delivery time accurately).

## Scope and evidence
Plans: `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.7.md` (C, SHA256 `7C7C6786D272…`) and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.7.md` (I, SHA256 `A70EE43B64B8…`). Mirrors in docs / BATONS / RADIO NET / INBOX / OUTBOX / `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX` all hash-match. **Accepted.**
Prior: `COS_SCORE_NET-817_CARDS_IMAGES_v1.6_20261107.md` (76; Cards 84 / Images 68).

Repository on EDS_Laptop: `C:\Users\ericd\Documents\MyVertexProject`, after `git fetch`. All citations are **p7 @4d17ca5e** via `git show` / `git grep` (not working tree). Verified: `origin/main` **9f04550a**; `origin/p7-v8.9` tip **4be8eba4** (no `numista_mobile/lib` or `numista_mobile/test` diff vs 4d17ca5e); `origin/dev` **4f0a6842** before this push. Read-only audit; proposed snippets were inspected, not compiled or applied.

## GEMINI38_REVIEW — real code from the pin (Tier-1 grounding)

**Package name** — `numista_mobile/pubspec.yaml:1` → `name: numista_ai`. Existing test imports `package:numista_ai/services/canonical_mint_asset_service.dart`.

**Images API** — `coin_image_service.dart:490–496` `static Future<CoinImageResult> fetchReferenceImages({required String year, String? mint, String? denomination, String? series, String? subject})`; `:637–655` `class CoinImageResult { final String? obverseUrl; final String? reverseUrl; … const CoinImageResult({...}); bool get hasObverse/hasReverse/hasAny }`. Header `:6–8`: reference images come from `gs://us_mint_coin_images` (Tier 1) and `gs://numista-reference-library` (Tier 2–5). **Plan v1.7 API quotes are correct.**

**Existing widget** — `my_collection_screen.dart:6356` `class _CollectionCardImage extends StatelessWidget` through `:6479 }`. Steal-guard `:6409–6417`:
```dart
// MF-V3-3: When subject is known and reverse is null (steal-guard ...
final refUrl = (ref?.reverseUrl?.isNotEmpty == true)
    ? ref!.reverseUrl!
    : (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)
        ? ref!.obverseUrl!
        : '';
```
Canonical pair also prefers reverse: `:6371 final canonUrl = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;`. User URLs read via `_F.imageObverse = 'image_url_obverse'` / `_F.imageReverse = 'image_url_reverse'` (`:76–77`).

**Real storage / host forms** — `firebase_options.dart:55,64,73` `storageBucket: 'studio-9101802118-8c9a8.firebasestorage.app'`; `.firebaserc` default `studio-9101802118-8c9a8`. User uploads: `my_collection_screen.dart:5015 final url = await snap.ref.getDownloadURL();` → `:5023–5024 .update({ field: url, ...` and `:5487–5493` `FirebaseStorage.instance.ref('users/$userEmail/coins/...')…getDownloadURL()` (Firebase download URLs are `https://firebasestorage.googleapis.com/v0/b/<bucket>/o/...`). Upload guard `canonical_mint_asset_service.dart:37–38` names `studio-9101802118-8c9a8-uploads` and `numista-uploads-studio-` (test fixtures use `numista-uploads-studio-9101802118-8c9a8`). `ref_image_widget.dart:57` `https://storage.googleapis.com/us_mint_coin_images/$path`. `canonical_mint_asset_service.dart:53` `numista-reference-library`. **`numista-vault.firebasestorage.app`, `numista-ai-images`, `numista-catalog-assets` appear nowhere in `numista_mobile` or `numista_backend` on the pin**; `numista-vault.firebaseapp.com` appears only as a backend CORS origin (`numista_backend/main.py:53`).

**CSP** — `numista_mobile/firebase.json:276` real `img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app` (plan §2.B misquotes it, omitting gstatic/run.app). No `*.firebasestorage.app` and no `*.web.app` in `img-src`.

**Cards valuation lines** — real `my_collection_screen.dart:3017–3023`:
```dart
3017: final valCpg = _parseNumber(m['cpgRetail']);
3018: final finalVal = valCpg;
3020: final fmt = intl.NumberFormat.currency(symbol: '\$');
3021: final valueText = finalVal > 0
3022:     ? fmt.format(finalVal)
3023:     : (m[_F.aiValue]?.toString() ?? '—');
```
Line 3015 is the tail of `displayTitle` (`: (themeStartsYear ? label : '$yearMint $label').trim();`). The pending-chip row is real **3167–3192** (`Row(` … `),`), with `:3170 if (valueText == '—' || m['enrichment_status'] == 'pending')`. Card surface `:3028–3032` = `_surface` (`:211` dark `0xFF1E2937`, light `Colors.white`) or virtual-child `0xFF0D1520` / `0xFFF5F5F0`.

**Denomination matcher** — `canonical_mint_asset_service.dart:430–434` exactly as quoted by plan (`RegExp(r'\b(1c|1¢|one cent|cent|penny)\b')` / `RegExp(r'\b(5c|5¢|five cents?|nickel)\b')`). **Anchor correct.** `canonicalYear` does **not** exist on the pin (only `_normYear` `:72`, `extractSku` `:78`, `resolveFromMap` `:153`).

**Inspector / Kaggle span** — fields `:150–151`; call site **`:3454 _fetchInspectorSimilar(data);`**; UI call `:3820 _buildSimilarCoinsInspector(),`; loader `:5252–5278`; UI `:5549–5684`. Google button `:3531–3548`, handler `:4387–4406`, `_onSearchEbay` `:4410` (EPN affiliate doc comment `:4408–4409`). **Ranges correct; 3454 call site omitted by both plans.**

**Existing test file** — `numista_mobile/test/services/canonical_mint_asset_service_test.dart` exists on the pin (**749 lines**, 28 live-doc + 14 synthetic cases).

## CoS-76 must-fix closeout verification
| # | Claim | Verdict |
|---|---|---|
| 1 | Images real API | **Closed** for `fetchReferenceImages` / `CoinImageResult` / `const CoinImageResult()` timeout. But widget still won't compile as written (see new MF-I2). |
| 2 | Ownership helper vs real hosts | **Not closed — worse.** Relative paths now admitted, but allowlist rejects real user-photo download URLs and Tier-1 `us_mint_coin_images`, admits three fabricated buckets, and adds attacker-registrable wildcards. |
| 3 | Pump harness with injectable fetcher | **Partially closed.** Harness + counted fetcher is the right shape; tests won't compile (package name, private-class calls) and the claimed `_RequestKey` refresh test is absent. |
| 4 | Cards pricing suite + full valuation diff | **Not closed.** Test pumps a test-local copy (`CollectionCardValuationRow`) of the code, not `my_collection_screen.dart`; line anchors off; AI-value fallback silently dropped. |
| 5 | Denomination lookbehind in production | **Half closed.** Production patch at correct lines; test still asserts a local `RegExp` copy, two of its assertions fail, and the file path overwrites a 749-line suite. |
| 6 | Anchors / `_RequestKey` | **Mostly closed** (5252, StatelessWidget 6356–6479, aliases + canonicalYear). Missing 3454 call site; `_RequestKey` depends on Cards' new `canonicalYear` without stated apply order. |
| 7 | Gates | **Closed** (main 9f04550a, Stripe OFF, PLAN ONLY, alerts-only $20/mo, separate YES, US-only, 3 AM, backup gate, non-force revert, `_onSearchEbay` preserved). Kaggle ownership now contradictory (see MF-B1). |

## Numbered must-fixes for v1.8

### Both plans
**MF-B1. [Ownership + compile] Kaggle inspector removal: one owner, complete span.** Images MF-6 says "Single deletion owner for Google/Kaggle is NET-816" and then "NET-817 cleanly removes inspector loader (5252–5278) and fields (149–152)"; AG's ACK of NET-829 says Catalog v1.11 will also handle the `_fetchInspectorSimilar(data);` call site at 3454. Pick exactly one owner (recommend NET-816 for all Google + Kaggle deletions, NET-817 cites it as a dependency). Whichever plan owns it must delete **3454, 3820, 5252–5278, 5549–5684 (+ `_showRefImageDialog`), 150–151** together — deleting the loader while 3454 remains does not compile. `_onSearchEbay` @4410 with EPN affiliate tags stays.

**MF-B2. [Tests] Use `package:numista_ai/...`.** Every proposed test imports `package:numista_mobile/...`; pubspec `name: numista_ai`. None compile.

**MF-B3. [Hygiene] Accurate DTG** (filed ~1:59 PM, stamped 3:30 PM) and a declared apply order: Cards `canonicalYear` must land before Images `_RequestKey`.

### Images (780c)
**MF-I1. [Blocking; ownership] Ground the allowlist in real URL forms only — exact names, no wildcards.** Must ACCEPT: `https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/...` (what `getDownloadURL()` writes at `my_collection_screen.dart:5015/5489/5493`; today the plan marks every manually uploaded user photo `INVALID_USER_PHOTO`); `storage.googleapis.com/us_mint_coin_images/` (Tier-1 reference index; today every Tier-1 reference image becomes "Reference not found"); `storage.googleapis.com/numista-reference-library/`; `storage.googleapis.com/studio-9101802118-8c9a8-uploads/`; `storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/` (exact, not the open prefix `numista-uploads-studio-`); `storage.googleapis.com/studio-9101802118-8c9a8.firebasestorage.app/` if used. REMOVE fabricated `numista-vault.firebasestorage.app`, `numista-ai-images`, `numista-catalog-assets`. REMOVE `host.endsWith('.firebasestorage.app')` (lines 317–319 return true for any project's bucket) and `host.endsWith('.web.app')` (any Firebase Hosting site) — both attacker-registrable. Reject relative paths containing a backslash (`/\evil.com` is protocol-relative in browsers). Quote one real Firestore-style fixture per accepted form (no AJ data, no real user emails).

**MF-I2. [Blocking; compile] Place helpers where callers can reach them.** §3.1 `_CollectionCardImageState` calls bare `isOwnedStorageUrl(...)`; §3.2 declares it `static` inside an unnamed class; §6.2 calls `_CollectionCardImage.isOwnedStorageUrl(...)` from a test file (library-private class → compile error). `_RequestKey.fromData` calls bare `_extractUserPhoto` (does not exist on pin; plan shows it indented as a member). Make `isOwnedStorageUrl` a public top-level function (or in a small `lib/utils/owned_storage_url.dart`) and `_extractUserPhoto` top-level private, and test the same symbol.

**MF-I3. [Blocking; behavior regression] Restore the shipped display policy.** Plan picks `obverseUrl` first for both canon and reference and drops the MF-V3-3 steal-guard (`:6409–6417`) while the closeout claims "Applies subject steal-guard policy". Keep: reverse preferred; obverse only when `subject.isEmpty`. Also: a reverse-only user photo (`revUserUrl` set, `obvUserUrl` null) currently nulls the future and then renders "No image available" — render the reverse; apply fail-closed to either side. State whether losing the circular glow / `BoxFit.contain` (`:6443–6477`) is intentional (coins get cropped by `BoxFit.cover`).

**MF-I4. [CSP truth]** Quote `firebase.json:276` exactly and show every accepted host is reachable under real `img-src`/`connect-src`; drop hosts CSP would block.

**MF-I5. [Tests]** Add the claimed `_RequestKey` refresh test (pump, then `pumpWidget` with `Year` changed from '' to populated → fetcher count 2). Use real bucket fixtures (not `numista-vault.firebasestorage.app`). Add accepted tests for the getDownloadURL and `us_mint_coin_images` forms and rejected tests for `evil.firebasestorage.app`, `evil.web.app`, `storage.googleapis.com/numista-uploads-studio-evil/`. For the 1964 Half Dollar reference test, prove `resolveFromMap` returns null for that fixture or the `fetchCount == 1` assertion is unproven.

### Cards (780b)
**MF-C1. [Blocking; anchors] Correct valuation anchors.** Real lines are **3017–3023** and **3167–3192** (not 3015–3025 / 3170–3195). Literal range replacement at 3015 deletes the tail of `displayTitle`. Use the real lines or explicit search/replace blocks only.

**MF-C2. [Blocking; regression] Do not silently drop AI value / enrichment state.** Today a card with no `cpgRetail` shows `m[_F.aiValue]`; the plan replaces it with face value + "Value pending AI estimate" even when an AI estimate exists, and drops the `enrichment_status == 'pending'` branch. State Eric/B05N-8 precedence explicitly (CPG retail → AI value → face value + chip) or cite the decision that removes AI value from cards, and keep cards consistent with table columns `:534–538` / `:3338–3345`.

**MF-C3. [Face value correctness]** `_computeFaceValue` is order-dependent: "Half Dime" → 0.10, "Two Cents"/"Three Cents"/"Fifty Cents" → 0.01, "Three Cent Nickel" → 0.05; real pin denominations include `\$1` and `Set` → `"$0.00"` + chip. Reuse the existing parser `MeltValueService.parseFaceValue(String rawDenom, {int qty = 1})` (`melt_value_service.dart:53`, already used by `home_dashboard.dart:300`) instead of a new duplicate, and show "—" rather than "$0.00" when unknown.

**MF-C4. [Blocking; tests] Test production code, don't copy it.** `my_collection_card_pricing_test.dart` defines its own `CollectionCardValuationRow` and asserts that copy — tautological, same defect as v1.6 Images. Extract the valuation row into a real widget in `lib/` (used by `_buildCardGrid`) and pump that, or pump `MyCollectionScreen` with fakes.

**MF-C5. [Blocking; tests] Don't overwrite the 749-line canonical suite; fix failing assertions.** §6.2 is a full-file body at `test/services/canonical_mint_asset_service_test.dart`, which exists on the pin with 28 live-doc cases — append a new `group` or use a new file. The lookbehind test asserts a local `RegExp` copy again (call `CanonicalMintAssetService.resolve`/`resolveFromMap` with denominations instead), and `hasMatch('1¢')` / `hasMatch('5¢')` are **false** under Dart/JS semantics because `\b` after `¢` at end-of-string has no word boundary (verified: `"1¢" false`, `"5¢" false`). Fix the production pattern (e.g. `(?!\w)` instead of trailing `\b`) and the expected values. Note `"25 cent"` still matches cent.

**MF-C6. [Contrast truth]** #D4AF37 on #0D1520 is **8.72:1** (not 6.8), on dark `_surface` #1E2937 ≈7:1, but on light `_surface` white only **2.10:1** and #F5F5F0 **1.92:1** — fails WCAG AA in light theme. Use theme-aware chip text (darker gold/brown in light mode) and test both brightnesses against the real surface colors.

**MF-C7. [Anchor] `canonicalYear` is new** — give its insertion point in `CanonicalMintAssetService` and say it is additive (no `resolveFromMap` behavior change).

## Rubrics
|Cards dimension|Score|
|---|---:|
|Branch/rollback/standing locks|18/20|
|Canonical year / denomination correctness|21/30|
|Retail precedence and contrast proposal|10/20|
|Shared structural removal/integration|13/15|
|Behavioral tests/provenance proof|5/15|
|**Cards**|**67/100 FAIL**|

|Images dimension|Score|
|---|---:|
|Branch/rollback/standing locks|17/20|
|Complete applicable widget/future lifecycle|13/25|
|User-photo preservation and ownership/CSP|5/25|
|Network truth/operational safety|11/15|
|Real verification and shared removals|7/15|
|**Images**|**53/100 FAIL**|

Combined arithmetic: (67+53)/2 = **60/100 FAIL**. Images regressed on ownership because the v1.7 allowlist would hide real user photos and Tier-1 reference images on Thanksgiving traffic while admitting third-party hosts. Score is plan readiness, not proof of runtime safety. No AJ PII encountered; no secrets copied. No code, deployment, Firestore, deletion, main, or Stripe authority granted. Revised CoS 95+, then independent SAG 95+, then Eric typed YES; separate gates remain separate.
