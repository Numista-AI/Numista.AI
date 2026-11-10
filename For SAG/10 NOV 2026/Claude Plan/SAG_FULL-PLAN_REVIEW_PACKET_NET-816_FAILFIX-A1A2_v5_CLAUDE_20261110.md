# SAG MANUAL FULL-PLAN REVIEW PACKET: NET-816 Catalog Chunk 1 Fail-Fix A1/A2, Plan v5 (writer: Claude)

Prepared 10 Nov 2026, about 4:20 PM ET (America/New_York), by GB CoS as a documentation-only packet preparer. This is a local file for Eric to upload by hand into a **fresh chat**. It is a **manual, fresh-chat SAG review**: nothing has been submitted anywhere, and no API was used.

## 1. What you are asked to do
- **Exact artifact under review:** A1, `PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v5_CLAUDE_20261110.md`, SHA-256 `0a7543aff8076f82ac66de1d5e4eb855a332272f326c453594162a368d123f52`, 26194 bytes, 401 lines. Line anchors (L#) refer to A1's own lines; line 1 is the first line after A1's BEGIN marker.
- **Review type:** a fresh, independent **FULL-PLAN** review of A1 as a whole. It is not a review of only the v4→v5 changes, and not a confirmation of the CoS score.
- **Pass bar:** PASS requires an explicit PASS, a score **≥95**, **and no critical or unresolved material finding**. A score ≥95 is not automatically a PASS, and a REVISE at any score is acceptable if you find a material defect. No outcome is expected.
- **Material defects only:** correctness, safety, permissions, execution. Cosmetic or wording points don't score. List them separately if at all; they are not grounds for REVISE.
- **A PASS grants no authority.** It grants no code, git, merge, deploy, Firestore, Stripe or go-live authority. A preview deploy would still need **Eric's new scoped typed YES naming the built fix commit SHA and the rollback target** (A1 §7.3). Your review is not a new plan attempt.

## 2. Status and honest distinctions
- **What the plan is:** NET-816 fixes two Code Reviewer findings in a Flutter web app on Firebase Hosting (A9):
  - **A1 (Blocker):** `/catalog` returns a 404 because there is no Hosting rewrite.
  - **A2 (Major):** a 90% silver half dime gets the Morgan dollar silver weight, about 10× too high on the collection dashboard.
- **Scope:** A1 is **PLAN ONLY**, covering exactly 3 files: `numista_mobile/firebase.json`, `lib/services/melt_value_service.dart`, and `test/catalog_chunk1_face_value_and_card_test.dart`.
- **A2 (CoS 100/100 PASS on v5)** is the designated CoS gate's score only. It is not a SAG score and does not bind you. Its four advisories are **unscored**; weigh them yourself.
- **History and counts:**
  - Track attempts 1–4 (writer AG CoS v5) scored 79, 87, 94 and 94, all REVISE.
  - v5 is **track attempt 5 of 10** and the first of 2 tries Eric allotted to writer Claude.
  - Founder's 4/10 rule: "New Rule, if someone is still failing after 4 tries, somebody else take over. If NO ONE gets it right by 10 total attempts, you notify me and we break it down into smaller bite-size chunks."
- **A3 (CoS v4 94 REVISE)** defines the three defects v5 must close:
  - **R1:** the rollback must not target `c547b7a0` (HOLD A10).
  - **R2:** the rollback block must be PowerShell with `$env:TEMP`, `Set-Location` first and stop-on-error.
  - **R3:** FT-4 must describe itself honestly.
- **A4 (v4 plan)** is a regression reference only.
- **CoS-verified facts, read-only, 10 Nov 2026** (you can't verify these yourself; treat them as CoS-stated):
  - **Repo state:** `numista_mobile` at branch tip `7fe4fae8` (`origin/p7-v8.9`, docs-only commit) is identical to `c547b7a0`.
  - **Source files A5–A8** are byte-exact at `c547b7a0`; their git blob ids match `git rev-parse c547b7a0:<path>`.
  - **Code blocks:** all 7 of v4's code blocks (the A1 rewrite, Changes 2.1–2.5 and the test block) are byte-identical in v5. Only the rollback block changed.
  - **`dart analyze`:** a scratch copy with those changes applied gives "No issues found", and the test block passes all 14 checks.
  - **Catalog simulation:** a Python port run on all 3,202 catalog rows shows no regressions.
  - **Rollback block:** the v5 PowerShell block was run in a scratch git repo on Windows PowerShell 5.1 with stubbed `flutter`/`firebase`. It completes on success; on a deploy failure it throws and its `finally` removes the worktree; it throws on the placeholder SHA and on `c547b7a0`. One edge case is A2 advisory 1: with stderr redirected (`2>&1`), git's informational stderr line trips `$ErrorActionPreference='Stop'` and the block fails closed.
  - **Firebase credentials:** the 11:40 AM ET preview attempt was blocked by expired credentials, and Eric's re-authentication is unconfirmed.
- **HOLD A10 (`74611e05`), decision section, quoted:**
  > 
  > ## Decision
  > The NET-816 preview-deploy baton `BATON_NET-816_AGCOS-V5_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1007.md` (SHA-256 `c65658e0e2783477e0d07b271dcf6cee1e5d939764ccd5ae4f257539e7fcdf0c`) is **HELD**.
  > 
  > It was **BLOCKED** at **11:40 AM ET** with Firebase/gcloud credentials expired, per AG file:
  > - `BLOCKED_BATON_NET-816_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1140.md`
  > - SHA-256 `67c5a39002c7cbee71c3c986fbd9b47a8df4fcc9b05f639bc472cb44464c47fe` (2245 B; found on day RADIO NET / BATONS / INBOX / OUTBOX; not seen in mailbox on this check)
  > 
  > **Do NOT re-issue or retry that preview deploy at `c547b7a0`.** That commit lacks the `/catalog` rewrite in `firebase.json` (**A1**), so /catalog would 404.
  > 
  > Re-issue the p7-gate preview deploy **only** at the **A1/A2-fixed commit**, after that fail-fix plan passes **CoS 95 + SAG 95 + Eric's typed YES**.
  > Eric's **10:06 AM ET YES** (card `t2455s9467`) covered **`c547b7a0` only**. The fixed commit needs his own **new scoped YES**.
  > 
- **HOLD A11 (`41b8bd5f`), summary:** go-live stays NOT ACTIVE regardless of Field Tester score. Do NOT fold to main, deploy live, or attach live Stripe keys. Every fix goes through CoS 95 + SAG 95 + Eric YES. `origin/main` stays `9f04550a45fa4da082ba8948c2d89a521a90fa45`.
- **Code Reviewer A1/A2, quoted from A9:**
> L16: | A1 | Blocker | numista_mobile/firebase.json (rewrites only /wishlist, /claim); main.dart ~133-180 | No /catalog rewrite, so numista.ai/catalog 404s; #/catalog also misses (no path URL strategy). | Catalog unreachable. No money/data impact. |
> L17: | A2 | Major | melt_value_service.dart:113 (half dime first), :192 (?? 0.77344), :238 (0.05 maps only to nickel) | 90% silver Half dime now falls to the Morgan dollar silver weight. | Dashboard value ~10x too high for those coins (max of AI vs melt). No data loss. |
> L90: | A1 | **Blocker** | `numista_mobile/firebase.json:49-132` (rewrites end at `/claim/**`). Route is `numista_mobile/lib/main.dart:133-134` and `:155-180`. | Hosting rewrites `/wishlist` and `/claim` to `index.html`. There is no `/catalog` or `/catalog/**` rewrite. The file’s own comment says unknown paths are a real HTTP 404 (`main.dart:99-114`). `CatalogBrowseScreen` is constructed only from that startup path check (`main.dart:178`). Nothing else in `lib/` navigates to it. `https://numista.ai/#/catalog` also misses: hash URLs have `uri.path == '/'` (`main.dart:113-114`), and there is no `usePathUrlStrategy` anywhere under `numista_mobile/`. | The public catalog URL does not open. No charge and no data write. The feature is unreachable on this Hosting config. | Add the same style of rewrite used for `/wishlist` (`firebase.json:114-120`): `/catalog` and `/catalog/**` → `/index.html`. Path URLs then hit the existing Dart branch. Hash URLs still will not. |
> L91: | A2 | **Major** | `numista_mobile/lib/services/melt_value_service.dart:111-112` (new order), `:189-191`, `:230-237`. Callers: `header_stats_bar.dart:108` and `:115`; `home_dashboard.dart:299-300`, `:380-387`. | This commit moves `half dime` ahead of `dime`, so face value is $0.05 (correct on the catalog card). `_matchDenom` maps face `0.05` only to a `nickel` table key. `_ag90` has dime / quarter / half / dollar and no nickel (`:11-16`). A 90% silver Half dime therefore takes the `?? 0.77344` dollar weight (the Morgan/Peace ounce on `:16`). Before this commit, `dime` matched first, so the same string used the dime weight `0.07234`. Dashboard value is `max(AI estimate, live melt)` (`home_dashboard.dart:387`). | Collection melt for a 90% silver Half dime is about 10× the previous dime-weight figure, and can replace a lower AI estimate as the shown value. Catalog cards themselves do not call `compute`. No Stripe charge. No coin documents are deleted. | Give face `0.05` on the 90% silver table a half-dime ounce, or stop using the dollar weight when the face value is a coin the table does not list. |

## 3. Areas to cover (whole plan)
1. **A1 fix correctness:** placement and effect of the `/catalog` and `/catalog/**` rewrites in A5, routing in A7 (path branch, hash fallthrough), and whether declaring `#/catalog` out of scope is honest.
2. **A2 fix correctness:** Changes 2.1–2.5 against A6, covering the half dime (0.03617 oz), 90%/40%/35% weights, the war-nickel route (0.05626 oz), the Morgan/Peace dollar fallback, null for unmodeled silver, and keyword guards.
3. **Tests:** the (a)–(e) expected values and whether the test compiles. The §6 gate and the FT-4 honesty and gaps in §5.1.
4. **R1:** the pre-deploy record of p7-gate, the RT-A/RT-B choice, the YES contents, never `c547b7a0`, and compliance with HOLD A10.
5. **R2:** whether the PowerShell rollback block is correct (paths, stop-on-error, native exit codes, `try/finally` cleanup, worktree isolation from the shared repo).
6. **Boundaries:** no checkout in the shared tree, the pinned deploy command `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8`, zero Firestore reads or writes, Stripe and the Christmas promo untouched, no live hosting or main, no secrets, and 3-file scope.
7. **Open questions in §9:** whether each is legitimate, and whether anything is presented as verified without support.

## 4. Requested output (concise)
1. An integer score out of 100 and an explicit disposition: **PASS** or **REVISE**.
2. Material or critical findings only, each with A1 line numbers or sections, why it is material, and the minimal fix (or "none").
3. Six one-line checks: (a) A1 rewrite and routing; (b) A2 melt logic and tests; (c) R1 rollback target and HOLD; (d) R2 PowerShell block; (e) FT-4 honesty and gaps; (f) execution boundary and no regression against v4.
4. Confirmation that you reviewed the full A1, with the **exact A1 SHA-256** you reviewed.

## 5. Byte-exact embedding and extraction rule
Each artifact sits between a line `<<<BEGIN ARTIFACT id=… sha256=… bytes=… lines=… path=…>>>` and a line `<<<END ARTIFACT id=…>>>`. The artifact's exact bytes begin right after the newline that ends the BEGIN line and run for exactly `bytes` bytes; the END line begins right after them, except that when an artifact does not end in a newline (A5–A8 here), exactly one separator LF that is NOT part of the artifact comes before the END line. No escaping or transformation was applied (UTF-8, LF). `lines` counts newline characters. There are exactly 11 artifacts. Paths are the preparer's box paths; A5–A8 are byte-exact copies of the `c547b7a0` blobs.

## 6. Manifest of embedded payloads
| ID | Role | Source path | SHA-256 | Bytes | Lines |
|---|---|---|---|---|---|
| A1 | Plan v5 (writer Claude) — EXACT ARTIFACT UNDER REVIEW | `/workspace/net816-failfix/src/PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v5_CLAUDE_20261110.md` | `0a7543aff8076f82ac66de1d5e4eb855a332272f326c453594162a368d123f52` | 26194 | 0 |
| A2 | CoS v5 score record: 100/100 PASS (CoS gate only; NOT SAG), with its four unscored advisories | `/workspace/net816-failfix/COS_SCORE_NET-816_FAILFIX-A1A2_v5_100_PASS_20261110.md` | `a19a799ca9cddac7af737c72381a2901f0cd14b7bab94f8beb0a2820f3ac20fa` | 9565 | 0 |
| A3 | CoS v4 score record: 94/100 REVISE (background; defines R1–R3) | `/workspace/net816-failfix/COS_SCORE_NET-816_FAILFIX-A1A2_v4_94_REVISE_20261110.md` | `dc67695493be76e5df1a1abec9a8fb2aac4a624d9111b9e637bde35d437a788b` | 10038 | 0 |
| A4 | Plan v4 (AG CoS v5) — regression reference only; NOT under review | `/workspace/net816-failfix/src/PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v4_AGCOS-V5_20261110.md` | `eed812708c6db9b307a1892eb29d79e21fbac3691005fd47fd9a9084bcbaeb1c` | 19947 | 1 |
| A5 | Source at c547b7a0: numista_mobile/firebase.json (git blob fd6ed208…) | `/workspace/net816-failfix/src/repo/firebase.json` | `6afc191159e3ec33246e3ed0da5f3b10254687d0a4c8b5b121a02a905a9b5f2c` | 7978 | 0 |
| A6 | Source at c547b7a0: numista_mobile/lib/services/melt_value_service.dart (git blob 8c2bd8f4…) | `/workspace/net816-failfix/src/repo/melt_value_service.dart` | `f9cde11702b280dbf9707ea3b695297f58c65b14ca18d2660408f5c847c325b4` | 12319 | 0 |
| A7 | Source at c547b7a0: numista_mobile/lib/main.dart (git blob e9053e3e…) | `/workspace/net816-failfix/src/repo/main.dart` | `cd6c6c5c166fec91cfc5fd67540aa35a5a7739a8374237bb33286fb8c1d71f26` | 18930 | 3 |
| A8 | Source at c547b7a0: numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart (git blob 23f9b854…) | `/workspace/net816-failfix/src/repo/catalog_chunk1_face_value_and_card_test.dart` | `6f08c560e2c2b3513be6100433b5bd5309eca570591cacef6b30993e6ba51da8` | 12421 | 0 |
| A9 | Code Reviewer go-live review (A1/A2 = NET-816 findings; B1–B5 are NET-827, out of scope) | `/workspace/net816-failfix/src/CODE_REVIEW_GO-LIVE_NET-816_NET-827_c547b7a0_20261110.md` | `3e2c16709736ab5a5cf834ed9aba9df66704465d7b86f24baf4cf56a0ad864ff` | 29493 | 0 |
| A10 | Preview HOLD 74611e05: no c547b7a0 preview deploy | `/workspace/net816-failfix/src/HOLD_NET-816_PREVIEW-DEPLOY_c547b7a0_NOT-REISSUED_AWAIT-A1A2-FIX_20261110-1148.md` | `74611e05e00a99e4dfb5f524f16a7dc92d540265986ff138c61ccf5884f11b6b` | 3208 | 0 |
| A11 | Go-live stop-rule HOLD 41b8bd5f and fail-fix plan order | `/workspace/net816-failfix/src/HOLD_NET-816_NET-827_AGCOS-V5_GO-LIVE-STOP-RULE_AND_FAILFIX-PLAN-ORDER_20261110-1113.md` | `41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d` | 3311 | 0 |

## A1: Plan v5 (writer Claude) — EXACT ARTIFACT UNDER REVIEW

<<<BEGIN ARTIFACT id=A1 sha256=0a7543aff8076f82ac66de1d5e4eb855a332272f326c453594162a368d123f52 bytes=26194 lines=401 path=/workspace/net816-failfix/src/PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v5_CLAUDE_20261110.md>>>
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
<<<END ARTIFACT id=A1>>>

## A2: CoS v5 score record: 100/100 PASS (CoS gate only; NOT SAG), with its four unscored advisories

<<<BEGIN ARTIFACT id=A2 sha256=a19a799ca9cddac7af737c72381a2901f0cd14b7bab94f8beb0a2820f3ac20fa bytes=9565 lines=69 path=/workspace/net816-failfix/COS_SCORE_NET-816_FAILFIX-A1A2_v5_100_PASS_20261110.md>>>
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
<<<END ARTIFACT id=A2>>>

## A3: CoS v4 score record: 94/100 REVISE (background; defines R1–R3)

<<<BEGIN ARTIFACT id=A3 sha256=dc67695493be76e5df1a1abec9a8fb2aac4a624d9111b9e637bde35d437a788b bytes=10038 lines=65 path=/workspace/net816-failfix/COS_SCORE_NET-816_FAILFIX-A1A2_v4_94_REVISE_20261110.md>>>
# DESIGNATED CoS PLAN SCORE: NET-816 Fail-Fix A1/A2 (AG CoS v5), plan v4

**Score: 94 / 100, REVISE** (pass mark 95; only material defects count: correctness, safety, permissions, execution. No points taken off for cosmetics.)
Scored by GB CoS (designated CoS gate), 10 Nov 2026, about 4:00 PM ET.
**Count: attempt 4 of 10 on the NET-816 fail-fix track; writer AG CoS v5's attempt 4 of 4, its final try.** Under Eric's 4/10 rule ("if someone is still failing after 4 tries, somebody else take over"), **a different writer must take attempt 5.** 6 of the 10 attempts remain; the Claude rule (attempts 9–10 go to Claude) is not yet triggered.

## Plan scored
- `BETA TEST\Grok Bot\8 OCT 26\BATONS\PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v4_AGCOS-V5_20261110.md`
- SHA-256 `eed812708c6db9b307a1892eb29d79e21fbac3691005fd47fd9a9084bcbaeb1c`, 19,947 bytes, 328 lines, last written 3:50:10 PM ET. This matches AG's report.
- All six routes are byte-identical (same SHA and size).

## Baseline and sources
- v3 record `COS_SCORE_NET-816_FAILFIX-A1A2_v3_94_REVISE_20261110.md`, SHA-256 `9d5b3549787cb04278b033ec9cfe819ffce83fa1d160bdc203ac9a0bc5a11aaf`.
- Code Reviewer review, SHA `3e2c1670…864ff`.
- HOLD/stop-rule order, SHA `41b8bd5f…778943d`.
- Preview HOLD `HOLD_NET-816_PREVIEW-DEPLOY_c547b7a0_NOT-REISSUED_AWAIT-A1A2-FIX_20261110-1148.md`, SHA `74611e05e00a99e4dfb5f524f16a7dc92d540265986ff138c61ccf5884f11b6b`.
- Repo checked read-only on EDS_Laptop:
  - `7fe4fae8` (3:51:57 PM ET, "docs(radio): file NET-816 fail-fix v4 plan…") is HEAD of `p7-v8.9` and equals `origin/p7-v8.9`. It adds 22 files, all under `BETA TEST/Grok Bot/8 OCT 26/{BATONS,INBOX,OUTBOX,RADIO NET}/` and `BETA TEST/Grok Bot/10 NOV 26/`. It only adds files, nothing under `numista_mobile`, so **it is docs only.**
  - `git diff c547b7a0 HEAD -- numista_mobile` is empty, and there are 0 dirty files, so **`numista_mobile` is unchanged from `c547b7a0`.**
  - `origin/main` = `9f04550a…`.
- Scratch only (`%TEMP%\cos_net816ff_ro\v4_check\`): `dart analyze` and `dart run` of the plan's test block against a scratch copy of `melt_value_service.dart` with v4 Changes 2.1–2.5 applied.
- Python port, v3 against v4, on all 3,202 catalog rows.

## v3 deduction closure map

| v3 | Status | Evidence |
|---|---|---|
| M1 rollback (shared-tree checkout; deploy form) | **Mostly closed** | The rule never to check out in `MyVertexProject` (line 300) and the separate worktree (line 305) are both right. The deploy command now matches the repo's pinned form exactly: `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8` (line 312). That's the same as the NET-816 preview baton (line 24) and DONE NET-772 (line 11), and it matches `numista_mobile/.firebaserc` default `studio-9101802118-8c9a8`. With no `--only`, it deploys the single hosting config (site `numista-vault`), which is a valid target. `--base-href "/"` matches CI (`ci-dev.yml:58`, `deploy-production.yml:59`).<br>**Build inputs are present in a clean worktree:** `firebase.json`, `.firebaserc`, `lib/firebase_options.dart` and `pubspec.lock` are all tracked. There is no root `firebase.json` that could be picked up by mistake. `flutter build` runs `pub get` itself. There is no `.env`, and the `String.fromEnvironment` URLs in `constants.dart:13–22` have production defaults. The only ignored files are `_checklists_source/*.pdf`, which `pubspec.yaml` doesn't reference. The existing `%TEMP%\p7gate_build_6ee3` worktree shows the same tracked-only pattern.<br>**`git worktree remove --force`** is safe: it deletes only that folder and its admin entry, and `--force` is needed because of the untracked `build/`.<br>New problems: **R1** and **R2** below. |
| M2 FT-4 zero-write | **Closed for zero-write, but the claim is inaccurate** | FT-4 is now a local `flutter test … --plain-name "half dime"` (line 268). The filter matches the new test name (it contains "half dime"), and the test is pure, with no Firebase. The 14 expectations pass in the Dart scratch run (the v4 test block is byte-identical to v3's). **$1.0851 = 0.03617 × $30** is correct, and it rounds to "$1.09". No fixture file needs to be created. The description is wrong, though (**R3**). |

## Deductions on v4 (each one is material)

| # | Pts | Area | Evidence | Defect |
|---|---|---|---|---|
| R1 | −3 | Permissions: rollback target | Plan lines 302–318 (rollback deploys `c547b7a0` to p7-gate, "Record deployed commit `c547b7a0`"). The same target has appeared since v2 and v3, and **this CoS missed it in the v2 and v3 scores.** | **The rollback deploys a commit that is under a standing CoS HOLD.** HOLD `74611e05…` (11:48 AM ET) says: "**Do NOT re-issue or retry that preview deploy at `c547b7a0`.** That commit lacks the `/catalog` rewrite (A1)." AG's own report says this HOLD "remain[s] in full force". `c547b7a0` was also **never on p7-gate**: its preview was BLOCKED at 11:40 AM ET (`BLOCKED_BATON_…20261110-1140.md`), so it isn't a "known-good" prior build. The plan names no authority for a rollback deploy. A rollback must restore whatever is **actually** on p7-gate before the fix deploy: record its version or commit, for example from `firebase hosting:channel:list`, or from the last DONE record, DONE NET-772 (4 Nov). Or it should say no redeploy, and Eric decides. Either way, the scoped YES must name the rollback target. |
| R2 | −2 | Safety / execution: shell syntax | Plan lines 303–316 (a block labeled `bash`, using `"%TEMP%\p7gate_rollback_c547"`, `cd C:\Users\…`) | The block only works in **cmd.exe**. In PowerShell, the shell AG uses on EDS_Laptop through its `.ps1` scripts, `%TEMP%` is **literal**. I confirmed this on the laptop: `"%TEMP%\p7gate_rollback_c547"` resolves to `<cwd>\%TEMP%\p7gate_rollback_c547`. Step 1 has no `cd` and must run inside the repo, so the "isolated" worktree would land **inside the shared `MyVertexProject` tree** as `MyVertexProject\%TEMP%\…`. The M1 rule exists to protect exactly that tree. A doc `git add -A` or the 18:00 auto-backup could then pick it up as an embedded repo. In bash, `cd C:\Users\…` also loses its backslashes. Use `$env:TEMP` or the absolute path `C:\Users\ericd\AppData\Local\Temp\p7gate_rollback_c547`, start with `Set-Location C:\Users\ericd\Documents\MyVertexProject`, label the block PowerShell, and stop on error, for example `$ErrorActionPreference='Stop'`. |
| R3 | −1 | Execution: Field Tester claim | Plan line 268 (FT-4 runs "against verified catalog Half Dime fixture (`assets/catalog/catalog_public_v1.json` row `NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2`) … confirming melt value for 1853 Half Dime resolves to **$1.0851**") | **The test never reads that file or that row.** It calls `compute` with literal strings (`'Silver (90%)'`, `'Half Dime'`). The real 1853 catalog row has `composition: null`, denomination `Half dime`, series `Seated Liberty Half Dime`. Run through v4 `compute`, it returns **null (N/A)**, not $1.0851, because there is no "silver" in its text. That's harmless for the catalog, since cards don't call `compute`. But the pass criterion claims a check that doesn't happen. The plan should state what the test proves and record the remaining gap: there is **no visual dashboard half-dime check on the preview**, because no zero-write half-dime account exists. FT-4 also repeats gate step 2 (line 276). The local test is acceptable as the A2 correctness proof, provided the plan says this honestly. |

**Total: 100 − 6 = 94, REVISE.**

## Required fixes for attempt 5 (new writer per the 4/10 rule; all small)
1. **R1:** Rollback target = the build actually on p7-gate before the fix deploy, recorded first. Or no redeploy, with Eric deciding. The scoped-YES text must name the rollback target. Remove "redeploy `c547b7a0`".
2. **R2:** Use a PowerShell block with `$env:TEMP` (or an absolute path), an explicit `Set-Location` into the repo first, and stop-on-error.
3. **R3:** Reword FT-4 to say it is a local unit-level A2 proof using literal inputs, not the catalog row. State that the preview dashboard visual check is deferred because no zero-write account exists.

Everything else in v4 is verified and can be reused as is: A1 rewrites, Changes 2.1–2.5, tests (a)–(e), FT-1 to FT-3, the gate, base and build identity, revert, the channel-delete rule, and scope.

## Regression scan
- **v3 to v4, catalog: 0 rows change.** Old to v4 is the same 328-row set as v3, with all improvements kept and no new regressions.
- Synthetic edge cases (advisories in v3) are now fixed:
  - "Silver / Dime / Wartime" now gives 0.07234 (v3 gave 0.05626).
  - "Quarter / Wartime" now gives 0.18084.
  - "5 Cents / Howard award" and "Edward" now give 0.03617.
  - "Silver, Copper, Manganese / 5 Cents / Jefferson" now gives 0.05626.
- Remaining advisory: the `war` substring still catches words like "Warren" at a 0.05 face value. That's hypothetical and not in the catalog.
- **The Dart scratch run reads "No issues found!" and 14 of 14 checks pass** on the v4-patched copy.

## Advisories (not scored)
- `firebase hosting:channel:deploy` without `--expires` resets the channel expiry to the CLI default; an earlier track used `--expires 30d`.
- Header line 2 says "Filed 15:55 EST"; the file was written at 3:50 PM ET.
- `7fe4fae8` also put `CODE_REVIEW_GO-LIVE…` and `UX_AUDIT_CHECKLIST…` (`10 NOV 26`), plus copies of this CoS's v3 score, into git. They are docs only, but note they are now in the repo history on `origin/p7-v8.9`.
- 404-page `/?route=Catalog` and the pre-existing catalog data issues carry over from v3.

## Authority statement
This score **grants no code, merge, deploy, Firestore, Stripe or go-live authority.** It is REVISE, so **no SAG packet was built** and nothing was copied to `For SAG`. Both HOLDs (`41b8bd5f…`, `74611e05…`) and the go-live stop rule stay in force. **AG CoS v5's writer attempts are used up (4 of 4).** Attempt 5 of 10 goes to a different writer, assigned by CoS/Eric; it is not self-assigned.
<<<END ARTIFACT id=A3>>>

## A4: Plan v4 (AG CoS v5) — regression reference only; NOT under review

<<<BEGIN ARTIFACT id=A4 sha256=eed812708c6db9b307a1892eb29d79e21fbac3691005fd47fd9a9084bcbaeb1c bytes=19947 lines=328 path=/workspace/net816-failfix/src/PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v4_AGCOS-V5_20261110.md>>>
# PLAN (v4) — NET-816 Catalog Chunk 1 Fail-Fix A1/A2 (AG CoS v5)
Filed: 2026-11-10 15:55 EST by AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
Target Track: NET-816 Catalog Chunk 1 v2.2 Fail-Fix (A1 Blocker & A2 Major).
In response to: `BATON_NET-816_AGCOS-V5_REVISE_FAILFIX-A1A2_v3-to-v4_CoS94_FINAL-WRITER-TRY_20261110-1524.md` & `COS_SCORE_NET-816_FAILFIX-A1A2_v3_94_REVISE_20261110.md` (CoS Score 94/100 REVISE).
Attempt: **Track attempt 4 of 10; AG CoS v5 attempt 4 of 4 (Final Writer Try)**.
Status: **STRICT PLAN ONLY — NO CODE, NO DEPLOYS, NO MERGES BEFORE GATED APPROVAL (CoS 95 + SAG 95 + Eric scoped typed YES)**.

---

## 1. Executive Summary & Defect Closure Matrix (M1 & M2)

Plan v4 preserves all verified defect closures from v1–v3 (D1–D6, N1–N5) and cleanly closes the two remaining material deductions (M1 and M2) from CoS Score 94:

| Defect | Area | Description in v3 | Resolution in v4 (§ reference) |
|---|---|---|---|
| **M1** | Safety / execution: rollback | Rollback used bare `git checkout c547b7a0` in shared `MyVertexProject` tree, risking deletion of 416 tracked governance files and leaving HEAD detached; deploy command dropped `--project` and used non-pinned syntax. | **Closed (§7.2):** Rollback strictly isolates build inside a temporary worktree (`git worktree add "%TEMP%\p7gate_rollback_c547" c547b7a0`). Shared workspace is never checked out. Uses pinned command: `flutter build web --release --base-href "/"` and `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8` on host machine (`EDS_Laptop`). Worktree removed after deployment. |
| **M2** | Execution: Field Tester | FT-4 attempted dashboard check using demo or non-existent fixtures, which could not show a half dime without unauthorized Firestore writes. | **Closed (§5 FT-4):** Selected CoS Score Option (b): replaced FT-4 with local read-only fixture check on the catalog half dime fixture (`NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2`) via `flutter test`, ensuring **zero live Firestore reads and zero Firestore writes**. |

---

## 2. Root Cause Analysis & Architectural Boundaries

### 2.1 A1 BLOCKER: Missing `/catalog` Firebase Hosting Rewrites & Scope Boundary on `#/catalog`
* **Locations:** `numista_mobile/firebase.json` lines 49–133 (`hosting.rewrites`), `numista_mobile/lib/main.dart` lines 113–181.
* **Server-Side Rewrites:**
  - Firebase Hosting uses explicit route rewrites rather than a blanket catch-all `**`.
  - While `/about`, `/pricing`, `/login`, etc., are explicitly rewritten to `/index.html`, `/catalog` and `/catalog/**` were omitted.
  - Adding `/catalog` and `/catalog/**` pointing to `/index.html` ensures direct browser requests and deep links return HTTP 200 with `/index.html`.
* **Client-Side Routing Architecture at `c547b7a0`:**
  - In `main.dart:115–118`, the entry-point route inspects `uri.path`.
  - Lines 154–181 check `if (normalizedPath == '/catalog' || path.startsWith('/catalog/'))` to launch `CatalogBrowseScreen`.
  - In single-page web apps, browsers never send the hash fragment (`#...`) to the server. A request for `https://numista.ai/#/catalog` arrives at Firebase Hosting with `path == '/'`, which rewrites to `/index.html`.
  - In `main.dart:113–114`, the codebase explicitly documents:
    `// Hash-fragment URLs (e.g. /#/claim?...) have uri.path == '/' — they pass through to the normal app flow correctly.`
  - Therefore, `/#/catalog` evaluates `uri.path == '/'`, skipping line 155 and falling through to the Front Door / Login / Home flow.
* **Scope Boundary (N1 Resolution):**
  - Canonical public catalog access for Numista.AI is **path-based** (`/catalog` and `/catalog/<nac>`).
  - Modifying `main.dart` to inspect `uri.fragment` is explicitly **OUT OF SCOPE** for this fail-fix track to strictly maintain the 3-file surgical scope (`firebase.json`, `melt_value_service.dart`, `catalog_chunk1_face_value_and_card_test.dart`) and avoid unintended side-effects on existing front-door hash routing.
  - Field Tester check FT-3 validates that `/#/catalog` returns HTTP 200 and loads the normal front-door flow cleanly without a 404 or crash.

### 2.2 A2 MAJOR & N4: Sub-Dollar Silver, War Nickel, and Half Dime Melt Logic
* **Locations:** `numista_mobile/lib/services/melt_value_service.dart` lines 11–17 (`_ag90`), 24–26 (`_ag35`), 189–202 (`compute()`), 230–238 (`_matchDenom`).
* **Root Causes:**
  1. `_ag90` table lacked `'half dime'`.
  2. `_matchDenom` only checked `'nickel'` for face value $0.05.
  3. Fallback `?? 0.77344` forced all unrecognized 90% silver coins to Morgan dollar weight.
  4. Line 201 `if (ag > 0) return ag * 0.77344 * count;` acted as an unconditional Morgan fallback for any coin containing "silver" without the "90%" keyword.
* **Fix Strategy:**
  - Route $0.05 silver coins containing `nickel`, `war`, or `wartime` in the combined text to `_ag35` (0.05626 oz).
  - Route other $0.05 silver coins (half dimes) to `_ag90['half dime']` (0.03617 oz).
  - Sub-dollar silver dimes, quarters, and halves resolve to their exact standard weights.
  - Morgan/Peace dollars (even with empty denom or denom "CC" with series "1$-Morgan dollar") safely resolve to 0.77344 oz.
  - Unmodeled silver tokens return `null` and never receive a Morgan weight.

---

## 3. Scope of Modifications (Strictly 3 Files)

This fail-fix track is strictly confined to 3 files:
1. `numista_mobile/firebase.json` (Hosting rewrites for `/catalog` and `/catalog/**`)
2. `numista_mobile/lib/services/melt_value_service.dart` (Melt valuation corrections)
3. `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart` (Unit and regression tests)

Zero modifications to `main.dart`, backend services, or database schemas.

---

## 4. Surgical Code Modification Specification (PLAN ONLY)

### File 1: `numista_mobile/firebase.json`
**Location:** Inside `hosting.rewrites` array (immediately following line 72 `/terms` rewrite, preceding line 73 `/about`):
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
* **Effect:** Direct HTTP GET requests to `/catalog` and deep links like `/catalog/<nac_code>` return HTTP 200 with `/index.html`, allowing `main.dart` to mount `CatalogBrowseScreen`.

---

### File 2: `numista_mobile/lib/services/melt_value_service.dart`

#### Change 2.1: Add `'half dime'` to `_ag90` table (lines 11–17)
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
Tightened to check face value $0.05 when matching war/wartime keywords:
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
Replace `if (ag > 0) return ag * 0.77344 * count;` with denomination-aware lookup routing war nickels and standard denominations correctly:
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

---

### File 3: `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`
**Location:** Inside `main()`, group `'NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1 & NET-837 #2/#4/#5)'`:
Add the following comprehensive regression test suite (14/14 expectations verified clean with zero Dart compile errors):
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

## 5. Bounded Field Tester Check (p7-gate Preview) (N1, N5, M2 Resolution)

Following build and deploy to the preview channel `p7-gate`, the Field Tester will execute the following 4 bounded checks with explicit PASS/FAIL rules:

| Check # | Target URL / Flow | Test Procedure | PASS Criteria | FAIL Criteria |
|---|---|---|---|---|
| **FT-1** | Direct GET `/catalog` | Open `https://numista-vault--p7-gate-<hash>.web.app/catalog` in a clean browser session. | HTTP 200 returned. Page mounts Flutter SPA, displays "Public Coin Catalog" header, search input, type-photo cards, and face value chips. | HTTP 404, blank page, or Firebase Hosting "Page Not Found". |
| **FT-2** | Direct GET `/catalog/<nac>` | Open `https://numista-vault--p7-gate-<hash>.web.app/catalog/NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2` (Real catalog NAC code for 1853 Seated Liberty Half Dime). | HTTP 200 returned. Deep link mounts directly into catalog item view for the 1853 Half Dime. Zero 404 errors. | HTTP 404, infinite spinner, or router exception screen. |
| **FT-3** | Direct GET `#/catalog` | Open `https://numista-vault--p7-gate-<hash>.web.app/#/catalog` in a clean browser session. | HTTP 200 returned (via `/` rewrite). App mounts cleanly into front-door / login / home flow (as documented in `main.dart:113-114`) without crash or 404. | HTTP 404, blank screen, crash, or redirection loop. |
| **FT-4** | Local Read-Only Fixture Verification (M2 Option b) | Execute local machine-checkable test command against verified catalog Half Dime fixture (`assets/catalog/catalog_public_v1.json` row `NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2`):<br>`cd numista_mobile && flutter test test/catalog_chunk1_face_value_and_card_test.dart --plain-name "half dime"` | Exit code 0 returned. 14 of 14 checks pass, confirming melt value for 1853 Half Dime resolves to **$1.0851** (~**$1.09** at $30/oz Ag) and NEVER **$23.20**. **Zero live Firestore reads and zero Firestore writes.** | Non-zero exit code, test failure, or melt value evaluated as $23.20. |

---

## 6. Machine-Checkable Verification Gate

Upon receiving gated authorization (CoS 95 + SAG 95 + Eric scoped typed YES):
1. `cd numista_mobile`
2. `flutter test test/catalog_chunk1_face_value_and_card_test.dart` (Must exit code 0; all existing and new tests pass).
3. `flutter analyze lib/services/melt_value_service.dart test/catalog_chunk1_face_value_and_card_test.dart` (Must exit code 0 with 0 issues).
4. `python -c "import json; d = json.load(open('firebase.json')); rewrites = [r.get('source') for r in d['hosting']['rewrites']]; assert '/catalog' in rewrites, 'missing /catalog'; assert '/catalog/**' in rewrites, 'missing /catalog/**'; print('firebase.json rewrites VERIFIED')"` (Must exit code 0).

---

## 7. Base Commit, Build Identity & Rollback Procedures (M1 Resolution)

### 7.1 Base Commit & Branch Identity
* **Base Branch:** `p7-v8.9`
* **Base Source Commit:** `c547b7a0` (Working tree source files in `numista_mobile/` are clean and identical to `c547b7a0`).
* **Built Commit Identity Requirement:**
  - Upon applying the surgical changes, a git commit will be created on `p7-v8.9`:
    `git commit -m "fix(catalog): add /catalog rewrites and correct half-dime melt value (NET-816 A1/A2)"`
  - The exact resulting commit SHA **MUST** be explicitly recorded in the `DONE_BATON_...` report.
  - Preview deploy to channel `p7-gate` will only proceed once Founder Eric provides a new scoped typed `YES` explicitly naming that built commit SHA.

### 7.2 Rollback Procedures (M1 Safety Resolution)
1. **Source Code Rollback:**
   - If unit tests fail before commit:
     `git checkout c547b7a0 -- numista_mobile/firebase.json numista_mobile/lib/services/melt_value_service.dart numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`
   - If already committed:
     `git revert --no-edit <built_commit_sha>` and push to `origin/p7-v8.9`.
2. **Hosting Channel `p7-gate` Rollback:**
   - **M1 CRITICAL SAFETY RULE:** **NEVER** run `git checkout c547b7a0` in the shared `MyVertexProject` workspace (which would delete 416 tracked governance files and detach HEAD).
   - **Isolated Worktree Rollback:**
     All rollback builds must execute in a dedicated, isolated temporary git worktree on the host machine (`EDS_Laptop`):
     ```bash
     # 1. Create isolated temporary worktree pinned to c547b7a0
     git worktree add "%TEMP%\p7gate_rollback_c547" c547b7a0

     # 2. Build release bundle with pinned base-href
     cd "%TEMP%\p7gate_rollback_c547\numista_mobile"
     flutter build web --release --base-href "/"

     # 3. Deploy to p7-gate using pinned project flag
     firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8

     # 4. Return to main workspace and cleanly delete temporary worktree
     cd C:\Users\ericd\Documents\MyVertexProject
     git worktree remove "%TEMP%\p7gate_rollback_c547" --force
     ```
   - Record deployed commit `c547b7a0` in the audit log.
   - **Channel Teardown Boundary:** Deleting the preview channel (`firebase hosting:channel:delete p7-gate -f`) is **STRICTLY PROHIBITED** without explicit prior typed `YES` from Founder Eric.

---

## 8. Invariant Protection & Scope Boundaries

1. **Strict PLAN ONLY:** Zero code files modified, zero git commits created, zero deploys executed prior to plan gate passage (CoS 95 + SAG 95 + Eric scoped typed YES).
2. **Pinned Repository Roots:** `origin/main` (`9f04550a45fa4da082ba8948c2d89a521a90fa45`) remains strictly pinned. Zero pushes or merges to `main`.
3. **Protected Infrastructure:** Live hosting (`numista.ai`), Cloud Firestore, and Stripe live mode remain strictly **OFF / UNTOUCHED**.
4. **Scope Isolation:** Changes are strictly confined to the 3 named files.
<<<END ARTIFACT id=A4>>>

## A5: Source at c547b7a0: numista_mobile/firebase.json (git blob fd6ed208…)

<<<BEGIN ARTIFACT id=A5 sha256=6afc191159e3ec33246e3ed0da5f3b10254687d0a4c8b5b121a02a905a9b5f2c bytes=7978 lines=302 path=/workspace/net816-failfix/src/repo/firebase.json>>>
{
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "hosting": {
    "site": "numista-vault",
    "public": "build/web",
    "trailingSlash": false,
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],

    "redirects": [
      {
        "source": "https://www.numista.ai/**",
        "destination": "https://numista.ai/:splat",
        "type": 301
      },
      {
        "source": "/app",
        "destination": "/",
        "type": 301
      },
      {
        "source": "/blog",
        "destination": "/about",
        "type": 301
      },
      {
        "source": "/signin",
        "destination": "/login",
        "type": 301
      },
      {
        "source": "/forgot",
        "destination": "/reset-password",
        "type": 301
      },
      {
        "source": "/reset",
        "destination": "/reset-password",
        "type": 301
      }
    ],

    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "numista-backend",
          "region": "us-central1"
        }
      },
      {
        "source": "/add_coins.html",
        "destination": "/add_coins.html"
      },
      {
        "source": "/scraper_dashboard.html",
        "destination": "/scraper_dashboard.html"
      },
      {
        "source": "/privacy",
        "destination": "/privacy.html"
      },
      {
        "source": "/terms",
        "destination": "/terms.html"
      },
      {
        "source": "/about",
        "destination": "/index.html"
      },
      {
        "source": "/pricing",
        "destination": "/index.html"
      },
      {
        "source": "/features",
        "destination": "/index.html"
      },
      {
        "source": "/faq",
        "destination": "/index.html"
      },
      {
        "source": "/login",
        "destination": "/index.html"
      },
      {
        "source": "/reset-password",
        "destination": "/index.html"
      },
      {
        "source": "/signup",
        "destination": "/index.html"
      },
      {
        "source": "/demo",
        "destination": "/index.html"
      },
      {
        "source": "/",
        "destination": "/index.html"
      },
      {
        "source": "/index.html",
        "destination": "/index.html"
      },
      {
        "source": "/wishlist",
        "destination": "/index.html"
      },
      {
        "source": "/wishlist/**",
        "destination": "/index.html"
      },
      {
        "source": "/attorney_portal",
        "destination": "/index.html"
      },
      {
        "source": "/claim",
        "destination": "/index.html"
      },
      {
        "source": "/claim/**",
        "destination": "/index.html"
      }
    ],

    "headers": [
      {
        "source": "**/*.@(js|css|wasm)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=31536000, immutable"
          }
        ]
      },
      {
        "source": "/index.html",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "/",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "/flutter_service_worker.js",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "/flutter_bootstrap.js",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "/version.json",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "/main.dart.js",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache, no-store, must-revalidate"
          }
        ]
      },
      {
        "source": "**/*.@(png|jpg|jpeg|gif|svg|ico|webp)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=86400"
          }
        ]
      },
      {
        "source": "/manifest.json",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=3600"
          },
          {
            "key": "Content-Type",
            "value": "application/manifest+json"
          }
        ]
      },
      {
        "source": "/robots.txt",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=86400"
          },
          {
            "key": "Content-Type",
            "value": "text/plain; charset=utf-8"
          }
        ]
      },
      {
        "source": "/sitemap.xml",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=86400"
          },
          {
            "key": "Content-Type",
            "value": "application/xml; charset=utf-8"
          }
        ]
      },
      {
        "source": "**",
        "headers": [
          {
            "key": "X-Frame-Options",
            "value": "SAMEORIGIN"
          },
          {
            "key": "X-Content-Type-Options",
            "value": "nosniff"
          },
          {
            "key": "Referrer-Policy",
            "value": "strict-origin-when-cross-origin"
          },
          {
            "key": "Permissions-Policy",
            "value": "camera=(self), microphone=(), geolocation=(), payment=()"
          },
          {
            "key": "Strict-Transport-Security",
            "value": "max-age=63072000; includeSubDomains; preload"
          },
          {
            "key": "X-DNS-Prefetch-Control",
            "value": "on"
          },
          {
            "key": "Content-Security-Policy",
            "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
          }
        ]
      }
    ]
  },
  "flutter": {
    "platforms": {
      "android": {
        "default": {
          "projectId": "studio-9101802118-8c9a8",
          "appId": "1:568985927038:android:efb96a51420403078b072f",
          "fileOutput": "android/app/google-services.json"
        }
      },
      "dart": {
        "lib/firebase_options.dart": {
          "projectId": "studio-9101802118-8c9a8",
          "configurations": {
            "android": "1:568985927038:android:efb96a51420403078b072f",
            "web": "1:568985927038:web:9ea56548eed27d5a8b072f",
            "windows": "1:568985927038:web:14e303f30991f9e78b072f"
          }
        }
      }
    }
  }
}
<<<END ARTIFACT id=A5>>>

## A6: Source at c547b7a0: numista_mobile/lib/services/melt_value_service.dart (git blob 8c2bd8f4…)

<<<BEGIN ARTIFACT id=A6 sha256=f9cde11702b280dbf9707ea3b695297f58c65b14ca18d2660408f5c847c325b4 bytes=12319 lines=239 path=/workspace/net816-failfix/src/repo/melt_value_service.dart>>>
// melt_value_service.dart
//
// Standardized Valuation Service for Numista.AI
// Calculates real-time face value and melt value for coins:
//   - Field precedence: Uses explicit numeric fields (denomination_numeric, troy_oz_pure_metal) when available
//   - Fallback normalization: Normalizes truncated/dirty strings ("Five Dollars (Hal..." -> $5.00)
//   - Spot price resilience: Live spot prices with cached fallback and offline indicator support

class MeltValueService {
  // ── Silver (Ag) troy oz per coin by denomination ───────────────────────────
  static const _ag90 = {
    'dime':        0.07234,   // 2.5g × 90% = 2.25g Ag ÷ 31.1035
    'quarter':     0.18084,   // 6.25g × 90% = 5.625g Ag ÷ 31.1035
    'half':        0.36169,   // 12.5g × 90% = 11.25g Ag ÷ 31.1035
    'half dollar': 0.36169,
    'dollar':      0.77344,   // Morgan / Peace: 26.73g × 90% ÷ 31.1035
  };

  static const _ag40 = {
    'half':        0.14792,
    'half dollar': 0.14792,
  };

  static const _ag35 = {
    'nickel': 0.05626,
  };

  static const double _silverEagleOz = 1.0;

  // ── Gold (Au) troy oz per coin by face value ───────────────────────────────
  static final _au90ByFaceValue = {
    1.0:  0.04837,   // $1 gold piece
    2.5:  0.12094,   // Quarter Eagle
    3.0:  0.14513,   // $3 gold piece
    5.0:  0.24188,   // Half Eagle
    10.0: 0.48375,   // Eagle
    20.0: 0.96750,   // Double Eagle
  };

  static final _au9167ByFaceValue = {
    5.0:  0.10,
    10.0: 0.25,
    25.0: 0.50,
    50.0: 1.00,
  };

  static const double _buffaloAuOz = 1.0;

  // ── Unified Face Value Parser ──────────────────────────────────────────────
  /// Parses denomination string to numerical USD value.
  /// Pre-processes dirty strings by stripping parenthetical notes and ellipses.
  /// Evaluates multi-word terms before generic single tokens.
  static double parseFaceValue(String rawDenom, {int qty = 1}) {
    final count = qty > 0 ? qty : 1;
    if (rawDenom.trim().isEmpty) return 0.0;

    // Normalization pipeline: lowercase, collapse whitespace, strip parenthetical & ellipses
    String s = rawDenom.toLowerCase().trim();
    s = s.replaceAll(RegExp(r'\(.*?\)'), '').trim();
    s = s.replaceAll(RegExp(r'\.{2,}'), '').trim();
    s = s.replaceAll('\u00bd', ' 1/2');
    s = s.replaceAll(RegExp(r'\s+'), ' ').trim();

    // Guard non-legal-tender blanks (planchets), non-USD units (candareens),
    // and multi-denomination sets/ranges ('$100/$50/$25/$10', '$1, $2, $5, $10', '3c-50c')
    if (s.contains('planchet') ||
        s.contains('candareen') ||
        RegExp(r'\$\d[\d,]*(?:\.\d+)?\s*(?:/\s*\$?|,\s*\$)\s*\d').hasMatch(s) ||
        RegExp(r'\d\s*(?:\u00a2|c|cents?)?\s*[\u2013\-]\s*\d').hasMatch(s)) {
      return 0.0;
    }

    double value = 0.0;

    // 0. Leading numeric & fractional patterns (N Dollars, 1,000 Dollars, 10,000 Dollars, 2 1/2 Dollars, G$2 1/2, 3 cents, $1000)
    final fracDollarMatch = RegExp(r'^(?:g?\$)?\s*(\d+)\s+1/2(?:\s*dollars?)?$').firstMatch(s);
    final leadDollarMatch = RegExp(r'^\$?\s*(\d[\d,]*(?:\.\d+)?)\s*(?:dollars?|\$)$').firstMatch(s);
    final leadCentMatch = RegExp(r'^(\d+(?:\.\d+)?)\s*(?:cents?|c|\u00a2)\b').firstMatch(s);
    final leadSymDollarMatch = RegExp(r'^\$\s*(\d[\d,]*(?:\.\d+)?)(?:\b|$)').firstMatch(s);

    if (fracDollarMatch != null) {
      value = (double.tryParse(fracDollarMatch.group(1)!) ?? 0.0) + 0.5;
    } else if (leadDollarMatch != null) {
      value = double.tryParse(leadDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
    } else if (leadCentMatch != null) {
      value = (double.tryParse(leadCentMatch.group(1)!) ?? 0.0) / 100.0;
    } else if (leadSymDollarMatch != null) {
      value = double.tryParse(leadSymDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
    }

    // 1. High Gold, Notes & Commemoratives
    else if (s.contains(r'$10,000') || s.contains(r'$10000') || s.contains('ten thousand dollar')) { value = 10000.00; }
    else if (s.contains(r'$1,000') || s.contains(r'$1000') || s.contains('one thousand dollar') || s.contains('thousand dollar')) { value = 1000.00; }
    else if (s.contains(r'$500') || s.contains('five hundred dollar')) { value = 500.00; }
    else if (s.contains(r'$100') || s.contains('one hundred dollar') || s.contains('hundred dollar')) { value = 100.00; }
    else if (s.contains(r'$50') || s.contains('fifty dollar')) { value = 50.00; }
    else if (s.contains(r'$40') || s.contains('forty dollar')) { value = 40.00; }
    else if (s.contains(r'$25') || s.contains('twenty five dollar') || s.contains('twenty-five dollar')) { value = 25.00; }
    else if (s.contains(r'$20') || s.contains('twenty dollar') || s.contains('double eagle')) { value = 20.00; }
    else if (s.contains(r'$10') || s.contains('ten dollar') || (s.contains('eagle') && !s.contains('half') && !s.contains('quarter') && !s.contains('silver'))) { value = 10.00; }
    else if (s.contains(r'$5') || s.contains('five dollar') || s.contains('half eagle')) { value = 5.00; }
    else if (s.contains(r'$4') || s.contains('four dollar') || s.contains('stella')) { value = 4.00; }
    else if (s.contains(r'$3') || s.contains('three dollar')) { value = 3.00; }
    else if (s.contains(r'$2.50') || s.contains(r'$2.5') || s.contains('2 1/2') || s.contains('quarter eagle') || s.contains('two and a half')) { value = 2.50; }
    else if (s.contains(r'$2') || s.contains('two dollar')) { value = 2.00; }

    // 2. Sub-Dollar & Standard Silver/Base Denominations (multi-word terms before single tokens)
    else if (s.contains('half dollar') || s.contains('fifty cent') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
    else if (s.contains('quarter dollar') || s.contains('twenty-five cent') || s.contains('twenty five cent') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
    else if (s.contains('twenty cent') || s.contains('20c') || s.contains('20 cent')) { value = 0.20; }
    else if (s.contains('half dime') || s.contains('half-dime')) { value = 0.05; }
    else if (s.contains('dime') || s.contains('ten cent') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
    else if (s.contains('three cent') || s.contains('3 cent') || s.contains('3c')) { value = 0.03; }
    else if (s.contains('nickel') || s.contains('five cent') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
    else if (s.contains('two cent') || s.contains('2 cent') || s.contains('2c')) { value = 0.02; }
    else if (s.contains('half cent') || s.contains('half-cent')) { value = 0.005; }
    else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
    else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }

    // 3. Fallback: plain numeric parse
    else {
      final match = RegExp(r'\d+(?:\.\d+)?').firstMatch(s);
      if (match != null) {
        final parsed = double.tryParse(match.group(0)!) ?? 0.0;
        value = parsed <= 1000.0 ? parsed : 0.0;
      }
    }

    return value * count;
  }

  // ── Public Melt Value Calculation API ──────────────────────────────────────
  /// Returns melt value in USD, or null for base-metal / non-precious coins.
  static double? compute({
    required String metalContent,
    required String denomination,
    required Map<String, double> spotPrices,
    String programSeries = '',
    String themeSubject = '',
    int qty = 1,
    Map<String, dynamic>? coinData,
  }) {
    final count = qty > 0 ? qty : 1;
    final ag = spotPrices['Silver'] ?? 0.0;
    final au = spotPrices['Gold']   ?? 0.0;

    if (ag == 0.0 && au == 0.0) return null;

    // Field Precedence: Check if backend numeric troy oz field is present
    if (coinData != null) {
      final ozNum = (coinData['troy_oz_pure_metal'] as num?)?.toDouble();
      final isGold = coinData['is_gold'] == true;
      final isSilver = coinData['is_silver'] == true;
      if (ozNum != null && ozNum > 0.0) {
        if (isGold && au > 0) return au * ozNum * count;
        if (isSilver && ag > 0) return ag * ozNum * count;
      }
    }

    final mc     = metalContent.trim().toLowerCase();
    final denom  = denomination.trim().toLowerCase();
    final series = programSeries.trim().toLowerCase();
    final theme  = themeSubject.trim().toLowerCase();
    final combined = '$mc $denom $series $theme';

    // ── Gold Detection ──────────────────────────────────────────────────────
    if (combined.contains('gold') || combined.contains('half eagle') || combined.contains('eagle') || combined.contains('double eagle')) {
      if (combined.contains('99.99') || combined.contains('buffalo')) {
        return au * _buffaloAuOz * count;
      }
      if (combined.contains('91.67') || combined.contains('gold eagle')) {
        final fv = parseFaceValue(denom);
        final oz = _au9167ByFaceValue[fv] ?? 1.0;
        return au * oz * count;
      }
      if (combined.contains('90%') || combined.contains('half eagle') || combined.contains('indian head gold') || combined.contains('pre-1933') || combined.contains('saint-gaudens') || combined.contains('liberty head')) {
        final fv = parseFaceValue(denom);
        final oz = _au90ByFaceValue[fv] ?? 0.24188;
        return au * oz * count;
      }
      if (au > 0) return au * 0.24188 * count;
    }

    // ── Silver Detection ────────────────────────────────────────────────────
    if (combined.contains('silver') || combined.contains('silver eagle') || combined.contains('peace dollar') || combined.contains('morgan')) {
      if (combined.contains('silver eagle') || combined.contains('99.9') || combined.contains('.999') || combined.contains('fine silver')) {
        return ag * _silverEagleOz * count;
      }
      if (combined.contains('90%') || combined.contains('morgan') || combined.contains('peace') || combined.contains('barber') || combined.contains('walking liberty') || combined.contains('standing liberty') || combined.contains('mercury')) {
        final oz = _matchDenom(_ag90, denom) ?? 0.77344;
        return ag * oz * count;
      }
      if (combined.contains('40%')) {
        final oz = _matchDenom(_ag40, denom) ?? 0.14792;
        return ag * oz * count;
      }
      if (combined.contains('35%') || combined.contains('war nickel')) {
        final oz = _matchDenom(_ag35, denom) ?? 0.05626;
        return ag * oz * count;
      }
      if (ag > 0) return ag * 0.77344 * count;
    }

    return null;
  }

  /// Formatted melt value string. Returns 'N/A' for non-precious coins.
  static String format({
    required String metalContent,
    required String denomination,
    required Map<String, double> spotPrices,
    String programSeries = '',
    String themeSubject = '',
    int qty = 1,
    Map<String, dynamic>? coinData,
  }) {
    final v = compute(
      metalContent: metalContent,
      denomination: denomination,
      spotPrices: spotPrices,
      programSeries: programSeries,
      themeSubject: themeSubject,
      qty: qty,
      coinData: coinData,
    );
    if (v == null) return 'N/A';
    return '\$${v.toStringAsFixed(2)}';
  }

  static double? _matchDenom(Map<String, double> table, String rawDenom) {
    final fv = parseFaceValue(rawDenom);
    if (fv == 1.00 && table.containsKey('dollar')) return table['dollar'];
    if (fv == 0.50 && table.containsKey('half')) return table['half'];
    if (fv == 0.25 && table.containsKey('quarter')) return table['quarter'];
    if (fv == 0.10 && table.containsKey('dime')) return table['dime'];
    if (fv == 0.05 && table.containsKey('nickel')) return table['nickel'];
    return null;
  }
}
<<<END ARTIFACT id=A6>>>

## A7: Source at c547b7a0: numista_mobile/lib/main.dart (git blob e9053e3e…)

<<<BEGIN ARTIFACT id=A7 sha256=cd6c6c5c166fec91cfc5fd67540aa35a5a7739a8374237bb33286fb8c1d71f26 bytes=18930 lines=487 path=/workspace/net816-failfix/src/repo/main.dart>>>
import 'dart:async';
import 'dart:ui';
import 'package:flutter/foundation.dart' show kIsWeb, kDebugMode, debugPrint;
import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'screens/welcome_screen.dart';
import 'screens/attorney_portal_screen.dart';
import 'screens/not_found_screen.dart';
import 'screens/public_wishlist_view_screen.dart';
import 'screens/catalog/catalog_browse_screen.dart';
import 'services/theme_provider.dart';
import 'widgets/morgan_feedback_drawer.dart';
import 'services/guest_seed_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'widgets/auth_gate.dart';
import 'constants.dart';  // ITEM 10: kApiBaseUrl startup guard
import 'package:google_fonts/google_fonts.dart';
import 'utils/numista_error_helper.dart';


Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('Uncaught platform error: $error\n$stack');
    return true; // handled
  };

  FlutterError.onError = (FlutterErrorDetails details) {
    debugPrint('FlutterError: ${details.exceptionAsString()}\n${details.stack}');
  };

  // Enable Flutter accessibility semantics on web so that Playwright
  // text= / aria-label locators can find flt-semantics nodes.
  // SemanticsBinding.instance is a no-op on non-web platforms.
  if (kIsWeb) {
    SemanticsBinding.instance.ensureSemantics();
  }

  ErrorWidget.builder = (FlutterErrorDetails details) {
    // Log full details to console in debug only — never to UI
    if (kDebugMode) {
      debugPrint('UI Error: ${details.exception}\n${details.stack}');
      FlutterError.dumpErrorToConsole(details);
    }
    return const _ErrorFallbackWidget();
  };

  final uri = Uri.base;

  // ── Public Wishlist deep-link detection ──────────────────────────────────
  final isPublicWishlist = uri.path.contains('/wishlist/') ||
      (uri.pathSegments.isNotEmpty && uri.pathSegments.first == 'wishlist') ||
      uri.queryParameters.containsKey('wishlist');
  if (isPublicWishlist) {
    String token = uri.queryParameters['wishlist'] ?? '';
    if (token.isEmpty && uri.pathSegments.length >= 2 && uri.pathSegments.first == 'wishlist') {
      token = uri.pathSegments[1];
    }
    if (token.isEmpty && uri.path.contains('/wishlist/')) {
      token = uri.path.split('/wishlist/').last.split('?').first.split('#').first;
    }
    if (token.isNotEmpty) {
      await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform,
      );
      runApp(MaterialApp(
        title: 'Numista.AI — Public Wish List',
        debugShowCheckedModeBanner: false,
        home: PublicWishlistViewScreen(token: token),
      ));
      return;
    }
  }

  // ── Attorney portal deep-link detection ──────────────────────────────────
  // If the URL contains /attorney?uid=...&token=... we skip auth entirely and
  // render the read-only attorney portal instead of the normal app.
  final isAttorneyPortal = uri.path.contains('/attorney') ||
      (uri.queryParameters.containsKey('uid') &&
       uri.queryParameters.containsKey('token'));
  if (isAttorneyPortal) {
    final uid   = uri.queryParameters['uid'] ?? '';
    final token = uri.queryParameters['token'] ?? '';
    if (uid.isNotEmpty && token.isNotEmpty) {
      await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform,
      );
      runApp(MaterialApp(
        title: 'Numista.AI — Estate Report',
        debugShowCheckedModeBanner: false,
        home: AttorneyPortalScreen(uid: uid, token: token),
      ));
      return;
    }
  }
  // ── Unknown-path guard (Soft-404 fix) ─────────────────────────────────────
  // Firebase Hosting now returns a real HTTP 404 for garbage URLs.
  // This guard handles the rare case where a valid-looking but unknown path
  // is navigated to *inside* the Flutter app (e.g. a stale bookmark that was
  // once real).
  //
  // Known real paths served by this app shell:
  //   /               — root / home
  //   /wishlist/**    — public wishlist deep links
  //   /attorney_portal — attorney/estate portal (caught above)
  //   /claim          — Phase-2 reservation (L5: routes to home, NOT NotFoundScreen)
  //   /claim/**       — Phase-2 reservation (same)
  //
  // Any other non-empty path not in this set shows NotFoundScreen.
  // Hash-fragment URLs (e.g. /#/claim?...) have uri.path == '/' — they pass
  // through to the normal app flow correctly.
  final path = uri.path;
  final normalizedPath = (path.endsWith('/') && path.length > 1)
      ? path.substring(0, path.length - 1)
      : path;

  final isKnownPath = path.isEmpty ||
      path == '/' ||
      path == '/index.html' ||
      normalizedPath == '/about' ||
      normalizedPath == '/pricing' ||
      normalizedPath == '/features' ||
      normalizedPath == '/faq' ||
      normalizedPath == '/login' ||
      normalizedPath == '/signup' ||
      normalizedPath == '/reset-password' ||
      normalizedPath == '/demo' ||
      normalizedPath == '/app' ||
      normalizedPath == '/blog' ||
      normalizedPath == '/catalog' ||
      path.startsWith('/catalog/') ||
      path.startsWith('/wishlist') ||
      path.startsWith('/attorney_portal') ||
      path.startsWith('/attorney') ||
      path.startsWith('/claim') || // L5: reserved — falls through to home, not NotFoundScreen
      path.startsWith('/privacy') ||
      path.startsWith('/terms') ||
      path.startsWith('/add_coins') ||
      path.startsWith('/scraper_dashboard') ||
      path.startsWith('/api/');

  if (!isKnownPath) {
    runApp(MaterialApp(
      title: 'Numista.AI',
      debugShowCheckedModeBanner: false,
      home: NotFoundScreen(attemptedPath: path),
    ));
    return;
  }

  // Public Catalog direct entry (zero auth required)
  if (normalizedPath == '/catalog' || path.startsWith('/catalog/')) {
    String? initialNacCode;
    if (path.startsWith('/catalog/')) {
      final sub = path.substring('/catalog/'.length).trim();
      if (sub.isNotEmpty) {
        initialNacCode = Uri.decodeComponent(sub);
      }
    }
    if (initialNacCode == null && uri.queryParameters.containsKey('item')) {
      initialNacCode = uri.queryParameters['item'];
    }
    runApp(MaterialApp(
      title: 'Numista.AI Public Catalog',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: Colors.white,
        primaryColor: const Color(0xFF0B2545),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1F5FAD),
          primary: const Color(0xFF0B2545),
        ),
      ),
      home: CatalogBrowseScreen(initialNacCode: initialNacCode),
    ));
    return;
  }

  // Synchronously parse Front Door URL routes
  bool isPendingDemo = false;
  String? pendingPublicRoute;
  int initialAuthTab = 0;
  bool showResetForm = false;

  if (normalizedPath == '/demo') {
    isPendingDemo = true;
  } else if (normalizedPath == '/about' ||
      normalizedPath == '/features' ||
      normalizedPath == '/pricing' ||
      normalizedPath == '/faq' ||
      normalizedPath == '/blog') {
    pendingPublicRoute = normalizedPath == '/blog' ? '/about' : normalizedPath;
  } else if (normalizedPath == '/login') {
    initialAuthTab = 0;
  } else if (normalizedPath == '/signup') {
    initialAuthTab = 1;
  } else if (normalizedPath == '/reset-password') {
    initialAuthTab = 0;
    showResetForm = true;
  }

  // ── General Route deep-link detection (e.g., ?route=Review%20Hub) ────────────
  if (uri.queryParameters.containsKey('route') && uri.queryParameters['route']!.isNotEmpty) {
    WelcomeScreen.pendingRoute = uri.queryParameters['route'];
  }

  // ITEM 10: kApiBaseUrl guard — prevents silent empty-URL HTTP calls.
  // This is a compile-time const so it will never be empty in production,
  // but this guard protects against misconfigured forks or env-var overrides.
  if (kApiBaseUrl.trim().isEmpty) {
    // Throw synchronously so Flutter's error reporter catches it before
    // any HTTP request can fire against an empty URL.
    throw StateError(
      '[Numista] kApiBaseUrl is empty. '
      'Set the backend URL in lib/constants.dart before building.',
    );
  }

  // On Flutter web, Firebase.initializeApp() can silently hang forever if the
  // network is slow or a service worker interferes. We wrap it in a 12-second
  // timeout so runApp() is always called, even in the worst case.
  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    ).timeout(const Duration(seconds: 12));
  } on TimeoutException {
    // Timed out — proceed anyway. The auth StreamBuilder may still resolve
    // once Firebase connects in the background.
    debugPrint('[Numista] Firebase.initializeApp() timed out — proceeding anyway.');
  } catch (e, stack) {
    // Hard failure — show a readable error screen instead of a blank page.
    runApp(MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        backgroundColor: const Color(0xFF0B1220),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 60),
              const Text('🔥 Firebase Init Failed',
                  style: TextStyle(
                      color: Colors.redAccent,
                      fontSize: 22,
                      fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              Text(NumistaErrorHelper.toUserFriendly(e, fallback: 'The app could not start. Please reload the page or contact support@numista.ai.'),
                  style: const TextStyle(
                      color: Colors.orangeAccent, fontSize: 14)),
              const SizedBox(height: 24),
              Text(stack.toString(),
                  style: const TextStyle(
                      color: Colors.white54, fontSize: 11)),
            ],
          ),
        ),
      ),
    ));
    return;
  }

  // Restore persistent Browse Demo state from SharedPreferences across reloads
  try {
    final prefs = await SharedPreferences.getInstance();
    final wasDemoActive = prefs.getBool('browse_demo_active') ?? false;
    if (wasDemoActive || isPendingDemo) {
      await GuestSeedService.activateBrowseDemo();
      isPendingDemo = true;
    }
  } catch (_) {}

  runApp(NumistaAIApp(
    isPendingDemo: isPendingDemo,
    pendingPublicRoute: pendingPublicRoute,
    initialAuthTab: initialAuthTab,
    showResetForm: showResetForm,
  ));
}

class NumistaAIApp extends StatefulWidget {
  final bool isPendingDemo;
  final String? pendingPublicRoute;
  final int initialAuthTab;
  final bool showResetForm;

  const NumistaAIApp({
    super.key,
    this.isPendingDemo = false,
    this.pendingPublicRoute,
    this.initialAuthTab = 0,
    this.showResetForm = false,
  });

  @override
  State<NumistaAIApp> createState() => _NumistaAIAppState();
}

class _NumistaAIAppState extends State<NumistaAIApp> {
  late bool _isPendingDemo;
  late String? _pendingPublicRoute;

  @override
  void initState() {
    super.initState();
    _isPendingDemo = widget.isPendingDemo;
    _pendingPublicRoute = widget.pendingPublicRoute;
    if (_isPendingDemo) {
      GuestSeedService.activateBrowseDemo();
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: ThemeProvider.instance,
      builder: (context, _) {
        return MaterialApp(
          title: 'Numista.AI',
          debugShowCheckedModeBanner: false,
          themeMode: ThemeProvider.instance.themeMode,
          theme: ThemeData(
            visualDensity: VisualDensity.standard,
            brightness: Brightness.light,
            scaffoldBackgroundColor: const Color(0xFFF4F4F2), // Premium parchment/platinum-silver bg
            primaryColor: const Color(0xFF8C7355), // Antique bronze
            cardColor: const Color(0xFFFFFFFF),
            dividerColor: const Color(0xFFE2E8F0),
            colorScheme: ColorScheme.fromSeed(
              seedColor: const Color(0xFF8C7355),
              brightness: Brightness.light,
              primary: const Color(0xFF8C7355),
              secondary: const Color(0xFFC9A227),
              surface: const Color(0xFFFFFFFF),
              error: const Color(0xFFDC3545),
            ),
            fontFamily: 'sans-serif',
            appBarTheme: const AppBarTheme(
              backgroundColor: Colors.white,
              foregroundColor: Color(0xFF0F172A),
              elevation: 0,
            ),
            scrollbarTheme: ScrollbarThemeData(
              thumbVisibility: WidgetStateProperty.all(true),
              trackVisibility: WidgetStateProperty.all(true),
              thickness: WidgetStateProperty.all(12.0),
              radius: const Radius.circular(6.0),
              thumbColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.hovered)) {
                  return const Color(0xFFC9A227);
                }
                return const Color(0xFF94A3B8);
              }),
              trackColor: WidgetStateProperty.all(const Color(0xFFE2E8F0)),
            ),
            textTheme: GoogleFonts.interTextTheme(ThemeData.light().textTheme).apply(
              bodyColor: const Color(0xFF0F172A),
              displayColor: const Color(0xFF0F172A),
            ),
          ),
          darkTheme: ThemeData(
            visualDensity: VisualDensity.standard,
            brightness: Brightness.dark,
            scaffoldBackgroundColor: const Color(0xFF0B1120), // Deep navy-black bg
            primaryColor: const Color(0xFFC9A227), // Metallic gold
            cardColor: const Color(0xFF1E2937), // Rich slate cards
            dividerColor: const Color(0xFF2D3143),
            colorScheme: ColorScheme.fromSeed(
              seedColor: const Color(0xFFC9A227),
              brightness: Brightness.dark,
              primary: const Color(0xFFC9A227),
              secondary: const Color(0xFFD4AF37),
              surface: const Color(0xFF1E2937),
              error: const Color(0xFFDC3545),
            ),
            fontFamily: 'sans-serif',
            appBarTheme: const AppBarTheme(
              backgroundColor: Color(0xFF1E2937),
              foregroundColor: Colors.white,
              elevation: 0,
            ),
            scrollbarTheme: ScrollbarThemeData(
              thumbVisibility: WidgetStateProperty.all(true),
              trackVisibility: WidgetStateProperty.all(true),
              thickness: WidgetStateProperty.all(12.0),
              radius: const Radius.circular(6.0),
              thumbColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.hovered)) {
                  return const Color(0xFFFFD700);
                }
                return const Color(0xFF475569);
              }),
              trackColor: WidgetStateProperty.all(const Color(0xFF1E293B)),
            ),
            textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme).apply(
              bodyColor: const Color(0xFFE8EAF0),
              displayColor: const Color(0xFFE8EAF0),
            ),
          ),
          // ITEM 3: Wrap every route in the text scaler + Morgan feedback drawer.
          // ThemeProvider.textScaleFactor is 1.0 / 1.3 / 1.6 per user setting.
          // MediaQuery.withClampedTextScaling clamps between minScaleFactor and
          // maxScaleFactor — we pin both to the chosen value so OS accessibility
          // settings do not override the in-app control on desktop web.
          builder: (context, child) {
            final scaleFactor = ThemeProvider.instance.textScaleFactor;
            return MediaQuery(
              data: MediaQuery.of(context).copyWith(
                textScaler: TextScaler.linear(scaleFactor),
              ),
              child: FeedbackDrawerOverlay(child: child ?? const SizedBox.shrink()),
            );
          },
      // --- Auth Gate ---------------------------------------------------------
      // StreamBuilder on authStateChanges: handles unauthenticated states,
      // public routes, demo mode, and transitions to BaseLayout on login.
      home: AuthGate(
        isDemo: _isPendingDemo,
        publicRoute: _pendingPublicRoute,
        initialAuthTab: widget.initialAuthTab,
        showResetForm: widget.showResetForm,
      ),
    );
      },
    );
  }
}

/// Fallback widget shown when ErrorWidget.builder is triggered.
/// Plain Material widget — no Navigator, no platform-specific APIs.
/// Report Issue: displays copyable support email address.
class _ErrorFallbackWidget extends StatelessWidget {
  const _ErrorFallbackWidget();

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFF1E2937),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 480),
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline,
                    color: Color(0xFFC9A227), size: 48),
                const SizedBox(height: 16),
                const Text(
                  'Something went wrong loading this screen.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Color(0xFFE8EAF0),
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Please refresh the page. If this keeps happening, '
                  'contact support at the address below.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Color(0xFF8B92B4), fontSize: 14),
                ),
                const SizedBox(height: 6),
                const SelectableText(
                  'support@numista.ai',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Color(0xFFC9A227),
                    fontSize: 14,
                    decoration: TextDecoration.underline,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
<<<END ARTIFACT id=A7>>>

## A8: Source at c547b7a0: numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart (git blob 23f9b854…)

<<<BEGIN ARTIFACT id=A8 sha256=6f08c560e2c2b3513be6100433b5bd5309eca570591cacef6b30993e6ba51da8 bytes=12421 lines=321 path=/workspace/net816-failfix/src/repo/catalog_chunk1_face_value_and_card_test.dart>>>
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_ai/services/melt_value_service.dart';

Future<void> pumpLoadedCatalog(WidgetTester tester, Widget app) async {
  // PlatformAssetBundle extends CachingAssetBundle. This exact key is cached
  // before the screen starts, so its rootBundle.loadString hits a completed
  // Future instead of creating a compute() isolate inside fake async.
  expect(rootBundle, isA<CachingAssetBundle>());
  final loaded = await tester.runAsync<String>(() async {
    return rootBundle.loadString('assets/catalog/catalog_public_v1.json');
  });
  expect(loaded, isNotNull, reason: 'Real-async catalog preload must complete');
  expect(tester.takeException(), isNull, reason: 'Catalog preload must not fail');
  await tester.pumpWidget(app);
  // Bounded frames: never settle an indeterminate loading spinner.
  for (var frame = 0;
      frame < 20 && find.byType(CircularProgressIndicator).evaluate().isNotEmpty;
      frame++) {
    await tester.pump(const Duration(milliseconds: 50));
    if (find.byType(CircularProgressIndicator).evaluate().isNotEmpty) {
      await tester.runAsync(() => Future<void>.delayed(const Duration(milliseconds: 50)));
    }
  }
  expect(find.byType(CircularProgressIndicator), findsNothing,
      reason: 'Cached catalog must leave loading state within bounded frames');
}

void main() {
  group('NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1 & NET-837 #2/#4/#5)', () {
    test('parses previously mis-valued catalog denominations, canonical names, sets, and planchets', () {
      const expectedByDenom = <String, double>{
        // Required CoS / Starter Prompt cases
        'Half dime': 0.05,
        '3 cents': 0.03,
        '3 Cents': 0.03,
        '10 Dollars': 10.00,
        '2 1/2 Dollars': 2.50,
        '1,000 Dollars': 1000.00,
        '10,000 Dollars': 10000.00,
        r'$1000': 1000.00,
        'Dime': 0.10,
        // Remaining N Dollars & catalog variants
        '1 Dollar': 1.00,
        '2 Dollars': 2.00,
        '5 Dollars': 5.00,
        '20 Dollars': 20.00,
        '50 Dollars': 50.00,
        '100 Dollars': 100.00,
        '500 Dollars': 500.00,
        'G\$2\u00bd': 2.50,
        r'$40': 40.00,
        r'$4 Stella': 4.00,
        'Half cent': 0.005,
        'half cent': 0.005,
        '1 Cent': 0.01,
        '1 cent': 0.01,
        '5 Cents': 0.05,
        '5 cents': 0.05,
        '10 Cents': 0.10,
        'Quarter': 0.25,
        '50 Cents': 0.50,
        'Half dollar': 0.50,
        'Dollar': 1.00,
        'Gold dollar': 1.00,
        r'1$': 1.00,
        // Canonical / user collection strings (caller blast radius)
        'Five Cents': 0.05,
        'Ten Cents': 0.10,
        'Ten Cent': 0.10,
        'Twenty-Five Cents': 0.25,
        'Fifty Cents': 0.50,
        'Three Cent Nickel': 0.03,
        '2 Cent': 0.02,
        '5 Dollar': 5.00,
        '25 Dollars (1/2 oz)': 25.00,
        // Multi-denomination sets, ranges, planchets & non-USD guards (NET-837 #5)
        r'$100/$50/$25/$10 platinum': 0.0,
        r'$50/$25/$10/$5 gold': 0.0,
        r'$1, $2, $5, $10 (uncut sheet)': 0.0,
        '3\u00a2\u201350\u00a2': 0.0,
        '50 cent coin planchet': 0.0,
        'Planchet for 1 Cent Coin': 0.0,
        '3.6 Candareens': 0.0,
        '': 0.0,
      };

      expectedByDenom.forEach((raw, expected) {
        expect(
          MeltValueService.parseFaceValue(raw),
          closeTo(expected, 1e-6),
          reason: 'Failed for denomination "$raw"',
        );
      });
    });

    test('full catalog_public_v1.json check: 0 mis-parses across all 3,202 entries, 66 non-null strings, and 71 (type, denomination) pairs', () {
      final file = File('assets/catalog/catalog_public_v1.json');
      final List<dynamic> rawList = json.decode(file.readAsStringSync()) as List<dynamic>;
      expect(rawList.length, 3202);

      // Exact 66 unique non-null denomination strings in catalog_public_v1.json (zero duplicate keys)
      const expectedCatalogDenomValues = <String, double>{
        r'$1 (1 oz silver)': 1.00,
        r'$10 eagle': 10.00,
        r'$100/$50/$25/$10 platinum': 0.00,
        r'$2.50 quarter eagle': 2.50,
        r'$20 double eagle': 20.00,
        r'$25 (1 oz palladium)': 25.00,
        r'$3': 3.00,
        r'$4 Stella': 4.00,
        r'$5 half eagle': 5.00,
        r'$50': 50.00,
        r'$50 (1 oz gold)': 50.00,
        r'$50/$25/$10/$5 gold': 0.00,
        '1 Cent': 0.01,
        '1 Dollar': 1.00,
        '1 cent': 0.01,
        r'1$': 1.00,
        '10 Cents': 0.10,
        '2 1/2 Dollars': 2.50,
        '20 Dollars': 20.00,
        '3 Cents': 0.03,
        '3 cents': 0.03,
        '3.6 Candareens': 0.00,
        '5 Cents': 0.05,
        '5 Dollars': 5.00,
        '5 cents': 0.05,
        '50 Cents': 0.50,
        '50 cent coin planchet': 0.00,
        'CC': 0.00,
        'D': 0.00,
        'Dime': 0.10,
        'Dollar': 1.00,
        'Dollar (two-coin set)': 1.00,
        'G\$2\u00bd': 2.50,
        'Gold dollar': 1.00,
        'Half cent': 0.005,
        'Half dime': 0.05,
        'Half dollar': 0.50,
        "New York World's Fair Billy Rose's Aquacade Commemorative Coin": 0.00,
        "New York World's Fair Frank Buck's Jungleland Commemorative Coin": 0.00,
        "New York World's Fair George Washington Commemorative Coin": 0.00,
        "New York World's Fair George Washington Inauguration Commemorative Coin": 0.00,
        "New York World's Fair Stack's Coin Dealers Commemorative Coin": 0.00,
        'O': 0.00,
        'Planchet for 1 Cent Coin': 0.00,
        'Quarter': 0.25,
        'Quarter (rolls/bags product)': 0.25,
        'copper': 0.00,
        'half cent': 0.005,
        r'$1': 1.00,
        r'$1, $2, $5, $10 (uncut sheet)': 0.00,
        r'$10': 10.00,
        r'$100': 100.00,
        r'$1000': 1000.00,
        r'$2': 2.00,
        r'$20': 20.00,
        r'$40': 40.00,
        r'$5': 5.00,
        r'$500': 500.00,
        '1,000 Dollars': 1000.00,
        '10 Dollars': 10.00,
        '10,000 Dollars': 10000.00,
        '100 Dollars': 100.00,
        '2 Dollars': 2.00,
        '3\u00a2\u201350\u00a2': 0.00,
        '50 Dollars': 50.00,
        '500 Dollars': 500.00,
      };
      expect(expectedCatalogDenomValues.length, 66);

      final seenPairs = <String>{};
      int misParses = 0;
      int medalCount = 0;
      for (final rawItem in rawList) {
        final item = Map<String, dynamic>.from(rawItem as Map);
        final type = item['type'] as String?;
        final denom = item['denomination'] as String?;
        seenPairs.add('$type|${denom ?? "NULL"}');
        if (type == 'medal') {
          medalCount++;
          expect(denom, isNull, reason: 'Medals have no face value denomination');
          continue;
        }
        expect(denom, isNotNull);
        final expected = expectedCatalogDenomValues[denom!];
        expect(expected, isNotNull, reason: 'Unmapped catalog denomination: $denom');
        final actual = MeltValueService.parseFaceValue(denom);
        if ((actual - expected!).abs() > 1e-6) {
          misParses++;
        }
      }
      expect(seenPairs.length, 71);
      expect(medalCount, 56);
      expect(misParses, 0);
    });

    test('caller blast-radius regression: header_stats_bar.dart:108 qty-weighted usdFaceSum & MeltValueService.compute', () {
      // Simulates header_stats_bar.dart:108 usdFaceSum accumulation over a multi-item collection
      final sampleCollection = <Map<String, dynamic>>[
        {'Denomination': 'Five Cents', 'qty': 4},           // 4 * 0.05 = 0.20 (was 0.04)
        {'Denomination': 'Twenty-Five Cents', 'qty': 2},    // 2 * 0.25 = 0.50 (was 0.02)
        {'Denomination': 'Half Dime', 'qty': 3},            // 3 * 0.05 = 0.15 (was 0.30)
        {'Denomination': 'Three Cent Nickel', 'qty': 1},    // 1 * 0.03 = 0.03 (was 0.05)
        {'Denomination': '25 Dollars (1/2 oz)', 'qty': 2},  // 2 * 25.00 = 50.00 (was 2.00)
      ];

      double usdFaceSum = 0.0;
      for (final m in sampleCollection) {
        final denom = m['Denomination'] as String;
        final qty = m['qty'] as int;
        usdFaceSum += MeltValueService.parseFaceValue(denom, qty: qty);
      }
      expect(usdFaceSum, closeTo(50.88, 1e-6));

      // Verify MeltValueService.compute (:141, :146, :200) uses corrected face values for gold/silver oz lookup
      const spot = <String, double>{'Gold': 3000.0, 'Silver': 30.0};
      // 1/2 oz Gold Eagle ('25 Dollars (1/2 oz)', 91.67% gold) -> fv=25.0 -> 0.50 oz * 3000 = 1500.0
      final halfOzGoldEagleMelt = MeltValueService.compute(
        metalContent: '91.67% Gold',
        denomination: '25 Dollars (1/2 oz)',
        spotPrices: spot,
      );
      expect(halfOzGoldEagleMelt, closeTo(1500.0, 1e-4));

      // Pre-1933 Quarter Eagle ('2 1/2 Dollars', 90% gold) -> fv=2.5 -> 0.12094 oz * 3000 = 362.82
      final quarterEagleMelt = MeltValueService.compute(
        metalContent: '90% Gold',
        denomination: '2 1/2 Dollars',
        spotPrices: spot,
      );
      expect(quarterEagleMelt, closeTo(362.82, 1e-2));

      // 90% Silver Quarter ('Twenty-Five Cents') -> fv=0.25 -> 0.18084 oz * 30 = 5.4252
      final silverQuarterMelt = MeltValueService.compute(
        metalContent: '90% Silver',
        denomination: 'Twenty-Five Cents',
        spotPrices: spot,
      );
      expect(silverQuarterMelt, closeTo(5.4252, 1e-3));
    });
  });

  group('NET-816 Chunk 1 — _CatalogCard Widget Tests (#2 & NET-837 #3/#6)', () {
    testWidgets('shows "type photo (date may differ)" when isTypeImage is true and renders parsed face value + honest non-promissory chip', (WidgetTester tester) async {
      await tester.binding.setSurfaceSize(const Size(1440, 2400));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      // 1842 Liberty Seated dollar in catalog_public_v1.json has primary_image: null, type_image != null, denomination: "Dollar"
      await pumpLoadedCatalog(
        tester,
        const MaterialApp(
          home: CatalogBrowseScreen(initialQuery: '1842 Liberty Seated dollar'),
        ),
      );
      await tester.pumpAndSettle();

      final gridFinder = find.byType(GridView);
      expect(gridFinder, findsOneWidget);

      // Scoped to GridView so initialQuery inside the search TextField (:44, :505-506) does not double-match
      expect(
        find.descendant(of: gridFinder, matching: find.text('1842 Liberty Seated dollar')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text('1842 \u00b7 Dollar')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text('type photo (date may differ)')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text(r'$1.00')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text('Face value \u00b7 No retail estimate')),
        findsOneWidget,
      );
      expect(find.text('Value pending AI estimate'), findsNothing);
    });

    testWidgets('medal cards display "No face value" and omit face-value chip', (WidgetTester tester) async {
      await tester.binding.setSurfaceSize(const Size(1440, 2400));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await pumpLoadedCatalog(
        tester,
        const MaterialApp(
          home: CatalogBrowseScreen(initialQuery: 'Libertas Americana medal'),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Medals (56)'));
      await tester.pumpAndSettle();

      final gridFinder = find.byType(GridView);
      expect(gridFinder, findsOneWidget);

      expect(
        find.descendant(of: gridFinder, matching: find.textContaining('Libertas Americana medal')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text('No face value')),
        findsOneWidget,
      );
      expect(find.text('Face Value N/A'), findsNothing);
      expect(find.text('Face value \u00b7 No retail estimate'), findsNothing);
      expect(find.text('Value pending AI estimate'), findsNothing);
    });
  });
}
<<<END ARTIFACT id=A8>>>

## A9: Code Reviewer go-live review (A1/A2 = NET-816 findings; B1–B5 are NET-827, out of scope)

<<<BEGIN ARTIFACT id=A9 sha256=3e2c16709736ab5a5cf834ed9aba9df66704465d7b86f24baf4cf56a0ad864ff bytes=29493 lines=219 path=/workspace/net816-failfix/src/CODE_REVIEW_GO-LIVE_NET-816_NET-827_c547b7a0_20261110.md>>>
# Code Reviewer (Argon) — Go-live review: NET-816 Catalog Chunk 1 + NET-827 Stripe Checkout v1.2

Filed 10 Nov 2026, about 11:15 AM ET. Code pin: p7-v8.9 `c547b7a0`. Plan reviewed: NET-827 v1.2, SHA-256 `273a3268933f9bc1dba25812deecec6c761b3e8de58fa23b45844f1e409ed39d`.

## BLUF

- **NET-816 Catalog Chunk 1: MUST-FIX (1 Blocker, 1 Major).** The face values and the "No face value" chip are correct for all 3,202 catalog rows, and the chunk writes no data. But the /catalog link does not open on Hosting, and the Half dime fix inflates collection melt for 90% silver Half dimes about 10x.
- **NET-827 Stripe Checkout v1.2: MUST-FIX (2 Blockers, 3 Major). DO NOT attach live Stripe keys to the code that exists now.** v1.2 is not built yet. The current checkout lets any signed-in user buy unlimited power_user/sovereign access for $4.99/month, and cancellations usually leave paid access in place.
- **Docs-only claim c547b7a0..999daf14: VERIFIED.** 21 commits, 335 paths, all .md/.txt/.bak docs; no app, config, rules or Hosting files.
- Under the stop rule (wrong charge / wrong access / data loss), B1 and B2 block real payments even at FT 90+. A1 blocks calling /catalog "live".

## Must-Fix

| ID | Sev | Where (c547b7a0) | Problem in plain English | Impact |
|---|---|---|---|---|
| A1 | Blocker | numista_mobile/firebase.json (rewrites only /wishlist, /claim); main.dart ~133-180 | No /catalog rewrite, so numista.ai/catalog 404s; #/catalog also misses (no path URL strategy). | Catalog unreachable. No money/data impact. |
| A2 | Major | melt_value_service.dart:113 (half dime first), :192 (?? 0.77344), :238 (0.05 maps only to nickel) | 90% silver Half dime now falls to the Morgan dollar silver weight. | Dashboard value ~10x too high for those coins (max of AI vs melt). No data loss. |
| B1 | Blocker | payment_routes.py:52-53, :75, :223-224; tier_gatekeeper.py:41-60 | Price comes from the tier NAME; anything not estate/family_estate is $4.99/mo, and the webhook grants whatever tier string was sent. | Wrong access: power_user/sovereign (unlimited) for $4.99/mo. |
| B2 | Blocker | payment_routes.py:208, :212-240; tier_gatekeeper.py:140-150 | Later subscription/invoice events can't find the user (uid only on session), are marked processed anyway; invoice.paid can rewrite stripe_tier to "pro". | Cancel/deletion doesn't remove paid access; no retry. |
| B3 | Major | payment_routes.py:60, :223 | Promo codes allowed on every session; webhook never checks amount_total or payment_status. | Any coupon (incl. a future 100% code) still grants full tier. |
| B4 | Major | payment_routes.py:~53, :196-240 | No idempotency key on session create; webhook dedupe is read-then-write, not a transaction. | Possible double charge; overlapping events double-apply. |
| B5 | Major | payment_routes.py:220-238 | charge.refunded and charge.dispute.created ignored (plan defers to Phase 2). | Refund/dispute keeps paid tier. Not safe for real cards. |

## Christmas code (26 Nov 2026 00:00 UTC rule)

Not in the repo today, so nothing is redeemable from code. **But the v1.2 plan's own snippet is unsafe:** it creates the promotion code with active=True and only expires_at=1798243199 (25 Dec 23:59:59 UTC). Stripe has no start time on that object. Running it before 26 Nov makes the code live immediately, and today's server accepts it on monthly sessions. Fix: keep the code inactive until 2026-11-26T00:00:00Z AND reject it server-side (session create + webhook) before that instant. Plan amendment needed.

## Keys

No live key committed (placeholders only). But stripe_config.py loads STRIPE_SECRET_KEY from env, then .env, then Streamlit secrets — no Secret Manager client and no test/live mode check. "Live keys only from Secret Manager" is enforced only by deployment config, which this review cannot see. Do not leave a test webhook secret on the production service.

## Verified OK

Checkout identity from verified Firebase token (not body); portal IDOR closed; amount is not a client field; webhook raw-body signature check, fails closed on Cloud Run if secret missing; tier writes are merge (no wipe); coins locked, never deleted; catalog chunk writes no Firestore and reads no user docs; medal chip only on type==medal, all 56 medals have null denomination.

## Unknowns (live-only)

Which Hosting site actually serves numista.ai; Secret Manager / Cloud Run env (live vs test keys); Stripe Dashboard coupons/promo codes already active; users with creation_timestamp < 1795669200000 (auto family_estate); deployed vs repo Firestore rules.

## Evidence and method

Static read-only cloud review (https://cursor.com/agents/bc-8faa7e77-0a81-562e-a040-3a5cd880e2be), plus my own spot-check of payment_routes.py, firebase.json and melt_value_service.dart at c547b7a0 via GitHub — B1, B2/B3 lines, A1 (no catalog rewrite) and A2 lines confirmed. No edits, pushes, merges, deploys, tests, or Stripe/Firebase/GCP calls. Full cloud report (SHA-256 aac3c129c961d2f80984c9a8a628a45e4fbf4d38b6698477cb7cc3bf0a61e826) appended below.

---

# Go-live review: NET-816 Catalog Chunk 1 and NET-827 Stripe Checkout

**Pin reviewed:** `c547b7a0ad22923d90042a259da9b56b2c0d6c0c` (checked out; `git rev-parse HEAD`).
**Branch tip checked:** `999daf14c4e96613aab5f6e9108e60a6cc7f0cc1` on `origin/p7-v8.9` after one `git fetch origin p7-v8.9` (local ref was stale at `63de1a45`).
**Attached NET-827 plan SHA-256:** `273a3268933f9bc1dba25812deecec6c761b3e8de58fa23b45844f1e409ed39d` (matches the uploaded v1.2 plan).
**Attached catalog plan SHA-256:** `e9677475b134d4964f302a7df484491d15e941c3c4dab593228b28935cc3dbfa`.

**No source edits, commits, pushes, branches, PRs, merges, deploys, app tests, emulators, or Stripe/Firebase/GCP API calls were made. No Secret Manager values and no user documents were read.** The only network use was the authorized `git fetch` of `p7-v8.9`. Catalog denomination counts below come from an offline local grouping of `catalog_public_v1.json`. Key files were classified with values redacted; the only Stripe key strings in git are placeholders.

---

## Docs-only claim after `c547b7a0`

`git diff --stat c547b7a0 999daf14` / `--name-only`: **21 commits, 335 paths. Application claim holds.**

| Extension | Count |
|---|---:|
| `.md` | 324 |
| `.txt` | 9 |
| `.bak_*` (backups of `WHOSE_TURN.md`) | 2 |

Zero paths under `numista_mobile/`, `numista_backend/`, `functions/`, `.github/`, and zero changes to `firebase.json`, `.firebaserc`, `firestore.rules`, or any `.dart` / `.py` / `.json` / `.yaml` / `.rules` file. The nine `.txt` files are SAG paste prompts and Muse notes. The two `.bak` files are markdown backups.

`git diff --name-only 76ffca1a^ c547b7a0` for `firebase.json` and `firestore.rules`: empty. Chunk 1’s code commits did not change Hosting rewrites or Firestore rules. Chunk 2 vs its parent (`76ffca1a` → `c547b7a0`) is only:

- `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`
- `numista_mobile/lib/services/melt_value_service.dart`
- `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`

---

## PART A — NET-816 Catalog Chunk 1

### BLUF: **MUST-FIX**

The public catalog screen, face-value parser, and medal chip match the approved v2.2 table for all 3,202 catalog rows, and this chunk does not write Firestore or read private user documents. Two material gaps block treating it as live on numista.ai:

1. A browser request for `/catalog` never reaches that screen, because Hosting has no rewrite for it.
2. The same parser change that fixes Half dime face value ($0.05) makes 90% silver Half dime melt use Morgan-dollar weight.

### Must-fix

| ID | Severity | Where (at `c547b7a0`) | What goes wrong | Money / access / data | Fix direction |
|---|---|---|---|---|---|
| A1 | **Blocker** | `numista_mobile/firebase.json:49-132` (rewrites end at `/claim/**`). Route is `numista_mobile/lib/main.dart:133-134` and `:155-180`. | Hosting rewrites `/wishlist` and `/claim` to `index.html`. There is no `/catalog` or `/catalog/**` rewrite. The file’s own comment says unknown paths are a real HTTP 404 (`main.dart:99-114`). `CatalogBrowseScreen` is constructed only from that startup path check (`main.dart:178`). Nothing else in `lib/` navigates to it. `https://numista.ai/#/catalog` also misses: hash URLs have `uri.path == '/'` (`main.dart:113-114`), and there is no `usePathUrlStrategy` anywhere under `numista_mobile/`. | The public catalog URL does not open. No charge and no data write. The feature is unreachable on this Hosting config. | Add the same style of rewrite used for `/wishlist` (`firebase.json:114-120`): `/catalog` and `/catalog/**` → `/index.html`. Path URLs then hit the existing Dart branch. Hash URLs still will not. |
| A2 | **Major** | `numista_mobile/lib/services/melt_value_service.dart:111-112` (new order), `:189-191`, `:230-237`. Callers: `header_stats_bar.dart:108` and `:115`; `home_dashboard.dart:299-300`, `:380-387`. | This commit moves `half dime` ahead of `dime`, so face value is $0.05 (correct on the catalog card). `_matchDenom` maps face `0.05` only to a `nickel` table key. `_ag90` has dime / quarter / half / dollar and no nickel (`:11-16`). A 90% silver Half dime therefore takes the `?? 0.77344` dollar weight (the Morgan/Peace ounce on `:16`). Before this commit, `dime` matched first, so the same string used the dime weight `0.07234`. Dashboard value is `max(AI estimate, live melt)` (`home_dashboard.dart:387`). | Collection melt for a 90% silver Half dime is about 10× the previous dime-weight figure, and can replace a lower AI estimate as the shown value. Catalog cards themselves do not call `compute`. No Stripe charge. No coin documents are deleted. | Give face `0.05` on the 90% silver table a half-dime ounce, or stop using the dollar weight when the face value is a coin the table does not list. |

### Face value and the “No face value” chip

Chip rule (`catalog_browse_screen.dart:1089-1164`):

- `item['type'] == 'medal'` → text **“No face value”**, and `parseFaceValue` is not called.
- Any other type → parsed amount, or an em dash when the parser returns 0. The amber “Face value · No retail estimate” chip still shows on that em dash. It is not the medal chip.

Offline grouping of `numista_mobile/assets/catalog/catalog_public_v1.json`: **3,202** rows (2,965 coin, 181 note, 56 medal), **71** type/denomination pairs, **66** non-null denomination strings. **0 medals have a denomination** (example: Libertas Americana medal, `catalog_public_v1.json:65-69`, `"denomination": null`). **0 non-medals have a null denomination.** Every non-medal denomination parses to the approved v2.2 value (0 mismatches).

So, in this catalog file:

- The medal chip does not hide a real face value.
- The em dash is only the approved zero set: multi-denomination sets, the planchet pair, `3.6 Candareens`, `CC` / `D` / `O`, `copper`, the five World’s Fair names, and `3¢–50¢`. The range guard (`melt_value_service.dart:69`) hits only `3¢–50¢` inside this file.
- A real face value **can** be hidden on a **collection** row, not a catalog row, when the denomination contains a digit, an optional “cent”, and a hyphen (the same guard). Example shape: `5 Cents - 1943`. The approved plan left that as a non-blocking advisory. It is not a new catalog-data defect.
- One catalog product shows a value the plan kept on purpose: `Dollar (two-coin set)` at `catalog_public_v1.json:216602` parses to **$1.00**, because the parenthetical is stripped and the remainder is “dollar” (`melt_value_service.dart:59` and `:118`). `Quarter (rolls/bags product)` parses to **$0.25**. Those are the approved numbers, and they are wrong if someone reads them as a set or roll total.

Half dime on the card is the correct **$0.05** (`catalog_public_v1.json:1391-1395`, denomination `Half dime`, type `coin`). The melt miss is A2, not the card.

### Writes, private data, rules

- The live `/catalog` screen loads `assets/catalog/catalog_public_v1.json` from the app bundle (`catalog_browse_screen.dart:59-63`). Asset is declared at `pubspec.yaml:97`.
- The “Send” control on the missing-item form only sets `_missingSubmitted` in widget state (`catalog_browse_screen.dart:789-795`). Nothing is stored.
- No Firestore, HTTP POST, or `SharedPreferences` use in `lib/screens/catalog/catalog_browse_screen.dart`. The catalog JSON keys are public reference fields (name, denomination, images, mintage, history). No email, uid, token, or user field.
- `UsNumismaticsCatalogScreen._handleAddToCollection` (`us_numismatics_catalog_screen.dart:68-88`) updates an in-memory map and a status string. It is not referenced from `main.dart`, so `/catalog` never opens it. It does not write Firestore.
- The catalog startup path does not call `Firebase.initializeApp` (contrast wishlist at `main.dart:66-68`). It does not read `users/{...}`.
- Firestore rules were not modified. Entitlement fields on `users/{email}` stay server-only (`numista_mobile/firestore.rules:85-101`). This chunk adds no catalog collection and no client rule that would let an anonymous visitor write or read another user’s coins.

---

## PART B — NET-827 Stripe Checkout v1.2

### BLUF: **MUST-FIX**

v1.2 is **not in the tree**. The checkout and webhook that exist at `c547b7a0` will, if a live secret key is attached, charge the wrong amount for any tier name the client sends and will leave paid access in place after cancel. Do not attach live Stripe keys to this code.

The plan’s own Christmas snippet does not encode a start time. Creating that promotion code before `2026-11-26T00:00:00Z` would make it redeemable immediately. That object is not in the repo today.

### Must-fix (defects in code that exists now)

| ID | Severity | Where | What goes wrong | Money / access / data | Fix direction |
|---|---|---|---|---|---|
| B1 | **Blocker** | `numista_backend/routes/payment_routes.py:49-73` and webhook `:220-226`. Schema: `schemas/payment_schemas.py:8-10` (`tier: str`, no enum). Limits: `tier_gatekeeper.py:41-50`. | The client cannot send a dollar amount. The client **can** send any tier string. The server charges **$4.99/month** (`unit_amount = 499`, interval `month`) for every name except `estate` and `family_estate`, which are **$29/year** (`2900`, interval `year`). The webhook then stores that same string as `stripe_tier`. `sovereign` and `power_user` are **not** in the $29 branch, and both have **unlimited** coins and AI allowance (`tier_gatekeeper.py:48-49`, `:59-60`). `check_and_enforce_coin_limit` returns immediately for `power_user` (`tier_gatekeeper.py:238-239`). | A signed-in user can open Checkout for `power_user` or `sovereign` at **$4.99/month** and receive unlimited access. `numismatist`, `dealer`, `gold`, `silver`, `platinum`, `copper`, and `beta_special` are also charged $4.99 and then stored under that name. `family_estate` is **$29/year** for a 2,500-coin / high AI tier. `pro` at $4.99 and `estate` at $29 match the comment in `stripe_service.dart:11` and are the only pair that matches this server. | Allowlist the tier on the server. Set the amount from a server table (or a server-side Stripe Price id), and grant only the tier that table says was paid. Ignore any amount or tier that is not on that list. |
| B2 | **Blocker** | Checkout create `payment_routes.py:53-74` (no `subscription_data`). Webhook identity and writes `:206-240`. Effective tier: `tier_gatekeeper.py:132-157`. | Checkout metadata is `user_uid` + `target_tier` on the **session only**. Subscription and invoice events usually have no `client_reference_id`, no `metadata.user_uid`, and often no email. `target_id` is then empty and the tier write is skipped (`:212`). The event is still marked processed (`:240`), so Stripe will not retry it. `invoice.paid` often **does** have `customer_email` and **does not** have `target_tier`, so the handler writes `users/{email}` with `stripe_tier = "pro"` (`:221-225`). | Cancel and `customer.subscription.deleted` leave the paying user’s tier in place. A renewal can overwrite `stripe_tier` to `pro` on a legacy user document keyed by email. `get_user_tier` also keeps `family_estate` whenever `is_lifetime_family_estate`, `is_ai_qc_account`, or `beta_tester` is set (`:140-143`), and whenever `creation_timestamp` is below `1795669200000` (`2026-11-26T05:00:00Z`, `:145-150`). A later `stripe_tier: free` would not remove those. Coins are not deleted: lock/unlock flips `locked_pending_upgrade` (`tier_gatekeeper.py:325-349`). | Put the Firebase uid and the paid tier on the subscription at create time. On every later event, resolve `customer` → that uid. Drop the email-as-document-id fallback. Do not mark the event done when no user document was updated. Decide explicitly what cancel does to `beta_tester` and lifetime flags; today those flags outrank `stripe_tier`. |
| B3 | **Major** | `payment_routes.py:58` and `:220-226`. | `allow_promotion_codes=True` on every session, including the $4.99 monthly ones. The webhook never reads `amount_total`, `payment_status`, or the coupon id. Access follows `metadata.target_tier` (default `"pro"`). | Any coupon that exists on the Stripe account, including a future 50% or 100% code, lowers the charge and still grants the full tier. A session that completes unpaid is treated as paid. Card-only (`:54`) makes the unpaid card case uncommon; the coupon case does not depend on that. | Turn promotion codes off until the annual-only rule and the coupon allowlist exist. Grant access only when `payment_status` is paid (or the amount is the expected F&F zero) **and** `amount_total` matches the server price for that tier. |
| B4 | **Major** | `payment_routes.py:53` (no idempotency key) and `:196-240`. | Duplicate protection is “read the event doc, later write it.” Two overlapping deliveries can both apply. Two checkout clicks create two sessions; completing both charges twice. A `subscription.deleted` that cannot see the user is stored as done (see B2). | Double charge if the buyer completes two sessions. Missed revocation is permanent for that event id. The tier write itself is a merge, so a repeated identical grant does not wipe the user document. | Idempotency key on session create, one active checkout per user. Claim the event in a transaction before fulfillment, and leave it retryable when the user was not found. |
| B5 | **Major** | `payment_routes.py:220-238` (handled types only). | Handled: `checkout.session.completed`, `customer.subscription.updated`, `invoice.paid`, `invoice.payment_failed` (3-day grace, `:227-232`), `customer.subscription.deleted` (only if a target id exists). `charge.refunded` and `charge.dispute.created` are ignored. The plan defers both to Phase 2. | A refund or dispute leaves the paid tier in place. With B2, cancellation usually does too. | Before live charges, revoke or lock on refund and dispute, and make deletion actually find the user (B2). Phase 2 is not safe for real cards. |

### (1) What is already true, and safe to keep

- Checkout identity comes from the verified Firebase token: `payment_routes.py:35` and `:47-48` (`_user.get("uid")`, token email). `req.user_email` is on the schema (`payment_schemas.py:9`) and is **not** used for the Stripe customer or the metadata uid. `StripeService` still sends `user_email` in the body (`stripe_service.dart:22-26`); the server ignores it for identity.
- Customer portal no longer takes a user email from the query or body. It uses `current_user` only (`payment_routes.py:82-97`). The Flutter caller does not send `user_email` (`stripe_service.dart:47-55`). This is the fix for the earlier portal IDOR.
- `get_current_user` verifies a Firebase ID token (`routes/deps.py:52-79`). The dev-guest bypass runs only when `K_SERVICE` is unset and `ENVIRONMENT` is not `production` and `ALLOW_UNAUTHENTICATED=1` (`deps.py:73-77`). Cloud Run sets `K_SERVICE`.
- Webhook uses the raw body (`payment_routes.py:172`) and `stripe.Webhook.construct_event` (`:182`). On Cloud Run, a missing `STRIPE_WEBHOOK_SECRET` is rejected (`:175-189`). The public allowlist is only so the webhook can skip the Firebase token (`main.py:159-162`); the signature check is inside the handler.
- Success URL (`payment_routes.py:71`) does not grant a tier. No screen under `numista_mobile/lib/` calls `StripeService`; nothing in `lib/` grants a tier from `?stripe=success`. Access is webhook-only. The API route is still mounted (`main.py:123`) and can be called with a bearer token.
- User-doc writes are `set(..., merge=True)` (`payment_routes.py:225`, `:232`, `:237`). They do not clear `beta_tester` or `is_lifetime_family_estate`. Clients cannot write those fields (`firestore.rules:85-101`).
- No `sk_live_` / `pk_live_` / live `whsec_` literal in git. `numista_backend/.env.template:5-7` and `.streamlit/secrets.toml` are placeholders (`sk_test_…`, `pk_test_…`, `whsec_…`). `stripe_config.py:8-9` and `:29-45` load `STRIPE_SECRET_KEY` from the environment, then a `.env` file if present (`load_dotenv`), then Streamlit secrets. There is no Secret Manager client and no check that the key is `sk_test_` vs `sk_live_`.

### (2) Plan items not built (expected, not scored as defects)

These are absent from `payment_routes.py`, `tier_gatekeeper.py`, and the Flutter caller. A later diff review should check them. They are not a reason to describe v1.2 as shipped.

- $30 one-time Beta Special, `mode=payment`, six calendar months via `relativedelta`, no auto-renew (plan §2.1, §4.1, §4.4).
- Copper / Silver / Platinum / Gold monthly and annual amounts (plan §2.2). Code prices are the legacy $4.99 / $29 pair (B1).
- `billing_cycle`, `pre_checkout_coin_count`, `app_version` metadata (plan §4.1).
- Annual-only `allow_promotion_codes`, monthly and Beta Special forced off (plan §3.2).
- Christmas coupon `xmas2026_50off_annual` and promotion code with `expires_at=1798243199` (plan §3.2). Repo search of `*.py` / `*.dart` / `*.yml` found no `xmas`, `christmas`, `1798243199`, or `STRIPE_PROMO`.
- F&F coupon, 500-cap, `is_friends_and_family`, `is_beta_tester`, `beta_access_type`, `$10` then `$5` AI allowance (plan §3.3).
- Transactional two-phase `stripe_events` lease, HTTP 500 while the lease is under 60s (plan §4.2). Current code is the read-then-write at `payment_routes.py:198-240`.
- Hold access until `checkout.session.async_payment_succeeded` (plan §4.3).
- Webhook rejection plus automatic refund when the Christmas coupon lands on a non-annual session (plan §3.2).
- Preview return URLs on `preview-catalog.numista.ai` (plan §4.1). Code returns to `https://numista.ai/#/settings` (`payment_routes.py:71-72` and `:121`).
- `invoice.paid` as a renewal that **refreshes the purchased tier** (plan §4.4). Current `invoice.paid` shares the “set tier from metadata, default pro” branch (B2).

`tier_gatekeeper.create_upgrade_checkout_session` (`:174-201`) is a second, unused checkout (only `check_and_enforce_coin_limit` calls it, and nothing in the request path calls that function). It uses env Price ids with mock fallbacks (`price_1ProMockID` and similar) and `allow_promotion_codes=True`. It is not the live Flutter path. Leave it unwired or it becomes another charge path.

### (3) Where the plan contradicts the code the builder must reconcile

| Topic | Plan | Code at `c547b7a0` | What the builder has to do |
|---|---|---|---|
| Price and mode | Server `price_data` amounts per tier; Beta Special is `mode=payment` at $30. | One `mode=subscription`. $4.99/mo or $29/yr from the tier **name** (`payment_routes.py:49-67`). | Replace the branch. Do not keep both. A client-supplied tier name must not choose an unlimited limit. |
| Who is charged | Token uid only. Plan agrees. | Already the token (`:47-48`). | Keep that. Do not reintroduce `req.user_email` as the customer. |
| Promo window | Christmas code active 26 Nov 2026 00:00:00 UTC through 25 Dec 2026 23:59:59 UTC. | No date check. `allow_promotion_codes=True` always (`:58`). | The plan snippet sets `active=True` at create time and only `expires_at=1798243199` (end). That timestamp is **2026-12-25 23:59:59 UTC**. There is no start field on the snippet. `Coupon.create` in the plan also has no `redeem_by`. Running that snippet before **2026-11-26T00:00:00Z** turns the code on immediately, and this server will accept it on monthly sessions too. Stripe’s `expires_at` does not block early redemption. Add a real start gate (leave `active` false until that instant, and reject the coupon in the webhook and in session create). Client-only checks would not be enough; the client does not see the code server-side today anyway. |
| F&F flag name | Writes `is_beta_tester: true`. | `get_user_tier` reads `beta_tester` (`tier_gatekeeper.py:142-143`). `is_friends_and_family` is not read. | Use the field name the gate actually honors, or teach the gate the new name. Writing `is_beta_tester` alone grants nothing. |
| Cancel vs comped users | `subscription.deleted` sets `stripe_tier` to `free`. | Even a successful free write loses to `beta_tester`, lifetime, and `creation_timestamp` (`tier_gatekeeper.py:140-150`). Nothing in this repo writes `creation_timestamp`; if production docs already have it and it is before `2026-11-26T05:00:00Z`, those accounts are `family_estate` regardless of Stripe. | Decide whether cancel overrides beta/lifetime. Do not assume `stripe_tier=free` changes what `get_user_tier` returns. |
| Refunds | Phase 2, log only (plan §4.5). | Ignored (B5). | For **live** cards this contradicts a safe go-live. Revoke before live mode, even though the preview plan deferred it. |
| Keys | Live keys only from Secret Manager; preview uses test secret names (plan §6). | Any string in `STRIPE_SECRET_KEY` is the API key (`stripe_config.py:29-70`, `payment_routes.py:28-30`). No mode check. | Inject the live key only into the production service, from Secret Manager, and do not also leave a test webhook secret on that service. A test webhook secret on a public URL would accept a forged event signed with the test secret. The code will not catch that mix. |
| Idempotency | Transaction, HTTP 500 while a lease is held (plan §4.2). | Read-then-write, HTTP 200 after skip (`payment_routes.py:198-202`). | Implement the transaction. The current 200-on-duplicate is fine for a finished event and wrong for an in-progress one. |
| App entry | Plan assumes the checkout endpoint is the product. | No screen calls `StripeService` (only `numista_mobile/test/services/bearer_header_integration_test.dart`). | Wiring a button to today’s endpoint ships B1–B5. Build the v1.2 session first. |

---

## Verified OK (short)

**Catalog**

- `/catalog` Dart branch is present and unauthenticated by design: `main.dart:154-180`. It shows `CatalogBrowseScreen` only.
- Medal chip and face line: `catalog_browse_screen.dart:1089-1196`. All 56 medals in the JSON have null denomination (sample `catalog_public_v1.json:65-69`).
- Parser matches the approved 66 denomination strings, including Half dime $0.05, `$1000` → 1000, `G$2½` → 2.50, and the intentional zeros: `melt_value_service.dart:53-129`.
- Bundle asset: `pubspec.yaml:92-97`.
- No catalog Firestore write. Rules for entitlement fields unchanged and server-only: `firestore.rules:85-101`.

**Payments**

- Token uid, not body user, on checkout: `payment_routes.py:35`, `:47-48`.
- Portal IDOR closed on the route the app calls: `payment_routes.py:82-114`, `stripe_service.dart:47-55`.
- Amount is not a client field: `payment_schemas.py:8-10`. The **tier string** is the hole (B1).
- Raw-body signature verify, and fail-closed on Cloud Run when the webhook secret is missing: `payment_routes.py:172-189`.
- Grace period on `invoice.payment_failed`: `payment_routes.py:227-232`.
- Coin rows are flagged, not deleted: `tier_gatekeeper.py:325-349`.
- No live key committed. Placeholders only: `.env.template:5-7`.

---

## Unknowns (only runtime or dashboard can prove)

- Whether the Firebase Hosting site that serves numista.ai is actually this `numista_mobile/firebase.json` (`site`: `numista-vault`, line 7). The repo file has no `/catalog` rewrite. A console-only rewrite would not show up here.
- Secret Manager contents, Cloud Run env bindings, and whether production `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` are live, test, or mixed.
- Stripe Dashboard: which Prices, Coupons, and Promotion Codes already exist; whether any code is `active` before 26 Nov 2026; webhook endpoint URL and signing secret; whether Tax is on. None of that is in git. This review did not call Stripe.
- Whether any `users/{id}` document has `creation_timestamp` below `1795669200000`. Nothing in this repo writes that field (`tier_gatekeeper.py:145-150` only reads it). If it is set, that account is `family_estate` until the cutoff regardless of Stripe.
- Stripe’s response to `Customer.list(email="")` if a token has a uid and no email (`payment_routes.py:96-108`). The portal no longer accepts a caller-supplied email. An empty token email is still passed through.
- Deployed Firestore rules vs `numista_mobile/firestore.rules`. This review did not read the live ruleset.

---

## What was not done

No file in the source tree was edited. No commit, push, branch, PR, merge, or deploy. No Flutter/pytest run, no emulator, no Stripe, Firebase, GCP, or Secret Manager API call, and no read of user documents. One `git fetch origin p7-v8.9` was used to obtain `999daf14` for the docs-only diff.
<<<END ARTIFACT id=A9>>>

## A10: Preview HOLD 74611e05: no c547b7a0 preview deploy

<<<BEGIN ARTIFACT id=A10 sha256=74611e05e00a99e4dfb5f524f16a7dc92d540265986ff138c61ccf5884f11b6b bytes=3208 lines=37 path=/workspace/net816-failfix/src/HOLD_NET-816_PREVIEW-DEPLOY_c547b7a0_NOT-REISSUED_AWAIT-A1A2-FIX_20261110-1148.md>>>
# HOLD — NET-816 p7-gate preview-deploy at c547b7a0 is not re-issued (AG CoS v5)
From: GB CoS via Desk. Decision time: **10 Nov 2026 ~11:47 AM ET** (America/New_York).
Filed: 2026-11-10 11:48:17 EST by Grok Bot Desk. **Decision record only. No WAKE. No code, git, Firebase, or gcloud.**
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
This record grants **no new authority**.

## Decision
The NET-816 preview-deploy baton `BATON_NET-816_AGCOS-V5_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1007.md` (SHA-256 `c65658e0e2783477e0d07b271dcf6cee1e5d939764ccd5ae4f257539e7fcdf0c`) is **HELD**.

It was **BLOCKED** at **11:40 AM ET** with Firebase/gcloud credentials expired, per AG file:
- `BLOCKED_BATON_NET-816_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1140.md`
- SHA-256 `67c5a39002c7cbee71c3c986fbd9b47a8df4fcc9b05f639bc472cb44464c47fe` (2245 B; found on day RADIO NET / BATONS / INBOX / OUTBOX; not seen in mailbox on this check)

**Do NOT re-issue or retry that preview deploy at `c547b7a0`.** That commit lacks the `/catalog` rewrite in `firebase.json` (**A1**), so /catalog would 404.

Re-issue the p7-gate preview deploy **only** at the **A1/A2-fixed commit**, after that fail-fix plan passes **CoS 95 + SAG 95 + Eric's typed YES**.
Eric's **10:06 AM ET YES** (card `t2455s9467`) covered **`c547b7a0` only**. The fixed commit needs his own **new scoped YES**.

## Credentials
Eric has been asked to run `firebase login --reauth` and `gcloud auth application-default login` on EDS_Laptop. This is **CoS-stated and not yet confirmed**. No agent handles his passwords.

## Free tier
Free tier is **10 coins lifetime** per `DECISION_NET-827_FREE-TIER-10-COINS-LIFETIME_RELEASES-HOLD_20261110-1139.md` (SHA-256 `2bf48ebcf9590f119987cc994b38256a7a147f015a8932352e863b35729942a9`).
That decision postdates and **supersedes** AG's contemporaneous ACK §4 wording (see findings below).

## Unchanged
- Go-live addendum `c2b6ac93b844a51d22be23ba428b3d098ad3f2e087e004b3aa6d63919755b4c2` stays **NOT ACTIVE** under HOLD `41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d`.
- The A1/A2 and B1–B5 fail-fix plans remain **plan-only**.
- NET-827 stays **queued**.

## AG BLOCKED / ACK findings (Desk read-only)
- **BLOCKED** as named above: named blocker is expired Firebase CLI session credentials; also records failed `gcloud auth application-default` refresh; live / main / Firestore / Stripe untouched; secondary note confirms A1 missing `/catalog` rewrite at `c547b7a0`.
- No separate ACK of that BLOCKED file, or of the preview-deploy baton, was found on this check.
- Contemporaneous AG ACK at ~11:40: `ACK_HOLD_NET-816_NET-827_AGCOS-V5_20261110-1140.md` SHA-256 `e358a92d6ed82b9d63b3f5985f342ecbb01eb05b6da1a4b74bbfe803694eee3a` (1436 B) — this ACKs the earlier HOLD / fail-fix plan-order notice, not the BLOCKED file.
- That ACK **§4** (“Free-Tier Coin Limit Hold”) says the free-tier limit is “Retained untouched at current codebase state pending CoS written confirmation of Eric's final decision.” That wording is **superseded** by the 10-coin lifetime decision above.

Filing this record ≠ a new preview-deploy baton and ≠ credential confirmation.
<<<END ARTIFACT id=A10>>>

## A11: Go-live stop-rule HOLD 41b8bd5f and fail-fix plan order

<<<BEGIN ARTIFACT id=A11 sha256=41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d bytes=3311 lines=35 path=/workspace/net816-failfix/src/HOLD_NET-816_NET-827_AGCOS-V5_GO-LIVE-STOP-RULE_AND_FAILFIX-PLAN-ORDER_20261110-1113.md>>>
# HOLD / FAIL-FIX PLAN ORDER — NET-816 + NET-827 (AG CoS v5)
From: GB CoS via Desk. CoS order timestamp: **10 Nov 2026 11:15 AM ET** (America/New_York).
Filed: 2026-11-10 11:13:11 EST by Grok Bot Desk. **Notice only. No WAKE.** Desk does not deploy, run git/Firebase/Stripe, or start work.
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
This notice grants **no new authority**. Every fix goes through the normal plan gate (**CoS 95 + SAG 95 + Eric YES**).

## 1) STOP-RULE HOLD — go-live stays NOT ACTIVE
Hold on `ADDENDUM_NET-816_NET-827_AGCOS-V5_CONDITIONAL-GO-LIVE_20261110-1033.md` (SHA-256 `c2b6ac93b844a51d22be23ba428b3d098ad3f2e087e004b3aa6d63919755b4c2`).
**Go-live stays NOT ACTIVE regardless of Field Tester score.**
Basis: Code Reviewer go-live review `C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\10 NOV 26\CODE_REVIEW_GO-LIVE_NET-816_NET-827_c547b7a0_20261110.md` (CoS-cited SHA starting `3e2c1670` ending `864ff`; Desk read-only laptop check: file exists, full SHA-256 `3e2c16709736ab5a5cf834ed9aba9df66704465d7b86f24baf4cf56a0ad864ff` — prefix/suffix match) found **wrong-access** and **wrong-charge** blockers.
**Do NOT** fold to main, deploy live, or attach live Stripe keys.
Lifting this hold needs a **new CoS written confirmation** after fixes pass the gate **and** Eric's YES.

## 2) NET-816 p7-gate PREVIEW deploy still authorized
Eric YES card `t2455s9467`; baton `BATON_NET-816_AGCOS-V5_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1007.md` SHA-256 `c65658e0e2783477e0d07b271dcf6cee1e5d939764ccd5ae4f257539e7fcdf0c`.
**Continue.** File **DONE** with preview URL and built commit (plus the other evidence required in that baton).

## 3) NET-816 FAIL-FIX — PLAN ONLY (no code), due before any live fold
- **A1 BLOCKER:** `firebase.json` has no `/catalog` rewrite at `c547b7a0`, so numista.ai/catalog and #/catalog would break.
- **A2 MAJOR:** Half dime fix uses Morgan-dollar weight for 90% silver half dime melt — about **10× too high** on the collection dashboard.

## 4) NET-827 v1.2 build stays QUEUED
Queued behind the Catalog field test; Stripe **test mode only**. Baton `BATON_NET-827_AGCOS-V5_QUEUED-PREVIEW-BUILD_STRIPE-CHECKOUT-PREVIEW_v1.2_p7-gate_20261110-1031.md` SHA-256 `6693232a39993ddb3e4b678d439a0cd37a91217a148f0fcb8e6d4ed0ec2c1175`.
A revised build plan must close:
- **B1:** Price set from tier name and webhook grants whatever tier was sent, so power_user/sovereign unlock for $4.99 (`payment_routes.py`:52–53, 75, 223–224).
- **B2:** Subscription/invoice events can't find the user but are marked processed, so cancel leaves paid access and `invoice.paid` can reset tier to pro.
- **B3:** Promo codes allowed on every session; `amount_total` and `payment_status` never checked.
- **B4:** No idempotency key; dedupe not transactional.
- **B5:** Refunds and disputes ignored.
Christmas code created **inactive** and rejected server-side before **26 Nov 2026 00:00 UTC**, never on monthly. Live keys from Secret Manager only, with a test/live mode check.

## FREE-TIER COIN LIMIT HOLD
Plan and code say **20**; Eric's 29 Oct and 1 Nov decisions say **10** (**CoS-stated**). Eric is deciding now. **Change nothing** until CoS confirms.

Filing this notice ≠ accepted/started and does not lift or start any production step.
<<<END ARTIFACT id=A11>>>

<<<END OF PACKET>>>
