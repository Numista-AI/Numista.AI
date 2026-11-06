# SAG SCORE — NET-815

- Reviewer: Stand Alone Grok through xAI API, model grok-4.7
- Date: 2026-11-05, America/New_York
- Method: independent review of plan text plus real repository excerpts; CoS score not supplied
- API response id: streamed
- Mode: SCORE ONLY; no execute, deploy, Firestore, main, or Stripe changes

## SAG_SCORE: 67/100 FAIL

## MUST_FIX
1. B05N-14 does not compile and does not require same series and type. `MintError` (fields through `isPublished`, `fromFirestore` at lines 150–176) has no `series` or `coinTypes`. Plan §10 calls `e.series` and `e.coinTypes` anyway. `widget.coin.series` / `widget.coin.type` are not evidenced; live `_loadAll` only reads `denomination` and `year` (dev coin detail 3504–3531). The filter still matches on year alone when those lists are empty (`if (!seriesMatch && e.series.isNotEmpty)` then `return e.years.contains(year)`), so unknown series/type does not fail closed. `_fetchLibraryErrors` is still `(denom, year)` while the call site passes four args. Greysheet only appends query params; no server filter is specified. No model/parser update.

2. Image host guard is in the wrong scope. §3.B declares `static const _allowedImageHosts` and `_isAllowedImageUrl` with no class. `static` is illegal at library top level. §8.B’s `_CatalogCard` (separate class from line 1069) calls `_isAllowedImageUrl` but does not define it. That call is an undefined identifier. CSP citation at `firebase.json` 283–284 is correct; the guard as written is not.

3. Retail chip patch does not compile and fails B27-11. `valCpg` is `double?`. `hasValidRetail` does not promote it, so `valCpg.toStringAsFixed(2)` in §8.B is invalid (`rawUrl!` shows the author knew a bang was needed). Chip is 11px `#B78103` on `#FFF8E1` (3.21:1), not WCAG AA 4.5:1 and not gold/black. `scripts/migrate_catalog_cpg_retail.py` names no source file, schema, or NAC join. Ground truth still has 3,202 entries and zero `cpgRetail` keys.

4. B05N-15 / B27-8 removal is not an applicable patch. Real Google Images widget continues past line 3538 (style still open at 3539–3545). “DELETE LINES 3531–3538” leaves a syntax error. Inspector already returns `SizedBox.shrink()` when not loading and empty (5550–5551), so the proposed empty-state text is unreachable and the spinner at 5570–5578 plus Kaggle caption at 5638–5641 stay. Those citations are from the p7 collection/ref-image files; execution is pinned to `origin/dev`, and the p7 cherry-pick list does not include these deletions.

5. Deep-link “verbatim” code is not the file. Real lines 71–82 match only `nac_code`, `orElse` returns `<String, dynamic>{}`, test `match.isNotEmpty`, and show the modal in a post-frame callback. Plan §2 and §4 quote `id` matching, `orElse: () => null` (type error on `List<Map>`), and a direct `_showItemDetailModal` during load. `window.history.pushState` / `popstate` is not Dart.

6. Verification commands do not test anything. Repo has `test/catalog_browse_test.dart`, not `test/catalog_browse_screen_test.dart`, `test/mint_error_matching_test.dart`, or `test/no_external_links_test.dart`. Plan includes no assertions. “Verified tests” is false.

7. Ask Morgan navigation does not fit the catalog app. `dev_main.dart` 166–179 runs `CatalogBrowseScreen` in a `MaterialApp` with no `routes`. §5 still `pushNamed('/collection')`; guest `/login` and `/signup` links are unspecified against that app.

## NON_BLOCKING
Spend runbook correctly marks the $20 Pub/Sub cap UNBUILT and does not run shutoff during review. Backup operator must be a human with GCP access, not an agent standing in for Eric. `git revert <execute commit set>` back to `b0b05808`, without checking out `18a8b8e5` or locked main `9f04550a`, is a valid rollback; the prose file list omits B05N files, but revert of the commit set would cover them. Allowlist hosts `numista.ai` / `numista-vault.web.app` are not explicit CSP `img-src` hosts (fail closed, not a leak). `ref_image_widget.dart` doc lines 6–9 still say `assets/kaggle/`. Microscope line 1335 and catalog lines 128–130, 209–214, 223–228, and 599–603 were not in the reviewed excerpts.

## PII_FINDINGS
NONE

## PLAIN_ENGLISH
This plan correctly names the dev branch, the real catalog card, and a safe way to undo the work, but the proposed code would not build. The image check is not attached to the card class, the known-error fix uses fields the error record does not have and can still match the wrong coin, and the new gold “Valuation Pending” label is too low-contrast. Do not treat this as ready for a typed YES until those patches are rewritten against the real files and real tests exist.

## RATIONALE
67/100 FAIL. Requirement 1 partial: retail UI is aimed at `_CatalogCard.build`, but the snippet does not compile, fails B27-11, and the JSON migration has no source. Requirement 2 partial: CSP lines 283–284 and `primary_image`/`type_image` are right; the host guard is an undefined cross-class call. Requirement 3 / B05N-14 failed: missing model fields, unguarded year match, caller signature gap, no tests. Requirement 4 / B05N-15 / B27-8 failed as an executable removal: short delete range, dead empty-state, p7-vs-dev gap. Requirement 5 passed: cap is honestly unbuilt and the manual runbook is present. Requirement 6 passed on pin `b0b05808` and revert-not-checkout; the deep-link citation “correction” failed because the quoted code is not the file.
