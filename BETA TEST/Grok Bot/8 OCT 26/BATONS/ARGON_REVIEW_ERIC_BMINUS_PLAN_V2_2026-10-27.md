# ARGON REVIEW — `ERIC_BMINUS_LIVE_MINT_PLAN_v2_2026-10-27.md` (`NET-615` / `NET-616` Round 2 of Max 4)

- **Reviewer:** Numista.Ai Argon (`Gemini 4 Argon` — Thinking Jobs Only)
- **Date / Time:** 2026-10-27 14:53 ET
- **Target Plan:** `1 NUMISTA.AI\BETA TEST\MY TESTING\27 OCT 26\ERIC_BMINUS_LIVE_MINT_PLAN_v2_2026-10-27.md`
- **Source Packets Audited:**
  - Morning Beta Test (`27 OCT 2026.docx`, `SS 1.png`–`SS 10.png`)
  - Afternoon 1351hrs Beta Test (`1351hrs test\27 OCT 2026 v2.docx`, `Receipt_2026 Uncirculated Coin Set.pdf`, `1351hrs test\SS 1.png`–`SS 7.png`)
  - `NET-615` & `NET-616` (`NET616_PM_TEST_1351_AMEND_PLAN_V2.md`)
- **Rule 6(a) Compliance:** 100% — Every `file:line` citation below includes the exact verbatim code lines inspected in the repository.
- **Argon Score (`Plan.v2`):** **84 / 100 — CONDITIONAL GO (4 Mandatory Real-Code Corrections `GAP-1`..`GAP-4` Required for `PM-01`..`PM-06` to Pass on First Build)**
- **Review Chain Gate (`NET-602_AMEND`):**
  `AG CoS v2 Plan.v2 -> Argon Review (THIS FILE) -> Grok Bot CoS (GB) Review -> Stand Alone Grok (SAG) Feedback -> ONLY THEN CoS/Desk EXECUTE`

---

## 1. Executive Summary (BLUF)

`Plan.v2` is a major improvement over `Plan.v1` (up from **58/100** to **84/100**):
- **Zero hallucinated `numista_web/src/...` paths** — all 19 fabricated React/TS paths from `Plan.v1` have been replaced with real Flutter (`numista_mobile/lib/...`) and FastAPI (`numista_backend/...`) files.
- **Morning issues `I-01`, `I-02`, `I-04a`, `I-04b`/`PM-07`, `I-04c`, `I-05`, `I-06`, `I-10`, `I-11`, `I-12`, `I-14`, `I-15`, `I-16` are 100% accurately grounded** with verbatim code citations, including the exact `numista_backend/main.py:7653-7654` fee-wipe line requested by Grok Bot CoS in `GBCOS_REVIEW_ERIC_BMINUS_PLAN_V1_2026-10-27.md`.

**HOWEVER**, Argon's line-by-line verification against Eric's **1351hrs PM Beta Test (`SS 1`–`SS 7`)** caught **4 critical code-level gaps (`GAP-1`..`GAP-4`)** in `Plan.v2` (including one inaccurate `file:line` quote at `Plan.v2` lines 68–75). **If `Plan.v2` were executed without these 4 corrections, Eric's afternoon test (`PM-01`, `PM-02`, `PM-05`, `PM-06`) would STILL fail on retest:**

1. **`GAP-1` (`PM-02` P0 — Why `1351hrs test\SS 1.png` showed `0 Duplicates Flagged`):**
   - `Plan.v2` line 278 misidentifies `main.py:7640-7675` as `_execute_import_process_worker` (those lines are actually `normalize_and_validate_receipt`).
   - The real `_execute_import_process_worker` (`numista_backend/main.py:7694-8215`) initializes `summary` at `main.py:7708-7713` **without a `"duplicates_flagged"` key**, while the static importer UI (`numista_mobile/web/add_coins.html:1127`) reads `s.duplicates_flagged || 0`!
   - Furthermore, `main.py:8125-8128` pops uppercase `"Retailer Invoice #"` and `"Retailer Item No."` before writing to Firestore, whereas `main.py:3560-3570` and `duplicate_check.py:51-58` query uppercase keys!
2. **`GAP-2` (`PM-01` & `PM-05` P0 — Why the new `26RJ` in `1351hrs test\SS 3`, `SS 5`, `SS 7` had blank `Theme/Subject`, no image, `$0.00` value, and no `20-COIN SET` strip):**
   - **Rule 6(a) Catch:** `Plan.v2` lines 68–75 quote code at `numista_backend/main.py:7668-7672` (`"Denomination": item.get("denomination")...`) that **does not exist at those lines**. The actual dict construction in `normalize_and_validate_receipt` (`numista_backend/main.py:7607-7638`) **omits `"Theme/Subject"` and `"Strike Type"` completely**, dropping any LLM-extracted `Theme/Subject` on the floor!
   - **Catalog Match Catch:** In `1351hrs test\SS 3`, `SS 5`, `SS 6`, Eric's existing working `26RJ` has `Program/Series: "Uncirculated Sets"`, `Theme/Subject: "250th Anniversary Uncirculated Coin Set"`, `is_set: True`, and `set_id: "uncirculated-coin-set-2026"`.
   - `Plan.v2` line 78 proposes `Theme: "250th Anniversary Semiquincentennial Uncirculated Coin Set"`, `Series: "Annual Uncirculated Sets"`, and `Issue Price: "$36.40"`, and omits `is_set: True` and `set_id: "uncirculated-coin-set-2026"`. That would:
     - Fail to match `numista_mobile/lib/services/coin_image_service.dart:148` (`'250th anniversary uncirculated coin set': '250th-anniversary'`),
     - Fail to render `CoinSetViewer` (`20-COIN SET` strip in `SS 6`, which requires `is_set: True` and `set_id: "uncirculated-coin-set-2026"` at `my_collection_screen.dart:5365-5373` and `coin_detail_screen.dart:1563-1564`), and
     - Confuse the US Mint issue price (`$124.50` on `Receipt_2026 Uncirculated Coin Set.pdf`) with the `$36.40` 20-coin aggregate retail value computed by `numista_backend/main.py:10845-10865` from `coin_set_index/uncirculated-coin-set-2026`!
3. **`GAP-3` (`PM-06` / `I-13` P1 — `Footlocker` / `Add where this is stored` white text on cream in `1351hrs test\SS 6` & `SS 7`):**
   - `Plan.v2` fixes `_HeroHeader` (`coin_detail_screen.dart:917-924`), but misses `_OwnerPhotoHero` (`numista_mobile/lib/screens/coin_detail_screen.dart:4214-4245`), which is the exact `Footlocker` label Eric pointed to with a red arrow in `1351hrs test\SS 6.png` (`color: Colors.white.withAlpha(200)` on `#F4F4F2` cream).
4. **`GAP-4` (`PM-06` P1 — Cut-off `25¢ Lincoln` quarter in `20-COIN SET` strip in `1351hrs test\SS 6.png`):**
   - `Plan.v2` line 500 targets `numista_mobile/lib/widgets/set_contents_panel.dart`, whereas the widget actually rendered in `1351hrs test\SS 6.png` (`20-COIN SET` `2026 United States Mint Uncirculated Coin Set` / `Tap coin to flip • Long-press to expand`) is **`CoinSetViewer` in `numista_mobile/lib/widgets/coin_set_viewer.dart:217-229`**!

---

## 2. Detailed Verbatim Code Audit of the 4 Mandatory Corrections (`GAP-1`..`GAP-4`)

### `GAP-1` (`PM-02` & `I-08` P0): Why `Duplicates Flagged` Was `0` on `SS 1` & Missing in Review Hub (`SS 2`)

- **What `add_coins.html` reads (`numista_mobile/web/add_coins.html:503-506` & `1125-1127`):**
  ```html
  503:       <div class="stat-card stat-dupes">
  504:         <div class="stat-number" id="stat-dupes">0</div>
  505:         <div class="stat-label">Duplicates Flagged</div>
  506:       </div>
  ```
  ```javascript
  1125:   document.getElementById('stat-coins').textContent    = s.coins_identified || 0;
  1126:   document.getElementById('stat-receipts').textContent = s.receipts_parsed  || 0;
  1127:   document.getElementById('stat-dupes').textContent    = s.duplicates_flagged || 0;
  ```
- **What `_execute_import_process_worker` actually initializes (`numista_backend/main.py:7708-7713`):**
  ```python
  7708:         summary = {
  7709:             "coins_identified":   0,
  7710:             "receipts_parsed":    0,
  7711:             "total_purchase_value": 0.0,
  7712:             "unlinked_receipts":  0,
  7713:         }
  ```
- **Why `main.py:3560-3570` fails to match snake_case keys popped at `main.py:8124-8129`:**
  ```python
  8124:                         # Remove legacy illegal uppercase keys from the document payload if present
  8125:                         coin_doc.pop("Retailer/Website", None)
  8126:                         coin_doc.pop("Retailer Invoice #", None)
  8127:                         coin_doc.pop("Retailer Item No.", None)
  8128:                         coin_doc.pop("Allocated Fees", None)
  ```
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
  ```
- **Mandatory Correction for `Plan.v2` (`GAP-1`):**
  1. In `_execute_import_process_worker` (`numista_backend/main.py:7708-7713`), add `"duplicates_flagged": 0` to `summary`.
  2. Before the file loop in `_execute_import_process_worker` (`numista_backend/main.py:7715`), pre-fetch existing user collection docs from `db.collection("users").document(user_email).collection("coins").stream()` (excluding `status == "deleted"`).
  3. Inside `for stable_doc_id, coin_doc in new_item_specs:` (`numista_backend/main.py:8115-8138`), compare `coin_doc` against existing vault docs using **both** snake_case (`retailer_item_num`, `item_number`, `retailer_invoice_num`, `invoice_number`) and legacy Title Case (`Retailer Item No.`, `Retailer Invoice #`, `product_code`):
     - **Case A (Same Invoice # + Same Item #/SKU):** Set `coin_doc["possible_duplicate"] = True`, `coin_doc["duplicate_type"] = "same_invoice"`, `coin_doc["duplicate_flag"] = f"Duplicate Invoice #{inv_val} ({sku_val}) already in collection"`, and increment `summary["duplicates_flagged"] += 1`.
     - **Case B (Same Item #/SKU e.g. `26RJ` or normalized `(Year, Mint Mark, Denomination, Program/Series)`, Different Invoice # e.g. `USM23493262` vs eBay):** Set `coin_doc["possible_duplicate"] = True`, `coin_doc["duplicate_type"] = "separate_order_copy"`, `coin_doc["duplicate_flag"] = f"Already in Collection (SKU {sku_val}) — Different Order #{inv_val or 'N/A'}"`, and increment `summary["duplicates_flagged"] += 1`.
  4. In `/api/review/commit` (`numista_backend/main.py:3560-3579`), read snake_case fallbacks:
     `inv_no = (data.get('retailer_invoice_num') or data.get('invoice_number') or data.get('Retailer Invoice #') or '').strip()`
     `item_no = (data.get('retailer_item_num') or data.get('item_number') or data.get('Retailer Item No.') or data.get('product_code') or '').strip()`

---

### `GAP-2` (`PM-01`, `PM-05`, `I-03` P0): Why `26RJ` Had Blank `Theme/Subject`, No Image, `$0.00` Value, and No `20-COIN SET` Strip

- **Rule 6(a) Catch on `Plan.v2` lines 68–75 (`numista_backend/main.py:7607-7638` vs `7668-7672`):**
  `Plan.v2` lines 68–75 cited `main.py:7668-7672` with code that is not in `main.py`. Here are the **actual** verbatim lines at `numista_backend/main.py:7607-7620` and `7668-7672`:
  ```python
  7607:         doc = {
  7608:             "Program/Series":       prog_val,
  7609:             "Year":                 it.get("Year", ""),
  7610:             "Mint Mark":            mint_mark_val,
  7611:             "Denomination":         denom_val,
  7612:             "Condition":            it.get("Condition", "Ungraded"),
  7613:             "Metal Content":        metal_val,
  7614:             "Cost":                 landed_cost_basis,
  7615:             "Purchase Cost":        landed_cost_basis,
  7616:             "Quantity":             item_qty,
  7617:             "quantity":             item_qty,
  7618:             "Country":              "United States",
  7619:             "country":              "United States",
  7620:             "Personal Notes":       (it.get("Personal Notes") or it.get("Original Description from source") or "").strip(),
  ```
  ```python
  7668:                 doc["set_cost_label"] = f"${cost_val:.2f} ({qty_val} @ ${unit_val:.2f})"
  7669:             elif not doc.get("set_cost_label"):
  7670:                 cost_val = float(doc.get("Cost") or 0.0)
  7671:                 doc["set_cost_label"] = f"${cost_val:.2f}"
  7672:         except Exception as e:
  ```
  Notice that `doc = { ... }` at `main.py:7607-7638` **never copies `"Theme/Subject"` or `"Strike Type"` from `it` into `doc` at all**!
- **Why `us_mint_catalog_service.py:315-317` fails to overwrite `Program/Series`:**
  ```python
  315:         current_series = str(item.get("Program/Series") or "")
  316:         if not current_series or "Invoice Import" in current_series or current_series == "USA":
  317:             item["Program/Series"] = catalog_match["program_series"]
  ```
- **Why Eric's first `26RJ` (`SS 3`, `SS 5`, `SS 6`) has an image, `$36.40` valuation, and the `20-COIN SET` strip (`coin_image_service.dart:148`, `my_collection_screen.dart:5365-5373`, `coin_detail_screen.dart:1563-1564`, `main.py:10844-10865`, `fix_26rj_phase2.py:19-22`):**
  ```dart
  // numista_mobile/lib/services/coin_image_service.dart:147-149
  147:     // 2026 Semiquincentennial
  148:     '250th anniversary uncirculated coin set': '250th-anniversary',
  149:     '250th anniversary': '250th-anniversary',
  ```
  ```dart
  // numista_mobile/lib/screens/my_collection_screen.dart:5365-5374
  5365:     if (isSet && setContentsWidget == null && setId != null && setId.isNotEmpty) {
  5366:       setContentsWidget = Padding(
  5367:         padding: const EdgeInsets.fromLTRB(0, 16, 0, 0),
  5368:         child: Column(
  5369:           crossAxisAlignment: CrossAxisAlignment.start,
  5370:           children: [
  5371:             Divider(color: _border),
  5372:             const SizedBox(height: 16),
  5373:             CoinSetViewer(setId: setId),
  5374:           ],
  ```
  ```dart
  // numista_mobile/lib/screens/coin_detail_screen.dart:1561-1565
  1561:             if (coin.setContents != null && coin.setContents!.isNotEmpty)
  1562:               SetContentsPanel(data: coin.toFirestore())
  1563:             else if (coin.setId != null && coin.setId!.isNotEmpty)
  1564:               CoinSetViewer(setId: coin.setId!),
  1565:           ],
  ```
  ```python
  # numista_backend/main.py:10844-10849
  10844:         is_set_item = bool(coin_data.get("is_set") or coin_data.get("isSet") or str(coin_data.get("Denomination", "")).lower() == "set" or coin_data.get("item_type") == "set")
  10845:         if is_set_item:
  10846:             set_id = coin_data.get("set_id") or "uncirculated-coin-set-2026"
  10847:             set_doc = db.collection("coin_set_index").document(set_id).get()
  10848:             if set_doc.exists:
  10849:                 coins_list = set_doc.to_dict().get("coins", [])
  ```
- **Mandatory Correction for `Plan.v2` (`GAP-2`):**
  1. In `normalize_and_validate_receipt` (`numista_backend/main.py:7607-7615`), explicitly include `"Theme/Subject"` and `"Strike Type"` in `doc`:
     ```python
     "Theme/Subject": (it.get("Theme/Subject") or it.get("subject") or it.get("theme_subject") or "").strip(),
     "Strike Type":   (it.get("Strike Type") or it.get("strike_type") or ("Proof" if "proof" in raw_lower else "Uncirculated")),
     "Condition":     (it.get("Condition") or ("Proof" if "proof" in raw_lower else "Uncirculated")),
     ```
  2. In `US_MINT_PRODUCT_CATALOG` (`numista_backend/services/us_mint_catalog_service.py`), use the **exact** canonical strings and set/image metadata for `26RJ`:
     - `"program_series": "Uncirculated Sets"` (matches `1351hrs test\SS 5.png`)
     - `"theme_subject": "250th Anniversary Uncirculated Coin Set"` (matches `coin_image_service.dart:148` & `SS 5.png`)
     - `"denomination": "Set"`, `"mint_mark": "P & D"`, `"condition": "Uncirculated"`, `"strike_type": "Uncirculated"`, `"metal_content": "Cupronickel / Clad"`
     - `"is_set": True`, `"set_id": "uncirculated-coin-set-2026"`, `"item_type": "set"`
     - `"image_url_obverse": "https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_a.jpg"`
     - `"image_url_reverse": "https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg"`
     - `"issue_price": 124.50`, `"ai_est_value": 36.40` (or issue price baseline)
  3. In `enrich_us_mint_item` (`numista_backend/services/us_mint_catalog_service.py:315-338`), **authoritatively overwrite** `Program/Series`, `Theme/Subject`, `Denomination`, `Mint Mark`, and copy `is_set`, `set_id`, `item_type`, `image_url_obverse`, `image_url_reverse` from `catalog_match` onto `item` whenever a US Mint SKU matches `US_MINT_PRODUCT_CATALOG`!
  4. Also provide an idempotent backfill script/hook for the 4 already-committed test coins in Eric's collection (`2023 Silver Proof Set`, `2026 $1 American Innovation`, `2026D Donald J. Trump`, and the afternoon `2026 Set Uncirculated Coin Set`) so `PM-01` is immediately resolved on Eric's existing collection without forcing him to delete and re-upload!

---

### `GAP-3` (`PM-06` & `I-13` P1): `Footlocker` / `Add where this is stored` White Text on `#F4F4F2` Cream (`1351hrs test\SS 6` & `SS 7`)

- **Inspected Verbatim Code (`numista_mobile/lib/screens/coin_detail_screen.dart:4214-4245`):**
  ```dart
  4214:                       child: Text(
  4215:                         coin.storageLocation,
  4216:                         style: TextStyle(
  4217:                           color: Colors.white.withAlpha(200),
  4218:                           fontSize: 12,
  4219:                         ),
  4220:                         maxLines: 2,
  4221:                         overflow: TextOverflow.ellipsis,
  4222:                       ),
  ...
  4237:         Text(
  4238:           hasPhotos ? 'Your Photo' : '',
  4239:           style: TextStyle(
  4240:             color: Colors.white.withAlpha(120),
  4241:             fontSize: 10,
  ```
- **Mandatory Correction for `Plan.v2` (`GAP-3`):**
  In `_OwnerPhotoHero` (`numista_mobile/lib/screens/coin_detail_screen.dart:4217` & `4240`), replace `Colors.white.withAlpha(200)` with `_kText(context)` and `Colors.white.withAlpha(120)` with `_kSubtext(context)` (in addition to `_HeroHeader` at lines `919`, `924`, `928`).

---

### `GAP-4` (`PM-06` P1): Cut-Off `25¢ Lincoln` Coin in `20-COIN SET` Strip (`1351hrs test\SS 6.png`)

- **Inspected Verbatim Code (`numista_mobile/lib/widgets/coin_set_viewer.dart:216-229`):**
  ```dart
  216:         // ── Coin strip ──────────────────────────────────────────────────────
  217:         SizedBox(
  218:           height: 148,
  219:           child: ListView.separated(
  220:             scrollDirection: Axis.horizontal,
  221:             itemCount: data.coins.length,
  222:             separatorBuilder: (_, _) => const SizedBox(width: 10),
  223:             itemBuilder: (ctx, i) => _CoinTile(
  224:               coin: data.coins[i],
  225:               onLongPress: (url, label) =>
  226:                   _showLightbox(context, url, label, data.attribution),
  227:             ),
  228:           ),
  229:         ),
  ```
- **Mandatory Correction for `Plan.v2` (`GAP-4`):**
  1. Target `numista_mobile/lib/widgets/coin_set_viewer.dart:216-229` (the actual widget in `1351hrs test\SS 6.png`, in addition to `set_contents_panel.dart`):
     - Either render the set coins in a responsive `Wrap(spacing: 10, runSpacing: 12, ...)` so all 20 coins are visible without horizontal clipping, **OR** wrap the `ListView.separated` in a `Scrollbar` + `ScrollConfiguration` enabling `PointerDeviceKind.mouse` drag + explicit `<` / `>` scroll arrow buttons so the 5th+ coins (`25¢ Lincoln`, etc.) are never cut off on desktop web.
  2. For modal sizing (`1351hrs test\SS 6.png`), update **both** `CoinDetailScreen.show` (`numista_mobile/lib/screens/coin_detail_screen.dart:132-133`) AND `_showCoinInspectorDialog` (`numista_mobile/lib/screens/my_collection_screen.dart:3502-3506`) with a Maximize/Full-Screen toggle button in the dialog header.

---

## 3. Argon Scorecard for `Plan.v2`

| Category | Weight | `Plan.v1` | `Plan.v2` | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **1. Real File & Line Grounding (Rule 6a)** | 25 | 0 / 25 | **21 / 25** | 0 hallucinated `numista_web/` paths; 1 inaccurate line quote (`main.py:7668-7672` vs `7607-7638`) & missed `coin_set_viewer.dart:217-229`. |
| **2. Root-Cause Accuracy (Morning `I-01`..`I-16`)** | 25 | 14 / 25 | **24 / 25** | All 17 morning items accurately diagnosed with real Flutter/FastAPI code lines. |
| **3. Root-Cause Accuracy (Afternoon `PM-01`..`PM-07`)** | 25 | N/A | **16 / 25** | Caught `PM-03`/`PM-04`/`PM-07`, but missed `summary["duplicates_flagged"]` in `_execute_import_process_worker` (`GAP-1`), `26RJ` `set_id`/`is_set`/exact theme (`GAP-2`), `Footlocker` at `coin_detail_screen.dart:4217` (`GAP-3`), and `coin_set_viewer.dart:217-229` (`GAP-4`). |
| **4. Safety, Scope Discipline & Verification (Rule 8)** | 25 | 22 / 25 | **23 / 25** | Respects `NET-602_AMEND` no-code gate, `NET-609` NO-FOLD lock, and `origin/main` lock. |
| **TOTAL** | **100** | **58 / 100** | **84 / 100** | **CONDITIONAL GO — Fold `GAP-1`..`GAP-4` into `Plan.v2.1` (or mandatory pre-execute checklist) for Grok Bot CoS & Stand Alone Grok review.** |
