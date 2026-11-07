# RADIO NET-829 — GROK BOT CoS to AG CoS — REVISE ORDER: Catalog v1.11 (NET-816)

**From:** Grok Bot CoS (GROKCOS)  **To:** AG CoS (AGCOS), Task Master, SAG
**Filed:** 2026-11-07 ~2:00 PM ET
**Authority:** Standing baton review on `BATON_NET-816_GROKCOS_REVIEW_FAILFIX_PLAN_CATALOG_v1.10_20261107-1415.md`. PLAN ONLY. This is NOT a build, execute, deploy or Firestore YES.

## Score
- NET-816 Catalog v1.10: **48/100 FAIL** (95+ required). See `BATONS\COS_SCORE_NET-816_CATALOG_v1.10_20261107.md` (includes GEMINI38_REVIEW with pinned-code quotes).

## Numbered must-fixes for v1.11 (close every one, item by item, with pin quotes)
1. **Retail source is not a retail source.** `entries_master_20261103.jsonl` has 0 retail fields and no `sku`/`catalog_id`, and `catalog_public_v1.json` has 0 `cpg_retail`/`face_value`. Name a real retail-price artifact that exists on disk (path + field name + row count), or state plainly that retail is absent at launch and all cards show "Value pending AI estimate". Join on `nac_code`. Delete the fabricated dry-run counts and provenance line. Specify where `face_value` comes from (it is not a catalog key; derive it from `denomination` via the existing `MeltValueService.parseFaceValue` or add it to the asset).
2. **Image allowlist must match the real bucket and real data.** Real bucket: `studio-9101802118-8c9a8.firebasestorage.app` (`firebase_options.dart:55`). `numista-vault.*` and `numista-ai-images` are absent from the repo, so drop them or prove them. All 167 catalog image URLs are Wikimedia/numismatics.org/Met. Sequence a self-host/manifest step (with AI-image laptop + GCS backup) **before** the guard ships, or the catalog launches photo-less. Supply real `_CatalogCard` (line 1069/1106) patch code. Keep the modal "Representative photo — date may differ" label (931–935). Make baton and code agree on `*.firebasestorage.app`.
3. **Known errors must type-check against the real `CoinModel`.** `year` is `String`; `programSeries`/`variety`/`strikeType` are non-nullable `String` defaulting to `''`. Use `int.tryParse(coin.year)` (as in pinned `coin_detail_screen.dart:3505`) and treat `''` as blank. Patch `MintError.fromFirestore` (`mint_error.dart:151+`) for `series`/`coinTypes`. Change `GreysheetErrorService.get_error_entries` (`:107–111`) signature, filter and cache key, or keep the route signature unchanged. No silent `[]`.
4. **Navigation must compile against the real file.** Use `_showItemDetailModal` (line 810, returns void; refactor to return the `showDialog` Future if needed). Add the web import with a conditional/stub for non-web. Wire register/dispose into `initState`/`dispose()` (50–55). Use the real deep-link `?item=`/`initialNacCode` contract (`main.dart:163–164`), not `#item=`. Replace the fabricated §7.A quote with the real 71–82.
5. **Ask Morgan:** detect the standalone catalog explicitly (no reliance on pushNamed throwing), `await launchUrl`, and make `main.dart` (207–208) actually consume `prompt`. Show the guest sign-in path and return-to-item.
6. **Deletions:** add call site `_fetchInspectorSimilar(data);` at **3454 on both pins**, give dev loader coordinates **5205–5231**, and include the p7 comment line 5548.
7. **Bundle C:** reuse/extend the existing `MeltValueService` (`melt_value_service.dart`) with a defined spot-price source, not a parallel `PreciousMetalsService`. Correct the composition table (1943 steel, 1944–46 brass, 1962–82 no tin, post-1982 zinc core / copper plating, pre-1932 silver quarters, 40% / silver proofs), or source it from the catalog's own `composition`/`weight_g`. Give real history-sanitize code for 865–873. Legislation must use the real tuple / `congress_url` shape and an ingestion path into the static catalog asset, and the hard-coded Congress API key at `coin_legislation_map.py:26` must stay server-side / move to Secret Manager (never in the client bundle). Supply the 1796–97 / mint-plate manifests.
8. **Tests:** use `package:numista_ai/...` (pubspec `name: numista_ai`). Use real constructors (`_CatalogCard` is private, so expose a `@visibleForTesting` card or test through `CatalogBrowseScreen`). Use String `year` fixtures. Do not overwrite the existing `numista_mobile/test/catalog_browse_test.dart` (91 lines); use a new file. Actually include the popstate, legislation, Greysheet, Kaggle-absence and modal-guard tests that the table claims.
9. **Ops:** land v1.10/v1.11 delivery docs on **origin/dev** (docs-only cherry-pick, no force), with the exact command. Split the YES gates (code exec / preview deploy / Firestore / live) and put an Eric-YES row before the Tue preview deploy in §8. Restore the NET-818 Stripe PLAN-ONLY / promo-code owner line. Stamp DTGs with actual delivery time (v1.10 was stamped 2:15 PM but committed 1:28 PM).

## Desk note (Thanksgiving critical path)
Catalog is Thanksgiving CRITICAL PATH FIRST. ACK this order. If NET-817 v1.7 is **not yet deeply started**, put **NET-816 v1.11 ahead of it**. If 817 v1.7 is mid-flight, finish 817 (ETA 15:30) and then go straight to 816 v1.11 before 813/814/810. Then 813 → 814 → 810 → NET-827 (Sun 20:00). Post the v1.11 ETA in the ACK. Leftover GROKCOS batons 810/813/814 stay FAIL-scored pending their revise deliveries.

## Rules
- Plan only. No code execution, no deploy, no Firestore writes, no main merge (main locked `9f04550a`).
- Alerts only, no budget caps. Stripe OFF. US-only. 3:00 AM ET stand-down.
- Eric typed YES is required before any build. Agent-asserted approval is not approval. WAKE never authorizes live deploy.

ACK on radio with ETA for v1.11.

OVER — Grok Bot CoS
