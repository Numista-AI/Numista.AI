# DONE — BATON NET-816 FAIL-FIX A1/A2 PLAN REVISE v2 -> v3 (AG CoS v5)
Filed: 2026-11-10 15:25 EST by AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
In response to: `BATON_NET-816_AGCOS-V5_REVISE_FAILFIX-A1A2_v2-to-v3_CoS87_20261110-1457.md` & `COS_SCORE_NET-816_FAILFIX-A1A2_v2_87_REVISE_20261110.md` (CoS Score 87/100 REVISE).

---

## 1. Plan v3 Artifact Details
* **File:** `BETA TEST\Grok Bot\8 OCT 26\BATONS\PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v3_AGCOS-V5_20261110.md`
* **SHA-256:** `801c0d80121c8c363381bb6d325dfbcf24fb2925d8bba3ee7456e3aa49658835`
* **Size:** 20,216 bytes
* **Distribution (All 6 Routes Verified):** Byte-identical copies distributed across:
  1. `BETA TEST\Grok Bot\8 OCT 26\BATONS\`
  2. `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\`
  3. `BETA TEST\Grok Bot\8 OCT 26\INBOX\`
  4. `BETA TEST\Grok Bot\8 OCT 26\OUTBOX\`
  5. `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\`
  6. `1 NUMISTA.AI\Grok CoS to Antigravity\OUTBOX\`
* **Preservation:** v1 (`19fd2307...`, 6,328 B) and v2 (`a0fd7ba4...`, 18,374 B) plan bytes preserved untouched.
* **Attempt Record:** Correctly labeled as track attempt **3 of 10**; AG CoS v5 attempt **3 of 4**.

---

## 2. Summary of Material Defect Closures (N1–N5)
1. **N1 Closed:** Explicitly declared `#/catalog` out of scope for this fail-fix track based on `main.dart:113–181` architecture (`uri.path` routing vs `uri.fragment`). Removed false claim from v2 line 34. Aligned FT-3 pass criteria to verify HTTP 200 and clean front-door/home load without 404 or crash.
2. **N2 Closed:** Escaped all literal dollar signs in Dart test reason strings (`\$30` and `\$1.09`) to eliminate compilation errors.
3. **N3 Closed:**
   - Rollback Option A explicitly checks out `c547b7a0` before building and deploying.
   - Replaced invalid `git revert -m` with standard `git revert --no-edit <built_commit_sha>`.
   - Stated that preview channel deletion (`firebase hosting:channel:delete p7-gate -f`) is strictly prohibited without explicit Founder Eric typed `YES`.
   - Stated that Firebase CLI deployment commands run on host machine (`EDS_Laptop`).
4. **N4 Closed:** Fixed war nickel mis-mapping by routing 5-cent silver coins with `nickel`, `war`, or `wartime` in combined text to `_ag35` (0.05626 oz) before half-dime lookup. Added regression test for `'Silver Alloy'`, `'5 cents'`, series `'Jefferson Wartime Nickel'` returning $1.6878 at $30/oz Ag.
5. **N5 Closed:**
   - FT-2 uses real catalog NAC code: `NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2`.
   - FT-4 specifies read-only demo/fixture state (`/demo` or pre-seeded test fixtures) with **zero live Firestore writes**.

---

## 3. Invariants & Next Steps
* **STRICT PLAN ONLY:** Zero code modified in repository. Zero commits or deploys executed.
* **Target Gate:** Ready for designated CoS scoring (target CoS 95+), followed by full-plan SAG 95 and Founder Eric's scoped typed `YES` for the p7-gate preview.
* `origin/main` strictly pinned at `9f04550a`. Live hosting, Firestore, and Stripe live mode remain strictly **OFF / UNTOUCHED**.
