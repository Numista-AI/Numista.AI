# DONE — BATON NET-816 FAIL-FIX A1/A2 PLAN REVISE v1 -> v2 (AG CoS v5)
Filed: 2026-11-10 14:55 EST by AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
In response to: `BATON_NET-816_AGCOS-V5_REVISE_FAILFIX-A1A2_v1-to-v2_CoS79_20261110-1400.md` & `COS_SCORE_NET-816_FAILFIX-A1A2_v1_79_REVISE_20261110.md` (CoS Score 79/100 REVISE).

---

## 1. Plan v2 Artifact Details
* **File:** `BETA TEST\Grok Bot\8 OCT 26\BATONS\PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v2_AGCOS-V5_20261110.md`
* **SHA-256:** `a0fd7ba4706eb2026fa548ed0c57f00402c8fe43c05df074bb89263ca4a3bfbb`
* **Size:** 18,374 bytes
* **Distribution:** Byte-identical copies distributed across all 4 channels:
  - `BETA TEST\Grok Bot\8 OCT 26\BATONS\`
  - `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\`
  - `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\`
  - `1 NUMISTA.AI\Grok CoS to Antigravity\OUTBOX\`
* **Preservation:** v1 plan (`19fd2307be1318a076663bc2b8771d41e5119605792e3f6dfb4f5e4e38f460c3`, 6,328 B) preserved untouched.

---

## 2. Summary of Defect Closures (D1–D6)
1. **D1 Closed:** Removed dangerous Morgan fallback at line 201 (`if (ag > 0) return ag * 0.77344 * count;`). Sub-dollar silver lacking "90%" text (14 dimes, 22 quarters, 62 halves, 28 89.24% pieces) now resolves via `_matchDenom(_ag90, denom)` to exact denomination weights (0.07234, 0.18084, 0.36169, 0.03617 oz). Unmodeled silver returns `null`.
2. **D2 Closed:** Base dollar fallback on `fv == 1.00 || combined.contains('dollar') || combined.contains('morgan') || combined.contains('peace')` rather than denom text alone, preserving Morgan/Peace dollars with empty denom or denom `CC` (series `1$-Morgan dollar`).
3. **D3 Closed:** Added regression tests (a)–(d) to `catalog_chunk1_face_value_and_card_test.dart` verifying:
   - (a) Unlisted 90% sub-dollar (e.g. "Twenty Cent") returns `null` and never `0.77344`.
   - (b) Kept dollar fallback preserved for Morgan/Peace with empty denom or denom `CC`.
   - (c) Standard denominations preserved (90% dime, quarter, half, dollar; 40% half; 35% war nickel).
   - (d) Half dime variants compute to 0.03617 oz * spot.
4. **D4 Closed:** Added bounded 4-step Field Tester test suite (`/catalog`, `/catalog/<nac>`, `#/catalog`, half dime dashboard melt value) with explicit PASS/FAIL rules.
5. **D5 Closed:** Documented SPA client-side hash routing (`#/catalog` served via `/index.html` rewrite at `/`) vs server-side path rewrites (`/catalog` and `/catalog/**`).
6. **D6 Closed:** Specified base branch `p7-v8.9`, base commit `c547b7a0`, mandated logging built commit SHA in DONE report, and defined exact rollback procedures for code and hosting channel.

---

## 3. Invariants & Next Steps
* **PLAN ONLY:** Zero code modified in repository. Zero commits or deploys executed.
* **Gating Requirements:** Ready for designated CoS scoring (target CoS 95), followed by full-plan SAG 95 and Founder Eric's scoped typed `YES` for the p7-gate preview.
* `origin/main` strictly pinned at `9f04550a`. Live hosting, Firestore, and Stripe live mode remain strictly **OFF / UNTOUCHED**.
