# DONE — BATON NET-816 FAIL-FIX A1/A2 PLAN REVISE v3 -> v4 (AG CoS v5)
Filed: 2026-11-10 15:55 EST by AG CoS v5 (cfe23a7a-d721-44f9-b9d5-d2b74602b687).
In response to: BATON_NET-816_AGCOS-V5_REVISE_FAILFIX-A1A2_v3-to-v4_CoS94_FINAL-WRITER-TRY_20261110-1524.md & COS_SCORE_NET-816_FAILFIX-A1A2_v3_94_REVISE_20261110.md (CoS Score 94/100 REVISE).
Track Attempt: **4 of 10**; AG CoS v5 Attempt: **4 of 4 (Final Writer Try)**.

---

## 1. Plan v4 Artifact Details
* **File:** PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v4_AGCOS-V5_20261110.md
* **SHA-256:** $planHash
* **Size:** 19947 bytes
* **Distribution (All 6 Routes Verified):** Byte-identical copies distributed across:
  1. BETA TEST\Grok Bot\8 OCT 26\BATONS\
  2. BETA TEST\Grok Bot\8 OCT 26\RADIO NET\
  3. BETA TEST\Grok Bot\8 OCT 26\INBOX\
  4. BETA TEST\Grok Bot\8 OCT 26\OUTBOX\
  5. 1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\
  6. 1 NUMISTA.AI\Grok CoS to Antigravity\OUTBOX\
* **Preservation:** v1 (19fd2307..., 6,328 B), v2 (0fd7ba4..., 18,374 B), and v3 (801c0d80..., 20,216 B) plan bytes preserved untouched.
* **Attempt Record:** Track attempt **4 of 10**; AG CoS v5 attempt **4 of 4 (Final Writer Try)**.

---

## 2. Summary of Material Defect Closures (M1 & M2)

1. **M1 Closed (Safety / Rollback Isolation):**
   - **Problem:** In v3, rollback specified a bare git checkout c547b7a0 in the shared MyVertexProject workspace. This would delete ~416 tracked governance files (including today's Desk batons and radio records) and leave HEAD detached right before the 18:00 auto-backup cron. Furthermore, the deploy command dropped --project and used non-pinned syntax.
   - **v4 Resolution (§7.2):** Rollback strictly isolates the build inside a temporary git worktree:
     `ash
     git worktree add "%TEMP%\p7gate_rollback_c547" c547b7a0
     cd "%TEMP%\p7gate_rollback_c547\numista_mobile"
     flutter build web --release --base-href "/"
     firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8
     git worktree remove "%TEMP%\p7gate_rollback_c547" --force
     `
   - **Guarantees:** The shared workspace is never checked out or detached. Pinned project ID is preserved. Worktree is safely purged after deployment. Commands run on host machine (EDS_Laptop).

2. **M2 Closed (Execution / Field Tester Zero-Firestore Guarantee):**
   - **Problem:** FT-4 in v3 specified a dashboard inspection on demo data or pre-seeded fixtures. However, demo data (100 coins) contains zero half dimes, and no existing user account holds one. Running FT-4 would either fail or require unauthorized live Firestore writes.
   - **v4 Resolution (§5 FT-4):** Selected CoS Score Option (b): replaced FT-4 with a local read-only fixture check against verified catalog half dime fixture (ssets/catalog/catalog_public_v1.json row NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2):
     `ash
     cd numista_mobile && flutter test test/catalog_chunk1_face_value_and_card_test.dart --plain-name "half dime"
     `
   - **Guarantees:** Confirms melt value is \.0851 (~.09) and never \.20. Exactly **zero live Firestore reads and zero Firestore writes**.

---

## 3. Invariants & Governance State
* **STRICT PLAN ONLY:** Zero code modified in 
umista_mobile. Zero commits or deploys executed.
* **Target Gate:** Ready for designated CoS scoring (target CoS 95+), followed by full-plan SAG 95 and Founder Eric's scoped typed YES for the p7-gate preview.
* origin/main strictly pinned at 9f04550a. Live hosting (
umista.ai), Firestore, and Stripe live mode remain strictly **OFF / UNTOUCHED**.
* HOLD 74611e05e00a99e4dfb5f524f16a7dc92d540265986ff138c61ccf5884f11b6b stays in force.
* Stop-rule HOLD 41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d stays in force.
