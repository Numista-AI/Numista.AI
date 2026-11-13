# Numista.AI — U.S. Numismatics Master Catalog (1776 – 2026)
## Architectural Specification & Implementation Plan (Argon Plan.v2.1)

> [!IMPORTANT]
> **SYSTEM & SPRINT LOCKS (MANDATORY HEADER RESTATEMENT):**
> - **PLAN ONLY — NO EXECUTE — NO FOLD — $0 UNAPPROVED SPEND.**
> - **Branch `origin/main` is STRICTLY LOCKED** until Mint FT PASS + Founder retest on live preview.
> - **Production Fold HOLD `586+588+589+590`** remains active.
> - **Mint FAIL-FIX (`NET-641` on `p7-gate`)** remains Day #1 priority; catalog engineering runs decoupled on `dev` and **never** touches Mint files.
> - **Discovery spend (`NET-640` ≤$60)** belongs solely to Catalog Research; this catalog integration plan incurs **$0.00**.
> - **Founder Rulings Sealed:** Incorporates Founder Eric Seaman's verbatim answers from October 29, 2026 (~8:44–8:49 AM ET) and addresses all GB CoS `NET-644` MUST-EDITS (87/100 Conditional GO).

---

## 1. Executive Summary & Product Vision

### 1.1 The Directive
To commemorate the 250th anniversary of the United States (the Semiquincentennial arc), Numista.AI will deploy an authoritative, academic-grade **U.S. Numismatics Master Catalog** at `https://numista.ai/catalog`. The catalog spans every American-authorized coin, bank note, and medal issued from **July 4, 1776 through October 28, 2026**, as well as foreign legal-tender specie that circulated extensively under Congressional acts in early America.

### 1.2 Core Product Pillars & Hard Boundaries
1. **Phased Scope & Release Alignment:**
   - **Phase 1A (Initial Launch — November 1, 2026):** Core verified U.S. Federal circulating & bullion coins (`1792–2026`), anchored by the 25 verified Evidence Packs (`AWQ`, `ASE`, `ATB`, `MORGAN`, `PEACE`, `STQ`, `AID`, etc.).
   - **Phase 1B (Pre-Black Friday Cut — November 27, 2026):** Expansion to maximum verified U.S. Federal circulating coins and major U.S. Federal paper currency (`1861–2026`) cleared by Catalog Research under the fold HOLD stack (`586+588+589+590`), plus U.S.-Philippines territorial coinage (`CC="PF"`, **INCLUDE** per standing rule).
   - **Phase 2 (Q1 2027 Expansion):** Pre-Federal & Colonial issues (`1776–1791`, `CC="CO"`), Foreign Specie circulating in early America (`1776–1857`, `CC="FS"`), Official U.S. Mint & Common Private Medals (`KIND="MD"`, `CLASS="OFF"` and `CLASS="PRV"`), and Multi-Modal Visual AI Photo Matching (`Scan AI`).
2. **Search Modality by Phase:**
   - **Phase 1:** Instant **Full-Text & Faceted Search** across title, year, series, denomination, mint facility (`FAC`), and external concordance IDs (Red Book, Friedberg, PCGS, NGC).
   - **Phase 2:** Multi-modal visual AI photo matching and microscope die-attribution.
3. **Desktop & Tablet First Browse / Mobile Companion (~90% Web / ~10% App):**
   - **Desktop & Tablet Primary Surface:** Deep catalog browsing, faceted filtering, multi-column grid comparisons, and archival inspection are engineered specifically for **Desktop Web and Tablet** (`≥1280px` primary master grid + 4-column sticky inspector, collapsing to responsive tablet views).
   - **Mobile Companion (~10% App Scope):** The mobile application is a focused, high-utility companion dedicated to **phone-only physical tasks**: quick camera additions to personal collections, slab barcode/NFC scanning, and purchase receipt capture. Full catalog browsing is not shoehorned into a cramped 2-column mobile phone feed.
4. **Resilient Dual-Sided Assets & Missing Image Policy:**
   - Verified numismatic records are **never** withheld due to missing photography. Missing images render a deterministic vector `DualSidedPlaceholder` while preserving 100% of metadata, dual-tier mintages, and primary citations.
5. **Non-Destructive Multi-Collection Isolation:**
   - `us_numismatics_catalog` is a **client read-only** reference collection. User collection additions route strictly by `kind` (`CN` → `users/{uid}/coins`, `BN` → `users/{uid}/currency`, `MD`/`TK`/`ST` → `users/{uid}/world_items`) via whole-document creation (`merge=false`), protecting Estate PDFs (`passport_pdf_generator.py`) and BigQuery ETL (`numista_bq_loader_job`).
6. **Zero Cross-Track Interference & FinOps Lock:**
   - Work executes strictly on branch `dev` (`origin/main` is locked). Mint FAIL-FIX (`NET-641` on `p7-gate`) remains Day #1 priority. This catalog integration plan incurs **$0** unapproved spend.

---

## 2. Universal Identifier Grammar (`NAC1`), Checksum & Schema Contracts

### 2.1 The `NAC1` Deterministic Grammar
Every catalog type is governed by a proprietary, human-readable, machine-parsable **NAC1 (Numista.AI Catalog v1)** identifier:

$$\text{NAC1} \,.\, \langle\text{KIND}\rangle \,.\, \langle\text{CC}\rangle \,.\, \langle\text{CLASS}\rangle \,.\, \langle\text{SERIES}\rangle \,.\, \langle\text{DATE}\rangle \,.\, \langle\text{FAC}\rangle \,.\, \langle\text{VAR}\rangle \,.\, \langle\text{CHK}\rangle$$

```bnf
nac          ::= "NAC1." kind "." cc "." class "." series "." date "." fac "." var "." chk
kind         ::= "CN" | "BN" | "MD" | "TK" | "ST"
cc           ::= "US" | "CO" | "PF" | "CS" | "FS"
class        ::= coin_class | note_class | medal_class
coin_class   ::= "HC" | "1C" | "2C" | "3C" | "5C" | "10C" | "20C" | "25C" | "50C" | "1D"
               | "G1" | "G2D5" | "G3" | "G5" | "G10" | "G20" | "G50" | "G100" | "1P" | "BUL"
note_class   ::= ("FRN" | "FRBN" | "SC" | "GC" | "TN" | "LT" | "NAT" | "DEM" | "CSA" | "CLC") denom
denom        ::= "1" | "2" | "5" | "10" | "20" | "50" | "100" | "500" | "1000" | "5000" | "10000" | "100000"
medal_class  ::= "OFF" | "PRV" | "CONG" | "PRES" | "ASSAY" | "COMM"
series       ::= 2*12 (ALPHA | DIGIT)
date         ::= YYYY | YYYY ("A"-"Z") | "ND" | "XXXX"
fac          ::= "P" | "D" | "S" | "W" | "CC" | "O" | "C" | "DD" | "M" | "PH" | "BEP" | "NARA" | "XX"
var          ::= "BASE" | 2*12 (ALPHA | DIGIT)
chk          ::= crockford32_char
```

#### Critical Segment Rules & Disambiguation
1. **Polity (`CC`) Disambiguation (Founder Q1 & Q2 Rulings, NET-644 MUST-3):**
   - **`US`**: United States Federal issues (`1792–2026`).
   - **`CO`**: Colonial & Pre-Federal issues (`1776–1791`). Separated from territorial codes to eliminate double-booking.
   - **`PF`**: U.S.-Philippines Territorial issues (`1903–1945`, explicitly **INCLUDED** per standing rule).
   - **`CS`**: Confederate States of America (`1861–1865`).
   - **`FS`**: Foreign Specie circulating in early America (`1776–1857`, e.g. Spanish-American 8 Reales). Lives in dedicated "Foreign Coins" catalog section per Founder Q2 ruling.
2. **Medal Class Scope (NET-644 MUST-4):**
   - **`OFF`**: Official U.S. Mint National / Congressional medals.
   - **`PRV`**: **Common Private Medals & Historic Tokens** (Civil War store cards, merchant tokens, exposition medals). Confirmed **IN SCOPE for Phase 2**.
   - **`CONG`**: Congressional Gold Medals.
   - **`PRES`**: Official Presidential Inaugural & Mint series medals.
   - **`ASSAY`**: Annual Assay Commission medals.
   - **`COMM`**: Sovereign commemorative medals authorized by federal/state statutes.
3. **Facility (`FAC`) vs. Struck Mint Mark Separation:**
   - `FAC` encodes the **striking city/facility**, never whether a mint mark letter is physically present on the die.
   - **Dahlonega vs. Denver Disambiguation:** Denver = **`D`**; Dahlonega (1838–1861 gold) = **`DD`**; Manila (U.S.-Philippines) = **`M`** (or `PH`); Charlotte = **`C`**; Carson City = **`CC`**; New Orleans = **`O`**.
   - **No-Mark Philadelphia Rule:** A Philadelphia coin struck without a mint mark (e.g., 1921 Morgan Dollar, 1794 Large Cent) uses `FAC = "P"` with schema fields `mint_mark_on_coin: false` and `mint_mark: null`. A marked Philadelphia coin (e.g., 1942-P War Nickel, 1980-P Quarter) uses `FAC = "P"`, `mint_mark_on_coin: true`, `mint_mark: "P"`.
   - **`XX` Reserved for Non-U.S.-Mint / Private Contracts:** Used only when struck outside the U.S. Mint / BEP (e.g., 1787 Fugio Cent under New Haven contract), paired with `facility_note`.

---

### 2.2 Deterministic Checksum Algorithm & Test Vectors (Grok Must-Fix #1)
Client-invented or malformed `nac_code` strings are rejected at both the Python API boundary and the ETL pipeline.

* **Payload:** All ASCII uppercase characters preceding the final `.CHK` separator (e.g., `NAC1.CN.US.1D.MORGAN.1881.S.BASE`).
* **Alphabet:** Crockford Base32 (`0123456789ABCDEFGHJKMNPQRSTVWXYZ`, length 32; excludes ambiguous `I`, `L`, `O`, `U`).
* **Hash Rationale:** Employs Bernstein djb2 hash multiplier (`33`) modulo prime `37` for uniform bit diffusion across short alphanumeric segments, projected into Crockford Base32 without truncation bias.
* **Hash Function:**

```python
import re

CROCKFORD_32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
NAC1_REGEX = re.compile(
    r"^(NAC1\.(CN|BN|MD|TK|ST)\.(US|CO|PF|CS|FS)\.[A-Z0-9]{2,8}\.[A-Z0-9]{2,12}\."
    r"([0-9]{4}[A-Z]?|ND|XXXX)\.(P|D|S|W|CC|O|C|DD|M|PH|BEP|NARA|XX)\."
    r"[A-Z0-9]{2,12})\.([0-9A-HJ-NP-TV-Z])$"
)

def compute_nac1_chk(payload: str) -> str:
    h = 0
    for b in payload.encode("utf-8"):
        h = (h * 33 + b) % 37
    return CROCKFORD_32[h % 32]

def validate_nac1(nac_code: str) -> bool:
    match = NAC1_REGEX.match(nac_code)
    if not match:
        return False
    payload, chk = match.group(1), match.group(6)
    return compute_nac1_chk(payload) == chk
```

#### Canonical Verified Test Vectors (13/13 100% Machine Verified)
| # | Issue Description | Payload | `CHK` | Full Verified `NAC1` |
| :--- | :--- | :--- | :---: | :--- |
| 1 | 1787 Fugio Cent (Colonial/Pre-Federal, `CC=CO`) | `NAC1.CN.CO.1C.FUGIO.1787.XX.BASE` | `K` | `NAC1.CN.CO.1C.FUGIO.1787.XX.BASE.K` |
| 2 | 1838-D Dahlonega $5 Half Eagle (`FAC=DD`, `MM=D`) | `NAC1.CN.US.G5.LIBCAP.1838.DD.BASE` | `3` | `NAC1.CN.US.G5.LIBCAP.1838.DD.BASE.3` |
| 3 | 1881-S Morgan Silver Dollar | `NAC1.CN.US.1D.MORGAN.1881.S.BASE` | `E` | `NAC1.CN.US.1D.MORGAN.1881.S.BASE.E` |
| 4 | 1921 Morgan Dollar (Phila, `mint_mark_on_coin=false`) | `NAC1.CN.US.1D.MORGAN.1921.P.BASE` | `4` | `NAC1.CN.US.1D.MORGAN.1921.P.BASE.4` |
| 5 | 1937-D Buffalo Nickel (3-Legged Variety) | `NAC1.CN.US.5C.BUFFALO.1937.D.3LEG` | `3` | `NAC1.CN.US.5C.BUFFALO.1937.D.3LEG.3` |
| 6 | 2022-P Maya Angelou Quarter (`default_face=REVERSE`) | `NAC1.CN.US.25C.AWQ.2022.P.MAYA` | `Z` | `NAC1.CN.US.25C.AWQ.2022.P.MAYA.Z` |
| 7 | 2024-W American Silver Eagle Proof | `NAC1.CN.US.1D.ASE.2024.W.PRF` | `S` | `NAC1.CN.US.1D.ASE.2024.W.PRF.S` |
| 8 | Series 2017A $1 Federal Reserve Note (BEP) | `NAC1.BN.US.FRN1.FED.2017A.BEP.BASE` | `6` | `NAC1.BN.US.FRN1.FED.2017A.BEP.BASE.6` |
| 9 | 1890 $1,000 Treasury Note ("Watermelon") | `NAC1.BN.US.TN1000.TREAS.1890.BEP.WM` | `C` | `NAC1.BN.US.TN1000.TREAS.1890.BEP.WM.C` |
| 10 | 1923-P Calvin Coolidge Presidential Medal | `NAC1.MD.US.PRES.PRES.1923.P.COOL` | `W` | `NAC1.MD.US.PRES.PRES.1923.P.COOL.W` |
| 11 | 1903-S U.S.-Philippines 1 Peso (`FAC=S`, `CC=PF`) | `NAC1.CN.PF.1P.PHL1P.1903.S.BASE` | `3` | `NAC1.CN.PF.1P.PHL1P.1903.S.BASE.3` |
| 12 | 1798 Spanish-American 8 Reales (`CC=FS`) | `NAC1.CN.FS.1D.SPAN8R.1798.M.BASE` | `1` | `NAC1.CN.FS.1D.SPAN8R.1798.M.BASE.1` |
| 13 | 1863 Civil War Store Card Token (`CLASS=PRV`) | `NAC1.MD.US.PRV.CWT.1863.XX.BASE` | `H` | `NAC1.MD.US.PRV.CWT.1863.XX.BASE.H` |

---

### 2.3 Firestore Reference Schema (`us_numismatics_catalog`)
All fields strictly adhere to `snake_case` naming:

```typescript
interface CatalogItem {
  // 1. Identity, Routing & Version Control
  nac_code: string;                  // Primary Key (Document ID == nac_code)
  nac_aliases: string[];             // Deprecated NAC1 codes resolving to this item
  seo_slug: string;                  // e.g. "coins/morgan-dollar/1881-s" (Unique indexed)
  kind: "CN" | "BN" | "MD" | "TK" | "ST";
  cc: "US" | "CO" | "PF" | "CS" | "FS"; // US Fed, Colonial, Philippines, CSA, Foreign Specie
  country_era: "PRE_FEDERAL" | "EARLY_FEDERAL" | "FEDERAL" | "CONFEDERATE" | "US_PHILIPPINES" | "FOREIGN_CIRCULATING";
  state_or_entity: string | null;    // For Pre-Federal facet: "CONTINENTAL", "CT", "MA", "NJ", "NY", "VT", null
  denomination_class: string;        // "1D", "25C", "SC5", "G5"
  series: string;                    // "MORGAN", "AWQ", "SILV"
  catalog_version: number;           // Monotonic integer incremented on verified metadata/mintage updates
  last_verified_at: string;          // ISO-8601 UTC timestamp of latest primary source verification

  // 2. Chronology, Facility & Display
  year: number;                      // Integer sort key (1776 to 2026)
  year_display: string;              // "1881-S", "1838-D (Dahlonega)", "Series 1899"
  facility_code: "P" | "D" | "S" | "W" | "CC" | "O" | "C" | "DD" | "M" | "PH" | "BEP" | "NARA" | "XX";
  mint_mark_on_coin: boolean;        // False for no-mark Phila (even though facility_code == "P")
  mint_mark: string | null;          // Exact letter struck on die ("S", "D", "CC", or null)
  facility_note: string | null;      // e.g. "New Haven private contract" when facility_code == "XX"
  title: string;                     // "1881-S Morgan Silver Dollar"
  subtitle: string;                  // "Liberty Head / Heraldic Eagle Reverse"

  // 3. Visual Assets & Unique Identity Side Rule
  default_face: "OBVERSE" | "REVERSE"; // Side that uniquely identifies the issue (e.g. "REVERSE" for AWQ/STQ)
  obverse_image_url: string | null;  // gs://numista-catalog-assets/ CDN WebP URL (or null)
  reverse_image_url: string | null;  // gs://numista-catalog-assets/ CDN WebP URL (or null)
  has_obverse_image: boolean;
  has_reverse_image: boolean;
  image_source_credit: string | null;// "Smithsonian NNC (CC0)", "U.S. Mint", "Verified Contributor: JohnDoe"
  image_tier: "MUSEUM" | "PUBLIC_DOMAIN" | "VERIFIED_COMMUNITY"; // Strict hierarchy per Founder Q3
  image_license_type: "CC0" | "US_GOV_PUBLIC_DOMAIN" | "INSTITUTIONAL_PERMISSION" | "COMMUNITY_VERIFIED_CC0" | "NONE";

  // 4. Authoritative Mintages (Dual-Tier Convention)
  mintage_official_mint: number | null; // Tier-A ONLY: US Mint Annual Reports / BEP Ledgers / Treasury Warrants
  mintage_commercial: number | null;    // Tier-B: Numismatic trade/reference consensus (Red Book / Friedberg)
  mintage_proof: number | null;         // Official proof strike total
  mintage_estimated: boolean;           // True for pre-1850 weight deliveries or partial records
  mintage_reconciliation_note: string | null; // Explains variance between Tier A and Tier B

  // 5. Physical & Numismatic Specifications
  specifications: {
    designer_obverse: string | null;
    designer_reverse: string | null;
    composition: string;
    fineness: number | null;            // e.g. 0.900 for 90% silver/gold (Required for CN bullion math)
    precious_metal_type: "SILVER" | "GOLD" | "PLATINUM" | "PALLADIUM" | "NONE";
    actual_metal_weight_oz: number | null; // ASW / AGW in troy ounces (null for clad/paper)
    weight_grams: number | null;
    diameter_mm: number | null;         // Or width_mm for banknotes
    height_mm?: number | null;          // Populated for BN rectangular notes
    edge: string | null;
    alignment: "COIN" | "MEDAL" | "NOTE";
  };

  // 6. Concordance & Crosswalk Identifiers
  concordance: {
    firestore_def_ref_id?: string | null;
    guide_book_red_book_id?: string | null;
    friedberg_number?: string | null;
    smithsonian_nnc_id?: string | null;
    pcgs_number?: number | null;          // Crosswalk only — NEVER used as Tier-A mintage source
    ngc_id?: string | null;
    gsid_xref?: string | null;
  };

  // 7. Mandatory Archival Evidence & Citations
  primary_citations: Array<{
    tier: "TIER_A_GOV" | "TIER_B_ACADEMIC";
    source_name: string;                  // e.g. "Annual Report of the Director of the Mint (1882)"
    citation_text: string;                // Page/table reference or warrant ID
    document_url?: string | null;
    verified_date: string;                // ISO-8601 date
  }>;
}
```

### 2.4 Firestore Security Rules & Write-Path Lockdown
Client SDKs have **zero write privileges** to `us_numismatics_catalog`. All catalog ingest and updates execute strictly via authenticated Google Cloud Admin / Batch ETL service accounts:

```javascript
// firestore.rules excerpt
match /us_numismatics_catalog/{nac_code} {
  // Public read access for Phase 1 SEO & Guest/Collector browsing
  allow get, list: if true;
  // Strictly forbidden from client SDK; only Admin SDK batch ETL may write
  allow create, update, delete: if false;
}
```

---

## 3. Multi-Collection Write Contract & Personal Collection Photo Toggle

### 3.1 Conditional Routing by `kind`
When an authenticated user clicks `+ Add to My Collection` on a catalog card, the request passes through `REQ_031` Firebase Auth JWT verification and `tier_gatekeeper.py`, routing strictly by `kind`:

| Catalog `kind` | Target Firestore Collection | Target Schema Contract | Downstream Consumers |
| :--- | :--- | :--- | :--- |
| **`CN`** (Coin) | `users/{uid}/coins` | `UserCollectionCoin` | Portfolio Coin Tally, `passport_pdf_generator.py`, `numista_bq_loader_job` (`coins` table) |
| **`BN`** (Bank Note) | `users/{uid}/currency` | `UserCollectionCurrency` | Currency Inventory, `numista_bq_loader_job` (`currency` table) |
| **`MD` / `TK` / `ST`** | `users/{uid}/world_items` | `UserCollectionWorldItem` | Exonumia & Sets Registry, `numista_bq_loader_job` (`world_items` table) |

> [!CAUTION]
> **Hard Boundary:** Bank notes (`BN`), medals (`MD`), tokens (`TK`), and sets (`ST`) must **never** be written to `users/{uid}/coins`. Contaminating `users/{uid}/coins` corrupts coin milestone tallies, breaks precious-metal melt calculations in `passport_pdf_generator.py`, and triggers schema dead-letter drops in `numista_bq_loader_job`.

### 3.2 Personal Collection Photo Toggle (`use_personal_photo`)
In their personal collections, collectors can upload photos of their specific graded/raw specimens while retaining full catalog linkage. Per Founder Q3 Ruling:
1. Each user collection document stores:
   - `custom_obverse_image_url: string | null`
   - `custom_reverse_image_url: string | null`
   - `use_personal_photo: boolean` (Default `true` if custom photos uploaded; togglable to `false` to display the catalog stock image instead).
2. The portfolio UI provides a one-click toggle: **`[📸 My Specimen Photo]` vs `[🏛️ Catalog Stock Photo]`**.

### 3.3 Idempotency, Whole-Document Writes & Snapshot Integrity
1. **Server-Side Checksum + Catalog Existence Verification:**
   Additions execute as atomic transactions using whole-document creation (`create()`, no `merge=true`). Document keys use `{nac_code}_SLOT1` (incrementing to `_SLOT2`, etc. for multiple specimens).
2. **"As-Of" Catalog Snapshot Protection:**
   User collection documents embed an immutable `catalog_snapshot` object (`catalog_version`, `title_at_acquire`, `mintage_official_at_acquire`, `obverse_image_url_at_acquire`), ensuring future reference updates never silently alter insurance or estate records.

---

## 4. Visual Design System & Desktop/Tablet Web UX Specification

### 4.1 Aesthetic Direction & Theme Tokens
The catalog uses a dark-mode **Archival Museum Studio** aesthetic engineered for high-contrast numismatic photography on Desktop Web (`≥1280px` 8-column browse grid + 4-column sticky right inspector):

| Design Token | Hex / Value | Usage |
| :--- | :--- | :--- |
| `Surface Background` | `#0D1017` | Primary page canvas |
| `Card / Inspector Surface` | `#161B26` | Elevated card containers and sticky detail inspector |
| `Stage Well Background` | `#090C12` | Recessed velvet-dark display well behind coin/note photography |
| `Border Subtle` | `#262F40` | Default card and filter rail hairlines (`1px solid`) |
| `Accent Gold / Primary` | `#F59E0B` | Active era scrubber, selected card border ring, Tier-B consensus highlight |
| `Verified Emerald` | `#10B981` | `CHK` verified badge, Tier-A official mintage lock, collection write confirmation |
| `Pre-Federal Amber Badge` | `#F59E0B` (`20%` bg) | Distinguishes 1776–1791 Colonial/State issues on unified timeline |
| `Foreign Specie Purple Badge` | `#A855F7` (`20%` bg) | Marks circulating foreign legal-tender coins (Spanish 8 Reales, etc.) |
| `Identity Side Sky Badge` | `#38BDF8` (`20%` bg) | Indicates when `default_face == "REVERSE"` is displayed by default |

### 4.2 Desktop Web Master Layout (`/catalog`)

```
+--------------------------------------------------------------------------------------------------+
|  URL: https://numista.ai/catalog/coins/morgan-dollar/1881-s   [Canonical: NAC1.CN.US.1D.MORGAN…] |
+--------------------------------------------------------------------------------------------------+
|  U.S. NUMISMATICS MASTER CATALOG (1776–2026)          [Search: year, series, Fr.#, NAC1…] [🔍]   |
|  TABS: [ ALL ] [🪙 COINS] [💵 BANK NOTES] [🎖️ MEDALS (Phase 2)] [🌎 FOREIGN SPECIE (1776–1857)]|
+--------------------------------------------------------------------------------------------------+
|  ERA PILLS: [All 1776–2026] [Pre-Federal 1776–1791] [Early Fed] [Gilded Age] [Modern & 250th]    |
|  SCRUBBER:  1776 ================================[ ≤ 2026 ]                                      |
|  (When Pre-Federal active) -> STATE FACET: [All] [Continental Congress] [CT] [MA] [NJ] [NY] [VT] |
|  FACILITY (FAC): [ALL] [P·Phila] [D·Denver] [S·SF] [W·WP] [CC] [O] [C] [DD·Dahlonega] [M·Manila] |
+--------------------------------------------------------------------------------------------------+
|  CATALOG BROWSE GRID (8 Cols)                        |  LIVE ARCHITECTURE INSPECTOR (4 Cols)     |
|                                                      |                                           |
|  +-----------------------+  +-----------------------+|  1881-S Morgan Silver Dollar     [CN]     |
|  | [1881-S]   [🔄 Flip]  |  | [2022-P AWQ] [🔄 Flip]||  ---------------------------------------  |
|  |                       |  | [Identity: Reverse]   ||  NAC1 SEGMENTS (Crockford-32 Verified):   |
|  |   ( 1881-S OBVERSE )  |  |   ( MAYA ANGELOU )    ||  [NAC1][CN][US][1D][MORGAN][1881][S][BASE]|
|  |   (  SILVER PHOTO  )  |  |   ( REVERSE PHOTO )   ||  Check Digit: [ E ] (Valid)               |
|  |                       |  |                       ||                                           |
|  | 1881-S Morgan Dollar  |  | 2022-P Maya Angelou   ||  FACILITY & MINT MARK (NAC §0.1):         |
|  | NAC1.CN.US.1D.MORGAN… |  | NAC1.CN.US.25C.AWQ…   ||  • FAC: "S" (San Francisco)               |
|  | Tier A: 12,760,000    |  | Tier A: 258,200,000   ||  • mint_mark_on_coin: true ("S")          |
|  | Tier B: 12,760,000    |  | Tier B: 258,200,000   ||  • Default Face: OBVERSE                  |
|  | [+ Add /coins] [Info] |  | [+ Add /coins] [Info] ||                                           |
|  +-----------------------+  +-----------------------+|  DUAL-TIER MINTAGE & CITATION:            |
|                                                      |  • Tier A (Gov): 12,760,000               |
|  +-----------------------+  +-----------------------+|  • Tier B (Trade): 12,760,000             |
|  | [Series 1899] [🔄Flip]|  | [1787 Fugio] [🔄 Flip]||  • Citation: US Mint Annual Report 1882   |
|  |                       |  | [Pre-Federal · NY]    ||                                           |
|  | [==================]  |  |   ( FUGIO OBVERSE )   ||  COLLECTION WRITE CONTRACT (REQ_031):     |
|  | [ $5 INDIAN CHIEF  ]  |  |   (  COPPER PHOTO  )  ||  • Target: users/{uid}/coins              |
|  | [==================]  |  |                       ||  • Key: NAC1.CN.US.1D…_SLOT1              |
|  | $5 Silver Certificate |  | 1787 Fugio Cent (BASE)||  • Mode: Whole-Doc create() (merge=false) |
|  | [+ Add /currency]     |  | [+ Add /coins] [Info] ||                                           |
|  +-----------------------+  +-----------------------+|                                           |
+--------------------------------------------------------------------------------------------------+
```

### 4.3 Card Anatomy & The "Unique Identity Side" Rule
1. **Default Face = Unique Identity Side (`default_face`):**
   - Standard series set `default_face: "OBVERSE"`.
   - Shared-obverse series (50 State Quarters `STQ`, America the Beautiful `ATB`, American Women Quarters `AWQ`) set `default_face: "REVERSE"` with an `Identity: Reverse` sky-blue badge.
   - Shared-reverse series (Presidential $1 `PRES`) set `default_face: "OBVERSE"`.
2. **Interactive 3D Card Flip (`550ms`):**
   - Clicking `🔄 Flip` rotates the stage `180°` along the Y-axis to reveal the opposite face in-place.

---

## 5. Missing Image Standard & Image Hierarchy Policy

### 5.1 Image Source Hierarchy (Founder Q3 Ruling)
To ensure the catalog maintains academic integrity while allowing high-quality community contributions, all catalog images follow a strict 3-tier hierarchy:
1. **Tier 1 (Museum Preferred):** Smithsonian National Numismatic Collection (NNC) CC0 Open Access, ANS, or major academic institutions.
2. **Tier 2 (U.S. Public Domain):** U.S. Mint, BEP, NARA, and Library of Congress official press and production plates.
3. **Tier 3 (Verified Collector Submissions — Strict Exception Path):**
   - Collector photo submissions are accepted **only** when:
     a) No Tier 1/2 image exists, OR the submission is proven to be **strictly higher resolution and quality** than the current placeholder/stock image.
     b) The photo passes automated AI quality pre-screening (sharpness, macro resolution, absence of glare/fingers).
     c) The photo is **formally reviewed and verified by a human Catalog Registrar**.
     d) The submitter signs an irrevocable CC0 / public-domain dedication.

### 5.2 Guest Download Restrictions (Founder Q4 Ruling)
- Unauthenticated visitors/guests browsing the public catalog can view photography on-screen, but **cannot download high-resolution images** (direct download actions disabled, CDN signed full-resolution URLs require authenticated session).

### 5.3 `DualSidedPlaceholder` Vector Standard
When photography is pending, the catalog renders vector die blueprints labeled `OBVERSE PENDING` / `REVERSE PENDING` with the `CC0 Archive Queue` badge.

---

## 6. Access Tiers, Routing & Server-Side Gatekeeping

### 6.1 SEO Slug + Canonical `NAC1` Routing
- Human-friendly public URL: `https://numista.ai/catalog/coins/morgan-dollar/1881-s`
- Deterministic canonical mapping: `/catalog/NAC1.CN.US.1D.MORGAN.1881.S.BASE.E` resolves with `301/canonical` to the SEO slug.

### 6.2 Server-Enforced Access Tiers (`tier_gatekeeper.py`)
All capabilities validate Firebase Auth tokens on Cloud Run backend endpoints:

| Capability | Guest / Public (Unauth) | Registered Free Collector | Pro / Research Subscriber | Server Enforcement Point |
| :--- | :---: | :---: | :---: | :--- |
| **Browse `/catalog`** | Public SEO | Unlimited | Unlimited | Firestore `allow get, list: if true;` |
| **Full-Text & Faceted Search** | **Session Rate-Limited** (e.g. 50 searches/day) | Unlimited | Unlimited | Cloud Run IP/UID Rate Limiter (`HTTP 429`) |
| **Image Downloads** | **NO DOWNLOAD** (View only) | Standard Res Download | Full High-Res Archival Download | CDN Signed URL Token Gate |
| **`+ Add to Collection`** | Prompt Sign-In (`HTTP 401`) | **Paid Feature** / Tier Gated (Free trial up to 5 items) | **Unlimited Items** | `tier_gatekeeper.py` Firestore transaction check |
| **Estate PDF & CSV Export** | Disabled (`HTTP 401`) | Disabled (`HTTP 403`) | Full Estate PDF + CSV Export | `passport_pdf_generator.py` auth gate |
| **Ask Morgan AI Queries** | Disabled (`HTTP 401`) | Disabled (`HTTP 403`) | Unlimited Archival Queries | `tier_gatekeeper.py` subscription check |

---

## 7. Phased Implementation Roadmap

### Phase 1A: Initial Production Launch (Target: November 1, 2026)
- **Scope:** Verified U.S. Federal circulating & bullion coins (`1792–2026`) anchored by the 25 verified Evidence Packs (`AWQ`, `ASE`, `ATB`, `MORGAN`, `PEACE`, `STQ`, `AID`, etc.).
- **Deliverables:** Desktop/Tablet Web `/catalog` browse grid, era scrubber, disambiguated `FAC` filter rail (`P`, `D`, `S`, `W`, `CC`, `O`, `C`, `DD`), instant text search, 3D card flip, and multi-collection write routing (`CN` → `users/{uid}/coins`).

### Phase 1B: Pre-Black Friday Cut (Target: November 27, 2026)
- **Scope:** Maximum verified U.S. Federal coins + U.S. Federal Paper Currency (`1861–2026`) cleared by Catalog Research under fold HOLD stack (`586+588+589+590`), plus U.S.-Philippines territorial coinage (`CC="PF"`).
- **Deliverables:** Currency tab routing `BN` to `users/{uid}/currency`.

### Phase 2: Post-Black Friday Semiquincentennial Completion (Q1 2027)
- **Scope:**
  - **Pre-Federal & Colonial Coinage (`1776–1791`, `CC="CO"`):** Interleaved into the unified 1776–2026 timeline with `"Pre-Federal"` badge and State Facet (`CONTINENTAL`, `CT`, `MA`, `NJ`, `NY`, `VT`).
  - **Foreign Specie Circulating in Early America (`1776–1857`, `CC="FS"`):** Dedicated Foreign Coins section (Spanish 8 Reales, etc.).
  - **Official & Common Private Medals (`KIND="MD"`, `CLASS="OFF"` and `CLASS="PRV"`):** Routing additions to `users/{uid}/world_items`.
  - **Multi-Modal Visual AI Photo Matching:** Camera upload attribution against catalog embeddings.
  - **Mobile Companion Camera Workflow:** Mobile companion app quick-add camera sync.

---

## 8. Strategic Architectural Decisions (Founder Rulings — Eric Seaman, Oct 29, 2026)

All strategic decisions are sealed with Founder Eric Seaman's verbatim confirmations (October 29, 2026 ~8:44–8:49 AM ET):

1. **Q1 — Pre-1792 Colonial & State Grouping:**
   - **Founder Ruling:** Pre-1792 coins interleave into the unified `1776–2026` timeline with a `"Pre-Federal"` badge and an Issuing State filter (`CONTINENTAL`, `CT`, `MA`, `NJ`, `NY`, `VT`). Confirmed.
2. **Q2 — Circulating Foreign Specie (Spanish 8 Reales, etc.):**
   - **Founder Ruling:** Stays out of the main circulating U.S. Federal catalog, but **must have an explicit place in the catalog** in a dedicated **Foreign Coins / Foreign Specie Circulating in Early America** section (`1776–1857`, `CC="FS"`). Confirmed with condition.
3. **Q3 — Missing Image & Community Photo Submissions:**
   - **Founder Ruling:** Image priority is strictly **Museum preferred → Public domain OK → User uploads allowed as 3rd option ONLY when verified (AI + human) AND higher quality than existing**. In personal collections, users can toggle between their own uploaded photos and catalog stock photos. Confirmed as modified.
4. **Q4 — Public Access & Monetization Boundaries:**
   - **Founder Ruling:** Browse and search are public; adding coins, exports, Morgan AI, and visual AI are paid features. Non-account visitors get search limitations and **NO image download**. Confirmed as modified.
5. **Mobile Architecture:**
   - **Founder Ruling:** The phone app is a small, specialized companion (~90% website / 10% app) for phone-only physical jobs: adding coins with camera, scanning slabs and receipts. Big catalog browsing stays on laptop/tablet. Confirmed.

---

## 9. Verification Gates & Safe Execution Standard

Before any implementation PR is promoted on `dev`, all five machine-checkable gates must return **Exit Code 0**:

```bash
# 1. Mint FAIL-FIX & Branch Isolation Smoke Gate (GB CoS #12)
git branch --show-current | grep -qx "dev"
git diff --name-only origin/dev..HEAD | grep -Ev "^(lib/screens/catalog/|lib/services/catalog/|lib/widgets/catalog/|numista_backend/catalog_|numista_tests/test_catalog_)" && exit 1 || true

# 2. Deterministic NAC1 Checksum, Parser & Schema Validation Gate
python -m pytest numista_tests/test_nac1_validator.py numista_tests/test_catalog_schema.py

# 3. Multi-Collection Routing & Downstream Protection Gate (Coins vs Currency vs World Items)
python -m pytest numista_tests/test_catalog_collection_routing.py numista_tests/test_passport_pdf_coin_guard.py

# 4. Flutter Static Analysis & Desktop Web Catalog Widget Tests
flutter analyze lib/screens/catalog/ lib/services/catalog/ lib/widgets/catalog/
flutter test test/catalog_browse_test.dart test/nac_code_parser_test.dart

# 5. Git Worktree Cleanliness
git status --porcelain
```

---
**Document Status:** Plan.v2.1 Complete — Ready for GB CoS & Stand Alone Grok Review  
**Author:** Argon (AG System Architect / Lead Engineer)  
**File Location:** `Numismatics Catalog/Argon Implementation Plan/US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V2.1.md`  
**Visual Mockup:** `Numismatics Catalog/Argon Implementation Plan/us_numismatics_catalog_mockup.html`
