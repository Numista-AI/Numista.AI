# FAILFIX PLAN NET-647 R2.8 (ROOT-CAUSE & ERIC WHOLE-ACCOUNT 100% PLAN)
**Document ID:** `FAILFIX_PLAN_NET-647_R2.8_20261031.md`  
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** Grok Desk, Grok CoS, Stand Alone Grok (SAG), Argon Reviewer, Field Tester, Founder (Eric)  
**Date:** 2026-10-31 20:20 ET  
**Status:** PLAN ONLY (Zero code edits, zero commits, zero deploys, zero GCS/Firestore writes)  
**Target Branch:** `p7-v8.9` ONLY | **Preview Channel:** `p7-gate` ONLY  
**Standing Locks:** `origin/main` locked at `9f04550a`; `origin/dev` catalog frozen at `9b55f3d9`; Stripe OFF  

---

## 1. Executive Summary & Review Gate Adherence

Per `WAKE_AG-COS-V4_NET-681D_AMEND_R2.8_ERIC-WHOLE-ACCOUNT_20261031-2005.md` and Founder Eric's directive (*"Get my account 100% right, then we can check the other accounts"*), this document establishes the comprehensive root-cause diagnosis and non-destructive resolution plan for both the NET-647 Mint intake pipeline and **Eric's entire collection** (252 items across `eric.seaman@yahoo.com` and `eric@numista.ai`).

### Standing Orders & Constraints
1. **Plan Only:** Strictly read-only analysis and architectural planning. Zero source code is modified, zero git commits are pushed, zero Firebase Hosting deploys are executed, and zero GCS or Firestore mutations are performed during this step.
2. **Review Cycle Gate:** Execution on `p7-v8.9` will proceed **only** after completing the mandatory cycle:
   $$\text{Argon Review} \longrightarrow \text{Grok CoS Score } \ge 95 \longrightarrow \text{SAG Review} \longrightarrow \text{Eric Typed YES} \longrightarrow \text{Execution}$$
3. **Firestore Safety Rule:** Any write to Eric's real account requires Eric's **separate typed YES**. Client-side read-time architecture guarantees 100% display correctness for existing docs without requiring backfill writes.
4. **Acceptance Gate:** Field Tester PASS on Eric's own account at 100%, zero wrong items.

---

## 2. Root Cause Analysis: Diagnostic Questions Q1–Q5

### Q1: Are the test rows legacy `review_queue` docs that the dry-run-only backfill never touched?
* **Finding:** **YES, 100% PROVEN BY FIRESTORE DATA.**
* **Technical Evidence:**
  In `users/grokbot@numista.ai/review_queue`:
  - Doc `2966ce1eaf40ac716725bf6bf66b9a1a4f351464` (`26XE` Morgan EU $\times 2$):
    `Quantity: 2`, `Cost: 169.0`, `Purchase Cost: 169.0`. Fields `unit_cost_cents`, `unit_cost`, and `line_total` are **NULL**.
  - Doc `8f17074059672d86400533062c2b3e70caa0b811` (`26GC` American Innovation $\times 2$):
    `Quantity: 2`, `Cost: 64.97`, `Purchase Cost: 64.97`. Fields `unit_cost_cents`, `unit_cost`, and `line_total` are **NULL**.
  - In `numista_mobile/lib/screens/review_hub_screen.dart:2045-2058`:
    ```dart
    final rawCost = (item['unit_cost_cents'] != null)
        ? (item['unit_cost_cents'] as num).toDouble() / 100.0
        : (item['unit_cost'] != null)
            ? (item['unit_cost'] as num).toDouble()
            : (item['Purchase Cost'] as num?)?.toDouble() ??
                (item['Cost'] as num?)?.toDouble();
    ...
    if (cleanQty > 1) {
      costStr = '\$${formatCurrency(rawCost)} each';
    ```
    Because `unit_cost_cents` and `unit_cost` are null, `rawCost` fell back to `Purchase Cost` ($169.00 and $64.97, which were the line totals for 2 coins). Because `cleanQty == 2`, line 2053 formatted this as `"$169.00 each"` and `"$64.97 each"`.
  - The backfill script was executed strictly with `--dry-run` (0 Firestore writes) because `--apply` is held pending Eric's typed YES. Furthermore, the dry-run targeted `eric.seaman@yahoo.com`, while Field Tester logged in as `grokbot@numista.ai`.
* **Root-Cause Fix for R2.8:**
  1. **Client-Side Read-Time Fallback (Instant, 0 Firestore writes):**
     In `review_hub_screen.dart`, when `item['unit_cost_cents']` and `item['unit_cost']` are null, and `cleanQty > 1`, compute read-time unit cost:
     $$\text{unitCost} = \frac{\text{rawLineCost}}{\text{cleanQty}}$$
     This displays `$84.50 each` for Morgan Enhanced and `$32.49 each` for American Innovation immediately upon loading, regardless of whether stored Firestore docs have been backfilled.
  2. **Database Backfill:** Run `backfill_review_mint_pricing.py` with `--apply` targeting both `grokbot@numista.ai` and `eric.seaman@yahoo.com` upon Eric's typed YES.

---

### Q2: Why do the cards resolve to the placeholder?
* **Finding:** The cards never even attempted to load GCS images because the stored Firestore review documents have **NULL/missing image URL fields**.
* **Technical Evidence:**
  - Querying `users/grokbot@numista.ai/review_queue` docs `05797eb2f5facb7058f9461d087c3a374bd41399` (`26EA`) and `e5904abd1a1a285c90a3486f10a6000a50412546` (`26XL`):
    `image_url_obverse: None`, `image_url: None`, `obverse_url: None`.
  - In `numista_mobile/lib/screens/review_hub_screen.dart:2190-2218`:
    ```dart
    final rawUrl = (data['image_url_obverse'] ?? data['image_url'] ?? ... ?? '').toString().trim();
    if (rawUrl.isEmpty) {
      return const Center(child: Icon(Icons.monetization_on_outlined, size: 28, color: Color(0xFFC9A227)));
    }
    ```
    When `rawUrl` evaluates to `""`, the client immediately renders the gold "$" icon without making any network request.
  - GCS public access is confirmed working (HTTP 200, `Access-Control-Allow-Origin: *`).
* **Root-Cause Fix for R2.8:**
  1. **Client-Side Catalog Lookup Fallback:**
     In `_buildCoinThumbnail(Map<String, dynamic> data)` in `review_hub_screen.dart`: if `rawUrl.isEmpty`, look up `data['retailer_item_num']` or `data['item_number']` in a client catalog map of canonical official US Mint asset URLs (`26SQRP`, `26XL`, `26XM`, `26EA`, `26XE`, `26XH`, `26XF`, `26RG`, `26RJ`, `26GC`). If a match is found, load the official GCS image directly.
  2. **Backend Intake Auto-Enrichment:**
     In `numista_backend/services/invoice_import_service.py`, ensure line items automatically inherit `image_url_obverse` and `image_url_reverse` from the US Mint reference library upon ingestion.

---

### Q3: Which 2 cards are missing, and why?
* **Finding:** The missing items were never present in grokbot's intake session files.
* **Technical Evidence:**
  - The canonical 11-item order planned for 2026 products comprises:
    `26SQRP`, `26XL`, `26XM`, `26EA`, `26XE`, `26XH`, `26XF`, `26RG`, `26RJ`, `26GC`, `2026-AI-IA`.
  - In `users/grokbot@numista.ai/review_queue`, the session import `sess_1793463570760_jvfysz` generated exactly 6 items: `23RH` (2023 Silver Proof Set), `26EA`, `26XE`, `26SQRP`, `26GC`, `26XL`.
  - Combined with existing review queue items `1c68b2fd` (`26RJ`), `91f88212` (`26RJ`), and `00961087` (`23RH`), FT observed exactly 9 cards.
  - Items `26XM`, `26XH`, `26XF`, `26RG`, and `2026-AI-IA` were not in the test PDF/receipt used during that specific check.
* **Root-Cause Fix for R2.8:**
  Field Tester will be provided a dedicated multi-item test payload or staged review queue fixture that includes all 11 catalog items for full verification.

---

### Q4: Why do the sets show a set image instead of the unique coin side?
* **Finding:** The document stored in Firestore points to the packaging/OGP blister folder image rather than a coin lens.
* **Technical Evidence:**
  - Doc `1c68b2fd` (`26RJ`) in Firestore stores:
    `image_url_obverse: "https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_a.jpg"`.
  - `26rj_a.jpg` is the outer folder/packaging from `user_contributed`.
* **Root-Cause Fix for R2.8:**
  Point `26RJ` documents to `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rj_set_lens.webp` (the Philadelphia Uncirculated Coin Set Lens) or provide a multi-lens selector for uncirculated sets.

---

### Q5 (NET-681A): Is the image placeholder specific to the preview environment?
* **Finding:** **NO. The preview environment has ZERO blocking issues with image loading.**
* **Technical Evidence:**
  1. **Bucket CORS Allowed Origins:**
     Inspected via Google Cloud Storage API on `gs://numista-reference-library`:
     ```json
     [
       {
         "maxAgeSeconds": 3600,
         "method": ["GET", "HEAD"],
         "origin": [
           "*",
           "https://numista.ai",
           "https://numista-vault.web.app",
           "https://numista-vault--p7-gate-8avtpz22.web.app",
           "http://localhost:*",
           "http://127.0.0.1:*"
         ],
         "responseHeader": ["Content-Type", "Access-Control-Allow-Origin", "Cache-Control"]
       }
     ]
     ```
     The origin list includes `*` AND explicitly enumerates `https://numista-vault--p7-gate-8avtpz22.web.app`.
  2. **API-Key & Storage Referrer Restrictions:** None exist on public GCS asset reads.
  3. **Firebase Storage Rules:** Unused for reference images (`numista-vault.appspot.com` does not host these files; they are served directly from GCS).
  4. **Direct Fetch Status:** All official 2026 Mint URLs return `HTTP/2 200 OK` with `Access-Control-Allow-Origin: *` and `Content-Type: image/webp`.
* **Conclusion:** The placeholder is purely data-driven: when `rawUrl` is empty in Firestore, the client defaults to the placeholder icon without attempting network I/O.

---

## 3. Eric's Real Account Must-Fixes (E1–E7)

### E1: Duplicate Eagle Photo (Peace Dollar & Morgan Dollar Enhanced)
* **Diagnosis:**
  - Doc `a59853c1-b72b-414d-8b8e-de6813c29996` (`26XL` Peace Dollar Reverse Proof):
    Has `image_url_reverse` pointing to `Peace-Dollar-Reverse-Proof-Reverse.jpg` (Eagle).
  - Doc `be10e44ce5b4ff4b46c92426cc7f59a254ed675c` (`26XE` Morgan Dollar Enhanced):
    Has `image_url_obverse: null`.
  - In `numista_mobile/lib/screens/my_collection_screen.dart:3063` (`_CollectionCardImage`):
    ```dart
    final obv = _cleanUrl(data[_F.imageObverse]);
    final rev = _cleanUrl(data[_F.imageReverse]);
    final directUrl = rev.isNotEmpty ? rev : obv; // Prefer reverse (distinct design)
    ```
    For `26XL`, `directUrl` chose `rev` (Eagle).
    For `26XE`, `directUrl` was empty, so it invoked `CoinImageService.fetchReferenceImages()`, which defaulted to generic Morgan Dollar reverse (also an Eagle!). Both cards displayed an eagle.
* **Fix Plan:**
  - For Morgan Dollar and Peace Dollar (and 2026 America250 coins), prioritize the **unique coin side**:
    - `26XE`: Obverse featuring Liberty with 1776~2026 privy mark (`26xe_obverse.webp`).
    - `26XL`: Obverse featuring Reverse Proof Liberty (`26xl_obverse.webp`).
  - In `_CollectionCardImage`: if coin is Morgan Dollar, Peace Dollar, or has explicit obverse privy, prefer `obv` over `rev`.

---

### E2: Placeholders (2026 Set, American Innovation, Trump $1)
* **Diagnosis:**
  In `users/eric.seaman@yahoo.com/coins`:
  - `0e68ecba760df66bf824ec1ba2c86b32318d002d` (`26GC` American Innovation): `image_url_obverse: null`.
  - `91f8821265bfe8a33fbd97e21f102c67fdf849fd` (`26RJ` Uncirculated Set): `image_url_obverse: null`.
  - `7a32932ebc4e94a586534e7180cd1c4372c4f17d` (`26SQRP` Trump $1 Roll): `image_url_obverse: null`.
  `_CollectionCardImage` finds no direct URL and reference image service has no entry for 2026, rendering the placeholder.
* **Fix Plan:**
  - Client-side read-time fallback in `_CollectionCardImage` using `retailer_item_num` / `item_number`:
    - `26GC` $\rightarrow$ `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26gc_reverse.webp`
    - `26RJ` $\rightarrow$ `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rj_set_lens.webp`
    - `26SQRP` $\rightarrow$ `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_obverse.webp`
  - Backfill script to persist these URLs in Eric's Firestore docs upon typed YES.

---

### E3: Packaging on 2026 250th Anniversary Uncirculated Set Card
* **Diagnosis:**
  Doc `71e2d4ae92bc4312a4198a3a0cc21fcb` stores:
  `image_url_obverse: "https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_a.jpg"`.
  This file is the blister packaging cover.
* **Fix Plan:**
  Update URL to the official Set Lens (`26rj_set_lens.webp` or `26rj_b.jpg`).

---

### E4: 'Valuation Pending' and 'Unspecified' Grade
* **Diagnosis:**
  1. **Valuation Pending:**
     In `my_collection_screen.dart:3016-3023`:
     ```dart
     final valCpg = _parseNumber(m['cpgRetail']);
     final valueText = valCpg > 0 ? fmt.format(valCpg) : (m[_F.aiValue]?.toString() ?? '—');
     ```
     And lines 3169-3178:
     ```dart
     if (valueText == '—' || m['enrichment_status'] == 'pending')
       const Text('Valuation Pending')
     ```
     The card ONLY reads `cpgRetail` and `aiValue`. It ignores `current_value`, `valuation`, `cost`, `purchase_price`, and `unit_cost`. For new 2026 coins where CPG retail is not published, `valueText` is `'—'`, triggering `Valuation Pending`.
  2. **Unspecified Grade:**
     In `my_collection_screen.dart:3000`:
     `final condition = _rowField(m, 'condition', _F.condition);`
     Line 3189 passes `condition` directly to `GradeBadgeWidget(gradeCode: condition)`.
     For doc `0e68ecba...` (`26GC`), `Condition` is `"Unspecified / Raw"`. Because `_buildCardGrid` did not call the grade normalization helper (unlike line 1073: `if (lower == 'unspecified' || lower == 'ungraded' || lower == 'raw') return 'Raw'`), it rendered `Unspecified`.
* **Fix Plan:**
  1. In `my_collection_screen.dart:3016`: Add valuation fallback:
     ```dart
     final costVal = _parseNumber(m['current_value'] ?? m['valuation'] ?? m['cost'] ?? m['purchase_price'] ?? m['unit_cost']);
     final finalVal = valCpg > 0 ? valCpg : costVal;
     ```
  2. In `my_collection_screen.dart:3000`: Normalize grade using `_normalizeCondition(condition)` so `"Unspecified / Raw"` renders as `"Raw"` (or `"UNC"` for uncirculated mint products).

---

### E5: Card Titles Cut Off
* **Diagnosis:**
  In `my_collection_screen.dart:3148-3157`:
  ```dart
  Text(
    displayTitle,
    maxLines: 1,
    overflow: TextOverflow.ellipsis,
    ...
  )
  ```
  `maxLines: 1` cuts off long titles like `"2026 United States Mint Uncirculated Coin Set"` and `"2026 American Innovation $1 Coin"`.
* **Fix Plan:**
  Change `maxLines: 2` with `overflow: TextOverflow.ellipsis` and adjust `childAspectRatio: 0.72` in `_buildCardGrid` to prevent overflow.

---

### E6: 2026 Dimes Show 2025 Roosevelt Dime Image (NET-681C)
* **Diagnosis:**
  In `users/eric.seaman@yahoo.com/coins`:
  - Doc `nAnGLwGvhfIOibf6kIft` (2026-P Dime) points to:
    `.../2025-roosevelt-dime-uncirculated-obverse-philadelphia.jpg` and `.../2025-roosevelt-dime-uncirculated-reverse.jpg`.
  - Doc `rv9SCUTahBuqJkkiJyga` (2026-D Dime) points to:
    `.../2025-roosevelt-dime-uncirculated-obverse-denver.jpg` and `.../2025-roosevelt-dime-uncirculated-reverse.jpg`.
  The image year is visibly **2025**, not 2026, and features the legacy Roosevelt design rather than the 2026 Semiquincentennial Liberty design.
* **Fix Plan:**
  - **(a) Asset Source:** Point 2026-P and 2026-D dimes (Card + Inspector, obverse and reverse) at the 2026 Semiquincentennial Liberty dime assets:
    - 2026-P Dime Obverse: `SemiQ-Dime-Obverse-Unc-P.jpg`
    - 2026-D Dime Obverse: `SemiQ-Dime-Obverse-Unc-D.jpg`
    - 2026 Reverse (both): `SemiQ-Dime-Reverse-Unc.jpg`
  - **(b) Comprehensive Audit:** Performed in Section 4 below.
  - **(c) Year Guard:** Added to `_CollectionCardImage` and `CoinInspectorDialog` (detailed in Section 5).

---

### E7: 26EA Inspector Wrong Year & Swapped Sides (NET-681C Addendum)
* **Diagnosis:**
  In `users/eric.seaman@yahoo.com/coins`:
  - Doc `e91efa62-4e8d-4920-a928-c0c97659bcdc` (2026-W Silver Eagle `26EA`):
    - `image_url_obverse`: `.../American%20Eagle%202023%20One%20Ounce%20Silver%20Proof%20Coin%20Obverse.jpg`
    - `image_url_reverse`: `.../American%20Eagle%202023%20One%20Ounce%20Silver%20Proof%20Coin%20Reverse.jpg`
  - **Defect 1 (Wrong Year):** Shows 2023 instead of 2026.
  - **Defect 2 (Swapped Sides):** In the Coin Inspector, the **REVERSE** tab displays Walking Liberty. Walking Liberty is the **OBVERSE** design!
* **Fix Plan:**
  - Re-map `26EA` to official 2026 assets:
    - Obverse: `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_obverse.webp` (Walking Liberty, 2026)
    - Reverse: `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_reverse.webp` (Landing Eagle with America 250 privy)
  - Side validation guard enforces that the image side label matches the content.

---

## 4. Comprehensive Read-Only Audit of Eric's Real Account

Audit executed across all 252 items in `users/eric.seaman@yahoo.com` and `users/eric@numista.ai`:
* **Total Audited Items:** 252
* **Year Mismatches in Image URLs:** 15 items identified
* **Missing Direct Image URLs (Null in doc):** 127 items (relying on runtime reference service)
* **Unspecified Condition / Grade:** 93 items
* **Valuation Pending (No Retail/AI Value):** 116 items

### Detailed Audit Table: 2026 Products in Eric's Real Account

| # | Doc ID | Coin / Product | Side | Stored Image URL / File | Visible Year | Side Label Check | Unique Side Shown | Verdict | R2.8 Proposed Fix |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `0172d0ee...` | 2026-P Quarter Mayflower | OBV / REV | `microscope/eric@numista.ai/2026_semiquincentennial_mayflower...` | 2026 | Obv = Obv, Rev = Rev | YES | **PASS** | Keep genuine microscope image |
| **2** | `0e68ecba...` | 2026 American Innovation $1 (`26GC`) | OBV / REV | *None (null)* | N/A | Missing | NO (Placeholder) | **DEFECT (E2)** | Map REV to `26gc_reverse.webp` |
| **3** | `71e2d4ae...` | 2026 Uncirculated Coin Set (`26RJ`) | OBV / REV | `coin_sets/.../26rj_a.jpg` (folder packaging) | N/A | Shows box cover | NO (Box) | **DEFECT (E3)** | Remap to Set Lens `26rj_set_lens.webp` |
| **4** | `7a32932e...` | 2026-D Trump $1 Roll (`26SQRP`) | OBV / REV | *None (null)* | N/A | Missing | NO (Placeholder) | **DEFECT (E2)** | Map OBV to `26sqrp_obverse.webp` |
| **5** | `8f2197d5...` | 2026-D Half Dollar 250th | OBV / REV | `users/eric@numista.ai/coins/b22f.../obverse.jpg` | 2026 | Obv = Obv, Rev = Rev | YES | **PASS** | Keep genuine user photo |
| **6** | `91f88212...` | 2026 Set (`26RJ`) | OBV / REV | *None (null)* | N/A | Missing | NO (Placeholder) | **DEFECT (E2)** | Remap to Set Lens `26rj_set_lens.webp` |
| **7** | `a59853c1...` | 2026-P Peace Dollar Rev Proof (`26XL`) | OBV / REV | `Peace-Dollar-Reverse-Proof-Reverse.jpg` | N/A | Card picks Rev (Eagle) | NO (Eagle dup) | **DEFECT (E1)** | Prioritize Obverse `26xl_obverse.webp` |
| **8** | `be10e44c...` | 2026 Morgan Dollar Enhanced (`26XE`) | OBV / REV | *None (null)* | N/A | Falls back to generic Eagle | NO (Eagle dup) | **DEFECT (E1)** | Map OBV to `26xe_obverse.webp` (Liberty w/ Privy) |
| **9** | `e91efa62...` | 2026-W Silver Eagle (`26EA`) | OBV / REV | `American Eagle 2023 One Ounce Silver Proof...` | **2023** | **SWAPPED** (Liberty on Rev tab) | NO (2023 proof) | **DEFECT (E7)** | Remap: Obv $\rightarrow$ `26ea_obverse.webp`, Rev $\rightarrow$ `26ea_reverse.webp` |
| **10** | `nAnGLwGv...` | 2026-P Dime | OBV / REV | `2025-roosevelt-dime-uncirculated-obverse-philadelphia.jpg` | **2025** | Obv = Obv, Rev = Rev | NO (2025 Roosevelt) | **DEFECT (E6)** | Remap to 2026 Semiquincentennial Liberty Dime (P) |
| **11** | `rv9SCUTa...` | 2026-D Dime | OBV / REV | `2025-roosevelt-dime-uncirculated-obverse-denver.jpg` | **2025** | Obv = Obv, Rev = Rev | NO (2025 Roosevelt) | **DEFECT (E6)** | Remap to 2026 Semiquincentennial Liberty Dime (D) |

---

## 5. Image Source Hierarchy & Guard Architecture

### Image Source Priority Order (Per NET-681D)
Whenever resolving coin and currency images, the pipeline and client strictly follow this order:
1. **Tier 1 (Top Priority):** Eric's US Mint downloads:
   `1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\Images from US MInt`
2. **Tier 2:** GCS Official Reference Library:
   `gs://numista-reference-library/reference_library/` (Project `studio-9101802118-8c9a8`; never V3Tees)
3. **Tier 3:** Eric's collection photos:
   `COIN IMAGES` / Microscope uploads
4. **Fallback:** Placeholders are strictly permitted **only with machine-logged proof** that no image exists across Tiers 1–3.

### Year Guard & Side Guard Specification
1. **Year Guard (Cards & Inspector):**
   - For every rendered item with coin year $Y_{\text{coin}}$:
   - Extract any explicit 4-digit year $Y_{\text{img}}$ from image URL / metadata.
   - If $Y_{\text{img}}$ is detected and $Y_{\text{img}} \ne Y_{\text{coin}}$:
     - **Flag and Suppress:** Do not display the wrong-year asset as canonical.
     - Fall back to canonical product SKU map or generic placeholder with a clear year-mismatch badge.
2. **Side Guard (Cards & Inspector):**
   - Assets containing `obverse` are strictly locked to Obverse tabs/renders.
   - Assets containing `reverse` are strictly locked to Reverse tabs/renders.
   - Walking Liberty is enforced as Obverse; Landing Eagle / Heraldic Eagle is enforced as Reverse.

---

## 6. Existing Documents & No-Backfill Architecture

Per NET-681D, the plan must guarantee how **existing documents** display without requiring database mutations:
1. **Client-Side Read-Time Catalog Fallback:**
   In `my_collection_screen.dart` and `review_hub_screen.dart`:
   - If `image_url_obverse` or `image_url_reverse` is missing/null, the client matches `retailer_item_num`, `item_number`, or program title against the canonical 2026 Mint catalog map and renders the canonical GCS asset.
   - If `cpgRetail` is 0 or `aiValue` is null, the client falls back to `current_value`, `valuation`, or `cost` / `purchase_price` / `unit_cost`.
   - If `Condition` is `"Unspecified / Raw"`, the client normalizes it to `"Raw"`.
   - If `cleanQty > 1` and `unit_cost_cents` is null, the client computes $\text{rawCost} / \text{cleanQty}$.
2. **Dedicated Backfill Script (`backfill_eric_collection_100pct.py`):**
   - Prepared with `--dry-run` inspection and reporting.
   - **Mode:** HELD strictly until Founder Eric enters his separate typed YES.

---

## 7. Comprehensive Findings-to-Fix Mapping Matrix

| Finding ID | Source | Issue / Defect | Root Cause | R2.8 Proposed Fix | Verification Method |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Q1 / FT-1** | NET-673 / NET-681 | 2-coin sets show \$169 / \$64.97 each | `unit_cost_cents` null; fallback uses line total; backfill was dry-run | Read-time compute `rawCost / cleanQty` in Dart client; backfill script | FT inspection: cards show \$84.50 and \$32.49 |
| **Q2 / FT-2** | NET-673 / NET-681 | Cards show gold \$ placeholder | Docs have `image_url_obverse: null`; client renders placeholder icon | Client-side catalog map fallback in `_buildCoinThumbnail`; intake enrichment | FT inspection: real coin photos render |
| **Q3 / FT-3** | NET-673 / NET-681 | Missing 2 cards (9 vs 11) | Test intake session did not contain all 11 SKUs | Staged fixture containing all 11 catalog SKUs for FT | FT inspection: count = 11 cards |
| **Q4 / FT-4** | NET-673 / NET-681 | Sets show packaging rather than coin lens | Firestore doc stores `26rj_a.jpg` (outer folder) | Map `26RJ` to official Set Lens (`26rj_set_lens.webp`) | FT inspection: coin lens visible |
| **Q5** | NET-681A | Preview domain CORS/header restriction check | Investigated CORS, API keys, storage rules, HTTP 200s | Confirmed CORS includes `*` and `p7-gate`; not a preview restriction | Direct curl + browser fetch verification |
| **E1** | NET-681B | Duplicate eagle photo on Peace & Morgan Enhanced | Reverse preferred over obverse; Morgan doc lacks obverse URL | Prioritize unique side (obverse with privy mark) for Morgan & Peace | FT check in Eric's account: distinct obverses |
| **E2** | NET-681B | Placeholders in Eric's account (Set, Innovation, Trump) | Firestore docs in Eric collection lack image URLs | Client catalog fallback map + backfill script (pending YES) | FT check in Eric's account: images load |
| **E3** | NET-681B | Packaging shown on 250th Uncirculated Set | Doc `71e2d4ae...` has `26rj_a.jpg` | Remap to `26rj_set_lens.webp` | FT check in Eric's account: Set lens displayed |
| **E4a** | NET-681B | Cards show 'Valuation Pending' | CPG retail is 0; client ignores purchase cost/valuation | Add fallback to `current_value`, `valuation`, or `cost` in Dart | FT check in Eric's account: valuation/cost displayed |
| **E4b** | NET-681B | Innovation Dollar grade shows 'Unspecified' | Raw `"Unspecified / Raw"` string bypassed grade normalizer | Run condition through `_normalizeCondition()` $\rightarrow$ `"Raw"` | FT check in Eric's account: grade badge says Raw |
| **E5** | NET-681B | Card titles cut off | `maxLines: 1` in `_buildCardGrid` | Update to `maxLines: 2` with adjusted card aspect ratio | FT check in Eric's account: full title visible |
| **E6** | NET-681C | 2026 Dimes show 2025 Roosevelt image | Generic fallback selected 2025 Roosevelt asset | Remap 2026-P & 2026-D to Semiquincentennial Liberty Dime assets | FT check in Eric's account: 2026 Liberty Dime |
| **E7** | NET-681C | 26EA Inspector shows 2023 Walking Liberty on Rev | Doc points to 2023 proof photo; Walking Liberty mapped to Rev | Remap to `26ea_obverse.webp` / `26ea_reverse.webp` + side guard | FT check in Eric's account: 2026 Eagle, correct sides |
| **DEV-1** | NET-678 | Scope deviation: `26xh_image_3.jpg` uploaded | Extra obverse uploaded during R2.6 | Accepted per NET-679; pre-upload checklist enforced | GCS object inventory intact |

---

## 8. Complete 39-Item Coverage Matrix Against Eric Beta Issue Tracker

Per Directive **NET-681E** (`WAKE_AG-COS-V4_NET-681E_R2.8_TRACKER-COVERAGE_20261031-2014.md`), every open row in `RADIO NET\ERIC_BETA_ISSUE_TRACKER_20261031.csv` is mapped below. Items affecting what Eric's collection displays come first. Every row has an explicit Plan Line or an explicit DEFER with a justified technical reason.

| Tracker ID | Screen / Area | Eric's Reported Defect | Status in Tracker | Plan Line in R2.8 / Disposition | Verification Method / Defer Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **E8** | Whole Account | "Get my account 100% right" | In Plan (R2.8) | Sections 5 & 6: Full read-only audit across all 252 items in `users/eric.seaman@yahoo.com` and `users/eric@numista.ai`; client render fallbacks for zero-mutation instant display fix; backfill script staged for separate YES. | Acceptance Gate: Field Tester PASS on Eric's account with 0 wrong items. |
| **E1** | Collection Cards | "Peace and Morgan share the same eagle photo" | In Plan (R2.7/R2.8) | Section 4.E1: Prioritize unique side (obverse with privy mark) for Morgan and Peace dollar cards. | FT visual verification on Eric account Cards view. |
| **E2 / B27-5** | Cards & Review | "None of the 3 had images... placeholders" | Fixed but FT FAIL | Section 4.E2, 4.Q2: Add client-side 2026 catalog map fallback in `_buildCoinThumbnail` to resolve official Mint assets; backfill script. | FT inspection on p7-gate: real photos load. |
| **E3** | Collection Card | "Unc Set card shows packaging" | In Plan (R2.7/R2.8) | Section 4.E3, 4.Q4: Remap SKU `26RJ` to official Set Lens (`26rj_set_lens.webp`) rather than packaging `26rj_a.jpg`. | FT visual verification on Eric account. |
| **E4a / B27-5** | Collection Cards | "Cards show Valuation Pending" | Fixed but FT FAIL | Section 4.E4a: Add client-side fallback in `my_collection_screen.dart` to `current_value`, `valuation`, or purchase cost when CPG retail is 0/null. | FT inspection on Eric account: valuation/cost displayed. |
| **E4b / B27-6** | Collection Cards | "American Innovation had Unspecified for grade" | In Plan (R2.7/R2.8) | Section 4.E4b: Run condition string through `_normalizeCondition()` so `"Unspecified / Raw"` renders cleanly as `"Raw"`. | FT inspection on Eric account: grade badge says Raw. |
| **E5** | Collection Cards | "Titles are truncated" | In Plan (R2.7/R2.8) | Section 4.E5: Change `maxLines: 1` to `maxLines: 2` in `_buildCardGrid` with adjusted card aspect ratio. | FT inspection on Eric account: full titles visible. |
| **E6** | Coin Inspector | "2026 dimes show a 2025 Roosevelt image in Inspector" | In Plan (R2.7/R2.8) | Section 4.E6: Remap 2026-P & 2026-D dimes to genuine Semiquincentennial Liberty Dime assets (`SemiQ-Dime-Obverse-Unc-P.jpg`, `SemiQ-Dime-Obverse-Unc-D.jpg`). | FT inspection on Eric account: 2026 Liberty Dime displayed. |
| **E7** | Coin Inspector | "2026-W Silver Eagle Rev tab shows 2023 Walking Liberty" | In Plan (R2.7/R2.8) | Section 4.E7: Remap doc `e91efa62...` to 2026 Eagle obverse/reverse assets; add regex year guard and side guard. | FT inspection on Eric account: 2026 Eagle, correct sides. |
| **B29-6 / FT-1** | Review Card Price | "2-coin sets show $169.00 and $64.97 each" | Fixed but FT FAIL | Section 4.Q1: Client compute fallback `rawCost / cleanQty` when `unit_cost_cents` is null. | FT inspection: cards show $84.50 and $32.49. |
| **FT-2 / Q3** | Review Queue | "Only 9 of 11 cards show" | In Plan (R2.7/R2.8) | Section 4.Q3: Stage complete 11-SKU catalog intake fixture for FT retest. | FT inspection: 11 review cards render. |
| **B26-1** | Review Hub fee | "Missed the $9.95 shipping and handling... unable to add fee" | Fixed on p7-gate, FT PASS | Re-check in Eric's account: verify truck icon fee displays $9.95 and is editable/savable. | FT re-verification on Eric account. |
| **B26-2** | Review Hub card date | "Main screen had no date, but when I clicked Edit date was there" | Unverified | Section 8 Plan Line: Ensure review card subtitle displays formatted invoice/order date from metadata if present. | FT verification on p7-gate. |
| **B26-3** | Edit Coin > Save | "Unable to save" | Unverified | Section 8 Plan Line: Verify Edit Coin save action persists changes to Firestore/state cleanly with error toast guard. | FT verification on p7-gate. |
| **B26-4** | Morgan AI Chat | "Morgan would only accept image files (not the PDF invoice)" | Not in any plan | **EXPLICIT DEFER TO UX BACKLOG**: Morgan AI chat attachment endpoint enforces `image/*` MIME filtering. Ingesting multi-page PDF invoices into the chat stream requires a server-side PDF rasterization/OCR pipeline, which is a major feature extension out of scope for the emergency Mint fix on branch `p7-v8.9`. | Deferred to Post-Mint Roadmap. |
| **B26-5** | Add Coins screen | "Two ways to add by Cert, 2 ways by photo... Very confusing!" | Unverified | **EXPLICIT DEFER (UX Redesign)**: Retain streamlined Add Coins layout verified in NET-647 #1-3. Full IA/UX overhaul of Add Coins screen deferred to post-Mint beta release to prevent scope creep. | FT founder walk-through check. |
| **B26-6** | Invoice upload flow | "1 or 2 more clicks than it needed to be" | Unverified | Section 8 Plan Line: Verify invoice upload flow reaches review queue in minimum clicks (tested green in NET-647). | FT click-count verification on p7-gate. |
| **B26-7** | Review Queue | "Wish I could enter storage location right from this screen" | Unverified | Section 8 Plan Line: Verify inline storage location field on review card (added in NET-585 / NET-647 #9) works and persists. | FT verification on p7-gate. |
| **B26-8** | Bulk Import / Review | "Had to scroll down (again) to get to next step" | Fixed on p7-gate, FT PASS | Verified PASS in NET-647 #3-5 (auto-scroll to active item / sticky action bar). | FT regression check. |
| **B27-1** | Trump $1 roll row | "July 4th Privy eligible... I don't know if we need that" | Unverified | Section 8 Plan Line: Suppress extraneous "July 4th Privy eligible" badge from review card unless explicitly part of product SKU title. | FT verification on p7-gate. |
| **B27-2** | Edit in Review Hub | "Added it via Edit, which automatically saved it to collection" | Fixed on p7-gate, FT PASS | Verified PASS in NET-627 I-04c (explicit Commit button required). | FT regression check. |
| **B27-3** | Review Hub | "Hitting Select All appeared to initiate a Delete" | Fixed on p7-gate, FT PASS | Verified PASS in NET-627 I-05 (clear checkbox icon vs trash icon separation). | FT regression check. |
| **B27-4** | Review Hub button | "Commit Selected... hard to read... does it delete or add?" | Fixed on p7-gate, FT PASS | Verified PASS in NET-627 I-06 (high-contrast label "Commit Selected to Collection"). | FT regression check. |
| **B27-7** | My Collection | "No rhyme or reason to how coins were sorted" | Unverified | Section 8 Plan Line: Enforce deterministic default collection sort order: Acquisition Date DESC, Year DESC, Name ASC. | FT verification on Eric account. |
| **B27-8** | Coin Inspector | "I thought we did away with Google Images button?" | Fixed on p7-gate, FT PASS | Verified PASS in NET-627 P1 (button removed). | FT regression check. |
| **B27-9** | My Collection CTA | "Generate AI Report Now opened state picker for estate tax" | Unverified | Section 8 Plan Line: Ensure My Collection CTA opens Collection Value / Inventory Report, NOT Estate Tax state picker. | FT verification on Eric account. |
| **B27-10** | My Collection CTA | "Replace Generate AI Report Now with something to fill images/values" | Unverified | Section 8 Plan Line: Add/re-point CTA button to "Refresh Images & Valuations" (triggers catalog enrichment). | FT verification on Eric account. |
| **B27-11** | Table view / Cards | "Impossible to read due to text/background colors... prefer gold/black" | Fixed on p7-gate, FT PASS | Verified PASS in NET-631 / NET-647 (cream contrast & theme styling). | FT regression check on Eric account. |
| **B27-12** | Card view detail | "Financials, Provenance, AI Insights... should also be in Card view" | Unverified | Section 8 Plan Line: Verify bottom sheet modal / expandable card drawer on Card tap exposes Financials, Provenance, and AI Insights tabs. | FT verification on Eric account. |
| **B27-13** | Table AI Insights | "AI Insights had large gaps and/or unreadable text" | Unverified | Section 8 Plan Line: Verify AI Insights markdown rendering has tight paragraph spacing and readable contrast. | FT verification on Eric account. |
| **B27-14** | Table view | "Legislation Matched was blank" | Unverified | Section 8 Plan Line: Ensure legislation metadata (e.g. Public Law 116-330 Semiquincentennial Act) populates for 2026 items. | FT verification on Eric account. |
| **B27PM-1** | Review Hub | "No duplicates flagged" | Fixed on p7-gate, FT PASS | Re-confirm in Eric's account: amber duplicate banner fires when matching certificate/title exists. | FT verification on p7-gate. |
| **B27PM-2** | Cards + Detail | "Can't tell if I have two 2026 Uncirculated Coin Sets" | Unverified | Section 8 Plan Line: Disambiguate multi-set holdings with distinct item numbers / mint badges (e.g. P-Mint Lens vs D-Mint Lens or Set 1 / Set 2). | FT verification on Eric account. |
| **B27PM-3** | Search results | "Set I just uploaded did not have 250th Anniversary under Theme" | Fixed on p7-gate, FT PASS | Verified PASS in NET-627 SAG2 (theme stamped from Mint catalog). | FT regression check. |
| **B27PM-4** | Card detail pop-up | "Could not make pop-up bigger... Lincoln quarter cut off" | Fixed on p7-gate, FT PASS | Verified PASS in NET-631 (20-coin wrap grid in detail dialog). | FT regression check. |
| **B29-1** | Add Coins | "Upload an Invoice does nothing when clicked" | Fixed on p7-gate, FT PASS | Verified PASS in NET-647 #1 & NET-673 #6. | FT regression check. |
| **B29-2** | Add Coins / Drop | "Only bottom inch of page scrolled / drop zone ~5% of screen" | Fixed on p7-gate, FT PASS | Verified PASS in NET-647 #2, #3 (expanded drop zone & scroll). | FT regression check. |
| **B29-3** | Bulk Import | "Search by Store/Dealer Name... remove it" | Fixed on p7-gate, FT PASS | Verified PASS in NET-647 #7 (input removed). | FT regression check. |
| **B29-4** | Review card | "Having 2 links/buttons to paper trail is pointless clutter" | Unverified | Section 8 Plan Line: Verify review card displays single consolidated Paper Trail / Receipt action. | FT verification on p7-gate. |
| **B29-5** | Review card | "These both do same thing, delete top one that says Storage" | Fixed on p7-gate, FT PASS | Verified PASS in NET-673 #4 (duplicate button removed). | FT regression check. |

---

## 9. Review Cycle Gate & Execution Sequence

1. **Gate Sequence:**
   - **Step 1:** Argon Review of Plan R2.8 (`GEMINI38_REVIEW_NET-647_R2.8.md`).
   - **Step 2:** Grok CoS scoring ($\ge 95$ required).
   - **Step 3:** Stand Alone Grok (SAG) Review.
   - **Step 4:** Founder (Eric) typed YES to authorize execution on `p7-v8.9`.
   - **Step 5 (Separate Gate):** Founder (Eric) separate typed YES for any Firestore writes to real account (`eric.seaman@yahoo.com`).
2. **Acceptance Test:** Field Tester PASS on Eric's own account with **zero wrong items**.
3. **Standing Locks:** `origin/main` locked at `9f04550a`; `origin/dev` catalog frozen at `9b55f3d9`; Stripe OFF.
