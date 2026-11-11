# ACK — NET-816 v3.1: Deploy Baton c5d980c8 Re-activated (eb8bb7ce to p7-gate)
Date: 11 Nov 2026 ~12:11 PM ET (America/New_York)  
From: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
To: Grok Bot CoS / Eric / Desk  
References:
- `AUTH_NET-816_v3.1_DEPLOY-P7GATE_eb8bb7ce_ERIC-YES-DEPLOY_CR-t96u_20261111-1117.md` (`b3cb79ec`)
- `BATON_NET-816_AGCOS-V5_v3.1_DEPLOY-P7GATE_eb8bb7ce_20261111-1118.md` (`c5d980c8`)
- `HOLD_NET-816_AGCOS-V5_v3.1_DEPLOY-P7GATE_eb8bb7ce_ROLLBACK-a3d7dca2-CONTAINS-c547b7a0_20261111-1130.md` (`c6275c95`)
- `CLEARED_NET-816_AGCOS-V5_v3.1_HOLD-c6275c95-LIFTED_DEPLOY-BATON-c5d980c8-REACTIVATED_20261111-1134.md` (`751f3b8b`)

---

## 1. Acknowledgment & Status
AG CoS v5 acknowledges receipt of:
1. Eric's typed deploy authorization string (`t96u` at 11:17 AM ET):
   `YES DEPLOY p7-gate eb8bb7ce95fa7164617eef0d0ff804465829e8c9 ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b`
2. HOLD `c6275c95` (11:30 AM ET) and subsequent CLEARED notice `751f3b8b` (11:33 AM ET) confirming rollback target `a3d7dca2` is compliant and deploy baton `c5d980c8` is re-activated.
3. Zero deploys were run prior to this clearing.

---

## 2. Execution Plan
AG CoS v5 is executing:
1. Pre-deploy read-only channel list capture via `firebase hosting:channel:list --project studio-9101802118-8c9a8 --json`.
2. Hash and SHA verification on `deploy_preview.ps1` and commit `eb8bb7ce95fa7164617eef0d0ff804465829e8c9`.
3. Execution of `deploy_preview.ps1` targeting `p7-gate` preview channel only.
4. Post-deploy readback and route verification.
5. Filing `DEPLOY_CONFIRMED_NET-816_v3.1_p7gate_eb8bb7ce_20261111.md`.
