# Catalog coverage count, 13 Oct 2026

Read-only Firestore count (project studio-9101802118-8c9a8), run 13 Oct 2026 from EDS_Laptop. Only reads, nothing written. Aggregates only: no account names or emails, no values.

## 1. Existing reports
None of these gives a current count of items with and without images:
- `numista_backend/nightly_data_audit.py`: per-item image check, but only for 2 hard-coded accounts. It writes to `weekly_audits`. Not run for this report.
- `latest_audit_report.md` (23 Aug): Greysheet slot audit, Eisenhower only.
- `program_seed_audit_report.json` (2 Sep): 33 programs, slot counts only (dry run).
- `US_Mint_Official_Programs_Checklist_Audit.md` (2-3 Sep, Brain Inbox): program checklist, no image or mintage counts.
- Ohio/PA IMAGE_MISMATCH plan (8 and 27 Sep): a single bug, not coverage.
- SITE_AUDIT_POST_DEPLOY 27/28/30 Sep, SCANNER_DEV_PUSH_AUDIT (12 Oct): site and scanner QA, not catalog coverage.

## 2. Headline numbers

**User collections** (collection group `users/*/coins` and `users/*/currency`, 1395 `_demo` seed rows excluded):
- Coins: 11053 rows in 17 accounts, **5312 distinct items** (by program + year + mint + variety)
  - With obverse image: 3342. With reverse: 3318. **With no image: 1970** (37%)
  - With mintage: **0**. With designer: **0**. User coin docs have no mintage or designer fields.
  - Matching an entry in `coin_image_index` (loose key match): 125
- Paper money: 413 rows in 1 account, **207 distinct notes**. With obverse image: 157. With reverse: 73. With no image: 50. With mintage or print run: 0. With designer: 0.
- World items: 2 (outside scope)

**Catalog side:**
- `global_programs`: 34 programs, 1892 slots. Slot fields are name, year and varieties. No image, mintage or designer fields.
- `definitive_reference`: 6503 docs. With image URLs: 1564. With non-empty mintage: 10. With designer: 0 (the field exists on 20 docs but is empty).
- `coins_reference`: 6302 docs (legacy, shape is similar)
- `coin_image_index`: 1003 entries (601 obverse, 404 reverse) in 44 program labels
- `currency_image_index`: 10 entries, all reference fallbacks

## 3. Breakdown by program
The full table is in CATALOG_COVERAGE_13OCT.csv. Program labels are as users entered them, so there are 412 coin labels. They still need to be normalized to `global_programs`.

| Type | Program (as entered) | Rows | Distinct | No image | Mintage |
|---|---|---|---|---|---|
| coin | (none) | 2645 | 721 | 2498 | 0 |
| coin | Roosevelt Dimes | 674 | 376 | 258 | 0 |
| coin | USA Invoice Import | 457 | 234 | 308 | 0 |
| coin | State and Territory Quarters | 425 | 36 | 0 | 0 |
| coin | National Park Quarters | 361 | 53 | 190 | 0 |
| coin | Lincoln Cent | 290 | 220 | 12 | 0 |
| coin | Liberty Seated | 273 | 117 | 136 | 0 |
| coin | America the Beautiful Quarters | 273 | 81 | 18 | 0 |
| coin | Presidential Dollars | 269 | 33 | 268 | 0 |
| coin | 50 State Quarters | 228 | 59 | 177 | 0 |
| coin | American Women Quarters | 225 | 21 | 142 | 0 |
| coin | The U.S. Nickel Collection | 202 | 138 | 113 | 0 |
| coin | Washington Silver Quarter | 201 | 165 | 0 | 0 |
| coin | Presidential $1 Coin Program | 157 | 38 | 21 | 0 |
| coin | Eisenhower Dollar | 132 | 32 | 54 | 0 |
| coin | Liberty Walking Half Dollar | 122 | 101 | 71 | 0 |
| coin | Lincoln Head Penny | 121 | 107 | 0 | 0 |
| coin | Barber | 117 | 79 | 49 | 0 |
| coin | Morgan Silver Dollar | 109 | 68 | 22 | 0 |
| coin | Kennedy Half Dollar | 106 | 98 | 1 | 0 |
| coin | American Eagle | 102 | 78 | 39 | 0 |
| coin | Mercury Dime | 100 | 79 | 2 | 0 |
| coin | Capped Bust Half Dollar | 97 | 25 | 63 | 0 |
| coin | Kennedy Half Dollar Series | 89 | 81 | 0 | 0 |
| coin | Franklin Half Dollar | 87 | 41 | 0 | 0 |
| paper_money | Federal Reserve Note | 162 | 55 | 22 | 0 |
| paper_money | Silver Certificate | 90 | 44 | 9 | 0 |
| paper_money | Legal Tender Note | 45 | 30 | 17 | 0 |
| paper_money | other | 26 | 23 | 20 | 0 |
| paper_money | Fractional Currency | 24 | 19 | 4 | 0 |
| paper_money | National Bank Note | 23 | 5 | 17 | 0 |
| paper_money | Confederate | 15 | 13 | 0 | 0 |
| paper_money | Federal Reserve Bank Note | 10 | 3 | 0 | 0 |
| paper_money | Gold Certificate | 7 | 7 | 0 | 0 |
| paper_money | Obsolete Currency | 4 | 3 | 4 | 0 |
| paper_money | Bank Note | 2 | 1 | 2 | 0 |
| paper_money | Military Payment Certificate | 2 | 2 | 0 | 0 |
| paper_money | Treasury Note | 2 | 2 | 0 | 0 |
| paper_money | Error Note | 1 | 0 | 1 | 0 |

## 4. Gaps and caveats
- Mintage and designer are effectively missing everywhere. They aren't in user items or program slots, and only about 10 `definitive_reference` docs have them.
- User items are not linked to the catalog by ID. Matching them to `definitive_reference` or `global_programs` needs a normalization pass, which wasn't done here. 'Distinct' therefore uses the labels as users typed them, which may over-count.
- 'Has image' means a non-empty image URL field. Whether each URL actually loads, and whether it shows the right coin, was not checked.
- BigQuery (`numista_bq_loader_job`) and the local `numista_coins.db` (7 Aug) were not used. Firestore is the live source.