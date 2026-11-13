# FT RESULT — NET-816 Catalog Chunk 1 — p7-gate preview — 10 Nov 2026 (~6:38 PM ET)
Tester: Field Tester, as grokbot@numista.ai. Read-only. Preview only, except one read-only search on live for comparison (CoS 6:22 PM add-on).
Target: https://numista-vault--p7-gate-8avtpz22.web.app (CoS pin: commit a3d7dca2, Hosting release a47a275d1eb6b51f)

## BLUF
SCORE 47/100, OVERALL FAIL (the bar is 95). The direct /catalog link works and the face values are right. However:
- `#/catalog` opens the home page, not the catalog.
- The build can't be pinned to the commit: version.json has no git_commit.
- The half dime melt check is BLOCKED because the test account has no half dime.
The 237-item gap is explained: 2,965 coins + 181 banknotes + 56 medals = 3,202, matching Code Reviewer's count.
I could not reproduce Eric's 500 error. The Go-live stays on HOLD (41b8bd5f).

## Pass/fail table
| # | Check | Result | Evidence |
|---|---|---|---|
| 0 | Build pin | FAIL / UNVERIFIED. version.json shows 8.18.15 / build 81818, but git_commit is absent, so a3d7dca2 can't be confirmed. | 00-version.png |
| 1a | Typing /catalog directly | PASS. The catalog renders with 2,965 items. | 01-catalog.png |
| 1b | Opening #/catalog | FAIL. It shows the signed-in welcome/home view, not the catalog. | 02-hash-catalog.png |
| 1c | /catalog/x | PASS. The catalog renders with "We don't have item 'x' in our reference catalog yet." | 03-catalog-x.png |
| 2 | Face values / "No face value" chip | PASS with one flag. The flag is a two-coin Morgan/Peace set, which shows "$1.00 Face value" (see the full list below). | 06–13, 16, 17, 29, 30 |
| 3 | 90% silver half dime melt | BLOCKED, not PASS. The grokbot collection has no half dime, and the 1796 catalog detail shows no melt value. | 05, 38, 39 |
| 4 | Search / empty state | NOTED, not scored. "half dime" gives 35 results; "xyzzy" and "1816" give 0; an empty search gives 2,965. | 18–21 |
| 6 | Coin Search 500 | NOT REPRODUCED / BLOCKED (details below). | 33, 34, 37 |
| 7 | 2,965 vs 3,202 | EXPLAINED (details below). | 23–28, 35, 36 |

Check 2, face values seen:
- Half cent $0.005, cent $0.01, half dime $0.05, dime $0.10, quarter $0.25, half dollar $0.50, dollar $1.00.
- 1908 $5 half eagle $5.00 and 1908 $10 eagle $10.00.
- Series 2017A $1 note $1.00.
- Medals show the "No face value" chip.
- Flag: the two-coin Morgan/Peace set shows "$1.00 Face value". Two dollar coins total $2.00, so either show $2.00 or the "No face value" chip.
- A search for "token" returns 0 items, so tokens were not tested.

Check 4, empty results: the page shows "No matching catalog items found", a "Reset search & filters" button and a "Missing something?" form. The UX point to note is that "1816" returns 0 results (the 1816 record gap from the earlier catalog test is still there).

Check 6, Coin Search 500:
- No separate Coin Search / Coin Reference Search screen was found in the app's navigation.
- The catalog search "Morgan dollar 1881" returned 0 items on both preview and live, with no 500 and no "Definitive Registry: 0 records".
- No failing request was captured. Eric's 6:22 PM path needs exact steps to reproduce.

Check 7, count gap:
- The Coins tab shows 2,965, Banknotes 181 and Medals 56, which adds up to 3,202.
- GET /assets/catalog_public_v1.json returned 200 with records 0–3201, which is 3,202 records.
- Nothing is missing.

## Half dime melt math
- Live Spot Prices: silver $51.51 (metals-api.com, 10 Nov 2026 6:24 PM ET).
- Expected melt at that spot: 0.03617 oz × $51.51 ≈ $1.86.
- The CoS figure of about $1.09 matches a spot price of about $30, so the expected value should be updated to the current spot.
- A 10x bug would show about $18.6.
- No coin was observed, so this check stays BLOCKED. It needs a test half dime in a test account (a Firestore write, which needs Eric's YES) or a melt value in the catalog detail.

## Other observations
- Console: about 166 errors, almost all CSP connect-src blocks on Wikimedia images. This is a recurring defect, still open.
- Time to first content: /catalog about 6.6 s, /catalog/x about 8.4 s.
- "Photos only" filter: 2,965 → 1,213, so about 59% of coins have no photo showing.
- Era Modern shows 1,124.
- Dashboard total melt (grokbot): $3,199.15.

## Scoring rubric (FT, 100 points)
| Area | Weight | Points |
|---|---|---|
| Build pin verified | 10 | 0 |
| Routes (/catalog, #/catalog) | 25 | 12 |
| Face values + chip | 25 | 20 |
| Half dime melt | 25 | 0 (BLOCKED, so no credit) |
| Catalog completeness (count gap) | 15 | 15 |
| **Total** | 100 | **47** |

## What would move it to PASS
1. Make #/catalog route to the catalog.
2. Stamp git_commit in version.json.
3. Give the set a $2.00 face value or the "No face value" chip.
4. Provide a half dime to observe: a CoS-approved test coin in grokbot, or a melt value on the catalog detail.

Screenshots: shots_net816.tar.gz (40 files).
