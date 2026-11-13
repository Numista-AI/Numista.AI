# ARGON (GEMINI 3.8) TECHNICAL REVIEW — `AG_PLAN_NET-747_CATALOG-BROWSE_v1.md`
**Baton:** `BATON_NET-747_AG_CATALOG-BROWSE-PLAN-ONLY_20261103.md`
**Plan Audited:** `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v1.md` (189 lines, filed 2026-11-03 12:47 PM ET)
**Reference Pack Audited Against:** `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/CATALOG_PLAN_v1_pack.zip` (`Plan.v1_catalog.md`, `ux/catalog_top_concept.html`, `ux/badges_concept.html`) + live codebase (`numista_mobile/lib/main.dart`, `numista_mobile/lib/screens/not_found_screen.dart`, `numista_mobile/firebase.json`)
**Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer / Gemini 3.8 Code Reviewer, Review-Only / No Execute)
**Timestamp:** 2026-11-03 12:58 PM ET
**Score:** **84 / 100 — REVISE TO `v2` BEFORE CoS 95+ / SAG SIGN-OFF**

---

## 1. Executive Summary

`AG_PLAN_NET-747_CATALOG-BROWSE_v1.md` properly enforces **precedence** (deferring behind the five 26 Nov must-ships and `NET-746`/`NET-748`), **branch isolation** (`catalog-browse-p7v12` off `p7v12`, keeping `origin/main` at `9f04550a`, `p7-v8.9`, and `dev` untouched), and **Eric's three binding decisions** from `Plan.v1_catalog.md` (interleaving 2000–2026 seed entries into the chronological checklist while excluding them from `"Newest Entries"`, rendering the 888 placeholders as name-only with `"Details coming"` without stacking badges, and stripping all internal `"seed"`, `"collection"`, and `"derived"` tokens).

However, cross-checking `AG_PLAN_NET-747_CATALOG-BROWSE_v1.md` against `Plan.v1_catalog.md`, `ux/badges_concept.html`, `ux/catalog_top_concept.html`, `numista_mobile/lib/main.dart`, `numista_mobile/lib/screens/not_found_screen.dart`, and `numista_mobile/firebase.json` surfaced **7 specific technical and specification gaps (`MF-747-1` through `MF-747-7`)** that must be corrected in `v2` before CoS 95+ and SAG sign-off:

1. **`MF-747-1` (Blocker — Violates `Plan.v1_catalog.md` Soft-404 Reuse Rule & Misstates Firebase Hosting Rewrite Behavior):** `AG_PLAN_NET-747_CATALOG-BROWSE_v1.md:155-156` proposes building a brand-new `CatalogSoft404Screen` and claims it will return *"genuine HTTP 404 header status via Firebase hosting rewrites."* That directly violates `Plan.v1_catalog.md:13` (*"The catalog soft-404 (Step 9) reuses the site soft-404 from the must-ship list. It doesn't build a second one."*) AND is technically impossible via static Firebase Hosting `rewrites` to `/index.html` (which always return HTTP 200). Furthermore, `numista_mobile/lib/main.dart:119-140` (`isKnownPath`) and `numista_mobile/firebase.json:49-133` do not yet include `/catalog` or `/catalog/**`.
2. **`MF-747-2` (Major — Badge Hex Colors & Icon Spec Mismatch vs Signed-Off `ux/badges_concept.html`):** `AG_PLAN_NET-747_CATALOG-BROWSE_v1.md:86` specifies `#1B365D` for the Pre-Federal pill and omits the outline/icon specs for the neutral pills, whereas `ux/badges_concept.html:6,12-14` explicitly locks `.pf{border:2px solid #1F5FAD;color:#0B2545;font-weight:bold}` (15.39:1 AAA text, 6.37:1 outline) and `.neu{border:2px solid #6b6b6b;color:#333}` with a circled `"i"` SVG on `"Needs source"` and a dotted-circle SVG (`stroke-dasharray="3 2.5"`) on `"Details coming"`.
3. **`MF-747-3` (Major — Missing Section Order & `"Newest Entries"` Component in Phase 1/2 Deliverable):** `Plan.v1_catalog.md:155` locks the page section order to `Top block -> In-progress line -> 1. Browse -> 2. Newest entries -> 3. Coverage by year -> 4. Missing something?`, and `Plan.v1_catalog.md:160` locks internal list sorting to **image + source first** so pages never lead with blank `"Needs source"` cards. `AG_PLAN_NET-747_CATALOG-BROWSE_v1.md:117-129` and `145-152` omit `"Newest Entries"` from the architecture diagram and widget list, and omit the `image + source first` list sort rule.
4. **`MF-747-4` (Major — Omitted `schema.json` NAC Code Regex Bug for Seed Codes):** `Plan.v1_catalog.md:135` explicitly warns: *"The NAC code pattern in `schema.json` doesn't match seed codes like `...BEP.BASE.2`. Validate both files and fix the schema before building URLs."* `AG_PLAN_NET-747_CATALOG-BROWSE_v1.md` omits this prerequisite schema fix.
5. **`MF-747-5` (Major — Omitted Image Ranking, `images_MANIFEST.csv` SHA-256 Verification, and Mandatory `license` + `credit` Attribution):** `Plan.v1_catalog.md:57-61,113,131` requires ranking images in order (`1. Museum first: NNC/Smithsonian, ANS, Met, BnF -> 2. Public domain: Wikimedia and others -> 3. Verified uploads`), verifying `sha256` against `images_MANIFEST.csv`, and displaying `license` and `credit` on every photo. `AG_PLAN_NET-747_CATALOG-BROWSE_v1.md` mentions `images_MANIFEST.csv` (171 images) in Section 1 (`line 33`), but omits image ranking, SHA-256 verification, and `license`+`credit` rendering from the pipeline and UI specs.
6. **`MF-747-6` (Moderate — Omitted the 4 Specific Shaky X-Post Claim Exclusions & Manual Read Gate):** `Plan.v1_catalog.md:71,86,145` explicitly mandates stripping/excluding 4 known shaky claims from `published_x_posts.csv` / `social_posts` (`Fugio source file`, `Chain cent grounding`, `1793 half-cent "first" claim`, and `1795 $10 placeholder link`) and gating `social_posts` behind a manual read. `AG_PLAN_NET-747_CATALOG-BROWSE_v1.md` omits `published_x_posts.csv` and those 4 explicit exclusions.
7. **`MF-747-7` (Moderate — Allow-List Field Mapping & 3,143-Item Flutter Web Virtualization):** `AG_PLAN_NET-747_CATALOG-BROWSE_v1.md:45` lists `status_badge` as an input allow-list field (whereas `Plan.v1_catalog.md:80-88` defines the exact input allow-list including `figures`—sanitized to `"Needs source"` when `status == "NOT_YET_SOURCED"` or source is `"collection-derived"`—and computes the single public badge from the sanitized state). Additionally, rendering 3,143 entries (2,906 coins) in Flutter Web requires explicit `SliverGrid` / `SliverList` (`SliverChildBuilderDelegate`) or paged virtualization (`Plan.v1_catalog.md:122`) so initial load and scrolling hold 60fps.

---

## 2. Rule 6(a) Verbatim Code & Specification Audit

### 2.1 `MF-747-1`: Soft-404 Reuse (`NotFoundScreen`) & `/catalog` Routing (`main.dart` + `firebase.json`)

- **`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v1.md:154-156` (verbatim):**
  ```markdown
  3. **Routing & Soft-404**:
     - Integrate catalog route `/catalog` and `/catalog/:nacCode`.
     - Implement `CatalogSoft404Screen` returning genuine HTTP 404 header status via Firebase hosting rewrites.
  ```

- **`INBOX/CATALOG_PLAN_v1_pack_extracted/Plan.v1_catalog.md:13` (verbatim):**
  ```markdown
  The catalog soft-404 (Step 9) reuses the site soft-404 from the must-ship list. It doesn't build a second one.
  ```

- **`INBOX/CATALOG_PLAN_v1_pack_extracted/Plan.v1_catalog.md:50` & `134` (verbatim):**
  ```markdown
  9. **Soft-404.** An unknown `/catalog/...` URL gets a friendly page: *"We don't have that one yet."* It offers search, Morgan, and a link to *"Missing something?"*. It returns a real 404 status, so search engines don't index it.
  ...
  - **Soft-404 must be a real 404.** Return HTTP 404 (or `<meta name="robots" content="noindex">` on SPA routes) so Google doesn't index 10,000 *"we don't have this yet"* pages.
  ```

- **`numista_mobile/lib/main.dart:119-149` (verbatim):**
  ```dart
    final isKnownPath = path.isEmpty ||
        path == '/' ||
        path == '/index.html' ||
        normalizedPath == '/about' ||
        normalizedPath == '/pricing' ||
        normalizedPath == '/features' ||
        normalizedPath == '/faq' ||
        normalizedPath == '/login' ||
        normalizedPath == '/signup' ||
        normalizedPath == '/reset-password' ||
        normalizedPath == '/demo' ||
        normalizedPath == '/app' ||
        normalizedPath == '/blog' ||
        path.startsWith('/wishlist') ||
        path.startsWith('/attorney_portal') ||
        path.startsWith('/attorney') ||
        path.startsWith('/claim') || // L5: reserved — falls through to home, not NotFoundScreen
        path.startsWith('/privacy') ||
        path.startsWith('/terms') ||
        path.startsWith('/add_coins') ||
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

- **`numista_mobile/firebase.json:54-65` (verbatim):**
  ```json
        {
          "source": "/",
          "destination": "/index.html"
        },
        {
          "source": "/about",
          "destination": "/index.html"
        },
        {
          "source": "/pricing",
          "destination": "/index.html"
        },
  ```

- **Required Fix (`MF-747-1`):**
  1. **Do NOT create a separate `CatalogSoft404Screen` widget.** Reuse and extend `NotFoundScreen` (`numista_mobile/lib/screens/not_found_screen.dart:18-23`) so that when `attemptedPath` starts with `/catalog/` (an unknown NAC slug), `NotFoundScreen` displays the catalog-aware copy (*"We don't have that one yet."*), the catalog search box, the `"Ask Morgan"` button, and the `"Missing something?"` link, AND injects `<meta name="robots" content="noindex">` into `document.head` on web (`Plan.v1_catalog.md:134`).
  2. **Specify exact `firebase.json` + `main.dart` routing:**
     - Add `normalizedPath == '/catalog' || path.startsWith('/catalog/')` to `isKnownPath` in `numista_mobile/lib/main.dart:119-140`, and validate `:nacCode` against the loaded `catalog_public.json` index—rendering `NotFoundScreen(attemptedPath: path)` when `:nacCode` is not in the 3,143-entry allow-list.
     - In `numista_mobile/firebase.json:54-133`, add `/catalog` and `/catalog/**` rewrites (or pre-generated static paths / Cloud Run handler if returning HTTP 404 header at the edge so unknown paths fall through to Firebase Hosting's `404.html` HTTP 404 response + SPA `<meta name="robots" content="noindex">`).

---

### 2.2 `MF-747-2`: Exact UX Badge Hex Colors & SVG Icons (`ux/badges_concept.html` & `ux/catalog_top_concept.html`)

- **`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v1.md:85-88` (verbatim):**
  ```markdown
  - **1-Badge-Per-Card Rule & Color Discipline**:
    - `"Pre-Federal (before 1792)"`: 32px pill, 2px solid navy outline (`#1B365D`), bold 16px text.
    - `"Needs source"`: 32px neutral pill, circled `"i"` icon, `#333333` text on light neutral background. **Never red, orange, or yellow.**
    - `"Details coming"`: 32px neutral pill for placeholder entries.
  ```

- **`INBOX/CATALOG_PLAN_v1_pack_extracted/ux/badges_concept.html:5-6` & `12-14` (verbatim):**
  ```html
  .tag{display:inline-flex;align-items:center;gap:8px;height:32px;padding:0 14px;border-radius:16px;font-size:16px;background:#fff;white-space:nowrap}
  .pf{border:2px solid #1F5FAD;color:#0B2545;font-weight:bold}.neu{border:2px solid #6b6b6b;color:#333}
  ...
  <tr><td><span class="tag pf">Pre-Federal (before 1792)</span></td><td>Pill, 32px tall, 2px outline #1F5FAD on white, text #0B2545 bold 16px</td><td>Text #0B2545 / #FFF: <b>15.39:1</b> (AAA)<br>Outline #1F5FAD / #FFF: <b>6.37:1</b> (≥3:1 non-text)</td></tr>
  <tr><td><span class="tag neu"><svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="8.5" fill="none" stroke="#333" stroke-width="2"/><rect x="9" y="8.5" width="2" height="6" fill="#333"/><circle cx="10" cy="5.7" r="1.3" fill="#333"/></svg>Needs source</span></td><td>Pill, 32px, 2px outline #6B6B6B, circled “i” icon + text #333 16px. Never red/orange.</td><td>Text #333 / #FFF: <b>12.63:1</b> (AAA)<br>Outline #6B6B6B / #FFF: <b>5.33:1</b></td></tr>
  <tr><td><span class="tag neu"><svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="8.5" fill="none" stroke="#333" stroke-width="2" stroke-dasharray="3 2.5"/></svg>Details coming</span></td><td>Same neutral style, dotted-circle icon + text #333 16px</td><td>Text #333 / #FFF: <b>12.63:1</b> (AAA)<br>Outline #6B6B6B / #FFF: <b>5.33:1</b></td></tr></table>
  ```

- **Required Fix (`MF-747-2`):**
  Update Section 3.2 (`lines 85-88`) of `AG_PLAN_NET-747_CATALOG-BROWSE_v1.md` to match the signed-off UX spec sheet verbatim:
  - All tags: `height: 32px`, `padding: 0 14px`, `border-radius: 16px`, `background: #FFFFFF`, `font-size: 16px`, non-interactive label placed directly under the coin name (`ux/badges_concept.html:5,16-17`).
  - `"Pre-Federal (before 1792)"`: `2px solid #1F5FAD` outline on `#FFFFFF`, bold `16px` text `#0B2545` (WCAG `15.39:1` text / `6.37:1` outline).
  - `"Needs source"`: `2px solid #6B6B6B` outline on `#FFFFFF`, `20x20` circled `"i"` icon (`#333333`) + `16px` text `#333333` (WCAG `12.63:1` text / `5.33:1` outline).
  - `"Details coming"`: `2px solid #6B6B6B` outline on `#FFFFFF`, `20x20` dotted-circle icon (`stroke-dasharray: 3 2.5`, `#333333`) + `16px` text `#333333`.
  - Also lock the top block palette from `ux/catalog_top_concept.html:10-24`: `H1` `40px` `#0B2545`; Search input `64px` tall, `2px solid #0B2545`, `22px` font; Primary `"Search"` button `#0B2545` bg / `#FFFFFF` text; Secondary `"Ask Morgan"` button `#FFFFFF` bg / `2px solid #1F5FAD` border / `#0B2545` text + `36x36` owl icon; In-progress note box `#F2F2F2` bg / `1px solid #D6D6D6` border; No-photo placeholder `96x96` circle with `3px dashed #8A8A8A` and `"No photo yet"` (`#333333` `16px`).

---

### 2.3 `MF-747-3`: Page Section Order, `"Newest Entries"` Widget, and `"Image + Source First"` List Sorting

- **`INBOX/CATALOG_PLAN_v1_pack_extracted/Plan.v1_catalog.md:155` & `160` (verbatim):**
  ```markdown
  2. **Order on the page:** Browse → Newest entries → Coverage by year → Missing something?
  ...
  6. **Data rules:** One tag per card. Placeholders show *"Details coming"* only. Inside lists, sort entries with image+source first.
  ```

- **`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v1.md:117-129` & `145-152` (verbatim):**
  ```markdown
      B --> C[Top Block: Morgan Owl + 64px Search + Ask Morgan]
      B --> D[Calm Neutral Banner: Built in Public]
      B --> E[Category Tabs: Coins 2,906 | Notes 181 | Medals 56 | Foreign Coming Later]
      B --> F[Coverage by Year Chart + 'Show as table' Toggle]
      B --> G[Browse Grid / Year-by-Year Checklist]
      B --> H['Missing something?' Submission Link]
  ```

- **Required Fix (`MF-747-3`):**
  1. Fix the page order in Section 4 (`lines 117-129`) and Section 5 (`lines 145-152`) to match `Plan.v1_catalog.md:155` exactly:
     - Top Block (Morgan Owl + 64px Search + Ask Morgan)
     - In-Progress Neutral Note (`"This catalog is being built in public. Some details still need a source."`)
     - **1. Browse** (Category Tabs: `Coins (2,906)` -> `Notes (181)` -> `Medals (56)` -> `Foreign Coins ("Foreign coins are coming later.")`)
     - **2. Newest Entries** (`CatalogNewestEntriesSection` — populated strictly from `entries_20261103.jsonl` and excluding `entries_seed_20261103.jsonl` per Eric's Decision #1)
     - **3. Coverage by Year** (`CatalogCoverageSection` — chart with `"Show as table"` toggle)
     - **4. Missing Something?** (`CatalogMissingSomethingSection` — plain form: entry name, optional link, optional note -> manual review queue, never auto-published per `Plan.v1_catalog.md:48,136`)
  2. Enforce `Plan.v1_catalog.md:160` Rule 6 inside browse lists: default-sort entries with **image + source first** (and provide a clear sort toggle when viewing the chronological year-by-year checklist) so users never land on a wall of blank `"Needs source"` cards first.

---

### 2.4 `MF-747-4`: `schema.json` NAC Code Pattern Validation for Seed Codes (`...BEP.BASE.2`)

- **`INBOX/CATALOG_PLAN_v1_pack_extracted/Plan.v1_catalog.md:135` (verbatim):**
  ```markdown
  - **Schema check.** The NAC code pattern in `schema.json` doesn't match seed codes like `...BEP.BASE.2`. Validate both files and fix the schema before building URLs.
  ```

- **Required Fix (`MF-747-4`):**
  Add an explicit step in Section 2 (`Data Sanitization & Build-Time Allow-List Pipeline`) and Section 5 (`Phase 1`) to update the `nac_code` regex pattern in `schema.json` so that multi-segment seed codes (including `.BEP.BASE.2` and similar suffixes across all 2,612 seed entries) pass schema validation and URL slug generation cleanly, with a unit test asserting `0` validation failures across all `3,143` combined entries.

---

### 2.5 `MF-747-5`: Image Priority Ranking, SHA-256 Verification, and `license` + `credit` Display

- **`INBOX/CATALOG_PLAN_v1_pack_extracted/Plan.v1_catalog.md:57-61`, `113`, & `131` (verbatim):**
  ```markdown
  When we have more than one image for an entry, we rank them in this order:
  1. **Museum first:** NNC / Smithsonian, ANS, Met, BnF.
  2. **Public domain:** Wikimedia and other public-domain sources.
  3. **Verified uploads:** clean photos from collectors.
  Every image shows its source and license.
  ...
  | `images_MANIFEST.csv` | **Partially.** Copy verified files (`sha256` checked) to CDN; keep `license` and `credit` for display. |
  ...
  - **Images need attribution.** Every photo we show must display its `credit` and `license` from `images_MANIFEST.csv`.
  ```

- **Required Fix (`MF-747-5`):**
  In Section 2.1 (`Allow-List Specification`) and Section 5 (`CatalogEntryDetailScreen` / `CatalogEntryCard`), specify:
  1. Build script verifies `sha256` for all 171 manifest images in `images_MANIFEST.csv`.
  2. When multiple images exist for an entry, sort by `1. Museum (NNC/Smithsonian, ANS, Met, BnF) -> 2. Public domain (Wikimedia, etc.) -> 3. Verified collector uploads`.
  3. Include `images: [{url, credit, license, source_tier}]` in `catalog_public.json` and render `credit` + `license` visibly beneath every displayed catalog image.

---

### 2.6 `MF-747-6`: Exclusion of the 4 Known Shaky X-Post Claims & `published_x_posts.csv` Gate

- **`INBOX/CATALOG_PLAN_v1_pack_extracted/Plan.v1_catalog.md:71`, `86`, & `145` (verbatim):**
  ```markdown
  - **Check the X posts before showing them.** Some early posts had shaky claims (Fugio source file, Chain cent grounding, 1793 half-cent "first" claim, 1795 $10 placeholder link). Keep the good stories, drop the shaky lines.
  ...
  - `social_posts` (only after a quick manual read)
  ...
  - **X posts:** Show on entry pages, after stripping the 4 known shaky claims.
  ```

- **Required Fix (`MF-747-6`):**
  In Section 2 (`Data Sanitization Pipeline`), explicitly add `published_x_posts.csv` / `social_posts` sanitization rules that strip or block the 4 known shaky claims (`Fugio source file`, `Chain cent grounding`, `1793 half-cent "first" claim`, and `1795 $10 placeholder link`) and add a unit test in `test/catalog_sanitizer_test.dart` verifying none of those 4 claims appear in `catalog_public.json`.

---

### 2.7 `MF-747-7`: Input Allow-List Field Accuracy & Flutter Web Virtualization for 3,143 Entries

- **`INBOX/AG_PLAN_NET-747_CATALOG-BROWSE_v1.md:45` (verbatim):**
  ```markdown
  - **Permitted Public Fields (Allow-List Only)**:
    `nac_code`, `title`, `year`, `category`, `subcategory`, `denomination`, `mint`, `composition`, `weight_g`, `diameter_mm`, `edge`, `designer`, `obverse_desc`, `reverse_desc`, `mintage_display`, `image_url`, `is_pre_federal`, `is_placeholder`, `status_badge`, `created_at_public`.
  ```

- **`INBOX/CATALOG_PLAN_v1_pack_extracted/Plan.v1_catalog.md:80-88` & `122` (verbatim):**
  ```markdown
  **Safe to show (allow-list):**
  - `nac_code`, `name`, `category`, `year_start`, `year_end`, `mint`, `denomination`
  - `composition`, `weight_grams`, `diameter_mm`, `edge`
  - `obverse`, `reverse`, `notes`
  - `references` (public catalog numbers)
  - `figures` — **only if** `status` is sourced; otherwise show *"Needs source"*
  - `social_posts` (only after a quick manual read)
  - `created_at` (used for *"Newest entries"* on the 531 real entries only)
  ...
  | Page speed | Pass | Fast load; paginate or virtualize the 2,906-coin list |
  ```

- **Required Fix (`MF-747-7`):**
  1. Align the Section 2.1 input field names with the actual JSONL schema in `Plan.v1_catalog.md:80-88` (`nac_code`, `name`, `category`, `year_start`, `year_end`, `mint`, `denomination`, `composition`, `weight_grams`, `diameter_mm`, `edge`, `obverse`, `reverse`, `notes`, `references`, `figures` [only if `status` is sourced, else `"Needs source"`], `social_posts` [after stripping the 4 shaky claims], and `created_at` [kept only on the 531 `entries_20261103.jsonl` records for `"Newest entries"`]), and specify that `status_badge`, `is_pre_federal`, and `is_placeholder` are **derived output fields** computed by `scripts/build_public_catalog.py`.
  2. Specify in Section 5 (`Phase 1` / `CatalogHomeScreen`) that the 2,906-coin browse view uses lazy viewport virtualization (`CustomScrollView` + `SliverGrid` / `SliverList` with `SliverChildBuilderDelegate` or pagination) so all 3,143 entries never mount simultaneously in the DOM.

---

## 3. Scoring Breakdown

| Category | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **Precedence & Branch / Prod Isolation (`Section 0`)** | 20 | **20 / 20** | Exemplary: defers behind 26 Nov must-ships & `NET-746`/`NET-748`; isolates to `catalog-browse-p7v12` off `p7v12`; keeps `origin/main` (`9f04550a`), `p7-v8.9`, and `dev` untouched. |
| **Eric's 3 Binding Decisions (`Section 3.1`)** | 20 | **20 / 20** | Accurately enforces interleaving 2000–2026 entries in chronological checklist, excluding seeds from `"Newest Entries"`, 888 `"Details coming"` single-tag rule, and zero internal leaks. |
| **Data Sanitization & Schema / Asset Pipeline (`Section 2`)** | 20 | **14 / 20** | Strong allow-list concept, but misses `schema.json` regex fix for `.BEP.BASE.2` (`MF-747-4`), image ranking + SHA-256 + `license`/`credit` attribution (`MF-747-5`), the 4 shaky X-post exclusions (`MF-747-6`), and exact input field names (`MF-747-7`). |
| **UX & Accessibility Compliance (`Section 3.2 & 4`)** | 20 | **15 / 20** | Captures 20px/24px/30px/40px typography and Morgan top block, but misses exact `#1F5FAD`/`#0B2545`/`#6B6B6B` badge colors & SVGs (`MF-747-2`), page section order / `"Newest Entries"` component, and `image+source first` list sorting (`MF-747-3`). |
| **Routing, Soft-404 Reuse & Verification (`Section 5 & 6`)** | 20 | **15 / 20** | Must reuse `NotFoundScreen` (`numista_mobile/lib/screens/not_found_screen.dart`) per `Plan.v1_catalog.md:13` instead of building a second `CatalogSoft404Screen`, and must specify `main.dart:119-140` (`isKnownPath`) + `firebase.json` routing & `Sliver` virtualization (`MF-747-1`, `MF-747-7`). |
| **TOTAL** | **100** | **84 / 100** | **REVISE TO `v2` (`MF-747-1` .. `MF-747-7`)** |

---

## 4. Handoff & Next Action

- **Status:** `84/100 — REVISE TO v2`.
- **Next Turn:** **AG CoS** (to incorporate `MF-747-1` through `MF-747-7` into `AG_PLAN_NET-747_CATALOG-BROWSE_v2.md`) or **Grok CoS** for review/consolidation. Once `MF-747-1`..`MF-747-7` are folded in, Argon is ready to re-verify immediately for `95+/100`.
