# ARGON PLAN.v1 — US Numismatics Catalog Site Integration (1776 – 2026)

- **Document ID:** `ARGON_PLAN_V1_US_NUMISMATICS_CATALOG_2026-10-28`
- **Architect:** Argon (AG System Architect / AG CoS)
- **Filed DTG:** 2026-10-28 ~11:45 AM ET (2026-10-28 15:45 UTC)
- **Authority / Directive:** NET-642 (Desk) & Direct Founder Brief (Eric Seaman)
- **Status:** **PLAN ONLY — NO EXECUTE / NO FOLD / NO SPEND AUTHORIZED BY THIS BATON**
- **Board Rule Compliance:**
  - `origin/main` strictly **LOCKED** (Mint FAIL-FIX on `p7-gate` remains Day #1 per NET-641; this plan does not steal Mint execution).
  - Production Fold on **HOLD** (`NET-609` / Stack `586+588+589+590`).
  - Credit Spend **$0** on this baton (afternoon Phase I index-wall ingest is owned separately by Catalog Research under NET-640).

---

## 1. Executive Summary & Vision

Eric's directive establishes the **US Numismatics Catalog**: an academic-grade, comprehensive reference spanning every coin, bank note, and medal used on USA territory from **1776 through October 28, 2026** (the full 250-year Semiquincentennial arc).

### Key Architectural Pillars
1. **Priority Hierarchy:** Coins and Bank Notes first (Phase 1); Medals (official U.S. Mint + common private commemoratives) second (Phase 2).
2. **Browsing & Discovery:** Default sortable by **Year produced** (1776 → 2026), filterable by **Kind** (Coin, Bank Note, Medal), **Class / Denomination**, **Issuing Authority / Mint**, and **Series**.
3. **Multi-Modal Search:** Full-text keyword search (terms, engravers, varieties) and visual image search integration with the existing Morgan AI brain.
4. **Resilient Dual-Sided Assets:** Every item displays Obverse/Front and Reverse/Back. When historical imagery is not yet sourced, clean standardized **SVG/Vector Placeholders** prevent broken UI and maintain catalog data completeness.
5. **Universal Internal Key:** Full integration with the proprietary **NAC1** identifier scheme (`NAC1.<KIND>.<CC>.<CLASS>.<SERIES>.<DATE>.<FAC>.<VAR>.<CHK>`) designed in `NAC_CODE_DESIGN_2026-10-28.md`.

---

## 2. Data Path & Storage Architecture

```
[Local Research & Staging]
C:\Users\ericd\Documents\MyVertexProject\Numismatics Catalog
  ├── 00_CATALOG_RESEARCH/ (Evidence packs, AR extracts, NNP/FRASER texts)
  ├── 01_INCOMING/ (Inbound batons & plans)
  ├── 02_STAGED_FOR_GCP/ (Normalized JSONL / CSV ready for ingest)
  └── 03_DO_NOT_DUPLICATE/ (Registry cross-checks)
           │
           ▼
[GCP Cloud Infrastructure (numista-morgan-pilot & studio)]
  ├── Discovery Engine (`numista-morgan-pilot`):
  │     ├── `morgan-docs` (Mint pages + primary source text)
  │     ├── `morgan-primary-fraser-bep` (Ingested FRASER & BEP primary records)
  │     └── `smithsonian-nnc` (54,306 CC0 object cards)
  └── Firestore (`studio-9101802118` - Production Reference DB):
        └── Collection: `us_numismatics_catalog` (Targeted read-only catalog collection)
           │
           ▼
[Flutter Front-End (`numista_mobile`)]
  ├── Route: `/catalog` -> `CatalogBrowseScreen`
  ├── Route: `/catalog/:nac_code` -> `CatalogItemDetailScreen`
  └── Services: `CatalogService` + `MorganSearchProvider`
```

### Data Pipeline Stages
1. **Staging (`02_STAGED_FOR_GCP`):** Standardized records emitted as JSONL matching the `CatalogItem` schema, keyed by `nac_code`.
2. **Crosswalk Enrichment:** Script joins each record against the 25 verified evidence packs (699 rows), the 1,152 verified AR mintage rows, and existing `definitive_reference` documents without overwriting verified values.
3. **Cloud Firestore Schema (`us_numismatics_catalog`):**
   ```typescript
   interface CatalogItem {
     nac_code: string;            // e.g. "NAC1.CN.US.1D.MORGAN.1881.S.BASE.E"
     kind: "CN" | "BN" | "MD" | "TK" | "ST";
     country: "US" | "PF";
     denomination_class: string;  // e.g. "1D", "FRN1", "50C"
     series: string;              // e.g. "MORGAN", "FRANKLIN", "AWQ"
     year: number;                // e.g. 1881
     year_display: string;        // e.g. "1881-S", "1787", "Series 2017A"
     facility: string;            // e.g. "S", "P", "D", "BEP", "XX"
     variety: string;             // e.g. "BASE", "3LEG", "VAM3"
     title: string;               // "1881-S Morgan Silver Dollar"
     obverse_image_url: string?;  // GCS CDN URL or null
     reverse_image_url: string?;  // GCS CDN URL or null
     has_obverse_image: boolean;
     has_reverse_image: boolean;
     mintage_mint_primary: number?; // Official Mint manufactured count (Tier A)
     mintage_trade_estimate: number?; // Secondary business strike convention (Tier B)
     mintage_proof: number?;
     specifications: {
       weight_grams: number?;
       diameter_mm: number?;
       composition: string?;
       fineness: number?;
       edge: string?;
     };
     historical_authority_citations: Array<{
       source_name: string;
       document_cite: string;
       url: string?;
     }>;
     crosswalk: {
       firestore_def_ref_id: string?;
       smithsonian_id: string?;
       pcgs_number: number?;
       ngc_id: string?;
       friedberg_number: string?;
     };
   }
   ```

---

## 3. UI Surfaces & UX Layout (Good Ideas & UX Designer)

### Screen 1: The Master Catalog Browse Screen (`/catalog`)
- **Top App Bar / Hero:**
  - Search Bar: Instant debounce query (matches Title, NAC Code, Denomination, Year, Engraver).
  - Camera / Lens Icon: Instant launch of Microscope / Image Scan to visual-match against the catalog.
- **Filter Rail / Drawer:**
  - **Category Tabs:** All | Coins | Bank Notes | Medals.
  - **Chronological Slider / Picker:** Quick jump to eras:
    - *Colonial & Confederation (1776–1791)*
    - *Early Federal (1792–1837)*
    - *Civil War & Gilded Age (1838–1900)*
    - *20th Century Renaissance (1901–1964)*
    - *Modern & Commemorative (1965–2025)*
    - *Semiquincentennial 250th (2026)*
  - **Mint / Facility Filter:** Philadelphia (P), Denver (D), San Francisco (S), West Point (W), Carson City (CC), New Orleans (O), Charlotte (C), Dahlonega (D), BEP.
  - **Image Filter:** Show All | Only With Images | Needs Sourcing.
- **Card Grid Layout (Infinite Scroll / Virtualized List):**
  - High-performance `SliverGrid` rendering 2-column (mobile) or 4-column (desktop web) cards.
  - Each card features:
    - **Dual Flippable Mini-Thumbnail:** Tapping a small toggle flips between Obverse and Reverse.
    - **Placeholder Graphics:** When an image is missing, a handsome vector silhouette renders with an embossed badge: `[Obverse Pending Sourcing]`.
    - **Year & Mintmark Badge:** e.g., `1881-S` in bold header.
    - **Official Mintage Pill:** Clear Tier-A vs Tier-B separation.
    - **NAC Code Chip:** Tap-to-copy internal handle.
    - **Quick Add Button:** `+ Add to My Collection` or `+ Add to Wishlist`.

### Screen 2: Catalog Detail Deep-Dive Screen (`/catalog/:nac_code`)
- Interactive high-res dual image viewer with zoom/pan inspection.
- Primary Archival Citations panel (linking directly to FRASER, BEP Fact Sheets, or NARA warrants).
- Morgan AI "Ask Morgan About This Issue" floating prompt drawer.
- Variety & Die State sub-table (e.g. VAMs, Doubled Dies, 3-Legged varieties).

---

## 4. Auth & Access Gating Strategy

1. **Guest / Public Tier (Front Door SEO & Engagement):**
   - Free, unauthenticated access to search, browse, filter, and view basic specifications and year mintages.
   - Designed to establish Numista.Ai as the canonical web destination for numismatic research.
2. **Free Registered Collector Tier:**
   - Unlocks `+ Add to Collection`, `+ Add to Wishlist`, and one-click export to CSV/PDF.
   - Saves custom filter sets and alerts.
3. **Advanced Research Tier (Future Pro/Subscriber):**
   - Direct queries against the Discovery Engine / Morgan Research Bot.
   - High-resolution raw archival document scans and provenance trails.

---

## 5. Preview vs Main Isolation Strategy

- **Hard Boundary:** Live production (`numista-vault.web.app` / `origin/main`) remains strictly **LOCKED**.
- **Preview Staging Environment:**
  - All Catalog UI changes developed exclusively on branch `dev`.
  - Preview deployments run to Firebase preview channels (e.g. `preview-catalog` or `p7-gate` once resolved).
- **Zero Impact on Mint Track:**
  - Mint FAIL-FIX (`NET-641`) on `p7-gate` is currently Day #1 priority for founder retest.
  - Catalog work is maintained in a completely decoupled feature package (`lib/screens/catalog/` and `lib/services/catalog/`) so that merging or testing Catalog code cannot destabilize the Mint Invoice/Dropzone fix.

---

## 6. Relationship to Existing Coin Cards, Checklists, & Mint Catalog

1. **Non-Destructive Overlap:** The Catalog does **not** replace the user's personal `CollectionRow` or `CoinModel`. Instead, existing collection items link to the catalog via the foreign key `nac_code`.
2. **Checklist Synergy:** The 25 sourced evidence packs (AWQ, ASE, ATB, Innovation $1) become instant official checklists generated directly from catalog queries.
3. **U.S. Mint Integration:** Modern Mint releases (2025–2026 SemiQ) maintain a live link between the Mint product page and the permanent catalog type card.

---

## 7. Shipping Roadmap: Black Friday Cut (Nov 27, 2026)

### Phase 1: Ships BEFORE Black Friday (Fri 27 Nov 2026)
- **Scope:** Complete US Circulating and Bullion Coins (1792–2026) + Major US Paper Currency (Large & Small Size FRNs, Silver Certificates, Gold Certificates).
- **Features:**
  - `/catalog` master searchable/scrollable grid sorted chronologically by Year.
  - Full-text search and faceted filters (Year, Denomination, Mint).
  - Dual-sided image viewer with fallback placeholders.
  - One-click `Add to Collection` / `Add to Wishlist`.
  - Initial 3,000+ verified catalog cards with NAC1 codes and primary mintage tables.

### Phase 2: Ships AFTER Black Friday (Q1 2027)
- **Scope:** Pre-Federal / Colonial Coppers (1776–1791), Official U.S. Mint Medals (Presidential, Congressional, Assay), Private Commemorative Medals, and World Specie.
- **Features:**
  - Visual Image Search (Microscope photo-matching directly to catalog items).
  - Advanced Morgan AI conversational research on individual catalog cards.
  - User image contribution / crowdsourced gap-filling review queue.

---

## 8. Verification & Test Commands (Rule 8 Compliance)

Before declaring any implementation phase complete, the following commands must exit code 0:
```bash
# 1. Frontend Flutter Analysis
flutter analyze lib/screens/catalog/ lib/services/catalog/

# 2. Frontend Widget Tests
flutter test test/catalog_browse_test.dart

# 3. Backend Data Integrity Check
python numista_tests/test_catalog_schema.py

# 4. Git Cleanliness
git status --porcelain
```

---
**Filed by Argon / AG CoS · Distributed to BATONS, INBOX, and RADIO NET · OVER.**
