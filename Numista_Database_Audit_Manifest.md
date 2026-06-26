# Numista.AI - Database Audit Manifest

Generated automatically by diagnostic audit worker to verify database integrity, schema alignment, and variety coverage.

## 1. Database Summary

Verifies that baseline records (10,007 base coins) and parsed/expanded varieties exist in the definitive reference table.

| Category | Total Row Count |
| --- | --- |
| banknote | 550 |
| coin | 11236 |
| medal | 142 |
| total | 11928 |


## 2. Historic Coin Sample (1878 Morgan Dollars)

Validates the division of variety identifiers vs. descriptive/historical notes.

| Year | Denomination | Mint Mark | Variety | Historical Notes / Descriptions | Document ID |
| --- | --- | --- | --- | --- | --- |
| 1878 | One Dollar | CC |  | Carson City Mint issue. Standard 1878 design. | ref_coin_morgan_dollars_one_dollar_1878_cc_none |
| 1878 | One Dollar | P |  | First year of issue. Standard 8 tail feathers design on reverse. | ref_coin_morgan_dollars_one_dollar_1878_p_none |
| 1878 | One Dollar | P | 7/8 Tail Feathers | 7 over 8 tail feathers variety, showing tips of the 8 tail feathers underneath the 7 tail feathers. | ref_coin_morgan_dollars_one_dollar_1878_p_7_8_tail_feathers |
| 1878 | One Dollar | P | 7 Tail Feathers, Reverse of 1878 | Second reverse design with parallel top arrow feather and flat breast on the eagle. | ref_coin_morgan_dollars_one_dollar_1878_p_7_tail_feathers__reverse_of_1878 |
| 1878 | One Dollar | P | 7 Tail Feathers, Reverse of 1879 | Third reverse design with slanted top arrow feather and rounded breast on the eagle. | ref_coin_morgan_dollars_one_dollar_1878_p_7_tail_feathers__reverse_of_1879 |


## 3. Privy Mark Check (2021 Morgan Dollars)

Confirms that privy marks struck on Philadelphia coins are cataloged cleanly in the database.

| Year | Denomination | Mint Mark | Variety | Historical Notes | Document ID |
| --- | --- | --- | --- | --- | --- |
| 2021 | One Dollar | CC | CC Privy Mark | Struck at the Philadelphia Mint. Features a 'CC' privy mark on the reverse to commemorate the historic Carson City Mint. | ref_coin_morgan_dollars_one_dollar_2021_cc_cc_privy_mark |
| 2021 | One Dollar | O | O Privy Mark | Struck at the Philadelphia Mint. Features an 'O' privy mark on the reverse to commemorate the historic New Orleans Mint. | ref_coin_morgan_dollars_one_dollar_2021_o_o_privy_mark |


## 4. Modern 2026 Edge Case (2026-W Morgan Dollar)

Verifies proper tracking of contemporary West Point Semiquincentennial mint issues.

| Year | Denomination | Mint Mark | Variety | Historical Notes | Document ID |
| --- | --- | --- | --- | --- | --- |
| 2026 | One Dollar | W | Liberty Bell 250 Privy Mark | Struck at the West Point Mint. Commemorates the 250th Anniversary of the United States (Semiquincentennial) with a dual date '1776 ~ 2026' and a Liberty Bell privy mark. | ref_coin_morgan_dollars_one_dollar_2026_w_liberty_bell_250_privy_mark |


## 5. Banknote Suffix Test (12-District Federal Reserve Note Expansion)

Verifies that small-size Federal Reserve Notes are programmatically expanded into 12 district varieties (A-L).

| Year | Denomination | Variety (Friedberg Suffix) | Note/District Description | Document ID |
| --- | --- | --- | --- | --- |
| 1963 | One Dollar | Fr. 1900-A - Granahan/Dillon Signatures - Green Seal - Boston [A] | First small-size $1 Federal Reserve Note. Replaced the $1 Silver Certificate. Features George Washington on the obverse and the Great Seal of the United States on the reverse. Issued by the Federal Reserve Bank of Boston (A). | ref_note_one_dollar_1963_fr__1900_a___granahan_dillon_signatures___green_seal___boston__a |
| 1963 | One Dollar | Fr. 1900-B - Granahan/Dillon Signatures - Green Seal - New York [B] | First small-size $1 Federal Reserve Note. Replaced the $1 Silver Certificate. Features George Washington on the obverse and the Great Seal of the United States on the reverse. Issued by the Federal Reserve Bank of New York (B). | ref_note_one_dollar_1963_fr__1900_b___granahan_dillon_signatures___green_seal___new_york__b |
| 1963 | One Dollar | Fr. 1900-G - Granahan/Dillon Signatures - Green Seal - Chicago [G] | First small-size $1 Federal Reserve Note. Replaced the $1 Silver Certificate. Features George Washington on the obverse and the Great Seal of the United States on the reverse. Issued by the Federal Reserve Bank of Chicago (G). | ref_note_one_dollar_1963_fr__1900_g___granahan_dillon_signatures___green_seal___chicago__g |


## 6. Anomaly Counts

Performs sanitization checks for NULL fields, formatting issues, or empty values.

| Anomaly Type Check | Count |
| --- | --- |
| Columns containing NULL values | 0 |
| Invalid 4-digit years (excluding empty/base coin types) | 0 |
| Empty or missing denomination strings | 0 |

