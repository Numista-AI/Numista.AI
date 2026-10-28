# Numista.AI — U.S. Numismatics Master Catalog (1776 – 2026)
## Architectural Specification & Implementation Plan (Argon Plan.v1)

> **Instructions for External LLM Reviewers (Grok & Gemini):**  
> You are reviewing this architectural specification for **Numista.AI**, a specialized AI-powered platform for numismatists, collectors, and researchers.  
> Review this plan for:
> 1. Architectural completeness, performance scalability, and data pipeline integrity.
> 2. Flutter/Web UX fluidity, especially regarding dual-sided coin/banknote rendering and virtualized list performance.
> 3. Specific answers and trade-off analysis for the **4 Strategic Architectural Questions** in Section 8.

---

## 1. Executive Summary & Product Vision

### 1.1 The Directive
To commemorate the 250th anniversary of the United States (the Semiquincentennial arc), Numista.AI will deploy a definitive, academic-grade **U.S. Numismatics Catalog**. The catalog spans every coin, bank note, and medal used on USA territory from **July 4, 1776 through October 28, 2026**.

### 1.2 Core Product Pillars
1. **Scope & Hierarchy:** Complete coverage of coins, paper currency, and medals. Initial priority (Phase 1) targets **Coins and Bank Notes**; secondary priority (Phase 2) integrates **Medals** (official U.S. Mint issues followed by historical commemoratives).
2. **Chronological Baseline & Multi-Modal Search:** Built upon an intuitive chronological axis starting at 1776. Fully searchable via text terms, denominations, engravers, varieties, and multi-modal visual image matching.
3. **Resilient Dual-Sided Assets & Missing Image Policy:** Complete numismatic data records must **never** be withheld from users due to missing photography. When images are unavailable, a high-fidelity **dual-sided placeholder standard** displays standardized obverse and reverse vector silhouettes while preserving 100% of metadata, mintages, and historical specifications.
4. **Universal Standardized Grammar (`NAC1`):** Every numismatic entity is governed by a deterministic, human-readable, machine-parsable identifier (`NAC1.<KIND>.<CC>.<CLASS>.<SERIES>.<DATE>.<FAC>.<VAR>.<CHK>`) that cleanly indexes coins, currency, and medals without naming collisions.
5. **Non-Destructive Integration:** The catalog functions as the single source of truth (SSOT) reference layer, seamlessly cross-linking with personal collection tracking, official checklists, and modern U.S. Mint releases.

---

## 2. Universal Identifier Grammar (`NAC1`) & Data Model

### 2.1 The `NAC1` Grammar Specification
To uniquely index ~250 years of diverse numismatic issues across coins, notes, and medals, all records adhere to the **NAC1 (Numista AI Catalog v1)** schema:

$$\text{NAC1} \,.\, \langle\text{KIND}\rangle \,.\, \langle\text{CC}\rangle \,.\, \langle\text{CLASS}\rangle \,.\, \langle\text{SERIES}\rangle \,.\, \langle\text{DATE}\rangle \,.\, \langle\text{FAC}\rangle \,.\, \langle\text{VAR}\rangle \,.\, \langle\text{CHK}\rangle$$

| Segment | Meaning | Allowed Tokens / Rules | Example |
| :--- | :--- | :--- | :--- |
| **KIND** | Physical Object Class | `CN` (Coin), `BN` (Bank Note), `MD` (Medal), `TK` (Token), `ST` (Stamp/Currency) | `CN` |
| **CC** | Country / Political Entity | `US` (United States Federal), `PF` (Pre-Federal / Colonial), `CS` (Confederate States) | `US` |
| **CLASS** | Denomination / Face Value | Standard tokens: `1C`, `5C`, `10C`, `25C`, `50C`, `1D`, `2D50`, `5D`, `10D`, `20D`, `FRN1`, `SC5`, `GC1000` | `1D` |
| **SERIES** | Design or Numismatic Type | Uppercase alphanumeric series identifier: `MORGAN`, `PEACE`, `FLOWINGHAIR`, `WALKINGLIBERTY` | `MORGAN` |
| **DATE** | Struck / Series Year | 4-digit Gregorian year (`1776` to `2026`) or range (`1787`, `1881`, `1921`) | `1881` |
| **FAC** | Mint Facility / Producer | Geographic facility token: `P` (Phila), `D` (Denver), `S` (SF), `W` (West Point), `CC` (Carson City), `O` (New Orleans), `C` (Charlotte), `BEP` (Bureau of Engraving and Printing), `XX` (Unknown/Private) | `S` |
| **VAR** | Variety / Die Marriage / State | Die variety or baseline strike: `BASE` (Regular business), `PROOF`, `3LEG`, `VAM3`, `DDO1`, `STAR` | `BASE` |
| **CHK** | Integrity Checksum | Modulo-36 or Luhn alphanumeric single-character verify digit | `E` |

*Canonical Example:* `NAC1.CN.US.1D.MORGAN.1881.S.BASE.E` (1881-S Morgan Silver Dollar, Regular Strike).

---

### 2.2 Firestore Schema Specification (`us_numismatics_catalog`)
All items reside in a globally replicated, read-optimized collection in Cloud Firestore:

```typescript
interface CatalogItem {
  // Identity & Routing
  nac_code: string;                  // Primary Key, e.g. "NAC1.CN.US.1D.MORGAN.1881.S.BASE.E"
  kind: "CN" | "BN" | "MD" | "TK";   // Object category
  country_era: "PRE_FEDERAL" | "EARLY_FEDERAL" | "FEDERAL" | "CONFEDERATE";
  denomination_class: string;        // "1D", "25C", "SC5"
  series: string;                    // "MORGAN", "AWQ", "SILVER_CERT"
  
  // Chronology & Display
  year: number;                      // Integer sort key (e.g. 1881)
  year_display: string;              // "1881-S", "Series 1899", "1787 Fugio"
  title: string;                     // "1881-S Morgan Silver Dollar"
  subtitle: string;                  // "Liberty Head / Eagle Reverse"
  
  // Imagery & Visual Assets
  obverse_image_url: string | null;  // High-res WebP CDN URL (or null if missing)
  reverse_image_url: string | null;  // High-res WebP CDN URL (or null if missing)
  has_obverse_image: boolean;        // Quick boolean flag for query filters
  has_reverse_image: boolean;        // Quick boolean flag for query filters
  image_source_credit: string | null;// "National Numismatic Collection / Smithsonian"
  
  // Authoritative Mintages (Dual-Tier Convention)
  mintage_official_mint: number | null; // Tier-A primary source (Mint Annual Report count)
  mintage_commercial: number | null;    // Tier-B numismatic consensus (deducting proofs/melt)
  mintage_proof: number | null;         // Official proof strike total
  mintage_estimated: boolean;           // True for pre-1850 estimates or weight-count deliveries
  
  // Physical & Numismatic Specifications
  specifications: {
    designer_obverse: string | null;    // "George T. Morgan"
    designer_reverse: string | null;
    composition: string;                // "90% Silver, 10% Copper"
    weight_grams: number | null;        // 26.73
    diameter_mm: number | null;         // 38.1
    edge: string | null;                // "Reeded", "Lettered", "Plain"
    alignment: "COIN" | "MEDAL";       // Coin turn (180 deg) vs Medal turn (0 deg)
  };
  
  // Concordance & External Identifiers
  concordance: {
    guide_book_red_book_id?: string;
    friedberg_number?: string;          // Bank note classification (e.g. "Fr. 282")
    smithsonian_nnc_id?: string;        // Smithsonian National Numismatic Collection ID
    pcgs_number?: number;               // PCGS coin number
    ngc_id?: string;                    // NGC coin ID
  };
  
  // Archival Evidence & Citations
  primary_citations: Array<{
    source_name: string;               // "U.S. Mint Annual Report 1882", "BEP Fact Sheet"
    citation_text: string;
    document_url?: string;
  }>;
}
```

---

## 3. Data Pipeline & Ingestion Architecture

```
[Local Catalog Research & Extraction]
  ├── Evidence Packs (25 verified series, 699 rows)
  ├── Annual Report Mintage Records (1,152 verified rows)
  ├── Smithsonian NNC Open Access Cards (54,306 CC0 records)
  └── FRASER / BEP Archival Fact Sheets
         │
         ▼
[Normalization & NAC1 Generation]
  ├── Python ETL Pipeline: `scripts/generate_nac1_records.py`
  ├── Schema Validation against `catalog_schema.json`
  └── Quality Assurance (Dual-source citation validation)
         │
         ▼
[GCP Staging & Storage]
  ├── GCS Bucket: `gs://numista-catalog-assets/`
  │     ├── High-Res Obverse/Reverse WebP Images
  │     └── Standalone Vector Placeholder SVGs
  ├── Discovery Engine (`numista-morgan-pilot`):
  │     └── Full-text & vector semantic indexing for AI inquiries
  └── Cloud Firestore (`us_numismatics_catalog`):
        └── Read-optimized, cached document store
         │
         ▼
[Flutter Client Presentation Layer]
  ├── `CatalogService` (HTTP / Firestore SDK with offline memory cache)
  └── UI Presentation: Virtualized Grid, Year Timeline Slider, Dual-Flip Cards
```

### Ingestion Safeguards & Non-Destructive Integrity
1. **Never Overwrite User Data:** Catalog records are strictly reference data. Personal collection records (`UserCollectionCoin`) maintain their own private schema and link to the catalog via `nac_code`.
2. **Zero Mass-Invention:** Records are only published if verified by at least one Tier-A primary source (U.S. Mint Annual Reports, BEP warrants, Treasury weight counts) or Tier-B academic reference (Red Book, Friedberg, Newman).
3. **Dual Mintage Parity:** Avoids controversial mintage debates by displaying **both** the official manufactured delivery count and the trade consensus figure side-by-side.

---

## 4. UI / UX Design & Presentation Layer

### 4.1 Master Catalog Screen (`/catalog`)
The user experience is designed for both lightning-fast scholarly lookup and serendipitous historical exploration:

```
+-----------------------------------------------------------------------+
|  [Search: "1881 Morgan", "Fr. 282", "Abel Buell"...]  [ (o) Scan AI ] |
+-----------------------------------------------------------------------+
|  TABS: [ ALL (250y) ]   [ COINS ]   [ BANK NOTES ]   [ MEDALS ]       |
+-----------------------------------------------------------------------+
|  ERA SLIDER:  1776 ==========[ 1881 ]======================== 2026   |
|  Quick Era: [Colonial] [Early Fed] [Civil War] [Gilded] [20th] [Modern] |
|  Mints: [x] P   [x] D   [x] S   [x] CC   [x] O   [x] W   [ ] BEP      |
+-----------------------------------------------------------------------+
|  GRID VIEW (Sorted Chronologically: 1776 -> 2026):                     |
|                                                                       |
|  +---------------------------+       +---------------------------+    |
|  | [FLIP]  (Obverse Photo)   |       | [FLIP]  (Front Photo)     |    |
|  |                           |       |                           |    |
|  | 1881-S Morgan Dollar      |       | Series 1899 $5 "Porthole" |    |
|  | NAC1.CN.US.1D.MORGAN...   |       | NAC1.BN.US.SC5.SILVER...  |    |
|  | Mintage: 12,760,000       |       | BEP Delivery: 13,440,000  |    |
|  | [ + Collection ] [ Detail ]|      | [ + Collection ] [ Detail ]|    |
|  +---------------------------+       +---------------------------+    |
|                                                                       |
|  +---------------------------+       +---------------------------+    |
|  | [FLIP]  (Vector Ghost)    |       | [FLIP]  (Obverse Photo)   |    |
|  |   [?] OBVERSE MISSING     |       |                           |    |
|  | 1787 Fugio Cent - Club    |       | 1921-S Walking Liberty    |    |
|  | NAC1.CN.PF.1C.FUGIO...    |       | NAC1.CN.US.50C.WALKING... |    |
|  | Mintage: Est. 398,577     |       | Mintage: 548,000          |    |
|  | [ + Collection ] [ Detail ]|      | [ + Collection ] [ Detail ]|    |
|  +---------------------------+       +---------------------------+    |
+-----------------------------------------------------------------------+
```

### 4.2 The Dual-Sided Card Interaction
Every card features an interactive **Flip Toggle**:
- **Front Side (Default):** Displays the coin Obverse or banknote Face, title, denomination, and mint facility.
- **Reverse Side (Flipped):** Seamless 3D flip animation revealing the coin Reverse or banknote Back, edge details, reverse designer, and official mintage.
- **One-Tap Quick Actions:** Direct buttons to `+ Add to My Collection` or `+ Add to Wishlist` without having to navigate away from the browsing scroll.

---

## 5. Missing Image Standard & Dual Placeholder Architecture

### 5.1 The Principle of Resilient Completeness
Numismatic databases often suffer from "orphan gaps" where rare dates or patterns are excluded simply because a public-domain photograph is unavailable. Numista.AI guarantees **100% catalog coverage**:
- If an image cannot be sourced from open collections (Smithsonian CC0, U.S. Mint public assets, or NARA), the catalog item **is published immediately** with full metadata, mintage records, and physical specifications.
- Missing images are represented by an aesthetically polished, vector-based **Dual Placeholder Component**.

### 5.2 Placeholder Technical Specification (`DualSidedPlaceholder`)
The placeholder is rendered as a clean, responsive Flutter widget:

```dart
class DualSidedPlaceholder extends StatelessWidget {
  final String kind; // "CN" (Coin), "BN" (Bank Note), "MD" (Medal)
  final String face; // "OBVERSE" | "REVERSE"
  final String denomination;
  final int year;

  const DualSidedPlaceholder({
    super.key,
    required this.kind,
    required this.face,
    required this.denomination,
    required this.year,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1E222D),
        borderRadius: BorderRadius.circular(kind == 'BN' ? 4.0 : 100.0),
        border: Border.all(color: const Color(0xFF2C3242), width: 1.5),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              kind == 'BN' ? Icons.crop_landscape : Icons.monetization_on_outlined,
              size: 40,
              color: Colors.white24,
            ),
            const SizedBox(height: 6),
            Text(
              face == 'OBVERSE' ? 'OBVERSE PENDING' : 'REVERSE PENDING',
              style: const TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.1,
                color: Colors.white38,
              ),
            ),
            Text(
              '$year · $denomination',
              style: const TextStyle(fontSize: 9, color: Colors.white24),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 6. Access Control, Auth, & Monetization Strategy

To balance broad community adoption (top-of-funnel discovery and SEO) with sustainable SaaS monetization, the Catalog utilizes a three-tier access model:

| Capability | Guest / Public (Unauth) | Registered Collector (Free) | Pro / Research Subscriber |
| :--- | :---: | :---: | :---: |
| **Browse & Filter 1776–2026** | Unlimited | Unlimited | Unlimited |
| **Full-Text & Facet Search** | Unlimited | Unlimited | Unlimited |
| **View Dual-Sided Images & Specs**| Yes | Yes | Yes |
| **Dual-Tier Mintages & Citations** | Basic View | Full Detailed Tables | Full Detailed Tables |
| **Add to Collection / Checklist** | Prompt to Sign In | Yes (Up to 250 items) | Unlimited Items |
| **Export to CSV / PDF Inventory**| No | Standard Export | Academic / Insurance Export |
| **AI Microscope Visual Photo Match**| 3 Free Tries / Month | 10 Free Tries / Month | Unlimited Real-Time Inferences |
| **Ask Morgan AI Research Queries** | No | 5 Queries / Day | Unlimited Archival Queries |

---

## 7. Phased Implementation Roadmap

### Phase 1: Pre-Black Friday Ship Cut (Deadline: November 27, 2026)
*Target: Deliver a complete, rock-solid core catalog covering modern & classic circulation.*
- **Scope:**
  - All U.S. Federal Circulating & Bullion Coins (1792 – 2026): Half Cents, Large Cents, Small Cents, Nickels, Dimes, Quarters (including AWQ & State Quarters), Half Dollars, and Silver/Gold Dollars.
  - Major U.S. Federal Paper Currency (1861 – 2026): Legal Tender Notes, Silver Certificates, Gold Certificates, and Federal Reserve Notes.
- **Deliverables:**
  - `/catalog` interactive master browse grid with dynamic Year filter (1792–2026).
  - Instant full-text search across Title, Year, Series, and Mint Facility.
  - Dual-sided card flip with fallback vector placeholders.
  - One-click `Add to My Collection` button synced with existing user accounts.
  - Initial database of ~3,500 verified coin types and ~800 major banknote varieties.

### Phase 2: Post-Black Friday Expansion (Q1 2027)
*Target: Complete the full 250-year arc back to 1776 and incorporate medals & visual AI.*
- **Scope:**
  - Pre-Federal & Colonial Issues (1776 – 1791): Continental Dollars, Fugio Cents, and State Coppers (CT, MA, NJ, NY, VT).
  - Official U.S. Mint Historical Medals (Julian & Keusch reference sets, Presidential & Congressional medals).
  - Multi-Modal AI Visual Search: Take or upload a photo to immediately identify any coin in the master catalog.
  - Crowdsourced Community Image Verification: Vetted collectors can submit high-res photos to replace missing image placeholders.

---

## 8. Strategic Architectural Questions for Grok & Gemini

We request specific feedback and recommendations from **Grok** and **Gemini** on the following four architectural and domain questions:

### Question 1: Pre-Federal Colonial/State Coinage Grouping (1776–1791)
> *Between 1776 and the Coinage Act of 1792, coinage was issued by individual sovereign states (e.g., Massachusetts, Connecticut, New Jersey, Vermont) alongside the Continental Congress (Fugio Cent, Continental Dollar).*  
> **Question:** In the chronological year-based catalog, should pre-1792 issues be:
> - **Option A (Unified Timeline):** Interleaved directly into the global 1776–1791 chronological timeline alongside early paper money, using a "Pre-Federal" badge?
> - **Option B (State-by-State Hierarchical):** Grouped under a dedicated "Pre-Federal / Colonies & States" section, subdivided by issuing entity?  
> *Which structure provides superior usability and historical accuracy?*

### Question 2: Circulating Foreign Specie Inclusion (Spanish-American 8 Reales)
> *Spanish-American silver (8 Reales / pieces of eight) and colonial coppers were legal tender in the United States until repealed by the Coinage Act of February 21, 1857.*  
> **Question:** Should circulating foreign legal-tender coins be included in the primary US Numismatics Catalog (tagged as `CIRCULATING_FOREIGN_SPECIE`), or should the catalog strictly restrict its scope to American-authorized issues (Federal, Pre-Federal, and Territorial)? What are the risks of scope creep vs user confusion?

### Question 3: Missing Asset Placeholder & Community Ingestion Strategy
> *When an image placeholder is shown (`OBVERSE PENDING`), we anticipate users will want to provide their own photographs.*  
> **Question:** Should we implement an automated "Submit Photo for this Issue" pipeline with an AI vetting gate (checking focus, lighting, background removal, and authenticity) before human review, or should image gap-filling remain strictly restricted to institutional, CC0, and official auction archives?

### Question 4: Catalog Route Architecture & SEO/Deep-Linking in Flutter Web
> *Numista.AI operates on Flutter Web and Mobile.*  
> **Question:** For `/catalog`, should the URL structure mirror the `NAC1` code (e.g. `numista.ai/catalog/NAC1.CN.US.1D.MORGAN.1881.S.BASE.E`) or use human-friendly slugs (e.g. `numista.ai/catalog/coins/morgan-dollar/1881-s`) with canonical redirects to the `NAC1` code? How do we best balance Flutter routing simplicity with web SEO indexing?

---

## 9. Verification & Safe Execution Standard

Before any code implementing this plan is staged or promoted to testing channels, the following machine-checkable gates must execute with **Exit Code 0**:

```bash
# 1. Flutter Code Analysis
flutter analyze lib/screens/catalog/ lib/services/catalog/ lib/widgets/catalog/

# 2. Automated Widget & Regression Tests
flutter test test/catalog_browse_test.dart
flutter test test/nac_code_parser_test.dart

# 3. Data Ingestion & Schema Compliance Check
python numista_tests/test_catalog_schema.py

# 4. Git Worktree Cleanliness (Dev branch only; main branch strictly locked)
git status --porcelain
```

---
**Document Status:** Complete & Ready for Grok / Gemini Review  
**Author:** Argon (AG System Architect / AG CoS)  
**File Location:** `Numismatics Catalog/Argon Implementation Plan/US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V1.md`
