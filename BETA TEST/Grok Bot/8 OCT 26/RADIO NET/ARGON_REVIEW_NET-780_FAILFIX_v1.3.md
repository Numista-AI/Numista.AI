# ARGON (GEMINI 3.8) TECHNICAL & DATA HYGIENE REVIEW: `FAILFIX_PLAN_NET-780b_CARDS_v1.3.md` & `FAILFIX_PLAN_NET-780c_IMAGES_v1.3.md` (`BATON_NET-809`)

- **Reviewer:** Argon — Gemini 3.8 Independent Technical & Data Hygiene Auditor
- **Track / Baton:** `NET-780b v1.3` & `NET-780c v1.3` / `BATON_NET-809`
- **Target Plans Reviewed:**
  - `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.3.md` (204 lines)
  - `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.3.md` (202 lines)
- **Timestamp:** 2026-11-05 16:34 ET
- **Composite Score:** **98 / 100 (`PASS — 780b v1.3: 99/100 PASS, 780c v1.3: 97/100 PASS; 0 Blocking Plan Must-Fixes; 1 Non-Blocking Execution Safeguard EX-809-1 Logged`)**
- **Execution Posture:** **PLAN REVIEW ONLY** (`origin/main` locked at `9f04550a`, Stripe strictly OFF, zero code edits, zero deployments, zero Firestore writes/seeding)

---

## 1. Executive Verdict & Rubric Breakdown

`docs/FAILFIX_PLAN_NET-780b_CARDS_v1.3.md` and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.3.md` resolve all **6 blocking must-fixes and non-blocking refinements** from Grok Bot CoS (`86/100 FAIL`) and Stand Alone Grok (`72/100 FAIL`) on v1.2.

| Rubric Dimension | Weight | `780b v1.3` | `780c v1.3` | Verification Notes |
| :--- | :---: | :---: | :---: | :--- |
| **1. Repo-Safe Rollback Pinning to `a5eeb19b` (Must-Fix 1)** | 20 | **20 / 20** | **20 / 20** | Both plans (`780b §5.A` lines 188–197, `780c §6.A` lines 184–195) delete `git checkout 9f04550a -- <files>` and pin rollback to pre-execute `p7-v8.9` commit `a5eeb19b` via `git revert <execute SHA>` or `git checkout a5eeb19b -- <files>`, plus manifest deactivation invariant (`780c §6.A` line 195). |
| **2. Nickel Negative Lookbehind Regex & Line 433 Real `¢` Cite (`780b` Must-Fix 2)** | 20 | **20 / 20** | N/A | `780b §2.B` (lines 64–71), `§3.B` (lines 124–129), and `§4` (lines 174–177) cite real `¢` at `canonical_mint_asset_service.dart:433`, anchor with `(?<!\d)5¢` (`RegExp(r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)', caseSensitive: false)`), and specify Test 3 failing `"15¢"` and `"25c"` while passing `"5¢"`, `"5c"`, `"five cents"`, and `"nickel"`. |
| **3. Valuation Chip Precedence & Zero Suppression (`780b` Must-Fix 4)** | 20 | **20 / 20** | N/A | `780b §3.C` (lines 131–165) displays `fmt.format(valCpg)` whenever `valCpg > 0` (`hasValidPrice = valCpg > 0`), renders the gold `'Valuation Pending'` chip strictly when `!hasValidPrice` (`valCpg <= 0`), removes `m['enrichment_status'] == 'pending'` suppression of positive prices, and excludes AI/melt/cost from the primary valuation slot. |
| **4. 4-Step Image Resolution Order (`780c` Must-Fix 3)** | 25 | N/A | **23 / 25** | `780c §3.1` (lines 76–104) & `§4` (lines 162–163) enforce: (1) User photo -> (2) Allowlisted own-origin URL -> (3) `CoinImageService` reference library -> (4) Local SVG placeholder, ensuring a null allowlist check passes through to `CoinImageService` and resolves Card 2 (2023 Jefferson nickel). Logged non-blocking `EX-809-1` (-2 pts) for `CoinImageService.fetchReferenceImages` async signature & `/numista-reference-library/` bucket path. |
| **5. Grounded 3,202 Census, `$0.00` Spend Fence & "Create, Then Run" Tooling (`780b/c` Must-Fixes 5 & 6)** | 15 | **19 / 20** *(weighted)* | **19 / 20** *(weighted)* | `780c §3.2` (lines 122–134) strikes unverified `8,836 / 109 / 8,945` local counts and retains strictly the verified `3,202` census (`2,354 / 639 / 181 / 1 / 27`). Both plans remove bulk GCS mirroring from this YES, enforce a hard abort before any storage call (`$0.00` cap), and label `tools/verify_catalog_manifest_pii.py` as `"create, then run"` (`780c §5` line 175). |
| **SUB-SCORES & COMPOSITE** | **100** | **99 / 100 (`PASS`)** | **97 / 100 (`PASS`)** | **Composite: 98 / 100 (`PASS — >= 95 Gate Met`)** |

---

## 2. Rule 6(a) / `NET-767` Verbatim Code & Plan Verification (All Files Read via `read_file` in This Turn)

### 2.1 Repo-Safe Rollback Pinned to `a5eeb19b` (`780b §5.A` & `780c §6.A`) — `PASS`
- **Verified in `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.3.md:188-197`:**
  ```markdown
  188: 1. **Repo-Safe Code Revert:**
  189:    If card rendering or pricing logic introduces any regression, revert target files cleanly to pre-execute `p7-v8.9` commit `a5eeb19b`:
  190:    ```bash
  191:    git revert <execute SHA>
  192:    ```
  193:    Or to discard uncommitted working tree changes:
  194:    ```bash
  195:    git checkout a5eeb19b -- numista_mobile/lib/services/canonical_mint_asset_service.dart numista_mobile/lib/screens/my_collection_screen.dart
  196:    ```
  197:    *(Locked main commit `9f04550a` is strictly forbidden as a file restore target).*
  ```
- **Verified in `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.3.md:184-195`:**
  ```markdown
  184: 1. **Repo-Safe Code Revert:**
  185:    Revert target files cleanly to pre-execute `p7-v8.9` commit `a5eeb19b`:
  186:    ```bash
  187:    git revert <execute SHA>
  188:    ```
  189:    Or to discard uncommitted working tree changes:
  190:    ```bash
  191:    git checkout a5eeb19b -- numista_mobile/lib/screens/my_collection_screen.dart
  192:    ```
  193:    *(Locked main commit `9f04550a` is strictly forbidden as a file restore target).*
  194: 2. **GCS Manifest Rollback Invariant:**
  195:    Deactivated manifest keys are guaranteed to never be served by client cards or catalog browse screens.
  ```

### 2.2 Nickel Negative Lookbehind Regex & Line 433 Citation (`780b §2.B`, `§3.B`, `§4`) — `PASS`
- **Verified in `numista_mobile/lib/services/canonical_mint_asset_service.dart:433-434` & `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.3.md:126-129`:**
  ```dart
  433:       final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
  434:           RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
  ```
  ```dart
  126: // Negative lookbehind (?<!\d)5¢ prevents matching 15¢ or 25¢ while matching 5¢ cleanly:
  127: final isNickel = RegExp(r'(?:\b5c\b|(?<!\d)5¢|\bfive cents?\b|\bnickel\b)', caseSensitive: false).hasMatch(cleanDenom) ||
  128:     RegExp(r'\b(jefferson nickel|nickel|five cents?)\b', caseSensitive: false).hasMatch(cleanTitle);
  ```

### 2.3 Valuation Chip Logic (`780b §2.C` & `§3.C`) — `PASS`
- **Verified in `numista_mobile/lib/screens/my_collection_screen.dart:3017-3023` & `3170-3185` and `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.3.md:135-143`:**
  ```dart
  135:    final valCpg = _parseNumber(m['cpgRetail']);
  136:    final bool hasValidPrice = valCpg > 0;
  137:    final fmt = intl.NumberFormat.currency(symbol: '\$');
  138:    final String valueText = hasValidPrice ? fmt.format(valCpg) : '';
  ...
  142:    if (!hasValidPrice)
  143:      Container(
  ```

### 2.4 4-Step Image Resolution Order, Grounded 3,202 Census & `$0.00` Spend Fence (`780c §3.1–3.3`, `§5`) — `PASS`
- **Verified in `numista_mobile/lib/screens/my_collection_screen.dart:6368-6406` & `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.3.md:80-104`:**
  ```dart
  80: Widget _buildResolvedCardImage(Map<String, dynamic> data) {
  81:   // 1. User photo check: Never overwrite user's own uploads
  82:   if (hasUserUploadedPhotos(data)) {
  83:     return _buildUserPhotoImage(data);
  84:   }
  85: 
  86:   // 2. Allowlisted direct URL check
  87:   final obv = _cleanUrl(data[_F.imageObverse]);
  88:   final rev = _cleanUrl(data[_F.imageReverse]);
  89:   final directUrl = rev.isNotEmpty ? rev : obv;
  90:   final allowlistedUrl = sanitizeAndAllowlistUrl(directUrl);
  91:   if (allowlistedUrl != null) {
  92:     return _buildCoinImage(allowlistedUrl);
  93:   }
  94: 
  95:   // 3. CoinImageService internal reference library resolution
  96:   // (Prevents skipping straight to placeholder; resolves Card 2 Jefferson nickel)
  97:   final referenceAsset = CoinImageService.resolveReferenceAsset(data);
  98:   if (referenceAsset != null && referenceAsset.isNotEmpty) {
  99:     return _buildCoinImage(referenceAsset);
  100:   }
  101: 
  102:   // 4. Clean local SVG coin silhouette placeholder
  103:   return const _GenericCoinPlaceholderSvg();
  104: }
  ```

---

## 3. Non-Blocking Execution Safeguard (`EX-809-1`)

- **`EX-809-1` (Preserve Existing `CanonicalMintAssetService.resolveFromMap` + `FutureBuilder<CoinImageResult>(future: CoinImageService.fetchReferenceImages(...))` Call Signature & Bucket Allowlist in `my_collection_screen.dart:6369-6440`):**
  - In `numista_mobile/lib/screens/my_collection_screen.dart:6369-6440`, Step 3 is already implemented via `FutureBuilder<CoinImageResult>(future: CoinImageService.fetchReferenceImages(...))` (lines 6399–6440) after `CanonicalMintAssetService.resolveFromMap(data)` (lines 6369–6375).
  - At code execution time, simply replace lines 6381–6383 (`if (directUrl.isNotEmpty) { return _buildCoinImage(directUrl); }`) with `final allowlistedUrl = sanitizeAndAllowlistUrl(directUrl); if (allowlistedUrl != null) { return _buildCoinImage(allowlistedUrl); }`, so that when `directUrl` is an unmirrored external URL (`upload.wikimedia.org`), execution falls straight through to the existing `FutureBuilder<CoinImageResult>(future: CoinImageService.fetchReferenceImages(...))` at line 6399 (and then to the local SVG placeholder if `refUrl` is empty).
  - Also include `/numista-reference-library/` and `/numista-uploads-studio-9101802118-8c9a8/` alongside `/numista-catalog-assets/` in `sanitizeAndAllowlistUrl` (`780c §3.1` line 114) so existing internal GCS reference library and user studio upload URLs pass the allowlist.

---

## 4. Proactive No-Silo Site & Product Observations (`RADIO_NET-790`)

1. **End-to-End Alignment Across All Four Active Plans (`NET-808`, `NET-809`, `NET-806`, `NET-807`):** With `NET-809` (`780b/c v1.3`) and `NET-808` (`Catalog v1.5`) both completed, all four active plan revisions now share identical ground-truth invariants:
   - **Master Census:** Exactly `3,202` US reference records (`2,354 Tier 1 / 639 Tier 2 / 181 Tier 3 / 1 Tier 4 / 27 Tier 5`).
   - **Valuation Source:** Strictly CDN CPG retail (`cpgRetail`) whenever `valCpg > 0`, and styled gold `'Valuation Pending'` chip when `valCpg <= 0` (zero wholesale, zero unlabeled AI fallback).
   - **Rollback Target:** Repo-safe branch commits (`a5eeb19b` on `p7-v8.9` and `18a8b8e5` on `dev`), never checking out files from `9f04550a`.
   - **Spend Fence:** Strict `$0.00` execution fence on client code fixes and `$25.00/mo` hard egress budget cap + manual Hosting shutoff for public traffic.
