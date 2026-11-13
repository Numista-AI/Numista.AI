# DESIGNATED CoS PLAN SCORE: NET-816 Fail-Fix A1/A2, plan v5 (writer: Claude)

**Score: 100 / 100, PASS. No material defects.** (Pass mark 95; only material defects count: correctness, safety, permissions, execution. Cosmetics are not deducted. The advisories below are not scored.)
Scored by GB CoS (designated CoS gate), 10 Nov 2026, **4:13 PM ET**.
**Count: track attempt 5 of 10; writer Claude's attempt 1 of 2.** Eric allotted Claude 2 tries (t2501u). The v6 try is **not needed**.

## Plan scored
- `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v5_CLAUDE_20261110.md`
- SHA-256 **`0a7543aff8076f82ac66de1d5e4eb855a332272f326c453594162a368d123f52`**, 26,194 bytes, 401 lines, LF line endings, written 4:08:07 PM ET. The laptop and box copies match.
- It isn't filed on any Desk route; it was delivered only to Eric's MY TESTING folder.

## Baseline and sources
- v4 record `COS_SCORE_NET-816_FAILFIX-A1A2_v4_94_REVISE_20261110.md`, SHA `dc67695493be76e5df1a1abec9a8fb2aac4a624d9111b9e637bde35d437a788b`.
- v4 plan, SHA `eed81270…aeb1c`.
- Claude test packet, SHA `49b0bcd3…ce39`.
- HOLDs `74611e05…` (preview) and `41b8bd5f…` (go-live stop rule).
- Repo checked read-only: `numista_mobile` is identical to `c547b7a0` at tip `7fe4fae8`.
- Scratch tests only, in `C:\Users\ericd\AppData\Local\Temp\cos_net816ff_ro\v5_check\`, on Windows PowerShell **5.1.26100** (EDS_Laptop has no `pwsh`). No repo writes.

## R1–R3 closure (each verified)

| v4 | Status | Evidence (v5 section / line) |
|---|---|---|
| **R1** rollback target / HOLD `74611e05` | **Closed** | **§7.1 line 302:** "`c547b7a0` is never a deploy target (HOLD `74611e05…`)".<br>**§7.2 lines 305–317:** a mandatory read-only pre-deploy record, using `firebase hosting:channel:list --project studio-9101802118-8c9a8` (a valid CLI command), plus the source commit or "UNKNOWN; do not guess". There are two rollback targets: **RT-A** (a recorded commit, only if it is known and not `c547b7a0`) and **RT-B** ("no redeploy", the default when unknown). Rolling back to "a commit under any HOLD is forbidden".<br>**§7.3 lines 319–326:** Eric's YES must name the built SHA, channel/project/host, the RT, and "`c547b7a0` is not deployed". "No rollback deploy runs unless the YES named RT-A with that SHA."<br>**Script line 343:** a guard throws on the placeholder or on `c547b7a0*`. Tested: **both throw before any git call** (modes `placeholder` and `forbidden`). |
| **R2** PowerShell syntax / isolation | **Closed** | **§7.4 lines 340–372:** the block is labeled `powershell` and has `$ErrorActionPreference='Stop'` (line 341). `Set-Location $Repo` comes before any `git worktree` (line 346). The path is `Join-Path $env:TEMP 'p7gate_rollback_target'` (line 347), with a guard that the worktree is outside the repo (line 348). `Invoke-Native` checks `$LASTEXITCODE` (lines 350–353), and `try/finally` removes the worktree and prunes (lines 366–371).<br>**Scratch run** (the verbatim block, with only the repo path, SHA and `$env:TEMP` redirected to scratch, and `flutter`/`firebase` replaced by native `.cmd` stubs that write to stderr):<br>success: completes; worktree removed; working folder back in the repo.<br>deploy fails with exit 1: throws "Command failed with exit code 1"; **the `finally` still removes the worktree**.<br>`Join-Path $env:TEMP` gives `C:\Users\ericd\AppData\Local\Temp\p7gate_rollback_target`, outside the repo, against v4's literal `%TEMP%`, which landed inside the repo. **The shared tree is never checked out**; `git worktree add --detach` is used. |
| **R3** FT-4 honesty | **Closed** | **§5 line 274:** "Local unit-level A2 proof on typed-in inputs (not on the preview)", with literal strings and $1.0851 = 0.03617 × $30, formatted `$1.09`. **§5.1 lines 276–280:** "does not read" the catalog row; the real row gives null, which is harmless; the preview dashboard check is "DEFERRED, not verified on preview"; and it overlaps gate step 2. All of that is accurate (confirmed against `catalog_public_v1.json` and the `/demo` asset). |

## No regressions against v4 (verified)
- **Code is byte-identical:** all 7 v4 code blocks reappear exactly in v5. Those are the A1 `/catalog` + `/catalog/**` rewrite JSON, Changes 2.1–2.5, and the 97-line test block (a)–(e) with escaped `\$`. Only v4's bash rollback block was replaced, as R2 requires.
- **Melt math:** I reran the simulation on all 3,202 catalog rows. v5 is identical to v4, with 0 rows changed. Against the original code, it's the same 328-row improvement set with no regressions, and the war nickel reads 0.05626.
- **Dart:** the test block is identical to the one CoS checked under `dart analyze` (no issues found) and `dart run`, which passed all 14 checks against the patched scratch service.
- **Pinned deploy command** `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8` appears in §7.1 line 303 and script line 364. Build is `--base-href "/"`.
- **Worktree isolation** is kept and strengthened. Zero Firestore reads or writes, and no rules deploy (§8.3). Stripe and the Christmas promo are untouched. Both HOLDs are honored (§8.5). `origin/main` stays pinned. The scope is exactly 3 files.
- FT-1 to FT-3 and gate step 4 have light copy edits only ("HTTP 200 returned" became "HTTP 200"); the pass/fail substance is unchanged. Not material.

## Open questions (§9): all legitimate, none invented

| # | Claude's question | CoS view |
|---|---|---|
| 1 | What's on p7-gate now | **Legitimate.** The packet said it was unverified, and Claude used the packet's NET-748 fact correctly. |
| 2 | Can `channel:list` output give the source commit? | **Legitimate**, and it shows good judgment. The output shows channel, URL, last release time and expiry, not a source commit, so RT-B as the default is the right call. |
| 3 | Firebase credentials unconfirmed | **Legitimate.** It's in the packet, and Claude correctly notes it blocks both §7.2 and the deploy. |
| 4 | Preview dashboard check deferred | **Legitimate.** It restates the R3 gap. |
| 5 | `--expires` | **Legitimate.** Claude correctly declined to change the pinned form. |
| 6 | Fix SHA, URL hash and release IDs don't exist yet | **Legitimate.** No values were invented. |

**Invented facts: none found.** Every command used is valid:
- `git worktree add --detach`, `git worktree remove --force`, `git worktree prune`
- `firebase hosting:channel:list` / `channel:deploy`
- `flutter build web`

Every path, SHA and name comes from the packet or the repo. The only new name, `p7gate_rollback_target`, is a new scratch folder name, not a claimed fact.

## Advisories (not scored; optional polish if anyone revises; v6 is NOT required)
1. **Captured-stderr edge case** (§7.4, `Invoke-Native`, line 351).
   - **Problem:** on Windows PowerShell 5.1, if the block is run with stderr redirected (for example `… 2>&1 | Tee-Object log`), `$ErrorActionPreference='Stop'` turns git's informational stderr line "Preparing worktree (detached HEAD …)" into a terminating error. The block then throws even though the command succeeded. I reproduced this in scratch.
   - **Impact:** it **fails closed**: the `finally` cleanup ran and nothing was left behind. A normal in-process run works.
   - **Fix that passed in scratch:** inside `Invoke-Native`, set `$ErrorActionPreference='Continue'` around `& $Cmd 2>&1 | ForEach-Object { "$_" }` and restore it in a `finally`, still checking `$LASTEXITCODE`.
2. **Abbreviated-SHA guard** (line 343). `-like 'c547b7a0*'` misses a shorter abbreviation such as `c547b7a`. Stronger: `if ((git rev-parse $RollbackSha) -eq 'c547b7a0ad22923d90042a259da9b56b2c0d6c0c') { throw … }`. The YES rule in §7.3 already blocks this, so it's belt and braces.
3. **§7.2 step 1 / §7.3 "release/version identifier".** `channel:list` gives the *last release time*, not a version ID. Wording such as "last release time (and version ID if obtainable)" avoids an unsatisfiable requirement. RT-B covers it either way.
4. **In-place fix build at the branch tip** (§7.4 line 377). Docs commits may land after the fix commit. Before an in-place build, add a check that `git diff <fix_sha> HEAD -- numista_mobile` is empty, and record both SHAs.

## Writer assessment (Claude, attempt 1)
- **Quality:** high. All three fixes closed in one pass. The rollback block is the strongest version on this track: exit-code checks, `try/finally` cleanup, a path guard, a forbidden-SHA guard and a manual cleanup line.
- **Honesty:** high. FT-4 and §5.1 state exactly what is and isn't proven. Unknowns are written as "UNKNOWN; do not guess", with RT-B as the safe default. No facts were invented.
- **Instruction-following:** high. It kept all code byte-identical, used the exact output name and header, included the change list and open questions, kept the pinned command, and honored every constraint. The only deviation is minor wording compression in FT-1 to FT-3, with no change to substance.

## Authority statement
This score **grants no code, git, merge, deploy, Firestore, Stripe or go-live authority.** It is a CoS PASS only. Next in the gate: a **full-plan SAG review ≥95 on this exact SHA (`0a7543af…3f52`)**, then **Eric's new scoped typed YES** naming the built fix SHA and the rollback target (§7.3). Per instruction, **no SAG packet was built**; it can be prepared when Eric or CoS asks. Both HOLDs (`74611e05…`, `41b8bd5f…`) and the go-live stop rule stay in force.
