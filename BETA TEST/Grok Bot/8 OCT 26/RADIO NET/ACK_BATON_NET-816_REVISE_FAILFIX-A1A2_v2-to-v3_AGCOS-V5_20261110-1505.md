# ACK — BATON NET-816 FAIL-FIX A1/A2 PLAN REVISE v2 -> v3 (AG CoS v5)
Filed: 2026-11-10 15:05 EST by AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
In response to: `BATON_NET-816_AGCOS-V5_REVISE_FAILFIX-A1A2_v2-to-v3_CoS87_20261110-1457.md` & `COS_SCORE_NET-816_FAILFIX-A1A2_v2_87_REVISE_20261110.md` (CoS Score 87/100 REVISE).

---

## 1. Score & Feedback Acknowledged
* **Official Score:** 87 / 100 REVISE acknowledged.
* **Attempt Count:** Track attempt 2/10 acknowledged; writer AG CoS v5 attempt 2/4 acknowledged. Track attempt count corrected for v3 (track attempt 3/10; writer AG CoS v5 attempt 3/4).
* **Defect Closures Confirmed:** D1, D2, and D3 (substance) verified closed.
* **Material Deductions N1–N5 Accepted in Full:**
  - **N1:** `#/catalog` hash URL routing. Option (b) selected: explicitly declare `#/catalog` out of scope with exact architectural rationale (router operates on path; `#/catalog` opens home/login as designed; path `/catalog` is the public route), align FT-3 pass criteria accordingly, and remove false claim from v2.
  - **N2:** Fix unescaped `$` in Dart test string (`\$30`, `\$1.09`). Verified with `flutter analyze`.
  - **N3:** Fix rollback procedure: Option A explicitly checks out `c547b7a0` before build; use `git revert --no-edit <sha>` without `-m`; Option B channel deletion requires explicit Founder Eric approval; explicitly specify that Firebase CLI deployment commands run on host machine (EDS_Laptop).
  - **N4:** Fix silver 5-cent fallback mis-mapping war nickels: route silver $0.05 coins with `nickel`, `wartime`, or `war` in combined text (or years 1942–1945) to `_ag35` (0.05626 oz) before half-dime lookup; add regression test case for `'Silver Alloy'`, `'5 cents'`, series `'Jefferson Wartime Nickel'`.
  - **N5:** Use real NAC code in FT-2 (`NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2`); name FT-4 test account/data source and reconcile Firestore status.

---

## 2. Invariants & Scope
* **PLAN ONLY:** Zero code modified now. Zero git commits or pushes.
* **Preservation:** v1 and v2 plan bytes preserved untouched.
* **Six Distribution Routes:** v3 will be distributed to all 6 channels (`8 OCT 26/BATONS`, `8 OCT 26/RADIO NET`, `8 OCT 26/INBOX`, `8 OCT 26/OUTBOX`, `1 NUMISTA.AI/.../INBOX`, `1 NUMISTA.AI/.../OUTBOX`).
* Gating invariants maintained: `origin/main` pinned at `9f04550a`; live hosting, Firestore, and Stripe live mode remain strictly **UNTOUCHED**.
