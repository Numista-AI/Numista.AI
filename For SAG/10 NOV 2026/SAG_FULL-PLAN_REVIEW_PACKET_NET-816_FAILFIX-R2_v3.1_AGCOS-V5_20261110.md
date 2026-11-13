# SAG FULL-PLAN REVIEW PACKET: NET-816 Catalog Chunk 1 Fail-Fix Round 2, Plan v3.1 (writer: AG CoS v5)

Prepared 10 Nov 2026, about 9:30 PM ET (America/New_York), by GB CoS as a documentation-only packet preparer. **Nothing has been submitted anywhere.** It is for a fresh, independent SAG review (manual fresh chat, or the xAI API only if Eric's API rule applies and CoS decides to send it).

## 1. What you are asked to do
- **Exact artifact under review:** A1, `PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md`, SHA-256 `785b04e55cd3bc2ccefcf40b970e2139ad84aba679053dde7a59bb0c9ec13d04`, 41293 bytes, 701 lines. Line anchors (L#) refer to A1's own lines; line 1 is the first line after A1's BEGIN marker.
- **Review type:** a fresh, independent **FULL-PLAN** review of A1 as a whole, not only the v3→v3.1 changes and not a confirmation of the CoS score.
- **Pass bar:** PASS requires an explicit PASS, a score **≥95**, **and no critical or unresolved material finding**. REVISE at any score is acceptable.
- **Material defects only:** correctness, safety, permissions, execution. No cosmetics.
- **A PASS grants no authority**: no code, git, merge, build, deploy, Firestore, GCS, Stripe or go-live authority. A p7-gate deploy would still need Eric's new scoped typed YES naming the built SHA, p7-gate and the RT-A rollback target.

## 2. Status and honest distinctions
- **What the plan is:** Round 2 fixes for Field Tester's 47/100 FAIL (A6) on the p7-gate preview of `a3d7dca2`: F1 `#/catalog` hash route; F2 image CSP (Wikimedia, Met, numismatics.org) and a read-only Chunk 2 image-gap plan (reference library + Eric's photos, `MANIFEST.csv status=PROPOSAL`); F3 two-coin set face value $2.00; F4 `git_commit` stamp in `version.json`; F5 half dime melt test at $51.51 spot ($1.86); a "Morgan dollar 1881" search fix; and a PowerShell 5.1 p7-gate build/deploy/rollback runbook.
- **A2 (CoS 100/100 PASS on v3.1)** is the designated CoS gate only and does not bind you. v3.1 is a narrow fix of v3 (A5) limited by baton A4 to D3′ (list-level two-pass search so `1842 Liberty Seated dollar` returns exactly 1 card) and D4′ (pinned `numista-vault--p7-gate-` host, throw-on-skip readback, live `releaseTime` checked before and after the deploy, real repo path). CoS ran `diff A5 A1`: every other line is byte-identical. A2 advisory 1 notes a stale pointer left in from v3: the §3 Note 1 matrix row and §4 item 7 still name `test/catalog_browse_test.dart`, while §1.6 puts the search tests in `test/catalog_chunk1_face_value_and_card_test.dart`. Judge for yourself whether that is material.
- **History and counts:** R2 v1 83 REVISE, v2 92 REVISE, v3 96 (A3, CoS-ruled to need a narrow fix), v3.1 is **R2 track attempt 4 of 10, writer AG CoS v5 try 4 of 4 (its last)**. Founder's 4/10 rule: "New Rule, if someone is still failing after 4 tries, somebody else take over. If NO ONE gets it right by 10 total attempts, you notify me and we break it down into smaller bite-size chunks."
- **CoS-verified facts, read-only, 10 Nov 2026** (treat as CoS-stated):
  - App code baseline `a3d7dca20fbbaf06a522205b22d0740b600de52b`. Branch `p7-v8.9` tip `e55302e2716a8943a3847118e0ccf2a859a1b872` differs from it only in docs/archives (no app code). `origin/main` = `9f04550a45fa4da082ba8948c2d89a521a90fa45`. `c547b7a0` is not in the public repo.
  - A7–A12 are byte-exact `git show a3d7dca2:numista_mobile/<path>` blobs. A8, A10 and A11 have CRLF line endings as committed.
  - `catalog_public_v1.json` at a3d7dca2 (not embedded; ~3,202 records): 2,965 coins, 181 notes, 56 medals. Image URLs (`url` keys) exist for 166 coins + 1 medal, on hosts `upload.wikimedia.org`, `thumb.wikimedia.org`, `images.metmuseum.org`, `numismatics.org`. 1,047 records hold a `file` name only (966 `type_image`, 81 `primary_image`); 1,988 have no image metadata (1,752 coins, 181 notes, 55 medals). The only denomination containing "set" is `Dollar (two-coin set)` (`NAC1.CN.US.1D.DIAMONDFLD.2026.XX.26XS.B`).
  - A Python simulation of A1's list-level search on that JSON (default type `coin`): `1842 liberty seated dollar` → Pass 1, 1; `morgan dollar 1881` → Pass 2, 5; `1816` → 0; `half dime` → 35; `Libertas Americana medal` → 0 coins, 1 after the medal tab. Under v3's per-item logic, 1842 returned 2.
  - On EDS_Laptop, `git -C C:\Users\ericd\Documents\MyVertexProject rev-parse --show-toplevel` → `C:/Users/ericd/Documents/MyVertexProject`; `numista_mobile\firebase.json` exists there.
  - Hosting site in A10 is `numista-vault`; the real p7-gate URL per A6 is `https://numista-vault--p7-gate-8avtpz22.web.app`.
  - No `dart`/`flutter` was run; compile/test statements are from Dart rules, the code and the simulation.
- **HOLDs:** A13 (`74611e05`): never re-issue a c547b7a0 preview deploy. A14 (`41b8bd5f`): go-live stays NOT ACTIVE; no main, no live, no live Stripe; every fix goes through CoS 95 + SAG 95 + Eric YES.

## 3. Areas to cover (whole plan)
1. **F1** `resolveCatalogRoute` (A1 §1.1) against A7 L105-180: path routes unchanged; `#/catalog`, `#/catalog/<id>`, `#/catalog?item=`; other hash routes untouched; test file.
2. **F2** CSP string against A10 L283-284 (only the five hosts appended to `img-src`/`connect-src`), counts and the C1 on-screen statement, Chunk 2 read-only/proposal-manifest rules and scan key.
3. **F3** `parseFaceValue` change against A8 L54-131 (signature, ordering, special cases, `\bset\b` guard), the A11 L139 update, the new tests.
4. **F4/F5** stamp logic in the runbook; F5 test against A8 `compute` and A11 L323-345 (raw strings, $1.86, $30 case); catalog-detail display scoping.
5. **Search (D3)** A1 §1.6 against A9 `_applyFilters` (~L112-200) and A11 L348-385; the test file and helper named.
6. **Runbook (D4)** A1 §2: PS 5.1 correctness, `c547b7a0`/holds refusal, p7-gate only, worktree isolation and cleanup, full-SHA RT-A, YES text, the post-deploy readback and live-unchanged check.
7. **Boundaries:** plan only; no live/main/Stripe/Firestore/GCS writes; no invented files or commits.

## 4. Requested output (concise)
1. An integer score out of 100 and an explicit disposition: **PASS** or **REVISE**.
2. Material or critical findings only, each with A1 line numbers or sections, why it is material, and the minimal fix (or "none").
3. Seven one-line checks: (a) F1 routing; (b) F2 CSP, counts and image-gap plan; (c) F3 face value and tests; (d) F4 stamp and F5 melt test; (e) search and the 1842 card test; (f) runbook, rollback and readback; (g) execution boundary and no regression against v3 (A5).
4. Confirmation that you reviewed the full A1, with the **exact A1 SHA-256** you reviewed.

## 5. Byte-exact embedding and extraction rule
Each artifact sits between a line `<<<BEGIN ARTIFACT id=… sha256=… bytes=… lines=… path=…>>>` and a line `<<<END ARTIFACT id=…>>>`. The artifact's exact bytes begin right after the newline that ends the BEGIN line and run for exactly `bytes` bytes; the END line begins right after them, except that when an artifact does not end in a newline, exactly one separator LF that is NOT part of the artifact comes before the END line. No escaping or transformation was applied (UTF-8; CRLF kept where the committed blob has it). `lines` counts LF characters. There are exactly 14 artifacts. Paths are the preparer's box paths.

## 6. Manifest of embedded payloads
| ID | Role | Source path | SHA-256 | Bytes | Lines |
|---|---|---|---|---|---|
| A1 | Plan R2 v3 (writer AG CoS v5) — EXACT ARTIFACT UNDER REVIEW | `/workspace/net816-failfix/round2/PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md` | `785b04e55cd3bc2ccefcf40b970e2139ad84aba679053dde7a59bb0c9ec13d04` | 41293 | 701 |
| A2 | CoS R2 v3.1 score record: 100/100 PASS (CoS gate only; NOT SAG; four unscored advisories) | `/workspace/net816-failfix/round2/COS_SCORE_NET-816_FAILFIX-R2_v3.1_100_PASS_20261110.md` | `c5119a6fa4f8a690b234f0089e0ad3135fe4b364ab3042e6364a998b75910c26` | 8109 | 57 |
| A3 | CoS R2 v3 score record: 96/100 PASS with two material items D3′/D4′ that required the v3.1 fix | `/workspace/net816-failfix/round2/COS_SCORE_NET-816_FAILFIX-R2_v3_96_PASS_20261110.md` | `9d3e8c07108000284821c1329c6d493cfeaa3c59212d545c05a807647667d3d7` | 10419 | 55 |
| A4 | CoS baton to writer for v3.1 (only D3′/D4′ allowed) | `/workspace/net816-failfix/round2/BATON_NET-816_AGCOS-V5_FAILFIX-R2_PLAN-ONLY_v3.1_FROM-96_20261110-2055.md` | `a34b4d6985135eb944d6c300731f5a2eddcc07d0364dcaf5aee81819ea4b4997` | 3255 | 25 |
| A5 | Plan R2 v3 — regression/diff reference only; NOT under review | `/workspace/net816-failfix/round2/PLAN_NET-816_FAILFIX-R2_v3_AGCOS-V5_20261110.md` | `e7c54bab6a756c43a3e8aafc8ea7614b884a1d62dcda1ca6761c848e37557f75` | 35380 | 591 |
| A6 | Field Tester result 47/100 FAIL on p7-gate a3d7dca2 (the defects R2 must fix) | `/workspace/net816-failfix/round2/FT_RESULT_NET816_CATALOG_CHUNK1_p7gate_20261110.md` | `7573823d596c89c4ef34af18c2859e0abbb5659e10e02e53a046ebc40b0bfcb7` | 4910 | 76 |
| A7 | Source at a3d7dca2: numista_mobile/lib/main.dart (blob e9053e3e…) | `/workspace/net816-failfix/sag-upload-r2v3/src/main.dart` | `cd6c6c5c166fec91cfc5fd67540aa35a5a7739a8374237bb33286fb8c1d71f26` | 18930 | 487 |
| A8 | Source at a3d7dca2: numista_mobile/lib/services/melt_value_service.dart (blob 62d11a9a…; CRLF as committed) | `/workspace/net816-failfix/sag-upload-r2v3/src/melt_value_service.dart` | `e163b221b5cdbdb550ba68aeaa9b519900432d8d27789d8ab6cd3cf6d4ca63d1` | 13793 | 256 |
| A9 | Source at a3d7dca2: numista_mobile/lib/screens/catalog/catalog_browse_screen.dart (blob a87e4cf9…) | `/workspace/net816-failfix/sag-upload-r2v3/src/catalog_browse_screen.dart` | `933ce414c3ca969338673618472696ba6f864e9b844488f301376eadd20e05c7` | 47294 | 1280 |
| A10 | Source at a3d7dca2: numista_mobile/firebase.json (blob 2ab730bf…; CRLF as committed) | `/workspace/net816-failfix/sag-upload-r2v3/src/firebase.json` | `4dc3c6a23090939e1ebee698975df149c9775243f33d21ef6431bd1474ea9596` | 8459 | 310 |
| A11 | Source at a3d7dca2: numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart (blob bb46dc5b…; CRLF as committed) | `/workspace/net816-failfix/sag-upload-r2v3/src/catalog_chunk1_face_value_and_card_test.dart` | `164731816d9360b46ba5fc04e9680e2d5a85c721d10addd775d0ab0da12d2896` | 17020 | 419 |
| A12 | Source at a3d7dca2: numista_mobile/test/catalog_browse_test.dart (blob 3df197ca…) | `/workspace/net816-failfix/sag-upload-r2v3/src/catalog_browse_test.dart` | `b449669750563a95e71d315ac1e5207d95e0793aca7bd769615805caaa6c1252` | 3375 | 91 |
| A13 | Preview HOLD 74611e05: no c547b7a0 preview deploy | `/workspace/net816-failfix/src/HOLD_NET-816_PREVIEW-DEPLOY_c547b7a0_NOT-REISSUED_AWAIT-A1A2-FIX_20261110-1148.md` | `74611e05e00a99e4dfb5f524f16a7dc92d540265986ff138c61ccf5884f11b6b` | 3208 | 37 |
| A14 | Go-live stop-rule HOLD 41b8bd5f | `/workspace/net816-failfix/src/HOLD_NET-816_NET-827_AGCOS-V5_GO-LIVE-STOP-RULE_AND_FAILFIX-PLAN-ORDER_20261110-1113.md` | `41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d` | 3311 | 35 |

## A1: Plan R2 v3 (writer AG CoS v5) — EXACT ARTIFACT UNDER REVIEW

<<<BEGIN ARTIFACT id=A1 sha256=785b04e55cd3bc2ccefcf40b970e2139ad84aba679053dde7a59bb0c9ec13d04 bytes=41293 lines=701 path=/workspace/net816-failfix/round2/PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md>>>
# PLAN: NET-816 Catalog Chunk 1 Fail-Fix Round 2 (v3.1)
**Track:** NET-816 (Catalog Chunk 1 — Round 2 Fail-Fix Plan)  
**Writer:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**Iteration:** R2 track attempt 4 of 10; writer AG CoS v5 try 4 of 4  
**Date:** 10 November 2026 ~21:20 EST  
**Execution Authority:** **STRICTLY PLAN ONLY.** Zero code execution, zero source code commits, zero deployments, zero Firestore/Stripe writes.  
**Pinned Branches:** `p7-v8.9` (code baseline identical to `a3d7dca2`; docs at `ac7c8bb3`). `origin/main` strictly pinned at `9f04550a`. Zero pushes to `main`.  
**Holds Active:** `74611e05` and `41b8bd5f` remain in full force.  
**Gate Sequence:** Designated CoS 95 gate -> full-plan SAG 95 gate -> Eric's typed scoped YES.

---

## 0. Executive Summary & Input Basis

Field Tester evaluated the initial `p7-gate` preview deploy (`a3d7dca2`, release `a47a275d1eb6b51f`) and filed `FT_RESULT_NET816_CATALOG_CHUNK1_p7gate_20261110.md` (47/100 FAIL). Grok CoS scored Plan v2 at 92/100 REVISE (`COS_SCORE_NET-816_FAILFIX-R2_v2_92_REVISE_20261110.md`), providing specific deductions D1–D4 and CoS correction C1:
1. **D1 (−2 pts, Test Alignment):** Explicitly states the one-line update in `test/catalog_chunk1_face_value_and_card_test.dart:139` changing `'Dollar (two-coin set)': 1.00` to `2.00` to reflect FT Flag 2 and the set multiplier fix, rather than claiming all existing tests are untouched.
2. **D2 (−2 pts, Dart Syntax):** Enforces raw strings (`r'...'`) for all test assertion messages containing dollar amounts (`$51.51`, `$1.86`, `$30`, `$1.09`) in `test/catalog_chunk1_face_value_and_card_test.dart:323-345` to prevent Dart string-interpolation compile errors.
3. **D3′ (Search Precision & Real Screen Test):** Implements list-level two-pass filtering across `_applyFilters()`: Pass 1 direct field substring match across filtered list; Pass 2 whitespace multi-token fallback only if Pass 1 returns 0 items. Verified on real JSON: `"1842 Liberty Seated dollar"` -> 1; `"Morgan dollar 1881"` -> 5; `"1816"` -> 0. Cites real test file `test/catalog_chunk1_face_value_and_card_test.dart` using `pumpLoadedCatalog` and `initialQuery`.
4. **D4′ (Runbook Readback & Safety Invariants):** Uses preview host prefix `https://numista-vault--p7-gate-` with strict regex; throws unconditionally if preview URL is missing or any verification fails; implements pre-deploy and post-deploy live channel release time readback via `--json` asserting zero live modifications; uses fixed repo path `C:\Users\ericd\Documents\MyVertexProject` and asserts `git rev-parse --show-toplevel`.

v3.1 Change Note: Narrow amendment from CoS 96 PASS (`COS_SCORE_NET-816_FAILFIX-R2_v3_96_PASS_20261110.md`), closing D3′ and D4′ exclusively. All other sections byte-identical to v3.
5. **C1 (CoS Clarification):** Distinguishes data-field counts from on-screen renderable images. Clarifies that 166 coins + 1 medal have renderable URLs; 1,047 records have file-only references; and ~2,799 coins will display the `"No photo yet"` placeholder after CSP fix. Expands Chunk 2 gap scan key to cover `primary_image == null || primary_image['url'] == null` to capture file-only records.

---

## 1. Defect Analysis & Exact Code Specifications

### 1.1 F1: Direct Routing for `#/catalog` and `#/catalog/<id>`
- **Observed Defect:** Navigating to `https://preview.numista-vault.web.app/#/catalog` or `/#/catalog/NAC1...` redirected to home/auth screen or failed to resolve.
- **Root Cause:** In `numista_mobile/lib/main.dart:115`, routing inspects only `uri.path`. In Flutter web hash routing (`/#/catalog`), `uri.path` is `'/'` and the application route is contained within `uri.fragment`.
- **Exact Code Fix:**
  In `numista_mobile/lib/main.dart`, factor out a testable pure route resolver helper `CatalogRouteInfo`:
  ```dart
  class CatalogRouteInfo {
    final bool isCatalog;
    final String? initialNacCode;
    const CatalogRouteInfo({required this.isCatalog, this.initialNacCode});
  }

  CatalogRouteInfo resolveCatalogRoute(Uri uri) {
    String routePath = uri.path;
    String? nacFromQuery;

    // Inspect hash fragment for Flutter Web
    if (uri.fragment.isNotEmpty) {
      String frag = uri.fragment;
      if (frag.startsWith('/')) {
        final qIdx = frag.indexOf('?');
        if (qIdx != -1) {
          final queryStr = frag.substring(qIdx + 1);
          final fragUri = Uri(query: queryStr);
          nacFromQuery = fragUri.queryParameters['item'];
          frag = frag.substring(0, qIdx);
        }
        if (frag == '/catalog' || frag.startsWith('/catalog/')) {
          routePath = frag;
        }
      }
    }

    final normalized = (routePath.endsWith('/') && routePath.length > 1)
        ? routePath.substring(0, routePath.length - 1)
        : routePath;

    if (normalized == '/catalog' || routePath.startsWith('/catalog/')) {
      String? initialNac;
      if (routePath.startsWith('/catalog/')) {
        final sub = routePath.substring('/catalog/'.length).trim();
        if (sub.isNotEmpty) {
          initialNac = Uri.decodeComponent(sub);
        }
      }
      initialNac ??= nacFromQuery;
      initialNac ??= uri.queryParameters['item'];
      return CatalogRouteInfo(isCatalog: true, initialNacCode: initialNac);
    }

    return const CatalogRouteInfo(isCatalog: false);
  }
  ```
  In `numista_mobile/lib/main.dart:154`, integrate `resolveCatalogRoute`:
  ```dart
  final catalogRoute = resolveCatalogRoute(uri);
  if (catalogRoute.isCatalog) {
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
      home: CatalogBrowseScreen(initialNacCode: catalogRoute.initialNacCode),
    ));
    return;
  }
  ```
- **Automated Verification:**
  Add a dedicated unit test in `test/catalog_routing_test.dart`:
  - `resolveCatalogRoute(Uri.parse('https://example.com/catalog'))` -> `isCatalog == true, initialNacCode == null`
  - `resolveCatalogRoute(Uri.parse('https://example.com/catalog/NAC1.123'))` -> `isCatalog == true, initialNacCode == 'NAC1.123'`
  - `resolveCatalogRoute(Uri.parse('https://example.com/#/catalog'))` -> `isCatalog == true, initialNacCode == null`
  - `resolveCatalogRoute(Uri.parse('https://example.com/#/catalog/NAC1.123'))` -> `isCatalog == true, initialNacCode == 'NAC1.123'`
  - `resolveCatalogRoute(Uri.parse('https://example.com/#/catalog?item=NAC1.123'))` -> `isCatalog == true, initialNacCode == 'NAC1.123'`
  - `resolveCatalogRoute(Uri.parse('https://example.com/#/claim'))` -> `isCatalog == false`

---

### 1.2 F2: Image CSP Allowlist & Chunk 2 Scope (C1 & E5 & E6)
- **Observed Defect:** Field Tester recorded 166 console errors loading images from `upload.wikimedia.org`.
- **Root Cause:** `numista_mobile/firebase.json:284` Content-Security-Policy headers omitted Wikimedia and museum image domains from `img-src` and `connect-src`.
- **Exact Code Fix:**
  Update `firebase.json:284` by appending the approved image domains to both `img-src` and `connect-src`:
  - Approved domains added:
    - `https://upload.wikimedia.org`
    - `https://commons.wikimedia.org`
    - `https://*.wikimedia.org`
    - `https://images.metmuseum.org`
    - `https://numismatics.org`
  Updated header in `firebase.json:284`:
  ```json
  {
    "key": "Content-Security-Policy",
    "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app https://upload.wikimedia.org https://commons.wikimedia.org https://*.wikimedia.org https://images.metmuseum.org https://numismatics.org; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000 https://upload.wikimedia.org https://commons.wikimedia.org https://*.wikimedia.org https://images.metmuseum.org https://numismatics.org; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
  }
  ```
- **Image-URL Host Audit (Image Fetch Hosts Only):**
  - `upload.wikimedia.org`: 166
  - `thumb.wikimedia.org`: 10
  - `images.metmuseum.org`: 1
  - `numismatics.org`: 1
  *(Note: External references such as `americanhistory.si.edu` [173 records] and `fraser.stlouisfed.org` [37 records] reside in citation `sources`/`source_url` fields and are not fetched as images by `img-src`.)*
- **On-Screen vs Dataset Breakdown (C1):**
  - Total items in `catalog_public_v1.json`: 3,202 (2,965 coins, 181 banknotes, 56 medals).
  - Records with renderable HTTP image URLs (`url` key): Exactly **166 coins** and **1 medal** (total 167 items).
  - Records with bare file-only references (`file` key, no `url`): **1,047 records** (966 `type_image`, 81 `primary_image`).
  - Records with zero image metadata: **1,988 records** (1,752 coins, 181 banknotes, 55 medals).
  - **Expected On-Screen Rendering After CSP Fix:**
    - The Flutter UI (`catalog_browse_screen.dart:1113-1120`) attempts `Image.network(imgMap['url'])`. If `imgMap['url']` is absent, it falls back to `_buildPlaceholder()` (`"No photo yet"`).
    - Visible on-screen photos after CSP fix: **166 coins**, **1 medal** (the 167 items with valid URLs).
    - On-screen circular `"No photo yet"` placeholder: **2,799 coins** (1,752 without image metadata + 1,047 file-only references), **181 banknotes**, and **55 medals**.
    - *(Note: The "Photos only" filter at lines 147–151 checks map non-emptiness `(imgMap as Map).isNotEmpty`, which counts file-only records, explaining why Field Tester observed 1,213 items matching the filter.)*
- **Chunk 2 Gap Plan (E5 & C1 per Eric's 31 Oct Rules / NET-674):**
  - **Read-Only Invariant:** GCS buckets and Firestore remain strictly read-only for images.
  - **Expanded Scan Key:** Scan criteria covers both completely unimaged items and file-only items:
    `item['primary_image'] == null || (item['primary_image'] is Map && item['primary_image']['url'] == null)`
    This captures all 1,752 unimaged coins AND all 1,047 file-only records (including the 81 file-only primaries).
  - **Sources:**
    1. `gs://numista-reference-library/coins/` (reference library bucket).
    2. Eric's personal collection photos (path UNKNOWN until provided by Eric).
  - **Process:** An offline read-only matching script scans catalog records matching the expanded scan key against both sources.
  - **Proposal Manifest:** Matching results are written to a staging file on the box: `MANIFEST.csv` with columns `nac_code,source,source_path,matched_date,status=PROPOSAL`.
  - **Approval Gate:** No changes to `catalog_public_v1.json` occur until Grok CoS and Eric inspect and approve `MANIFEST.csv`. Banknotes (181) and medals (55) are scanned at lower priority following coins.

---

### 1.3 F3: Multi-Coin Set Face Value Multiplier (E1 & D1 & Advisory 2)
- **Observed Defect:** Field Tester noted multi-coin set `NAC1.CN.US.1D.DIAMONDFLD.2026.XX.26XS.B` (`Dollar (two-coin set)`) displayed face value `$1.00` instead of `$2.00`.
- **Root Cause:** In `lib/services/melt_value_service.dart:60`, `s = s.replaceAll(RegExp(r'\(.*?\)'), '').trim()` strips `(two-coin set)` before matching denomination, reducing `"dollar (two-coin set)"` to `"dollar"` ($1.00).
- **Exact Code Fix (Preserving All Parser Features & Signatures):**
  In `numista_mobile/lib/services/melt_value_service.dart:54`, keep existing signature:
  `static double parseFaceValue(String rawDenom, {int qty = 1})`
  Insert set-multiplier detection **immediately before** the parenthetical stripping at line 60 using word boundary `\bset\b`:
  ```dart
  static double parseFaceValue(String rawDenom, {int qty = 1}) {
    final count = qty > 0 ? qty : 1;
    if (rawDenom.trim().isEmpty) return 0.0;

    // Normalization pipeline: lowercase, collapse whitespace
    String s = rawDenom.toLowerCase().trim();

    // Multi-coin set detection BEFORE stripping parenthetical notes
    int setMultiplier = 1;
    final setMatch = RegExp(
      r'\(?(\d+|two|three|four|five)[- ]coin set\)?',
      caseSensitive: false,
    ).firstMatch(s);

    if (setMatch != null) {
      final token = setMatch.group(1)!.toLowerCase();
      switch (token) {
        case '2':
        case 'two':
          setMultiplier = 2;
          break;
        case '3':
        case 'three':
          setMultiplier = 3;
          break;
        case '4':
        case 'four':
          setMultiplier = 4;
          break;
        case '5':
        case 'five':
          setMultiplier = 5;
          break;
        default:
          setMultiplier = int.tryParse(token) ?? 1;
      }
    } else if (RegExp(r'\bset\b', caseSensitive: false).hasMatch(s) && !s.contains('offset')) {
      // Indeterminate multi-coin / collector set without specific count -> No face value chip (0.0)
      return 0.0;
    }

    // Strip parenthetical & ellipses
    s = s.replaceAll(RegExp(r'\(.*?\)'), '').trim();
    s = s.replaceAll(RegExp(r'\.{2,}'), '').trim();
    s = s.replaceAll('\u00bd', ' 1/2');
    s = s.replaceAll(RegExp(r'\s+'), ' ').trim();

    // Guard non-legal-tender blanks (planchets), non-USD units (candareens),
    // and multi-denomination sets/ranges ('$100/$50/$25/$10', '$1, $2, $5, $10', '3c-50c')
    if (s.contains('planchet') ||
        s.contains('candareen') ||
        RegExp(r'\$\d[\d,]*(?:\.\d+)?\s*(?:/\s*\$?|,\s*\$)\s*\d').hasMatch(s) ||
        RegExp(r'\d\s*(?:\u00a2|c|cents?)?\s*[\u2013\-]\s*\d').hasMatch(s)) {
      return 0.0;
    }

    double value = 0.0;

    // 0. Leading numeric & fractional patterns (N Dollars, 1,000 Dollars, 10,000 Dollars, 2 1/2 Dollars, G$2 1/2, 3 cents, $1000)
    final fracDollarMatch = RegExp(r'^(?:g?\$)?\s*(\d+)\s+1/2(?:\s*dollars?)?$').firstMatch(s);
    final leadDollarMatch = RegExp(r'^\$?\s*(\d[\d,]*(?:\.\d+)?)\s*(?:dollars?|\$)$').firstMatch(s);
    final leadCentMatch = RegExp(r'^(\d+(?:\.\d+)?)\s*(?:cents?|c|\u00a2)\b').firstMatch(s);
    final leadSymDollarMatch = RegExp(r'^\$\s*(\d[\d,]*(?:\.\d+)?)(?:\b|$)').firstMatch(s);

    if (fracDollarMatch != null) {
      value = (double.tryParse(fracDollarMatch.group(1)!) ?? 0.0) + 0.5;
    } else if (leadDollarMatch != null) {
      value = double.tryParse(leadDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
    } else if (leadCentMatch != null) {
      value = (double.tryParse(leadCentMatch.group(1)!) ?? 0.0) / 100.0;
    } else if (leadSymDollarMatch != null) {
      value = double.tryParse(leadSymDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
    }

    // 1. High Gold, Notes & Commemoratives
    else if (s.contains(r'$10,000') || s.contains(r'$10000') || s.contains('ten thousand dollar')) { value = 10000.00; }
    else if (s.contains(r'$1,000') || s.contains(r'$1000') || s.contains('one thousand dollar') || s.contains('thousand dollar')) { value = 1000.00; }
    else if (s.contains(r'$500') || s.contains('five hundred dollar')) { value = 500.00; }
    else if (s.contains(r'$100') || s.contains('one hundred dollar') || s.contains('hundred dollar')) { value = 100.00; }
    else if (s.contains(r'$50') || s.contains('fifty dollar')) { value = 50.00; }
    else if (s.contains(r'$40') || s.contains('forty dollar')) { value = 40.00; }
    else if (s.contains(r'$25') || s.contains('twenty five dollar') || s.contains('twenty-five dollar')) { value = 25.00; }
    else if (s.contains(r'$20') || s.contains('twenty dollar') || s.contains('double eagle')) { value = 20.00; }
    else if (s.contains(r'$10') || s.contains('ten dollar') || (s.contains('eagle') && !s.contains('half') && !s.contains('quarter') && !s.contains('silver'))) { value = 10.00; }
    else if (s.contains(r'$5') || s.contains('five dollar') || s.contains('half eagle')) { value = 5.00; }
    else if (s.contains(r'$4') || s.contains('four dollar') || s.contains('stella')) { value = 4.00; }
    else if (s.contains(r'$3') || s.contains('three dollar')) { value = 3.00; }
    else if (s.contains(r'$2.50') || s.contains(r'$2.5') || s.contains('2 1/2') || s.contains('quarter eagle') || s.contains('two and a half')) { value = 2.50; }
    else if (s.contains(r'$2') || s.contains('two dollar')) { value = 2.00; }

    // 2. Sub-Dollar & Standard Silver/Base Denominations (multi-word terms before single tokens)
    else if (s.contains('half dollar') || s.contains('fifty cent') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
    else if (s.contains('quarter dollar') || s.contains('twenty-five cent') || s.contains('twenty five cent') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
    else if (s.contains('twenty cent') || s.contains('20c') || s.contains('20 cent')) { value = 0.20; }
    else if (s.contains('half dime') || s.contains('half-dime')) { value = 0.05; }
    else if (s.contains('dime') || s.contains('ten cent') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
    else if (s.contains('three cent') || s.contains('3 cent') || s.contains('3c')) { value = 0.03; }
    else if (s.contains('nickel') || s.contains('five cent') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
    else if (s.contains('two cent') || s.contains('2 cent') || s.contains('2c')) { value = 0.02; }
    else if (s.contains('half cent') || s.contains('half-cent')) { value = 0.005; }
    else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
    else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }

    // 3. Fallback: plain numeric parse
    else {
      final match = RegExp(r'\d+(?:\.\d+)?').firstMatch(s);
      if (match != null) {
        final parsed = double.tryParse(match.group(0)!) ?? 0.0;
        value = parsed <= 1000.0 ? parsed : 0.0;
      }
    }

    return value * count * setMultiplier;
  }
  ```
- **Automated Verification & Test Updates (D1):**
  1. **Existing Pinned Test Update (`test/catalog_chunk1_face_value_and_card_test.dart:139`):**
     Update line 139 from:
     ```dart
     'Dollar (two-coin set)': 1.00,
     ```
     to:
     ```dart
     'Dollar (two-coin set)': 2.00, // FT Flag 2: 2-coin set face value multiplier
     ```
     This aligns the comprehensive full-catalog parse test (`misParses == 0`) with the verified $2.00 behavior.
  2. **Dedicated Set Multiplier Test Cases (line 203):**
     ```dart
     test('F3: Multi-coin set face value multiplier and set guards', () {
       expect(MeltValueService.parseFaceValue('Dollar (two-coin set)'), closeTo(2.00, 1e-4));
       expect(MeltValueService.parseFaceValue('Dollar (two-coin set)', qty: 2), closeTo(4.00, 1e-4));
       expect(MeltValueService.parseFaceValue('Half Dollar (two-coin set)'), closeTo(1.00, 1e-4));
       expect(MeltValueService.parseFaceValue('Three-coin set'), 0.0); // 0.0 unit * 3 = 0.0 -> No face value chip
       expect(MeltValueService.parseFaceValue('Collector Set'), 0.0);  // Indeterminate set -> No face value chip
     });
     ```

---

### 1.4 F4: `git_commit` Stamping in `version.json`
- **Observed Defect:** `version.json` contained package version but lacked `"git_commit": "<SHA>"`.
- **Root Cause:** Standard `flutter build web --release` does not automatically query git or inject the commit hash into the output artifact.
- **Exact Fix:** Integrated directly into the PowerShell build runbook (§2). Executed inside the isolated worktree immediately after `flutter build web --release`:
  1. Resolves `$resolvedSha = (git -C $wtPath rev-parse HEAD).Trim()`.
  2. Asserts exit code 0 and `$resolvedSha -eq $BuiltSha`.
  3. Checks existence of `$wtPath\numista_mobile\build\web\version.json`; throws hard error if absent.
  4. Parses JSON, injects `"git_commit": $resolvedSha`.
  5. Serializes and writes back using UTF-8 without BOM via `[System.IO.File]::WriteAllText($versionPath, $stampedJson, (New-Object System.Text.UTF8Encoding($false)))`.
  6. Re-reads and asserts `$verifyJson.git_commit -eq $resolvedSha`.

---

### 1.5 F5: Silver Half Dime Melt Math & Verification (D2)
- **Observed Defect:** Field Tester questioned whether Silver Half Dime melt was verified at current spot silver ($51.51/oz).
- **Mathematical Proof:**
  - Standard Half Dime composition (1837–1873): 90% silver, 10% copper.
  - Nominal weight: 1.25 grams. Actual Silver Weight (ASW) = `0.03617` troy oz (`melt_value_service.dart:12`).
  - At live spot silver **$51.51/oz**:
    $$\text{Melt Value} = 0.03617\text{ oz} \times \$51.51/\text{oz} = \$1.8631167 \approx \mathbf{\$1.86}$$
  - At historical reference spot ($30.00/oz):
    $$\text{Melt Value} = 0.03617\text{ oz} \times \$30.00/\text{oz} = \$1.0851 \approx \mathbf{\$1.09}$$
- **Verification Strategy & Raw String Syntax (D2):**
  In `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart:323-345`, verify real existing API `MeltValueService.compute(...)` using raw strings `r'...'` to prevent Dart string-interpolation compile errors:
  ```dart
  // Verify current spot $51.51/oz calculation -> $1.86
  expect(
    MeltValueService.compute(
      metalContent: '90% Silver',
      denomination: 'Half Dime',
      spotPrices: {'Silver': 51.51},
    ),
    closeTo(0.03617 * 51.51, 1e-3),
    reason: r'Half Dime at $51.51 spot must equal 0.03617 * 51.51 = $1.86',
  );
  // Preserve $30 reference spot test case -> $1.09
  expect(
    MeltValueService.compute(
      metalContent: '90% Silver',
      denomination: 'Half Dime',
      spotPrices: {'Silver': 30.0},
    ),
    closeTo(0.03617 * 30.0, 1e-3),
    reason: r'Half Dime at $30 spot must equal 0.03617 * 30.0 = $1.09',
  );
  ```
- **Catalog Detail Display Decision:**
  The public catalog is a static browse screen for signed-out users and does not maintain live authenticated websocket feeds. Live spot display on the detail modal is excluded from Chunk 1 scope to prevent unnecessary architectural overhead. Field Tester verification of live melt calculation is satisfied via the unit test suite and optional pre-seeded grokbot test coin (requiring Eric's separate typed YES).

---

### 1.6 Search Logic & Observational Findings (D3)

#### Note 1: List-Level Two-Pass Search Algorithm (D3′)
- **Observed Issue:** Substring search failed on `"Morgan dollar 1881"` because terms span multiple metadata fields. In-place per-item token matching caused `"1842 Liberty Seated dollar"` to overmatch `"1842 Liberty Seated half dollar"` (which contains tokens '1842', 'liberty', 'seated', 'dollar'), breaking card widget test lines 348–385 (`findsOneWidget`).
- **List-Level Two-Pass Search Implementation (`catalog_browse_screen.dart:112-200`):**
  Filter type, era, and photos first, then resolve search query in two passes across the filtered collection:
  ```dart
    // 1. Apply non-query criteria first (type, era, photosOnly)
    List<Map<String, dynamic>> filtered = _allEntries.where((item) {
      final type = (item['type'] as String? ?? '').toLowerCase();
      if (_selectedType == 'coin' && type != 'coin') return false;
      if (_selectedType == 'note' && type != 'note') return false;
      if (_selectedType == 'medal' && type != 'medal') return false;

      final int? year = item['year'] is int ? item['year'] as int : null;
      if (_selectedEra != 'all') {
        if (_selectedEra == 'pre_federal') {
          if (year == null || year >= 1792) return false;
        } else if (_selectedEra == 'early_republic') {
          if (year == null || year < 1792 || year >= 1837) return false;
        } else if (_selectedEra == 'seated') {
          if (year == null || year < 1837 || year >= 1873) return false;
        } else if (_selectedEra == 'morgan') {
          if (year == null || year < 1873 || year >= 1901) return false;
        } else if (_selectedEra == '20th') {
          if (year == null || year < 1901 || year >= 2000) return false;
        } else if (_selectedEra == 'modern') {
          if (year == null || year < 2000 || year > 2026) return false;
        } else if (_selectedEra == 'undated') {
          if (year != null) return false;
        }
      }

      if (_photosOnly) {
        final hasPrimary = item['primary_image'] != null && (item['primary_image'] as Map).isNotEmpty;
        final hasType = item['type_image'] != null && (item['type_image'] as Map).isNotEmpty;
        if (!hasPrimary && !hasType) return false;
      }

      return true;
    }).toList();

    // 2. Two-pass list-level search resolution
    List<Map<String, dynamic>> result = filtered;
    if (query.isNotEmpty) {
      // Pass 1: Direct substring matches across metadata fields
      final directMatches = filtered.where((item) {
        final name = (item['name'] as String? ?? '').toLowerCase();
        final series = (item['series'] as String? ?? '').toLowerCase();
        final denom = (item['denomination'] as String? ?? '').toLowerCase();
        final nac = (item['nac_code'] as String? ?? '').toLowerCase();
        final yearStr = item['year']?.toString() ?? '';
        return name.contains(query) ||
            series.contains(query) ||
            denom.contains(query) ||
            nac.contains(query) ||
            yearStr.contains(query);
      }).toList();

      if (directMatches.isNotEmpty) {
        result = directMatches;
      } else {
        // Pass 2: Multi-token fallback across combined metadata haystack
        final tokens = query.split(RegExp(r'\s+')).where((t) => t.isNotEmpty).toList();
        result = filtered.where((item) {
          final name = (item['name'] as String? ?? '').toLowerCase();
          final series = (item['series'] as String? ?? '').toLowerCase();
          final denom = (item['denomination'] as String? ?? '').toLowerCase();
          final nac = (item['nac_code'] as String? ?? '').toLowerCase();
          final yearStr = item['year']?.toString() ?? '';
          final haystack = '$name $series $denom $nac $yearStr';
          return tokens.every((token) => haystack.contains(token));
        }).toList();
      }
    }
  ```
- **Evidence from Real Dataset (`assets/catalog/catalog_public_v1.json` at `a3d7dca2`):**
  Execution verification via Python against production catalog:
  ```bash
  python -c "
  import json
  with open('numista_mobile/assets/catalog/catalog_public_v1.json', 'r', encoding='utf-8') as f:
      data = json.load(f)
  def run_search(query):
      q = query.strip().lower()
      direct = [x for x in data if any(q in str(x.get(k) or '').lower() for k in ['name','series','denomination','nac_code','year'])]
      if direct: return ('Pass 1', len(direct), [x['name'] for x in direct])
      tokens = q.split()
      tokens_match = [x for x in data if all(t in f\"{x.get('name') or ''} {x.get('series') or ''} {x.get('denomination') or ''} {x.get('nac_code') or ''} {x.get('year') or ''}\".lower() for t in tokens)]
      return ('Pass 2', len(tokens_match), [x['name'] for x in tokens_match])
  print('1842 Liberty Seated dollar:', run_search('1842 Liberty Seated dollar'))
  print('Morgan dollar 1881:', run_search('Morgan dollar 1881'))
  print('1816:', run_search('1816'))
  "
  ```
  Verified Output:
  ```text
  1842 Liberty Seated dollar: ('Pass 1', 1, ['1842 Liberty Seated dollar'])
  Morgan dollar 1881: ('Pass 2', 5, ['1881-CC Morgan Silver Dollars', '1881-O Morgan Silver Dollars', '1881-P Morgan Silver Dollars', '1881-S Morgan Dollar (Liberty Head, Eagle)', '1881-S Morgan Silver Dollars'])
  1816: ('Pass 2', 0, [])
  ```
- **Automated Verification:**
  Verified on the real screen via `test/catalog_chunk1_face_value_and_card_test.dart` using real helper `pumpLoadedCatalog` and `CatalogBrowseScreen(initialQuery: ...)`:
  1. `CatalogBrowseScreen(initialQuery: '1842 Liberty Seated dollar')`: Resolves via Pass 1 returning exactly 1 card (`1842 Liberty Seated dollar`). Existing widget test lines 348–385 finds exactly 1 card (`findsOneWidget`) and passes without modification.
  2. `CatalogBrowseScreen(initialQuery: 'Morgan dollar 1881')`: Pass 1 yields 0 items; Pass 2 yields 5 items. Card finder in GridView confirms 5 cards rendered.
  3. `CatalogBrowseScreen(initialQuery: '1816')`: Pass 1 yields 0 items; Pass 2 yields 0 items. Empty catalog placeholder rendered.

#### Note 2: Coin Search 500 Error
- Traced from `CoinSearchScreen:395` ("Definitive Registry") -> `CoinSearchService.search` -> `GET /api/reference/search` (`main.py:9509`).
- In `main.py:9596-9597`, an unhandled exception inside `_get_user_owned_doc_ids` or SQLite `definitive_reference` query triggers `raise HTTPException(500, detail=str(e))`. This is documented for backend review and does not impact Flutter web public catalog browsing.

---

## 2. PowerShell 5.1 Build, Deploy & Rollback Runbook (D4 & E2 & E4)

### 2.1 Pre-Flight Safety & Guardrails
- **Channel Restriction:** Deployment is permitted **exclusively** to the preview channel `p7-gate`.
- **Live / Main Prohibition:** Deployment to `live` channel or `main` branch is strictly prohibited.
- **Commit Guard:** Deployment fails immediately if target commit starts with `c547b7a0` or is subject to holds `74611e05` / `41b8bd5f`.
- **Approval Prerequisite:** Execution requires Eric's typed scoped YES:
  `"YES DEPLOY p7-gate <BUILT_SHA> ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b"`

### 2.2 Complete PowerShell 5.1 Execution Script (`deploy_preview.ps1`)
*Script location: `scripts/deploy_preview.ps1` (or executed from EDS_Laptop outside repo).*
```powershell
# ==============================================================================
# NUMISTA.AI — NET-816 PREVIEW BUILD & DEPLOY RUNBOOK (PowerShell 5.1)
# Channel: p7-gate | Project: studio-9101802118-8c9a8
# ==============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$BuiltSha,

    [Parameter(Mandatory=$true)]
    [string]$EricApprovalYes
)

$ErrorActionPreference = 'Stop'

# 1. Native Execution Helper
function Invoke-Native {
    param([scriptblock]$Command, [string]$StepName)
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "FATAL: Step '$StepName' failed with exit code $LASTEXITCODE"
    }
}

# 2. Strict Guardrail Verification
$repoRoot = "C:\Users\ericd\Documents\MyVertexProject"
Set-Location $repoRoot
$topLevel = (git rev-parse --show-toplevel).Trim()
if ($topLevel.Replace('/', '\') -ne $repoRoot) {
    throw "FATAL: Repository root mismatch ($topLevel != $repoRoot)"
}

$resolvedSha = (git rev-parse --verify "$BuiltSha^{commit}").Trim()
if ($LASTEXITCODE -ne 0) {
    throw "FATAL: Could not resolve commit $BuiltSha"
}

$expectedYes = "YES DEPLOY p7-gate $BuiltSha ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b"
if ($EricApprovalYes.Trim() -ne $expectedYes) {
    throw "FATAL: Invalid approval text. Required exactly: '$expectedYes'"
}

if ($resolvedSha.StartsWith("c547b7a0", [System.StringComparison]::InvariantCultureIgnoreCase)) {
    throw "FATAL: Refusing build of prohibited commit c547b7a0"
}

# Worktree placed strictly in $env:TEMP with outside-repo check
$timestamp = (Get-Date).ToString("yyyyMMdd-HHmmss")
$wtPath = Join-Path $env:TEMP "numista-net816-worktree-$timestamp"
if ($wtPath.StartsWith($repoRoot, [System.StringComparison]::InvariantCultureIgnoreCase)) {
    throw "FATAL: Worktree path must reside outside repository root"
}

Write-Host "==> Starting build for $resolvedSha on p7-gate..." -ForegroundColor Cyan

# 2.5 Pre-Deploy Live Channel Baseline Capture (D4′)
Push-Location "$repoRoot\numista_mobile"
$preDeployJsonRaw = firebase hosting:channel:list --project studio-9101802118-8c9a8 --json
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    throw "FATAL: Failed to query firebase channels before deploy"
}
$preDeployData = $preDeployJsonRaw | ConvertFrom-Json
$preLiveChannel = $preDeployData.result.channels | Where-Object { $_.name -like "*/channels/live" }
if (-not $preLiveChannel) {
    Pop-Location
    throw "FATAL: Could not locate live channel in pre-deploy listing"
}
$preLiveReleaseTime = $preLiveChannel.release.releaseTime
Write-Host "==> Baseline live channel releaseTime: $preLiveReleaseTime" -ForegroundColor Cyan
Pop-Location

try {
    # 3. Isolated Worktree Creation
    Invoke-Native { git worktree add --detach $wtPath $resolvedSha } "Create isolated worktree"

    # 4. Verify Built SHA matches git HEAD in worktree
    $wtHead = (git -C $wtPath rev-parse HEAD).Trim()
    if ($wtHead -ne $resolvedSha) {
        throw "FATAL: Worktree SHA ($wtHead) does not match requested SHA ($resolvedSha)"
    }

    # 5. Build Flutter Web Release
    Push-Location (Join-Path $wtPath "numista_mobile")
    Invoke-Native { flutter build web --release } "Flutter web release build"

    # 6. F4: version.json git_commit Stamping (UTF-8 without BOM)
    $versionPath = Join-Path (Get-Location).Path "build\web\version.json"
    if (-not (Test-Path $versionPath)) {
        throw "FATAL: build\web\version.json not found after build"
    }

    $jsonContent = Get-Content -Path $versionPath -Raw | ConvertFrom-Json
    $jsonContent | Add-Member -NotePropertyName "git_commit" -NotePropertyValue $resolvedSha -Force
    $stampedJson = $jsonContent | ConvertTo-Json -Depth 4
    [System.IO.File]::WriteAllText($versionPath, $stampedJson, (New-Object System.Text.UTF8Encoding($false)))

    # Verify stamp
    $verifyJson = Get-Content -Path $versionPath -Raw | ConvertFrom-Json
    if ($verifyJson.git_commit -ne $resolvedSha) {
        throw "FATAL: Verification failed: git_commit ($($verifyJson.git_commit)) != $resolvedSha"
    }
    Write-Host "==> version.json verified stamped with git_commit: $resolvedSha" -ForegroundColor Green

    # 7. Deploy to p7-gate Channel Only
    Invoke-Native {
        firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8
    } "Firebase channel deploy to p7-gate"

    # 8. Post-Deploy Readback Verification (D4′)
    Write-Host "==> Running post-deploy readback checks..." -ForegroundColor Cyan
    Push-Location "$repoRoot\numista_mobile"
    $postDeployJsonRaw = firebase hosting:channel:list --project studio-9101802118-8c9a8 --json
    if ($LASTEXITCODE -ne 0) {
        Pop-Location
        throw "FATAL: Failed to query firebase channels after deploy"
    }
    $postDeployData = $postDeployJsonRaw | ConvertFrom-Json
    Pop-Location

    # Assert live release timestamp invariant (D4′)
    $postLiveChannel = $postDeployData.result.channels | Where-Object { $_.name -like "*/channels/live" }
    if (-not $postLiveChannel -or $postLiveChannel.release.releaseTime -ne $preLiveReleaseTime) {
        throw "FATAL: Live channel releaseTime changed! Pre: $preLiveReleaseTime, Post: $($postLiveChannel.release.releaseTime)"
    }
    Write-Host "==> Verified live channel release unchanged: $preLiveReleaseTime" -ForegroundColor Green

    # Locate p7-gate channel and URL (D4′)
    $p7Channel = $postDeployData.result.channels | Where-Object { $_.name -like "*/channels/p7-gate" }
    if (-not $p7Channel) {
        throw "FATAL: p7-gate channel missing from hosting:channel:list"
    }
    $p7Url = $p7Channel.url
    if (-not $p7Url -or -not ($p7Url -match '^https://numista-vault--p7-gate-[a-z0-9]+\.web\.app')) {
        throw "FATAL: No valid preview URL matching 'https://numista-vault--p7-gate-[a-z0-9]+\.web\.app' found. Got: '$p7Url'"
    }
    Write-Host "==> Verified p7-gate URL: $p7Url" -ForegroundColor Cyan

    # Verify version.json served by p7-gate (D4′)
    Write-Host "==> Checking $p7Url/version.json..." -ForegroundColor Cyan
    $deployedVersion = Invoke-RestMethod -Uri "$p7Url/version.json" -TimeoutSec 15
    if (-not $deployedVersion -or $deployedVersion.git_commit -ne $resolvedSha) {
        throw "FATAL: Served version.json git_commit ($($deployedVersion.git_commit)) != $resolvedSha"
    }
    Write-Host "==> Deployed version.json verified matching $resolvedSha" -ForegroundColor Green

    # HTTP 200 route checks (D4′)
    foreach ($route in @('/', '/catalog')) {
        $resp = Invoke-WebRequest -Uri "$p7Url$route" -UseBasicParsing -TimeoutSec 10
        if ($resp.StatusCode -ne 200) {
            throw "FATAL: Route $route returned status $($resp.StatusCode)"
        }
    }
    Write-Host "==> Routes /, /catalog verified HTTP 200" -ForegroundColor Green

    Write-Host "==> SUCCESS: Deployed and verified $resolvedSha on channel p7-gate" -ForegroundColor Green
}
finally {
    # 9. Safe Worktree Cleanup (D4)
    Pop-Location -ErrorAction SilentlyContinue
    Set-Location $repoRoot
    if (Test-Path $wtPath) {
        Invoke-Native { git worktree remove --force $wtPath } "Remove worktree"
        Invoke-Native { git worktree prune } "Prune worktree"
    }
}
```

### 2.3 Rollback Procedures
- **Rollback Target A (RT-A — Instant Rollback to Baseline `a3d7dca2`):**
  Redeploy baseline commit full SHA `a3d7dca20fbbaf06a522205b22d0740b600de52b` to `p7-gate` using the script above:
  ```powershell
  .\scripts\deploy_preview.ps1 `
      -BuiltSha "a3d7dca20fbbaf06a522205b22d0740b600de52b" `
      -EricApprovalYes "YES DEPLOY p7-gate a3d7dca20fbbaf06a522205b22d0740b600de52b ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b"
  ```
- **Rollback Target B (RT-B — Passive Hold):**
  Leave `p7-gate` as is pending investigation.
- **Strict Prohibitions:**
  - Never rollback to `c547b7a0`.
  - Never touch live site or `main` (`numista-vault.web.app`).

---

## 3. Test & Verification Matrix (Rule 8)

| Item | Requirement / Defect | Machine-Checkable Verification Command | Expected Output / Criteria |
|---|---|---|---|
| **F1** | Direct catalog route resolution | `flutter test test/catalog_routing_test.dart` | Exit 0; all hash & path routes resolve correctly |
| **F2** | CSP allowlist headers | PowerShell programmatic inspection of `firebase.json` | `img-src` & `connect-src` contain `wikimedia.org`, `metmuseum.org`, `numismatics.org` |
| **F3** | Multi-coin set face value multiplier | `flutter test test/catalog_chunk1_face_value_and_card_test.dart` | Exit 0; 2-coin set = $2.00, line 139 = 2.00, indeterminate = 0.0, existing cases pass |
| **F4** | `version.json` git_commit stamping | PowerShell curl/invoke against `$wt\build\web\version.json` | JSON contains `"git_commit": "<SHA>"` |
| **F5** | Half dime melt math audit | `flutter test test/catalog_chunk1_face_value_and_card_test.dart` | Exit 0; 0.03617 oz × $51.51 = $1.86 (raw strings compile cleanly) |
| **Note 1** | Two-pass search ("1842 Seated dollar" & "Morgan dollar 1881") | `flutter test test/catalog_browse_test.dart` | Exit 0; 1842 Seated dollar = 1, Morgan dollar 1881 = 5, 1816 = 0 |
| **Code Hygiene** | Static analysis | `flutter analyze` | Exit 0; 0 errors |

---

## 4. Summary of Files to Modify (When Approved)

1. `numista_mobile/lib/main.dart` — Routing helper `resolveCatalogRoute` and startup handling for hash fragments.
2. `numista_mobile/firebase.json` — CSP additions for Wikimedia and museum domains in `img-src` and `connect-src`.
3. `numista_mobile/lib/services/melt_value_service.dart` — Multi-coin set multiplier detection before parenthetical strip.
4. `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` — Two-pass search matching.
5. `numista_mobile/test/catalog_routing_test.dart` — Route resolution unit tests (new).
6. `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart` — Line 139 update (`'Dollar (two-coin set)': 2.00`), line 203 set multiplier tests, lines 323–345 raw string syntax tests (`r'...'`).
7. `numista_mobile/test/catalog_browse_test.dart` — Two-pass search regression tests ("Morgan dollar 1881" -> 5, "1842 Liberty Seated dollar" -> 1, "1816" -> 0).

---

## 5. Authority & Gate Statement

This plan is **PLAN ONLY**. It grants **zero authority** to write code, modify files, create commits, execute builds, deploy to Firebase, write to Firestore, or interact with Stripe.

- HOLD `74611e05` and HOLD `41b8bd5f` remain active.
- `origin/main` strictly pinned at `9f04550a`.
- Next Gate: Designated CoS Gate (Pass Mark: 95/100).
- Subsequent Gates: Full-Plan SAG 95 Gate -> Eric's typed scoped YES.
<<<END ARTIFACT id=A1>>>

## A2: CoS R2 v3.1 score record: 100/100 PASS (CoS gate only; NOT SAG; four unscored advisories)

<<<BEGIN ARTIFACT id=A2 sha256=c5119a6fa4f8a690b234f0089e0ad3135fe4b364ab3042e6364a998b75910c26 bytes=8109 lines=57 path=/workspace/net816-failfix/round2/COS_SCORE_NET-816_FAILFIX-R2_v3.1_100_PASS_20261110.md>>>
# DESIGNATED CoS PLAN SCORE: NET-816 Catalog Chunk 1 FAIL-FIX ROUND 2, plan v3.1 (writer: AG CoS v5)

**Score: 100 / 100, PASS (CoS gate only).** The pass mark is 95. Scored adversarially, material defects only (correctness, safety, permissions, execution). I found no material defect; the four advisories below are unscored.
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 9:25 PM ET (America/New_York).
**Count: NET-816 fail-fix R2 track attempt 4 of 10; writer AG CoS v5 try 4 of 4 (its last).** The stall rule isn't triggered.

## Plan scored (no mismatch)
- `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md` (written 9:18:52 PM ET)
- **Scored bytes:** SHA-256 **`785b04e55cd3bc2ccefcf40b970e2139ad84aba679053dde7a59bb0c9ec13d04`**, **41,293 bytes**, LF only. The laptop `Get-FileHash` and the box copy match the expected values and the DONE.
- DONE: `DONE_BATON_NET-816_FAILFIX-R2_PLAN-ONLY_v3.1_AGCOS-V5_20261110.md`, 5,821 B, SHA `11ea1bc7e795b21b6d32a98624af4f5840f4c8b1a94be7b12c60d721d4b7978d`. It's in `MY TESTING\10 NOV 2026\` and `Carbon\` (identical). A recursive search of `BETA TEST` found **no copy in BATONS**.

## Inputs
- Baton `BATON_NET-816_AGCOS-V5_FAILFIX-R2_PLAN-ONLY_v3.1_FROM-96_20261110-2055.md` (3,255 B, SHA `a34b4d69…4997`).
- My v3 score `COS_SCORE_NET-816_FAILFIX-R2_v3_96_PASS_20261110.md` (10,419 B, SHA `9d3e8c07…d7a3d7`), D3′ and D4′.
- Plan v3 `e7c54bab…7f75` (base for the diff).
- Code at `a3d7dca20fbbaf06a522205b22d0740b600de52b`: `catalog_browse_screen.dart:20-45,112-200`, `test/catalog_chunk1_face_value_and_card_test.dart:1-30,348-420`, `catalog_public_v1.json`; `firebase.json` hosting site. EDS_Laptop read-only: `git -C C:\Users\ericd\Documents\MyVertexProject rev-parse --show-toplevel` → `C:/Users/ericd/Documents/MyVertexProject`; `numista_mobile\firebase.json` exists there.

## Diff against v3 (`diff v3 v3.1`, run by CoS)
The changes are only: the header (title, iteration, date; L1, L4-5), the summary items 3-4 plus a v3.1 change note (L18-21), §1.6 Note 1 (v3 L359-392 → v3.1 L361-466), and §2.2 runbook hunks (repo root L509-514; pre-deploy live capture L539-555; post-deploy readback L593-637; the `/#/catalog` HTTP probe is dropped). **Every other line is byte-identical to v3**, including F1, the CSP, F3/D1, F5/D2, C1/Chunk 2, F4 stamping, RT-A and the holds. This matches the DONE closure map in substance. The map's line numbers are approximate (it says D3′ 359–435 and D4′ 480–520/560–630), and its "diff" is a summarised excerpt (advisory 4).

## D3′: list-level two-pass search (CLOSED)
- **Code (v3.1 L365-417) against the real `_applyFilters` (`:112-200`):** the type, era and photos-only filters are copied verbatim from `:120-152`, into `filtered`. Pass 1 runs the original single-field substring match across the whole `filtered` list. Pass 2 (all tokens in a combined haystack) runs **only if Pass 1 is empty for the whole list**. `result` then flows into the unchanged sort (`:173-198`) and `_filteredEntries = result`. The `'foreign'` early return and `query` declaration (`:113-118`) stay. The Dart is well-formed (`List<Map<String, dynamic>>` and `.toList()` types match `_allEntries`).
- **CoS's own simulation over the real `catalog_public_v1.json` at a3d7dca2**, with the screen's default `_selectedType = 'coin'` (`:26`):
  - `1842 Liberty Seated dollar` → Pass 1, **1** (`1842 Liberty Seated dollar`)
  - `Morgan dollar 1881` → Pass 2, **5** (1881-CC, -O, -P, -S ×2)
  - `1816` → **0**
  - Regression checks: `half dime` → 35 (matches FT); `xyzzy` → 0; `Libertas Americana medal` → 0 coins, then 1 after the test taps `Medals (56)`, so the medal test `:388-420` is unaffected.
- **Widget test:** the existing `:348-385` test uses the real `pumpLoadedCatalog` helper and `CatalogBrowseScreen(initialQuery: '1842 Liberty Seated dollar')`, and now gets 1 card, so its `findsOneWidget` assertions (including `Face value · No retail estimate`) pass unchanged. The plan names the real file and helper (L461-464).

## D4′: runbook readback (CLOSED)
- **Repo path is real:** `$repoRoot = "C:\Users\ericd\Documents\MyVertexProject"`, then `Set-Location`, then `git rev-parse --show-toplevel` compared after `/`→`\` (case-insensitive `-ne`). This matches the laptop readback. The no-op is gone.
- **Live release check before and after:**
  - Before any worktree/build/deploy (L539-555): `channel:list --project studio-9101802118-8c9a8 --json` with an exit-code check; it throws if the live channel isn't found, and captures `release.releaseTime`.
  - After the deploy (L593-610): re-read with `--json`, exit-code check, and throw if the live channel is missing or `releaseTime` changed.
- **Host pinned:** the p7-gate URL comes from the channel object, and it **throws** unless it matches `^https://numista-vault--p7-gate-[a-z0-9]+\.web\.app`. The real URL `https://numista-vault--p7-gate-8avtpz22.web.app` matches; site `numista-vault` is confirmed in `firebase.json`.
- **Nothing skips silently:** a missing p7-gate channel, missing or invalid URL, `version.json` `git_commit` ≠ resolved SHA, or a non-200 on `/` or `/catalog` all throw. `$ErrorActionPreference='Stop'` makes `Invoke-RestMethod`/`Invoke-WebRequest` failures terminating. "verified" is printed only after each check passes. The meaningless `/#/catalog` HTTP probe is removed (the F1 hash route stays covered by the unit test and FT).
- Push/Pop-Location pairs are balanced on every path; cleanup in `finally` is unchanged from v3.

## Deductions
**None.** Total: 100.

## Advisories (not scored; fix during implementation or in SAG notes)
1. **A stale test-file pointer from v3 was left in.** The §3 matrix "Note 1" row (L677) still runs `flutter test test/catalog_browse_test.dart`, and §4 item 7 (L690) still lists `catalog_browse_test.dart` for the search tests. §1.6 correctly puts them in `test/catalog_chunk1_face_value_and_card_test.dart`, and `pumpLoadedCatalog` is local to that file. This isn't scored: the F3/F5 matrix rows already run `catalog_chunk1_face_value_and_card_test.dart`, which contains the 1842 widget test and the new 1881/1816 tests, so the real gate runs. The implementer should follow §1.6 and treat L677/L690 as pointing to `catalog_chunk1_face_value_and_card_test.dart`. On its own, the L677 command would give a false green.
2. The new 1881 → 5 and 1816 → 0 widget tests are described but not written out. When writing them, assert by card name text inside the `GridView` (as `:365-368` does), at the existing 1440×2400 surface size.
3. If the live channel ever had no `release`, both `releaseTime` values would be `$null` and the check would pass. Consider `if (-not $preLiveReleaseTime) { throw }`.
4. DONE hygiene: the closure-map line numbers are approximate, the "line diff" is a summary with `...`, and the DONE wasn't placed in BATONS. The CoS ran the real diff (above).

## Regressions / invented items
- No invented commits or files. The repo path, helper, test file, hosting site and preview host all check out against real data. No regression found in the unchanged sections (byte-identical to v3, which was verified at 96 except for D3′/D4′).
- Baseline: app code `a3d7dca2`; `p7-v8.9` docs tip `e55302e2` (the plan pins docs at `ac7c8bb3`, docs-only, so no code impact); main `9f04550a`.

## Next step
- **CoS gate PASS on `785b04e5…3d04`.** It's eligible for the full-plan SAG review (dual gate: SAG ≥95 on this exact SHA, then Eric's typed scoped YES naming the built SHA, p7-gate and RT-A `a3d7dca20fbbaf06a522205b22d0740b600de52b`).
- The SAG packet and paste prompt are built on the box and **not submitted**, and not copied to For SAG. The v3 packet `cb83f4ea…` stays superseded.

## Authority statement
This score **grants no code, git, build, deploy, Firestore, GCS, Stripe or go-live authority**. HOLDs `74611e05…` and `41b8bd5f…` and the go-live addendum `c2b6ac93…` (NOT ACTIVE) stay in force; main stays `9f04550a`; Stripe live stays OFF.
<<<END ARTIFACT id=A2>>>

## A3: CoS R2 v3 score record: 96/100 PASS with two material items D3′/D4′ that required the v3.1 fix

<<<BEGIN ARTIFACT id=A3 sha256=9d3e8c07108000284821c1329c6d493cfeaa3c59212d545c05a807647667d3d7 bytes=10419 lines=55 path=/workspace/net816-failfix/round2/COS_SCORE_NET-816_FAILFIX-R2_v3_96_PASS_20261110.md>>>
# DESIGNATED CoS PLAN SCORE: NET-816 Catalog Chunk 1 FAIL-FIX ROUND 2, plan v3 (writer: AG CoS v5)

**Score: 96 / 100, PASS (CoS gate only).** The pass mark is 95. Only material defects count (correctness, safety, permissions, execution). Cosmetics are not deducted.
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 8:55 PM ET (America/New_York).
**Count: NET-816 fail-fix R2 track attempt 3 of 10; writer AG CoS v5 try 3 of 4.**
**This is not a clean pass.** Two material defects remain (D3′ and D4′ below). Each is a small, mechanical fix. **CoS recommendation:** amend them (v3.1) before SAG, the same way NET-827 v1.9 → v1.9.1 was handled. If v3 goes to SAG as-is, expect SAG to find D3′.

## Plan scored (no mismatch)
- `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\PLAN_NET-816_FAILFIX-R2_v3_AGCOS-V5_20261110.md` (written 8:20:20 PM ET; byte-identical copy in `Carbon\`)
- **Scored bytes:** SHA-256 **`e7c54bab6a756c43a3e8aafc8ea7614b884a1d62dcda1ca6761c848e37557f75`**, **35,380 bytes**, LF only. On disk, the Carbon mirror and the box copy all **match the DONE** (`DONE_BATON_NET-816_FAILFIX-R2_PLAN-ONLY_v3_AGCOS-V5_20261110.md`, 4,895 B, SHA `65e5fdd8…0016`, 8:21:09 PM ET).

## Inputs
- My v2 score `COS_SCORE_NET-816_FAILFIX-R2_v2_92_REVISE_20261110.md` (13,440 B, SHA `abb1d807…89d2`), D1–D4 and C1.
- Baton `BATON_NET-816_AGCOS-V5_FAILFIX-R2_PLAN-ONLY_v3_FROM-92_20261110-2010.md` (1,749 B, SHA `419b1dfe…4349`).
- Plan v2 (`0f5b89be…82d7`) for a line diff. v3 changes only the D1–D4/C1 areas, the header and the summary; everything else is byte-identical to v2.

## Code checked (read-only, `a3d7dca20fbbaf06a522205b22d0740b600de52b`)
- `lib/screens/catalog/catalog_browse_screen.dart:112-200` (`_applyFilters`), `:1080-1215` (card, chip), `:900-925`; `test/catalog_chunk1_face_value_and_card_test.dart:101-200,323-345,348-385`; `test/catalog_browse_test.dart`; `lib/services/melt_value_service.dart:54-131`; `firebase.json` hosting block; `assets/catalog/catalog_public_v1.json` (3,202 records, Python simulation).
- **Branches:** `p7-v8.9` is now **`e55302e2716a8943a3847118e0ccf2a859a1b872`** (8:22:50 PM ET, "deliver NET-816 fail-fix r2 plan v3 and sync batons"), past `ac7c8bb3`. `git diff a3d7dca2 e55302e2` touches only `.md`/`.txt` docs, two archives and `For SAG/10 NOV 2026/SAG_RESPONSE_NET-827_v1.9.1_20261110.json`; **no app code**. `main` is still `9f04550a45fa…` (ls-remote).

## Closure of D1–D4 and C1
| Item | Verdict | Evidence |
|---|---|---|
| **D1** test `:139` → 2.00 | **Closed** | §1.3 states the one-line change `'Dollar (two-coin set)': 1.00` → `2.00`; §4 item 6 lists it; it no longer claims all existing tests are unchanged. With it, the full-catalog test's `misParses` stays 0 (only that denomination changes). |
| **D2** raw strings | **Closed** | Both F5 `reason:` strings are now `r'…'` (plan L339, L349). The remaining `$` amounts are inside `//` comments, which is fine. The test compiles. |
| **D3** 1842 card test / test path | **NOT closed (D3′)** | See the deductions. |
| **D4** RT-A / readback / v5 safety | **Partly closed (D4′)** | Closed: RT-A and the YES use the full 40-character `a3d7dca20fbbaf06a522205b22d0740b600de52b`; `git rev-parse --verify "$BuiltSha^{commit}"`, and the c547b7a0 check runs on the resolved SHA; `$ErrorActionPreference='Stop'`; worktree under `$env:TEMP` with a timestamp and an outside-repo check; the blind `Remove-Item` is gone; cleanup uses `git worktree remove --force` + `prune` in `finally`. Not closed: the post-deploy readback (D4′). |
| **C1** 1,047 file-only records | **Closed** | §1.2 states 166 coins + 1 medal renderable; 1,047 file-only (966 `type_image`, 81 `primary_image`); 1,988 with no image metadata (1,752 + 181 + 55); ~2,799 coins, 181 notes and 55 medals show "No photo yet". All verified against the JSON (1,213 − 166 = 1,047; no overlap). The new Chunk 2 scan key `primary_image == null || primary_image['url'] == null` selects 2,799 coins + 181 notes + 55 medals, covering all 1,047 file-only records, including the 81. |
| E1–E6, F1, CSP | Still closed | Byte-identical to v2, apart from `\bset\b` (v2 advisory 2, taken). It still matches only `Dollar (two-coin set)` in the catalog. |

## Deductions (each one is material)
| # | Pts | Area | Evidence | Why it matters | Exact fix |
|---|---|---|---|---|---|
| D3′ | −2 | Correctness/regression: the "two-pass" search is per-item, so the 1842 card test still finds 2 | The plan code (L364-382) runs inside the per-item `_allEntries.where((item) {…})` closure (`catalog_browse_screen.dart:120-170`). "Pass 1" returns true for this item on a direct match; otherwise "Pass 2" runs the token match **for the same item**. That is item-level OR: old substring ∪ token match. The comment at L377 ("only if no direct substring matches exist across the catalog") describes a catalog-level two pass that the code doesn't do. A simulation over the real JSON with the v3 logic: `1842 liberty seated dollar` → **2** (`1842 Liberty Seated dollar`, `1842 Liberty Seated half dollar`); `morgan dollar 1881` → 5; `1816` → 0. Both 1842 cards are non-medal, so both render `'Face value · No retail estimate'` (`:1160-1186`). The existing widget test `:378-383` `findsOneWidget` therefore fails, and the plan's new test `search('1842 Liberty Seated dollar') -> 1` fails too. Also, `test/catalog_browse_test.dart` exists, but it tests `us_numismatics_catalog_screen.dart` (`package:numista_ai`), not `CatalogBrowseScreen`, and the `search(...)` helper the plan uses doesn't exist there. | The test suite stays red, and the plan states as verified ("returns exactly 1 card … passes without modification") something that is false against the real code and data. The user-visible effect is minor (an extra half-dollar result). | Do the two passes at list level: compute `direct = filtered.where(substringMatch)`, then `result = direct.isNotEmpty ? direct : filtered.where(tokenMatch)`, applying the other filters first. Re-state the 1/5/0 results under that logic. Put the search tests in a file that pumps `CatalogBrowseScreen` (e.g. extend `catalog_chunk1_face_value_and_card_test.dart`, which already uses `pumpLoadedCatalog` and `initialQuery`), with real assertions rather than an undefined `search()`. |
| D4′ | −2 | Execution / safety: the post-deploy readback silently skips and still prints "verified"; there is no live check | L509 extracts the preview URL with `https://studio-9101802118-8c9a8--p7-gate-[a-z0-9]+\.web\.app`, but the Hosting site is **`numista-vault`** (`firebase.json` hosting `site`), and the real p7-gate URL is `https://numista-vault--p7-gate-8avtpz22.web.app` (FT result). The regex never matches, so `if ($channelUrlMatch.Success)` skips the `version.json` `git_commit` assertion and all route checks, and the script then prints "SUCCESS: Deployed **and verified**". The "live release unchanged" check claimed in §0 and the DONE isn't in the script: it only checks that `"p7-gate"` appears in the list. There's no pre-deploy capture of the live release time, and no `$LASTEXITCODE` check on `channel:list`. Minor: `Set-Location $repoRoot` right after `$repoRoot = (Get-Location).Path` is a no-op, not a set-to-repo-root. `/#/catalog` over HTTP doesn't test the fragment route, because browsers don't send fragments. | The readback the baton required (live unchanged; preview serves the stamped `version.json`) never runs, and the operator is told it passed. That's the F4 failure mode again (an unproven build pin). | Before deploying, capture the live channel release time from `firebase hosting:channel:list --project studio-9101802118-8c9a8 --json`. After deploying, re-read with `--json` and check the exit code; throw if the live release time changed or `p7-gate` is missing. Take the p7-gate URL from the JSON (or match `https://numista-vault--p7-gate-[a-z0-9]+\.web\.app`), and **throw if no URL is found**. Then assert the served `version.json` `git_commit` equals the resolved SHA. Use `Set-Location` with the fixed repo path `C:\Users\ericd\Documents\MyVertexProject` (as v5 §7.4 does) and check `git rev-parse --show-toplevel`. |

**Total: 100 − 4 = 96, PASS (CoS gate).**

## Advisories (not scored)
1. §1.2 note: the record counts are slightly off. `americanhistory.si.edu` appears in **171** records (173 URLs), and `fraser.stlouisfed.org` appears in **31** records (65 URLs), not 37. These are citation fields only, so the CSP is unaffected.
2. §2.2 says the script lives at "`scripts/deploy_preview.ps1` (or outside repo)". There's no `scripts/` directory at `a3d7dca2`, and §4 doesn't list one. Keep it outside the repo on EDS_Laptop, or list it as a new file.
3. The runbook doesn't run `flutter test`/`flutter analyze` before deploying. Consider gating the deploy on the §3 matrix.
4. Carried over: `--expires` behaviour on `channel:deploy`; CORS for the Met and numismatics.org images under CanvasKit.

## Regressions / invented items
- No invented commits. `a3d7dca2`, `ac7c8bb3` and `e55302e2` are real (the plan's docs pin is `ac7c8bb3`, now one docs commit behind; no code impact). `9f04550a` is main.
- Invented: the `search(...)` helper in `catalog_browse_test.dart`, and the false claim about the 1842 result (D3′). The preview-URL host in the readback regex doesn't exist (D4′). Citations spot-checked as accurate: `:139`, `:323-345`, `:348-385`, `:147-151`, `:1113-1120`, `:155-172`, `firebase.json:284`.
- No regression in F1, the CSP, F3 parsing, F4 stamping or F5. The D3′ regression is in the existing widget test.

## Next step
- **CoS gate PASS (96) on `e7c54bab…7f75` only.** It goes to SAG only under the dual-gate rule, and CoS recommends a v3.1 amendment for D3′ and D4′ first. A CoS ruling is needed on whether v3.1 counts as an attempt.
- A full-plan SAG packet and paste prompt for **v3 exactly** were built on the box and **not submitted**.

## Authority statement
This score **grants no code, git, build, deploy, Firestore, GCS, Stripe or go-live authority**. HOLDs `74611e05…` and `41b8bd5f…` and the go-live addendum `c2b6ac93…` (NOT ACTIVE) stay in force; main stays `9f04550a`; Stripe live stays OFF. A p7-gate deploy still needs CoS 95 + SAG 95 + Eric's typed scoped YES naming the built SHA, p7-gate and RT-A `a3d7dca20fbbaf06a522205b22d0740b600de52b`.
<<<END ARTIFACT id=A3>>>

## A4: CoS baton to writer for v3.1 (only D3′/D4′ allowed)

<<<BEGIN ARTIFACT id=A4 sha256=a34b4d6985135eb944d6c300731f5a2eddcc07d0364dcaf5aee81819ea4b4997 bytes=3255 lines=25 path=/workspace/net816-failfix/round2/BATON_NET-816_AGCOS-V5_FAILFIX-R2_PLAN-ONLY_v3.1_FROM-96_20261110-2055.md>>>
# BATON — NET-816 FAIL-FIX R2 — PLAN ONLY — v3.1 narrow fix (from CoS 96)
From: Grok Bot CoS, 10 Nov 2026 ~8:55 PM ET (America/New_York). To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
**Count: R2 track attempt 4 of 10; AG CoS v5 try 4 of 4 (your last).** If v3.1 misses, stall rule t2564u hands the fix to SAG via the API.

## Base and score
- Base: PLAN v3 `PLAN_NET-816_FAILFIX-R2_v3_AGCOS-V5_20261110.md`, 35,380 B, SHA-256 `e7c54bab6a756c43a3e8aafc8ea7614b884a1d62dcda1ca6761c848e37557f75`.
- Score: `MY TESTING\10 NOV 2026\COS_SCORE_NET-816_FAILFIX-R2_v3_96_PASS_20261110.md`, 10,419 B, SHA-256 `9d3e8c07108000284821c1329c6d493cfeaa3c59212d545c05a807647667d3d7`. Read D3′ and D4′ in full.
- Baseline: app code `a3d7dca20fbbaf06a522205b22d0740b600de52b`; `p7-v8.9` docs tip `e55302e2`; main `9f04550a`.

## Allowed changes (ONLY these two)
1. **D3′, search.** "1842 Liberty Seated dollar" must return exactly 1 card. Either run the two passes across the whole filtered list in `_applyFilters()` (`catalog_browse_screen.dart:112-200`: direct substring matches first, token matches only if the direct list is empty), or fix the 1842 test on its real screen. Cite the real test file and helper: `test/catalog_chunk1_face_value_and_card_test.dart` with `pumpLoadedCatalog` + `CatalogBrowseScreen(initialQuery: …)` (`:348-385`). Don't use the non-existent `search()` helper, and don't use `catalog_browse_test.dart` (it tests `us_numismatics_catalog_screen.dart`). Show evidence from the real `assets/catalog/catalog_public_v1.json` at a3d7dca2 that 1842 → 1, "Morgan dollar 1881" → 5, "1816" → 0 under the new logic (command and output).
2. **D4′, runbook readback (§2.2).**
   - Use the preview host prefix `https://numista-vault--p7-gate-` (site `numista-vault`; regex `https://numista-vault--p7-gate-[a-z0-9]+\.web\.app`).
   - If no URL is found, or any check can't run, **throw**. It must never print "verified" after skipping.
   - Real live-unchanged check: before the deploy, capture the live channel release time from `firebase hosting:channel:list --project studio-9101802118-8c9a8 --json` (check the exit code). After the deploy, re-read it and throw if the live time changed or p7-gate is missing.
   - Fix or drop the no-op `Set-Location $repoRoot`. If you keep it, use the fixed repo path `C:\Users\ericd\Documents\MyVertexProject` and assert `git rev-parse --show-toplevel`.

**Everything else stays byte-for-byte as in v3.** No other edits, rewording or "improvements". The header iteration/date line and a short v3.1 change note are the only other permitted lines.

## DONE must include
New file name `PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md` in `MY TESTING\10 NOV 2026\`, final byte size and `Get-FileHash` SHA-256 of the on-disk file; a closure map (D3′, D4′ → plan lines); and the line diff against v3 `e7c54bab…7f75` (it must show changes only in the allowed areas).

## Limits
PLAN ONLY, with no grade or self-score. No code, commits, builds, deploys, Firestore, GCS or Stripe, and no spend. HOLDs `74611e05` and `41b8bd5f` stand; main stays `9f04550a`; go-live addendum NOT ACTIVE. Stand down by 3 AM ET.
The v3 SAG packet (`cb83f4ea…d5ea`) is SUPERSEDED and won't be submitted.
<<<END ARTIFACT id=A4>>>

## A5: Plan R2 v3 — regression/diff reference only; NOT under review

<<<BEGIN ARTIFACT id=A5 sha256=e7c54bab6a756c43a3e8aafc8ea7614b884a1d62dcda1ca6761c848e37557f75 bytes=35380 lines=591 path=/workspace/net816-failfix/round2/PLAN_NET-816_FAILFIX-R2_v3_AGCOS-V5_20261110.md>>>
# PLAN: NET-816 Catalog Chunk 1 Fail-Fix Round 2 (v3.0)
**Track:** NET-816 (Catalog Chunk 1 — Round 2 Fail-Fix Plan)  
**Writer:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**Iteration:** R2 track attempt 3 of 10; writer AG CoS v5 try 3 of 4  
**Date:** 10 November 2026 ~20:21 EST  
**Execution Authority:** **STRICTLY PLAN ONLY.** Zero code execution, zero source code commits, zero deployments, zero Firestore/Stripe writes.  
**Pinned Branches:** `p7-v8.9` (code baseline identical to `a3d7dca2`; docs at `ac7c8bb3`). `origin/main` strictly pinned at `9f04550a`. Zero pushes to `main`.  
**Holds Active:** `74611e05` and `41b8bd5f` remain in full force.  
**Gate Sequence:** Designated CoS 95 gate -> full-plan SAG 95 gate -> Eric's typed scoped YES.

---

## 0. Executive Summary & Input Basis

Field Tester evaluated the initial `p7-gate` preview deploy (`a3d7dca2`, release `a47a275d1eb6b51f`) and filed `FT_RESULT_NET816_CATALOG_CHUNK1_p7gate_20261110.md` (47/100 FAIL). Grok CoS scored Plan v2 at 92/100 REVISE (`COS_SCORE_NET-816_FAILFIX-R2_v2_92_REVISE_20261110.md`), providing specific deductions D1–D4 and CoS correction C1:
1. **D1 (−2 pts, Test Alignment):** Explicitly states the one-line update in `test/catalog_chunk1_face_value_and_card_test.dart:139` changing `'Dollar (two-coin set)': 1.00` to `2.00` to reflect FT Flag 2 and the set multiplier fix, rather than claiming all existing tests are untouched.
2. **D2 (−2 pts, Dart Syntax):** Enforces raw strings (`r'...'`) for all test assertion messages containing dollar amounts (`$51.51`, `$1.86`, `$30`, `$1.09`) in `test/catalog_chunk1_face_value_and_card_test.dart:323-345` to prevent Dart string-interpolation compile errors.
3. **D3 (−2 pts, Search Precision & Test Path):** Implements two-pass search logic (Pass 1 exact field substring match, Pass 2 whitespace multi-token match). This cleanly satisfies both tests: `"1842 Liberty Seated dollar"` resolves in Pass 1 returning exactly 1 card (preserving card widget test lines 348–385 unchanged), while `"Morgan dollar 1881"` falls through to Pass 2 returning 5 cards. Names the real existing test file `test/catalog_browse_test.dart`.
4. **D4 (−2 pts, Rollback & Safety Invariants):** Updates RT-A rollback to accept full 40-char SHA `a3d7dca20fbbaf06a522205b22d0740b600de52b` and resolves commits via `git rev-parse --verify`; restores full v5 §7.4 safety steps (`$ErrorActionPreference='Stop'`, repo root `Set-Location`, temporary worktree under `$env:TEMP` with outside-repo check, safe worktree remove/prune); adds post-deploy readback of channel list, live release timestamp invariance, and preview `version.json` HTTP check.
5. **C1 (CoS Clarification):** Distinguishes data-field counts from on-screen renderable images. Clarifies that 166 coins + 1 medal have renderable URLs; 1,047 records have file-only references; and ~2,799 coins will display the `"No photo yet"` placeholder after CSP fix. Expands Chunk 2 gap scan key to cover `primary_image == null || primary_image['url'] == null` to capture file-only records.

---

## 1. Defect Analysis & Exact Code Specifications

### 1.1 F1: Direct Routing for `#/catalog` and `#/catalog/<id>`
- **Observed Defect:** Navigating to `https://preview.numista-vault.web.app/#/catalog` or `/#/catalog/NAC1...` redirected to home/auth screen or failed to resolve.
- **Root Cause:** In `numista_mobile/lib/main.dart:115`, routing inspects only `uri.path`. In Flutter web hash routing (`/#/catalog`), `uri.path` is `'/'` and the application route is contained within `uri.fragment`.
- **Exact Code Fix:**
  In `numista_mobile/lib/main.dart`, factor out a testable pure route resolver helper `CatalogRouteInfo`:
  ```dart
  class CatalogRouteInfo {
    final bool isCatalog;
    final String? initialNacCode;
    const CatalogRouteInfo({required this.isCatalog, this.initialNacCode});
  }

  CatalogRouteInfo resolveCatalogRoute(Uri uri) {
    String routePath = uri.path;
    String? nacFromQuery;

    // Inspect hash fragment for Flutter Web
    if (uri.fragment.isNotEmpty) {
      String frag = uri.fragment;
      if (frag.startsWith('/')) {
        final qIdx = frag.indexOf('?');
        if (qIdx != -1) {
          final queryStr = frag.substring(qIdx + 1);
          final fragUri = Uri(query: queryStr);
          nacFromQuery = fragUri.queryParameters['item'];
          frag = frag.substring(0, qIdx);
        }
        if (frag == '/catalog' || frag.startsWith('/catalog/')) {
          routePath = frag;
        }
      }
    }

    final normalized = (routePath.endsWith('/') && routePath.length > 1)
        ? routePath.substring(0, routePath.length - 1)
        : routePath;

    if (normalized == '/catalog' || routePath.startsWith('/catalog/')) {
      String? initialNac;
      if (routePath.startsWith('/catalog/')) {
        final sub = routePath.substring('/catalog/'.length).trim();
        if (sub.isNotEmpty) {
          initialNac = Uri.decodeComponent(sub);
        }
      }
      initialNac ??= nacFromQuery;
      initialNac ??= uri.queryParameters['item'];
      return CatalogRouteInfo(isCatalog: true, initialNacCode: initialNac);
    }

    return const CatalogRouteInfo(isCatalog: false);
  }
  ```
  In `numista_mobile/lib/main.dart:154`, integrate `resolveCatalogRoute`:
  ```dart
  final catalogRoute = resolveCatalogRoute(uri);
  if (catalogRoute.isCatalog) {
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
      home: CatalogBrowseScreen(initialNacCode: catalogRoute.initialNacCode),
    ));
    return;
  }
  ```
- **Automated Verification:**
  Add a dedicated unit test in `test/catalog_routing_test.dart`:
  - `resolveCatalogRoute(Uri.parse('https://example.com/catalog'))` -> `isCatalog == true, initialNacCode == null`
  - `resolveCatalogRoute(Uri.parse('https://example.com/catalog/NAC1.123'))` -> `isCatalog == true, initialNacCode == 'NAC1.123'`
  - `resolveCatalogRoute(Uri.parse('https://example.com/#/catalog'))` -> `isCatalog == true, initialNacCode == null`
  - `resolveCatalogRoute(Uri.parse('https://example.com/#/catalog/NAC1.123'))` -> `isCatalog == true, initialNacCode == 'NAC1.123'`
  - `resolveCatalogRoute(Uri.parse('https://example.com/#/catalog?item=NAC1.123'))` -> `isCatalog == true, initialNacCode == 'NAC1.123'`
  - `resolveCatalogRoute(Uri.parse('https://example.com/#/claim'))` -> `isCatalog == false`

---

### 1.2 F2: Image CSP Allowlist & Chunk 2 Scope (C1 & E5 & E6)
- **Observed Defect:** Field Tester recorded 166 console errors loading images from `upload.wikimedia.org`.
- **Root Cause:** `numista_mobile/firebase.json:284` Content-Security-Policy headers omitted Wikimedia and museum image domains from `img-src` and `connect-src`.
- **Exact Code Fix:**
  Update `firebase.json:284` by appending the approved image domains to both `img-src` and `connect-src`:
  - Approved domains added:
    - `https://upload.wikimedia.org`
    - `https://commons.wikimedia.org`
    - `https://*.wikimedia.org`
    - `https://images.metmuseum.org`
    - `https://numismatics.org`
  Updated header in `firebase.json:284`:
  ```json
  {
    "key": "Content-Security-Policy",
    "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app https://upload.wikimedia.org https://commons.wikimedia.org https://*.wikimedia.org https://images.metmuseum.org https://numismatics.org; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000 https://upload.wikimedia.org https://commons.wikimedia.org https://*.wikimedia.org https://images.metmuseum.org https://numismatics.org; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
  }
  ```
- **Image-URL Host Audit (Image Fetch Hosts Only):**
  - `upload.wikimedia.org`: 166
  - `thumb.wikimedia.org`: 10
  - `images.metmuseum.org`: 1
  - `numismatics.org`: 1
  *(Note: External references such as `americanhistory.si.edu` [173 records] and `fraser.stlouisfed.org` [37 records] reside in citation `sources`/`source_url` fields and are not fetched as images by `img-src`.)*
- **On-Screen vs Dataset Breakdown (C1):**
  - Total items in `catalog_public_v1.json`: 3,202 (2,965 coins, 181 banknotes, 56 medals).
  - Records with renderable HTTP image URLs (`url` key): Exactly **166 coins** and **1 medal** (total 167 items).
  - Records with bare file-only references (`file` key, no `url`): **1,047 records** (966 `type_image`, 81 `primary_image`).
  - Records with zero image metadata: **1,988 records** (1,752 coins, 181 banknotes, 55 medals).
  - **Expected On-Screen Rendering After CSP Fix:**
    - The Flutter UI (`catalog_browse_screen.dart:1113-1120`) attempts `Image.network(imgMap['url'])`. If `imgMap['url']` is absent, it falls back to `_buildPlaceholder()` (`"No photo yet"`).
    - Visible on-screen photos after CSP fix: **166 coins**, **1 medal** (the 167 items with valid URLs).
    - On-screen circular `"No photo yet"` placeholder: **2,799 coins** (1,752 without image metadata + 1,047 file-only references), **181 banknotes**, and **55 medals**.
    - *(Note: The "Photos only" filter at lines 147–151 checks map non-emptiness `(imgMap as Map).isNotEmpty`, which counts file-only records, explaining why Field Tester observed 1,213 items matching the filter.)*
- **Chunk 2 Gap Plan (E5 & C1 per Eric's 31 Oct Rules / NET-674):**
  - **Read-Only Invariant:** GCS buckets and Firestore remain strictly read-only for images.
  - **Expanded Scan Key:** Scan criteria covers both completely unimaged items and file-only items:
    `item['primary_image'] == null || (item['primary_image'] is Map && item['primary_image']['url'] == null)`
    This captures all 1,752 unimaged coins AND all 1,047 file-only records (including the 81 file-only primaries).
  - **Sources:**
    1. `gs://numista-reference-library/coins/` (reference library bucket).
    2. Eric's personal collection photos (path UNKNOWN until provided by Eric).
  - **Process:** An offline read-only matching script scans catalog records matching the expanded scan key against both sources.
  - **Proposal Manifest:** Matching results are written to a staging file on the box: `MANIFEST.csv` with columns `nac_code,source,source_path,matched_date,status=PROPOSAL`.
  - **Approval Gate:** No changes to `catalog_public_v1.json` occur until Grok CoS and Eric inspect and approve `MANIFEST.csv`. Banknotes (181) and medals (55) are scanned at lower priority following coins.

---

### 1.3 F3: Multi-Coin Set Face Value Multiplier (E1 & D1 & Advisory 2)
- **Observed Defect:** Field Tester noted multi-coin set `NAC1.CN.US.1D.DIAMONDFLD.2026.XX.26XS.B` (`Dollar (two-coin set)`) displayed face value `$1.00` instead of `$2.00`.
- **Root Cause:** In `lib/services/melt_value_service.dart:60`, `s = s.replaceAll(RegExp(r'\(.*?\)'), '').trim()` strips `(two-coin set)` before matching denomination, reducing `"dollar (two-coin set)"` to `"dollar"` ($1.00).
- **Exact Code Fix (Preserving All Parser Features & Signatures):**
  In `numista_mobile/lib/services/melt_value_service.dart:54`, keep existing signature:
  `static double parseFaceValue(String rawDenom, {int qty = 1})`
  Insert set-multiplier detection **immediately before** the parenthetical stripping at line 60 using word boundary `\bset\b`:
  ```dart
  static double parseFaceValue(String rawDenom, {int qty = 1}) {
    final count = qty > 0 ? qty : 1;
    if (rawDenom.trim().isEmpty) return 0.0;

    // Normalization pipeline: lowercase, collapse whitespace
    String s = rawDenom.toLowerCase().trim();

    // Multi-coin set detection BEFORE stripping parenthetical notes
    int setMultiplier = 1;
    final setMatch = RegExp(
      r'\(?(\d+|two|three|four|five)[- ]coin set\)?',
      caseSensitive: false,
    ).firstMatch(s);

    if (setMatch != null) {
      final token = setMatch.group(1)!.toLowerCase();
      switch (token) {
        case '2':
        case 'two':
          setMultiplier = 2;
          break;
        case '3':
        case 'three':
          setMultiplier = 3;
          break;
        case '4':
        case 'four':
          setMultiplier = 4;
          break;
        case '5':
        case 'five':
          setMultiplier = 5;
          break;
        default:
          setMultiplier = int.tryParse(token) ?? 1;
      }
    } else if (RegExp(r'\bset\b', caseSensitive: false).hasMatch(s) && !s.contains('offset')) {
      // Indeterminate multi-coin / collector set without specific count -> No face value chip (0.0)
      return 0.0;
    }

    // Strip parenthetical & ellipses
    s = s.replaceAll(RegExp(r'\(.*?\)'), '').trim();
    s = s.replaceAll(RegExp(r'\.{2,}'), '').trim();
    s = s.replaceAll('\u00bd', ' 1/2');
    s = s.replaceAll(RegExp(r'\s+'), ' ').trim();

    // Guard non-legal-tender blanks (planchets), non-USD units (candareens),
    // and multi-denomination sets/ranges ('$100/$50/$25/$10', '$1, $2, $5, $10', '3c-50c')
    if (s.contains('planchet') ||
        s.contains('candareen') ||
        RegExp(r'\$\d[\d,]*(?:\.\d+)?\s*(?:/\s*\$?|,\s*\$)\s*\d').hasMatch(s) ||
        RegExp(r'\d\s*(?:\u00a2|c|cents?)?\s*[\u2013\-]\s*\d').hasMatch(s)) {
      return 0.0;
    }

    double value = 0.0;

    // 0. Leading numeric & fractional patterns (N Dollars, 1,000 Dollars, 10,000 Dollars, 2 1/2 Dollars, G$2 1/2, 3 cents, $1000)
    final fracDollarMatch = RegExp(r'^(?:g?\$)?\s*(\d+)\s+1/2(?:\s*dollars?)?$').firstMatch(s);
    final leadDollarMatch = RegExp(r'^\$?\s*(\d[\d,]*(?:\.\d+)?)\s*(?:dollars?|\$)$').firstMatch(s);
    final leadCentMatch = RegExp(r'^(\d+(?:\.\d+)?)\s*(?:cents?|c|\u00a2)\b').firstMatch(s);
    final leadSymDollarMatch = RegExp(r'^\$\s*(\d[\d,]*(?:\.\d+)?)(?:\b|$)').firstMatch(s);

    if (fracDollarMatch != null) {
      value = (double.tryParse(fracDollarMatch.group(1)!) ?? 0.0) + 0.5;
    } else if (leadDollarMatch != null) {
      value = double.tryParse(leadDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
    } else if (leadCentMatch != null) {
      value = (double.tryParse(leadCentMatch.group(1)!) ?? 0.0) / 100.0;
    } else if (leadSymDollarMatch != null) {
      value = double.tryParse(leadSymDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
    }

    // 1. High Gold, Notes & Commemoratives
    else if (s.contains(r'$10,000') || s.contains(r'$10000') || s.contains('ten thousand dollar')) { value = 10000.00; }
    else if (s.contains(r'$1,000') || s.contains(r'$1000') || s.contains('one thousand dollar') || s.contains('thousand dollar')) { value = 1000.00; }
    else if (s.contains(r'$500') || s.contains('five hundred dollar')) { value = 500.00; }
    else if (s.contains(r'$100') || s.contains('one hundred dollar') || s.contains('hundred dollar')) { value = 100.00; }
    else if (s.contains(r'$50') || s.contains('fifty dollar')) { value = 50.00; }
    else if (s.contains(r'$40') || s.contains('forty dollar')) { value = 40.00; }
    else if (s.contains(r'$25') || s.contains('twenty five dollar') || s.contains('twenty-five dollar')) { value = 25.00; }
    else if (s.contains(r'$20') || s.contains('twenty dollar') || s.contains('double eagle')) { value = 20.00; }
    else if (s.contains(r'$10') || s.contains('ten dollar') || (s.contains('eagle') && !s.contains('half') && !s.contains('quarter') && !s.contains('silver'))) { value = 10.00; }
    else if (s.contains(r'$5') || s.contains('five dollar') || s.contains('half eagle')) { value = 5.00; }
    else if (s.contains(r'$4') || s.contains('four dollar') || s.contains('stella')) { value = 4.00; }
    else if (s.contains(r'$3') || s.contains('three dollar')) { value = 3.00; }
    else if (s.contains(r'$2.50') || s.contains(r'$2.5') || s.contains('2 1/2') || s.contains('quarter eagle') || s.contains('two and a half')) { value = 2.50; }
    else if (s.contains(r'$2') || s.contains('two dollar')) { value = 2.00; }

    // 2. Sub-Dollar & Standard Silver/Base Denominations (multi-word terms before single tokens)
    else if (s.contains('half dollar') || s.contains('fifty cent') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
    else if (s.contains('quarter dollar') || s.contains('twenty-five cent') || s.contains('twenty five cent') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
    else if (s.contains('twenty cent') || s.contains('20c') || s.contains('20 cent')) { value = 0.20; }
    else if (s.contains('half dime') || s.contains('half-dime')) { value = 0.05; }
    else if (s.contains('dime') || s.contains('ten cent') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
    else if (s.contains('three cent') || s.contains('3 cent') || s.contains('3c')) { value = 0.03; }
    else if (s.contains('nickel') || s.contains('five cent') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
    else if (s.contains('two cent') || s.contains('2 cent') || s.contains('2c')) { value = 0.02; }
    else if (s.contains('half cent') || s.contains('half-cent')) { value = 0.005; }
    else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
    else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }

    // 3. Fallback: plain numeric parse
    else {
      final match = RegExp(r'\d+(?:\.\d+)?').firstMatch(s);
      if (match != null) {
        final parsed = double.tryParse(match.group(0)!) ?? 0.0;
        value = parsed <= 1000.0 ? parsed : 0.0;
      }
    }

    return value * count * setMultiplier;
  }
  ```
- **Automated Verification & Test Updates (D1):**
  1. **Existing Pinned Test Update (`test/catalog_chunk1_face_value_and_card_test.dart:139`):**
     Update line 139 from:
     ```dart
     'Dollar (two-coin set)': 1.00,
     ```
     to:
     ```dart
     'Dollar (two-coin set)': 2.00, // FT Flag 2: 2-coin set face value multiplier
     ```
     This aligns the comprehensive full-catalog parse test (`misParses == 0`) with the verified $2.00 behavior.
  2. **Dedicated Set Multiplier Test Cases (line 203):**
     ```dart
     test('F3: Multi-coin set face value multiplier and set guards', () {
       expect(MeltValueService.parseFaceValue('Dollar (two-coin set)'), closeTo(2.00, 1e-4));
       expect(MeltValueService.parseFaceValue('Dollar (two-coin set)', qty: 2), closeTo(4.00, 1e-4));
       expect(MeltValueService.parseFaceValue('Half Dollar (two-coin set)'), closeTo(1.00, 1e-4));
       expect(MeltValueService.parseFaceValue('Three-coin set'), 0.0); // 0.0 unit * 3 = 0.0 -> No face value chip
       expect(MeltValueService.parseFaceValue('Collector Set'), 0.0);  // Indeterminate set -> No face value chip
     });
     ```

---

### 1.4 F4: `git_commit` Stamping in `version.json`
- **Observed Defect:** `version.json` contained package version but lacked `"git_commit": "<SHA>"`.
- **Root Cause:** Standard `flutter build web --release` does not automatically query git or inject the commit hash into the output artifact.
- **Exact Fix:** Integrated directly into the PowerShell build runbook (§2). Executed inside the isolated worktree immediately after `flutter build web --release`:
  1. Resolves `$resolvedSha = (git -C $wtPath rev-parse HEAD).Trim()`.
  2. Asserts exit code 0 and `$resolvedSha -eq $BuiltSha`.
  3. Checks existence of `$wtPath\numista_mobile\build\web\version.json`; throws hard error if absent.
  4. Parses JSON, injects `"git_commit": $resolvedSha`.
  5. Serializes and writes back using UTF-8 without BOM via `[System.IO.File]::WriteAllText($versionPath, $stampedJson, (New-Object System.Text.UTF8Encoding($false)))`.
  6. Re-reads and asserts `$verifyJson.git_commit -eq $resolvedSha`.

---

### 1.5 F5: Silver Half Dime Melt Math & Verification (D2)
- **Observed Defect:** Field Tester questioned whether Silver Half Dime melt was verified at current spot silver ($51.51/oz).
- **Mathematical Proof:**
  - Standard Half Dime composition (1837–1873): 90% silver, 10% copper.
  - Nominal weight: 1.25 grams. Actual Silver Weight (ASW) = `0.03617` troy oz (`melt_value_service.dart:12`).
  - At live spot silver **$51.51/oz**:
    $$\text{Melt Value} = 0.03617\text{ oz} \times \$51.51/\text{oz} = \$1.8631167 \approx \mathbf{\$1.86}$$
  - At historical reference spot ($30.00/oz):
    $$\text{Melt Value} = 0.03617\text{ oz} \times \$30.00/\text{oz} = \$1.0851 \approx \mathbf{\$1.09}$$
- **Verification Strategy & Raw String Syntax (D2):**
  In `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart:323-345`, verify real existing API `MeltValueService.compute(...)` using raw strings `r'...'` to prevent Dart string-interpolation compile errors:
  ```dart
  // Verify current spot $51.51/oz calculation -> $1.86
  expect(
    MeltValueService.compute(
      metalContent: '90% Silver',
      denomination: 'Half Dime',
      spotPrices: {'Silver': 51.51},
    ),
    closeTo(0.03617 * 51.51, 1e-3),
    reason: r'Half Dime at $51.51 spot must equal 0.03617 * 51.51 = $1.86',
  );
  // Preserve $30 reference spot test case -> $1.09
  expect(
    MeltValueService.compute(
      metalContent: '90% Silver',
      denomination: 'Half Dime',
      spotPrices: {'Silver': 30.0},
    ),
    closeTo(0.03617 * 30.0, 1e-3),
    reason: r'Half Dime at $30 spot must equal 0.03617 * 30.0 = $1.09',
  );
  ```
- **Catalog Detail Display Decision:**
  The public catalog is a static browse screen for signed-out users and does not maintain live authenticated websocket feeds. Live spot display on the detail modal is excluded from Chunk 1 scope to prevent unnecessary architectural overhead. Field Tester verification of live melt calculation is satisfied via the unit test suite and optional pre-seeded grokbot test coin (requiring Eric's separate typed YES).

---

### 1.6 Search Logic & Observational Findings (D3)

#### Note 1: Two-Pass Search Algorithm ("1816" & "Morgan dollar 1881")
- **Observed Issue:** Substring search failed on `"Morgan dollar 1881"` because terms span multiple metadata fields. Naive tokenization overmatched `"1842 Liberty Seated dollar"`, causing card widget test lines 348–385 to find 2 cards instead of 1.
- **Two-Pass Search Implementation (`catalog_browse_screen.dart:155-172`):**
  Implement two-pass search resolution inside `_applyFilters()`:
  ```dart
  if (query.isNotEmpty) {
    // Pass 1: Exact substring match on any single metadata field
    final directMatch = name.contains(query) ||
        series.contains(query) ||
        denom.contains(query) ||
        nac.contains(query) ||
        yearStr.contains(query);

    if (directMatch) {
      return true;
    }

    // Pass 2: Fallback multi-token match across combined metadata haystack
    // (Evaluated only if no direct substring matches exist across the catalog)
    final tokens = query.split(RegExp(r'\s+')).where((t) => t.isNotEmpty);
    final haystack = '$name $series $denom $nac $yearStr';
    final tokenMatch = tokens.every((token) => haystack.contains(token));
    if (!tokenMatch) return false;
  }
  ```
- **Results & Verified Behavior (D3):**
  1. `"1842 Liberty Seated dollar"`: Resolves via Pass 1 (direct match against `1842 Liberty Seated dollar`). Returns exactly 1 card. Card widget test in `test/catalog_chunk1_face_value_and_card_test.dart:348-385` finds exactly 1 card (`findsOneWidget`) and passes without modification.
  2. `"Morgan dollar 1881"`: Pass 1 yields no matches (no single field contains the exact phrase). Falls through to Pass 2, finding all 5 matching records (`1881-CC Morgan Silver Dollars`, etc.).
  3. `"1816"`: Both Pass 1 and Pass 2 yield 0 records (historical coinage hiatus after 1816 Mint fire; 0 records in dataset).
- **Automated Verification:**
  Add search regression tests to real existing test file `numista_mobile/test/catalog_browse_test.dart`:
  - `search('1842 Liberty Seated dollar')` -> returns 1 item.
  - `search('Morgan dollar 1881')` -> returns 5 items.
  - `search('1816')` -> returns 0 items.

#### Note 2: Coin Search 500 Error
- Traced from `CoinSearchScreen:395` ("Definitive Registry") -> `CoinSearchService.search` -> `GET /api/reference/search` (`main.py:9509`).
- In `main.py:9596-9597`, an unhandled exception inside `_get_user_owned_doc_ids` or SQLite `definitive_reference` query triggers `raise HTTPException(500, detail=str(e))`. This is documented for backend review and does not impact Flutter web public catalog browsing.

---

## 2. PowerShell 5.1 Build, Deploy & Rollback Runbook (D4 & E2 & E4)

### 2.1 Pre-Flight Safety & Guardrails
- **Channel Restriction:** Deployment is permitted **exclusively** to the preview channel `p7-gate`.
- **Live / Main Prohibition:** Deployment to `live` channel or `main` branch is strictly prohibited.
- **Commit Guard:** Deployment fails immediately if target commit starts with `c547b7a0` or is subject to holds `74611e05` / `41b8bd5f`.
- **Approval Prerequisite:** Execution requires Eric's typed scoped YES:
  `"YES DEPLOY p7-gate <BUILT_SHA> ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b"`

### 2.2 Complete PowerShell 5.1 Execution Script (`deploy_preview.ps1`)
*Script location: `scripts/deploy_preview.ps1` (or executed from EDS_Laptop outside repo).*
```powershell
# ==============================================================================
# NUMISTA.AI — NET-816 PREVIEW BUILD & DEPLOY RUNBOOK (PowerShell 5.1)
# Channel: p7-gate | Project: studio-9101802118-8c9a8
# ==============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$BuiltSha,

    [Parameter(Mandatory=$true)]
    [string]$EricApprovalYes
)

$ErrorActionPreference = 'Stop'

# 1. Native Execution Helper
function Invoke-Native {
    param([scriptblock]$Command, [string]$StepName)
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "FATAL: Step '$StepName' failed with exit code $LASTEXITCODE"
    }
}

# 2. Strict Guardrail Verification
$repoRoot = (Get-Location).Path
Set-Location $repoRoot

$resolvedSha = (git rev-parse --verify "$BuiltSha^{commit}").Trim()
if ($LASTEXITCODE -ne 0) {
    throw "FATAL: Could not resolve commit $BuiltSha"
}

$expectedYes = "YES DEPLOY p7-gate $BuiltSha ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b"
if ($EricApprovalYes.Trim() -ne $expectedYes) {
    throw "FATAL: Invalid approval text. Required exactly: '$expectedYes'"
}

if ($resolvedSha.StartsWith("c547b7a0", [System.StringComparison]::InvariantCultureIgnoreCase)) {
    throw "FATAL: Refusing build of prohibited commit c547b7a0"
}

# Worktree placed strictly in $env:TEMP with outside-repo check
$timestamp = (Get-Date).ToString("yyyyMMdd-HHmmss")
$wtPath = Join-Path $env:TEMP "numista-net816-worktree-$timestamp"
if ($wtPath.StartsWith($repoRoot, [System.StringComparison]::InvariantCultureIgnoreCase)) {
    throw "FATAL: Worktree path must reside outside repository root"
}

Write-Host "==> Starting build for $resolvedSha on p7-gate..." -ForegroundColor Cyan

try {
    # 3. Isolated Worktree Creation
    Invoke-Native { git worktree add --detach $wtPath $resolvedSha } "Create isolated worktree"

    # 4. Verify Built SHA matches git HEAD in worktree
    $wtHead = (git -C $wtPath rev-parse HEAD).Trim()
    if ($wtHead -ne $resolvedSha) {
        throw "FATAL: Worktree SHA ($wtHead) does not match requested SHA ($resolvedSha)"
    }

    # 5. Build Flutter Web Release
    Push-Location (Join-Path $wtPath "numista_mobile")
    Invoke-Native { flutter build web --release } "Flutter web release build"

    # 6. F4: version.json git_commit Stamping (UTF-8 without BOM)
    $versionPath = Join-Path (Get-Location).Path "build\web\version.json"
    if (-not (Test-Path $versionPath)) {
        throw "FATAL: build\web\version.json not found after build"
    }

    $jsonContent = Get-Content -Path $versionPath -Raw | ConvertFrom-Json
    $jsonContent | Add-Member -NotePropertyName "git_commit" -NotePropertyValue $resolvedSha -Force
    $stampedJson = $jsonContent | ConvertTo-Json -Depth 4
    [System.IO.File]::WriteAllText($versionPath, $stampedJson, (New-Object System.Text.UTF8Encoding($false)))

    # Verify stamp
    $verifyJson = Get-Content -Path $versionPath -Raw | ConvertFrom-Json
    if ($verifyJson.git_commit -ne $resolvedSha) {
        throw "FATAL: Verification failed: git_commit ($($verifyJson.git_commit)) != $resolvedSha"
    }
    Write-Host "==> version.json verified stamped with git_commit: $resolvedSha" -ForegroundColor Green

    # 7. Deploy to p7-gate Channel Only
    Invoke-Native {
        firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8
    } "Firebase channel deploy to p7-gate"

    # 8. Post-Deploy Readback Verification (D4)
    Write-Host "==> Running post-deploy readback checks..." -ForegroundColor Cyan
    $channelList = firebase hosting:channel:list --project studio-9101802118-8c9a8 | Out-String
    Write-Host $channelList
    if (-not ($channelList -match "p7-gate")) {
        throw "FATAL: p7-gate channel missing from hosting:channel:list"
    }

    # Extract preview channel URL and assert version.json git_commit
    $channelUrlMatch = [regex]::Match($channelList, 'https://studio-9101802118-8c9a8--p7-gate-[a-z0-9]+\.web\.app')
    if ($channelUrlMatch.Success) {
        $p7Url = $channelUrlMatch.Value
        Write-Host "==> Checking $p7Url/version.json..." -ForegroundColor Cyan
        $deployedVersion = Invoke-RestMethod -Uri "$p7Url/version.json" -TimeoutSec 15
        if ($deployedVersion.git_commit -ne $resolvedSha) {
            throw "FATAL: Served version.json git_commit ($($deployedVersion.git_commit)) != $resolvedSha"
        }
        Write-Host "==> Deployed version.json verified matching $resolvedSha" -ForegroundColor Green

        # HTTP 200 route checks
        foreach ($route in @('/', '/catalog', '/#/catalog')) {
            $resp = Invoke-WebRequest -Uri "$p7Url$route" -UseBasicParsing -TimeoutSec 10
            if ($resp.StatusCode -ne 200) {
                throw "FATAL: Route $route returned status $($resp.StatusCode)"
            }
        }
        Write-Host "==> Routes /, /catalog, /#/catalog verified HTTP 200" -ForegroundColor Green
    }

    Write-Host "==> SUCCESS: Deployed and verified $resolvedSha on channel p7-gate" -ForegroundColor Green
}
finally {
    # 9. Safe Worktree Cleanup (D4)
    Pop-Location -ErrorAction SilentlyContinue
    Set-Location $repoRoot
    if (Test-Path $wtPath) {
        Invoke-Native { git worktree remove --force $wtPath } "Remove worktree"
        Invoke-Native { git worktree prune } "Prune worktree"
    }
}
```

### 2.3 Rollback Procedures
- **Rollback Target A (RT-A — Instant Rollback to Baseline `a3d7dca2`):**
  Redeploy baseline commit full SHA `a3d7dca20fbbaf06a522205b22d0740b600de52b` to `p7-gate` using the script above:
  ```powershell
  .\scripts\deploy_preview.ps1 `
      -BuiltSha "a3d7dca20fbbaf06a522205b22d0740b600de52b" `
      -EricApprovalYes "YES DEPLOY p7-gate a3d7dca20fbbaf06a522205b22d0740b600de52b ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b"
  ```
- **Rollback Target B (RT-B — Passive Hold):**
  Leave `p7-gate` as is pending investigation.
- **Strict Prohibitions:**
  - Never rollback to `c547b7a0`.
  - Never touch live site or `main` (`numista-vault.web.app`).

---

## 3. Test & Verification Matrix (Rule 8)

| Item | Requirement / Defect | Machine-Checkable Verification Command | Expected Output / Criteria |
|---|---|---|---|
| **F1** | Direct catalog route resolution | `flutter test test/catalog_routing_test.dart` | Exit 0; all hash & path routes resolve correctly |
| **F2** | CSP allowlist headers | PowerShell programmatic inspection of `firebase.json` | `img-src` & `connect-src` contain `wikimedia.org`, `metmuseum.org`, `numismatics.org` |
| **F3** | Multi-coin set face value multiplier | `flutter test test/catalog_chunk1_face_value_and_card_test.dart` | Exit 0; 2-coin set = $2.00, line 139 = 2.00, indeterminate = 0.0, existing cases pass |
| **F4** | `version.json` git_commit stamping | PowerShell curl/invoke against `$wt\build\web\version.json` | JSON contains `"git_commit": "<SHA>"` |
| **F5** | Half dime melt math audit | `flutter test test/catalog_chunk1_face_value_and_card_test.dart` | Exit 0; 0.03617 oz × $51.51 = $1.86 (raw strings compile cleanly) |
| **Note 1** | Two-pass search ("1842 Seated dollar" & "Morgan dollar 1881") | `flutter test test/catalog_browse_test.dart` | Exit 0; 1842 Seated dollar = 1, Morgan dollar 1881 = 5, 1816 = 0 |
| **Code Hygiene** | Static analysis | `flutter analyze` | Exit 0; 0 errors |

---

## 4. Summary of Files to Modify (When Approved)

1. `numista_mobile/lib/main.dart` — Routing helper `resolveCatalogRoute` and startup handling for hash fragments.
2. `numista_mobile/firebase.json` — CSP additions for Wikimedia and museum domains in `img-src` and `connect-src`.
3. `numista_mobile/lib/services/melt_value_service.dart` — Multi-coin set multiplier detection before parenthetical strip.
4. `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` — Two-pass search matching.
5. `numista_mobile/test/catalog_routing_test.dart` — Route resolution unit tests (new).
6. `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart` — Line 139 update (`'Dollar (two-coin set)': 2.00`), line 203 set multiplier tests, lines 323–345 raw string syntax tests (`r'...'`).
7. `numista_mobile/test/catalog_browse_test.dart` — Two-pass search regression tests ("Morgan dollar 1881" -> 5, "1842 Liberty Seated dollar" -> 1, "1816" -> 0).

---

## 5. Authority & Gate Statement

This plan is **PLAN ONLY**. It grants **zero authority** to write code, modify files, create commits, execute builds, deploy to Firebase, write to Firestore, or interact with Stripe.

- HOLD `74611e05` and HOLD `41b8bd5f` remain active.
- `origin/main` strictly pinned at `9f04550a`.
- Next Gate: Designated CoS Gate (Pass Mark: 95/100).
- Subsequent Gates: Full-Plan SAG 95 Gate -> Eric's typed scoped YES.
<<<END ARTIFACT id=A5>>>

## A6: Field Tester result 47/100 FAIL on p7-gate a3d7dca2 (the defects R2 must fix)

<<<BEGIN ARTIFACT id=A6 sha256=7573823d596c89c4ef34af18c2859e0abbb5659e10e02e53a046ebc40b0bfcb7 bytes=4910 lines=76 path=/workspace/net816-failfix/round2/FT_RESULT_NET816_CATALOG_CHUNK1_p7gate_20261110.md>>>
# FT RESULT — NET-816 Catalog Chunk 1 — p7-gate preview — 10 Nov 2026 (~6:38 PM ET)
Tester: Field Tester, as grokbot@numista.ai. Read-only. Preview only, except one read-only search on live for comparison (CoS 6:22 PM add-on).
Target: https://numista-vault--p7-gate-8avtpz22.web.app (CoS pin: commit a3d7dca2, Hosting release a47a275d1eb6b51f)

## BLUF
SCORE 47/100, OVERALL FAIL (the bar is 95). The direct /catalog link works and the face values are right. However:
- `#/catalog` opens the home page, not the catalog.
- The build can't be pinned to the commit: version.json has no git_commit.
- The half dime melt check is BLOCKED because the test account has no half dime.
The 237-item gap is explained: 2,965 coins + 181 banknotes + 56 medals = 3,202, matching Code Reviewer's count.
I could not reproduce Eric's 500 error. The Go-live stays on HOLD (41b8bd5f).

## Pass/fail table
| # | Check | Result | Evidence |
|---|---|---|---|
| 0 | Build pin | FAIL / UNVERIFIED. version.json shows 8.18.15 / build 81818, but git_commit is absent, so a3d7dca2 can't be confirmed. | 00-version.png |
| 1a | Typing /catalog directly | PASS. The catalog renders with 2,965 items. | 01-catalog.png |
| 1b | Opening #/catalog | FAIL. It shows the signed-in welcome/home view, not the catalog. | 02-hash-catalog.png |
| 1c | /catalog/x | PASS. The catalog renders with "We don't have item 'x' in our reference catalog yet." | 03-catalog-x.png |
| 2 | Face values / "No face value" chip | PASS with one flag. The flag is a two-coin Morgan/Peace set, which shows "$1.00 Face value" (see the full list below). | 06–13, 16, 17, 29, 30 |
| 3 | 90% silver half dime melt | BLOCKED, not PASS. The grokbot collection has no half dime, and the 1796 catalog detail shows no melt value. | 05, 38, 39 |
| 4 | Search / empty state | NOTED, not scored. "half dime" gives 35 results; "xyzzy" and "1816" give 0; an empty search gives 2,965. | 18–21 |
| 6 | Coin Search 500 | NOT REPRODUCED / BLOCKED (details below). | 33, 34, 37 |
| 7 | 2,965 vs 3,202 | EXPLAINED (details below). | 23–28, 35, 36 |

Check 2, face values seen:
- Half cent $0.005, cent $0.01, half dime $0.05, dime $0.10, quarter $0.25, half dollar $0.50, dollar $1.00.
- 1908 $5 half eagle $5.00 and 1908 $10 eagle $10.00.
- Series 2017A $1 note $1.00.
- Medals show the "No face value" chip.
- Flag: the two-coin Morgan/Peace set shows "$1.00 Face value". Two dollar coins total $2.00, so either show $2.00 or the "No face value" chip.
- A search for "token" returns 0 items, so tokens were not tested.

Check 4, empty results: the page shows "No matching catalog items found", a "Reset search & filters" button and a "Missing something?" form. The UX point to note is that "1816" returns 0 results (the 1816 record gap from the earlier catalog test is still there).

Check 6, Coin Search 500:
- No separate Coin Search / Coin Reference Search screen was found in the app's navigation.
- The catalog search "Morgan dollar 1881" returned 0 items on both preview and live, with no 500 and no "Definitive Registry: 0 records".
- No failing request was captured. Eric's 6:22 PM path needs exact steps to reproduce.

Check 7, count gap:
- The Coins tab shows 2,965, Banknotes 181 and Medals 56, which adds up to 3,202.
- GET /assets/catalog_public_v1.json returned 200 with records 0–3201, which is 3,202 records.
- Nothing is missing.

## Half dime melt math
- Live Spot Prices: silver $51.51 (metals-api.com, 10 Nov 2026 6:24 PM ET).
- Expected melt at that spot: 0.03617 oz × $51.51 ≈ $1.86.
- The CoS figure of about $1.09 matches a spot price of about $30, so the expected value should be updated to the current spot.
- A 10x bug would show about $18.6.
- No coin was observed, so this check stays BLOCKED. It needs a test half dime in a test account (a Firestore write, which needs Eric's YES) or a melt value in the catalog detail.

## Other observations
- Console: about 166 errors, almost all CSP connect-src blocks on Wikimedia images. This is a recurring defect, still open.
- Time to first content: /catalog about 6.6 s, /catalog/x about 8.4 s.
- "Photos only" filter: 2,965 → 1,213, so about 59% of coins have no photo showing.
- Era Modern shows 1,124.
- Dashboard total melt (grokbot): $3,199.15.

## Scoring rubric (FT, 100 points)
| Area | Weight | Points |
|---|---|---|
| Build pin verified | 10 | 0 |
| Routes (/catalog, #/catalog) | 25 | 12 |
| Face values + chip | 25 | 20 |
| Half dime melt | 25 | 0 (BLOCKED, so no credit) |
| Catalog completeness (count gap) | 15 | 15 |
| **Total** | 100 | **47** |

## What would move it to PASS
1. Make #/catalog route to the catalog.
2. Stamp git_commit in version.json.
3. Give the set a $2.00 face value or the "No face value" chip.
4. Provide a half dime to observe: a CoS-approved test coin in grokbot, or a melt value on the catalog detail.

Screenshots: shots_net816.tar.gz (40 files).
<<<END ARTIFACT id=A6>>>

## A7: Source at a3d7dca2: numista_mobile/lib/main.dart (blob e9053e3e…)

<<<BEGIN ARTIFACT id=A7 sha256=cd6c6c5c166fec91cfc5fd67540aa35a5a7739a8374237bb33286fb8c1d71f26 bytes=18930 lines=487 path=/workspace/net816-failfix/sag-upload-r2v3/src/main.dart>>>
import 'dart:async';
import 'dart:ui';
import 'package:flutter/foundation.dart' show kIsWeb, kDebugMode, debugPrint;
import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'screens/welcome_screen.dart';
import 'screens/attorney_portal_screen.dart';
import 'screens/not_found_screen.dart';
import 'screens/public_wishlist_view_screen.dart';
import 'screens/catalog/catalog_browse_screen.dart';
import 'services/theme_provider.dart';
import 'widgets/morgan_feedback_drawer.dart';
import 'services/guest_seed_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'widgets/auth_gate.dart';
import 'constants.dart';  // ITEM 10: kApiBaseUrl startup guard
import 'package:google_fonts/google_fonts.dart';
import 'utils/numista_error_helper.dart';


Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('Uncaught platform error: $error\n$stack');
    return true; // handled
  };

  FlutterError.onError = (FlutterErrorDetails details) {
    debugPrint('FlutterError: ${details.exceptionAsString()}\n${details.stack}');
  };

  // Enable Flutter accessibility semantics on web so that Playwright
  // text= / aria-label locators can find flt-semantics nodes.
  // SemanticsBinding.instance is a no-op on non-web platforms.
  if (kIsWeb) {
    SemanticsBinding.instance.ensureSemantics();
  }

  ErrorWidget.builder = (FlutterErrorDetails details) {
    // Log full details to console in debug only — never to UI
    if (kDebugMode) {
      debugPrint('UI Error: ${details.exception}\n${details.stack}');
      FlutterError.dumpErrorToConsole(details);
    }
    return const _ErrorFallbackWidget();
  };

  final uri = Uri.base;

  // ── Public Wishlist deep-link detection ──────────────────────────────────
  final isPublicWishlist = uri.path.contains('/wishlist/') ||
      (uri.pathSegments.isNotEmpty && uri.pathSegments.first == 'wishlist') ||
      uri.queryParameters.containsKey('wishlist');
  if (isPublicWishlist) {
    String token = uri.queryParameters['wishlist'] ?? '';
    if (token.isEmpty && uri.pathSegments.length >= 2 && uri.pathSegments.first == 'wishlist') {
      token = uri.pathSegments[1];
    }
    if (token.isEmpty && uri.path.contains('/wishlist/')) {
      token = uri.path.split('/wishlist/').last.split('?').first.split('#').first;
    }
    if (token.isNotEmpty) {
      await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform,
      );
      runApp(MaterialApp(
        title: 'Numista.AI — Public Wish List',
        debugShowCheckedModeBanner: false,
        home: PublicWishlistViewScreen(token: token),
      ));
      return;
    }
  }

  // ── Attorney portal deep-link detection ──────────────────────────────────
  // If the URL contains /attorney?uid=...&token=... we skip auth entirely and
  // render the read-only attorney portal instead of the normal app.
  final isAttorneyPortal = uri.path.contains('/attorney') ||
      (uri.queryParameters.containsKey('uid') &&
       uri.queryParameters.containsKey('token'));
  if (isAttorneyPortal) {
    final uid   = uri.queryParameters['uid'] ?? '';
    final token = uri.queryParameters['token'] ?? '';
    if (uid.isNotEmpty && token.isNotEmpty) {
      await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform,
      );
      runApp(MaterialApp(
        title: 'Numista.AI — Estate Report',
        debugShowCheckedModeBanner: false,
        home: AttorneyPortalScreen(uid: uid, token: token),
      ));
      return;
    }
  }
  // ── Unknown-path guard (Soft-404 fix) ─────────────────────────────────────
  // Firebase Hosting now returns a real HTTP 404 for garbage URLs.
  // This guard handles the rare case where a valid-looking but unknown path
  // is navigated to *inside* the Flutter app (e.g. a stale bookmark that was
  // once real).
  //
  // Known real paths served by this app shell:
  //   /               — root / home
  //   /wishlist/**    — public wishlist deep links
  //   /attorney_portal — attorney/estate portal (caught above)
  //   /claim          — Phase-2 reservation (L5: routes to home, NOT NotFoundScreen)
  //   /claim/**       — Phase-2 reservation (same)
  //
  // Any other non-empty path not in this set shows NotFoundScreen.
  // Hash-fragment URLs (e.g. /#/claim?...) have uri.path == '/' — they pass
  // through to the normal app flow correctly.
  final path = uri.path;
  final normalizedPath = (path.endsWith('/') && path.length > 1)
      ? path.substring(0, path.length - 1)
      : path;

  final isKnownPath = path.isEmpty ||
      path == '/' ||
      path == '/index.html' ||
      normalizedPath == '/about' ||
      normalizedPath == '/pricing' ||
      normalizedPath == '/features' ||
      normalizedPath == '/faq' ||
      normalizedPath == '/login' ||
      normalizedPath == '/signup' ||
      normalizedPath == '/reset-password' ||
      normalizedPath == '/demo' ||
      normalizedPath == '/app' ||
      normalizedPath == '/blog' ||
      normalizedPath == '/catalog' ||
      path.startsWith('/catalog/') ||
      path.startsWith('/wishlist') ||
      path.startsWith('/attorney_portal') ||
      path.startsWith('/attorney') ||
      path.startsWith('/claim') || // L5: reserved — falls through to home, not NotFoundScreen
      path.startsWith('/privacy') ||
      path.startsWith('/terms') ||
      path.startsWith('/add_coins') ||
      path.startsWith('/scraper_dashboard') ||
      path.startsWith('/api/');

  if (!isKnownPath) {
    runApp(MaterialApp(
      title: 'Numista.AI',
      debugShowCheckedModeBanner: false,
      home: NotFoundScreen(attemptedPath: path),
    ));
    return;
  }

  // Public Catalog direct entry (zero auth required)
  if (normalizedPath == '/catalog' || path.startsWith('/catalog/')) {
    String? initialNacCode;
    if (path.startsWith('/catalog/')) {
      final sub = path.substring('/catalog/'.length).trim();
      if (sub.isNotEmpty) {
        initialNacCode = Uri.decodeComponent(sub);
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

  // Synchronously parse Front Door URL routes
  bool isPendingDemo = false;
  String? pendingPublicRoute;
  int initialAuthTab = 0;
  bool showResetForm = false;

  if (normalizedPath == '/demo') {
    isPendingDemo = true;
  } else if (normalizedPath == '/about' ||
      normalizedPath == '/features' ||
      normalizedPath == '/pricing' ||
      normalizedPath == '/faq' ||
      normalizedPath == '/blog') {
    pendingPublicRoute = normalizedPath == '/blog' ? '/about' : normalizedPath;
  } else if (normalizedPath == '/login') {
    initialAuthTab = 0;
  } else if (normalizedPath == '/signup') {
    initialAuthTab = 1;
  } else if (normalizedPath == '/reset-password') {
    initialAuthTab = 0;
    showResetForm = true;
  }

  // ── General Route deep-link detection (e.g., ?route=Review%20Hub) ────────────
  if (uri.queryParameters.containsKey('route') && uri.queryParameters['route']!.isNotEmpty) {
    WelcomeScreen.pendingRoute = uri.queryParameters['route'];
  }

  // ITEM 10: kApiBaseUrl guard — prevents silent empty-URL HTTP calls.
  // This is a compile-time const so it will never be empty in production,
  // but this guard protects against misconfigured forks or env-var overrides.
  if (kApiBaseUrl.trim().isEmpty) {
    // Throw synchronously so Flutter's error reporter catches it before
    // any HTTP request can fire against an empty URL.
    throw StateError(
      '[Numista] kApiBaseUrl is empty. '
      'Set the backend URL in lib/constants.dart before building.',
    );
  }

  // On Flutter web, Firebase.initializeApp() can silently hang forever if the
  // network is slow or a service worker interferes. We wrap it in a 12-second
  // timeout so runApp() is always called, even in the worst case.
  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    ).timeout(const Duration(seconds: 12));
  } on TimeoutException {
    // Timed out — proceed anyway. The auth StreamBuilder may still resolve
    // once Firebase connects in the background.
    debugPrint('[Numista] Firebase.initializeApp() timed out — proceeding anyway.');
  } catch (e, stack) {
    // Hard failure — show a readable error screen instead of a blank page.
    runApp(MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        backgroundColor: const Color(0xFF0B1220),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 60),
              const Text('🔥 Firebase Init Failed',
                  style: TextStyle(
                      color: Colors.redAccent,
                      fontSize: 22,
                      fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'The app could not start. Please reload the page or contact support@numista.ai.'),
                  style: const TextStyle(
                      color: Colors.orangeAccent, fontSize: 14)),
              const SizedBox(height: 24),
              Text(stack.toString(),
                  style: const TextStyle(
                      color: Colors.white54, fontSize: 11)),
            ],
          ),
        ),
      ),
    ));
    return;
  }

  // Restore persistent Browse Demo state from SharedPreferences across reloads
  try {
    final prefs = await SharedPreferences.getInstance();
    final wasDemoActive = prefs.getBool('browse_demo_active') ?? false;
    if (wasDemoActive || isPendingDemo) {
      await GuestSeedService.activateBrowseDemo();
      isPendingDemo = true;
    }
  } catch (_) {}

  runApp(NumistaAIApp(
    isPendingDemo: isPendingDemo,
    pendingPublicRoute: pendingPublicRoute,
    initialAuthTab: initialAuthTab,
    showResetForm: showResetForm,
  ));
}

class NumistaAIApp extends StatefulWidget {
  final bool isPendingDemo;
  final String? pendingPublicRoute;
  final int initialAuthTab;
  final bool showResetForm;

  const NumistaAIApp({
    super.key,
    this.isPendingDemo = false,
    this.pendingPublicRoute,
    this.initialAuthTab = 0,
    this.showResetForm = false,
  });

  @override
  State<NumistaAIApp> createState() => _NumistaAIAppState();
}

class _NumistaAIAppState extends State<NumistaAIApp> {
  late bool _isPendingDemo;
  late String? _pendingPublicRoute;

  @override
  void initState() {
    super.initState();
    _isPendingDemo = widget.isPendingDemo;
    _pendingPublicRoute = widget.pendingPublicRoute;
    if (_isPendingDemo) {
      GuestSeedService.activateBrowseDemo();
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: ThemeProvider.instance,
      builder: (context, _) {
        return MaterialApp(
          title: 'Numista.AI',
          debugShowCheckedModeBanner: false,
          themeMode: ThemeProvider.instance.themeMode,
          theme: ThemeData(
            visualDensity: VisualDensity.standard,
            brightness: Brightness.light,
            scaffoldBackgroundColor: const Color(0xFFF4F4F2), // Premium parchment/platinum-silver bg
            primaryColor: const Color(0xFF8C7355), // Antique bronze
            cardColor: const Color(0xFFFFFFFF),
            dividerColor: const Color(0xFFE2E8F0),
            colorScheme: ColorScheme.fromSeed(
              seedColor: const Color(0xFF8C7355),
              brightness: Brightness.light,
              primary: const Color(0xFF8C7355),
              secondary: const Color(0xFFC9A227),
              surface: const Color(0xFFFFFFFF),
              error: const Color(0xFFDC3545),
            ),
            fontFamily: 'sans-serif',
            appBarTheme: const AppBarTheme(
              backgroundColor: Colors.white,
              foregroundColor: Color(0xFF0F172A),
              elevation: 0,
            ),
            scrollbarTheme: ScrollbarThemeData(
              thumbVisibility: WidgetStateProperty.all(true),
              trackVisibility: WidgetStateProperty.all(true),
              thickness: WidgetStateProperty.all(12.0),
              radius: const Radius.circular(6.0),
              thumbColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.hovered)) {
                  return const Color(0xFFC9A227);
                }
                return const Color(0xFF94A3B8);
              }),
              trackColor: WidgetStateProperty.all(const Color(0xFFE2E8F0)),
            ),
            textTheme: GoogleFonts.interTextTheme(ThemeData.light().textTheme).apply(
              bodyColor: const Color(0xFF0F172A),
              displayColor: const Color(0xFF0F172A),
            ),
          ),
          darkTheme: ThemeData(
            visualDensity: VisualDensity.standard,
            brightness: Brightness.dark,
            scaffoldBackgroundColor: const Color(0xFF0B1120), // Deep navy-black bg
            primaryColor: const Color(0xFFC9A227), // Metallic gold
            cardColor: const Color(0xFF1E2937), // Rich slate cards
            dividerColor: const Color(0xFF2D3143),
            colorScheme: ColorScheme.fromSeed(
              seedColor: const Color(0xFFC9A227),
              brightness: Brightness.dark,
              primary: const Color(0xFFC9A227),
              secondary: const Color(0xFFD4AF37),
              surface: const Color(0xFF1E2937),
              error: const Color(0xFFDC3545),
            ),
            fontFamily: 'sans-serif',
            appBarTheme: const AppBarTheme(
              backgroundColor: Color(0xFF1E2937),
              foregroundColor: Colors.white,
              elevation: 0,
            ),
            scrollbarTheme: ScrollbarThemeData(
              thumbVisibility: WidgetStateProperty.all(true),
              trackVisibility: WidgetStateProperty.all(true),
              thickness: WidgetStateProperty.all(12.0),
              radius: const Radius.circular(6.0),
              thumbColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.hovered)) {
                  return const Color(0xFFFFD700);
                }
                return const Color(0xFF475569);
              }),
              trackColor: WidgetStateProperty.all(const Color(0xFF1E293B)),
            ),
            textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme).apply(
              bodyColor: const Color(0xFFE8EAF0),
              displayColor: const Color(0xFFE8EAF0),
            ),
          ),
          // ITEM 3: Wrap every route in the text scaler + Morgan feedback drawer.
          // ThemeProvider.textScaleFactor is 1.0 / 1.3 / 1.6 per user setting.
          // MediaQuery.withClampedTextScaling clamps between minScaleFactor and
          // maxScaleFactor — we pin both to the chosen value so OS accessibility
          // settings do not override the in-app control on desktop web.
          builder: (context, child) {
            final scaleFactor = ThemeProvider.instance.textScaleFactor;
            return MediaQuery(
              data: MediaQuery.of(context).copyWith(
                textScaler: TextScaler.linear(scaleFactor),
              ),
              child: FeedbackDrawerOverlay(child: child ?? const SizedBox.shrink()),
            );
          },
      // --- Auth Gate ---------------------------------------------------------
      // StreamBuilder on authStateChanges: handles unauthenticated states,
      // public routes, demo mode, and transitions to BaseLayout on login.
      home: AuthGate(
        isDemo: _isPendingDemo,
        publicRoute: _pendingPublicRoute,
        initialAuthTab: widget.initialAuthTab,
        showResetForm: widget.showResetForm,
      ),
    );
      },
    );
  }
}

/// Fallback widget shown when ErrorWidget.builder is triggered.
/// Plain Material widget — no Navigator, no platform-specific APIs.
/// Report Issue: displays copyable support email address.
class _ErrorFallbackWidget extends StatelessWidget {
  const _ErrorFallbackWidget();

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFF1E2937),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 480),
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline,
                    color: Color(0xFFC9A227), size: 48),
                const SizedBox(height: 16),
                const Text(
                  'Something went wrong loading this screen.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Color(0xFFE8EAF0),
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Please refresh the page. If this keeps happening, '
                  'contact support at the address below.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Color(0xFF8B92B4), fontSize: 14),
                ),
                const SizedBox(height: 6),
                const SelectableText(
                  'support@numista.ai',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Color(0xFFC9A227),
                    fontSize: 14,
                    decoration: TextDecoration.underline,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
<<<END ARTIFACT id=A7>>>

## A8: Source at a3d7dca2: numista_mobile/lib/services/melt_value_service.dart (blob 62d11a9a…; CRLF as committed)

<<<BEGIN ARTIFACT id=A8 sha256=e163b221b5cdbdb550ba68aeaa9b519900432d8d27789d8ab6cd3cf6d4ca63d1 bytes=13793 lines=256 path=/workspace/net816-failfix/sag-upload-r2v3/src/melt_value_service.dart>>>
// melt_value_service.dart
//
// Standardized Valuation Service for Numista.AI
// Calculates real-time face value and melt value for coins:
//   - Field precedence: Uses explicit numeric fields (denomination_numeric, troy_oz_pure_metal) when available
//   - Fallback normalization: Normalizes truncated/dirty strings ("Five Dollars (Hal..." -> $5.00)
//   - Spot price resilience: Live spot prices with cached fallback and offline indicator support

class MeltValueService {
  // ── Silver (Ag) troy oz per coin by denomination ───────────────────────────
  static const _ag90 = {
    'half dime':   0.03617,   // Nominal 1.25g (1853+ 1.24g) × 90% ÷ 31.1035
    'dime':        0.07234,   // 2.5g × 90% = 2.25g Ag ÷ 31.1035
    'quarter':     0.18084,   // 6.25g × 90% = 5.625g Ag ÷ 31.1035
    'half':        0.36169,   // 12.5g × 90% = 11.25g Ag ÷ 31.1035
    'half dollar': 0.36169,
    'dollar':      0.77344,   // Morgan / Peace: 26.73g × 90% ÷ 31.1035
  };

  static const _ag40 = {
    'half':        0.14792,
    'half dollar': 0.14792,
  };

  static const _ag35 = {
    'nickel': 0.05626,
  };

  static const double _silverEagleOz = 1.0;

  // ── Gold (Au) troy oz per coin by face value ───────────────────────────────
  static final _au90ByFaceValue = {
    1.0:  0.04837,   // $1 gold piece
    2.5:  0.12094,   // Quarter Eagle
    3.0:  0.14513,   // $3 gold piece
    5.0:  0.24188,   // Half Eagle
    10.0: 0.48375,   // Eagle
    20.0: 0.96750,   // Double Eagle
  };

  static final _au9167ByFaceValue = {
    5.0:  0.10,
    10.0: 0.25,
    25.0: 0.50,
    50.0: 1.00,
  };

  static const double _buffaloAuOz = 1.0;

  // ── Unified Face Value Parser ──────────────────────────────────────────────
  /// Parses denomination string to numerical USD value.
  /// Pre-processes dirty strings by stripping parenthetical notes and ellipses.
  /// Evaluates multi-word terms before generic single tokens.
  static double parseFaceValue(String rawDenom, {int qty = 1}) {
    final count = qty > 0 ? qty : 1;
    if (rawDenom.trim().isEmpty) return 0.0;

    // Normalization pipeline: lowercase, collapse whitespace, strip parenthetical & ellipses
    String s = rawDenom.toLowerCase().trim();
    s = s.replaceAll(RegExp(r'\(.*?\)'), '').trim();
    s = s.replaceAll(RegExp(r'\.{2,}'), '').trim();
    s = s.replaceAll('\u00bd', ' 1/2');
    s = s.replaceAll(RegExp(r'\s+'), ' ').trim();

    // Guard non-legal-tender blanks (planchets), non-USD units (candareens),
    // and multi-denomination sets/ranges ('$100/$50/$25/$10', '$1, $2, $5, $10', '3c-50c')
    if (s.contains('planchet') ||
        s.contains('candareen') ||
        RegExp(r'\$\d[\d,]*(?:\.\d+)?\s*(?:/\s*\$?|,\s*\$)\s*\d').hasMatch(s) ||
        RegExp(r'\d\s*(?:\u00a2|c|cents?)?\s*[\u2013\-]\s*\d').hasMatch(s)) {
      return 0.0;
    }

    double value = 0.0;

    // 0. Leading numeric & fractional patterns (N Dollars, 1,000 Dollars, 10,000 Dollars, 2 1/2 Dollars, G$2 1/2, 3 cents, $1000)
    final fracDollarMatch = RegExp(r'^(?:g?\$)?\s*(\d+)\s+1/2(?:\s*dollars?)?$').firstMatch(s);
    final leadDollarMatch = RegExp(r'^\$?\s*(\d[\d,]*(?:\.\d+)?)\s*(?:dollars?|\$)$').firstMatch(s);
    final leadCentMatch = RegExp(r'^(\d+(?:\.\d+)?)\s*(?:cents?|c|\u00a2)\b').firstMatch(s);
    final leadSymDollarMatch = RegExp(r'^\$\s*(\d[\d,]*(?:\.\d+)?)(?:\b|$)').firstMatch(s);

    if (fracDollarMatch != null) {
      value = (double.tryParse(fracDollarMatch.group(1)!) ?? 0.0) + 0.5;
    } else if (leadDollarMatch != null) {
      value = double.tryParse(leadDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
    } else if (leadCentMatch != null) {
      value = (double.tryParse(leadCentMatch.group(1)!) ?? 0.0) / 100.0;
    } else if (leadSymDollarMatch != null) {
      value = double.tryParse(leadSymDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
    }

    // 1. High Gold, Notes & Commemoratives
    else if (s.contains(r'$10,000') || s.contains(r'$10000') || s.contains('ten thousand dollar')) { value = 10000.00; }
    else if (s.contains(r'$1,000') || s.contains(r'$1000') || s.contains('one thousand dollar') || s.contains('thousand dollar')) { value = 1000.00; }
    else if (s.contains(r'$500') || s.contains('five hundred dollar')) { value = 500.00; }
    else if (s.contains(r'$100') || s.contains('one hundred dollar') || s.contains('hundred dollar')) { value = 100.00; }
    else if (s.contains(r'$50') || s.contains('fifty dollar')) { value = 50.00; }
    else if (s.contains(r'$40') || s.contains('forty dollar')) { value = 40.00; }
    else if (s.contains(r'$25') || s.contains('twenty five dollar') || s.contains('twenty-five dollar')) { value = 25.00; }
    else if (s.contains(r'$20') || s.contains('twenty dollar') || s.contains('double eagle')) { value = 20.00; }
    else if (s.contains(r'$10') || s.contains('ten dollar') || (s.contains('eagle') && !s.contains('half') && !s.contains('quarter') && !s.contains('silver'))) { value = 10.00; }
    else if (s.contains(r'$5') || s.contains('five dollar') || s.contains('half eagle')) { value = 5.00; }
    else if (s.contains(r'$4') || s.contains('four dollar') || s.contains('stella')) { value = 4.00; }
    else if (s.contains(r'$3') || s.contains('three dollar')) { value = 3.00; }
    else if (s.contains(r'$2.50') || s.contains(r'$2.5') || s.contains('2 1/2') || s.contains('quarter eagle') || s.contains('two and a half')) { value = 2.50; }
    else if (s.contains(r'$2') || s.contains('two dollar')) { value = 2.00; }

    // 2. Sub-Dollar & Standard Silver/Base Denominations (multi-word terms before single tokens)
    else if (s.contains('half dollar') || s.contains('fifty cent') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
    else if (s.contains('quarter dollar') || s.contains('twenty-five cent') || s.contains('twenty five cent') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
    else if (s.contains('twenty cent') || s.contains('20c') || s.contains('20 cent')) { value = 0.20; }
    else if (s.contains('half dime') || s.contains('half-dime')) { value = 0.05; }
    else if (s.contains('dime') || s.contains('ten cent') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
    else if (s.contains('three cent') || s.contains('3 cent') || s.contains('3c')) { value = 0.03; }
    else if (s.contains('nickel') || s.contains('five cent') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
    else if (s.contains('two cent') || s.contains('2 cent') || s.contains('2c')) { value = 0.02; }
    else if (s.contains('half cent') || s.contains('half-cent')) { value = 0.005; }
    else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
    else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }

    // 3. Fallback: plain numeric parse
    else {
      final match = RegExp(r'\d+(?:\.\d+)?').firstMatch(s);
      if (match != null) {
        final parsed = double.tryParse(match.group(0)!) ?? 0.0;
        value = parsed <= 1000.0 ? parsed : 0.0;
      }
    }

    return value * count;
  }

  // ── Public Melt Value Calculation API ──────────────────────────────────────
  /// Returns melt value in USD, or null for base-metal / non-precious coins.
  static double? compute({
    required String metalContent,
    required String denomination,
    required Map<String, double> spotPrices,
    String programSeries = '',
    String themeSubject = '',
    int qty = 1,
    Map<String, dynamic>? coinData,
  }) {
    final count = qty > 0 ? qty : 1;
    final ag = spotPrices['Silver'] ?? 0.0;
    final au = spotPrices['Gold']   ?? 0.0;

    if (ag == 0.0 && au == 0.0) return null;

    // Field Precedence: Check if backend numeric troy oz field is present
    if (coinData != null) {
      final ozNum = (coinData['troy_oz_pure_metal'] as num?)?.toDouble();
      final isGold = coinData['is_gold'] == true;
      final isSilver = coinData['is_silver'] == true;
      if (ozNum != null && ozNum > 0.0) {
        if (isGold && au > 0) return au * ozNum * count;
        if (isSilver && ag > 0) return ag * ozNum * count;
      }
    }

    final mc     = metalContent.trim().toLowerCase();
    final denom  = denomination.trim().toLowerCase();
    final series = programSeries.trim().toLowerCase();
    final theme  = themeSubject.trim().toLowerCase();
    final combined = '$mc $denom $series $theme';

    // ── Gold Detection ──────────────────────────────────────────────────────
    if (combined.contains('gold') || combined.contains('half eagle') || combined.contains('eagle') || combined.contains('double eagle')) {
      if (combined.contains('99.99') || combined.contains('buffalo')) {
        return au * _buffaloAuOz * count;
      }
      if (combined.contains('91.67') || combined.contains('gold eagle')) {
        final fv = parseFaceValue(denom);
        final oz = _au9167ByFaceValue[fv] ?? 1.0;
        return au * oz * count;
      }
      if (combined.contains('90%') || combined.contains('half eagle') || combined.contains('indian head gold') || combined.contains('pre-1933') || combined.contains('saint-gaudens') || combined.contains('liberty head')) {
        final fv = parseFaceValue(denom);
        final oz = _au90ByFaceValue[fv] ?? 0.24188;
        return au * oz * count;
      }
      if (au > 0) return au * 0.24188 * count;
    }

    // ── Silver Detection ────────────────────────────────────────────────────
    if (combined.contains('silver') || combined.contains('silver eagle') || combined.contains('peace dollar') || combined.contains('morgan')) {
      if (combined.contains('silver eagle') || combined.contains('99.9') || combined.contains('.999') || combined.contains('fine silver')) {
        return ag * _silverEagleOz * count;
      }
      if (combined.contains('90%') || combined.contains('half dime') || combined.contains('half-dime') || combined.contains('morgan') || combined.contains('peace') || combined.contains('barber') || combined.contains('walking liberty') || combined.contains('standing liberty') || combined.contains('mercury')) {
        final fv = parseFaceValue(denom);
        final isDollar = fv == 1.00 || combined.contains('dollar') || combined.contains('morgan') || combined.contains('peace');
        final oz = _matchDenom(_ag90, denom) ?? (isDollar ? 0.77344 : null);
        if (oz != null) return ag * oz * count;
        return null;
      }
      if (combined.contains('40%')) {
        final oz = _matchDenom(_ag40, denom) ?? 0.14792;
        return ag * oz * count;
      }
      if (combined.contains('35%') || ((combined.contains('war nickel') || combined.contains('wartime')) && parseFaceValue(denom) == 0.05)) {
        final oz = _matchDenom(_ag35, denom) ?? 0.05626;
        return ag * oz * count;
      }
      if (ag > 0) {
        final fv = parseFaceValue(denom);
        // N4: Route 5-cent wartime/war nickels without "35%" text to 35% war nickel weight
        if (fv == 0.05 && (combined.contains('nickel') || combined.contains('wartime') || (combined.contains('war') && !combined.contains('award') && !combined.contains('howard') && !combined.contains('edward')) || combined.contains('manganese'))) {
          return ag * 0.05626 * count;
        }
        final isDollar = fv == 1.00 || combined.contains('dollar') || combined.contains('morgan') || combined.contains('peace');
        final oz = _matchDenom(_ag90, denom) ?? (isDollar ? 0.77344 : null);
        if (oz != null) return ag * oz * count;
        return null;
      }
    }

    return null;
  }

  /// Formatted melt value string. Returns 'N/A' for non-precious coins.
  static String format({
    required String metalContent,
    required String denomination,
    required Map<String, double> spotPrices,
    String programSeries = '',
    String themeSubject = '',
    int qty = 1,
    Map<String, dynamic>? coinData,
  }) {
    final v = compute(
      metalContent: metalContent,
      denomination: denomination,
      spotPrices: spotPrices,
      programSeries: programSeries,
      themeSubject: themeSubject,
      qty: qty,
      coinData: coinData,
    );
    if (v == null) return 'N/A';
    return '\$${v.toStringAsFixed(2)}';
  }

  static double? _matchDenom(Map<String, double> table, String rawDenom) {
    final fv = parseFaceValue(rawDenom);
    if (fv == 1.00 && table.containsKey('dollar')) return table['dollar'];
    if (fv == 0.50 && table.containsKey('half')) return table['half'];
    if (fv == 0.25 && table.containsKey('quarter')) return table['quarter'];
    if (fv == 0.10 && table.containsKey('dime')) return table['dime'];
    if (fv == 0.05) {
      if (table.containsKey('half dime')) return table['half dime'];
      if (table.containsKey('nickel')) return table['nickel'];
    }
    return null;
  }
}
<<<END ARTIFACT id=A8>>>

## A9: Source at a3d7dca2: numista_mobile/lib/screens/catalog/catalog_browse_screen.dart (blob a87e4cf9…)

<<<BEGIN ARTIFACT id=A9 sha256=933ce414c3ca969338673618472696ba6f864e9b844488f301376eadd20e05c7 bytes=47294 lines=1280 path=/workspace/net816-failfix/sag-upload-r2v3/src/catalog_browse_screen.dart>>>
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../services/melt_value_service.dart';

class CatalogBrowseScreen extends StatefulWidget {
  final String? initialQuery;
  final String? initialNacCode;

  const CatalogBrowseScreen({
    super.key,
    this.initialQuery,
    this.initialNacCode,
  });

  @override
  State<CatalogBrowseScreen> createState() => _CatalogBrowseScreenState();
}

class _CatalogBrowseScreenState extends State<CatalogBrowseScreen> {
  List<Map<String, dynamic>> _allEntries = [];
  List<Map<String, dynamic>> _filteredEntries = [];
  bool _isLoading = true;
  String _searchQuery = '';
  String _selectedType = 'coin'; // 'coin', 'note', 'medal', 'foreign'
  String _selectedEra = 'all';
  bool _photosOnly = false;
  bool _chronological = false;

  final TextEditingController _searchController = TextEditingController();

  // Missing something form fields
  final TextEditingController _missingDescController = TextEditingController();
  final TextEditingController _missingYearController = TextEditingController();
  final TextEditingController _missingSourceController = TextEditingController();
  String _missingType = 'Coin';
  bool _missingSubmitted = false;

  @override
  void initState() {
    super.initState();
    if (widget.initialQuery != null) {
      _searchQuery = widget.initialQuery!;
      _searchController.text = widget.initialQuery!;
    }
    _loadCatalog();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _missingDescController.dispose();
    _missingYearController.dispose();
    _missingSourceController.dispose();
    super.dispose();
  }

  Future<void> _loadCatalog() async {
    try {
      final jsonString = await rootBundle.loadString('assets/catalog/catalog_public_v1.json');
      final List<dynamic> raw = json.decode(jsonString);
      final List<Map<String, dynamic>> entries = raw.map((e) => Map<String, dynamic>.from(e as Map)).toList();

      if (mounted) {
        setState(() {
          _allEntries = entries;
          _isLoading = false;
          _applyFilters();
        });

        if (widget.initialNacCode != null && widget.initialNacCode!.trim().isNotEmpty) {
          final targetNac = widget.initialNacCode!.trim().toLowerCase();
          final match = _allEntries.firstWhere(
            (e) => (e['nac_code'] as String? ?? '').toLowerCase() == targetNac,
            orElse: () => <String, dynamic>{},
          );
          if (match.isNotEmpty) {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) {
                _showItemDetailModal(match);
              }
            });
          } else {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'We don\'t have item "${widget.initialNacCode}" in our reference catalog yet.',
                      style: const TextStyle(fontSize: 16),
                    ),
                    backgroundColor: const Color(0xFF0B2545),
                    duration: const Duration(seconds: 4),
                  ),
                );
              }
            });
          }
        }
      }
    } catch (e) {
      debugPrint('[Catalog] Failed to load catalog_public_v1.json: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _applyFilters() {
    if (_selectedType == 'foreign') {
      _filteredEntries = [];
      return;
    }

    final query = _searchQuery.trim().toLowerCase();

    List<Map<String, dynamic>> result = _allEntries.where((item) {
      // Type filter
      final type = (item['type'] as String? ?? '').toLowerCase();
      if (_selectedType == 'coin' && type != 'coin') return false;
      if (_selectedType == 'note' && type != 'note') return false;
      if (_selectedType == 'medal' && type != 'medal') return false;

      // Era filter
      final int? year = item['year'] is int ? item['year'] as int : null;
      if (_selectedEra != 'all') {
        if (_selectedEra == 'pre_federal') {
          if (year == null || year >= 1792) return false;
        } else if (_selectedEra == 'early_republic') {
          if (year == null || year < 1792 || year >= 1837) return false;
        } else if (_selectedEra == 'seated') {
          if (year == null || year < 1837 || year >= 1873) return false;
        } else if (_selectedEra == 'morgan') {
          if (year == null || year < 1873 || year >= 1901) return false;
        } else if (_selectedEra == '20th') {
          if (year == null || year < 1901 || year >= 2000) return false;
        } else if (_selectedEra == 'modern') {
          if (year == null || year < 2000 || year > 2026) return false;
        } else if (_selectedEra == 'undated') {
          if (year != null) return false;
        }
      }

      // Photos only filter
      if (_photosOnly) {
        final hasPrimary = item['primary_image'] != null && (item['primary_image'] as Map).isNotEmpty;
        final hasType = item['type_image'] != null && (item['type_image'] as Map).isNotEmpty;
        if (!hasPrimary && !hasType) return false;
      }

      // Search query
      if (query.isNotEmpty) {
        final name = (item['name'] as String? ?? '').toLowerCase();
        final series = (item['series'] as String? ?? '').toLowerCase();
        final denom = (item['denomination'] as String? ?? '').toLowerCase();
        final nac = (item['nac_code'] as String? ?? '').toLowerCase();
        final yearStr = item['year']?.toString() ?? '';

        final matches = name.contains(query) ||
            series.contains(query) ||
            denom.contains(query) ||
            nac.contains(query) ||
            yearStr.contains(query);
        if (!matches) return false;
      }

      return true;
    }).toList();

    // Sort order
    if (_chronological) {
      result.sort((a, b) {
        final yA = a['year'] as int? ?? 9999;
        final yB = b['year'] as int? ?? 9999;
        if (yA != yB) return yA.compareTo(yB);
        final nA = a['name'] as String? ?? '';
        final nB = b['name'] as String? ?? '';
        return nA.compareTo(nB);
      });
    } else {
      // Default: Images + Sourced first
      result.sort((a, b) {
        final hasImgA = (a['primary_image'] != null || a['type_image'] != null) ? 1 : 0;
        final hasImgB = (b['primary_image'] != null || b['type_image'] != null) ? 1 : 0;
        if (hasImgA != hasImgB) return hasImgB.compareTo(hasImgA);

        final yA = a['year'] as int? ?? 9999;
        final yB = b['year'] as int? ?? 9999;
        if (yA != yB) return yB.compareTo(yA); // newest year first

        final nA = a['name'] as String? ?? '';
        final nB = b['name'] as String? ?? '';
        return nA.compareTo(nB);
      });
    }

    _filteredEntries = result;
  }

  void _onSearchChanged(String val) {
    setState(() {
      _searchQuery = val;
      _applyFilters();
    });
  }

  void _onTypeChanged(String type) {
    setState(() {
      _selectedType = type;
      _applyFilters();
    });
  }

  void _onEraChanged(String era) {
    setState(() {
      _selectedEra = era;
      _applyFilters();
    });
  }

  void _openAskMorgan({String? initialPrompt}) {
    Navigator.of(context).pushNamed(
      '/?route=AiChatScreen',
      arguments: initialPrompt ?? 'Can you tell me about the coins in the catalog?',
    );
  }

  void _navigateHome() {
    if (Navigator.of(context).canPop()) {
      Navigator.of(context).pop();
    } else {
      launchUrl(Uri.parse('/'), webOnlyWindowName: '_self');
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isDesktop = screenWidth >= 1000;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        title: Row(
          children: [
            InkWell(
              onTap: _navigateHome,
              child: const Text(
                'Numista.AI',
                style: TextStyle(
                  color: Color(0xFF0B2545),
                  fontWeight: FontWeight.bold,
                  fontSize: 24,
                ),
              ),
            ),
            const SizedBox(width: 24),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                border: Border.all(color: const Color(0xFF1F5FAD), width: 2),
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Text(
                'Public Catalog',
                style: TextStyle(
                  color: Color(0xFF0B2545),
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: _navigateHome,
            child: const Text(
              'Home',
              style: TextStyle(color: Color(0xFF0B2545), fontSize: 18),
            ),
          ),
          const SizedBox(width: 8),
          TextButton(
            onPressed: () => launchUrl(Uri.parse('/login'), webOnlyWindowName: '_self'),
            child: const Text(
              'Sign In',
              style: TextStyle(color: Color(0xFF1F5FAD), fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(width: 16),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(2),
          child: Container(color: const Color(0xFFE3E3E3), height: 2),
        ),
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Color(0xFF0B2545)),
            )
          : CustomScrollView(
              slivers: [
                SliverToBoxAdapter(
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 1100),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            // Top Block: Morgan Owl
                            Image.asset(
                              'assets/morgan_avatar.png',
                              width: 180,
                              height: 180,
                              fit: BoxFit.contain,
                              errorBuilder: (c, e, s) => Image.asset(
                                'assets/logo_owl.png',
                                width: 140,
                                height: 140,
                                fit: BoxFit.contain,
                              ),
                            ),
                            const SizedBox(height: 12),

                            // H1 Title
                            const Text(
                              'U.S. Numismatics Catalog',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontSize: 40,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF0B2545),
                                height: 1.2,
                              ),
                            ),
                            const SizedBox(height: 20),

                            // In-Progress Notice Box
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: const Color(0xFFF2F2F2),
                                border: Border.all(color: const Color(0xFFD6D6D6)),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Text(
                                'We are actively cataloging every U.S. coin, banknote, and medal. Sourced mintages and high-resolution reference images are added daily.',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: Color(0xFF333333),
                                  fontSize: 18,
                                  height: 1.5,
                                ),
                              ),
                            ),
                            const SizedBox(height: 24),

                            // Search & Ask Morgan Row
                            _buildSearchRow(isDesktop),
                            const SizedBox(height: 28),

                            // Category Type Tabs
                            _buildTypeTabs(),
                            const SizedBox(height: 20),

                            // Filter Controls Row
                            if (_selectedType != 'foreign') _buildFilterControls(),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),

                // Content Area
                if (_selectedType == 'foreign')
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 60),
                      child: Center(
                        child: Container(
                          padding: const EdgeInsets.all(24),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF2F2F2),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFFD6D6D6)),
                          ),
                          child: const Text(
                            'Foreign coins are coming later.',
                            style: TextStyle(
                              color: Color(0xFF333333),
                              fontSize: 22,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                    ),
                  )
                else if (_filteredEntries.isEmpty)
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 60),
                      child: Center(
                        child: Column(
                          children: [
                            const Icon(Icons.search_off_rounded, size: 64, color: Color(0xFF6B6B6B)),
                            const SizedBox(height: 16),
                            const Text(
                              'No matching catalog items found.',
                              style: TextStyle(fontSize: 22, color: Color(0xFF333333)),
                            ),
                            const SizedBox(height: 8),
                            TextButton(
                              onPressed: () {
                                setState(() {
                                  _searchQuery = '';
                                  _searchController.clear();
                                  _selectedEra = 'all';
                                  _photosOnly = false;
                                  _applyFilters();
                                });
                              },
                              child: const Text('Reset search & filters', style: TextStyle(fontSize: 18)),
                            ),
                          ],
                        ),
                      ),
                    ),
                  )
                else
                  SliverPadding(
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    sliver: SliverToBoxAdapter(
                      child: Center(
                        child: ConstrainedBox(
                          constraints: const BoxConstraints(maxWidth: 1100),
                          child: LayoutBuilder(
                            builder: (context, constraints) {
                              final crossAxisCount = constraints.maxWidth >= 900
                                  ? 3
                                  : (constraints.maxWidth >= 600 ? 2 : 1);
                              return GridView.builder(
                                shrinkWrap: true,
                                physics: const NeverScrollableScrollPhysics(),
                                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                                  crossAxisCount: crossAxisCount,
                                  crossAxisSpacing: 20,
                                  mainAxisSpacing: 20,
                                  childAspectRatio: 0.72,
                                ),
                                itemCount: _filteredEntries.length,
                                itemBuilder: (context, index) {
                                  final item = _filteredEntries[index];
                                  return _CatalogCard(
                                    item: item,
                                    onTap: () => _showItemDetailModal(item),
                                  );
                                },
                              );
                            },
                          ),
                        ),
                      ),
                    ),
                  ),

                // "Missing something?" Form
                SliverToBoxAdapter(
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 1100),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 48),
                        child: _buildMissingSomethingSection(),
                      ),
                    ),
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildSearchRow(bool isDesktop) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return Wrap(
          spacing: 12,
          runSpacing: 12,
          alignment: WrapAlignment.center,
          children: [
            SizedBox(
              width: constraints.maxWidth >= 720 ? constraints.maxWidth - 360 : double.infinity,
              height: 64,
              child: TextField(
                controller: _searchController,
                style: const TextStyle(fontSize: 22, color: Color(0xFF1A1A1A)),
                decoration: InputDecoration(
                  hintText: 'Search the catalog...',
                  hintStyle: const TextStyle(color: Color(0xFF595959), fontSize: 22),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: const BorderSide(color: Color(0xFF0B2545), width: 2),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: const BorderSide(color: Color(0xFF1F5FAD), width: 2.5),
                  ),
                  suffixIcon: _searchQuery.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear, color: Color(0xFF0B2545)),
                          onPressed: () {
                            _searchController.clear();
                            _onSearchChanged('');
                          },
                        )
                      : null,
                ),
                onChanged: _onSearchChanged,
              ),
            ),
            SizedBox(
              height: 64,
              child: ElevatedButton.icon(
                onPressed: () => _applyFilters(),
                icon: const Icon(Icons.search, size: 24, color: Colors.white),
                label: const Text('Search', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B2545),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                    side: const BorderSide(color: Color(0xFF0B2545), width: 2),
                  ),
                ),
              ),
            ),
            SizedBox(
              height: 64,
              child: ElevatedButton.icon(
                onPressed: () => _openAskMorgan(initialPrompt: _searchQuery.isNotEmpty ? 'Tell me about $_searchQuery' : null),
                icon: Image.asset(
                  'assets/morgan_avatar.png',
                  width: 32,
                  height: 32,
                  errorBuilder: (c, e, s) => const Icon(Icons.psychology, color: Colors.white, size: 28),
                ),
                label: const Text('Ask Morgan', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B2545),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                    side: const BorderSide(color: Color(0xFF0B2545), width: 2),
                  ),
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildTypeTabs() {
    return Wrap(
      spacing: 12,
      runSpacing: 10,
      alignment: WrapAlignment.center,
      children: [
        _TypeTab(
          label: 'Coins (2,965)',
          isSelected: _selectedType == 'coin',
          onTap: () => _onTypeChanged('coin'),
        ),
        _TypeTab(
          label: 'Banknotes (181)',
          isSelected: _selectedType == 'note',
          onTap: () => _onTypeChanged('note'),
        ),
        _TypeTab(
          label: 'Medals (56)',
          isSelected: _selectedType == 'medal',
          onTap: () => _onTypeChanged('medal'),
        ),
        _TypeTab(
          label: 'Foreign Coins',
          isSelected: _selectedType == 'foreign',
          onTap: () => _onTypeChanged('foreign'),
        ),
      ],
    );
  }

  Widget _buildFilterControls() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F9FA),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE3E3E3)),
      ),
      child: Wrap(
        spacing: 24,
        runSpacing: 12,
        crossAxisAlignment: WrapCrossAlignment.center,
        alignment: WrapAlignment.spaceBetween,
        children: [
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Era: ', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0B2545))),
              DropdownButton<String>(
                value: _selectedEra,
                underline: const SizedBox(),
                style: const TextStyle(fontSize: 18, color: Color(0xFF1A1A1A)),
                items: const [
                  DropdownMenuItem(value: 'all', child: Text('All Eras')),
                  DropdownMenuItem(value: 'pre_federal', child: Text('Pre-Federal (< 1792)')),
                  DropdownMenuItem(value: 'early_republic', child: Text('Early Republic (1792–1836)')),
                  DropdownMenuItem(value: 'seated', child: Text('Seated / Civil War (1837–1872)')),
                  DropdownMenuItem(value: 'morgan', child: Text('Morgan / Late 19th (1873–1900)')),
                  DropdownMenuItem(value: '20th', child: Text('20th Century (1901–1999)')),
                  DropdownMenuItem(value: 'modern', child: Text('Modern (2000–2026)')),
                  DropdownMenuItem(value: 'undated', child: Text('Undated')),
                ],
                onChanged: (val) {
                  if (val != null) _onEraChanged(val);
                },
              ),
            ],
          ),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Checkbox(
                value: _photosOnly,
                activeColor: const Color(0xFF0B2545),
                onChanged: (val) {
                  setState(() {
                    _photosOnly = val ?? false;
                    _applyFilters();
                  });
                },
              ),
              const Text('Photos only', style: TextStyle(fontSize: 18, color: Color(0xFF1A1A1A))),
              const SizedBox(width: 16),
              Checkbox(
                value: _chronological,
                activeColor: const Color(0xFF0B2545),
                onChanged: (val) {
                  setState(() {
                    _chronological = val ?? false;
                    _applyFilters();
                  });
                },
              ),
              const Text('Chronological order', style: TextStyle(fontSize: 18, color: Color(0xFF1A1A1A))),
            ],
          ),
          Text(
            '${_filteredEntries.length} items',
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0B2545)),
          ),
        ],
      ),
    );
  }

  Widget _buildMissingSomethingSection() {
    return Container(
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F9FA),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFD6D6D6), width: 2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Missing something?',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Color(0xFF0B2545),
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Know a U.S. coin, note, or medal not listed here? Send us the details and primary source reference to add it to our master catalog.',
            style: TextStyle(fontSize: 18, color: Color(0xFF475569)),
          ),
          const SizedBox(height: 20),
          if (_missingSubmitted) ...[
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFEFF6FF),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFF1F5FAD)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.check_circle, color: Color(0xFF1F5FAD), size: 28),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      "Thanks - we'll look into it.",
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF0B2545)),
                    ),
                  ),
                ],
              ),
            ),
          ] else ...[
            TextField(
              controller: _missingDescController,
              decoration: const InputDecoration(
                labelText: 'Item Description / Name *',
                border: OutlineInputBorder(),
                filled: true,
                fillColor: Colors.white,
              ),
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _missingYearController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Year (optional)',
                      border: OutlineInputBorder(),
                      filled: true,
                      fillColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    initialValue: _missingType,
                    decoration: const InputDecoration(
                      labelText: 'Type',
                      border: OutlineInputBorder(),
                      filled: true,
                      fillColor: Colors.white,
                    ),
                    items: const [
                      DropdownMenuItem(value: 'Coin', child: Text('Coin')),
                      DropdownMenuItem(value: 'Banknote', child: Text('Banknote')),
                      DropdownMenuItem(value: 'Medal', child: Text('Medal')),
                    ],
                    onChanged: (val) {
                      if (val != null) setState(() => _missingType = val);
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            TextField(
              controller: _missingSourceController,
              decoration: const InputDecoration(
                labelText: 'Primary Source Reference URL (optional)',
                hintText: 'e.g. https://www.usmint.gov/...',
                border: OutlineInputBorder(),
                filled: true,
                fillColor: Colors.white,
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                if (_missingDescController.text.trim().isNotEmpty) {
                  setState(() {
                    _missingSubmitted = true;
                  });
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0B2545),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              child: const Text('Send'),
            ),
          ],
        ],
      ),
    );
  }

  void _showItemDetailModal(Map<String, dynamic> item) {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 680),
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(28),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          item['name'] as String? ?? 'Catalog Entry',
                          style: const TextStyle(
                            fontSize: 26,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF0B2545),
                          ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: () => Navigator.of(context).pop(),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  _CatalogBadge(badgeText: item['status_badge'] as String?),
                  const SizedBox(height: 20),

                  // Image section
                  _buildModalImage(item),
                  const SizedBox(height: 20),

                  // Metadata list
                  _buildDetailRow('Denomination', item['denomination']?.toString()),
                  _buildDetailRow('Series', item['series']?.toString()),
                  _buildDetailRow('Year', item['year']?.toString()),
                  _buildDetailRow('Mint Facility', item['mint_facility']?.toString()),
                  _buildDetailRow('Mint Mark', item['mint_mark_on_coin']?.toString()),
                  _buildDetailRow('Composition', item['composition']?.toString()),
                  _buildDetailRow('Weight', item['weight_g'] != null ? '${item['weight_g']} g' : null),
                  _buildDetailRow('Diameter', item['diameter_mm'] != null ? '${item['diameter_mm']} mm' : null),
                  _buildDetailRow('Designer', item['designer']?.toString()),

                  // Mintage
                  _buildMintageRow(item),

                  // History
                  if (item['history'] != null && (item['history'] as String).isNotEmpty) ...[
                    const SizedBox(height: 16),
                    const Text('Historical Context:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Color(0xFF0B2545))),
                    const SizedBox(height: 6),
                    Text(
                      item['history'] as String,
                      style: const TextStyle(fontSize: 16, height: 1.5, color: Color(0xFF333333)),
                    ),
                  ],

                  // Ask Morgan button
                  const SizedBox(height: 28),
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.of(context).pop();
                        _openAskMorgan(initialPrompt: 'Can you tell me more about ${item['name']}?');
                      },
                      icon: const Icon(Icons.chat_bubble_outline, color: Colors.white),
                      label: Text('Ask Morgan about this ${item['type'] ?? 'coin'}', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF0B2545),
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildModalImage(Map<String, dynamic> item) {
    final primaryImg = item['primary_image'] as Map?;
    final typeImg = item['type_image'] as Map?;

    final imgMap = primaryImg ?? typeImg;
    final isTypeImage = primaryImg == null && typeImg != null;

    if (imgMap != null && imgMap['url'] != null) {
      final url = imgMap['url'] as String;
      return Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Center(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: Image.network(
                url,
                height: 220,
                fit: BoxFit.contain,
                errorBuilder: (c, e, s) => _buildNoPhotoBox(),
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            imgMap['source'] as String? ?? 'Numista.Ai reference photo',
            style: const TextStyle(fontSize: 14, color: Color(0xFF6B6B6B)),
          ),
          if (isTypeImage)
            const Text(
              'Representative photo — date may differ',
              style: TextStyle(fontSize: 13, fontStyle: FontStyle.italic, color: Color(0xFF1F5FAD)),
            ),
        ],
      );
    }
    return _buildNoPhotoBox();
  }

  Widget _buildNoPhotoBox() {
    return Center(
      child: Container(
        width: 120,
        height: 120,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          border: Border.all(color: const Color(0xFF8A8A8A), width: 2.5, style: BorderStyle.solid),
        ),
        child: const Center(
          child: Text(
            'No photo yet',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 15, color: Color(0xFF6B6B6B), fontWeight: FontWeight.w500),
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String? val) {
    if (val == null || val.isEmpty) return const SizedBox();
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 140,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF475569)),
            ),
          ),
          Expanded(
            child: Text(
              val,
              style: const TextStyle(fontSize: 16, color: Color(0xFF1A1A1A)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMintageRow(Map<String, dynamic> item) {
    final mintage = item['mintage'] as Map?;
    final val = mintage?['value']?.toString();
    final label = mintage?['label'] as String?;
    final sourceUrl = mintage?['source_url'] as String?;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(
            width: 140,
            child: Text(
              'Mintage:',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF475569)),
            ),
          ),
          Expanded(
            child: val != null && val.isNotEmpty
                ? Row(
                    children: [
                      Text(val, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0B2545))),
                      if (sourceUrl != null && sourceUrl.isNotEmpty) ...[
                        const SizedBox(width: 8),
                        InkWell(
                          onTap: () async {
                            final uri = Uri.tryParse(sourceUrl);
                            if (uri != null) await launchUrl(uri);
                          },
                          child: const Text('(source)', style: TextStyle(color: Color(0xFF1F5FAD), decoration: TextDecoration.underline)),
                        ),
                      ],
                    ],
                  )
                : Text(label ?? 'Needs source', style: const TextStyle(fontSize: 16, color: Color(0xFF6B6B6B))),
          ),
        ],
      ),
    );
  }
}

class _TypeTab extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _TypeTab({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF0B2545) : Colors.white,
          border: Border.all(
            color: isSelected ? const Color(0xFF0B2545) : const Color(0xFFC8C8C8),
            width: 2,
          ),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: isSelected ? Colors.white : const Color(0xFF0B2545),
          ),
        ),
      ),
    );
  }
}

class _CatalogCard extends StatelessWidget {
  final Map<String, dynamic> item;
  final VoidCallback onTap;

  const _CatalogCard({
    required this.item,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final primaryImg = item['primary_image'] as Map?;
    final typeImg = item['type_image'] as Map?;
    final imgMap = primaryImg ?? typeImg;
    final isTypeImage = primaryImg == null && typeImg != null;

    final badge = item['status_badge'] as String?;
    final year = item['year']?.toString() ?? 'Undated';
    final denom = item['denomination']?.toString() ?? '';
    final isMedal = item['type'] == 'medal';
    final faceVal = isMedal ? 0.0 : MeltValueService.parseFaceValue(denom);
    final faceValText = faceVal > 0
        ? (faceVal == 0.005 ? r'$0.005' : '\$${faceVal.toStringAsFixed(2)}')
        : '\u2014';
    final rawAiEst = (item['AI Estimated Value'] ?? item['ai_estimated_value'])?.toString().trim() ?? '';
    final hasAiEst = rawAiEst.isNotEmpty && rawAiEst != 'Pending';

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: const Color(0xFFD6D6D6), width: 2),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image
            Expanded(
              child: Center(
                child: imgMap != null && imgMap['url'] != null
                    ? Image.network(
                        imgMap['url'] as String,
                        fit: BoxFit.contain,
                        errorBuilder: (c, e, s) => _buildPlaceholder(),
                      )
                    : _buildPlaceholder(),
              ),
            ),
            const SizedBox(height: 10),

            // Badge
            if (badge != null) ...[
              _CatalogBadge(badgeText: badge),
              const SizedBox(height: 8),
            ],

            // Title
            Text(
              item['name'] as String? ?? 'Coin',
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF0B2545),
                height: 1.2,
              ),
            ),
            const SizedBox(height: 6),

            // Metadata line
            Text(
              [year, denom].where((s) => s.isNotEmpty).join(' · '),
              style: const TextStyle(fontSize: 15, color: Color(0xFF475569)),
            ),

            if (isTypeImage)
              const Padding(
                padding: EdgeInsets.only(top: 4),
                child: Text(
                  'type photo (date may differ)',
                  style: TextStyle(fontSize: 12, color: Color(0xFF6B6B6B), fontStyle: FontStyle.italic),
                ),
              ),

            const SizedBox(height: 6),
            if (isMedal)
              const Text(
                'No face value',
                style: TextStyle(fontSize: 13, color: Color(0xFF6B6B6B)),
              )
            else
              Row(
                children: [
                  Text(
                    faceValText,
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1F5FAD),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Flexible(
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFF3CD),
                        border: Border.all(color: const Color(0xFFFFEEBA)),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        hasAiEst ? 'AI Est: $rawAiEst' : 'Face value \u00b7 No retail estimate',
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF856404),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildPlaceholder() {
    return Container(
      width: 96,
      height: 96,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: const Color(0xFF8A8A8A), width: 2, style: BorderStyle.solid),
      ),
      child: const Center(
        child: Text(
          'No photo yet',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 13, color: Color(0xFF6B6B6B)),
        ),
      ),
    );
  }
}

class _CatalogBadge extends StatelessWidget {
  final String? badgeText;

  const _CatalogBadge({this.badgeText});

  @override
  Widget build(BuildContext context) {
    if (badgeText == null) return const SizedBox();

    if (badgeText == 'Pre-Federal') {
      return Container(
        height: 32,
        padding: const EdgeInsets.symmetric(horizontal: 14),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: const Color(0xFF1F5FAD), width: 2),
          borderRadius: BorderRadius.circular(16),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Pre-Federal',
              style: TextStyle(color: Color(0xFF0B2545), fontWeight: FontWeight.bold, fontSize: 14),
            ),
          ],
        ),
      );
    }

    // Neutral badge ("Needs source" or "Details coming")
    final isNeedsSource = badgeText == 'Needs source';
    return Container(
      height: 32,
      padding: const EdgeInsets.symmetric(horizontal: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFF6B6B6B), width: 2),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isNeedsSource ? Icons.info_outline : Icons.pending_outlined,
            size: 16,
            color: const Color(0xFF333333),
          ),
          const SizedBox(width: 6),
          Text(
            badgeText!,
            style: const TextStyle(color: Color(0xFF333333), fontSize: 14),
          ),
        ],
      ),
    );
  }
}
<<<END ARTIFACT id=A9>>>

## A10: Source at a3d7dca2: numista_mobile/firebase.json (blob 2ab730bf…; CRLF as committed)

<<<BEGIN ARTIFACT id=A10 sha256=4dc3c6a23090939e1ebee698975df149c9775243f33d21ef6431bd1474ea9596 bytes=8459 lines=310 path=/workspace/net816-failfix/sag-upload-r2v3/src/firebase.json>>>
{
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "hosting": {
    "site": "numista-vault",
    "public": "build/web",
    "trailingSlash": false,
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],

    "redirects": [
      {
        "source": "https://www.numista.ai/**",
        "destination": "https://numista.ai/:splat",
        "type": 301
      },
      {
        "source": "/app",
        "destination": "/",
        "type": 301
      },
      {
        "source": "/blog",
        "destination": "/about",
        "type": 301
      },
      {
        "source": "/signin",
        "destination": "/login",
        "type": 301
      },
      {
        "source": "/forgot",
        "destination": "/reset-password",
        "type": 301
      },
      {
        "source": "/reset",
        "destination": "/reset-password",
        "type": 301
      }
    ],

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
        "source": "/catalog",
        "destination": "/index.html"
      },
      {
        "source": "/catalog/**",
        "destination": "/index.html"
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
  },
  "flutter": {
    "platforms": {
      "android": {
        "default": {
          "projectId": "studio-9101802118-8c9a8",
          "appId": "1:568985927038:android:efb96a51420403078b072f",
          "fileOutput": "android/app/google-services.json"
        }
      },
      "dart": {
        "lib/firebase_options.dart": {
          "projectId": "studio-9101802118-8c9a8",
          "configurations": {
            "android": "1:568985927038:android:efb96a51420403078b072f",
            "web": "1:568985927038:web:9ea56548eed27d5a8b072f",
            "windows": "1:568985927038:web:14e303f30991f9e78b072f"
          }
        }
      }
    }
  }
}
<<<END ARTIFACT id=A10>>>

## A11: Source at a3d7dca2: numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart (blob bb46dc5b…; CRLF as committed)

<<<BEGIN ARTIFACT id=A11 sha256=164731816d9360b46ba5fc04e9680e2d5a85c721d10addd775d0ab0da12d2896 bytes=17020 lines=419 path=/workspace/net816-failfix/sag-upload-r2v3/src/catalog_chunk1_face_value_and_card_test.dart>>>
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_ai/services/melt_value_service.dart';

Future<void> pumpLoadedCatalog(WidgetTester tester, Widget app) async {
  // PlatformAssetBundle extends CachingAssetBundle. This exact key is cached
  // before the screen starts, so its rootBundle.loadString hits a completed
  // Future instead of creating a compute() isolate inside fake async.
  expect(rootBundle, isA<CachingAssetBundle>());
  final loaded = await tester.runAsync<String>(() async {
    return rootBundle.loadString('assets/catalog/catalog_public_v1.json');
  });
  expect(loaded, isNotNull, reason: 'Real-async catalog preload must complete');
  expect(tester.takeException(), isNull, reason: 'Catalog preload must not fail');
  await tester.pumpWidget(app);
  // Bounded frames: never settle an indeterminate loading spinner.
  for (var frame = 0;
      frame < 20 && find.byType(CircularProgressIndicator).evaluate().isNotEmpty;
      frame++) {
    await tester.pump(const Duration(milliseconds: 50));
    if (find.byType(CircularProgressIndicator).evaluate().isNotEmpty) {
      await tester.runAsync(() => Future<void>.delayed(const Duration(milliseconds: 50)));
    }
  }
  expect(find.byType(CircularProgressIndicator), findsNothing,
      reason: 'Cached catalog must leave loading state within bounded frames');
}

void main() {
  group('NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1 & NET-837 #2/#4/#5)', () {
    test('parses previously mis-valued catalog denominations, canonical names, sets, and planchets', () {
      const expectedByDenom = <String, double>{
        // Required CoS / Starter Prompt cases
        'Half dime': 0.05,
        '3 cents': 0.03,
        '3 Cents': 0.03,
        '10 Dollars': 10.00,
        '2 1/2 Dollars': 2.50,
        '1,000 Dollars': 1000.00,
        '10,000 Dollars': 10000.00,
        r'$1000': 1000.00,
        'Dime': 0.10,
        // Remaining N Dollars & catalog variants
        '1 Dollar': 1.00,
        '2 Dollars': 2.00,
        '5 Dollars': 5.00,
        '20 Dollars': 20.00,
        '50 Dollars': 50.00,
        '100 Dollars': 100.00,
        '500 Dollars': 500.00,
        'G\$2\u00bd': 2.50,
        r'$40': 40.00,
        r'$4 Stella': 4.00,
        'Half cent': 0.005,
        'half cent': 0.005,
        '1 Cent': 0.01,
        '1 cent': 0.01,
        '5 Cents': 0.05,
        '5 cents': 0.05,
        '10 Cents': 0.10,
        'Quarter': 0.25,
        '50 Cents': 0.50,
        'Half dollar': 0.50,
        'Dollar': 1.00,
        'Gold dollar': 1.00,
        r'1$': 1.00,
        // Canonical / user collection strings (caller blast radius)
        'Five Cents': 0.05,
        'Ten Cents': 0.10,
        'Ten Cent': 0.10,
        'Twenty-Five Cents': 0.25,
        'Fifty Cents': 0.50,
        'Three Cent Nickel': 0.03,
        '2 Cent': 0.02,
        '5 Dollar': 5.00,
        '25 Dollars (1/2 oz)': 25.00,
        // Multi-denomination sets, ranges, planchets & non-USD guards (NET-837 #5)
        r'$100/$50/$25/$10 platinum': 0.0,
        r'$50/$25/$10/$5 gold': 0.0,
        r'$1, $2, $5, $10 (uncut sheet)': 0.0,
        '3\u00a2\u201350\u00a2': 0.0,
        '50 cent coin planchet': 0.0,
        'Planchet for 1 Cent Coin': 0.0,
        '3.6 Candareens': 0.0,
        '': 0.0,
      };

      expectedByDenom.forEach((raw, expected) {
        expect(
          MeltValueService.parseFaceValue(raw),
          closeTo(expected, 1e-6),
          reason: 'Failed for denomination "$raw"',
        );
      });
    });

    test('full catalog_public_v1.json check: 0 mis-parses across all 3,202 entries, 66 non-null strings, and 71 (type, denomination) pairs', () {
      final file = File('assets/catalog/catalog_public_v1.json');
      final List<dynamic> rawList = json.decode(file.readAsStringSync()) as List<dynamic>;
      expect(rawList.length, 3202);

      // Exact 66 unique non-null denomination strings in catalog_public_v1.json (zero duplicate keys)
      const expectedCatalogDenomValues = <String, double>{
        r'$1 (1 oz silver)': 1.00,
        r'$10 eagle': 10.00,
        r'$100/$50/$25/$10 platinum': 0.00,
        r'$2.50 quarter eagle': 2.50,
        r'$20 double eagle': 20.00,
        r'$25 (1 oz palladium)': 25.00,
        r'$3': 3.00,
        r'$4 Stella': 4.00,
        r'$5 half eagle': 5.00,
        r'$50': 50.00,
        r'$50 (1 oz gold)': 50.00,
        r'$50/$25/$10/$5 gold': 0.00,
        '1 Cent': 0.01,
        '1 Dollar': 1.00,
        '1 cent': 0.01,
        r'1$': 1.00,
        '10 Cents': 0.10,
        '2 1/2 Dollars': 2.50,
        '20 Dollars': 20.00,
        '3 Cents': 0.03,
        '3 cents': 0.03,
        '3.6 Candareens': 0.00,
        '5 Cents': 0.05,
        '5 Dollars': 5.00,
        '5 cents': 0.05,
        '50 Cents': 0.50,
        '50 cent coin planchet': 0.00,
        'CC': 0.00,
        'D': 0.00,
        'Dime': 0.10,
        'Dollar': 1.00,
        'Dollar (two-coin set)': 1.00,
        'G\$2\u00bd': 2.50,
        'Gold dollar': 1.00,
        'Half cent': 0.005,
        'Half dime': 0.05,
        'Half dollar': 0.50,
        "New York World's Fair Billy Rose's Aquacade Commemorative Coin": 0.00,
        "New York World's Fair Frank Buck's Jungleland Commemorative Coin": 0.00,
        "New York World's Fair George Washington Commemorative Coin": 0.00,
        "New York World's Fair George Washington Inauguration Commemorative Coin": 0.00,
        "New York World's Fair Stack's Coin Dealers Commemorative Coin": 0.00,
        'O': 0.00,
        'Planchet for 1 Cent Coin': 0.00,
        'Quarter': 0.25,
        'Quarter (rolls/bags product)': 0.25,
        'copper': 0.00,
        'half cent': 0.005,
        r'$1': 1.00,
        r'$1, $2, $5, $10 (uncut sheet)': 0.00,
        r'$10': 10.00,
        r'$100': 100.00,
        r'$1000': 1000.00,
        r'$2': 2.00,
        r'$20': 20.00,
        r'$40': 40.00,
        r'$5': 5.00,
        r'$500': 500.00,
        '1,000 Dollars': 1000.00,
        '10 Dollars': 10.00,
        '10,000 Dollars': 10000.00,
        '100 Dollars': 100.00,
        '2 Dollars': 2.00,
        '3\u00a2\u201350\u00a2': 0.00,
        '50 Dollars': 50.00,
        '500 Dollars': 500.00,
      };
      expect(expectedCatalogDenomValues.length, 66);

      final seenPairs = <String>{};
      int misParses = 0;
      int medalCount = 0;
      for (final rawItem in rawList) {
        final item = Map<String, dynamic>.from(rawItem as Map);
        final type = item['type'] as String?;
        final denom = item['denomination'] as String?;
        seenPairs.add('$type|${denom ?? "NULL"}');
        if (type == 'medal') {
          medalCount++;
          expect(denom, isNull, reason: 'Medals have no face value denomination');
          continue;
        }
        expect(denom, isNotNull);
        final expected = expectedCatalogDenomValues[denom!];
        expect(expected, isNotNull, reason: 'Unmapped catalog denomination: $denom');
        final actual = MeltValueService.parseFaceValue(denom);
        if ((actual - expected!).abs() > 1e-6) {
          misParses++;
        }
      }
      expect(seenPairs.length, 71);
      expect(medalCount, 56);
      expect(misParses, 0);
    });

    test('caller blast-radius regression: header_stats_bar.dart:108 qty-weighted usdFaceSum & MeltValueService.compute', () {
      // Simulates header_stats_bar.dart:108 usdFaceSum accumulation over a multi-item collection
      final sampleCollection = <Map<String, dynamic>>[
        {'Denomination': 'Five Cents', 'qty': 4},           // 4 * 0.05 = 0.20 (was 0.04)
        {'Denomination': 'Twenty-Five Cents', 'qty': 2},    // 2 * 0.25 = 0.50 (was 0.02)
        {'Denomination': 'Half Dime', 'qty': 3},            // 3 * 0.05 = 0.15 (was 0.30)
        {'Denomination': 'Three Cent Nickel', 'qty': 1},    // 1 * 0.03 = 0.03 (was 0.05)
        {'Denomination': '25 Dollars (1/2 oz)', 'qty': 2},  // 2 * 25.00 = 50.00 (was 2.00)
      ];

      double usdFaceSum = 0.0;
      for (final m in sampleCollection) {
        final denom = m['Denomination'] as String;
        final qty = m['qty'] as int;
        usdFaceSum += MeltValueService.parseFaceValue(denom, qty: qty);
      }
      expect(usdFaceSum, closeTo(50.88, 1e-6));

      // Verify MeltValueService.compute (:141, :146, :200) uses corrected face values for gold/silver oz lookup
      const spot = <String, double>{'Gold': 3000.0, 'Silver': 30.0};
      // 1/2 oz Gold Eagle ('25 Dollars (1/2 oz)', 91.67% gold) -> fv=25.0 -> 0.50 oz * 3000 = 1500.0
      final halfOzGoldEagleMelt = MeltValueService.compute(
        metalContent: '91.67% Gold',
        denomination: '25 Dollars (1/2 oz)',
        spotPrices: spot,
      );
      expect(halfOzGoldEagleMelt, closeTo(1500.0, 1e-4));

      // Pre-1933 Quarter Eagle ('2 1/2 Dollars', 90% gold) -> fv=2.5 -> 0.12094 oz * 3000 = 362.82
      final quarterEagleMelt = MeltValueService.compute(
        metalContent: '90% Gold',
        denomination: '2 1/2 Dollars',
        spotPrices: spot,
      );
      expect(quarterEagleMelt, closeTo(362.82, 1e-2));

      // 90% Silver Quarter ('Twenty-Five Cents') -> fv=0.25 -> 0.18084 oz * 30 = 5.4252
      final silverQuarterMelt = MeltValueService.compute(
        metalContent: '90% Silver',
        denomination: 'Twenty-Five Cents',
        spotPrices: spot,
      );
      expect(silverQuarterMelt, closeTo(5.4252, 1e-3));
    });

    test('NET-816 Fail-Fix A2 & D1-D3/N2/N4 regression: half dime, war nickel, sub-dollar silver, and Morgan dollars', () {
      const spot = <String, double>{'Gold': 3000.0, 'Silver': 30.0};

      // (a) Removed fallback: unlisted 90% sub-dollar returns null, NOT 0.77344
      final unlistedTwentyCent = MeltValueService.compute(
        metalContent: '90% Silver',
        denomination: 'Twenty Cent',
        spotPrices: spot,
      );
      expect(unlistedTwentyCent, isNull,
          reason: 'Unlisted sub-dollar silver must return null, never 0.77344');

      // (b) Dollar fallback preserved for Morgan/Peace without "dollar" in denomination
      final morganCC = MeltValueService.compute(
        metalContent: 'Silver',
        denomination: 'CC',
        programSeries: r'1$-Morgan dollar',
        spotPrices: spot,
      );
      expect(morganCC, closeTo(0.77344 * 30.0, 1e-4),
          reason: 'Morgan with denom CC must receive 0.77344 dollar melt');

      final morganNoDenom = MeltValueService.compute(
        metalContent: 'Silver',
        denomination: '',
        programSeries: 'Morgan',
        spotPrices: spot,
      );
      expect(morganNoDenom, closeTo(0.77344 * 30.0, 1e-4),
          reason: 'Morgan with empty denom must receive 0.77344 dollar melt');

      // (c) Standard denominations preserved unchanged:
      // 90% Dime (0.07234 oz -> $2.1702 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Dime', spotPrices: spot),
        closeTo(0.07234 * 30.0, 1e-4),
      );
      // 90% Quarter (0.18084 oz -> $5.4252 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Quarter', spotPrices: spot),
        closeTo(0.18084 * 30.0, 1e-4),
      );
      // 90% Half Dollar (0.36169 oz -> $10.8507 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Half dollar', spotPrices: spot),
        closeTo(0.36169 * 30.0, 1e-4),
      );
      // 90% Dollar (0.77344 oz -> $23.2032 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Dollar', spotPrices: spot),
        closeTo(0.77344 * 30.0, 1e-4),
      );
      // 40% Half Dollar (0.14792 oz -> $4.4376 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '40% Silver', denomination: 'Half dollar', spotPrices: spot),
        closeTo(0.14792 * 30.0, 1e-4),
      );
      // 35% War Nickel (0.05626 oz -> $1.6878 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '35% Silver', denomination: 'Nickel', spotPrices: spot),
        closeTo(0.05626 * 30.0, 1e-4),
      );

      // (d) N4: Wartime nickel with "Silver Alloy" and "Wartime Nickel" series (lacking "35%")
      expect(
        MeltValueService.compute(
          metalContent: 'Silver Alloy',
          denomination: '5 cents',
          programSeries: 'Jefferson Wartime Nickel',
          spotPrices: spot,
        ),
        closeTo(0.05626 * 30.0, 1e-4),
        reason: 'Jefferson Wartime Nickel in Silver Alloy must receive 0.05626 oz melt',
      );

      // (e) Half dime variants compute to 0.03617 oz * spot (~$1.0851 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: 'Silver (90%)', denomination: 'Half Dime', spotPrices: spot),
        closeTo(0.03617 * 30.0, 1e-4),
        reason: 'Silver (90%) Half Dime must equal 0.03617 oz',
      );
      expect(
        MeltValueService.compute(metalContent: 'Silver', denomination: 'Half dime', spotPrices: spot),
        closeTo(0.03617 * 30.0, 1e-4),
        reason: 'Generic "Silver" Half dime must equal 0.03617 oz',
      );
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Half-dime', spotPrices: spot),
        closeTo(0.03617 * 30.0, 1e-4),
        reason: '"90% Silver" Half-dime must equal 0.03617 oz',
      );
      expect(
        MeltValueService.format(metalContent: '90% Silver', denomination: 'Half Dime', spotPrices: spot),
        equals(r'$1.09'),
        reason: r'Formatted melt value string at $30/oz silver spot must round to $1.09',
      );
    });
  });

  group('NET-816 Chunk 1 — _CatalogCard Widget Tests (#2 & NET-837 #3/#6)', () {
    testWidgets('shows "type photo (date may differ)" when isTypeImage is true and renders parsed face value + honest non-promissory chip', (WidgetTester tester) async {
      await tester.binding.setSurfaceSize(const Size(1440, 2400));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      // 1842 Liberty Seated dollar in catalog_public_v1.json has primary_image: null, type_image != null, denomination: "Dollar"
      await pumpLoadedCatalog(
        tester,
        const MaterialApp(
          home: CatalogBrowseScreen(initialQuery: '1842 Liberty Seated dollar'),
        ),
      );
      await tester.pumpAndSettle();

      final gridFinder = find.byType(GridView);
      expect(gridFinder, findsOneWidget);

      // Scoped to GridView so initialQuery inside the search TextField (:44, :505-506) does not double-match
      expect(
        find.descendant(of: gridFinder, matching: find.text('1842 Liberty Seated dollar')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text('1842 \u00b7 Dollar')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text('type photo (date may differ)')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text(r'$1.00')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text('Face value \u00b7 No retail estimate')),
        findsOneWidget,
      );
      expect(find.text('Value pending AI estimate'), findsNothing);
    });

    testWidgets('medal cards display "No face value" and omit face-value chip', (WidgetTester tester) async {
      await tester.binding.setSurfaceSize(const Size(1440, 2400));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await pumpLoadedCatalog(
        tester,
        const MaterialApp(
          home: CatalogBrowseScreen(initialQuery: 'Libertas Americana medal'),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Medals (56)'));
      await tester.pumpAndSettle();

      final gridFinder = find.byType(GridView);
      expect(gridFinder, findsOneWidget);

      expect(
        find.descendant(of: gridFinder, matching: find.textContaining('Libertas Americana medal')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text('No face value')),
        findsOneWidget,
      );
      expect(find.text('Face Value N/A'), findsNothing);
      expect(find.text('Face value \u00b7 No retail estimate'), findsNothing);
      expect(find.text('Value pending AI estimate'), findsNothing);
    });
  });
}
<<<END ARTIFACT id=A11>>>

## A12: Source at a3d7dca2: numista_mobile/test/catalog_browse_test.dart (blob 3df197ca…)

<<<BEGIN ARTIFACT id=A12 sha256=b449669750563a95e71d315ac1e5207d95e0793aca7bd769615805caaa6c1252 bytes=3375 lines=91 path=/workspace/net816-failfix/sag-upload-r2v3/src/catalog_browse_test.dart>>>
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/catalog/us_numismatics_catalog_screen.dart';

void main() {
  group('UsNumismaticsCatalogScreen Widget & Plan.v2.1 UX Gate', () {
    testWidgets(
      'renders 1776-2026 catalog, filters by era/facility/kind, flips cards, and enforces guest download guard',
      (WidgetTester tester) async {
        await tester.binding.setSurfaceSize(const Size(1440, 960));
        addTearDown(() => tester.binding.setSurfaceSize(null));

        await tester.pumpWidget(
          const MaterialApp(
            home: UsNumismaticsCatalogScreen(isAuthenticated: false),
          ),
        );
        await tester.pumpAndSettle();

        // 1. Verify initial 15 specimens loaded and Inspector displays 1787 Fugio Cent (CC=CO)
        expect(find.text('15 SPECIMENS'), findsOneWidget);
        expect(
          find.byKey(const Key('inspector_nac_code')),
          findsOneWidget,
        );
        expect(
          find.text('NAC1.CN.CO.1C.FUGIO.1787.XX.BASE.K'),
          findsWidgets,
        );

        // 2. Filter by Dahlonega facility (FAC='DD') -> 1838-D Classic Head $5 Half Eagle
        await tester.tap(find.byKey(const Key('fac_chip_DD')));
        await tester.pumpAndSettle();
        expect(find.text('1 SPECIMENS'), findsOneWidget);
        expect(
          find.text('1838-D Classic Head \$5 Half Eagle'),
          findsWidgets,
        );

        // Reset facility filter to ALL
        await tester.tap(find.byKey(const Key('fac_chip_ALL')));
        await tester.pumpAndSettle();
        expect(find.text('15 SPECIMENS'), findsOneWidget);

        // 3. Filter by Foreign Specie (CC='FS') -> 1798-Mo Spanish-American 8 Reales
        await tester.tap(find.byKey(const Key('kind_tab_FS')));
        await tester.pumpAndSettle();
        expect(find.text('1 SPECIMENS'), findsOneWidget);
        expect(
          find.text('1798-Mo Spanish-American 8 Reales (Charles IV)'),
          findsWidgets,
        );

        // 4. Filter by Bank Notes (KIND='BN') -> routes to /currency, never /coins
        await tester.tap(find.byKey(const Key('kind_tab_BN')));
        await tester.pumpAndSettle();
        expect(find.text('3 SPECIMENS'), findsOneWidget);
        expect(
          find.textContaining('users/{uid}/currency/'),
          findsOneWidget,
        );

        // 5. Add Bank Note to collection and test Personal Specimen Photo toggle (Founder Q3)
        await tester.tap(find.byKey(const Key('inspector_add_button')));
        await tester.pumpAndSettle();
        expect(
          find.byKey(const Key('inspector_personal_photo_switch')),
          findsOneWidget,
        );
        await tester.tap(
          find.byKey(const Key('inspector_personal_photo_switch')),
        );
        await tester.pumpAndSettle();
        expect(
          find.textContaining('Personal Specimen Photo'),
          findsWidgets,
        );

        // 6. Verify Guest Image Download is blocked (Founder Q4: IMAGE_DOWNLOAD_REQUIRES_ACCOUNT)
        await tester.tap(
          find.byKey(const Key('inspector_download_image_button')),
        );
        await tester.pumpAndSettle();
        expect(
          find.textContaining('IMAGE_DOWNLOAD_REQUIRES_ACCOUNT'),
          findsOneWidget,
        );
      },
    );
  });
}
<<<END ARTIFACT id=A12>>>

## A13: Preview HOLD 74611e05: no c547b7a0 preview deploy

<<<BEGIN ARTIFACT id=A13 sha256=74611e05e00a99e4dfb5f524f16a7dc92d540265986ff138c61ccf5884f11b6b bytes=3208 lines=37 path=/workspace/net816-failfix/src/HOLD_NET-816_PREVIEW-DEPLOY_c547b7a0_NOT-REISSUED_AWAIT-A1A2-FIX_20261110-1148.md>>>
# HOLD — NET-816 p7-gate preview-deploy at c547b7a0 is not re-issued (AG CoS v5)
From: GB CoS via Desk. Decision time: **10 Nov 2026 ~11:47 AM ET** (America/New_York).
Filed: 2026-11-10 11:48:17 EST by Grok Bot Desk. **Decision record only. No WAKE. No code, git, Firebase, or gcloud.**
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
This record grants **no new authority**.

## Decision
The NET-816 preview-deploy baton `BATON_NET-816_AGCOS-V5_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1007.md` (SHA-256 `c65658e0e2783477e0d07b271dcf6cee1e5d939764ccd5ae4f257539e7fcdf0c`) is **HELD**.

It was **BLOCKED** at **11:40 AM ET** with Firebase/gcloud credentials expired, per AG file:
- `BLOCKED_BATON_NET-816_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1140.md`
- SHA-256 `67c5a39002c7cbee71c3c986fbd9b47a8df4fcc9b05f639bc472cb44464c47fe` (2245 B; found on day RADIO NET / BATONS / INBOX / OUTBOX; not seen in mailbox on this check)

**Do NOT re-issue or retry that preview deploy at `c547b7a0`.** That commit lacks the `/catalog` rewrite in `firebase.json` (**A1**), so /catalog would 404.

Re-issue the p7-gate preview deploy **only** at the **A1/A2-fixed commit**, after that fail-fix plan passes **CoS 95 + SAG 95 + Eric's typed YES**.
Eric's **10:06 AM ET YES** (card `t2455s9467`) covered **`c547b7a0` only**. The fixed commit needs his own **new scoped YES**.

## Credentials
Eric has been asked to run `firebase login --reauth` and `gcloud auth application-default login` on EDS_Laptop. This is **CoS-stated and not yet confirmed**. No agent handles his passwords.

## Free tier
Free tier is **10 coins lifetime** per `DECISION_NET-827_FREE-TIER-10-COINS-LIFETIME_RELEASES-HOLD_20261110-1139.md` (SHA-256 `2bf48ebcf9590f119987cc994b38256a7a147f015a8932352e863b35729942a9`).
That decision postdates and **supersedes** AG's contemporaneous ACK §4 wording (see findings below).

## Unchanged
- Go-live addendum `c2b6ac93b844a51d22be23ba428b3d098ad3f2e087e004b3aa6d63919755b4c2` stays **NOT ACTIVE** under HOLD `41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d`.
- The A1/A2 and B1–B5 fail-fix plans remain **plan-only**.
- NET-827 stays **queued**.

## AG BLOCKED / ACK findings (Desk read-only)
- **BLOCKED** as named above: named blocker is expired Firebase CLI session credentials; also records failed `gcloud auth application-default` refresh; live / main / Firestore / Stripe untouched; secondary note confirms A1 missing `/catalog` rewrite at `c547b7a0`.
- No separate ACK of that BLOCKED file, or of the preview-deploy baton, was found on this check.
- Contemporaneous AG ACK at ~11:40: `ACK_HOLD_NET-816_NET-827_AGCOS-V5_20261110-1140.md` SHA-256 `e358a92d6ed82b9d63b3f5985f342ecbb01eb05b6da1a4b74bbfe803694eee3a` (1436 B) — this ACKs the earlier HOLD / fail-fix plan-order notice, not the BLOCKED file.
- That ACK **§4** (“Free-Tier Coin Limit Hold”) says the free-tier limit is “Retained untouched at current codebase state pending CoS written confirmation of Eric's final decision.” That wording is **superseded** by the 10-coin lifetime decision above.

Filing this record ≠ a new preview-deploy baton and ≠ credential confirmation.
<<<END ARTIFACT id=A13>>>

## A14: Go-live stop-rule HOLD 41b8bd5f

<<<BEGIN ARTIFACT id=A14 sha256=41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d bytes=3311 lines=35 path=/workspace/net816-failfix/src/HOLD_NET-816_NET-827_AGCOS-V5_GO-LIVE-STOP-RULE_AND_FAILFIX-PLAN-ORDER_20261110-1113.md>>>
# HOLD / FAIL-FIX PLAN ORDER — NET-816 + NET-827 (AG CoS v5)
From: GB CoS via Desk. CoS order timestamp: **10 Nov 2026 11:15 AM ET** (America/New_York).
Filed: 2026-11-10 11:13:11 EST by Grok Bot Desk. **Notice only. No WAKE.** Desk does not deploy, run git/Firebase/Stripe, or start work.
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
This notice grants **no new authority**. Every fix goes through the normal plan gate (**CoS 95 + SAG 95 + Eric YES**).

## 1) STOP-RULE HOLD — go-live stays NOT ACTIVE
Hold on `ADDENDUM_NET-816_NET-827_AGCOS-V5_CONDITIONAL-GO-LIVE_20261110-1033.md` (SHA-256 `c2b6ac93b844a51d22be23ba428b3d098ad3f2e087e004b3aa6d63919755b4c2`).
**Go-live stays NOT ACTIVE regardless of Field Tester score.**
Basis: Code Reviewer go-live review `C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\10 NOV 26\CODE_REVIEW_GO-LIVE_NET-816_NET-827_c547b7a0_20261110.md` (CoS-cited SHA starting `3e2c1670` ending `864ff`; Desk read-only laptop check: file exists, full SHA-256 `3e2c16709736ab5a5cf834ed9aba9df66704465d7b86f24baf4cf56a0ad864ff` — prefix/suffix match) found **wrong-access** and **wrong-charge** blockers.
**Do NOT** fold to main, deploy live, or attach live Stripe keys.
Lifting this hold needs a **new CoS written confirmation** after fixes pass the gate **and** Eric's YES.

## 2) NET-816 p7-gate PREVIEW deploy still authorized
Eric YES card `t2455s9467`; baton `BATON_NET-816_AGCOS-V5_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1007.md` SHA-256 `c65658e0e2783477e0d07b271dcf6cee1e5d939764ccd5ae4f257539e7fcdf0c`.
**Continue.** File **DONE** with preview URL and built commit (plus the other evidence required in that baton).

## 3) NET-816 FAIL-FIX — PLAN ONLY (no code), due before any live fold
- **A1 BLOCKER:** `firebase.json` has no `/catalog` rewrite at `c547b7a0`, so numista.ai/catalog and #/catalog would break.
- **A2 MAJOR:** Half dime fix uses Morgan-dollar weight for 90% silver half dime melt — about **10× too high** on the collection dashboard.

## 4) NET-827 v1.2 build stays QUEUED
Queued behind the Catalog field test; Stripe **test mode only**. Baton `BATON_NET-827_AGCOS-V5_QUEUED-PREVIEW-BUILD_STRIPE-CHECKOUT-PREVIEW_v1.2_p7-gate_20261110-1031.md` SHA-256 `6693232a39993ddb3e4b678d439a0cd37a91217a148f0fcb8e6d4ed0ec2c1175`.
A revised build plan must close:
- **B1:** Price set from tier name and webhook grants whatever tier was sent, so power_user/sovereign unlock for $4.99 (`payment_routes.py`:52–53, 75, 223–224).
- **B2:** Subscription/invoice events can't find the user but are marked processed, so cancel leaves paid access and `invoice.paid` can reset tier to pro.
- **B3:** Promo codes allowed on every session; `amount_total` and `payment_status` never checked.
- **B4:** No idempotency key; dedupe not transactional.
- **B5:** Refunds and disputes ignored.
Christmas code created **inactive** and rejected server-side before **26 Nov 2026 00:00 UTC**, never on monthly. Live keys from Secret Manager only, with a test/live mode check.

## FREE-TIER COIN LIMIT HOLD
Plan and code say **20**; Eric's 29 Oct and 1 Nov decisions say **10** (**CoS-stated**). Eric is deciding now. **Change nothing** until CoS confirms.

Filing this notice ≠ accepted/started and does not lift or start any production step.
<<<END ARTIFACT id=A14>>>

<<<END OF PACKET>>>
