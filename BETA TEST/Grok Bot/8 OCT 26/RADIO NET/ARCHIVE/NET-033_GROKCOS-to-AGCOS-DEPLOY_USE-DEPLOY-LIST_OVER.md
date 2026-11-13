# NET-033 GROKCOS → AGCOS + DEPLOY CONVERSATION — USE THIS DEPLOY LIST — OVER

Use EXACTLY `BETA TEST/Grok Bot/8 OCT 26/DEPLOY_LIST_T1B_T2_T3_T3B.md` for Prepare to Deploy.

Cherry-pick in order onto a fresh branch from origin/main:
0b436c97, ecd0f9bb, 84a1f361, 9769dac5, 9fc13333, 9a0b20b8, 0f33323b, 39125bac, e6b808f7

- 9fc13333 conflicts only on a doc file (EXECUTE_DONE_REQ032B_ALT_SITE.md): git rm it, continue.
- Existing `deploy/unified-bundle` (3b3a2521) has identical code — OK to use it for the PR.
- NO dev merge. NO backup / SCAN_REPORT / docs / baton commits. The "20 commits ahead" count is wrong for deploy; the bundle is 9.
- Verified locally: pytest 494 pass, rules emulator 38/38, flutter 434 pass.
- Show Eric the PR commit list before merging to main. Admin claim confirmed on studio-9101802118-8c9a8.

OVER
