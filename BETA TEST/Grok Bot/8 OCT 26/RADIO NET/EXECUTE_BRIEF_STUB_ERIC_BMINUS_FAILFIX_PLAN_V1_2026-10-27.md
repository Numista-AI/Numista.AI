# EXECUTE BRIEF STUB — Eric B- FAIL-FIX Plan.v1 (NET-630)
**Filed:** 2026-10-27 ~5:44 PM ET by Antigravity Desk (CoS NET-630 order)
**Status:** STUB ONLY — NO CODE / NO DEPLOY / NO AUTHORIZE until SAG score + Eric typed YES
**Preview target after YES:** p7-gate only | origin/main LOCKED
**Plan:** ERIC_BMINUS_FAILFIX_PLAN_v1_2026-10-27.md
**Scores:** Argon 71 CONDITIONAL GO | GB 91 PASS WITH EDITS | SAG paste filed (Eric pasting)

## Mandatory locks (fold Argon Must-Fix 1-5 + GB FF-1..3)

### Fee (I-04b)
1. Also patch/narrow `main.py:7589-7590` 26SQRP blanket `allocated_fee = 0.0` (plan §A.1 alone is insufficient).
2. Parent roll Hub fee vs children: keep invoice S&H ($9.95) on Hub-visible pack/roll parent; do NOT multiply full $9.95 onto pack-expanded children; preserve 26RJ Fee $9.95.
3. Consistent fields: `shipping_fee` / `shipping_amount` / `allocated_fees`.

### Images + vals (I-07 / PM-01)
4. Real `BackgroundTasks` async enrich on `commit_reviews` + named worker; sets/rolls = catalog images + issue_price first (do not wait on Greysheet); skip Greysheet overwrite of catalog baseline for sets.
5. Stamp PascalCase `AI Estimated Value` + `ai_estimated_value` on `/api/review/commit` (FT path); also mirror `keep_set_as_is`.
6. Prove 26RJ catalog image URLs exist and copy to vault on Commit (Argon: URLs exist in catalog; debug fill-missing skip if Theme filled but images empty). Dual-write OK as belt.
7. GB FF-3: fill-missing-only baseline (never overwrite non-blank collector/Greysheet); log enrich errors (no bare except:pass); sets skip GS overwrite.

### No regress
IG-1 dup amber, fill-missing Theme/Condition, 26RJ Fee $9.95, cream contrast, 20-coin wrap.

## Retest proofs (FT pack after preview)
- Commit new 26RJ -> real image + non-zero val (not Pending/$0/Image unavailable)
- 26SQRP Hub Fee = $9.95
- Prior PASS green
- Firestore dumps: committed 26RJ vault + 26SQRP Hub row

## Fallback (Eric YES locked — only if NEXT FT still misses a P0)
Argon writes plan -> GB+SAG review -> Claude/3.8 EXECUTE only. Finish current AG->Argon->GB->SAG cycle first. No mid-flight switch.

## Gate
Do NOT open this stub for coding until: SAG feedback on Plan.v1 + Eric typed YES for preview EXECUTE. Desk will file LIVE EXECUTE wake then.

OVER.
