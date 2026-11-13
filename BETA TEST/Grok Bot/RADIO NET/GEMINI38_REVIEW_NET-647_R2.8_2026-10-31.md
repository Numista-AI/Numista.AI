# GEMINI 3.8 (ARGON) TECHNICAL REVIEW — `FAILFIX_PLAN_NET-647_R2.8_20261031.md`
- **Track:** `NET-647` / `NET-681` / `NET-681A`–`NET-681E` / `NET-683` / `NET-684` (Mint FAIL-FIX Plan R2.8 — Root-Cause & Eric Whole-Account 100% Remediation + 39-Row Tracker Coverage)
- **Plan Under Review:** `FAILFIX_PLAN_NET-647_R2.8_20261031.md` (Updated 2026-10-31 20:33 ET with §8 39-Item Tracker Coverage Matrix)
- **Reviewer:** `Argon` (`Numista.Ai Argon` — `31035602-8cdd-403f-8b72-7280605f5100`)
- **Timestamp:** `2026-10-31T20:48:00-04:00`
- **Role & Governance Compliance:** **DOCS-ONLY (`NO EXECUTE`)** — Zero source code edits, zero git commits of code, zero deploys, zero GCS/Firestore writes. `origin/main` locked at `9f04550a`; `origin/dev` frozen at `9b55f3d9`; Stripe OFF; `V3Tees` untouched. All `file:line` citations include verbatim code lines checked per `GEMINI.md` Rule 6(a).

---

## 1. Executive Summary & Score

- **Argon Score:** **89 / 100 — REVISE (`R2.8.1` Fix-Only Plan Precision Pass Required Before ≥95 Gate)**
- **What R2.8 Gets Right:**
  1. **Root-Cause Answers (`Q1–Q5`):** Correctly identifies why R2.6 (`33076f6a`) failed Field Tester (`FT_RESULT_NET673_R2.6_33076f6a_FAIL.md`): the R2.6 Firestore backfill was run in `--dry-run` only (0 writes), leaving existing `grokbot@numista.ai/review_queue` docs with `unit_cost_cents: null`, `image_url_obverse: null`, and `26rj_a.jpg` (packaging cover), while `review_hub_screen.dart` lacked a read-time client fallback for existing un-enriched documents. Also properly verifies `Q5` (CORS on `gs://numista-reference-library` allows `*` and `https://numista-vault--p7-gate-8avtpz22.web.app`, returning `HTTP 200 OK`).
  2. **39-Row Beta Issue Tracker Matrix (`NET-681E`):** Section 8 accounts for all 39 rows of `ERIC_BETA_ISSUE_TRACKER_20261031.csv` with display-first ordering and justified defers for `B26-4` (Morgan chat PDF OCR pipeline) and `B26-5` (Add Coins IA overhaul).
  3. **3-Tier Image Source Priority & Two-Gate Backfill Governance (`NET-681D`):** Properly locks Tier 1 (`Images from US MInt`) $\rightarrow$ Tier 2 (`gs://numista-reference-library`) $\rightarrow$ Tier 3 (`COIN IMAGES` / Microscope) and holds `--apply` on `eric.seaman@yahoo.com` for Eric's separate typed YES.

- **Why R2.8 Scores `89/100` (6 Concrete Code/Data Bugs That Would Cause Field Tester FAIL on Eric's Real Account if Executed As-Written):**
  Argon performed a read-only inspection of all 252 Firestore documents in `users/eric.seaman@yahoo.com` and `users/eric@numista.ai`, downloaded and visually inspected the stored GCS assets on `e91efa62` (`26EA`), and checked every proposed Dart code change against `p7-v8.9` (`33076f6a`). We caught **6 critical implementation defects**:
  1. **`MUST-FIX 1` (`NET-681D` Whole-Account Table Incomplete — Omitted 13 Non-2026 Wrong-Coin/Wrong-Year Items in `eric.seaman@yahoo.com`, Including `"Kansas" -> "Arkansas"` & 5 Wrong ATB Park Reverses):** R2.8 §4 (lines 275–288) only tabulates **11 items** (the 2026 subset) out of 252 and omits the required `Valuation`, `Grade`, and `Title` columns. Argon's read-only audit of all 252 items uncovered **13 non-2026 items with wrong-year/wrong-coin URLs**, including **7 severe wrong-design matches** (`2005 Kansas` showing `2003 Arkansas`; `2019 American Memorial Park` showing `2015 Blue Ridge Parkway`; `2020 Salt River Bay` showing `2017 Ozark Riverways`; `2013 Mount Rushmore` showing `2010 Mount Hood`; `2018 Cumberland Island` showing `2016 Cumberland Gap`; `2018 Block Island` showing `2017 Ellis Island`; `1962 Lincoln Cent` showing `1909 Wheat Cent`).
  2. **`MUST-FIX 2` (Client-Side Catalog Fallback in R2.8 §6 Line 322 Only Triggers When `image_url_obverse` is `null` — Will NOT Fix `26XL`, `26RJ`, `26EA`, or `2026 Dimes` Without Backfill, and Filename-Only Side/Year Guards Fail on `26EA` & `26XL`):**
     - In Eric's Firestore collection, `a59853c1` (`26XL`), `71e2d4ae` (`26RJ`), `e91efa62` (`26EA`), `nAnGLwGv` (`2026-P Dime`), and `rv9SCUTa` (`2026-D Dime`) have **non-null** `image_url_obverse`/`image_url_reverse` fields pointing to wrong/legacy URLs! If the client-side catalog fallback only runs when `image_url_obverse` is `null`, **5 of the 9 defective 2026 items in Eric's account will still fail on `p7-gate`!**
     - Furthermore, Argon downloaded and visually inspected `e91efa62`'s GCS files (`American Eagle 2023 One Ounce Silver Proof Coin Obverse.jpg` and `...Reverse.jpg`): **the GCS files themselves have swapped pixel contents** (`...Obverse.jpg` is the Landing Eagle reverse; `...Reverse.jpg` is the 2023 Walking Liberty obverse!). Thus R2.8 §5's filename-only Side Guard (`'obverse' in url` / `'reverse' in url`) **cannot detect the swap on `e91efa62`**, and R2.8 §5's filename-only Year Guard **cannot detect that `Peace-Dollar-Reverse-Proof-Obverse.jpg` on `a59853c1` (`26XL`) shows `2023` on the coin face**!
  3. **`MUST-FIX 3` (`Q1` Non-Existent Code Quote & Roll `$2.44` Division Regression Trap in `review_hub_screen.dart:2040-2058`):** R2.8 §2 Q1 (lines 36–46) quotes code that does not exist in `review_hub_screen.dart:2040-2058`, uses `item[...]` instead of `data[...]`, and proposes dividing `rawCost / cleanQty` whenever `unit_cost_cents` is null — which would divide an already-per-unit `Purchase Cost` and must use integer-cent `ROUND_HALF_UP` (`((rawCost * 100) / cleanQty).round() / 100.0`) so `$64.97 / 2 = $32.49` (`3249` cents).
  4. **`MUST-FIX 4` (`E4a` Valuation Fallback Key-Case Mismatch in `my_collection_screen.dart:3016-3022`):** R2.8 §3 E4a (line 206) checks lowercase `m['cost'] ?? m['purchase_price']`, whereas Eric's actual Firestore docs (`0e68ecba`, `91f88212`, `be10e44c`, `a59853c1`, `e91efa62`) store Title-Case `'Purchase Cost'` and `'Cost'` (`_F.cost`), or nested `m['paper_trail']['purchase_price']`, often formatted with `'\$'` (`"\$2.00"`). Lowercase-only lookup will still render `'Valuation Pending'` on `0e68ecba`, `91f88212`, and `be10e44c`!
  5. **`MUST-FIX 5` (`E4b` Grade Helper Name in `my_collection_screen.dart:1042` & `3000`):** R2.8 §3 E4b (line 209) calls non-existent `_normalizeCondition(condition)`; the existing static helper in `my_collection_screen.dart:1042` is `_conditionLabel(String raw)`, which already maps `"Unspecified / Raw"` $\rightarrow$ `"Raw"`.
  6. **`MUST-FIX 6` (Exact Line Citation for `_CollectionCardImage` at `my_collection_screen.dart:6357-6364` & Year-Guard Regex False Positives on UUIDs/Dimensions):** R2.8 cites line `3063` instead of `6358-6360`, and `scratch/audit_eric_whole_account.py` matched `2000` inside `2000x2000.jpg` dimensions and misses `_`-delimited years (`\b` treats `_` as a word char).

---

## 2. Verbatim Code Citations & Detailed Audit Findings (Per `GEMINI.md` Rule 6a)

### Finding 1 (`MUST-FIX 1`): Complete Read-Only Audit of All Non-2026 Wrong-Coin / Wrong-Year Items in `users/eric.seaman@yahoo.com/coins` (`NET-681D`)

`WAKE_AG-COS-V4_NET-681D_AMEND_R2.8_ERIC-WHOLE-ACCOUNT_20261031-2005.md` (lines 10–16) mandated:
> *"A read-only audit table of EVERY coin and currency item in Eric's account (`eric.seaman@yahoo.com` / `eric@numista.ai`). For each item, record: the card image and both Inspector sides; the year that is visible on each image, compared with the coin's year; whether the side label is correct; whether the card shows the side unique to that coin; valuation, grade and title; for sets, which image is shown."*

In `scratch/audit_eric_whole_account.py:87-104`, AG CoS v4 only printed `mismatched_years[:10]` to stdout and only pasted the 11 items from 2026 into R2.8 §4 (lines 275–288):
```python
# Verbatim from scratch/audit_eric_whole_account.py:87-104
mismatched_years = [r for r in audit_results if not r['obv_year_match'] or not r['rev_year_match']]
side_swaps = [r for r in audit_results if r['side_swap']]
missing_images = [r for r in audit_results if not r['obv'] and not r['rev']]
unspecified_grades = [r for r in audit_results if 'unspecified' in r['grade'].lower()]
pending_vals = [r for r in audit_results if r['val'] == 'Pending']
...
print("\n--- SAMPLE YEAR MISMATCHES ---")
for r in mismatched_years[:10]:
    print(f"ID: {r['id']} | Year: {r['year']} | Title: {r['title']}")
```

Argon executed a complete read-only inspection of all 252 docs in `users/eric.seaman@yahoo.com` and `users/eric@numista.ai`. Below are the **13 additional non-2026 items in `users/eric.seaman@yahoo.com/coins`** with wrong-coin or wrong-year stored URLs that R2.8 §4 omitted:

| # | Doc ID (`eric.seaman@yahoo.com`) | Coin Year & Series | Stored `Theme/Subject` | Stored `image_url_obverse` | Stored `image_url_reverse` | Defect Category | Required R2.8.1 Fix |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **12** | `5b424047-77e0-496e-a513-6ef180b515a6` | `2005` 50 State Quarters | `Kansas` | `.../50_State_and_Territories_quarter_obverse__28Denver_29.jpg` | `.../2003-50-state-quarters-coin-arkansas-uncirculated-reverse.jpg` | **WRONG STATE & YEAR (`2003 Arkansas` on `2005 Kansas` due to substring `"kansas"` in `"arkansas"`)** | Suppress wrong-year/wrong-state reverse via Year/Subject Guard; resolve `2005 Kansas` reverse |
| **13** | `3346cda5-5935-4303-bf62-de43041f3175` | `2019` ATB Quarters | `American Memorial Park (Northern Mariana Islands)` | `.../2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | `.../2015-america-the-beautiful-quarters-coin-blue-ridge-parkway-north-carolina-uncirculated-reverse.jpg` | **WRONG PARK & YEAR (`2015 Blue Ridge Parkway NC` on `2019 American Memorial Park`)** | Suppress `2015` reverse via Year Guard; resolve `2019 American Memorial Park` reverse |
| **14** | `b243621c-5a35-45f0-84bf-8786eb1547f9` | `2020` ATB Quarters | `Salt River Bay (U.S. Virgin Islands)` | `.../2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | `.../2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg` | **WRONG PARK & YEAR (`2017 Ozark Riverways MO` on `2020 Salt River Bay` due to `"river"` token)** | Suppress `2017` reverse via Year Guard; resolve `2020 Salt River Bay` reverse |
| **15** | `c336e53e-4105-44bd-8c08-f30ae0328467` | `2013` ATB Quarters | `Mount Rushmore (South Dakota)` | `.../2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg` | `.../2010-america-the-beautiful-quarters-coin-mount-hood-oregon-uncirculated-reverse.jpg` | **WRONG PARK & YEAR (`2010 Mount Hood OR` on `2013 Mount Rushmore SD` due to `"mount"` token)** | Suppress `2010` reverse via Year Guard; resolve `2013 Mount Rushmore` reverse |
| **16** | `cba5e585-758f-4b10-be7a-1a59a1f4b2e6` | `2018` ATB Quarters | `Cumberland Island (Georgia)` | `.../2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | `.../2016-america-the-beautiful-quarters-coin-cumberland-gap-kentucky-uncirculated-reverse.jpg` | **WRONG PARK & YEAR (`2016 Cumberland Gap KY` on `2018 Cumberland Island GA` due to `"cumberland"` token)** | Suppress `2016` reverse via Year Guard; resolve `2018 Cumberland Island` reverse |
| **17** | `d7fec246-983f-40de-8b58-854f59460bce` | `2018` ATB Quarters | `Block Island (Rhode Island)` | `.../2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg` | `.../2017-america-the-beautiful-quarters-coin-ellis-island-new-jersey-uncirculated-reverse.jpg` | **WRONG PARK & YEAR (`2017 Ellis Island NJ` on `2018 Block Island RI` due to `"island"` token)** | Suppress `2017` reverse via Year Guard; resolve `2018 Block Island` reverse |
| **18** | `Wq2UhSQNs67u34VFJDaI` | `1962` Lincoln Cent | `Abraham Lincoln` | `.../NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg` (`1909` Wheat) | `.../2008-lincoln-one-cent-reverse-2000x2000.jpg` (`2008`) | **WRONG YEAR & TYPE (`1909 Wheat Cent` obverse on `1962 Memorial Cent`)** | Suppress `1909`/`2008` via Year Guard |
| **19** | `UOBfFO2mqgLg86NSsyss` | `2019` ATB Quarters | `San Antonio Missions` | `.../1932-george-washington-quarter-obverse.jpg` (`1932` dated obverse) | `.../2019-...-san-antonio-missions-texas-uncirculated-reverse.jpg` (`2019` PASS) | **WRONG OBVERSE YEAR (`1932` dated obverse on `2019` ATB quarter in Inspector)** | Suppress `1932` obverse via Year Guard; use ATB quarter obverse |
| **20–24** | `3f437576...` (`2017` Effigy Mounds), `6ff959a0...` (`2017` Frederick Douglass), `96eeb7b6...` (`2010` Yellowstone), `ab35ab5d...` (`2017` George Rogers Clark), `b785236f...` (`2017` Ozark Riverways) | `2010` / `2017` ATB Quarters | Correct park reverse (`REV` matches coin year & park) | `.../2011-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg` (or `2010-...-obverse-d.webp`) | Correct `2017` / `2010` park reverse | **Filename year mismatch on shared undated ATB obverse (`ab35ab5d` also check P/D mint mark)** | Remap obverse to matching year/mint ATB obverse or allow undated series obverse with matching mint mark |

Also note: in `eric@numista.ai/coins`, there are **3 additional 2026 docs** (`0a2bc793-8d62-47c3-88cd-7a5b9be434ba` `2026 Uncirculated Coin Set`, `be10e44ce5b4ff4b46c92426cc7f59a254ed675c` `26XE`, and `faa5b1cf-7fd1-4fe6-90e8-51c2eaa7122c` `2026 Semiquincentennial President`) plus `2fa325166682b70aa0d64da45786c94aa4742d21` (`2023 Silver Proof Set 23RH`) with `OBV=None, REV=None`. All of these must be listed in §4 (and a full 252-row companion CSV `ERIC_ACCOUNT_252_AUDIT_20261031.csv` generated in `RADIO NET/`).

---

### Finding 2 (`MUST-FIX 2`): Client-Side Catalog Override Must Trigger on Legacy/Wrong Stored Reference URLs, Not Only When `image_url_obverse` is `null` (`R2.8 §6 Line 322` & `E7` Swapped-File Discovery)

In `_CollectionCardImage` ([`my_collection_screen.dart:6357-6364`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6357-L6364)) and `_showCoinInspectorDialog` ([`my_collection_screen.dart:3467-3496`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3467-L3496)):
```dart
// Verbatim from numista_mobile/lib/screens/my_collection_screen.dart:6357-6364
  @override
  Widget build(BuildContext context) {
    final obv = _cleanUrl(data[_F.imageObverse]);
    final rev = _cleanUrl(data[_F.imageReverse]);
    final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)

    if (directUrl.isNotEmpty) {
      return _buildCoinImage(directUrl);
    }
```
```dart
// Verbatim from numista_mobile/lib/screens/my_collection_screen.dart:3467-3469 & 3490-3496
    final hasUserPhoto = data[_F.imageObverse]?.toString().startsWith('http') == true
        || data[_F.imageReverse]?.toString().startsWith('http') == true;
    final refFuture = hasUserPhoto
        ? null
        : CoinImageService.fetchReferenceImages(
...
          final obvUrl   = data[_F.imageObverse]?.toString() ?? '';
          final revUrl   = data[_F.imageReverse]?.toString() ?? '';
          final hasObv   = obvUrl.isNotEmpty && obvUrl.startsWith('http');
          final hasRev   = revUrl.isNotEmpty && revUrl.startsWith('http');
          final showObv  = _vaultShowObverse || (!hasRev && hasObv);
          final activeUrl = showObv ? obvUrl : revUrl;
          final hasActive = showObv ? hasObv : hasRev;
```

**Why R2.8 §6 Line 322 & §5 Lines 304–313 Will Fail Without This Fix:**
1. R2.8 §6 line 322 states: *"If `image_url_obverse` or `image_url_reverse` is missing/null, the client matches `retailer_item_num`, `item_number`, or program title against the canonical 2026 Mint catalog map and renders the canonical GCS asset."*
2. However, in `users/eric.seaman@yahoo.com/coins`, **5 of the 9 defective 2026 docs have NON-NULL `image_url_obverse` and `image_url_reverse`**:
   - `71e2d4ae92bc4312a4198a3a0cc21fcb` (`26RJ`): `image_url_obverse = '.../26rj_a.jpg'` (outer box), `image_url_reverse = '.../26rj_e.jpg'`.
   - `a59853c1-b72b-414d-8b8e-de6813c29996` (`26XL`): `image_url_obverse = '.../Peace-Dollar-Reverse-Proof-Obverse.jpg'` (visually displays **`2023`** on the coin face, with **no year in the filename**!), `image_url_reverse = '.../Peace-Dollar-Reverse-Proof-Reverse.jpg'`.
   - `e91efa62-4e8d-4920-a928-c0c97659bcdc` (`26EA`):
     - `image_url_obverse = 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/American%20Eagle%202023%20One%20Ounce%20Silver%20Proof%20Coin%20Obverse.jpg'` (54,062 bytes, MD5 `89de4c4b1cd896b5a9eab5f7ed18da50`) — **Argon visual inspection confirmed this file is actually the Landing Eagle REVERSE!**
     - `image_url_reverse = 'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/American%20Eagle%202023%20One%20Ounce%20Silver%20Proof%20Coin%20Reverse.jpg'` (54,902 bytes, MD5 `96f680d4ad85e37b136acaa205303041`) — **Argon visual inspection confirmed this file is actually the 2023 Walking Liberty OBVERSE!**
   - `nAnGLwGvhfIOibf6kIft` (`2026-P Dime`) & `rv9SCUTahBuqJkkiJyga` (`2026-D Dime`): `image_url_obverse = '.../2025-roosevelt-dime-uncirculated-obverse-philadelphia.jpg'` (and `-denver.jpg`), `image_url_reverse = '.../2025-roosevelt-dime-uncirculated-reverse.jpg'`.
3. **Required R2.8.1 Fix:**
   - Define a shared helper ` Canonical2026MintAssets.resolve(Map<String, dynamic> data)` used by `_CollectionCardImage`, `_showCoinInspectorDialog`, `_buildCoinVaultGallery`, and `ReviewHubScreen`.
   - Whenever `year == '2026'` and the item matches a 2026 US Mint catalog SKU (`26EA, 26XE, 26XL, 26XH, 26XM, 26XF, 26RG, 26RJ, 26SQRP, 26GC`) or 2026 circulating change (`2026-P Dime`, `2026-D Dime`), **override** `image_url_obverse` and `image_url_reverse` with the canonical 2026 US Mint assets **unless** the stored URL is a genuine user/microscope upload (`/users/` or `/microscope/`).
   - Also note: for `nAnGLwGv` and `rv9SCUTa` (`2026-P` and `2026-D` Dimes), R2.8 §3 E6 (lines 239–241) references `SemiQ-Dime-Obverse-Unc-P.jpg`, `SemiQ-Dime-Obverse-Unc-D.jpg`, and `SemiQ-Dime-Reverse-Unc.jpg` from `1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\Images from US MInt\`, which are **not yet in `gs://numista-reference-library/reference_library/us_mint_official/2026_products/`**. R2.8.1 must explicitly list those 3 files (with MD5/SHA256) in the `EXECUTE`-time `--no-clobber` upload table (or bundle them as Flutter assets) so they do not 404 on `p7-gate`!

---

### Finding 3 (`MUST-FIX 3`): `Q1` Code Citation & Roll `$2.44` Regression Guard in [`review_hub_screen.dart:2040-2058`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/review_hub_screen.dart#L2040-L2058)

R2.8 §2 Q1 (lines 36–46) quotes non-existent code (`final rawCost = (item['unit_cost_cents'] != null) ...`). Here is the actual verbatim code in [`numista_mobile/lib/screens/review_hub_screen.dart:2040-2058`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/review_hub_screen.dart#L2040-L2058) on `p7-v8.9` (`33076f6a`):
```dart
// Verbatim from numista_mobile/lib/screens/review_hub_screen.dart:2040-2058
    final rawQty = data['Quantity'] ?? data['quantity'] ?? 1;
    final cleanQty = (rawQty is num) ? rawQty.toInt() : (int.tryParse(rawQty.toString()) ?? 1);
    final rawCost = data['Purchase Cost'] ?? data['Cost'];
    final feeVal = data['allocated_fees'] ?? data['shipping_fee'] ?? 0;
    final numFee = (feeVal is num) ? feeVal.toDouble() : (double.tryParse(feeVal.toString()) ?? 0.0);

    String costLine = 'Cost: —';
    if (rawCost != null && rawCost.toString().isNotEmpty && rawCost.toString() != '—') {
      final numCost = (rawCost is num) ? rawCost.toDouble() : double.tryParse(rawCost.toString().replaceAll(r'$', '').replaceAll(',', ''));
      if (numCost != null) {
        if (cleanQty > 1) {
          costLine = '${formatCurrency(numCost)} each';
        } else {
          costLine = 'Cost: ${formatCurrency(numCost)}';
        }
      } else {
        costLine = 'Cost: $rawCost';
      }
    }
```

**Required R2.8.1 Fix for `review_hub_screen.dart:2040-2058`:**
1. Prefer `data['unit_cost_cents']` (divided by `100.0`) or `data['unit_cost']` when present.
2. When `cleanQty > 1` and both `unit_cost_cents` and `unit_cost` are `null`, only divide `numCost` by `cleanQty` when `numCost` represents the multi-unit line total (e.g., `data['line_total_cents'] == null` or `(numCost * 100).round() == data['line_total_cents']` or `numCost > 10.0`), using integer-cent `ROUND_HALF_UP`:
   ```dart
   final unitCostCents = (data['unit_cost_cents'] is num)
       ? (data['unit_cost_cents'] as num).toInt()
       : (data['unit_cost'] != null)
           ? ((double.tryParse(data['unit_cost'].toString()) ?? 0.0) * 100).round()
           : (cleanQty > 1 && numCost != null)
               ? ((numCost * 100.0) / cleanQty).round()
               : (numCost != null ? (numCost * 100.0).round() : null);
   ```
   This guarantees `169.00 / 2 -> 8450 cents ($84.50 each)`, `64.97 / 2 -> 3249 cents ($32.49 each)`, and preserves `26SQRP` (`unit_cost: 2.44 -> 244 cents ($2.44 each)`).

---

### Finding 4 (`MUST-FIX 4`): `E4a` Valuation Fallback Key-Case Mismatch in [`my_collection_screen.dart:3016-3022`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3016-L3022)

Here is the verbatim code in [`numista_mobile/lib/screens/my_collection_screen.dart:3016-3022`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3016-L3022):
```dart
// Verbatim from numista_mobile/lib/screens/my_collection_screen.dart:3016-3022
        final cpgRetail = (m['cpgRetail'] as num?)?.toDouble() ?? 0.0;
        final aiValue = m[_F.aiValue]?.toString() ?? '';
        final hasRetail = cpgRetail > 0;
        final hasAi = aiValue.isNotEmpty && aiValue != '—' && aiValue != '0' && aiValue != '0.0';
        final valueText = hasRetail
            ? '\$${cpgRetail.toStringAsFixed(2)}'
            : (hasAi ? aiValue : 'Valuation Pending');
```

**Why R2.8 §3 E4a (line 206) Fails on Eric's Real Docs:**
- R2.8 line 206 proposes:
  `final costVal = _parseNumber(m['current_value'] ?? m['valuation'] ?? m['cost'] ?? m['purchase_price'] ?? m['unit_cost']);`
- In `users/eric.seaman@yahoo.com/coins`:
  - Doc `0e68ecba...` (`26GC`): has `'Purchase Cost': 64.97, 'Cost': 64.97` (Title-Case!), and `'cost'` is **absent (`None`)**.
  - Doc `91f88212...` (`26RJ`): has `'Purchase Cost': 134.45, 'Cost': 134.45` (Title-Case!), and `'cost'` is **absent (`None`)**.
  - Doc `be10e44c...` (`26XE`): has `'Purchase Cost': 169.0, 'Cost': 169.0` (Title-Case!), and `'cost'` is **absent (`None`)**.
- **Required R2.8.1 Fix:** Check Title-Case and snake_case keys plus `paper_trail`:
  ```dart
  final rawFallbackVal = m['current_value'] ??
      m['valuation'] ??
      m['estimated_value'] ??
      m['ai_est_value'] ??
      m['unit_cost'] ??
      m['Purchase Cost'] ??
      m[_F.cost] ??
      m['cost'] ??
      m['purchase_price'] ??
      (m['paper_trail'] is Map ? m['paper_trail']['purchase_price'] : null);
  ```
  and parse via `double.tryParse(rawFallbackVal.toString().replaceAll(r'$', '').replaceAll(',', '').trim())`.

---

### Finding 5 (`MUST-FIX 5`): `E4b` Grade Normalization Helper in [`my_collection_screen.dart:1042-1058`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L1042-L1058) & [`3000`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3000)

Here is the verbatim code in [`numista_mobile/lib/screens/my_collection_screen.dart:1042-1058`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L1042-L1058) and [`3000-3002`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3000-L3002):
```dart
// Verbatim from numista_mobile/lib/screens/my_collection_screen.dart:1042-1058
  static String _conditionLabel(String raw) {
    if (raw.isEmpty || raw == 'null') return '';

    if (raw.contains('/')) {
      final parts = raw.split('/').map((s) => s.trim()).toList();
      final left = parts[0].toLowerCase();
      final right = parts.length > 1 ? parts[1].trim() : '';

      if (left.contains('unspecified')) {
        if (right.isEmpty ||
            right.toLowerCase() == 'raw' ||
            right.toLowerCase() == 'ungraded' ||
            right.toLowerCase() == 'unspecified') {
          return 'Raw';
        }
        return _formatConditionToken(right);
      }
```
```dart
// Verbatim from numista_mobile/lib/screens/my_collection_screen.dart:3000-3002
        final condition = _rowField(m, 'condition', _F.condition);
        final certNo = _rowField(m, 'cert_number', _F.gradingCert);
        final gradingSvc = _rowField(m, 'grading_service', _F.gradingService);
```

- R2.8 line 209 references `_normalizeCondition(condition)`, which does not exist in `my_collection_screen.dart`. Instead, call the existing static method `_conditionLabel(_rowField(m, 'condition', _F.condition))` at line 3000 (and in the Inspector badge if rendered raw), which already transforms `"Unspecified / Raw"` $\rightarrow$ `"Raw"`.

---

### Finding 6 (`MUST-FIX 6`): Year-Guard Regex Scope & `_CollectionCardImage` Line Citation ([`my_collection_screen.dart:6357-6364`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6357-L6364))

1. Update R2.8 §3 E1 line 142 citation from `my_collection_screen.dart:3063` to `my_collection_screen.dart:6358-6360` (`_CollectionCardImage.build`).
2. In R2.8 §5 (`Year Guard`), specify that year extraction:
   - Operates ONLY on the **decoded filename basename** (`Uri.decodeFull(url.split('?').first.split('/').last)`), never on the full URL path (which contains UUIDs and timestamps).
   - Strips pixel dimension patterns (`\d{3,4}x\d{3,4}`, e.g. `2000x2000`) before matching `(?:^|[^0-9])(1[789]\d\d|20\d\d)(?:$|[^0-9])` (note: do not use `\b` because `_` is a word character in regex and fails on `2026_semiquincentennial_...`).
   - Exempts user/microscope uploads (`/users/` and `/microscope/`).

---

## 3. Scoring Breakdown & Actionable Checklist for `R2.8.1`

| Category | Max | Score | Notes |
| :--- | :-: | :-: | :--- |
| **Root-Cause Diagnosis (`Q1–Q5`)** | 20 | 18 | Accurate root causes; `-2` for fabricated code snippet & missing `unit_cost` guard in `Q1` |
| **Eric 2026 Account Fixes (`E1–E7`)** | 25 | 21 | `-4` because client fallback in §6 only triggers when URL is `null` (misses `26XL`, `26RJ`, `26EA`, `2026 Dimes`), plus `E4a` Title-Case `'Purchase Cost'`/`'Cost'` bug & `E4b` `_conditionLabel` name |
| **Whole-Account 252-Item Audit (`NET-681D`)** | 25 | 20 | `-5` because §4 table only lists 11 of 252 items and omits the 13 non-2026 wrong-state/wrong-year items (`Kansas->Arkansas`, 5 ATB park steals, `1962->1909` cent, `2019->1932` quarter) |
| **39-Row Issue Tracker Matrix (`NET-681E`)** | 20 | 20 | Complete 39/39 coverage matrix with display-first priority and justified defers for `B26-4` & `B26-5` |
| **Governance, Locks & Two-Gate Safety** | 10 | 10 | 100% compliant (docs-only, `main` `9f04550a`, `dev` `9b55f3d9`, Stripe OFF, separate YES for Firestore backfill) |
| **TOTAL** | **100** | **89** | **REVISE (`R2.8.1` Fix-Only Pass Required)** |

### Checklist for `R2.8.1` to Reach `≥ 95/100 GO`:
1. **`[MUST-FIX 1]`** Expand §4 to include the **13 non-2026 wrong-year/wrong-coin items** in `users/eric.seaman@yahoo.com/coins` (Items 12–24 in table above: `2005 Kansas`, `2019 American Memorial Park`, `2020 Salt River Bay`, `2013 Mount Rushmore`, `2018 Cumberland Island`, `2018 Block Island`, `1962 Lincoln Cent`, `2019 San Antonio Missions`, and the 5 ATB obverse year mismatches) + the 4 items in `eric@numista.ai/coins`, add `Valuation`, `Grade`, and `Title` columns, and generate the companion 252-row CSV (`ERIC_ACCOUNT_252_AUDIT_20261031.csv`) in `RADIO NET/`.
2. **`[MUST-FIX 2]`** Update §6 Client-Side Catalog Fallback so that for 2026 US Mint catalog coins/sets/dimes, the canonical 2026 asset map **overrides** stale/wrong reference URLs (`26rj_a.jpg`, `Peace-Dollar-Reverse-Proof-Obverse.jpg`, `American Eagle 2023...`, `2025-roosevelt-dime...`), not only `null` URLs; and list the 3 Semiquincentennial Dime images (`SemiQ-Dime-Obverse-Unc-P.jpg`, `SemiQ-Dime-Obverse-Unc-D.jpg`, `SemiQ-Dime-Reverse-Unc.jpg`) in the `EXECUTE`-time `--no-clobber` GCS upload manifest.
3. **`[MUST-FIX 3]`** Replace the fabricated `Q1` code block with the verbatim `review_hub_screen.dart:2040-2058` code and guard `rawCost / cleanQty` with `data['unit_cost_cents']` / `data['unit_cost']` priority and `ROUND_HALF_UP` integer cents.
4. **`[MUST-FIX 4]`** Include Title-Case `m['Purchase Cost']` and `m[_F.cost]` (`'Cost'`) + `m['paper_trail']['purchase_price']` in the `E4a` valuation fallback at `my_collection_screen.dart:3016-3022`.
5. **`[MUST-FIX 5]`** Use existing `_conditionLabel(...)` (`my_collection_screen.dart:1042`) at `my_collection_screen.dart:3000` for `E4b`.
6. **`[MUST-FIX 6]`** Cite `my_collection_screen.dart:6358-6360` (`_CollectionCardImage.build`) for `E1` and scope the §5 Year Guard regex `(?:^|[^0-9])(1[789]\d\d|20\d\d)(?:$|[^0-9])` strictly to the decoded filename basename (excluding `\d{3,4}x\d{3,4}` dimensions and `/users/` or `/microscope/` personal scans).
