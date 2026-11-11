# BLOCKED — NET-816 v3.1: Deploy Baton c5d980c8 (eb8bb7ce to p7-gate)
Date: 11 Nov 2026 ~12:28 PM ET (America/New_York)  
From: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
To: Grok Bot CoS / Eric / Antigravity Desk  
Status: **BLOCKED (Deploy Step 7: Firebase API Upload Failure)**  

---

## 1. References
- Baton: `BATON_NET-816_AGCOS-V5_v3.1_DEPLOY-P7GATE_eb8bb7ce_20261111-1118.md` (`c5d980c8`)
- Approval: `AUTH_NET-816_v3.1_DEPLOY-P7GATE_eb8bb7ce_ERIC-YES-DEPLOY_CR-t96u_20261111-1117.md` (`b3cb79ec`)
- HOLD: `HOLD_NET-816_AGCOS-V5_v3.1_DEPLOY-P7GATE_eb8bb7ce_ROLLBACK-a3d7dca2-CONTAINS-c547b7a0_20261111-1130.md` (`c6275c95`)
- CLEARED: `CLEARED_NET-816_AGCOS-V5_v3.1_HOLD-c6275c95-LIFTED_DEPLOY-BATON-c5d980c8-REACTIVATED_20261111-1134.md` (`751f3b8b`)
- Plan: `PLAN_NET-816_FAILFIX-R2_v3.1_AGCOS-V5_20261110.md` (`785b04e5...`)
- Code Review: `CODE_REVIEW_NET-816_v3.1_eb8bb7ce_20261111.md` (PASS by Code Reviewer Argon)
- Target Commit: `eb8bb7ce95fa7164617eef0d0ff804465829e8c9` (local branch `p7-v8.9`)

---

## 2. Execution Summary & Failure Description
At 12:14 PM ET, following reactivation via CLEARED notice `751f3b8b`, AG CoS initiated `deploy_preview.ps1` with verified arguments:
- BuiltSha: `eb8bb7ce95fa7164617eef0d0ff804465829e8c9`
- EricApprovalYes: `YES DEPLOY p7-gate eb8bb7ce95fa7164617eef0d0ff804465829e8c9 ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b`

### Completed Steps Prior to Failure:
1. Approval string verification: PASS.
2. Prohibited commit check (`c547b7a0`): PASS.
3. Pre-deploy baseline capture: PASS (`live` channel on `studio-9101802118-8c9a8` recorded at release `1782346245074000`).
4. Isolated worktree creation in `$env:TEMP`: PASS (`numista-net816-worktree-20261111-121407`).
5. Worktree HEAD verification matching `eb8bb7ce...`: PASS.
6. Flutter web release build (`flutter build web --release`): PASS.
7. `version.json` stamped and verified locally with `git_commit: eb8bb7ce95fa7164617eef0d0ff804465829e8c9`: PASS.

### Failed Step (Step 7: Firebase Channel Deploy):
Command: `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8` inside `numista_mobile`.
Output:
```
Deploying to 'p7-gate' on numista-vault...
i  hosting:channel: Adding version files to channel p7-gate...
!  hosting: upload error: Unable to parse JSON: SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
Error: Task index 0 failed: retries exhausted after 4 attempts, with error: Unable to parse JSON: SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
FATAL: Step 'Firebase channel deploy to p7-gate' failed with exit code 1
```

**Root Cause:**
Upstream Google/Firebase Hosting upload API endpoint returned an HTML 5xx error response page (`<!DOCTYPE ...>`) during version file upload rather than JSON, exhausting all 4 automatic retries in the Firebase CLI.

---

## 3. Current System State & Invariant Checks
1. **Production / Live Invariant:**
   - Production URL (`https://numista-vault.web.app`) and project root URL (`https://studio-9101802118-8c9a8.web.app`): **100% UNTOUCHED**. Release timestamp unchanged.
2. **Preview Channel (`p7-gate`):**
   - File upload failed; release was not finalized with `eb8bb7ce`.
   - Readback of `https://numista-vault--p7-gate-8avtpz22.web.app/version.json` serves the prior state (`app_name: numista_ai`, `version: 8.18.15`, `build_number: 81818`; no `git_commit` field).
3. **Rollback Policy Adherence:**
   - Per `CLEARED` directive item 3: *"ROLLBACK now needs its OWN approved action. If the deploy or the readback fails, do NOT roll back on your own; file BLOCKED with the details and stop."*
   - **AG CoS has NOT triggered rollback.**
4. **Git Hygiene:**
   - Zero git push to origin (`origin/main` locked at `9f04550a`; `p7-v8.9` commit `eb8bb7ce` remains strictly local).
   - Temporary worktree in `$env:TEMP` cleaned up and pruned; `git worktree list` verified clean.

---

## 4. Observations & Next Steps
1. **Transient API Error:**
   The failure was caused by upstream Firebase API returning an HTML error page. A retry of the deploy step is the standard remedy once Firebase upload endpoints are responsive.
2. **Script Readback Note for Grok CoS / Desk:**
   In `deploy_preview.ps1` (line 122), the post-deploy readback runs `firebase hosting:channel:list --project studio-9101802118-8c9a8 --json`. Because `p7-gate` is provisioned under site `numista-vault` (as defined in `numista_mobile/firebase.json`), querying without `--site numista-vault` returns only the default site's channels. Adding `--site numista-vault` ensures line 133 resolves `$p7Channel`.
3. **Standing Down / Awaiting Authorization:**
   Per protocol, AG CoS v5 stops and stands down awaiting Eric / Grok CoS decision:
   - Instruction to retry deploy of `eb8bb7ce` to `p7-gate`, or
   - Instruction to execute an authorized rollback action.
