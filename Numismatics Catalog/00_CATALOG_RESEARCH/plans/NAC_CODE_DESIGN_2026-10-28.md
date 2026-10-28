# NAC — Numista.Ai Catalog item codes (proprietary)

**Filed:** Wednesday, 28 Oct 2026 ~7:45 AM ET (America/New_York)  
**Owner:** Catalog Research (Eric Seaman / Numista.Ai / SGroup)  
**Status:** DESIGN — ready for org use in Slack / batons / Firestore crosswalk fields. **Not** a public Greysheet/GSID replacement.  
**Box:** `/workspace/catalog-research/NAC_CODE_DESIGN_2026-10-28.md`  
**Laptop:** `C:\Users\ericd\Documents\MyVertexProject\Numismatics Catalog\00_CATALOG_RESEARCH\plans\NAC_CODE_DESIGN_2026-10-28.md`

---

## 0. Disclaimer (read first)

**NAC is proprietary to Numista.Ai / SGroup.** It exists so teammates and agents can share a stable, human-readable handle for the same physical type (coin / bank note / medal) in Slack, email, batons, and internal DBs.

It is **inspired by conceptual dimensions** of industry catalog systems (including CDN / Greysheet’s publicly described GSID role as a universal catalog key and their Node→Collectible hierarchy). It is **not**:

- a copy of Greysheet Identification (GSID) numbers or tables  
- a substitute for paid Greysheet / CDN API data  
- a public price-guide identifier  
- a license to reproduce CDN catalog metadata or wholesale numbering  

We **do not** scrape paid Greysheet content, call the paid CDN API for this design, or invent GSID values. If a licensed GSID is later obtained via the org’s paid API, store it only as an optional opaque foreign key (`gsid_xref`) — never as the NAC itself.

## 0.1 LOCKED DECISIONS (Eric, 28 Oct 2026 ~11:17–11:18 AM ET)

These override any conflicting text below.

1. **FAC = mint city, P/D/S/W/O/CC/C/DD (Dahlonega)/as needed (Eric final, 28 Oct ~11:21 AM ET: "Just use P, D, S for the city").** FAC encodes the striking facility city only. No special no-mark token (no `NMN`/`NP`/`XX` for U.S. Mint coins). Mark presence is separate metadata: `mint_mark_on_coin` (true/false) and optional `mint_mark` (letter as struck, if it differs from FAC). No-mark Philadelphia = `FAC=P` + `mint_mark_on_coin:false`; marked-P Philadelphia (e.g. 1942-P nickel, 1980+ P) = `FAC=P` + `mint_mark_on_coin:true`, `mint_mark:"P"`. Two coins differing only by mark presence that are distinct catalog types are separated via `VAR`/`DATE` rules, not FAC. `XX` remains only for non-U.S.-Mint pieces (1787 Fugio — New Haven contract; private medals/tokens) or not applicable; documented separately with `facility_note` (e.g. "New Haven contract").
2. **Proof sets / Mint products:** issue **both** a `KIND=ST` set/product NAC (one per product, e.g. annual Proof Set) **and** individual `CN` NACs for every component coin. The ST record lists its component NACs; component coins keep their own codes.
3. **Private medal SERIES:** free slug, **2–12 chars, uppercase A–Z0–9 only**, logged in the series registry on first use (never reuse a slug for a different series). `PRIV` remains the catch-all.

---

## 1. What we borrow conceptually from Greysheet / CDN (public docs only)

Public Greysheet materials describe (high level):

| Concept | Public Greysheet / CDN pattern | NAC response |
|---|---|---|
| Universal key | GSID = proprietary unique ID for coin/currency types; master key across Whitman/CDN products | NAC = our own proprietary key for **internal** sharing |
| Hierarchy | **Nodes** (category folders) nest until a **leaf node**; **Collectibles** live only on leaves (e.g. U.S. Coins → Nickels → V-Nickels Proof → 1883 5c No Cents PR) | NAC **encodes** the useful dimensions of that path in a fixed field order (not a tree of numeric node IDs) |
| Coverage intent | Federal coins, paper, medals/tokens growth, world modern | NAC Kind covers CN / BN / MD (+ TK; ST = set/product, active per §0.1) |
| Cross-refs | CDN X-refs PCGS#, NGCID, Krause, Friedberg, Pick | NAC carries optional `*_xref` fields; does **not** embed third-party numbers in the primary code |
| Identity grain | One collectible ≈ type+date+mint+major variety (grade is pricing, not identity) | Same: **grade is never in NAC** |

**Public sources consulted (no paid API):**  
- https://www.greysheet.com/gsid — GSID as proprietary universal identifier  
- https://www.greysheet.com/cms/1049/cdn-public-api-v2-usage-guide — Nodes vs Collectibles; `GsId` as `long`; X-ref mention  
- https://www.greysheet.com/cms/1053/api-terms-of-use-and-license-agreement — GSID display/license constraints  

GSID itself is an **opaque numeric** identifier in public API DTOs. NAC deliberately uses a **segmented, mnemonic, versioned** string instead.

---

## 2. Design goals

1. **Proprietary** alphabet, separators, field order, and version prefix — clearly not GSID.  
2. **Human-readable** in Slack/email/batons (mnemonic series tokens).  
3. **Stable:** same physical catalog type → same NAC forever (once assigned).  
4. **Covers** coins, bank notes, medals (official U.S. Mint + common private commemoratives users may add).  
5. **Typo-catchable:** version prefix + trailing checksum.  
6. **Map-friendly** to studio Firestore `definitive_reference` and Discovery `morgan-docs` via crosswalk fields — **do not invent mintages** or Firestore IDs.

---

## 3. Full grammar (NAC1)

### 3.1 Wire form

```
NAC1.<KIND>.<CC>.<CLASS>.<SERIES>.<DATE>.<FAC>.<VAR>.<CHK>
```

- Separator: **period** (`.`) only — never hyphen chains that look like date ranges.  
- Alphabet for tokens: `A–Z`, `0–9` (uppercase). No lowercase; no spaces.  
- Ambiguous glyphs avoided in `<CHK>` (Crockford Base32 set: `0–9 A–H J–N P–T V–Z`, excluding `I L O U`).

### 3.2 BNF

```bnf
nac            ::= "NAC" ver "." kind "." cc "." class "." series "." date "." fac "." var "." chk
ver            ::= DIGIT+                          ; currently "1"
kind           ::= "CN" | "BN" | "MD" | "TK" | "ST" ; coin | banknote | medal | token | set/product
cc             ::= ALPHA ALPHA                     ; ISO 3166-1 alpha-2; "US" for United States;
                                                   ; "PF" = pre-federal Confederation issues under US catalog
class          ::= coin_class | note_class | medal_class
coin_class     ::= "1C" | "5C" | "10C" | "25C" | "50C" | "1D" | "2D5" | "3C" | "20C"
                 | "G1" | "G2D5" | "G3" | "G5" | "G10" | "G20" | "G50" | "G100"
                 | "BUL"                           ; bullion face where legal-tender face is $1 ASE-class → prefer 1D+SERIES
note_class     ::= "FRN" denom | "FRBN" denom | "SC" denom | "GC" denom | "TN" denom
                 | "LT" denom | "NAT" denom | "DEM" denom | "CSA" denom | "CLC" denom
denom          ::= "1" | "2" | "5" | "10" | "20" | "50" | "100" | "500" | "1000" | "5000" | "10000" | "100000"
medal_class    ::= "OFF" | "PRV" | "CONG" | "PRES" | "ASSAY" | "COMM"
series         ::= 2*12 (ALPHA | DIGIT)            ; mnemonic registry token (see §5)
date           ::= YYYY | YYYY "A"-"Z" | "ND" | "XXXX"
                                                   ; YYYY = calendar year on piece / series year for notes;
                                                   ; optional letter suffix for FRN series (e.g. 2017A)
fac            ::= mint | "XX" | "BEP" | "NARA"     ; XX = not U.S. Mint / not applicable (no-MM U.S. Mint coins = P)
mint           ::= "P" | "D" | "S" | "W" | "CC" | "O" | "C" | "M" | "A" | "T" | "Y"
                 | "PH"                            ; Philippine / Manila when distinct facility needed
var            ::= "BASE" | 2*12 (ALPHA | DIGIT)   ; BASE = default type; else variety/product token
chk            ::= crockford32                     ; single check char over payload (§4)
```

### 3.3 Field table

| # | Field | Len | Purpose | Notes |
|---|---|---|---|---|
| 0 | `NAC`+`ver` | 4+ | Scheme + breaking-change version | `NAC1` now; `NAC2` only if grammar breaks |
| 1 | `KIND` | 2 | Object family | CN / BN / MD / TK / ST |
| 2 | `CC` | 2 | Issuing polity | US primary; foreign later |
| 3 | `CLASS` | 2–8 | Denomination or note/medal family | Not Greysheet node IDs |
| 4 | `SERIES` | 2–12 | Type / program mnemonic | Registry-controlled; private medals = free slug A–Z0–9 ≤12 (§0.1) |
| 5 | `DATE` | 2–5 | Year or FRN series year | `ND` undated medals; `XXXX` unknown (rare) |
| 6 | `FAC` | 1–4 | Mint / BEP / none | Facility of issue, not storage |
| 7 | `VAR` | 2–12 | Variety or product finish | `BASE`, `PRF`, `RP`, `SMS`, `VAM3`, `3LEG`, honoree short code, etc. |
| 8 | `CHK` | 1 | Checksum | Catches typos |

**Not in NAC:** grade, CAC/plus, population, price, ownership, condition, serial number of a specific note bill (instance), mintage figures.

---

## 4. Checksum algorithm (NAC1)

Payload = everything before the final `.CHK`, ASCII uppercase as written.

```
alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"   # Crockford-32, len 32
h = 0
for each byte b in UTF-8(payload):
    h = (h * 33 + b) mod 37
CHK = alphabet[h mod 32]
```

Validators: recompute; reject mismatch. Generators: always append computed CHK.  
(Mod 37 then map to 32 keeps a small catch for single-char typos without resembling GSID numerics.)

---

## 5. Series mnemonic registry (starter — US)

Assign via Catalog Research registrar. **Do not** invent mintages when adding a series.

| SERIES | Meaning | KIND |
|---|---|---|
| FUGIO | Fugio cent (1787) | CN |
| CHAIN | 1793 Chain cent | CN |
| MORGAN | Morgan dollar | CN |
| PEACE | Peace dollar | CN |
| ASE | American Silver Eagle | CN |
| AGE | American Gold Eagle | CN |
| AWQ | American Women Quarters | CN |
| ATB | America the Beautiful Quarters | CN |
| STQ | 50 State Quarters | CN |
| AID | American Innovation $1 | CN |
| LINCOLN | Lincoln cent (umbrella; use VAR for Wheat/Memorial/Shield when needed) | CN |
| BUFFALO | Buffalo / Indian Head 5¢ | CN |
| JEFF | Jefferson 5¢ | CN |
| ROOS | Roosevelt 10¢ | CN |
| WASH | Washington 25¢ (classic) | CN |
| WALKER | Walking Liberty 50¢ | CN |
| FRANKLIN | Franklin 50¢ | CN |
| KENNEDY | Kennedy 50¢ | CN |
| SAC | Sacagawea / Native American $1 | CN |
| PRES | Presidential $1 | CN |
| SEMIQ | 2026 Semiquincentennial circulating/collectible types | CN / BN as applicable |
| FED | Federal Reserve Note (modern FRN family when CLASS carries denom) | BN |
| TREAS | Treasury / coin notes (e.g. 1890 “Watermelon” family) | BN |
| SILV | Silver Certificate family | BN |
| GOLD | Gold Certificate family | BN |
| FRBN | Federal Reserve Bank Note family | BN |
| PRES | Presidential medal (Mint) — MD + CLASS PRES | MD |
| CONG | Congressional medal | MD |
| ASSAY | Assay / Mint medal | MD |
| COMM | Generic commemorative medal program token | MD |
| PRIV | Catch-all private commemorative when no better SERIES | MD |

New series: append to registry file (future `NAC_SERIES_REGISTRY.md`); never reuse a token for a different type.

---

## 6. Collision rules

1. **Same physical type → same NAC.** Reassignment forbidden once published internally.  
2. **Grade / stickering / toning** → not a new NAC (instance attributes).  
3. **Distinct Mint product finishes** that collectors treat as different catalog lines (Proof, Reverse Proof, Uncirculated Burnished, SMS, Enhanced) → different `VAR` (`PRF`, `RP`, `UNC`, `SMS`, `ENH`, …).  
4. **Mint mark / facility** differences → different `FAC`. Mark as struck → that letter. **FAC = mint city** (§0.1 #1); no-mark Philly → `P` + `mint_mark_on_coin:false`, marked P → `P` + `mint_mark_on_coin:true`. `XX` only for non-U.S.-Mint pieces / not applicable.  
5. **Major attributed varieties** (VAM, 3-Leg, Doubled Die) → `VAR` token from a controlled list; minor uncatalogued die states stay `BASE` until registrar promotes.  
6. **Bank notes:** series year + facility `BEP`; Friedberg number lives in `friedberg_xref`, not in NAC. Large-size vs small-size distinguished by SERIES/CLASS, not by stuffing Fr. into the code.  
7. **Medals:** `CLASS=OFF` official U.S. Mint (incl. Presidential/Congressional/Assay); `CLASS=PRV` common private commemoratives. Do **not** invent rows that duplicate existing studio `definitive_reference` medal docs — attach NAC via crosswalk.  
8. **Collision on generate:** if two types hash to same string before CHK (should not with full fields), registrar appends `VAR` disambiguator `X2`, `X3`, … and logs.  
9. **Unknown date:** prefer research before `XXXX`; `XXXX` is a last resort and must be upgraded when year is known (treat as **correction**, emit alias map old→new).  
10. **Aliases:** keep `nac_aliases[]` for deprecated codes after corrections; never silently delete.

---

## 7. Versioning

| Version | When | Rule |
|---|---|---|
| **NAC1** | 28 Oct 2026 | Current grammar in this doc |
| **NAC2** | Only if field order/alphabet/KIND set must break | Dual-publish nac1 + nac2 during migration; batons cite both |

Non-breaking adds (new SERIES tokens, new VAR tokens) stay on **NAC1**.

---

## 8. Crosswalk to existing Numista.Ai stores (no invented mintages / IDs)

```yaml
nac_code: "NAC1...."           # primary
firestore_def_ref_id: null     # studio definitive_reference doc id WHEN known from live attach
morgan_docs_ids: []            # Discovery unstructured doc ids when present
morgan_factcheck_ids: []
smithsonian_nnc_ids: []        # if object cards map 1:1
gsid_xref: null                # ONLY if returned by org paid CDN API — opaque long/string, never invented
pcgs_xref: null
ngc_xref: null
friedberg_xref: null
pick_xref: null
krause_xref: null
redbook_xref: null
evidence_pack_row_ids: []      # e.g. FG-586-04
notes: "crosswalk filled only from observed keys; mintages live in sourced fields elsewhere"
```

**Live studio counts (26 Oct inventory, not re-pulled today):** `definitive_reference` ≈ 6,503 (coin 5,770 / banknote 620 / medal 113). NAC assignment for those rows = **attach audit**, not mass invent.

---

## 9. Worked examples (≥12)

Checksums below are **computed with the §4 algorithm** (verify in code before shipping parsers).

| # | Plain description | NAC1 |
|---|---|---|
| 1 | 1787 Fugio cent (no mint mark; New Haven contract, not U.S. Mint → XX) | `NAC1.CN.US.1C.FUGIO.1787.XX.BASE.1` |
| 2 | 1881-S Morgan dollar, business strike | `NAC1.CN.US.1D.MORGAN.1881.S.BASE.E` |
| 3 | 1921 Morgan dollar, Philadelphia, BASE | `NAC1.CN.US.1D.MORGAN.1921.P.BASE.4` |
| 4 | 1937-D Buffalo 5¢ Three-Legged | `NAC1.CN.US.5C.BUFFALO.1937.D.3LEG.3` |
| 5 | 2022-P American Women Quarter — Maya Angelou | `NAC1.CN.US.25C.AWQ.2022.P.MAYA.Z` |
| 6 | 2024-W American Silver Eagle Proof | `NAC1.CN.US.1D.ASE.2024.W.PRF.S` |
| 7 | 1955 Franklin half dollar (P) | `NAC1.CN.US.50C.FRANKLIN.1955.P.BASE.N` |
| 8 | 1921-S Walking Liberty half | `NAC1.CN.US.50C.WALKER.1921.S.BASE.K` |
| 9 | FRN $1 Series 2017A (BEP) | `NAC1.BN.US.FRN1.FED.2017A.BEP.BASE.6` |
| 10 | 1890 $1,000 Treasury Note (“Watermelon” family) | `NAC1.BN.US.TN1000.TREAS.1890.BEP.WM.C` |
| 11 | Official U.S. Mint Presidential medal — Coolidge (illustrative) | `NAC1.MD.US.PRES.PRES.1923.P.COOL.W` |
| 12 | Common private commemorative medal (user-addable class) | `NAC1.MD.US.PRV.PRIV.2000.XX.BASE.3` |
| 13 | 2026 Semiquincentennial quarter — Mayflower Compact (D) | `NAC1.CN.US.25C.SEMIQ.2026.D.MAYF.Z` |
| 14 | 2026 Morgan reverse proof (W), America250 collectible | `NAC1.CN.US.1D.MORGAN.2026.W.RP.B` |
| 15 | 1794 large cent, no mint mark (U.S. Mint Philadelphia → P per §0.1) | `NAC1.CN.US.1C.LGCENT.1794.P.BASE.2` |

### Checksum verification helper (Python)

```python
ALPH = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
def nac_chk(payload: str) -> str:
    h = 0
    for b in payload.encode("utf-8"):
        h = (h * 33 + b) % 37
    return ALPH[h % 32]

def make(kind, cc, clas, series, date, fac, var):
    payload = f"NAC1.{kind}.{cc}.{clas}.{series}.{date}.{fac}.{var}"
    return f"{payload}.{nac_chk(payload)}"
```

*(Examples in the table were generated with this helper on 28 Oct 2026; regenerate if the grammar changes.)*

---

## 10. Org usage cheat-sheet

- Slack/baton: cite NAC in backticks: `` `NAC1.CN.US.1D.MORGAN.1881.S.BASE.E` ``  
- Prefer NAC over long prose titles when pointing agents at a type.  
- Pair with evidence IDs when grounding: `` `NAC1…` / FG-586-04 ``  
- Never paste Greysheet wholesale prices into public surfaces without CDN license review (out of scope for NAC itself).

---

## 11. Implementation sketch (later — not this task)

1. Shared validator module (Python + TypeScript) implementing §4.  
2. Registrar sheet / Firestore collection `nac_registry` with crosswalk fields (§8).  
3. One-time attach pass: map existing `definitive_reference` rows → NAC without rewriting mintages.  
4. Morgan / Catalog Research batons start requiring NAC on new HOLD rows.

---

## 12. Open questions for Eric

All three resolved 28 Oct 2026 — see §0.1 LOCKED DECISIONS.

---

**End of NAC1 design.** Catalog Research · 28 Oct 2026.
