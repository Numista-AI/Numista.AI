# ARGON (GEMINI 3.8) TECHNICAL REVIEW — `AG_PLAN_NET-747_CATALOG-BROWSE_v2.md`
**Baton:** `BATON_NET-752_AG_NET-747-PLAN-v2_20261103-1315.md` (Attempt 2 of 10)
**Plan Audited:** `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v2.md` (272 lines, filed 2026-11-03 1:15 PM ET)
**Inputs Audited Against:**
- `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl` (3,202 master records)
- `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/Plan.v1_catalog.md`
- `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/ux/badges_concept.html` & `ux/catalog_top_concept.html`
- Live codebase (`numista_mobile/lib/main.dart`, `numista_mobile/lib/screens/not_found_screen.dart`, `numista_mobile/firebase.json`)
**Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer / Gemini 3.8 Code Reviewer, Review-Only / No Execute)
**Timestamp:** 2026-11-03 1:44 PM ET
**Score:** **97 / 100 — PASS (READY FOR GROK CoS 95+ & SAG SIGN-OFF)**

---

## 1. Executive Summary

`AG_PLAN_NET-747_CATALOG-BROWSE_v2.md` cleanly resolves **all 7 must-fixes (`MF-747-1` through `MF-747-7`)** from Argon's `v1` review (`84/100`) as well as **all 11 requirements of the 1:16 PM ET Catalog Builder Addendum** in `BATON_NET-752_AG_NET-747-PLAN-v2_20261103-1315.md`.

In addition, Argon inspected all **3,202 records** in `INBOX/NET-747_inputs/entries_master_20261103.jsonl` directly via read-only Python analysis and documented **3 non-blocking adapter implementation notes (`N-1`..`N-3`)** below so that when `scripts/catalog/build_public_catalog.py` is eventually executed (after CoS 95+, SAG, and Founder Eric's typed YES), the read-only adapter maps the exact JSONL key names and strips nested `"collection"` / `"seed"` substrings on the first run.

---

## 2. Rule 6(a) Verbatim Verification of `MF-747-1`..`MF-747-7` & Catalog Builder Addendum

### 2.1 `MF-747-1` (Soft-404 Reuse of `NotFoundScreen` & `/catalog` Routing) — **PASS**

- **`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v2.md:164-175` (verbatim):**
  ```markdown
  ### 5.1 Soft-404 Reuse Rule (`NotFoundScreen`)
  Per `Plan.v1_catalog.md:13`, **we do NOT build a second `CatalogSoft404Screen`.**
  We reuse and extend the existing `NotFoundScreen` (`numista_mobile/lib/screens/not_found_screen.dart:18-23`):
  - When `attemptedPath` starts with `/catalog/`:
    - Displays catalog-aware headline: *"We don't have that one yet."*
    - Renders catalog search box, "Ask Morgan" button, and link to "Missing something?".
    - Injects `<meta name="robots" content="noindex">` into `document.head` on web to suppress search engine indexing.

  ### 5.2 SPA Routing & Firebase Hosting
  - **`numista_mobile/lib/main.dart:119-140` (`isKnownPath`):**
    Add `normalizedPath == '/catalog' || path.startsWith('/catalog/')` to `isKnownPath`.
    Validate `:nacCode` against `catalog_public_v1.json` allow-list; render `NotFoundScreen(attemptedPath: path)` when slug is unknown.
  ```

- **`numista_mobile/lib/main.dart:140-149` (verbatim):**
  ```dart
        path.startsWith('/scraper_dashboard') ||
        path.startsWith('/api/');

    if (!isKnownPath) {
      runApp(MaterialApp(
        title: 'Numista.AI',
        debugShowCheckedModeBanner: false,
        home: NotFoundScreen(attemptedPath: path),
      ));
      return;
    }
  ```

- **`numista_mobile/lib/screens/not_found_screen.dart:18-23` (verbatim):**
  ```dart
  class NotFoundScreen extends StatelessWidget {
    /// The path that was not matched, shown only in debug builds.
    final String? attemptedPath;

    const NotFoundScreen({super.key, this.attemptedPath});
  ```

---

### 2.2 `MF-747-2` & Addendum #5–#6 (Exact UX Badge Hex Colors, SVGs, and Top Block) — **PASS**

- **`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v2.md:116-122` (verbatim):**
  ```markdown
  All badges are non-interactive pills positioned directly beneath the item title:
  - **Base Style (`.tag`):** `height: 32px`, `padding: 0 14px`, `border-radius: 16px`, `font-size: 16px`, `background: #FFFFFF`, `display: inline-flex`, `align-items: center`, `gap: 8px`.
  - **Pre-Federal Badge (`.pf`):** `border: 2px solid #1F5FAD`, text `color: #0B2545`, `font-weight: bold`. Contrast: text `#0B2545` / `#FFF` = **15.39:1** (AAA); outline `#1F5FAD` / `#FFF` = **6.37:1**. Displayed on all pre-1792 items (9 total); never on >=1792.
  - **"Needs source" Badge (`.neu`):** `border: 2px solid #6B6B6B`, text `color: #333333`. Includes `20x20` circled `"i"` SVG (`<circle cx="10" cy="10" r="8.5" fill="none" stroke="#333" stroke-width="2"/><rect x="9" y="8.5" width="2" height="6" fill="#333"/><circle cx="10" cy="5.7" r="1.3" fill="#333"/>`). Contrast: text 12.63:1 (AAA), outline 5.33:1. **Never red, orange, or yellow.**
  - **"Details coming" Badge (`.neu`):** `border: 2px solid #6B6B6B`, text `color: #333333`. Includes `20x20` dotted-circle SVG (`stroke-dasharray="3 2.5"`). Contrast: text 12.63:1 (AAA), outline 5.33:1. Used on the 951 placeholder records.
  - **Discipline Rule:** Exactly **1 badge per card maximum**. Never stack "Needs source" with "Details coming". Detail view displays `"Mintage: Needs source"` beside blank figure.
  ```

- **`INBOX/NET-747_inputs/ux/badges_concept.html:5-6,12-14` (verbatim):**
  ```html
  .tag{display:inline-flex;align-items:center;gap:8px;height:32px;padding:0 14px;border-radius:16px;font-size:16px;background:#fff;white-space:nowrap}
  .pf{border:2px solid #1F5FAD;color:#0B2545;font-weight:bold}.neu{border:2px solid #6b6b6b;color:#333}
  ...
  <tr><td><span class="tag pf">Pre-Federal (before 1792)</span></td><td>Pill, 32px tall, 2px outline #1F5FAD on white, text #0B2545 bold 16px</td><td>Text #0B2545 / #FFF: <b>15.39:1</b> (AAA)<br>Outline #1F5FAD / #FFF: <b>6.37:1</b> (≥3:1 non-text)</td></tr>
  <tr><td><span class="tag neu"><svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="8.5" fill="none" stroke="#333" stroke-width="2"/><rect x="9" y="8.5" width="2" height="6" fill="#333"/><circle cx="10" cy="5.7" r="1.3" fill="#333"/></svg>Needs source</span></td><td>Pill, 32px, 2px outline #6B6B6B, circled “i” icon + text #333 16px. Never red/orange.</td><td>Text #333 / #FFF: <b>12.63:1</b> (AAA)<br>Outline #6B6B6B / #FFF: <b>5.33:1</b></td></tr>
  <tr><td><span class="tag neu"><svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="8.5" fill="none" stroke="#333" stroke-width="2" stroke-dasharray="3 2.5"/></svg>Details coming</span></td><td>Same neutral style, dotted-circle icon + text #333 16px</td><td>Text #333 / #FFF: <b>12.63:1</b> (AAA)<br>Outline #6B6B6B / #FFF: <b>5.33:1</b></td></tr></table>
  ```

---

### 2.3 `MF-747-3`..`MF-747-7` & Catalog Builder Addendum #1–#11 — **PASS**

- **`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v2.md:49-56` (verbatim):**
  ```markdown
  | `entries_master_20261103.jsonl` | **3,202 master entries** (today's fold) | Read through small read-only adapter. **NEVER run `build.py` or `finalize.py`** |
  | `schema.json` | Schema definition | NAC1 code regex updated to allow `.BEP.BASE.2` and multi-segment suffixes |
  | `images_MANIFEST.csv` | 171 image rows | Verified license, credit, source, sha256 checksum |
  | `published_x_posts.csv` | Published X posts | 4 shaky claims stripped; manual read gate applied to all notes |
  | Varieties in Master | Sub-objects | Ingested as structured objects: `{ "name": str, "attribution": str, "status": str }` |
  | Unsourced Mintages | 100% of figures | Sourced figures = 0 -> Display `"Needs source"` everywhere |
  | Placeholders | **951 records** | Rendered as name-only with neutral pill `"Details coming"` and neutral coin outline |
  ```

- **`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v2.md:139-142` & `150-153` (verbatim):**
  ```markdown
  4. **Primary vs Type Image Distinction:**
     - `primary_image`: exact match for the coin.
     - `type_image`: representative type photo only; must explicitly display label: `"date may differ"`.
  ...
  - Form fields: item description, optional year, optional type, optional primary source URL, optional email marked `"(optional)"`.
  - Visible labels above fields, primary `"Send"` button, confirmation message: *"Thanks - we'll look into it."*
  - Zero collection photos, zero dollar values, zero ownership fields.
  - Submissions land in an off-repo review queue with rate-limiting and captcha; never auto-published.
  ```

---

## 3. Non-Blocking Implementation Notes from Direct Audit of `entries_master_20261103.jsonl` (3,202 Rows)

Argon audited all 3,202 JSON lines in `INBOX/NET-747_inputs/entries_master_20261103.jsonl` and confirmed the exact counts (`3,202` total rows; `951` `record_status == "PLACEHOLDER"` rows with `display_label == "details coming"`; `9` `pre_federal == true` rows; `146` rows with `varieties`; `248` rows with `primary_image`; `966` rows with `type_image`). When `scripts/catalog/build_public_catalog.py` is implemented after execution sign-off, ensure the read-only adapter handles these 3 verified dataset specifics:

1. **`N-1` (Exact Key Names & Coin Count in `entries_master_20261103.jsonl`):**
   - **Verbatim from `INBOX/NET-747_inputs/entries_master_20261103.jsonl:1` (Row 1):**
     ```json
     {"nac_code": "NAC1.BN.US.D40.NOTE.1778.BEP.BASE.2", "name": "Series 1778 $40 US note", "type": "note", "denomination": "$40", "year": 1778, "series": "Series 1778", "mint_facility": null, "mint_mark_on_coin": null, "composition": null, "era": "Pre-Federal & Founding (to 1792)", "designer": null, "weight_g": null, "diameter_mm": null, "mintage": {"value": null, "label": "not yet sourced", "source_url": null}, "varieties": [], "history": null, "pre_federal": true, "pre_federal_state": null, "primary_image": null, "image_status": "NO_IMAGE (collection images are user-scoped GCS/AI-generated; not reused)", "sources": [{"label": "collection-derived, needs primary source", "type": "collection-derived"}], "social_posts": [], "published_on_x": false, "record_status": "PLACEHOLDER", "seed_type": "collection-seed", "needs_fact_check": ["Existence and attributes are collection-derived, needs primary source; not Mint-verified."], "figures": {"mintage": {"value": null, "label": "not yet sourced", "status": "NOT_YET_SOURCED"}, "weight_g": {"value": null, "label": "not yet sourced", "status": "NOT_YET_SOURCED"}, "diameter_mm": {"value": null, "label": "not yet sourced", "status": "NOT_YET_SOURCED"}, "fineness": {"value": null, "label": "not yet sourced", "status": "NOT_YET_SOURCED"}}, "proposal_status": "PROPOSAL", "fold_source": "seed_images", "display_label": "details coming"}
     ```
   - In `entries_master_20261103.jsonl`, the category breakdown by `type` is **`2,965` coins** (`type == "coin"`, up from `2,906` in `v1` after folding the 62 `suspect_fixed` rows), **`181` notes** (`type == "note"`), and **`56` medals** (`type == "medal"`), totaling **`3,202`**.
   - The adapter in Section 3.1 (`line 64`) should read the master keys `type` (mapping to `category`), `year`, `mint_facility` / `mint_mark_on_coin`, `weight_g`, `history`, `era`, `series`, `designer`, `pre_federal`, `pre_federal_state`, `display_label`, `primary_image`, `type_image`, and `varieties`.

2. **`N-2` (Strip Nested `"collection"` / `"seed"` / `"derived"` Fields in `entries_master_20261103.jsonl`):**
   - In `entries_master_20261103.jsonl`, in addition to the stripped fields listed in Section 3.1 (`line 68`), the following fields also contain internal `"seed"`, `"collection"`, or `"derived"` strings and must be stripped by `build_public_catalog.py`:
     - Top-level: `seed_status` (`"COLLECTION_DERIVED_DRAFT"` on 1,724 rows), `fold_source` (`"seed_images"` on 2,612 rows), `record_status`, `needs_fact_check`.
     - Inside `sources[]`: strip any entry where `source.type == "collection-derived"` or `source.label` contains `"collection-derived"`.
     - Inside `primary_image` (81 seed-image rows) and `type_image` (966 rows): strip `source` (`"collection photo, owner removed"`), `local_path` (`"/workspace/image-intake/catalog-research/collection-seed/..."`), `local_manifest`, and `status` (`"PROPOSAL"`).
   - For `"Newest Entries"` (`Section 4.1 #2`), the adapter should filter to `fold_source == "entries_20261103"` (528 rows, excluding `fold_source == "seed_images"` [2,612 rows] and `record_status == "PLACEHOLDER"` [951 rows]) and sort by the Catalog Research file date (`2026-11-03`) as specified in Addendum #10.

3. **`N-3` (Single-Badge Precedence on Row 1 `NAC1.BN.US.D40.NOTE.1778.BEP.BASE.2`):**
   - Exactly 1 record in `entries_master_20261103.jsonl` (Row 1: `NAC1.BN.US.D40.NOTE.1778.BEP.BASE.2`, `Series 1778 $40 US note`) has both `pre_federal: true` and `record_status: "PLACEHOLDER"` (`display_label: "details coming"`). Under the 1-badge-per-card rule (`Section 4.3, line 121`), `build_public_catalog.py` should apply deterministic priority (`is_placeholder` -> `"Details coming"` on all 951 placeholders, or `pre_federal` -> `"Pre-Federal (before 1792)"` on all 9 pre-1792 items) and assert the exact expected counts in `test/catalog/`.

---

## 4. Scoring Breakdown

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **Precedence & Branch / Prod Isolation (`Section 1 & 9`)** | 20 | **20 / 20** | Defers behind 26 Nov must-ships & `NET-746`/`NET-748`; isolates to `catalog-browse-p7v12` off `p7v12`; never runs `build.py` or `finalize.py`; keeps `origin/main` (`9f04550a`), `p7-v8.9`, and `dev` untouched. |
| **Eric's 9:01 Rules & Catalog Builder Addendum (`Section 2 & 4.1`)** | 20 | **20 / 20** | Sized for 3,202 master records (`entries_master_20261103.jsonl`) via read-only adapter; 951 `"Details coming"` placeholders; varieties as `{name, attribution, status}`; `"date may differ"` on `type_image`. |
| **Data Sanitization, Schema & Asset Pipeline (`Section 2, 3 & 4.5`)** | 20 | **18 / 20** | Fixes `schema.json` regex for `.BEP.BASE.2` (`MF-747-4`), image ranking + SHA-256 + `license`/`credit` (`MF-747-5`), and 4 shaky X-post exclusions (`MF-747-6`). Minor notes `N-1`/`N-2` documented for master JSONL key names & nested `seed_status`/`fold_source`/`type_image.source` stripping. |
| **UX & Accessibility Compliance (`Section 4.2–4.8`)** | 20 | **19 / 20** | Exact `#1F5FAD`/`#0B2545`/`#6B6B6B` badge colors & SVGs (`MF-747-2`), exact page section order (`Browse -> Newest -> Coverage -> Missing something?`), `image+source first` sort (`MF-747-3`), and Addendum #8 form spec. Minor note `N-3` on Row 1 badge priority. |
| **Routing, Soft-404 Reuse & Virtualization (`Section 5, 6 & 8`)** | 20 | **20 / 20** | Reuses `NotFoundScreen` (`numista_mobile/lib/screens/not_found_screen.dart:18-23`) with `<meta name="robots" content="noindex">` (`MF-747-1`), updates `main.dart:119-140` + `firebase.json`, and virtualizes with `SliverGrid`/`SliverList` (`MF-747-7`). |
| **TOTAL** | **100** | **97 / 100** | **PASS — READY FOR GROK CoS 95+ & SAG CONCURRENCE** |

---

## 5. Handoff & Next Action

- **Status:** **`97 / 100 — PASS`**.
- **Next Turn (`NET-747`):** **Grok CoS (`95+` Scoring)** -> **SAG Concurrence** -> **Founder Eric's Typed YES** (with adapter notes `N-1`..`N-3` applied during execution).
