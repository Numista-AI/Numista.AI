# BATON — NET-816 fail-fix v5 BUILD ONLY (no deploy) (AG CoS v5)
Filed: 2026-11-10 16:24:32 EST by Grok Bot Desk, on CoS order. **BUILD ONLY. NO DEPLOY. No WAKE.**
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
Desk files only — Desk does not implement, test, commit, push, or deploy.

## Authority (Desk-verified primary)
- Transcript: Chief of Staff `87de4a6a-9522-4ece-bdfb-87ad19298514`. CoS cites owner message **t2507u**, **2026-11-10 4:23 PM ET**.
- Speaker `cu:420206129`. Desk ReadTranscript of the same exchange; Eric's own user message, verbatim:
  > OK. Go
- That answered CoS's immediately preceding proposal (key scope sentences, verbatim):
  > If you agree, say "go" and I'll send Antigravity the build job for the preview site only. Before anything deploys, I'll bring you the build number and rollback target for your YES.

This is **build + read-only channel record only**. It is **not** a deploy YES. A later scoped Eric typed YES, naming the built SHA and rollback target, is still required before any deploy.

## Gate (Desk-verified file hashes)
- Plan: `PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v5_CLAUDE_20261110.md` SHA-256 `0a7543aff8076f82ac66de1d5e4eb855a332272f326c453594162a368d123f52` (26,194 B).
- CoS **100 PASS**: `COS_SCORE_NET-816_FAILFIX-A1A2_v5_100_PASS_20261110.md` SHA-256 `a19a799ca9cddac7af737c72381a2901f0cd14b7bab94f8beb0a2820f3ac20fa` (9,565 B).
- SAG **97 PASS**: `SAG_RESULT_NET-816_FAILFIX_v5_97_PASS_20261110.md` SHA-256 `347743f2a5015141bb46f6aaab1c459bbe9fc01ce03e41c7e99cc7704f842deb` (847 B). Per CoS, and as seen in the CoS transcript, the SAG result was **pasted by Eric**.

## Scope (exactly)
1. Implement the **3-file change exactly** as written in the v5 plan code blocks, on branch `p7-v8.9`, in an **isolated worktree** (never a checkout in the shared MyVertexProject tree). **No other files.**
2. Run the plan's local tests (`flutter test`, including the half dime test) and `dart analyze`; report full results.
3. Commit and push to **origin `p7-v8.9` ONLY**; report the built fix commit SHA.
4. Make the plan's **READ-ONLY** record of what is currently on the p7-gate channel; report its release time and the rollback target (**RT-A** or **RT-B**).

**STOP after step 4.** File **DONE** on all six routes with commit SHA, test output, and channel record. CoS then brings Eric a scoped YES naming that SHA and rollback target.

## Hard stops
- **No firebase deploy of any kind** (including preview / p7-gate).
- **No main** (stays `9f04550a`, source-stated).
- No live, no Firestore reads or writes, no Stripe.
- No checkout in the shared MyVertexProject tree.
- `c547b7a0` is **never deployed**.
- HOLD `74611e05e00a99e4dfb5f524f16a7dc92d540265986ff138c61ccf5884f11b6b` and stop-rule HOLD `41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d` stay in force.
- Go-live addendum SHA `c2b6ac93b844a51d22be23ba428b3d098ad3f2e087e004b3aa6d63919755b4c2` stays **NOT ACTIVE**.
- Observe the **3 AM ET stand-down**.

## Required returns
1. **ACK** on receipt. **ACK is not start of anything beyond this scope.**
2. **DONE** on all six routes with built commit SHA, full test/`dart analyze` output, and the p7-gate channel record (release time + RT-A or RT-B), or **BLOCKED** with a named blocker (no workaround; no peer contact).

Filing this baton ≠ accepted/started and ≠ deploy authorization.
