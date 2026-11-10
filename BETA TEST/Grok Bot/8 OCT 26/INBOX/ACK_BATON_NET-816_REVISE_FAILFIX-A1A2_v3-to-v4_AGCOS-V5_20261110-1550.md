# ACK — BATON NET-816 FAIL-FIX A1/A2 PLAN REVISE v3 -> v4 — FINAL WRITER TRY (AG CoS v5)
Filed: 2026-11-10 15:50 EST by AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
In response to: `BATON_NET-816_AGCOS-V5_REVISE_FAILFIX-A1A2_v3-to-v4_CoS94_FINAL-WRITER-TRY_20261110-1524.md` & `COS_SCORE_NET-816_FAILFIX-A1A2_v3_94_REVISE_20261110.md` (CoS Score 94/100 REVISE).

---

## 1. Score & Feedback Acknowledged
* **Official Score:** 94 / 100 REVISE acknowledged (1 point from 95 pass mark).
* **Attempt Count:** Track attempt **4 of 10**; AG CoS v5 attempt **4 of 4** (**Final Writer Try** under Eric's 4-tries rule).
* **Defect Closures Confirmed:** N1 (`#/catalog` out-of-scope architecture), N2 (Dart compile syntax with 14/14 tests passing), and N4 (war nickel weight 0.05626 oz) verified closed with zero regressions.
* **Material Deductions M1 & M2 Accepted in Full:**
  - **M1 (Safety / Rollback):** Rollback from `c547b7a0` MUST NEVER run `git checkout` inside the shared `MyVertexProject` workspace (which would delete 416 tracked governance files and detach HEAD). Rollback MUST use an isolated temporary git worktree at `c547b7a0` (`git worktree add "%TEMP%\p7gate_rollback_c547" c547b7a0`). Pinned deploy command with `--project studio-9101802118-8c9a8` and `--base-href "/"` explicitly specified, executed on host machine (`EDS_Laptop`). Worktree cleaned up after deployment.
  - **M2 (Execution / Field Tester):** FT-4 replaced with Option (b): local read-only check against the catalog half dime fixture (`assets/catalog/catalog_public_v1.json` row `NAC1.CN.US.H10C.SEATEDLIBE.1853.XX.BASE.2`) via machine-checkable test command, ensuring **zero live Firestore reads and zero Firestore writes**.

---

## 2. Invariants & Scope
* **PLAN ONLY:** Zero code modified now. Zero git commits or pushes.
* **Preservation:** v1 (`19fd2307...`), v2 (`a0fd7ba4...`), and v3 (`801c0d80...`) plan bytes preserved untouched.
* **Six Distribution Routes:** v4 will be distributed across all 6 channels (`8 OCT 26/BATONS`, `8 OCT 26/RADIO NET`, `8 OCT 26/INBOX`, `8 OCT 26/OUTBOX`, `1 NUMISTA.AI/.../INBOX`, `1 NUMISTA.AI/.../OUTBOX`).
* Gating invariants maintained: `origin/main` pinned at `9f04550a`; live hosting, Firestore, and Stripe live mode remain strictly **UNTOUCHED**.
