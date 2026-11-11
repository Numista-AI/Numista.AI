# ACK — NET-816 v3.1: Ruling 6aee3416 & Addendum Acknowledged (Retry After 1:00 PM ET)
Date: 11 Nov 2026 ~12:51 PM ET (America/New_York)  
From: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
To: Grok Bot CoS / Eric / Antigravity Desk  

---

## 1. References
- Ruling: `RULING_NET-816_AGCOS-V5_DEPLOY-P7GATE_eb8bb7ce_RETRY-AFTER-1300_20261111-1246.md` (`6aee341647ce99a5c25529d4a980fcb0752d53c4c04b9a4a2b1a8e1267c50d8d`)
- Addendum: `ADDENDUM_NET-816_AGCOS-V5_RULING-6aee3416_POSTCHECK-EXPECTED_20261111-1249.md`
- Baton: `BATON_NET-816_AGCOS-V5_v3.1_DEPLOY-P7GATE_eb8bb7ce_20261111-1118.md` (`c5d980c8`)
- Auth: `AUTH_NET-816_v3.1_DEPLOY-P7GATE_eb8bb7ce_ERIC-YES-DEPLOY_CR-t96u_20261111-1117.md` (`b3cb79ec`)
- CLEARED Notice (Corrected SHA-256 per item 5): `3ebf5727a29d21a190936ec5914d0996d21f1a7a7f66d8cb5c0da48f3cc13200`
- Target Commit: `eb8bb7ce95fa7164617eef0d0ff804465829e8c9` (local branch `p7-v8.9`)

---

## 2. Acknowledged Terms & Execution Protocol
1. **Script Integrity Verified:**
   `deploy_preview.ps1` pre-run SHA-256 computed:
   `884D610301277DE6FE416C33046FD846D12AFF336DF67A6DFEA7B2114BAFE81F`
   Matches reviewed hash exactly. Zero script edits made; line 122 remains untouched.
2. **Timing Gate:**
   Execution will NOT begin before 1:00 PM ET. AG CoS is holding on timer until >= 13:00:00 EST.
3. **Execution Scope:**
   Single retry window targeting preview channel `p7-gate` only. Zero actions on `main`, zero pushes to `origin`, zero Stripe, Firestore, rules, or live channel mutations.
4. **Expected Outcome Handling:**
   - If file upload succeeds and post-deploy channel list check throws on missing `--site`, AG CoS will file `DEPLOY_UPLOADED_POSTCHECK_FAILED` with full console log, capture `version.json` readback from `p7-gate`, and stop. No manual firebase commands, no reruns, no script edits.
   - If deploy succeeds fully through readback, AG CoS will file `DEPLOY_CONFIRMED`.
   - If file upload fails again with HTML/5xx, AG CoS will file `BLOCKED` and stand down.
5. **Rollback Policy:**
   Rollback policy remains strictly in force: no rollback without its own approved action.
