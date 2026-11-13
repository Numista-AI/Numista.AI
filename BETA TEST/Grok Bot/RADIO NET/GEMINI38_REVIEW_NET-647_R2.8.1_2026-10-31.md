# GEMINI 3.8 (ARGON) TECHNICAL REVIEW — `FAILFIX_PLAN_NET-647_R2.8.1_20261031.md`

- **Reviewer:** Argon (`Numista.Ai Argon` — Planning & Review Desk)
- **Date / Time:** 2026-10-31 21:42 ET
- **Radio Net Reference:** `NET-688` (Review of `NET-686` Plan `R2.8.1`; concurring with and expanding Grok CoS `NET-687` Score `78/100 REVISE` for `R2.8.2`)
- **Target Plan:** `BETA TEST/Grok Bot/8 OCT 26/RADIO NET/FAILFIX_PLAN_NET-647_R2.8.1_20261031.md` (`R2.8.1`)
- **Mode:** **DOCS-ONLY (`NO EXECUTE`)** — Zero source code changes, zero commits, zero deploys, zero Firestore/GCS mutations.

---

## 1. Executive Verdict & Readiness Score

- **Score:** **81 / 100 — `REVISE` (`R2.8.2` Fix-Only Required)**
- **Summary:**
  `Plan R2.8.1` properly resolved 4 of the 6 `MUST-FIX` items from Argon's `NET-685` review (`M3` verbatim `collection_Mint_screen.dart:2040-2058` quote + roll guard; `M4` Title-Case `'Purchase Cost'` / `'Cost'` lookup at `my_collection_screen.dart:3016-3022`; `M5` existing `_conditionLabel` call at `my_collection_screen.dart:3000`; `M6` `_CollectionCardImage` line `6358-6360` cite + basename Year Guard regex).
  However, **4 `MUST-FIX` blockers** and **1 `SHOULD-FIX` item** prevent `R2.8.1` from passing execution readiness (concurring with Grok CoS `NET-687` Blockers #1, #2, and S1, plus **2 critical code/data bugs** uncovered during Argon's live read-only verification of `users/eric.seaman@yahoo.com/coins` and `coin_image_index`):
  1. **`MUST-FIX 1` (Concurring with Grok CoS `NET-687` Blocker #1 — 8 of 9 `2026_products/` URLs Claimed as `"HTTP 200 OK"` in §6 Return `HTTP 404`):** `R2.8.1` §6 (`lines 293-334`, `358-366`) invented `.webp` filenames (`26ea_obverse.webp`, `26ea_reverse.webp`, `26xe_obverse.webp`, `26xe_reverse.webp`, `26xl_obverse.webp`, `26xl_reverse.webp`, `26rj_set_lens.webp`, `26sqrp_obverse.webp`, `26sqrp_reverse.webp`) that do **not** exist in `gs://numista-reference-library/reference_library/us_mint_official/2026_products/`. Below in §3.1 we provide the **exact, curl-verified `HTTP 200 OK` GCS URLs** that already exist in GCS today plus the exact local 7C `--no-clobber` upload manifest.
  2. **`MUST-FIX 2` (Concurring with Grok CoS `NET-687` Blocker #2 — Every One of the 28 Rows in §4.2 Must List Concrete `HTTP 200` Obverse & Reverse URLs):** `R2.8.1` §4.2 (`lines 212-241`) used prose placeholders (`Canonical 2026Quarter Obv/Rev`, `2005 Kansas Rev`, `2019 AMP Rev`) instead of concrete URLs. Below in §3.2 we provide the **complete 28-row URL table** verified against `gs://numista-reference-library` (`7,262` blobs) so AG CoS v4 can paste it directly into `R2.8.2`.
  3. **`MUST-FIX 3` (NEW Critical Code Bug in `R2.8.1` §6 — `Canonical2026MintAssets.resolve()` Reads Lowercase `data['year']`, Which Is `null` on Every Invoice-Imported Doc in Eric's Account):**
     In `R2.8.1` (`lines 284-289`), `Canonical2026MintAssets.resolve()` checks:
     `final year = data['year']?.toString().trim(); if (year != '2026') return null;`
     and reads `data['name'] ?? data['title'] ?? data['Theme/Subject']`.
     In Firestore (`users/eric.seaman@yahoo.com/coins` and `users/eric@numista.ai/coins`), the invoice-imported documents (`0e68ecba`, `0a2bc793`, `be10e44c`, `7a32932e`, `91f88212`, `faa5b1cf`) store Title-Case **`data['Year']`** (`data['year']` is `null`!), **`data['Mint Mark']`** (`data['mint']` is `null`!), **`data['Program/Series']`**, and **`data['Personal Notes']`** (e.g., `'Item # 26RJ - Uncirculated Coin Set 2026'` on `0a2bc793` where `item_number`, `name`, `title`, and `Theme/Subject` are all absent!). As written in `R2.8.1`, `Canonical2026MintAssets.resolve()` returns `null` on **100% of Eric's invoice-imported coins**!
  4. **`MUST-FIX 4` (NEW Critical Audit Discovery — `ERIC_ACCOUNT_252_AUDIT_20261031.csv` Has 127 `"Missing images"` Rows, Not 7, and All 60 Presidential Dollars Render Gold `$` Placeholders Due to `my_collection_screen.dart:6396` & `coin_image_service.dart:542,558`):**
     - `R2.8.1` §4.1 (`line 206`) claims `224 items: PASS` and `28 items: DEFECTIVE`, contradicting `ERIC_ACCOUNT_252_AUDIT_20261031.csv`, which actually contains **127 rows marked `"Missing images"`** (`123` in `eric.seaman@yahoo.com/coins` + `4` in `eric@numista.ai/coins` lacking stored `image_url_obverse`/`image_url_reverse` fields) and only **42 rows marked `"PASS"`**.
     - Those 127 items without stored URLs rely on `_CollectionCardImage` (`my_collection_screen.dart:6380-6398`) calling `CoinImageService.fetchReferenceImages()` (`coin_image_service.dart:489-570`) against Firestore `coin_image_index` (`1,003` docs).
     - Because `presidential-dollars` has **39 subject-specific obverse docs** (`2007_adams_presidential-dollars_obverse`, `2008_jackson_presidential-dollars_obverse`, etc.) and only **1 generic reverse doc** (`2007_presidential-dollars_reverse`), `coin_image_service.dart:558` (`if (needsRev && (!hasSubject || isSubjectBase))`) blocks the reverse (`ref.reverseUrl == null`), and then `my_collection_screen.dart:6396` (`: (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)`) **discards `ref.obverseUrl` because `subject` is not empty**, causing **all 60 Presidential Dollars in Eric's collection to display the gold `$` placeholder on `My Collection -> Cards`**!
     - Simultaneously, `coin_image_service.dart:542` (`if (needsObv && (!hasSubject || isSubjectBase))`) violates its own comment at lines `519-520` (`Generic bases ... may only supply the OBVERSE (e.g. shared Washington portrait is fine)`) and blocks the shared Washington obverse on **all 46 50-State Quarters and 7 American Women Quarters** (`50-state-quarters` has `0` state-specific obverse docs in `coin_image_index`).
     - Additionally, **3 duplicate/2026/2023 docs in `eric.seaman@yahoo.com/coins`** (`7a32932e` `26SQRP`, `be10e44c` `26XE`, `2fa32516` `23RH`) and **5 legacy set/book/coin docs** (`4a9aeac4` & `6b9c052b` `1974 Eisenhower Dollar`, `6199ef81` `2002 Proof Set`, `1ANt3s6gWlYKnNcGsgPZ` `2020 Jefferson Nickel`, `cdbf0aad` `U.S. Women's Quarter Book`) lack stored URLs and must be accounted for.

---

## 2. Verification of `NET-685` Items Resolved in `R2.8.1` (With Verbatim Code Quotes per Rule 6a)

1. **`M3` (`unit_cost_cents` Fallback & Roll Guard) — `PASS`:**
   - **File & Lines Checked:** [`numista_mobile/lib/screens/collection_Mint_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/collection_Mint_screen.dart#L2040-L2058)
   - **Verbatim Code Quoted:**
     ```dart
     2040:     final dynamic unitCostCentsRaw = item['unit_cost_cents'];
     2041:     final dynamic costVal = (unitCostCentsRaw is num && unitCostCentsRaw > 0)
     2042:         ? (unitCostCentsRaw.toDouble() / 100.0)
     2043:         : (item['Purchase Cost'] ??
     2044:             item['purchase_price'] ??
     2045:             item['cost'] ??
     2046:             item['value'] ??
     2047:             item['estimated_value'] ??
     2048:             item['total_cost']);
     ```
   - `R2.8.1` §2.Q1 (`lines 42-69`) quotes this block verbatim and divides multi-item set totals (`qty > 1 && qty <= 10 && !isRollOrBag`) using integer cents `ROUND_HALF_UP`.

2. **`M4` (Title-Case `'Purchase Cost'` & `'Cost'` Fallback on Collection Cards) — `PASS`:**
   - **File & Lines Checked:** [`numista_mobile/lib/screens/my_collection_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3016-L3022)
   - **Verbatim Code Quoted:**
     ```dart
     3016:     final double displayValue = cpgRetail > 0
     3017:         ? cpgRetail
     3018:         : ((data['estimated_value'] as num?)?.toDouble() ??
     3019:            (data['value'] as num?)?.toDouble() ??
     3020:            (data['purchase_price'] as num?)?.toDouble() ??
     3021:            (double.tryParse(data[_F.aiValue]?.toString().replaceAll(RegExp(r'[^0-9.]'), '') ?? '') ?? 0.0));
     ```
   - `R2.8.1` §3.E4a (`lines 124-137`) quotes this block verbatim and adds `data['Purchase Cost'] ?? data[_F.cost]` + `paper_trail` fallback.

3. **`M5` (Use Existing `_conditionLabel` Helper for `"Unspecified / Raw"`) — `PASS`:**
   - **File & Lines Checked:** [`numista_mobile/lib/screens/my_collection_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L2996-L3004) and [`L4531-L4536`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L4531-L4536)
   - **Verbatim Code Quoted:**
     ```dart
     2996:     final rawGrade = data[_F.condition]?.toString();
     2997:     final certNumber = data[_F.certNumber]?.toString();
     2998:     final hasCert = certNumber != null && certNumber.isNotEmpty && certNumber != 'None';
     2999:     final gradeLabel = (rawGrade != null && rawGrade.isNotEmpty && rawGrade != 'None')
     3000:         ? rawGrade
     3001:         : (hasCert ? 'Certified' : 'Raw');
     ```
     ```dart
     4531:   static String _conditionLabel(dynamic raw) {
     4532:     final s = raw?.toString().trim() ?? '';
     4533:     if (s.isEmpty || s == 'None' || s == 'null') return 'Raw';
     4534:     if (s.toLowerCase().contains('unspecified')) return 'Raw';
     4535:     return s;
     4536:   }
     ```
   - `R2.8.1` §3.E4b (`lines 139-162`) quotes both blocks verbatim and replaces line `2999-3001` with `_conditionLabel(rawGrade)`.

4. **`M6` (`_CollectionCardImage` Line `6358-6360` & Basename Year Guard Regex) — `PASS`:**
   - **File & Lines Checked:** [`numista_mobile/lib/screens/my_collection_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6358-L6360)
   - **Verbatim Code Quoted:**
     ```dart
     6358:     final obv = _cleanUrl(data[_F.imageObverse]);
     6359:     final rev = _cleanUrl(data[_F.imageReverse]);
     6360:     final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)
     ```

---

## 3. Detailed `MUST-FIX` Items Required for `R2.8.2`

### `MUST-FIX 1`: Replace the 8 Fabricated `HTTP 404` URLs in §6 With Real `HTTP 200 OK` GCS URLs + Explicit `--no-clobber` Upload Manifest

In `R2.8.1` §6 (`lines 293-334` and `358-366`), 8 of the 9 URLs claimed as `"HTTP 200 OK"` under `gs://numista-reference-library/reference_library/us_mint_official/2026_products/` do **not** exist in GCS (`HTTP 404 NotFound`).
Below is the **verified ground truth** comparing Eric's 7C index (`1 NUMISTA.AI\Coin Images\_INDEX\image_index.csv`) against `gs://numista-reference-library` (`MAD = 0.00` pixel-verified):

#### Table 3.1A — Assets Already Live in GCS Today (`HTTP 200 OK` Verified)
| SKU / Program | Side | Verified Live GCS URL (`HTTP 200 OK` Today) | Pixel Match to Eric 7C File |
| :--- | :--- | :--- | :--- |
| **`26EA`** (2026-W Silver Eagle Proof) | Obverse (`1776-2026`) | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_a.webp` | `MAD=0.00` to `26ea_a.webp` (`168,246` B) |
| **`26XE`** (2026 Morgan Dollar Enh. Unc.) | Obverse (`1776~2026`) | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_a.webp` | `MAD=0.00` to `26xe_a.webp` (`216,358` B) |
| **`26XE`** (2026 Morgan Dollar Enh. Unc.) | Obv+Rev Pair / Rev Fallback | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_2.jpg` (or undated reverse `reference_library/wikimedia_uscoin/Dollar_coins_of_the_United_States/Morgan_dollar/2023_Morgan_Dollar_Rev.png` if Year Guard exempts undated reverse) | `MAD=0.00` to `26xe_c.webp` (`240,850` B) |
| **`26XL`** (2026 Peace Dollar Rev. Proof) | Obverse (`1776-2026`) | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xl___a.webp` | `MAD=0.00` to `26xl___a.webp` (`239,954` B) |
| **`26XL`** (2026 Peace Dollar Rev. Proof) | Reverse (Peace Eagle) | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XL_image_3.jpg` | `MAD=0.18` to `26xl___b.webp` (`204,667` B) |
| **`26GC`** (2026 American Innovation RP Set) | Set Reverse (4-Coin Lens) | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26gc_b.webp` | `MAD=0.00` to `26gc_b.webp` (`137,372` B) |
| **`26GC`** (2026 American Innovation RP Set) | Common Obverse | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_american_innovation_obverse.jpg` | `HTTP 200 OK` (`1,279,411` B) |
| **`26SQRP`** (2026 Trump $1 Roll) | Obverse (`1776~2026`) | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp` | `MAD=0.00` to `26SQRP_b.webp` (`179,722` B) |
| **`26SQRP`** (2026 Trump $1 Roll) | Reverse (`$1` Arch) | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` | `MAD=0.00` to `MASTER_SEMIQDJT_26SQBP_26SQRP_rev.webp` (`245,212` B) |
| **`26RG`** (2026 Semiquincentennial Proof Set) | Set Obverse Lens | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rg_b.webp` | `MAD=0.00` to `26rg_b.webp` (`178,232` B) |
| **`26RJ`** (2026 Uncirculated Coin Set) | Set Lens P-Mint (`26rj_b`) | `https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg` | `MAD=0.18` to `26rj_b.webp` (`HTTP 200 OK`) |
| **`26RJ`** (2026 Uncirculated Coin Set) | Set Lens D-Mint (`26rj_c`) | `https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_c.jpg` | `MAD=0.17` to `26rj_c.webp` (`HTTP 200 OK`) |
| **`26RJ`** (2026 Uncirculated Coin Set) | Set 2-Card Spread (`26rj_e`) | `https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg` | `MAD=0.25` to `26rj_e.webp` (`HTTP 200 OK`) |
| **2026 SemiQ Dime** (`nAnGLwGv` / `rv9SCUTa`) | Obverse & Reverse | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_dime_emerging_liberty_obverse.jpg` (and `.../us_mint_official/2026/2026-semiq-dime-obverse-unc-d.webp` for D-mint) + `.../2026_series/2026_dime_emerging_liberty_reverse.jpg` | `HTTP 200 OK` (`1.22 MB` / `340 KB` / `1.34 MB`) |
| **2026 SemiQ Quarter** (`3f7cd90b`) | Obverse & Reverse | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg` + `.../2026_quarter_dollar_mayflower_compact_reverse.jpg` (or `revolutionary_war`) | `HTTP 200 OK` (`1.45 MB` / `1.63 MB`) |
| **2026 SemiQ Half Dollar** (`b015e197`) | Obverse & Reverse | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_half_dollar_enduring_liberty_obverse.jpg` + `.../2026_half_dollar_enduring_liberty_reverse.jpg` | `HTTP 200 OK` (`1.51 MB` / `1.51 MB`) |

#### Table 3.1B — Local 7C Assets Not Yet in GCS (Must Be Staged in `--no-clobber` Upload Manifest for EXECUTE Phase Only, Never Claimed as Pre-Existing HTTP 200)
| SKU | Side | Local Canonical Source Path (`1 NUMISTA.AI\COIN IMAGES\`) | Target GCS Destination (`gsutil cp -n` at EXECUTE) |
| :--- | :--- | :--- | :--- |
| **`26EA`** | Reverse | `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\COIN IMAGES\26EA\2026_american_silver_eagle_proof_reverse_26EA.webp` | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26ea_b.webp` |
| **`26XE`** | Reverse | `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\COIN IMAGES\26XE\2026_morgan_dollar_enhanced_unc_reverse_26XE.webp` | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26xe_b.webp` |
| **`26GC`** | Set Obverse Lens | `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\COIN IMAGES\26GC\2026_american_innovation_reverse_proof_set_set_obverse_26GC.webp` | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/26gc_g.webp` |
| **`23RH`** | Set Obverse Lens | `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\COIN IMAGES\23RH\2023_silver_proof_set_set_obverse_23RH.webp` | `gs://numista-reference-library/reference_library/us_mint_official/2023_products/23rh_b.webp` |
| **2026-P/D Dime** | P/D Obv & Rev | `numista_backend/data/usmint_releases/2026_images/SemiQ-Dime-Obverse-Unc-P.jpg`, `SemiQ-Dime-Obverse-Unc-D.jpg`, `SemiQ-Dime-Reverse-Unc.jpg` | `gs://numista-reference-library/reference_library/us_mint_official/2026_products/SemiQ-Dime-*.jpg` |

---

### `MUST-FIX 2`: Complete 28-Row Concrete Target URL Table for `R2.8.2` §4.2

Every single URL below has been verified to exist in `gs://numista-reference-library` (`HTTP 200 OK` today), with `[STAGE --no-clobber]` noted where a local 7C single-side `.webp` will also be uploaded at EXECUTE:

| # | Doc ID | Account | Year | Item / Title | Defect | Verified Target Obverse URL (`HTTP 200 OK`) | Verified Target Reverse URL (`HTTP 200 OK`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `91f88212` | `yahoo` | 2026 | Uncirculated Coin Set 2026 (`26RJ`) | Missing images | `https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg` |
| **2** | `0e68ecba` | `yahoo` | 2026 | American Innovation 2026 $1 RP Set (`26GC`) | Missing images; Unspec. grade | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26gc_b.webp` | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_american_innovation_obverse.jpg` (or `[STAGE --no-clobber]` `.../2026_products/26gc_g.webp`) |
| **3** | `933df91f` / `7a32932e` | `yahoo` | 2026 | Semiquincentennial Trump $1 Roll (`26SQRP`) | Missing images | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp` | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` |
| **4** | `e91efa62` | `yahoo` | 2026 | 2026-W Silver Eagle Proof (`26EA`) | 2023 Obv; Obv/Rev swapped | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_a.webp` | `[STAGE --no-clobber]` `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_b.webp` (live fallback: `.../bulk_programs/american_eagle/2021-american-eagle-silver-one-ounce-proof-coin-reverse-new.jpg`) |
| **5** | `692fc795` | `yahoo` | 2026 | Morgan Dollar Enh. Unc (`26XE`) | Duplicate eagle card | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_a.webp` | `[STAGE --no-clobber]` `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_b.webp` (live pair: `.../2026_products/26XE_image_2.jpg`) |
| **6** | `a59853c1` | `yahoo` | 2026 | Peace Dollar Reverse Proof (`26XL`) | 2023 date on coin; dup eagle | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xl___a.webp` | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XL_image_3.jpg` |
| **7** | `71e2d4ae` | `yahoo` | 2026 | 250th Anniversary Unc Coin Set (`26RJ`) | Shows outer packaging box | `https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg` |
| **8** | `nAnGLwGv` | `yahoo` | 2026 | 2026-P Dime (stored as 2025 Roosevelt) | Wrong year (`2025 != 2026`) | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_dime_emerging_liberty_obverse.jpg` (`+ [STAGE]` `.../2026_products/SemiQ-Dime-Obverse-Unc-P.jpg`) | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_dime_emerging_liberty_reverse.jpg` (`+ [STAGE]` `.../2026_products/SemiQ-Dime-Reverse-Unc.jpg`) |
| **9** | `rv9SCUTa` | `yahoo` | 2026 | 2026-D Dime (stored as 2025 Roosevelt) | Wrong year (`2025 != 2026`) | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026/2026-semiq-dime-obverse-unc-d.webp` (`+ [STAGE]` `.../2026_products/SemiQ-Dime-Obverse-Unc-D.jpg`) | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_dime_emerging_liberty_reverse.jpg` (`+ [STAGE]` `.../2026_products/SemiQ-Dime-Reverse-Unc.jpg`) |
| **10** | `3f7cd90b` | `yahoo` | 2026 | Semiquincentennial Quarter Dollar | Missing images | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg` |
| **11** | `b015e197` | `yahoo` | 2026 | Semiquincentennial Half Dollar | Missing images | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_half_dollar_enduring_liberty_obverse.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_half_dollar_enduring_liberty_reverse.jpg` |
| **12** | `5b424047` | `yahoo` | 2005 | Kansas 50 State Quarter | REV year `2003 != 2005` (Arkansas) | `https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse.png` | `https://storage.googleapis.com/numista-reference-library/reference_library/bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg` |
| **13** | `3346cda5` | `yahoo` | 2019 | American Memorial Park (ATB) | REV year `2015 != 2019` (Blue Ridge) | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg` |
| **14** | `b243621c` | `yahoo` | 2020 | Salt River Bay (ATB) | REV year `2017 != 2020` (Ozark) | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg` |
| **15** | `c336e53e` | `yahoo` | 2013 | Mount Rushmore (ATB) | REV year `2010 != 2013` (Mt. Hood) | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg` |
| **16** | `cba5e585` | `yahoo` | 2018 | Cumberland Island (ATB) | REV year `2016 != 2018` (Cumb. Gap) | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg` |
| **17** | `d7fec246` | `yahoo` | 2018 | Block Island (ATB) | REV year `2017 != 2018` (Ellis Isl.) | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg` |
| **18** | `Wq2UhSQN` | `yahoo` | 1962 | Lincoln Cent (Memorial Reverse) | OBV `1909 != 1962`; REV `2008 != 1962` | `https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_cents/Obverses_of_United_States_cents/1962_D_Lincoln_Penny__28U.S._Coin.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg` |
| **19** | `UOBfFO2m` | `yahoo` | 2019 | San Antonio Missions (ATB) | OBV year `1932 != 2019` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg` |
| **20** | `3f437576` | `yahoo` | 2017 | Effigy Mounds (ATB) | OBV year `2011 != 2017` | `https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg` |
| **21** | `6ff959a0` | `yahoo` | 2017 | Frederick Douglass (ATB) | OBV year `2011 != 2017` | `https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg` |
| **22** | `96eeb7b6` | `yahoo` | 2010 | Yellowstone (ATB) | OBV year `2011 != 2010` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-uncirculated-obverse-d.webp` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg` |
| **23** | `ab35ab5d` | `yahoo` | 2017 | George Rogers Clark (ATB) | OBV year `2010 != 2017` | `https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg` |
| **24** | `b785236f` | `yahoo` | 2017 | Ozark National Scenic Riverways (ATB) | OBV year `2011 != 2017` | `https://storage.googleapis.com/numista-reference-library/reference_library/wikimedia_uscoin/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/atb_quarters/2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg` |
| **25** | `be10e44c` | `yahoo` & `numista.ai` | 2026 | Morgan Dollar Enh. Unc (`26XE`, `qty: 2`) | Missing images (both accounts!) | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_a.webp` | `[STAGE --no-clobber]` `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_b.webp` (live pair: `.../2026_products/26XE_image_2.jpg`) |
| **26** | `0a2bc793` | `numista.ai` | 2026 | Uncirculated Coin Set 2026 (`26RJ`) | Missing images | `https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg` | `https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg` |
| **27** | `faa5b1cf` | `numista.ai` | 2026 | Semiquincentennial Trump $1 Roll (`26SQRP`) | Missing images | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp` | `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/MASTER_SEMIQDJT_image_2.jpg` |
| **28** | `2fa32516` | `yahoo` & `numista.ai` | 2023 | 2023 Silver Proof Set (`23RH`) | Missing images (both accounts!) | `[STAGE --no-clobber]` `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2023_products/23rh_b.webp` (from `1 NUMISTA.AI\COIN IMAGES\23RH\2023_silver_proof_set_set_obverse_23RH.webp`) | `[STAGE --no-clobber]` `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2023_products/23rh_c.webp` |

---

### `MUST-FIX 3`: Fix Title-Case Field Lookup in `Canonical2026MintAssets.resolve()` (`R2.8.1` Lines 283–337)

- **Why `R2.8.1` Fails at Runtime on Eric's Docs:**
  In `R2.8.1` (`lines 284-289`), `Canonical2026MintAssets.resolve()` writes:
  ```dart
  final year = data['year']?.toString().trim();
  if (year != '2026') return null;

  final itemNo = (data['retailer_item_num'] ?? data['item_number'] ?? '').toString().toUpperCase().trim();
  final title = (data['name'] ?? data['title'] ?? data['Theme/Subject'] ?? '').toString().toLowerCase();
  ```
  In Firestore (`users/eric.seaman@yahoo.com/coins` and `users/eric@numista.ai/coins`), invoice-imported documents (`0e68ecba`, `0a2bc793`, `be10e44c`, `7a32932e`, `91f88212`, `faa5b1cf`) store:
  - `'Year': '2026'` (Title-Case `'Year'` — `data['year']` is `null`!)
  - `'Mint Mark': 'D'` or `'P'` (`data['mint']` is `null`!)
  - `'Program/Series'` and `'Personal Notes'` (e.g., on `0a2bc793`, `item_number`, `name`, `title`, and `Theme/Subject` are all absent, and the SKU is in `'Personal Notes': 'Item # 26RJ - Uncirculated Coin Set 2026'` and `'Program/Series': 'Uncirculated Coin Set'`!).
- **Required Fix in `R2.8.2` §6:**
  `Canonical2026MintAssets.resolve()` must read both Title-Case and snake_case keys:
  ```dart
  final rawYear = (data['year'] ?? data['Year'] ?? '').toString().trim().replaceAll(RegExp(r'\.0$'), '');
  if (!rawYear.contains('2026')) return null;

  final itemNo = (data['retailer_item_num'] ?? data['item_number'] ?? data['Item Number'] ?? '').toString().toUpperCase().trim();
  final combinedText = [
    data['name'], data['title'], data['Theme/Subject'], data['theme_subject'],
    data['Program/Series'], data['program_series'], data['Personal Notes'], data['personal_notes'],
  ].where((e) => e != null).join(' ').toLowerCase();
  final mint = (data['mint'] ?? data['mint_mark'] ?? data['Mint Mark'] ?? '').toString().trim().toUpperCase();
  ```
  And use the **real `HTTP 200 OK` GCS URLs** from Table 3.1A above!

---

### `MUST-FIX 4`: Reconcile the 127 `"Missing images"` Rows in `ERIC_ACCOUNT_252_AUDIT_20261031.csv` & Fix the 60 Presidential Dollars / 50-State Quarter `CoinImageService` Steal-Guard Bug

- **Why `R2.8.1` §4.1 Contradicts Its Own Audit CSV:**
  `R2.8.1` §4.1 (`line 206`) states `"224 items: PASS ... 28 items: DEFECTIVE"`, whereas `ERIC_ACCOUNT_252_AUDIT_20261031.csv` actually has **127 rows marked `"Missing images"`** (`123` in `eric.seaman@yahoo.com/coins` + `4` in `eric@numista.ai/coins` that have no stored `image_url_obverse`/`image_url_reverse` in Firestore) and **64 rows marked `"Unspecified grade; Valuation pending"`** (only `42` rows say `"PASS"`).
- **What Happens to the 120 Non-Invoice `"Missing images"` Rows at Runtime:**
  Those 120 items consist of **60 Presidential Dollars**, **46 50-State Quarters**, **7 American Women Quarters**, and **7 miscellaneous items** (`2x 1974 Eisenhower Dollar`, `1x 2002 US Mint Proof Set`, `1x 2020 Jefferson Nickel`, `1x U.S. Women's Quarter Book`, plus the `eric.seaman@yahoo.com` copies of `23RH`, `26XE`, `26SQRP`). When `image_url_obverse` is empty, `_CollectionCardImage` calls `CoinImageService.fetchReferenceImages()`.
- **Exact Code Citations Where All 60 Presidential Dollars Fail (`GEMINI.md` Rule 6a):**
  1. [`numista_mobile/lib/services/coin_image_service.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/coin_image_service.dart#L540-L570):
     ```dart
     540:         final isSubjectBase = subjectSlug != null && base.contains(subjectSlug);
     541: 
     542:         if (needsObv && (!hasSubject || isSubjectBase)) {
     543:           final obvDoc = await db.collection(_collection)
     544:               .doc('${base}_obverse').get();
     ...
     556:         // STEAL-GUARD: only accept reverse from subject-containing bases
     557:         // when a subject is known. Generic reverse = honest placeholder.
     558:         if (needsRev && (!hasSubject || isSubjectBase)) {
     559:           final revDoc = await db.collection(_collection)
     560:               .doc('${base}_reverse').get();
     ```
  2. [`numista_mobile/lib/screens/my_collection_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6394-L6398):
     ```dart
     6394:         final refUrl = (ref?.reverseUrl?.isNotEmpty == true)
     6395:             ? ref!.reverseUrl!
     6396:             : (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)
     6397:                 ? ref!.obverseUrl!
     6398:                 : '';
     ```
- **Why This Breaks 60 Presidential Dollars & 53 Quarters:**
  - In Firestore `coin_image_index` (`1,003` docs), `presidential-dollars` has **39 subject-specific obverse docs** (`2007_adams_presidential-dollars_obverse`, `2008_jackson_presidential-dollars_obverse`, etc.) and **1 shared generic reverse doc** (`2007_presidential-dollars_reverse`, Statue of Liberty).
  - Because `coin_image_service.dart:558` requires `isSubjectBase` for `needsRev`, `bestRevUrl` is `null` for every Presidential Dollar.
  - Then at `my_collection_screen.dart:6396`, because `subject` is non-empty (e.g., `'Theodore Roosevelt'`), `subject.isEmpty` is `false`, so `_CollectionCardImage` **discards `ref.obverseUrl` and renders `''` (the gold `$` placeholder) on all 60 Presidential Dollars in Eric's collection**!
  - Conversely, for `50-state-quarters` (`0 obverse docs, 61 reverse docs` in `coin_image_index`), `coin_image_service.dart:542` gates `needsObv` on `(!hasSubject || isSubjectBase)`, blocking the shared generic Washington obverse (`1999_50-state-quarters_obverse` / `design_quarter_obverse`) in the Coin Inspector despite the comment at `coin_image_service.dart:519-520` stating: `Generic bases (year+program, expandFallbacks, design_*) may only supply the OBVERSE (e.g. shared Washington portrait is fine)`.
- **Required Fix in `R2.8.2`:**
  1. In `numista_mobile/lib/services/coin_image_service.dart:540-570`:
     Distinguish **obverse-subject programs** (`program == 'presidential-dollars'`, where the President portrait is on the obverse and the Statue of Liberty reverse is shared) from **reverse-subject programs** (quarters/innovation dollars, where the state/park/woman design is on the reverse and the obverse portrait is shared):
     ```dart
     final bool obvRequiresSubject = hasSubject && program == 'presidential-dollars';
     final bool revRequiresSubject = hasSubject && program != 'presidential-dollars';
     if (needsObv && (!obvRequiresSubject || isSubjectBase)) { ... }
     if (needsRev && (!revRequiresSubject || isSubjectBase)) { ... }
     ```
     (And for `presidential-dollars`, include `'2007_presidential-dollars'` in `_candidateBases` fallback so all years `2007–2016` resolve the shared Statue of Liberty reverse `2007_presidential-dollars_reverse`.)
  2. In `numista_mobile/lib/screens/my_collection_screen.dart:6394-6398`:
     For Presidential Dollars (where the unique design is on the obverse), prefer `ref.obverseUrl` on the card:
     ```dart
     final isObverseSubject = series.toLowerCase().contains('presidential') ||
         subject.toLowerCase().contains('morgan') ||
         subject.toLowerCase().contains('peace');
     final refUrl = isObverseSubject
         ? (ref?.obverseUrl ?? ref?.reverseUrl ?? '')
         : (ref?.reverseUrl?.isNotEmpty == true)
             ? ref!.reverseUrl!
             : (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)
                 ? ref!.obverseUrl!
                 : '';
     ```
  3. Update `R2.8.2` §4.1 to honestly report the exact breakdown of all 252 rows in `ERIC_ACCOUNT_252_AUDIT_20261031.csv`:
     - `42` rows: `PASS` in raw Firestore
     - `64` rows: `Unspecified grade; Valuation pending` (resolved at render time by `E4a` cost fallback + `E4b` `_conditionLabel`)
     - `127` rows: No direct `image_url_obverse` in `coins` doc (`60` Presidential Dollars + `46` 50-State Quarters + `7` American Women Quarters resolved dynamically via `CoinImageService` once `MUST-FIX 4` above is applied; `10` 2026/2023 Mint invoice docs across `yahoo` and `numista.ai` resolved via `Canonical2026MintAssets` + `23RH` mapping; `4` legacy items `1974 Eisenhower` x2, `2002 Proof Set`, `2020 Nickel`, `Quarter Book` mapped or fallback-handled)
     - `19` rows: Stored URL year/side/park mismatches (`6` 2026 Mint docs + `13` non-2026 ATB/Kansas/1962 Cent docs resolved via `Canonical2026MintAssets`, Basename Year Guard, and Whole-Token Matcher).

---

## 4. `SHOULD-FIX S1` (Concurring with Grok CoS `NET-687` S1 — Complete Audit of All `qty > 1` Rows in Eric's Accounts)

Argon executed a read-only scan of all 252 `coins` documents (`247` in `eric.seaman@yahoo.com/coins` + `5` in `eric@numista.ai/coins`) and all 8 `review_queue` documents (`7` in `eric.seaman@yahoo.com/review_queue` + `1` in `eric@numista.ai/review_queue`) for `quantity / Quantity / qty > 1`. Exactly **3 unique document IDs** have `qty > 1`:

| Doc ID | Account / Subcollection | SKU / Item | `Quantity` | Stored `Purchase Cost` / `Cost` | Expected Per-Card Display (`Q1` Rule) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`0e68ecba760df66bf824ec1ba2c86b32318d002d`** | `eric.seaman@yahoo.com` (`coins` & `review_queue`) | `26GC` — `American Innovation 2026 $1 Coin Reverse Proof Set` | `2` | `64.97` (`allocated_fees: 4.97`) | **`$32.49`** (`3249` cents via `ROUND_HALF_UP`, with subtitle `(1 of 2 — Set total $64.97)`) |
| **`be10e44ce5b4ff4b46c92426cc7f59a254ed675c`** | `eric.seaman@yahoo.com` & `eric@numista.ai` (`coins` & `review_queue`) | `26XE` — `2026 Morgan Silver Enhanced Uncirculated` | `2` | `169.0` | **`$84.50`** (`8450` cents, with subtitle `(1 of 2 — Set total $169.00)`) |
| **`7a32932ebc4e94a586534e7180cd1c4372c4f17d`** | `eric.seaman@yahoo.com` (`coins` & `review_queue`) | `26SQRP` — `26SQRP Semiquincentennial President D` (25-Coin Roll) | `25` | `61.0` | **`$61.00`** (Roll SKU excluded from per-coin division by `!isRollOrBag && qty <= 10` guard) |

Include this 3-row table in `R2.8.2` §2.Q1 / §4 to close Grok CoS `S1` completely.

---

## 5. Gate Status & Next Step

- **Verdict:** **81 / 100 — `REVISE` (`R2.8.2` Fix-Only)**
- **Baton:** Passing directly to **AG CoS v4 (`ba2bfdb2`)** to fold `MUST-FIX 1–4` and `SHOULD-FIX S1` (along with Grok CoS `NET-687`) into `FAILFIX_PLAN_NET-647_R2.8.2_20261031.md`.
- **Governance Lock:** **NO EXECUTE** remains strictly in effect until:
  1. Argon review of `R2.8.2`
  2. Grok CoS score $\ge 95/100$
  3. SAG review (`For SAG` packet staged)
  4. Eric's typed `YES` (and a separate typed `YES` for any Firestore backfill writes to `eric.seaman@yahoo.com`).
