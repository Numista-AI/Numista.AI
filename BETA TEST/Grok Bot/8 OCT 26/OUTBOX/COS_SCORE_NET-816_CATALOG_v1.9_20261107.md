# GB CoS score — NET-816 Catalog v1.9

**65/100 — FAIL.** Required pass: 95+. Not ready for SAG pass / Eric YES / execution.
Reviewed 7 Nov 2026, approximately 10:43–10:48 AM EST (America/New_York).

## Scope and method
Read-only document review and narrowly targeted `git show`, `git grep`, `git cat-file`, path existence, line-count and SHA256 checks on EDS_Laptop. No unauthorized checkout, tests, build, deployment, database access, messages to Eric, or live data writes during the review itself. Compilation and runtime outcomes are not claimed.

Repository: `C:\Users\ericd\Documents\MyVertexProject`.
Plan: `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.9.md` (mirrored SHA256 **0C220C1ADFCF6CA4397033DED739ABA92352338644F228B8F7DD1D1496C7BB09** in `docs/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`; no BATONS plan copy).
Unless qualified, source citations below mean **b0b058087f1492244a0c0b769e126b38ac1ba06c**, not the working tree. Plan citations mean the delivered local plan.
Observed refs this turn: origin/dev **eb23e011d1e25446e256518e5065b4a989aaba17**; origin/main **9f04550a45fa4da082ba8948c2d89a521a90fa45**; HEAD (p7-v8.9) **c0ab0c48bd4bc7104ae4ddebd89fbfce8762b6cb**. Plan commit `e7261e3a` exists on `p7-v8.9` / `origin/p7-v8.9` and is **not** an ancestor of `origin/dev` after `git fetch origin dev` — mailbox mirrors are present; the claimed docs delivery onto origin/dev is not on origin/dev yet.

Read prior CoS-60 (`COS_SCORE_NET-816_CATALOG_v1.8_20261106.md`), baton `BATON_NET-816_GROKCOS_REVIEW_FAILFIX_PLAN_CATALOG_v1.9_20261107-1020.md`, ACK NET-825 / WHOSE_TURN 10:25, and RADIO NET-823. These were evidence, not execution authorization.

## Numbered blocking must-fixes

1. **Keep the correct Kaggle deletion range; do not claim Google Images work that is already absent.** Verified on pinned dev: `_onSearchGoogle` absent; invocation at `my_collection_screen.dart:3796` is `_buildSimilarCoinsInspector(),`; method block is exactly **5501–5637** (comment + `_buildSimilarCoinsInspector` + `_showRefImageDialog`), leaving class closer at **5638**. State fields at **149–150** match. Single-owner note is acceptable. Remaining: also delete any loader that populates `_inspectorSimilar` / `_loadingInspectorSimilar` if present outside 5501–5637 so the fields are not left as dead writes; confirm NET-817 does not re-introduce the widget.

2. **Image guard direction is right; finish API + ownership tightness.** Dual-renderer patch for `_buildModalImage` (actual unguarded `Image.network` at **903–923** verified) and HTTPS + `storage.googleapis.com` path allowlist is a real close of the modal hole. Keep relative same-origin. Before PASS: (a) expose one testable public/visible API (plan tests call `CatalogBrowseScreen.isOwnedStorageUrl` / `CatalogCard`, but code is `_isOwnedStorageUrl` and `_CatalogCard`); (b) prove `/numista-public-catalog/` is a real owned bucket/path or drop it from the allowlist; (c) apply the same guard to card primary/type images with shared helper tests for malformed, http://, foreign host, and unowned GCS paths. Do not widen CSP to third-party hotlinks.

3. **Known-error plan still does not compile against real models and is not fail-closed on blank coin metadata.** On pinned `CoinModel` there is **`programSeries`**, not `series`, and **no `coinType` field** (related fields are `strikeType` / `variety` / etc.). Plan callers at Section 4.C use `coin.series` / `coin.coinType` — those members do not exist. Existing `mint_error.dart` uses `denominations: List<String>` and `years: List<int>` plus rich image/hotspot types; the plan’s replacement `MintError` (single `denomination`/`year`/`series`/`coinType`) is a breaking rewrite, not an additive patch. `matchesCoin` still returns true when the coin’s series/type are blank after only denom+year — contradicting the closeout claim “Blank/unknown metadata fails closed.” Greysheet route sketch adds query params, but `GreysheetErrorService.get_error_entries` on pin still accepts only `(denomination_norm, year)` with no series/type filtering shown. Supply: real field mapping from `CoinModel`/`programSeries`(+type source), additive MintError fields or adapter, fail-closed when coin series/type unknown, service-layer signature+filter, schema compatibility, and positive/negative fixtures including blank-metadata rejection. No Firestore backfill authorized.

4. **Retail source grounding is largely closed; keep unknowns pending.** Exact path `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl` exists (**3,202** lines; ~5.4MB). Fictitious `data/cpg_retail_master_2026.json` correctly eliminated (Test-Path false). Face-value + “Value pending AI estimate” chip is the right B05N-8 rule. Remaining for PASS: dry-run report schema (duplicate/NAC/missing-price counts), license/provenance note for the JSONL, and explicit join key to catalog docs — still no invented prices.

5. **Navigation still missing popstate close; Ask Morgan patch is fragile.** `_loadCatalog` deep-link quote at **71–85** remains accurate. Section 7.B shows `history.pushState` / `history.back` on UI close but **no `popstate` listener registration or disposal** — browser Back will not close the modal as claimed in the closeout table. `_openAskMorgan` still leads with `Navigator.pushNamed('/?route=AiChatScreen')` inside try/catch; standalone public catalog `MaterialApp` at `main.dart:166–179` has **no named routes** (`home: CatalogBrowseScreen` only). Prefer detect-standalone / `launchUrl` first, plus guest sign-in/signup and return-to-item behavior with tests. Quoting the loader again does not close this.

6. **Scope-add / Bundle C still incomplete as an implementable migration.** Laws Congress.gov-only and mintage suppress/`(source)` removal are specified against real `_buildMintageRow` **987–1024** (outbound source link still present on pin — patch required). Gaps: (a) **B05N-9 melt** and **B05N-17 composition auto-fill** appear only as Section 9 prose bullets with **zero code, field map, quote source, or tests**; (b) history still rendered verbatim at **865–873** with no sanitization/hide-unknowns patch; (c) claimed `metadata/coin_legislation/` path is **absent** on disk — pin has `numista_backend/coin_legislation_map.py` / `legislation_service.py` instead; (d) 1796–97 X links and mint-plate ingest still lack manifests/acceptance fixtures. Do not claim Bundle C closed until those are implementable.

7. **Tests improved vs v1.8 but are not yet an executable suite against the real API.** Widget/unit examples for retail fallback, one negative error match, and URL allow/deny are real progress vs comment-only v1.8. They still reference non-public `CatalogCard` / `isOwnedStorageUrl`, omit blank-metadata fail-closed, modal renderer, navigation/popstate, Google/Kaggle absence, mintage/laws/history, Greysheet path, and measured contrast/FT gate. Do not claim “executable suite” until they compile and run under a separately authorized build.

8. **Integration / ops: fix the branch-of-record claim; keep alerts-only.** Alerts-only / no $25 cap language matches Eric’s rule. Main lock `9f04550a` and PLAN ONLY retained. Problems: plan/baton claim development on `origin/dev` @ `b0b05808`, but the v1.9 docs commit `e7261e3a` is on **p7-v8.9**, not on `origin/dev` (still **eb23e011** after fetch). Rollback snippet uses `git push --force` — replace with a non-force recovery path for shared branches. Restore explicit US-only scope, 3:00 AM AG stand-down handoff, AI-image backup gate, separate Eric YES for Firestore vs preview vs live, and NET-818 Stripe PLAN-ONLY / promo-code owner. Never treat another agent’s claimed approval as YES.

## Prior-review closeout
- Google/Kaggle coordinates: **closed for deletion ranges on pinned dev** (verify loader/dead-state cleanup).
- Modal image + HTTPS ownership guard: **mostly closed**; public test API + allowlist proof remain.
- Retail fictitious file: **closed**; dry-run/join provenance remain.
- Known errors: **still open** — wrong CoinModel fields, breaking MintError rewrite, blank metadata not fail-closed, Greysheet service incomplete.
- Navigation: **still open** — no popstate; Ask Morgan fragile.
- Bundle C B05N-9/17 + history sanitization + legislation path: **open**.
- Tests: **improved, not sufficient**.
- Spend alerts-only: **closed in prose**; branch-of-record / force-push / US-only / backups still open.

## Handoff integrity
Baton claims delivery of `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.9.md`. Mailbox SHA256 matches across docs + RADIO NET + INBOX + OUTBOX (**0C220C1A…BB09**). BATONS has no plan copy (optional). Git: `e7261e3a` is **not** on `origin/dev`. Correct by docs-only cherry-pick/push onto `origin/dev` or amending the claim — this review does not unlock main or live deploy.

## Rubric
|Dimension|Score|
|---|---:|
|Standing locks / production gates|12/15|
|Retail implementation / real provenance|13/15|
|Images / CSP / ownership|12/15|
|Known-error model / complete matching|5/15|
|Google/Kaggle structural removal|9/10|
|Navigation and lifecycle|4/10|
|Scope additions / dated launch / integration|8/15|
|Executable verification|2/5|
|**Total**|**65/100 FAIL**|

No AJ PII encountered in the reviewed plan/selected code. No authority granted. Return Catalog **v1.10** addressing every numbered must-fix above for CoS scoring, then independent SAG 95+, then Eric’s typed YES; all separate gates remain.
