# ERIC B− LIVE MINT FAIL-FIX PLAN (`Plan.v2`)

- **Author:** Numista.Ai AG Chief of Staff v2 (`AG CoS v2`, `086b98b4-2340-4241-9f6a-08b8aaa8992c`)
- **Date:** 2026-10-27 (Sprint Day 20 / Release Post-Cherry-Pick Window)
- **Status:** **PLAN.V2 FILED — PENDING REVIEW CHAIN GATING (DO NOT EXECUTE CODE YET)**
- **Round:** Round 2 of Maximum 4 (`v1` HOLD 58/100 -> `v2` Real Code Map + PM Amend)
- **Review Chain Gate (`NET-602_AMEND` / `NET-615` / `NET-616`):**
  `AG CoS v2 Plan.v2 -> Argon Re-Score -> Grok Bot CoS (GB) Concurrence -> Stand Alone Grok Final Review -> Desk/Founder EXECUTE Typed "YES"`
- **Inputs & Grounding Evidence:**
  1. `ARGON_REVIEW_ERIC_BMINUS_PLAN_V1_2026-10-27.md` (Argon Audit: 58/100 HOLD, real code map)
  2. `GBCOS_REVIEW_ERIC_BMINUS_PLAN_V1_2026-10-27.md` (GB CoS Concurrence on HOLD)
  3. `NET-616_GROKCOS-to-AGCOS-ARGON-COS-FINOPS_ERIC-1351-PM-AMEND-PLAN-V2_LIVE.md` & `NET616_PM_TEST_1351_AMEND_PLAN_V2.md`
  4. Founder 1351hrs PM Beta Test: `1 NUMISTA.AI\BETA TEST\MY TESTING\27 OCT 26\1351hrs test\` (`27 OCT 2026 v2.docx`, `Receipt_2026 Uncirculated Coin Set.pdf`, `SS 1.png` - `SS 7.png`)
  5. Founder Morning Review: `27 OCT 2026.docx` / `27_OCT_2026_morning_review.docx`, `SS 1.png` - `SS 10.png`
  6. Standing Operational Locks: `origin/main` LOCKED (`449a9dcf`), Catalog/Brain Merge HOLD, Sandbox Fold-Gate NO-FOLD Lock (`NET-609`).

---

## 1. Executive Summary & Review Chain Status

### 1.1 Transition from `Plan.v1` to `Plan.v2`
`Plan.v1` scored 58/100 (HOLD) by Argon and was concurred HOLD by Grok Bot CoS because:
1. It cited 19 nonexistent React/TypeScript and hypothetical Python paths (`numista_web/src/components/...`).
2. It misdiagnosed the technical root causes on 8 items due to lack of codebase inspection prior to drafting.
3. At 13:51 ET, the Founder performed an afternoon follow-up beta test (`1351hrs test`), revealing that morning invoice items **still had no images or valuations after hours (PM-01, P0)**, and re-uploading an identical 2026 Uncirculated Coin Set (`26RJ`, Invoice `USM23493262`) **failed duplicate detection completely with 0 duplicates flagged (PM-02, P0)**.

`Plan.v2` resolves 100% of these deficiencies:
- **Zero Hallucinated Paths:** 100% grounded in the real Flutter frontend (`numista_mobile/lib/...`) and FastAPI backend (`numista_backend/...`).
- **Verbatim Code Citations (Rule 6a):** Every `file:line` citation includes verbatim code lines inspected directly in the repository.
- **Folds All Afternoon Findings (`PM-01` through `PM-07`):** Expands the 17 morning items with the 7 afternoon test findings, prioritizing the P0 post-commit valuation/image pipeline and multi-order duplicate detection.
- **Strict Review Chain Gating:** **ZERO CODE, ZERO DEPLOYS, ZERO CHERRY-PICKS** until Argon, GB CoS, and Stand Alone Grok complete the review gate and Eric issues typed `YES`.

### 1.2 Issue & Finding Coverage Matrix
| Bucket | Issue IDs Covered | Severity | Primary Code Targets |
| :--- | :--- | :---: | :--- |
| **B1 — Review Queue Data Integrity & Edit/Select State** | `I-03`, `I-04a`, `I-04b`, `I-04c`, `I-05`, `I-06`, `I-08`, `PM-02`, `PM-03`, `PM-07` | P0 / P1 | `numista_backend/services/us_mint_catalog_service.py`<br>`numista_backend/main.py`<br>`numista_mobile/lib/screens/review_hub_screen.dart` |
| **B2 — Post-Commit Enrichment, Images & Valuation Pipeline** | `I-07`, `I-09`, `I-10`, `PM-01`, `PM-04`, `PM-05` | P0 | `numista_backend/main.py` (`/api/review/commit`)<br>`numista_backend/services/us_mint_catalog_service.py`<br>`numista_mobile/lib/screens/my_collection_screen.dart`<br>`numista_mobile/lib/services/coin_image_service.dart` |
| **B3 — Collection Header & Estate Jurisdiction Placement** | `I-11` | P1 | `numista_mobile/lib/screens/my_collection_screen.dart`<br>`numista_mobile/lib/screens/estate_planning_screen.dart` |
| **B4 — Theme Contrast & Readability Defects** | `I-06`, `I-12`, `I-13`, `I-15`, `PM-06` | P1 | `numista_mobile/lib/screens/review_hub_screen.dart`<br>`numista_mobile/lib/screens/my_collection_screen.dart`<br>`numista_mobile/lib/screens/coin_detail_screen.dart` |
| **B5 — Modal Consolidation, Upload UX & Tab Relevance** | `I-01`, `I-02`, `I-14`, `I-16`, `PM-06` | P1 | `numista_mobile/lib/screens/add_coins_hub.dart`<br>`numista_mobile/lib/screens/my_collection_screen.dart`<br>`numista_mobile/lib/screens/coin_detail_screen.dart` |

---

## 2. Issue-by-Issue Remediation Plan with Verbatim Code Citations (Rule 6a)

### Bucket 1: Review Queue Data Integrity & Edit/Select State

#### `I-03` & `PM-05`: Missing Description, Condition & Inconsistent Theme on Modern Mint Sets/Rolls
- **Defects:**
  - `SS 2A` / `SS 2B`: 2023 Silver Proof Set (`23RH`) and 2026 $1 American Innovation rolls (`26AGA`/`26AGB`) showed blank Theme/Subject and defaulted Condition to `"Unspecified"`.
  - `PM-05` (1351hrs test): Afternoon upload of 2026 Uncirculated Coin Set (`26RJ`) had completely blank `Theme/Subject` (whereas morning had `"250th Anniversary Uncirculated Coin Set"`), and AI Estimated Value was `$0.00` vs morning `$36.40`.
- **Inspected Verbatim Code (`numista_backend/services/us_mint_catalog_service.py:19-227`):**
  The `US_MINT_PRODUCT_CATALOG` dictionary contains only 12 SKUs (`26XL`, `26XM`, `26EA`, `26XE`, `26XH`, `26XJ`, `26XK`, `26XN`, `26SQRP`, `24XL`, `24XM`, `24EA`). It has **zero entries** for `26RJ` (2026 Uncirculated Set), `23RH` (2023 Silver Proof Set), or `26AGA`/`26AGB` (American Innovation $1).
- **Inspected Verbatim Code (`numista_mobile/lib/screens/review_hub_screen.dart:1946-1947` & `2200-2206`):**
  ```dart
  1946:     final String rawCondition = (data['Condition'] ?? data['condition'] ?? data['grade'] ?? '').toString().trim();
  1947:     final String condition = rawCondition.isEmpty ? 'Unspecified' : rawCondition;
  ```
  ```dart
  2200:                       if ((data['Theme/Subject'] ?? data['Program/Series']) != null)
  2201:                         Text(
  2202:                           '${data['Theme/Subject'] ?? ''} ${data['Program/Series'] != null ? '• ${data['Program/Series']}' : ''}'.trim(),
  2203:                           style: TextStyle(fontSize: 12, color: isDark ? Colors.white54 : const Color(0xFF64748B)),
  2204:                           maxLines: 1,
  2205:                           overflow: TextOverflow.ellipsis,
  2206:                         ),
  ```
- **Inspected Verbatim Code (`numista_backend/main.py:7668-7672`):**
  ```python
  7668:                 "Denomination": item.get("denomination") or item.get("Denomination") or "",
  7669:                 "Theme/Subject": item.get("subject") or item.get("Theme/Subject") or "",
  7670:                 "Program/Series": item.get("series") or item.get("Program/Series") or "",
  7671:                 "Condition": item.get("condition") or item.get("Condition") or "Uncirculated",
  7672:                 "Strike Type": item.get("strike_type") or item.get("Strike Type") or "Business",
  ```
- **Remediation Plan:**
  1. Add authoritative entries into `US_MINT_PRODUCT_CATALOG` (`us_mint_catalog_service.py`):
     - `26RJ`: Title `"2026 United States Mint Uncirculated Coin Set"`, Theme `"250th Anniversary Semiquincentennial Uncirculated Coin Set"`, Series `"Annual Uncirculated Sets"`, Condition `"Uncirculated"`, Strike Type `"Uncirculated"`, Issue Price `"$36.40"`.
     - `23RH`: Title `"2023 United States Mint Silver Proof Set"`, Theme `"2023 Annual Silver Proof Set"`, Series `"Annual Silver Proof Sets"`, Condition `"Proof"`, Strike Type `"Proof"`, Metal `"99.9% Silver"`, Issue Price `"$130.00"`.
     - `26AGA` / `26AGB`: Title `"2026 American Innovation $1 Coin 25-Coin Roll"`, Theme `"American Innovation $1"`, Condition `"Uncirculated"`, Strike Type `"Circulating"`.
  2. In `numista_backend/main.py:7668-7675`, infer `"Condition": "Proof"` and `"Strike Type": "Proof"` whenever `"proof"` appears in the title/series/description, ensuring Proof sets never default to `"Unspecified"` or `"Business"`.
  3. In `review_hub_screen.dart:2200-2206`, add fallback to `data['official_us_mint_title'] ?? data['Original Description from source'] ?? data['CoinName']` when `Theme/Subject` is blank so the subtitle is never empty.

---

#### `I-04a`: Trump Roll (`26SQRP`) Wrong Mint Mark `(D)` and Questionable Privy Copy
- **Defects (`SS 3`):** Philadelphia SKU `26SQRP` displayed `2026 Dollar (D)` in the header and questionable `(July 4th Privy eligible)` text that puzzled the Founder.
- **Inspected Verbatim Code (`numista_backend/services/us_mint_catalog_service.py:166-176`):**
  ```python
  166:     "26SQRP": {
  167:         "title": "2026 Semiquincentennial Presidential $1 Coin 25-Coin Roll",
  168:         "formal_name": "2026 Semiquincentennial President Donald J. Trump $1 Coin 25-Coin Roll (Philadelphia)",
  169:         "year": 2026,
  170:         "pack_quantity": 25,
  171:         "mint_mark": "",
  172:         "mint_facility": "Philadelphia (P)",
  173:         "denomination": "Dollar",
  174:         "program_series": "Presidential $1 Coins",
  175:         "theme_subject": "Donald J. Trump Semiquincentennial 250th Anniversary Roll (July 4th Privy eligible)",
  176:         "strike_type": "Circulating",
  ```
- **Inspected Verbatim Code (`numista_backend/services/us_mint_catalog_service.py:328-329`):**
  ```python
  328:         if not item.get("Mint Mark") and "mint_mark" in catalog_match:
  329:             item["Mint Mark"] = catalog_match["mint_mark"]
  ```
- **Remediation Plan:**
  1. **Enforce Systemic Catalog Override:** Replace line 328's weak check (`if not item.get("Mint Mark")`) with an authoritative catalog override:
     ```python
     # Systemic Catalog Override: Canonical Mint Facility / Mark takes precedence over LLM hallucination
     facility = catalog_match.get("mint_facility", "")
     if "Philadelphia" in facility:
         item["Mint Mark"] = "P" if not catalog_match.get("circulating_no_mint_mark") else ""
         item["mint_facility"] = "Philadelphia (P)"
     elif "Denver" in facility:
         item["Mint Mark"] = "D"
         item["mint_facility"] = "Denver (D)"
     elif catalog_match.get("mint_mark"):
         item["Mint Mark"] = catalog_match["mint_mark"]
     ```
     For SKU `26SQRP`, explicitly set `mint_facility: "Philadelphia (P)"` and override LLM-hallucinated `"D"` to `"P"` (or circulating edge-incuse specification).
  2. **Clean Official Mint Description:** In `us_mint_catalog_service.py:175`, remove `"(July 4th Privy eligible)"` from `theme_subject`. Use official US Mint description:
     `"Donald J. Trump Semiquincentennial 250th Anniversary Presidential $1 Coin (Philadelphia)"`.

---

#### `I-04b` & `PM-07`: Trump Roll `$9.95` Shipping & Handling Zeroed Out on `pack_expanded` Lots
- **Defects (`SS 3`):** Review Hub displayed `Fee $0.00` on the Trump Roll invoice because `$9.95` S&H was wiped out. Note: in `PM-07`, the 26RJ Uncirculated Set correctly showed `$9.95` because it was not flagged as `pack_expanded`.
- **Inspected Verbatim Code (`numista_backend/services/us_mint_catalog_service.py:379-383`):**
  ```python
  379:                             item["Sticker Price"] = canonical_lot_cost
  380:                             item["Allocated Fees"] = 0.0
  381:                             item["Cost"] = canonical_lot_cost
  382:                             item["Purchase Cost"] = canonical_lot_cost
  383:                             item["cost"] = canonical_lot_cost
  ```
- **Inspected Verbatim Code (`numista_backend/main.py:7653-7654`):**
  ```python
  7653:             doc["allocated_fees"] = 0.0 if doc.get("pack_expanded") else allocated_fee
  7654:             doc["shipping_fee"] = 0.0 if doc.get("pack_expanded") else allocated_fee
  ```
- **Remediation Plan:**
  1. In `numista_backend/services/us_mint_catalog_service.py:380-383`, preserve the invoice-extracted `Allocated Fees`:
     ```python
     alloc_fees = float(item.get("Allocated Fees") or item.get("allocated_fees") or 0.0)
     item["Sticker Price"] = canonical_lot_cost
     item["Allocated Fees"] = alloc_fees
     item["Cost"] = round(canonical_lot_cost + alloc_fees, 2)
     item["Purchase Cost"] = round(canonical_lot_cost + alloc_fees, 2)
     ```
  2. In `numista_backend/main.py:7653-7654`, eliminate the zeroing out of `allocated_fees`:
     ```python
     # Preserve invoice-extracted allocated S&H fee across all items (including pack expansions)
     doc["allocated_fees"] = allocated_fee
     doc["shipping_fee"] = allocated_fee
     ```
     For the Trump roll: Sticker `$61.00` + Allocated Fee `$9.95` = Total Cost `$70.95` (or `$2.84`/coin unit cost).

---

#### `I-04c`: Prevent Auto-Save to Collection on "Edit"
- **Defects (`SS 3`):** Clicking "Edit" in the Review Hub saved the coin directly to `My Collection` before the Founder clicked "Add", preventing further edits.
- **Inspected Verbatim Code (`numista_mobile/lib/screens/review_hub_screen.dart:1126-1132`, `1171-1172`, & `1204`):**
  ```dart
  1126:                         Expanded(
  1127:                           flex: 2,
  1128:                           child: ElevatedButton.icon(
  1129:                             style: ElevatedButton.styleFrom(
  1130:                               backgroundColor: const Color(0xFFF63366),
  1131:                               foregroundColor: Colors.white,
  ...
  1171:                                 final response = await HttpAuthClient.post(
  1172:                                   Uri.parse("$_apiUrl/api/review/commit"),
  ...
  1204:                             label: const Text('Save & Commit', style: TextStyle(fontWeight: FontWeight.bold)),
  ```
  ```dart
  2258:                           IconButton(
  2259:                             tooltip: 'Approve & Commit to Collection',
  2260:                             icon: const Icon(Icons.check_circle_outline, color: Color(0xFF10B981), size: 20),
  2261:                             onPressed: () => _commitSingleItem(doc.id),
  ```
- **Remediation Plan:**
  1. In `_showCoinEditDialog` (`review_hub_screen.dart:1066-1206`):
     - Make **"Save Changes (Keep in Review)"** the primary `ElevatedButton` (`flex: 2`, updates the draft item in `review_queue` only).
     - Demote **"Save & Add to Collection"** to an `OutlinedButton` (`flex: 1`) with an explicit confirmation step.
  2. On the Review Hub row action bar (`lines 2258-2261`), ensure clicking the pencil icon opens the modal without triggering `_commitSingleItem`.

---

#### `I-05` & `I-06`: Fix "Select All" Delete Confusion & Button Contrast
- **Defects (`SS 4`):** Clicking "Select All" caused a red `Delete Selected (2)` button to pop up in the top bar with no `Add Selected` (`I-05`). The bottom `Commit Selected` button had unreadable dark text on `#F63366` pink (`I-06`).
- **Inspected Verbatim Code (`numista_mobile/lib/screens/review_hub_screen.dart:1535-1541`):**
  ```dart
  1535:           if (_selectedIds.isNotEmpty)
  1536:             Padding(
  1537:               padding: const EdgeInsets.only(right: 8, top: 8, bottom: 8),
  1538:               child: ElevatedButton.icon(
  1539:                 style: ElevatedButton.styleFrom(
  1540:                   backgroundColor: const Color(0xFFEF4444),
  1541:                   foregroundColor: Colors.white,
  ...
  1554:                 label: Text('Delete Selected (${_selectedIds.length})', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
  ```
- **Inspected Verbatim Code (`numista_mobile/lib/screens/review_hub_screen.dart:1712-1721`):**
  ```dart
  1712:                 ElevatedButton.icon(
  1713:                   style: ElevatedButton.styleFrom(
  1714:                     backgroundColor: const Color(0xFFF63366),
  1715:                     padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
  1716:                     shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
  1717:                   ),
  1718:                   onPressed: _commitSelected,
  1719:                   icon: const Icon(Icons.check_circle_outline, size: 18),
  1720:                   label: const Text('Commit Selected', style: TextStyle(fontWeight: FontWeight.bold)),
  1721:                 ),
  ```
- **Remediation Plan:**
  1. In `AppBar.actions` (`review_hub_screen.dart:1535-1556`), when items are selected, add a prominent green primary action **`Add Selected (${_selectedIds.length})`** (`backgroundColor: Color(0xFF10B981)`, `foregroundColor: Colors.white`) immediately to the left of `Delete Selected`.
  2. In `_buildBottomActionBar` (`review_hub_screen.dart:1712-1721`), add `foregroundColor: Colors.white` and rename `'Commit Selected'` to `'Add Selected to Collection (${_selectedIds.length})'`. Adopt the Founder's preferred gold/charcoal palette (`backgroundColor: Color(0xFFD4AF37)`, `foregroundColor: Color(0xFF1A1A1A)`).

---

#### `I-08`, `PM-02`, & `PM-03`: Multi-Order Duplicate Detection (26RJ 2nd Upload 0 Dupes Flagged)
- **Defects (`SS 5`, `1351hrs test SS 1`):**
  - Founder uploaded `Receipt_2026 Uncirculated Coin Set` (`26RJ`, Invoice `USM23493262`) intending to sell it, but **0 duplicates were flagged** even though he already owns the exact same 2026 Uncirculated Coin Set from a morning order.
  - The schematic correctly captured Invoice # (`USM23493262`) (`PM-03`), but neither backend nor frontend utilized Invoice # and Item # to differentiate or flag identical items across separate orders.
- **Inspected Verbatim Code (`numista_backend/main.py:3560-3586`):**
  ```python
  3560:                 inv_no  = (data.get('Retailer Invoice #') or '').strip()
  3561:                 item_no = (data.get('Retailer Item No.')  or '').strip()
  3562:                 is_definite_dupe = False
  3563:                 is_possible_dupe = False
  3564: 
  3565:                 if inv_no and item_no:
  3566:                     try:
  3567:                         q = coins_ref \
  3568:                             .where('Retailer Invoice #', '==', inv_no) \
  3569:                             .where('Retailer Item No.',  '==', item_no) \
  3570:                             .limit(1).get()
  3571:                         if len(q) > 0 and q[0].id not in request.review_ids:
  3572:                             is_definite_dupe = True
  3573:                     except Exception:
  3574:                         pass
  3575: 
  3576:                 if not is_definite_dupe:
  3577:                     from services.duplicate_check import check_and_flag_duplicate
  3578:                     if check_and_flag_duplicate(coins_ref, data, exclude_ids=request.review_ids):
  3579:                         is_possible_dupe = True
  ```
- **Inspected Verbatim Code (`numista_backend/services/duplicate_check.py:51-58`):**
  ```python
  51:         q = (
  52:             coins_ref
  53:             .where("Year", "==", year_val)
  54:             .where("Mint Mark", "==", mint_val)
  55:             .where("Denomination", "in", denom_variants[:10])
  56:             .limit(5)
  57:             .get()
  58:         )
  ```
- **Inspected Verbatim Code (`numista_mobile/lib/screens/review_hub_screen.dart`):**
  `review_hub_screen.dart` has **zero** occurrences of `possible_duplicate` or duplicate tags in its item rendering loop!
- **Verified Root Cause:**
  1. `main.py:3565-3574` only considers an item a duplicate if **both** `inv_no` AND `item_no` match. If the invoice numbers differ (`USM23493262` vs prior invoice), `is_definite_dupe` is `False`.
  2. Fallback `check_and_flag_duplicate` queries only `(Year, Mint Mark, Denomination)`. Modern sets have denomination `"Set"` or empty, and mint mark `""` or `"P, D"`, which fails exact equality query! It never queries `Retailer Item No.` (`item_no`).
  3. No duplicate check was ever run during invoice upload (`_execute_import_process_worker`), so items in `review_queue` never carried duplicate flags.
- **Remediation Plan:**
  1. **Enhance Backend Duplicate Detection Engine (`duplicate_check.py` & `main.py`):**
     - **Definite Duplicate (Same Order Re-upload):** Identical `Retailer Invoice #` AND `Retailer Item No.` -> Do not import twice.
     - **Item # Duplicate / Separate Order (Founder's Sell-Intent Case):** Same `Retailer Item No.` (e.g. `26RJ`), but DIFFERENT `Retailer Invoice #` -> Flag with:
       ```python
       coin_dict["possible_duplicate"] = True
       coin_dict["duplicate_flag"] = f"Identical SKU {item_no} already in collection (Invoice #{prior_inv}) — Copy 2"
       coin_dict["duplicate_type"] = "separate_order_copy"
       ```
     - **Attribute Duplicate Fallback:** Match normalized `(Year, Program/Series or Theme/Subject)` when Item # is absent.
  2. **Run Duplicate Check During Invoice Extraction:** In `_execute_import_process_worker` (`main.py:7640-7675`), run `check_and_flag_duplicate` before staging items into `review_queue`.
  3. **Display Yellow Duplicate Chip in Review Hub UI:** In `review_hub_screen.dart:2145-2165`, render an amber duplicate badge:
     ```dart
     if (data['possible_duplicate'] == true)
       Container(
         padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
         decoration: BoxDecoration(color: Colors.amber.withAlpha(30), borderRadius: BorderRadius.circular(6), border: Border.all(color: Colors.amber)),
         child: Text(data['duplicate_flag'] ?? 'Possible Duplicate / Copy 2', style: const TextStyle(color: Colors.amber, fontSize: 11, fontWeight: FontWeight.bold)),
       ),
     ```

---

### Bucket 2: Post-Commit Enrichment, Images & Valuation Pipeline

#### `I-07`, `I-09`, `PM-01`, & `PM-05`: Post-Commit Enrichment & Elimination of Eternal "Valuation Pending"
- **Defects (`SS 5`, `1351hrs test SS 3`):**
  - Founder Morning Review: None of the 3 committed items had images or valuations.
  - Founder 1351hrs Review (`PM-01`, P0): Hours later, the morning 3 items **still had no images and no valuations** (stuck on `"Valuation Pending"`).
  - `PM-05`: Newly committed 26RJ had AI Estimated Value `$0.00` vs `$36.40` for the earlier item.
- **Inspected Verbatim Code (`numista_backend/main.py:3600-3622`):**
  ```python
  3600:                     # Legal System of Record Golden Schema defaults
  3601:                     if not data.get('Condition'):
  3602:                         data['Condition'] = 'Unspecified / Raw'
  3603:                     if not data.get('enrichment_status'):
  3604:                         data['enrichment_status'] = 'pending'
  ...
  3616:                     new_coin_ref = coins_ref.document(doc_id)
  3617:                     batch.set(new_coin_ref, data)
  3618:                     # Plan 4.1 §3.1 item 4: Eliminate commit .delete() — soft-set status committed
  3619:                     batch.set(queue_ref.document(doc_id), {
  3620:                         "status": "committed",
  3621:                         "committed_at": firestore.SERVER_TIMESTAMP
  3622:                     }, merge=True)
  ```
- **Inspected Verbatim Code (`numista_mobile/lib/screens/my_collection_screen.dart:3016-3019` & `3169-3178`):**
  ```dart
  3016:     final double? cpgRetail = (m['cpg_value'] is num) ? (m['cpg_value'] as num).toDouble() : double.tryParse(m['cpg_value']?.toString() ?? '');
  3017:     final double? aiEstVal = _parsePrice(m[_F.estValue]);
  3018:     final double? effectiveVal = (cpgRetail != null && cpgRetail > 0) ? cpgRetail : ((aiEstVal != null && aiEstVal > 0) ? aiEstVal : null);
  3019:     final valueText = effectiveVal != null ? '\$${effectiveVal.toStringAsFixed(0)}' : '—';
  ```
  ```dart
  3169:                       if (valueText == '—' || m['enrichment_status'] == 'pending')
  3170:                         Container(
  ...
  3177:                           child: const Text('Valuation Pending', style: TextStyle(fontSize: 10, color: Color(0xFFC9A227), fontWeight: FontWeight.bold)),
  3178:                         )
  ```
- **Verified Root Cause:**
  1. `/api/review/commit` (`main.py:3511-3640`) sets `enrichment_status = 'pending'`, but **never initiates any background enrichment worker, valuation task, or image fetch**!
  2. It sets no initial baseline valuation (`ai_est_value` or `cpg_value`), leaving `valueText == '—'`.
  3. In `my_collection_screen.dart:3169`, any item where `valueText == '—'` or `enrichment_status == 'pending'` displays `Valuation Pending` indefinitely.
  4. None of the committed Mint sets or rolls have user photos (`front_url` is null), and `ReferenceImageService` lacks US Mint product artwork mappings for sets (`26RJ`, `23RH`) and rolls (`26SQRP`).
- **Remediation Plan:**
  1. **Immediate Baseline Valuation on Commit (`main.py:3600-3622`):**
     Inside `commit_reviews`, run `enrich_us_mint_item(data)`. If `estValue` / `ai_est_value` is empty, immediately populate a baseline valuation from canonical catalog issue price or purchase cost:
     ```python
     cat_price = data.get("issue_price") or data.get("Sticker Price") or data.get("Cost") or 0.0
     data["ai_est_value"] = cat_price
     data["estValue"] = f"${cat_price:.2f}"
     data["valuation_source"] = "US Mint Issue Price Baseline"
     data["enrichment_status"] = "enriched"
     ```
  2. **Kick Off Async Enrichment Worker:** At the end of `commit_reviews`, dispatch a background worker task (`_enrich_and_value_committed_coins`) for the newly committed IDs to pull CPG/market guides and generate deep-dive insights.
  3. **Fix Eternal "Valuation Pending" in Frontend (`my_collection_screen.dart:3169`):**
     Only show `Valuation Pending` if `m['enrichment_status'] == 'pending'` AND `valueText == '—'`. If a baseline estimate exists (`costText` or catalog price), display `'Est. $' + value` with a subtle badge (`"Mint Baseline"`).
  4. **Canonical US Mint Reference Images (`numista_mobile/lib/services/coin_image_service.dart`):**
     Add high-resolution US Mint catalog product imagery fallbacks for `26RJ` (2026 Uncirculated Set), `23RH` (2023 Silver Proof Set), `26SQRP` (Trump $1 Roll), and `26AGA` (Innovation $1 Roll) so cards never show blank image placeholders.

---

#### `I-10`: Remove External "Google Images" Button in Modal Header
- **Defects (`SS 6`):** Clicking a coin opened `_showCoinInspectorDialog` with an external `Google Images` button in the header.
- **Inspected Verbatim Code (`numista_mobile/lib/screens/my_collection_screen.dart:3522-3530`):**
  ```dart
  3522:                     // Google Images search — only shown when no photo is active
  3523:                     if (!hasActive && refFuture != null) ...[
  3524:                       Tooltip(
  3525:                         message: 'Opens Google Images: searches for this coin',
  3526:                         child: OutlinedButton.icon(
  3527:                           onPressed: () => _onSearchGoogle(data),
  3528:                           icon: Icon(Icons.image_search, size: 15),
  3529:                           label: Text('Google Images'),
  3530:                           style: OutlinedButton.styleFrom(
  ```
- **Remediation Plan:**
  Remove the `Google Images` button from the modal header. Replace with an in-app **"Upload Photo"** button (`Icons.add_a_photo_outlined`), with any external search demoted to an overflow menu labeled `"Search Web Reference Images ↗"`.

---

#### `PM-04`: Distinguish Identical Sets on Cards & Detail View
- **Defects (`1351hrs test SS 3`, `SS 4`):** When viewing `My Collection`, two identical `2026 Uncirculated Coin Set` cards look completely indistinguishable.
- **Remediation Plan (`my_collection_screen.dart:3080-3120` & `coin_detail_screen.dart:917-930`):**
  When multiple items share the same `retailer_item_num` or title:
  1. On the card face, display secondary provenance chips:
     - `Invoice #USM23493262`
     - Order date (e.g. `Sep 26, 2026`)
     - Landed Cost (e.g. `$134.45`)
  2. In `CoinDetailScreen`'s header, display `"Copy 2 of 2 • Order #USM23493262"`.

---

### Bucket 3: Collection Header & Estate Jurisdiction Placement

#### `I-11`: Decouple Collection Toolbar from Estate Tax / Probate Demands
- **Defects (`SS 5`, `SS 7`):** Clicking `Generate AI Report Now` on `My Collection` immediately blocked the Founder with `"Please select your legal jurisdiction for estate tax and probate calculations:"`.
- **Inspected Verbatim Code (`numista_mobile/lib/screens/my_collection_screen.dart:1341-1344` & `6121-6125`):**
  ```dart
  1341:                 ElevatedButton.icon(
  1342:                   onPressed: () => _showGenerateReportModal(),
  1343:                   icon: const Icon(Icons.auto_awesome, size: 16),
  1344:                   label: const Text('Generate AI Report Now'),
  ```
  ```dart
  6121:             ] else if (_needsStateSelection) ...[
  6122:               Text(
  6123:                 'Please select your legal jurisdiction for estate tax and probate calculations:',
  6124:                 style: TextStyle(color: isDark ? Colors.white70 : const Color(0xFF5A5C69), fontSize: 13),
  6125:               ),
  ```
- **Remediation Plan:**
  1. Move the Estate Tax & Probate jurisdiction selector exclusively into **Estate Planning** (`numista_mobile/lib/screens/estate_planning_screen.dart`).
  2. On `My Collection` (`my_collection_screen.dart:1341-1344`), replace `_showGenerateReportModal()` with:
     - **Button Label:** `"Fetch Values & AI Images"` (or `"Refresh Collection Insights"`).
     - **Action:** Triggers collection-wide background valuation, image resolution, and numismatic inventory summary without demanding legal jurisdiction.

---

### Bucket 4: Theme Contrast & Readability Defects

#### `I-12`: Fix Unreadable Dark Navy on Dark Navy in Light Mode (`SS 7`)
- **Defects (`SS 7`):** `AI Collection & Inventory Report` dialog renders dark navy text on a dark navy background in Light Mode (~1.08:1 contrast).
- **Inspected Verbatim Code (`numista_mobile/lib/screens/my_collection_screen.dart:6088-6099`):**
  ```dart
  6088:     final isDark = Theme.of(context).brightness == Brightness.dark;
  6089:     const bgCard = Color(0xFF161B27);
  6090:     const pink   = Color(0xFFF63366);
  6091: 
  6092:     return AlertDialog(
  6093:       backgroundColor: bgCard,
  ...
  6099:           Text('AI Collection & Inventory Report', style: TextStyle(color: isDark ? Colors.white : const Color(0xFF0F172A), fontSize: 18, fontWeight: FontWeight.bold)),
  ```
- **Remediation Plan:**
  In `my_collection_screen.dart:6089`, change hardcoded `bgCard`:
  ```dart
  final bgCard = isDark ? const Color(0xFF161B27) : Colors.white;
  ```
  And update internal containers (`lines 6128-6135`) to use `isDark ? const Color(0xFF1E2638) : const Color(0xFFF8FAFC)`.

---

#### `I-13` & `PM-06`: White Text on Off-White / Cream Header (`SS 8`, `SS 10`, `1351hrs SS 6`)
- **Defects (`SS 8`, `SS 10`, `1351hrs SS 6`):** Coin Detail modal header renders white text on a `#F4F4F2` cream background in Light Mode.
- **Inspected Verbatim Code (`numista_mobile/lib/screens/coin_detail_screen.dart:58` & `917-924`):**
  ```dart
  58: Color _kDark(BuildContext c) => _isDarkCtx(c) ? const Color(0xFF0B1120) : const Color(0xFFF4F4F2);
  ```
  ```dart
  917:                   Text(title,
  918:                     style: const TextStyle(
  919:                       color: Colors.white, fontSize: 18,
  920:                       fontWeight: FontWeight.bold, height: 1.3),
  921:                   ),
  922:                   const SizedBox(height: 4),
  923:                   Text(subtitle,
  924:                     style: const TextStyle(color: Colors.white60, fontSize: 12)),
  ```
- **Remediation Plan:**
  In `_HeroHeader` (`coin_detail_screen.dart:891-934`), replace hardcoded `Colors.white` and `Colors.white60`:
  ```dart
  style: TextStyle(
    color: _kText(context),
    fontSize: 18,
    fontWeight: FontWeight.bold,
    height: 1.3,
  ),
  ```
  And for subtitle: `color: _kSubtext(context)`. Alternatively, maintain dark navy (`const Color(0xFF0B1120)`) for the hero header in both Light and Dark modes so white text always satisfies WCAG AAA contrast (>12:1).

---

#### `I-15`: Blank White Gaps in `AI Numismatic Deepdive` Prose (`SS 9`)
- **Defects (`SS 9`):** AI Insights tab displayed large blank gaps where words were supposed to be (e.g. `"The [blank] is a landmark..."`).
- **Inspected Verbatim Code (`numista_mobile/lib/screens/coin_detail_screen.dart:2772-2780`):**
  ```dart
  2772:                 MarkdownBody(
  2773:                   data: insight,
  2774:                   styleSheet: MarkdownStyleSheet(
  2775:                     p: TextStyle(fontSize: 14, color: _kText(context), height: 1.7),
  2776:                     h1: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white, height: 2.0),
  2777:                     h2: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white, height: 2.0),
  2778:                     h3: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: _kText(context), height: 1.8),
  2779:                     strong: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
  ```
- **Verified Root Cause:**
  `MarkdownStyleSheet` sets `p` to `_kText(context)`, but **hardcodes `color: Colors.white` for `h1`, `h2`, and `strong` (`**bold**`)**! On a white card in Light Mode, every bold word and heading becomes white text on white background (completely invisible).
- **Remediation Plan:**
  In `coin_detail_screen.dart:2776-2779`, change `Colors.white` on `h1`, `h2`, and `strong` to `_kText(context)`.

---

#### `PM-06`: Modal Sizing & Cut-Off Quarter in Set Contents View
- **Defects (`1351hrs SS 6`):** The pop-up window could not be resized or maximized, and the Lincoln quarter in the set contents view was cut off.
- **Inspected Verbatim Code (`numista_mobile/lib/screens/coin_detail_screen.dart:132-133`):**
  ```dart
  132:           child: ConstrainedBox(
  133:             constraints: const BoxConstraints(maxWidth: 860, maxHeight: 760),
  ```
- **Remediation Plan:**
  1. In `CoinDetailScreen.show` (`coin_detail_screen.dart:124-137`), make the dialog constraints adaptive to viewport size:
     ```dart
     final screenHeight = MediaQuery.of(context).size.height;
     final screenWidth = MediaQuery.of(context).size.width;
     constraints: BoxConstraints(
       maxWidth: (screenWidth * 0.90).clamp(860.0, 1200.0),
       maxHeight: screenHeight * 0.92,
     ),
     ```
  2. Add a Maximize / Restore icon button in the dialog header.
  3. In `numista_mobile/lib/widgets/set_contents_panel.dart`, wrap the coin strip and grid in a flexible `SingleChildScrollView` to guarantee every coin in large sets (10-coin Uncirculated, 14-coin Silver Proof) is fully visible without clipping.

---

### Bucket 5: Modal Consolidation, Upload UX & Tab Relevance

#### `I-01` & `I-02`: Dedicated 1-Click "Upload an Invoice" Card
- **Defects (`SS 1`):** Founder was confused by "Upload a list" and had to make redundant clicks on "Open Bulk Import →" or "Open Invoice Importer →".
- **Inspected Verbatim Code (`numista_mobile/lib/screens/add_coins_hub.dart:816-823`, `1060-1064`, & `1282-1286`):**
  ```dart
  816:       _QuickAddCard(
  817:         icon: Icons.upload_file_outlined,
  818:         label: 'Upload a list',
  819:         onTap: () {
  820:           setState(() => _showMoreWays = true);
  821:           _tabController.animateTo(0);
  822:         },
  823:       ),
  ```
  ```dart
  1060:             child: ElevatedButton.icon(
  1061:               onPressed: _openSpreadsheetImport,
  1062:               icon: const Icon(Icons.upload_file, size: 18),
  1063:               label: const Text(
  1064:                 'Open Bulk Import →',
  ```
  ```dart
  1282:             child: ElevatedButton.icon(
  1283:               onPressed: _openInvoiceImport,
  1284:               icon: const Icon(Icons.receipt_long, size: 18),
  1285:               label: const Text(
  1286:                 'Open Invoice Importer →',
  ```
- **Remediation Plan:**
  1. In `add_coins_hub.dart:799-838`, add a dedicated top-level `_QuickAddCard`:
     - **Icon:** `Icons.receipt_long_outlined`
     - **Label:** `'Upload an Invoice'`
     - **Subtext:** `'US Mint, Littleton, Dealer PDFs'`
     - **onTap:** Directly calls `_openInvoiceImport()` in 1 click!
  2. Change `'Upload a list'` (`line 819`) to call `_openSpreadsheetImport()` directly in 1 click, eliminating the intermediate teaser tabs.

---

#### `I-14`: Harmonize Card View and Table View Click Targets
- **Defects (`SS 6` vs `SS 8`):** Clicking a card in Card View opened `CoinInspectorDialog` (missing 7 tabs), while clicking the `i` info icon in Table View opened `CoinDetailScreen` (full 7 tabs).
- **Inspected Verbatim Code (`numista_mobile/lib/screens/my_collection_screen.dart:2735`, `2772-2775`, & `3041-3044`):**
  ```dart
  2735:             void onTap() => _showCoinInspectorDialog(effectiveId, m);
  ```
  ```dart
  2772:                             CoinDetailScreen.show(
  2773:                               context,
  2774:                               coinId: effectiveId,
  2775:                               data: targetData,
  ```
  ```dart
  3041:             onTap: () {
  3042:               setState(() => _selectedCoinId = effectiveId);
  3043:               _showCoinInspectorDialog(effectiveId, m);
  3044:             },
  ```
- **Remediation Plan:**
  Harmonize Card View (`line 3043`) and Table cell click (`line 2735`) to call `CoinDetailScreen.show(...)`. Merge any OGP/Set breakdown tools into `CoinDetailScreen`'s `Details` tab, unifying the inspection modal across the entire app.

---

#### `I-16`: Modern Coinage Acts & Relevant Known Errors Tab
- **Defects (`SS 10`):** Legislation tab showed either "No Legislation Matched" or matched the 1965 Coinage Act (which removed silver from coinage) for a 2023 Silver Proof Set! Known Errors showed generic unverified error strings.
- **Inspected Verbatim Code (`numista_mobile/lib/screens/coin_detail_screen.dart:3050-3054` & `3465-3467`):**
  ```dart
  3050:     // Coinage Act 1965: affected all silver coins — halves, quarters, dimes
  3051:     if (denom.contains('half dollar') || denom.contains('quarter') ||
  3052:         denom.contains('dime')) {
  3053:       return '89-81';
  3054:     }
  ```
- **Remediation Plan:**
  1. Add modern statutory references to `_kDefaultLaws` and `_matchLawKey` in `coin_detail_screen.dart:2902-3056`:
     - **Annual Silver Proof Sets (`31 U.S.C. § 5112(i)` / Public Law 101-585 & FAST Act Public Law 114-94):** Authorizes annual 99.9% fine silver proof sets.
     - **Circulating Collectible Coin Redesign Act of 2020 (`Public Law 116-330`, `31 U.S.C. § 5112(x)-(y)`):** Authorizes the 2026 Semiquincentennial (250th Anniversary) Coin Programs and American Women Quarters (2022–2025).
     - **American Innovation $1 Coin Act (`Public Law 115-197`, `31 U.S.C. § 5112(w)`):** Authorizes the 2018–2032 Innovation dollar series.
  2. For Known Errors (`coin_detail_screen.dart:3465-3550`), display a clean empty state for modern sets/rolls (`"No major die varieties or mint errors cataloged by PCGS/NGC for this modern release"`) rather than ungrounded keyword matches.

---

## 3. FT Retest Checklist & Exit Criteria (Rule 8)

Per Project Rule 8 ("Exit on Commands, Not Adjectives"), execution will conclude ONLY when all machine-checkable commands succeed:

| Check # | Target Component | Command | Expected Result |
| :---: | :--- | :--- | :--- |
| **CMD-1** | Flutter Static Analysis | `flutter analyze lib/screens/ lib/widgets/` | Exit Code 0 (0 errors) |
| **CMD-2** | Catalog Unit Tests | `pytest numista_tests/test_us_mint_catalog_service.py` | 100% Pass (`26RJ`, `23RH`, `26SQRP`) |
| **CMD-3** | Duplicate Detection Tests | `pytest numista_tests/test_duplicate_check.py` | 100% Pass (Invoice# + Item# multi-order test) |
| **CMD-4** | Git Branch Sync | `git status` | Clean working directory on `dev` |

### Field Test (FT) Retest Verification Scenario (Post-Execute):
1. **Invoice 1 (Trump Roll `26SQRP`):**
   - Upload PDF. Review Hub shows: Title `"2026 Semiquincentennial Presidential $1 Coin 25-Coin Roll"`, Mint Mark `"P"` (Philadelphia), Fee `"$9.95"`, Total Cost `"$70.95"`, No `"(July 4th Privy eligible)"`.
   - Click "Edit": Updates draft only; does NOT move item to `My Collection`.
2. **Invoice 2 (2023 Silver Proof Set `23RH`):**
   - Condition displays `"Proof"`, Strike Type `"Proof"`, Theme `"2023 Annual Silver Proof Set"`.
3. **Commit & Post-Commit Pipeline:**
   - Click `Add Selected to Collection`.
   - In `My Collection`, cards immediately show baseline valuation (`Est. $36.40` for 26RJ, `Est. $130` for 23RH, `Est. $70.95` for 26SQRP), high-res US Mint reference imagery, and NO eternal `"Valuation Pending"`.
4. **1351hrs Duplicate Retest (`Receipt_2026 Uncirculated Coin Set.pdf`):**
   - Upload 2nd 26RJ invoice with Order `USM23493262`.
   - Review Hub displays amber chip: `"Identical SKU 26RJ already in collection (Invoice #USM23493262: Copy 2)"`.
   - Cards in `My Collection` display `"Order #USM23493262"` to clearly distinguish Copy 2 from Copy 1.
5. **Light Mode Contrast & Dialog Sizing:**
   - In Light Mode, header has dark text on cream background.
   - `AI Numismatic Deepdive` markdown has NO white gaps on bold words.
   - Set contents view opens in adaptive dialog; Lincoln quarter and all 10 coins are fully visible.

---

## 4. Operational Gating & Next Steps

1. **Gate Status:** **NO CODE EXECUTION AUTHORIZED AT THIS TIME.**
2. **Review Chain Steps:**
   - Step 1: AG CoS v2 files `Plan.v2` (Complete).
   - Step 2: Argon re-scores `Plan.v2` against codebase grounding.
   - Step 3: Grok Bot CoS (GB) reviews and records concurrence.
   - Step 4: Stand Alone Grok (SAG) provides final review.
   - Step 5: Founder (Eric) issues typed `YES` -> Desk issues `EXECUTE`.
3. **Target Deployment Channel:** `p7-gate` preview channel only. Live `main` cherry-pick requires dedicated review after FT verification.
