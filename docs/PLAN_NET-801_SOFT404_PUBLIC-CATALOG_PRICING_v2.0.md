# Architecture & Implementation Plan: NET-801 v2.0 (BATON_NET-814)
## Public Catalog Direct Route, Soft-404 Elimination, Static Entry Generation, Retail Pricing Projection & Pricing Surface Plan v2.0

**Document Tracking:** `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v2.0.md`  
**Byte-Identical Mirror:** `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v2.0.md`  
**Review Baton:** `REVISE_NET-814_v1.9_to_v2.0_VERIFIED_20261108-1155.md`  
**Date & Timestamp:** 2026-11-12 (America/New_York)  
**Pins (full SHAs, `git rev-parse`):** pin `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235`; catalog baseline `b0b05808` (identical to `cc815522` / `origin/dev` for catalog paths; replaces stale `bde8b402`); main locked `9f04550a`.  
**Author (v2.0):** Antigravity CoS. Earlier versions: v1.7–v1.9 GB CoS fresh writer; v1.0–v1.6 Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).  

### v2.0 Close-Out of `REVISE_NET-814_v1.9_to_v2.0_VERIFIED_20261108-1155.md`
| # | Verified Must-Fix / Polish | v2.0 Resolution | Section |
|---|---|---|---|
| **MF-3 (REAL)** | Fail-closed pricing (`$30 / 6 months` and `"2027"` world coverage still specified) | Generator & in-app copy emit **ONLY** the 4 established free-beta strings (`public_info_screens.dart:362/396/407/412`) until a separate Founder YES. Added negative tests asserting `$30 / 6 months` and `2027` are absent. US-only stays; no promo codes. | §8.2, §9.2 |
| **MF-1 (REAL)** | `firebase.json` `@@ -115,6` wrong (`4d17ca5e` `/claim/**` is `:130`) | Split into two explicit edits: (a) Pin `4d17ca5e` (`@@ -127,6 +127,14 @@`) inserts `/catalog` + `/catalog/**` after `/claim/**` at `:130`; (b) `origin/dev` (`cc815522`) changes ONLY existing `/catalog/**` destination to `/catalog_unknown.html`. | §3.2 |
| **MF-2 (REAL)** | Widget test expected `'Reference Catalog'`; hardcoded `-xyz.web.app` | Updated test to assert `'Public Catalog'` (`b0b05808:270`) & `'U.S. Numismatics Catalog'` (`:335`) with fixture/Image mock before `pumpAndSettle`; `PREVIEW_URL` captured from `hosting:channel:deploy`; widget tests run BEFORE preview deploy. | §7.2, §9.1, §9.2 |
| **MF-4 (REAL)** | `isApprovedCatalogImageUrl` placement & call sites | Placed in named production file `numista_mobile/lib/utils/catalog_image_guard.dart` (listed in §7.5), wired before `Image.network` at `b0b05808:catalog_browse_screen.dart:918` and `:1106` with fallback to `_buildNoPhotoBox()`/`_buildPlaceholder()`. Added call-site asserts. | §6.4, §7.5, §9.3a |
| **MF-5 (REAL)** | Invented `mintage?['source_name'] ?? 'US Mint Records'` | Dropped `source_name` and `'US Mint Records'` default; `_buildMintageRow` renders plain text `value`/`label` only with no `launchUrl`. | §6.4 |
| **MF-6 (REAL)** | Per-coin HTML sample had bare `<base href="/">` | Rule: clone `build/web/index.html` after `flutter build web --release`, preserve Flutter bootstrap payload, replace only title/description/canonical/OG/Twitter; `og:image` emitted only from guarded non-null `primary_image['url']`. | §3.4 |
| **MF-9 (REAL)** | Negative OG test | Asserted 1921-P Morgan HTML has no `og:image` and no `twitter:image`. | §9.4 |
| **MF-7 (Manifest)** | `public_catalog_route.dart` & `catalog_image_guard_test.dart` in §7.5 | Added `lib/routing/public_catalog_route.dart`, `lib/utils/catalog_image_guard.dart`, and `test/services/catalog_image_guard_test.dart` to §7.5. | §7.5 |
| **Rollback** | `tac` + unconditional `git push origin dev` | `git revert` only (no `reset --hard`), portable `awk` reverse order (dropped `tac`), push behind separate Founder YES, main `9f04550a`. | §7.3 |
| **MF-8 (FALSE)** | `5,142 Reference Coins` | Verified at `4d17ca5e:numista_mobile/lib/screens/login_screen.dart:338` and `:466`; cited verbatim, replacement uses exact `3,202` count (no rounding). | §5.1 |
| **Polish** | Title drift, `:135–234` → `:135–280`, `try/catch` `Uri.decodeComponent`, `/catalog_unknown.html` note | Fixed all 4 polish items. | Header, §2.1, §9.2 |

### v1.9 Close-Out of CoS-94 Must-Fix (round 3, 08:12 ET; ONLY this item changed)
| # | CoS-94 must-fix | v1.9 change | Evidence |
|---|---|---|---|
| **MF-F3-RawPath** | Literal `.`/`..` segments were only checked on `uri.pathSegments`, which Dart has already normalized | §6.4 adds `_hasRawDotSegment(url)`: on the **raw string**, before `Uri.tryParse`, drop any `?`/`#` suffix, split on `/`, reject if any segment is exactly `.` or `..`. Runs for both local-asset and HTTPS forms. Encoded (`%2e`) and post-parse decoded segment checks are retained. §9.3a adds in-allowlist normalization negatives (`us_mint_coin_images/a/../x.jpg`, `.../reference/a/../x.jpg`, `us_mint_coin_images/./x.jpg`, a cross-allowed-bucket `../numista-reference-library/...`). | Dart `Uri` default implementation always normalizes paths (https://api.dart.dev/dart-core/Uri/normalizePath.html, per CoS). No Dart test run. |

### v1.8 Close-Out of CoS-88 Must-Fixes (`COS_SCORE_NET-814_SOFT404-CATALOG-PRICING_v1.7_20261108.md`; ONLY these items changed)
| # | CoS-88 must-fix | v1.8 change | Verified evidence |
|---|---|---|---|
| **F1 (MF-2, privacy)** | §8.2 carried a literal private promotion code | The code string is **removed** from §8.2. Rule stated: no promo code literal may appear in public copy, generated HTML, fixtures, screenshots or plan artifacts; eligibility, if ever needed, is handled privately with no exposed token. §8.2 pricing/coverage bullets are relabeled **PROPOSED — founder decision reference not attached**; they are not accepted marketing facts. Only the existing free-beta strings at `public_info_screens.dart` 362/396/407/412 are established. | Redaction also applied in place (working tree; git history NOT rewritten) to every earlier plan/score copy that contained the literal: docs v1.4–v1.7 primary + mirror, docs `COS_SCORE_..._v1.3_20261107.md`, and handoff copies in BATONS / INBOX / OUTBOX / RADIO NET. Post-redaction scan of docs + `8 OCT 26` tree: 0 hits. Prior commits (incl. `0f97725b`) still contain it in history. |
| **F2 (MF-1)** | curl cannot see Flutter-injected noindex | Server-side contract (§3.6): the generator emits a static `build/web/catalog_unknown.html` = copy of `index.html` with `<meta name="robots" content="noindex, follow">` and canonical `https://numista.ai/catalog` baked in. The `/catalog/**` rewrite destination becomes `/catalog_unknown.html`. Firebase Hosting serves existing static files before rewrites, so valid per-coin pages (`/catalog/<nac>/index.html`, no noindex) stay indexable and the root shell `index.html` is unchanged. Test 2 curl now asserts the served noindex from that file. Limitation kept honest: status remains **HTTP 200** (Hosting rewrites cannot return 404 for a matched SPA path). In-app banner + `replaceState` are verified by a separate headless-browser check (§9.1 Test 2b), not curl. | Dev `numista_mobile/web/index.html`: root canonical `:23` `<link rel="canonical" href="https://numista.ai/">`, no robots tag (per CoS audit; `:23` re-read 8 Nov). Static-before-rewrite precedence is documented Firebase Hosting behavior; not executed here. |
| **F3 (MF-3)** | Image guard accepted the entire upload bucket and any Firebase `/o/` object | §6.4 guard narrowed: `us_mint_coin_images` and `numista-reference-library` (pin index emitters), plus `numista-uploads-studio-9101802118-8c9a8` **only** under `reference/` (promoted destination). Firebase Storage `firebasestorage.googleapis.com/.../o/` URLs (private original uploads) are **rejected**. Rejects userinfo, port, query-less traversal (`.`/`..` raw or `%2e`-encoded), backslashes, empty segments; local assets only under `assets/catalog/images/` without `..`. Passing the guard is necessary, not sufficient: existing per-image release gates still apply. Negative + positive tests added (§9.3a). | `git show 4d17ca5e:numista_backend/_scripts/promote_user_photos.py`: `:35 BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"`, `:36 REF_PREFIX = "reference"`, `:37 PUBLIC_BASE = "https://storage.googleapis.com"`, `:130 return f"{PUBLIC_BASE}/{BUCKET_NAME}/{dest_path}"`, `:196 dest_path = f"{REF_PREFIX}/{program_slug}/{doc_id}.jpg"`. |
| **F4 (MF-4)** | Rollback loop could exit in a subshell then still pull/push | §7.3 rewritten: `set -euo pipefail`, branch assertion (`dev`, never `main`), clean-tree check, preflight of every SHA before any revert, non-subshell `while … done < <(tac …)` loop, `git revert --abort` + `exit 1` on conflict, and pull/push only after a success flag. No rollback was run. | Plan-internal shell; pattern standard bash. |

### v1.7 Close-Out of CoS-90 Remaining Defects (carried forward)
| # | CoS-90 defect | v1.7 change | Verified evidence |
|---|---|---|---|
| **E1** | §3.4 1921-P sample invents `og:image` / `twitter:image` and uses `twitter:card summary_large_image` | Removed `og:image`, `og:image:width`, `og:image:height`, `og:image:alt`, and `twitter:image` from the sample; `twitter:card` is now `summary`. Generator rule stated: image tags are emitted **only** when the record's `primary_image` is non-null; otherwise omitted. No substitute image URL is invented. | `git show origin/dev:numista_mobile/assets/catalog/catalog_public_v1.json` (origin/dev `bde8b402`, 8 Nov ~07:33 ET): record `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3`, `name` "1921-P Morgan Silver Dollars", `primary_image` null, `type_image` null, `secondary_image` null, `extra_images` null. |
| **E2** | `showPublic` wire-up used `item['nac']` | The NET-813 handoff sentence (near the `_showItemDetailModal` :810 quote) now matches NET-813 v1.8 §4.1: `UnifiedCoinDetailScreen.showPublic(context, projection: PublicCoinProjection.fromCatalogMap(item))`, where `fromCatalogMap` reads `item['nac_code']`. | Same JSON: 3,202 rows; **3,202** have `nac_code`; **0** have a `nac` key. |
| **E3** | `extractInitialNac` shown only inside the test file | Helper lives in production file `numista_mobile/lib/routing/public_catalog_route.dart` (new, to be authored on Eric YES); `main.dart` imports and calls it in the `:154–181` dispatch; the test imports `package:numista_ai/routing/public_catalog_route.dart`. Added to the file manifest. | Pin `numista_mobile/pubspec.yaml` line 1 `name: numista_ai` (verified in NET-810 review). Path is new; nothing at that path exists today (not invented as existing). |

**Revision Status:** Attempt **3/4** on v1.5 (incorporating full resolutions for all 6 Numbered Must-Fixes from Grok Bot CoS 75/100 FAIL in `COS_SCORE_NET-814_SOFT404-CATALOG-PRICING_v1.4_20261107.md` and `RADIO_NET-847`)  
**Target Codebase Pin:** `4d17ca5e`  
**Origin Dev Integration Target:** `origin/dev`  
**Operational Standing Locks:** `origin/main` strictly locked at `9f04550a45fa4da082ba8948c2d89a521a90fa45`; Stripe strictly locked OFF (zero live keys or active checkout endpoints); strict PLAN ONLY (preview gate only; zero code edits, builds, Firestore writes/seeding, or live production deployments without Founder Eric's explicit typed YES); alerts-only ($20.00/month Google Cloud Billing threshold); **NEVER budget caps or automated Hosting shutdowns**; no Argon (permanently dropped per Founder Eric typed YES 5 Nov 18:07 ET).

---

## 1. Executive Summary & Ground-Truth Alignment (Resolving CoS-75 Must-Fixes)

This v1.5 architecture plan delivers the definitive, implementable engineering specification for resolving soft-404 routing defects, providing clean public entry for `/catalog`, `/catalog/<nac>`, and `/pricing`, projecting CPG® reference retail pricing, and establishing an alert-only operational posture.

### Summary of CoS-75 Numbered Must-Fix Resolutions:
1. **Surgical Merge Diff for `firebase.json` (MF-1):**
   - Eliminated the dangerous full replacement block from v1.4 that dropped pin rewrites (`/add_coins.html`, `/scraper_dashboard.html`, `/privacy -> /privacy.html`, `/terms -> /terms.html`, `/index.html`) and cache-control headers (`/index.html`, `/`, `/flutter_service_worker.js`, `/flutter_bootstrap.js`, `/version.json`, `/main.dart.js` no-cache).
   - Quoted verbatim pin lines from `git show 4d17ca5e:numista_mobile/firebase.json` and `git show origin/dev:numista_mobile/firebase.json`.
   - Provided a minimal, surgical merge diff that strictly preserves all pin legal/tool rewrites and no-cache headers, adding only the catalog/pricing rewrites and cache entries.
2. **Real NAC Codes Everywhere & Non-Null Field OG Descriptions (MF-2):**
   - Completely struck invented NAC codes (`US-1921-MORGAN` and `US-1909-S-VDB-CENT`).
   - Replaced all sample HTML, feed schemas, smoke URLs, and test suites with verified real NAC codes from `assets/catalog/catalog_public_v1.json`, specifically `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` (1921-P Morgan Silver Dollars) and `NAC1.CN.US.1C.LINCOLNCEN.1909.S.BASE.2` (1909-S Lincoln Cent).
   - Ensured sample OpenGraph descriptions are derived strictly from non-null fields (year: 1921, denomination: Dollar, series: Morgan Silver Dollars, composition: 90% Silver). Zero fabricated claims of mintage or CPG pricing when those fields are null.
3. **Honest CPG Feed & License Sourcing (MF-3):**
   - Explicitly acknowledged that `numista_backend/data/cpg_retail_feed_v2026.11.json` and `numista_backend/_scripts/join_cpg_catalog_feed.py` do not exist on pin `4d17ca5e` or `origin/dev`.
   - Struck all claims of an executed "CDN Publishing CPG® data reference agreement".
   - Formally designated commercial CPG feed acquisition and licensing as **To be acquired (Founder Eric decision)**.
   - Enforced fail-closed behavior: all 3,202 public catalog records renders the neutral slate gray chip `'Valuation Pending'` until an authorized feed is acquired and joined.
4. **Accurate Census Description, Status Badges & Foreign Exclusion (MF-4):**
   - Corrected numismatic census description: exactly **3,202** public records comprising **2,965 coins** (`type: coin`, NAC segment `CN`), **181 bank notes** (`type: note`, NAC segment `BN`), and **56 medals** (`type: medal`, NAC segment `MD`).
   - Grounded status badge UI in the actual `status_badge` JSON field: `'Needs source'` (1,724), `'Details coming'` (950), `'Pre-Federal'` (9), and `null` (519 baseline records).
   - Specified explicit foreign exclusion verification by asserting segment 2 of the NAC code equals `US` (`nac_code.split('.')[2] == 'US'`).
5. **Served-Response Preview Tests & Routing Dispatch (MF-5):**
   - Authored executable `curl` verification commands testing live HTTP status codes and response bodies on the preview channel:
     - Real per-coin URL (HTTP 200 + per-coin canonical and OpenGraph tags).
     - Invalid NAC URL (HTTP 200 + `<meta name="robots" content="noindex">` soft-404).
     - `/catalog`, `/pricing`, `/privacy`, `/terms` (HTTP 200).
     - Unrelated bad path (HTTP 404).
   - Documented and tested `main.dart` route dispatch for `/catalog` and `/catalog/<nac>`.
6. **Rollback Nits & Comprehensive File Manifest (MF-6):**
   - Specified pre-deploy capture of `releases[0]` (the active live release snapshot) from the Google Cloud Hosting REST API.
   - Reversed git rollback loop to revert commits in reverse chronological order (newest commit first), with ancestry checks and conflict abort.
   - Added a complete File Manifest explicitly designating unauthored scripts as **To be authored upon Founder Eric typed YES** and missing feeds as **To be acquired (Founder Eric decision)**.

---


### CoS-86 Review Closeout Matrix (v1.5 -> v1.6, Attempt 4/4)
| Must-Fix ID | Category | Requirement from CoS-86 (`RADIO_NET-850`) | Resolution in v1.6 |
|---|---|---|---|
| **MF-1** | Routing Ground Truth | Re-quote `origin/dev:numista_mobile/lib/main.dart` catalog dispatch at lines **154–181** (replacing incorrect citation lines 215–245, which are Firebase init timeout/error UI). | Lines 154–181 quoted verbatim in §4.1; lines 215–245 explicitly clarified as error UI. |
| **MF-2** | Public Call Site Grounding | Do not cite `catalog_browse_screen.dart:315` as public `showPublic` call site (line 315 is `child: Column(` owl header). Quote real sites: card tap `:466` and `_showItemDetailModal` at `:810` (and initial NAC `:80`). | Quoted `:466`, `:810`, and `:80` verbatim in §4.2; noted `:315` is non-interactive header layout. |
| **MF-3** | `firebase.json` Pin Labels | Correct pin `firebase.json` line labels: rewrite `source` entries run through `/claim/**` at **line 130** (array ends line 133); headers begin around **line 137** (`**/*.@(js|css|wasm)`), not 119–234. | Exact line ranges 51–133 and 135–234 labelled in §3.1 and surgical diff preserved. |
| **MF-4** | `main.dart` Dispatch Test | Add `main.dart` route parsing test, or explain why `main()` top-level is untestable in widget tests and covered by preview curls. | Added pure route parsing unit test `extractInitialNac` in §9.2 and detailed why top-level `main()` requires browser globals and is covered by §9.1 preview curls. |
| **MF-5** | 1921 Morgan OG Image | Do not invent an OG image for `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` (all image fields are null; do not emit mintage figure). Omit `og:image` when null. | Cleaned sample in §3.4: omitted `og:image` and `twitter:image`; omitted mintage; only non-null fields included. |
| **MF-6** | Valuation Pending Chip Color | Align Valuation Pending chip color everywhere to neutral slate gray (`#F1F5F9` background, `#64748B` text), replacing leftover "gold chip" text. | Replaced "gold chip" with neutral slate gray chip in §1, §6.2, and §6.3. |
| **MF-7** | Manifest Table Alignment | Add `test/services/catalog_census_privacy_test.dart` to §7.5 file manifest table. | Added to table in §7.5. |
| **MF-8** | Delivery Tracking | Document v1.5 delivery commit (`4a124977`) and track v1.6 delivery on branch `dev`. | Documented in §11. |

---

## 2. Standing Operational Constraints & Pinned Boundaries

1. **Production Branch Lock:** `origin/main` is pinned and locked at commit `9f04550a45fa4da082ba8948c2d89a521a90fa45`. No commits, merges, or pushes to `origin/main` are permitted.
2. **Strict PLAN ONLY:** Zero production deployments, zero code edits, zero builds, zero Firestore writes or schema migrations, and zero deletions without Founder Eric's explicit typed YES.
3. **Stripe Lock:** Stripe remains completely locked OFF across all client and backend code paths. No live keys, no Stripe checkout sessions, and no billing endpoints may be enabled.
4. **Cloud Billing Posture (Alert-Only):** Cost control is governed strictly by an alert-only threshold of **$20.00/month** in Google Cloud Billing. **Automated budget caps, programmatic Hosting disablement, and traffic dropping are strictly prohibited.**
5. **Argon Dropped:** Argon is permanently dropped from the stack (typed YES from Eric on 5 Nov 18:07 ET).
6. **Rule 6a Verbatim Citations:** All citations of existing code are quoted verbatim from `git show 4d17ca5e:<path>` or `git show origin/dev:<path>`.

---

## 3. Route HTML and Firebase Hosting Agreement (Resolving MF-1 and MF-2)

### 3.1 Ground Truth in `numista_mobile/firebase.json`
Inspecting `numista_mobile/firebase.json` at `git show 4d17ca5e:numista_mobile/firebase.json`:
- Lines 51–133 (`rewrites` array at pin, with `source` rules extending through `/claim/**` at line 130 and array closure at line 133):
```json
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "numista-backend",
          "region": "us-central1"
        }
      },
      {
        "source": "/add_coins.html",
        "destination": "/add_coins.html"
      },
      {
        "source": "/scraper_dashboard.html",
        "destination": "/scraper_dashboard.html"
      },
      {
        "source": "/privacy",
        "destination": "/privacy.html"
      },
      {
        "source": "/terms",
        "destination": "/terms.html"
      },
      {
        "source": "/about",
        "destination": "/index.html"
      },
      {
        "source": "/pricing",
        "destination": "/index.html"
      },
      {
        "source": "/features",
        "destination": "/index.html"
      },
      {
        "source": "/faq",
        "destination": "/index.html"
      },
      {
        "source": "/login",
        "destination": "/index.html"
      },
      {
        "source": "/reset-password",
        "destination": "/index.html"
      },
      {
        "source": "/signup",
        "destination": "/index.html"
      },
      {
        "source": "/demo",
        "destination": "/index.html"
      },
      {
        "source": "/",
        "destination": "/index.html"
      },
      {
        "source": "/index.html",
        "destination": "/index.html"
      },
      {
        "source": "/wishlist",
        "destination": "/index.html"
      },
      {
        "source": "/wishlist/**",
        "destination": "/index.html"
      },
      {
        "source": "/attorney_portal",
        "destination": "/index.html"
      },
      {
        "source": "/claim",
        "destination": "/index.html"
      },
      {
        "source": "/claim/**",
        "destination": "/index.html"
      }
    ],
```

- Lines 135–280 (`headers` array at pin, starting with `"headers": [` at line 135 and first rule `"source": "**/*.@(js|css|wasm)"` at line 137):
```json
    "headers": [
      {
        "source": "**/*.@(js|css|wasm)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=31536000, immutable"
          }
        ]
      },
      {
        "source": "/index.html",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "/",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "/flutter_service_worker.js",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "/flutter_bootstrap.js",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "/version.json",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "/main.dart.js",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "**/*.@(png|jpg|jpeg|gif|svg|ico|webp)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=86400"
          }
        ]
      },
      {
        "source": "/manifest.json",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=3600"
          },
          {
            "key": "Content-Type",
            "value": "application/manifest+json"
          }
        ]
      },
      {
        "source": "/robots.txt",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=86400"
          },
          {
            "key": "Content-Type",
            "value": "text/plain; charset=utf-8"
          }
        ]
      },
      {
        "source": "/sitemap.xml",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=86400"
          },
          {
            "key": "Content-Type",
            "value": "application/xml; charset=utf-8"
          }
        ]
      },
      {
        "source": "**",
        "headers": [
          {
            "key": "X-Frame-Options",
            "value": "SAMEORIGIN"
          },
          {
            "key": "X-Content-Type-Options",
            "value": "nosniff"
          },
          {
            "key": "Referrer-Policy",
            "value": "strict-origin-when-cross-origin"
          },
          {
            "key": "Permissions-Policy",
            "value": "camera=(self), microphone=(), geolocation=(), payment=()"
          },
          {
            "key": "Strict-Transport-Security",
            "value": "max-age=63072000; includeSubDomains; preload"
          },
          {
            "key": "X-DNS-Prefetch-Control",
            "value": "on"
          },
          {
            "key": "Content-Security-Policy",
            "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
          }
        ]
      }
    ]
```

- Reconciled entries from `git show origin/dev:numista_mobile/firebase.json` (lines 132–139):
```json
      {
        "source": "/catalog",
        "destination": "/index.html"
      },
      {
        "source": "/catalog/**",
        "destination": "/index.html"
      }
```

### 3.2 Two Explicit `firebase.json` Edits: Pin `4d17ca5e` vs `origin/dev` (`cc815522`) (v2.0 MF-1)
Because `4d17ca5e` has no `/catalog` rewrites (and no catch-all `**` before `/claim/**` at `:130`), whereas `origin/dev` (`cc815522`) already has `/catalog` and `/catalog/**` at `:132–139`, the plan specifies **two explicit per-branch edits**:

1. **Edit A — On Pin `4d17ca5e` (append after `/claim/**` at `:130`):**
```diff
--- a/numista_mobile/firebase.json
+++ b/numista_mobile/firebase.json
@@ -127,6 +127,14 @@
       {
         "source": "/claim/**",
         "destination": "/index.html"
+      },
+      {
+        "source": "/catalog",
+        "destination": "/index.html"
+      },
+      {
+        "source": "/catalog/**",
+        "destination": "/catalog_unknown.html"
       }
     ],
     "headers": [
@@ -165,6 +173,22 @@
           }
         ]
       },
+      {
+        "source": "/catalog/**/index.html",
+        "headers": [
+          {
+            "key": "Cache-Control",
+            "value": "public, max-age=3600"
+          }
+        ]
+      },
+      {
+        "source": "/pricing/index.html",
+        "headers": [
+          {
+            "key": "Cache-Control",
+            "value": "public, max-age=3600"
+          }
+        ]
+      },
       {
         "source": "**/*.@(png|jpg|jpeg|gif|svg|ico|webp)",
         "headers": [
```

2. **Edit B — On `origin/dev` (`cc815522`, change ONLY the existing `/catalog/**` destination):**
```diff
--- a/numista_mobile/firebase.json
+++ b/numista_mobile/firebase.json
@@ -135,5 +135,5 @@
       {
         "source": "/catalog/**",
-        "destination": "/index.html"
+        "destination": "/catalog_unknown.html"
       }
```
*(Do not append duplicate `/catalog` or `/catalog/**` entries on `origin/dev`; add only the two `Cache-Control` header blocks above if not already present.)*

### 3.3 Static File Serving Precedence & Resolution
Firebase Hosting serves exact static file matches from `public: build/web` **before** evaluating rewrite rules:
1. `https://numista.ai/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` matches the physical file `build/web/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3/index.html` and is served directly with HTTP 200 and per-coin canonical and OpenGraph tags.
2. `https://numista.ai/catalog` matches `build/web/catalog/index.html` and is served directly with HTTP 200.
3. `https://numista.ai/pricing` matches `build/web/pricing/index.html` and is served directly with HTTP 200.
4. `https://numista.ai/privacy` matches `/privacy -> /privacy.html` rewrite and serves `build/web/privacy.html` with HTTP 200.
5. `https://numista.ai/terms` matches `/terms -> /terms.html` rewrite and serves `build/web/terms.html` with HTTP 200.
6. Unknown NAC codes (e.g. `/catalog/NAC1.CN.US.NONEXISTENT.BASE.9`): No physical static file exists. Request falls through to rewrite `{"source": "/catalog/**", "destination": "/catalog_unknown.html"}`, returning HTTP 200 and booting the Flutter SPA, which renders `_CatalogNotFoundBanner` and inserts `<meta name="robots" content="noindex">`.
7. Unrelated bad paths (e.g. `/arbitrary-bad-path-123`): Matches **no rewrite** in `firebase.json` (since there is no catch-all `**` rewrite). Firebase Hosting serves `build/web/404.html` with an authentic HTTP 404 status.

### 3.4 Generator Architecture & Per-Coin Static Route Generation Pipeline (v2.0 MF-6)
During the release build pipeline, after `flutter build web --release` completes, a dedicated Dart script `tool/generate_catalog_html.dart` (marked **To be authored upon Founder Eric typed YES**) runs before deployment.

**Template Cloning Rule (v2.0 MF-6):** The generator MUST **clone `build/web/index.html`** produced by `flutter build web --release` (preserving the exact Flutter bootstrap payload, scripts, base href, and asset hashes), and replace **only** `<title>`, `<meta name="description">`, `<link rel="canonical">`, `og:*`, and `twitter:*` meta tags. It MUST emit `og:image*` and `twitter:image` **only** when `isApprovedCatalogImageUrl(primary_image['url'])` is true for a non-null `primary_image['url']`. For `/catalog_unknown.html`, it clones `build/web/index.html` and injects `<meta name="robots" content="noindex, follow">` + canonical `https://numista.ai/catalog`. (Polish note: `/catalog_unknown.html` is a Hosting rewrite target; `isKnownPath` / route guards only need to treat `/catalog/**` cleanly.)

The generator performs two tasks:
1. Generates static entrypoints for `/catalog/index.html` and `/pricing/index.html`.
2. Iterates over `assets/catalog/catalog_public_v1.json` and generates a dedicated static HTML entrypoint for every valid coin record at `build/web/catalog/<nac>/index.html`.

#### Directory Structure in `build/web/`:
```
build/web/
├── index.html                                        (Root SPA shell)
├── 404.html                                          (Authentic 404 response for unknown non-catalog paths)
├── catalog/
│   ├── index.html                                    (Catalog root metadata)
│   ├── NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3/
│   │   └── index.html                                (Per-coin metadata for 1921-P Morgan Dollar)
│   ├── NAC1.CN.US.1C.LINCOLNCEN.1909.S.BASE.2/
│   │   └── index.html                                (Per-coin metadata for 1909-S Lincoln Cent)
│   └── ...                                           (All 3,202 valid catalog records)
└── pricing/
    └── index.html                                    (Pricing surface metadata)
```

#### Sample Generated Per-Coin HTML (`build/web/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3/index.html`):
Notice: Derived strictly from non-null fields in record `NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3` (`name`: "1921-P Morgan Silver Dollars", `year`: 1921, `denomination`: "Dollar", `series`: "Morgan Silver Dollars", `mint_facility`: "Philadelphia", `composition`: "90% Silver", `era`: "Barber to Golden Age (1892–1932)"). Zero claims of null mintage or non-existent CPG pricing:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <base href="/">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Numista.AI Reference Catalog – 1921-P Morgan Silver Dollars</title>
  <meta name="description" content="View specifications and historical details for 1921-P Morgan Silver Dollars (1921, Dollar, Morgan Silver Dollars, 90% Silver) in the Numista.AI Public Catalog." />
  
  <!-- OpenGraph Metadata for Crawlers & Social Previews -->
  <meta property="og:site_name" content="Numista.AI" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="Numista.AI Reference Catalog – 1921-P Morgan Silver Dollars" />
  <meta property="og:description" content="View specifications and historical details for 1921-P Morgan Silver Dollars (1921, Dollar, Morgan Silver Dollars, 90% Silver) in the Numista.AI Public Catalog." />
  <meta property="og:url" content="https://numista.ai/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3" />
  <!-- v1.7 (E1): no og:image tags. This record's primary_image/type_image/secondary_image/extra_images are all null.
       The generator emits og:image* and twitter:image ONLY when primary_image is non-null. -->
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="Numista.AI Reference Catalog – 1921-P Morgan Silver Dollars" />
  <meta name="twitter:description" content="View specifications and historical details for 1921-P Morgan Silver Dollars in the Numista.AI Public Catalog." />
  
  <link rel="canonical" href="https://numista.ai/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3" />
  <link rel="icon" type="image/png" href="favicon.png" />
  
  <!-- Flutter Web Bootstrap -->
  <script src="flutter_bootstrap.js" async></script>
</head>
<body>
</body>
</html>
```

### 3.5 Root Base and Asset Resolution (`<base href="/">`)
Every generated HTML document includes `<base href="/">`. This guarantees that relative asset requests (`assets/fonts/...`, `flutter_bootstrap.js`, `manifest.json`) resolve against the origin root `https://numista.ai/` rather than a virtual directory like `https://numista.ai/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3/assets/...`.

### 3.6 Elimination of In-App Soft-404 on Unknown NAC Code
1. **Crawler Status:** In a static SPA architecture without edge server-side rendering, requesting an unknown NAC code (e.g. `/catalog/NAC1.CN.US.NONEXISTENT.BASE.9`) matches the rewrite `{"source": "/catalog/**", "destination": "/catalog_unknown.html"}`. (v1.8 F2) The rewrite destination is the generator-emitted static `build/web/catalog_unknown.html` (an `index.html` copy with `<meta name="robots" content="noindex, follow">` and `<link rel="canonical" href="https://numista.ai/catalog">` in the served HTML), returned with HTTP 200. The noindex is therefore visible to non-JS crawlers and to curl. Valid codes resolve to their static per-coin `index.html` first (no noindex). Root `index.html` is NOT modified. HTTP 200 (not 404) is a retained limitation of Hosting rewrites.
2. **Client-Side Resolution:** Once Flutter Web initializes in the client browser, `CatalogBrowseScreen` detects that `initialNacCode` does not match any entry in `_allEntries`.
3. **In-Screen Banner:** Instead of a transient snackbar, `CatalogBrowseScreen` renders the persistent in-screen widget `_CatalogNotFoundBanner`.
4. **URL Normalization:** Flutter Web executes `window.history.replaceState({}, '', '/catalog')` to normalize the browser address bar back to `/catalog`.
5. **Authentic 404 on Non-Catalog Routes:** Any route outside of `/catalog`, `/pricing`, and declared SPA routes (e.g. `/not-a-coin`, `/random-bad-path`) matches NO rewrite and is served `build/web/404.html` with an authentic HTTP 404 response.

#### In-Screen `_CatalogNotFoundBanner` Implementation:
```dart
class _CatalogNotFoundBanner extends StatelessWidget {
  final String unknownCode;
  final VoidCallback onDismiss;

  const _CatalogNotFoundBanner({
    Key? key,
    required this.unknownCode,
    required this.onDismiss,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFFEF2F2),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFEF4444), width: 1.5),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.info_outline, color: Color(0xFFDC2626), size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Item Not Found',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF991B1B),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Reference code "$unknownCode" was not found in the public catalog. You are viewing the full reference directory below.',
                  style: const TextStyle(fontSize: 14, color: Color(0xFF7F1D1D), height: 1.4),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, color: Color(0xFF991B1B), size: 20),
            onPressed: onDismiss,
            tooltip: 'Dismiss message',
          ),
        ],
      ),
    );
  }
}
```

---

## 4. Target Tree Branch Integration Contract

### 4.1 Ground Truth Comparison: `4d17ca5e` vs `origin/dev`
- **Pin `4d17ca5e:numista_mobile/lib/main.dart`:**
  - Lines 119–140: `isKnownPath` contains no catalog paths.
  - Lines 142–148: Unknown paths hit `NotFoundScreen(attemptedPath: path)`.
  - Import list (lines 8–19) does not import `catalog_browse_screen.dart`.
- **Target `origin/dev:numista_mobile/lib/main.dart`:**
  - Line 12: `import 'screens/catalog/catalog_browse_screen.dart';`
  - Lines 133–134: Whitelists `normalizedPath == '/catalog'` and `path.startsWith('/catalog/')`.
  - Lines **154–181** (verbatim from `git show origin/dev:numista_mobile/lib/main.dart`): Direct public catalog route dispatch:
```dart
  // Public Catalog direct entry (zero auth required)
  if (normalizedPath == '/catalog' || path.startsWith('/catalog/')) {
    String? initialNacCode;
    if (path.startsWith('/catalog/')) {
      final sub = path.substring('/catalog/'.length).trim();
      if (sub.isNotEmpty) {
        try {
          initialNacCode = Uri.decodeComponent(sub);
        } on ArgumentError {
          initialNacCode = sub;
        }
      }
    }
    if (initialNacCode == null && uri.queryParameters.containsKey('item')) {
      initialNacCode = uri.queryParameters['item'];
    }
    runApp(MaterialApp(
      title: 'Numista.AI Public Catalog',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: Colors.white,
        primaryColor: const Color(0xFF0B2545),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1F5FAD),
          primary: const Color(0xFF0B2545),
        ),
      ),
      home: CatalogBrowseScreen(initialNacCode: initialNacCode),
    ));
    return;
  }
```
*(Clarification per MF-1: Lines 215–245 of `main.dart` on `origin/dev` contain the `Firebase.initializeApp` timeout catch and `kApiBaseUrl` error screen UI, not routing. The public catalog dispatch is verified exclusively at lines 154–181).*

### 4.2 Public Call Site Grounding in `catalog_browse_screen.dart` (Resolving MF-2)
Examining `git show origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`:
- **Line 315:** `child: Column(` (Non-interactive Morgan owl header layout. Line 315 is NOT a call site for detail modal or `showPublic`).
- **Real Call Sites:**
  - **Line 466 (Catalog Card tap):**
    ```dart
    onTap: () => _showItemDetailModal(item),
    ```
  - **Line 80 (Initial NAC match on mount):**
    ```dart
    _showItemDetailModal(match);
    ```
  - **Line 810 (Modal display function definition):**
    ```dart
    void _showItemDetailModal(Map<String, dynamic> item) {
    ```
- **Unified Coin Detail View Integration:**
  In NET-813, `UnifiedCoinDetailScreen.showPublic(context, projection: PublicCoinProjection.fromCatalogMap(item))` (v1.7 E2: `fromCatalogMap` reads the real catalog key `item['nac_code']`; public records have no `nac` key) is wired into `_showItemDetailModal` at line 810, cleanly replacing the legacy dialog while preserving both invocation paths (`:466` card tap and `:80` URL initial NAC match).

---

## 5. Master Data Sourcing, Census, Status Badges & Privacy (Resolving MF-4)

### 5.1 Repository Master Census
The authoritative repository public catalog dataset is `numista_mobile/assets/catalog/catalog_public_v1.json` (tracked in git).
- **Target Reference Census:** Exactly **3,202** reference entries.
- **Accurate Census Breakdown:**
  - **2,965 Coins** (`type: "coin"`, NAC code segment 1: `CN`)
  - **181 Bank Notes** (`type: "note"`, NAC code segment 1: `BN`)
  - **56 Medals** (`type: "medal"`, NAC code segment 1: `MD`)
- **Foreign / World Numismatics Exclusion:** Every single record of the 3,202 entries contains `.US.` in its NAC code (segment 2). The programmatic filter checks:
  ```dart
  bool isUnitedStatesRecord(String nacCode) {
    final parts = nacCode.split('.');
    return parts.length > 2 && parts[2] == 'US';
  }
  ```
  Any non-US item is strictly excluded.
- **Marketing Claim Alignment (v2.0 MF-1b):** Verified occurrences in `4d17ca5e:numista_mobile/lib/screens/login_screen.dart:338` and `:466` (`_StatBadge(value: '5,142', label: 'Reference\nCoins'),`) are updated to the exact verified census: `"3,202 Reference Items"` (no rounding).

### 5.2 Content Verification & Status Classification
Every catalog record is classified into an explicit numismatic status badge grounded strictly in the `status_badge` field of `catalog_public_v1.json`:
- `'Needs source'`: 1,724 records
- `'Details coming'`: 950 records
- `'Pre-Federal'`: 9 records
- `null`: 519 records (displayed without a status badge chip as standard baseline reference entries)

### 5.3 Strict Privacy Prohibitions (Zero AJ PII / Private Collection Exposure)
The public catalog is an immutable numismatic reference database. Under NO circumstances does the catalog contain or project:
1. User IDs, emails, names, or addresses.
2. Individual collection inventories, acquisition dates, purchase prices, or cost baselines.
3. Private grades, certification numbers, or slab barcodes.
4. User-uploaded photographs (all catalog images must originate from verified reference sources).
5. Private notes, storage locations, or insurance appraisals.

---

## 6. Retail Pricing Projection & Feed Sourcing Honesty (Resolving MF-3)

### 6.1 Authorized Retail Join Specification & Feed Status
Public users require authoritative, educational retail pricing:
- **Authorized Dataset:** **CPG® Retail Price Guide Reference Feed (CDN Publishing)**.
- **Feed Status:** `numista_backend/data/cpg_retail_feed_v2026.11.json` and `numista_backend/_scripts/join_cpg_catalog_feed.py` **do not exist** at pin `4d17ca5e` or `origin/dev`.
- **License / Agreement Status:** No CDN Publishing CPG® data reference agreement document exists or has been executed.
- **Operational Classification:** Commercial CPG feed acquisition and data licensing is designated as **To be acquired (Founder Eric decision)**.
- **Feed JSON Schema (Target):**
```json
{
  "feed_version": "2026.11",
  "as_of_date": "2026-11-01",
  "provider": "CDN Publishing CPG",
  "records": [
    {
      "nac_code": "NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3",
      "cpg_retail_usd": 42.00,
      "as_of": "2026-11-01T00:00:00Z"
    }
  ]
}
```

### 6.2 Missing & Invalid Join Policy ('Valuation Pending')
- **Fail-Closed Rule:** Because no CPG retail feed has been acquired, `cpg_retail` is absent or `null` for all public records in `catalog_public_v1.json`. The UI strictly renders the neutral slate gray chip: `'Valuation Pending'`.
- **Positive-Precedence Rule:** If and when an authorized feed is joined, only positive numbers (`cpg_retail > 0`) are formatted as `$XX.XX`.
- **Zero Wholesale Data:** Greysheet wholesale bid/ask prices are strictly excluded from public display.

### 6.3 Card and Modal Retail Renderers
In `_CatalogCard` and `_showItemDetailModal`:
```dart
Widget _buildRetailPriceChip(Map<String, dynamic> item) {
  final dynamic val = item['cpg_retail'];
  final double? retail = (val is num) ? val.toDouble() : null;

  if (retail != null && retail > 0) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        'CPG \$${retail.toStringAsFixed(2)}',
        style: const TextStyle(
          color: Color(0xFFF8FAFC),
          fontWeight: FontWeight.bold,
          fontSize: 12,
        ),
      ),
    );
  }

  return Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
    decoration: BoxDecoration(
      color: const Color(0xFFF1F5F9),
      borderRadius: BorderRadius.circular(6),
      border: Border.all(color: const Color(0xFFCBD5E1)),
    ),
    child: const Text(
      'Valuation Pending',
      style: TextStyle(
        color: Color(0xFF64748B),
        fontWeight: FontWeight.w600,
        fontSize: 12,
      ),
    ),
  );
}
```

### 6.4 Image Sourcing, Guarded Fetch, and Outbound Link Neutralization
All public catalog image URLs must pass strict validation against verified first-party emitters. `isApprovedCatalogImageUrl` lives in production code at `numista_mobile/lib/utils/catalog_image_guard.dart` and is imported by `catalog_browse_screen.dart` to gate both `primary_image['url']` and `type_image['url']` before any `Image.network` call:

```dart
// numista_mobile/lib/utils/catalog_image_guard.dart (PRODUCTION file; v2.0 MF-2)
/// v1.9: raw-string dot-segment check. MUST run before Uri.tryParse, because Dart's
/// Uri normalizes `.`/`..` out of pathSegments.
bool _hasRawDotSegment(String url) {
  final pathPart = url.split(RegExp(r'[?#]')).first;
  return pathPart.split('/').any((seg) => seg == '.' || seg == '..');
}

bool isApprovedCatalogImageUrl(String url) {
  if (url.isEmpty || url.contains('\\')) return false;
  if (_hasRawDotSegment(url)) return false; // v1.9 MF-F3-RawPath: before any parsing
  final lower = url.toLowerCase();
  // Reject encoded traversal / separators before any parsing (v1.8 F3)
  if (lower.contains('%2e') || lower.contains('%2f') || lower.contains('%5c')) return false;

  // Bundled local catalog assets only, no traversal
  if (url.startsWith('assets/catalog/images/')) {
    return !url.split('/').any((seg) => seg.isEmpty || seg == '.' || seg == '..');
  }

  final uri = Uri.tryParse(url);
  if (uri == null || uri.scheme != 'https') return false;
  if (uri.userInfo.isNotEmpty || uri.hasPort) return false;
  if (uri.host != 'storage.googleapis.com') return false; // firebasestorage.googleapis.com (private originals) rejected

  final seg = uri.pathSegments;
  if (seg.length < 2 || seg.any((p) => p.isEmpty || p == '.' || p == '..')) return false;

  switch (seg.first) {
    case 'us_mint_coin_images':        // build_image_index.py emitter (pin)
    case 'numista-reference-library':  // build_image_index.py / build_currency_image_index.py emitters (pin)
      return true;
    case 'numista-uploads-studio-9101802118-8c9a8':
      // Only the promoted public reference destination (promote_user_photos.py :35-36, :196)
      return seg[1] == 'reference';
    default:
      return false;
  }
}
// Passing this guard is NECESSARY, not sufficient: per-image release/provenance gates still apply.
```

#### Call-Site Wiring in `catalog_browse_screen.dart` (v2.0 MF-2):
Both `Image.network` call sites in `cc815522:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` are gated before network fetch:
1. **Line 918 (Detail modal `primary_image` / `type_image` hero):**
   - Current: `child: Image.network(url, height: 220, fit: BoxFit.contain, errorBuilder: (c, e, s) => _buildNoPhotoBox(),)`
   - Guarded: `child: isApprovedCatalogImageUrl(url) ? Image.network(url, height: 220, fit: BoxFit.contain, errorBuilder: (c, e, s) => _buildNoPhotoBox(),) : _buildNoPhotoBox(),`
2. **Line 1106 (Catalog card `primary_image` / `type_image` thumbnail):**
   - Current: `imgMap != null && imgMap['url'] != null ? Image.network(imgMap['url'] as String, fit: BoxFit.contain, errorBuilder: (c, e, s) => _buildPlaceholder(),) : _buildPlaceholder()`
   - Guarded: `imgMap != null && imgMap['url'] is String && isApprovedCatalogImageUrl(imgMap['url'] as String) ? Image.network(imgMap['url'] as String, fit: BoxFit.contain, errorBuilder: (c, e, s) => _buildPlaceholder(),) : _buildPlaceholder()`

#### Rejection of Invented Buckets:
The bucket `numista-vault.firebasestorage.app/reference_catalog/` is completely struck. `numista-vault` is exclusively a Firebase Hosting site ID (`firebase.json:7`), not a verified Cloud Storage bucket.

#### Outbound Mintage Link Neutralization (v2.0 MF-3):
In `cc815522:catalog_browse_screen.dart:987–1017`, external `source_url` launching (`launchUrl`) is removed and replaced with plain-text rendering of the mintage `value` and `label` only (no invented `mintage?['source_name'] ?? 'US Mint Records'` fallback):
```dart
Text(
  val,
  style: const TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.bold,
    color: Color(0xFF0B2545),
  ),
),
```

---

## 7. Operational Controls, Rollback, and Spending Protection (Resolving MF-1 & MF-6)

### 7.1 Permanent Removal of Budget Caps
- Automated budget caps, programmatic Hosting disablement, and traffic dropping are permanently eliminated.
- Cost control is enforced strictly via a **$20.00/month alert-only threshold** in Google Cloud Billing.
- If spending reaches $20.00/month, Google Cloud Billing triggers an email alert to Founder Eric and the AG CoS desk. Operations personnel manually review CDN caching and asset egress without degrading user availability.

### 7.2 Non-Destructive Deployment via Preview Channel
Widget/unit tests (§9.2, §9.3, §9.3a) run and pass **before** any preview channel deploy. All deployment testing occurs on an isolated preview channel before any live deployment, capturing the live `PREVIEW_URL` directly from `firebase hosting:channel:deploy` output:
```bash
# 0. Pre-deploy gate: run unit & widget tests first
cd numista_mobile
flutter test test/screens/catalog_soft404_routing_test.dart test/services/catalog_census_privacy_test.dart test/services/catalog_image_guard_test.dart

# 1. Build release web bundle
flutter build web --release

# 2. Run static catalog generator
dart run tool/generate_catalog_html.dart

# 3. Deploy to isolated preview channel (Hosting only) and capture PREVIEW_URL
DEPLOY_JSON=$(firebase hosting:channel:deploy pre-thanksgiving-net814 --site numista-vault --expires 48h --json)
PREVIEW_URL=$(python3 -c "import json,sys; print(json.load(sys.stdin)['result']['numista-vault']['url'])" <<< "$DEPLOY_JSON")
echo "Preview URL: $PREVIEW_URL"
```

### 7.3 Real Git Rollback Procedure (Reverse Chronological Order)
All commits contributing to NET-814 are tracked in `scratch/revert_shas_net814.txt`. `origin/main` remains locked at `9f04550a` (no merge or push to `main`).

If a rollback is required, commits are reverted locally in **reverse chronological order** (newest commit first) using portable `awk` (no `tac`, no `reset --hard`, and push stays behind a separate explicit Founder YES):
```bash
#!/usr/bin/env bash
set -euo pipefail
LIST=scratch/revert_shas_net814.txt   # exact NET-814 commit SHAs recorded at execution time, one per line
BR=$(git rev-parse --abbrev-ref HEAD)
[ "$BR" = "dev" ] || { echo "ABORT: on '$BR', expected dev"; exit 1; }
[ "$BR" != "main" ] || exit 1
git diff --quiet && git diff --cached --quiet || { echo "ABORT: dirty tree"; exit 1; }

# Preflight ALL SHAs before touching anything
while read -r sha; do
  [ -z "$sha" ] && continue
  git cat-file -e "$sha^{commit}" || { echo "ABORT: $sha not a commit"; exit 1; }
  git merge-base --is-ancestor "$sha" HEAD || { echo "ABORT: $sha not in HEAD ancestry"; exit 1; }
done < "$LIST"

# Portable reverse order via awk (no tac / no process substitution)
REV_LIST=$(awk '{lines[NR]=$0} END {for (i=NR; i>=1; i--) if (lines[i] != "") print lines[i]}' "$LIST")
for sha in $REV_LIST; do
  if ! git revert --no-edit "$sha"; then
    git revert --abort || true
    echo "ABORT: conflict reverting $sha; local tree restored"; exit 1
  fi
done

echo "Local revert complete. Push requires separate explicit Founder YES."
```

### 7.4 Real Firebase Hosting Release Restore (Pre-Deploy Capture)
To restore a prior live Hosting release:

#### Pre-Deploy Release ID Capture (Gate Check):
Prior to executing `firebase deploy`, capture the current live release ID from the Google Cloud Hosting REST API. Under pre-deploy conditions, `releases[0]` represents the active live release:
```bash
# Query the live release history pre-deploy using Google Cloud OAuth token
PRE_DEPLOY_VERSION_NAME=$(curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://firebasehosting.googleapis.com/v1beta1/sites/numista-vault/releases?pageSize=2" \
  | jq -r '.releases[0].version.name')

# Extract bare version ID (stripping 'sites/numista-vault/versions/' prefix)
PRE_DEPLOY_VERSION_ID=$(echo "$PRE_DEPLOY_VERSION_NAME" | awk -F'/' '{print $NF}')
echo "Pre-deploy active live version ID: $PRE_DEPLOY_VERSION_ID"
```

#### Official Capture via Firebase Console (Manual Verification):
1. Navigate to: `https://console.firebase.google.com/project/studio-9101802118-8c9a8/hosting/sites/numista-vault/releases`
2. Identify the active release and record the bare version ID.

#### Supported Firebase Hosting Clone & Rollback Command:
```bash
# Clone the pre-deploy bare version ID to live
firebase hosting:clone numista-vault@$PRE_DEPLOY_VERSION_ID numista-vault:live

# Delete preview channel
firebase hosting:channel:delete pre-thanksgiving-net814 --site numista-vault --force

# Verify live availability
curl -s -o /dev/null -w "%{http_code}\n" https://numista.ai/
curl -s -o /dev/null -w "%{http_code}\n" https://numista.ai/catalog
curl -s -o /dev/null -w "%{http_code}\n" https://numista.ai/pricing
```

### 7.5 Comprehensive File Manifest
| Path | Status | Purpose |
|---|---|---|
| `numista_mobile/firebase.json` | **Existing (Pin `4d17ca5e`)** | Minimal surgical merge diff for catalog rewrites and caching |
| `numista_mobile/lib/main.dart` | **Existing (`origin/dev`)** | Public catalog direct route dispatch |
| `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` | **Existing (`origin/dev`)** | Catalog browse UI, modal, and `_CatalogNotFoundBanner` |
| `numista_mobile/assets/catalog/catalog_public_v1.json` | **Existing (`origin/dev`)** | 3,202 public reference records (2,965 coins, 181 notes, 56 medals) |
| `numista_mobile/lib/widgets/auth_gate.dart` | **Existing (Pin `4d17ca5e`)** | Public route precedence update |
| `numista_mobile/lib/routing/public_catalog_route.dart` | **To be authored upon Eric YES** | Pure `extractInitialNac(Uri)` helper imported by `main.dart` and tests |
| `numista_mobile/lib/utils/catalog_image_guard.dart` | **To be authored upon Eric YES** | `isApprovedCatalogImageUrl(String)` guard imported by `catalog_browse_screen.dart` |
| `numista_mobile/test/services/catalog_image_guard_test.dart` | **To be authored upon Eric YES** | Positive/negative URL guard and call-site tests |
| `numista_mobile/test/services/catalog_census_privacy_test.dart` | **To be authored upon Eric YES** | Privacy redaction and master census validation test (MF-7) |
| `numista_mobile/tool/generate_catalog_html.dart` | **To be authored upon Eric YES** | Generates static HTML entrypoints in `build/web/catalog/` |
| `numista_backend/data/cpg_retail_feed_v2026.11.json` | **To be acquired (Eric decision)** | Commercial retail price feed |
| `numista_backend/_scripts/join_cpg_catalog_feed.py` | **Deferred (Eric decision)** | Build-time retail price join script |
| `numista_mobile/test/screens/catalog_soft404_routing_test.dart` | **To be authored upon Eric YES** | Route and unknown-NAC widget tests |
| `numista_mobile/test/web/static_route_html_test.py` | **To be authored upon Eric YES** | Static HTML generator and canonical tag tests |

---

## 8. Pricing Content, AuthGate Precedence, and Operational Gates

### 8.1 Ground Truth in `public_info_screens.dart`
Checking `git show 4d17ca5e:numista_mobile/lib/screens/public_info_screens.dart`:
- Line 362: `'Free During Beta — Pricing TBA'`
- Line 396: `'\$0 / month'`
- Line 407: `'...completely free for registered participants.'`
- Line 412: `'...Existing beta accounts will be grandfathered—you will not be asked to pay for your active beta access.'`

### 8.2 Fail-Closed Pricing & Coverage Surface Copy (v2.0 MF-1b)
Until a separate explicit Founder YES authorizes paid tiers or a world-numismatics release date, **both `generate_catalog_html.dart` (`/pricing/index.html`) and `public_info_screens.dart` MUST emit ONLY the 4 established free-beta strings** verified in `4d17ca5e:numista_mobile/lib/screens/public_info_screens.dart:362, 396, 407, 412`:
- `'Free During Beta — Pricing TBA'` (`:362`)
- `'\$0 / month'` (`:396`)
- `'...completely free for registered participants.'` (`:407`)
- `'...Existing beta accounts will be grandfathered—you will not be asked to pay for your active beta access.'` (`:412`)

**Hard Prohibitions (Fail-Closed):**
- Paid pricing (`$30 / 6 months`) and world-coverage ETA (`2027`) are **removed from active output** (prohibited in generated `/pricing/index.html`, widgets, fixtures, and screenshots until explicit Founder approval).
- US-only remains the operative scope (`Numista.AI currently supports United States coinage and currency.`).
- Promo codes remain strictly private: no promo-code literal appears in this plan, generated pages, fixtures, or tests.
- Credit card checkout remains offline (`Stripe OFF`).

### 8.3 AuthGate Public Route Precedence (`widgets/auth_gate.dart`)
In `git show 4d17ca5e:numista_mobile/lib/widgets/auth_gate.dart`:
- Lines 101–103: `if (snapshot.connectionState == ConnectionState.waiting) return _buildSplash();`
- Lines 106–148: `if (snapshot.hasData && snapshot.data != null)` (Signed-in checks precede public route).
- Lines 157–159: `if (widget.publicRoute != null) return PublicInfoShell(targetRoute: widget.publicRoute!);`

#### Solution:
Move the `widget.publicRoute != null` check **immediately after** `snapshot.connectionState == ConnectionState.waiting`, ensuring that a signed-in user navigating directly to `/pricing` or `/about` views the requested public screen rather than being forced to `BaseLayout()`.

---

## 9. Automated Testing Strategy (Resolving MF-2 and MF-5)

### 9.1 Served-Response Tests on Preview Channel
Executed **after** §7.2 widget tests pass and `PREVIEW_URL` is captured from `firebase hosting:channel:deploy`:

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${PREVIEW_URL:?Set PREVIEW_URL from §7.2 firebase hosting:channel:deploy output}"

echo "=== Test 1: Real Per-Coin URL (HTTP 200 + Per-Coin Canonical) ==="
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PREVIEW_URL/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3")
[ "$STATUS" -eq 200 ] || { echo "FAIL: Expected 200, got $STATUS"; exit 1; }
BODY=$(curl -sS "$PREVIEW_URL/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3")
echo "$BODY" | grep -F '<link rel="canonical" href="https://numista.ai/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3"'
echo "$BODY" | grep -F '<meta property="og:title" content="Numista.AI Reference Catalog – 1921-P Morgan Silver Dollars"'

echo "=== Test 2: Invalid NAC Code URL (HTTP 200 + Soft-404 Noindex) ==="
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PREVIEW_URL/catalog/NAC1.CN.US.NONEXISTENT.BASE.9")
[ "$STATUS" -eq 200 ] || { echo "FAIL: Expected 200, got $STATUS"; exit 1; }
BODY=$(curl -sS "$PREVIEW_URL/catalog/NAC1.CN.US.NONEXISTENT.BASE.9")
echo "$BODY" | grep -F '<meta name="robots" content="noindex, follow">'
# Valid per-coin page must NOT carry noindex
curl -sS "$PREVIEW_URL/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3" | grep -qi 'name="robots" content="noindex' && { echo "FAIL: valid page noindexed"; exit 1; } || true

# Test 2b (browser, not curl): headless Chromium (e.g. Playwright, to be added with approval) loads the unknown URL,
# waits for Flutter, asserts the _CatalogNotFoundBanner text is visible and location.pathname == '/catalog'.
# curl tests prove served HTML/status only; they do NOT prove main.dart dispatch or widget behavior.

echo "=== Test 3: Catalog Root URL (HTTP 200) ==="
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PREVIEW_URL/catalog")
[ "$STATUS" -eq 200 ] || { echo "FAIL: Expected 200, got $STATUS"; exit 1; }

echo "=== Test 4: Pricing URL (HTTP 200) ==="
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PREVIEW_URL/pricing")
[ "$STATUS" -eq 200 ] || { echo "FAIL: Expected 200, got $STATUS"; exit 1; }

echo "=== Test 5: Legal URLs (HTTP 200) ==="
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PREVIEW_URL/privacy")
[ "$STATUS" -eq 200 ] || { echo "FAIL: Expected 200, got $STATUS"; exit 1; }
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PREVIEW_URL/terms")
[ "$STATUS" -eq 200 ] || { echo "FAIL: Expected 200, got $STATUS"; exit 1; }

echo "=== Test 6: Unrelated Bad Path (Authentic HTTP 404) ==="
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PREVIEW_URL/arbitrary-nonexistent-path-98765")
[ "$STATUS" -eq 404 ] || { echo "FAIL: Expected 404, got $STATUS"; exit 1; }

echo "All Preview Served-Response Tests PASSED!"
```

### 9.2 `PublicCatalogRoutingHarness` & `main.dart` Dispatch Tests (`test/screens/catalog_soft404_routing_test.dart`) — To Be Authored

#### 9.2.1 Architecture Note on `main.dart` Top-Level Testing (Resolving MF-4)
In Flutter Web, top-level `void main() async` in `lib/main.dart` binds to platform browser window globals (`Uri.base`, `window.location.pathname`) that are absent in the headless `testWidgets` environment. Furthermore, executing `main()` triggers global `Firebase.initializeApp()` and platform-level services. Therefore:
1. The route parsing and NAC extraction logic from `main.dart:154–181` is factored into a pure, headless-testable helper function `extractInitialNac(Uri uri)` that lives in **production code** at `numista_mobile/lib/routing/public_catalog_route.dart` (v1.7 E3). `main.dart` imports it (`import 'routing/public_catalog_route.dart';`) and calls `extractInitialNac(Uri.base)` in the dispatch; the unit test imports the same file, so tests exercise the shipped function, not a copy.
2. The headless unit tests below validate this extraction logic against `/catalog`, `/catalog/:nac`, and `?item=:nac`.
3. End-to-end routing into `CatalogBrowseScreen` is verified via the preview curl tests in §9.1 and widget pump tests below.

```dart
// numista_mobile/lib/routing/public_catalog_route.dart (PRODUCTION file; v1.7 E3)
// Pure routing helper extracted from main.dart:154-181
String? extractInitialNac(Uri uri) {
  final path = uri.path;
  final normalizedPath = path.endsWith('/') && path.length > 1 
      ? path.substring(0, path.length - 1) 
      : path;
  if (normalizedPath == '/catalog' || path.startsWith('/catalog/')) {
    String? initialNacCode;
    if (path.startsWith('/catalog/')) {
      final sub = path.substring('/catalog/'.length).trim();
      if (sub.isNotEmpty) {
        try {
          initialNacCode = Uri.decodeComponent(sub);
        } on ArgumentError {
          initialNacCode = sub;
        }
      }
    }
    if (initialNacCode == null && uri.queryParameters.containsKey('item')) {
      initialNacCode = uri.queryParameters['item'];
    }
    return initialNacCode;
  }
  return null;
}
```

#### 9.2.2 Test Suite Implementation
All imports use `package:numista_ai/...` and test real NAC codes:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_ai/routing/public_catalog_route.dart'; // v1.7 E3: real helper, not a local copy

void main() {
  group('main.dart Dispatch Route Extraction (MF-4)', () {
    test('extractInitialNac: returns null for bare /catalog', () {
      final uri = Uri.parse('https://numista.ai/catalog');
      expect(extractInitialNac(uri), isNull);
    });

    test('extractInitialNac: parses NAC from /catalog/<nac>', () {
      final uri = Uri.parse('https://numista.ai/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3');
      expect(extractInitialNac(uri), equals('NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3'));
    });

    test('extractInitialNac: parses NAC from query parameter ?item=<nac>', () {
      final uri = Uri.parse('https://numista.ai/catalog?item=NAC1.CN.US.1C.LINCOLNCEN.1909.S.BASE.2');
      expect(extractInitialNac(uri), equals('NAC1.CN.US.1C.LINCOLNCEN.1909.S.BASE.2'));
    });

    test('extractInitialNac: returns null for non-catalog path', () {
      final uri = Uri.parse('https://numista.ai/pricing');
      expect(extractInitialNac(uri), isNull);
    });
  });

  testWidgets('Routing: Catalog loads successfully with light theme', (tester) async {
    // Load bundled/fixture catalog asset & stub network images before pumpAndSettle
    TestWidgetsFlutterBinding.ensureInitialized();
    await tester.pumpWidget(
      const MaterialApp(
        home: CatalogBrowseScreen(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Public Catalog'), findsOneWidget);
    expect(find.text('U.S. Numismatics Catalog'), findsOneWidget);
    expect(find.byType(TextField), findsOneWidget); // Search bar
  });

  testWidgets('Pricing: Fail-closed copy excludes unapproved tier & ETA', (tester) async {
    expect(find.textContaining(r'$30 / 6 months'), findsNothing);
    expect(find.textContaining('2027'), findsNothing);
  });

  testWidgets('Routing: Valid NAC code auto-selects and displays detail', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: CatalogBrowseScreen(initialNacCode: 'NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3'),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('1921-P Morgan Silver Dollars'), findsWidgets);
  });

  testWidgets('Routing: Unknown NAC code displays persistent in-screen banner', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: CatalogBrowseScreen(initialNacCode: 'NAC1.CN.US.NONEXISTENT.BASE.9'),
      ),
    );
    await tester.pumpAndSettle();

    expect(
      find.textContaining('Reference code "NAC1.CN.US.NONEXISTENT.BASE.9" was not found in the public catalog.'),
      findsOneWidget,
    );
  });
}
```

### 9.3 `CensusAndPrivacyHarness` (`test/services/catalog_census_privacy_test.dart`) – To Be Authored
Loads `assets/catalog/catalog_public_v1.json` directly from the asset manifest:
```dart
import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('Census: Public catalog contains exactly 3,202 records and zero PII', () async {
    final file = File('assets/catalog/catalog_public_v1.json');
    expect(file.existsSync(), isTrue, reason: 'Public catalog asset must exist');

    final content = await file.readAsString();
    final List<dynamic> catalog = jsonDecode(content);

    expect(catalog.length, equals(3202));

    int coins = 0;
    int notes = 0;
    int medals = 0;

    final forbiddenKeys = [
      'uid', 'email', 'userId', 'purchase_price', 'private_notes',
      'cert_number', 'cost_basis', 'user_id', 'acquisition_date'
    ];

    for (final item in catalog) {
      final map = item as Map<String, dynamic>;
      final type = map['type'] as String?;
      if (type == 'coin') coins++;
      if (type == 'note') notes++;
      if (type == 'medal') medals++;

      // Verify foreign exclusion: segment 2 of nac_code must be US
      final nac = map['nac_code'] as String;
      final parts = nac.split('.');
      expect(parts.length, greaterThan(2));
      expect(parts[2], equals('US'), reason: 'All records must be US numismatics');

      for (final key in forbiddenKeys) {
        expect(map.containsKey(key), isFalse, reason: 'Public catalog must not contain $key');
      }
    }

    expect(coins, equals(2965));
    expect(notes, equals(181));
    expect(medals, equals(56));
  });
}
```

### 9.3a Image Guard Tests (v1.8 F3) – To Be Authored (`test/services/catalog_image_guard_test.dart`)
```dart
// rejects
expect(isApprovedCatalogImageUrl('https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fu1%2Fphoto.jpg?alt=media'), isFalse);
expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/u1/original.jpg'), isFalse);
expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/us_mint_coin_images/../numista-uploads-studio-9101802118-8c9a8/users/u1/x.jpg'), isFalse);
expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/us_mint_coin_images/%2E%2E/other/x.jpg'), isFalse);
expect(isApprovedCatalogImageUrl('https://user@storage.googleapis.com/us_mint_coin_images/x.png'), isFalse);
expect(isApprovedCatalogImageUrl('assets/catalog/images/../../secret.png'), isFalse);
// v1.9 MF-F3-RawPath: in-allowlist normalization must still be rejected (raw check, pre-parse)
expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/us_mint_coin_images/a/../x.jpg'), isFalse);
expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/us_mint_coin_images/./x.jpg'), isFalse);
expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference/a/../x.jpg'), isFalse);
expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/us_mint_coin_images/../numista-reference-library/x.jpg'), isFalse);
// accepts (fixture URL shapes from pin emitters; fixtures, not claims that these objects exist)
expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference/fixture_program/fixture_doc.jpg'), isTrue);
expect(isApprovedCatalogImageUrl('https://storage.googleapis.com/us_mint_coin_images/fixture.png'), isTrue);
// Call-site wiring verification (MF-2):
// Both catalog_browse_screen.dart:918 and :1106 import and call isApprovedCatalogImageUrl()
// from package:numista_ai/utils/catalog_image_guard.dart before Image.network().
// An unapproved URL (e.g., private firebasestorage) falls back to _buildNoPhotoBox() / _buildPlaceholder().
```

### 9.4 `StaticRouteHtmlHarness` (`test/web/static_route_html_test.py`) – To Be Authored
Inspects output artifacts in `build/web/` using real NAC code:
```python
import os
import unittest

class TestStaticCatalogHtml(unittest.TestCase):
    def test_per_coin_html_exists_and_has_canonical(self):
        coin_path = os.path.join('build', 'web', 'catalog', 'NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3', 'index.html')
        self.assertTrue(os.path.exists(coin_path), "Per-coin static HTML must exist for 1921 Morgan")
        with open(coin_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('<link rel="canonical" href="https://numista.ai/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3"', content)
        self.assertIn('<meta property="og:title" content="Numista.AI Reference Catalog – 1921-P Morgan Silver Dollars"', content)
        self.assertIn('<base href="/"', content)
        # v2.0: primary_image is null on 1921-P Morgan; og:image and twitter:image MUST be omitted
        self.assertNotIn('<meta property="og:image"', content)
        self.assertNotIn('<meta name="twitter:image"', content)

    def test_catalog_root_html_exists(self):
        root_path = os.path.join('build', 'web', 'catalog', 'index.html')
        self.assertTrue(os.path.exists(root_path), "Catalog root static HTML must exist")
        with open(root_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('<link rel="canonical" href="https://numista.ai/catalog"', content)

    def test_pricing_html_exists(self):
        pricing_path = os.path.join('build', 'web', 'pricing', 'index.html')
        self.assertTrue(os.path.exists(pricing_path), "Pricing static HTML must exist")
        with open(pricing_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('<link rel="canonical" href="https://numista.ai/pricing"', content)
        self.assertNotIn('$30 / 6 months', content)
        self.assertNotIn('2027', content)

if __name__ == '__main__':
    unittest.main()
```

---

## 10. Multi-Agent Review Chain & Operational Submission

| Stage | Reviewer | Criteria | Target |
|---|---|---|---|
| 1 | Grok Bot Chief of Staff | Architectural completeness, minimal surgical merge diff, real NAC codes, honest CPG status, census grounding, served-response tests, reverse revert order | $\ge 95 / 100$ |
| 2 | Stand Alone Grok (SAG) | Independent verification & security check | $\ge 95 / 100$ |
| 3 | Founder Eric | Final operational gating | Explicit Typed YES |

**Author Signature:**  
*Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)*  
*Timestamp: 2026-11-07 20:45:00 -05:00*


---

## 11. Document Revision & Delivery History
- **2026-11-07 ~21:45 ET (v1.6 Delivery):** Delivered Plan v1.6 (Attempt 4/4) resolving all 7 must-fixes from `COS_SCORE_NET-814_SOFT404-CATALOG-PRICING_v1.5_20261107.md` (86 FAIL) and `RADIO_NET-850`. Re-quoted `origin/dev:main.dart` lines 154–181 (MF-1); grounded call sites in `catalog_browse_screen.dart:466/810/80` (MF-2); corrected pin `firebase.json` line labels to 51–133 and 135–234 (MF-3); added pure `extractInitialNac` route unit tests and architecture explanation (MF-4); cleaned 1921 Morgan OG tags and omitted `og:image` when null (MF-5); aligned Valuation Pending chip to slate gray everywhere (MF-6); added `catalog_census_privacy_test.dart` to §7.5 manifest (MF-7); recorded v1.5 delivery commit `4a124977`.
- **2026-11-07 ~20:45 ET (v1.5 Delivery):** Delivered Plan v1.5 at commit `4a124977`.
- **2026-11-07 ~19:50 ET (v1.4 Delivery):** Delivered Plan v1.4.
- **2026-11-07 ~19:35 ET (v1.3 Delivery):** Delivered Plan v1.3.
- **2026-11-08 ~07:34 ET (v1.7, GB CoS fresh writer):** Closes E1–E3 only (CoS-90 remaining defects). PLAN ONLY. File manifest addition: `numista_mobile/lib/routing/public_catalog_route.dart` (New, to be authored upon Eric YES; holds `extractInitialNac`).
- **2026-11-08 ~07:55 ET (v1.8, GB CoS fresh writer round 2):** Closes CoS-88 MF-1..MF-4 only (F1–F4). PLAN ONLY. Manifest additions: generator output `build/web/catalog_unknown.html`; `test/services/catalog_image_guard_test.dart` (both to be authored on Eric YES).
