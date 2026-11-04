# GEMINI 3.8 (ARGON) REVIEW — NET-647 MINT FAIL-FIX PLAN R2.4 & CONTACT SHEET R2.4
**Reviewer:** Numista.Ai Argon (`31035602-8cdd-403f-8b72-7280605f5100`)  
**Date:** 2026-10-31 17:36 EDT  
**Target Plan:** [`FAILFIX_PLAN_NET-647_R2.4_20261031-1715.md`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.4_20261031-1715.md)  
**Target Contact Sheet:** [`NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.4.png`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.4.png) (`1280 x 1560` px)  
**Governing Directives:** [`COS_SCORE_NET-647_R2.3_88_REVISE_20261031-1655.md`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/COS_SCORE_NET-647_R2.3_88_REVISE_20261031-1655.md), `NET-665A`, `NET-665B`, `NET-665C`, [`WAKE_ARGON_NET-665_REVIEW_R2.4_20261031-1650.md`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/WAKES/WAKE_ARGON_NET-665_REVIEW_R2.4_20261031-1650.md)  
**Argon Score:** **84 / 100 — REVISE (`R2.5` Fix-Only Visual & Crop Re-Render Required Before CoS Can Score $\ge 95$)**  
**Execution Status:** **NO EXECUTE** (`origin/dev` frozen at `9b55f3d9`, `origin/main` frozen at `9f04550a`, zero source code modified).

---

## 1. Executive Verdict & Scope Verification

1. **Fix-Only & Pricing Contract Unchanged — PASS:**
   - Sections 2–6, 8 (pricing math), 9 (`POST /api/review/bulk_update`), and 10 (40-file `flutter test` gate and build identity `8.18.15+81818`) remain untouched from the approved R2.2/R2.3 baseline.
   - Python `Decimal` `ROUND_HALF_UP` (`$64.97 / 2 = $32.49`, `unit_cost_cents = 3249`), Dart string-based `formatCurrency(num amount)`, deletion of the `qty == 25` heuristic, and the dry-run CSV backfill (`backfill_review_mint_pricing.py` scoped strictly to `review_queue` `status == 'pending'`, never touching `coins/`) are preserved intact.
   - **Zero code was executed** (`git status` confirmed clean on source files; only plan/contact-sheet rendering ran in `numista_backend/scratch/create_contact_sheet_r24.py`).
2. **Eric's 7C Folder (`Images from US MInt`) Fixed 4 Key Obverses (`26SQRP`, `26XL`, `26EA`, `26XE`) — PASS:**
   - Main grid tiles `#1: 26SQRP` (`26SQRP_b.webp`), `#2: 26XL` (`26xl___a.webp`), `#4: 26EA` (`26ea_a.webp`), and `#5: 26XE` (`26xe_a.webp`) now display genuine 2026 single-coin obverses with Semiquincentennial `1776-2026` / `1776~2026` dates and `250` Liberty Bell privy marks (on `26XL`, `26EA`, `26XE`), resolving CoS MUST-FIX #2 (`26EA` reverse swap) and MUST-FIX #3 (`26XE` 2025 Morgan swap).
3. **Why R2.4 Must Be Revised (`84/100 — REVISE`):**
   - Direct visual inspection of [`NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.4.png`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.4.png) by eye caught **4 visual defects in the rendered contact sheet** and **1 plan text/code drift item**:
     1. **Tiles `#3: 26XM` & `#6: 26XH`** use `26XH_image_1.jpg` (a **box + velvet case + COA packaging composite**) instead of the clean single-coin obverse `26XH_image_3.jpg` (`1000x875` in the GCS bucket), violating `NET-665B` (`"no composites on cards"`) and displaying `"ENHANCED UNCIRCULATED COIN"` packaging text on the regular Uncirculated `26XM` card.
     2. **Tile `#7: 26XF`** uses `26XF_image_2.jpg` (an extreme side-rim macro detail crop of the `250` bell privy and cheek) instead of a full coin obverse, does not show the `1776~2026` date at all, and is omitted from the Section 2 Date Zoom Row.
     3. **Tile `#10: 26GC`** is labeled `Side: Obverse (Statue of Liberty)` in the card, §7.3 table, and Zoom Bay #7, but renders `26gc_a.webp` (the 4-coin reverse lens + outer box packaging composite), and Zoom Bay #7 crops the cardboard box flap (`* 2026 ERICAN INNOVATION...`).
     4. **Section 2 Date Zoom Row crops (`create_contact_sheet_r24.py`) missed the target dates/privies on 5 of the 7 bays:**
        - **Bay 1 (`26SQRP`):** Cuts off `"2026"` on the right (shows only `"7 6 ~"`).
        - **Bay 2 (`26XL`):** Cuts off the bottom half of `"1776-2026"` and misses the Liberty Bell privy.
        - **Bay 3 (`26EA`):** Crops Liberty's gown/feet above the sun rays, completely cutting off `"1776-2026"` at the bottom rim.
        - **Bay 5 (`26XH`):** Hits **blank white background and the corner of the COA card** (zero coin, zero date, zero privy).
        - **Bay 7 (`26GC`):** Crops the cardboard box text (`* 2026 ERICAN INNOVATION...`) under the label `"2026 Innovation Obverse"`.

Below we provide the exact file replacements and exact `(left, top, right, bottom)` pixel bounding boxes so AG CoS v4 can re-render `R2.5` cleanly in minutes.

---

## 2. Rule 6(a) Verbatim Code Citations Audited

Per `GEMINI.md` Rule 6(a), every `file:line` citation inspected for `Plan R2.4` is pasted verbatim below:

### 2.1 Contact Sheet Generator (`numista_backend/scratch/create_contact_sheet_r24.py:24-135, 255-260`)
```python
items = [
    {
        'sku': '26SQRP',
        'name': 'Trump $1 25-Coin Roll',
        'side': 'Obverse (Trump)',
        'year_status': 'Genuine 2026 Obverse (7C)',
        'local_rel': r'Semiquincentennial President Donald J. Trump 2026 $1 Coin Rolls & Bags\26SQRP_b.webp',
        'url': 'https://upload.wikimedia.org/wikipedia/commons/d/d7/Semiquincentennial_President_Donald_J._Trump_dollar_obverse%2C_uncirculated.jpg',
        'zoom_box': (280, 680, 560, 800), # zoom on 2026 date under bust
        'zoom_label': '2026 Strike (Eric 7C)',
        'is_obverse': True
    },
    {
        'sku': '26XL',
        'name': '2026 Peace Dollar Rev Proof',
        'side': 'Obverse (Peace Liberty)',
        'year_status': 'Genuine 2026 Obverse (7C)',
        'local_rel': r'Peace Silver Dollar 2026 Reverse Proof Coin\26xl___a.webp',
        'url': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XL_image_1.jpg',
        'zoom_box': (480, 800, 720, 940),
        'zoom_label': '1776~2026 Dual Date & Bell',
        'is_obverse': True
    },
    {
        'sku': '26XM',
        'name': '2026 Peace Dollar Uncirculated',
        'side': 'Obverse (Peace Liberty)',
        'year_status': 'Genuine 2026 Obverse (665B)',
        'local_rel': None,
        'url': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XH_image_1.jpg',
        'zoom_box': (420, 720, 620, 830),
        'zoom_label': '1776~2026 Dual Date & Privy',
        'is_obverse': True
    },
    {
        'sku': '26EA',
        'name': '2026 Silver Eagle Proof',
        'side': 'Obverse (Walking Liberty)',
        'year_status': 'Genuine 2026 Obverse (7C)',
        'local_rel': r'American Eagle 2026 One Ounce Silver Proof Coin\26ea_a.webp',
        'url': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26EA_image_3.jpg',
        'zoom_box': (520, 840, 680, 940),
        'zoom_label': '2026 Date Strike',
        'is_obverse': True
    },
    {
        'sku': '26XE',
        'name': '2026 Morgan Enhanced Unc',
        'side': 'Obverse (Morgan Liberty)',
        'year_status': 'Genuine 2026 Obverse (7C)',
        'local_rel': r'Morgan Silver Dollar 2026 Enhanced Uncirculated Coin\26xe_a.webp',
        'url': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XE_image_1.jpg',
        'zoom_box': (480, 840, 720, 980),
        'zoom_label': '2026 Date Strike',
        'is_obverse': True
    },
    {
        'sku': '26XH',
        'name': '2026 Peace Enhanced Unc',
        'side': 'Obverse (Peace Liberty)',
        'year_status': 'Genuine 2026 Obverse (665B)',
        'local_rel': None,
        'url': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XH_image_1.jpg',
        'zoom_box': (420, 720, 620, 830),
        'zoom_label': '1776~2026 Dual Date & Privy',
        'is_obverse': True
    },
    {
        'sku': '26XF',
        'name': '2026 Morgan Dollar Rev Proof',
        'side': 'Obverse (Morgan Liberty)',
        'year_status': 'Genuine 2026 Obverse (665B)',
        'local_rel': None,
        'url': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XF_image_2.jpg',
        'zoom_box': (420, 870, 660, 1020),
        'zoom_label': '2026 Date Strike',
        'is_obverse': True
    },
...
    {
        'sku': '26GC',
        'name': '2026 Innovation Rev Proof Set',
        'side': 'Obverse (Statue of Liberty)',
        'year_status': 'Genuine 2026 Obverse (7C)',
        'local_rel': r'American Innovation 2026 $1 Coin Reverse Proof Set\26gc_a.webp',
        'url': 'https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_american_innovation_iowa_reverse.jpg',
        'zoom_box': (300, 400, 700, 700),
        'zoom_label': '2026 Innovation Obverse',
        'is_obverse': True
    },
```
```python
# 7 zoom items across width
zoom_skus = ['26SQRP', '26XL', '26EA', '26XE', '26XH', '26RJ', '26GC']
zoom_w = (canvas_w - 60) // len(zoom_skus)
zoom_box_h = 130
```

### 2.2 US Mint Catalog Service (`numista_backend/services/us_mint_catalog_service.py:166-181`)
```python
    "26SQRP": {
        "title": "2026 Semiquincentennial Presidential $1 Coin 25-Coin Roll",
        "formal_name": "2026 Semiquincentennial President Donald J. Trump $1 Coin 25-Coin Roll (Philadelphia)",
        "year": 2026,
        "mint_mark": "",
        "mint_facility": "Philadelphia (P)",
        "denomination": "Dollar",
        "program_series": "Presidential $1 Coins",
        "theme_subject": "Donald J. Trump Semiquincentennial 250th Anniversary Roll (July 4th Privy eligible)",
        "strike_type": "Circulating",
        "condition": "Uncirculated",
        "metal_content": "Manganese-Brass (88.5% Cu, 6% Zn, 3.5% Mn, 2% Ni)",
        "issue_price": "$61.00",
        "retailer": "United States Mint",
        "catalog_url": "https://catalog.usmint.gov/",
    },
```

### 2.3 Review Queue Bulk Update Route (`numista_backend/main.py:3765-3781`)
```python
@app.post("/api/review/bulk_update")
async def bulk_update_reviews(request: BulkUpdateRequest, _user: dict = Depends(get_current_user)):
    """
    Applies shared metadata to multiple items in the review queue.
    """
    caller_email = (_user.get('email') or '').strip().lower()
    if not caller_email:
        caller_email = (_user.get('uid') or '').strip()
    if request.user_email and request.user_email.strip():
        if request.user_email.strip().lower() != caller_email:
            raise HTTPException(status_code=403, detail="Forbidden: email mismatch")

    allowed_keys = {"storage_location", "condition", "notes", "status"}
    for k in (request.updates or {}).keys():
        if k not in allowed_keys:
            raise HTTPException(status_code=400, detail=f"Invalid update field: {k}")
```

### 2.4 Review Hub Direct Firestore Update (`numista_mobile/lib/screens/review_hub_screen.dart:1054-1069`)
```dart
                                await FirebaseFirestore.instance
                                    .collection('users')
                                    .doc(user.email!)
                                    .collection('review_queue')
                                    .doc(docId)
                                    .update(updates);
                                if (!mounted) return;
                                nav.pop();
                                messenger.showSnackBar(
                                  const SnackBar(content: Text('Changes saved to Review Queue.')),
                                );
                              } catch (e) {
                                setDialogState(() => isSaving = false);
                                dialogMessenger.showSnackBar(
                                  SnackBar(content: Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'Save failed. Please try again.')), backgroundColor: Colors.red[700]),
                                );
                              }
```

### 2.5 Error Helper Default Return (`numista_mobile/lib/utils/numista_error_helper.dart:88-90`) & Build Version (`numista_mobile/pubspec.yaml:19`)
```dart
      default:
        return _unknown;
    }
```
```yaml
version: 8.18.15+81818
```

---

## 3. Point-by-Point Visual Audit of `NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.4.png`

### 3.1 Main 11-Tile Thumbnail Grid Inspection

| Tile | SKU | Source File Used in R2.4 | Eye-Inspection Result | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **#1** | `26SQRP` | `26SQRP_b.webp` (`1000x875`, Eric 7C) | Genuine single-coin 2026 Trump $1 Obverse showing `1776 ~ 2026` dual date below bust. | **PASS** |
| **#2** | `26XL` | `26xl___a.webp` (`1200x1050`, Eric 7C) | Genuine single-coin 2026 Peace Dollar Reverse Proof Obverse showing `1776-2026` and Liberty Bell `250` privy. | **PASS** |
| **#3** | `26XM` | `26XH_image_1.jpg` (`1000x875`, GCS) | **FAIL:** Renders outer box + open case + COA packaging composite (`"2026 Peace Dollar ENHANCED UNCIRCULATED COIN"` text visible on box/COA!) instead of a single coin obverse. | **MUST-FIX (AF-R2.4-1)** |
| **#4** | `26EA` | `26ea_a.webp` (`1200x1050`, Eric 7C) | Genuine single-coin 2026 Silver Eagle Proof Obverse (Walking Liberty, `1776-2026` at bottom rim, `250` Liberty Bell privy on right field). Fixes CoS MUST-FIX #2. | **PASS** |
| **#5** | `26XE` | `26xe_a.webp` (`1200x1050`, Eric 7C) | Genuine single-coin 2026 Morgan Enhanced Unc Obverse (`*1776~2026*` at bottom rim, `250` Liberty Bell privy behind cap). Fixes CoS MUST-FIX #3. | **PASS** |
| **#6** | `26XH` | `26XH_image_1.jpg` (`1000x875`, GCS) | **FAIL:** Renders outer box + open case + COA packaging composite instead of single-coin obverse `26XH_image_3.jpg`, violating `NET-665B` (`"no composites on cards"`). | **MUST-FIX (AF-R2.4-1)** |
| **#7** | `26XF` | `26XF_image_2.jpg` (`1000x875`, GCS) | **FAIL:** Renders an extreme side-rim macro crop of Liberty's cheek, `UM`, and the `250` bell privy — not a full coin obverse and does not show the `1776~2026` date. | **MUST-FIX (AF-R2.4-2)** |
| **#8** | `26RG` | `26rg_b.webp` (`1200x1050`, Eric 7C) | Genuine 2026 Semiquincentennial Proof Set 5-coin plastic blister lens (`1776-2026` quarters/half/dollar/cent/nickel). | **PASS** |
| **#9** | `26RJ` | `26rj_a.webp` (`1200x1050`, Eric 7C) | Genuine 2026 Uncirculated Coin Set folder & 20-coin blister cards (`2026 UNCIRCULATED COIN SET` banner). | **PASS** |
| **#10** | `26GC` | `26gc_a.webp` (`1200x1050`, Eric 7C) | **FAIL:** Labeled `Side: Obverse (Statue of Liberty)`, but renders `26gc_a.webp` (the 4-coin reverse lens + outer box composite). | **MUST-FIX (AF-R2.4-3)** |
| **#11** | `2026-AI-IA` | `2026_american_innovation_iowa_reverse.jpg` (GCS) | Genuine 2026 American Innovation Iowa Reverse (Norman Borlaug). | **PASS** |

---

### 3.2 Section 2 Date Zoom Row Eye-Inspection (`create_contact_sheet_r24.py:255-295`)

| Zoom Bay | SKU | R2.4 `zoom_box` | What Actually Rendered in `R2.4.png` | Verdict & Exact R2.5 `zoom_box` Fix |
| :--- | :--- | :--- | :--- | :--- |
| **Bay 1** | `26SQRP` | `(280, 680, 560, 800)` on `1000x875` | **FAIL:** Cropped too far left (`x=280..560`). Shows `"7 6 ~"` and completely cuts off `"2026"` (`x=500..730`)! | **MUST-FIX:** Use `zoom_box = (270, 700, 730, 845)` on `26SQRP_b.webp`. |
| **Bay 2** | `26XL` | `(480, 800, 720, 940)` on `1200x1050` | **FAIL:** Cropped too high (`y=800..940`). Slices right through the top half of `"1776-2026"` (`y=900..1015`) and misses the Liberty Bell privy (`x=310..440, y=620..760`). | **MUST-FIX:** Use `zoom_box = (370, 885, 830, 1025)` for the full `1776-2026` dual date (or `(300, 620, 830, 1025)` to include both Bell privy & date). |
| **Bay 3** | `26EA` | `(520, 840, 680, 940)` on `1200x1050` | **FAIL:** Cropped Liberty's gown/feet above the sun rays (`y=840..940`), **completely cutting off `"1776-2026"`** at the bottom rim (`y=915..1020`)! | **MUST-FIX:** Use `zoom_box = (370, 910, 830, 1025)` on `26ea_a.webp`. |
| **Bay 4** | `26XE` | `(480, 840, 720, 980)` on `1200x1050` | Shows `"76~2026"` at the bottom of the crop (`1` and `*` slightly clipped on left/right). | **TUNE:** Widen slightly to `zoom_box = (350, 850, 850, 1015)` on `26xe_a.webp` so the entire `*1776~2026*` legend is centered. |
| **Bay 5** | `26XH` | `(420, 720, 620, 830)` on `26XH_image_1.jpg` | **FAIL:** Hits **blank white background and the bottom-left corner of the COA booklet** — shows zero coin, zero date, and zero privy! | **MUST-FIX:** Switch source image to `26XH_image_3.jpg` (`1000x875`) and use `zoom_box = (315, 730, 685, 855)`. |
| **Bay 6** | `26RJ` | `(280, 40, 720, 200)` on `26rj_a.webp` | Shows `"2026 UNCIRCULATED COIN SET"` packaging banner (`"UNITED STATES MINT"` top line slightly clipped at right). | **PASS** (optional widen to `(260, 40, 760, 210)`). |
| **Bay 7** | `26GC` | `(300, 400, 700, 700)` on `26gc_a.webp` | **FAIL:** Labeled `"2026 Innovation Obverse"`, but crops the cardboard box flap (`"* 2026 ERICAN INNOVATION COIN REVERSE PROOF SET"`)! | **MUST-FIX:** See `AF-R2.4-3` below (`26gc_g.webp` / `26gc_h.webp` or relabel as Set Packaging). |

---

## 4. Detailed Actionable Fixes Required for `R2.5` (`AF-R2.4-1` through `AF-R2.4-5`)

### `AF-R2.4-1` (CRITICAL): Replace `26XH_image_1.jpg` (Box+Case+COA Composite) with `26XH_image_3.jpg` (Clean Single-Coin 2026 Peace Dollar Obverse) on `26XH` and `26XM`
- **Root Cause:** In `FAILFIX_PLAN_NET-647_R2.4_20261031-1715.md` (§7.3 rows 3 & 6) and `create_contact_sheet_r24.py` (`lines 53, 86`), both `26XM` and `26XH` use `26XH_image_1.jpg`, which is the outer box + open case + COA composite. Not only does `NET-665B` forbid composites on coin cards (`"no composites on cards"`), using `26XH_image_1.jpg` on `26XM` (`2026 Peace Dollar Uncirculated`) displays a box and COA printed with `"2026 Peace Dollar ENHANCED UNCIRCULATED COIN"`.
- **Exact Fix:** Use `https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26XH_image_3.jpg` (`1000x875`, already in the GCS bucket and local `scratch/mint_2026_official/26XH_image_3.jpg`), which is the clean, full-bleed single-coin **2026 Peace Dollar Enhanced Uncirculated Obverse** showing `LIBERTY`, `IN GOD WE TRVST`, the `250` Liberty Bell privy mark, and `1776~2026` at the bottom rim. Set `zoom_box = (315, 730, 685, 855)`.

### `AF-R2.4-2` (CRITICAL): Replace `26XF_image_2.jpg` (Side-Rim Macro Detail Crop) on Tile `#7: 26XF` with a Full-Coin 2026 Morgan Obverse and Include in Date Zoom
- **Root Cause:** `26XF_image_2.jpg` (`create_contact_sheet_r24.py:97`) is a macro close-up of the right rim (`UM` and the `250` Liberty Bell privy mark) — not a full coin obverse, and it does not contain the `1776~2026` date.
- **Exact Fix:** For `26XF` (`2026 Morgan Dollar Reverse Proof`), use a full-coin 2026 Morgan Obverse as the primary card thumbnail — either `26xe_a.webp` (`Morgan Silver Dollar 2026 Enhanced Uncirculated Coin\26xe_a.webp` from Eric's 7C folder, with the same finish-agnostic note used for `26XM`/`26XH` per CoS MUST-FIX #1, since both show George T. Morgan's 2026 `*1776~2026*` + `250` Liberty Bell obverse) or `gs://numista-reference-library/reference_library/2026_series/2026p_morgan_silver_dollar_reverse_proof_coin.png` (`255x255` transparent Reverse Proof obverse). Keep `26XF_image_2.jpg` as a secondary macro privy image if desired, and include all dated coin obverses in the Section 2 Zoom Row.

### `AF-R2.4-3` (HIGH): Resolve `26GC` (`#10`) Obverse vs. Set Packaging Mismatch Using `26gc_g.webp` / `26gc_h.webp`
- **Root Cause:** Tile `#10` (`26GC`), §7.3 row 10, and Zoom Bay #7 label `26GC` as `Side: Obverse (Statue of Liberty)` / `2026 Innovation Obverse`, while rendering `26gc_a.webp` (the 4-coin reverse lens + box composite) and cropping the cardboard box text.
- **Exact Fix:** Eric's folder `American Innovation 2026 $1 Coin Reverse Proof Set\` contains 8 files (`26gc_a.webp` through `26gc_h.webp`):
  - `26gc_g.webp` (`1200x1050`) is the **4-coin Reverse Proof Set lens showing all 4 Statue of Liberty Obverses** with `IN GOD WE TRUST`, `$1`, and the `250` Liberty Bell gear privy mark!
  - `26gc_h.webp` (`1200x1050`) is the **official US Mint macro close-up of the `250` Liberty Bell gear privy mark** on the 2026 American Innovation Obverse!
  - Use `26gc_g.webp` (or `26gc_b.webp` if showing the 4-coin reverse lens) for Tile `#10` (clean lens without outer box composite), and for Zoom Bay #7 either crop one Statue of Liberty obverse from `26gc_g.webp` (`zoom_box = (310, 240, 580, 510)`) or display `26gc_h.webp` (`250` Liberty Bell gear privy mark). Note in §7.3 that American Innovation $1 coins have edge-incused dates (`2026`), while the obverse carries the 2026-specific `250` Liberty Bell gear privy mark.

### `AF-R2.4-4` (CRITICAL): Fix Section 2 Date Zoom Row Bounding Boxes in `create_contact_sheet_r24.py`
- Update `zoom_box` coordinates in the contact sheet script so every single bay visibly frames its full date / privy mark without clipping:
  - `26SQRP` (`26SQRP_b.webp`, `1000x875`): `(270, 700, 730, 845)` — frames the complete `"1776 ~ 2026"` dual date.
  - `26XL` (`26xl___a.webp`, `1200x1050`): `(370, 885, 830, 1025)` — frames the complete `"1776-2026"` dual date at the bottom rim.
  - `26EA` (`26ea_a.webp`, `1200x1050`): `(370, 910, 830, 1025)` — frames the complete `"1776-2026"` dual date at the bottom rim.
  - `26XE` (`26xe_a.webp`, `1200x1050`): `(350, 850, 850, 1015)` — frames the complete `"*1776~2026*"` dual date at the bottom rim.
  - `26XH` (`26XH_image_3.jpg`, `1000x875`): `(315, 730, 685, 855)` — frames the complete `"1776~2026"` dual date at the bottom rim.
  - `26RJ` (`26rj_a.webp`, `1200x1050`): `(260, 40, 760, 210)` — frames the `"2026 UNCIRCULATED COIN SET"` header banner.
  - `26GC` (`26gc_g.webp`, `1200x1050`): `(310, 240, 580, 510)` — frames the top-left Statue of Liberty Obverse (`IN GOD WE TRUST`, `$1`, and `250` Liberty Bell gear privy).

### `AF-R2.4-5` (MODERATE): Align Plan Text (§7.1, §7.2) and §8 Code Snippet with §7.3 Table
- In [`FAILFIX_PLAN_NET-647_R2.4_20261031-1715.md`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.4_20261031-1715.md) lines `225, 229, 245, 247, 248`, update the prose descriptions of `26SQRP`, `26EA`, and `26XE` from `"2026" date strike` to their actual Semiquincentennial dual dates (`"1776 ~ 2026"` / `"1776-2026"`) and `250` Liberty Bell privy marks (on `26EA` and `26XE`).
- In §8 (`line 308`), update `"26SQRP"` `"image_url_obverse"` from the legacy Wikimedia URL to `"https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26SQRP_b.webp"` so §8 matches §7.3 row 1.

---

## 5. Summary Scorecard

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Fix-Only Discipline & Pricing/Rounding Preservation** | 30 | **30 / 30** | Sections 2–6, 8 (pricing), 9 (`bulk_update_reviews`), and 10 (40-file test gate & `8.18.15+81818`) untouched. Zero code executed. |
| **2. Eric 7C Integration & Single-Coin 2026 Obverses** | 35 | **26 / 35** | `26SQRP`, `26XL`, `26EA`, `26XE` fixed cleanly; `-9` for `26XH`/`26XM` box composite (`26XH_image_1.jpg`), `26XF` side-rim macro (`26XF_image_2.jpg`), and `26GC` box composite (`26gc_a.webp`). |
| **3. Contact Sheet Date Zoom Row Accuracy** | 25 | **19 / 25** | Section 2 Date Zoom Row added, but 5 of 7 `zoom_box` crops missed/clipped the dates (`26SQRP`, `26XL`, `26EA`, `26XH` white space, `26GC` box flap). |
| **4. Plan Internal Consistency & Canonical Paths** | 10 | **9 / 10** | Canonical `8 OCT 26/RADIO NET/` path and provenance fixed; `-1` for §8 `26SQRP` URL and §7.1/7.2 dual-date prose drift. |
| **TOTAL** | **100** | **84 / 100** | **REVISE (`R2.5`) — Re-render contact sheet & update §7/§8 table/text using exact coordinates above.** |
