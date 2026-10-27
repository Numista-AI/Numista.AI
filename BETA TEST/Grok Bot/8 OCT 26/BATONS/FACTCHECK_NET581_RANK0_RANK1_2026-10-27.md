# FACT-CHECK — NET-581 Rank 0–1 (Fugio + Image Parity)
**Filed:** 2026-10-27 ~10:15 AM ET (America/New_York)  
**Reviewer:** Morgan (US Numismatics Fact Checker) — independent SME  
**Input draft:** `DRAFT_GAPFILL_REPORT_NET581_RANK0_RANK1.md` (AG CoS ~8:50 PM ET 26 Oct)  
**Mode:** REPORT-ONLY — no live catalog / Firestore / Brain writes  

---

## 1. Executive verdict

### **PASS WITH CORRECTIONS**

Core Rank-1 Fugio narrative (Confederation authorization, Jarvis/New Haven contract, Franklin-inspired sundial design, reverse chain/WE ARE ONE, Pointed vs Club Rays, UNITED STATES vs STATES UNITED, Estimated/Disputed mintage, copper ~157.5 grains / ~28–29 mm, sundial as primary card image) is **Supported** against Tier A/B sources.

Corrections required before any future merge (still report-only tonight):

- **Reverse legend hierarchy** is inverted in the draft: circulation issues use **UNITED STATES / STATES UNITED**; **AMERICAN CONGRESS** is the ultra-rare Newman 1-CC **pattern**, not a peer “or variant.”
- **New Haven Restrike** must not be attributed as “struck by C. Wyllys Betts.” Betts is tied to the die discovery story; **Horatio N. Rust** struck the mid-19th-c pieces; modern literature treats them as **copy dies / misnamed “restrikes”** (not true restrikes from original 1787 production dies)—still **not** 1787 circulation.
- Optional strengtheners: name **Abel Buell (Buel)** as die engraver; cite Treasury weight-count **~398,577** as the best Estimated figure while keeping Estimated/Disputed (no invented single integer as “official Mint” fact).
- Rank-0 **parity rules and priority targets are sound**; the **~6,503 / ~1,000 / ~4,800 image-gap counts are UNVERIFIED** from local `/workspace/morgan_db` artifacts (no `definitive_reference` dump found to corroborate).

---

## 2. Evidence table — Rank 1 (1787 Fugio Cent)

| # | Claim (draft) | draft_value | Verdict | proposed_correction | source_url_1 | source_url_2 | quote/excerpt | confidence | tier |
|---|---|---|---|---|---|---|---|---|---|
| 1a | Authorized Apr 21, 1787 | Resolution of Congress of the Confederation Apr 21 & Jul 6, 1787 | **Supported** | Keep both dates; specify Apr 21 = contract authority (300 tons copper coin, federal standard, Jarvis); Jul 6 = design mandate. | https://docsouth.unc.edu/csr/index.html/document/csr20-0098 | https://www.pcgs.com/coinfacts/category/fugio-cents-1787/5954 | “Resolved, That the board of treasury be… authorized to contract for three hundred tons of copper coin, of the Federal Standard, agreeably to the proposition of Mr. James Jarvis” (Apr 21, 1787). | High | A (JCC via DocSouth) / B (PCGS reprint of Crosby quoting JCC) |
| 1b | Authorized Jul 6, 1787 (design) | same | **Supported** | Keep; quote device text in notes. | https://www.pcgs.com/coinfacts/category/fugio-cents-1787/5954 | https://www.pcgs.com/books/garret/Chapter05/18 | “Friday, July 6, 1787… stamp… thirteen circles linked together… 'United States,'… 'We are one;'… dial… 'Fugio,'… '1787'… 'Mind your Business.'” | High | B citing A (Journals of Congress) |
| 2 | Contractor James Jarvis / Company for Coining Coppers, New Haven CT | James Jarvis (Company for Coining Coppers, New Haven, CT) | **Supported** (nuance) | Prefer: “Contractor **James Jarvis** (Jarvis & Co.), New Haven, CT; production associated with the Connecticut copper works (historically the Company for Coining Coppers / Broome & Platt circle). Dies by **Abel Buell**.” Do not imply a single neat corporate identity for all 1787 striking. | https://americanhistory.si.edu/collections/object/nmah_1096631 | https://stacksbowers.com/bank-of-new-york-hoard-of-fugio-coppers/ | Smithsonian: “James Jarvis, a Connecticut coiner, was selected…” Stack’s: “struck at James Jarvis’ mint in New Haven… Engraved by Abel Buell.” | High (Jarvis/New Haven); Med (exact company name) | A (Smithsonian NNC) / B (Stack’s Bowers) |
| 3 | First official US coin under Articles of Confederation | “First official coin authorized by the United States government under the Articles of Confederation.” | **Supported** (careful wording OK) | Prefer slightly tighter: “**First circulating copper coinage authorized by the United States in Congress assembled under the Articles of Confederation** (contract issue; pre–U.S. Mint).” Avoid bare “first US coin” without Confederation/contract context. | https://americanhistory.si.edu/collections/object/nmah_1096631 | https://www.pcgs.com/news/fugio-cents-the-first-regular-issue-united-states-coin | Smithsonian: “resolved in 1787 to issue the **first national coinage**, copper cents now known as ‘Fugio Cents.’” PCGS 2022: “first regular-issue United States coin, duly authorized by Congress acting under the Articles of Confederation.” Crosby via PCGS: “earliest coins issued by the authority of the United States.” | High | A / B |
| 4a | Obverse: sundial + rays; FUGIO, 1787, MIND YOUR BUSINESS | as draft | **Supported** | None material. Note Jul 6 text places FUGIO / 1787 beside meridian sun above dial; MIND YOUR BUSINESS below. | https://www.pcgs.com/coinfacts/category/fugio-cents-1787/5954 | https://americanhistory.si.edu/collections/object/nmah_1096631 | Jul 6 resolve (via Crosby/PCGS); Smithsonian Obverse: “Sundial below sun… FUGIO / 1787 / MIND YOUR BUSINESS.” | High | A/B |
| 4b | Franklin inspired 1776 Continental designs; did NOT personally engrave | as draft | **Supported** | Keep “inspired, did not engrave.” Add engraver: **Abel Buell**. | https://americanhistory.si.edu/collections/object/nmah_1096631 | https://stacksbowers.com/bank-of-new-york-hoard-of-fugio-coppers/ | Smithsonian: “Benjamin Franklin inspired this obverse design…” Stack’s/Crosby: dies by Abel Buell/Buel. | High | A / B |
| 5a | Reverse: 13 links; WE ARE ONE | as draft | **Supported** | None. | https://www.pcgs.com/coinfacts/category/fugio-cents-1787/5954 | https://americanhistory.si.edu/collections/object/nmah_1096631 | Jul 6: thirteen linked circles; center “We are one.” Smithsonian Reverse: “13 interlocking rings… UNITED STATES / WE ARE ONE.” | High | A/B |
| 5b | Inner legend AMERICAN CONGRESS vs UNITED STATES variants | “AMERICAN CONGRESS (or variant UNITED STATES)” | **Weak** → correct | Rewrite: Circulation: **UNITED STATES** and **STATES UNITED** (legend order/placement). **AMERICAN CONGRESS** = Newman **1-CC pattern** (Board of Treasury Jul 6 mandated UNITED STATES; ~3–4 known). Do not present AMERICAN CONGRESS as a normal peer variant. | https://www.pcgs.com/coinfacts/coin/1787-fugio-1c-american-congress-newman-1-cc-bn/871 | https://learn.apmex.com/coin-guide/guide-to-colonial-values/fugio-coppers-1787/ | PCGS lists American Congress Newman 1-CC as distinct variety; APMEX: American Congress reverse is “one of the rarest of all types”; Jul 6 resolve specifies “United States.” | High | B |
| 6a | Pointed Rays vs Club Rays | Pointed dominant; Club Rays distinct hubs | **Supported** | None. | https://www.pcgs.com/coinfacts/category/fugio-cents-1787/5954 | https://www.pcgs.com/coinfacts/coin/1787-fugio-1c-american-congress-newman-1-cc-bn/871 | Crosby via PCGS: sun’s rays “very heavy… known as ‘club rays.’” PCGS major varieties include Club Rays types. | High | B |
| 6b | UNITED STATES vs STATES UNITED | as draft | **Supported** | Keep; optionally note UNITED above / STATES below as scarcer Bank of NY-associated arrangement. | https://www.pcgs.com/coinfacts/category/fugio-cents-1787/5954 | https://stacksbowers.com/bank-of-new-york-hoard-of-fugio-coppers/ | Crosby: “order of the words UNITED STATES… often transposed to STATES UNITED.” Stack’s: scarce UNITED above / STATES below in BONY hoard. | High | B |
| 6c | New Haven Restrike ~1860 by C. Wyllys Betts | “Struck from copy dies by C. Wyllys Betts; narrower rings…” | **Weak / partly Contradicted** | Replace with: “So-called **New Haven Restrike** (c. 1858–1860): mid-19th-century pieces traditionally linked to dies found in New Haven (Broome & Platt store); **C. Wyllys Betts** associated with discovery; **Horatio N. Rust** struck examples. Catalog as **copy / ‘New Haven Restrike’**—**not** 1787 circulation. Note: whether dies are original 1780s dies vs mid-19th copy dies is **disputed** in modern literature; do not call Betts the striker.” | https://www.coinworld.com/news/us-coins/popular-restrikes-in-heritages-january-auctions.html | https://www.numisbids.com/sale/9515/lot/3320 | Coin World: “wasn’t made in New Haven and isn’t a restrike… Rust… claiming… Betts…” Heritage/NumisBids: Betts discovered dies 1858; Rust struck 1860. | Med–High | B |
| 6d | Raised rims / concave devices as patterns | as draft | **Supported** | Keep as special/pattern types (Raised Rims etc.). | https://www.pcgs.com/coinfacts/coin/1787-fugio-1c-american-congress-newman-1-cc-bn/871 | https://learn.apmex.com/coin-guide/guide-to-colonial-values/fugio-coppers-1787/ | PCGS major varieties include Raised Rims; APMEX discusses Raised Rims type. | Med | B |
| 7a | Mintage ~398,000–400,000 Estimated/Disputed | Disputed/Estimated ~398k–400k; no single invented integer | **Supported** | Keep Estimated/Disputed. May cite **~398,577** as Treasury **weight-count** of copper delivered (8,968 lb @ 2¼ lb per dollar) per PCGS research quoting 1789/1791 Treasury/auditor records—still mark Estimated (weight-count; Jarvis/government book discrepancy exists). Do **not** invent a different integer. | https://www.pcgs.com/news/fugio-cents-the-first-regular-issue-united-states-coin | https://www.pcgs.com/coinfacts/category/fugio-cents-1787/5954 | PCGS: “official figures showing… weight-count mintage of **398,577**… auditor’s report of October 21, 1791… 8968 lbs… $3,985.77.” Crosby/Sep 30 1788 committee: 300-ton contract “no part… fulfilled” / small part of copper-sale contract received. | High (as Estimated); no Tier-A Mint circular with a single census | B citing A (Treasury records) |
| 7b | Jarvis failed full contract; BONY hoard ~1856 | as draft | **Supported** | Soften “~1788 discovered in 1856” → keg remained unopened until **1856**; pieces dated 1787, largely struck **1788**. | https://stacksbowers.com/bank-of-new-york-hoard-of-fugio-coppers/ | https://www.pcgs.com/coinfacts/category/fugio-cents-1787/5954 | Stack’s: “keg… remained unopened until 1856”; “dated 1787 but struck in 1788.” | High | B |
| 8a | Specs: copper; ~157.5 grains / ~10.2 g | as draft | **Supported** | Frame 157.5 grains as **federal standard** (Act of Aug 8, 1786 / contract “federal standard”); note extant weights vary (BONY averages reported lighter). ~10.2 g is grain→gram conversion of 157.5. | https://www.pcgs.com/news/early-american-fugio-cent-reclassified-as-regular-issue | https://www.pcgs.com/news/fugio-cents-the-first-regular-issue-united-states-coin | PCGS: cents “157.5 grains of pure copper” under 1786 federal standard. | High (standard); Med (as-struck mean) | B citing A |
| 8b | Diameter ~28–29 mm; plain edge | as draft | **Supported** | Keep range. Smithsonian specimen 28.4 mm; Numista lists 29 mm; PCGS lists Edge: Plain on varieties checked. | https://americanhistory.si.edu/collections/object/nmah_1096631 | https://en.numista.com/23012 | Smithsonian measurements: “overall: 28.4 mm”; Numista: Weight 10.2 g, Diameter 29 mm. | High | A / B |
| 8c | 100% copper (varied CT stock purity) | as draft | **Supported** (soft) | Prefer “Copper (Connecticut copper stock; purity not uniformly assayed in Tier A).” Avoid absolute “100%” if purity varied. | https://americanhistory.si.edu/collections/object/nmah_1096631 | https://www.pcgs.com/coinfacts/category/fugio-cents-1787/5954 | Smithsonian physical description: copper. | Med | A |
| 9 | Sundial primary / unique side for card image | Obverse (Primary Image) = sundial | **Supported** | Keep Eric card-image rule: show sundial/obverse as primary. Matches Smithsonian side assignment and distinctive device. (Jul 6 text lists chain side first, then dial—numismatic/card convention still treats sundial as obverse.) | https://americanhistory.si.edu/collections/object/nmah_1096631 | (Eric standing rule / RECONCILED_TONIGHT Rank 0–1) | Smithsonian: Obverse = sundial; Reverse = 13 rings. | High | A + project rule |

---

## 3. Rank 0 — Image parity (light pass)

**Parity rules — sound for Numista.Ai**

- Strict side verification (obverse = primary date/portrait device; reverse = heraldic / denomination / series device): **OK**.
- No single-side duplicate placeholders: **OK** (critical for catalog UX).
- High-priority targets — **OK / keep**:
  - Early federal coppers (Chain / Wreath Large Cents — unique reverse wreaths / chain): correct unique-side risk.
  - Mercury Dimes (fasces reverse): correct.
  - Walking Liberty Halves (eagle reverse): correct (“eagle on mountain/rock”).
  - Washington Classic Quarters (heraldic eagle reverse): correct.

**Minor notes (not FAIL)**

- Consider also prioritizing **Fugio** itself once C1 lands (sundial unique-side)—already called out in RECONCILED Rank 0/1.
- Chain Cent reverse is chain links (not wreath); draft’s parenthetical “unique reverse wreaths” should read **“unique reverse devices (chain / wreath)”** so Chain is not mislabeled.

**Baseline counts — UNVERIFIED**

| Draft claim | Local corroboration |
|---|---|
| definitive_reference 6,503 (5,770 coin / 620 note / 113 medal) | Repeated in RECONCILED + Rank 6–7 (113 medals) only. **No** `definitive_reference` dump under `/workspace/morgan_db` to recount. `backup_coins_13aug2026.json` = **4,992** coin-ish rows (different snapshot; not proof of 5,770). |
| ~1,000 with matched obverse/reverse | `image_index_full.csv` ≈ **1,005** rows, but those are **per-side image docs**, not dual-matched coin records. Cannot confirm “~1,000 matched pairs.” |
| ~4,800 unattached / lack dual-sided verified images | **Not corroborated.** Do not invent a count. Flag for FIN OPS morning verify against live `definitive_reference`. |

---

## 4. Unresolved conflicts for Eric EOD

1. **New Haven “Restrike” die authenticity** — Mainstream catalog/auction practice: mid-19th-c copy dies (Rust; misnamed). Minority scholarship (e.g. McDowell/Casey, JEAN 2019) argues some dies may be period. Catalog safely as **“New Haven Restrike” (copy / later striking)** — **not** 1787 circulation — and footnote the dispute rather than pick a side without Eric.
2. **Mintage display integer** — Adopt **Estimated ~398,577 (Treasury weight-count)** vs keep **~398,000–400,000** range only? Draft’s Estimated/Disputed posture is compliant either way; recommend showing **398,577 (est., wt-count)** + note Jarvis contract shortfall / book discrepancy.
3. **Rank-0 gap arithmetic** — Need FIN OPS pull of current `definitive_reference` image attachment stats before using ~4,800 in any public/museum gap narrative.
4. **“Company for Coining Coppers”** label — Historically the CT copper company; Fugio striking is under **Jarvis** contract / New Haven circle. Wording polish only unless Eric wants a specific corporate string in the type header.

---

## 5. Exact wording fixes (old → new)

### Fix A — Status line (tighten, still Supported)
**OLD:**  
`Status: First official coin authorized by the United States government under the Articles of Confederation.`

**NEW:**  
`Status: First circulating copper coinage authorized by the United States in Congress assembled under the Articles of Confederation (federal contract issue; pre–U.S. Mint, 1792).`

### Fix B — Contractor line
**OLD:**  
`Contractor: James Jarvis (Company for Coining Coppers, New Haven, CT)`

**NEW:**  
`Contractor: James Jarvis (Jarvis & Co.), New Haven, CT — associated with the Connecticut copper works (Company for Coining Coppers / Broome & Platt circle). Dies engraved by Abel Buell.`

### Fix C — Reverse legends (priority correction)
**OLD:**  
`Central circular boss inscribed WE ARE ONE, surrounded by inner legend ring inscribed AMERICAN CONGRESS (or variant UNITED STATES).`

**NEW:**  
`Central boss: WE ARE ONE. Circulation legend ring: UNITED STATES or STATES UNITED (order/placement varieties; scarce UNITED above / STATES below). Pattern only: AMERICAN CONGRESS (Newman 1-CC; Jul 6, 1787 Board of Treasury mandate specified UNITED STATES; a few specimens known).`

### Fix D — New Haven Restrike (priority correction)
**OLD:**  
`New Haven Restrike (c. 1860): Struck from copy dies by C. Wyllys Betts; narrower rings, distinct high-relief lettering. (Must be classified strictly as restrike/pattern, not 1787 circulation).`

**NEW:**  
`So-called New Haven Restrike (c. 1858–1860): Later pieces traditionally tied to dies found in New Haven (Broome & Platt store); C. Wyllys Betts associated with the discovery narrative; examples struck by Horatio N. Rust. Designs differ from 1787 circulation (e.g., thinner rings / distinct lettering). Catalog as copy / “New Haven Restrike” — NOT 1787 circulation. (Whether any dies are original period dies vs mid-19th copy dies remains disputed; do not treat as Jarvis 1787 output.)`

### Fix E — Mintage note (optional strengthen, still Estimated)
**OLD:**  
`Mintage Figure: Disputed / Estimated ~398,000–400,000 pieces (Jarvis failed to fulfill full contract for 300 tons of copper; Bank of New York hoard of ~1788 discovered in 1856 provided uncirculated specimens).`

**NEW:**  
`Mintage: Estimated / Disputed — best cited figure ~398,577 (Treasury weight-count of copper coin delivered: 8,968 lb at the federal 2¼ lb per dollar standard; PCGS synthesis of 1789/1791 Treasury–auditor records). Not a piece-counted Mint report. Jarvis did not fulfill the 300-ton contract. Bank of New York keg of Unc. pieces remained sealed until ~1856 (coins dated 1787; generally struck 1788).`

### Fix F — Rank 0 Chain/Wreath parenthetical
**OLD:**  
`Early federal coppers (Chain/Wreath Large Cents — unique reverse wreaths).`

**NEW:**  
`Early federal coppers (Chain/Wreath Large Cents — unique reverse devices: chain links / wreath).`

### Fix G — Composition absolute
**OLD:**  
`Composition: 100% Copper (varied purity from Connecticut copper stock).`

**NEW:**  
`Composition: Copper (Connecticut copper stock; purity not uniformly documented in Tier A).`

---

## Sign-off

- **Overall:** PASS WITH CORRECTIONS  
- **Blocking for later live merge:** Fix C (AMERICAN CONGRESS hierarchy) and Fix D (New Haven Restrike attribution).  
- **Non-blocking:** Fix A/B/E/F/G + Rank-0 count verify.  
- **No live writes performed.**
