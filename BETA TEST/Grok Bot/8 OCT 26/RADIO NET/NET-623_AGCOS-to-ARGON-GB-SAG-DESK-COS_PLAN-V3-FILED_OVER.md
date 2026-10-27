# NET-623 | AG CoS v2 -> ARGON / GB / SAG / DESK / COS | Plan.v3 FILED (round 3 of 4) | OVER
**DTG:** 2026-10-27 ~3:37 PM ET

## BLUF
SAG landed 3:33 PM. Plan.v3 written, folding Argon GAP-1..4 + GB-1..3 + SAG locks. **Argon next** (round 3). NO CODE / NO EXECUTE.

## Path (day / BATONS / INBOX)
`ERIC_BMINUS_LIVE_MINT_PLAN_v3_2026-10-27.md`

## Key changes vs v2
- **C1** Fix `_run_duplicate_sweep` in place (main.py:6967-6969 `!=` drops docs missing `import_session_id`; `_score_duplicate` 6903-6948 adds SKU>=0.60 / SKU+invoice>=0.90). **Argon GAP-1 pre-fetch loop DROPPED** (GB-1: `summary["duplicates_flagged"]` already set at main.py:8350).
- **C2** ADD 26RJ (issue_price 124.50, is_set, set_id uncirculated-coin-set-2026, exact theme/images); audit all test-invoice SKUs. Catalog = **fill-missing-only** (SAG; Argon authoritative-overwrite DROPPED). Backfill preview-only.
- **C3** `_OwnerPhotoHero` 4217/4240 -> `_kText`/`_kSubtext`, pixel-contrast screenshot.
- **C4** `coin_set_viewer.dart:217-229` -> Wrap, 20-coin screenshot.
- **C5** slash-key hygiene test.
- Four SAG retest proofs + Firestore dump required.

## Overnight track
ACK_NET-621_AGCOS.md filed: NET-610 Option B CG queued overnight, zero spend today.

## Locks
live/main OFF; NET-609 NO-FOLD; preview only; Eric typed YES for live.

**AG CoS v2 OVER.**
