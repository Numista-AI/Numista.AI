# GB CoS score — NET-817 Cards v2.0 + Images v2.0

**Combined: 95.5/100 — PASS.** Equal-weight plan scores: **Cards 96/100 PASS; Images 95/100 PASS**. Each plan must reach 95+; averaging never bypasses a failed plan. Both plans clear the bar, so the package PASSES.
Reviewed 7 Nov 2026, approximately 7:15–7:20 PM EST (America/New_York). Baton `BATON_NET-817_GROKCOS_REVIEW_CARDS-IMAGES_v2.0_20261107-1915.md` (file mtime 7:10 PM ET, stamped 7:15 PM ET). Writer: AG CoS v5 `cfe23a7a`, attempt **2/4**.

## Scope and evidence
Plans: `docs/FAILFIX_PLAN_NET-780b_CARDS_v2.0.md` and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v2.0.md` (mtime 5:15:47 PM ET; 55702 / 59331 bytes). Delivery commit observed: **`bf329da1`** on `origin/p7-v8.9` (`docs(net-817): deliver Cards v2.0 and Images v2.0 failfix plans, review baton, and ACK NET-840 (attempt 2/4)`, 7:11:29 PM ET). Docs-only counterpart on `origin/dev`: **`d5db8605`** (same message, 7:12:11 PM ET). Prior: `COS_SCORE_NET-817_CARDS_IMAGES_v1.9_20261107.md` (Combined 86 FAIL; Cards 95 PASS / Images 78 FAIL).

Repository on EDS_Laptop `C:\Users\ericd\Documents\MyVertexProject`. All citations checked at **p7 @4d17ca5e** via `git show` / `git ls-tree` (not the working tree, not plan quotes alone). Verified: `origin/main` **9f04550a** (unchanged); `git diff --stat 4d17ca5e HEAD -- numista_mobile/` empty (docs-only tip `397f83ba` after later NET-813 v1.4 docs delivery; v2.0 plans themselves landed at `bf329da1`); Stripe OFF; PLAN ONLY. Pin `4d17ca5e` message: deliver NET-817 v1.5 plans. `c294fd3c` (cited as last `numista_mobile/` code commit on p7) exists and is the last commit touching `numista_mobile/` at the pin. Live smoke already taken by the watch at ~7:12 PM ET: `https://numista.ai` 200, `main.dart.js` 200, bad path 404, catalog 200, pricing 200.

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
// :3170 shipped pending-chip gate
if (valueText == '—' || m['enrichment_status'] == 'pending')
```
Widget still reads `'AI Estimated Value'` first; sentinel filter and intentional CPG>0 suppresses chip remain documented vs shipped `:3170`. Imports stay relative; plan still adds `import '../widgets/collection_card_valuation_row.dart';`. **MF-B3' / MF-C1 / MF-C2' remain closed.**

**Face-value parser** — `melt_value_service.dart` at pin (verified `:53+`, bug order at `:80–86`):
```dart
else if (s.contains('dime') || s.contains('10c') || ...) { value = 0.10; }
else if (s.contains('half dime')) { value = 0.05; }   // AFTER dime — Half Dime → $0.10 BUG
else if (s.contains('nickel') || s.contains('5c') || ...) { value = 0.05; }
else if (s.contains('three cent') || ...) { value = 0.03; }  // AFTER nickel — Three Cent Nickel → $0.05 BUG
else if (s.contains('penny') || s.contains('cent') || ...) { value = 0.01; } // Five Cents → $0.01 BUG
```
`DenominationCanon` (`numista_mobile/lib/constants/denomination_canon.dart:4–9`): `'Cent'`, `'Five Cents'`, `'Dime'`, `'Quarter Dollar'`, `'Half Dollar'`, `'Dollar'`. Plan still patches order (`half dime` before `dime`, `three cent` before `nickel`, adds `five cent`/`ten cent`/`fifty cent`/`twenty-five cent`) AND `resolveFaceValue` exact-switches canon constants before `parseFaceValue`. Full widget table test preserved. **New polish (not required for 95):** standalone `MeltValueService.parseFaceValue` table in §6.1 covering `Cent` / `Five Cents` / `Dime` / `Quarter Dollar` / `Half Dollar` / `Dollar` / `Half Dime` / `Three Cent Nickel` / `Set` for the shared `home_dashboard` call site. **MF-C3' closed + polished.**

**Denomination matcher** — pin `:431–434` unchanged and still correctly quoted:
```dart
final isCent = RegExp(r'\b(1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) || ...
final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) || ...
```
Plan still replaces with lookbehind/`(?!\w)` form including `1 cents?`, neutral title `'2026 Coin'`, positive/negative guards. `canonicalYear` still absent at pin (only `_normYear`); additive after `:76` OK. **MF-C5' / MF-C7 closed (preserved).**

**Images widget** — pin `:6356–6417` (verified) still quoted:
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
Plan keeps **canonical → user → reference**, patches `hasUserUploadedPhotos` with `users%2f`, `extractUserPhoto` keeps URL-only semantics, same-State `ValueKey('card')` + `identical` refresh proof (§6.2 Case 7), `ref_image_widget` path `lib/widgets/common/ref_image_widget.dart:57` verified. **MF-I3' / MF-I6 / MF-I5' remain closed.** CSP `:276` `img-src` lacks `firebasestorage.googleapis.com` — additive patch still correct (**MF-I4 closed**).

**MF-I7' — NOW closed (was blocking in v1.9).** CoS independently `git show` / `git ls-tree` at `4d17ca5e` and compared the plan's quoted blocks:

- `numista_backend/scripts/reference_library/*` still does **not** exist. Real paths `numista_backend/_scripts/build_image_index.py`, `build_currency_image_index.py`, `promote_user_photos.py` **do** exist and are the paths the v2.0 plan quotes.
- Real `build_image_index.py`: `:45` `FIRESTORE_COLLECTION = "coin_image_index"`; `:46` `PUBLIC_URL_BASE = "https://storage.googleapis.com"`; `:53–103` `SCAN_TARGETS` (not `SOURCES`) with prefixes `Numista_Attributed_Coins (1)/`, `reference_library/bulk_programs/`, `wikimedia_uscoin/`, `rare_uscoin/`, `balabaskar_coins/`, `2026_series/`, `user_contributed/`; `:302–303` `encoded_path = blob_name.replace(" ", "%20")` then `public_url = f"{PUBLIC_URL_BASE}/{bucket}/{encoded_path}"`. Plan quotes these lines verbatim.
- Real `build_currency_image_index.py`: `:39` `FIRESTORE_COLLECTION = "currency_image_index"`; `:40` `REFERENCE_BUCKET = "numista-reference-library"`; `:41` `GCS_PREFIX = "reference_library/us_banknotes/"` (not `wikimedia_uscurrency`); `:267` `public_url = f"{PUBLIC_URL_BASE}/{REFERENCE_BUCKET}/{blob.name}"`. Plan quotes these lines verbatim.
- Real `promote_user_photos.py`: `:16–18` docstring `reference/{program_slug}/{year}_{program_slug}_{side}.jpg` and `coin_image_index`; `:35` `BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"`; `:36` `REF_PREFIX = "reference"`; `:37` `PUBLIC_BASE = "https://storage.googleapis.com"`; `:130` `return f"{PUBLIC_BASE}/{BUCKET_NAME}/{dest_path}"` (no `UPLOADS_BUCKET`/`REF_BUCKET`). Plan quotes these lines verbatim.
- Real `coin_image_service.dart`: `:17` `static const _collection = 'coin_image_index';`; `public_url` reads at `:567` `bestObvUrl = d['public_url'] as String?;` and `:583` `bestRevUrl = d['public_url'] as String?;`. Plan quotes `:16–18` and `:561–589` verbatim. The v1.9 `:404` cite is gone.

Fabricated identifiers `scripts/reference_library/`, `SOURCES`, `us_mint_direct`/`pcgs_coinfacts` as `SOURCES` keys, `CURRENCY_PREFIX = "reference_library/wikimedia_uscurrency/"`, `UPLOADS_BUCKET`, `REF_BUCKET`, Firestore collections `reference_images` / `currency_reference_images`, and `coin_image_service.dart:404` appear only in the closeout table as items **dropped**, not as claimed quotes. The substring `s.contains('/reference_images/')` at plan §3.C is a verbatim quote of shipped `canonical_mint_asset_service.dart:35`, not a collection-name invention.

`isOwnedStorageUrl` Form A (`firebasestorage.googleapis.com` + `studio-9101802118-8c9a8.firebasestorage.app`), Form B (`storage.googleapis.com` + `us_mint_coin_images` / `numista-reference-library` / `numista-uploads-studio-9101802118-8c9a8` plus the already-shipped upload/`firebasestorage.app` roots), and relative `/assets/...` match the real emitted URL shapes. §6.1 fixtures are sanitized (`anon_user_1` / generic coin filenames; no AJ PII) and cover mint `%20` encoding, each `reference_library/{folder}/` shape used by `SCAN_TARGETS` (balabaskar is the same form as the other `reference_library/` prefixes; a dedicated balabaskar URL is omitted but not a distinct host/bucket form), `us_banknotes/`, and `reference/{program_slug}/...`.

**eBay / Google quotes** — still verified `OutlinedButton.icon` + `void _onSearchGoogle` / `void _onSearchEbay` → `EpnService.generateSearchUrl(coin, soldOnly: true)`. **MF-B1' remains closed.**

**Pin hygiene** — pre-flight `git diff --quiet 4d17ca5e HEAD -- numista_mobile/`; DTG 16:33 / 16:37 ET matches the “observed wall-clock while drafting” claim (files written 17:15:47 ET). **MF-B2' remains closed.** `647d3401` (`chore: auto-backup 2026-11-07 18:00`, includes mobile code) exists but is **not** an ancestor of current `HEAD`/`origin/p7-v8.9`.

## v1.9 must-fix closeout verification
| # | Verdict |
|---|---|
| MF-B1' | **Closed** (preserved) |
| MF-B2' | **Closed** (preserved) |
| MF-B3' | **Closed** (preserved) |
| MF-C2' | **Closed** (preserved) |
| MF-C3' | **Closed** (preserved) + standalone `parseFaceValue` table polish added |
| MF-C5' | **Closed** (preserved) |
| MF-C6' | **Closed** (preserved) |
| MF-I3' | **Closed** (preserved; canonical→user→ref + `users%2f`) |
| MF-I6 | **Closed** (preserved) |
| MF-I7 / MF-I7' | **Closed** (real `_scripts/` emitters and collections `coin_image_index` / `currency_image_index` quoted verbatim from `git show 4d17ca5e`) |
| MF-I5' | **Closed** (preserved) |
| MF-I4 | **Closed** (preserved) |
| MF-I1 | **Closed** (allowlist aligned with real emitted URL shapes) |

## Numbered must-fixes
None. Both plans are ≥95. Next step is independent SAG review ≥95, then Founder Eric typed YES. No SAG score is invented here. No Eric ping.

Cards v2.0 is not a byte-identical copy of v1.9 (header/table restated for v2.0; §6.2 test filename bumped to `canonical_mint_asset_service_v2_0_test.dart`; file is 1048 vs 1064 lines) but every item marked Closed in v1.9 is still present and still accurate vs `git show`. The added §6.1 `parseFaceValue` table is optional polish and does not regress Cards.

## Rubrics
|Cards dimension|Score|
|---|---:|
|Branch/rollback/standing locks|19/20|
|Canonical year / denomination correctness|29/30|
|Retail precedence and contrast proposal|19/20|
|Shared structural removal/integration|14/15|
|Behavioral tests/provenance proof|15/15|
|**Cards**|**96/100 PASS**|

|Images dimension|Score|
|---|---:|
|Branch/rollback/standing locks|19/20|
|Complete applicable widget/future lifecycle|23/25|
|User-photo preservation and ownership/CSP|23/25|
|Network truth/operational safety|15/15|
|Real verification and shared removals|15/15|
|**Images**|**95/100 PASS**|

Combined arithmetic: (96+95)/2 = **95.5/100 PASS**. Cards stays at the v1.9 bar plus one polish point on the standalone `parseFaceValue` table (behavioral tests 14→15). Images clears the bar because MF-I7' is honestly closed and prior closes hold. Score is plan readiness, not runtime proof. No AJ PII; no secrets. No code/deploy/Firestore/main/Stripe authority. Path: CoS 95+ **each** (met) → independent SAG 95+ → Eric typed YES. Writer was AG CoS v5 `cfe23a7a` attempt **2/4** (package passed; no revise). Stall: NET-840/838/813 ACK'd (do not re-flag); NET-813 v1.4 review baton subsequently landed at 19:25 stamp / commit `397f83ba` (observed this run, **not scored**); NET-841 Catalog Chunk1 v2.2 stall stands, next re-flag ~19:43 ET (not re-flagged this run). No Eric ping.
