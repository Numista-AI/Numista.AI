# Numista.AI — U.S. Numismatics Master Catalog (1776 – 2026)
## Architectural Specification & Implementation Plan (Argon Plan.v2)

> **Instructions for External LLM Reviewers (Standalone Grok, Standalone Gemini, and GB CoS):**  
> This is **Version 2 (Plan.v2)** of the Numista.AI U.S. Numismatics Master Catalog specification. It incorporates all mandatory fixes from the v1 review cycle (Standalone Gemini Decision Matrix & Domain Audit, Standalone Grok Must-Fix & Acceptance Criteria, GB CoS NET-642 12 Must-Edits) and locks Founder Eric Seaman's decisions on Strategic Questions Q1–Q4.  
> Review this specification for:
> 1. Closure of all v1 write-path, multi-collection routing (`CN` / `BN` / `MD`), idempotency, and downstream pipeline (`passport_pdf_generator.py`, `numista_bq_loader_job`, `tier_gatekeeper.py`) contracts.
> 2. Enforceability of the deterministic `NAC1` Crockford-32 checksum, facility disambiguation (`D` vs `DD`), and `mint_mark_on_coin` separation.
> 3. Desktop Web visual design completeness, `default_face` Unique Identity Side rendering, and SEO slug + canonical `NAC1` routing.

---

## 1. Executive Summary & Product Vision

### 1.1 The Directive
To commemorate the 250th anniversary of the United States (the Semiquincentennial arc), Numista.AI will deploy an authoritative, academic-grade **U.S. Numismatics Master Catalog** on Desktop Web (`https://numista.ai/catalog`). The catalog spans every American-authorized coin, bank note, and medal issued from **July 4, 1776 through October 28, 2026**.

### 1.2 Core Product Pillars & Hard Boundaries
1. **Phased Scope & Release Alignment:**
   - **Phase 1A (Initial Launch — November 1, 2026):** Core verified U.S. Federal circulating & bullion coins (`1792–2026`), anchored by the 25 verified Evidence Packs (`AWQ`, `ASE`, `ATB`, `MORGAN`, `PEACE`, `STQ`, `AID`, etc.).
   - **Phase 1B (Pre-Black Friday Cut — November 27, 2026):** Expansion to maximum verified U.S. Federal circulating coins and major U.S. Federal paper currency (`1861–2026`) cleared by Catalog Research under the fold HOLD stack (`586+588+589+590`), plus U.S.-Philippines territorial coinage (`CC="PF"`, **INCLUDE** per standing rule).
   - **Phase 2 (Q1 2027 Expansion):** Pre-Federal & Colonial issues (`1776–1791`), Official U.S. Mint & Historical Medals (`KIND="MD"`), and Multi-Modal Visual AI Photo Matching (`Scan AI`).
2. **Search Modality by Phase:**
   - **Phase 1:** Instant **Full-Text & Faceted Search** across title, year, series, denomination, mint facility (`FAC`), and external concordance IDs (Red Book, Friedberg, PCGS, NGC).
   - **Phase 2:** Multi-modal visual AI photo matching and microscope attribution.
3. **Strictly Desktop Web (`https://numista.ai`):**
   - Engineered exclusively for **Desktop Web** (`https://numista.ai`) through the end of 2026. All mobile layouts, mobile web companion views, and native mobile app routing are strictly out of scope until 2027.
4. **Resilient Dual-Sided Assets & Missing Image Policy:**
   - Verified numismatic records are **never** withheld due to missing photography. Missing images render a deterministic vector `DualSidedPlaceholder` while preserving 100% of metadata, dual-tier mintages, and primary citations.
5. **Non-Destructive Multi-Collection Isolation:**
   - `us_numismatics_catalog` is a **client read-only** reference collection. User collection additions route strictly by `kind` (`CN` → `users/{uid}/coins`, `BN` → `users/{uid}/currency`, `MD`/`TK`/`ST` → `users/{uid}/world_items`) via whole-document creation (`merge=false`), protecting Estate PDFs (`passport_pdf_generator.py`) and BigQuery ETL (`numista_bq_loader_job`).
6. **Zero Cross-Track Interference & FinOps Lock:**
   - Work executes strictly on branch `dev` (`origin/main` is locked). Mint FAIL-FIX (`NET-641` on `p7-gate`) remains Day #1 priority and its files are never touched by catalog work. Catalog Research owns `NET-640` Discovery spend (`≤$60`); this catalog integration plan incurs **$0** unapproved spend.

---

## 2. Universal Identifier Grammar (`NAC1`), Checksum & Schema Contracts

### 2.1 The `NAC1` Deterministic Grammar
Every catalog type is governed by a proprietary, human-readable, machine-parsable **NAC1 (Numista.AI Catalog v1)** identifier (`NAC_CODE_DESIGN_2026-10-28.md`):

$$\text{NAC1} \,.\, \langle\text{KIND}\rangle \,.\, \langle\text{CC}\rangle \,.\, \langle\text{CLASS}\rangle \,.\, \langle\text{SERIES}\rangle \,.\, \langle\text{DATE}\rangle \,.\, \langle\text{FAC}\rangle \,.\, \langle\text{VAR}\rangle \,.\, \langle\text{CHK}\rangle$$

```bnf
nac          ::= "NAC1." kind "." cc "." class "." series "." date "." fac "." var "." chk
kind         ::= "CN" | "BN" | "MD" | "TK" | "ST"
cc           ::= "US" | "PF" | "CS"
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

#### Critical Segment Rules & Facility Disambiguation (NAC §0.1 & GB CoS #6)
1. **Polity (`CC`) Enum Locked (Founder Q2 Ruling):**
   - `US`: United States Federal issues (`1792–2026`).
   - `PF`: Pre-Federal / Colonial / State issues (`1776–1791`) **and** U.S.-Philippines Territorial issues (`1903–1945`, explicitly **INCLUDED**).
   - `CS`: Confederate States of America (`1861–1865`).
   - *Foreign Specie Exclusion:* Foreign legal-tender coins (e.g., Spanish-American 8 Reales) are **excluded** from the primary U.S. Catalog to prevent scope creep.
2. **Facility (`FAC`) vs. Struck Mint Mark Separation:**
   - `FAC` encodes the **striking city/facility**, never whether a mint mark letter is physically present on the die.
   - **Dahlonega vs. Denver Disambiguation:** Denver = **`D`**; Dahlonega (1838–1861 gold) = **`DD`**; Manila (U.S.-Philippines) = **`M`** (or `PH`); Charlotte = **`C`**; Carson City = **`CC`**; New Orleans = **`O`**.
   - **No-Mark Philadelphia Rule:** A Philadelphia coin struck without a mint mark (e.g., 1921 Morgan Dollar, 1794 Large Cent) uses `FAC = "P"` with schema fields `mint_mark_on_coin: false` and `mint_mark: null`. A marked Philadelphia coin (e.g., 1942-P War Nickel, 1980-P Quarter) uses `FAC = "P"`, `mint_mark_on_coin: true`, `mint_mark: "P"`.
   - **`XX` Reserved for Non-U.S.-Mint / Private Contracts:** Used only when struck outside the U.S. Mint / BEP (e.g., 1787 Fugio Cent under New Haven contract), paired with `facility_note`.
3. **Sets (`KIND="ST"`):**
   - Official Mint Proof/Mint Sets receive a set-level `NAC1.ST...` code listing component coin `nac_code`s in `component_nacs[]`, while each individual coin retains its own `NAC1.CN...` record.

---

### 2.2 Deterministic Checksum Algorithm & Test Vectors (Grok Must-Fix #1)
Client-invented or malformed `nac_code` strings are rejected at both the Python API boundary and the ETL pipeline.

* **Payload:** All ASCII uppercase characters preceding the final `.CHK` separator (e.g., `NAC1.CN.US.1D.MORGAN.1881.S.BASE`).
* **Alphabet:** Crockford Base32 (`0123456789ABCDEFGHJKMNPQRSTVWXYZ`, length 32; excludes `I`, `L`, `O`, `U`).
* **Hash Function:**

```python
import re

CROCKFORD_32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
NAC1_REGEX = re.compile(
    r"^(NAC1\.(CN|BN|MD|TK|ST)\.(US|PF|CS)\.[A-Z0-9]{2,8}\.[A-Z0-9]{2,12}\."
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
    payload,chk = match.group(1), match.group(5)
    return compute_nac1_chk(payload) == chk
```

#### Canonical Verified Test Vectors
| # | Issue Description | Payload | `CHK` | Full Verified `NAC1` |
| :--- | :--- | :--- | :---: | :--- |
| 1 | 1787 Fugio Cent (Pre-Federal, New Haven contract) | `NAC1.CN.PF.1C.FUGIO.1787.XX.BASE` | `H` | `NAC1.CN.PF.1C.FUGIO.1787.XX.BASE.H` |
| 2 | 1838-D Dahlonega $5 Half Eagle (`FAC=DD`, `MM=D`) | `NAC1.CN.US.G5.LIBCAP.1838.DD.BASE` | `3` | `NAC1.CN.US.G5.LIBCAP.1838.DD.BASE.3` |
| 3 | 1881-S Morgan Silver Dollar | `NAC1.CN.US.1D.MORGAN.1881.S.BASE` | `E` | `NAC1.CN.US.1D.MORGAN.1881.S.BASE.E` |
| 4 | 1921 Morgan Dollar (Phila, `mint_mark_on_coin=false`) | `NAC1.CN.US.1D.MORGAN.1921.P.BASE` | `4` | `NAC1.CN.US.1D.MORGAN.1921.P.BASE.4` |
| 5 | 1937-D Buffalo Nickel (3-Legged Variety) | `NAC1.CN.US.5C.BUFFALO.1937.D.3LEG` | `3` | `NAC1.CN.US.5C.BUFFALO.1937.D.3LEG.3` |
| 6 | 2022-P Maya Angelou Quarter (`default_face=REVERSE`) | `NAC1.CN.US.25C.AWQ.2022.P.MAYA` | `Z` | `NAC1.CN.US.25C.AWQ.2022.P.MAYA.Z` |
| 7 | 2024-W American Silver Eagle Proof | `NAC1.CN.US.1D.ASE.2024.W.PRF` | `S` | `NAC1.CN.US.1D.ASE.2024.W.PRF.S` |
| 8 | Series 2017A $1 Federal Reserve Note (BEP) | `NAC1.BN.US.FRN1.FED.2017A.BEP.BASE` | `6` | `NAC1.BN.US.FRN1.FED.2017A.BEP.BASE.6` |
| 9 | 1890 $1,000 Treasury Note ("Watermelon") | `NAC1.BN.US.TN1000.TREAS.1890.BEP.WM` | `C` | `NAC1.BN.US.TN1000.TREAS.1890.BEP.WM.C` |
| 10 | 1923-P Calvin Coolidge Presidential Medal | `NAC1.MD.US.PRES.PRES.1923.P.COOL` | `W` | `NAC1.MD.US.PRES.PRES.1923.P.COOL.W` |

#### Collision & Alias Resolution Rules
1. Once published, a `nac_code` is **immutable**.
2. If two distinct types ever collide on the 8-segment payload before `CHK`, the Catalog Research registrar appends a disambiguator to `VAR` (`X2`, `X3`) and logs it in `NAC_SERIES_REGISTRY.md`.
3. If an unknown date (`XXXX`) is later resolved by archival research, the upgraded code becomes primary and the prior code is retained in `nac_aliases: string[]` with an automatic 301 lookup redirect.

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
  cc: "US" | "PF" | "CS";            // Issuing polity (PF = Pre-Federal or US-Philippines)
  country_era: "PRE_FEDERAL" | "EARLY_FEDERAL" | "FEDERAL" | "CONFEDERATE" | "US_PHILIPPINES";
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

  // 3. Visual Assets & Unique Identity Side Rule (GB CoS #1)
  default_face: "OBVERSE" | "REVERSE"; // Side that uniquely identifies the issue (e.g. "REVERSE" for AWQ/STQ)
  obverse_image_url: string | null;  // gs://numista-catalog-assets/ CDN WebP URL (or null)
  reverse_image_url: string | null;  // gs://numista-catalog-assets/ CDN WebP URL (or null)
  has_obverse_image: boolean;
  has_reverse_image: boolean;
  image_source_credit: string | null;// Must be Institutional/CC0 in Phase 1 (e.g. "Smithsonian NNC (CC0)")
  image_license_type: "CC0" | "US_GOV_PUBLIC_DOMAIN" | "INSTITUTIONAL_PERMISSION" | "NONE";

  // 4. Authoritative Mintages (Dual-Tier Convention — GB CoS #2 & Grok #3)
  mintage_official_mint: number | null; // Tier-A ONLY: US Mint Annual Reports / BEP Ledgers / Treasury Warrants
  mintage_commercial: number | null;    // Tier-B: Numismatic trade/reference consensus (Red Book / Friedberg)
  mintage_proof: number | null;         // Official proof strike total
  mintage_estimated: boolean;           // True for pre-1850 weight deliveries or partial records
  mintage_reconciliation_note: string | null; // Explains variance between Tier A and Tier B (e.g. Pittman Act melt)

  // 5. Physical & Numismatic Specifications
  // Hard Ingestion Rule: Whenever specifications.fineness != null, specifications.precious_metal_type
  // MUST be explicitly populated with "SILVER" | "GOLD" | "PLATINUM" | "PALLADIUM" (never "NONE" or null).
  specifications: {
    designer_obverse: string | null;
    designer_reverse: string | null;
    composition: string;
    fineness: number | null;            // e.g. 0.900 for 90% silver/gold (Required for CN bullion/melt math)
    precious_metal_type: "SILVER" | "GOLD" | "PLATINUM" | "PALLADIUM" | "NONE";
    actual_metal_weight_oz: number | null; // ASW / AGW in troy ounces (null for clad/paper)
    weight_grams: number | null;
    diameter_mm: number | null;         // Or width_mm for banknotes
    height_mm?: number | null;          // Populated for BN rectangular notes
    edge: string | null;
    alignment: "COIN" | "MEDAL" | "NOTE";
  };

  // 6. Concordance & Crosswalk Identifiers (NAC §8)
  concordance: {
    firestore_def_ref_id?: string | null; // Attached studio definitive_reference ID
    guide_book_red_book_id?: string | null;
    friedberg_number?: string | null;     // Bank notes (e.g. "Fr. 278")
    smithsonian_nnc_id?: string | null;
    pcgs_number?: number | null;          // Crosswalk only — NEVER used as Tier-A mintage source
    ngc_id?: string | null;
    gsid_xref?: string | null;            // Optional opaque FK ONLY if returned by paid org CDN API; never invented
  };

  // 7. Mandatory Archival Evidence & Citations (Grok #3)
  primary_citations: Array<{
    tier: "TIER_A_GOV" | "TIER_B_ACADEMIC";
    source_name: string;                  // e.g. "Annual Report of the Director of the Mint (1882)"
    citation_text: string;                // Page/table reference or warrant ID
    document_url?: string | null;
    verified_date: string;                // ISO-8601 date
  }>;                                     // Schema validation rejects publication if length == 0
}
```

### 2.4 Firestore Security Rules & Write-Path Lockdown (GB CoS #3)
Client SDKs have **zero write privileges** to `us_numismatics_catalog`. All catalog ingest and updates execute strictly via authenticated Google Cloud Admin / Batch ETL service accounts:

```javascript
// firestore.rules excerpt
match /us_numismatics_catalog/{nac_code} {
  // Public read access for Phase 1 SEO & Guest/Collector browsing (Founder Q4 Ruling)
  allow get, list: if true;
  // Strictly forbidden from client SDK; only Admin SDK batch ETL may write
  allow create, update, delete: if false;
}
```

---

## 3. Multi-Collection Write Contract & Downstream Pipeline Isolation

### 3.1 Conditional Routing by `kind` (Gemini Must-Fix #1 & #5, GB CoS #4)
When an authenticated user clicks `+ Add to My Collection` on a catalog card, the request **must** pass through the existing authenticated collection write stack (`REQ_031` Firebase Auth JWT verification + `tier_gatekeeper.py` quota validation) and route strictly by `kind`:

| Catalog `kind` | Target Firestore Collection | Target Schema Contract | Downstream Consumers |
| :--- | :--- | :--- | :--- |
| **`CN`** (Coin) | `users/{uid}/coins` | `UserCollectionCoin` | Portfolio Coin Tally, `passport_pdf_generator.py`, `numista_bq_loader_job` (`coins` table) |
| **`BN`** (Bank Note) | `users/{uid}/currency` | `UserCollectionCurrency` | Currency Inventory, `numista_bq_loader_job` (`currency` table) |
| **`MD` / `TK` / `ST`** | `users/{uid}/world_items` | `UserCollectionWorldItem` | Exonumia & Sets Registry, `numista_bq_loader_job` (`world_items` table) |

> [!CAUTION]
> **Hard Boundary:** Bank notes (`BN`), medals (`MD`), tokens (`TK`), and sets (`ST`) must **never** be written to `users/{uid}/coins`. Contaminating `users/{uid}/coins` corrupts coin milestone tallies, breaks precious-metal melt calculations in `passport_pdf_generator.py`, and triggers schema dead-letter drops in `numista_bq_loader_job`.

### 3.2 Idempotency, Whole-Document Writes & Snapshot Integrity (Gemini #3 & Grok #2)
All three user collection schemas (`UserCollectionCoin`, `UserCollectionCurrency`, and `UserCollectionWorldItem`) reference the catalog record by `nac_code` and persist the `catalog_snapshot` fields defined below.

1. **Server-Side Checksum + Catalog Existence Verification & Whole-Document Creation (`create()`, No `merge=true`):**
   - Collection additions execute strictly on the backend (`REQ_031` path behind `tier_gatekeeper.py`) as whole-document creates (`SetOptions(merge=true)` is prohibited on ingest).
   - **Mandatory Spoofing Guard:** Before executing the user collection write, the backend handler **must** call `validate_nac1(nac_code)` **and** verify within the same Firestore transaction that `us_numismatics_catalog/{nac_code}` exists (`catalog_doc.exists == True`), rejecting any client-invented or unreleased `nac_code` with `HTTP 400/404`.
2. **Normalized Subcollection Document Key & Multi-Tab Race Prevention:**
   - Because user subcollections (`users/{uid}/coins/{doc_id}`, `users/{uid}/currency/{doc_id}`, `users/{uid}/world_items/{doc_id}`) are already scoped by `{uid}`, the document ID omits the redundant `{uid}_` prefix and uses:
     $$\text{doc\_id} = \texttt{\{nac\_code\}\_SLOT1}$$
   - Inside a single atomic Firestore transaction:
     ```python
     if not validate_nac1(nac_code):
         raise HTTPException(status_code=400, detail="INVALID_NAC1_CHECKSUM")
     catalog_snap = tx.get(db.collection("us_numismatics_catalog").document(nac_code))
     if not catalog_snap.exists:
         raise HTTPException(status_code=404, detail="CATALOG_ITEM_NOT_FOUND")
     user_doc_ref = db.collection("users").document(uid).collection(target_col).document(f"{nac_code}_SLOT1")
     if tx.get(user_doc_ref).exists:
         return existing_doc  # HTTP 200 OK — Idempotent replay
     tx.create(user_doc_ref, whole_doc_payload)
     ```
   - If two browser tabs replay the same Quick Add concurrently, the transaction returns the existing document idempotently (`HTTP 200 OK — Already in Collection`) rather than creating duplicate rows. When a user explicitly adds a second graded specimen of the same `nac_code`, the server increments `_SLOT2`, `_SLOT3`, etc.
3. **"As-Of" Catalog Snapshot Protection (Grok Operational Risk #4):**
   - Each user collection document embeds an immutable `catalog_snapshot` object (`catalog_version`, `title_at_acquire`, `mintage_official_at_acquire`, `obverse_image_url_at_acquire`) alongside the live `nac_code` foreign key. If the reference catalog later updates a mintage estimate or replaces a placeholder photo, the user's estate/insurance record is never silently mutated; the UI displays an optional *"Catalog reference updated to v{N}"* badge.
4. **Audit Logging:**
   - Every collection mutation (`ADD`, `UPDATE`, `DELETE`, `EXPORT`) writes an immutable server-timestamped entry to `users/{uid}/collection_audit_log` for estate and insurance provenance.

### 3.3 Downstream Pipeline Guards (`passport_pdf_generator.py` & `numista_bq_loader_job`)
Before any catalog integration code merges to `dev`, defensive schema guards are enforced on the protected backend pipelines:
- **`passport_pdf_generator.py` Guard:** Validates `doc.get("kind", "CN") == "CN"` and checks `specifications.fineness` null-safety before computing bullion melt value.
- **`numista_bq_loader_job` Guard:** Routes change-stream events strictly by collection path (`coins` vs `currency` vs `world_items`) and validates `nac_code` against `validate_nac1()` before streaming to BigQuery.

---

## 4. Visual Design System & Desktop Web UX Specification

> **Interactive Prototype Reference:**  
> A live, clickable HTML/CSS/JS visual prototype accompanies this plan at:  
> `Numismatics Catalog/Argon Implementation Plan/us_numismatics_catalog_mockup.html`

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
| `Pre-Federal Amber Badge` | `#F59E0B` (`20%` bg) | Distinguishes 1776–1791 Colonial/State issues on the unified timeline |
| `Identity Side Sky Badge` | `#38BDF8` (`20%` bg) | Indicates when `default_face == "REVERSE"` is displayed by default |

---

### 4.2 Desktop Web Master Layout (`/catalog`)

```
+--------------------------------------------------------------------------------------------------+
|  URL: https://numista.ai/catalog/coins/morgan-dollar/1881-s   [Canonical: NAC1.CN.US.1D.MORGAN…] |
+--------------------------------------------------------------------------------------------------+
|  U.S. NUMISMATICS MASTER CATALOG (1776–2026)          [Search: year, series, Fr.#, NAC1…] [🔍]   |
|  TABS: [ ALL ]  [ 🪙 COINS (→ /coins) ]  [ 💵 BANK NOTES (→ /currency) ]  [ 🎖️ MEDALS (Phase 2) ]|
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
|  | [Series 1899] [🔄Flip]|  | [1838-D]     [🔄 Flip]||  • Citation: US Mint Annual Report 1882   |
|  |                       |  | [FAC: DD · Dahlonega] ||                                           |
|  | [==================]  |  |   ( 1838-D OBVERSE )  ||  COLLECTION WRITE CONTRACT (REQ_031):     |
|  | [ $5 INDIAN CHIEF  ]  |  |   (  GOLD PHOTO    )  ||  • Target: users/{uid}/coins              |
|  | [==================]  |  |                       ||  • Key: NAC1.CN.US.1D…_SLOT1              |
|  | $5 Silver Certificate |  | 1838-D Classic $5 Gold||  • Mode: Whole-Doc create() (merge=false) |
|  | [+ Add /currency]     |  | [+ Add /coins] [Info] ||                                           |
|  +-----------------------+  +-----------------------+|                                           |
+--------------------------------------------------------------------------------------------------+
```

---

### 4.3 Card Anatomy & The "Unique Identity Side" Rule (GB CoS #1)
1. **Unified Stage Container (`min-height: 168px`):**
   - **Coins & Medals (`CN` / `MD`):** Rendered inside a `144px × 144px` circular medallion frame with subtle metallic rim lighting (`Silver`, `Gold`, `Copper`, or `Bronze` gradient ring).
   - **Bank Notes (`BN`):** Rendered inside a `256px × 112px` wide rectangular currency frame (`~2.28:1` aspect ratio) inside the exact same `168px`-tall stage well, keeping card heights 100% aligned across mixed rows.
2. **Default Face = Unique Identity Side (`default_face`):**
   - Standard series (Morgan Dollar, Lincoln Cent, Walking Liberty) set `default_face: "OBVERSE"`.
   - Shared-obverse commemorative programs where the distinguishing design is on the reverse (e.g., **50 State Quarters (`STQ`)**, **America the Beautiful (`ATB`)**, **American Women Quarters (`AWQ`)**) set `default_face: "REVERSE"` so the card immediately shows the unique state or honoree artwork, accompanied by an `Identity: Reverse` sky-blue pill.
   - Shared-reverse series where the distinguishing portrait is on the obverse (e.g., **Presidential $1 (`PRES`)**) set `default_face: "OBVERSE"`.
3. **Interactive 3D Card Flip (`550ms cubic-bezier(0.22, 1, 0.36, 1)`):**
   - Clicking `🔄 Flip` rotates the stage `180°` along the Y-axis (`preserve-3d`, `backface-visibility: hidden`) to reveal the opposite face without navigating away from the scroll position.
   - A global `🔄 Flip All Cards` toggle in the filter bar allows researchers to inspect all reverses simultaneously.

---

## 5. Missing Image Standard & Locked Image Source Policy

### 5.1 Locked Institutional/CC0 Image Policy (Founder Q3 Ruling & Grok #4)
1. **Phase 1 & Early Phase 2 — Institutional & Public Domain Only:**
   - All catalog photography in Phase 1 and early Phase 2 must originate strictly from verified institutional CC0 or U.S. Government public-domain sources:
     - **Smithsonian National Numismatic Collection (NNC)** CC0 Open Access (`54,306` records)
     - **U.S. Mint / Bureau of Engraving and Printing (BEP)** official press & production imagery (`17 U.S.C. § 105` public domain)
     - **National Archives (NARA) / FRASER** digitized archival plates
   - Every image record must populate `image_source_credit` and `image_license_type`.
2. **No Automated Community Photo Uploads in Phase 1:**
   - Automated user photo submission pipelines are **disabled** in Phase 1 to eliminate copyright contamination, lighting artifacts, and variety misattribution.
   - Any future Phase 2B collector submission workflow will require: (a) explicit CC0/irrevocable license grant, (b) automated server-side EXIF/GPS metadata stripping, (c) AI quality pre-screen, and (d) mandatory human Catalog Registrar sign-off before promotion to `gs://numista-catalog-assets/`.

### 5.2 `DualSidedPlaceholder` Vector Specification
When `has_obverse_image == false` or `has_reverse_image == false`, the UI renders `DualSidedPlaceholder`:
- Displays a precision die-blueprint vector silhouette (circular concentric die rings for `CN`/`MD`; engraved rectangular border frame for `BN`).
- Clearly labels `OBVERSE PENDING` or `REVERSE PENDING` alongside the year, denomination, and `CC0 Archive Queue` status badge.

---

## 6. Routing, Access Control & Server-Side Tier Enforcement

### 6.1 SEO Slug + Canonical `NAC1` Routing Architecture (Founder Q4 Ruling)
To maximize organic Google Search indexing while preserving deterministic internal identity:
1. **Primary Public Shareable URL (Human-Friendly Slug):**
   - Pattern: `https://numista.ai/catalog/<kind-plural>/<series-slug>/<year-mint-var>`
   - Examples:
     - `https://numista.ai/catalog/coins/morgan-dollar/1881-s`
     - `https://numista.ai/catalog/coins/american-women-quarters/2022-p-maya-angelou`
     - `https://numista.ai/catalog/banknotes/silver-certificate-5/series-1899-chief`
2. **Direct `NAC1` Deep-Link Resolution & Canonical Tag:**
   - Navigating directly to `https://numista.ai/catalog/NAC1.CN.US.1D.MORGAN.1881.S.BASE.E` resolves immediately (`301/canonical`) to the human-friendly slug while injecting:
     ```html
     <link rel="canonical" href="https://numista.ai/catalog/coins/morgan-dollar/1881-s" />
     <meta name="numista:nac_code" content="NAC1.CN.US.1D.MORGAN.1881.S.BASE.E" />
     ```

### 6.2 Server-Enforced Access Tiers via `tier_gatekeeper.py` (Gemini Must-Fix #7 & Grok #5)
Entitlements are **never** trusted from client state. Every protected action validates the user's Firebase Auth token and queries `tier_gatekeeper.py` on the backend:

| Capability | Guest / Public (Unauth) | Registered Collector (Free) | Pro / Research Subscriber | Server Enforcement Point |
| :--- | :---: | :---: | :---: | :--- |
| **Browse, Filter & Search `/catalog`** | Unlimited (Public SEO) | Unlimited | Unlimited | Firestore `allow get, list: if true;` + CDN Cache |
| **View Dual-Sided Photos & Mintages** | Full View | Full View | Full View | Public Reference Read |
| **`+ Add to Collection` (Routed by `kind`)** | Prompt Sign-In (`401`) | Up to **250 Total Items** across collections | **Unlimited Items** | `tier_gatekeeper.py` atomic count check inside Firestore transaction (`HTTP 403 QUOTA_EXCEEDED` on 251st item) |
| **Estate PDF (`passport_pdf_generator.py`) & CSV Export** | Disabled (`401`) | Standard CSV (`≤250 rows`, `3/day` rate limit) | Unlimited Estate PDF + Full Insurance CSV | `tier_gatekeeper.py` + Cloud Run rate limiter (`HTTP 429`) |
| **Ask Morgan AI Archival Queries** | Disabled (`401`) | `5 Queries / Day` | Unlimited (Fair-use rate limit) | `tier_gatekeeper.py` server counter (graceful fallback if LLM unavailable) |

---

## 7. Phased Implementation Roadmap

### Phase 1A: Initial Production Launch (Deadline: November 1, 2026)
*Target: Stable Desktop Web `/catalog` launch with verified U.S. Federal circulating coins.*
- **Scope:**
  - Verified U.S. Federal circulating & bullion coin series (`1792–2026`) anchored by the 25 verified Evidence Packs (`AWQ`, `ASE`, `ATB`, `MORGAN`, `PEACE`, `STQ`, `AID`, etc.).
- **Deliverables:**
  - Desktop/Tablet Web `/catalog` browse grid, era scrubber, and disambiguated `FAC` filter rail (`P`, `D`, `S`, `W`, `CC`, `O`, `C`, `DD`).
  - Instant full-text & faceted search.
  - 3D dual-sided card flip respecting `default_face` (Unique Identity Side) and `DualSidedPlaceholder`.
  - Server-validated `+ Add to My Collection` routing `CN` whole-documents to `users/{uid}/coins` under `REQ_031` and `tier_gatekeeper.py`.

### Phase 1B: Pre-Black Friday Cut (Deadline: November 27, 2026)
*Target: Maximum verified U.S. Coins + Federal Bank Notes cleared by Catalog Research.*
- **Scope:**
  - All remaining verified U.S. Federal coin series + U.S.-Philippines territorial issues (`CC="PF"`).
  - Verified U.S. Federal Paper Currency (`1861–2026`: Legal Tender, Silver/Gold Certificates, FRNs) routing `BN` additions to `users/{uid}/currency`.
  - *Note on Volume:* Total card count is governed strictly by Catalog Research verified throughput and fold HOLD (`586+588+589+590`) clearance—zero unverified or mass-invented rows.

### Phase 2: Post-Black Friday Semiquincentennial Completion (Q1 2027)
*Target: Complete the back-to-1776 arc, official Medals, and Visual AI Photo Match.*
- **Scope:**
  - **Pre-Federal & Colonial Coinage (`1776–1791`):** Interleaved into the unified 1776–2026 timeline with `"Pre-Federal"` badges and the secondary **Issuing Authority / State Facet** (`CONTINENTAL`, `CT`, `MA`, `NJ`, `NY`, `VT`).
  - **Official U.S. Mint & Historical Medals (`KIND="MD"`):** Routing additions to `users/{uid}/world_items`.
  - **Multi-Modal Visual AI Photo Match:** Camera/upload visual attribution against catalog reference embeddings.

---

## 8. Locked Strategic Architectural Decisions (Founder Rulings)

All four strategic questions from Plan.v1 have been formally decided by Founder Eric Seaman on October 28, 2026:

1. **Q1 — Pre-Federal Colonial/State Grouping (1776–1791): LOCKED TO UNIFIED TIMELINE + STATE FACET**
   - Pre-1792 issues interleave chronologically into the primary `1776–2026` timeline with a `"Pre-Federal"` badge, paired with a secondary **Issuing Authority Facet** (`Continental Congress`, `Connecticut`, `Massachusetts`, `New Jersey`, `New York`, `Vermont`) when browsing the Pre-Federal era.
2. **Q2 — Circulating Foreign Specie (Spanish 8 Reales, etc.): LOCKED TO EXCLUDE FROM PRIMARY US CATALOG**
   - The primary U.S. Numismatics Catalog is restricted strictly to American-authorized issues (`US` Federal, `PF` Pre-Federal & U.S.-Philippines Territorial, and `CS` Confederate). Foreign legal-tender specie is excluded to prevent scope creep and may live in a separate World Specie companion facet later.
3. **Q3 — Missing Image Placeholder & Community Submissions: LOCKED TO INSTITUTIONAL / CC0 ONLY**
   - Phase 1 and early Phase 2 accept strictly institutional CC0 and U.S. Government public-domain imagery. No automated user photo upload pipeline is exposed in Phase 1.
4. **Q4 — URL Routing & Public Access: LOCKED TO SEO SLUGS + CANONICAL `NAC1`**
   - Public URLs use human-friendly SEO slugs (`/catalog/coins/morgan-dollar/1881-s`) with canonical metadata and `301` resolution from `/catalog/NAC1...`. Catalog browsing and search are public/ungated for SEO discovery.

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
**Document Status:** Plan.v2 Complete — Ready for Grok & Gemini Re-Score  
**Author:** Argon (AG System Architect / Lead Engineer)  
**File Location:** `Numismatics Catalog/Argon Implementation Plan/US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V2.md`  
**Visual Mockup:** `Numismatics Catalog/Argon Implementation Plan/us_numismatics_catalog_mockup.html`
