# Catalog Chunk 1 — new writer wake
Filed: 2026-11-07 15:04:32 ET (America/New_York, observed clock).
TO: Antigravity conversation 9bbe20e4-a0d5-4a25-b16a-f616630ad4bb ONLY.
New Catalog writer; Chunk 1; attempt 1 of 4. This is NOT AG CoS v4. Old AGv4 remains OFF Catalog; do not resume its parked work. Cards next writer remains CoS's decision; rest of queue unchanged.
PLAN ONLY. Chunk 1 only (the two must-fixes in the starter). No implementation, code changes, test/build execution, deploy, API action, spending, or git mutation is authorized by this wake. Preserve all starter gates below: p7-gate only / p7-v8.9 future target; main locked at 9f04550a; Stripe OFF; real file:line/branch/SHA evidence; honest completion timestamp; four-failed-try cap; GB CoS >=95 then SAG >=95 then Eric typed YES, no Argon.
Please ACK addressed to this conversation/wake with your honest ETA (ET) for the plan AND GROKCOS_REVIEW baton. If not yet estimable, say so. Do not invent an ETA. File an ACK through ordinary shared RADIO/BATONS; file copy is not ACK.
Bundled starter, unchanged, is in RADIO NET, BATONS and INBOX under STARTER_CATALOG_FRESH-AG_CHUNK1_20261107.md. Full authoritative starter follows; its historical paste instruction is superseded only by this addressed delivery. No new NET number allocated.

--- BEGIN STARTER ---
# STARTER PROMPT: Catalog NET-777/816, FRESH Antigravity writer, CHUNK 1
Prepared by Grok Bot Desk, 2026-11-07 2:55 PM ET (observed). Eric pastes this into a NEW Antigravity chat. Nothing in this file authorizes execution.

## Who you are / lineage
You are the NEW plan writer for Catalog NET-777/816 (Public Catalog Browse, Thanksgiving critical path). The previous writer (AG CoS v4) is PARKED after 10+ failed attempts (last: v1.11, GB CoS 58/100). Do not continue its thread or reuse its prose.
- New-writer counter: your first submission = **attempt 1**. After **4 failed tries**, stop and hand off (4-try rule).
- Lineage counter (kept separately, not erased): AG CoS v4 = 10+ attempts, v1.10 = 48, v1.11 = 58.

## Hard rules
- **PLAN ONLY.** No code edits, builds, tests runs, deploys, Firestore/DB writes, bucket uploads, merges, pushes of code.
- Future authorized target: **p7-gate only** (`p7-v8.9`). **origin/main locked at `9f04550a`**, never touch. **Stripe OFF.** Alerts only, **no spend caps**; do not change any billing/budget controls.
- **Do NOT copy stale claims** from v1.x plans, scores, or this prompt. Every pin below was reported by GB CoS on 7 Nov; you must re-verify each read-only (`git show`, `git grep`, `git rev-parse`) and quote real **file:line + branch + commit SHA** for every claim. If you can't verify, say "unverified".
- **Honest DTG:** stamp the real time you finish (check the clock). No future dating (v1.10 and v1.11 both failed on this).
- Approval chain: GB CoS ≥95 → SAG ≥95 → **Eric's typed YES**. No Argon. An agent saying "approved" is not approval.

## Reported pins to verify (from GB CoS score v1.11)
dev `b0b058087f1492244a0c0b769e126b38ac1ba06c` · p7 `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235` · origin/main `9f04550a` · origin/dev also cited as `b15fdda1` (reconcile which is current).

## CHUNK 1 (this delivery): 2 must-fixes, nothing else
Source: `BATONS\RADIO_NET-831_GROKCOS-to-AGCOS_REVISE-816-v1.12_20261107.md` items 1-2; `BATONS\COS_SCORE_NET-816_CATALOG_v1.11_20261107.md` lines 14, 17, 20, 23.
1. **Face-value parser (NET-831 #1).** Plan a patch to `MeltValueService.parseFaceValue` (reported `numista_mobile/.../melt_value_service.dart:53-99`) — patch, don't wrap. Parse leading numerics first (`N Dollars`, `1,000 Dollars`, `10,000 Dollars`, `2 1/2 Dollars`, `3 cents`, `$1000`); check `half dime` before `dime` (reported :80/:81); `dollar` branch reported :87. Reported impact: 103/3,202 entries mis-valued (Half dime→$0.10 ×35, 3 cents→$0.01 ×9, N Dollars→$1.00 ×58, $1000→$100). Re-count yourself from `catalog_public_v1.json` `denomination` values. State medal display (no face value) explicitly; correct contrast claim to 4.96:1 (#856404 on #FFF3CD) or re-measure.
2. **Card patch (NET-831 #2).** Minimal diff to `_CatalogCard` in `catalog_browse_screen.dart`: keep the reported `1142-1149` `'type photo (date may differ)'` label and existing title/metadata styling; add `melt_value_service.dart` import at `:1-4`. No rewrite labelled "verbatim".

**Deliverable:** `docs/FAILFIX_PLAN_NET-777_CATALOG_CHUNK1_v2.0.md` containing: verified pins table; exact before/after diffs (planned, not applied); closeout table per item with file:line evidence; planned tests (not run) in a NEW test file (keep the existing 91-line `catalog_browse_test.dart`, package `numista_ai`) with expected outcomes, e.g. `'Half dime'`→0.05, `'3 cents'`→0.03, `'10 Dollars'`→10.00, `'2 1/2 Dollars'`→2.50, `'1,000 Dollars'`→1000.00, `'$1000'`→1000.00, `'Dime'`→0.10 unchanged, and a widget test asserting the card shows `'type photo (date may differ)'` when `isTypeImage`; plus a full-catalog check that 0 of the re-counted mis-parses remain.
**Rollback (history-preserving):** future change lands as its own commit on p7 only; rollback = `git revert <sha>` (no `reset`/`checkout <old sha>`/force push). Docs land via temp worktree + `git checkout <sha> -- <paths>` (not `cherry-pick -- paths`), no force.
Then file `BATON_NET-816_GROKCOS_REVIEW_CATALOG_CHUNK1_<real-DTG>.md` (attempt 1 of 4).

## Parked later chunks (do NOT work on these now)
- **C2:** NET-831 #4 known-error caller (keep `Future<List<MintError>>`, `coin_detail_screen.dart:3526`, `Future.wait` :3507-3514, cite 3505); #5 Greysheet real helpers + route `except → []` swallow (`greysheet_error_routes.py:79-82`); #10-part MintError fixtures (18 required params, `mint_error.dart:100-118`).
- **C3:** #6 Ask Morgan standalone flag (`main.dart:166-178`, :207-209, `welcome_screen.dart:17`, BaseLayout :203-209, `ai_chat_screen.dart:31`); #7 web history helpers (`web_meta*.dart`, initState 40-47, dispose 50-56).
- **C4:** #3 images delivery (CSP `numista_mobile/firebase.json:284`, CORS/read rules, drop unowned CDN hosts, attribution, own Eric-YES upload gate).
- **C5:** #8 Bundle C grounding (real `/api/spot_prices`, `valuation_routes.py:13/:63`, coverage 1,871 & 5 /3,202, sanitizer, real NAC1 codes); #9 Congress.gov key rotation (`coin_legislation_map.py:26`; never quote the key).
- **C6:** #11 single gate numbering, separate production Eric-YES gate (13 Nov target), DTG discipline; #10 remaining tests.
Do not take over Cards NET-817 or any other queue item.

--- END STARTER ---