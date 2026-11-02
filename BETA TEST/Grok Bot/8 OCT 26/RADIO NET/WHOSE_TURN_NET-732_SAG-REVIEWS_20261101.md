# WHOSE_TURN — NET-732 — GB CoS → ERIC — SAG round 2 filed (2026-11-01 ~10:05 PM EST)
(Renumbered from NET-731, which was a duplicate: NET-731 belongs to BATON/RADIO_OVER NET-647.)

Round 1 (Stand Alone Grok, xAI API grok-4.7, context-free):
- NET-706 R5 72 REVISE | NET-718 R3 71 REVISE | NET-676 v1.1 76 REVISE

Round 2 (fix-only revisions by GB CoS, checked against origin/dev 32d4b42e):
- NET-706 R6 Meta ad: 78 REVISE — SAG_REVIEW_NET-706-R6_78_REVISE_20261101.md (plan: PRELAUNCH_PLAN_NET-706_R6_META-AD_20261101.md)
- NET-718 R4 Security: 74 REVISE — SAG_REVIEW_NET-718-R4_74_REVISE_20261101.md (plan: SECURITY_PLAN_NET-718_R4_USER-PROTECTION_20261101.md)
- NET-676 v1.2 Images: 76 REVISE — SAG_REVIEW_NET-676-v1.2_76_REVISE_20261101.md (plan: PLAN_IMAGE_CONSOLIDATION_v1.2.md)

None passed. Open for Eric: legacy cutoff (code 26 Nov 00:00 ET vs decision 27 Nov 00:00 ET); UNVERIFIED prices ($1,500 lifetime, $5/1,000 top-up, 6x export rule other than $95.94); code charges $4.99 / $29 vs Plan v3.2; $109/$150 annuals to re-confirm; Stripe billing_address_collection "auto" may still ask for a full address for some cards.
Next turn: GB CoS (R7 / R5 / v1.3) on Eric's go. No push, execute or send. Any PASS still needs Eric's typed YES. OVER.

---
## Round 3 (GB CoS, 1 Nov 2026 ~10:05 PM ET) — all REVISE, nothing pushed/executed/sent
| Plan | Score | Verdict | File |
|---|---|---|---|
| NET-706 R7 | 71 (was 78) | REVISE | SAG_REVIEW_NET-706-R7_71_REVISE_20261101.md |
| NET-718 R5 | 74 (was 74) | REVISE | SAG_REVIEW_NET-718-R5_74_REVISE_20261101.md |
| NET-676 v1.3 | 78 (was 76) | REVISE | SAG_REVIEW_NET-676-v1.3_78_REVISE_20261101.md |

**Settled (Eric):** Legacy cutoff 2026-11-26T05:00Z (code correct). Free = 10 coins (code `tier_gatekeeper.py:42 "free": 20` needs NEW WORK).

**WHOSE TURN: ERIC** — decisions needed before round 4:
1. Stripe: `billing_address_collection` has only `auto`/`required` (Stripe API docs). No setting guarantees no street address. Accept "Stripe-held, Numista never stores" as an explicit exception to Rule 1, or choose another payment flow.
2. Source or drop the §5.2 non-code prices ($49.99, $8.99/$89.99, $10.99/$109, $15.99/$150, $95.94, $500, $625) — still UNVERIFIED.
3. GCS: copies soft-deleted before soft delete is turned off cannot be purged early (Google docs); accept that limit?

**GB CoS regression to fix in R8:** R7 `attributionParams()` filters out `stripe`/`session_id`, which would break Purchase. Other fixes are in each review's must-fix list.
