# STAND ALONE GROK (SAG) & GEMINI PASTE PACKET — NET-646 (Plan.v2.2)
**Task:** Independent Architectural & Mechanism Re-Review of Argon **Plan.v2.2** for the Numista.AI U.S. Numismatics Master Catalog (1776–2026).
**Prior Scores of Record:**
- GB CoS Plan.v2.1 Score: **79/100 CONDITIONAL GO** (INBOX\GBCOS_REVIEW_NET-642_PLAN-V2.1_2026-10-29.md)
- Stand Alone Grok (SAG) Plan.v2.1 Score: **74/100 CONDITIONAL GO** (Numismatics Catalog\29 OCT 26\SAG_Review_NET-642_Plan_v2.1.docx)
- SAG Addendum on Plan.v2: **58/100 CONDITIONAL NO-GO** (INBOX\WAKE_AG-COS_ARGON_NET644_ADDENDUM_SAG-MUSTFIX_20261029.md)

**Please score Plan.v2.2 (0–100) and verify that all 9 GB CoS MUST-EDITS, all 8 SAG v2.1 must-fixes (S1–S8), and all 9 SAG Addendum mechanism items are closed.**

---
# Numista.AI â€” U.S. Numismatics Master Catalog (1776 â€“ 2026)
## Architectural Specification & Implementation Plan (Argon Plan.v2.2)

> [!IMPORTANT]
> **SYSTEM & SPRINT LOCKS (MANDATORY HEADER RESTATEMENT):**
> - **PLAN ONLY â€” NO EXECUTE â€” NO FOLD â€” $0 UNAPPROVED SPEND.**
> - **Branch `origin/main` is STRICTLY LOCKED** until Mint FT PASS + Founder retest on live preview.
> - **Production Fold HOLD `586+588+589+590`** remains active. (Note: Founder Eric Seaman's 29 Oct 2026 9:13 AM ET YES in `NET-645` applies **solely** to the separate 2-figure lane â€” `1921-S Walker = 548,000` and `1955-P Franklin = 2,876,381` â€” and does **not** lift the broader HOLD `586/588/589/590`.)
> - **Mint FAIL-FIX (`NET-641` on `p7-gate`)** remains Day #1 priority; catalog engineering runs strictly decoupled on `dev` and **never** touches forbidden Mint or `p7-gate` paths (Â§9.1).
> - **Discovery spend (`NET-640` â‰¤\$60)** belongs solely to Catalog Research; this catalog integration plan incurs **\$0.00**.
> - **Reviews of Record Cited & Resolved:**
>   1. **GB CoS Plan.v2.1 Review (`79/100 CONDITIONAL GO`)**: `INBOX\GBCOS_REVIEW_NET-642_PLAN-V2.1_2026-10-29.md` (MUST-EDITS 1â€“9).
>   2. **Stand Alone Grok (SAG) Plan.v2.1 Review (`74/100 CONDITIONAL GO`)**: `Numismatics Catalog\29 OCT 26\SAG_Review_NET-642_Plan_v2.1.docx` (Must-Fixes S1â€“S8).
>   3. **SAG Addendum (`58/100 CONDITIONAL NO-GO` on v2)**: `INBOX\WAKE_AG-COS_ARGON_NET644_ADDENDUM_SAG-MUSTFIX_20261029.md` (Mechanism Fixes 1â€“9).

---

## 0. Traceability Matrix â€” SAG Addendum (1â€“9), SAG v2.1 (S1â€“S8), & GB CoS v2.1 (MUST-EDITS 1â€“9)

Every mechanism gap identified across the **SAG Addendum (`58/100`)**, **SAG v2.1 Review (`74/100`)**, and **GB CoS v2.1 Review (`79/100`)** is mapped below to its concrete, server-enforced specification and named unit test:

| SAG Addendum (v2 58/100) | SAG v2.1 (74/100) | GB CoS v2.1 (79/100) | Requirement Summary | Plan.v2.2 Section & Concrete Mechanism | Named Verification Gate / Test |
| :---: | :---: | :---: | :--- | :--- | :--- |
| **SAG #1** | Closed + Facility Clash | **MUST-EDIT 4** | Server-enforced `CC` â†” `country_era` â†” `year` agreement validator; resolve `FAC=M` (Manila) vs `FAC=MO` (Mexico City) collision; re-issue Vector #12 (`NAC1.CN.FS.1D.SPAN8R.1798.MO.BASE.P`). | **Â§2.1 & Â§2.3.1** (`validate_cc_era_year_agreement` + `FAC=MO` added to grammar/regex + Vector #12 re-issued with `CHK=P`). | `numista_tests/test_nac1_validator.py::test_cc_era_year_agreement` |
| **SAG #2** | **S1** | **MUST-EDIT 1** | Single atomic Firestore transaction for `+ Add to Collection`; server-side `validate_nac1`; read catalog doc inside txn to derive `kind` & snapshot server-side; reject client-supplied `kind`/`slot`/`tier`; race-safe `_SLOT{N}` allocation via per-`(uid, nac_code)` counter doc in txn; `Idempotency-Key` replay protection. | **Â§3.3** (Full Python `@firestore.transactional` implementation + `Idempotency-Key` ledger + client field rejection). | `numista_tests/test_catalog_add_race.py::test_two_tab_concurrent_add_and_idempotent_retry` |
| **SAG #3** | **S2 & S8** | **MUST-EDIT 2** | Close `allow list: if true` scrape/download bypass; enforce Firebase App Check + Cloud Armor WAF + Cloud Run paginated browse/search API; public docs expose watermarked thumbs only (full-res behind authenticated signed URL); define Cloud Monitoring alert thresholds + owner; label `"50 searches/day"` & free download res as **`[PENDING ERIC â€” Agent Proposal]`**. | **Â§2.4, Â§5.2, & Â§6.2â€“6.3** (Firestore `list` disabled for raw unauth SDK; Cloud Run `/api/v1/catalog/search` + App Check + Cloud Armor + Monitoring Alert Table). | `numista_tests/test_catalog_collection_routing.py::test_guest_rate_limit_and_download_guard` |
| **SAG #4** | **S3** | **MUST-EDIT 3** | ETL & Pydantic schema validator: `mintage_official_mint != null` requires $\ge 1$ `TIER_A_GOV` citation from official U.S. Mint / Treasury / BEP / FRASER / NARA authority and explicitly rejects PCGS, NGC, Red Book, Whitman, Greysheet, or Numista domains. | **Â§2.3.2** (`validate_tier_a_mintage_authority` Pydantic `@model_validator` + domain blocklist). | `numista_tests/test_catalog_schema.py::test_tier_a_mintage_validator_rejects_commercial_sources` |
| **SAG #5** | Closed | **MUST-EDIT 8** | Mark `NAC1` Crockford-32 algorithm & vectors **FROZEN**; fix regex `<CHK>` class from `[0-9A-HJ-NP-TV-Z]` (which admitted `L`) to `[0-9A-HJ-KM-NP-TV-Z]`; correct the `% 37` then `% 32` mathematical rationale text. | **Â§2.2** (FROZEN banner, exact 32-char regex excluding `I,L,O,U`, accurate residue weight explanation). | `numista_tests/test_nac1_validator.py::test_regex_rejects_excluded_crockford_chars_I_L_O_U` |
| **SAG #6** | **S4** | **MUST-EDIT 5** | Exhaustive forbidden Mint FAIL-FIX / `p7-gate` path prefix list; reconcile allowlist with `firestore.rules` and `tier_gatekeeper.py` via explicit Scoped Gatekeeper Exception protocol. | **Â§9.1 & Â§9.2** (Exhaustive Forbidden Path Prefixes table + reconciled allowlist & scoped review exception). | **Â§9.2 Gate 1** (`git diff` forbidden-prefix & allowlist check) |
| **SAG #7** | Closed | **MUST-EDIT 9** | Phase 2 includes common private medals (`CLASS=PRV`); resolve `KIND=TK` (tokens) vs `KIND=MD/PRV` (private medals) cleanly; fix 1787 Fugio Cent state tag to `"CONTINENTAL"` (`Pre-Federal Â· Continental Congress`); schedule mobile slab/receipt scan in Phase 2. | **Â§2.1 #2, Â§4.2, & Â§7.3** (`KIND=TK` for tokens vs `KIND=MD` + `CLASS=PRV` for private medals; Fugio tagged `CONTINENTAL`; slab/receipt scan scheduled in Phase 2). | `numista_tests/test_nac1_validator.py` & `test/nac_code_parser_test.dart` |
| **SAG #8** | **S6** | **MUST-EDIT 6** | Replace fixed calendar dates (1 Nov / 27 Nov) with **Evidence-Gated Ship Table** (1 Nov / 27 Nov marked aspirational earliest windows only; gated on Mint FT PASS, CR Evidence Pack clearance, Founder fold YES, and `origin/main` unlock). | **Â§1.2 & Â§7.1** (Mandatory Ship-Gate Table Aâ€“D governing Phase 1A, Phase 1B, and Phase 2). | Governance Gate Aâ€“D sign-off |
| **SAG #9** | **S5** | **MUST-EDIT 7** | Zero user PII in public `us_numismatics_catalog` docs or user `catalog_snapshot` objects; contributor credit uses opaque attribution IDs (`"Numista.AI Verified Community Archive (CC0 #C-0104)"`) unless explicit institutional credit. | **Â§2.3.3 & Â§3.3** (`validate_zero_pii_public_catalog` validator rejecting `@`, UIDs, or raw `"Verified Contributor: <username>"` strings). | `numista_tests/test_catalog_schema.py::test_public_catalog_and_snapshot_reject_user_pii` |
| â€” | **S7** | **MUST-EDIT 9** | **"Free trial up to 5 items"** for free registered accounts is **`[FOUNDER-CONFIRMED â€” Eric 29 Oct 9:23 AM ET]`** (drop `PENDING` label) and is **server-enforced** inside the add transaction. | **Â§3.3 & Â§6.2** (Transactional check `user_doc.catalog_trial_count < 5` for `FREE` tier; raises `HTTP 402 FREE_TRIAL_LIMIT_EXCEEDED`). | `numista_tests/test_catalog_collection_routing.py::test_free_trial_5_item_server_enforcement` |

---

## 1. Executive Summary & Product Vision

### 1.1 The Directive
To commemorate the 250th anniversary of the United States (the Semiquincentennial arc), Numista.AI will deploy an authoritative, academic-grade **U.S. Numismatics Master Catalog** at `https://numista.ai/catalog`. The catalog spans every American-authorized coin, bank note, medal, and token issued from **July 4, 1776 through October 28, 2026**, as well as foreign legal-tender specie that circulated extensively under Congressional acts in early America (`1776â€“1857`).

### 1.2 Core Product Pillars & Evidence-Gated Release Alignment
1. **Evidence-Gated Phased Scope (SAG #8 / S6 / GB MUST-EDIT 6):**
   Calendar dates (`November 1, 2026` and `November 27, 2026`) are **aspirational earliest windows only**. No phase may promote to production (`origin/main`) until all four ship gates in **Â§7.1** are satisfied:
   - **Phase 1A (Earliest Aspirational Window: Nov 1, 2026 â€” Gated on Mint FT PASS + CR Evidence Clearance + `main` Unlock):** Core verified U.S. Federal circulating & bullion coins (`1792â€“2026`), anchored by the 25 verified Evidence Packs (`AWQ`, `ASE`, `ATB`, `MORGAN`, `PEACE`, `STQ`, `AID`, etc.).
   - **Phase 1B (Earliest Aspirational Window: Nov 27, 2026 â€” Gated on CR Evidence Clearance + Founder Fold YES per Batch):** Expansion to verified U.S. Federal circulating coins and major U.S. Federal paper currency (`1861â€“2026`) cleared by Catalog Research once Founder lifts specific batches from HOLD (`586+588+589+590`), plus U.S.-Philippines territorial coinage (`CC="PF"`, **INCLUDE** per standing rule). *(Note: Founder's 29 Oct 9:13 AM ET YES in `NET-645` authorizes folding only `1921-S Walker = 548,000` and `1955-P Franklin = 2,876,381`.)*
   - **Phase 2 (Q1 2027 Expansion â€” Evidence-Gated):** Pre-Federal & Colonial issues (`1776â€“1791`, `CC="CO"`), Foreign Specie circulating in early America (`1776â€“1857`, `CC="FS"`), Official U.S. Mint & Common Private Medals (`KIND="MD"`, `CLASS="OFF"` and `CLASS="PRV"`), Historic/Civil War/Hard Times Tokens (`KIND="TK"`), Mobile Companion Camera Quick-Add + Slab Barcode/NFC & Dealer Receipt OCR Scanning, and Multi-Modal Visual AI Photo Matching (`Scan AI`).
2. **Search Modality by Phase:**
   - **Phase 1:** Instant **Full-Text & Faceted Search** across title, year, series, denomination, mint facility (`FAC`), and external concordance IDs (Red Book, Friedberg, PCGS, NGC).
   - **Phase 2:** Multi-modal visual AI photo matching and microscope die-attribution.
3. **Desktop & Tablet First Browse / Mobile Companion (~90% Web / ~10% App):**
   - **Desktop & Tablet Primary Surface:** Deep catalog browsing, faceted filtering, multi-column grid comparisons, and archival inspection are engineered specifically for **Desktop Web and Tablet** (`â‰¥1280px` primary master grid + 4-column sticky inspector, collapsing to responsive tablet views).
   - **Mobile Companion (~10% App Scope):** The mobile application is a focused, high-utility companion dedicated to **phone-only physical tasks**: quick camera additions to personal collections, grading slab barcode/NFC scanning, and dealer receipt OCR capture (explicitly scheduled in **Phase 2, Â§7.3**). Full catalog browsing is not shoehorned into a cramped 2-column mobile phone feed.
4. **Resilient Dual-Sided Assets & Missing Image Policy:**
   - Verified numismatic records are **never** withheld due to missing photography. Missing images render a deterministic vector `DualSidedPlaceholder` while preserving 100% of metadata, dual-tier mintages, and primary citations.
5. **Non-Destructive Multi-Collection Isolation:**
   - `us_numismatics_catalog` is a **client write-locked** reference collection. User collection additions execute inside a single atomic server transaction (**Â§3.3**) that reads `kind` from the catalog document server-side and routes strictly by `kind` (`CN` â†’ `users/{uid}/coins`, `BN` â†’ `users/{uid}/currency`, `MD`/`TK`/`ST` â†’ `users/{uid}/world_items`) via whole-document creation (`txn.create()`, `merge=false`), protecting Estate PDFs (`passport_pdf_generator.py`) and BigQuery ETL (`numista_bq_loader_job`).
6. **Zero Cross-Track Interference & FinOps Lock:**
   - Work executes strictly on branch `dev` (`origin/main` is locked). Mint FAIL-FIX (`NET-641` on `p7-gate`) remains Day #1 priority. This catalog integration plan incurs **\$0** unapproved spend.

---

## 2. Universal Identifier Grammar (`NAC1`), Frozen Checksum & Schema Contracts

### 2.1 The `NAC1` Deterministic Grammar
Every catalog type is governed by a proprietary, human-readable, machine-parsable **NAC1 (Numista.AI Catalog v1)** identifier:

$$\text{NAC1} \,.\, \langle\text{KIND}\rangle \,.\, \langle\text{CC}\rangle \,.\, \langle\text{CLASS}\rangle \,.\, \langle\text{SERIES}\rangle \,.\, \langle\text{DATE}\rangle \,.\, \langle\text{FAC}\rangle \,.\, \langle\text{VAR}\rangle \,.\, \langle\text{CHK}\rangle$$

```bnf
nac          ::= "NAC1." kind "." cc "." class "." series "." date "." fac "." var "." chk
kind         ::= "CN" | "BN" | "MD" | "TK" | "ST"
cc           ::= "US" | "CO" | "PF" | "CS" | "FS"
class        ::= coin_class | note_class | medal_class | token_class
coin_class   ::= "HC" | "1C" | "2C" | "3C" | "5C" | "10C" | "20C" | "25C" | "50C" | "1D"
               | "G1" | "G2D5" | "G3" | "G5" | "G10" | "G20" | "G50" | "G100" | "1P" | "8R" | "BUL"
note_class   ::= ("FRN" | "FRBN" | "SC" | "GC" | "TN" | "LT" | "NAT" | "DEM" | "CSA" | "CLC") denom
denom        ::= "1" | "2" | "5" | "10" | "20" | "50" | "100" | "500" | "1000" | "5000" | "10000" | "100000"
medal_class  ::= "OFF" | "PRV" | "CONG" | "PRES" | "ASSAY" | "COMM"
token_class  ::= "PRV" | "HTT" | "CWT" | "TRD"
series       ::= 2*12 (ALPHA | DIGIT)
date         ::= YYYY | YYYY ("A"-"Z") | "ND" | "XXXX"
fac          ::= "P" | "D" | "S" | "W" | "CC" | "O" | "C" | "DD" | "M" | "MO" | "L" | "PTS" | "PH" | "BEP" | "NARA" | "XX"
var          ::= "BASE" | 2*12 (ALPHA | DIGIT)
chk          ::= crockford32_char
```

#### Critical Segment Rules & Disambiguation
1. **Polity (`CC`) Disambiguation & Server-Enforced Era/Year Bounds (Founder Q1 & Q2 Rulings, SAG #1, GB MUST-EDIT 4):**
   - **`US`**: United States Federal issues (`country_era == "FEDERAL" | "EARLY_FEDERAL"`, `1792 <= year <= 2026`).
   - **`CO`**: Colonial & Pre-Federal issues (`country_era == "PRE_FEDERAL"`, `1776 <= year <= 1792`, e.g., 1787 Fugio Cent under Continental Congress authority). Separated from territorial codes to eliminate double-booking.
   - **`PF`**: U.S.-Philippines Territorial issues (`country_era == "US_PHILIPPINES"`, `1903 <= year <= 1946`, explicitly **INCLUDED** per standing rule).
   - **`CS`**: Confederate States of America (`country_era == "CONFEDERATE"`, `1861 <= year <= 1865`).
   - **`FS`**: Foreign Specie circulating as legal tender in early America (`country_era == "FOREIGN_CIRCULATING"`, `1776 <= year <= 1857` â€” demonetized by the Coinage Act of Feb 21, 1857). Lives in the dedicated "Foreign Coins" catalog section per Founder Q2 ruling.
2. **Medals (`KIND="MD"`) vs. Tokens (`KIND="TK"`) Clean Boundary (SAG #7, GB MUST-EDIT 9):**
   - **`KIND="MD"` (Medals):** Non-denominated medallic issues with no merchant-exchange face value. Includes:
     - `CLASS="OFF"`: Official U.S. Mint National / Treasury medals.
     - `CLASS="PRV"`: **Common Private Medals** (world's fair/exposition medals, private commemorative/award medals, society medals â€” confirmed **IN SCOPE for Phase 2**).
     - `CLASS="CONG" | "PRES" | "ASSAY" | "COMM"`: Congressional Gold, Presidential series, Annual Assay Commission, and statutory commemorative medals.
   - **`KIND="TK"` (Tokens):** Private or merchant exchange tokens bearing an explicit or implied trade/monetary denomination (`CLASS="CWT"` Civil War store cards/tokens, `CLASS="HTT"` Hard Times tokens, `CLASS="TRD"` merchant trade tokens, `CLASS="PRV"` general private tokens â€” **IN SCOPE for Phase 2**). Both `MD` and `TK` route to `users/{uid}/world_items` (**Â§3.1**).
3. **Facility (`FAC`) vs. Struck Mint Mark Separation & Manila (`M`) vs. Mexico City (`MO`) Disambiguation (GB MUST-EDIT 4):**
   - `FAC` encodes the **striking city/facility**, never whether a mint mark letter is physically present on the die.
   - **Dahlonega vs. Denver Disambiguation:** Denver = **`D`**; Dahlonega (1838â€“1861 gold) = **`DD`**; Charlotte = **`C`**; Carson City = **`CC`**; New Orleans = **`O`**.
   - **Manila (`M`) vs. Mexico City (`MO`) Disambiguation:**
     - **`M`** (or `PH`): **Manila Mint** (1920â€“1941, valid **only** with `CC="PF"` U.S.-Philippines).
     - **`MO`**: **Mexico City Mint (`Mo` mint mark)** (valid with `CC="FS"` Foreign Specie, e.g., 1798 Spanish Colonial 8 Reales `NAC1.CN.FS.1D.SPAN8R.1798.MO.BASE.P`). Additional foreign specie mints: `L` (Lima), `PTS` (PotosÃ­).
   - **No-Mark Philadelphia Rule:** A Philadelphia coin struck without a mint mark (e.g., 1921 Morgan Dollar, 1794 Large Cent) uses `FAC = "P"` with schema fields `mint_mark_on_coin: false` and `mint_mark: null`. A marked Philadelphia coin (e.g., 1942-P War Nickel, 1980-P Quarter) uses `FAC = "P"`, `mint_mark_on_coin: true`, `mint_mark: "P"`.
   - **`XX` Reserved for Non-U.S.-Mint / Private Contracts:** Used only when struck outside sovereign mints / BEP (e.g., 1787 Fugio Cent under New Haven contract for Continental Congress), paired with `facility_note`.

---

### 2.2 FROZEN Deterministic Checksum Algorithm & Test Vectors (SAG #5 / GB MUST-EDIT 8)

> [!IMPORTANT]
> **FROZEN ALGORITHM & VECTORS DECLARATION:**
> The `compute_nac1_chk` algorithm and canonical test vectors below are **FROZEN**. Any change to the multiplier, prime modulus, or alphabet mapping is strictly forbidden so that minted `NAC1` primary keys and external citations remain permanently immutable.

Client-invented or malformed `nac_code` strings are rejected at both the Python API boundary and the ETL pipeline.

* **Payload:** All ASCII uppercase characters preceding the final `.CHK` separator (e.g., `NAC1.CN.US.1D.MORGAN.1881.S.BASE`).
* **Alphabet:** Crockford Base32 (`0123456789ABCDEFGHJKMNPQRSTVWXYZ`, length 32; excludes visually ambiguous `I`, `L`, `O`, `U`).
* **Mathematical Specification (Corrected Rationale per GB MUST-EDIT 8):**
  The checksum computes a polynomial rolling hash over the UTF-8 byte sequence using multiplier `33` modulo prime `37` (`h = (h * 33 + b) % 37`), followed by a final index projection `CROCKFORD_32[h % 32]`. Because `37` is prime, every character position contributes non-trivially without power-of-two bit masking; the final `h % 32` reduction maps residues `0..4` (Crockford symbols `0..4`) with weight `2/37` and residues `5..31` with weight `1/37`. This exact two-step reduction is **frozen** to preserve 100% compatibility with all published test vectors.
* **Regex Character Class Fix (GB MUST-EDIT 8):**
  The final `<CHK>` capture group uses the exact 32-symbol Crockford character class `([0-9A-HJ-KM-NP-TV-Z])`, which explicitly excludes `I`, `L`, `O`, and `U` (fixing the v2.1 regex typo `[0-9A-HJ-NP-TV-Z]` that inadvertently admitted `L`).

```python
import re

CROCKFORD_32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
NAC1_REGEX = re.compile(
    r"^(NAC1\.(CN|BN|MD|TK|ST)\.(US|CO|PF|CS|FS)\.[A-Z0-9]{2,8}\.[A-Z0-9_]{2,12}\."
    r"([0-9]{4}[A-Z]?|ND|XXXX)\.(P|D|S|W|CC|O|C|DD|M|MO|L|PTS|PH|BEP|NARA|XX)\."
    r"[A-Z0-9_]{2,12})\.([0-9A-HJ-KM-NP-TV-Z])$"
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

#### Canonical FROZEN Test Vectors (14/14 100% Machine Verified)
*(Note: Vector #12 is re-issued with `FAC=MO` for Mexico City Mint (`CHK=P`), resolving the Manila `FAC=M` collision per GB MUST-EDIT 4. Vector #14 adds the explicit `KIND=TK` Civil War Token vector alongside Vector #13 `KIND=MD/PRV` per GB MUST-EDIT 9.)*

| # | Issue Description | Payload | `CHK` | Full Verified `NAC1` |
| :--- | :--- | :--- | :---: | :--- |
| 1 | 1787 Fugio Cent (Pre-Federal Continental Congress, `CC=CO`) | `NAC1.CN.CO.1C.FUGIO.1787.XX.BASE` | `K` | `NAC1.CN.CO.1C.FUGIO.1787.XX.BASE.K` |
| 2 | 1838-D Dahlonega \$5 Half Eagle (`FAC=DD`, `MM=D`) | `NAC1.CN.US.G5.LIBCAP.1838.DD.BASE` | `3` | `NAC1.CN.US.G5.LIBCAP.1838.DD.BASE.3` |
| 3 | 1881-S Morgan Silver Dollar | `NAC1.CN.US.1D.MORGAN.1881.S.BASE` | `E` | `NAC1.CN.US.1D.MORGAN.1881.S.BASE.E` |
| 4 | 1921 Morgan Dollar (Phila, `mint_mark_on_coin=false`) | `NAC1.CN.US.1D.MORGAN.1921.P.BASE` | `4` | `NAC1.CN.US.1D.MORGAN.1921.P.BASE.4` |
| 5 | 1937-D Buffalo Nickel (3-Legged Variety) | `NAC1.CN.US.5C.BUFFALO.1937.D.3LEG` | `3` | `NAC1.CN.US.5C.BUFFALO.1937.D.3LEG.3` |
| 6 | 2022-P Maya Angelou Quarter (`default_face=REVERSE`) | `NAC1.CN.US.25C.AWQ.2022.P.MAYA` | `Z` | `NAC1.CN.US.25C.AWQ.2022.P.MAYA.Z` |
| 7 | 2024-W American Silver Eagle Proof | `NAC1.CN.US.1D.ASE.2024.W.PRF` | `S` | `NAC1.CN.US.1D.ASE.2024.W.PRF.S` |
| 8 | Series 2017A \$1 Federal Reserve Note (BEP) | `NAC1.BN.US.FRN1.FED.2017A.BEP.BASE` | `6` | `NAC1.BN.US.FRN1.FED.2017A.BEP.BASE.6` |
| 9 | 1890 \$1,000 Treasury Note ("Watermelon") | `NAC1.BN.US.TN1000.TREAS.1890.BEP.WM` | `C` | `NAC1.BN.US.TN1000.TREAS.1890.BEP.WM.C` |
| 10 | 1923-P Calvin Coolidge Presidential Medal | `NAC1.MD.US.PRES.PRES.1923.P.COOL` | `W` | `NAC1.MD.US.PRES.PRES.1923.P.COOL.W` |
| 11 | 1903-S U.S.-Philippines 1 Peso (`FAC=S`, `CC=PF`) | `NAC1.CN.PF.1P.PHL1P.1903.S.BASE` | `3` | `NAC1.CN.PF.1P.PHL1P.1903.S.BASE.3` |
| 12 | 1798-Mo Spanish-American 8 Reales (`CC=FS`, `FAC=MO` Mexico City) | `NAC1.CN.FS.1D.SPAN8R.1798.MO.BASE` | `P` | `NAC1.CN.FS.1D.SPAN8R.1798.MO.BASE.P` |
| 13 | 1863 Private Patriotic / Exposition Medal (`KIND=MD`, `CLASS=PRV`) | `NAC1.MD.US.PRV.CWT.1863.XX.BASE` | `H` | `NAC1.MD.US.PRV.CWT.1863.XX.BASE.H` |
| 14 | 1863 Civil War Store Card Token (`KIND=TK`, `CLASS=PRV`) | `NAC1.TK.US.PRV.CWT.1863.XX.BASE` | `T` | `NAC1.TK.US.PRV.CWT.1863.XX.BASE.T` |

---

### 2.3 Firestore Reference Schema (`us_numismatics_catalog`) & Server Validators
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
  denomination_class: string;        // "1D", "25C", "SC5", "G5", "PRV"
  series: string;                    // "MORGAN", "AWQ", "SILV", "FUGIO"
  catalog_version: number;           // Monotonic integer incremented on verified metadata/mintage updates
  last_verified_at: string;          // ISO-8601 UTC timestamp of latest primary source verification

  // 2. Chronology, Facility & Display
  year: number;                      // Integer sort key (1776 to 2026)
  year_display: string;              // "1881-S", "1838-D (Dahlonega)", "1798-Mo (Mexico City)"
  facility_code: "P" | "D" | "S" | "W" | "CC" | "O" | "C" | "DD" | "M" | "MO" | "L" | "PTS" | "PH" | "BEP" | "NARA" | "XX";
  mint_mark_on_coin: boolean;        // False for no-mark Phila (even though facility_code == "P")
  mint_mark: string | null;          // Exact letter struck on die ("S", "D", "CC", "Mo", or null)
  facility_note: string | null;      // e.g. "New Haven contract for Continental Congress" when facility_code == "XX"
  title: string;                     // "1881-S Morgan Silver Dollar"
  subtitle: string;                  // "Liberty Head / Heraldic Eagle Reverse"

  // 3. Visual Assets, Thumbnail Separation & Zero-PII Attribution (SAG #3, #9)
  default_face: "OBVERSE" | "REVERSE"; // Side that uniquely identifies the issue (e.g. "REVERSE" for AWQ/STQ)
  obverse_thumb_url: string | null;  // Public web display WebP thumbnail (<= 600px, watermarked/rate-limited CDN)
  reverse_thumb_url: string | null;  // Public web display WebP thumbnail (<= 600px, watermarked/rate-limited CDN)
  obverse_image_url: string | null;  // Protected archival asset path (served ONLY via authenticated signed URL)
  reverse_image_url: string | null;  // Protected archival asset path (served ONLY via authenticated signed URL)
  has_obverse_image: boolean;
  has_reverse_image: boolean;
  image_source_credit: string | null;// ZERO USER PII: "Smithsonian NNC (CC0)", "U.S. Mint", or "Numista.AI Verified Community Archive (CC0 #C-0104)"
  image_tier: "MUSEUM" | "PUBLIC_DOMAIN" | "VERIFIED_COMMUNITY" | "NONE"; // Strict hierarchy per Founder Q3
  image_license_type: "CC0" | "US_GOV_PUBLIC_DOMAIN" | "INSTITUTIONAL_PERMISSION" | "COMMUNITY_VERIFIED_CC0" | "NONE";

  // 4. Authoritative Mintages (Dual-Tier Convention â€” Validated per Â§2.3.2)
  mintage_official_mint: number | null; // Tier-A ONLY: US Mint Annual Reports / BEP Ledgers / Treasury Warrants
  mintage_commercial: number | null;    // Tier-B: Numismatic trade/reference consensus (Red Book / Friedberg / PCGS)
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
    pcgs_number?: number | null;          // Crosswalk only â€” NEVER used as Tier-A mintage source
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

#### 2.3.1 Server-Enforced `CC` â†” `country_era` â†” `year` & Facility Agreement Validator (SAG #1 / GB MUST-EDIT 4)
Every `CatalogItem` ingested by ETL or served by `catalog_models.py` enforces a strict cross-field invariant (`validate_cc_era_year_agreement`):
1. **`CC == "CO"` (Colonial / Pre-Federal):** Requires `country_era == "PRE_FEDERAL"`, `1776 <= year <= 1792`, and `facility_code not in {"M", "PH", "MO", "L", "PTS"}`.
2. **`CC == "PF"` (U.S.-Philippines Territorial):** Requires `country_era == "US_PHILIPPINES"`, `1903 <= year <= 1946`, and `facility_code in {"P", "D", "S", "M", "PH"}`.
3. **`CC == "CS"` (Confederate States):** Requires `country_era == "CONFEDERATE"` and `1861 <= year <= 1865`.
4. **`CC == "FS"` (Foreign Specie Legal Tender):** Requires `country_era == "FOREIGN_CIRCULATING"`, `1776 <= year <= 1857` (demonetized Feb 21, 1857), and `facility_code in {"MO", "L", "PTS", "XX"}` (`FAC="M"` is strictly rejected on `CC="FS"` to prevent Manila vs. Mexico City conflation).
5. **`CC == "US"` (U.S. Federal):** Requires `country_era in {"EARLY_FEDERAL", "FEDERAL"}`, `1792 <= year <= 2026`, and `facility_code not in {"M", "PH", "MO", "L", "PTS"}`.

#### 2.3.2 Server-Enforced Tier-A Official Mintage Validator (SAG #4 / S3 / GB MUST-EDIT 3)
To guarantee that commercial estimates (PCGS, NGC, Red Book, Greysheet) never contaminate `mintage_official_mint`, `CatalogItem` enforces `validate_tier_a_mintage_authority` at the Pydantic model and ETL gate:

```python
FORBIDDEN_TIER_A_TOKENS = (
    "pcgs", "coinfacts", "ngc", "ngccoin", "red book", "redbook",
    "yeoman", "whitman", "greysheet", "cdn", "numista", "heritage", "ha.com", "cointrackers"
)
REQUIRED_TIER_A_AUTHORITIES = (
    "u.s. mint", "us mint", "director of the mint", "treasury",
    "bureau of engraving and printing", "bep", "fraser", "national archives", "nara", "statutes at large"
)

@model_validator(mode="after")
def validate_tier_a_mintage_authority(self) -> "CatalogItemRecord":
    if self.mintage_official_mint is not None:
        tier_a_cites = [c for c in self.primary_citations if c.tier == "TIER_A_GOV"]
        if not tier_a_cites:
            raise ValueError(
                f"{self.nac_code}: mintage_official_mint={self.mintage_official_mint} requires "
                "at least one TIER_A_GOV citation from U.S. Mint / Treasury / BEP / NARA."
            )
        for c in tier_a_cites:
            combined = f"{c.source_name} {c.citation_text} {c.document_url or ''}".lower()
            if any(bad in combined for bad in FORBIDDEN_TIER_A_TOKENS):
                raise ValueError(
                    f"{self.nac_code}: Commercial source '{c.source_name}' is strictly forbidden "
                    "as a TIER_A_GOV citation for mintage_official_mint."
                )
            if not any(auth in combined for auth in REQUIRED_TIER_A_AUTHORITIES):
                raise ValueError(
                    f"{self.nac_code}: TIER_A_GOV citation '{c.source_name}' must cite official "
                    "U.S. Mint / Treasury / BEP / FRASER / NARA authority."
                )
    return self
```

#### 2.3.3 Zero User PII Validator for Public Docs & Snapshots (SAG #9 / S5 / GB MUST-EDIT 7)
Public catalog documents (`us_numismatics_catalog/{nac_code}`) and embedded user `catalog_snapshot` objects must contain **zero user PII** (no contributor usernames, email addresses, Firebase UIDs, or personal display names):
- Community-contributed images verified under Founder Q3 must format `image_source_credit` using an **opaque archival attribution ID**: e.g., `"Numista.AI Verified Community Archive (CC0 #C-0104)"`.
- `CatalogItem` and `CatalogSnapshot` run `validate_zero_pii_public_catalog`, which rejects any `image_source_credit` containing `@` (email), `Verified Contributor:` followed by a handle, `uid:`, or raw user identifiers.

---

### 2.4 Firestore Security Rules & Public Surface Lockdown (SAG #3 / S2 / GB MUST-EDIT 2)
In Plan.v2.1, `allow list: if true` allowed unauthenticated scrapers to dump the entire `us_numismatics_catalog` collection directly from Firestore, bypassing Cloud Run rate limits (`HTTP 429`) and exposing `obverse_image_url` / `reverse_image_url` to guests in violation of Founder Q4.

**Plan.v2.2 closes this bypass completely:**
1. **Direct Client SDK `list` Disabled for Guests:** Public guest browsing and search are served **exclusively through the Cloud Run paginated API** (`GET /api/v1/catalog/search`), where Firebase App Check, Cloud Armor IP rate limiting, and the guest search quota are enforced.
2. **Authenticated + App Check Gate on Firestore Reads:** Even for authenticated clients, direct Firestore reads require a valid **Firebase App Check token** (`request.app_check_token != null`), and full-resolution archival URLs (`obverse_image_url` / `reverse_image_url`) are stripped from public payloads and served only via short-lived CDN signed URLs on `GET /api/v1/catalog/{nac_code}/image-download` for authenticated accounts.
3. **Zero Client Writes:** `allow create, update, delete: if false;` remains absolute.

```javascript
// firestore.rules excerpt (Scoped addition â€” see Â§9.1 Exception Protocol)
match /us_numismatics_catalog/{nac_code} {
  // Single-doc lookup allowed only with valid Firebase App Check attestation;
  // Unauthenticated bulk collection listing (list) is BLOCKED at Firestore level
  // so all browse/search traffic passes through Cloud Run rate-limiting & Cloud Armor.
  allow get: if request.app_check_token != null;
  allow list: if request.auth != null && request.app_check_token != null
              && request.query.limit <= 50;

  // Strictly forbidden from client SDK; only Admin SDK batch ETL may write
  allow create, update, delete: if false;
}
```

---

## 3. Multi-Collection Write Contract, Server Transaction & Photo Toggle

### 3.1 Conditional Routing by Server-Read `kind`
When an authenticated user clicks `+ Add to My Collection` on a catalog card, the request is handled by `POST /api/v1/collection/from-catalog`. **The server never trusts client-supplied `kind`, `slot`, or `tier` fields.** Instead, the server reads `numismatics_catalog/{nac_code}` inside the transaction and routes strictly by the catalog document's `kind`:

| Catalog `kind` (Server-Read) | Target Firestore Collection | Target Schema Contract | Downstream Consumers |
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
   - `use_personal_photo: boolean` (Default `true` if custom photos uploaded; togglable to `false` to display the catalog stock image instead via `PATCH /api/v1/collection/catalog-photo-toggle`).
2. The portfolio UI provides a one-click toggle: **`[ðŸ“¸ My Specimen Photo]` vs `[ðŸ›ï¸ Catalog Stock Photo]`**.

### 3.3 Atomic Server Transaction, Race-Safe `_SLOT{N}` Allocation, Idempotency & 5-Item Free Trial Gate (SAG #2, S1, S7 / GB MUST-EDIT 1)
To prevent two-tab race conditions, duplicate slot overwrites, or client-spoofed `kind`/`slot`/`tier` fields, `POST /api/v1/collection/from-catalog` executes a **single atomic Firestore transaction**:

1. **Client Payload Restriction:** The request schema (`CatalogCollectionAddRequest`) accepts **only** `nac_code`, `idempotency_key` (or `Idempotency-Key` HTTP header), and optional user acquisition notes (`grade_note`, `purchase_price`, `custom_obverse_image_url`, `custom_reverse_image_url`, `use_personal_photo`). Any client payload containing `kind`, `slot`, `slot_index`, `target_collection`, or `user_tier` is **rejected with `HTTP 422 Unprocessable Entity`** (`extra="forbid"`).
2. **Step-by-Step Transactional Execution:**

```python
@firestore.transactional
def _execute_catalog_add_txn(
    txn: firestore.Transaction,
    db: firestore.Client,
    uid: str,
    nac_code: str,
    idempotency_key: str,
    req: CatalogCollectionAddRequest,
) -> dict:
    # 1. Validate NAC1 grammar & frozen Crockford-32 check digit server-side
    if not validate_nac1(nac_code):
        raise ValueError(f"INVALID_NAC1_CODE: {nac_code}")

    # 2. Check Idempotency-Key ledger inside the transaction (safe retry without _SLOT3)
    idem_ref = db.document(f"users/{uid}/catalog_idempotency/{idempotency_key}")
    idem_snap = idem_ref.get(transaction=txn)
    if idem_snap.exists:
        saved = idem_snap.to_dict()
        return {**saved, "idempotent_replay": True}

    # 3. Read authoritative catalog document inside the transaction (never trust client kind)
    cat_ref = db.document(f"us_numismatics_catalog/{nac_code}")
    cat_snap = cat_ref.get(transaction=txn)
    if not cat_snap.exists:
        raise LookupError(f"CATALOG_ITEM_NOT_FOUND: {nac_code}")
    cat_data = cat_snap.to_dict()

    # 4. Read user entitlement doc inside the transaction & enforce Founder-confirmed 5-item Free Trial
    user_ref = db.document(f"users/{uid}")
    user_snap = user_ref.get(transaction=txn)
    user_data = user_snap.to_dict() if user_snap.exists else {"subscription_tier": "FREE", "catalog_trial_count": 0}
    tier = user_data.get("subscription_tier", "FREE")
    trial_count = int(user_data.get("catalog_trial_count", 0))
    if tier == "FREE" and trial_count >= 5:
        raise PermissionError("FREE_TRIAL_LIMIT_EXCEEDED: Free accounts are limited to 5 catalog additions.")

    # 5. Derive target collection strictly from server-read catalog kind
    server_kind = cat_data["kind"]
    target_collection = KIND_TO_COLLECTION[server_kind]  # CN->coins, BN->currency, MD/TK/ST->world_items

    # 6. Allocate race-safe _SLOT{N} via per-(uid, nac_code) counter doc inside the transaction
    slug = nac_code.replace(".", "_")
    counter_ref = db.document(f"users/{uid}/catalog_slot_counters/{slug}")
    counter_snap = counter_ref.get(transaction=txn)
    next_slot = (int(counter_snap.to_dict().get("last_slot", 0)) + 1) if counter_snap.exists else 1
    doc_id = f"{slug}_SLOT{next_slot}"
    target_ref = db.document(f"users/{uid}/{target_collection}/{doc_id}")

    # 7. Build zero-PII immutable catalog_snapshot (catalog reference fields ONLY)
    catalog_snapshot = {
        "nac_code": nac_code,
        "catalog_version": cat_data["catalog_version"],
        "title_at_acquire": cat_data["title"],
        "kind": server_kind,
        "cc": cat_data["cc"],
        "year": cat_data["year"],
        "facility_code": cat_data["facility_code"],
        "mintage_official_at_acquire": cat_data.get("mintage_official_mint"),
        "obverse_thumb_url_at_acquire": cat_data.get("obverse_thumb_url"),
        "reverse_thumb_url_at_acquire": cat_data.get("reverse_thumb_url"),
    }

    # 8. Atomic whole-document creation (txn.create fails closed if doc_id already exists)
    txn.set(counter_ref, {"nac_code": nac_code, "last_slot": next_slot})
    txn. set(user_ref, {"catalog_trial_count": trial_count + 1}, merge=True)
    txn.create(target_ref, {
        "doc_id": doc_id,
        "nac_code": nac_code,
        "kind": server_kind,
        "slot_index": next_slot,
        "target_collection": target_collection,
        "use_personal_photo": bool(req.custom_obverse_image_url or req.custom_reverse_image_url) if req.use_personal_photo is None else req.use_personal_photo,
        "custom_obverse_image_url": req.custom_obverse_image_url,
        "custom_reverse_image_url": req.custom_reverse_image_url,
        "catalog_snapshot": catalog_snapshot,
    })
    result = {
        "uid": uid,
        "nac_code": nac_code,
        "kind": server_kind,
        "target_collection": target_collection,
        "doc_id": doc_id,
        "doc_path": f"users/{uid}/{target_collection}/{doc_id}",
        "slot_index": next_slot,
        "idempotency_key": idempotency_key,
        "idempotent_replay": False,
    }
    txn.create(idem_ref, result)
    return result
```

3. **Named Concurrency & Idempotency Test (`numista_tests/test_catalog_add_race.py`):**
   - **Two-Tab Race Test:** Fires 2 concurrent `add_from_catalog` requests with distinct `Idempotency-Key` values (`key-tab-1`, `key-tab-2`) for the same `(uid, nac_code)` and asserts deterministic allocation of `_SLOT1` and `_SLOT2` with zero lost updates or overwrites.
   - **Idempotent Retry Test:** Replays `key-tab-1` and `key-tab-2` and asserts that the server returns the original `_SLOT1` / `_SLOT2` responses (`idempotent_replay=True`) and **never** allocates `_SLOT3`.
   - **Untrusted Client Field Rejection Test:** Asserts that passing `kind`, `slot`, or `tier` in the client request body raises a validation error and cannot override server-side routing.

---

## 4. Visual Design System & Desktop/Tablet Web UX Specification

### 4.1 Aesthetic Direction & Theme Tokens
The catalog uses a dark-mode **Archival Museum Studio** aesthetic engineered for high-contrast numismatic photography on Desktop Web (`â‰¥1280px` 8-column browse grid + 4-column sticky right inspector):

| Design Token | Hex / Value | Usage |
| :--- | :--- | :--- |
| `Surface Background` | `#0D1017` | Primary page canvas |
| `Card / Inspector Surface` | `#161B26` | Elevated card containers and sticky detail inspector |
| `Stage Well Background` | `#090C12` | Recessed velvet-dark display well behind coin/note photography |
| `Border Subtle` | `#262F40` | Default card and filter rail hairlines (`1px solid`) |
| `Accent Gold / Primary` | `#F59E0B` | Active era scrubber, selected card border ring, Tier-B consensus highlight |
| `Verified Emerald` | `#10B981` | `CHK` verified badge, Tier-A official mintage lock, collection write confirmation |
| `Pre-Federal Amber Badge` | `#F59E0B` (`20%` bg) | Distinguishes 1776â€“1791 Colonial/State issues on unified timeline |
| `Foreign Specie Purple Badge` | `#A855F7` (`20%` bg) | Marks circulating foreign legal-tender coins (Spanish 8 Reales, etc.) |
| `Identity Side Sky Badge` | `#38BDF8` (`20%` bg) | Indicates when `default_face == "REVERSE"` is displayed by default |

### 4.2 Desktop Web Master Layout (`/catalog`)
*(Note per GB MUST-EDIT 9: The 1787 Fugio Cent card badge is corrected from `"Pre-Federal Â· NY"` to **`"Pre-Federal Â· Continental"`** (`state_or_entity = "CONTINENTAL"`), reflecting its authorization by the Continental Congress on April 21, 1787.)*

```
+--------------------------------------------------------------------------------------------------+
|  URL: https://numista.ai/catalog/coins/morgan-dollar/1881-s   [Canonical: NAC1.CN.US.1D.MORGANâ€¦] |
+--------------------------------------------------------------------------------------------------+
|  U.S. NUMISMATICS MASTER CATALOG (1776â€“2026)          [Search: year, series, Fr.#, NAC1â€¦] [ðŸ”]   |
|  TABS: [ ALL ] [ðŸª™ COINS] [ðŸ’µ BANK NOTES] [ðŸŽ–ï¸ MEDALS & TOKENS (Phase 2)] [ðŸŒŽ FOREIGN SPECIE]     |
+--------------------------------------------------------------------------------------------------+
|  ERA PILLS: [All 1776â€“2026] [Pre-Federal 1776â€“1791] [Early Fed] [Gilded Age] [Modern & 250th]    |
|  SCRUBBER:  1776 ================================[ â‰¤ 2026 ]                                      |
|  (When Pre-Federal active) -> STATE FACET: [All] [Continental Congress] [CT] [MA] [NJ] [NY] [VT] |
|  FACILITY (FAC): [ALL] [P] [D] [S] [W] [CC] [O] [C] [DDÂ·Dahlonega] [MÂ·Manila] [MOÂ·Mexico City]   |
+--------------------------------------------------------------------------------------------------+
|  CATALOG BROWSE GRID (8 Cols)                        |  LIVE ARCHITECTURE INSPECTOR (4 Cols)     |
|                                                      |                                           |
|  +-----------------------+  +-----------------------+|  1881-S Morgan Silver Dollar     [CN]     |
|  | [1881-S]   [ðŸ”„ Flip]  |  | [2022-P AWQ] [ðŸ”„ Flip]||  ---------------------------------------  |
|  |                       |  | [Identity: Reverse]   ||  NAC1 SEGMENTS (Crockford-32 Verified):   |
|  |   ( 1881-S OBVERSE )  |  |   ( MAYA ANGELOU )    ||  [NAC1][CN][US][1D][MORGAN][1881][S][BASE]|
|  |   (  SILVER PHOTO  )  |  |   ( REVERSE PHOTO )   ||  Check Digit: [ E ] (Valid â€” FROZEN)      |
|  |                       |  |                       ||                                           |
|  | 1881-S Morgan Dollar  |  | 2022-P Maya Angelou   ||  FACILITY & MINT MARK (NAC Â§0.1):         |
|  | NAC1.CN.US.1D.MORGANâ€¦ |  | NAC1.CN.US.25C.AWQâ€¦   ||  â€¢ FAC: "S" (San Francisco)               |
|  | Tier A: 12,760,000    |  | Tier A: 258,200,000   ||  â€¢ mint_mark_on_coin: true ("S")          |
|  | Tier B: 12,760,000    |  | Tier B: 258,200,000   ||  â€¢ Default Face: OBVERSE                  |
|  | [+ Add /coins] [Info] |  | [+ Add /coins] [Info] ||                                           |
|  +-----------------------+  +-----------------------+|  DUAL-TIER MINTAGE & CITATION:            |
|                                                      |  â€¢ Tier A (Gov): 12,760,000               |
|  +-----------------------+  +-----------------------+|  â€¢ Tier B (Trade): 12,760,000             |
|  | [Series 1899] [ðŸ”„Flip]|  | [1787 Fugio] [ðŸ”„ Flip]||  â€¢ Citation: US Mint Annual Report 1882   |
|  |                       |  | [Pre-FedÂ·Continental] ||                                           |
|  | [==================]  |  |   ( FUGIO OBVERSE )   ||  COLLECTION WRITE CONTRACT (REQ_031):     |
|  | [ $5 INDIAN CHIEF  ]  |  |   (  COPPER PHOTO  )  ||  â€¢ Target: users/{uid}/coins              |
|  | [==================]  |  |                       ||  â€¢ Key: NAC1_CN_US_1Dâ€¦_SLOT1 (Server Txn) |
|  | $5 Silver Certificate |  | 1787 Fugio Cent (BASE)||  â€¢ Mode: Atomic txn.create() + Idem-Key   |
|  | [+ Add /currency]     |  | [+ Add /coins] [Info] ||                                           |
|  +-----------------------+  +-----------------------+|                                           |
+--------------------------------------------------------------------------------------------------+
```

### 4.3 Card Anatomy & The "Unique Identity Side" Rule
1. **Default Face = Unique Identity Side (`default_face`):**
   - Standard series set `default_face: "OBVERSE"`.
   - Shared-obverse series (50 State Quarters `STQ`, America the Beautiful `ATB`, American Women Quarters `AWQ`) set `default_face: "REVERSE"` with an `Identity: Reverse` sky-blue badge.
   - Shared-reverse series (Presidential \$1 `PRES`) set `default_face: "OBVERSE"`.
2. **Interactive 3D Card Flip (`550ms`):**
   - Clicking `ðŸ”„ Flip` rotates the stage `180Â°` along the Y-axis to reveal the opposite face in-place.

---

## 5. Missing Image Standard & Image Hierarchy Policy

### 5.1 Image Source Hierarchy & Zero-PII Credit (Founder Q3 Ruling + SAG #9)
To ensure the catalog maintains academic integrity while allowing high-quality community contributions, all catalog images follow a strict 3-tier hierarchy:
1. **Tier 1 (`MUSEUM` â€” Preferred):** Smithsonian National Numismatic Collection (NNC) CC0 Open Access, ANS, or major academic institutions.
2. **Tier 2 (`PUBLIC_DOMAIN`):** U.S. Mint, BEP, NARA, and Library of Congress official press and production plates.
3. **Tier 3 (`VERIFIED_COMMUNITY` â€” Strict Exception Path):**
   - Collector photo submissions are accepted **only** when:
     a) No Tier 1/2 image exists, OR the submission is proven to be **strictly higher resolution and quality** than the current placeholder/stock image.
     b) The photo passes automated AI quality pre-screening (sharpness, macro resolution, absence of glare/fingers).
     c) The photo is **formally reviewed and verified by a human Catalog Registrar**.
     d) The submitter signs an irrevocable CC0 / public-domain dedication.
     e) **Zero User PII in Public Docs (SAG #9):** Public catalog docs credit community submissions using an opaque archival ID (`"Numista.AI Verified Community Archive (CC0 #C-0104)"`) and **never** expose usernames, emails, or UIDs in public Firestore documents or snapshots.

### 5.2 Guest Download Restrictions & Thumbnail Separation (Founder Q4 Ruling + SAG #3)
- Public catalog responses expose **only** low-resolution display thumbnails (`obverse_thumb_url` / `reverse_thumb_url`, $\le 600\text{px}$ WebP).
- High-resolution archival images (`obverse_image_url` / `reverse_image_url`) are gated behind `GET /api/v1/catalog/{nac_code}/image-download`. Unauthenticated guests receive **`HTTP 403 IMAGE_DOWNLOAD_REQUIRES_ACCOUNT`** (Founder Q4: **NO image download for non-account visitors**).

### 5.3 `DualSidedPlaceholder` Vector Standard
When photography is pending (`image_tier == "NONE"`), the catalog renders vector die blueprints labeled `OBVERSE PENDING` / `REVERSE PENDING` with the `CC0 Archive Queue` badge.

---

## 6. Access Tiers, Public Surface Protection & Cloud Monitoring

### 6.1 SEO Slug + Canonical `NAC1` Routing
- Human-friendly public URL: `https://numista.ai/catalog/coins/morgan-dollar/1881-s`
- Deterministic canonical mapping: `/catalog/NAC1.CN.US.1D.MORGAN.1881.S.BASE.E` resolves with `301/canonical` to the SEO slug.

### 6.2 Server-Enforced Access Tiers (SAG S1, S2, S7, S8 / GB MUST-EDIT 2 & 9)
All capabilities are enforced server-side on Cloud Run:

| Capability | Guest / Public (Unauth) | Registered Free Collector | Pro / Research Subscriber | Server Enforcement Point | Ruling / Proposal Status |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Browse `/catalog`** | Public SEO (via Cloud Run API; raw Firestore `list` blocked) | Unlimited | Unlimited | Cloud Run `/api/v1/catalog/search` + App Check + Cloud Armor | **FOUNDER-CONFIRMED (Q4)** |
| **Full-Text & Faceted Search** | **Session Rate-Limited** (`50 searches/day` `[PENDING ERIC â€” Agent Proposal]`) | Unlimited | Unlimited | Cloud Run IP/Session Rate Limiter (`HTTP 429`) + Cloud Armor | Rate-limit principle **FOUNDER-CONFIRMED (Q4)**; `50/day` number is **`[PENDING ERIC â€” Agent Proposal]`** (SAG S8) |
| **Image Downloads** | **NO DOWNLOAD** (`HTTP 403`) | Standard Res (`[PENDING ERIC â€” Agent Proposal]`) | Full High-Res Archival Download | `GET /api/v1/catalog/{nac_code}/image-download` Signed URL Gate | Guest NO DOWNLOAD **FOUNDER-CONFIRMED (Q4)**; Free vs. Pro download tier split is **`[PENDING ERIC â€” Agent Proposal]`** (SAG S8) |
| **`+ Add to Collection`** | Prompt Sign-In (`HTTP 401`) | **Free Trial up to 5 Items** (`catalog_trial_count < 5`), then Paid Upgrade (`HTTP 402`) | **Unlimited Items** | Atomic Firestore Transaction (`_execute_catalog_add_txn`, Â§3.3) | **FOUNDER-CONFIRMED (Eric 29 Oct 9:23 AM ET, SAG S7)** |
| **Estate PDF & CSV Export** | Disabled (`HTTP 401`) | Disabled (`HTTP 403`) | Full Estate PDF + CSV Export | `passport_pdf_generator.py` auth gate | **FOUNDER-CONFIRMED (Q4)** |
| **Ask Morgan AI / Visual AI** | Disabled (`HTTP 401`) | Disabled (`HTTP 403`) | Unlimited Archival Queries | `tier_gatekeeper.py` subscription check | **FOUNDER-CONFIRMED (Q4)** |

### 6.3 App Check, Cloud Armor & Cloud Monitoring Alert Thresholds (SAG #3 / S2 / GB MUST-EDIT 2)
Before any public `/catalog` deployment, the following four infrastructure guards and monitoring alerts must be active:

| Guard / Metric | Concrete Threshold | Automated Action | Alert Channel & Owner |
| :--- | :--- | :--- | :--- |
| **1. Firebase App Check** | Enforced on `us_numismatics_catalog` (`request.app_check_token != null`) and `/api/v1/catalog/*` headers | Reject unattested SDK/bot requests with `HTTP 401/403` | AG Ops / Security Log |
| **2. Cloud Armor IP Rate Limit** | `> 120 req / min` per IP on `/api/v1/catalog/*` | Edge throttle `HTTP 429` for `600s` | Cloud Armor Security Policy |
| **3. Guest Search Quota Spike** | `> 5%` of `/api/v1/catalog/search` responses returning `HTTP 429` over a `5-minute` rolling window | Trigger scraping anomaly alert | Cloud Monitoring Alert â†’ **AG Ops & Founder** |
| **4. Firestore Read Burst Guard** | `> 25,000` Firestore document reads / `15-minute` window on `us_numismatics_catalog` | Trip circuit-breaker to serve cached CDN catalog pages; page owner | FinOps Budget & Read Alert â†’ **AG Ops & Founder** |

---

## 7. Evidence-Gated Phased Implementation Roadmap

### 7.1 Mandatory Ship Gates (SAG #8 / S6 / GB MUST-EDIT 6)
Calendar dates (`November 1, 2026` and `November 27, 2026`) are **aspirational earliest targets only**. No phase may be merged to `origin/main` or deployed to production until **all four ship gates** below are green:

| Gate ID | Gate Name | Mandatory Exit Criterion | Authority |
| :---: | :--- | :--- | :--- |
| **Gate A** | **Mint FAIL-FIX (`NET-641`) & `p7-gate` Clearance** | Mint FAIL-FIX passes full FT verification AND Founder completes live preview retest. | Founder Eric Seaman |
| **Gate B** | **Catalog Research Evidence Pack Clearance** | Every specimen in the phase batch has a CR-verified Evidence Pack with `TIER_A_GOV` primary citations passing `validate_tier_a_mintage_authority` (Â§2.3.2). | Catalog Research + Automated Schema Gate |
| **Gate C** | **Explicit Founder Fold Clearance** | Founder explicitly lifts the fold HOLD (`586/588/589/590`) for the specific batch. *(Currently only the 2 `NET-645` figures â€” `1921-S Walker = 548,000` and `1955-P Franklin = 2,876,381` â€” have Founder fold YES.)* | Founder Eric Seaman |
| **Gate D** | **Production Branch (`origin/main`) Unlock** | Founder explicitly authorizes unlocking `origin/main` ("Prepare to Deploy"). | Founder Eric Seaman |

### 7.2 Phase 1A & Phase 1B (Gated by Gates Aâ€“D Above)
- **Phase 1A (Earliest Aspirational Window: Nov 1, 2026 â€” Behind Gates Aâ€“D):**
  - **Scope:** Verified U.S. Federal circulating & bullion coins (`1792â€“2026`) anchored by the 25 verified Evidence Packs (`AWQ`, `ASE`, `ATB`, `MORGAN`, `PEACE`, `STQ`, `AID`, etc.), including the 2 Founder-cleared `NET-645` figures (`1921-S Walker = 548,000` and `1955-P Franklin = 2,876,381`).
  - **Deliverables:** Desktop/Tablet Web `/catalog` browse grid, era scrubber, disambiguated `FAC` filter rail (`P`, `D`, `S`, `W`, `CC`, `O`, `C`, `DD`, `M`, `MO`), instant text search, 3D card flip, atomic server add transaction (`CN` â†’ `users/{uid}/coins`), and App Check + Cloud Armor + Monitoring alerts.
- **Phase 1B (Earliest Aspirational Window: Nov 27, 2026 â€” Behind Gates Aâ€“D):**
  - **Scope:** Additional U.S. Federal coins + U.S. Federal Paper Currency (`1861â€“2026`) cleared by Catalog Research once Founder lifts HOLD batches (`586+588+589+590`), plus U.S.-Philippines territorial coinage (`CC="PF"`).
  - **Deliverables:** Currency tab routing `BN` to `users/{uid}/currency`.

### 7.3 Phase 2: Post-Black Friday Semiquincentennial Completion (Q1 2027 â€” Behind Gates B & C)
- **Pre-Federal & Colonial Coinage (`1776â€“1791`, `CC="CO"`):** Interleaved into the unified 1776â€“2026 timeline with `"Pre-Federal"` badge and State/Authority Facet (`CONTINENTAL`, `CT`, `MA`, `NJ`, `NY`, `VT`).
- **Foreign Specie Circulating in Early America (`1776â€“1857`, `CC="FS"`, `FAC="MO"|"L"|"PTS"`):** Dedicated Foreign Coins section (Spanish-American 8 Reales, etc.).
- **Official & Common Private Medals (`KIND="MD"`, `CLASS="OFF"` and `CLASS="PRV"`) + Historic Tokens (`KIND="TK"`):** Routing additions to `users/{uid}/world_items`.
- **Mobile Companion Physical Workflows (GB MUST-EDIT 9):**
  1. **Camera Quick-Add Workflow:** Rapid obverse/reverse mobile camera capture directly into personal collection slots.
  2. **Grading Slab Barcode / NFC & Dealer Receipt OCR Scan:** Dedicated mobile scanner reading PCGS/NGC slab barcodes/QR codes and dealer invoice line-items to auto-populate `nac_code` collection additions.
- **Multi-Modal Visual AI Photo Matching (`Scan AI`):** Camera upload attribution against catalog embeddings.

---

## 8. Strategic Architectural Decisions (Founder Rulings â€” Eric Seaman, Oct 29, 2026)

All strategic decisions are sealed with Founder Eric Seaman's verbatim confirmations (October 29, 2026):

1. **Q1 â€” Pre-1792 Colonial & State Grouping (8:44 AM ET):**
   - **Founder Ruling:** Pre-1792 coins interleave into the unified `1776â€“2026` timeline with a `"Pre-Federal"` badge and an Issuing State/Authority filter (`CONTINENTAL`, `CT`, `MA`, `NJ`, `NY`, `VT`). Confirmed.
2. **Q2 â€” Circulating Foreign Specie (8:44 AM ET):**
   - **Founder Ruling:** Stays out of the main circulating U.S. Federal catalog, but **must have an explicit place in the catalog** in a dedicated **Foreign Coins / Foreign Specie Circulating in Early America** section (`1776â€“1857`, `CC="FS"`). Confirmed with condition.
3. **Q3 â€” Missing Image & Community Photo Submissions (8:44 AM ET):**
   - **Founder Ruling:** Image priority is strictly **Museum preferred â†’ Public domain OK â†’ User uploads allowed as 3rd option ONLY when verified (AI + human) AND higher quality than existing**. In personal collections, users can toggle between their own uploaded photos and catalog stock photos. Confirmed as modified.
4. **Q4 â€” Public Access, 5-Item Free Trial & Monetization Boundaries (8:44 AM ET & 9:23 AM ET):**
   - **Founder Ruling:** Browse and search are public; adding coins, exports, Morgan AI, and visual AI are paid features (**with a Founder-confirmed 5-item free trial for free registered accounts**, confirmed by Eric at 9:23 AM ET). Non-account visitors get search limitations and **NO image download**. *(Specific `"50 searches/day"` guest threshold and free-tier download resolution remain labeled `[PENDING ERIC â€” Agent Proposal]` per SAG S8.)*
5. **Mobile Architecture (8:44 AM ET):**
   - **Founder Ruling:** The phone app is a small, specialized companion (~90% website / 10% app) for phone-only physical jobs: adding coins with camera, scanning slabs and receipts (scheduled in Phase 2, Â§7.3). Big catalog browsing stays on laptop/tablet. Confirmed.

---

## 9. Forbidden Path Prefixes, Reconciled Allowlist & Verification Gates

### 9.1 Exhaustive Forbidden Path Prefix List (SAG #6 / S4 / GB MUST-EDIT 5)
To guarantee zero interference with **Mint FAIL-FIX (`NET-641`)**, **`p7-gate`**, Estate PDF generation, or BigQuery ETL, catalog work on `dev` is **strictly forbidden** from modifying any file matching the following prefixes:

| Forbidden Path Prefix / File | Protected System / Owner | Enforcement |
| :--- | :--- | :--- |
| `numista_backend/routes/mint_*` / `numista_backend/services/mint_*` / `numista_backend/mint_*` | Mint FAIL-FIX (`NET-641` Day #1 Priority) | Hard Gate 1 (`exit 1`) |
| `numista_mobile/lib/screens/mint/` / `numista_mobile/lib/widgets/mint/` / `numista_mobile/lib/services/mint*` | Mint FAIL-FIX Frontend (`p7-gate`) | Hard Gate 1 (`exit 1`) |
| `numista_backend/passport_pdf_generator.py` | Estate Passport PDF Engine | Hard Gate 1 (`exit 1`) |
| `numista_backend/numista_bq_loader_job/` | BigQuery Analytics ETL Pipeline | Hard Gate 1 (`exit 1`) |
| `numista_backend/tier_gatekeeper.py` | Shared Subscription Gatekeeper | **Forbidden during `NET-641`** (Catalog uses self-contained gate in `catalog_service.py`; integration into `tier_gatekeeper.py` requires Scoped Gatekeeper Exception after `NET-641` clears) |
| `firestore.rules` / `firestore.indexes.json` | Global Firestore Security Rules | **Forbidden during `NET-641`** (Rule snippet in Â§2.4 is staged in plan documentation only until `NET-641` clears and a Scoped Rules PR is approved) |
| Any branch other than `dev` (`main`, `p7-gate`) | Production & Mint Gate Branches | Hard Gate 1 (`exit 1`) |

### 9.2 Reconciled Allowlist & Machine-Checkable Verification Gates
All catalog code changes on `dev` are restricted exclusively to the catalog-scoped allowlist below (`numista_backend/catalog_*`, `numista_backend/routes/catalog_routes.py`, `numista_backend/data/catalog_dev_fixture.json`, `numista_backend/tests/test_catalog_*`, `numista_tests/test_*catalog*.py`, `numista_tests/test_nac1_validator.py`, `numista_tests/test_passport_pdf_coin_guard.py`, and `numista_mobile/{lib,test}/**/catalog*`).

Before any implementation PR is promoted on `dev`, all five machine-checkable gates must return **Exit Code 0**:

```bash
# 1. Mint FAIL-FIX & Forbidden-Prefix Isolation Gate (SAG #6 / S4 / GB MUST-EDIT 5)
git branch --show-current | grep -qx "dev"
git diff --name-only origin/dev..HEAD | grep -E "^(numista_backend/(routes/)?mint_|numista_mobile/lib/.*/mint|numista_backend/passport_pdf_generator\.py|numista_backend/numista_bq_loader_job/|numista_backend/tier_gatekeeper\.py|firestore\.rules)" && exit 1 || true
git diff --name-only origin/dev..HEAD | grep -Ev "^(numista_mobile/lib/(screens|services|widgets)/catalog/|numista_mobile/test/(catalog_browse_test|nac_code_parser_test)\.dart|numista_backend/(catalog_|routes/catalog_routes\.py|data/catalog_dev_fixture\.json|tests/test_catalog_)|numista_tests/test_(nac1_validator|catalog_schema|catalog_collection_routing|catalog_add_race|passport_pdf_coin_guard)\.py|Numismatics Catalog/|1 NUMISTA\.AI/)" && exit 1 || true

# 2. Deterministic NAC1 Checksum (FROZEN), Era/Year/Facility Agreement, Tier-A Authority & Zero-PII Schema Gate
python -m pytest numista_tests/test_nac1_validator.py numista_tests/test_catalog_schema.py -v

# 3. Atomic Server Add Transaction, Two-Tab Race (_SLOT1/_SLOT2), Idempotency, 5-Item Free Trial & Collection Routing Gate
python -m pytest numista_tests/test_catalog_add_race.py numista_tests/test_catalog_collection_routing.py numista_tests/test_passport_pdf_coin_guard.py -v

# 4. Flutter Static Analysis & Desktop Web Catalog Widget Tests
flutter analyze --no-pub lib/screens/catalog/ lib/services/catalog/ lib/widgets/catalog/
flutter test --no-pub test/nac_code_parser_test.dart test/catalog_browse_test.dart

# 5. Git Worktree Cleanliness
git status --porcelain
```

---
**Document Status:** Plan.v2.2 Complete â€” Closes all GB CoS (`79/100`), SAG v2.1 (`74/100`), and SAG Addendum (`58/100`) Must-Fixes  
**Author:** Argon (AG System Architect / Lead Engineer)  
**File Location:** `Numismatics Catalog/Argon Implementation Plan/US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V2.2.md`  
**Visual Mockup:** `Numismatics Catalog/Argon Implementation Plan/us_numismatics_catalog_mockup.html`

