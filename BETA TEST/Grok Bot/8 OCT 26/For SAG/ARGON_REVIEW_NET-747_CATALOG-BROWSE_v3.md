# ARGON_REVIEW_NET-747_CATALOG-BROWSE_v3 — Independent Technical & Data-Hygiene Audit of `AG_PLAN_NET-747_CATALOG-BROWSE_v3.md`

- **Reviewer:** Argon (`31035602` — Independent Technical Reviewer / Gemini 3.8 Code & Data Auditor)
- **Date / Time:** 2026-11-03 14:31 ET
- **Baton:** [`BATON_NET-754_ARGON_REVIEW_NET-747-v3_20261103-1425.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/BATON_NET-754_ARGON_REVIEW_NET-747-v3_20261103-1425.md)
- **Target Plan:** [`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md) (363 lines, filed 2026-11-03 14:13 ET by AG CoS v4)
- **Reference Directives & Data:**
  - [`INBOX/GBCOS_SCORE_NET-747_CATALOG-BROWSE_v2.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/GBCOS_SCORE_NET-747_CATALOG-BROWSE_v2.md) (`82/100 REVISE`)
  - [`BATONS/BATON_NET-753_AG_NET-747-PLAN-v3_20261103-1353.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/BATON_NET-753_AG_NET-747-PLAN-v3_20261103-1353.md)
  - [`INBOX/NET-747_inputs/entries_master_20261103.jsonl`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl) (`3,202` records)
- **Role / Boundary:** Review & Plans ONLY (`NO EXECUTE`). No code modified, no git commits/pushes, no deploys.

---

## 1. Executive Verdict & Score

- **Score:** **88 / 100 — REVISE TO v4 (4 of 6 `BATON_NET-754` Checks PASS Cleanly; 2 Checks (`#1` Nested Sub-Field Allow-List & `#2` Nested Scrub + Plain `"collection"` Gate) Have Live Data Leaks Verified Against `entries_master_20261103.jsonl`)**
- **Executive Summary:**
  - `AG_PLAN_NET-747_CATALOG-BROWSE_v3.md` cleanly resolves **Checks #3, #4, #5, and #6** from `BATON_NET-754` / `GBCOS_SCORE_NET-747_CATALOG-BROWSE_v2.md` (plus all 5 non-blocking notes `N-a`..`N-e`):
    - **Check #3 (`PASS`):** Exact 3,202 breakdown (`2,965` coins + `181` notes + `56` medals = `3,202`), `4` sourced mintages vs `3,198` `"Needs source"`, `951` placeholders (`display_label == "details coming"`), `9` Pre-Federal items.
    - **Check #4 (`PASS`):** Honest disclosure that `created_at` / `date_added` do not exist in `entries_master_20261103.jsonl`, fallback to Catalog Research file date (`3 Nov 2026`) with visible UI disclosure note, and exclusion of `fold_source == "seed_images"` (`2,612` rows) via internal boolean `is_interleaved_checklist_only: true`.
    - **Check #5 (`PASS`):** `"Ask Morgan"` button restyled as a filled navy primary button (`background: #0B2545`, `color: #FFFFFF`, `border: 2px solid #0B2545`) with `36x36` owl icon.
    - **Check #6 (`PASS`):** Explicit `firestore.rules` deploy guard and Firestore write guard requiring Founder Eric's separate typed YES, plus Phase 3 deploy YES explicitly restricted to preview channel `p7v12` (`origin/main` stays `9f04550a`).
  - **Why `v3` Cannot Pass Gate Without a Surgical `v4` (`MF-v3-A`, `MF-v3-B`, `MF-v3-C` on Checks #1 & #2):**
    When we ran an exhaustive key-by-key and substring-by-substring Python audit of all `3,202` rows in `entries_master_20261103.jsonl` against `v3`'s Section 3.1 allow-list (lines 116–147), Section 3.2 nested scrub rules (lines 149–155), and Section 3.2 PII gate scanner (line 158), we found **three concrete data-hygiene leaks** that would ship `"collection"` / `"COLLECTION_DERIVED"` wording into `catalog_public_v1.json` and break 81 exact-year seed images:
    1. **`MF-v3-A` (Check #1 & #2 — `type_image.source` [966 rows], `secondary_image.source` [23 rows], and `primary_image.source` [81 rows] Leak `"collection photo, owner removed"`, and `primary_image` Drops `file` on 81 Exact-Year Images):**
       - In `v3` lines 23–24 and 132–133, `type_image` and `secondary_image` explicitly whitelist the `source` sub-field:
         - `type_image: {url, file, side, note, resolution, source}`
         - `secondary_image: {url, file, side, resolution, source, unique_side}`
       - In `entries_master_20261103.jsonl`, **every single `type_image` (`966` rows) and every single `secondary_image` (`23` rows)** contains `"source": "collection photo, owner removed"` and `"status": "PROPOSAL"`!
       - Because `v3` line 158 only scans for `"collection-derived"` and `"collection-seed"` (NOT `"collection photo"` or plain `"collection"`), **all `989` `type_image` + `secondary_image` objects would publish `"source": "collection photo, owner removed"` straight into `catalog_public_v1.json` while passing `v3`'s scanner!**
       - Conversely, `v3` line 131 omits `file` from `primary_image: {url, full_url, side, unique_side, license, credit, source_url, resolution}`, even though the **81 exact-year seed `primary_image` rows** (e.g. Row 903 `NAC1.CN.US.50C.WALKINGLIB.1916.D.BASE.R`) have `"file": "NAC1-CN-US-50C-WALKINGLIB-1916-D-BASE-R-S01-OBV-6a5204d0.jpg"` and **no `url` key**—meaning `v3` line 131 strips the image path from all 81 exact-year seed `primary_image` objects!
    2. **`MF-v3-B` (Check #1 & #2 — `figures.composition` Leaks `"collection-derived, needs primary source"` and `"COLLECTION_DERIVED"` on 1,724 Rows, and `figures.*` Sub-Keys Are Not Allow-Listed):**
       - In `entries_master_20261103.jsonl`, all **1,724** non-null `figures.composition` objects are:
         `{"value": "Silver", "label": "collection-derived, needs primary source", "status": "COLLECTION_DERIVED"}` (0 of 1,724 are `SUPPORTED`).
       - Furthermore, `SUPPORTED` `figures.*` objects in `entries_master_20261103.jsonl` contain internal RAG pipeline keys: `claim`, `doc_id`, `from_file` (`"EXTRACT_retry.json"`), `grounding_score`, `method`, `replaced`, and `status`.
       - `v3` line 138 lists `figures: {mintage, weight_g, diameter_mm, fineness, composition}` without defining the permitted sub-keys inside each `figures.<metric>` object (`{value, unit, label, source_url}`) and without scrubbing `figures.composition` (`status == "COLLECTION_DERIVED"` / `label == "collection-derived, needs primary source"`).
    3. **`MF-v3-C` (Check #2 — `v3` Line 158 Scanner Omits Plain `"collection"`, Missing 12 Seed Rows with Album Names Containing `"Collection"` + 989 `"collection photo, owner removed"` + 1,724 `"COLLECTION_DERIVED"`):**
       - `BATON_NET-754` item #2 specifically directed: *"(v3 lists 'collection-derived' as a scan token; confirm plain 'collection' is caught too)."*
       - Confirmed: `v3` line 158 does **NOT** scan for plain `"collection"` or plain `"derived"`; it only scans for `"collection-derived"`, `"collection-seed"`, `"user-scoped"`.
       - Moreover, `v3` line 154 explicitly exempts *"The U.S. Nickel Collection in official series names"*, which is actually one of **12 `fold_source == "seed_images"` rows** where third-party album/marketing titles (`"The U.S. Nickel Collection"`, `"The World War II U.S. Coin Collection"`, `"Modern Morgan and Peace Silver Dollar Collection"`, `"The Ultimate Modern Morgan and Peace Silver Dollar Collection"`, `"Celebrating America Coin Collection"`) were ingested into `name` and `series` from user collection albums!

---

## 2. Point-by-Point Audit Against `BATON_NET-754` (6 Mandatory Checks)

### Check #1: Positive Field Allow-List for `catalog_public_v1.json` (Including Nested Sub-Fields of `primary_image`, `type_image`, `secondary_image`, `extra_images[]`)

- **Status:** **FAIL (`MF-v3-A` & `MF-v3-B`)**
- **Verbatim Citation from [`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md:130-139`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md#L130-L139):**
  ```markdown
  **Permitted Nested Sub-Fields (Strict Schema Enforcement):**
  - `primary_image`: `{url, full_url, side, unique_side, license, credit, source_url, resolution}`
  - `type_image`: `{url, file, side, note, resolution, source}`
  - `secondary_image`: `{url, file, side, resolution, source, unique_side}`
  - `extra_images[]`: `[{url, full_url, side, unique_side, license, credit, source_url}]`
  - `variety`: `{name, parent_nac_code, fs_number, description}`
  - `signatures`: `{left, right, titles}`
  - `seal`: `{color, type}`
  - `figures`: `{mintage, weight_g, diameter_mm, fineness, composition}`
  ```
- **Verbatim Citation from [`INBOX/NET-747_inputs/entries_master_20261103.jsonl:4`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl#L4) (Row 4 `NAC1.CN.US.1D.LIBERTYSEA.1840.XX.BASE.D` — representative of all 966 `type_image` rows):**
  ```json
  "type_image": {"file": "NAC1-CN-US-1D-LIBERTYSEA-XXXX-XX-NO-M-S01-OBV-aa088f27.jpg", "side": "OBV", "resolution": [314, 314], "note": "Representative type photo (year not visible on coin); exact year/mint visual not separately cataloged.", "source": "collection photo, owner removed", "status": "PROPOSAL"}
  ```
- **Verbatim Citation from [`INBOX/NET-747_inputs/entries_master_20261103.jsonl:903`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl#L903) (Row 903 `NAC1.CN.US.50C.WALKINGLIB.1916.D.BASE.R` — representative of all 81 exact-year seed `primary_image` rows and all 23 `secondary_image` rows):**
  ```json
  "primary_image": {"file": "NAC1-CN-US-50C-WALKINGLIB-1916-D-BASE-R-S01-OBV-6a5204d0.jpg", "side": "OBV", "resolution": [703, 700], "source": "collection photo, owner removed", "status": "PROPOSAL", "unique_side": true}, "secondary_image": {"file": "NAC1-CN-US-50C-WALKINGLIB-1916-D-BASE-R-S01-REV-5aaeb65b.jpg", "side": "REV", "resolution": [703, 704], "source": "collection photo, owner removed", "status": "PROPOSAL", "unique_side": true}
  ```
- **Verbatim Citation from [`INBOX/NET-747_inputs/entries_master_20261103.jsonl:51`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl#L51) (Row 51 `NAC1.CN.US.25C.DRAPEDBUST.1807.XX.BASE.M` — representative of all 1,724 `figures.composition` objects):**
  ```json
  "composition": {"value": "Silver", "label": "collection-derived, needs primary source", "status": "COLLECTION_DERIVED"}
  ```
- **Why Check #1 Fails (`MF-v3-A` & `MF-v3-B`):**
  1. **Allow-listing `source` inside `type_image` and `secondary_image` leaks `"collection photo, owner removed"` 989 times:** Every single `type_image` (`966` rows) and every single `secondary_image` (`23` rows) in `entries_master_20261103.jsonl` has `"source": "collection photo, owner removed"`. `source` and `status` MUST be removed from the nested allow-list of `primary_image`, `type_image`, and `secondary_image` and added to the explicit strip list!
  2. **Omitting `file` from `primary_image` breaks all 81 exact-year seed images:** In `entries_master_20261103.jsonl`, the `188` Wikimedia/museum `primary_image` objects use `url`/`full_url`, whereas the `81` exact-year seed `primary_image` objects (`188 + 81 = 269` total `primary_image` rows) only have `file` (`"NAC1-....jpg"`), NOT `url`. Either `file` must be included in `primary_image`'s allow-list (`{url, full_url, file, side, unique_side, license, credit, source_url, resolution}`) or transformed at build time into the public GCS CDN `url`.
  3. **`figures.<metric>` nested sub-keys must be strictly allow-listed:** In `entries_master_20261103.jsonl`, `figures.<metric>` contains `['claim', 'doc_id', 'from_file', 'grounding_score', 'label', 'method', 'replaced', 'source_url', 'status', 'unit', 'value']`. Each `figures.<metric>` sub-object must only allow `{value, unit, label, source_url}` (stripping `claim`, `doc_id`, `from_file`, `grounding_score`, `method`, `replaced`, `status`), and `figures.composition` (`1,724` rows, all `status == "COLLECTION_DERIVED"` and `label == "collection-derived, needs primary source"`) must either have its `label` scrubbed to `"Needs source"` (or be mapped to `value: null, label: "Needs source"` like all other unsourced figures).

---

### Check #2: Strip List + Real Scrub Step for `"seed"` and `"collection"` Wording Inside Nested Values, and Scan FAILS on Any Hit (Including Plain `"collection"`)

- **Status:** **FAIL (`MF-v3-C`)**
- **Verbatim Citation from [`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md:149-158`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md#L149-L158):**
  ```markdown
  ### 3.2 Scrubbing Pipeline for Nested Values & Automated Gate
  A dedicated scrubbing transformation (`scrub_nested_provenance()`) runs over all allowed string values (including nested values inside `history`, `notes`, `variety.description`, and `type_image.note`) prior to serialization:
  1. Any occurrence of `"seed"`, `"seed_images"`, `"seed-derived"`, `"collection-derived"`, `"collection-seed"`, or `"user-scoped"` is scrubbed or replaced with neutral catalog terminology (`"Catalog Research"` or `"Needs source"`).
  2. Specifically, inside `notes[]` and `history`, strings matching `"type_image attached from same-series seed image..."` are completely stripped from the array.
  3. Any `display_label` or `figures.*.label` containing `"not yet sourced"` is normalized to `"Needs source"`.
  4. Legitimate numismatic/museum credits (e.g., `"National Numismatic Collection, Smithsonian Institution"` in `primary_image.credit`, or `"The U.S. Nickel Collection"` in official series names) are preserved, while internal provenance phrases (`"collection-derived"`, `"collection-seed"`, `"from seed"`, `"user collection"`) are strictly banned.

  **Automated PII Gate (`pii_gate_validator.py`):**
  - Scans the entire serialized `catalog_public_v1.json` text.
  - **FAILS the build (exit code 1)** on ANY regex match for: `eric`, `user_id`, `uid`, `owner`, `personal`, `vault`, `seed`, `collection-derived`, `collection-seed`, `user-scoped`, `fold_source`, `seed_id`, `image_Match_type`, `image_source`, `match_reason`, `doc_id`, `grounding_score`, `gs://`, `firebasestorage`, `192.168.`, or email patterns (`[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+`).
  ```
- **Verbatim Citation from [`INBOX/NET-747_inputs/entries_master_20261103.jsonl:1250`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl#L1250) & [`3082`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl#L3082) (Representative of 12 `fold_source == "seed_images"` rows with album titles in `name` / `series`):**
  ```json
  "nac_code": "NAC1.CN.US.1C.THEWORLDWA.1942.S.BASE.1", "type": "coin", "name": "1942-S The World War II U.S. Coin Collection 1 cent", "series": "The World War II U.S. Coin Collection"
  "nac_code": "NAC1.CN.US.1D.THEULTIMAT.2023.XX.PEACE.B", "type": "coin", "name": "2023 The Ultimate Modern Morgan and Peace Silver Dollar Collection", "series": "The Ultimate Modern Morgan and Peace Silver Dollar Collection"
  ```
- **Why Check #2 Fails (`MF-v3-C`):**
  1. **`v3` line 158 does NOT scan for plain `"collection"` or plain `"derived"`:**
     - As `BATON_NET-754` line 10 suspected, `v3` line 158 only scans for hyphenated `"collection-derived"` and `"collection-seed"`.
     - Consequently, `v3`'s scanner completely misses:
       - `"collection photo, owner removed"` (`1,070` total occurrences in `entries_master_20261103.jsonl`: `966` in `type_image.source`, `23` in `secondary_image.source`, `81` in `primary_image.source`, of which `989` are in `v3`'s allow-list!). Note: `"owner"` in `"owner removed"` would catch those if `source` were left in, ONLY because `"owner"` happens to be in the regex, not because `"collection"` is caught!
       - `"COLLECTION_DERIVED"` (`1,724` occurrences in `figures.composition.status` with an underscore instead of a hyphen!).
       - **12 `fold_source == "seed_images"` rows** where `name` and `series` contain third-party subscription album names from the seed collection (`"The U.S. Nickel Collection"` [Row 1996], `"The World War II U.S. Coin Collection"` [Rows 1250, 1251, 1252, 1659, 1920], `"Modern Morgan and Peace Silver Dollar Collection"` [Row 3081], `"The Ultimate Modern Morgan and Peace Silver Dollar Collection"` [Rows 3082, 3084, 3085, 3086], `"Celebrating America Coin Collection"` [Row 3123]). None of those 5 strings are official U.S. Mint series names—they are PCS Stamps & Coins / Littleton / Bradford Exchange collector album titles from the seed photos!
  2. **Required Fix for `v4` (`MF-v3-C`):**
     - `pii_gate_validator.py` MUST scan **case-insensitively (`re.IGNORECASE`)** for plain **`collection`** and plain **`derived`** (in addition to `seed`, `eric`, `owner`, `vault`, etc.).
     - Before running the gate scan on `catalog_public_v1.json`, the validator may strip only an explicit, exact museum-provenance allow-list:
       1. `"National Numismatic Collection"` (159 `primary_image.credit`, 11 `extra_images[].credit`, 6 `history` strings)
       2. `"Josiah K. Lilly Jr. Collection"` (Row 1049 `series`, Smithsonian NNC provenance)
       3. `"herbarium collection"` (Row 3106 `history` text about botanist Jane Colden's 18th-century flora portfolio)
       4. Museum URL paths: `metmuseum.org/art/collection/`, `numismatics.org/collectionimages/`, `si.edu/collection/`
     - **Any other match of `"collection"` or `"derived"` or `"seed"` anywhere in `catalog_public_v1.json` MUST fail the build (`exit code 1`).**
     - For the 12 `fold_source == "seed_images"` rows with collector-album names in `name`/`series` (`THEWORLDWA`, `THEUSNICKE`, `MODERNMORG`, `THEULTIMAT`, `CELEBRATIN`), normalize their `name`/`series` in the build script to standard numismatic names/series (or replace `"Collection"` with `"Series"` / `"Issue"` in `name` and `series`) so zero collector-album titles leak into the public catalog.

---

### Check #3: Correct Counts (`3,202` Total = `2,965` Coins + `181` Notes + `56` Medals; `4` Sourced Mintages vs `3,198` `"Needs source"`; `951` Placeholders)

- **Status:** **PASS (`100%` Verified Against `entries_master_20261103.jsonl`)**
- **Verbatim Citation from [`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md:82-88`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md#L82-L88):**
  ```markdown
  | Category | Exact Count | Filter / Condition in `entries_master_20261103.jsonl` |
  | :--- | :--- | :--- |
  | **Total Records** | **3,202** | All rows in `entries_master_20261103.jsonl` |
  | **U.S. Coins** | **2,965** | `type == "coin"` (includes **9** Pre-Federal items where `pre_federal == true`) |
  | **Paper Money (Notes)** | **181** | `type == "note"` |
  | **Medals & Tokens** | **56** | `type == "medal"` |
  | **Sourced Mintages** | **4** | `figures.mintage.value != null` (`1796 Draped Bust cent: 974,700`, `1820 Capped Bust: 27,550`, `1854 Indian head Ty2: 14,632`, `1925 5 Cents: 3,000,000`) |
  | **Unsourced Mintages** | **3,198** | `figures.mintage.value == null` → Rendered as `"Needs source"` |
  | **Placeholders ("Details coming")** | **951** | `display_label == "details coming"` → Rendered with `"Details coming"` badge |
  ```
- **Bonus Data-Quality Note (`N-v3-1` — Non-Blocking Flag for Catalog Research / AG CoS):**
  When inspecting the 4 rows where `figures.mintage.status == "SUPPORTED"` in `entries_master_20261103.jsonl`, we noticed that two of the four (`from_file: "EXTRACT_retry.json"`) matched the wrong coin in the Mint Annual Report PDF:
  - Row 1022 (`NAC1.CN.US.5CENTS.X.1925.XX.BASE.8`, `5 Cents, United States, 1925`):
    ```json
    "mintage": {"value": 3000000, "unit": "pieces", "source_url": "https://fraser.stlouisfed.org/files/docs/publications/usmint/usmint_1925_annual-report.pdf#page=11", "doc_id": "lptext-fraser-mint-ar-lp-1925-p011", "grounding_score": 0.928, "status": "SUPPORTED", "claim": "* **San Salvador, 5 centavos, nickel:** 3,000,000 pieces", "from_file": "EXTRACT_retry.json", "replaced": null}
    ```
    *(That 3,000,000 mintage is foreign coinage struck by the U.S. Mint for El Salvador (`5 centavos`), not the 1925 U.S. Buffalo Nickel (`35,565,100`)!)*
  - Row 223 (`NAC1.CN.US.GD1.INDIANHEAD.1854.XX.TY2.1`, `1854 Indian head (Ty2)`):
    ```json
    "mintage": {"value": 14632, "unit": "pieces", "source_url": "https://fraser.stlouisfed.org/files/docs/publications/usmint/usmint_1864_annual-report.pdf#page=23", "doc_id": "lptext-fraser-mint-ar-lp-1864-p023", "grounding_score": 0.951, "status": "SUPPORTED", "claim": "* At the **San Francisco Branch Mint**, a total of **14,632** gold dollar pieces were coined in the year 1854.", "from_file": "EXTRACT_retry.json", "replaced": null}
    ```
    *(14,632 is the 1854-S Type 1 gold dollar mintage, whereas `1854.XX.TY2` is Philadelphia Type 2.)*
  - Recommendation (`N-v3-1`): Flag rows 223 and 1022 for Catalog Research review (or revert those two mismatched `EXTRACT_retry.json` mintages to `"Needs source"` so the public catalog doesn't show El Salvador's mintage on a 1925 U.S. 5-cent piece).

---

### Check #4: Newest Entries — Honest File-Date Disclosure (`3 Nov 2026`) + Seed Exclusion (`fold_source == "seed_images"` Excluded)

- **Status:** **PASS**
- **Verbatim Citation from [`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md:172-175`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md#L172-L175) & [`189`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md#L189):**
  ```markdown
  3. **Newest Entries Rail (`NewestEntriesRail`)**:
     - **Filter Rule**: Displays only non-interleaved Catalog Research records (`is_interleaved_checklist_only == false`, which excludes all 2,612 `fold_source == "seed_images"` items at build time so zero seed items ever appear in Newest Entries).
     - **Timestamp Disclosure**: Because `created_at` and `date_added` do not exist in `entries_master_20261103.jsonl`, records use the Catalog Research file date (`2026-11-03`).
     - **UI Disclosure Note**: Renders a visible subtitle directly beneath the rail header: *"Entries sorted by Catalog Research file date (3 Nov 2026)."*
  ```
  ```markdown
     - `Newest First` (sorts by Catalog Research file date `3 Nov 2026`, prioritizing non-interleaved records with verified primary imagery; displays visible note: *"Entries sorted by Catalog Research file date (3 Nov 2026)"*)
  ```

---

### Check #5: Ask Morgan Button — Filled Navy Button (`#0B2545`, White Text, `2px solid #0B2545`, `36x36` Owl Icon)

- **Status:** **PASS**
- **Verbatim Citation from [`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md:208`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md#L208) & [`256`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md#L256):**
  ```markdown
  - **"Ask Morgan" Primary Action Button**: Styled as a prominent **filled navy button (`background: #0B2545`, `color: #FFFFFF`, `border: 2px solid #0B2545`)** with the `36x36` Morgan owl icon, opening the Morgan chat panel pre-seeded with the active `nac_code` and `name`.
  ```
  ```markdown
  - **Filled Navy "Ask Morgan" Button (`#0B2545` background, `#FFFFFF` text, `2px solid #0B2545` border, `36x36` owl icon)**: Placed at the top of the action bar and inside the Specifications section.
  ```

---

### Check #6: Firestore Rules Guard + Preview-Only Deploy Gate (`p7v12` Only)

- **Status:** **PASS**
- **Verbatim Citation from [`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md:70-71`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md#L70-L71) & [`359-360`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Grok%20CoS%20to%20Antigravity/INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v3.md#L359-L360):**
  ```markdown
  - **Firestore Rules & Writes Guard**: **NO `firestore.rules` deploy and NO Firestore writes without Founder Eric's separate typed YES.** During preview (`p7v12`), `Flag / Suggest Correction` submissions validate locally in-memory with a zero-PII math/honeypot captcha and display a preview confirmation toast without writing to production Firestore unless Eric explicitly approves Firestore rules deployment.
  - **Preview-Only Deploy Gate**: Phase 3 deployment targets **ONLY Firebase Hosting preview channel `p7v12`**. Production (`main` / `numista-vault.web.app`) remains untouched at `9f04550a`.
  ```

---

## 3. Summary Checklist of Required Fixes for `v4` (3 Surgical Edits in Section 3.1 & Section 3.2)

| ID | Location in `v3` | Exact Surgical Change Required in `v4` |
| :--- | :--- | :--- |
| **`MF-v3-A`** | Section 3.1 (lines 23–24, 131–133) | 1. **Remove `source` (and `status`)** from the permitted sub-fields of `type_image`, `secondary_image`, and `primary_image` (eliminating all 1,070 occurrences of `"source": "collection photo, owner removed"`).<br>2. **Add `file`** (or map `file` -> public GCS CDN `url`) to `primary_image` permitted sub-fields so the 81 exact-year seed `primary_image` objects do not lose their image path. |
| **`MF-v3-B`** | Section 3.1 & 3.2 (lines 29, 138, 151–153) | 1. Define the permitted sub-fields inside each `figures.<metric>` object as `{value, unit, label, source_url}` (explicitly stripping `status`, `claim`, `doc_id`, `from_file`, `grounding_score`, `method`, `replaced`).<br>2. Explicitly scrub `figures.composition` (`1,724` rows where `status == "COLLECTION_DERIVED"` and `label == "collection-derived, needs primary source"`): either normalize `label` to `"Needs source"` (or map `COLLECTION_DERIVED` entries to `value: null, label: "Needs source"`). |
| **`MF-v3-C`** | Section 3.2 (lines 154, 158) | 1. Add case-insensitive plain **`collection`** and plain **`derived`** to `pii_gate_validator.py`'s fail-on-hit regex list (after allowing only the exact museum strings `"National Numismatic Collection"`, `"Josiah K. Lilly Jr. Collection"`, `"herbarium collection"`, and museum URLs `metmuseum.org/art/collection/`, `numismatics.org/collectionimages/`, `si.edu/collection/`).<br>2. Remove the `v3` line 154 exemption for `"The U.S. Nickel Collection"` and normalize the **12 `fold_source == "seed_images"` rows** whose `name`/`series` contain third-party collector-album titles (`THEWORLDWA`, `THEUSNICKE`, `MODERNMORG`, `THEULTIMAT`, `CELEBRATIN`) so zero `"Collection"` album names leak into `catalog_public_v1.json`. |
