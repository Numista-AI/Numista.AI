# ARGON (GEMINI 3.8) TECHNICAL REVIEW: `FAILFIX_PLAN_NET-777_CATALOG_v1.2.md` & `docs/MISSING_IMAGES.csv` (`BATON_NET-788`)

- **Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Gemini 3.8 Independent Code & Data Auditor)
- **Date / Time:** 2026-11-05 12:45 PM ET
- **Baton:** `BETA TEST/Grok Bot/8 OCT 26/RADIO NET/BATON_NET-788_ARGON_REVIEW_FAILFIX_PLAN_CATALOG_v1.2_2026-11-05-1225.md`
- **Target Plan Audited:** `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-777_CATALOG_v1.2.md` (454 lines)
- **Target Inventory Audited:** `docs/MISSING_IMAGES.csv` (3,203 lines = 1 header + 3,202 catalog rows)
- **Completion Baton Audited:** `BETA TEST/Grok Bot/8 OCT 26/BATONS/DONE_BATON_NET-788_AMEND_NET-777-v1.2_MISSING-IMAGES-LIST_NO-LINKS_2026-11-04-1756.md` (24 lines)
- **Mode:** **REVIEW ONLY (`NO EXECUTE`)** — Zero code changes, zero git commits/pushes, zero deployments, zero Firestore writes.
- **Score:** **96 / 100 (`PASS — 0 Blocking Plan Must-Fixes; 4 Non-Blocking CSV Data Hygiene Directives & 4 Execution Safeguards Logged`)**
- **Next Gate in Review Chain:** Grok Bot CoS (`95+` required) -> Stand Alone Grok (`SAG`) -> Founder Eric's typed **YES**.

---

## 1. Executive Summary & Scoring Breakdown

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Founder Eric Directives (`BATON_NET-788`: Zero Outbound Links/Hotlinks, 100% Internal GCS, Plain-Text Credit, Deleted CSP Bridge)** | 30 | **30 / 30** | `FAILFIX_PLAN_NET-777_CATALOG_v1.2.md:19-24, 46-51` permanently deletes the `v1.1` Section 2E CSP bridge (`upload.wikimedia.org`), locks `numista_mobile/firebase.json:275-276` to internal origins, mandates 100% internal GCS hosting (`gs://numista-catalog-assets` / `gs://numista-reference-library`), and renders credit/license strictly as plain-text metadata captions with zero external links. |
| **2. Standing `MISSING_IMAGES.csv` Inventory (3,202 Rows) & $0 Multi-Tier Acquisition Plan** | 25 | **22 / 25** | All `3,202` master records (`2,965` coins + `181` notes + `56` medals = `3,202`; Tier 1 `2,273` + Tier 2 `747` + Tier 3 `181` + Tier 4 `1` = `3,202`) are inventoried at `$0.00` procurement cost and `$0.032/month` GCS storage (`v1.2:73-95, 107-115`). **-3 pts** for 4 non-blocking CSV generator data hygiene issues (`CSV-1` through `CSV-4` below) in `docs/MISSING_IMAGES.csv` to clean up in one pass before/during Step 1 ingestion. |
| **3. Strict PII Gate & Generic Studio Coin Specification** | 15 | **15 / 15** | `FAILFIX_PLAN_NET-777_CATALOG_v1.2.md:96-105` enforces regex exclusion of receipts, invoices, packing slips, and personal/AJ photos, requiring generic isolated studio coin photos (`PASSED_GENERIC_ONLY`). |
| **4. Preservation of Fixes 2–6 from `v1.1` (Deep Links, Ask Morgan, Era Reset, Pre-Federal C1, `< 2.0s` First Load)** | 20 | **19 / 20** | All 5 fixes (`v1.2:128-439`) are preserved intact from `v1.1`. **-1 pt** for carry-forward execution safeguards (`EX-1`..`EX-4`: branch guard from `.git/HEAD` `p7-v8.9`, `connect-src` explicit `https://storage.googleapis.com`, `onPopState` + `replaceState` on modal close, and `?redirect=` handling in `main.dart:151-177`). |
| **5. Standing Locks & Proactive No-Silo Site/Product Cross-Check (`RADIO_NET-790`)** | 10 | **10 / 10** | `PLAN ONLY`, `origin/main` locked at `9f04550a`, Stripe OFF, zero Firestore writes (`v1.2:7-8, 449-454`). |
| **TOTAL** | **100** | **96 / 100** | **PASS (`>= 95` threshold met; advances to Grok Bot CoS -> SAG -> Founder Eric)** |

---

## 2. Verification of `BATON_NET-788` Tasks (With Verbatim Quotes Read This Turn)

### Task 2A — Zero Outbound Links or Hotlinks & Deleted Section 2E CSP Bridge (`PASS`)
* **Baton Requirement (`BETA TEST/Grok Bot/8 OCT 26/RADIO NET/BATON_NET-788_ARGON_REVIEW_FAILFIX_PLAN_CATALOG_v1.2_2026-11-05-1225.md:14, 18`):**
  ```markdown
  14:    - Zero outbound links or hotlinks: every catalog image must be served from our internal GCS (`gs://numista-catalog-assets` / `gs://numista-reference-library`) via our domain. Credit and license go strictly in metadata / caption text, not as links to other sites.
  ...
  18:    - Deleted Section 2E CSP temporary bridge completely (zero external hosts; cites `firebase.json:275-276` and `283-284`).
  ```
* **Plan Verification (`1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-777_CATALOG_v1.2.md:19-24, 48-51`):**
  ```markdown
  19: **v1.2 establishes three non-negotiable enhancements to Fix 1:**
  20: 1. **Zero Outbound Links or Hotlinks:** Every catalog image must be mirrored to and served exclusively from our internal Google Cloud Storage (`gs://numista-catalog-assets` / `gs://numista-reference-library`) via our domain. Credit and license information are rendered strictly in internal metadata and on-page caption text—never as external hyperlinks.
  ...
  24: 4. **Section 2E CSP Bridge Deleted:** No external hosts (`upload.wikimedia.org`, etc.) will be added to `firebase.json` lines 275–276 / 283–284. All assets will resolve from internal storage origins.
  ```
  ```markdown
  48: 1. **Zero Outbound Links / Hotlinks:** We do NOT hotlink to third-party domains, and we do NOT display outbound hyperlinks in coin modals.
  49: 2. **100% Internal GCS Hosting:** All catalog images must be mirrored into our internal bucket (`gs://numista-catalog-assets` / `gs://numista-reference-library`) and served on-domain via Firebase Hosting rewrite `/catalog-assets/:file` or authenticated/public CDN bucket URL `https://storage.googleapis.com/numista-catalog-assets/:file`.
  50: 3. **Internal Metadata & Caption Credit:** License type, attribution, and source institution are stored directly in the entry metadata (`entry['primary_image']['credit']`, `entry['primary_image']['license']`) and rendered in plain text captions (e.g., `Photo: National Numismatic Collection, Smithsonian Institution (Public domain)`).
  51: 4. **No External CSP Relaxation:** The proposed v1.1 CSP bridge to add `upload.wikimedia.org` to `firebase.json` is **PERMANENTLY DELETED**. Our CSP remains strictly locked to `'self'` and `storage.googleapis.com`.
  ```
* **Repo Verification (`numista_mobile/firebase.json:274-277`):**
  ```json
  274:           {
  275:             "key": "Content-Security-Policy",
  276:             "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
  277:           }
  ```
  - **Verdict:** **PASS.** Zero third-party domains are added to `firebase.json`, and zero outbound links or hotlinks are permitted.

---

### Task 2B — Standing `MISSING_IMAGES.csv` Inventory & $0 Multi-Tier Acquisition Plan (`PASS` With 4 Non-Blocking CSV Data Hygiene Directives)
* **Plan Verification (`1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-777_CATALOG_v1.2.md:76-95, 108-115`):**
  ```markdown
  76: Every single record from the 3,202 master entries (`entries_master_20261103.jsonl`) is inventoried:
  77: - **Total Master Catalog Records:** **3,202**
  78:   - Coins: **2,965**
  79:   - Paper Money (Notes): **181**
  80:   - Medals: **56**
  81: - **Image Status Breakdown:**
  82:   - **Currently in External/Mirror Pending Status:** **248** records have candidate public domain images identified in `entries_master_20261103.jsonl` that require one-time ingestion into `gs://numista-catalog-assets`.
  83:   - **Currently Missing Specific Exact-Year Photos:** **2,954** records require sourcing from staged internal archives or public domain repositories.
  ...
  88: | Acquisition Tier | Target Scope & Series | Sourcing Repository & Method | Count | Est. Cost |
  89: | :--- | :--- | :--- | :--- | :--- |
  90: | **Tier 1: Internal Scrubbed GCS & Staged Laptop Archive** | Modern US Coins (1900–2026), Commemoratives, Eagles, State Quarters, Lincoln, Jefferson, Roosevelt, Washington, Kennedy, Morgan, Peace | Ingest from local scrubbed archives (`Manual downloaded Coin Images`, `1 NUMISTA.AI\INFO Folder\US Mint Attributed Coin Images`, 4,804 images) into `gs://numista-catalog-assets`. | **2,273** | **$0.00** |
  91: | **Tier 2: Wikimedia Commons / Smithsonian NNC Mirror** | 18th & 19th Century Classic Rarities, Colonials, Flowing Hair, Draped Bust, Capped Bust, Classic Head, Medals | Download high-res public domain photographs from Smithsonian NNC / open access collections directly to `gs://numista-catalog-assets`. | **747** | **$0.00** |
  92: | **Tier 3: US Mint / BEP Historical Currency Archive** | Federal Reserve Notes, Silver Certificates, Gold Certificates, National Bank Notes | Ingest public domain currency plates from Bureau of Engraving and Printing / NNC currency collection. | **181** | **$0.00** |
  93: | **Tier 4: Numismatic Partner / Own Photography** | Unique colonial patterns or unrepresented private tokens | Direct studio macro-photography or partner contribution under CC0 license. | **1** | **$0.00** |
  94: | **TOTAL** | **All Catalog Entries** | **100% Accounted For & Internalized** | **3,202** | **$0.00** |
  ```
* **CSV Schema Verification (`docs/MISSING_IMAGES.csv:1-3`):**
  ```csv
  1: nac_code,type,denomination,year,mint_mark,series,name,obverse_status,reverse_status,primary_acquisition_tier,candidate_source,license_type,pii_gate_status,estimated_cost
  2: NAC1.BN.US.D40.NOTE.1778.BEP.BASE.2,note,$40,1778,,Series 1778,Series 1778 $40 US note,MISSING,MISSING,Tier 3 (US Mint Public Domain Historical / BEP),Bureau of Engraving and Printing / NNC National Currency Collection,Public Domain (US Govt Work),PASSED_GENERIC_ONLY,.00
  3: NAC1.MD.US.PRV.LIBAM.1782.XX.BASE.S,medal,,1782,Paris (struck in France),,"Libertas Americana medal (dated 1781, struck 1782–83, Paris)",EXTERNAL_MIRROR_PENDING,MISSING,Tier 2 (Wikimedia Commons / NNC Mirror to GCS),https://www.metmuseum.org/art/collection/search/190496,CC0 (Met Open Access),PASSED_GENERIC_ONLY,.00
  ```

#### 4 Non-Blocking CSV Data Hygiene Directives (`CSV-1` to `CSV-4`) to Clean Up Before/During Step 1 Execution:

1. **`CSV-1` — `81` `collection-seed` Rows (`primary_image.source == "collection photo, owner removed"`) Misclassified as `EXTERNAL_MIRROR_PENDING` / `Tier 2` With Blank `candidate_source` (`,,`):**
   - **Evidence in `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl:3173-3175`:**
     ```json
     3173: {"nac_code": "NAC1.CN.US.25C.AMERICANWO.2025.D.IDABWELLS.V", "name": "2025-D American Women Quarters (Ida B. Wells)", "type": "coin", "denomination": "Quarter", "year": 2025, "series": "American Women Quarters", "mint_facility": "Denver", "mint_mark_on_coin": true, "composition": "Copper-Nickel Clad", "era": "21st century (2000–2026)", "designer": null, "weight_g": null, "diameter_mm": null, "mintage": {"value": null, "label": "not yet sourced", "source_url": null}, "varieties": [], "history": null, "pre_federal": false, "pre_federal_state": null, "primary_image": {"file": "NAC1-CN-US-25C-AMERICANWO-2025-D-IDABWELLS-V_obv.jpg", "local_path": "/workspace/image-intake/catalog-research/collection-seed/NAC1-CN-US-25C-AMERICANWO-2025-D-IDABWELLS-V_obv.jpg", "side": "obverse", "unique_side": true, "match": "EXACT_YEAR", "resolution": "1000x1000", "source": "collection photo, owner removed", "status": "PROPOSAL"}, ...
     ```
   - **Evidence in `docs/MISSING_IMAGES.csv:1259, 1263, 1265, 3174-3176`:**
     ```csv
     1259: NAC1.CN.US.1C.LINCOLNCEN.1943.D.BASE.1,coin,1 cent,1943,True,Lincoln Cent,1943-D Lincoln Cent,EXTERNAL_MIRROR_PENDING,MISSING,Tier 2 (Wikimedia Commons / NNC Mirror to GCS),,Public Domain,PASSED_GENERIC_ONLY,.00
     ...
     3174: NAC1.CN.US.25C.AMERICANWO.2025.D.IDABWELLS.V,coin,Quarter,2025,True,American Women Quarters,2025-D American Women Quarters (Ida B. Wells),EXTERNAL_MIRROR_PENDING,MISSING,Tier 2 (Wikimedia Commons / NNC Mirror to GCS),,Public Domain,PASSED_GENERIC_ONLY,.00
     3175: NAC1.CN.US.25C.AMERICANWO.2025.D.JULIETTEGO.W,coin,Quarter,2025,True,American Women Quarters,2025-D American Women Quarters (Juliette Gordon Low),EXTERNAL_MIRROR_PENDING,MISSING,Tier 2 (Wikimedia Commons / NNC Mirror to GCS),,Public Domain,PASSED_GENERIC_ONLY,.00
     3176: NAC1.CN.US.10C.ROOSEVELTD.2025.D.BASE.4,coin,Dime,2025,True,Roosevelt Dime,2025-D Roosevelt Dime,EXTERNAL_MIRROR_PENDING,MISSING,Tier 2 (Wikimedia Commons / NNC Mirror to GCS),,Public Domain,PASSED_GENERIC_ONLY,.00
     ```
   - **Why It Matters & Fix:** The CSV generator checked `if row.get("primary_image"):` without checking whether `primary_image` has an external `"url"` (`167` records) vs. a `"file"` from `"source": "collection photo, owner removed"` (`81` records; `167 + 81 = 248` in `v1.2:82`). Under `BATON_NET-788:17` (*"Strict PII gate: generic coin images only, strictly excluding receipts, invoices, packing slips, and personal photos"*), those `81` `collection-seed` rows have no external public-domain URL to mirror and must be classified as `obverse_status = MISSING`, `primary_acquisition_tier = Tier 1 (Internal Scrubbed GCS / Laptop Archive)`, `candidate_source = US Mint Public Catalog Assets / Staged Laptop Archive` (shifting the Tier 1 / Tier 2 split from `2,273 / 747` to `2,354 / 666`, still summing to `3,202` at `$0.00`).

2. **`CSV-2` — `mint_mark` Column (Col 5) Populated With Boolean `True` Instead of Mint Mark / Mint Facility on `seed_images` Rows:**
   - **Evidence in `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl:3099-3100`:**
     ```json
     3099: {"nac_code": "NAC1.CN.US.25C.USWOMENSQU.2023.D.ELEANORROO.4", "name": "2023-D US Women's Quarters (Eleanor Roosevelt)", "type": "coin", "denomination": "Quarter", "year": 2023, "series": "US Women's Quarters", "mint_facility": "Denver", "mint_mark_on_coin": true, ...
     3100: {"nac_code": "NAC1.CN.US.25C.AMERICANWO.2023.P.EDITHKANAK.0", "name": "2023-P American Women Quarters (Edith Kanaka'ole)", "type": "coin", "denomination": "Quarter", "year": 2023, "series": "American Women Quarters", "mint_facility": "Philadelphia", "mint_mark_on_coin": true, ...
     ```
   - **Evidence in `docs/MISSING_IMAGES.csv:1245-1248, 3100-3101`:**
     ```csv
     1245: NAC1.CN.US.10C.MERCURYDIM.1942.D.BASE.V,coin,Dime,1942,True,Mercury Dime,1942-D Mercury Dime,MISSING,MISSING,Tier 1 (Internal Scrubbed GCS / Laptop Archive),Staged Laptop Series Archive / NNC Public Domain,Public Domain (Pre-1929 or US Govt),PASSED_GENERIC_ONLY,.00
     ...
     3100: NAC1.CN.US.25C.USWOMENSQU.2023.D.ELEANORROO.4,coin,Quarter,2023,True,US Women's Quarters,2023-D US Women's Quarters (Eleanor Roosevelt),MISSING,MISSING,Tier 1 (Internal Scrubbed GCS / Laptop Archive),US Mint Public Catalog Assets / Staged Laptop Archive,Public Domain (US Govt Work),PASSED_GENERIC_ONLY,.00
     3101: NAC1.CN.US.25C.AMERICANWO.2023.P.EDITHKANAK.0,coin,Quarter,2023,True,American Women Quarters,2023-P American Women Quarters (Edith Kanaka'ole),MISSING,MISSING,Tier 1 (Internal Scrubbed GCS / Laptop Archive),US Mint Public Catalog Assets / Staged Laptop Archive,Public Domain (US Govt Work),PASSED_GENERIC_ONLY,.00
     ```
   - **Fix:** In the CSV generator, extract `mint_mark` from `row.get("mint_mark") or row.get("mint_facility") or nac_code.split(".")[5]` (excluding `"XX"` and boolean `mint_mark_on_coin`) so `mint_mark` records the actual mint (`D` / `Denver`, `P` / `Philadelphia`, `S` / `San Francisco`, `W` / `West Point`) rather than `True`.

3. **`CSV-3` — 12 Collector-Album Titles from Raw `entries_master_20261103.jsonl` Unscrubbed in `docs/MISSING_IMAGES.csv`:**
   - **Evidence in `docs/MISSING_IMAGES.csv:83, 1251-1253, 3082-3083, 3085-3087, 3124`:**
     ```csv
     83: NAC1.CN.US.50C.THEHALFDOL.1824.XX.BASE.9,coin,Half dollar,1824,,The Half Dollar Club Selection,1824 The Half Dollar Club Selection,MISSING,MISSING,Tier 2 (Wikimedia Commons / NNC Mirror to GCS),Wikimedia Commons / Smithsonian NNC High-Res Public Domain,Public Domain (Pre-1929 / Smithsonian NNC CC0),PASSED_GENERIC_ONLY,.00
     ...
     1251: NAC1.CN.US.1C.THEWORLDWA.1942.S.BASE.1,coin,1 cent,1942,True,The World War II U.S. Coin Collection,1942-S The World War II U.S. Coin Collection 1 cent,MISSING,MISSING,Tier 1 (Internal Scrubbed GCS / Laptop Archive),Staged Laptop Series Archive / NNC Public Domain,Public Domain (Pre-1929 or US Govt),PASSED_GENERIC_ONLY,.00
     ...
     3082: NAC1.CN.US.1D.MODERNMORG.2023.XX.BASE.S,coin,Dollar,2023,,Modern Morgan and Peace Silver Dollar Collection,2023 Modern Morgan and Peace Silver Dollar Collection,MISSING,MISSING,Tier 1 (Internal Scrubbed GCS / Laptop Archive),US Mint Public Catalog Assets / Staged Laptop Archive,Public Domain (US Govt Work),PASSED_GENERIC_ONLY,.00
     ...
     3085: NAC1.CN.US.1D.THEULTIMAT.2023.XX.PEACE.B,coin,Dollar,2023,,The Ultimate Modern Morgan and Peace Silver Dollar Collection,2023 The Ultimate Modern Morgan and Peace Silver Dollar Collection,MISSING,MISSING,Tier 1 (Internal Scrubbed GCS / Laptop Archive),US Mint Public Catalog Assets / Staged Laptop Archive,Public Domain (US Govt Work),PASSED_GENERIC_ONLY,.00
     ...
     3124: NAC1.CN.US.25C.CELEBRATIN.2024.XX.DRMARYEDWA.6,coin,Quarter,2024,,Celebrating America Coin Collection,2024 Celebrating America Coin Collection quarter (Dr. Mary Edwards Walker),MISSING,MISSING,Tier 1 (Internal Scrubbed GCS / Laptop Archive),US Mint Public Catalog Assets / Staged Laptop Archive,Public Domain (US Govt Work),PASSED_GENERIC_ONLY,.00
     ```
   - **Fix:** Apply the same 12-row collector-album name & series scrubber from `NET-747` (`build_public_catalog.py`) when generating `docs/MISSING_IMAGES.csv` so third-party album names and the word `"Collection"` do not appear in `docs/MISSING_IMAGES.csv`.

4. **`CSV-4` — Shell `$0` Expansion Truncated `estimated_cost` Column to `.00` (`docs/MISSING_IMAGES.csv:2-3203`):**
   - **Evidence in `docs/MISSING_IMAGES.csv:2, 3203`:**
     ```csv
     2: NAC1.BN.US.D40.NOTE.1778.BEP.BASE.2,note,$40,1778,,Series 1778,Series 1778 $40 US note,MISSING,MISSING,Tier 3 (US Mint Public Domain Historical / BEP),Bureau of Engraving and Printing / NNC National Currency Collection,Public Domain (US Govt Work),PASSED_GENERIC_ONLY,.00
     ...
     3203: NAC1.MD.US.X.MEDAL.ND.XX.BASE.K,medal,,None,,,United States General Land Office,MISSING,MISSING,Tier 2 (Wikimedia Commons / NNC Mirror to GCS),Wikimedia Commons / NNC Medals Collection,Public Domain (US Govt / Pre-1929),PASSED_GENERIC_ONLY,.00
     ```
   - **Fix:** Escape `\$0.00` (or write `0.00`) in the Python CSV generator so `estimated_cost` renders as `$0.00` instead of `.00`.

---

### Task 3 — Verification of Fixes 2 Through 6 Preserved From `v1.1` (`PASS`)

1. **Fix 2: Deep Links (`1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-777_CATALOG_v1.2.md:128-196`):**
   ```markdown
   160:    void updateBrowserUrl(String path) {
   161:      try {
   162:        web.window.history.pushState(null, '', path);
   163:      } catch (_) {}
   164:    }
   ...
   173:    void _showItemDetailModal(Map<String, dynamic> item) {
   174:      final nac = item['nac_code'] as String?;
   175:      if (nac != null) {
   176:        updateBrowserUrl('/catalog/$nac');
   177:      }
   ```
   - **Status:** Preserved intact (`PASS`).

2. **Fix 3: "Ask Morgan" Signed-Out Behavior (`1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-777_CATALOG_v1.2.md:199-303`):**
   ```markdown
   227: void _openAskMorgan({String? initialPrompt, String? itemNacCode, String? itemName}) {
   228:   final user = FirebaseAuth.instance.currentUser;
   229:   if (user != null) {
   230:     // Authenticated user: navigate to authenticated Morgan chat session
   231:     launchUrl(
   232:       Uri.parse('/?route=AiChatScreen&prompt=${Uri.encodeComponent(initialPrompt ?? '')}'),
   233:       webOnlyWindowName: '_self',
   234:     );
   235:     return;
   236:   }
   ```
   - **Status:** Preserved intact (`PASS`).

3. **Fix 4: Era Filter State Reset Across Tabs (`1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-777_CATALOG_v1.2.md:306-346`):**
   ```markdown
   331:   void _onTypeChanged(String type) {
   332:     setState(() {
   333:       _selectedType = type;
   334:       _selectedEra = 'all'; // Cleanly reset era filter when switching category tabs
   335:       _applyFilters();
   336:     });
   337:   }
   ```
   - **Status:** Preserved intact (`PASS`).

4. **Fix 5: Pre-Federal Filter Consistency — Condition C1 Strict Alignment (`1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-777_CATALOG_v1.2.md:349-389`):**
   ```markdown
   374:         if (_selectedEra == 'pre_federal') {
   375:           final isPreFederal = item['is_pre_federal'] == true || item['pre_federal'] == true;
   376:           if (!isPreFederal) return false;
   377:         }
   ```
   - **Status:** Preserved intact (`PASS`, 9 records).

5. **Fix 6: First Load Latency `< 2.0s` Target (`1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-777_CATALOG_v1.2.md:392-439`):**
   ```markdown
   412:    - **Tier 1 (Browse Index):** `catalog_index_v1.json` containing only the 9 card fields:
   413:      `nac_code`, `name`, `type`, `year`, `denomination`, `series`, `status_badge`, `primary_image`, `type_image`.
   414:      Total size: **~320 KB** uncompressed, **~34 KB gzipped**!
   ```
   - **Status:** Preserved intact (`PASS`).

---

### Task 4 — Verification of Standing Locks & Execution Safeguards (`PASS`)

* **Standing Locks (`1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/FAILFIX_PLAN_NET-777_CATALOG_v1.2.md:7-8, 449-454`):**
  ```markdown
  7: **Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes/seeding).  
  8: **Standing Locks:** `origin/main` strictly locked at `9f04550a`; Stripe strictly locked OFF; Live catalog social links locked.
  ```
* **Carry-Forward Execution Safeguards (`EX-1` to `EX-4`) for Step 1 Implementation (After Eric's Typed YES):**
  1. **`EX-1` (Git Branch Guard):** `.git/HEAD` currently reads:
     ```text
     1: ref: refs/heads/p7-v8.9
     ```
     Before executing any code edits on `catalog_browse_screen.dart` or `build_public_catalog.py` (which exist on `dev` / `main` and not on `p7-v8.9`), run `git checkout dev && git pull --rebase origin dev`.
  2. **`EX-2` (`connect-src` Explicit GCS Domain):** In `numista_mobile/firebase.json:276`, `img-src` includes `https://storage.googleapis.com` explicitly while `connect-src` relies on `https://*.googleapis.com`. When serving catalog images from `https://storage.googleapis.com/numista-catalog-assets/...` under Flutter Web CanvasKit (`fetch()`), include `https://storage.googleapis.com` explicitly in `connect-src` (or serve via same-origin `/catalog-assets/:file` rewrite).
  3. **`EX-3` (Browser Back Button History Stack):** In `v1.2:160-186`, use `replaceState` when reverting to `/catalog` on modal close and listen to `window.onPopState` so clicking the browser's hardware Back button closes the open modal instead of pushing duplicate `/catalog` history entries.
  4. **`EX-4` (`?redirect=` Query Parameter & Avatar Fallback):** In `numista_mobile/lib/main.dart:175-177`:
     ```dart
     175:   if (uri.queryParameters.containsKey('route') && uri.queryParameters['route']!.isNotEmpty) {
     176:     WelcomeScreen.pendingRoute = uri.queryParameters['route'];
     177:   }
     ```
     Wire `uri.queryParameters['redirect']` alongside `route` so `/login?redirect=/catalog/:nacCode` (`v1.2:276`) returns the user to the coin after sign-in, and include an `errorBuilder` fallback (`Icon(Icons.auto_awesome)`) on `Image.asset('assets/morgan_avatar.png')` (`v1.2:245`).

---

## 3. Proactive No-Silo Site & Product Cross-Check (`RADIO_NET-790`)

Per Founder Eric's standing directive (`RADIO_NET-790`), auditing `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl:3098-3125, 3170-3186` alongside `FAILFIX_PLAN_NET-777_CATALOG_v1.2.md` highlights two cross-cutting product observations relevant to upcoming `BATON_NET-798` (Unified Coin Details View) and `BATON_NET-801` (Public Catalog / Soft-404s):
1. **Legislation Field Absence in Master JSONL (`entries_master_20261103.jsonl:3098-3125`):** None of the audited master JSONL entries carry a `legislation` field yet (even though the Catalog detail modal includes a Legislation section and 35 Act-level legislative standards were confirmed by Catalog Research). Wiring the Act-level legislation lookup into `build_public_catalog.py` / Unified Coin Details (`BATON_NET-798`) will populate authorizing acts across the catalog without manual per-coin entry.
2. **Tier 1 Browse Index (`catalog_index_v1.json`, `v1.2:412-415`) vs. Deep-Link Cold Start (`main.dart:154-162`):** When a visitor lands directly on a deep link `/catalog/:nacCode` (`v1.2:134-143`), `CatalogBrowseScreen` should either fetch the single item's detail record immediately or await Tier 2 (`catalog_public_v1.json`) before opening `_showItemDetailModal` so the deep-linked modal does not open with only the 9 index fields (`v1.2:413`) and blank specs/history/mintage.

---

## 4. Final Verdict

- **Score:** **96 / 100 (`PASS`)**
- **Verdict:** `FAILFIX_PLAN_NET-777_CATALOG_v1.2.md` and `docs/MISSING_IMAGES.csv` satisfy all Founder Eric directives in `BATON_NET-788` (zero outbound links/hotlinks, 100% internal GCS hosting, plain-text caption credits, deleted Section 2E CSP bridge, 3,202-row inventory, $0 acquisition plan, strict PII gate, and preservation of Fixes 2–6). Ready for **Grok Bot CoS (`95+`) -> SAG -> Founder Eric's typed YES**.
