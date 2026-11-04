# GEMINI 3.8 (ARGON) REVIEW — NET-647 MINT FAIL-FIX PLAN R2.5 & CONTACT SHEET R2.5
**Reviewer:** Numista.Ai Argon (`31035602-8cdd-403f-8b72-7280605f5100`)  
**Date:** 2026-10-31 18:12 EDT  
**Target Plan:** [`FAILFIX_PLAN_NET-647_R2.5_20261031-1800.md`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.5_20261031-1800.md)  
**Target Contact Sheet:** [`NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.5.png`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.5.png) (`1280 x 1520` px) & `scratch/crops_r25/*.png`  
**Governing Directives:** [`WAKE_ARGON_NET-668_REVIEW_R2.5_20261031-1750.md`](file:///C:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/WAKE_ARGON_NET-668_REVIEW_R2.5_20261031-1750.md), [`WAKE_AG-COS-V4_NET-668_FIX-ONLY_R2.5_20261031-1750.md`](file:///C:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/WAKE_AG-COS-V4_NET-668_FIX-ONLY_R2.5_20261031-1750.md), `NET-668`, `NET-665D`  
**Argon Score:** **93 / 100 — WRITTEN PLAN & ALL 11 MAIN CARD THUMBNAILS 100% PASS (`100/100`); `-7` FOR 3 ZOOM BAYS (`26SQRP`, `26XL`, `26XH`) ON CONTACT SHEET PNG CLIPPING OUTER `'1'` & `'6'`/`'26'` DIGITS OF `'1776~2026'`**  
**Execution Status:** **NO EXECUTE** (`origin/dev` frozen at `9b55f3d9`, `origin/main` frozen at `9f04550a`, zero source code modified).

---

## 1. Executive Audit Against `WAKE_AG-COS-V4_NET-668` Must-Fixes `(a)–(f)`

| Item | Requirement (`WAKE_AG-COS-V4_NET-668`) | Audit of `R2.5` Plan & Contact Sheet PNG | Verdict |
| :--- | :--- | :--- | :---: |
| **Fix-Only & Pricing Frozen** | Confirm fix-only, pricing frozen (`ROUND_HALF_UP` `$32.49` / `3249` cents), and no code executed. | Sections 2–6, 8 (pricing math), 9 (`POST /api/review/bulk_update`), and 10 (40-file `flutter test` gate & `8.18.15+81818` stamp) are 100% untouched. Zero source code modified. | **PASS** |
| **`(a)` `26XM` & `26XH`** | Replace box/case/COA composite with clean obverse `26XH_image_3.jpg` (or equivalent dated obverse). | Both tiles `#3: 26XM` and `#6: 26XH` in `NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.5.png` and §7.3 (`lines 270, 273`) now use `26XH_image_3.jpg` (`1000x875` clean single-coin 2026 Peace Dollar Obverse with `1776~2026` and `250` Liberty Bell privy). Box/case/COA composite completely eliminated. | **PASS** |
| **`(b)` `26XF`** | Replace rim-macro crop with an obverse that shows the date. | Tile `#7: 26XF` and §7.3 (`line 274`) now use the full-coin 2026 Morgan Obverse (`26xe_a.webp` with finish-agnostic note per CoS MUST-FIX #1), showing `*1776~2026*` and `250` Liberty Bell privy, and Bay 6 in Section 2 displays the unclipped `*1776~2026*` zoom. | **PASS** |
| **`(c)` `26GC`** | Use `26gc_b` (CoS decision — shows the 4 unique 2026 designs: Iowa Borlaug, mobile refrigeration, Cray-1 Wisconsin, Jobs California; `26gc_g`, `26gc_h`, and `26gc_a` barred). | Tile `#10: 26GC` and §7.3 (`line 277`) now render `26gc_b.webp` (`1200x1050` clean 4-coin reverse lens showing Iowa Borlaug, Minnesota Mobile Refrigeration, Wisconsin Cray-1, and California Steve Jobs), labeled `Side: 4-Coin Reverse Lens (Iowa, Refrig, Cray-1, Jobs)`. | **PASS** |
| **`(d)` Date Zooms** | Redo so every bay shows the full date, unclipped. | **4 of 7 bays (`Bay 3: 26EA`, `Bay 4: 26XE`, `Bay 6: 26XF`, `Bay 7: 26RJ`) are 100% unclipped (`PASS`).** However, eye-inspection of `scratch/crops_r25/26SQRP.png`, `26XL.png`, and `26XH.png` shows **3 bays still clip the outer `"1"` on the left and `"6"` / `"2 6"` of `"2026"` on the right** because the date curves wider up the coin rim: `26SQRP` shows `"7 6 ~ 2 0"`, `26XL` shows `"7 7 6 ~ 2 0 2"`, and `26XH` shows `"7 7 6 ~ 2 0 2"`. See §3 below for visually verified wider crop coordinates. | **PARTIAL (`4/7` Unclipped; `3/7` Need Wider Rim-Arc Crop)** |
| **`(e)` Drifted Plan Text** | Fix A7 date wording; A8 `26SQRP` entry must point to Eric's folder or bucket file — not the old Wikimedia URL. | §7.1 (`lines 204–241`), §7.2 (`lines 254–260`), and §7.3 (`lines 268–278`) align the Semiquincentennial dual-date wording (`1776 ~ 2026`, `1776-2026`, `*1776~2026*`), and §8 (`line 317`) updates `26SQRP` `"image_url_obverse"` to `"https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp"`. | **PASS** |
| **`(f)` Naming** | Mint code lowercase in target names (e.g. `_26ea`), per `test_series_manifest_sync`. | All target GCS paths in §7.3 (`lines 268–278`), §8 (`line 317`), and §10 (`line 340`) use strictly lowercase mint codes (`26sqrp_b.webp`, `26xl___a.webp`, `26xh_image_3.jpg`, `26ea_a.webp`, `26xe_a.webp`, `26rg_b.webp`, `26rj_a.webp`, `26gc_b.webp`). | **PASS** |

---

## 2. Rule 6(a) Verbatim Code & Plan Citations Audited

Per `GEMINI.md` Rule 6(a), every `file:line` citation inspected for `Plan R2.5` is pasted verbatim below:

### 2.1 Plan R2.5 Date Zoom & Lowercase Target Table (`FAILFIX_PLAN_NET-647_R2.5_20261031-1800.md:226-241, 266-278, 302-320`)
```markdown
5. **Unclipped Date Zoom Bounding Boxes (`AF-R2.4-4`, WAKE-668 d):**
   - Section 2 Date Zoom Row coordinates updated so every single bay provides a 100% unclipped, full-bleed view of the date / title banner:
     - **Bay 1 (`26SQRP`):** `(270, 700, 730, 845)` on `26SQRP_b.webp` -> complete `"1776 ~ 2026"` dual date.
     - **Bay 2 (`26XL`):** `(370, 885, 830, 1025)` on `26xl___a.webp` -> complete `"1776-2026"` dual date & bottom rim.
     - **Bay 3 (`26EA`):** `(370, 910, 830, 1025)` on `26ea_a.webp` -> complete `"1776-2026"` dual date strike.
     - **Bay 4 (`26XE`):** `(350, 850, 850, 1015)` on `26xe_a.webp` -> complete `"*1776~2026*"` Morgan dual date.
     - **Bay 5 (`26XH`):** `(315, 730, 685, 855)` on `26XH_image_3.jpg` -> complete `"1776~2026"` Peace dual date & privy.
     - **Bay 6 (`26XF`):** `(350, 850, 850, 1015)` on `26xe_a.webp` -> complete `"*1776~2026*"` Morgan dual date.
     - **Bay 7 (`26RJ`):** `(260, 40, 760, 210)` on `26rj_a.webp` -> complete `"2026 UNCIRCULATED COIN SET"` header banner.

6. **Target Naming: Lowercase Mint Codes (WAKE-668 f):**
   - Per `test_series_manifest_sync.py` conventions, target GCS blob names use strictly lowercase mint codes (e.g. `26sqrp_b.webp`, `26xl___a.webp`, `26xh_image_3.jpg`, `26ea_a.webp`, `26xe_a.webp`, `26rg_b.webp`, `26rj_a.webp`, `26gc_b.webp`).

7. **Prose & Section 8 Alignment (`AF-R2.4-5`, WAKE-668 e):**
   - Dual-date wording aligned across all sections (`1776 ~ 2026`, `1776-2026`, `*1776~2026*`).
   - Section 8 catalog snippet `26SQRP` `"image_url_obverse"` updated from legacy Wikimedia link to canonical GCS path: `"https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp"`.
```
```markdown
| # | SKU | Product Name | Unique Side Depicted | Primary Image Source File (NET-665C / 665B) | Target GCS Path (Lowercase Mint Code) | Status Badge |
| :- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **26SQRP** | Trump $1 25-Coin Roll | **Obverse** (Trump) | Eric 7C: `26SQRP_b.webp` | `gs://numista-reference-library/.../2026_products/26sqrp_b.webp` | **Genuine 2026 Obverse (7C)** |
| 2 | **26XL** | 2026 Peace Dollar Rev Proof | **Obverse** (Peace Liberty) | Eric 7C: `26xl___a.webp` | `gs://numista-reference-library/.../2026_products/26xl___a.webp` | **Genuine 2026 Obverse (7C)** |
| 3 | **26XM** | 2026 Peace Dollar Uncirculated | **Obverse** (Peace Liberty) | NET-665B: `26XH_image_3.jpg` | `gs://numista-reference-library/.../2026_products/26xh_image_3.jpg` | **Genuine 2026 Obverse (665B)** |
| 4 | **26EA** | 2026 Silver Eagle Proof | **Obverse** (Walking Liberty)| Eric 7C: `26ea_a.webp` | `gs://numista-reference-library/.../2026_products/26ea_a.webp` | **Genuine 2026 Obverse (7C)** |
| 5 | **26XE** | 2026 Morgan Enhanced Unc | **Obverse** (Morgan Liberty) | Eric 7C: `26xe_a.webp` | `gs://numista-reference-library/.../2026_products/26xe_a.webp` | **Genuine 2026 Obverse (7C)** |
| 6 | **26XH** | 2026 Peace Enhanced Unc | **Obverse** (Peace Liberty) | NET-665B: `26XH_image_3.jpg` | `gs://numista-reference-library/.../2026_products/26xh_image_3.jpg` | **Genuine 2026 Obverse (665B)** |
| 7 | **26XF** | 2026 Morgan Dollar Rev Proof | **Obverse** (Morgan Liberty) | Eric 7C: `26xe_a.webp` | `gs://numista-reference-library/.../2026_products/26xe_a.webp` | **Genuine 2026 Obverse (7C)** |
| 8 | **26RG** | 2026 Semiquin Proof Set | **Set Blister Lens** (Coins) | Eric 7C: `26rg_b.webp` | `gs://numista-reference-library/.../2026_products/26rg_b.webp` | **Genuine 2026 Lens (7C)** |
| 9 | **26RJ** | 2026 Uncirculated Coin Set | **Packaging** (Blister Card) | Eric 7C: `26rj_a.webp` | `gs://numista-reference-library/.../2026_products/26rj_a.webp` | **Genuine 2026 Packaging (7C)** |
| 10| **26GC** | 2026 Innovation Rev Proof Set| **4-Coin Reverse Lens** (Iowa, Refrig, Cray-1, Jobs)| Eric 7C: `26gc_b.webp` | `gs://numista-reference-library/.../2026_products/26gc_b.webp` | **Genuine 2026 Reverse Lens (7C)** |
| 11| **2026-AI-IA**| American Innovation Iowa | **Reverse** (Iowa Subject) | NET-665B: `2026_american_innovation_iowa_reverse.jpg` | `gs://numista-reference-library/.../2026_series/2026_american_innovation_iowa_reverse.jpg` | **Genuine 2026 Reverse (665B)** |
```
```python
"26SQRP": {
    "title": "2026 Semiquincentennial Presidential $1 25-Coin Roll (Donald J. Trump)",
    "formal_name": "Semiquincentennial Presidential $1 Coin 2026 Rolls \u2013 Donald J. Trump",
    "year": 2026,
    "mint_mark": "",
    "denomination": "Dollar",
    "program_series": "Presidential $1 Coins",
    "theme_subject": "Donald J. Trump",
    "strike_type": "Uncirculated",
    "condition": "Uncirculated",
    "metal_content": "Manganese-Brass",
    "issue_price": "$61.00",
    "coins_per_roll": 25,
    "face_value": "$25.00",
    "retailer": "United States Mint",
    "image_url_obverse": "https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp",
    "representative_image": False,
}
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

## 3. Eye-Inspection of Section 2 Date Zoom Row (`NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.5.png` & `scratch/crops_r25/*.png`)

Why did Bays 1, 2, and 5 still clip the outer `"1"` and `"6"` / `"2 6"` digits in `R2.5`? Because on `26SQRP_b.webp`, `26xl___a.webp`, and `26XH_image_3.jpg`, the Semiquincentennial legend `"1 7 7 6 ~ 2 0 2 6"` is spaced wide along the curved lower rim, so the outer `"1"` and `"2 6"` curve upward and outward beyond `x=270..730`, `x=370..830`, and `x=315..685`.

We tested and visually inspected wider crop boxes directly against the source files to guarantee **zero** digit clipping:

| Zoom Bay | SKU | R2.5 Crop Used | What Actually Rendered in `R2.5.png` (`scratch/crops_r25/`) | Verdict & Visually Verified Unclipped Crop Box |
| :--- | :--- | :--- | :--- | :--- |
| **Bay 1** | `26SQRP` | `(270, 700, 730, 845)` on `26SQRP_b.webp` (`1000x875`) | **CLIPPED:** Shows **`"7 6 ~ 2 0"`** — cuts off `"1"` on the left and **`"2 6"`** of `"2026"` on the right! | **RE-CROP:** **`(160, 580, 840, 845)`** (visually verified to show the entire `"1 7 7 6 ~ 2 0 2 6"` arc with margin). |
| **Bay 2** | `26XL` | `(370, 885, 830, 1025)` on `26xl___a.webp` (`1200x1050`) | **CLIPPED:** Shows **`"7 7 6 ~ 2 0 2"`** — cuts off `"1"` on the left and **`"6"`** of `"2026"` on the right! | **RE-CROP:** **`(250, 815, 950, 1025)`** (visually verified to show the entire `"1 7 7 6 ~ 2 0 2 6"` arc with margin). |
| **Bay 3** | `26EA` | `(370, 910, 830, 1025)` on `26ea_a.webp` (`1200x1050`) | **100% UNCLIPPED:** Crisp, full `"1776-2026"` centered at bottom rim. | **PASS** |
| **Bay 4** | `26XE` | `(350, 850, 850, 1015)` on `26xe_a.webp` (`1200x1050`) | **100% UNCLIPPED:** Crisp, full `"*1776~2026*"` with flanking stars. | **PASS** |
| **Bay 5** | `26XH` | `(315, 730, 685, 855)` on `26XH_image_3.jpg` (`1000x875`) | **CLIPPED:** Shows **`"7 7 6 ~ 2 0 2"`** — cuts off `"1"` on the left and **`"6"`** of `"2026"` on the right! | **RE-CROP:** **`(210, 680, 790, 855)`** (visually verified to show the entire `"1 7 7 6 ~ 2 0 2 6"` arc with margin). |
| **Bay 6** | `26XF` | `(350, 850, 850, 1015)` on `26xe_a.webp` (`1200x1050`) | **100% UNCLIPPED:** Crisp, full `"*1776~2026*"` with flanking stars. | **PASS** |
| **Bay 7** | `26RJ` | `(260, 40, 760, 210)` on `26rj_a.webp` (`1200x1050`) | **100% UNCLIPPED:** Crisp `"2026 United States Mint UNCIRCULATED COIN SET"` banner and Treasury seal. | **PASS** |

*Minor Layout Note on Contact Sheet PNG Section 2 Header:* The right-aligned green sub-caption `"All crops 100% unclipped • Confirmed genuine Semiquincentennial strikes"` overlaps the right end of `"SECTION 2: OBLIGATORY DATE ZOOM ROW (HIGH-MAGNIFICATION DATE / BANNER INSPECTION BAYS)"` at `x ≈ 725..810` — shorten the left title to `"SECTION 2: OBLIGATORY DATE ZOOM ROW"` so the two strings do not collide.

---

## 4. Summary Scorecard

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Fix-Only Discipline & Pricing/Rounding Preservation** | 30 | **30 / 30** | Sections 2–6, 8 (pricing), 9 (`bulk_update_reviews`), and 10 (40-file test gate & `8.18.15+81818`) untouched. Zero code executed. |
| **2. All 11 Main Grid Card Thumbnails (`WAKE-668` `a, b, c`)** | 35 | **35 / 35** | `26XM`/`26XH` (`26XH_image_3.jpg`), `26XF` (`26xe_a.webp`), and `26GC` (`26gc_b.webp`) 100% fixed; all 11 upper-grid cards are clean, genuine 2026 images with zero box/case/COA composites. |
| **3. Contact Sheet Date Zoom Row (`WAKE-668` `d`)** | 25 | **18 / 25** | Bays 3 (`26EA`), 4 (`26XE`), 6 (`26XF`), and 7 (`26RJ`) are 100% unclipped; `-7` because Bays 1 (`26SQRP`: `"7 6 ~ 2 0"`), 2 (`26XL`: `"7 7 6 ~ 2 0 2"`), and 5 (`26XH`: `"7 7 6 ~ 2 0 2"`) still clip the outer `"1"` and `"6"` / `"2 6"` digits of `"1776~2026"`. Exact verified boxes provided in §3. |
| **4. Plan Text Alignment & Lowercase Naming (`WAKE-668` `e, f`)** | 10 | **10 / 10** | Dual-date prose aligned, §8 `26SQRP` URL updated to `26sqrp_b.webp`, and all target GCS paths use lowercase mint codes per `test_series_manifest_sync`. |
| **TOTAL** | **100** | **93 / 100** | **WRITTEN PLAN & 11 MAIN THUMBNAILS 100% READY; RE-CROP ZOOM BAYS 1, 2, 5 (`(160,580,840,845)`, `(250,815,950,1025)`, `(210,680,790,855)`) ON CONTACT SHEET PNG SO `'2026'` IS UNCLIPPED.** |
