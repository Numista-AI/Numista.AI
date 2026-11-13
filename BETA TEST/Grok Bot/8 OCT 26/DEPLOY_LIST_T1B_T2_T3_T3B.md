# DEPLOY LIST — T1B + T2 + T3 + T3b (Grok CoS, 13 OCT 26 ~4:00 PM ET)

Eric YES received (t778u / t781u). Method: cherry-pick ONLY these code commits, IN THIS ORDER, onto a fresh branch from origin/main. NO dev merge. NO backup, SCAN_REPORT, docs, baton or radio commits.

## Ordered cherry-pick list (9 commits)
| # | dev SHA | Track | Subject |
|---|---------|-------|---------|
| 1 | 0b436c97 | T2 | feat(gate0): Morgan confirm-before-write, soft delete, action log, caps, privacy |
| 2 | ecd0f9bb | T3 | feat(032): bigger text tokens, PIN box widget, 6-item nav, 3-choice add coin |
| 3 | 84a1f361 | T3b | feat(032b): UI variant service, server-gated alt site Phase A |
| 4 | 9769dac5 | T2 V2 | fix(gate0-v2): propose/undo, money strip, transactional confirm |
| 5 | 9fc13333 | T3 V2 + T3b V2 | fix(ux-v2+t3b-v2): 14px floor, PIN, wildcard exclusions, ui_variant fail-safe |
| 6 | 9a0b20b8 | T1B + T2/T3/T3b V3 | fix: default-deny middleware, entitlement guard, strip fields, rules |
| 7 | 0f33323b | T1B/T3b rules tests | fix(emulator-tests): rules + test fixes, 28/28 |
| 8 | 39125bac | T1B V2 + T3b V4 | fix: full JWT verify, admin claim, IDOR, route walk test, server-only rules |
| 9 | e6b808f7 | T3 F1/F2 | fix(t3-f1-f2): FreeScanPreviewScreen fonts, focus test |

Already on main (git cherry "-"): a774152f fix(031) — T1, shipped via PR #256. Do not re-pick.

## Mixed-commit conflict (expected, docs-only)
9fc13333 also edits `BETA TEST/Grok Bot/8 OCT 26/EXECUTE_DONE_REQ032B_ALT_SITE.md`, which doesn't exist on main → modify/delete conflict. Resolve by DROPPING that doc file (`git rm` it) and `git cherry-pick --continue`. No code conflicts in any commit.

## Verification (local temp branch, not pushed)
- All 9 applied; only conflict = the doc file above.
- Result tree has ZERO files under BETA TEST/, docs/, SCAN_REPORT or pytest-output.
- Code (numista_backend, numista_mobile lib/test/rules/package.json) is IDENTICAL to origin/dev (empty diff).
- Code is IDENTICAL to existing remote branch `deploy/unified-bundle` (3b3a2521) — that branch is acceptable for the PR.
- Backend pytest: **494 passed** (needs `-s`; default capture hits a pytest I/O closed-file bug on this laptop, not a test failure).
- Firestore rules emulator (jest): **38/38 passed**.
- flutter test: **434 passed, all tests passed**.

## Dependencies
No bundle commit depends on a non-bundle commit for code. Only dependency on outside commits is the doc file in 9fc13333 (drop it). Bundle needs a774152f, already on main.

## Excluded (36 commits)
- Backups: 3036cd06, f49c1fb2, 561b3f44, 3a768301 (touch _scripts/ + pytest-output — not for prod)
- Scan reports: 35ca53a9, e5f5760c, d76e3a4d, c9824e3b
- Docs/batons/radio/rules/reviews: 9ce7d4fa, 67ea1040, f663c91a, 296a57fe, 407e575d, a3e50238, 5fa75bd6, 18e5b829, a79c0c94, e3504813, 18c7e13b, fc1f9065, b9236a9e, 8f126ea1, 817208b2, 22c1ab83, 113f79f5, 6ed27d18 (docs-only, NOT code), 71191231, ecb4aaf3, 42ba03cf, e048b340, 8fbd4efe, d2457ce4, e12eb773, 481156ec, 3a985597
- Other code not in bundle: none.

## Pre-deploy
- eric@numista.ai has `admin: true` on studio-9101802118-8c9a8 (confirmed by Grok CoS). numista-vault was the wrong project.
- After deploy: Field Tester smoke test on live.
