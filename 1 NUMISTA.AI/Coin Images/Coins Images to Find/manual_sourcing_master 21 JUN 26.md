# Manual Image Sourcing — AJ's Complete List

This document consolidates every item in AJ's collection that requires a human to
manually find an image. Items are organized by category with specific sourcing guidance.

> [!IMPORTANT]
> **Graded currency (PMG/PCGS certs) is NOT on this list** — those are being handled
> automatically by the cert scraper. This list covers only items that need manual searching.

---

## SECTION A — COINS (6 items)

These 6 ATB (America the Beautiful) quarter records have a blank `Theme/Subject` field,
so the automated image matcher can't identify which park design they are.

**Action required:** Look up each coin in AJ's physical collection or purchase receipt,
identify the park design, then tell me the design name to fill in Firestore.

| Year | Mint | Import Source | Likely Issue |
|------|------|---------------|--------------|
| 2015 | — | Miscellaneous purchases | Silver Proof Year Set — individual park not recorded |
| 2016 | — | Miscellaneous purchases | Silver Proof Year Set — individual park not recorded |
| 2019 | — | Unknown | Description says "Michigan Pictured Rocks" but year=2019 (Pictured Rocks is 2018) |
| 2019 | — | Unknown | Description says "national parks" — generic set, no specific park |
| 2020 | S | Unknown | "National Park quarters Silver Proof Year set 5 coins" — set purchase |
| 2021 | — | Unknown | Check receipt — likely Tuskegee Airmen (Alabama), the only 2021 ATB design |

**Where to look:** The [US Mint ATB program page](https://www.usmint.gov/coins/coin-medal-programs/america-the-beautiful-quarters)
lists every design by year. Once you identify the park, just let me know the park name.

---

## SECTION B — PAPER CURRENCY (96 items)

### B1. National Bank Notes (23 items)
Each is unique to a specific issuing bank and location.
**Where to find images:** Heritage Auctions (ha.com) → search by bank name + state + denomination + year.
Also try [National Bank Note Census](https://www.usmint.gov) or eBay completed listings.

| Year | Denomination | Description | Friedberg # | Grade |
|------|-------------|-------------|-------------|-------|
| See [AJ_Manual_Image_Sourcing_Currency.csv](file:///C:/Users/ericd/Documents/MyVertexProject/AJ_Manual_Image_Sourcing_Currency.csv) for all 23 rows with full details |

---

### B2. Confederate Currency (13 items)
CSA notes are identified by Type number (T-1 through T-72).
**Where to find images:** 
- [Newman Numismatic Portal](https://nnp.wustl.edu/) — best free source for CSA scans
- Heritage Auctions → Confederate currency category
- Search by CSA Type number (e.g., "T-46 Confederate $10 1864")

| Year | Denomination | Description | CSA Type | Grade |
|------|-------------|-------------|----------|-------|
| See CSV for all 13 rows |

---

### B3. Obsolete Currency (4 items)
Pre-Federal Reserve state bank notes — each is unique.
**Where to find images:**
- Heritage Auctions → Obsolete Currency category
- Search by: state name + bank name + denomination + approximate date
- [PCGS Currency](https://www.pcgscurrency.com/coinfacts)

| Year | Denomination | Description | Grade |
|------|-------------|-------------|-------|
| See CSV for all 4 rows |

---

### B4. Gold Certificates (7 items)
**Where to find images:** Heritage Auctions → search by Friedberg number + denomination.
The Friedberg catalog number is the key identifier (e.g., Fr. 1173 = 1922 $10 Gold Certificate).

| Year | Denomination | Grade | Friedberg # (need to look up) |
|------|-------------|-------|-------------------------------|
| 1907–22 | $10 | Very Good | Fr. 1167–1173 range |
| 1906 | $20 | Good | Fr. 1178–1179 range |
| 1862 | $50 | Fine | Fr. 1189 range |
| 1922 | $10 | Very Fine | Fr. 1173 |
| 1928 | $10 | Very Good | Fr. 2400 |
| 1928 | $20 | Fine | Fr. 2402 |
| 1922 | $20 | Very Good | Fr. 1179 |

> [!TIP]
> For Gold Certificates, the **Friedberg number** is the critical lookup key.
> A paper money dealer or the [Standard Catalog of U.S. Paper Money](https://www.numismaster.com)
> can confirm the exact Fr. number from denomination + year + size (large vs small).

---

### B5. Blank / Unclassified Items (49 items)
These landed without a recognized type label. Many appear to be:
- Modern Federal Reserve Notes (auto-sourceable once confirmed)
- Legal Tender Notes ("Red Seal" $2, $5 notes)
- Colonial / early state bank notes
- A few probable mis-classifications

**Recommended action:** The [AJ_Manual_Image_Sourcing_Currency.csv](file:///C:/Users/ericd/Documents/MyVertexProject/AJ_Manual_Image_Sourcing_Currency.csv)
has the full Description for all 49. A quick scan of the descriptions will let us re-classify most.

Notable items in this group:
- `"50 Confederate Note 1864 - Crisp unused $150"` — should be Confederate (type fix needed)
- `"$500 3rd Bank of United States Philadelphia"` — rare, needs Heritage Auctions search
- `"West River Bank VT"`, `"Bank of Windsor VT"` — Vermont obsolete notes
- `"Bank of New Brunswick NJ"` — New Jersey obsolete note
- `"5c Fractional Currency 1862-1869"` — Fractional (auto-sourceable)

---

## Summary

| Category | Items | Auto-sourceable? |
|----------|-------|-----------------|
| ATB coins (blank design) | 6 | After you ID the park name |
| National Bank Notes | 23 | ❌ Manual only |
| Confederate Currency | 13 | ❌ Manual (by CSA Type#) |
| Obsolete Currency | 4 | ❌ Manual |
| Gold Certificates | 7 | ❌ Manual (by Friedberg#) |
| Blank/Unclassified currency | 49 | Partially — after re-classification |
| **PMG/PCGS graded items** | TBD | ✅ **Cert scraper running now** |

**Full data file:** [AJ_Manual_Image_Sourcing_Currency.csv](file:///C:/Users/ericd/Documents/MyVertexProject/AJ_Manual_Image_Sourcing_Currency.csv)
