# Mint AR mintage check: 1921-S Walker and 1955 Franklin (2026-10-27)
Read-only. No gcloud, no Agent Builder, no spend.

FRASER index: https://fraser.stlouisfed.org/title/united-states-mint-annual-report-9404  
FY1922 issue: https://fraser.stlouisfed.org/title/united-states-mint-annual-report-9404/fiscal-year-ended-june-30-1922-including-report-production-precious-metals-calendar-year-1921-700688

## BLUF for NET-610 pack (CoS lock ~1:58 PM ET 27 Oct)
| Coin | Mint-primary (AR) | Secondary only | Reject |
|---|---|---|---|
| **1921-S Walking Liberty half** | **548,000** (AR p.49) | — | 542,000 |
| **1955 Franklin half (Philadelphia)** | **2,876,381** (AR p.38 TABLE 15, incl. proofs in that cell) | **2,498,181** PCGS/catalog business-strike — **not** Mint-primary | 2,496,000 / 2,496,700 |

CoS withdrew the medium-derived subtract as Mint-primary. Prior “use 2,498,181 from AR” language below is historical only — see Exact cell quotes / CoS amend.

## 1) 1921-S Walking Liberty half — CONFIRMED **548,000**
- File: `/workspace/morgan_search/docs/annualreportofdi1922unit.txt` (Director of the Mint AR, fiscal year ended 30 Jun 1922).
- Table: “Coinage of the United States during the **calendar year 1921**” (~L9558–9658).
- **Half dollars → Regular → San Francisco: 548,000 pieces; value $274,000.00** (548,000 × $0.50 = $274,000 — checks).
- Philadelphia Regular half: 246,000 / $123,000.00. Other half rows are commemoratives (Pilgrim / Missouri / Alabama).
- **542,000** appears in `/workspace/morgan_search/docs/annualreportofdi1921unit_b7v1.txt` but **not** as a clean SF half-dollar mintage cell — do not use.
- Morgan’s **548,000** matches the Mint AR. OK for the evidence pack.

## 2) 1955 Franklin half — use **2,498,181** (business); do not use 2,496k
- Correct AR file for **calendar year 1955** coinage: `/workspace/morgan_search/docs/annualreportofdi1957unit.txt` (title page: fiscal year ended 30 Jun **1956**), Table 15 (~L4758).
- Wrong file for this check: `annualreportofdi1956unit.txt` is FY ended 30 Jun **1955** with **calendar year 1954** tables.
- Philadelphia half dollars in CY1955 table: **2,876,381** pieces; face **$1,438,190.50** (checks at × $0.50). OCR lost the clean proof vs business breakout that CY1954 tables show as a separate half line.
- **2,876,381 − 378,200 = 2,498,181**. The 378,200 proof-set figure is the standard catalog proof mintage for 1955; it was **not** found as its own line in this OCR. So **2,498,181 is the business-strike figure consistent with the AR total**, matching PCGS CoinFacts, but it is **not** a standalone printed AR cell in our text.
- **Reject 2,496k:** in the CY1954 table (`annualreportofdi1956unit.txt` ~L4925), **$2,496,700.00** is San Francisco half-dollar **face value** (pieces 4,993,400 × $0.50) — a value column, not a 1955 mintage.
- Pack citation tip: cite AR CY1955 Phil half **2,876,381** (incl. proofs) and state business-strike **2,498,181** = AR total − 1955 proof sets **378,200**, with Tier B corroboration if CoS wants a second source.

## Not authorized
No Agent Builder / Check Grounding re-run from this note. Wed 28 Oct 1:00 PM ET Week-1+fold billing reconcile unchanged.

## Exact cell quotes for NET-612 (2026-10-27 re-OCR / PDF page check)

Sources pulled this turn (no Agent Builder / no gcloud):
- IA PDF `annualreportofdi1922unit` → `/workspace/roi/mint_ar_pdfs/annualreportofdi1922unit.pdf` (FRASER item 700688)
- IA PDF `annualreportofdi1957unit` (FY ended 30 Jun **1956**, CY **1955**) → `/workspace/roi/mint_ar_pdfs/annualreportofdi1957unit.pdf` (FRASER item 700721)
- Page PNGs: `FY1922_p49_CY1921_coinage.png`, `FY1956_p38_TABLE15_CY1955.png`, `FY1956_p39_TABLE17_proof_footnote.png`

### FG-590-16 — 1921-S Walking Liberty half — **PRINTED CELL = 548,000**

**Paste-ready quote:**

> U.S. Mint, *Annual Report of the Director of the Mint*, fiscal year ended June 30, 1922 (incl. CY 1921). Printed **p. 49**. Table: **“Coinage of the United States during the calendar year 1921.”**  
> Row: **Half dollars: → Regular**  
> Column: **San Francisco → Pieces: 548,000** | **Value: 274,000.00**  
> (Same row Philadelphia Regular: 246,000 / 123,000.00. Face check: 548,000 × $0.50 = $274,000.00.)

Reject **542,000** — not this SF Regular half cell.

### FG-590-17 — 1955 Franklin Philadelphia — **2,498,181 is NOT a printed AR cell**

**Paste-ready quote (what the AR actually prints):**

> U.S. Mint, *Annual Report of the Director of the Mint*, fiscal year ended June 30, 1956 (incl. CY 1955). Printed **p. 38**. **TABLE 15. — United States coins manufactured, calendar year 1955.**  
> Row: **Half dollars..........**  
> Column: **Philadelphia Mint → Number of pieces: 2,876,381** | **Face value: $1,438,190.50**  
> (SF and Denver half columns blank/“—”; Total half pieces also **2,876,381**. Face check: 2,876,381 × $0.50 = $1,438,190.50.)  
> Table 15 footnotes do **not** break out proof vs business; footnote 2 is SF-only (“Production for January, February, and March only…”).

**Honest gap on 2,498,181:**
- String **`2,498,181` does not appear** anywhere in the FY1956 AR PDF text or on TABLE 15 page image.
- Nearby proof footnote is on **TABLE 17** (printed **p. 39**), shipments CY1955: **“Includes 346,001 sets of proof coins sold by the Philadelphia Mint.”** That is **not** the catalog 378,200 figure, and TABLE 17 is shipments (all mints), not Phil half mintage.
- Therefore **do not cite 2,498,181 as an AR cell**. If the pack needs a business-strike figure, cite AR Phil half **2,876,381** (incl. whatever proofs the Mint rolled into that cell) and treat **2,498,181** as Tier-B/catalog-derived (commonly 2,876,381 − 378,200), **not** Mint AR primary.

Keep PCGS/catalog secondary until CoS accepts a non-AR source. **Do not invent** alternate mintages.
