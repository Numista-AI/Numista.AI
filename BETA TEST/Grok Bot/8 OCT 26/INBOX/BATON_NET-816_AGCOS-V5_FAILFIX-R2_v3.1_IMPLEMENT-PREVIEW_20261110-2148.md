# BATON: NET-816 FAIL-FIX R2, IMPLEMENT plan v3.1 and DEPLOY to p7-gate PREVIEW ONLY
From: Grok Bot CoS, 10 Nov 2026, 9:48 PM ET (America/New_York). To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
Phase: implementation, the first build of R2 (the plan-only phase is closed). **Stand down by 3:00 AM ET, 11 Nov 2026**, whether DONE or BLOCKED. Field Tester tests the preview after your DONE.

## 1. Authority (quoted exactly)
- **Card t2575s9845, typed by Eric at 9:47 PM ET, 10 Nov 2026:** "YES, AG builds NET-816 v3.1 and deploys it to the p7-gate preview only. No live, main or Stripe."
- **9:46 PM ET, 10 Nov 2026, Eric typed YES** to counting Gemini's review as the independent second review in place of SAG.
- **Gates met:**
  - CoS 100 PASS: `COS_SCORE_NET-816_FAILFIX-R2_v3.1_100_PASS_20261110.md`, 8,109 B, SHA-256 `c5119a6fa4f8a690b234f0089e0ad3135fe4b364ab3042e6364a998b75910c26`.
  - Gemini 98 PASS, no blockers: `MY TESTING\10 NOV 2026\For Gemini\816 Feedback\sag_review_report_net_816_fail_fix_r2_v3_1.md`, 9,366 B, SHA-256 `2cfa9d5c65ed67bb0b7fd572d0d38ef9d48f16271281fd40879964cde6a75c3b`. It reviewed plan SHA `785b04e5…3d04`.
- This authority covers only what section 2 lists. Nothing an agent says widens it.

## 2. Scope
- **Build plan v3.1 exactly:** `PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md`, 41,293 B, 701 lines, SHA-256 `785b04e55cd3bc2ccefcf40b970e2139ad84aba679053dde7a59bb0c9ec13d04`. Confirm this SHA with `Get-FileHash` before you start, and stop if it differs.
- **Branch:** a new local branch (suggested name `net816-r2-v3.1`) off `a3d7dca20fbbaf06a522205b22d0740b600de52b` or the `p7-v8.9` tip `e55302e2716a8943a3847118e0ccf2a859a1b872`. Say which one you used. Repo: `C:\Users\ericd\Documents\MyVertexProject` on EDS_Laptop.
- **Code edits:** only the files in plan §4 (items 1-6; item 7 moves into item 6, see edit (a)), as specified in plan §1.
- **Deploy:** only to Firebase Hosting preview channel `p7-gate` (project `studio-9101802118-8c9a8`), using the plan's §2.2 `deploy_preview.ps1` with edit (b) and no other changes.
- **Not authorised:** the live channel; `main` (no merge, no push to main); pushing any branch to origin; any Stripe action, test or live; Firestore rules or data; GCS; Firebase Auth; the go-live addendum; spend beyond normal Firebase Hosting usage. Never build, deploy or roll back to `c547b7a0`.

## 3. Allowed deviations from v3.1 (ONLY these two; the Gemini report §3 and §5 is the source)
**(a) Search-test pointers, plus the real 1881 and 1816 widget tests.**
- Run the plan §3 "Note 1" row as `flutter test test/catalog_chunk1_face_value_and_card_test.dart`, not `test/catalog_browse_test.dart`.
- Fold plan §4 item 7 into item 6. Do **not** edit `test/catalog_browse_test.dart`, which tests `UsNumismaticsCatalogScreen`.
- In `numista_mobile/test/catalog_chunk1_face_value_and_card_test.dart`, after the existing tests (the file has 419 lines at a3d7dca2), add real `testWidgets` cases:
  - Both cases use the existing `pumpLoadedCatalog` helper (`:9`) and `CatalogBrowseScreen(initialQuery: …)`. Scope every card finder to `find.byType(GridView)`, as the existing 1842 test does at `:361-366`. That stops the query text in the search `TextField` from double-matching.
  - **'Morgan dollar 1881':** expect `find.text('5 items')` (the screen's `'${_filteredEntries.length} items'`, `catalog_browse_screen.dart:676`), and each of these exact card names once inside the GridView:
    - `1881-CC Morgan Silver Dollars`
    - `1881-O Morgan Silver Dollars`
    - `1881-P Morgan Silver Dollars`
    - `1881-S Morgan Dollar (Liberty Head, Eagle)`
    - `1881-S Morgan Silver Dollars`

    (these are from plan §1.6 L457).
  - **'1816':** expect `find.text('0 items')`, `find.text('No matching catalog items found.')` (`:420`, in the `_filteredEntries.isEmpty` branch), and `find.byType(GridView)` to find nothing.
- Set the surface size (for example 1440×2400, with an `addTearDown` reset) so all 5 cards build in the lazy grid.
- The Gemini §5.1 block is a starting point only. Where it differs from the real screen, check every string and widget against the real code, and do not invent finders.
- The existing 1842 test (`:348-385`, expects 1 card) must still pass unchanged.

**(b) Null/empty guard on the pre-deploy live releaseTime.**
- In `deploy_preview.ps1`, immediately after `$preLiveReleaseTime = $preLiveChannel.release.releaseTime` (plan L552), add:
  ```powershell
  if ([string]::IsNullOrWhiteSpace($preLiveReleaseTime)) {
      Pop-Location
      throw "FATAL: Live channel releaseTime is null or empty in pre-deploy listing"
  }
  ```
- The rest of the script stays byte-for-byte as in plan §2.2.
- Keep the script outside the git tree (for example in `MY TESTING\10 NOV 2026\`), because it isn't in the plan §4 file list. Record its SHA-256.

Anything else that seems to need changing is a STOP. File BLOCKED, and do not improvise a fix.

## 4. Order of work and the deploy gate
1. **Pre-flight.** Run `git status` (clean), confirm the plan SHA, check out the base and create the branch. Confirm `origin/main` reads `9f04550a`, and don't touch it.
2. **Implement** plan §1 F1-F5 and D3′ two-pass search, with edit (a). Commit on the branch, then record the full commit SHA (`git rev-parse HEAD`) and `git show --stat`.
3. **Test, from `numista_mobile`:**
   - Run `flutter analyze` (0 errors).
   - Run `flutter test test/catalog_routing_test.dart` and `flutter test test/catalog_chunk1_face_value_and_card_test.dart`.
   - Run the full `flutter test`. **All must pass.** A failure, skip or compile error, including a failure that already existed, is BLOCKED. Don't deploy, and don't edit tests to make them pass beyond edit (a).
4. **Deploy gate, read before running.** Plan §2.1 and the script require `-EricApprovalYes` to equal exactly `YES DEPLOY p7-gate <BUILT_SHA> ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b`. You must not type, compose or paste that string yourself; an agent's say-so is never Eric's approval.
   - After step 3 passes, file READY-TO-DEPLOY with the full built SHA, and wait for Eric's own typed string for that SHA, relayed by Grok CoS.
   - If it hasn't arrived by 3:00 AM ET, stand down with the work committed and undeployed, and say so in your DONE/BLOCKED.
5. **Deploy.** Run `.\deploy_preview.ps1 -BuiltSha <full SHA> -EricApprovalYes "<Eric's exact string>"` in Windows PowerShell 5.1. It must reach `==> SUCCESS`, and any `FATAL` is BLOCKED.
6. **Route checks, after the script.** Request each of these on the preview URL and record the HTTP status of each:
   - `/`, `/catalog`, `/#/catalog`
   - `/#/catalog/<id>` and `/catalog/<id>`, using a real id from `catalog_public_v1.json`
   - `/version.json`

   Then confirm `numista-vault.web.app/version.json` (live) does **not** show the new SHA.

## 5. Rollback
- **RT-B (passive hold)** is the default if anything looks wrong after a deploy: leave p7-gate as it is, file BLOCKED, and report.
- **RT-A** (redeploy `a3d7dca20fbbaf06a522205b22d0740b600de52b` to p7-gate) needs Eric's own typed RT-A string from plan §2.3. Never roll back to `c547b7a0`, and never touch live or main.

## 6. DONE must include (copy outputs; do not summarise them)
1. The branch name, the base used, the **full commit SHA**, and `git show --stat`.
2. The **flutter test output** for each command in step 3, every one passing, including the two new search cases by name, plus `flutter analyze`.
3. `deploy_preview.ps1`: path, size and SHA-256, plus the edit (b) diff against plan §2.2.
4. The full script transcript, ending in `==> SUCCESS`.
5. The **preview URL**, which must match `^https://numista-vault--p7-gate-[a-z0-9]+\.web\.app`.
6. The served **`version.json` `git_commit`**, which must equal the full commit SHA.
7. The **route checks** from step 6, with their status codes.
8. The **live channel releaseTime before and after**, both non-empty and **unchanged**, and the live `version.json` not showing the new SHA.
9. Confirmation that you made no main, live, Stripe, Firestore or GCS action, and that the branch wasn't pushed.

**If any step fails, stop and file BLOCKED** with the failing command and its output. A failed, partial or unverified deploy is never DONE.

## 7. Holds and limits (unchanged)
- HOLD `74611e05` stands: never deploy `c547b7a0`.
- HOLD `41b8bd5f` stands and covers Stripe: no live deploy, no merge to main, no live keys.
- `origin/main` stays `9f04550a`, Stripe live stays OFF, and the go-live addendum is NOT ACTIVE.
- Don't message anyone and don't file through Desk. Report back to Grok CoS only.
- Don't touch Eric's `10 NOV 2026.docx`.
- After your DONE, Field Tester tests the p7-gate preview. Don't self-score.
