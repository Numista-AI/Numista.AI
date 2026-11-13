# BATON NET-815 — To: AG CoS v4 — PLAN ONLY: Catalog FAILFIX v1.7 (CoS 64 / SAG 74 FAIL on v1.6)

Source: GB CoS, 5 Nov ~6:10 PM ET. Thanksgiving CRITICAL PATH. Argon 99 PASS; CoS **64 FAIL**, SAG **74 FAIL** after real-code review.
Scores: `COS_SCORE_NET-811_FAILFIX-777-v1.6_20261105.md`, `SAG_SCORE_NET-811_FAILFIX-777-v1.6_20261105.md`.
Deliverable: `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.7.md`. Take before all noncritical work. PLAN ONLY; Eric YES blocked.

## Verified OK — preserve, do not regress

1. **Rollback:** `b0b058087f1492244a0c0b769e126b38ac1ba06c` is confirmed current origin/dev HEAD. Complete future execute-commit `git revert` back to that real pre-execute state plus named Hosting release/channel restore is valid. Never restore from 18a8b8e5 or locked main 9f04550a.
2. **Mintage:** proposed plain-text `val` / `label` snippet correctly drops `sourceUrl`, `InkWell`, `launchUrl`, and undefined `sourceInstitution`. Keep as SPECIFIED, not already done.
3. Foreign Coins removal, era reset, flag-only pre-federal intent, existing `initialNacCode`, and Morgan constructor remain grounded. Correct deep-link citation to 71–81 rather than 68–75.

## Blocking must-fixes

1. **Retail must attach to the real card.** Dev loader lines 58–63 loads `catalog_public_v1.json`; grid creates `_CatalogCard(item: item)`. Actual card lines 1079–1150 has no `cpgRetail`, `valCpg`, `fmt`, or `Valuation Pending`. Patch `_CatalogCard.build`, not isolated pseudocode. Define sourced migration/fallback from real JSON (currently 3,202 entries, zero `cpgRetail`) and reject wholesale. Tests: positive numeric/string retail always wins over pending; zero/missing gets pending; no AI/melt/cost/wholesale fallback.
2. **Close the real image path.** JSON uses `primary_image` / `type_image` maps, not `primary_image_url`. There are 167 external primary URLs (155 upload.wikimedia, 10 thumb.wikimedia, 1 Met, 1 ANS), and card lines 1105–1109 feeds `imgMap['url']` directly to `Image.network`. Specify migration and strict pre-fetch host/path guard; reject before fetch and use the actual placeholder. AI only labeled `ai_replica_images`, never primary/type/card/index. Correct CSP cite: 275–276 is HSTS; actual CSP is 283–284. Do not claim external images are internal-only acquisition notes when the card renders them.
3. **B05N-14:** add same coin type AND series matching to `MintErrorService.getErrorsForCoin`, `_KnownErrorsTab`, and Greysheet request/filter path. Empty years/unknown series must fail closed, not match any coin. Add regression proving a 1999 NJ state-quarter clipped-planchet example cannot appear on a 1958 Washington quarter; include positive same-series case.
4. **B05N-15:** remove Google Images button and `_onSearchGoogle` external action from `my_collection_screen.dart` (3531–3538, 4387–4405), Similar/Kaggle panel (5560–5639), and Kaggle label/fallback in `microscope_scan_screen.dart:1335` and `ref_image_widget.dart:47`. No off-site photo action. Add regression tests for all Inspector/clone surfaces and a bounded terminal state instead of indefinite spinner.
5. **Spend readiness:** manual Hosting disable/channel delete is only a valid proposed shutoff, not a functioning alert system. Label automated $20 email unbuilt until provisioned/tested. Supply pre-ad runbook: verified budget/resource mapping, test notification, one accountable human plus backup, monitoring cadence, command verification and incident evidence. Do not execute shutoff in plan review.
6. **Branch:** choose dev only, or give exact integration of dev b0b05808 catalog screen, asset bundle, `/catalog` known path and Hosting rewrites into p7-v8.9 without clobbering newer work. Current p7 has none of these and renders NotFoundScreen for `/catalog`. Rollback must use the actual pre-execute SHA of the chosen branch.

Locks: origin/main 9f04550a, Stripe OFF, zero execute/deploy, zero Firestore writes/rules, no external messages, no AJ/collector PII, money items after launch. No secrets in artifacts.
Chain: AG -> GB CoS (95+) -> SAG (95+) -> Eric typed YES. (Argon dropped Eric YES 6:07 PM ET 5 Nov FIN OPS; file GROKCOS_REVIEW on DONE.)
