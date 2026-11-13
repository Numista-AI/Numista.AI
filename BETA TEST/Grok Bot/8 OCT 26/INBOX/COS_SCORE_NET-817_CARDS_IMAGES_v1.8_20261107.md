# GB CoS score — NET-817 Cards v1.8 + Images v1.8

**Combined: 73/100 — FAIL.** Equal-weight plan scores: **Cards 70/100 FAIL; Images 76/100 FAIL**. Each plan must reach 95+; averaging never bypasses a failed plan.
Reviewed 7 Nov 2026, approximately 2:40–2:55 PM EST (America/New_York). Baton `BATON_NET-817_GROKCOS_REVIEW_FAILFIX_PLAN_780b-780c_v1.8_20261107-1430.md` (file mtime 2:16 PM ET, stamped 2:30 PM ET; delivery commit `7b61664a` on origin/p7-v8.9). Stamp is ~14 min ahead of file time — minor, improved from v1.7.

**Writer-cap:** per `RADIO_NOTE_CATALOG_PARKED_WRITER-CAP_2026-11-07-1420.md`, this is the single CoS score of AG CoS v4's final NET-817 delivery. **AG CoS v4 is OFF NET-817 and must not reopen it.** CoS assigns the v1.9 writer (see RADIO_NET-832).

## Scope and evidence
Plans: `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.8.md` (C, SHA256 `DA8A575BB3CF…`) and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.8.md` (I, SHA256 `672D8E11E82B…`). Mirrors in docs / BATONS / RADIO NET / INBOX / OUTBOX / `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX` all hash-match. **Accepted.**
Prior: `COS_SCORE_NET-817_CARDS_IMAGES_v1.7_20261107.md` (60; Cards 67 / Images 53).

Repository on EDS_Laptop `C:\Users\ericd\Documents\MyVertexProject`, after `git fetch`. All citations checked at **p7 @4d17ca5e** via `git show` / `git grep` (not the working tree). Verified: `origin/main` **9f04550a** (unchanged); `origin/p7-v8.9` tip **7e8ece75** (docs-only; zero `numista_mobile/lib`, `numista_mobile/test` or `firebase.json` diff vs 4d17ca5e); `origin/dev` **cf622fb8** before this push. Read-only audit; proposed snippets inspected, not compiled or applied. Live smoke (parent, ~2:40 PM ET): `https://numista.ai` 200, `main.dart.js` 200, bad path 404.

## GEMINI38_REVIEW — real code from the pin (Tier-1 grounding)

**Package** — `numista_mobile/pubspec.yaml:1` `name: numista_ai`. Both plans now import `package:numista_ai/...`. **Closed.**

**Card valuation (`my_collection_screen.dart`)** — `:47 class _F {` … `:72 static const aiValue = 'AI Estimated Value';`, `:51 denomination = 'Denomination'`, `:76–77 imageObverse = 'image_url_obverse'` / `imageReverse = 'image_url_reverse'`. Lines `:3017–3023` exactly as plan quotes (`final valCpg = _parseNumber(m['cpgRetail']);` … `: (m[_F.aiValue]?.toString() ?? '—');`). `:3015` is the `displayTitle` tail. Row `:3167–3192` with `:3170 if (valueText == '—' || m['enrichment_status'] == 'pending')`. `valueText` is referenced only at `:3021, 3170, 3182` (safe to remove). Table column `:3338–3346`:
```dart
case _F.aiValue:
  final coinCpg = _parseNumber(m['cpgRetail']);
  ...
  final av = m[_F.aiValue]?.toString().trim() ?? '';
  if (av == 'Pending' || av == 'null' || av.isEmpty) return '';
```
**Plan widget reads `data['ai_value'] ?? data['aiValue']` — neither key exists in production; the real key is `'AI Estimated Value'` (`_F.aiValue`).** Imports at `:14–44` are relative (`'../widgets/grade_badge_widget.dart'`, `'../services/melt_value_service.dart'`, …); there is no import of a `collection_card_valuation_row.dart` or `collection_card_image.dart`.

**Face-value parser** — `melt_value_service.dart:53 static double parseFaceValue(String rawDenom, {int qty = 1})`. Order on the pin:
```dart
:77  else if (s.contains('half dollar') || s.contains('50c') || s.contains('50 cent') ...) { value = 0.50; }
:78  else if (s.contains('quarter dollar') || s.contains('quarter') || s.contains('25c') ...) { value = 0.25; }
:80  else if (s.contains('dime') || s.contains('10c') || s.contains('10 cent') ...) { value = 0.10; }
:81  else if (s.contains('half dime')) { value = 0.05; }
:82  else if (s.contains('nickel') || s.contains('5c') || s.contains('5 cent') ...) { value = 0.05; }
:86  else if (s.contains('penny') || s.contains('cent') || s.contains('1c') ...) { value = 0.01; }
```
CoS traced it against the canonical names in `lib/constants/denomination_canon.dart:4–9` (`'Cent'`, `'Five Cents'`, `'Dime'`, `'Quarter Dollar'`, `'Half Dollar'`, `'Dollar'`): **`'Five Cents'` → $0.01** ("five cents" contains none of nickel/5c/"5 cent", so it falls to the `cent` branch at :86). "Ten Cents" → $0.01, "Fifty Cents" → $0.01, "Half Dime" → $0.10 (`dime` at :80 wins before `half dime` at :81), "Three Cent Nickel" → $0.05. Plan §1 claims the parser "evaluates multi-word tokens ('half dime', 'three cent', 'half dollar') before generic tokens" — **not true for half dime / three-cent nickel, and the canonical nickel name is mispriced.** (Parent audit marked the order "correct" — CoS re-traced at the pin and records the trace; the defect is in how the shared parser handles canonical names, so the fix is a plan-level normalisation or test-guarded parser fix, not a blame item.)

**GradeBadgeWidget** — `lib/widgets/grade_badge_widget.dart:10/14–16` `const GradeBadgeWidget({… required this.gradeCode})`. Plan import path/param correct.

**Denomination matcher** — `canonical_mint_asset_service.dart:430` comment, `:431–434` as quoted. `denomination_canon.dart:26 '1 cent': cent` is a real alias. Proposed `(?<!\d\s*)\bcent\b` **rejects `"1 cent"`** (lookbehind sees `1 `), so a `1 cent` denomination now resolves only if the title also says "lincoln cent / one cent / penny" — a regression. Proposed tests use titles `'Lincoln Cent'` / `'Jefferson Nickel'`, which already satisfy the **unchanged title regexes** (`:432`, `:434`), so the 1¢/5¢ tests pass on the old code too — **non-discriminating**. `canonicalYear` is new (only `_normYear :72–76`, `extractSku :78`, `resolveFromMap :153`); insertion after :76 is correct and additive.

**Images widget** — `:6356 class _CollectionCardImage extends StatelessWidget`, constructor `:6358 const _CollectionCardImage({required this.data});`, single call site `:3064 child: _CollectionCardImage(data: m),`. Shipped order:
```dart
:6369 final canon = CanonicalMintAssetService.resolveFromMap(data);
:6370 if (canon != null) { final canonUrl = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl; ... return _buildCoinImage(canonUrl); }
:6360 static String _cleanUrl(dynamic val) { ... if (s.isEmpty || s.startsWith('gs://') || !s.startsWith('http')) return ''; return s; }
:6379 final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)
:6413 final refUrl = (ref?.reverseUrl?.isNotEmpty == true) ? ref!.reverseUrl! : (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true) ? ref!.obverseUrl! : '';
```
So the shipped policy is **canonical Mint asset first, then user photo, then reference**, and non-`http` junk in a photo field falls through to the reference lookup. The plan is **user photo first**, and any non-empty non-`gs://` string (e.g. `N/A`, `pending`, a local path) is treated as a user photo, fails `isOwnedStorageUrl`, and shows a placeholder with **no reference fetch**. (`resolveFromMap` `:156` already returns null when `hasUserUploadedPhotos` matches `studio-9101802118-8c9a8-uploads` / `numista-uploads-studio-` / `/users/`; but getDownloadURL URLs are `.../o/users%2F...`, encoded, so `/users/` does not match. Putting user photos first may be the right product call, but it reverses shipped behaviour and the plan claims "restored shipped display policy".) Steal-guard, `BoxFit.contain`, `blurRadius: 14` are reproduced faithfully.

**Reference source** — `coin_image_service.dart:562–583` reads `obverse.public_url` / `reverse.public_url` from Firestore index docs; `numista_backend/_scripts/build_currency_image_index.py:267` builds `f"{PUBLIC_URL_BASE}/{REFERENCE_BUCKET}/{blob.name}"`. The plan never shows that every `public_url` in the index falls inside its allowlist (probable but unproven); any outside host will now be hidden.

**Real host forms** — `firebase_options.dart:55,64,73` bucket `studio-9101802118-8c9a8.firebasestorage.app`; `my_collection_screen.dart:5015` `getDownloadURL()`; `lib/widgets/common/ref_image_widget.dart:57` `https://storage.googleapis.com/us_mint_coin_images/$path` (plan cites `ref_image_widget.dart` without `common/` — path nit); `canonical_mint_asset_service.dart:52–53` `_base = 'https://storage.googleapis.com/numista-reference-library/reference_library'`; `:37–38` upload buckets. Fabricated buckets and wildcards are gone. **Allowlist forms are real — MF-I1 closed.**

**CSP** — `numista_mobile/firebase.json:276` matches the plan's verbatim quote; `img-src` lacks `firebasestorage.googleapis.com`; `connect-src` has `https://*.googleapis.com`. Adding `https://firebasestorage.googleapis.com` to `img-src` is correct and additive. **MF-I4 closed.**

**eBay** — `:4408–4409` doc comment "Opens eBay SOLD listings … using an EPN affiliate link"; `:4410 void _onSearchEbay(...)` → `:4413 EpnService.generateSearchUrl(coin, soldOnly: true)`. Plan's quoted `campid=5339123164, customid=numista_app_search` comment and `Future<void>` signature do not appear at those lines — stale quote (minor; preservation intent correct).

**Pin hygiene** — §4.A of both plans says "locked to p7-v8.9 at HEAD `ebf1eed8`" — that is the NET-830 ACK docs commit; tip is now 7e8ece75. Pre-flight should assert "no `numista_mobile/` diff vs 4d17ca5e", not a docs HEAD.

## CoS-60 must-fix closeout verification
| # | Claim | Verdict |
|---|---|---|
| MF-B1 | NET-816 sole deletion owner; 817 deletes nothing; `_onSearchEbay` kept | **Closed as plan text.** **Gate risk:** NET-816 Catalog is PARKED (writer-cap), so the Kaggle/Google inspector deletions (3454, 3820, 5252–5278, 5549–5684, 150–151, 3531–3548, 4387–4406) currently have **no active writer and may not land before Thanksgiving**. 817 compiles without them, but the Cards/Images outcome Eric expects (inspector gone) is blocked until CoS re-homes the deletions. |
| MF-B2 | `package:numista_ai` | **Closed.** |
| MF-B3 | DTG + apply order | **Mostly closed** (order Cards → Images stated; DTG 14 min ahead of file; stale `ebf1eed8` pin). |
| MF-C1 | Anchors 3017–3023 / 3167–3192 | **Closed.** |
| MF-C2 | AI value + enrichment state kept | **NOT closed — blocking.** Widget reads `ai_value`/`aiValue`; production key is `'AI Estimated Value'`. Every real AI estimate is dropped → face value + chip. Same silent regression as v1.7. Also doesn't exclude `'Pending'`/`'null'` like the table (`:3346`). Unstated change: CPG>0 + `enrichment_status=='pending'` used to show the chip; now it doesn't. |
| MF-C3 | Reuse `parseFaceValue`; '—' when unknown | **Partially closed.** Reuse and '—' done. Canonical `'Five Cents'` → $0.01 (plus Ten/Fifty Cents, Half Dime, Three Cent Nickel); no test covers the `DenominationCanon` names; plan's ordering claim is false. |
| MF-C4 | Real widget in lib/, pumped by tests | **Mostly closed.** `CollectionCardValuationRow` in lib/widgets is right, **but no import is added to `my_collection_screen.dart`** → compile failure as written. |
| MF-C5 | Keep 749-line suite; `(?!\w)` fix | **Partially closed.** New file keeps the suite. The regex rewrite regresses `'1 cent'`; the 1¢/5¢ tests don't discriminate (title rescues); 15¢/25c guards also pass on old code. |
| MF-C6 | Theme-aware contrast | **Mostly closed.** Colours and ratios are right. The contrast "test" checks constants, not the colours the widget renders (tautological). |
| MF-C7 | Additive `canonicalYear` after :76 | **Closed.** |
| MF-I1 | Real allowlist only | **Closed** (all forms real; wildcards and fabricated buckets gone; backslash/`//` rejected). Residual: index `public_url` forms not shown to be inside the list. |
| MF-I2 | Reachable public helpers + public widget | **Mostly closed.** Top-level `isOwnedStorageUrl`, `extractUserPhoto`, public `CollectionCardImage` + `CollectionCardImageRequestKey`. **Missing import of `collection_card_image.dart` in `my_collection_screen.dart`** → the `:6357` wrapper won't compile. |
| MF-I3 | Shipped display policy + steal-guard | **Partially closed.** Steal-guard, reverse preference, contain/glow are faithful. **Precedence is inverted** (user photo before canonical, shipped is canonical first) while the plan claims "restored". Non-URL junk now fails closed instead of falling through to the reference (regression vs `_cleanUrl`). |
| MF-I4 | CSP truth | **Closed.** |
| MF-I5 | Tests | **Mostly closed.** Accept/reject fixtures real; `resolveFromMap(...) isNull` proof present; refresh test present. Refresh test doesn't assert it's the same State (no key or State-identity check), so it relies on implicit tree reuse. No test for junk fields falling through, canonical-vs-user precedence, or a `public_url` sample form. |

## Numbered must-fixes for v1.9 (writer assigned by CoS — NOT AG CoS v4)

### Both plans
**MF-B1'. [Gate] Re-home the Kaggle/Google deletions or record the dependency as blocked.** NET-816 is PARKED. Either CoS's split hands the deletion span (3454, 3820, 5252–5278, 5549–5684 incl. `_showRefImageDialog`, 150–151, 3531–3548, 4387–4406) to an active owner, or 817 v1.9 says outright that inspector removal is out of scope and blocked. Don't cite a parked plan as a live prerequisite. Keep `_onSearchEbay` (`:4410`, `EpnService.generateSearchUrl`). Fix the stale campid quote.
**MF-B2'. [Hygiene] Pin pre-flight to code, not docs:** `git diff --quiet 4d17ca5e <apply-base> -- numista_mobile/` (drop `ebf1eed8`). Stamp the DTG at real file time.
**MF-B3'. [Compile] Add the imports to `my_collection_screen.dart`** in the same relative style as `:14–44`: `import '../widgets/collection_card_valuation_row.dart';` (Cards) and `import '../widgets/collection_card_image.dart';` (Images). State whether `intl`/`MeltValueService` imports stay used.

### Cards (780b)
**MF-C2'. [Blocking; regression] Read the real AI key.** Use `data[_F.aiValue]`. Since `_F` is library-private, pass the value in, or read `'AI Estimated Value'`, with optional aliases `ai_estimated_value` / camelCase. Never rely only on `ai_value`/`aiValue`. Treat `'Pending'`, `'null'` and empty as absent (match `:3346`). Add a widget test with `{'AI Estimated Value': '35.00', 'cpgRetail': 0}` → `$35.00`. State the CPG>0 + `enrichment_status=='pending'` behaviour (shipped shows the chip) and keep it or cite the decision that changes it.
**MF-C3'. [Correctness] Make face value right for canonical names.** Normalise the denomination through `DenominationCanon.colloquialMap` (or an explicit card-local map) before `parseFaceValue`, OR propose a separately scoped, test-guarded parser fix (it is shared with `home_dashboard.dart:300`; reorder `half dime` before `dime`, add `five cent`/`ten cent`/`fifty cent`, and put `three cent` before `nickel`). Add a table test: Cent .01, Five Cents .05, Dime .10, Quarter Dollar .25, Half Dollar .50, Dollar 1.00, Half Dime .05, Three Cent Nickel .03, Set → '—'. Drop the false ordering claim.
**MF-C5'. [Regression + tests] Don't break `'1 cent'`.** Use, e.g., `RegExp(r'(?<![\d.])(?:1c|1¢|1 cent|one cent|penny)(?!\w)|(?<![\d.]\s?)(?<!\w)cent(?!\w)')`, or keep the original alternation and only replace the trailing `\b` with `(?!\w)`. Show results for `1 cent`, `1¢`, `cent`, `25 cent`, `15¢`, `5¢`, `five cents`. Make the tests discriminating: use titles that don't hit the title regex (e.g. `'title': '2026 Coin'`) so only the denomination path decides. Include `'1 cent'` → `2026-CENT-P`.
**MF-C6'. [Tests] Assert rendered colours.** Pump the widget in light and dark themes, read `tester.widget<Text>(find.text('Value pending AI estimate')).style!.color`, and assert contrast against the real card surface (`_surface` `:211`, virtual child `0xFF0D1520`/`0xFFF5F5F0`) and the light chip background `#FFF3CD`.

### Images (780c)
**MF-I3'. [Behaviour] Declare precedence.** Shipped is canonical → user photo → reference (`:6369–6383`). Either keep it, or cite Eric/B-decision for "user photo first" and list the cards whose display changes (e.g. 2026 SKUs with a user photo). Don't call an inversion "restored".
**MF-I6. [Regression] Only real URLs count as user photos.** In `extractUserPhoto`, keep shipped `_cleanUrl` semantics: accept only `https://` (or an explicitly decided `/`-relative form). Non-URL junk (`N/A`, `pending`, local paths) returns '' so the card falls through to canonical/reference. Fail closed only for well-formed URLs that aren't owned. Add tests for junk → reference fetch called, and foreign `https://` → placeholder.
**MF-I7. [Ownership evidence] Prove the reference `public_url` forms.** Use a read-only check (no writes): grep `PUBLIC_URL_BASE`/`REFERENCE_BUCKET` in `build_currency_image_index.py` and the index writers, or do a sampled read of the index collection. Show every `public_url` host/bucket is inside the allowlist, or add the missing exact bucket. Quote one sanitised fixture per form (no AJ data, no emails).
**MF-I5'. [Tests] Same-State refresh proof.** Give `CollectionCardImage` a fixed `key: const ValueKey('card')` in both pumps, capture `tester.state(...)` before and after, and assert `identical` plus fetch count 2. Add canonical-vs-user precedence tests matching whatever MF-I3' decides. Fix the `ref_image_widget` path to `lib/widgets/common/ref_image_widget.dart`.

## Rubrics
|Cards dimension|Score|
|---|---:|
|Branch/rollback/standing locks|17/20|
|Canonical year / denomination correctness|22/30|
|Retail precedence and contrast proposal|9/20|
|Shared structural removal/integration|12/15|
|Behavioral tests/provenance proof|10/15|
|**Cards**|**70/100 FAIL**|

|Images dimension|Score|
|---|---:|
|Branch/rollback/standing locks|17/20|
|Complete applicable widget/future lifecycle|19/25|
|User-photo preservation and ownership/CSP|18/25|
|Network truth/operational safety|12/15|
|Real verification and shared removals|10/15|
|**Images**|**76/100 FAIL**|

Combined arithmetic: (70+76)/2 = **73/100 FAIL**. Images made real progress (allowlist, CSP, public seams, steal-guard all fixed). Cards still drops every real AI estimate because it reads the wrong key, which is the same blocker as v1.7. Score is plan readiness, not proof of runtime safety. No AJ PII encountered; no secrets copied. No code, deployment, Firestore, deletion, main, or Stripe authority granted. Path stays: revised CoS 95+ each → independent SAG 95+ → Eric typed YES; separate gates remain separate. Writer-cap: AG CoS v4 OFF NET-817; Catalog NET-816 remains PARKED (not scored here).
