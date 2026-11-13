# DESIGNATED CoS PLAN SCORE: NET-816 Fail-Fix A1/A2 (AG CoS v5), plan v3

**Score: 94 / 100, REVISE** (pass mark 95; only material defects count: correctness, safety, permissions, execution. No points taken off for cosmetics.)
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 3:20 PM ET.
**Count: attempt 3 of 10 on the NET-816 fail-fix track; writer AG CoS v5's attempt 3 of 4.** The plan's line 5 is now correct. A v4 would be v5's **4th and last** attempt under Eric's 4/10 rule; if v4 fails, someone else takes over.

## Plan scored
- `BETA TEST\Grok Bot\8 OCT 26\BATONS\PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v3_AGCOS-V5_20261110.md`
- SHA-256 `801c0d80121c8c363381bb6d325dfbcf24fb2925d8bba3ee7456e3aa49658835`, 20,216 bytes, 323 lines, last written 3:05:42 PM ET. This matches Desk's report.
- All six routes are byte-identical (same SHA and size): `8 OCT 26\BATONS`, `\RADIO NET`, `\INBOX`, `\OUTBOX`, and `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX` and `\OUTBOX`.

## Baseline and sources
- v2 record `COS_SCORE_NET-816_FAILFIX-A1A2_v2_87_REVISE_20261110.md`, SHA-256 `ea161668d053ca733550242e92247bfeb572291b5255c9ba15ab51de59cb2dea`.
- v1 record, SHA `a4754854…dec50885`.
- Code Reviewer review, SHA `3e2c1670…864ff`.
- HOLD order, SHA `41b8bd5f…778943d`.
- Source checked read-only at `c547b7a0`, using `git show` / `git grep`. `numista_mobile` is identical between `c547b7a0` and HEAD `999daf14`.
- Scratch checks on the laptop only, in `%TEMP%\cos_net816ff_ro\v3_check\`:
  - `dart analyze` on the plan's test block, run as written.
  - `dart run` of that block against a scratch copy of `melt_value_service.dart` with v3 Changes 2.1–2.5 applied.
- Python port, v2 against v3, on all 3,202 catalog rows.

## v2 deduction closure map

| v2 | Status | Evidence |
|---|---|---|
| N1 `#/catalog` | **Closed** | Plan §2.1 (lines 32–42) is now accurate: `main.dart:113–114` and `:155`, with hash URLs falling through to the front door. FT-3 (line 271) now expects that behavior. Declaring it out of scope is **acceptable and honest**. `git grep -F '#/catalog'` at `c547b7a0` finds **no** references anywhere in the repo: app code, `web/` HTML, the sitemap or docs. No in-app code navigates to `CatalogBrowseScreen` except the path branch. The UX checklist (`UX_AUDIT_CHECKLIST_NET-816_NET-827_2026-11-10.md`) only uses the live path `https://numista.ai/catalog`. Nothing relies on the hash form. |
| N2 test compile | **Closed** | Line 256 escapes `\$30` and `\$1.09`; line 255 uses `r'$1.09'`. `dart analyze` on the scratch folder (the test block plus the v3-patched service and a minimal test harness): **No issues found.** `dart run` with the exact test block against the v3-patched service: **14 of 14 expectations pass, 0 fail.** |
| N3 rollback | **Partly closed** (see M1) | Fixed: `git revert --no-edit` (line 302); channel delete needs Eric's typed YES (line 314); host-machine rule stated (line 304); a checkout of `c547b7a0` is now present (line 308). The new checkout step is itself unsafe (M1). |
| N4 war nickel | **Closed** | Changes 2.3 and 2.5 (lines 120–154). Math: 5.0 g × 35% = 1.75 g ÷ 31.1035 = 0.056264 oz, and 0.05626 × $30 = **$1.6878**, which is right. Test (d) (lines 226–235) passes in the Dart run. The `Silver Alloy / 5 cents / Jefferson Wartime Nickel` input goes through the 35% branch (Change 2.3 `wartime`); `_matchDenom(_ag35)` at 0.05 skips the absent half-dime key and returns `nickel`, 0.05626. The **half-dime path is unaffected**: all 35 catalog half dimes, including the three 1871–1872 "5 cents / Silver" rows, stay at 0.03617, and the three half-dime tests pass. |
| N5 Field Tester | **Partly closed** (see M2) | FT-2 is closed: `NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2` exists in `catalog_public_v1.json` (1853 Seated Liberty Half Dime). `catalog_browse_screen.dart:72–80` matches the lowercased NAC exactly and opens that item's detail modal, so FT-2 can pass. FT-4 is still not runnable with zero writes (M2). |

## Deductions on v3 (each one is material)

| # | Pts | Area | Evidence | Defect |
|---|---|---|---|---|
| M1 | −4 | Safety / execution: rollback | Plan lines 306–313: "On `EDS_Laptop`: `git checkout c547b7a0` / `cd numista_mobile` / `flutter build web --release` / `firebase hosting:channel:deploy p7-gate --only hosting`" | **1. The checkout runs in the shared working tree.** The only repo this applies to is `C:\Users\ericd\Documents\MyVertexProject`, on branch `p7-v8.9`. That same tree holds the Desk routes (`BETA TEST\…\BATONS`, `RADIO NET`, `INBOX`, `OUTBOX`, `1 NUMISTA.AI\…`). I checked read-only: **416 tracked files added since `c547b7a0` would be removed from disk**, including today's NET-816/NET-827 batons, ACKs and HOLD copies. HEAD would be left detached with no step to return to `p7-v8.9`, and the daily 18:00 `chore: auto-backup` commit would then land on a detached HEAD. The files can be recovered from git, but other agents would lose the live routes in the middle of a rollback. The established safe pattern is a separate worktree, as in the existing `%TEMP%\p7gate_build_*` and `p7gate_deploy_*` folders.<br>**2. The deploy command differs from the SAG-pinned form.** The form pinned in earlier SAG advice and used by the NET-816 preview baton is `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8`, run from `numista_mobile`. v3 drops `--project` and adds `--only hosting`; `--only` takes a hosting site or target name (here `numista-vault`), not the word `hosting`. CI also builds with `--base-href "/"`. |
| M2 | −2 | Execution: Field Tester | Plan line 272 FT-4: "Uses read-only pre-seeded test fixtures or client-side demo mode (`/demo`). **Zero live Firestore writes.**" | **Neither source can show a half dime.** Browse-demo is read-only (`guest_seed_service.dart:10–11`, "no Firestore reads or writes"), but its asset `assets/guest_demo_coins.json` at `c547b7a0` has **100 coins and no half dime**; the only 5¢ coin is a 2026 nickel. No pre-seeded fixture or test account holding a 90% silver half dime is named, and none exists in the repo. Without adding a coin, which is a write, the Field Tester can't run FT-4. |

**Total: 100 − 6 = 94, REVISE.**

## Required fixes for v4 (both must close; this is v5's last attempt)
1. **M1:** Build and deploy the rollback from a dedicated worktree at `c547b7a0`, for example `git worktree add "%TEMP%\p7gate_rollback_c547" c547b7a0`. Never run `git checkout` in `MyVertexProject`. Use the pinned command `cd <worktree>\numista_mobile && flutter build web --release --base-href "/" && firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8`, on the host. Record the deployed SHA and remove the worktree afterwards. Apply the same rule to the forward build of the fix commit if it is built anywhere other than the `p7-v8.9` tree.
2. **M2:** Make FT-4 runnable with no writes. Choose one:
   - (a) Name an existing test account that already holds a 90% silver half dime, with read-only viewing.
   - (b) Replace FT-4 with a local read-only check against a fixture.
   - (c) Add a half dime to `guest_demo_coins.json`. That is a 4th file, so update the scope and add a test.
   - (d) Get Eric's explicit approval for one named test-account write.

## New-regression scan
- **v2 to v3, catalog:** exactly **1 row** changes: `1942-P Jefferson Wartime Nickel`, from 0.03617 to **0.05626**, now correct.
- **No other row changes and no new regressions.** All of v2's verified improvements carry over unchanged (old to v3: 328 rows changed, same set as v2).
- Synthetic edge cases, not in the catalog; advisories, not scored:
  - (i) Change 2.3's `wartime` keyword isn't limited to a 0.05 face value. A hypothetical "Silver / Dime" or "Quarter" with "wartime" in its text would get 0.05626.
  - (ii) The `war` substring in Change 2.5 also matches "award", "Howard" and "Edward", but only at a 0.05 face value.
  - (iii) A war nickel recorded as "Silver, Copper, Manganese" / "5 Cents" / "Jefferson" (no "nickel" or "war") still reads as a half dime (0.03617). Adding `manganese` or years 1942–1945 would close that.
  - A v4 may tighten these, but they don't block.

## Advisories (not scored)
- `numista_mobile/web/404.html:135` "Search the Catalog" links to `/?route=Catalog`. That goes to the in-app route path (`WelcomeScreen.pendingRoute`), not the public `/catalog`. It's a pre-existing UX issue outside A1, worth noting for UX.
- Header line 2 says "Filed 15:20 EST"; the file was written at 3:05 PM ET.
- v2's pre-existing data issues still stand: about 80 clad quarters labeled "Washington Silver Quarter", and 40% Ike dollars reading 0.77344.

## Authority statement
This score **grants no code, merge, deploy, Firestore, Stripe or go-live authority.** It is REVISE, so **no SAG packet was built** and nothing was copied to `For SAG`. The HOLD order and go-live stop rule stay in force. Next step: v4 from AG CoS v5, which would be track attempt 4 of 10 and writer attempt 4 of 4, then CoS 95, then full-plan SAG 95 on the exact SHA, then Eric's new scoped typed YES for the p7-gate preview only.
