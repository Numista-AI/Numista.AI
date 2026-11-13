# BATON — NET-816 Catalog Chunk 1 v2.2 PREVIEW-DEPLOY (AG CoS v5)
Filed: 2026-11-10 10:07:49 EST by Grok Bot Desk. **PREVIEW CHANNEL ONLY. No WAKE.** Desk files this baton only — Desk does **not** deploy, run Firebase, run git, or touch accounts.
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
Track: NET-816 Catalog Chunk 1 v2.2 — p7-gate preview deploy so Field Tester can later test. This baton does **not** include the Field Tester handoff.

## Authority (parent-verified primary)
- Transcript: Chief of Staff `87de4a6a-9522-4ece-bdfb-87ad19298514` position **21099**.
- Time: **2026-11-10 10:06 AM ET** (America/New_York).
- CoS card `t2455s9467`: “Deploy Catalog Chunk 1 to the p7-gate preview site only, so Field Tester can test it? Main, production, Firestore, Stripe and the catalog fold stay excluded.”
- Actual Eric answer, verbatim:
  > YES, deploy Catalog Chunk 1 (p7-v8.9 at c547b7a0) to the p7-gate preview channel only; no main, production, Firestore, Stripe or catalog fold

This is scoped preview-channel authority only — not production, not a fold, not a new commit/push, and not Field Tester contact.

## Ask
If you have **actual active work**, queue this **after** it — do not interrupt.
Build and deploy Catalog Chunk 1 v2.2 to the **p7-gate preview channel only**, then file **DEPLOY DONE** (or named **BLOCKED**). Filing this baton ≠ accepted/started.

## Build / deploy scope
- Build from `origin/p7-v8.9` at **`c547b7a0`**.
- `2785a134` is acceptable **only** because commits after `c547b7a0` are docs-only (**CoS-stated**). AG **must confirm** the post-`c547b7a0` diff is docs-only before using `2785a134`; otherwise build `c547b7a0`.
- Record **which SHA was actually built**.
- Pinned command, from cwd `C:\Users\ericd\Documents\MyVertexProject\numista_mobile\`:
  `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8`

## Excluded (hard holds)
- **main** stays `9f04550a` (source-stated; do not merge or deploy main).
- No production / live hosting deploy.
- No Firestore data or rules.
- No Stripe.
- No catalog fold.
- No new commits or pushes.
- No workaround if blocked — file a named **BLOCKED**.

## Required completion evidence — DEPLOY DONE
File a DEPLOY DONE record with:
1. Preview URL
2. Built commit SHA (the SHA actually built)
3. Firebase release/version hash
4. Deploy time (ET / America/New_York)
5. Confirmation that live numista.ai was **untouched**

If anything blocks, file a named **BLOCKED** instead; no workaround.

## Record-only corrections for AG's next DONE note (non-blocking)
From `/workspace/evidence/NET-816_COS_INTAKE_20261110.md` **:33–36** (already noted; not a reason to refuse this preview deploy):
- Undisclosed test-setup change (`pumpAndSettle` / related setup) vs DONE saying the plan was “applied as written.”
- DONE listed 8 nonexistent files; actual commit matched the plan list.
- ACK cited stale tip `9b5ee742` vs `2785a134`.
- Pushed to `origin/p7-v8.9` when only local commits were allowed (**Nov 8 push, not new**).

For the **next** DONE note: build DONE file lists from the **actual commit file list**; declare every plan deviation; **no push**.

## After this baton (not in scope here)
After DEPLOY DONE, **CoS** hands Field Tester a bounded check of the /catalog face-value display and the medal “No face value” chip. Do **not** contact Field Tester under this baton.

## Required returns
1. **ACK** — start or queued-behind-named-active-work; honest ETA or ETA unknown.
2. **PROGRESS** as needed.
3. **DEPLOY DONE** with the evidence listed above, or **BLOCKED** with a named blocker (no workaround; no peer contact).
