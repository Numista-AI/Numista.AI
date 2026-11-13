# PLAN (v5) — NET-816 Catalog Chunk 1 Fail-Fix A1/A2
Filed: 2026-11-10 (ET), writer: Claude.
Target Track: NET-816 Catalog Chunk 1 v2.2 Fail-Fix (A1 Blocker & A2 Major).
In response to: `COS_SCORE_NET-816_FAILFIX-A1A2_v4_94_REVISE_20261110.md` (94/100 REVISE; R1, R2, R3).
Attempt: Track attempt 5 of 10; writer Claude attempt 1 of 4
Status: **STRICT PLAN ONLY. NO CODE, NO DEPLOYS, NO MERGES, NO FIRESTORE, NO STRIPE before gated approval (CoS 95, then full-plan SAG 95, then Eric's own scoped typed YES).**

---

## 0. v4 → v5 change list

| # | Where | Change | Reason |
|---|---|---|---|
| R1 | §7.2, §7.3, §9 | Rollback no longer redeploys `c547b7a0`. A **pre-deploy record** of what is actually on p7-gate is mandatory (§7.2). Rollback target = that recorded build, or "no redeploy". The target goes into Eric's scoped YES text (§7.3). `c547b7a0` is barred from every deploy. | HOLD `74611e05…` forbids a `c547b7a0` deploy. `c547b7a0` was never on p7-gate (blocked 11:40 AM ET). |
| R2 | §7.4 | Rollback block is now `powershell`: `$ErrorActionPreference='Stop'`, `Set-Location` into the repo before any `git worktree`, `$env:TEMP` path, native-exit-code checks, `try/finally` worktree removal. | `%TEMP%` is literal in PowerShell and would put the worktree inside the shared repo. |
| R3 | §5 FT-4, §5.1 | FT-4 is described as a local unit-level A2 proof on typed-in inputs. It does not read the 1853 catalog row. The visual half-dime dashboard check on the preview is a stated deferred gap, not a pass. | The test calls `compute` with literals. The real row has `composition: null` and returns null from `compute`. |
| — | §1 | Defect-closure table now lists R1–R3. | Housekeeping. |
| — | §7.1 | Built-commit SHA must be named in the YES. | Needed so R1's YES text is coherent. |

Everything else is carried from v4 unchanged: A1 rewrites, Changes 2.1–2.5, tests (a)–(e), FT-1 to FT-3, the §6 gate, base/build identity, `git revert --no-edit`, the channel-delete rule, and the 3-file scope.

---

## 1. Executive Summary & Defect Closure

| Defect | Area | Resolution in v5 |
|---|---|---|
| **R1** | Permissions: rollback target | **Closed (§7.2–§7.3):** rollback restores the build recorded on p7-gate before the fix deploy, or is "no redeploy". The target is named in Eric's YES. `c547b7a0` is never deployed. |
| **R2** | Safety: shell syntax | **Closed (§7.4):** PowerShell block, `Set-Location` first, `$env:TEMP`, stop on error, guaranteed worktree cleanup. |
| **R3** | Execution: FT-4 honesty | **Closed (§5, §5.1):** FT-4 is a local unit proof on literals. The real 1853 row is not checked. The preview dashboard check is deferred. |

(v4's M1/M2 closures remain: isolated worktree, never check out in the shared tree, pinned deploy form, zero-write FT-4.)

---

## 2. Root Cause Analysis & Architectural Boundaries

### 2.1 A1 BLOCKER: Missing `/catalog` Firebase Hosting Rewrites & Scope Boundary on `#/catalog`
* **Locations:** `numista_mobile/firebase.json` lines 49–133 (`hosting.rewrites`), `numista_mobile/lib/main.dart` lines 113–181.
* **Server-side rewrites:**
  - Firebase Hosting uses explicit rewrites, not a blanket `**`.
  - `/about`, `/pricing`, `/login` etc. are rewritten to `/index.html`. `/catalog` and `/catalog/**` were omitted.
  - Adding both, pointing to `/index.html`, makes direct requests and deep links return HTTP 200 with `/index.html`.
* **Client-side routing at `c547b7a0`:**
  - `main.dart:115–118` inspects `uri.path`.
  - `main.dart:154–181` launches `CatalogBrowseScreen` if `normalizedPath == '/catalog' || path.startsWith('/catalog/')`.
  - Browsers never send the hash fragment to the server. `https://numista.ai/#/catalog` arrives with `path == '/'`.
  - `main.dart:113–114` documents: `// Hash-fragment URLs (e.g. /#/claim?...) have uri.path == '/' — they pass through to the normal app flow correctly.` So `/#/catalog` skips line 155 and falls through to the front-door flow.
* **Scope boundary (N1):**
  - Canonical public catalog access is **path-based** (`/catalog`, `/catalog/<nac>`).
  - Changing `main.dart` to inspect `uri.fragment` is **OUT OF SCOPE**. It keeps the 3-file scope and avoids side effects on front-door hash routing.
  - FT-3 checks that `/#/catalog` loads the normal front-door flow without a 404 or crash.

### 2.2 A2 MAJOR & N4: Sub-Dollar Silver, War Nickel, and Half Dime Melt Logic
* **Locations:** `numista_mobile/lib/services/melt_value_service.dart` lines 11–17 (`_ag90`), 24–26 (`_ag35`), 189–202 (`compute()`), 230–238 (`_matchDenom`).
* **Root causes:**
  1. `_ag90` lacked `'half dime'`.
  2. `_matchDenom` mapped $0.05 only to `'nickel'`.
  3. The `?? 0.77344` fallback gave all unrecognized 90% silver the Morgan dollar weight.
  4. Line 201 `if (ag > 0) return ag * 0.77344 * count;` was an unconditional Morgan fallback for any "silver" coin without "90%".
* **Fix strategy:**
  - $0.05 silver coins with `nickel`, `war` or `wartime` in the combined text go to `_ag35` (0.05626 oz).
  - Other $0.05 silver coins (half dimes) go to `_ag90['half dime']` (0.03617 oz).
  - Dimes, quarters and halves resolve to their standard weights.
  - Morgan/Peace dollars (even with empty denom, or denom "CC" with series "1$-Morgan dollar") resolve to 0.77344 oz.
  - Unmodeled silver tokens return `null` and never get a Morgan weight.

---

## 3. Scope of Modifications (Strictly 3 Files)

1. `numista_mobile/firebase.json` (Hosting rewrites for `/catalog` and `/catalog/**`)
2. `numista_mobile/lib/services/melt_value_service.dart` (melt valuation corrections)
3. `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart` (unit and regression tests)

Zero modifications to `main.dart`, backend services, or database schemas.

---

## 4. Surgical Code Modification Specification (PLAN ONLY)

### File 1: `numista_mobile/firebase.json`
**Location:** inside `hosting.rewrites`, after the `/terms` rewrite (line 72) and before `/about` (line 73):
```json
      {
        "source": "/catalog",
        "destination": "/index.html"
      },
      {
        "source": "/catalog/**",
        "destination": "/index.html"
      },
```
* **Effect:** GET `/catalog` and `/catalog/<nac_code>` return HTTP 200 with `/index.html`, so `main.dart` mounts `CatalogBrowseScreen`.

### File 2: `numista_mobile/lib/services/melt_value_service.dart`

#### Change 2.1: Add `'half dime'` to `_ag90` (lines 11–17)
```dart
  static const _ag90 = {
    'half dime':   0.03617,   // Nominal 1.25g (1853+ 1.24g) × 90% ÷ 31.1035
    'dime':        0.07234,   // 2.5g × 90% = 2.25g Ag ÷ 31.1035
    'quarter':     0.18084,   // 6.25g × 90% = 5.625g Ag ÷ 31.1035
    'half':        0.36169,   // 12.5g × 90% = 11.25g Ag ÷ 31.1035
    'half dollar': 0.36169,
    'dollar':      0.77344,   // Morgan / Peace: 26.73g × 90% ÷ 31.1035
  };
```

#### Change 2.2: Update `_matchDenom` for $0.05 face value (lines 230–238)
```dart
  static double? _matchDenom(Map<String, double> table, String rawDenom) {
    final fv = parseFaceValue(rawDenom);
    if (fv == 1.00 && table.containsKey('dollar')) return table['dollar'];
    if (fv == 0.50 && table.containsKey('half')) return table['half'];
    if (fv == 0.25 && table.containsKey('quarter')) return table['quarter'];
    if (fv == 0.10 && table.containsKey('dime')) return table['dime'];
    if (fv == 0.05) {
      if (table.containsKey('half dime')) return table['half dime'];
      if (table.containsKey('nickel')) return table['nickel'];
    }
    return null;
  }
```

#### Change 2.3: Update 35% War Nickel Detection (lines 197–200)
```dart
      if (combined.contains('35%') || ((combined.contains('war nickel') || combined.contains('wartime')) && parseFaceValue(denom) == 0.05)) {
        final oz = _matchDenom(_ag35, denom) ?? 0.05626;
        return ag * oz * count;
      }
```

#### Change 2.4: Fix 90% Silver Block & Preserve Robust Dollar Fallback (lines 189–192)
```dart
      if (combined.contains('90%') || combined.contains('half dime') || combined.contains('half-dime') || combined.contains('morgan') || combined.contains('peace') || combined.contains('barber') || combined.contains('walking liberty') || combined.contains('standing liberty') || combined.contains('mercury')) {
        final fv = parseFaceValue(denom);
        final isDollar = fv == 1.00 || combined.contains('dollar') || combined.contains('morgan') || combined.contains('peace');
        final oz = _matchDenom(_ag90, denom) ?? (isDollar ? 0.77344 : null);
        if (oz != null) return ag * oz * count;
        return null;
      }
```

#### Change 2.5: Close Generic Silver Morgan Inflation Fallback (lines 201–202)
Replace `if (ag > 0) return ag * 0.77344 * count;` with:
```dart
      if (ag > 0) {
        final fv = parseFaceValue(denom);
        // N4: Route 5-cent wartime/war nickels without "35%" text to 35% war nickel weight
        if (fv == 0.05 && (combined.contains('nickel') || combined.contains('wartime') || (combined.contains('war') && !combined.contains('award') && !combined.contains('howard') && !combined.contains('edward')) || combined.contains('manganese'))) {
          return ag * 0.05626 * count;
        }
        final isDollar = fv == 1.00 || combined.contains('dollar') || combined.contains('morgan') || combined.contains('peace');
        final oz = _matchDenom(_ag90, denom) ?? (isDollar ? 0.77344 : null);
        if (oz != null) return ag * oz * count;
        return null;
      }
```

### File 3: `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`
**Location:** inside `main()`, group `'NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1 & NET-837 #2/#4/#5)'`:
```dart
    test('NET-816 Fail-Fix A2 & D1-D3/N2/N4 regression: half dime, war nickel, sub-dollar silver, and Morgan dollars', () {
      const spot = <String, double>{'Gold': 3000.0, 'Silver': 30.0};

      // (a) Removed fallback: unlisted 90% sub-dollar returns null, NOT 0.77344
      final unlistedTwentyCent = MeltValueService.compute(
        metalContent: '90% Silver',
        denomination: 'Twenty Cent',
        spotPrices: spot,
      );
      expect(unlistedTwentyCent, isNull,
          reason: 'Unlisted sub-dollar silver must return null, never 0.77344');

      // (b) Dollar fallback preserved for Morgan/Peace without "dollar" in denomination
      final morganCC = MeltValueService.compute(
        metalContent: 'Silver',
        denomination: 'CC',
        programSeries: '1\$-Morgan dollar',
        spotPrices: spot,
      );
      expect(morganCC, closeTo(0.77344 * 30.0, 1e-4),
          reason: 'Morgan with denom CC must receive 0.77344 dollar melt');

      final morganNoDenom = MeltValueService.compute(
        metalContent: 'Silver',
        denomination: '',
        programSeries: 'Morgan',
        spotPrices: spot,
      );
      expect(morganNoDenom, closeTo(0.77344 * 30.0, 1e-4),
          reason: 'Morgan with empty denom must receive 0.77344 dollar melt');

      // (c) Standard denominations preserved unchanged:
      // 90% Dime (0.07234 oz -> $2.1702 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Dime', spotPrices: spot),
        closeTo(0.07234 * 30.0, 1e-4),
      );
      // 90% Quarter (0.18084 oz -> $5.4252 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Quarter', spotPrices: spot),
        closeTo(0.18084 * 30.0, 1e-4),
      );
      // 90% Half Dollar (0.36169 oz -> $10.8507 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Half dollar', spotPrices: spot),
        closeTo(0.36169 * 30.0, 1e-4),
      );
      // 90% Dollar (0.77344 oz -> $23.2032 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Dollar', spotPrices: spot),
        closeTo(0.77344 * 30.0, 1e-4),
      );
      // 40% Half Dollar (0.14792 oz -> $4.4376 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '40% Silver', denomination: 'Half dollar', spotPrices: spot),
        closeTo(0.14792 * 30.0, 1e-4),
      );
      // 35% War Nickel (0.05626 oz -> $1.6878 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '35% Silver', denomination: 'Nickel', spotPrices: spot),
        closeTo(0.05626 * 30.0, 1e-4),
      );

      // (d) N4: Wartime nickel with "Silver Alloy" and "Wartime Nickel" series (lacking "35%")
      expect(
        MeltValueService.compute(
          metalContent: 'Silver Alloy',
          denomination: '5 cents',
          programSeries: 'Jefferson Wartime Nickel',
          spotPrices: spot,
        ),
        closeTo(0.05626 * 30.0, 1e-4),
        reason: 'Jefferson Wartime Nickel in Silver Alloy must receive 0.05626 oz melt',
      );

      // (e) Half dime variants compute to 0.03617 oz * spot (~$1.0851 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: 'Silver (90%)', denomination: 'Half Dime', spotPrices: spot),
        closeTo(0.03617 * 30.0, 1e-4),
        reason: 'Silver (90%) Half Dime must equal 0.03617 oz',
      );
      expect(
        MeltValueService.compute(metalContent: 'Silver', denomination: 'Half dime', spotPrices: spot),
        closeTo(0.03617 * 30.0, 1e-4),
        reason: 'Generic "Silver" Half dime must equal 0.03617 oz',
      );
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Half-dime', spotPrices: spot),
        closeTo(0.03617 * 30.0, 1e-4),
        reason: '"90% Silver" Half-dime must equal 0.03617 oz',
      );
      expect(
        MeltValueService.format(metalContent: '90% Silver', denomination: 'Half Dime', spotPrices: spot),
        equals(r'$1.09'),
        reason: 'Formatted melt value string at \$30/oz silver spot must round to \$1.09',
      );
    });
```

---

## 5. Bounded Field Tester Checks (p7-gate Preview)

After build and deploy to `p7-gate`, the Field Tester runs these checks. FT-1 to FT-3 are on the preview. FT-4 is local.

| Check # | Target URL / Flow | Test Procedure | PASS Criteria | FAIL Criteria |
|---|---|---|---|---|
| **FT-1** | Direct GET `/catalog` | Open `https://numista-vault--p7-gate-<hash>.web.app/catalog` in a clean browser session. | HTTP 200. Page mounts Flutter SPA, shows "Public Coin Catalog" header, search input, type-photo cards, face value chips. | HTTP 404, blank page, or Firebase "Page Not Found". |
| **FT-2** | Direct GET `/catalog/<nac>` | Open `https://numista-vault--p7-gate-<hash>.web.app/catalog/NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2` (1853 Seated Liberty Half Dime). | HTTP 200. Deep link mounts the catalog item view for the 1853 Half Dime. Zero 404s. | HTTP 404, infinite spinner, or router exception screen. |
| **FT-3** | Direct GET `#/catalog` | Open `https://numista-vault--p7-gate-<hash>.web.app/#/catalog` in a clean browser session. | HTTP 200 (via `/` rewrite). App mounts into the front-door / login / home flow (per `main.dart:113-114`) without crash or 404. | HTTP 404, blank screen, crash, or redirect loop. |
| **FT-4** | **Local unit-level A2 proof on typed-in inputs** (not on the preview) | `cd numista_mobile; flutter test test/catalog_chunk1_face_value_and_card_test.dart --plain-name "half dime"` | Exit code 0. The A2 assertions pass: `MeltValueService.compute`/`format`, given the **literal strings** `'Silver (90%)'` / `'Half Dime'` and the like, return 0.03617 oz × spot (= $1.0851 at $30/oz, formatted `$1.09`), never the Morgan $23.20. Zero Firestore reads or writes. | Non-zero exit code, any test failure, or a half-dime result equal to the Morgan value ($23.20 at $30/oz). |

### 5.1 What FT-4 does NOT prove (stated gaps)
1. FT-4 **does not read** `assets/catalog/catalog_public_v1.json` or the row `NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2`. It never touches the real 1853 catalog row.
2. That real row has `composition: null`, `denomination: "Half dime"`, `series: "Seated Liberty Half Dime"`. Run through `compute` it returns **null (N/A)**, because no "silver" appears in its text. This is harmless: catalog cards never call `compute`.
3. **Deferred / not passed:** a visual half-dime **dashboard** melt check on the preview. It is not possible without a Firestore write. No zero-write account or demo coin holding a half dime exists, and the `/demo` data (`assets/guest_demo_coins.json`, 100 coins) has no half dime. This stays an open gap, recorded in the DONE report as "DEFERRED, not verified on preview". A later Eric-authorized track may close it.
4. FT-4 overlaps §6 step 2 (same test file). It is kept only as the named, filtered A2 proof.

---

## 6. Machine-Checkable Verification Gate

On gated authorization (CoS 95 + SAG 95 + Eric scoped typed YES):
1. `cd numista_mobile`
2. `flutter test test/catalog_chunk1_face_value_and_card_test.dart` (exit 0; all existing and new tests pass).
3. `flutter analyze lib/services/melt_value_service.dart test/catalog_chunk1_face_value_and_card_test.dart` (exit 0, 0 issues).
4. `python -c "import json; d = json.load(open('firebase.json')); rewrites = [r.get('source') for r in d['hosting']['rewrites']]; assert '/catalog' in rewrites, 'missing /catalog'; assert '/catalog/**' in rewrites, 'missing /catalog/**'; print('firebase.json rewrites VERIFIED')"` (exit 0).

---

## 7. Base Commit, Build Identity, Pre-Deploy Record & Rollback

### 7.1 Base Commit & Build Identity
* **Base branch:** `p7-v8.9`. **Base source commit:** `c547b7a0`. `numista_mobile/` at branch tip `7fe4fae8` is identical to it. `7fe4fae8` is docs-only.
* On the fix, create one commit on `p7-v8.9`:
  `git commit -m "fix(catalog): add /catalog rewrites and correct half-dime melt value (NET-816 A1/A2)"`
* The exact resulting SHA **MUST** be recorded in the `DONE_BATON_...` report.
* The preview deploy proceeds only after Eric gives a new scoped typed YES naming that built SHA (see §7.3).
* **`c547b7a0` is never a deploy target** (HOLD `74611e05…`). The A1/A2-fixed commit is the only commit that may be deployed to p7-gate.
* Deploy form (pinned): `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8`, run from `numista_mobile` (or the worktree's `numista_mobile`), on `EDS_Laptop`. Build: `flutter build web --release --base-href "/"`.

### 7.2 Pre-Deploy Record of p7-gate (mandatory, read-only, before the fix deploy)
CoS has **not** verified what is on p7-gate now (last *recorded* deploy: `EXECUTE_DONE_NET-748_v5_2026-11-04.md`). The plan therefore assumes nothing. Before the fix deploy, on `EDS_Laptop`, the executing agent records in the DONE report:
1. Output of `firebase hosting:channel:list --project studio-9101802118-8c9a8`. This is read-only. It needs valid Firebase credentials and no Firestore access. Record the p7-gate entry: channel URL, release/version identifier and time, and expiry.
2. The **source commit** of that release, if it can be determined from the channel/release metadata or from a DONE record for the matching deploy. If it can't be determined, write "source commit UNKNOWN". Do not guess.
3. The current branch tip SHA and `git status` (clean for `numista_mobile`).
4. Whether the channel exists at all. If it doesn't, rollback = "no redeploy" (nothing to restore).

From this record, the **Rollback Target (RT)** is exactly one of:
* **RT-A: "Rebuild and redeploy commit `<SHA>`".** `<SHA>` is the recorded source commit of the release found in step 2. Allowed only if the source commit is known and is **not** `c547b7a0`.
* **RT-B: "No redeploy".** Used when the source commit is unknown, when the channel didn't exist, or when Eric prefers it. If the fix deploy is bad, the channel is left as-is and Eric decides the next step (for example a new fix plan). No automatic restore.

If the recorded build's source commit is not known, **RT-B is the default.**
Rolling back to a commit that is under any HOLD is forbidden. `c547b7a0` is excluded by name.

### 7.3 Eric's scoped YES must name the rollback target
The request for Eric's new typed YES for the preview deploy must contain all of the following, and the YES is valid only if its text names them:
* The built fix commit SHA (§7.1).
* Target: channel `p7-gate`, project `studio-9101802118-8c9a8`, host `EDS_Laptop`. No live hosting.
* **Rollback target:** either `RT-A: commit <SHA recorded in §7.2>`, or `RT-B: no redeploy`, with the recorded p7-gate release/version identifier quoted.
* A statement that `c547b7a0` is not deployed.

No rollback deploy runs unless the YES named RT-A with that SHA. Without an RT-A YES, nothing is redeployed.

### 7.4 Rollback Procedures

1. **Source rollback (no deploy):**
   * If unit tests fail before commit:
     `git checkout c547b7a0 -- numista_mobile/firebase.json numista_mobile/lib/services/melt_value_service.dart numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`
     (path-limited restore of 3 files only. It is not a tree checkout).
   * If already committed: `git revert --no-edit <built_commit_sha>` and push to `origin/p7-v8.9`.

2. **Hosting channel `p7-gate` rollback (RT-A only, in an isolated worktree).**
   **SAFETY RULE:** never run `git checkout <commit>` in the shared `C:\Users\ericd\Documents\MyVertexProject` tree (it holds the live Desk filing folders). Any build of a commit other than the branch tip happens in a separate worktree under `$env:TEMP`.
   Set `$RollbackSha` from the §7.2 record (a full or abbreviated SHA that is **not** `c547b7a0`). Requires valid Firebase credentials (an Eric action, not an agent action).

```powershell
$ErrorActionPreference = 'Stop'
$RollbackSha = '<SHA recorded in section 7.2 and named in Eric YES>'   # must be filled in; never c547b7a0
if ($RollbackSha -like '<*' -or $RollbackSha -like 'c547b7a0*') { throw 'Rollback SHA missing or forbidden (c547b7a0).' }

$Repo = 'C:\Users\ericd\Documents\MyVertexProject'
Set-Location $Repo                                   # must precede any git worktree command
$Wt = Join-Path $env:TEMP 'p7gate_rollback_target'   # = C:\Users\ericd\AppData\Local\Temp\p7gate_rollback_target
if ($Wt -notlike "$env:TEMP*" -or $Wt -like "$Repo*") { throw 'Worktree path must be outside the repo.' }

function Invoke-Native([scriptblock]$Cmd) {          # $ErrorActionPreference does not catch native exit codes
  & $Cmd
  if ($LASTEXITCODE -ne 0) { throw "Command failed with exit code ${LASTEXITCODE}: $Cmd" }
}

try {
  # 1. Isolated detached worktree at the recorded rollback commit (shared tree untouched)
  Invoke-Native { git worktree add --detach $Wt $RollbackSha }

  # 2. Build with the pinned base-href
  Set-Location (Join-Path $Wt 'numista_mobile')
  Invoke-Native { flutter build web --release --base-href "/" }

  # 3. Deploy to p7-gate with the pinned form (preview channel only)
  Invoke-Native { firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8 }
}
finally {
  # 4. Always leave the shared repo and remove the worktree, even after a failure
  Set-Location $Repo
  if (Test-Path $Wt) { git worktree remove $Wt --force }
  git worktree prune
}
```

   * `try/finally` guarantees worktree removal after any failure. If PowerShell itself is killed mid-run, clean up with `Set-Location C:\Users\ericd\Documents\MyVertexProject; git worktree remove "$env:TEMP\p7gate_rollback_target" --force; git worktree prune`.
   * `git worktree remove --force` deletes only that folder and its admin entry. `--force` is needed because of the untracked `build/`.
   * Record in the audit log: `$RollbackSha`, the new p7-gate release/version, and the time. Never record `c547b7a0` as deployed.
   * The same worktree pattern, with the fix SHA instead of `$RollbackSha`, applies if the fix build is made from a commit other than the current tip. Building at the current branch tip may be done in place, with no checkout.

3. **Channel teardown boundary:** deleting the channel (`firebase hosting:channel:delete p7-gate -f`) is **STRICTLY PROHIBITED** without Eric's prior explicit typed YES.

---

## 8. Invariant Protection & Scope Boundaries

1. **Strict PLAN ONLY:** no code modified, no commits, no deploys before the plan gate (CoS 95 + SAG 95 + Eric scoped typed YES).
2. **Pinned roots:** `origin/main` stays `9f04550a45fa4da082ba8948c2d89a521a90fa45`. No push or merge to `main`.
3. **Protected infrastructure:** live hosting (`numista.ai`) is not deployed. Cloud Firestore is not read or written, and no Firestore rules are deployed. Stripe is untouched. The Christmas promo code (NET-827) is untouched. No live Stripe keys.
4. **Scope isolation:** exactly the 3 named files.
5. **Standing HOLDs honored:** preview HOLD `74611e05…` (no `c547b7a0` deploy, ever. Preview deploy only at the A1/A2-fixed commit after CoS 95, SAG 95 and Eric's new scoped YES). Go-live stop-rule HOLD `41b8bd5f…` (no live deploy, no merge to `main`, no live Stripe keys).
6. No secrets, tokens or keys appear in this plan. Firebase re-authentication is an Eric action; no agent handles passwords.

---

## 9. Open questions / facts not available

1. **What is on p7-gate now.** Unverified by CoS. Last recorded deploy is NET-748 (4 Nov 2026). §7.2 requires recording it before the fix deploy. Until then RT-A vs RT-B is undecided, and RT-B is the default.
2. **Whether the p7-gate release's source commit can be derived** from `firebase hosting:channel:list` output alone. The packet doesn't say what metadata that output carries. If it can't, RT-B applies unless Eric supplies a SHA.
3. **Firebase CLI credential status.** The 11:40 AM ET attempt was blocked by expired credentials. Re-authentication by Eric is not confirmed. This blocks both the §7.2 record and any deploy.
4. **Preview dashboard half-dime visual check:** deferred (§5.1). No zero-write account or demo coin exists.
5. **Channel expiry.** `channel:deploy` without `--expires` resets expiry to the CLI default (CoS advisory). Whether to add `--expires` would change the pinned command form, so it is not added. Eric/CoS may decide.
6. **Exact fix commit SHA, preview URL hash, and release IDs** do not exist yet. They are recorded at execution time and are not invented here.
