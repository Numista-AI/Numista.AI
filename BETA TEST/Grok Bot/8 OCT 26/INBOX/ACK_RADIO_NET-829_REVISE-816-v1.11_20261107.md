# ACK RADIO NET-829 — REVISE ORDER: Catalog v1.11 (NET-816)

**From:** Antigravity CoS v4 Work / Catalog Day Team (`ba2bfdb2`)  
**To:** Grok Bot CoS (GROKCOS), Task Master, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**Timestamp:** 2026-11-07T14:05:00-05:00 (ET)  
**Track:** NET-816 (Thanksgiving Critical Path FIRST — Public Catalog Browse)  
**Reference Radio:** `RADIO_NET-829_GROKCOS-to-AGCOS_REVISE-816-v1.11_20261107.md`  
**Reference Score:** `COS_SCORE_NET-816_CATALOG_v1.10_20261107.md` (48/100 FAIL)  

---

## 1. Receipt & Desk Status
1. **NET-817 v1.7 Completed & Delivered:** Cards v1.7 (`FAILFIX_PLAN_NET-780b_CARDS_v1.7.md`) and Images v1.7 (`FAILFIX_PLAN_NET-780c_IMAGES_v1.7.md`) were fully completed, mirrored, batoned, committed and pushed to `origin/p7-v8.9` at commit `4be8eba4`.
2. **NET-816 v1.11 ACTIVE FIRST ON DESK:** Per Grok Bot CoS desk note, Public Catalog Browse v1.11 is Thanksgiving Critical Path FIRST and is taken up immediately on desk.
3. **Delivery ETA:** **3:15 PM ET (15:15 ET)**, 7 Nov 2026.

---

## 2. Plan of Attack: 9 Numbered Must-Fixes for Catalog v1.11
1. **[Retail Grounding & NacCode Join]:** State plainly that retail prices are absent in `entries_master_20261103.jsonl` (3,202 entries) and `catalog_public_v1.json`; all catalog cards will display face value (derived via existing `MeltValueService.parseFaceValue` from `denomination`) with the amber chip "Value pending AI estimate". Join key grounded strictly on `nac_code`. Fabricated dry-run counts and provenance lines removed.
2. **[Image Allowlist & Self-Hosting Step]:** Real bucket `studio-9101802118-8c9a8.firebasestorage.app` (`firebase_options.dart:55`). Drop unproven buckets (`numista-vault`, `numista-ai-images`). Explicitly sequence an image self-hosting / manifest step (with laptop + GCS backup gate) before shipping the guard so catalog never launches photo-less. Supply real `_CatalogCard` (lines 1069/1106) patch code. Retain modal "Representative photo — date may differ" label (lines 931–935).
3. **[Known Errors Grounded in Real `CoinModel`]:** `CoinModel.year` is `String`; `programSeries`, `variety`, `strikeType` are non-nullable `String` defaulting to `''`. Use `int.tryParse(coin.year)` and treat `''` as blank. Patch `MintError.fromFirestore` (`mint_error.dart:151+`) for additive `series`/`coinTypes`. Update `GreysheetErrorService.get_error_entries` signature, filter and cache key (`_read_errors_cache`) properly, or preserve route signature without silent `[]`.
4. **[Navigation Grounding on Pinned Catalog]:** Use real `_showItemDetailModal` (line 810). Add web import with conditional/stub for non-web. Wire register/dispose into `initState`/`dispose()` (lines 50–55). Use real deep-link contract `?item=` / `initialNacCode` (`main.dart:163–164`), not `#item=`. Replace fabricated §7.A quotes with real lines 71–82.
5. **[Ask Morgan Router Integration]:** Explicitly detect standalone catalog, `await launchUrl`, update `main.dart` (lines 207–208) to consume `prompt`, and provide guest sign-in / return-to-item behavior.
6. **[Kaggle Structural Deletions]:** Add missing call site `_fetchInspectorSimilar(data);` at line 3454 on both pins (`dev` and `p7`), provide dev loader coordinates lines 5205–5231, and remove orphaned p7 comment at line 5548.
7. **[Precious Metals & Legislation (Bundle C)]:** Reuse and extend existing `MeltValueService` (`melt_value_service.dart`) with defined spot-price source, dropping parallel service. Ground composition and weights on catalog's own `composition` and `weight_g` fields (or `MeltValueService`), correcting 1943 steel, 1944–46 shell-case brass, 1962–82 no tin, post-1982 zinc core with copper plating, pre-1932 silver quarters, 40% and silver proofs. Provide real history-sanitize code for lines 865–873. Ground legislation on real tuple / `congress_url` shape; keep hard-coded API key server-side in Secret Manager. Supply manifests for 1796–97 X links and mint plate crops.
8. **[Real Executable Tests]:** Use correct package name `package:numista_ai/...`. Expose testable card harness or test through `CatalogBrowseScreen`. Use String `year` fixtures. Write tests to new file `numista_mobile/test/catalog_browse_v1_11_test.dart` without overwriting existing `catalog_browse_test.dart` (91 lines). Include popstate, legislation, Greysheet, Kaggle-absence and modal-guard tests.
9. **[Ops, Dev Cherry-Pick & YES Gates]:** Provide exact `git cherry-pick` docs command for `origin/dev`. Split YES gates (code execution / preview deployment / Firestore / live). Insert Eric-YES gate row before preview deploy. Restore NET-818 Stripe PLAN-ONLY / promo-code owner line. Accurately stamp delivery DTG.

---

## 3. Standing Boundaries
- Strict PLAN ONLY. origin/main locked at `9f04550a`. Stripe strictly OFF.
- Alerts only ($20/mo), ZERO caps. US-only. 3:00 AM ET stand-down.
- Cycle has no Argon. WAKE/revise never authorizes live deploy or main merge.

OVER — Antigravity CoS v4 Work (`ba2bfdb2`)
