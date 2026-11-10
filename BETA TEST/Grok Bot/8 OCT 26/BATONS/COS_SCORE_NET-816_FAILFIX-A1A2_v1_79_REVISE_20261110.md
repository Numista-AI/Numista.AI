# DESIGNATED CoS PLAN SCORE: NET-816 Fail-Fix A1/A2 (AG CoS v5), plan v1

**Score: 79 / 100, REVISE** (pass mark 95; only material defects count: correctness, safety, permissions, execution. No points taken off for cosmetics.)
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 1:59 PM ET.
Track: NET-816 fail-fix (A1/A2). **This is attempt 1 of 10** on the track and writer AG CoS v5's attempt 1 of 4 (Eric's 4/10 rule; the Claude rule applies after 8 failures).

## Plan scored
- File: `BETA TEST\Grok Bot\8 OCT 26\BATONS\PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_AGCOS-V5_20261110.md`
- SHA-256 `19fd2307be1318a076663bc2b8771d41e5119605792e3f6dfb4f5e4e38f460c3`, 6,328 bytes, 117 lines. Last written 1:47:48 PM ET.
- The RADIO NET (1:48:21 PM ET), INBOX (1:48:32 PM ET) and OUTBOX (1:48:47 PM ET) copies are byte-identical (same SHA and size).

## Scored against
- Code Reviewer go-live review `BETA TEST\Grok Bot\10 NOV 26\CODE_REVIEW_GO-LIVE_NET-816_NET-827_c547b7a0_20261110.md`, SHA-256 `3e2c16709736ab5a5cf834ed9aba9df66704465d7b86f24baf4cf56a0ad864ff`. Uses findings A1 (lines 16 and 90) and A2 (lines 17 and 91).
- HOLD order `HOLD_NET-816_NET-827_AGCOS-V5_GO-LIVE-STOP-RULE_AND_FAILFIX-PLAN-ORDER_20261110-1113.md`, SHA-256 `41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d`, section 3 (lines 18–20).
- Source, checked read-only: the MyVertexProject repo is on branch p7-v8.9 at HEAD `999daf14`. `git diff c547b7a0 HEAD` is empty for firebase.json, melt_value_service.dart, main.dart and the chunk 1 test, and the working tree is clean for those files, so the working-tree files match `c547b7a0`. Hashes:
  - firebase.json `6afc1911…5a9b5f2c`
  - test `6f08c560…a51da8`
  - melt_value_service.dart and main.dart were copied to the box.
- Melt logic: the box ported `parseFaceValue`, `_matchDenom` and the silver branch of `compute()` to Python, old and as planned. It ran them on all 3,202 rows of `catalog_public_v1.json` and on synthetic cases.

## What the plan gets right (no deduction)
- **A1 root cause and fix.** firebase.json `hosting.rewrites` (lines 49–133) has no `/catalog` entry and no catch-all `**` rewrite. Adding `/catalog` and `/catalog/**` pointing to `/index.html` (plan lines 38–47) is the right SPA target.
  - main.dart already treats `/catalog` and `/catalog/<nac>` as known paths and routes them to `CatalogBrowseScreen` (main.dart, the known-path list and the "Public Catalog direct entry" block). A function or Cloud Run target is not needed.
  - The new entries do not shadow anything. `/api/**` (Cloud Run) comes first, and no static `/catalog` file exists (Flutter assets sit under `/assets/...`). Placement inside the array is safe.
- **A2 root cause** (plan lines 16–30) matches the source exactly: `_ag90` lines 11–17, the `?? 0.77344` at line 190, and the 0.05→`nickel`-only mapping at line 236. The plan's "21.4×" (against the true half-dime ounce) and the CR's "about 10×" (against the old dime weight) are consistent.
- **Half dime fix.** Adding `'half dime': 0.03617`, the 0.05 branch, and `half dime` in the 90% keyword list turns all modeled half-dime variants into 0.03617 oz. The variants are "Silver (90%)/Half Dime", "Silver/Half dime" (which used to take the line-201 generic Morgan weight) and "90% Silver/Half-dime".
  - 90% dime, quarter, half and dollar are unchanged. So are 40% halves (0.14792) and 35% war nickels (0.05626).
  - The new `return null` cannot crash anything: `compute()` already returns `double?` and N/A for base metal.
- **Gates and scope** (lines 5, 115–117): the order is CoS 95 + SAG 95 + Eric's typed YES. Preview needs a new scoped YES, because t2455s9467 covered only `c547b7a0`. main stays pinned, and live hosting, Firestore and Stripe are untouched.

## Deductions (each one is material)

| # | Pts | Area | Evidence | Defect |
|---|---|---|---|---|
| D1 | −5 | Correctness | Plan line 91 ("will NOT silently assign a 1-dollar Morgan melt weight to an unrecognized coin"), against melt_value_service.dart line 201 `if (ag > 0) return ag * 0.77344 * count;`, which the plan does not change | The plan's stated effect is false. Any sub-dollar silver coin whose metal text lacks "90%" or a series keyword still gets the Morgan dollar weight. Catalog-row simulation, with metal content shown in quotes: 14 "Silver" dimes, 22 "Silver" quarters, 62 "Silver" half dollars, 28 "89.24% Silver" quarters and halves, plus "5 cents/3 cents/10 Cents silver". That is 10.7× too high for a dime and 4.3× for a quarter. It is the same wrong-dashboard-value class as A2, and Field Tester can hit it. Fix it, or name it explicitly as out of scope with a follow-up ticket and a truthful effect statement. |
| D2 | −3 | Correctness (regression) | Plan line 86 `?? (denom.contains('dollar') ? 0.77344 : 0.0)` | The dollar fallback now depends on the word "dollar" in the denomination only. Morgan or Peace coins whose denomination doesn't contain "dollar" lose their melt value and go from 0.77344 to null. Real catalog example: the denomination `CC` with series `1$-Morgan dollar` drops from 0.77344 to null. An empty denomination with series "Morgan" does the same. The test should check the combined text (`morgan` / `peace` / `dollar`) or face value 1.00, not the denomination alone. |
| D3 | −4 | Execution: test coverage | Plan lines 95–101 and 105–110 | The only new test is the half dime (plus an unspecified `format` check). Missing tests:<br>(a) the removed fallback: a 90% unlisted sub-dollar such as "Twenty Cent" returns null and no longer 0.77344;<br>(b) the dollar fallback is kept for Morgan or Peace without "dollar" in the denomination;<br>(c) 90% dime, quarter, half and dollar plus 40% half and 35% war nickel stay unchanged;<br>(d) "Silver / Half dime" (no "90%") and "Half-dime".<br>Without (a)–(c), the gate cannot catch D2-type regressions. |
| D4 | −3 | Execution: Field Tester check | Not present anywhere in the plan | The plan has no bounded Field Tester check for the p7-gate preview. It needs these checks:<br>1. A direct GET of `/catalog` returns 200 and the catalog screen.<br>2. `/catalog/<nac_code>` opens that item.<br>3. `#/catalog` behaves as stated (see D5).<br>4. A 90% silver half dime shows about spot × 0.03617 on the collection dashboard.<br>Each needs pass/fail criteria. |
| D5 | −3 | Correctness: scope | HOLD section 3 line 19 ("numista.ai/catalog **and #/catalog** would break"). CR line 16 and line 90 ("Hash URLs still will not") | The plan never mentions `#/catalog`. It needs to add hash handling or explicitly put it out of scope with the reason. Field Tester and UX must know which URL form is supported, or a hash link will fail in preview. |
| D6 | −3 | Execution: rollback and build identity | Plan lines 105–117 | No rollback is defined: no revert of the two-file change and no way to roll the p7-gate channel back to the prior `c547b7a0` build. The plan also doesn't name the base commit or branch for the fix (`c547b7a0` versus p7-v8.9 HEAD `999daf14`), and doesn't say that the built commit SHA must be recorded for the new scoped YES. |

**Total: 100 − 21 = 79, REVISE.**

## Required fixes for v2 (all must close to reach 95)
1. **D1:** Close the line-201 generic silver Morgan fallback for sub-dollar US silver, using the face-value table or returning null. Otherwise mark it out of scope with a ticket. Either way, correct the line-91 effect statement so it is true.
2. **D2:** Base the kept 0.77344 fallback on face value 1.00 or the combined text (`morgan` / `peace` / `dollar`), not on `denom.contains('dollar')`.
3. **D3:** Add regression tests (a)–(d) above, all inside `catalog_chunk1_face_value_and_card_test.dart`, with exact expected values.
4. **D4:** Add the bounded Field Tester check (`/catalog`, `/catalog/<nac>`, `#/catalog`, half dime dashboard melt) with pass/fail criteria.
5. **D5:** State how `#/catalog` is handled: fixed, or out of scope with the reason.
6. **D6:** Name the base commit and branch, require the built commit SHA in the DONE report, and define a rollback for both the code and the p7-gate channel.

## Advisories (not scored)
- Half dime weight: the catalog's 35 half dimes run 1794–1863.
  - Capped Bust and early types: 1.35 g at 0.8924 fine is about 0.0387 oz.
  - Seated 1837–1853: 1.34 g at 0.900 is about 0.0388 oz.
  - Seated 1853–1873: 1.24 g at 0.900 is about 0.0359 oz.
  - 0.03617 is within about 1% for 1853+ and about 7% low for earlier years. That is acceptable for a dashboard estimate. The plan's "1.25 g" comment (line 57) should say the nominal value or 1.24 g.
- Line references are slightly off: the `/terms` rewrite ends at line 72, not 73 (plan line 37), and the rewrites run to line 133, not 115 (plan line 12). Placement is still safe.
- A 90% twenty-cent piece (4.5 g, about 0.1447 oz) now returns null. A table entry is optional. Catalog data also has 3 "20 Cent Piece" rows with the denomination "1 cent", which is a data issue outside this track.

## Authority statement
This score **grants no code, merge, deploy, Firestore, Stripe or go-live authority.** It is REVISE, so **no SAG packet was built**. The HOLD order and the go-live stop rule stay in force. Moving forward needs a v2 plan, then CoS 95, then full-plan SAG 95 on the exact SHA, then Eric's new scoped typed YES for the p7-gate preview only.
