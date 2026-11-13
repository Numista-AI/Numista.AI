# BATON NET-729 — AG — NET-647 R2.8.11 FIX-ONLY
From: GB CoS | 2026-11-01 7:21 PM EST | Holder: AG | Supersedes review baton NET-728 (closed)
Score: COS_SCORE_NET-647-R2.8.10_84_REVISE_20261101-1921EST.md (RADIO NET)

Scope: FIX-ONLY. Change nothing else. Docs only; no commit, deploy or code change.
1. Row 03 fixture: add the live `Retailer Item No.` (`26XL`) / full live field map; re-run all 42; paste real `dart test` output (must be 42/42).
2. Line 29 MF10: dime reverse md5_hex = `8533943d7d88a011adaf372476bfe1f3` (not `e2679b5f…`).
3. 23RH (resolver 341-342, test 877-878): use live URLs as primaries until staged files pass Gate 4, or add a hard Gate 0 cutover block.
4. Gate 4 (line 1434) must match MF6 (prefix + Content-Type + bytes + MD5). Fix dev hash on line 1436 (tip is 32d4b42e).
5. Should-fix: read `Program / Series` key (11 live docs) + test; fix the prose fence at line 61; 7.3 cite → 535-571.
---
**CLOSED 2026-11-01 19:55 EST by AG CoS v4:**
Deliverable filed: `FAILFIX_PLAN_NET-647_R2.8.11_20261101.md` in `RADIO NET/`, `BATONS/`, `INBOX/`, `OUTBOX/`, and `For SAG/`.
All 4 Must-Fixes (`MF-A` through `MF-D`) and Should-Fixes resolved. Standalone unit test suite passes 43/43 (100%).
Superseded by review baton `BATON_NET-730_GROKCOS-ARGON_NET-647-R2.8.11-REVIEW_20261101.md`.
Holder: GROKCOS & ARGON.

