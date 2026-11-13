# VERIFY — 1955 Franklin half dollar mintage (Philadelphia)

**Date:** 2026-10-27 (America/New_York)  
**Author:** SME (Morgan / Numista.Ai) — report-only; no catalog writes  
**Trigger:** FinOps FRASER OCR + CoS ask — Mint AR prints Phil **2,876,381** only; **2,498,181** not in AR; proof-set footnote **346,001** (not 378,200). CoS proposes pack Mint-primary = **2,876,381**.

---

## Executive answer

| Question | Answer |
|---|---|
| What does Mint AR print for 1955 Phil Franklin halves? | **2,876,381** — total pieces manufactured at Philadelphia, calendar year 1955. No D/S. |
| Does Mint label that figure business-only / circulating-only? | **No.** Later Mint summary (AR 1964 Table 21 fn 2) explicitly: Phil column **“Includes proof coins 1950–1963.”** |
| Does any Mint/Treasury primary print **2,498,181** as business-only? | **No.** Not in AR FY1956 (CY1955), not in AR 1964 Table 21, not found in extracted Mint AR text. |
| Where does **2,498,181** come from? | **Catalog/derived:** `2,876,381 − 378,200 = 2,498,181` (Mint Phil total minus conventional proof mintage used by PCGS/Breen/Red Book tradition). |
| What about **346,001**? | Mint AR FY1956 **Table 17 (shipments CY1955)** footnote: “Includes **346,001** sets of proof coins sold by Philadelphia Mint.” **Not** a manufacture business-only breakout. `2,876,381 − 346,001 = 2,530,380` ≠ 2,498,181. |
| CoS Mint-primary **2,876,381**? | **CONFIRM** (do not override). Label as Phil **total manufactured CY1955 (includes proofs)**. |
| How to display **2,498,181**? | **Secondary / derived catalog figure** (PCGS/NGC/Red Book–aligned business-strike), **not** Mint-primary. Keep as correction vs draft **2,496,000** for catalog display, but do not cite Mint AR as printing 2,498,181. |

---

## 1. Primary sources opened this turn

### A. Mint Annual Report — FY ended June 30, 1956 (includes CY 1955 production)

| Item | Value |
|---|---|
| FRASER title page | https://fraser.stlouisfed.org/title/united-states-mint-annual-report-9404/fiscal-year-ended-june-30-1956-including-report-production-consumption-gold-silver-calendar-year-1955-700721 |
| **PDF download URL** | https://fraser.stlouisfed.org/files/docs/publications/usmint/usmint_1956_annual-report.pdf |
| Local extract | `/workspace/morgan_db/audit/gap_plans/tmp_fraser/usmint_1956_annual-report.pdf` (+ `usmint_1956.txt`) |
| Method | `curl` download; `pdftotext -layout`; integer grep |

### B. Mint Annual Report — FY ended June 30, 1964 (Franklin series Table 21)

| Item | Value |
|---|---|
| FRASER / PDF | https://fraser.stlouisfed.org/files/docs/publications/usmint/usmint_1964_annual-report.pdf |
| Local extract | `…/tmp_fraser/usmint_1964_annual-report.pdf` (Table 21 @ PDF p.69 / printed p.55) |
| NNP corroboration | NNP OCR snippet of Table 21 already showed Phil 1955 = 2,876,381 |

---

## 2. Exact integers in Mint AR FY1956 (CY1955)

### Table 11 — United States coins manufactured, calendar year 1955  
*(PDF p.40; printed p.18)*

| Denomination | Philadelphia | San Francisco | Denver | Total |
|---|---:|---:|---:|---:|
| **Half dollars** | **2,876,381** | *(blank)* | *(blank)* | **2,876,381** |

**Labeling:** Table title = coins **manufactured**, calendar year 1955. Row does **not** say “circulating only,” “business strike,” or “excluding proof.” Face-value block matches `$1,438,190.50` = 2,876,381 × $0.50.

**Same Phil total repeated** in world coinage summary for United States (PDF ~p.61): half dollars **2,876,381**.

### Table 17 — Shipments of United States coins for circulation, calendar year 1955  
*(PDF p.41)*

Footnote 1 (OCR cleaned):

> Includes **346,001** sets of proof coins sold by Philadelphia Mint.

**Attachment:** This footnote is on the **shipments** table, **not** on Table 11 manufacture. It does **not** print a business-only half-dollar mintage.

### Integers searched in full AR FY1956 text — **ABSENT**

| Integer | Present in AR FY1956? |
|---|---|
| **2,876,381** | **YES** (manufacture total Phil / US halves CY1955) |
| **346,001** | **YES** (shipments fn — proof **sets sold**) |
| **2,498,181** | **NO** |
| **378,200** | **NO** |
| **2,496,000** | **NO** |
| **2,530,380** | **NO** |

### FY1956 narrative (different window — do not confuse with CY1955)

Fiscal-year 1956 half-dollar production (narrative + FY table): **2,424,654** pieces — fiscal window, not calendar-year 1955 mintage. Phil FY1956 also cites **2,083,042 proof coins** (individual coins, not sets) of regular-issue proof production in that fiscal year.

---

## 3. Mint AR 1964 — Table 21 (Franklin series totals)

**Title:** “Total number of Benjamin Franklin–Liberty Bell design half dollars manufactured by the United States Mints”  
*(PDF p.69; printed p.55)*

| Calendar year | Philadelphia | Denver | San Francisco | Total |
|---|---:|---:|---:|---:|
| **1955** | **2,876,381** | *(blank)* | *(blank)* | **2,876,381** |

**Footnote 2 (critical):**

> **Includes proof coins 1950–1963.**

So Mint’s own later series summary treats Phil yearly totals (including 1955’s 2,876,381) as **including proofs**. That locks Mint-primary labeling: **total manufactured, proofs included** — not business-only.

**2,498,181 / 378,200** do not appear in the Table 21 extract.

---

## 4. Can 2,498,181 be sourced as Mint business-strike only?

**No Mint/Treasury primary found that prints 2,498,181.**

Derivation used by catalogs (exact arithmetic):

```
2,876,381  (Mint Phil total CY1955 — AR FY1956 Table 11 / AR 1964 Table 21)
−  378,200  (conventional 1955 proof-set / proof-half mintage — PCGS/Breen/industry)
= 2,498,181  (published “regular strike” / business mintage)
```

**Using Mint’s own 346,001 proof-sets-sold footnote does NOT recover 2,498,181:**

```
2,876,381 − 346,001 = 2,530,380  ≠ 2,498,181
```

Therefore:

- **2,498,181** = catalog/secondary **derived** business figure (Mint total − industry proof figure 378,200).  
- It is **not** a Mint-printed business-only cell.  
- FinOps OCR was correct: **2,498,181 is not in the AR.**

---

## 5. Red Book / PCGS / NGC / industry — how they treat the split

| Source | Business / regular | Proof | Notes |
|---|---:|---:|---|
| **PCGS CoinFacts** #6670 (Regular Strike) | **2,498,181** | — | https://www.pcgs.com/coinfacts/coin/1955-50c/6670 |
| **PCGS CoinFacts** #6696 (Proof) | — | **378,200** | https://www.pcgs.com/coinfacts/coin/1955-50c/6696 |
| **Walter Breen** (*Encyclopedia of U.S. and Colonial Proof Coins*) | implies business ≪ proofs ×6 | **Set [378,200]** | Explicit set count 378,200 for 1955 |
| **CoinMintages / FranklinHalfGuide-style tables** | **2,498,181** | **378,200** | Same split; Phil business + proof = Mint total |
| **Numismatic News** (1955 low mintages) | **2,498,181** | — | Circulation figure only |
| **NGC** | Industry-standard **2,498,181** for MS / regular (board + explorer listings); some aggregate KM tables may show Mint-style totals | Proof traditionally **378,200** | JS-rendered explorer pages not fully scrapeable this turn; no Mint PDF support for 2,498,181 |
| **Red Book tradition** | Aligns with **2,498,181** business / **378,200** proof (same industry split) | Same | Not opened as a live Red Book PDF this turn; consistent with PCGS/Breen/CoinMintages |

**Proof packaging note (secondary):** 1955 mid-year switch box → flat pack. Specialty literature (PCGS news, ProofSetGuide) states Mint did **not** keep a reliable official split of box vs flat-pack quantities; total industry mintage remains **378,200**. Do **not** treat **346,001** as “the” proof mintage for subtracting from manufacture totals.

**Why FinOps saw 346,001:** Correct AR OCR of Table 17 shipments footnote (sets **sold** in CY1955 shipment accounting) — different concept from the 378,200 proof **mintage** used by catalogs.

---

## 6. Evidence-pack recommendation (for CoS / Desk / AG)

### Mint-primary (pack fold cite)

| Field | Recommendation |
|---|---|
| **Figure** | **2,876,381** |
| **Label** | Philadelphia Franklin half dollars **manufactured**, calendar year **1955** — **total pieces (includes proof coins)** |
| **Primary cites** | (1) AR Director of the Mint, FY ended June 30, 1956, Table 11 (CY1955 manufacture) — PDF: https://fraser.stlouisfed.org/files/docs/publications/usmint/usmint_1956_annual-report.pdf (printed p.18 / PDF p.40). (2) Same series total + explicit proof-inclusion: AR FY1964 Table 21 + fn 2 “Includes proof coins 1950–1963” — PDF: https://fraser.stlouisfed.org/files/docs/publications/usmint/usmint_1964_annual-report.pdf (printed p.55 / PDF p.69). |
| **Tight claim** | The U.S. Mint Annual Report records **2,876,381** Franklin half dollars manufactured at Philadelphia in calendar year 1955 (no Denver/San Francisco); Mint’s 1964 series summary states Philadelphia totals for 1950–1963 **include proof coins**. |

### CoS decision

**CONFIRM** CoS Mint-primary **2,876,381**.  
**Do not OVERRIDE** with 2,498,181 as Mint-primary.

### How to display 2,498,181

| Option | Guidance |
|---|---|
| **Recommended** | Show as **catalog / secondary business-strike mintage: 2,498,181** (derived: Mint total 2,876,381 − conventional proof mintage 378,200), citing PCGS #6670 (and Red Book–aligned catalogs). |
| **Also correct for catalog fold vs draft** | Draft **2,496,000** remains wrong as a catalog figure; if catalog UI shows business mintage, use **2,498,181** not 2,496k — but attribute to catalogs, not as “Mint AR prints 2,498,181.” |
| **Omit from Mint-primary pack cell** | Yes — omit 2,498,181 from any claim that Mint printed business-only. |
| **Proof figure in pack** | Prefer dual note: Mint shipments fn **346,001** sets sold (CY1955 Table 17); catalog/proof mintage **378,200**. Do not subtract 346,001 from 2,876,381 to invent a business figure. |

### Correction to prior SME cite pack (#11)

`EVIDENCE_PACK_CITES_NET581_FOLDS_2026-10-27.md` §11 previously proposed Mint AR as primary for **2,498,181**. **Revise:** Mint-primary = **2,876,381** (total incl. proofs); **2,498,181** = Tier B catalog/derived. Fold vs draft 2,496,000 still stands for **catalog** display, with corrected attribution.

---

## 7. Arithmetic checklist (FinOps / CoS)

| Expression | Result | Meaning |
|---|---:|---|
| 2,498,181 + 378,200 | **2,876,381** | Catalog business + catalog proof = Mint Phil total |
| 2,876,381 − 378,200 | **2,498,181** | How catalogs derive business |
| 2,876,381 − 346,001 | **2,530,380** | Mint total − AR shipments proof-sets-sold ≠ catalog business |
| 2,498,181 in Mint AR? | **No** | Confirmed via full-text search of AR FY1956 extract |

---

## 8. Roll-up for SendToAgent → Chief of Staff

See final assistant message / CoS reply block.

---

## Appendix — file paths

- This verify: `/workspace/morgan_db/audit/gap_plans/VERIFY_1955_FRANKLIN_MINTAGE_2026-10-27.md`
- PDFs / text: `/workspace/morgan_db/audit/gap_plans/tmp_fraser/usmint_1956_annual-report.pdf`, `usmint_1956.txt`, `usmint_1964_annual-report.pdf`, `usmint_1964_p50_90.txt`
- Prior cite pack to revise §11: `…/EVIDENCE_PACK_CITES_NET581_FOLDS_2026-10-27.md`
