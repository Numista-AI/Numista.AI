# AJ's Collection — Questions to Ask Her
*Generated 2026-06-20 from 3,900 scanned Firestore records*

> [!IMPORTANT]
> Full CSV with all 893 flagged records: [AJ_questions_report_2026-06-20.csv](file:///C:/Users/ericd/Documents/MyVertexProject/AJ_questions_report_2026-06-20.csv)
> Open it in Excel, fill in the "question_for_AJ" column as you talk to her, then send it back for re-import.

---

## Summary of Issues Found

| Issue | Count | Priority |
|---|---|---|
| Records entered as SETS, not individual coins | 668 | 🟡 Medium |
| Possible currency in coin collection | 143 | 🔴 High |
| Missing Denomination | 96 | 🟡 Medium |
| Missing Year | 59 | 🔴 High |
| Missing both Program AND Denomination | 29 | 🔴 High |
| Year entered as a date range | 17 | 🔴 High |
| Missing Condition/Grade | 14 | 🟢 Low |
| Invalid year values (N/A, Multiple, Pending, etc.) | 9 | 🔴 High |

---

## 🔴 Priority 1 — Ask AJ First

### 1. Year Entered as a Range (not a specific year)
These need to be broken out into individual coins OR confirmed as sets:

| Year as entered | Description | What to ask |
|---|---|---|
| `1909-1958` | (Lincoln series range) | Is this a complete date set? Which specific coins? |
| `1968-98` | 31 different US proof sets | Which specific years does she have? |
| `2018-20` | 41 Native American quarters and folder | Which specific years/designs? |
| `1916-1920` | 5 Different Mint Wheat Cents | Which 5 years exactly? |
| `1943-46` | (unknown series) | Which years? |
| `1941-45` | (unknown series) | Which years? |
| `1936-38` | (unknown series) | Which years? |
| `1964-2012` | (unknown series) | Specific years or complete set? |
| `2015-2024` | (unknown series) | Specific years or complete set? |
| `1916-1920` | Walking Liberty series | Which 5 coins exactly? |
| `1979-99` | Susan B Anthony | Which years? (only 1979-81 + 1999 were minted) |
| `1999-2010` | State/NP Quarters set? | Which specific quarters? |
| `11914-16` | (typo — likely 1914-16) | Confirm year and series |

### 2. Invalid Year Values
| Record | Year entered | What to ask |
|---|---|---|
| Multiple records | `N/A` | What year is this coin? |
| Multiple records | `Multiple` | Confirm — is this a multi-year set? |
| 1 record | `Pending` | Was this coin identified yet? |
| 1 record | `Year` (literal word) | Data entry error — what year? |
| 1 record | `19th & 20th century` | Which specific coins? |

### 3. SET Records with Large Quantities
These are entered as a single record but represent multiple coins:

| Qty | Description | What to ask |
|---|---|---|
| 50 | (set record) | List of all 50 individual coins? |
| 15 | (set record) | List of all 15? |
| 12 | (set record — 1890 coin?) | What 12 coins are in this set? |
| 6 | "1880-1885CC 6 piece Carson City Morgan set" | Individual years: 1880-CC, 1881-CC, 1882-CC, 1883-CC, 1884-CC, 1885-CC? |
| 5 | (5-coin set) | Individual coins? |
| 4 | (4-coin set) | Individual coins? |
| 3 | (3-coin set) | Individual coins? |
| 2 | (2-coin set) | Individual coins? |

---

## 🔴 Currency That Needs to Move

These 143 records appear to be **paper money / currency** currently stored in the coin collection. They need to be verified and moved to the `currency` collection:

> Note: Some of these may be false positives (coins with the word "note" in the description). Please review the full CSV and mark which ones are truly paper money.

**Known true currency (from issue uploads — definitely need to move):**
- `50 bank notes from 50 countries with chart` — *clearly not a coin*
- `100 coins from ioo countries` — *verify: coins or notes?*
- All records from `Paper Money.xlsx` (413 items in the separate currency import queue)

---

## 🟡 Missing Year (59 records)
These coins have no year recorded at all. AJ would need to look at the physical coin or invoice:

The most common programs with missing years:
- Buffalo Nickels (year worn off is common on these)
- Various "invoice" entries where year wasn't recorded at purchase
- Miscellaneous purchases with no date

---

## 🟡 Missing Denomination (96 records)
These have a program name but no denomination filled in. Usually easy to fill in once you know the program — most can be auto-filled:

- All Morgan Silver Dollars → `1 Dollar`
- All Franklin Half Dollars → `Half Dollar`
- etc.

> [!TIP]
> Many of these can be auto-corrected by program name. Ask me to run a script to fill in obvious denominations automatically.

---

## 🟢 Missing Condition/Grade (14 records)
Low priority — just 14 coins with no condition entered. Easy to fill in later.

---

## How to Use This Report

1. **Open** [AJ_questions_report_2026-06-20.csv](file:///C:/Users/ericd/Documents/MyVertexProject/AJ_questions_report_2026-06-20.csv) in Excel
2. **Sort by Priority** (column A) — start with Priority 1
3. **Fill in** the `question_for_AJ` column with notes from your conversation with her
4. **Save** and send back — I'll re-import the corrected data

---

*Note: The 668 "set" flags are the biggest group but lowest urgency — many of AJ's coins were purchased as sets (PCS, GovMint, etc.) and are legitimately recorded that way. Only the ones with Quantity > 1 truly need to be broken into individual records.*
