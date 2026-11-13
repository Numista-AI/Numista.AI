# BLOCKED — NET-816 v3.1: Deploy Retry Halted (Firebase CLI Credentials Expired)
Date: 11 Nov 2026 ~1:04 PM ET (America/New_York)  
From: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
To: Grok Bot CoS / Eric / Antigravity Desk  
Status: **BLOCKED (Firebase CLI Authentication Expired: Requires Eric to run `firebase login --reauth`)**  

---

## 1. References
- Ruling: `RULING_NET-816_AGCOS-V5_DEPLOY-P7GATE_eb8bb7ce_RETRY-AFTER-1300_20261111-1246.md` (`6aee341647ce99a5c25529d4a980fcb0752d53c4c04b9a4a2b1a8e1267c50d8d`)
- Addendum: `ADDENDUM_NET-816_AGCOS-V5_RULING-6aee3416_POSTCHECK-EXPECTED_20261111-1249.md`
- ACK: `ACK_RULING_NET-816_AGCOS-V5_RETRY-AFTER-1300_20261111-1250.md`
- Baton: `BATON_NET-816_AGCOS-V5_v3.1_DEPLOY-P7GATE_eb8bb7ce_20261111-1118.md` (`c5d980c8`)
- Auth: `AUTH_NET-816_v3.1_DEPLOY-P7GATE_eb8bb7ce_ERIC-YES-DEPLOY_CR-t96u_20261111-1117.md` (`b3cb79ec`)
- Target Commit: `eb8bb7ce95fa7164617eef0d0ff804465829e8c9` (local branch `p7-v8.9`)

---

## 2. Execution Diagnostic
1. **Timing Gate:**
   Execution initiated at 13:00:31 EST (strictly after 1:00 PM ET).
2. **Script Integrity Check:**
   Pre-run SHA-256 of `deploy_preview.ps1` computed:
   `884D610301277DE6FE416C33046FD846D12AFF336DF67A6DFEA7B2114BAFE81F`
   Matches reviewed hash exactly. Zero script edits made.
3. **Execution Output:**
   Command:
   `powershell -ExecutionPolicy Bypass -File "1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\deploy_preview.ps1" -BuiltSha "eb8bb7ce95fa7164617eef0d0ff804465829e8c9" -EricApprovalYes "YES DEPLOY p7-gate eb8bb7ce95fa7164617eef0d0ff804465829e8c9 ROLLBACK=a3d7dca20fbbaf06a522205b22d0740b600de52b"`

   Output:
   ```text
   ==> Starting build for eb8bb7ce95fa7164617eef0d0ff804465829e8c9 on p7-gate...
   FATAL: Failed to query firebase channels before deploy
   At C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\deploy_preview.ps1:61 char:5
   +     throw "FATAL: Failed to query firebase channels before deploy"
   +     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
       + CategoryInfo          : OperationStopped: (FATAL: Failed t...s before deploy:String) [], RuntimeException
       + FullyQualifiedErrorId : FATAL: Failed to query firebase channels before deploy
   ```
4. **Underlying Root Cause:**
   Direct execution of the underlying pre-deploy check (`firebase hosting:channel:list --project studio-9101802118-8c9a8 --json`) returned:
   ```json
   {
     "status": "error",
     "error": "Failed to get Firebase project studio-9101802118-8c9a8. Please make sure the project exists and your account has permission to access it."
   }
   ```
   Executing `firebase projects:list` revealed the exact underlying failure:
   ```text
   Authentication Error: Your credentials are no longer valid. Please run firebase login --reauth

   For CI servers and headless environments, generate a new token with firebase login:ci
   Error: Failed to list Firebase projects. See firebase-debug.log for more info.
   ```
   The Firebase CLI OAuth refresh token for `eric@numista.ai` expired between 12:27 PM ET and 1:00 PM ET.

---

## 3. Served Readback & Invariant Checks
1. **Served `p7-gate` Readback:**
   URL: `https://numista-vault--p7-gate-8avtpz22.web.app/version.json`
   Payload:
   ```json
   {
       "app_name": "numista_ai",
       "version": "8.18.15",
       "build_number": "81818",
       "package_name": "numista_ai"
   }
   ```
   `git_commit` is **absent**. Deployed preview remains at prior state; `eb8bb7ce` was not deployed.
2. **Production Invariant:**
   `https://numista-vault.web.app/version.json` and `https://studio-9101802118-8c9a8.web.app` are **100% untouched and unchanged**.
3. **Worktree & Git Hygiene:**
   - Script exited at pre-flight check before worktree creation; `git worktree list` verified clean.
   - Zero git push to origin; `origin/main` locked at `9f04550a`; `eb8bb7ce` remains local only.
4. **Rollback Policy:**
   No rollback executed.

---

## 4. Status & Standing Down
Per RULING 6aee3416 Item 3 (*"There is no third try without Eric"*) and because OAuth re-authentication requires user interactive browser login:
1. **AG CoS v5 stands down.**
2. **Action Required by Eric:**
   Eric must run in his terminal:
   ```bash
   firebase login --reauth
   ```
   to renew Firebase CLI session tokens before any further Firebase Hosting operations can proceed.
