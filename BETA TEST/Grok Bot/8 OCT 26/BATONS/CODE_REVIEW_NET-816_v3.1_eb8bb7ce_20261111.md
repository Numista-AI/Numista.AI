# CODE REVIEW — NET-816 Catalog Chunk 1 Fail-Fix R2, Plan v3.1 — BUILT_SHA eb8bb7ce

- **Reviewer:** Code Reviewer (Argon), for Eric Seaman / Numista.Ai
- **Date:** Wed 11 Nov 2026, ~10:20 AM ET (America/New_York)
- **Build under review:** `eb8bb7ce95fa7164617eef0d0ff804465829e8c9` (local branch `p7-v8.9`, EDS_Laptop, not pushed)
- **Base:** `a3d7dca20fbbaf06a522205b22d0740b600de52b`
- **Plan:** `PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md`, SHA-256 `785b04e5…3d04`, 41,293 B
- **Method:** Read-only. I used `git show`, `git diff`, `git log`, `git rev-parse` and `Get-FileHash`, plus a Python port of the face-value and melt logic run against the 3,202-row catalog asset on the box. I made no edits, checkouts, worktrees, pushes or deploys, and I did not run `deploy_preview.ps1`. I did not re-run `flutter test`; AG's results are reported below as **unverified**.

---

## BLUF: **PASS**

There are **0 Blocker and 0 Major findings** in money, access, data writes, routing or security on `eb8bb7ce`.

In plain English:
- The catalog link now opens the catalog instead of home.
- A two-coin set now shows $2.00.
- A silver half dime now melts at about $1.86 (silver at $51.51), not the old roughly 10x Morgan figure.
- Wikimedia photos are allowed in without loosening anything that runs code.
- The deploy script builds exactly this commit in a clean copy and stamps that commit ID into `version.json`. It checks the stamp before and after deploying, and it can only deploy to the p7-gate preview.
- The build touches no payments, no user data, no backend and no database rules.

**Condition (already part of the existing gate, not new):** the served `version.json` `git_commit` must read `eb8bb7ce95fa7164617eef0d0ff804465829e8c9`. The script enforces this at lines 103–106 and 145–148. It can only be confirmed once the preview is deployed, which still needs Eric's own `YES DEPLOY` line.

---

## 1. Pre-flight facts

| Check | Result |
|---|---|
| `eb8bb7ce` exists, type commit | Yes. Full SHA `eb8bb7ce95fa7164617eef0d0ff804465829e8c9`. HEAD of `p7-v8.9` = the same SHA. |
| Merge-base with `a3d7dca2` | `a3d7dca20fbbaf06a522205b22d0740b600de52b`, so the base is correct. |
| Commits from base to build | 13. **Only `eb8bb7ce` touches code.** The other 12 change docs only (`BETA TEST/**`, `Commercials/**`, `.md/.txt/.tar.gz/.zip`). No `numista_backend`, Firestore rules, Stripe or functions files are touched. |
| Code files in `eb8bb7ce` | 6 files, +238/−24: `firebase.json`, `lib/main.dart`, `lib/screens/catalog/catalog_browse_screen.dart`, `lib/services/melt_value_service.dart`, `test/catalog_chunk1_face_value_and_card_test.dart`, `test/catalog_routing_test.dart` (new). This matches plan §4 items 1–6. |
| Working tree | Dirty outside the app: 16 deleted `Commercials/**.mp4` files and untracked BATON/RADIO `.md` files. **`git status --porcelain -- numista_mobile numista_backend` is empty.** It does not matter either way, because the deploy script builds from a fresh detached worktree at the SHA (script :79–85), not from the working folder. |
| Catalog asset | `numista_mobile/assets/catalog/catalog_public_v1.json`, blob `a018d13a…` (5,895,259 B). The box copy hashes to the same git blob. |

## 2. Hash verifications

| File | Claimed | Actual | Match |
|---|---|---|---|
| Plan v3.1 (laptop `1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\` and `…\Carbon\`) | 785b04e5…3d04, 41,293 B | `785B04E55CD3BC2CCEFCF40B970E2139AD84ABA679053DDE7A59BB0C9EC13D04`, 41,293 B | ✅ |
| Plan v3.1 box copy (`/workspace/net816-failfix/round2/`) | same | `785b04e5…ec13d04`, 41,293 B, 701 lines | ✅ |
| READY file (RADIO NET, also BATONS/OUTBOX) | bc2d638a…8789, 7,133 B | `BC2D638AEA830E7654704F9FAC7E0B0A5E8B24D40D50D7BDFC7B4553364E8789`, 7,133 B | ✅ |
| READY box copy | same | `bc2d638a…364e8789`, 7,133 B | ✅ |
| `deploy_preview.ps1` (`1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\`, outside the git tree) | 884D6103…E81F, 7,390 B | `884D610301277DE6FE416C33046FD846D12AFF336DF67A6DFEA7B2114BAFE81F`, 7,390 B | ✅ |
| Implement baton | bf74d5e5… | `bf74d5e57d5c88dc…` | ✅ |

`MY TESTING\11 NOV 2026\` has no `NET-816_v3.1_REVIEW` folder and no AG bundle or patch. It holds only Eric's Franklin photos and `11 NOV 2026.docx`. I reviewed the commit directly.

## 3. Item table (FT47 R2 items + D3′/D4′)

| # | Item | Verdict | Evidence (at eb8bb7ce) |
|---|---|---|---|
| 1 | **`#/catalog` and `/catalog` go home** | **FIXED** | `main.dart:29-68` adds `resolveCatalogRoute`, which reads the `#` fragment (`:34-47`), including `#/catalog/<id>` and `#/catalog?item=<id>`. `main.dart:202-219` runs it before any auth or Firebase init and launches a separate `MaterialApp` with `home: CatalogBrowseScreen`, so it needs no login and has no auth redirect. Ordering: the known-path guard `:167-199` lets `/` (hash URLs) and `/catalog`, `/catalog/**` through (`:180-181`). The earlier wishlist and attorney checks (`:101-145`) cannot match a catalog URL. Hosting `firebase.json:74-79` rewrites `/catalog` and `/catalog/**` to `/index.html`, and `/` is served by `:114`. Logged-in and logged-out users get the same path, because the catalog branch runs before `AuthGate`. |
| 2 | **`version.json` git_commit == BUILT_SHA** | **PASS (enforced by script; confirm on preview)** | No `version.json` is committed in the tree, which is correct because a commit cannot contain its own SHA. `deploy_preview.ps1` handles it: `:33` resolves the SHA, `:79` creates `git worktree add --detach` at that SHA, and `:82-85` asserts worktree HEAD == SHA, so a dirty tree cannot leak in. `:89` runs `flutter build web --release` inside the worktree. `:97-100` writes `git_commit=$resolvedSha` (UTF-8 without BOM), and `:103-106` re-reads it and throws on mismatch. `:111` deploys from inside the worktree. `:145-148` reads back the served `$p7Url/version.json` and throws if it is not equal. `firebase.json:190-194` sets `version.json` to `no-cache, no-store`, so the readback is not stale. |
| 3 | **Wikimedia CSP** | **PASS, no weakening** | `firebase.json:284`: only `img-src` and `connect-src` gain `upload.wikimedia.org commons.wikimedia.org *.wikimedia.org images.metmuseum.org numismatics.org`. `script-src`, `default-src`, `frame-src`, `worker-src` and `style-src` are byte-identical to base. No `*` or new `unsafe-*` is added. `connect-src` is needed because Flutter web fetches images over XHR. The value matches plan §1.2 exactly. |
| 4 | **Multi-coin face values** | **FIXED** | `melt_value_service.dart:61-93` sets the set multiplier before the parenthesis strip at `:95`, and `:165` returns `value*count*setMultiplier`. A bare "set" with no count returns 0.0 (`:90-93`), which means no chip. Simulation over all 3,202 catalog rows: only **one** row contains "set": `NAC1.CN.US.1D.DIAMONDFLD.2026.XX.26XS.B` "Dollar (two-coin set)" → **$2.00**. No other catalog face value changes. The public card uses `parseFaceValue` only (`catalog_browse_screen.dart:1108`). |
| 5 | **Half-dime melt** | **FIXED** | `_ag90['half dime'] = 0.03617` (`:12`, 1.25 g × 0.900 ÷ 31.1035). `_matchDenom` checks half dime before nickel at `:285-288`. 35% war nickels go to `_ag35` 0.05626 (`:236-239`, `:243-245`). Cupro-nickel nickels have no "silver" text, so they return null, meaning no melt. Simulation over the catalog's 155 five-cent rows: "Half dime"/Silver → 0.03617, 35%-silver nickels → 0.05626, and cupro-nickel and blank-composition rows → no melt. **No five-cent row reaches the 0.77344 Morgan fallback.** The only catalog row that reaches the silver 0.77344 fallback is `NAC1.CN.US.CC.1MORGANDOL.1878.XX.BASE.5` (denomination "CC", 26.73 g), which really is a Morgan dollar, so the value is correct. At $51.51 spot: 0.03617 × 51.51 = **$1.86**. |
| 6a | **D3′ two-pass search (1842)** | **PASS** | `catalog_browse_screen.dart:120-189` (approx.) filters by type, era and photos first. Pass 1 is a whole-query substring match. Pass 2 runs only when Pass 1 is empty and requires every token. This matches plan §1.6 line for line. "1842 Liberty Seated dollar" resolves in Pass 1 to exactly one entry, so the existing 1842 widget test is unchanged. It is read-only and in-memory over the bundled asset, with no network calls or writes. |
| 6b | **D4′ post-deploy readback, preview prefix** | **PASS** | Script `:57-75` captures the live channel `releaseTime` before deploying. `:126-129` asserts it is unchanged after. `:133-140` requires a URL matching `^https://numista-vault--p7-gate-[a-z0-9]+\.web\.app`. `:145-148` reads back `version.json`. `:152-158` checks HTTP 200 on `/` and `/catalog`. The deploy command is only `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8` (`:111`), so it cannot touch live, Firestore rules, functions or the backend. `:43-45` refuses `c547b7a0`. `:38-41` requires Eric's exact `YES DEPLOY p7-gate <SHA> ROLLBACK=a3d7dca2…` string. |
| 7 | **No user-data writes / backend / auth / Stripe** | **PASS** | Diff names: no `numista_backend`, `firestore.rules`, `storage.rules`, `functions` or Stripe file. Only the NET-827 plan `.md` docs mention Stripe. `catalog_browse_screen.dart` has no Firestore, FirebaseAuth or HTTP calls; it loads `rootBundle` `assets/catalog/catalog_public_v1.json` (`:61`). No auth logic changed in `main.dart`. |
| 8 | **Tests meaningful (not tautological)** | **PASS (AG run unverified)** | `catalog_routing_test.dart` (new, 6 cases) calls the real `resolveCatalogRoute` used by `main.dart:202`, covering path, hash, hash+id, hash+`?item=`, and the negative case `#/claim`. Melt tests call the real `MeltValueService.compute('90% Silver','Half Dime',{Silver:51.51})` and expect `0.03617*51.51`. The F3 set tests and the line-139 pin (1.00 → 2.00) call the real `parseFaceValue`. The 1881 and 1816 widget tests pump the real `CatalogBrowseScreen(initialQuery:)` against the real asset, with finders scoped to `GridView`. AG reports `flutter analyze` 0 issues, routing 6/6, chunk1 9/9 and full suite 738/738. I did not re-run any of them. |

## 4. Must-Fix (Blocker / Major only)

**None.**

## 5. Deviations (a) and (b)

- **(a) Search tests moved into `catalog_chunk1_face_value_and_card_test.dart`, with the real 1881 and 1816 widget tests.** **Acceptable.** `test/catalog_browse_test.dart` is not in the diff, so it is untouched as the baton required. The new tests are at the end of the file, use `pumpLoadedCatalog`, set the surface to 1440×2400 with `addTearDown`, and scope card finders to `find.byType(GridView)`. They assert `'5 items'` plus the five exact card names, and `'0 items'` plus `'No matching catalog items found.'`. The existing 1842 test is unchanged. Small gap, not material: the 1816 case does not assert that the GridView is empty, as baton §3(a) asked. The `'0 items'` and placeholder text cover the same thing.
- **(b) Null/empty guard on the pre-deploy live `releaseTime`.** **Correct, and it hides nothing; it makes the script safer.** A diff of the script against plan §2.2 (lines 484–649) shows exactly two differences: the 4-line guard at `:70-73` and a UTF-8 BOM on line 1, which is harmless and helps PowerShell 5.1 read the file. The guard sits outside the `try` (`:77`) and runs before any worktree, build or deploy. It does `Pop-Location`, which balances the `Push-Location` at `:57`, and then `throw "FATAL: …"`, so a missing value stops the run loudly.
  - Without the guard, if the CLI returned no `releaseTime` for live, `$preLiveReleaseTime` would be `$null`. The post-deploy check at `:127` (`-ne $preLiveReleaseTime`) would then pass whenever the post value was also null. The "live unchanged" proof would quietly be meaningless.
  - The only cost is operational: if the Firebase CLI ever leaves out that field, the script refuses to deploy. That fails closed, and nothing reaches preview or live.

## 6. Non-gating notes (Minor / pre-existing; not Blocker or Major for this build)

1. **Same-tab hash edit (Minor, test-procedure note).** The catalog switch happens only at page load (`main.dart:98`, `:202`). If a tester is already on the app and only edits the address bar to add `#/catalog`, the browser does not reload, and `NumistaAIApp` has no `onGenerateRoute` for `/catalog`. The tester stays on home. Opening the URL in a new tab, pasting it fresh or reloading works. **Tell Field Tester to load the URL fresh or press reload.** Nothing in the app links to `#/catalog` internally, so real users are not affected.
2. **Pre-existing melt bug, not touched by this diff (raise as a separate ticket).** In `melt_value_service.dart:203`, `combined.contains('eagle')` sends any text containing "eagle" to the **gold** branch, including "Silver Eagle". A coin whose denomination or series says "Silver Eagle" would be priced at gold × 0.24188 oz instead of silver × 1 oz, roughly 19x too high. The same line is at `origin/main:136` and `a3d7dca2:168`, so it is already live and is **not a regression**. The collection screen calls `compute()` without `programSeries` (`my_collection_screen.dart:553`), and catalog Silver Eagles say just "Dollar". So the exposure is limited to user coins whose denomination text contains "eagle". It is display-only, with no charge and no data write. **It does not gate this preview.**
3. **`finally` cleanup can hide the first error (Minor).** In script `:162-169`, if `git worktree remove` throws inside `finally`, PowerShell shows that error instead of the original FATAL. The deploy is still blocked; only the log message is less clear.
4. **The script's route check is HTTP-only.** `:152-158` proves `/` and `/catalog` return 200. Status codes cannot show whether hash routing renders the catalog on the client, so Field Tester's visual check on `/#/catalog` and `/#/catalog/<id>` is still needed (baton §4 step 6).

## 7. Unknowns (only live or runtime can settle)

- The served `version.json` `git_commit` on p7-gate, which needs the deploy and Eric's `YES DEPLOY` line.
- Whether the Firebase CLI JSON includes `release.releaseTime` for the live channel. If it does not, the guard stops the run safely.
- The test pass counts are AG-reported and were not re-run by me.
- Whether the worktree build resolves the same Flutter and pub versions. `pubspec.lock` is tracked, so this is likely.

— Code Reviewer (Argon), read-only review, no edits/pushes/deploys.
