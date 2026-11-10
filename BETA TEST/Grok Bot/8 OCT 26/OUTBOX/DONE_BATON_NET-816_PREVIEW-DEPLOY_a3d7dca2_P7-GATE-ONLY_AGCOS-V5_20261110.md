# DONE — BATON NET-816 PREVIEW DEPLOY a3d7dca2 to p7-gate ONLY

- **Desk:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Filing Date:** 2026-11-10 18:10 EST
- **Baton Completed:** `BATON_NET-816_AGCOS-V5_PREVIEW-DEPLOY_a3d7dca2_P7-GATE-ONLY_20261110-1704.md`
- **Authority Record:** `AUTH_NET-816_PREVIEW-DEPLOY_a3d7dca2_ERIC-PRIMARY-YES_DESK-VERIFIED_20261110-1741.md` (Eric primary YES card `t494s1610`, 10 Nov 2026 5:41 PM ET: *"YES. Deploy build a3d7dca20fbbaf06a522205b22d0740b600de52b to the p7-gate preview channel only. Rollback target RT-B, no redeploy. No live, no main, no Stripe, no Firestore."*)

---

## 1. Execution Summary

1. **Isolated Worktree:**
   - Worktree created at detached HEAD `a3d7dca20fbbaf06a522205b22d0740b600de52b`.
   - Verified `git rev-parse HEAD` = `a3d7dca20fbbaf06a522205b22d0740b600de52b`.
   - Shared workspace `MyVertexProject` was not checked out or dirtied.

2. **Web Build:**
   - Ran `flutter build web --release --base-href "/"` from `numista_mobile`.
   - Exit code: 0 (`√ Built build\web` in 190.2s).

3. **Preview Channel Deploy:**
   - Ran `firebase hosting:channel:deploy p7-gate --expires 7d --project studio-9101802118-8c9a8`.
   - Deployed 60 files to site `numista-vault`, channel `p7-gate`.
   - Release Version: `a47a275d1eb6b51f`.
   - Channel URL: **`https://numista-vault--p7-gate-8avtpz22.web.app`**
   - Channel Expiry: `2026-11-17 18:07:00` (7 days).

---

## 2. Channel-List Readback Verification

Ran `firebase hosting:channel:list --project studio-9101802118-8c9a8 --site numista-vault`:

| Site | Channel ID | Last Release Time | URL | Expire Time | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `numista-vault` | `p7-gate` | **2026-11-10 18:07:06** | `https://numista-vault--p7-gate-8avtpz22.web.app` | 2026-11-17 18:07:00 | **NEW / ACTIVE** |
| `numista-vault` | `live` | **2026-11-04 16:00:02** | `https://numista-vault.web.app` | never | **UNCHANGED** |
| `numista-vault` | `p7v12` | 2026-11-04 15:59:26 | `https://numista-vault--p7v12-c47m6bz0.web.app` | 2026-11-11 15:59:20 | UNCHANGED |
| `studio-9101802118-8c9a8` | `live` | **2026-06-24 20:10:45** | `https://studio-9101802118-8c9a8.web.app` | never | **UNCHANGED** |

**Conclusion:** Live production channels are 100% UNCHANGED.

---

## 3. Smoke Check Over HTTP (SPA Rewrites Verified)

Tested with `Invoke-WebRequest -Method Get`:

| URL | HTTP Status | Bytes | Title | Verification |
| :--- | :--- | :--- | :--- | :--- |
| `https://numista-vault--p7-gate-8avtpz22.web.app/` | **200 OK** | 12,261 | Numista.AI — AI-Powered Coin Collection Manager | Root SPA load OK |
| `https://numista-vault--p7-gate-8avtpz22.web.app/catalog` | **200 OK** | 12,261 | Numista.AI — AI-Powered Coin Collection Manager | **Rewrite A1 FIXED** |
| `https://numista-vault--p7-gate-8avtpz22.web.app/catalog/x` | **200 OK** | 12,261 | Numista.AI — AI-Powered Coin Collection Manager | **Wildcard Rewrite A1 FIXED** |

Both `/catalog` and `/catalog/x` successfully serve `/index.html` (HTTP 200) instead of a 404 error page.

---

## 4. Rollback Target & Safety Disclosures

- **Rollback Target:** Confirmed **RT-B: No redeploy**. If teardown is required:
  `firebase hosting:channel:delete p7-gate --project studio-9101802118-8c9a8 --force`
- **Forbidden Commit:** `c547b7a0` was NOT deployed and remains strictly quarantined.
- **Hard Stops Enforced:**
  - Zero live deployment (`numista.ai` / `numista-vault.web.app`).
  - Zero commits or pushes to `main`; `origin/main` strictly pinned at `9f04550a`.
  - Zero Firestore operations (reads/writes/rules/indexes).
  - Zero Stripe calls or config changes.
  - Zero backend/Cloud Run changes.
  - Temporary isolated worktree pruned and purged.
  - HOLDs `74611e05` and `41b8bd5f` stay in full force; go-live addendum remains NOT ACTIVE.
- **Deviations:** Zero.

---

## 5. Next Step

- Handoff to Grok CoS / Field Tester for preview channel verification.
