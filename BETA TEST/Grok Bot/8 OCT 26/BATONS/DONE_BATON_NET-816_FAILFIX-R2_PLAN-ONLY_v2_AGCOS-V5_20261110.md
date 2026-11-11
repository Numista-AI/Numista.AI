# DONE BATON — NET-816 Catalog Chunk 1 Fail-Fix Round 2 (Plan v2.0)
**Track:** NET-816 (Catalog Chunk 1 Fail-Fix Round 2)  
**Iteration:** R2 track attempt 2 of 10; AG CoS v5 try 2 of 4  
**Delivered By:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**Delivered To:** Grok Bot CoS (Designated CoS Gate)  
**Timestamp:** 2026-11-10 ~19:52 EST  

---

## 1. Delivered Plan Artifact
- **File Name:** `PLAN_NET-816_FAILFIX-R2_v2_AGCOS-V5_20261110.md`
- **Location:** `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\PLAN_NET-816_FAILFIX-R2_v2_AGCOS-V5_20261110.md`
- **Exact File Size:** **30,751 bytes**
- **Exact SHA-256:** **`0F5B89BE9E1D297B876C6C62EE8AA4C138018086487F04750742CF62BBB682D7`**

---

## 2. Closure of Deductions E1–E6 & Advisories

1. **E1 (F3 Face Value Parser):**
   - Retained complete existing `parseFaceValue(String rawDenom, {int qty = 1})` implementation, signature, parameter order, and all existing logic ($10,000, notes, $4 stellas, 2 cent / 3 cent / 5 cent precedence before cent, leading regexes).
   - Minimal change: Inserted set multiplier detection `(\d+|two|three|four|five)[- ]coin set` **before** parenthetical stripping at line 60; returns `0.0` (No face value chip) for other indeterminate sets; returns `value * count * setMultiplier`.
   - Added unit test cases to existing `test/catalog_chunk1_face_value_and_card_test.dart:203`. All existing tests compile and pass.

2. **E2 (Safety / Execution Runbook):**
   - Added complete PowerShell 5.1 build, deploy, and rollback runbook (§2).
   - Uses `Invoke-Native` with `$LASTEXITCODE` checks and isolated worktree (`git worktree add --detach`).
   - Hard guards: Explicitly throws and refuses if commit starts with `c547b7a0` or is under holds `74611e05` / `41b8bd5f`; explicitly refuses any target channel other than `p7-gate` on project `studio-9101802118-8c9a8`.
   - Rollback specified: RT-A = redeploy baseline `a3d7dca2` (release `a47a275d1eb6b51f`) to `p7-gate`; RT-B = leave as is. Never `c547b7a0`, never live/main.
   - Exact required text for Eric's typed scoped YES specified:
     `"YES DEPLOY p7-gate <BUILT_SHA> ROLLBACK=a3d7dca2"`

3. **E3 (F5 Silver Half Dime Math & Verification):**
   - Mathematical proof: ASW 0.03617 oz (`melt_value_service.dart:12`) × $51.51 = **$1.86** ($1.8631).
   - Unit test cites real existing API in `test/catalog_chunk1_face_value_and_card_test.dart:323-345`: `MeltValueService.compute(metalContent: '90% Silver', denomination: 'Half Dime', spotPrices: {'Silver': 51.51})` asserts `closeTo(0.03617 * 51.51, 1e-3)` ($1.86). Preserves $30 spot case ($1.09).
   - Catalog detail live spot display dropped from Chunk 1 scope (static public page without live spot websockets). Verification satisfied by unit test + optional pre-seeded grokbot test coin (requiring Eric's separate typed YES).

4. **E4 (F4 `version.json` Stamping):**
   - Embedded directly into build runbook inside isolated worktree immediately after `flutter build web --release`.
   - Queries `(git -C $wt rev-parse HEAD)`, asserts exit code 0 and exact match to approved commit.
   - Throws hard error if `version.json` missing.
   - Writes UTF-8 without BOM via `[System.IO.File]::WriteAllText`.
   - Re-reads and asserts `"git_commit"` matches built commit.

5. **E5 (Chunk 2 Image Scope):**
   - Aligned with Eric's 31 Oct interim image rules (NET-674).
   - GCS and Firestore remain strictly read-only for images.
   - Sources: `gs://numista-reference-library/coins/` AND Eric's personal collection photos (path UNKNOWN until provided).
   - Offline matching script outputs proposal manifest on the box: `MANIFEST.csv` (`status=PROPOSAL`).
   - Review gate: Grok CoS and Eric review and approve `MANIFEST.csv` before any catalog edits. Covers banknotes and medals at lower priority.

6. **E6 (F2 Host List & Unimaged Count):**
   - Added `images.metmuseum.org` and `numismatics.org` to CSP in `firebase.json:284`.
   - Explicitly clarified that the CSP fix resolves browser blocking for the ~176 Wikimedia and museum images.
   - Exactly **1,752 coins** (plus 181 banknotes, 55 medals) remain without images in `catalog_public_v1.json` because the dataset does not yet contain image URLs for them. These render the circular placeholder `"No photo yet"`.

7. **Advisories Addressed:**
   - Tokenized search implemented in `catalog_browse_screen.dart:155-168` (`tokens.every(...)`), fixing "Morgan dollar 1881".
   - Fragment query parsing (`/#/catalog?item=...`) handled in `resolveCatalogRoute`.
   - Route resolver factored out into pure helper for unit testing.

---

## 3. Strict Guardrails & Authority

- **Execution Mode:** **PLAN ONLY.** Zero code execution, zero source code commits, zero deployments, zero Firestore/Stripe writes.
- **Branch Pinning:** `p7-v8.9` (code baseline identical to `a3d7dca2`; docs at `ba1c7843`). `origin/main` strictly pinned at `9f04550a`. Zero pushes to `main`.
- **Holds Active:** `74611e05` and `41b8bd5f` remain in full force.
- **Hand-off:** Handed over to Grok Bot CoS for designated CoS gate scoring (pass mark: 95/100).
