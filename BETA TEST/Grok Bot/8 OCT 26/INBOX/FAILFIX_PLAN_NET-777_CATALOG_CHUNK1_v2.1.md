# FAILFIX PLAN: Public Catalog Browse — CHUNK 1 (`v2.1`) (NET-777 / NET-816 / NET-831 Items 1–2 / NET-837)

**Document Path:** `docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.1.md`  
**Version:** `v2.1` (Chunk 1 of 6 — Scoped to `RADIO_NET-831` Items 1–2 & `RADIO_NET-837` Items 1–7)  
**Writer Lineage:**
- **Active Writer:** Catalog Chunk 1 Writer (`9bbe20e4-a0d5-4a25-b16a-f616630ad4bb`) — **New-Writer Attempt 2 of 4** (governed by the 4-try rule: stop and notify Eric after 4 failed tries).
- **New-Writer Prior Attempts:** `v2.0` (Attempt 1 of 4) = 68/100 FAIL (`COS_SCORE_NET-816_CATALOG_CHUNK1_v2.0_20261107.md`).
- **Prior Writer Lineage (preserved separately, not erased):** AG CoS v4 (`ba2bfdb2`) = 10+ attempts, parked under writer-cap hold; `v1.10` = 48/100 FAIL (`COS_SCORE_NET-816_CATALOG_v1.10_20261107.md`); `v1.11` = 58/100 FAIL (`COS_SCORE_NET-816_CATALOG_v1.11_20261107.md`).

**Filed DTG:** `2026-11-07T16:08:00-05:00` (4:08 PM EST, America/New_York — verified against system clock at filing)  
**Authority:** `BETA TEST/Grok Bot/8 OCT 26/BATONS/RADIO_NET-837_GROKCOS-to-CHUNK1WRITER-9bbe20e4_REVISE-816-CHUNK1-v2.1_20261107.md`, `BETA TEST/Grok Bot/8 OCT 26/BATONS/COS_SCORE_NET-816_CATALOG_CHUNK1_v2.0_20261107.md` (68/100 FAIL), `BETA TEST/Grok Bot/8 OCT 26/OUTBOX/STARTER_CATALOG_FRESH-AG_CHUNK1_20261107.md`, and `BETA TEST/Grok Bot/8 OCT 26/BATONS/RADIO_NET-831_GROKCOS-to-AGCOS_REVISE-816-v1.12_20261107.md` (items 1–2).

---

## 0. Standing Hard Rules & Gate Discipline

1. **PLAN ONLY:** Zero source code edits, zero builds, zero test executions, zero deploys, zero Firestore/database writes, zero GCS bucket uploads, and zero branch merges are performed in this delivery.
2. **Branch & Target Locks:**
   - Future authorized build/preview target: **`p7-v8.9` (`p7-gate` preview) only**, via the two-commit landing sequence in §3 (Prerequisite Commit 1: Catalog baseline port from `dev` `b0b05808` to `p7-v8.9`; Commit 2: Chunk 1 patches and tests).
   - Production lock: **`origin/main` is locked at `9f04550a` (`9f04550a45fa4da082ba8948c2d89a521a90fa45`)** and must never be touched.
   - **Stripe:** Strictly **OFF**.
   - **Billing / Spend Controls:** **Alerts only, no spend caps.** Never modify billing or budget cap controls.
3. **Approval Chain:** GB CoS ≥ 95/100 → Independent SAG ≥ 95/100 → **Founder Eric's explicit typed `YES`** before any code execution. No Argon in the review cycle. An agent asserting approval is never approval.
4. **Scope Boundary:** This document covers **Chunk 1 only** (`RADIO_NET-831` #1 Face-Value Parser & #2 `_CatalogCard` minimal diff + `RADIO_NET-837` #1–#7). Chunks 2–6 (#3 Images/CSP/CORS, #4 Known-Error Caller, #5 Greysheet, #6 Ask Morgan, #7 Web History, #8 Bundle C, #9 Congress.gov Key Rotation, #10 remaining tests, #11 full gate matrix) remain parked for subsequent chunks. Cards `NET-817` and all other queue items are untouched.

---

## 1. Read-Only Verified Repository Pins (`git rev-parse` / `git ls-tree` / `git show`)

Every pin reported in `STARTER_CATALOG_FRESH-AG_CHUNK1_20261107.md:17`, `COS_SCORE_NET-816_CATALOG_v1.11_20261107.md:10`, and `COS_SCORE_NET-816_CATALOG_CHUNK1_v2.0_20261107.md:10` was re-verified read-only on `2026-11-07`:

| Ref / Pin | Full Commit SHA | Status & Ancestry Reconciliation |
|---|---|---|
| Reported `dev` pin | `b0b058087f1492244a0c0b769e126b38ac1ba06c` | Verified ancestor of both local `dev` (`eb23e011d1e25446e256518e5065b4a989aaba17`) and `origin/dev` (`f097707d...`). Contains the Catalog source tree (`catalog_browse_screen.dart`, `us_numismatics_catalog_screen.dart`, `web_meta*.dart`, `catalog_service.dart`, `nac_code_parser.dart`, `catalog_inspector_panel.dart`, `dual_sided_catalog_card.dart`, `catalog_public_v1.json`, `catalog_browse_test.dart`, `nac_code_parser_test.dart`, `melt_value_service.dart`). |
| Reported `origin/dev` pin (`b15fdda1`) | `b15fdda1be1dc36bf94fd97ca1817b63992bb09d` | Verified ancestor of `origin/dev`. Zero source files changed between `b0b05808`, `b15fdda1`, `afbbbd45`, `602c82d3`, and `f097707d`. |
| `origin/dev` tip at `v2.0` filing | `afbbbd45950c459c04a1e82b437dd346c522c3da` | `origin/dev` tip immediately prior to `v2.0` docs sync (`602c82d347250e55507e936ce4aceffa45ce99be`). |
| Current `origin/dev` HEAD at `v2.1` filing | `f097707d` (ancestor `602c82d347250e55507e936ce4aceffa45ce99be`) | `docs(cos): land NET-813 FAIL76 + NET-816 Chunk1 FAIL68 scores onto dev`. |
| Reported `p7` pin | `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235` | Verified ancestor of `p7-v8.9` / `origin/p7-v8.9`. |
| `origin/p7-v8.9` tip at `v2.0` filing | `c8c4dbdd80a5fc6fc69a0dc149e0dc4abcf04f97` | Corrects `v2.0` §1 (which cited `5fbff9af`; two docs-only handoff commits landed between `5fbff9af` and `c8c4dbdd` at `15:09:14 EST` before `f7e8369a`). |
| Current `origin/p7-v8.9` HEAD at `v2.1` filing | `2cddeda8` (ancestor `e8721405` → `f7e8369a` → `c8c4dbdd`) | `docs(net-817): deliver Cards v1.9 and Images v1.9 failfix plans and review baton (AG CoS v5 attempt 1/4)`. |
| Locked `origin/main` | `9f04550a45fa4da082ba8948c2d89a521a90fa45` | Verified intact at `9f04550a`. Untouched. |

### Verified Target & Prerequisite File Blobs Across Pins

| File Path | Blob SHA on `b0b05808` (`dev`) | Blob SHA on `origin/p7-v8.9` | Lines / Status |
|---|---|---|---|
| `numista_mobile/lib/services/melt_value_service.dart` | `b210bff669d34f8a16bb63c79ea1e5b6a78db653` | `b210bff669d34f8a16bb63c79ea1e5b6a78db653` | **208 lines.** Byte-identical across `b0b05808`, `4d17ca5e`, `origin/dev`, and `origin/p7-v8.9`. |
| `numista_mobile/lib/screens/home_dashboard.dart` | `4708815005...` (`:299-301`, `:415`, `:440`, `:472`) | `a0015bf45a...` (`:299-301`, `:415`, `:440`, `:472`) | `_computeFaceValue` and all 3 caller lines (`:415`, `:440`, `:472`) are at identical line numbers on both branches. |
| `numista_mobile/lib/widgets/header_stats_bar.dart` | `4e1ba9b3f8...` (`:108`) | `4e1ba9b3f8...` (`:108`) | Byte-identical across `b0b05808` and `origin/p7-v8.9`. |
| `numista_mobile/pubspec.yaml` | `7d5aa3c378...` (has `- assets/catalog/` at `:97`) | `639a908851...` (lacks `- assets/catalog/` at `:97`) | **130 lines** on `p7-v8.9`. Prerequisite hunk adds `- assets/catalog/` (§3.B). |
| `numista_mobile/lib/main.dart` | `e9053e3ec3...` (has `/catalog` route `:12`, `:132-133`, `:154-181`) | `a46ef10e89...` (lacks `/catalog` route) | Prerequisite hunk ports `/catalog` import and route block (§3.C). |
| `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` | `3a0d310936a1715034e65c7384476c19e2030ad7` | *(absent — ported in Prerequisite Commit 1)* | **1,232 lines.** Ported in §3.A, patched in §5. |
| `numista_mobile/lib/screens/catalog/us_numismatics_catalog_screen.dart` | `fde73f5a252e180b50b2eb290da859efd30e1609` | *(absent — ported in Prerequisite Commit 1)* | **598 lines.** Ported in §3.A so `test/catalog_browse_test.dart` compiles and runs. |
| `numista_mobile/lib/screens/catalog/web_meta.dart` | `3e4e53cfc743b756d889d37681acef193b28bd0e` | *(absent — ported in Prerequisite Commit 1)* | **3 lines.** Ported in §3.A. |
| `numista_mobile/lib/screens/catalog/web_meta_stub.dart` | `6e13a102c8b64324bcb08d5cc601832a0a6b1c5b` | *(absent — ported in Prerequisite Commit 1)* | **4 lines.** Ported in §3.A. |
| `numista_mobile/lib/screens/catalog/web_meta_web.dart` | `2868ee2c00d03075f4cf14d60e59c9b0531d8f45` | *(absent — ported in Prerequisite Commit 1)* | **13 lines.** Ported in §3.A. |
| `numista_mobile/lib/services/catalog/catalog_service.dart` | `6e79607fe6c5645cc95ba2fd7d64af582d6eb018` | *(absent — ported in Prerequisite Commit 1)* | **865 lines.** Required by `us_numismatics_catalog_screen.dart`. Ported in §3.A. |
| `numista_mobile/lib/services/catalog/nac_code_parser.dart` | `48611b020257ebb247af84517c222976a08d0814` | *(absent — ported in Prerequisite Commit 1)* | **113 lines.** Required by `catalog_service.dart`. Ported in §3.A. |
| `numista_mobile/lib/widgets/catalog/catalog_inspector_panel.dart` | `101c90be679a179154eb1c99429bb1eaea7ffe3d` | *(absent — ported in Prerequisite Commit 1)* | **380 lines.** Required by `us_numismatics_catalog_screen.dart`. Ported in §3.A. |
| `numista_mobile/lib/widgets/catalog/dual_sided_catalog_card.dart` | `6109f9032ce9830561005a696e67e0c0c50cbd09` | *(absent — ported in Prerequisite Commit 1)* | **481 lines.** Required by `us_numismatics_catalog_screen.dart`. Ported in §3.A. |
| `numista_mobile/assets/catalog/catalog_public_v1.json` | `a018d13ad3a3aac2ae84afad704d53543fe2b5df` | *(absent — ported in Prerequisite Commit 1)* | **3,202 entries** (`217,232` lines). Ported in §3.A. |
| `numista_mobile/test/catalog_browse_test.dart` | `3df197ca2cc0424b5dac7f1ad491a5ca9bb669af` | *(absent — ported in Prerequisite Commit 1)* | **91 lines.** Ported in §3.A and preserved untouched. |
| `numista_mobile/test/nac_code_parser_test.dart` | `f36e523c616a44b068ca6a5bdf8b6d709a0a461b` | *(absent — ported in Prerequisite Commit 1)* | **83 lines.** Ported in §3.A. |

---

## 2. Closeout Table for `RADIO_NET-837` (CoS-68 Blocking Must-Fixes #1–#7) & `RADIO_NET-831` (#1–#2)

| # | `RADIO_NET-837` / CoS-68 Must-Fix | Verified Pinned Code Evidence (`file:line` + SHA + verbatim line) | Planned Resolution in `v2.1` | Section |
|---|---|---|---|---|
| **1** | **Landing path (blocking):** Catalog tree, asset, `pubspec.yaml` `assets/catalog/`, and `main.dart` `/catalog` route are absent on `p7-v8.9`. Add a prerequisite step that ports the catalog tree from `dev` `b0b05808` to `p7-v8.9` via `git checkout b0b05808 -- <exact paths>`, provide exact `pubspec.yaml` and `main.dart` hunks against `p7-v8.9`, verify imports/dependencies against `p7-v8.9`, and update §7 rollback. | • `origin/p7-v8.9:numista_mobile/pubspec.yaml:92-97` (blob `639a908851`):<br>`92:   assets:`<br>`93:     - assets/`<br>`94:     - assets/data/`<br>`95:     - assets/fonts/`<br>`96:     - assets/mint_mark_diagrams/`<br>• `b0b05808:numista_mobile/pubspec.yaml:97` (blob `7d5aa3c378`):<br>`97:     - assets/catalog/`<br>• `b0b05808:numista_mobile/lib/main.dart:12, 132-133, 154-181` (blob `e9053e3ec3`):<br>`12: import 'screens/catalog/catalog_browse_screen.dart';`<br>`132:       normalizedPath == '/catalog' ||`<br>`133:       path.startsWith('/catalog/') ||`<br>`155:   if (normalizedPath == '/catalog' || path.startsWith('/catalog/')) {` | Defines **Prerequisite Commit 1** on `p7-v8.9`:<br>1. `git checkout b0b058087f1492244a0c0b769e126b38ac1ba06c -- <12 exact catalog paths>` (full transitive import closure so both `CatalogBrowseScreen` and `UsNumismaticsCatalogScreen` / `catalog_browse_test.dart` compile).<br>2. Applies `git apply`-verified hunks to `numista_mobile/pubspec.yaml` (`@@ -94,6 +94,7 @@`) and `numista_mobile/lib/main.dart` (`@@ -9,6 +9,7 @@`, `@@ -129,6 +130,8 @@`, `@@ -148,6 +151,35 @@`).<br>3. Verified all external packages (`flutter`, `flutter_test`, `url_launcher: ^6.3.2` at `p7 pubspec.yaml:48`, `web: ^1.1.0` at `p7 pubspec.yaml:49`) are already on `p7-v8.9`.<br>4. Updated §7 rollback to revert Commit 2 and/or Prerequisite Commit 1 cleanly via `git revert`. | §3, §7 |
| **2** | **Test compile (blocking):** Remove duplicate `const` map key `r'$50'` in `expectedCatalogDenomValues` (or key by `(type, denomination)`). Confirm no other duplicate keys exist. | In `v2.0` lines 601 and 649, `r'$50'` appeared twice in `const expectedCatalogDenomValues` because `'$50'` exists in both `type == 'coin'` (×2) and `type == 'note'` (×6). Four strings appear in both `coin` and `note`: `'$50'`, `'1 Dollar'`, `'20 Dollars'`, `'5 Dollars'`. | Removed duplicate `r'$50'` from `expectedCatalogDenomValues` (now contains the exact **66 unique non-null `denomination` strings**, verified unique) and added `expectedByTypeAndDenom` keyed by `'type|denomination'` covering all **71 distinct `(type, denomination)` pairs**. | §6 |
| **3** | **Widget finders (blocking):** Scope title and name finders to the grid (`find.descendant(of: find.byType(GridView), ...)`) so `initialQuery` in the search `TextField` (`:43–44`, `:505–506`) does not double-match. | `b0b05808:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:42-45, 505-506` (blob `3a0d310936`):<br>`42:     if (widget.initialQuery != null) {`<br>`43:       _searchQuery = widget.initialQuery!;`<br>`44:       _searchController.text = widget.initialQuery!;`<br>`45:     }`<br>`505:               child: TextField(`<br>`506:                 controller: _searchController,` | Scoped widget test finders for card text to `find.descendant(of: find.byType(GridView), matching: ...)` so `_searchController.text` inside the search `TextField`'s `EditableText` never double-matches the card title. | §6 |
| **4** | **Caller blast radius:** List every `parseFaceValue` caller (`home_dashboard.dart:300`, `header_stats_bar.dart:108`, `melt_value_service.dart:141/146/200`). State that user and collection face totals will change, with examples. Add regression tests for `header_stats_bar` face-sum inputs. | • `numista_mobile/lib/screens/home_dashboard.dart:299-301, 415, 440, 472`:<br>`299:   static double _computeFaceValue(String denom) {`<br>`300:     return MeltValueService.parseFaceValue(denom);`<br>`301:   }`<br>• `numista_mobile/lib/widgets/header_stats_bar.dart:107-109` (blob `4e1ba9b3f8`):<br>`107:       if (!isForeign) {`<br>`108:         usdFaceSum += MeltValueService.parseFaceValue(denom, qty: qty);`<br>`109:       }`<br>• `numista_mobile/lib/services/melt_value_service.dart:141, 146, 200` (blob `b210bff669`):<br>`141:         final fv = parseFaceValue(denom);`<br>`146:         final fv = parseFaceValue(denom);`<br>`200:     final fv = parseFaceValue(rawDenom);` | Added dedicated §4.D caller blast-radius analysis covering all 5 call sites, documenting how existing user collection face-value totals (and gold/silver melt lookups) change with concrete before/after examples, and added unit regression tests for `qty`-weighted `usdFaceSum` accumulation and `MeltValueService.compute` in §6. | §4.D, §6 |
| **5** | **Face-value semantics:** Multi-denomination sets (`'$1, $2, $5, $10 (uncut sheet)'`, `'$100/$50/$25/$10 platinum'`, `'$50/$25/$10/$5 gold'`) and planchets (`'50 cent coin planchet'`, `'Planchet for 1 Cent Coin'`): return `0.0` → display `'—'` on card, never just the max or legal-tender value on an unstruck blank. Update expected map. | `b0b05808:numista_mobile/assets/catalog/catalog_public_v1.json` (blob `a018d13a`):<br>• `'$100/$50/$25/$10 platinum'` (`coin` ×1)<br>• `'$50/$25/$10/$5 gold'` (`coin` ×1)<br>• `'$1, $2, $5, $10 (uncut sheet)'` (`note` ×1)<br>• `'50 cent coin planchet'` (`coin` ×1)<br>• `'Planchet for 1 Cent Coin'` (`coin` ×1) | Added early guard in `MeltValueService.parseFaceValue` returning `0.0` for `s.contains('planchet')`, `s.contains('candareen')`, multi-denomination `$` lists (`RegExp(r'\$\d[\d,]*(?:\.\d+)?\s*(?:/\s*\$?|,\s*\$)\s*\d')`), and numeric ranges (`RegExp(r'\d\s*(?:\u00a2|c|cents?)?\s*[\u2013\-]\s*\d')`). All 7 strings return `0.0` and render `'—'` on `_CatalogCard`. Updated §4.A table and §6 expected maps. | §4.A, §4.C, §6 |
| **6** | **AI-estimate chip:** Either name the pipeline, data key (aligned with NET-817 `'AI Estimated Value'`) and owning chunk, or replace the chip in Chunk 1 with honest copy and no promise of an estimate. | `numista_mobile/lib/widgets/header_stats_bar.dart:92` (blob `4e1ba9b3f8`):<br>`92:       final rawAi = m['AI Estimated Value'] ?? m['ai_estimated_value'];`<br>And `b0b05808:numista_mobile/assets/catalog/catalog_public_v1.json`: `0 / 3,202` entries have `'AI Estimated Value'`, `'ai_estimated_value'`, or `'cpg_retail'`. | Both aligned and made honest:<br>1. `_CatalogCard` checks `final rawAiEst = (item['AI Estimated Value'] ?? item['ai_estimated_value'])?.toString().trim() ?? '';` (exact NET-817 key alignment).<br>2. Since `0 / 3,202` static catalog entries have `'AI Estimated Value'` and no AI-estimate pipeline is scheduled in Chunks 1–6, `_CatalogCard` replaces the unbacked `'Value pending AI estimate'` promise with honest copy: **`'Face value \u00b7 No retail estimate'`** (`#856404` on `#FFF3CD`, 4.96:1 WCAG AA). | §4.B, §5 |
| **7** | **Hygiene:** Recount hunk headers so all diffs are `git apply`-clean. Correct `"70 pairs"` to **71 `(type, denomination)` pairs / 67 distinct `denomination` values (66 non-null strings + `null`)**. Record `p7-v8.9` tip at `v2.0` filing as `c8c4dbdd`. | Verified via `git diff --no-index -U3` and `git apply --cached --check` (exit code `0` on all 4 diffs):<br>• `pubspec.yaml`: `@@ -94,6 +94,7 @@`<br>• `main.dart`: `@@ -9,6 +9,7 @@`, `@@ -129,6 +130,8 @@`, `@@ -148,6 +151,35 @@`<br>• `melt_value_service.dart`: `@@ -58,31 +58,62 @@`<br>• `catalog_browse_screen.dart`: `@@ -2,6 +2,7 @@`, `@@ -1085,6 +1086,13 @@`, `@@ -1147,6 +1155,46 @@` | All 4 diffs in §3.B, §3.C, §4.C, and §5.B are generated directly from `git diff -U3` against the pinned blobs and verified `git apply`-clean (`exit=0`). Corrected pair/string counts to **71 `(type, denomination)` pairs and 67 distinct `denomination` values (66 non-null strings + `null`)** everywhere. Recorded `c8c4dbdd` in §1. | §1, §3, §4, §5 |

---

## 3. Blocking Must-Fix #1: Prerequisite Catalog Baseline Port from `dev` (`b0b05808`) to `p7-v8.9`

Because `p7-v8.9` (`origin/p7-v8.9`) does not yet contain the `lib/screens/catalog/`, `lib/services/catalog/`, `lib/widgets/catalog/`, `assets/catalog/catalog_public_v1.json`, or `test/catalog_browse_test.dart` files that landed on `dev` (`b0b058087f1492244a0c0b769e126b38ac1ba06c`), Chunk 1 execution on `p7-v8.9` (after GB CoS ≥95, SAG ≥95, and Founder Eric's typed `YES`) is structured as **two sequential atomic commits** on `p7-v8.9`:

1. **Prerequisite Commit 1 (Baseline Port from `b0b05808` to `p7-v8.9`):** Ports the 12 catalog files byte-for-byte from `b0b058087f1492244a0c0b769e126b38ac1ba06c` plus the `pubspec.yaml` asset declaration hunk and `main.dart` `/catalog` route hunk.
2. **Commit 2 (Chunk 1 Failfix Patch & Tests on `p7-v8.9`):** Applies the `MeltValueService.parseFaceValue` diff (§4.C), the `_CatalogCard` minimal diff (§5.B), and adds `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart` (§6).

### A. Exact Files Ported in Prerequisite Commit 1 (`git checkout b0b058087f1492244a0c0b769e126b38ac1ba06c -- <paths>`)

```bash
git checkout b0b058087f1492244a0c0b769e126b38ac1ba06c -- \
  numista_mobile/lib/screens/catalog/catalog_browse_screen.dart \
  numista_mobile/lib/screens/catalog/us_numismatics_catalog_screen.dart \
  numista_mobile/lib/screens/catalog/web_meta.dart \
  numista_mobile/lib/screens/catalog/web_meta_stub.dart \
  numista_mobile/lib/screens/catalog/web_meta_web.dart \
  numista_mobile/lib/services/catalog/catalog_service.dart \
  numista_mobile/lib/services/catalog/nac_code_parser.dart \
  numista_mobile/lib/widgets/catalog/catalog_inspector_panel.dart \
  numista_mobile/lib/widgets/catalog/dual_sided_catalog_card.dart \
  numista_mobile/assets/catalog/catalog_public_v1.json \
  numista_mobile/test/catalog_browse_test.dart \
  numista_mobile/test/nac_code_parser_test.dart
```

#### Transitive Import & Package Dependency Audit Against `origin/p7-v8.9`

Every `import` and `export` statement across all 12 ported files was audited read-only against `origin/p7-v8.9`:
- `catalog_browse_screen.dart:1-4`: `dart:convert`, `package:flutter/material.dart`, `package:flutter/services.dart`, `package:url_launcher/url_launcher.dart` → `url_launcher: ^6.3.2` is present at `origin/p7-v8.9:numista_mobile/pubspec.yaml:48`.
- `us_numismatics_catalog_screen.dart:1-4`: `package:flutter/material.dart`, `../../services/catalog/catalog_service.dart`, `../../widgets/catalog/catalog_inspector_panel.dart`, `../../widgets/catalog/dual_sided_catalog_card.dart` → all 3 relative targets are included in the 12-file checkout above.
- `web_meta.dart:2-3`, `web_meta_stub.dart:1-4`, `web_meta_web.dart:2`: `package:web/web.dart` → `web: ^1.1.0` is present at `origin/p7-v8.9:numista_mobile/pubspec.yaml:49`.
- `catalog_service.dart:7`: `nac_code_parser.dart` → included in the 12-file checkout above.
- `catalog_inspector_panel.dart:1-4` & `dual_sided_catalog_card.dart:1-3`: `dart:math`, `package:flutter/material.dart`, `catalog_service.dart`, `nac_code_parser.dart` → all included.
- `test/catalog_browse_test.dart:1-3` & `test/nac_code_parser_test.dart:1-3`: `package:flutter/material.dart`, `package:flutter_test/flutter_test.dart`, `package:numista_ai/...` → `flutter_test` is present at `origin/p7-v8.9:numista_mobile/pubspec.yaml:65` and `name: numista_ai` at `:1`.

### B. Prerequisite `numista_mobile/pubspec.yaml` Diff Against `origin/p7-v8.9` (Verified `git apply --cached --check` Exit `0`)

#### Pinned `origin/p7-v8.9:numista_mobile/pubspec.yaml:92-99` (blob `639a908851`):
```yaml
92:   assets:
93:     - assets/
94:     - assets/data/
95:     - assets/fonts/
96:     - assets/mint_mark_diagrams/
97: 
98: 
99:   fonts:
```

#### Planned Unified Diff (`numista_mobile/pubspec.yaml`):
```diff
--- a/numista_mobile/pubspec.yaml
+++ b/numista_mobile/pubspec.yaml
@@ -94,6 +94,7 @@ flutter:
     - assets/data/
     - assets/fonts/
     - assets/mint_mark_diagrams/
+    - assets/catalog/
 
 
   fonts:
```

### C. Prerequisite `numista_mobile/lib/main.dart` Diff Against `origin/p7-v8.9` (Verified `git apply --cached --check` Exit `0`)

#### Pinned `origin/p7-v8.9:numista_mobile/lib/main.dart:9-15, 129-154` (blob `a46ef10e89`):
```dart
9: import 'screens/attorney_portal_screen.dart';
10: import 'screens/not_found_screen.dart';
11: import 'screens/public_wishlist_view_screen.dart';
12: import 'services/theme_provider.dart';
13: import 'widgets/morgan_feedback_drawer.dart';
14: import 'services/guest_seed_service.dart';
...
129:       normalizedPath == '/demo' ||
130:       normalizedPath == '/app' ||
131:       normalizedPath == '/blog' ||
132:       path.startsWith('/wishlist') ||
133:       path.startsWith('/attorney_portal') ||
...
148:     return;
149:   }
150: 
151:   // Synchronously parse Front Door URL routes
152:   bool isPendingDemo = false;
153:   String? pendingPublicRoute;
```

#### Planned Unified Diff (`numista_mobile/lib/main.dart`):
```diff
--- a/numista_mobile/lib/main.dart
+++ b/numista_mobile/lib/main.dart
@@ -9,6 +9,7 @@ import 'screens/welcome_screen.dart';
 import 'screens/attorney_portal_screen.dart';
 import 'screens/not_found_screen.dart';
 import 'screens/public_wishlist_view_screen.dart';
+import 'screens/catalog/catalog_browse_screen.dart';
 import 'services/theme_provider.dart';
 import 'widgets/morgan_feedback_drawer.dart';
 import 'services/guest_seed_service.dart';
@@ -129,6 +130,8 @@ Future<void> main() async {
       normalizedPath == '/demo' ||
       normalizedPath == '/app' ||
       normalizedPath == '/blog' ||
+      normalizedPath == '/catalog' ||
+      path.startsWith('/catalog/') ||
       path.startsWith('/wishlist') ||
       path.startsWith('/attorney_portal') ||
       path.startsWith('/attorney') ||
@@ -148,6 +151,35 @@ Future<void> main() async {
     return;
   }
 
+  // Public Catalog direct entry (zero auth required)
+  if (normalizedPath == '/catalog' || path.startsWith('/catalog/')) {
+    String? initialNacCode;
+    if (path.startsWith('/catalog/')) {
+      final sub = path.substring('/catalog/'.length).trim();
+      if (sub.isNotEmpty) {
+        initialNacCode = Uri.decodeComponent(sub);
+      }
+    }
+    if (initialNacCode == null && uri.queryParameters.containsKey('item')) {
+      initialNacCode = uri.queryParameters['item'];
+    }
+    runApp(MaterialApp(
+      title: 'Numista.AI Public Catalog',
+      debugShowCheckedModeBanner: false,
+      theme: ThemeData(
+        brightness: Brightness.light,
+        scaffoldBackgroundColor: Colors.white,
+        primaryColor: const Color(0xFF0B2545),
+        colorScheme: ColorScheme.fromSeed(
+          seedColor: const Color(0xFF1F5FAD),
+          primary: const Color(0xFF0B2545),
+        ),
+      ),
+      home: CatalogBrowseScreen(initialNacCode: initialNacCode),
+    ));
+    return;
+  }
+
   // Synchronously parse Front Door URL routes
   bool isPendingDemo = false;
   String? pendingPublicRoute;
```

---

## 4. Must-Fix #1 (`RADIO_NET-831` #1) & `RADIO_NET-837` #4–#7: `MeltValueService.parseFaceValue` Patch, Semantics, Re-Count & Caller Blast Radius

### A. Independent Re-Count of `catalog_public_v1.json` (`b0b05808`, 3,202 Entries, 71 `(type, denomination)` Pairs, 67 Distinct `denomination` Values)

Read-only inspection of `b0b05808:numista_mobile/assets/catalog/catalog_public_v1.json` (blob `a018d13ad3a3aac2ae84afad704d53543fe2b5df`) confirms:
- **3,202 total entries:** `2,965` `coin`, `181` `note`, `56` `medal`.
- **71 distinct `(type, denomination)` pairs** across **67 distinct `denomination` values** (`66` unique non-null strings + `null` on all 56 medals; 4 strings appear in both `coin` and `note`: `'$50'`, `'1 Dollar'`, `'20 Dollars'`, `'5 Dollars'`).
- **0 retail price fields:** `0` occurrences of `cpg_retail`, `retail`, `face_value`, `AI Estimated Value`, or `ai_estimated_value`.
- **Primary join key `nac_code`:** present on `3,202 / 3,202` entries.

#### 1. Breakdown of the 103 CoS-Reported Mis-Valued Entries + 23 Additional Entries Corrected in `v2.1` (126 Total Entries Changed)

| Failure Category | Raw `denomination` String in `catalog_public_v1.json` | Item `type` | Entry Count | Pinned Output (`:53-99`) | Pinned Line Causing Defect | Patched `v2.1` Output (USD) |
|---|---|---|---:|---:|---|---:|
| **1. `Half dime` shadowed by `dime`** | `'Half dime'` | `coin` | 35 | `$0.10` | `:80` `s.contains('dime')` runs before `:81` `s.contains('half dime')` | **`0.05`** |
| **2. `3 cents` falls through to `cent`** | `'3 cents'` (`6`) + `'3 Cents'` (`3`) | `coin` | 9 | `$0.01` | `:83` checks `'three cent'` or `'3c'` (no space); hits `:86` `s.contains('cent')` | **`0.03`** |
| **3. `N Dollars` ($N \neq 1$) falls through to `dollar`** | `'2 1/2 Dollars'` (`coin` ×1)<br>`'2 Dollars'` (`note` ×3)<br>`'5 Dollars'` (`coin` ×1, `note` ×7)<br>`'10 Dollars'` (`note` ×11)<br>`'20 Dollars'` (`coin` ×3, `note` ×8)<br>`'50 Dollars'` (`note` ×6)<br>`'100 Dollars'` (`note` ×7)<br>`'500 Dollars'` (`note` ×3)<br>`'1,000 Dollars'` (`note` ×6)<br>`'10,000 Dollars'` (`note` ×2) | `coin` (5), `note` (53) | 58 | `$1.00` | Word/symbol checks at `:65-74` miss `<digits> dollars`; all 58 hit `:87` `s.contains('dollar')` | **`2.50`** / **`2.00`** / **`5.00`** / **`10.00`** / **`20.00`** / **`50.00`** / **`100.00`** / **`500.00`** / **`1000.00`** / **`10000.00`** |
| **4. `$1000` shadowed by `$100`** | `'$1000'` | `note` | 1 | `$100.00` | `:66` `s.contains(r'$100')` matches prefix of `'$1000'` | **`1000.00`** |
| **Subtotal (4 CoS-Reported Categories)** | | | **103** | | `35 + 9 + 58 + 1 = 103` entries | |
| **5. Quarter Eagle `G$2½` shadowed by `$2`** | `'G$2½'` (`'G$2\u00bd'`) | `coin` | 16 | `$2.00` | `:74` `s.contains(r'$2')` matches prefix of `'g$2½'` | **`2.50`** |
| **6. Multi-denomination sets/ranges (`RADIO_NET-837` #5)** | `'$100/$50/$25/$10 platinum'` (`coin` ×1)<br>`'$50/$25/$10/$5 gold'` (`coin` ×1)<br>`'$1, $2, $5, $10 (uncut sheet)'` (`note` ×1)<br>`'3¢–50¢'` (`note` ×1) | `coin` (2), `note` (2) | 4 | `$100.00`<br>`$50.00`<br>`$10.00`<br>`$3.00` | `:66`, `:67`, `:70` picked the highest `$` token in a multi-coin/sheet set; `:91` parsed `'3'` from `'3¢–50¢'` as `$3.00` | **`0.00`** (card renders `'—'`, never just the max) |
| **7. Unstruck planchets & non-USD pattern (`RADIO_NET-837` #5)** | `'50 cent coin planchet'` (`coin` ×1)<br>`'Planchet for 1 Cent Coin'` (`coin` ×1)<br>`'3.6 Candareens'` (`coin` ×1) | `coin` | 3 | `$0.50`<br>`$0.01`<br>`$3.60` | Unstruck planchet blanks are not legal tender; Candareens is a non-USD unit | **`0.00`** (card renders `'—'`) |
| **Total Catalog Entries Changed** | | | **126** | | `103 + 16 + 4 + 3 = 126` entries | |

#### 2. Complete 71-Row `(type, denomination)` Audit Table Across All 3,202 Entries (67 Distinct `denomination` Values)

| # | `type` | Raw `denomination` | Count | Pinned (`:53-99`) | Patched (`v2.1`) | Card Display Status |
|---:|---|---|---:|---:|---:|---|
| 1 | `coin` | `'$1 (1 oz silver)'` | 1 | `1.00` | `1.00` | `$1.00` · Unchanged ✓ |
| 2 | `coin` | `'$10 eagle'` | 11 | `10.00` | `10.00` | `$10.00` · Unchanged ✓ |
| 3 | `coin` | `'$100/$50/$25/$10 platinum'` | 1 | `100.00` | **`0.00`** | **`'—'` (Multi-denom set guard, NET-837 #5)** |
| 4 | `coin` | `'$2.50 quarter eagle'` | 2 | `2.50` | `2.50` | `$2.50` · Unchanged ✓ |
| 5 | `coin` | `'$20 double eagle'` | 15 | `20.00` | `20.00` | `$20.00` · Unchanged ✓ |
| 6 | `coin` | `'$25 (1 oz palladium)'` | 1 | `25.00` | `25.00` | `$25.00` · Unchanged ✓ |
| 7 | `coin` | `'$3'` | 3 | `3.00` | `3.00` | `$3.00` · Unchanged ✓ |
| 8 | `coin` | `'$4 Stella'` | 2 | `4.00` | `4.00` | `$4.00` · Unchanged ✓ |
| 9 | `coin` | `'$5 half eagle'` | 18 | `5.00` | `5.00` | `$5.00` · Unchanged ✓ |
| 10 | `coin` | `'$50'` *(shared string #1/4)* | 2 | `50.00` | `50.00` | `$50.00` · Unchanged ✓ |
| 11 | `coin` | `'$50 (1 oz gold)'` | 1 | `50.00` | `50.00` | `$50.00` · Unchanged ✓ |
| 12 | `coin` | `'$50/$25/$10/$5 gold'` | 1 | `50.00` | **`0.00`** | **`'—'` (Multi-denom set guard, NET-837 #5)** |
| 13 | `coin` | `'1 Cent'` | 11 | `0.01` | `0.01` | `$0.01` · Unchanged ✓ |
| 14 | `coin` | `'1 Dollar'` *(shared string #2/4)* | 2 | `1.00` | `1.00` | `$1.00` · Unchanged ✓ |
| 15 | `coin` | `'1 cent'` | 381 | `0.01` | `0.01` | `$0.01` · Unchanged ✓ |
| 16 | `coin` | `'1$'` | 11 | `1.00` | `1.00` | `$1.00` · Unchanged ✓ |
| 17 | `coin` | `'10 Cents'` | 4 | `0.10` | `0.10` | `$0.10` · Unchanged ✓ |
| 18 | `coin` | `'2 1/2 Dollars'` | 1 | `1.00` | **`2.50`** | **`$2.50` (Fixed, NET-831 #1)** |
| 19 | `coin` | `'20 Dollars'` *(shared string #3/4)* | 3 | `1.00` | **`20.00`** | **`$20.00` (Fixed, NET-831 #1)** |
| 20 | `coin` | `'3 Cents'` | 3 | `0.01` | **`0.03`** | **`$0.03` (Fixed, NET-831 #1)** |
| 21 | `coin` | `'3 cents'` | 6 | `0.01` | **`0.03`** | **`$0.03` (Fixed, NET-831 #1)** |
| 22 | `coin` | `'3.6 Candareens'` | 1 | `3.60` | **`0.00`** | **`'—'` (Non-USD guard, NET-837 #5)** |
| 23 | `coin` | `'5 Cents'` | 4 | `0.05` | `0.05` | `$0.05` · Unchanged ✓ |
| 24 | `coin` | `'5 Dollars'` *(shared string #4/4)* | 1 | `1.00` | **`5.00`** | **`$5.00` (Fixed, NET-831 #1)** |
| 25 | `coin` | `'5 cents'` | 116 | `0.05` | `0.05` | `$0.05` · Unchanged ✓ |
| 26 | `coin` | `'50 Cents'` | 3 | `0.50` | `0.50` | `$0.50` · Unchanged ✓ |
| 27 | `coin` | `'50 cent coin planchet'` | 1 | `0.50` | **`0.00`** | **`'—'` (Planchet guard, NET-837 #5)** |
| 28 | `coin` | `'CC'` | 1 | `0.00` | `0.00` | `'—'` · Unchanged ✓ |
| 29 | `coin` | `'D'` | 1 | `0.00` | `0.00` | `'—'` · Unchanged ✓ |
| 30 | `coin` | `'Dime'` | 407 | `0.10` | `0.10` | `$0.10` · Unchanged ✓ |
| 31 | `coin` | `'Dollar'` | 497 | `1.00` | `1.00` | `$1.00` · Unchanged ✓ |
| 32 | `coin` | `'Dollar (two-coin set)'` | 1 | `1.00` | `1.00` | `$1.00` · Unchanged ✓ |
| 33 | `coin` | `'G$2½'` | 16 | `2.00` | **`2.50`** | **`$2.50` (Fixed Quarter Eagle ½)** |
| 34 | `coin` | `'Gold dollar'` | 3 | `1.00` | `1.00` | `$1.00` · Unchanged ✓ |
| 35 | `coin` | `'Half cent'` | 7 | `0.005` | `0.005` | `$0.005` · Unchanged ✓ |
| 36 | `coin` | `'Half dime'` | 35 | `0.10` | **`0.05`** | **`$0.05` (Fixed, NET-831 #1)** |
| 37 | `coin` | `'Half dollar'` | 431 | `0.50` | `0.50` | `$0.50` · Unchanged ✓ |
| 38 | `coin` | `"New York World's Fair Billy Rose's Aquacade Commemorative Coin"` | 1 | `0.00` | `0.00` | `'—'` · Unchanged ✓ |
| 39 | `coin` | `"New York World's Fair Frank Buck's Jungleland Commemorative Coin"` | 1 | `0.00` | `0.00` | `'—'` · Unchanged ✓ |
| 40 | `coin` | `"New York World's Fair George Washington Commemorative Coin"` | 1 | `0.00` | `0.00` | `'—'` · Unchanged ✓ |
| 41 | `coin` | `"New York World's Fair George Washington Inauguration Commemorative Coin"` | 1 | `0.00` | `0.00` | `'—'` · Unchanged ✓ |
| 42 | `coin` | `"New York World's Fair Stack's Coin Dealers Commemorative Coin"` | 1 | `0.00` | `0.00` | `'—'` · Unchanged ✓ |
| 43 | `coin` | `'O'` | 4 | `0.00` | `0.00` | `'—'` · Unchanged ✓ |
| 44 | `coin` | `'Planchet for 1 Cent Coin'` | 1 | `0.01` | **`0.00`** | **`'—'` (Planchet guard, NET-837 #5)** |
| 45 | `coin` | `'Quarter'` | 943 | `0.25` | `0.25` | `$0.25` · Unchanged ✓ |
| 46 | `coin` | `'Quarter (rolls/bags product)'` | 1 | `0.25` | `0.25` | `$0.25` · Unchanged ✓ |
| 47 | `coin` | `'copper'` | 5 | `0.00` | `0.00` | `'—'` · Unchanged ✓ |
| 48 | `coin` | `'half cent'` | 1 | `0.005` | `0.005` | `$0.005` · Unchanged ✓ |
| 49 | `medal` | `null` | 56 | `0.00` | `0.00` | **`'No face value'` (Medal rule)** |
| 50 | `note` | `'$1'` | 41 | `1.00` | `1.00` | `$1.00` · Unchanged ✓ |
| 51 | `note` | `'$1, $2, $5, $10 (uncut sheet)'` | 1 | `10.00` | **`0.00`** | **`'—'` (Multi-denom set guard, NET-837 #5)** |
| 52 | `note` | `'$10'` | 13 | `10.00` | `10.00` | `$10.00` · Unchanged ✓ |
| 53 | `note` | `'$100'` | 6 | `100.00` | `100.00` | `$100.00` · Unchanged ✓ |
| 54 | `note` | `'$1000'` | 1 | `100.00` | **`1000.00`** | **`$1000.00` (Fixed, NET-831 #1)** |
| 55 | `note` | `'$2'` | 20 | `2.00` | `2.00` | `$2.00` · Unchanged ✓ |
| 56 | `note` | `'$20'` | 13 | `20.00` | `20.00` | `$20.00` · Unchanged ✓ |
| 57 | `note` | `'$40'` | 1 | `40.00` | `40.00` | `$40.00` · Unchanged ✓ |
| 58 | `note` | `'$5'` | 16 | `5.00` | `5.00` | `$5.00` · Unchanged ✓ |
| 59 | `note` | `'$50'` *(shared string #1/4)* | 6 | `50.00` | `50.00` | `$50.00` · Unchanged ✓ |
| 60 | `note` | `'$500'` | 2 | `500.00` | `500.00` | `$500.00` · Unchanged ✓ |
| 61 | `note` | `'1 Dollar'` *(shared string #2/4)* | 7 | `1.00` | `1.00` | `$1.00` · Unchanged ✓ |
| 62 | `note` | `'1,000 Dollars'` | 6 | `1.00` | **`1000.00`** | **`$1000.00` (Fixed, NET-831 #1)** |
| 63 | `note` | `'10 Dollars'` | 11 | `1.00` | **`10.00`** | **`$10.00` (Fixed, NET-831 #1)** |
| 64 | `note` | `'10,000 Dollars'` | 2 | `1.00` | **`10000.00`** | **`$10000.00` (Fixed, NET-831 #1)** |
| 65 | `note` | `'100 Dollars'` | 7 | `1.00` | **`100.00`** | **`$100.00` (Fixed, NET-831 #1)** |
| 66 | `note` | `'2 Dollars'` | 3 | `1.00` | **`2.00`** | **`$2.00` (Fixed, NET-831 #1)** |
| 67 | `note` | `'20 Dollars'` *(shared string #3/4)* | 8 | `1.00` | **`20.00`** | **`$20.00` (Fixed, NET-831 #1)** |
| 68 | `note` | `'3¢–50¢'` | 1 | `3.00` | **`0.00`** | **`'—'` (Range guard, NET-837 #5)** |
| 69 | `note` | `'5 Dollars'` *(shared string #4/4)* | 7 | `1.00` | **`5.00`** | **`$5.00` (Fixed, NET-831 #1)** |
| 70 | `note` | `'50 Dollars'` | 6 | `1.00` | **`50.00`** | **`$50.00` (Fixed, NET-831 #1)** |
| 71 | `note` | `'500 Dollars'` | 3 | `1.00` | **`500.00`** | **`$500.00` (Fixed, NET-831 #1)** |

---

### B. Explicit Medal Display, Non-Medal Unknown Display, `'AI Estimated Value'` Alignment & Contrast Specification (`RADIO_NET-837` #5–#6)

1. **Medal Display (56 Entries, `item['type'] == 'medal'`):**
   - All 56 medals in `catalog_public_v1.json` have `"denomination": null` and are non-denominated exonumia.
   - `_CatalogCard` checks `final isMedal = item['type'] == 'medal';` and never passes `item['name']` to `parseFaceValue`.
   - When `isMedal == true`, `_CatalogCard` renders `'No face value'` (`TextStyle(fontSize: 13, color: Color(0xFF6B6B6B))`) and omits any face-value amount or amber chip.
2. **Non-Medal Sets, Planchets & Unknown Denomination Display (23 Entries where `faceVal == 0.0`):**
   - For the 23 non-medal entries whose `denomination` string is not a single legal-tender USD coin/note denomination (`'$100/$50/$25/$10 platinum'` ×1, `'$50/$25/$10/$5 gold'` ×1, `'$1, $2, $5, $10 (uncut sheet)'` ×1, `'3¢–50¢'` ×1, `'50 cent coin planchet'` ×1, `'Planchet for 1 Cent Coin'` ×1, `'3.6 Candareens'` ×1, `'CC'` ×1, `'D'` ×1, `'O'` ×4, `'copper'` ×5, World's Fair commemorative coins ×5), `parseFaceValue` returns `0.0`, and `_CatalogCard` displays `'\u2014'` (`'—'`, never `'$0.00'`).
3. **NET-817 `'AI Estimated Value'` Key Alignment & Honest Non-Promissory Copy (`RADIO_NET-837` #6):**
   - `_CatalogCard` reads `final rawAiEst = (item['AI Estimated Value'] ?? item['ai_estimated_value'])?.toString().trim() ?? '';` and `final hasAiEst = rawAiEst.isNotEmpty && rawAiEst != 'Pending';`, matching the exact production key `'AI Estimated Value'` used in `numista_mobile/lib/widgets/header_stats_bar.dart:92` and NET-817.
   - Because `0 / 3,202` static entries in `catalog_public_v1.json` have `'AI Estimated Value'` and no AI-estimate pipeline is scheduled for static public catalog browse in Chunks 1–6, `_CatalogCard` does **not** render the promissory text `'Value pending AI estimate'`. Instead, when `!hasAiEst`, the amber badge renders honest copy: **`'Face value \u00b7 No retail estimate'`** (and if `hasAiEst` is ever populated via `'AI Estimated Value'`, it renders `'AI Est: $rawAiEst'`).
4. **Re-Measured WCAG 2.1 Contrast Ratios:**
   - Amber chip text `#856404` ($L = 0.141097$) on `#FFF3CD` ($L = 0.897690$): $\frac{0.897690 + 0.05}{0.141097 + 0.05} = 4.9592:1 \approx \mathbf{4.96:1}$ (passes WCAG 2.1 AA `4.5:1`).
   - Face-value text `#1F5FAD` on `#FFFFFF`: **6.37:1** (passes WCAG 2.1 AA).
   - Muted `'No face value'` / `'type photo (date may differ)'` text `#6B6B6B` on `#FFFFFF`: **5.33:1** (passes WCAG 2.1 AA).

---

### C. Pinned Before / Planned After Diff for `numista_mobile/lib/services/melt_value_service.dart:53-99` (Verified `git apply --cached --check` Exit `0`)

#### Pinned Code (`b0b05808` / `4d17ca5e` / `origin/dev` / `origin/p7-v8.9`, blob `b210bff669d34f8a16bb63c79ea1e5b6a78db653`, lines 53–99):
```dart
53:   static double parseFaceValue(String rawDenom, {int qty = 1}) {
54:     final count = qty > 0 ? qty : 1;
55:     if (rawDenom.trim().isEmpty) return 0.0;
56: 
57:     // Normalization pipeline: lowercase, collapse whitespace, strip parenthetical & ellipses
58:     String s = rawDenom.toLowerCase().trim();
59:     s = s.replaceAll(RegExp(r'\(.*?\)'), '').trim();
60:     s = s.replaceAll(RegExp(r'\.{2,}'), '').trim();
61: 
62:     double value = 0.0;
63: 
64:     // 1. High Gold & Commemoratives
65:     if (s.contains(r'$500') || s.contains('five hundred dollar')) { value = 500.00; }
66:     else if (s.contains(r'$100') || s.contains('one hundred dollar') || s.contains('hundred dollar')) { value = 100.00; }
67:     else if (s.contains(r'$50') || s.contains('fifty dollar')) { value = 50.00; }
68:     else if (s.contains(r'$25') || s.contains('twenty five dollar') || s.contains('twenty-five dollar')) { value = 25.00; }
69:     else if (s.contains(r'$20') || s.contains('twenty dollar') || s.contains('double eagle')) { value = 20.00; }
70:     else if (s.contains(r'$10') || s.contains('ten dollar') || (s.contains('eagle') && !s.contains('half') && !s.contains('quarter') && !s.contains('silver'))) { value = 10.00; }
71:     else if (s.contains(r'$5') || s.contains('five dollar') || s.contains('half eagle')) { value = 5.00; }
72:     else if (s.contains(r'$3') || s.contains('three dollar')) { value = 3.00; }
73:     else if (s.contains(r'$2.50') || s.contains(r'$2.5') || s.contains('quarter eagle') || s.contains('two and a half')) { value = 2.50; }
74:     else if (s.contains(r'$2') || s.contains('two dollar')) { value = 2.00; }
75: 
76:     // 2. Sub-Dollar & Standard Silver/Base Denominations
77:     else if (s.contains('half dollar') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
78:     else if (s.contains('quarter dollar') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
79:     else if (s.contains('twenty cent') || s.contains('20c')) { value = 0.20; }
80:     else if (s.contains('dime') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
81:     else if (s.contains('half dime')) { value = 0.05; }
82:     else if (s.contains('nickel') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
83:     else if (s.contains('three cent') || s.contains('3c')) { value = 0.03; }
84:     else if (s.contains('two cent') || s.contains('2c')) { value = 0.02; }
85:     else if (s.contains('half cent')) { value = 0.005; }
86:     else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
87:     else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }
88: 
89:     // 3. Fallback: plain numeric parse
90:     else {
91:       final match = RegExp(r'\d+(?:\.\d+)?').firstMatch(s);
92:       if (match != null) {
93:         final parsed = double.tryParse(match.group(0)!) ?? 0.0;
94:         value = parsed <= 1000.0 ? parsed : 0.0;
95:       }
96:     }
97: 
98:     return value * count;
99:   }
```

#### Planned Unified Diff (`numista_mobile/lib/services/melt_value_service.dart`, Hunk Header `@@ -58,31 +58,62 @@` Verified `git apply`-Clean):
```diff
--- a/numista_mobile/lib/services/melt_value_service.dart
+++ b/numista_mobile/lib/services/melt_value_service.dart
@@ -58,31 +58,62 @@ class MeltValueService {
     String s = rawDenom.toLowerCase().trim();
     s = s.replaceAll(RegExp(r'\(.*?\)'), '').trim();
     s = s.replaceAll(RegExp(r'\.{2,}'), '').trim();
+    s = s.replaceAll('\u00bd', ' 1/2');
+    s = s.replaceAll(RegExp(r'\s+'), ' ').trim();
+
+    // Guard non-legal-tender blanks (planchets), non-USD units (candareens),
+    // and multi-denomination sets/ranges ('$100/$50/$25/$10', '$1, $2, $5, $10', '3c-50c')
+    if (s.contains('planchet') ||
+        s.contains('candareen') ||
+        RegExp(r'\$\d[\d,]*(?:\.\d+)?\s*(?:/\s*\$?|,\s*\$)\s*\d').hasMatch(s) ||
+        RegExp(r'\d\s*(?:\u00a2|c|cents?)?\s*[\u2013\-]\s*\d').hasMatch(s)) {
+      return 0.0;
+    }
 
     double value = 0.0;
 
-    // 1. High Gold & Commemoratives
-    if (s.contains(r'$500') || s.contains('five hundred dollar')) { value = 500.00; }
+    // 0. Leading numeric & fractional patterns (N Dollars, 1,000 Dollars, 10,000 Dollars, 2 1/2 Dollars, G$2 1/2, 3 cents, $1000)
+    final fracDollarMatch = RegExp(r'^(?:g?\$)?\s*(\d+)\s+1/2(?:\s*dollars?)?$').firstMatch(s);
+    final leadDollarMatch = RegExp(r'^\$?\s*(\d[\d,]*(?:\.\d+)?)\s*(?:dollars?|\$)$').firstMatch(s);
+    final leadCentMatch = RegExp(r'^(\d+(?:\.\d+)?)\s*(?:cents?|c|\u00a2)\b').firstMatch(s);
+    final leadSymDollarMatch = RegExp(r'^\$\s*(\d[\d,]*(?:\.\d+)?)(?:\b|$)').firstMatch(s);
+
+    if (fracDollarMatch != null) {
+      value = (double.tryParse(fracDollarMatch.group(1)!) ?? 0.0) + 0.5;
+    } else if (leadDollarMatch != null) {
+      value = double.tryParse(leadDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
+    } else if (leadCentMatch != null) {
+      value = (double.tryParse(leadCentMatch.group(1)!) ?? 0.0) / 100.0;
+    } else if (leadSymDollarMatch != null) {
+      value = double.tryParse(leadSymDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
+    }
+
+    // 1. High Gold, Notes & Commemoratives
+    else if (s.contains(r'$10,000') || s.contains(r'$10000') || s.contains('ten thousand dollar')) { value = 10000.00; }
+    else if (s.contains(r'$1,000') || s.contains(r'$1000') || s.contains('one thousand dollar') || s.contains('thousand dollar')) { value = 1000.00; }
+    else if (s.contains(r'$500') || s.contains('five hundred dollar')) { value = 500.00; }
     else if (s.contains(r'$100') || s.contains('one hundred dollar') || s.contains('hundred dollar')) { value = 100.00; }
     else if (s.contains(r'$50') || s.contains('fifty dollar')) { value = 50.00; }
+    else if (s.contains(r'$40') || s.contains('forty dollar')) { value = 40.00; }
     else if (s.contains(r'$25') || s.contains('twenty five dollar') || s.contains('twenty-five dollar')) { value = 25.00; }
     else if (s.contains(r'$20') || s.contains('twenty dollar') || s.contains('double eagle')) { value = 20.00; }
     else if (s.contains(r'$10') || s.contains('ten dollar') || (s.contains('eagle') && !s.contains('half') && !s.contains('quarter') && !s.contains('silver'))) { value = 10.00; }
     else if (s.contains(r'$5') || s.contains('five dollar') || s.contains('half eagle')) { value = 5.00; }
+    else if (s.contains(r'$4') || s.contains('four dollar') || s.contains('stella')) { value = 4.00; }
     else if (s.contains(r'$3') || s.contains('three dollar')) { value = 3.00; }
-    else if (s.contains(r'$2.50') || s.contains(r'$2.5') || s.contains('quarter eagle') || s.contains('two and a half')) { value = 2.50; }
+    else if (s.contains(r'$2.50') || s.contains(r'$2.5') || s.contains('2 1/2') || s.contains('quarter eagle') || s.contains('two and a half')) { value = 2.50; }
     else if (s.contains(r'$2') || s.contains('two dollar')) { value = 2.00; }
 
-    // 2. Sub-Dollar & Standard Silver/Base Denominations
-    else if (s.contains('half dollar') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
-    else if (s.contains('quarter dollar') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
-    else if (s.contains('twenty cent') || s.contains('20c')) { value = 0.20; }
-    else if (s.contains('dime') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
-    else if (s.contains('half dime')) { value = 0.05; }
-    else if (s.contains('nickel') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
-    else if (s.contains('three cent') || s.contains('3c')) { value = 0.03; }
-    else if (s.contains('two cent') || s.contains('2c')) { value = 0.02; }
-    else if (s.contains('half cent')) { value = 0.005; }
+    // 2. Sub-Dollar & Standard Silver/Base Denominations (multi-word terms before single tokens)
+    else if (s.contains('half dollar') || s.contains('fifty cent') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
+    else if (s.contains('quarter dollar') || s.contains('twenty-five cent') || s.contains('twenty five cent') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
+    else if (s.contains('twenty cent') || s.contains('20c') || s.contains('20 cent')) { value = 0.20; }
+    else if (s.contains('half dime') || s.contains('half-dime')) { value = 0.05; }
+    else if (s.contains('dime') || s.contains('ten cent') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
+    else if (s.contains('three cent') || s.contains('3 cent') || s.contains('3c')) { value = 0.03; }
+    else if (s.contains('nickel') || s.contains('five cent') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
+    else if (s.contains('two cent') || s.contains('2 cent') || s.contains('2c')) { value = 0.02; }
+    else if (s.contains('half cent') || s.contains('half-cent')) { value = 0.005; }
     else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
     else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }
```

---

### D. Caller Blast-Radius Audit Across the Repository (`RADIO_NET-837` #4)

`MeltValueService.parseFaceValue` (`numista_mobile/lib/services/melt_value_service.dart:53`) is a shared static parser. A read-only `git grep -n "parseFaceValue"` across `b0b05808` (`dev`) and `origin/p7-v8.9` confirms **5 production call sites** (identical line numbers on both branches):

| # | File & Line (`b0b05808` & `origin/p7-v8.9`) | Verbatim Code Line(s) | Purpose & Blast-Radius Impact of `v2.1` Patch |
|---:|---|---|---|
| 1 | `numista_mobile/lib/screens/home_dashboard.dart:299-301` (called at `:415`, `:440`, `:472`) | `299:   static double _computeFaceValue(String denom) {`<br>`300:     return MeltValueService.parseFaceValue(denom);`<br>`301:   }`<br>`415:               faceValue       += _computeFaceValue(data['Denomination']?.toString() ?? '');`<br>`440:               faceValue       += _computeFaceValue(data['Denomination']?.toString() ?? '');`<br>`472:               faceValue += _computeFaceValue(data['denomination']?.toString() ?? '');` | Computes the user's Dashboard `'Face Value'` metric card (`:746`, `:760`). **Existing user dashboard face-value totals will change** (moving from mis-parsed values to accurate legal-tender sums; see table below). |
| 2 | `numista_mobile/lib/widgets/header_stats_bar.dart:106-109` (blob `4e1ba9b3f8`) | `106:       final denom = m['Denomination']?.toString() ?? m['denomination']?.toString() ?? '';`<br>`107:       if (!isForeign) {`<br>`108:         usdFaceSum += MeltValueService.parseFaceValue(denom, qty: qty);`<br>`109:       }` | Computes `usdFaceSum` in the top `HeaderStatsBar` across all items in the user's collection (including the largest user account). **Existing user header face-value totals will change** whenever the collection contains canonical or numeric-prefix denomination strings listed below. |
| 3 | `numista_mobile/lib/services/melt_value_service.dart:140-144` (blob `b210bff669`) | `140:       if (combined.contains('91.67') || combined.contains('gold eagle')) {`<br>`141:         final fv = parseFaceValue(denom);`<br>`142:         final oz = _au9167ByFaceValue[fv] ?? 1.0;`<br>`143:         return au * oz * count;`<br>`144:       }` | Maps `.9167` American Gold Eagle denominations to `_au9167ByFaceValue` (`{5.0: 0.10, 10.0: 0.25, 25.0: 0.50, 50.0: 1.00}`). Previously, `'5 Dollars'`, `'10 Dollars'`, `'25 Dollars (1/2 oz)'`, and `'50 Dollars'` returned `fv = 1.0` (falling back to `1.0 oz` instead of `0.10`, `0.25`, `0.50`, `1.00` oz). Now resolves exact troy oz. |
| 4 | `numista_mobile/lib/services/melt_value_service.dart:145-149` (blob `b210bff669`) | `145:       if (combined.contains('90%') || combined.contains('half eagle') || combined.contains('indian head gold') || combined.contains('pre-1933') || combined.contains('saint-gaudens') || combined.contains('liberty head')) {`<br>`146:         final fv = parseFaceValue(denom);`<br>`147:         final oz = _au90ByFaceValue[fv] ?? 0.24188;`<br>`148:         return au * oz * count;`<br>`149:       }` | Maps 90% pre-1933 U.S. gold to `_au90ByFaceValue` (`{1.0: 0.04837, 2.5: 0.12094, 3.0: 0.14513, 5.0: 0.24188, 10.0: 0.48375, 20.0: 0.96750}`). Previously, `'2 1/2 Dollars'` (`1.0`), `'G$2½'` (`2.0`), `'5 Dollars'` (`1.0`), and `'20 Dollars'` (`1.0`) missed their table keys and defaulted to `0.24188 oz` ($5 Half Eagle). Now resolves exact troy oz (`0.12094`, `0.24188`, `0.96750`). |
| 5 | `numista_mobile/lib/services/melt_value_service.dart:199-207` (blob `b210bff669`) | `199:   static double? _matchDenom(Map<String, double> table, String rawDenom) {`<br>`200:     final fv = parseFaceValue(rawDenom);`<br>`201:     if (fv == 1.00 && table.containsKey('dollar')) return table['dollar'];`<br>`202:     if (fv == 0.50 && table.containsKey('half')) return table['half'];`<br>`203:     if (fv == 0.25 && table.containsKey('quarter')) return table['quarter'];`<br>`204:     if (fv == 0.10 && table.containsKey('dime')) return table['dime'];`<br>`205:     if (fv == 0.05 && table.containsKey('nickel')) return table['nickel'];`<br>`206:     return null;`<br>`207:   }` | Maps 90%, 40%, and 35% silver coins to `_ag90`, `_ag40`, `_ag35`. Previously, `'Fifty Cents'` (`0.01`), `'Twenty-Five Cents'` (`0.01`), and `'Ten Cents'` (`0.01`) returned `null` and fell back to `0.77344 oz` (Morgan/Peace dollar weight!). Now resolves exact silver weights (`0.36169`, `0.18084`, `0.07234` oz). |

#### Concrete User Collection Face-Total Movement Examples (`header_stats_bar.dart:108` & `home_dashboard.dart:300`)

| Collection `Denomination` String | Pinned `parseFaceValue` | Patched `v2.1` `parseFaceValue` | Net Delta per Coin (`qty = 1`) | Reason for Movement |
|---|---:|---:|---:|---|
| `'Five Cents'` | `$0.01` | **`$0.05`** | `+$0.04` | `'five cent'` added before generic `'cent'` |
| `'Ten Cents'` / `'Ten Cent'` | `$0.01` | **`$0.10`** | `+$0.09` | `'ten cent'` added before generic `'cent'` |
| `'Twenty-Five Cents'` | `$0.01` | **`$0.25`** | `+$0.24` | `'twenty-five cent'` added before generic `'cent'` |
| `'Fifty Cents'` | `$0.01` | **`$0.50`** | `+$0.49` | `'fifty cent'` added before generic `'cent'` |
| `'2 Cent'` / `'2 Cents'` | `$0.01` | **`$0.02`** | `+$0.01` | Leading numeric cent & `'2 cent'` before `'cent'` |
| `'3 Cents'` / `'3 cents'` | `$0.01` | **`$0.03`** | `+$0.02` | Leading numeric cent & `'3 cent'` before `'cent'` |
| `'Three Cent Nickel'` | `$0.05` | **`$0.03`** | `-$0.02` | `'three cent'` evaluated before `'nickel'` |
| `'Half Dime'` / `'Half dime'` | `$0.10` | **`$0.05`** | `-$0.05` | `'half dime'` evaluated before `'dime'` |
| `'5 Dollar'` / `'5 Dollars'` | `$1.00` | **`$5.00`** | `+$4.00` | Leading numeric dollar before `'dollar'` |
| `'25 Dollars (1/2 oz)'` | `$1.00` | **`$25.00`** | `+$24.00` | Parenthetical stripped → `'25 dollars'` → `25.00` |
| `'G$2½'` / `'2 1/2 Dollars'` | `$2.00` / `$1.00` | **`$2.50`** | `+$0.50` / `+$1.50` | `\u00bd` normalized to `' 1/2'`, `fracDollarMatch` |

---

## 5. Must-Fix #2 (`RADIO_NET-831` #2) & `RADIO_NET-837` #6–#7: Minimal Diff to `_CatalogCard` (`numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`)

### A. Pinned Code Verification (`b0b05808` / Prerequisite Commit 1 on `p7-v8.9`, blob `3a0d310936a1715034e65c7384476c19e2030ad7`)

#### Pinned Lines 1–7 (`numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:1-7`):
```dart
1: import 'dart:convert';
2: import 'package:flutter/material.dart';
3: import 'package:flutter/services.dart';
4: import 'package:url_launcher/url_launcher.dart';
5: 
6: class CatalogBrowseScreen extends StatefulWidget {
7:   final String? initialQuery;
```

#### Pinned Lines 1080–1154 (`numista_mobile/lib/screens/catalog/catalog_browse_screen.dart:1080-1154`):
```dart
1080:     final primaryImg = item['primary_image'] as Map?;
1081:     final typeImg = item['type_image'] as Map?;
1082:     final imgMap = primaryImg ?? typeImg;
1083:     final isTypeImage = primaryImg == null && typeImg != null;
1084: 
1085:     final badge = item['status_badge'] as String?;
1086:     final year = item['year']?.toString() ?? 'Undated';
1087:     final denom = item['denomination']?.toString() ?? '';
1088: 
1089:     return InkWell(
1090:       onTap: onTap,
1091:       borderRadius: BorderRadius.circular(12),
1092:       child: Container(
1093:         padding: const EdgeInsets.all(16),
1094:         decoration: BoxDecoration(
1095:           color: Colors.white,
1096:           border: Border.all(color: const Color(0xFFD6D6D6), width: 2),
1097:           borderRadius: BorderRadius.circular(12),
1098:         ),
1099:         child: Column(
1100:           crossAxisAlignment: CrossAxisAlignment.start,
1101:           children: [
1102:             // Image
1103:             Expanded(
1104:               child: Center(
1105:                 child: imgMap != null && imgMap['url'] != null
1106:                     ? Image.network(
1107:                         imgMap['url'] as String,
1108:                         fit: BoxFit.contain,
1109:                         errorBuilder: (c, e, s) => _buildPlaceholder(),
1110:                       )
1111:                     : _buildPlaceholder(),
1112:               ),
1113:             ),
1114:             const SizedBox(height: 10),
1115: 
1116:             // Badge
1117:             if (badge != null) ...[
1118:               _CatalogBadge(badgeText: badge),
1119:               const SizedBox(height: 8),
1120:             ],
1121: 
1122:             // Title
1123:             Text(
1124:               item['name'] as String? ?? 'Coin',
1125:               maxLines: 2,
1126:               overflow: TextOverflow.ellipsis,
1127:               style: const TextStyle(
1128:                 fontSize: 18,
1129:                 fontWeight: FontWeight.bold,
1130:                 color: Color(0xFF0B2545),
1131:                 height: 1.2,
1132:               ),
1133:             ),
1134:             const SizedBox(height: 6),
1135: 
1136:             // Metadata line
1137:             Text(
1138:               [year, denom].where((s) => s.isNotEmpty).join(' · '),
1139:               style: const TextStyle(fontSize: 15, color: Color(0xFF475569)),
1140:             ),
1141: 
1142:             if (isTypeImage)
1143:               const Padding(
1144:                 padding: EdgeInsets.only(top: 4),
1145:                 child: Text(
1146:                   'type photo (date may differ)',
1147:                   style: TextStyle(fontSize: 12, color: Color(0xFF6B6B6B), fontStyle: FontStyle.italic),
1148:                 ),
1149:               ),
1150:           ],
1151:         ),
1152:       ),
1153:     );
1154:   }
```

### B. Planned Minimal Unified Diff (`numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`, Verified `git apply --check` Exit `0`)

```diff
--- a/numista_mobile/lib/screens/catalog/catalog_browse_screen.dart
+++ b/numista_mobile/lib/screens/catalog/catalog_browse_screen.dart
@@ -2,6 +2,7 @@ import 'dart:convert';
 import 'package:flutter/material.dart';
 import 'package:flutter/services.dart';
 import 'package:url_launcher/url_launcher.dart';
+import '../../services/melt_value_service.dart';
 
 class CatalogBrowseScreen extends StatefulWidget {
   final String? initialQuery;
@@ -1085,6 +1086,13 @@ class _CatalogCard extends StatelessWidget {
     final badge = item['status_badge'] as String?;
     final year = item['year']?.toString() ?? 'Undated';
     final denom = item['denomination']?.toString() ?? '';
+    final isMedal = item['type'] == 'medal';
+    final faceVal = isMedal ? 0.0 : MeltValueService.parseFaceValue(denom);
+    final faceValText = faceVal > 0
+        ? (faceVal == 0.005 ? r'$0.005' : '\$${faceVal.toStringAsFixed(2)}')
+        : '\u2014';
+    final rawAiEst = (item['AI Estimated Value'] ?? item['ai_estimated_value'])?.toString().trim() ?? '';
+    final hasAiEst = rawAiEst.isNotEmpty && rawAiEst != 'Pending';
 
     return InkWell(
       onTap: onTap,
@@ -1147,6 +1155,46 @@ class _CatalogCard extends StatelessWidget {
                   style: TextStyle(fontSize: 12, color: Color(0xFF6B6B6B), fontStyle: FontStyle.italic),
                 ),
               ),
+
+            const SizedBox(height: 6),
+            if (isMedal)
+              const Text(
+                'No face value',
+                style: TextStyle(fontSize: 13, color: Color(0xFF6B6B6B)),
+              )
+            else
+              Row(
+                children: [
+                  Text(
+                    faceValText,
+                    style: const TextStyle(
+                      fontSize: 15,
+                      fontWeight: FontWeight.bold,
+                      color: Color(0xFF1F5FAD),
+                    ),
+                  ),
+                  const SizedBox(width: 8),
+                  Flexible(
+                    child: Container(
+                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
+                      decoration: BoxDecoration(
+                        color: const Color(0xFFFFF3CD),
+                        border: Border.all(color: const Color(0xFFFFEEBA)),
+                        borderRadius: BorderRadius.circular(4),
+                      ),
+                      child: Text(
+                        hasAiEst ? 'AI Est: $rawAiEst' : 'Face value \u00b7 No retail estimate',
+                        overflow: TextOverflow.ellipsis,
+                        style: const TextStyle(
+                          fontSize: 11,
+                          fontWeight: FontWeight.w600,
+                          color: Color(0xFF856404),
+                        ),
+                      ),
+                    ),
+                  ),
+                ],
+              ),
           ],
         ),
       ),
```

---

## 6. Planned Tests (Not Run) in New Test File (`numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`)

- **Existing Test Preserved:** `numista_mobile/test/catalog_browse_test.dart` (91 lines, blob `3df197ca2cc0424b5dac7f1ad491a5ca9bb669af`) is ported in Prerequisite Commit 1 and preserved untouched.
- **No Duplicate `const` Map Keys (`RADIO_NET-837` #2):** `expectedCatalogDenomValues` contains the exact **66 unique non-null `denomination` strings** (`r'$50'` appears once; asserted `expectedCatalogDenomValues.length == 66`). In addition, `expectedByTypeAndDenom` keys all **71 `(type, denomination)` pairs** by `'type|denomination'`, asserting `expectedByTypeAndDenom.length == 71`.
- **GridView-Scoped Widget Finders (`RADIO_NET-837` #3):** Because `CatalogBrowseScreen(initialQuery: ...)` populates `_searchController.text = widget.initialQuery!` (`catalog_browse_screen.dart:44`, rendered in the search `TextField` at `:505–506`), card assertions use `find.descendant(of: find.byType(GridView), matching: ...)` so the search `EditableText` never double-matches.
- **Caller Blast-Radius Regression Tests (`RADIO_NET-837` #4):** Includes dedicated regression tests for `header_stats_bar.dart:108` `qty`-weighted `usdFaceSum` accumulation, `home_dashboard.dart:300` `_computeFaceValue` inputs, and `MeltValueService.compute` gold/silver lookups (`melt_value_service.dart:141, 146, 200`).

### Planned Contents of `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`

```dart
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_ai/services/melt_value_service.dart';

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
  });

  group('NET-816 Chunk 1 — _CatalogCard Widget Tests (#2 & NET-837 #3/#6)', () {
    testWidgets('shows "type photo (date may differ)" when isTypeImage is true and renders parsed face value + honest non-promissory chip', (WidgetTester tester) async {
      await tester.binding.setSurfaceSize(const Size(1440, 960));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      // 1842 Liberty Seated dollar in catalog_public_v1.json has primary_image: null, type_image != null, denomination: "Dollar"
      await tester.pumpWidget(
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
      await tester.binding.setSurfaceSize(const Size(1440, 960));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
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
```

---

## 7. History-Preserving Landing, Rollback & Docs Sync Procedure (`RADIO_NET-837` #1)

1. **Future Two-Commit Code Landing on `p7-v8.9` Only (After GB CoS ≥95, SAG ≥95, and Eric's Typed `YES`):**
   - **Prerequisite Commit 1 (`<prereq_port_sha>`):** Ports the 12 catalog baseline files from `b0b058087f1492244a0c0b769e126b38ac1ba06c` (§3.A) and applies the `pubspec.yaml` (§3.B) and `main.dart` (§3.C) hunks on `p7-v8.9`.
   - **Commit 2 (`<chunk1_patch_sha>`):** Applies the `MeltValueService.parseFaceValue` diff (§4.C), the `_CatalogCard` minimal diff (§5.B), and adds `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart` (§6) on `p7-v8.9`.
2. **History-Preserving Rollback on `p7-v8.9` (No `reset`, No `checkout <old_sha>`, No Force Push):**
   - To revert only the Chunk 1 patch while keeping the Catalog baseline port on `p7-v8.9`:
     ```bash
     git revert --no-edit <chunk1_patch_sha>
     git push origin p7-v8.9
     ```
   - To revert both the Chunk 1 patch and the Prerequisite Catalog port in reverse topological order:
     ```bash
     git revert --no-edit <chunk1_patch_sha> <prereq_port_sha>
     git push origin p7-v8.9
     ```
   - `origin/main` remains locked at `9f04550a` (`9f04550a45fa4da082ba8948c2d89a521a90fa45`).
3. **Docs Sync to `origin/dev` via Temporary Worktree + `git checkout <sha> -- <paths>` (No `cherry-pick -- <paths>`, No Force):**
   ```powershell
   git fetch origin dev
   git worktree add ..\temp-dev-chunk1-v21 origin/dev
   Push-Location ..\temp-dev-chunk1-v21
   git checkout <p7_doc_commit_sha> -- `
     "docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.1.md" `
     "BETA TEST/Grok Bot/8 OCT 26/BATONS/ACK_RADIO_NET-837_REVISE-816-CHUNK1-v2.1_20261107.md" `
     "BETA TEST/Grok Bot/8 OCT 26/BATONS/DONE_BATON_NET-816_REVISE_CATALOG_CHUNK1_v2.1_TO-WRITER-9bbe20e4_ATTEMPT2_PER-COS-68_20261107.md" `
     "BETA TEST/Grok Bot/8 OCT 26/BATONS/BATON_NET-816_GROKCOS_REVIEW_CATALOG_CHUNK1_v2.1_20261107-1608.md"
   git rm -f --ignore-unmatch "BETA TEST/Grok Bot/8 OCT 26/BATONS/BATON_NET-816_REVISE_CATALOG_CHUNK1_v2.1_TO-WRITER-9bbe20e4_ATTEMPT2_PER-COS-68_20261107.md"
   git add -A "docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.1.md" "BETA TEST/Grok Bot/8 OCT 26/BATONS/"
   git commit -m "docs(net-816): deliver Catalog Chunk 1 failfix plan v2.1 and review baton (attempt 2/4)"
   git push origin HEAD:refs/heads/dev
   Pop-Location
   Remove-Item -Recurse -Force ..\temp-dev-chunk1-v21 -ErrorAction SilentlyContinue
   git worktree prune
   ```
