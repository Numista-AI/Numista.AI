# BATON - RSI CONTROLS PLAN AUTHORSHIP REQUEST -> AG CoS v5 (cfe23a7a-d721-44f9-b9d5-d2b74602b687)
Filed by: Grok Bot Desk (Antigravity Desk) | Filed (real, box clock ET): 2026-11-07 19:27:16 -05:00
Type: PLAN-AUTHORSHIP REQUEST ONLY. No NET number assigned (none invented; CoS/Task Master may assign).
Status: **QUEUED - pending AG ACK. NOT scheduled, NO ETA asserted.** Do NOT interrupt current work.

## 1. Authorization (as reported - not independently verified)
- RSI Engineer reports Eric authorized at 19:25 ET 2026-11-07: "hand the package to Antigravity Desk for AG to write the scoped plan; DO NOT activate changes." CoS notes this was NOT independently verified. Treat as **RSI-reported authorization for plan authorship only. Zero execution permission.**
- Source package: RSI Control Implementation Plan - Proposed: https://cursor.com/canvas/store-dd8ba1d7-08eb-44f0-bc63-5a101f52005a/28d2f1ff-ee68-4248-9d35-e3a6d3215554
- Score history: CoS first scored the PRIOR package 88/100. The REVISED package has **NO new score**. Do not cite 88 as current.

## 2. Queue placement (CoS-stated, 19:25 ET - NOT an AG ACK/ETA)
CoS placement: RSI plan goes **LAST**, behind: NET-813 v1.4 (CoS cited 20:30) -> any NET-817 revise -> NET-814 v1.3 (22:00) -> NET-810 v1.1 (23:15) -> NET-827 Stripe preview (Sun 18:00). Do not displace any of these.
Conditional exception (CoS): v5 MAY start RSI tonight ONLY if NET-810 lands with time remaining before the 03:00 ET AG stand-down; otherwise start after NET-827 is delivered Sunday.
Note: WHOSE_TURN header at 19:35 (AG CoS v5) shows 813 + 814 delivered and 810 on desk ETA 21:00 - CoS placement above still governs; AG decides start only per that condition.

## 3. Ask of AG CoS v5
1. File ACK: `ACK_BATON_RSI-CONTROLS_AGCOS-V5_PLAN-AUTHORSHIP_<real stamp>.md` in BATONS (mirror INBOX/OUTBOX/RADIO NET) with honest start condition + ETA. Real timestamps only; no future-dating.
2. When your turn arrives per Section 2, AUTHOR the scoped plan (plan text only). Return it via BATON to GROKCOS for scoring.

## 4. Required plan scope
A. Writer replacement: mandatory replacement after **4 failed submissions** by one writer on a track; persistent counters; counting examples (fail/pass/withdrawn/blocked).
B. **10 TOTAL unique delivered submissions** on a workstream (not 10 failures) -> notify Eric + propose split BEFORE any further revision; split chunks inherit counters (define inheritance rules with examples).
C. Pinned-source evidence manifest + preflight (full 40-char SHA, file:line, git-show proof) before any claim.
D. Distinct gates: ACK / review / approval / execution / Field Tester closure - each with owner, artifact name, and pass criteria.
E. Proposed 5-plan pilot: eligibility, metrics, baseline caveats, denominators (blocked/withdrawn/open/review-only counted separately), comparability rule.
F. Exact insertion blocks (text to be inserted into which prompt/watch/doc - PROPOSED, not applied), notifier + disposition proof, rollback capture.
G. Field Tester evidence for EVERY open beta item before any broad-retest recommendation.
Proposed owners (pending verification): AG v5 authors; CoS owns watch prompts `ag-plan-handoff-watch` and `ag-plan-handoff-watch-evening` (NO edits; CoS edits only after Eric YES); Desk preflight/RADIO naming; Task Master d07feb3d-6f92-4eb2-a30e-1bd338744b7f ledger.

## 5. Source verification (Desk, read-only, from existing filed documents - no repo commands run)
- Repo: github.com/Numista-AI/Numista.AI (cited in DEPLOY_DONE_P2_COIN_COUNT.md:8, EXECUTE_DONE_P7_V8_11.md:96).
- main lock full SHA `9f04550a45fa4da082ba8948c2d89a521a90fa45` (cited BATONS/COS_SCORE_NET-812_780b-780c-v1.4_20261105.md:4, COS_SCORE_NET-810_..._v1_20261107.md:10, NET-814 v1.3 baton:16).
- `4d17ca5e` appears in filed docs as `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235` (COS_SCORE_NET-780b_CARDS_v1.5:14, COS_SCORE_NET-816_CATALOG_v1.11:10). `b0b05808` appears as `b0b058087f1492244a0c0b769e126b38ac1ba06c` (WHOSE_TURN.md:583; ACK_BATON_NET-815...:19). These are DOCUMENT-CITED expansions, **not Desk-verified against the repo**. AG MUST confirm via read-only `git rev-parse`/`git show` in preflight.
- NET-817 fixture: per COS_SCORE_NET-817_CARDS_IMAGES_v2.0_20261107.md:61-64 (CoS git show/ls-tree at 4d17ca5e): `numista_backend/scripts/reference_library/*` does NOT exist (unsupported-claim case); real paths `numista_backend/_scripts/build_image_index.py`, `build_currency_image_index.py`, `promote_user_photos.py` exist. CoS-cited, not Desk-verified -> AG preflight re-verify.

## 6. Locks / guardrails
PLAN ONLY. main `9f04550a` locked. Stripe OFF. No bot/prompt/routine/code/Firestore/deploy activation; no watch edits. Pipeline: AG plan -> CoS >=95 -> SAG >=95 -> Eric exact-change typed YES. Retired AG CoS v4 (ba2bfdb2) must NOT be woken. Catalog writer 9bbe20e4 (NET-816) separate and unchanged. Counter: new track, AG CoS v5 attempt 1.
