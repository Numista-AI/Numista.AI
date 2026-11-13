# ACK — BATON NET-816 PREVIEW DEPLOY a3d7dca2 to p7-gate ONLY

- **Desk:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Baton Received:** `BATON_NET-816_AGCOS-V5_PREVIEW-DEPLOY_a3d7dca2_P7-GATE-ONLY_20261110-1704.md`
- **Authority Record:** `AUTH_NET-816_PREVIEW-DEPLOY_a3d7dca2_ERIC-PRIMARY-YES_DESK-VERIFIED_20261110-1741.md` (Eric primary YES card `t494s1610`, 10 Nov 2026 5:41 PM ET)
- **Target Commit:** `a3d7dca20fbbaf06a522205b22d0740b600de52b`
- **Scope:** Build web app in isolated worktree and deploy ONLY to preview channel `p7-gate` (`--project studio-9101802118-8c9a8 --expires 7d`).
- **Rollback Target:** RT-B (No redeploy; if failed, delete `p7-gate`).
- **Hard Stops Maintained:** Zero live deployment, `origin/main` stays pinned at `9f04550a`, zero Firestore reads/writes/indexes, zero Stripe calls, zero Cloud Run touch. HOLDs `74611e05` and `41b8bd5f` remain in full force.
- **Status:** ACKNOWLEDGED. Proceeding with isolated worktree build and preview channel deploy.
