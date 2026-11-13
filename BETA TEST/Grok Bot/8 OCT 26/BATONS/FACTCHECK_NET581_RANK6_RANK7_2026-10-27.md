# FACT-CHECK — NET-581 Rank 6–7 (Thin Evidence Packs A1–A7 + Medals P2)
**Filed:** 2026-10-27 ~11:45 AM ET (America/New_York)  
**Reviewer:** Morgan (US Numismatics Fact Checker) — independent SME  
**Input draft:** `DRAFT_GAPFILL_REPORT_NET581_RANK6_RANK7.md` (AG CoS ~10:12 PM ET 26 Oct)  
**Context:** `RECONCILED_TONIGHT_2026-10-26.md`  
**Mode:** REPORT-ONLY — no live catalog / Firestore / Brain writes  
**Style match:** `FACTCHECK_NET581_RANK4_RANK5_2026-10-27.md`

---

## 1. Executive verdict

### **PASS WITH CORRECTIONS**

Rank 6 thin-pack frames (A1 Mercury, A2 Walking Liberty, A3 Franklin, A4 Ike, A5 SBA, A7 Barber) are **largely Supported** at type / key-date / major-variety level. Designers, design descriptions, FSB/FBL-as-grade (not type), Ike reverse Types 1–3 + Bicentennial lettering Types 1–2, SBA Wide Rim / Proof S Types, and Barber key mintages hold. **A6 Fifty State Quarters correctly PRESERVED AS DONE** — zero re-scrape language; compliant with RECONCILED / FIN OPS.

**Blocking / high-priority corrections before any later merge:**

1. **1921-S Walking Liberty mintage** — Draft **542,000** is **wrong**. Correct Tier B figure: **548,000** (PCGS CoinFacts / Stack’s Bowers / Coin World consensus).
2. **1955 Franklin mintage** — Draft **2,496,000** is **wrong / rounded incorrectly**. Correct: **2,498,181** (PCGS CoinFacts circulation mintage).
3. **Walker mint-mark move “Act of Feb 14, 1917”** — Soften. Feb 14, 1917 was a **Mint / administrative (verbal) order**, **not** a Congressional Act. Also clarify **1917-D and 1917-S exist in both Obverse and Reverse mintmark placements**.

**Also fix / tighten:** Franklin “first non-presidential citizen” careful wording; SBA “first circulating real American woman” careful wording (commemoratives ≠ circulating); optional note Gilroy Roberts finished Franklin reverse after Sinnock’s death; Barber 1913-S “lowest 20th-c silver” claim is traditional Tier B Supported — keep with “regular business-strike” qualifier already present.

**Rank 7 Medals:** DONE posture **correctly preserved** (no forced expansion). Counts **113 total / 68 Cong / 43 Pres** are **UNVERIFIED** from local `/workspace/morgan_db` artifacts — no `definitive_reference` dump found to recount (same gap flagged in Rank 0–1). `backup_coins_13aug2026.json` = 4,992 coin collection rows with only ~18 medal-string hits — **not** proof of 113. Do **not** invent medal rows. Gap-fill only if FIN OPS later flags holes.

**Thin packs — do NOT force Supported:** Full Mercury / Walker / Franklin / Barber die-variety depth beyond named majors; Micro S exact punch-date genealogy beyond “Philippine coinage stock” tradition; Ike Type 2 population / hub chronology micro-detail; SBA Proof S punch genealogy; medals inventory arithmetic pending FinOps `definitive_reference`.

---

## 2. Evidence tables

### 2a. Mintage rows (mandatory) — every integer in the draft

| # | Issue (draft) | draft_value | Verdict | Mint-preferred / Tier B figure | source_url_1 | source_url_2 | confidence | tier |
|---|---|---|---|---|---|---|---|---|
| M-1 | 1916-D Mercury | **264,000** | **Supported** | 264,000 | https://www.pcgs.com/coinfacts/coin/1916-d-10c/4906 | https://stacksbowers.com/coin-resource-center/coin/1916-d-mercury-dime/ | High | B (aligns Mint annual reports tradition) |
| M-2 | 1921 Mercury | **1,230,000** | **Supported** | 1,230,000 | https://www.pcgs.com/coinfacts/coin/1921-10c/4934 | https://www.pcgs.com/news/semi-key-1921-mercury-dimes | High | B |
| M-3 | 1921-D Mercury | **1,080,000** | **Supported** | 1,080,000 | https://www.pcgs.com/coinfacts/coin/1921-d-10c/4936 | https://www.pcgs.com/news/semi-key-1921-mercury-dimes | High | B |
| M-4 | 1921 Walker | **246,000** | **Supported** | 246,000 | https://www.numismaticnews.net/item-of-the-week-walking-liberty-half-series-full-of-tough-dates | https://keydatecoins.com/1921-walking-liberty-half-dollar/ | High | B |
| M-5 | 1921-D Walker | **208,000** | **Supported** | 208,000 (lowest regular of series) | https://keydatecoins.com/1921-walking-liberty-half-dollar/ | https://www.numismaticnews.net/item-of-the-week-walking-liberty-half-series-full-of-tough-dates | High | B |
| M-6 | 1921-S Walker | **542,000** | **Contradicted** | **548,000** | https://www.pcgs.com/coinfacts/coin/6585 | https://stacksbowers.com/coin-resource-center/coin/1921-s-walking-liberty-half-dollar/ | High | B |
| M-7 | 1938-D Walker | **491,600** | **Supported** | 491,600 | https://www.numismaticnews.net/item-of-the-week-walking-liberty-half-series-full-of-tough-dates | https://mintagerecord.com/coins/walking-liberty-halves/ | High | B |
| M-8 | 1949-S Franklin | **3,744,000** | **Supported** | 3,744,000 | https://www.pcgs.com/coinfacts/coin/1949-s-50c/6655 | — | High | B |
| M-9 | 1953-S Franklin | **4,148,000** | **Supported** | 4,148,000 | https://www.pcgs.com/news/the-rare-1953-s-franklin-half-dollar-with-full-bell-lines | — | High | B |
| M-10 | 1955 Franklin | **2,496,000** | **Contradicted** | **2,498,181** | https://www.pcgs.com/coinfacts/coin/1955-50c/6670 | https://www.numismaticnews.net/collecting-101/coins-of-1955-why-were-the-mintages-so-low | High | B |
| M-11 | 1896-S Barber Q | **188,039** | **Supported** | 188,039 | https://www.pcgs.com/news/the-1896-s-barber-quarter-is-a-series-key | https://stacksbowers.com/coin-resource-center/us-coins/quarter-dollars/barber-quarter/ | High | B |
| M-12 | 1901-S Barber Q | **72,664** | **Supported** | 72,664 | https://www.pcgs.com/news/the-1896-s-barber-quarter-is-a-series-key | https://stacksbowers.com/coin-resource-center/us-coins/quarter-dollars/barber-quarter/ | High | B |
| M-13 | 1913-S Barber Q | **40,000** | **Supported** | 40,000 | https://www.pcgs.com/news/the-rare-1913-s-barber-quarter | https://www.pcgs.com/coinfacts/coin/1913-s-25c/5666 | High | B |

**Invented mintages check:** No freestyle invented integers found. Two draft integers are **wrong vs Tier B consensus** (M-6, M-10) — correct to cited figures; do not invent alternatives. No Tier A U.S. Mint public PDF re-fetched this turn for these classic dates; PCGS/Stack’s/NN figures are the standing Red Book–aligned tradition and are treated as Tier B OK where Mint has no conflicting public integer in local packs.

---

### 2b. Rank 6 — A1 Mercury Dimes

| # | Claim (draft) | draft_value | Verdict | proposed_correction | source_url_1 | source_url_2 | quote/excerpt | confidence | tier |
|---|---|---|---|---|---|---|---|---|---|
| A1-1 | Designer Adolph A. Weinman | as draft | **Supported** | Keep (Adolph Alexander Weinman). | https://www.pcgs.com/coinfacts/coin/1916-d-10c/4906 | https://en.wikipedia.org/wiki/Mercury_dime | PCGS Designer: Adolph Alexander Weinman. | High | B |
| A1-2 | Obverse winged Phrygian cap; “Mercury” misnomer; liberty of thought | as draft | **Supported** | Keep. | https://en.wikipedia.org/wiki/Mercury_dime | https://www.usmint.gov/ | Traditional Mint/Weinman Liberty-of-thought explanation. | High | B |
| A1-3 | Reverse fasces + olive branch | as draft | **Supported** | Keep. Soften “unity, authority, and readiness for peace” as interpretive OK. | https://en.wikipedia.org/wiki/Mercury_dime | — | Standard reverse devices. | High | B |
| A1-4 | 1942/1 and 1942/1-D overdates | as draft | **Supported** | Keep as major variety rows (doubled hub / overdate). Prefer catalog labels **1942/1** and **1942/1-D** (FS-101 family). | https://www.pcgs.com/news/six-classic-mercury-dime-key-dates-and-rarities | — | Classic Mercury overdates. | High | B |
| A1-5 | 1945-S Micro S from Philippine coinage punch stock | as draft | **Supported** (nuance) | Keep Micro S as variety row. Prefer: “Attributed to a smaller **S** punch associated with **U.S. Philippine** coinage punches at San Francisco (traditional attribution; exact punch inventory dates disputed in specialty lit).” | https://www.pcgs.com/news/the-lowdown-on-the-1945-s-micro-s-mercury-dime | https://www.pcgs.com/coinfacts/coin/5062 | PCGS/Stack’s: Micro S from Philippine punch tradition. | High (variety exists); Med (exact punch stock story) | B |
| A1-6 | FSB / FB = strike/grade, not type | as draft | **Supported** | Keep catalog rule. | https://www.pcgs.com/coinfacts/coin/4907 | — | FB is designation, not separate type. | High | B |

---

### 2c. Rank 6 — A2 Walking Liberty Halves

| # | Claim (draft) | draft_value | Verdict | proposed_correction | source_url_1 | source_url_2 | quote/excerpt | confidence | tier |
|---|---|---|---|---|---|---|---|---|---|
| A2-1 | Designer Adolph A. Weinman; striding Liberty; eagle on pine rock | as draft | **Supported** | Keep. | https://www.pcgs.com/news/mintmark-moved-walking-liberty-half-dollars | — | Standard Weinman design. | High | B |
| A2-2 | Mint mark 1916–1917 obverse; 1917–1947 reverse; “Act of Feb 14, 1917” | “Act of Feb 14, 1917” | **Weak** (Act) / **Supported** (placement change) | Prefer: “**1916 and early 1917:** mintmark (D/S) on **obverse** below IN GOD WE TRUST. **From mid-1917:** mintmark on **reverse** lower left. **1917-D and 1917-S exist in both Obverse and Reverse mintmark varieties.** Move ordered **Feb 14, 1917** by Mint administration (**verbal / administrative order** — **not** a Congressional Act); motive traditionally die-wear / mark appearing as defect.” | https://www.pcgs.com/news/mintmark-moved-walking-liberty-half-dollars | https://www.numismaticnews.net/archive/verbal-order-sent-half-mintmark-to-reverse | PCGS/NN: verbal order Feb 14, 1917; both 1917 placements exist. | High | B |
| A2-3 | Key dates 1921 / 1921-D / 1921-S / 1938-D | see mintage table | **Supported** except 1921-S figure | Fix 1921-S to **548,000**. Keep scarcity narratives (1921-S elusive in high grade despite higher mintage). | https://www.pcgs.com/coinfacts/coin/6585 | https://www.coinworld.com/news/us-coins/market-analysis-mint-state-series-key-in-1921-s-half-dollar | PCGS/CW: 548,000; MS key. | High | B |

---

### 2d. Rank 6 — A3 Franklin Halves

| # | Claim (draft) | draft_value | Verdict | proposed_correction | source_url_1 | source_url_2 | quote/excerpt | confidence | tier |
|---|---|---|---|---|---|---|---|---|---|
| A3-1 | Designer John R. Sinnock | as draft | **Supported** (nuance) | Prefer: “**John R. Sinnock** (obverse / overall design); after Sinnock’s 1947 death, **Gilroy Roberts** completed / refined reverse work for production.” Do not strip Sinnock credit. | https://www.usmint.gov/learn/history/historical-documents/new-half-dollar-design-benjamin-franklins-profile | https://www.pcgs.com/news/why-such-a-small-eagle-on-the-franklin-half-dollar | Mint historical doc + PCGS: Sinnock design; Roberts finish. | High | A / B |
| A3-2 | “first regular-issue non-presidential American citizen depicted on circulating US coinage” | as draft | **Supported** (careful) | Prefer tighter: “First **regular-issue circulating** U.S. coin to depict a **non-presidential historical American** (Benjamin Franklin). Prior regular portraits were presidents (Lincoln, Washington, Jefferson, FDR). Do **not** confuse with commemoratives (e.g., 1893 Isabella — Spanish queen, not circulating regular issue).” “Citizen” OK; avoid absolute “first American on a coin.” | https://en.wikipedia.org/wiki/Franklin_Half_Dollar | https://www.usmint.gov/learn/history/historical-documents/new-half-dollar-design-benjamin-franklins-profile | Traditional claim: first non-president on regular U.S. coin. | High | B / A-ish |
| A3-3 | Liberty Bell + small eagle; Act of 1873 eagle requirement above 25¢ | as draft | **Supported** | Keep. Prefer “Coinage Act / Revised Statutes tradition requiring an eagle on silver denominations larger than the dime.” | https://www.pcgs.com/news/why-such-a-small-eagle-on-the-franklin-half-dollar | — | PCGS: small eagle added to satisfy statute. | High | B |
| A3-4 | 1955 Bugs Bunny die clash | as draft | **Supported** | Keep as named clash variety (not separate type). Soften “buck teeth” as collector nickname OK. | https://www.pcgs.com/news/bugs-bunny-franklin-half-dollars | — | PCGS: clash with eagle wings → Bugs Bunny nickname. | High | B |
| A3-5 | FBL = condition attribute, not type | as draft | **Supported** | Keep. | https://www.pcgs.com/news/the-rare-1953-s-franklin-half-dollar-with-full-bell-lines | — | FBL is designation. | High | B |

---

### 2e. Rank 6 — A4 Eisenhower Dollars

| # | Claim (draft) | draft_value | Verdict | proposed_correction | source_url_1 | source_url_2 | quote/excerpt | confidence | tier |
|---|---|---|---|---|---|---|---|---|---|
| A4-1 | Designer Frank Gasparro | as draft | **Supported** | Keep. | https://www.ngccoin.com/news/article/812/1972-Eisenhower-Ike-Dollar-Types/ | — | Standard attribution. | High | B |
| A4-2 | CuNi clad vs 40% silver clad; 80% Ag clad / 20.9% Ag core; net 0.3161 oz | as draft | **Supported** | Keep compositional split. Silver = collector S issues (Proof / Uncirculated), not circulation CuNi. | https://www.ikegroup.info/?page_id=840 | https://www.usmint.gov/news/inside-the-mint/one-hundred-years-of-silver-dollar-coinage-1878-1978 | Outer 80% Ag; net ~0.3161 troy oz Ag. | High | B / A-ish |
| A4-3 | 1972 Type 1 / 2 / 3 reverse (islands / relief) | as draft | **Supported** | Keep. Prefer Type 2: “high-relief reverse from proof-hub family; Earth appears without the three islands; Florida as triangular landmass / smudge.” Type 1 low-relief + 3 islands; Type 3 improved high-relief + 3 islands. | https://www.ngccoin.com/news/article/812/1972-Eisenhower-Ike-Dollar-Types/ | https://www.pcgs.com/news/3-types-of-1972-eisenhower-dollars | NGC/PCGS Type 1–3 island/relief diagnostics. | High | B |
| A4-4 | Bicentennial 1776-1976 Type 1 bold vs Type 2 delicate lettering | as draft | **Supported** | Keep. Prefer: Type 1 = bold / thick sans-like lettering (mostly 1975-dated production for dual-date); Type 2 = thinner / sharper lettering with improved definition (1976 production). Dual date **1776–1976** on all. | https://learn.apmex.com/learning-guide/coin-collecting/errors/what-are-the-reverse-die-varieties-of-eisenhower-dollars/ | https://www.ngccoin.com/news/article/10538/usa-coin-album-eisenhower-dollar/ | APMEX/NGC Bicentennial lettering types. | High | B |

**Ike mintages:** Draft invents **none**. Compliant.

---

### 2f. Rank 6 — A5 Susan B. Anthony Dollars

| # | Claim (draft) | draft_value | Verdict | proposed_correction | source_url_1 | source_url_2 | quote/excerpt | confidence | tier |
|---|---|---|---|---|---|---|---|---|---|
| A5-1 | Designer Frank Gasparro; hendecagonal inner border | as draft | **Supported** | Keep. | https://www.ngccoin.com/news/article/11531/face-value-anthony-dollar/ | — | 11-sided inner border to aid vending differentiation. | High | B |
| A5-2 | “First circulating US coin honoring an actual real American woman” | as draft | **Supported** (careful) | Prefer: “First **circulating** U.S. coin to depict a **historical American woman** (Susan B. Anthony). Commemoratives (e.g., 1893 Isabella quarter — Spanish queen) do not count as circulating regular-issue. Soften ‘actual real’ → ‘historical American woman.’” | https://www.ngccoin.com/news/article/11531/face-value-anthony-dollar/ | — | NGC: first regularly circulating U.S. coin depicting an actual woman. | High | B |
| A5-3 | 1979-P Wide Rim / Near Date | as draft | **Supported** | Keep. Prefer dual label **Wide Rim / Near Date** (PCGS FS-301). Philadelphia circulation only for this variety framing. | https://www.pcgs.com/news/1979-near-date-susan-b-anthony-dollars | https://www.pcgs.com/coinfacts/coin/1979-p-sba-1-wide-rim/99571 | PCGS Near Date / Wide Rim. | High | B |
| A5-4 | 1979-S Type 1 Filled S vs Type 2 Clear S; 1981-S Type 1 Flat vs Type 2 Clear | as draft | **Supported** | Keep Proof S-type splits. | https://www.ngccoin.com/news/article/11531/face-value-anthony-dollar/ | — | Standard Proof S Type 1/2 distinctions. | High | B |
| A5-5 | 1999-P/D re-authorized for vending / transit before Sacagawea | as draft | **Supported** | Keep. | https://www.ngccoin.com/news/article/11531/face-value-anthony-dollar/ | — | 1999 revival ahead of Sacagawea. | High | B |

**SBA mintages:** None invented. Compliant.

---

### 2g. Rank 6 — A6 Fifty State Quarters (DONE check)

| # | Claim (draft) | draft_value | Verdict | proposed_correction | source_url_1 | source_url_2 | quote/excerpt | confidence | tier |
|---|---|---|---|---|---|---|---|---|---|
| A6-1 | PRESERVED AS DONE; zero re-scraping | as draft | **Supported** | Keep. Matches RECONCILED “A6 State Quarters · DONE” and FIN OPS inventory instruction. **Do not** expand or re-scrape. | `RECONCILED_TONIGHT_2026-10-26.md` | `PRIORITY_GAP_CHECKLIST_FUGIO_TO_2026_2026-10-26.md` | RECONCILED: A6 DONE — DO NOT REDO. | High | project |

---

### 2h. Rank 6 — A7 Barber Quarters

| # | Claim (draft) | draft_value | Verdict | proposed_correction | source_url_1 | source_url_2 | quote/excerpt | confidence | tier |
|---|---|---|---|---|---|---|---|---|---|
| A7-1 | Designer Charles E. Barber; Liberty head + heraldic eagle | as draft | **Supported** | Keep. | https://stacksbowers.com/coin-resource-center/us-coins/quarter-dollars/barber-quarter/ | — | Standard Barber type. | High | B |
| A7-2 | Keys 1896-S / 1901-S / 1913-S mintages | see mintage table | **Supported** | Keep integers. Note: **1901-S** is often rarer in circulated grades than lower-mintage **1913-S** (survival ≠ mintage). | https://stacksbowers.com/coin-resource-center/us-coins/quarter-dollars/barber-quarter/ | https://www.pcgs.com/news/the-1896-s-barber-quarter-is-a-series-key | Stack’s: rarity order ≠ mintage order. | High | B |
| A7-3 | 1913-S = lowest regular business-strike mintage in 20th-c US silver | as draft | **Supported** (traditional) | Keep with existing “regular business strike” qualifier. Traditional Tier B claim for 40,000. | https://www.pcgs.com/news/the-rare-1913-s-barber-quarter | https://www.numismaticnews.net/collecting-101/1913-s-barber-no-place-go | PCGS/NN: lowest-mintage regular 20th-c silver business strike. | High | B |

---

### 2i. Rank 7 — Medals P2

| # | Claim (draft) | draft_value | Verdict | proposed_correction | source_url_1 | source_url_2 | quote/excerpt | confidence | tier |
|---|---|---|---|---|---|---|---|---|---|
| P2-1 | Cong 68 + Pres 43 = 113 in definitive_reference | 68 / 43 / 113 | **UNVERIFIED** | Do **not** force Supported. Mark **UNVERIFIED pending FIN OPS `definitive_reference` recount**. Local check: no definitive_reference dump under `/workspace/morgan_db`; `backup_coins_13aug2026.json` = 4,992 rows / ~18 medal-string hits — **not** corroboration of 113. Same UNVERIFIED posture as Rank 0–1 image-gap arithmetic. | `RECONCILED_TONIGHT_2026-10-26.md` | Rank 0–1 FACTCHECK local inventory note | RECONCILED: medals DONE/strong; P2 last / gap-fill only if holes. | Low (counts) / High (DONE posture) | project |
| P2-2 | Series solid DONE; no immediate gaps; no unnecessary expansion | as draft | **Supported** (posture) | Keep DONE / no-forced-expansion. Gap-fill **only** if FIN OPS later flags holes. **Do not invent medal rows.** | `RECONCILED_TONIGHT_2026-10-26.md` | `PRIORITY_GAP_CHECKLIST_FUGIO_TO_2026_2026-10-26.md` | P2 medals last / holdings already strong. | High | project |

---

## 3. Unresolved for Eric EOD

1. **1921-S Walker display** — Confirm catalog shows **548,000** (not 542,000). Any source that still prints 542k should be treated as typo vs PCGS/Stack’s/CW.
2. **1955 Franklin display** — Confirm **2,498,181** (not 2,496,000). Was 2,496,000 a Red Book rounding / proof-exclusion artifact in an AG source?
3. **Walker mint-mark education** — UI: always show **1917 Obverse vs Reverse mintmark** as distinct varieties for D and S?
4. **Franklin / SBA significance copy** — Adopt tightened “first regular-issue circulating…” / “first circulating historical American woman” language for Numista.Ai cards?
5. **Medals 113 / 68 Cong / 43 Pres** — Needs FinOps `definitive_reference` recount before any medals UI badge or gap math. Until then: **DONE posture only; no expansion; counts UNVERIFIED.**
6. **Tier A Mint PDF re-pull** — Classic 1916–1955 mintages not re-verified against a live Mint annual-report PDF this turn (ADC/FinOps morning re-check still pending per CoS). If Mint public integer ever diverges from PCGS, Mint wins.

---

## 4. Exact wording fixes (old → new)

### Fix A — 1921-S Walker mintage (**priority / blocking**)
**OLD:** `1921-S: 542,000 (Extremely elusive in higher grades).`  
**NEW:** `1921-S: **548,000** (higher mintage than 1921 / 1921-D but extremely elusive in higher Mint State grades).`

### Fix B — 1955 Franklin mintage (**priority / blocking**)
**OLD:** `1955: 2,496,000 ("Bugs Bunny" die clash variety — …).`  
**NEW:** `1955: **2,498,181** (lowest regular business-strike mintage of the Franklin series). Separately catalog the **"Bugs Bunny"** die-clash variety (obverse clash with reverse eagle wings → buck-teeth nickname) as a variety / attribution — not a mintage.**

### Fix C — Walker mint-mark move (**priority**)
**OLD:** `1917–1947: Mint mark moved to Reverse … (Act of Feb 14, 1917 design adjustment to avoid obverse die wear).`  
**NEW:** `1916 + early 1917: mintmark (D/S) on **obverse** below IN GOD WE TRUST. Mid-1917 onward: mintmark on **reverse** lower left. **1917-D and 1917-S exist in both Obverse and Reverse mintmark varieties.** Placement change ordered **Feb 14, 1917** by Mint administration (**verbal / administrative order — not a Congressional Act**); traditional motive = obverse mark looking like a die defect / wear concern.`

### Fix D — Franklin “first citizen” wording
**OLD:** `… first regular-issue non-presidential American citizen depicted on circulating US coinage.`  
**NEW:** `First **regular-issue circulating** U.S. coin to depict a **non-presidential historical American** (Benjamin Franklin). Prior regular circulating portraits were U.S. presidents. Commemoratives are out of scope for this claim.`

### Fix E — SBA “first woman” wording
**OLD:** `First circulating US coin honoring an actual real American woman.`  
**NEW:** `First **circulating** U.S. coin to depict a **historical American woman** (Susan B. Anthony). (1893 Isabella commemorative = Spanish queen / non-circulating commemorative — not a counterexample.)`

### Fix F — Sinnock / Roberts (non-blocking polish)
**OLD:** `Designer: John R. Sinnock.`  
**NEW:** `Designer: **John R. Sinnock** (principal); reverse production finish associated with **Gilroy Roberts** after Sinnock’s 1947 death.`

### Fix G — Micro S attribution (non-blocking tighten)
**OLD:** `1945-S Micro S (repunched small mint mark punch from Philippine coinage stock).`  
**NEW:** `1945-S Micro S — smaller S mintmark variety traditionally attributed to a **Philippine-coinage** punch at San Francisco (specialty literature; exact punch inventory dates disputed). Catalog as major variety row.`

---

## 5. Explicit thin / don’t-force-Supported flags

| Pack | Status | Guidance |
|---|---|---|
| Mercury full die varieties beyond 1942/1, 1942/1-D, Micro S | Thin | Named majors Supported; don’t force census |
| Micro S punch-date genealogy | Specialty thin | Traditional PH punch OK; don’t invent punch serials |
| Walker full die varieties / 1916-S low-mintage depth | Thin beyond keys | Keys Supported; depth later |
| Franklin full clash / DDR matrix beyond Bugs Bunny | Thin | Bugs Bunny OK; don’t force full clash set |
| Ike Type 2 population / hub chronology micro-detail | Thin | Types 1–3 Supported; no invented pops |
| SBA Proof S punch genealogy | Thin | Type 1/2 Supported; no invented punch IDs |
| Barber full die varieties | Thin beyond three keys | Keys Supported |
| A6 State Quarters | **DONE — preserved** | No re-scrape |
| Medals 113 / 68 / 43 arithmetic | **UNVERIFIED** | DONE posture only; no invented rows |
| Any mintage not in draft | — | Do not invent |

---

## 6. Invented mintages check

| Location | Figure | Finding |
|---|---|---|
| 1916-D / 1921 / 1921-D Mercury | 264k / 1.23M / 1.08M | **Supported** Tier B — not invented |
| 1921 / 1921-D / 1938-D Walker | 246k / 208k / 491.6k | **Supported** Tier B — not invented |
| **1921-S Walker** | **542,000** | **Contradicted** — correct to **548,000** (not invent a third figure) |
| 1949-S / 1953-S Franklin | 3,744,000 / 4,148,000 | **Supported** Tier B |
| **1955 Franklin** | **2,496,000** | **Contradicted** — correct to **2,498,181** |
| Barber 1896-S / 1901-S / 1913-S | 188,039 / 72,664 / 40,000 | **Supported** Tier B |
| Ike / SBA / medals | — | **No mintage integers invented** in those sections |

---

## 7. NET-581 ranks 0–7 SME status (roll-up stub)

- **Rank 0–1** (`FACTCHECK_NET581_RANK0_RANK1_2026-10-27.md`): **PASS WITH CORRECTIONS** — Fugio core Supported; blockers = AMERICAN CONGRESS = Newman 1-CC pattern only; New Haven = copy/later (Betts discovery / Rust struck), not 1787; Rank-0 image-gap counts UNVERIFIED.
- **Rank 2–3** (`FACTCHECK_NET581_RANK2_RANK3_2026-10-27.md`): **PASS WITH CORRECTIONS** — colonial types largely Supported; blockers = Grand Watermelon = 1890 $1000 Treasury Note (not Gold Cert); 1923 Porthole $5 = Silver Certificate (not LT); Chief Running Antelope (not Black Hawk); N5 FRN/FRBN missing vs RECONCILED.
- **Rank 4–5** (`FACTCHECK_NET581_RANK4_RANK5_2026-10-27.md`): **PASS WITH CORRECTIONS** — early-federal + US-PH largely Supported; blockers = gold headers → $2.50/$5/$10/$20; PH 20¢/50¢ .900 then .750; Manila M from 1925; Melecio spelling; no invented mintages (1794 dollar 1,758 = Tier A).
- **Rank 6–7** (this file): **PASS WITH CORRECTIONS** — A1–A5/A7 largely Supported; **A6 DONE correctly preserved**; blockers = **1921-S Walker 548,000** (not 542k) + **1955 Franklin 2,498,181** (not 2,496k) + soften “Act of Feb 14, 1917”; medals DONE posture OK, **113/68/43 UNVERIFIED** pending FinOps — no forced medal expansion.
- **Cross-cutting:** All ranks report-only; **no live catalog / Firestore / Brain writes**; Mint/Treasury wins on mintage conflicts; thin packs not forced Supported; FinOps `definitive_reference` recount still needed for Rank-0 image-gap + Rank-7 medal counts.
- **Overnight routing note:** Drafts sat in BATONS/`dev` without prior Morgan wake; SME completed 0–7 morning of 27 Oct 2026 ET after CoS/Desk GO.
- **Ready for CoS merge gate only after** listed blocking fixes are applied in sandbox drafts — still **no live writes** until Eric / CoS authorize.

---

## Sign-off

- **Overall:** **PASS WITH CORRECTIONS**
- **Blocking for later live merge:** Fix A (1921-S = 548,000), Fix B (1955 = 2,498,181), Fix C (mint-mark order ≠ Act; both 1917 placements).
- **Strongly recommended:** Fix D–E (Franklin / SBA significance wording).
- **Non-blocking polish:** Fix F–G (Roberts; Micro S tighten).
- **A6 DONE:** **preserved correctly** — no re-scrape.
- **Medals:** DONE posture **correct**; counts **UNVERIFIED** locally — **do not invent medal rows**.
- **No invented mintages** beyond the two **wrong** draft integers corrected above.
- **No live catalog / Firestore / Brain writes performed.**
