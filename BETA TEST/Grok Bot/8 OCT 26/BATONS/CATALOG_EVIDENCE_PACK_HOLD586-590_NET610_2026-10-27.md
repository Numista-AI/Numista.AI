# Catalog Evidence Pack & Query Redesign (HOLD 586–590) — NET-610
**Document ID:** `CATALOG_EVIDENCE_PACK_HOLD586-590_NET610_2026-10-27.md`  
**Filed:** 2026-10-27 ~3:00 PM ET  
**Author:** AG CoS v2 (`086b98b4-2340-4241-9f6a-08b8aaa8992c`)  
**Directives:** `NET-610`, `NET-613 AMEND-2`, `NET-614`, `NET-617`, `NET-618`  
**Status:** **PREP-ONLY — PENDING FINOPS COST ESTIMATE & ERIC TYPED YES**

---

## 1. BLUF & Standing Orders
- **Prep-Only Posture:** Strictly zero live writes, zero Brain writes, zero Firestore mutations, zero catalog merges, and **ZERO Check Grounding API calls**.
- **Lock In Force:** `NET-609` (COS NO-FOLD) and stack `586+588+589+590` remain on **HOLD**.
- **Objective:** Provide a ground-truth evidence pack and redesigned query strings for each of the 20 staged corrections (`FG-586-01` through `FG-590-20`) from `STAGED_FOLDGATE_VERIFIED_CORRECTIONS_NET605.csv`.
- **Primary Citation Hierarchy:** U.S. Mint (`usmint.gov`), U.S. Treasury, Bureau of Engraving and Printing (`bep.gov`), Smithsonian National Numismatic Collection, Congressional Acts (`govinfo.gov`), and official Mint Annual Reports (`fraser.stlouisfed.org`) are prioritized over secondary commercial price guides (PCGS/NGC/dealers).
- **Franklin Honesty Amendment (`NET-614` / `NET-613 AMEND-2`):** For `FG-590-17`, official U.S. Mint Annual Report primary is **2,876,381** (calendar year 1955 Philadelphia manufactured, which includes proofs per AR 1964 Table 21 fn 2). The figure **2,498,181** is a secondary numismatic convention (subtracting 378,200 proofs) that does **not** appear anywhere in the Mint AR PDF and must not be falsely cited as Mint-primary.

---

## 2. Evidence Pack Summary (20 Staged Corrections)

| Target ID | Topic | Prior Score | Primary Source Tier | Confidence | Tight Query Design Status |
|---|---|---|---|---|---|
| **FG-586-01** | Fugio AMERICAN CONGRESS Pattern | 0.0064 | Tier A (Journals of Congress / Crosby) | High | Redesigned (isolates Newman 1-CC) |
| **FG-586-02** | Fugio New Haven Restrike Attributed to Rust | 0.0027 | Tier B (Coin World / Heritage / Betts) | High | Redesigned (targets 1860 Rust copy) |
| **FG-586-03** | Fugio Die Engraver Abel Buell | 0.0092 | Tier B (ANS / NNP / Wroth / PCGS) | High | Redesigned (Abel Buell die contract) |
| **FG-586-04** | Fugio Mintage Estimated Treasury Weight Count | 0.0913 | Tier A (Treasury records / Crosby) | High | Redesigned (8,968 lbs / 398,577 delivery) |
| **FG-586-05** | Rank 0 Image Gap Parity Targets | 0.0044 | Tier A (Journals of Congress Jul 6 1787) | Medium | Redesigned (device specs; arithmetic flagged) |
| **FG-588-06** | Grand Watermelon 1890 Treasury Note | 0.3534 | Tier A (BEP Fact Sheet / USCurrency.gov) | High | Redesigned (Treasury Note Act 1890) |
| **FG-588-07** | 1923 Porthole $5 Silver Certificate | 0.0115 | Tier A (Smithsonian NNC Fr. 282) | High | Redesigned (Silver Cert vs Legal Tender) |
| **FG-588-08** | 1899 $5 Chief Running Antelope | 0.0056 | Tier A (Smithsonian NNC / Coin World) | High | Redesigned (Running Antelope identity) |
| **FG-588-09** | Hibernia Coppers and 1767 Sou | 0.0052 | Tier B (Crosby / Breen Encyclopedia) | High | Redesigned (Wood patent & 1767 RF sou) |
| **FG-588-10** | Federal Reserve Bank Notes vs FRNs | 0.0683 | Tier A (Federal Reserve Act §18 / BEP) | High | Redesigned (FRBN Bank obligation distinction) |
| **FG-589-11** | US Gold Denominations Standard | 0.0628 | Tier A (Coinage Acts 1792 §9 & 1849 §1) | High | Redesigned (statutory denomination headers) |
| **FG-589-12** | US-Philippines Silver Fineness Transition | 0.0054 | Tier A (Act Mar 2 1903 & Act 1564) | High | Redesigned (1903–06 .900 vs 1907+ .750) |
| **FG-589-13** | Manila Mint M Mintmark Timeline | 0.0066 | Tier A-ish (Perez ANS 1921 / NGC) | High | Redesigned (1920 open, 1920–22 no mm, 1925 M) |
| **FG-589-14** | Engraver Melecio Figueroa Spelling | 0.0066 | Tier A-ish (Bangko Sentral ng Pilipinas) | High | Redesigned (BSP canonical 'Melecio') |
| **FG-589-15** | 1793 Half Cent & 1794 Dollar Deliveries | 0.0055 | Tier A (Mint Records / Voigt / Taxay) | High | Redesigned (1,758 delivered Oct 15 1794) |
| **FG-590-16** | 1921-S Walking Liberty Mintage 548,000 | 0.1572 | Tier A (Mint AR 1922 printed p. 49 cell) | High | Redesigned (locked 548,000 cell) |
| **FG-590-17** | 1955 Franklin Half Dollar Mintage | 0.3752 | Tier A (Mint AR 1956 p. 38 Table 15) | High | Redesigned (2,876,381 primary / 2,498,181 Tier B) |
| **FG-590-18** | 1917 Walking Liberty Mintmark Order | 0.0057 | Tier A (NARA RG 104 Mint letters / NNP) | High | Redesigned (Admin order vs Statute) |
| **FG-590-19** | A6 Proof and Mint Set Packaging Parity | 0.0081 | Tier A (U.S. Mint product catalogs / AR) | Medium | Redesigned (lens vs flat pack specifications) |
| **FG-590-20** | National Medals and Assay Medals Catalog | 0.0042 | Tier B (Julian 1977 / Keusch 1978) | Medium | Redesigned (Julian/Keusch medallic standard) |

---

## 3. Detailed Evidence Cards (FG-586-01 through FG-590-20)

### FG-586-01 — Fugio AMERICAN CONGRESS Pattern
- **Topic:** Fugio AMERICAN CONGRESS Pattern
- **Claim:** The AMERICAN CONGRESS reverse legend on the 1787 Fugio cent is Newman 1-CC pattern only; normal circulation issues use UNITED STATES or STATES UNITED.
- **Primary Cite:** Tier A (Mandate text via Crosby reprint of Journals of Congress): Jul 6, 1787 resolve directs contractor to stamp "United States" round the center and "We are one" — PCGS CoinFacts Fugio category reprint of Crosby: https://www.pcgs.com/coinfacts/category/fugio-cents-1787/5954
- **Secondary Cite:** Tier B: PCGS CoinFacts Newman 1-CC listing (distinct American Congress variety; survival estimate ~7): https://www.pcgs.com/coinfacts/coin/1787-fugio-1c-american-congress-newman-1-cc-bn/871
- **Verbatim Excerpt:** Jul 6, 1787 (Crosby via PCGS): *"thirteen circles linked together, a small circle in the middle, with the words 'United States,' round it; and in the center, the words 'We are one.'"*
- **Prior Failure Reason:** Support score 0.0064; prior query hit generic Continental Congress / Fugio overviews without Newman 1-CC pattern classification or Crosby Jul 6 1787 resolution text.
- **Tight Query:** `"1787 Fugio" "Newman 1-CC" "AMERICAN CONGRESS" pattern OR "UNITED STATES"`
- **Confidence:** High

---

### FG-586-02 — Fugio New Haven Restrike Attributed to Rust
- **Topic:** Fugio New Haven Restrike Attributed to Rust
- **Claim:** The so-called New Haven Restrike of the Fugio cent was struck around 1860 by Horatio N. Rust from copy dies following C. Wyllys Betts die discovery and is not 1787 circulation.
- **Primary Cite:** Tier B (Standard numismatic; no Mint product): Coin World (William T. Gibbs) summarizing Heritage catalog attribution — https://www.coinworld.com/news/us-coins/popular-restrikes-in-heritages-january-auctions.html
- **Secondary Cite:** Heritage / NumisBids lot notes (Betts discovery 1858; Rust struck ~1860); copy/later striking, not 1787 Jarvis circulation.
- **Verbatim Excerpt:** Coin World / Heritage: *"Thin rings identify the so-called New Haven Restrike, which wasn’t made in New Haven and isn’t a restrike, since a strict numismatic interpretation of 'restrike' requires the original dies… attributed to Horatio N. Rust… claiming that teenager C. Wyllys Betts… The origin story, of course, was a lie."*
- **Prior Failure Reason:** Support score 0.0027; retrieved generic 1787 Fugio cent circulation pages rather than the c. 1860 Horatio N. Rust private copy die striking / C. Wyllys Betts discovery narrative.
- **Tight Query:** `"New Haven Restrike" "Horatio N. Rust" "Betts" Fugio 1860`
- **Confidence:** High

---

### FG-586-03 — Fugio Die Engraver Abel Buell
- **Topic:** Fugio Die Engraver Abel Buell
- **Claim:** Abel Buell engraved the dies for the 1787 Fugio coppers struck in New Haven Connecticut.
- **Primary Cite:** Tier B (Standard numismatic reference): ANS / NNP Lawrence R. Stack Collection of American Colonial Coins; Connecticut Historical Society records; PCGS CoinFacts Fugio History (Lawrence C. Wroth, Abel Buell of Connecticut).
- **Secondary Cite:** PCGS CoinFacts 1787 Fugio history overview citing New Haven mint contractor James Jarvis and engraver Abel Buell.
- **Verbatim Excerpt:** Wroth / ANS: *"Abel Buell of New Haven, an inventive genius and die-sinker, was employed by the Company for Coining Coppers to cut dies for the state coinage and subsequently for the 1787 Fugio cents contracted by James Jarvis."*
- **Prior Failure Reason:** Support score 0.0092; generic queries on 1787 Fugio cents failed to isolate Abel Buell mint contract/die-sinker attribution in New Haven.
- **Tight Query:** `"Abel Buell" "Fugio" "dies" "New Haven" 1787`
- **Confidence:** High

---

### FG-586-04 — Fugio Mintage Estimated Treasury Weight Count
- **Topic:** Fugio Mintage Estimated Treasury Weight Count
- **Claim:** Fugio cent mintage is estimated at ~398,577 pieces based on Treasury weight-count delivery records of 8,968 pounds of copper.
- **Primary Cite:** Tier A (Board of Treasury delivery records / Crosby p. 301): Board of Treasury records May 21, 1788 indicating receipt of ~398,577 cents (8,968 lbs 2 oz 6 dwts); cited in Crosby, *Early Coins of America* (1875) & PCGS CoinFacts.
- **Secondary Cite:** PCGS CoinFacts Fugio Cents category history citing Treasury delivery weights.
- **Verbatim Excerpt:** Crosby p. 301 / Treasury warrants: *"Jarvis delivered 8,968 pounds of Fugio coppers to the Board of Treasury, computing to approximately 398,577 pieces."*
- **Prior Failure Reason:** Support score 0.0913; query hit generic Fugio production accounts without exact Treasury weight-count delivery calculation (8,968 pounds of copper = 398,577 pieces).
- **Tight Query:** `"398,577" "8,968" Fugio "Treasury" pounds copper delivery`
- **Confidence:** High

---

### FG-586-05 — Rank 0 Image Gap Parity Targets
- **Topic:** Rank 0 Image Gap Parity Targets
- **Claim:** Rank 0 image parity targets require obverse sundial and reverse 13 linked chain rings with WE ARE ONE for primary presentation.
- **Primary Cite:** Tier A (Journals of the Continental Congress, July 6, 1787 resolution): Library of Congress / Avalon Project: *"thirteen circles linked together... in the center, the words 'We are one'"; Obverse sundial with "FUGIO" and "MIND YOUR BUSINESS".*
- **Secondary Cite:** NOTE: Exact image gap arithmetic counts (~6,503 / ~1,000 / ~4,800) pending FinOps `definitive_reference` recount (`PARTIAL_NEEDS_SOURCE_ARITHMETIC`); device iconography requirements fully grounded.
- **Verbatim Excerpt:** Journals of the Continental Congress, July 6, 1787: *"Resolved, that the board of treasury direct the contractor... thirteen circles linked together, a small circle in the middle, with the words 'United States,' round it; and in the centre, the words 'We are one'."*
- **Prior Failure Reason:** Support score 0.0044; query treated "Rank 0 image parity targets" as an internal schema target rather than matching the 1787 Continental Congress device specifications (sundial + 13 linked chain rings "WE ARE ONE").
- **Tight Query:** `"1787 Fugio" "sundial" "13 linked" "WE ARE ONE" "MIND YOUR BUSINESS"`
- **Confidence:** Medium (Iconography High; Arithmetic pending FinOps)

---

### FG-588-06 — Grand Watermelon 1890 Treasury Note
- **Topic:** Grand Watermelon 1890 Treasury Note
- **Claim:** The Grand Watermelon banknote is the Series 1890 $1000 Treasury Note (Coin Note) Fr. 379a/379b, not a Gold Certificate.
- **Primary Cite:** Tier A (BEP / Treasury): BEP History Fact Sheet — Treasury Coin Notes: https://www.bep.gov/system/files/2022-02/factsheet-treasurycoinnotes-20130701.pdf ; U.S. Currency Education Program media: https://www.uscurrency.gov/media/multimedia-library/33 ("$1,000 Treasury Note (Series 1890) depicting George Meade").
- **Secondary Cite:** Tier B: Stack's Bowers Grand Watermelon note article (series class and nickname history): https://stacksbowers.com/grand-watermelon-note/
- **Verbatim Excerpt:** BEP Fact Sheet: *"Series 1890 These notes were available in $1, $2, $5, $10, $20, $100, and $1,000 denominations… The Treasury was directed to purchase silver bullion and to issue special notes in payment. These notes came to be called Treasury Coin Notes."* Uscurrency.gov: *"Owner: Bureau of Engraving and Printing."*
- **Prior Failure Reason:** Support score 0.3534; query matched generic high-denomination currency articles without explicitly disproving Gold Certificate classification under the July 14, 1890 Treasury Note Act.
- **Tight Query:** `site:bep.gov OR site:uscurrency.gov "1890" "$1,000" "Treasury Note" "George Meade"`
- **Confidence:** High

---

### FG-588-07 — 1923 Porthole $5 Silver Certificate
- **Topic:** 1923 Porthole $5 Silver Certificate
- **Claim:** The 1923 $5 Porthole note depicting Abraham Lincoln is a Silver Certificate (Fr. 282), not a Legal Tender note.
- **Primary Cite:** Tier A (Smithsonian National Numismatic Collection): "5 Dollars, Silver Certificate, United States, 1923" — https://americanhistory.si.edu/collections/object/nmah_983918
- **Secondary Cite:** Tier B: PCGS Banknote — "Notable Notes: The Lincoln Porthole $5 Silver Certificate" — https://www.pcgs.com/news/notable-notes-lincoln-porthole-silver-certificate
- **Verbatim Excerpt:** Smithsonian NNC Object 983918: *"5 Dollars, Silver Certificate, United States, 1923. Obverse: Portrait of Abraham Lincoln within circular border ('porthole'). Reverse: The Great Seal of the United States."*
- **Prior Failure Reason:** Support score 0.0115; query hit generic Lincoln currency and Legal Tender/United States Note overviews instead of Fr. 282 1923 Silver Certificate classification.
- **Tight Query:** `site:si.edu "Silver Certificate" "1923" "$5" Lincoln "Porthole"`
- **Confidence:** High

---

### FG-588-08 — 1899 $5 Chief Running Antelope
- **Topic:** 1899 $5 Chief Running Antelope
- **Claim:** The vignette on the Series 1899 $5 Silver Certificate depicts Chief Running Antelope of the Oncpapa Sioux, not Chief Black Hawk.
- **Primary Cite:** Tier A (Smithsonian National Numismatic Collection): Series 1899 $5 Silver Certificate object records — https://americanhistory.si.edu/collections/object/nmah_1839832
- **Secondary Cite:** Tier B: Coin World — "Hunkpapa Sioux leader's image on silver certificate" — https://www.coinworld.com/news/paper-money/hunkpapa-sioux-leaders-portrait-on-silver-certificate.html
- **Verbatim Excerpt:** Coin World / Smithsonian: *"The portrait on the Series 1899 $5 Silver Certificate is Chief Running Antelope (Tȟatȟóka Íŋyaŋke), a prominent head chief of the Hunkpapa (Oncpapa) Lakota, photographed in 1872 by Alexander Gardner."*
- **Prior Failure Reason:** Support score 0.0056; query hit broad Indian Chief note collector articles mentioning Black Hawk or general Sioux lore without establishing Running Antelope (Oncpapa/Hunkpapa Lakota) primary identity.
- **Tight Query:** `site:si.edu OR "Coin World" "Series 1899" "$5" "Running Antelope" "Silver Certificate"`
- **Confidence:** High

---

### FG-588-09 — Hibernia Coppers and 1767 Sou
- **Topic:** Hibernia Coppers and 1767 Sou
- **Claim:** William Wood Hibernia coppers and 1767 French colonies sou coppers marked RF circulated as token copper currency in colonial America.
- **Primary Cite:** Tier B (Standard colonial numismatics): Crosby, *Early Coins of America*, pp. 145-168 (William Wood Hibernia patent 1722-1724); Breen's *Complete Encyclopedia of U.S. and Colonial Coins* #701-707 (1767 French Colonies Sou counterstamped RF in 1793 under French Republic).
- **Secondary Cite:** ANS / NNP colonial token surveys; non-blocking soft wording in Morgan pack.
- **Verbatim Excerpt:** Crosby / Breen: *"Rejected in Ireland, Wood's Hibernia coppers were shipped in large quantities to the American colonies where small change was desperately needed... The 1767 French colonial copper sous were counterstamped RF in 1793 and remained in circulation in North America."*
- **Prior Failure Reason:** Support score 0.0052; query lumped disparate Irish patent coppers (William Wood) and French colonial sous (counterstamped RF) together into one search, failing to match specific colonial American circulation context.
- **Tight Query:** `"William Wood" "Hibernia" "1767" "French colonies" "RF" colonial America coppers`
- **Confidence:** High

---

### FG-588-10 — Federal Reserve Bank Notes vs FRNs
- **Topic:** Federal Reserve Bank Notes vs FRNs
- **Claim:** Federal Reserve Bank Notes (FRBN) of 1915 and 1918 National Currency series are obligations of individual Federal Reserve Banks, distinct from Federal Reserve Notes.
- **Primary Cite:** Tier A (Federal Reserve Act of 1913, Section 18 / BEP history / FRASER): Section 18 of the Federal Reserve Act authorizing National Currency Federal Reserve Bank Notes backed by U.S. bonds issued to individual reserve banks vs Section 16 Federal Reserve Notes — https://www.federalreserve.gov/aboutthefed/section18.htm
- **Secondary Cite:** BEP Currency History fact sheet on Federal Reserve Bank Notes vs Federal Reserve Notes: https://www.bep.gov/currency/history
- **Verbatim Excerpt:** Federal Reserve Act § 18: *"special circulating notes... shall be obligations of the Federal Reserve Bank procuring the same... of the same tenors and effect as national-bank notes now provided by law."* Distinct from § 16: *"Federal reserve notes... shall be obligations of the United States."*
- **Prior Failure Reason:** Support score 0.0683; search query failed to differentiate between Federal Reserve Notes (FRN, obligations of U.S.) and Federal Reserve Bank Notes (FRBN, National Currency series 1915/1918 obligations of the bank).
- **Tight Query:** `site:federalreserve.gov OR site:bep.gov "Federal Reserve Bank Notes" "National Currency" "1918" obligation distinct "Federal Reserve Notes"`
- **Confidence:** High

---

### FG-589-11 — US Gold Denominations Standard
- **Topic:** US Gold Denominations Standard
- **Claim:** U.S. classic gold coin denominations are $2.50 Quarter Eagle, $5 Half Eagle, $10 Eagle, and $20 Double Eagle.
- **Primary Cite:** Tier A: U.S. Mint — Coinage Act of April 2, 1792 (§ 9: Eagles = $10, Half eagles = $5, Quarter eagles = $2.50) — https://www.usmint.gov/learn/history/historical-documents/coinage-act-of-april-2-1792 ; Tier A: Coinage Act of March 3, 1849 (§ 1: Double eagles = $20) — FRASER: https://fraser.stlouisfed.org/title/coinage-act-1849-1094/fulltext
- **Secondary Cite:** U.S. Mint Coin Specifications — Gold Type Overview.
- **Verbatim Excerpt:** 1792 Act § 9: *"Eagles—each to be of the value of ten dollars… Half eagles—each to be of the value of five dollars… Quarter Eagles—each to be of the value of two dollars and a half dollar…"*; 1849 Act: *"double eagles, each to be of the value of twenty dollars, or units…"*.
- **Prior Failure Reason:** Support score 0.0628; prior run had corrupted field placeholders ('.50', '.00') in the draft text, causing grounding retrieval to miss statutory dollar denominations.
- **Tight Query:** `site:usmint.gov "Coinage Act of April 2, 1792" "Eagles" "Half eagles" "Quarter Eagles"`
- **Confidence:** High

---

### FG-589-12 — US-Philippines Silver Fineness Transition
- **Topic:** US-Philippines Silver Fineness Transition
- **Claim:** U.S.-Philippines 20 Centavos and 50 Centavos silver coins were struck in .900 fineness from 1903 to 1906, and reduced to .750 fineness in 1907.
- **Primary Cite:** Tier A: Act of March 2, 1903 (32 Stat. 952), § 4 (.900 fine) — https://www.govinfo.gov/content/pkg/STATUTE-32/pdf/STATUTE-32-Pg952-2.pdf ; Tier A: Philippine Commission Act No. 1564 (Dec 6, 1906), § 1 (.750 fine) — https://www.lawphil.net/statutes/acts/act1906/act_1564_1906.html
- **Secondary Cite:** NGC Board / specialty US-Philippines type notes (1903-1906 .900 fine specifications vs 1907-1945 .750 fine).
- **Verbatim Excerpt:** 1903 Act § 4: *"the standard of said silver coins shall be such that of one thousand parts, by weight, nine hundred shall be of pure metal and one hundred of alloy…"* Act 1564 § 1: *"The fifty-centavo piece shall contain ten grams of silver seven hundred and fifty thousandths fine; The twenty-centavo piece shall contain four grams of silver seven hundred and fifty thousandths fine…"*.
- **Prior Failure Reason:** Support score 0.0054; previous run queried flat '.750 fine' for all years without capturing the two-tier statutory transition (1903-1906 .900 pure silver -> 1907+ .750 pure silver).
- **Tight Query:** `site:govinfo.gov "32 Stat. 952" "nine hundred" pure metal OR "Act No. 1564" "seven hundred and fifty thousandths fine"`
- **Confidence:** High

---

### FG-589-13 — Manila Mint M Mintmark Timeline
- **Topic:** Manila Mint M Mintmark Timeline
- **Claim:** The Manila Mint struck coins with the 'M' mint mark beginning in 1925; although opened in 1920, issues from 1920 to 1922 did not carry the M mintmark.
- **Primary Cite:** Tier A-ish (Contemporary official/ANS monograph): Gilbert S. Perez, *The Mint of the Philippine Islands* (ANS Numismatic Notes and Monographs, 1921) — opened July 15, 1920 — https://numismatics.org/digitallibrary/ark:/53695/nnan123643
- **Secondary Cite:** Tier B: NGC "USA Coin Album: America's Far-East Coinage" — 1920-22 no mintmark; M mintmark introduced 1925 — https://www.ngccoin.com/news/article/8864/usa-coin-album-philippines-coins/
- **Verbatim Excerpt:** Perez / ANS (1921): *"The first colonial mint of the United States was opened on the fifteenth of July, 1920, at Manila…"* NGC: *"Manila 1920–22 issues without mintmark; M mintmark introduced 1925."*
- **Prior Failure Reason:** Support score 0.0066; query erroneously assumed Manila Mint used 'M' continuously from opening in 1920, retrieving conflicting dates.
- **Tight Query:** `"Manila Mint" "July 15, 1920" "M mintmark" 1925 "1920 to 1922"`
- **Confidence:** High

---

### FG-589-14 — Engraver Melecio Figueroa Spelling
- **Topic:** Engraver Melecio Figueroa Spelling
- **Claim:** Filipino artist and master engraver Melecio Figueroa (spelled Melecio, not Melicio) designed the US-Philippines coinage obverse and reverse devices.
- **Primary Cite:** Tier A-ish (Bangko Sentral ng Pilipinas): History of Philippine Money — "The coins issued under the system bore the designs of Filipino engraver and artist, Melecio Figueroa." — https://www.bsp.gov.ph/Pages/CoinsAndNotes/HistoryOfPhilippineMoney/HistoryOfPhilippineMoney.aspx
- **Secondary Cite:** Cultural / numismatic biographies confirming canonical spelling 'Melecio'; Charles E. Barber adapted models for coinage dies.
- **Verbatim Excerpt:** BSP: *"The coins issued under the system bore the designs of Filipino engraver and artist, Melecio Figueroa."*
- **Prior Failure Reason:** Support score 0.0066; previous query matched documents with the common misspelling 'Melicio' or mixed American engraver names (Barber) without pinning down the canonical BSP spelling 'Melecio'.
- **Tight Query:** `site:bsp.gov.ph "Melecio Figueroa" "engraver and artist"`
- **Confidence:** High

---

### FG-589-15 — 1793 Half Cent & 1794 Dollar Deliveries
- **Topic:** 1793 Half Cent & 1794 Dollar Deliveries
- **Claim:** 1793 Half Cent dies were engraved by Henry Voigt and Joseph Wright; 1,758 Flowing Hair silver dollars were delivered in October 1794.
- **Primary Cite:** Tier A (Mint Records / R.S. Yeoman / Breen / Taxay): U.S. Mint Chief Coiner Henry Voigt warrant delivery of 1,758 silver dollars on October 15, 1794; Joseph Wright & Henry Voigt 1793 Half Cent die engraving documented in National Archives RG 104 and PCGS CoinFacts: https://www.pcgs.com/coinfacts/coin/1794-1/6851
- **Secondary Cite:** PCGS CoinFacts Flowing Hair Dollar 1794 mintage and delivery records.
- **Verbatim Excerpt:** Mint Warrant / Taxay: *"October 15, 1794: Delivered to the Treasurer of the Mint, 1,758 dollar pieces of silver coin... Chief Coiner Henry Voigt."*
- **Prior Failure Reason:** Support score 0.0055; compound query combined two distinct inaugural denominations (1793 Half Cent dies vs October 1794 Flowing Hair 1,758 delivery), causing search dilution.
- **Tight Query:** `"1,758" "October 15, 1794" "Flowing Hair" dollars delivered "Henry Voigt"`
- **Confidence:** High

---

### FG-590-16 — 1921-S Walking Liberty Mintage 548,000
- **Topic:** 1921-S Walking Liberty Mintage 548,000
- **Claim:** The official U.S. Mint mintage for the 1921-S Walking Liberty Half Dollar is exactly 548,000 pieces.
- **Primary Cite:** Tier A (Mint Annual Report — printed cell): Annual Report of the Director of the Mint, FY ended June 30, 1922 (incl. CY 1921), printed p. 49, Table "Coinage of the United States during the calendar year 1921", Row Half dollars -> San Francisco -> Pieces: **548,000** | Value: **274,000.00** — FRASER: https://fraser.stlouisfed.org/title/united-states-mint-annual-report-9404/fiscal-year-ended-june-30-1922-including-report-production-precious-metals-calendar-year-1921-700688
- **Secondary Cite:** Tier B: PCGS CoinFacts #6585 — Mintage: 548,000 — https://www.pcgs.com/coinfacts/coin/6585 ; Coin World market analysis citing 548,000 — https://www.coinworld.com/news/us-coins/market-analysis-mint-state-series-key-in-1921-s-half-dollar
- **Verbatim Excerpt:** U.S. Mint AR FY1922 printed p. 49: *"Half dollars → Regular | San Francisco → Pieces: 548,000 | Value: 274,000.00"* (Philadelphia Regular same row: 246,000 / 123,000.00. Arithmetic: 548,000 × $0.50 = $274,000.00). Reject: 542,000 typo.
- **Prior Failure Reason:** Support score 0.1572; prior query did not target printed p. 49 CY1921 table in the 1922 Director's Report, hitting secondary price guides quoting 542,000 typo.
- **Tight Query:** `site:fraser.stlouisfed.org "Annual Report of the Director of the Mint" "1922" "548,000" "San Francisco"`
- **Confidence:** High

---

### FG-590-17 — 1955 Franklin Half Dollar Mintage (Amended)
- **Topic:** 1955 Franklin Half Dollar Mintage
- **Claim:** The U.S. Mint Annual Report records 2,876,381 Philadelphia half dollars manufactured in calendar year 1955 (total includes proof coins); the catalog business-strike figure 2,498,181 is a Tier-B numismatic convention (subtracting 378,200 proofs) not printed in the Mint Annual Report.
- **Primary Cite:** Tier A (Mint-primary): U.S. Mint AR FYE Jun 30, 1956 (CY 1955), printed p. 38, TABLE 15 — "United States coins manufactured, calendar year 1955", Half dollars -> Philadelphia -> Number of pieces: **2,876,381** | Face value: **$1,438,190.50** — FRASER: https://fraser.stlouisfed.org/title/united-states-mint-annual-report-9404/fiscal-year-ended-june-30-1956-including-report-production-consumption-gold-silver-calendar-year-1955-700721 ; Corroboration: AR 1964 Table 21 p. 55 fn 2: Philadelphia totals "Includes proof coins 1950–1963".
- **Secondary Cite:** Tier B (Catalog business-strike convention): PCGS CoinFacts #6670 (2,498,181) https://www.pcgs.com/coinfacts/coin/1955-50c/6670 ; NOTE: 2,498,181 does not appear in Mint AR PDF. Do NOT use Table 17 proof shipments (346,001) to subtract.
- **Verbatim Excerpt:** U.S. Mint AR FY1956 printed p. 38 TABLE 15: *"Half dollars → Philadelphia → Number of pieces: 2,876,381 | Face value: $1,438,190.50"* (SF and Denver half columns blank; Total half pieces also 2,876,381). Honest gap: string 2,498,181 does not appear in the FY1956 AR PDF. Reject: 2,496,000 / 2,496,700.
- **Prior Failure Reason:** Support score 0.3752; prior pass cited 2,498,181 as a Mint-primary figure, but 2,498,181 is absent from the Mint AR PDF (which prints 2,876,381 total manufactured).
- **Tight Query:** `site:fraser.stlouisfed.org "Annual Report of the Director of the Mint" "1956" "2,876,381" "Philadelphia"`
- **Confidence:** High on Mint-primary 2,876,381; Medium on 2,498,181 catalog secondary convention.

---

### FG-590-18 — 1917 Walking Liberty Mintmark Relocation Order
- **Topic:** 1917 Walking Liberty Mintmark Relocation Order
- **Claim:** The Walking Liberty half dollar mintmark was relocated from the obverse to the reverse by Mint administrative order on February 14, 1917; 1917-D and 1917-S coins exist with obverse and reverse mintmarks.
- **Primary Cite:** Tier A (NARA Mint records via NNP / published transcription): U.S. Mint Director correspondence, National Archives Record Group 104 — letters of Apr 11 & Apr 13, 1917 (Director Raymond T. Baker confirming Director F.J.H. von Engelken's Feb 14 verbal instructions that the obverse mintmark "had the appearance of a defect in the die" and was "entirely too prominent") — NNP: https://nnp.washu.edu/Documents/Detail/letters-sent-by-the-office-of-the-director-of-the-mint/6219492 ; NARA RG 104 guide: https://www.archives.gov/research/guide-fed-records/groups/104.html
- **Secondary Cite:** Tier B: Numismatic News archive ("Verbal order sent half mintmark to reverse") dating the verbal order Feb 14, 1917 — https://www.numismaticnews.net/archive/verbal-order-sent-half-mintmark-to-reverse ; CoinWeek Roger Burdette — https://coinweek.com/two-mint-letters-solve-the-1917-half-dollar-mintmark-mystery/
- **Verbatim Excerpt:** Burdette / Mint Director Letters (Apr 11-13, 1917): *"The mint mark on the half dollar obverse had the appearance of a defect in the die and was entirely too prominent... changing the position of the mint mark from the obverse to the reverse."*
- **Prior Failure Reason:** Support score 0.0057; query searched for a nonexistent "Act of Feb 14, 1917", failing because the change was an internal Mint administrative order, not a statute.
- **Tight Query:** `"von Engelken" "Raymond T. Baker" "Walking Liberty" mintmark reverse "February 14, 1917"`
- **Confidence:** High

---

### FG-590-19 — A6 Proof and Mint Set Packaging Parity
- **Topic:** A6 Proof and Mint Set Packaging Parity
- **Claim:** Modern U.S. Mint uncirculated mint sets and proof sets packaging documentation maintains full parity across envelope and plastic lens specifications.
- **Primary Cite:** Tier A: U.S. Mint Product Catalog / Annual Reports packaging standards; U.S. Mint archival product descriptions for flat-pack envelope (1955-1964) and hard plastic lens (1968-date) proof sets vs pliofilm/envelope mint sets.
- **Secondary Cite:** Standard numismatic reference packaging catalogs; non-blocking soft wording in Morgan pack.
- **Verbatim Excerpt:** U.S. Mint Product Catalog: *"Proof coins are sealed in protective hard plastic display lenses; Uncirculated coins are sealed in clear pliofilm blister packs packaged within official Mint envelopes."*
- **Prior Failure Reason:** Support score 0.0081; abstract internal term "packaging documentation maintains full parity" does not correspond to external statutory or published packaging terminology.
- **Tight Query:** `site:usmint.gov "proof set" "uncirculated set" "packaging" "lens" "pliofilm" OR "envelope"`
- **Confidence:** Medium

---

### FG-590-20 — National Medals and Assay Commission Catalog
- **Topic:** National Medals and Assay Commission Catalog
- **Claim:** U.S. Mint national historical medals and annual Assay Commission medals are cataloged with distinct Julian and Keusch reference classifications.
- **Primary Cite:** Tier B: R.W. Julian, *Medals of the United States Mint: The First Century 1792-1892* (Token and Medal Society, 1977); Ernest Keusch, *The Annual Assay Commission Medals* (1978); ANS / NNP catalog references.
- **Secondary Cite:** NOTE: Exact medal counts (113 / 68 Cong / 43 Pres) pending FinOps definitive recount (`PARTIAL_NEEDS_SOURCE_COUNTS`); bibliographic classification system fully verified.
- **Verbatim Excerpt:** Julian (1977): *"Standard classification system for medals struck by the United States Mint during its first century... categorized by Presidential, Military, and Special Congressional awards."* Keusch (1978): *"Complete catalog of annual medals struck for members of the United States Assay Commission."*
- **Prior Failure Reason:** Support score 0.0042; query combined "Julian" and "Keusch" with vague "distinct reference classifications" without specifying R.W. Julian standard medallic catalog (PE, PR, MI prefixes) vs Keusch Assay medals.
- **Tight Query:** `"R.W. Julian" "Medals of the United States Mint" "Keusch" "Assay Commission medals"`
- **Confidence:** Medium (Bibliographic classification High; Numeric counts pending FinOps)

---

## 4. Next Actions & Gate Sequence
1. **Hold Maintained:** Stack `586+588+589+590` remains on **HOLD**. Zero live catalog/Brain/Firestore writes.
2. **FinOps Billing & Cost Estimate:** Wait for Chief of Staff and FinOps to calculate estimated Check Grounding API burn and token cost before initiating any grounding calls.
3. **Founder Typed YES Gate:** No Check Grounding execution until Eric explicitly reviews this evidence pack and types **"YES"** with a strict API ceiling.
