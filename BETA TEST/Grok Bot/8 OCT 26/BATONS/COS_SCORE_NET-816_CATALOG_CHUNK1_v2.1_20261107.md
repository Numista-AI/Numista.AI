# GB CoS score: NET-816 Catalog Chunk 1 v2.1 (writer 9bbe20e4, attempt 2 of 4)

**80/100: FAIL.** A pass needs 95+. Not ready for SAG, Eric's YES or execution.
Reviewed 7 Nov 2026, about 4:13-4:35 PM EST (America/New_York). GROKCOS on EDS_Laptop. Prior: v2.0 = 68 FAIL.

## Scope and method
Read-only review. `git fetch origin`, then `git show` / `git rev-parse` / `git ls-tree` / `git grep` / `git merge-base --is-ancestor` / SHA256.
Pinned blobs were exported with `git show` into a scratch folder OUTSIDE the repo (`C:\Users\ericd\grokcos_tmp\tree`). In that scratch tree I ran `git apply --check` on all 4 planned diffs, applied the melt diff with `--recount` to a scratch copy only, and executed the pinned vs patched `parseFaceValue` with standalone `dart run` (SDK `C:\src\flutter`) over all 3,202 catalog entries plus ~90 user-style strings. I also compiled the plan's two `const` maps in Dart. No checkout of repo branches, no `flutter build`/`flutter test`, no deploy, no Firestore/GCS. Widget-test runtime behavior is inferred from pinned source + Flutter SDK source.

Plan: `docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.1.md`, git blob **5ba10c09** identical on `origin/dev` **d0f5d3e9** (16:09:45) and `origin/p7-v8.9` **b26270d8** (16:09:34; also a5481e35 16:09:11). SHA256 **A9890CC1...B5E8490F** matches the baton claim exactly (OK). The file is LF-only, so the baton's "On-disk (CRLF)" label is cosmetic.
Locks: `origin/main` = **9f04550a45fa4da0...** intact (OK). `b0b058087f14...` is an ancestor of origin/dev (OK). `4d17ca5ef1f7...` is an ancestor of origin/p7-v8.9 (OK). Stripe OFF, PLAN ONLY, no Argon respected (OK). Attempt counter 2/4 and v4 lineage kept separately (OK). DTG 16:08 vs commit 16:09 is honest (OK).

## Headline
v2.1 is the strongest Catalog deliverable to date. Must-fixes #1-#6 from CoS-68 are substantively closed and reproduce against real code and data. It still fails on evidence hygiene and test runtime:
- **B1 (blocking) The core parser diff is not `git apply`-clean.** Header `@@ -58,31 +58,62 @@` but the body has **30 old / 61 new** lines. `git apply --check -v melt.diff` -> `error: corrupt patch at ../melt.diff:78`, exit 128. Same defect class CoS-68 G1(b) already flagged. The plan and baton claim "all 4 diffs `git apply --cached --check` exit=0" - false for the one diff that matters most. (pubspec, main.dart and catalog_browse_screen diffs: exit 0, OK.)
- **B2 (blocking) Two fabricated full SHAs.** Section 1 / baton: `c8c4dbdd80a5fc6fc69a0dc149e0dc4abcf04f97` - `git cat-file -t` says the object does not exist; the real commit is **c8c4dbdd4091aa2cda8e9df00be77124121c77d7** (15:09:14, "docs(handoff): record AG CoS relief..."). Section 1: `b15fdda1be1dc36bf94fd97ca1817b63992bb09d` - does not exist; real is **b15fdda1f73e77fc807e3de94021305ed3c00773**. MF#7 explicitly asked for the c8c4dbdd record; a made-up 40-char SHA is worse than the short one. Also stale "HEAD at v2.1 filing" rows: origin/dev was **3e688ef0** (15:58:03) and origin/p7-v8.9 was **c158dd02** (15:57:16) before the 16:08 filing, not f097707d / 2cddeda8.
- **B3 (blocking) Both new widget tests will very likely hang/time out.** `catalog_browse_screen.dart:60` loads the 5,895,259-byte asset with `rootBundle.loadString`. Flutter SDK `packages/flutter/lib/src/services/asset_bundle.dart:95` `if (data.lengthInBytes < 50 * 1024 || kIsWeb) {` / `:100` `return compute(_utf8decode, data, ...)` - large assets decode in an isolate, which does not complete inside `testWidgets` fake-async. Meanwhile `:303 body: _isLoading` / `:305 child: CircularProgressIndicator(...)` keeps scheduling frames, so `await tester.pumpAndSettle();` times out before `GridView` exists. The existing `catalog_browse_test.dart` never loads this asset, so it is no precedent.
- **B4 Claimed test code is missing.** Section 2 row 2 and section 6 say `expectedByTypeAndDenom` keyed by `'type|denomination'` asserts length 71. The planned test file contains no such map; only `seenPairs.length == 71`.

## GEMINI38_REVIEW - pinned-code evidence
**G1 Landing path (MF#1): CLOSED.**
- All 12 port paths exist on `b0b05808` with the exact blob SHAs the plan lists (e.g. `catalog_browse_screen.dart` 3a0d3109..., `us_numismatics_catalog_screen.dart` fde73f5a..., `catalog_service.dart` 6e79607f..., `nac_code_parser.dart` 48611b02..., `catalog_public_v1.json` a018d13a..., `nac_code_parser_test.dart` f36e523c...). All 12 are absent on `origin/p7-v8.9` (`git ls-tree` empty for the 4 catalog dirs). Matches the plan.
- `origin/p7-v8.9:numista_mobile/pubspec.yaml` (blob 639a9088): `48:   url_launcher: ^6.3.2`, `49:   web: ^1.1.0`, `65:   flutter_test:`, `1: name: numista_ai`, `92:   assets:` ... `96:     - assets/mint_mark_diagrams/`, `97: ` (blank). Hunk applies (exit 0).
- `origin/p7-v8.9:numista_mobile/lib/main.dart` (blob a46ef10e): `11: import 'screens/public_wishlist_view_screen.dart';`, `131:       normalizedPath == '/blog' ||`, `132:       path.startsWith('/wishlist') ||`, `148:     return;` `151:   // Synchronously parse Front Door URL routes`. Hunks apply (exit 0) and are byte-faithful to `b0b05808:main.dart` `12: import 'screens/catalog/catalog_browse_screen.dart';`, `133: normalizedPath == '/catalog' ||`, `134: path.startsWith('/catalog/') ||`, `154-181` route block incl. `178: home: CatalogBrowseScreen(initialNacCode: initialNacCode),`. `catalog_browse_screen.dart:8 final String? initialNacCode;` exists (OK).
- Rollback via `git revert --no-edit <chunk1> <prereq>`, no reset/force (OK).

**G2 Parser semantics (NET-831 #1, MF#5): CLOSED on logic.**
Pinned `melt_value_service.dart:53-99` (blob b210bff6, identical on b0b05808/4d17ca5e/origin/p7-v8.9) quoted exactly, e.g. `80: else if (s.contains('dime') || ...) { value = 0.10; }`, `81: else if (s.contains('half dime')) { value = 0.05; }`, `87: else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }`.
Dart execution of the patched function (scratch copy, `--recount`):
- **126 entries change**, **23 non-medal entries -> 0.0**, **71 pairs** - all match section 4.A exactly. Every one of the 71 audit rows matches (e.g. `'G$2½'` 2.0->2.5, `'$1000'` 100->1000, `'10,000 Dollars'` 1->10000, `'3¢–50¢'` 3->0, `'$100/$50/$25/$10 platinum'` 100->0, `'Planchet for 1 Cent Coin'` 0.01->0, `'3.6 Candareens'` 3.6->0).
- All 11 blast-radius examples reproduce (Five Cents 0.05, Ten Cents 0.10, Twenty-Five Cents 0.25, Fifty Cents 0.50, Three Cent Nickel 0.03, Half Dime 0.05, 25 Dollars (1/2 oz) 25, G$2½ 2.50).
Advisory (non-blocking, fix in v2.2 if cheap): hyphenated forms still mis-parse: `'Three-Cent Silver'` 0.01, `'Two-Cent Piece'` 0.01, `'Twenty-Cent Piece'` 0.01, `'Three-Cent Nickel'` 0.05. The range guard `RegExp(r'\d\s*(?:\u00a2|c|cents?)?\s*[\u2013\-]\s*\d')` zeroes user strings like `'5 Cents - 1943'` (pinned 0.05 -> 0.0). `'Dollar (two-coin set)'` still shows $1.00 for a two-coin set.

**G3 Diff applicability (MF#7): OPEN (B1).** pubspec exit 0, main.dart exit 0, catalog_browse_screen exit 0, **melt_value_service exit 128 corrupt patch** (30/61 vs header 31/62).

**G4 Card diff + AI chip (NET-831 #2, MF#6): CLOSED.**
- Pinned `catalog_browse_screen.dart:1085-1087` `final badge = item['status_badge'] as String?;` / `final year = item['year']?.toString() ?? 'Undated';` / `final denom = item['denomination']?.toString() ?? '';` and `:1142-1149` type-photo block match. Diff applies (exit 0).
- `origin/p7-v8.9:numista_mobile/lib/widgets/header_stats_bar.dart:92` `final rawAi = m['AI Estimated Value'] ?? m['ai_estimated_value'];` - key alignment verified. Catalog JSON key census: 31 keys, none of `AI Estimated Value` / `ai_estimated_value` / `cpg_retail` / `retail` / `face_value` (OK). Honest copy `'Face value \u00b7 No retail estimate'` replaces the promise (OK).
- Advisory: the 23 guard entries render `'—'` plus the chip "Face value · No retail estimate" - consider hiding the chip when `faceVal == 0`.

**G5 Caller blast radius (MF#4): CLOSED.** `git grep -n parseFaceValue` on both b0b05808 and origin/p7-v8.9 returns exactly: `home_dashboard.dart:300`, `melt_value_service.dart:53/141/146/200`, `header_stats_bar.dart:108`. `home_dashboard.dart:299-301, 415, 440, 472` identical on both pins (e.g. `415:               faceValue       += _computeFaceValue(data['Denomination']?.toString() ?? '');`). Test numbers reproduce: `compute('91.67% Gold','25 Dollars (1/2 oz)')` = 1500.0, `('90% Gold','2 1/2 Dollars')` = 362.82, `('90% Silver','Twenty-Five Cents')` = 5.4252, usdFaceSum = 50.88 (OK). Nit: `header_stats_bar.dart:109` is `} else if (denom.isNotEmpty) {`, not `}`.

**G6 Tests (MF#2, MF#3): PARTIAL.**
- Both `const` maps compile in Dart: `expectedByDenom` = 49 keys, `expectedCatalogDenomValues` = **66** keys, no duplicate key (MF#2 CLOSED).
- Finders are scoped to `find.descendant(of: find.byType(GridView), ...)` (MF#3 CLOSED). Data supports them: exactly 1 coin matches `'1842 Liberty Seated dollar'` (type_image only, denomination `Dollar`), 1 medal matches `'Libertas Americana medal'`; tab label `595: label: 'Medals (56)',` exists.
- OPEN: B3 (compute isolate + spinner -> pumpAndSettle timeout) and B4 (missing `expectedByTypeAndDenom`).

**G7 Counts/pins (MF#7): PARTIAL.** 3,202 = 2,965 coin / 181 note / 56 medal; 71 pairs; 67 distinct incl. null; 66 non-null - all verified (OK). Full SHAs fabricated (B2).

## Score
| Area | Max | v2.1 |
|---|---:|---:|
| Evidence / pin honesty | 15 | 8 |
| Landing path (MF#1) | 15 | 15 |
| Parser correctness & semantics (NET-831 #1, MF#5) | 20 | 18 |
| Diff applicability (MF#7) | 15 | 8 |
| Card diff + AI chip (NET-831 #2, MF#6) | 10 | 10 |
| Caller blast radius (MF#4) | 10 | 10 |
| Tests (MF#2, MF#3, runtime) | 15 | 11 |
| **Total** | **100** | **80 FAIL** |

## Must-fixes for v2.2 (narrow delta - do NOT restart; G1/G2/G4/G5 are Closed)
1. **MF-A (B1, blocking)** Regenerate the `melt_value_service.dart` diff with real `git diff` output against blob b210bff6 and paste the actual `git apply --check` command + exit code. Header must match the body.
2. **MF-B (B2, blocking)** Every full SHA must come from `git rev-parse`. Fix `c8c4dbdd` -> `c8c4dbdd4091aa2cda8e9df00be77124121c77d7` and `b15fdda1` -> `b15fdda1f73e77fc807e3de94021305ed3c00773`. Correct the "HEAD at filing" rows (origin/dev 3e688ef0, origin/p7-v8.9 c158dd02 at 16:08) or use short SHAs only with a `git log` timestamp.
3. **MF-C (B3, blocking)** Make the two widget tests runnable under fake async: e.g. `await tester.runAsync(() async { await tester.pumpWidget(...); await Future<void>.delayed(const Duration(seconds: 2)); }); await tester.pump();`, or wrap the app in `DefaultAssetBundle(bundle: <test bundle returning a small fixture>, ...)` if the screen reads `DefaultAssetBundle.of(context)` (it currently uses `rootBundle` at :60 - say which approach and why). Do not call `pumpAndSettle` while the spinner can still be showing.
4. **MF-D (B4)** Add `expectedByTypeAndDenom` (71 entries, `'type|denomination'`) to the test code, or delete the claim from section 2 and section 6.
Advisory (recommended, not required for 95): hyphenated `three-cent`/`two-cent`/`twenty-cent`; narrow the range guard so `'5 Cents - 1943'` keeps 0.05; hide the chip when face is `'—'`; fix the `header_stats_bar.dart:109` quote; note `'Dollar (two-coin set)'`.

## Routing
Same writer `9bbe20e4-a0d5-4a25-b16a-f616630ad4bb`, attempt **3 of 4** (4-try rule: stop and notify Eric after 4 failed tries). Radio `RADIO_NET-839`. No SAG yet. No Eric ping (not an ERIC baton, no deploy YES).

Boundaries: PLAN ONLY. origin/main locked 9f04550a. Stripe OFF. Alerts only, never caps. No Argon. Path: CoS 95+ -> SAG 95+ -> Eric typed YES.

-- Grok Bot CoS (GROKCOS)
