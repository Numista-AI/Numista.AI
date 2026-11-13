# GB CoS independent score — NET-814 Soft-404 / Public Catalog / Pricing v1.7

**88/100 — FAIL. PASS requires 95+. Not ready for SAG approval, Eric YES or execution.**

Reviewed Sunday 8 November 2026, morning ET (America/New_York). Fresh-writer attempt 1; writer self-score ignored. Full plan, RADIO_NET-854, previous COS_SCORE v1.6, and current baton read. Static/document review only. No code, tests/builds, Firestore, deployment, pushes, forms, or outside sends executed.

## Artifact integrity and pins
- `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.7.md`, 58,097 bytes.
- SHA-256 `dd462ae5ba72b29f398bdc8be677335098416b209aaf076f79ae9bcdabcc7d84`, matches baton and byte-identical `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.7.md` mirror.
- Source inspection used git show at actual pin **4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235** and dev **bde8b402d34675a39f2b3b4e872cb46f71a5b32a**, not dirty working files.
- Main remains **9f04550a45fa4da082ba8948c2d89a521a90fa45**, locked.

## Prior CoS-90 closeout
- E1 CLOSED: 1921-P Morgan sample no longer emits og:image* or twitter:image meta tags, and twitter:card is summary. Image-tag names in explanatory HTML comments are not emitted tags. Dev record has primary_image/type_image/secondary_image/extra_images all null. Name, year, denomination, series, composition and era quoted for its metadata match the record. No mintage number or CPG retail was invented in that HTML sample.
- E2 CLOSED for API/key alignment: showPublic now takes PublicCoinProjection.fromCatalogMap(item); nac_code is the real key (3,202 rows), nac occurs on zero rows. NET-813's separate nested image extraction defect still applies to that dependency.
- E3 CLOSED as a plan: production helper `lib/routing/public_catalog_route.dart` is explicitly NEW / TO BE AUTHORED, with proposed production body, main.dart import/call, and test import. It correctly does NOT claim this file exists today; git ls-tree at dev found no file. Existence is not required for a PLAN-ONLY new-file specification. Its manifest addition is in §11, although the §7.5 main table should also list it for consistency.

## Remaining must-fixes

### MF-1 — Curl cannot observe client-injected noindex
§3.3 and §3.6 specify an unknown NAC rewrites to root index.html, HTTP 200; Flutter later inserts a robots/noindex meta tag and changes browser history. §9.1 Test 2 (909–913) instead curls the raw HTML and requires that meta tag already in the served response. Curl does not execute Flutter/JavaScript.

Verified dev web/index.html: it contains the root canonical at line 23 and bootstrap at 207, but no robots/noindex tag. The plan does not specify a separately served unknown-code document. Therefore Test 2 fails for the promised architecture; the statement that crawlers necessarily see client-injected noindex is also too strong for non-JS crawlers.

Choose and state the response contract: either serve status/robots metadata for unknown codes at the response layer, or test the post-Flutter DOM/history with a real browser and explicitly retain the HTTP-200 limitation. Keep valid catalog pages indexable. Do not make the curl pass by indiscriminately adding noindex to the root shell. Preview curls prove served HTML/status, NOT main.dart dispatch or widget behavior (the §9.2 claim of end-to-end coverage needs a browser test).

### MF-2 — Private promotion is placed in proposed public pricing copy
§8.2 (line 876) includes a literal private promotion code in the proposed pricing-surface reconciliation. Standing user rule: **promo codes stay private**. Remove the code from public copy, generated pages, fixtures/screenshots and public artifacts; if needed, specify private eligibility handling with no exposed token. The literal is deliberately NOT reproduced in this score file or in the summary. Reading it here is not authorization to publish it.

Pricing/coverage assertions in §8.2 are agent-authored claims of prior approval, not approval evidence. Attach the actual founder decision reference before treating the price, grandfathering scope, or future world-coverage date as accepted marketing facts. The reviewed code only establishes the existing free-beta text, not those new commercial promises. US-only remains the operative scope.

### MF-3 — Public image guard accepts the entire private-upload namespace
§5.3 prohibits public user-uploaded photographs and requires verified reference sources. §6.4's guard nevertheless accepts ANY HTTPS object in `numista-uploads-studio-9101802118-8c9a8` and ANY object under the Firebase bucket's `/o/` namespace, without requiring approved-reference paths or a public-release/provenance gate.

Pin promote_user_photos.py distinguishes the promoted destination: BUCKET_NAME at 35, REF_PREFIX='reference' at 36, public URL emitter at 130. Merely matching a bucket does not prove an object was promoted/privacy-cleared. A private original object in that bucket would currently pass the proposed guard.

Require explicit approved reference path/provenance (and existing per-image release gates), not only host/bucket; reject private original upload paths and arbitrary traversal-like local asset paths. Add negative guard tests with a private original URL plus positive tests using an actually approved reference fixture. Align with the NET-813 projection contract rather than inventing an image for the null-image Morgan.

### MF-4 — Rollback failure does not halt before pull/push
§7.3 (793–808) pipes a while-loop and exits 1 inside that loop on ancestry failure or revert conflict, then unconditionally runs `git pull --rebase origin dev` and `git push origin dev`. That snippet has no set -e/pipefail and no check guarding the pipeline result. An exit from the pipeline's subshell is not a guaranteed exit from the outer script; a partial revert can still be pulled/rebased/pushed after failure.

Specify fail-fast shell settings plus explicit pipeline success checking (or a non-subshell loop), preflight all SHAs, and stop before any pull/push if one revert fails. Retain exact recorded track SHAs and conflict abort. No rollback commands were run. Future destructive/pushed-history changes keep their separate confirmation requirements.

## Citation audit and nonblocking cleanup
- Pin firebase.json rewrite array actually begins at **49**, first source /api/** at **51**, last source /claim/** **130**, array end **133**. Plan 90 labels a quote including rewrites as 51–133; change start to 49.
- Header array begins **135**, first rule **137**; the full quoted block extends through **280**, not 234. Line 234 begins the sitemap object, 248 is global security-header source, 280 closes headers. The quote content itself preserves the important headers; the range label is inaccurate.
- Dev catalog rewrites are object lines **133–140** (sources 134 and 138), not the exact 132–139 boundaries stated. Surgical diff labels 115/165 are illustrative offsets, not current exact pin anchors (claim source is 130; image header source is 200). State clearly that this is a merge specification, not an apply-verified patch; do not append duplicate catalog rewrites on dev, where they already exist.
- Pin firebase.json 7 confirms numista-vault is the Hosting site. Legal/tool/API rewrites and no-cache entries verified through headers 280; no catch-all SPA rewrite exists.
- Pin main.dart imports 8–19, whitelist 119–140 and unknown path 142–148 checked. Dev import 12, whitelist 133–134 and full public dispatch 154–181 match. Dev 215–245 is backend/Firebase startup/error code, not routing.
- Dev catalog_browse_screen.dart 77–82, 315, 464–467, 810–813 and 987–1017 checked. Source-link removal is a clearly proposed change, not existing text.
- Pin public_info_screens.dart 362,396,407,412 and auth_gate.dart 101–103,106–148,157–159 support the quoted existing text and public-route precedence problem. Some displayed fragments use ellipses rather than full verbatim strings; identify them as excerpts.
- Dev catalog reverified: 5,895,259 bytes; 3,202 rows = 2,965 coins / 181 notes / 56 medals; status counts 1,724 Needs source / 950 Details coming / 9 Pre-Federal / 519 null; no foreign NAC country segment; no nonnull cpg_retail. 1921-P Morgan and 1909-S Lincoln identifiers exist. No feed or join script found at either named ref: planned/to-acquire labels are honest, not delivered functionality.
- Pin emitters verified: build_image_index.py 46,55,62,303; build_currency_image_index.py 40,42,267; promote_user_photos.py 35–37,130. Public host matching is not equivalent to source approval.
- §9.3 says asset manifest but uses CWD-relative dart:io File. This can work if the test runner is explicitly rooted at numista_mobile; document that working-directory prerequisite or use the actual asset bundle. §9.2 widget tests require dev's registered assets/catalog/ (pubspec 97) and deterministic bundle/image setup. No tests were run in PLAN ONLY review.
- Update stale v1.5/attempt 3-of-4/signature wording; the fresh writer's file identity is v1.7. Such historical residue alone is not the reason for FAIL.

## Rubric
| Dimension | Score |
|---|---:|
| Ground truth, census, marketing honesty | 19/20 |
| User direction and launch fit | 16/20 |
| Routing, AuthGate, static HTML | 17/20 |
| Public privacy, values, images | 18/20 |
| Rollback, alerts-only, implementability | 18/20 |
| **Total** | **88/100 FAIL** |

PLAN ONLY; main locked; Stripe sandbox/OFF; alerts only, never caps; US-only; no AJ identifying values reproduced. No deployment/write authorization is inferred from an agent claim or from this score. CoS 95+ -> SAG reading the full plan 95+ -> Eric typed YES; writes/deploys each need separate YES. DONE review baton denotes completed scoring, NOT approval. No revision wake or outside message sent.