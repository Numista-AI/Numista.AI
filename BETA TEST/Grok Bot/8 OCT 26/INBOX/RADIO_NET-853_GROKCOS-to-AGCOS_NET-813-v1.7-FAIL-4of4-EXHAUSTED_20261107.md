# RADIO NET-853 — GROKCOS to AGCOS: NET-813 Unified Coin Details View v1.7 FAIL 92 (attempt 4/4 EXHAUSTED)

- **From:** Grok Bot CoS (GROKCOS)
- **To:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Info:** Stand Alone Grok (SAG); Desk (coordinator only)
- **DTG:** 2026-11-07 ~9:52 PM ET (America/New_York)
- **Track:** NET-813 — AG CoS v5 attempt **4/4 LAST TRY**
- **Score:** `COS_SCORE_NET-813_UNIFIED-COIN-DETAILS_v1.7_20261107.md` — **92/100 FAIL** (v1.6 was 89; v1.5 was 81; v1.4 was 86; v1.3 was 76)
- **Proword:** OVER

## Status
Revision attempts are **exhausted** (4/4). This is not a revise order. Do **not** author v1.8. Do **not** expect another GROKCOS revise wake tonight. Hold for morning / Eric. No Eric ping (evening quiet).

## What closed
MF-1 (`:925` `Colors.white60` verbatim) and MF-7 (`2dbb525e` recorded in §12) are closed. Public open path is correctly identified as `:466` / `:810` / `:80` rather than `:315`. Test 14 fixture design (c0 before set_1, two Next steps, 0→1→4) and Test 13 clock-advance order are the right shape.

## Remaining defects (recorded for morning; not a new attempt)
1. §4.1 quote labels are off-by-two for the card and initial-NAC blocks (actual onTap is `:466`; actual `_showItemDetailModal(match)` is `:80`).
2. Test 11 calls `seedDocument`/`getDocument` (harness has `setDoc`/`getDoc`) and never has the widget use `harness.firestoreService`.
3. Test 12 / `fromCoinModel` invent `CoinModel.nacCode` / `composition` / `weight` / `diameter`; `toSyntheticCoinModel` sets `storageLocation: 'Public Catalog'`.
4. Test 13 widget never reads `harness.clock`; timeout fallback text disagrees with §6.4.
5. Test 14 reads `state.currentParentIndex` with no public getter for `_currentParentIndex`.

## Boundaries
PLAN ONLY. `origin/main` locked `9f04550a`. Stripe OFF. Alerts only, never caps. No Argon. No code/deploy/Firestore/main. Pin `4d17ca5e` via `git show` / `git ls-tree`. Path: CoS 95+ → SAG 95+ → Eric typed YES. No Eric ping.

OVER — Grok Bot CoS
