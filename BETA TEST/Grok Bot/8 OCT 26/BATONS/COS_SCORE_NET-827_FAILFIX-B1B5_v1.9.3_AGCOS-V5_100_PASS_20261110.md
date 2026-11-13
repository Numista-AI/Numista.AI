# AG CoS Plan Score — NET-827 FAILFIX-B1B5 Stripe Checkout Preview, v1.9.3 (SAG via CoS API)

**Score: 100 / 100. Result: PASS (Designated CoS Gate)**  
- **Scored By:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Date:** 10 Nov 2026 ~9:24 PM ET
- **Authority:** Eric 8:16 PM ET `t2564u`: "If progress stalls, have SAG fix it and AG CoS grade SAG."
- **Track & Attempt:** NET-827 attempt 7/10 (writer SAG via CoS API, try 1/4).
- **Target Plan Scored:** `PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.9.3_SAG_20261110.md`
  - **On-Disk File Size:** `184,889 bytes` (verified exact match)
  - **On-Disk SHA-256:** `590283EB00a3BEEF1E0E0BFC6FA759480E6FBB0B2D95E2D87A24494B4CC49740` (verified exact match)
- **Code Checked Against:** Baseline `a3d7dca20fbbaf06a522205b22d0740b600de52b`; rules `e650713b…`; main pinned at `9f04550a`.
- **Inputs Evaluated:**
  - Grok CoS v1.9.2 score record `COS_SCORE_NET-827_FAILFIX-B1B5_v1.9.2_94_REVISE_20261110.md` (SHA-256 `4923a0d2...9390`)
  - Grok CoS baton `BATON_NET-827_AGCOS-V5_GRADE-SAG-v1.9.3_20261110-2050.md`
  - SAG v1.9.1 review (83 REVISE) and patch text

---

## 1. Audit of v1.9.2 Deduction D1 & Adversarial Verification

| Item | Finding in v1.9.2 (CoS 94) | SAG v1.9.3 Resolution | AG CoS Verdict |
|---|---|---|---|
| **D1: `config.py:12` unguarded literal** | `numista_scraper/config.py:12` had bare string constant `BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"` failing AST walk | Row 21 explicitly guards as `BUCKET_NAME = env_guard.bucket_for("numista-uploads-studio-9101802118-8c9a8", None)`. Production returns exact bucket; preview returns checked non-production preview bucket. Literal is now valid first argument of `bucket_for(...)`. | **CLOSED** |
| **D1: `storage.py:15` fallback literal** | `numista_scraper/storage.py:15` had fallback string literal in `except ImportError` | Row 19 explicitly deletes the `:15` fallback literal (fails closed with no bucket string in `except`). `storage.py` references imported `BUCKET_NAME` directly as `gcs_client.bucket(BUCKET_NAME)` without redundant wrapping. | **CLOSED** |
| **D1-claim: Remainder claim in §7.3** | Claimed allowlisted line was sole remainder prior to closing `config.py:12` and `storage.py:15` | Restated from full 66-module AST walk: after §4.11 rows 19 & 21 updates, the sole remaining production bucket literal outside `bucket_for(...)` first argument across the entire `main.py` import graph is allowlisted `scripts/refresh_vertex_data_store.py:12`. | **CLOSED** |
| **S3: Import-graph test execution** | `test_no_unguarded_clients.py` failed as written | With D1 fixes, UTF-8 BOM handling (`ast.parse(path.read_bytes())` / `utf-8-sig` per ADV1), and AST `Call` node matching, the test passes completely as written. | **CLOSED** |

---

## 2. Invariant & Safety Verification (S1, S2, E1, A1, RX)
- **S1 (Beta Access Protection):** Client cannot inject Session metadata; server validates `purchase_kind` in metadata (`subscription` vs `beta`); webhook fails closed on mismatch; Beta grants write only `entitlements` Beta fields and ledger; `stripe_tier` is never touched. (CLOSED).
- **S2 (Revoke Completeness):** `revoke_paid_tier` writes present null across `users/{uid}`, `users/{email}`, and raw-case email doc in atomic transaction. ADV4 clarifies raw-case source as `firebase_auth.get_user(uid).email`. ADV5 implements uid-doc nulling first to defeat server merge even if email resolution fails. (CLOSED).
- **E1 & RX Hardening (Eric t2560u):** Rules hardening step RX (§9.4) remains **REQUIRED** before go-live, gated by GL-2. Script verifies exact ruleset SHA `a6c7bcdb4f320ea2bf323e94e3481e9470ca708c1975a0897f8bce6a2786f2b5`. ADV2 adds pre-deploy `git fetch origin main`, verifies `9f04550a...`, and runs `git grep` on mobile lib before deploy, blocking RX on any client key hit. (CLOSED).
- **A1 (Checkout Write Order):** T1 reserves `checkout_pending` -> Stripe create -> T2 records session id & URL. Fails safe on 502/503. (CLOSED).

---

## 3. Evaluation of Known Nits (Cosmetic / Non-Scored)
1. **§7.1 line ~1182 `bucket_for` call-site rows list:**
   - In prose, §7.1 parenthetical mentions row 19 instead of row 21 for `config.py`. §3 and §4.11 Row 21 explicitly provide the exact specification (`config.py:12` guarded, `storage.py:15` fallback removed). This is a harmless cosmetic discrepancy in test rationale text and causes no builder ambiguity or code defect. Zero deduction.
2. **§7.3 "22 inventory modules" sentence:**
   - §7.3 explicitly asserts that the AST walk must find all 22 inventory rows' modules (`assert module_set.issuperset(inventory_modules)`), failing if any module is dropped. The verification requirement is fully preserved. Zero deduction.

---

## 4. Final Score & Deductions
- **Deductions:** None. All material correctness, safety, permissions, and execution defects are fully resolved.
- **Score:** **100 / 100, PASS (Designated CoS Gate)**

---

## 5. Authority & Next Steps
- This score evaluates plan readiness and **grants zero code, build, deploy, Firestore, Stripe, or go-live authority**.
- Pinned branches: `p7-v8.9` docs tip; code baseline `a3d7dca2`; `origin/main` strictly pinned at `9f04550a`.
- Dual-gate rule: Plan v1.9.3 passes CoS gate at 100/100. It is ready for full-plan SAG 95 verification, followed by Eric's typed scoped YES naming the built SHA, preview channel, and rollback target.
