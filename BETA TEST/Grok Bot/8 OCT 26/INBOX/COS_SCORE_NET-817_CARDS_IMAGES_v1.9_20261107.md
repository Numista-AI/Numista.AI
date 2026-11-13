# GB CoS score — NET-817 Cards v1.9 + Images v1.9

**Combined: 86/100 — FAIL.** Equal-weight plan scores: **Cards 95/100 PASS; Images 78/100 FAIL**. Each plan must reach 95+; averaging never bypasses a failed plan.
Reviewed 7 Nov 2026, approximately 3:50–3:55 PM EST (America/New_York). Baton `BATON_NET-817_GROKCOS_REVIEW_CARDS-IMAGES_v1.9_20261107-1542.md` (file mtime 3:42 PM ET, stamped 3:42 PM ET). Writer: AG CoS v5 `cfe23a7a`, attempt **1/4**.

## Scope and evidence
Plans: `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.9.md` and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.9.md` (delivery commit `2cddeda8` on origin/p7-v8.9). Prior: `COS_SCORE_NET-817_CARDS_IMAGES_v1.8_20261107.md` (73; Cards 70 / Images 76).

Repository on EDS_Laptop `C:\Users\ericd\Documents\MyVertexProject`. All citations checked at **p7 @4d17ca5e** via `git show` / `git ls-tree` (not the working tree, not plan quotes alone). Verified: `origin/main` **9f04550a** (unchanged); `git diff --stat 4d17ca5e HEAD -- numista_mobile/` empty (docs-only tip `2cddeda8`); Stripe OFF; PLAN ONLY. Live smoke ~3:55 PM ET: `https://numista.ai` 200, `main.dart.js` 200.

## GEMINI38_REVIEW — real code from the pin (Tier-1 grounding)

**Package** — `numista_mobile/pubspec.yaml:1` `name: numista_ai`. Plans import `package:numista_ai/...`. **Closed (preserved).**

**Card valuation (`my_collection_screen.dart`)** — Verified via `git show 4d17ca5e:...`:
```dart
// :72
static const aiValue          = 'AI Estimated Value';
// :3017-3023
final valCpg = _parseNumber(m['cpgRetail']);
final finalVal = valCpg;
final fmt = intl.NumberFormat.currency(symbol: '$');
final valueText = finalVal > 0
    ? fmt.format(finalVal)
    : (m[_F.aiValue]?.toString() ?? '—');
// :3170 shipped chip text
child: const Text('Valuation Pending', ...)
// :3345-3355 table AI column filters Pending/null/empty and formats ranges
```
`valueText` refs only at `:3021, :3170, :3182` — safe to remove when wiring `CollectionCardValuationRow`. Imports `:1–44` are relative; plan adds `import '../widgets/collection_card_valuation_row.dart';` after `:44`. **MF-B3' / MF-C1 / MF-C2' closed in plan text** (widget reads `'AI Estimated Value'` first; sentinel filter; intentional CPG>0 suppresses chip documented vs shipped `:3170`).

**Face-value parser** — `melt_value_service.dart:53+` at pin (verified):
```dart
else if (s.contains('dime') || s.contains('10c') || ...) { value = 0.10; }
else if (s.contains('half dime')) { value = 0.05; }   // AFTER dime — Half Dime → $0.10 BUG
else if (s.contains('nickel') || s.contains('5c') || ...) { value = 0.05; }
else if (s.contains('three cent') || ...) { value = 0.03; }  // AFTER nickel — Three Cent Nickel → $0.05 BUG
else if (s.contains('penny') || s.contains('cent') || ...) { value = 0.01; } // Five Cents → $0.01 BUG
```
`DenominationCanon` (`:4–9`): `'Cent'`, `'Five Cents'`, `'Dime'`, `'Quarter Dollar'`, `'Half Dollar'`, `'Dollar'`. Plan drops the false v1.8 ordering claim, patches order (`half dime` before `dime`, `three cent` before `nickel`, adds `five cent`/`ten cent`/`fifty cent`/`twenty-five cent`), AND `resolveFaceValue` exact-switches canon constants before `parseFaceValue`. Full table test present. **MF-C3' closed.**

**Denomination matcher** — pin `:431–434`:
```dart
final isCent = RegExp(r'\b(1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) || ...
final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) || ...
```
Plan replaces with lookbehind/`(?!\w)` form including `1 cents?`, neutral title `'2026 Coin'`, positive/negative guards. `canonicalYear` still absent at pin (only `_normYear`); additive after `:76` OK. **MF-C5' / MF-C7 closed in plan text.**

**Images widget** — pin `:6356–6417` (verified):
```dart
static String _cleanUrl(dynamic val) {
  if (val == null) return '';
  final s = val.toString().trim();
  if (s.isEmpty || s.startsWith('gs://') || !s.startsWith('http')) return '';
  return s;
}
final canon = CanonicalMintAssetService.resolveFromMap(data); // FIRST
// then direct user URL (rev preferred), then CoinImageService.fetchReferenceImages
```
Plan keeps **canonical → user → reference**, patches `hasUserUploadedPhotos` with `users%2f`, `extractUserPhoto` keeps URL-only semantics, same-State `ValueKey('card')` + `identical` refresh proof, `ref_image_widget` path `lib/widgets/common/ref_image_widget.dart:57` verified. **MF-I3' / MF-I6 / MF-I5' closed in plan text.** CSP `:276` img-src lacks `firebasestorage.googleapis.com` — additive patch still correct (**MF-I4 closed**).

**MF-I7 — NOT closed (blocking).** Plan claims verbatim quotes from:
- `numista_backend/scripts/reference_library/build_image_index.py` with `SOURCES`, `us_mint_direct`/`pcgs_coinfacts`/…, and `"public_url": f"{PUBLIC_URL_BASE}/{bucket}/{path}"`
- `build_currency_image_index.py` `BUCKET_NAME` / `CURRENCY_PREFIX = "reference_library/wikimedia_uscurrency/"`
- `promote_user_photos.py` `UPLOADS_BUCKET` / `REF_BUCKET` line 130
- Firestore collections `reference_images` / `currency_reference_images`
- `coin_image_service.dart:404`

**CoS `git show` / `git ls-tree` at `4d17ca5e`:**
- Those `scripts/reference_library/*` paths **do not exist**. Real paths: `numista_backend/_scripts/build_image_index.py`, `build_currency_image_index.py`, `promote_user_photos.py`.
- Real `build_image_index.py`: `FIRESTORE_COLLECTION = "coin_image_index"`, `PUBLIC_URL_BASE = "https://storage.googleapis.com"`, `SCAN_TARGETS` (not `SOURCES`); `public_url = f"{PUBLIC_URL_BASE}/{bucket}/{encoded_path}"`.
- Real `build_currency_image_index.py`: `REFERENCE_BUCKET = "numista-reference-library"`, `GCS_PREFIX = "reference_library/us_banknotes/"` (not `wikimedia_uscurrency`), `currency_image_index`.
- Real `promote_user_photos.py`: `BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"`, `PUBLIC_BASE`, returns `f"{PUBLIC_BASE}/{BUCKET_NAME}/{dest_path}"` (no `UPLOADS_BUCKET`/`REF_BUCKET`).
- Real `coin_image_service.dart`: `static const _collection = 'coin_image_index';` — `public_url` reads are at the Firestore doc probes (not `:404` as quoted).

Allowlist hosts/buckets themselves remain plausible for real emitters (`us_mint_coin_images`, `numista-reference-library`, `numista-uploads-studio-9101802118-8c9a8`), but Tier-1 requires honest `git show` quotes. Fabricated path/identifier/collection quotes reopen MF-I7.

**eBay / Google quotes** — verified `OutlinedButton.icon` + `void _onSearchGoogle` / `void _onSearchEbay` → `EpnService.generateSearchUrl(coin, soldOnly: true)`. Stale campid quote gone. **MF-B1' closed** (817 independent; inspector deletion optional only if CoS directs; NET-816 PARKED recorded).

**Pin hygiene** — pre-flight `git diff --quiet 4d17ca5e HEAD -- numista_mobile/`; DTG 15:35–15:42 ET matches file times. **MF-B2' closed.**

## v1.8 must-fix closeout verification
| # | Verdict |
|---|---|
| MF-B1' | **Closed** (parked dependency recorded; quotes corrected; eBay preserved) |
| MF-B2' | **Closed** |
| MF-B3' | **Closed** (both imports in diffs; intl/MeltValueService remain used) |
| MF-C2' | **Closed** |
| MF-C3' | **Closed** |
| MF-C5' | **Closed** |
| MF-C6' | **Closed** (rendered Text/Container colours asserted) |
| MF-I3' | **Closed** (canonical→user→ref + `users%2f`) |
| MF-I6 | **Closed** |
| MF-I7 | **NOT closed — blocking** (fabricated script paths/identifiers/collections) |
| MF-I5' | **Closed** |

## Numbered must-fixes for v2.0 (AG CoS v5 attempt 2/4)

### Images (780c) — blocking
**MF-I7'. [Tier-1 evidence] Re-quote real index emitters from `git show 4d17ca5e`.** Use `numista_backend/_scripts/build_image_index.py` (`SCAN_TARGETS`, `coin_image_index`, real `public_url` assignment), `_scripts/build_currency_image_index.py` (`REFERENCE_BUCKET`, `GCS_PREFIX = "reference_library/us_banknotes/"`, `currency_image_index`), `_scripts/promote_user_photos.py` (`BUCKET_NAME`/`PUBLIC_BASE` return form). Drop `scripts/reference_library/`, fabricated `SOURCES`/`BUCKET_NAME`/`CURRENCY_PREFIX`/`UPLOADS_BUCKET`/`REF_BUCKET`, and collection names `reference_images`/`currency_reference_images`. Cite `coin_image_service.dart` `_collection = 'coin_image_index'` and the real `public_url` read sites. Replace MF-I7 fixtures with one sanitised URL per **real** emitted path shape (e.g. `us_banknotes/...`, `reference/{program}/...`) — no AJ PII.

### Cards (780b)
Cards plan reaches **95** and may be preserved verbatim in the v2.0 package if Images-only deltas are isolated. Optional polish (not required to keep Cards ≥95): add a tiny standalone `MeltValueService.parseFaceValue` table unit test covering Half Dime / Three Cent Nickel / Five Cents for the shared `home_dashboard` call site.

### Both
Keep every item marked Closed above. Keep PLAN ONLY / main `9f04550a` / Stripe OFF / no Argon / Cards→Images apply order / `_onSearchEbay`.

## Rubrics
|Cards dimension|Score|
|---|---:|
|Branch/rollback/standing locks|19/20|
|Canonical year / denomination correctness|29/30|
|Retail precedence and contrast proposal|19/20|
|Shared structural removal/integration|14/15|
|Behavioral tests/provenance proof|14/15|
|**Cards**|**95/100 PASS**|

|Images dimension|Score|
|---|---:|
|Branch/rollback/standing locks|18/20|
|Complete applicable widget/future lifecycle|22/25|
|User-photo preservation and ownership/CSP|17/25|
|Network truth/operational safety|9/15|
|Real verification and shared removals|12/15|
|**Images**|**78/100 FAIL**|

Combined arithmetic: (95+78)/2 = **86/100 FAIL**. Cards clears the bar; Images is blocked solely on fabricated MF-I7 emitter evidence despite real progress on precedence/`users%2f`/`_cleanUrl`/refresh/CSP. Score is plan readiness, not runtime proof. No AJ PII; no secrets. No code/deploy/Firestore/main/Stripe authority. Path: revised CoS 95+ **each** → independent SAG 95+ → Eric typed YES. Writer remains AG CoS v5 `cfe23a7a` attempt **2/4**. Stall: AG on NET-813 v1.4 ETA 16:50 — under 2h, no stall reflag. No Eric ping.