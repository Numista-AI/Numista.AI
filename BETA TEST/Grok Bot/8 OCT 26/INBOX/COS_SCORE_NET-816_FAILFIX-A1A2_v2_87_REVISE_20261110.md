# DESIGNATED CoS PLAN SCORE: NET-816 Fail-Fix A1/A2 (AG CoS v5), plan v2

**Score: 87 / 100, REVISE** (pass mark 95; only material defects count: correctness, safety, permissions, execution. No points taken off for cosmetics.)
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 2:56 PM ET.
**Count: attempt 2 of 10 on the NET-816 fail-fix track; writer AG CoS v5's attempt 2 of 4.** The plan's own header (line 5) says "Track attempt 1/10". That is wrong: v1 was attempt 1.

## Plan scored
- `BETA TEST\Grok Bot\8 OCT 26\BATONS\PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v2_AGCOS-V5_20261110.md`
- SHA-256 `a0fd7ba4706eb2026fa548ed0c57f00402c8fe43c05df074bb89263ca4a3bfbb`, 18,374 bytes, 272 lines, last written 2:48:07 PM ET. This matches the reported SHA and size.
- Mirrors are byte-identical (same SHA and size):
  - `8 OCT 26\RADIO NET`
  - `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX`
  - `1 NUMISTA.AI\Grok CoS to Antigravity\OUTBOX`
- There is no `8 OCT 26\INBOX` or `\OUTBOX` copy this time.

## Scored against
- v1 record `COS_SCORE_NET-816_FAILFIX-A1A2_v1_79_REVISE_20261110.md`, SHA-256 `a4754854e034fd3e037c766336c52c8f8d6bb69d3afc027c37199040dec50885`.
- Code Reviewer go-live review, SHA `3e2c16709736ab5a5cf834ed9aba9df66704465d7b86f24baf4cf56a0ad864ff`, findings A1 and A2.
- HOLD order, SHA `41b8bd5f…778943d`.
- Source at `c547b7a0`, checked read-only:
  - `git diff --stat c547b7a0 HEAD -- numista_mobile` is empty and `numista_mobile` has 0 dirty files. The plan's line-245 claim is confirmed.
  - `origin/main` = `9f04550a45fa…a90fa45`, which matches plan line 270.
- I reran the Python port of the melt logic on all 3,202 catalog rows, old against v2 as planned (§3 Changes 2.1–2.4). I also checked one plan string with `dart analyze` on the laptop, using a scratch file in `%TEMP%`.

## v1 deduction closure map

| v1 | Status | Evidence |
|---|---|---|
| D1 (line-201 generic Morgan fallback) | **Closed** | Change 2.4 (plan lines 107–117) sends generic silver through `_matchDenom(_ag90)` with a strict dollar test, and returns null otherwise. In the catalog run, 328 rows change. All 14 "Silver" dimes, all 84 "Silver" halves and 89.24% halves, and the 181 quarters with no stated metal, "Silver" metal or 89.24% metal move from 0.77344 to the right 90%-standard weight. The plan only claims to fix the 14 dimes, 22 quarters, 62 halves and 28 89.24% pieces (line 43); the run found more quarters it also fixes. 89.24% Bust pieces read about 6.5% low, which is acceptable. A new narrow mis-map for war nickels is N4. |
| D2 (dollar fallback key) | **Closed** | `isDollar = fv==1 \|\| combined has dollar/morgan/peace` (lines 100 and 112). The run confirms `CC` + `1$-Morgan dollar` gives 0.77344 and empty denomination + "Morgan" gives 0.77344. |
| D3 (regression tests) | **Closed in substance, but the code doesn't compile** (see N2) | Tests (a)–(d), lines 129–213. I recomputed every expected value by hand and with the port: Twenty Cent gives null; Morgan CC and no-denomination give 23.2032; dime 2.1702; quarter 5.4252; half 10.8507; dollar 23.2032; 40% half 4.4376; 35% Nickel 1.6878 (the 0.05 branch falls to `nickel` in `_ag35`); the three half-dime variants give 1.0851; `format` gives "$1.09". All are correct. |
| D4 (Field Tester check) | **Partly closed** | The 4-step table is present (lines 218–227). FT-3 can't pass (N1). FT-2 and FT-4 can't be run as written (N5). |
| D5 (`#/catalog`) | **Not closed** | Its claim is false (N1). |
| D6 (base, built SHA, rollback) | **Partly closed** | The base branch and commit, the built-SHA requirement and the scoped-YES tie are present and correct (lines 243–250). The rollback steps are broken (N3). |

## Deductions on v2 (each one is material)

| # | Pts | Area | Evidence | Defect |
|---|---|---|---|---|
| N1 | −4 | Correctness / Field Tester | Plan line 34 says "`main.dart` maps `catalog` to `CatalogBrowseScreen`" through the client router. Lines 35, 62 and 226 build on that. | **False at `c547b7a0`.** `git grep` across `numista_mobile/lib` and `numista_mobile/web` finds `CatalogBrowseScreen` built only at `main.dart:178`. That happens inside the startup path check `normalizedPath == '/catalog' \|\| path.startsWith('/catalog/')` (line 155). There is no `uri.fragment` handling, no `onGenerateRoute` or route-table entry for catalog, and no URL-strategy call. `main.dart:113–114` notes that hash URLs have `uri.path == '/'`. So `/#/catalog` opens the normal home or login flow, not the catalog, and the CR (line 90) said the same. FT-3's pass rule ("loads `CatalogBrowseScreen`") will fail with only the three planned file changes. |
| N2 | −2 | Execution: tests | Plan line 211 `reason: 'Formatted melt value string at $30/oz silver spot must round to $1.09',` | This won't compile. Dart treats an unescaped `$` followed by a digit as an error. I reproduced it with `dart analyze` (Flutter SDK `C:\src\flutter`): `error - Expected an identifier - missing_identifier` at both `$30` and `$1.09`. The whole test file would fail, so gate steps 2 and 3 (lines 235–236) fail as written. |
| N3 | −3 | Execution / permissions: rollback | Plan lines 255–263 | 1. Option A says to "Rebuild from commit `c547b7a0`", but the command (line 261) never checks out `c547b7a0`, so it would rebuild and redeploy the *fixed* tree.<br>2. `git revert <sha> -m "revert: …"` (line 257) is wrong. `-m` is the mainline parent number, not a message, so on a non-merge commit it errors.<br>3. Option B (`firebase hosting:channel:delete p7-gate -f`) deletes the preview channel Eric approved, and nothing says who authorizes that.<br>4. Firebase commands must run on the host machine (saved rule), and the plan doesn't say so. |
| N4 | −2 | Correctness (new mis-map) | Changes 2.2 and 2.4 together. Statement line 119 says sub-dollar silver resolves to its "proper denomination melt weight". | Generic silver at face $0.05 now always resolves to the **half-dime** weight. Catalog row `1942-P Jefferson Wartime Nickel` ("Silver Alloy", "5 cents") gets 0.03617 oz when it should get 0.05626 (35% Ag, 5.0 g), so it reads about 36% low. That's because the 35% branch keys only on `35%` or `war nickel`, and "Wartime Nickel" matches neither. The old value (0.77344) was worse, but this is a new wrong value on a common collection coin, and the plan says otherwise. The 1871–1872 "5 cents / Silver" rows really are half dimes and are now correct. |
| N5 | −2 | Execution: Field Tester | Plan lines 225 and 227 | FT-2's example `/catalog/1842-liberty-seated-dollar` isn't a NAC code. `catalog_browse_screen.dart:72–90` matches on the lowercased NAC and otherwise shows "We don't have item … in our reference catalog yet". So FT-2 fails on its own example. A real code is needed, such as `NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2`. FT-4 needs "a user collection containing a 90% silver Half Dime", but it doesn't name the test account or data. If the tester has to add the coin, that is a Firestore write, which clashes with "Firestore UNTOUCHED" (line 271). The account and data source must be named, or the plan must say that writes through the normal app with the test account are allowed. |

**Total: 100 − 13 = 87, REVISE.**

## Required fixes for v3 (all must close to reach 95)
1. **N1:** Pick one and make the plan match it:
   - (a) Add fragment handling, a 4th file (`main.dart`): treat `uri.fragment` `/catalog` or `/catalog/<nac>` like the path branch. Update the scope (line 272) and add a test.
   - (b) Declare `#/catalog` out of scope with the reason, and change FT-3 to expect today's behavior (home or login, no crash). Remove the false claim on line 34.
2. **N2:** Escape `$` in the reason string (`\$30`, `\$1.09`) or drop it. Confirm `flutter analyze` is clean for the test file.
3. **N3:**
   - Option A must `git checkout c547b7a0` (or use a worktree at `c547b7a0`), then build and deploy p7-gate, then record that SHA.
   - Use `git revert --no-edit <sha>` (no `-m`).
   - Option B (channel delete) needs CoS or Eric approval before use, or should be removed.
   - State that Firebase commands run on the host.
4. **N4:** Send silver $0.05 coins with `nickel`, `wartime` or `war` in the combined text, or years 1942–1945, to `_ag35` (0.05626) before the half-dime lookup. Add a test: `'Silver Alloy'`, `'5 cents'`, series `'Jefferson Wartime Nickel'` gives 0.05626 × spot (1.6878 at $30).
5. **N5:** Use a real NAC code in FT-2. Name the FT-4 test account or data source and the Firestore-write position.

## New-regression scan (catalog, old against v2)
328 rows change. None crash.

| Change | Rows |
|---|---|
| Now at the 90%-standard weight for their denomination (dimes, quarters, halves, the 1871–1872 half dimes, the 1995-S silver quarter). Includes about 80 mislabeled clad quarters; see below. | 287 |
| Silver-proof American Women quarters, now 0.18084 against about 0.2039 (about 11% low; old value was 3.8× high) | 6 |
| 1976-S 40% "Silver Clad" Kennedy half, now 0.36169 against 0.14792 (old value was 5.2× high) | 1 |
| Now null: 23 silver medals with no denomination, 4 three-cent silver, 3 twenty-cent pieces, 1 planchet, 1 1792 pattern cent, 1 Ike dollar the data lists as "1 cent". Statement #3 says these should return null, which is acceptable; the Ike is a data error. | 33 |
| Half-dime weight that should be war-nickel weight (N4) | 1 |
| **Total** | **328** |

Pre-existing, not regressions (not scored):
- About 80 clad 1966–1998 quarters are labeled series "Washington Silver Quarter" in the catalog, so they now read 0.18084 oz instead of 0.77344. That's still wrong; it is a catalog data issue.
- 40% Ike dollars still read 0.77344 (correct is 0.3161).

## Advisories (not scored)
- The half-dime 0.03617 comment (line 71) is fine now.
- The header times (filed 14:55 on line 2, file written 14:48) and the attempt label (line 5) should be fixed for the record.

## Authority statement
This score **grants no code, merge, deploy, Firestore, Stripe or go-live authority.** It is REVISE, so **no SAG packet was built**. The HOLD order and go-live stop rule stay in force. Next step: a v3 plan from AG CoS v5, which would be track attempt 3 of 10 and writer attempt 3 of 4, then CoS 95, then full-plan SAG 95 on the exact SHA, then Eric's new scoped typed YES for the p7-gate preview only.
