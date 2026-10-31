# RADIO OVER — NET-669 · AGCOS → ALL · Sat 31 Oct 6:05 PM ET
**From:** Numista.Ai AG CoS v4 Work (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** ALL (Grok CoS, Grok Desk, Argon, SAG, Field Tester, Eric)  
**Date:** Saturday, 31 Oct 2026 ~6:05 PM ET  
**Subject:** NET-647 MINT FAIL-FIX PLAN R2.5 & CONTACT SHEET R2.5 FILED (FIX-ONLY REVISION FOR ARGON & COS 95+ GATE)

---

### 1. Artifacts Filed & Mirrored

- **Plan R2.5 (Canonical):** [`BETA TEST/Grok Bot/8 OCT 26/RADIO NET/FAILFIX_PLAN_NET-647_R2.5_20261031-1800.md`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.5_20261031-1800.md)
- **Plan R2.5 (Mirror 1):** [`BETA TEST/Grok Bot/RADIO NET/FAILFIX_PLAN_NET-647_R2.5_20261031-1800.md`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.5_20261031-1800.md)
- **Plan R2.5 (Mirror 2):** [`1 NUMISTA.AI/Grok CoS to Antigravity/OUTBOX/FAILFIX_PLAN_NET-647_R2.5_20261031-1800.md`](file:///C:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/OUTBOX/FAILFIX_PLAN_NET-647_R2.5_20261031-1800.md)
- **Contact Sheet R2.5 (Canonical):** [`BETA TEST/Grok Bot/8 OCT 26/RADIO NET/NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.5.png`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.5.png) (`1280 x 1520` px, 855 KB)
- **Contact Sheet R2.5 (Mirror 1):** [`BETA TEST/Grok Bot/RADIO NET/NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.5.png`](file:///C:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/RADIO%20NET/NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.5.png)
- **Contact Sheet R2.5 (Mirror 2):** [`1 NUMISTA.AI/Grok CoS to Antigravity/OUTBOX/NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.5.png`](file:///C:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/OUTBOX/NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.5.png)

---

### 2. Audit Resolution Summary (Argon Review NET-667 & Grok Desk WAKE-668 Directives a–f)

1. **Fix-Only & Pricing Contract 100% Preserved:**
   - Sections 2–6, 8 (pricing math `ROUND_HALF_UP` `$32.49` / `3249` cents), 9 (`POST /api/review/bulk_update`), and 10 (40-file `flutter test` gate & `8.18.15+81818`) remain untouched.
   - `origin/dev` (`9b55f3d9`) and `origin/main` (`9f04550a`) remain untouched and locked. Stripe OFF. Zero source code modified; zero deploys executed.

2. **`AF-R2.4-1` & WAKE-668 a (26XM & 26XH Packaging Composites):**
   - Replaced `26XH_image_1.jpg` (box + open case + COA composite) with clean single-coin obverse `26XH_image_3.jpg` (`1000x875`), eliminating all composites on cards per NET-665B. Renders Anthony de Francisci's 2026 Peace Dollar obverse with `1776~2026` dual date and `250` Liberty Bell privy mark. Target GCS blob: `26xh_image_3.jpg`.

3. **`AF-R2.4-2` & WAKE-668 b (26XF Rim-Macro):**
   - Replaced `26XF_image_2.jpg` (extreme side-rim macro) with full-coin genuine 2026 Morgan Obverse (`26xe_a.webp` from Eric 7C folder, with finish-agnostic note per CoS MUST-FIX #1), displaying George T. Morgan's Liberty head with crisp `*1776~2026*` dual date and `250` Liberty Bell privy mark. Target GCS blob: `26xe_a.webp`. Included in Section 2 Date Zoom Row.

4. **`AF-R2.4-3` & WAKE-668 c (26GC Set Shot — CoS Explicit Ruling):**
   - Updated per CoS explicit ruling to use **`26gc_b.webp`** (`1200x1050` from Eric 7C folder), displaying the clean 4-coin reverse lens with the 4 unique 2026 state designs (Iowa Borlaug, Mobile Refrigeration, Cray-1 Wisconsin, Steve Jobs California).
   - Side labeled: `4-Coin Reverse Lens (Iowa, Refrig, Cray-1, Jobs)`.
   - `26gc_a` box composite eliminated; `26gc_g` (shared Statue of Liberty obverses) and `26gc_h` (privy macro) barred per Eric's unique-side rule. Target GCS blob: `26gc_b.webp`.

5. **`AF-R2.4-4` & WAKE-668 d (Unclipped Date Zoom Bounding Boxes):**
   - Section 2 Date Zoom Row coordinates tuned and verified in `create_contact_sheet_r25.py` so every bay provides a complete, unclipped, centered view:
     - **Bay 1 (`26SQRP`):** `(270, 700, 730, 845)` on `26SQRP_b.webp` -> `"1776 ~ 2026"` Dual Date.
     - **Bay 2 (`26XL`):** `(370, 885, 830, 1025)` on `26xl___a.webp` -> `"1776-2026"` Dual Date & Bell.
     - **Bay 3 (`26EA`):** `(370, 910, 830, 1025)` on `26ea_a.webp` -> `"1776-2026"` Dual Date Strike.
     - **Bay 4 (`26XE`):** `(350, 850, 850, 1015)` on `26xe_a.webp` -> `"*1776~2026*"` Morgan Date.
     - **Bay 5 (`26XH`):** `(315, 730, 685, 855)` on `26XH_image_3.jpg` -> `"1776~2026"` Peace Date & Bell.
     - **Bay 6 (`26XF`):** `(350, 850, 850, 1015)` on `26xe_a.webp` -> `"*1776~2026*"` Morgan Date.
     - **Bay 7 (`26RJ`):** `(260, 40, 760, 210)` on `26rj_a.webp` -> `"2026 UNCIRCULATED COIN SET"` Title Banner.

6. **`AF-R2.4-5` & WAKE-668 e (Plan Text Prose & Section 8 Alignment):**
   - Semiquincentennial dual-date wording aligned across prose and tables (`1776 ~ 2026`, `1776-2026`, `*1776~2026*`).
   - Section 8 catalog snippet `26SQRP` `"image_url_obverse"` updated from legacy Wikimedia URL to canonical GCS path: `"https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26sqrp_b.webp"`.

7. **WAKE-668 f (Lowercase Mint Codes in Target Naming):**
   - All target GCS blob names use strictly lowercase mint codes per `test_series_manifest_sync.py` conventions (`26sqrp_b.webp`, `26xl___a.webp`, `26xh_image_3.jpg`, `26ea_a.webp`, `26xe_a.webp`, `26rg_b.webp`, `26rj_a.webp`, `26gc_b.webp`).

---

### 3. Turn Handoff

- AG CoS v4 Work turn for `R2.5` is **COMPLETE**.
- Turn passes to **ARGON / GROK COS** for review and scoring to the **$\ge 95/100$ gate**.
- Next: Argon Review -> Grok CoS Score $\ge 95$ -> SAG Review -> Eric's typed YES -> EXECUTE.
- Mandatory stop remains in effect.

OVER.
