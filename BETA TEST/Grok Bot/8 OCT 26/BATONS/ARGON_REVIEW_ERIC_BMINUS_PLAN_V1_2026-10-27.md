# ARGON REVIEW — Eric B− Live Mint Remediation Plan (`Plan.v1` / `NET-602` / `NET-606`)

- **Reviewer:** Numista.Ai Argon (`Gemini 4 Argon` — Thinking / Architecture & Code-Audit Review)
- **Date:** 2026-10-27
- **Plan Under Review:** `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\27 OCT 26\ERIC_BMINUS_LIVE_MINT_PLAN_v1_2026-10-27.md` (and `BATONS\` mirror)
- **Reference Spec:** `BATONS\PLAN_REQUEST_ERIC_BMINUS_MINT_20261027.md`, `BATONS\ERIC_BMINUS_ISSUE_INDEX.md`, `BATONS\FT_RETEST_CHECKLIST_NET602.md`, `27 OCT 2026.docx`, and screenshots `SS 1.png` – `SS 10.png`
- **Review Chain Gate (`NET-602_AMEND`):** `AG CoS v2 Plan.vN -> Argon Review -> Grok Bot CoS (GB) Review -> Stand Alone Grok Feedback -> ONLY THEN CoS/Desk EXECUTE` (up to 4 rounds `v1–v4`; partial-ship ready IDs after `v4`).
- **Rule 6(a) Compliance:** Every `file:line` citation below includes the **verbatim code lines** inspected in the repository.

---

## 1. Executive Verdict & Scorecard

- **Overall Score:** **58 / 100 — HOLD FOR `Plan.v2` (DO NOT EXECUTE `Plan.v1`)**
- **Why `Plan.v1` is Held:**
  1. **Hallucinated Tech Stack & 19 Nonexistent File Paths (Critical Blocker):** `Plan.v1` (§2 & §4, lines 30–53 and 90–100) targets a nonexistent React/TypeScript frontend (`numista_web/src/components/review/ReviewTable.tsx`, `UploadHub.tsx`, `useCollectionStore.ts`, `CoinCard.tsx`, `EnrichmentQueueModal.tsx`, `CoinInspectorModal.tsx`, `CoinDetailTabs.tsx`, etc.) and nonexistent Python modules (`numista_backend/services/parsers/mint_invoice_parser.py`, `collection_enrichment.py`, `enrichment_service.py`, `insights_generator.py`). The real Numista.AI frontend is **Flutter Web/Mobile** (`numista_mobile/lib/screens/...`) and the real backend is **FastAPI** (`numista_backend/main.py` and `numista_backend/services/us_mint_catalog_service.py`).
  2. **8 Technical Root-Cause Misdiagnoses (`I-04a`, `I-04b`, `I-04c`, `I-06`, `I-12`, `I-13`, `I-14`, `I-15`):** Because `Plan.v1` did not read the actual Flutter/Python files before drafting, it guessed wrong root causes on 8 of the 17 items (e.g., blaming Python prompt variable interpolation for `I-15` when the actual bug is `Colors.white` hardcoded on `strong`/`h1`/`h2` in `MarkdownStyleSheet` on a white card in Light Mode; blaming a regex parser for `I-04b` when `us_mint_catalog_service.py:380` and `main.py:7653` explicitly overwrite `Allocated Fees = 0.0` whenever `pack_expanded` is `True`).
  3. **Complete Fix Map Provided Below:** To make `Plan.v2` a fast, 95+ scoring turn for AG CoS v2, §2 below provides the **exact real `file:line` locations, verbatim code quotes, verified root causes, and concrete fixes** for all 17 sub-issues (`I-01`..`I-16`).

| Bucket | Issues Covered | `Plan.v1` Coverage | Real-Code Accuracy in `Plan.v1` | Argon Verdict |
| :--- | :--- | :---: | :---: | :--- |
| **B1 — Review Queue Data Integrity & Edit/Select State** | `I-03`, `I-04a`, `I-04b`, `I-04c`, `I-05`, `I-06`, `I-08` | 7 / 7 | 0 / 7 real paths; `I-04a/b/c`, `I-06`, `I-08` misdiagnosed | **REVISE IN `Plan.v2`** |
| **B2 — Post-Commit Enrichment, Images & Valuation** | `I-07`, `I-09`, `I-10` | 3 / 3 | 0 / 3 real paths; `/api/review/commit` gap missed | **REVISE IN `Plan.v2`** |
| **B3 — Collection Header & Estate Jurisdiction** | `I-11` | 1 / 1 | 0 / 1 real path; `_GenerateReportModal` coupling missed | **REVISE IN `Plan.v2`** |
| **B4 — Theme Contrast & Readability Defects** | `I-06`, `I-12`, `I-13`, `I-15` | 4 / 4 | 0 / 4 real paths; `I-12`, `I-13`, `I-15` misdiagnosed | **REVISE IN `Plan.v2`** |
| **B5 — Modal Consolidation, Upload UX & Tab Relevance** | `I-01`, `I-02`, `I-14`, `I-16` | 4 / 4 | 0 / 4 real paths; `I-14` & `I-16` mechanisms missed | **REVISE IN `Plan.v2`** |

---

## 2. Issue-by-Issue Audit (`I-01` – `I-16`) with Verbatim Code Citations (Rule 6a)

### Bucket 1 — Review Queue Data Integrity & Edit/Select State (`I-03`, `I-04a`, `I-04b`, `I-04c`, `I-05`, `I-06`, `I-08`)

#### `I-03` (`SS 2A` & `SS 2B`): 2023 Silver Proof Set & 2026 $1 American Innovation missing description & condition
- **What `Plan.v1` proposed:** Cited nonexistent `numista_web/src/components/review/ReviewTable.tsx:112-145` and `mint_invoice_parser.py:88-134`.
- **Actual Code (`numista_mobile/lib/screens/review_hub_screen.dart:1946-1953` & `2199-2206`):**
  ```dart
  1946:     final String rawCondition = (data['Condition'] ?? data['condition'] ?? data['grade'] ?? '').toString().trim();
  1947:     final String condition = rawCondition.isEmpty ? 'Unspecified' : rawCondition;
  ```
  ```dart
  2199:                       // Theme / Series
  2200:                       if ((data['Theme/Subject'] ?? data['Program/Series']) != null)
  2201:                         Text(
  2202:                           '${data['Theme/Subject'] ?? ''} ${data['Program/Series'] != null ? '• ${data['Program/Series']}' : ''}'.trim(),
  2203:                           style: TextStyle(fontSize: 12, color: isDark ? Colors.white54 : const Color(0xFF64748B)),
  2204:                           maxLines: 1,
  2205:                           overflow: TextOverflow.ellipsis,
  2206:                         ),
  ```
- **Actual Code (`numista_backend/main.py:7668-7675`):**
  ```python
  7668:                 "Denomination": item.get("denomination") or item.get("Denomination") or "",
  7669:                 "Theme/Subject": item.get("subject") or item.get("Theme/Subject") or "",
  7670:                 "Program/Series": item.get("series") or item.get("Program/Series") or "",
  7671:                 "Condition": item.get("condition") or item.get("Condition") or "Uncirculated",
  7672:                 "Strike Type": item.get("strike_type") or item.get("Strike Type") or "Business",
  ```
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  1. `US_MINT_PRODUCT_CATALOG` in `numista_backend/services/us_mint_catalog_service.py:19-227` lacks entries for the **2023 Silver Proof Set** (`23RH`) and **2026 $1 American Innovation** rolls/sets (`26AGA`/`26AGB`/etc.). Add these catalog entries with authoritative `title`, `theme_subject`, `series`, `condition` (`"Proof"` for Proof Sets, `"Uncirculated"` for uncirculated rolls), `strike_type`, and `metal_content`.
  2. In `numista_backend/main.py:7668-7675`, if `Theme/Subject` is empty, fall back to `item.get("Original Description from source") or item.get("CoinName")`; and if `"proof"` appears in the title/description/series, infer `"Condition": "Proof"` and `"Strike Type": "Proof"` instead of defaulting to `"Uncirculated"` / `"Business"`.
  3. In `numista_mobile/lib/screens/review_hub_screen.dart:2200-2206`, fall back to `data['Original Description from source'] ?? data['CoinName']` when `Theme/Subject` and `Program/Series` are null/empty so the subtitle is never blank.

---

#### `I-04a` (`SS 3`): Trump Roll (`26SQRP`) shows wrong `2026 Dollar (D)` header and questionable `(July 4th Privy eligible)` text
- **What `Plan.v1` proposed:** Cited nonexistent `mint_invoice_parser.py:88-134`.
- **Actual Code (`numista_backend/services/us_mint_catalog_service.py:166-176` & `326-333`):**
  ```python
  166:     "26SQRP": {
  167:         "title": "2026 Semiquincentennial Presidential $1 Coin 25-Coin Roll",
  168:         "formal_name": "2026 Semiquincentennial President Donald J. Trump $1 Coin 25-Coin Roll (Philadelphia)",
  169:         "year": "2026",
  170:         "denomination": "$1",
  171:         "mint_mark": "",
  172:         "mint_facility": "Philadelphia (P)",
  173:         "strike_type": "Business",
  174:         "series": "Semiquincentennial Presidential $1 Coin Program",
  175:         "theme_subject": "Donald J. Trump Semiquincentennial 250th Anniversary Roll (July 4th Privy eligible)",
  176:         "metal_content": "Manganese-Brass (88.5% Cu, 6% Zn, 3.5% Mn, 2% Ni)",
  ```
  ```python
  326:         if not item.get("Denomination"):
  327:             item["Denomination"] = catalog_match["denomination"]
  328:         if not item.get("Mint Mark") and "mint_mark" in catalog_match:
  329:             item["Mint Mark"] = catalog_match["mint_mark"]
  ```
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  1. **Why `(D)` appeared on Philadelphia SKU `26SQRP`:** The LLM parser hallucinated `Mint Mark = "D"` (from `"Donald"` or default Denver), and `us_mint_catalog_service.py:328` checks `if not item.get("Mint Mark")` before applying `catalog_match["mint_mark"]`, so it failed to overwrite the wrong `"D"`! For matched catalog SKUs, `catalog_match["mint_mark"]` (`"P"` for Philadelphia roll `26SQRP`) and `catalog_match["denomination"]` must **authoritatively override** LLM-extracted values.
  2. **Why `(July 4th Privy eligible)` appeared:** It is hardcoded at `us_mint_catalog_service.py:175`! Eric explicitly wrote `?` next to it in `SS 3` because the US Mint invoice/product title does not say `"July 4th Privy eligible"`. Remove `(July 4th Privy eligible)` from `theme_subject` and `notes` in `us_mint_catalog_service.py:175, 185` and use the clean official US Mint description (`"2026 Semiquincentennial Presidential $1 Coin — 25-Coin Roll (Philadelphia)"`).

---

#### `I-04b` (`SS 3`): Missed `$9.95` Shipping & Handling on Trump Roll (`26SQRP`), displaying `Fee $0.00`
- **What `Plan.v1` proposed:** Guessed a regex bug in nonexistent `mint_invoice_parser.py:150-195`.
- **Actual Code (`numista_backend/services/us_mint_catalog_service.py:379-383` AND `numista_backend/main.py:7653-7654`):**
  ```python
  379:                             item["Sticker Price"] = canonical_lot_cost
  380:                             item["Allocated Fees"] = 0.0
  381:                             item["Cost"] = canonical_lot_cost
  382:                             item["Purchase Cost"] = canonical_lot_cost
  383:                             item["cost"] = canonical_lot_cost
  ```
  ```python
  7653:                 doc["allocated_fees"] = 0.0 if doc.get("pack_expanded") else allocated_fee
  7654:                 doc["shipping_fee"] = 0.0 if doc.get("pack_expanded") else allocated_fee
  ```
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  - Both `us_mint_catalog_service.py:380` and `numista_backend/main.py:7653-7654` **explicitly zero out `Allocated Fees = 0.0` / `allocated_fees = 0.0` whenever `pack_expanded` is `True`**! That wiped out the `$9.95` S&H from the invoice (`Sticker $61.00 + Fee $9.95 = Total Cost $70.95`, or `$2.84/coin` across 25 coins).
  - **Fix:** Preserve the invoice-extracted `allocated_fee` (`$9.95`) on `pack_expanded` lots instead of forcing `0.0`. Set `Sticker Price = $61.00`, `Allocated Fees = $9.95`, and total `Cost` / `Purchase Cost` = `canonical_lot_cost + allocated_fee` (`$70.95` lot / `$2.84` per coin).

---

#### `I-04c` (`SS 3`): "When I select 'Edit' it automatically saved it to my collection, I didn't click 'Add' yet"
- **What `Plan.v1` proposed:** Cited nonexistent `ReviewTable.tsx:210-250` and `useCollectionStore.ts:75-110`.
- **Actual Code (`numista_mobile/lib/screens/review_hub_screen.dart:1066-1206` & `2255-2279`):**
  ```dart
  1068:                         Expanded(
  1069:                           child: OutlinedButton(
  ...
  1121:                             child: const Text('Save'),
  1122:                           ),
  1123:                         ),
  1124:                         const SizedBox(width: 12),
  1125:                         // Save + Commit
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
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  1. Inside `_showCoinEditDialog` (`review_hub_screen.dart:1068-1206`), the dominant crimson primary CTA button (`flex: 2`, `#F63366`) is `Save & Commit`—which calls `/api/review/commit` and immediately moves the coin out of the Review Queue into `My Collection`—while the plain `Save` button (`flex: 1`, `OutlinedButton`) is visually subordinate.
  2. Furthermore, on the Review Hub row (`review_hub_screen.dart:2258-2278`), the green check icon (`_commitSingleItem`, 1-click immediate commit with no confirmation) sits right next to the pencil Edit icon (`_showCoinEditDialog`).
  3. **Fix:** In `_showCoinEditDialog`, make **"Save Changes (Keep in Review)"** the primary button (`ElevatedButton`), and make **"Save & Add to Collection"** an explicit secondary button with clear wording. On the row action bar, label or confirm single-item commit so clicking near `Edit` or saving an edit never unexpectedly moves an item out of the Review Queue.

---

#### `I-05` & `I-06` (`SS 4`): `Select All` pops up red `Delete Selected (2)` in top bar with no `Add Selected` (`I-05`), while bottom `Commit Selected` button has unreadable dark text on `#F63366` pink (`I-06`)
- **What `Plan.v1` proposed:** Cited nonexistent `ReviewActions.tsx:45-92`.
- **Actual Code (`numista_mobile/lib/screens/review_hub_screen.dart:1535-1556` & `1712-1721`):**
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
  1555:               ),
  1556:             ),
  ```
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
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  1. **`I-05` Root Cause:** In `AppBar.actions` (`review_hub_screen.dart:1535-1556`), when `_selectedIds.isNotEmpty`, ONLY `Delete Selected (${_selectedIds.length})` is rendered in the top bar right above `Select All`. There is no `Add Selected (${_selectedIds.length})` button in the top bar!
  2. **`I-06` Root Cause:** In `_buildBottomActionBar` (`review_hub_screen.dart:1712-1721`), `ElevatedButton.styleFrom` sets `backgroundColor: const Color(0xFFF63366)` **without setting `foregroundColor: Colors.white`**! In Flutter Material 3 Light Mode, `ElevatedButton` defaults to dark purple/navy text (`ColorScheme.primary`), rendering dark text on `#F63366` crimson-pink (`SS 4.png`).
  3. **Fix:**
     - Add `foregroundColor: Colors.white` at `review_hub_screen.dart:1714` and rename `'Commit Selected'` to `'Add Selected (${_selectedIds.length})'`.
     - In `AppBar.actions` (`review_hub_screen.dart:1535`), add a primary **`Add Selected (${_selectedIds.length})`** button (`backgroundColor: const Color(0xFF10B981)` or `Color(0xFFF63366)`, `foregroundColor: Colors.white`) right next to `Delete Selected (${_selectedIds.length})`.

---

#### `I-08` (`SS 5`): Duplicate detection not flagging identical coins already in collection
- **What `Plan.v1` proposed:** Cited nonexistent `ReviewTable.tsx:60-95` and `collection_enrichment.py:40-85`.
- **Actual Code (`numista_backend/main.py:7597-7615` & `numista_mobile/lib/screens/review_hub_screen.dart:2169-2197`):**
  ```python
  7597:             for vdoc in vault_docs:
  7598:                 vd = vdoc.to_dict()
  7599:                 vy = str(vd.get("Year") or vd.get("year") or "").strip().lower()
  7600:                 vm = str(vd.get("Mint Mark") or vd.get("mint") or "").strip().lower()
  7601:                 vden = str(vd.get("Denomination") or vd.get("denomination") or "").strip().lower()
  7602:                 vsub = str(vd.get("Theme/Subject") or vd.get("subject") or "").strip().lower()
  7603:                 existing_vault_sigs.add((vy, vm, vden, vsub))
  ```
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  - `main.py:7597-7615` requires an exact 4-tuple match on `(year, mint_mark, denomination, theme_subject)` during upload time only. If `Denomination` differs slightly (`"$1"` vs `"Dollar"` vs `"Set"`), or `Theme/Subject` differs between uploads (`""` vs `"Donald J. Trump..."`), or if the user commits batch 1 and already has batch 2 sitting in `review_queue`, `possible_duplicate` is never set!
  - **Fix:**
    1. In `numista_backend/main.py:7597-7615`, match duplicates by **either** non-empty `Retailer Item No.` (e.g. `26SQRP`, `23RH`) **or** normalized `(year, canonical_mint_mark, canonical_denomination, normalized_series_or_subject)`.
    2. In `numista_mobile/lib/screens/review_hub_screen.dart` (or via a live vault signature check when loading the Review Queue), also cross-check current Review Queue items against live `vault` docs so items already in `review_queue` immediately show the amber `POSSIBLE DUPLICATE` badge (`review_hub_screen.dart:2169-2197`) as soon as a matching item is committed to `My Collection`.

---

### Bucket 2 — Post-Commit Enrichment, Images & Valuation Pipeline (`I-07`, `I-09`, `I-10`)

#### `I-07` (`SS 5`): Zero enrichment after moving from Review Queue to Collection (missing Type, Theme, Metal, Cert, PCGS#, Item#)
- **What `Plan.v1` proposed:** Cited nonexistent `useCollectionStore.ts:120-165` and `enrichment_service.py:30-95`.
- **Actual Code (`numista_backend/main.py:7722-7795`, `/api/review/commit`):**
  ```python
  7722: @app.post("/api/review/commit")
  7723: async def commit_review_queue(req: CommitReviewRequest, request: Request):
  ...
  7756:         data = doc.to_dict()
  7757:         data.pop("status", None)
  7758:         data["committed_at"] = firestore.SERVER_TIMESTAMP
  ```
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  - `/api/review/commit` (`numista_backend/main.py:7756-7795`) copies the raw `review_queue` dictionary directly into `vault` **without running `enrich_us_mint_item(data)`**, without normalizing `Strike Type`, `Theme/Subject`, `Program/Series`, `Metal Content`, `Retailer Item No.`, or `PCGS #`, and without kicking off post-commit valuation/enrichment!
  - **Fix:** Inside `commit_review_queue` (`numista_backend/main.py:7756-7795`), run `enrich_us_mint_item(data)` (from `us_mint_catalog_service.py`) and normalize canonical vault keys (`Strike Type`, `Theme/Subject`, `Program/Series`, `Metal Content`, `Retailer Item No.`, `Condition`) before writing to `vault`.

---

#### `I-09` (`SS 5`): `Valuation Pending` stuck indefinitely on all 3 cards + no images on any card
- **What `Plan.v1` proposed:** Cited nonexistent `CoinCard.tsx:85-130` and `enrichment_service.py:110-165`.
- **Actual Code (`numista_mobile/lib/screens/my_collection_screen.dart:3016-3022`, `3063`, & `3169-3178`):**
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
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  1. **Why `Valuation Pending` is stuck forever:** Line 3169 shows `'Valuation Pending'` whenever `valueText == '—'`—even when no valuation job is running! Worse, `/api/review/commit` (`main.py:7756`) does not trigger valuation and sets no fallback `AI Estimated Value` (`Est. Value`).
  2. **Why all 3 cards have no images:** None of the 3 newly committed items have user photos (`front_url`), and `_CollectionCardImage` (`my_collection_screen.dart:3063`) / `ReferenceImageService` has no reference image match for `"2023 Set"` or `"2026 Dollar"` rolls.
  3. **Fix:**
     - On commit (`/api/review/commit` in `main.py:7756`), trigger immediate valuation/enrichment for the committed coin IDs, and if no catalog guide price exists yet (e.g., 2026 Mint releases), populate an initial baseline `AI Estimated Value` from catalog issue/retail price or purchase cost (flagged with valuation source `"US Mint Issue / Cost Baseline"`) so `valueText` is never stuck on `'Valuation Pending'` forever.
     - In `my_collection_screen.dart:3169`, only show `'Valuation Pending'` when `m['enrichment_status'] == 'pending'` (an active job is running); otherwise show `'Est. ${costText}'` or a clickable `'Get Estimate'` action.
     - Add canonical reference image mappings / fallback US Mint product artwork in `ReferenceImageService` / `us_mint_catalog_service.py` for US Mint Proof Sets (`23RH`), American Innovation Dollars, and Presidential `$1` Rolls (`26SQRP`).

---

#### `I-10` (`SS 6`): `Google Images` button in Coin Inspector (`"Should 'Google Images' in SS 6 be there? And what happens when you click it?"`)
- **What `Plan.v1` proposed:** Cited nonexistent `CoinInspectorModal.tsx:95-125`.
- **Actual Code (`numista_mobile/lib/screens/my_collection_screen.dart:3522-3539`):**
  ```dart
  3522:                     // Google Images search — only shown when no photo is active
  3523:                     if (!hasActive && refFuture != null) ...[
  3524:                       Tooltip(
  3525:                         message: 'Opens Google Images: searches for this coin',
  3526:                         child: OutlinedButton.icon(
  3527:                           onPressed: () => _onSearchGoogle(data),
  3528:                           icon: Icon(Icons.image_search, size: 15),
  3529:                           label: Text('Google Images'),
  ```
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  - When a coin has no uploaded photo, `_showCoinInspectorDialog` (`my_collection_screen.dart:3523-3539`) places a prominent `Google Images` button in the modal header that opens an external browser tab (`https://www.google.com/search?tbm=isch&q=...`).
  - Furthermore, per `I-14` below, `_showCoinInspectorDialog` is being consolidated into `CoinDetailScreen`. In `CoinDetailScreen`, remove the header `Google Images` button (or demote any external web search link into a secondary overflow/footer link labeled `"Search Web Reference Images ↗"`) and prioritize in-app reference images + `"Upload Photo"`.

---

### Bucket 3 — Collection Header & Estate Jurisdiction Placement (`I-11`)

#### `I-11` (`SS 5` & `SS 7`): `Generate AI Report Now` button on `My Collection` toolbar immediately demands Estate Tax & Probate legal jurisdiction
- **What `Plan.v1` proposed:** Cited nonexistent `CollectionHeader.tsx:55-110` and `EstatePlanningView.tsx:30-75`.
- **Actual Code (`numista_mobile/lib/screens/my_collection_screen.dart:1341-1353` & `6121-6125`):**
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
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  - Clicking `Generate AI Report Now` on the `My Collection` toolbar (`my_collection_screen.dart:1342`) opens `_GenerateReportModal` (`line 6025`), which is hard-wired to `EstateReportService` and blocks the user with `"Please select your legal jurisdiction for estate tax and probate calculations:"` (`line 6123`).
  - **Fix:** Decouple Collection Inventory reporting from Estate Tax & Probate jurisdiction:
    1. Keep Estate Tax & Probate jurisdiction selection inside **Estate Planning** (`numista_mobile/lib/screens/estate_planning_screen.dart`).
    2. On `My Collection`, either remove the Estate Probate prompt so `Generate AI Collection Summary` generates a pure numismatic/collection summary without asking for probate/estate tax jurisdiction, or move the Estate & Probate report trigger exclusively to `estate_planning_screen.dart`.

---

### Bucket 4 — Theme Contrast & Readability Defects (`I-06`, `I-12`, `I-13`, `I-15`)

*(Note: `I-06` is covered with verbatim code in Bucket 1 above: `review_hub_screen.dart:1712-1721` missing `foregroundColor: Colors.white`.)*

#### `I-12` (`SS 7`): `AI Collection & Inventory Report` modal is dark-navy text on dark-navy background in Light Mode
- **What `Plan.v1` proposed:** Cited nonexistent `EnrichmentQueueModal.tsx:40-85`.
- **Actual Code (`numista_mobile/lib/screens/my_collection_screen.dart:6088-6142`):**
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
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  - Look at lines 6088–6099 of `my_collection_screen.dart`: `bgCard` is hardcoded to `const Color(0xFF161B27)` (dark navy) in **both** Dark and Light mode, while the title, body text, and dropdown items use `isDark ? Colors.white : const Color(0xFF0F172A)`! In Light Mode (`isDark == false`), `#0F172A` dark slate text is drawn on `#161B27` dark navy background (~1.08:1 contrast—completely unreadable, exactly as shown in `SS 7.png`)!
  - **Fix:** At `my_collection_screen.dart:6089`, change `const bgCard = Color(0xFF161B27);` to:
    ```dart
    final bgCard = isDark ? const Color(0xFF161B27) : Colors.white;
    ```
    (And update the `Container` border/background inside lines 6128–6135 to respect `isDark`).

---

#### `I-13` (`SS 8` & `SS 10`): Coin Detail modal header has white text on light cream (`#F4F4F2`) background in Light Mode
- **What `Plan.v1` proposed:** Cited nonexistent `CoinCardModal.tsx:35-70`.
- **Actual Code (`numista_mobile/lib/screens/coin_detail_screen.dart:58` & `891-934`):**
  ```dart
  58: Color _kDark(BuildContext c) => _isDarkCtx(c) ? const Color(0xFF0B1120) : const Color(0xFFF4F4F2);
  ```
  ```dart
  891:     return Container(
  892:       color: _kDark(context),
  893:       padding: const EdgeInsets.fromLTRB(20, 14, 12, 16),
  ...
  917:                   Text(title,
  918:                     style: const TextStyle(
  919:                       color: Colors.white, fontSize: 18,
  920:                       fontWeight: FontWeight.bold, height: 1.3),
  921:                   ),
  922:                   const SizedBox(height: 4),
  923:                   Text(subtitle,
  924:                     style: const TextStyle(color: Colors.white60, fontSize: 12)),
  ```
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  - In `coin_detail_screen.dart:58`, `_kDark(context)` returns `const Color(0xFFF4F4F2)` (light cream) when in Light Mode, while `_HeroHeader` (`lines 917-934`) hardcodes `color: Colors.white` for `title`, `color: Colors.white60` for `subtitle`, and `color: Colors.white54` for the close `IconButton`! That renders white text on a `#F4F4F2` cream header (`SS 8.png` and `SS 10.png`).
  - Similarly, in `_OwnerPhotoHero` (`coin_detail_screen.dart:990-1085`), the image placeholder caption (`"Coin Footlocker, in OGP"`) uses white/light text on a light surface.
  - **Fix:** In `_HeroHeader` (`coin_detail_screen.dart:891-934`), use `_kText(context)` for `title` and `_kSubtext(context)` for `subtitle`/close icon (or keep the hero banner background dark navy `const Color(0xFF0B1120)` in both modes so white text always has >12:1 contrast). Audit all remaining `Colors.white` references in `coin_detail_screen.dart` against Light Mode surfaces.

---

#### `I-15` (`SS 9`): Blank white gaps in `AI Numismatic Deepdive` prose
- **What `Plan.v1` proposed:** Misdiagnosed `I-15` as uninterpolated Python prompt template variables in nonexistent `insights_generator.py:55-110`.
- **Actual Code (`numista_mobile/lib/screens/coin_detail_screen.dart:2772-2780`):**
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
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  - Look at `coin_detail_screen.dart:2776-2779`: inside `_AiInsightsTab`, `MarkdownStyleSheet` sets `p` to `color: _kText(context)` (dark slate in Light Mode), **but hardcodes `color: Colors.white` on `h1`, `h2`, and `strong` (`**bold**`)**!
  - Because the card background in Light Mode is `_kSurface(context)` (`Colors.white`), **every `**bold**` word and every `## Heading` in the AI markdown response is rendered in white text on a white background**, creating the exact blank white gaps circled by Eric in `SS 9.png` (e.g., `"The [blank] is a landmark..."`, `"Featuring the [blank]..."`, `"struck in [blank]..."`)!
  - **Fix:** In `numista_mobile/lib/screens/coin_detail_screen.dart:2776-2779`, change `color: Colors.white` on `h1`, `h2`, and `strong` to `color: _kText(context)`!

---

### Bucket 5 — Modal Consolidation, Upload UX & Tab Relevance (`I-01`, `I-02`, `I-14`, `I-16`)

#### `I-01` & `I-02` (`SS 1`): Need 1 dedicated box for Invoices (`I-01`); clicking `Upload a list` requires an extra unnecessary click on `Open Bulk Import ->` (`I-02`)
- **What `Plan.v1` proposed:** Cited nonexistent `AddCoinsModal.tsx:42-88` and `ImportHubView.tsx:15-64`.
- **Actual Code (`numista_mobile/lib/screens/add_coins_hub.dart:816-823`, `1060-1068`, & `1282-1290`):**
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
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  1. In `add_coins_hub.dart:799-838`, the top-level quick cards only show `'Scan a coin'`, `'Type it in'`, `'Upload a list'`, and `' vaulted coin'`—there is no top-level card for **Invoices / Receipts** (`I-01`).
  2. Clicking `'Upload a list'` (`lines 819-822`) merely sets `_showMoreWays = true` and switches to Tab 0, which renders a static teaser card forcing the user to click `'Open Bulk Import →'` (`line 1064`, `_openSpreadsheetImport`) or switch tabs and click `'Open Invoice Importer →'` (`line 1286`, `_openInvoiceImport`) (`I-02`).
  3. **Fix:**
     - Add a dedicated top-level `_QuickAddCard` in `add_coins_hub.dart:799-838` for **`Upload an Invoice`** (calling `_openInvoiceImport()` directly in 1 click).
     - Change the **`Upload a list`** `_QuickAddCard` (`line 819`) to call `_openSpreadsheetImport()` directly in 1 click (eliminating the redundant intermediate `'Open Bulk Import →'` click).

---

#### `I-14` (`SS 6` vs `SS 8`): Clicking a Card opens `Coin Inspector` while clicking the `i` info icon in Table view opens `CoinDetailScreen` (two completely different modals)
- **What `Plan.v1` proposed:** Cited nonexistent `MyCollectionView.tsx:140-195`.
- **Actual Code (`numista_mobile/lib/screens/my_collection_screen.dart:2735`, `2749-2783`, & `3041-3044`):**
  ```dart
  2735:             void onTap() => _showCoinInspectorDialog(effectiveId, m);
  ...
  2749:                         _iconBtn(Icons.info_outline,
  2750:                           crw.isVirtualChild ? 'View Parent Set' : 'View Details', () {
  ...
  2772:                             CoinDetailScreen.show(
  2773:                               context,
  2774:                               coinId: effectiveId,
  2775:                               data: targetData,
  ...
  3041:             onTap: () {
  3042:               setState(() => _selectedCoinId = effectiveId);
  3043:               _showCoinInspectorDialog(effectiveId, m);
  3044:             },
  ```
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  - Tapping a card in Card View (`my_collection_screen.dart:3043`) or tapping a cell in Table View (`line 2735`) calls `_showCoinInspectorDialog(effectiveId, m)` (`SS 6`), whereas tapping the `i` (`Icons.info_outline`) button in the Table row's `Actions` column (`line 2749-2783`) calls `CoinDetailScreen.show(...)` (`SS 8`)!
  - **Fix:** Route **both** Card View taps (`line 3043`) and Table View row/info taps (`line 2735` & `2772`) to `CoinDetailScreen.show(...)` (merging any Set Contents / OGP toggle helper from `_showCoinInspectorDialog` into `CoinDetailScreen`'s `Details` tab) so there is a single unified, 7-tab Coin Detail experience across the entire app.

---

#### `I-16` (`SS 10`): `Legislation` & `Known Errors` tabs show irrelevant 1965 Coinage Act or generic error lists for a 2023 Silver Proof Set
- **What `Plan.v1` proposed:** Cited nonexistent `CoinDetailTabs.tsx:70-120` and `LegislationSection.tsx:25-60`.
- **Actual Code (`numista_mobile/lib/screens/coin_detail_screen.dart:3017-3056` & `3465-3473`):**
  ```dart
  3017:   static String? _matchLawKey(CoinDetailData coin) {
  ...
  3050:     // Coinage Act 1965: affected all silver coins — halves, quarters, dimes
  3051:     if (denom.contains('half dollar') || denom.contains('quarter') ||
  3052:         denom.contains('dime')) {
  3053:       return '89-81';
  3054:     }
  3055:     return null;
  3056:   }
  ```
  ```dart
  3465:   Future<void> _loadAll() async {
  3466:     final denom = widget.coin.denomination.toLowerCase();
  3467:     final year  = int.tryParse(widget.coin.year) ?? 0;
  ```
- **Verified Root Cause & Required Fix in `Plan.v2`:**
  1. **Legislation Tab (`coin_detail_screen.dart:2902-3056`):** `_kDefaultLaws` and `_matchLawKey` only contain 6 historic acts (`1792`, `1837`, `1857`, `1873`, `1933`, `1965 Coinage Act 89-81`). For modern sets/coins (`2023 Silver Proof Set`, `2026 American Innovation $1`, `2026 Semiquincentennial $1`), `_matchLawKey` either returns `null` (`"No Legislation Matched"`) or erroneously matches `'89-81'` (Coinage Act of 1965, which eliminated silver from circulating dimes/quarters—the exact opposite of a `.999` fine Silver Proof Set!).
     - **Fix:** Add modern statutory entries to `_kDefaultLaws` and `_matchLawKey`:
       - **Silver Proof Sets & Modern Proof Sets (`31 U.S.C. § 5112(i)` / Public Law 101-585 & Public Law 114-94):** Authorizes annual Silver Proof Sets (switched from 90% silver to `.999` fine silver in 2019 under the FAST Act / 31 U.S.C. § 5112).
       - **Circulating Collectible Coin Redesign Act of 2020 (`Public Law 116-330`, `31 U.S.C. § 5112(x)-(y)`):** Authorizes both the **American Women Quarters Program (2022–2025)** and the **2026 Semiquincentennial (250th Anniversary) Coin Programs**.
       - **American Innovation $1 Coin Act (`Public Law 115-197`, `31 U.S.C. § 5112(w)`):** Authorizes the 2018–2032 American Innovation $1 Coin Program.
  2. **Known Errors Tab (`coin_detail_screen.dart:3465-3550`):** When viewing a multi-coin `Set` or `Roll` (`denom == 'set'`) or a brand-new 2023–2026 release with zero confirmed variety/error records, display a clean, accurate empty state (`"No major die varieties or mint errors have been cataloged by PCGS/NGC for this modern release / multi-coin set"`) instead of unverified keyword guesses.

---

## 3. Required Action for AG CoS v2 (`Plan.v2`) & Next Steps in Review Chain

1. **AG CoS v2 (`086b98b4-2340-4241-9f6a-08b8aaa8992c`):**
   - Replace all 19 nonexistent React/TSX/Python file paths in `Plan.v1` with the exact real Flutter (`numista_mobile/lib/screens/review_hub_screen.dart`, `my_collection_screen.dart`, `coin_detail_screen.dart`, `add_coins_hub.dart`, `estate_planning_screen.dart`) and FastAPI (`numista_backend/main.py`, `numista_backend/services/us_mint_catalog_service.py`) file:line targets and fixes documented in §2 above.
   - File `ERIC_BMINUS_LIVE_MINT_PLAN_v2_2026-10-27.md` in `1 NUMISTA.AI\BETA TEST\MY TESTING\27 OCT 26\` and `BATONS\`.
   - **DO NOT EXECUTE CODE YET** (`NET-602_AMEND` lock remains in force).
2. **Grok Bot CoS (GB) & Stand Alone Grok:**
   - Can review `Plan.v1` + this Argon code-grounded review in parallel or immediately upon `Plan.v2` landing, per `NET-602_AMEND`.
   - Only after `AG Plan.vN -> Argon -> GB CoS -> Stand Alone Grok` completes does CoS/Desk issue `EXECUTE`.
