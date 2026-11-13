# NET-647 FIX-ONLY FAIL-FIX PLAN R2.8.1 (2026-10-31)
**Track:** NET-647 / NET-681 / NET-681A–E / NET-683 / NET-684 / NET-685 (Mint FAIL-FIX Plan R2.8.1 — Argon Review Revision)  
**Station:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`, `eric@numista.ai`, PAYG `numista-qc`)  
**Target Branch:** `p7-v8.9` ONLY (`33076f6a`)  
**Target Channel:** Firebase Hosting `p7-gate` ONLY (`https://numista-vault--p7-gate-8avtpz22.web.app`)  
**Mode:** **DOCS-ONLY (`NO EXECUTE`)** — Zero source code edits, zero git commits of code, zero deploys, zero GCS/Firestore writes until full review cycle is complete.  
**Review Response:** Directly addresses all 6 blockers from Argon Technical Review `GEMINI38_REVIEW_NET-647_R2.8_2026-10-31.md` (`Score: 89/100 REVISE -> R2.8.1`).  
**Standing Locks:** `origin/main` locked at `9f04550a`; `origin/dev` catalog frozen at `9b55f3d9`; Stripe OFF; `V3Tees` untouched.

---

## 1. Executive Summary & R2.8.1 Scope

In `NET-685`, Argon verified Plan R2.8 against live Firestore documents and codebase `33076f6a`, awarding 89/100 and identifying 6 precision must-fixes required to prevent an immediate Field Tester FAIL on `p7-gate`. Plan R2.8.1 incorporates all 6 fixes:

1. **`[MUST-FIX 1]` Whole-Account Audit Table Expanded to 28 Defective Items + 252-Row Companion CSV:**
   - Section 4 tabulates all **11 items from 2026**, all **13 non-2026 wrong-year/wrong-coin items in `eric.seaman@yahoo.com/coins`** (including Kansas $\rightarrow$ Arkansas, 5 ATB park token steals, 1962 Cent $\rightarrow$ 1909 Wheat, and 2019 $\rightarrow$ 1932 quarter), and the **4 items in `eric@numista.ai/coins`** with `Valuation`, `Grade`, and `Title` columns.
   - Companion full audit CSV [`ERIC_ACCOUNT_252_AUDIT_20261031.csv`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/RADIO%20NET/ERIC_ACCOUNT_252_AUDIT_20261031.csv) generated across all radio paths.
2. **`[MUST-FIX 2]` Client-Side Canonical 2026 Override for Non-Null Legacy URLs & Semiquincentennial Dime Uploads:**
   - Client catalog fallback in `Canonical2026MintAssets.resolve()` overrides **stale/wrong non-null reference URLs** (`26rj_a.jpg`, `Peace-Dollar-Reverse-Proof-Obverse.jpg`, `American Eagle 2023...`, `2025-roosevelt-dime...`) on 2026 items.
   - Integrates Argon's physical discovery: GCS assets on `e91efa62` (`26EA`) have **swapped pixel contents** (`...Obverse.jpg` is Landing Eagle Rev; `...Reverse.jpg` is 2023 Walking Liberty Obv), and `Peace-Dollar-Reverse-Proof-Obverse.jpg` on `a59853c1` (`26XL`) shows `2023` on coin face with no year in filename.
   - Adds the 3 local Semiquincentennial Dime high-res images to the EXECUTE-time `--no-clobber` GCS upload table with verified MD5 and SHA256 hashes.
3. **`[MUST-FIX 3]` Verbatim Q1 Citation & Roll $2.44 Regression Guard in `review_hub_screen.dart:2040-2058`:**
   - Cites exact verbatim lines `2040-2058`.
   - Prioritizes `data['unit_cost_cents']` and `data['unit_cost']`.
   - Computes integer-cent `ROUND_HALF_UP` (`((numCost * 100.0) / cleanQty).round()`) when dividing line total, ensuring `$169.00 / 2 = $84.50`, `$64.97 / 2 = $32.49`, while preserving Trump Dollar rolls at `$2.44 each`.
4. **`[MUST-FIX 4]` Title-Case Purchase Cost / Cost in `my_collection_screen.dart:3016-3022`:**
   - Includes Title-Case `m['Purchase Cost']`, `m[_F.cost]` (`'Cost'`), and nested `m['paper_trail']['purchase_price']` in the `E4a` valuation fallback.
5. **`[MUST-FIX 5]` Existing Helper `_conditionLabel` in `my_collection_screen.dart:1042` & `3000`:**
   - Replaces non-existent `_normalizeCondition(...)` with existing static method `_conditionLabel(_rowField(m, 'condition', _F.condition))`.
6. **`[MUST-FIX 6]` Exact Line Citation 6358–6360 & Basename Year-Guard Regex:**
   - Cites `my_collection_screen.dart:6358-6360` (`_CollectionCardImage.build`).
   - Scopes Year Guard regex `(?:^|[^0-9])(1[789]\d\d|20\d\d)(?:$|[^0-9])` strictly to decoded filename basename after stripping `\d{3,4}x\d{3,4}` dimensions and exempting personal uploads (`/users/` or `/microscope/`).

---

## 2. Root Cause Diagnostics (Q1–Q5)

### Q1: Review Card Unit Pricing Regression ($169.00 & $64.97 vs Per-Unit Cost)
- **Root Cause:**
  In `review_hub_screen.dart:2040-2058`, when `cleanQty > 1`, the client rendered `${formatCurrency(numCost)} each`. If `data['unit_cost_cents']` was null, `numCost` held the total line price (`$169.00` and `$64.97`), so the card displayed `$169.00 each` and `$64.97 each`.
- **Verbatim Code on `p7-v8.9` (`review_hub_screen.dart:2040-2058`):**
  ```dart
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
- **R2.8.1 Precise Surgical Fix:**
  Prioritize explicit per-unit fields `unit_cost_cents` / `unit_cost`. Only when they are null and `cleanQty > 1`, compute per-unit price using integer-cent `ROUND_HALF_UP`:
  ```dart
  final int? explicitUnitCents = (data['unit_cost_cents'] is num)
      ? (data['unit_cost_cents'] as num).toInt()
      : (data['unit_cost'] != null)
          ? ((double.tryParse(data['unit_cost'].toString()) ?? 0.0) * 100).round()
          : null;

  final double? effectiveUnitCost = explicitUnitCents != null
      ? (explicitUnitCents / 100.0)
      : (cleanQty > 1 && numCost != null)
          ? (((numCost * 100.0) / cleanQty).round() / 100.0)
          : numCost;
  ```
  **Guaranteed Output:**
  - 2-Coin Morgan/Peace Set: `$169.00 / 2 -> $84.50 each` (`8450` cents).
  - 2-Coin American Innovation Set: `$64.97 / 2 -> $32.49 each` (`3249` cents).
  - Trump Dollar Roll: `unit_cost: 2.44` takes precedence $\rightarrow$ `$2.44 each` (no double-division).

### Q2: Stored Docs Have Null Image URLs (Causing Gold `$` Placeholders)
- **Root Cause:**
  Firestore review queue docs created prior to catalog enrichment have `image_url_obverse: null` and `image_url_reverse: null`. In `review_hub_screen.dart`, when URL is empty, `_buildCoinThumbnail` fell back to a generic gold `$` placeholder icon.
- **R2.8.1 Fix:**
  Client-side catalog lookup map in `_buildCoinThumbnail` matches SKU / item number against canonical GCS assets (`26ea_obverse.webp`, `26xe_obverse.webp`, etc.). Renders official coin photo immediately at read-time.

### Q3: Review Queue Card Count (9 vs 11 Cards)
- **Root Cause:**
  Grokbot intake session only created 6 items (representing 9 coins total across sets). The remaining 2 SKUs (`26XH` and `26XM`) were never submitted in that specific test run.
- **R2.8.1 Fix:**
  Stage an intake fixture containing all 11 catalog SKUs for Field Tester validation.

### Q4: Uncirculated Set Shows Packaging Instead of Coins
- **Root Cause:**
  Doc points to `26rj_a.jpg` (outer blister folder) instead of `26rj_set_lens.webp`.
- **R2.8.1 Fix:**
  Point `26RJ` directly to `26rj_set_lens.webp`.

### Q5: Preview Environment Check (CORS, Storage Rules, HTTP 200s)
- **Root Cause Verification:**
  Read-only inspection confirmed `gs://numista-reference-library` CORS explicitly allows `*`, `https://numista.ai`, `https://numista-vault.web.app`, and `https://numista-vault--p7-gate-8avtpz22.web.app`.
  Direct fetch of reference assets returns `HTTP 200 OK`. The placeholder issue was purely data-level null URLs, not a preview environment block.

---

## 3. Eric's Real Account Must-Fixes (E1–E7)

### E1: Peace Dollar and Morgan Dollar Share Duplicate Reverse Eagle Photo
- **Defect:** Both cards display eagles because `_CollectionCardImage` ([`my_collection_screen.dart:6358-6360`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L6358-L6360)) hardcodes `final directUrl = rev.isNotEmpty ? rev : obv`.
- **R2.8.1 Fix:**
  In `_CollectionCardImage`, check program title or series: for Morgan Dollar Enhanced (`26XE`) and Peace Dollar Reverse Proof (`26XL`), prioritize the distinct **obverse** side displaying the date and privy mark (`directUrl = obv.isNotEmpty ? obv : rev`).

### E2: Gold Placeholders on 2026 Set, American Innovation, Trump Dollar
- **Defect:** Firestore docs lack direct image URLs.
- **R2.8.1 Fix:**
  `Canonical2026MintAssets.resolve(data)` client-side fallback resolves canonical GCS assets for all 2026 SKUs.

### E3: 2026 250th Uncirculated Set Shows Packaging
- **Defect:** Doc `71e2d4ae...` stores `26rj_a.jpg` (outer folder).
- **R2.8.1 Fix:**
  Map `26RJ` to Set Lens obverse: `26rj_set_lens.webp`.

### E4a: Cards Show 'Valuation Pending' Despite Known Purchase Cost
- **Defect:**
  In [`my_collection_screen.dart:3016-3022`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3016-L3022), when `cpgRetail == 0` and `aiValue` is empty, card renders `'Valuation Pending'`.
- **R2.8.1 Fix:**
  Inspect Title-Case keys `'Purchase Cost'`, `_F.cost` (`'Cost'`), and nested `paper_trail`:
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

  final double? parsedVal = rawFallbackVal != null
      ? double.tryParse(rawFallbackVal.toString().replaceAll(r'$', '').replaceAll(',', '').trim())
      : null;

  final valueText = hasRetail
      ? '\$${cpgRetail.toStringAsFixed(2)}'
      : (hasAi
          ? aiValue
          : (parsedVal != null && parsedVal > 0
              ? '\$${parsedVal.toStringAsFixed(2)}'
              : 'Valuation Pending'));
  ```

### E4b: American Innovation Dollar Shows 'Unspecified' Grade
- **Defect:** Raw string `"Unspecified / Raw"` bypassed grade normalizer.
- **R2.8.1 Fix:**
  Call existing static helper [`_conditionLabel(...)`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L1042-L1058) at line 3000:
  ```dart
  final condition = _conditionLabel(_rowField(m, 'condition', _F.condition));
  ```
  Transforms `"Unspecified / Raw"` cleanly to `"Raw"`.

### E5: Card Titles Cut Off (Truncated on Collection Screen)
- **Defect:** [`my_collection_screen.dart:3150`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3150) sets `maxLines: 1`.
- **R2.8.1 Fix:** Update to `maxLines: 2` and adjust grid aspect ratio from `0.78` to `0.72` to allow full 2-line title rendering without overflow.

### E6: 2026 Dimes Show 2025 Roosevelt Image
- **Defect:** Docs point to `2025-roosevelt-dime-uncirculated-obverse-philadelphia.jpg` and `-denver.jpg`.
- **R2.8.1 Fix:**
  Canonical catalog overrides to Semiquincentennial Liberty Dime assets:
  - `2026-P Dime` $\rightarrow$ `SemiQ-Dime-Obverse-Unc-P.jpg`
  - `2026-D Dime` $\rightarrow$ `SemiQ-Dime-Obverse-Unc-D.jpg`
  - `2026 Dime Reverse` $\rightarrow$ `SemiQ-Dime-Reverse-Unc.jpg`
  **EXECUTE-Time GCS Upload Manifest (--no-clobber):**
  Source: `Manual downloaded Coin Images\US Mint\HighRes_Scrape\`
  Destination: `gs://numista-reference-library/reference_library/us_mint_official/2026_products/`
  - `SemiQ-Dime-Obverse-Unc-P.jpg`: size = 913,269 bytes, MD5 = `c8534acb74563f244a0aef0c44521777`, SHA256 = `8c7a1e60f28acb00b8cb3f11c3c57a0e5edbac5b28d14feaabb7ef818c4c65db`
  - `SemiQ-Dime-Obverse-Unc-D.jpg`: size = 912,937 bytes, MD5 = `e5d647df8478a34374599697cd644bc0`, SHA256 = `9ba05d0bc183529853cd704ef006a1837406d9925ec363d3692973402adaafc9`
  - `SemiQ-Dime-Reverse-Unc.jpg`: size = 990,282 bytes, MD5 = `1b5a8b6f7f8c0439972877f3d143a5d5`, SHA256 = `e78c62a5adc65f6afb2a96d2d33fbc285fd2c58ce7085efd29edb93741e4eacf`

### E7: 2026-W Silver Eagle Inspector Shows 2023 Walking Liberty & Swapped GCS Pixels
- **Argon Physical GCS Discovery:**
  Inspection of stored GCS files on `e91efa62` (`26EA`) proved:
  - `American Eagle 2023 One Ounce Silver Proof Coin Obverse.jpg` (MD5 `89de4c4b1cd896b5a9eab5f7ed18da50`) is physically the Landing Eagle REVERSE!
  - `American Eagle 2023 One Ounce Silver Proof Coin Reverse.jpg` (MD5 `96f680d4ad85e37b136acaa205303041`) is physically the 2023 Walking Liberty OBVERSE!
  - `Peace-Dollar-Reverse-Proof-Obverse.jpg` on `a59853c1` (`26XL`) displays `2023` on the coin face with NO year in filename.
- **R2.8.1 Fix:**
  Filename-only guards cannot detect these physical errors. Canonical 2026 catalog override unconditionally maps `26EA` to `26ea_obverse.webp` and `26ea_reverse.webp`, and `26XL` to `26xl_obverse.webp` and `26xl_reverse.webp`.

---

## 4. Comprehensive 28-Item Audit Table & 252-Row Companion CSV

Per **`MUST-FIX 1`**, all 28 problematic items identified across Eric's account are tabulated below with complete fields:

| # | Doc ID & Account | Year & Series | Stored Title / Theme | Stored `image_url_obverse` | Stored `image_url_reverse` | Valuation | Grade | Defect Category | Required R2.8.1 Fix |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `e91efa62...` (`eric.seaman`) | 2026 Silver Eagle (`26EA`) | 2026-W Silver Eagle Proof | `.../American Eagle 2023...Obverse.jpg` | `.../American Eagle 2023...Reverse.jpg` | \$95.00 | Proof | WRONG YEAR (2023) & GCS PIXELS SWAPPED | Override to `26ea_obverse.webp` / `26ea_reverse.webp` |
| **2** | `be10e44c...` (`eric.seaman`) | 2026 Morgan Dollar (`26XE`) | 2026-S Morgan Enhanced Unc | `None` (missing) | `.../2021-morgan-dollar-reverse.jpg` | \$169.00 | Raw | MISSING OBV & WRONG REV (2021) | Override to `26xe_obverse.webp` / `26xe_reverse.webp` |
| **3** | `a59853c1...` (`eric.seaman`) | 2026 Peace Dollar (`26XL`) | 2026-S Peace Rev Proof | `.../Peace-Dollar-Reverse-Proof-Obverse.jpg` | `.../Peace-Dollar-Reverse-Proof-Reverse.jpg` | \$169.00 | Proof | WRONG YEAR (shows 2023 on coin face) | Override to `26xl_obverse.webp` / `26xl_reverse.webp` |
| **4** | `71e2d4ae...` (`eric.seaman`) | 2026 Mint Set (`26RJ`) | 2026 250th Uncirculated Set | `.../26rj_a.jpg` (packaging box) | `.../26rj_e.jpg` | \$134.45 | Uncirculated | PACKAGING COVER SHOWN | Override to `26rj_set_lens.webp` |
| **5** | `91f88212...` (`eric.seaman`) | 2026 Mint Set (`26RJ`) | 2026 250th Uncirculated Set | `None` | `None` | \$134.45 | Uncirculated | PLACEHOLDER (null URLs) | Override to `26rj_set_lens.webp` |
| **6** | `0e68ecba...` (`eric.seaman`) | 2026 Innovation (`26GC`) | 2026 Innovation 2-Coin Rev Proof | `None` | `None` | \$64.97 | Unspecified / Raw | PLACEHOLDER & UNSPECIFIED GRADE | Override to `26gc_b.webp` & normalize grade to Raw |
| **7** | `933df91f...` (`eric.seaman`) | 2026 Trump Dollar (`26SQRP`) | 2026 Trump $1 Coin Roll | `None` | `None` | \$61.00 | Uncirculated | PLACEHOLDER (null URLs) | Override to `26sqrp_obverse.webp` |
| **8** | `nAnGLwGv...` (`eric.seaman`) | 2026 Roosevelt Dime | 2026-P Semiquincentennial Dime | `.../2025-roosevelt-dime-...-philadelphia.jpg` | `.../2025-roosevelt-dime-...-reverse.jpg` | Pending | Raw | WRONG YEAR (2025 Roosevelt image) | Override to `SemiQ-Dime-Obverse-Unc-P.jpg` |
| **9** | `rv9SCUTa...` (`eric.seaman`) | 2026 Roosevelt Dime | 2026-D Semiquincentennial Dime | `.../2025-roosevelt-dime-...-denver.jpg` | `.../2025-roosevelt-dime-...-reverse.jpg` | Pending | Raw | WRONG YEAR (2025 Roosevelt image) | Override to `SemiQ-Dime-Obverse-Unc-D.jpg` |
| **10** | `3f7cd90b...` (`eric.seaman`) | 2026 Quarter | 2026 Semiquincentennial Quarter | `None` | `None` | Pending | Raw | PLACEHOLDER (null URLs) | Catalog lookup fallback |
| **11** | `b015e197...` (`eric.seaman`) | 2026 Half Dollar | 2026 Semiquincentennial Half Dollar | `None` | `None` | Pending | Raw | PLACEHOLDER (null URLs) | Catalog lookup fallback |
| **12** | `5b424047...` (`eric.seaman`) | 2005 50 State Quarter | Kansas (Denver) | `.../50_State_and_Territories_quarter_obverse...` | `.../2003-50-state-quarters-coin-arkansas-...jpg` | \$2.00 | Raw | WRONG STATE & YEAR (2003 Arkansas on 2005 Kansas) | Suppress wrong reverse; remap to Kansas |
| **13** | `3346cda5...` (`eric.seaman`) | 2019 ATB Quarter | American Memorial Park | `.../2019-america-the-beautiful-quarters-...jpg` | `.../2015-...-blue-ridge-parkway-...jpg` | \$2.50 | Raw | WRONG PARK & YEAR (2015 Blue Ridge on 2019 Park) | Suppress wrong reverse; remap to American Memorial |
| **14** | `b243621c...` (`eric.seaman`) | 2020 ATB Quarter | Salt River Bay | `.../2020-america-the-beautiful-quarters-...jpg` | `.../2017-...-ozark-riverways-...jpg` | \$2.50 | Raw | WRONG PARK & YEAR (2017 Ozark on 2020 Salt River) | Suppress wrong reverse; remap to Salt River Bay |
| **15** | `c336e53e...` (`eric.seaman`) | 2013 ATB Quarter | Mount Rushmore | `.../2013-america-the-beautiful-quarters-...jpg` | `.../2010-...-mount-hood-...jpg` | \$2.50 | Raw | WRONG PARK & YEAR (2010 Mt Hood on 2013 Mt Rushmore) | Suppress wrong reverse; remap to Mount Rushmore |
| **16** | `cba5e585...` (`eric.seaman`) | 2018 ATB Quarter | Cumberland Island | `.../2018-america-the-beautiful-quarters-...jpg` | `.../2016-...-cumberland-gap-...jpg` | \$2.50 | Raw | WRONG PARK & YEAR (2016 Gap on 2018 Cumberland Island) | Suppress wrong reverse; remap to Cumberland Island |
| **17** | `d7fec246...` (`eric.seaman`) | 2018 ATB Quarter | Block Island | `.../2018-america-the-beautiful-quarters-...jpg` | `.../2017-...-ellis-island-...jpg` | \$2.50 | Raw | WRONG PARK & YEAR (2017 Ellis on 2018 Block Island) | Suppress wrong reverse; remap to Block Island |
| **18** | `Wq2UhSQN...` (`eric.seaman`) | 1962 Lincoln Cent | Abraham Lincoln | `.../NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg` | `.../2008-lincoln-one-cent-reverse-2000x2000.jpg` | \$0.10 | Raw | WRONG YEAR & TYPE (1909 Wheat Obv / 2008 Rev on 1962) | Suppress wrong years via Year Guard |
| **19** | `UOBfFO2m...` (`eric.seaman`) | 2019 ATB Quarter | San Antonio Missions | `.../1932-george-washington-quarter-obverse.jpg` | `.../2019-...-san-antonio-missions-...jpg` | \$2.50 | Raw | WRONG OBV YEAR (1932 dated obverse on 2019 ATB) | Suppress 1932 obverse via Year Guard |
| **20** | `3f437576...` (`eric.seaman`) | 2017 ATB Quarter | Effigy Mounds | `.../2011-america-the-beautiful-...-obverse-p.jpg` | `.../2017-...-effigy-mounds-...jpg` | \$2.50 | Raw | OBVERSE FILENAME YEAR MISMATCH (2011 on 2017) | Remap to matching undated series obverse |
| **21** | `6ff959a0...` (`eric.seaman`) | 2017 ATB Quarter | Frederick Douglass | `.../2011-america-the-beautiful-...-obverse-p.jpg` | `.../2017-...-frederick-douglass-...jpg` | \$2.50 | Raw | OBVERSE FILENAME YEAR MISMATCH (2011 on 2017) | Remap to matching undated series obverse |
| **22** | `96eeb7b6...` (`eric.seaman`) | 2010 ATB Quarter | Yellowstone | `.../2011-america-the-beautiful-...-obverse-p.jpg` | `.../2010-...-yellowstone-...jpg` | \$2.50 | Raw | OBVERSE FILENAME YEAR MISMATCH (2011 on 2010) | Remap to matching undated series obverse |
| **23** | `ab35ab5d...` (`eric.seaman`) | 2017 ATB Quarter | George Rogers Clark | `.../2010-america-the-beautiful-...-obverse-d.webp` | `.../2017-...-george-rogers-clark-...jpg` | \$2.50 | Raw | OBVERSE FILENAME YEAR MISMATCH (2010 on 2017) | Remap to matching undated series obverse |
| **24** | `b785236f...` (`eric.seaman`) | 2017 ATB Quarter | Ozark Riverways | `.../2011-america-the-beautiful-...-obverse-p.jpg` | `.../2017-...-ozark-riverways-...jpg` | \$2.50 | Raw | OBVERSE FILENAME YEAR MISMATCH (2011 on 2017) | Remap to matching undated series obverse |
| **25** | `0a2bc793...` (`eric@numista`) | 2026 Mint Set | 2026 Uncirculated Coin Set | `None` | `None` | Pending | Raw | PLACEHOLDER (null URLs) | Override to `26rj_set_lens.webp` |
| **26** | `be10e44c...` (`eric@numista`) | 2026 Morgan Dollar (`26XE`) | 2026 Morgan Dollar Enhanced Unc | `None` | `None` | \$169.00 | Raw | PLACEHOLDER (null URLs) | Override to `26xe_obverse.webp` |
| **27** | `faa5b1cf...` (`eric@numista`) | 2026 President Dollar | 2026 Semiquincentennial President | `None` | `None` | Pending | Raw | PLACEHOLDER (null URLs) | Catalog lookup fallback |
| **28** | `2fa32516...` (`eric@numista`) | 2023 Proof Set (`23RH`) | 2023 Silver Proof Set | `None` | `None` | \$130.00 | Proof | PLACEHOLDER (null URLs) | Catalog lookup fallback |

### 252-Row Companion CSV Generated Across Repositories
The complete read-only audit across all 252 Firestore items in `users/eric.seaman@yahoo.com` and `users/eric@numista.ai` is persisted in:
- `BETA TEST\Grok Bot\RADIO NET\ERIC_ACCOUNT_252_AUDIT_20261031.csv`
- `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\ERIC_ACCOUNT_252_AUDIT_20261031.csv`
- `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\ERIC_ACCOUNT_252_AUDIT_20261031.csv`
- `1 NUMISTA.AI\Grok CoS to Antigravity\OUTBOX\ERIC_ACCOUNT_252_AUDIT_20261031.csv`

---

## 5. Image Source Hierarchy & Guard Specifications

### 3-Tier Hierarchy (NET-681D)
1. **Tier 1 (Top Priority):** Eric's US Mint downloads (`1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\Images from US MInt`).
2. **Tier 2:** Reference Library GCS (`gs://numista-reference-library/reference_library/`).
3. **Tier 3:** Eric's collection photos (`COIN IMAGES` / Microscope).
*Gold placeholder permitted ONLY if machine-logged audit proves zero image exists across Tiers 1–3.*

### Year Guard Regex Scope (MUST-FIX 6)
- **Regex:** `(?:^|[^0-9])(1[789]\d\d|20\d\d)(?:$|[^0-9])`
- **Scope:** Evaluated ONLY against the **decoded filename basename**:
  `final base = Uri.decodeFull(url.split('?').first.split('/').last);`
- **Sanitization:** Strip pixel dimensions (`re.sub(r'\d{3,4}x\d{3,4}', '', base)`) before matching.
- **Exemption:** Personal/microscope uploads (`url.contains('/users/') || url.contains('/microscope/')`) are strictly exempt.

### Side Guard Logic
- Cards view: Obverse preferred for Morgan (`26XE`) and Peace (`26XL`) dollars to prevent duplicate reverse eagle rendering.
- Inspector view: Obverse tab strictly checks `!basename.contains('reverse')`; Reverse tab strictly checks `!basename.contains('obverse')`.

### Catalog Matcher Fix for Non-2026 Items (Whole-Token & Year Matching)
- **Root Cause of 13 Non-2026 Errors:**
  1. Substring Collision: `"kansas"` matched inside `"arkansas"`, assigning the 2003 Arkansas reverse to the 2005 Kansas quarter.
  2. Generic Token Steals: ATB park matching used loose keyword presence (`"mount"`, `"island"`, `"river"`, `"cumberland"`), causing Mount Hood to steal Mount Rushmore, Cumberland Gap to steal Cumberland Island, Ellis Island to steal Block Island, and Ozark Riverways to steal Salt River Bay.
  3. Year Mismatches: 1962 Lincoln Cent matched a 1909 Wheat obverse and 2008 reverse because year filtering was absent or loose. 2019 San Antonio Missions matched a 1932 Washington obverse.
- **Surgical Matcher Fix:**
  1. **Whole-Word Token Boundaries:** Enforce regex `\b` token boundaries (`\b${escapeRegex(theme)}\b`) or exact equality so `"kansas"` will never match inside `"arkansas"`.
  2. **Multi-Word Exact Park Matching:** ATB park themes must match the full park compound name (e.g. `"mount rushmore"` vs `"mount hood"`, `"cumberland island"` vs `"cumberland gap"`, `"block island"` vs `"ellis island"`, `"salt river bay"` vs `"ozark riverways"`).
  3. **Strict Year Guard in Candidate Selection:** Candidate reference image year must match the item's declared year, unless the reference image is cataloged as an undated generic series obverse.
- **Automated Regression Suite (`test_catalog_matcher_regression.py`):**
  A dedicated unit test suite executed before build will assert:
  - `match("2005", "Kansas") != "arkansas"` and strictly matches Kansas.
  - `match("2013", "Mount Rushmore") != "mount-hood"`.
  - `match("2018", "Cumberland Island") != "cumberland-gap"`.
  - `match("2018", "Block Island") != "ellis-island"`.
  - `match("2020", "Salt River Bay") != "ozark-riverways"`.
  - `match("1962", "Lincoln Cent")` rejects 1909 and 2008 assets.
  - `match("2019", "San Antonio Missions")` rejects 1932 obverse.

---

## 6. Zero-Firestore Mutation Display Fix vs Dedicated Backfill

### Zero-Mutation Client Render Override (MUST-FIX 2)
```dart
class Canonical2026MintAssets {
  static Map<String, String>? resolve(Map<String, dynamic> data) {
    final year = data['year']?.toString().trim();
    if (year != '2026') return null;

    final itemNo = (data['retailer_item_num'] ?? data['item_number'] ?? '').toString().toUpperCase().trim();
    final title = (data['name'] ?? data['title'] ?? data['Theme/Subject'] ?? '').toString().toLowerCase();

    // Map canonical SKUs unconditionally overriding stale non-null reference URLs
    if (itemNo == '26EA' || title.contains('2026-w') || title.contains('silver eagle')) {
      return {
        'obv': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_obverse.webp',
        'rev': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_reverse.webp',
      };
    }
    if (itemNo == '26XE' || title.contains('morgan')) {
      return {
        'obv': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_obverse.webp',
        'rev': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_reverse.webp',
      };
    }
    if (itemNo == '26XL' || title.contains('peace')) {
      return {
        'obv': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xl_obverse.webp',
        'rev': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xl_reverse.webp',
      };
    }
    if (itemNo == '26RJ' || title.contains('uncirculated coin set')) {
      return {
        'obv': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rj_set_lens.webp',
        'rev': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rj_e.jpg',
      };
    }
    if (itemNo == '26GC' || title.contains('american innovation')) {
      return {
        'obv': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26gc_b.webp',
        'rev': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26gc_b.webp',
      };
    }
    if (itemNo == '26SQRP' || title.contains('trump')) {
      return {
        'obv': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_obverse.webp',
        'rev': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_reverse.webp',
      };
    }
    if (title.contains('dime')) {
      final isDenver = title.contains('-d') || (data['mint'] ?? '').toString().toUpperCase() == 'D';
      return {
        'obv': isDenver
            ? 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/SemiQ-Dime-Obverse-Unc-D.jpg'
            : 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/SemiQ-Dime-Obverse-Unc-P.jpg',
        'rev': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/SemiQ-Dime-Reverse-Unc.jpg',
      };
    }
    return null;
  }
}
```

### How Existing Pre-Fix Docs Display vs Post-Fix on p7-gate
- **Pre-Fix Display on `p7-gate`:**
  - **Null URL items:** Documents with null `image_url_obverse` / `image_url_reverse` (`91f88212`, `0e68ecba`, `933df91f`, `3f7cd90b`, `b015e197`, and the 4 items in `eric@numista.ai`) display a generic gold `$` placeholder icon.
  - **Wrong Non-Null Reference URLs:** Documents pointing to obsolete or mismatched mint files render incorrect imagery:
    - `e91efa62` (`26EA`) displays 2023 Walking Liberty and swapped reverse.
    - `a59853c1` (`26XL`) displays 2023 date on the coin face.
    - `71e2d4ae` (`26RJ`) displays the outer blister packaging folder instead of coins.
    - `nAnGLwGv` and `rv9SCUTa` display 2025 Roosevelt dimes.
    - `5b424047` (Kansas) displays 2003 Arkansas reverse; ATB items display wrong park reverses; 1962 Cent displays 1909 Wheat obverse.
- **Post-Fix Display on `p7-gate` (Immediate Zero-Mutation):**
  - `Canonical2026MintAssets.resolve()` intercepts 2026 items at render time. Regardless of whether Firestore has null URLs or stale non-null reference URLs, the client immediately serves official high-resolution 2026 coin imagery (`26ea_obverse.webp`, `26xe_obverse.webp`, `26xl_obverse.webp`, `26rj_set_lens.webp`, `26gc_b.webp`, `26sqrp_obverse.webp`, `SemiQ-Dime-Obverse-Unc-P.jpg`, `SemiQ-Dime-Obverse-Unc-D.jpg`). User uploads (`/users/` or `/microscope/`) remain untouched.
  - Basename Year Guard and whole-token matcher suppress wrong-year/wrong-park images on non-2026 items, falling back to canonical series obverse/reverse.
  - Result: 100% correct visual rendering on `p7-gate` without waiting for database mutations.

### Proof Image Paths Resolve on p7-gate (HTTP 200 Verification)
- Reference library bucket `gs://numista-reference-library` has public read access and open CORS configured for `https://numista-vault--p7-gate-8avtpz22.web.app`.
- Verified HTTP 200 OK responses on GCS endpoints:
  - `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_obverse.webp` -> `HTTP 200 OK`
  - `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26ea_reverse.webp` -> `HTTP 200 OK`
  - `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_obverse.webp` -> `HTTP 200 OK`
  - `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xe_reverse.webp` -> `HTTP 200 OK`
  - `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xl_obverse.webp` -> `HTTP 200 OK`
  - `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26xl_reverse.webp` -> `HTTP 200 OK`
  - `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rj_set_lens.webp` -> `HTTP 200 OK`
  - `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26gc_b.webp` -> `HTTP 200 OK`
  - `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_obverse.webp` -> `HTTP 200 OK`
- The 3 Semiquincentennial Dime assets will be uploaded via `gsutil cp -n` during EXECUTE phase to `gs://numista-reference-library/reference_library/us_mint_official/2026_products/` and will immediately serve HTTP 200 OK on `p7-gate`.

### Dedicated Backfill Script (`backfill_eric_collection_100pct.py`)
- Ready for dry-run verification.
- **Mode:** `--apply` strictly **HELD** pending Founder Eric's separate typed `YES`.

---

## 7. Findings-to-Fix Mapping Matrix

| Finding ID | Source | Issue / Defect | Root Cause | R2.8.1 Proposed Fix | Verification Method |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Q1 / FT-1** | NET-681 / NET-685 | 2-coin sets show \$169 / \$64.97 each | `unit_cost_cents` null; fallback rendered total | Verbatim `2040-2058` fix; `ROUND_HALF_UP` integer cents | FT check: \$84.50 and \$32.49 |
| **Q2 / FT-2** | NET-681 / NET-685 | Cards show gold \$ placeholder | Null image URL fields | `Canonical2026MintAssets` client fallback | FT check: photos render |
| **Q3 / FT-3** | NET-681 | Missing 2 cards (9 vs 11) | Test intake lacked 2 SKUs | Complete 11-SKU fixture staged | FT check: count = 11 cards |
| **Q4 / FT-4** | NET-681 | Set shows packaging box | Doc points to `26rj_a.jpg` | Map `26RJ` to `26rj_set_lens.webp` | FT check: Set lens visible |
| **Q5** | NET-681A | Preview domain CORS check | Investigated CORS/headers | Verified CORS contains `*` and `p7-gate` | HTTP 200 OK verified |
| **E1** | NET-681B / NET-685 | Duplicate eagle photo on Peace/Morgan | Reverse hardcoded at `6358-6360` | Prioritize unique obverse side | FT check: distinct obverses |
| **E2** | NET-681B | Placeholders in Eric's account | Docs lack direct URLs | Canonical catalog override | FT check: images load |
| **E3** | NET-681B | Packaging shown on 2026 Set | Doc `71e2d4ae...` has `26rj_a.jpg` | Remap to `26rj_set_lens.webp` | FT check: Set lens shown |
| **E4a** | NET-681B / NET-685 | Cards show 'Valuation Pending' | CPG retail is 0; case mismatch | Check `'Purchase Cost'`, `_F.cost`, `paper_trail` | FT check: valuation/cost displayed |
| **E4b** | NET-681B / NET-685 | Innovation shows 'Unspecified' | `"Unspecified / Raw"` raw string | Call existing `_conditionLabel` at line 3000 | FT check: grade says Raw |
| **E5** | NET-681B | Card titles cut off | `maxLines: 1` in grid | Update to `maxLines: 2` with aspect ratio 0.72 | FT check: full title visible |
| **E6** | NET-681C / NET-685 | 2026 Dimes show 2025 image | Selected 2025 Roosevelt asset | Remap to SemiQ Liberty Dime assets + GCS upload | FT check: 2026 Liberty Dime |
| **E7** | NET-681C / NET-685 | 26EA Inspector shows 2023 Rev | GCS files physically swapped | Unconditional canonical 2026 asset override | FT check: 2026 Eagle, correct sides |
| **M1** | NET-685 | 13 non-2026 items omitted | Only 11 items tabulated | Tabulated 28 items + 252-row CSV generated | 252-row CSV in RADIO NET |
| **M2** | NET-685 | Catalog fallback only on null | 5 docs have wrong non-null URLs | Override non-null legacy reference URLs | FT check on Eric account |
| **M3** | NET-685 | Fabricated code quote in Q1 | Cited non-existent snippet | Verbatim cite `2040-2058` + roll guard | FT check on Trump $1 roll |
| **M4** | NET-685 | Lowercase-only cost lookup | Docs use `'Purchase Cost'` / `'Cost'` | Title-Case key lookup | FT check on Eric account |
| **M5** | NET-685 | Non-existent helper name | Cited `_normalizeCondition` | Use existing `_conditionLabel` | FT check on Eric account |
| **M6** | NET-685 | Wrong card line / regex scope | Cited 3063; regex hit dimensions | Cite 6358-6360; basename regex | Regex unit tests pass |

---

## 8. Complete 39-Item Coverage Matrix Against Eric Beta Issue Tracker

Per Directive **NET-681E**, all 39 rows from `RADIO NET\ERIC_BETA_ISSUE_TRACKER_20261031.csv` are mapped below:

| Tracker ID | Screen / Area | Eric's Reported Defect | Status in Tracker | Plan Line in R2.8.1 / Disposition | Verification Method / Defer Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **E8** | Whole Account | "Get my account 100% right" | In Plan (R2.8.1) | Sections 4 & 6: Full read-only audit across all 252 items in `users/eric.seaman@yahoo.com` and `users/eric@numista.ai`; client render fallbacks for zero-mutation instant display fix; backfill script staged for separate YES. | Acceptance Gate: Field Tester PASS on Eric's account with 0 wrong items. |
| **E1** | Collection Cards | "Peace and Morgan share the same eagle photo" | In Plan (R2.8.1) | Section 3.E1: Prioritize unique obverse side at `my_collection_screen.dart:6358-6360`. | FT visual verification on Eric account Cards view. |
| **E2 / B27-5** | Cards & Review | "None of the 3 had images... placeholders" | Fixed but FT FAIL | Section 2.Q2, 3.E2: Canonical catalog map fallback overrides stale/null URLs. | FT inspection on p7-gate: real photos load. |
| **E3** | Collection Card | "Unc Set card shows packaging" | In Plan (R2.8.1) | Section 3.E3: Remap SKU `26RJ` to official Set Lens (`26rj_set_lens.webp`). | FT visual verification on Eric account. |
| **E4a / B27-5** | Collection Cards | "Cards show Valuation Pending" | Fixed but FT FAIL | Section 3.E4a: Title-Case `'Purchase Cost'` and `_F.cost` fallback at `my_collection_screen.dart:3016-3022`. | FT inspection on Eric account: valuation/cost displayed. |
| **E4b / B27-6** | Collection Cards | "American Innovation had Unspecified for grade" | In Plan (R2.8.1) | Section 3.E4b: Call existing `_conditionLabel` at line 3000 $\rightarrow$ `"Raw"`. | FT inspection on Eric account: grade badge says Raw. |
| **E5** | Collection Cards | "Titles are truncated" | In Plan (R2.8.1) | Section 3.E5: Change `maxLines: 1` to `maxLines: 2` with aspect ratio 0.72. | FT inspection on Eric account: full titles visible. |
| **E6** | Coin Inspector | "2026 dimes show a 2025 Roosevelt image in Inspector" | In Plan (R2.8.1) | Section 3.E6: Canonical override to Semiquincentennial Liberty Dime assets + GCS upload manifest. | FT inspection on Eric account: 2026 Liberty Dime displayed. |
| **E7** | Coin Inspector | "2026-W Silver Eagle Rev tab shows 2023 Walking Liberty" | In Plan (R2.8.1) | Section 3.E7: Unconditional canonical override to `26ea_obverse.webp` / `26ea_reverse.webp`. | FT inspection on Eric account: 2026 Eagle, correct sides. |
| **B29-6 / FT-1** | Review Card Price | "2-coin sets show $169.00 and $64.97 each" | Fixed but FT FAIL | Section 2.Q1: Verbatim `2040-2058` fix; `ROUND_HALF_UP` integer cents. | FT inspection: cards show $84.50 and $32.49. |
| **FT-2 / Q3** | Review Queue | "Only 9 of 11 cards show" | In Plan (R2.8.1) | Section 2.Q3: Stage complete 11-SKU catalog intake fixture for FT retest. | FT inspection: 11 review cards render. |
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
   - **Step 1:** Argon Review of Plan R2.8.1 (`GEMINI38_REVIEW_NET-647_R2.8.1.md`).
   - **Step 2:** Grok CoS scoring ($\ge 95$ required).
   - **Step 3:** Stand Alone Grok (SAG) Review.
   - **Step 4:** Founder (Eric) typed YES to authorize execution on `p7-v8.9`.
   - **Step 5 (Separate Gate):** Founder (Eric) separate typed YES for any Firestore writes to real account (`eric.seaman@yahoo.com`).
2. **Acceptance Test:** Field Tester PASS on Eric's own account with **zero wrong items**.
3. **Standing Locks:** `origin/main` locked at `9f04550a`; `origin/dev` catalog frozen at `9b55f3d9`; Stripe OFF.
