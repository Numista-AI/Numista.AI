# GEMINI 3.8 TECHNICAL REVIEW: `FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md`

- **Review ID:** `GEMINI38_REVIEW_NET-647_R2.8.18_2026-11-02`
- **Track / NET:** `NET-647` (Vault / Mint Order / Coin Image Rendering & Official US Mint Reference Asset Pipeline) / `BATON_NET-745`
- **Plan Under Review:** [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md)
- **Author of Plan:** GB CoS (Grok Bot Chief of Staff; attempt 6 of 10 under Founder Eric's 2 Nov 5:58 PM ET rule)
- **Reviewer:** Gemini 3.8 Code Reviewer in Antigravity (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)
- **Date:** 2026-11-02
- **Git Baseline Verified:** `origin/dev` (`6e19c71d` / app code tree `01a03f90`)
- **Measured Plan MD5:** `2A7805A7DC3C85EBCEE22574BE84BA6D` (verified against sidecar `.md5` file)
- **Score:** **`100 / 100 — PASS`**
- **Execution Gate:** **STAGED FOR GATE 3 FOUNDER ERIC TYPED YES** — Plan passes consensus threshold (>= 95). Zero code edits, zero builds, zero deploys, zero GCS uploads, zero Firestore writes without Founder Eric's typed `YES`.

---

## 1. Executive Summary & Scoring Breakdown

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Data Accuracy & Firestore Lineage (§4)** | 20 | **20 / 20** | All 28 rows in Section 4 table match `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json` verbatim (doc IDs, accounts, SKUs, years, mints, and themes). Exactly 28 rows, exactly 9 columns per row. |
| **2. URL & Byte Truth (§4 & §4.1.1)** | 20 | **20 / 20** | All primary and fallback URLs, measured byte counts, and MD5 digests reconciled to live GCS HEAD probes. Row 28 reverse MD5 prefix verified as `beb40fba68` (matching live GCS HEAD `584,055 B` and §4.1.3 row 001). Rows 01, 02, 26 col 9 explicitly itemize distinct bytes, MD5 digests, and status for both `_a` (LIVE HTTP 200) and `_b` (STAGED Gate 4). §4.1.1 Half Dollar bytes match live GCS HEAD. |
| **3. Unit Tests & Execution Output (§3.2)** | 15 | **15 / 15** | Unit test suite contains 44 unique tests (28 live Firestore cases + 14 synthetic tracker cases + 2 reference/catalog lookup cases). Nullable fallbacks cleanly asserted (`expect(pair.fallbackObverseUrl, isNull);` / `expect(pair.fallbackReverseUrl, isNull);`). Verbatim console output embedded at L1251–L1265 confirms `00:00 +44: All tests passed!` (Exit code 0). |
| **4. Architectural Guards & Non-Destructive Protection (§3.1)** | 15 | **15 / 15** | Row 11 microscope user photo non-destructive protection intact via `hasUserUploadedPhotos` guard in `resolveFromMap` (returns `null`, leaving user photos untouched). West Point guard strictly protects `26EA` from S mint confusion. Broken HTTP 404 fallback on `2026-DIME-D` eliminated with `fallbackObverseUrl: null`. |
| **5. Census & Staging Transparency (§3 line 75, §4.1.3)** | 10 | **10 / 10** | Census counts in §3 line 75 reconciled with §4.1.3: exactly 114 total reference suite paths, 110 Live HTTP 200, and 4 explicitly staged for Gate 4 upload (`26ea_b.webp`, `26xe_b.webp`, `23rh_b.webp`, `23rh_c.webp`) with local byte sizes and MD5 digests. Stale narrative bullets purged. |
| **6. Document Structure & Single-Service Hygiene (§3.1, §3.2, §1, EOF)** | 10 | **10 / 10** | Exactly one `class CanonicalMintAssetService` (L103) and one `class CanonicalMintAssetPair` (L81) in the document. Section 1 R2.8.18 Deliberation Matrix cleanly positioned at top with exact line number citations (L12–L21). Document terminates cleanly at L1735 with `**END PLAN R2.8.18**`. |
| **7. Claim Honesty & Sidecar Verification** | 5 | **5 / 5** | Sidecar `FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md.md5` hashes to `2A7805A7DC3C85EBCEE22574BE84BA6D`. All MD5 prefixes verified against live GCS HEAD probes or measured local files. Gate 6 correctly cites dev tip `6e19c71d`. |
| **8. Rule 6(a) Verbatim Code Citations (§7)** | 5 | **5 / 5** | All 5 repository integration targets in §7 cite exact verbatim code matching active repository tip `origin/dev 01a03f90`. |
| **TOTAL** | **100** | **`100 / 100`** | **Verdict: `PASS` (Consensus >= 95; Staged for Founder Eric Typed YES)** |

---

## 2. Rule 6(a) Verbatim Verification of R2.8.18 Fixes (F-1 through F-5)

Per Standing Order 6(a), each checked item is cited with its exact file:line reference and verbatim quote from `FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md`:

### 2.1 Item F-1: Row 28 Reverse MD5 Prefix Reconciled to Live GCS HEAD
- **Finding in R2.8.17:** Row 28 reverse listed invented prefix `md5: 0313c4fb1c...`.
- **Verification in R2.8.18:** Updated to live GCS HEAD digest prefix `beb40fba68` (`vrQPumi94UYMhlxdfVTYpg==` = `beb40fba68bde1460c865c5d7d54d8a6`, `584,055 B`), matching Section 4.1.3 row 001.
- **Verbatim Line Cite:**
  [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:1300`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L1300):
  ```markdown
  | 28 | `2fa325166682b70aa0d64da45786c94aa4742d21` | `eric@numista.ai` | `23RH` | `2023` | Silver Proof Set (10-coin set) | `reference_library/2023_series/2023_american_women_quarters_five_honorees_composite.jpg` (`711,501 B` (`md5: 1e65934dca...`)) | `reference_library/2023_series/2023_american_innovation_four_states_composite.jpg` (`584,055 B` (`md5: beb40fba68...`)) | `reference_library/us_mint_official/2023_products/23rh_b.webp` (`226,854 B`, `STAGED Gate 4`) / `reference_library/us_mint_official/2023_products/23rh_c.webp` (`161,734 B`, `STAGED Gate 4`) |
  ```

### 2.2 Item F-2: Rows 01, 02, 26 Column 9 Disambiguation
- **Finding in R2.8.17:** Column 9 displayed a single byte/MD5 label ambiguous between `_a` and `_b` files.
- **Verification in R2.8.18:** Both paths carry distinct byte sizes, MD5 prefixes, and explicit status labels (`HTTP 200 LIVE` vs `STAGED Gate 4`).
- **Verbatim Line Cites:**
  - **Row 01:** [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:1273`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L1273):
    ```markdown
    | 01 | `e91efa62-4e8d-4920-a928-c0c97659bcdc` | `eric.seaman@yahoo.com` | `26EA` | `2026-W` | America250 | `reference_library/us_mint_official/2026_products/26EA_image_1.jpg` (`126,209 B` (`md5: cb25bbc19d…`)) | `reference_library/us_mint_official/2026_products/26EA_image_2.jpg` (`139,910 B` (`md5: cfa91a545c…`)) | `reference_library/us_mint_official/2026_products/26ea_a.webp` (`168,246 B`, `md5: 790d13287d...`, `HTTP 200 LIVE`) / `reference_library/us_mint_official/2026_products/26ea_b.webp` (`164,146 B`, `md5: 62ad11e997...`, `STAGED Gate 4`) |
    ```
  - **Row 02:** [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:1274`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L1274):
    ```markdown
    | 02 | `be10e44ce5b4ff4b46c92426cc7f59a254ed675c` | `eric.seaman@yahoo.com` | `26XE` | `2026` | Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026) | `reference_library/us_mint_official/2026_products/26XE_image_2.jpg` (`240,850 B` (`md5: 030c23e7cc…`)) | `reference_library/us_mint_official/2026_products/26XE_image_3.jpg` (`285,827 B` (`md5: e056a201fc…`)) | `reference_library/us_mint_official/2026_products/26xe_a.webp` (`216,358 B`, `md5: 96290c2d73...`, `HTTP 200 LIVE`) / `reference_library/us_mint_official/2026_products/26xe_b.webp` (`245,878 B`, `md5: 3a77694c9a...`, `STAGED Gate 4`) |
    ```
  - **Row 26:** [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:1298`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L1298):
    ```markdown
    | 26 | `be10e44ce5b4ff4b46c92426cc7f59a254ed675c` | `eric@numista.ai` | `26XE` | `2026` | Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy, 1776~2026) | `reference_library/us_mint_official/2026_products/26XE_image_2.jpg` (`240,850 B` (`md5: 030c23e7cc…`)) | `reference_library/us_mint_official/2026_products/26XE_image_3.jpg` (`285,827 B` (`md5: e056a201fc…`)) | `reference_library/us_mint_official/2026_products/26xe_a.webp` (`216,358 B`, `md5: 96290c2d73...`, `HTTP 200 LIVE`) / `reference_library/us_mint_official/2026_products/26xe_b.webp` (`245,878 B`, `md5: 3a77694c9a...`, `STAGED Gate 4`) |
    ```

### 2.3 Item F-3: Section 3 Census Counts Reconciled
- **Finding in R2.8.17:** Section 3 bullet cited stale text `95/97 live, 2/97 staged`.
- **Verification in R2.8.18:** Line 75 reconciled with Section 4.1.3: exactly 114 paths, 110 Live, 4 Staged.
- **Verbatim Line Cite:**
  [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:75`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L75):
  ```markdown
  - Uses **only verified GCS paths** in `gs://numista-reference-library` (Section 4.1.3 census: `114` paths, `110` live HTTP 200 right now; `4` explicitly staged for Gate 4: `26ea_b.webp`, `26xe_b.webp`, `23rh_b.webp`, `23rh_c.webp`, each HTTP 404 live until upload, with live HTTP 200 primaries).
  ```

### 2.4 Item F-4: Section 9.2 Gate 6 Repository Tip Harmonization
- **Finding in R2.8.17:** Gate 6 cited stale dev tip `32d4b42e`, contradicting header.
- **Verification in R2.8.18:** Line 1729 cites live git tip `6e19c71d` before docs commit, confirming app code unchanged since `01a03f90`.
- **Verbatim Line Cite:**
  [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:1729`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L1729):
  ```markdown
  - **Gate 6:** Deploy exclusively to Firebase Hosting preview channel `p7-gate` (`https://numista-vault--p7-gate-8avtpz22.web.app`) on branch `p7-v8.9`. `origin/main` locked at `9f04550a`; `origin/dev` tip at `6e19c71d` before this plan's docs commit (live `git rev-parse origin/dev`, 2 Nov ~6:05 PM ET); app code on dev unchanged since `01a03f90`, same as header. Preview deployment channel uses `p7-v8.9` strictly; zero code pushes to `dev` or `main`.
  ```

### 2.5 Item F-5: Section 1 Deliberation Matrix Line Number Citations
- **Finding in R2.8.17:** Section 1 matrix cited section names instead of exact plan line numbers.
- **Verification in R2.8.18:** Lines 14–20 cite exact line numbers of final document.
- **Verbatim Line Cites:**
  [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:14-20`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L14-L20):
  ```markdown
  | Item | COS_SCORE R2.8.17 finding | Resolution in R2.8.18 | Changed lines (this file) |
  | :---: | :--- | :--- | :--- |
  | **F-1** | Row 28 reverse MD5 prefix `0313c4fb1c` had no source | Set to `beb40fba68` (live HEAD x-goog-hash `vrQPumi94UYMhlxdfVTYpg==` = `beb40fba68bde1460c865c5d7d54d8a6`, 584,055 B, matches 4.1.3 row 001) | Row 28: line 1300 |
  | **F-2** | Rows 01, 02, 26 col 9 showed one size/MD5 for two paths | Each path now carries its own bytes, MD5 prefix and status: `26ea_a` 168,246 B `790d13287d` LIVE; `26ea_b` 164,146 B `62ad11e997` STAGED; `26xe_a` 216,358 B `96290c2d73` LIVE; `26xe_b` 245,878 B `3a77694c9a` STAGED | Row 01: line 1273; Row 02: line 1274; Row 26: line 1298 |
  | **F-3** | Section 3 bullet said 95/97 live, 2/97 staged | Now matches the 4.1.3 census: 114 paths, 110 LIVE, 4 STAGED (rows 111-114: 26ea_b, 26xe_b, 23rh_b, 23rh_c) | line 75 |
  | **F-4** | Gate 6 said dev tip 32d4b42e | Gate 6 now states live-checked dev tip `6e19c71d` (pre-commit), code unchanged since `01a03f90`, same as header | line 1729 |
  | **F-5** | Section 1 cited sections, not lines | This table cites line numbers of the final R2.8.18 file | lines 12-21; header lines 1-8; footer line 1735 |
  ```

---

## 3. Structural & Functional Checks

1. **Single-Service Copy:**
   - Exactly one definition of `CanonicalMintAssetPair` at line 81:
     [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:81`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L81):
     ```dart
     class CanonicalMintAssetPair {
     ```
   - Exactly one definition of `CanonicalMintAssetService` at line 103:
     [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:103`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L103):
     ```dart
     class CanonicalMintAssetService {
     ```
2. **Nullable Fallback Safety & Redundant Fallback Elimination:**
   - Verified `2026-DIME-D` fallbacks are both `null`:
     [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:407-408`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L407-L408):
     ```dart
               fallbackObverseUrl: null,
               fallbackReverseUrl: null,
     ```
   - Verified `26SQRP` fallback reverse is `null`:
     [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:256`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L256):
     ```dart
           fallbackReverseUrl: null,
     ```
3. **Execution Output:**
   - Verified verbatim unit test output ending at line 1265:
     [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:1265`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L1265):
     ```text
     00:00 +44: All tests passed!
     ```
4. **Clean Termination:**
   - Document terminates at line 1735 with no extraneous trailing content:
     [`FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md:1735`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/FAILFIX_PLAN_NET-647_R2.8.18_CoS_20261102.md#L1735):
     ```markdown
     **END PLAN R2.8.18**
     ```

---

## 4. Verdict & Execution Gate

- **Consensus Score:** **`100 / 100 — PASS`** (Threshold >= 95 satisfied).
- **Execution Gate Status:** **STAGED FOR FOUNDER ERIC TYPED YES** (Gate 3).
- **Operating Mode:** DOCS-ONLY. Deployment gate remains strictly locked until Founder Eric reviews consensus score and gives typed `YES`.
